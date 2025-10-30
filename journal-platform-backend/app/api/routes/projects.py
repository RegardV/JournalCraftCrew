"""
Project Management API Routes
Phase 3.3: Core API Services Implementation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user, get_db
from app.services.project_service import ProjectService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Project Management"])

# Pydantic models for request/response
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Project title")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    type: str = Field("journal", description="Project type")
    theme_id: Optional[int] = Field(None, description="Theme ID for project")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Project title")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: Optional[str] = Field(None, description="Project status")
    theme_id: Optional[int] = Field(None, description="Theme ID for project")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    type: str
    status: str
    theme_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None
    word_count: int
    created_at: str
    updated_at: str

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    pagination: Dict[str, Any]

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    try:
        project_service = ProjectService(db)
        result = await project_service.create_project(
            user_id=current_user["id"],
            title=project_data.title,
            description=project_data.description,
            type=project_data.type,
            theme_id=project_data.theme_id,
            settings=project_data.settings
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Project creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Project creation failed due to internal error"
        )

@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=50),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None)
):
    """Get user's projects with pagination and filtering"""
    try:
        project_service = ProjectService(db)
        result = await project_service.get_user_projects(
            user_id=current_user["id"],
            skip=skip,
            limit=limit,
            search=search,
            status_filter=status_filter
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve projects"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific project by ID"""
    try:
        project_service = ProjectService(db)
        result = await project_service.get_project(
            project_id=project_id,
            user_id=current_user["id"]
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve project"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update project"""
    try:
        project_service = ProjectService(db)
        result = await project_service.update_project(
            project_id=project_id,
            user_id=current_user["id"],
            title=project_data.title,
            description=project_data.description,
            status=project_data.status,
            theme_id=project_data.theme_id,
            settings=project_data.settings
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update project"
        )

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete project"""
    try:
        project_service = ProjectService(db)
        await project_service.delete_project(
            project_id=project_id,
            user_id=current_user["id"]
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete project"
        )

@router.post("/{project_id}/duplicate", response_model=ProjectResponse, status_code=201)
async def duplicate_project(
    project_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate project"""
    try:
        # Get project details first to determine what to duplicate
        project_service = ProjectService(db)
        original_project = await project_service.get_project(
            project_id=project_id,
            user_id=current_user["id"]
        )

        # Create duplicate with "Copy of" prefix
        new_title = f"Copy of {original_project['project']['title']}"

        result = await project_service.duplicate_project(
            project_id=project_id,
            user_id=current_user["id"],
            new_title=new_title
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to duplicate project {project_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to duplicate project"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_project_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project statistics for dashboard"""
    try:
        project_service = ProjectService(db)
        result = await project_service.get_project_statistics(
            user_id=current_user["id"]
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get project statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve project statistics"
        )