# SentinelX - Advanced Security Framework

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-❤️-red.svg)](https://github.com/sentinelx)
[![Framework](https://img.shields.io/badge/Type-Security%20Framework-red.svg)](https://github.com/sentinelx)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](docs/CONTRIBUTING.md)

```
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     ██╗  ██╗
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     ╚██╗██╔╝
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║      ╚███╔╝ 
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║      ██╔██╗ 
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗██╔╝ ██╗
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝
                          🦁 CYBER SAMURAI FRAMEWORK 🦁
```

**SentinelX** is a production-ready Python framework for offensive and defensive security operations across Web2 and Web3 environments. It provides a comprehensive suite of security tools with a modern CLI interface, workflow orchestration, and extensible plugin architecture.

> 🎯 **Mission:** Guard digital infrastructure like a black ops cyber samurai. Hunt vulnerabilities. Neutralize threats. Optimize defenses. Operate with zero tolerance for sloppy security.
> 
> See [`SENTINELX_MASTER_PROMPT.md`](SENTINELX_MASTER_PROMPT.md) for the complete operational framework.

## 🎯 Features

### Core Capabilities
- **21 Security Tasks** across all major security domains (14 original + 7 advanced pwn tasks)
- **Advanced Pwn Toolkit** with buffer overflows, ROP chains, heap exploitation, and shellcode generation
- **Workflow Orchestration** with dependency management and error handling
- **Professional CLI Interface** with rich formatting and interactive modes
- **Plugin Architecture** for easy extension and customization
- **Advanced Reporting** with multiple output formats
- **Performance Profiling** and benchmarking tools
- **Docker Integration** for sandboxed execution
- **Configuration Management** with validation and templates

### Security Domains
- 🔒 **Smart Contract Auditing** (Slither, Mythril, CVSS)
- 💥 **Advanced Binary Exploitation** (Buffer overflows, ROP chains, Heap exploitation, Shellcode generation)
- 🎯 **Comprehensive Pwn Toolkit** (Automated exploitation, Multi-technique analysis, CTF-ready)
- ⛓️ **Blockchain Security** (Chain monitoring, Transaction analysis)
- 🎭 **Red Team Operations** (C2, Advanced lateral movement with pwncat-cs, Comprehensive social engineering campaigns)
- 🔍 **Digital Forensics** (Memory, Disk, Blockchain IR)
- 🤖 **AI Security** (LLM assistance, Prompt injection testing)
- 🌐 **Web Security** (Static analysis, Vulnerability scanning)

## � Project Structure

```
sentinelx/
├── sentinelx/              # Core framework code
│   ├── core/              # Framework core (tasks, registry, context)
│   ├── audit/             # Smart contract auditing tasks
│   ├── exploit/           # Exploit development tools
│   ├── blockchain/        # Blockchain security tools
│   ├── redteam/           # Red team operation tools
│   ├── forensic/          # Digital forensics tools
│   ├── ai/                # AI-powered security tools
│   └── cli.py             # Command-line interface
├── docs/                  # Comprehensive documentation
│   ├── USER_GUIDE.md      # User guide and tutorials
│   ├── DEVELOPER_GUIDE.md # Developer and extension guide
│   ├── API_REFERENCE.md   # Complete API documentation
│   └── TASK_REFERENCE.md  # Task reference guide
├── examples/              # Examples and tutorials
│   ├── workflows/         # Workflow templates
│   └── custom_tasks/      # Custom task examples
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── dev/                   # Development files and reports
├── logs/                  # Application logs
├── config.yaml.example    # Configuration template
└── requirements.txt       # Dependencies
```

## �🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/sentinelx.git
cd sentinelx

# Install in development mode
pip install -e .

# Verify installation
python -c "import sentinelx; print('✅ SentinelX installed successfully')"
```

### Basic Usage

```bash
# List all available tasks
sentinelx list

# Get information about a specific task
sentinelx info slither

# Run a task
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}"

# Interactive mode
sentinelx interactive

# Search for tasks
sentinelx search "smart contract"
```

### Workflow Example

```bash
# Generate a workflow template
sentinelx workflow template audit_workflow.yaml --type audit

# Run the workflow
sentinelx workflow run audit_workflow.yaml

# List available workflows
sentinelx workflow list
```

## 🏗️ Architecture

SentinelX follows a modular architecture with clear separation of concerns:

```
sentinelx/
├── core/           # Core framework components
│   ├── registry.py # Plugin registration system
│   ├── task.py     # Base task class and interfaces
│   ├── context.py  # Execution context and configuration
│   ├── workflow.py # Workflow orchestration engine
│   └── utils.py    # Utility functions
├── audit/          # Smart contract auditing tasks
├── exploit/        # Exploit development tools
├── blockchain/     # Blockchain security tools
├── redteam/        # Red team operation tools
├── forensic/       # Digital forensics tools
├── ai/             # AI-powered security tools
├── cli.py          # Command-line interface
└── __init__.py     # Package initialization
```

## 🎮 Available Commands

### Core Commands
- `list` - List all registered tasks with categorization
- `info <task>` - Detailed information about a specific task
- `run <task>` - Execute a security task
- `search <query>` - Search tasks by name or description
- `validate` - Validate tasks and configuration
- `interactive` - Interactive task execution mode
- `config` - Configuration management utilities
- `version` - Show version information

### Workflow Commands
- `workflow run <file>` - Execute workflow from file
- `workflow template <file>` - Generate workflow templates
- `workflow list` - List available workflows and tasks

### Advanced Commands (Phase 4)
- `docker setup` - Setup Docker environment
- `docker run <task>` - Run tasks in containers
- `perf profile <task>` - Performance profiling
- `perf benchmark <tasks>` - Benchmark multiple tasks
- `report generate <file>` - Generate professional reports

## 🔧 Configuration

Create a configuration file to customize SentinelX:

```bash
# Initialize configuration interactively
sentinelx config init

# Show current configuration
sentinelx config show

# Validate configuration
sentinelx config validate
```

Example configuration:

```yaml
version: "1.0"
debug: false
log_level: "INFO"
output_dir: "./outputs"
temp_dir: "./temp"

blockchain:
  ethereum_rpc: "https://mainnet.infura.io/v3/YOUR_KEY"
  polygon_rpc: "https://polygon-rpc.com"
  timeout: 30

openai:
  api_key: "your-openai-key"
  model: "gpt-3.5-turbo"
  max_tokens: 1000
```

## 🛡️ Security Tasks

### Smart Contract Auditing
```bash
# Slither analysis
sentinelx run slither -p "{contract_path: 'contract.sol', format: 'json'}"

# Mythril analysis
sentinelx run mythril -p "{contract_path: 'contract.sol', timeout: 300}"

# CVSS scoring
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}"
```

### Exploit Development
```bash
# Comprehensive pwn analysis
sentinelx run pwn-toolkit -p "{binary: './challenge'}"

# Buffer overflow exploitation
sentinelx run binary-pwn -p "{binary: './target', type: 'buffer_overflow'}"

# ROP chain generation
sentinelx run rop-exploit -p "{binary: './target', type: 'execve', target: '/bin/sh'}"

# Heap exploitation
sentinelx run heap-exploit -p "{binary: './heap_challenge', technique: 'fastbin_dup'}"

# Generate shellcode
sentinelx run shellcode -p "{arch: 'amd64', payload: '/bin/sh'}"

# Fuzzing
sentinelx run fuzzer -p "{target: 'http://example.com', iterations: 1000}"
```

### Web Security
```bash
# Static code analysis
sentinelx run web2-static -p "{target: 'app.php', language: 'php'}"
```

### Blockchain Security
```bash
# Monitor blockchain
sentinelx run chain-monitor -p "{network: 'ethereum', addresses: ['0x123...']}"
```

## 🔄 Workflows

Workflows allow you to chain multiple security tasks together:

```yaml
name: "comprehensive_audit"
description: "Complete security audit workflow"
continue_on_error: true

steps:
  - name: "contract_analysis"
    task: "slither"
    params:
      contract_path: "contract.sol"
  
  - name: "deep_analysis"
    task: "mythril"
    params:
      contract_path: "contract.sol"
      timeout: 300
    depends_on: ["contract_analysis"]
  
  - name: "vulnerability_scoring"
    task: "cvss"
    params:
      vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    depends_on: ["deep_analysis"]
```

## 🧪 Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sentinelx

# Run specific test file
pytest tests/test_core.py
```

### Creating New Tasks

1. Create your task class:
```python
from sentinelx.core.task import Task, register_task

@register_task("my-task")
class MyTask(Task):
    """Custom security task."""
    
    REQUIRED_PARAMS = ["target"]
    OPTIONAL_PARAMS = ["timeout"]
    
    async def execute(self, context, **kwargs):
        # Your task implementation
        return {"status": "completed", "data": result}
```

2. Register and test:
```bash
# Verify registration
sentinelx list | grep my-task

# Test your task
sentinelx run my-task -p "{target: 'test'}"
```

## 📚 Documentation

For detailed documentation, see the [docs/](docs/) directory:

### User Documentation
- [**User Guide**](docs/USER_GUIDE.md) - Complete user documentation and tutorials
- [**FAQ**](docs/FAQ.md) - Frequently asked questions and troubleshooting
- [**Task Reference**](docs/TASK_REFERENCE.md) - Complete task documentation and examples

### Specialized Security Toolkits
- [**PWN Toolkit**](docs/PWN_TOOLKIT.md) - Comprehensive binary exploitation documentation
- [**Social Engineering Toolkit**](docs/SOCIAL_ENGINEERING_TOOLKIT.md) - Complete social engineering framework documentation
- [**Lateral Movement Toolkit**](docs/LATERAL_MOVEMENT_TOOLKIT.md) - Advanced lateral movement with pwncat-cs integration

### Developer Documentation  
- [**Developer Guide**](docs/DEVELOPER_GUIDE.md) - Development and plugin creation guide
- [**API Reference**](docs/API_REFERENCE.md) - Complete Python API documentation
- [**Advanced Features**](docs/ADVANCED_FEATURES.md) - Docker, performance, and reporting features
- [**Contributing Guide**](docs/CONTRIBUTING.md) - How to contribute to SentinelX

### Examples and Tutorials
- [**Examples Directory**](examples/) - Practical usage examples and tutorials
- [**Workflow Examples**](examples/workflows/) - Pre-built security assessment workflows
- [**Custom Task Examples**](examples/custom_task_example.py) - Complete task development examples

## 🎉 Current Status

**All Core Phases Complete!** SentinelX is now a production-ready security framework with:

### ✅ Implemented Features
- **18+ Security Tasks** across all major domains
- **Complete Workflow Orchestration** with dependency resolution
- **Professional CLI Interface** with rich formatting and interactive modes
- **Plugin Architecture** for easy extension
- **Advanced Reporting** and performance profiling
- **Docker Integration** for sandboxed execution
- **Configuration Management** with validation

### Security Task Categories
- 🔒 **Smart Contract Audit**: Slither, Mythril, CVSS
- 💥 **Exploit Development**: Shellcode, Fuzzing, AutoPwn
- ⛓️ **Blockchain Security**: Chain monitoring, Transaction analysis
- 🎭 **Red Team Operations**: C2, Advanced lateral movement with pwncat-cs, Comprehensive social engineering campaigns
- 🔍 **Digital Forensics**: Memory, Disk, Blockchain IR
- 🤖 **AI Security**: LLM assistance, Prompt injection testing
- 🌐 **Web Security**: Static analysis, Vulnerability scanning

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/sentinelx.git
cd sentinelx

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/sentinelx/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/sentinelx/discussions)

## 🎉 Acknowledgments

- Built with modern Python async/await patterns
- Uses [Typer](https://typer.tiangolo.com/) for CLI interface
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Powered by industry-standard security tools

---

**SentinelX** - Empowering security professionals with comprehensive, extensible, and professional security frameworks.

#### Digital Forensics
- **MemoryForensics** - Memory dump analysis
- **DiskForensics** - Disk image investigation  
- **ChainIR** - Blockchain incident response

#### AI-Powered Security
- **LLMAssist** - AI security analysis, code review, and threat modeling

### 🚀 Ready for Production Use

All tasks include:
- ✅ Comprehensive parameter validation
- ✅ Professional error handling  
- ✅ CLI integration with YAML/JSON output
- ✅ Real-world testing and validation
- ✅ Detailed logging and status reporting

### Example Usage

```bash
# Smart contract security analysis
sentinelx run slither -p "{contract_path: MyToken.sol}"
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}"

# Web application security
sentinelx run web2-static -p "{target: app.php, min_severity: medium}"
sentinelx run fuzzer -p "{target: 'http://example.com/login', type: sql, iterations: 50}"

# Blockchain monitoring
sentinelx run chain-monitor -p "{network: ethereum, type: network_status}"
sentinelx run chain-monitor -p "{network: ethereum, type: gas_tracker}"

# AI security analysis
sentinelx run llm-assist -p "{prompt: 'What is the OWASP Top 10?', type: security_question}"
sentinelx run llm-assist -p "{analyze_code: 'SELECT * FROM users WHERE id = ' + input, type: code_review}"

# Exploit development
sentinelx run shellcode -p "{type: sh, arch: x86_64, format: hex}"
```

SentinelX provides a unified interface to orchestrate specialized security tooling from a single command line interface, making it ideal for security professionals, penetration testers, and development teams.

## Requirements

Dependencies are listed in `requirements.txt`:

- typer
- rich
- pydantic
- slither-analyzer
- mythril
- angr
- pwntools
- scapy
- fastapi
- uvicorn[standard]
- graphviz
- PyYAML

