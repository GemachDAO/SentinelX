from __future__ import annotations
from ..core.task import Task

class ChainIR(Task):
    async def run(self):
        address = self.params.get("address")
        return {"incident_address": address}
