"""
Fire Station Service for Riviera Beach.

Manages fire station locations, apparatus, and response districts.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class ApparatusType(str, Enum):
    """Fire apparatus types."""
    ENGINE = "engine"
    LADDER = "ladder"
    RESCUE = "rescue"
    AMBULANCE = "ambulance"
    BRUSH = "brush"
    HAZMAT = "hazmat"
    BOAT = "boat"
    COMMAND = "command"


class FireApparatus(BaseModel):
    """Fire apparatus information."""
    apparatus_id: str
    apparatus_type: ApparatusType
    unit_number: str
    station_id: str
    in_service: bool = True
    capabilities: list[str] = Field(default_factory=list)


class FireStation(BaseModel):
    """Fire station information."""
    station_id: str
    name: str
    station_number: int
    address: str
    city: str = "Riviera Beach"
    state: str = "FL"
    zip_code: str = "33404"
    lat: float
    lon: float
    phone: str | None = None
    staffing: str | None = None
    apparatus: list[FireApparatus] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    response_district: str | None = None


class FireStationService:
    """
    Service for managing fire station data for Riviera Beach.
    
    Provides:
    - Fire station locations
    - Apparatus lists
    - Response district boundaries
    - Station capabilities
    """
    
    # Riviera Beach Fire Rescue stations
    FIRE_STATIONS = [
        FireStation(
            station_id="rbfr_station_1",
            name="Riviera Beach Fire Rescue Station 1",
            station_number=1,
            address="600 W Blue Heron Blvd",
            lat=26.7753,
            lon=-80.0620,
            phone="(561) 845-4000",
            staffing="24/7",
            apparatus=[
                FireApparatus(
                    apparatus_id="e1",
                    apparatus_type=ApparatusType.ENGINE,
                    unit_number="Engine 1",
                    station_id="rbfr_station_1",
                    capabilities=["Fire Suppression", "EMS First Response", "Vehicle Extrication"]
                ),
                FireApparatus(
                    apparatus_id="r1",
                    apparatus_type=ApparatusType.RESCUE,
                    unit_number="Rescue 1",
                    station_id="rbfr_station_1",
                    capabilities=["Advanced Life Support", "Technical Rescue"]
                ),
                FireApparatus(
                    apparatus_id="bc1",
                    apparatus_type=ApparatusType.COMMAND,
                    unit_number="Battalion 1",
                    station_id="rbfr_station_1",
                    capabilities=["Incident Command", "Fire Investigation"]
                ),
            ],
            services=["Fire Suppression", "EMS", "Technical Rescue", "Fire Prevention"],
            response_district="District 1 - Central/West"
        ),
        FireStation(
            station_id="rbfr_station_2",
            name="Riviera Beach Fire Rescue Station 2",
            station_number=2,
            address="2080 W Blue Heron Blvd",
            lat=26.7753,
            lon=-80.0800,
            phone="(561) 845-4002",
            staffing="24/7",
            apparatus=[
                FireApparatus(
                    apparatus_id="e2",
                    apparatus_type=ApparatusType.ENGINE,
                    unit_number="Engine 2",
                    station_id="rbfr_station_2",
                    capabilities=["Fire Suppression", "EMS First Response"]
                ),
                FireApparatus(
                    apparatus_id="l2",
                    apparatus_type=ApparatusType.LADDER,
                    unit_number="Ladder 2",
                    station_id="rbfr_station_2",
                    capabilities=["Aerial Operations", "Ventilation", "High-Rise Response"]
                ),
            ],
            services=["Fire Suppression", "EMS", "Aerial Operations"],
            response_district="District 2 - West"
        ),
        FireStation(
            station_id="rbfr_station_3",
            name="Riviera Beach Fire Rescue Station 3 - Singer Island",
            station_number=3,
            address="2500 N Ocean Dr",
            lat=26.7900,
            lon=-80.0350,
            phone="(561) 845-4003",
            staffing="24/7",
            apparatus=[
                FireApparatus(
                    apparatus_id="e3",
                    apparatus_type=ApparatusType.ENGINE,
                    unit_number="Engine 3",
                    station_id="rbfr_station_3",
                    capabilities=["Fire Suppression", "EMS First Response", "Beach Response"]
                ),
                FireApparatus(
                    apparatus_id="r3",
                    apparatus_type=ApparatusType.RESCUE,
                    unit_number="Rescue 3",
                    station_id="rbfr_station_3",
                    capabilities=["Advanced Life Support", "Water Rescue"]
                ),
                FireApparatus(
                    apparatus_id="m3",
                    apparatus_type=ApparatusType.BOAT,
                    unit_number="Marine 3",
                    station_id="rbfr_station_3",
                    capabilities=["Water Rescue", "Marine Firefighting"]
                ),
            ],
            services=["Fire Suppression", "EMS", "Water Rescue", "Beach Safety"],
            response_district="District 3 - Singer Island/Beach"
        ),
    ]
    
    # Palm Beach County Fire Rescue stations nearby (mutual aid)
    PBCFR_STATIONS = [
        {
            "name": "PBCFR Station 22",
            "address": "Palm Beach Gardens",
            "lat": 26.8200,
            "lon": -80.0700,
            "note": "Mutual aid - north"
        },
        {
            "name": "PBCFR Station 14",
            "address": "West Palm Beach",
            "lat": 26.7500,
            "lon": -80.0900,
            "note": "Mutual aid - south"
        },
    ]
    
    def __init__(self) -> None:
        """Initialize the Fire Station Service."""
        self._stations_loaded = False
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
    
    async def load_stations(self) -> dict[str, Any]:
        """
        Load fire station data.
        
        Returns:
            dict: GeoJSON feature collection of fire stations
        """
        logger.info("loading_fire_stations", city="Riviera Beach")
        
        features = []
        
        for station in self.FIRE_STATIONS:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [station.lon, station.lat]
                },
                "properties": {
                    "station_id": station.station_id,
                    "name": station.name,
                    "station_number": station.station_number,
                    "address": station.address,
                    "city": station.city,
                    "state": station.state,
                    "zip_code": station.zip_code,
                    "phone": station.phone,
                    "staffing": station.staffing,
                    "apparatus_count": len(station.apparatus),
                    "apparatus_types": [a.apparatus_type.value for a in station.apparatus],
                    "services": station.services,
                    "response_district": station.response_district,
                    "category": "fire"
                },
                "id": station.station_id
            })
        
        self._stations_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Riviera Beach Fire Rescue (Public Data)",
                "agency": "RBFR",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_stations(self) -> list[FireStation]:
        """Get list of fire stations."""
        return self.FIRE_STATIONS
    
    def get_station_by_id(self, station_id: str) -> FireStation | None:
        """
        Get station by ID.
        
        Args:
            station_id: Station identifier
            
        Returns:
            FireStation or None
        """
        for station in self.FIRE_STATIONS:
            if station.station_id == station_id:
                return station
        return None
    
    def get_station_by_number(self, station_number: int) -> FireStation | None:
        """
        Get station by number.
        
        Args:
            station_number: Station number
            
        Returns:
            FireStation or None
        """
        for station in self.FIRE_STATIONS:
            if station.station_number == station_number:
                return station
        return None
    
    def get_all_apparatus(self) -> list[FireApparatus]:
        """Get list of all apparatus across all stations."""
        apparatus = []
        for station in self.FIRE_STATIONS:
            apparatus.extend(station.apparatus)
        return apparatus
    
    def get_apparatus_by_type(self, apparatus_type: ApparatusType) -> list[FireApparatus]:
        """
        Get apparatus by type.
        
        Args:
            apparatus_type: Type of apparatus
            
        Returns:
            List of matching apparatus
        """
        return [
            a for station in self.FIRE_STATIONS
            for a in station.apparatus
            if a.apparatus_type == apparatus_type
        ]
    
    def get_nearest_station(self, lat: float, lon: float) -> FireStation | None:
        """
        Get nearest fire station to a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Nearest FireStation or None
        """
        if not self.FIRE_STATIONS:
            return None
        
        def distance_sq(s: FireStation) -> float:
            return (s.lat - lat) ** 2 + (s.lon - lon) ** 2
        
        return min(self.FIRE_STATIONS, key=distance_sq)
    
    def get_stations_geojson(self) -> dict[str, Any]:
        """
        Get fire stations as GeoJSON.
        
        Returns:
            dict: GeoJSON feature collection
        """
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [s.lon, s.lat]
                },
                "properties": {
                    "station_id": s.station_id,
                    "name": s.name,
                    "station_number": s.station_number,
                    "address": s.address,
                    "category": "fire"
                },
                "id": s.station_id
            }
            for s in self.FIRE_STATIONS
        ]
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of fire station data."""
        all_apparatus = self.get_all_apparatus()
        
        return {
            "agency": "Riviera Beach Fire Rescue",
            "total_stations": len(self.FIRE_STATIONS),
            "total_apparatus": len(all_apparatus),
            "apparatus_by_type": {
                at.value: len(self.get_apparatus_by_type(at))
                for at in ApparatusType
            },
            "stations_loaded": self._stations_loaded,
            "mutual_aid_stations": len(self.PBCFR_STATIONS)
        }
