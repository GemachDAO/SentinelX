from __future__ import annotations
import asyncio
import socket
import subprocess
import json
import platform
from typing import Dict, Any, List, Optional
from ..core.task import Task

class LateralMove(Task):
    """Network lateral movement techniques for red team operations"""
    
    async def run(self):
        """Execute lateral movement techniques"""
        target_host = self.params.get("host")
        technique = self.params.get("technique", "scan")  # scan, smb, rdp, ssh, wmi
        credentials = self.params.get("credentials", {})
        network_range = self.params.get("network_range")
        
        if not target_host and not network_range:
            return {"error": "Either target_host or network_range parameter is required"}
            
        try:
            results = {
                "technique": technique,
                "timestamp": asyncio.get_running_loop().time(),
                "findings": [],
                "successful_moves": [],
                "failed_attempts": []
            }
            
            if technique == "scan":
                scan_results = await self._network_discovery(target_host or network_range)
                results["discovery"] = scan_results
                
            elif technique == "smb":
                smb_results = await self._smb_lateral_move(target_host, credentials)
                results["smb_analysis"] = smb_results
                
            elif technique == "rdp":
                rdp_results = await self._rdp_lateral_move(target_host, credentials)
                results["rdp_analysis"] = rdp_results
                
            elif technique == "ssh":
                ssh_results = await self._ssh_lateral_move(target_host, credentials)
                results["ssh_analysis"] = ssh_results
                
            elif technique == "wmi":
                wmi_results = await self._wmi_lateral_move(target_host, credentials)
                results["wmi_analysis"] = wmi_results
                
            elif technique == "comprehensive":
                # Run all techniques
                results["discovery"] = await self._network_discovery(target_host or network_range)
                if target_host:
                    results["smb_analysis"] = await self._smb_lateral_move(target_host, credentials)
                    results["rdp_analysis"] = await self._rdp_lateral_move(target_host, credentials)
                    results["ssh_analysis"] = await self._ssh_lateral_move(target_host, credentials)
                    results["wmi_analysis"] = await self._wmi_lateral_move(target_host, credentials)
                    
            else:
                return {"error": f"Unknown technique: {technique}"}
                
            return results
            
        except Exception as e:
            return {"error": f"Lateral movement failed: {str(e)}"}
            
    async def _network_discovery(self, target: str) -> Dict[str, Any]:
        """Discover live hosts and services on the network"""
        discovery = {
            "target": target,
            "live_hosts": [],
            "open_ports": {},
            "services": {},
            "vulnerabilities": []
        }
        
        try:
            # Check if target is single host or range
            if "/" in target:  # CIDR notation
                hosts = await self._scan_network_range(target)
            else:
                hosts = [target]
                
            # Scan each host
            for host in hosts:
                if await self._is_host_alive(host):
                    discovery["live_hosts"].append(host)
                    
                    # Port scan
                    open_ports = await self._port_scan(host)
                    if open_ports:
                        discovery["open_ports"][host] = open_ports 
                        
                    # Service detection
                    services = await self._service_detection(host, open_ports)
                    if services:
                        discovery["services"][host] = services
                        
        except Exception as e:
            discovery["error"] = f"Network discovery failed: {str(e)}"
            
        return discovery
        
    async def _smb_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Attempt SMB-based lateral movement"""
        smb_analysis = {
            "target": host,
            "smb_version": "unknown",
            "shares_accessible": [],
            "credentials_valid": False,
            "lateral_move_possible": False,
            "findings": []
        }
        
        try:
            # Check if SMB port is open
            if not await self._check_port(host, 445):
                smb_analysis["findings"].append("SMB port 445 not accessible")
                return smb_analysis
                
            # Try to enumerate SMB shares (requires smbclient or similar)
            # This is a simulation - in production you'd use tools like smbclient, crackmapexec
            smb_analysis["findings"].append("SMB service detected on port 445")
            
            # Simulate credential testing
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            
            if username and password:
                # In production, test credentials with smbclient or impacket
                smb_analysis["credentials_valid"] = "simulated_test"
                smb_analysis["findings"].append(f"Testing credentials: {username}:{'*' * len(password)}")
                
            # Common SMB attack vectors
            smb_analysis["attack_vectors"] = [
                "Pass-the-hash attacks",
                "SMB relay attacks", 
                "Eternal Blue exploitation (MS17-010)",
                "SMB signing disabled",
                "Null session enumeration"
            ]
            
        except Exception as e:
            smb_analysis["error"] = f"SMB analysis failed: {str(e)}"
            
        return smb_analysis
        
    async def _rdp_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Attempt RDP-based lateral movement"""
        rdp_analysis = {
            "target": host,
            "rdp_accessible": False,
            "credentials_valid": False,
            "rdp_security": {},
            "findings": []
        }
        
        try:
            # Check RDP port
            if await self._check_port(host, 3389):
                rdp_analysis["rdp_accessible"] = True
                rdp_analysis["findings"].append("RDP service accessible on port 3389")
                
                # RDP security checks
                rdp_analysis["rdp_security"] = {
                    "nla_enabled": "unknown",  # Network Level Authentication
                    "encryption_level": "unknown",
                    "allow_rdp_connections": True
                }
                
                # Simulate credential testing
                username = credentials.get("username", "")
                password = credentials.get("password", "")
                
                if username and password:
                    rdp_analysis["findings"].append(f"Would test RDP login: {username}")
                    
                # RDP attack vectors
                rdp_analysis["attack_vectors"] = [
                    "Credential brute forcing",
                    "BlueKeep exploitation (CVE-2019-0708)",
                    "RDP session hijacking",
                    "Pass-the-hash via RDP"
                ]
            else:
                rdp_analysis["findings"].append("RDP port 3389 not accessible")
                
        except Exception as e:
            rdp_analysis["error"] = f"RDP analysis failed: {str(e)}"
            
        return rdp_analysis
        
    async def _ssh_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Attempt SSH-based lateral movement"""
        ssh_analysis = {
            "target": host,
            "ssh_accessible": False,
            "ssh_version": "unknown",
            "auth_methods": [],
            "findings": []
        }
        
        try:
            # Check SSH port
            if await self._check_port(host, 22):
                ssh_analysis["ssh_accessible"] = True
                ssh_analysis["findings"].append("SSH service accessible on port 22")
                
                # SSH version detection (simulated)
                ssh_analysis["ssh_version"] = "OpenSSH_7.4"
                ssh_analysis["auth_methods"] = ["password", "publickey"]
                
                # Simulate credential testing
                username = credentials.get("username", "")
                password = credentials.get("password", "")
                private_key = credentials.get("private_key", "")
                
                if username and (password or private_key):
                    ssh_analysis["findings"].append(f"Would test SSH login: {username}")
                    
                # SSH attack vectors
                ssh_analysis["attack_vectors"] = [
                    "Credential brute forcing",
                    "SSH key-based authentication",
                    "SSH tunneling for pivoting",
                    "Weak SSH configurations"
                ]
            else:
                ssh_analysis["findings"].append("SSH port 22 not accessible")
                
        except Exception as e:
            ssh_analysis["error"] = f"SSH analysis failed: {str(e)}"
            
        return ssh_analysis
        
    async def _wmi_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Attempt WMI-based lateral movement (Windows only)"""
        wmi_analysis = {
            "target": host,
            "wmi_accessible": False,
            "credentials_valid": False,
            "findings": []
        }
        
        try:
            # WMI typically uses RPC (port 135) and dynamic ports
            if await self._check_port(host, 135):
                wmi_analysis["wmi_accessible"] = True
                wmi_analysis["findings"].append("WMI/RPC service accessible on port 135")
                
                # Simulate WMI credential testing
                username = credentials.get("username", "")
                password = credentials.get("password", "")
                domain = credentials.get("domain", "")
                
                if username and password:
                    wmi_analysis["findings"].append(f"Would test WMI authentication: {domain}\\{username}")
                    
                # WMI attack vectors
                wmi_analysis["attack_vectors"] = [
                    "WMI command execution",
                    "WMI event subscriptions for persistence",
                    "DCOM lateral movement",
                    "Pass-the-hash via WMI"
                ]
            else:
                wmi_analysis["findings"].append("WMI/RPC port 135 not accessible")
                
        except Exception as e:
            wmi_analysis["error"] = f"WMI analysis failed: {str(e)}"
            
        return wmi_analysis
        
    async def _scan_network_range(self, cidr: str) -> List[str]:
        """Generate list of hosts from CIDR range"""
        # Simplified - in production use ipaddress module
        base_ip = cidr.split('/')[0]
        base_parts = base_ip.split('.')
        hosts = []
        
        # Generate first 10 hosts for demo
        for i in range(1, 11):
            host = f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}"
            hosts.append(host)
            
        return hosts
        
    async def _is_host_alive(self, host: str) -> bool:
        """Check if host is alive using ping"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ping", "-n", "1", host], 
                                      capture_output=True, text=True, timeout=3)
            else:
                result = subprocess.run(["ping", "-c", "1", host], 
                                      capture_output=True, text=True, timeout=3)
            return result.returncode == 0
        except:
            return False
            
    async def _port_scan(self, host: str) -> List[int]:
        """Scan common ports on target host"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 3389, 5985, 5986]
        open_ports = []
        
        for port in common_ports:
            if await self._check_port(host, port):
                open_ports.append(port)
                
        return open_ports
        
    async def _check_port(self, host: str, port: int) -> bool:
        """Check if specific port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
            
    async def _service_detection(self, host: str, ports: List[int]) -> Dict[int, str]:
        """Detect services running on open ports"""
        services = {}
        
        # Common service mappings
        service_map = {
            21: "FTP",
            22: "SSH", 
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            135: "RPC/WMI",
            139: "NetBIOS-SSN",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            3389: "RDP",
            5985: "WinRM HTTP",
            5986: "WinRM HTTPS"
        }
        
        for port in ports:
            if port in service_map:
                services[port] = service_map[port]
            else:
                services[port] = "Unknown"
                
        return services
