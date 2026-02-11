"""
Performance Monitoring Utilities

Provides utilities for monitoring application performance and metrics.
"""

import time
import functools
from typing import Callable, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Utilities for monitoring performance metrics."""

    @staticmethod
    def time_function(func: Callable) -> Callable:
        """
        Decorator to measure function execution time.

        Args:
            func: Function to measure

        Returns:
            Wrapped function that logs execution time
        """
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"{func.__name__} completed in {duration_ms:.2f}ms",
                    extra={"duration_ms": duration_ms, "function": func.__name__}
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{func.__name__} failed after {duration_ms:.2f}ms: {e}",
                    extra={"duration_ms": duration_ms, "function": func.__name__}
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"{func.__name__} completed in {duration_ms:.2f}ms",
                    extra={"duration_ms": duration_ms, "function": func.__name__}
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"{func.__name__} failed after {duration_ms:.2f}ms: {e}",
                    extra={"duration_ms": duration_ms, "function": func.__name__}
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    @staticmethod
    @contextmanager
    def measure_time(operation_name: str):
        """
        Context manager to measure operation time.

        Args:
            operation_name: Name of the operation being measured

        Example:
            with PerformanceMonitor.measure_time("database_query"):
                result = db.query(...)
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"{operation_name} completed in {duration_ms:.2f}ms",
                extra={"duration_ms": duration_ms, "operation": operation_name}
            )


class MetricsCollector:
    """Collect and aggregate application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "response_times": [],
            "database_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def record_request(self, success: bool, response_time_ms: float):
        """
        Record an HTTP request.

        Args:
            success: Whether the request was successful
            response_time_ms: Response time in milliseconds
        """
        self.metrics["requests_total"] += 1
        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_error"] += 1
        self.metrics["response_times"].append(response_time_ms)

    def record_database_query(self):
        """Record a database query."""
        self.metrics["database_queries"] += 1

    def record_cache_hit(self):
        """Record a cache hit."""
        self.metrics["cache_hits"] += 1

    def record_cache_miss(self):
        """Record a cache miss."""
        self.metrics["cache_misses"] += 1

    def get_metrics(self) -> dict:
        """
        Get current metrics.

        Returns:
            Dict with current metrics
        """
        response_times = self.metrics["response_times"]

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
        else:
            avg_response_time = 0
            p95_response_time = 0
            p99_response_time = 0

        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = (
            (self.metrics["cache_hits"] / cache_total * 100)
            if cache_total > 0
            else 0
        )

        return {
            "requests": {
                "total": self.metrics["requests_total"],
                "success": self.metrics["requests_success"],
                "error": self.metrics["requests_error"],
                "error_rate": (
                    (self.metrics["requests_error"] / self.metrics["requests_total"] * 100)
                    if self.metrics["requests_total"] > 0
                    else 0
                )
            },
            "response_times": {
                "avg_ms": round(avg_response_time, 2),
                "p95_ms": round(p95_response_time, 2),
                "p99_ms": round(p99_response_time, 2)
            },
            "database": {
                "queries": self.metrics["database_queries"]
            },
            "cache": {
                "hits": self.metrics["cache_hits"],
                "misses": self.metrics["cache_misses"],
                "hit_rate": round(cache_hit_rate, 2)
            }
        }

    def reset(self):
        """Reset all metrics."""
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "response_times": [],
            "database_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()
