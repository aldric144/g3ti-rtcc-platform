"""
BWC (Body-Worn Camera) integration for the G3TI RTCC-UIP Backend.

Body-Worn Camera systems provide:
- Video recording management
- Evidence chain of custody
- Video redaction and export
- Sharing and collaboration
- Comprehensive audit trails

This integration enables:
- Video retrieval and streaming
- Recording status and metadata
- Evidence management and tagging
- Officer assignment lookup
- Incident linking and categorization
- Real-time recording events via webhook
"""

import hashlib
import hmac
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.logging import audit_logger, get_logger
from app.integrations.base import BaseIntegration
from app.schemas.events import EventSource

logger = get_logger(__name__)


class BWCIntegration(BaseIntegration[dict[str, Any]]):
    """
    Body-Worn Camera integration client.

    Provides methods for interacting with BWC systems including
    video retrieval, recording status, and evidence management.

    Supports common BWC platforms like Axon, Motorola, etc.
    """

    ENDPOINT_HEALTH = "/api/v1/health"
    ENDPOINT_RECORDINGS = "/api/v1/recordings"
    ENDPOINT_RECORDING_DETAIL = "/api/v1/recordings/{recording_id}"
    ENDPOINT_RECORDING_STREAM = "/api/v1/recordings/{recording_id}/stream"
    ENDPOINT_RECORDING_DOWNLOAD = "/api/v1/recordings/{recording_id}/download"
    ENDPOINT_OFFICERS = "/api/v1/officers"
    ENDPOINT_OFFICER_DETAIL = "/api/v1/officers/{officer_id}"
    ENDPOINT_OFFICER_RECORDINGS = "/api/v1/officers/{officer_id}/recordings"
    ENDPOINT_DEVICES = "/api/v1/devices"
    ENDPOINT_DEVICE_STATUS = "/api/v1/devices/{device_id}/status"
    ENDPOINT_INCIDENTS = "/api/v1/incidents"
    ENDPOINT_INCIDENT_RECORDINGS = "/api/v1/incidents/{incident_id}/recordings"
    ENDPOINT_TAGS = "/api/v1/recordings/{recording_id}/tags"
    ENDPOINT_EVIDENCE = "/api/v1/evidence"

    def __init__(self) -> None:
        """Initialize BWC integration."""
        super().__init__(
            base_url=settings.bwc_api_url,
            api_key=settings.bwc_api_key,
            timeout=30.0,
        )
        self._agency_id = getattr(settings, "bwc_agency_id", None)
        self._webhook_secret = getattr(settings, "bwc_webhook_secret", None)

    @property
    def source(self) -> EventSource:
        """Get the event source."""
        return EventSource.BWC

    def _get_auth_headers(self) -> dict[str, str]:
        """Get BWC-specific authentication headers."""
        headers = super()._get_auth_headers()
        if self._api_key:
            headers["X-BWC-API-Key"] = self._api_key
        if self._agency_id:
            headers["X-Agency-ID"] = self._agency_id
        return headers

    async def health_check(self) -> bool:
        """
        Verify connectivity to BWC system.

        Returns:
            bool: True if BWC system is reachable and responding
        """
        if not self.is_configured:
            return False

        try:
            response = await self.get(self.ENDPOINT_HEALTH)
            return response.get("status") in ["healthy", "ok", "connected"]
        except Exception as e:
            logger.warning("bwc_health_check_failed", error=str(e))
            return False

    async def normalize_event(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize BWC event data.

        Args:
            raw_data: Raw data from BWC system

        Returns:
            dict: Normalized data with standard fields
        """
        recording = raw_data.get("recording", raw_data)
        officer = recording.get("officer", {})
        device = recording.get("device", {})

        return {
            "source": "bwc",
            "recording_id": recording.get("id", recording.get("recordingId")),
            "timestamp": recording.get("timestamp", recording.get("startTime")),
            "officer_id": officer.get("id", recording.get("officerId")),
            "officer_name": officer.get("name", recording.get("officerName")),
            "device_id": device.get("id", recording.get("deviceId")),
            "device_serial": device.get("serialNumber"),
            "duration": recording.get("duration"),
            "status": recording.get("status"),
            "category": recording.get("category"),
            "tags": recording.get("tags", []),
            "incident_id": recording.get("incidentId"),
            "latitude": recording.get("latitude"),
            "longitude": recording.get("longitude"),
        }

    async def get_recordings(
        self,
        officer_id: str | None = None,
        incident_id: str | None = None,
        device_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get BWC recordings with filters.

        Args:
            officer_id: Filter by officer
            incident_id: Filter by incident
            device_id: Filter by device
            start_date: Start date filter
            end_date: End date filter
            category: Filter by category
            status: Filter by status
            limit: Maximum results

        Returns:
            list: Recording metadata
        """
        if not self.is_connected:
            logger.warning("bwc_not_connected_for_recordings")
            return []

        try:
            params: dict[str, Any] = {"limit": limit}

            if officer_id:
                params["officerId"] = officer_id
            if incident_id:
                params["incidentId"] = incident_id
            if device_id:
                params["deviceId"] = device_id
            if start_date:
                params["startDate"] = start_date.isoformat()
            if end_date:
                params["endDate"] = end_date.isoformat()
            if category:
                params["category"] = category
            if status:
                params["status"] = status

            response = await self.get(self.ENDPOINT_RECORDINGS, params=params)
            recordings = response.get("recordings", response.get("items", []))

            logger.info("bwc_recordings_retrieved", count=len(recordings))

            return recordings

        except Exception as e:
            logger.error("bwc_get_recordings_failed", error=str(e))
            return []

    async def get_recording_detail(self, recording_id: str) -> dict[str, Any] | None:
        """
        Get detailed information for a specific recording.

        Args:
            recording_id: Recording identifier

        Returns:
            dict | None: Recording details including metadata and evidence info
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_RECORDING_DETAIL.format(recording_id=recording_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("bwc_get_recording_detail_failed", recording_id=recording_id, error=str(e))
            return None

    async def get_recording_stream_url(
        self,
        recording_id: str,
        user_id: str | None = None,
        purpose: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Get streaming URL for a recording.

        Args:
            recording_id: Recording identifier
            user_id: User requesting access (for audit)
            purpose: Purpose of access (for audit)

        Returns:
            dict | None: Stream URL and access token
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_RECORDING_STREAM.format(recording_id=recording_id)

            data: dict[str, Any] = {}
            if user_id:
                data["requestedBy"] = user_id
            if purpose:
                data["purpose"] = purpose

            response = await self.post(endpoint, data=data)

            audit_logger.log_entity_access(
                entity_type="bwc_recording",
                entity_id=recording_id,
                action="stream",
                user_id=user_id or "system",
                details={"purpose": purpose},
            )

            logger.info("bwc_stream_url_generated", recording_id=recording_id)

            return response

        except Exception as e:
            logger.error("bwc_get_stream_url_failed", recording_id=recording_id, error=str(e))
            return None

    async def get_recording_download_url(
        self,
        recording_id: str,
        user_id: str | None = None,
        purpose: str | None = None,
        format: str = "mp4",
    ) -> dict[str, Any] | None:
        """
        Get download URL for a recording.

        Args:
            recording_id: Recording identifier
            user_id: User requesting download (for audit)
            purpose: Purpose of download (for audit)
            format: Download format (mp4, original)

        Returns:
            dict | None: Download URL and expiration
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_RECORDING_DOWNLOAD.format(recording_id=recording_id)

            data: dict[str, Any] = {"format": format}
            if user_id:
                data["requestedBy"] = user_id
            if purpose:
                data["purpose"] = purpose

            response = await self.post(endpoint, data=data)

            audit_logger.log_entity_access(
                entity_type="bwc_recording",
                entity_id=recording_id,
                action="download",
                user_id=user_id or "system",
                details={"purpose": purpose, "format": format},
            )

            logger.info("bwc_download_url_generated", recording_id=recording_id)

            return response

        except Exception as e:
            logger.error("bwc_get_download_url_failed", recording_id=recording_id, error=str(e))
            return None

    async def get_officers(self, status: str | None = None) -> list[dict[str, Any]]:
        """
        Get officers with BWC assignments.

        Args:
            status: Filter by status (active, inactive)

        Returns:
            list: Officer information
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {}
            if status:
                params["status"] = status

            response = await self.get(self.ENDPOINT_OFFICERS, params=params)
            return response.get("officers", [])

        except Exception as e:
            logger.error("bwc_get_officers_failed", error=str(e))
            return []

    async def get_officer_detail(self, officer_id: str) -> dict[str, Any] | None:
        """
        Get detailed information for an officer.

        Args:
            officer_id: Officer identifier

        Returns:
            dict | None: Officer details including device assignments
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_OFFICER_DETAIL.format(officer_id=officer_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("bwc_get_officer_detail_failed", officer_id=officer_id, error=str(e))
            return None

    async def get_officer_recordings(
        self,
        officer_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get recordings for a specific officer.

        Args:
            officer_id: Officer identifier
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum results

        Returns:
            list: Officer's recordings
        """
        if not self.is_connected:
            return []

        try:
            endpoint = self.ENDPOINT_OFFICER_RECORDINGS.format(officer_id=officer_id)
            params: dict[str, Any] = {"limit": limit}

            if start_date:
                params["startDate"] = start_date.isoformat()
            if end_date:
                params["endDate"] = end_date.isoformat()

            response = await self.get(endpoint, params=params)
            return response.get("recordings", [])

        except Exception as e:
            logger.error("bwc_get_officer_recordings_failed", officer_id=officer_id, error=str(e))
            return []

    async def get_devices(self, status: str | None = None) -> list[dict[str, Any]]:
        """
        Get BWC devices.

        Args:
            status: Filter by status (online, offline, charging)

        Returns:
            list: Device information
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {}
            if status:
                params["status"] = status

            response = await self.get(self.ENDPOINT_DEVICES, params=params)
            return response.get("devices", [])

        except Exception as e:
            logger.error("bwc_get_devices_failed", error=str(e))
            return []

    async def get_device_status(self, device_id: str) -> dict[str, Any] | None:
        """
        Get status of a specific device.

        Args:
            device_id: Device identifier

        Returns:
            dict | None: Device status including battery, storage, connectivity
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_DEVICE_STATUS.format(device_id=device_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("bwc_get_device_status_failed", device_id=device_id, error=str(e))
            return None

    async def link_to_incident(
        self,
        recording_id: str,
        incident_id: str,
        user_id: str | None = None,
        notes: str | None = None,
    ) -> bool:
        """
        Link a recording to an incident.

        Args:
            recording_id: Recording identifier
            incident_id: Incident identifier
            user_id: User making the link
            notes: Optional notes

        Returns:
            bool: True if linked successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_INCIDENT_RECORDINGS.format(incident_id=incident_id)

            data: dict[str, Any] = {"recordingId": recording_id}
            if user_id:
                data["linkedBy"] = user_id
            if notes:
                data["notes"] = notes

            await self.post(endpoint, data=data)

            audit_logger.log_system_event(
                event_type="bwc_recording_linked",
                details={
                    "recording_id": recording_id,
                    "incident_id": incident_id,
                    "user_id": user_id,
                },
            )

            logger.info(
                "bwc_recording_linked_to_incident",
                recording_id=recording_id,
                incident_id=incident_id,
            )

            return True

        except Exception as e:
            logger.error(
                "bwc_link_to_incident_failed",
                recording_id=recording_id,
                incident_id=incident_id,
                error=str(e),
            )
            return False

    async def add_tags(
        self,
        recording_id: str,
        tags: list[str],
        user_id: str | None = None,
    ) -> bool:
        """
        Add tags to a recording.

        Args:
            recording_id: Recording identifier
            tags: Tags to add
            user_id: User adding tags

        Returns:
            bool: True if tags added successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_TAGS.format(recording_id=recording_id)

            data: dict[str, Any] = {"tags": tags}
            if user_id:
                data["addedBy"] = user_id

            await self.post(endpoint, data=data)

            logger.info("bwc_tags_added", recording_id=recording_id, tags=tags)

            return True

        except Exception as e:
            logger.error("bwc_add_tags_failed", recording_id=recording_id, error=str(e))
            return False

    async def get_incident_recordings(self, incident_id: str) -> list[dict[str, Any]]:
        """
        Get all recordings linked to an incident.

        Args:
            incident_id: Incident identifier

        Returns:
            list: Recordings linked to the incident
        """
        if not self.is_connected:
            return []

        try:
            endpoint = self.ENDPOINT_INCIDENT_RECORDINGS.format(incident_id=incident_id)
            response = await self.get(endpoint)
            return response.get("recordings", [])

        except Exception as e:
            logger.error(
                "bwc_get_incident_recordings_failed", incident_id=incident_id, error=str(e)
            )
            return []

    async def create_evidence_package(
        self,
        recording_ids: list[str],
        case_number: str,
        description: str,
        user_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Create an evidence package from recordings.

        Args:
            recording_ids: List of recording IDs to include
            case_number: Associated case number
            description: Package description
            user_id: User creating the package

        Returns:
            dict | None: Evidence package info
        """
        if not self.is_connected:
            return None

        try:
            data: dict[str, Any] = {
                "recordingIds": recording_ids,
                "caseNumber": case_number,
                "description": description,
            }

            if user_id:
                data["createdBy"] = user_id

            response = await self.post(self.ENDPOINT_EVIDENCE, data=data)

            audit_logger.log_system_event(
                event_type="bwc_evidence_package_created",
                details={
                    "package_id": response.get("id"),
                    "case_number": case_number,
                    "recording_count": len(recording_ids),
                    "user_id": user_id,
                },
            )

            logger.info(
                "bwc_evidence_package_created",
                case_number=case_number,
                recording_count=len(recording_ids),
            )

            return response

        except Exception as e:
            logger.error("bwc_create_evidence_package_failed", error=str(e))
            return None

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from BWC system.

        Args:
            payload: Raw webhook payload
            signature: Signature from X-BWC-Signature header

        Returns:
            bool: True if signature is valid
        """
        if not self._webhook_secret:
            logger.warning("bwc_webhook_secret_not_configured")
            return True

        expected = hmac.new(
            self._webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def process_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming webhook from BWC system.

        Args:
            payload: Webhook payload

        Returns:
            dict: Processed event data ready for ingestion
        """
        event_type = payload.get("eventType", payload.get("type", "recording_event"))
        recording = payload.get("recording", payload)
        officer = recording.get("officer", {})
        device = recording.get("device", {})
        location = recording.get("location", {})

        processed: dict[str, Any] = {
            "source": "bwc",
            "event_type": event_type,
            "timestamp": payload.get("timestamp", datetime.now(UTC).isoformat()),
            "recordingId": recording.get("id", recording.get("recordingId")),
            "officerId": officer.get("id", recording.get("officerId")),
            "officerName": officer.get("name", recording.get("officerName")),
            "officerBadge": officer.get("badgeNumber"),
            "deviceId": device.get("id", recording.get("deviceId")),
            "deviceSerial": device.get("serialNumber"),
            "status": recording.get("status"),
            "startTime": recording.get("startTime"),
            "endTime": recording.get("endTime"),
            "duration": recording.get("duration"),
            "latitude": location.get("latitude", recording.get("latitude")),
            "longitude": location.get("longitude", recording.get("longitude")),
            "category": recording.get("category"),
            "tags": recording.get("tags", []),
            "incidentId": recording.get("incidentId"),
            "triggerType": recording.get("triggerType"),
        }

        logger.debug(
            "bwc_webhook_processed",
            event_type=event_type,
            recording_id=processed.get("recordingId"),
        )

        return processed


_bwc_integration: BWCIntegration | None = None


def get_bwc_integration() -> BWCIntegration:
    """Get the BWC integration instance."""
    global _bwc_integration
    if _bwc_integration is None:
        _bwc_integration = BWCIntegration()
    return _bwc_integration
