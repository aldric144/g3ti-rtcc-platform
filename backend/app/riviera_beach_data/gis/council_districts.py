"""
Council District Service for Riviera Beach.

Manages council district boundary data and lookups.
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


class CouncilMember(BaseModel):
    """Council member information."""
    district: int
    name: str
    title: str
    term_start: str | None = None
    term_end: str | None = None
    email: str | None = None
    phone: str | None = None


class CouncilDistrictInfo(BaseModel):
    """Council district information."""
    district_number: int
    district_name: str
    area_description: str
    population_estimate: int | None = None
    neighborhoods: list[str] = Field(default_factory=list)


class CouncilDistrictService:
    """
    Service for managing Riviera Beach council district data.
    
    Provides:
    - Council district boundary access
    - District lookup by location
    - Council member information
    - District statistics
    """
    
    # Riviera Beach City Council information (public data)
    COUNCIL_INFO = {
        "mayor": {
            "title": "Mayor",
            "note": "Elected at-large"
        },
        "total_districts": 5,
        "election_cycle": "4 years",
        "city_hall_address": "600 W Blue Heron Blvd, Riviera Beach, FL 33404"
    }
    
    DISTRICT_INFO = [
        CouncilDistrictInfo(
            district_number=1,
            district_name="District 1 - Northwest",
            area_description="Northwest section of Riviera Beach",
            population_estimate=7500,
            neighborhoods=["Northwest Neighborhood", "Industrial Area"]
        ),
        CouncilDistrictInfo(
            district_number=2,
            district_name="District 2 - Northeast",
            area_description="Northeast section including waterfront",
            population_estimate=7800,
            neighborhoods=["Northeast Neighborhood", "Waterfront Area"]
        ),
        CouncilDistrictInfo(
            district_number=3,
            district_name="District 3 - Central",
            area_description="Central business district and downtown",
            population_estimate=8200,
            neighborhoods=["Downtown", "Central Business District", "Marina District"]
        ),
        CouncilDistrictInfo(
            district_number=4,
            district_name="District 4 - Southwest",
            area_description="Southwest residential area",
            population_estimate=7200,
            neighborhoods=["Southwest Neighborhood", "Residential West"]
        ),
        CouncilDistrictInfo(
            district_number=5,
            district_name="District 5 - Southeast",
            area_description="Southeast section including Singer Island",
            population_estimate=7264,
            neighborhoods=["Singer Island", "Southeast Neighborhood", "Beach Area"]
        ),
    ]
    
    def __init__(self, boundary_loader: GISBoundaryLoader | None = None) -> None:
        """Initialize the Council District Service."""
        self._loader = boundary_loader or GISBoundaryLoader()
        self._districts: GeoJSONFeatureCollection | None = None
    
    async def load_districts(self) -> GeoJSONFeatureCollection:
        """
        Load council district boundaries.
        
        Returns:
            GeoJSONFeatureCollection: District boundary polygons
        """
        if self._districts is None:
            self._districts = await self._loader.load_council_districts()
            logger.info(
                "council_districts_loaded",
                city="Riviera Beach",
                district_count=len(self._districts.features)
            )
        return self._districts
    
    def get_districts(self) -> GeoJSONFeatureCollection | None:
        """Get loaded district boundaries."""
        return self._districts
    
    def get_district_by_number(self, district_number: int) -> CouncilDistrictInfo | None:
        """
        Get district information by number.
        
        Args:
            district_number: District number (1-5)
            
        Returns:
            CouncilDistrictInfo or None
        """
        for district in self.DISTRICT_INFO:
            if district.district_number == district_number:
                return district
        return None
    
    def get_district_by_location(self, lat: float, lon: float) -> int | None:
        """
        Get district number for a given location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            District number or None if outside city
        """
        # Simple grid-based lookup (approximate)
        # Riviera Beach bounding box
        min_lat, max_lat = 26.7400, 26.8100
        min_lon, max_lon = -80.1000, -80.0300
        
        if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
            return None
        
        # Divide into grid
        mid_lat = (min_lat + max_lat) / 2
        mid_lon = (min_lon + max_lon) / 2
        lower_mid_lat = min_lat + (max_lat - min_lat) * 0.35
        
        if lat > mid_lat:
            # Northern districts (1 or 2)
            if lon < mid_lon:
                return 1  # Northwest
            else:
                return 2  # Northeast
        elif lat > lower_mid_lat:
            return 3  # Central
        else:
            # Southern districts (4 or 5)
            if lon < mid_lon:
                return 4  # Southwest
            else:
                return 5  # Southeast
    
    def get_all_district_info(self) -> list[CouncilDistrictInfo]:
        """Get information for all districts."""
        return self.DISTRICT_INFO
    
    def get_council_info(self) -> dict[str, Any]:
        """Get general council information."""
        return self.COUNCIL_INFO
    
    def get_districts_geojson(self) -> dict[str, Any]:
        """
        Get district boundaries as GeoJSON dict.
        
        Returns:
            dict: GeoJSON representation
        """
        if self._districts:
            return self._districts.model_dump()
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {"error": "Districts not loaded"}
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of council district data."""
        return {
            "city": "Riviera Beach",
            "total_districts": self.COUNCIL_INFO["total_districts"],
            "districts_loaded": self._districts is not None,
            "feature_count": len(self._districts.features) if self._districts else 0,
            "districts": [
                {
                    "number": d.district_number,
                    "name": d.district_name,
                    "population": d.population_estimate
                }
                for d in self.DISTRICT_INFO
            ]
        }
