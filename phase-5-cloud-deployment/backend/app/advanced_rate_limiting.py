"""
API Rate Limiting with Token Bucket

Advanced rate limiting implementation with multiple strategies.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception."""
    pass


class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.

        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from bucket."""
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill

        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_available_tokens(self) -> float:
        """Get available tokens."""
        self._refill()
        return self.tokens

    def get_wait_time(self, tokens: int = 1) -> float:
        """Get wait time until tokens available."""
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class SlidingWindowCounter:
    """Sliding window counter rate limiter."""

    def __init__(self, window_size_seconds: int, max_requests: int):
        """Initialize sliding window counter."""
        self.window_size = window_size_seconds
        self.max_requests = max_requests
        self.requests: deque = deque()

    def allow_request(self) -> bool:
        """Check if request is allowed."""
        now = time.time()
        cutoff = now - self.window_size

        # Remove old requests
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True

        return False

    def get_remaining_requests(self) -> int:
        """Get remaining requests in window."""
        now = time.time()
        cutoff = now - self.window_size

        # Remove old requests
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

        return max(0, self.max_requests - len(self.requests))

    def get_reset_time(self) -> float:
        """Get time until window resets."""
        if not self.requests:
            return 0.0

        oldest_request = self.requests[0]
        reset_time = oldest_request + self.window_size
        return max(0.0, reset_time - time.time())


class LeakyBucket:
    """Leaky bucket rate limiter."""

    def __init__(self, capacity: int, leak_rate: float):
        """Initialize leaky bucket.

        Args:
            capacity: Maximum bucket size
            leak_rate: Requests leaked per second
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.level = 0.0
        self.last_leak = time.time()

    def allow_request(self) -> bool:
        """Check if request is allowed."""
        self._leak()

        if self.level < self.capacity:
            self.level += 1
            return True

        return False

    def _leak(self):
        """Leak requests from bucket."""
        now = time.time()
        elapsed = now - self.last_leak

        leaked = elapsed * self.leak_rate
        self.level = max(0.0, self.level - leaked)
        self.last_leak = now

    def get_level(self) -> float:
        """Get current bucket level."""
        self._leak()
        return self.level


class FixedWindowCounter:
    """Fixed window counter rate limiter."""

    def __init__(self, window_size_seconds: int, max_requests: int):
        """Initialize fixed window counter."""
        self.window_size = window_size_seconds
        self.max_requests = max_requests
        self.windows: Dict[int, int] = {}

    def allow_request(self) -> bool:
        """Check if request is allowed."""
        window_key = int(time.time() / self.window_size)

        if window_key not in self.windows:
            self.windows[window_key] = 0

        if self.windows[window_key] < self.max_requests:
            self.windows[window_key] += 1
            self._cleanup_old_windows(window_key)
            return True

        return False

    def _cleanup_old_windows(self, current_window: int):
        """Cleanup old windows."""
        old_windows = [w for w in self.windows if w < current_window - 1]
        for window in old_windows:
            del self.windows[window]


class RateLimiterManager:
    """Manage rate limiters for different clients."""

    def __init__(self, strategy: str = "token_bucket"):
        """Initialize rate limiter manager."""
        self.strategy = strategy
        self.limiters: Dict[str, Any] = {}
        self.default_config = {
            "token_bucket": {"capacity": 100, "refill_rate": 10},
            "sliding_window": {"window_size": 60, "max_requests": 100},
            "leaky_bucket": {"capacity": 100, "leak_rate": 10},
            "fixed_window": {"window_size": 60, "max_requests": 100}
        }

    def get_limiter(self, client_id: str):
        """Get or create rate limiter for client."""
        if client_id not in self.limiters:
            self.limiters[client_id] = self._create_limiter()

        return self.limiters[client_id]

    def _create_limiter(self):
        """Create rate limiter based on strategy."""
        config = self.default_config[self.strategy]

        if self.strategy == "token_bucket":
            return TokenBucket(config["capacity"], config["refill_rate"])
        elif self.strategy == "sliding_window":
            return SlidingWindowCounter(config["window_size"], config["max_requests"])
        elif self.strategy == "leaky_bucket":
            return LeakyBucket(config["capacity"], config["leak_rate"])
        elif self.strategy == "fixed_window":
            return FixedWindowCounter(config["window_size"], config["max_requests"])

    def check_rate_limit(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        limiter = self.get_limiter(client_id)

        if self.strategy == "token_bucket":
            return limiter.consume()
        else:
            return limiter.allow_request()

    def get_rate_limit_info(self, client_id: str) -> Dict[str, Any]:
        """Get rate limit info for client."""
        limiter = self.get_limiter(client_id)

        if self.strategy == "token_bucket":
            return {
                "available_tokens": limiter.get_available_tokens(),
                "capacity": limiter.capacity,
                "refill_rate": limiter.refill_rate
            }
        elif self.strategy == "sliding_window":
            return {
                "remaining_requests": limiter.get_remaining_requests(),
                "max_requests": limiter.max_requests,
                "reset_time": limiter.get_reset_time()
            }
        elif self.strategy == "leaky_bucket":
            return {
                "current_level": limiter.get_level(),
                "capacity": limiter.capacity,
                "leak_rate": limiter.leak_rate
            }

        return {}


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on system load."""

    def __init__(self, base_limit: int):
        """Initialize adaptive rate limiter."""
        self.base_limit = base_limit
        self.current_limit = base_limit
        self.system_load = 0.0
        self.limiter = TokenBucket(base_limit, base_limit / 60)

    def update_system_load(self, load: float):
        """Update system load (0.0 to 1.0)."""
        self.system_load = load

        # Adjust limit based on load
        if load > 0.8:
            self.current_limit = int(self.base_limit * 0.5)
        elif load > 0.6:
            self.current_limit = int(self.base_limit * 0.75)
        else:
            self.current_limit = self.base_limit

        # Update limiter
        self.limiter.capacity = self.current_limit
        self.limiter.refill_rate = self.current_limit / 60

    def allow_request(self) -> bool:
        """Check if request is allowed."""
        return self.limiter.consume()


class QuotaManager:
    """Manage API quotas."""

    def __init__(self):
        """Initialize quota manager."""
        self.quotas: Dict[str, Dict[str, Any]] = {}

    def set_quota(
        self,
        client_id: str,
        daily_limit: int,
        monthly_limit: int
    ):
        """Set quota for client."""
        self.quotas[client_id] = {
            "daily_limit": daily_limit,
            "monthly_limit": monthly_limit,
            "daily_used": 0,
            "monthly_used": 0,
            "last_reset_daily": datetime.utcnow().date(),
            "last_reset_monthly": datetime.utcnow().replace(day=1).date()
        }

    def consume_quota(self, client_id: str, amount: int = 1) -> bool:
        """Consume quota."""
        if client_id not in self.quotas:
            return True

        quota = self.quotas[client_id]
        self._reset_if_needed(quota)

        if (quota["daily_used"] + amount <= quota["daily_limit"] and
            quota["monthly_used"] + amount <= quota["monthly_limit"]):
            quota["daily_used"] += amount
            quota["monthly_used"] += amount
            return True

        return False

    def _reset_if_needed(self, quota: Dict[str, Any]):
        """Reset quota if period expired."""
        today = datetime.utcnow().date()

        # Reset daily
        if quota["last_reset_daily"] < today:
            quota["daily_used"] = 0
            quota["last_reset_daily"] = today

        # Reset monthly
        month_start = datetime.utcnow().replace(day=1).date()
        if quota["last_reset_monthly"] < month_start:
            quota["monthly_used"] = 0
            quota["last_reset_monthly"] = month_start

    def get_quota_info(self, client_id: str) -> Dict[str, Any]:
        """Get quota information."""
        if client_id not in self.quotas:
            return {}

        quota = self.quotas[client_id]
        self._reset_if_needed(quota)

        return {
            "daily_limit": quota["daily_limit"],
            "daily_used": quota["daily_used"],
            "daily_remaining": quota["daily_limit"] - quota["daily_used"],
            "monthly_limit": quota["monthly_limit"],
            "monthly_used": quota["monthly_used"],
            "monthly_remaining": quota["monthly_limit"] - quota["monthly_used"]
        }


class RateLimitMiddleware:
    """Middleware for rate limiting."""

    def __init__(self, rate_limiter_manager: RateLimiterManager):
        """Initialize rate limit middleware."""
        self.rate_limiter = rate_limiter_manager

    async def __call__(self, request):
        """Apply rate limiting."""
        client_id = self._get_client_id(request)

        if not self.rate_limiter.check_rate_limit(client_id):
            info = self.rate_limiter.get_rate_limit_info(client_id)

            logger.warning(
                f"Rate limit exceeded: {client_id}",
                extra={"client_id": client_id, "info": info}
            )

            raise RateLimitExceeded("Rate limit exceeded")

    def _get_client_id(self, request) -> str:
        """Get client identifier."""
        # Try API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key

        # Try user ID
        if hasattr(request, "user") and request.user:
            return f"user:{request.user.id}"

        # Fall back to IP
        return request.client.host if hasattr(request, "client") else "unknown"


class RateLimitMetrics:
    """Track rate limiting metrics."""

    def __init__(self):
        """Initialize rate limit metrics."""
        self.total_requests = 0
        self.blocked_requests = 0
        self.client_metrics: Dict[str, Dict[str, int]] = {}

    def record_request(self, client_id: str, blocked: bool):
        """Record request."""
        self.total_requests += 1

        if blocked:
            self.blocked_requests += 1

        if client_id not in self.client_metrics:
            self.client_metrics[client_id] = {
                "total": 0,
                "blocked": 0
            }

        self.client_metrics[client_id]["total"] += 1
        if blocked:
            self.client_metrics[client_id]["blocked"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics."""
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "block_rate": (
                self.blocked_requests / self.total_requests
                if self.total_requests > 0 else 0
            ),
            "unique_clients": len(self.client_metrics)
        }

    def get_client_metrics(self, client_id: str) -> Dict[str, Any]:
        """Get metrics for client."""
        if client_id not in self.client_metrics:
            return {}

        metrics = self.client_metrics[client_id]
        return {
            "total_requests": metrics["total"],
            "blocked_requests": metrics["blocked"],
            "block_rate": (
                metrics["blocked"] / metrics["total"]
                if metrics["total"] > 0 else 0
            )
        }


# Global instances
rate_limiter_manager = RateLimiterManager(strategy="token_bucket")
quota_manager = QuotaManager()
rate_limit_middleware = RateLimitMiddleware(rate_limiter_manager)
rate_limit_metrics = RateLimitMetrics()


# Helper functions
def check_rate_limit(client_id: str) -> bool:
    """Check rate limit for client."""
    allowed = rate_limiter_manager.check_rate_limit(client_id)
    rate_limit_metrics.record_request(client_id, not allowed)
    return allowed


def get_rate_limit_info(client_id: str) -> Dict[str, Any]:
    """Get rate limit info."""
    return rate_limiter_manager.get_rate_limit_info(client_id)


def set_quota(client_id: str, daily_limit: int, monthly_limit: int):
    """Set quota for client."""
    quota_manager.set_quota(client_id, daily_limit, monthly_limit)


def consume_quota(client_id: str, amount: int = 1) -> bool:
    """Consume quota."""
    return quota_manager.consume_quota(client_id, amount)
