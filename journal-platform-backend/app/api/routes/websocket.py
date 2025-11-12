"""
Enhanced WebSocket Manager for Real-time CrewAI Progress Tracking
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import asyncio
import uuid
from enum import Enum


class MessageType(Enum):
    """Message types for WebSocket communications"""
    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"
    WORKFLOW_ERROR = "workflow_error"
    WORKFLOW_CANCELLED = "workflow_cancelled"

    AGENT_START = "agent_start"
    AGENT_PROGRESS = "agent_progress"
    AGENT_COMPLETE = "agent_complete"
    AGENT_ERROR = "agent_error"

    STEP_START = "step_start"
    STEP_PROGRESS = "step_progress"
    STEP_COMPLETE = "step_complete"

    SYSTEM_NOTIFICATION = "system_notification"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class AgentProgressTracker:
    """Track detailed progress for individual agents"""

    def __init__(self, agent_name: str, total_steps: int = 100):
        self.agent_name = agent_name
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = datetime.now()
        self.subtasks = []
        self.current_subtask = None
        self.estimated_completion = None
        self.progress_log = []

    def update_progress(self, step: int, message: str = None):
        """Update agent progress"""
        self.current_step = max(0, min(step, self.total_steps))
        if message:
            self.progress_log.append({
                "step": self.current_step,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })

    def start_subtask(self, subtask_name: str, steps: int = 1):
        """Start a new subtask"""
        self.current_subtask = {
            "name": subtask_name,
            "steps": steps,
            "completed": 0,
            "start_time": datetime.now()
        }
        self.subtasks.append(self.current_subtask)

    def complete_subtask(self):
        """Mark current subtask as complete"""
        if self.current_subtask:
            self.current_subtask["completed"] = self.current_subtask["steps"]
            self.current_subtask["end_time"] = datetime.now()

    def get_progress_data(self) -> Dict[str, Any]:
        """Get current progress data"""
        return {
            "agent_name": self.agent_name,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress_percentage": round((self.current_step / self.total_steps) * 100, 1),
            "current_subtask": self.current_subtask["name"] if self.current_subtask else None,
            "completed_subtasks": len([s for s in self.subtasks if s.get("completed") == s.get("steps")]),
            "total_subtasks": len(self.subtasks),
            "start_time": self.start_time.isoformat(),
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None
        }


class EnhancedConnectionManager:
    """Enhanced WebSocket connection manager with advanced progress tracking"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, List[str]] = {}  # user_id -> [connection_ids]
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}  # connection_id -> metadata
        self.workflow_subscribers: Dict[str, List[str]] = {}  # workflow_id -> [connection_ids]
        self.agent_trackers: Dict[str, AgentProgressTracker] = {}  # agent_id -> progress tracker

        # Background task for heartbeat and cleanup
        self._heartbeat_task = None

    async def connect(self, websocket: WebSocket, connection_id: str, user_id: int, metadata: Dict[str, Any] = None):
        """Accept and store WebSocket connection with metadata"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket

        # Store connection metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            **(metadata or {})
        }

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)

        # Start heartbeat if not running
        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    def disconnect(self, connection_id: str, user_id: Optional[int] = None):
        """Remove WebSocket connection and cleanup subscriptions"""
        # Remove from active connections
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from user connections
        user_id = user_id or self.connection_metadata.get(connection_id, {}).get("user_id")
        if user_id and user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove from workflow subscriptions
        for workflow_id, subscribers in self.workflow_subscribers.items():
            if connection_id in subscribers:
                subscribers.remove(connection_id)

        # Clean up metadata
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]

    async def subscribe_to_workflow(self, connection_id: str, workflow_id: str):
        """Subscribe connection to specific workflow updates"""
        if workflow_id not in self.workflow_subscribers:
            self.workflow_subscribers[workflow_id] = []

        if connection_id not in self.workflow_subscribers[workflow_id]:
            self.workflow_subscribers[workflow_id].append(connection_id)

    async def unsubscribe_from_workflow(self, connection_id: str, workflow_id: str):
        """Unsubscribe connection from workflow updates"""
        if workflow_id in self.workflow_subscribers:
            if connection_id in self.workflow_subscribers[workflow_id]:
                self.workflow_subscribers[workflow_id].remove(connection_id)

    async def send_message(self, message: Dict[str, Any], connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                # Add timestamp if not present
                if "timestamp" not in message:
                    message["timestamp"] = datetime.now().isoformat()

                await self.active_connections[connection_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                print(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
                return False
        return False

    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection (legacy compatibility)"""
        await self.send_message(message, connection_id)

    async def send_workflow_update(self, workflow_id: str, message: Dict[str, Any]):
        """Send update to all subscribers of a workflow"""
        if workflow_id in self.workflow_subscribers:
            disconnected = []
            for connection_id in self.workflow_subscribers[workflow_id]:
                if not await self.send_message(message, connection_id):
                    disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                self.disconnect(connection_id)

    async def send_user_message(self, message: dict, user_id: int):
        """Send message to all connections for a user"""
        if user_id in self.user_connections:
            disconnected = []
            for connection_id in self.user_connections[user_id]:
                if not await self.send_message(message, connection_id):
                    disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                self.disconnect(connection_id)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection_id in self.active_connections:
            if not await self.send_message(message, connection_id):
                disconnected.append(connection_id)

        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)

    def get_agent_tracker(self, agent_id: str, create_if_missing: bool = True) -> Optional[AgentProgressTracker]:
        """Get or create agent progress tracker"""
        if agent_id not in self.agent_trackers and create_if_missing:
            self.agent_trackers[agent_id] = AgentProgressTracker(agent_id)
        return self.agent_trackers.get(agent_id)

    async def update_agent_progress(self, workflow_id: str, agent_id: str, step: int, message: str = None):
        """Update agent progress and notify subscribers"""
        tracker = self.get_agent_tracker(agent_id)
        if tracker:
            tracker.update_progress(step, message)

            # Send update to workflow subscribers
            await self.send_workflow_update(workflow_id, {
                "type": MessageType.AGENT_PROGRESS.value,
                "workflow_id": workflow_id,
                "agent_id": agent_id,
                "progress": tracker.get_progress_data(),
                "message": message
            })

    async def start_agent_subtask(self, workflow_id: str, agent_id: str, subtask_name: str, steps: int = 1):
        """Start a new subtask for an agent"""
        tracker = self.get_agent_tracker(agent_id)
        if tracker:
            tracker.start_subtask(subtask_name, steps)

            await self.send_workflow_update(workflow_id, {
                "type": MessageType.STEP_START.value,
                "workflow_id": workflow_id,
                "agent_id": agent_id,
                "subtask": subtask_name,
                "steps": steps
            })

    async def complete_agent_subtask(self, workflow_id: str, agent_id: str):
        """Complete current subtask for an agent"""
        tracker = self.get_agent_tracker(agent_id)
        if tracker:
            tracker.complete_subtask()

            await self.send_workflow_update(workflow_id, {
                "type": MessageType.STEP_COMPLETE.value,
                "workflow_id": workflow_id,
                "agent_id": agent_id,
                "progress": tracker.get_progress_data()
            })

    async def _heartbeat_loop(self):
        """Background task to send heartbeats and cleanup connections"""
        while True:
            try:
                # Send heartbeat to all connections
                heartbeat_message = {
                    "type": MessageType.HEARTBEAT.value,
                    "timestamp": datetime.now().isoformat(),
                    "active_connections": len(self.active_connections)
                }

                await self.broadcast(heartbeat_message)

                # Check for stale connections (no heartbeat for 5 minutes)
                now = datetime.now()
                stale_connections = []

                for connection_id, metadata in self.connection_metadata.items():
                    last_heartbeat = datetime.fromisoformat(metadata.get("last_heartbeat", metadata.get("connected_at")))
                    if (now - last_heartbeat).total_seconds() > 300:  # 5 minutes
                        stale_connections.append(connection_id)

                # Clean up stale connections
                for connection_id in stale_connections:
                    print(f"Cleaning up stale connection: {connection_id}")
                    self.disconnect(connection_id)

                await asyncio.sleep(30)  # Heartbeat every 30 seconds

            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(30)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "user_connections": len(self.user_connections),
            "workflow_subscriptions": len(self.workflow_subscribers),
            "agent_trackers": len(self.agent_trackers)
        }

    async def shutdown(self):
        """Cleanup and shutdown the connection manager"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass


# Global enhanced manager instance
manager = EnhancedConnectionManager()