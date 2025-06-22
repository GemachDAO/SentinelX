# SentinelX Task Reference

This document provides comprehensive information about all available security tasks in SentinelX.

## Table of Contents

1. [Smart Contract Auditing](#smart-contract-auditing)
2. [Exploit Development](#exploit-development)
3. [Blockchain Security](#blockchain-security)
4. [Red Team Operations](#red-team-operations)
5. [Digital Forensics](#digital-forensics)
6. [AI Security](#ai-security)
7. [Web Security](#web-security)
8. [Task Usage Examples](#task-usage-examples)

## Smart Contract Auditing

### slither - Slither Static Analysis
**Category**: Smart Contract Audit  
**Status**: Production Ready ✅

Performs static analysis of Solidity smart contracts using the Slither analyzer.

#### Parameters
- **contract_path** (required): Path to the Solidity contract file
- **format** (optional): Output format ('json', 'text', 'sarif') - default: 'json'
- **detectors** (optional): Comma-separated list of specific detectors to run
- **exclude** (optional): Comma-separated list of detectors to exclude

#### Example Usage
```bash
# Basic analysis
sentinelx run slither -p "{contract_path: 'MyToken.sol'}"

# With specific format and detectors
sentinelx run slither -p "{
  contract_path: 'contracts/Token.sol',
  format: 'json',
  detectors: 'reentrancy-eth,uninitialized-state'
}"
```

#### Output Format
```yaml
status: completed
contract_path: MyToken.sol
vulnerabilities_found: 3
detectors_run: ['reentrancy-eth', 'uninitialized-state', 'solc-version']
results:
  - detector: reentrancy-eth
    severity: high
    description: "Reentrancy vulnerability detected"
    line: 45
    function: withdraw
  - detector: uninitialized-state
    severity: medium
    description: "Uninitialized state variable"
    line: 12
    variable: owner
summary:
  high: 1
  medium: 1
  low: 1
  info: 0
```

---

### mythril - Mythril Symbolic Execution
**Category**: Smart Contract Audit  
**Status**: Production Ready ✅

Performs symbolic execution analysis of smart contracts using Mythril.

#### Parameters
- **contract_path** (required): Path to the contract file
- **timeout** (optional): Analysis timeout in seconds - default: 300
- **max_depth** (optional): Maximum symbolic execution depth - default: 12
- **strategy** (optional): Analysis strategy ('dfs', 'bfs') - default: 'dfs'
- **modules** (optional): Comma-separated list of analysis modules

#### Example Usage
```bash
# Basic analysis
sentinelx run mythril -p "{contract_path: 'MyToken.sol'}"

# With custom timeout and strategy
sentinelx run mythril -p "{
  contract_path: 'contracts/Token.sol',
  timeout: 600,
  max_depth: 15,
  strategy: 'bfs'
}"
```

#### Output Format
```yaml
status: completed
contract_path: MyToken.sol
analysis_time: 234.5
issues_found: 2
results:
  - swc_id: SWC-107
    title: Reentrancy
    severity: High
    description: "External call can be initiated by anyone"
    function: withdraw
    line: 45
    gas_used: 2300
  - swc_id: SWC-101
    title: Integer Overflow
    severity: Medium
    description: "Arithmetic operation can overflow"
    function: transfer
    line: 28
summary:
  high: 1
  medium: 1
  low: 0
  gas_analysis: true
```

---

### cvss - CVSS Vulnerability Scoring
**Category**: Smart Contract Audit  
**Status**: Production Ready ✅

Calculates CVSS v3.1 vulnerability scores and provides severity ratings.

#### Parameters
- **vector** (required): CVSS v3.1 vector string (e.g., "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
- **temporal_metrics** (optional): Include temporal metrics in calculation
- **environmental_metrics** (optional): Include environmental metrics

#### Example Usage
```bash
# Basic CVSS calculation
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}"

# With temporal metrics
sentinelx run cvss -p "{
  vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:F/RL:O/RC:C',
  temporal_metrics: true
}"
```

#### Output Format
```yaml
status: completed
vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
base_score: 9.8
temporal_score: 8.5
environmental_score: 9.8
severity: CRITICAL
metrics:
  attack_vector: NETWORK
  attack_complexity: LOW
  privileges_required: NONE
  user_interaction: NONE
  scope: UNCHANGED
  confidentiality: HIGH
  integrity: HIGH
  availability: HIGH
recommendations:
  - "Implement input validation"
  - "Add access controls"
  - "Enable logging and monitoring"
```

## Exploit Development

### shellcode - Shellcode Generation
**Category**: Exploit Development  
**Status**: Production Ready ✅

Generates shellcode for various architectures using pwntools.

#### Parameters
- **arch** (required): Target architecture ('amd64', 'i386', 'arm', 'aarch64', 'mips')
- **payload** (required): Payload type ('/bin/sh', 'reverse_shell', 'bind_shell', 'custom')
- **host** (optional): Target host for reverse shells
- **port** (optional): Target port for network payloads
- **encoder** (optional): Encoder to use ('none', 'xor', 'alpha')

#### Example Usage
```bash
# Basic shell spawn
sentinelx run shellcode -p "{arch: 'amd64', payload: '/bin/sh'}"

# Reverse shell
sentinelx run shellcode -p "{
  arch: 'amd64',
  payload: 'reverse_shell',
  host: '192.168.1.100',
  port: 4444
}"

# Encoded shellcode
sentinelx run shellcode -p "{
  arch: 'i386',
  payload: '/bin/sh',
  encoder: 'alpha'
}"
```

#### Output Format
```yaml
status: completed
arch: amd64
payload: /bin/sh
shellcode_length: 48
encoded: false
shellcode_hex: "4831ff4831f64889e34889e54889e24889e748c7c03b0000000f05"
shellcode_asm: |
  xor rdi, rdi
  xor rsi, rsi
  mov rbx, rsp
  mov rbp, rsp
  mov rdx, rsp
  mov rdi, rsp
  mov rax, 0x3b
  syscall
c_array: |
  char shellcode[] = {
    0x48, 0x31, 0xff, 0x48, 0x31, 0xf6, 0x48, 0x89,
    // ... rest of shellcode
  };
python_bytes: "b'\\x48\\x31\\xff\\x48\\x31\\xf6\\x48\\x89'"
```

---

### fuzzer - Security Fuzzing
**Category**: Exploit Development / Web Security  
**Status**: Production Ready ✅

Performs intelligent security fuzzing with various payload types.

#### Parameters
- **target** (required): Target URL or file path
- **method** (optional): HTTP method for web fuzzing - default: 'GET'
- **iterations** (optional): Number of fuzzing iterations - default: 100
- **payload_types** (optional): Types of payloads to use - default: ['overflow', 'injection', 'format']
- **timeout** (optional): Request timeout in seconds - default: 10

#### Example Usage
```bash
# Basic web fuzzing
sentinelx run fuzzer -p "{target: 'https://example.com/api/search'}"

# POST endpoint fuzzing
sentinelx run fuzzer -p "{
  target: 'https://example.com/api/login',
  method: 'POST',
  iterations: 500,
  payload_types: ['injection', 'overflow']
}"

# File fuzzing
sentinelx run fuzzer -p "{
  target: '/path/to/binary',
  iterations: 1000,
  payload_types: ['overflow', 'format']
}"
```

#### Output Format
```yaml
status: completed
target: https://example.com/api/search
iterations_completed: 100
crashes_detected: 3
anomalies_found: 7
payload_types_used: ['overflow', 'injection', 'format']
results:
  crashes:
    - iteration: 45
      payload_type: overflow
      payload_length: 1024
      response_code: 500
      crash_signature: "buffer_overflow_detected"
  anomalies:
    - iteration: 23
      payload_type: injection
      response_time: 5.2
      unusual_response: true
statistics:
  success_rate: 0.93
  average_response_time: 0.8
  error_rate: 0.07
```

---

### autopwn - Automatic Exploit Generation
**Category**: Exploit Development  
**Status**: Functional/Simulated ⚠️

Attempts automatic exploit generation for binaries (requires angr framework).

#### Parameters
- **binary_path** (required): Path to target binary
- **crash_input** (optional): Known crash input file
- **analysis_timeout** (optional): Analysis timeout in seconds - default: 600
- **exploration_technique** (optional): Exploration technique to use

#### Example Usage
```bash
# Basic exploit generation
sentinelx run autopwn -p "{binary_path: './vulnerable_binary'}"

# With crash input
sentinelx run autopwn -p "{
  binary_path: './target',
  crash_input: './crash.txt',
  analysis_timeout: 1200
}"
```

## Blockchain Security

### chain-monitor - Blockchain Monitoring
**Category**: Blockchain Security  
**Status**: Production Ready ✅

Monitors blockchain networks for suspicious activities and transactions.

#### Parameters
- **network** (required): Blockchain network ('ethereum', 'polygon', 'bsc', 'arbitrum')
- **addresses** (optional): List of addresses to monitor
- **duration** (optional): Monitoring duration in seconds - default: 300
- **events** (optional): Specific events to monitor
- **alerts** (optional): Alert conditions

#### Example Usage
```bash
# Monitor Ethereum network
sentinelx run chain-monitor -p "{
  network: 'ethereum',
  addresses: ['0x123...', '0x456...'],
  duration: 600
}"

# Monitor specific events
sentinelx run chain-monitor -p "{
  network: 'polygon',
  events: ['Transfer', 'Approval', 'Swap'],
  alerts: ['large_transfer', 'unusual_gas']
}"
```

#### Output Format
```yaml
status: completed
network: ethereum
monitoring_duration: 600
addresses_monitored: 2
events_detected: 45
alerts_triggered: 3
results:
  transactions:
    - hash: "0xabc..."
      from: "0x123..."
      to: "0x456..."
      value: 1000000000000000000
      gas_used: 21000
      timestamp: "2025-06-22T10:30:00Z"
  alerts:
    - type: large_transfer
      transaction: "0xabc..."
      amount: "1000 ETH"
      severity: high
summary:
  total_transactions: 45
  total_volume: "2500 ETH"
  unique_addresses: 12
  suspicious_activity: 3
```

---

### tx-replay - Transaction Replay Analysis
**Category**: Blockchain Security  
**Status**: Functional/Simulated ⚠️

Replays and analyzes blockchain transactions for security assessment.

#### Parameters
- **transaction_hash** (required): Transaction hash to replay
- **network** (required): Blockchain network
- **fork_block** (optional): Block number to fork from
- **gas_analysis** (optional): Perform gas optimization analysis

#### Example Usage
```bash
# Replay transaction
sentinelx run tx-replay -p "{
  transaction_hash: '0xabc123...',
  network: 'ethereum',
  gas_analysis: true
}"
```

---

### rwa-scan - Real World Asset Scanner
**Category**: Blockchain Security  
**Status**: Functional/Simulated ⚠️

Scans Real World Asset (RWA) protocols for security vulnerabilities.

#### Parameters
- **protocol** (required): RWA protocol to scan ('centrifuge', 'maple', 'goldfinch')
- **contracts** (optional): Specific contract addresses
- **analysis_depth** (optional): Analysis depth level

#### Example Usage
```bash
# Scan RWA protocol
sentinelx run rwa-scan -p "{
  protocol: 'centrifuge',
  analysis_depth: 'deep'
}"
```

## Red Team Operations

### c2 - Command & Control Server
**Category**: Red Team Operations  
**Status**: Functional/Simulated ⚠️

Sets up a command and control server for red team operations.

#### Parameters
- **port** (optional): Server port - default: 8080
- **bind_address** (optional): Bind address - default: '0.0.0.0'
- **encryption** (optional): Enable encryption - default: true
- **auth_key** (optional): Authentication key

#### Example Usage
```bash
# Basic C2 server
sentinelx run c2 -p "{port: 9999, encryption: true}"
```

---

### lateral-move - Lateral Movement
**Category**: Red Team Operations  
**Status**: Functional/Simulated ⚠️

Performs lateral movement techniques for network penetration.

#### Parameters
- **target_network** (required): Target network range
- **technique** (optional): Movement technique ('smb', 'rdp', 'ssh')
- **credentials** (optional): Authentication credentials

#### Example Usage
```bash
# SMB lateral movement
sentinelx run lateral-move -p "{
  target_network: '192.168.1.0/24',
  technique: 'smb'
}"
```

---

### social-eng - Social Engineering
**Category**: Red Team Operations  
**Status**: Functional/Simulated ⚠️

Generates and manages social engineering campaigns.

#### Parameters
- **campaign_type** (required): Campaign type ('phishing', 'pretext', 'spear_phishing')
- **targets** (optional): Target list
- **template** (optional): Email/message template

#### Example Usage
```bash
# Phishing campaign
sentinelx run social-eng -p "{
  campaign_type: 'phishing',
  template: 'it_support'
}"
```

## Digital Forensics

### memory-forensics - Memory Analysis
**Category**: Digital Forensics  
**Status**: Functional/Simulated ⚠️

Performs memory forensics analysis using Volatility framework.

#### Parameters
- **memory_dump** (required): Path to memory dump file
- **profile** (optional): Memory profile to use
- **plugins** (optional): Volatility plugins to run

#### Example Usage
```bash
# Basic memory analysis
sentinelx run memory-forensics -p "{
  memory_dump: './memory.dmp',
  profile: 'Win10x64_19041'
}"
```

---

### disk-forensics - Disk Analysis
**Category**: Digital Forensics  
**Status**: Functional/Simulated ⚠️

Performs disk forensics analysis using Sleuth Kit.

#### Parameters
- **disk_image** (required): Path to disk image
- **filesystem** (optional): Filesystem type
- **analysis_type** (optional): Type of analysis to perform

#### Example Usage
```bash
# Disk forensics
sentinelx run disk-forensics -p "{
  disk_image: './disk.dd',
  filesystem: 'ntfs'
}"
```

---

### chain-ir - Blockchain Incident Response
**Category**: Digital Forensics  
**Status**: Functional/Simulated ⚠️

Performs blockchain incident response and analysis.

#### Parameters
- **incident_hash** (required): Transaction hash related to incident
- **network** (required): Blockchain network
- **analysis_scope** (optional): Scope of analysis

#### Example Usage
```bash
# Blockchain IR
sentinelx run chain-ir -p "{
  incident_hash: '0xabc123...',
  network: 'ethereum'
}"
```

## AI Security

### llm-assist - AI Security Assistant
**Category**: AI Security  
**Status**: Production Ready ✅

Provides AI-powered security analysis and assistance using LLMs.

#### Parameters
- **task_type** (required): Type of assistance ('code_review', 'threat_model', 'vuln_analysis')
- **input_data** (required): Data to analyze
- **model** (optional): LLM model to use - default: 'gpt-3.5-turbo'
- **max_tokens** (optional): Maximum tokens for response

#### Example Usage
```bash
# Code review assistance
sentinelx run llm-assist -p "{
  task_type: 'code_review',
  input_data: 'function login(user, pass) { ... }'
}"

# Threat modeling
sentinelx run llm-assist -p "{
  task_type: 'threat_model',
  input_data: 'Web application with user authentication and payment processing'
}"
```

#### Output Format
```yaml
status: completed
task_type: code_review
model_used: gpt-3.5-turbo
analysis:
  vulnerabilities_identified: 3
  recommendations: 5
  confidence_score: 0.85
results:
  vulnerabilities:
    - type: sql_injection
      line: 15
      severity: high
      description: "SQL injection vulnerability in login function"
      recommendation: "Use parameterized queries"
  recommendations:
    - category: authentication
      priority: high
      description: "Implement password hashing"
    - category: validation
      priority: medium
      description: "Add input sanitization"
summary: "Code review completed with 3 vulnerabilities found"
```

---

### prompt-injection - Prompt Injection Testing
**Category**: AI Security  
**Status**: Functional/Simulated ⚠️

Tests LLM applications for prompt injection vulnerabilities.

#### Parameters
- **target_llm** (required): Target LLM endpoint or application
- **injection_types** (optional): Types of injections to test
- **payload_file** (optional): Custom payload file

#### Example Usage
```bash
# Test prompt injection
sentinelx run prompt-injection -p "{
  target_llm: 'https://api.example.com/chat',
  injection_types: ['direct', 'indirect', 'jailbreak']
}"
```

## Web Security

### web2-static - Web Application Static Analysis
**Category**: Web Security  
**Status**: Production Ready ✅

Performs static analysis of web applications for security vulnerabilities.

#### Parameters
- **target** (required): Target file or directory to analyze
- **language** (required): Programming language ('php', 'python', 'javascript', 'java')
- **rules** (optional): Custom rule file
- **output_format** (optional): Output format - default: 'json'

#### Example Usage
```bash
# PHP application analysis
sentinelx run web2-static -p "{
  target: 'webapp.php',
  language: 'php'
}"

# Python Flask application
sentinelx run web2-static -p "{
  target: './app/',
  language: 'python',
  rules: 'custom_rules.yaml'
}"

# JavaScript/Node.js analysis
sentinelx run web2-static -p "{
  target: 'server.js',
  language: 'javascript'
}"
```

#### Output Format
```yaml
status: completed
target: webapp.php
language: php
lines_analyzed: 1250
vulnerabilities_found: 8
results:
  - type: sql_injection
    severity: high
    line: 45
    function: getUserData
    description: "SQL injection vulnerability in user data retrieval"
    code_snippet: "$query = \"SELECT * FROM users WHERE id = \" . $_GET['id'];"
    recommendation: "Use prepared statements"
  - type: xss
    severity: medium
    line: 78
    function: displayMessage
    description: "Cross-site scripting vulnerability"
    code_snippet: "echo $_POST['message'];"
    recommendation: "Sanitize user input with htmlspecialchars()"
  - type: command_injection
    severity: critical
    line: 120
    function: processFile
    description: "Command injection vulnerability"
    code_snippet: "exec('convert ' . $_FILES['image']['name']);"
    recommendation: "Validate and escape file names"
summary:
  critical: 1
  high: 3
  medium: 3
  low: 1
  info: 0
  owasp_top_10:
    - A03_injection
    - A07_xss
categories:
  injection: 4
  xss: 2
  insecure_file_handling: 1
  information_disclosure: 1
```

## Task Usage Examples

### Workflow Integration Examples

#### Smart Contract Audit Workflow
```yaml
name: "smart_contract_audit"
description: "Complete smart contract security audit"
steps:
  - name: "slither_analysis"
    task: "slither"
    params:
      contract_path: "contracts/Token.sol"
      format: "json"
  
  - name: "mythril_analysis"
    task: "mythril"
    params:
      contract_path: "contracts/Token.sol"
      timeout: 300
    depends_on: ["slither_analysis"]
  
  - name: "vulnerability_scoring"
    task: "cvss"
    params:
      vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    depends_on: ["mythril_analysis"]
```

#### Web Application Security Assessment
```yaml
name: "web_security_assessment"
description: "Comprehensive web application security assessment"
steps:
  - name: "static_analysis"
    task: "web2-static"
    params:
      target: "webapp/"
      language: "php"
  
  - name: "fuzzing_test"
    task: "fuzzer"
    params:
      target: "https://webapp.example.com"
      iterations: 500
    depends_on: ["static_analysis"]
  
  - name: "ai_code_review"
    task: "llm-assist"
    params:
      task_type: "code_review"
      input_data: "{{static_analysis.vulnerable_code}}"
    depends_on: ["static_analysis"]
```

#### Blockchain Security Monitoring
```yaml
name: "blockchain_monitoring"
description: "Continuous blockchain security monitoring"
steps:
  - name: "chain_monitoring"
    task: "chain-monitor"
    params:
      network: "ethereum"
      duration: 3600
      addresses: ["0x123...", "0x456..."]
  
  - name: "transaction_analysis"
    task: "tx-replay"
    params:
      transaction_hash: "{{chain_monitoring.suspicious_tx}}"
      network: "ethereum"
    depends_on: ["chain_monitoring"]
```

### CLI Usage Patterns

#### Quick Vulnerability Assessment
```bash
# Run multiple tasks in sequence
sentinelx run slither -p "{contract_path: 'Token.sol'}" && \
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}" && \
sentinelx run web2-static -p "{target: 'webapp.php', language: 'php'}"
```

#### Automated Reporting
```bash
# Generate workflow and run with reporting
sentinelx workflow template audit.yaml --type audit
sentinelx workflow run audit.yaml -o results.json
sentinelx report generate results.json --format html
```

#### Performance Monitoring
```bash
# Profile task performance
sentinelx perf profile slither --iterations 5
sentinelx perf benchmark "slither,mythril,web2-static" --iterations 3
```

### Parameter Validation Examples

Each task validates its parameters according to its specification:

```bash
# This will fail - missing required parameter
sentinelx run slither -p "{format: 'json'}"
# Error: Missing required parameter: contract_path

# This will succeed - all required parameters provided
sentinelx run slither -p "{contract_path: 'Token.sol', format: 'json'}"

# Validation also checks parameter types and values
sentinelx run cvss -p "{vector: 'invalid_vector'}"
# Error: Invalid CVSS vector format
```

---

For more detailed usage examples and integration guides, see the [User Guide](USER_GUIDE.md) and [Developer Guide](DEVELOPER_GUIDE.md).
