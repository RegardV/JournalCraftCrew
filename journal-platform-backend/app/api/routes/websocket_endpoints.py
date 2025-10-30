"""
WebSocket Endpoints for Real-time Communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from ...core.deps import get_db, get_current_user_ws
from ...models.user import User
from .websocket import manager

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time AI generation progress
    """
    # Generate unique connection ID
    connection_id = str(uuid.uuid4())

    # Verify user authentication (you might want to pass token as query param)
    try:
        # For now, we'll accept the connection and authenticate via token
        await manager.connect(websocket, connection_id, user_id)
    except Exception as e:
        await websocket.close(code=4001, reason=f"Connection failed: {str(e)}")
        return

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()

            # Handle client messages (e.g., ping, subscription requests)
            # For now, just echo back or handle as needed

    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
    except Exception as e:
        manager.disconnect(connection_id, user_id)


@router.websocket("/ws/job/{job_id}")
async def job_progress_websocket(
    websocket: WebSocket,
    job_id: str,
    token: str = Query(..., description="Authentication token")
):
    """
    WebSocket endpoint for specific job progress tracking
    """
    # Verify token and get user_id (implement token validation)
    # For now, we'll use a simple approach
    connection_id = str(uuid.uuid4())

    # Extract user_id from job_id format: gen_{user_id}_{timestamp}
    try:
        user_id = int(job_id.split('_')[1])
    except (IndexError, ValueError):
        await websocket.close(code=4000, reason="Invalid job ID format")
        return

    try:
        await manager.connect(websocket, connection_id, user_id)

        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connection_established",
            "job_id": job_id,
            "message": "Connected to job progress updates"
        }, connection_id)

    except Exception as e:
        await websocket.close(code=4001, reason=f"Connection failed: {str(e)}")
        return

    try:
        while True:
            # Keep connection alive for progress updates
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
    except Exception as e:
        manager.disconnect(connection_id, user_id)