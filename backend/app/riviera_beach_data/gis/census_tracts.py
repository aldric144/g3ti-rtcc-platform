"""
Census Tract Service for Riviera Beach.

Manages census tract, block group, and block boundary data.
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


class CensusTractInfo(BaseModel):
    """Census tract information."""
    tract_id: str
    tract_name: str
    state_fips: str = "12"
    county_fips: str = "099"
    population: int | None = None
    housing_units: int | None = None
    land_area_sq_miles: float | None = None
    water_area_sq_miles: float | None = None


class CensusTractService:
    """
    Service for managing census tract data for Riviera Beach.
    
    Provides:
    - Census tract boundary access
    - Block group boundaries
    - Tract lookup by location
    - Demographic data integration
    """
    
    # Census tracts that cover Riviera Beach (2020 Census)
    RIVIERA_BEACH_TRACTS = [
        CensusTractInfo(
            tract_id="120990054.01",
            tract_name="Census Tract 54.01",
            population=3500,
            housing_units=1400,
            land_area_sq_miles=1.2
        ),
        CensusTractInfo(
            tract_id="120990054.02",
            tract_name="Census Tract 54.02",
            population=4200,
            housing_units=1700,
            land_area_sq_miles=1.1
        ),
        CensusTractInfo(
            tract_id="120990055.00",
            tract_name="Census Tract 55",
            population=3800,
            housing_units=1500,
            land_area_sq_miles=1.3
        ),
        CensusTractInfo(
            tract_id="120990056.01",
            tract_name="Census Tract 56.01",
            population=4100,
            housing_units=1650,
            land_area_sq_miles=1.0
        ),
        CensusTractInfo(
            tract_id="120990056.02",
            tract_name="Census Tract 56.02",
            population=3900,
            housing_units=1550,
            land_area_sq_miles=1.15
        ),
        CensusTractInfo(
            tract_id="120990057.00",
            tract_name="Census Tract 57",
            population=4500,
            housing_units=1800,
            land_area_sq_miles=1.25
        ),
        CensusTractInfo(
            tract_id="120990058.01",
            tract_name="Census Tract 58.01",
            population=3200,
            housing_units=1280,
            land_area_sq_miles=0.95
        ),
        CensusTractInfo(
            tract_id="120990058.02",
            tract_name="Census Tract 58.02",
            population=3700,
            housing_units=1480,
            land_area_sq_miles=1.05
        ),
    ]
    
    def __init__(self, boundary_loader: GISBoundaryLoader | None = None) -> None:
        """Initialize the Census Tract Service."""
        self._loader = boundary_loader or GISBoundaryLoader()
        self._tracts: GeoJSONFeatureCollection | None = None
        self._block_groups: GeoJSONFeatureCollection | None = None
    
    async def load_tracts(self) -> GeoJSONFeatureCollection:
        """
        Load census tract boundaries.
        
        Returns:
            GeoJSONFeatureCollection: Tract boundary polygons
        """
        if self._tracts is None:
            self._tracts = await self._loader.load_census_tracts()
            logger.info(
                "census_tracts_loaded",
                city="Riviera Beach",
                tract_count=len(self._tracts.features)
            )
        return self._tracts
    
    async def load_block_groups(self) -> GeoJSONFeatureCollection:
        """
        Load census block group boundaries.
        
        Returns:
            GeoJSONFeatureCollection: Block group boundary polygons
        """
        if self._block_groups is None:
            self._block_groups = await self._loader.load_census_block_groups()
            logger.info(
                "census_block_groups_loaded",
                city="Riviera Beach",
                block_group_count=len(self._block_groups.features)
            )
        return self._block_groups
    
    def get_tracts(self) -> GeoJSONFeatureCollection | None:
        """Get loaded tract boundaries."""
        return self._tracts
    
    def get_block_groups(self) -> GeoJSONFeatureCollection | None:
        """Get loaded block group boundaries."""
        return self._block_groups
    
    def get_tract_info(self, tract_id: str) -> CensusTractInfo | None:
        """
        Get tract information by ID.
        
        Args:
            tract_id: Census tract ID
            
        Returns:
            CensusTractInfo or None
        """
        for tract in self.RIVIERA_BEACH_TRACTS:
            if tract.tract_id == tract_id or tract_id in tract.tract_id:
                return tract
        return None
    
    def get_all_tract_info(self) -> list[CensusTractInfo]:
        """Get information for all tracts."""
        return self.RIVIERA_BEACH_TRACTS
    
    def get_total_population(self) -> int:
        """Get total population across all tracts."""
        return sum(t.population or 0 for t in self.RIVIERA_BEACH_TRACTS)
    
    def get_total_housing_units(self) -> int:
        """Get total housing units across all tracts."""
        return sum(t.housing_units or 0 for t in self.RIVIERA_BEACH_TRACTS)
    
    def get_tract_by_location(self, lat: float, lon: float) -> str | None:
        """
        Get tract ID for a given location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Tract ID or None if outside area
        """
        # Simple grid-based lookup (approximate)
        min_lat, max_lat = 26.7400, 26.8100
        min_lon, max_lon = -80.1000, -80.0300
        
        if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
            return None
        
        # Calculate grid position
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon
        
        row = int((lat - min_lat) / lat_range * 4)
        col = int((lon - min_lon) / lon_range * 2)
        
        index = min(row * 2 + col, len(self.RIVIERA_BEACH_TRACTS) - 1)
        return self.RIVIERA_BEACH_TRACTS[index].tract_id
    
    def get_tracts_geojson(self) -> dict[str, Any]:
        """
        Get tract boundaries as GeoJSON dict.
        
        Returns:
            dict: GeoJSON representation
        """
        if self._tracts:
            return self._tracts.model_dump()
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {"error": "Tracts not loaded"}
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of census tract data."""
        return {
            "city": "Riviera Beach",
            "state_fips": "12",
            "county_fips": "099",
            "total_tracts": len(self.RIVIERA_BEACH_TRACTS),
            "total_population": self.get_total_population(),
            "total_housing_units": self.get_total_housing_units(),
            "tracts_loaded": self._tracts is not None,
            "block_groups_loaded": self._block_groups is not None,
            "tract_feature_count": len(self._tracts.features) if self._tracts else 0,
            "tracts": [
                {
                    "id": t.tract_id,
                    "name": t.tract_name,
                    "population": t.population
                }
                for t in self.RIVIERA_BEACH_TRACTS
            ]
        }
