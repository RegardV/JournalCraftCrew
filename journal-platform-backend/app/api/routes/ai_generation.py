"""
AI Generation API Routes - Redirected to CrewAI Workflow
This file has been refactored to redirect all AI generation requests to the real CrewAI workflow system.
Previously contained mock implementations that have been removed in favor of the actual 9-agent system.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pydantic import BaseModel, Field
import json

from ...core.deps import get_db, get_current_user
from ...models.user import User
from .crewai_workflow import crewai_service

router = APIRouter()


# Pydantic models for compatibility - these redirect to CrewAI workflow
class AIGenerationRequest(BaseModel):
    theme: str = Field(..., description="Journal theme (mindfulness, productivity, creativity, etc.)")
    title_style: str = Field(..., description="Title style (inspirational, practical, creative)")
    research_depth: str = Field(default="standard", description="Research depth (basic, standard, comprehensive)")
    target_audience: str = Field(default="general", description="Target audience for the journal")
    include_images: bool = Field(default=True, description="Generate images for the journal")
    export_format: str = Field(default="pdf", description="Export format (pdf, epub, kdp)")


class AIGenerationResponse(BaseModel):
    workflow_id: str = Field(..., description="CrewAI workflow ID for tracking progress")
    status: str = Field(..., description="Initial status of the workflow")
    message: str = Field(..., description="Redirect message explaining the workflow")


class GenerationProgress(BaseModel):
    workflow_id: str
    status: str
    current_stage: str
    progress_percentage: int
    current_agent: str = None
    estimated_time_remaining: int = None
    result_data: Dict[str, Any] = None
    error_message: str = None


class JournalGenerationResult(BaseModel):
    project_id: int
    workflow_id: str
    status: str
    message: str


def _convert_to_crewai_preferences(request: AIGenerationRequest) -> Dict[str, Any]:
    """Convert legacy AI generation request to CrewAI preferences format"""

    # Map research depth to insight count
    depth_mapping = {
        "basic": "light",        # 5 insights
        "standard": "medium",    # 15 insights
        "comprehensive": "deep"  # 25 insights
    }

    # Map title styles to CrewAI styles
    style_mapping = {
        "inspirational": "inspirational",
        "practical": "professional",
        "creative": "creative",
        "mindful": "mindfulness",
        "academic": "academic"
    }

    # Convert theme to CrewAI format
    theme = request.theme.lower().strip()
    if not theme.startswith("journaling for "):
        theme = f"Journaling for {theme}"

    return {
        "theme": theme,
        "title_style": style_mapping.get(request.title_style.lower(), "professional"),
        "research_depth": depth_mapping.get(request.research_depth.lower(), "medium"),
        "author_style": "Dynamic selection based on theme",  # Will be determined by onboarding agent
        "target_audience": request.target_audience,
        "include_images": request.include_images,
        "export_format": request.export_format,
        "workflow_type": "standard" if request.research_depth != "comprehensive" else "comprehensive",
        "action": "new_workflow"  # New workflow, not continuation
    }


@router.post("/generate-journal", response_model=AIGenerationResponse)
async def generate_journal(
    request: AIGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate journal using CrewAI workflow.

    This endpoint has been refactored to use the real 9-agent CrewAI system instead of mock implementations.
    The request parameters are converted to CrewAI preferences and processed through the standard workflow.

    Requires user to have configured their OpenAI API key.
    """
    try:
        # Check if user has configured their OpenAI API key
        if not current_user.openai_api_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key required. Please configure your API key in account settings before generating content."
            )

        # Convert legacy request to CrewAI preferences
        crewai_preferences = _convert_to_crewai_preferences(request)

        # Create a title for the project
        title = f"{request.title_style.title()} {request.theme.title()} Journal"

        # Start CrewAI workflow with user's OpenAI API key
        workflow_response = await crewai_service.start_workflow(
            user_id=current_user.id,
            preferences={
                **crewai_preferences,
                "title": title
            },
            db=db,
            openai_api_key=current_user.openai_api_key
        )

        return AIGenerationResponse(
            workflow_id=workflow_response.workflow_id,
            status=workflow_response.status,
            message="Journal generation started using CrewAI 9-agent system. Track progress with the workflow_id."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start CrewAI workflow: {str(e)}"
        )


@router.get("/progress/{workflow_id}", response_model=GenerationProgress)
async def get_generation_progress(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get journal generation progress from CrewAI workflow.

    This endpoint now redirects to the CrewAI workflow status tracking system.
    """
    try:
        # Get progress from CrewAI workflow service
        workflow_status = await crewai_service.get_workflow_status(workflow_id, current_user.id)

        if not workflow_status:
            raise HTTPException(
                status_code=404,
                detail="Workflow not found or access denied"
            )

        # Convert CrewAI status to legacy format
        return GenerationProgress(
            workflow_id=workflow_status.workflow_id,
            status=workflow_status.status,
            current_stage=workflow_status.current_agent or "Initializing",
            progress_percentage=workflow_status.progress_percentage,
            current_agent=workflow_status.current_agent,
            estimated_time_remaining=workflow_status.estimated_time_remaining,
            result_data=workflow_status.result_data,
            error_message=workflow_status.error_message
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workflow progress: {str(e)}"
        )


@router.post("/continue-workflow/{workflow_id}")
async def continue_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Continue a paused or interrupted workflow.

    This endpoint leverages the CrewAI workflow continuation capabilities.
    """
    try:
        # Check if workflow exists and can be continued
        workflow_status = await crewai_service.get_workflow_status(workflow_id, current_user.id)

        if not workflow_status:
            raise HTTPException(
                status_code=404,
                detail="Workflow not found"
            )

        if workflow_status.status not in ["paused", "interrupted"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot continue workflow in status: {workflow_status.status}"
            )

        # Resume the workflow (this would be implemented in crewai_service)
        await crewai_service.resume_workflow(workflow_id, current_user.id)

        return {"message": "Workflow resumed successfully", "workflow_id": workflow_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to continue workflow: {str(e)}"
        )


@router.get("/result/{workflow_id}", response_model=JournalGenerationResult)
async def get_generation_result(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the final result of journal generation.

    This endpoint provides the generation results from the CrewAI workflow.
    """
    try:
        # Get final workflow status
        workflow_status = await crewai_service.get_workflow_status(workflow_id, current_user.id)

        if not workflow_status:
            raise HTTPException(
                status_code=404,
                detail="Workflow not found"
            )

        if workflow_status.status not in ["completed", "failed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Workflow not completed yet. Current status: {workflow_status.status}"
            )

        return JournalGenerationResult(
            project_id=workflow_status.project_id,
            workflow_id=workflow_status.workflow_id,
            status=workflow_status.status,
            message="Journal generation completed through CrewAI 9-agent system" if workflow_status.status == "completed" else "Journal generation failed"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get generation result: {str(e)}"
        )


# Legacy endpoint compatibility
@router.get("/health")
async def health_check():
    """
    Health check endpoint for backwards compatibility.

    Returns status indicating this endpoint now redirects to CrewAI workflow.
    """
    return {
        "status": "healthy",
        "message": "AI Generation API has been refactored to use CrewAI 9-agent system",
        "redirect": "All generation requests now use real CrewAI workflows",
        "deprecated": "This endpoint exists for backwards compatibility only"
    }