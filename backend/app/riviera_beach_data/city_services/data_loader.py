"""
City Services Data Loader for Riviera Beach.

Coordinates loading of all city service data.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.city_services.trash_pickup import TrashPickupService
from app.riviera_beach_data.city_services.stormwater import StormwaterService
from app.riviera_beach_data.city_services.streetlights import StreetlightService

logger = get_logger(__name__)


class CityServicesDataLoader:
    """Coordinates loading of all city service data for Riviera Beach."""
    
    def __init__(self) -> None:
        """Initialize the City Services Data Loader."""
        self.trash_service = TrashPickupService()
        self.stormwater_service = StormwaterService()
        self.streetlight_service = StreetlightService()
        self._loaded = False
    
    async def load_all(self) -> dict[str, Any]:
        """Load all city service data."""
        logger.info("city_services_data_loader_starting", city="Riviera Beach")
        
        results = {
            "loaded": [],
            "failed": [],
            "total_features": 0,
            "loaded_at": datetime.now(UTC).isoformat()
        }
        
        try:
            trash_data = await self.trash_service.load_pickup_zones()
            results["loaded"].append("trash_pickup")
            results["total_features"] += len(trash_data.get("features", []))
        except Exception as e:
            results["failed"].append({"type": "trash_pickup", "error": str(e)})
        
        try:
            stormwater_data = await self.stormwater_service.load_infrastructure()
            results["loaded"].append("stormwater")
            results["total_features"] += len(stormwater_data.get("features", []))
        except Exception as e:
            results["failed"].append({"type": "stormwater", "error": str(e)})
        
        try:
            streetlight_data = await self.streetlight_service.load_streetlights()
            results["loaded"].append("streetlights")
            results["total_features"] += len(streetlight_data.get("features", []))
        except Exception as e:
            results["failed"].append({"type": "streetlights", "error": str(e)})
        
        self._loaded = True
        return results
    
    def get_all_geojson(self) -> dict[str, Any]:
        """Get all city service data as GeoJSON."""
        features = []
        features.extend(self.trash_service.get_zones_geojson().get("features", []))
        features.extend(self.stormwater_service.get_infrastructure_geojson().get("features", []))
        features.extend(self.streetlight_service.get_streetlights_geojson().get("features", []))
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "City of Riviera Beach Public Works",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all city service data."""
        return {
            "city": "Riviera Beach",
            "loaded": self._loaded,
            "trash_pickup": self.trash_service.get_summary(),
            "stormwater": self.stormwater_service.get_summary(),
            "streetlights": self.streetlight_service.get_summary()
        }
