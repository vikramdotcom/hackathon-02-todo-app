"""
Tests for Background Job Processing System
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from app.background_jobs import (
    Job,
    JobStatus,
    JobPriority,
    JobQueue,
    Worker,
    JobScheduler
)


class TestJob:
    """Test Job class."""

    def test_job_initialization(self):
        """Test job initialization."""
        job = Job(
            id="job-1",
            task_name="test_task",
            args=(1, 2),
            kwargs={"key": "value"},
            priority=JobPriority.HIGH
        )

        assert job.id == "job-1"
        assert job.task_name == "test_task"
        assert job.args == (1, 2)
        assert job.kwargs == {"key": "value"}
        assert job.priority == JobPriority.HIGH
        assert job.status == JobStatus.PENDING

    def test_job_default_values(self):
        """Test job default values."""
        job = Job(id="job-1", task_name="test_task")

        assert job.args == ()
        assert job.kwargs == {}
        assert job.priority == JobPriority.NORMAL
        assert job.max_retries == 3
        assert job.timeout == 300

    def test_job_to_dict(self):
        """Test converting job to dictionary."""
        job = Job(id="job-1", task_name="test_task")

        job_dict = job.to_dict()

        assert job_dict["id"] == "job-1"
        assert job_dict["task_name"] == "test_task"
        assert job_dict["status"] == JobStatus.PENDING
        assert "created_at" in job_dict


class TestJobQueue:
    """Test JobQueue class."""

    def test_queue_initialization(self):
        """Test queue initialization."""
        queue = JobQueue()

        assert queue.jobs == {}

    def test_enqueue_job(self):
        """Test enqueueing a job."""
        queue = JobQueue()
        job = Job(id="job-1", task_name="test_task")

        queue.enqueue(job)

        assert "job-1" in queue.jobs
        assert queue.jobs["job-1"] == job

    def test_dequeue_job(self):
        """Test dequeueing a job."""
        queue = JobQueue()
        job = Job(id="job-1", task_name="test_task")
        queue.enqueue(job)

        dequeued = queue.dequeue()

        assert dequeued == job

    def test_dequeue_empty_queue(self):
        """Test dequeueing from empty queue."""
        queue = JobQueue()

        assert queue.dequeue() is None

    def test_dequeue_priority_order(self):
        """Test jobs are dequeued by priority."""
        queue = JobQueue()

        job_low = Job(id="job-1", task_name="test", priority=JobPriority.LOW)
        job_high = Job(id="job-2", task_name="test", priority=JobPriority.HIGH)
        job_normal = Job(id="job-3", task_name="test", priority=JobPriority.NORMAL)

        queue.enqueue(job_low)
        queue.enqueue(job_high)
        queue.enqueue(job_normal)

        # Should dequeue high priority first
        assert queue.dequeue() == job_high

    def test_dequeue_scheduled_jobs(self):
        """Test only ready jobs are dequeued."""
        queue = JobQueue()

        # Job scheduled in the future
        future_job = Job(
            id="job-1",
            task_name="test",
            scheduled_at=datetime.utcnow() + timedelta(hours=1)
        )

        # Job ready now
        ready_job = Job(id="job-2", task_name="test")

        queue.enqueue(future_job)
        queue.enqueue(ready_job)

        # Should only dequeue ready job
        assert queue.dequeue() == ready_job

    def test_get_job(self):
        """Test getting job by ID."""
        queue = JobQueue()
        job = Job(id="job-1", task_name="test_task")
        queue.enqueue(job)

        retrieved = queue.get_job("job-1")

        assert retrieved == job

    def test_get_job_not_found(self):
        """Test getting non-existent job."""
        queue = JobQueue()

        assert queue.get_job("nonexistent") is None

    def test_cancel_job(self):
        """Test cancelling a job."""
        queue = JobQueue()
        job = Job(id="job-1", task_name="test_task")
        queue.enqueue(job)

        result = queue.cancel_job("job-1")

        assert result is True
        assert job.status == JobStatus.CANCELLED

    def test_cancel_running_job(self):
        """Test cannot cancel running job."""
        queue = JobQueue()
        job = Job(id="job-1", task_name="test_task")
        job.status = JobStatus.RUNNING
        queue.enqueue(job)

        result = queue.cancel_job("job-1")

        assert result is False

    def test_get_jobs_all(self):
        """Test getting all jobs."""
        queue = JobQueue()

        job1 = Job(id="job-1", task_name="test")
        job2 = Job(id="job-2", task_name="test")

        queue.enqueue(job1)
        queue.enqueue(job2)

        jobs = queue.get_jobs()

        assert len(jobs) == 2

    def test_get_jobs_by_status(self):
        """Test filtering jobs by status."""
        queue = JobQueue()

        job1 = Job(id="job-1", task_name="test")
        job1.status = JobStatus.COMPLETED

        job2 = Job(id="job-2", task_name="test")
        job2.status = JobStatus.PENDING

        queue.enqueue(job1)
        queue.enqueue(job2)

        jobs = queue.get_jobs(status=JobStatus.PENDING)

        assert len(jobs) == 1
        assert jobs[0].status == JobStatus.PENDING

    def test_get_jobs_by_task_name(self):
        """Test filtering jobs by task name."""
        queue = JobQueue()

        job1 = Job(id="job-1", task_name="task_a")
        job2 = Job(id="job-2", task_name="task_b")

        queue.enqueue(job1)
        queue.enqueue(job2)

        jobs = queue.get_jobs(task_name="task_a")

        assert len(jobs) == 1
        assert jobs[0].task_name == "task_a"

    def test_cleanup_old_jobs(self):
        """Test cleaning up old jobs."""
        queue = JobQueue()

        # Old completed job
        old_job = Job(id="job-1", task_name="test")
        old_job.status = JobStatus.COMPLETED
        old_job.completed_at = datetime.utcnow() - timedelta(days=10)

        # Recent job
        recent_job = Job(id="job-2", task_name="test")
        recent_job.status = JobStatus.COMPLETED
        recent_job.completed_at = datetime.utcnow()

        queue.enqueue(old_job)
        queue.enqueue(recent_job)

        queue.cleanup_old_jobs(days=7)

        assert "job-1" not in queue.jobs
        assert "job-2" in queue.jobs


class TestWorker:
    """Test Worker class."""

    def test_worker_initialization(self):
        """Test worker initialization."""
        queue = JobQueue()
        tasks = {}

        worker = Worker(queue=queue, tasks=tasks)

        assert worker.queue == queue
        assert worker.tasks == tasks
        assert worker.running is False
        assert worker.current_job is None

    @pytest.mark.asyncio
    async def test_worker_process_job_success(self):
        """Test worker processing successful job."""
        queue = JobQueue()

        async def test_task():
            return "success"

        tasks = {"test_task": test_task}
        worker = Worker(queue=queue, tasks=tasks)

        job = Job(id="job-1", task_name="test_task")
        queue.enqueue(job)

        await worker._process_job(job)

        assert job.status == JobStatus.COMPLETED
        assert job.result == "success"

    @pytest.mark.asyncio
    async def test_worker_process_job_failure(self):
        """Test worker processing failed job."""
        queue = JobQueue()

        async def failing_task():
            raise ValueError("Test error")

        tasks = {"test_task": failing_task}
        worker = Worker(queue=queue, tasks=tasks)

        job = Job(id="job-1", task_name="test_task", max_retries=1)
        queue.enqueue(job)

        await worker._process_job(job)

        assert job.status == JobStatus.PENDING  # Retrying
        assert job.retry_count == 1

    @pytest.mark.asyncio
    async def test_worker_process_job_max_retries(self):
        """Test job fails after max retries."""
        queue = JobQueue()

        async def failing_task():
            raise ValueError("Test error")

        tasks = {"test_task": failing_task}
        worker = Worker(queue=queue, tasks=tasks)

        job = Job(id="job-1", task_name="test_task", max_retries=2)
        queue.enqueue(job)

        # First attempt
        await worker._process_job(job)
        assert job.retry_count == 1

        # Second attempt
        await worker._process_job(job)
        assert job.status == JobStatus.FAILED
        assert job.retry_count == 2


class TestJobScheduler:
    """Test JobScheduler class."""

    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        queue = JobQueue()
        tasks = {}

        scheduler = JobScheduler(queue=queue, tasks=tasks)

        assert scheduler.queue == queue
        assert scheduler.tasks == tasks
        assert scheduler.workers == []

    def test_schedule_job(self):
        """Test scheduling a job."""
        queue = JobQueue()
        tasks = {"test_task": lambda: None}

        scheduler = JobScheduler(queue=queue, tasks=tasks)

        job = scheduler.schedule(
            task_name="test_task",
            args=(1, 2),
            kwargs={"key": "value"},
            priority=JobPriority.HIGH
        )

        assert job.task_name == "test_task"
        assert job.args == (1, 2)
        assert job.kwargs == {"key": "value"}
        assert job.priority == JobPriority.HIGH
        assert job.id in queue.jobs

    def test_schedule_job_with_delay(self):
        """Test scheduling job with delay."""
        queue = JobQueue()
        tasks = {"test_task": lambda: None}

        scheduler = JobScheduler(queue=queue, tasks=tasks)

        job = scheduler.schedule(
            task_name="test_task",
            delay=60
        )

        # Job should be scheduled in the future
        assert job.scheduled_at > datetime.utcnow()


class TestJobStatus:
    """Test JobStatus enum."""

    def test_statuses_exist(self):
        """Test that all statuses exist."""
        assert hasattr(JobStatus, "PENDING")
        assert hasattr(JobStatus, "RUNNING")
        assert hasattr(JobStatus, "COMPLETED")
        assert hasattr(JobStatus, "FAILED")
        assert hasattr(JobStatus, "CANCELLED")
        assert hasattr(JobStatus, "RETRYING")


class TestJobPriority:
    """Test JobPriority enum."""

    def test_priorities_exist(self):
        """Test that all priorities exist."""
        assert hasattr(JobPriority, "LOW")
        assert hasattr(JobPriority, "NORMAL")
        assert hasattr(JobPriority, "HIGH")
        assert hasattr(JobPriority, "CRITICAL")
