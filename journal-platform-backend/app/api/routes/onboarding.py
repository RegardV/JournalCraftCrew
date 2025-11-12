"""
Onboarding Agent API Routes
Integrates the CLI onboarding agent with web interface
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import os
import sys
import json
from pathlib import Path

# Add agents directory to path for CrewAI integration
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))
try:
    from agents.onboarding_agent import create_onboarding_agent
    from agents.discovery_agent import discover_idea
    from config.settings import TITLE_STYLES, VALID_RESEARCH_DEPTHS, OUTPUT_DIR, JSON_SUBDIR, DATE_FORMAT
    from utils import parse_llm_json, save_json, log_debug
except ImportError as e:
    print(f"Import error in onboarding: {e}")
    # Fallback configurations
    TITLE_STYLES = [
        "motivational", "actionable", "insightful", "inspirational", "practical",
        "thought-provoking", "encouraging", "implementable", "illuminating", "empowering"
    ]
    VALID_RESEARCH_DEPTHS = {
        "light": 5,
        "medium": 15,
        "deep": 25
    }
    OUTPUT_DIR = "../LLM_output"
    JSON_SUBDIR = "Json_output"
    DATE_FORMAT = "%Y-%m-%d"

from ...core.deps import get_db, get_current_user
from ...models.user import User
from ...models.project import Project
from crewai import LLM

router = APIRouter()


# Pydantic models for onboarding requests
class ThemeValidationRequest(BaseModel):
    theme: str = Field(..., description="User-provided journal theme")


class ThemeValidationResponse(BaseModel):
    original_theme: str
    formatted_theme: str
    is_valid: bool
    message: Optional[str] = None


class AuthorStyleRequest(BaseModel):
    theme: str = Field(..., description="Journal theme for author suggestions")


class AuthorStyleResponse(BaseModel):
    authors: List[Dict[str, str]]
    theme: str
    fallback_used: bool = False


class OnboardingPreferencesRequest(BaseModel):
    theme: str = Field(..., description="Journal theme")
    title: str = Field(..., description="User's preferred journal title")
    title_style: str = Field(..., description="Selected title style")
    author_style: str = Field(..., description="Selected author style")
    research_depth: str = Field(..., description="Research depth")


class OnboardingPreferencesResponse(BaseModel):
    preferences: Dict[str, Any]
    run_directory: str
    preferences_file: str
    is_valid: bool


class TitleGenerationRequest(BaseModel):
    theme: str = Field(..., description="Journal theme")
    title_style: str = Field(..., description="Selected title style")


class TitleGenerationResponse(BaseModel):
    titles: List[str]
    styled_titles: List[str]
    theme: str
    title_style: str


# Onboarding Service
class OnboardingService:
    def __init__(self):
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize LLM for onboarding agent"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            return LLM(
                model="gpt-4",
                api_key=api_key,
                temperature=0.7,
                max_tokens=1000
            )
        except Exception as e:
            log_debug(f"Failed to initialize LLM: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize AI services")

    async def validate_theme(self, theme: str) -> ThemeValidationResponse:
        """Validate and format journal theme"""
        if not theme or not theme.strip():
            return ThemeValidationResponse(
                original_theme=theme,
                formatted_theme="",
                is_valid=False,
                message="Theme cannot be empty"
            )

        original_theme = theme.strip()
        formatted_theme = original_theme

        # Auto-format theme with "Journaling for" prefix if needed
        if 'for' not in original_theme.lower():
            formatted_theme = f"Journaling for {original_theme}"

        return ThemeValidationResponse(
            original_theme=original_theme,
            formatted_theme=formatted_theme,
            is_valid=True,
            message=f"Theme formatted as: {formatted_theme}" if original_theme != formatted_theme else None
        )

    async def get_author_styles(self, theme: str) -> AuthorStyleResponse:
        """Get dynamic author styles based on theme"""
        fallback_used = False

        try:
            # Create temporary directory for LLM output
            temp_dir = os.path.join(OUTPUT_DIR, "temp_web_onboarding")
            os.makedirs(temp_dir, exist_ok=True)

            # Generate author style prompt
            author_prompt = (
                f"List 5 bestselling authors in the '{theme}' niche or related personal development themes for 2025, "
                "each with a short style description (e.g., 'direct actionable'). "
                "Return a JSON list of dictionaries with 'name' and 'style' keys, "
                "e.g., [{\"name\": \"James Clear\", \"style\": \"direct actionable\"}, ...]. "
                "Ensure valid JSON with no extra text outside the list."
            )

            # Call LLM for author suggestions
            authors = parse_llm_json(self.llm, author_prompt, temp_dir, "author_styles.txt",
                                   expected_keys=["name", "style"], flatten=False)

            if not authors or not isinstance(authors, list):
                raise ValueError("Invalid author list returned")

            log_debug(f"LLM returned {len(authors)} authors for theme '{theme}'")

        except Exception as e:
            log_debug(f"Failed to fetch dynamic authors for '{theme}': {e}. Using fallback.")
            fallback_used = True
            # Fallback author styles
            authors = [
                {"name": "James Clear", "style": "direct actionable"},
                {"name": "Mark Manson", "style": "blunt irreverent"},
                {"name": "Brené Brown", "style": "empathetic research-driven"},
                {"name": "Robin Sharma", "style": "inspirational narrative"},
                {"name": "Mel Robbins", "style": "direct motivational"}
            ]

        return AuthorStyleResponse(
            authors=authors,
            theme=theme,
            fallback_used=fallback_used
        )

    async def generate_titles(self, theme: str, title_style: str) -> TitleGenerationResponse:
        """Generate title ideas based on theme and title style"""
        try:
            # Create temporary directory for LLM output
            temp_dir = os.path.join(OUTPUT_DIR, "temp_web_onboarding")
            os.makedirs(temp_dir, exist_ok=True)

            # Use the discovery agent for title generation
            from agents.discovery_agent import create_discovery_agent

            discovery_agent = create_discovery_agent(self.llm)

            # Call discovery agent
            result = discover_idea(discovery_agent, theme=theme, title_style=title_style)

            if not isinstance(result, dict) or 'titles' not in result or 'styled_titles' not in result:
                raise ValueError("Invalid discovery agent response")

            log_debug(f"Generated {len(result['titles'])} + {len(result['styled_titles'])} title options")

            return TitleGenerationResponse(
                titles=result['titles'],
                styled_titles=result['styled_titles'],
                theme=theme,
                title_style=title_style
            )

        except Exception as e:
            log_debug(f"Failed to generate titles: {e}")
            # Fallback titles
            fallback_titles = [
                f"The {theme.title()} Journey",
                f"30 Days of {theme.title()}",
                f"{theme.title()} Mastery",
                f"Your {theme.title()} Guide",
                f"{theme.title()} Unleashed"
            ]

            fallback_styled = [
                f"Discover {theme.title()}: A Complete Journey",
                f"The Art of {theme.title()}: Daily Practices",
                f"{theme.title()} Path: Finding Your Way",
                f"Embrace {theme.title()}: A New Beginning",
                f"The {theme.title()} Way: Transformative Practices"
            ]

            return TitleGenerationResponse(
                titles=fallback_titles,
                styled_titles=fallback_styled,
                theme=theme,
                title_style=title_style
            )

    async def save_preferences(self, preferences: OnboardingPreferencesRequest, user_id: int) -> OnboardingPreferencesResponse:
        """Save onboarding preferences and create project directory"""
        try:
            today = datetime.now().strftime(DATE_FORMAT)

            # Create run directory
            run_dir = os.path.join(OUTPUT_DIR, f"{preferences.title.replace(' ', '_')}_{today}")
            os.makedirs(run_dir, exist_ok=True)

            # Create JSON directory
            json_dir = os.path.join(run_dir, JSON_SUBDIR)
            os.makedirs(json_dir, exist_ok=True)

            # Prepare preferences data
            prefs_data = {
                "theme": preferences.theme,
                "title": preferences.title,
                "title_style": preferences.title_style,
                "author_style": preferences.author_style,
                "research_depth": preferences.research_depth,
                "run_dir": run_dir,
                "date": today,
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }

            # Save preferences to JSON file
            prefs_file = os.path.join(json_dir, f"onboarding_prefs_{preferences.title}_{preferences.theme}.json")
            save_json(prefs_data, prefs_file)

            log_debug(f"Saved onboarding preferences to {prefs_file}")

            return OnboardingPreferencesResponse(
                preferences=prefs_data,
                run_directory=run_dir,
                preferences_file=prefs_file,
                is_valid=True
            )

        except Exception as e:
            log_debug(f"Failed to save preferences: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save preferences: {str(e)}")


# Initialize service
onboarding_service = OnboardingService()


@router.get("/title-styles")
async def get_title_styles():
    """Get available title styles"""
    return {
        "styles": [
            {"id": style, "name": style.replace("_", " ").title(), "description": f"{style.replace('_', ' ').title()} approach"}
            for style in TITLE_STYLES
        ]
    }


@router.get("/research-depths")
async def get_research_depths():
    """Get available research depth options"""
    return {
        "depths": [
            {"id": depth, "name": depth.title(), "insights": count}
            for depth, count in VALID_RESEARCH_DEPTHS.items()
        ]
    }


@router.post("/validate-theme", response_model=ThemeValidationResponse)
async def validate_theme(request: ThemeValidationRequest):
    """Validate and format journal theme"""
    return await onboarding_service.validate_theme(request.theme)


@router.post("/author-styles", response_model=AuthorStyleResponse)
async def get_author_styles(request: AuthorStyleRequest):
    """Get author style suggestions based on theme"""
    return await onboarding_service.get_author_styles(request.theme)


@router.post("/generate-titles", response_model=TitleGenerationResponse)
async def generate_titles(request: TitleGenerationRequest):
    """Generate title ideas based on theme and style"""
    return await onboarding_service.generate_titles(request.theme, request.title_style)


@router.post("/save-preferences", response_model=OnboardingPreferencesResponse)
async def save_preferences(
    request: OnboardingPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save onboarding preferences and create project directory"""

    # Validate preferences
    if request.title_style not in TITLE_STYLES:
        raise HTTPException(status_code=400, detail=f"Invalid title style. Must be one of: {TITLE_STYLES}")

    if request.research_depth not in VALID_RESEARCH_DEPTHS:
        raise HTTPException(status_code=400, detail=f"Invalid research depth. Must be one of: {list(VALID_RESEARCH_DEPTHS.keys())}")

    # Save preferences
    result = await onboarding_service.save_preferences(request, current_user.id)

    # Create project record in database
    try:
        project = Project(
            user_id=current_user.id,
            title=request.title,
            description=f"AI-generated {request.theme} journal with {request.author_style} style",
            theme=request.theme,
            status="onboarding_complete",
            onboarding_preferences=json.dumps(result.preferences),
            project_directory=result.run_directory
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

        # Add project ID to response
        result.preferences["project_id"] = project.id

    except Exception as e:
        log_debug(f"Failed to create project record: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project record")

    return result


@router.get("/existing-projects")
async def get_existing_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get existing projects for the current user"""
    try:
        # Query projects from database
        result = await db.execute(
            "SELECT id, title, description, theme, status, created_at, project_directory "
            "FROM projects "
            "WHERE user_id = :user_id "
            "ORDER BY created_at DESC",
            {"user_id": current_user.id}
        )
        projects = result.fetchall()

        return {
            "projects": [
                {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "theme": project.theme,
                    "status": project.status,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                    "project_directory": project.project_directory
                }
                for project in projects
            ]
        }

    except Exception as e:
        log_debug(f"Failed to fetch existing projects: {e}")
        # Fallback to directory-based project detection
        return await _get_projects_from_directory(current_user.id)


async def _get_projects_from_directory(user_id: int) -> Dict[str, Any]:
    """Fallback method to get projects from directory structure"""
    try:
        output_path = Path(OUTPUT_DIR)
        if not output_path.exists():
            return {"projects": []}

        projects = []
        for project_dir in output_path.iterdir():
            if project_dir.is_dir():
                # Try to read preferences file
                prefs_file = project_dir / JSON_SUBDIR / f"onboarding_prefs_{project_dir.name}.json"
                if prefs_file.exists():
                    try:
                        with open(prefs_file, 'r') as f:
                            prefs = json.load(f)
                            if prefs.get("user_id") == user_id:
                                projects.append({
                                    "title": prefs.get("title", project_dir.name),
                                    "theme": prefs.get("theme", "Unknown"),
                                    "status": "saved",
                                    "created_at": prefs.get("date"),
                                    "project_directory": str(project_dir)
                                })
                    except Exception:
                        continue

        return {"projects": projects}

    except Exception as e:
        log_debug(f"Failed to get projects from directory: {e}")
        return {"projects": []}