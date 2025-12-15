"""
Environmental Data Loader for Riviera Beach.

Coordinates loading of all environmental and emergency data.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.environmental.noaa_weather import NOAAWeatherService
from app.riviera_beach_data.environmental.nws_alerts import NWSAlertService
from app.riviera_beach_data.environmental.tide_charts import TideChartService

logger = get_logger(__name__)


class EnvironmentalDataLoader:
    """Coordinates loading of all environmental data for Riviera Beach."""
    
    def __init__(self) -> None:
        """Initialize the Environmental Data Loader."""
        self.weather_service = NOAAWeatherService()
        self.alert_service = NWSAlertService()
        self.tide_service = TideChartService()
        self._loaded = False
    
    async def load_all(self) -> dict[str, Any]:
        """Load all environmental data."""
        logger.info("environmental_data_loader_starting", city="Riviera Beach")
        
        results = {
            "loaded": [],
            "failed": [],
            "total_records": 0,
            "loaded_at": datetime.now(UTC).isoformat()
        }
        
        try:
            weather_data = await self.weather_service.load_weather_data()
            results["loaded"].append("weather")
            results["total_records"] += 1
        except Exception as e:
            results["failed"].append({"type": "weather", "error": str(e)})
        
        try:
            alert_data = await self.alert_service.load_alerts()
            results["loaded"].append("alerts")
            results["total_records"] += len(alert_data.get("alerts", []))
        except Exception as e:
            results["failed"].append({"type": "alerts", "error": str(e)})
        
        try:
            tide_data = await self.tide_service.load_tide_data()
            results["loaded"].append("tides")
            results["total_records"] += len(tide_data.get("predictions", []))
        except Exception as e:
            results["failed"].append({"type": "tides", "error": str(e)})
        
        self._loaded = True
        return results
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all environmental data."""
        return {
            "city": "Riviera Beach",
            "loaded": self._loaded,
            "weather": self.weather_service.get_summary(),
            "alerts": self.alert_service.get_summary(),
            "tides": self.tide_service.get_summary()
        }
