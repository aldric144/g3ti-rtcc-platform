"""
NWS Alert Service for Riviera Beach.

Manages National Weather Service alerts and warnings.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    EXTREME = "Extreme"
    SEVERE = "Severe"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


class AlertType(str, Enum):
    """Alert types."""
    HURRICANE_WARNING = "Hurricane Warning"
    HURRICANE_WATCH = "Hurricane Watch"
    TROPICAL_STORM_WARNING = "Tropical Storm Warning"
    TROPICAL_STORM_WATCH = "Tropical Storm Watch"
    TORNADO_WARNING = "Tornado Warning"
    TORNADO_WATCH = "Tornado Watch"
    SEVERE_THUNDERSTORM_WARNING = "Severe Thunderstorm Warning"
    FLOOD_WARNING = "Flood Warning"
    FLOOD_WATCH = "Flood Watch"
    COASTAL_FLOOD_WARNING = "Coastal Flood Warning"
    RIP_CURRENT_STATEMENT = "Rip Current Statement"
    HEAT_ADVISORY = "Heat Advisory"
    EXCESSIVE_HEAT_WARNING = "Excessive Heat Warning"
    FIRE_WEATHER_WATCH = "Fire Weather Watch"
    RED_FLAG_WARNING = "Red Flag Warning"
    BEACH_HAZARDS_STATEMENT = "Beach Hazards Statement"
    SPECIAL_WEATHER_STATEMENT = "Special Weather Statement"


class WeatherAlert(BaseModel):
    """Weather alert information."""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    headline: str
    description: str
    instruction: str | None = None
    effective: datetime
    expires: datetime
    areas_affected: list[str] = Field(default_factory=list)
    source: str = "NWS Miami"


class NWSAlertService:
    """
    Service for NWS weather alerts for Riviera Beach.
    
    Data source: NWS Alerts API
    """
    
    # NWS Alerts API
    NWS_ALERTS_API = "https://api.weather.gov/alerts/active"
    
    # Palm Beach County zone
    ZONE = "FLZ068"  # Palm Beach County
    
    # Riviera Beach coordinates
    LAT = 26.7753
    LON = -80.0583
    
    def __init__(self) -> None:
        """Initialize the NWS Alert Service."""
        self._alerts_loaded = False
        self._active_alerts: list[WeatherAlert] = []
        self._http_client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": "G3TI-RTCC-Platform/1.0"}
            )
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    async def load_alerts(self) -> dict[str, Any]:
        """Load active weather alerts."""
        logger.info("loading_nws_alerts", city="Riviera Beach")
        
        try:
            client = await self._get_client()
            
            # Get alerts for Palm Beach County zone
            response = await client.get(
                self.NWS_ALERTS_API,
                params={"zone": self.ZONE}
            )
            
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                
                self._active_alerts = []
                for feature in features:
                    props = feature.get("properties", {})
                    
                    self._active_alerts.append(WeatherAlert(
                        alert_id=props.get("id", ""),
                        alert_type=props.get("event", "Unknown"),
                        severity=AlertSeverity(props.get("severity", "Unknown")),
                        headline=props.get("headline", ""),
                        description=props.get("description", ""),
                        instruction=props.get("instruction"),
                        effective=datetime.fromisoformat(props.get("effective", datetime.now(UTC).isoformat()).replace("Z", "+00:00")),
                        expires=datetime.fromisoformat(props.get("expires", datetime.now(UTC).isoformat()).replace("Z", "+00:00")),
                        areas_affected=props.get("areaDesc", "").split("; "),
                        source=props.get("senderName", "NWS Miami")
                    ))
                
                logger.info("nws_alerts_loaded", count=len(self._active_alerts))
        except Exception as e:
            logger.warning("nws_alerts_api_failed", error=str(e))
            self._active_alerts = []
        
        self._alerts_loaded = True
        
        return {
            "alerts": [a.model_dump() for a in self._active_alerts],
            "metadata": {
                "source": "NWS Alerts API",
                "zone": self.ZONE,
                "location": "Palm Beach County, FL",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_active_alerts(self) -> list[WeatherAlert]:
        """Get active weather alerts."""
        return self._active_alerts
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> list[WeatherAlert]:
        """Get alerts by severity."""
        return [a for a in self._active_alerts if a.severity == severity]
    
    def get_hurricane_alerts(self) -> list[WeatherAlert]:
        """Get hurricane-related alerts."""
        hurricane_types = ["Hurricane", "Tropical Storm"]
        return [
            a for a in self._active_alerts
            if any(ht in a.alert_type for ht in hurricane_types)
        ]
    
    def has_active_alerts(self) -> bool:
        """Check if there are active alerts."""
        return len(self._active_alerts) > 0
    
    def get_highest_severity(self) -> AlertSeverity | None:
        """Get highest severity among active alerts."""
        if not self._active_alerts:
            return None
        
        severity_order = [
            AlertSeverity.EXTREME,
            AlertSeverity.SEVERE,
            AlertSeverity.MODERATE,
            AlertSeverity.MINOR
        ]
        
        for severity in severity_order:
            if any(a.severity == severity for a in self._active_alerts):
                return severity
        
        return AlertSeverity.UNKNOWN
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of alert data."""
        return {
            "location": "Palm Beach County, FL",
            "active_alerts": len(self._active_alerts),
            "highest_severity": self.get_highest_severity().value if self.get_highest_severity() else None,
            "has_hurricane_alerts": len(self.get_hurricane_alerts()) > 0,
            "alerts_loaded": self._alerts_loaded
        }
