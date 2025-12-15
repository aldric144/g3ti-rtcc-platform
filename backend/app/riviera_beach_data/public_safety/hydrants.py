"""
Fire Hydrant Service for Riviera Beach.

Manages fire hydrant location and flow class data from Palm Beach County GIS.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class HydrantFlowClass(str, Enum):
    """Fire hydrant flow classification (NFPA color coding)."""
    CLASS_AA = "AA"  # 1500+ GPM - Light Blue
    CLASS_A = "A"    # 1000-1499 GPM - Green
    CLASS_B = "B"    # 500-999 GPM - Orange
    CLASS_C = "C"    # Below 500 GPM - Red
    UNKNOWN = "unknown"


class HydrantStatus(str, Enum):
    """Hydrant operational status."""
    IN_SERVICE = "in_service"
    OUT_OF_SERVICE = "out_of_service"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class FireHydrant(BaseModel):
    """Fire hydrant information."""
    hydrant_id: str
    lat: float
    lon: float
    flow_class: HydrantFlowClass = HydrantFlowClass.UNKNOWN
    flow_gpm: int | None = None
    status: HydrantStatus = HydrantStatus.UNKNOWN
    address_near: str | None = None
    main_size_inches: float | None = None
    last_tested: str | None = None
    owner: str = "City of Riviera Beach"


class HydrantService:
    """
    Service for managing fire hydrant data for Riviera Beach.
    
    Data source: Palm Beach County GIS
    
    Provides:
    - Hydrant locations
    - Flow class information
    - Hydrant status
    - Spatial queries
    """
    
    # Palm Beach County GIS REST API for hydrants
    PBC_GIS_HYDRANT_URL = "https://maps.pbcgov.org/arcgis/rest/services/Utilities/MapServer/0/query"
    
    # Riviera Beach bounding box
    BBOX = {
        "min_lat": 26.7400,
        "max_lat": 26.8100,
        "min_lon": -80.1000,
        "max_lon": -80.0300
    }
    
    # Sample hydrant data (representative locations)
    SAMPLE_HYDRANTS = [
        FireHydrant(
            hydrant_id="h001",
            lat=26.7753,
            lon=-80.0620,
            flow_class=HydrantFlowClass.CLASS_A,
            flow_gpm=1200,
            status=HydrantStatus.IN_SERVICE,
            address_near="600 W Blue Heron Blvd",
            main_size_inches=8.0
        ),
        FireHydrant(
            hydrant_id="h002",
            lat=26.7753,
            lon=-80.0583,
            flow_class=HydrantFlowClass.CLASS_A,
            flow_gpm=1100,
            status=HydrantStatus.IN_SERVICE,
            address_near="Blue Heron Blvd & Broadway",
            main_size_inches=8.0
        ),
        FireHydrant(
            hydrant_id="h003",
            lat=26.7800,
            lon=-80.0500,
            flow_class=HydrantFlowClass.CLASS_B,
            flow_gpm=800,
            status=HydrantStatus.IN_SERVICE,
            address_near="200 E 13th St",
            main_size_inches=6.0
        ),
        FireHydrant(
            hydrant_id="h004",
            lat=26.7900,
            lon=-80.0350,
            flow_class=HydrantFlowClass.CLASS_A,
            flow_gpm=1300,
            status=HydrantStatus.IN_SERVICE,
            address_near="2500 N Ocean Dr",
            main_size_inches=8.0
        ),
        FireHydrant(
            hydrant_id="h005",
            lat=26.7650,
            lon=-80.0583,
            flow_class=HydrantFlowClass.CLASS_B,
            flow_gpm=750,
            status=HydrantStatus.IN_SERVICE,
            address_near="Broadway & Avenue E",
            main_size_inches=6.0
        ),
        FireHydrant(
            hydrant_id="h006",
            lat=26.7700,
            lon=-80.0700,
            flow_class=HydrantFlowClass.CLASS_A,
            flow_gpm=1400,
            status=HydrantStatus.IN_SERVICE,
            address_near="I-95 & Blue Heron Blvd",
            main_size_inches=10.0
        ),
        FireHydrant(
            hydrant_id="h007",
            lat=26.7600,
            lon=-80.0450,
            flow_class=HydrantFlowClass.CLASS_B,
            flow_gpm=900,
            status=HydrantStatus.IN_SERVICE,
            address_near="Port of Palm Beach",
            main_size_inches=8.0
        ),
        FireHydrant(
            hydrant_id="h008",
            lat=26.7850,
            lon=-80.0400,
            flow_class=HydrantFlowClass.CLASS_A,
            flow_gpm=1150,
            status=HydrantStatus.IN_SERVICE,
            address_near="Marina District",
            main_size_inches=8.0
        ),
    ]
    
    def __init__(self) -> None:
        """Initialize the Hydrant Service."""
        self._hydrants: list[FireHydrant] = []
        self._hydrants_loaded = False
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
    
    async def load_hydrants(self) -> dict[str, Any]:
        """
        Load fire hydrant data.
        
        Attempts to load from Palm Beach County GIS, falls back to sample data.
        
        Returns:
            dict: GeoJSON feature collection of hydrants
        """
        logger.info("loading_hydrants", city="Riviera Beach")
        
        # Try to load from PBC GIS
        try:
            hydrants = await self._load_from_pbc_gis()
            if hydrants:
                self._hydrants = hydrants
                logger.info("hydrants_loaded_from_gis", count=len(hydrants))
        except Exception as e:
            logger.warning("hydrant_gis_load_failed", error=str(e))
        
        # Fall back to sample data if GIS load failed
        if not self._hydrants:
            self._hydrants = self.SAMPLE_HYDRANTS
            logger.info("hydrants_loaded_from_sample", count=len(self._hydrants))
        
        self._hydrants_loaded = True
        
        return self.get_hydrants_geojson()
    
    async def _load_from_pbc_gis(self) -> list[FireHydrant]:
        """
        Load hydrants from Palm Beach County GIS.
        
        Returns:
            List of FireHydrant objects
        """
        params = {
            "geometry": f"{self.BBOX['min_lon']},{self.BBOX['min_lat']},{self.BBOX['max_lon']},{self.BBOX['max_lat']}",
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "f": "geojson",
            "outSR": "4326",
            "resultRecordCount": 1000
        }
        
        client = await self._get_client()
        response = await client.get(self.PBC_GIS_HYDRANT_URL, params=params)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        hydrants = []
        
        for i, feature in enumerate(data.get("features", [])):
            geom = feature.get("geometry", {})
            props = feature.get("properties", {})
            
            if geom.get("type") != "Point":
                continue
            
            coords = geom.get("coordinates", [])
            if len(coords) < 2:
                continue
            
            # Parse flow class from properties
            flow_gpm = props.get("FLOW_GPM") or props.get("flow_gpm")
            flow_class = self._determine_flow_class(flow_gpm)
            
            hydrants.append(FireHydrant(
                hydrant_id=f"h{i:04d}",
                lat=coords[1],
                lon=coords[0],
                flow_class=flow_class,
                flow_gpm=flow_gpm,
                status=HydrantStatus.IN_SERVICE,
                address_near=props.get("ADDRESS") or props.get("address"),
                main_size_inches=props.get("MAIN_SIZE") or props.get("main_size")
            ))
        
        return hydrants
    
    def _determine_flow_class(self, flow_gpm: int | None) -> HydrantFlowClass:
        """Determine flow class based on GPM."""
        if flow_gpm is None:
            return HydrantFlowClass.UNKNOWN
        if flow_gpm >= 1500:
            return HydrantFlowClass.CLASS_AA
        if flow_gpm >= 1000:
            return HydrantFlowClass.CLASS_A
        if flow_gpm >= 500:
            return HydrantFlowClass.CLASS_B
        return HydrantFlowClass.CLASS_C
    
    def get_hydrants(self) -> list[FireHydrant]:
        """Get list of hydrants."""
        return self._hydrants if self._hydrants else self.SAMPLE_HYDRANTS
    
    def get_hydrant_by_id(self, hydrant_id: str) -> FireHydrant | None:
        """
        Get hydrant by ID.
        
        Args:
            hydrant_id: Hydrant identifier
            
        Returns:
            FireHydrant or None
        """
        for hydrant in self.get_hydrants():
            if hydrant.hydrant_id == hydrant_id:
                return hydrant
        return None
    
    def get_hydrants_by_flow_class(self, flow_class: HydrantFlowClass) -> list[FireHydrant]:
        """
        Get hydrants by flow class.
        
        Args:
            flow_class: Flow classification
            
        Returns:
            List of matching hydrants
        """
        return [h for h in self.get_hydrants() if h.flow_class == flow_class]
    
    def get_hydrants_in_radius(
        self, lat: float, lon: float, radius_miles: float = 0.5
    ) -> list[FireHydrant]:
        """
        Get hydrants within a radius of a location.
        
        Args:
            lat: Center latitude
            lon: Center longitude
            radius_miles: Search radius in miles
            
        Returns:
            List of hydrants within radius
        """
        # Approximate conversion: 1 degree lat ≈ 69 miles
        radius_deg = radius_miles / 69.0
        
        return [
            h for h in self.get_hydrants()
            if ((h.lat - lat) ** 2 + (h.lon - lon) ** 2) ** 0.5 <= radius_deg
        ]
    
    def get_nearest_hydrant(self, lat: float, lon: float) -> FireHydrant | None:
        """
        Get nearest hydrant to a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Nearest FireHydrant or None
        """
        hydrants = self.get_hydrants()
        if not hydrants:
            return None
        
        def distance_sq(h: FireHydrant) -> float:
            return (h.lat - lat) ** 2 + (h.lon - lon) ** 2
        
        return min(hydrants, key=distance_sq)
    
    def get_hydrants_geojson(self) -> dict[str, Any]:
        """
        Get hydrants as GeoJSON.
        
        Returns:
            dict: GeoJSON feature collection
        """
        hydrants = self.get_hydrants()
        
        # Color mapping for flow classes (NFPA standard)
        color_map = {
            HydrantFlowClass.CLASS_AA: "#87CEEB",  # Light Blue
            HydrantFlowClass.CLASS_A: "#00FF00",   # Green
            HydrantFlowClass.CLASS_B: "#FFA500",   # Orange
            HydrantFlowClass.CLASS_C: "#FF0000",   # Red
            HydrantFlowClass.UNKNOWN: "#808080",   # Gray
        }
        
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [h.lon, h.lat]
                },
                "properties": {
                    "hydrant_id": h.hydrant_id,
                    "flow_class": h.flow_class.value,
                    "flow_gpm": h.flow_gpm,
                    "status": h.status.value,
                    "address_near": h.address_near,
                    "main_size_inches": h.main_size_inches,
                    "owner": h.owner,
                    "marker_color": color_map.get(h.flow_class, "#808080"),
                    "category": "hydrant"
                },
                "id": h.hydrant_id
            }
            for h in hydrants
        ]
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Palm Beach County GIS / Sample Data",
                "color_legend": {
                    "Light Blue (AA)": "1500+ GPM",
                    "Green (A)": "1000-1499 GPM",
                    "Orange (B)": "500-999 GPM",
                    "Red (C)": "Below 500 GPM"
                },
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of hydrant data."""
        hydrants = self.get_hydrants()
        
        return {
            "total_hydrants": len(hydrants),
            "by_flow_class": {
                fc.value: len(self.get_hydrants_by_flow_class(fc))
                for fc in HydrantFlowClass
            },
            "hydrants_loaded": self._hydrants_loaded,
            "data_source": "PBC GIS" if self._hydrants else "Sample Data"
        }
