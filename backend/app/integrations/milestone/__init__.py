"""
Milestone VMS integration for the G3TI RTCC-UIP Backend.

Milestone XProtect is a Video Management System (VMS) that provides:
- Live video streaming
- Video recording and playback
- Camera management
- Motion detection and analytics
- Event notifications

This integration enables:
- Camera status monitoring and management
- Live video streaming URLs
- Video clip retrieval and export
- Alert notifications via webhook
- PTZ camera control
- Analytics event processing
"""

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.logging import audit_logger, get_logger
from app.integrations.base import BaseIntegration
from app.schemas.events import CameraAlertEvent, EventSource

logger = get_logger(__name__)


class MilestoneIntegration(BaseIntegration[CameraAlertEvent]):
    """
    Milestone XProtect VMS integration client.

    Provides methods for interacting with Milestone VMS including
    camera management, video retrieval, and event handling.

    API Documentation: https://doc.milestonesys.com/mipsdkmobile/
    """

    ENDPOINT_HEALTH = "/api/rest/v1/health"
    ENDPOINT_CAMERAS = "/api/rest/v1/cameras"
    ENDPOINT_CAMERA_DETAIL = "/api/rest/v1/cameras/{camera_id}"
    ENDPOINT_CAMERA_STATUS = "/api/rest/v1/cameras/{camera_id}/status"
    ENDPOINT_LIVE_STREAM = "/api/rest/v1/cameras/{camera_id}/live"
    ENDPOINT_SNAPSHOT = "/api/rest/v1/cameras/{camera_id}/snapshot"
    ENDPOINT_VIDEO_EXPORT = "/api/rest/v1/cameras/{camera_id}/export"
    ENDPOINT_PTZ = "/api/rest/v1/cameras/{camera_id}/ptz"
    ENDPOINT_EVENTS = "/api/rest/v1/events"
    ENDPOINT_ANALYTICS = "/api/rest/v1/analytics"
    ENDPOINT_BOOKMARKS = "/api/rest/v1/bookmarks"
    ENDPOINT_RECORDINGS = "/api/rest/v1/cameras/{camera_id}/recordings"

    def __init__(self) -> None:
        """Initialize Milestone integration."""
        super().__init__(
            base_url=settings.milestone_api_url,
            api_key=settings.milestone_api_key,
            timeout=30.0,
        )
        self._server_id = getattr(settings, "milestone_server_id", None)
        self._webhook_secret = getattr(settings, "milestone_webhook_secret", None)

    @property
    def source(self) -> EventSource:
        """Get the event source."""
        return EventSource.MILESTONE

    def _get_auth_headers(self) -> dict[str, str]:
        """Get Milestone-specific authentication headers."""
        headers = super()._get_auth_headers()
        if self._api_key:
            headers["X-Milestone-API-Key"] = self._api_key
        if self._server_id:
            headers["X-Server-ID"] = self._server_id
        return headers

    async def health_check(self) -> bool:
        """
        Verify connectivity to Milestone VMS.

        Returns:
            bool: True if Milestone is reachable and responding
        """
        if not self.is_configured:
            return False

        try:
            response = await self.get(self.ENDPOINT_HEALTH)
            return response.get("status") in ["healthy", "ok", "connected"]
        except Exception as e:
            logger.warning("milestone_health_check_failed", error=str(e))
            return False

    async def normalize_event(self, raw_data: dict[str, Any]) -> CameraAlertEvent:
        """
        Normalize Milestone event to standard format.

        Args:
            raw_data: Raw event data from Milestone webhook or API

        Returns:
            CameraAlertEvent: Normalized camera alert
        """
        camera = raw_data.get("camera", {})
        analytics = raw_data.get("analytics", {})

        return CameraAlertEvent(
            camera_id=camera.get("id", raw_data.get("cameraId", "")),
            camera_name=camera.get("name", raw_data.get("cameraName", "Unknown Camera")),
            alert_type=raw_data.get("eventType", raw_data.get("type", "motion")),
            confidence=analytics.get("confidence", raw_data.get("confidence")),
            snapshot_url=raw_data.get("snapshotUrl", raw_data.get("imageUrl")),
            video_clip_url=raw_data.get("videoClipUrl", raw_data.get("clipUrl")),
            detected_objects=analytics.get("objects", raw_data.get("detectedObjects", [])),
        )

    async def get_cameras(
        self,
        status: str | None = None,
        group_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get list of cameras from Milestone.

        Args:
            status: Filter by status (online, offline, recording)
            group_id: Filter by camera group

        Returns:
            list: Camera information including ID, name, location, status
        """
        if not self.is_connected:
            logger.warning("milestone_not_connected_for_cameras")
            return []

        try:
            params: dict[str, Any] = {}
            if status:
                params["status"] = status
            if group_id:
                params["groupId"] = group_id

            response = await self.get(self.ENDPOINT_CAMERAS, params=params)
            cameras = response.get("cameras", response.get("items", []))

            logger.info("milestone_cameras_retrieved", count=len(cameras))

            return cameras

        except Exception as e:
            logger.error("milestone_get_cameras_failed", error=str(e))
            return []

    async def get_camera_detail(self, camera_id: str) -> dict[str, Any] | None:
        """
        Get detailed information for a specific camera.

        Args:
            camera_id: Camera identifier

        Returns:
            dict | None: Camera details including capabilities
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_CAMERA_DETAIL.format(camera_id=camera_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("milestone_get_camera_detail_failed", camera_id=camera_id, error=str(e))
            return None

    async def get_camera_status(self, camera_id: str) -> dict[str, Any] | None:
        """
        Get current status of a specific camera.

        Args:
            camera_id: Camera identifier

        Returns:
            dict | None: Camera status including recording state, connectivity
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_CAMERA_STATUS.format(camera_id=camera_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("milestone_get_camera_status_failed", camera_id=camera_id, error=str(e))
            return None

    async def get_live_stream_url(
        self,
        camera_id: str,
        stream_type: str = "main",
        protocol: str = "rtsp",
    ) -> dict[str, Any] | None:
        """
        Get live stream URL for a camera.

        Args:
            camera_id: Camera identifier
            stream_type: Stream type (main, sub)
            protocol: Streaming protocol (rtsp, hls, webrtc)

        Returns:
            dict | None: Stream URL and connection info
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_LIVE_STREAM.format(camera_id=camera_id)
            params = {"streamType": stream_type, "protocol": protocol}

            response = await self.get(endpoint, params=params)

            logger.debug("milestone_live_stream_url_retrieved", camera_id=camera_id)

            return response

        except Exception as e:
            logger.error("milestone_get_live_stream_failed", camera_id=camera_id, error=str(e))
            return None

    async def get_snapshot(
        self,
        camera_id: str,
        timestamp: datetime | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> dict[str, Any] | None:
        """
        Get snapshot from camera.

        Args:
            camera_id: Camera identifier
            timestamp: Specific timestamp (None for current)
            width: Image width
            height: Image height

        Returns:
            dict | None: Snapshot URL and metadata
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_SNAPSHOT.format(camera_id=camera_id)
            params: dict[str, Any] = {}

            if timestamp:
                params["timestamp"] = timestamp.isoformat()
            if width:
                params["width"] = width
            if height:
                params["height"] = height

            response = await self.get(endpoint, params=params)

            logger.debug("milestone_snapshot_retrieved", camera_id=camera_id)

            return response

        except Exception as e:
            logger.error("milestone_get_snapshot_failed", camera_id=camera_id, error=str(e))
            return None

    async def export_video_clip(
        self,
        camera_id: str,
        start_time: datetime,
        end_time: datetime,
        format: str = "mp4",
    ) -> dict[str, Any] | None:
        """
        Export video clip for a time range.

        Args:
            camera_id: Camera identifier
            start_time: Start time
            end_time: End time
            format: Export format (mp4, avi, mkv)

        Returns:
            dict | None: Export job info including download URL when ready
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_VIDEO_EXPORT.format(camera_id=camera_id)

            data = {
                "startTime": start_time.isoformat(),
                "endTime": end_time.isoformat(),
                "format": format,
            }

            response = await self.post(endpoint, data=data)

            logger.info(
                "milestone_video_export_started",
                camera_id=camera_id,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
            )

            audit_logger.log_system_event(
                event_type="milestone_video_export",
                details={
                    "camera_id": camera_id,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                },
            )

            return response

        except Exception as e:
            logger.error("milestone_export_video_failed", camera_id=camera_id, error=str(e))
            return None

    async def get_recordings(
        self,
        camera_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get recording segments for a camera.

        Args:
            camera_id: Camera identifier
            start_time: Start of time range
            end_time: End of time range

        Returns:
            list: Recording segments with timestamps
        """
        if not self.is_connected:
            return []

        try:
            endpoint = self.ENDPOINT_RECORDINGS.format(camera_id=camera_id)
            params: dict[str, Any] = {}

            if start_time:
                params["startTime"] = start_time.isoformat()
            if end_time:
                params["endTime"] = end_time.isoformat()

            response = await self.get(endpoint, params=params)
            return response.get("recordings", response.get("segments", []))

        except Exception as e:
            logger.error("milestone_get_recordings_failed", camera_id=camera_id, error=str(e))
            return []

    async def ptz_control(
        self,
        camera_id: str,
        action: str,
        pan: float | None = None,
        tilt: float | None = None,
        zoom: float | None = None,
        preset: str | None = None,
    ) -> bool:
        """
        Control PTZ camera.

        Args:
            camera_id: Camera identifier
            action: PTZ action (move, stop, goto_preset, home)
            pan: Pan value (-1.0 to 1.0)
            tilt: Tilt value (-1.0 to 1.0)
            zoom: Zoom value (-1.0 to 1.0)
            preset: Preset name for goto_preset action

        Returns:
            bool: True if command sent successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_PTZ.format(camera_id=camera_id)

            data: dict[str, Any] = {"action": action}

            if pan is not None:
                data["pan"] = pan
            if tilt is not None:
                data["tilt"] = tilt
            if zoom is not None:
                data["zoom"] = zoom
            if preset:
                data["preset"] = preset

            await self.post(endpoint, data=data)

            logger.info("milestone_ptz_command_sent", camera_id=camera_id, action=action)

            audit_logger.log_system_event(
                event_type="milestone_ptz_control",
                details={"camera_id": camera_id, "action": action},
            )

            return True

        except Exception as e:
            logger.error("milestone_ptz_control_failed", camera_id=camera_id, error=str(e))
            return False

    async def get_recent_events(
        self,
        hours: int = 24,
        event_types: list[str] | None = None,
        camera_ids: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get recent events from Milestone.

        Args:
            hours: Hours to look back
            event_types: Filter by event types
            camera_ids: Filter by camera IDs
            limit: Maximum events to return

        Returns:
            list: Recent events
        """
        if not self.is_connected:
            return []

        try:
            end_time = datetime.now(UTC)
            start_time = end_time - timedelta(hours=hours)

            params: dict[str, Any] = {
                "startTime": start_time.isoformat(),
                "endTime": end_time.isoformat(),
                "limit": limit,
            }

            if event_types:
                params["eventTypes"] = ",".join(event_types)
            if camera_ids:
                params["cameraIds"] = ",".join(camera_ids)

            response = await self.get(self.ENDPOINT_EVENTS, params=params)
            return response.get("events", [])

        except Exception as e:
            logger.error("milestone_get_events_failed", error=str(e))
            return []

    async def get_analytics_events(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        analytics_types: list[str] | None = None,
        camera_ids: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get analytics events (object detection, motion, etc.).

        Args:
            start_time: Start of time range
            end_time: End of time range
            analytics_types: Filter by analytics types (motion, object, face, etc.)
            camera_ids: Filter by camera IDs
            limit: Maximum events

        Returns:
            list: Analytics events
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {"limit": limit}

            if start_time:
                params["startTime"] = start_time.isoformat()
            if end_time:
                params["endTime"] = end_time.isoformat()
            if analytics_types:
                params["types"] = ",".join(analytics_types)
            if camera_ids:
                params["cameraIds"] = ",".join(camera_ids)

            response = await self.get(self.ENDPOINT_ANALYTICS, params=params)
            return response.get("events", response.get("analytics", []))

        except Exception as e:
            logger.error("milestone_get_analytics_failed", error=str(e))
            return []

    async def create_bookmark(
        self,
        camera_id: str,
        timestamp: datetime,
        description: str,
        user_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Create a bookmark for a specific time on a camera.

        Args:
            camera_id: Camera identifier
            timestamp: Timestamp to bookmark
            description: Bookmark description
            user_id: User creating the bookmark

        Returns:
            dict | None: Created bookmark info
        """
        if not self.is_connected:
            return None

        try:
            data = {
                "cameraId": camera_id,
                "timestamp": timestamp.isoformat(),
                "description": description,
            }

            if user_id:
                data["createdBy"] = user_id

            response = await self.post(self.ENDPOINT_BOOKMARKS, data=data)

            logger.info("milestone_bookmark_created", camera_id=camera_id)

            return response

        except Exception as e:
            logger.error("milestone_create_bookmark_failed", camera_id=camera_id, error=str(e))
            return None

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Milestone.

        Args:
            payload: Raw webhook payload
            signature: Signature from X-Milestone-Signature header

        Returns:
            bool: True if signature is valid
        """
        if not self._webhook_secret:
            logger.warning("milestone_webhook_secret_not_configured")
            return True

        expected = hmac.new(
            self._webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def process_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming webhook from Milestone.

        Args:
            payload: Webhook payload

        Returns:
            dict: Processed event data ready for ingestion
        """
        event = payload.get("event", payload)
        camera = event.get("camera", {})
        location = camera.get("location", {})
        analytics = event.get("analytics", {})

        processed: dict[str, Any] = {
            "source": "milestone",
            "id": event.get("id", event.get("eventId")),
            "timestamp": event.get("timestamp", event.get("eventTime")),
            "eventType": event.get("eventType", event.get("type", "motion")),
            "cameraId": camera.get("id", event.get("cameraId")),
            "cameraName": camera.get("name", event.get("cameraName")),
            "latitude": location.get("latitude", event.get("latitude")),
            "longitude": location.get("longitude", event.get("longitude")),
            "address": location.get("address", event.get("address")),
            "snapshotUrl": event.get("snapshotUrl", event.get("imageUrl")),
            "videoClipUrl": event.get("videoClipUrl", event.get("clipUrl")),
            "confidence": analytics.get("confidence", event.get("confidence")),
            "detectedObjects": analytics.get("objects", event.get("detectedObjects", [])),
            "ruleName": event.get("ruleName"),
            "zoneName": event.get("zoneName"),
        }

        logger.debug(
            "milestone_webhook_processed",
            event_id=processed.get("id"),
            event_type=processed.get("eventType"),
        )

        return processed


_milestone_integration: MilestoneIntegration | None = None


def get_milestone_integration() -> MilestoneIntegration:
    """Get the Milestone integration instance."""
    global _milestone_integration
    if _milestone_integration is None:
        _milestone_integration = MilestoneIntegration()
    return _milestone_integration
