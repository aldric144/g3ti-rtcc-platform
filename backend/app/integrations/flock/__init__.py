"""
Flock Safety LPR integration for the G3TI RTCC-UIP Backend.

Flock Safety provides License Plate Recognition (LPR) services:
- Automatic license plate capture
- Vehicle identification
- Hotlist matching
- Alert notifications
- Historical search

This integration enables:
- Real-time LPR alerts via webhook
- Vehicle search by plate, make, model, color
- Hotlist management (add/remove plates)
- Camera network monitoring
- Historical plate sighting queries
"""

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.logging import audit_logger, get_logger
from app.integrations.base import BaseIntegration
from app.schemas.events import EventSource, FlockLPREvent

logger = get_logger(__name__)


class FlockIntegration(BaseIntegration[FlockLPREvent]):
    """
    Flock Safety LPR integration client.

    Provides methods for interacting with Flock Safety including
    LPR alerts, vehicle search, and hotlist management.

    API Documentation: https://api.flocksafety.com/docs
    """

    ENDPOINT_HEALTH = "/v1/health"
    ENDPOINT_PLATES = "/v2/plates"
    ENDPOINT_PLATE_READS = "/v2/plate-reads"
    ENDPOINT_HOTLISTS = "/v2/hotlists"
    ENDPOINT_HOTLIST_PLATES = "/v2/hotlists/{hotlist_id}/plates"
    ENDPOINT_CAMERAS = "/v2/cameras"
    ENDPOINT_ALERTS = "/v2/alerts"
    ENDPOINT_SEARCH = "/v2/search"

    def __init__(self) -> None:
        """Initialize Flock integration."""
        super().__init__(
            base_url=settings.flock_api_url,
            api_key=settings.flock_api_key,
            timeout=30.0,
        )
        self._agency_id = getattr(settings, "flock_agency_id", None)
        self._webhook_secret = getattr(settings, "flock_webhook_secret", None)

    @property
    def source(self) -> EventSource:
        """Get the event source."""
        return EventSource.FLOCK

    def _get_auth_headers(self) -> dict[str, str]:
        """Get Flock-specific authentication headers."""
        headers = super()._get_auth_headers()
        if self._api_key:
            headers["X-API-Key"] = self._api_key
            headers.pop("Authorization", None)
        if self._agency_id:
            headers["X-Agency-ID"] = self._agency_id
        return headers

    async def health_check(self) -> bool:
        """
        Verify connectivity to Flock Safety.

        Returns:
            bool: True if Flock is reachable and responding
        """
        if not self.is_configured:
            return False

        try:
            response = await self.get(self.ENDPOINT_HEALTH)
            return response.get("status") == "healthy"
        except Exception as e:
            logger.warning("flock_health_check_failed", error=str(e))
            return False

    async def normalize_event(self, raw_data: dict[str, Any]) -> FlockLPREvent:
        """
        Normalize Flock event to standard format.

        Args:
            raw_data: Raw event data from Flock webhook or API

        Returns:
            FlockLPREvent: Normalized LPR event
        """
        plate_data = raw_data.get("plate", raw_data)
        vehicle_data = raw_data.get("vehicle", {})

        return FlockLPREvent(
            plate_number=plate_data.get("plateNumber", plate_data.get("plate", "")),
            plate_state=plate_data.get("plateState", plate_data.get("state")),
            vehicle_make=vehicle_data.get("make", raw_data.get("vehicleMake")),
            vehicle_model=vehicle_data.get("model", raw_data.get("vehicleModel")),
            vehicle_color=vehicle_data.get("color", raw_data.get("vehicleColor")),
            camera_id=raw_data.get("cameraId", raw_data.get("deviceId", "")),
            image_url=raw_data.get("imageUrl", raw_data.get("plateImageUrl")),
            alert_type=raw_data.get("alertType", raw_data.get("type")),
            hotlist_name=raw_data.get("hotlistName", raw_data.get("listName")),
        )

    async def search_plate(
        self,
        plate_number: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search for license plate sightings.

        Args:
            plate_number: License plate to search (supports wildcards)
            start_date: Start date for search range
            end_date: End date for search range
            limit: Maximum results to return

        Returns:
            list: Plate sightings with location and timestamp
        """
        if not self.is_connected:
            logger.warning("flock_not_connected_for_search")
            return []

        try:
            if not end_date:
                end_date = datetime.now(UTC)
            if not start_date:
                start_date = end_date - timedelta(days=30)

            params = {
                "plate": plate_number.upper(),
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "limit": limit,
            }

            response = await self.get(self.ENDPOINT_SEARCH, params=params)
            results = response.get("results", response.get("reads", []))

            logger.info(
                "flock_plate_search_complete",
                plate=plate_number,
                results_count=len(results),
            )

            audit_logger.log_system_event(
                event_type="flock_plate_search",
                details={"plate_number": plate_number, "results_count": len(results)},
            )

            return results

        except Exception as e:
            logger.error("flock_plate_search_failed", plate=plate_number, error=str(e))
            return []

    async def search_vehicle(
        self,
        make: str | None = None,
        model: str | None = None,
        color: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search for vehicles by attributes.

        Args:
            make: Vehicle make (e.g., "Honda", "Ford")
            model: Vehicle model (e.g., "Civic", "F-150")
            color: Vehicle color (e.g., "Black", "White")
            start_date: Start date for search range
            end_date: End date for search range
            limit: Maximum results to return

        Returns:
            list: Matching vehicle sightings
        """
        if not self.is_connected:
            return []

        try:
            if not end_date:
                end_date = datetime.now(UTC)
            if not start_date:
                start_date = end_date - timedelta(days=30)

            params = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "limit": limit,
            }

            if make:
                params["make"] = make
            if model:
                params["model"] = model
            if color:
                params["color"] = color

            response = await self.get(self.ENDPOINT_SEARCH, params=params)
            return response.get("results", [])

        except Exception as e:
            logger.error("flock_vehicle_search_failed", error=str(e))
            return []

    async def get_plate_reads(
        self,
        camera_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get recent plate reads, optionally filtered by camera.

        Args:
            camera_id: Filter by specific camera
            start_date: Start date for range
            end_date: End date for range
            limit: Maximum results

        Returns:
            list: Recent plate reads
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {"limit": limit}

            if camera_id:
                params["cameraId"] = camera_id
            if start_date:
                params["startDate"] = start_date.isoformat()
            if end_date:
                params["endDate"] = end_date.isoformat()

            response = await self.get(self.ENDPOINT_PLATE_READS, params=params)
            return response.get("reads", response.get("results", []))

        except Exception as e:
            logger.error("flock_get_plate_reads_failed", error=str(e))
            return []

    async def get_hotlists(self) -> list[dict[str, Any]]:
        """
        Get all configured hotlists.

        Returns:
            list: Hotlist information including ID, name, and plate count
        """
        if not self.is_connected:
            return []

        try:
            response = await self.get(self.ENDPOINT_HOTLISTS)
            return response.get("hotlists", response.get("lists", []))

        except Exception as e:
            logger.error("flock_get_hotlists_failed", error=str(e))
            return []

    async def get_hotlist_plates(self, hotlist_id: str) -> list[dict[str, Any]]:
        """
        Get all plates in a specific hotlist.

        Args:
            hotlist_id: Hotlist identifier

        Returns:
            list: Plates in the hotlist
        """
        if not self.is_connected:
            return []

        try:
            endpoint = self.ENDPOINT_HOTLIST_PLATES.format(hotlist_id=hotlist_id)
            response = await self.get(endpoint)
            return response.get("plates", [])

        except Exception as e:
            logger.error("flock_get_hotlist_plates_failed", hotlist_id=hotlist_id, error=str(e))
            return []

    async def add_to_hotlist(
        self,
        hotlist_id: str,
        plate_number: str,
        reason: str,
        plate_state: str | None = None,
        expiration_date: datetime | None = None,
        notes: str | None = None,
    ) -> bool:
        """
        Add a plate to a hotlist.

        Args:
            hotlist_id: Hotlist identifier
            plate_number: Plate to add
            reason: Reason for adding (e.g., "Stolen Vehicle", "BOLO")
            plate_state: State of the plate
            expiration_date: When the entry should expire
            notes: Additional notes

        Returns:
            bool: True if added successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_HOTLIST_PLATES.format(hotlist_id=hotlist_id)

            data: dict[str, Any] = {
                "plateNumber": plate_number.upper(),
                "reason": reason,
            }

            if plate_state:
                data["plateState"] = plate_state.upper()
            if expiration_date:
                data["expirationDate"] = expiration_date.isoformat()
            if notes:
                data["notes"] = notes

            await self.post(endpoint, data=data)

            logger.info(
                "flock_plate_added_to_hotlist",
                hotlist_id=hotlist_id,
                plate=plate_number,
                reason=reason,
            )

            audit_logger.log_system_event(
                event_type="flock_hotlist_add",
                details={"hotlist_id": hotlist_id, "plate_number": plate_number, "reason": reason},
            )

            return True

        except Exception as e:
            logger.error(
                "flock_add_to_hotlist_failed",
                hotlist_id=hotlist_id,
                plate=plate_number,
                error=str(e),
            )
            return False

    async def remove_from_hotlist(self, hotlist_id: str, plate_number: str) -> bool:
        """
        Remove a plate from a hotlist.

        Args:
            hotlist_id: Hotlist identifier
            plate_number: Plate to remove

        Returns:
            bool: True if removed successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = f"{self.ENDPOINT_HOTLIST_PLATES.format(hotlist_id=hotlist_id)}/{plate_number.upper()}"
            await self._request("DELETE", endpoint)

            logger.info(
                "flock_plate_removed_from_hotlist",
                hotlist_id=hotlist_id,
                plate=plate_number,
            )

            audit_logger.log_system_event(
                event_type="flock_hotlist_remove",
                details={"hotlist_id": hotlist_id, "plate_number": plate_number},
            )

            return True

        except Exception as e:
            logger.error(
                "flock_remove_from_hotlist_failed",
                hotlist_id=hotlist_id,
                plate=plate_number,
                error=str(e),
            )
            return False

    async def get_cameras(self) -> list[dict[str, Any]]:
        """
        Get all cameras in the network.

        Returns:
            list: Camera information including ID, name, location, status
        """
        if not self.is_connected:
            return []

        try:
            response = await self.get(self.ENDPOINT_CAMERAS)
            return response.get("cameras", response.get("devices", []))

        except Exception as e:
            logger.error("flock_get_cameras_failed", error=str(e))
            return []

    async def get_camera_status(self, camera_id: str) -> dict[str, Any] | None:
        """
        Get status of a specific camera.

        Args:
            camera_id: Camera identifier

        Returns:
            dict | None: Camera status or None if not found
        """
        if not self.is_connected:
            return None

        try:
            response = await self.get(f"{self.ENDPOINT_CAMERAS}/{camera_id}")
            return response

        except Exception as e:
            logger.error("flock_get_camera_status_failed", camera_id=camera_id, error=str(e))
            return None

    async def get_recent_alerts(
        self,
        limit: int = 50,
        acknowledged: bool | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get recent alerts from Flock.

        Args:
            limit: Maximum alerts to return
            acknowledged: Filter by acknowledgment status

        Returns:
            list: Recent alerts
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {"limit": limit}
            if acknowledged is not None:
                params["acknowledged"] = str(acknowledged).lower()

            response = await self.get(self.ENDPOINT_ALERTS, params=params)
            return response.get("alerts", [])

        except Exception as e:
            logger.error("flock_get_alerts_failed", error=str(e))
            return []

    async def acknowledge_alert(self, alert_id: str, notes: str | None = None) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert identifier
            notes: Optional acknowledgment notes

        Returns:
            bool: True if acknowledged successfully
        """
        if not self.is_connected:
            return False

        try:
            data: dict[str, Any] = {"acknowledged": True}
            if notes:
                data["notes"] = notes

            await self.post(f"{self.ENDPOINT_ALERTS}/{alert_id}/acknowledge", data=data)
            logger.info("flock_alert_acknowledged", alert_id=alert_id)
            return True

        except Exception as e:
            logger.error("flock_acknowledge_alert_failed", alert_id=alert_id, error=str(e))
            return False

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Flock.

        Args:
            payload: Raw webhook payload
            signature: Signature from X-Flock-Signature header

        Returns:
            bool: True if signature is valid
        """
        if not self._webhook_secret:
            logger.warning("flock_webhook_secret_not_configured")
            return True

        expected = hmac.new(
            self._webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def process_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming webhook from Flock.

        Args:
            payload: Webhook payload

        Returns:
            dict: Processed event data ready for ingestion
        """
        event_type = payload.get("eventType", payload.get("type", "plate_read"))

        processed: dict[str, Any] = {
            "source": "flock",
            "event_type": event_type,
            "timestamp": payload.get("timestamp", datetime.now(UTC).isoformat()),
            "plateNumber": payload.get("plateNumber", payload.get("plate", {}).get("number")),
            "plateState": payload.get("plateState", payload.get("plate", {}).get("state")),
            "latitude": payload.get("latitude", payload.get("location", {}).get("lat")),
            "longitude": payload.get("longitude", payload.get("location", {}).get("lng")),
            "address": payload.get("address", payload.get("location", {}).get("address")),
            "cameraId": payload.get("cameraId", payload.get("deviceId")),
            "cameraName": payload.get("cameraName", payload.get("deviceName")),
            "imageUrl": payload.get("imageUrl", payload.get("plateImageUrl")),
            "contextImageUrl": payload.get("contextImageUrl"),
        }

        vehicle = payload.get("vehicle", {})
        processed["vehicleMake"] = vehicle.get("make", payload.get("vehicleMake"))
        processed["vehicleModel"] = vehicle.get("model", payload.get("vehicleModel"))
        processed["vehicleColor"] = vehicle.get("color", payload.get("vehicleColor"))
        processed["vehicleYear"] = vehicle.get("year", payload.get("vehicleYear"))

        if event_type in ["alert", "hotlist_hit"]:
            processed["alertType"] = payload.get("alertType", "hotlist")
            processed["hotlistMatch"] = True
            processed["hotlistName"] = payload.get("hotlistName", payload.get("listName"))
            processed["hotlistReason"] = payload.get("reason")

        logger.debug("flock_webhook_processed", event_type=event_type)

        return processed


_flock_integration: FlockIntegration | None = None


def get_flock_integration() -> FlockIntegration:
    """Get the Flock integration instance."""
    global _flock_integration
    if _flock_integration is None:
        _flock_integration = FlockIntegration()
    return _flock_integration
