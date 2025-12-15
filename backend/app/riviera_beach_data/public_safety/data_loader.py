"""
Public Safety Data Loader for Riviera Beach.

Coordinates loading of all public safety infrastructure data.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.public_safety.fire_stations import FireStationService
from app.riviera_beach_data.public_safety.hydrants import HydrantService
from app.riviera_beach_data.public_safety.police_locations import PoliceLocationService

logger = get_logger(__name__)


class PublicSafetyDataLoader:
    """
    Coordinates loading of all public safety data for Riviera Beach.
    
    Loads:
    - Police facility locations (public only)
    - Fire station locations and apparatus
    - Fire hydrant locations
    - Response district boundaries
    """
    
    def __init__(self) -> None:
        """Initialize the Public Safety Data Loader."""
        self.police_service = PoliceLocationService()
        self.fire_service = FireStationService()
        self.hydrant_service = HydrantService()
        self._loaded = False
    
    async def load_all(self) -> dict[str, Any]:
        """
        Load all public safety data.
        
        Returns:
            dict: Summary of loaded data
        """
        logger.info("public_safety_data_loader_starting", city="Riviera Beach")
        
        results = {
            "loaded": [],
            "failed": [],
            "total_features": 0,
            "loaded_at": datetime.now(UTC).isoformat()
        }
        
        # Load police locations
        try:
            police_data = await self.police_service.load_locations()
            results["loaded"].append("police_locations")
            results["total_features"] += len(police_data.get("features", []))
            logger.info("police_locations_loaded", count=len(police_data.get("features", [])))
        except Exception as e:
            results["failed"].append({"type": "police_locations", "error": str(e)})
            logger.warning("police_locations_load_failed", error=str(e))
        
        # Load fire stations
        try:
            fire_data = await self.fire_service.load_stations()
            results["loaded"].append("fire_stations")
            results["total_features"] += len(fire_data.get("features", []))
            logger.info("fire_stations_loaded", count=len(fire_data.get("features", [])))
        except Exception as e:
            results["failed"].append({"type": "fire_stations", "error": str(e)})
            logger.warning("fire_stations_load_failed", error=str(e))
        
        # Load hydrants
        try:
            hydrant_data = await self.hydrant_service.load_hydrants()
            results["loaded"].append("hydrants")
            results["total_features"] += len(hydrant_data.get("features", []))
            logger.info("hydrants_loaded", count=len(hydrant_data.get("features", [])))
        except Exception as e:
            results["failed"].append({"type": "hydrants", "error": str(e)})
            logger.warning("hydrants_load_failed", error=str(e))
        
        self._loaded = True
        
        logger.info(
            "public_safety_data_loader_complete",
            loaded_count=len(results["loaded"]),
            failed_count=len(results["failed"]),
            total_features=results["total_features"]
        )
        
        return results
    
    def get_all_geojson(self) -> dict[str, Any]:
        """
        Get all public safety data as GeoJSON.
        
        Returns:
            dict: Combined GeoJSON feature collection
        """
        features = []
        
        # Add police locations
        police_geojson = self.police_service.get_locations_geojson()
        features.extend(police_geojson.get("features", []))
        
        # Add fire stations
        fire_geojson = self.fire_service.get_stations_geojson()
        features.extend(fire_geojson.get("features", []))
        
        # Add hydrants
        hydrant_geojson = self.hydrant_service.get_hydrants_geojson()
        features.extend(hydrant_geojson.get("features", []))
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Riviera Beach Public Safety Data",
                "categories": ["police", "fire", "hydrants"],
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all public safety data."""
        return {
            "city": "Riviera Beach",
            "loaded": self._loaded,
            "police": self.police_service.get_summary(),
            "fire": self.fire_service.get_summary(),
            "hydrants": self.hydrant_service.get_summary()
        }
