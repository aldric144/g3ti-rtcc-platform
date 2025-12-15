"""
Road Centerline Service for Riviera Beach.

Manages road network data including centerlines, intersections, and routing.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.riviera_beach_data.gis.boundary_loader import (
    BoundaryType,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GISBoundaryLoader,
)

logger = get_logger(__name__)


class RoadClass(str, Enum):
    """Road classification types."""
    INTERSTATE = "interstate"
    US_HIGHWAY = "us_highway"
    STATE_HIGHWAY = "state_highway"
    MAJOR_ARTERIAL = "major_arterial"
    MINOR_ARTERIAL = "minor_arterial"
    COLLECTOR = "collector"
    LOCAL = "local"
    PRIVATE = "private"


class RoadInfo(BaseModel):
    """Road information."""
    name: str
    road_class: RoadClass
    speed_limit: int | None = None
    lanes: int | None = None
    one_way: bool = False
    surface_type: str = "paved"
    length_miles: float | None = None


class IntersectionInfo(BaseModel):
    """Intersection information."""
    intersection_id: str
    street_1: str
    street_2: str
    lat: float
    lon: float
    signal_type: str | None = None  # "traffic_light", "stop_sign", "yield", None
    is_major: bool = False


class RoadCenterlineService:
    """
    Service for managing road centerline data for Riviera Beach.
    
    Provides:
    - Road centerline geometry access
    - Road classification and attributes
    - Intersection data
    - Major corridor identification
    - Choke point analysis
    """
    
    # Major roads in Riviera Beach
    MAJOR_ROADS = [
        RoadInfo(
            name="Interstate 95",
            road_class=RoadClass.INTERSTATE,
            speed_limit=70,
            lanes=6,
            one_way=False,
            length_miles=4.2
        ),
        RoadInfo(
            name="US Highway 1 (Federal Highway)",
            road_class=RoadClass.US_HIGHWAY,
            speed_limit=45,
            lanes=4,
            one_way=False,
            length_miles=3.8
        ),
        RoadInfo(
            name="Blue Heron Boulevard",
            road_class=RoadClass.MAJOR_ARTERIAL,
            speed_limit=45,
            lanes=4,
            one_way=False,
            length_miles=2.5
        ),
        RoadInfo(
            name="Broadway",
            road_class=RoadClass.MAJOR_ARTERIAL,
            speed_limit=35,
            lanes=4,
            one_way=False,
            length_miles=2.8
        ),
        RoadInfo(
            name="Avenue E",
            road_class=RoadClass.MINOR_ARTERIAL,
            speed_limit=30,
            lanes=2,
            one_way=False,
            length_miles=1.5
        ),
        RoadInfo(
            name="Singer Island Road",
            road_class=RoadClass.COLLECTOR,
            speed_limit=35,
            lanes=2,
            one_way=False,
            length_miles=2.0
        ),
        RoadInfo(
            name="13th Street",
            road_class=RoadClass.COLLECTOR,
            speed_limit=30,
            lanes=2,
            one_way=False,
            length_miles=1.2
        ),
        RoadInfo(
            name="President Barack Obama Highway",
            road_class=RoadClass.MAJOR_ARTERIAL,
            speed_limit=45,
            lanes=4,
            one_way=False,
            length_miles=1.8
        ),
    ]
    
    # Major intersections
    MAJOR_INTERSECTIONS = [
        IntersectionInfo(
            intersection_id="int_001",
            street_1="Blue Heron Boulevard",
            street_2="Broadway",
            lat=26.7753,
            lon=-80.0583,
            signal_type="traffic_light",
            is_major=True
        ),
        IntersectionInfo(
            intersection_id="int_002",
            street_1="Blue Heron Boulevard",
            street_2="US Highway 1",
            lat=26.7753,
            lon=-80.0500,
            signal_type="traffic_light",
            is_major=True
        ),
        IntersectionInfo(
            intersection_id="int_003",
            street_1="Blue Heron Boulevard",
            street_2="I-95 Ramp",
            lat=26.7753,
            lon=-80.0700,
            signal_type="traffic_light",
            is_major=True
        ),
        IntersectionInfo(
            intersection_id="int_004",
            street_1="Broadway",
            street_2="Avenue E",
            lat=26.7650,
            lon=-80.0583,
            signal_type="traffic_light",
            is_major=True
        ),
        IntersectionInfo(
            intersection_id="int_005",
            street_1="Broadway",
            street_2="13th Street",
            lat=26.7800,
            lon=-80.0583,
            signal_type="traffic_light",
            is_major=True
        ),
    ]
    
    # Choke points (areas prone to congestion or limited access)
    CHOKE_POINTS = [
        {
            "name": "Blue Heron Bridge",
            "type": "bridge",
            "lat": 26.7753,
            "lon": -80.0400,
            "description": "Bridge connecting mainland to Singer Island",
            "risk_level": "high",
            "evacuation_critical": True
        },
        {
            "name": "I-95 Blue Heron Interchange",
            "type": "interchange",
            "lat": 26.7753,
            "lon": -80.0700,
            "description": "Major highway interchange",
            "risk_level": "medium",
            "evacuation_critical": True
        },
        {
            "name": "Port of Palm Beach Entrance",
            "type": "port_access",
            "lat": 26.7650,
            "lon": -80.0450,
            "description": "Port access road",
            "risk_level": "medium",
            "evacuation_critical": False
        },
    ]
    
    def __init__(self, boundary_loader: GISBoundaryLoader | None = None) -> None:
        """Initialize the Road Centerline Service."""
        self._loader = boundary_loader or GISBoundaryLoader()
        self._centerlines: GeoJSONFeatureCollection | None = None
    
    async def load_centerlines(self) -> GeoJSONFeatureCollection:
        """
        Load road centerline data.
        
        Returns:
            GeoJSONFeatureCollection: Road centerline features
        """
        if self._centerlines is None:
            self._centerlines = await self._loader.load_road_centerlines()
            logger.info(
                "road_centerlines_loaded",
                city="Riviera Beach",
                road_count=len(self._centerlines.features)
            )
        return self._centerlines
    
    def get_centerlines(self) -> GeoJSONFeatureCollection | None:
        """Get loaded road centerlines."""
        return self._centerlines
    
    def get_major_roads(self) -> list[RoadInfo]:
        """Get list of major roads."""
        return self.MAJOR_ROADS
    
    def get_road_by_name(self, name: str) -> RoadInfo | None:
        """
        Get road information by name.
        
        Args:
            name: Road name (partial match supported)
            
        Returns:
            RoadInfo or None
        """
        name_lower = name.lower()
        for road in self.MAJOR_ROADS:
            if name_lower in road.name.lower():
                return road
        return None
    
    def get_roads_by_class(self, road_class: RoadClass) -> list[RoadInfo]:
        """
        Get roads by classification.
        
        Args:
            road_class: Road classification
            
        Returns:
            List of matching roads
        """
        return [r for r in self.MAJOR_ROADS if r.road_class == road_class]
    
    def get_major_intersections(self) -> list[IntersectionInfo]:
        """Get list of major intersections."""
        return self.MAJOR_INTERSECTIONS
    
    def get_intersection_by_streets(
        self, street_1: str, street_2: str
    ) -> IntersectionInfo | None:
        """
        Get intersection by street names.
        
        Args:
            street_1: First street name
            street_2: Second street name
            
        Returns:
            IntersectionInfo or None
        """
        s1_lower = street_1.lower()
        s2_lower = street_2.lower()
        
        for intersection in self.MAJOR_INTERSECTIONS:
            if (
                (s1_lower in intersection.street_1.lower() and 
                 s2_lower in intersection.street_2.lower()) or
                (s2_lower in intersection.street_1.lower() and 
                 s1_lower in intersection.street_2.lower())
            ):
                return intersection
        return None
    
    def get_choke_points(self) -> list[dict[str, Any]]:
        """Get list of traffic choke points."""
        return self.CHOKE_POINTS
    
    def get_evacuation_routes(self) -> list[dict[str, Any]]:
        """
        Get evacuation route information.
        
        Returns:
            List of evacuation routes
        """
        return [
            {
                "name": "I-95 North",
                "direction": "north",
                "access_points": ["Blue Heron Boulevard", "45th Street"],
                "capacity": "high",
                "notes": "Primary evacuation route northbound"
            },
            {
                "name": "I-95 South",
                "direction": "south",
                "access_points": ["Blue Heron Boulevard", "45th Street"],
                "capacity": "high",
                "notes": "Primary evacuation route southbound"
            },
            {
                "name": "US-1 North",
                "direction": "north",
                "access_points": ["Blue Heron Boulevard", "Broadway"],
                "capacity": "medium",
                "notes": "Secondary evacuation route"
            },
            {
                "name": "Blue Heron Boulevard West",
                "direction": "west",
                "access_points": ["Broadway", "US-1"],
                "capacity": "medium",
                "notes": "Evacuation from Singer Island"
            },
        ]
    
    def get_centerlines_geojson(self) -> dict[str, Any]:
        """
        Get road centerlines as GeoJSON dict.
        
        Returns:
            dict: GeoJSON representation
        """
        if self._centerlines:
            return self._centerlines.model_dump()
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {"error": "Centerlines not loaded"}
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of road centerline data."""
        return {
            "city": "Riviera Beach",
            "major_roads": len(self.MAJOR_ROADS),
            "major_intersections": len(self.MAJOR_INTERSECTIONS),
            "choke_points": len(self.CHOKE_POINTS),
            "centerlines_loaded": self._centerlines is not None,
            "feature_count": len(self._centerlines.features) if self._centerlines else 0,
            "road_classes": {
                rc.value: len(self.get_roads_by_class(rc))
                for rc in RoadClass
            },
            "total_road_miles": sum(r.length_miles or 0 for r in self.MAJOR_ROADS)
        }
