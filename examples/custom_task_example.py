#!/usr/bin/env python3
"""
Custom Task Development Example

This example demonstrates how to create custom security tasks for SentinelX,
including proper task registration, parameter validation, and result formatting.
"""

import asyncio
import json
import logging
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from sentinelx.core.task import Task, register_task, task_metadata
from sentinelx.core.context import Context
from sentinelx.core.registry import PluginRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@register_task("file-hash-analyzer")
@task_metadata(
    category="forensics",
    description="Analyze file hashes and detect suspicious files",
    tags=["forensics", "malware", "hash-analysis"],
    version="1.0.0",
    author="SentinelX Team"
)
class FileHashAnalyzer(Task):
    """
    Custom task that analyzes file hashes and checks them against
    known malware databases and suspicious file indicators.
    """
    
    # Define required and optional parameters
    REQUIRED_PARAMS = ["file_path"]
    OPTIONAL_PARAMS = ["hash_types", "check_virustotal", "output_format"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.supported_hash_types = ["md5", "sha1", "sha256", "sha512"]
        
    async def execute(self, context: Context, **kwargs) -> Dict[str, Any]:
        """
        Execute file hash analysis.
        
        Args:
            context: Execution context
            **kwargs: Task parameters
            
        Returns:
            Analysis results dictionary
        """
        # Extract parameters
        file_path = kwargs["file_path"]
        hash_types = kwargs.get("hash_types", ["md5", "sha1", "sha256"])
        check_virustotal = kwargs.get("check_virustotal", False)
        output_format = kwargs.get("output_format", "json")
        
        logger.info(f"Starting file hash analysis for: {file_path}")
        
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            # Calculate file hashes
            hashes = self._calculate_hashes(file_path, hash_types)
            
            # Get file metadata
            metadata = self._get_file_metadata(file_path)
            
            # Perform hash analysis
            analysis_results = await self._analyze_hashes(hashes, context)
            
            # Check against threat intelligence (if enabled)
            threat_intel = {}
            if check_virustotal:
                threat_intel = await self._check_threat_intelligence(hashes, context)
            
            # Generate suspicious indicators
            indicators = self._generate_indicators(hashes, metadata, analysis_results)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(analysis_results, threat_intel, indicators)
            
            # Prepare results
            results = {
                "status": "completed",
                "file_path": file_path,
                "file_metadata": metadata,
                "hashes": hashes,
                "hash_analysis": analysis_results,
                "threat_intelligence": threat_intel,
                "suspicious_indicators": indicators,
                "risk_score": risk_score,
                "timestamp": context.get_timestamp(),
                "recommendations": self._generate_recommendations(risk_score, indicators)
            }
            
            logger.info(f"File hash analysis completed. Risk score: {risk_score}")
            return results
            
        except Exception as e:
            logger.error(f"File hash analysis failed: {e}")
            raise
    
    def _calculate_hashes(self, file_path: str, hash_types: List[str]) -> Dict[str, str]:
        """Calculate various hash types for the file."""
        hashes = {}
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            for hash_type in hash_types:
                if hash_type.lower() in self.supported_hash_types:
                    if hash_type.lower() == "md5":
                        hashes["md5"] = hashlib.md5(file_data).hexdigest()
                    elif hash_type.lower() == "sha1":
                        hashes["sha1"] = hashlib.sha1(file_data).hexdigest()
                    elif hash_type.lower() == "sha256":
                        hashes["sha256"] = hashlib.sha256(file_data).hexdigest()
                    elif hash_type.lower() == "sha512":
                        hashes["sha512"] = hashlib.sha512(file_data).hexdigest()
                        
        except Exception as e:
            logger.error(f"Failed to calculate hashes: {e}")
            raise
            
        return hashes
    
    def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract file metadata."""
        file_obj = Path(file_path)
        stat = file_obj.stat()
        
        return {
            "filename": file_obj.name,
            "size": stat.st_size,
            "modified_time": stat.st_mtime,
            "created_time": stat.st_ctime if hasattr(stat, 'st_ctime') else None,
            "permissions": oct(stat.st_mode)[-3:],
            "extension": file_obj.suffix.lower()
        }
    
    async def _analyze_hashes(self, hashes: Dict[str, str], context: Context) -> Dict[str, Any]:
        """Analyze hashes for suspicious patterns."""
        analysis = {
            "entropy_analysis": {},
            "pattern_analysis": {},
            "known_malware_hashes": [],
            "suspicious_characteristics": []
        }
        
        # Check for known malware hashes (simplified example)
        known_malware = context.get("known_malware_hashes", [])
        for hash_type, hash_value in hashes.items():
            if hash_value.lower() in [h.lower() for h in known_malware]:
                analysis["known_malware_hashes"].append({
                    "hash_type": hash_type,
                    "hash_value": hash_value,
                    "threat_level": "high"
                })
        
        # Analyze hash characteristics
        for hash_type, hash_value in hashes.items():
            # Check for suspicious patterns (e.g., too many zeros, patterns)
            zero_count = hash_value.count('0')
            if zero_count > len(hash_value) * 0.3:  # More than 30% zeros
                analysis["suspicious_characteristics"].append(
                    f"{hash_type} hash has unusually high number of zeros ({zero_count})"
                )
            
            # Check for repeated patterns
            if len(set(hash_value)) < len(hash_value) * 0.5:  # Less than 50% unique characters
                analysis["suspicious_characteristics"].append(
                    f"{hash_type} hash shows repeated patterns, may indicate crafted hash"
                )
        
        return analysis
    
    async def _check_threat_intelligence(self, hashes: Dict[str, str], context: Context) -> Dict[str, Any]:
        """Check hashes against threat intelligence sources."""
        threat_intel = {
            "virustotal_results": {},
            "threat_feeds": [],
            "reputation_score": 0
        }
        
        # Simulate VirusTotal API check (in real implementation, use actual API)
        vt_api_key = context.get("virustotal_api_key")
        if vt_api_key:
            logger.info("Checking hashes against VirusTotal (simulated)")
            # In real implementation, make actual API calls
            threat_intel["virustotal_results"] = {
                "checked": True,
                "detections": 0,  # Simulated result
                "scan_date": context.get_timestamp(),
                "permalink": f"https://virustotal.com/file/{hashes.get('sha256', '')}/analysis/"
            }
        
        return threat_intel
    
    def _generate_indicators(self, hashes: Dict[str, str], metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suspicious indicators based on analysis."""
        indicators = []
        
        # File size indicators
        if metadata["size"] == 0:
            indicators.append({
                "type": "file_characteristics",
                "indicator": "zero_byte_file",
                "description": "File has zero bytes, may be a placeholder or damaged",
                "severity": "medium"
            })
        elif metadata["size"] > 100 * 1024 * 1024:  # > 100MB
            indicators.append({
                "type": "file_characteristics", 
                "indicator": "large_file_size",
                "description": f"Large file size ({metadata['size']} bytes) may indicate packed malware",
                "severity": "low"
            })
        
        # Extension indicators
        suspicious_extensions = [".exe", ".scr", ".bat", ".cmd", ".pif", ".com"]
        if metadata["extension"] in suspicious_extensions:
            indicators.append({
                "type": "file_extension",
                "indicator": "suspicious_extension",
                "description": f"File extension '{metadata['extension']}' is commonly used by malware",
                "severity": "medium"
            })
        
        # Hash analysis indicators
        if analysis["known_malware_hashes"]:
            indicators.append({
                "type": "hash_match",
                "indicator": "known_malware_hash",
                "description": "File hash matches known malware signature",
                "severity": "critical"
            })
        
        return indicators
    
    def _calculate_risk_score(self, analysis: Dict[str, Any], threat_intel: Dict[str, Any], indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall risk score for the file."""
        base_score = 0
        
        # Score based on known malware matches
        if analysis["known_malware_hashes"]:
            base_score += 80
        
        # Score based on suspicious characteristics
        base_score += len(analysis["suspicious_characteristics"]) * 10
        
        # Score based on threat intelligence
        if threat_intel.get("virustotal_results", {}).get("detections", 0) > 0:
            base_score += 60
        
        # Score based on indicators
        for indicator in indicators:
            severity = indicator.get("severity", "low")
            if severity == "critical":
                base_score += 40
            elif severity == "high":
                base_score += 30
            elif severity == "medium":
                base_score += 15
            elif severity == "low":
                base_score += 5
        
        # Normalize score to 0-100
        normalized_score = min(base_score, 100)
        
        # Determine risk level
        if normalized_score >= 80:
            risk_level = "critical"
        elif normalized_score >= 60:
            risk_level = "high"
        elif normalized_score >= 40:
            risk_level = "medium"
        elif normalized_score >= 20:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        return {
            "score": normalized_score,
            "level": risk_level,
            "factors": {
                "malware_matches": len(analysis["known_malware_hashes"]),
                "suspicious_characteristics": len(analysis["suspicious_characteristics"]),
                "threat_intel_detections": threat_intel.get("virustotal_results", {}).get("detections", 0),
                "indicators_count": len(indicators)
            }
        }
    
    def _generate_recommendations(self, risk_score: Dict[str, Any], indicators: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on analysis."""
        recommendations = []
        
        if risk_score["level"] == "critical":
            recommendations.extend([
                "🚨 CRITICAL: Quarantine this file immediately",
                "🔒 Block file hash in security controls",
                "🔍 Investigate system for signs of compromise",
                "📊 Run full antimalware scan on affected systems"
            ])
        elif risk_score["level"] == "high":
            recommendations.extend([
                "⚠️ HIGH RISK: Review file carefully before execution",
                "🛡️ Run in sandboxed environment if analysis required",
                "🔍 Check file with multiple antivirus engines"
            ])
        elif risk_score["level"] == "medium":
            recommendations.extend([
                "📋 MEDIUM RISK: Exercise caution with this file",
                "🔍 Consider additional analysis if file behavior is suspicious"
            ])
        else:
            recommendations.extend([
                "✅ File appears to have low security risk",
                "💡 Continue monitoring file behavior if executed"
            ])
        
        # Add specific recommendations based on indicators
        for indicator in indicators:
            if indicator["type"] == "file_extension":
                recommendations.append("🔍 Verify file is legitimate executable before running")
            elif indicator["type"] == "hash_match":
                recommendations.append("🚨 File matches known malware - do not execute")
        
        return recommendations


@register_task("network-port-scanner")
@task_metadata(
    category="reconnaissance",
    description="Advanced network port scanner with service detection",
    tags=["network", "reconnaissance", "ports", "services"],
    version="1.0.0"
)
class NetworkPortScanner(Task):
    """
    Custom network port scanning task with advanced features.
    """
    
    REQUIRED_PARAMS = ["target"]
    OPTIONAL_PARAMS = ["ports", "scan_type", "timeout", "threads", "service_detection"]
    
    async def execute(self, context: Context, **kwargs) -> Dict[str, Any]:
        """Execute network port scan."""
        target = kwargs["target"]
        ports = kwargs.get("ports", "1-1000")
        scan_type = kwargs.get("scan_type", "tcp")
        timeout = kwargs.get("timeout", 5)
        threads = kwargs.get("threads", 100)
        service_detection = kwargs.get("service_detection", True)
        
        logger.info(f"Starting port scan of {target}")
        
        try:
            # Parse port range
            port_list = self._parse_port_range(ports)
            
            # Perform port scan
            scan_results = await self._scan_ports(target, port_list, scan_type, timeout, threads)
            
            # Service detection on open ports
            services = {}
            if service_detection and scan_results["open_ports"]:
                services = await self._detect_services(target, scan_results["open_ports"], timeout)
            
            # Generate security assessment
            security_assessment = self._assess_security(scan_results, services)
            
            return {
                "status": "completed",
                "target": target,
                "scan_results": scan_results,
                "services": services,
                "security_assessment": security_assessment,
                "timestamp": context.get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Port scan failed: {e}")
            raise
    
    def _parse_port_range(self, ports: str) -> List[int]:
        """Parse port range specification."""
        port_list = []
        
        for part in ports.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                port_list.extend(range(start, end + 1))
            else:
                port_list.append(int(part))
        
        return sorted(set(port_list))
    
    async def _scan_ports(self, target: str, ports: List[int], scan_type: str, timeout: int, threads: int) -> Dict[str, Any]:
        """Perform the actual port scan."""
        # This is a simplified implementation
        # In practice, you'd use proper socket programming or tools like nmap
        
        open_ports = []
        closed_ports = []
        filtered_ports = []
        
        # Simulate scanning (replace with actual implementation)
        import random
        for port in ports[:10]:  # Limit for demo
            # Simulate random results
            result = random.choice(["open", "closed", "filtered"])
            if result == "open":
                open_ports.append(port)
            elif result == "closed":
                closed_ports.append(port)
            else:
                filtered_ports.append(port)
        
        return {
            "open_ports": open_ports,
            "closed_ports": closed_ports,
            "filtered_ports": filtered_ports,
            "total_scanned": len(ports)
        }
    
    async def _detect_services(self, target: str, open_ports: List[int], timeout: int) -> Dict[int, Dict[str, Any]]:
        """Detect services running on open ports."""
        services = {}
        
        # Common port to service mapping
        common_services = {
            21: "FTP",
            22: "SSH", 
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S"
        }
        
        for port in open_ports:
            service_info = {
                "port": port,
                "service": common_services.get(port, "Unknown"),
                "version": "Unknown",
                "banner": ""
            }
            services[port] = service_info
        
        return services
    
    def _assess_security(self, scan_results: Dict[str, Any], services: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """Assess security based on scan results."""
        risks = []
        recommendations = []
        
        # Check for risky services
        risky_ports = [21, 23, 135, 139, 445]  # FTP, Telnet, RPC, NetBIOS
        for port in scan_results["open_ports"]:
            if port in risky_ports:
                risks.append(f"Port {port} ({services.get(port, {}).get('service', 'Unknown')}) is known to be risky")
        
        # Generate recommendations
        if len(scan_results["open_ports"]) > 10:
            recommendations.append("Consider reducing the number of exposed services")
        
        if 23 in scan_results["open_ports"]:  # Telnet
            recommendations.append("Replace Telnet with SSH for secure remote access")
        
        return {
            "risk_level": "high" if risks else "medium" if scan_results["open_ports"] else "low",
            "risks": risks,
            "recommendations": recommendations
        }


# Example usage and testing functions
async def test_file_hash_analyzer():
    """Test the file hash analyzer task."""
    print("\n=== Testing File Hash Analyzer ===")
    
    # Create a test file
    test_file = Path("test_file.txt")
    test_file.write_text("This is a test file for hash analysis.")
    
    try:
        context = Context.load("config.yaml")
        
        # Create and run the custom task
        task = PluginRegistry.create(
            "file-hash-analyzer",
            file_path=str(test_file),
            hash_types=["md5", "sha256"],
            check_virustotal=False
        )
        
        result = await task.execute(context)
        
        print(f"Analysis completed for: {result['file_path']}")
        print(f"Risk Score: {result['risk_score']['score']} ({result['risk_score']['level']})")
        print(f"Hashes: {json.dumps(result['hashes'], indent=2)}")
        print(f"Indicators: {len(result['suspicious_indicators'])}")
        
        if result['recommendations']:
            print("Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
        
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

async def test_network_port_scanner():
    """Test the network port scanner task."""
    print("\n=== Testing Network Port Scanner ===")
    
    context = Context.load("config.yaml")
    
    # Create and run the custom task
    task = PluginRegistry.create(
        "network-port-scanner",
        target="127.0.0.1",
        ports="21-25,80,443",
        scan_type="tcp",
        service_detection=True
    )
    
    result = await task.execute(context)
    
    print(f"Scan completed for: {result['target']}")
    print(f"Open ports: {result['scan_results']['open_ports']}")
    print(f"Services detected: {len(result['services'])}")
    print(f"Security risk level: {result['security_assessment']['risk_level']}")

async def main():
    """Main example runner."""
    print("SentinelX Custom Task Development Examples")
    print("=" * 50)
    
    # Register our custom tasks
    PluginRegistry.discover()
    
    # Test file hash analyzer
    await test_file_hash_analyzer()
    
    # Test network port scanner
    await test_network_port_scanner()
    
    print("\n" + "=" * 50)
    print("Custom task examples completed!")

if __name__ == "__main__":
    asyncio.run(main())
