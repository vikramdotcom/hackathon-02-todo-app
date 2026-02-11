"""
Response Caching System

Cache HTTP responses with ETags and conditional requests.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class CachedResponse:
    """Cached HTTP response."""

    def __init__(self, data: Any, etag: str, ttl_seconds: int = 300):
        """Initialize cached response."""
        self.data = data
        self.etag = etag
        self.cached_at = datetime.utcnow()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if cache is expired."""
        age = (datetime.utcnow() - self.cached_at).total_seconds()
        return age > self.ttl_seconds


class ResponseCache:
    """Cache HTTP responses."""

    def __init__(self):
        """Initialize response cache."""
        self.cache: Dict[str, CachedResponse] = {}

    def generate_etag(self, data: str) -> str:
        """Generate ETag for response."""
        return hashlib.md5(data.encode()).hexdigest()

    def cache_response(self, key: str, data: Any, ttl_seconds: int = 300):
        """Cache response."""
        etag = self.generate_etag(str(data))
        self.cache[key] = CachedResponse(data, etag, ttl_seconds)

    def get_cached(self, key: str, if_none_match: Optional[str] = None) -> Optional[tuple[Any, str, bool]]:
        """Get cached response."""
        if key not in self.cache:
            return None

        cached = self.cache[key]

        if cached.is_expired():
            del self.cache[key]
            return None

        # Check ETag match
        not_modified = if_none_match == cached.etag

        return cached.data, cached.etag, not_modified


response_cache = ResponseCache()
