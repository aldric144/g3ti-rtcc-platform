"""
City Boundary Service for Riviera Beach.

Provides access to city boundary data and spatial queries.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.riviera_beach_data.gis.boundary_loader import (
    BoundaryType,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GISBoundaryLoader,
)

logger = get_logger(__name__)


class CityBoundaryInfo(BaseModel):
    """City boundary information."""
    city_name: str = "Riviera Beach"
    state: str = "Florida"
    county: str = "Palm Beach"
    zip_code: str = "33404"
    fips_state: str = "12"
    fips_county: str = "099"
    population_estimate: int = 37964
    area_sq_miles: float = 9.5
    incorporated_year: str = "1922"
    center_lat: float = 26.7753
    center_lon: float = -80.0583
    bounding_box: dict[str, float] = Field(default_factory=lambda: {
        "min_lat": 26.7400,
        "max_lat": 26.8100,
        "min_lon": -80.1000,
        "max_lon": -80.0300
    })


class CityBoundaryService:
    """
    Service for managing Riviera Beach city boundary data.
    
    Provides:
    - City boundary polygon access
    - Point-in-boundary checks
    - Boundary metadata
    - Neighboring municipality info
    """
    
    def __init__(self, boundary_loader: GISBoundaryLoader | None = None) -> None:
        """Initialize the City Boundary Service."""
        self._loader = boundary_loader or GISBoundaryLoader()
        self._boundary: GeoJSONFeatureCollection | None = None
        self._info = CityBoundaryInfo()
    
    async def load_boundary(self) -> GeoJSONFeatureCollection:
        """
        Load the city boundary data.
        
        Returns:
            GeoJSONFeatureCollection: City boundary polygon
        """
        if self._boundary is None:
            self._boundary = await self._loader.load_city_boundary()
            logger.info(
                "city_boundary_loaded",
                city="Riviera Beach",
                feature_count=len(self._boundary.features)
            )
        return self._boundary
    
    def get_boundary(self) -> GeoJSONFeatureCollection | None:
        """Get the loaded city boundary."""
        return self._boundary
    
    def get_info(self) -> CityBoundaryInfo:
        """Get city boundary information."""
        return self._info
    
    def point_in_city(self, lat: float, lon: float) -> bool:
        """
        Check if a point is within the city boundary.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            bool: True if point is within city boundary
        """
        # Simple bounding box check (for full polygon check, use shapely)
        bbox = self._info.bounding_box
        return (
            bbox["min_lat"] <= lat <= bbox["max_lat"] and
            bbox["min_lon"] <= lon <= bbox["max_lon"]
        )
    
    def get_neighboring_municipalities(self) -> list[dict[str, Any]]:
        """
        Get information about neighboring municipalities.
        
        Returns:
            list: Neighboring municipality information
        """
        return [
            {
                "name": "West Palm Beach",
                "direction": "south",
                "shared_boundary": True,
                "population": 117415
            },
            {
                "name": "Palm Beach Gardens",
                "direction": "north",
                "shared_boundary": True,
                "population": 56502
            },
            {
                "name": "Lake Park",
                "direction": "northwest",
                "shared_boundary": True,
                "population": 8457
            },
            {
                "name": "Palm Beach Shores",
                "direction": "east",
                "shared_boundary": True,
                "population": 1142
            },
            {
                "name": "Singer Island",
                "direction": "east",
                "shared_boundary": True,
                "note": "Part of Riviera Beach"
            }
        ]
    
    def get_boundary_geojson(self) -> dict[str, Any]:
        """
        Get city boundary as GeoJSON dict.
        
        Returns:
            dict: GeoJSON representation
        """
        if self._boundary:
            return self._boundary.model_dump()
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {"error": "Boundary not loaded"}
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of city boundary data."""
        return {
            "city": self._info.city_name,
            "state": self._info.state,
            "county": self._info.county,
            "zip_code": self._info.zip_code,
            "population": self._info.population_estimate,
            "area_sq_miles": self._info.area_sq_miles,
            "center": {
                "lat": self._info.center_lat,
                "lon": self._info.center_lon
            },
            "bounding_box": self._info.bounding_box,
            "boundary_loaded": self._boundary is not None,
            "feature_count": len(self._boundary.features) if self._boundary else 0
        }
