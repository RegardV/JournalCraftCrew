"""
Inventory Models for Team Engagement and Activity Tracking
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
from enum import Enum

from .base import BaseModel


class ActivityType(str, Enum):
    """Types of team activities that can be tracked"""
    GENERATING = "generating"
    REVIEWING = "reviewing"
    EDITING = "editing"
    UPLOADING = "uploading"
    COMMENTING = "commenting"
    ASSIGNING = "assigning"
    APPROVING = "approving"
    EXPORTING = "exporting"


class InventoryTeamActivity(BaseModel):
    """Track team activities on journal inventories"""
    __tablename__ = 'inventory_team_activity'

    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=True)

    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # ActivityType value
    details = Column(Text, nullable=True)  # Human-readable description
    progress = Column(Integer, default=0)  # 0-100 percentage
    status = Column(String(50), default="active")  # 'active', 'completed', 'failed', 'paused'

    # Activity metadata
    target_id = Column(String(255), nullable=True)  # ID of the item being worked on
    target_type = Column(String(50), nullable=True)  # 'journal_entry', 'project', 'media', etc.
    assigned_to = Column(Integer, ForeignKey('users.id'), nullable=True)  # If assigned to someone else
    priority = Column(String(20), default="normal")  # 'low', 'normal', 'high', 'urgent'

    # Timing information
    estimated_completion = Column(DateTime(timezone=True), nullable=True)
    actual_completion = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Activity data
    metadata = Column(JSON, nullable=True)  # Additional activity-specific data
    result = Column(JSON, nullable=True)  # Activity results/output
    error_message = Column(Text, nullable=True)

    # Collaboration data
    collaborators = Column(JSON, nullable=True)  # List of user IDs involved
    visibility = Column(String(20), default="team")  # 'private', 'team', 'public'

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    project = relationship("Project", foreign_keys=[project_id])
    journal_entry = relationship("JournalEntry", foreign_keys=[journal_entry_id])

    def __repr__(self):
        return f"<InventoryTeamActivity(id={self.id}, type='{self.activity_type}', user_id={self.user_id})>"

    def is_active(self):
        """Check if activity is currently active"""
        return self.status == "active" and not self.actual_completion

    def is_overdue(self):
        """Check if activity is overdue"""
        if self.estimated_completion and not self.actual_completion:
            return datetime.now(timezone.utc) > self.estimated_completion
        return False

    def get_duration_minutes(self):
        """Calculate duration in minutes if completed"""
        if self.actual_completion:
            duration = self.actual_completion - self.created_at
            return int(duration.total_seconds() / 60)
        return None


class InventoryGenerationContext(BaseModel):
    """Store context for AI-powered generation from inventory"""
    __tablename__ = 'inventory_generation_context'

    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id'), nullable=True)

    # Context information
    context_type = Column(String(50), nullable=False)  # 'empty_inventory', 'content_gap', 'enhancement', etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Generation context
    context_data = Column(JSON, nullable=False)  # Rich context information
    inventory_analysis = Column(JSON, nullable=True)  # Analysis of current inventory state
    user_preferences = Column(JSON, nullable=True)  # User's generation preferences

    # AI suggestions
    suggestions = Column(JSON, nullable=True)  # AI-powered generation suggestions
    recommendation_score = Column(Float, nullable=True)  # 0-1 confidence score
    recommendation_reason = Column(Text, nullable=True)

    # Generation parameters
    generation_config = Column(JSON, nullable=True)  # AI generation configuration
    template_id = Column(Integer, nullable=True)  # Suggested template
    tone = Column(String(100), nullable=True)  # Suggested tone
    style_preferences = Column(JSON, nullable=True)

    # Content gaps analysis
    identified_gaps = Column(JSON, nullable=True)  # Missing content categories
    suggested_topics = Column(JSON, nullable=True)  # AI-suggested topics
    content_structure = Column(JSON, nullable=True)  # Suggested structure

    # Team assignment
    suggested_assignees = Column(JSON, nullable=True)  # Suggested team members
    collaboration_type = Column(String(50), nullable=True)  # 'individual', 'pair', 'team'

    # Status tracking
    status = Column(String(50), default="pending")  # 'pending', 'accepted', 'rejected', 'completed'
    accepted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    accepted_user = relationship("User", foreign_keys=[accepted_by])
    project = relationship("Project", foreign_keys=[project_id])
    journal_entry = relationship("JournalEntry", foreign_keys=[journal_entry_id])

    def __repr__(self):
        return f"<InventoryGenerationContext(id={self.id}, type='{self.context_type}', user_id={self.user_id})>"

    def is_expired(self):
        """Check if context has expired"""
        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at
        return False

    def is_active(self):
        """Check if context is still active and pending"""
        return self.status == "pending" and not self.is_expired()


class QuickAction(BaseModel):
    """Quick actions available from inventory engagement interface"""
    __tablename__ = 'inventory_quick_actions'

    # Action identification
    action_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)  # Icon identifier

    # Action configuration
    action_type = Column(String(50), nullable=False)  # 'generation', 'navigation', 'upload', 'edit', etc.
    target_route = Column(String(255), nullable=True)  # Frontend route for navigation
    api_endpoint = Column(String(255), nullable=True)  # Backend endpoint to call

    # Display and behavior
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    requires_context = Column(Boolean, default=False)  # Requires inventory context to be relevant

    # Conditional logic
    conditions = Column(JSON, nullable=True)  # Conditions for when action should be shown
    parameters = Column(JSON, nullable=True)  # Default parameters for the action

    # Permissions and roles
    required_permissions = Column(JSON, nullable=True)  # Required user permissions
    allowed_user_types = Column(JSON, nullable=True)  # 'owner', 'collaborator', 'viewer', etc.

    # Analytics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)  # 0-1 success rate

    def __repr__(self):
        return f"<QuickAction(id={self.id}, action_id='{self.action_id}', title='{self.title}')>"

    def is_available_for_user(self, user, inventory_context):
        """Check if action is available for given user and context"""
        if not self.is_active:
            return False

        # Check permissions
        if self.required_permissions:
            # TODO: Implement permission checking logic
            pass

        # Check conditions
        if self.conditions and inventory_context:
            return self._evaluate_conditions(inventory_context)

        return True

    def _evaluate_conditions(self, context):
        """Evaluate conditional logic for action availability"""
        # TODO: Implement condition evaluation logic
        # Examples: has_content: false, is_owner: true, team_size: >1, etc.
        return True