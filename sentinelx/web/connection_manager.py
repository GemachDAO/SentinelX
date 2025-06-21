"""
WebSocket connection manager for real-time updates in SentinelX Web API.
"""
import json
from typing import List, Dict, Any
from fastapi import WebSocket
from ..core.utils import logger

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": None,
            "user_id": "anonymous",
            "subscriptions": []
        }
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected WebSocket clients."""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_subscribers(self, message: Dict[str, Any], subscription_type: str):
        """Broadcast to clients subscribed to a specific type of update."""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                metadata = self.connection_metadata.get(connection, {})
                subscriptions = metadata.get("subscriptions", [])
                
                if subscription_type in subscriptions or "all" in subscriptions:
                    await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to subscriber: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
    
    def subscribe_connection(self, websocket: WebSocket, subscription_type: str):
        """Subscribe a connection to specific update types."""
        if websocket in self.connection_metadata:
            subscriptions = self.connection_metadata[websocket].get("subscriptions", [])
            if subscription_type not in subscriptions:
                subscriptions.append(subscription_type)
                self.connection_metadata[websocket]["subscriptions"] = subscriptions
    
    def unsubscribe_connection(self, websocket: WebSocket, subscription_type: str):
        """Unsubscribe a connection from specific update types."""
        if websocket in self.connection_metadata:
            subscriptions = self.connection_metadata[websocket].get("subscriptions", [])
            if subscription_type in subscriptions:
                subscriptions.remove(subscription_type)
                self.connection_metadata[websocket]["subscriptions"] = subscriptions
