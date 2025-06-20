import abc
import asyncio
import datetime as dt
from typing import Any, Optional

class Task(metaclass=abc.ABCMeta):
    """Abstract base for all actionable units."""

    def __init__(self, *, ctx: "Context", **params: Any) -> None:
        self.ctx = ctx
        self.params = params
        self.started: Optional[dt.datetime] = None
        self.result: Any = None

    async def __call__(self) -> Any:
        self.started = dt.datetime.utcnow()
        await self.before()
        self.result = await self.run()
        await self.after()
        return self.result

    async def before(self) -> None:
        pass

    async def after(self) -> None:
        pass

    @abc.abstractmethod
    async def run(self) -> Any:
        """Run the task."""
        raise NotImplementedError
