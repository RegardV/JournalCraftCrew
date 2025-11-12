"""
Journal Content Analysis API Routes
Provides endpoints for analyzing existing journal content and getting enhancement recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from ...core.deps import get_db, get_current_user
from ...models.user import User
from ...models.project import Project
from ...services.journal_content_analyzer import journal_content_analyzer
from ..routes.crewai_workflow import crewai_service

router = APIRouter()


# Pydantic models
class ProjectAnalysisRequest(BaseModel):
    project_id: int = Field(..., description="ID of the project to analyze")
    force_refresh: bool = Field(default=False, description="Force analysis refresh (skip cache)")


class ProjectAnalysisResponse(BaseModel):
    project_id: int
    analysis: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    analyzed_at: str
    cached: bool


class EnhancementRequest(BaseModel):
    project_id: int = Field(..., description="ID of the project to enhance")
    enhancement_type: str = Field(..., description="Type of enhancement: 'complete_missing', 'improve_quality', 'add_variant'")
    selected_recommendations: List[str] = Field(default=[], description="Specific recommendations to implement")
    custom_preferences: Dict[str, Any] = Field(default_factory=dict, description="Custom enhancement preferences")


class EnhancementResponse(BaseModel):
    workflow_id: str
    status: str
    message: str
    estimated_time: int


class RecommendationAction(BaseModel):
    project_id: int
    recommendation_id: str
    action: str = Field(..., description="Action: 'accept', 'reject', 'modify'")


@router.post("/analyze-project/{project_id}", response_model=ProjectAnalysisResponse)
async def analyze_project(
    project_id: int,
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a journal project and return comprehensive analysis with enhancement recommendations
    """
    try:
        # Verify project ownership
        project_query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Analyze project
        analysis = await journal_content_analyzer.analyze_project_state(project_id, db)

        # Extract recommendations from analysis
        recommendations = analysis.get("recommendations", [])

        return ProjectAnalysisResponse(
            project_id=project_id,
            analysis=analysis,
            recommendations=recommendations,
            analyzed_at="2025-01-11T00:00:00Z",  # Would use actual timestamp
            cached=False  # Would check if analysis was from cache
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze project: {str(e)}")


@router.post("/enhance-project", response_model=EnhancementResponse)
async def enhance_project(
    request: EnhancementRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start an enhancement workflow for an existing project using CrewAI agents
    """
    try:
        # Verify project ownership
        project_query = select(Project).where(
            and_(
                Project.id == request.project_id,
                Project.user_id == current_user.id
            )
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get current project analysis for context
        analysis = await journal_content_analyzer.analyze_project_state(request.project_id, db)

        # Determine enhancement workflow based on type
        workflow_preferences = await _build_enhancement_preferences(
            request, project, analysis
        )

        # Start CrewAI enhancement workflow
        workflow_response = await crewai_service.start_workflow(
            user_id=current_user.id,
            preferences=workflow_preferences,
            db=db
        )

        return EnhancementResponse(
            workflow_id=workflow_response.workflow_id,
            status=workflow_response.status,
            message=f"Enhancement workflow started: {request.enhancement_type}",
            estimated_time=_estimate_enhancement_time(request.enhancement_type, analysis)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start enhancement: {str(e)}")


@router.get("/recommendations/{project_id}")
async def get_project_recommendations(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get enhancement recommendations for a specific project
    """
    try:
        # Verify project ownership
        project_query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get project analysis
        analysis = await journal_content_analyzer.analyze_project_state(project_id, db)

        return {
            "project_id": project_id,
            "recommendations": analysis.get("recommendations", []),
            "enhancement_potential": analysis.get("enhancement_potential", 0),
            "current_quality": analysis.get("quality_scores", {}),
            "missing_components": analysis.get("missing_components", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/quick-enhance/{project_id}")
async def quick_enhance_project(
    project_id: int,
    enhancement_type: str,  # 'add_images', 'improve_writing', 'expand_content', 'create_pdf'
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick enhancement action with predefined workflows
    """
    try:
        # Verify project ownership
        project_query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Build quick enhancement preferences
        preferences = _build_quick_enhancement_preferences(enhancement_type, project)

        # Start enhancement workflow
        workflow_response = await crewai_service.start_workflow(
            user_id=current_user.id,
            preferences=preferences,
            db=db
        )

        return {
            "workflow_id": workflow_response.workflow_id,
            "status": "started",
            "enhancement_type": enhancement_type,
            "message": f"Quick enhancement started: {enhancement_type}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start quick enhancement: {str(e)}")


@router.get("/quality-score/{project_id}")
async def get_content_quality_score(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed quality assessment for project content
    """
    try:
        # Verify project ownership
        project_query = select(Project).where(
            and_(
                Project.id == project_id,
                Project.user_id == current_user.id
            )
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get project analysis
        analysis = await journal_content_analyzer.analyze_project_state(project_id, db)

        return {
            "project_id": project_id,
            "quality_scores": analysis.get("quality_scores", {}),
            "completion_map": analysis.get("completion_map", {}),
            "content_analysis": {
                "total_files": len(analysis.get("existing_files", [])),
                "content_size": analysis.get("content_size", 0),
                "project_age_days": analysis.get("project_age_days", 0)
            },
            "enhancement_opportunities": analysis.get("enhancement_potential", 0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quality score: {str(e)}")


def _build_enhancement_preferences(
    request: EnhancementRequest, project: Project, analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Build enhancement preferences for CrewAI workflow"""

    preferences = {
        "title": project.title,
        "theme": project.theme or "General Journaling",
        "action": "enhance_content",
        "enhancement_type": request.enhancement_type,
        "project_directory": journal_content_analyzer._get_project_directory(project),
        "existing_files": analysis.get("existing_files", []),
        "completion_map": analysis.get("completion_map", {}),
        "quality_scores": analysis.get("quality_scores", {})
    }

    # Add custom preferences
    preferences.update(request.custom_preferences)

    # Add selected recommendations
    if request.selected_recommendations:
        preferences["selected_recommendations"] = request.selected_recommendations

    # Determine agents based on enhancement type
    if request.enhancement_type == "complete_missing":
        missing = analysis.get("missing_components", [])
        if "research_findings" in missing:
            preferences["required_agents"] = ["research_agent"]
        if "journal_content" in missing:
            preferences["required_agents"] = preferences.get("required_agents", []) + ["content_curator_agent"]
        if "visual_assets" in missing:
            preferences["required_agents"] = preferences.get("required_agents", []) + ["media_agent"]
        if "pdf_generation" in missing:
            preferences["required_agents"] = preferences.get("required_agents", []) + ["pdf_builder_agent"]

    elif request.enhancement_type == "improve_quality":
        preferences["required_agents"] = ["editor_agent", "content_curator_agent"]
        if analysis.get("quality_scores", {}).get("visual_appeal", 0) < 60:
            preferences["required_agents"].append("media_agent")

    elif request.enhancement_type == "add_variant":
        preferences["required_agents"] = ["discovery_agent", "content_curator_agent", "pdf_builder_agent"]

    return preferences


def _build_quick_enhancement_preferences(enhancement_type: str, project: Project) -> Dict[str, Any]:
    """Build preferences for quick enhancement actions"""

    base_preferences = {
        "title": project.title,
        "theme": project.theme or "General Journaling",
        "action": "quick_enhance",
        "enhancement_type": enhancement_type,
        "project_directory": journal_content_analyzer._get_project_directory(project)
    }

    if enhancement_type == "add_images":
        base_preferences.update({
            "required_agents": ["media_agent"],
            "description": "Generate visual assets for existing content"
        })

    elif enhancement_type == "improve_writing":
        base_preferences.update({
            "required_agents": ["editor_agent"],
            "description": "Polish and improve writing quality"
        })

    elif enhancement_type == "expand_content":
        base_preferences.update({
            "required_agents": ["content_curator_agent", "research_agent"],
            "description": "Expand content with additional sections and insights"
        })

    elif enhancement_type == "create_pdf":
        base_preferences.update({
            "required_agents": ["pdf_builder_agent"],
            "description": "Generate professional PDF output"
        })

    return base_preferences


def _estimate_enhancement_time(enhancement_type: str, analysis: Dict[str, Any]) -> int:
    """Estimate enhancement time in minutes"""

    missing_count = len(analysis.get("missing_components", []))
    quality_score = analysis.get("quality_scores", {}).get("overall_quality", 0)

    if enhancement_type == "complete_missing":
        return missing_count * 8  # 8 minutes per missing component
    elif enhancement_type == "improve_quality":
        return 20  # Base time for quality improvements
    elif enhancement_type == "add_variant":
        return 25  # Time to create a new variant
    else:
        return 15  # Default enhancement time