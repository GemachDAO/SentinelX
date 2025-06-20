from __future__ import annotations
from ..core.task import Task

class DiskForensics(Task):
    async def run(self):
        image = self.params.get("image")
        return {"disk_image": image}
