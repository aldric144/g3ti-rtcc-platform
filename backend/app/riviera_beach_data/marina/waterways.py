"""
Waterway Service for Riviera Beach.

Manages Intracoastal Waterway and navigation channel data.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class ChannelType(str, Enum):
    """Navigation channel types."""
    ICW = "intracoastal_waterway"
    INLET = "inlet"
    HARBOR = "harbor"
    ANCHORAGE = "anchorage"
    RESTRICTED = "restricted"


class NavigationMarker(BaseModel):
    """Navigation marker/aid."""
    marker_id: str
    name: str
    marker_type: str  # buoy, daymark, light
    lat: float
    lon: float
    color: str
    light_characteristic: str | None = None
    notes: str | None = None


class WaterwayChannel(BaseModel):
    """Waterway channel information."""
    channel_id: str
    name: str
    channel_type: ChannelType
    controlling_depth_ft: float
    width_ft: float | None = None
    speed_limit_kts: int | None = None
    notes: str | None = None


class WaterwayService:
    """
    Service for waterway and navigation data for Riviera Beach.
    """
    
    # Navigation channels
    CHANNELS = [
        WaterwayChannel(
            channel_id="icw_main",
            name="Intracoastal Waterway - Lake Worth",
            channel_type=ChannelType.ICW,
            controlling_depth_ft=10.0,
            width_ft=125,
            speed_limit_kts=25,
            notes="Main ICW channel through Lake Worth"
        ),
        WaterwayChannel(
            channel_id="lake_worth_inlet",
            name="Lake Worth Inlet",
            channel_type=ChannelType.INLET,
            controlling_depth_ft=35.0,
            width_ft=400,
            notes="Main ocean access for Port of Palm Beach"
        ),
        WaterwayChannel(
            channel_id="marina_channel",
            name="Riviera Beach Marina Channel",
            channel_type=ChannelType.HARBOR,
            controlling_depth_ft=8.0,
            width_ft=75,
            speed_limit_kts=5,
            notes="No wake zone in marina basin"
        ),
        WaterwayChannel(
            channel_id="peanut_island_anchorage",
            name="Peanut Island Anchorage",
            channel_type=ChannelType.ANCHORAGE,
            controlling_depth_ft=6.0,
            notes="Popular weekend anchorage area"
        ),
        WaterwayChannel(
            channel_id="port_channel",
            name="Port of Palm Beach Ship Channel",
            channel_type=ChannelType.RESTRICTED,
            controlling_depth_ft=33.0,
            width_ft=500,
            notes="Commercial shipping - recreational vessels yield"
        ),
    ]
    
    # Navigation markers (sample)
    MARKERS = [
        NavigationMarker(
            marker_id="g1",
            name="Green 1",
            marker_type="buoy",
            lat=26.7820,
            lon=-80.0400,
            color="green",
            notes="Marina entrance"
        ),
        NavigationMarker(
            marker_id="r2",
            name="Red 2",
            marker_type="buoy",
            lat=26.7815,
            lon=-80.0410,
            color="red",
            notes="Marina entrance"
        ),
        NavigationMarker(
            marker_id="icw_g15",
            name="ICW Green 15",
            marker_type="daymark",
            lat=26.7850,
            lon=-80.0380,
            color="green",
            notes="ICW channel marker"
        ),
        NavigationMarker(
            marker_id="inlet_light",
            name="Lake Worth Inlet Light",
            marker_type="light",
            lat=26.7700,
            lon=-80.0300,
            color="white",
            light_characteristic="Fl W 6s",
            notes="Inlet entrance light"
        ),
    ]
    
    # Beach and water safety zones
    SAFETY_ZONES = [
        {
            "zone_id": "swim_zone_1",
            "name": "Singer Island Beach - Swim Zone",
            "zone_type": "swimming",
            "lat": 26.7900,
            "lon": -80.0320,
            "notes": "Lifeguard protected beach"
        },
        {
            "zone_id": "no_wake_marina",
            "name": "Marina No Wake Zone",
            "zone_type": "no_wake",
            "lat": 26.7800,
            "lon": -80.0450,
            "notes": "Idle speed only"
        },
        {
            "zone_id": "manatee_zone",
            "name": "Manatee Protection Zone",
            "zone_type": "manatee_protection",
            "lat": 26.7750,
            "lon": -80.0480,
            "notes": "Slow speed Nov-Mar"
        },
    ]
    
    def __init__(self) -> None:
        """Initialize the Waterway Service."""
        self._waterways_loaded = False
    
    async def load_waterways(self) -> dict[str, Any]:
        """Load waterway data."""
        logger.info("loading_waterways", city="Riviera Beach")
        
        features = []
        
        # Add markers
        for marker in self.MARKERS:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [marker.lon, marker.lat]},
                "properties": {
                    "marker_id": marker.marker_id,
                    "name": marker.name,
                    "marker_type": marker.marker_type,
                    "color": marker.color,
                    "category": "navigation_marker"
                },
                "id": marker.marker_id
            })
        
        # Add safety zones
        for zone in self.SAFETY_ZONES:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [zone["lon"], zone["lat"]]},
                "properties": {
                    "zone_id": zone["zone_id"],
                    "name": zone["name"],
                    "zone_type": zone["zone_type"],
                    "notes": zone["notes"],
                    "category": "safety_zone"
                },
                "id": zone["zone_id"]
            })
        
        self._waterways_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "NOAA Charts / USCG",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_channels(self) -> list[WaterwayChannel]:
        """Get navigation channels."""
        return self.CHANNELS
    
    def get_markers(self) -> list[NavigationMarker]:
        """Get navigation markers."""
        return self.MARKERS
    
    def get_safety_zones(self) -> list[dict[str, Any]]:
        """Get safety zones."""
        return self.SAFETY_ZONES
    
    def get_waterways_geojson(self) -> dict[str, Any]:
        """Get waterways as GeoJSON."""
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [m.lon, m.lat]},
                "properties": {"name": m.name, "type": m.marker_type, "category": "waterway"},
                "id": m.marker_id
            }
            for m in self.MARKERS
        ]
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of waterway data."""
        return {
            "total_channels": len(self.CHANNELS),
            "total_markers": len(self.MARKERS),
            "safety_zones": len(self.SAFETY_ZONES),
            "waterways_loaded": self._waterways_loaded
        }
