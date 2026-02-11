"""
Real-time Collaboration System

Enable real-time collaboration features with WebSocket support.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types."""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    TODO_UPDATE = "todo_update"
    TODO_CREATE = "todo_create"
    TODO_DELETE = "todo_delete"
    USER_TYPING = "user_typing"
    USER_PRESENCE = "user_presence"
    CURSOR_MOVE = "cursor_move"
    COMMENT = "comment"
    NOTIFICATION = "notification"


class UserPresence(str, Enum):
    """User presence status."""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


class CollaborationMessage:
    """Real-time collaboration message."""

    def __init__(
        self,
        message_type: MessageType,
        user_id: int,
        data: Dict[str, Any],
        room_id: Optional[str] = None
    ):
        """Initialize collaboration message."""
        self.message_type = message_type
        self.user_id = user_id
        self.data = data
        self.room_id = room_id
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.message_type.value,
            "user_id": self.user_id,
            "data": self.data,
            "room_id": self.room_id,
            "timestamp": self.timestamp.isoformat()
        }

    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


class CollaborationRoom:
    """Collaboration room for real-time updates."""

    def __init__(self, room_id: str, name: str):
        """Initialize collaboration room."""
        self.room_id = room_id
        self.name = name
        self.users: Set[int] = set()
        self.created_at = datetime.utcnow()
        self.message_history: List[CollaborationMessage] = []

    def add_user(self, user_id: int):
        """Add user to room."""
        self.users.add(user_id)
        logger.info(f"User {user_id} joined room {self.room_id}")

    def remove_user(self, user_id: int):
        """Remove user from room."""
        self.users.discard(user_id)
        logger.info(f"User {user_id} left room {self.room_id}")

    def broadcast_message(self, message: CollaborationMessage):
        """Broadcast message to all users in room."""
        self.message_history.append(message)
        logger.info(
            f"Broadcasting message in room {self.room_id}",
            extra={
                "room_id": self.room_id,
                "message_type": message.message_type.value,
                "user_count": len(self.users)
            }
        )

    def get_active_users(self) -> List[int]:
        """Get active users in room."""
        return list(self.users)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "user_count": len(self.users),
            "created_at": self.created_at.isoformat()
        }


class PresenceManager:
    """Manage user presence status."""

    def __init__(self):
        """Initialize presence manager."""
        self.user_presence: Dict[int, UserPresence] = {}
        self.last_seen: Dict[int, datetime] = {}

    def set_presence(self, user_id: int, status: UserPresence):
        """Set user presence."""
        self.user_presence[user_id] = status
        self.last_seen[user_id] = datetime.utcnow()

        logger.info(
            f"User presence updated: {status.value}",
            extra={"user_id": user_id, "status": status.value}
        )

    def get_presence(self, user_id: int) -> UserPresence:
        """Get user presence."""
        return self.user_presence.get(user_id, UserPresence.OFFLINE)

    def update_activity(self, user_id: int):
        """Update user activity timestamp."""
        self.last_seen[user_id] = datetime.utcnow()

    def get_online_users(self) -> List[int]:
        """Get online users."""
        return [
            user_id for user_id, status in self.user_presence.items()
            if status == UserPresence.ONLINE
        ]

    def cleanup_stale_presence(self, timeout_minutes: int = 5):
        """Cleanup stale presence data."""
        now = datetime.utcnow()
        stale_users = []

        for user_id, last_seen in self.last_seen.items():
            if (now - last_seen).total_seconds() > timeout_minutes * 60:
                stale_users.append(user_id)

        for user_id in stale_users:
            self.user_presence[user_id] = UserPresence.OFFLINE

        if stale_users:
            logger.info(f"Cleaned up {len(stale_users)} stale presence records")


class TypingIndicator:
    """Manage typing indicators."""

    def __init__(self):
        """Initialize typing indicator."""
        self.typing_users: Dict[str, Set[int]] = {}
        self.typing_timestamps: Dict[tuple[str, int], datetime] = {}

    def start_typing(self, room_id: str, user_id: int):
        """User started typing."""
        if room_id not in self.typing_users:
            self.typing_users[room_id] = set()

        self.typing_users[room_id].add(user_id)
        self.typing_timestamps[(room_id, user_id)] = datetime.utcnow()

    def stop_typing(self, room_id: str, user_id: int):
        """User stopped typing."""
        if room_id in self.typing_users:
            self.typing_users[room_id].discard(user_id)

        key = (room_id, user_id)
        if key in self.typing_timestamps:
            del self.typing_timestamps[key]

    def get_typing_users(self, room_id: str) -> List[int]:
        """Get users currently typing in room."""
        return list(self.typing_users.get(room_id, set()))

    def cleanup_stale_typing(self, timeout_seconds: int = 5):
        """Cleanup stale typing indicators."""
        now = datetime.utcnow()
        stale_keys = []

        for key, timestamp in self.typing_timestamps.items():
            if (now - timestamp).total_seconds() > timeout_seconds:
                stale_keys.append(key)

        for room_id, user_id in stale_keys:
            self.stop_typing(room_id, user_id)


class CollaborationManager:
    """Manage real-time collaboration."""

    def __init__(self):
        """Initialize collaboration manager."""
        self.rooms: Dict[str, CollaborationRoom] = {}
        self.user_connections: Dict[int, Set[str]] = {}
        self.presence_manager = PresenceManager()
        self.typing_indicator = TypingIndicator()

    def create_room(self, room_id: str, name: str) -> CollaborationRoom:
        """Create collaboration room."""
        room = CollaborationRoom(room_id, name)
        self.rooms[room_id] = room

        logger.info(f"Created collaboration room: {room_id}")
        return room

    def get_room(self, room_id: str) -> Optional[CollaborationRoom]:
        """Get collaboration room."""
        return self.rooms.get(room_id)

    def join_room(self, room_id: str, user_id: int):
        """User joins room."""
        if room_id not in self.rooms:
            self.create_room(room_id, f"Room {room_id}")

        room = self.rooms[room_id]
        room.add_user(user_id)

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(room_id)

        # Update presence
        self.presence_manager.set_presence(user_id, UserPresence.ONLINE)

        # Broadcast join message
        message = CollaborationMessage(
            MessageType.USER_PRESENCE,
            user_id,
            {"status": "joined"},
            room_id
        )
        room.broadcast_message(message)

    def leave_room(self, room_id: str, user_id: int):
        """User leaves room."""
        if room_id in self.rooms:
            room = self.rooms[room_id]
            room.remove_user(user_id)

            # Update user connections
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(room_id)

            # Broadcast leave message
            message = CollaborationMessage(
                MessageType.USER_PRESENCE,
                user_id,
                {"status": "left"},
                room_id
            )
            room.broadcast_message(message)

    def broadcast_to_room(
        self,
        room_id: str,
        message_type: MessageType,
        user_id: int,
        data: Dict[str, Any]
    ):
        """Broadcast message to room."""
        if room_id in self.rooms:
            message = CollaborationMessage(message_type, user_id, data, room_id)
            self.rooms[room_id].broadcast_message(message)

    def notify_todo_update(
        self,
        room_id: str,
        user_id: int,
        todo_id: int,
        changes: Dict[str, Any]
    ):
        """Notify room of todo update."""
        self.broadcast_to_room(
            room_id,
            MessageType.TODO_UPDATE,
            user_id,
            {"todo_id": todo_id, "changes": changes}
        )

    def notify_todo_create(
        self,
        room_id: str,
        user_id: int,
        todo_data: Dict[str, Any]
    ):
        """Notify room of todo creation."""
        self.broadcast_to_room(
            room_id,
            MessageType.TODO_CREATE,
            user_id,
            {"todo": todo_data}
        )

    def notify_todo_delete(
        self,
        room_id: str,
        user_id: int,
        todo_id: int
    ):
        """Notify room of todo deletion."""
        self.broadcast_to_room(
            room_id,
            MessageType.TODO_DELETE,
            user_id,
            {"todo_id": todo_id}
        )

    def set_user_typing(self, room_id: str, user_id: int, is_typing: bool):
        """Set user typing status."""
        if is_typing:
            self.typing_indicator.start_typing(room_id, user_id)
        else:
            self.typing_indicator.stop_typing(room_id, user_id)

        # Broadcast typing status
        self.broadcast_to_room(
            room_id,
            MessageType.USER_TYPING,
            user_id,
            {"is_typing": is_typing}
        )

    def get_room_state(self, room_id: str) -> Optional[Dict[str, Any]]:
        """Get current room state."""
        room = self.rooms.get(room_id)
        if not room:
            return None

        return {
            "room": room.to_dict(),
            "active_users": room.get_active_users(),
            "typing_users": self.typing_indicator.get_typing_users(room_id)
        }

    def cleanup(self):
        """Cleanup stale data."""
        self.presence_manager.cleanup_stale_presence()
        self.typing_indicator.cleanup_stale_typing()


# Global collaboration manager
collaboration_manager = CollaborationManager()


# Helper functions
def create_collaboration_room(room_id: str, name: str) -> CollaborationRoom:
    """Create collaboration room."""
    return collaboration_manager.create_room(room_id, name)


def join_collaboration_room(room_id: str, user_id: int):
    """Join collaboration room."""
    collaboration_manager.join_room(room_id, user_id)


def broadcast_todo_update(
    room_id: str,
    user_id: int,
    todo_id: int,
    changes: Dict[str, Any]
):
    """Broadcast todo update."""
    collaboration_manager.notify_todo_update(room_id, user_id, todo_id, changes)
