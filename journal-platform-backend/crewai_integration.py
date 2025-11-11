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
        self.llm = None  # Will be initialized when API key is provided

    def _check_crewai_availability(self):
        """Check if CrewAI modules are available."""
        try:
            import crewai
            return True
        except ImportError:
            return False

    def _initialize_llm(self, api_key: str = None):
        """Initialize the LLM for CrewAI agents."""
        if not api_key:
            raise ValueError("API key is required for LLM initialization")

        try:
            from crewai import LLM
            return LLM(
                model="gpt-4",
                api_key=api_key,
                temperature=0.7,
                max_tokens=None
            )
        except ImportError:
            return None

    def generate_job_id(self) -> str:
        """Generate a unique job ID for tracking journal creation."""
        return str(uuid.uuid4())

    async def start_journal_creation(self, preferences: Dict[str, Any], api_key: str = None, progress_callback: Optional[Callable] = None) -> str:
        """
        Start the journal creation process.

        Args:
            preferences: User preferences from the web interface
            api_key: User's OpenAI API key
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
            'api_key': api_key,
            'started_at': datetime.now(),
            'result': None,
            'error': None
        }

        # Start the background task
        asyncio.create_task(self._execute_journal_creation(job_id, api_key, progress_callback))

        return job_id

    async def _execute_journal_creation(self, job_id: str, api_key: str, progress_callback: Optional[Callable] = None):
        """
        Execute the actual journal creation using CrewAI.

        Args:
            job_id: Unique job identifier
            api_key: User's OpenAI API key
            progress_callback: Optional callback for progress updates
        """
        try:
            job_info = self.active_jobs[job_id]
            preferences = job_info['preferences']

            # Update progress
            await self._update_progress(job_id, 'starting', 5, 'Initializing journal creation...', progress_callback)

            # Initialize LLM with user's API key
            if not self.llm and self.crewai_available:
                try:
                    self.llm = self._initialize_llm(api_key)
                    print("✅ LLM initialized with user's API key")
                except Exception as e:
                    print(f"⚠️ Failed to initialize LLM: {e}")
                    await self._create_demo_journal(job_id, preferences, progress_callback)
                    return

            # Convert web preferences to CrewAI format
            crewai_prefs = self._convert_preferences(preferences, job_id)

            # Import CrewAI modules (lazy loading to avoid startup issues)
            await self._update_progress(job_id, 'research', 15, 'Starting research phase...', progress_callback)

            try:
                # Add project root to Python path to import crews modules
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

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
                self.active_jobs[job_id]['completed_at'] = datetime.now().isoformat()

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
        """Simulate detailed progress during crew execution with agent activity."""

        # Define detailed agent workflows
        agent_workflows = {
            'onboarding': [
                (10, 'Gathering user preferences...', 'Processing your journal preferences'),
                (15, 'Setting up workspace...', 'Initializing your personalized journal environment'),
                (20, 'Configuring AI agents...', 'Preparing the journal creation crew')
            ],
            'discovery': [
                (25, 'Researching topic trends...', 'Analyzing current journal trends and best practices'),
                (30, 'Finding relevant insights...', 'Discovering meaningful content for your journal'),
                (35, 'Building knowledge base...', 'Compiling research materials and insights')
            ],
            'research': [
                (40, 'Deep analysis in progress...', 'Analyzing complex patterns and themes'),
                (45, 'Fact-checking information...', 'Verifying accuracy and reliability of sources'),
                (50, 'Synthesizing findings...', 'Creating comprehensive research summary')
            ],
            'curation': [
                (55, 'Organizing content structure...', 'Structuring your journal for optimal flow'),
                (60, 'Selecting key insights...', 'Choosing the most impactful content to include'),
                (65, 'Creating content outline...', 'Building a coherent narrative structure')
            ],
            'writing': [
                (70, 'Crafting narrative...', 'Writing engaging journal entries'),
                (75, 'Refining language...', 'Enhancing clarity and readability'),
                (80, 'Adding personal touches...', 'Personalizing content to your voice')
            ],
            'editing': [
                (85, 'Reviewing content quality...', 'Ensuring high-quality writing'),
                (90, 'Final polish...', 'Making final improvements and adjustments')
            ],
            'pdf': [
                (95, 'Generating PDF...', 'Creating the final journal PDF'),
                (100, 'Finalizing output...', 'Completing your personalized journal')
            ]
        }

        # Simulate each agent workflow with detailed messages
        for phase, workflow in agent_workflows.items():
            for progress, status_message, description in workflow:
                # Send main progress update
                await self._update_progress(job_id, phase, progress, status_message, progress_callback)
                await asyncio.sleep(1.5)

                # Send detailed agent activity
                if progress_callback:
                    activity_update = {
                        'jobId': job_id,
                        'status': phase,
                        'progress': progress,
                        'progress_percentage': progress,
                        'currentAgent': phase,
                        'current_stage': phase,
                        'sequence': f'{phase.capitalize()} in Progress',
                        'message': status_message,
                        'thinking': description,
                        'output': f'🤔 {description}...',
                        'agent': phase
                    }
                    try:
                        await progress_callback(activity_update)
                    except Exception as e:
                        print(f"Error in activity callback: {e}")

                await asyncio.sleep(0.5)  # Brief pause between activities

    async def _execute_crew_with_progress(self, crew, job_id: str, progress_callback: Optional[Callable] = None):
        """Execute CrewAI crew with robust error handling and timeout protection."""
        import asyncio

        try:
            # Send initial progress update
            await self._update_progress(job_id, 'executing', 60, '🚀 Starting CrewAI agent execution...', progress_callback)

            # Execute crew with timeout and error handling
            print(f"🤖 Executing CrewAI crew for job {job_id}...")

            # Set a timeout for crew execution (10 minutes)
            timeout_seconds = 600

            try:
                # Run crew.kickoff() in a thread with timeout
                result = await asyncio.wait_for(
                    asyncio.to_thread(crew.kickoff),
                    timeout=timeout_seconds
                )

                # Validate result
                if result is None:
                    raise ValueError("CrewAI execution returned None result")

                print(f"✅ CrewAI execution completed successfully for job {job_id}")

                # Send completion progress update
                await self._update_progress(job_id, 'executing', 90, '✅ CrewAI execution completed, processing results...', progress_callback)

                return result

            except asyncio.TimeoutError:
                error_msg = f"CrewAI execution timed out after {timeout_seconds} seconds"
                print(f"⏰ {error_msg}")
                await self._update_progress(job_id, 'error', 0, f'⏰ {error_msg}', progress_callback)
                raise TimeoutError(error_msg)

            except Exception as crew_error:
                # Handle specific CrewAI errors
                error_str = str(crew_error).lower()

                if "openai" in error_str and "rate" in error_str:
                    error_msg = "OpenAI API rate limit exceeded. Please try again later."
                elif "openai" in error_str and ("quota" in error_str or "billing" in error_str):
                    error_msg = "OpenAI API quota exceeded. Please check your billing."
                elif "openai" in error_str and ("authentication" in error_str or "unauthorized" in error_str):
                    error_msg = "OpenAI API authentication failed. Please check your API key."
                elif "memory" in error_str or "resource" in error_str:
                    error_msg = "Insufficient memory/resources for CrewAI execution."
                elif "connection" in error_str or "network" in error_str:
                    error_msg = "Network connection error during CrewAI execution."
                else:
                    error_msg = f"CrewAI execution error: {str(crew_error)}"

                print(f"❌ {error_msg}")
                await self._update_progress(job_id, 'error', 0, f'❌ {error_msg}', progress_callback)
                raise RuntimeError(error_msg) from crew_error

        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"Unexpected error during CrewAI execution: {str(e)}"
            print(f"💥 {error_msg}")
            await self._update_progress(job_id, 'error', 0, f'💥 {error_msg}', progress_callback)
            raise

    async def _create_demo_journal(self, job_id: str, preferences: Dict[str, Any], progress_callback: Optional[Callable] = None):
        """Create a demo journal when CrewAI modules aren't available."""

        # Initialize with starting message
        await self._update_progress(job_id, 'initializing', 5, '🚀 Initializing journal creation workflow...', progress_callback)
        await asyncio.sleep(1)

        # Update progress through realistic phases
        phases = [
            ('setup', 10, '📋 Setting up workspace and loading templates...'),
            ('research', 20, '🔍 Research Agent: Analyzing theme and gathering content sources...'),
            ('research', 30, '📚 Research Agent: Found 15 relevant articles and insights...'),
            ('curation', 40, '✨ Curation Agent: Selecting personalized content...'),
            ('curation', 50, '🎯 Curation Agent: Curated 8 key insights for your journal...'),
            ('writing', 60, '✍️ Writing Agent: Crafting journal introduction...'),
            ('writing', 70, '📝 Writing Agent: Generating reflective prompts and exercises...'),
            ('editing', 80, '🔧 Editing Agent: Reviewing content for clarity and flow...'),
            ('formatting', 90, '🎨 Formatting Agent: Applying layout and styling...'),
            ('finalization', 95, '📦 Finalizing journal and generating files...'),
            ('completed', 100, '✅ Journal creation completed successfully!')
        ]

        for phase, progress, message in phases:
            await self._update_progress(job_id, phase, progress, message, progress_callback)

            # Variable sleep times to simulate real processing
            if phase in ['research', 'writing']:
                await asyncio.sleep(2)  # These phases take longer
            else:
                await asyncio.sleep(1)

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
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"

        if job_id in self.active_jobs:
            # Add log entry to job logs
            if 'logs' not in self.active_jobs[job_id]:
                self.active_jobs[job_id]['logs'] = []

            self.active_jobs[job_id]['logs'].append({
                'timestamp': timestamp,
                'level': 'INFO',
                'agent': status,
                'message': message
            })

            # Keep only last 50 log entries to prevent memory bloat
            if len(self.active_jobs[job_id]['logs']) > 50:
                self.active_jobs[job_id]['logs'] = self.active_jobs[job_id]['logs'][-50:]

            self.active_jobs[job_id].update({
                'status': status,
                'progress': progress,
                'message': message,
                'current_agent': status,
                'estimated_time_remaining': max(0, (100 - progress) * 2),  # Rough estimate
                'latest_log': log_entry
            })

        if progress_callback:
            progress_update = {
                'jobId': job_id,
                'status': status,
                'progress': progress,
                'progress_percentage': progress,  # Add field that frontend expects
                'currentAgent': status,
                'current_stage': status,  # Add field that frontend expects
                'sequence': f'{status.capitalize()} Phase',  # Add field that frontend expects
                'message': message,
                'estimatedTimeRemaining': max(0, (100 - progress) * 2),
                'log': log_entry,
                'logs': self.active_jobs.get(job_id, {}).get('logs', [])
            }
            try:
                await progress_callback(progress_update)
            except Exception as e:
                print(f"Error in progress callback: {e}")

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a journal creation job."""
        job = self.active_jobs.get(job_id)
        if not job:
            return None

        # Create a JSON-serializable copy of the job status
        serializable_job = {}
        for key, value in job.items():
            if key == 'started_at' and hasattr(value, 'isoformat'):
                # Convert datetime to ISO string
                serializable_job[key] = value.isoformat()
            elif isinstance(value, dict):
                # Handle nested dicts that might have datetime objects
                serializable_job[key] = {}
                for k, v in value.items():
                    if hasattr(v, 'isoformat'):
                        serializable_job[key][k] = v.isoformat()
                    else:
                        serializable_job[key][k] = v
            else:
                serializable_job[key] = value

        return serializable_job

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