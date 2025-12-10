"""
Grid Fusion Engine.

Correlates and fuses data from multiple sensor sources with LPR, drones, and CAD.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class CorrelationType(str, Enum):
    """Types of correlations between data sources."""
    SENSOR_SENSOR = "sensor_sensor"
    SENSOR_LPR = "sensor_lpr"
    SENSOR_DRONE = "sensor_drone"
    SENSOR_CAD = "sensor_cad"
    LPR_DRONE = "lpr_drone"
    LPR_CAD = "lpr_cad"
    DRONE_CAD = "drone_cad"
    MULTI_SOURCE = "multi_source"


class FusionConfidence(str, Enum):
    """Confidence levels for fused events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class DataSource(BaseModel):
    """Data source in a fused event."""
    source_id: str
    source_type: str
    timestamp: datetime
    latitude: float
    longitude: float
    data: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0


class FusedEvent(BaseModel):
    """Fused event from multiple data sources."""
    fusion_id: str
    correlation_type: CorrelationType
    confidence: FusionConfidence = FusionConfidence.MEDIUM
    confidence_score: float = 0.5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    center_latitude: float
    center_longitude: float
    radius_m: float = 100.0
    sources: list[DataSource] = Field(default_factory=list)
    event_type: str = ""
    description: str = ""
    severity: str = "info"
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    incident_id: Optional[str] = None
    zone_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CorrelationRule(BaseModel):
    """Rule for correlating data sources."""
    rule_id: str
    name: str
    source_types: list[str]
    correlation_type: CorrelationType
    time_window_seconds: int = 60
    distance_threshold_m: float = 500.0
    min_sources: int = 2
    confidence_boost: float = 0.1
    enabled: bool = True
    priority: int = 1
    tags: list[str] = Field(default_factory=list)


class FusionConfig(BaseModel):
    """Configuration for grid fusion engine."""
    max_fused_events: int = 50000
    default_time_window_seconds: int = 60
    default_distance_threshold_m: float = 500.0
    auto_verify_threshold: float = 0.9
    min_confidence_threshold: float = 0.3


class FusionMetrics(BaseModel):
    """Metrics for grid fusion engine."""
    total_fusions: int = 0
    fusions_by_type: dict[str, int] = Field(default_factory=dict)
    fusions_by_confidence: dict[str, int] = Field(default_factory=dict)
    active_fusions: int = 0
    verified_fusions: int = 0
    avg_sources_per_fusion: float = 0.0


class GridFusionEngine:
    """
    Grid Fusion Engine.
    
    Correlates and fuses data from multiple sensor sources with LPR, drones, and CAD.
    """
    
    def __init__(self, config: Optional[FusionConfig] = None):
        self.config = config or FusionConfig()
        self._fused_events: dict[str, FusedEvent] = {}
        self._event_history: deque[FusedEvent] = deque(maxlen=self.config.max_fused_events)
        self._rules: dict[str, CorrelationRule] = {}
        self._pending_sources: deque[DataSource] = deque(maxlen=10000)
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = FusionMetrics()
        
        self._init_default_rules()
    
    def _init_default_rules(self) -> None:
        """Initialize default correlation rules."""
        default_rules = [
            CorrelationRule(
                rule_id="rule-gunshot-lpr",
                name="Gunshot + LPR Correlation",
                source_types=["gunshot", "lpr"],
                correlation_type=CorrelationType.SENSOR_LPR,
                time_window_seconds=120,
                distance_threshold_m=300.0,
                confidence_boost=0.2,
                tags=["gunshot", "vehicle"],
            ),
            CorrelationRule(
                rule_id="rule-gunshot-drone",
                name="Gunshot + Drone Correlation",
                source_types=["gunshot", "drone_telemetry"],
                correlation_type=CorrelationType.SENSOR_DRONE,
                time_window_seconds=60,
                distance_threshold_m=500.0,
                confidence_boost=0.15,
                tags=["gunshot", "aerial"],
            ),
            CorrelationRule(
                rule_id="rule-crowd-environmental",
                name="Crowd + Environmental Correlation",
                source_types=["crowd_density", "environmental"],
                correlation_type=CorrelationType.SENSOR_SENSOR,
                time_window_seconds=300,
                distance_threshold_m=200.0,
                confidence_boost=0.1,
                tags=["crowd", "environmental"],
            ),
            CorrelationRule(
                rule_id="rule-panic-cad",
                name="Panic Beacon + CAD Correlation",
                source_types=["panic_beacon", "cad_incident"],
                correlation_type=CorrelationType.SENSOR_CAD,
                time_window_seconds=180,
                distance_threshold_m=100.0,
                confidence_boost=0.25,
                tags=["panic", "emergency"],
            ),
            CorrelationRule(
                rule_id="rule-lpr-cad",
                name="LPR + CAD Correlation",
                source_types=["lpr", "cad_incident"],
                correlation_type=CorrelationType.LPR_CAD,
                time_window_seconds=300,
                distance_threshold_m=500.0,
                confidence_boost=0.2,
                tags=["vehicle", "incident"],
            ),
            CorrelationRule(
                rule_id="rule-multi-sensor",
                name="Multi-Sensor Correlation",
                source_types=["gunshot", "crowd_density", "environmental", "panic_beacon"],
                correlation_type=CorrelationType.MULTI_SOURCE,
                time_window_seconds=120,
                distance_threshold_m=300.0,
                min_sources=3,
                confidence_boost=0.3,
                tags=["multi-source"],
            ),
        ]
        
        for rule in default_rules:
            self._rules[rule.rule_id] = rule
    
    async def start(self) -> None:
        """Start the fusion engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the fusion engine."""
        self._running = False
    
    async def add_source(
        self,
        source_id: str,
        source_type: str,
        latitude: float,
        longitude: float,
        data: Optional[dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> DataSource:
        """Add a data source for potential fusion."""
        source = DataSource(
            source_id=source_id,
            source_type=source_type,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            data=data or {},
            confidence=confidence,
        )
        
        self._pending_sources.append(source)
        
        await self._process_correlations(source)
        
        return source
    
    async def _process_correlations(self, new_source: DataSource) -> None:
        """Process correlations for a new data source."""
        for rule in self._rules.values():
            if not rule.enabled:
                continue
            
            if new_source.source_type not in rule.source_types:
                continue
            
            matching_sources = self._find_matching_sources(new_source, rule)
            
            if len(matching_sources) >= rule.min_sources - 1:
                all_sources = [new_source] + matching_sources
                await self._create_or_update_fusion(all_sources, rule)
    
    def _find_matching_sources(
        self,
        source: DataSource,
        rule: CorrelationRule,
    ) -> list[DataSource]:
        """Find sources matching a correlation rule."""
        matches = []
        cutoff_time = source.timestamp.timestamp() - rule.time_window_seconds
        
        for pending in self._pending_sources:
            if pending.source_id == source.source_id:
                continue
            
            if pending.source_type not in rule.source_types:
                continue
            
            if pending.source_type == source.source_type:
                continue
            
            if pending.timestamp.timestamp() < cutoff_time:
                continue
            
            distance = self._calculate_distance(
                source.latitude, source.longitude,
                pending.latitude, pending.longitude,
            ) * 1000
            
            if distance <= rule.distance_threshold_m:
                matches.append(pending)
        
        return matches
    
    async def _create_or_update_fusion(
        self,
        sources: list[DataSource],
        rule: CorrelationRule,
    ) -> FusedEvent:
        """Create or update a fused event."""
        existing = self._find_existing_fusion(sources)
        
        if existing:
            for source in sources:
                if not any(s.source_id == source.source_id for s in existing.sources):
                    existing.sources.append(source)
            
            existing.updated_at = datetime.now(timezone.utc)
            existing.confidence_score = min(1.0, existing.confidence_score + rule.confidence_boost)
            existing.confidence = self._score_to_confidence(existing.confidence_score)
            
            self._recalculate_center(existing)
            
            await self._notify_callbacks(existing, "updated")
            return existing
        
        center_lat = sum(s.latitude for s in sources) / len(sources)
        center_lon = sum(s.longitude for s in sources) / len(sources)
        
        max_distance = 0.0
        for s in sources:
            dist = self._calculate_distance(center_lat, center_lon, s.latitude, s.longitude) * 1000
            max_distance = max(max_distance, dist)
        
        base_confidence = sum(s.confidence for s in sources) / len(sources)
        confidence_score = min(1.0, base_confidence * 0.5 + rule.confidence_boost + (len(sources) - 2) * 0.1)
        
        event_type = self._determine_event_type(sources)
        severity = self._determine_severity(sources, confidence_score)
        
        fusion = FusedEvent(
            fusion_id=f"fusion-{uuid.uuid4().hex[:12]}",
            correlation_type=rule.correlation_type,
            confidence=self._score_to_confidence(confidence_score),
            confidence_score=confidence_score,
            center_latitude=center_lat,
            center_longitude=center_lon,
            radius_m=max(100.0, max_distance * 1.2),
            sources=sources,
            event_type=event_type,
            description=f"Fused event from {len(sources)} sources: {', '.join(s.source_type for s in sources)}",
            severity=severity,
            tags=rule.tags.copy(),
        )
        
        if confidence_score >= self.config.auto_verify_threshold:
            fusion.verified = True
            fusion.verified_at = datetime.now(timezone.utc)
        
        self._fused_events[fusion.fusion_id] = fusion
        self._event_history.append(fusion)
        
        self._metrics.total_fusions += 1
        self._update_metrics()
        
        await self._notify_callbacks(fusion, "created")
        
        return fusion
    
    def _find_existing_fusion(self, sources: list[DataSource]) -> Optional[FusedEvent]:
        """Find an existing fusion that matches the sources."""
        source_ids = {s.source_id for s in sources}
        
        for fusion in self._fused_events.values():
            fusion_source_ids = {s.source_id for s in fusion.sources}
            if source_ids & fusion_source_ids:
                return fusion
        
        return None
    
    def _recalculate_center(self, fusion: FusedEvent) -> None:
        """Recalculate the center point of a fusion."""
        if not fusion.sources:
            return
        
        fusion.center_latitude = sum(s.latitude for s in fusion.sources) / len(fusion.sources)
        fusion.center_longitude = sum(s.longitude for s in fusion.sources) / len(fusion.sources)
        
        max_distance = 0.0
        for s in fusion.sources:
            dist = self._calculate_distance(
                fusion.center_latitude, fusion.center_longitude,
                s.latitude, s.longitude,
            ) * 1000
            max_distance = max(max_distance, dist)
        
        fusion.radius_m = max(100.0, max_distance * 1.2)
    
    def _determine_event_type(self, sources: list[DataSource]) -> str:
        """Determine the event type based on sources."""
        source_types = {s.source_type for s in sources}
        
        if "gunshot" in source_types:
            return "gunshot_incident"
        if "panic_beacon" in source_types:
            return "emergency_alert"
        if "crowd_density" in source_types and "environmental" in source_types:
            return "crowd_hazard"
        if "lpr" in source_types:
            return "vehicle_incident"
        
        return "multi_source_event"
    
    def _determine_severity(self, sources: list[DataSource], confidence: float) -> str:
        """Determine severity based on sources and confidence."""
        source_types = {s.source_type for s in sources}
        
        if "gunshot" in source_types or "panic_beacon" in source_types:
            return "critical" if confidence > 0.7 else "high"
        
        if confidence > 0.8:
            return "high"
        if confidence > 0.5:
            return "medium"
        
        return "low"
    
    def _score_to_confidence(self, score: float) -> FusionConfidence:
        """Convert confidence score to confidence level."""
        if score >= 0.9:
            return FusionConfidence.VERIFIED
        if score >= 0.7:
            return FusionConfidence.HIGH
        if score >= 0.4:
            return FusionConfidence.MEDIUM
        return FusionConfidence.LOW
    
    async def verify_fusion(
        self,
        fusion_id: str,
        verified_by: str,
    ) -> bool:
        """Verify a fused event."""
        fusion = self._fused_events.get(fusion_id)
        if not fusion:
            return False
        
        fusion.verified = True
        fusion.verified_by = verified_by
        fusion.verified_at = datetime.now(timezone.utc)
        fusion.confidence = FusionConfidence.VERIFIED
        fusion.confidence_score = 1.0
        
        self._metrics.verified_fusions += 1
        
        await self._notify_callbacks(fusion, "verified")
        return True
    
    async def link_to_incident(
        self,
        fusion_id: str,
        incident_id: str,
    ) -> bool:
        """Link a fused event to an incident."""
        fusion = self._fused_events.get(fusion_id)
        if not fusion:
            return False
        
        fusion.incident_id = incident_id
        fusion.updated_at = datetime.now(timezone.utc)
        
        await self._notify_callbacks(fusion, "linked")
        return True
    
    def get_fusion(self, fusion_id: str) -> Optional[FusedEvent]:
        """Get a fused event by ID."""
        return self._fused_events.get(fusion_id)
    
    def get_active_fusions(self) -> list[FusedEvent]:
        """Get all active fused events."""
        return list(self._fused_events.values())
    
    def get_fusions_by_type(self, correlation_type: CorrelationType) -> list[FusedEvent]:
        """Get fusions by correlation type."""
        return [f for f in self._fused_events.values() if f.correlation_type == correlation_type]
    
    def get_fusions_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[FusedEvent]:
        """Get fusions within a geographic area."""
        result = []
        for fusion in self._fused_events.values():
            distance = self._calculate_distance(
                center_lat, center_lon,
                fusion.center_latitude, fusion.center_longitude,
            )
            if distance <= radius_km:
                result.append(fusion)
        return result
    
    def get_recent_fusions(self, limit: int = 100) -> list[FusedEvent]:
        """Get recent fused events."""
        fusions = list(self._event_history)
        fusions.reverse()
        return fusions[:limit]
    
    def get_rule(self, rule_id: str) -> Optional[CorrelationRule]:
        """Get a correlation rule by ID."""
        return self._rules.get(rule_id)
    
    def get_all_rules(self) -> list[CorrelationRule]:
        """Get all correlation rules."""
        return list(self._rules.values())
    
    def add_rule(self, rule: CorrelationRule) -> None:
        """Add a correlation rule."""
        self._rules[rule.rule_id] = rule
    
    def update_rule(
        self,
        rule_id: str,
        enabled: Optional[bool] = None,
        time_window_seconds: Optional[int] = None,
        distance_threshold_m: Optional[float] = None,
    ) -> bool:
        """Update a correlation rule."""
        rule = self._rules.get(rule_id)
        if not rule:
            return False
        
        if enabled is not None:
            rule.enabled = enabled
        if time_window_seconds is not None:
            rule.time_window_seconds = time_window_seconds
        if distance_threshold_m is not None:
            rule.distance_threshold_m = distance_threshold_m
        
        return True
    
    def get_metrics(self) -> FusionMetrics:
        """Get fusion metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get fusion engine status."""
        return {
            "running": self._running,
            "total_fusions": len(self._fused_events),
            "pending_sources": len(self._pending_sources),
            "active_rules": len([r for r in self._rules.values() if r.enabled]),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for fusion events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update fusion metrics."""
        type_counts: dict[str, int] = {}
        confidence_counts: dict[str, int] = {}
        total_sources = 0
        verified = 0
        
        for fusion in self._fused_events.values():
            type_counts[fusion.correlation_type.value] = type_counts.get(fusion.correlation_type.value, 0) + 1
            confidence_counts[fusion.confidence.value] = confidence_counts.get(fusion.confidence.value, 0) + 1
            total_sources += len(fusion.sources)
            if fusion.verified:
                verified += 1
        
        self._metrics.fusions_by_type = type_counts
        self._metrics.fusions_by_confidence = confidence_counts
        self._metrics.active_fusions = len(self._fused_events)
        self._metrics.verified_fusions = verified
        self._metrics.avg_sources_per_fusion = total_sources / len(self._fused_events) if self._fused_events else 0.0
    
    async def _notify_callbacks(self, fusion: FusedEvent, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(fusion, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        import math
        
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
