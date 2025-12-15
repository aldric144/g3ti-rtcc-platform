"""
Hazard Zone Service for Riviera Beach.

Manages hazard zone data including FEMA flood zones, storm surge, and evacuation zones.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class HazardType(str, Enum):
    """Hazard zone types."""
    FEMA_FLOOD = "fema_flood"
    STORM_SURGE = "storm_surge"
    HURRICANE_EVACUATION = "hurricane_evacuation"
    COASTAL_HIGH_HAZARD = "coastal_high_hazard"
    SPECIAL_FLOOD_HAZARD = "special_flood_hazard"


class FloodZone(str, Enum):
    """FEMA flood zone designations."""
    ZONE_A = "A"      # 100-year flood, no BFE
    ZONE_AE = "AE"    # 100-year flood with BFE
    ZONE_AH = "AH"    # 100-year flood, ponding
    ZONE_AO = "AO"    # 100-year flood, sheet flow
    ZONE_VE = "VE"    # Coastal high hazard with BFE
    ZONE_X = "X"      # 500-year flood or minimal risk
    ZONE_X500 = "X500"  # 500-year flood
    ZONE_D = "D"      # Undetermined


class EvacuationZone(str, Enum):
    """Hurricane evacuation zones."""
    ZONE_A = "A"  # Evacuate for Category 1+
    ZONE_B = "B"  # Evacuate for Category 2+
    ZONE_C = "C"  # Evacuate for Category 3+
    ZONE_D = "D"  # Evacuate for Category 4+
    ZONE_E = "E"  # Evacuate for Category 5


class HazardZoneInfo(BaseModel):
    """Hazard zone information."""
    zone_id: str
    name: str
    hazard_type: HazardType
    zone_designation: str
    risk_level: str  # high, medium, low
    description: str
    evacuation_required: bool = False
    affected_population: int | None = None


class HazardZoneService:
    """
    Service for managing hazard zone data for Riviera Beach.
    
    Provides:
    - FEMA Flood Zones
    - Storm surge zones
    - Hurricane evacuation zones
    - Coastal high hazard areas
    """
    
    # FEMA Flood Zone API
    FEMA_FLOOD_API = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
    
    # Riviera Beach bounding box
    BBOX = {
        "min_lat": 26.7400,
        "max_lat": 26.8100,
        "min_lon": -80.1000,
        "max_lon": -80.0300
    }
    
    # Hazard zones in Riviera Beach
    HAZARD_ZONES = [
        # FEMA Flood Zones
        HazardZoneInfo(
            zone_id="fema_ae_1",
            name="FEMA Flood Zone AE - Coastal",
            hazard_type=HazardType.FEMA_FLOOD,
            zone_designation="AE",
            risk_level="high",
            description="100-year flood zone with base flood elevation, coastal areas",
            evacuation_required=True,
            affected_population=8000
        ),
        HazardZoneInfo(
            zone_id="fema_ve_1",
            name="FEMA Flood Zone VE - Singer Island",
            hazard_type=HazardType.FEMA_FLOOD,
            zone_designation="VE",
            risk_level="high",
            description="Coastal high hazard area with wave action, Singer Island beachfront",
            evacuation_required=True,
            affected_population=3000
        ),
        HazardZoneInfo(
            zone_id="fema_x_1",
            name="FEMA Flood Zone X - Minimal Risk",
            hazard_type=HazardType.FEMA_FLOOD,
            zone_designation="X",
            risk_level="low",
            description="Minimal flood hazard area, outside 500-year floodplain",
            evacuation_required=False,
            affected_population=15000
        ),
        HazardZoneInfo(
            zone_id="fema_x500_1",
            name="FEMA Flood Zone X500 - Moderate Risk",
            hazard_type=HazardType.FEMA_FLOOD,
            zone_designation="X500",
            risk_level="medium",
            description="500-year flood zone, moderate flood risk",
            evacuation_required=False,
            affected_population=12000
        ),
        
        # Storm Surge Zones
        HazardZoneInfo(
            zone_id="surge_cat1",
            name="Storm Surge Zone - Category 1",
            hazard_type=HazardType.STORM_SURGE,
            zone_designation="CAT1",
            risk_level="high",
            description="Areas subject to storm surge from Category 1 hurricane",
            evacuation_required=True,
            affected_population=5000
        ),
        HazardZoneInfo(
            zone_id="surge_cat2",
            name="Storm Surge Zone - Category 2",
            hazard_type=HazardType.STORM_SURGE,
            zone_designation="CAT2",
            risk_level="high",
            description="Areas subject to storm surge from Category 2 hurricane",
            evacuation_required=True,
            affected_population=10000
        ),
        HazardZoneInfo(
            zone_id="surge_cat3",
            name="Storm Surge Zone - Category 3",
            hazard_type=HazardType.STORM_SURGE,
            zone_designation="CAT3",
            risk_level="high",
            description="Areas subject to storm surge from Category 3 hurricane",
            evacuation_required=True,
            affected_population=18000
        ),
        
        # Hurricane Evacuation Zones
        HazardZoneInfo(
            zone_id="evac_a",
            name="Hurricane Evacuation Zone A",
            hazard_type=HazardType.HURRICANE_EVACUATION,
            zone_designation="A",
            risk_level="high",
            description="Evacuate for Category 1 or higher hurricane - Singer Island, coastal areas",
            evacuation_required=True,
            affected_population=7500
        ),
        HazardZoneInfo(
            zone_id="evac_b",
            name="Hurricane Evacuation Zone B",
            hazard_type=HazardType.HURRICANE_EVACUATION,
            zone_designation="B",
            risk_level="high",
            description="Evacuate for Category 2 or higher hurricane - low-lying areas",
            evacuation_required=True,
            affected_population=12000
        ),
        HazardZoneInfo(
            zone_id="evac_c",
            name="Hurricane Evacuation Zone C",
            hazard_type=HazardType.HURRICANE_EVACUATION,
            zone_designation="C",
            risk_level="medium",
            description="Evacuate for Category 3 or higher hurricane",
            evacuation_required=True,
            affected_population=8000
        ),
        
        # Coastal High Hazard Area
        HazardZoneInfo(
            zone_id="chha_1",
            name="Coastal High Hazard Area",
            hazard_type=HazardType.COASTAL_HIGH_HAZARD,
            zone_designation="CHHA",
            risk_level="high",
            description="Area subject to high velocity wave action from storms",
            evacuation_required=True,
            affected_population=4000
        ),
    ]
    
    # Approximate zone polygons (simplified)
    ZONE_POLYGONS = {
        "evac_a": [
            [-80.0450, 26.8100],  # NE
            [-80.0300, 26.8100],  # NE corner
            [-80.0300, 26.7600],  # SE
            [-80.0450, 26.7600],  # SW
            [-80.0450, 26.8100],  # Close
        ],
        "evac_b": [
            [-80.0583, 26.8100],
            [-80.0450, 26.8100],
            [-80.0450, 26.7400],
            [-80.0583, 26.7400],
            [-80.0583, 26.8100],
        ],
        "evac_c": [
            [-80.0750, 26.8100],
            [-80.0583, 26.8100],
            [-80.0583, 26.7400],
            [-80.0750, 26.7400],
            [-80.0750, 26.8100],
        ],
    }
    
    def __init__(self) -> None:
        """Initialize the Hazard Zone Service."""
        self._hazard_zones_loaded = False
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
    
    async def load_hazard_zones(self) -> dict[str, Any]:
        """
        Load hazard zone data.
        
        Returns:
            dict: GeoJSON feature collection of hazard zones
        """
        logger.info("loading_hazard_zones", city="Riviera Beach")
        
        features = []
        
        # Add zone polygons where available
        for zone in self.HAZARD_ZONES:
            polygon = self.ZONE_POLYGONS.get(zone.zone_id)
            
            if polygon:
                geometry = {
                    "type": "Polygon",
                    "coordinates": [polygon]
                }
            else:
                # Use bounding box as fallback
                geometry = {
                    "type": "Polygon",
                    "coordinates": [[
                        [self.BBOX["min_lon"], self.BBOX["max_lat"]],
                        [self.BBOX["max_lon"], self.BBOX["max_lat"]],
                        [self.BBOX["max_lon"], self.BBOX["min_lat"]],
                        [self.BBOX["min_lon"], self.BBOX["min_lat"]],
                        [self.BBOX["min_lon"], self.BBOX["max_lat"]],
                    ]]
                }
            
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "zone_id": zone.zone_id,
                    "name": zone.name,
                    "hazard_type": zone.hazard_type.value,
                    "zone_designation": zone.zone_designation,
                    "risk_level": zone.risk_level,
                    "description": zone.description,
                    "evacuation_required": zone.evacuation_required,
                    "affected_population": zone.affected_population,
                    "category": "hazard_zone"
                },
                "id": zone.zone_id
            })
        
        self._hazard_zones_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "FEMA NFHL / Palm Beach County Emergency Management",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_hazard_zones(self) -> list[HazardZoneInfo]:
        """Get list of hazard zones."""
        return self.HAZARD_ZONES
    
    def get_zone_by_id(self, zone_id: str) -> HazardZoneInfo | None:
        """Get zone by ID."""
        for zone in self.HAZARD_ZONES:
            if zone.zone_id == zone_id:
                return zone
        return None
    
    def get_zones_by_type(self, hazard_type: HazardType) -> list[HazardZoneInfo]:
        """Get zones by hazard type."""
        return [z for z in self.HAZARD_ZONES if z.hazard_type == hazard_type]
    
    def get_evacuation_zones(self) -> list[HazardZoneInfo]:
        """Get zones requiring evacuation."""
        return [z for z in self.HAZARD_ZONES if z.evacuation_required]
    
    def get_high_risk_zones(self) -> list[HazardZoneInfo]:
        """Get high-risk zones."""
        return [z for z in self.HAZARD_ZONES if z.risk_level == "high"]
    
    def get_evacuation_zone_for_location(self, lat: float, lon: float) -> str | None:
        """
        Get evacuation zone for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Evacuation zone designation or None
        """
        # Simple zone lookup based on longitude (east = Zone A, west = Zone C)
        if lon > -80.0450:
            return "A"  # Coastal/Singer Island
        elif lon > -80.0583:
            return "B"  # Near coast
        elif lon > -80.0750:
            return "C"  # Inland
        return None  # Outside evacuation zones
    
    def get_flood_zone_for_location(self, lat: float, lon: float) -> str | None:
        """
        Get FEMA flood zone for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Flood zone designation or None
        """
        # Simple zone lookup based on location
        if lon > -80.0400:
            return "VE"  # Coastal high hazard
        elif lon > -80.0500:
            return "AE"  # 100-year flood
        elif lon > -80.0700:
            return "X500"  # 500-year flood
        return "X"  # Minimal risk
    
    def get_hazard_zones_geojson(self) -> dict[str, Any]:
        """Get hazard zones as GeoJSON."""
        features = []
        
        for zone in self.HAZARD_ZONES:
            polygon = self.ZONE_POLYGONS.get(zone.zone_id)
            
            if polygon:
                geometry = {
                    "type": "Polygon",
                    "coordinates": [polygon]
                }
            else:
                geometry = {
                    "type": "Point",
                    "coordinates": [
                        (self.BBOX["min_lon"] + self.BBOX["max_lon"]) / 2,
                        (self.BBOX["min_lat"] + self.BBOX["max_lat"]) / 2
                    ]
                }
            
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "zone_id": zone.zone_id,
                    "name": zone.name,
                    "hazard_type": zone.hazard_type.value,
                    "risk_level": zone.risk_level,
                    "evacuation_required": zone.evacuation_required,
                    "category": "hazard_zone"
                },
                "id": zone.zone_id
            })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of hazard zone data."""
        return {
            "total_zones": len(self.HAZARD_ZONES),
            "by_type": {
                ht.value: len(self.get_zones_by_type(ht))
                for ht in HazardType
            },
            "evacuation_required_count": len(self.get_evacuation_zones()),
            "high_risk_count": len(self.get_high_risk_zones()),
            "total_affected_population": sum(
                z.affected_population or 0 for z in self.HAZARD_ZONES
            ),
            "hazard_zones_loaded": self._hazard_zones_loaded
        }
