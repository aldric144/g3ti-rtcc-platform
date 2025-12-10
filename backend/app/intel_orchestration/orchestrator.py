"""
Intelligence Orchestrator - Master Controller for G3TI RTCC-UIP.

This module provides the central coordination layer that manages all intelligence
sources, engines, and subsystems across the platform.
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class IntelSource(str, Enum):
    """Intelligence source systems."""
    AI_ENGINE = "ai_engine"
    TACTICAL_ENGINE = "tactical_engine"
    INVESTIGATIONS_ENGINE = "investigations_engine"
    OFFICER_SAFETY = "officer_safety"
    DISPATCH_COMMS = "dispatch_comms"
    FEDERAL_NDEX = "federal_ndex"
    FEDERAL_NCIC = "federal_ncic"
    FEDERAL_ETRACE = "federal_etrace"
    FEDERAL_DHS_SAR = "federal_dhs_sar"
    FEDERATION_HUB = "federation_hub"
    DATA_LAKE = "data_lake"
    ETL_PIPELINE = "etl_pipeline"
    EXTERNAL_FEED = "external_feed"


class IntelCategory(str, Enum):
    """Intelligence category classification."""
    PERSON = "person"
    VEHICLE = "vehicle"
    WEAPON = "weapon"
    INCIDENT = "incident"
    PATTERN = "pattern"
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"
    NETWORK = "network"
    THREAT = "threat"
    LEAD = "lead"


class IntelTier(str, Enum):
    """Intelligence priority tier."""
    TIER_1 = "tier_1"  # Immediate officer safety threat
    TIER_2 = "tier_2"  # High-priority investigative lead
    TIER_3 = "tier_3"  # Tactical awareness signal
    TIER_4 = "tier_4"  # Informational intelligence


class OrchestrationStatus(str, Enum):
    """Orchestration system status."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    ERROR = "error"


class IntelSignal(BaseModel):
    """Raw intelligence signal from any source."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: IntelSource
    category: IntelCategory
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    jurisdiction: str
    confidence: float = Field(ge=0.0, le=1.0)
    data: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw_payload: dict[str, Any] | None = None
    correlation_hints: list[str] = Field(default_factory=list)
    priority_modifiers: dict[str, float] = Field(default_factory=dict)


class FusedIntelligence(BaseModel):
    """Fused intelligence output from correlation engine."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    tier: IntelTier
    priority_score: float = Field(ge=0.0, le=100.0)
    categories: list[IntelCategory]
    sources: list[IntelSource]
    source_signals: list[str]  # IDs of contributing signals
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    jurisdiction: str
    title: str
    summary: str
    entities: dict[str, Any] = Field(default_factory=dict)
    correlations: list[dict[str, Any]] = Field(default_factory=list)
    threat_assessment: dict[str, Any] | None = None
    recommended_actions: list[str] = Field(default_factory=list)
    routing_destinations: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    expiration: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OrchestrationConfig(BaseModel):
    """Configuration for the Intelligence Orchestrator."""
    enabled: bool = True
    max_concurrent_pipelines: int = 10
    signal_buffer_size: int = 10000
    fusion_batch_size: int = 100
    fusion_interval_seconds: float = 1.0
    correlation_threshold: float = 0.6
    priority_threshold: float = 30.0
    auto_route_enabled: bool = True
    websocket_broadcast_enabled: bool = True
    audit_logging_enabled: bool = True
    knowledge_graph_sync_enabled: bool = True
    degraded_mode_threshold: int = 5  # Consecutive errors before degraded mode
    sources_enabled: dict[str, bool] = Field(default_factory=lambda: {
        source.value: True for source in IntelSource
    })


class OrchestrationMetrics(BaseModel):
    """Metrics for orchestration performance."""
    signals_received: int = 0
    signals_processed: int = 0
    signals_dropped: int = 0
    fusions_created: int = 0
    alerts_routed: int = 0
    correlations_found: int = 0
    avg_processing_time_ms: float = 0.0
    pipeline_errors: int = 0
    last_signal_time: datetime | None = None
    last_fusion_time: datetime | None = None
    uptime_seconds: float = 0.0


class IntelOrchestrator:
    """
    Master Intelligence Orchestrator.

    Coordinates all intelligence sources, engines, and subsystems across
    the G3TI RTCC-UIP platform.
    """

    def __init__(self, config: OrchestrationConfig | None = None):
        self.config = config or OrchestrationConfig()
        self.status = OrchestrationStatus.INITIALIZING
        self.metrics = OrchestrationMetrics()
        self._start_time: datetime | None = None
        self._signal_queue: asyncio.Queue[IntelSignal] = asyncio.Queue(
            maxsize=self.config.signal_buffer_size
        )
        self._fusion_queue: asyncio.Queue[FusedIntelligence] = asyncio.Queue()
        self._running = False
        self._tasks: list[asyncio.Task] = []
        self._error_count = 0
        self._source_handlers: dict[IntelSource, Callable] = {}
        self._pipeline_handlers: dict[str, Callable] = {}
        self._websocket_connections: set = set()

        # Component references (injected during initialization)
        self._correlator = None
        self._rules_engine = None
        self._alerts_router = None
        self._knowledge_graph_sync = None
        self._audit_log = None
        self._pipelines: dict[str, Any] = {}

        logger.info("IntelOrchestrator initialized with config: %s", self.config)

    async def initialize(
        self,
        correlator=None,
        rules_engine=None,
        alerts_router=None,
        knowledge_graph_sync=None,
        audit_log=None,
    ):
        """Initialize orchestrator with component dependencies."""
        self._correlator = correlator
        self._rules_engine = rules_engine
        self._alerts_router = alerts_router
        self._knowledge_graph_sync = knowledge_graph_sync
        self._audit_log = audit_log

        if self._audit_log and self.config.audit_logging_enabled:
            await self._audit_log.log_action(
                action="orchestrator_initialized",
                details={"config": self.config.model_dump()},
            )

        logger.info("IntelOrchestrator components initialized")

    async def start(self):
        """Start the orchestration engine."""
        if self._running:
            logger.warning("Orchestrator already running")
            return

        self._running = True
        self._start_time = datetime.now(UTC)
        self.status = OrchestrationStatus.RUNNING

        # Start background tasks
        self._tasks = [
            asyncio.create_task(self._signal_processor()),
            asyncio.create_task(self._fusion_processor()),
            asyncio.create_task(self._metrics_updater()),
        ]

        if self._audit_log and self.config.audit_logging_enabled:
            await self._audit_log.log_action(
                action="orchestrator_started",
                details={"start_time": self._start_time.isoformat()},
            )

        logger.info("IntelOrchestrator started")

    async def stop(self):
        """Stop the orchestration engine."""
        self._running = False
        self.status = OrchestrationStatus.STOPPED

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._tasks.clear()

        if self._audit_log and self.config.audit_logging_enabled:
            await self._audit_log.log_action(
                action="orchestrator_stopped",
                details={"uptime_seconds": self.metrics.uptime_seconds},
            )

        logger.info("IntelOrchestrator stopped")

    async def pause(self):
        """Pause signal processing."""
        self.status = OrchestrationStatus.PAUSED
        logger.info("IntelOrchestrator paused")

    async def resume(self):
        """Resume signal processing."""
        if self._running:
            self.status = OrchestrationStatus.RUNNING
            logger.info("IntelOrchestrator resumed")

    async def ingest_signal(self, signal: IntelSignal) -> bool:
        """
        Ingest a raw intelligence signal into the orchestration pipeline.

        Returns True if signal was accepted, False if dropped.
        """
        if not self._running or self.status == OrchestrationStatus.PAUSED:
            logger.debug("Signal dropped - orchestrator not running or paused")
            self.metrics.signals_dropped += 1
            return False

        if not self.config.sources_enabled.get(signal.source.value, True):
            logger.debug("Signal dropped - source %s disabled", signal.source)
            self.metrics.signals_dropped += 1
            return False

        try:
            self._signal_queue.put_nowait(signal)
            self.metrics.signals_received += 1
            self.metrics.last_signal_time = datetime.now(UTC)

            if self._audit_log and self.config.audit_logging_enabled:
                await self._audit_log.log_action(
                    action="signal_ingested",
                    details={
                        "signal_id": signal.id,
                        "source": signal.source.value,
                        "category": signal.category.value,
                    },
                )

            return True
        except asyncio.QueueFull:
            logger.warning("Signal queue full - dropping signal %s", signal.id)
            self.metrics.signals_dropped += 1
            return False

    async def ingest_signals_batch(self, signals: list[IntelSignal]) -> int:
        """Ingest multiple signals. Returns count of accepted signals."""
        accepted = 0
        for signal in signals:
            if await self.ingest_signal(signal):
                accepted += 1
        return accepted

    async def _signal_processor(self):
        """Background task to process incoming signals."""
        batch: list[IntelSignal] = []
        last_process_time = datetime.now(UTC)

        while self._running:
            try:
                # Collect signals into batch
                try:
                    signal = await asyncio.wait_for(
                        self._signal_queue.get(),
                        timeout=self.config.fusion_interval_seconds,
                    )
                    batch.append(signal)
                except TimeoutError:
                    pass

                # Process batch if interval elapsed or batch full
                now = datetime.now(UTC)
                elapsed = (now - last_process_time).total_seconds()

                if batch and (
                    len(batch) >= self.config.fusion_batch_size
                    or elapsed >= self.config.fusion_interval_seconds
                ):
                    await self._process_signal_batch(batch)
                    batch = []
                    last_process_time = now

            except Exception as e:
                logger.error("Error in signal processor: %s", e)
                self._error_count += 1
                self._check_degraded_mode()

    async def _process_signal_batch(self, signals: list[IntelSignal]):
        """Process a batch of signals through the pipeline."""
        start_time = datetime.now(UTC)

        for signal in signals:
            try:
                # Normalize signal
                normalized = await self._normalize_signal(signal)

                # Enrich signal
                enriched = await self._enrich_signal(normalized)

                # Correlate with existing intelligence
                if self._correlator:
                    correlations = await self._correlator.correlate(enriched)
                    enriched.metadata["correlations"] = correlations

                # Score priority
                if self._rules_engine:
                    priority = await self._rules_engine.calculate_priority(enriched)
                    enriched.priority_modifiers["calculated"] = priority

                # Check if signal should be fused
                if self._should_fuse(enriched):
                    fused = await self._create_fusion(enriched)
                    await self._fusion_queue.put(fused)

                self.metrics.signals_processed += 1

            except Exception as e:
                logger.error("Error processing signal %s: %s", signal.id, e)
                self.metrics.pipeline_errors += 1

        # Update processing time metric
        elapsed_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
        self.metrics.avg_processing_time_ms = (
            self.metrics.avg_processing_time_ms * 0.9 + elapsed_ms * 0.1
        )

    async def _normalize_signal(self, signal: IntelSignal) -> IntelSignal:
        """Normalize signal data to standard format."""
        # Apply source-specific normalization
        handler = self._source_handlers.get(signal.source)
        if handler:
            signal = await handler(signal)

        # Ensure required fields
        if not signal.metadata.get("normalized"):
            signal.metadata["normalized"] = True
            signal.metadata["normalized_at"] = datetime.now(UTC).isoformat()

        return signal

    async def _enrich_signal(self, signal: IntelSignal) -> IntelSignal:
        """Enrich signal with additional context."""
        # Add jurisdiction context
        signal.metadata["enriched"] = True
        signal.metadata["enriched_at"] = datetime.now(UTC).isoformat()

        # Add source reliability score
        source_reliability = self._get_source_reliability(signal.source)
        signal.metadata["source_reliability"] = source_reliability

        # Adjust confidence based on source reliability
        signal.confidence = signal.confidence * source_reliability

        return signal

    def _get_source_reliability(self, source: IntelSource) -> float:
        """Get reliability score for a source (0.0 - 1.0)."""
        reliability_scores = {
            IntelSource.AI_ENGINE: 0.85,
            IntelSource.TACTICAL_ENGINE: 0.90,
            IntelSource.INVESTIGATIONS_ENGINE: 0.95,
            IntelSource.OFFICER_SAFETY: 0.95,
            IntelSource.DISPATCH_COMMS: 0.90,
            IntelSource.FEDERAL_NDEX: 0.98,
            IntelSource.FEDERAL_NCIC: 0.99,
            IntelSource.FEDERAL_ETRACE: 0.97,
            IntelSource.FEDERAL_DHS_SAR: 0.96,
            IntelSource.FEDERATION_HUB: 0.88,
            IntelSource.DATA_LAKE: 0.92,
            IntelSource.ETL_PIPELINE: 0.85,
            IntelSource.EXTERNAL_FEED: 0.75,
        }
        return reliability_scores.get(source, 0.80)

    def _should_fuse(self, signal: IntelSignal) -> bool:
        """Determine if signal should trigger fusion."""
        # Check correlation threshold
        correlations = signal.metadata.get("correlations", [])
        if correlations:
            max_correlation = max(c.get("score", 0) for c in correlations)
            if max_correlation >= self.config.correlation_threshold:
                return True

        # Check priority threshold
        priority = signal.priority_modifiers.get("calculated", 0)
        if priority >= self.config.priority_threshold:
            return True

        # Check for high-confidence signals
        if signal.confidence >= 0.9:
            return True

        return False

    async def _create_fusion(self, signal: IntelSignal) -> FusedIntelligence:
        """Create fused intelligence from signal and correlations."""
        correlations = signal.metadata.get("correlations", [])
        priority = signal.priority_modifiers.get("calculated", 50.0)

        # Determine tier based on priority
        tier = self._determine_tier(priority, signal)

        # Generate title and summary
        title = self._generate_title(signal)
        summary = self._generate_summary(signal, correlations)

        # Determine routing destinations
        destinations = self._determine_routing(tier, signal)

        fused = FusedIntelligence(
            tier=tier,
            priority_score=priority,
            categories=[signal.category],
            sources=[signal.source],
            source_signals=[signal.id],
            jurisdiction=signal.jurisdiction,
            title=title,
            summary=summary,
            entities=signal.data,
            correlations=correlations,
            recommended_actions=self._generate_recommendations(tier, signal),
            routing_destinations=destinations,
            confidence=signal.confidence,
            metadata={
                "original_signal": signal.id,
                "fusion_time": datetime.now(UTC).isoformat(),
            },
        )

        self.metrics.fusions_created += 1
        self.metrics.last_fusion_time = datetime.now(UTC)

        return fused

    def _determine_tier(self, priority: float, signal: IntelSignal) -> IntelTier:
        """Determine intelligence tier based on priority and signal."""
        # Officer safety always gets Tier 1
        if signal.source == IntelSource.OFFICER_SAFETY:
            return IntelTier.TIER_1

        # Priority-based tier assignment
        if priority >= 80:
            return IntelTier.TIER_1
        elif priority >= 60:
            return IntelTier.TIER_2
        elif priority >= 40:
            return IntelTier.TIER_3
        else:
            return IntelTier.TIER_4

    def _generate_title(self, signal: IntelSignal) -> str:
        """Generate a title for fused intelligence."""
        category_titles = {
            IntelCategory.PERSON: "Person of Interest Alert",
            IntelCategory.VEHICLE: "Vehicle Intelligence",
            IntelCategory.WEAPON: "Weapon Detection Alert",
            IntelCategory.INCIDENT: "Incident Intelligence",
            IntelCategory.PATTERN: "Pattern Detection",
            IntelCategory.GEOGRAPHIC: "Geographic Intelligence",
            IntelCategory.TEMPORAL: "Temporal Pattern Alert",
            IntelCategory.NETWORK: "Network Analysis",
            IntelCategory.THREAT: "Threat Assessment",
            IntelCategory.LEAD: "Investigative Lead",
        }
        return category_titles.get(signal.category, "Intelligence Alert")

    def _generate_summary(
        self, signal: IntelSignal, correlations: list[dict]
    ) -> str:
        """Generate a summary for fused intelligence."""
        parts = [
            f"Source: {signal.source.value}",
            f"Category: {signal.category.value}",
            f"Confidence: {signal.confidence:.0%}",
        ]

        if correlations:
            parts.append(f"Correlations: {len(correlations)} entities linked")

        return " | ".join(parts)

    def _determine_routing(
        self, tier: IntelTier, signal: IntelSignal
    ) -> list[str]:
        """Determine routing destinations based on tier and signal."""
        destinations = ["rtcc_dashboard"]

        if tier == IntelTier.TIER_1:
            destinations.extend([
                "officer_safety_alerts",
                "dispatch_comms",
                "mobile_mdt",
                "tactical_dashboard",
            ])
        elif tier == IntelTier.TIER_2:
            destinations.extend([
                "investigations_dashboard",
                "tactical_dashboard",
            ])
        elif tier == IntelTier.TIER_3:
            destinations.append("tactical_dashboard")

        # Source-specific routing
        if signal.source == IntelSource.INVESTIGATIONS_ENGINE:
            if "investigations_dashboard" not in destinations:
                destinations.append("investigations_dashboard")

        return destinations

    def _generate_recommendations(
        self, tier: IntelTier, signal: IntelSignal
    ) -> list[str]:
        """Generate recommended actions based on tier and signal."""
        recommendations = []

        if tier == IntelTier.TIER_1:
            recommendations.extend([
                "Immediate officer notification required",
                "Dispatch backup units if applicable",
                "Monitor real-time location updates",
            ])
        elif tier == IntelTier.TIER_2:
            recommendations.extend([
                "Assign to investigator for follow-up",
                "Cross-reference with open cases",
                "Document in case management system",
            ])
        elif tier == IntelTier.TIER_3:
            recommendations.extend([
                "Add to tactical awareness briefing",
                "Monitor for pattern development",
            ])
        else:
            recommendations.append("Archive for future reference")

        return recommendations

    async def _fusion_processor(self):
        """Background task to process fused intelligence."""
        while self._running:
            try:
                fused = await asyncio.wait_for(
                    self._fusion_queue.get(),
                    timeout=1.0,
                )

                # Route the fused intelligence
                if self._alerts_router and self.config.auto_route_enabled:
                    await self._alerts_router.route(fused)
                    self.metrics.alerts_routed += 1

                # Sync to knowledge graph
                if self._knowledge_graph_sync and self.config.knowledge_graph_sync_enabled:
                    await self._knowledge_graph_sync.sync_intelligence(fused)

                # Broadcast via WebSocket
                if self.config.websocket_broadcast_enabled:
                    await self._broadcast_fusion(fused)

                # Audit log
                if self._audit_log and self.config.audit_logging_enabled:
                    await self._audit_log.log_action(
                        action="fusion_processed",
                        details={
                            "fusion_id": fused.id,
                            "tier": fused.tier.value,
                            "priority": fused.priority_score,
                            "destinations": fused.routing_destinations,
                        },
                    )

            except TimeoutError:
                continue
            except Exception as e:
                logger.error("Error in fusion processor: %s", e)
                self._error_count += 1
                self._check_degraded_mode()

    async def _broadcast_fusion(self, fused: FusedIntelligence):
        """Broadcast fused intelligence to WebSocket connections."""
        message = {
            "type": "fused_intelligence",
            "data": fused.model_dump(mode="json"),
        }

        for ws in list(self._websocket_connections):
            try:
                await ws.send_json(message)
            except Exception:
                self._websocket_connections.discard(ws)

    async def _metrics_updater(self):
        """Background task to update metrics."""
        while self._running:
            try:
                await asyncio.sleep(1.0)

                if self._start_time:
                    self.metrics.uptime_seconds = (
                        datetime.now(UTC) - self._start_time
                    ).total_seconds()

            except Exception as e:
                logger.error("Error in metrics updater: %s", e)

    def _check_degraded_mode(self):
        """Check if system should enter degraded mode."""
        if self._error_count >= self.config.degraded_mode_threshold:
            if self.status != OrchestrationStatus.DEGRADED:
                self.status = OrchestrationStatus.DEGRADED
                logger.warning("Orchestrator entering degraded mode")

    def register_websocket(self, websocket):
        """Register a WebSocket connection for broadcasts."""
        self._websocket_connections.add(websocket)

    def unregister_websocket(self, websocket):
        """Unregister a WebSocket connection."""
        self._websocket_connections.discard(websocket)

    def register_source_handler(
        self, source: IntelSource, handler: Callable
    ):
        """Register a custom handler for a source."""
        self._source_handlers[source] = handler

    def get_status(self) -> dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "status": self.status.value,
            "config": self.config.model_dump(),
            "metrics": self.metrics.model_dump(),
            "queue_sizes": {
                "signal_queue": self._signal_queue.qsize(),
                "fusion_queue": self._fusion_queue.qsize(),
            },
            "active_tasks": len(self._tasks),
            "websocket_connections": len(self._websocket_connections),
        }

    def get_metrics(self) -> OrchestrationMetrics:
        """Get current metrics."""
        return self.metrics
