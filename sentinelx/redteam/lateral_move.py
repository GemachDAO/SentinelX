from __future__ import annotations
from ..core.task import Task

class LateralMove(Task):
    async def run(self):
        host = self.params.get("host")
        return {"moved_to": host}
