# SentinelX Developer Guide

This guide covers extending SentinelX with custom tasks, plugins, and advanced integrations.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Creating Custom Tasks](#creating-custom-tasks)
3. [Plugin Development](#plugin-development)
4. [Core Framework Extension](#core-framework-extension)
5. [Testing](#testing)
6. [Advanced Integration](#advanced-integration)
7. [Best Practices](#best-practices)
8. [API Reference](#api-reference)

## Architecture Overview

SentinelX follows a modular architecture with clear separation of concerns:

```
sentinelx/
├── core/                 # Core framework components
│   ├── registry.py      # Plugin registration and discovery
│   ├── task.py          # Base task class and decorators
│   ├── context.py       # Execution context and configuration
│   ├── workflow.py      # Workflow orchestration engine
│   └── utils.py         # Utility functions and helpers
├── audit/               # Smart contract auditing tasks
├── exploit/             # Exploit development tools
├── blockchain/          # Blockchain security tools
├── redteam/             # Red team operation tools
├── forensic/            # Digital forensics tools
├── ai/                  # AI-powered security tools
├── cli.py               # Command-line interface
└── __init__.py          # Package initialization
```

### Key Components

#### 1. Task System
- **Base Task Class**: All tasks inherit from `sentinelx.core.task.Task`
- **Registration**: Tasks are automatically discovered and registered
- **Execution**: Async execution with context and parameter validation

#### 2. Plugin Registry
- **Discovery**: Automatic plugin discovery via entry points
- **Registration**: Tasks register themselves using decorators
- **Management**: Central registry for all available tasks

#### 3. Context System
- **Configuration**: Centralized configuration management
- **Environment**: Environment variable resolution
- **Sandboxing**: Isolated execution contexts

#### 4. Workflow Engine
- **Orchestration**: Multi-step workflow execution
- **Dependencies**: Topological sorting for task dependencies
- **Error Handling**: Configurable error handling and recovery

## Creating Custom Tasks

### Basic Task Structure

```python
# my_custom_task.py
from sentinelx.core.task import Task, register_task
from typing import Dict, Any
import asyncio

@register_task("my-custom-task")
class MyCustomTask(Task):
    """
    A custom security task that demonstrates the framework.
    
    This task performs custom security analysis and returns results
    in a standardized format.
    """
    
    # Define required parameters (validated at runtime)
    REQUIRED_PARAMS = ["target"]
    
    # Define optional parameters with defaults
    OPTIONAL_PARAMS = ["timeout", "verbose"]
    
    async def execute(self, context: "Context", **kwargs) -> Dict[str, Any]:
        """
        Execute the custom security task.
        
        Args:
            context: Execution context with configuration
            **kwargs: Task parameters
            
        Returns:
            Dict containing task results
        """
        target = kwargs["target"]
        timeout = kwargs.get("timeout", 30)
        verbose = kwargs.get("verbose", False)
        
        if verbose:
            self.logger.info(f"Starting analysis of {target}")
        
        # Perform your custom analysis here
        results = await self._perform_analysis(target, timeout)
        
        return {
            "status": "completed",
            "target": target,
            "results": results,
            "metadata": {
                "execution_time": self.execution_time,
                "timestamp": self.start_time.isoformat()
            }
        }
    
    async def _perform_analysis(self, target: str, timeout: int) -> Dict[str, Any]:
        """Perform the actual analysis."""
        # Simulate analysis work
        await asyncio.sleep(0.1)
        
        return {
            "vulnerabilities_found": 3,
            "severity": "medium",
            "details": f"Analysis completed for {target}"
        }
```

### Advanced Task Features

#### Parameter Validation

```python
@register_task("advanced-task")
class AdvancedTask(Task):
    """Advanced task with parameter validation."""
    
    REQUIRED_PARAMS = ["target", "scan_type"]
    OPTIONAL_PARAMS = ["depth", "timeout"]
    
    def validate_parameters(self, **kwargs) -> None:
        """Custom parameter validation."""
        super().validate_parameters(**kwargs)
        
        # Validate scan_type
        valid_types = ["quick", "deep", "comprehensive"]
        if kwargs["scan_type"] not in valid_types:
            raise ValueError(f"scan_type must be one of: {valid_types}")
        
        # Validate depth range
        depth = kwargs.get("depth", 1)
        if not 1 <= depth <= 10:
            raise ValueError("depth must be between 1 and 10")
    
    async def execute(self, context, **kwargs):
        # Parameters are already validated
        scan_type = kwargs["scan_type"]
        depth = kwargs.get("depth", 1)
        
        # Implementation based on scan_type
        if scan_type == "quick":
            return await self._quick_scan(**kwargs)
        elif scan_type == "deep":
            return await self._deep_scan(depth, **kwargs)
        else:
            return await self._comprehensive_scan(depth, **kwargs)
```

#### Error Handling

```python
from sentinelx.core.task import TaskError

@register_task("robust-task")
class RobustTask(Task):
    """Task with robust error handling."""
    
    async def execute(self, context, **kwargs):
        try:
            # Risky operation
            result = await self._risky_operation(**kwargs)
            return {"status": "success", "data": result}
            
        except ConnectionError as e:
            # Handle network errors
            self.logger.error(f"Network error: {e}")
            raise TaskError(f"Failed to connect to target: {e}")
            
        except TimeoutError as e:
            # Handle timeout errors
            self.logger.warning(f"Operation timed out: {e}")
            return {
                "status": "timeout",
                "error": str(e),
                "partial_results": self._get_partial_results()
            }
            
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise TaskError(f"Task execution failed: {e}")
    
    async def _risky_operation(self, **kwargs):
        """Simulate a risky operation."""
        # Your implementation here
        pass
    
    def _get_partial_results(self):
        """Return partial results if available."""
        return {"partial": True, "message": "Operation incomplete"}
```

#### Progress Tracking

```python
from rich.progress import Progress

@register_task("progress-task")
class ProgressTask(Task):
    """Task with progress tracking."""
    
    async def execute(self, context, **kwargs):
        items = kwargs.get("items", [])
        
        with Progress() as progress:
            task_progress = progress.add_task(
                "[cyan]Processing items...", 
                total=len(items)
            )
            
            results = []
            for i, item in enumerate(items):
                # Process item
                result = await self._process_item(item)
                results.append(result)
                
                # Update progress
                progress.update(
                    task_progress, 
                    completed=i+1,
                    description=f"[cyan]Processed {i+1}/{len(items)} items"
                )
        
        return {
            "status": "completed",
            "processed_count": len(results),
            "results": results
        }
    
    async def _process_item(self, item):
        """Process a single item."""
        await asyncio.sleep(0.1)  # Simulate work
        return {"item": item, "processed": True}
```

### External Tool Integration

#### Subprocess Integration

```python
import subprocess
import tempfile
from pathlib import Path

@register_task("external-tool")
class ExternalToolTask(Task):
    """Task that integrates with external security tools."""
    
    REQUIRED_PARAMS = ["target_file"]
    
    async def execute(self, context, **kwargs):
        target_file = Path(kwargs["target_file"])
        
        if not target_file.exists():
            raise TaskError(f"Target file not found: {target_file}")
        
        # Run external tool
        result = await self._run_external_tool(target_file)
        
        # Parse and return results
        return self._parse_tool_output(result)
    
    async def _run_external_tool(self, target_file: Path) -> str:
        """Run external security tool."""
        cmd = ["security-scanner", "--format", "json", str(target_file)]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise TaskError(f"External tool failed: {error_msg}")
            
            return stdout.decode()
            
        except FileNotFoundError:
            raise TaskError("External tool 'security-scanner' not found")
    
    def _parse_tool_output(self, output: str) -> Dict[str, Any]:
        """Parse tool output into standardized format."""
        try:
            import json
            raw_data = json.loads(output)
            
            return {
                "status": "completed",
                "vulnerabilities": raw_data.get("vulnerabilities", []),
                "summary": {
                    "total_issues": len(raw_data.get("vulnerabilities", [])),
                    "severity_breakdown": self._analyze_severity(raw_data)
                }
            }
        except json.JSONDecodeError as e:
            raise TaskError(f"Failed to parse tool output: {e}")
    
    def _analyze_severity(self, data: Dict) -> Dict[str, int]:
        """Analyze vulnerability severity distribution."""
        severity_count = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for vuln in data.get("vulnerabilities", []):
            severity = vuln.get("severity", "unknown").lower()
            if severity in severity_count:
                severity_count[severity] += 1
        
        return severity_count
```

#### HTTP API Integration

```python
import aiohttp
import asyncio

@register_task("api-scanner")
class APIScanner(Task):
    """Task that integrates with HTTP APIs."""
    
    REQUIRED_PARAMS = ["api_endpoint"]
    OPTIONAL_PARAMS = ["api_key", "timeout"]
    
    async def execute(self, context, **kwargs):
        endpoint = kwargs["api_endpoint"]
        api_key = kwargs.get("api_key")
        timeout = kwargs.get("timeout", 30)
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            results = await self._scan_api(session, endpoint, api_key)
        
        return results
    
    async def _scan_api(self, session: aiohttp.ClientSession, endpoint: str, api_key: str = None):
        """Scan API endpoint for vulnerabilities."""
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            # Test basic connectivity
            async with session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Perform security analysis
                    security_analysis = await self._analyze_api_security(session, endpoint, headers)
                    
                    return {
                        "status": "completed",
                        "endpoint": endpoint,
                        "response_status": response.status,
                        "security_analysis": security_analysis
                    }
                else:
                    return {
                        "status": "error",
                        "endpoint": endpoint,
                        "error": f"HTTP {response.status}"
                    }
        
        except aiohttp.ClientError as e:
            raise TaskError(f"Failed to connect to API: {e}")
    
    async def _analyze_api_security(self, session, endpoint, headers):
        """Perform security analysis of the API."""
        analysis = {
            "ssl_security": await self._check_ssl_security(session, endpoint),
            "authentication": await self._check_authentication(session, endpoint, headers),
            "rate_limiting": await self._check_rate_limiting(session, endpoint, headers)
        }
        return analysis
    
    async def _check_ssl_security(self, session, endpoint):
        """Check SSL/TLS security."""
        # Implementation for SSL analysis
        return {"secure": True, "details": "TLS 1.2+ enabled"}
    
    async def _check_authentication(self, session, endpoint, headers):
        """Check authentication mechanisms."""
        # Implementation for auth analysis
        return {"method": "bearer_token", "secure": bool(headers.get("Authorization"))}
    
    async def _check_rate_limiting(self, session, endpoint, headers):
        """Check rate limiting implementation."""
        # Implementation for rate limit testing
        return {"implemented": True, "limit": "100/minute"}
```

## Plugin Development

### Plugin Structure

Create a plugin package that can be installed separately:

```
my_sentinelx_plugin/
├── setup.py
├── my_sentinelx_plugin/
│   ├── __init__.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── custom_audit.py
│   │   └── custom_exploit.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
└── tests/
    ├── __init__.py
    └── test_tasks.py
```

#### Plugin Entry Points

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="my-sentinelx-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "sentinelx>=1.0.0",
        # Other dependencies
    ],
    entry_points={
        "sentinelx.tasks": [
            "custom-audit = my_sentinelx_plugin.tasks.custom_audit:CustomAuditTask",
            "custom-exploit = my_sentinelx_plugin.tasks.custom_exploit:CustomExploitTask",
        ]
    }
)
```

#### Plugin Tasks

```python
# my_sentinelx_plugin/tasks/custom_audit.py
from sentinelx.core.task import Task, register_task

@register_task("custom-audit")
class CustomAuditTask(Task):
    """Custom audit task from plugin."""
    
    async def execute(self, context, **kwargs):
        # Plugin-specific implementation
        return {"status": "completed", "plugin": "my-custom-plugin"}
```

### Plugin Installation

```bash
# Install plugin
pip install my-sentinelx-plugin

# Verify installation
sentinelx list | grep custom

# Use plugin task
sentinelx run custom-audit
```

## Core Framework Extension

### Extending the Context System

```python
# custom_context.py
from sentinelx.core.context import Context
from typing import Dict, Any

class CustomContext(Context):
    """Extended context with custom functionality."""
    
    def __init__(self, config_data: Dict[str, Any] = None):
        super().__init__(config_data)
        self._custom_cache = {}
    
    def get_custom_setting(self, key: str, default=None):
        """Get custom setting with caching."""
        if key in self._custom_cache:
            return self._custom_cache[key]
        
        value = self.config.get("custom", {}).get(key, default)
        self._custom_cache[key] = value
        return value
    
    def set_custom_setting(self, key: str, value):
        """Set custom setting."""
        if "custom" not in self.config:
            self.config["custom"] = {}
        self.config["custom"][key] = value
        self._custom_cache[key] = value
```

### Custom Registry Extensions

```python
# custom_registry.py
from sentinelx.core.registry import PluginRegistry
from typing import List, Dict, Any

class CustomPluginRegistry(PluginRegistry):
    """Extended registry with custom features."""
    
    def __init__(self):
        super().__init__()
        self._task_metadata = {}
    
    def register_with_metadata(self, name: str, task_class, metadata: Dict[str, Any]):
        """Register task with additional metadata."""
        self.register(name, task_class)
        self._task_metadata[name] = metadata
    
    def get_tasks_by_category(self, category: str) -> List[str]:
        """Get tasks filtered by category."""
        matching_tasks = []
        for task_name, metadata in self._task_metadata.items():
            if metadata.get("category") == category:
                matching_tasks.append(task_name)
        return matching_tasks
    
    def get_task_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a specific task."""
        return self._task_metadata.get(name, {})
```

### Custom Workflow Steps

```python
# custom_workflow.py
from sentinelx.core.workflow import WorkflowEngine, WorkflowStep
from typing import Dict, Any

class CustomWorkflowStep(WorkflowStep):
    """Extended workflow step with custom features."""
    
    def __init__(self, name: str, task: str, params: Dict[str, Any] = None, **kwargs):
        super().__init__(name, task, params, **kwargs)
        self.retry_count = kwargs.get("retry_count", 0)
        self.retry_delay = kwargs.get("retry_delay", 1)
    
    async def execute_with_retry(self, engine: WorkflowEngine, context):
        """Execute step with retry logic."""
        for attempt in range(self.retry_count + 1):
            try:
                return await self.execute(engine, context)
            except Exception as e:
                if attempt < self.retry_count:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise e

class CustomWorkflowEngine(WorkflowEngine):
    """Extended workflow engine with custom step types."""
    
    def create_step(self, step_data: Dict[str, Any]) -> WorkflowStep:
        """Create custom workflow step."""
        if step_data.get("type") == "retry":
            return CustomWorkflowStep(**step_data)
        return super().create_step(step_data)
```

## Testing

### Unit Testing Tasks

```python
# tests/test_my_custom_task.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from sentinelx.core.context import Context
from my_custom_task import MyCustomTask

class TestMyCustomTask:
    
    @pytest.fixture
    def context(self):
        """Create test context."""
        return Context()
    
    @pytest.fixture
    def task(self):
        """Create task instance."""
        return MyCustomTask()
    
    @pytest.mark.asyncio
    async def test_execute_success(self, task, context):
        """Test successful task execution."""
        params = {"target": "test.example.com", "timeout": 30}
        
        result = await task.execute(context, **params)
        
        assert result["status"] == "completed"
        assert result["target"] == "test.example.com"
        assert "results" in result
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_target(self, task, context):
        """Test task execution with invalid target."""
        params = {"target": "", "timeout": 30}
        
        with pytest.raises(ValueError):
            await task.execute(context, **params)
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, task, context):
        """Test parameter validation."""
        # Missing required parameter
        with pytest.raises(ValueError):
            task.validate_parameters(timeout=30)
        
        # Valid parameters
        task.validate_parameters(target="test.com", timeout=30)
    
    @pytest.mark.asyncio
    async def test_with_mocked_external_call(self, task, context):
        """Test task with mocked external dependencies."""
        params = {"target": "test.com"}
        
        with patch.object(task, '_perform_analysis') as mock_analysis:
            mock_analysis.return_value = {"vulnerabilities_found": 0}
            
            result = await task.execute(context, **params)
            
            assert result["status"] == "completed"
            mock_analysis.assert_called_once_with("test.com", 30)
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
import tempfile
from pathlib import Path
from sentinelx.core.registry import PluginRegistry
from sentinelx.core.context import Context

class TestIntegration:
    
    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return PluginRegistry()
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary configuration file."""
        config_data = """
        version: "1.0"
        debug: true
        test_mode: true
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_data)
            yield f.name
        
        Path(f.name).unlink()
    
    def test_task_registration(self, registry):
        """Test task registration."""
        initial_count = len(registry.list_tasks())
        
        # Register test task
        @register_task("test-task")
        class TestTask(Task):
            async def execute(self, context, **kwargs):
                return {"test": True}
        
        assert len(registry.list_tasks()) == initial_count + 1
        assert "test-task" in registry.list_tasks()
    
    def test_context_loading(self, temp_config):
        """Test context loading from file."""
        context = Context.load(temp_config)
        
        assert context.config["version"] == "1.0"
        assert context.config["debug"] is True
    
    @pytest.mark.asyncio
    async def test_end_to_end_execution(self, registry, temp_config):
        """Test end-to-end task execution."""
        context = Context.load(temp_config)
        
        # Create and execute task
        task_instance = registry.create("cvss", ctx=context, 
                                       vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L")
        
        result = await task_instance()
        
        assert "score" in result
        assert "severity" in result
```

### Workflow Testing

```python
# tests/test_workflow.py
import pytest
import yaml
import tempfile
from pathlib import Path
from sentinelx.core.workflow import WorkflowEngine
from sentinelx.core.context import Context
from sentinelx.core.registry import PluginRegistry

class TestWorkflow:
    
    @pytest.fixture
    def workflow_definition(self):
        """Create test workflow definition."""
        return {
            "name": "test_workflow",
            "description": "Test workflow",
            "steps": [
                {
                    "name": "step1",
                    "task": "cvss",
                    "params": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L"}
                },
                {
                    "name": "step2",
                    "task": "cvss",
                    "params": {"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"},
                    "depends_on": ["step1"]
                }
            ]
        }
    
    @pytest.fixture
    def workflow_file(self, workflow_definition):
        """Create temporary workflow file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(workflow_definition, f)
            yield f.name
        
        Path(f.name).unlink()
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self, workflow_file):
        """Test workflow execution."""
        context = Context()
        registry = PluginRegistry()
        engine = WorkflowEngine(registry)
        
        # Load and execute workflow
        workflow_def = await engine.load_workflow(Path(workflow_file))
        result = await engine.execute_workflow(workflow_def, context)
        
        assert result.status == "completed"
        assert len(result.steps_completed) == 2
        assert result.errors == []
    
    @pytest.mark.asyncio
    async def test_workflow_dependency_resolution(self, workflow_definition):
        """Test workflow dependency resolution."""
        context = Context()
        registry = PluginRegistry()
        engine = WorkflowEngine(registry)
        
        # Test dependency order
        steps = engine._resolve_dependencies(workflow_definition["steps"])
        
        # step1 should come before step2
        step1_index = next(i for i, s in enumerate(steps) if s.name == "step1")
        step2_index = next(i for i, s in enumerate(steps) if s.name == "step2")
        
        assert step1_index < step2_index
```

## Advanced Integration

### Database Integration

```python
# database_task.py
import aiosqlite
from sentinelx.core.task import Task, register_task

@register_task("database-scan")
class DatabaseScanTask(Task):
    """Task that integrates with databases."""
    
    REQUIRED_PARAMS = ["database_path"]
    OPTIONAL_PARAMS = ["query_timeout"]
    
    async def execute(self, context, **kwargs):
        db_path = kwargs["database_path"]
        timeout = kwargs.get("query_timeout", 30)
        
        async with aiosqlite.connect(db_path, timeout=timeout) as db:
            results = await self._scan_database(db)
        
        return results
    
    async def _scan_database(self, db):
        """Perform security scan of database."""
        findings = []
        
        # Check for common security issues
        findings.extend(await self._check_sql_injection_vectors(db))
        findings.extend(await self._check_privilege_escalation(db))
        findings.extend(await self._check_data_exposure(db))
        
        return {
            "status": "completed",
            "findings": findings,
            "summary": {
                "total_issues": len(findings),
                "severity_breakdown": self._analyze_findings(findings)
            }
        }
    
    async def _check_sql_injection_vectors(self, db):
        """Check for SQL injection vulnerabilities."""
        # Implementation for SQL injection detection
        return []
    
    async def _check_privilege_escalation(self, db):
        """Check for privilege escalation opportunities."""
        # Implementation for privilege escalation detection
        return []
    
    async def _check_data_exposure(self, db):
        """Check for data exposure risks."""
        # Implementation for data exposure detection
        return []
```

### Cloud Service Integration

```python
# cloud_security_task.py
import boto3
from botocore.exceptions import ClientError
from sentinelx.core.task import Task, register_task

@register_task("aws-security-scan")
class AWSSecurityScanTask(Task):
    """Task that integrates with AWS services."""
    
    REQUIRED_PARAMS = ["aws_region"]
    OPTIONAL_PARAMS = ["aws_profile", "services"]
    
    async def execute(self, context, **kwargs):
        region = kwargs["aws_region"]
        profile = kwargs.get("aws_profile", "default")
        services = kwargs.get("services", ["ec2", "s3", "iam"])
        
        # Initialize AWS session
        session = boto3.Session(profile_name=profile, region_name=region)
        
        results = {}
        for service in services:
            results[service] = await self._scan_service(session, service)
        
        return {
            "status": "completed",
            "region": region,
            "services_scanned": services,
            "results": results
        }
    
    async def _scan_service(self, session, service_name):
        """Scan specific AWS service for security issues."""
        if service_name == "ec2":
            return await self._scan_ec2(session)
        elif service_name == "s3":
            return await self._scan_s3(session)
        elif service_name == "iam":
            return await self._scan_iam(session)
        else:
            return {"error": f"Unknown service: {service_name}"}
    
    async def _scan_ec2(self, session):
        """Scan EC2 instances for security issues."""
        ec2 = session.client('ec2')
        issues = []
        
        try:
            # Check for instances with public IPs
            response = ec2.describe_instances()
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    if instance.get('PublicIpAddress'):
                        issues.append({
                            "type": "public_instance",
                            "instance_id": instance['InstanceId'],
                            "severity": "medium",
                            "description": "Instance has public IP address"
                        })
            
            return {"issues": issues, "instances_checked": len(response['Reservations'])}
            
        except ClientError as e:
            return {"error": str(e)}
```

### Machine Learning Integration

```python
# ml_security_task.py
import numpy as np
from sklearn.ensemble import IsolationForest
from sentinelx.core.task import Task, register_task

@register_task("ml-anomaly-detection")
class MLAnomalyDetectionTask(Task):
    """Task that uses ML for security anomaly detection."""
    
    REQUIRED_PARAMS = ["log_data"]
    OPTIONAL_PARAMS = ["contamination", "model_type"]
    
    async def execute(self, context, **kwargs):
        log_data = kwargs["log_data"]
        contamination = kwargs.get("contamination", 0.1)
        model_type = kwargs.get("model_type", "isolation_forest")
        
        # Prepare data
        features = await self._extract_features(log_data)
        
        # Train model
        model = await self._train_model(features, model_type, contamination)
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(model, features)
        
        return {
            "status": "completed",
            "model_type": model_type,
            "features_extracted": len(features),
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies
        }
    
    async def _extract_features(self, log_data):
        """Extract features from log data."""
        # Feature extraction logic
        features = []
        
        for log_entry in log_data:
            feature_vector = [
                len(log_entry.get("message", "")),
                log_entry.get("response_time", 0),
                log_entry.get("status_code", 200),
                len(log_entry.get("user_agent", ""))
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    async def _train_model(self, features, model_type, contamination):
        """Train anomaly detection model."""
        if model_type == "isolation_forest":
            model = IsolationForest(contamination=contamination, random_state=42)
            model.fit(features)
            return model
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    async def _detect_anomalies(self, model, features):
        """Detect anomalies using trained model."""
        predictions = model.predict(features)
        anomaly_indices = np.where(predictions == -1)[0]
        
        anomalies = []
        for idx in anomaly_indices:
            anomalies.append({
                "index": int(idx),
                "feature_vector": features[idx].tolist(),
                "anomaly_score": float(model.decision_function([features[idx]])[0])
            })
        
        return anomalies
```

## Best Practices

### Task Development

1. **Use Clear Naming**: Choose descriptive task names that reflect functionality
2. **Document Parameters**: Always document required and optional parameters
3. **Validate Input**: Implement robust parameter validation
4. **Handle Errors Gracefully**: Use appropriate error handling and logging
5. **Return Consistent Formats**: Follow standard result format conventions
6. **Support Async Operations**: Use async/await for I/O operations
7. **Log Appropriately**: Use structured logging for debugging and monitoring

### Plugin Development

1. **Namespace Properly**: Use unique names to avoid conflicts
2. **Version Dependencies**: Specify compatible SentinelX versions
3. **Test Thoroughly**: Include comprehensive tests
4. **Document Usage**: Provide clear usage examples
5. **Follow Conventions**: Adhere to SentinelX coding standards

### Performance Optimization

1. **Use Async I/O**: Leverage asyncio for concurrent operations
2. **Cache Results**: Cache expensive computations when appropriate
3. **Optimize Imports**: Import only what you need
4. **Monitor Memory**: Be aware of memory usage in long-running tasks
5. **Profile Code**: Use profiling tools to identify bottlenecks

### Security Considerations

1. **Validate All Input**: Never trust external input
2. **Sanitize File Paths**: Prevent directory traversal attacks
3. **Handle Secrets Safely**: Use secure methods for API keys and credentials
4. **Implement Timeouts**: Prevent hanging operations
5. **Audit Dependencies**: Regularly check for security vulnerabilities

## API Reference

### Core Classes

#### Task
```python
class Task:
    """Base class for all SentinelX tasks."""
    
    REQUIRED_PARAMS: List[str] = []
    OPTIONAL_PARAMS: List[str] = []
    
    async def execute(self, context: Context, **kwargs) -> Dict[str, Any]:
        """Execute the task."""
        pass
    
    def validate_parameters(self, **kwargs) -> None:
        """Validate task parameters."""
        pass
```

#### Context
```python
class Context:
    """Execution context for tasks."""
    
    def __init__(self, config_data: Dict[str, Any] = None):
        """Initialize context."""
        pass
    
    @classmethod
    def load(cls, config_path: str = None) -> "Context":
        """Load context from configuration file."""
        pass
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        pass
```

#### PluginRegistry
```python
class PluginRegistry:
    """Registry for managing tasks and plugins."""
    
    @classmethod
    def register(cls, name: str, task_class: Type[Task]) -> None:
        """Register a task."""
        pass
    
    @classmethod
    def list_tasks(cls) -> List[str]:
        """List all registered tasks."""
        pass
    
    @classmethod
    def create(cls, name: str, ctx: Context, **kwargs) -> Task:
        """Create task instance."""
        pass
```

### Decorators

#### register_task
```python
def register_task(name: str):
    """Decorator to register a task."""
    def decorator(cls):
        PluginRegistry.register(name, cls)
        return cls
    return decorator
```

### Utility Functions

#### TaskError
```python
class TaskError(Exception):
    """Exception raised by tasks."""
    pass
```

---

This Developer Guide provides comprehensive information for extending SentinelX. For user documentation, see the [User Guide](USER_GUIDE.md).
