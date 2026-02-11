"""
User Analytics and Behavior Tracking

Track user behavior, engagement, and analytics events.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Analytics event types."""
    PAGE_VIEW = "page_view"
    BUTTON_CLICK = "button_click"
    FORM_SUBMIT = "form_submit"
    TODO_CREATE = "todo_create"
    TODO_UPDATE = "todo_update"
    TODO_DELETE = "todo_delete"
    TODO_COMPLETE = "todo_complete"
    SEARCH = "search"
    FILTER = "filter"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    SIGNUP = "signup"
    ERROR = "error"


class AnalyticsEvent:
    """Analytics event."""

    def __init__(
        self,
        event_type: EventType,
        user_id: Optional[int],
        properties: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """Initialize analytics event."""
        self.event_type = event_type
        self.user_id = user_id
        self.properties = properties or {}
        self.session_id = session_id
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "properties": self.properties,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat()
        }


class UserSession:
    """User session tracking."""

    def __init__(self, session_id: str, user_id: Optional[int]):
        """Initialize user session."""
        self.session_id = session_id
        self.user_id = user_id
        self.started_at = datetime.utcnow()
        self.last_activity = self.started_at
        self.events: List[AnalyticsEvent] = []
        self.page_views = 0
        self.actions = 0

    def record_event(self, event: AnalyticsEvent):
        """Record event in session."""
        self.events.append(event)
        self.last_activity = datetime.utcnow()

        if event.event_type == EventType.PAGE_VIEW:
            self.page_views += 1
        else:
            self.actions += 1

    def get_duration(self) -> timedelta:
        """Get session duration."""
        return self.last_activity - self.started_at

    def is_active(self, timeout_minutes: int = 30) -> bool:
        """Check if session is active."""
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - self.last_activity < timeout

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "started_at": self.started_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "duration_seconds": self.get_duration().total_seconds(),
            "page_views": self.page_views,
            "actions": self.actions,
            "events": len(self.events)
        }


class UserBehavior:
    """User behavior profile."""

    def __init__(self, user_id: int):
        """Initialize user behavior."""
        self.user_id = user_id
        self.first_seen = datetime.utcnow()
        self.last_seen = self.first_seen
        self.total_sessions = 0
        self.total_events = 0
        self.event_counts: Dict[str, int] = defaultdict(int)
        self.feature_usage: Dict[str, int] = defaultdict(int)

    def record_event(self, event: AnalyticsEvent):
        """Record event."""
        self.last_seen = datetime.utcnow()
        self.total_events += 1
        self.event_counts[event.event_type.value] += 1

        # Track feature usage
        if "feature" in event.properties:
            self.feature_usage[event.properties["feature"]] += 1

    def get_engagement_score(self) -> float:
        """Calculate engagement score (0-100)."""
        # Simple engagement scoring
        score = 0.0

        # Sessions (max 30 points)
        score += min(self.total_sessions * 2, 30)

        # Events (max 40 points)
        score += min(self.total_events * 0.5, 40)

        # Feature diversity (max 30 points)
        unique_features = len(self.feature_usage)
        score += min(unique_features * 5, 30)

        return min(score, 100.0)

    def get_most_used_features(self, limit: int = 5) -> List[tuple[str, int]]:
        """Get most used features."""
        return sorted(
            self.feature_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "total_sessions": self.total_sessions,
            "total_events": self.total_events,
            "engagement_score": self.get_engagement_score(),
            "event_counts": dict(self.event_counts),
            "top_features": self.get_most_used_features()
        }


class AnalyticsTracker:
    """Track analytics events."""

    def __init__(self):
        """Initialize analytics tracker."""
        self.events: List[AnalyticsEvent] = []
        self.sessions: Dict[str, UserSession] = {}
        self.user_behaviors: Dict[int, UserBehavior] = {}

    def track(
        self,
        event_type: EventType,
        user_id: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """Track event."""
        event = AnalyticsEvent(event_type, user_id, properties, session_id)
        self.events.append(event)

        # Update session
        if session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = UserSession(session_id, user_id)
            self.sessions[session_id].record_event(event)

        # Update user behavior
        if user_id:
            if user_id not in self.user_behaviors:
                self.user_behaviors[user_id] = UserBehavior(user_id)
            self.user_behaviors[user_id].record_event(event)

        logger.info(
            f"Tracked event: {event_type.value}",
            extra={
                "event_type": event_type.value,
                "user_id": user_id,
                "session_id": session_id
            }
        )

    def get_user_behavior(self, user_id: int) -> Optional[UserBehavior]:
        """Get user behavior."""
        return self.user_behaviors.get(user_id)

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session."""
        return self.sessions.get(session_id)

    def get_active_sessions(self) -> List[UserSession]:
        """Get active sessions."""
        return [s for s in self.sessions.values() if s.is_active()]

    def get_event_counts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get event counts."""
        counts: Dict[str, int] = defaultdict(int)

        for event in self.events:
            if start_date and event.timestamp < start_date:
                continue
            if end_date and event.timestamp > end_date:
                continue

            counts[event.event_type.value] += 1

        return dict(counts)

    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most engaged users."""
        users = sorted(
            self.user_behaviors.values(),
            key=lambda u: u.get_engagement_score(),
            reverse=True
        )[:limit]

        return [u.to_dict() for u in users]

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        return {
            "total_events": len(self.events),
            "total_sessions": len(self.sessions),
            "active_sessions": len(self.get_active_sessions()),
            "total_users": len(self.user_behaviors),
            "event_counts": self.get_event_counts(),
            "top_users": self.get_top_users(5)
        }


class FunnelAnalyzer:
    """Analyze conversion funnels."""

    def __init__(self, steps: List[EventType]):
        """Initialize funnel analyzer."""
        self.steps = steps
        self.funnel_data: Dict[int, List[EventType]] = defaultdict(list)

    def track_user_event(self, user_id: int, event_type: EventType):
        """Track user event in funnel."""
        if event_type in self.steps:
            self.funnel_data[user_id].append(event_type)

    def get_funnel_stats(self) -> Dict[str, Any]:
        """Get funnel statistics."""
        step_counts = {step.value: 0 for step in self.steps}
        completed_users = 0

        for user_events in self.funnel_data.values():
            # Track which steps user completed
            for i, step in enumerate(self.steps):
                if step in user_events:
                    step_counts[step.value] += 1

            # Check if user completed all steps
            if all(step in user_events for step in self.steps):
                completed_users += 1

        total_users = len(self.funnel_data)

        return {
            "total_users": total_users,
            "completed_users": completed_users,
            "completion_rate": completed_users / total_users if total_users > 0 else 0,
            "step_counts": step_counts,
            "drop_off_rates": self._calculate_drop_off_rates(step_counts, total_users)
        }

    def _calculate_drop_off_rates(
        self,
        step_counts: Dict[str, int],
        total_users: int
    ) -> Dict[str, float]:
        """Calculate drop-off rates."""
        drop_off = {}
        prev_count = total_users

        for step in self.steps:
            current_count = step_counts[step.value]
            if prev_count > 0:
                drop_off[step.value] = 1 - (current_count / prev_count)
            else:
                drop_off[step.value] = 0.0
            prev_count = current_count

        return drop_off


# Global analytics tracker
analytics_tracker = AnalyticsTracker()


# Helper functions
def track_event(
    event_type: EventType,
    user_id: Optional[int] = None,
    properties: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
):
    """Track analytics event."""
    analytics_tracker.track(event_type, user_id, properties, session_id)


def track_page_view(
    page: str,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None
):
    """Track page view."""
    track_event(
        EventType.PAGE_VIEW,
        user_id,
        {"page": page},
        session_id
    )


def track_action(
    action: str,
    user_id: Optional[int] = None,
    properties: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
):
    """Track user action."""
    props = properties or {}
    props["action"] = action

    track_event(
        EventType.BUTTON_CLICK,
        user_id,
        props,
        session_id
    )
