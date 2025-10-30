"""
Journal Entry API Routes
Combines AI Crew generation with user customization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user, get_db
from app.services.journal_service import JournalService
from app.services.ai_crew_service import AICrewService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/journals", tags=["Journal Management"])

# Pydantic models
class JournalEntryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    ai_generated_content: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None
    is_private: bool = True

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None
    is_private: Optional[bool] = None
    is_favorite: Optional[bool] = None

class JournalEntryResponse(BaseModel):
    id: int
    title: str
    content: str
    ai_generated_content: Optional[str] = None
    word_count: int
    mood: Optional[str] = None
    tags: Optional[List[str]] = None
    is_private: bool
    is_favorite: bool
    cover_image: Optional[str] = None
    created_at: str
    updated_at: str
    last_accessed: Optional[str] = None

class AIGenerationRequest(BaseModel):
    theme: str = Field(..., description="Theme for AI generation")
    title_style: str = Field(..., description="Style for title")
    author_style: str = Field(..., description="Writing style for content")
    research_depth: str = Field("basic", description="Research depth level")
    custom_prompt: Optional[str] = None

class JournalEntryListResponse(BaseModel):
    entries: List[JournalEntryResponse]
    pagination: Dict[str, Any]

@router.post("/ai-generate", response_model=Dict[str, Any], status_code=201)
async def generate_journal_with_ai(
    request: AIGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate journal content using AI Crew"""
    try:
        ai_crew_service = AICrewService()
        journal_service = JournalService(db)

        # Step 1: Generate content with AI Crew
        generation_result = await ai_crew_service.generate_journal_content(
            user_id=current_user["id"],
            theme=request.theme,
            title_style=request.title_style,
            author_style=request.author_style,
            research_depth=request.research_depth,
            custom_prompt=request.custom_prompt
        )

        # Step 2: Create journal entry with AI content
        journal_entry = await journal_service.create_journal_entry(
            user_id=current_user["id"],
            title=generation_result["title"],
            content=generation_result["content"],
            ai_generated_content=generation_result["raw_ai_content"],
            ai_theme=request.theme,
            ai_generation_date=generation_result["generated_at"],
            generation_prompt=generation_result.get("prompt", ""),
            mood=generation_result.get("mood"),
            tags=generation_result.get("tags", []),
            cover_image=generation_result.get("cover_image"),
            attached_images=generation_result.get("images", [])
        )

        return {
            "message": "AI-generated journal created successfully",
            "entry": journal_entry,
            "ai_metadata": {
                "theme": request.theme,
                "generation_time": generation_result.get("generation_time", 0),
                "agents_used": generation_result.get("agents_used", []),
                "word_count": generation_result.get("word_count", 0)
            }
        }

    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="AI generation failed"
        )

@router.post("/", response_model=JournalEntryResponse, status_code=201)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new journal entry"""
    try:
        journal_service = JournalService(db)
        result = await journal_service.create_journal_entry(
            user_id=current_user["id"],
            title=entry_data.title,
            content=entry_data.content,
            ai_generated_content=entry_data.ai_generated_content,
            mood=entry_data.mood,
            tags=entry_data.tags,
            is_private=entry_data.is_private
        )
        return result

    except Exception as e:
        logger.error(f"Failed to create journal entry: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create journal entry"
        )

@router.get("/", response_model=JournalEntryListResponse)
async def get_journal_entries(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    search: Optional[str] = Query(None),
    mood_filter: Optional[str] = Query(None),
    tag_filter: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """Get user's journal entries with filtering"""
    try:
        journal_service = JournalService(db)
        result = await journal_service.get_user_entries(
            user_id=current_user["id"],
            skip=skip,
            limit=limit,
            search=search,
            mood_filter=mood_filter,
            tag_filter=tag_filter,
            date_from=date_from,
            date_to=date_to
        )
        return result

    except Exception as e:
        logger.error(f"Failed to get journal entries: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve journal entries"
        )

@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific journal entry"""
    try:
        journal_service = JournalService(db)
        result = await journal_service.get_journal_entry(
            entry_id=entry_id,
            user_id=current_user["id"]
        )

        # Update last accessed time
        await journal_service.update_last_accessed(entry_id, current_user["id"])

        return result

    except Exception as e:
        logger.error(f"Failed to get journal entry {entry_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve journal entry"
        )

@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: int,
    entry_data: JournalEntryUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update journal entry"""
    try:
        journal_service = JournalService(db)
        result = await journal_service.update_journal_entry(
            entry_id=entry_id,
            user_id=current_user["id"],
            title=entry_data.title,
            content=entry_data.content,
            mood=entry_data.mood,
            tags=entry_data.tags,
            is_private=entry_data.is_private,
            is_favorite=entry_data.is_favorite,
            is_customized=True  # Mark as user-customized
        )
        return result

    except Exception as e:
        logger.error(f"Failed to update journal entry {entry_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update journal entry"
        )

@router.delete("/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete journal entry"""
    try:
        journal_service = JournalService(db)
        await journal_service.delete_journal_entry(
            entry_id=entry_id,
            user_id=current_user["id"]
        )

    except Exception as e:
        logger.error(f"Failed to delete journal entry {entry_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete journal entry"
        )

@router.post("/{entry_id}/images", response_model=Dict[str, Any])
async def upload_journal_image(
    entry_id: int,
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload image for journal entry"""
    try:
        journal_service = JournalService(db)

        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Only image files are allowed"
            )

        result = await journal_service.upload_entry_image(
            entry_id=entry_id,
            user_id=current_user["id"],
            file=file,
            is_ai_generated=False
        )

        return {
            "message": "Image uploaded successfully",
            "image": result
        }

    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload image"
        )

@router.get("/ai-themes", response_model=Dict[str, Any])
async def get_ai_generation_themes(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get available AI generation themes"""
    try:
        ai_crew_service = AICrewService()
        themes = await ai_crew_service.get_available_themes()

        return {
            "themes": themes,
            "usage_stats": await ai_crew_service.get_user_theme_usage(current_user["id"])
        }

    except Exception as e:
        logger.error(f"Failed to get AI themes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve AI themes"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_journal_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get journal statistics for dashboard"""
    try:
        journal_service = JournalService(db)
        result = await journal_service.get_journal_statistics(current_user["id"])
        return result

    except Exception as e:
        logger.error(f"Failed to get journal statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve journal statistics"
        )

@router.post("/export-to-project", response_model=Dict[str, Any])
async def export_journal_to_project(
    entry_id: int,
    project_data: dict,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export journal entry to project format"""
    try:
        journal_service = JournalService(db)
        result = await journal_service.export_to_project(
            entry_id=entry_id,
            user_id=current_user["id"],
            project_data=project_data
        )

        return {
            "message": "Journal entry exported to project successfully",
            "project": result
        }

    except Exception as e:
        logger.error(f"Failed to export journal to project: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to export journal to project"
        )

@router.get("/search", response_model=JournalEntryListResponse)
async def search_journal_entries(
    q: str = Query(..., min_length=2),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50)
):
    """Search journal entries"""
    try:
        journal_service = JournalService(db)
        result = await journal_service.search_entries(
            user_id=current_user["id"],
            query=q,
            skip=skip,
            limit=limit
        )
        return result

    except Exception as e:
        logger.error(f"Failed to search journal entries: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to search journal entries"
        )