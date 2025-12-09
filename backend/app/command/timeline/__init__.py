"""
Operational Timeline Engine for G3TI RTCC-UIP.

Provides auto-logging of events from CAD, LPR, gunfire detection,
unit movements, ICS changes, and manual command log entries.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class TimelineEventType(str, Enum):
    """Types of timeline events."""

    # CAD Events
    CAD_CALL_RECEIVED = "cad_call_received"
    CAD_CALL_DISPATCHED = "cad_call_dispatched"
    CAD_CALL_UPDATED = "cad_call_updated"
    CAD_CALL_CLOSED = "cad_call_closed"
    CAD_PRIORITY_CHANGE = "cad_priority_change"

    # Unit Events
    UNIT_ASSIGNED = "unit_assigned"
    UNIT_EN_ROUTE = "unit_en_route"
    UNIT_ARRIVED = "unit_arrived"
    UNIT_DEPARTED = "unit_departed"
    UNIT_STATUS_CHANGE = "unit_status_change"

    # Detection Events
    GUNFIRE_DETECTED = "gunfire_detected"
    LPR_HIT = "lpr_hit"
    BOLO_MATCH = "bolo_match"

    # ICS Events
    ICS_ROLE_ASSIGNED = "ics_role_assigned"
    ICS_ROLE_CHANGED = "ics_role_changed"
    COMMANDER_CHANGE = "commander_change"

    # Resource Events
    RESOURCE_ASSIGNED = "resource_assigned"
    RESOURCE_ARRIVED = "resource_arrived"
    RESOURCE_RELEASED = "resource_released"
    RESOURCE_REQUESTED = "resource_requested"

    # Safety Events
    OFFICER_SAFETY_ALERT = "officer_safety_alert"
    THREAT_DETECTED = "threat_detected"
    PERIMETER_BREACH = "perimeter_breach"

    # Scene Events
    SCENE_CREATED = "scene_created"
    SCENE_STATUS_CHANGE = "scene_status_change"
    TACTICAL_ROLE_CHANGE = "tactical_role_change"

    # Command Events
    INCIDENT_CREATED = "incident_created"
    INCIDENT_ACTIVATED = "incident_activated"
    INCIDENT_STATUS_CHANGE = "incident_status_change"
    INCIDENT_CLOSED = "incident_closed"

    # Communication Events
    ALERT_SENT = "alert_sent"
    BULLETIN_PUBLISHED = "bulletin_published"
    MESSAGE_SENT = "message_sent"

    # Manual Events
    COMMAND_NOTE = "command_note"
    TACTICAL_UPDATE = "tactical_update"
    INTELLIGENCE_UPDATE = "intelligence_update"
    SITUATION_REPORT = "situation_report"

    # Map Events
    PERIMETER_ESTABLISHED = "perimeter_established"
    PERIMETER_UPDATED = "perimeter_updated"
    HOT_ZONE_MARKED = "hot_zone_marked"
    EVACUATION_ORDERED = "evacuation_ordered"

    # Other
    CUSTOM = "custom"
    SYSTEM = "system"


class EventPriority(str, Enum):
    """Priority level of timeline events."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventSource(str, Enum):
    """Source of timeline events."""

    CAD = "cad"
    LPR = "lpr"
    SHOTSPOTTER = "shotspotter"
    OFFICER_SAFETY = "officer_safety"
    TACTICAL = "tactical"
    ICS = "ics"
    RESOURCES = "resources"
    COMMUNICATIONS = "communications"
    RTCC = "rtcc"
    COMMAND = "command"
    SYSTEM = "system"
    MANUAL = "manual"


class GeoLocation(BaseModel):
    """Geographic location."""

    latitude: float
    longitude: float
    address: str | None = None


class TimelineEvent(BaseModel):
    """Event in the operational timeline."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    event_type: TimelineEventType
    source: EventSource
    priority: EventPriority = EventPriority.MEDIUM
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    title: str
    description: str | None = None
    location: GeoLocation | None = None
    related_entity_id: str | None = None
    related_entity_type: str | None = None
    user_id: str | None = None
    user_name: str | None = None
    badge: str | None = None
    unit_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_pinned: bool = False
    is_redacted: bool = False
    attachments: list[str] = Field(default_factory=list)
    audit_id: str = Field(default_factory=lambda: f"AUDIT-TL-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class TimelineFilter(BaseModel):
    """Filter for timeline queries."""

    event_types: list[TimelineEventType] | None = None
    sources: list[EventSource] | None = None
    priorities: list[EventPriority] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    user_id: str | None = None
    unit_id: str | None = None
    pinned_only: bool = False
    search_text: str | None = None


class TimelineEngine:
    """
    Engine for operational timeline management.

    Provides auto-logging of events from various sources,
    manual command log entries, and timeline queries.
    """

    def __init__(self) -> None:
        """Initialize the timeline engine."""
        self._events: dict[str, list[TimelineEvent]] = {}  # incident_id -> events
        self._event_handlers: dict[TimelineEventType, list] = {}

        logger.info("timeline_engine_initialized")

    async def add_event(
        self,
        incident_id: str,
        event_type: TimelineEventType,
        source: EventSource,
        title: str,
        description: str | None = None,
        priority: EventPriority = EventPriority.MEDIUM,
        timestamp: datetime | None = None,
        location: GeoLocation | None = None,
        related_entity_id: str | None = None,
        related_entity_type: str | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
        badge: str | None = None,
        unit_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        attachments: list[str] | None = None,
    ) -> TimelineEvent:
        """
        Add an event to the timeline.

        Args:
            incident_id: ID of the incident
            event_type: Type of event
            source: Source of event
            title: Event title
            description: Event description
            priority: Event priority
            timestamp: Event timestamp (defaults to now)
            location: Event location
            related_entity_id: ID of related entity
            related_entity_type: Type of related entity
            user_id: User who triggered event
            user_name: Name of user
            badge: Badge number
            unit_id: Unit identifier
            metadata: Additional metadata
            attachments: List of attachment URLs

        Returns:
            Created TimelineEvent
        """
        event = TimelineEvent(
            incident_id=incident_id,
            event_type=event_type,
            source=source,
            priority=priority,
            timestamp=timestamp or datetime.now(UTC),
            title=title,
            description=description,
            location=location,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type,
            user_id=user_id,
            user_name=user_name,
            badge=badge,
            unit_id=unit_id,
            metadata=metadata or {},
            attachments=attachments or [],
        )

        if incident_id not in self._events:
            self._events[incident_id] = []
        self._events[incident_id].append(event)

        # Trigger event handlers
        await self._trigger_handlers(event)

        logger.info(
            "timeline_event_added",
            incident_id=incident_id,
            event_type=event_type,
            title=title,
            priority=priority,
            audit_id=event.audit_id,
        )

        return event

    async def add_command_note(
        self,
        incident_id: str,
        note: str,
        user_id: str | None = None,
        user_name: str | None = None,
        priority: EventPriority = EventPriority.MEDIUM,
        attachments: list[str] | None = None,
    ) -> TimelineEvent:
        """
        Add a manual command note to the timeline.

        Args:
            incident_id: ID of the incident
            note: Note content
            user_id: User adding note
            user_name: Name of user
            priority: Note priority
            attachments: List of attachment URLs

        Returns:
            Created TimelineEvent
        """
        return await self.add_event(
            incident_id=incident_id,
            event_type=TimelineEventType.COMMAND_NOTE,
            source=EventSource.COMMAND,
            title="Command Note",
            description=note,
            priority=priority,
            user_id=user_id,
            user_name=user_name,
            attachments=attachments,
        )

    async def add_tactical_update(
        self,
        incident_id: str,
        update: str,
        location: GeoLocation | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
        priority: EventPriority = EventPriority.HIGH,
    ) -> TimelineEvent:
        """
        Add a tactical update to the timeline.

        Args:
            incident_id: ID of the incident
            update: Update content
            location: Location of update
            user_id: User adding update
            user_name: Name of user
            priority: Update priority

        Returns:
            Created TimelineEvent
        """
        return await self.add_event(
            incident_id=incident_id,
            event_type=TimelineEventType.TACTICAL_UPDATE,
            source=EventSource.TACTICAL,
            title="Tactical Update",
            description=update,
            priority=priority,
            location=location,
            user_id=user_id,
            user_name=user_name,
        )

    async def add_situation_report(
        self,
        incident_id: str,
        report: str,
        user_id: str | None = None,
        user_name: str | None = None,
    ) -> TimelineEvent:
        """
        Add a situation report to the timeline.

        Args:
            incident_id: ID of the incident
            report: Report content
            user_id: User adding report
            user_name: Name of user

        Returns:
            Created TimelineEvent
        """
        return await self.add_event(
            incident_id=incident_id,
            event_type=TimelineEventType.SITUATION_REPORT,
            source=EventSource.COMMAND,
            title="Situation Report",
            description=report,
            priority=EventPriority.HIGH,
            user_id=user_id,
            user_name=user_name,
        )

    async def log_cad_event(
        self,
        incident_id: str,
        cad_id: str,
        event_type: TimelineEventType,
        title: str,
        description: str | None = None,
        location: GeoLocation | None = None,
        priority: EventPriority = EventPriority.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineEvent:
        """
        Log a CAD event to the timeline.

        Args:
            incident_id: ID of the incident
            cad_id: CAD call ID
            event_type: Type of CAD event
            title: Event title
            description: Event description
            location: Event location
            priority: Event priority
            metadata: Additional metadata

        Returns:
            Created TimelineEvent
        """
        return await self.add_event(
            incident_id=incident_id,
            event_type=event_type,
            source=EventSource.CAD,
            title=title,
            description=description,
            priority=priority,
            location=location,
            related_entity_id=cad_id,
            related_entity_type="cad_call",
            metadata=metadata,
        )

    async def log_unit_event(
        self,
        incident_id: str,
        unit_id: str,
        event_type: TimelineEventType,
        title: str,
        description: str | None = None,
        badge: str | None = None,
        location: GeoLocation | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineEvent:
        """
        Log a unit event to the timeline.

        Args:
            incident_id: ID of the incident
            unit_id: Unit identifier
            event_type: Type of unit event
            title: Event title
            description: Event description
            badge: Officer badge
            location: Event location
            metadata: Additional metadata

        Returns:
            Created TimelineEvent
        """
        return await self.add_event(
            incident_id=incident_id,
            event_type=event_type,
            source=EventSource.CAD,
            title=title,
            description=description,
            priority=EventPriority.MEDIUM,
            location=location,
            unit_id=unit_id,
            badge=badge,
            related_entity_id=unit_id,
            related_entity_type="unit",
            metadata=metadata,
        )

    async def log_gunfire_detection(
        self,
        incident_id: str,
        detection_id: str,
        location: GeoLocation,
        rounds_detected: int | None = None,
        confidence: float | None = None,
    ) -> TimelineEvent:
        """
        Log a gunfire detection to the timeline.

        Args:
            incident_id: ID of the incident
            detection_id: Detection ID
            location: Detection location
            rounds_detected: Number of rounds
            confidence: Detection confidence

        Returns:
            Created TimelineEvent
        """
        description = "Gunfire detected"
        if rounds_detected:
            description += f" - {rounds_detected} rounds"
        if confidence:
            description += f" (confidence: {confidence:.0%})"

        return await self.add_event(
            incident_id=incident_id,
            event_type=TimelineEventType.GUNFIRE_DETECTED,
            source=EventSource.SHOTSPOTTER,
            title="Gunfire Detected",
            description=description,
            priority=EventPriority.CRITICAL,
            location=location,
            related_entity_id=detection_id,
            related_entity_type="gunfire_detection",
            metadata={
                "rounds_detected": rounds_detected,
                "confidence": confidence,
            },
        )

    async def log_lpr_hit(
        self,
        incident_id: str,
        plate: str,
        camera_id: str,
        location: GeoLocation,
        alert_type: str | None = None,
        vehicle_description: str | None = None,
    ) -> TimelineEvent:
        """
        Log an LPR hit to the timeline.

        Args:
            incident_id: ID of the incident
            plate: License plate
            camera_id: Camera ID
            location: Detection location
            alert_type: Type of alert (BOLO, stolen, etc.)
            vehicle_description: Vehicle description

        Returns:
            Created TimelineEvent
        """
        title = f"LPR Hit: {plate}"
        description = f"Plate {plate} detected"
        if alert_type:
            description += f" - {alert_type}"
        if vehicle_description:
            description += f" ({vehicle_description})"

        return await self.add_event(
            incident_id=incident_id,
            event_type=TimelineEventType.LPR_HIT,
            source=EventSource.LPR,
            title=title,
            description=description,
            priority=EventPriority.HIGH,
            location=location,
            related_entity_id=plate,
            related_entity_type="license_plate",
            metadata={
                "plate": plate,
                "camera_id": camera_id,
                "alert_type": alert_type,
                "vehicle_description": vehicle_description,
            },
        )

    async def log_ics_change(
        self,
        incident_id: str,
        event_type: TimelineEventType,
        role: str,
        badge: str,
        name: str | None = None,
        previous_badge: str | None = None,
        assigned_by: str | None = None,
    ) -> TimelineEvent:
        """
        Log an ICS change to the timeline.

        Args:
            incident_id: ID of the incident
            event_type: Type of ICS event
            role: ICS role
            badge: Badge of person assigned
            name: Name of person
            previous_badge: Previous person's badge
            assigned_by: User making assignment

        Returns:
            Created TimelineEvent
        """
        title = f"ICS: {role.replace('_', ' ').title()}"
        description = f"{name or badge} assigned to {role.replace('_', ' ').title()}"
        if previous_badge:
            description += f" (relieving {previous_badge})"

        return await self.add_event(
            incident_id=incident_id,
            event_type=event_type,
            source=EventSource.ICS,
            title=title,
            description=description,
            priority=EventPriority.HIGH,
            badge=badge,
            user_id=assigned_by,
            metadata={
                "role": role,
                "badge": badge,
                "name": name,
                "previous_badge": previous_badge,
            },
        )

    async def log_officer_safety_alert(
        self,
        incident_id: str,
        alert_type: str,
        badge: str,
        location: GeoLocation | None = None,
        threat_level: str | None = None,
        description: str | None = None,
    ) -> TimelineEvent:
        """
        Log an officer safety alert to the timeline.

        Args:
            incident_id: ID of the incident
            alert_type: Type of safety alert
            badge: Officer badge
            location: Alert location
            threat_level: Threat level
            description: Alert description

        Returns:
            Created TimelineEvent
        """
        title = f"Officer Safety: {alert_type.replace('_', ' ').title()}"

        return await self.add_event(
            incident_id=incident_id,
            event_type=TimelineEventType.OFFICER_SAFETY_ALERT,
            source=EventSource.OFFICER_SAFETY,
            title=title,
            description=description or f"Safety alert for officer {badge}",
            priority=EventPriority.CRITICAL,
            location=location,
            badge=badge,
            metadata={
                "alert_type": alert_type,
                "threat_level": threat_level,
            },
        )

    async def log_resource_event(
        self,
        incident_id: str,
        event_type: TimelineEventType,
        resource_id: str,
        resource_name: str,
        resource_type: str,
        user_id: str | None = None,
        location: GeoLocation | None = None,
    ) -> TimelineEvent:
        """
        Log a resource event to the timeline.

        Args:
            incident_id: ID of the incident
            event_type: Type of resource event
            resource_id: Resource ID
            resource_name: Resource name
            resource_type: Type of resource
            user_id: User triggering event
            location: Event location

        Returns:
            Created TimelineEvent
        """
        action = event_type.value.replace("resource_", "").replace("_", " ")
        title = f"Resource {action.title()}: {resource_name}"

        return await self.add_event(
            incident_id=incident_id,
            event_type=event_type,
            source=EventSource.RESOURCES,
            title=title,
            description=f"{resource_type.replace('_', ' ').title()} {resource_name} {action}",
            priority=EventPriority.MEDIUM,
            location=location,
            user_id=user_id,
            related_entity_id=resource_id,
            related_entity_type="resource",
            metadata={
                "resource_type": resource_type,
            },
        )

    async def pin_event(
        self,
        incident_id: str,
        event_id: str,
        pinned_by: str | None = None,
    ) -> TimelineEvent | None:
        """
        Pin an event to highlight it.

        Args:
            incident_id: ID of the incident
            event_id: ID of event to pin
            pinned_by: User pinning event

        Returns:
            Updated TimelineEvent or None
        """
        events = self._events.get(incident_id, [])
        event = next((e for e in events if e.id == event_id), None)

        if not event:
            return None

        event.is_pinned = True

        logger.info(
            "timeline_event_pinned",
            incident_id=incident_id,
            event_id=event_id,
            pinned_by=pinned_by,
        )

        return event

    async def unpin_event(
        self,
        incident_id: str,
        event_id: str,
    ) -> TimelineEvent | None:
        """
        Unpin an event.

        Args:
            incident_id: ID of the incident
            event_id: ID of event to unpin

        Returns:
            Updated TimelineEvent or None
        """
        events = self._events.get(incident_id, [])
        event = next((e for e in events if e.id == event_id), None)

        if not event:
            return None

        event.is_pinned = False
        return event

    async def redact_event(
        self,
        incident_id: str,
        event_id: str,
        redacted_by: str | None = None,
        reason: str | None = None,
    ) -> TimelineEvent | None:
        """
        Redact an event (hide sensitive content).

        Args:
            incident_id: ID of the incident
            event_id: ID of event to redact
            redacted_by: User redacting event
            reason: Reason for redaction

        Returns:
            Updated TimelineEvent or None
        """
        events = self._events.get(incident_id, [])
        event = next((e for e in events if e.id == event_id), None)

        if not event:
            return None

        event.is_redacted = True
        event.metadata["redacted_by"] = redacted_by
        event.metadata["redaction_reason"] = reason
        event.metadata["redacted_at"] = datetime.now(UTC).isoformat()

        logger.info(
            "timeline_event_redacted",
            incident_id=incident_id,
            event_id=event_id,
            redacted_by=redacted_by,
            reason=reason,
        )

        return event

    async def get_timeline(
        self,
        incident_id: str,
        filter_params: TimelineFilter | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TimelineEvent]:
        """
        Get timeline events for an incident.

        Args:
            incident_id: ID of the incident
            filter_params: Optional filter parameters
            limit: Maximum number to return
            offset: Number to skip

        Returns:
            List of TimelineEvent
        """
        events = self._events.get(incident_id, [])

        if filter_params:
            if filter_params.event_types:
                type_values = [
                    t.value if isinstance(t, TimelineEventType) else t
                    for t in filter_params.event_types
                ]
                events = [e for e in events if e.event_type in type_values]

            if filter_params.sources:
                source_values = [
                    s.value if isinstance(s, EventSource) else s
                    for s in filter_params.sources
                ]
                events = [e for e in events if e.source in source_values]

            if filter_params.priorities:
                priority_values = [
                    p.value if isinstance(p, EventPriority) else p
                    for p in filter_params.priorities
                ]
                events = [e for e in events if e.priority in priority_values]

            if filter_params.start_time:
                events = [e for e in events if e.timestamp >= filter_params.start_time]

            if filter_params.end_time:
                events = [e for e in events if e.timestamp <= filter_params.end_time]

            if filter_params.user_id:
                events = [e for e in events if e.user_id == filter_params.user_id]

            if filter_params.unit_id:
                events = [e for e in events if e.unit_id == filter_params.unit_id]

            if filter_params.pinned_only:
                events = [e for e in events if e.is_pinned]

            if filter_params.search_text:
                search = filter_params.search_text.lower()
                events = [
                    e for e in events
                    if search in e.title.lower() or
                    (e.description and search in e.description.lower())
                ]

        # Sort by timestamp descending (most recent first)
        events.sort(key=lambda x: x.timestamp, reverse=True)

        return events[offset:offset + limit]

    async def get_pinned_events(
        self,
        incident_id: str,
    ) -> list[TimelineEvent]:
        """
        Get pinned events for an incident.

        Args:
            incident_id: ID of the incident

        Returns:
            List of pinned TimelineEvent
        """
        events = self._events.get(incident_id, [])
        pinned = [e for e in events if e.is_pinned]
        pinned.sort(key=lambda x: x.timestamp, reverse=True)
        return pinned

    async def get_critical_events(
        self,
        incident_id: str,
        limit: int = 20,
    ) -> list[TimelineEvent]:
        """
        Get critical priority events.

        Args:
            incident_id: ID of the incident
            limit: Maximum number to return

        Returns:
            List of critical TimelineEvent
        """
        events = self._events.get(incident_id, [])
        critical = [e for e in events if e.priority == EventPriority.CRITICAL.value]
        critical.sort(key=lambda x: x.timestamp, reverse=True)
        return critical[:limit]

    async def get_events_by_type(
        self,
        incident_id: str,
        event_type: TimelineEventType,
        limit: int = 50,
    ) -> list[TimelineEvent]:
        """
        Get events of a specific type.

        Args:
            incident_id: ID of the incident
            event_type: Type of events to get
            limit: Maximum number to return

        Returns:
            List of TimelineEvent
        """
        events = self._events.get(incident_id, [])
        type_value = event_type.value if isinstance(event_type, TimelineEventType) else event_type
        filtered = [e for e in events if e.event_type == type_value]
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered[:limit]

    async def get_events_by_source(
        self,
        incident_id: str,
        source: EventSource,
        limit: int = 50,
    ) -> list[TimelineEvent]:
        """
        Get events from a specific source.

        Args:
            incident_id: ID of the incident
            source: Source of events
            limit: Maximum number to return

        Returns:
            List of TimelineEvent
        """
        events = self._events.get(incident_id, [])
        source_value = source.value if isinstance(source, EventSource) else source
        filtered = [e for e in events if e.source == source_value]
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered[:limit]

    async def get_timeline_statistics(
        self,
        incident_id: str,
    ) -> dict[str, Any]:
        """
        Get statistics about the timeline.

        Args:
            incident_id: ID of the incident

        Returns:
            Dictionary of statistics
        """
        events = self._events.get(incident_id, [])

        # Count by type
        by_type: dict[str, int] = {}
        for event in events:
            by_type[event.event_type] = by_type.get(event.event_type, 0) + 1

        # Count by source
        by_source: dict[str, int] = {}
        for event in events:
            by_source[event.source] = by_source.get(event.source, 0) + 1

        # Count by priority
        by_priority: dict[str, int] = {}
        for event in events:
            by_priority[event.priority] = by_priority.get(event.priority, 0) + 1

        # Time range
        if events:
            timestamps = [e.timestamp for e in events]
            first_event = min(timestamps)
            last_event = max(timestamps)
            duration = last_event - first_event
        else:
            first_event = None
            last_event = None
            duration = None

        return {
            "total_events": len(events),
            "pinned_count": sum(1 for e in events if e.is_pinned),
            "critical_count": by_priority.get(EventPriority.CRITICAL.value, 0),
            "by_type": by_type,
            "by_source": by_source,
            "by_priority": by_priority,
            "first_event": first_event.isoformat() if first_event else None,
            "last_event": last_event.isoformat() if last_event else None,
            "duration_seconds": duration.total_seconds() if duration else None,
        }

    async def export_timeline(
        self,
        incident_id: str,
        format_type: str = "json",
    ) -> dict[str, Any] | str:
        """
        Export timeline data.

        Args:
            incident_id: ID of the incident
            format_type: Export format (json, text)

        Returns:
            Exported timeline data
        """
        events = self._events.get(incident_id, [])
        events.sort(key=lambda x: x.timestamp)

        if format_type == "text":
            lines = []
            for event in events:
                timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                line = f"[{timestamp}] [{event.priority.upper()}] [{event.source}] {event.title}"
                if event.description:
                    line += f" - {event.description}"
                lines.append(line)
            return "\n".join(lines)

        return {
            "incident_id": incident_id,
            "exported_at": datetime.now(UTC).isoformat(),
            "event_count": len(events),
            "events": [e.model_dump() for e in events],
        }

    def register_handler(
        self,
        event_type: TimelineEventType,
        handler: Any,
    ) -> None:
        """
        Register a handler for a specific event type.

        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    async def _trigger_handlers(self, event: TimelineEvent) -> None:
        """Trigger registered handlers for an event."""
        event_type = TimelineEventType(event.event_type) if isinstance(event.event_type, str) else event.event_type
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    "timeline_handler_error",
                    event_type=event_type,
                    error=str(e),
                )
