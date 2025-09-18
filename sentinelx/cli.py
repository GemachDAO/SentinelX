from __future__ import annotations
import typer
import asyncio
import yaml
import json
import sys
import logging
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from .core.registry import PluginRegistry
from .core.context import Context
from .core.task import TaskError
from .core.workflow import WorkflowEngine

# Phase 4 imports (optional)
try:
    from .deployment import DockerManager
    HAS_DOCKER = True
except ImportError:
    HAS_DOCKER = False

try:
    from .performance import PerformanceProfiler, BenchmarkSuite
    HAS_PERFORMANCE = True
except ImportError:
    HAS_PERFORMANCE = False

try:
    from .reporting import ReportGenerator, SecurityReport, ReportSection
    HAS_REPORTING = True
except ImportError:
    HAS_REPORTING = False



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = typer.Typer(help="SentinelX - Modular Security Framework")
console = Console()

# Phase 4: Add new command groups (conditionally)
if HAS_DOCKER:
    docker_app = typer.Typer(help="Docker deployment and sandboxing commands")
    app.add_typer(docker_app, name="docker")

if HAS_PERFORMANCE:
    performance_app = typer.Typer(help="Performance monitoring and optimization commands")
    app.add_typer(performance_app, name="perf")

if HAS_REPORTING:
    report_app = typer.Typer(help="Advanced reporting commands")
    app.add_typer(report_app, name="report")

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
def list_tasks(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category (audit, exploit, blockchain, redteam, forensic, ai, web)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed information for each task")
):
    """List all registered tasks, optionally filtered by category."""
    tasks = PluginRegistry.list_tasks()
    
    if not tasks:
        rprint("[yellow]No tasks registered[/yellow]")
        return
    
    # New header line expected by tests
    rprint("Registered SentinelX Tasks")
    
    # Organize tasks by category
    categories = {
        "Smart Contract Audit": [],
        "Exploit Development": [],
        "Blockchain Security": [],
        "Red Team Operations": [],
        "Digital Forensics": [],
        "AI Security": [],
        "Web Security": [],
        "Other": []
    }
    
    for task_name in sorted(tasks):
        task_cls = PluginRegistry.get_task_class(task_name)
        if not task_cls:
            continue
            
        # Categorize based on task name and module
        if any(x in task_name for x in ['slither', 'mythril', 'cvss']):
            categories["Smart Contract Audit"].append((task_name, task_cls))
        elif any(x in task_name for x in ['shellcode', 'fuzzer', 'autopwn']):
            categories["Exploit Development"].append((task_name, task_cls))
        elif any(x in task_name for x in ['chain', 'tx-replay', 'rwa']):
            categories["Blockchain Security"].append((task_name, task_cls))
        elif any(x in task_name for x in ['c2', 'lateral', 'social']):
            categories["Red Team Operations"].append((task_name, task_cls))
        elif any(x in task_name for x in ['memory', 'disk', 'forensic']):
            categories["Digital Forensics"].append((task_name, task_cls))
        elif any(x in task_name for x in ['llm', 'prompt', 'ai']):
            categories["AI Security"].append((task_name, task_cls))
        elif 'web' in task_name or 'fuzzer' in task_name:
            categories["Web Security"].append((task_name, task_cls))
        else:
            categories["Other"].append((task_name, task_cls))
    
    # Filter by category if specified
    if category:
        category_map = {
            "audit": "Smart Contract Audit",
            "exploit": "Exploit Development", 
            "blockchain": "Blockchain Security",
            "redteam": "Red Team Operations",
            "forensic": "Digital Forensics",
            "ai": "AI Security",
            "web": "Web Security"
        }
        filter_cat = category_map.get(category.lower())
        if filter_cat and filter_cat in categories:
            categories = {filter_cat: categories[filter_cat]}
        else:
            rprint(f"[red]Unknown category: {category}[/red]")
            rprint(f"[yellow]Available categories: {', '.join(category_map.keys())}[/yellow]")
            return
    
    # Display tasks by category
    total_tasks = 0
    for cat_name, task_list in categories.items():
        if not task_list:
            continue
            
        rprint(f"\n[bold blue]🔥 {cat_name} ({len(task_list)} tasks)[/bold blue]")
        
        if detailed:
            table = Table()
            table.add_column("Task", style="cyan")
            table.add_column("Description", style="green")
            table.add_column("Module", style="yellow")
            
            for task_name, task_cls in task_list:
                description = (task_cls.__doc__ or "No description").split('\n')[0][:60]
                if len(description) >= 60:
                    description += "..."
                table.add_row(
                    task_name,
                    description,
                    task_cls.__module__.split('.')[-1]
                )
            console.print(table)
        else:
            # Simple list view
            for task_name, task_cls in task_list:
                description = (task_cls.__doc__ or "No description").split('\n')[0][:40]
                if len(description) >= 40:
                    description += "..."
                rprint(f"  🎯 [cyan]{task_name:20}[/cyan] - {description}")
        
        total_tasks += len(task_list)
    
    rprint(f"\n[bold green]📊 Total: {total_tasks} security tasks available[/bold green]")
    rprint(f"[dim]Use 'sentinelx info <task_name>' for detailed information[/dim]")
    rprint(f"[dim]Use 'sentinelx list --category <cat>' to filter by category[/dim]")

@app.command()
def info(
    task_name: str = typer.Argument(..., help="Name of the task to get info about"),
    examples: bool = typer.Option(False, "--examples", "-e", help="Show usage examples")
):
    """Get detailed information about a specific task."""
    task_cls = PluginRegistry.get_task_class(task_name)
    
    if not task_cls:
        rprint(f"[red]❌ Task '{task_name}' not found[/red]")
        
        # Suggest similar tasks
        all_tasks = PluginRegistry.list_tasks()
        similar = [t for t in all_tasks if task_name.lower() in t.lower() or t.lower() in task_name.lower()]
        
        if similar:
            rprint(f"[yellow]💡 Did you mean one of these?[/yellow]")
            for sim_task in similar[:5]:
                rprint(f"  • {sim_task}")
        else:
            rprint(f"[blue]Available tasks:[/blue] {', '.join(sorted(all_tasks)[:10])}{'...' if len(all_tasks) > 10 else ''}")
        
        rprint(f"[dim]Use 'sentinelx list' to see all available tasks[/dim]")
        raise typer.Exit(1)
    
    # New header line expected by tests
    rprint(f"Task Information: {task_name}")
    
    # Enhanced task information display
    rprint(f"[bold green]🎯 {task_name}[/bold green]")
    rprint("─" * 50)
    
    # Basic information
    table = Table(show_header=False, box=None)
    table.add_column("Property", style="cyan", width=15)
    table.add_column("Value", style="white")
    
    table.add_row("📋 Name", task_name)
    table.add_row("🏷️ Class", task_cls.__name__)
    table.add_row("📦 Module", task_cls.__module__)
    
    # Get category
    category = "Other"
    if any(x in task_name for x in ['slither', 'mythril', 'cvss']):
        category = "Smart Contract Audit"
    elif any(x in task_name for x in ['shellcode', 'fuzzer', 'autopwn']):
        category = "Exploit Development"
    elif any(x in task_name for x in ['chain', 'tx-replay', 'rwa']):
        category = "Blockchain Security"
    elif any(x in task_name for x in ['c2', 'lateral', 'social']):
        category = "Red Team Operations"
    elif any(x in task_name for x in ['memory', 'disk', 'forensic']):
        category = "Digital Forensics"
    elif any(x in task_name for x in ['llm', 'prompt', 'ai']):
        category = "AI Security"
    elif 'web' in task_name or 'static' in task_name.lower():
        category = "Web Security"
    
    table.add_row("📂 Category", category)
    
    # Documentation
    doc = task_cls.__doc__ or "No documentation available"
    doc_lines = doc.strip().split('\n')
    main_doc = doc_lines[0] if doc_lines else "No description"
    table.add_row("📝 Description", main_doc)
    
    console.print(table)
    
    # Extended documentation if available
    if len(doc_lines) > 1:
        rprint(f"\n[bold]📖 Extended Documentation:[/bold]")
        for line in doc_lines[1:]:
            if line.strip():
                rprint(f"  {line.strip()}")
    
    # Parameters information
    required_params = getattr(task_cls, 'REQUIRED_PARAMS', [])
    optional_params = getattr(task_cls, 'OPTIONAL_PARAMS', [])
    
    if required_params or optional_params:
        rprint(f"\n[bold]⚙️ Parameters:[/bold]")
        
        if required_params:
            rprint(f"[red]Required:[/red]")
            for param in required_params:
                rprint(f"  • {param}")
        
        if optional_params:
            rprint(f"[yellow]Optional:[/yellow]")
            for param in optional_params:
                rprint(f"  • {param}")
    
    # Usage examples
    if examples:
        rprint(f"\n[bold]💡 Usage Examples:[/bold]")
        
        # Generate examples based on task type
        if task_name == "cvss":
            rprint(f"  [dim]# Basic CVSS scoring[/dim]")
            rprint(f"  sentinelx run {task_name} -p \"{{vector: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'}}\"")
        elif task_name == "slither":
            rprint(f"  [dim]# Analyze smart contract[/dim]")
            rprint(f"  sentinelx run {task_name} -p \"{{contract_path: 'contract.sol', format: 'json'}}\"")
        elif task_name == "web2-static":
            rprint(f"  [dim]# Static code analysis[/dim]")
            rprint(f"  sentinelx run {task_name} -p \"{{target: 'app.php', language: 'php'}}\"")
        elif task_name == "shellcode":
            rprint(f"  [dim]# Generate shellcode[/dim]")
            rprint(f"  sentinelx run {task_name} -p \"{{arch: 'amd64', payload: '/bin/sh'}}\"")
        else:
            rprint(f"  [dim]# Basic execution[/dim]")
            rprint(f"  sentinelx run {task_name}")
            rprint(f"  [dim]# With parameters[/dim]")
            rprint(f"  sentinelx run {task_name} -p \"{{param1: 'value1'}}\"")
        
        rprint(f"  [dim]# With custom config and verbose output[/dim]")
        rprint(f"  sentinelx run {task_name} -c config.yaml -v")
        rprint(f"  [dim]# Output as JSON[/dim]")
        rprint(f"  sentinelx run {task_name} -f json")
    
    rprint(f"\n[dim]💡 Use --examples to see usage examples[/dim]")
    rprint(f"[dim]💡 Use 'sentinelx run {task_name} --help' for run-specific options[/dim]")

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

# ===== PHASE 4: DOCKER COMMANDS =====

if HAS_DOCKER:
    @docker_app.command("setup")
    def docker_setup(
        force_rebuild: bool = typer.Option(False, "--force", "-f", help="Force rebuild of images")
    ):
        """Set up Docker environment for SentinelX."""
        rprint("[bold blue]🐳 Setting up SentinelX Docker environment...[/bold blue]")
        
        try:
            manager = DockerManager()
            result = asyncio.run(manager.setup(force_rebuild=force_rebuild))
            
            if result["success"]:
                rprint("[green]✅ Docker environment setup complete![/green]")
                rprint("\n[bold]Images built:[/bold]")
                for name, image_id in result["images"].items():
                    if "ERROR" not in str(image_id):
                        rprint(f"  ✅ {name}: {image_id[:12] if len(str(image_id)) > 12 else image_id}")
                    else:
                        rprint(f"  ❌ {name}: {image_id}")
                
                rprint("\n[bold]Networks created:[/bold]")
                for name, net_id in result["networks"].items():
                    if "ERROR" not in str(net_id):
                        rprint(f"  ✅ {name}: {net_id if net_id == 'EXISTS' else net_id[:12]}")
                    else:
                        rprint(f"  ❌ {name}: {net_id}")
            else:
                rprint("[red]❌ Docker environment setup failed![/red]")
        except Exception as e:
            rprint(f"[red]Error setting up Docker: {e}[/red]")
            raise typer.Exit(1)

    @docker_app.command("run")
    def docker_run(
        task: str = typer.Argument(..., help="Task to run in Docker"),
        params: str = typer.Option("{}", "--params", "-p", help="Task parameters as YAML/JSON"),
        dangerous: bool = typer.Option(False, "--sandbox", "-s", help="Use isolated sandbox for dangerous tasks"),
        timeout: int = typer.Option(300, "--timeout", "-t", help="Execution timeout in seconds")
    ):
        """Run a task in Docker container."""
        rprint(f"[bold blue]🐳 Running task '{task}' in Docker{'(sandbox)' if dangerous else ''}...[/bold blue]")
        
        try:
            from .deployment import DockerTaskRunner, DockerConfig
            
            # Parse parameters
            task_args = yaml.safe_load(params) or {}
            
            # Configure Docker runner
            config = DockerConfig(timeout=timeout)
            runner = DockerTaskRunner(config)
            
            # Run task
            result = asyncio.run(runner.run_task_sandboxed(task, task_args, dangerous))
            
            if result["success"]:
                rprint("[green]✅ Task completed successfully![/green]")
                rprint(f"Container ID: {result['container_id']}")
                if result.get("result"):
                    rprint("\n[bold]Result:[/bold]")
                    rprint(yaml.dump(result["result"], default_flow_style=False))
            else:
                rprint(f"[red]❌ Task failed: {result['error']}[/red]")
                if result.get("logs"):
                    rprint("\n[bold]Logs:[/bold]")
                    rprint(result["logs"])
        except Exception as e:
            rprint(f"[red]Error running Docker task: {e}[/red]")
            raise typer.Exit(1)

    @docker_app.command("cleanup")
    def docker_cleanup():
        """Clean up SentinelX Docker resources."""
        rprint("[bold yellow]🧹 Cleaning up Docker resources...[/bold yellow]")
        
        try:
            manager = DockerManager()
            result = manager.cleanup()
            
            rprint("[green]✅ Cleanup complete![/green]")
            rprint(f"Containers removed: {len(result.get('containers', []))}")
            rprint(f"Images removed: {len(result.get('images', []))}")
            rprint(f"Networks removed: {len(result.get('networks', []))}")
        except Exception as e:
            rprint(f"[red]Error during cleanup: {e}[/red]")
            raise typer.Exit(1)

# ===== PHASE 4: PERFORMANCE COMMANDS =====

if HAS_PERFORMANCE:
    @performance_app.command("profile")
    def perf_profile(
        task: str = typer.Argument(..., help="Task to profile"),
        params: str = typer.Option("{}", "--params", "-p", help="Task parameters"),
        iterations: int = typer.Option(1, "--iterations", "-i", help="Number of iterations"),
        output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results")
    ):
        """Profile task performance."""
        rprint(f"[bold yellow]⚡ Profiling task '{task}' ({iterations} iterations)...[/bold yellow]")
        
        try:
            profiler = PerformanceProfiler()
            task_args = yaml.safe_load(params) or {}
            
            # Get task from registry
            task_cls = PluginRegistry.get_task(task)
            if not task_cls:
                rprint(f"[red]Task '{task}' not found[/red]")
                raise typer.Exit(1)
            
            # Profile multiple iterations
            total_time = 0
            total_memory = 0
            
            for i in range(iterations):
                with profiler.profile_context(f"iteration_{i}"):
                    context = Context()
                    task_instance = task_cls()
                    asyncio.run(task_instance.execute(context, **task_args))
                
                metrics = profiler._profiling_data[f"iteration_{i}"]
                total_time += metrics.execution_time
                total_memory += metrics.memory_usage.get("delta_rss", 0)
            
            avg_time = total_time / iterations
            avg_memory = total_memory / iterations
            
            # Display results
            table = Table(title=f"Performance Profile: {task}")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Iterations", str(iterations))
            table.add_row("Average Time", f"{avg_time:.3f}s")
            table.add_row("Total Time", f"{total_time:.3f}s")
            table.add_row("Average Memory Delta", f"{avg_memory:,} bytes")
            table.add_row("Throughput", f"{iterations/total_time:.2f} ops/sec")
            
            console.print(table)
            
            # Save to file if requested
            if output:
                results = {
                    "task": task,
                    "iterations": iterations,
                    "avg_time": avg_time,
                    "total_time": total_time,
                    "avg_memory": avg_memory,
                    "throughput": iterations/total_time
                }
                with open(output, 'w') as f:
                    yaml.dump(results, f)
                rprint(f"[green]Results saved to {output}[/green]")
                
        except Exception as e:
            rprint(f"[red]Error profiling task: {e}[/red]")
            raise typer.Exit(1)

    @performance_app.command("benchmark")
    def perf_benchmark(
        tasks: str = typer.Argument(..., help="Comma-separated list of tasks to benchmark"),
        iterations: int = typer.Option(10, "--iterations", "-i", help="Number of iterations per task"),
        output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for report")
    ):
        """Run comprehensive benchmark suite."""
        task_list = [t.strip() for t in tasks.split(",")]
        rprint(f"[bold yellow]🏃 Benchmarking tasks: {', '.join(task_list)}[/bold yellow]")
        
        try:
            suite = BenchmarkSuite()
            
            for task_name in task_list:
                task_cls = PluginRegistry.get_task(task_name)
                if not task_cls:
                    rprint(f"[yellow]Warning: Task '{task_name}' not found, skipping[/yellow]")
                    continue
                
                async def task_func():
                    context = Context()
                    task_instance = task_cls()
                    await task_instance.execute(context)
                
                result = asyncio.run(suite.benchmark_task(task_name, task_func, iterations))
                
                rprint(f"[green]✅ {task_name}: {result['execution_time']['average']:.3f}s avg[/green]")
            
            # Generate report
            report_text = suite.generate_report(Path(output) if output else None)
            
            if not output:
                console.print("\n" + report_text)
            
            rprint("[green]✅ Benchmark complete![/green]")
            
        except Exception as e:
            rprint(f"[red]Error running benchmark: {e}[/red]")
            raise typer.Exit(1)

# ===== PHASE 4: REPORTING COMMANDS =====

if HAS_REPORTING:
    @report_app.command("generate")
    def report_generate(
        workflow_file: str = typer.Argument(..., help="Path to workflow results file"),
        format: str = typer.Option("html", "--format", "-f", help="Output format (html, pdf, markdown, json)"),
        output: str = typer.Option("report", "--output", "-o", help="Output file path (without extension)"),
        template: Optional[str] = typer.Option(None, "--template", "-t", help="Custom template file")
    ):
        """Generate advanced security report from workflow results."""
        rprint(f"[bold blue]📊 Generating {format.upper()} report...[/bold blue]")
        
        try:
            # Load workflow results
            with open(workflow_file, 'r') as f:
                workflow_data = yaml.safe_load(f)
            
            generator = ReportGenerator()
            
            # Create report from workflow data
            report = SecurityReport(
                title=workflow_data.get("title", "Security Assessment Report"),
                workflow_name=workflow_data.get("workflow_name", "Unknown"),
                execution_time=workflow_data.get("execution_time", "Unknown"),
                duration=workflow_data.get("duration", 0),
                status=workflow_data.get("status", "completed")
            )
            
            # Add sections from workflow results
            for step_name, step_result in workflow_data.get("results", {}).items():
                section = ReportSection(
                    title=step_name,
                    content=f"<p>{step_result.get('summary', 'Task completed successfully')}</p>",
                    data=step_result,
                    severity=step_result.get("severity", "info")
                )
                report.sections.append(section)
            
            # Generate summary statistics
            report.summary = generator.generate_summary(report)
            
            # Export report
            output_path = Path(output)
            generator.export_report(report, output_path, format)
            
            rprint(f"[green]✅ Report generated: {output_path.with_suffix('.' + format)}[/green]")
            
        except Exception as e:
            rprint(f"[red]Error generating report: {e}[/red]")
            raise typer.Exit(1)

    @report_app.command("template")
    def report_template(
        action: str = typer.Argument(..., help="Action: list, create, or customize"),
        name: Optional[str] = typer.Option(None, "--name", "-n", help="Template name"),
        output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for template")
    ):
        """Manage report templates."""
        generator = ReportGenerator()
        
        if action == "list":
            rprint("[bold blue]📋 Available report templates:[/bold blue]")
            rprint("  • base_report.html (Default HTML template)")
            rprint("  • executive_summary.md (Executive summary template)")
            rprint("  • technical_details.html (Technical details template)")
            
        elif action == "create":
            if not name or not output:
                rprint("[red]Error: --name and --output required for create action[/red]")
                raise typer.Exit(1)
                
            generator.create_template(name, Path(output))
            rprint(f"[green]✅ Template '{name}' created at {output}[/green]")
            
        elif action == "customize":
            rprint("[yellow]Template customization feature coming soon![/yellow]")
            
        else:
            rprint(f"[red]Unknown action: {action}[/red]")
            raise typer.Exit(1)

@app.command()
def search(
    query: str = typer.Argument(..., help="Search term for tasks and descriptions"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", "-s", help="Case sensitive search")
):
    """Search for tasks by name or description."""
    tasks = PluginRegistry.list_tasks()
    
    if not tasks:
        rprint("[yellow]No tasks registered[/yellow]")
        return
    
    search_term = query if case_sensitive else query.lower()
    matches = []
    
    for task_name in tasks:
        task_cls = PluginRegistry.get_task_class(task_name)
        if not task_cls:
            continue
        
        # Search in task name
        task_match = search_term in (task_name if case_sensitive else task_name.lower())
        
        # Search in description/docstring
        doc = task_cls.__doc__ or ""
        doc_match = search_term in (doc if case_sensitive else doc.lower())
        
        # Search in module name
        module_match = search_term in (task_cls.__module__ if case_sensitive else task_cls.__module__.lower())
        
        if task_match or doc_match or module_match:
            match_reasons = []
            if task_match:
                match_reasons.append("name")
            if doc_match:
                match_reasons.append("description")
            if module_match:
                match_reasons.append("module")
            
            matches.append((task_name, task_cls, match_reasons))
    
    if not matches:
        rprint(f"[yellow]No tasks found matching '{query}'[/yellow]")
        rprint("[dim]💡 Try a different search term or use 'sentinelx list' to see all tasks[/dim]")
        return
    
    rprint(f"[bold green]🔍 Found {len(matches)} task(s) matching '{query}':[/bold green]")
    rprint("─" * 60)
    
    for i, (task_name, task_cls, reasons) in enumerate(matches, 1):
        # Highlight the matching parts
        description = (task_cls.__doc__ or "No description").split('\n')[0]
        
        reason_text = ", ".join(reasons)
        rprint(f"\n[bold cyan]{i}. {task_name}[/bold cyan] [dim](matched in: {reason_text})[/dim]")
        rprint(f"   [green]{description}[/green]")
        rprint(f"   [dim]Module: {task_cls.__module__.split('.')[-1]}[/dim]")
    
    rprint(f"\n[dim]💡 Use 'sentinelx info <task_name>' for detailed information[/dim]")
    rprint(f"[dim]💡 Use 'sentinelx run <task_name>' to execute a task[/dim]")

@app.command()
def validate(
    task: Optional[str] = typer.Argument(None, help="Specific task to validate (optional)"),
    config: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file to validate"),
    check_deps: bool = typer.Option(True, "--check-deps", help="Check external dependencies"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Validate tasks and configuration."""
    rprint("[bold blue]🔍 SentinelX Validation Report[/bold blue]")
    rprint("─" * 50)
    
    issues = []
    successes = []
    
    # Validate configuration
    try:
        ctx = Context.load(config if Path(config).exists() else None)
        successes.append(f"✅ Configuration loaded successfully")
        if verbose:
            rprint(f"[green]✅ Configuration loaded from {config if Path(config).exists() else 'defaults'}[/green]")
    except Exception as e:
        issues.append(f"❌ Configuration error: {e}")
        rprint(f"[red]❌ Configuration error: {e}[/red]")
    
    # Get tasks to validate
    if task:
        tasks_to_check = [task] if task in PluginRegistry.list_tasks() else []
        if not tasks_to_check:
            rprint(f"[red]❌ Task '{task}' not found[/red]")
            return
    else:
        tasks_to_check = PluginRegistry.list_tasks()
    
    # Validate each task
    task_results = {}
    for task_name in tasks_to_check:
        try:
            task_cls = PluginRegistry.get_task_class(task_name)
            if not task_cls:
                issues.append(f"❌ Task '{task_name}' class not found")
                continue
                
            # Basic validation
            has_execute = hasattr(task_cls, 'execute') and callable(getattr(task_cls, 'execute'))
            has_doc = bool(task_cls.__doc__ and task_cls.__doc__.strip())
            
            task_issues = []
            task_successes = []
            
            if has_execute:
                task_successes.append("Has execute method")
            else:
                task_issues.append("Missing execute method")
            
            if has_doc:
                task_successes.append("Has documentation")
            else:
                task_issues.append("Missing documentation")
            
            # Check for required parameters attribute
            if hasattr(task_cls, 'REQUIRED_PARAMS'):
                task_successes.append("Has parameter specification")
            
            task_results[task_name] = {
                'issues': task_issues,
                'successes': task_successes,
                'status': 'ok' if not task_issues else 'warning'
            }
            
        except Exception as e:
            issues.append(f"❌ Task '{task_name}' validation failed: {e}")
            task_results[task_name] = {
                'issues': [f"Validation failed: {e}"],
                'successes': [],
                'status': 'error'
            }
    
    # Display results
    if verbose or task:
        rprint(f"\n[bold]📋 Task Validation Results:[/bold]")
        for task_name, result in task_results.items():
            status_color = {"ok": "green", "warning": "yellow", "error": "red"}[result['status']]
            status_icon = {"ok": "✅", "warning": "⚠️", "error": "❌"}[result['status']]
            
            rprint(f"\n{status_icon} [bold]{task_name}[/bold] [{status_color}]{result['status'].upper()}[/{status_color}]")
            
            for success in result['successes']:
                rprint(f"  [green]✅ {success}[/green]")
            
            for issue in result['issues']:
                rprint(f"  [red]❌ {issue}[/red]")
    
    # Summary
    total_tasks = len(task_results)
    ok_tasks = sum(1 for r in task_results.values() if r['status'] == 'ok')
    warning_tasks = sum(1 for r in task_results.values() if r['status'] == 'warning')
    error_tasks = sum(1 for r in task_results.values() if r['status'] == 'error')
    
    rprint(f"\n[bold]📊 Summary:[/bold]")
    rprint(f"  Tasks validated: {total_tasks}")
    rprint(f"  [green]✅ OK: {ok_tasks}[/green]")
    if warning_tasks > 0:
        rprint(f"  [yellow]⚠️ Warnings: {warning_tasks}[/yellow]")
    if error_tasks > 0:
        rprint(f"  [red]❌ Errors: {error_tasks}[/red]")
    
    if issues:
        rprint(f"\n[bold red]🚨 Issues Found:{len(issues)}[/bold red]")
        for issue in issues:
            rprint(f"  {issue}")
    
    if not issues and not any(r['issues'] for r in task_results.values()):
        rprint(f"\n[bold green]🎉 All validations passed![/bold green]")
    
    rprint(f"\n[dim]💡 Use --verbose for detailed task validation results[/dim]")

@app.command()
def interactive(
    task: Optional[str] = typer.Argument(None, help="Task to run interactively (optional)")
):
    """Interactive task execution with guided parameter input."""
    tasks = PluginRegistry.list_tasks()
    
    if not tasks:
        rprint("[red]No tasks available[/red]")
        return
    
    # Task selection if not provided
    if not task:
        rprint("[bold blue]🎯 SentinelX Interactive Mode[/bold blue]")
        rprint("─" * 50)
        rprint("Select a task to run:\n")
        
        # Group tasks by category for better UX
        categories = {}
        for task_name in sorted(tasks):
            task_cls = PluginRegistry.get_task_class(task_name)
            if not task_cls:
                continue
                
            if any(x in task_name for x in ['slither', 'mythril', 'cvss']):
                cat = "Smart Contract Audit"
            elif any(x in task_name for x in ['shellcode', 'fuzzer', 'autopwn']):
                cat = "Exploit Development"
            elif any(x in task_name for x in ['chain', 'tx-replay', 'rwa']):
                cat = "Blockchain Security"
            elif any(x in task_name for x in ['c2', 'lateral', 'social']):
                cat = "Red Team Operations"
            elif any(x in task_name for x in ['memory', 'disk', 'forensic']):
                cat = "Digital Forensics"
            elif any(x in task_name for x in ['llm', 'prompt', 'ai']):
                cat = "AI Security"
            elif 'web' in task_name or 'static' in task_name.lower():
                cat = "Web Security"
            else:
                cat = "Other"
            
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((task_name, task_cls))
        
        # Display categorized tasks
        task_index = 1
        task_map = {}
        
        for cat_name, task_list in categories.items():
            if not task_list:
                continue
            rprint(f"[bold blue]{cat_name}:[/bold blue]")
            for task_name, task_cls in task_list:
                desc = (task_cls.__doc__ or "No description").split('\n')[0][:50]
                if len(desc) >= 50:
                    desc += "..."
                rprint(f"  {task_index:2d}. [cyan]{task_name}[/cyan] - {desc}")
                task_map[task_index] = task_name
                task_index += 1
            rprint()
        
        # Get user selection
        try:
            choice = typer.prompt("Enter task number", type=int)
            if choice not in task_map:
                rprint(f"[red]Invalid choice: {choice}[/red]")
                return
            task = task_map[choice]
        except (ValueError, typer.Abort):
            rprint("[yellow]Cancelled[/yellow]")
            return
    
    # Validate selected task
    task_cls = PluginRegistry.get_task_class(task)
    if not task_cls:
        rprint(f"[red]Task '{task}' not found[/red]")
        return
    
    rprint(f"\n[bold green]🎯 Running: {task}[/bold green]")
    rprint(f"[dim]{task_cls.__doc__ or 'No description'}[/dim]")
    rprint("─" * 50)
    
    # Interactive parameter collection
    params = {}
    
    # Check for predefined parameters
    required_params = getattr(task_cls, 'REQUIRED_PARAMS', [])
    optional_params = getattr(task_cls, 'OPTIONAL_PARAMS', [])
    
    if required_params:
        rprint("[bold red]Required Parameters:[/bold red]")
        for param in required_params:
            value = typer.prompt(f"  {param}")
            params[param] = value
    
    if optional_params:
        rprint("\n[bold yellow]Optional Parameters:[/bold yellow]")
        rprint("[dim](Press Enter to skip)[/dim]")
        for param in optional_params:
            value = typer.prompt(f"  {param}", default="", show_default=False)
            if value.strip():
                params[param] = value
    
    # Ask for additional parameters
    rprint("\n[bold blue]Additional Parameters:[/bold blue]")
    rprint("[dim](Enter parameter name and value, or press Enter to continue)[/dim]")
    
    while True:
        param_name = typer.prompt("Parameter name", default="", show_default=False)
        if not param_name.strip():
            break
        param_value = typer.prompt(f"Value for '{param_name}'")
        params[param_name] = param_value
    
    # Configuration options
    rprint("\n[bold blue]Execution Options:[/bold blue]")
    verbose = typer.confirm("Enable verbose logging?", default=False)
    output_format = typer.prompt("Output format", default="yaml", 
                                type=typer.Choice(["yaml", "json", "table"]))
    
    # Execute the task
    try:
        rprint(f"\n[bold green]🚀 Executing {task}...[/bold green]")
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Load context
        ctx = Context.load(None)  # Use default config
        
        # Create and run task
        task_instance = PluginRegistry.create(task, ctx=ctx, **params)
        
        with console.status(f"[bold green]Running {task}..."):
            result = asyncio.run(task_instance())
        
        rprint("[bold green]✅ Task completed successfully![/bold green]")
        rprint("─" * 50)
        
        # Display results
        if output_format == "json":
            rprint(json.dumps(result, indent=2, default=str))
        elif output_format == "table" and isinstance(result, dict):
            table = Table(title=f"Results: {task}")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in result.items():
                table.add_row(str(key), str(value))
            console.print(table)
        else:  # YAML
            rprint(yaml.dump(result, default_flow_style=False))
        
        # Ask if user wants to save results
        if typer.confirm("\nSave results to file?", default=False):
            filename = typer.prompt("Filename", default=f"{task}_results.yaml")
            with open(filename, 'w') as f:
                if filename.endswith('.json'):
                    json.dump(result, f, indent=2, default=str)
                else:
                    yaml.dump(result, f, default_flow_style=False)
            rprint(f"[green]Results saved to {filename}[/green]")
    
    except Exception as e:
        rprint(f"[red]❌ Task execution failed: {e}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()

@app.command()
def config(
    action: str = typer.Argument(..., help="Action: init, show, edit, validate"),
    file: str = typer.Option("config.yaml", "--file", "-f", help="Config file path")
):
    """Configuration management utilities."""
    config_path = Path(file)
    
    if action == "init":
        if config_path.exists():
            if not typer.confirm(f"Config file {file} exists. Overwrite?"):
                return
        
        rprint("[bold blue]🔧 Creating SentinelX Configuration[/bold blue]")
        rprint("─" * 50)
        
        # Interactive configuration creation
        config_data = {
            "version": "1.0",
            "debug": typer.confirm("Enable debug mode?", default=False),
            "log_level": typer.prompt("Log level", default="INFO", 
                                    type=typer.Choice(["DEBUG", "INFO", "WARNING", "ERROR"])),
            "output_dir": typer.prompt("Output directory", default="./outputs"),
            "temp_dir": typer.prompt("Temporary directory", default="./temp"),
        }
        
        # Task-specific configurations
        if typer.confirm("Configure blockchain settings?", default=False):
            config_data["blockchain"] = {
                "ethereum_rpc": typer.prompt("Ethereum RPC URL", default="https://mainnet.infura.io/v3/YOUR_KEY"),
                "polygon_rpc": typer.prompt("Polygon RPC URL", default="https://polygon-rpc.com"),
                "timeout": typer.prompt("RPC timeout (seconds)", default=30, type=int)
            }
        
        if typer.confirm("Configure OpenAI settings?", default=False):
            config_data["openai"] = {
                "api_key": typer.prompt("OpenAI API Key", hide_input=True),
                "model": typer.prompt("Default model", default="gpt-3.5-turbo"),
                "max_tokens": typer.prompt("Max tokens", default=1000, type=int)
            }
        
        # Save configuration
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        rprint(f"[green]✅ Configuration saved to {file}[/green]")
        
    elif action == "show":
        if not config_path.exists():
            rprint(f"[red]Config file {file} not found[/red]")
            return
        
        rprint(f"[bold blue]📋 Configuration: {file}[/bold blue]")
        rprint("─" * 50)
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Pretty print configuration
        def print_config(data, indent=0):
            for key, value in data.items():
                if isinstance(value, dict):
                    rprint(f"{'  ' * indent}[cyan]{key}:[/cyan]")
                    print_config(value, indent + 1)
                else:
                    rprint(f"{'  ' * indent}[cyan]{key}:[/cyan] {value}")
        
        print_config(config_data)
        
    elif action == "edit":
        if not config_path.exists():
            rprint(f"[red]Config file {file} not found. Use 'config init' first.[/red]")
            return
        
        import subprocess
        import os
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.call([editor, str(config_path)])
        
    elif action == "validate":
        if not config_path.exists():
            rprint(f"[red]Config file {file} not found[/red]")
            return
        
        try:
            ctx = Context.load(file)
            rprint("[green]✅ Configuration is valid[/green]")
        except Exception as e:
            rprint(f"[red]❌ Configuration error: {e}[/red]")
    
    else:
        rprint(f"[red]Unknown action: {action}[/red]")
        rprint("Available actions: init, show, edit, validate")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
