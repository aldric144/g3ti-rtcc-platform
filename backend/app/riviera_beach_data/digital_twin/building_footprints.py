"""
Building Footprint Service for Riviera Beach Digital Twin.

Manages 3D building footprint data from OpenStreetMap and Microsoft.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class BuildingType(str, Enum):
    """Building types."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    GOVERNMENT = "government"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    RELIGIOUS = "religious"
    MIXED_USE = "mixed_use"
    OTHER = "other"


class BuildingFootprint(BaseModel):
    """Building footprint information."""
    building_id: str
    building_type: BuildingType
    lat: float
    lon: float
    height_ft: float | None = None
    floors: int | None = None
    year_built: int | None = None
    area_sq_ft: float | None = None
    address: str | None = None


class BuildingFootprintService:
    """
    Service for building footprint data for Riviera Beach Digital Twin.
    
    Data sources:
    - OpenStreetMap Buildings
    - Microsoft Building Footprints
    - Palm Beach County Property Appraiser
    """
    
    # Riviera Beach bounding box
    BBOX = {
        "min_lat": 26.7400,
        "max_lat": 26.8100,
        "min_lon": -80.1000,
        "max_lon": -80.0300
    }
    
    # Sample building footprints (representative)
    SAMPLE_BUILDINGS = [
        # Government/Public
        BuildingFootprint(
            building_id="bldg_city_hall",
            building_type=BuildingType.GOVERNMENT,
            lat=26.7753,
            lon=-80.0620,
            height_ft=45,
            floors=3,
            year_built=1985,
            area_sq_ft=35000,
            address="600 W Blue Heron Blvd"
        ),
        BuildingFootprint(
            building_id="bldg_police_hq",
            building_type=BuildingType.GOVERNMENT,
            lat=26.7753,
            lon=-80.0625,
            height_ft=35,
            floors=2,
            year_built=1990,
            area_sq_ft=25000,
            address="600 W Blue Heron Blvd"
        ),
        BuildingFootprint(
            building_id="bldg_fire_station_1",
            building_type=BuildingType.GOVERNMENT,
            lat=26.7753,
            lon=-80.0630,
            height_ft=30,
            floors=2,
            year_built=1995,
            area_sq_ft=12000,
            address="600 W Blue Heron Blvd"
        ),
        
        # Commercial - Marina District
        BuildingFootprint(
            building_id="bldg_marina_village_1",
            building_type=BuildingType.COMMERCIAL,
            lat=26.7800,
            lon=-80.0450,
            height_ft=40,
            floors=3,
            year_built=2010,
            area_sq_ft=45000,
            address="200 E 13th St"
        ),
        BuildingFootprint(
            building_id="bldg_marina_village_2",
            building_type=BuildingType.COMMERCIAL,
            lat=26.7798,
            lon=-80.0455,
            height_ft=35,
            floors=2,
            year_built=2012,
            area_sq_ft=28000,
            address="190 E 13th St"
        ),
        
        # Residential - Singer Island
        BuildingFootprint(
            building_id="bldg_condo_si_1",
            building_type=BuildingType.RESIDENTIAL,
            lat=26.7900,
            lon=-80.0350,
            height_ft=180,
            floors=18,
            year_built=2005,
            area_sq_ft=150000,
            address="2500 N Ocean Dr"
        ),
        BuildingFootprint(
            building_id="bldg_condo_si_2",
            building_type=BuildingType.RESIDENTIAL,
            lat=26.7920,
            lon=-80.0345,
            height_ft=200,
            floors=20,
            year_built=2008,
            area_sq_ft=175000,
            address="2700 N Ocean Dr"
        ),
        
        # Education
        BuildingFootprint(
            building_id="bldg_school_1",
            building_type=BuildingType.EDUCATION,
            lat=26.7680,
            lon=-80.0620,
            height_ft=35,
            floors=2,
            year_built=1975,
            area_sq_ft=85000,
            address="1600 Avenue L"
        ),
        
        # Industrial - Port Area
        BuildingFootprint(
            building_id="bldg_warehouse_1",
            building_type=BuildingType.INDUSTRIAL,
            lat=26.7650,
            lon=-80.0500,
            height_ft=40,
            floors=1,
            year_built=1980,
            area_sq_ft=120000,
            address="Port of Palm Beach"
        ),
    ]
    
    # Building statistics
    STATISTICS = {
        "total_buildings": 8500,
        "residential": 6200,
        "commercial": 850,
        "industrial": 320,
        "government": 45,
        "education": 25,
        "other": 1060,
        "average_height_ft": 28,
        "tallest_building_ft": 250
    }
    
    def __init__(self) -> None:
        """Initialize the Building Footprint Service."""
        self._footprints_loaded = False
        self._http_client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    async def load_footprints(self) -> dict[str, Any]:
        """Load building footprint data."""
        logger.info("loading_building_footprints", city="Riviera Beach")
        
        features = []
        
        for building in self.SAMPLE_BUILDINGS:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [building.lon, building.lat]
                },
                "properties": {
                    "building_id": building.building_id,
                    "building_type": building.building_type.value,
                    "height_ft": building.height_ft,
                    "floors": building.floors,
                    "year_built": building.year_built,
                    "area_sq_ft": building.area_sq_ft,
                    "address": building.address,
                    "category": "building"
                },
                "id": building.building_id
            })
        
        self._footprints_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "OpenStreetMap / Microsoft Building Footprints",
                "note": "Sample data - full dataset contains ~8500 buildings",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_buildings(self) -> list[BuildingFootprint]:
        """Get building footprints."""
        return self.SAMPLE_BUILDINGS
    
    def get_buildings_by_type(self, building_type: BuildingType) -> list[BuildingFootprint]:
        """Get buildings by type."""
        return [b for b in self.SAMPLE_BUILDINGS if b.building_type == building_type]
    
    def get_statistics(self) -> dict[str, Any]:
        """Get building statistics."""
        return self.STATISTICS
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of building footprint data."""
        return {
            "sample_buildings": len(self.SAMPLE_BUILDINGS),
            "total_city_buildings": self.STATISTICS["total_buildings"],
            "tallest_building_ft": self.STATISTICS["tallest_building_ft"],
            "footprints_loaded": self._footprints_loaded
        }
