"""
Performance Monitoring and Profiling

Monitor application performance and identify bottlenecks.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class PerformanceMetric:
    """Performance metric data."""

    def __init__(self, name: str, duration_ms: float, timestamp: datetime):
        """Initialize performance metric."""
        self.name = name
        self.duration_ms = duration_ms
        self.timestamp = timestamp
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class PerformanceMonitor:
    """Monitor application performance."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: List[PerformanceMetric] = []
        self.aggregated_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "total_ms": 0,
                "min_ms": float('inf'),
                "max_ms": 0,
                "avg_ms": 0
            }
        )

    def record_metric(self, name: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
        """Record performance metric."""
        metric = PerformanceMetric(name, duration_ms, datetime.utcnow())

        if metadata:
            metric.metadata = metadata

        self.metrics.append(metric)

        # Update aggregated stats
        stats = self.aggregated_stats[name]
        stats["count"] += 1
        stats["total_ms"] += duration_ms
        stats["min_ms"] = min(stats["min_ms"], duration_ms)
        stats["max_ms"] = max(stats["max_ms"], duration_ms)
        stats["avg_ms"] = stats["total_ms"] / stats["count"]

        # Log slow operations
        if duration_ms > 1000:  # > 1 second
            logger.warning(
                f"Slow operation detected: {name}",
                extra={"name": name, "duration_ms": duration_ms}
            )

    def get_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for metric."""
        return self.aggregated_stats.get(name)

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get all statistics."""
        return dict(self.aggregated_stats)

    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest operations."""
        sorted_metrics = sorted(
            self.metrics,
            key=lambda m: m.duration_ms,
            reverse=True
        )
        return [m.to_dict() for m in sorted_metrics[:limit]]

    def clear_metrics(self):
        """Clear all metrics."""
        self.metrics.clear()
        self.aggregated_stats.clear()


class Timer:
    """Context manager for timing operations."""

    def __init__(self, name: str, monitor: PerformanceMonitor):
        """Initialize timer."""
        self.name = name
        self.monitor = monitor
        self.start_time: Optional[float] = None
        self.duration_ms: Optional[float] = None

    def __enter__(self):
        """Start timer."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and record metric."""
        if self.start_time:
            end_time = time.perf_counter()
            self.duration_ms = (end_time - self.start_time) * 1000
            self.monitor.record_metric(self.name, self.duration_ms)


def timed(monitor: PerformanceMonitor, name: Optional[str] = None):
    """Decorator for timing functions."""
    def decorator(func: Callable):
        metric_name = name or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                monitor.record_metric(metric_name, duration_ms)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                monitor.record_metric(metric_name, duration_ms)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class MemoryProfiler:
    """Profile memory usage."""

    def __init__(self):
        """Initialize memory profiler."""
        self.snapshots: List[Dict[str, Any]] = []

    def take_snapshot(self, label: str):
        """Take memory snapshot."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        snapshot = {
            "label": label,
            "timestamp": datetime.utcnow().isoformat(),
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024
        }

        self.snapshots.append(snapshot)

        logger.info(
            f"Memory snapshot: {label}",
            extra={"label": label, "rss_mb": snapshot["rss_mb"]}
        )

    def get_snapshots(self) -> List[Dict[str, Any]]:
        """Get all snapshots."""
        return self.snapshots

    def get_memory_growth(self) -> Optional[float]:
        """Get memory growth since first snapshot."""
        if len(self.snapshots) < 2:
            return None

        first = self.snapshots[0]["rss_mb"]
        last = self.snapshots[-1]["rss_mb"]

        return last - first


class QueryProfiler:
    """Profile database queries."""

    def __init__(self):
        """Initialize query profiler."""
        self.queries: List[Dict[str, Any]] = []

    def record_query(
        self,
        query: str,
        duration_ms: float,
        rows_affected: int = 0
    ):
        """Record query execution."""
        query_record = {
            "query": query,
            "duration_ms": duration_ms,
            "rows_affected": rows_affected,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.queries.append(query_record)

        # Log slow queries
        if duration_ms > 100:  # > 100ms
            logger.warning(
                f"Slow query detected",
                extra={"duration_ms": duration_ms, "query": query[:100]}
            )

    def get_slow_queries(self, threshold_ms: float = 100) -> List[Dict[str, Any]]:
        """Get slow queries."""
        return [
            q for q in self.queries
            if q["duration_ms"] > threshold_ms
        ]

    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics."""
        if not self.queries:
            return {}

        durations = [q["duration_ms"] for q in self.queries]

        return {
            "total_queries": len(self.queries),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "slow_queries": len(self.get_slow_queries())
        }


class RequestProfiler:
    """Profile HTTP requests."""

    def __init__(self):
        """Initialize request profiler."""
        self.requests: List[Dict[str, Any]] = []

    def record_request(
        self,
        method: str,
        path: str,
        duration_ms: float,
        status_code: int
    ):
        """Record request."""
        request_record = {
            "method": method,
            "path": path,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.requests.append(request_record)

    def get_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics by endpoint."""
        stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "total_ms": 0,
                "avg_ms": 0,
                "errors": 0
            }
        )

        for req in self.requests:
            endpoint = f"{req['method']} {req['path']}"
            stat = stats[endpoint]

            stat["count"] += 1
            stat["total_ms"] += req["duration_ms"]
            stat["avg_ms"] = stat["total_ms"] / stat["count"]

            if req["status_code"] >= 400:
                stat["errors"] += 1

        return dict(stats)

    def get_slowest_endpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest endpoints."""
        sorted_requests = sorted(
            self.requests,
            key=lambda r: r["duration_ms"],
            reverse=True
        )
        return sorted_requests[:limit]


class BottleneckDetector:
    """Detect performance bottlenecks."""

    def __init__(
        self,
        performance_monitor: PerformanceMonitor,
        query_profiler: QueryProfiler
    ):
        """Initialize bottleneck detector."""
        self.performance_monitor = performance_monitor
        self.query_profiler = query_profiler

    def detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks."""
        bottlenecks = []

        # Check slow operations
        slow_ops = self.performance_monitor.get_slowest_operations(5)
        for op in slow_ops:
            if op["duration_ms"] > 1000:
                bottlenecks.append({
                    "type": "slow_operation",
                    "name": op["name"],
                    "duration_ms": op["duration_ms"],
                    "severity": "high" if op["duration_ms"] > 5000 else "medium"
                })

        # Check slow queries
        slow_queries = self.query_profiler.get_slow_queries(100)
        if len(slow_queries) > 10:
            bottlenecks.append({
                "type": "slow_queries",
                "count": len(slow_queries),
                "severity": "high"
            })

        return bottlenecks

    def get_recommendations(self) -> List[str]:
        """Get performance recommendations."""
        recommendations = []
        bottlenecks = self.detect_bottlenecks()

        for bottleneck in bottlenecks:
            if bottleneck["type"] == "slow_operation":
                recommendations.append(
                    f"Optimize {bottleneck['name']} - currently taking {bottleneck['duration_ms']:.0f}ms"
                )
            elif bottleneck["type"] == "slow_queries":
                recommendations.append(
                    f"Optimize database queries - {bottleneck['count']} slow queries detected"
                )

        return recommendations


class PerformanceReport:
    """Generate performance reports."""

    def __init__(
        self,
        performance_monitor: PerformanceMonitor,
        memory_profiler: MemoryProfiler,
        query_profiler: QueryProfiler,
        request_profiler: RequestProfiler
    ):
        """Initialize performance report."""
        self.performance_monitor = performance_monitor
        self.memory_profiler = memory_profiler
        self.query_profiler = query_profiler
        self.request_profiler = request_profiler

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "operations": self.performance_monitor.get_all_stats(),
            "slowest_operations": self.performance_monitor.get_slowest_operations(10),
            "memory": {
                "snapshots": self.memory_profiler.get_snapshots(),
                "growth_mb": self.memory_profiler.get_memory_growth()
            },
            "queries": self.query_profiler.get_query_stats(),
            "slow_queries": self.query_profiler.get_slow_queries()[:10],
            "endpoints": self.request_profiler.get_endpoint_stats(),
            "slowest_endpoints": self.request_profiler.get_slowest_endpoints(10)
        }


# Global instances
performance_monitor = PerformanceMonitor()
memory_profiler = MemoryProfiler()
query_profiler = QueryProfiler()
request_profiler = RequestProfiler()
bottleneck_detector = BottleneckDetector(performance_monitor, query_profiler)
performance_report = PerformanceReport(
    performance_monitor,
    memory_profiler,
    query_profiler,
    request_profiler
)


# Helper functions
def time_operation(name: str):
    """Context manager for timing operations."""
    return Timer(name, performance_monitor)


def record_query(query: str, duration_ms: float, rows_affected: int = 0):
    """Record query execution."""
    query_profiler.record_query(query, duration_ms, rows_affected)


def record_request(method: str, path: str, duration_ms: float, status_code: int):
    """Record HTTP request."""
    request_profiler.record_request(method, path, duration_ms, status_code)


def get_performance_report() -> Dict[str, Any]:
    """Get performance report."""
    return performance_report.generate_report()
