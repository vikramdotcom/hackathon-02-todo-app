"""Conversation manager for session storage and management."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from app.chat.models.chat_models import ConversationSession, MessageMetadata

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation sessions with in-memory storage."""

    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, ConversationSession] = {}
        self.session_timeout_minutes = session_timeout_minutes
        self._cleanup_task: Optional[asyncio.Task] = None
        logger.info(f'ConversationManager initialized (timeout: {session_timeout_minutes}min)')

    def create_session(self, user_id: int) -> str:
        session = ConversationSession.create(user_id)
        self.sessions[session.session_id] = session
        logger.info(f'Created session {session.session_id} for user {user_id}')
        return session.session_id

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        session = self.sessions.get(session_id)
        if not session:
            return None
        if session.is_expired(self.session_timeout_minutes):
            del self.sessions[session_id]
            return None
        return session

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[MessageMetadata] = None) -> bool:
        session = self.get_session(session_id)
        if not session:
            return False
        session.add_message(role, content, metadata)
        
        # Maintain sliding window: keep last 20 messages (10 pairs)
        max_messages = 20
        if len(session.messages) > max_messages:
            session.messages = session.messages[-max_messages:]
            logger.debug(f'Pruned messages for session {session_id}, kept last {max_messages}')
        
        return True

    def update_context(self, session_id: str, **context_updates) -> bool:
        session = self.get_session(session_id)
        if not session:
            return False
        for key, value in context_updates.items():
            if hasattr(session.context, key):
                setattr(session.context, key, value)
        return True

    def update_session(self, session_id: str, session: ConversationSession) -> bool:
        """Update an existing session in storage.

        Args:
            session_id: Session identifier
            session: Updated session object

        Returns:
            True if session was updated, False if not found
        """
        if session_id not in self.sessions:
            return False
        self.sessions[session_id] = session
        return True

    def clear_expired_confirmations(self) -> int:
        """Clear expired pending confirmations from all sessions.
        
        Returns:
            Number of confirmations cleared
        """
        cleared_count = 0
        for session in self.sessions.values():
            if session.context.pending_confirmation:
                if session.context.pending_confirmation.is_expired():
                    session.context.pending_confirmation = None
                    cleared_count += 1
        
        if cleared_count > 0:
            logger.info(f'Cleared {cleared_count} expired confirmations')
        
        return cleared_count

    def cleanup_expired_sessions(self) -> int:
        expired = [sid for sid, s in self.sessions.items() if s.is_expired(self.session_timeout_minutes)]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            logger.info(f'Cleaned up {len(expired)} expired sessions')
        return len(expired)

    async def start_cleanup_task(self, interval_seconds: int = 300):
        if self._cleanup_task and not self._cleanup_task.done():
            return
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(interval_seconds)
                    self.cleanup_expired_sessions()
                    self.clear_expired_confirmations()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f'Error in cleanup: {e}')
        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def stop_cleanup_task(self):
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    def update_context_with_todos(self, session_id: str, todos: list) -> bool:
        """Update context with query results and todo references."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Store todo IDs in last_query_results
        todo_ids = [todo.get('id') for todo in todos if todo.get('id')]
        session.context.last_query_results = todo_ids
        
        # Add todo references to context
        for todo in todos:
            if todo.get('id'):
                session.context.add_todo_reference(
                    todo_id=todo['id'],
                    title=todo.get('title', ''),
                    completed=todo.get('completed', False)
                )
        
        logger.debug(f'Updated context with {len(todos)} todos for session {session_id}')
        return True


_conversation_manager: Optional[ConversationManager] = None

def init_conversation_manager(session_timeout_minutes: int = 30) -> ConversationManager:
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager(session_timeout_minutes)
    return _conversation_manager

def get_conversation_manager() -> ConversationManager:
    if _conversation_manager is None:
        raise RuntimeError('ConversationManager not initialized')
    return _conversation_manager
