"""
Export Model for Journal Platform
Phase 3.4: Export Service Implementation
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from enum import Enum

from .base import BaseModel


class ExportFormat(str, Enum):
    """Supported export formats"""
    PDF = "pdf"
    EPUB = "epub"
    KDP = "kdp"


class ExportJob(BaseModel):
    """Export job model for tracking export operations"""
    __tablename__ = 'export_jobs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    # Export configuration
    export_format = Column(String, nullable=False)  # pdf, epub, kdp
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed, cancelled

    # Progress tracking
    progress = Column(Integer, default=0)  # 0-100 percentage
    estimated_completion = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Export results
    file_url = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    download_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Export configuration (JSON fields)
    export_options = Column(JSON, nullable=True)  # Format-specific options
    kdp_metadata = Column(JSON, nullable=True)  # KDP publishing metadata

    # Processing details
    processing_time = Column(Integer, nullable=True)  # seconds
    queue_position = Column(Integer, nullable=True)
    worker_id = Column(String, nullable=True)  # ID of worker processing the job

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    project = relationship("Project", foreign_keys=[project_id])


class ExportTemplate(BaseModel):
    """Export template model for reusable export configurations"""
    __tablename__ = 'export_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # pdf, epub, kdp, custom
    export_format = Column(String, nullable=False)  # pdf, epub, kdp

    # Template configuration
    template_options = Column(JSON, nullable=False)  # Default export options
    kdp_settings = Column(JSON, nullable=True)  # KDP-specific settings

    # Template metadata
    is_premium = Column(Boolean, default=False)
    is_system = Column(Boolean, default=True)  # System templates vs user templates
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # For user templates
    usage_count = Column(Integer, default=0)
    rating = Column(Integer, nullable=True)  # 1-5 stars

    # Preview
    preview_url = Column(String, nullable=True)
    sample_output_url = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class ExportHistory(BaseModel):
    """Export history for tracking user export patterns"""
    __tablename__ = 'export_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    export_job_id = Column(Integer, ForeignKey('export_jobs.id'), nullable=True)

    # Export summary
    export_format = Column(String, nullable=False)
    project_title = Column(String, nullable=False)
    project_type = Column(String, nullable=True)

    # Results
    status = Column(String, nullable=False)  # completed, failed, cancelled
    file_size = Column(Integer, nullable=True)
    processing_time = Column(Integer, nullable=True)

    # Analytics
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    source = Column(String, nullable=True)  # web, api, mobile

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    export_job = relationship("ExportJob", foreign_keys=[export_job_id])


class KDPSubmission(BaseModel):
    """KDP submission tracking"""
    __tablename__ = 'kdp_submissions'

    id = Column(Integer, primary_key=True, index=True)
    export_job_id = Column(Integer, ForeignKey('export_jobs.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Amazon KDP details
    kdp_submission_id = Column(String, nullable=True)  # Amazon's submission ID
    kdp_project_id = Column(String, nullable=True)  # Amazon's project ID
    kdp_title = Column(String, nullable=False)
    kdp_subtitle = Column(String, nullable=True)
    kdp_author = Column(String, nullable=False)
    kdp_publisher = Column(String, nullable=True)

    # Book details
    isbn = Column(String, nullable=True)
    language = Column(String, nullable=False)
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)

    # Publishing status
    kdp_status = Column(String, nullable=False, default="draft")  # draft, review, live, removed
    publication_date = Column(DateTime(timezone=True), nullable=True)
    last_synced = Column(DateTime(timezone=True), nullable=True)

    # Financial
    royalty_rate = Column(String, nullable=True)
    list_price = Column(String, nullable=True)
    currency = Column(String, nullable=True)

    # Sales tracking
    sales_rank = Column(Integer, nullable=True)
    reviews_count = Column(Integer, default=0)
    average_rating = Column(Integer, nullable=True)

    # Metadata
    kdp_categories = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    export_job = relationship("ExportJob", foreign_keys=[export_job_id])
    user = relationship("User", foreign_keys=[user_id])


class ExportFile(BaseModel):
    """Export file management"""
    __tablename__ = 'export_files'

    id = Column(Integer, primary_key=True, index=True)
    export_job_id = Column(Integer, ForeignKey('export_jobs.id'), nullable=False)

    # File details
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    checksum = Column(String, nullable=True)  # MD5 or SHA256

    # File metadata
    file_type = Column(String, nullable=False)  # pdf, epub, cover, manuscript
    is_primary = Column(Boolean, default=False)  # Main export file vs supplementary
    is_public = Column(Boolean, default=False)  # For preview files

    # Storage details
    storage_backend = Column(String, default="local")  # local, s3, gcs, azure
    storage_path = Column(String, nullable=True)
    cdn_url = Column(String, nullable=True)

    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    download_count = Column(Integer, default=0)

    # Relationships
    export_job = relationship("ExportJob", foreign_keys=[export_job_id])


class ExportQueue(BaseModel):
    """Export queue management"""
    __tablename__ = 'export_queue'

    id = Column(Integer, primary_key=True, index=True)
    export_job_id = Column(Integer, ForeignKey('export_jobs.id'), nullable=False)
    queue_name = Column(String, nullable=False)  # priority, standard, bulk
    priority = Column(Integer, default=5)  # 1-10, lower number = higher priority

    # Queue status
    status = Column(String, nullable=False, default="queued")  # queued, processing, completed, failed
    worker_id = Column(String, nullable=True)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)

    # Timing
    queued_at = Column(DateTime(timezone=True), server_default=func.now())
    started_processing_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # seconds

    # Queue metadata
    batch_id = Column(String, nullable=True)  # For batch processing
    parent_job_id = Column(Integer, nullable=True)  # For job dependencies

    # Relationships
    export_job = relationship("ExportJob", foreign_keys=[export_job_id])