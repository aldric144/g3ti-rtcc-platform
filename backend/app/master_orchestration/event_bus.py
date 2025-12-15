"""
Master Event Bus - Unified orchestration bus for all RTCC modules.
Phase 37: Master UI Integration & System Orchestration Shell
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
import hashlib
import json
import asyncio


class EventType(Enum):
    ALERT = "alert"
    SYSTEM_MESSAGE = "system_message"
    TACTICAL_EVENT = "tactical_event"
    DRONE_TELEMETRY = "drone_telemetry"
    ROBOTICS_TELEMETRY = "robotics_telemetry"
    CAD_UPDATE = "cad_update"
    INVESTIGATION_LEAD = "investigation_lead"
    GLOBAL_THREAT = "global_threat"
    CONSTITUTIONAL_ALERT = "constitutional_alert"
    HUMAN_STABILITY_ALERT = "human_stability_alert"
    TRANSPARENCY_FLAG = "transparency_flag"
    OFFICER_SAFETY = "officer_safety"
    MORAL_COMPASS_ALERT = "moral_compass_alert"
    CITY_BRAIN_UPDATE = "city_brain_update"
    GOVERNANCE_UPDATE = "governance_update"
    FUSION_CLOUD_UPDATE = "fusion_cloud_update"
    AUTONOMOUS_ACTION = "autonomous_action"
    EMERGENCY_MANAGEMENT = "emergency_management"
    CYBER_THREAT = "cyber_threat"
    PREDICTIVE_ALERT = "predictive_alert"
    DIGITAL_TWIN_UPDATE = "digital_twin_update"
    SENSOR_DATA = "sensor_data"
    MODULE_STATUS = "module_status"
    HEARTBEAT = "heartbeat"
    STATE_SYNC = "state_sync"
    USER_ACTION = "user_action"


class EventPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventSource(Enum):
    REAL_TIME_OPS = "real_time_ops"
    INVESTIGATIONS = "investigations"
    TACTICAL_ANALYTICS = "tactical_analytics"
    OFFICER_SAFETY = "officer_safety"
    COMMUNICATIONS = "communications"
    ROBOTICS = "robotics"
    DRONE_OPS = "drone_ops"
    DIGITAL_TWIN = "digital_twin"
    PREDICTIVE_INTEL = "predictive_intel"
    HUMAN_STABILITY = "human_stability"
    MORAL_COMPASS = "moral_compass"
    GLOBAL_AWARENESS = "global_awareness"
    AI_CITY_BRAIN = "ai_city_brain"
    GOVERNANCE_ENGINE = "governance_engine"
    FUSION_CLOUD = "fusion_cloud"
    AUTONOMOUS_OPS = "autonomous_ops"
    CITY_AUTONOMY = "city_autonomy"
    PUBLIC_GUARDIAN = "public_guardian"
    OFFICER_ASSIST = "officer_assist"
    CYBER_INTEL = "cyber_intel"
    EMERGENCY_MGMT = "emergency_mgmt"
    SENTINEL_SUPERVISOR = "sentinel_supervisor"
    AI_PERSONAS = "ai_personas"
    ETHICS_GUARDIAN = "ethics_guardian"
    CONSTITUTION_ENGINE = "constitution_engine"
    DATA_LAKE = "data_lake"
    INTEL_ORCHESTRATION = "intel_orchestration"
    OPS_CONTINUITY = "ops_continuity"
    ENTERPRISE_INFRA = "enterprise_infra"
    THREAT_INTEL = "threat_intel"
    NATIONAL_SECURITY = "national_security"
    DETECTIVE_AI = "detective_ai"
    SYSTEM = "system"
    USER = "user"


@dataclass
class MasterEvent:
    event_id: str = field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:12]}")
    event_type: EventType = EventType.SYSTEM_MESSAGE
    priority: EventPriority = EventPriority.MEDIUM
    source: EventSource = EventSource.SYSTEM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    title: str = ""
    summary: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    geolocation: Optional[Dict[str, float]] = None
    constitutional_compliance: bool = True
    moral_compass_tag: Optional[str] = None
    public_safety_audit_ref: Optional[str] = None
    affected_modules: List[str] = field(default_factory=list)
    requires_acknowledgment: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_hash: str = ""

    def __post_init__(self):
        if not self.event_hash:
            self.event_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.event_type.value}:{self.source.value}:{self.title}:{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "priority": self.priority.value,
            "source": self.source.value,
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "summary": self.summary,
            "details": self.details,
            "geolocation": self.geolocation,
            "constitutional_compliance": self.constitutional_compliance,
            "moral_compass_tag": self.moral_compass_tag,
            "public_safety_audit_ref": self.public_safety_audit_ref,
            "affected_modules": self.affected_modules,
            "requires_acknowledgment": self.requires_acknowledgment,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
            "event_hash": self.event_hash,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class EventSubscription:
    subscription_id: str = field(default_factory=lambda: f"sub-{uuid.uuid4().hex[:12]}")
    subscriber_id: str = ""
    event_types: List[EventType] = field(default_factory=list)
    sources: List[EventSource] = field(default_factory=list)
    min_priority: EventPriority = EventPriority.INFO
    callback: Optional[Callable[[MasterEvent], None]] = None
    async_callback: Optional[Callable[[MasterEvent], Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscription_id": self.subscription_id,
            "subscriber_id": self.subscriber_id,
            "event_types": [et.value for et in self.event_types],
            "sources": [s.value for s in self.sources],
            "min_priority": self.min_priority.value,
            "created_at": self.created_at.isoformat(),
            "active": self.active,
            "metadata": self.metadata,
        }


class MasterEventBus:
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

        self._events: Dict[str, MasterEvent] = {}
        self._subscriptions: Dict[str, EventSubscription] = {}
        self._event_history: List[MasterEvent] = []
        self._max_history = 10000
        self._statistics = {
            "events_published": 0,
            "events_delivered": 0,
            "subscriptions_created": 0,
            "subscriptions_active": 0,
        }
        self._priority_order = {
            EventPriority.CRITICAL: 0,
            EventPriority.HIGH: 1,
            EventPriority.MEDIUM: 2,
            EventPriority.LOW: 3,
            EventPriority.INFO: 4,
        }

    async def publish(self, event: MasterEvent) -> bool:
        self._events[event.event_id] = event
        self._event_history.append(event)
        self._statistics["events_published"] += 1

        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        await self._deliver_event(event)
        return True

    def publish_sync(self, event: MasterEvent) -> bool:
        self._events[event.event_id] = event
        self._event_history.append(event)
        self._statistics["events_published"] += 1

        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        self._deliver_event_sync(event)
        return True

    async def _deliver_event(self, event: MasterEvent):
        for sub in self._subscriptions.values():
            if not sub.active:
                continue

            if not self._matches_subscription(event, sub):
                continue

            try:
                if sub.async_callback:
                    await sub.async_callback(event)
                    self._statistics["events_delivered"] += 1
                elif sub.callback:
                    sub.callback(event)
                    self._statistics["events_delivered"] += 1
            except Exception:
                pass

    def _deliver_event_sync(self, event: MasterEvent):
        for sub in self._subscriptions.values():
            if not sub.active:
                continue

            if not self._matches_subscription(event, sub):
                continue

            try:
                if sub.callback:
                    sub.callback(event)
                    self._statistics["events_delivered"] += 1
            except Exception:
                pass

    def _matches_subscription(self, event: MasterEvent, sub: EventSubscription) -> bool:
        if sub.event_types and event.event_type not in sub.event_types:
            return False

        if sub.sources and event.source not in sub.sources:
            return False

        if self._priority_order[event.priority] > self._priority_order[sub.min_priority]:
            return False

        return True

    def subscribe(
        self,
        subscriber_id: str,
        event_types: Optional[List[EventType]] = None,
        sources: Optional[List[EventSource]] = None,
        min_priority: EventPriority = EventPriority.INFO,
        callback: Optional[Callable[[MasterEvent], None]] = None,
        async_callback: Optional[Callable[[MasterEvent], Any]] = None,
    ) -> EventSubscription:
        subscription = EventSubscription(
            subscriber_id=subscriber_id,
            event_types=event_types or [],
            sources=sources or [],
            min_priority=min_priority,
            callback=callback,
            async_callback=async_callback,
        )
        self._subscriptions[subscription.subscription_id] = subscription
        self._statistics["subscriptions_created"] += 1
        self._statistics["subscriptions_active"] += 1
        return subscription

    def unsubscribe(self, subscription_id: str) -> bool:
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id].active = False
            self._statistics["subscriptions_active"] -= 1
            return True
        return False

    def remove_subscription(self, subscription_id: str) -> bool:
        if subscription_id in self._subscriptions:
            if self._subscriptions[subscription_id].active:
                self._statistics["subscriptions_active"] -= 1
            del self._subscriptions[subscription_id]
            return True
        return False

    def get_event(self, event_id: str) -> Optional[MasterEvent]:
        return self._events.get(event_id)

    def get_recent_events(
        self,
        limit: int = 100,
        event_types: Optional[List[EventType]] = None,
        sources: Optional[List[EventSource]] = None,
        min_priority: Optional[EventPriority] = None,
    ) -> List[MasterEvent]:
        events = list(reversed(self._event_history))

        if event_types:
            events = [e for e in events if e.event_type in event_types]

        if sources:
            events = [e for e in events if e.source in sources]

        if min_priority:
            max_order = self._priority_order[min_priority]
            events = [e for e in events if self._priority_order[e.priority] <= max_order]

        return events[:limit]

    def get_events_by_source(self, source: EventSource, limit: int = 100) -> List[MasterEvent]:
        events = [e for e in reversed(self._event_history) if e.source == source]
        return events[:limit]

    def get_events_by_type(self, event_type: EventType, limit: int = 100) -> List[MasterEvent]:
        events = [e for e in reversed(self._event_history) if e.event_type == event_type]
        return events[:limit]

    def acknowledge_event(self, event_id: str, acknowledged_by: str) -> bool:
        event = self._events.get(event_id)
        if event and event.requires_acknowledgment:
            event.acknowledged_by = acknowledged_by
            event.acknowledged_at = datetime.utcnow()
            return True
        return False

    def get_unacknowledged_events(self) -> List[MasterEvent]:
        return [
            e for e in self._event_history
            if e.requires_acknowledgment and not e.acknowledged_by
        ]

    def get_subscription(self, subscription_id: str) -> Optional[EventSubscription]:
        return self._subscriptions.get(subscription_id)

    def get_subscriptions_by_subscriber(self, subscriber_id: str) -> List[EventSubscription]:
        return [s for s in self._subscriptions.values() if s.subscriber_id == subscriber_id]

    def get_active_subscriptions(self) -> List[EventSubscription]:
        return [s for s in self._subscriptions.values() if s.active]

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self._statistics,
            "total_events_in_history": len(self._event_history),
            "total_subscriptions": len(self._subscriptions),
            "events_by_type": self._count_events_by_type(),
            "events_by_source": self._count_events_by_source(),
            "events_by_priority": self._count_events_by_priority(),
        }

    def _count_events_by_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for event in self._event_history:
            key = event.event_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _count_events_by_source(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for event in self._event_history:
            key = event.source.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _count_events_by_priority(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for event in self._event_history:
            key = event.priority.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def clear_history(self):
        self._event_history = []
        self._events = {}

    def create_event(
        self,
        event_type: EventType,
        source: EventSource,
        title: str,
        summary: str = "",
        priority: EventPriority = EventPriority.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        geolocation: Optional[Dict[str, float]] = None,
        constitutional_compliance: bool = True,
        moral_compass_tag: Optional[str] = None,
        public_safety_audit_ref: Optional[str] = None,
        affected_modules: Optional[List[str]] = None,
        requires_acknowledgment: bool = False,
    ) -> MasterEvent:
        return MasterEvent(
            event_type=event_type,
            source=source,
            title=title,
            summary=summary,
            priority=priority,
            details=details or {},
            geolocation=geolocation,
            constitutional_compliance=constitutional_compliance,
            moral_compass_tag=moral_compass_tag,
            public_safety_audit_ref=public_safety_audit_ref,
            affected_modules=affected_modules or [],
            requires_acknowledgment=requires_acknowledgment,
        )
