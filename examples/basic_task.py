#!/usr/bin/env python3
"""
Basic Task Execution Example

This example demonstrates how to run individual SentinelX security tasks
programmatically and handle their results.
"""

import asyncio
import logging
from pathlib import Path
from sentinelx.core.context import Context
from sentinelx.core.registry import PluginRegistry
from sentinelx.core.task import TaskError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_single_task():
    """Example: Run a single security task."""
    try:
        # Load configuration
        context = Context.load("config.yaml")
        
        # Create and run CVSS scoring task
        task = PluginRegistry.create(
            "cvss",
            vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        )
        
        logger.info("Running CVSS scoring task...")
        result = await task.execute(context)
        
        # Display results
        print("\n=== CVSS Scoring Results ===")
        print(f"Vector: {result.get('vector')}")
        print(f"Base Score: {result.get('base_score')}")
        print(f"Severity: {result.get('severity')}")
        print(f"Environmental Score: {result.get('environmental_score', 'N/A')}")
        
        return result
        
    except TaskError as e:
        logger.error(f"Task execution failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

async def run_multiple_tasks():
    """Example: Run multiple tasks sequentially."""
    context = Context.load("config.yaml")
    
    tasks = [
        {
            "name": "cvss",
            "params": {"vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N"}
        },
        {
            "name": "cvss", 
            "params": {"vector": "CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H"}
        }
    ]
    
    results = []
    
    for task_config in tasks:
        try:
            task = PluginRegistry.create(
                task_config["name"],
                **task_config["params"]
            )
            
            logger.info(f"Running task: {task_config['name']}")
            result = await task.execute(context)
            results.append(result)
            
            print(f"\nTask: {task_config['name']}")
            print(f"Vector: {result.get('vector')}")
            print(f"Score: {result.get('base_score')} ({result.get('severity')})")
            
        except Exception as e:
            logger.error(f"Task {task_config['name']} failed: {e}")
            continue
    
    return results

async def run_with_error_handling():
    """Example: Proper error handling for task execution."""
    context = Context.load("config.yaml")
    
    # Try to run a task that might fail
    try:
        task = PluginRegistry.create(
            "slither",
            contract_path="nonexistent_contract.sol"  # This will fail
        )
        
        result = await task.execute(context)
        
    except TaskError as e:
        logger.warning(f"Task failed as expected: {e}")
        print(f"Handled task error: {e}")
        
        # Try with a valid example
        try:
            # Create a simple test contract
            test_contract = Path("test_contract.sol")
            test_contract.write_text("""
pragma solidity ^0.8.0;

contract SimpleToken {
    mapping(address => uint256) public balances;
    
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}
""")
            
            # Run analysis on the test contract
            task = PluginRegistry.create(
                "slither",
                contract_path=str(test_contract),
                format="json"
            )
            
            result = await task.execute(context)
            print(f"\nSlither analysis completed successfully!")
            print(f"Vulnerabilities found: {result.get('vulnerabilities_found', 0)}")
            
            # Clean up
            test_contract.unlink()
            
        except Exception as inner_e:
            logger.error(f"Backup task also failed: {inner_e}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def list_available_tasks():
    """Example: List and explore available tasks."""
    print("\n=== Available SentinelX Tasks ===")
    
    tasks = PluginRegistry.list_tasks()
    
    # Group by category
    categories = {}
    for task in tasks:
        category = task.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(task)
    
    for category, task_list in categories.items():
        print(f"\n{category}:")
        for task in task_list:
            status = "✅" if task.get('ready', False) else "⚠️"
            print(f"  {status} {task['name']} - {task.get('description', 'No description')}")

def search_tasks():
    """Example: Search for specific tasks."""
    print("\n=== Task Search Examples ===")
    
    # Search for contract-related tasks
    contract_tasks = PluginRegistry.search_tasks("contract")
    print(f"\nContract-related tasks ({len(contract_tasks)}):")
    for task in contract_tasks:
        print(f"  • {task['name']} - {task.get('description', '')}")
    
    # Search for web security tasks
    web_tasks = PluginRegistry.search_tasks("web")
    print(f"\nWeb security tasks ({len(web_tasks)}):")
    for task in web_tasks:
        print(f"  • {task['name']} - {task.get('description', '')}")

async def main():
    """Main example runner."""
    print("SentinelX Basic Task Execution Examples")
    print("=" * 40)
    
    # Discover available tasks
    PluginRegistry.discover()
    
    # List available tasks
    list_available_tasks()
    
    # Search for tasks
    search_tasks()
    
    # Run single task example
    print("\n" + "=" * 40)
    print("Running single task example...")
    await run_single_task()
    
    # Run multiple tasks example
    print("\n" + "=" * 40)
    print("Running multiple tasks example...")
    await run_multiple_tasks()
    
    # Error handling example
    print("\n" + "=" * 40)
    print("Running error handling example...")
    await run_with_error_handling()
    
    print("\n" + "=" * 40)
    print("Examples completed!")

if __name__ == "__main__":
    asyncio.run(main())
