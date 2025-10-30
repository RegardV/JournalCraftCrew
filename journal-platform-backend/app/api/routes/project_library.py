"""
Project Library API Routes
Manages user's AI-generated and customized journal projects
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user, get_db
from app.services.project_library_service import ProjectLibraryService
from app.models.export import ExportFormat
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/library", tags=["Project Library"])

# Pydantic models for requests and responses
class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    layout: Optional[str] = Field(None, description="Layout style")
    font_size: Optional[str] = Field(None, description="Font size")
    font_family: Optional[str] = Field(None, description="Font family")
    page_numbers: Optional[bool] = Field(None, description="Include page numbers")
    table_of_contents: Optional[bool] = Field(None, description="Include table of contents")
    date_format: Optional[str] = Field(None, description="Date format")
    custom_css: Optional[str] = Field(None, description="Custom CSS")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    tags: Optional[List[str]] = Field(None, description="Project tags")

class ProjectCreateRequest(BaseModel):
    title: str = Field(..., description="Project title")
    ai_content: dict = Field(..., description="AI-generated content")
    description: Optional[str] = Field(None, description="Project description")

class ProjectSummary(BaseModel):
    id: int
    title: str
    description: Optional[str]
    type: str
    status: str
    theme: Optional[str]
    cover_image_url: Optional[str]
    word_count: int
    estimated_reading_time: int
    tags: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    ai_generated: bool
    customization_applied: bool
    ai_theme: Optional[str] = None
    title_style: Optional[str] = None

class ProjectStatistics(BaseModel):
    total_projects: int
    ai_generated_projects: int
    customized_projects: int
    published_projects: int
    total_word_count: int
    project_types: dict
    project_statuses: dict
    recent_activity: List[dict]


@router.get("/projects", response_model=dict)
async def get_user_projects(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    project_type: Optional[str] = Query(None, description="Filter by type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's project library with filtering and pagination"""
    try:
        library_service = ProjectLibraryService(db)
        result = await library_service.get_user_projects(
            user_id=current_user["id"],
            status_filter=status_filter,
            project_type=project_type,
            page=page,
            limit=limit,
            search_query=search
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting user projects: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve projects"
        )


@router.get("/projects/{project_id}", response_model=dict)
async def get_project_detail(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed project information"""
    try:
        library_service = ProjectLibraryService(db)
        result = await library_service.get_project_detail(
            project_id=project_id,
            user_id=current_user["id"]
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting project detail: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve project details"
        )


@router.post("/projects", status_code=201)
async def create_project_from_ai(
    project_data: ProjectCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create project from AI-generated content"""
    try:
        # Check if user has sufficient AI credits
        if current_user.get("ai_credits", 0) <= 0:
            raise HTTPException(
                status_code=402,
                detail="Insufficient AI credits. Please upgrade your plan."
            )

        library_service = ProjectLibraryService(db)
        result = await library_service.create_project_from_ai(
            user_id=current_user["id"],
            ai_content=project_data.ai_content,
            title=project_data.title
        )

        logger.info(f"Created AI project {result['project_id']} for user {current_user['id']}")
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating project from AI: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create project from AI content"
        )


@router.put("/projects/{project_id}")
async def update_project_customization(
    project_id: int,
    customization_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update project with user customizations"""
    try:
        library_service = ProjectLibraryService(db)

        # Only include non-None fields
        update_dict = {k: v for k, v in customization_data.dict().items() if v is not None}

        if not update_dict:
            raise HTTPException(
                status_code=400,
                detail="No customization data provided"
            )

        result = await library_service.update_project_customization(
            project_id=project_id,
            user_id=current_user["id"],
            customization_data=update_dict
        )

        logger.info(f"Updated customization for project {project_id} by user {current_user['id']}")
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating project customization: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update project customization"
        )


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project and all associated data"""
    try:
        library_service = ProjectLibraryService(db)
        result = await library_service.delete_project(
            project_id=project_id,
            user_id=current_user["id"]
        )

        logger.info(f"Deleted project {project_id} by user {current_user['id']}")
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete project"
        )


@router.get("/statistics", response_model=ProjectStatistics)
async def get_project_statistics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's project library statistics"""
    try:
        library_service = ProjectLibraryService(db)
        result = await library_service.get_project_statistics(
            user_id=current_user["id"]
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting project statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve project statistics"
        )


@router.get("/filters")
async def get_available_filters():
    """Get available filter options for project library"""
    return {
        "status_filters": [
            {"value": "draft", "label": "Draft"},
            {"value": "in_progress", "label": "In Progress"},
            {"value": "review", "label": "Under Review"},
            {"value": "completed", "label": "Completed"},
            {"value": "published", "label": "Published"},
            {"value": "archived", "label": "Archived"},
            {"value": "ai_generating", "label": "AI Generating"},
            {"value": "ai_completed", "label": "AI Completed"}
        ],
        "type_filters": [
            {"value": "personal", "label": "Personal"},
            {"value": "project", "label": "Project"},
            {"value": "therapeutic", "label": "Therapeutic"},
            {"value": "creative", "label": "Creative"},
            {"value": "travel", "label": "Travel"},
            {"value": "family", "label": "Family"},
            {"value": "professional", "label": "Professional"}
        ],
        "sort_options": [
            {"value": "updated_at", "label": "Last Updated"},
            {"value": "created_at", "label": "Created Date"},
            {"value": "title", "label": "Title"},
            {"value": "word_count", "label": "Word Count"}
        ],
        "export_formats": [
            {"value": "pdf", "label": "PDF"},
            {"value": "epub", "label": "EPUB"},
            {"value": "kdp", "label": "Amazon KDP"}
        ]
    }


@router.post("/projects/{project_id}/duplicate")
async def duplicate_project(
    project_id: int,
    title: Optional[str] = Query(None, description="New project title"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate an existing project"""
    try:
        library_service = ProjectLibraryService(db)

        # Get original project
        original_project = await library_service.get_project_detail(
            project_id=project_id,
            user_id=current_user["id"]
        )

        if not original_project:
            raise HTTPException(
                status_code=404,
                detail="Original project not found"
            )

        # Create duplicate
        duplicate_title = title or f"{original_project['title']} (Copy)"
        duplicate_data = {
            "title": duplicate_title,
            "description": f"Copy of: {original_project.get('description', '')}",
            "type": original_project.get('type', 'personal'),
            "ai_content": original_project.get('ai_generated_content', {}),
            "settings": original_project.get('settings', {})
        }

        result = await library_service.create_project_from_ai(
            user_id=current_user["id"],
            ai_content=duplicate_data["ai_content"] or {},
            title=duplicate_data["title"]
        )

        # Update the duplicate with custom settings
        if duplicate_data.get("settings"):
            await library_service.update_project_customization(
                project_id=result["project_id"],
                user_id=current_user["id"],
                customization_data=duplicate_data["settings"]
            )

        logger.info(f"Duplicated project {project_id} as {result['project_id']} for user {current_user['id']}")
        return {
            "message": "Project duplicated successfully",
            "original_project_id": project_id,
            "new_project_id": result["project_id"],
            "new_title": duplicate_title
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error duplicating project: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to duplicate project"
        )