from __future__ import annotations
from ..core.task import Task

class Web2Static(Task):
    async def run(self):
        target = self.params.get("target")
        return {"target": target, "result": "static analysis placeholder"}
