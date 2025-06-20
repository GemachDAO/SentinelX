import abc
import asyncio
import datetime as dt
import logging
from typing import Any, Optional, Dict, Callable, TypeVar
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='Task')

def register_task(name: str) -> Callable[[type[T]], type[T]]:
    """Decorator to register a task class with the plugin registry."""
    def decorator(cls: type[T]) -> type[T]:
        # Import here to avoid circular imports
        from .registry import PluginRegistry
        PluginRegistry.register(name, cls)
        return cls
    return decorator

class TaskError(Exception):
    """Base exception for task-related errors."""
    pass

class TaskValidationError(TaskError):
    """Raised when task parameters are invalid."""
    pass

class TaskExecutionError(TaskError):
    """Raised when task execution fails."""
    pass

class Task(metaclass=abc.ABCMeta):
    """Abstract base for all actionable units."""

    def __init__(self, *, ctx: "Context", **params: Any) -> None:
        self.ctx = ctx
        self.params = params
        self.started: Optional[dt.datetime] = None
        self.finished: Optional[dt.datetime] = None
        self.result: Any = None
        self.error: Optional[Exception] = None
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    async def __call__(self) -> Any:
        """Execute the task with proper lifecycle management."""
        self.started = dt.datetime.utcnow()
        
        try:
            # Validate parameters before execution
            await self.validate_params()
            
            # Setup phase
            await self.before()
            
            # Main execution
            self.result = await self.run()
            
            # Cleanup phase
            await self.after()
            
            self.logger.info(f"Task completed successfully in {self.duration:.2f}s")
            
        except Exception as e:
            self.error = e
            self.logger.error(f"Task failed: {e}")
            await self.on_error(e)
            raise
        finally:
            self.finished = dt.datetime.utcnow()
            
        return self.result

    @property
    def duration(self) -> float:
        """Return task execution duration in seconds."""
        if self.started and self.finished:
            return (self.finished - self.started).total_seconds()
        elif self.started:
            return (dt.datetime.utcnow() - self.started).total_seconds()
        return 0.0

    @property
    def status(self) -> str:
        """Return current task status."""
        if self.error:
            return "failed"
        elif self.finished:
            return "completed"
        elif self.started:
            return "running"
        else:
            return "pending"

    async def validate_params(self) -> None:
        """Validate task parameters. Override in subclasses for custom validation."""
        required_params = getattr(self, 'REQUIRED_PARAMS', [])
        missing = [param for param in required_params if param not in self.params]
        if missing:
            raise TaskValidationError(f"Missing required parameters: {missing}")

    async def before(self) -> None:
        """Hook called before task execution. Override for setup logic."""
        pass

    async def after(self) -> None:
        """Hook called after successful task execution. Override for cleanup logic."""
        pass

    async def on_error(self, error: Exception) -> None:
        """Hook called when task execution fails. Override for error handling."""
        pass

    @abc.abstractmethod
    async def run(self) -> Any:
        """Run the task. Must be implemented by subclasses."""
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the task state."""
        return {
            'task_class': f"{self.__class__.__module__}.{self.__class__.__name__}",
            'params': self.params,
            'started': self.started.isoformat() if self.started else None,
            'finished': self.finished.isoformat() if self.finished else None,
            'duration': self.duration,
            'status': self.status,
            'result': self.result,
            'error': str(self.error) if self.error else None,
        }
