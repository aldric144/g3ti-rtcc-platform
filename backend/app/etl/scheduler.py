"""
ETL Pipeline Scheduler for G3TI RTCC-UIP.

This module provides scheduling capabilities for ETL pipelines including:
- Cron-based scheduling
- Interval-based scheduling
- One-time job execution
- Job monitoring and management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """Schedule type enumeration."""

    CRON = "cron"
    INTERVAL = "interval"
    ONCE = "once"


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ScheduledJob(BaseModel):
    """Scheduled job configuration."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Job ID")
    name: str = Field(description="Job name")
    pipeline_name: str = Field(description="Pipeline to execute")
    schedule_type: ScheduleType = Field(description="Schedule type")

    # Schedule configuration
    cron_expression: str | None = Field(default=None, description="Cron expression")
    interval_seconds: int | None = Field(default=None, description="Interval in seconds")
    run_at: datetime | None = Field(default=None, description="One-time run datetime")

    # Execution parameters
    source_params: dict[str, Any] = Field(default_factory=dict, description="Source parameters")
    target_params: dict[str, Any] = Field(default_factory=dict, description="Target parameters")

    # Status
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current status")
    enabled: bool = Field(default=True, description="Whether job is enabled")

    # Execution history
    last_run: datetime | None = Field(default=None, description="Last execution time")
    next_run: datetime | None = Field(default=None, description="Next scheduled run")
    run_count: int = Field(default=0, description="Total run count")
    success_count: int = Field(default=0, description="Successful run count")
    failure_count: int = Field(default=0, description="Failed run count")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class JobExecution(BaseModel):
    """Record of a job execution."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Execution ID")
    job_id: str = Field(description="Job ID")
    pipeline_name: str = Field(description="Pipeline name")
    status: JobStatus = Field(description="Execution status")
    started_at: datetime = Field(description="Start time")
    completed_at: datetime | None = Field(default=None, description="Completion time")
    duration_seconds: float | None = Field(default=None, description="Duration")
    records_processed: int = Field(default=0, description="Records processed")
    errors: list[dict[str, Any]] = Field(default_factory=list, description="Errors")


class ETLScheduler:
    """
    Scheduler for ETL pipeline jobs.

    Manages scheduled execution of ETL pipelines with support for:
    - Cron-based scheduling
    - Interval-based scheduling
    - One-time execution
    - Job monitoring and history
    """

    def __init__(self, pipeline_executor: Callable[..., Any] | None = None):
        """
        Initialize the scheduler.

        Args:
            pipeline_executor: Function to execute pipelines
        """
        self._jobs: dict[str, ScheduledJob] = {}
        self._executions: list[JobExecution] = []
        self._running = False
        self._executor = pipeline_executor
        self._tasks: dict[str, asyncio.Task[Any]] = {}

        logger.info("ETLScheduler initialized")

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    def add_job(self, job: ScheduledJob) -> None:
        """
        Add a scheduled job.

        Args:
            job: Job to add
        """
        # Calculate next run time
        job.next_run = self._calculate_next_run(job)
        self._jobs[job.id] = job
        logger.info(f"Added job '{job.name}' (id={job.id}), next run: {job.next_run}")

    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.

        Args:
            job_id: Job ID to remove

        Returns:
            True if job was removed
        """
        if job_id in self._jobs:
            # Cancel running task if any
            if job_id in self._tasks:
                self._tasks[job_id].cancel()
                del self._tasks[job_id]

            del self._jobs[job_id]
            logger.info(f"Removed job {job_id}")
            return True
        return False

    def get_job(self, job_id: str) -> ScheduledJob | None:
        """
        Get a job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job or None
        """
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[ScheduledJob]:
        """
        List all scheduled jobs.

        Returns:
            List of jobs
        """
        return list(self._jobs.values())

    def pause_job(self, job_id: str) -> bool:
        """
        Pause a scheduled job.

        Args:
            job_id: Job ID

        Returns:
            True if job was paused
        """
        job = self._jobs.get(job_id)
        if job:
            job.status = JobStatus.PAUSED
            job.enabled = False
            job.updated_at = datetime.utcnow()
            logger.info(f"Paused job {job_id}")
            return True
        return False

    def resume_job(self, job_id: str) -> bool:
        """
        Resume a paused job.

        Args:
            job_id: Job ID

        Returns:
            True if job was resumed
        """
        job = self._jobs.get(job_id)
        if job:
            job.status = JobStatus.PENDING
            job.enabled = True
            job.next_run = self._calculate_next_run(job)
            job.updated_at = datetime.utcnow()
            logger.info(f"Resumed job {job_id}")
            return True
        return False

    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler is already running")
            return

        self._running = True
        logger.info("Starting ETL scheduler")

        # Start the main scheduler loop
        asyncio.create_task(self._scheduler_loop())

    async def stop(self) -> None:
        """Stop the scheduler."""
        logger.info("Stopping ETL scheduler")
        self._running = False

        # Cancel all running tasks
        for task in self._tasks.values():
            task.cancel()

        self._tasks.clear()

    async def run_job_now(self, job_id: str) -> JobExecution | None:
        """
        Run a job immediately.

        Args:
            job_id: Job ID to run

        Returns:
            Job execution record
        """
        job = self._jobs.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return None

        return await self._execute_job(job)

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        logger.info("Scheduler loop started")

        while self._running:
            try:
                now = datetime.utcnow()

                for job_id, job in list(self._jobs.items()):
                    # Skip disabled or paused jobs
                    if not job.enabled or job.status == JobStatus.PAUSED:
                        continue

                    # Skip jobs already running
                    if job.status == JobStatus.RUNNING:
                        continue

                    # Check if job should run
                    if job.next_run and job.next_run <= now:
                        # Execute job in background
                        task = asyncio.create_task(self._execute_job(job))
                        self._tasks[job_id] = task

                # Sleep before next check
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(5)

        logger.info("Scheduler loop stopped")

    async def _execute_job(self, job: ScheduledJob) -> JobExecution:
        """
        Execute a scheduled job.

        Args:
            job: Job to execute

        Returns:
            Execution record
        """
        import uuid

        execution_id = str(uuid.uuid4())
        started_at = datetime.utcnow()

        execution = JobExecution(
            id=execution_id,
            job_id=job.id,
            pipeline_name=job.pipeline_name,
            status=JobStatus.RUNNING,
            started_at=started_at,
        )

        job.status = JobStatus.RUNNING
        job.last_run = started_at
        job.run_count += 1

        logger.info(f"Executing job '{job.name}' (execution={execution_id})")

        try:
            # Execute pipeline
            if self._executor:
                if asyncio.iscoroutinefunction(self._executor):
                    result = await self._executor(
                        job.pipeline_name,
                        job.source_params,
                        job.target_params,
                    )
                else:
                    result = self._executor(
                        job.pipeline_name,
                        job.source_params,
                        job.target_params,
                    )

                if isinstance(result, dict):
                    execution.records_processed = result.get("records_loaded", 0)
                    if result.get("errors"):
                        execution.errors = result["errors"]

            execution.status = JobStatus.COMPLETED
            job.status = JobStatus.COMPLETED
            job.success_count += 1

            logger.info(f"Job '{job.name}' completed successfully")

        except Exception as e:
            logger.error(f"Job '{job.name}' failed: {e}")
            execution.status = JobStatus.FAILED
            execution.errors.append({"error": str(e)})
            job.status = JobStatus.FAILED
            job.failure_count += 1

        # Finalize execution
        execution.completed_at = datetime.utcnow()
        execution.duration_seconds = (
            execution.completed_at - execution.started_at
        ).total_seconds()

        # Update job for next run
        job.next_run = self._calculate_next_run(job)
        job.updated_at = datetime.utcnow()

        # Store execution record
        self._executions.append(execution)
        if len(self._executions) > 1000:
            self._executions = self._executions[-1000:]

        # Clean up task reference
        if job.id in self._tasks:
            del self._tasks[job.id]

        return execution

    def _calculate_next_run(self, job: ScheduledJob) -> datetime | None:
        """
        Calculate next run time for a job.

        Args:
            job: Job to calculate for

        Returns:
            Next run datetime or None
        """
        now = datetime.utcnow()

        if job.schedule_type == ScheduleType.ONCE:
            # One-time job
            if job.run_at and job.run_at > now and job.run_count == 0:
                return job.run_at
            return None

        elif job.schedule_type == ScheduleType.INTERVAL:
            # Interval-based job
            if job.interval_seconds:
                if job.last_run:
                    return job.last_run + timedelta(seconds=job.interval_seconds)
                return now + timedelta(seconds=job.interval_seconds)
            return None

        elif job.schedule_type == ScheduleType.CRON:
            # Cron-based job
            if job.cron_expression:
                return self._parse_cron_next(job.cron_expression, now)
            return None

        return None

    def _parse_cron_next(self, expression: str, after: datetime) -> datetime:
        """
        Parse cron expression and get next run time.

        Simplified cron parser supporting:
        - minute hour day month weekday
        - * for any value
        - */n for every n units

        Args:
            expression: Cron expression
            after: Calculate next run after this time

        Returns:
            Next run datetime
        """
        try:
            parts = expression.split()
            if len(parts) != 5:
                logger.warning(f"Invalid cron expression: {expression}")
                return after + timedelta(hours=1)

            minute, hour, day, month, weekday = parts

            # Simplified: just handle basic cases
            next_run = after.replace(second=0, microsecond=0)

            # Parse minute
            if minute == "*":
                pass
            elif minute.startswith("*/"):
                interval = int(minute[2:])
                next_minute = ((next_run.minute // interval) + 1) * interval
                if next_minute >= 60:
                    next_run = next_run + timedelta(hours=1)
                    next_run = next_run.replace(minute=0)
                else:
                    next_run = next_run.replace(minute=next_minute)
            else:
                target_minute = int(minute)
                if next_run.minute >= target_minute:
                    next_run = next_run + timedelta(hours=1)
                next_run = next_run.replace(minute=target_minute)

            # Parse hour
            if hour == "*":
                pass
            elif hour.startswith("*/"):
                interval = int(hour[2:])
                next_hour = ((next_run.hour // interval) + 1) * interval
                if next_hour >= 24:
                    next_run = next_run + timedelta(days=1)
                    next_run = next_run.replace(hour=0)
                else:
                    next_run = next_run.replace(hour=next_hour)
            else:
                target_hour = int(hour)
                if next_run.hour >= target_hour:
                    next_run = next_run + timedelta(days=1)
                next_run = next_run.replace(hour=target_hour)

            return next_run

        except Exception as e:
            logger.error(f"Cron parse error: {e}")
            return after + timedelta(hours=1)

    def get_execution_history(
        self,
        job_id: str | None = None,
        limit: int = 50,
    ) -> list[JobExecution]:
        """
        Get job execution history.

        Args:
            job_id: Optional filter by job ID
            limit: Maximum results

        Returns:
            List of executions
        """
        history = self._executions

        if job_id:
            history = [e for e in history if e.job_id == job_id]

        return history[-limit:]

    def get_scheduler_status(self) -> dict[str, Any]:
        """
        Get scheduler status summary.

        Returns:
            Status summary
        """
        jobs = list(self._jobs.values())

        return {
            "is_running": self._running,
            "total_jobs": len(jobs),
            "enabled_jobs": sum(1 for j in jobs if j.enabled),
            "paused_jobs": sum(1 for j in jobs if j.status == JobStatus.PAUSED),
            "running_jobs": sum(1 for j in jobs if j.status == JobStatus.RUNNING),
            "total_executions": len(self._executions),
            "recent_failures": sum(
                1 for e in self._executions[-100:] if e.status == JobStatus.FAILED
            ),
        }


def create_daily_aggregate_job(
    jurisdiction: str,
    pipeline_name: str = "daily_aggregate",
) -> ScheduledJob:
    """
    Create a daily aggregate computation job.

    Args:
        jurisdiction: Jurisdiction code
        pipeline_name: Pipeline name

    Returns:
        Configured job
    """
    import uuid

    return ScheduledJob(
        id=str(uuid.uuid4()),
        name=f"Daily Aggregate - {jurisdiction}",
        pipeline_name=pipeline_name,
        schedule_type=ScheduleType.CRON,
        cron_expression="0 2 * * *",  # 2 AM daily
        source_params={"jurisdiction": jurisdiction},
        target_params={},
    )


def create_hourly_ingestion_job(
    source_type: str,
    pipeline_name: str,
) -> ScheduledJob:
    """
    Create an hourly data ingestion job.

    Args:
        source_type: Source system type
        pipeline_name: Pipeline name

    Returns:
        Configured job
    """
    import uuid

    return ScheduledJob(
        id=str(uuid.uuid4()),
        name=f"Hourly Ingestion - {source_type}",
        pipeline_name=pipeline_name,
        schedule_type=ScheduleType.INTERVAL,
        interval_seconds=3600,  # 1 hour
        source_params={"source_type": source_type},
        target_params={},
    )


def create_quality_check_job(
    partition_key: str,
    pipeline_name: str = "quality_check",
) -> ScheduledJob:
    """
    Create a data quality check job.

    Args:
        partition_key: Partition to check
        pipeline_name: Pipeline name

    Returns:
        Configured job
    """
    import uuid

    return ScheduledJob(
        id=str(uuid.uuid4()),
        name=f"Quality Check - {partition_key}",
        pipeline_name=pipeline_name,
        schedule_type=ScheduleType.CRON,
        cron_expression="0 4 * * *",  # 4 AM daily
        source_params={"partition_key": partition_key},
        target_params={},
    )
