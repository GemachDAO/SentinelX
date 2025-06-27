# SentinelX Lateral Movement Toolkit Documentation

## Overview

The SentinelX Lateral Movement Toolkit provides advanced capabilities for network traversal, pivoting, and lateral movement techniques used in penetration testing and red team operations. This toolkit integrates with `pwncat-cs` for powerful post-exploitation capabilities and supports multiple attack vectors.

## ⚠️ Legal and Ethical Notice

**FOR AUTHORIZED SECURITY TESTING ONLY**

This toolkit must only be used for:
- Authorized penetration testing with explicit written permission
- Internal security assessments within your organization
- Red team exercises with proper authorization
- Educational purposes in controlled environments

Unauthorized use may violate local, state, and federal laws. Always obtain proper authorization before conducting any lateral movement activities.

## Features

### 🎯 **Core Capabilities**
- **Network Discovery** - Advanced host and service enumeration
- **pwncat-cs Integration** - Powerful post-exploitation framework
- **Multi-Protocol Support** - SSH, SMB, RDP, WMI, PowerShell
- **Pivoting & Tunneling** - SOCKS proxies, port forwarding, covert channels
- **Session Management** - Multiple concurrent sessions with pivot chains
- **Automated Exploitation** - Credential testing and vulnerability exploitation

### 🔧 **Supported Techniques**
1. **Network Scanning** - Comprehensive host and port discovery
2. **pwncat Sessions** - Reverse/bind shells with full post-exploitation
3. **SMB Lateral Movement** - Pass-the-hash, relay attacks, share enumeration
4. **SSH Pivoting** - Tunneling, port forwarding, key-based authentication
5. **RDP Exploitation** - Credential attacks, session hijacking
6. **WMI Attacks** - Remote execution, persistence, DCOM exploitation
7. **PowerShell Remoting** - WinRM, command execution, credential harvesting
8. **Pivot Chains** - Multi-hop lateral movement through compromised hosts
9. **Covert Tunneling** - DNS, HTTP, ICMP tunnels for stealth communication
10. **Port Forwarding** - Local, remote, and dynamic port forwarding

## Lateral Movement Techniques

### 1. Network Discovery
Comprehensive network reconnaissance and service enumeration.

**Parameters:**
- `technique`: "scan"
- `network_range`: CIDR notation (e.g., "192.168.1.0/24")
- `host`: Single target host

**Features:**
- Live host detection via ping
- Advanced port scanning (30+ common ports)
- Service version detection
- Quick vulnerability assessment
- Network topology mapping

### 2. pwncat-cs Integration
Advanced post-exploitation using the pwncat-cs framework.

**Parameters:**
- `technique`: "pwncat"
- `host`: Target host
- `payload_type`: "reverse_shell", "bind_shell", "ssh", "winrm"
- `listen_port`: Listener port for shells
- `credentials`: Authentication credentials

**Capabilities:**
- Reverse and bind shell management
- SSH and WinRM session establishment
- Post-exploitation automation
- Privilege escalation modules
- Persistence mechanisms
- Network enumeration from compromised hosts

### 3. SMB Lateral Movement
Advanced SMB-based lateral movement techniques.

**Parameters:**
- `technique`: "smb"
- `host`: Target host
- `credentials`: Username, password, NTLM hash

**Attack Vectors:**
- Pass-the-hash attacks
- SMB relay attacks
- EternalBlue exploitation (MS17-010)
- Null session enumeration
- Share enumeration and access
- SMB signing bypass

### 4. SSH Pivoting
SSH-based lateral movement and pivoting.

**Parameters:**
- `technique`: "ssh"
- `host`: Target host
- `credentials`: Username, password, private_key

**Capabilities:**
- SSH session establishment
- Local port forwarding
- Remote port forwarding
- Dynamic port forwarding (SOCKS proxy)
- SSH key enumeration
- Multi-hop SSH tunneling

### 5. RDP Exploitation
Remote Desktop Protocol exploitation and lateral movement.

**Parameters:**
- `technique`: "rdp"
- `host`: Target host
- `credentials`: Username, password

**Attack Techniques:**
- Credential brute forcing
- BlueKeep exploitation (CVE-2019-0708)
- RDP session hijacking
- Sticky keys backdoor
- Registry modification via RDP

### 6. WMI Attacks
Windows Management Instrumentation lateral movement.

**Parameters:**
- `technique`: "wmi"
- `host`: Target host
- `credentials`: Username, password, domain

**Capabilities:**
- WMI command execution
- Pass-the-hash via WMI
- DCOM lateral movement
- WMI event subscriptions for persistence
- Registry access and modification
- Service management

### 7. PowerShell Remoting
PowerShell-based lateral movement and execution.

**Parameters:**
- `technique`: "powershell"
- `host`: Target host
- `credentials`: Username, password, domain

**Features:**
- WinRM connectivity testing
- PowerShell remote execution
- Credential harvesting
- Registry manipulation
- Alternative execution methods
- AMSI and execution policy bypass

### 8. Pivot Chains
Multi-hop lateral movement through compromised hosts.

**Parameters:**
- `technique`: "pivot"
- `host`: Pivot host
- `credentials`: Authentication credentials

**Capabilities:**
- SOCKS proxy creation
- Multi-hop pivoting
- Network enumeration from pivot
- Pivot chain management
- Reachable network discovery

### 9. Covert Tunneling
Stealth communication channels for covert operations.

**Parameters:**
- `technique`: "tunnel"
- `host`: Target host
- `credentials`: Authentication credentials

**Tunnel Types:**
- DNS tunneling via TXT records
- HTTP/HTTPS tunneling
- ICMP tunneling
- SSH tunneling
- Covert channel analysis

### 10. Port Forwarding
Advanced port forwarding for service access.

**Parameters:**
- `technique`: "port_forward"
- `host`: Target host
- `credentials`: Authentication credentials

**Forward Types:**
- Local port forwarding (bring remote services local)
- Remote port forwarding (expose local services remotely)
- Dynamic port forwarding (SOCKS proxy)
- Multi-hop port forwarding

## Usage Examples

### Basic Network Discovery
```python
from sentinelx.redteam.lateral_move import LateralMovement

# Network scan
task = LateralMovement(
    name="network_scan",
    params={
        "technique": "scan",
        "network_range": "192.168.1.0/24"
    }
)

results = await task.run()
```

### pwncat-cs Reverse Shell
```python
task = LateralMovement(
    name="pwncat_reverse_shell",
    params={
        "technique": "pwncat",
        "host": "192.168.1.100",
        "payload_type": "reverse_shell",
        "listen_port": 4444,
        "credentials": {
            "username": "admin",
            "password": "password123"
        }
    }
)

results = await task.run()
```

### SMB Lateral Movement
```python
task = LateralMovement(
    name="smb_lateral_move",
    params={
        "technique": "smb",
        "host": "192.168.1.50",
        "credentials": {
            "username": "administrator",
            "password": "admin123",
            "ntlm_hash": "aad3b435b51404eeaad3b435b51404ee:5fbc3d5fec8206a30f4b6c473d68ae76"
        }
    }
)

results = await task.run()
```

### SSH Pivoting
```python
task = LateralMovement(
    name="ssh_pivot",
    params={
        "technique": "ssh",
        "host": "10.0.0.50",
        "credentials": {
            "username": "ubuntu",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\n..."
        }
    }
)

results = await task.run()
```

### Comprehensive Assessment
```python
task = LateralMovement(
    name="comprehensive_lateral_move",
    params={
        "technique": "comprehensive",
        "host": "192.168.1.100",
        "network_range": "192.168.1.0/24",
        "credentials": {
            "username": "admin",
            "password": "password123",
            "domain": "CORPORATE"
        }
    }
)

results = await task.run()
```

## Credential Formats

### Basic Authentication
```python
credentials = {
    "username": "admin",
    "password": "password123",
    "domain": "CORPORATE"  # Optional for Windows
}
```

### SSH Key Authentication
```python
credentials = {
    "username": "ubuntu",
    "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...",
    "passphrase": "key_passphrase"  # Optional
}
```

### Pass-the-Hash
```python
credentials = {
    "username": "administrator",
    "ntlm_hash": "aad3b435b51404eeaad3b435b51404ee:5fbc3d5fec8206a30f4b6c473d68ae76",
    "domain": "CORPORATE"
}
```

## Output Structure

### Network Discovery Results
```python
results = {
    "technique": "scan",
    "discovery": {
        "target": "192.168.1.0/24",
        "live_hosts": ["192.168.1.1", "192.168.1.100"],
        "open_ports": {
            "192.168.1.100": [22, 80, 443, 3389]
        },
        "services": {
            "192.168.1.100": {
                22: {"name": "SSH", "description": "Secure Shell"},
                80: {"name": "HTTP", "description": "Web Server"}
            }
        },
        "vulnerabilities": [
            {
                "host": "192.168.1.100",
                "port": 3389,
                "vulnerability": "Potential BlueKeep (CVE-2019-0708)",
                "severity": "critical"
            }
        ]
    }
}
```

### pwncat Session Results
```python
results = {
    "technique": "pwncat",
    "pwncat_analysis": {
        "session_established": True,
        "session_id": "reverse_192.168.1.100_4444",
        "post_exploitation": {
            "system_info": {
                "os": "Linux",
                "hostname": "web-server",
                "current_user": "www-data"
            },
            "privilege_escalation": {
                "techniques_attempted": ["sudo -i", "SUID binaries"],
                "success": False
            },
            "credential_harvesting": {
                "credentials_found": 2,
                "files_of_interest": ["/etc/passwd", "~/.ssh/authorized_keys"]
            }
        },
        "persistence": {
            "successful_methods": ["SSH key persistence"]
        }
    }
}
```

## Advanced Features

### Session Management
The toolkit maintains active sessions for reuse and pivot chaining:

```python
# Sessions are stored in self.active_sessions
session_info = {
    "id": "ssh_192.168.1.100_admin",
    "type": "ssh",
    "host": "192.168.1.100",
    "status": "active",
    "capabilities": ["tunneling", "pivoting", "file_transfer"]
}
```

### Pivot Chain Creation
Multi-hop lateral movement through compromised hosts:

```python
pivot_chain = {
    "hop_1": {"host": "192.168.1.100", "method": "ssh"},
    "hop_2": {"host": "10.0.0.50", "method": "ssh"},
    "final_target": "172.16.0.100",
    "socks_proxy": {"port": 1080, "status": "active"}
}
```

### Covert Channel Analysis
Stealth communication assessment:

```python
covert_channels = [
    {
        "type": "DNS",
        "method": "TXT record exfiltration",
        "covert_rating": "high",
        "detection_difficulty": "high"
    },
    {
        "type": "ICMP",
        "method": "Data payload tunneling",
        "covert_rating": "high",
        "detection_difficulty": "high"
    }
]
```

## Integration with pwncat-cs

### Installation
```bash
pip install pwncat-cs
```

### Key Features
- **Session Management**: Automatic session handling and persistence
- **Post-Exploitation**: Built-in modules for privilege escalation
- **Persistence**: Automatic backdoor installation
- **Pivoting**: Network traversal and tunneling
- **File Operations**: Upload/download capabilities
- **Enumeration**: Comprehensive system enumeration

### pwncat Commands
Common pwncat-cs commands available through the toolkit:

```bash
# Establish reverse shell listener
pwncat-cs -lp 4444

# Connect to bind shell
pwncat-cs connect://192.168.1.100:4444

# SSH connection
pwncat-cs ssh://user@192.168.1.100

# Upload file
upload /local/file.txt /remote/path/

# Download file
download /remote/file.txt /local/path/

# Create SOCKS proxy
proxy --port 1080

# Enumerate system
enumerate
```

## Best Practices

### Planning Phase
1. **Obtain Authorization**: Written permission for all lateral movement activities
2. **Scope Definition**: Clear boundaries and target networks
3. **Risk Assessment**: Understand potential impact of lateral movement
4. **Credential Management**: Secure handling of harvested credentials
5. **Documentation**: Detailed logging of all activities

### Execution Phase
1. **Start Conservatively**: Begin with passive reconnaissance
2. **Maintain Stealth**: Use covert channels when possible
3. **Session Management**: Properly manage and clean up sessions
4. **Pivot Carefully**: Test connectivity before establishing pivots
5. **Monitor Detection**: Watch for security alerts and responses

### Post-Exploitation
1. **Comprehensive Enumeration**: Gather complete system information
2. **Credential Harvesting**: Collect credentials for further movement
3. **Persistence**: Establish reliable backdoors
4. **Cleanup**: Remove traces and temporary files
5. **Documentation**: Record all findings and access paths

## Security Considerations

### Operational Security
- Use encrypted communication channels
- Rotate credentials and backdoors regularly
- Monitor for defensive responses
- Maintain multiple exit strategies

### Detection Avoidance
- Randomize timing between operations
- Use legitimate tools and techniques
- Blend with normal network traffic
- Avoid signature-based detection

### Incident Response
- Have cleanup procedures ready
- Maintain detailed activity logs
- Be prepared to explain actions if detected
- Coordinate with defensive teams if applicable

## Troubleshooting

### Common Issues

1. **Session Timeouts**
   - Increase timeout values
   - Use keep-alive mechanisms
   - Monitor network stability

2. **Authentication Failures**
   - Verify credential format
   - Check account lockout policies
   - Test authentication methods

3. **Network Connectivity**
   - Verify network paths
   - Check firewall rules
   - Test port accessibility

4. **pwncat-cs Integration**
   - Ensure proper installation
   - Check Python dependencies
   - Verify listener configuration

### Performance Optimization
- Use asynchronous operations for scanning
- Limit concurrent connections
- Optimize payload sizes
- Cache session information

## Integration with Other SentinelX Modules

### Exploit Integration
- Use exploit modules to gain initial access
- Chain exploits with lateral movement
- Combine binary exploitation with network pivoting

### Social Engineering
- Use social engineering for credential harvesting
- Combine phishing with lateral movement
- Leverage trust relationships for movement

### Forensics Integration
- Analyze lateral movement artifacts
- Investigate attack paths
- Study persistence mechanisms

## Advanced Techniques

### Living Off The Land
- Use built-in system tools
- Leverage legitimate software
- Avoid custom malware detection

### Multi-Stage Attacks
- Chain multiple techniques together
- Use different protocols for each stage
- Implement fallback mechanisms

### Persistence Mechanisms
- Registry modifications
- Service installations
- Scheduled tasks
- WMI event subscriptions

## Future Enhancements

### Planned Features
- Machine learning for path optimization
- Automated credential correlation
- Enhanced stealth capabilities
- Cloud environment support

### Community Contributions
- Custom technique implementations
- Platform-specific modules
- Detection evasion techniques
- Performance improvements

---

*This documentation is part of the SentinelX Security Framework. For updates and additional resources, visit the project repository.*
