"""
Phase 38: Event Fusion Bus (EFB)
Central nervous system for the RTCC platform.
Ingests ALL WebSocket + REST events, fuses them using timestamps, geolocation,
entity IDs, and threat levels, and outputs unified event objects.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
import asyncio
from collections import deque


class FusionStrategy(Enum):
    TIMESTAMP = "timestamp"
    GEOLOCATION = "geolocation"
    ENTITY_ID = "entity_id"
    THREAT_LEVEL = "threat_level"
    COMPOSITE = "composite"


@dataclass
class EventBuffer:
    buffer_id: str = field(default_factory=lambda: f"buf-{uuid.uuid4().hex[:8]}")
    source: str = ""
    events: List[Dict[str, Any]] = field(default_factory=list)
    max_size: int = 1000
    flush_interval_seconds: int = 5
    last_flush: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_event(self, event: Dict[str, Any]) -> bool:
        """Add event to buffer."""
        if len(self.events) >= self.max_size:
            self.events.pop(0)
        self.events.append(event)
        return True

    def flush(self) -> List[Dict[str, Any]]:
        """Flush and return all events."""
        events = self.events.copy()
        self.events.clear()
        self.last_flush = datetime.utcnow()
        return events

    def should_flush(self) -> bool:
        """Check if buffer should be flushed."""
        if len(self.events) >= self.max_size:
            return True
        elapsed = (datetime.utcnow() - self.last_flush).total_seconds()
        return elapsed >= self.flush_interval_seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "buffer_id": self.buffer_id,
            "source": self.source,
            "event_count": len(self.events),
            "max_size": self.max_size,
            "flush_interval_seconds": self.flush_interval_seconds,
            "last_flush": self.last_flush.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class FusedEvent:
    fused_event_id: str = field(default_factory=lambda: f"fused-{uuid.uuid4().hex[:12]}")
    source_events: List[str] = field(default_factory=list)
    source_count: int = 0
    fusion_strategy: FusionStrategy = FusionStrategy.COMPOSITE
    timestamp: datetime = field(default_factory=datetime.utcnow)
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    primary_source: str = ""
    all_sources: List[str] = field(default_factory=list)
    event_type: str = ""
    category: str = ""
    priority: int = 5
    threat_level: Optional[str] = None
    geolocation: Optional[Dict[str, float]] = None
    entity_ids: List[str] = field(default_factory=list)
    title: str = ""
    summary: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    correlated_data: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 100.0
    requires_action: bool = False
    recommended_actions: List[str] = field(default_factory=list)
    explainability_log: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fused_event_id": self.fused_event_id,
            "source_events": self.source_events,
            "source_count": self.source_count,
            "fusion_strategy": self.fusion_strategy.value,
            "timestamp": self.timestamp.isoformat(),
            "time_window_start": self.time_window_start.isoformat() if self.time_window_start else None,
            "time_window_end": self.time_window_end.isoformat() if self.time_window_end else None,
            "primary_source": self.primary_source,
            "all_sources": self.all_sources,
            "event_type": self.event_type,
            "category": self.category,
            "priority": self.priority,
            "threat_level": self.threat_level,
            "geolocation": self.geolocation,
            "entity_ids": self.entity_ids,
            "title": self.title,
            "summary": self.summary,
            "details": self.details,
            "correlated_data": self.correlated_data,
            "confidence_score": self.confidence_score,
            "requires_action": self.requires_action,
            "recommended_actions": self.recommended_actions,
            "explainability_log": self.explainability_log,
            "metadata": self.metadata,
        }


@dataclass
class FusionResult:
    result_id: str = field(default_factory=lambda: f"fusion-{uuid.uuid4().hex[:8]}")
    fused_events: List[FusedEvent] = field(default_factory=list)
    unfused_events: List[Dict[str, Any]] = field(default_factory=list)
    total_input_events: int = 0
    fusion_rate: float = 0.0
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "fused_events": [e.to_dict() for e in self.fused_events],
            "unfused_count": len(self.unfused_events),
            "total_input_events": self.total_input_events,
            "fusion_rate": self.fusion_rate,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


class EventFusionBus:
    """
    Central nervous system for the RTCC platform.
    Ingests, buffers, debounces, rate-limits, and fuses events from all sources.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.buffers: Dict[str, EventBuffer] = {}
        self.fused_events: List[FusedEvent] = []
        self.event_history: deque = deque(maxlen=10000)
        self.subscribers: Dict[str, List[Callable]] = {}
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.debounce_windows: Dict[str, datetime] = {}
        self.fusion_rules: List[Dict[str, Any]] = []
        self.statistics: Dict[str, Any] = {
            "total_events_received": 0,
            "total_events_fused": 0,
            "total_events_dropped": 0,
            "events_by_source": {},
            "fusion_operations": 0,
            "average_fusion_time_ms": 0.0,
        }
        self._register_default_sources()
        self._register_default_fusion_rules()

    def _register_default_sources(self):
        """Register default event sources with buffers."""
        sources = [
            "cad_system", "dispatch", "drone_ops", "robotics",
            "officer_safety", "tactical_analytics", "threat_intel",
            "investigations", "digital_twin", "predictive_intel",
            "human_stability", "moral_compass", "city_autonomy",
            "fusion_cloud", "emergency_mgmt", "public_guardian",
            "cyber_intel", "ai_sentinel", "ai_personas",
            "sensor_grid", "lpr_network", "gunshot_detection",
            "cctv_network", "weather_service", "traffic_system",
        ]
        for source in sources:
            self.buffers[source] = EventBuffer(source=source)
            self.rate_limits[source] = {
                "max_events_per_second": 100,
                "current_count": 0,
                "window_start": datetime.utcnow(),
            }

    def _register_default_fusion_rules(self):
        """Register default event fusion rules."""
        self.fusion_rules = [
            {
                "name": "gunshot_correlation",
                "description": "Correlate gunshot detections with nearby incidents",
                "event_types": ["gunshot_detected", "shots_fired"],
                "time_window_seconds": 30,
                "geo_radius_meters": 500,
                "min_events": 2,
            },
            {
                "name": "officer_distress_correlation",
                "description": "Correlate officer distress signals with location data",
                "event_types": ["officer_distress", "panic_button", "man_down"],
                "time_window_seconds": 60,
                "geo_radius_meters": 100,
                "min_events": 1,
            },
            {
                "name": "vehicle_pursuit_correlation",
                "description": "Correlate LPR hits with pursuit events",
                "event_types": ["lpr_hit", "vehicle_pursuit", "bolo_match"],
                "time_window_seconds": 120,
                "entity_match": True,
                "min_events": 2,
            },
            {
                "name": "threat_escalation",
                "description": "Correlate escalating threat indicators",
                "event_types": ["threat_detected", "threat_escalation", "active_threat"],
                "time_window_seconds": 300,
                "geo_radius_meters": 1000,
                "min_events": 2,
            },
            {
                "name": "multi_sensor_incident",
                "description": "Correlate multiple sensor detections",
                "event_types": ["sensor_alert", "camera_alert", "audio_alert"],
                "time_window_seconds": 60,
                "geo_radius_meters": 200,
                "min_events": 3,
            },
        ]

    def ingest_event(
        self, source: str, event: Dict[str, Any]
    ) -> bool:
        """Ingest an event from a source."""
        if not self._check_rate_limit(source):
            self.statistics["total_events_dropped"] += 1
            return False

        if self._is_debounced(source, event):
            return False

        if source not in self.buffers:
            self.buffers[source] = EventBuffer(source=source)

        event["_ingested_at"] = datetime.utcnow().isoformat()
        event["_source"] = source
        self.buffers[source].add_event(event)
        self.event_history.append(event)

        self.statistics["total_events_received"] += 1
        self.statistics["events_by_source"][source] = (
            self.statistics["events_by_source"].get(source, 0) + 1
        )

        return True

    def _check_rate_limit(self, source: str) -> bool:
        """Check if source is within rate limit."""
        if source not in self.rate_limits:
            return True

        limit = self.rate_limits[source]
        now = datetime.utcnow()

        if (now - limit["window_start"]).total_seconds() >= 1.0:
            limit["current_count"] = 0
            limit["window_start"] = now

        if limit["current_count"] >= limit["max_events_per_second"]:
            return False

        limit["current_count"] += 1
        return True

    def _is_debounced(self, source: str, event: Dict[str, Any]) -> bool:
        """Check if event should be debounced."""
        event_key = f"{source}:{event.get('event_type', '')}:{event.get('entity_id', '')}"
        now = datetime.utcnow()

        if event_key in self.debounce_windows:
            last_time = self.debounce_windows[event_key]
            if (now - last_time).total_seconds() < 1.0:
                return True

        self.debounce_windows[event_key] = now
        return False

    async def fuse_events(
        self, events: List[Dict[str, Any]] = None
    ) -> FusionResult:
        """Fuse events from all buffers or provided list."""
        start_time = datetime.utcnow()

        if events is None:
            events = []
            for buffer in self.buffers.values():
                if buffer.should_flush():
                    events.extend(buffer.flush())

        if not events:
            return FusionResult(total_input_events=0)

        fused = []
        unfused = []

        for rule in self.fusion_rules:
            matching_events = [
                e for e in events
                if e.get("event_type") in rule.get("event_types", [])
            ]

            if len(matching_events) >= rule.get("min_events", 1):
                fused_event = self._create_fused_event(matching_events, rule)
                fused.append(fused_event)
                self.fused_events.append(fused_event)

                for e in matching_events:
                    if e in events:
                        events.remove(e)

        unfused = events

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        self.statistics["fusion_operations"] += 1
        self.statistics["total_events_fused"] += len(fused)

        result = FusionResult(
            fused_events=fused,
            unfused_events=unfused,
            total_input_events=len(fused) + len(unfused),
            fusion_rate=(len(fused) / (len(fused) + len(unfused))) * 100 if fused or unfused else 0,
            processing_time_ms=processing_time,
        )

        await self._notify_subscribers(result)

        return result

    def _create_fused_event(
        self, events: List[Dict[str, Any]], rule: Dict[str, Any]
    ) -> FusedEvent:
        """Create a fused event from multiple source events."""
        source_ids = [e.get("event_id", str(uuid.uuid4())) for e in events]
        sources = list(set(e.get("_source", "unknown") for e in events))
        timestamps = [
            datetime.fromisoformat(e["_ingested_at"].replace("Z", "+00:00"))
            if isinstance(e.get("_ingested_at"), str)
            else datetime.utcnow()
            for e in events
        ]

        priorities = [e.get("priority", 5) for e in events]
        min_priority = min(priorities)

        geolocations = [e.get("geolocation") for e in events if e.get("geolocation")]
        avg_geolocation = None
        if geolocations:
            avg_lat = sum(g.get("lat", 0) for g in geolocations) / len(geolocations)
            avg_lng = sum(g.get("lng", 0) for g in geolocations) / len(geolocations)
            avg_geolocation = {"lat": avg_lat, "lng": avg_lng}

        entity_ids = list(set(
            eid for e in events
            for eid in (e.get("entity_ids", []) if isinstance(e.get("entity_ids"), list) else [e.get("entity_id")] if e.get("entity_id") else [])
        ))

        threat_levels = [e.get("threat_level") for e in events if e.get("threat_level")]
        highest_threat = max(threat_levels, default=None, key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x, 0))

        fused = FusedEvent(
            source_events=source_ids,
            source_count=len(events),
            fusion_strategy=FusionStrategy.COMPOSITE,
            time_window_start=min(timestamps),
            time_window_end=max(timestamps),
            primary_source=sources[0] if sources else "unknown",
            all_sources=sources,
            event_type=rule.get("name", "fused_event"),
            category=events[0].get("category", "general"),
            priority=min_priority,
            threat_level=highest_threat,
            geolocation=avg_geolocation,
            entity_ids=entity_ids,
            title=f"Fused: {rule.get('name', 'Event Correlation')}",
            summary=f"Correlated {len(events)} events from {len(sources)} sources",
            details={
                "rule_name": rule.get("name"),
                "rule_description": rule.get("description"),
                "source_event_types": list(set(e.get("event_type") for e in events)),
            },
            correlated_data={
                "events": [
                    {
                        "id": e.get("event_id"),
                        "type": e.get("event_type"),
                        "source": e.get("_source"),
                    }
                    for e in events
                ],
            },
            confidence_score=min(100.0, 50.0 + (len(events) * 10)),
            requires_action=min_priority <= 2,
            recommended_actions=self._generate_recommendations(events, rule),
            explainability_log=[
                f"Fusion rule '{rule.get('name')}' matched {len(events)} events",
                f"Time window: {rule.get('time_window_seconds', 60)} seconds",
                f"Sources involved: {', '.join(sources)}",
            ],
        )

        return fused

    def _generate_recommendations(
        self, events: List[Dict[str, Any]], rule: Dict[str, Any]
    ) -> List[str]:
        """Generate action recommendations based on fused events."""
        recommendations = []
        rule_name = rule.get("name", "")

        if "gunshot" in rule_name:
            recommendations.extend([
                "Dispatch nearest units to location",
                "Deploy surveillance drone",
                "Alert tactical team",
            ])
        elif "officer_distress" in rule_name:
            recommendations.extend([
                "Immediate backup dispatch",
                "Notify supervisor",
                "Track officer location",
            ])
        elif "vehicle_pursuit" in rule_name:
            recommendations.extend([
                "Coordinate pursuit units",
                "Deploy spike strips if authorized",
                "Notify air support",
            ])
        elif "threat" in rule_name:
            recommendations.extend([
                "Elevate threat level",
                "Notify command center",
                "Prepare tactical response",
            ])
        else:
            recommendations.append("Review correlated events for action")

        return recommendations

    async def _notify_subscribers(self, result: FusionResult):
        """Notify subscribers of fusion results."""
        for subscriber_list in self.subscribers.values():
            for callback in subscriber_list:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(result)
                    else:
                        callback(result)
                except Exception:
                    pass

    def subscribe(self, subscriber_id: str, callback: Callable) -> bool:
        """Subscribe to fusion results."""
        if subscriber_id not in self.subscribers:
            self.subscribers[subscriber_id] = []
        self.subscribers[subscriber_id].append(callback)
        return True

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from fusion results."""
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
            return True
        return False

    def add_fusion_rule(self, rule: Dict[str, Any]) -> bool:
        """Add a new fusion rule."""
        self.fusion_rules.append(rule)
        return True

    def remove_fusion_rule(self, rule_name: str) -> bool:
        """Remove a fusion rule by name."""
        self.fusion_rules = [r for r in self.fusion_rules if r.get("name") != rule_name]
        return True

    def set_rate_limit(
        self, source: str, max_events_per_second: int
    ) -> bool:
        """Set rate limit for a source."""
        self.rate_limits[source] = {
            "max_events_per_second": max_events_per_second,
            "current_count": 0,
            "window_start": datetime.utcnow(),
        }
        return True

    def get_buffer_status(self) -> Dict[str, Any]:
        """Get status of all buffers."""
        return {
            source: buffer.to_dict()
            for source, buffer in self.buffers.items()
        }

    def get_fused_events(
        self, limit: int = 100, event_type: str = None
    ) -> List[Dict[str, Any]]:
        """Get fused events."""
        events = self.fused_events[-limit:]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return [e.to_dict() for e in events]

    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get raw event history."""
        return list(self.event_history)[-limit:]

    def get_fusion_rules(self) -> List[Dict[str, Any]]:
        """Get all fusion rules."""
        return self.fusion_rules

    def get_statistics(self) -> Dict[str, Any]:
        """Get event fusion bus statistics."""
        return {
            **self.statistics,
            "active_buffers": len(self.buffers),
            "total_fused_events": len(self.fused_events),
            "active_subscribers": len(self.subscribers),
            "fusion_rules_count": len(self.fusion_rules),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def flush_all_buffers(self) -> List[Dict[str, Any]]:
        """Flush all buffers and return events."""
        all_events = []
        for buffer in self.buffers.values():
            all_events.extend(buffer.flush())
        return all_events

    def clear_history(self) -> int:
        """Clear event history."""
        count = len(self.event_history)
        self.event_history.clear()
        self.fused_events.clear()
        return count
