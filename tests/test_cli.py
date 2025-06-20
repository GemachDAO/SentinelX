"""
Integration tests for CLI functionality.
"""
import pytest
import tempfile
from pathlib import Path
from typer.testing import CliRunner
import yaml

from sentinelx.cli import app
from sentinelx.core.registry import PluginRegistry


class TestCLI:
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def sample_config(self):
        """Create sample configuration file."""
        config_data = {
            "network": {"retries": 2, "timeout": 15},
            "blockchain": {"rpc_urls": ["http://localhost:8545"]},
            "secrets": {"test_key": "test_value"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            return Path(f.name)
    
    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """Ensure tasks are discovered for CLI tests."""
        # Clear and rediscover tasks
        PluginRegistry.clear()
        PluginRegistry.discover()
    
    def test_cli_list_tasks(self, runner):
        """Test listing available tasks."""
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "Registered SentinelX Tasks" in result.stdout
        # Should show some built-in tasks
        assert "slither" in result.stdout or "cvss" in result.stdout
    
    def test_cli_version(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert "SentinelX" in result.stdout
        assert "version" in result.stdout
    
    def test_cli_task_info(self, runner):
        """Test getting task information."""
        result = runner.invoke(app, ["info", "cvss"])
        
        assert result.exit_code == 0
        assert "Task Information: cvss" in result.stdout
        assert "CVSSCalculator" in result.stdout
    
    def test_cli_task_info_unknown(self, runner):
        """Test getting info for unknown task."""
        result = runner.invoke(app, ["info", "nonexistent-task"])
        
        assert result.exit_code == 1
        assert "Task 'nonexistent-task' not found" in result.stdout
    
    def test_cli_run_task_basic(self, runner, sample_config):
        """Test running a basic task."""
        result = runner.invoke(app, [
            "run", "cvss",
            "--config", str(sample_config),
            "--params", '{"vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}'
        ])
        
        # Task should execute (even if it's just a placeholder)
        assert result.exit_code == 0
    
    def test_cli_run_task_invalid_params(self, runner, sample_config):
        """Test running task with invalid parameters."""
        result = runner.invoke(app, [
            "run", "cvss",
            "--config", str(sample_config),
            "--params", "invalid-json"
        ])
        
        assert result.exit_code == 1
        assert "Parameters must be a dictionary" in result.stdout
    
    def test_cli_run_unknown_task(self, runner, sample_config):
        """Test running unknown task."""
        result = runner.invoke(app, [
            "run", "nonexistent-task",
            "--config", str(sample_config),
            "--params", "{}"
        ])
        
        assert result.exit_code == 1
        assert "Unknown task" in result.stdout
    
    def test_cli_run_task_json_output(self, runner, sample_config):
        """Test task output in JSON format."""
        result = runner.invoke(app, [
            "run", "cvss",
            "--config", str(sample_config),
            "--params", '{"vector": "test"}',
            "--format", "json"
        ])
        
        assert result.exit_code == 0
        # Output should be valid JSON (contains braces)
        assert "{" in result.stdout and "}" in result.stdout
    
    def test_cli_verbose_mode(self, runner, sample_config):
        """Test verbose logging mode."""
        result = runner.invoke(app, [
            "run", "cvss",
            "--config", str(sample_config),
            "--params", '{"vector": "test"}',
            "--verbose"
        ])
        
        # Should complete successfully with verbose output
        assert result.exit_code == 0
    
    def test_cli_nonexistent_config(self, runner):
        """Test running with nonexistent config file."""
        result = runner.invoke(app, [
            "run", "cvss",
            "--config", "nonexistent.yaml",
            "--params", '{"vector": "test"}'
        ])
        
        # Should still work with default config
        assert result.exit_code == 0
    
    def teardown_method(self, method):
        """Clean up after each test."""
        # Clean up any temporary files
        import glob
        for temp_file in glob.glob("*.yaml"):
            try:
                Path(temp_file).unlink()
            except FileNotFoundError:
                pass
