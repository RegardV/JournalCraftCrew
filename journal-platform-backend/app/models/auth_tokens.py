"""
Authentication Token Models
Database models for email verification, password reset, and refresh tokens
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class EmailVerification(BaseModel):
    """Email verification tokens model"""
    __tablename__ = 'email_verifications'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def is_expired(self):
        """Check if token has expired"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()


class PasswordReset(BaseModel):
    """Password reset tokens model"""
    __tablename__ = 'password_resets'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def is_expired(self):
        """Check if token has expired"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()


class RefreshToken(BaseModel):
    """Refresh tokens model for token storage and management"""
    __tablename__ = 'refresh_tokens'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    device_info = Column(Text, nullable=True)  # JSON string with device info
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def is_expired(self):
        """Check if token has expired"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if token is valid (not revoked and not expired)"""
        return not self.is_revoked and not self.is_expired()

    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used_at = datetime.utcnow()


class OAuthAccount(BaseModel):
    """OAuth account linking model"""
    __tablename__ = 'oauth_accounts'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    provider = Column(String(50), nullable=False)  # 'google', 'github', etc.
    provider_id = Column(String(255), nullable=False)
    provider_email = Column(String(255), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    token_type = Column(String(50), nullable=True)
    scope = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def is_access_token_expired(self):
        """Check if OAuth access token has expired"""
        if not self.expires_at:
            return False  # Some providers don't expire tokens
        return datetime.utcnow() > self.expires_at


class LoginAttempt(BaseModel):
    """Login attempt tracking for security"""
    __tablename__ = 'login_attempts'

    email = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Optional user reference (if email exists in system)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class SecurityEvent(BaseModel):
    """Security event logging for audit trail"""
    __tablename__ = 'security_events'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    event_type = Column(String(100), nullable=False)  # 'login', 'logout', 'password_change', etc.
    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string with additional event data
    severity = Column(String(20), default="info")  # 'info', 'warning', 'critical'

    # Relationships
    user = relationship("User", foreign_keys=[user_id])