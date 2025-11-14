"""
User Model for Journal Craft Crew Platform
Authentication and user profile management
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum

from .base import BaseModel


class UserSubscription(str, Enum):
    """User subscription types"""
    FREE = "free"
    PREMIUM = "premium"


class User(BaseModel):
    """User account model for authentication and profile management"""
    __tablename__ = 'users'

    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)

    # Authentication
    password_hash = Column(String(255), nullable=False)  # For local auth
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    reset_password_expires = Column(DateTime(timezone=True), nullable=True)

    # OAuth2 providers
    google_id = Column(String(255), nullable=True, unique=True)
    github_id = Column(String(255), nullable=True, unique=True)
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'github', etc.

    # User preferences
    preferences = Column(JSON, nullable=True)  # User settings, themes, etc.
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")

    # User profile and subscription
    profile_type = Column(String(50), default="personal_journaler")  # 'personal_journaler', 'content_creator'
    subscription = Column(String(20), default=UserSubscription.FREE)  # Using UserSubscription enum
    library_access = Column(Boolean, default=True)

    # OpenAI API configuration (user brings their own key)
    openai_api_key = Column(String(255), nullable=True)  # Encrypted user's OpenAI API key
    ai_provider = Column(String(50), default="openai")  # AI provider choice

    # Legacy billing fields (kept for backwards compatibility)
    is_premium = Column(Boolean, default=False)
    subscription_id = Column(String(255), nullable=True)
    subscription_expires = Column(DateTime(timezone=True), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # User status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)

    # Profile information
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)

    # Email preferences
    email_notifications = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=False)
    digest_frequency = Column(String(20), default="weekly")  # 'daily', 'weekly', 'monthly'

    # Privacy settings
    profile_public = Column(Boolean, default=False)
    allow_analytics = Column(Boolean, default=True)

    # Metadata
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    referral_source = Column(String(255), nullable=True)
    referral_code = Column(String(50), nullable=True)

    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    journal_templates = relationship("JournalTemplate", back_populates="user", cascade="all, delete-orphan")
    journal_media = relationship("JournalMedia", back_populates="user", cascade="all, delete-orphan")
    export_jobs = relationship("ExportJob", back_populates="user", cascade="all, delete-orphan")
    export_templates = relationship("ExportTemplate", back_populates="user", cascade="all, delete-orphan")
    export_history = relationship("ExportHistory", back_populates="user", cascade="all, delete-orphan")
    kdp_submissions = relationship("KDPSubmission", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary, optionally including sensitive fields"""
        data = super().to_dict()
        if not include_sensitive:
            # Remove sensitive fields
            sensitive_fields = [
                'password_hash', 'verification_token', 'reset_password_token',
                'google_id', 'github_id', 'stripe_customer_id', 'ip_address',
                'openai_api_key'  # Never expose API keys in API responses
            ]
            for field in sensitive_fields:
                data.pop(field, None)
        return data

    def update_last_login(self):
        """Update last login timestamp and increment login count"""
        self.last_login = datetime.utcnow()
        self.login_count += 1

    def is_subscription_active(self):
        """Check if user has active premium subscription"""
        if not self.is_premium or not self.subscription_expires:
            return False
        return datetime.utcnow() < self.subscription_expires