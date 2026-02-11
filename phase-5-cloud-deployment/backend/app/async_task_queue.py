"""
Async Task Queue System

Background task processing with priority queues.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)


class TaskPriority(int, Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class Task:
    """Background task."""

    def __init__(self, task_id: str, func: Callable, priority: TaskPriority = TaskPriority.NORMAL):
        """Initialize task."""
        self.task_id = task_id
        self.func = func
        self.priority = priority
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.status = "pending"
        self.result: Optional[Any] = None
        self.error: Optional[str] = None

    async def execute(self):
        """Execute task."""
        self.status = "running"
        self.started_at = datetime.utcnow()

        try:
            self.result = await self.func()
            self.status = "completed"
        except Exception as e:
            self.error = str(e)
            self.status = "failed"
            logger.error(f"Task failed: {self.task_id} - {e}")

        self.completed_at = datetime.utcnow()


class TaskQueue:
    """Async task queue."""

    def __init__(self, max_workers: int = 5):
        """Initialize task queue."""
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.workers: List[asyncio.Task] = []

    async def enqueue(self, task: Task):
        """Enqueue task."""
        self.tasks[task.task_id] = task
        await self.queue.put((-task.priority.value, task))
        logger.info(f"Task enqueued: {task.task_id} (priority: {task.priority.name})")

    async def worker(self):
        """Worker to process tasks."""
        while True:
            _, task = await self.queue.get()
            await task.execute()
            self.queue.task_done()

    async def start_workers(self):
        """Start worker tasks."""
        self.workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.max_workers)
        ]


task_queue = TaskQueue()
