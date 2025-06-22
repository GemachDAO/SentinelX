# SentinelX Frequently Asked Questions (FAQ)

Common questions and answers about using and extending SentinelX.

## Table of Contents

1. [General Questions](#general-questions)
2. [Installation & Setup](#installation--setup)
3. [Usage & CLI](#usage--cli)
4. [Task Development](#task-development)
5. [Workflows](#workflows)
6. [Docker & Deployment](#docker--deployment)
7. [Performance & Optimization](#performance--optimization)
8. [Troubleshooting](#troubleshooting)
9. [Security & Best Practices](#security--best-practices)
10. [Contributing](#contributing)

## General Questions

### What is SentinelX?

SentinelX is a comprehensive Python security framework that unifies various security tools and methodologies into a single, extensible platform. It provides a CLI interface, workflow orchestration, and plugin architecture for security professionals, developers, and security teams.

### What types of security analysis does SentinelX support?

SentinelX supports multiple security domains:
- **Smart Contract Security**: Slither, Mythril, CVSS scoring
- **Web Application Security**: Static analysis, fuzzing, vulnerability scanning
- **Blockchain Security**: Transaction analysis, chain monitoring
- **Digital Forensics**: Memory analysis, disk forensics, incident response
- **Red Team Operations**: C2, lateral movement, social engineering
- **AI Security**: LLM assistance, adversarial testing

### How is SentinelX different from other security tools?

SentinelX differs in several ways:
- **Unified Interface**: Single CLI for multiple security tools
- **Workflow Orchestration**: Complex multi-step security processes
- **Extensible Architecture**: Easy to add custom security tasks
- **Modern Python Framework**: Built with async/await, type hints
- **Professional Reporting**: Advanced visualization and documentation

### Is SentinelX free to use?

Yes, SentinelX is open source and free to use under the MIT license. You can use it for commercial and non-commercial purposes.

## Installation & Setup

### What are the system requirements?

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, Windows
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 2GB free space for dependencies

### How do I install SentinelX?

```bash
# Clone the repository
git clone https://github.com/your-org/sentinelx.git
cd sentinelx

# Install in development mode
pip install -e .

# Verify installation
sentinelx --help
```

### I'm getting permission errors during installation. What should I do?

Use a virtual environment to avoid permission issues:

```bash
# Create virtual environment
python -m venv sentinelx-env
source sentinelx-env/bin/activate  # On Windows: sentinelx-env\Scripts\activate

# Install SentinelX
pip install -e .
```

### How do I install optional dependencies for specific tasks?

```bash
# Install smart contract analysis tools
pip install slither-analyzer mythril

# Install web security tools
pip install pwntools scapy

# Install all optional dependencies
pip install -e ".[all]"
```

### Can I install SentinelX using pip?

Currently, SentinelX is installed from source. We plan to publish to PyPI in future releases:

```bash
# Future PyPI installation (not yet available)
pip install sentinelx
```

## Usage & CLI

### How do I list all available security tasks?

```bash
# List all tasks
sentinelx list

# List tasks by category
sentinelx list --category smart-contract

# Search for specific tasks
sentinelx search "contract"
```

### How do I get information about a specific task?

```bash
# Get detailed task information
sentinelx info slither

# Show parameter requirements
sentinelx info slither --show-params

# Show usage examples
sentinelx info slither --examples
```

### How do I run a security task?

```bash
# Basic task execution
sentinelx run cvss -p "{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}"

# Task with multiple parameters
sentinelx run slither -p "{contract_path: 'MyToken.sol', format: 'json'}"

# Using configuration file
sentinelx run slither -c my_config.yaml -p "{contract_path: 'contract.sol'}"
```

### What output formats are supported?

SentinelX supports multiple output formats:
- **YAML**: Default human-readable format
- **JSON**: Machine-readable structured data
- **Table**: Formatted console table
- **CSV**: Comma-separated values for spreadsheets

```bash
# Specify output format
sentinelx run cvss -p "{vector: '...'}" --format json
sentinelx run slither -p "{contract_path: 'token.sol'}" --format table
```

### How do I save task results to a file?

```bash
# Redirect output to file
sentinelx run slither -p "{contract_path: 'token.sol'}" > results.yaml

# Use JSON format for structured data
sentinelx run slither -p "{contract_path: 'token.sol'}" --format json > results.json
```

### Can I run multiple tasks in parallel?

Yes, use workflows for parallel execution:

```yaml
# workflow.yaml
workflow:
  name: "Parallel Analysis"
  steps:
    - name: "slither"
      task: "slither"
      parameters: {contract_path: "token.sol"}
    - name: "mythril"  
      task: "mythril"
      parameters: {contract_path: "token.sol"}
      parallel_with: ["slither"]
```

```bash
sentinelx workflow run workflow.yaml
```

## Task Development

### How do I create a custom security task?

1. **Create task class**:

```python
from sentinelx.core.task import Task, register_task

@register_task("my-custom-task")
class MyCustomTask(Task):
    REQUIRED_PARAMS = ["target"]
    OPTIONAL_PARAMS = ["timeout"]
    
    async def execute(self, context, **kwargs):
        target = kwargs["target"]
        # Your security analysis logic here
        return {"status": "completed", "target": target, "results": {}}
```

2. **Register the task**:
The `@register_task` decorator automatically registers your task.

3. **Test the task**:
```bash
sentinelx run my-custom-task -p "{target: 'test-target'}"
```

### What should my task return?

Tasks should return a standardized dictionary:

```python
{
    "status": "completed",  # completed, failed, timeout
    "task": "my-task",
    "duration": 12.34,
    "timestamp": "2024-01-01T00:00:00Z",
    "results": {
        # Your task-specific results
    },
    "metadata": {
        "version": "1.0.0",
        "parameters": {...}
    },
    "errors": [],    # List of error messages
    "warnings": []   # List of warning messages
}
```

### How do I validate task parameters?

Override the `validate_params` method:

```python
def validate_params(self, **kwargs):
    super().validate_params(**kwargs)
    
    # Custom validation
    if "timeout" in kwargs and kwargs["timeout"] < 1:
        raise ValidationError("Timeout must be positive")
    
    if "target" in kwargs and not kwargs["target"].startswith("http"):
        raise ValidationError("Target must be a valid URL")
```

### Can I use external tools in my task?

Yes, you can call external tools using subprocess:

```python
import subprocess
import json

async def execute(self, context, **kwargs):
    # Call external tool
    result = subprocess.run(
        ["external-tool", "--arg", kwargs["target"]],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    if result.returncode != 0:
        raise TaskError(f"External tool failed: {result.stderr}")
    
    # Parse output
    output = json.loads(result.stdout)
    
    return {
        "status": "completed",
        "results": output,
        "metadata": {"tool_version": "1.0.0"}
    }
```

### How do I handle errors in my task?

Use proper exception handling and SentinelX error types:

```python
from sentinelx.core.task import TaskError, ValidationError

async def execute(self, context, **kwargs):
    try:
        # Your task logic
        result = await self.perform_analysis()
        return result
        
    except FileNotFoundError as e:
        raise TaskError(f"Required file not found: {e}")
    
    except subprocess.TimeoutExpired:
        raise TaskError("Analysis timed out")
    
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Unexpected error in {self.name}: {e}")
        raise TaskError(f"Task execution failed: {e}")
```

## Workflows

### What are workflows and when should I use them?

Workflows orchestrate multiple security tasks in sequence or parallel. Use workflows for:
- **Comprehensive security audits** (multiple analysis tools)
- **Complex penetration testing** (reconnaissance → scanning → exploitation)
- **Compliance checking** (multiple validation steps)
- **Incident response procedures** (structured investigation steps)

### How do I create a workflow?

Create a YAML file describing your workflow:

```yaml
workflow:
  name: "Smart Contract Audit"
  steps:
    - name: "static_analysis"
      task: "slither"
      parameters: {contract_path: "${contract_path}"}
      
    - name: "symbolic_execution"
      task: "mythril"
      parameters: {contract_path: "${contract_path}"}
      depends_on: ["static_analysis"]
      
    - name: "generate_report"
      task: "report-generator"
      parameters:
        inputs: ["${static_analysis.results}", "${symbolic_execution.results}"]
      depends_on: ["static_analysis", "symbolic_execution"]
```

### How do I pass data between workflow steps?

Use variable substitution to pass results between steps:

```yaml
steps:
  - name: "scan"
    task: "scanner"
    parameters: {target: "${target_url}"}
    
  - name: "analyze"
    task: "analyzer"
    parameters:
      scan_results: "${scan.results}"
      vulnerabilities: "${scan.results.vulnerabilities}"
```

### Can workflows handle failures gracefully?

Yes, workflows support error handling:

```yaml
workflow:
  config:
    retry_failed: true
    continue_on_error: true
    
  steps:
    - name: "risky_task"
      task: "might-fail"
      optional: true  # Continue even if this fails
      retry_on_failure: true
      retry_count: 3
```

### How do I run workflows?

```bash
# Run workflow file
sentinelx workflow run audit.yaml

# Run with variables
sentinelx workflow run audit.yaml -v contract_path=MyToken.sol

# List available workflows
sentinelx workflow list

# Validate workflow before running
sentinelx workflow validate audit.yaml
```

## Docker & Deployment

### Does SentinelX support Docker?

Yes, SentinelX has comprehensive Docker support:

```bash
# Setup Docker environment
sentinelx docker setup

# Run task in container
sentinelx docker run slither -p "{contract_path: 'MyToken.sol'}"

# Cleanup containers
sentinelx docker cleanup
```

### How do I configure Docker settings?

In your configuration file:

```yaml
sentinelx:
  docker:
    enabled: true
    base_image: "python:3.9-slim"
    memory_limit: "2g"
    cpu_limit: "2"
    network: "bridge"
    volumes:
      - "${PWD}/contracts:/contracts:ro"
      - "${PWD}/output:/output:rw"
```

### Can I use custom Docker images for specific tasks?

Yes, specify custom images in configuration:

```yaml
sentinelx:
  docker:
    task_images:
      slither: "trailofbits/slither:latest"
      mythril: "mythril/myth:latest"
      custom-task: "my-org/custom-security-tool:v1.0"
```

### Is SentinelX available as a Docker image?

Currently, you need to build your own Docker image:

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Install SentinelX
COPY . /app
WORKDIR /app
RUN pip install -e .

ENTRYPOINT ["sentinelx"]
```

## Performance & Optimization

### How can I improve task performance?

1. **Use appropriate timeout values**
2. **Enable parallel execution in workflows**
3. **Use Docker for resource isolation**
4. **Optimize task parameters**

```bash
# Profile task performance
sentinelx perf profile slither -p "{contract_path: 'token.sol'}"

# Run benchmark
sentinelx perf benchmark --tasks slither,mythril
```

### Why are some tasks slow?

Common reasons for slow performance:
- **Large input files**: Some tools scale poorly with file size
- **Deep analysis settings**: Tools like Mythril can be configured for deeper analysis
- **Network dependencies**: Tasks that fetch external data
- **Insufficient resources**: CPU/memory constraints

### How do I monitor resource usage?

Enable performance monitoring:

```yaml
sentinelx:
  performance:
    profiling_enabled: true
    metrics_collection: true
    benchmark_enabled: true
```

```bash
# View performance metrics
sentinelx perf metrics --task slither --timeframe 24h
```

### Can I limit resource usage?

Yes, configure resource limits:

```yaml
sentinelx:
  limits:
    max_memory: "4g"
    max_cpu: 4
    max_execution_time: 1800  # 30 minutes
    max_file_size: "100MB"
```

## Troubleshooting

### Common Error Messages

#### "Task 'xyz' not found"
**Cause**: Task is not registered or misspelled.
**Solution**: 
```bash
# List available tasks
sentinelx list

# Check task name spelling
sentinelx search "xyz"
```

#### "Required parameter 'param' missing"
**Cause**: Task requires a parameter that wasn't provided.
**Solution**:
```bash
# Check task requirements
sentinelx info task-name --show-params

# Provide required parameter
sentinelx run task-name -p "{param: 'value'}"
```

#### "Permission denied" errors
**Cause**: Insufficient file system permissions.
**Solution**:
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate

# Or run with appropriate permissions
sudo sentinelx run task-name
```

#### "Docker not available"
**Cause**: Docker is not installed or not running.
**Solution**:
```bash
# Install Docker
# https://docs.docker.com/get-docker/

# Start Docker service
sudo systemctl start docker

# Disable Docker in config if not needed
sentinelx config set docker.enabled false
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Enable debug output
sentinelx run task-name -v -p "{...}"

# Or set in configuration
sentinelx config set debug true
```

### Log Files

Check log files for detailed error information:

```bash
# Default log location
tail -f ~/.sentinelx/logs/sentinelx.log

# Or check current directory
tail -f ./sentinelx.log
```

### Getting Help

If you can't resolve an issue:

1. **Check documentation**: [docs/](../docs/)
2. **Search issues**: [GitHub Issues](https://github.com/your-org/sentinelx/issues)
3. **Ask community**: [GitHub Discussions](https://github.com/your-org/sentinelx/discussions)
4. **Report bug**: Create new issue with details

## Security & Best Practices

### Is it safe to run SentinelX on production systems?

**No**, SentinelX should not be run on production systems. Use dedicated security testing environments:

- **Isolated networks**: Separate from production
- **Test data**: Use anonymized or synthetic data
- **Resource limits**: Configure appropriate limits
- **Monitoring**: Enable audit logging

### How do I secure SentinelX deployments?

1. **Use Docker containers** for isolation
2. **Configure resource limits** to prevent DoS
3. **Enable audit logging** for compliance
4. **Restrict network access** to required services only
5. **Use encrypted storage** for sensitive results

```yaml
sentinelx:
  security:
    audit_logging: true
    encrypt_results: true
    sandbox_enabled: true
    max_file_size: "100MB"
    allowed_extensions: [".sol", ".py", ".js"]
```

### Should I run SentinelX as root?

**No**, never run SentinelX as root. Use:
- **Dedicated user account** with minimal privileges
- **Virtual environments** for Python dependencies
- **Docker containers** for additional isolation

### How do I handle sensitive data?

1. **Avoid sensitive data** in task parameters
2. **Use configuration files** for secrets
3. **Enable encryption** for stored results
4. **Implement data retention policies**

```yaml
sentinelx:
  security:
    encrypt_results: true
    data_retention_days: 30
    anonymize_logs: true
```

### What data does SentinelX collect?

SentinelX only collects data you explicitly provide:
- **Task parameters** and results
- **Performance metrics** (if enabled)
- **Log data** for debugging
- **Configuration settings**

No data is sent to external services without your explicit configuration.

## Contributing

### How can I contribute to SentinelX?

See our [Contributing Guide](CONTRIBUTING.md) for detailed information. Ways to contribute:
- **Report bugs** and suggest features
- **Write security tasks** for new tools
- **Improve documentation** and examples
- **Submit code improvements** and fixes

### I found a security vulnerability. How do I report it?

**Do not** report security vulnerabilities in public issues. Instead:
1. **Email**: security@sentinelx.org
2. **Provide details**: Clear description and reproduction steps
3. **Be patient**: We'll respond within 48 hours

### How do I add a new security tool integration?

1. **Create a task class** that wraps your tool
2. **Add proper error handling** and validation
3. **Write tests** for your integration
4. **Update documentation** with usage examples
5. **Submit a pull request**

See [examples/custom_task_example.py](../examples/custom_task_example.py) for a complete example.

### Can I get paid for contributing?

Currently, SentinelX is a volunteer-driven open source project. We recognize contributions through:
- **Contributor recognition** in documentation
- **Maintainer opportunities** for regular contributors
- **Conference speaking opportunities** (when available)

---

## Still Have Questions?

If your question isn't answered here:

1. **Search the documentation**: Check all guides and references
2. **GitHub Discussions**: Ask the community
3. **GitHub Issues**: Report bugs or request features
4. **Discord**: Join our community chat (link in README)

We're here to help you succeed with SentinelX!
