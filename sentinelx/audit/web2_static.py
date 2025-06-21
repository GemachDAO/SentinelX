from __future__ import annotations
import re
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..core.task import Task


class Web2Static(Task):
    """Static analysis of web applications and source code."""
    
    # Common vulnerability patterns
    VULNERABILITY_PATTERNS = {
        # SQL Injection patterns
        'sql_injection': [
            r'SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*\+.*',
            r'(query|execute)\s*\(\s*["\'].*\+.*["\']',
            r'Statement\.executeQuery\s*\(\s*["\'].*\+.*["\']',
            r'mysql_query\s*\(\s*["\'].*\$.*["\']',
            r'mysqli_query\s*\(\s*.*,\s*["\'].*\$.*["\']',
        ],
        
        # XSS patterns
        'xss': [
            r'document\.write\s*\(\s*.*\+.*\)',
            r'innerHTML\s*=\s*.*\+.*',
            r'echo\s+.*\$_(GET|POST|REQUEST)\[',
            r'print\s+.*request\.(GET|POST)\[',
            r'response\.write\s*\(\s*.*request\[',
        ],
        
        # Command Injection patterns
        'command_injection': [
            r'(system|exec|shell_exec|passthru)\s*\(\s*.*\$',
            r'Runtime\.getRuntime\(\)\.exec\s*\(\s*.*\+',
            r'subprocess\.(call|run|Popen)\s*\(\s*.*\+',
            r'os\.(system|popen)\s*\(\s*.*\+',
        ],
        
        # Path Traversal patterns
        'path_traversal': [
            r'(include|require|file_get_contents)\s*\(\s*.*\$',
            r'fopen\s*\(\s*.*\$_(GET|POST|REQUEST)',
            r'FileInputStream\s*\(\s*.*\+',
            r'open\s*\(\s*.*\+.*["\']r["\']',
        ],
        
        # Hardcoded credentials
        'hardcoded_secrets': [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']{16,}["\']',
            r'secret\s*=\s*["\'][^"\']{8,}["\']',
            r'token\s*=\s*["\'][^"\']{16,}["\']',
        ],
        
        # Insecure random
        'weak_random': [
            r'Math\.random\(\)',
            r'Random\(\)\.next',
            r'rand\(\)',
            r'srand\(',
        ],
        
        # Crypto issues
        'crypto_issues': [
            r'MD5\s*\(',
            r'SHA1\s*\(',
            r'DES\s*\(',
            r'RC4\s*\(',
        ]
    }
    
    # File extensions to analyze
    SUPPORTED_EXTENSIONS = {
        '.php', '.py', '.js', '.java', '.jsp', '.asp', '.aspx', 
        '.rb', '.go', '.cpp', '.c', '.cs', '.ts', '.tsx', '.jsx'
    }
    
    async def validate_params(self) -> None:
        """Validate Web2Static parameters."""
        target = self.params.get("target")
        if not target:
            raise ValueError("target parameter is required")
        
        target_path = Path(target)
        if not target_path.exists():
            raise ValueError(f"Target path not found: {target_path}")
    
    async def run(self) -> Dict[str, Any]:
        """Execute static analysis on web application source code."""
        target = Path(self.params["target"])
        include_patterns = self.params.get("include", ["*"])
        exclude_patterns = self.params.get("exclude", [])
        severity_filter = self.params.get("min_severity", "low")
        
        self.logger.info(f"Starting static analysis of {target}")
        
        # Collect files to analyze
        files_to_scan = self._collect_files(target, include_patterns, exclude_patterns)
        
        if not files_to_scan:
            return {
                "target": str(target),
                "files_scanned": 0,
                "vulnerabilities": [],
                "summary": {"total": 0, "by_type": {}, "by_severity": {}}
            }
        
        self.logger.info(f"Scanning {len(files_to_scan)} files")
        
        # Analyze files
        vulnerabilities = []
        for file_path in files_to_scan:
            file_vulns = await self._analyze_file(file_path)
            vulnerabilities.extend(file_vulns)
        
        # Filter by severity
        filtered_vulns = self._filter_by_severity(vulnerabilities, severity_filter)
        
        # Generate summary
        summary = self._generate_summary(filtered_vulns)
        
        self.logger.info(f"Found {len(filtered_vulns)} vulnerabilities")
        
        return {
            "target": str(target),
            "files_scanned": len(files_to_scan),
            "vulnerabilities": filtered_vulns,
            "summary": summary,
            "analysis_info": {
                "patterns_checked": len(self.VULNERABILITY_PATTERNS),
                "file_types": list(self.SUPPORTED_EXTENSIONS),
                "severity_filter": severity_filter
            }
        }
    
    def _collect_files(self, target: Path, include: List[str], exclude: List[str]) -> List[Path]:
        """Collect files to analyze based on include/exclude patterns."""
        files = []
        
        if target.is_file():
            if target.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                files.append(target)
        else:
            # Recursively find files
            for ext in self.SUPPORTED_EXTENSIONS:
                pattern = f"**/*{ext}"
                files.extend(target.glob(pattern))
        
        # Apply include/exclude filters
        if include and include != ["*"]:
            filtered_files = []
            for file_path in files:
                for pattern in include:
                    if pattern in str(file_path):
                        filtered_files.append(file_path)
                        break
            files = filtered_files
        
        if exclude:
            filtered_files = []
            for file_path in files:
                should_exclude = False
                for pattern in exclude:
                    if pattern in str(file_path):
                        should_exclude = True
                        break
                if not should_exclude:
                    filtered_files.append(file_path)
            files = filtered_files
        
        return files
    
    async def _analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a single file for vulnerabilities."""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            self.logger.warning(f"Could not read file {file_path}: {e}")
            return vulnerabilities
        
        # Check each vulnerability pattern
        for vuln_type, patterns in self.VULNERABILITY_PATTERNS.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        vuln = {
                            "type": vuln_type,
                            "file": str(file_path),
                            "line": line_num,
                            "column": match.start() + 1,
                            "code": line.strip(),
                            "matched_text": match.group(),
                            "pattern": pattern,
                            "severity": self._get_severity(vuln_type),
                            "description": self._get_description(vuln_type),
                            "recommendation": self._get_recommendation(vuln_type)
                        }
                        vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type."""
        severity_map = {
            'sql_injection': 'high',
            'xss': 'high', 
            'command_injection': 'critical',
            'path_traversal': 'high',
            'hardcoded_secrets': 'medium',
            'weak_random': 'medium',
            'crypto_issues': 'medium'
        }
        return severity_map.get(vuln_type, 'low')
    
    def _get_description(self, vuln_type: str) -> str:
        """Get description for vulnerability type."""
        descriptions = {
            'sql_injection': 'Potential SQL injection vulnerability detected',
            'xss': 'Potential Cross-Site Scripting (XSS) vulnerability detected',
            'command_injection': 'Potential command injection vulnerability detected',
            'path_traversal': 'Potential path traversal vulnerability detected',
            'hardcoded_secrets': 'Hardcoded credentials or secrets detected',
            'weak_random': 'Weak random number generation detected',
            'crypto_issues': 'Weak cryptographic algorithm detected'
        }
        return descriptions.get(vuln_type, 'Security issue detected')
    
    def _get_recommendation(self, vuln_type: str) -> str:
        """Get recommendation for vulnerability type."""
        recommendations = {
            'sql_injection': 'Use parameterized queries or prepared statements',
            'xss': 'Sanitize and validate all user input before output',
            'command_injection': 'Avoid executing system commands with user input',
            'path_traversal': 'Validate and sanitize file paths, use whitelist approach',
            'hardcoded_secrets': 'Use environment variables or secure configuration',
            'weak_random': 'Use cryptographically secure random number generator',
            'crypto_issues': 'Use modern, secure cryptographic algorithms'
        }
        return recommendations.get(vuln_type, 'Review and remediate the security issue')
    
    def _filter_by_severity(self, vulnerabilities: List[Dict[str, Any]], min_severity: str) -> List[Dict[str, Any]]:
        """Filter vulnerabilities by minimum severity level."""
        severity_levels = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        min_level = severity_levels.get(min_severity.lower(), 0)
        
        return [
            vuln for vuln in vulnerabilities 
            if severity_levels.get(vuln['severity'], 0) >= min_level
        ]
    
    def _generate_summary(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics."""
        total = len(vulnerabilities)
        
        by_type = {}
        by_severity = {}
        
        for vuln in vulnerabilities:
            vuln_type = vuln['type']
            severity = vuln['severity']
            
            by_type[vuln_type] = by_type.get(vuln_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total": total,
            "by_type": by_type,
            "by_severity": by_severity
        }
