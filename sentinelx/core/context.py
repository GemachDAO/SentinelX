from __future__ import annotations
import os
import yaml
from pydantic import BaseModel
from typing import Any, Dict

class Context(BaseModel):
    config: Dict[str, Any] = {}

    @classmethod
    def load(cls, path: str = "config.yaml") -> "Context":
        if not os.path.exists(path):
            data: Dict[str, Any] = {}
        else:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
        def resolve(value: Any) -> Any:
            if isinstance(value, str) and value.startswith("ENV:"):
                return os.getenv(value[4:], "")
            if isinstance(value, dict):
                return {k: resolve(v) for k, v in value.items()}
            if isinstance(value, list):
                return [resolve(v) for v in value]
            return value
        resolved = resolve(data)
        return cls(config=resolved)

    def sandbox(self, docker: bool = False, seccomp: str | None = None) -> None:
        """Placeholder for sandboxing helpers."""
        pass
