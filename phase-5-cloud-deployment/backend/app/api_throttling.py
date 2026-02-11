"""
API Throttling System

Advanced request throttling with quotas and burst handling.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class ThrottlePolicy:
    """Throttle policy for API requests."""

    def __init__(self, requests_per_minute: int, burst_size: int):
        """Initialize throttle policy."""
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.request_times: deque = deque(maxlen=burst_size)

    def allow_request(self) -> bool:
        """Check if request is allowed."""
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)

        # Remove old requests
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()

        if len(self.request_times) < self.requests_per_minute:
            self.request_times.append(now)
            return True

        return False


class ThrottleManager:
    """Manage throttling policies."""

    def __init__(self):
        """Initialize throttle manager."""
        self.policies: Dict[str, ThrottlePolicy] = {}

    def set_policy(self, client_id: str, requests_per_minute: int, burst_size: int):
        """Set throttle policy for client."""
        self.policies[client_id] = ThrottlePolicy(requests_per_minute, burst_size)

    def check_throttle(self, client_id: str) -> bool:
        """Check if request is throttled."""
        if client_id not in self.policies:
            return True

        return self.policies[client_id].allow_request()


throttle_manager = ThrottleManager()
