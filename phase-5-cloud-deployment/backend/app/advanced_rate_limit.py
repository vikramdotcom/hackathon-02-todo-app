"""
API Rate Limiting with Token Bucket Algorithm

Advanced rate limiting with per-user and per-endpoint limits.
"""

import logging
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RateLimitTier(str, Enum):
    """Rate limit tiers."""

    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class RateLimitConfig:
    """Rate limit configuration."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
        burst_size: int = 10
    ):
        """
        Initialize rate limit config.

        Args:
            requests_per_minute: Requests allowed per minute
            requests_per_hour: Requests allowed per hour
            requests_per_day: Requests allowed per day
            burst_size: Burst capacity
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.burst_size = burst_size


# Tier configurations
TIER_CONFIGS = {
    RateLimitTier.FREE: RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=100,
        requests_per_day=1000,
        burst_size=5
    ),
    RateLimitTier.BASIC: RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
        burst_size=10
    ),
    RateLimitTier.PREMIUM: RateLimitConfig(
        requests_per_minute=300,
        requests_per_hour=5000,
        requests_per_day=50000,
        burst_size=50
    ),
    RateLimitTier.ENTERPRISE: RateLimitConfig(
        requests_per_minute=1000,
        requests_per_hour=20000,
        requests_per_day=200000,
        burst_size=100
    )
}


class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens consumed successfully
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time to wait for tokens.

        Args:
            tokens: Number of tokens needed

        Returns:
            Wait time in seconds
        """
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate

    def get_available_tokens(self) -> int:
        """Get number of available tokens."""
        self._refill()
        return int(self.tokens)


class RateLimiter:
    """Advanced rate limiter with multiple time windows."""

    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config

        # Create token buckets for different time windows
        self.minute_bucket = TokenBucket(
            capacity=config.requests_per_minute,
            refill_rate=config.requests_per_minute / 60.0
        )

        self.hour_bucket = TokenBucket(
            capacity=config.requests_per_hour,
            refill_rate=config.requests_per_hour / 3600.0
        )

        self.day_bucket = TokenBucket(
            capacity=config.requests_per_day,
            refill_rate=config.requests_per_day / 86400.0
        )

        self.burst_bucket = TokenBucket(
            capacity=config.burst_size,
            refill_rate=config.burst_size / 10.0  # Refill burst in 10 seconds
        )

    def check_limit(self) -> Tuple[bool, Optional[float]]:
        """
        Check if request is allowed.

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        # Check all buckets
        if not self.burst_bucket.consume():
            wait_time = self.burst_bucket.get_wait_time()
            return False, wait_time

        if not self.minute_bucket.consume():
            wait_time = self.minute_bucket.get_wait_time()
            return False, wait_time

        if not self.hour_bucket.consume():
            wait_time = self.hour_bucket.get_wait_time()
            return False, wait_time

        if not self.day_bucket.consume():
            wait_time = self.day_bucket.get_wait_time()
            return False, wait_time

        return True, None

    def get_limits(self) -> Dict[str, int]:
        """
        Get current limits.

        Returns:
            Dictionary of limits
        """
        return {
            "minute": {
                "limit": self.config.requests_per_minute,
                "remaining": self.minute_bucket.get_available_tokens()
            },
            "hour": {
                "limit": self.config.requests_per_hour,
                "remaining": self.hour_bucket.get_available_tokens()
            },
            "day": {
                "limit": self.config.requests_per_day,
                "remaining": self.day_bucket.get_available_tokens()
            },
            "burst": {
                "limit": self.config.burst_size,
                "remaining": self.burst_bucket.get_available_tokens()
            }
        }


class RateLimitManager:
    """Manage rate limiters for users and endpoints."""

    def __init__(self):
        """Initialize rate limit manager."""
        self.user_limiters: Dict[int, RateLimiter] = {}
        self.endpoint_limiters: Dict[str, RateLimiter] = {}
        self.user_tiers: Dict[int, RateLimitTier] = {}

    def set_user_tier(self, user_id: int, tier: RateLimitTier):
        """
        Set user's rate limit tier.

        Args:
            user_id: User ID
            tier: Rate limit tier
        """
        self.user_tiers[user_id] = tier

        # Create new limiter with tier config
        config = TIER_CONFIGS[tier]
        self.user_limiters[user_id] = RateLimiter(config)

        logger.info(
            f"Set rate limit tier for user {user_id}",
            extra={"user_id": user_id, "tier": tier}
        )

    def get_user_limiter(self, user_id: int) -> RateLimiter:
        """
        Get rate limiter for user.

        Args:
            user_id: User ID

        Returns:
            RateLimiter instance
        """
        if user_id not in self.user_limiters:
            # Default to FREE tier
            self.set_user_tier(user_id, RateLimitTier.FREE)

        return self.user_limiters[user_id]

    def check_user_limit(self, user_id: int) -> Tuple[bool, Optional[float]]:
        """
        Check rate limit for user.

        Args:
            user_id: User ID

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        limiter = self.get_user_limiter(user_id)
        allowed, retry_after = limiter.check_limit()

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for user {user_id}",
                extra={
                    "user_id": user_id,
                    "retry_after": retry_after
                }
            )

        return allowed, retry_after

    def get_user_limits(self, user_id: int) -> Dict[str, int]:
        """
        Get current limits for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary of limits
        """
        limiter = self.get_user_limiter(user_id)
        return limiter.get_limits()

    def register_endpoint_limit(
        self,
        endpoint: str,
        config: RateLimitConfig
    ):
        """
        Register rate limit for endpoint.

        Args:
            endpoint: Endpoint path
            config: Rate limit configuration
        """
        self.endpoint_limiters[endpoint] = RateLimiter(config)
        logger.info(f"Registered rate limit for endpoint: {endpoint}")

    def check_endpoint_limit(self, endpoint: str) -> Tuple[bool, Optional[float]]:
        """
        Check rate limit for endpoint.

        Args:
            endpoint: Endpoint path

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        if endpoint not in self.endpoint_limiters:
            return True, None

        limiter = self.endpoint_limiters[endpoint]
        return limiter.check_limit()


# Global rate limit manager
rate_limit_manager = RateLimitManager()


# FastAPI middleware
class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI."""

    def __init__(self, app, manager: RateLimitManager):
        """
        Initialize middleware.

        Args:
            app: FastAPI app
            manager: Rate limit manager
        """
        self.app = app
        self.manager = manager

    async def __call__(self, scope, receive, send):
        """Process request with rate limiting."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract user ID from request
        # In production, get from JWT token or session
        user_id = scope.get("user_id", 0)

        # Check rate limit
        allowed, retry_after = self.manager.check_user_limit(user_id)

        if not allowed:
            # Send rate limit exceeded response
            response = {
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"retry-after", str(int(retry_after)).encode())
                ],
                "body": b'{"error": "rate_limit_exceeded", "message": "Too many requests"}'
            }

            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": response["headers"]
            })

            await send({
                "type": "http.response.body",
                "body": response["body"]
            })

            return

        # Add rate limit headers
        limits = self.manager.get_user_limits(user_id)

        # Continue with request
        await self.app(scope, receive, send)


# Example usage
def setup_rate_limits():
    """Setup rate limits for endpoints."""

    # Strict limits for expensive operations
    rate_limit_manager.register_endpoint_limit(
        "/api/v2/todos/search",
        RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=500,
            requests_per_day=5000,
            burst_size=5
        )
    )

    # Moderate limits for write operations
    rate_limit_manager.register_endpoint_limit(
        "/api/v2/todos",
        RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_size=10
        )
    )
