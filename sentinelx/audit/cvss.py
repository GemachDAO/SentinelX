from __future__ import annotations
from ..core.task import Task

class CVSSCalculator(Task):
    async def run(self):
        vector = self.params.get("vector")
        return {"vector": vector, "score": 0.0}
