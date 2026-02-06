"""Data models for chat feature.

This module defines the data structures for conversation management,
including sessions, messages, context, and confirmation tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class MessageMetadata:
    """Additional context for a message."""
    message_type: Optional[str] = None  # text, todo_display, confirmation_request, error
    referenced_todos: List[int] = field(default_factory=list)
    function_call: Optional[Dict] = None
    tokens_used: Optional[int] = None


@dataclass
class ChatMessage:
    """Individual message in a conversation."""
    message_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[MessageMetadata] = None

    @classmethod
    def create(cls, role: str, content: str, metadata: Optional[MessageMetadata] = None):
        """Create a new chat message with generated ID and timestamp."""
        return cls(
            message_id=str(uuid4()),
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )


@dataclass
class TodoReference:
    """Cached todo information for context resolution."""
    todo_id: int
    title: str
    completed: bool
    last_mentioned_at: datetime


@dataclass
class PendingConfirmation:
    """Tracks destructive operations awaiting user confirmation."""
    operation: str  # delete, bulk_delete, bulk_update
    target_todo_ids: List[int]
    created_at: datetime
    expires_at: datetime
    operation_details: Optional[Dict] = None

    def is_expired(self) -> bool:
        """Check if confirmation has expired."""
        return datetime.utcnow() > self.expires_at


@dataclass
class ConversationContext:
    """Maintains state and references within conversation."""
    referenced_todos: Dict[int, TodoReference] = field(default_factory=dict)
    last_query_results: Optional[List[int]] = None
    pending_confirmation: Optional[PendingConfirmation] = None
    user_preferences: Dict = field(default_factory=dict)

    def add_todo_reference(self, todo_id: int, title: str, completed: bool):
        """Add or update a todo reference in context."""
        self.referenced_todos[todo_id] = TodoReference(
            todo_id=todo_id,
            title=title,
            completed=completed,
            last_mentioned_at=datetime.utcnow()
        )

    def get_todo_by_position(self, position: int) -> Optional[int]:
        """Get todo ID by position in last query results (1-indexed)."""
        if not self.last_query_results or position < 1 or position > len(self.last_query_results):
            return None
        return self.last_query_results[position - 1]

    def clear_expired_confirmation(self):
        """Remove pending confirmation if expired."""
        if self.pending_confirmation and self.pending_confirmation.is_expired():
            self.pending_confirmation = None


@dataclass
class ConversationSession:
    """Tracks an ongoing chat interaction for a user."""
    session_id: str
    user_id: int
    created_at: datetime
    last_activity_at: datetime
    message_count: int
    messages: List[ChatMessage]
    context: ConversationContext

    @classmethod
    def create(cls, user_id: int):
        """Create a new conversation session."""
        now = datetime.utcnow()
        return cls(
            session_id=str(uuid4()),
            user_id=user_id,
            created_at=now,
            last_activity_at=now,
            message_count=0,
            messages=[],
            context=ConversationContext()
        )

    def add_message(self, role: str, content: str, metadata: Optional[MessageMetadata] = None):
        """Add a message to the conversation."""
        message = ChatMessage.create(role, content, metadata)
        self.messages.append(message)
        self.message_count += 1
        self.last_activity_at = datetime.utcnow()
        return message

    def get_recent_messages(self, limit: int = 20) -> List[ChatMessage]:
        """Get the most recent messages (sliding window)."""
        return self.messages[-limit:] if len(self.messages) > limit else self.messages

    def get_message_history(self, limit: int = 20) -> List[Dict]:
        """Get message history formatted for LLM API.

        Returns messages in the format expected by OpenAI API:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        recent_messages = self.get_recent_messages(limit)
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in recent_messages
        ]

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired due to inactivity."""
        from datetime import timedelta
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - self.last_activity_at > timeout

    def to_dict(self) -> Dict:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity_at": self.last_activity_at.isoformat(),
            "message_count": self.message_count,
            "messages": [
                {
                    "message_id": msg.message_id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata.__dict__ if msg.metadata else None
                }
                for msg in self.messages
            ]
        }
