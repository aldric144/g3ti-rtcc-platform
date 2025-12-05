"""
Event normalizer for the G3TI RTCC-UIP Backend.

This module normalizes raw events from various sources into a
standardized format for consistent processing and storage.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.schemas.common import GeoLocation
from app.schemas.events import (
    EventCreate,
    EventPriority,
    EventSource,
    EventType,
)

logger = get_logger(__name__)


class EventNormalizer:
    """
    Normalizes events from various sources into a standard format.

    Each source has specific field mappings and transformation rules
    to convert raw data into the common EventCreate schema.
    """

    def __init__(self) -> None:
        """Initialize the event normalizer."""
        self._normalizers = {
            EventSource.SHOTSPOTTER: self._normalize_shotspotter,
            EventSource.FLOCK: self._normalize_flock,
            EventSource.MILESTONE: self._normalize_milestone,
            EventSource.ONESOLUTION: self._normalize_onesolution,
            EventSource.NESS: self._normalize_ness,
            EventSource.BWC: self._normalize_bwc,
            EventSource.HOTSHEETS: self._normalize_hotsheets,
            EventSource.CAD: self._normalize_cad,
        }

    async def normalize(self, source: EventSource, raw_data: dict[str, Any]) -> EventCreate:
        """
        Normalize raw event data from a specific source.

        Args:
            source: The event source
            raw_data: Raw event data from the source

        Returns:
            EventCreate: Normalized event ready for processing
        """
        normalizer = self._normalizers.get(source)
        if not normalizer:
            logger.warning("no_normalizer_for_source", source=source.value)
            return self._normalize_generic(source, raw_data)

        try:
            event = await normalizer(raw_data)
            logger.debug(
                "event_normalized",
                source=source.value,
                event_type=event.event_type.value,
            )
            return event
        except Exception as e:
            logger.error(
                "normalization_failed",
                source=source.value,
                error=str(e),
                raw_data=raw_data,
            )
            raise

    async def _normalize_shotspotter(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize ShotSpotter gunshot detection event."""
        # Extract location
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=float(raw_data["latitude"]),
                longitude=float(raw_data["longitude"]),
            )

        # Determine priority based on rounds detected
        rounds = raw_data.get("rounds", raw_data.get("roundsDetected", 1))
        if rounds >= 10:
            priority = EventPriority.CRITICAL
        elif rounds >= 5:
            priority = EventPriority.HIGH
        else:
            priority = EventPriority.HIGH  # All gunshots are at least high priority

        # Build description
        confidence = raw_data.get("confidence", 0.0)
        description = f"{rounds} round(s) detected with {confidence:.0%} confidence"
        if raw_data.get("sensorIds"):
            description += f". Detected by sensors: {', '.join(raw_data['sensorIds'])}"

        return EventCreate(
            event_type=EventType.GUNSHOT,
            source=EventSource.SHOTSPOTTER,
            priority=priority,
            title=f"Gunshot Detected - {rounds} Round(s)",
            description=description,
            location=location,
            address=raw_data.get("address"),
            timestamp=self._parse_timestamp(raw_data.get("timestamp")),
            source_event_id=raw_data.get("incidentId", raw_data.get("id")),
            metadata={
                "rounds_detected": rounds,
                "confidence": confidence,
                "sensor_ids": raw_data.get("sensorIds", []),
                "audio_url": raw_data.get("audioUrl"),
                "incident_type": raw_data.get("incidentType", "gunshot"),
            },
            tags=["gunshot", "shotspotter", f"rounds_{rounds}"],
        )

    async def _normalize_flock(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize Flock LPR event."""
        # Extract location
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=float(raw_data["latitude"]),
                longitude=float(raw_data["longitude"]),
            )

        # Determine event type and priority based on alert type
        alert_type = raw_data.get("alertType", "").lower()
        is_hotlist_hit = raw_data.get("hotlistMatch", False) or "hotlist" in alert_type

        if is_hotlist_hit:
            event_type = EventType.LPR_ALERT
            priority = EventPriority.HIGH
        else:
            event_type = EventType.LPR_HIT
            priority = EventPriority.MEDIUM

        # Build title and description
        plate = raw_data.get("plateNumber", raw_data.get("plate", "UNKNOWN"))
        state = raw_data.get("plateState", raw_data.get("state", ""))
        vehicle_desc = self._build_vehicle_description(raw_data)

        title = f"LPR {'Alert' if is_hotlist_hit else 'Read'}: {plate}"
        if state:
            title += f" ({state})"

        description = f"License plate {plate} captured"
        if vehicle_desc:
            description += f" - {vehicle_desc}"
        if is_hotlist_hit:
            hotlist_name = raw_data.get("hotlistName", "Unknown Hotlist")
            description += f". HOTLIST MATCH: {hotlist_name}"

        return EventCreate(
            event_type=event_type,
            source=EventSource.FLOCK,
            priority=priority,
            title=title,
            description=description,
            location=location,
            address=raw_data.get("address", raw_data.get("location")),
            timestamp=self._parse_timestamp(raw_data.get("timestamp", raw_data.get("captureTime"))),
            source_event_id=raw_data.get("id", raw_data.get("readId")),
            metadata={
                "plate_number": plate,
                "plate_state": state,
                "vehicle_make": raw_data.get("vehicleMake", raw_data.get("make")),
                "vehicle_model": raw_data.get("vehicleModel", raw_data.get("model")),
                "vehicle_color": raw_data.get("vehicleColor", raw_data.get("color")),
                "vehicle_year": raw_data.get("vehicleYear", raw_data.get("year")),
                "camera_id": raw_data.get("cameraId", raw_data.get("deviceId")),
                "camera_name": raw_data.get("cameraName", raw_data.get("deviceName")),
                "image_url": raw_data.get("imageUrl", raw_data.get("plateImageUrl")),
                "context_image_url": raw_data.get("contextImageUrl"),
                "hotlist_match": is_hotlist_hit,
                "hotlist_name": raw_data.get("hotlistName"),
                "alert_type": alert_type,
                "direction": raw_data.get("direction"),
                "speed": raw_data.get("speed"),
            },
            tags=self._build_flock_tags(raw_data, is_hotlist_hit),
        )

    async def _normalize_milestone(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize Milestone VMS camera event."""
        # Extract location
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=float(raw_data["latitude"]),
                longitude=float(raw_data["longitude"]),
            )

        # Determine event type based on alert type
        alert_type = raw_data.get("alertType", raw_data.get("eventType", "")).lower()
        if "motion" in alert_type:
            event_type = EventType.CAMERA_MOTION
            priority = EventPriority.LOW
        elif "analytics" in alert_type or "ai" in alert_type:
            event_type = EventType.CAMERA_ALERT
            priority = EventPriority.MEDIUM
        else:
            event_type = EventType.CAMERA_ALERT
            priority = EventPriority.MEDIUM

        # Increase priority for certain detection types
        detected_objects = raw_data.get("detectedObjects", [])
        if any(obj.lower() in ["weapon", "gun", "knife", "fight"] for obj in detected_objects):
            priority = EventPriority.HIGH

        camera_name = raw_data.get("cameraName", raw_data.get("deviceName", "Unknown Camera"))
        title = f"Camera Alert: {camera_name}"

        description = f"Alert from camera {camera_name}"
        if detected_objects:
            description += f". Detected: {', '.join(detected_objects)}"

        return EventCreate(
            event_type=event_type,
            source=EventSource.MILESTONE,
            priority=priority,
            title=title,
            description=description,
            location=location,
            address=raw_data.get("address", raw_data.get("location")),
            timestamp=self._parse_timestamp(raw_data.get("timestamp", raw_data.get("eventTime"))),
            source_event_id=raw_data.get("id", raw_data.get("eventId")),
            metadata={
                "camera_id": raw_data.get("cameraId", raw_data.get("deviceId")),
                "camera_name": camera_name,
                "alert_type": alert_type,
                "confidence": raw_data.get("confidence"),
                "snapshot_url": raw_data.get("snapshotUrl", raw_data.get("imageUrl")),
                "video_clip_url": raw_data.get("videoClipUrl", raw_data.get("clipUrl")),
                "detected_objects": detected_objects,
                "rule_name": raw_data.get("ruleName"),
                "zone_name": raw_data.get("zoneName"),
            },
            tags=["camera", "milestone", alert_type] + [obj.lower() for obj in detected_objects],
        )

    async def _normalize_onesolution(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize OneSolution CAD/RMS incident event."""
        # Extract location
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=float(raw_data["latitude"]),
                longitude=float(raw_data["longitude"]),
            )

        # Determine event type based on status
        status = raw_data.get("status", "").lower()
        if status in ["new", "created", "pending"]:
            event_type = EventType.INCIDENT_CREATED
        elif status in ["closed", "cleared", "completed"]:
            event_type = EventType.INCIDENT_CLOSED
        else:
            event_type = EventType.INCIDENT_UPDATED

        # Determine priority based on incident type
        incident_type = raw_data.get("incidentType", raw_data.get("callType", "")).lower()
        priority = self._get_incident_priority(incident_type)

        incident_number = raw_data.get("incidentNumber", raw_data.get("callNumber", "Unknown"))
        title = f"Incident {incident_number}: {raw_data.get('incidentType', 'Unknown Type')}"

        description = raw_data.get("narrative", raw_data.get("description", ""))
        if not description:
            description = f"Incident type: {incident_type}. Status: {status}"

        responding_units = raw_data.get("respondingUnits", raw_data.get("units", []))
        if responding_units:
            description += f". Responding units: {', '.join(responding_units)}"

        return EventCreate(
            event_type=event_type,
            source=EventSource.ONESOLUTION,
            priority=priority,
            title=title,
            description=description,
            location=location,
            address=raw_data.get("address", raw_data.get("location")),
            timestamp=self._parse_timestamp(raw_data.get("timestamp", raw_data.get("callTime"))),
            source_event_id=raw_data.get("id", raw_data.get("incidentId")),
            related_incident_id=raw_data.get("incidentId"),
            metadata={
                "incident_id": raw_data.get("incidentId"),
                "incident_number": incident_number,
                "incident_type": incident_type,
                "call_type": raw_data.get("callType"),
                "status": status,
                "priority_code": raw_data.get("priorityCode"),
                "responding_units": responding_units,
                "caller_info": raw_data.get("callerInfo"),
                "disposition": raw_data.get("disposition"),
                "beat": raw_data.get("beat"),
                "district": raw_data.get("district"),
            },
            tags=["incident", "cad", incident_type.replace(" ", "_")],
        )

    async def _normalize_ness(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize NESS records management event."""
        # NESS typically provides person/case updates
        record_type = raw_data.get("recordType", "record").lower()

        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=float(raw_data["latitude"]),
                longitude=float(raw_data["longitude"]),
            )

        event_type = EventType.INTEGRATION_DATA
        priority = EventPriority.MEDIUM

        # Check for warrant or alert flags
        if raw_data.get("hasWarrant") or raw_data.get("alertFlag"):
            priority = EventPriority.HIGH

        title = f"NESS {record_type.title()} Update"
        if raw_data.get("caseNumber"):
            title += f": {raw_data['caseNumber']}"

        description = raw_data.get("description", "Record update from NESS RMS")

        return EventCreate(
            event_type=event_type,
            source=EventSource.NESS,
            priority=priority,
            title=title,
            description=description,
            location=location,
            address=raw_data.get("address"),
            timestamp=self._parse_timestamp(raw_data.get("timestamp", raw_data.get("updateTime"))),
            source_event_id=raw_data.get("id", raw_data.get("recordId")),
            metadata={
                "record_type": record_type,
                "record_id": raw_data.get("recordId"),
                "case_number": raw_data.get("caseNumber"),
                "person_id": raw_data.get("personId"),
                "has_warrant": raw_data.get("hasWarrant", False),
                "alert_flag": raw_data.get("alertFlag", False),
                "alert_reason": raw_data.get("alertReason"),
                "officer_id": raw_data.get("officerId"),
            },
            tags=["ness", "rms", record_type],
        )

    async def _normalize_bwc(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize body-worn camera event."""
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=float(raw_data["latitude"]),
                longitude=float(raw_data["longitude"]),
            )

        # BWC events are typically recording start/stop or flagged events
        event_subtype = raw_data.get("eventType", "recording").lower()

        if "flag" in event_subtype or raw_data.get("flagged"):
            priority = EventPriority.HIGH
            event_type = EventType.SYSTEM_ALERT
        else:
            priority = EventPriority.LOW
            event_type = EventType.INTEGRATION_DATA

        officer_name = raw_data.get("officerName", raw_data.get("officerId", "Unknown Officer"))
        title = f"BWC Event: {officer_name}"

        description = f"Body-worn camera event from {officer_name}"
        if raw_data.get("flagReason"):
            description += f". Flag reason: {raw_data['flagReason']}"

        return EventCreate(
            event_type=event_type,
            source=EventSource.BWC,
            priority=priority,
            title=title,
            description=description,
            location=location,
            address=raw_data.get("address"),
            timestamp=self._parse_timestamp(raw_data.get("timestamp", raw_data.get("eventTime"))),
            source_event_id=raw_data.get("id", raw_data.get("eventId")),
            metadata={
                "officer_id": raw_data.get("officerId"),
                "officer_name": officer_name,
                "device_id": raw_data.get("deviceId"),
                "recording_id": raw_data.get("recordingId"),
                "event_subtype": event_subtype,
                "flagged": raw_data.get("flagged", False),
                "flag_reason": raw_data.get("flagReason"),
                "duration": raw_data.get("duration"),
                "video_url": raw_data.get("videoUrl"),
            },
            tags=["bwc", "body_camera", event_subtype],
        )

    async def _normalize_hotsheets(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize HotSheets wanted vehicle/person alert."""
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=float(raw_data["latitude"]),
                longitude=float(raw_data["longitude"]),
            )

        # HotSheets alerts are always high priority
        alert_type = raw_data.get("alertType", "wanted").lower()

        if "stolen" in alert_type or "felony" in alert_type:
            priority = EventPriority.CRITICAL
        else:
            priority = EventPriority.HIGH

        event_type = EventType.LPR_ALERT if raw_data.get("plateNumber") else EventType.SYSTEM_ALERT

        # Build title based on alert type
        if raw_data.get("plateNumber"):
            title = f"HotSheet Alert: {raw_data['plateNumber']}"
        elif raw_data.get("personName"):
            title = f"HotSheet Alert: {raw_data['personName']}"
        else:
            title = f"HotSheet Alert: {alert_type.title()}"

        description = raw_data.get("reason", raw_data.get("description", ""))
        if not description:
            description = f"HotSheet {alert_type} alert"

        return EventCreate(
            event_type=event_type,
            source=EventSource.HOTSHEETS,
            priority=priority,
            title=title,
            description=description,
            location=location,
            address=raw_data.get("address"),
            timestamp=self._parse_timestamp(raw_data.get("timestamp")),
            source_event_id=raw_data.get("id", raw_data.get("alertId")),
            metadata={
                "alert_type": alert_type,
                "plate_number": raw_data.get("plateNumber"),
                "plate_state": raw_data.get("plateState"),
                "vehicle_description": raw_data.get("vehicleDescription"),
                "person_name": raw_data.get("personName"),
                "person_description": raw_data.get("personDescription"),
                "reason": raw_data.get("reason"),
                "entered_by": raw_data.get("enteredBy"),
                "entered_date": raw_data.get("enteredDate"),
                "expiration_date": raw_data.get("expirationDate"),
                "ncic_number": raw_data.get("ncicNumber"),
                "case_number": raw_data.get("caseNumber"),
            },
            tags=["hotsheet", "wanted", alert_type],
        )

    async def _normalize_cad(self, raw_data: dict[str, Any]) -> EventCreate:
        """Normalize generic CAD event (fallback for non-OneSolution CAD)."""
        return await self._normalize_onesolution(raw_data)

    def _normalize_generic(self, source: EventSource, raw_data: dict[str, Any]) -> EventCreate:
        """Generic normalizer for unknown sources."""
        location = None
        if "latitude" in raw_data and "longitude" in raw_data:
            location = GeoLocation(
                latitude=float(raw_data["latitude"]),
                longitude=float(raw_data["longitude"]),
            )

        return EventCreate(
            event_type=EventType.INTEGRATION_DATA,
            source=source,
            priority=EventPriority.MEDIUM,
            title=raw_data.get("title", f"Event from {source.value}"),
            description=raw_data.get("description", str(raw_data)),
            location=location,
            address=raw_data.get("address"),
            timestamp=self._parse_timestamp(raw_data.get("timestamp")),
            source_event_id=raw_data.get("id"),
            metadata=raw_data,
            tags=[source.value],
        )

    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse timestamp from various formats."""
        if timestamp is None:
            return datetime.now(UTC)

        if isinstance(timestamp, datetime):
            return timestamp

        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(timestamp, tz=UTC)

        if isinstance(timestamp, str):
            # Try ISO format first
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                pass

            # Try common formats
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
                "%m/%d/%Y %H:%M:%S",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt).replace(tzinfo=UTC)
                except ValueError:
                    continue

        logger.warning("unparseable_timestamp", timestamp=timestamp)
        return datetime.now(UTC)

    def _build_vehicle_description(self, raw_data: dict[str, Any]) -> str:
        """Build a human-readable vehicle description."""
        parts = []

        year = raw_data.get("vehicleYear", raw_data.get("year"))
        if year:
            parts.append(str(year))

        color = raw_data.get("vehicleColor", raw_data.get("color"))
        if color:
            parts.append(color)

        make = raw_data.get("vehicleMake", raw_data.get("make"))
        if make:
            parts.append(make)

        model = raw_data.get("vehicleModel", raw_data.get("model"))
        if model:
            parts.append(model)

        return " ".join(parts)

    def _build_flock_tags(self, raw_data: dict[str, Any], is_hotlist_hit: bool) -> list[str]:
        """Build tags for Flock LPR events."""
        tags = ["lpr", "flock"]

        if is_hotlist_hit:
            tags.append("hotlist_hit")
            if raw_data.get("hotlistName"):
                tags.append(f"hotlist_{raw_data['hotlistName'].lower().replace(' ', '_')}")

        if raw_data.get("vehicleMake"):
            tags.append(raw_data["vehicleMake"].lower())

        if raw_data.get("plateState"):
            tags.append(f"state_{raw_data['plateState'].lower()}")

        return tags

    def _get_incident_priority(self, incident_type: str) -> EventPriority:
        """Determine priority based on incident type."""
        critical_types = [
            "shooting",
            "shots fired",
            "homicide",
            "murder",
            "active shooter",
            "hostage",
            "bomb",
            "explosion",
        ]
        high_types = [
            "robbery",
            "assault",
            "burglary in progress",
            "pursuit",
            "officer down",
            "officer needs assistance",
            "domestic violence",
            "kidnapping",
            "carjacking",
            "stabbing",
        ]
        medium_types = [
            "theft",
            "burglary",
            "vandalism",
            "disturbance",
            "suspicious",
            "trespass",
            "accident with injuries",
        ]

        incident_lower = incident_type.lower()

        if any(t in incident_lower for t in critical_types):
            return EventPriority.CRITICAL
        elif any(t in incident_lower for t in high_types):
            return EventPriority.HIGH
        elif any(t in incident_lower for t in medium_types):
            return EventPriority.MEDIUM
        else:
            return EventPriority.LOW
