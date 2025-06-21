# SentinelX

SentinelX is a modular Python framework for offensive and defensive security operations across Web2 and Web3.  It exposes a plugin-based task system so additional tooling can be integrated without modifying the core framework.

## Features

- **Unified runtime** – the `Task` abstraction enables asynchronous operations and provides hooks for setup and teardown.  Tasks are discovered through a `PluginRegistry` and instantiated with a `Context` loaded from YAML configuration.
- **Threat modeling** utilities for building simple STRIDE style models and rendering diagrams.
- **Auditing** modules for smart contracts and Web2 applications.
- **Exploit development** helpers including fuzzing and automatic exploit generation.
- **Red team** components such as a minimal C2 server and lateral movement helpers.
- **Blockchain monitoring** tasks for transaction replay or real world asset scanning.
- **Forensics** utilities for memory, disk and on‑chain incident response.
- **AI assistance** for prompt crafting or LLM based helpers.
- Command line interface built with [Typer](https://typer.tiangolo.com) to run any registered task.

## Directory structure

```
sentinelx/
├── core/            # runtime, plugin system and utilities
│   ├── context.py
│   ├── registry.py
│   ├── task.py
│   └── utils.py
├── threatmodel/     # threat modeling helpers
│   ├── model.py
│   └── diagrams.py
├── audit/           # static analysis modules
│   ├── smart_contract.py
│   ├── web2_static.py
│   └── cvss.py
├── exploit/         # fuzzing and exploit generation
│   ├── fuzzing.py
│   ├── exploit_gen.py
│   └── shellcode.py
├── redteam/         # C2 server and other red team tools
│   ├── c2.py
│   ├── lateral_move.py
│   └── social_eng.py
├── blockchain/      # chain watchers and transaction tools
│   ├── monitor.py
│   ├── replay.py
│   └── rwascan.py
├── forensic/        # memory and disk forensics
│   ├── memory.py
│   ├── disk.py
│   └── chain_ir.py
├── ai/              # LLM helpers and adversarial tools
│   ├── llm_assist.py
│   └── adversarial.py
└── cli.py           # entry point for running tasks
```

## Installation

Install dependencies and run the framework directly from the repository:

```bash
python -m pip install -r requirements.txt
```

## Configuration

Create a `config.yaml` (see `config.yaml.example`) to define network settings and secrets.  Values prefixed with `ENV:` are resolved from environment variables when `Context.load()` is called.

```yaml
network:
  http_proxy: http://127.0.0.1:8080
  retries: 3

blockchain:
  rpc_urls:
    - https://arb1.gemachdao.io
    - https://solana-mainnet.gemachdao.io

secrets:
  etherscan_api: ENV:ETHERSCAN_APIKEY
  openai: ENV:OPENAI_KEY
```

## CLI usage

The CLI loads the configuration, discovers plugins and runs the specified task.

```bash
python -m sentinelx.cli run <task-name> --params '<yaml_or_json>'
```

Example:

```bash
python -m sentinelx.cli run slither --params '{sol_file: MyToken.sol}'
```

The CLI prints the YAML result returned by the task.

## Writing plugins

Subclass `Task` to create new actions and register them with `PluginRegistry.register`.  Alternatively, expose an entry point named `sentinelx.tasks` in your project so the framework can discover your plugin automatically.

## Project Status

**Phase 2 Complete!** SentinelX is now a fully functional modular security framework with 16+ implemented tasks across all security domains.

### ✅ Implemented & Tested Tasks

#### Smart Contract Security
- **SlitherScan** - Static analysis using Slither (JSON output, vulnerability detection)
- **MythrilScan** - Symbolic execution analysis using Mythril
- **CVSSCalculator** - Complete CVSS v3.1 scoring and severity assessment

#### Web Application Security  
- **Web2Static** - Multi-language static code analysis (SQL injection, XSS, command injection detection)
- **Fuzzer** - Intelligent security fuzzing with multiple payload types

#### Exploit Development
- **ShellcodeGen** - Cross-architecture shellcode generation using pwntools
- **AutoPwn** - Automatic exploit generation (requires angr)

#### Blockchain Operations
- **ChainMonitor** - Real-time blockchain monitoring (Ethereum, Polygon, BSC, Arbitrum)
- **TxReplay** - Transaction replay and analysis
- **RwaScan** - Real-world asset scanning

#### Red Team Operations
- **C2Server** - Command and control infrastructure
- **LateralMove** - Lateral movement helpers
- **SocialEngineering** - Social engineering campaign tools

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

