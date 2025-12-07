"""
HotSheets integration for the G3TI RTCC-UIP Backend.

HotSheets provides BOLO (Be On the Lookout) and wanted lists:
- Stolen vehicles
- Wanted persons
- Missing persons
- Amber alerts
- Custom BOLOs
- Officer safety alerts

This integration enables:
- BOLO list management and distribution
- Real-time alert notifications via webhook
- Plate and person matching
- List synchronization across agencies
- Alert acknowledgment and tracking
"""

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.logging import audit_logger, get_logger
from app.integrations.base import BaseIntegration
from app.schemas.events import EventSource

logger = get_logger(__name__)


class HotSheetsIntegration(BaseIntegration[dict[str, Any]]):
    """
    HotSheets BOLO integration client.

    Provides methods for managing BOLO lists including
    creation, distribution, and match notifications.

    Supports integration with regional and national BOLO systems.
    """

    ENDPOINT_HEALTH = "/api/v1/health"
    ENDPOINT_BOLOS = "/api/v1/bolos"
    ENDPOINT_BOLO_DETAIL = "/api/v1/bolos/{bolo_id}"
    ENDPOINT_BOLO_CANCEL = "/api/v1/bolos/{bolo_id}/cancel"
    ENDPOINT_BOLO_EXTEND = "/api/v1/bolos/{bolo_id}/extend"
    ENDPOINT_VEHICLES = "/api/v1/vehicles"
    ENDPOINT_VEHICLE_CHECK = "/api/v1/vehicles/check"
    ENDPOINT_PERSONS = "/api/v1/persons"
    ENDPOINT_PERSON_CHECK = "/api/v1/persons/check"
    ENDPOINT_ALERTS = "/api/v1/alerts"
    ENDPOINT_ALERT_ACKNOWLEDGE = "/api/v1/alerts/{alert_id}/acknowledge"
    ENDPOINT_LISTS = "/api/v1/lists"
    ENDPOINT_LIST_ENTRIES = "/api/v1/lists/{list_id}/entries"
    ENDPOINT_SYNC = "/api/v1/sync"

    def __init__(self) -> None:
        """Initialize HotSheets integration."""
        super().__init__(
            base_url=settings.hotsheets_api_url,
            api_key=settings.hotsheets_api_key,
            timeout=30.0,
        )
        self._agency_id = getattr(settings, "hotsheets_agency_id", None)
        self._agency_ori = getattr(settings, "hotsheets_agency_ori", None)
        self._webhook_secret = getattr(settings, "hotsheets_webhook_secret", None)

    @property
    def source(self) -> EventSource:
        """Get the event source."""
        return EventSource.HOTSHEETS

    def _get_auth_headers(self) -> dict[str, str]:
        """Get HotSheets-specific authentication headers."""
        headers = super()._get_auth_headers()
        if self._api_key:
            headers["X-HotSheets-API-Key"] = self._api_key
        if self._agency_id:
            headers["X-Agency-ID"] = self._agency_id
        if self._agency_ori:
            headers["X-Agency-ORI"] = self._agency_ori
        return headers

    async def health_check(self) -> bool:
        """
        Verify connectivity to HotSheets.

        Returns:
            bool: True if HotSheets is reachable and responding
        """
        if not self.is_configured:
            return False

        try:
            response = await self.get(self.ENDPOINT_HEALTH)
            return response.get("status") in ["healthy", "ok", "connected"]
        except Exception as e:
            logger.warning("hotsheets_health_check_failed", error=str(e))
            return False

    async def normalize_event(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize HotSheets event data.

        Args:
            raw_data: Raw data from HotSheets

        Returns:
            dict: Normalized data with standard fields
        """
        bolo = raw_data.get("bolo", raw_data)
        subject = bolo.get("subject", {})

        normalized = {
            "source": "hotsheets",
            "bolo_id": bolo.get("id", bolo.get("boloId")),
            "bolo_type": bolo.get("type", bolo.get("boloType")),
            "timestamp": bolo.get("timestamp", bolo.get("createdAt")),
            "status": bolo.get("status"),
            "priority": bolo.get("priority"),
            "description": bolo.get("description"),
            "reason": bolo.get("reason"),
            "expiration": bolo.get("expiration", bolo.get("expiresAt")),
            "originating_agency": bolo.get("originatingAgency"),
            "case_number": bolo.get("caseNumber"),
        }

        if bolo.get("type") == "vehicle" or "plateNumber" in subject:
            normalized["plate_number"] = subject.get("plateNumber")
            normalized["plate_state"] = subject.get("plateState")
            normalized["vehicle_make"] = subject.get("make")
            normalized["vehicle_model"] = subject.get("model")
            normalized["vehicle_color"] = subject.get("color")
            normalized["vehicle_year"] = subject.get("year")
            normalized["vin"] = subject.get("vin")

        if bolo.get("type") == "person" or "firstName" in subject:
            normalized["first_name"] = subject.get("firstName")
            normalized["last_name"] = subject.get("lastName")
            normalized["dob"] = subject.get("dateOfBirth")
            normalized["gender"] = subject.get("gender")
            normalized["race"] = subject.get("race")
            normalized["height"] = subject.get("height")
            normalized["weight"] = subject.get("weight")
            normalized["hair_color"] = subject.get("hairColor")
            normalized["eye_color"] = subject.get("eyeColor")

        return normalized

    async def get_active_bolos(
        self,
        bolo_type: str | None = None,
        priority: str | None = None,
        include_expired: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get active BOLO entries.

        Args:
            bolo_type: Filter by type (vehicle, person, property)
            priority: Filter by priority (critical, high, medium, low)
            include_expired: Include recently expired BOLOs
            limit: Maximum results

        Returns:
            list: Active BOLOs
        """
        if not self.is_connected:
            logger.warning("hotsheets_not_connected_for_bolos")
            return []

        try:
            params: dict[str, Any] = {
                "status": "active",
                "limit": limit,
            }

            if bolo_type:
                params["type"] = bolo_type
            if priority:
                params["priority"] = priority
            if include_expired:
                params["includeExpired"] = "true"

            response = await self.get(self.ENDPOINT_BOLOS, params=params)
            bolos = response.get("bolos", response.get("items", []))

            logger.info("hotsheets_bolos_retrieved", count=len(bolos))

            return bolos

        except Exception as e:
            logger.error("hotsheets_get_bolos_failed", error=str(e))
            return []

    async def get_bolo_detail(self, bolo_id: str) -> dict[str, Any] | None:
        """
        Get detailed information for a specific BOLO.

        Args:
            bolo_id: BOLO identifier

        Returns:
            dict | None: BOLO details
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_BOLO_DETAIL.format(bolo_id=bolo_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("hotsheets_get_bolo_detail_failed", bolo_id=bolo_id, error=str(e))
            return None

    async def create_bolo(
        self,
        bolo_type: str,
        description: str,
        details: dict[str, Any],
        priority: str = "medium",
        expiration_hours: int = 72,
        case_number: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Create a new BOLO entry.

        Args:
            bolo_type: Type of BOLO (vehicle, person, property)
            description: BOLO description
            details: Subject details (plate, vehicle info, person info, etc.)
            priority: Priority level (critical, high, medium, low)
            expiration_hours: Hours until expiration
            case_number: Associated case number
            user_id: Creating user

        Returns:
            dict | None: Created BOLO
        """
        if not self.is_connected:
            return None

        try:
            expiration = datetime.now(UTC) + timedelta(hours=expiration_hours)

            data: dict[str, Any] = {
                "type": bolo_type,
                "description": description,
                "subject": details,
                "priority": priority,
                "expiresAt": expiration.isoformat(),
                "originatingAgency": self._agency_ori,
            }

            if case_number:
                data["caseNumber"] = case_number
            if user_id:
                data["createdBy"] = user_id

            response = await self.post(self.ENDPOINT_BOLOS, data=data)

            audit_logger.log_system_event(
                event_type="hotsheets_bolo_created",
                details={
                    "bolo_id": response.get("id"),
                    "bolo_type": bolo_type,
                    "priority": priority,
                    "user_id": user_id,
                },
            )

            logger.info(
                "hotsheets_bolo_created",
                bolo_id=response.get("id"),
                bolo_type=bolo_type,
            )

            return response

        except Exception as e:
            logger.error("hotsheets_create_bolo_failed", error=str(e))
            return None

    async def cancel_bolo(
        self,
        bolo_id: str,
        reason: str,
        user_id: str | None = None,
    ) -> bool:
        """
        Cancel an active BOLO.

        Args:
            bolo_id: BOLO identifier
            reason: Cancellation reason
            user_id: Canceling user

        Returns:
            bool: True if canceled successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_BOLO_CANCEL.format(bolo_id=bolo_id)

            data: dict[str, Any] = {"reason": reason}
            if user_id:
                data["canceledBy"] = user_id

            await self.post(endpoint, data=data)

            audit_logger.log_system_event(
                event_type="hotsheets_bolo_canceled",
                details={
                    "bolo_id": bolo_id,
                    "reason": reason,
                    "user_id": user_id,
                },
            )

            logger.info("hotsheets_bolo_canceled", bolo_id=bolo_id, reason=reason)

            return True

        except Exception as e:
            logger.error("hotsheets_cancel_bolo_failed", bolo_id=bolo_id, error=str(e))
            return False

    async def extend_bolo(
        self,
        bolo_id: str,
        hours: int = 24,
        user_id: str | None = None,
    ) -> bool:
        """
        Extend a BOLO's expiration.

        Args:
            bolo_id: BOLO identifier
            hours: Hours to extend
            user_id: User extending

        Returns:
            bool: True if extended successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_BOLO_EXTEND.format(bolo_id=bolo_id)

            data: dict[str, Any] = {"hours": hours}
            if user_id:
                data["extendedBy"] = user_id

            await self.post(endpoint, data=data)

            logger.info("hotsheets_bolo_extended", bolo_id=bolo_id, hours=hours)

            return True

        except Exception as e:
            logger.error("hotsheets_extend_bolo_failed", bolo_id=bolo_id, error=str(e))
            return False

    async def check_plate(
        self,
        plate_number: str,
        plate_state: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Check if a plate is on any hotlist.

        Args:
            plate_number: License plate to check
            plate_state: Plate state (optional)
            user_id: User performing check

        Returns:
            dict: Match results including any matching BOLOs
        """
        if not self.is_connected:
            return {"matches": [], "checked": False, "error": "Not connected"}

        try:
            data: dict[str, Any] = {"plateNumber": plate_number.upper()}

            if plate_state:
                data["plateState"] = plate_state.upper()
            if user_id:
                data["checkedBy"] = user_id

            response = await self.post(self.ENDPOINT_VEHICLE_CHECK, data=data)

            matches = response.get("matches", [])
            has_match = len(matches) > 0

            audit_logger.log_system_event(
                event_type="hotsheets_plate_check",
                details={
                    "plate_number": plate_number,
                    "plate_state": plate_state,
                    "has_match": has_match,
                    "match_count": len(matches),
                    "user_id": user_id,
                },
            )

            logger.info(
                "hotsheets_plate_checked",
                plate=plate_number,
                has_match=has_match,
            )

            return {
                "matches": matches,
                "checked": True,
                "has_match": has_match,
                "check_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("hotsheets_check_plate_failed", plate=plate_number, error=str(e))
            return {"matches": [], "checked": False, "error": str(e)}

    async def check_person(
        self,
        first_name: str,
        last_name: str,
        dob: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Check if a person is on any wanted list.

        Args:
            first_name: Person's first name
            last_name: Person's last name
            dob: Date of birth (YYYY-MM-DD)
            user_id: User performing check

        Returns:
            dict: Match results including any matching BOLOs
        """
        if not self.is_connected:
            return {"matches": [], "checked": False, "error": "Not connected"}

        try:
            data: dict[str, Any] = {
                "firstName": first_name,
                "lastName": last_name,
            }

            if dob:
                data["dateOfBirth"] = dob
            if user_id:
                data["checkedBy"] = user_id

            response = await self.post(self.ENDPOINT_PERSON_CHECK, data=data)

            matches = response.get("matches", [])
            has_match = len(matches) > 0

            audit_logger.log_system_event(
                event_type="hotsheets_person_check",
                details={
                    "first_name": first_name,
                    "last_name": last_name,
                    "has_match": has_match,
                    "match_count": len(matches),
                    "user_id": user_id,
                },
            )

            logger.info(
                "hotsheets_person_checked",
                name=f"{first_name} {last_name}",
                has_match=has_match,
            )

            return {
                "matches": matches,
                "checked": True,
                "has_match": has_match,
                "check_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("hotsheets_check_person_failed", error=str(e))
            return {"matches": [], "checked": False, "error": str(e)}

    async def get_stolen_vehicles(
        self,
        state: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get list of stolen vehicles.

        Args:
            state: Filter by state
            limit: Maximum results

        Returns:
            list: Stolen vehicle entries
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {
                "type": "stolen",
                "limit": limit,
            }

            if state:
                params["state"] = state.upper()

            response = await self.get(self.ENDPOINT_VEHICLES, params=params)
            return response.get("vehicles", [])

        except Exception as e:
            logger.error("hotsheets_get_stolen_vehicles_failed", error=str(e))
            return []

    async def get_wanted_persons(
        self,
        warrant_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get list of wanted persons.

        Args:
            warrant_type: Filter by warrant type (felony, misdemeanor)
            limit: Maximum results

        Returns:
            list: Wanted person entries
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {
                "status": "wanted",
                "limit": limit,
            }

            if warrant_type:
                params["warrantType"] = warrant_type

            response = await self.get(self.ENDPOINT_PERSONS, params=params)
            return response.get("persons", [])

        except Exception as e:
            logger.error("hotsheets_get_wanted_persons_failed", error=str(e))
            return []

    async def get_recent_alerts(
        self,
        hours: int = 24,
        acknowledged: bool | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get recent alerts/matches.

        Args:
            hours: Hours to look back
            acknowledged: Filter by acknowledgment status
            limit: Maximum results

        Returns:
            list: Recent alerts
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

            if acknowledged is not None:
                params["acknowledged"] = str(acknowledged).lower()

            response = await self.get(self.ENDPOINT_ALERTS, params=params)
            return response.get("alerts", [])

        except Exception as e:
            logger.error("hotsheets_get_alerts_failed", error=str(e))
            return []

    async def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str | None = None,
        notes: str | None = None,
    ) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert identifier
            user_id: User acknowledging
            notes: Optional notes

        Returns:
            bool: True if acknowledged successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_ALERT_ACKNOWLEDGE.format(alert_id=alert_id)

            data: dict[str, Any] = {
                "acknowledgedAt": datetime.now(UTC).isoformat(),
            }

            if user_id:
                data["acknowledgedBy"] = user_id
            if notes:
                data["notes"] = notes

            await self.post(endpoint, data=data)

            logger.info("hotsheets_alert_acknowledged", alert_id=alert_id)

            return True

        except Exception as e:
            logger.error("hotsheets_acknowledge_alert_failed", alert_id=alert_id, error=str(e))
            return False

    async def get_lists(self) -> list[dict[str, Any]]:
        """
        Get available hotlists.

        Returns:
            list: Available lists with metadata
        """
        if not self.is_connected:
            return []

        try:
            response = await self.get(self.ENDPOINT_LISTS)
            return response.get("lists", [])

        except Exception as e:
            logger.error("hotsheets_get_lists_failed", error=str(e))
            return []

    async def get_list_entries(
        self,
        list_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get entries from a specific list.

        Args:
            list_id: List identifier
            limit: Maximum results

        Returns:
            list: List entries
        """
        if not self.is_connected:
            return []

        try:
            endpoint = self.ENDPOINT_LIST_ENTRIES.format(list_id=list_id)
            params = {"limit": limit}

            response = await self.get(endpoint, params=params)
            return response.get("entries", [])

        except Exception as e:
            logger.error("hotsheets_get_list_entries_failed", list_id=list_id, error=str(e))
            return []

    async def sync_lists(self) -> dict[str, Any]:
        """
        Trigger synchronization with external BOLO sources.

        Returns:
            dict: Sync status and statistics
        """
        if not self.is_connected:
            return {"success": False, "error": "Not connected"}

        try:
            response = await self.post(self.ENDPOINT_SYNC, data={})

            logger.info(
                "hotsheets_sync_triggered",
                added=response.get("added", 0),
                updated=response.get("updated", 0),
                removed=response.get("removed", 0),
            )

            return response

        except Exception as e:
            logger.error("hotsheets_sync_failed", error=str(e))
            return {"success": False, "error": str(e)}

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from HotSheets.

        Args:
            payload: Raw webhook payload
            signature: Signature from X-HotSheets-Signature header

        Returns:
            bool: True if signature is valid
        """
        if not self._webhook_secret:
            logger.warning("hotsheets_webhook_secret_not_configured")
            return True

        expected = hmac.new(
            self._webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def process_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming webhook from HotSheets.

        Args:
            payload: Webhook payload

        Returns:
            dict: Processed event data ready for ingestion
        """
        event_type = payload.get("eventType", payload.get("type", "bolo_alert"))
        bolo = payload.get("bolo", payload)
        subject = bolo.get("subject", {})
        match_info = payload.get("match", {})

        processed: dict[str, Any] = {
            "source": "hotsheets",
            "event_type": event_type,
            "timestamp": payload.get("timestamp", datetime.now(UTC).isoformat()),
            "boloId": bolo.get("id", bolo.get("boloId")),
            "boloType": bolo.get("type", bolo.get("boloType")),
            "status": bolo.get("status"),
            "priority": bolo.get("priority"),
            "description": bolo.get("description"),
            "reason": bolo.get("reason"),
            "caseNumber": bolo.get("caseNumber"),
            "originatingAgency": bolo.get("originatingAgency"),
            "expiresAt": bolo.get("expiresAt", bolo.get("expiration")),
        }

        if bolo.get("type") == "vehicle" or "plateNumber" in subject:
            processed["plateNumber"] = subject.get("plateNumber")
            processed["plateState"] = subject.get("plateState")
            processed["vehicleMake"] = subject.get("make")
            processed["vehicleModel"] = subject.get("model")
            processed["vehicleColor"] = subject.get("color")
            processed["vehicleYear"] = subject.get("year")
            processed["vin"] = subject.get("vin")

        if bolo.get("type") == "person" or "firstName" in subject:
            processed["firstName"] = subject.get("firstName")
            processed["lastName"] = subject.get("lastName")
            processed["dateOfBirth"] = subject.get("dateOfBirth")
            processed["gender"] = subject.get("gender")
            processed["description"] = subject.get("description")

        if match_info:
            processed["matchType"] = match_info.get("type")
            processed["matchSource"] = match_info.get("source")
            processed["matchConfidence"] = match_info.get("confidence")
            processed["matchLocation"] = match_info.get("location")
            processed["latitude"] = match_info.get("latitude")
            processed["longitude"] = match_info.get("longitude")

        logger.debug(
            "hotsheets_webhook_processed",
            event_type=event_type,
            bolo_id=processed.get("boloId"),
        )

        return processed


_hotsheets_integration: HotSheetsIntegration | None = None


def get_hotsheets_integration() -> HotSheetsIntegration:
    """Get the HotSheets integration instance."""
    global _hotsheets_integration
    if _hotsheets_integration is None:
        _hotsheets_integration = HotSheetsIntegration()
    return _hotsheets_integration
