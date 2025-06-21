"""
FastAPI application factory and configuration for SentinelX Web API.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from ..core.registry import PluginRegistry
from ..core.context import Context
from ..core.utils import logger
from .models import (
    TaskListResponse, TaskInfoResponse, TaskExecutionRequest, TaskExecutionResponse,
    WorkflowListResponse, WorkflowExecutionRequest, WorkflowExecutionResponse,
    ReportListResponse, ExecutionStatus, WebSocketMessage
)
from .connection_manager import ConnectionManager

# Global connection manager for WebSocket connections
connection_manager = ConnectionManager()

# Global execution tracking
active_executions: Dict[str, Dict[str, Any]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting SentinelX Web API")
    PluginRegistry.discover()
    logger.info(f"Discovered {len(PluginRegistry.list_tasks())} tasks")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SentinelX Web API")

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="SentinelX API",
        description="Enterprise Security Framework Web API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # CORS middleware for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Security
    security = HTTPBearer(auto_error=False)
    
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Simple token authentication (to be enhanced with real auth)."""
        if not credentials:
            return {"user": "anonymous", "role": "user"}
        # TODO: Implement real JWT token validation
        return {"user": "admin", "role": "admin"}
    
    # Task Management Endpoints
    @app.get("/api/v1/tasks", response_model=TaskListResponse)
    async def list_tasks(user=Depends(get_current_user)):
        """List all available tasks."""
        try:
            tasks = PluginRegistry.list_tasks()
            task_list = []
            
            for task_name in tasks:
                task_cls = PluginRegistry.get_task(task_name)
                if task_cls:
                    task_list.append({
                        "name": task_name,
                        "description": getattr(task_cls, "__doc__", "").strip().split('\n')[0] if task_cls.__doc__ else "",
                        "category": getattr(task_cls, "category", "unknown"),
                        "parameters": getattr(task_cls, "parameters", {}),
                        "enabled": True
                    })
            
            return TaskListResponse(
                tasks=task_list,
                total=len(task_list),
                message="Tasks retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")
    
    @app.get("/api/v1/tasks/{task_name}/info", response_model=TaskInfoResponse)
    async def get_task_info(task_name: str, user=Depends(get_current_user)):
        """Get detailed information about a specific task."""
        try:
            task_cls = PluginRegistry.get_task(task_name)
            if not task_cls:
                raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found")
            
            return TaskInfoResponse(
                name=task_name,
                description=getattr(task_cls, "__doc__", "").strip() if task_cls.__doc__ else "",
                category=getattr(task_cls, "category", "unknown"),
                parameters=getattr(task_cls, "parameters", {}),
                examples=getattr(task_cls, "examples", []),
                enabled=True,
                version="1.0.0"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting task info for {task_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get task info: {str(e)}")
    
    @app.post("/api/v1/tasks/{task_name}/run", response_model=TaskExecutionResponse)
    async def execute_task(
        task_name: str, 
        request: TaskExecutionRequest,
        user=Depends(get_current_user)
    ):
        """Execute a task with given parameters."""
        execution_id = str(uuid.uuid4())
        
        try:
            # Get task class
            task_cls = PluginRegistry.get_task(task_name)
            if not task_cls:
                raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found")
            
            # Create context and task instance
            context = Context()
            if request.config:
                context.config.update(request.config)
            
            task_instance = task_cls(context)
            
            # Track execution
            active_executions[execution_id] = {
                "task_name": task_name,
                "status": "running",
                "start_time": datetime.utcnow(),
                "progress": 0
            }
            
            # Notify WebSocket clients
            await connection_manager.broadcast({
                "type": "execution_started",
                "execution_id": execution_id,
                "task_name": task_name,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Execute task asynchronously
            asyncio.create_task(execute_task_async(execution_id, task_instance, request.parameters))
            
            return TaskExecutionResponse(
                execution_id=execution_id,
                task_name=task_name,
                status="started",
                message="Task execution started",
                start_time=datetime.utcnow()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")
            active_executions[execution_id] = {
                "task_name": task_name,
                "status": "failed",
                "start_time": datetime.utcnow(),
                "error": str(e)
            }
            raise HTTPException(status_code=500, detail=f"Failed to execute task: {str(e)}")
    
    @app.get("/api/v1/executions/{execution_id}/status", response_model=ExecutionStatus)
    async def get_execution_status(execution_id: str, user=Depends(get_current_user)):
        """Get the status of a task execution."""
        if execution_id not in active_executions:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        execution = active_executions[execution_id]
        return ExecutionStatus(
            execution_id=execution_id,
            task_name=execution["task_name"],
            status=execution["status"],
            progress=execution.get("progress", 0),
            start_time=execution["start_time"],
            end_time=execution.get("end_time"),
            result=execution.get("result"),
            error=execution.get("error")
        )
    
    # Workflow Management Endpoints
    @app.get("/api/v1/workflows", response_model=WorkflowListResponse)
    async def list_workflows(user=Depends(get_current_user)):
        """List available workflow templates."""
        # TODO: Implement workflow template discovery
        workflows = [
            {
                "name": "basic_audit",
                "description": "Basic security audit workflow",
                "template": "audit",
                "steps": ["web2-static", "cvss"]
            },
            {
                "name": "smart_contract_audit", 
                "description": "Comprehensive smart contract security audit",
                "template": "smart_contract",
                "steps": ["slither", "mythril", "cvss"]
            }
        ]
        
        return WorkflowListResponse(
            workflows=workflows,
            total=len(workflows),
            message="Workflows retrieved successfully"
        )
    
    @app.post("/api/v1/workflows/run", response_model=WorkflowExecutionResponse)
    async def execute_workflow(
        request: WorkflowExecutionRequest,
        user=Depends(get_current_user)
    ):
        """Execute a workflow."""
        execution_id = str(uuid.uuid4())
        
        # TODO: Implement workflow execution using existing workflow engine
        return WorkflowExecutionResponse(
            execution_id=execution_id,
            workflow_name=request.workflow_name,
            status="started",
            message="Workflow execution started",
            start_time=datetime.utcnow()
        )
    
    # Report Management Endpoints
    @app.get("/api/v1/reports", response_model=ReportListResponse)
    async def list_reports(user=Depends(get_current_user)):
        """List generated reports."""
        # TODO: Implement report listing from filesystem
        reports = []
        
        return ReportListResponse(
            reports=reports,
            total=len(reports),
            message="Reports retrieved successfully"
        )
    
    # WebSocket Endpoint
    @app.websocket("/ws/execution")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time execution updates."""
        await connection_manager.connect(websocket)
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                # Echo back for heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
        except WebSocketDisconnect:
            connection_manager.disconnect(websocket)
    
    # Health Check
    @app.get("/api/v1/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "tasks_loaded": len(PluginRegistry.list_tasks())
        }
    
    # Static files for frontend (when built)
    try:
        app.mount("/", StaticFiles(directory="sentinelx/web/static", html=True), name="static")
    except RuntimeError:
        # Static directory doesn't exist yet
        pass
    
    return app

async def execute_task_async(execution_id: str, task_instance, parameters: Dict[str, Any]):
    """Execute task asynchronously and update status."""
    try:
        # Update progress
        active_executions[execution_id]["progress"] = 25
        await connection_manager.broadcast({
            "type": "execution_progress",
            "execution_id": execution_id,
            "progress": 25
        })
        
        # Execute task
        result = await asyncio.get_event_loop().run_in_executor(
            None, task_instance.execute, parameters
        )
        
        # Update completion
        active_executions[execution_id].update({
            "status": "completed",
            "progress": 100,
            "end_time": datetime.utcnow(),
            "result": result
        })
        
        await connection_manager.broadcast({
            "type": "execution_completed",
            "execution_id": execution_id,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Task execution {execution_id} failed: {e}")
        active_executions[execution_id].update({
            "status": "failed",
            "progress": 0,
            "end_time": datetime.utcnow(),
            "error": str(e)
        })
        
        await connection_manager.broadcast({
            "type": "execution_failed",
            "execution_id": execution_id,
            "error": str(e)
        })

# Create the app instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
