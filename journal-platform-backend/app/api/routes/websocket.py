"""
WebSocket Manager for Real-time AI Generation Progress
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, List[str]] = {}  # user_id -> [connection_ids]

    async def connect(self, websocket: WebSocket, connection_id: str, user_id: int):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)

    def disconnect(self, connection_id: str, user_id: int):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from user connections
        if user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except Exception:
                # Connection closed, remove it
                self.disconnect(connection_id, None)

    async def send_user_message(self, message: dict, user_id: int):
        """Send message to all connections for a user"""
        if user_id in self.user_connections:
            disconnected = []
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_text(json.dumps(message))
                    except Exception:
                        disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                self.disconnect(connection_id, user_id)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected.append(connection_id)

        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id, None)


# Global manager instance
manager = ConnectionManager()