from __future__ import annotations
import typer
import asyncio
import yaml
import json
import sys
import logging
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from .core.registry import PluginRegistry
from .core.context import Context
from .core.task import TaskError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = typer.Typer(help="SentinelX - Modular Security Framework")
console = Console()

# Auto-discover plugins when module is imported
PluginRegistry.discover()

@app.command()
def run(
    task: str = typer.Argument(..., help="Name of the task to run"),
    params: str = typer.Option("{}", "--params", "-p", help="YAML/JSON parameters string"),
    config: str = typer.Option("config.yaml", "--config", "-c", help="Path to configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    output_format: str = typer.Option("yaml", "--format", "-f", help="Output format (yaml, json, table)")
):
    """Run a registered SentinelX task."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Parse parameters
        try:
            p = yaml.safe_load(params) or {}
            if not isinstance(p, dict):
                raise ValueError("Parameters must be a dictionary")
        except yaml.YAMLError as e:
            rprint(f"[red]Error parsing parameters: {e}[/red]")
            raise typer.Exit(1)
        
        # Load context
        try:
            ctx = Context.load(config)
        except Exception as e:
            rprint(f"[red]Error loading configuration: {e}[/red]")
            raise typer.Exit(1)
        
        # Create and run task
        try:
            task_instance = PluginRegistry.create(task, ctx=ctx, **p)
            
            with console.status(f"[bold green]Running task '{task}'..."):
                result = asyncio.run(task_instance())
            
            # Output results
            if output_format.lower() == "json":
                print(json.dumps(result, indent=2, default=str))
            elif output_format.lower() == "table" and isinstance(result, dict):
                table = Table(title=f"Task '{task}' Results")
                table.add_column("Key", style="cyan")
                table.add_column("Value", style="magenta")
                
                for key, value in result.items():
                    table.add_row(str(key), str(value))
                
                console.print(table)
            else:  # Default to YAML
                print(yaml.dump(result, default_flow_style=False))
                
        except ValueError as e:
            rprint(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        except TaskError as e:
            rprint(f"[red]Task execution failed: {e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            rprint(f"[red]Unexpected error: {e}[/red]")
            if verbose:
                import traceback
                traceback.print_exc()
            raise typer.Exit(1)
    
    except typer.Exit:
        raise
    except Exception as e:
        rprint(f"[red]Fatal error: {e}[/red]")
        raise typer.Exit(1)

@app.command("list")
def list_tasks():
    """List all registered tasks."""
    tasks = PluginRegistry.list_tasks()
    
    if not tasks:
        rprint("[yellow]No tasks registered[/yellow]")
        return
    
    table = Table(title="Registered SentinelX Tasks")
    table.add_column("Task Name", style="cyan")
    table.add_column("Task Class", style="magenta")
    table.add_column("Module", style="green")
    
    for task_name in tasks:
        task_cls = PluginRegistry.get_task_class(task_name)
        if task_cls:
            table.add_row(
                task_name,
                task_cls.__name__,
                task_cls.__module__
            )
    
    console.print(table)

@app.command()
def info(task_name: str = typer.Argument(..., help="Name of the task to get info about")):
    """Get detailed information about a specific task."""
    task_cls = PluginRegistry.get_task_class(task_name)
    
    if not task_cls:
        rprint(f"[red]Task '{task_name}' not found[/red]")
        available = ", ".join(PluginRegistry.list_tasks())
        rprint(f"Available tasks: {available}")
        raise typer.Exit(1)
    
    table = Table(title=f"Task Information: {task_name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Name", task_name)
    table.add_row("Class", task_cls.__name__)
    table.add_row("Module", task_cls.__module__)
    table.add_row("Doc", task_cls.__doc__ or "No documentation available")
    
    # Show required parameters if defined
    required_params = getattr(task_cls, 'REQUIRED_PARAMS', [])
    if required_params:
        table.add_row("Required Parameters", ", ".join(required_params))
    
    console.print(table)

@app.command()
def version():
    """Show SentinelX version information."""
    try:
        import importlib.metadata
        version = importlib.metadata.version("sentinelx")
    except Exception:
        version = "development"  
    
    rprint(f"[bold green]SentinelX[/bold green] version [cyan]{version}[/cyan]")
    rprint(f"Registered tasks: [yellow]{len(PluginRegistry.list_tasks())}[/yellow]")

if __name__ == "__main__":
    app()

def main():
    """Entry point for the sentinelx command."""
    app()
