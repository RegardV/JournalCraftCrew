"""
Journal Platform Database Models
Phase 3: Backend Development
"""

from .base import BaseModel
from .export import ExportJob, ExportFormat, ExportTemplate, ExportHistory, KDPSubmission, ExportFile, ExportQueue
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Table, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserSubscription(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    AI_GENERATING = "ai_generating"
    AI_COMPLETED = "ai_completed"

class ProjectType(str, Enum):
    PERSONAL = "personal"
    PROJECT = "project"
    THERAPEUTIC = "therapeutic"
    CREATIVE = "creative"
    TRAVEL = "travel"
    FAMILY = "family"
    PROFESSIONAL = "professional"

# Association tables for many-to-many relationships
user_project_association = Table(
    'user_project_association',
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True)
)

class User(BaseModel):
    """User model for authentication and profile management"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    subscription = Column(String, nullable=False, default=UserSubscription.FREE)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Preferences (as JSON or separate model)
    preferences = Column(Text, nullable=True)  # JSON field for user preferences
    profile_type = Column(String, default="personal_journaler")  # personal_journaler OR content_creator
    ai_credits = Column(Integer, default=10)  # Credits for AI generation
    library_access = Column(Boolean, default=True)
    theme_preference = Column(String, nullable=True)
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    notification_email = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    notification_marketing = Column(Boolean, default=False)
    notification_updates = Column(Boolean, default=True)

    # Privacy settings
    profile_visibility = Column(String, default="private")  # private, friends, public
    share_analytics = Column(Boolean, default=True)
    allow_collaboration = Column(Boolean, default=True)

    # Relationships
    projects = relationship("Project", secondary="user_projects", back_populates="user_projects_assoc")
    collaborations = relationship("Project", secondary="collaborator_projects", back_populates="user_collaborations_assoc")

class Project(BaseModel):
    """Project model for journal management"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False, default=ProjectType.PERSONAL)
    status = Column(String, nullable=False, default=ProjectStatus.DRAFT)
    visibility = Column(String, default="private")  # private, shared, public
    theme_id = Column(Integer, ForeignKey('themes.id'), nullable=True)
    cover_image_url = Column(String, nullable=True)

    # AI Generation data
    ai_generated_content = Column(Text, nullable=True)  # JSON field for AI-generated content
    theme = Column(String, nullable=True)  # AI-generated theme

    # Project settings (JSON field)
    layout = Column(String, default="single-column")
    font_size = Column(String, default="medium")
    font_family = Column(String, default="serif")
    page_numbers = Column(Boolean, default=True)
    table_of_contents = Column(Boolean, default=False)
    date_format = Column(String, default="us")  # us, international, iso
    custom_css = Column(Text, nullable=True)

    # Metadata
    word_count = Column(Integer, default=0)
    estimated_reading_time = Column(Integer, default=0)
    tags = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_edited = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship("User", foreign_keys=[user_id])

    # Many-to-many relationships
    chapters = relationship("Chapter", secondary="project_chapters", back_populates="chapter_project_assoc")
    collaborators = relationship("User", secondary="project_collaborators", back_populates="user_project_association")
    export_history = relationship("ExportRecord", secondary="project_exports", back_populates="export_record_project_assoc")
    files = relationship("UploadedFile", secondary="project_files", back_populates="file_project_assoc")

class Chapter(BaseModel):
    """Chapter model for journal content management"""
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, default=0)
    word_count = Column(Integer, default=0)

    # Chapter metadata
    mood = Column(String, nullable=True)
    location = Column(String, nullable=True)
    weather = Column(String, nullable=True)
    is_locked = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    author = relationship("User", foreign_keys=[author_id])

class Theme(BaseModel):
    """Theme model for journal customization"""
    __tablename__ = 'themes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # vintage, modern, minimal, artistic, seasonal

    # Theme configuration (JSON fields)
    primary_color = Column(String, nullable=False)
    secondary_color = Column(String, nullable=False)
    accent_color = Column(String, nullable=False)
    background_color = Column(String, nullable=False)
    text_color = Column(String, nullable=False)
    border_color = Column(String, nullable=False)

    # Typography settings (JSON fields)
    primary_font = Column(String, nullable=False)
    secondary_font = Column(String, nullable=False)
    monospace_font = Column(String, nullable=False)

    # Layout configuration (JSON fields)
    page_margins = Column(Text, nullable=True)  # JSON object
    spacing = Column(Text, nullable=True)  # JSON object
    border_radius = Column(String, nullable=True)
    shadows = Column(Text, nullable=True)  # JSON object

    # Visual assets
    preview_url = Column(String, nullable=True)
    cover_templates = Column(Text, nullable=True)  # JSON array of template data

    # Theme metadata
    is_premium = Column(Boolean, default=False)
    is_seasonal = Column(Boolean, default=False)
    season = Column(String, nullable=True)  # spring, summer, autumn, winter

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    projects = relationship("Project", secondary="theme_projects", back_populates="project_theme_assoc")

# Association tables
project_theme_association = Table(
    'project_theme_association',
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('theme_id', Integer, ForeignKey('themes.id'))
)

class ExportRecord(BaseModel):
    """Export record for tracking journal exports"""
    __tablename__ = 'export_records'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    format = Column(String, nullable=False)  # pdf, epub, kdp
    status = Column(String, nullable=False)  # processing, completed, failed, expired
    file_size = Column(Integer, nullable=True)
    download_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Export settings (JSON fields)
    settings = Column(Text, nullable=True)  # JSON object for export parameters

    # KDP publishing data
    kdp_id = Column(String, nullable=True)
    kdp_title = Column(String, nullable=True)
    kdp_author = Column(String, nullable=True)
    isbn = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    kdp_status = Column(String, nullable=True)  # draft, review, published, withdrawn
    kdp_royalty_rate = Column(String, nullable=True)
    sales_url = Column(String, nullable=True)

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    user = relationship("User", foreign_keys=[user_id])

class UploadedFile(BaseModel):
    """Uploaded file model for file management"""
    __tablename__ = 'uploaded_files'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # image, document, other

    # File processing
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String, nullable=True)  # uploaded, processing, completed, failed
    processing_error = Column(Text, nullable=True)

    # File metadata
    alt_text = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    user = relationship("User", foreign_keys=[user_id])

# Association tables for many-to-many relationships
project_files_assoc = Table(
    'project_files_assoc',
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('file_id', Integer, ForeignKey('uploaded_files.id'))
)

project_chapters_assoc = Table(
    'project_chapters_assoc',
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('chapter_id', Integer, ForeignKey('chapters.id'))
)

project_exports_assoc = Table(
    'project_exports_assoc',
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('export_record_id', Integer, ForeignKey('export_records.id'))
)

user_collaborations_assoc = Table(
    'user_collaborations_assoc',
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

user_projects_assoc = Table(
    'user_projects_assoc',
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

chapter_project_assoc = Table(
    'chapter_project_assoc',
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('chapter_id', Integer, ForeignKey('chapters.id'))
)