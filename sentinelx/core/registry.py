import importlib
import pkg_resources
from typing import Type, Dict
from .task import Task

class PluginRegistry:
    _tasks: Dict[str, Type[Task]] = {}

    @classmethod
    def discover(cls, group: str = "sentinelx.tasks") -> None:
        for ep in pkg_resources.iter_entry_points(group=group):
            mod = importlib.import_module(ep.module_name)
            cls.register(ep.name, getattr(mod, ep.attrs[0]))

    @classmethod
    def register(cls, name: str, task_cls: Type[Task]) -> None:
        cls._tasks[name] = task_cls

    @classmethod
    def create(cls, name: str, **kw) -> Task:
        return cls._tasks[name](**kw)
