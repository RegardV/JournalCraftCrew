"""
API Dependencies
Phase 3: Backend Development
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer as FastAPIHTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, AsyncGenerator
from datetime import datetime
import logging

from app.core.database import get_async_session
from app.api.routes import auth, users, projects, themes, export

logger = logging.getLogger(__name__)

# HTTP Bearer authentication for protected routes
class HTTPBearer(FastAPIHTTPBearer):
    """HTTP Bearer token authentication"""

    def __init__(self, auto_error: bool = False):
        super().__init__(
            scheme_name="Bearer",
            auto_error=auto_error,
            description="Bearer token authentication"
        )

async def __call__(self, request):
        credentials = await super().__call__(request)
        if not credentials or not credentials.scheme:
            raise HTTPException(
                status_code=403,
                detail="Invalid authentication scheme"
            )

        # TODO: Validate token against database
        return credentials

# Dependency function to get current authenticated user
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """Get current authenticated user from JWT token"""
    try:
        # Allow missing credentials for optional endpoints
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get auth service
        from app.services.auth_service import AuthService
        auth_service = AuthService(db)

        # Get user from token
        user = await auth_service.get_current_user_from_token(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription": user.subscription,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "preferences": user.preferences
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency function to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session for FastAPI dependencies"""
    async for session in get_async_session():
        yield session

# WebSocket authentication for real-time connections
async def get_current_user_ws(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """Get current authenticated user from WebSocket token"""
    try:
        if not token:
            raise HTTPException(
                status_code=401,
                detail="No authentication token provided"
            )

        # Get auth service
        from app.services.auth_service import AuthService
        auth_service = AuthService(db)

        # Get user from token
        user = await auth_service.get_current_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription": user.subscription,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "preferences": user.preferences
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

# Optional dependency function - doesn't raise exceptions for missing credentials
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """Get current authenticated user from JWT token (optional)"""
    try:
        # Return None for missing credentials
        if not credentials or not credentials.credentials:
            return None

        # Get auth service
        from app.services.auth_service import AuthService
        auth_service = AuthService(db)

        # Get user from token
        user = await auth_service.get_current_user_from_token(credentials.credentials)
        if not user:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription": user.subscription,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "preferences": user.preferences
        }

    except Exception as e:
        logger.warning(f"Optional authentication failed: {e}")
        return None