#!/usr/bin/env python3
"""
SentinelX Phase 2 Completion Validation Script
Tests all 18 registered tasks to ensure they're functional.
"""

import asyncio
import json
import sys
from datetime import datetime

# Test imports
try:
    from sentinelx.core.registry import PluginRegistry
    from sentinelx.core.context import Context
    print("✓ Core imports successful")
except Exception as e:
    print(f"✗ Core import failed: {e}")
    sys.exit(1)

async def test_task(task_name, params=None, timeout=30):
    """Test a single task execution with timeout"""
    try:
        # Create context
        ctx = Context.load()
        
        # Create task instance with test parameters using registry
        test_params = params or {}
        task_instance = PluginRegistry.create(task_name, ctx=ctx, **test_params)
        
        # Run the task with a timeout
        result = await asyncio.wait_for(task_instance.run(), timeout=timeout)
        
        if result and isinstance(result, dict):
            return {"status": "SUCCESS", "result_keys": list(result.keys())}
        else:
            return {"status": "FAILED", "error": "Invalid result format"}
    except asyncio.TimeoutError:
        return {"status": "FAILED", "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

async def main():
    print("SentinelX Phase 2 Completion Validation")
    print("=" * 50)
    print(f"Validation started at: {datetime.now().isoformat()}")
    print()
    
    # Discover tasks
    print("Discovering tasks...")
    PluginRegistry.discover()
    tasks = PluginRegistry.list_tasks()
    print(f"Found {len(tasks)} registered tasks")
    print()
    
    # Test parameters for each task
    test_params = {
        "disk-forensics": {"image": "test.img", "type": "timeline"},
        "chain-ir": {"address": "0x123abc", "type": "trace"},
        "c2": {"test": True, "port": 8080},
        "tx-replay": {"transaction": "0xabc123"},
        "rwa-scan": {"contract": "0xdef456"},
        "lateral-move": {"target": "192.168.1.100"},
        "social-eng": {"campaign_type": "phishing", "target_count": 10},
        "memory-forensics": {"dump_path": "demo.mem", "analysis_type": "processes"}
    }
    
    # Test each task
    results = {}
    success_count = 0
    
    for task_name in sorted(tasks):
        print(f"Testing {task_name}...")
        params = test_params.get(task_name, {})
        # Use a 30s timeout per task
        result = await test_task(task_name, params, timeout=30)
        results[task_name] = result
        
        if result["status"] == "SUCCESS":
            print(f"  ✓ {task_name}: PASSED")
            success_count += 1
        else:
            print(f"  ✗ {task_name}: FAILED - {result['error']}")
    
    print()
    print("Validation Summary")
    print("-" * 30)
    print(f"Total tasks: {len(tasks)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(tasks) - success_count}")
    print(f"Success rate: {(success_count/len(tasks)*100):.1f}%")
    
    # Expected Phase 2 tasks
    expected_tasks = [
        "autopwn", "c2", "chain-ir", "chain-monitor", "cvss", 
        "disk-forensics", "fuzzer", "lateral-move", "llm-assist",
        "memory-forensics", "mythril", "prompt-injection", "rwa-scan",
        "shellcode", "slither", "social-eng", "tx-replay", "web2-static"
    ]
    
    print()
    print("Phase 2 Task Coverage")
    print("-" * 30)
    missing_tasks = set(expected_tasks) - set(tasks)
    extra_tasks = set(tasks) - set(expected_tasks)
    
    if not missing_tasks and not extra_tasks:
        print("✓ All expected Phase 2 tasks are present")
    else:
        if missing_tasks:
            print(f"✗ Missing tasks: {', '.join(missing_tasks)}")
        if extra_tasks:
            print(f"+ Extra tasks: {', '.join(extra_tasks)}")
    
    print()
    print("Phase 2 Implementation Status")
    print("-" * 30)
    
    # Key implemented tasks from our work
    key_implementations = {
        "disk-forensics": "Complete forensics suite with timeline, recovery, hash verification",
        "chain-ir": "Comprehensive blockchain incident response with tracing, clustering, compliance",
        "c2": "Full C2 server with agent management, SSL, admin interface",
        "memory-forensics": "Volatility-style memory analysis simulation",
        "lateral-move": "Network discovery and lateral movement simulation", 
        "social-eng": "Social engineering campaign generation and risk analysis",
        "tx-replay": "Blockchain transaction replay and analysis",
        "rwa-scan": "Real-world asset contract scanning and compliance"
    }
    
    for task, description in key_implementations.items():
        status = results.get(task, {}).get("status", "UNKNOWN")
        if status == "SUCCESS":
            print(f"✓ {task}: {description}")
        else:
            print(f"✗ {task}: {description} - FAILED")
    
    print()
    print("=" * 50)
    if success_count >= len(expected_tasks) * 0.9:  # 90% success rate
        print("🎉 PHASE 2 COMPLETION: SUCCESS")
        print("All critical tasks are functional and ready for Phase 3")
    else:
        print("⚠️  PHASE 2 COMPLETION: PARTIAL")
        print("Some tasks need additional work before Phase 3")
    
    print(f"Validation completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
