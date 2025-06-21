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
from .core.workflow import WorkflowEngine

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

# Workflow commands
workflow_app = typer.Typer(help="Workflow orchestration commands")
app.add_typer(workflow_app, name="workflow")

@workflow_app.command("run")
def workflow_run(
    workflow_file: str = typer.Argument(..., help="Workflow YAML/JSON file path"),
    config: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file path"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results"),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format (json, yaml)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Run a workflow from a YAML/JSON file."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    async def _run_workflow():
        try:
            # Initialize context and registry
            context = Context.load(None)  # Use default config for now
            registry = PluginRegistry()
            
            # Initialize workflow engine
            engine = WorkflowEngine(registry)
            
            # Load and execute workflow
            from pathlib import Path
            workflow_path = Path(workflow_file)
            if not workflow_path.exists():
                rprint(f"[red]Workflow file not found: {workflow_file}[/red]")
                raise typer.Exit(1)
            
            rprint(f"[blue]Loading workflow from:[/blue] {workflow_file}")
            workflow_def = await engine.load_workflow(workflow_path)
            
            rprint(f"[blue]Executing workflow:[/blue] {workflow_def.get('name', 'unnamed')}")
            
            result = await engine.execute_workflow(workflow_def, context)
            
            # Format output
            if output_format == 'yaml':
                output_data = yaml.dump(result.__dict__, default_flow_style=False)
            else:
                output_data = json.dumps(result.__dict__, indent=2, default=str)
            
            # Save or print results
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                rprint(f"[green]Results saved to {output}[/green]")
            else:
                console.print(output_data)
            
            # Print summary
            status_color = "green" if result.status == "completed" else ("yellow" if result.status == "partial" else "red")
            rprint(f"\n[bold]Workflow Status:[/bold] [{status_color}]{result.status}[/{status_color}]")
            rprint(f"[bold]Steps Completed:[/bold] {len(result.steps_completed)}")
            rprint(f"[bold]Duration:[/bold] {result.total_duration:.2f}s")
            
            if result.errors:
                rprint(f"[bold red]Errors:[/bold red] {len(result.errors)}")
                for error in result.errors:
                    rprint(f"  [red]•[/red] {error}")
            
        except Exception as e:
            rprint(f"[red]Workflow execution failed: {e}[/red]")
            if verbose:
                import traceback
                traceback.print_exc()
            raise typer.Exit(1)
    
    asyncio.run(_run_workflow())

@workflow_app.command("template")
def workflow_template(
    output_file: str = typer.Argument(..., help="Output file path for template"),
    template_type: str = typer.Option("basic", "--type", "-t", help="Template type (basic, audit, assessment)")
):
    """Generate a workflow template file."""
    from pathlib import Path
    
    templates = {
        "basic": {
            "name": "basic_security_workflow",
            "description": "Basic security assessment workflow",
            "continue_on_error": True,
            "steps": [
                {
                    "name": "static_analysis",
                    "task": "web2-static",  
                    "params": {
                        "file_path": "test_code.php",
                        "language": "php"
                    }
                },
                {
                    "name": "vulnerability_scoring",
                    "task": "cvss",
                    "params": {
                        "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                    },
                    "depends_on": ["static_analysis"]
                }
            ]
        },
        "audit": {
            "name": "smart_contract_audit",
            "description": "Complete smart contract security audit",
            "continue_on_error": True,
            "steps": [
                {
                    "name": "slither_analysis",
                    "task": "slither",
                    "params": {
                        "contract_path": "test_contract.sol",
                        "format": "json"
                    }
                },
                {
                    "name": "mythril_analysis", 
                    "task": "mythril",
                    "params": {
                        "contract_path": "test_contract.sol",
                        "timeout": 300
                    },
                    "depends_on": ["slither_analysis"]
                },
                {
                    "name": "cvss_scoring",
                    "task": "cvss",
                    "params": {
                        "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                    },
                    "depends_on": ["mythril_analysis"]
                }
            ]
        },
        "assessment": {
            "name": "comprehensive_assessment",
            "description": "Comprehensive security assessment workflow",
            "continue_on_error": True,
            "steps": [
                {
                    "name": "contract_scan",
                    "task": "slither",
                    "params": {
                        "contract_path": "test_contract.sol"
                    }
                },
                {
                    "name": "web_scan",
                    "task": "web2-static",
                    "params": {
                        "file_path": "test_vulnerable.php",
                        "language": "php"
                    }
                },
                {
                    "name": "shellcode_gen",
                    "task": "shellcode",
                    "params": {
                        "arch": "amd64",
                        "payload": "/bin/sh"
                    },
                    "depends_on": ["contract_scan", "web_scan"]
                }
            ]
        }
    }
    
    if template_type not in templates:
        rprint(f"[red]Unknown template type: {template_type}[/red]")
        rprint(f"Available types: {', '.join(templates.keys())}")
        raise typer.Exit(1)
    
    template_workflow = templates[template_type]
    output_path = Path(output_file)
    
    try:
        if output_path.suffix.lower() in ['.yaml', '.yml']:
            with open(output_path, 'w') as f:
                yaml.dump(template_workflow, f, default_flow_style=False)
        else:
            with open(output_path, 'w') as f:
                json.dump(template_workflow, f, indent=2)
        
        rprint(f"[green]Workflow template created:[/green] {output_path}")
        rprint(f"[blue]Template type:[/blue] {template_type}")
        rprint(f"[blue]Steps:[/blue] {len(template_workflow['steps'])}")
        
    except Exception as e:
        rprint(f"[red]Error creating template: {e}[/red]")
        raise typer.Exit(1)

@workflow_app.command("list")
def workflow_list():
    """List available workflow templates and tasks."""
    
    # Show available template types
    rprint("[bold blue]Available Template Types:[/bold blue]")
    templates = [
        ("basic", "Basic security assessment workflow"),
        ("audit", "Complete smart contract security audit"),
        ("assessment", "Comprehensive security assessment workflow")
    ]
    
    for name, description in templates:
        rprint(f"  [cyan]{name}[/cyan]: {description}")
    
    # Show available tasks for workflows
    rprint("\n[bold blue]Available Tasks for Workflows:[/bold blue]")
    tasks = PluginRegistry.list_tasks()
    
    # Group tasks by category
    categories = {}
    for task_name in tasks:
        if 'audit' in task_name or 'cvss' in task_name or 'slither' in task_name or 'mythril' in task_name:
            category = "Audit"
        elif 'web' in task_name or 'fuzzer' in task_name:
            category = "Web Security"
        elif 'shell' in task_name or 'autopwn' in task_name:
            category = "Exploit"
        elif 'chain' in task_name or 'tx' in task_name or 'rwa' in task_name:
            category = "Blockchain"
        elif 'c2' in task_name or 'lateral' in task_name or 'social' in task_name:
            category = "Red Team"
        elif 'memory' in task_name or 'disk' in task_name or 'chain-ir' in task_name:
            category = "Forensics"
        elif 'llm' in task_name or 'prompt' in task_name:
            category = "AI Security"
        else:
            category = "Other"
        
        if category not in categories:
            categories[category] = []
        categories[category].append(task_name)
    
    for category, task_names in sorted(categories.items()):
        rprint(f"\n  [bold yellow]{category}:[/bold yellow]")
        for task_name in sorted(task_names):
            rprint(f"    • {task_name}")

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
