# Contributing to SentinelX

Thank you for your interest in contributing to SentinelX! This guide will help you get started with contributing to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Contribution Guidelines](#contribution-guidelines)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Submitting Changes](#submitting-changes)
8. [Community](#community)

## Getting Started

### Ways to Contribute

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Implement new features or fix bugs
- **Documentation**: Improve or expand documentation
- **Security Tasks**: Add new security analysis capabilities
- **Testing**: Improve test coverage and quality
- **Examples**: Create tutorials and examples

### Before You Start

1. **Check existing issues** to see if your idea/bug is already being worked on
2. **Read the documentation** to understand the project structure
3. **Join our community** to discuss your contribution ideas
4. **Review the code of conduct** to understand our standards

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)
- Virtual environment tools (venv, conda, etc.)

### Setup Instructions

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/sentinelx.git
   cd sentinelx
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode
   pip install -e ".[dev]"
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Verify installation**
   ```bash
   # Run tests
   pytest
   
   # Check code formatting
   black --check .
   flake8 .
   
   # Run CLI
   sentinelx --help
   ```

4. **Set up pre-commit hooks** (recommended)
   ```bash
   pre-commit install
   ```

### Development Dependencies

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=2.17.0
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
```

## Contribution Guidelines

### Issue Reporting

When reporting bugs or requesting features:

1. **Use descriptive titles**
2. **Provide detailed descriptions**
3. **Include reproduction steps** for bugs
4. **Add relevant labels** (bug, enhancement, documentation, etc.)
5. **Include environment information** (Python version, OS, etc.)

#### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command: `sentinelx run task-name -p "..."`
2. See error

**Expected Behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- SentinelX Version: [e.g., 1.0.0]

**Additional Context**
Add any other context about the problem here.
```

#### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the problem this feature would solve.

**Proposed Solution**
If you have ideas for implementation, describe them here.

**Alternatives Considered**
Any alternative solutions you've considered.

**Additional Context**
Any other context or screenshots about the feature request.
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the code standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run full test suite
   pytest
   
   # Check code coverage
   pytest --cov=sentinelx
   
   # Run linting
   black .
   flake8 .
   mypy .
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new security task for XYZ analysis"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Standards

### Coding Style

We follow PEP 8 with some specific guidelines:

- **Line length**: 88 characters (Black default)
- **Imports**: Use absolute imports, group by standard library, third-party, local
- **Type hints**: Required for all public functions and methods
- **Docstrings**: Required for all public classes and functions (Google style)

### Code Formatting

We use automated code formatting tools:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type check with mypy
mypy .
```

### Example Code Style

```python
"""
Module docstring describing the purpose of this module.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from sentinelx.core.task import Task, register_task
from sentinelx.core.context import Context


logger = logging.getLogger(__name__)


@register_task("example-task")
class ExampleTask(Task):
    """
    Example security task following SentinelX coding standards.
    
    This task demonstrates proper code structure, documentation,
    and type hints for SentinelX security tasks.
    
    Attributes:
        REQUIRED_PARAMS: List of required parameter names
        OPTIONAL_PARAMS: List of optional parameter names
    """
    
    REQUIRED_PARAMS = ["target"]
    OPTIONAL_PARAMS = ["timeout", "verbose"]
    
    def __init__(self, **kwargs) -> None:
        """Initialize the example task."""
        super().__init__(**kwargs)
        self._results_cache: Dict[str, Any] = {}
    
    async def execute(self, context: Context, **kwargs) -> Dict[str, Any]:
        """
        Execute the example security task.
        
        Args:
            context: Execution context with configuration
            **kwargs: Task parameters including:
                - target: Target to analyze (required)
                - timeout: Analysis timeout in seconds (optional)
                - verbose: Enable verbose output (optional)
        
        Returns:
            Dictionary containing analysis results with keys:
            - status: Task execution status
            - target: Analyzed target
            - results: Analysis findings
            - metadata: Task metadata
        
        Raises:
            ValidationError: If required parameters are missing
            TaskError: If task execution fails
        """
        target = kwargs["target"]
        timeout = kwargs.get("timeout", 300)
        verbose = kwargs.get("verbose", False)
        
        logger.info(f"Starting analysis of target: {target}")
        
        try:
            # Perform analysis
            analysis_results = await self._perform_analysis(
                target=target,
                timeout=timeout,
                verbose=verbose
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis_results)
            
            return {
                "status": "completed",
                "target": target,
                "results": analysis_results,
                "recommendations": recommendations,
                "metadata": {
                    "task_version": "1.0.0",
                    "analysis_duration": analysis_results.get("duration", 0),
                    "timestamp": context.get_timestamp(),
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for {target}: {e}")
            raise
    
    async def _perform_analysis(
        self,
        target: str,
        timeout: int,
        verbose: bool
    ) -> Dict[str, Any]:
        """
        Perform the actual security analysis.
        
        Args:
            target: Target to analyze
            timeout: Analysis timeout
            verbose: Verbose output flag
            
        Returns:
            Analysis results dictionary
        """
        # Implementation here
        return {"findings": [], "duration": 0}
    
    def _generate_recommendations(
        self,
        analysis_results: Dict[str, Any]
    ) -> List[str]:
        """
        Generate security recommendations based on analysis results.
        
        Args:
            analysis_results: Results from security analysis
            
        Returns:
            List of security recommendations
        """
        recommendations = []
        
        findings = analysis_results.get("findings", [])
        if not findings:
            recommendations.append("✅ No security issues detected")
        else:
            recommendations.append(f"⚠️ Found {len(findings)} security issues")
            
        return recommendations
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_core/          # Core module tests
│   ├── test_tasks/         # Task-specific tests
│   └── test_cli/           # CLI tests
├── integration/            # Integration tests
│   ├── test_workflows/     # Workflow tests
│   └── test_docker/        # Docker integration tests
└── fixtures/               # Test data and fixtures
    ├── contracts/          # Sample contracts for testing
    └── configurations/     # Test configurations
```

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_tasks/test_example_task.py
import pytest
from unittest.mock import Mock, AsyncMock

from sentinelx.core.context import Context
from sentinelx.core.task import ValidationError
from sentinelx.tasks.example_task import ExampleTask


class TestExampleTask:
    """Test cases for ExampleTask."""
    
    @pytest.fixture
    def context(self):
        """Create test context."""
        return Context(config={"debug": True})
    
    @pytest.fixture
    def task(self):
        """Create test task instance."""
        return ExampleTask()
    
    @pytest.mark.asyncio
    async def test_execute_success(self, task, context):
        """Test successful task execution."""
        result = await task.execute(
            context,
            target="test-target",
            timeout=60
        )
        
        assert result["status"] == "completed"
        assert result["target"] == "test-target"
        assert "results" in result
        assert "metadata" in result
    
    @pytest.mark.asyncio
    async def test_execute_missing_required_param(self, task, context):
        """Test task execution with missing required parameter."""
        with pytest.raises(ValidationError):
            await task.execute(context)
    
    def test_generate_recommendations(self, task):
        """Test recommendation generation."""
        analysis_results = {"findings": [{"type": "vulnerability", "severity": "high"}]}
        recommendations = task._generate_recommendations(analysis_results)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("security issues" in rec for rec in recommendations)
```

#### Integration Tests

```python
# tests/integration/test_task_execution.py
import pytest
from pathlib import Path

from sentinelx.core.context import Context
from sentinelx.core.registry import PluginRegistry


class TestTaskExecution:
    """Integration tests for task execution."""
    
    @pytest.fixture(scope="session")
    def sample_contract(self, tmp_path_factory):
        """Create sample contract for testing."""
        contract_dir = tmp_path_factory.mktemp("contracts")
        contract_file = contract_dir / "Sample.sol"
        contract_file.write_text("""
        pragma solidity ^0.8.0;
        contract Sample {
            uint256 public value;
            function setValue(uint256 _value) public {
                value = _value;
            }
        }
        """)
        return str(contract_file)
    
    @pytest.mark.asyncio
    async def test_slither_task_execution(self, sample_contract):
        """Test Slither task execution end-to-end."""
        context = Context.load("config.yaml")
        
        task = PluginRegistry.create(
            "slither",
            contract_path=sample_contract
        )
        
        result = await task.execute(context)
        
        assert result["status"] in ["completed", "failed"]
        if result["status"] == "completed":
            assert "results" in result
            assert "vulnerabilities" in result["results"]
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_tasks/test_example_task.py

# Run with coverage
pytest --cov=sentinelx --cov-report=html

# Run only fast tests (exclude slow integration tests)
pytest -m "not slow"

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Test Configuration

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path

from sentinelx.core.context import Context


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_context(temp_dir):
    """Create test context."""
    config = {
        "working_dir": str(temp_dir),
        "debug": True,
        "timeout": 60
    }
    return Context(config=config)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "sentinelx": {
            "debug": True,
            "timeout": 300,
            "docker": {"enabled": False}
        }
    }


# Mark slow tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
```

## Documentation

### Documentation Standards

- **API Documentation**: Use Google-style docstrings
- **User Documentation**: Write clear, example-driven guides
- **Code Comments**: Explain complex logic, not obvious code
- **README Updates**: Keep installation and usage instructions current

### Building Documentation

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build HTML documentation
cd docs
make html

# Build PDF documentation
make latexpdf

# Serve documentation locally
python -m http.server 8000 -d _build/html
```

### Documentation Structure

```
docs/
├── index.rst               # Main documentation index
├── user_guide/            # User documentation
├── developer_guide/       # Developer documentation  
├── api_reference/         # API documentation
├── examples/              # Example code and tutorials
├── _static/               # Static assets (images, CSS)
├── _templates/            # Custom templates
└── conf.py               # Sphinx configuration
```

## Submitting Changes

### Commit Message Format

We follow conventional commits:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(tasks): add new malware analysis task
fix(cli): resolve parameter parsing issue
docs(api): update API reference for new features
test(core): add unit tests for task registry
```

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows the project style guidelines
- [ ] All tests pass (`pytest`)
- [ ] Code coverage is maintained or improved
- [ ] Documentation is updated if needed
- [ ] Commit messages follow conventional format
- [ ] Pull request has a clear description
- [ ] Related issues are referenced
- [ ] Changes are backwards compatible (or breaking changes are documented)

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: Project maintainers review the code
3. **Discussion**: Address feedback and questions
4. **Approval**: Once approved, changes are merged
5. **Release**: Changes are included in the next release

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Discord**: Real-time chat and support (link in README)
- **Email**: security@sentinelx.org for security-related issues

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Major contributions highlighted
- **Documentation**: Contributor attribution where appropriate

## Getting Help

If you need help with contributing:

1. **Check the documentation** for answers to common questions
2. **Search existing issues** for similar problems
3. **Ask in GitHub Discussions** for general questions
4. **Open an issue** for specific bugs or feature requests
5. **Join our Discord** for real-time help

Thank you for contributing to SentinelX! Your contributions help make security analysis more accessible and effective for everyone.
