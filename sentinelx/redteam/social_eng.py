from __future__ import annotations
from ..core.task import Task

class SocialEngineering(Task):
    async def run(self):
        target = self.params.get("target")
        return {"phished": target}
