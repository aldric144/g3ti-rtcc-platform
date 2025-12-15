"""
Marina Layout Service for Riviera Beach.

Manages marina layout, dock maps, and facility information.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class DockType(str, Enum):
    """Dock types."""
    WET_SLIP = "wet_slip"
    DRY_STORAGE = "dry_storage"
    TRANSIENT = "transient"
    FUEL_DOCK = "fuel_dock"
    PUMP_OUT = "pump_out"
    BOAT_RAMP = "boat_ramp"


class MarinaFacility(BaseModel):
    """Marina facility information."""
    facility_id: str
    name: str
    facility_type: str
    lat: float
    lon: float
    description: str | None = None
    capacity: int | None = None
    max_vessel_length_ft: int | None = None
    amenities: list[str] = Field(default_factory=list)
    contact_phone: str | None = None
    vhf_channel: int | None = None


class Dock(BaseModel):
    """Dock information."""
    dock_id: str
    dock_name: str
    dock_type: DockType
    lat: float
    lon: float
    slips: int | None = None
    max_length_ft: int | None = None
    power_available: list[str] = Field(default_factory=list)
    water_depth_ft: float | None = None


class MarinaLayoutService:
    """
    Service for marina layout data for Riviera Beach.
    """
    
    # Riviera Beach Marina facilities
    MARINA_FACILITIES = [
        MarinaFacility(
            facility_id="rb_marina_main",
            name="Riviera Beach Marina",
            facility_type="municipal_marina",
            lat=26.7800,
            lon=-80.0450,
            description="Full-service municipal marina with 194 wet slips",
            capacity=194,
            max_vessel_length_ft=150,
            amenities=[
                "Fuel Dock", "Pump Out", "Shore Power", "Water",
                "WiFi", "Restrooms", "Showers", "Laundry",
                "Ship Store", "Ice", "Bait & Tackle"
            ],
            contact_phone="(561) 842-7806",
            vhf_channel=16
        ),
        MarinaFacility(
            facility_id="rb_marina_village",
            name="Riviera Beach Marina Village",
            facility_type="commercial_district",
            lat=26.7795,
            lon=-80.0445,
            description="Waterfront dining and entertainment district",
            amenities=["Restaurants", "Shops", "Event Space", "Parking"]
        ),
        MarinaFacility(
            facility_id="rb_boat_ramp",
            name="Riviera Beach Public Boat Ramp",
            facility_type="boat_ramp",
            lat=26.7810,
            lon=-80.0460,
            description="Public boat launch with parking",
            amenities=["Boat Ramp", "Parking", "Fish Cleaning Station"],
            contact_phone="(561) 845-4070"
        ),
        MarinaFacility(
            facility_id="peanut_island_ferry",
            name="Peanut Island Ferry Dock",
            facility_type="ferry_terminal",
            lat=26.7780,
            lon=-80.0420,
            description="Ferry service to Peanut Island",
            amenities=["Ferry Service", "Ticket Sales"]
        ),
    ]
    
    # Dock layout
    DOCKS = [
        Dock(
            dock_id="dock_a",
            dock_name="Dock A",
            dock_type=DockType.WET_SLIP,
            lat=26.7802,
            lon=-80.0448,
            slips=32,
            max_length_ft=50,
            power_available=["30A", "50A"],
            water_depth_ft=8.0
        ),
        Dock(
            dock_id="dock_b",
            dock_name="Dock B",
            dock_type=DockType.WET_SLIP,
            lat=26.7800,
            lon=-80.0452,
            slips=28,
            max_length_ft=60,
            power_available=["30A", "50A", "100A"],
            water_depth_ft=10.0
        ),
        Dock(
            dock_id="dock_c",
            dock_name="Dock C",
            dock_type=DockType.WET_SLIP,
            lat=26.7798,
            lon=-80.0456,
            slips=24,
            max_length_ft=80,
            power_available=["50A", "100A"],
            water_depth_ft=12.0
        ),
        Dock(
            dock_id="dock_d",
            dock_name="Dock D - Mega Yacht",
            dock_type=DockType.WET_SLIP,
            lat=26.7796,
            lon=-80.0460,
            slips=8,
            max_length_ft=150,
            power_available=["100A", "200A"],
            water_depth_ft=15.0
        ),
        Dock(
            dock_id="fuel_dock",
            dock_name="Fuel Dock",
            dock_type=DockType.FUEL_DOCK,
            lat=26.7805,
            lon=-80.0445,
            max_length_ft=100,
            water_depth_ft=10.0
        ),
        Dock(
            dock_id="transient_dock",
            dock_name="Transient Dock",
            dock_type=DockType.TRANSIENT,
            lat=26.7808,
            lon=-80.0442,
            slips=12,
            max_length_ft=60,
            power_available=["30A", "50A"],
            water_depth_ft=8.0
        ),
    ]
    
    def __init__(self) -> None:
        """Initialize the Marina Layout Service."""
        self._marina_loaded = False
    
    async def load_marina_data(self) -> dict[str, Any]:
        """Load marina layout data."""
        logger.info("loading_marina_data", city="Riviera Beach")
        
        features = []
        
        # Add facilities
        for facility in self.MARINA_FACILITIES:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [facility.lon, facility.lat]},
                "properties": {
                    "facility_id": facility.facility_id,
                    "name": facility.name,
                    "facility_type": facility.facility_type,
                    "description": facility.description,
                    "capacity": facility.capacity,
                    "amenities": facility.amenities,
                    "category": "marina_facility"
                },
                "id": facility.facility_id
            })
        
        # Add docks
        for dock in self.DOCKS:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [dock.lon, dock.lat]},
                "properties": {
                    "dock_id": dock.dock_id,
                    "name": dock.dock_name,
                    "dock_type": dock.dock_type.value,
                    "slips": dock.slips,
                    "max_length_ft": dock.max_length_ft,
                    "water_depth_ft": dock.water_depth_ft,
                    "category": "dock"
                },
                "id": dock.dock_id
            })
        
        self._marina_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "City of Riviera Beach Marina",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_facilities(self) -> list[MarinaFacility]:
        """Get marina facilities."""
        return self.MARINA_FACILITIES
    
    def get_docks(self) -> list[Dock]:
        """Get dock information."""
        return self.DOCKS
    
    def get_total_slips(self) -> int:
        """Get total number of slips."""
        return sum(d.slips or 0 for d in self.DOCKS)
    
    def get_marina_geojson(self) -> dict[str, Any]:
        """Get marina data as GeoJSON."""
        features = []
        for f in self.MARINA_FACILITIES:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [f.lon, f.lat]},
                "properties": {"name": f.name, "type": f.facility_type, "category": "marina"},
                "id": f.facility_id
            })
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of marina data."""
        return {
            "marina_name": "Riviera Beach Marina",
            "total_facilities": len(self.MARINA_FACILITIES),
            "total_docks": len(self.DOCKS),
            "total_slips": self.get_total_slips(),
            "max_vessel_length_ft": 150,
            "marina_loaded": self._marina_loaded
        }
