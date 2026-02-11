"""
Social Features and Sharing

Enable social features like sharing, following, and activity feeds.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ActivityType(str, Enum):
    """Activity types for feed."""
    TODO_CREATE = "todo_create"
    TODO_COMPLETE = "todo_complete"
    TODO_SHARE = "todo_share"
    USER_FOLLOW = "user_follow"
    COMMENT = "comment"
    LIKE = "like"


class Activity:
    """User activity."""

    def __init__(
        self,
        activity_type: ActivityType,
        user_id: int,
        data: Dict[str, Any],
        visibility: str = "public"
    ):
        """Initialize activity."""
        self.activity_type = activity_type
        self.user_id = user_id
        self.data = data
        self.visibility = visibility
        self.timestamp = datetime.utcnow()
        self.likes: Set[int] = set()
        self.comments: List[Dict[str, Any]] = []

    def add_like(self, user_id: int):
        """Add like to activity."""
        self.likes.add(user_id)

    def remove_like(self, user_id: int):
        """Remove like from activity."""
        self.likes.discard(user_id)

    def add_comment(self, user_id: int, text: str):
        """Add comment to activity."""
        comment = {
            "user_id": user_id,
            "text": text,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.comments.append(comment)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "activity_type": self.activity_type.value,
            "user_id": self.user_id,
            "data": self.data,
            "visibility": self.visibility,
            "timestamp": self.timestamp.isoformat(),
            "likes": len(self.likes),
            "comments": len(self.comments)
        }


class SocialGraph:
    """Manage user relationships."""

    def __init__(self):
        """Initialize social graph."""
        self.followers: Dict[int, Set[int]] = {}
        self.following: Dict[int, Set[int]] = {}

    def follow(self, follower_id: int, followee_id: int):
        """User follows another user."""
        if follower_id == followee_id:
            raise ValueError("Cannot follow yourself")

        if follower_id not in self.following:
            self.following[follower_id] = set()
        self.following[follower_id].add(followee_id)

        if followee_id not in self.followers:
            self.followers[followee_id] = set()
        self.followers[followee_id].add(follower_id)

        logger.info(f"User {follower_id} followed user {followee_id}")

    def unfollow(self, follower_id: int, followee_id: int):
        """User unfollows another user."""
        if follower_id in self.following:
            self.following[follower_id].discard(followee_id)

        if followee_id in self.followers:
            self.followers[followee_id].discard(follower_id)

        logger.info(f"User {follower_id} unfollowed user {followee_id}")

    def get_followers(self, user_id: int) -> List[int]:
        """Get user's followers."""
        return list(self.followers.get(user_id, set()))

    def get_following(self, user_id: int) -> List[int]:
        """Get users that user is following."""
        return list(self.following.get(user_id, set()))

    def is_following(self, follower_id: int, followee_id: int) -> bool:
        """Check if user is following another user."""
        return followee_id in self.following.get(follower_id, set())

    def get_follower_count(self, user_id: int) -> int:
        """Get follower count."""
        return len(self.followers.get(user_id, set()))

    def get_following_count(self, user_id: int) -> int:
        """Get following count."""
        return len(self.following.get(user_id, set()))


class ActivityFeed:
    """Manage activity feed."""

    def __init__(self):
        """Initialize activity feed."""
        self.activities: List[Activity] = []
        self.user_activities: Dict[int, List[Activity]] = {}

    def post_activity(self, activity: Activity):
        """Post activity to feed."""
        self.activities.append(activity)

        if activity.user_id not in self.user_activities:
            self.user_activities[activity.user_id] = []
        self.user_activities[activity.user_id].append(activity)

        logger.info(
            f"Posted activity: {activity.activity_type.value}",
            extra={"user_id": activity.user_id, "type": activity.activity_type.value}
        )

    def get_user_feed(
        self,
        user_id: int,
        following: List[int],
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get personalized feed for user."""
        # Get activities from followed users
        feed_activities = []

        for activity in reversed(self.activities):
            if activity.user_id in following or activity.user_id == user_id:
                if activity.visibility == "public":
                    feed_activities.append(activity)

            if len(feed_activities) >= limit:
                break

        return [a.to_dict() for a in feed_activities]

    def get_user_activities(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get activities for specific user."""
        activities = self.user_activities.get(user_id, [])
        return [a.to_dict() for a in reversed(activities[-limit:])]


class ShareManager:
    """Manage todo sharing."""

    def __init__(self):
        """Initialize share manager."""
        self.shares: Dict[str, Dict[str, Any]] = {}

    def create_share_link(
        self,
        todo_id: int,
        user_id: int,
        permissions: List[str],
        expires_hours: Optional[int] = None
    ) -> str:
        """Create share link for todo."""
        import secrets
        share_token = secrets.token_urlsafe(32)

        expires_at = None
        if expires_hours:
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

        self.shares[share_token] = {
            "todo_id": todo_id,
            "user_id": user_id,
            "permissions": permissions,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "access_count": 0
        }

        logger.info(
            f"Created share link for todo {todo_id}",
            extra={"todo_id": todo_id, "user_id": user_id}
        )

        return share_token

    def verify_share_link(self, share_token: str) -> Optional[Dict[str, Any]]:
        """Verify share link."""
        if share_token not in self.shares:
            return None

        share = self.shares[share_token]

        # Check expiry
        if share["expires_at"] and datetime.utcnow() > share["expires_at"]:
            del self.shares[share_token]
            return None

        # Increment access count
        share["access_count"] += 1

        return share

    def revoke_share_link(self, share_token: str):
        """Revoke share link."""
        if share_token in self.shares:
            del self.shares[share_token]
            logger.info(f"Revoked share link: {share_token}")


class CommentSystem:
    """Manage comments on todos."""

    def __init__(self):
        """Initialize comment system."""
        self.comments: Dict[int, List[Dict[str, Any]]] = {}

    def add_comment(
        self,
        todo_id: int,
        user_id: int,
        text: str,
        parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add comment to todo."""
        if todo_id not in self.comments:
            self.comments[todo_id] = []

        comment = {
            "id": len(self.comments[todo_id]) + 1,
            "user_id": user_id,
            "text": text,
            "parent_id": parent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "likes": 0
        }

        self.comments[todo_id].append(comment)

        logger.info(
            f"Added comment to todo {todo_id}",
            extra={"todo_id": todo_id, "user_id": user_id}
        )

        return comment

    def get_comments(self, todo_id: int) -> List[Dict[str, Any]]:
        """Get comments for todo."""
        return self.comments.get(todo_id, [])

    def delete_comment(self, todo_id: int, comment_id: int):
        """Delete comment."""
        if todo_id in self.comments:
            self.comments[todo_id] = [
                c for c in self.comments[todo_id]
                if c["id"] != comment_id
            ]


class LikeSystem:
    """Manage likes on todos and activities."""

    def __init__(self):
        """Initialize like system."""
        self.likes: Dict[str, Set[int]] = {}

    def add_like(self, item_type: str, item_id: int, user_id: int):
        """Add like."""
        key = f"{item_type}:{item_id}"

        if key not in self.likes:
            self.likes[key] = set()

        self.likes[key].add(user_id)

        logger.info(
            f"User {user_id} liked {item_type} {item_id}",
            extra={"item_type": item_type, "item_id": item_id, "user_id": user_id}
        )

    def remove_like(self, item_type: str, item_id: int, user_id: int):
        """Remove like."""
        key = f"{item_type}:{item_id}"

        if key in self.likes:
            self.likes[key].discard(user_id)

    def get_like_count(self, item_type: str, item_id: int) -> int:
        """Get like count."""
        key = f"{item_type}:{item_id}"
        return len(self.likes.get(key, set()))

    def has_liked(self, item_type: str, item_id: int, user_id: int) -> bool:
        """Check if user has liked item."""
        key = f"{item_type}:{item_id}"
        return user_id in self.likes.get(key, set())


class NotificationPreferences:
    """Manage user notification preferences."""

    def __init__(self):
        """Initialize notification preferences."""
        self.preferences: Dict[int, Dict[str, bool]] = {}

    def set_preference(self, user_id: int, notification_type: str, enabled: bool):
        """Set notification preference."""
        if user_id not in self.preferences:
            self.preferences[user_id] = {}

        self.preferences[user_id][notification_type] = enabled

    def get_preference(self, user_id: int, notification_type: str) -> bool:
        """Get notification preference."""
        if user_id not in self.preferences:
            return True  # Default to enabled

        return self.preferences[user_id].get(notification_type, True)

    def get_all_preferences(self, user_id: int) -> Dict[str, bool]:
        """Get all preferences for user."""
        return self.preferences.get(user_id, {})


# Global instances
social_graph = SocialGraph()
activity_feed = ActivityFeed()
share_manager = ShareManager()
comment_system = CommentSystem()
like_system = LikeSystem()
notification_preferences = NotificationPreferences()


# Helper functions
def follow_user(follower_id: int, followee_id: int):
    """Follow user."""
    social_graph.follow(follower_id, followee_id)

    # Post activity
    activity = Activity(
        ActivityType.USER_FOLLOW,
        follower_id,
        {"followee_id": followee_id}
    )
    activity_feed.post_activity(activity)


def share_todo(todo_id: int, user_id: int, permissions: List[str]) -> str:
    """Share todo."""
    share_token = share_manager.create_share_link(todo_id, user_id, permissions)

    # Post activity
    activity = Activity(
        ActivityType.TODO_SHARE,
        user_id,
        {"todo_id": todo_id}
    )
    activity_feed.post_activity(activity)

    return share_token


def add_todo_comment(todo_id: int, user_id: int, text: str) -> Dict[str, Any]:
    """Add comment to todo."""
    comment = comment_system.add_comment(todo_id, user_id, text)

    # Post activity
    activity = Activity(
        ActivityType.COMMENT,
        user_id,
        {"todo_id": todo_id, "comment": text}
    )
    activity_feed.post_activity(activity)

    return comment


def like_todo(todo_id: int, user_id: int):
    """Like todo."""
    like_system.add_like("todo", todo_id, user_id)

    # Post activity
    activity = Activity(
        ActivityType.LIKE,
        user_id,
        {"todo_id": todo_id}
    )
    activity_feed.post_activity(activity)
