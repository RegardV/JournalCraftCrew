"""
Export Service for PDF, EPUB, and KDP integration
Phase 3.4: Export Service Implementation
"""

import asyncio
import tempfile
import os
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException, status
import json
import uuid
from pathlib import Path
import logging

from app.models.export import ExportJob, ExportFormat
from app.models.project import Project
from app.models.user import User
from app.models.theme import Theme
from app.core.database import get_async_session

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting projects to various formats and platforms"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.temp_dir = Path(tempfile.gettempdir()) / "journal_exports"

    async def create_export_job(
        self,
        user_id: int,
        project_id: int,
        export_format: str,
        export_options: Optional[Dict[str, Any]] = None,
        kdp_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new export job with validation"""
        try:
            # Validate project exists and belongs to user
            project_result = await self.db.execute(
                select(Project).where(
                    and_(Project.id == project_id, Project.user_id == user_id)
                )
            )
            project = project_result.scalar_one_or_none()

            if not project:
                raise HTTPException(
                    status_code=404,
                    detail="Project not found"
                )

            # Validate export format
            valid_formats = [format.value for format in ExportFormat]
            if export_format not in valid_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid export format. Supported formats: {', '.join(valid_formats)}"
                )

            # Check if export is already in progress
            existing_export = await self.db.execute(
                select(ExportJob).where(
                    and_(
                        ExportJob.project_id == project_id,
                        ExportJob.user_id == user_id,
                        ExportJob.status == "pending"
                    )
                )
            )
            if existing_export.scalar_one_or_none():
                raise HTTPException(
                    status_code=409,
                    detail="Export already in progress for this project"
                )

            # Create export job
            export_job = ExportJob(
                user_id=user_id,
                project_id=project_id,
                export_format=export_format,
                status="pending",
                progress=0,
                export_options=export_options or {},
                kdp_metadata=kdp_metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(export_job)
            await self.db.commit()
            await self.db.refresh(export_job)

            # Start async export processing
            asyncio.create_task(self._process_export_job(export_job.id))

            logger.info(f"Export job created: {export_job.id} - {export_format}")
            return {
                "message": "Export job created successfully",
                "export_job": {
                    "id": export_job.id,
                    "project_id": export_job.project_id,
                    "export_format": export_job.export_format,
                    "status": export_job.status,
                    "created_at": export_job.created_at.isoformat(),
                    "estimated_completion": self._estimate_completion_time(export_format)
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create export job: {e}")
            raise HTTPException(
                status_code=500,
                detail="Export job creation failed due to internal error"
            )

    async def get_export_jobs(
        self,
        user_id: int,
        project_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get user's export jobs with filtering"""
        try:
            # Build query
            query = select(ExportJob).where(ExportJob.user_id == user_id)

            # Apply filters
            if project_id:
                query = query.where(ExportJob.project_id == project_id)
            if status_filter:
                query = query.where(ExportJob.status == status_filter)

            # Add ordering
            query = query.order_by(ExportJob.created_at.desc())

            # Execute with pagination
            result = await self.db.execute(query.offset(skip).limit(limit))
            export_jobs = result.scalars().all()

            # Get total count
            count_query = select(func.count(ExportJob.id)).where(ExportJob.user_id == user_id)
            if project_id:
                count_query = count_query.where(ExportJob.project_id == project_id)
            if status_filter:
                count_query = count_query.where(ExportJob.status == status_filter)

            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            return {
                "export_jobs": [
                    {
                        "id": job.id,
                        "project_id": job.project_id,
                        "export_format": job.export_format,
                        "status": job.status,
                        "progress": job.progress,
                        "file_url": job.file_url,
                        "error_message": job.error_message,
                        "export_options": job.export_options,
                        "kdp_metadata": job.kdp_metadata,
                        "created_at": job.created_at.isoformat(),
                        "updated_at": job.updated_at.isoformat(),
                        "completed_at": job.completed_at.isoformat() if job.completed_at else None
                    }
                    for job in export_jobs
                ],
                "pagination": {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "has_more": skip + limit < total
                }
            }

        except Exception as e:
            logger.error(f"Failed to get export jobs: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve export jobs"
            )

    async def get_export_job(
        self,
        export_job_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Get specific export job with ownership verification"""
        try:
            result = await self.db.execute(
                select(ExportJob).where(
                    and_(ExportJob.id == export_job_id, ExportJob.user_id == user_id)
                )
            )
            export_job = result.scalar_one_or_none()

            if not export_job:
                raise HTTPException(
                    status_code=404,
                    detail="Export job not found"
                )

            return {
                "export_job": {
                    "id": export_job.id,
                    "project_id": export_job.project_id,
                    "export_format": export_job.export_format,
                    "status": export_job.status,
                    "progress": export_job.progress,
                    "file_url": export_job.file_url,
                    "file_size": export_job.file_size,
                    "error_message": export_job.error_message,
                    "export_options": export_job.export_options,
                    "kdp_metadata": export_job.kdp_metadata,
                    "created_at": export_job.created_at.isoformat(),
                    "updated_at": export_job.updated_at.isoformat(),
                    "completed_at": export_job.completed_at.isoformat() if export_job.completed_at else None
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get export job: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve export job"
            )

    async def cancel_export_job(
        self,
        export_job_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Cancel an export job"""
        try:
            result = await self.db.execute(
                select(ExportJob).where(
                    and_(
                        ExportJob.id == export_job_id,
                        ExportJob.user_id == user_id,
                        ExportJob.status.in_(["pending", "processing"])
                    )
                )
            )
            export_job = result.scalar_one_or_none()

            if not export_job:
                raise HTTPException(
                    status_code=404,
                    detail="Export job not found or cannot be cancelled"
                )

            export_job.status = "cancelled"
            export_job.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Export job cancelled: {export_job_id}")
            return {"message": "Export job cancelled successfully"}

        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to cancel export job: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to cancel export job"
            )

    async def get_export_statistics(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Get export usage statistics"""
        try:
            # Get export counts by format
            format_counts = await self.db.execute(
                select(
                    ExportJob.export_format,
                    func.count(ExportJob.id).label("count")
                ).where(ExportJob.user_id == user_id)
                .group_by(ExportJob.export_format)
            )
            format_result = format_counts.all()

            # Get export counts by status
            status_counts = await self.db.execute(
                select(
                    ExportJob.status,
                    func.count(ExportJob.id).label("count")
                ).where(ExportJob.user_id == user_id)
                .group_by(ExportJob.status)
            )
            status_result = status_counts.all()

            # Build statistics
            format_stats = {row.export_format: row.count for row in format_result}
            status_stats = {row.status: row.count for row in status_result}

            total_exports = sum(status_stats.values())
            completed_exports = status_stats.get("completed", 0)
            success_rate = round((completed_exports / total_exports * 100), 1) if total_exports > 0 else 0

            return {
                "total_exports": total_exports,
                "format_breakdown": format_stats,
                "status_breakdown": status_stats,
                "success_rate": success_rate,
                "most_used_format": max(format_stats.items(), key=lambda x: x[1])[0] if format_stats else None
            }

        except Exception as e:
            logger.error(f"Failed to get export statistics: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve export statistics"
            )

    async def _process_export_job(
        self,
        export_job_id: int
    ) -> None:
        """Process export job asynchronously"""
        try:
            # Get export job
            result = await self.db.execute(
                select(ExportJob).where(ExportJob.id == export_job_id)
            )
            export_job = result.scalar_one_or_none()

            if not export_job:
                logger.error(f"Export job {export_job_id} not found")
                return

            # Get project with theme
            project_result = await self.db.execute(
                select(Project).where(Project.id == export_job.project_id)
            )
            project = project_result.scalar_one_or_none()

            if not project:
                logger.error(f"Project {export_job.project_id} not found")
                await self._mark_job_failed(export_job_id, "Project not found")
                return

            # Update status to processing
            export_job.status = "processing"
            export_job.progress = 10
            await self.db.commit()

            # Export based on format
            if export_job.export_format == "pdf":
                await self._export_to_pdf(export_job, project)
            elif export_job.export_format == "epub":
                await self._export_to_epub(export_job, project)
            elif export_job.export_format == "kdp":
                await self._export_to_kdp(export_job, project)
            else:
                await self._mark_job_failed(export_job_id, f"Unsupported export format: {export_job.export_format}")

        except Exception as e:
            logger.error(f"Export job processing failed: {e}")
            await self._mark_job_failed(export_job_id, str(e))

    async def _export_to_pdf(
        self,
        export_job: ExportJob,
        project: Project
    ) -> None:
        """Export project to PDF format"""
        try:
            # Update progress
            export_job.progress = 30
            await self.db.commit()

            # Generate PDF content
            pdf_content = await self._generate_pdf_content(project)

            # Update progress
            export_job.progress = 70
            await self.db.commit()

            # Save file
            file_path = await self._save_export_file(
                export_job, project, pdf_content, "pdf"
            )

            # Mark as completed
            export_job.status = "completed"
            export_job.progress = 100
            export_job.file_url = f"/exports/{file_path.name}"
            export_job.file_size = len(pdf_content)
            export_job.completed_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"PDF export completed: {export_job.id}")

        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            await self._mark_job_failed(export_job.id, str(e))

    async def _export_to_epub(
        self,
        export_job: ExportJob,
        project: Project
    ) -> None:
        """Export project to EPUB format"""
        try:
            # Update progress
            export_job.progress = 30
            await self.db.commit()

            # Generate EPUB content
            epub_content = await self._generate_epub_content(project)

            # Update progress
            export_job.progress = 70
            await self.db.commit()

            # Save file
            file_path = await self._save_export_file(
                export_job, project, epub_content, "epub"
            )

            # Mark as completed
            export_job.status = "completed"
            export_job.progress = 100
            export_job.file_url = f"/exports/{file_path.name}"
            export_job.file_size = len(epub_content)
            export_job.completed_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"EPUB export completed: {export_job.id}")

        except Exception as e:
            logger.error(f"EPUB export failed: {e}")
            await self._mark_job_failed(export_job.id, str(e))

    async def _export_to_kdp(
        self,
        export_job: ExportJob,
        project: Project
    ) -> None:
        """Export project to KDP-ready format"""
        try:
            # Update progress
            export_job.progress = 20
            await self.db.commit()

            # Generate KDP manuscript
            manuscript_content = await self._generate_kdp_manuscript(project)

            # Update progress
            export_job.progress = 50
            await self.db.commit()

            # Generate KDP cover if needed
            if export_job.kdp_metadata.get("generate_cover", False):
                cover_content = await self._generate_kdp_cover(project, export_job.kdp_metadata)
                export_job.progress = 70
                await self.db.commit()

            # Save manuscript
            manuscript_path = await self._save_export_file(
                export_job, project, manuscript_content, "pdf"
            )

            # Mark as completed (ready for KDP upload)
            export_job.status = "completed"
            export_job.progress = 100
            export_job.file_url = f"/exports/{manuscript_path.name}"
            export_job.file_size = len(manuscript_content)
            export_job.completed_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"KDP export completed: {export_job.id}")

        except Exception as e:
            logger.error(f"KDP export failed: {e}")
            await self._mark_job_failed(export_job.id, str(e))

    async def _generate_pdf_content(self, project: Project) -> bytes:
        """Generate PDF content from project"""
        # This would integrate with a PDF generation library like reportlab
        # For now, return placeholder content
        pdf_header = f"%PDF-1.4\n% Generated for project: {project.title}\n"
        return pdf_header.encode('utf-8')

    async def _generate_epub_content(self, project: Project) -> bytes:
        """Generate EPUB content from project"""
        # This would integrate with an EPUB generation library
        # For now, return placeholder content
        epub_header = f"<?xml version='1.0' encoding='UTF-8'?>\n<package xmlns='http://www.idpf.org/2007/opf'>\n<title>{project.title}</title>\n"
        return epub_header.encode('utf-8')

    async def _generate_kdp_manuscript(self, project: Project) -> bytes:
        """Generate KDP-ready manuscript"""
        # KDP requires specific formatting for print-on-demand
        # This would generate a properly formatted PDF for KDP submission
        kdp_header = f"%PDF-1.4\n% KDP manuscript for: {project.title}\n"
        return kdp_header.encode('utf-8')

    async def _generate_kdp_cover(self, project: Project, metadata: Dict[str, Any]) -> bytes:
        """Generate KDP cover image"""
        # This would generate a cover based on theme and metadata
        cover_data = b"KDP cover image placeholder"
        return cover_data

    async def _save_export_file(
        self,
        export_job: ExportJob,
        project: Project,
        content: bytes,
        extension: str
    ) -> Path:
        """Save export file to storage"""
        # Ensure temp directory exists
        self.temp_dir.mkdir(exist_ok=True)

        # Generate unique filename
        filename = f"export_{export_job.id}_{project.title.replace(' ', '_')[:20]}_{uuid.uuid4().hex[:8]}.{extension}"
        file_path = self.temp_dir / filename

        # Save content
        with open(file_path, 'wb') as f:
            f.write(content)

        return file_path

    async def _mark_job_failed(
        self,
        export_job_id: int,
        error_message: str
    ) -> None:
        """Mark export job as failed"""
        try:
            result = await self.db.execute(
                select(ExportJob).where(ExportJob.id == export_job_id)
            )
            export_job = result.scalar_one_or_none()

            if export_job:
                export_job.status = "failed"
                export_job.error_message = error_message
                export_job.updated_at = datetime.utcnow()
                await self.db.commit()

        except Exception as e:
            logger.error(f"Failed to mark export job {export_job_id} as failed: {e}")

    def _estimate_completion_time(self, export_format: str) -> str:
        """Estimate completion time based on export format"""
        # Estimated times in seconds
        time_estimates = {
            "pdf": "2-5 minutes",
            "epub": "1-3 minutes",
            "kdp": "5-10 minutes"
        }
        return time_estimates.get(export_format, "2-5 minutes")