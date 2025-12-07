"""
NESS integration for the G3TI RTCC-UIP Backend.

NESS (National Enforcement Support System) provides:
- Warrant checks and NCIC queries
- Criminal history records
- Driver license verification
- Vehicle registration lookup
- Stolen vehicle/property checks
- Missing/wanted person queries

This integration enables:
- Person background checks with CJIS compliance
- Warrant verification and alerts
- Vehicle registration and stolen checks
- License status verification
- NCIC/NLETS message handling

Note: All NESS queries require proper authorization and are
subject to CJIS audit logging requirements.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.logging import audit_logger, get_logger
from app.integrations.base import BaseIntegration
from app.schemas.events import EventSource

logger = get_logger(__name__)


class NESSIntegration(BaseIntegration[dict[str, Any]]):
    """
    NESS integration client.

    Provides methods for querying NESS including warrant checks,
    criminal history, and vehicle registration lookups.

    Note: NESS queries are highly regulated and require proper
    authorization and audit logging for CJIS compliance.

    All queries are logged with user ID, purpose, and timestamp
    for audit trail requirements.
    """

    ENDPOINT_HEALTH = "/api/v1/health"
    ENDPOINT_WARRANTS = "/api/v1/ncic/warrants"
    ENDPOINT_CRIMINAL_HISTORY = "/api/v1/ncic/criminal-history"
    ENDPOINT_LICENSE = "/api/v1/nlets/license"
    ENDPOINT_VEHICLE = "/api/v1/nlets/vehicle"
    ENDPOINT_STOLEN_VEHICLE = "/api/v1/ncic/stolen-vehicle"
    ENDPOINT_STOLEN_PROPERTY = "/api/v1/ncic/stolen-property"
    ENDPOINT_MISSING_PERSON = "/api/v1/ncic/missing-person"
    ENDPOINT_WANTED_PERSON = "/api/v1/ncic/wanted-person"
    ENDPOINT_PERSON_QUERY = "/api/v1/query/person"
    ENDPOINT_VEHICLE_QUERY = "/api/v1/query/vehicle"
    ENDPOINT_MESSAGE = "/api/v1/message"

    def __init__(self) -> None:
        """Initialize NESS integration."""
        super().__init__(
            base_url=settings.ness_api_url,
            api_key=settings.ness_api_key,
            timeout=60.0,
        )
        self._agency_ori = getattr(settings, "ness_agency_ori", None)
        self._operator_id = getattr(settings, "ness_operator_id", None)

    @property
    def source(self) -> EventSource:
        """Get the event source."""
        return EventSource.NESS

    def _get_auth_headers(self) -> dict[str, str]:
        """Get NESS-specific authentication headers."""
        headers = super()._get_auth_headers()
        if self._api_key:
            headers["X-NESS-API-Key"] = self._api_key
        if self._agency_ori:
            headers["X-Agency-ORI"] = self._agency_ori
        return headers

    async def health_check(self) -> bool:
        """
        Verify connectivity to NESS.

        Returns:
            bool: True if NESS is reachable and responding
        """
        if not self.is_configured:
            return False

        try:
            response = await self.get(self.ENDPOINT_HEALTH)
            return response.get("status") in ["healthy", "ok", "connected"]
        except Exception as e:
            logger.warning("ness_health_check_failed", error=str(e))
            return False

    async def normalize_event(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize NESS response data.

        Args:
            raw_data: Raw data from NESS

        Returns:
            dict: Normalized data with standard fields
        """
        normalized = {
            "source": "ness",
            "timestamp": raw_data.get("timestamp", datetime.now(UTC).isoformat()),
            "query_id": raw_data.get("queryId", raw_data.get("transactionId")),
            "record_type": raw_data.get("recordType", "unknown"),
            "has_warrant": raw_data.get("hasWarrant", False),
            "alert_flag": raw_data.get("alertFlag", False),
            "alert_reason": raw_data.get("alertReason"),
        }

        if "person" in raw_data:
            normalized["person"] = raw_data["person"]
        if "vehicle" in raw_data:
            normalized["vehicle"] = raw_data["vehicle"]
        if "results" in raw_data:
            normalized["results"] = raw_data["results"]

        return normalized

    def _log_cjis_query(
        self,
        query_type: str,
        user_id: str | None,
        purpose: str | None,
        query_params: dict[str, Any],
        response_summary: dict[str, Any],
    ) -> str:
        """
        Log CJIS-compliant audit entry for a query.

        Args:
            query_type: Type of query performed
            user_id: User who initiated the query
            purpose: Stated purpose of the query
            query_params: Parameters used in the query
            response_summary: Summary of the response

        Returns:
            str: Query transaction ID
        """
        transaction_id = str(uuid.uuid4())

        audit_logger.log_system_event(
            event_type=f"ness_{query_type}",
            details={
                "transaction_id": transaction_id,
                "user_id": user_id or "system",
                "purpose": purpose or "law_enforcement",
                "query_params": {k: v for k, v in query_params.items() if k not in ["ssn"]},
                "response_summary": response_summary,
                "timestamp": datetime.now(UTC).isoformat(),
                "agency_ori": self._agency_ori,
            },
        )

        logger.info(
            "ness_cjis_query_logged",
            query_type=query_type,
            transaction_id=transaction_id,
            user_id=user_id,
        )

        return transaction_id

    async def check_warrants(
        self,
        first_name: str,
        last_name: str,
        dob: str | None = None,
        ssn: str | None = None,
        user_id: str | None = None,
        purpose: str | None = None,
    ) -> dict[str, Any]:
        """
        Check for active warrants.

        Args:
            first_name: Person's first name
            last_name: Person's last name
            dob: Date of birth (YYYY-MM-DD)
            ssn: Social Security Number (optional, for more accurate matching)
            user_id: User making the query (required for audit)
            purpose: Purpose of query (required for audit)

        Returns:
            dict: Warrant check results including any active warrants
        """
        if not self.is_connected:
            return {"error": "NESS not connected", "results": [], "has_warrants": False}

        try:
            data: dict[str, Any] = {
                "firstName": first_name,
                "lastName": last_name,
                "operatorId": self._operator_id or user_id,
                "purpose": purpose or "law_enforcement_inquiry",
            }

            if dob:
                data["dateOfBirth"] = dob
            if ssn:
                data["ssn"] = ssn

            response = await self.post(self.ENDPOINT_WARRANTS, data=data)

            results = response.get("warrants", response.get("results", []))
            has_warrants = len(results) > 0

            self._log_cjis_query(
                query_type="warrant_check",
                user_id=user_id,
                purpose=purpose,
                query_params={"first_name": first_name, "last_name": last_name, "dob": dob},
                response_summary={"has_warrants": has_warrants, "count": len(results)},
            )

            return {
                "results": results,
                "has_warrants": has_warrants,
                "query_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("ness_warrant_check_failed", error=str(e))
            return {"error": str(e), "results": [], "has_warrants": False}

    async def get_criminal_history(
        self,
        first_name: str,
        last_name: str,
        dob: str | None = None,
        ssn: str | None = None,
        state_id: str | None = None,
        user_id: str | None = None,
        purpose: str | None = None,
    ) -> dict[str, Any]:
        """
        Get criminal history record.

        Args:
            first_name: Person's first name
            last_name: Person's last name
            dob: Date of birth
            ssn: Social Security Number
            state_id: State ID number
            user_id: User making the query
            purpose: Purpose of query

        Returns:
            dict: Criminal history results
        """
        if not self.is_connected:
            return {"error": "NESS not connected", "records": []}

        try:
            data: dict[str, Any] = {
                "firstName": first_name,
                "lastName": last_name,
                "operatorId": self._operator_id or user_id,
                "purpose": purpose or "criminal_justice",
            }

            if dob:
                data["dateOfBirth"] = dob
            if ssn:
                data["ssn"] = ssn
            if state_id:
                data["stateId"] = state_id

            response = await self.post(self.ENDPOINT_CRIMINAL_HISTORY, data=data)

            records = response.get("records", response.get("history", []))

            self._log_cjis_query(
                query_type="criminal_history",
                user_id=user_id,
                purpose=purpose,
                query_params={"first_name": first_name, "last_name": last_name, "dob": dob},
                response_summary={"record_count": len(records)},
            )

            return {
                "records": records,
                "query_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("ness_criminal_history_failed", error=str(e))
            return {"error": str(e), "records": []}

    async def verify_license(
        self,
        license_number: str,
        state: str,
        user_id: str | None = None,
        purpose: str | None = None,
    ) -> dict[str, Any]:
        """
        Verify driver's license.

        Args:
            license_number: License number
            state: Issuing state (2-letter code)
            user_id: User making the query
            purpose: Purpose of query

        Returns:
            dict: License verification results including status and restrictions
        """
        if not self.is_connected:
            return {"error": "NESS not connected", "valid": None}

        try:
            data = {
                "licenseNumber": license_number.upper(),
                "state": state.upper(),
                "operatorId": self._operator_id or user_id,
                "purpose": purpose or "traffic_stop",
            }

            response = await self.post(self.ENDPOINT_LICENSE, data=data)

            self._log_cjis_query(
                query_type="license_verification",
                user_id=user_id,
                purpose=purpose,
                query_params={"license_number": license_number, "state": state},
                response_summary={"valid": response.get("valid"), "status": response.get("status")},
            )

            return {
                "valid": response.get("valid"),
                "status": response.get("status"),
                "expiration_date": response.get("expirationDate"),
                "restrictions": response.get("restrictions", []),
                "endorsements": response.get("endorsements", []),
                "holder": response.get("holder", {}),
                "query_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("ness_license_verification_failed", error=str(e))
            return {"error": str(e), "valid": None}

    async def lookup_vehicle_registration(
        self,
        plate_number: str,
        state: str,
        user_id: str | None = None,
        purpose: str | None = None,
    ) -> dict[str, Any]:
        """
        Look up vehicle registration.

        Args:
            plate_number: License plate number
            state: Plate state (2-letter code)
            user_id: User making the query
            purpose: Purpose of query

        Returns:
            dict: Vehicle registration results including owner info
        """
        if not self.is_connected:
            return {"error": "NESS not connected", "registration": None}

        try:
            data = {
                "plateNumber": plate_number.upper(),
                "state": state.upper(),
                "operatorId": self._operator_id or user_id,
                "purpose": purpose or "traffic_stop",
            }

            response = await self.post(self.ENDPOINT_VEHICLE, data=data)

            self._log_cjis_query(
                query_type="vehicle_registration",
                user_id=user_id,
                purpose=purpose,
                query_params={"plate_number": plate_number, "state": state},
                response_summary={"found": response.get("registration") is not None},
            )

            return {
                "registration": response.get("registration"),
                "owner": response.get("owner"),
                "vehicle": response.get("vehicle"),
                "query_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("ness_vehicle_registration_failed", error=str(e))
            return {"error": str(e), "registration": None}

    async def check_stolen_vehicle(
        self,
        plate_number: str | None = None,
        state: str | None = None,
        vin: str | None = None,
        user_id: str | None = None,
        purpose: str | None = None,
    ) -> dict[str, Any]:
        """
        Check if a vehicle is reported stolen.

        Args:
            plate_number: License plate number
            state: Plate state
            vin: Vehicle identification number
            user_id: User making the query
            purpose: Purpose of query

        Returns:
            dict: Stolen vehicle check results
        """
        if not self.is_connected:
            return {"error": "NESS not connected", "is_stolen": None}

        try:
            data: dict[str, Any] = {
                "operatorId": self._operator_id or user_id,
                "purpose": purpose or "vehicle_stop",
            }

            if plate_number:
                data["plateNumber"] = plate_number.upper()
            if state:
                data["state"] = state.upper()
            if vin:
                data["vin"] = vin.upper()

            response = await self.post(self.ENDPOINT_STOLEN_VEHICLE, data=data)

            is_stolen = response.get("isStolen", response.get("stolen", False))

            self._log_cjis_query(
                query_type="stolen_vehicle_check",
                user_id=user_id,
                purpose=purpose,
                query_params={"plate_number": plate_number, "state": state, "vin": vin},
                response_summary={"is_stolen": is_stolen},
            )

            return {
                "is_stolen": is_stolen,
                "ncic_number": response.get("ncicNumber"),
                "stolen_date": response.get("stolenDate"),
                "reporting_agency": response.get("reportingAgency"),
                "case_number": response.get("caseNumber"),
                "query_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("ness_stolen_vehicle_check_failed", error=str(e))
            return {"error": str(e), "is_stolen": None}

    async def check_wanted_person(
        self,
        first_name: str,
        last_name: str,
        dob: str | None = None,
        user_id: str | None = None,
        purpose: str | None = None,
    ) -> dict[str, Any]:
        """
        Check if a person is wanted.

        Args:
            first_name: Person's first name
            last_name: Person's last name
            dob: Date of birth
            user_id: User making the query
            purpose: Purpose of query

        Returns:
            dict: Wanted person check results
        """
        if not self.is_connected:
            return {"error": "NESS not connected", "is_wanted": None}

        try:
            data: dict[str, Any] = {
                "firstName": first_name,
                "lastName": last_name,
                "operatorId": self._operator_id or user_id,
                "purpose": purpose or "field_interview",
            }

            if dob:
                data["dateOfBirth"] = dob

            response = await self.post(self.ENDPOINT_WANTED_PERSON, data=data)

            is_wanted = response.get("isWanted", response.get("wanted", False))

            self._log_cjis_query(
                query_type="wanted_person_check",
                user_id=user_id,
                purpose=purpose,
                query_params={"first_name": first_name, "last_name": last_name, "dob": dob},
                response_summary={"is_wanted": is_wanted},
            )

            return {
                "is_wanted": is_wanted,
                "warrants": response.get("warrants", []),
                "ncic_number": response.get("ncicNumber"),
                "query_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("ness_wanted_person_check_failed", error=str(e))
            return {"error": str(e), "is_wanted": None}

    async def comprehensive_person_query(
        self,
        first_name: str,
        last_name: str,
        dob: str | None = None,
        ssn: str | None = None,
        license_number: str | None = None,
        license_state: str | None = None,
        user_id: str | None = None,
        purpose: str | None = None,
    ) -> dict[str, Any]:
        """
        Perform comprehensive person query (warrants, criminal history, license).

        Args:
            first_name: Person's first name
            last_name: Person's last name
            dob: Date of birth
            ssn: Social Security Number
            license_number: Driver's license number
            license_state: License state
            user_id: User making the query
            purpose: Purpose of query

        Returns:
            dict: Comprehensive query results
        """
        if not self.is_connected:
            return {"error": "NESS not connected"}

        try:
            data: dict[str, Any] = {
                "firstName": first_name,
                "lastName": last_name,
                "operatorId": self._operator_id or user_id,
                "purpose": purpose or "comprehensive_check",
                "includeWarrants": True,
                "includeCriminalHistory": True,
                "includeLicense": license_number is not None,
            }

            if dob:
                data["dateOfBirth"] = dob
            if ssn:
                data["ssn"] = ssn
            if license_number:
                data["licenseNumber"] = license_number
            if license_state:
                data["licenseState"] = license_state

            response = await self.post(self.ENDPOINT_PERSON_QUERY, data=data)

            self._log_cjis_query(
                query_type="comprehensive_person_query",
                user_id=user_id,
                purpose=purpose,
                query_params={"first_name": first_name, "last_name": last_name, "dob": dob},
                response_summary={
                    "has_warrants": response.get("hasWarrants", False),
                    "has_criminal_history": len(response.get("criminalHistory", [])) > 0,
                },
            )

            return {
                "person": response.get("person"),
                "warrants": response.get("warrants", []),
                "has_warrants": response.get("hasWarrants", False),
                "criminal_history": response.get("criminalHistory", []),
                "license": response.get("license"),
                "alerts": response.get("alerts", []),
                "query_time": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("ness_comprehensive_query_failed", error=str(e))
            return {"error": str(e)}

    async def process_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming webhook/message from NESS.

        Args:
            payload: Webhook payload (typically NCIC hit notifications)

        Returns:
            dict: Processed event data ready for ingestion
        """
        message_type = payload.get("messageType", payload.get("type", "notification"))

        processed: dict[str, Any] = {
            "source": "ness",
            "message_type": message_type,
            "timestamp": payload.get("timestamp", datetime.now(UTC).isoformat()),
            "transaction_id": payload.get("transactionId"),
            "record_type": payload.get("recordType"),
            "has_warrant": payload.get("hasWarrant", False),
            "alert_flag": payload.get("alertFlag", False),
            "alert_reason": payload.get("alertReason"),
        }

        if payload.get("person"):
            processed["personId"] = payload["person"].get("id")
            processed["personName"] = (
                f"{payload['person'].get('firstName', '')} {payload['person'].get('lastName', '')}".strip()
            )

        if payload.get("vehicle"):
            processed["plateNumber"] = payload["vehicle"].get("plateNumber")
            processed["plateState"] = payload["vehicle"].get("state")

        logger.debug(
            "ness_webhook_processed",
            message_type=message_type,
            has_warrant=processed.get("has_warrant"),
        )

        return processed


_ness_integration: NESSIntegration | None = None


def get_ness_integration() -> NESSIntegration:
    """Get the NESS integration instance."""
    global _ness_integration
    if _ness_integration is None:
        _ness_integration = NESSIntegration()
    return _ness_integration
