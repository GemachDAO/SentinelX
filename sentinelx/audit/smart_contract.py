from __future__ import annotations
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from ..core.task import Task


class SlitherScan(Task):
    """Smart contract security analysis using Slither."""
    
    async def validate_params(self) -> None:
        """Validate SlitherScan parameters."""
        if not self.params.get("contract_path"):
            raise ValueError("contract_path parameter is required")
        
        contract_path = Path(self.params["contract_path"])
        if not contract_path.exists():
            raise ValueError(f"Contract file not found: {contract_path}")
        
        if not contract_path.suffix == ".sol":
            raise ValueError("Only Solidity (.sol) files are supported")
    
    async def run(self) -> Dict[str, Any]:
        """Execute Slither analysis on a Solidity contract."""
        contract_path = Path(self.params["contract_path"])
        output_format = self.params.get("format", "json")
        detectors = self.params.get("detectors", "all")
        
        self.logger.info(f"Starting Slither analysis of {contract_path}")
        
        try:
            # Build slither command
            cmd = ["slither", str(contract_path)]
            
            if output_format == "json":
                cmd.extend(["--json", "-"])
            
            if detectors != "all":
                cmd.extend(["--detect", detectors])
            
            # Add common flags for better analysis
            cmd.extend([
                "--solc-remaps", "@=node_modules/@",
                "--exclude-optimization"
            ])
            
            if self.params.get("exclude_info", True):
                cmd.append("--exclude-informational")
            
            # Remove empty strings from cmd
            cmd = [arg for arg in cmd if arg]
            
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            
            # Execute Slither
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.params.get("timeout", 300),  # 5 minute timeout
                cwd=contract_path.parent
            )
            
            # Parse results
            if output_format == "json":
                try:
                    slither_output = json.loads(result.stdout) if result.stdout else {}
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as text output
                    slither_output = {"raw_output": result.stdout, "error": result.stderr}
            else:
                slither_output = {"output": result.stdout, "error": result.stderr}
            
            # Process and categorize findings
            findings = self._process_findings(slither_output)
            
            # Generate summary
            summary = self._generate_summary(findings)
            
            analysis_result = {
                "contract_path": str(contract_path),
                "slither_version": self._get_slither_version(),
                "analysis_time": self.duration,
                "summary": summary,
                "findings": findings,
                "raw_output": slither_output if self.params.get("include_raw", False) else None,
                "command_used": " ".join(cmd),
                "exit_code": result.returncode
            }
            
            if result.returncode != 0:
                self.logger.warning(f"Slither exited with code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Slither stderr: {result.stderr}")
                    analysis_result["errors"] = result.stderr
            
            self.logger.info(f"Slither analysis completed. Found {len(findings)} issues.")
            return analysis_result
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Slither analysis timed out after {self.params.get('timeout', 300)} seconds")
        except Exception as e:
            self.logger.error(f"Slither analysis failed: {str(e)}")
            raise RuntimeError(f"Slither analysis failed: {str(e)}")
    
    def _process_findings(self, slither_output: Dict) -> List[Dict[str, Any]]:
        """Process and normalize Slither findings."""
        findings = []
        
        if "results" in slither_output and "detectors" in slither_output["results"]:
            for detector in slither_output["results"]["detectors"]:
                finding = {
                    "detector": detector.get("check", "unknown"),
                    "impact": detector.get("impact", "unknown"),
                    "confidence": detector.get("confidence", "unknown"),
                    "description": detector.get("description", ""),
                    "elements": detector.get("elements", []),
                    "first_markdown_element": detector.get("first_markdown_element", ""),
                    "id": detector.get("id", ""),
                    "markdown": detector.get("markdown", "")
                }
                
                # Add severity based on impact
                finding["severity"] = self._map_impact_to_severity(finding["impact"])
                
                findings.append(finding)
        
        # Sort by severity (Critical > High > Medium > Low > Info)
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Informational": 4}
        findings.sort(key=lambda x: severity_order.get(x["severity"], 5))
        
        return findings
    
    def _map_impact_to_severity(self, impact: str) -> str:
        """Map Slither impact levels to standard severity levels."""
        impact_mapping = {
            "High": "Critical",
            "Medium": "High", 
            "Low": "Medium",
            "Informational": "Low"
        }
        return impact_mapping.get(impact, "Informational")
    
    def _generate_summary(self, findings: List[Dict]) -> Dict[str, Any]:
        """Generate a summary of findings."""
        summary = {
            "total_issues": len(findings),
            "by_severity": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0},
            "by_detector": {},
            "critical_issues": []
        }
        
        for finding in findings:
            severity = finding["severity"]
            detector = finding["detector"]
            
            summary["by_severity"][severity] += 1
            summary["by_detector"][detector] = summary["by_detector"].get(detector, 0) + 1
            
            # Track critical issues for quick review
            if severity in ["Critical", "High"]:
                summary["critical_issues"].append({
                    "detector": detector,
                    "description": finding["description"][:200] + "..." if len(finding["description"]) > 200 else finding["description"]
                })
        
        return summary
    
    def _get_slither_version(self) -> str:
        """Get Slither version."""
        try:
            result = subprocess.run(["slither", "--version"], capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"


class MythrilScan(Task):
    """Smart contract security analysis using Mythril."""
    
    async def validate_params(self) -> None:
        """Validate MythrilScan parameters."""
        if not self.params.get("contract_path"):
            raise ValueError("contract_path parameter is required")
        
        contract_path = Path(self.params["contract_path"])
        if not contract_path.exists():
            raise ValueError(f"Contract file not found: {contract_path}")
        
        if not contract_path.suffix == ".sol":
            raise ValueError("Only Solidity (.sol) files are supported")
    
    async def run(self) -> Dict[str, Any]:
        """Execute Mythril analysis on a Solidity contract."""
        contract_path = Path(self.params["contract_path"])
        output_format = self.params.get("format", "json")
        execution_timeout = self.params.get("execution_timeout", 86400)  # 24 hours default
        
        self.logger.info(f"Starting Mythril analysis of {contract_path}")
        
        try:
            # Build mythril command
            cmd = ["myth", "analyze", str(contract_path)]
            
            if output_format == "json":
                cmd.extend(["-o", "json"])
            
            # Add execution timeout
            cmd.extend(["--execution-timeout", str(execution_timeout)])
            
            # Add solver timeout
            solver_timeout = self.params.get("solver_timeout", 10000)
            cmd.extend(["--solver-timeout", str(solver_timeout)])
            
            # Add max depth if specified
            if "max_depth" in self.params:
                cmd.extend(["--max-depth", str(self.params["max_depth"])])
            
            # Add strategy if specified
            strategy = self.params.get("strategy", "dfs")
            cmd.extend(["--strategy", strategy])
            
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            
            # Execute Mythril
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.params.get("timeout", 1800),  # 30 minute timeout
                cwd=contract_path.parent
            )
            
            # Parse results
            if output_format == "json":
                try:
                    mythril_output = json.loads(result.stdout) if result.stdout else {}
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as text output
                    mythril_output = {"raw_output": result.stdout, "error": result.stderr}
            else:
                mythril_output = {"output": result.stdout, "error": result.stderr}
            
            # Process and categorize findings
            findings = self._process_mythril_findings(mythril_output)
            
            # Generate summary
            summary = self._generate_mythril_summary(findings)
            
            analysis_result = {
                "contract_path": str(contract_path),
                "mythril_version": self._get_mythril_version(),
                "analysis_time": self.duration,
                "summary": summary,
                "findings": findings,
                "raw_output": mythril_output if self.params.get("include_raw", False) else None,
                "command_used": " ".join(cmd),
                "exit_code": result.returncode
            }
            
            if result.returncode != 0:
                self.logger.warning(f"Mythril exited with code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Mythril stderr: {result.stderr}")
                    analysis_result["errors"] = result.stderr
            
            self.logger.info(f"Mythril analysis completed. Found {len(findings)} issues.")
            return analysis_result
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Mythril analysis timed out after {self.params.get('timeout', 1800)} seconds")
        except Exception as e:
            self.logger.error(f"Mythril analysis failed: {str(e)}")
            raise RuntimeError(f"Mythril analysis failed: {str(e)}")
    
    def _process_mythril_findings(self, mythril_output: Dict) -> List[Dict[str, Any]]:
        """Process and normalize Mythril findings."""
        findings = []
        
        if "issues" in mythril_output:
            for issue in mythril_output["issues"]:
                finding = {
                    "swc_id": issue.get("swc-id", "unknown"),
                    "title": issue.get("title", ""),
                    "description": issue.get("description", ""),
                    "severity": issue.get("severity", "unknown").lower(),
                    "contract": issue.get("contract", ""),
                    "function": issue.get("function", ""),
                    "address": issue.get("address", ""),
                    "lineno": issue.get("lineno", 0),
                    "code": issue.get("code", ""),
                    "transaction_sequence": issue.get("transaction_sequence", {})
                }
                
                # Standardize severity levels
                finding["severity"] = self._standardize_mythril_severity(finding["severity"])
                
                findings.append(finding)
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}
        findings.sort(key=lambda x: severity_order.get(x["severity"], 5))
        
        return findings
    
    def _standardize_mythril_severity(self, severity: str) -> str:
        """Standardize Mythril severity levels."""
        severity_mapping = {
            "high": "High",
            "medium": "Medium", 
            "low": "Low"
        }
        return severity_mapping.get(severity.lower(), "Informational")
    
    def _generate_mythril_summary(self, findings: List[Dict]) -> Dict[str, Any]:
        """Generate a summary of Mythril findings."""
        summary = {
            "total_issues": len(findings),
            "by_severity": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0},
            "by_swc": {},
            "critical_issues": []
        }
        
        for finding in findings:
            severity = finding["severity"]
            swc_id = finding["swc_id"]
            
            summary["by_severity"][severity] += 1
            summary["by_swc"][swc_id] = summary["by_swc"].get(swc_id, 0) + 1
            
            # Track high severity issues for quick review
            if severity in ["Critical", "High"]:
                summary["critical_issues"].append({
                    "swc_id": swc_id,
                    "title": finding["title"],
                    "description": finding["description"][:200] + "..." if len(finding["description"]) > 200 else finding["description"]
                })
        
        return summary
    
    def _get_mythril_version(self) -> str:
        """Get Mythril version."""
        try:
            result = subprocess.run(["myth", "version"], capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"
