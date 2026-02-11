"""
Tests for Retry Logic and Circuit Breaker
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from app.retry import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerError,
    RetryStrategy,
    retry,
    async_retry
)


class TestCircuitBreaker:
    """Test CircuitBreaker class."""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization."""
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 60
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_successful_call(self):
        """Test successful call through circuit breaker."""
        cb = CircuitBreaker()

        def successful_func():
            return "success"

        result = cb.call(successful_func)

        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_failure_count(self):
        """Test circuit breaker counts failures."""
        cb = CircuitBreaker(failure_threshold=3)

        def failing_func():
            raise ValueError("Test error")

        # First failure
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.failure_count == 1
        assert cb.state == CircuitState.CLOSED

        # Second failure
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.failure_count == 2
        assert cb.state == CircuitState.CLOSED

        # Third failure - should open circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.failure_count == 3
        assert cb.state == CircuitState.OPEN

    def test_circuit_breaker_open_rejects_calls(self):
        """Test that open circuit rejects calls."""
        cb = CircuitBreaker(failure_threshold=1)

        def failing_func():
            raise ValueError("Test error")

        # Trigger circuit to open
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == CircuitState.OPEN

        # Next call should be rejected
        with pytest.raises(CircuitBreakerError):
            cb.call(failing_func)

    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0)

        def failing_func():
            raise ValueError("Test error")

        def successful_func():
            return "success"

        # Open the circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout (set to 0 for testing)
        import time
        time.sleep(0.1)

        # Next call should enter half-open state and succeed
        result = cb.call(successful_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_reset_on_success(self):
        """Test that success resets failure count."""
        cb = CircuitBreaker(failure_threshold=3)

        def failing_func():
            raise ValueError("Test error")

        def successful_func():
            return "success"

        # Two failures
        with pytest.raises(ValueError):
            cb.call(failing_func)
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.failure_count == 2

        # Success should reset count
        cb.call(successful_func)
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_async_call(self):
        """Test async call through circuit breaker."""
        cb = CircuitBreaker()

        async def async_successful_func():
            return "async success"

        result = await cb.call_async(async_successful_func)

        assert result == "async success"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_breaker_async_failure(self):
        """Test async failure handling."""
        cb = CircuitBreaker(failure_threshold=1)

        async def async_failing_func():
            raise ValueError("Async error")

        with pytest.raises(ValueError):
            await cb.call_async(async_failing_func)

        assert cb.state == CircuitState.OPEN


class TestRetryDecorator:
    """Test retry decorator."""

    def test_retry_successful_call(self):
        """Test retry with successful call."""
        call_count = [0]

        @retry(max_attempts=3)
        def successful_func():
            call_count[0] += 1
            return "success"

        result = successful_func()

        assert result == "success"
        assert call_count[0] == 1

    def test_retry_eventual_success(self):
        """Test retry with eventual success."""
        call_count = [0]

        @retry(max_attempts=3, delay=0.1)
        def eventually_successful_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Not yet")
            return "success"

        result = eventually_successful_func()

        assert result == "success"
        assert call_count[0] == 3

    def test_retry_max_attempts_exceeded(self):
        """Test retry when max attempts exceeded."""
        call_count = [0]

        @retry(max_attempts=3, delay=0.1)
        def always_failing_func():
            call_count[0] += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_failing_func()

        assert call_count[0] == 3

    def test_retry_exponential_backoff(self):
        """Test exponential backoff strategy."""
        call_times = []

        @retry(max_attempts=3, delay=0.1, strategy=RetryStrategy.EXPONENTIAL, backoff_factor=2.0)
        def failing_func():
            call_times.append(datetime.utcnow())
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_func()

        assert len(call_times) == 3

        # Check that delays increase exponentially
        if len(call_times) >= 2:
            delay1 = (call_times[1] - call_times[0]).total_seconds()
            assert delay1 >= 0.1  # First delay

        if len(call_times) >= 3:
            delay2 = (call_times[2] - call_times[1]).total_seconds()
            assert delay2 >= 0.2  # Second delay (doubled)

    def test_retry_linear_backoff(self):
        """Test linear backoff strategy."""
        call_count = [0]

        @retry(max_attempts=3, delay=0.1, strategy=RetryStrategy.LINEAR)
        def failing_func():
            call_count[0] += 1
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_func()

        assert call_count[0] == 3

    def test_retry_constant_backoff(self):
        """Test constant backoff strategy."""
        call_count = [0]

        @retry(max_attempts=3, delay=0.1, strategy=RetryStrategy.CONSTANT)
        def failing_func():
            call_count[0] += 1
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_func()

        assert call_count[0] == 3

    def test_retry_specific_exceptions(self):
        """Test retry with specific exception types."""
        call_count = [0]

        @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
        def func_with_specific_error():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("Retryable error")
            return "success"

        result = func_with_specific_error()
        assert result == "success"
        assert call_count[0] == 2


class TestAsyncRetryDecorator:
    """Test async retry decorator."""

    @pytest.mark.asyncio
    async def test_async_retry_successful_call(self):
        """Test async retry with successful call."""
        call_count = [0]

        @async_retry(max_attempts=3)
        async def async_successful_func():
            call_count[0] += 1
            return "async success"

        result = await async_successful_func()

        assert result == "async success"
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_async_retry_eventual_success(self):
        """Test async retry with eventual success."""
        call_count = [0]

        @async_retry(max_attempts=3, delay=0.1)
        async def eventually_successful_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Not yet")
            return "success"

        result = await eventually_successful_func()

        assert result == "success"
        assert call_count[0] == 3

    @pytest.mark.asyncio
    async def test_async_retry_max_attempts_exceeded(self):
        """Test async retry when max attempts exceeded."""
        call_count = [0]

        @async_retry(max_attempts=3, delay=0.1)
        async def always_failing_func():
            call_count[0] += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            await always_failing_func()

        assert call_count[0] == 3

    @pytest.mark.asyncio
    async def test_async_retry_exponential_backoff(self):
        """Test async exponential backoff."""
        call_count = [0]

        @async_retry(max_attempts=3, delay=0.1, strategy=RetryStrategy.EXPONENTIAL)
        async def failing_func():
            call_count[0] += 1
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await failing_func()

        assert call_count[0] == 3


class TestRetryStrategy:
    """Test RetryStrategy enum."""

    def test_retry_strategies_exist(self):
        """Test that all retry strategies exist."""
        assert hasattr(RetryStrategy, "EXPONENTIAL")
        assert hasattr(RetryStrategy, "LINEAR")
        assert hasattr(RetryStrategy, "CONSTANT")

    def test_retry_strategy_values(self):
        """Test retry strategy string values."""
        assert RetryStrategy.EXPONENTIAL == "exponential"
        assert RetryStrategy.LINEAR == "linear"
        assert RetryStrategy.CONSTANT == "constant"
