"""
Journal Entry Model for User + AI Generated Content
Combines CrewAI output with user customization
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .base import BaseModel


class JournalEntry(BaseModel):
    """User's journal entries combining AI generation and personal editing"""
    __tablename__ = 'journal_entries'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)

    # Entry metadata
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    ai_generated_content = Column(Text, nullable=True)  # Original AI content
    word_count = Column(Integer, default=0)

    # AI Generation metadata
    ai_generation_date = Column(DateTime(timezone=True), nullable=True)
    ai_theme = Column(String, nullable=True)
    ai_agent_version = Column(String, nullable=True)
    generation_prompt = Column(Text, nullable=True)

    # User customization
    is_customized = Column(Boolean, default=False)
    customization_date = Column(DateTime(timezone=True), nullable=True)
    user_images = Column(JSON, nullable=True)  # User uploaded images
    custom_styling = Column(JSON, nullable=True)  # User-applied styling

    # Entry metadata
    mood = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # User-defined tags
    is_private = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)

    # Media
    cover_image = Column(String, nullable=True)  # User or AI generated cover
    attached_images = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_accessed = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    project = relationship("Project", foreign_keys=[project_id])


class JournalTemplate(BaseModel):
    """AI-generated journal templates users can customize"""
    __tablename__ = 'journal_templates'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Template metadata
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    theme = Column(String, nullable=False)

    # AI Generation data
    ai_generated_content = Column(Text, nullable=False)
    ai_prompt = Column(Text, nullable=True)
    ai_generation_config = Column(JSON, nullable=True)

    # Template usage
    usage_count = Column(Integer, default=0)
    rating = Column(Integer, nullable=True)  # User rating 1-5

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class JournalMedia(BaseModel):
    """Media attached to journal entries"""
    __tablename__ = 'journal_media'

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Media metadata
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)

    # Media type
    media_type = Column(String, nullable=False)  # 'cover', 'inline', 'attachment'
    is_ai_generated = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)

    # Media processing
    processed_at = Column(DateTime(timezone=True), nullable=True)
    thumbnail_path = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    entry = relationship("JournalEntry", foreign_keys=[entry_id])
    user = relationship("User", foreign_keys=[user_id])