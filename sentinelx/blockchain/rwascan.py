from __future__ import annotations
from ..core.task import Task

class RwaScan(Task):
    async def run(self):
        address = self.params.get("address")
        return {"scanned": address}
