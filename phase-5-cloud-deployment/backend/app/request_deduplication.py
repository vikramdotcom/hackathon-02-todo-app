"""
Request Deduplication System

Prevent duplicate request processing with idempotency keys.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class RequestCache:
    """Cache for processed requests."""

    def __init__(self, ttl_minutes: int = 60):
        """Initialize request cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_minutes = ttl_minutes

    def add_request(self, idempotency_key: str, response: Any):
        """Add processed request to cache."""
        self.cache[idempotency_key] = {
            "response": response,
            "timestamp": datetime.utcnow()
        }

    def get_cached_response(self, idempotency_key: str) -> Optional[Any]:
        """Get cached response if exists."""
        if idempotency_key not in self.cache:
            return None

        entry = self.cache[idempotency_key]
        age = datetime.utcnow() - entry["timestamp"]

        if age > timedelta(minutes=self.ttl_minutes):
            del self.cache[idempotency_key]
            return None

        return entry["response"]

    def generate_key(self, request_data: str) -> str:
        """Generate idempotency key from request data."""
        return hashlib.sha256(request_data.encode()).hexdigest()


request_cache = RequestCache()
