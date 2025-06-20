from __future__ import annotations
from ..core.task import Task

class LLMAssist(Task):
    async def run(self):
        prompt = self.params.get("prompt")
        return {"response": f"Processed {prompt}"}
