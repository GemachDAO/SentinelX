"""
Tests for the Task base class and task execution.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from sentinelx.core.task import Task, TaskError, TaskValidationError, TaskExecutionError, register_task
from sentinelx.core.context import Context


class TestTask:
    
    class SampleTask(Task):
        """Sample task for testing."""
        REQUIRED_PARAMS = ["target"]
        
        async def run(self):
            return {"result": f"processed {self.params.get('target')}"}
    
    class FailingTask(Task):
        """Task that always fails."""
        
        async def run(self):
            raise Exception("Task execution failed")
    
    class SlowTask(Task):
        """Task that takes time to complete."""
        
        async def run(self):
            await asyncio.sleep(0.1)
            return {"status": "completed"}
    
    @pytest.fixture
    def sample_task(self, mock_context):
        """Create a sample task instance."""
        return self.SampleTask(ctx=mock_context, target="test.example.com")
    
    def test_task_initialization(self, mock_context):
        """Test task initialization."""
        params = {"target": "example.com", "verbose": True}
        task = self.SampleTask(ctx=mock_context, **params)
        
        assert task.ctx == mock_context
        assert task.params == params
        assert task.started is None
        assert task.finished is None
        assert task.result is None
        assert task.error is None
        assert task.status == "pending"
    
    @pytest.mark.asyncio
    async def test_successful_task_execution(self, sample_task):
        """Test successful task execution."""
        result = await sample_task()
        
        assert result == {"result": "processed test.example.com"}
        assert sample_task.result == result
        assert sample_task.started is not None
        assert sample_task.finished is not None
        assert sample_task.error is None
        assert sample_task.status == "completed"
        assert sample_task.duration > 0
    
    @pytest.mark.asyncio
    async def test_task_execution_failure(self, mock_context):
        """Test task execution failure handling."""
        task = self.FailingTask(ctx=mock_context)
        
        with pytest.raises(Exception, match="Task execution failed"):
            await task()
        
        assert task.started is not None
        assert task.finished is not None
        assert task.error is not None
        assert task.status == "failed"
        assert task.result is None
    
    @pytest.mark.asyncio
    async def test_task_parameter_validation(self, mock_context):
        """Test task parameter validation."""
        # Task with missing required parameter
        task = self.SampleTask(ctx=mock_context)  # Missing 'target'
        
        with pytest.raises(TaskValidationError, match="Missing required parameters"):
            await task()
    
    @pytest.mark.asyncio
    async def test_task_lifecycle_hooks(self, mock_context):
        """Test task lifecycle hooks are called."""
        
        class HookedTask(Task):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.before_called = False
                self.after_called = False
                self.error_called = False
            
            async def before(self):
                self.before_called = True
            
            async def after(self):
                self.after_called = True
            
            async def on_error(self, error):
                self.error_called = True
            
            async def run(self):
                return {"status": "success"}
        
        task = HookedTask(ctx=mock_context)
        await task()
        
        assert task.before_called
        assert task.after_called
        assert not task.error_called
    
    @pytest.mark.asyncio
    async def test_task_error_hook(self, mock_context):
        """Test error hook is called on failure."""
        
        class ErrorHookedTask(Task):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.error_called = False
                self.error_received = None
            
            async def on_error(self, error):
                self.error_called = True
                self.error_received = error
            
            async def run(self):
                raise ValueError("Test error")
        
        task = ErrorHookedTask(ctx=mock_context)
        
        with pytest.raises(ValueError):
            await task()
        
        assert task.error_called
        assert isinstance(task.error_received, ValueError)
    
    def test_task_duration_calculation(self, mock_context):
        """Test task duration calculation."""
        task = self.SampleTask(ctx=mock_context, target="test")
        
        # Before execution
        assert task.duration == 0.0
        
        # Mock started time
        task.started = datetime.utcnow()
        duration_running = task.duration
        assert duration_running > 0
        
        # Mock finished time
        import time
        time.sleep(0.01)  # Small delay
        task.finished = datetime.utcnow()
        duration_completed = task.duration
        assert duration_completed > duration_running
    
    def test_task_to_dict(self, sample_task):
        """Test task dictionary representation."""
        task_dict = sample_task.to_dict()
        
        expected_keys = {
            'task_class', 'params', 'started', 'finished',
            'duration', 'status', 'result', 'error'
        }
        assert set(task_dict.keys()) == expected_keys
        assert task_dict['status'] == 'pending'
        assert task_dict['params'] == {'target': 'test.example.com'}
    
    @pytest.mark.asyncio
    async def test_task_timing(self, mock_context):
        """Test task execution timing."""
        task = self.SlowTask(ctx=mock_context)
        
        start_time = datetime.utcnow()
        await task()
        end_time = datetime.utcnow()
        
        # Task should have taken at least 0.1 seconds
        assert task.duration >= 0.1
        # Task timing should be consistent with actual execution time
        actual_duration = (end_time - start_time).total_seconds()
        assert abs(task.duration - actual_duration) < 0.05  # 50ms tolerance


class TestTaskRegistration:
    
    def test_register_task_decorator(self):
        """Test the register_task decorator."""
        from sentinelx.core.registry import PluginRegistry
        
        # Clear registry first
        PluginRegistry.clear()
        
        @register_task("test-decorated-task")
        class DecoratedTask(Task):
            async def run(self):
                return {"decorated": True}
        
        # Task should be registered
        assert "test-decorated-task" in PluginRegistry._tasks
        assert PluginRegistry._tasks["test-decorated-task"] == DecoratedTask
    
    def test_task_logging(self, mock_context, caplog):
        """Test task logging functionality."""
        
        class LoggingTask(Task):
            async def run(self):
                self.logger.info("Task is running")
                return {"logged": True}
        
        task = LoggingTask(ctx=mock_context)
        
        # Task logger should be properly configured
        assert task.logger.name.endswith("LoggingTask")
    
    @pytest.mark.asyncio
    async def test_task_with_complex_validation(self, mock_context):
        """Test task with complex parameter validation."""
        
        class ComplexValidationTask(Task):
            REQUIRED_PARAMS = ["url", "method"]
            
            async def validate_params(self):
                await super().validate_params()
                
                # Custom validation
                if self.params.get("method") not in ["GET", "POST", "PUT"]:
                    raise TaskValidationError("Invalid HTTP method")
                
                if not self.params.get("url", "").startswith("http"):
                    raise TaskValidationError("URL must start with http")
            
            async def run(self):
                return {"validated": True}
        
        # Valid params
        task = ComplexValidationTask(
            ctx=mock_context,
            url="https://example.com",
            method="GET"
        )
        result = await task()
        assert result["validated"] is True
        
        # Invalid method
        task = ComplexValidationTask(
            ctx=mock_context,
            url="https://example.com",
            method="INVALID"
        )
        with pytest.raises(TaskValidationError, match="Invalid HTTP method"):
            await task()
        
        # Invalid URL
        task = ComplexValidationTask(
            ctx=mock_context,
            url="ftp://example.com",
            method="GET"
        )
        with pytest.raises(TaskValidationError, match="URL must start with http"):
            await task()
