"""
Theme Engine API Routes
Phase 3.3: Core API Services Implementation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user, get_db
from app.services.theme_service import ThemeService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/themes", tags=["Theme Engine"])

# Pydantic models for request/response
class ThemeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_premium: bool
    is_seasonal: bool
    season: Optional[str] = None
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    border_color: str
    preview_url: Optional[str] = None
    cover_templates: Optional[List[dict]] = None
    created_at: str
    updated_at: str

class ThemeListResponse(BaseModel):
    themes: List[ThemeResponse]
    pagination: Dict[str, Any]

class ThemeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Theme name")
    description: Optional[str] = Field(None, max_length=500, description="Theme description")
    category: str = Field(..., description="Theme category")
    primary_color: str = Field("#000000", description="Primary color in hex format")
    secondary_color: str = Field("#FFFFFF", description="Secondary color in hex format")
    accent_color: str = Field("#007BFF", description="Accent color in hex format")
    background_color: str = Field("#FFFFFF", description="Background color in hex format")
    text_color: str = Field("#333333", description="Text color in hex format")
    border_color: str = Field("#E0E0E0", description="Border color in hex format")

class ThemeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Theme name")
    description: Optional[str] = Field(None, max_length=500, description="Theme description")
    category: Optional[str] = Field(None, description="Theme category")
    primary_color: Optional[str] = Field(None, description="Primary color in hex format")
    secondary_color: Optional[str] = Field(None, description="Secondary color in hex format")
    accent_color: Optional[str] = Field(None, description="Accent color in hex format")
    background_color: Optional[str] = Field(None, description="Background color in hex format")
    text_color: Optional[str] = Field(None, description="Text color in hex format")
    border_color: Optional[str] = Field(None, description="Border color in hex format")

class CustomThemeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Custom theme name")
    description: Optional[str] = Field(None, max_length=500, description="Theme description")
    primary_color: str = Field(..., description="Primary color in hex format")
    secondary_color: str = Field(..., description="Secondary color in hex format")
    accent_color: str = Field(..., description="Accent color in hex format")
    background_color: str = Field(..., description="Background color in hex format")
    text_color: str = Field(..., description="Text color in hex format")
    border_color: str = Field(..., description="Border color in hex format")

class ThemePreferenceUpdate(BaseModel):
    theme_id: int = Field(..., description="Theme ID to set as preference")
    is_favorite: bool = Field(False, description="Mark theme as favorite")

@router.get("/", response_model=ThemeListResponse)
async def get_themes(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=50),
    category: Optional[str] = Query(None),
    is_premium: Optional[bool] = Query(None),
    is_seasonal: Optional[bool] = Query(None),
    season: Optional[str] = Query(None)
):
    """Get all available themes with filtering and pagination"""
    try:
        theme_service = ThemeService(db)
        result = await theme_service.get_all_themes(
            user_id=current_user["id"],
            category=category,
            is_premium=is_premium,
            is_seasonal=is_seasonal,
            season=season,
            limit=limit,
            skip=skip
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get themes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve themes"
        )

@router.get("/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific theme by ID"""
    try:
        theme_service = ThemeService(db)
        result = await theme_service.get_theme_by_id(
            theme_id=theme_id,
            user_id=current_user["id"]
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get theme {theme_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve theme"
        )

@router.post("/", response_model=ThemeResponse, status_code=201)
async def create_theme(
    theme_data: ThemeCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new theme (admin only)"""
    try:
        # Check if user is admin (TODO: implement role-based access)
        # For now, allow all users to create themes

        theme_service = ThemeService(db)
        result = await theme_service.create_custom_theme(
            user_id=current_user["id"],
            name=theme_data.name,
            description=theme_data.description,
            category=theme_data.category,
            primary_color=theme_data.primary_color,
            secondary_color=theme_data.secondary_color,
            accent_color=theme_data.accent_color,
            background_color=theme_data.background_color,
            text_color=theme_data.text_color,
            border_color=theme_data.border_color
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to create theme: {e}")
        raise HTTPException(
            status_code=500,
            detail="Theme creation failed due to internal error"
        )

@router.put("/{theme_id}", response_model=ThemeResponse, status_code=200)
async def update_theme(
    theme_id: int,
    theme_data: ThemeUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update theme (admin only)"""
    try:
        # Check if user is admin (TODO: implement role-based access)
        # For now, allow all users to update themes

        # This would be implemented to update theme properties
        # For now, return not implemented response
        raise HTTPException(
            status_code=501,
            detail="Theme update not implemented yet"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to update theme {theme_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Theme update failed due to internal error"
        )

@router.delete("/{theme_id}", status_code=204)
async def delete_theme(
    theme_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete theme (admin only)"""
    try:
        # Check if user is admin (TODO: implement role-based access)
        # For now, allow all users to delete themes

        # This would be implemented to delete theme
        # For now, return not implemented response
        raise HTTPException(
            status_code=501,
            detail="Theme deletion not implemented yet"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to delete theme {theme_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Theme deletion failed due to internal error"
        )

@router.post("/custom", response_model=ThemeResponse, status_code=201)
async def create_custom_theme(
    theme_data: CustomThemeCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a custom theme for the user"""
    try:
        theme_service = ThemeService(db)
        result = await theme_service.create_custom_theme(
            user_id=current_user["id"],
            name=theme_data.name,
            description=theme_data.description,
            primary_color=theme_data.primary_color,
            secondary_color=theme_data.secondary_color,
            accent_color=theme_data.accent_color,
            background_color=theme_data.background_color,
            text_color=theme_data.text_color,
            border_color=theme_data.border_color
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to create custom theme: {e}")
        raise HTTPException(
            status_code=500,
            detail="Custom theme creation failed due to internal error"
        )

@router.get("/user/preferences", response_model=Dict[str, Any])
async def get_user_theme_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's theme preferences and usage"""
    try:
        theme_service = ThemeService(db)
        result = await theme_service.get_user_theme_preferences(
            user_id=current_user["id"]
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get user theme preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve theme preferences"
        )

@router.put("/user/preferences", response_model=Dict[str, Any])
async def update_theme_preference(
    preference_data: ThemePreferenceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's theme preference"""
    try:
        theme_service = ThemeService(db)
        result = await theme_service.update_user_theme_preference(
            user_id=current_user["id"],
            theme_id=preference_data.theme_id,
            is_favorite=preference_data.is_favorite
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to update theme preference: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update theme preference"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_theme_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get theme usage statistics (admin only)"""
    try:
        # Check if user is admin (TODO: implement role-based access)
        theme_service = ThemeService(db)
        result = await theme_service.get_theme_statistics(
            user_id=current_user["id"]
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get theme statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve theme statistics"
        )