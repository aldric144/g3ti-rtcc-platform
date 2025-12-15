"""
Transportation Infrastructure Service for Riviera Beach.

Manages transportation infrastructure including marina, bridges, rail, and transit.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class TransportationType(str, Enum):
    """Transportation infrastructure types."""
    MARINA = "marina"
    BRIDGE = "bridge"
    DRAWBRIDGE = "drawbridge"
    RAIL = "rail"
    BUS_ROUTE = "bus_route"
    BUS_STOP = "bus_stop"
    PORT = "port"
    EVACUATION_ROUTE = "evacuation_route"


class TransportationFacility(BaseModel):
    """Transportation facility information."""
    facility_id: str
    name: str
    transport_type: TransportationType
    address: str | None = None
    lat: float
    lon: float
    owner: str | None = None
    description: str | None = None
    capacity: str | None = None
    operational_hours: str | None = None
    is_evacuation_critical: bool = False


class BusRoute(BaseModel):
    """PalmTran bus route information."""
    route_id: str
    route_number: str
    route_name: str
    stops_in_riviera_beach: int
    frequency_minutes: int | None = None
    operating_hours: str | None = None


class TransportationService:
    """
    Service for managing transportation infrastructure data for Riviera Beach.
    
    Provides:
    - Marina layout
    - Bridges and drawbridges
    - Rail lines (FEC Railroad)
    - Bus routes (PalmTran GTFS)
    - Evacuation routes
    """
    
    # Transportation facilities
    TRANSPORTATION_FACILITIES = [
        # Marina
        TransportationFacility(
            facility_id="marina_1",
            name="Riviera Beach Marina",
            transport_type=TransportationType.MARINA,
            address="200 E 13th St, Riviera Beach, FL 33404",
            lat=26.7800,
            lon=-80.0450,
            owner="City of Riviera Beach",
            description="Full-service municipal marina with 194 wet slips",
            capacity="194 wet slips, 200 dry storage",
            operational_hours="24/7 access for slip holders"
        ),
        TransportationFacility(
            facility_id="marina_2",
            name="Riviera Beach Marina Village",
            transport_type=TransportationType.MARINA,
            address="190 E 13th St, Riviera Beach, FL 33404",
            lat=26.7795,
            lon=-80.0445,
            owner="City of Riviera Beach",
            description="Marina village with restaurants and shops",
            operational_hours="Varies by business"
        ),
        
        # Port
        TransportationFacility(
            facility_id="port_1",
            name="Port of Palm Beach",
            transport_type=TransportationType.PORT,
            address="1 E 11th St, Riviera Beach, FL 33404",
            lat=26.7650,
            lon=-80.0450,
            owner="Port of Palm Beach District",
            description="Fourth busiest container port in Florida",
            capacity="2.5 million tons annually",
            operational_hours="24/7",
            is_evacuation_critical=True
        ),
        
        # Bridges
        TransportationFacility(
            facility_id="bridge_1",
            name="Blue Heron Bridge",
            transport_type=TransportationType.DRAWBRIDGE,
            lat=26.7753,
            lon=-80.0400,
            owner="Palm Beach County",
            description="Drawbridge connecting mainland to Singer Island",
            is_evacuation_critical=True
        ),
        TransportationFacility(
            facility_id="bridge_2",
            name="Riviera Beach Bridge (SR 710)",
            transport_type=TransportationType.BRIDGE,
            lat=26.7753,
            lon=-80.0500,
            owner="FDOT",
            description="State road bridge over Intracoastal",
            is_evacuation_critical=True
        ),
        
        # Rail
        TransportationFacility(
            facility_id="rail_1",
            name="FEC Railway - Riviera Beach Corridor",
            transport_type=TransportationType.RAIL,
            lat=26.7750,
            lon=-80.0550,
            owner="Florida East Coast Railway",
            description="Freight rail corridor through Riviera Beach"
        ),
        TransportationFacility(
            facility_id="rail_2",
            name="Brightline/Virgin Trains Corridor",
            transport_type=TransportationType.RAIL,
            lat=26.7750,
            lon=-80.0560,
            owner="Brightline",
            description="High-speed passenger rail corridor (no station in RB)"
        ),
        
        # Evacuation Routes
        TransportationFacility(
            facility_id="evac_1",
            name="I-95 Evacuation Route",
            transport_type=TransportationType.EVACUATION_ROUTE,
            lat=26.7753,
            lon=-80.0700,
            owner="FDOT",
            description="Primary hurricane evacuation route",
            is_evacuation_critical=True
        ),
        TransportationFacility(
            facility_id="evac_2",
            name="US-1 Evacuation Route",
            transport_type=TransportationType.EVACUATION_ROUTE,
            lat=26.7753,
            lon=-80.0500,
            owner="FDOT",
            description="Secondary hurricane evacuation route",
            is_evacuation_critical=True
        ),
    ]
    
    # PalmTran bus routes serving Riviera Beach
    BUS_ROUTES = [
        BusRoute(
            route_id="palmtran_1",
            route_number="1",
            route_name="US 1 - Tri-Rail",
            stops_in_riviera_beach=8,
            frequency_minutes=30,
            operating_hours="5:30 AM - 10:30 PM"
        ),
        BusRoute(
            route_id="palmtran_40",
            route_number="40",
            route_name="Blue Heron Blvd",
            stops_in_riviera_beach=12,
            frequency_minutes=30,
            operating_hours="6:00 AM - 9:00 PM"
        ),
        BusRoute(
            route_id="palmtran_41",
            route_number="41",
            route_name="Northlake Blvd",
            stops_in_riviera_beach=4,
            frequency_minutes=45,
            operating_hours="6:00 AM - 8:00 PM"
        ),
        BusRoute(
            route_id="palmtran_44",
            route_number="44",
            route_name="Singer Island",
            stops_in_riviera_beach=6,
            frequency_minutes=60,
            operating_hours="7:00 AM - 7:00 PM"
        ),
    ]
    
    # Bus stops in Riviera Beach (sample)
    BUS_STOPS = [
        {"stop_id": "stop_001", "name": "Blue Heron & Broadway", "lat": 26.7753, "lon": -80.0583, "routes": ["40"]},
        {"stop_id": "stop_002", "name": "Blue Heron & US-1", "lat": 26.7753, "lon": -80.0500, "routes": ["1", "40"]},
        {"stop_id": "stop_003", "name": "Blue Heron & I-95", "lat": 26.7753, "lon": -80.0700, "routes": ["40"]},
        {"stop_id": "stop_004", "name": "Broadway & 13th St", "lat": 26.7800, "lon": -80.0583, "routes": ["40"]},
        {"stop_id": "stop_005", "name": "Singer Island - Ocean Dr", "lat": 26.7900, "lon": -80.0350, "routes": ["44"]},
        {"stop_id": "stop_006", "name": "Marina Village", "lat": 26.7795, "lon": -80.0450, "routes": ["40", "44"]},
    ]
    
    def __init__(self) -> None:
        """Initialize the Transportation Service."""
        self._transportation_loaded = False
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
    
    async def load_transportation(self) -> dict[str, Any]:
        """
        Load transportation infrastructure data.
        
        Returns:
            dict: GeoJSON feature collection of transportation
        """
        logger.info("loading_transportation", city="Riviera Beach")
        
        features = []
        
        # Add facilities
        for facility in self.TRANSPORTATION_FACILITIES:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [facility.lon, facility.lat]
                },
                "properties": {
                    "facility_id": facility.facility_id,
                    "name": facility.name,
                    "transport_type": facility.transport_type.value,
                    "address": facility.address,
                    "owner": facility.owner,
                    "description": facility.description,
                    "capacity": facility.capacity,
                    "operational_hours": facility.operational_hours,
                    "is_evacuation_critical": facility.is_evacuation_critical,
                    "category": "transportation"
                },
                "id": facility.facility_id
            })
        
        # Add bus stops
        for stop in self.BUS_STOPS:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [stop["lon"], stop["lat"]]
                },
                "properties": {
                    "facility_id": stop["stop_id"],
                    "name": stop["name"],
                    "transport_type": "bus_stop",
                    "routes": stop["routes"],
                    "category": "transportation"
                },
                "id": stop["stop_id"]
            })
        
        self._transportation_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Riviera Beach / PalmTran / FDOT",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_facilities(self) -> list[TransportationFacility]:
        """Get list of transportation facilities."""
        return self.TRANSPORTATION_FACILITIES
    
    def get_facility_by_id(self, facility_id: str) -> TransportationFacility | None:
        """Get facility by ID."""
        for facility in self.TRANSPORTATION_FACILITIES:
            if facility.facility_id == facility_id:
                return facility
        return None
    
    def get_facilities_by_type(self, transport_type: TransportationType) -> list[TransportationFacility]:
        """Get facilities by type."""
        return [f for f in self.TRANSPORTATION_FACILITIES if f.transport_type == transport_type]
    
    def get_evacuation_critical(self) -> list[TransportationFacility]:
        """Get evacuation-critical facilities."""
        return [f for f in self.TRANSPORTATION_FACILITIES if f.is_evacuation_critical]
    
    def get_bus_routes(self) -> list[BusRoute]:
        """Get PalmTran bus routes."""
        return self.BUS_ROUTES
    
    def get_bus_stops(self) -> list[dict[str, Any]]:
        """Get bus stops."""
        return self.BUS_STOPS
    
    def get_transportation_geojson(self) -> dict[str, Any]:
        """Get transportation as GeoJSON."""
        features = []
        
        for f in self.TRANSPORTATION_FACILITIES:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [f.lon, f.lat]
                },
                "properties": {
                    "facility_id": f.facility_id,
                    "name": f.name,
                    "transport_type": f.transport_type.value,
                    "is_evacuation_critical": f.is_evacuation_critical,
                    "category": "transportation"
                },
                "id": f.facility_id
            })
        
        for stop in self.BUS_STOPS:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [stop["lon"], stop["lat"]]
                },
                "properties": {
                    "facility_id": stop["stop_id"],
                    "name": stop["name"],
                    "transport_type": "bus_stop",
                    "category": "transportation"
                },
                "id": stop["stop_id"]
            })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of transportation data."""
        return {
            "total_facilities": len(self.TRANSPORTATION_FACILITIES),
            "by_type": {
                tt.value: len(self.get_facilities_by_type(tt))
                for tt in TransportationType
            },
            "evacuation_critical_count": len(self.get_evacuation_critical()),
            "bus_routes": len(self.BUS_ROUTES),
            "bus_stops": len(self.BUS_STOPS),
            "transportation_loaded": self._transportation_loaded
        }
