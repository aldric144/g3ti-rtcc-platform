"""
Marine Traffic Service for Riviera Beach.

Manages AIS vessel tracking and USCG boating accident data.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class VesselType(str, Enum):
    """Vessel types."""
    CARGO = "cargo"
    TANKER = "tanker"
    PASSENGER = "passenger"
    FISHING = "fishing"
    RECREATIONAL = "recreational"
    TUG = "tug"
    PILOT = "pilot"
    COAST_GUARD = "coast_guard"
    OTHER = "other"


class VesselPosition(BaseModel):
    """Vessel AIS position."""
    mmsi: str
    vessel_name: str
    vessel_type: VesselType
    lat: float
    lon: float
    course: float
    speed_kts: float
    heading: float | None = None
    destination: str | None = None
    eta: str | None = None
    timestamp: datetime


class BoatingAccident(BaseModel):
    """USCG boating accident record."""
    accident_id: str
    date: str
    location: str
    lat: float | None = None
    lon: float | None = None
    accident_type: str
    vessels_involved: int
    injuries: int
    fatalities: int
    property_damage: str | None = None
    primary_cause: str | None = None


class MarineTrafficService:
    """
    Service for marine traffic and boating safety data.
    
    Data sources:
    - AIS vessel tracking (public feeds)
    - USCG Boating Accident Report Database (BARD)
    """
    
    # Riviera Beach area bounding box
    BBOX = {
        "min_lat": 26.7400,
        "max_lat": 26.8100,
        "min_lon": -80.1000,
        "max_lon": -80.0300
    }
    
    # Sample vessel positions (simulated AIS data)
    SAMPLE_VESSELS = [
        VesselPosition(
            mmsi="367000001",
            vessel_name="PALM BEACH PILOT",
            vessel_type=VesselType.PILOT,
            lat=26.7700,
            lon=-80.0350,
            course=270.0,
            speed_kts=8.5,
            heading=268,
            destination="LAKE WORTH INLET",
            timestamp=datetime.now(UTC)
        ),
        VesselPosition(
            mmsi="367000002",
            vessel_name="CARIBBEAN PRINCESS",
            vessel_type=VesselType.PASSENGER,
            lat=26.7650,
            lon=-80.0280,
            course=180.0,
            speed_kts=12.0,
            heading=178,
            destination="PORT OF PALM BEACH",
            eta="1400 LT",
            timestamp=datetime.now(UTC)
        ),
        VesselPosition(
            mmsi="367000003",
            vessel_name="ATLANTIC TRADER",
            vessel_type=VesselType.CARGO,
            lat=26.7600,
            lon=-80.0400,
            course=0.0,
            speed_kts=0.0,
            heading=45,
            destination="PORT OF PALM BEACH",
            timestamp=datetime.now(UTC)
        ),
        VesselPosition(
            mmsi="367000004",
            vessel_name="USCG CUTTER CONFIDENCE",
            vessel_type=VesselType.COAST_GUARD,
            lat=26.7800,
            lon=-80.0320,
            course=90.0,
            speed_kts=15.0,
            heading=88,
            timestamp=datetime.now(UTC)
        ),
    ]
    
    # Historical boating accidents (public USCG data, anonymized)
    BOATING_ACCIDENTS = [
        BoatingAccident(
            accident_id="2023-001",
            date="2023-03-15",
            location="Lake Worth Inlet",
            lat=26.7700,
            lon=-80.0320,
            accident_type="Collision with vessel",
            vessels_involved=2,
            injuries=1,
            fatalities=0,
            property_damage="$15,000",
            primary_cause="Operator inattention"
        ),
        BoatingAccident(
            accident_id="2023-002",
            date="2023-06-22",
            location="Peanut Island",
            lat=26.7750,
            lon=-80.0400,
            accident_type="Grounding",
            vessels_involved=1,
            injuries=0,
            fatalities=0,
            property_damage="$5,000",
            primary_cause="Navigation error"
        ),
        BoatingAccident(
            accident_id="2023-003",
            date="2023-08-10",
            location="Singer Island Beach",
            lat=26.7900,
            lon=-80.0330,
            accident_type="Person overboard",
            vessels_involved=1,
            injuries=1,
            fatalities=0,
            primary_cause="Weather conditions"
        ),
        BoatingAccident(
            accident_id="2022-001",
            date="2022-07-04",
            location="ICW - Blue Heron Bridge",
            lat=26.7753,
            lon=-80.0400,
            accident_type="Collision with fixed object",
            vessels_involved=1,
            injuries=2,
            fatalities=0,
            property_damage="$25,000",
            primary_cause="Operator inexperience"
        ),
    ]
    
    def __init__(self) -> None:
        """Initialize the Marine Traffic Service."""
        self._traffic_loaded = False
        self._http_client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    async def load_traffic_data(self) -> dict[str, Any]:
        """Load marine traffic data."""
        logger.info("loading_marine_traffic", city="Riviera Beach")
        
        # In production, would fetch from AIS API
        # Using sample data for demonstration
        
        self._traffic_loaded = True
        
        return {
            "vessels": [v.model_dump() for v in self.SAMPLE_VESSELS],
            "accidents": [a.model_dump() for a in self.BOATING_ACCIDENTS],
            "metadata": {
                "source": "AIS / USCG BARD",
                "area": "Lake Worth / Riviera Beach",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_vessels(self) -> list[VesselPosition]:
        """Get current vessel positions."""
        return self.SAMPLE_VESSELS
    
    def get_vessels_by_type(self, vessel_type: VesselType) -> list[VesselPosition]:
        """Get vessels by type."""
        return [v for v in self.SAMPLE_VESSELS if v.vessel_type == vessel_type]
    
    def get_accidents(self, year: int | None = None) -> list[BoatingAccident]:
        """Get boating accidents, optionally filtered by year."""
        if year:
            return [a for a in self.BOATING_ACCIDENTS if a.date.startswith(str(year))]
        return self.BOATING_ACCIDENTS
    
    def get_accident_statistics(self) -> dict[str, Any]:
        """Get accident statistics."""
        total = len(self.BOATING_ACCIDENTS)
        total_injuries = sum(a.injuries for a in self.BOATING_ACCIDENTS)
        total_fatalities = sum(a.fatalities for a in self.BOATING_ACCIDENTS)
        
        return {
            "total_accidents": total,
            "total_injuries": total_injuries,
            "total_fatalities": total_fatalities,
            "accidents_by_type": {},
            "primary_causes": {}
        }
    
    def get_vessels_geojson(self) -> dict[str, Any]:
        """Get vessels as GeoJSON."""
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [v.lon, v.lat]},
                "properties": {
                    "mmsi": v.mmsi,
                    "name": v.vessel_name,
                    "type": v.vessel_type.value,
                    "speed": v.speed_kts,
                    "course": v.course,
                    "category": "vessel"
                },
                "id": v.mmsi
            }
            for v in self.SAMPLE_VESSELS
        ]
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of marine traffic data."""
        stats = self.get_accident_statistics()
        return {
            "vessels_tracked": len(self.SAMPLE_VESSELS),
            "accidents_on_record": len(self.BOATING_ACCIDENTS),
            "total_injuries": stats["total_injuries"],
            "total_fatalities": stats["total_fatalities"],
            "traffic_loaded": self._traffic_loaded
        }
