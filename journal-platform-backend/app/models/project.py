"""
Project Model for Journal Craft Crew Platform
Project management and organization
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .base import BaseModel


class Project(BaseModel):
    """Project model for organizing journal entries and content"""
    __tablename__ = 'projects'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Basic project information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)

    # Project type and configuration
    project_type = Column(String(50), nullable=False, default="journal")  # 'journal', 'book', 'collection'
    category = Column(String(100), nullable=True)  # 'personal', 'travel', 'work', 'creative', etc.

    # Project metadata
    cover_image = Column(String(500), nullable=True)
    color_scheme = Column(JSON, nullable=True)  # Theme colors
    font_preferences = Column(JSON, nullable=True)

    # Project settings
    is_public = Column(Boolean, default=False)
    allow_collaboration = Column(Boolean, default=False)
    allow_comments = Column(Boolean, default=True)
    enable_ai_generation = Column(Boolean, default=True)

    # Project status
    status = Column(String(50), nullable=False, default="active")  # 'active', 'completed', 'archived', 'deleted'
    progress = Column(Integer, default=0)  # 0-100 percentage

    # Content statistics
    word_count = Column(Integer, default=0)
    entry_count = Column(Integer, default=0)
    estimated_reading_time = Column(Integer, nullable=True)  # minutes

    # Project timeline
    start_date = Column(DateTime(timezone=True), nullable=True)
    target_date = Column(DateTime(timezone=True), nullable=True)
    completion_date = Column(DateTime(timezone=True), nullable=True)

    # AI Generation settings
    ai_style_preferences = Column(JSON, nullable=True)
    ai_tone = Column(String(100), nullable=True)  # 'formal', 'casual', 'creative', etc.
    ai_topics = Column(JSON, nullable=True)  # Preferred topics for AI generation

    # Export settings
    export_preferences = Column(JSON, nullable=True)
    default_export_format = Column(String(50), default="pdf")

    # Template and structure
    template_id = Column(Integer, ForeignKey('journal_templates.id'), nullable=True)
    structure_template = Column(JSON, nullable=True)  # Chapter/section structure

    # Collaboration settings
    collaborators = Column(JSON, nullable=True)  # List of user IDs and permissions
    owner_notes = Column(Text, nullable=True)

    # Publishing settings
    publish_settings = Column(JSON, nullable=True)
    kdp_enabled = Column(Boolean, default=False)

    # Metadata
    tags = Column(JSON, nullable=True)
    search_keywords = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    journal_entries = relationship("JournalEntry", back_populates="project", cascade="all, delete-orphan")
    export_jobs = relationship("ExportJob", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}', user_id={self.user_id})>"

    def update_statistics(self):
        """Update project statistics based on journal entries"""
        # This would typically be called when entries are added/updated
        # Implementation would aggregate data from related journal entries
        pass

    def is_collaborator(self, user_id: int) -> bool:
        """Check if a user is a collaborator on this project"""
        if not self.collaborators:
            return False
        return any(collab.get('user_id') == user_id for collab in self.collaborators)

    def get_collaborator_role(self, user_id: int) -> str:
        """Get the role of a collaborator"""
        if not self.collaborators:
            return None
        for collab in self.collaborators:
            if collab.get('user_id') == user_id:
                return collab.get('role', 'viewer')
        return None

    def can_edit(self, user_id: int) -> bool:
        """Check if user can edit this project"""
        if self.user_id == user_id:
            return True
        role = self.get_collaborator_role(user_id)
        return role in ['editor', 'admin']

    def to_dict(self, include_sensitive=False):
        """Convert project to dictionary"""
        data = super().to_dict()
        if not include_sensitive:
            # Remove sensitive or unnecessary fields for public display
            data.pop('owner_notes', None)
            data.pop('collaborators', None)
        return data