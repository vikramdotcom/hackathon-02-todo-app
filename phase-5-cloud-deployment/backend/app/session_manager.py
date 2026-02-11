"""
Session Management System

Manage user sessions with Redis backend.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class Session:
    """User session."""

    def __init__(
        self,
        session_id: str,
        user_id: int,
        data: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ):
        """Initialize session."""
        self.session_id = session_id
        self.user_id = user_id
        self.data = data or {}
        self.created_at = datetime.utcnow()
        self.expires_at = expires_at or (self.created_at + timedelta(hours=24))
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    def refresh(self, hours: int = 24):
        """Refresh session expiry."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_accessed = datetime.utcnow()

    def set(self, key: str, value: Any):
        """Set session data."""
        self.data[key] = value
        self.last_accessed = datetime.utcnow()

    def get(self, key: str, default: Any = None) -> Any:
        """Get session data."""
        self.last_accessed = datetime.utcnow()
        return self.data.get(key, default)

    def delete(self, key: str):
        """Delete session data."""
        if key in self.data:
            del self.data[key]
        self.last_accessed = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create from dictionary."""
        session = cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            data=data.get("data", {}),
            expires_at=datetime.fromisoformat(data["expires_at"])
        )
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_accessed = datetime.fromisoformat(data["last_accessed"])
        return session


class SessionManager:
    """Manage user sessions."""

    def __init__(self, redis_client=None):
        """Initialize session manager."""
        self.redis = redis_client
        self.sessions: Dict[str, Session] = {}  # In-memory fallback

    def generate_session_id(self) -> str:
        """Generate unique session ID."""
        return str(uuid.uuid4())

    def generate_token(self, session_id: str, secret: str) -> str:
        """Generate session token."""
        data = f"{session_id}:{secret}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def create_session(
        self,
        user_id: int,
        data: Optional[Dict[str, Any]] = None,
        expires_hours: int = 24
    ) -> Session:
        """Create new session."""
        session_id = self.generate_session_id()
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

        session = Session(
            session_id=session_id,
            user_id=user_id,
            data=data,
            expires_at=expires_at
        )

        await self._save_session(session)

        logger.info(
            f"Created session for user {user_id}",
            extra={"user_id": user_id, "session_id": session_id}
        )

        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session = await self._load_session(session_id)

        if not session:
            return None

        if session.is_expired():
            await self.delete_session(session_id)
            return None

        return session

    async def update_session(self, session: Session):
        """Update session."""
        await self._save_session(session)

    async def delete_session(self, session_id: str):
        """Delete session."""
        if self.redis:
            try:
                await self.redis.delete(f"session:{session_id}")
            except Exception as e:
                logger.error(f"Error deleting session from Redis: {e}")

        if session_id in self.sessions:
            del self.sessions[session_id]

        logger.info(f"Deleted session {session_id}")

    async def delete_user_sessions(self, user_id: int):
        """Delete all sessions for user."""
        # In-memory
        to_delete = [
            sid for sid, session in self.sessions.items()
            if session.user_id == user_id
        ]

        for session_id in to_delete:
            await self.delete_session(session_id)

        logger.info(f"Deleted all sessions for user {user_id}")

    async def cleanup_expired(self):
        """Cleanup expired sessions."""
        expired = []

        for session_id, session in self.sessions.items():
            if session.is_expired():
                expired.append(session_id)

        for session_id in expired:
            await self.delete_session(session_id)

        logger.info(f"Cleaned up {len(expired)} expired sessions")

    async def _save_session(self, session: Session):
        """Save session to storage."""
        if self.redis:
            try:
                key = f"session:{session.session_id}"
                value = json.dumps(session.to_dict())
                ttl = int((session.expires_at - datetime.utcnow()).total_seconds())

                await self.redis.setex(key, ttl, value)
            except Exception as e:
                logger.error(f"Error saving session to Redis: {e}")

        # Also save in memory as fallback
        self.sessions[session.session_id] = session

    async def _load_session(self, session_id: str) -> Optional[Session]:
        """Load session from storage."""
        if self.redis:
            try:
                key = f"session:{session_id}"
                value = await self.redis.get(key)

                if value:
                    data = json.loads(value)
                    return Session.from_dict(data)
            except Exception as e:
                logger.error(f"Error loading session from Redis: {e}")

        # Fallback to in-memory
        return self.sessions.get(session_id)

    async def get_active_sessions_count(self, user_id: Optional[int] = None) -> int:
        """Get count of active sessions."""
        count = 0

        for session in self.sessions.values():
            if not session.is_expired():
                if user_id is None or session.user_id == user_id:
                    count += 1

        return count


# Global session manager
session_manager = SessionManager()


# Middleware helper
async def get_session_from_request(request) -> Optional[Session]:
    """Get session from request."""
    # Try to get session ID from cookie
    session_id = request.cookies.get("session_id")

    if not session_id:
        # Try to get from header
        session_id = request.headers.get("X-Session-ID")

    if not session_id:
        return None

    return await session_manager.get_session(session_id)


async def require_session(request) -> Session:
    """Require valid session."""
    session = await get_session_from_request(request)

    if not session:
        raise ValueError("No valid session")

    return session
