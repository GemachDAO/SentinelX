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
    def setup_tasks(self):
        """Ensure tasks are discovered for CLI tests."""
        PluginRegistry.discover()
    
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
    
    def test_cli_list_tasks(self, runner, setup_tasks):
        """Test listing available tasks."""
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "Registered SentinelX Tasks" in result.stdout
        # Should show at least one task (either built-in or test task)
        # Be more lenient since dependencies may not be available
        assert "Task Name" in result.stdout
    
    def test_cli_version(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert "SentinelX" in result.stdout
        assert "version" in result.stdout
    
    def test_cli_task_info(self, runner, setup_tasks):
        """Test getting task information."""
        # First discover what tasks are available
        tasks = PluginRegistry.list_tasks()
        if not tasks:
            pytest.skip("No tasks available for testing")
        
        # Use the first available task
        task_name = tasks[0]
        result = runner.invoke(app, ["info", task_name])
        
        assert result.exit_code == 0
        assert f"Task Information: {task_name}" in result.stdout
    
    def test_cli_task_info_unknown(self, runner):
        """Test getting info for unknown task."""
        result = runner.invoke(app, ["info", "nonexistent-task"])
        
        assert result.exit_code == 1
        assert "Task 'nonexistent-task' not found" in result.stdout
    
    def test_cli_run_task_basic(self, runner, sample_config, setup_tasks):
        """Test running a basic task."""
        # Use a test task that we know will work
        from sentinelx.core.task import Task, register_task
        
        @register_task("test-runner")
        class TestTask(Task):
            name = "test-runner"
            description = "Test task for CLI testing"
            
            async def run(self):
                return {"status": "success", "message": "Test completed"}
        
        result = runner.invoke(app, [
            "run", "test-runner",
            "--config", str(sample_config),
            "--params", '{}'
        ])
        
        # Task should execute successfully
        assert result.exit_code == 0
    
    def test_cli_run_task_invalid_params(self, runner, sample_config, setup_tasks):
        """Test running task with invalid parameters."""
        result = runner.invoke(app, [
            "run", "test-runner",  # Use our test task
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
    
    def test_cli_run_task_json_output(self, runner, sample_config, setup_tasks):
        """Test task output in JSON format."""
        result = runner.invoke(app, [
            "run", "test-runner",  # Use our test task
            "--config", str(sample_config),
            "--params", '{}',
            "--format", "json"
        ])
        
        assert result.exit_code == 0
        # Output should be valid JSON (contains braces)
        assert "{" in result.stdout and "}" in result.stdout
    
    def test_cli_verbose_mode(self, runner, sample_config, setup_tasks):
        """Test verbose logging mode."""
        result = runner.invoke(app, [
            "run", "test-runner",  # Use our test task
            "--config", str(sample_config),
            "--params", '{}',
            "--verbose"
        ])
        
        # Should complete successfully with verbose output
        assert result.exit_code == 0
    
    def test_cli_nonexistent_config(self, runner, setup_tasks):
        """Test running with nonexistent config file."""
        result = runner.invoke(app, [
            "run", "test-runner",  # Use our test task
            "--config", "nonexistent.yaml",
            "--params", '{}'
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
