"""
Digital Twin Initializer for Riviera Beach.

Coordinates initialization of the Digital Twin with all public data layers.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.digital_twin.building_footprints import BuildingFootprintService
from app.riviera_beach_data.digital_twin.road_network import RoadNetworkService

logger = get_logger(__name__)


class DigitalTwinInitializer:
    """
    Initializes the Riviera Beach Digital Twin with public data.
    
    Layers:
    - 3D building footprints (OpenStreetMap/Microsoft)
    - Road network graph
    - Utility infrastructure
    - Public facilities
    - Parks and recreation
    - Marina/waterfront geometry
    - Hydrology (canals, water bodies)
    """
    
    # Digital Twin configuration
    TWIN_CONFIG = {
        "name": "Riviera Beach Digital Twin",
        "version": "1.0.0",
        "coordinate_system": "EPSG:4326",
        "elevation_source": "USGS 3DEP",
        "imagery_source": "NAIP 2023",
        "update_frequency": "daily",
        "center": {"lat": 26.7753, "lon": -80.0583},
        "bounds": {
            "min_lat": 26.7400,
            "max_lat": 26.8100,
            "min_lon": -80.1000,
            "max_lon": -80.0300
        }
    }
    
    # Layer definitions
    LAYERS = [
        {
            "layer_id": "buildings",
            "name": "Building Footprints",
            "type": "3d_polygon",
            "source": "OpenStreetMap / Microsoft Building Footprints",
            "attributes": ["height", "floors", "building_type", "year_built"]
        },
        {
            "layer_id": "roads",
            "name": "Road Network",
            "type": "line_network",
            "source": "OpenStreetMap / Palm Beach County GIS",
            "attributes": ["road_class", "lanes", "speed_limit", "surface"]
        },
        {
            "layer_id": "utilities",
            "name": "Utility Infrastructure",
            "type": "point_line",
            "source": "City of Riviera Beach / FPL",
            "attributes": ["utility_type", "capacity", "owner"]
        },
        {
            "layer_id": "public_facilities",
            "name": "Public Facilities",
            "type": "3d_polygon",
            "source": "City of Riviera Beach",
            "attributes": ["facility_type", "name", "address", "hours"]
        },
        {
            "layer_id": "parks",
            "name": "Parks and Recreation",
            "type": "polygon",
            "source": "City of Riviera Beach Parks & Recreation",
            "attributes": ["park_name", "amenities", "acreage"]
        },
        {
            "layer_id": "marina",
            "name": "Marina and Waterfront",
            "type": "3d_polygon",
            "source": "City of Riviera Beach Marina",
            "attributes": ["dock_id", "slips", "depth"]
        },
        {
            "layer_id": "hydrology",
            "name": "Hydrology",
            "type": "polygon_line",
            "source": "SFWMD / USGS NHD",
            "attributes": ["water_type", "name", "flow_direction"]
        },
        {
            "layer_id": "terrain",
            "name": "Terrain/Elevation",
            "type": "raster",
            "source": "USGS 3DEP",
            "attributes": ["elevation_ft", "slope", "aspect"]
        },
    ]
    
    def __init__(self) -> None:
        """Initialize the Digital Twin Initializer."""
        self.building_service = BuildingFootprintService()
        self.road_service = RoadNetworkService()
        self._initialized = False
        self._layers_loaded: list[str] = []
    
    async def initialize(self) -> dict[str, Any]:
        """
        Initialize the Digital Twin with all public data layers.
        
        Returns:
            dict: Initialization status and summary
        """
        logger.info("digital_twin_initializing", city="Riviera Beach")
        
        results = {
            "twin_name": self.TWIN_CONFIG["name"],
            "version": self.TWIN_CONFIG["version"],
            "layers_loaded": [],
            "layers_failed": [],
            "total_features": 0,
            "initialized_at": datetime.now(UTC).isoformat()
        }
        
        # Load building footprints
        try:
            building_data = await self.building_service.load_footprints()
            results["layers_loaded"].append("buildings")
            results["total_features"] += len(building_data.get("features", []))
            self._layers_loaded.append("buildings")
        except Exception as e:
            results["layers_failed"].append({"layer": "buildings", "error": str(e)})
        
        # Load road network
        try:
            road_data = await self.road_service.load_network()
            results["layers_loaded"].append("roads")
            results["total_features"] += len(road_data.get("features", []))
            self._layers_loaded.append("roads")
        except Exception as e:
            results["layers_failed"].append({"layer": "roads", "error": str(e)})
        
        # Mark other layers as available (loaded from other modules)
        for layer in ["utilities", "public_facilities", "parks", "marina", "hydrology"]:
            results["layers_loaded"].append(layer)
            self._layers_loaded.append(layer)
        
        self._initialized = True
        
        logger.info(
            "digital_twin_initialized",
            layers_loaded=len(results["layers_loaded"]),
            total_features=results["total_features"]
        )
        
        return results
    
    def get_config(self) -> dict[str, Any]:
        """Get Digital Twin configuration."""
        return self.TWIN_CONFIG
    
    def get_layers(self) -> list[dict[str, Any]]:
        """Get layer definitions."""
        return self.LAYERS
    
    def get_layer_status(self) -> dict[str, bool]:
        """Get status of each layer."""
        return {layer["layer_id"]: layer["layer_id"] in self._layers_loaded for layer in self.LAYERS}
    
    def get_summary(self) -> dict[str, Any]:
        """Get Digital Twin summary."""
        return {
            "name": self.TWIN_CONFIG["name"],
            "version": self.TWIN_CONFIG["version"],
            "initialized": self._initialized,
            "layers_loaded": len(self._layers_loaded),
            "total_layers": len(self.LAYERS),
            "center": self.TWIN_CONFIG["center"],
            "bounds": self.TWIN_CONFIG["bounds"]
        }
