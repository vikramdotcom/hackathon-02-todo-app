"""
Request Replay System

Replay failed requests with exponential backoff.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ReplayableRequest:
    """Request that can be replayed."""

    def __init__(self, request_id: str, func: Callable, max_retries: int = 3):
        """Initialize replayable request."""
        self.request_id = request_id
        self.func = func
        self.max_retries = max_retries
        self.retry_count = 0
        self.last_attempt: Optional[datetime] = None
        self.status = "pending"

    async def execute(self) -> bool:
        """Execute request with retry logic."""
        while self.retry_count < self.max_retries:
            try:
                self.last_attempt = datetime.utcnow()
                await self.func()
                self.status = "success"
                return True
            except Exception as e:
                self.retry_count += 1
                logger.warning(f"Request failed (attempt {self.retry_count}): {e}")

                if self.retry_count < self.max_retries:
                    delay = 2 ** self.retry_count
                    await asyncio.sleep(delay)

        self.status = "failed"
        return False


class RequestReplayManager:
    """Manage request replay."""

    def __init__(self):
        """Initialize replay manager."""
        self.requests: Dict[str, ReplayableRequest] = {}

    async def replay_request(self, request_id: str, func: Callable) -> bool:
        """Replay failed request."""
        request = ReplayableRequest(request_id, func)
        self.requests[request_id] = request
        return await request.execute()


replay_manager = RequestReplayManager()
