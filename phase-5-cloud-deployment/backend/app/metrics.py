"""
Performance Metrics Collection

Provides utilities for collecting and analyzing performance metrics.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, stdev
import json

logger = logging.getLogger(__name__)


class MetricType:
    """Metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class Metric:
    """Performance metric."""

    def __init__(self, name: str, metric_type: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Initialize metric."""
        self.name = name
        self.metric_type = metric_type
        self.value = value
        self.tags = tags or {}
        self.timestamp = datetime.utcnow()


class MetricsCollector:
    """Collect and aggregate metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)

    def increment(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Increment counter."""
        key = self._make_key(name, tags)
        self.counters[key] += value

        metric = Metric(name, MetricType.COUNTER, value, tags)
        self.metrics.append(metric)

    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set gauge value."""
        key = self._make_key(name, tags)
        self.gauges[key] = value

        metric = Metric(name, MetricType.GAUGE, value, tags)
        self.metrics.append(metric)

    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record histogram value."""
        key = self._make_key(name, tags)
        self.histograms[key].append(value)

        metric = Metric(name, MetricType.HISTOGRAM, value, tags)
        self.metrics.append(metric)

    def timing(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record timing."""
        key = self._make_key(name, tags)
        self.timers[key].append(duration_ms)

        metric = Metric(name, MetricType.TIMER, duration_ms, tags)
        self.metrics.append(metric)

    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Make metric key."""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"

    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get counter value."""
        key = self._make_key(name, tags)
        return self.counters.get(key, 0.0)

    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get gauge value."""
        key = self._make_key(name, tags)
        return self.gauges.get(key)

    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._make_key(name, tags)
        values = self.histograms.get(key, [])

        if not values:
            return {}

        sorted_values = sorted(values)

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": mean(values),
            "median": median(values),
            "p95": sorted_values[int(len(values) * 0.95)] if len(values) > 0 else 0,
            "p99": sorted_values[int(len(values) * 0.99)] if len(values) > 0 else 0,
            "stdev": stdev(values) if len(values) > 1 else 0
        }

    def get_timer_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics."""
        key = self._make_key(name, tags)
        values = self.timers.get(key, [])

        if not values:
            return {}

        sorted_values = sorted(values)

        return {
            "count": len(values),
            "min_ms": min(values),
            "max_ms": max(values),
            "mean_ms": mean(values),
            "median_ms": median(values),
            "p95_ms": sorted_values[int(len(values) * 0.95)] if len(values) > 0 else 0,
            "p99_ms": sorted_values[int(len(values) * 0.99)] if len(values) > 0 else 0,
            "stdev_ms": stdev(values) if len(values) > 1 else 0
        }

    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {k: self.get_histogram_stats(k.split("[")[0]) for k in self.histograms.keys()},
            "timers": {k: self.get_timer_stats(k.split("[")[0]) for k in self.timers.keys()}
        }

    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timers.clear()


class Timer:
    """Context manager for timing operations."""

    def __init__(self, collector: MetricsCollector, name: str, tags: Optional[Dict[str, str]] = None):
        """Initialize timer."""
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start_time = None

    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and record."""
        duration_ms = (time.time() - self.start_time) * 1000
        self.collector.timing(self.name, duration_ms, self.tags)


# Global metrics collector
metrics_collector = MetricsCollector()


# Decorator for timing functions
def timed(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator to time function execution."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with Timer(metrics_collector, metric_name, tags):
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            with Timer(metrics_collector, metric_name, tags):
                return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Example usage
@timed("api.todos.list")
async def list_todos():
    """Example timed function."""
    pass


# Metric reporters
class MetricsReporter:
    """Report metrics to external systems."""

    def __init__(self, collector: MetricsCollector):
        """Initialize reporter."""
        self.collector = collector

    def report_to_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Counters
        for key, value in self.collector.counters.items():
            lines.append(f"{key} {value}")

        # Gauges
        for key, value in self.collector.gauges.items():
            lines.append(f"{key} {value}")

        return "\n".join(lines)

    def report_to_json(self) -> str:
        """Export metrics as JSON."""
        return json.dumps(self.collector.export_metrics(), indent=2)

    def report_to_statsd(self, host: str = "localhost", port: int = 8125):
        """Send metrics to StatsD."""
        # In production, use statsd client
        logger.info(f"Would send metrics to StatsD at {host}:{port}")


# Application metrics
class ApplicationMetrics:
    """Track application-level metrics."""

    def __init__(self, collector: MetricsCollector):
        """Initialize application metrics."""
        self.collector = collector

    def track_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Track HTTP request."""
        tags = {
            "method": method,
            "path": path,
            "status": str(status_code)
        }

        self.collector.increment("http.requests.total", tags=tags)
        self.collector.timing("http.request.duration", duration_ms, tags=tags)

        if status_code >= 500:
            self.collector.increment("http.errors.5xx", tags=tags)
        elif status_code >= 400:
            self.collector.increment("http.errors.4xx", tags=tags)

    def track_database_query(self, operation: str, duration_ms: float, success: bool):
        """Track database query."""
        tags = {
            "operation": operation,
            "success": str(success)
        }

        self.collector.increment("db.queries.total", tags=tags)
        self.collector.timing("db.query.duration", duration_ms, tags=tags)

    def track_cache_hit(self, cache_name: str, hit: bool):
        """Track cache hit/miss."""
        tags = {"cache": cache_name}

        if hit:
            self.collector.increment("cache.hits", tags=tags)
        else:
            self.collector.increment("cache.misses", tags=tags)

    def track_background_job(self, job_type: str, duration_ms: float, success: bool):
        """Track background job."""
        tags = {
            "job_type": job_type,
            "success": str(success)
        }

        self.collector.increment("jobs.total", tags=tags)
        self.collector.timing("jobs.duration", duration_ms, tags=tags)


# Global application metrics
app_metrics = ApplicationMetrics(metrics_collector)
