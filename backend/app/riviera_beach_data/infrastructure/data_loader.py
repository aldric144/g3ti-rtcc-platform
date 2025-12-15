"""
Infrastructure Data Loader for Riviera Beach.

Coordinates loading of all critical infrastructure data.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.infrastructure.utilities import UtilityService
from app.riviera_beach_data.infrastructure.transportation import TransportationService
from app.riviera_beach_data.infrastructure.hazard_zones import HazardZoneService

logger = get_logger(__name__)


class InfrastructureDataLoader:
    """
    Coordinates loading of all critical infrastructure data for Riviera Beach.
    
    Loads:
    - Utility infrastructure (water, power, communications)
    - Transportation infrastructure (roads, bridges, transit)
    - Hazard zones (flood, storm surge, evacuation)
    """
    
    def __init__(self) -> None:
        """Initialize the Infrastructure Data Loader."""
        self.utility_service = UtilityService()
        self.transportation_service = TransportationService()
        self.hazard_service = HazardZoneService()
        self._loaded = False
    
    async def load_all(self) -> dict[str, Any]:
        """
        Load all infrastructure data.
        
        Returns:
            dict: Summary of loaded data
        """
        logger.info("infrastructure_data_loader_starting", city="Riviera Beach")
        
        results = {
            "loaded": [],
            "failed": [],
            "total_features": 0,
            "loaded_at": datetime.now(UTC).isoformat()
        }
        
        # Load utilities
        try:
            utility_data = await self.utility_service.load_utilities()
            results["loaded"].append("utilities")
            results["total_features"] += len(utility_data.get("features", []))
            logger.info("utilities_loaded", count=len(utility_data.get("features", [])))
        except Exception as e:
            results["failed"].append({"type": "utilities", "error": str(e)})
            logger.warning("utilities_load_failed", error=str(e))
        
        # Load transportation
        try:
            transport_data = await self.transportation_service.load_transportation()
            results["loaded"].append("transportation")
            results["total_features"] += len(transport_data.get("features", []))
            logger.info("transportation_loaded", count=len(transport_data.get("features", [])))
        except Exception as e:
            results["failed"].append({"type": "transportation", "error": str(e)})
            logger.warning("transportation_load_failed", error=str(e))
        
        # Load hazard zones
        try:
            hazard_data = await self.hazard_service.load_hazard_zones()
            results["loaded"].append("hazard_zones")
            results["total_features"] += len(hazard_data.get("features", []))
            logger.info("hazard_zones_loaded", count=len(hazard_data.get("features", [])))
        except Exception as e:
            results["failed"].append({"type": "hazard_zones", "error": str(e)})
            logger.warning("hazard_zones_load_failed", error=str(e))
        
        self._loaded = True
        
        logger.info(
            "infrastructure_data_loader_complete",
            loaded_count=len(results["loaded"]),
            failed_count=len(results["failed"]),
            total_features=results["total_features"]
        )
        
        return results
    
    def get_all_geojson(self) -> dict[str, Any]:
        """
        Get all infrastructure data as GeoJSON.
        
        Returns:
            dict: Combined GeoJSON feature collection
        """
        features = []
        
        # Add utilities
        utility_geojson = self.utility_service.get_utilities_geojson()
        features.extend(utility_geojson.get("features", []))
        
        # Add transportation
        transport_geojson = self.transportation_service.get_transportation_geojson()
        features.extend(transport_geojson.get("features", []))
        
        # Add hazard zones
        hazard_geojson = self.hazard_service.get_hazard_zones_geojson()
        features.extend(hazard_geojson.get("features", []))
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Riviera Beach Critical Infrastructure Data",
                "categories": ["utilities", "transportation", "hazard_zones"],
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all infrastructure data."""
        return {
            "city": "Riviera Beach",
            "loaded": self._loaded,
            "utilities": self.utility_service.get_summary(),
            "transportation": self.transportation_service.get_summary(),
            "hazard_zones": self.hazard_service.get_summary()
        }
