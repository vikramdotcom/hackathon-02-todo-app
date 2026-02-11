"""
Cron Job Scheduler

Schedule and manage recurring tasks with cron expressions.
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import asyncio
from croniter import croniter

logger = logging.getLogger(__name__)


class CronJob:
    """Scheduled cron job."""

    def __init__(
        self,
        name: str,
        cron_expression: str,
        task: Callable,
        enabled: bool = True,
        timezone: str = "UTC"
    ):
        """Initialize cron job."""
        self.name = name
        self.cron_expression = cron_expression
        self.task = task
        self.enabled = enabled
        self.timezone = timezone
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0
        self._calculate_next_run()

    def _calculate_next_run(self):
        """Calculate next run time."""
        try:
            cron = croniter(self.cron_expression, datetime.utcnow())
            self.next_run = cron.get_next(datetime)
        except Exception as e:
            logger.error(f"Invalid cron expression for {self.name}: {e}")
            self.next_run = None

    def should_run(self) -> bool:
        """Check if job should run now."""
        if not self.enabled or not self.next_run:
            return False

        return datetime.utcnow() >= self.next_run

    async def run(self):
        """Execute the job."""
        if not self.enabled:
            return

        try:
            logger.info(f"Running cron job: {self.name}")
            self.last_run = datetime.utcnow()

            if asyncio.iscoroutinefunction(self.task):
                await self.task()
            else:
                self.task()

            self.run_count += 1
            self._calculate_next_run()

            logger.info(
                f"Cron job completed: {self.name}",
                extra={
                    "job": self.name,
                    "run_count": self.run_count,
                    "next_run": self.next_run.isoformat() if self.next_run else None
                }
            )

        except Exception as e:
            self.error_count += 1
            logger.error(
                f"Cron job failed: {self.name}",
                extra={"job": self.name, "error": str(e)},
                exc_info=True
            )
            self._calculate_next_run()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "cron_expression": self.cron_expression,
            "enabled": self.enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "error_count": self.error_count
        }


class CronScheduler:
    """Manage cron jobs."""

    def __init__(self):
        """Initialize scheduler."""
        self.jobs: Dict[str, CronJob] = {}
        self.running = False

    def register(self, job: CronJob):
        """Register cron job."""
        self.jobs[job.name] = job
        logger.info(f"Registered cron job: {job.name} ({job.cron_expression})")

    def unregister(self, name: str):
        """Unregister cron job."""
        if name in self.jobs:
            del self.jobs[name]
            logger.info(f"Unregistered cron job: {name}")

    def enable_job(self, name: str):
        """Enable job."""
        if name in self.jobs:
            self.jobs[name].enabled = True
            logger.info(f"Enabled cron job: {name}")

    def disable_job(self, name: str):
        """Disable job."""
        if name in self.jobs:
            self.jobs[name].enabled = False
            logger.info(f"Disabled cron job: {name}")

    async def start(self):
        """Start scheduler."""
        self.running = True
        logger.info("Cron scheduler started")

        while self.running:
            try:
                # Check all jobs
                for job in self.jobs.values():
                    if job.should_run():
                        asyncio.create_task(job.run())

                # Sleep for 1 minute
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
                await asyncio.sleep(60)

    def stop(self):
        """Stop scheduler."""
        self.running = False
        logger.info("Cron scheduler stopped")

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs."""
        return [job.to_dict() for job in self.jobs.values()]


# Global scheduler
cron_scheduler = CronScheduler()


# Example cron jobs
async def cleanup_old_data():
    """Cleanup old data."""
    logger.info("Running cleanup job")
    # Cleanup logic here


async def send_daily_digest():
    """Send daily digest emails."""
    logger.info("Sending daily digest")
    # Email logic here


async def backup_database():
    """Backup database."""
    logger.info("Running database backup")
    # Backup logic here


async def update_statistics():
    """Update statistics."""
    logger.info("Updating statistics")
    # Statistics logic here


# Register default jobs
def register_default_jobs():
    """Register default cron jobs."""

    # Cleanup old data daily at 2 AM
    cron_scheduler.register(CronJob(
        name="cleanup_old_data",
        cron_expression="0 2 * * *",
        task=cleanup_old_data
    ))

    # Send daily digest at 8 AM
    cron_scheduler.register(CronJob(
        name="daily_digest",
        cron_expression="0 8 * * *",
        task=send_daily_digest
    ))

    # Backup database every 6 hours
    cron_scheduler.register(CronJob(
        name="database_backup",
        cron_expression="0 */6 * * *",
        task=backup_database
    ))

    # Update statistics every hour
    cron_scheduler.register(CronJob(
        name="update_statistics",
        cron_expression="0 * * * *",
        task=update_statistics
    ))
