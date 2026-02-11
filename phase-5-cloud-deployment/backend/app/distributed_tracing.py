"""
Distributed Tracing System

Implement distributed tracing for microservices.
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SpanKind(str, Enum):
    """Span kind types."""
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class Span:
    """Distributed tracing span."""

    def __init__(
        self,
        trace_id: str,
        span_id: str,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL
    ):
        """Initialize span."""
        self.trace_id = trace_id
        self.span_id = span_id
        self.operation_name = operation_name
        self.parent_span_id = parent_span_id
        self.kind = kind
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.tags: Dict[str, Any] = {}
        self.logs: List[Dict[str, Any]] = []
        self.status = "ok"

    def set_tag(self, key: str, value: Any):
        """Set span tag."""
        self.tags[key] = value

    def log(self, message: str, fields: Optional[Dict[str, Any]] = None):
        """Add log to span."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "fields": fields or {}
        }
        self.logs.append(log_entry)

    def finish(self):
        """Finish span."""
        self.end_time = datetime.utcnow()

    def get_duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if not self.end_time:
            return None

        duration = (self.end_time - self.start_time).total_seconds() * 1000
        return duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "operation_name": self.operation_name,
            "parent_span_id": self.parent_span_id,
            "kind": self.kind.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.get_duration_ms(),
            "tags": self.tags,
            "logs": self.logs,
            "status": self.status
        }


class Tracer:
    """Distributed tracer."""

    def __init__(self, service_name: str):
        """Initialize tracer."""
        self.service_name = service_name
        self.active_spans: Dict[str, Span] = {}
        self.completed_spans: List[Span] = []

    def start_span(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL
    ) -> Span:
        """Start new span."""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())

        span = Span(trace_id, span_id, operation_name, parent_span_id, kind)
        span.set_tag("service.name", self.service_name)

        self.active_spans[span_id] = span

        logger.info(
            f"Started span: {operation_name}",
            extra={
                "trace_id": trace_id,
                "span_id": span_id,
                "operation": operation_name
            }
        )

        return span

    def finish_span(self, span: Span):
        """Finish span."""
        span.finish()

        if span.span_id in self.active_spans:
            del self.active_spans[span.span_id]

        self.completed_spans.append(span)

        logger.info(
            f"Finished span: {span.operation_name}",
            extra={
                "trace_id": span.trace_id,
                "span_id": span.span_id,
                "duration_ms": span.get_duration_ms()
            }
        )

    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for trace."""
        return [
            span for span in self.completed_spans
            if span.trace_id == trace_id
        ]


class TraceContext:
    """Trace context for propagation."""

    def __init__(self, trace_id: str, span_id: str):
        """Initialize trace context."""
        self.trace_id = trace_id
        self.span_id = span_id

    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers."""
        return {
            "X-Trace-ID": self.trace_id,
            "X-Span-ID": self.span_id
        }

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional['TraceContext']:
        """Create from HTTP headers."""
        trace_id = headers.get("X-Trace-ID")
        span_id = headers.get("X-Span-ID")

        if trace_id and span_id:
            return cls(trace_id, span_id)

        return None


class SpanExporter:
    """Export spans to backend."""

    def __init__(self, endpoint: str):
        """Initialize span exporter."""
        self.endpoint = endpoint
        self.buffer: List[Span] = []
        self.batch_size = 100

    def export_span(self, span: Span):
        """Export span."""
        self.buffer.append(span)

        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self):
        """Flush buffered spans."""
        if not self.buffer:
            return

        # In production, send to tracing backend (Jaeger, Zipkin, etc.)
        logger.info(f"Exporting {len(self.buffer)} spans to {self.endpoint}")

        self.buffer.clear()


class TracingMiddleware:
    """Middleware for automatic tracing."""

    def __init__(self, tracer: Tracer):
        """Initialize tracing middleware."""
        self.tracer = tracer

    async def __call__(self, request):
        """Trace request."""
        # Extract trace context from headers
        context = TraceContext.from_headers(dict(request.headers))

        parent_span_id = context.span_id if context else None

        # Start span
        span = self.tracer.start_span(
            f"{request.method} {request.path}",
            parent_span_id,
            SpanKind.SERVER
        )

        # Add request tags
        span.set_tag("http.method", request.method)
        span.set_tag("http.url", str(request.url))
        span.set_tag("http.target", request.path)

        try:
            # Attach span to request
            request.span = span

            # Continue processing
            # In production, this would call next middleware/handler

        finally:
            # Finish span
            self.tracer.finish_span(span)


class DistributedTracer:
    """Distributed tracing coordinator."""

    def __init__(self):
        """Initialize distributed tracer."""
        self.tracers: Dict[str, Tracer] = {}
        self.exporter: Optional[SpanExporter] = None

    def get_tracer(self, service_name: str) -> Tracer:
        """Get or create tracer for service."""
        if service_name not in self.tracers:
            self.tracers[service_name] = Tracer(service_name)

        return self.tracers[service_name]

    def set_exporter(self, exporter: SpanExporter):
        """Set span exporter."""
        self.exporter = exporter

    def get_trace_tree(self, trace_id: str) -> Dict[str, Any]:
        """Get trace as tree structure."""
        # Collect all spans for trace
        all_spans = []
        for tracer in self.tracers.values():
            all_spans.extend(tracer.get_trace(trace_id))

        if not all_spans:
            return {}

        # Build tree
        spans_by_id = {span.span_id: span for span in all_spans}
        root_spans = [span for span in all_spans if not span.parent_span_id]

        def build_tree(span: Span) -> Dict[str, Any]:
            children = [
                build_tree(child)
                for child in all_spans
                if child.parent_span_id == span.span_id
            ]

            return {
                "span": span.to_dict(),
                "children": children
            }

        return {
            "trace_id": trace_id,
            "root_spans": [build_tree(span) for span in root_spans]
        }


class ServiceDependencyGraph:
    """Track service dependencies from traces."""

    def __init__(self):
        """Initialize dependency graph."""
        self.dependencies: Dict[str, set] = {}

    def record_dependency(self, from_service: str, to_service: str):
        """Record service dependency."""
        if from_service not in self.dependencies:
            self.dependencies[from_service] = set()

        self.dependencies[from_service].add(to_service)

    def get_dependencies(self, service: str) -> List[str]:
        """Get dependencies for service."""
        return list(self.dependencies.get(service, set()))

    def get_graph(self) -> Dict[str, List[str]]:
        """Get full dependency graph."""
        return {
            service: list(deps)
            for service, deps in self.dependencies.items()
        }


class TraceAnalyzer:
    """Analyze traces for insights."""

    def __init__(self, distributed_tracer: DistributedTracer):
        """Initialize trace analyzer."""
        self.distributed_tracer = distributed_tracer

    def find_slow_spans(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        """Find slow spans across all traces."""
        slow_spans = []

        for tracer in self.distributed_tracer.tracers.values():
            for span in tracer.completed_spans:
                duration = span.get_duration_ms()
                if duration and duration > threshold_ms:
                    slow_spans.append(span.to_dict())

        return sorted(slow_spans, key=lambda s: s["duration_ms"], reverse=True)

    def get_service_latencies(self) -> Dict[str, Dict[str, float]]:
        """Get latency statistics by service."""
        latencies: Dict[str, List[float]] = {}

        for service_name, tracer in self.distributed_tracer.tracers.items():
            service_durations = []

            for span in tracer.completed_spans:
                duration = span.get_duration_ms()
                if duration:
                    service_durations.append(duration)

            if service_durations:
                latencies[service_name] = service_durations

        # Calculate statistics
        stats = {}
        for service, durations in latencies.items():
            stats[service] = {
                "count": len(durations),
                "avg_ms": sum(durations) / len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "p95_ms": self._percentile(durations, 95),
                "p99_ms": self._percentile(durations, 99)
            }

        return stats

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


class SamplingStrategy:
    """Trace sampling strategy."""

    def __init__(self, sample_rate: float = 1.0):
        """Initialize sampling strategy."""
        self.sample_rate = sample_rate

    def should_sample(self) -> bool:
        """Determine if trace should be sampled."""
        import random
        return random.random() < self.sample_rate


# Global instances
distributed_tracer = DistributedTracer()
service_dependency_graph = ServiceDependencyGraph()
trace_analyzer = TraceAnalyzer(distributed_tracer)
sampling_strategy = SamplingStrategy(sample_rate=1.0)


# Helper functions
def get_tracer(service_name: str) -> Tracer:
    """Get tracer for service."""
    return distributed_tracer.get_tracer(service_name)


def start_span(
    service_name: str,
    operation_name: str,
    parent_span_id: Optional[str] = None
) -> Span:
    """Start new span."""
    tracer = get_tracer(service_name)
    return tracer.start_span(operation_name, parent_span_id)


def get_trace_tree(trace_id: str) -> Dict[str, Any]:
    """Get trace tree."""
    return distributed_tracer.get_trace_tree(trace_id)
