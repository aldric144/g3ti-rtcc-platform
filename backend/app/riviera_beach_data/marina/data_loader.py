"""
Marina Data Loader for Riviera Beach.

Coordinates loading of all marina and waterway data.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.marina.marina_layout import MarinaLayoutService
from app.riviera_beach_data.marina.waterways import WaterwayService
from app.riviera_beach_data.marina.marine_traffic import MarineTrafficService

logger = get_logger(__name__)


class MarinaDataLoader:
    """Coordinates loading of all marina and waterway data for Riviera Beach."""
    
    def __init__(self) -> None:
        """Initialize the Marina Data Loader."""
        self.marina_service = MarinaLayoutService()
        self.waterway_service = WaterwayService()
        self.traffic_service = MarineTrafficService()
        self._loaded = False
    
    async def load_all(self) -> dict[str, Any]:
        """Load all marina and waterway data."""
        logger.info("marina_data_loader_starting", city="Riviera Beach")
        
        results = {
            "loaded": [],
            "failed": [],
            "total_features": 0,
            "loaded_at": datetime.now(UTC).isoformat()
        }
        
        try:
            marina_data = await self.marina_service.load_marina_data()
            results["loaded"].append("marina")
            results["total_features"] += len(marina_data.get("features", []))
        except Exception as e:
            results["failed"].append({"type": "marina", "error": str(e)})
        
        try:
            waterway_data = await self.waterway_service.load_waterways()
            results["loaded"].append("waterways")
            results["total_features"] += len(waterway_data.get("features", []))
        except Exception as e:
            results["failed"].append({"type": "waterways", "error": str(e)})
        
        try:
            traffic_data = await self.traffic_service.load_traffic_data()
            results["loaded"].append("marine_traffic")
            results["total_features"] += len(traffic_data.get("vessels", []))
        except Exception as e:
            results["failed"].append({"type": "marine_traffic", "error": str(e)})
        
        self._loaded = True
        return results
    
    def get_all_geojson(self) -> dict[str, Any]:
        """Get all marina data as GeoJSON."""
        features = []
        features.extend(self.marina_service.get_marina_geojson().get("features", []))
        features.extend(self.waterway_service.get_waterways_geojson().get("features", []))
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Riviera Beach Marina & Waterway Data",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all marina data."""
        return {
            "city": "Riviera Beach",
            "loaded": self._loaded,
            "marina": self.marina_service.get_summary(),
            "waterways": self.waterway_service.get_summary(),
            "marine_traffic": self.traffic_service.get_summary()
        }
