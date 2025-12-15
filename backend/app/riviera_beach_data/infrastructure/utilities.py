"""
Utility Infrastructure Service for Riviera Beach.

Manages utility infrastructure data including water, power, and communications.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class UtilityType(str, Enum):
    """Utility infrastructure types."""
    WATER_TREATMENT = "water_treatment"
    WASTEWATER = "wastewater"
    POWER_SUBSTATION = "power_substation"
    POWER_TRANSMISSION = "power_transmission"
    CELLULAR_TOWER = "cellular_tower"
    PUMP_STATION = "pump_station"
    WATER_TOWER = "water_tower"


class UtilityFacility(BaseModel):
    """Utility facility information."""
    facility_id: str
    name: str
    utility_type: UtilityType
    address: str | None = None
    lat: float
    lon: float
    owner: str
    capacity: str | None = None
    status: str = "operational"
    critical_level: str = "high"  # high, medium, low
    description: str | None = None


class UtilityService:
    """
    Service for managing utility infrastructure data for Riviera Beach.
    
    Provides:
    - Water treatment facilities
    - Wastewater facilities
    - Power substations and transmission lines
    - Cellular towers
    """
    
    # Riviera Beach utility facilities
    UTILITY_FACILITIES = [
        # Water Infrastructure
        UtilityFacility(
            facility_id="water_treatment_1",
            name="Riviera Beach Water Treatment Plant",
            utility_type=UtilityType.WATER_TREATMENT,
            address="1800 W 10th St, Riviera Beach, FL 33404",
            lat=26.7680,
            lon=-80.0750,
            owner="City of Riviera Beach Utilities",
            capacity="12 MGD",
            critical_level="high",
            description="Primary water treatment facility serving Riviera Beach"
        ),
        UtilityFacility(
            facility_id="wastewater_1",
            name="Riviera Beach Wastewater Treatment Facility",
            utility_type=UtilityType.WASTEWATER,
            address="1900 W 10th St, Riviera Beach, FL 33404",
            lat=26.7670,
            lon=-80.0760,
            owner="City of Riviera Beach Utilities",
            capacity="8 MGD",
            critical_level="high",
            description="Primary wastewater treatment facility"
        ),
        UtilityFacility(
            facility_id="pump_station_1",
            name="Blue Heron Pump Station",
            utility_type=UtilityType.PUMP_STATION,
            lat=26.7753,
            lon=-80.0650,
            owner="City of Riviera Beach Utilities",
            critical_level="medium",
            description="Water distribution pump station"
        ),
        UtilityFacility(
            facility_id="pump_station_2",
            name="Singer Island Pump Station",
            utility_type=UtilityType.PUMP_STATION,
            lat=26.7900,
            lon=-80.0380,
            owner="City of Riviera Beach Utilities",
            critical_level="high",
            description="Water distribution pump station for Singer Island"
        ),
        
        # Power Infrastructure (FPL)
        UtilityFacility(
            facility_id="fpl_substation_1",
            name="FPL Riviera Beach Substation",
            utility_type=UtilityType.POWER_SUBSTATION,
            lat=26.7700,
            lon=-80.0800,
            owner="Florida Power & Light",
            capacity="138kV/13.2kV",
            critical_level="high",
            description="Primary electrical substation serving Riviera Beach"
        ),
        UtilityFacility(
            facility_id="fpl_substation_2",
            name="FPL Blue Heron Substation",
            utility_type=UtilityType.POWER_SUBSTATION,
            lat=26.7753,
            lon=-80.0900,
            owner="Florida Power & Light",
            capacity="69kV/13.2kV",
            critical_level="medium",
            description="Secondary electrical substation"
        ),
        UtilityFacility(
            facility_id="fpl_transmission_1",
            name="FPL 138kV Transmission Corridor",
            utility_type=UtilityType.POWER_TRANSMISSION,
            lat=26.7750,
            lon=-80.0850,
            owner="Florida Power & Light",
            capacity="138kV",
            critical_level="high",
            description="Major transmission corridor through Riviera Beach"
        ),
        
        # Cellular Infrastructure (FCC Database)
        UtilityFacility(
            facility_id="cell_tower_1",
            name="AT&T Cell Tower - Blue Heron",
            utility_type=UtilityType.CELLULAR_TOWER,
            lat=26.7753,
            lon=-80.0620,
            owner="AT&T",
            critical_level="medium",
            description="Cellular communications tower"
        ),
        UtilityFacility(
            facility_id="cell_tower_2",
            name="Verizon Cell Tower - Broadway",
            utility_type=UtilityType.CELLULAR_TOWER,
            lat=26.7800,
            lon=-80.0583,
            owner="Verizon",
            critical_level="medium",
            description="Cellular communications tower"
        ),
        UtilityFacility(
            facility_id="cell_tower_3",
            name="T-Mobile Cell Tower - Singer Island",
            utility_type=UtilityType.CELLULAR_TOWER,
            lat=26.7900,
            lon=-80.0350,
            owner="T-Mobile",
            critical_level="medium",
            description="Cellular communications tower serving Singer Island"
        ),
        UtilityFacility(
            facility_id="cell_tower_4",
            name="Crown Castle Tower - Industrial",
            utility_type=UtilityType.CELLULAR_TOWER,
            lat=26.7650,
            lon=-80.0700,
            owner="Crown Castle",
            critical_level="medium",
            description="Multi-carrier cellular tower"
        ),
    ]
    
    def __init__(self) -> None:
        """Initialize the Utility Service."""
        self._utilities_loaded = False
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
    
    async def load_utilities(self) -> dict[str, Any]:
        """
        Load utility infrastructure data.
        
        Returns:
            dict: GeoJSON feature collection of utilities
        """
        logger.info("loading_utilities", city="Riviera Beach")
        
        features = []
        
        for facility in self.UTILITY_FACILITIES:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [facility.lon, facility.lat]
                },
                "properties": {
                    "facility_id": facility.facility_id,
                    "name": facility.name,
                    "utility_type": facility.utility_type.value,
                    "address": facility.address,
                    "owner": facility.owner,
                    "capacity": facility.capacity,
                    "status": facility.status,
                    "critical_level": facility.critical_level,
                    "description": facility.description,
                    "category": "utility"
                },
                "id": facility.facility_id
            })
        
        self._utilities_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Riviera Beach Utilities / FPL / FCC",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_facilities(self) -> list[UtilityFacility]:
        """Get list of utility facilities."""
        return self.UTILITY_FACILITIES
    
    def get_facility_by_id(self, facility_id: str) -> UtilityFacility | None:
        """Get facility by ID."""
        for facility in self.UTILITY_FACILITIES:
            if facility.facility_id == facility_id:
                return facility
        return None
    
    def get_facilities_by_type(self, utility_type: UtilityType) -> list[UtilityFacility]:
        """Get facilities by type."""
        return [f for f in self.UTILITY_FACILITIES if f.utility_type == utility_type]
    
    def get_critical_facilities(self) -> list[UtilityFacility]:
        """Get high-criticality facilities."""
        return [f for f in self.UTILITY_FACILITIES if f.critical_level == "high"]
    
    def get_utilities_geojson(self) -> dict[str, Any]:
        """Get utilities as GeoJSON."""
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
                    "utility_type": f.utility_type.value,
                    "owner": f.owner,
                    "critical_level": f.critical_level,
                    "category": "utility"
                },
                "id": f.facility_id
            }
            for f in self.UTILITY_FACILITIES
        ]
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of utility data."""
        return {
            "total_facilities": len(self.UTILITY_FACILITIES),
            "by_type": {
                ut.value: len(self.get_facilities_by_type(ut))
                for ut in UtilityType
            },
            "critical_count": len(self.get_critical_facilities()),
            "utilities_loaded": self._utilities_loaded
        }
