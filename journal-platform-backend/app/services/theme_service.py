"""
Theme Engine Service
Phase 3.3: Core API Services Implementation
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.models.theme import Theme
from app.models.user import User
from app.core.database import get_async_session
import logging

logger = logging.getLogger(__name__)


class ThemeService:
    """Service for theme management and personalization"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_themes(
        self,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        is_premium: Optional[bool] = None,
        is_seasonal: Optional[bool] = None
        season: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """Get all available themes with filtering and pagination"""
        try:
            # Build base query
            query = select(Theme).where(Theme.is_active == True)

            # Apply filters
            if user_id is not None:
                # For now, return all themes (premium check later)
                pass
            if category:
                query = query.where(Theme.category == category)
            if is_premium is not None:
                query = query.where(Theme.is_premium == is_premium)
            if is_seasonal is not None:
                query = query.where(Theme.is_seasonal == is_seasonal)
            if season:
                query = query.where(Theme.season == season)

            # Add ordering
            query = query.order_by(Theme.name)

            # Apply pagination
            themes = await self.db.execute(
                query.offset(skip).limit(limit)
            )
            theme_list = themes.scalars().all()

            return {
                "themes": [
                    {
                        "id": theme.id,
                        "name": theme.name,
                        "description": theme.description,
                        "category": theme.category,
                        "is_premium": theme.is_premium,
                        "is_seasonal": theme.is_seasonal,
                        "season": theme.season,
                        "primary_color": theme.primary_color,
                        "secondary_color": theme.secondary_color,
                        "accent_color": theme.accent_color,
                        "background_color": theme.background_color,
                        "text_color": theme.text_color,
                        "border_color": theme.border_color,
                        "preview_url": theme.preview_url,
                        "cover_templates": theme.cover_templates,
                        "created_at": theme.created_at.isoformat(),
                        "updated_at": theme.updated_at.isoformat()
                    }
                    for theme in theme_list
                ],
                "pagination": {
                    "total": len(theme_list),
                    "skip": skip,
                    "limit": limit,
                    "has_more": skip + limit < len(theme_list)
                }
            }

        except Exception as e:
            logger.error(f"Failed to get themes: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve themes"
            )

    async def get_theme_by_id(
        self,
        theme_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get specific theme by ID"""
        try:
            query = select(Theme).where(
                and_(Theme.id == theme_id, Theme.is_active == True)
            )

            result = await self.db.execute(query)
            theme = result.scalar_one_or_none()

            if not theme:
                raise HTTPException(
                    status_code=404,
                    detail="Theme not found"
                )

            return {
                "theme": {
                    "id": theme.id,
                    "name": theme.name,
                    "description": theme.description,
                    "category": theme.category,
                    "is_premium": theme.is_premium,
                    "is_seasonal": theme.is_seasonal,
                    "season": theme.season,
                    "primary_color": theme.primary_color,
                    "secondary_color": theme.secondary_color,
                    "accent_color": theme.accent_color,
                    "background_color": theme.background_color,
                    "text_color": theme.text_color,
                    "border_color": theme.border_color,
                    "preview_url": theme.preview_url,
                    "cover_templates": theme.cover_templates,
                    "created_at": theme.created_at.isoformat(),
                    "updated_at": theme.updated_at.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Failed to get theme {theme_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve theme"
            )

    async def create_custom_theme(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        category: str = "custom",
        primary_color: str,
        secondary_color: str,
        accent_color: str,
        background_color: str,
        text_color: str,
        border_color: str,
        cover_templates: Optional[List[dict]] = None
    ) -> Dict[str, Any]:
        """Create custom user theme"""
        try:
            # Create custom theme
            custom_theme = Theme(
                user_id=user_id,
                name=name,
                description=description or f"Custom theme created by user",
                category=category,
                is_premium=False,
                is_seasonal=False,
                primary_color=primary_color,
                secondary_color=secondary_color,
                accent_color=accent_color,
                background_color=background_color,
                text_color=text_color,
                border_color=border_color,
                cover_templates=cover_templates or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(custom_theme)
            await self.db.commit()
            await self.db.refresh(custom_theme)

            logger.info(f"Custom theme created: {custom_theme.id} - {custom_theme.name}")
            return {
                "message": "Custom theme created successfully",
                "theme": {
                    "id": custom_theme.id,
                    "name": custom_theme.name,
                    "description": custom_theme.description,
                    "category": custom_theme.category,
                    "is_premium": custom_theme.is_premium,
                    "is_seasonal": custom_theme.is_seasonal,
                    "season": custom_theme.season,
                    "primary_color": custom_theme.primary_color,
                    "secondary_color": custom_theme.secondary_color,
                    "accent_color": custom_theme.accent_color,
                    "background_color": custom_theme.background_color,
                    "text_color": custom_theme.text_color,
                    "border_color": custom_theme.border_color,
                    "cover_templates": custom_theme.cover_templates,
                    "created_at": custom_theme.created_at.isoformat(),
                    "updated_at": custom_theme.updated_at.isoformat()
                }
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create custom theme: {e}")
            raise HTTPException(
                status_code=500,
                detail="Theme creation failed due to internal error"
            )

    async def get_user_theme_preferences(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Get user's theme preferences and usage"""
        try:
            # Get themes used by user
            used_themes_query = select(Theme.id).join(
                Project, Project.theme_id
            ).where(
                and_(Project.user_id == user_id, Project.theme_id.isnot(None))
            ).distinct()

            used_themes_result = await self.db.execute(used_themes_query)
            used_theme_ids = [row[0] for row in used_themes_result.all()]

            if not used_theme_ids:
                return {
                    "used_themes": [],
                    "favorite_themes": [],
                    "usage_stats": {
                        "total_projects": 0,
                        "themes_used": 0,
                        "most_used_category": None,
                        "recent_theme": None
                    }
                }

            # Get theme details for used themes
            themes_query = select(Theme).where(Theme.id.in_(used_theme_ids))
            used_themes_result = await self.db.execute(themes_query)
            used_themes = used_themes_result.scalars().all()

            # Get user favorite themes (this would come from user preferences)
            favorite_themes = []  # TODO: Implement from user preferences

            return {
                "used_themes": [
                    {
                        "id": theme.id,
                        "name": theme.name,
                        "category": theme.category,
                        "is_premium": theme.is_premium,
                        "preview_url": theme.preview_url
                    }
                    for theme in used_themes
                ],
                "favorite_themes": favorite_themes,
                "usage_stats": {
                    "total_projects": await self._get_user_project_count(user_id),
                    "themes_used": len(used_theme_ids),
                    "most_used_category": self._get_most_used_category(used_themes),
                    "recent_theme": self._get_most_recent_theme(used_themes)
                }
            }

        except Exception as e:
            logger.error(f"Failed to get user theme preferences: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve theme preferences"
            )

    async def update_user_theme_preference(
        self,
        user_id: int,
        theme_id: int,
        is_favorite: bool = False
    ) -> Dict[str, Any]:
        """Update user's theme preference"""
        try:
            # This would update a user_preferences table
            # For now, return success message
            # TODO: Implement actual user preference storage

            logger.info(f"Theme preference updated for user {user_id}: theme {theme_id}")
            return {
                "message": "Theme preference updated successfully",
                "theme_id": theme_id,
                "is_favorite": is_favorite
            }

        except Exception as e:
            logger.error(f"Failed to update theme preference: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update theme preference"
            )

    async def get_theme_statistics(
        self,
    user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get theme usage statistics"""
        try:
            # Get theme usage count
            if user_id:
                user_filter = Project.user_id == user_id
            else:
                user_filter = True  # All projects for admin stats

            themes_query = select(Theme.id).join(
                Project, Project.theme_id
            ).where(user_filter if user_id else True)

            usage_result = await self.db.execute(
                select(Theme.id, func.count(Theme.id))
                .join(Project, Project.theme_id)
                .where(user_filter if user_id else True)
                .group_by(Theme.id)
            )

            theme_usage = {}
            for row in usage_result.all():
                theme_usage[row.Theme.id] = row[1]

            # Get total projects count for percentage calculation
            total_projects_query = select(func.count(Project.id))
            if user_id:
                total_projects_query = total_projects_query.where(Project.user_id == user_id)

            total_projects_result = await self.db.execute(total_projects_query)
            total_projects = total_projects_result.scalar() or 0

            return {
                "total_themes": len(theme_usage),
                "theme_usage": theme_usage,
                "usage_percentages": {
                    str(theme_id): (count / total_projects * 100) if total_projects > 0 else 0
                    for theme_id, count in theme_usage.items()
                },
                "total_projects": total_projects
            }

        except Exception as e:
            logger.error(f"Failed to get theme statistics: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve theme statistics"
            )

    async def _get_user_project_count(self, user_id: int) -> int:
        """Get total projects for user"""
        result = await self.db.execute(
            select(func.count(Project.id)).where(Project.user_id == user_id)
        )
        return result.scalar() or 0

    async def _get_most_used_category(self, themes: List[Theme]) -> Optional[str]:
        """Get most commonly used theme category"""
        if not themes:
            return None

        # Count usage by category
        category_counts = {}
        for theme in themes:
            category = theme.category
            category_counts[category] = category_counts.get(category, 0) + 1

        return max(category_counts.items(), key=lambda x: x[1])[0]

    async def _get_most_recent_theme(self, themes: List[Theme]) -> Optional[Theme]:
        """Get most recently used theme"""
        if not themes:
            return None

        return max(themes, key=lambda t: t.updated_at or datetime.min)