"""
Event processor for the G3TI RTCC-UIP Backend.

This module provides event normalization and processing for events
from various sources (ShotSpotter, Flock, Milestone, etc.).

The event processor:
- Normalizes events from different formats
- Enriches events with additional data
- Routes events to appropriate handlers
- Logs events for audit purposes
"""

import uuid
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.schemas.common import GeoLocation
from app.schemas.events import (
    EventCreate,
    EventPriority,
    EventResponse,
    EventSource,
    EventType,
)
from app.services.events.websocket_manager import WebSocketManager, get_websocket_manager

logger = get_logger(__name__)


class EventProcessor:
    """
    Processes and normalizes events from various sources.

    Provides methods for:
    - Event normalization from different source formats
    - Event enrichment with additional context
    - Event routing to WebSocket clients
    - Event persistence and logging
    """

    def __init__(self, ws_manager: WebSocketManager | None = None) -> None:
        """
        Initialize the event processor.

        Args:
            ws_manager: WebSocket manager for broadcasting
        """
        self._ws_manager = ws_manager
        self._event_store: dict[str, EventResponse] = {}  # In-memory store
        self._handlers: dict[
            EventSource, Callable[[dict[str, Any]], Coroutine[Any, Any, EventCreate]]
        ] = {}

        # Register source-specific normalizers
        self._register_normalizers()

    def _register_normalizers(self) -> None:
        """Register event normalizers for each source."""
        self._handlers[EventSource.SHOTSPOTTER] = self._normalize_shotspotter
        self._handlers[EventSource.FLOCK] = self._normalize_flock
        self._handlers[EventSource.MILESTONE] = self._normalize_milestone
        self._handlers[EventSource.CAD] = self._normalize_cad
        self._handlers[EventSource.MANUAL] = self._normalize_manual
        self._handlers[EventSource.SYSTEM] = self._normalize_system

    async def _get_ws_manager(self) -> WebSocketManager:
        """Get WebSocket manager, using global if not provided."""
        if self._ws_manager is None:
            self._ws_manager = get_websocket_manager()
        return self._ws_manager

    async def process_event(
        self, source: EventSource, raw_data: dict[str, Any], user_id: str | None = None
    ) -> EventResponse:
        """
        Process and normalize an event from a source.

        Args:
            source: Event source
            raw_data: Raw event data from source
            user_id: User ID if manually created

        Returns:
            EventResponse: Processed event
        """
        # Get normalizer for source
        normalizer = self._handlers.get(source, self._normalize_generic)

        # Normalize event
        event_create = await normalizer(raw_data)

        # Create event response
        event_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        event = EventResponse(
            id=event_id,
            event_type=event_create.event_type,
            source=event_create.source,
            priority=event_create.priority,
            title=event_create.title,
            description=event_create.description,
            location=event_create.location,
            address=event_create.address,
            timestamp=event_create.timestamp,
            metadata=event_create.metadata,
            tags=event_create.tags,
            source_event_id=event_create.source_event_id,
            created_at=now,
            related_entity_ids=event_create.related_entity_ids,
            related_incident_id=event_create.related_incident_id,
        )

        # Store event
        self._event_store[event_id] = event

        # Broadcast to WebSocket clients
        ws_manager = await self._get_ws_manager()

        location_dict = None
        if event.location:
            location_dict = {"lat": event.location.latitude, "lon": event.location.longitude}

        await ws_manager.broadcast_event(
            event_type=event.event_type,
            source=event.source,
            priority=event.priority,
            payload=event.model_dump(),
            location=location_dict,
            tags=event.tags,
        )

        # Log event
        logger.info(
            "event_processed",
            event_id=event_id,
            event_type=event.event_type.value,
            source=source.value,
            priority=event.priority.value,
        )

        return event

    async def get_event(self, event_id: str) -> EventResponse | None:
        """
        Get an event by ID.

        Args:
            event_id: Event identifier

        Returns:
            EventResponse or None: Event if found
        """
        return self._event_store.get(event_id)

    async def acknowledge_event(
        self, event_id: str, user_id: str, notes: str | None = None
    ) -> bool:
        """
        Acknowledge an event.

        Args:
            event_id: Event identifier
            user_id: User acknowledging the event
            notes: Optional acknowledgment notes

        Returns:
            bool: True if acknowledged successfully
        """
        event = self._event_store.get(event_id)
        if not event:
            return False

        event.acknowledged = True
        event.acknowledged_by = user_id
        event.acknowledged_at = datetime.now(UTC)

        if notes:
            event.metadata["acknowledgment_notes"] = notes

        logger.info("event_acknowledged", event_id=event_id, user_id=user_id)

        return True

    async def get_recent_events(
        self,
        limit: int = 100,
        event_types: list[EventType] | None = None,
        sources: list[EventSource] | None = None,
        acknowledged: bool | None = None,
    ) -> list[EventResponse]:
        """
        Get recent events with optional filtering.

        Args:
            limit: Maximum events to return
            event_types: Filter by event types
            sources: Filter by sources
            acknowledged: Filter by acknowledgment status

        Returns:
            list: Recent events
        """
        events = list(self._event_store.values())

        # Apply filters
        if event_types:
            events = [e for e in events if e.event_type in event_types]

        if sources:
            events = [e for e in events if e.source in sources]

        if acknowledged is not None:
            events = [e for e in events if e.acknowledged == acknowledged]

        # Sort by timestamp descending
        events.sort(key=lambda e: e.timestamp, reverse=True)

        return events[:limit]

    # Source-specific normalizers

    async def _normalize_shotspotter(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize ShotSpotter event data."""
        rounds = raw_data.get("rounds_detected", 1)
        confidence = raw_data.get("confidence", 0.0)

        # Determine priority based on rounds and confidence
        if rounds >= 10 or confidence >= 0.95:
            priority = EventPriority.CRITICAL
        elif rounds >= 5 or confidence >= 0.8:
            priority = EventPriority.HIGH
        else:
            priority = EventPriority.MEDIUM

        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=raw_data["latitude"],
                longitude=raw_data["longitude"],
                accuracy=raw_data.get("accuracy"),
            )

        return EventCreate(
            event_type=EventType.GUNSHOT,
            source=EventSource.SHOTSPOTTER,
            priority=priority,
            title=f"Gunshot Detected - {rounds} round(s)",
            description=f"ShotSpotter detected {rounds} round(s) with {confidence:.0%} confidence",
            location=location,
            address=raw_data.get("address"),
            timestamp=datetime.fromisoformat(
                raw_data.get("timestamp", datetime.now(UTC).isoformat())
            ),
            metadata={
                "rounds_detected": rounds,
                "confidence": confidence,
                "sensor_ids": raw_data.get("sensor_ids", []),
                "audio_url": raw_data.get("audio_url"),
            },
            tags=["gunshot", "shotspotter"],
            source_event_id=raw_data.get("event_id"),
        )

    async def _normalize_flock(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize Flock Safety LPR event data."""
        plate = raw_data.get("plate_number", "UNKNOWN")
        alert_type = raw_data.get("alert_type", "detection")

        # Determine priority based on alert type
        if alert_type in ("stolen", "wanted", "amber_alert"):
            priority = EventPriority.CRITICAL
        elif alert_type in ("bolo", "hotlist"):
            priority = EventPriority.HIGH
        else:
            priority = EventPriority.LOW

        # Determine event type
        if alert_type in ("stolen", "wanted", "bolo", "hotlist", "amber_alert"):
            event_type = EventType.LPR_ALERT
        else:
            event_type = EventType.LPR_HIT

        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(latitude=raw_data["latitude"], longitude=raw_data["longitude"])

        vehicle_desc = (
            " ".join(
                filter(
                    None,
                    [
                        raw_data.get("vehicle_color"),
                        raw_data.get("vehicle_make"),
                        raw_data.get("vehicle_model"),
                    ],
                )
            )
            or "Vehicle"
        )

        return EventCreate(
            event_type=event_type,
            source=EventSource.FLOCK,
            priority=priority,
            title=f"LPR: {plate} - {alert_type.replace('_', ' ').title()}",
            description=f"{vehicle_desc} with plate {plate} detected",
            location=location,
            address=raw_data.get("address"),
            timestamp=datetime.fromisoformat(
                raw_data.get("timestamp", datetime.now(UTC).isoformat())
            ),
            metadata={
                "plate_number": plate,
                "plate_state": raw_data.get("plate_state"),
                "vehicle_make": raw_data.get("vehicle_make"),
                "vehicle_model": raw_data.get("vehicle_model"),
                "vehicle_color": raw_data.get("vehicle_color"),
                "camera_id": raw_data.get("camera_id"),
                "image_url": raw_data.get("image_url"),
                "alert_type": alert_type,
                "hotlist_name": raw_data.get("hotlist_name"),
            },
            tags=["lpr", "flock", alert_type],
            source_event_id=raw_data.get("event_id"),
        )

    async def _normalize_milestone(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize Milestone VMS event data."""
        alert_type = raw_data.get("alert_type", "motion")
        camera_name = raw_data.get("camera_name", "Unknown Camera")

        # Determine priority
        if alert_type in ("intrusion", "gunshot", "person_down"):
            priority = EventPriority.HIGH
        elif alert_type in ("motion", "loitering"):
            priority = EventPriority.MEDIUM
        else:
            priority = EventPriority.LOW

        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(latitude=raw_data["latitude"], longitude=raw_data["longitude"])

        return EventCreate(
            event_type=EventType.CAMERA_ALERT,
            source=EventSource.MILESTONE,
            priority=priority,
            title=f"Camera Alert: {camera_name} - {alert_type.replace('_', ' ').title()}",
            description=raw_data.get("description", f"Alert from {camera_name}"),
            location=location,
            address=raw_data.get("address"),
            timestamp=datetime.fromisoformat(
                raw_data.get("timestamp", datetime.now(UTC).isoformat())
            ),
            metadata={
                "camera_id": raw_data.get("camera_id"),
                "camera_name": camera_name,
                "alert_type": alert_type,
                "confidence": raw_data.get("confidence"),
                "snapshot_url": raw_data.get("snapshot_url"),
                "video_clip_url": raw_data.get("video_clip_url"),
                "detected_objects": raw_data.get("detected_objects", []),
            },
            tags=["camera", "milestone", alert_type],
            source_event_id=raw_data.get("event_id"),
        )

    async def _normalize_cad(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize CAD (Computer Aided Dispatch) event data."""
        incident_type = raw_data.get("incident_type", "unknown")
        status = raw_data.get("status", "active")

        # Map status to event type
        if status == "created":
            event_type = EventType.INCIDENT_CREATED
        elif status == "closed":
            event_type = EventType.INCIDENT_CLOSED
        else:
            event_type = EventType.INCIDENT_UPDATED

        # Determine priority
        priority_map = {
            "shooting": EventPriority.CRITICAL,
            "homicide": EventPriority.CRITICAL,
            "robbery": EventPriority.HIGH,
            "assault": EventPriority.HIGH,
            "burglary": EventPriority.MEDIUM,
            "theft": EventPriority.LOW,
        }
        priority = priority_map.get(incident_type.lower(), EventPriority.MEDIUM)

        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(latitude=raw_data["latitude"], longitude=raw_data["longitude"])

        return EventCreate(
            event_type=event_type,
            source=EventSource.CAD,
            priority=priority,
            title=f"Incident: {incident_type.replace('_', ' ').title()} - {status.title()}",
            description=raw_data.get("description", ""),
            location=location,
            address=raw_data.get("address"),
            timestamp=datetime.fromisoformat(
                raw_data.get("timestamp", datetime.now(UTC).isoformat())
            ),
            metadata={
                "incident_number": raw_data.get("incident_number"),
                "incident_type": incident_type,
                "status": status,
                "responding_units": raw_data.get("responding_units", []),
                "caller_info": raw_data.get("caller_info"),
            },
            tags=["incident", "cad", incident_type],
            source_event_id=raw_data.get("event_id"),
            related_incident_id=raw_data.get("incident_id"),
        )

    async def _normalize_manual(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize manually created event data."""
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(latitude=raw_data["latitude"], longitude=raw_data["longitude"])

        return EventCreate(
            event_type=EventType(raw_data.get("event_type", "system_alert")),
            source=EventSource.MANUAL,
            priority=EventPriority(raw_data.get("priority", "medium")),
            title=raw_data.get("title", "Manual Event"),
            description=raw_data.get("description"),
            location=location,
            address=raw_data.get("address"),
            timestamp=datetime.fromisoformat(
                raw_data.get("timestamp", datetime.now(UTC).isoformat())
            ),
            metadata=raw_data.get("metadata", {}),
            tags=raw_data.get("tags", ["manual"]),
        )

    async def _normalize_system(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize system event data."""
        return EventCreate(
            event_type=EventType.SYSTEM_ALERT,
            source=EventSource.SYSTEM,
            priority=EventPriority(raw_data.get("priority", "info")),
            title=raw_data.get("title", "System Event"),
            description=raw_data.get("description"),
            location=None,
            address=None,
            timestamp=datetime.now(UTC),
            metadata=raw_data.get("metadata", {}),
            tags=["system"],
        )

    async def _normalize_generic(self, raw_data: dict[str, Any]) -> EventCreate:
        """Generic normalizer for unknown sources."""
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(latitude=raw_data["latitude"], longitude=raw_data["longitude"])

        return EventCreate(
            event_type=EventType(raw_data.get("event_type", "integration_data")),
            source=EventSource(raw_data.get("source", "system")),
            priority=EventPriority(raw_data.get("priority", "medium")),
            title=raw_data.get("title", "Event"),
            description=raw_data.get("description"),
            location=location,
            address=raw_data.get("address"),
            timestamp=datetime.fromisoformat(
                raw_data.get("timestamp", datetime.now(UTC).isoformat())
            ),
            metadata=raw_data,
            tags=raw_data.get("tags", []),
            source_event_id=raw_data.get("event_id"),
        )


# Global event processor instance
_event_processor: EventProcessor | None = None


def get_event_processor() -> EventProcessor:
    """Get the event processor instance."""
    global _event_processor
    if _event_processor is None:
        _event_processor = EventProcessor()
    return _event_processor
