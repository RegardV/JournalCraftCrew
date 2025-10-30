"""
Export API Routes for PDF, EPUB, and KDP integration
Phase 3.4: Export Service Implementation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user, get_db
from app.services.export_service import ExportService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exports", tags=["Export Service"])

# Pydantic models for request/response
class ExportJobCreate(BaseModel):
    project_id: int = Field(..., description="Project ID to export")
    export_format: str = Field(..., description="Export format: pdf, epub, kdp")
    export_options: Optional[Dict[str, Any]] = Field(None, description="Export format options")
    kdp_metadata: Optional[Dict[str, Any]] = Field(None, description="KDP publishing metadata")

class ExportJobResponse(BaseModel):
    id: int
    project_id: int
    export_format: str
    status: str
    progress: int
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    export_options: Optional[Dict[str, Any]] = None
    kdp_metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None

class ExportJobListResponse(BaseModel):
    export_jobs: List[ExportJobResponse]
    pagination: Dict[str, Any]

class KDPMetadata(BaseModel):
    title: str = Field(..., description="Book title for KDP")
    subtitle: Optional[str] = Field(None, description="Book subtitle")
    author: str = Field(..., description="Author name")
    publisher: Optional[str] = Field(None, description="Publisher name")
    isbn: Optional[str] = Field(None, description="ISBN number")
    description: str = Field(..., description="Book description")
    keywords: List[str] = Field(default_factory=list, description="Keywords for search")
    language: str = Field("en-US", description="Language code")
    categories: List[str] = Field(default_factory=list, description="KDP categories")
    trim_size: str = Field("6x9", description="Book trim size")
    page_color: str = Field("white", description="Page color")
    generate_cover: bool = Field(False, description="Auto-generate cover")
    cover_text: Optional[str] = Field(None, description="Cover text")

class ExportOptions(BaseModel):
    pdf_options: Optional[Dict[str, Any]] = Field(None, description="PDF export options")
    epub_options: Optional[Dict[str, Any]] = Field(None, description="EPUB export options")
    include_toc: bool = Field(True, description="Include table of contents")
    include_page_numbers: bool = Field(True, description="Include page numbers")
    font_size: int = Field(12, description="Base font size")
    margin_size: str = Field("standard", description="Margin size: narrow, standard, wide")

@router.post("/jobs", response_model=Dict[str, Any], status_code=201)
async def create_export_job(
    export_data: ExportJobCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new export job"""
    try:
        export_service = ExportService(db)
        result = await export_service.create_export_job(
            user_id=current_user["id"],
            project_id=export_data.project_id,
            export_format=export_data.export_format,
            export_options=export_data.export_options,
            kdp_metadata=export_data.kdp_metadata
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to create export job: {e}")
        raise HTTPException(
            status_code=500,
            detail="Export job creation failed due to internal error"
        )

@router.get("/jobs", response_model=ExportJobListResponse)
async def get_export_jobs(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    project_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None)
):
    """Get user's export jobs with filtering and pagination"""
    try:
        export_service = ExportService(db)
        result = await export_service.get_export_jobs(
            user_id=current_user["id"],
            project_id=project_id,
            status_filter=status_filter,
            skip=skip,
            limit=limit
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get export jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve export jobs"
        )

@router.get("/jobs/{export_job_id}", response_model=Dict[str, Any])
async def get_export_job(
    export_job_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific export job by ID"""
    try:
        export_service = ExportService(db)
        result = await export_service.get_export_job(
            export_job_id=export_job_id,
            user_id=current_user["id"]
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get export job {export_job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve export job"
        )

@router.put("/jobs/{export_job_id}/cancel", response_model=Dict[str, Any])
async def cancel_export_job(
    export_job_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an export job"""
    try:
        export_service = ExportService(db)
        result = await export_service.cancel_export_job(
            export_job_id=export_job_id,
            user_id=current_user["id"]
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to cancel export job {export_job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel export job"
        )

@router.get("/formats", response_model=Dict[str, Any])
async def get_supported_formats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get supported export formats and their options"""
    try:
        return {
            "supported_formats": {
                "pdf": {
                    "name": "PDF",
                    "description": "Portable Document Format for printing and sharing",
                    "options": {
                        "page_size": ["A4", "A5", "Letter", "Legal"],
                        "orientation": ["portrait", "landscape"],
                        "margin_size": ["narrow", "standard", "wide"],
                        "font_family": ["serif", "sans-serif", "monospace"],
                        "font_size": {"min": 8, "max": 24, "default": 12},
                        "include_page_numbers": {"type": "boolean", "default": True},
                        "include_toc": {"type": "boolean", "default": True},
                        "cover_image": {"type": "file", "optional": True}
                    },
                    "file_extensions": [".pdf"],
                    "estimated_time": "2-5 minutes"
                },
                "epub": {
                    "name": "EPUB",
                    "description": "Electronic publication format for e-readers",
                    "options": {
                        "font_size": {"min": 10, "max": 24, "default": 14},
                        "font_family": ["serif", "sans-serif"],
                        "line_height": {"min": 1.2, "max": 2.0, "default": 1.6},
                        "include_toc": {"type": "boolean", "default": True},
                        "cover_image": {"type": "file", "optional": True}
                    },
                    "file_extensions": [".epub"],
                    "estimated_time": "1-3 minutes"
                },
                "kdp": {
                    "name": "Kindle Direct Publishing",
                    "description": "Amazon KDP-ready format for print and digital publishing",
                    "options": {
                        "trim_size": ["6x9", "5.5x8.5", "8.5x11", "4.25x7"],
                        "page_color": ["white", "cream"],
                        "interior_type": ["black_and_white", "color"],
                        "paper_type": ["standard", "premium"],
                        "cover_finish": ["glossy", "matte"],
                        "generate_cover": {"type": "boolean", "default": False}
                    },
                    "file_extensions": [".pdf"],
                    "estimated_time": "5-10 minutes"
                }
            }
        }

    except Exception as e:
        logger.error(f"Failed to get supported formats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve supported formats"
        )

@router.post("/kdp/preview", response_model=Dict[str, Any])
async def preview_kdp_export(
    project_id: int,
    kdp_metadata: KDPMetadata,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Preview KDP export settings and metadata"""
    try:
        export_service = ExportService(db)

        # This would validate KDP metadata and provide preview
        # For now, return metadata validation result
        return {
            "message": "KDP metadata validated successfully",
            "metadata": {
                "title": kdp_metadata.title,
                "subtitle": kdp_metadata.subtitle,
                "author": kdp_metadata.author,
                "description": kdp_metadata.description,
                "trim_size": kdp_metadata.trim_size,
                "page_color": kdp_metadata.page_color,
                "categories": kdp_metadata.categories,
                "keywords": kdp_metadata.keywords
            },
            "preview_url": f"/exports/preview/kdp/{project_id}",
            "validation_status": "valid",
            "estimated_pages": "200-300",  # Would be calculated from project content
            "estimated_file_size": "5-15 MB"
        }

    except Exception as e:
        logger.error(f"Failed to preview KDP export: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to preview KDP export"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_export_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get export usage statistics for dashboard"""
    try:
        export_service = ExportService(db)
        result = await export_service.get_export_statistics(
            user_id=current_user["id"]
        )
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to get export statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve export statistics"
        )

@router.get("/templates", response_model=Dict[str, Any])
async def get_export_templates(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get export templates and presets"""
    try:
        return {
            "export_templates": {
                "pdf": {
                    "novel": {
                        "name": "Novel Template",
                        "description": "Standard novel format with chapters and pagination",
                        "options": {
                            "page_size": "A5",
                            "margin_size": "standard",
                            "font_family": "serif",
                            "font_size": 11,
                            "include_toc": True,
                            "include_page_numbers": True
                        }
                    },
                    "journal": {
                        "name": "Journal Template",
                        "description": "Personal journal format with dated entries",
                        "options": {
                            "page_size": "A4",
                            "margin_size": "wide",
                            "font_family": "sans-serif",
                            "font_size": 12,
                            "include_toc": False,
                            "include_page_numbers": True
                        }
                    },
                    "cookbook": {
                        "name": "Cookbook Template",
                        "description": "Recipe book format with ingredient lists and instructions",
                        "options": {
                            "page_size": "Letter",
                            "margin_size": "standard",
                            "font_family": "sans-serif",
                            "font_size": 10,
                            "include_toc": True,
                            "include_page_numbers": True
                        }
                    }
                },
                "epub": {
                    "fiction": {
                        "name": "Fiction E-book",
                        "description": "Optimized for fiction reading on e-readers",
                        "options": {
                            "font_size": 14,
                            "font_family": "serif",
                            "line_height": 1.6,
                            "include_toc": True
                        }
                    },
                    "nonfiction": {
                        "name": "Non-fiction E-book",
                        "description": "Professional format for non-fiction content",
                        "options": {
                            "font_size": 13,
                            "font_family": "sans-serif",
                            "line_height": 1.5,
                            "include_toc": True
                        }
                    }
                },
                "kdp": {
                    "standard_novel": {
                        "name": "Standard Novel",
                        "description": "Amazon standard novel format",
                        "options": {
                            "trim_size": "6x9",
                            "page_color": "cream",
                            "interior_type": "black_and_white",
                            "paper_type": "standard",
                            "cover_finish": "matte"
                        }
                    },
                    "childrens_book": {
                        "name": "Children's Book",
                        "description": "Picture book format with color interior",
                        "options": {
                            "trim_size": "8.5x11",
                            "page_color": "white",
                            "interior_type": "color",
                            "paper_type": "premium",
                            "cover_finish": "glossy"
                        }
                    }
                }
            }
        }

    except Exception as e:
        logger.error(f"Failed to get export templates: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve export templates"
        )

@router.delete("/jobs/{export_job_id}", status_code=204)
async def delete_export_job(
    export_job_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete export job and associated files"""
    try:
        export_service = ExportService(db)

        # This would delete the export job and associated files
        # For now, return not implemented
        raise HTTPException(
            status_code=501,
            detail="Export job deletion not implemented yet"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to delete export job {export_job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete export job"
        )