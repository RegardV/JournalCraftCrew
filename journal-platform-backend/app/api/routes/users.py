"""
Users API Routes
Phase 3: Backend Development
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models import User, UserSubscription
from app.api.dependencies import get_current_user, get_db

router = APIRouter(prefix="/users", tags=["User Management"])

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    preferences: Optional[dict] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription: Optional[UserSubscription] = None
    preferences: Optional[dict] = None

class UserPreferences(BaseModel):
    theme_preference: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_marketing: Optional[bool] = None
    notification_updates: Optional[bool] = None
    profile_visibility: Optional[str] = None
    share_analytics: Optional[bool] = None
    allow_collaboration: Optional[bool] = None

@router.get("/", response_model=List[UserResponse])
async def get_users(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get users list (admin only)"""
    # TODO: Implement admin check
    # For now, return empty list
    return []

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "subscription": current_user.subscription,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "preferences": current_user.preferences
    }

    return UserResponse(**user_data)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    # TODO: Implement user profile update in database
    # For now, return mock success response

    updated_user = current_user
    if user_update.full_name:
        updated_user.full_name = user_update.full_name
    if user_update.avatar_url:
        updated_user.avatar_url = user_update.avatar_url
    if user_update.subscription:
        updated_user.subscription = user_update.subscription
    if user_update.preferences:
        updated_user.preferences.update(user_update.preferences)

    # TODO: Save to database
    # updated_user.updated_at = datetime.utcnow()

    return UserResponse(**{
        "id": updated_user.id,
        "email": updated_user.email,
        "full_name": updated_user.full_name,
        "avatar_url": updated_user.avatar_url,
        "subscription": updated_user.subscription,
        "is_active": updated_user.is_active,
        "is_verified": updated_user.is_verified,
        "created_at": updated_user.created_at,
        "updated_at": updated_user.updated_at,
        "preferences": updated_user.preferences
    })

@router.post("/preferences", response_model=dict)
async def update_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    # TODO: Save preferences to database
    # For now, return success response

    if preferences:
        current_user.preferences.update(preferences.dict())
        # TODO: Save to database
        # current_user.updated_at = datetime.utcnow()

    return {
        "message": "Preferences updated successfully",
        "preferences": preferences.dict()
    }

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # TODO: Implement password change with proper validation
    # For now, return success response

    return {
        "message": "Password change functionality not implemented yet"
    }