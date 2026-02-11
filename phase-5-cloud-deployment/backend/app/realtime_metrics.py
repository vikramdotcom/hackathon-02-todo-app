"""
Real-time Metrics and Monitoring Dashboard

Collect and visualize real-time application metrics.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class MetricType:
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class Metric:
    """Base metric class."""

    def __init__(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Initialize metric."""
        self.name = name
        self.labels = labels or {}
        self.created_at = datetime.utcnow()


class Counter(Metric):
    """Counter metric that only increases."""

    def __init__(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Initialize counter."""
        super().__init__(name, labels)
        self.value = 0

    def inc(self, amount: float = 1):
        """Increment counter."""
        self.value += amount

    def get_value(self) -> float:
        """Get counter value."""
        return self.value


class Gauge(Metric):
    """Gauge metric that can go up and down."""

    def __init__(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Initialize gauge."""
        super().__init__(name, labels)
        self.value = 0

    def set(self, value: float):
        """Set gauge value."""
        self.value = value

    def inc(self, amount: float = 1):
        """Increment gauge."""
        self.value += amount

    def dec(self, amount: float = 1):
        """Decrement gauge."""
        self.value -= amount

    def get_value(self) -> float:
        """Get gauge value."""
        return self.value


class Histogram(Metric):
    """Histogram metric for distributions."""

    def __init__(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Initialize histogram."""
        super().__init__(name, labels)
        self.observations: List[float] = []
        self.sum = 0.0
        self.count = 0

    def observe(self, value: float):
        """Observe a value."""
        self.observations.append(value)
        self.sum += value
        self.count += 1

    def get_percentile(self, percentile: float) -> float:
        """Get percentile value."""
        if not self.observations:
            return 0.0

        sorted_obs = sorted(self.observations)
        index = int(len(sorted_obs) * percentile / 100)
        return sorted_obs[min(index, len(sorted_obs) - 1)]

    def get_stats(self) -> Dict[str, float]:
        """Get histogram statistics."""
        if not self.observations:
            return {
                "count": 0,
                "sum": 0,
                "mean": 0,
                "min": 0,
                "max": 0,
                "p50": 0,
                "p95": 0,
                "p99": 0
            }

        return {
            "count": self.count,
            "sum": self.sum,
            "mean": self.sum / self.count,
            "min": min(self.observations),
            "max": max(self.observations),
            "p50": self.get_percentile(50),
            "p95": self.get_percentile(95),
            "p99": self.get_percentile(99)
        }


class TimeSeriesMetric:
    """Time series metric with windowing."""

    def __init__(self, name: str, window_size: int = 60):
        """Initialize time series metric."""
        self.name = name
        self.window_size = window_size
        self.data_points: deque = deque(maxlen=window_size)

    def record(self, value: float, timestamp: Optional[datetime] = None):
        """Record data point."""
        ts = timestamp or datetime.utcnow()
        self.data_points.append({
            "timestamp": ts,
            "value": value
        })

    def get_recent_values(self, seconds: int = 60) -> List[float]:
        """Get recent values."""
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        return [
            dp["value"] for dp in self.data_points
            if dp["timestamp"] > cutoff
        ]

    def get_average(self, seconds: int = 60) -> float:
        """Get average over time window."""
        values = self.get_recent_values(seconds)
        return statistics.mean(values) if values else 0.0

    def get_rate(self, seconds: int = 60) -> float:
        """Get rate of change."""
        values = self.get_recent_values(seconds)
        if len(values) < 2:
            return 0.0

        return (values[-1] - values[0]) / seconds


class MetricsRegistry:
    """Registry for all metrics."""

    def __init__(self):
        """Initialize metrics registry."""
        self.counters: Dict[str, Counter] = {}
        self.gauges: Dict[str, Gauge] = {}
        self.histograms: Dict[str, Histogram] = {}
        self.time_series: Dict[str, TimeSeriesMetric] = {}

    def counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> Counter:
        """Get or create counter."""
        key = self._make_key(name, labels)
        if key not in self.counters:
            self.counters[key] = Counter(name, labels)
        return self.counters[key]

    def gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> Gauge:
        """Get or create gauge."""
        key = self._make_key(name, labels)
        if key not in self.gauges:
            self.gauges[key] = Gauge(name, labels)
        return self.gauges[key]

    def histogram(self, name: str, labels: Optional[Dict[str, str]] = None) -> Histogram:
        """Get or create histogram."""
        key = self._make_key(name, labels)
        if key not in self.histograms:
            self.histograms[key] = Histogram(name, labels)
        return self.histograms[key]

    def time_series(self, name: str) -> TimeSeriesMetric:
        """Get or create time series metric."""
        if name not in self.time_series:
            self.time_series[name] = TimeSeriesMetric(name)
        return self.time_series[name]

    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Make unique key for metric."""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            "counters": {k: c.get_value() for k, c in self.counters.items()},
            "gauges": {k: g.get_value() for k, g in self.gauges.items()},
            "histograms": {k: h.get_stats() for k, h in self.histograms.items()}
        }


class DashboardWidget:
    """Dashboard widget for displaying metrics."""

    def __init__(self, widget_id: str, widget_type: str, title: str):
        """Initialize dashboard widget."""
        self.widget_id = widget_id
        self.widget_type = widget_type
        self.title = title
        self.metrics: List[str] = []
        self.config: Dict[str, Any] = {}

    def add_metric(self, metric_name: str):
        """Add metric to widget."""
        self.metrics.append(metric_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "widget_id": self.widget_id,
            "type": self.widget_type,
            "title": self.title,
            "metrics": self.metrics,
            "config": self.config
        }


class Dashboard:
    """Metrics dashboard."""

    def __init__(self, name: str):
        """Initialize dashboard."""
        self.name = name
        self.widgets: Dict[str, DashboardWidget] = {}
        self.created_at = datetime.utcnow()

    def add_widget(self, widget: DashboardWidget):
        """Add widget to dashboard."""
        self.widgets[widget.widget_id] = widget

    def get_widget(self, widget_id: str) -> Optional[DashboardWidget]:
        """Get widget by ID."""
        return self.widgets.get(widget_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "widgets": [w.to_dict() for w in self.widgets.values()]
        }


class AlertRule:
    """Alert rule for metrics."""

    def __init__(
        self,
        name: str,
        metric_name: str,
        condition: str,
        threshold: float,
        duration_seconds: int = 60
    ):
        """Initialize alert rule."""
        self.name = name
        self.metric_name = metric_name
        self.condition = condition  # "gt", "lt", "eq"
        self.threshold = threshold
        self.duration_seconds = duration_seconds
        self.triggered = False
        self.triggered_at: Optional[datetime] = None

    def evaluate(self, metric_value: float) -> bool:
        """Evaluate alert rule."""
        if self.condition == "gt":
            return metric_value > self.threshold
        elif self.condition == "lt":
            return metric_value < self.threshold
        elif self.condition == "eq":
            return metric_value == self.threshold
        return False

    def trigger(self):
        """Trigger alert."""
        if not self.triggered:
            self.triggered = True
            self.triggered_at = datetime.utcnow()
            logger.warning(
                f"Alert triggered: {self.name}",
                extra={"alert": self.name, "metric": self.metric_name}
            )

    def resolve(self):
        """Resolve alert."""
        if self.triggered:
            self.triggered = False
            logger.info(f"Alert resolved: {self.name}")


class AlertManager:
    """Manage metric alerts."""

    def __init__(self, metrics_registry: MetricsRegistry):
        """Initialize alert manager."""
        self.metrics_registry = metrics_registry
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: List[str] = []

    def add_rule(self, rule: AlertRule):
        """Add alert rule."""
        self.rules[rule.name] = rule

    def evaluate_rules(self):
        """Evaluate all alert rules."""
        for rule in self.rules.values():
            # Get metric value
            metric_value = self._get_metric_value(rule.metric_name)

            if metric_value is None:
                continue

            # Evaluate condition
            if rule.evaluate(metric_value):
                if not rule.triggered:
                    rule.trigger()
                    self.active_alerts.append(rule.name)
            else:
                if rule.triggered:
                    rule.resolve()
                    if rule.name in self.active_alerts:
                        self.active_alerts.remove(rule.name)

    def _get_metric_value(self, metric_name: str) -> Optional[float]:
        """Get metric value."""
        if metric_name in self.metrics_registry.counters:
            return self.metrics_registry.counters[metric_name].get_value()
        elif metric_name in self.metrics_registry.gauges:
            return self.metrics_registry.gauges[metric_name].get_value()
        return None

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""
        return [
            {
                "name": rule.name,
                "metric": rule.metric_name,
                "threshold": rule.threshold,
                "triggered_at": rule.triggered_at.isoformat() if rule.triggered_at else None
            }
            for name, rule in self.rules.items()
            if name in self.active_alerts
        ]


class MetricsExporter:
    """Export metrics in various formats."""

    def __init__(self, metrics_registry: MetricsRegistry):
        """Initialize metrics exporter."""
        self.metrics_registry = metrics_registry

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Counters
        for key, counter in self.metrics_registry.counters.items():
            lines.append(f"# TYPE {counter.name} counter")
            lines.append(f"{key} {counter.get_value()}")

        # Gauges
        for key, gauge in self.metrics_registry.gauges.items():
            lines.append(f"# TYPE {gauge.name} gauge")
            lines.append(f"{key} {gauge.get_value()}")

        # Histograms
        for key, histogram in self.metrics_registry.histograms.items():
            stats = histogram.get_stats()
            lines.append(f"# TYPE {histogram.name} histogram")
            lines.append(f"{key}_count {stats['count']}")
            lines.append(f"{key}_sum {stats['sum']}")

        return "\n".join(lines)

    def export_json(self) -> Dict[str, Any]:
        """Export metrics in JSON format."""
        return self.metrics_registry.get_all_metrics()


class HealthCheckMonitor:
    """Monitor application health."""

    def __init__(self):
        """Initialize health check monitor."""
        self.checks: Dict[str, Dict[str, Any]] = {}

    def register_check(self, name: str, check_func):
        """Register health check."""
        self.checks[name] = {
            "function": check_func,
            "last_result": None,
            "last_check": None
        }

    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        for name, check in self.checks.items():
            try:
                result = await check["function"]()
                check["last_result"] = result
                check["last_check"] = datetime.utcnow()

                results["checks"][name] = {
                    "status": "healthy" if result else "unhealthy",
                    "timestamp": check["last_check"].isoformat()
                }

                if not result:
                    results["status"] = "unhealthy"

            except Exception as e:
                logger.error(f"Health check failed: {name}: {e}")
                results["checks"][name] = {
                    "status": "error",
                    "error": str(e)
                }
                results["status"] = "unhealthy"

        return results


# Global instances
metrics_registry = MetricsRegistry()
alert_manager = AlertManager(metrics_registry)
metrics_exporter = MetricsExporter(metrics_registry)
health_check_monitor = HealthCheckMonitor()


# Helper functions
def counter(name: str, labels: Optional[Dict[str, str]] = None) -> Counter:
    """Get counter metric."""
    return metrics_registry.counter(name, labels)


def gauge(name: str, labels: Optional[Dict[str, str]] = None) -> Gauge:
    """Get gauge metric."""
    return metrics_registry.gauge(name, labels)


def histogram(name: str, labels: Optional[Dict[str, str]] = None) -> Histogram:
    """Get histogram metric."""
    return metrics_registry.histogram(name, labels)


def time_series(name: str) -> TimeSeriesMetric:
    """Get time series metric."""
    return metrics_registry.time_series(name)


def create_dashboard(name: str) -> Dashboard:
    """Create dashboard."""
    return Dashboard(name)


def add_alert_rule(
    name: str,
    metric_name: str,
    condition: str,
    threshold: float
):
    """Add alert rule."""
    rule = AlertRule(name, metric_name, condition, threshold)
    alert_manager.add_rule(rule)


async def get_health_status() -> Dict[str, Any]:
    """Get health status."""
    return await health_check_monitor.run_checks()


# Example usage
http_requests_total = counter("http_requests_total", {"method": "GET"})
active_connections = gauge("active_connections")
request_duration = histogram("request_duration_seconds")
cpu_usage = time_series("cpu_usage_percent")
