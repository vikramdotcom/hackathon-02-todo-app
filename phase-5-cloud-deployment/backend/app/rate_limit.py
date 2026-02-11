"""
Rate Limiting Utilities

Provides rate limiting functionality to prevent API abuse.
"""

import time
from typing import Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter using token bucket algorithm.

    For production, consider using Redis-based rate limiting.
    """

    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_minute / 60
        self._buckets: Dict[str, Dict] = defaultdict(lambda: {
            "tokens": self.requests_per_minute,
            "last_update": time.time()
        })

    def _refill_bucket(self, bucket: Dict) -> None:
        """
        Refill tokens in bucket based on elapsed time.

        Args:
            bucket: Bucket dictionary with tokens and last_update
        """
        now = time.time()
        elapsed = now - bucket["last_update"]

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.requests_per_second
        bucket["tokens"] = min(
            self.requests_per_minute,
            bucket["tokens"] + tokens_to_add
        )
        bucket["last_update"] = now

    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed for given key.

        Args:
            key: Identifier for rate limiting (e.g., user_id, IP address)

        Returns:
            True if request is allowed, False otherwise
        """
        bucket = self._buckets[key]
        self._refill_bucket(bucket)

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            logger.debug(f"Rate limit check passed for {key}: {bucket['tokens']:.2f} tokens remaining")
            return True
        else:
            logger.warning(f"Rate limit exceeded for {key}")
            return False

    def get_remaining(self, key: str) -> int:
        """
        Get remaining requests for given key.

        Args:
            key: Identifier for rate limiting

        Returns:
            Number of remaining requests
        """
        bucket = self._buckets[key]
        self._refill_bucket(bucket)
        return int(bucket["tokens"])

    def reset(self, key: str) -> None:
        """
        Reset rate limit for given key.

        Args:
            key: Identifier for rate limiting
        """
        if key in self._buckets:
            del self._buckets[key]
            logger.info(f"Rate limit reset for {key}")

    def get_stats(self) -> Dict:
        """
        Get rate limiter statistics.

        Returns:
            Dict with rate limiter stats
        """
        return {
            "requests_per_minute": self.requests_per_minute,
            "tracked_keys": len(self._buckets)
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


def check_rate_limit(key: str, limit: Optional[int] = None) -> tuple[bool, int]:
    """
    Check rate limit for given key.

    Args:
        key: Identifier for rate limiting
        limit: Optional custom limit (uses default if not provided)

    Returns:
        Tuple of (is_allowed, remaining_requests)
    """
    if limit:
        # Create temporary rate limiter with custom limit
        limiter = RateLimiter(requests_per_minute=limit)
        allowed = limiter.is_allowed(key)
        remaining = limiter.get_remaining(key)
    else:
        allowed = rate_limiter.is_allowed(key)
        remaining = rate_limiter.get_remaining(key)

    return allowed, remaining
