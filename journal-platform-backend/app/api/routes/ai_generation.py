"""
AI Generation API Routes
Integrates existing CrewAI agent system with web UI
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import json
import asyncio
import os
import sys

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../agents"))

from ...core.deps import get_db, get_current_user
from ...models.user import User
from ...models.project import Project
from ...models.journal import JournalEntry, JournalTemplate
from ...models.export import ExportJob
from .websocket import manager

router = APIRouter()


# Pydantic models for AI generation requests
class AIGenerationRequest(BaseModel):
    theme: str = Field(..., description="Journal theme (mindfulness, productivity, creativity, etc.)")
    title_style: str = Field(..., description="Title style (inspirational, practical, creative)")
    research_depth: str = Field(default="standard", description="Research depth (basic, standard, comprehensive)")
    target_audience: str = Field(default="general", description="Target audience for the journal")
    include_images: bool = Field(default=True, description="Generate images for the journal")
    export_format: str = Field(default="pdf", description="Export format (pdf, epub, kdp)")


class AIGenerationResponse(BaseModel):
    job_id: str = Field(..., description="Unique job ID for tracking generation progress")
    status: str = Field(..., description="Initial status of the generation job")
    estimated_time: int = Field(..., description="Estimated completion time in seconds")


class GenerationProgress(BaseModel):
    job_id: str
    status: str  # 'pending', 'researching', 'curating', 'editing', 'generating_media', 'building_pdf', 'completed', 'failed'
    current_stage: str
    progress_percentage: int
    current_agent: Optional[str] = None
    estimated_time_remaining: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class JournalGenerationResult(BaseModel):
    project_id: int
    journal_content: Dict[str, Any]
    theme_data: Dict[str, Any]
    export_job_id: Optional[int] = None
    generation_metadata: Dict[str, Any]


# AI Generation Service
class AIGenerationService:
    def __init__(self):
        self.active_jobs = {}

    async def start_journal_generation(self,
                                      user_id: int,
                                      request: AIGenerationRequest,
                                      db: AsyncSession) -> AIGenerationResponse:
        """Start AI journal generation using existing CrewAI agents"""

        job_id = f"gen_{user_id}_{int(datetime.now().timestamp())}"

        # Create initial project record
        project = Project(
            user_id=user_id,
            title=f"AI Journal - {request.theme.title()}",
            description=f"AI-generated {request.theme} journal with {request.title_style} style",
            theme=request.theme,
            status="ai_generating"
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

        # Initialize job tracking
        self.active_jobs[job_id] = {
            "project_id": project.id,
            "status": "pending",
            "progress": 0,
            "current_stage": "Initializing AI generation",
            "start_time": datetime.now(),
            "user_id": user_id,
            "request_data": request.dict()
        }

        # Start background generation process
        asyncio.create_task(self._run_ai_generation(job_id, project.id, request, db))

        return AIGenerationResponse(
            job_id=job_id,
            status="pending",
            estimated_time=180  # 3 minutes estimated
        )

    async def _run_ai_generation(self,
                                 job_id: str,
                                 project_id: int,
                                 request: AIGenerationRequest,
                                 db: AsyncSession):
        """Run the actual AI generation using existing agents"""
        try:
            # Import existing agents
            from manager_agent import ManagerAgent

            # Update progress
            await self._update_progress(job_id, "researching", 10, "Starting content research...")

            # Initialize manager agent with user preferences
            manager = ManagerAgent()

            # Simulate the agent workflow (this would integrate with your existing agents)
            generation_data = await self._execute_agent_workflow(manager, request, job_id)

            # Save generated content to database
            await self._save_generated_content(project_id, generation_data, db)

            # Complete the job
            await self._update_progress(job_id, "completed", 100, "Journal generation completed!")

        except Exception as e:
            await self._update_progress(job_id, "failed", 0, f"Generation failed: {str(e)}")

    async def _execute_agent_workflow(self, manager, request: AIGenerationRequest, job_id: str) -> Dict[str, Any]:
        """Execute the existing agent workflow with progress tracking"""

        # Phase 1: Discovery and Research
        await self._update_progress(job_id, "researching", 20, "Discovering themes and researching content...")
        # This would call your discovery_agent and research_agent

        # Phase 2: Content Curation
        await self._update_progress(job_id, "curating", 40, "Curating 30-day journal content...")
        # This would call your content_curator_agent

        # Phase 3: Editing and Polish
        await self._update_progress(job_id, "editing", 60, "Editing and polishing content...")
        # This would call your editor_agent

        # Phase 4: Media Generation
        if request.include_images:
            await self._update_progress(job_id, "generating_media", 80, "Generating images and media...")
            # This would call your media_agent

        # Phase 5: PDF Building
        await self._update_progress(job_id, "building_pdf", 95, "Building professional PDF...")
        # This would call your pdf_builder_agent

        # Return mock generated data for now
        return {
            "theme": request.theme,
            "title_style": request.title_style,
            "journal_content": {
                "title": f"My {request.theme.title()} Journey",
                "intro_spread": {
                    "left": {"writeup": "Welcome to your mindfulness journey..."},
                    "right": {"writeup": "This journal will guide you through..."}
                },
                "days": [
                    {
                        "day": 1,
                        "theme": "Beginning with awareness",
                        "prompt": "Take three deep breaths and notice...",
                        "image": "day1_full.png",
                        "bottom_quote": "Every journey begins with a single step"
                    }
                    # ... more days
                ]
            },
            "theme_data": {
                "colors": {"primary": "#6B5B6", "secondary": "#E8F5E8"},
                "fonts": {"body": "DejaVu Sans", "heading": "DejaVu Sans Bold"},
                "layout": "standard"
            }
        }

    async def _save_generated_content(self, project_id: int, generation_data: Dict[str, Any], db: AsyncSession):
        """Save the AI-generated content to the database"""

        # Update project with generated content
        project = await db.get(Project, project_id)
        project.ai_generated_content = generation_data
        project.status = "ai_completed"

        # Create journal template from generated content
        template = JournalTemplate(
            user_id=project.user_id,
            name=f"{generation_data['theme'].title()} Journal Template",
            description=f"AI-generated {generation_data['theme']} journal template",
            theme=generation_data["theme"],
            ai_generated_content=json.dumps(generation_data),
            ai_prompt=f"Theme: {generation_data['theme']}, Style: {generation_data.get('title_style', 'standard')}"
        )
        db.add(template)

        await db.commit()

    async def _update_progress(self, job_id: str, status: str, progress: int, message: str):
        """Update job progress and notify via WebSocket"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id].update({
                "status": status,
                "progress": progress,
                "current_stage": message,
                "last_update": datetime.now()
            })

            # Send WebSocket update
            progress_data = GenerationProgress(
                job_id=job_id,
                status=status,
                current_stage=message,
                progress_percentage=progress
            )
            await manager.send_personal_message(progress_data.dict(), job_id)

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a generation job"""
        return self.active_jobs.get(job_id)


# Initialize service
ai_service = AIGenerationService()


@router.post("/generate-journal", response_model=AIGenerationResponse)
async def generate_journal_with_ai(
    request: AIGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start AI journal generation using existing CrewAI agents"""
    return await ai_service.start_journal_generation(current_user.id, request, db)


@router.get("/progress/{job_id}", response_model=GenerationProgress)
async def get_generation_progress(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get real-time progress of AI journal generation"""
    job_status = await ai_service.get_job_status(job_id)

    if not job_status:
        raise HTTPException(status_code=404, detail="Generation job not found")

    if job_status.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return GenerationProgress(
        job_id=job_id,
        status=job_status["status"],
        current_stage=job_status["current_stage"],
        progress_percentage=job_status["progress"],
        estimated_time_remaining=max(0, 180 - int((datetime.now() - job_status["start_time"]).total_seconds()))
    )


@router.get("/themes")
async def get_available_themes():
    """Get list of available AI journal themes"""
    return {
        "themes": [
            {"id": "mindfulness", "name": "Mindfulness", "description": "Daily mindfulness and meditation exercises"},
            {"id": "productivity", "name": "Productivity", "description": "Focus on goals and achievement"},
            {"id": "creativity", "name": "Creativity", "description": "Unlock creative potential"},
            {"id": "gratitude", "name": "Gratitude", "description": "Daily gratitude practice"},
            {"id": "fitness", "name": "Fitness", "description": "Health and wellness tracking"},
            {"id": "finance", "name": "Finance", "description": "Financial planning and mindfulness"}
        ]
    }


@router.get("/title-styles")
async def get_available_title_styles():
    """Get list of available title styles"""
    return {
        "styles": [
            {"id": "inspirational", "name": "Inspirational", "description": "Motivating and uplifting tone"},
            {"id": "practical", "name": "Practical", "description": "Straightforward and actionable"},
            {"id": "creative", "name": "Creative", "description": "Artistic and expressive"},
            {"id": "scientific", "name": "Scientific", "description": "Evidence-based and analytical"},
            {"id": "spiritual", "name": "Spiritual", "description": "Mindfulness and inner growth"}
        ]
    }


@router.post("/cancel/{job_id}")
async def cancel_generation_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel an active AI generation job"""
    job_status = await ai_service.get_job_status(job_id)

    if not job_status:
        raise HTTPException(status_code=404, detail="Generation job not found")

    if job_status.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if job_status["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")

    # Cancel the job
    await ai_service._update_progress(job_id, "failed", 0, "Job cancelled by user")

    return {"message": "Generation job cancelled successfully"}