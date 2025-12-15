"""
Streetlight Service for Riviera Beach.

Manages streetlight location and status data.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class LightType(str, Enum):
    """Streetlight types."""
    LED = "led"
    HPS = "high_pressure_sodium"
    METAL_HALIDE = "metal_halide"
    DECORATIVE = "decorative"


class LightStatus(str, Enum):
    """Streetlight status."""
    OPERATIONAL = "operational"
    OUT = "out"
    MAINTENANCE = "maintenance"
    SCHEDULED_REPLACEMENT = "scheduled_replacement"


class Streetlight(BaseModel):
    """Streetlight information."""
    light_id: str
    pole_number: str
    lat: float
    lon: float
    light_type: LightType
    wattage: int
    status: LightStatus = LightStatus.OPERATIONAL
    owner: str = "City of Riviera Beach"
    circuit: str | None = None
    last_maintained: str | None = None


class StreetlightService:
    """
    Service for streetlight data for Riviera Beach.
    """
    
    # Sample streetlights (representative locations along major roads)
    STREETLIGHTS = [
        # Blue Heron Blvd
        Streetlight(light_id="sl_001", pole_number="BH-001", lat=26.7753, lon=-80.0500, light_type=LightType.LED, wattage=150, circuit="BH-1"),
        Streetlight(light_id="sl_002", pole_number="BH-002", lat=26.7753, lon=-80.0520, light_type=LightType.LED, wattage=150, circuit="BH-1"),
        Streetlight(light_id="sl_003", pole_number="BH-003", lat=26.7753, lon=-80.0540, light_type=LightType.LED, wattage=150, circuit="BH-1"),
        Streetlight(light_id="sl_004", pole_number="BH-004", lat=26.7753, lon=-80.0560, light_type=LightType.LED, wattage=150, circuit="BH-1"),
        Streetlight(light_id="sl_005", pole_number="BH-005", lat=26.7753, lon=-80.0580, light_type=LightType.LED, wattage=150, circuit="BH-1"),
        Streetlight(light_id="sl_006", pole_number="BH-006", lat=26.7753, lon=-80.0600, light_type=LightType.LED, wattage=150, circuit="BH-2"),
        Streetlight(light_id="sl_007", pole_number="BH-007", lat=26.7753, lon=-80.0620, light_type=LightType.LED, wattage=150, circuit="BH-2"),
        Streetlight(light_id="sl_008", pole_number="BH-008", lat=26.7753, lon=-80.0640, light_type=LightType.LED, wattage=150, circuit="BH-2"),
        
        # Broadway
        Streetlight(light_id="sl_101", pole_number="BR-001", lat=26.7700, lon=-80.0583, light_type=LightType.LED, wattage=100, circuit="BR-1"),
        Streetlight(light_id="sl_102", pole_number="BR-002", lat=26.7720, lon=-80.0583, light_type=LightType.LED, wattage=100, circuit="BR-1"),
        Streetlight(light_id="sl_103", pole_number="BR-003", lat=26.7740, lon=-80.0583, light_type=LightType.LED, wattage=100, circuit="BR-1"),
        Streetlight(light_id="sl_104", pole_number="BR-004", lat=26.7760, lon=-80.0583, light_type=LightType.LED, wattage=100, circuit="BR-1"),
        Streetlight(light_id="sl_105", pole_number="BR-005", lat=26.7780, lon=-80.0583, light_type=LightType.LED, wattage=100, circuit="BR-1"),
        
        # Marina District (decorative)
        Streetlight(light_id="sl_201", pole_number="MD-001", lat=26.7800, lon=-80.0450, light_type=LightType.DECORATIVE, wattage=75, circuit="MD-1"),
        Streetlight(light_id="sl_202", pole_number="MD-002", lat=26.7798, lon=-80.0455, light_type=LightType.DECORATIVE, wattage=75, circuit="MD-1"),
        Streetlight(light_id="sl_203", pole_number="MD-003", lat=26.7796, lon=-80.0460, light_type=LightType.DECORATIVE, wattage=75, circuit="MD-1"),
        
        # Singer Island
        Streetlight(light_id="sl_301", pole_number="SI-001", lat=26.7900, lon=-80.0350, light_type=LightType.LED, wattage=150, circuit="SI-1"),
        Streetlight(light_id="sl_302", pole_number="SI-002", lat=26.7920, lon=-80.0350, light_type=LightType.LED, wattage=150, circuit="SI-1"),
        Streetlight(light_id="sl_303", pole_number="SI-003", lat=26.7940, lon=-80.0350, light_type=LightType.LED, wattage=150, circuit="SI-1"),
    ]
    
    # Streetlight statistics
    STATISTICS = {
        "total_lights": 2850,
        "led_converted": 2100,
        "conversion_rate": 73.7,
        "average_age_years": 12,
        "annual_maintenance_budget": 450000,
        "energy_savings_annual": 185000
    }
    
    def __init__(self) -> None:
        """Initialize the Streetlight Service."""
        self._streetlights_loaded = False
    
    async def load_streetlights(self) -> dict[str, Any]:
        """Load streetlight data."""
        logger.info("loading_streetlights", city="Riviera Beach")
        
        features = []
        
        for light in self.STREETLIGHTS:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [light.lon, light.lat]},
                "properties": {
                    "light_id": light.light_id,
                    "pole_number": light.pole_number,
                    "light_type": light.light_type.value,
                    "wattage": light.wattage,
                    "status": light.status.value,
                    "circuit": light.circuit,
                    "category": "streetlight"
                },
                "id": light.light_id
            })
        
        self._streetlights_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "City of Riviera Beach Public Works",
                "note": "Sample data - full dataset contains ~2850 lights",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_streetlights(self) -> list[Streetlight]:
        """Get streetlights."""
        return self.STREETLIGHTS
    
    def get_lights_by_type(self, light_type: LightType) -> list[Streetlight]:
        """Get lights by type."""
        return [l for l in self.STREETLIGHTS if l.light_type == light_type]
    
    def get_lights_by_status(self, status: LightStatus) -> list[Streetlight]:
        """Get lights by status."""
        return [l for l in self.STREETLIGHTS if l.status == status]
    
    def get_statistics(self) -> dict[str, Any]:
        """Get streetlight statistics."""
        return self.STATISTICS
    
    def get_streetlights_geojson(self) -> dict[str, Any]:
        """Get streetlights as GeoJSON."""
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [l.lon, l.lat]},
                "properties": {"pole": l.pole_number, "type": l.light_type.value, "category": "streetlight"},
                "id": l.light_id
            }
            for l in self.STREETLIGHTS
        ]
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of streetlight data."""
        return {
            "sample_lights": len(self.STREETLIGHTS),
            "total_city_lights": self.STATISTICS["total_lights"],
            "led_conversion_rate": self.STATISTICS["conversion_rate"],
            "streetlights_loaded": self._streetlights_loaded
        }
