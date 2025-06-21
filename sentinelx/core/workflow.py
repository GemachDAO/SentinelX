"""
Workflow orchestration system for chaining SentinelX tasks.
"""
from __future__ import annotations
import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from .context import Context
from .registry import PluginRegistry
from .task import Task
import logging

logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    name: str
    task: str
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    condition: Optional[str] = None

@dataclass
class WorkflowResult:
    """Results from workflow execution."""
    workflow_name: str
    status: str
    steps_completed: List[str]
    step_results: Dict[str, Any]
    total_duration: float
    errors: List[str] = field(default_factory=list)

class WorkflowEngine:
    """Orchestrates execution of multi-step security workflows."""
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.logger = logging.getLogger(__name__)
    
    async def load_workflow(self, workflow_path: Path) -> Dict[str, Any]:
        """Load workflow definition from YAML file."""
        try:
            with open(workflow_path, 'r') as f:
                if workflow_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load workflow {workflow_path}: {e}")
            raise
    
    async def execute_workflow(self, workflow_def: Dict[str, Any], context: Context) -> WorkflowResult:
        """Execute a complete workflow with dependency management."""
        workflow_name = workflow_def.get('name', 'unnamed_workflow')
        steps = workflow_def.get('steps', [])
        
        self.logger.info(f"Starting workflow: {workflow_name}")
        
        # Parse workflow steps
        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(
                name=step_def['name'],
                task=step_def['task'],
                params=step_def.get('params', {}),
                depends_on=step_def.get('depends_on', []),
                output_mapping=step_def.get('output_mapping', {}),
                condition=step_def.get('condition')
            )
            workflow_steps.append(step)
        
        # Execute workflow with dependency resolution
        start_time = asyncio.get_event_loop().time()
        step_results = {}
        completed_steps = []
        errors = []
        
        try:
            # Topological sort for dependency resolution
            execution_order = self._resolve_dependencies(workflow_steps)
            
            for step in execution_order:
                if not self._should_execute_step(step, step_results):
                    self.logger.info(f"Skipping step {step.name} due to condition")
                    continue
                
                # Prepare step parameters with data from previous steps
                step_params = self._prepare_step_params(step, step_results, context)
                
                # Execute the step
                self.logger.info(f"Executing step: {step.name} (task: {step.task})")
                
                try:
                    task_result = await self._execute_step(step.task, step_params, context)
                    step_results[step.name] = task_result
                    completed_steps.append(step.name)
                    
                    self.logger.info(f"Step {step.name} completed successfully")
                    
                except Exception as e:
                    error_msg = f"Step {step.name} failed: {str(e)}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                    
                    # Check if workflow should continue on error
                    if not workflow_def.get('continue_on_error', False):
                        break
            
            duration = asyncio.get_event_loop().time() - start_time
            status = "completed" if not errors else ("partial" if completed_steps else "failed")
            
            result = WorkflowResult(
                workflow_name=workflow_name,
                status=status,
                steps_completed=completed_steps,
                step_results=step_results,
                total_duration=duration,
                errors=errors
            )
            
            self.logger.info(f"Workflow {workflow_name} {status} in {duration:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            duration = asyncio.get_event_loop().time() - start_time
            return WorkflowResult(
                workflow_name=workflow_name,
                status="failed",
                steps_completed=completed_steps,
                step_results=step_results,
                total_duration=duration,
                errors=errors + [str(e)]
            )
    
    def _resolve_dependencies(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Resolve step dependencies using topological sort."""
        # Simple dependency resolution - in production would use proper topological sort
        step_map = {step.name: step for step in steps}
        resolved = []
        remaining = steps.copy()
        
        while remaining:
            ready_steps = [step for step in remaining if all(dep in [s.name for s in resolved] for dep in step.depends_on)]
            
            if not ready_steps:
                raise ValueError("Circular dependency detected in workflow")
            
            for step in ready_steps:
                resolved.append(step)
                remaining.remove(step)
        
        return resolved
    
    def _should_execute_step(self, step: WorkflowStep, step_results: Dict[str, Any]) -> bool:
        """Check if step should be executed based on conditions."""
        if not step.condition:
            return True
        
        # Simple condition evaluation - in production would use proper expression parser
        try:
            # Example: "step1.status == 'success'"
            return eval(step.condition, {"__builtins__": {}}, step_results)
        except:
            self.logger.warning(f"Could not evaluate condition for step {step.name}: {step.condition}")
            return True
    
    def _prepare_step_params(self, step: WorkflowStep, step_results: Dict[str, Any], context: Context) -> Dict[str, Any]:
        """Prepare parameters for step execution, including data from previous steps."""
        params = step.params.copy()
        
        # Apply output mapping from previous steps
        for source_path, target_param in step.output_mapping.items():
            try:
                # Example: "step1.contract_path" -> get step1 results and extract contract_path
                if '.' in source_path:
                    step_name, field_path = source_path.split('.', 1)
                    if step_name in step_results:
                        value = self._extract_nested_value(step_results[step_name], field_path)
                        params[target_param] = value
            except Exception as e:
                self.logger.warning(f"Could not map {source_path} to {target_param}: {e}")
        
        return params
    
    def _extract_nested_value(self, data: Any, path: str) -> Any:
        """Extract nested value from data using dot notation."""
        if '.' not in path:
            return data.get(path) if isinstance(data, dict) else getattr(data, path, None)
        
        first, rest = path.split('.', 1)
        if isinstance(data, dict):
            return self._extract_nested_value(data.get(first, {}), rest)
        else:
            return self._extract_nested_value(getattr(data, first, {}), rest)
    
    async def _execute_step(self, task_name: str, params: Dict[str, Any], context: Context) -> Any:
        """Execute a single workflow step."""
        task_cls = self.registry.get_task(task_name)
        if not task_cls:
            raise ValueError(f"Task not found: {task_name}")
        
        # Create task instance with proper keyword arguments
        task_instance = task_cls(ctx=context, **params)
        
        # Validate and run task
        await task_instance.validate_params()
        return await task_instance.run()
