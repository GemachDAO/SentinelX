from __future__ import annotations
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import ssl
import secrets
import base64
import asyncio
import json
from typing import Dict, Any
from ..core.task import Task

class C2Server(Task):
    """Command & Control Server for red team operations"""
    
    async def run(self):
        """Start C2 server with encrypted communications"""
        host = self.params.get("host", "0.0.0.0")
        port = self.params.get("port", 4443)
        use_ssl = self.params.get("ssl", False)
        certfile = self.params.get("certfile")
        keyfile = self.params.get("keyfile") 
        
        app = FastAPI()
        
        # Active agent sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        @app.websocket("/agent")
        async def agent_endpoint(websocket: WebSocket):
            """Handle agent connections"""
            await websocket.accept()
            agent_id = secrets.token_hex(6)
            
            self.sessions[agent_id] = {
                "websocket": websocket,
                "connected_at": asyncio.get_running_loop().time(),
                "status": "active",
                "last_seen": asyncio.get_running_loop().time()
            }
            
            try:
                while True:
                    # Receive agent data
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Update last seen
                    self.sessions[agent_id]["last_seen"] = asyncio.get_running_loop().time()
                    
                    # Process agent message
                    response = await self._process_agent_message(agent_id, message)
                    
                    # Send response to agent
                    await websocket.send_text(json.dumps(response))
                    
            except WebSocketDisconnect:
                self.sessions[agent_id]["status"] = "disconnected"
                del self.sessions[agent_id]
                
        @app.get("/admin/agents")
        async def list_agents():
            """List active agents"""
            return {
                "agents": {
                    aid: {
                        "status": info["status"],
                        "last_seen": info["last_seen"],
                        "connected_at": info["connected_at"]
                    }
                    for aid, info in self.sessions.items()
                }
            }
            
        @app.post("/admin/task/{agent_id}")
        async def send_task(agent_id: str, task: dict):
            """Send task to specific agent"""
            if agent_id not in self.sessions:
                return {"error": "Agent not found"}
                
            try:
                ws = self.sessions[agent_id]["websocket"]
                await ws.send_text(json.dumps({
                    "type": "task",
                    "command": task.get("command"),
                    "args": task.get("args", [])
                }))
                return {"status": "task_sent", "agent_id": agent_id}
            except Exception as e:
                return {"error": str(e)}
        
        # Configure SSL if requested
        ssl_context = None
        if use_ssl and certfile:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile, keyfile)
        
        # Start server
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            ssl_keyfile=keyfile if use_ssl else None,
            ssl_certfile=certfile if use_ssl else None
        )
        
        server = uvicorn.Server(config)
        
        # Run server in background for testing
        if self.params.get("test", False):
            # Return server configuration for testing
            return {
                "status": "configured",
                "server_mode": "test",
                "host": host,
                "port": port,
                "ssl_enabled": use_ssl,
                "agents_endpoint": f"{'wss' if use_ssl else 'ws'}://{host}:{port}/agent",
                "admin_endpoint": f"{'https' if use_ssl else 'http'}://{host}:{port}/admin"
            }
        else:
            # Start the server (blocking)
            await server.serve()
            
    async def _process_agent_message(self, agent_id: str, message: dict) -> dict:
        """Process message from agent"""
        msg_type = message.get("type")
        
        if msg_type == "heartbeat":
            return {"type": "ack", "timestamp": asyncio.get_running_loop().time()}
        elif msg_type == "result":
            return {"type": "ack", "received": True}
        elif msg_type == "error":
            return {"type": "ack", "error_logged": True}
        else:
            return {"type": "unknown", "message": "Unknown message type"}
