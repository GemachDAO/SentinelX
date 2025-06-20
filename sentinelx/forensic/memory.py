from __future__ import annotations
from ..core.task import Task

class MemoryForensics(Task):
    async def run(self):
        dump = self.params.get("dump")
        return {"memory_dump": dump}
