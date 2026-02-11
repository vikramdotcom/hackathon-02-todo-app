"""
Stream Processing System

Real-time stream processing with windowing and aggregation.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class StreamWindow:
    """Time-based window for stream processing."""

    def __init__(self, window_size_seconds: int):
        """Initialize stream window."""
        self.window_size = window_size_seconds
        self.events: deque = deque()

    def add_event(self, event: Dict[str, Any]):
        """Add event to window."""
        event["timestamp"] = datetime.utcnow()
        self.events.append(event)
        self._cleanup_old_events()

    def _cleanup_old_events(self):
        """Remove old events outside window."""
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_size)
        while self.events and self.events[0]["timestamp"] < cutoff:
            self.events.popleft()

    def get_events(self) -> List[Dict[str, Any]]:
        """Get events in window."""
        self._cleanup_old_events()
        return list(self.events)


class StreamProcessor:
    """Process event streams."""

    def __init__(self, name: str):
        """Initialize stream processor."""
        self.name = name
        self.window = StreamWindow(60)

    async def process_event(self, event: Dict[str, Any]):
        """Process stream event."""
        self.window.add_event(event)
        logger.info(f"Event processed: {self.name}")


stream_processor = StreamProcessor("default")
