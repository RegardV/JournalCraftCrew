"""
Export Service API Routes
Phase 3: Backend Development - Complete Implementation
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

from app.models import Project, User
from app.models.export import ExportJob, ExportFormat, ExportHistory, KDPSubmission
from app.api.dependencies import get_current_user, get_async_db
from app.services.export_service import ExportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["Export Service"])

class ExportRequest(BaseModel):
    export_format: str
    quality: Optional[int] = 90  # 1-100
    include_images: bool = True
    page_numbers: bool = True
    table_of_contents: bool = False
    custom_css: Optional[str] = None

class KDPRequest(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    generate_cover: bool = False
    royalty_rate: Optional[str] = "35.0"

class ExportSettings(BaseModel):
    quality: int = 90
    include_images: bool = True
    page_numbers: bool = True
    table_of_contents: bool = False
    custom_css: Optional[str] = None

@router.get("/jobs")
async def get_export_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 50,
    project_id: Optional[int] = None,
    status_filter: Optional[str] = None
):
    """Get export jobs history"""
    export_service = ExportService(db)
    return await export_service.get_export_jobs(
        user_id=current_user.id,
        project_id=project_id,
        status_filter=status_filter,
        skip=skip,
        limit=limit
    )

@router.get("/jobs/{job_id}")
async def get_export_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get specific export job details"""
    export_service = ExportService(db)
    return await export_service.get_export_job(
        export_job_id=job_id,
        user_id=current_user.id
    )

@router.post("/request/{project_id}")
async def request_export(
    project_id: int,
    export_request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Request export for project"""
    export_service = ExportService(db)

    # Build export options
    export_options = {
        "quality": export_request.quality,
        "include_images": export_request.include_images,
        "page_numbers": export_request.page_numbers,
        "table_of_contents": export_request.table_of_contents,
        "custom_css": export_request.custom_css
    }

    return await export_service.create_export_job(
        user_id=current_user.id,
        project_id=project_id,
        export_format=export_request.export_format,
        export_options=export_options
    )

@router.post("/cancel/{job_id}")
async def cancel_export_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Cancel export job"""
    export_service = ExportService(db)
    return await export_service.cancel_export_job(
        export_job_id=job_id,
        user_id=current_user.id
    )

@router.get("/statistics")
async def get_export_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get export usage statistics"""
    export_service = ExportService(db)
    return await export_service.get_export_statistics(user_id=current_user.id)

@router.post("/kdp/submit/{job_id}")
async def submit_to_kdp(
    job_id: int,
    kdp_data: KDPRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Submit completed export to Amazon KDP"""
    export_service = ExportService(db)

    # Build KDP metadata
    kdp_metadata = {
        "title": kdp_data.title,
        "author": kdp_data.author,
        "isbn": kdp_data.isbn,
        "generate_cover": kdp_data.generate_cover,
        "royalty_rate": kdp_data.royalty_rate
    }

    return await export_service.create_export_job(
        user_id=current_user.id,
        project_id=job_id,  # This should be project_id, but using job_id for KDP workflow
        export_format="kdp",
        kdp_metadata=kdp_metadata
    )

@router.get("/kdp/submissions")
async def get_kdp_submissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 50
):
    """Get KDP submissions history"""
    try:
        result = await db.execute(
            select(KDPSubmission)
            .where(KDPSubmission.user_id == current_user.id)
            .order_by(desc(KDPSubmission.created_at))
            .offset(skip)
            .limit(limit)
        )
        submissions = result.scalars().all()

        return [
            {
                "id": sub.id,
                "export_job_id": sub.export_job_id,
                "kdp_title": sub.kdp_title,
                "kdp_author": sub.kdp_author,
                "isbn": sub.isbn,
                "kdp_status": sub.kdp_status,
                "publication_date": sub.publication_date.isoformat() if sub.publication_date else None,
                "royalty_rate": sub.royalty_rate,
                "sales_url": sub.sales_url,
                "created_at": sub.created_at.isoformat()
            }
            for sub in submissions
        ]

    except Exception as e:
        logger.error(f"Failed to get KDP submissions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve KDP submissions"
        )

@router.get("/kdp/status/{submission_id}")
async def get_kdp_submission_status(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get KDP submission status"""
    try:
        result = await db.execute(
            select(KDPSubmission).where(
                and_(
                    KDPSubmission.id == submission_id,
                    KDPSubmission.user_id == current_user.id
                )
            )
        )
        submission = result.scalar_one_or_none()

        if not submission:
            raise HTTPException(
                status_code=404,
                detail="KDP submission not found"
            )

        return {
            "id": submission.id,
            "kdp_title": submission.kdp_title,
            "kdp_author": submission.kdp_author,
            "isbn": submission.isbn,
            "kdp_status": submission.kdp_status,
            "publication_date": submission.publication_date.isoformat() if submission.publication_date else None,
            "royalty_rate": submission.royalty_rate,
            "sales_url": submission.sales_url,
            "last_synced": submission.last_synced.isoformat() if submission.last_synced else None,
            "sales_rank": submission.sales_rank,
            "reviews_count": submission.reviews_count,
            "average_rating": submission.average_rating
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get KDP submission status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve KDP submission status"
        )