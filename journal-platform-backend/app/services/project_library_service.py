"""
Project Library Service
Manages user's AI-generated and customized journal projects
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from fastapi import HTTPException

from app.models import Project, User, JournalEntry, JournalTemplate
from app.models.export import ExportJob
import logging

logger = logging.getLogger(__name__)


class ProjectLibraryService:
    """Service for managing user's project library"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_projects(
        self,
        user_id: int,
        status_filter: Optional[str] = None,
        project_type: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's projects with filtering and pagination"""
        try:
            # Build base query
            query = select(Project).where(Project.user_id == user_id)

            # Apply filters
            if status_filter:
                query = query.where(Project.status == status_filter)

            if project_type:
                query = query.where(Project.type == project_type)

            if search_query:
                search_pattern = f"%{search_query}%"
                query = query.where(
                    or_(
                        Project.title.ilike(search_pattern),
                        Project.description.ilike(search_pattern)
                    )
                )

            # Order by updated_at desc
            query = query.order_by(desc(Project.updated_at))

            # Get total count
            count_query = select(Project).where(Project.user_id == user_id)
            if status_filter:
                count_query = count_query.where(Project.status == status_filter)
            if project_type:
                count_query = count_query.where(Project.type == project_type)
            if search_query:
                search_pattern = f"%{search_query}%"
                count_query = count_query.where(
                    or_(
                        Project.title.ilike(search_pattern),
                        Project.description.ilike(search_pattern)
                    )
                )

            total_result = await self.db.execute(count_query)
            total = len(total_result.scalars().all())

            # Apply pagination
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

            # Execute query
            result = await self.db.execute(query)
            projects = result.scalars().all()

            # Format projects
            formatted_projects = []
            for project in projects:
                formatted_project = {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "type": project.type,
                    "status": project.status,
                    "theme": project.theme,
                    "cover_image_url": project.cover_image_url,
                    "word_count": project.word_count,
                    "estimated_reading_time": project.estimated_reading_time,
                    "tags": project.tags.split(',') if project.tags else [],
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                    "last_edited": project.last_edited.isoformat() if project.last_edited else None,
                    "ai_generated": bool(project.ai_generated_content),
                    "customization_applied": bool(project.custom_css is not None)
                }

                # Add AI generation metadata if available
                if project.ai_generated_content:
                    try:
                        ai_content = json.loads(project.ai_generated_content)
                        formatted_project["ai_theme"] = ai_content.get("theme")
                        formatted_project["title_style"] = ai_content.get("title_style")
                        formatted_project["generation_date"] = ai_content.get("generated_at")
                    except (json.JSONDecodeError, KeyError):
                        logger.warning(f"Failed to parse AI content for project {project.id}")

                formatted_projects.append(formatted_project)

            return {
                "projects": formatted_projects,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }

        except Exception as e:
            logger.error(f"Error getting user projects: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve projects"
            )

    async def get_project_detail(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """Get detailed project information"""
        try:
            # Get project
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

            # Get project entries
            entries_result = await self.db.execute(
                select(JournalEntry).where(JournalEntry.project_id == project_id)
            )
            entries = entries_result.scalars().all()

            # Get export history
            exports_result = await self.db.execute(
                select(ExportJob).where(ExportJob.project_id == project_id)
            )
            exports = exports_result.scalars().all()

            # Format project detail
            project_detail = {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "type": project.type,
                "status": project.status,
                "visibility": project.visibility,
                "theme_id": project.theme_id,
                "theme": project.theme,
                "cover_image_url": project.cover_image_url,
                "word_count": project.word_count,
                "estimated_reading_time": project.estimated_reading_time,
                "tags": project.tags.split(',') if project.tags else [],
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                "last_edited": project.last_edited.isoformat() if project.last_edited else None,

                # Settings
                "settings": {
                    "layout": project.layout,
                    "font_size": project.font_size,
                    "font_family": project.font_family,
                    "page_numbers": project.page_numbers,
                    "table_of_contents": project.table_of_contents,
                    "date_format": project.date_format,
                    "custom_css": project.custom_css
                },

                # AI Generation data
                "ai_generated_content": json.loads(project.ai_generated_content) if project.ai_generated_content else None,
                "ai_generated": bool(project.ai_generated_content),

                # Entries
                "entries_count": len(entries),
                "entries": [
                    {
                        "id": entry.id,
                        "title": entry.title,
                        "content": entry.content,
                        "word_count": entry.word_count,
                        "mood": entry.mood,
                        "tags": entry.tags,
                        "cover_image": entry.cover_image,
                        "created_at": entry.created_at.isoformat() if entry.created_at else None,
                        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
                        "last_accessed": entry.last_accessed.isoformat() if entry.last_accessed else None,
                        "ai_generated": bool(entry.ai_generated_content),
                        "is_customized": entry.is_customized
                    }
                    for entry in entries
                ],

                # Export history
                "export_history": [
                    {
                        "id": export.id,
                        "format": export.format,
                        "status": export.status,
                        "file_size": export.file_size,
                        "download_url": export.download_url,
                        "created_at": export.created_at.isoformat() if export.created_at else None,
                        "settings": json.loads(export.settings) if export.settings else None
                    }
                    for export in exports
                ]
            }

            return project_detail

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting project detail: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve project details"
            )

    async def create_project_from_ai(
        self,
        user_id: int,
        ai_content: Dict[str, Any],
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create project from AI-generated content"""
        try:
            # Create project
            project = Project(
                user_id=user_id,
                title=title or ai_content.get("journal_content", {}).get("title", "AI Generated Journal"),
                description=f"AI-generated {ai_content.get('theme', 'journal')} with {ai_content.get('title_style', 'standard')} style",
                type="project",
                status="ai_completed",
                theme=ai_content.get("theme"),
                ai_generated_content=json.dumps(ai_content),
                word_count=0,  # Will be calculated from AI content
                visibility="private"
            )

            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)

            # Create journal entries from AI content
            journal_content = ai_content.get("journal_content", {})
            entries_created = []

            # Add intro spread
            if "intro_spread" in journal_content:
                intro_entry = JournalEntry(
                    user_id=user_id,
                    project_id=project.id,
                    title="Introduction",
                    content=json.dumps(journal_content["intro_spread"]),
                    ai_generated_content=json.dumps(journal_content["intro_spread"]),
                    word_count=len(str(journal_content["intro_spread"]).split()),
                    ai_theme=ai_content.get("theme"),
                    ai_agent_version="v1.0"
                )
                self.db.add(intro_entry)
                entries_created.append("intro")

            # Add daily entries
            if "days" in journal_content:
                for day_data in journal_content["days"]:
                    day_entry = JournalEntry(
                        user_id=user_id,
                        project_id=project.id,
                        title=f"Day {day_data.get('day', 1)} - {day_data.get('theme', '')}",
                        content=json.dumps(day_data),
                        ai_generated_content=json.dumps(day_data),
                        word_count=len(str(day_data).split()),
                        mood=day_data.get("mood", "neutral"),
                        tags=[day_data.get("theme", "")],
                        ai_theme=ai_content.get("theme"),
                        ai_agent_version="v1.0"
                    )
                    self.db.add(day_entry)
                    entries_created.append(f"day_{day_data.get('day', 1)}")

            await self.db.commit()

            logger.info(f"Created AI project {project.id} for user {user_id} with {len(entries_created)} entries")

            return {
                "message": "Project created successfully from AI content",
                "project_id": project.id,
                "title": project.title,
                "entries_created": len(entries_created),
                "ai_theme": ai_content.get("theme"),
                "status": project.status
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating project from AI content: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create project from AI content"
            )

    async def update_project_customization(
        self,
        project_id: int,
        user_id: int,
        customization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update project with user customizations"""
        try:
            # Verify project ownership
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

            # Update customizable fields
            if "title" in customization_data:
                project.title = customization_data["title"]

            if "description" in customization_data:
                project.description = customization_data["description"]

            if "layout" in customization_data:
                project.layout = customization_data["layout"]

            if "font_size" in customization_data:
                project.font_size = customization_data["font_size"]

            if "font_family" in customization_data:
                project.font_family = customization_data["font_family"]

            if "page_numbers" in customization_data:
                project.page_numbers = customization_data["page_numbers"]

            if "table_of_contents" in customization_data:
                project.table_of_contents = customization_data["table_of_contents"]

            if "date_format" in customization_data:
                project.date_format = customization_data["date_format"]

            if "custom_css" in customization_data:
                project.custom_css = customization_data["custom_css"]

            if "cover_image_url" in customization_data:
                project.cover_image_url = customization_data["cover_image_url"]

            if "tags" in customization_data:
                if isinstance(customization_data["tags"], list):
                    project.tags = ','.join(customization_data["tags"])
                else:
                    project.tags = customization_data["tags"]

            # Update status to indicate customization
            if project.status == "ai_completed":
                project.status = "in_progress"

            project.updated_at = datetime.utcnow()
            project.last_edited = datetime.utcnow()

            await self.db.commit()

            return {
                "message": "Project customization updated successfully",
                "project_id": project.id,
                "updated_fields": list(customization_data.keys()),
                "status": project.status
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating project customization: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update project customization"
            )

    async def delete_project(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a project and all associated data"""
        try:
            # Verify project ownership
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

            # Delete project (cascade will handle related records)
            await self.db.delete(project)
            await self.db.commit()

            logger.info(f"Deleted project {project_id} for user {user_id}")

            return {
                "message": "Project deleted successfully",
                "project_id": project_id
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting project: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete project"
            )

    async def get_project_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get user's project library statistics"""
        try:
            # Get all user projects
            result = await self.db.execute(
                select(Project).where(Project.user_id == user_id)
            )
            projects = result.scalars().all()

            # Calculate statistics
            total_projects = len(projects)
            ai_generated = sum(1 for p in projects if p.ai_generated_content)
            customized = sum(1 for p in projects if p.custom_css or p.status == "in_progress")
            published = sum(1 for p in projects if p.status == "published")

            # Get project type distribution
            type_counts = {}
            status_counts = {}

            for project in projects:
                # Type distribution
                project_type = project.type or "unknown"
                type_counts[project_type] = type_counts.get(project_type, 0) + 1

                # Status distribution
                project_status = project.status or "unknown"
                status_counts[project_status] = status_counts.get(project_status, 0) + 1

            # Total word count
            total_words = sum(p.word_count or 0 for p in projects)

            return {
                "total_projects": total_projects,
                "ai_generated_projects": ai_generated,
                "customized_projects": customized,
                "published_projects": published,
                "total_word_count": total_words,
                "project_types": type_counts,
                "project_statuses": status_counts,
                "recent_activity": [
                    {
                        "project_id": p.id,
                        "title": p.title,
                        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                        "action": "updated" if p.last_edited and p.last_edited > p.updated_at else "created"
                    }
                    for p in sorted(projects, key=lambda x: x.updated_at or x.created_at, reverse=True)[:5]
                ]
            }

        except Exception as e:
            logger.error(f"Error getting project statistics: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve project statistics"
            )