"""
Request Correlation System

Track requests across distributed services with correlation IDs.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class CorrelationContext:
    """Correlation context for distributed tracing."""

    def __init__(self, correlation_id: Optional[str] = None):
        """Initialize correlation context."""
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.parent_id: Optional[str] = None
        self.service_name: Optional[str] = None
        self.started_at = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}

    def add_metadata(self, key: str, value: Any):
        """Add metadata to context."""
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "correlation_id": self.correlation_id,
            "parent_id": self.parent_id,
            "service_name": self.service_name,
            "started_at": self.started_at.isoformat(),
            "metadata": self.metadata
        }


class CorrelationManager:
    """Manage correlation contexts."""

    def __init__(self):
        """Initialize correlation manager."""
        self.contexts: Dict[str, CorrelationContext] = {}

    def create_context(self, correlation_id: Optional[str] = None) -> CorrelationContext:
        """Create new correlation context."""
        context = CorrelationContext(correlation_id)
        self.contexts[context.correlation_id] = context
        return context

    def get_context(self, correlation_id: str) -> Optional[CorrelationContext]:
        """Get correlation context."""
        return self.contexts.get(correlation_id)


correlation_manager = CorrelationManager()
