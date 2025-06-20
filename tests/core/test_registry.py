"""
Tests for the PluginRegistry and task discovery system.
"""
import pytest
from unittest.mock import Mock, patch
import importlib

from sentinelx.core.registry import PluginRegistry
from sentinelx.core.task import Task


class TestPluginRegistry:
    
    class MockTask(Task):
        """Mock task for testing."""
        async def run(self):
            return {"mock": True}
    
    class AnotherTask(Task):
        """Another mock task for testing."""
        async def run(self):
            return {"another": True}
    
    def test_register_task(self, clean_registry):
        """Test task registration."""
        PluginRegistry.register("test-task", self.MockTask)
        
        assert "test-task" in PluginRegistry._tasks
        assert PluginRegistry._tasks["test-task"] == self.MockTask
    
    def test_register_invalid_task_class(self, clean_registry):
        """Test registering invalid task class raises error."""
        class NotATask:
            pass
        
        with pytest.raises(ValueError, match="must inherit from Task"):
            PluginRegistry.register("invalid", NotATask)
    
    def test_register_duplicate_task_warning(self, clean_registry, caplog):
        """Test warning when registering duplicate task names."""
        PluginRegistry.register("duplicate-task", self.MockTask)
        PluginRegistry.register("duplicate-task", self.AnotherTask)
        
        assert "already registered, overriding" in caplog.text
        # Should have the second task
        assert PluginRegistry._tasks["duplicate-task"] == self.AnotherTask
    
    def test_unregister_task(self, clean_registry):
        """Test task unregistration."""
        PluginRegistry.register("temp-task", self.MockTask)
        assert "temp-task" in PluginRegistry._tasks
        
        PluginRegistry.unregister("temp-task")
        assert "temp-task" not in PluginRegistry._tasks
    
    def test_create_task(self, clean_registry, mock_context):
        """Test task creation."""
        PluginRegistry.register("create-test", self.MockTask)
        
        task = PluginRegistry.create("create-test", ctx=mock_context, param1="value1")
        
        assert isinstance(task, self.MockTask)
        assert task.ctx == mock_context
        assert task.params == {"param1": "value1"}
    
    def test_create_unknown_task(self, clean_registry):
        """Test creating unknown task raises error."""
        with pytest.raises(ValueError, match="Unknown task 'nonexistent'"):
            PluginRegistry.create("nonexistent")
    
    def test_list_tasks(self, clean_registry):
        """Test listing registered tasks."""
        assert PluginRegistry.list_tasks() == []
        
        PluginRegistry.register("task-a", self.MockTask)
        PluginRegistry.register("task-b", self.AnotherTask)
        
        tasks = PluginRegistry.list_tasks()
        assert sorted(tasks) == ["task-a", "task-b"]
    
    def test_get_task_class(self, clean_registry):
        """Test getting task class by name."""
        PluginRegistry.register("get-test", self.MockTask)
        
        task_cls = PluginRegistry.get_task_class("get-test")
        assert task_cls == self.MockTask
        
        unknown_cls = PluginRegistry.get_task_class("unknown")
        assert unknown_cls is None
    
    def test_clear_registry(self, clean_registry):
        """Test clearing the registry."""
        PluginRegistry.register("clear-test", self.MockTask)
        assert len(PluginRegistry._tasks) > 0
        
        PluginRegistry.clear()
        assert len(PluginRegistry._tasks) == 0
        assert not PluginRegistry._discovered

    def test_builtin_task_registration(self, clean_registry):
        """Test that built-in tasks are registered on discovery."""
        # Discovery should register built-in tasks
        PluginRegistry.discover()

        # Check that some built-in tasks are registered
        tasks = PluginRegistry.list_tasks()
        # Only check for tasks that should work without external dependencies
        expected_tasks = [
            "slither", "cvss", "fuzzer", "c2",
            "chain-monitor", "memory-forensics", "llm-assist"
        ]

        for task in expected_tasks:
            assert task in tasks, f"Built-in task '{task}' not registered"
    
    def test_discovery_idempotent(self, clean_registry):
        """Test that discovery can be called multiple times safely."""
        PluginRegistry.discover()
        initial_tasks = set(PluginRegistry.list_tasks())
        
        PluginRegistry.discover()  # Call again
        second_tasks = set(PluginRegistry.list_tasks())
        
        assert initial_tasks == second_tasks
        assert PluginRegistry._discovered is True
    
    @patch('pkg_resources.iter_entry_points')
    def test_entry_point_discovery(self, mock_iter_entry_points, clean_registry):
        """Test discovery from entry points."""
        # Mock entry point
        mock_entry_point = Mock()
        mock_entry_point.name = "external-task"
        mock_entry_point.module_name = "external.module"
        mock_entry_point.attrs = ["ExternalTask"]
        
        mock_iter_entry_points.return_value = [mock_entry_point]
        
        # Mock module and task class
        mock_module = Mock()
        mock_module.ExternalTask = self.MockTask
        
        with patch('importlib.import_module', return_value=mock_module):
            PluginRegistry.discover()
        
        # External task should be registered
        assert "external-task" in PluginRegistry.list_tasks()
        assert PluginRegistry.get_task_class("external-task") == self.MockTask
    
    @patch('pkg_resources.iter_entry_points')
    def test_entry_point_discovery_failure(self, mock_iter_entry_points, clean_registry, caplog):
        """Test handling of entry point discovery failures."""
        # Mock failing entry point
        mock_entry_point = Mock()
        mock_entry_point.name = "failing-task"
        mock_entry_point.module_name = "nonexistent.module"
        mock_entry_point.attrs = ["NonexistentTask"]
        
        mock_iter_entry_points.return_value = [mock_entry_point]
        
        # Import will fail
        with patch('importlib.import_module', side_effect=ImportError("Module not found")):
            PluginRegistry.discover()
        
        # Should log warning and continue
        assert "Failed to load task 'failing-task'" in caplog.text
        assert "failing-task" not in PluginRegistry.list_tasks()
    
    def test_builtin_task_loading_failure(self, clean_registry, caplog):
        """Test handling of built-in task loading failures."""
        # Mock a failing import for one of the built-in tasks
        with patch('importlib.import_module') as mock_import:
            def side_effect(module_name):
                if "smart_contract" in module_name:
                    raise ImportError("Slither not available")
                # Return a mock module for other imports
                mock_module = Mock()
                # Set up mock attributes for various task classes
                for attr in ['CVSSCalculator', 'Web2Static', 'AutoPwn', 'Fuzzer', 
                           'ShellcodeGen', 'C2Server', 'LateralMove', 'SocialEngineering',
                           'ChainMonitor', 'TxReplay', 'RwaScan', 'MemoryForensics',
                           'DiskForensics', 'ChainIR', 'LLMAssist', 'PromptInjection']:
                    setattr(mock_module, attr, self.MockTask)
                return mock_module
            
            mock_import.side_effect = side_effect
            PluginRegistry.discover()
        
        # Should log warning for failed task
        assert "Failed to register built-in task 'slither'" in caplog.text
        # But other tasks should still be registered
        assert len(PluginRegistry.list_tasks()) > 0
