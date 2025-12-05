"""
OneSolution CAD/RMS integration for the G3TI RTCC-UIP Backend.

OneSolution is a Computer-Aided Dispatch (CAD) and Records Management System (RMS):
- Real-time CAD events and dispatch
- Incident reports and case management
- Arrest records and booking
- Person and vehicle records
- Property/evidence tracking
- Unit status and location

This integration enables:
- Real-time CAD event streaming via webhook
- Incident data retrieval and search
- Person and vehicle lookup
- Unit status monitoring
- Call for service tracking
"""

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.logging import audit_logger, get_logger
from app.integrations.base import BaseIntegration
from app.schemas.events import EventSource, IncidentEvent

logger = get_logger(__name__)


class OneSolutionIntegration(BaseIntegration[IncidentEvent]):
    """
    OneSolution CAD/RMS integration client.

    Provides methods for interacting with OneSolution including
    CAD events, incident retrieval, person lookup, and case management.

    API Documentation: https://docs.hexagonsi.com/onesolution/api
    """

    ENDPOINT_HEALTH = "/api/v1/health"
    ENDPOINT_INCIDENTS = "/api/v1/incidents"
    ENDPOINT_INCIDENT_DETAIL = "/api/v1/incidents/{incident_id}"
    ENDPOINT_CALLS = "/api/v1/cad/calls"
    ENDPOINT_CALL_DETAIL = "/api/v1/cad/calls/{call_id}"
    ENDPOINT_UNITS = "/api/v1/cad/units"
    ENDPOINT_UNIT_STATUS = "/api/v1/cad/units/{unit_id}/status"
    ENDPOINT_PERSONS = "/api/v1/rms/persons"
    ENDPOINT_PERSON_DETAIL = "/api/v1/rms/persons/{person_id}"
    ENDPOINT_VEHICLES = "/api/v1/rms/vehicles"
    ENDPOINT_ARRESTS = "/api/v1/rms/arrests"
    ENDPOINT_CASES = "/api/v1/rms/cases"
    ENDPOINT_NARRATIVES = "/api/v1/incidents/{incident_id}/narratives"

    def __init__(self) -> None:
        """Initialize OneSolution integration."""
        super().__init__(
            base_url=settings.onesolution_api_url,
            api_key=settings.onesolution_api_key,
            timeout=30.0,
        )
        self._agency_ori = getattr(settings, "onesolution_agency_ori", None)
        self._webhook_secret = getattr(settings, "onesolution_webhook_secret", None)

    @property
    def source(self) -> EventSource:
        """Get the event source."""
        return EventSource.ONESOLUTION

    def _get_auth_headers(self) -> dict[str, str]:
        """Get OneSolution-specific authentication headers."""
        headers = super()._get_auth_headers()
        if self._api_key:
            headers["X-OneSolution-API-Key"] = self._api_key
        if self._agency_ori:
            headers["X-Agency-ORI"] = self._agency_ori
        return headers

    async def health_check(self) -> bool:
        """
        Verify connectivity to OneSolution.

        Returns:
            bool: True if OneSolution is reachable and responding
        """
        if not self.is_configured:
            return False

        try:
            response = await self.get(self.ENDPOINT_HEALTH)
            return response.get("status") in ["healthy", "ok", "connected"]
        except Exception as e:
            logger.warning("onesolution_health_check_failed", error=str(e))
            return False

    async def normalize_event(self, raw_data: dict[str, Any]) -> IncidentEvent:
        """
        Normalize OneSolution event to standard format.

        Args:
            raw_data: Raw event data from OneSolution webhook or API

        Returns:
            IncidentEvent: Normalized incident event
        """
        call = raw_data.get("call", raw_data)

        return IncidentEvent(
            incident_id=call.get("incidentId", call.get("id", "")),
            incident_number=call.get("incidentNumber", call.get("callNumber", "")),
            incident_type=call.get("incidentType", call.get("callType", "")),
            status=call.get("status", call.get("callStatus", "")),
            responding_units=call.get("respondingUnits", call.get("units", [])),
            previous_status=call.get("previousStatus"),
        )

    async def get_active_calls(
        self,
        priority: str | None = None,
        call_type: str | None = None,
        beat: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get active CAD calls.

        Args:
            priority: Filter by priority code
            call_type: Filter by call type
            beat: Filter by beat/zone

        Returns:
            list: Active calls for service
        """
        if not self.is_connected:
            logger.warning("onesolution_not_connected_for_calls")
            return []

        try:
            params: dict[str, Any] = {"status": "active"}

            if priority:
                params["priority"] = priority
            if call_type:
                params["callType"] = call_type
            if beat:
                params["beat"] = beat

            response = await self.get(self.ENDPOINT_CALLS, params=params)
            calls = response.get("calls", response.get("items", []))

            logger.info("onesolution_active_calls_retrieved", count=len(calls))

            return calls

        except Exception as e:
            logger.error("onesolution_get_active_calls_failed", error=str(e))
            return []

    async def get_call_detail(self, call_id: str) -> dict[str, Any] | None:
        """
        Get detailed information for a specific call.

        Args:
            call_id: Call identifier

        Returns:
            dict | None: Call details including narrative, units, timeline
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_CALL_DETAIL.format(call_id=call_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("onesolution_get_call_detail_failed", call_id=call_id, error=str(e))
            return None

    async def get_incident(self, incident_number: str) -> dict[str, Any] | None:
        """
        Get incident details by number.

        Args:
            incident_number: Incident number

        Returns:
            dict | None: Incident details
        """
        if not self.is_connected:
            return None

        try:
            params = {"incidentNumber": incident_number}
            response = await self.get(self.ENDPOINT_INCIDENTS, params=params)

            incidents = response.get("incidents", [])
            if incidents:
                return incidents[0]
            return None

        except Exception as e:
            logger.error(
                "onesolution_get_incident_failed", incident_number=incident_number, error=str(e)
            )
            return None

    async def search_incidents(
        self,
        query: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        incident_type: str | None = None,
        status: str | None = None,
        beat: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search incidents.

        Args:
            query: Full-text search query
            start_date: Start date filter
            end_date: End date filter
            incident_type: Incident type filter
            status: Status filter
            beat: Beat/zone filter
            limit: Maximum results

        Returns:
            list: Matching incidents
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {"limit": limit}

            if query:
                params["q"] = query
            if start_date:
                params["startDate"] = start_date.isoformat()
            if end_date:
                params["endDate"] = end_date.isoformat()
            if incident_type:
                params["incidentType"] = incident_type
            if status:
                params["status"] = status
            if beat:
                params["beat"] = beat

            response = await self.get(self.ENDPOINT_INCIDENTS, params=params)
            incidents = response.get("incidents", [])

            logger.info("onesolution_incident_search_complete", count=len(incidents))

            return incidents

        except Exception as e:
            logger.error("onesolution_search_incidents_failed", error=str(e))
            return []

    async def get_incident_narrative(self, incident_id: str) -> list[dict[str, Any]]:
        """
        Get narrative entries for an incident.

        Args:
            incident_id: Incident identifier

        Returns:
            list: Narrative entries with timestamps and authors
        """
        if not self.is_connected:
            return []

        try:
            endpoint = self.ENDPOINT_NARRATIVES.format(incident_id=incident_id)
            response = await self.get(endpoint)
            return response.get("narratives", [])

        except Exception as e:
            logger.error("onesolution_get_narrative_failed", incident_id=incident_id, error=str(e))
            return []

    async def get_units(self, status: str | None = None) -> list[dict[str, Any]]:
        """
        Get CAD units.

        Args:
            status: Filter by status (available, dispatched, on_scene, etc.)

        Returns:
            list: Unit information including status and location
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {}
            if status:
                params["status"] = status

            response = await self.get(self.ENDPOINT_UNITS, params=params)
            return response.get("units", [])

        except Exception as e:
            logger.error("onesolution_get_units_failed", error=str(e))
            return []

    async def get_unit_status(self, unit_id: str) -> dict[str, Any] | None:
        """
        Get current status of a specific unit.

        Args:
            unit_id: Unit identifier

        Returns:
            dict | None: Unit status including location, assigned call
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_UNIT_STATUS.format(unit_id=unit_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("onesolution_get_unit_status_failed", unit_id=unit_id, error=str(e))
            return None

    async def get_person(self, person_id: str) -> dict[str, Any] | None:
        """
        Get person record by ID.

        Args:
            person_id: Person identifier

        Returns:
            dict | None: Person record
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_PERSON_DETAIL.format(person_id=person_id)
            response = await self.get(endpoint)

            audit_logger.log_entity_access(
                entity_type="person",
                entity_id=person_id,
                action="view",
                user_id="system",
                details={"source": "onesolution"},
            )

            return response

        except Exception as e:
            logger.error("onesolution_get_person_failed", person_id=person_id, error=str(e))
            return None

    async def search_persons(
        self,
        name: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        dob: str | None = None,
        ssn_last4: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Search person records.

        Args:
            name: Full name to search
            first_name: First name
            last_name: Last name
            dob: Date of birth (YYYY-MM-DD)
            ssn_last4: Last 4 digits of SSN
            limit: Maximum results

        Returns:
            list: Matching person records
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {"limit": limit}

            if name:
                params["name"] = name
            if first_name:
                params["firstName"] = first_name
            if last_name:
                params["lastName"] = last_name
            if dob:
                params["dob"] = dob
            if ssn_last4:
                params["ssnLast4"] = ssn_last4

            response = await self.get(self.ENDPOINT_PERSONS, params=params)
            persons = response.get("persons", [])

            audit_logger.log_system_event(
                event_type="onesolution_person_search",
                details={"results_count": len(persons)},
            )

            return persons

        except Exception as e:
            logger.error("onesolution_search_persons_failed", error=str(e))
            return []

    async def search_vehicles(
        self,
        plate_number: str | None = None,
        plate_state: str | None = None,
        vin: str | None = None,
        make: str | None = None,
        model: str | None = None,
        color: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Search vehicle records.

        Args:
            plate_number: License plate number
            plate_state: Plate state
            vin: Vehicle identification number
            make: Vehicle make
            model: Vehicle model
            color: Vehicle color
            limit: Maximum results

        Returns:
            list: Matching vehicle records
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {"limit": limit}

            if plate_number:
                params["plateNumber"] = plate_number.upper()
            if plate_state:
                params["plateState"] = plate_state.upper()
            if vin:
                params["vin"] = vin.upper()
            if make:
                params["make"] = make
            if model:
                params["model"] = model
            if color:
                params["color"] = color

            response = await self.get(self.ENDPOINT_VEHICLES, params=params)
            return response.get("vehicles", [])

        except Exception as e:
            logger.error("onesolution_search_vehicles_failed", error=str(e))
            return []

    async def get_recent_arrests(
        self,
        hours: int = 24,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get recent arrests.

        Args:
            hours: Hours to look back
            limit: Maximum results

        Returns:
            list: Recent arrest records
        """
        if not self.is_connected:
            return []

        try:
            end_time = datetime.now(UTC)
            start_time = end_time - timedelta(hours=hours)

            params: dict[str, Any] = {
                "startDate": start_time.isoformat(),
                "endDate": end_time.isoformat(),
                "limit": limit,
            }

            response = await self.get(self.ENDPOINT_ARRESTS, params=params)
            return response.get("arrests", [])

        except Exception as e:
            logger.error("onesolution_get_arrests_failed", error=str(e))
            return []

    async def get_case(self, case_number: str) -> dict[str, Any] | None:
        """
        Get case details by case number.

        Args:
            case_number: Case number

        Returns:
            dict | None: Case details
        """
        if not self.is_connected:
            return None

        try:
            params = {"caseNumber": case_number}
            response = await self.get(self.ENDPOINT_CASES, params=params)

            cases = response.get("cases", [])
            if cases:
                return cases[0]
            return None

        except Exception as e:
            logger.error("onesolution_get_case_failed", case_number=case_number, error=str(e))
            return None

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from OneSolution.

        Args:
            payload: Raw webhook payload
            signature: Signature from X-OneSolution-Signature header

        Returns:
            bool: True if signature is valid
        """
        if not self._webhook_secret:
            logger.warning("onesolution_webhook_secret_not_configured")
            return True

        expected = hmac.new(
            self._webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def process_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming webhook from OneSolution CAD.

        Args:
            payload: Webhook payload

        Returns:
            dict: Processed event data ready for ingestion
        """
        event_type = payload.get("eventType", payload.get("type", "call_update"))
        call = payload.get("call", payload)
        location = call.get("location", {})

        processed: dict[str, Any] = {
            "source": "onesolution",
            "event_type": event_type,
            "id": call.get("id", call.get("callId")),
            "timestamp": call.get("timestamp", call.get("updateTime")),
            "incidentId": call.get("incidentId"),
            "incidentNumber": call.get("incidentNumber", call.get("callNumber")),
            "incidentType": call.get("incidentType", call.get("callType")),
            "callType": call.get("callType"),
            "status": call.get("status", call.get("callStatus")),
            "previousStatus": call.get("previousStatus"),
            "priorityCode": call.get("priorityCode", call.get("priority")),
            "latitude": location.get("latitude", call.get("latitude")),
            "longitude": location.get("longitude", call.get("longitude")),
            "address": location.get("address", call.get("address")),
            "beat": call.get("beat"),
            "district": call.get("district"),
            "respondingUnits": call.get("respondingUnits", call.get("units", [])),
            "narrative": call.get("narrative"),
            "callerInfo": call.get("callerInfo"),
            "disposition": call.get("disposition"),
        }

        logger.debug(
            "onesolution_webhook_processed",
            event_type=event_type,
            incident_number=processed.get("incidentNumber"),
        )

        return processed


_onesolution_integration: OneSolutionIntegration | None = None


def get_onesolution_integration() -> OneSolutionIntegration:
    """Get the OneSolution integration instance."""
    global _onesolution_integration
    if _onesolution_integration is None:
        _onesolution_integration = OneSolutionIntegration()
    return _onesolution_integration
