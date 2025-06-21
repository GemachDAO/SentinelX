"""
Pydantic models for SentinelX Web API requests and responses.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field

# Base Response Model
class BaseResponse(BaseModel):
    """Base response model with common fields."""
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Task Models
class TaskInfo(BaseModel):
    """Information about a single task."""
    name: str
    description: str
    category: str
    parameters: Dict[str, Any] = {}
    enabled: bool = True

class TaskListResponse(BaseResponse):
    """Response for listing tasks."""
    tasks: List[TaskInfo]
    total: int

class TaskInfoResponse(BaseResponse):
    """Detailed task information response."""
    name: str
    description: str
    category: str
    parameters: Dict[str, Any] = {}
    examples: List[Dict[str, Any]] = []
    enabled: bool = True
    version: str = "1.0.0"

class TaskExecutionRequest(BaseModel):
    """Request to execute a task."""
    parameters: Dict[str, Any] = {}
    config: Optional[Dict[str, Any]] = None
    async_execution: bool = True

class TaskExecutionResponse(BaseResponse):
    """Response from task execution."""
    execution_id: str
    task_name: str
    status: str
    start_time: datetime
    result: Optional[Dict[str, Any]] = None

class ExecutionStatus(BaseModel):
    """Status of a task execution."""
    execution_id: str
    task_name: str
    status: str  # running, completed, failed
    progress: int = 0  # 0-100
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Workflow Models
class WorkflowInfo(BaseModel):
    """Information about a workflow."""
    name: str
    description: str
    template: str
    steps: List[str]

class WorkflowListResponse(BaseResponse):
    """Response for listing workflows."""
    workflows: List[WorkflowInfo]
    total: int

class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow."""
    workflow_name: str
    parameters: Dict[str, Any] = {}
    config: Optional[Dict[str, Any]] = None

class WorkflowExecutionResponse(BaseResponse):
    """Response from workflow execution."""
    execution_id: str
    workflow_name: str
    status: str
    start_time: datetime
    steps: Optional[List[str]] = None

# Report Models
class ReportInfo(BaseModel):
    """Information about a generated report."""
    id: str
    name: str
    type: str  # html, pdf, json, markdown
    task_name: Optional[str] = None
    workflow_name: Optional[str] = None
    created_at: datetime
    file_size: int
    file_path: str

class ReportListResponse(BaseResponse):
    """Response for listing reports."""
    reports: List[ReportInfo]
    total: int

# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str
    execution_id: Optional[str] = None
    task_name: Optional[str] = None
    workflow_name: Optional[str] = None
    progress: Optional[int] = None
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# User Authentication Models
class UserInfo(BaseModel):
    """User information."""
    username: str
    role: str = "user"
    permissions: List[str] = []

class LoginRequest(BaseModel):
    """Login request."""
    username: str
    password: str

class LoginResponse(BaseResponse):
    """Login response."""
    token: str
    user: UserInfo
    expires_at: datetime

# System Status Models
class SystemHealth(BaseModel):
    """System health status."""
    status: str
    timestamp: datetime
    version: str
    tasks_loaded: int
    active_executions: int
    uptime_seconds: float

class SystemMetrics(BaseModel):
    """System performance metrics."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    request_count: int

# Error Models
class ErrorResponse(BaseModel):
    """Error response format."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
