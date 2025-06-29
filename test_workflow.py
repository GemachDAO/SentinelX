#!/usr/bin/env python3
"""
Test script to verify workflow functionality works directly.
"""
import asyncio
import sys
sys.path.insert(0, '/workspaces/SentinelX')

from sentinelx.core.context import Context
from sentinelx.core.registry import PluginRegistry
from sentinelx.core.workflow import WorkflowEngine
from pathlib import Path

async def test_workflow():
    """Test workflow execution directly."""
    print("Testing workflow system...")
    
    # Initialize components
    context = Context.load(None)
    PluginRegistry.discover()
    registry = PluginRegistry()
    engine = WorkflowEngine(registry)
    
    # Simple workflow definition
    workflow_def = {
        "name": "test_workflow",
        "description": "Simple test workflow",
        "continue_on_error": True,
        "steps": [
            {
                "name": "cvss_test",
                "task": "cvss",
                "params": {
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                }
            }
        ]
    }
    
    print("Running workflow...")
    result = await engine.execute_workflow(workflow_def, context)
    
    print(f"Workflow Status: {result.status}")
    print(f"Steps Completed: {result.steps_completed}")
    print(f"Duration: {result.total_duration:.2f}s")
    
    if result.errors:
        print(f"Errors: {result.errors}")
    
    return result.status == "completed"

if __name__ == "__main__":
    success = asyncio.run(test_workflow())
    print(f"Test {'PASSED' if success else 'FAILED'}")
