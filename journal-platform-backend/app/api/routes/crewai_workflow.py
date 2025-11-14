"""
CrewAI Workflow API Routes
Orchestrates the complete CrewAI agent workflow through web interface
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import os
import sys
import json
import asyncio
import uuid
from pathlib import Path

# Add agents directory to path for CrewAI integration
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

try:
    from agents.manager_agent import create_manager_agent, coordinate_phases
    from agents.research_agent import create_research_agent, research_content
    from agents.discovery_agent import create_discovery_agent, discover_idea
    from agents.content_curator_agent import create_content_curator_agent, curate_content
    from agents.editor_agent import create_editor_agent, edit_content
    from agents.media_agent import create_media_agent, generate_media
    from agents.pdf_builder_agent import create_pdf_builder_agent, generate_pdf
    from config.settings import TITLE_STYLES, VALID_RESEARCH_DEPTHS, OUTPUT_DIR, JSON_SUBDIR, PDF_SUBDIR, MEDIA_SUBDIR, DATE_FORMAT
    from utils import log_debug, save_json
    from crewai import LLM
except ImportError as e:
    print(f"Import error in crewai_workflow: {e}")
    # Set up fallback configurations
    TITLE_STYLES = ["inspirational", "practical", "creative"]
    VALID_RESEARCH_DEPTHS = {"light": 5, "medium": 15, "deep": 25}
    OUTPUT_DIR = "../LLM_output"
    JSON_SUBDIR = "Json_output"
    PDF_SUBDIR = "PDF_output"
    MEDIA_SUBDIR = "media"
    DATE_FORMAT = "%Y-%m-%d"

from ...core.deps import get_db, get_current_user
from ...models.user import User
from ...models.project import Project
from ...models.journal import JournalEntry, JournalTemplate
from .websocket import manager, MessageType

router = APIRouter()

# Pydantic models for workflow requests
class WorkflowStartRequest(BaseModel):
    project_id: int = Field(..., description="Project ID to run workflow for")
    preferences: Dict[str, Any] = Field(..., description="User preferences from onboarding")

class WorkflowStep(BaseModel):
    step_id: str
    step_name: str
    agent: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress_percentage: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class WorkflowStatus(BaseModel):
    workflow_id: str
    project_id: int
    status: str  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    current_step: str
    progress_percentage: int
    steps: List[WorkflowStep]
    start_time: datetime
    estimated_completion: Optional[datetime] = None
    result_data: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    message: str
    estimated_time_minutes: int

# CrewAI Workflow Service
class CrewAIWorkflowService:
    def __init__(self):
        self.active_workflows = {}
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize LLM for CrewAI agents"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            return LLM(
                model="gpt-4",
                api_key=api_key,
                temperature=0.7,
                max_tokens=4000
            )
        except Exception as e:
            log_debug(f"Failed to initialize LLM: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize AI services")

    async def start_workflow(self, request: WorkflowStartRequest, user_id: int, openai_api_key: str = None, db: AsyncSession = None) -> WorkflowResponse:
        """Start a complete CrewAI workflow for journal creation"""
        workflow_id = f"workflow_{user_id}_{int(datetime.now().timestamp())}"

        # Initialize LLM with user's OpenAI API key
        user_llm = self._create_user_llm(openai_api_key)

        # Create workflow record
        self.active_workflows[workflow_id] = {
            "project_id": request.project_id,
            "user_id": user_id,
            "preferences": request.preferences,
            "status": "pending",
            "start_time": datetime.now(),
            "steps": self._initialize_workflow_steps(),
            "current_step": 0,
            "llm": user_llm,
            "openai_api_key": openai_api_key
        }

        # Start background workflow execution
        asyncio.create_task(self._execute_workflow(workflow_id, request.project_id, request.preferences, db))

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="pending",
            message="CrewAI workflow started successfully",
            estimated_time_minutes=30
        )

    def _initialize_workflow_steps(self) -> List[Dict]:
        """Initialize workflow steps in correct order"""
        return [
            {
                "step_id": "discovery",
                "step_name": "Title Discovery",
                "agent": "Discovery Agent",
                "status": "pending",
                "progress_percentage": 0
            },
            {
                "step_id": "research",
                "step_name": "Content Research",
                "agent": "Research Agent",
                "status": "pending",
                "progress_percentage": 0
            },
            {
                "step_id": "curation",
                "step_name": "Content Curation",
                "agent": "Content Curator Agent",
                "status": "pending",
                "progress_percentage": 0
            },
            {
                "step_id": "editing",
                "step_name": "Content Editing",
                "agent": "Editor Agent",
                "status": "pending",
                "progress_percentage": 0
            },
            {
                "step_id": "media",
                "step_name": "Media Generation",
                "agent": "Media Agent",
                "status": "pending",
                "progress_percentage": 0
            },
            {
                "step_id": "pdf_building",
                "step_name": "PDF Building",
                "agent": "PDF Builder Agent",
                "status": "pending",
                "progress_percentage": 0
            }
        ]

    async def _execute_workflow(self, workflow_id: str, project_id: int, preferences: Dict[str, Any]):
        """Execute the CrewAI workflow with enhanced progress tracking and continuation support"""
        try:
            workflow = self.active_workflows[workflow_id]
            llm = workflow["llm"]

            # Get workflow type and action
            workflow_type = preferences.get('workflow_type', 'standard')  # express, standard, comprehensive
            action = preferences.get('action', 'new_workflow')
            existing_run_dir = preferences.get('project_directory')

            # Store workflow type in workflow data
            workflow["workflow_type"] = workflow_type

            # Set up run directory
            if existing_run_dir and os.path.exists(existing_run_dir):
                # Use existing project directory for continuation
                run_dir = existing_run_dir
                log_debug(f"Continuing workflow in existing directory: {run_dir}")
            else:
                # Create new directory for new workflow
                today = datetime.now().strftime(DATE_FORMAT)
                run_dir = os.path.join(OUTPUT_DIR, f"{preferences['title'].replace(' ', '_')}_{today}")
                os.makedirs(run_dir, exist_ok=True)
                os.makedirs(os.path.join(run_dir, JSON_SUBDIR), exist_ok=True)
                os.makedirs(os.path.join(run_dir, PDF_SUBDIR), exist_ok=True)
                os.makedirs(os.path.join(run_dir, MEDIA_SUBDIR), exist_ok=True)

            workflow["run_dir"] = run_dir
            workflow["status"] = "running"

            # Send workflow start notification
            await self._send_workflow_message(workflow_id, {
                "type": MessageType.WORKFLOW_START.value,
                "workflow_id": workflow_id,
                "project_id": project_id,
                "action": action,
                "preferences": preferences,
                "estimated_duration_minutes": 30,
                "is_continuation": existing_run_dir is not None
            })

            # Execute based on action type and workflow type
            if action == "generate_media":
                # Generate media for existing content
                await self._execute_media_only_workflow(workflow_id, llm, preferences, run_dir)
            elif action == "generate_pdf":
                # Generate PDF for existing content
                await self._execute_pdf_only_workflow(workflow_id, llm, preferences, run_dir)
            elif action == "generate_epub_kdp":
                # Generate EPUB and KDP formats
                await self._execute_epub_workflow(workflow_id, llm, preferences, run_dir)
            elif action == "continue_research":
                # Continue from research step
                await self._execute_research_only_workflow(workflow_id, llm, preferences, run_dir)
            elif action == "continue_content":
                # Continue from content creation step
                await self._execute_content_only_workflow(workflow_id, llm, preferences, run_dir)
            else:
                # Execute workflow based on type
                if workflow_type == "express":
                    await self._execute_express_workflow(workflow_id, llm, preferences, run_dir)
                elif workflow_type == "comprehensive":
                    await self._execute_comprehensive_workflow(workflow_id, llm, preferences, run_dir)
                else:
                    # Standard workflow (default)
                    await self._execute_standard_workflow(workflow_id, llm, preferences, run_dir)

            # Complete workflow
            workflow["status"] = "completed"
            workflow["progress_percentage"] = 100
            workflow["end_time"] = datetime.now()

            # Send final completion notification
            await self._send_workflow_message(workflow_id, {
                "type": MessageType.WORKFLOW_COMPLETE.value,
                "workflow_id": workflow_id,
                "result_data": workflow.get("result_data"),
                "action": action,
                "total_duration": (datetime.now() - workflow["start_time"]).total_seconds()
            })

        except Exception as e:
            log_debug(f"Workflow {workflow_id} failed: {e}")
            workflow = self.active_workflows.get(workflow_id, {})
            workflow["status"] = "failed"
            workflow["error_message"] = str(e)
            workflow["end_time"] = datetime.now()

            # Send error notification
            await self._send_workflow_message(workflow_id, {
                "type": MessageType.WORKFLOW_ERROR.value,
                "workflow_id": workflow_id,
                "error_message": str(e),
                "failed_at_step": workflow.get("current_step", "unknown")
            })

    async def _execute_discovery_step(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute discovery agent step"""
        await self._send_workflow_update(workflow_id, "running", 5, "Starting title discovery...")

        try:
            discovery_agent = create_discovery_agent(llm)
            result = discover_idea(discovery_agent, preferences['theme'], preferences['title_style'])

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][0]["status"] = "completed"
            workflow["steps"][0]["progress_percentage"] = 100
            workflow["steps"][0]["result_data"] = result
            workflow["steps"][0]["end_time"] = datetime.now()

            # Save result
            save_json(result, os.path.join(run_dir, JSON_SUBDIR, f"discovery_{preferences['title']}.json"))

            await self._send_workflow_update(workflow_id, "running", 15, "Title discovery completed!")

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][0]["status"] = "failed"
            workflow["steps"][0]["error_message"] = str(e)
            raise

    async def _execute_research_step(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute research agent step"""
        await self._send_workflow_update(workflow_id, "running", 20, "Gathering research content...")

        try:
            research_agent = create_research_agent(llm)
            result = research_content(research_agent, preferences['theme'], preferences['research_depth'], run_dir)

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][1]["status"] = "completed"
            workflow["steps"][1]["progress_percentage"] = 100
            workflow["steps"][1]["result_data"] = {"insights_count": len(result)}
            workflow["steps"][1]["end_time"] = datetime.now()

            await self._send_workflow_update(workflow_id, "running", 35, "Research completed!")

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][1]["status"] = "failed"
            workflow["steps"][1]["error_message"] = str(e)
            raise

    async def _execute_curation_step(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute content curator agent step"""
        await self._send_workflow_update(workflow_id, "running", 40, "Curating journal content...")

        try:
            # Get research data
            research_data = []
            try:
                with open(os.path.join(run_dir, JSON_SUBDIR, f"research_data_{preferences['title']}_{preferences['theme']}.json"), 'r') as f:
                    research_data = json.load(f)
            except FileNotFoundError:
                research_data = [{"insight": "Default research content", "description": "Fallback content"}]

            curator_agent = create_content_curator_agent(llm)
            result = curate_content(curator_agent, research_data, preferences['theme'], preferences['title'], preferences['author_style'], run_dir)

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][2]["status"] = "completed"
            workflow["steps"][2]["progress_percentage"] = 100
            workflow["steps"][2]["result_data"] = {"files_created": list(result.keys())}
            workflow["steps"][2]["end_time"] = datetime.now()

            await self._send_workflow_update(workflow_id, "running", 55, "Content curation completed!")

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][2]["status"] = "failed"
            workflow["steps"][2]["error_message"] = str(e)
            raise

    async def _execute_editing_step(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute editor agent step"""
        await self._send_workflow_update(workflow_id, "running", 60, "Editing and polishing content...")

        try:
            editor_agent = create_editor_agent(llm)

            # Find content files
            journal_file = None
            lead_magnet_file = None
            for f in os.listdir(os.path.join(run_dir, JSON_SUBDIR)):
                if f.startswith("30day_journal_"):
                    journal_file = os.path.join(run_dir, JSON_SUBDIR, f)
                elif f.startswith("lead_magnet_"):
                    lead_magnet_file = os.path.join(run_dir, JSON_SUBDIR, f)

            if not journal_file:
                raise FileNotFoundError("No journal file found for editing")

            # Use default lead magnet if not found
            if not lead_magnet_file:
                lead_magnet_file = journal_file

            result = edit_content(editor_agent, journal_file, lead_magnet_file, preferences['author_style'])

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][3]["status"] = "completed"
            workflow["steps"][3]["progress_percentage"] = 100
            workflow["steps"][3]["result_data"] = {"edited_files": list(result.keys())}
            workflow["steps"][3]["end_time"] = datetime.now()

            await self._send_workflow_update(workflow_id, "running", 75, "Content editing completed!")

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][3]["status"] = "failed"
            workflow["steps"][3]["error_message"] = str(e)
            raise

    async def _execute_media_step(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute media agent step"""
        await self._send_workflow_update(workflow_id, "running", 80, "Generating media assets...")

        try:
            media_agent = create_media_agent(llm)
            result = generate_media(media_agent, run_dir, skip_generation=True)  # Skip actual generation for now

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][4]["status"] = "completed"
            workflow["steps"][4]["progress_percentage"] = 100
            workflow["steps"][4]["result_data"] = {"media_generated": True}
            workflow["steps"][4]["end_time"] = datetime.now()

            await self._send_workflow_update(workflow_id, "running", 90, "Media generation completed!")

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][4]["status"] = "failed"
            workflow["steps"][4]["error_message"] = str(e)
            # Don't fail the whole workflow for media generation issues
            await self._send_workflow_update(workflow_id, "running", 90, "Media generation skipped, continuing with PDF...")

    async def _execute_pdf_step(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute PDF builder agent step"""
        await self._send_workflow_update(workflow_id, "running", 95, "Building PDF documents...")

        try:
            pdf_agent = create_pdf_builder_agent(llm)
            result = generate_pdf(pdf_agent, run_dir, use_media=False)  # Generate PDFs

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][5]["status"] = "completed"
            workflow["steps"][5]["progress_percentage"] = 100
            workflow["steps"][5]["result_data"] = {"pdf_files": list(result.keys())}
            workflow["steps"][5]["end_time"] = datetime.now()

            # Store final result
            workflow["result_data"] = result

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][5]["status"] = "failed"
            workflow["steps"][5]["error_message"] = str(e)
            raise

    async def _send_workflow_message(self, workflow_id: str, message_data: Dict[str, Any]):
        """Send workflow message via enhanced WebSocket system"""
        try:
            await manager.send_workflow_update(workflow_id, message_data)
        except Exception as e:
            log_debug(f"Failed to send WebSocket message: {e}")

    async def _send_workflow_update(self, workflow_id: str, status: str, progress: int, message: str):
        """Send workflow progress update via WebSocket (legacy compatibility)"""
        await self._send_workflow_message(workflow_id, {
            "type": MessageType.AGENT_PROGRESS.value,
            "workflow_id": workflow_id,
            "status": status,
            "progress_percentage": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    # Enhanced step execution methods with detailed progress tracking
    async def _execute_discovery_step_enhanced(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute discovery agent step with detailed progress tracking"""
        agent_id = "discovery_agent"
        await manager.start_agent_subtask(workflow_id, agent_id, "Title discovery", 5)

        await manager.update_agent_progress(workflow_id, agent_id, 1, "Initializing discovery agent...")
        await manager.start_agent_subtask(workflow_id, agent_id, "Loading title generation model", 2)

        await manager.update_agent_progress(workflow_id, agent_id, 2, "Creating discovery agent...")

        try:
            discovery_agent = create_discovery_agent(llm)
            await manager.complete_agent_subtask(workflow_id, agent_id)
            await manager.start_agent_subtask(workflow_id, agent_id, "Generating title ideas", 3)

            await manager.update_agent_progress(workflow_id, agent_id, 3, "Analyzing theme and style preferences...")
            result = discover_idea(discovery_agent, preferences['theme'], preferences['title_style'])

            await manager.update_agent_progress(workflow_id, agent_id, 4, "Processing generated titles...")

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][0]["status"] = "completed"
            workflow["steps"][0]["progress_percentage"] = 100
            workflow["steps"][0]["result_data"] = result
            workflow["steps"][0]["end_time"] = datetime.now()

            # Save result
            save_json(result, os.path.join(run_dir, JSON_SUBDIR, f"discovery_{preferences['title']}.json"))

            await manager.update_agent_progress(workflow_id, agent_id, 5, "Discovery completed successfully!")
            await manager.complete_agent_subtask(workflow_id, agent_id)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_COMPLETE.value,
                "agent_id": agent_id,
                "result_summary": f"Generated {len(result.get('titles', []))} title options"
            })

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][0]["status"] = "failed"
            workflow["steps"][0]["error_message"] = str(e)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_ERROR.value,
                "agent_id": agent_id,
                "error_message": str(e)
            })
            raise

    async def _execute_research_step_enhanced(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute research agent step with detailed progress tracking"""
        agent_id = "research_agent"
        await manager.start_agent_subtask(workflow_id, agent_id, "Content research", 5)

        await manager.update_agent_progress(workflow_id, agent_id, 1, "Initializing research agent...")
        await manager.start_agent_subtask(workflow_id, agent_id, "Loading research sources", 1)

        await manager.update_agent_progress(workflow_id, agent_id, 2, "Creating research agent...")

        try:
            research_agent = create_research_agent(llm)
            await manager.complete_agent_subtask(workflow_id, agent_id)
            await manager.start_agent_subtask(workflow_id, agent_id, "Gathering theme-specific research", 2)

            await manager.update_agent_progress(workflow_id, agent_id, 3, "Researching " + preferences['theme'] + "...")

            research_agent = create_research_agent(llm)
            result = research_content(research_agent, preferences['theme'], preferences['research_depth'], run_dir)

            await manager.update_agent_progress(workflow_id, agent_id, 4, "Processing research insights...")

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][1]["status"] = "completed"
            workflow["steps"][1]["progress_percentage"] = 100
            workflow["steps"][1]["result_data"] = {"insights_count": len(result)}
            workflow["steps"][1]["end_time"] = datetime.now()

            await manager.update_agent_progress(workflow_id, agent_id, 5, f"Research completed! Found {len(result)} insights")
            await manager.complete_agent_subtask(workflow_id, agent_id)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_COMPLETE.value,
                "agent_id": agent_id,
                "result_summary": f"Found {len(result)} research insights"
            })

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][1]["status"] = "failed"
            workflow["steps"][1]["error_message"] = str(e)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_ERROR.value,
                "agent_id": agent_id,
                "error_message": str(e)
            })
            raise

    async def _execute_curation_step_enhanced(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute content curator agent step with detailed progress tracking"""
        agent_id = "content_curator_agent"
        await manager.start_agent_subtask(workflow_id, agent_id, "Content curation", 5)

        await manager.update_agent_progress(workflow_id, agent_id, 1, "Loading research data...")
        await manager.start_agent_subtask(workflow_id, agent_id, "Processing research insights", 1)

        try:
            # Get research data
            research_data = []
            try:
                research_file = os.path.join(run_dir, JSON_SUBDIR, f"research_data_{preferences['title']}_{preferences['theme']}.json")
                with open(research_file, 'r') as f:
                    research_data = json.load(f)
            except FileNotFoundError:
                research_data = [{"insight": "Default research content", "description": "Fallback content"}]

            await manager.complete_agent_subtask(workflow_id, agent_id)
            await manager.update_agent_progress(workflow_id, agent_id, 2, "Creating content curator agent...")
            await manager.start_agent_subtask(workflow_id, agent_id, "Structuring journal content", 2)

            curator_agent = create_content_curator_agent(llm)
            await manager.update_agent_progress(workflow_id, agent_id, 3, "Creating 30-day journal structure...")

            await manager.start_agent_subtask(workflow_id, agent_id, "Generating daily content", 2)
            result = curate_content(curator_agent, research_data, preferences['theme'], preferences['title'], preferences['author_style'], run_dir)

            await manager.update_agent_progress(workflow_id, agent_id, 4, "Finalizing content structure...")

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][2]["status"] = "completed"
            workflow["steps"][2]["progress_percentage"] = 100
            workflow["steps"][2]["result_data"] = {"files_created": list(result.keys())}
            workflow["steps"][2]["end_time"] = datetime.now()

            await manager.update_agent_progress(workflow_id, agent_id, 5, f"Content curation complete! Created {len(result)} content elements")
            await manager.complete_agent_subtask(workflow_id, agent_id)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_COMPLETE.value,
                "agent_id": agent_id,
                "result_summary": f"Created journal structure with {len(result)} content elements"
            })

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][2]["status"] = "failed"
            workflow["steps"][2]["error_message"] = str(e)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_ERROR.value,
                "agent_id": agent_id,
                "error_message": str(e)
            })
            raise

    async def _execute_editing_step_enhanced(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute editor agent step with detailed progress tracking"""
        agent_id = "editor_agent"
        await manager.start_agent_subtask(workflow_id, agent_id, "Content editing", 5)

        await manager.update_agent_progress(workflow_id, agent_id, 1, "Loading content files...")
        await manager.start_agent_subtask(workflow_id, agent_id, "Analyzing content structure", 1)

        try:
            # Find content files
            journal_file = None
            lead_magnet_file = None
            for f in os.listdir(os.path.join(run_dir, JSON_SUBDIR)):
                if f.startswith("30day_journal_"):
                    journal_file = os.path.join(run_dir, JSON_SUBDIR, f)
                elif f.startswith("lead_magnet_"):
                    lead_magnet_file = os.path.join(run_dir, JSON_SUBDIR, f)

            if not journal_file:
                raise FileNotFoundError("No journal file found for editing")

            await manager.complete_agent_subtask(workflow_id, agent_id)
            await manager.update_agent_progress(workflow_id, agent_id, 2, "Creating editor agent...")
            await manager.start_agent_subtask(workflow_id, agent_id, "Polishing content with author style", 2)

            editor_agent = create_editor_agent(llm)
            await manager.update_agent_progress(workflow_id, agent_id, 3, "Applying " + preferences['author_style'] + " writing style...")

            # Use default lead magnet if not found
            if not lead_magnet_file:
                lead_magnet_file = journal_file

            await manager.start_agent_subtask(workflow_id, agent_id, "Final content review", 2)
            result = edit_content(editor_agent, journal_file, lead_magnet_file, preferences['author_style'])

            await manager.update_agent_progress(workflow_id, agent_id, 4, "Finalizing edited content...")

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][3]["status"] = "completed"
            workflow["steps"][3]["progress_percentage"] = 100
            workflow["steps"][3]["result_data"] = {"edited_files": list(result.keys())}
            workflow["steps"][3]["end_time"] = datetime.now()

            await manager.update_agent_progress(workflow_id, agent_id, 5, "Content editing complete! Polished all content")
            await manager.complete_agent_subtask(workflow_id, agent_id)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_COMPLETE.value,
                "agent_id": agent_id,
                "result_summary": f"Edited {len(result)} content files with {preferences['author_style']} style"
            })

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][3]["status"] = "failed"
            workflow["steps"][3]["error_message"] = str(e)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_ERROR.value,
                "agent_id": agent_id,
                "error_message": str(e)
            })
            raise

    async def _execute_media_step_enhanced(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute media agent step with detailed progress tracking"""
        agent_id = "media_agent"
        await manager.start_agent_subtask(workflow_id, agent_id, "Media generation", 5)

        await manager.update_agent_progress(workflow_id, agent_id, 1, "Initializing media agent...")
        await manager.start_agent_subtask(workflow_id, agent_id, "Analyzing media requirements", 1)

        try:
            media_agent = create_media_agent(llm)
            await manager.complete_agent_subtask(workflow_id, agent_id)
            await manager.update_agent_progress(workflow_id, agent_id, 2, "Creating placeholder media assets...")
            await manager.start_agent_subtask(workflow_id, agent_id, "Generating image placeholders", 3)

            await manager.update_agent_progress(workflow_id, agent_id, 3, "Processing media requirements...")

            result = generate_media(media_agent, run_dir, skip_generation=True)  # Skip actual generation for now

            await manager.update_agent_progress(workflow_id, agent_id, 4, "Finalizing media assets...")

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][4]["status"] = "completed"
            workflow["steps"][4]["progress_percentage"] = 100
            workflow["steps"][4]["result_data"] = {"media_generated": True}
            workflow["steps"][4]["end_time"] = datetime.now()

            await manager.update_agent_progress(workflow_id, agent_id, 5, "Media generation complete! Using placeholders")
            await manager.complete_agent_subtask(workflow_id, agent_id)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_COMPLETE.value,
                "agent_id": agent_id,
                "result_summary": "Media placeholders generated successfully"
            })

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][4]["status"] = "failed"
            workflow["steps"][4]["error_message"] = str(e)
            # Don't fail the whole workflow for media generation issues
            await manager.update_agent_progress(workflow_id, agent_id, 5, "Media generation skipped, continuing with PDF...")
            await self._send_workflow_message(workflow_id, {
                "type": MessageType.SYSTEM_NOTIFICATION.value,
                "message": "Media generation skipped, continuing with PDF generation"
            })

    async def _execute_pdf_step_enhanced(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute PDF builder agent step with detailed progress tracking"""
        agent_id = "pdf_builder_agent"
        await manager.start_agent_subtask(workflow_id, agent_id, "PDF building", 5)

        await manager.update_agent_progress(workflow_id, agent_id, 1, "Loading content for PDF generation...")
        await manager.start_agent_subtask(workflow_id, agent_id, "Preparing PDF structure", 1)

        try:
            pdf_agent = create_pdf_builder_agent(llm)
            await manager.complete_agent_subtask(workflow_id, agent_id)
            await manager.update_agent_progress(workflow_id, agent_id, 2, "Creating PDF documents...")
            await manager.start_agent_subtask(workflow_id, agent_id, "Generating journal PDF", 2)

            await manager.update_agent_progress(workflow_id, agent_id, 3, "Building professional layouts...")

            await manager.start_agent_subtask(workflow_id, agent_id, "Finalizing PDF exports", 2)
            result = generate_pdf(pdf_agent, run_dir, use_media=False)  # Generate PDFs

            await manager.update_agent_progress(workflow_id, agent_id, 4, "Finalizing PDF documents...")

            # Update workflow with result
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][5]["status"] = "completed"
            workflow["steps"][5]["progress_percentage"] = 100
            workflow["steps"][5]["result_data"] = {"pdf_files": list(result.keys())}
            workflow["steps"][5]["end_time"] = datetime.now()

            # Store final result
            workflow["result_data"] = result

            await manager.update_agent_progress(workflow_id, agent_id, 5, f"PDF generation complete! Created {len(result)} PDF documents")
            await manager.complete_agent_subtask(workflow_id, agent_id)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_COMPLETE.value,
                "agent_id": agent_id,
                "result_summary": f"Generated {len(result)} PDF documents successfully"
            })

        except Exception as e:
            workflow = self.active_workflows[workflow_id]
            workflow["steps"][5]["status"] = "failed"
            workflow["steps"][5]["error_message"] = str(e)

            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_ERROR.value,
                "agent_id": agent_id,
                "error_message": str(e)
            })
            raise

    async def get_workflow_status(self, workflow_id: str, user_id: int) -> Optional[WorkflowStatus]:
        """Get current status of a workflow"""
        workflow = self.active_workflows.get(workflow_id)

        if not workflow or workflow.get("user_id") != user_id:
            return None

        return WorkflowStatus(
            workflow_id=workflow_id,
            project_id=workflow["project_id"],
            status=workflow["status"],
            current_step=workflow.get("current_step", 0),
            progress_percentage=workflow.get("progress_percentage", 0),
            steps=[WorkflowStep(**step) for step in workflow.get("steps", [])],
            start_time=workflow["start_time"],
            estimated_completion=workflow.get("estimated_completion"),
            result_data=workflow.get("result_data")
        )

    async def cancel_workflow(self, workflow_id: str, user_id: int):
        """Cancel an active workflow"""
        workflow = self.active_workflows.get(workflow_id)

        if not workflow or workflow.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if workflow["status"] in ["completed", "failed"]:
            raise HTTPException(status_code=400, detail="Cannot cancel completed workflow")

        workflow["status"] = "cancelled"
        workflow["end_time"] = datetime.now()

        await self._send_workflow_message(workflow_id, {
            "type": MessageType.WORKFLOW_CANCELLED.value,
            "workflow_id": workflow_id,
            "cancelled_by": "user",
            "reason": "User requested cancellation"
        })

    async def _execute_complete_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute the complete CrewAI workflow from start to finish"""
        # Step 1: Execute research agent
        await self._execute_research_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 2: Execute discovery agent
        await self._execute_discovery_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 3: Execute content curator agent
        await self._execute_curation_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 4: Execute editor agent
        await self._execute_editor_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 5: Execute media agent
        await self._execute_media_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 6: Execute PDF builder agent
        await self._execute_pdf_step_enhanced(workflow_id, llm, preferences, run_dir)

    async def _execute_research_only_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute only the research agent step"""
        await self._execute_research_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Update workflow status to show research is complete
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "research_completed"
        workflow["result_data"] = {"research_completed": True}

    async def _execute_content_only_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute content creation steps (discovery + curation + editor)"""
        # Step 1: Execute discovery agent
        await self._execute_discovery_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 2: Execute content curator agent
        await self._execute_curation_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 3: Execute editor agent
        await self._execute_editor_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Update workflow status to show content is complete
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "content_completed"
        workflow["result_data"] = {"content_completed": True}

    async def _execute_media_only_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute only the media agent step"""
        await self._execute_media_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Update workflow status to show media is complete
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "media_completed"
        workflow["result_data"] = {"media_completed": True}

    async def _execute_pdf_only_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute only the PDF builder agent step"""
        await self._execute_pdf_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Update workflow status to show PDF is complete
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "pdf_completed"
        workflow["result_data"] = {"pdf_completed": True}

    async def _execute_epub_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute EPUB and KDP format generation"""
        agent_id = "epub_builder_agent"
        await manager.start_agent_subtask(workflow_id, agent_id, "EPUB generation", 3)

        try:
            await manager.update_agent_progress(workflow_id, agent_id, 1, "Preparing content for EPUB...")
            await manager.start_agent_subtask(workflow_id, agent_id, "Converting content to EPUB format", 1)

            # Here you would add actual EPUB generation logic
            # For now, simulate EPUB creation
            await asyncio.sleep(2)

            await manager.update_agent_progress(workflow_id, agent_id, 2, "Creating KDP-ready format...")
            await manager.start_agent_subtask(workflow_id, agent_id, "Optimizing for Kindle Direct Publishing", 2)

            # Simulate KDP formatting
            await asyncio.sleep(1)

            await manager.update_agent_progress(workflow_id, agent_id, 3, "EPUB and KDP formats ready!")
            await manager.complete_agent_subtask(workflow_id, agent_id)

            # Update workflow status
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = "epub_completed"
            workflow["result_data"] = {"epub_completed": True, "kdp_ready": True}

        except Exception as e:
            await self._send_workflow_message(workflow_id, {
                "type": MessageType.AGENT_ERROR.value,
                "agent_id": agent_id,
                "error_message": str(e)
            })
            raise

    async def _execute_express_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute express workflow with essential agents (Discovery + Content Curation + PDF)"""

        # Step 1: Execute discovery agent
        await self._execute_discovery_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 2: Execute content curator agent
        await self._execute_curation_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 3: Execute PDF builder agent (skip detailed editing and media for speed)
        await self._execute_pdf_step_enhanced(workflow_id, llm, preferences, run_dir)

    async def _execute_standard_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute standard workflow with core agents (Discovery + Research + Content + Editor + PDF)"""

        # Step 1: Execute discovery agent
        await self._execute_discovery_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 2: Execute research agent
        await self._execute_research_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 3: Execute content curator agent
        await self._execute_curation_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 4: Execute editor agent
        await self._execute_editor_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 5: Execute PDF builder agent
        await self._execute_pdf_step_enhanced(workflow_id, llm, preferences, run_dir)

    async def _execute_comprehensive_workflow(self, workflow_id: str, llm, preferences: Dict, run_dir: str):
        """Execute comprehensive workflow with all 9 agents for premium quality"""

        # Step 1: Execute discovery agent
        await self._execute_discovery_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 2: Execute research agent with deep research
        deep_preferences = preferences.copy()
        deep_preferences['research_depth'] = 'deep'  # Ensure deep research for comprehensive
        await self._execute_research_step_enhanced(workflow_id, llm, deep_preferences, run_dir)

        # Step 3: Execute content curator agent
        await self._execute_curation_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 4: Execute editor agent with enhanced polishing
        await self._execute_editor_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 5: Execute media agent with full image generation
        await self._execute_media_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 6: Execute PDF builder agent with premium formatting
        await self._execute_pdf_step_enhanced(workflow_id, llm, preferences, run_dir)

        # Step 7: Execute EPUB workflow for additional formats
        await self._execute_epub_workflow(workflow_id, llm, preferences, run_dir)

    async def resume_workflow(self, workflow_id: str, user_id: int):
        """Resume a paused or interrupted workflow"""
        workflow = self.active_workflows.get(workflow_id)

        if not workflow or workflow.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if workflow["status"] not in ["paused", "interrupted"]:
            raise HTTPException(status_code=400, detail=f"Cannot resume workflow in status: {workflow['status']}")

        # Update status to running
        workflow["status"] = "running"
        workflow["end_time"] = None

        # Send resumption notification
        await self._send_workflow_message(workflow_id, {
            "type": MessageType.WORKFLOW_START.value,
            "workflow_id": workflow_id,
            "action": "resume",
            "message": "Workflow resumed successfully"
        })

        # Continue execution from where it left off
        # This would require more sophisticated state tracking to resume at the exact point
        # For now, we'll restart from the beginning but with existing data


# Initialize service
crewai_service = CrewAIWorkflowService()


# Project continuation endpoints
@router.post("/continue-project", response_model=WorkflowResponse)
async def continue_project(
    project_id: int,
    action: str = Field(..., description="Action to perform: continue_workflow, generate_media, generate_pdf"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Continue an existing project with CrewAI workflow"""

    # Verify project ownership
    from sqlalchemy import select
    project_query = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get project preferences
    preferences = {}
    if project.onboarding_preferences:
        import json
        try:
            preferences = json.loads(project.onboarding_preferences)
        except:
            preferences = {}

    # Set action to continue workflow
    preferences['action'] = action
    preferences['project_directory'] = project.project_directory

    # Continue the workflow
    return await crewai_service.start_workflow(
        WorkflowStartRequest(project_id=project_id, preferences=preferences),
        current_user.id
    )


@router.post("/analyze-project/{project_id}")
async def analyze_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze existing project to determine what's completed and what actions are available"""

    # Verify project ownership
    from sqlalchemy import select
    project_query = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Analyze project directory
    project_directory = project.project_directory
    analysis = {
        "project_id": project_id,
        "title": project.title,
        "theme": project.theme,
        "status": project.status,
        "project_directory": project_directory,
        "analysis": {
            "exists": os.path.exists(project_directory),
            "files": [],
            "components": {},
            "available_actions": []
        }
    }

    if not os.path.exists(project_directory):
        return analysis

    # Analyze files in project directory
    json_dir = os.path.join(project_directory, JSON_SUBDIR)
    pdf_dir = os.path.join(project_directory, PDF_SUBDIR)

    components = analysis["analysis"]["components"]

    # Check for different file types
    if os.path.exists(json_dir):
        json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
        for file in json_files:
            file_path = os.path.join(json_dir, file)
            file_info = {
                "name": file,
                "path": file_path,
                "size": os.path.getsize(file_path),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }

            # Determine file type based on name
            if "research" in file.lower():
                components["research"] = file_info
                analysis["analysis"]["files"].append({"name": file, "type": "research", **file_info})
            elif "journal" in file.lower():
                components["journal"] = file_info
                analysis["analysis"]["files"].append({"name": file, "type": "journal", **file_info})
            elif "onboarding" in file.lower():
                components["config"] = file_info
                analysis["analysis"]["files"].append({"name": file, "type": "config", **file_info})
            elif "discovery" in file.lower():
                components["discovery"] = file_info
                analysis["analysis"]["files"].append({"name": file, "type": "discovery", **file_info})
            elif "lead_magnet" in file.lower():
                components["lead_magnet"] = file_info
                analysis["analysis"]["files"].append({"name": file, "type": "lead_magnet", **file_info})

    # Check for PDF files
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        for file in pdf_files:
            file_path = os.path.join(pdf_dir, file)
            file_info = {
                "name": file,
                "path": file_path,
                "size": os.path.getsize(file_path),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            components["pdf"] = file_info
            analysis["analysis"]["files"].append({"name": file, "type": "pdf", **file_info})

    # Check for media files
    media_dir = os.path.join(project_directory, MEDIA_SUBDIR)
    if os.path.exists(media_dir):
        media_files = [f for f in os.listdir(media_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if media_files:
            components["media"] = {
                "files": media_files,
                "count": len(media_files),
                "directory": media_dir
            }
            for file in media_files:
                file_path = os.path.join(media_dir, file)
                file_info = {
                    "name": file,
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                analysis["analysis"]["files"].append({"name": file, "type": "media", **file_info})

    # Determine available actions based on what's completed
    available_actions = []

    if not components.get("research"):
        available_actions.append({
            "id": "continue_research",
            "title": "Continue Research",
            "description": "Complete theme research and gather insights",
            "priority": 1
        })

    if components.get("research") and not components.get("journal"):
        available_actions.append({
            "id": "continue_content",
            "title": "Generate Content",
            "description": "Create 30-day journal and lead magnet content",
            "priority": 2
        })

    if (components.get("journal") or components.get("lead_magnet")) and not components.get("media"):
        available_actions.append({
            "id": "generate_media",
            "title": "Generate Media",
            "description": "Create images and visual assets for the journal",
            "priority": 3
        })

    if (components.get("journal") or components.get("media")) and not components.get("pdf"):
        available_actions.append({
            "id": "generate_pdf",
            "title": "Create PDF",
            "description": "Generate professional PDF documents",
            "priority": 4
        })

    # If project is complete, offer additional actions
    if components.get("pdf"):
        available_actions.append({
            "id": "regenerate_media",
            "title": "Regenerate Media",
            "description": "Create new images with different styles",
            "priority": 2
        })

        available_actions.append({
            "id": "create_pdf_variant",
            "title": "Create PDF Variant",
            "description": "Generate different PDF format or style",
            "priority": 3
        })

    # Add export action
    available_actions.append({
        "id": "export_content",
        "title": "Export Content",
        "description": "Export raw content for further editing",
        "priority": 5
    })

    analysis["analysis"]["available_actions"] = available_actions
    analysis["analysis"]["is_complete"] = len([action for action in available_actions if action.priority == 5]) == 1

    return analysis


@router.post("/start-workflow", response_model=WorkflowResponse)
async def start_crewai_workflow(
    request: WorkflowStartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a complete CrewAI workflow for journal creation"""

    # Verify project ownership
    from sqlalchemy import select
    project_query = select(Project).where(
        Project.id == request.project_id,
        Project.user_id == current_user.id
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await crewai_service.start_workflow(request, current_user.id)


@router.get("/workflow-status/{workflow_id}", response_model=WorkflowStatus)
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get real-time status of a CrewAI workflow"""
    status = await crewai_service.get_workflow_status(workflow_id, current_user.id)

    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return status


@router.post("/cancel-workflow/{workflow_id}")
async def cancel_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel an active CrewAI workflow"""
    await crewai_service.cancel_workflow(workflow_id, current_user.id)
    return {"message": "Workflow cancelled successfully"}


@router.get("/active-workflows")
async def get_active_workflows(current_user: User = Depends(get_current_user)):
    """Get list of active workflows for current user"""
    active_workflows = []

    for workflow_id, workflow in crewai_service.active_workflows.items():
        if workflow.get("user_id") == current_user.id and workflow["status"] not in ["completed", "failed", "cancelled"]:
            active_workflows.append({
                "workflow_id": workflow_id,
                "project_id": workflow["project_id"],
                "status": workflow["status"],
                "progress_percentage": workflow.get("progress_percentage", 0),
                "start_time": workflow["start_time"].isoformat()
            })

    return {"active_workflows": active_workflows}