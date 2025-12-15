"""
Trash Pickup Service for Riviera Beach.

Manages trash and bulk pickup zone data.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class PickupType(str, Enum):
    """Pickup service types."""
    RESIDENTIAL_TRASH = "residential_trash"
    RESIDENTIAL_RECYCLING = "residential_recycling"
    BULK_PICKUP = "bulk_pickup"
    YARD_WASTE = "yard_waste"
    COMMERCIAL = "commercial"


class PickupZone(BaseModel):
    """Pickup zone information."""
    zone_id: str
    zone_name: str
    pickup_type: PickupType
    pickup_day: str
    pickup_time: str | None = None
    notes: str | None = None


class TrashPickupService:
    """
    Service for trash and bulk pickup data for Riviera Beach.
    """
    
    # Pickup zones
    PICKUP_ZONES = [
        # Monday zones
        PickupZone(
            zone_id="zone_a",
            zone_name="Zone A - Northwest",
            pickup_type=PickupType.RESIDENTIAL_TRASH,
            pickup_day="Monday, Thursday",
            pickup_time="7:00 AM",
            notes="West of I-95, North of Blue Heron"
        ),
        PickupZone(
            zone_id="zone_a_recycle",
            zone_name="Zone A - Northwest Recycling",
            pickup_type=PickupType.RESIDENTIAL_RECYCLING,
            pickup_day="Monday",
            pickup_time="7:00 AM"
        ),
        # Tuesday zones
        PickupZone(
            zone_id="zone_b",
            zone_name="Zone B - Northeast",
            pickup_type=PickupType.RESIDENTIAL_TRASH,
            pickup_day="Tuesday, Friday",
            pickup_time="7:00 AM",
            notes="East of I-95, North of Blue Heron"
        ),
        PickupZone(
            zone_id="zone_b_recycle",
            zone_name="Zone B - Northeast Recycling",
            pickup_type=PickupType.RESIDENTIAL_RECYCLING,
            pickup_day="Tuesday",
            pickup_time="7:00 AM"
        ),
        # Wednesday zones
        PickupZone(
            zone_id="zone_c",
            zone_name="Zone C - South",
            pickup_type=PickupType.RESIDENTIAL_TRASH,
            pickup_day="Wednesday, Saturday",
            pickup_time="7:00 AM",
            notes="South of Blue Heron Blvd"
        ),
        PickupZone(
            zone_id="zone_c_recycle",
            zone_name="Zone C - South Recycling",
            pickup_type=PickupType.RESIDENTIAL_RECYCLING,
            pickup_day="Wednesday",
            pickup_time="7:00 AM"
        ),
        # Singer Island
        PickupZone(
            zone_id="zone_si",
            zone_name="Zone SI - Singer Island",
            pickup_type=PickupType.RESIDENTIAL_TRASH,
            pickup_day="Monday, Thursday",
            pickup_time="6:00 AM",
            notes="All Singer Island residential"
        ),
        # Bulk pickup
        PickupZone(
            zone_id="bulk_north",
            zone_name="Bulk Pickup - North",
            pickup_type=PickupType.BULK_PICKUP,
            pickup_day="1st Monday of month",
            notes="North of Blue Heron Blvd"
        ),
        PickupZone(
            zone_id="bulk_south",
            zone_name="Bulk Pickup - South",
            pickup_type=PickupType.BULK_PICKUP,
            pickup_day="3rd Monday of month",
            notes="South of Blue Heron Blvd"
        ),
        # Yard waste
        PickupZone(
            zone_id="yard_waste",
            zone_name="Yard Waste Collection",
            pickup_type=PickupType.YARD_WASTE,
            pickup_day="Same as trash day",
            notes="Place at curb by 7:00 AM"
        ),
    ]
    
    # Zone boundaries (approximate)
    ZONE_BOUNDARIES = {
        "zone_a": {
            "description": "Northwest Riviera Beach",
            "bounds": {"north": 26.8100, "south": 26.7753, "east": -80.0700, "west": -80.1000}
        },
        "zone_b": {
            "description": "Northeast Riviera Beach",
            "bounds": {"north": 26.8100, "south": 26.7753, "east": -80.0450, "west": -80.0700}
        },
        "zone_c": {
            "description": "South Riviera Beach",
            "bounds": {"north": 26.7753, "south": 26.7400, "east": -80.0450, "west": -80.1000}
        },
        "zone_si": {
            "description": "Singer Island",
            "bounds": {"north": 26.8100, "south": 26.7600, "east": -80.0300, "west": -80.0450}
        },
    }
    
    def __init__(self) -> None:
        """Initialize the Trash Pickup Service."""
        self._zones_loaded = False
    
    async def load_pickup_zones(self) -> dict[str, Any]:
        """Load pickup zone data."""
        logger.info("loading_pickup_zones", city="Riviera Beach")
        
        features = []
        
        for zone_id, boundary in self.ZONE_BOUNDARIES.items():
            bounds = boundary["bounds"]
            # Create polygon from bounds
            polygon = [
                [bounds["west"], bounds["north"]],
                [bounds["east"], bounds["north"]],
                [bounds["east"], bounds["south"]],
                [bounds["west"], bounds["south"]],
                [bounds["west"], bounds["north"]],
            ]
            
            # Find matching zone info
            zone_info = next((z for z in self.PICKUP_ZONES if z.zone_id == zone_id), None)
            
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [polygon]},
                "properties": {
                    "zone_id": zone_id,
                    "name": zone_info.zone_name if zone_info else boundary["description"],
                    "pickup_day": zone_info.pickup_day if zone_info else "Unknown",
                    "pickup_type": zone_info.pickup_type.value if zone_info else "residential_trash",
                    "category": "pickup_zone"
                },
                "id": zone_id
            })
        
        self._zones_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "City of Riviera Beach Public Works",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_zones(self) -> list[PickupZone]:
        """Get pickup zones."""
        return self.PICKUP_ZONES
    
    def get_zone_for_location(self, lat: float, lon: float) -> str | None:
        """Get pickup zone for a location."""
        for zone_id, boundary in self.ZONE_BOUNDARIES.items():
            bounds = boundary["bounds"]
            if (bounds["south"] <= lat <= bounds["north"] and
                bounds["west"] <= lon <= bounds["east"]):
                return zone_id
        return None
    
    def get_pickup_schedule(self, zone_id: str) -> list[PickupZone]:
        """Get pickup schedule for a zone."""
        base_zone = zone_id.split("_")[0] + "_" + zone_id.split("_")[1] if "_" in zone_id else zone_id
        return [z for z in self.PICKUP_ZONES if z.zone_id.startswith(base_zone[:6])]
    
    def get_zones_geojson(self) -> dict[str, Any]:
        """Get zones as GeoJSON."""
        features = []
        for zone_id, boundary in self.ZONE_BOUNDARIES.items():
            bounds = boundary["bounds"]
            center_lat = (bounds["north"] + bounds["south"]) / 2
            center_lon = (bounds["east"] + bounds["west"]) / 2
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [center_lon, center_lat]},
                "properties": {"zone_id": zone_id, "name": boundary["description"], "category": "pickup_zone"},
                "id": zone_id
            })
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of pickup zone data."""
        return {
            "total_zones": len(self.ZONE_BOUNDARIES),
            "pickup_schedules": len(self.PICKUP_ZONES),
            "zones_loaded": self._zones_loaded
        }
