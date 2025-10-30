"""
Authentication API Routes
Phase 3.2: User Authentication & Authorization System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

from app.api.dependencies import get_current_user, get_db
from app.services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic models for request/response
class UserRegistration(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (8-128 characters)")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    profile_type: str = Field("personal_journaler", description="Profile type: 'personal_journaler' or 'content_creator'")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    subscription: str
    profile_type: str
    ai_credits: int
    library_access: bool
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class ChangePassword(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

class ResetPassword(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

class ForgotPassword(BaseModel):
    email: EmailStr = Field(..., description="Email address for password reset")

@router.post("/register", response_model=dict, status_code=201)
async def register(
    user_data: UserRegistration,
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            profile_type=user_data.profile_type
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Registration endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed due to internal error"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return tokens"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.authenticate_user(
            email=user_data.email,
            password=user_data.password
        )

        # Log successful login
        logger.info(f"User login successful: {user_data.email} from {request.client.host}")
        return result

    except HTTPException as e:
        # Log failed login attempt
        logger.warning(f"User login failed: {user_data.email} from {request.client.host}")
        raise e
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication failed due to internal error"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.refresh_access_token(
            refresh_token=token_data.refresh_token
        )
        logger.info(f"Token refreshed successfully")
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Token refresh failed due to internal error"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(**current_user)

@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user),
    request: Request
):
    """Logout user (invalidate tokens)"""
    try:
        # TODO: Implement proper token invalidation with Redis/blacklist
        logger.info(f"User logout: {current_user['email']} from {request.client.host}")
        return {"message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Logout failed due to internal error"
        )

@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify user email"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.verify_email(token)
        logger.info(f"Email verification attempted with token: {token}")
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Email verification failed due to internal error"
        )

@router.post("/forgot-password")
async def forgot_password(
    email_data: ForgotPassword,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.request_password_reset(
            email=email_data.email
        )
        logger.info(f"Password reset requested for: {email_data.email} from {request.client.host}")
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password reset request failed due to internal error"
        )

@router.post("/reset-password")
async def reset_password(
    reset_data: ResetPassword,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.reset_password(
            token=reset_data.token,
            new_password=reset_data.new_password
        )
        logger.info(f"Password reset attempted with token")
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password reset failed due to internal error"
        )

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    try:
        from app.core.security import password_manager
        from app.models.user import User
        from sqlalchemy import select
        from datetime import datetime

        # Get user to verify current password
        result = await db.execute(
            select(User).where(User.id == current_user["id"])
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        # Verify current password
        if not password_manager.verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )

        # Hash new password and update
        user.hashed_password = password_manager.hash_password(password_data.new_password)
        user.updated_at = datetime.utcnow()

        await db.commit()
        logger.info(f"Password changed for user: {current_user['email']}")
        return {"message": "Password changed successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password change failed due to internal error"
        )

# OAuth2 endpoints (placeholder for future implementation)
@router.get("/oauth/google")
async def google_oauth():
    """Google OAuth2 callback placeholder"""
    # TODO: Implement Google OAuth2 flow
    return {"message": "Google OAuth2 not implemented yet"}

@router.get("/oauth/github")
async def github_oauth():
    """GitHub OAuth callback placeholder"""
    # TODO: Implement GitHub OAuth2 flow
    return {"message": "GitHub OAuth2 not implemented yet"}