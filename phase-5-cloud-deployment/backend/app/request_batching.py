"""
Request Batching System

Batch multiple requests for efficient processing.
"""

import logging
from typing import List, Any, Callable
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class RequestBatcher:
    """Batch requests for efficient processing."""

    def __init__(self, batch_size: int = 10, max_wait_ms: int = 100):
        """Initialize request batcher."""
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.pending_requests: List[Any] = []
        self.processor: Callable = None

    def set_processor(self, processor: Callable):
        """Set batch processor function."""
        self.processor = processor

    async def add_request(self, request: Any) -> Any:
        """Add request to batch."""
        self.pending_requests.append(request)

        if len(self.pending_requests) >= self.batch_size:
            return await self._process_batch()

        await asyncio.sleep(self.max_wait_ms / 1000)
        return await self._process_batch()

    async def _process_batch(self):
        """Process current batch."""
        if not self.pending_requests:
            return None

        batch = self.pending_requests[:]
        self.pending_requests.clear()

        logger.info(f"Processing batch of {len(batch)} requests")
        return await self.processor(batch)


request_batcher = RequestBatcher()
