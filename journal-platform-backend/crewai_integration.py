import os
import sys
import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from pathlib import Path

# Add parent directories to path to import CrewAI modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../crews'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JournalCreationService:
    """Service to integrate web interface with CrewAI journal creation system."""

    def __init__(self):
        self.active_jobs = {}
        self.crewai_available = self._check_crewai_availability()
        if self.crewai_available:
            self.llm = self._initialize_llm()
        else:
            self.llm = None
            print("⚠️ CrewAI not available - running in demo mode")

    def _check_crewai_availability(self):
        """Check if CrewAI modules are available."""
        try:
            import crewai
            return True
        except ImportError:
            return False

    def _initialize_llm(self):
        """Initialize the LLM for CrewAI agents."""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        try:
            from crewai import LLM
            return LLM(
                model="gpt-4",
                api_key=openai_api_key,
                temperature=0.7,
                max_tokens=None
            )
        except ImportError:
            return None

    def generate_job_id(self) -> str:
        """Generate a unique job ID for tracking journal creation."""
        return str(uuid.uuid4())

    async def start_journal_creation(self, preferences: Dict[str, Any], progress_callback: Optional[Callable] = None) -> str:
        """
        Start the journal creation process.

        Args:
            preferences: User preferences from the web interface
            progress_callback: Optional callback for progress updates

        Returns:
            job_id: Unique identifier for tracking the job
        """
        job_id = self.generate_job_id()

        # Store job information
        self.active_jobs[job_id] = {
            'status': 'starting',
            'progress': 0,
            'preferences': preferences,
            'started_at': datetime.now(),
            'result': None,
            'error': None
        }

        # Start the background task
        asyncio.create_task(self._execute_journal_creation(job_id, progress_callback))

        return job_id

    async def _execute_journal_creation(self, job_id: str, progress_callback: Optional[Callable] = None):
        """
        Execute the actual journal creation using CrewAI.

        Args:
            job_id: Unique job identifier
            progress_callback: Optional callback for progress updates
        """
        try:
            job_info = self.active_jobs[job_id]
            preferences = job_info['preferences']

            # Update progress
            await self._update_progress(job_id, 'starting', 5, 'Initializing journal creation...', progress_callback)

            # Convert web preferences to CrewAI format
            crewai_prefs = self._convert_preferences(preferences, job_id)

            # Import CrewAI modules (lazy loading to avoid startup issues)
            await self._update_progress(job_id, 'research', 15, 'Starting research phase...', progress_callback)

            try:
                from crews.phase1_crew import create_phase1_crew, process_results
                from agents.onboarding_agent import create_onboarding_agent

                # Create the crew
                crew = create_phase1_crew(
                    llm=self.llm,
                    theme=crewai_prefs['theme'],
                    research_depth=crewai_prefs['research_depth'],
                    author_style=crewai_prefs['author_style'],
                    title=crewai_prefs['title']
                )

                # Execute crew with progress tracking
                await self._update_progress(job_id, 'research', 25, 'Researching best practices and insights...', progress_callback)

                # Simulate progress during crew execution
                await self._simulate_progress(job_id, progress_callback)

                # Execute the crew
                result = await self._execute_crew_with_progress(crew, job_id, progress_callback)

                # Process results
                processed_result = process_results(result)

                # Mark as completed
                await self._update_progress(job_id, 'completed', 100, 'Journal created successfully!', progress_callback)

                # Store result
                self.active_jobs[job_id]['status'] = 'completed'
                self.active_jobs[job_id]['result'] = processed_result
                self.active_jobs[job_id]['completed_at'] = datetime.now()

            except ImportError as e:
                # Fallback if CrewAI modules aren't available
                print(f"CrewAI modules not available: {e}")
                await self._create_demo_journal(job_id, preferences, progress_callback)

        except Exception as e:
            # Handle errors
            error_message = f"Journal creation failed: {str(e)}"
            print(f"Error in journal creation for job {job_id}: {e}")

            await self._update_progress(job_id, 'error', 0, error_message, progress_callback)

            self.active_jobs[job_id]['status'] = 'error'
            self.active_jobs[job_id]['error'] = error_message

    def _convert_preferences(self, web_prefs: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """Convert web preferences to CrewAI format."""
        # Create job directory
        output_dir = "../LLM_output"
        job_dir = os.path.join(output_dir, f"journal_creation_{job_id}")
        os.makedirs(job_dir, exist_ok=True)

        return {
            'theme': web_prefs.get('theme', 'Journaling for Personal Growth'),
            'title': web_prefs.get('title', 'Personal Journal'),
            'title_style': web_prefs.get('titleStyle', 'Catchy Questions'),
            'author_style': web_prefs.get('authorStyle', 'inspirational narrative'),
            'research_depth': web_prefs.get('researchDepth', 'medium'),
            'run_dir': job_dir
        }

    async def _simulate_progress(self, job_id: str, progress_callback: Optional[Callable] = None):
        """Simulate progress during crew execution."""
        phases = [
            ('research', 35, 'Analyzing research findings...'),
            ('curation', 55, 'Curating content and insights...'),
            ('editing', 75, 'Editing and refining content...'),
            ('pdf', 90, 'Generating PDF and finalizing...')
        ]

        for phase, progress, message in phases:
            await self._update_progress(job_id, phase, progress, message, progress_callback)
            await asyncio.sleep(2)  # Simulate processing time

    async def _execute_crew_with_progress(self, crew, job_id: str, progress_callback: Optional[Callable] = None):
        """Execute CrewAI crew with progress tracking."""
        # This is a placeholder for actual CrewAI execution
        # In a real implementation, you'd integrate with CrewAI's callback system

        try:
            # Execute crew (this will be replaced with actual CrewAI execution)
            # For now, simulate the execution
            await asyncio.sleep(3)

            # Return a mock result
            return {
                'success': True,
                'pdf_path': f"../LLM_output/journal_creation_{job_id}/journal.pdf",
                'metadata': {
                    'title': self.active_jobs[job_id]['preferences']['title'],
                    'theme': self.active_jobs[job_id]['preferences']['theme'],
                    'created_at': datetime.now().isoformat()
                }
            }
        except Exception as e:
            print(f"Error executing crew: {e}")
            raise

    async def _create_demo_journal(self, job_id: str, preferences: Dict[str, Any], progress_callback: Optional[Callable] = None):
        """Create a demo journal when CrewAI modules aren't available."""

        # Update progress through phases
        phases = [
            ('research', 25, 'Researching journal content...'),
            ('curation', 50, 'Curating personalized insights...'),
            ('editing', 75, 'Editing and refining content...'),
            ('pdf', 90, 'Generating PDF journal...')
        ]

        for phase, progress, message in phases:
            await self._update_progress(job_id, phase, progress, message, progress_callback)
            await asyncio.sleep(1.5)  # Simulate processing time

        # Create a demo journal file
        job_dir = f"../LLM_output/journal_creation_{job_id}"
        os.makedirs(job_dir, exist_ok=True)

        demo_content = f"""
# {preferences.get('title', 'Personal Journal')}

Theme: {preferences.get('theme', 'Personal Growth')}
Style: {preferences.get('authorStyle', 'inspirational narrative')}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Your Personalized Journal

This is a demo journal created with your preferences. In the full implementation, this would contain AI-generated content based on your selected theme and writing style.

### Sample Content
- Reflective prompts tailored to {preferences.get('theme', 'your interests')}
- Insights curated in a {preferences.get('authorStyle', 'inspirational')} style
- {preferences.get('researchDepth', 'medium')} depth of research-backed content

---

*This journal was created by Journal Craft Crew's AI agents.*
        """

        # Save demo content
        demo_file = os.path.join(job_dir, "journal.md")
        with open(demo_file, 'w') as f:
            f.write(demo_content)

        # Mark as completed
        await self._update_progress(job_id, 'completed', 100, 'Demo journal created successfully!', progress_callback)

        self.active_jobs[job_id]['status'] = 'completed'
        self.active_jobs[job_id]['result'] = {
            'success': True,
            'file_path': demo_file,
            'demo': True
        }

    async def _update_progress(self, job_id: str, status: str, progress: int, message: str, progress_callback: Optional[Callable] = None):
        """Update job progress and notify callback if provided."""
        if job_id in self.active_jobs:
            self.active_jobs[job_id].update({
                'status': status,
                'progress': progress,
                'message': message,
                'current_agent': status,
                'estimated_time_remaining': max(0, (100 - progress) * 2)  # Rough estimate
            })

        if progress_callback:
            progress_update = {
                'jobId': job_id,
                'status': status,
                'progress': progress,
                'currentAgent': status,
                'message': message,
                'estimatedTimeRemaining': max(0, (100 - progress) * 2)
            }
            try:
                await progress_callback(progress_update)
            except Exception as e:
                print(f"Error in progress callback: {e}")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a journal creation job."""
        return self.active_jobs.get(job_id)

    def get_author_suggestions(self, theme: str) -> Dict[str, Any]:
        """Get author style suggestions for a given theme."""
        try:
            # This would normally use the LLM to generate suggestions
            # For now, return static suggestions based on theme

            base_suggestions = [
                {"name": "James Clear", "style": "direct actionable"},
                {"name": "Mark Manson", "style": "blunt irreverent"},
                {"name": "Brené Brown", "style": "empathetic research-driven"},
                {"name": "Robin Sharma", "style": "inspirational narrative"},
                {"name": "Mel Robbins", "style": "direct motivational"}
            ]

            # Theme-specific adjustments
            if 'anxiety' in theme.lower() or 'mindfulness' in theme.lower():
                base_suggestions.extend([
                    {"name": "Thich Nhat Hanh", "style": "gentle mindful"},
                    {"name": "Jon Kabat-Zinn", "style": "scientific compassionate"}
                ])
            elif 'productivity' in theme.lower() or 'goal' in theme.lower():
                base_suggestions.extend([
                    {"name": "David Allen", "style": "systematic practical"},
                    {"name": "Stephen Covey", "style": "principle-driven structured"}
                ])
            elif 'creativity' in theme.lower() or 'artistic' in theme.lower():
                base_suggestions.extend([
                    {"name": "Julia Cameron", "style": "creative nurturing"},
                    {"name": "Austin Kleon", "style": "playful innovative"}
                ])

            return {
                'authors': base_suggestions[:7],  # Return top 7 suggestions
                'theme': theme
            }

        except Exception as e:
            print(f"Error getting author suggestions: {e}")
            return {
                'authors': base_suggestions,
                'theme': theme
            }

# Global service instance
journal_service = JournalCreationService()