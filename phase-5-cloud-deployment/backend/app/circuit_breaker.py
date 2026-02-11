"""
Circuit Breaker Pattern Implementation

Prevent cascading failures with circuit breaker pattern.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerError(Exception):
    """Circuit breaker open exception."""
    pass


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering half-open state")
            else:
                raise CircuitBreakerError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.success_count += 1

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker closed after successful recovery")

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt reset."""
        if not self.last_failure_time:
            return False

        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class BulkheadIsolation:
    """Bulkhead pattern for resource isolation."""

    def __init__(self, max_concurrent: int):
        """Initialize bulkhead.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_count = 0
        self.rejected_count = 0

    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with bulkhead isolation."""
        if self.semaphore.locked():
            self.rejected_count += 1
            raise Exception("Bulkhead capacity exceeded")

        async with self.semaphore:
            self.active_count += 1
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                self.active_count -= 1

    def get_stats(self) -> Dict[str, Any]:
        """Get bulkhead statistics."""
        return {
            "max_concurrent": self.max_concurrent,
            "active_count": self.active_count,
            "rejected_count": self.rejected_count,
            "available_capacity": self.max_concurrent - self.active_count
        }


class RetryPolicy:
    """Retry policy with exponential backoff."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        """Initialize retry policy."""
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with retry policy."""
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                last_exception = e

                if attempt < self.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)

        logger.error(f"All {self.max_attempts} attempts failed")
        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for attempt."""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


class Timeout:
    """Timeout wrapper for operations."""

    def __init__(self, timeout_seconds: float):
        """Initialize timeout."""
        self.timeout_seconds = timeout_seconds

    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with timeout."""
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {self.timeout_seconds}s")
            raise


class FallbackHandler:
    """Fallback handler for degraded operations."""

    def __init__(self, fallback_func: Callable):
        """Initialize fallback handler."""
        self.fallback_func = fallback_func

    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with fallback."""
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logger.warning(f"Primary function failed, using fallback: {e}")
            return await self.fallback_func(*args, **kwargs)


class ResiliencePolicy:
    """Combined resilience policy."""

    def __init__(
        self,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_policy: Optional[RetryPolicy] = None,
        timeout: Optional[Timeout] = None,
        fallback: Optional[FallbackHandler] = None
    ):
        """Initialize resilience policy."""
        self.circuit_breaker = circuit_breaker
        self.retry_policy = retry_policy
        self.timeout = timeout
        self.fallback = fallback

    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with resilience policies."""
        async def wrapped_func(*args, **kwargs):
            result = await func(*args, **kwargs)
            return result

        # Apply timeout
        if self.timeout:
            original_func = wrapped_func
            async def wrapped_func(*args, **kwargs):
                return await self.timeout.execute(original_func, *args, **kwargs)

        # Apply retry
        if self.retry_policy:
            original_func = wrapped_func
            async def wrapped_func(*args, **kwargs):
                return await self.retry_policy.execute(original_func, *args, **kwargs)

        # Apply circuit breaker
        if self.circuit_breaker:
            original_func = wrapped_func
            async def wrapped_func(*args, **kwargs):
                return await self.circuit_breaker.call(original_func, *args, **kwargs)

        # Apply fallback
        if self.fallback:
            original_func = wrapped_func
            async def wrapped_func(*args, **kwargs):
                return await self.fallback.execute(original_func, *args, **kwargs)

        return await wrapped_func(*args, **kwargs)


# Global instances
default_circuit_breaker = CircuitBreaker()
default_retry_policy = RetryPolicy()
default_timeout = Timeout(30.0)


# Helper functions
async def with_circuit_breaker(func: Callable, *args, **kwargs):
    """Execute function with circuit breaker."""
    return await default_circuit_breaker.call(func, *args, **kwargs)


async def with_retry(func: Callable, *args, **kwargs):
    """Execute function with retry."""
    return await default_retry_policy.execute(func, *args, **kwargs)


async def with_timeout(func: Callable, timeout_seconds: float, *args, **kwargs):
    """Execute function with timeout."""
    timeout = Timeout(timeout_seconds)
    return await timeout.execute(func, *args, **kwargs)
