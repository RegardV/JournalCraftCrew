"""
Project Management Service
Phase 3.3: Core API Services Implementation
"""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status

from app.models.project import Project, ProjectCollaborator
from app.models.user import User
from app.models.theme import Theme
from app.core.database import get_async_session
import logging

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for project management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        type: str = "journal",
        theme_id: Optional[int] = None
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new project"""
        try:
            # Validate project data
            if not title or len(title.strip()) < 1:
                raise HTTPException(
                    status_code=400,
                    detail="Project title is required"
                )

            # Create project with default values
            project = Project(
                user_id=user_id,
                title=title.strip(),
                description=description or "",
                type=type,
                status="draft",
                theme_id=theme_id,
                content={"pages": []},  # Initial empty content
                settings=settings or {
                    "format": "a5",
                    "orientation": "portrait",
                    "margins": "standard",
                    "page_numbers": True,
                    "table_of_contents": False
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)

            logger.info(f"Project created: {project.id} - {project.title}")
            return {
                "message": "Project created successfully",
                "project": {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "type": project.type,
                    "status": project.status,
                    "theme_id": project.theme_id,
                    "content": project.content,
                    "settings": project.settings,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Project creation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Project creation failed due to internal error"
            )

    async def get_user_projects(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's projects with pagination and filtering"""
        try:
            # Build query
            query = select(Project).where(Project.user_id == user_id)

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.where(Project.title.ilike(search_term))

            # Apply status filter
            if status_filter:
                query = query.where(Project.status == status_filter)

            # Add ordering
            query = query.order_by(Project.updated_at.desc())

            # Execute with pagination
            result = await self.db.execute(query.offset(skip).limit(limit))
            projects = result.scalars().all()

            # Get total count
            count_query = select(func.count(Project.id)).where(Project.user_id == user_id)
            if search:
                count_query = count_query.where(Project.title.ilike(f"%{search}%"))
            if status_filter:
                count_query = count_query.where(Project.status == status_filter)

            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            return {
                "projects": [
                    {
                        "id": project.id,
                        "title": project.title,
                        "description": project.description,
                        "type": project.type,
                        "status": project.status,
                        "theme_id": project.theme_id,
                        "word_count": len(str(project.content.get("pages", []))),
                        "created_at": project.created_at.isoformat(),
                        "updated_at": project.updated_at.isoformat()
                    }
                    for project in projects
                ],
                "pagination": {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "has_more": skip + limit < total
                }
            }

        except Exception as e:
            logger.error(f"Failed to get user projects: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve projects"
            )

    async def get_project(
        self,
        project_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Get specific project with ownership verification"""
        try:
            result = await self.db.execute(
                select(Project).where(
                    and_(Project.id == project_id, Project.user_id == user_id)
                )
            )
            project = result.scalar_one_or_none()

            if not project:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found"
                )

            return {
                "project": {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "type": project.type,
                    "status": project.status,
                    "theme_id": project.theme_id,
                    "content": project.content,
                    "settings": project.settings,
                    "word_count": len(str(project.content.get("pages", []))),
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve project"
            )

    async def update_project(
        self,
        project_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        theme_id: Optional[int] = None,
        content: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update project with validation"""
        try:
            # Get existing project
            result = await self.db.execute(
                select(Project).where(
                    and_(Project.id == project_id, Project.user_id == user_id)
                )
            )
            project = result.scalar_one_or_none()

            if not project:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found"
                )

            # Update fields if provided
            if title is not None:
                project.title = title.strip()
            if description is not None:
                project.description = description
            if status is not None:
                project.status = status
            if theme_id is not None:
                project.theme_id = theme_id
            if content is not None:
                project.content = content
            if settings is not None:
                project.settings = settings

            project.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(project)

            logger.info(f"Project updated: {project.id} - {project.title}")
            return {
                "message": "Project updated successfully",
                "project": {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "type": project.type,
                    "status": project.status,
                    "theme_id": project.theme_id,
                    "content": project.content,
                    "settings": project.settings,
                    "word_count": len(str(project.content.get("pages", []))),
                    "updated_at": project.updated_at.isoformat()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Project update failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Project update failed due to internal error"
            )

    async def delete_project(
        self,
        project_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Delete project with ownership verification"""
        try:
            # Check project exists and belongs to user
            result = await self.db.execute(
                select(Project).where(
                    and_(Project.id == project_id, Project.user_id == user_id)
                )
            )
            project = result.scalar_one_or_none()

            if not project:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found"
                )

            # TODO: Check for active exports or collaborators
            # For now, allow deletion if no active exports

            await self.db.delete(project)
            await self.db.commit()

            logger.info(f"Project deleted: {project_id} - {project.title}")
            return {"message": "Project deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Project deletion failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Project deletion failed due to internal error"
            )

    async def duplicate_project(
        self,
        project_id: int,
        user_id: int,
        new_title: str
    ) -> Dict[str, Any]:
        """Duplicate project with new content copy"""
        try:
            # Get original project
            result = await self.db.execute(
                select(Project).where(
                    and_(Project.id == project_id, Project.user_id == user_id)
                )
            )
            original_project = result.scalar_one_or_none()

            if not original_project:
                raise HTTPException(
                    status_code=404,
                    detail="Original project not found"
                )

            # Create duplicate
            new_project = Project(
                user_id=user_id,
                title=new_title.strip(),
                description=f"Copy of {original_project.title}",
                type=original_project.type,
                status="draft",
                theme_id=original_project.theme_id,
                content=original_project.content.copy(),  # Deep copy
                settings=original_project.settings.copy() if original_project.settings else {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(new_project)
            await self.db.commit()
            await self.db.refresh(new_project)

            logger.info(f"Project duplicated: {new_project.id} - {new_project.title}")
            return {
                "message": "Project duplicated successfully",
                "project": {
                    "id": new_project.id,
                    "title": new_project.title,
                    "description": new_project.description,
                    "type": new_project.type,
                    "status": new_project.status,
                    "theme_id": new_project.theme_id,
                    "content": new_project.content,
                    "settings": new_project.settings,
                    "word_count": len(str(new_project.content.get("pages", []))),
                    "created_at": new_project.created_at.isoformat(),
                    "updated_at": new_project.updated_at.isoformat()
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Project duplication failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Project duplication failed due to internal error"
            )

    async def get_project_statistics(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Get project statistics for dashboard"""
        try:
            # Get project counts by status
            status_counts = await self.db.execute(
                select(
                    Project.status,
                    func.count(Project.id).label("count")
                ).where(Project.user_id == user_id)
                .group_by(Project.status)
            )
            status_result = status_counts.all()

            # Build statistics dict
            stats = {status: 0 for status in ["draft", "in_progress", "completed", "archived"]}

            for row in status_result:
                if row.status in stats:
                    stats[row.status] = row.count

            total_projects = sum(stats.values())

            # Get total word count
            word_count_result = await self.db.execute(
                select(func.sum(func.length(Project.content))).where(
                    and_(Project.user_id == user_id, Project.type == "journal")
                )
            )
            total_words = word_count_result.scalar() or 0

            return {
                "total_projects": total_projects,
                "status_breakdown": stats,
                "total_word_count": total_words,
                "completion_rate": round((stats.get("completed", 0) / total_projects * 100), 1) if total_projects > 0 else 0
            }

        except Exception as e:
            logger.error(f"Failed to get project statistics: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve project statistics"
            )