"""
Request Tracing System

Detailed request tracing for debugging and monitoring.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class TraceEvent:
    """Trace event."""

    def __init__(self, event_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Initialize trace event."""
        self.event_type = event_type
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


class RequestTrace:
    """Request trace."""

    def __init__(self, trace_id: str):
        """Initialize request trace."""
        self.trace_id = trace_id
        self.events: List[TraceEvent] = []
        self.started_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None

    def add_event(self, event_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Add trace event."""
        event = TraceEvent(event_type, message, metadata)
        self.events.append(event)

    def complete(self):
        """Mark trace as complete."""
        self.completed_at = datetime.utcnow()

    def get_duration_ms(self) -> float:
        """Get trace duration in milliseconds."""
        end = self.completed_at or datetime.utcnow()
        return (end - self.started_at).total_seconds() * 1000


class RequestTracer:
    """Trace requests."""

    def __init__(self):
        """Initialize request tracer."""
        self.traces: Dict[str, RequestTrace] = {}

    def start_trace(self, trace_id: str) -> RequestTrace:
        """Start new trace."""
        trace = RequestTrace(trace_id)
        self.traces[trace_id] = trace
        return trace

    def get_trace(self, trace_id: str) -> Optional[RequestTrace]:
        """Get trace by ID."""
        return self.traces.get(trace_id)


request_tracer = RequestTracer()
