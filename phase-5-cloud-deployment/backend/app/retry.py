"""
Retry Logic and Circuit Breaker

Provides utilities for handling transient failures and preventing cascade failures.
"""

import asyncio
import logging
from typing import Callable, Any, Optional, Type
from functools import wraps
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class RetryStrategy(str, Enum):
    """Retry strategies."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self.state != CircuitState.OPEN:
            return False

        if not self.last_failure_time:
            return True

        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering half-open state")
            else:
                raise CircuitBreakerError("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker closed after successful call")

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}",
                extra={"error": str(e)}
            )

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error("Circuit breaker opened due to failures")

            raise

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute async function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering half-open state")
            else:
                raise CircuitBreakerError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)

            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker closed after successful call")

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}",
                extra={"error": str(e)}
            )

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error("Circuit breaker opened due to failures")

            raise


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator for functions.

    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries (seconds)
        strategy: Retry strategy (exponential, linear, constant)
        backoff_factor: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    attempt += 1

                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retry attempts ({max_attempts}) reached for {func.__name__}",
                            extra={"error": str(e)}
                        )
                        raise

                    logger.warning(
                        f"Retry attempt {attempt}/{max_attempts} for {func.__name__}",
                        extra={"error": str(e), "delay": current_delay}
                    )

                    import time
                    time.sleep(current_delay)

                    # Calculate next delay based on strategy
                    if strategy == RetryStrategy.EXPONENTIAL:
                        current_delay *= backoff_factor
                    elif strategy == RetryStrategy.LINEAR:
                        current_delay += delay

        return wrapper
    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Async retry decorator for coroutines.

    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries (seconds)
        strategy: Retry strategy (exponential, linear, constant)
        backoff_factor: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated coroutine
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    attempt += 1

                    if attempt >= max_attempts:
                        logger.error(
                            f"Max retry attempts ({max_attempts}) reached for {func.__name__}",
                            extra={"error": str(e)}
                        )
                        raise

                    logger.warning(
                        f"Retry attempt {attempt}/{max_attempts} for {func.__name__}",
                        extra={"error": str(e), "delay": current_delay}
                    )

                    await asyncio.sleep(current_delay)

                    # Calculate next delay based on strategy
                    if strategy == RetryStrategy.EXPONENTIAL:
                        current_delay *= backoff_factor
                    elif strategy == RetryStrategy.LINEAR:
                        current_delay += delay

        return wrapper
    return decorator


# Example usage
@retry(max_attempts=3, delay=1.0, strategy=RetryStrategy.EXPONENTIAL)
def fetch_external_data(url: str) -> dict:
    """Fetch data from external API with retry."""
    import requests
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


@async_retry(max_attempts=3, delay=1.0, strategy=RetryStrategy.EXPONENTIAL)
async def async_fetch_external_data(url: str) -> dict:
    """Async fetch data from external API with retry."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
