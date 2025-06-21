from __future__ import annotations
import json
import re
from typing import Dict, Any, List, Optional
from ..core.task import Task


class LLMAssist(Task):
    """AI-powered security analysis and assistance."""
    
    # Security knowledge base patterns and templates
    SECURITY_PATTERNS = {
        "sql_injection": {
            "description": "SQL injection vulnerability analysis",
            "indicators": ["union", "select", "insert", "delete", "drop", "exec", "'", "\"", ";", "--"],
            "severity": "high",
            "remediation": "Use parameterized queries, input validation, and least privilege database access"
        },
        "xss": {
            "description": "Cross-site scripting vulnerability analysis", 
            "indicators": ["<script>", "javascript:", "onerror", "onload", "alert(", "prompt(", "confirm("],
            "severity": "high",
            "remediation": "Implement proper input sanitization, output encoding, and Content Security Policy"
        },
        "command_injection": {
            "description": "Command injection vulnerability analysis",
            "indicators": [";", "&&", "||", "|", "`", "$(", "system(", "exec(", "shell_exec("],
            "severity": "critical",
            "remediation": "Avoid executing system commands with user input, use whitelisting, and sandboxing"
        },
        "path_traversal": {
            "description": "Path traversal vulnerability analysis",
            "indicators": ["../", "..\\", "/etc/", "\\windows\\", "passwd", "shadow"],
            "severity": "high",
            "remediation": "Validate file paths, use chroot jails, and implement proper access controls"
        },
        "buffer_overflow": {
            "description": "Buffer overflow vulnerability analysis",
            "indicators": ["strcpy", "strcat", "sprintf", "gets", "scanf", "AAAA", "\\x41"],
            "severity": "critical",
            "remediation": "Use safe string functions, implement stack protection, and enable ASLR"
        },
        "crypto_weakness": {
            "description": "Cryptographic weakness analysis",
            "indicators": ["md5", "sha1", "des", "rc4", "weak", "random", "rand()", "Math.random"],
            "severity": "medium",
            "remediation": "Use strong cryptographic algorithms, secure random number generators, and proper key management"
        }
    }
    
    # Common security questions and responses
    SECURITY_KB = {
        "owasp_top_10": {
            "2021": [
                "Broken Access Control",
                "Cryptographic Failures", 
                "Injection",
                "Insecure Design",
                "Security Misconfiguration",
                "Vulnerable and Outdated Components",
                "Identification and Authentication Failures",
                "Software and Data Integrity Failures",
                "Security Logging and Monitoring Failures",
                "Server-Side Request Forgery (SSRF)"
            ]
        },
        "common_ports": {
            "21": "FTP", "22": "SSH", "23": "Telnet", "25": "SMTP", "53": "DNS",
            "80": "HTTP", "110": "POP3", "143": "IMAP", "443": "HTTPS", "993": "IMAPS",
            "995": "POP3S", "3389": "RDP", "5432": "PostgreSQL", "3306": "MySQL"
        }
    }
    
    async def validate_params(self) -> None:
        """Validate LLMAssist parameters."""
        if not self.params.get("prompt") and not self.params.get("analyze_code"):
            raise ValueError("Either 'prompt' or 'analyze_code' parameter is required")
    
    async def run(self) -> Dict[str, Any]:
        """Execute AI-powered security analysis."""
        prompt = self.params.get("prompt", "")
        code_to_analyze = self.params.get("analyze_code", "")
        analysis_type = self.params.get("type", "general")
        context = self.params.get("context", "")
        
        self.logger.info(f"Starting AI security analysis - type: {analysis_type}")
        
        results = {
            "analysis_type": analysis_type,
            "timestamp": __import__('time').time(),
            "input": {
                "prompt": prompt,
                "has_code": bool(code_to_analyze),
                "context": context
            }
        }
        
        # Route to appropriate analysis method
        if analysis_type == "code_review":
            results.update(await self._analyze_code_security(code_to_analyze))
        elif analysis_type == "vulnerability_assessment":
            results.update(await self._assess_vulnerabilities(prompt, code_to_analyze))
        elif analysis_type == "security_question":
            results.update(await self._answer_security_question(prompt))
        elif analysis_type == "threat_modeling":
            results.update(await self._generate_threat_model(prompt, context))
        elif analysis_type == "remediation_advice":
            results.update(await self._provide_remediation_advice(prompt, code_to_analyze))
        else:  # general
            results.update(await self._general_security_analysis(prompt, code_to_analyze, context))
        
        self.logger.info("AI security analysis completed")
        return results
    
    async def _analyze_code_security(self, code: str) -> Dict[str, Any]:
        """Analyze code for security vulnerabilities."""
        if not code:
            return {"error": "No code provided for analysis"}
        
        vulnerabilities = []
        security_score = 100
        recommendations = []
        
        # Analyze against known patterns
        for vuln_type, pattern_info in self.SECURITY_PATTERNS.items():
            matches = []
            for indicator in pattern_info["indicators"]:
                if indicator.lower() in code.lower():
                    # Find line numbers where indicator appears
                    lines = code.split('\n')
                    for i, line in enumerate(lines):
                        if indicator.lower() in line.lower():
                            matches.append({
                                "line": i + 1,
                                "code": line.strip(),
                                "indicator": indicator
                            })
            
            if matches:
                vulnerability = {
                    "type": vuln_type,
                    "description": pattern_info["description"],
                    "severity": pattern_info["severity"],
                    "matches": matches[:5],  # Limit to first 5 matches
                    "remediation": pattern_info["remediation"]
                }
                vulnerabilities.append(vulnerability)
                
                # Adjust security score based on severity
                severity_impact = {"low": 5, "medium": 15, "high": 25, "critical": 40}
                security_score -= severity_impact.get(pattern_info["severity"], 10)
        
        # Generate recommendations
        if vulnerabilities:
            recommendations.extend([
                "Implement comprehensive input validation",
                "Use parameterized queries for database operations",
                "Apply output encoding for user data",
                "Implement proper error handling",
                "Use secure coding practices and frameworks"
            ])
        else:
            recommendations.append("No obvious security issues detected, but consider professional security review")
        
        # Code complexity analysis
        code_metrics = self._analyze_code_complexity(code)
        
        return {
            "code_analysis": {
                "vulnerabilities": vulnerabilities,
                "vulnerability_count": len(vulnerabilities),
                "security_score": max(0, security_score),
                "risk_level": self._calculate_risk_level(security_score),
                "recommendations": recommendations,
                "code_metrics": code_metrics
            }
        }
    
    async def _assess_vulnerabilities(self, description: str, code: str = "") -> Dict[str, Any]:
        """Assess vulnerabilities based on description and optional code."""
        assessment = {
            "vulnerability_type": "unknown",
            "severity": "medium",
            "likelihood": "medium",
            "impact": "medium",
            "cvss_estimate": 5.0
        }
        
        description_lower = description.lower()
        
        # Pattern matching for vulnerability types
        if any(keyword in description_lower for keyword in ["sql", "injection", "database"]):
            assessment.update({
                "vulnerability_type": "SQL Injection",
                "severity": "high",
                "likelihood": "high",
                "impact": "high",
                "cvss_estimate": 8.2,
                "description": "SQL injection vulnerabilities allow attackers to manipulate database queries",
                "exploitation_complexity": "low",
                "remediation_priority": "immediate"
            })
        elif any(keyword in description_lower for keyword in ["xss", "cross-site", "script"]):
            assessment.update({
                "vulnerability_type": "Cross-Site Scripting (XSS)",
                "severity": "high", 
                "likelihood": "high",
                "impact": "medium",
                "cvss_estimate": 7.4,
                "description": "XSS vulnerabilities allow execution of malicious scripts in user browsers",
                "exploitation_complexity": "low"
            })
        elif any(keyword in description_lower for keyword in ["command", "execution", "rce"]):
            assessment.update({
                "vulnerability_type": "Remote Code Execution",
                "severity": "critical",
                "likelihood": "medium",
                "impact": "critical",
                "cvss_estimate": 9.3,
                "description": "Remote code execution allows attackers to run arbitrary commands on the server",
                "exploitation_complexity": "medium",
                "remediation_priority": "critical"
            })
        elif any(keyword in description_lower for keyword in ["buffer", "overflow", "memory"]):
            assessment.update({
                "vulnerability_type": "Buffer Overflow",
                "severity": "high",
                "likelihood": "medium", 
                "impact": "high",
                "cvss_estimate": 8.1,
                "description": "Buffer overflow vulnerabilities can lead to code execution or DoS",
                "exploitation_complexity": "high"
            })
        
        # If code is provided, enhance assessment
        if code:
            code_analysis = await self._analyze_code_security(code)
            if code_analysis.get("code_analysis", {}).get("vulnerabilities"):
                assessment["code_confirmation"] = True
                assessment["additional_findings"] = code_analysis["code_analysis"]["vulnerabilities"]
        
        return {"vulnerability_assessment": assessment}
    
    async def _answer_security_question(self, question: str) -> Dict[str, Any]:
        """Answer common security questions."""
        question_lower = question.lower()
        
        # OWASP Top 10 questions
        if "owasp" in question_lower and "top" in question_lower:
            return {
                "security_answer": {
                    "question": question,
                    "answer": "The OWASP Top 10 2021 includes: " + ", ".join(self.SECURITY_KB["owasp_top_10"]["2021"]),
                    "reference": "https://owasp.org/Top10/",
                    "category": "standards"
                }
            }
        
        # Port scanning questions
        elif "port" in question_lower and any(keyword in question_lower for keyword in ["scan", "common", "well-known"]):
            common_ports = self.SECURITY_KB["common_ports"]
            port_list = [f"{port} ({service})" for port, service in list(common_ports.items())[:10]]
            return {
                "security_answer": {
                    "question": question,
                    "answer": f"Common ports include: {', '.join(port_list)}",
                    "category": "networking"
                }
            }
        
        # CIA Triad questions
        elif "cia" in question_lower or "confidentiality" in question_lower:
            return {
                "security_answer": {
                    "question": question,
                    "answer": "The CIA Triad represents the three pillars of information security: Confidentiality (protecting information from unauthorized access), Integrity (ensuring information accuracy and completeness), and Availability (ensuring authorized access to information when needed).",
                    "category": "fundamentals"
                }
            }
        
        # Default response for unrecognized questions
        else:
            return {
                "security_answer": {
                    "question": question,
                    "answer": "I don't have specific information about this security topic. Consider consulting OWASP, NIST, or other security frameworks for authoritative guidance.",
                    "category": "general",
                    "suggestions": [
                        "Try rephrasing your question",
                        "Check OWASP resources",
                        "Consult security documentation",
                        "Consider professional security training"
                    ]
                }
            }
    
    async def _generate_threat_model(self, system_description: str, context: str) -> Dict[str, Any]:
        """Generate a basic threat model."""
        threats = []
        assets = []
        attack_vectors = []
        
        description_lower = system_description.lower()
        
        # Identify assets based on description
        if "database" in description_lower:
            assets.append("Database containing sensitive information")
        if "user" in description_lower:
            assets.append("User accounts and personal data")
        if "api" in description_lower:
            assets.append("API endpoints and services")
        if "web" in description_lower:
            assets.append("Web application and user sessions")
        
        # Common threats based on system type
        if "web" in description_lower:
            threats.extend([
                {"threat": "SQL Injection", "likelihood": "high", "impact": "high"},
                {"threat": "Cross-Site Scripting", "likelihood": "high", "impact": "medium"},
                {"threat": "CSRF", "likelihood": "medium", "impact": "medium"},
                {"threat": "Session Hijacking", "likelihood": "medium", "impact": "high"}
            ])
            attack_vectors.extend(["Malicious user input", "Compromised user accounts", "Man-in-the-middle attacks"])
        
        if "api" in description_lower:
            threats.extend([
                {"threat": "API Abuse", "likelihood": "high", "impact": "medium"},
                {"threat": "Broken Authentication", "likelihood": "medium", "impact": "high"},
                {"threat": "Data Exposure", "likelihood": "medium", "impact": "critical"}
            ])
            attack_vectors.extend(["Unauthorized API access", "Token theft", "Rate limit bypass"])
        
        return {
            "threat_model": {
                "system_description": system_description,
                "identified_assets": assets,
                "potential_threats": threats,
                "attack_vectors": attack_vectors,
                "recommendations": [
                    "Implement defense in depth",
                    "Regular security testing and code review",
                    "Monitor and log security events",
                    "Keep systems updated and patched",
                    "Train developers on secure coding practices"
                ]
            }
        }
    
    async def _provide_remediation_advice(self, vulnerability_description: str, code: str = "") -> Dict[str, Any]:
        """Provide remediation advice for security issues."""
        advice = {
            "immediate_actions": [],
            "short_term_fixes": [],
            "long_term_improvements": []
        }
        
        vuln_lower = vulnerability_description.lower()
        
        if "sql" in vuln_lower and "injection" in vuln_lower:
            advice.update({
                "immediate_actions": [
                    "Use parameterized queries/prepared statements",
                    "Validate and sanitize all user inputs",
                    "Implement least privilege database access"
                ],
                "short_term_fixes": [
                    "Deploy Web Application Firewall (WAF)",
                    "Implement input validation middleware",
                    "Add database activity monitoring"
                ],
                "long_term_improvements": [
                    "Code review and security training",
                    "Implement SAST/DAST in CI/CD pipeline",
                    "Regular penetration testing"
                ]
            })
        elif "xss" in vuln_lower:
            advice.update({
                "immediate_actions": [
                    "Implement output encoding/escaping",
                    "Use Content Security Policy (CSP)",
                    "Validate and sanitize user inputs"
                ],
                "short_term_fixes": [
                    "Deploy XSS protection headers",
                    "Implement input validation framework",
                    "Use template engines with auto-escaping"
                ],
                "long_term_improvements": [
                    "Security awareness training",
                    "Regular security code reviews",
                    "Implement security testing in development"
                ]
            })
        
        return {"remediation_advice": advice}
    
    async def _general_security_analysis(self, prompt: str, code: str, context: str) -> Dict[str, Any]:
        """Provide general security analysis and guidance."""
        analysis = {
            "summary": "General security analysis completed",
            "findings": [],
            "recommendations": []
        }
        
        # Analyze provided code if available
        if code:
            code_analysis = await self._analyze_code_security(code)
            analysis["code_findings"] = code_analysis.get("code_analysis", {})
        
        # Analyze prompt for security keywords
        if prompt:
            prompt_lower = prompt.lower()
            security_keywords = ["vulnerability", "exploit", "attack", "security", "breach", "malware", "phishing"]
            
            found_keywords = [keyword for keyword in security_keywords if keyword in prompt_lower]
            if found_keywords:
                analysis["findings"].append(f"Security-related keywords detected: {', '.join(found_keywords)}")
        
        # General security recommendations
        analysis["recommendations"].extend([
            "Follow secure coding practices",
            "Implement proper input validation",
            "Use up-to-date security libraries",
            "Regular security assessments",
            "Security awareness training"
        ])
        
        return {"general_analysis": analysis}
    
    def _analyze_code_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        return {
            "total_lines": len(lines),
            "lines_of_code": len(non_empty_lines),
            "comment_lines": len([line for line in lines if line.strip().startswith(('#', '//', '/*'))]),
            "estimated_functions": len(re.findall(r'\b(function|def|void|int|String)\s+\w+\s*\(', code)),
            "complexity_score": min(10, len(non_empty_lines) / 10)  # Simple complexity metric
        }
    
    def _calculate_risk_level(self, security_score: int) -> str:
        """Calculate risk level based on security score."""
        if security_score >= 80:
            return "low"
        elif security_score >= 60:
            return "medium"
        elif security_score >= 40:
            return "high"
        else:
            return "critical"
