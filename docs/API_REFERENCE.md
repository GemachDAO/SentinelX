# SentinelX API Reference

Complete API reference for the SentinelX security framework.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Task System](#task-system)
3. [Plugin Registry](#plugin-registry)
4. [Context Management](#context-management)
5. [Workflow Engine](#workflow-engine)
6. [Deployment](#deployment)
7. [Performance](#performance)
8. [Reporting](#reporting)
9. [Utilities](#utilities)

## Core Classes

### Task

Base class for all SentinelX security tasks.

```python
from sentinelx.core.task import Task

class Task:
    """
    Base class for all security tasks in SentinelX.
    
    Attributes:
        name: Unique task identifier
        description: Human-readable task description
        REQUIRED_PARAMS: List of required parameter names
        OPTIONAL_PARAMS: List of optional parameter names
    """
    
    async def execute(self, context: Context, **kwargs) -> Dict[str, Any]:
        """
        Execute the security task.
        
        Args:
            context: Execution context with configuration
            **kwargs: Task parameters
            
        Returns:
            Dictionary containing task results
            
        Raises:
            TaskError: If task execution fails
            ValidationError: If parameters are invalid
        """
        pass
    
    def validate_params(self, **kwargs) -> None:
        """
        Validate task parameters.
        
        Args:
            **kwargs: Parameters to validate
            
        Raises:
            ValidationError: If required parameters are missing
        """
        pass
```

#### Task Decorators

```python
from sentinelx.core.task import register_task, task_metadata

@register_task("my-task")
@task_metadata(
    category="custom",
    description="My custom security task",
    tags=["security", "custom"],
    version="1.0.0"
)
class MyTask(Task):
    pass
```

### Context

Execution context containing configuration and environment.

```python
from sentinelx.core.context import Context

class Context:
    """
    Execution context for tasks and workflows.
    
    Attributes:
        config: Configuration dictionary
        environment: Environment variables
        working_dir: Working directory path
        temp_dir: Temporary directory path
    """
    
    @classmethod
    def load(cls, config_path: str = "config.yaml") -> "Context":
        """
        Load context from configuration file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Initialized Context instance
        """
        pass
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        pass
    
    def set(self, key: str, value):
        """Set configuration value."""
        pass
```

### PluginRegistry

Central registry for task discovery and management.

```python
from sentinelx.core.registry import PluginRegistry

class PluginRegistry:
    """
    Central registry for task plugins and management.
    """
    
    @classmethod
    def discover(cls) -> None:
        """Discover and register all available tasks."""
        pass
    
    @classmethod
    def register(cls, name: str, task_class: Type[Task]) -> None:
        """
        Register a task class.
        
        Args:
            name: Task identifier
            task_class: Task class to register
        """
        pass
    
    @classmethod
    def create(cls, name: str, **kwargs) -> Task:
        """
        Create task instance.
        
        Args:
            name: Task identifier
            **kwargs: Task parameters
            
        Returns:
            Task instance
        """
        pass
    
    @classmethod
    def list_tasks(cls) -> List[Dict[str, Any]]:
        """List all registered tasks."""
        pass
    
    @classmethod
    def search_tasks(cls, query: str) -> List[Dict[str, Any]]:
        """Search tasks by name or description."""
        pass
```

## Task System

### Task Categories

SentinelX organizes tasks into the following categories:

#### Smart Contract Auditing
- `slither` - Static analysis with Slither
- `mythril` - Symbolic execution with Mythril
- `cvss` - CVSS scoring calculator

#### Exploit Development
- `shellcode` - Shellcode generation
- `fuzzer` - Web application fuzzing
- `exploit-gen` - Automated exploit generation

#### Blockchain Security
- `chain-monitor` - Blockchain monitoring
- `transaction-replay` - Transaction replay attacks
- `rwa-scan` - RWA token scanning

#### Red Team Operations
- `c2` - Command and control operations
- `lateral-move` - Lateral movement techniques
- `social-eng` - Social engineering campaigns

#### Digital Forensics
- `memory-dump` - Memory analysis
- `disk-forensics` - Disk forensics
- `chain-ir` - Blockchain incident response

#### AI Security
- `llm-assist` - AI-powered security assistance
- `adversarial` - Adversarial AI testing

#### Web Security
- `web2-static` - Static web application analysis

### Task Parameters

All tasks accept parameters through a standardized interface:

```python
# Required parameters - must be provided
REQUIRED_PARAMS = ["target", "output_dir"]

# Optional parameters - have defaults
OPTIONAL_PARAMS = ["timeout", "verbose", "format"]

# Parameter validation
def validate_params(self, **kwargs):
    for param in self.REQUIRED_PARAMS:
        if param not in kwargs:
            raise ValidationError(f"Required parameter '{param}' missing")
```

### Task Results

Tasks return standardized result dictionaries:

```python
{
    "status": "completed",  # completed, failed, timeout
    "task": "slither",
    "duration": 12.34,
    "timestamp": "2024-01-01T00:00:00Z",
    "results": {
        # Task-specific results
    },
    "metadata": {
        "version": "1.0.0",
        "parameters": {...},
        "environment": {...}
    },
    "errors": [],  # List of error messages if any
    "warnings": []  # List of warning messages if any
}
```

## Workflow Engine

### WorkflowEngine

Orchestrates multi-step security workflows.

```python
from sentinelx.core.workflow import WorkflowEngine

class WorkflowEngine:
    """
    Workflow orchestration engine for complex security operations.
    """
    
    async def execute_workflow(
        self, 
        workflow_config: Dict[str, Any],
        context: Context
    ) -> Dict[str, Any]:
        """
        Execute a workflow from configuration.
        
        Args:
            workflow_config: Workflow definition
            context: Execution context
            
        Returns:
            Workflow execution results
        """
        pass
    
    def validate_workflow(self, workflow_config: Dict[str, Any]) -> List[str]:
        """
        Validate workflow configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        pass
```

### Workflow Configuration

```yaml
# workflow.yaml
workflow:
  name: "Smart Contract Security Audit"
  version: "1.0.0"
  description: "Comprehensive smart contract security analysis"
  
  variables:
    contract_path: "MyToken.sol"
    output_dir: "./audit_results"
  
  steps:
    - name: "static_analysis"
      task: "slither"
      parameters:
        contract_path: "${contract_path}"
        format: "json"
      timeout: 300
      
    - name: "symbolic_execution"
      task: "mythril"
      parameters:
        contract_path: "${contract_path}"
        timeout: 600
      depends_on: ["static_analysis"]
      
    - name: "cvss_scoring"
      task: "cvss"
      parameters:
        findings: "${static_analysis.results.vulnerabilities}"
      depends_on: ["static_analysis"]
  
  on_failure:
    - action: "notify"
      target: "admin@company.com"
    - action: "cleanup"
      target: "${output_dir}"
```

## Deployment

### DockerManager

Container-based task execution for enhanced security.

```python
from sentinelx.deployment import DockerManager

class DockerManager:
    """
    Docker-based deployment and sandboxing manager.
    """
    
    async def setup_environment(
        self, 
        task_name: str,
        requirements: List[str] = None
    ) -> str:
        """
        Set up isolated Docker environment for task.
        
        Args:
            task_name: Name of the task
            requirements: Additional package requirements
            
        Returns:
            Container ID
        """
        pass
    
    async def execute_task(
        self, 
        container_id: str,
        task: Task,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute task in Docker container.
        
        Args:
            container_id: Target container
            task: Task to execute
            **kwargs: Task parameters
            
        Returns:
            Task execution results
        """
        pass
    
    async def cleanup(self, container_id: str) -> None:
        """Clean up container resources."""
        pass
```

## Performance

### PerformanceProfiler

Performance monitoring and optimization tools.

```python
from sentinelx.performance import PerformanceProfiler

class PerformanceProfiler:
    """
    Performance profiling and monitoring for tasks.
    """
    
    async def profile_task(
        self, 
        task: Task,
        iterations: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Profile task performance.
        
        Args:
            task: Task to profile
            iterations: Number of profiling iterations
            **kwargs: Task parameters
            
        Returns:
            Performance metrics
        """
        pass
    
    def analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze profiling results and generate recommendations."""
        pass
```

### BenchmarkSuite

Comprehensive benchmarking for security tasks.

```python
from sentinelx.performance import BenchmarkSuite

class BenchmarkSuite:
    """
    Benchmark suite for performance testing.
    """
    
    async def run_benchmark(
        self, 
        task_names: List[str],
        test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run benchmark tests for specified tasks.
        
        Args:
            task_names: Tasks to benchmark
            test_data: Test data and parameters
            
        Returns:
            Benchmark results
        """
        pass
```

## Reporting

### ReportGenerator

Advanced reporting and visualization tools.

```python
from sentinelx.reporting import ReportGenerator, SecurityReport

class ReportGenerator:
    """
    Advanced security report generation.
    """
    
    def generate_report(
        self, 
        results: List[Dict[str, Any]],
        template: str = "default",
        format: str = "html"
    ) -> SecurityReport:
        """
        Generate comprehensive security report.
        
        Args:
            results: Task execution results
            template: Report template name
            format: Output format (html, pdf, json)
            
        Returns:
            Generated security report
        """
        pass
    
    def create_dashboard(
        self, 
        reports: List[SecurityReport]
    ) -> str:
        """Create interactive security dashboard."""
        pass
```

## Error Handling

### TaskError

Base exception for task-related errors.

```python
from sentinelx.core.task import TaskError

class TaskError(Exception):
    """
    Base exception for task execution errors.
    
    Attributes:
        task: Task that caused the error
        message: Error message
        details: Additional error details
    """
    
    def __init__(
        self, 
        message: str, 
        task: str = None,
        details: Dict = None
    ):
        self.task = task
        self.message = message
        self.details = details or {}
        super().__init__(message)
```

### ValidationError

Parameter validation errors.

```python
from sentinelx.core.task import ValidationError

class ValidationError(TaskError):
    """Parameter validation error."""
    pass
```

## Utilities

### Utility Functions

Common utility functions used across the framework.

```python
from sentinelx.core.utils import (
    load_config,
    validate_file_path,
    create_temp_dir,
    format_duration,
    sanitize_filename
)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    pass

def validate_file_path(path: str, must_exist: bool = True) -> Path:
    """Validate and normalize file path."""
    pass

def create_temp_dir(prefix: str = "sentinelx") -> Path:
    """Create temporary directory."""
    pass

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    pass

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage."""
    pass
```

## Configuration Schema

### Main Configuration

```yaml
# config.yaml
sentinelx:
  # Global settings
  version: "1.0.0"
  debug: false
  max_workers: 4
  timeout: 3600
  
  # Directories
  working_dir: "./work"
  output_dir: "./output"
  temp_dir: "/tmp/sentinelx"
  
  # Logging
  logging:
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: "sentinelx.log"
  
  # Task defaults
  task_defaults:
    timeout: 300
    retry_count: 3
    retry_delay: 5
  
  # External tools
  tools:
    slither:
      binary: "slither"
      extra_args: []
    mythril:
      binary: "myth"
      timeout: 600
  
  # Docker settings
  docker:
    enabled: false
    base_image: "python:3.9-slim"
    network: "bridge"
    memory_limit: "2g"
  
  # Performance
  performance:
    profiling_enabled: false
    benchmark_enabled: false
    metrics_retention_days: 30
  
  # Reporting
  reporting:
    default_format: "html"
    include_charts: true
    theme: "default"
```

## Examples

### Basic Task Usage

```python
import asyncio
from sentinelx.core.context import Context
from sentinelx.core.registry import PluginRegistry

async def main():
    # Load configuration
    context = Context.load("config.yaml")
    
    # Create task
    task = PluginRegistry.create(
        "slither",
        contract_path="MyToken.sol",
        format="json"
    )
    
    # Execute task
    result = await task.execute(context)
    print(result)

asyncio.run(main())
```

### Custom Task Development

```python
from sentinelx.core.task import Task, register_task
from typing import Dict, Any

@register_task("my-scanner")
class MySecurityScanner(Task):
    """Custom security scanner task."""
    
    REQUIRED_PARAMS = ["target"]
    OPTIONAL_PARAMS = ["depth", "timeout"]
    
    async def execute(self, context, **kwargs) -> Dict[str, Any]:
        target = kwargs["target"]
        depth = kwargs.get("depth", 3)
        
        # Implement your security scanning logic
        vulnerabilities = await self.scan_target(target, depth)
        
        return {
            "status": "completed",
            "target": target,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "scan_depth": depth
        }
    
    async def scan_target(self, target: str, depth: int) -> List[Dict]:
        # Your scanning implementation
        return []
```

## CLI Integration

All API components are accessible through the CLI:

```bash
# List available tasks
sentinelx list

# Get task information
sentinelx info slither

# Run task with parameters
sentinelx run slither -p "{contract_path: 'MyToken.sol'}"

# Execute workflow
sentinelx workflow run audit_workflow.yaml

# Performance profiling
sentinelx perf profile slither -p "{contract_path: 'test.sol'}"

# Generate reports
sentinelx report generate results.json --format html
```

This API reference provides complete documentation for extending and integrating with the SentinelX security framework.
