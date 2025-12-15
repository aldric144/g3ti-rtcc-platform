"""
Stormwater Infrastructure Service for Riviera Beach.

Manages stormwater drainage infrastructure data.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class InfrastructureType(str, Enum):
    """Stormwater infrastructure types."""
    STORM_DRAIN = "storm_drain"
    CATCH_BASIN = "catch_basin"
    OUTFALL = "outfall"
    RETENTION_POND = "retention_pond"
    PUMP_STATION = "pump_station"
    CANAL = "canal"
    CULVERT = "culvert"


class StormwaterAsset(BaseModel):
    """Stormwater infrastructure asset."""
    asset_id: str
    name: str
    asset_type: InfrastructureType
    lat: float
    lon: float
    capacity: str | None = None
    condition: str | None = None
    last_inspected: str | None = None
    notes: str | None = None


class StormwaterService:
    """
    Service for stormwater infrastructure data for Riviera Beach.
    """
    
    # Stormwater assets (sample)
    STORMWATER_ASSETS = [
        StormwaterAsset(
            asset_id="pump_1",
            name="Blue Heron Stormwater Pump Station",
            asset_type=InfrastructureType.PUMP_STATION,
            lat=26.7753,
            lon=-80.0650,
            capacity="5000 GPM",
            condition="Good",
            notes="Primary pump station for central drainage"
        ),
        StormwaterAsset(
            asset_id="pump_2",
            name="Singer Island Pump Station",
            asset_type=InfrastructureType.PUMP_STATION,
            lat=26.7900,
            lon=-80.0380,
            capacity="3000 GPM",
            condition="Good",
            notes="Serves Singer Island drainage"
        ),
        StormwaterAsset(
            asset_id="pond_1",
            name="Northwest Retention Pond",
            asset_type=InfrastructureType.RETENTION_POND,
            lat=26.7850,
            lon=-80.0800,
            capacity="2.5 acre-feet",
            condition="Good"
        ),
        StormwaterAsset(
            asset_id="pond_2",
            name="Industrial Area Retention",
            asset_type=InfrastructureType.RETENTION_POND,
            lat=26.7650,
            lon=-80.0700,
            capacity="3.0 acre-feet",
            condition="Fair"
        ),
        StormwaterAsset(
            asset_id="outfall_1",
            name="Lake Worth Outfall #1",
            asset_type=InfrastructureType.OUTFALL,
            lat=26.7800,
            lon=-80.0480,
            notes="Discharges to Lake Worth Lagoon"
        ),
        StormwaterAsset(
            asset_id="outfall_2",
            name="Intracoastal Outfall #2",
            asset_type=InfrastructureType.OUTFALL,
            lat=26.7750,
            lon=-80.0450,
            notes="Discharges to Intracoastal Waterway"
        ),
        StormwaterAsset(
            asset_id="canal_1",
            name="C-17 Canal",
            asset_type=InfrastructureType.CANAL,
            lat=26.7700,
            lon=-80.0900,
            notes="SFWMD canal - primary drainage"
        ),
    ]
    
    # Drainage basins
    DRAINAGE_BASINS = [
        {
            "basin_id": "basin_north",
            "name": "North Basin",
            "area_acres": 850,
            "primary_outfall": "outfall_1"
        },
        {
            "basin_id": "basin_central",
            "name": "Central Basin",
            "area_acres": 1200,
            "primary_outfall": "outfall_2"
        },
        {
            "basin_id": "basin_south",
            "name": "South Basin",
            "area_acres": 650,
            "primary_outfall": "canal_1"
        },
    ]
    
    def __init__(self) -> None:
        """Initialize the Stormwater Service."""
        self._infrastructure_loaded = False
    
    async def load_infrastructure(self) -> dict[str, Any]:
        """Load stormwater infrastructure data."""
        logger.info("loading_stormwater_infrastructure", city="Riviera Beach")
        
        features = []
        
        for asset in self.STORMWATER_ASSETS:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [asset.lon, asset.lat]},
                "properties": {
                    "asset_id": asset.asset_id,
                    "name": asset.name,
                    "asset_type": asset.asset_type.value,
                    "capacity": asset.capacity,
                    "condition": asset.condition,
                    "notes": asset.notes,
                    "category": "stormwater"
                },
                "id": asset.asset_id
            })
        
        self._infrastructure_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "City of Riviera Beach Public Works",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_assets(self) -> list[StormwaterAsset]:
        """Get stormwater assets."""
        return self.STORMWATER_ASSETS
    
    def get_assets_by_type(self, asset_type: InfrastructureType) -> list[StormwaterAsset]:
        """Get assets by type."""
        return [a for a in self.STORMWATER_ASSETS if a.asset_type == asset_type]
    
    def get_drainage_basins(self) -> list[dict[str, Any]]:
        """Get drainage basins."""
        return self.DRAINAGE_BASINS
    
    def get_infrastructure_geojson(self) -> dict[str, Any]:
        """Get infrastructure as GeoJSON."""
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [a.lon, a.lat]},
                "properties": {"name": a.name, "type": a.asset_type.value, "category": "stormwater"},
                "id": a.asset_id
            }
            for a in self.STORMWATER_ASSETS
        ]
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of stormwater data."""
        return {
            "total_assets": len(self.STORMWATER_ASSETS),
            "by_type": {it.value: len(self.get_assets_by_type(it)) for it in InfrastructureType},
            "drainage_basins": len(self.DRAINAGE_BASINS),
            "infrastructure_loaded": self._infrastructure_loaded
        }
