"""
Background Job Processing System

Provides background job queue and worker management for async tasks.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job status types."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(str, Enum):
    """Job priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Job:
    """Background job."""

    def __init__(
        self,
        id: str,
        task_name: str,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
        timeout: int = 300,
        scheduled_at: Optional[datetime] = None
    ):
        """
        Initialize job.

        Args:
            id: Job ID
            task_name: Task function name
            args: Positional arguments
            kwargs: Keyword arguments
            priority: Job priority
            max_retries: Maximum retry attempts
            timeout: Timeout in seconds
            scheduled_at: When to run the job
        """
        self.id = id
        self.task_name = task_name
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.max_retries = max_retries
        self.timeout = timeout
        self.scheduled_at = scheduled_at or datetime.utcnow()

        self.status = JobStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.retry_count = 0
        self.result: Optional[Any] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "task_name": self.task_name,
            "args": self.args,
            "kwargs": self.kwargs,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "result": self.result,
            "error": self.error
        }


class JobQueue:
    """Job queue with priority support."""

    def __init__(self):
        """Initialize job queue."""
        self.jobs: Dict[str, Job] = {}
        self.priority_order = {
            JobPriority.CRITICAL: 0,
            JobPriority.HIGH: 1,
            JobPriority.NORMAL: 2,
            JobPriority.LOW: 3
        }

    def enqueue(self, job: Job):
        """
        Add job to queue.

        Args:
            job: Job to enqueue
        """
        self.jobs[job.id] = job
        logger.info(
            f"Enqueued job {job.id}",
            extra={
                "job_id": job.id,
                "task_name": job.task_name,
                "priority": job.priority
            }
        )

    def dequeue(self) -> Optional[Job]:
        """
        Get next job from queue.

        Returns:
            Next job or None
        """
        # Get pending jobs that are ready to run
        ready_jobs = [
            job for job in self.jobs.values()
            if job.status == JobStatus.PENDING
            and job.scheduled_at <= datetime.utcnow()
        ]

        if not ready_jobs:
            return None

        # Sort by priority, then by created_at
        ready_jobs.sort(
            key=lambda j: (
                self.priority_order[j.priority],
                j.created_at
            )
        )

        return ready_jobs[0]

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job or None
        """
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.

        Args:
            job_id: Job ID

        Returns:
            True if cancelled
        """
        job = self.jobs.get(job_id)

        if job and job.status == JobStatus.PENDING:
            job.status = JobStatus.CANCELLED
            logger.info(f"Cancelled job {job_id}")
            return True

        return False

    def get_jobs(
        self,
        status: Optional[JobStatus] = None,
        task_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Job]:
        """
        Get jobs with filters.

        Args:
            status: Filter by status
            task_name: Filter by task name
            limit: Maximum jobs to return

        Returns:
            List of jobs
        """
        jobs = list(self.jobs.values())

        if status:
            jobs = [j for j in jobs if j.status == status]

        if task_name:
            jobs = [j for j in jobs if j.task_name == task_name]

        # Sort by created_at descending
        jobs.sort(key=lambda j: j.created_at, reverse=True)

        return jobs[:limit]

    def cleanup_old_jobs(self, days: int = 7):
        """
        Remove old completed/failed jobs.

        Args:
            days: Days to keep
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        removed = 0

        for job_id, job in list(self.jobs.items()):
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                if job.completed_at and job.completed_at < cutoff:
                    del self.jobs[job_id]
                    removed += 1

        if removed > 0:
            logger.info(f"Cleaned up {removed} old jobs")


class Worker:
    """Background job worker."""

    def __init__(
        self,
        queue: JobQueue,
        tasks: Dict[str, Callable],
        worker_id: str = None
    ):
        """
        Initialize worker.

        Args:
            queue: Job queue
            tasks: Dictionary of task name to function
            worker_id: Worker identifier
        """
        self.queue = queue
        self.tasks = tasks
        self.worker_id = worker_id or str(uuid.uuid4())
        self.running = False
        self.current_job: Optional[Job] = None

    async def start(self):
        """Start worker."""
        self.running = True
        logger.info(f"Worker {self.worker_id} started")

        while self.running:
            try:
                job = self.queue.dequeue()

                if job:
                    await self._process_job(job)
                else:
                    # No jobs available, wait a bit
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(
                    f"Worker {self.worker_id} error: {e}",
                    exc_info=True
                )
                await asyncio.sleep(1)

    def stop(self):
        """Stop worker."""
        self.running = False
        logger.info(f"Worker {self.worker_id} stopped")

    async def _process_job(self, job: Job):
        """
        Process a job.

        Args:
            job: Job to process
        """
        self.current_job = job
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()

        logger.info(
            f"Worker {self.worker_id} processing job {job.id}",
            extra={
                "worker_id": self.worker_id,
                "job_id": job.id,
                "task_name": job.task_name
            }
        )

        try:
            # Get task function
            task_func = self.tasks.get(job.task_name)

            if not task_func:
                raise ValueError(f"Task not found: {job.task_name}")

            # Execute task with timeout
            result = await asyncio.wait_for(
                task_func(*job.args, **job.kwargs),
                timeout=job.timeout
            )

            # Job completed successfully
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.result = result

            logger.info(
                f"Job {job.id} completed successfully",
                extra={
                    "job_id": job.id,
                    "duration": (job.completed_at - job.started_at).total_seconds()
                }
            )

        except asyncio.TimeoutError:
            job.error = f"Job timed out after {job.timeout}s"
            await self._handle_job_failure(job)

        except Exception as e:
            job.error = str(e)
            await self._handle_job_failure(job)

        finally:
            self.current_job = None

    async def _handle_job_failure(self, job: Job):
        """
        Handle job failure with retry logic.

        Args:
            job: Failed job
        """
        job.retry_count += 1

        if job.retry_count < job.max_retries:
            # Retry job
            job.status = JobStatus.RETRYING
            job.scheduled_at = datetime.utcnow() + timedelta(
                seconds=60 * (2 ** job.retry_count)  # Exponential backoff
            )

            logger.warning(
                f"Job {job.id} failed, retrying (attempt {job.retry_count}/{job.max_retries})",
                extra={
                    "job_id": job.id,
                    "error": job.error,
                    "next_retry": job.scheduled_at.isoformat()
                }
            )

            # Reset to pending for retry
            job.status = JobStatus.PENDING

        else:
            # Max retries reached
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()

            logger.error(
                f"Job {job.id} failed after {job.max_retries} retries",
                extra={
                    "job_id": job.id,
                    "error": job.error
                }
            )


class JobScheduler:
    """Schedule and manage background jobs."""

    def __init__(self, queue: JobQueue, tasks: Dict[str, Callable]):
        """
        Initialize scheduler.

        Args:
            queue: Job queue
            tasks: Available tasks
        """
        self.queue = queue
        self.tasks = tasks
        self.workers: List[Worker] = []

    def schedule(
        self,
        task_name: str,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        priority: JobPriority = JobPriority.NORMAL,
        delay: int = 0,
        **job_options
    ) -> Job:
        """
        Schedule a job.

        Args:
            task_name: Task function name
            args: Positional arguments
            kwargs: Keyword arguments
            priority: Job priority
            delay: Delay in seconds
            **job_options: Additional job options

        Returns:
            Created job
        """
        job_id = str(uuid.uuid4())
        scheduled_at = datetime.utcnow() + timedelta(seconds=delay)

        job = Job(
            id=job_id,
            task_name=task_name,
            args=args,
            kwargs=kwargs,
            priority=priority,
            scheduled_at=scheduled_at,
            **job_options
        )

        self.queue.enqueue(job)

        return job

    def start_workers(self, num_workers: int = 4):
        """
        Start worker pool.

        Args:
            num_workers: Number of workers to start
        """
        for i in range(num_workers):
            worker = Worker(
                queue=self.queue,
                tasks=self.tasks,
                worker_id=f"worker-{i+1}"
            )
            self.workers.append(worker)

            # Start worker in background
            asyncio.create_task(worker.start())

        logger.info(f"Started {num_workers} workers")

    def stop_workers(self):
        """Stop all workers."""
        for worker in self.workers:
            worker.stop()

        self.workers.clear()
        logger.info("Stopped all workers")


# Global job queue and scheduler
job_queue = JobQueue()
job_scheduler = None  # Initialize with tasks


# Example task functions
async def send_email_task(to: str, subject: str, body: str):
    """Example: Send email task."""
    logger.info(f"Sending email to {to}: {subject}")
    await asyncio.sleep(1)  # Simulate email sending
    return {"status": "sent", "to": to}


async def process_webhook_task(webhook_id: int, event: str, payload: Dict[str, Any]):
    """Example: Process webhook task."""
    logger.info(f"Processing webhook {webhook_id} for event {event}")
    await asyncio.sleep(0.5)  # Simulate processing
    return {"status": "processed", "webhook_id": webhook_id}


async def cleanup_old_data_task(days: int = 30):
    """Example: Cleanup old data task."""
    logger.info(f"Cleaning up data older than {days} days")
    await asyncio.sleep(2)  # Simulate cleanup
    return {"status": "completed", "days": days}


# Register tasks
AVAILABLE_TASKS = {
    "send_email": send_email_task,
    "process_webhook": process_webhook_task,
    "cleanup_old_data": cleanup_old_data_task
}
