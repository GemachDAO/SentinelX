from __future__ import annotations
from ..core.task import Task

class ChainMonitor(Task):
    async def run(self):
        network = self.params.get("network")
        return {"monitoring": network}
