# SentinelX User Guide

Welcome to the SentinelX User Guide! This comprehensive guide will help you get started with SentinelX and master its powerful security capabilities.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Command Reference](#command-reference)
4. [Configuration](#configuration)
5. [Working with Tasks](#working-with-tasks)
6. [Workflow Orchestration](#workflow-orchestration)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/your-org/sentinelx.git
cd sentinelx

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Verify installation
sentinelx version
```

### Dependencies

SentinelX automatically manages its dependencies. Core dependencies include:

- **typer** - CLI framework
- **rich** - Terminal formatting and progress bars
- **pyyaml** - Configuration and data serialization
- **asyncio** - Asynchronous execution

Optional dependencies are installed as needed for specific tasks:

- **slither-analyzer** - Smart contract analysis
- **mythril** - Symbolic execution
- **pwntools** - Exploit development
- **web3** - Blockchain interaction
- **openai** - AI-powered features

## Quick Start

### Your First Command

```bash
# List all available tasks
sentinelx list

# Get information about a specific task
sentinelx info cvss

# Run a simple CVSS calculation
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}"
```

### Interactive Mode

For beginners, interactive mode provides guided task execution:

```bash
sentinelx interactive
```

This will:
1. Show categorized task lists
2. Guide you through parameter selection
3. Execute the task with real-time feedback
4. Offer to save results

### Search and Discovery

Find tasks by name or description:

```bash
# Search for smart contract related tasks
sentinelx search "smart contract"

# Search for web security tasks
sentinelx search "web"

# Search by specific functionality
sentinelx search "fuzzing"
```

## Command Reference

### Core Commands

#### `list` - List Tasks
```bash
# List all tasks
sentinelx list

# Filter by category
sentinelx list --category audit

# Show detailed information
sentinelx list --detailed
```

Categories: `audit`, `exploit`, `blockchain`, `redteam`, `forensic`, `ai`, `web`

#### `info` - Task Information
```bash
# Basic information
sentinelx info slither

# Include usage examples
sentinelx info slither --examples
```

#### `run` - Execute Task
```bash
# Basic execution
sentinelx run <task_name>

# With parameters
sentinelx run <task_name> -p "{param1: 'value1', param2: 'value2'}"

# With custom configuration
sentinelx run <task_name> -c custom_config.yaml

# Verbose output
sentinelx run <task_name> -v

# Different output format
sentinelx run <task_name> -f json
```

Output formats: `yaml` (default), `json`, `table`

#### `search` - Find Tasks
```bash
# Basic search
sentinelx search "vulnerability"

# Case-sensitive search
sentinelx search "CVSS" --case-sensitive
```

#### `validate` - Validation
```bash
# Validate all tasks
sentinelx validate

# Validate specific task
sentinelx validate slither

# Validate configuration
sentinelx validate --config config.yaml

# Check dependencies
sentinelx validate --check-deps
```

#### `interactive` - Interactive Mode
```bash
# Start interactive session
sentinelx interactive

# Interactive with specific task
sentinelx interactive slither
```

#### `config` - Configuration Management
```bash
# Initialize configuration
sentinelx config init

# Show current configuration
sentinelx config show

# Edit configuration
sentinelx config edit

# Validate configuration
sentinelx config validate
```

### Workflow Commands

#### `workflow run` - Execute Workflow
```bash
# Run workflow from file
sentinelx workflow run audit_workflow.yaml

# With custom configuration
sentinelx workflow run audit_workflow.yaml -c config.yaml

# Save results to file
sentinelx workflow run audit_workflow.yaml -o results.json

# Different output format
sentinelx workflow run audit_workflow.yaml -f yaml
```

#### `workflow template` - Generate Templates
```bash
# Basic template
sentinelx workflow template basic_workflow.yaml --type basic

# Audit template
sentinelx workflow template smart_contract_audit.yaml --type audit

# Comprehensive assessment
sentinelx workflow template full_assessment.yaml --type assessment
```

#### `workflow list` - List Available Resources
```bash
# Show templates and available tasks
sentinelx workflow list
```

### Advanced Commands (Phase 4)

#### Docker Commands
```bash
# Setup Docker environment
sentinelx docker setup

# Run task in container
sentinelx docker run <task_name> -p "{params}"

# Sandbox mode for dangerous tasks
sentinelx docker run <task_name> --sandbox

# Cleanup Docker resources
sentinelx docker cleanup
```

#### Performance Commands
```bash
# Profile task performance
sentinelx perf profile <task_name> --iterations 10

# Benchmark multiple tasks
sentinelx perf benchmark "slither,mythril,cvss" --iterations 5

# Save results
sentinelx perf profile <task_name> -o profile_results.yaml
```

#### Reporting Commands
```bash
# Generate report from workflow results
sentinelx report generate results.json --format html

# Use custom template
sentinelx report generate results.json --template custom.html

# Different formats
sentinelx report generate results.json --format pdf
```

## Configuration

### Configuration File Structure

SentinelX uses YAML configuration files. Here's a complete example:

```yaml
# config.yaml
version: "1.0"
debug: false
log_level: "INFO"
output_dir: "./outputs"
temp_dir: "./temp"

# Blockchain configuration
blockchain:
  ethereum_rpc: "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
  polygon_rpc: "https://polygon-rpc.com"
  arbitrum_rpc: "https://arb1.arbitrum.io/rpc"
  timeout: 30
  retries: 3

# OpenAI configuration
openai:
  api_key: "your-openai-api-key"
  model: "gpt-3.5-turbo"
  max_tokens: 1000
  temperature: 0.7

# Network configuration
network:
  http_proxy: null
  https_proxy: null
  timeout: 30
  retries: 3

# Output configuration
output:
  format: "yaml"
  save_results: true
  timestamp_files: true

# Security configuration
security:
  sandbox_mode: false
  allow_dangerous_tasks: false
  max_execution_time: 300
```

### Environment Variables

Sensitive values can be loaded from environment variables:

```yaml
openai:
  api_key: "ENV:OPENAI_API_KEY"

blockchain:
  ethereum_rpc: "ENV:ETHEREUM_RPC_URL"
```

Set environment variables:
```bash
export OPENAI_API_KEY="your-key-here"
export ETHEREUM_RPC_URL="https://mainnet.infura.io/v3/your-project-id"
```

### Configuration Management

```bash
# Create initial configuration interactively
sentinelx config init

# View current configuration
sentinelx config show

# Edit configuration (uses $EDITOR)
sentinelx config edit

# Validate configuration
sentinelx config validate
```

## Working with Tasks

### Task Categories

SentinelX organizes tasks into logical categories:

#### Smart Contract Auditing
- **slither** - Static analysis using Slither
- **mythril** - Symbolic execution analysis
- **cvss** - CVSS vulnerability scoring

#### Exploit Development
- **shellcode** - Shellcode generation
- **fuzzer** - Security fuzzing
- **autopwn** - Automatic exploit generation

#### Blockchain Security
- **chain-monitor** - Blockchain monitoring
- **tx-replay** - Transaction replay analysis
- **rwa-scan** - Real-world asset scanning

#### Red Team Operations
- **c2** - Command and control server
- **lateral-move** - Lateral movement techniques
- **social-eng** - Social engineering campaigns

#### Digital Forensics
- **memory-forensics** - Memory analysis
- **disk-forensics** - Disk forensics
- **chain-ir** - Blockchain incident response

#### AI Security
- **llm-assist** - AI-powered security assistance
- **prompt-injection** - Prompt injection testing

#### Web Security
- **web2-static** - Static code analysis

### Task Parameters

Tasks accept parameters in YAML or JSON format:

```bash
# YAML parameters (recommended)
sentinelx run slither -p "{contract_path: 'MyToken.sol', format: 'json'}"

# JSON parameters
sentinelx run slither -p '{"contract_path": "MyToken.sol", "format": "json"}'

# Complex parameters
sentinelx run chain-monitor -p "
{
  network: 'ethereum',
  addresses: ['0x123...', '0x456...'],
  events: ['Transfer', 'Approval'],
  timeout: 300
}
"
```

### Task Examples

#### Smart Contract Analysis

```bash
# Slither analysis
sentinelx run slither -p "{contract_path: 'contracts/MyToken.sol'}"

# Mythril with timeout
sentinelx run mythril -p "{contract_path: 'contracts/MyToken.sol', timeout: 300}"

# CVSS scoring
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}"
```

#### Web Security Testing

```bash
# Static analysis of PHP code
sentinelx run web2-static -p "{target: 'app.php', language: 'php'}"

# Fuzzing web application
sentinelx run fuzzer -p "{target: 'https://example.com/api', method: 'POST'}"
```

#### Blockchain Operations

```bash
# Monitor Ethereum addresses
sentinelx run chain-monitor -p "
{
  network: 'ethereum',
  addresses: ['0x1234...'],
  duration: 600
}
"

# Scan DeFi protocol
sentinelx run rwa-scan -p "{protocol: 'uniswap', version: 'v3'}"
```

#### Exploit Development

```bash
# Generate x64 shellcode
sentinelx run shellcode -p "{arch: 'amd64', payload: '/bin/sh'}"

# Generate ARM shellcode
sentinelx run shellcode -p "{arch: 'arm', payload: 'reverse_shell', host: '192.168.1.100', port: 4444}"
```

### Output Formats

SentinelX supports multiple output formats:

#### YAML (Default)
```bash
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}" -f yaml
```

#### JSON
```bash
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}" -f json
```

#### Table (for structured data)
```bash
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}" -f table
```

## Workflow Orchestration

Workflows allow you to chain multiple security tasks together with dependency management and error handling.

### Creating Workflows

#### Basic Workflow Structure

```yaml
name: "basic_security_assessment"
description: "Basic security assessment workflow"
continue_on_error: true

steps:
  - name: "static_analysis"
    task: "web2-static"
    params:
      target: "vulnerable_app.php"
      language: "php"
  
  - name: "vulnerability_scoring"
    task: "cvss"
    params:
      vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    depends_on: ["static_analysis"]
```

#### Smart Contract Audit Workflow

```yaml
name: "smart_contract_audit"
description: "Comprehensive smart contract security audit"
continue_on_error: true

steps:
  - name: "slither_analysis"
    task: "slither"
    params:
      contract_path: "contracts/MyToken.sol"
      format: "json"
  
  - name: "mythril_analysis"
    task: "mythril"
    params:
      contract_path: "contracts/MyToken.sol"
      timeout: 300
    depends_on: ["slither_analysis"]
  
  - name: "vulnerability_assessment"
    task: "cvss"
    params:
      vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    depends_on: ["mythril_analysis"]
```

#### Comprehensive Security Assessment

```yaml
name: "comprehensive_assessment"
description: "Multi-domain security assessment"
continue_on_error: true

steps:
  - name: "contract_analysis"
    task: "slither"
    params:
      contract_path: "contracts/Token.sol"
  
  - name: "web_analysis"
    task: "web2-static"
    params:
      target: "backend/api.php"
      language: "php"
  
  - name: "blockchain_monitoring"
    task: "chain-monitor"
    params:
      network: "ethereum"
      addresses: ["0x123..."]
      duration: 300
    depends_on: ["contract_analysis"]
  
  - name: "exploit_generation"
    task: "shellcode"
    params:
      arch: "amd64"
      payload: "/bin/sh"
    depends_on: ["web_analysis", "contract_analysis"]
```

### Workflow Features

#### Dependency Management
```yaml
steps:
  - name: "step1"
    task: "task1"
    
  - name: "step2"
    task: "task2"
    depends_on: ["step1"]  # Runs after step1
    
  - name: "step3"
    task: "task3"
    depends_on: ["step1", "step2"]  # Runs after both step1 and step2
```

#### Error Handling
```yaml
# Continue workflow even if tasks fail
continue_on_error: true

# Or handle errors per step
steps:
  - name: "optional_step"
    task: "risky_task"
    continue_on_error: true
```

#### Parameter Passing
```yaml
steps:
  - name: "analysis"
    task: "slither"
    params:
      contract_path: "contract.sol"
    output_mapping:
      vulnerabilities: "vuln_count"
  
  - name: "scoring"
    task: "cvss"
    params:
      # Use output from previous step
      vector: "{{analysis.cvss_vector}}"
    depends_on: ["analysis"]
```

### Running Workflows

```bash
# Generate template
sentinelx workflow template my_workflow.yaml --type audit

# Execute workflow
sentinelx workflow run my_workflow.yaml

# With custom configuration
sentinelx workflow run my_workflow.yaml -c config.yaml

# Save results
sentinelx workflow run my_workflow.yaml -o results.json -f json

# Verbose execution
sentinelx workflow run my_workflow.yaml -v
```

### Workflow Templates

SentinelX provides pre-built templates:

- **basic** - Simple security assessment
- **audit** - Smart contract audit workflow
- **assessment** - Comprehensive security assessment

```bash
# Generate templates
sentinelx workflow template basic.yaml --type basic
sentinelx workflow template audit.yaml --type audit
sentinelx workflow template assessment.yaml --type assessment
```

## Advanced Features

### Interactive Mode

Interactive mode provides a guided experience:

```bash
sentinelx interactive
```

Features:
- Categorized task selection
- Guided parameter input
- Real-time feedback
- Result saving options

### Performance Profiling

Monitor task performance:

```bash
# Profile single task
sentinelx perf profile slither --iterations 5

# Benchmark multiple tasks
sentinelx perf benchmark "slither,mythril,cvss" --iterations 3

# Save profiling results
sentinelx perf profile slither -o profile_results.yaml
```

### Docker Integration

Run tasks in isolated containers:

```bash
# Setup Docker environment
sentinelx docker setup

# Run task in container
sentinelx docker run slither -p "{contract_path: 'contract.sol'}"

# Sandbox mode for dangerous tasks
sentinelx docker run autopwn --sandbox

# Cleanup
sentinelx docker cleanup
```

### Advanced Reporting

Generate professional reports:

```bash
# HTML report
sentinelx report generate workflow_results.json --format html

# PDF report
sentinelx report generate workflow_results.json --format pdf

# Custom template
sentinelx report generate workflow_results.json --template custom.html
```

### Configuration Validation

Ensure your setup is correct:

```bash
# Validate all tasks
sentinelx validate

# Validate specific task
sentinelx validate slither

# Check dependencies
sentinelx validate --check-deps

# Verbose validation
sentinelx validate -v
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Problem: Module not found
# Solution: Ensure proper installation
pip install -e .

# Verify installation
python -c "import sentinelx; print('OK')"
```

#### Configuration Issues
```bash
# Problem: Configuration file not found
# Solution: Create configuration
sentinelx config init

# Validate configuration
sentinelx config validate
```

#### Task Execution Failures
```bash
# Problem: Task fails to execute
# Solution: Use verbose mode for debugging
sentinelx run <task> -v

# Check task requirements
sentinelx info <task>

# Validate task
sentinelx validate <task>
```

#### Network/API Issues
```bash
# Problem: API timeouts or network issues
# Solution: Check configuration
sentinelx config show

# Test connectivity
sentinelx validate --check-deps
```

### Debug Mode

Enable debug logging:

```bash
# Verbose output
sentinelx run <task> -v

# Debug configuration
sentinelx config init  # Set debug: true

# Check logs
tail -f ~/.sentinelx/logs/sentinelx.log
```

### Getting Help

```bash
# General help
sentinelx --help

# Command-specific help
sentinelx run --help
sentinelx workflow --help

# Task information
sentinelx info <task_name>

# List all tasks
sentinelx list --detailed
```

### Performance Issues

```bash
# Profile task performance
sentinelx perf profile <task> --iterations 1

# Check system resources
sentinelx validate --check-deps

# Use Docker for isolation
sentinelx docker run <task>
```

### Reporting Issues

When reporting issues, please include:

1. SentinelX version: `sentinelx version`
2. Python version: `python --version`
3. Operating system
4. Full error message with `-v` flag
5. Configuration file (without sensitive data)
6. Steps to reproduce

---

This completes the User Guide. For developer information, see the [Developer Guide](DEVELOPER_GUIDE.md).
