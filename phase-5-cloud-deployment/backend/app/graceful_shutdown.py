"""
Graceful Shutdown Handler

Handle application shutdown gracefully with cleanup.
"""

import logging
import signal
import asyncio
from typing import List, Callable

logger = logging.getLogger(__name__)


class ShutdownHandler:
    """Handle graceful shutdown."""

    def __init__(self):
        """Initialize shutdown handler."""
        self.shutdown_hooks: List[Callable] = []
        self.is_shutting_down = False

    def register_hook(self, hook: Callable):
        """Register shutdown hook."""
        self.shutdown_hooks.append(hook)

    async def shutdown(self):
        """Execute graceful shutdown."""
        if self.is_shutting_down:
            return

        self.is_shutting_down = True
        logger.info("Starting graceful shutdown...")

        for hook in self.shutdown_hooks:
            try:
                await hook()
            except Exception as e:
                logger.error(f"Shutdown hook failed: {e}")

        logger.info("Graceful shutdown completed")

    def setup_signal_handlers(self):
        """Setup signal handlers for shutdown."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signal."""
        logger.info(f"Received signal {signum}")
        asyncio.create_task(self.shutdown())


shutdown_handler = ShutdownHandler()
