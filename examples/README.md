# SentinelX Examples

This directory contains practical examples and tutorials for using SentinelX.

## Quick Start Examples

### 1. Basic Task Execution
- `basic_task.py` - Running individual security tasks
- `task_parameters.py` - Working with task parameters
- `error_handling.py` - Handling task errors

### 2. Smart Contract Security
- `smart_contract_audit.py` - Complete smart contract audit workflow
- `defi_security_scan.py` - DeFi protocol security analysis
- `token_security_check.py` - ERC-20 token security validation

### 3. Web Application Security
- `web_security_scan.py` - Web application security assessment
- `api_security_test.py` - REST API security testing
- `vulnerability_scanner.py` - Automated vulnerability detection

### 4. Workflow Orchestration
- `audit_workflow.yaml` - Smart contract audit workflow
- `pentest_workflow.yaml` - Penetration testing workflow
- `compliance_check.yaml` - Security compliance validation

### 5. Custom Task Development
- `custom_task_example.py` - Creating custom security tasks
- `plugin_development.py` - Developing SentinelX plugins
- `integration_example.py` - Integrating external tools

### 6. Advanced Features
- `docker_deployment.py` - Sandboxed task execution
- `performance_optimization.py` - Performance monitoring
- `report_generation.py` - Custom report generation

### 7. Real-World Scenarios
- `incident_response.py` - Security incident response
- `compliance_audit.py` - Regulatory compliance audit
- `threat_modeling.py` - Threat modeling workflow

## Configuration Examples

### Basic Configuration
```yaml
# examples/config/basic.yaml
sentinelx:
  debug: false
  timeout: 1800
  working_dir: "./work"
  output_dir: "./results"
```

### Advanced Configuration
```yaml
# examples/config/advanced.yaml
sentinelx:
  debug: true
  max_workers: 8
  timeout: 3600
  
  docker:
    enabled: true
    memory_limit: "4g"
    
  performance:
    profiling_enabled: true
    benchmark_enabled: true
```

## Running Examples

All examples can be run from the SentinelX root directory:

```bash
# Basic examples
python examples/basic_task.py
python examples/smart_contract_audit.py

# Workflow examples
sentinelx workflow run examples/workflows/audit_workflow.yaml

# Custom development
python examples/custom_task_example.py
```

## Requirements

Some examples may require additional dependencies:

```bash
# Install example dependencies
pip install -r examples/requirements.txt
```

## Contributing Examples

To contribute new examples:

1. Create a new Python file in the appropriate subdirectory
2. Include comprehensive comments and documentation
3. Add error handling and logging
4. Test with various inputs and scenarios
5. Update this README with your example

## Support

For questions about examples or tutorials:

- Check the main documentation in `/docs/`
- Review the API reference in `/docs/API_REFERENCE.md`
- Open an issue for example-specific questions
