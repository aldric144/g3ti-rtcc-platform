"""
ShotSpotter integration for the G3TI RTCC-UIP Backend.

ShotSpotter (now SoundThinking) provides acoustic gunshot detection:
- Real-time gunshot alerts
- Location triangulation
- Round count estimation
- Audio clip capture
- Historical analysis

This integration enables:
- Real-time gunshot notifications
- Alert acknowledgment
- Historical search
- Sensor status monitoring
"""

from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.base import BaseIntegration
from app.schemas.events import EventSource, ShotSpotterEvent

logger = get_logger(__name__)


class ShotSpotterIntegration(BaseIntegration[ShotSpotterEvent]):
    """
    ShotSpotter gunshot detection integration client.

    Provides methods for interacting with ShotSpotter including
    real-time alerts, historical search, and sensor management.
    """

    def __init__(self) -> None:
        """Initialize ShotSpotter integration."""
        super().__init__(
            base_url=settings.shotspotter_api_url,
            api_key=settings.shotspotter_api_key,
            timeout=30.0,
        )

    @property
    def source(self) -> EventSource:
        """Get the event source."""
        return EventSource.SHOTSPOTTER

    async def health_check(self) -> bool:
        """
        Verify connectivity to ShotSpotter.

        Returns:
            bool: True if ShotSpotter is reachable
        """
        if not self.is_configured:
            return False

        try:
            # In production, this would call the ShotSpotter API
            return False
        except Exception as e:
            logger.warning("shotspotter_health_check_failed", error=str(e))
            return False

    async def normalize_event(self, raw_data: dict[str, Any]) -> ShotSpotterEvent:
        """
        Normalize ShotSpotter event to standard format.

        Args:
            raw_data: Raw event data from ShotSpotter

        Returns:
            ShotSpotterEvent: Normalized gunshot event
        """
        return ShotSpotterEvent(
            rounds_detected=raw_data.get("roundsDetected", 1),
            confidence=raw_data.get("confidence", 0.0),
            sensor_ids=raw_data.get("sensorIds", []),
            audio_url=raw_data.get("audioUrl"),
        )

    async def get_recent_alerts(self, hours: int = 24, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent gunshot alerts.

        Args:
            hours: Hours to look back
            limit: Maximum alerts to return

        Returns:
            list: Recent alerts
        """
        if not self.is_connected:
            return []

        # Placeholder - would call ShotSpotter API
        return []

    async def get_alert_details(self, alert_id: str) -> dict[str, Any] | None:
        """
        Get details for a specific alert.

        Args:
            alert_id: Alert identifier

        Returns:
            dict or None: Alert details
        """
        if not self.is_connected:
            return None

        # Placeholder - would call ShotSpotter API
        return None

    async def get_audio_clip(self, alert_id: str) -> str | None:
        """
        Get audio clip URL for an alert.

        Args:
            alert_id: Alert identifier

        Returns:
            str or None: Audio clip URL
        """
        if not self.is_connected:
            return None

        # Placeholder - would call ShotSpotter API
        return None

    async def acknowledge_alert(
        self, alert_id: str, user_id: str, notes: str | None = None
    ) -> bool:
        """
        Acknowledge a gunshot alert.

        Args:
            alert_id: Alert identifier
            user_id: User acknowledging
            notes: Optional notes

        Returns:
            bool: True if acknowledged successfully
        """
        if not self.is_connected:
            return False

        # Placeholder - would call ShotSpotter API
        return False


# Global instance
_shotspotter_integration: ShotSpotterIntegration | None = None


def get_shotspotter_integration() -> ShotSpotterIntegration:
    """Get the ShotSpotter integration instance."""
    global _shotspotter_integration
    if _shotspotter_integration is None:
        _shotspotter_integration = ShotSpotterIntegration()
    return _shotspotter_integration
