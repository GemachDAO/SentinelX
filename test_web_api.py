#!/usr/bin/env python3
"""
Quick test of SentinelX Web API functionality.
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from sentinelx.web import create_app
from sentinelx.core.registry import PluginRegistry

async def test_api_locally():
    """Test the API functionality locally without running a server."""
    print("🚀 Testing SentinelX Web API...")
    
    # Create the FastAPI app
    app = create_app()
    
    # Test that the app was created successfully
    print("✅ FastAPI app created successfully")
    
    # Test task discovery
    PluginRegistry.discover()
    tasks = PluginRegistry.list_tasks()
    print(f"✅ {len(tasks)} tasks discovered: {', '.join(tasks[:5])}{'...' if len(tasks) > 5 else ''}")
    
    # Test getting task info
    if tasks:
        task_name = tasks[0]
        task_cls = PluginRegistry.get_task(task_name)
        if task_cls:
            print(f"✅ Task '{task_name}' loaded successfully")
            doc = getattr(task_cls, '__doc__', 'N/A') or 'No description available'
            print(f"   Description: {doc[:100]}...")
    
    print("\n🎉 Web API is ready!")
    print("📋 Available endpoints:")
    print("   • GET /api/v1/tasks - List all tasks")
    print("   • GET /api/v1/tasks/{name}/info - Get task details")
    print("   • POST /api/v1/tasks/{name}/run - Execute task")
    print("   • GET /api/v1/health - Health check")
    print("   • WebSocket /ws/execution - Real-time updates")
    print("\n🌐 To start the server: python -m sentinelx web start")
    print("📚 API docs will be at: http://localhost:8000/api/docs")

if __name__ == "__main__":
    asyncio.run(test_api_locally())
