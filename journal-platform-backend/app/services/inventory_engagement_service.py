"""
Inventory Engagement Service
Handles team activity tracking and contextual generation for inventory screens
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import json
import logging

from ..models.inventory import (
    InventoryTeamActivity, InventoryGenerationContext, QuickAction, ActivityType
)
from ..models.project import Project
from ..models.journal import JournalEntry
from ..models.user import User

logger = logging.getLogger(__name__)


class InventoryEngagementService:
    """Service for managing inventory engagement and team collaboration"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== Inventory Analysis ====================

    def analyze_inventory_state(
        self,
        user_id: int,
        project_id: Optional[int] = None,
        journal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze the current inventory state and provide engagement recommendations

        Returns:
            Dict containing inventory analysis, suggestions, and available actions
        """
        try:
            # Determine the scope of analysis
            if journal_id:
                analysis = self._analyze_journal_inventory(journal_id, user_id)
            elif project_id:
                analysis = self._analyze_project_inventory(project_id, user_id)
            else:
                analysis = self._analyze_user_inventory(user_id)

            # Get quick actions available for this context
            quick_actions = self.get_available_quick_actions(user_id, analysis)

            # Get current team activity
            team_activity = self.get_active_team_activity(user_id, project_id, journal_id)

            # Generate contextual suggestions
            suggestions = self._generate_contextual_suggestions(analysis, team_activity)

            return {
                "inventory_state": analysis,
                "quick_actions": quick_actions,
                "team_activity": team_activity,
                "suggestions": suggestions,
                "metadata": {
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                    "user_id": user_id,
                    "project_id": project_id,
                    "journal_id": journal_id
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing inventory state: {str(e)}")
            raise

    def _analyze_journal_inventory(self, journal_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze inventory state for a specific journal"""
        journal = self.db.query(JournalEntry).filter(
            JournalEntry.id == journal_id,
            JournalEntry.user_id == user_id
        ).first()

        if not journal:
            return {"has_content": False, "content_type": "none", "gaps": ["no_journal"]}

        # Check if journal has content
        has_content = bool(journal.content and len(journal.content.strip()) > 0)

        # Analyze content completeness
        content_gaps = []
        if not journal.title:
            content_gaps.append("missing_title")
        if not journal.content:
            content_gaps.append("missing_content")
        if not journal.cover_image:
            content_gaps.append("missing_cover")
        if not journal.tags:
            content_gaps.append("missing_tags")

        return {
            "has_content": has_content,
            "content_type": "journal",
            "content_quality": self._assess_content_quality(journal),
            "gaps": content_gaps,
            "journal_metadata": {
                "title": journal.title,
                "word_count": journal.word_count,
                "last_accessed": journal.last_accessed.isoformat() if journal.last_accessed else None,
                "ai_generated": bool(journal.ai_generated_content),
                "is_customized": journal.is_customized
            }
        }

    def _analyze_project_inventory(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze inventory state for a project"""
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()

        if not project:
            return {"has_content": False, "content_type": "none", "gaps": ["no_project"]}

        # Count journal entries in project
        entry_count = self.db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.project_id == project_id
        ).scalar()

        has_content = entry_count > 0

        # Analyze project completeness
        content_gaps = []
        if not project.description:
            content_gaps.append("missing_description")
        if not project.cover_image:
            content_gaps.append("missing_cover")
        if entry_count == 0:
            content_gaps.append("no_entries")
        if entry_count < 3:
            content_gaps.append("minimal_content")

        return {
            "has_content": has_content,
            "content_type": "project",
            "content_quality": self._assess_project_quality(project, entry_count),
            "gaps": content_gaps,
            "project_metadata": {
                "title": project.title,
                "entry_count": entry_count,
                "word_count": project.word_count,
                "progress": project.progress,
                "status": project.status
            }
        }

    def _analyze_user_inventory(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's overall inventory state"""
        # Count all journal entries
        entry_count = self.db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.user_id == user_id
        ).scalar()

        # Count all projects
        project_count = self.db.query(func.count(Project.id)).filter(
            Project.user_id == user_id,
            Project.status != 'deleted'
        ).scalar()

        has_content = entry_count > 0 or project_count > 0

        # Analyze overall completeness
        content_gaps = []
        if entry_count == 0:
            content_gaps.append("no_entries")
        if entry_count < 5:
            content_gaps.append("minimal_content")
        if project_count == 0:
            content_gaps.append("no_projects")

        return {
            "has_content": has_content,
            "content_type": "user_inventory",
            "content_quality": self._assess_user_inventory_quality(entry_count, project_count),
            "gaps": content_gaps,
            "inventory_metadata": {
                "entry_count": entry_count,
                "project_count": project_count,
                "analysis_scope": "user_level"
            }
        }

    # ==================== Content Quality Assessment ====================

    def _assess_content_quality(self, journal: JournalEntry) -> str:
        """Assess the quality of journal content"""
        if not journal.content:
            return "empty"

        word_count = journal.word_count or 0
        has_ai_content = bool(journal.ai_generated_content)
        is_customized = journal.is_customized
        has_media = bool(journal.attached_images or journal.cover_image)

        if word_count < 50:
            return "minimal"
        elif word_count < 200 and not has_media:
            return "basic"
        elif is_customized or has_media:
            return "enhanced"
        elif has_ai_content:
            return "ai_generated"
        else:
            return "standard"

    def _assess_project_quality(self, project: Project, entry_count: int) -> str:
        """Assess the quality and completeness of a project"""
        if entry_count == 0:
            return "empty"
        elif entry_count < 3:
            return "minimal"
        elif entry_count < 10:
            return "developing"
        elif project.progress and project.progress > 80:
            return "comprehensive"
        else:
            return "standard"

    def _assess_user_inventory_quality(self, entry_count: int, project_count: int) -> str:
        """Assess the overall quality of user's inventory"""
        if entry_count == 0:
            return "empty"
        elif entry_count < 5:
            return "minimal"
        elif entry_count < 20 and project_count < 2:
            return "developing"
        elif entry_count > 50 or project_count > 5:
            return "comprehensive"
        else:
            return "standard"

    # ==================== Team Activity Management ====================

    def get_active_team_activity(
        self,
        user_id: int,
        project_id: Optional[int] = None,
        journal_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get current team activity for the specified scope"""
        query = self.db.query(InventoryTeamActivity, User).join(
            User, InventoryTeamActivity.user_id == User.id
        ).filter(
            InventoryTeamActivity.status == "active"
        )

        # Filter by scope
        if journal_id:
            query = query.filter(InventoryTeamActivity.journal_entry_id == journal_id)
        elif project_id:
            query = query.filter(InventoryTeamActivity.project_id == project_id)
        else:
            query = query.filter(InventoryTeamActivity.user_id == user_id)

        activities = query.order_by(desc(InventoryTeamActivity.created_at)).limit(limit).all()

        result = []
        for activity, user in activities:
            result.append({
                "id": activity.id,
                "activity_type": activity.activity_type,
                "details": activity.details,
                "progress": activity.progress,
                "user": {
                    "id": user.id,
                    "name": user.full_name or user.username,
                    "email": user.email
                },
                "created_at": activity.created_at.isoformat(),
                "estimated_completion": activity.estimated_completion.isoformat() if activity.estimated_completion else None,
                "target_id": activity.target_id,
                "target_type": activity.target_type,
                "priority": activity.priority
            })

        return result

    def create_team_activity(
        self,
        user_id: int,
        activity_type: ActivityType,
        details: str,
        project_id: Optional[int] = None,
        journal_id: Optional[int] = None,
        target_id: Optional[str] = None,
        target_type: Optional[str] = None,
        assigned_to: Optional[int] = None,
        estimated_completion: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InventoryTeamActivity:
        """Create a new team activity record"""
        activity = InventoryTeamActivity(
            user_id=user_id,
            project_id=project_id,
            journal_entry_id=journal_id,
            activity_type=activity_type.value,
            details=details,
            target_id=target_id,
            target_type=target_type,
            assigned_to=assigned_to,
            estimated_completion=estimated_completion,
            metadata=metadata or {}
        )

        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)

        logger.info(f"Created team activity: {activity_type.value} by user {user_id}")
        return activity

    def update_activity_progress(
        self,
        activity_id: int,
        progress: int,
        status: Optional[str] = None
    ) -> bool:
        """Update progress of an existing activity"""
        activity = self.db.query(InventoryTeamActivity).filter(
            InventoryTeamActivity.id == activity_id
        ).first()

        if not activity:
            return False

        activity.progress = min(100, max(0, progress))
        if status:
            activity.status = status

        if progress >= 100 and status != "paused":
            activity.actual_completion = datetime.now(timezone.utc)
            activity.status = "completed"

        self.db.commit()
        return True

    # ==================== Quick Actions Management ====================

    def get_available_quick_actions(
        self,
        user_id: int,
        inventory_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get quick actions available for the current context"""
        actions = self.db.query(QuickAction).filter(
            QuickAction.is_active == True
        ).order_by(QuickAction.display_order).all()

        available_actions = []
        for action in actions:
            if self._is_action_available(action, inventory_context):
                available_actions.append({
                    "id": action.action_id,
                    "title": action.title,
                    "description": action.description,
                    "icon": action.icon,
                    "action_type": action.action_type,
                    "target_route": action.target_route,
                    "api_endpoint": action.api_endpoint,
                    "parameters": action.parameters or {}
                })

        return available_actions

    def _is_action_available(self, action: QuickAction, context: Dict[str, Any]) -> bool:
        """Check if a quick action should be available in the current context"""
        # If action doesn't require context, it's always available
        if not action.requires_context:
            return True

        # Check conditions if they exist
        if action.conditions:
            return self._evaluate_action_conditions(action.conditions, context)

        return True

    def _evaluate_action_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate conditional logic for action availability"""
        inventory_state = context.get("inventory_state", {})

        # Check various conditions
        for condition, expected_value in conditions.items():
            if condition == "has_content" and inventory_state.get("has_content") != expected_value:
                return False
            elif condition == "content_type" and inventory_state.get("content_type") != expected_value:
                return False
            elif condition == "has_gaps" and expected_value and not inventory_state.get("gaps"):
                return False
            elif condition == "gap_contains" and expected_value not in inventory_state.get("gaps", []):
                return False

        return True

    # ==================== Contextual Suggestions ====================

    def _generate_contextual_suggestions(
        self,
        inventory_analysis: Dict[str, Any],
        team_activity: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered suggestions based on current context"""
        suggestions = []
        inventory_state = inventory_analysis.get("inventory_state", {})
        gaps = inventory_state.get("gaps", [])

        # Generate suggestions based on gaps
        for gap in gaps:
            suggestion = self._create_gap_suggestion(gap, inventory_state)
            if suggestion:
                suggestions.append(suggestion)

        # Generate suggestions based on team activity
        if team_activity:
            suggestions.append({
                "type": "team_collaboration",
                "title": "Join Active Work",
                "description": f"Team members are currently working on {len(team_activity)} items",
                "action_text": "View Activity",
                "priority": "medium",
                "data": {"activity_count": len(team_activity)}
            })

        # Generate enhancement suggestions
        if inventory_state.get("has_content"):
            content_quality = inventory_state.get("content_quality", "")
            if content_quality in ["minimal", "basic"]:
                suggestions.append({
                    "type": "content_enhancement",
                    "title": "Enhance Your Content",
                    "description": "Add more detail, images, or structure to improve quality",
                    "action_text": "Enhance Now",
                    "priority": "low",
                    "data": {"current_quality": content_quality}
                })

        return suggestions

    def _create_gap_suggestion(self, gap: str, inventory_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a suggestion for a specific content gap"""
        gap_suggestions = {
            "no_journal": {
                "type": "content_creation",
                "title": "Start Your First Journal",
                "description": "Create your first AI-generated journal entry",
                "action_text": "Create Journal",
                "priority": "high"
            },
            "no_entries": {
                "type": "content_creation",
                "title": "Add Journal Entries",
                "description": "Start building your journal collection",
                "action_text": "Add Entry",
                "priority": "high"
            },
            "no_projects": {
                "type": "project_creation",
                "title": "Create a Project",
                "description": "Organize your journals into themed projects",
                "action_text": "Create Project",
                "priority": "medium"
            },
            "missing_title": {
                "type": "content_editing",
                "title": "Add a Compelling Title",
                "description": "Make your content more discoverable with a great title",
                "action_text": "Add Title",
                "priority": "medium"
            },
            "missing_content": {
                "type": "content_creation",
                "title": "Generate Content",
                "description": "Use AI to generate engaging journal content",
                "action_text": "Generate Content",
                "priority": "high"
            },
            "missing_cover": {
                "type": "media_creation",
                "title": "Add a Cover Image",
                "description": "Make your journal visually appealing with AI-generated art",
                "action_text": "Generate Cover",
                "priority": "low"
            },
            "missing_tags": {
                "type": "metadata_editing",
                "title": "Add Tags",
                "description": "Help organize and categorize your content",
                "action_text": "Add Tags",
                "priority": "low"
            }
        }

        return gap_suggestions.get(gap)

    # ==================== Generation Context Management ====================

    def create_generation_context(
        self,
        user_id: int,
        context_type: str,
        title: str,
        context_data: Dict[str, Any],
        project_id: Optional[int] = None,
        journal_id: Optional[int] = None,
        suggestions: Optional[List[Dict[str, Any]]] = None
    ) -> InventoryGenerationContext:
        """Create a new generation context record"""
        generation_context = InventoryGenerationContext(
            user_id=user_id,
            project_id=project_id,
            journal_entry_id=journal_id,
            context_type=context_type,
            title=title,
            context_data=context_data,
            suggestions=suggestions or [],
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

        self.db.add(generation_context)
        self.db.commit()
        self.db.refresh(generation_context)

        return generation_context

    def get_active_generation_contexts(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[InventoryGenerationContext]:
        """Get active generation contexts for a user"""
        return self.db.query(InventoryGenerationContext).filter(
            InventoryGenerationContext.user_id == user_id,
            InventoryGenerationContext.status == "pending",
            or_(
                InventoryGenerationContext.expires_at.is_(None),
                InventoryGenerationContext.expires_at > datetime.now(timezone.utc)
            )
        ).order_by(desc(InventoryGenerationContext.created_at)).limit(limit).all()

    def accept_generation_context(
        self,
        context_id: int,
        user_id: int
    ) -> bool:
        """Accept a generation context and mark it as accepted"""
        context = self.db.query(InventoryGenerationContext).filter(
            InventoryGenerationContext.id == context_id,
            InventoryGenerationContext.user_id == user_id,
            InventoryGenerationContext.status == "pending"
        ).first()

        if not context or context.is_expired():
            return False

        context.status = "accepted"
        context.accepted_by = user_id
        context.accepted_at = datetime.now(timezone.utc)

        self.db.commit()
        return True

    # ==================== Analytics ====================

    def get_user_engagement_metrics(self, user_id: int) -> Dict[str, Any]:
        """Get engagement metrics for a user"""
        # Recent activity count
        recent_activity = self.db.query(func.count(InventoryTeamActivity.id)).filter(
            InventoryTeamActivity.user_id == user_id,
            InventoryTeamActivity.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
        ).scalar()

        # Team activity involving user
        team_activity = self.db.query(func.count(InventoryTeamActivity.id)).filter(
            or_(
                InventoryTeamActivity.user_id == user_id,
                InventoryTeamActivity.assigned_to == user_id
            ),
            InventoryTeamActivity.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
        ).scalar()

        # Generation contexts created/accepted
        contexts_created = self.db.query(func.count(InventoryGenerationContext.id)).filter(
            InventoryGenerationContext.user_id == user_id,
            InventoryGenerationContext.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
        ).scalar()

        contexts_accepted = self.db.query(func.count(InventoryGenerationContext.id)).filter(
            InventoryGenerationContext.accepted_by == user_id,
            InventoryGenerationContext.accepted_at >= datetime.now(timezone.utc) - timedelta(days=30)
        ).scalar()

        return {
            "recent_activity_count": recent_activity,
            "team_activity_count": team_activity,
            "contexts_created_count": contexts_created,
            "contexts_accepted_count": contexts_accepted,
            "acceptance_rate": (contexts_accepted / contexts_created * 100) if contexts_created > 0 else 0,
            "engagement_level": self._calculate_engagement_level(recent_activity, team_activity)
        }

    def _calculate_engagement_level(self, recent_activity: int, team_activity: int) -> str:
        """Calculate overall engagement level"""
        total_activity = recent_activity + team_activity

        if total_activity == 0:
            return "inactive"
        elif total_activity < 5:
            return "low"
        elif total_activity < 15:
            return "moderate"
        elif total_activity < 30:
            return "active"
        else:
            return "highly_active"