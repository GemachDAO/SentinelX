#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspaces/SentinelX')

print("Testing basic imports...")
try:
    from sentinelx.core.workflow import WorkflowEngine
    print("✓ WorkflowEngine imported successfully")
except Exception as e:
    print(f"✗ WorkflowEngine import failed: {e}")

try:
    from sentinelx.core.registry import PluginRegistry
    print("✓ PluginRegistry imported successfully")
except Exception as e:
    print(f"✗ PluginRegistry import failed: {e}")

try:
    from sentinelx.core.context import Context
    print("✓ Context imported successfully")
except Exception as e:
    print(f"✗ Context import failed: {e}")

print("Basic imports test completed.")
