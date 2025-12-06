"""
Event schemas for the G3TI RTCC-UIP Backend.

This module defines schemas for real-time events transmitted via WebSocket,
including event normalization, subscriptions, and message formats.

Events are normalized from various sources (ShotSpotter, Flock, etc.)
into a common format for consistent processing and display.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import GeoLocation, RTCCBaseModel


class EventType(str, Enum):
    """Types of real-time events."""

    # Gunshot detection events
    GUNSHOT = "gunshot"
    GUNSHOT_CONFIRMED = "gunshot_confirmed"

    # License plate reader events
    LPR_HIT = "lpr_hit"
    LPR_ALERT = "lpr_alert"

    # Camera events
    CAMERA_ALERT = "camera_alert"
    CAMERA_MOTION = "camera_motion"
    CAMERA_STATUS = "camera_status"

    # Incident events
    INCIDENT_CREATED = "incident_created"
    INCIDENT_UPDATED = "incident_updated"
    INCIDENT_CLOSED = "incident_closed"

    # Officer events
    OFFICER_DISPATCH = "officer_dispatch"
    OFFICER_ARRIVAL = "officer_arrival"
    OFFICER_CLEAR = "officer_clear"

    # System events
    SYSTEM_ALERT = "system_alert"
    SYSTEM_STATUS = "system_status"

    # Integration events
    INTEGRATION_DATA = "integration_data"
    INTEGRATION_ERROR = "integration_error"

    # AI Intelligence events
    AI_ANOMALY_DETECTED = "ai_anomaly_detected"
    AI_PATTERN_SHIFT = "ai_pattern_shift"
    AI_HIGH_RISK_ENTITY = "ai_high_risk_entity"
    AI_RELATIONSHIP_DISCOVERED = "ai_relationship_discovered"
    AI_PREDICTIVE_ALERT = "ai_predictive_alert"
    AI_ENTITY_RESOLVED = "ai_entity_resolved"
    AI_QUERY_RESULT = "ai_query_result"


class EventPriority(str, Enum):
    """Event priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventSource(str, Enum):
    """Sources of events."""

    SHOTSPOTTER = "shotspotter"
    FLOCK = "flock"
    MILESTONE = "milestone"
    ONESOLUTION = "onesolution"
    NESS = "ness"
    BWC = "bwc"
    HOTSHEETS = "hotsheets"
    CAD = "cad"
    MANUAL = "manual"
    SYSTEM = "system"
    AI_ENGINE = "ai_engine"


class EventBase(RTCCBaseModel):
    """Base schema for all events."""

    event_type: EventType = Field(description="Type of event")
    source: EventSource = Field(description="Source system of the event")
    priority: EventPriority = Field(default=EventPriority.MEDIUM, description="Event priority")
    title: str = Field(max_length=200, description="Event title/summary")
    description: str | None = Field(default=None, max_length=2000, description="Event description")
    location: GeoLocation | None = Field(default=None, description="Event location")
    address: str | None = Field(default=None, max_length=500, description="Event address")
    timestamp: datetime = Field(description="When the event occurred")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional event-specific metadata"
    )
    tags: list[str] = Field(default_factory=list, description="Event tags for filtering")


class EventCreate(EventBase):
    """Schema for creating a new event."""

    source_event_id: str | None = Field(
        default=None, max_length=100, description="Original event ID from source system"
    )
    related_entity_ids: list[str] = Field(
        default_factory=list, description="IDs of related entities (persons, vehicles, etc.)"
    )
    related_incident_id: str | None = Field(
        default=None, description="Related incident ID if applicable"
    )


class EventResponse(EventBase):
    """Schema for event response."""

    id: str = Field(description="Unique event identifier")
    source_event_id: str | None = Field(
        default=None, description="Original event ID from source system"
    )
    created_at: datetime = Field(description="When the event was created in the system")
    acknowledged: bool = Field(default=False, description="Whether event has been acknowledged")
    acknowledged_by: str | None = Field(default=None, description="User who acknowledged")
    acknowledged_at: datetime | None = Field(default=None, description="Acknowledgment timestamp")
    related_entity_ids: list[str] = Field(
        default_factory=list, description="IDs of related entities"
    )
    related_incident_id: str | None = Field(default=None, description="Related incident ID")


class WebSocketMessageType(str, Enum):
    """Types of WebSocket messages."""

    # Client to server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ACKNOWLEDGE = "acknowledge"
    PING = "ping"

    # Server to client
    EVENT = "event"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    ACKNOWLEDGED = "acknowledged"
    PONG = "pong"
    ERROR = "error"
    CONNECTED = "connected"


class WebSocketMessage(RTCCBaseModel):
    """Schema for WebSocket messages."""

    type: WebSocketMessageType = Field(description="Message type")
    payload: dict[str, Any] = Field(default_factory=dict, description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    message_id: str | None = Field(default=None, description="Message ID for correlation")


class EventSubscription(RTCCBaseModel):
    """Schema for event subscription configuration."""

    event_types: list[EventType] = Field(
        default_factory=list, description="Event types to subscribe to (empty = all)"
    )
    sources: list[EventSource] = Field(
        default_factory=list, description="Event sources to subscribe to (empty = all)"
    )
    priorities: list[EventPriority] = Field(
        default_factory=list, description="Priority levels to subscribe to (empty = all)"
    )
    geographic_bounds: dict[str, float] | None = Field(
        default=None, description="Geographic bounding box (north, south, east, west)"
    )
    tags: list[str] = Field(default_factory=list, description="Tags to filter by")


class EventAcknowledge(RTCCBaseModel):
    """Schema for acknowledging an event."""

    event_id: str = Field(description="Event ID to acknowledge")
    notes: str | None = Field(default=None, max_length=500, description="Acknowledgment notes")


class EventFilter(RTCCBaseModel):
    """Schema for filtering events in queries."""

    event_types: list[EventType] | None = None
    sources: list[EventSource] | None = None
    priorities: list[EventPriority] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    acknowledged: bool | None = None
    tags: list[str] | None = None
    search_query: str | None = Field(default=None, max_length=200)


# Normalized event schemas for specific sources


class ShotSpotterEvent(RTCCBaseModel):
    """Normalized ShotSpotter event data."""

    rounds_detected: int = Field(ge=1, description="Number of rounds detected")
    confidence: float = Field(ge=0, le=1, description="Detection confidence")
    sensor_ids: list[str] = Field(default_factory=list, description="Detecting sensor IDs")
    audio_url: str | None = Field(default=None, description="Audio clip URL")


class FlockLPREvent(RTCCBaseModel):
    """Normalized Flock LPR event data."""

    plate_number: str = Field(description="Detected license plate")
    plate_state: str | None = Field(default=None, description="Plate state")
    vehicle_make: str | None = Field(default=None, description="Vehicle make")
    vehicle_model: str | None = Field(default=None, description="Vehicle model")
    vehicle_color: str | None = Field(default=None, description="Vehicle color")
    camera_id: str = Field(description="Camera ID that captured the plate")
    image_url: str | None = Field(default=None, description="Capture image URL")
    alert_type: str | None = Field(default=None, description="Type of alert triggered")
    hotlist_name: str | None = Field(default=None, description="Matching hotlist name")


class CameraAlertEvent(RTCCBaseModel):
    """Normalized camera alert event data."""

    camera_id: str = Field(description="Camera ID")
    camera_name: str = Field(description="Camera name")
    alert_type: str = Field(description="Type of alert")
    confidence: float | None = Field(default=None, ge=0, le=1, description="Detection confidence")
    snapshot_url: str | None = Field(default=None, description="Snapshot URL")
    video_clip_url: str | None = Field(default=None, description="Video clip URL")
    detected_objects: list[str] = Field(
        default_factory=list, description="Detected objects/persons"
    )


class IncidentEvent(RTCCBaseModel):
    """Normalized incident event data."""

    incident_id: str = Field(description="Incident ID")
    incident_number: str = Field(description="Incident number")
    incident_type: str = Field(description="Incident type")
    status: str = Field(description="Incident status")
    responding_units: list[str] = Field(default_factory=list, description="Responding unit IDs")
    previous_status: str | None = Field(default=None, description="Previous status (for updates)")
