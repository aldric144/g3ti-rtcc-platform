"""
Phase 38: Event Router
Subscribes to every WebSocket channel in the system.
Normalizes events into a unified schema and routes them to appropriate orchestrator pipelines.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid


class EventCategory(Enum):
    INCIDENT = "incident"
    ALERT = "alert"
    TACTICAL = "tactical"
    OFFICER = "officer"
    DRONE = "drone"
    ROBOT = "robot"
    INVESTIGATION = "investigation"
    THREAT = "threat"
    EMERGENCY = "emergency"
    COMPLIANCE = "compliance"
    SYSTEM = "system"
    SENSOR = "sensor"
    CITY = "city"
    HUMAN_STABILITY = "human_stability"
    PREDICTIVE = "predictive"
    FUSION = "fusion"
    CYBER = "cyber"
    GOVERNANCE = "governance"


class EventPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


@dataclass
class EventSchema:
    schema_id: str = field(default_factory=lambda: f"schema-{uuid.uuid4().hex[:8]}")
    name: str = ""
    version: str = "1.0.0"
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    field_types: Dict[str, str] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)

    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate data against schema."""
        errors = []
        for field_name in self.required_fields:
            if field_name not in data:
                errors.append(f"Missing required field: {field_name}")
        return len(errors) == 0, errors


@dataclass
class NormalizedEvent:
    event_id: str = field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:12]}")
    original_event_id: str = ""
    source_channel: str = ""
    source_subsystem: str = ""
    category: EventCategory = EventCategory.SYSTEM
    priority: EventPriority = EventPriority.MEDIUM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    received_at: datetime = field(default_factory=datetime.utcnow)
    title: str = ""
    summary: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    geolocation: Optional[Dict[str, float]] = None
    entity_ids: List[str] = field(default_factory=list)
    threat_level: Optional[str] = None
    affected_units: List[str] = field(default_factory=list)
    requires_action: bool = False
    action_deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    routed_to: List[str] = field(default_factory=list)
    processed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "original_event_id": self.original_event_id,
            "source_channel": self.source_channel,
            "source_subsystem": self.source_subsystem,
            "category": self.category.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "received_at": self.received_at.isoformat(),
            "title": self.title,
            "summary": self.summary,
            "details": self.details,
            "geolocation": self.geolocation,
            "entity_ids": self.entity_ids,
            "threat_level": self.threat_level,
            "affected_units": self.affected_units,
            "requires_action": self.requires_action,
            "action_deadline": self.action_deadline.isoformat() if self.action_deadline else None,
            "metadata": self.metadata,
            "routed_to": self.routed_to,
            "processed": self.processed,
        }


@dataclass
class RoutingRule:
    rule_id: str = field(default_factory=lambda: f"rule-{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    source_channels: List[str] = field(default_factory=list)
    categories: List[EventCategory] = field(default_factory=list)
    min_priority: EventPriority = EventPriority.INFO
    conditions: Dict[str, Any] = field(default_factory=dict)
    target_pipelines: List[str] = field(default_factory=list)
    transform: Optional[Callable] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def matches(self, event: NormalizedEvent) -> bool:
        """Check if event matches this routing rule."""
        if not self.enabled:
            return False
        if self.source_channels and event.source_channel not in self.source_channels:
            return False
        if self.categories and event.category not in self.categories:
            return False
        if event.priority.value > self.min_priority.value:
            return False
        for key, value in self.conditions.items():
            if key not in event.details or event.details[key] != value:
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "source_channels": self.source_channels,
            "categories": [c.value for c in self.categories],
            "min_priority": self.min_priority.value,
            "conditions": self.conditions,
            "target_pipelines": self.target_pipelines,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
        }


class EventRouter:
    """
    Routes events from all WebSocket channels to appropriate orchestrator pipelines.
    Normalizes events into a unified schema for consistent processing.
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

        self.routing_rules: Dict[str, RoutingRule] = {}
        self.channel_subscriptions: Dict[str, List[str]] = {}
        self.pipeline_handlers: Dict[str, Callable] = {}
        self.event_history: List[NormalizedEvent] = []
        self.schemas: Dict[str, EventSchema] = {}
        self.statistics: Dict[str, Any] = {
            "events_received": 0,
            "events_routed": 0,
            "events_dropped": 0,
            "events_by_category": {},
            "events_by_channel": {},
        }
        self._register_default_channels()
        self._register_default_rules()
        self._register_default_schemas()

    def _register_default_channels(self):
        """Register default WebSocket channels."""
        channels = [
            "events", "alerts", "module_status", "state_sync",
            "notifications", "tactical", "officer_safety",
            "drone_telemetry", "robot_telemetry", "investigations",
            "threats", "emergency", "compliance", "all",
            "incidents", "dispatch", "sensor_data", "city_brain",
            "governance", "human_stability", "moral_compass",
            "predictive", "fusion_cloud", "cyber_intel",
        ]
        for channel in channels:
            self.channel_subscriptions[channel] = []

    def _register_default_rules(self):
        """Register default routing rules."""
        default_rules = [
            RoutingRule(
                name="Critical Alerts",
                description="Route all critical alerts to emergency pipeline",
                categories=[EventCategory.ALERT, EventCategory.EMERGENCY],
                min_priority=EventPriority.CRITICAL,
                target_pipelines=["emergency_response", "command_center"],
            ),
            RoutingRule(
                name="Officer Safety",
                description="Route officer safety events",
                categories=[EventCategory.OFFICER],
                min_priority=EventPriority.HIGH,
                target_pipelines=["officer_safety", "dispatch"],
            ),
            RoutingRule(
                name="Tactical Events",
                description="Route tactical events to analytics",
                categories=[EventCategory.TACTICAL, EventCategory.INCIDENT],
                min_priority=EventPriority.MEDIUM,
                target_pipelines=["tactical_analytics", "predictive_intel"],
            ),
            RoutingRule(
                name="Drone Operations",
                description="Route drone telemetry and events",
                categories=[EventCategory.DRONE],
                min_priority=EventPriority.LOW,
                target_pipelines=["drone_ops", "digital_twin"],
            ),
            RoutingRule(
                name="Robot Operations",
                description="Route robot telemetry and events",
                categories=[EventCategory.ROBOT],
                min_priority=EventPriority.LOW,
                target_pipelines=["robotics", "digital_twin"],
            ),
            RoutingRule(
                name="Investigations",
                description="Route investigation events",
                categories=[EventCategory.INVESTIGATION],
                min_priority=EventPriority.MEDIUM,
                target_pipelines=["investigations", "case_management"],
            ),
            RoutingRule(
                name="Threat Intelligence",
                description="Route threat events",
                categories=[EventCategory.THREAT, EventCategory.CYBER],
                min_priority=EventPriority.HIGH,
                target_pipelines=["threat_intel", "fusion_cloud"],
            ),
            RoutingRule(
                name="Human Stability",
                description="Route human stability events",
                categories=[EventCategory.HUMAN_STABILITY],
                min_priority=EventPriority.MEDIUM,
                target_pipelines=["human_stability", "crisis_response"],
            ),
            RoutingRule(
                name="Compliance Events",
                description="Route compliance and governance events",
                categories=[EventCategory.COMPLIANCE, EventCategory.GOVERNANCE],
                min_priority=EventPriority.LOW,
                target_pipelines=["compliance", "audit"],
            ),
            RoutingRule(
                name="City Operations",
                description="Route city brain and autonomy events",
                categories=[EventCategory.CITY],
                min_priority=EventPriority.MEDIUM,
                target_pipelines=["city_brain", "city_autonomy"],
            ),
        ]
        for rule in default_rules:
            self.routing_rules[rule.rule_id] = rule

    def _register_default_schemas(self):
        """Register default event schemas."""
        self.schemas["standard"] = EventSchema(
            name="Standard Event",
            required_fields=["event_id", "timestamp", "source"],
            optional_fields=["title", "summary", "details", "geolocation"],
            field_types={
                "event_id": "string",
                "timestamp": "datetime",
                "source": "string",
                "title": "string",
                "summary": "string",
                "details": "object",
                "geolocation": "object",
            },
        )

    def normalize_event(
        self,
        raw_event: Dict[str, Any],
        source_channel: str,
        source_subsystem: str = "",
    ) -> NormalizedEvent:
        """Normalize a raw event into the unified schema."""
        category = self._determine_category(raw_event, source_channel)
        priority = self._determine_priority(raw_event)

        normalized = NormalizedEvent(
            original_event_id=raw_event.get("event_id", raw_event.get("id", "")),
            source_channel=source_channel,
            source_subsystem=source_subsystem or raw_event.get("source", "unknown"),
            category=category,
            priority=priority,
            timestamp=self._parse_timestamp(raw_event.get("timestamp")),
            title=raw_event.get("title", raw_event.get("name", "")),
            summary=raw_event.get("summary", raw_event.get("description", "")),
            details=raw_event.get("details", raw_event.get("data", {})),
            geolocation=raw_event.get("geolocation", raw_event.get("location")),
            entity_ids=raw_event.get("entity_ids", []),
            threat_level=raw_event.get("threat_level"),
            affected_units=raw_event.get("affected_units", []),
            requires_action=raw_event.get("requires_action", False),
            metadata=raw_event.get("metadata", {}),
        )

        self.statistics["events_received"] += 1
        self.statistics["events_by_channel"][source_channel] = (
            self.statistics["events_by_channel"].get(source_channel, 0) + 1
        )
        self.statistics["events_by_category"][category.value] = (
            self.statistics["events_by_category"].get(category.value, 0) + 1
        )

        return normalized

    def _determine_category(
        self, event: Dict[str, Any], channel: str
    ) -> EventCategory:
        """Determine event category from raw event and channel."""
        channel_category_map = {
            "alerts": EventCategory.ALERT,
            "incidents": EventCategory.INCIDENT,
            "tactical": EventCategory.TACTICAL,
            "officer_safety": EventCategory.OFFICER,
            "drone_telemetry": EventCategory.DRONE,
            "robot_telemetry": EventCategory.ROBOT,
            "investigations": EventCategory.INVESTIGATION,
            "threats": EventCategory.THREAT,
            "emergency": EventCategory.EMERGENCY,
            "compliance": EventCategory.COMPLIANCE,
            "sensor_data": EventCategory.SENSOR,
            "city_brain": EventCategory.CITY,
            "human_stability": EventCategory.HUMAN_STABILITY,
            "predictive": EventCategory.PREDICTIVE,
            "fusion_cloud": EventCategory.FUSION,
            "cyber_intel": EventCategory.CYBER,
            "governance": EventCategory.GOVERNANCE,
        }
        return channel_category_map.get(channel, EventCategory.SYSTEM)

    def _determine_priority(self, event: Dict[str, Any]) -> EventPriority:
        """Determine event priority from raw event."""
        priority_str = event.get("priority", event.get("severity", "medium"))
        if isinstance(priority_str, int):
            return EventPriority(min(max(priority_str, 1), 5))
        priority_map = {
            "critical": EventPriority.CRITICAL,
            "high": EventPriority.HIGH,
            "medium": EventPriority.MEDIUM,
            "low": EventPriority.LOW,
            "info": EventPriority.INFO,
        }
        return priority_map.get(str(priority_str).lower(), EventPriority.MEDIUM)

    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse timestamp from various formats."""
        if timestamp is None:
            return datetime.utcnow()
        if isinstance(timestamp, datetime):
            return timestamp
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                return datetime.utcnow()
        return datetime.utcnow()

    def route_event(self, event: NormalizedEvent) -> List[str]:
        """Route an event to appropriate pipelines based on routing rules."""
        routed_to = []
        for rule in self.routing_rules.values():
            if rule.matches(event):
                for pipeline in rule.target_pipelines:
                    if pipeline not in routed_to:
                        routed_to.append(pipeline)
                        handler = self.pipeline_handlers.get(pipeline)
                        if handler:
                            try:
                                handler(event)
                            except Exception:
                                pass

        event.routed_to = routed_to
        event.processed = True
        self.event_history.append(event)

        if routed_to:
            self.statistics["events_routed"] += 1
        else:
            self.statistics["events_dropped"] += 1

        return routed_to

    def add_routing_rule(self, rule: RoutingRule) -> bool:
        """Add a new routing rule."""
        self.routing_rules[rule.rule_id] = rule
        return True

    def remove_routing_rule(self, rule_id: str) -> bool:
        """Remove a routing rule."""
        if rule_id in self.routing_rules:
            del self.routing_rules[rule_id]
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a routing rule."""
        if rule_id in self.routing_rules:
            self.routing_rules[rule_id].enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a routing rule."""
        if rule_id in self.routing_rules:
            self.routing_rules[rule_id].enabled = False
            return True
        return False

    def register_pipeline_handler(
        self, pipeline: str, handler: Callable
    ) -> bool:
        """Register a handler for a pipeline."""
        self.pipeline_handlers[pipeline] = handler
        return True

    def subscribe_to_channel(self, channel: str, subscriber_id: str) -> bool:
        """Subscribe to a channel."""
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = []
        if subscriber_id not in self.channel_subscriptions[channel]:
            self.channel_subscriptions[channel].append(subscriber_id)
        return True

    def unsubscribe_from_channel(self, channel: str, subscriber_id: str) -> bool:
        """Unsubscribe from a channel."""
        if channel in self.channel_subscriptions:
            if subscriber_id in self.channel_subscriptions[channel]:
                self.channel_subscriptions[channel].remove(subscriber_id)
                return True
        return False

    def get_routing_rules(self) -> List[Dict[str, Any]]:
        """Get all routing rules."""
        return [rule.to_dict() for rule in self.routing_rules.values()]

    def get_event_history(
        self, limit: int = 100, category: EventCategory = None
    ) -> List[Dict[str, Any]]:
        """Get event history."""
        history = self.event_history[-limit:]
        if category:
            history = [e for e in history if e.category == category]
        return [e.to_dict() for e in history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            **self.statistics,
            "active_rules": len([r for r in self.routing_rules.values() if r.enabled]),
            "total_rules": len(self.routing_rules),
            "registered_pipelines": len(self.pipeline_handlers),
            "subscribed_channels": len(self.channel_subscriptions),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_channels(self) -> List[str]:
        """Get list of available channels."""
        return list(self.channel_subscriptions.keys())

    def get_pipelines(self) -> List[str]:
        """Get list of registered pipelines."""
        return list(self.pipeline_handlers.keys())
