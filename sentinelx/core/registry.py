import importlib
import pkg_resources
import logging
from typing import Type, Dict, List, Optional
from .task import Task

logger = logging.getLogger(__name__)

class PluginRegistry:
    _tasks: Dict[str, Type[Task]] = {}
    _discovered: bool = False

    @classmethod
    def discover(cls, group: str = "sentinelx.tasks") -> None:
        """Discover and register tasks from entry points and built-in modules."""
        if cls._discovered:
            return
        
        # First, register built-in tasks
        cls._register_builtin_tasks()
        
        # Then discover from entry points
        try:
            for ep in pkg_resources.iter_entry_points(group=group):
                try:
                    mod = importlib.import_module(ep.module_name)
                    task_cls = getattr(mod, ep.attrs[0])
                    cls.register(ep.name, task_cls)
                    logger.info(f"Registered task '{ep.name}' from entry point")
                except Exception as e:
                    logger.warning(f"Failed to load task '{ep.name}': {e}")
        except Exception as e:
            logger.warning(f"Entry point discovery failed: {e}")
        
        cls._discovered = True
        logger.info(f"Task discovery completed. Registered tasks: {list(cls._tasks.keys())}")

    @classmethod
    def _register_builtin_tasks(cls) -> None:
        """Register built-in tasks from the sentinelx package."""
        builtin_tasks = [
            # Audit tasks
            ('slither', 'sentinelx.audit.smart_contract', 'SlitherScan'),
            ('cvss', 'sentinelx.audit.cvss', 'CVSSCalculator'), 
            ('web2-static', 'sentinelx.audit.web2_static', 'Web2Static'),
            
            # Exploit tasks
            ('autopwn', 'sentinelx.exploit.exploit_gen', 'AutoPwn'),
            ('binary-pwn', 'sentinelx.exploit.binary_pwn', 'BinaryExploit'),
            ('rop-exploit', 'sentinelx.exploit.rop_exploit', 'ROPExploit'),
            ('heap-exploit', 'sentinelx.exploit.heap_exploit', 'HeapExploit'),
            ('pwn-toolkit', 'sentinelx.exploit.pwn_toolkit', 'PwnToolkit'),
            ('fuzzer', 'sentinelx.exploit.fuzzing', 'Fuzzer'),
            ('shellcode', 'sentinelx.exploit.shellcode', 'ShellcodeGen'),
            
            # Red team tasks
            ('c2', 'sentinelx.redteam.c2', 'C2Server'),
            ('lateral-move', 'sentinelx.redteam.lateral_move', 'LateralMove'),
            ('social-eng', 'sentinelx.redteam.social_eng', 'SocialEngineering'),
            
            # Blockchain tasks
            ('chain-monitor', 'sentinelx.blockchain.monitor', 'ChainMonitor'),
            ('tx-replay', 'sentinelx.blockchain.replay', 'TxReplay'),
            ('rwa-scan', 'sentinelx.blockchain.rwascan', 'RwaScan'),
            
            # Forensics tasks
            ('memory-forensics', 'sentinelx.forensic.memory', 'MemoryForensics'),
            ('disk-forensics', 'sentinelx.forensic.disk', 'DiskForensics'),
            ('chain-ir', 'sentinelx.forensic.chain_ir', 'ChainIR'),
            
            # AI tasks
            ('llm-assist', 'sentinelx.ai.llm_assist', 'LLMAssist'),
            ('prompt-injection', 'sentinelx.ai.adversarial', 'PromptInjection'),
        ]
        
        for task_name, module_name, class_name in builtin_tasks:
            try:
                mod = importlib.import_module(module_name)
                task_cls = getattr(mod, class_name)
                cls.register(task_name, task_cls)
                logger.debug(f"Registered built-in task '{task_name}'")
            except Exception as e:
                logger.warning(f"Failed to register built-in task '{task_name}': {e}")

    @classmethod
    def register(cls, name: str, task_cls: Type[Task]) -> None:
        """Register a task class with the given name."""
        if not issubclass(task_cls, Task):
            raise ValueError(f"Task class {task_cls} must inherit from Task")
        
        if name in cls._tasks:
            logger.warning(f"Task '{name}' is already registered, overriding")
        
        cls._tasks[name] = task_cls
        logger.debug(f"Registered task '{name}' -> {task_cls}")

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a task by name."""
        if name in cls._tasks:
            del cls._tasks[name]
            logger.debug(f"Unregistered task '{name}'")

    @classmethod
    def create(cls, name: str, **kw) -> Task:
        """Create a task instance by name."""
        if name not in cls._tasks:
            available = ', '.join(sorted(cls._tasks.keys()))
            raise ValueError(f"Unknown task '{name}'. Available tasks: {available}")
        
        return cls._tasks[name](**kw)

    @classmethod
    def list_tasks(cls) -> List[str]:
        """Return a list of all registered task names."""
        return sorted(cls._tasks.keys())

    @classmethod
    def get_task_class(cls, name: str) -> Optional[Type[Task]]:
        """Get the task class for a given name."""
        return cls._tasks.get(name)

    @classmethod 
    def get_task(cls, name: str) -> Optional[Type[Task]]:
        """Get the task class for a given name (alias for get_task_class)."""
        return cls.get_task_class(name)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tasks (useful for testing)."""
        cls._tasks.clear()
        cls._discovered = False
