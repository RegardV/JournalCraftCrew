"""
Journal Platform Database Models
Clean implementation with proper BaseModel inheritance
"""

# Import the base model first
from .base import BaseModel

# Import individual model modules
from .user import User
from .project import Project
from .journal import JournalEntry, JournalTemplate, JournalMedia
from .export import (
    ExportJob, ExportFormat, ExportTemplate, ExportHistory,
    KDPSubmission, ExportFile, ExportQueue
)
from .auth_tokens import (
    EmailVerification, PasswordReset, RefreshToken, OAuthAccount,
    LoginAttempt, SecurityEvent
)
from .inventory import (
    InventoryTeamActivity, InventoryGenerationContext, QuickAction, ActivityType
)

# Export all models for easy importing
__all__ = [
    # Base
    "BaseModel",

    # Core entities
    "User",
    "Project",

    # Journal entities
    "JournalEntry",
    "JournalTemplate",
    "JournalMedia",

    # Export entities
    "ExportJob",
    "ExportFormat",
    "ExportTemplate",
    "ExportHistory",
    "KDPSubmission",
    "ExportFile",
    "ExportQueue",

    # Authentication entities
    "EmailVerification",
    "PasswordReset",
    "RefreshToken",
    "OAuthAccount",
    "LoginAttempt",
    "SecurityEvent",

    # Inventory entities
    "InventoryTeamActivity",
    "InventoryGenerationContext",
    "QuickAction",
    "ActivityType",
]