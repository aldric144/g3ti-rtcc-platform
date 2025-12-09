"""
ETL Pipeline Core for G3TI RTCC-UIP.

This module provides the core ETL pipeline infrastructure including:
- Pipeline configuration and management
- Execution orchestration
- Status tracking and monitoring
- Error handling and recovery
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class PipelineStatus(str, Enum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class PipelineStage(str, Enum):
    """Pipeline execution stages."""

    EXTRACT = "extract"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    LOAD = "load"
    COMPLETE = "complete"


class PipelineConfig(BaseModel):
    """Pipeline configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    name: str = Field(description="Pipeline name")
    source_type: str = Field(description="Source system type (CAD, RMS, etc.)")
    batch_size: int = Field(default=1000, ge=1, description="Batch processing size")
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    retry_delay_seconds: int = Field(default=60, ge=1, description="Delay between retries")
    timeout_seconds: int = Field(default=3600, ge=60, description="Pipeline timeout")
    parallel_workers: int = Field(default=4, ge=1, description="Parallel worker count")
    validation_enabled: bool = Field(default=True, description="Enable data validation")
    deduplication_enabled: bool = Field(default=True, description="Enable deduplication")
    quality_threshold: float = Field(
        default=0.95, ge=0, le=1, description="Minimum quality score"
    )


class PipelineMetrics(BaseModel):
    """Pipeline execution metrics."""

    model_config = ConfigDict(from_attributes=True)

    records_extracted: int = Field(default=0, description="Records extracted")
    records_transformed: int = Field(default=0, description="Records transformed")
    records_validated: int = Field(default=0, description="Records validated")
    records_loaded: int = Field(default=0, description="Records loaded")
    records_failed: int = Field(default=0, description="Records failed")
    records_skipped: int = Field(default=0, description="Records skipped (duplicates)")
    validation_errors: int = Field(default=0, description="Validation errors")
    transform_errors: int = Field(default=0, description="Transform errors")
    load_errors: int = Field(default=0, description="Load errors")
    duration_seconds: float = Field(default=0.0, description="Execution duration")
    throughput_per_second: float = Field(default=0.0, description="Records per second")


class PipelineRun(BaseModel):
    """Pipeline execution run record."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Run ID")
    pipeline_name: str = Field(description="Pipeline name")
    status: PipelineStatus = Field(default=PipelineStatus.PENDING)
    current_stage: PipelineStage = Field(default=PipelineStage.EXTRACT)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    metrics: PipelineMetrics = Field(default_factory=PipelineMetrics)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    config: PipelineConfig | None = Field(default=None)


class ETLPipeline:
    """
    Core ETL Pipeline orchestrator.

    Manages the execution of extract-transform-load operations
    with monitoring, error handling, and recovery capabilities.
    """

    def __init__(
        self,
        config: PipelineConfig,
        extractor: Callable[..., Any] | None = None,
        transformer: Callable[..., Any] | None = None,
        validator: Callable[..., Any] | None = None,
        loader: Callable[..., Any] | None = None,
    ):
        """
        Initialize the ETL Pipeline.

        Args:
            config: Pipeline configuration
            extractor: Data extraction function
            transformer: Data transformation function
            validator: Data validation function
            loader: Data loading function
        """
        self.config = config
        self.extractor = extractor
        self.transformer = transformer
        self.validator = validator
        self.loader = loader

        self._current_run: PipelineRun | None = None
        self._is_running = False
        self._should_stop = False

        logger.info(f"ETLPipeline '{config.name}' initialized")

    @property
    def is_running(self) -> bool:
        """Check if pipeline is currently running."""
        return self._is_running

    @property
    def current_run(self) -> PipelineRun | None:
        """Get current run information."""
        return self._current_run

    async def execute(
        self,
        source_params: dict[str, Any] | None = None,
        target_params: dict[str, Any] | None = None,
    ) -> PipelineRun:
        """
        Execute the ETL pipeline.

        Args:
            source_params: Parameters for data extraction
            target_params: Parameters for data loading

        Returns:
            Pipeline run record with results
        """
        if self._is_running:
            raise RuntimeError(f"Pipeline '{self.config.name}' is already running")

        # Initialize run
        run_id = str(uuid.uuid4())
        self._current_run = PipelineRun(
            id=run_id,
            pipeline_name=self.config.name,
            status=PipelineStatus.RUNNING,
            started_at=datetime.utcnow(),
            config=self.config,
        )
        self._is_running = True
        self._should_stop = False

        logger.info(f"Starting pipeline run {run_id} for '{self.config.name}'")

        try:
            # Extract stage
            self._current_run.current_stage = PipelineStage.EXTRACT
            extracted_data = await self._execute_extract(source_params or {})

            if self._should_stop:
                return self._finalize_run(PipelineStatus.CANCELLED)

            # Transform stage
            self._current_run.current_stage = PipelineStage.TRANSFORM
            transformed_data = await self._execute_transform(extracted_data)

            if self._should_stop:
                return self._finalize_run(PipelineStatus.CANCELLED)

            # Validate stage
            if self.config.validation_enabled:
                self._current_run.current_stage = PipelineStage.VALIDATE
                validated_data = await self._execute_validate(transformed_data)
            else:
                validated_data = transformed_data

            if self._should_stop:
                return self._finalize_run(PipelineStatus.CANCELLED)

            # Load stage
            self._current_run.current_stage = PipelineStage.LOAD
            await self._execute_load(validated_data, target_params or {})

            self._current_run.current_stage = PipelineStage.COMPLETE
            return self._finalize_run(PipelineStatus.COMPLETED)

        except Exception as e:
            logger.error(f"Pipeline '{self.config.name}' failed: {e}")
            self._current_run.errors.append({
                "stage": self._current_run.current_stage.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })
            return self._finalize_run(PipelineStatus.FAILED)

    async def _execute_extract(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Execute extraction stage."""
        logger.info(f"Extracting data for pipeline '{self.config.name}'")

        if self.extractor is None:
            logger.warning("No extractor configured, returning empty data")
            return []

        try:
            if asyncio.iscoroutinefunction(self.extractor):
                data = await self.extractor(**params)
            else:
                data = self.extractor(**params)

            if not isinstance(data, list):
                data = [data]

            self._current_run.metrics.records_extracted = len(data)
            logger.info(f"Extracted {len(data)} records")
            return data

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            self._current_run.errors.append({
                "stage": "extract",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })
            raise

    async def _execute_transform(
        self, data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Execute transformation stage."""
        logger.info(f"Transforming {len(data)} records")

        if self.transformer is None:
            self._current_run.metrics.records_transformed = len(data)
            return data

        transformed = []
        errors = 0

        for record in data:
            try:
                if asyncio.iscoroutinefunction(self.transformer):
                    result = await self.transformer(record)
                else:
                    result = self.transformer(record)

                if result is not None:
                    transformed.append(result)

            except Exception as e:
                errors += 1
                logger.warning(f"Transform error: {e}")
                self._current_run.errors.append({
                    "stage": "transform",
                    "error": str(e),
                    "record_id": record.get("id", "unknown"),
                    "timestamp": datetime.utcnow().isoformat(),
                })

        self._current_run.metrics.records_transformed = len(transformed)
        self._current_run.metrics.transform_errors = errors
        logger.info(f"Transformed {len(transformed)} records, {errors} errors")

        return transformed

    async def _execute_validate(
        self, data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Execute validation stage."""
        logger.info(f"Validating {len(data)} records")

        if self.validator is None:
            self._current_run.metrics.records_validated = len(data)
            return data

        validated = []
        errors = 0

        for record in data:
            try:
                if asyncio.iscoroutinefunction(self.validator):
                    is_valid = await self.validator(record)
                else:
                    is_valid = self.validator(record)

                if is_valid:
                    validated.append(record)
                else:
                    errors += 1

            except Exception as e:
                errors += 1
                logger.warning(f"Validation error: {e}")

        self._current_run.metrics.records_validated = len(validated)
        self._current_run.metrics.validation_errors = errors
        logger.info(f"Validated {len(validated)} records, {errors} invalid")

        # Check quality threshold
        if len(data) > 0:
            quality_score = len(validated) / len(data)
            if quality_score < self.config.quality_threshold:
                logger.warning(
                    f"Quality score {quality_score:.2f} below threshold "
                    f"{self.config.quality_threshold}"
                )

        return validated

    async def _execute_load(
        self,
        data: list[dict[str, Any]],
        params: dict[str, Any],
    ) -> None:
        """Execute loading stage."""
        logger.info(f"Loading {len(data)} records")

        if self.loader is None:
            logger.warning("No loader configured, skipping load")
            self._current_run.metrics.records_loaded = len(data)
            return

        loaded = 0
        errors = 0

        # Process in batches
        for i in range(0, len(data), self.config.batch_size):
            batch = data[i : i + self.config.batch_size]

            try:
                if asyncio.iscoroutinefunction(self.loader):
                    result = await self.loader(batch, **params)
                else:
                    result = self.loader(batch, **params)

                if isinstance(result, dict):
                    loaded += result.get("successful", len(batch))
                    errors += result.get("failed", 0)
                else:
                    loaded += len(batch)

            except Exception as e:
                errors += len(batch)
                logger.error(f"Load error for batch: {e}")
                self._current_run.errors.append({
                    "stage": "load",
                    "error": str(e),
                    "batch_start": i,
                    "batch_size": len(batch),
                    "timestamp": datetime.utcnow().isoformat(),
                })

        self._current_run.metrics.records_loaded = loaded
        self._current_run.metrics.load_errors = errors
        logger.info(f"Loaded {loaded} records, {errors} errors")

    def _finalize_run(self, status: PipelineStatus) -> PipelineRun:
        """Finalize the pipeline run."""
        self._current_run.status = status
        self._current_run.completed_at = datetime.utcnow()

        # Calculate duration and throughput
        if self._current_run.started_at:
            duration = (
                self._current_run.completed_at - self._current_run.started_at
            ).total_seconds()
            self._current_run.metrics.duration_seconds = duration

            if duration > 0:
                total_processed = self._current_run.metrics.records_loaded
                self._current_run.metrics.throughput_per_second = total_processed / duration

        self._is_running = False

        logger.info(
            f"Pipeline '{self.config.name}' completed with status {status.value}. "
            f"Loaded {self._current_run.metrics.records_loaded} records in "
            f"{self._current_run.metrics.duration_seconds:.2f}s"
        )

        return self._current_run

    def stop(self) -> None:
        """Request pipeline to stop."""
        logger.info(f"Stop requested for pipeline '{self.config.name}'")
        self._should_stop = True

    def get_status(self) -> dict[str, Any]:
        """Get current pipeline status."""
        if self._current_run is None:
            return {
                "pipeline_name": self.config.name,
                "status": "idle",
                "last_run": None,
            }

        return {
            "pipeline_name": self.config.name,
            "run_id": self._current_run.id,
            "status": self._current_run.status.value,
            "current_stage": self._current_run.current_stage.value,
            "started_at": (
                self._current_run.started_at.isoformat()
                if self._current_run.started_at
                else None
            ),
            "metrics": self._current_run.metrics.model_dump(),
            "error_count": len(self._current_run.errors),
        }


class PipelineManager:
    """
    Manager for multiple ETL pipelines.

    Provides centralized management of pipeline instances,
    scheduling, and monitoring.
    """

    def __init__(self):
        """Initialize the Pipeline Manager."""
        self._pipelines: dict[str, ETLPipeline] = {}
        self._run_history: list[PipelineRun] = []

        logger.info("PipelineManager initialized")

    def register_pipeline(self, pipeline: ETLPipeline) -> None:
        """
        Register a pipeline with the manager.

        Args:
            pipeline: Pipeline to register
        """
        name = pipeline.config.name
        if name in self._pipelines:
            logger.warning(f"Overwriting existing pipeline '{name}'")

        self._pipelines[name] = pipeline
        logger.info(f"Registered pipeline '{name}'")

    def get_pipeline(self, name: str) -> ETLPipeline | None:
        """
        Get a registered pipeline by name.

        Args:
            name: Pipeline name

        Returns:
            Pipeline instance or None
        """
        return self._pipelines.get(name)

    def list_pipelines(self) -> list[dict[str, Any]]:
        """
        List all registered pipelines.

        Returns:
            List of pipeline information
        """
        return [
            {
                "name": name,
                "source_type": pipeline.config.source_type,
                "is_running": pipeline.is_running,
                "status": pipeline.get_status(),
            }
            for name, pipeline in self._pipelines.items()
        ]

    async def execute_pipeline(
        self,
        name: str,
        source_params: dict[str, Any] | None = None,
        target_params: dict[str, Any] | None = None,
    ) -> PipelineRun:
        """
        Execute a registered pipeline.

        Args:
            name: Pipeline name
            source_params: Source parameters
            target_params: Target parameters

        Returns:
            Pipeline run record
        """
        pipeline = self._pipelines.get(name)
        if pipeline is None:
            raise ValueError(f"Pipeline '{name}' not found")

        run = await pipeline.execute(source_params, target_params)
        self._run_history.append(run)

        # Keep only last 100 runs
        if len(self._run_history) > 100:
            self._run_history = self._run_history[-100:]

        return run

    def get_run_history(
        self,
        pipeline_name: str | None = None,
        limit: int = 20,
    ) -> list[PipelineRun]:
        """
        Get pipeline run history.

        Args:
            pipeline_name: Optional filter by pipeline name
            limit: Maximum results

        Returns:
            List of pipeline runs
        """
        history = self._run_history

        if pipeline_name:
            history = [r for r in history if r.pipeline_name == pipeline_name]

        return history[-limit:]

    def stop_pipeline(self, name: str) -> bool:
        """
        Stop a running pipeline.

        Args:
            name: Pipeline name

        Returns:
            True if stop was requested
        """
        pipeline = self._pipelines.get(name)
        if pipeline is None:
            return False

        if pipeline.is_running:
            pipeline.stop()
            return True

        return False
