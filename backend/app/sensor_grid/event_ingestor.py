"""
Sensor Event Ingestor.

Handles ingestion and processing of sensor events from the smart sensor grid.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class EventSeverity(str, Enum):
    """Severity levels for sensor events."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventCategory(str, Enum):
    """Categories of sensor events."""
    GUNSHOT = "gunshot"
    ENVIRONMENTAL = "environmental"
    CROWD = "crowd"
    STRUCTURAL = "structural"
    PANIC = "panic"
    PRESENCE = "presence"
    TRAFFIC = "traffic"
    WEATHER = "weather"
    HAZMAT = "hazmat"
    SECURITY = "security"


class SensorEvent(BaseModel):
    """Sensor event model."""
    event_id: str
    sensor_id: str
    sensor_type: str
    category: EventCategory
    severity: EventSeverity = EventSeverity.INFO
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    value: Optional[float] = None
    unit: Optional[str] = None
    description: str = ""
    confidence: float = 1.0
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    correlated_events: list[str] = Field(default_factory=list)
    incident_id: Optional[str] = None
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GunshotEvent(BaseModel):
    """Gunshot detection event."""
    event_id: str
    sensor_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    confidence: float
    caliber_estimate: Optional[str] = None
    shot_count: int = 1
    direction_deg: Optional[float] = None
    distance_m: Optional[float] = None
    audio_signature_id: Optional[str] = None
    triangulated: bool = False
    triangulation_sensors: list[str] = Field(default_factory=list)


class EnvironmentalEvent(BaseModel):
    """Environmental sensor event."""
    event_id: str
    sensor_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    event_type: str
    value: float
    unit: str
    threshold_exceeded: bool = False
    threshold_value: Optional[float] = None
    hazard_level: str = "none"
    recommended_action: Optional[str] = None


class CrowdEvent(BaseModel):
    """Crowd density event."""
    event_id: str
    sensor_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    density_level: str
    estimated_count: int
    area_sq_m: float
    density_per_sq_m: float
    trend: str = "stable"
    alert_triggered: bool = False


class PanicEvent(BaseModel):
    """Panic beacon activation event."""
    event_id: str
    sensor_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    beacon_id: str
    activation_type: str
    user_id: Optional[str] = None
    message: Optional[str] = None
    audio_recording_id: Optional[str] = None


class IngestorConfig(BaseModel):
    """Configuration for sensor event ingestor."""
    max_events_stored: int = 100000
    event_ttl_hours: int = 24
    batch_size: int = 100
    auto_correlate: bool = True
    correlation_window_seconds: int = 60
    correlation_radius_m: float = 500.0


class IngestorMetrics(BaseModel):
    """Metrics for sensor event ingestor."""
    total_events_ingested: int = 0
    events_by_category: dict[str, int] = Field(default_factory=dict)
    events_by_severity: dict[str, int] = Field(default_factory=dict)
    events_per_minute: float = 0.0
    active_events: int = 0
    correlated_events: int = 0


class SensorEventIngestor:
    """
    Sensor Event Ingestor.
    
    Handles ingestion and processing of sensor events from the smart sensor grid.
    """
    
    def __init__(self, config: Optional[IngestorConfig] = None):
        self.config = config or IngestorConfig()
        self._events: dict[str, SensorEvent] = {}
        self._event_history: deque[SensorEvent] = deque(maxlen=self.config.max_events_stored)
        self._gunshot_events: deque[GunshotEvent] = deque(maxlen=10000)
        self._environmental_events: deque[EnvironmentalEvent] = deque(maxlen=10000)
        self._crowd_events: deque[CrowdEvent] = deque(maxlen=10000)
        self._panic_events: deque[PanicEvent] = deque(maxlen=10000)
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = IngestorMetrics()
    
    async def start(self) -> None:
        """Start the event ingestor."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the event ingestor."""
        self._running = False
    
    async def ingest_event(
        self,
        sensor_id: str,
        sensor_type: str,
        category: EventCategory,
        latitude: float,
        longitude: float,
        severity: EventSeverity = EventSeverity.INFO,
        value: Optional[float] = None,
        unit: Optional[str] = None,
        description: str = "",
        confidence: float = 1.0,
        raw_data: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> SensorEvent:
        """Ingest a sensor event."""
        event = SensorEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            category=category,
            severity=severity,
            latitude=latitude,
            longitude=longitude,
            value=value,
            unit=unit,
            description=description,
            confidence=confidence,
            raw_data=raw_data or {},
            metadata=metadata or {},
        )
        
        self._events[event.event_id] = event
        self._event_history.append(event)
        
        self._metrics.total_events_ingested += 1
        self._update_metrics()
        
        if self.config.auto_correlate:
            await self._correlate_event(event)
        
        await self._notify_callbacks(event, "ingested")
        
        return event
    
    async def ingest_gunshot(
        self,
        sensor_id: str,
        latitude: float,
        longitude: float,
        confidence: float,
        shot_count: int = 1,
        caliber_estimate: Optional[str] = None,
        direction_deg: Optional[float] = None,
        distance_m: Optional[float] = None,
    ) -> tuple[SensorEvent, GunshotEvent]:
        """Ingest a gunshot detection event."""
        gunshot = GunshotEvent(
            event_id=f"gunshot-{uuid.uuid4().hex[:12]}",
            sensor_id=sensor_id,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            confidence=confidence,
            shot_count=shot_count,
            caliber_estimate=caliber_estimate,
            direction_deg=direction_deg,
            distance_m=distance_m,
        )
        self._gunshot_events.append(gunshot)
        
        severity = EventSeverity.CRITICAL if confidence > 0.9 else EventSeverity.HIGH
        
        event = await self.ingest_event(
            sensor_id=sensor_id,
            sensor_type="gunshot",
            category=EventCategory.GUNSHOT,
            latitude=latitude,
            longitude=longitude,
            severity=severity,
            value=float(shot_count),
            unit="shots",
            description=f"Gunshot detected: {shot_count} shot(s), confidence {confidence:.0%}",
            confidence=confidence,
            metadata={
                "gunshot_event_id": gunshot.event_id,
                "caliber_estimate": caliber_estimate,
                "direction_deg": direction_deg,
            },
        )
        
        return event, gunshot
    
    async def ingest_environmental(
        self,
        sensor_id: str,
        event_type: str,
        latitude: float,
        longitude: float,
        value: float,
        unit: str,
        threshold_value: Optional[float] = None,
    ) -> tuple[SensorEvent, EnvironmentalEvent]:
        """Ingest an environmental sensor event."""
        threshold_exceeded = threshold_value is not None and value > threshold_value
        
        if threshold_exceeded:
            hazard_level = "high" if value > threshold_value * 1.5 else "medium"
        else:
            hazard_level = "low" if value > (threshold_value or 0) * 0.8 else "none"
        
        env_event = EnvironmentalEvent(
            event_id=f"env-{uuid.uuid4().hex[:12]}",
            sensor_id=sensor_id,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            event_type=event_type,
            value=value,
            unit=unit,
            threshold_exceeded=threshold_exceeded,
            threshold_value=threshold_value,
            hazard_level=hazard_level,
        )
        self._environmental_events.append(env_event)
        
        if threshold_exceeded:
            severity = EventSeverity.HIGH if hazard_level == "high" else EventSeverity.MEDIUM
        else:
            severity = EventSeverity.LOW if hazard_level == "low" else EventSeverity.INFO
        
        event = await self.ingest_event(
            sensor_id=sensor_id,
            sensor_type=f"environmental_{event_type}",
            category=EventCategory.ENVIRONMENTAL,
            latitude=latitude,
            longitude=longitude,
            severity=severity,
            value=value,
            unit=unit,
            description=f"Environmental {event_type}: {value} {unit}",
            metadata={
                "environmental_event_id": env_event.event_id,
                "threshold_exceeded": threshold_exceeded,
                "hazard_level": hazard_level,
            },
        )
        
        return event, env_event
    
    async def ingest_crowd_density(
        self,
        sensor_id: str,
        latitude: float,
        longitude: float,
        estimated_count: int,
        area_sq_m: float,
        trend: str = "stable",
    ) -> tuple[SensorEvent, CrowdEvent]:
        """Ingest a crowd density event."""
        density_per_sq_m = estimated_count / area_sq_m if area_sq_m > 0 else 0
        
        if density_per_sq_m > 4.0:
            density_level = "critical"
            severity = EventSeverity.CRITICAL
        elif density_per_sq_m > 2.5:
            density_level = "high"
            severity = EventSeverity.HIGH
        elif density_per_sq_m > 1.0:
            density_level = "medium"
            severity = EventSeverity.MEDIUM
        else:
            density_level = "low"
            severity = EventSeverity.INFO
        
        crowd_event = CrowdEvent(
            event_id=f"crowd-{uuid.uuid4().hex[:12]}",
            sensor_id=sensor_id,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            density_level=density_level,
            estimated_count=estimated_count,
            area_sq_m=area_sq_m,
            density_per_sq_m=density_per_sq_m,
            trend=trend,
            alert_triggered=density_level in ["critical", "high"],
        )
        self._crowd_events.append(crowd_event)
        
        event = await self.ingest_event(
            sensor_id=sensor_id,
            sensor_type="crowd_density",
            category=EventCategory.CROWD,
            latitude=latitude,
            longitude=longitude,
            severity=severity,
            value=float(estimated_count),
            unit="people",
            description=f"Crowd density: {estimated_count} people, {density_level} density",
            metadata={
                "crowd_event_id": crowd_event.event_id,
                "density_level": density_level,
                "density_per_sq_m": density_per_sq_m,
                "trend": trend,
            },
        )
        
        return event, crowd_event
    
    async def ingest_panic_beacon(
        self,
        sensor_id: str,
        beacon_id: str,
        latitude: float,
        longitude: float,
        activation_type: str,
        user_id: Optional[str] = None,
        message: Optional[str] = None,
    ) -> tuple[SensorEvent, PanicEvent]:
        """Ingest a panic beacon activation event."""
        panic_event = PanicEvent(
            event_id=f"panic-{uuid.uuid4().hex[:12]}",
            sensor_id=sensor_id,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            beacon_id=beacon_id,
            activation_type=activation_type,
            user_id=user_id,
            message=message,
        )
        self._panic_events.append(panic_event)
        
        event = await self.ingest_event(
            sensor_id=sensor_id,
            sensor_type="panic_beacon",
            category=EventCategory.PANIC,
            latitude=latitude,
            longitude=longitude,
            severity=EventSeverity.CRITICAL,
            description=f"Panic beacon activated: {activation_type}",
            metadata={
                "panic_event_id": panic_event.event_id,
                "beacon_id": beacon_id,
                "activation_type": activation_type,
                "user_id": user_id,
            },
        )
        
        return event, panic_event
    
    async def acknowledge_event(
        self,
        event_id: str,
        acknowledged_by: str,
    ) -> bool:
        """Acknowledge an event."""
        event = self._events.get(event_id)
        if not event:
            return False
        
        event.acknowledged = True
        event.acknowledged_by = acknowledged_by
        event.acknowledged_at = datetime.now(timezone.utc)
        
        await self._notify_callbacks(event, "acknowledged")
        return True
    
    async def verify_event(
        self,
        event_id: str,
        verified_by: str,
        verified: bool = True,
    ) -> bool:
        """Verify or reject an event."""
        event = self._events.get(event_id)
        if not event:
            return False
        
        event.verified = verified
        event.verified_by = verified_by
        event.verified_at = datetime.now(timezone.utc)
        
        await self._notify_callbacks(event, "verified" if verified else "rejected")
        return True
    
    async def resolve_event(
        self,
        event_id: str,
        resolved_by: str,
    ) -> bool:
        """Resolve an event."""
        event = self._events.get(event_id)
        if not event:
            return False
        
        event.resolved = True
        event.resolved_by = resolved_by
        event.resolved_at = datetime.now(timezone.utc)
        
        await self._notify_callbacks(event, "resolved")
        return True
    
    def get_event(self, event_id: str) -> Optional[SensorEvent]:
        """Get event by ID."""
        return self._events.get(event_id)
    
    def get_active_events(self) -> list[SensorEvent]:
        """Get all active (unresolved) events."""
        return [e for e in self._events.values() if not e.resolved]
    
    def get_events_by_category(self, category: EventCategory) -> list[SensorEvent]:
        """Get events by category."""
        return [e for e in self._events.values() if e.category == category]
    
    def get_events_by_severity(self, severity: EventSeverity) -> list[SensorEvent]:
        """Get events by severity."""
        return [e for e in self._events.values() if e.severity == severity]
    
    def get_events_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[SensorEvent]:
        """Get events within a geographic area."""
        result = []
        for event in self._events.values():
            distance = self._calculate_distance(
                center_lat, center_lon,
                event.latitude, event.longitude,
            )
            if distance <= radius_km:
                result.append(event)
        return result
    
    def get_recent_events(self, limit: int = 100) -> list[SensorEvent]:
        """Get recent events."""
        events = list(self._event_history)
        events.reverse()
        return events[:limit]
    
    def get_gunshot_events(self, limit: int = 100) -> list[GunshotEvent]:
        """Get recent gunshot events."""
        events = list(self._gunshot_events)
        events.reverse()
        return events[:limit]
    
    def get_environmental_events(self, limit: int = 100) -> list[EnvironmentalEvent]:
        """Get recent environmental events."""
        events = list(self._environmental_events)
        events.reverse()
        return events[:limit]
    
    def get_crowd_events(self, limit: int = 100) -> list[CrowdEvent]:
        """Get recent crowd events."""
        events = list(self._crowd_events)
        events.reverse()
        return events[:limit]
    
    def get_panic_events(self, limit: int = 100) -> list[PanicEvent]:
        """Get recent panic events."""
        events = list(self._panic_events)
        events.reverse()
        return events[:limit]
    
    def get_metrics(self) -> IngestorMetrics:
        """Get ingestor metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get ingestor status."""
        return {
            "running": self._running,
            "total_events": len(self._events),
            "active_events": len(self.get_active_events()),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for event notifications."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def _correlate_event(self, event: SensorEvent) -> None:
        """Correlate event with nearby events."""
        window_start = event.timestamp.timestamp() - self.config.correlation_window_seconds
        
        for other_event in self._events.values():
            if other_event.event_id == event.event_id:
                continue
            
            if other_event.timestamp.timestamp() < window_start:
                continue
            
            distance = self._calculate_distance(
                event.latitude, event.longitude,
                other_event.latitude, other_event.longitude,
            ) * 1000
            
            if distance <= self.config.correlation_radius_m:
                if other_event.event_id not in event.correlated_events:
                    event.correlated_events.append(other_event.event_id)
                if event.event_id not in other_event.correlated_events:
                    other_event.correlated_events.append(event.event_id)
                self._metrics.correlated_events += 1
    
    def _update_metrics(self) -> None:
        """Update ingestor metrics."""
        category_counts: dict[str, int] = {}
        severity_counts: dict[str, int] = {}
        active = 0
        
        for event in self._events.values():
            category_counts[event.category.value] = category_counts.get(event.category.value, 0) + 1
            severity_counts[event.severity.value] = severity_counts.get(event.severity.value, 0) + 1
            if not event.resolved:
                active += 1
        
        self._metrics.events_by_category = category_counts
        self._metrics.events_by_severity = severity_counts
        self._metrics.active_events = active
    
    async def _notify_callbacks(self, event: SensorEvent, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(event, event_type)
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
