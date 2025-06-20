from __future__ import annotations
import json
from datetime import datetime
from typing import Any


def audit_log(message: str, **data: Any) -> None:
    entry = {"ts": datetime.utcnow().isoformat(), "msg": message, **data}
    print(json.dumps(entry))
