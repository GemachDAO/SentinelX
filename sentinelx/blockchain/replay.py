from __future__ import annotations
from ..core.task import Task

class TxReplay(Task):
    async def run(self):
        tx_hash = self.params.get("tx_hash")
        return {"replayed": tx_hash}
