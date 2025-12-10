"""
Intelligence Pipelines for G3TI RTCC-UIP.

This module provides async, queue-based pipeline architecture for processing
intelligence signals through various stages.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PipelineStage(str, Enum):
    """Pipeline processing stages."""
    INGEST = "ingest"
    NORMALIZE = "normalize"
    VALIDATE = "validate"
    ENRICH = "enrich"
    CORRELATE = "correlate"
    SCORE = "score"
    ROUTE = "route"
    COMPLETE = "complete"
    ERROR = "error"


class PipelineType(str, Enum):
    """Types of intelligence pipelines."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    FUSION = "fusion"
    ALERT_PRIORITY = "alert_priority"
    OFFICER_SAFETY = "officer_safety"
    INVESTIGATIVE_LEAD = "investigative_lead"
    DATA_LAKE_FEEDBACK = "data_lake_feedback"


class PipelineStatus(str, Enum):
    """Pipeline operational status."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class PipelineConfig(BaseModel):
    """Configuration for intelligence pipelines."""
    name: str
    pipeline_type: PipelineType
    enabled: bool = True
    max_queue_size: int = 5000
    batch_size: int = 100
    batch_timeout_seconds: float = 1.0
    max_retries: int = 3
    retry_delay_seconds: float = 0.5
    parallel_workers: int = 4
    timeout_seconds: float = 30.0
    priority: int = 5  # 1-10, higher = more priority
    stages: list[PipelineStage] = Field(default_factory=lambda: [
        PipelineStage.INGEST,
        PipelineStage.NORMALIZE,
        PipelineStage.VALIDATE,
        PipelineStage.ENRICH,
        PipelineStage.CORRELATE,
        PipelineStage.SCORE,
        PipelineStage.ROUTE,
        PipelineStage.COMPLETE,
    ])


class PipelineMetrics(BaseModel):
    """Metrics for pipeline performance."""
    items_received: int = 0
    items_processed: int = 0
    items_failed: int = 0
    items_retried: int = 0
    avg_processing_time_ms: float = 0.0
    current_queue_size: int = 0
    last_processed_time: datetime | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)


class PipelineItem(BaseModel, Generic[T]):
    """Item being processed through a pipeline."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    data: Any
    stage: PipelineStage = PipelineStage.INGEST
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    retries: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class StageProcessor(ABC):
    """Abstract base class for pipeline stage processors."""

    @abstractmethod
    async def process(self, item: PipelineItem) -> PipelineItem:
        """Process an item through this stage."""
        pass

    @property
    @abstractmethod
    def stage(self) -> PipelineStage:
        """Return the stage this processor handles."""
        pass


class IntelPipeline:
    """
    Base intelligence pipeline with async queue-based processing.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.status = PipelineStatus.IDLE
        self.metrics = PipelineMetrics()
        self._queue: asyncio.Queue[PipelineItem] = asyncio.Queue(
            maxsize=config.max_queue_size
        )
        self._output_queue: asyncio.Queue[PipelineItem] = asyncio.Queue()
        self._running = False
        self._workers: list[asyncio.Task] = []
        self._stage_processors: dict[PipelineStage, StageProcessor] = {}
        self._stage_handlers: dict[PipelineStage, Callable] = {}
        self._output_handlers: list[Callable] = []

        logger.info("Pipeline %s initialized", config.name)

    def register_stage_processor(self, processor: StageProcessor):
        """Register a stage processor."""
        self._stage_processors[processor.stage] = processor

    def register_stage_handler(
        self, stage: PipelineStage, handler: Callable
    ):
        """Register a handler function for a stage."""
        self._stage_handlers[stage] = handler

    def register_output_handler(self, handler: Callable):
        """Register a handler for pipeline output."""
        self._output_handlers.append(handler)

    async def start(self):
        """Start the pipeline."""
        if self._running:
            return

        self._running = True
        self.status = PipelineStatus.RUNNING

        # Start worker tasks
        for i in range(self.config.parallel_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)

        # Start output handler
        self._workers.append(asyncio.create_task(self._output_processor()))

        logger.info("Pipeline %s started with %d workers",
                   self.config.name, self.config.parallel_workers)

    async def stop(self):
        """Stop the pipeline."""
        self._running = False
        self.status = PipelineStatus.STOPPED

        for worker in self._workers:
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass

        self._workers.clear()
        logger.info("Pipeline %s stopped", self.config.name)

    async def pause(self):
        """Pause the pipeline."""
        self.status = PipelineStatus.PAUSED

    async def resume(self):
        """Resume the pipeline."""
        if self._running:
            self.status = PipelineStatus.RUNNING

    async def submit(self, data: Any) -> str:
        """Submit data to the pipeline. Returns item ID."""
        item = PipelineItem(data=data)

        try:
            self._queue.put_nowait(item)
            self.metrics.items_received += 1
            self.metrics.current_queue_size = self._queue.qsize()
            return item.id
        except asyncio.QueueFull:
            logger.warning("Pipeline %s queue full", self.config.name)
            raise

    async def submit_batch(self, items: list[Any]) -> list[str]:
        """Submit multiple items. Returns list of item IDs."""
        ids = []
        for data in items:
            try:
                item_id = await self.submit(data)
                ids.append(item_id)
            except asyncio.QueueFull:
                break
        return ids

    async def _worker(self, worker_id: int):
        """Worker task to process items from queue."""
        while self._running:
            try:
                if self.status == PipelineStatus.PAUSED:
                    await asyncio.sleep(0.1)
                    continue

                # Get item from queue
                try:
                    item = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=self.config.batch_timeout_seconds,
                    )
                except TimeoutError:
                    continue

                # Process through stages
                start_time = datetime.now(UTC)

                try:
                    item = await self._process_item(item)

                    # Send to output queue
                    await self._output_queue.put(item)

                    self.metrics.items_processed += 1
                    self.metrics.last_processed_time = datetime.now(UTC)

                except Exception as e:
                    logger.error("Worker %d error processing item %s: %s",
                               worker_id, item.id, e)
                    item.stage = PipelineStage.ERROR
                    item.errors.append(str(e))
                    self.metrics.items_failed += 1

                    # Retry logic
                    if item.retries < self.config.max_retries:
                        item.retries += 1
                        self.metrics.items_retried += 1
                        await asyncio.sleep(self.config.retry_delay_seconds)
                        await self._queue.put(item)

                # Update metrics
                elapsed_ms = (
                    datetime.now(UTC) - start_time
                ).total_seconds() * 1000
                self.metrics.avg_processing_time_ms = (
                    self.metrics.avg_processing_time_ms * 0.9 + elapsed_ms * 0.1
                )
                self.metrics.current_queue_size = self._queue.qsize()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Worker %d unexpected error: %s", worker_id, e)

    async def _process_item(self, item: PipelineItem) -> PipelineItem:
        """Process item through all configured stages."""
        for stage in self.config.stages:
            if stage == PipelineStage.COMPLETE:
                item.stage = stage
                break

            item.stage = stage
            item.updated_at = datetime.now(UTC)

            # Try stage processor first
            if stage in self._stage_processors:
                item = await self._stage_processors[stage].process(item)
            # Then try handler function
            elif stage in self._stage_handlers:
                item = await self._stage_handlers[stage](item)
            # Default processing
            else:
                item = await self._default_stage_handler(stage, item)

        return item

    async def _default_stage_handler(
        self, stage: PipelineStage, item: PipelineItem
    ) -> PipelineItem:
        """Default handler for stages without custom processors."""
        item.metadata[f"{stage.value}_completed"] = True
        item.metadata[f"{stage.value}_time"] = datetime.now(UTC).isoformat()
        return item

    async def _output_processor(self):
        """Process completed items and send to output handlers."""
        while self._running:
            try:
                item = await asyncio.wait_for(
                    self._output_queue.get(),
                    timeout=1.0,
                )

                for handler in self._output_handlers:
                    try:
                        await handler(item)
                    except Exception as e:
                        logger.error("Output handler error: %s", e)

            except TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    def get_status(self) -> dict[str, Any]:
        """Get pipeline status."""
        return {
            "name": self.config.name,
            "type": self.config.pipeline_type.value,
            "status": self.status.value,
            "metrics": self.metrics.model_dump(),
            "workers": len(self._workers),
            "queue_size": self._queue.qsize(),
        }


class RealTimePipeline(IntelPipeline):
    """
    Real-time signal processing pipeline.

    Optimized for low-latency processing of incoming intelligence signals.
    """

    def __init__(self, name: str = "real_time_pipeline"):
        config = PipelineConfig(
            name=name,
            pipeline_type=PipelineType.REAL_TIME,
            batch_size=10,
            batch_timeout_seconds=0.1,
            parallel_workers=8,
            priority=10,
        )
        super().__init__(config)

    async def _default_stage_handler(
        self, stage: PipelineStage, item: PipelineItem
    ) -> PipelineItem:
        """Real-time optimized stage handling."""
        if stage == PipelineStage.NORMALIZE:
            item.data = await self._normalize_realtime(item.data)
        elif stage == PipelineStage.VALIDATE:
            item.data = await self._validate_realtime(item.data)
        elif stage == PipelineStage.ENRICH:
            item.data = await self._enrich_realtime(item.data)

        return await super()._default_stage_handler(stage, item)

    async def _normalize_realtime(self, data: Any) -> Any:
        """Fast normalization for real-time data."""
        if isinstance(data, dict):
            data["_normalized"] = True
            data["_pipeline"] = "real_time"
        return data

    async def _validate_realtime(self, data: Any) -> Any:
        """Fast validation for real-time data."""
        if isinstance(data, dict):
            data["_validated"] = True
        return data

    async def _enrich_realtime(self, data: Any) -> Any:
        """Fast enrichment for real-time data."""
        if isinstance(data, dict):
            data["_enriched"] = True
            data["_enriched_at"] = datetime.now(UTC).isoformat()
        return data


class BatchPipeline(IntelPipeline):
    """
    Batch analytics processing pipeline.

    Optimized for throughput when processing historical or bulk data.
    """

    def __init__(self, name: str = "batch_pipeline"):
        config = PipelineConfig(
            name=name,
            pipeline_type=PipelineType.BATCH,
            batch_size=500,
            batch_timeout_seconds=5.0,
            parallel_workers=4,
            priority=3,
        )
        super().__init__(config)
        self._batch_buffer: list[PipelineItem] = []

    async def submit_for_batch(self, data: Any) -> str:
        """Submit data for batch processing."""
        item = PipelineItem(data=data)
        self._batch_buffer.append(item)

        if len(self._batch_buffer) >= self.config.batch_size:
            await self._flush_batch()

        return item.id

    async def _flush_batch(self):
        """Flush batch buffer to processing queue."""
        if not self._batch_buffer:
            return

        for item in self._batch_buffer:
            try:
                self._queue.put_nowait(item)
                self.metrics.items_received += 1
            except asyncio.QueueFull:
                logger.warning("Batch pipeline queue full")
                break

        self._batch_buffer.clear()


class FusionPipeline(IntelPipeline):
    """
    Cross-engine fusion pipeline.

    Combines intelligence from multiple sources and engines.
    """

    def __init__(self, name: str = "fusion_pipeline"):
        config = PipelineConfig(
            name=name,
            pipeline_type=PipelineType.FUSION,
            batch_size=50,
            batch_timeout_seconds=2.0,
            parallel_workers=4,
            priority=8,
            stages=[
                PipelineStage.INGEST,
                PipelineStage.NORMALIZE,
                PipelineStage.CORRELATE,
                PipelineStage.SCORE,
                PipelineStage.ROUTE,
                PipelineStage.COMPLETE,
            ],
        )
        super().__init__(config)
        self._correlation_buffer: dict[str, list[PipelineItem]] = {}
        self._correlation_window_seconds = 30.0

    async def submit_for_fusion(
        self, data: Any, correlation_key: str
    ) -> str:
        """Submit data for fusion with correlation key."""
        item = PipelineItem(data=data)
        item.metadata["correlation_key"] = correlation_key

        # Add to correlation buffer
        if correlation_key not in self._correlation_buffer:
            self._correlation_buffer[correlation_key] = []
        self._correlation_buffer[correlation_key].append(item)

        # Check if ready for fusion
        await self._check_fusion_ready(correlation_key)

        return item.id

    async def _check_fusion_ready(self, correlation_key: str):
        """Check if correlation group is ready for fusion."""
        items = self._correlation_buffer.get(correlation_key, [])

        if len(items) >= 2:  # Minimum items for fusion
            # Create fused item
            fused_data = {
                "correlation_key": correlation_key,
                "source_items": [item.data for item in items],
                "source_count": len(items),
                "fused_at": datetime.now(UTC).isoformat(),
            }

            fused_item = PipelineItem(data=fused_data)
            fused_item.metadata["is_fused"] = True
            fused_item.metadata["source_ids"] = [item.id for item in items]

            await self._queue.put(fused_item)
            self.metrics.items_received += 1

            # Clear buffer
            del self._correlation_buffer[correlation_key]


class AlertPriorityPipeline(IntelPipeline):
    """
    Alert prioritization pipeline.

    Scores and prioritizes alerts for routing.
    """

    def __init__(self, name: str = "alert_priority_pipeline"):
        config = PipelineConfig(
            name=name,
            pipeline_type=PipelineType.ALERT_PRIORITY,
            batch_size=20,
            batch_timeout_seconds=0.5,
            parallel_workers=6,
            priority=9,
            stages=[
                PipelineStage.INGEST,
                PipelineStage.VALIDATE,
                PipelineStage.SCORE,
                PipelineStage.ROUTE,
                PipelineStage.COMPLETE,
            ],
        )
        super().__init__(config)

    async def _default_stage_handler(
        self, stage: PipelineStage, item: PipelineItem
    ) -> PipelineItem:
        """Alert-specific stage handling."""
        if stage == PipelineStage.SCORE:
            item.data = await self._score_alert(item.data)
        elif stage == PipelineStage.ROUTE:
            item.data = await self._determine_routing(item.data)

        return await super()._default_stage_handler(stage, item)

    async def _score_alert(self, data: Any) -> Any:
        """Score alert priority."""
        if isinstance(data, dict):
            # Calculate priority score (0-100)
            base_score = data.get("base_priority", 50)
            confidence = data.get("confidence", 0.5)
            urgency = data.get("urgency_modifier", 1.0)

            priority_score = min(100, base_score * confidence * urgency)
            data["priority_score"] = priority_score
            data["priority_tier"] = self._get_tier(priority_score)

        return data

    def _get_tier(self, score: float) -> str:
        """Get priority tier from score."""
        if score >= 80:
            return "tier_1"
        elif score >= 60:
            return "tier_2"
        elif score >= 40:
            return "tier_3"
        return "tier_4"

    async def _determine_routing(self, data: Any) -> Any:
        """Determine alert routing destinations."""
        if isinstance(data, dict):
            tier = data.get("priority_tier", "tier_4")
            destinations = ["rtcc_dashboard"]

            if tier == "tier_1":
                destinations.extend([
                    "officer_safety",
                    "dispatch",
                    "mobile_mdt",
                ])
            elif tier == "tier_2":
                destinations.extend([
                    "investigations",
                    "tactical",
                ])
            elif tier == "tier_3":
                destinations.append("tactical")

            data["routing_destinations"] = destinations

        return data


class OfficerSafetyPipeline(IntelPipeline):
    """
    Officer safety escalation pipeline.

    High-priority pipeline for officer safety threats.
    """

    def __init__(self, name: str = "officer_safety_pipeline"):
        config = PipelineConfig(
            name=name,
            pipeline_type=PipelineType.OFFICER_SAFETY,
            batch_size=1,  # Process immediately
            batch_timeout_seconds=0.05,
            parallel_workers=10,
            priority=10,  # Highest priority
            max_retries=5,
            stages=[
                PipelineStage.INGEST,
                PipelineStage.VALIDATE,
                PipelineStage.ENRICH,
                PipelineStage.ROUTE,
                PipelineStage.COMPLETE,
            ],
        )
        super().__init__(config)

    async def _default_stage_handler(
        self, stage: PipelineStage, item: PipelineItem
    ) -> PipelineItem:
        """Officer safety specific handling."""
        if stage == PipelineStage.ENRICH:
            item.data = await self._enrich_officer_safety(item.data)
        elif stage == PipelineStage.ROUTE:
            item.data = await self._route_officer_safety(item.data)

        return await super()._default_stage_handler(stage, item)

    async def _enrich_officer_safety(self, data: Any) -> Any:
        """Enrich with officer safety context."""
        if isinstance(data, dict):
            data["priority_tier"] = "tier_1"
            data["priority_score"] = 100
            data["immediate_action_required"] = True
            data["enriched_at"] = datetime.now(UTC).isoformat()
        return data

    async def _route_officer_safety(self, data: Any) -> Any:
        """Route to all officer safety destinations."""
        if isinstance(data, dict):
            data["routing_destinations"] = [
                "officer_safety_alerts",
                "dispatch_comms",
                "mobile_mdt",
                "tactical_dashboard",
                "rtcc_dashboard",
                "command_center",
            ]
            data["broadcast_priority"] = "immediate"
        return data


class InvestigativeLeadPipeline(IntelPipeline):
    """
    Investigative lead generation pipeline.

    Generates and routes investigative leads from intelligence.
    """

    def __init__(self, name: str = "investigative_lead_pipeline"):
        config = PipelineConfig(
            name=name,
            pipeline_type=PipelineType.INVESTIGATIVE_LEAD,
            batch_size=25,
            batch_timeout_seconds=2.0,
            parallel_workers=4,
            priority=6,
            stages=[
                PipelineStage.INGEST,
                PipelineStage.NORMALIZE,
                PipelineStage.VALIDATE,
                PipelineStage.ENRICH,
                PipelineStage.CORRELATE,
                PipelineStage.SCORE,
                PipelineStage.ROUTE,
                PipelineStage.COMPLETE,
            ],
        )
        super().__init__(config)

    async def _default_stage_handler(
        self, stage: PipelineStage, item: PipelineItem
    ) -> PipelineItem:
        """Investigative lead specific handling."""
        if stage == PipelineStage.CORRELATE:
            item.data = await self._correlate_to_cases(item.data)
        elif stage == PipelineStage.SCORE:
            item.data = await self._score_lead(item.data)

        return await super()._default_stage_handler(stage, item)

    async def _correlate_to_cases(self, data: Any) -> Any:
        """Correlate lead to existing cases."""
        if isinstance(data, dict):
            # Placeholder for case correlation logic
            data["case_correlations"] = []
            data["correlation_checked"] = True
        return data

    async def _score_lead(self, data: Any) -> Any:
        """Score lead quality and relevance."""
        if isinstance(data, dict):
            # Calculate lead score
            confidence = data.get("confidence", 0.5)
            relevance = data.get("relevance", 0.5)
            timeliness = data.get("timeliness", 0.5)

            lead_score = (confidence * 0.4 + relevance * 0.4 + timeliness * 0.2) * 100
            data["lead_score"] = lead_score
            data["lead_quality"] = self._get_lead_quality(lead_score)
        return data

    def _get_lead_quality(self, score: float) -> str:
        """Get lead quality classification."""
        if score >= 80:
            return "high"
        elif score >= 50:
            return "medium"
        return "low"


class DataLakeFeedbackPipeline(IntelPipeline):
    """
    Data lake feedback loop pipeline.

    Processes feedback from data lake analytics back into orchestration.
    """

    def __init__(self, name: str = "data_lake_feedback_pipeline"):
        config = PipelineConfig(
            name=name,
            pipeline_type=PipelineType.DATA_LAKE_FEEDBACK,
            batch_size=100,
            batch_timeout_seconds=5.0,
            parallel_workers=2,
            priority=4,
            stages=[
                PipelineStage.INGEST,
                PipelineStage.NORMALIZE,
                PipelineStage.VALIDATE,
                PipelineStage.ENRICH,
                PipelineStage.ROUTE,
                PipelineStage.COMPLETE,
            ],
        )
        super().__init__(config)

    async def _default_stage_handler(
        self, stage: PipelineStage, item: PipelineItem
    ) -> PipelineItem:
        """Data lake feedback specific handling."""
        if stage == PipelineStage.NORMALIZE:
            item.data = await self._normalize_analytics(item.data)
        elif stage == PipelineStage.ENRICH:
            item.data = await self._enrich_with_context(item.data)

        return await super()._default_stage_handler(stage, item)

    async def _normalize_analytics(self, data: Any) -> Any:
        """Normalize analytics output format."""
        if isinstance(data, dict):
            data["source"] = "data_lake"
            data["analytics_type"] = data.get("type", "unknown")
            data["_normalized"] = True
        return data

    async def _enrich_with_context(self, data: Any) -> Any:
        """Enrich with historical context."""
        if isinstance(data, dict):
            data["historical_context"] = True
            data["enriched_at"] = datetime.now(UTC).isoformat()
        return data


class PipelineManager:
    """
    Manager for all intelligence pipelines.
    """

    def __init__(self):
        self._pipelines: dict[str, IntelPipeline] = {}
        self._running = False

    def register_pipeline(self, pipeline: IntelPipeline):
        """Register a pipeline."""
        self._pipelines[pipeline.config.name] = pipeline
        logger.info("Registered pipeline: %s", pipeline.config.name)

    def get_pipeline(self, name: str) -> IntelPipeline | None:
        """Get a pipeline by name."""
        return self._pipelines.get(name)

    def get_pipelines_by_type(
        self, pipeline_type: PipelineType
    ) -> list[IntelPipeline]:
        """Get all pipelines of a specific type."""
        return [
            p for p in self._pipelines.values()
            if p.config.pipeline_type == pipeline_type
        ]

    async def start_all(self):
        """Start all registered pipelines."""
        self._running = True
        for pipeline in self._pipelines.values():
            if pipeline.config.enabled:
                await pipeline.start()
        logger.info("Started %d pipelines", len(self._pipelines))

    async def stop_all(self):
        """Stop all pipelines."""
        self._running = False
        for pipeline in self._pipelines.values():
            await pipeline.stop()
        logger.info("Stopped all pipelines")

    def get_all_status(self) -> dict[str, Any]:
        """Get status of all pipelines."""
        return {
            name: pipeline.get_status()
            for name, pipeline in self._pipelines.items()
        }

    def get_all_metrics(self) -> dict[str, PipelineMetrics]:
        """Get metrics for all pipelines."""
        return {
            name: pipeline.metrics
            for name, pipeline in self._pipelines.items()
        }
