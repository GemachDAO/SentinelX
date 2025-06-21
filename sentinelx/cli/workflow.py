"""
Workflow CLI commands for SentinelX.
"""
import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, Any
import click
from ..core.context import Context
from ..core.registry import PluginRegistry
from ..core.workflow import WorkflowEngine

@click.group()
def workflow():
    """Workflow orchestration commands."""
    pass

@workflow.command()
@click.argument('workflow_file', type=click.Path(exists=True))
@click.option('--config', '-c', help='Configuration file path')
@click.option('--output', '-o', help='Output file for results')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'yaml']))
def run(workflow_file: str, config: str, output: str, output_format: str):
    """Run a workflow from a YAML/JSON file."""
    async def _run_workflow():
        # Initialize context and registry
        context = Context.load(Path(config) if config else None)
        registry = PluginRegistry()
        registry.discover_builtin_tasks()
        
        # Initialize workflow engine
        engine = WorkflowEngine(registry)
        
        # Load and execute workflow
        workflow_path = Path(workflow_file)
        workflow_def = await engine.load_workflow(workflow_path)
        
        click.echo(f"Executing workflow: {workflow_def.get('name', 'unnamed')}")
        
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
            click.echo(f"Results saved to {output}")
        else:
            click.echo(output_data)
        
        # Print summary
        click.echo(f"\nWorkflow Status: {result.status}")
        click.echo(f"Steps Completed: {len(result.steps_completed)}")
        click.echo(f"Duration: {result.total_duration:.2f}s")
        
        if result.errors:
            click.echo(f"Errors: {len(result.errors)}")
            for error in result.errors:
                click.echo(f"  - {error}")
    
    asyncio.run(_run_workflow())

@workflow.command()
@click.argument('output_file', type=click.Path())
def template(output_file: str):
    """Generate a workflow template file."""
    template_workflow = {
        "name": "security_assessment_workflow",
        "description": "Comprehensive security assessment workflow",
        "continue_on_error": True,
        "steps": [
            {
                "name": "contract_analysis",
                "task": "slither",
                "params": {
                    "contract_path": "test_contract.sol",
                    "format": "json"
                },
                "output_mapping": {}
            },
            {
                "name": "vulnerability_scoring",
                "task": "cvss",
                "params": {
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                },
                "depends_on": ["contract_analysis"]
            },
            {
                "name": "shellcode_generation",
                "task": "shellcode",
                "params": {
                    "arch": "amd64",
                    "payload": "/bin/sh"
                },
                "depends_on": ["vulnerability_scoring"]
            },
            {
                "name": "fuzzing_test",
                "task": "fuzzer",
                "params": {
                    "target": "test_binary",
                    "payload_type": "buffer_overflow"
                },
                "depends_on": ["shellcode_generation"]
            }
        ]
    }
    
    output_path = Path(output_file)
    if output_path.suffix.lower() in ['.yaml', '.yml']:
        with open(output_path, 'w') as f:
            yaml.dump(template_workflow, f, default_flow_style=False)
    else:
        with open(output_path, 'w') as f:
            json.dump(template_workflow, f, indent=2)
    
    click.echo(f"Workflow template created: {output_path}")

@workflow.command()
def list_templates():
    """List available workflow templates."""
    templates = [
        {
            "name": "smart_contract_audit",
            "description": "Complete smart contract security audit"
        },
        {
            "name": "web_app_assessment", 
            "description": "Web application security assessment"
        },
        {
            "name": "blockchain_investigation",
            "description": "Blockchain incident response and investigation"
        },
        {
            "name": "red_team_assessment",
            "description": "Red team engagement workflow"
        }
    ]
    
    click.echo("Available workflow templates:")
    for template in templates:
        click.echo(f"  - {template['name']}: {template['description']}")
