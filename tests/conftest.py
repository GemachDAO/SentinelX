"""
Test fixtures and utilities for SentinelX tests.
"""
import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock

from sentinelx.core.context import Context
from sentinelx.core.task import Task
from sentinelx.core.registry import PluginRegistry


class MockTask(Task):
    """Mock task for testing purposes."""
    
    async def run(self) -> Dict[str, Any]:
        return {"status": "success", "params": self.params}


class FailingTask(Task):
    """Mock task that always fails for testing error handling."""
    
    async def run(self) -> Dict[str, Any]:
        raise Exception("Intentional test failure")


@pytest.fixture
def mock_context():
    """Create a mock context for testing."""
    config = {
        "network": {
            "retries": 3,
            "timeout": 30
        },
        "blockchain": {
            "rpc_urls": ["http://localhost:8545"]
        },
        "secrets": {
            "test_key": "test_value"
        }
    }
    return Context(config=config)


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    config_data = {
        "network": {
            "http_proxy": "http://proxy.example.com:8080",
            "retries": 5,
            "timeout": 60
        },
        "blockchain": {
            "rpc_urls": [
                "https://mainnet.infura.io/v3/test",
                "https://eth-mainnet.alchemyapi.io/v2/test"
            ],
            "default_chain": "ethereum"
        },
        "secrets": {
            "etherscan_api": "ENV:ETHERSCAN_API_KEY",
            "openai": "ENV:OPENAI_API_KEY"
        },
        "sandbox": {
            "enabled": True,
            "docker_enabled": False
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_file = Path(f.name)
    
    yield temp_file
    
    # Cleanup
    temp_file.unlink()


@pytest.fixture
def clean_registry():
    """Clean the plugin registry before and after tests."""
    # Clear registry before test
    PluginRegistry.clear()
    
    yield
    
    # Clear registry after test to avoid interference
    PluginRegistry.clear()


@pytest.fixture
def registered_mock_tasks(clean_registry):
    """Register mock tasks for testing."""
    PluginRegistry.register("mock-task", MockTask)
    PluginRegistry.register("failing-task", FailingTask)
    return ["mock-task", "failing-task"]


@pytest.fixture
def sample_task_params():
    """Sample parameters for task testing."""
    return {
        "target": "test.example.com",
        "timeout": 30,
        "verbose": True,
        "options": ["--scan-all", "--output-json"]
    }


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return Mock()


@pytest.fixture(autouse=True)
def setup_test_logging(caplog):
    """Setup logging for tests."""
    import logging
    logging.getLogger("sentinelx").setLevel(logging.DEBUG)
    yield
