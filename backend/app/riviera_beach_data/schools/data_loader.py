"""
School Data Loader for Riviera Beach.

Coordinates loading of all school and youth infrastructure data.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.schools.school_locations import SchoolLocationService
from app.riviera_beach_data.schools.youth_facilities import YouthFacilityService

logger = get_logger(__name__)


class SchoolDataLoader:
    """
    Coordinates loading of all school and youth data for Riviera Beach.
    """
    
    def __init__(self) -> None:
        """Initialize the School Data Loader."""
        self.school_service = SchoolLocationService()
        self.youth_service = YouthFacilityService()
        self._loaded = False
    
    async def load_all(self) -> dict[str, Any]:
        """Load all school and youth data."""
        logger.info("school_data_loader_starting", city="Riviera Beach")
        
        results = {
            "loaded": [],
            "failed": [],
            "total_features": 0,
            "loaded_at": datetime.now(UTC).isoformat()
        }
        
        try:
            school_data = await self.school_service.load_schools()
            results["loaded"].append("schools")
            results["total_features"] += len(school_data.get("features", []))
        except Exception as e:
            results["failed"].append({"type": "schools", "error": str(e)})
        
        try:
            youth_data = await self.youth_service.load_facilities()
            results["loaded"].append("youth_facilities")
            results["total_features"] += len(youth_data.get("features", []))
        except Exception as e:
            results["failed"].append({"type": "youth_facilities", "error": str(e)})
        
        self._loaded = True
        return results
    
    def get_all_geojson(self) -> dict[str, Any]:
        """Get all school and youth data as GeoJSON."""
        features = []
        features.extend(self.school_service.get_schools_geojson().get("features", []))
        features.extend(self.youth_service.get_facilities_geojson().get("features", []))
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Riviera Beach Schools & Youth Data",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all school and youth data."""
        return {
            "city": "Riviera Beach",
            "loaded": self._loaded,
            "schools": self.school_service.get_summary(),
            "youth_facilities": self.youth_service.get_summary()
        }
