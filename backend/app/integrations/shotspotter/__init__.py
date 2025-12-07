"""
ShotSpotter integration for the G3TI RTCC-UIP Backend.

ShotSpotter (now SoundThinking) provides acoustic gunshot detection:
- Real-time gunshot alerts
- Location triangulation
- Round count estimation
- Audio clip capture
- Historical analysis

This integration enables:
- Real-time gunshot notifications via webhook
- Alert acknowledgment and dispatch
- Historical incident search
- Sensor network status monitoring
- Audio clip retrieval
"""

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.logging import audit_logger, get_logger
from app.integrations.base import BaseIntegration
from app.schemas.events import EventSource, ShotSpotterEvent

logger = get_logger(__name__)


class ShotSpotterIntegration(BaseIntegration[ShotSpotterEvent]):
    """
    ShotSpotter gunshot detection integration client.

    Provides methods for interacting with ShotSpotter/SoundThinking including
    real-time alerts, historical search, and sensor management.

    API Documentation: https://api.soundthinking.com/docs
    """

    ENDPOINT_HEALTH = "/api/v1/health"
    ENDPOINT_INCIDENTS = "/api/v1/incidents"
    ENDPOINT_INCIDENT_DETAIL = "/api/v1/incidents/{incident_id}"
    ENDPOINT_AUDIO = "/api/v1/incidents/{incident_id}/audio"
    ENDPOINT_ACKNOWLEDGE = "/api/v1/incidents/{incident_id}/acknowledge"
    ENDPOINT_DISPATCH = "/api/v1/incidents/{incident_id}/dispatch"
    ENDPOINT_SENSORS = "/api/v1/sensors"
    ENDPOINT_SENSOR_STATUS = "/api/v1/sensors/{sensor_id}/status"
    ENDPOINT_COVERAGE = "/api/v1/coverage"
    ENDPOINT_STATISTICS = "/api/v1/statistics"

    def __init__(self) -> None:
        """Initialize ShotSpotter integration."""
        super().__init__(
            base_url=settings.shotspotter_api_url,
            api_key=settings.shotspotter_api_key,
            timeout=30.0,
        )
        self._agency_id = getattr(settings, "shotspotter_agency_id", None)
        self._webhook_secret = getattr(settings, "shotspotter_webhook_secret", None)

    @property
    def source(self) -> EventSource:
        """Get the event source."""
        return EventSource.SHOTSPOTTER

    def _get_auth_headers(self) -> dict[str, str]:
        """Get ShotSpotter-specific authentication headers."""
        headers = super()._get_auth_headers()
        if self._api_key:
            headers["X-SoundThinking-API-Key"] = self._api_key
        if self._agency_id:
            headers["X-Agency-ID"] = self._agency_id
        return headers

    async def health_check(self) -> bool:
        """
        Verify connectivity to ShotSpotter.

        Returns:
            bool: True if ShotSpotter is reachable and responding
        """
        if not self.is_configured:
            return False

        try:
            response = await self.get(self.ENDPOINT_HEALTH)
            return response.get("status") in ["healthy", "ok", "operational"]
        except Exception as e:
            logger.warning("shotspotter_health_check_failed", error=str(e))
            return False

    async def normalize_event(self, raw_data: dict[str, Any]) -> ShotSpotterEvent:
        """
        Normalize ShotSpotter event to standard format.

        Args:
            raw_data: Raw event data from ShotSpotter webhook or API

        Returns:
            ShotSpotterEvent: Normalized gunshot event
        """
        return ShotSpotterEvent(
            rounds_detected=raw_data.get("roundsDetected", raw_data.get("rounds", 1)),
            confidence=raw_data.get("confidence", raw_data.get("probability", 0.0)),
            sensor_ids=raw_data.get("sensorIds", raw_data.get("sensors", [])),
            audio_url=raw_data.get("audioUrl", raw_data.get("audio_clip_url")),
        )

    async def get_recent_alerts(
        self,
        hours: int = 24,
        limit: int = 100,
        incident_type: str | None = None,
        min_rounds: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get recent gunshot alerts.

        Args:
            hours: Hours to look back
            limit: Maximum alerts to return
            incident_type: Filter by type (gunshot, gunshot_or_firecracker, etc.)
            min_rounds: Minimum rounds detected

        Returns:
            list: Recent gunshot incidents
        """
        if not self.is_connected:
            logger.warning("shotspotter_not_connected_for_alerts")
            return []

        try:
            end_time = datetime.now(UTC)
            start_time = end_time - timedelta(hours=hours)

            params: dict[str, Any] = {
                "startTime": start_time.isoformat(),
                "endTime": end_time.isoformat(),
                "limit": limit,
            }

            if incident_type:
                params["incidentType"] = incident_type
            if min_rounds:
                params["minRounds"] = min_rounds

            response = await self.get(self.ENDPOINT_INCIDENTS, params=params)
            incidents = response.get("incidents", response.get("data", []))

            logger.info(
                "shotspotter_alerts_retrieved",
                count=len(incidents),
                hours=hours,
            )

            return incidents

        except Exception as e:
            logger.error("shotspotter_get_alerts_failed", error=str(e))
            return []

    async def get_alert_details(self, alert_id: str) -> dict[str, Any] | None:
        """
        Get detailed information for a specific alert.

        Args:
            alert_id: Alert/incident identifier

        Returns:
            dict | None: Detailed alert information
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_INCIDENT_DETAIL.format(incident_id=alert_id)
            response = await self.get(endpoint)

            logger.debug("shotspotter_alert_details_retrieved", alert_id=alert_id)

            return response

        except Exception as e:
            logger.error("shotspotter_get_alert_details_failed", alert_id=alert_id, error=str(e))
            return None

    async def get_audio_clip(self, alert_id: str) -> dict[str, Any] | None:
        """
        Get audio clip information for an alert.

        Args:
            alert_id: Alert identifier

        Returns:
            dict | None: Audio clip info including URL and duration
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_AUDIO.format(incident_id=alert_id)
            response = await self.get(endpoint)

            logger.debug("shotspotter_audio_retrieved", alert_id=alert_id)

            return response

        except Exception as e:
            logger.error("shotspotter_get_audio_failed", alert_id=alert_id, error=str(e))
            return None

    async def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str,
        notes: str | None = None,
        classification: str | None = None,
    ) -> bool:
        """
        Acknowledge a gunshot alert.

        Args:
            alert_id: Alert identifier
            user_id: User acknowledging the alert
            notes: Optional acknowledgment notes
            classification: Optional classification (confirmed, probable, possible, etc.)

        Returns:
            bool: True if acknowledged successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_ACKNOWLEDGE.format(incident_id=alert_id)

            data: dict[str, Any] = {
                "acknowledgedBy": user_id,
                "acknowledgedAt": datetime.now(UTC).isoformat(),
            }

            if notes:
                data["notes"] = notes
            if classification:
                data["classification"] = classification

            await self.post(endpoint, data=data)

            logger.info(
                "shotspotter_alert_acknowledged",
                alert_id=alert_id,
                user_id=user_id,
            )

            audit_logger.log_system_event(
                event_type="shotspotter_acknowledge",
                details={
                    "alert_id": alert_id,
                    "user_id": user_id,
                    "classification": classification,
                },
            )

            return True

        except Exception as e:
            logger.error(
                "shotspotter_acknowledge_failed",
                alert_id=alert_id,
                error=str(e),
            )
            return False

    async def dispatch_units(
        self,
        alert_id: str,
        unit_ids: list[str],
        dispatcher_id: str,
        notes: str | None = None,
    ) -> bool:
        """
        Record unit dispatch for an alert.

        Args:
            alert_id: Alert identifier
            unit_ids: List of unit IDs being dispatched
            dispatcher_id: ID of the dispatcher
            notes: Optional dispatch notes

        Returns:
            bool: True if dispatch recorded successfully
        """
        if not self.is_connected:
            return False

        try:
            endpoint = self.ENDPOINT_DISPATCH.format(incident_id=alert_id)

            data: dict[str, Any] = {
                "unitIds": unit_ids,
                "dispatchedBy": dispatcher_id,
                "dispatchedAt": datetime.now(UTC).isoformat(),
            }

            if notes:
                data["notes"] = notes

            await self.post(endpoint, data=data)

            logger.info(
                "shotspotter_units_dispatched",
                alert_id=alert_id,
                units=unit_ids,
            )

            audit_logger.log_system_event(
                event_type="shotspotter_dispatch",
                details={
                    "alert_id": alert_id,
                    "unit_ids": unit_ids,
                    "dispatcher_id": dispatcher_id,
                },
            )

            return True

        except Exception as e:
            logger.error(
                "shotspotter_dispatch_failed",
                alert_id=alert_id,
                error=str(e),
            )
            return False

    async def get_sensors(self, status: str | None = None) -> list[dict[str, Any]]:
        """
        Get all sensors in the network.

        Args:
            status: Filter by status (online, offline, maintenance)

        Returns:
            list: Sensor information
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {}
            if status:
                params["status"] = status

            response = await self.get(self.ENDPOINT_SENSORS, params=params)
            return response.get("sensors", [])

        except Exception as e:
            logger.error("shotspotter_get_sensors_failed", error=str(e))
            return []

    async def get_sensor_status(self, sensor_id: str) -> dict[str, Any] | None:
        """
        Get status of a specific sensor.

        Args:
            sensor_id: Sensor identifier

        Returns:
            dict | None: Sensor status information
        """
        if not self.is_connected:
            return None

        try:
            endpoint = self.ENDPOINT_SENSOR_STATUS.format(sensor_id=sensor_id)
            response = await self.get(endpoint)
            return response

        except Exception as e:
            logger.error("shotspotter_get_sensor_status_failed", sensor_id=sensor_id, error=str(e))
            return None

    async def get_coverage_area(self) -> dict[str, Any] | None:
        """
        Get the coverage area polygon for the agency.

        Returns:
            dict | None: GeoJSON polygon of coverage area
        """
        if not self.is_connected:
            return None

        try:
            response = await self.get(self.ENDPOINT_COVERAGE)
            return response

        except Exception as e:
            logger.error("shotspotter_get_coverage_failed", error=str(e))
            return None

    async def get_statistics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any] | None:
        """
        Get incident statistics for a time period.

        Args:
            start_date: Start of period
            end_date: End of period

        Returns:
            dict | None: Statistics including counts, response times, etc.
        """
        if not self.is_connected:
            return None

        try:
            params: dict[str, Any] = {}
            if start_date:
                params["startDate"] = start_date.isoformat()
            if end_date:
                params["endDate"] = end_date.isoformat()

            response = await self.get(self.ENDPOINT_STATISTICS, params=params)
            return response

        except Exception as e:
            logger.error("shotspotter_get_statistics_failed", error=str(e))
            return None

    async def search_incidents(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        radius_meters: float = 500,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search for incidents by location and time.

        Args:
            latitude: Center latitude for geo search
            longitude: Center longitude for geo search
            radius_meters: Search radius in meters
            start_date: Start of time range
            end_date: End of time range
            limit: Maximum results

        Returns:
            list: Matching incidents
        """
        if not self.is_connected:
            return []

        try:
            params: dict[str, Any] = {"limit": limit}

            if latitude and longitude:
                params["latitude"] = latitude
                params["longitude"] = longitude
                params["radius"] = radius_meters

            if start_date:
                params["startDate"] = start_date.isoformat()
            if end_date:
                params["endDate"] = end_date.isoformat()

            response = await self.get(self.ENDPOINT_INCIDENTS, params=params)

            incidents = response.get("incidents", [])

            logger.info(
                "shotspotter_search_complete",
                results_count=len(incidents),
            )

            return incidents

        except Exception as e:
            logger.error("shotspotter_search_failed", error=str(e))
            return []

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from ShotSpotter.

        Args:
            payload: Raw webhook payload
            signature: Signature from X-SoundThinking-Signature header

        Returns:
            bool: True if signature is valid
        """
        if not self._webhook_secret:
            logger.warning("shotspotter_webhook_secret_not_configured")
            return True

        expected = hmac.new(
            self._webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    async def process_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming webhook from ShotSpotter.

        Args:
            payload: Webhook payload

        Returns:
            dict: Processed event data ready for ingestion
        """
        incident = payload.get("incident", payload)
        location = incident.get("location", {})

        processed: dict[str, Any] = {
            "source": "shotspotter",
            "id": incident.get("id", incident.get("incidentId")),
            "timestamp": incident.get("timestamp", incident.get("eventTime")),
            "incidentType": incident.get("incidentType", "gunshot"),
            "rounds": incident.get("rounds", incident.get("roundsDetected", 1)),
            "roundsDetected": incident.get("rounds", incident.get("roundsDetected", 1)),
            "confidence": incident.get("confidence", incident.get("probability", 0.0)),
            "latitude": location.get("latitude", incident.get("latitude")),
            "longitude": location.get("longitude", incident.get("longitude")),
            "address": location.get("address", incident.get("address")),
            "sensorIds": incident.get("sensorIds", incident.get("sensors", [])),
            "audioUrl": incident.get("audioUrl", incident.get("audio_clip_url")),
            "status": incident.get("status", "new"),
        }

        logger.debug(
            "shotspotter_webhook_processed",
            incident_id=processed.get("id"),
            rounds=processed.get("rounds"),
        )

        return processed


_shotspotter_integration: ShotSpotterIntegration | None = None


def get_shotspotter_integration() -> ShotSpotterIntegration:
    """Get the ShotSpotter integration instance."""
    global _shotspotter_integration
    if _shotspotter_integration is None:
        _shotspotter_integration = ShotSpotterIntegration()
    return _shotspotter_integration
