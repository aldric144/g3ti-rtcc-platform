"""
Police Location Service for Riviera Beach.

Manages public police facility location data.
NOTE: This module only contains PUBLIC data - no internal RBPD data.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class FacilityType(str, Enum):
    """Police facility types."""
    HEADQUARTERS = "headquarters"
    SUBSTATION = "substation"
    COMMUNITY_CENTER = "community_center"
    TRAINING_FACILITY = "training_facility"


class PoliceFacility(BaseModel):
    """Police facility information (public data only)."""
    facility_id: str
    name: str
    facility_type: FacilityType
    address: str
    city: str = "Riviera Beach"
    state: str = "FL"
    zip_code: str = "33404"
    lat: float
    lon: float
    phone: str | None = None
    hours: str | None = None
    services: list[str] = Field(default_factory=list)
    is_public_access: bool = True


class PoliceLocationService:
    """
    Service for managing public police facility locations.
    
    NOTE: This service only provides PUBLIC information about
    police facilities. No internal operational data is included.
    
    Provides:
    - RBPD headquarters location
    - Public substation locations
    - Community policing centers
    """
    
    # Public police facilities in Riviera Beach
    PUBLIC_FACILITIES = [
        PoliceFacility(
            facility_id="rbpd_hq",
            name="Riviera Beach Police Department Headquarters",
            facility_type=FacilityType.HEADQUARTERS,
            address="600 W Blue Heron Blvd",
            lat=26.7753,
            lon=-80.0620,
            phone="(561) 845-4123",
            hours="24/7",
            services=[
                "Emergency Response",
                "Records",
                "Community Services",
                "Investigations"
            ],
            is_public_access=True
        ),
        PoliceFacility(
            facility_id="rbpd_community_1",
            name="RBPD Community Policing Center - Marina",
            facility_type=FacilityType.COMMUNITY_CENTER,
            address="200 E 13th St",
            lat=26.7800,
            lon=-80.0500,
            phone="(561) 845-4100",
            hours="Mon-Fri 8AM-5PM",
            services=[
                "Community Outreach",
                "Crime Prevention",
                "Neighborhood Watch"
            ],
            is_public_access=True
        ),
        PoliceFacility(
            facility_id="rbpd_substation_1",
            name="RBPD Singer Island Substation",
            facility_type=FacilityType.SUBSTATION,
            address="2500 N Ocean Dr",
            lat=26.7900,
            lon=-80.0350,
            phone="(561) 845-4150",
            hours="24/7",
            services=[
                "Patrol Services",
                "Beach Safety Coordination"
            ],
            is_public_access=True
        ),
    ]
    
    # Palm Beach County Sheriff's Office nearby facilities
    PBSO_FACILITIES = [
        {
            "name": "PBSO North District",
            "address": "3228 Gun Club Rd, West Palm Beach, FL",
            "lat": 26.6800,
            "lon": -80.1200,
            "note": "County sheriff facility - mutual aid"
        }
    ]
    
    def __init__(self) -> None:
        """Initialize the Police Location Service."""
        self._locations_loaded = False
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
    
    async def load_locations(self) -> dict[str, Any]:
        """
        Load police facility locations.
        
        Returns:
            dict: GeoJSON feature collection of police facilities
        """
        logger.info("loading_police_locations", city="Riviera Beach")
        
        features = []
        
        for facility in self.PUBLIC_FACILITIES:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [facility.lon, facility.lat]
                },
                "properties": {
                    "facility_id": facility.facility_id,
                    "name": facility.name,
                    "facility_type": facility.facility_type.value,
                    "address": facility.address,
                    "city": facility.city,
                    "state": facility.state,
                    "zip_code": facility.zip_code,
                    "phone": facility.phone,
                    "hours": facility.hours,
                    "services": facility.services,
                    "is_public_access": facility.is_public_access,
                    "category": "police",
                    "agency": "Riviera Beach Police Department"
                },
                "id": facility.facility_id
            })
        
        self._locations_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Riviera Beach Police Department (Public Data)",
                "agency": "RBPD",
                "note": "Public facility locations only",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_facilities(self) -> list[PoliceFacility]:
        """Get list of public police facilities."""
        return self.PUBLIC_FACILITIES
    
    def get_facility_by_id(self, facility_id: str) -> PoliceFacility | None:
        """
        Get facility by ID.
        
        Args:
            facility_id: Facility identifier
            
        Returns:
            PoliceFacility or None
        """
        for facility in self.PUBLIC_FACILITIES:
            if facility.facility_id == facility_id:
                return facility
        return None
    
    def get_headquarters(self) -> PoliceFacility | None:
        """Get RBPD headquarters information."""
        for facility in self.PUBLIC_FACILITIES:
            if facility.facility_type == FacilityType.HEADQUARTERS:
                return facility
        return None
    
    def get_nearest_facility(self, lat: float, lon: float) -> PoliceFacility | None:
        """
        Get nearest police facility to a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Nearest PoliceFacility or None
        """
        if not self.PUBLIC_FACILITIES:
            return None
        
        def distance_sq(f: PoliceFacility) -> float:
            return (f.lat - lat) ** 2 + (f.lon - lon) ** 2
        
        return min(self.PUBLIC_FACILITIES, key=distance_sq)
    
    def get_locations_geojson(self) -> dict[str, Any]:
        """
        Get police locations as GeoJSON.
        
        Returns:
            dict: GeoJSON feature collection
        """
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [f.lon, f.lat]
                },
                "properties": {
                    "facility_id": f.facility_id,
                    "name": f.name,
                    "facility_type": f.facility_type.value,
                    "address": f.address,
                    "category": "police"
                },
                "id": f.facility_id
            }
            for f in self.PUBLIC_FACILITIES
        ]
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of police location data."""
        return {
            "agency": "Riviera Beach Police Department",
            "total_facilities": len(self.PUBLIC_FACILITIES),
            "facility_types": {
                ft.value: len([f for f in self.PUBLIC_FACILITIES if f.facility_type == ft])
                for ft in FacilityType
            },
            "locations_loaded": self._locations_loaded,
            "data_type": "public_only"
        }
