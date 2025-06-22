#!/usr/bin/env python3
"""
Debug script to identify the task initialization issue.
"""

import sys
import traceback
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    try:
        print("🔍 SentinelX Task Initialization Debug")
        print("=" * 50)
        
        # Test basic imports
        print("\n1. Testing core imports...")
        from sentinelx.core.context import Context
        from sentinelx.core.registry import PluginRegistry
        from sentinelx.core.task import Task
        print("✅ Core imports successful")
        
        # Test context creation
        print("\n2. Testing context creation...")
        context = Context()
        print(f"✅ Context created: {type(context)}")
        print(f"   Context type: {type(context).__name__}")
        
        # Test task discovery
        print("\n3. Testing task discovery...")
        PluginRegistry.discover()
        tasks = PluginRegistry.list_tasks()
        print(f"✅ Found {len(tasks)} tasks")
        
        # Test creating a simple task class directly
        print("\n4. Testing direct task creation...")
        from sentinelx.audit.cvss import CVSSCalculator
        print(f"✅ Imported CVSSCalculator: {CVSSCalculator}")
        print(f"   CVSSCalculator MRO: {CVSSCalculator.__mro__}")
        
        # Try direct instantiation
        print("\n5. Testing direct task instantiation...")
        try:
            # This should work
            task_direct = CVSSCalculator(ctx=context, vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
            print(f"✅ Direct instantiation successful: {task_direct}")
        except Exception as e:
            print(f"❌ Direct instantiation failed: {e}")
            traceback.print_exc()
        
        # Test registry creation
        print("\n6. Testing registry task creation...")
        try:
            task_registry = PluginRegistry.create("cvss", ctx=context, vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
            print(f"✅ Registry creation successful: {task_registry}")
        except Exception as e:
            print(f"❌ Registry creation failed: {e}")
            traceback.print_exc()
            
        # Test a few different tasks
        print("\n7. Testing other task classes...")
        task_classes_to_test = [
            ("slither", "sentinelx.audit.smart_contract", "SlitherScan"),
            ("web2-static", "sentinelx.audit.web2_static", "Web2Static"),
            ("shellcode", "sentinelx.exploit.shellcode", "ShellcodeGen"),
        ]
        
        for task_name, module_name, class_name in task_classes_to_test:
            try:
                print(f"\n   Testing {task_name}...")
                import importlib
                mod = importlib.import_module(module_name)
                task_cls = getattr(mod, class_name)
                print(f"   ✅ Imported {class_name}: {task_cls}")
                print(f"   MRO: {task_cls.__mro__}")
                
                # Try direct instantiation
                task_instance = task_cls(ctx=context)
                print(f"   ✅ Direct instantiation successful")
                
                # Try registry creation
                if task_name in tasks:
                    registry_instance = PluginRegistry.create(task_name, ctx=context)
                    print(f"   ✅ Registry creation successful")
                else:
                    print(f"   ⚠️ Task {task_name} not found in registry")
                    
            except Exception as e:
                print(f"   ❌ Failed {task_name}: {e}")
                traceback.print_exc()
        
        print("\n" + "=" * 50)
        print("🎉 Debug completed!")
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
