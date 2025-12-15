"""
Road Network Service for Riviera Beach Digital Twin.

Manages road network graph data for routing and analysis.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class RoadClass(str, Enum):
    """Road classification."""
    INTERSTATE = "interstate"
    US_HIGHWAY = "us_highway"
    STATE_HIGHWAY = "state_highway"
    MAJOR_ARTERIAL = "major_arterial"
    MINOR_ARTERIAL = "minor_arterial"
    COLLECTOR = "collector"
    LOCAL = "local"
    PRIVATE = "private"


class RoadSegment(BaseModel):
    """Road segment for network graph."""
    segment_id: str
    name: str
    road_class: RoadClass
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    length_miles: float
    lanes: int = 2
    speed_limit_mph: int = 35
    one_way: bool = False
    surface: str = "asphalt"


class Intersection(BaseModel):
    """Road intersection/node."""
    node_id: str
    lat: float
    lon: float
    signal_type: str | None = None
    connected_segments: list[str] = Field(default_factory=list)


class RoadNetworkService:
    """
    Service for road network data for Riviera Beach Digital Twin.
    
    Provides:
    - Road segments with attributes
    - Intersection nodes
    - Network graph for routing
    """
    
    # Road segments (sample)
    ROAD_SEGMENTS = [
        # I-95
        RoadSegment(
            segment_id="i95_n",
            name="I-95 Northbound",
            road_class=RoadClass.INTERSTATE,
            start_lat=26.7400,
            start_lon=-80.0700,
            end_lat=26.8100,
            end_lon=-80.0700,
            length_miles=4.8,
            lanes=3,
            speed_limit_mph=65,
            one_way=True
        ),
        RoadSegment(
            segment_id="i95_s",
            name="I-95 Southbound",
            road_class=RoadClass.INTERSTATE,
            start_lat=26.8100,
            start_lon=-80.0705,
            end_lat=26.7400,
            end_lon=-80.0705,
            length_miles=4.8,
            lanes=3,
            speed_limit_mph=65,
            one_way=True
        ),
        
        # Blue Heron Blvd
        RoadSegment(
            segment_id="blue_heron_w",
            name="Blue Heron Blvd (West)",
            road_class=RoadClass.MAJOR_ARTERIAL,
            start_lat=26.7753,
            start_lon=-80.1000,
            end_lat=26.7753,
            end_lon=-80.0700,
            length_miles=2.0,
            lanes=4,
            speed_limit_mph=45
        ),
        RoadSegment(
            segment_id="blue_heron_e",
            name="Blue Heron Blvd (East)",
            road_class=RoadClass.MAJOR_ARTERIAL,
            start_lat=26.7753,
            start_lon=-80.0700,
            end_lat=26.7753,
            end_lon=-80.0400,
            length_miles=2.0,
            lanes=4,
            speed_limit_mph=40
        ),
        
        # US-1
        RoadSegment(
            segment_id="us1",
            name="US Highway 1",
            road_class=RoadClass.US_HIGHWAY,
            start_lat=26.7400,
            start_lon=-80.0500,
            end_lat=26.8100,
            end_lon=-80.0500,
            length_miles=4.8,
            lanes=4,
            speed_limit_mph=45
        ),
        
        # Broadway
        RoadSegment(
            segment_id="broadway",
            name="Broadway",
            road_class=RoadClass.MINOR_ARTERIAL,
            start_lat=26.7600,
            start_lon=-80.0583,
            end_lat=26.7900,
            end_lon=-80.0583,
            length_miles=2.1,
            lanes=2,
            speed_limit_mph=35
        ),
        
        # Singer Island
        RoadSegment(
            segment_id="ocean_dr",
            name="Ocean Drive",
            road_class=RoadClass.COLLECTOR,
            start_lat=26.7800,
            start_lon=-80.0350,
            end_lat=26.8100,
            end_lon=-80.0350,
            length_miles=2.1,
            lanes=2,
            speed_limit_mph=35
        ),
    ]
    
    # Major intersections
    INTERSECTIONS = [
        Intersection(
            node_id="int_bh_i95",
            lat=26.7753,
            lon=-80.0700,
            signal_type="traffic_signal",
            connected_segments=["blue_heron_w", "blue_heron_e", "i95_n", "i95_s"]
        ),
        Intersection(
            node_id="int_bh_us1",
            lat=26.7753,
            lon=-80.0500,
            signal_type="traffic_signal",
            connected_segments=["blue_heron_e", "us1"]
        ),
        Intersection(
            node_id="int_bh_broadway",
            lat=26.7753,
            lon=-80.0583,
            signal_type="traffic_signal",
            connected_segments=["blue_heron_e", "broadway"]
        ),
    ]
    
    # Network statistics
    STATISTICS = {
        "total_road_miles": 125.5,
        "interstate_miles": 9.6,
        "arterial_miles": 28.5,
        "collector_miles": 35.2,
        "local_miles": 52.2,
        "signalized_intersections": 45,
        "stop_controlled_intersections": 180
    }
    
    def __init__(self) -> None:
        """Initialize the Road Network Service."""
        self._network_loaded = False
    
    async def load_network(self) -> dict[str, Any]:
        """Load road network data."""
        logger.info("loading_road_network", city="Riviera Beach")
        
        features = []
        
        # Add road segments as LineStrings
        for segment in self.ROAD_SEGMENTS:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [segment.start_lon, segment.start_lat],
                        [segment.end_lon, segment.end_lat]
                    ]
                },
                "properties": {
                    "segment_id": segment.segment_id,
                    "name": segment.name,
                    "road_class": segment.road_class.value,
                    "length_miles": segment.length_miles,
                    "lanes": segment.lanes,
                    "speed_limit_mph": segment.speed_limit_mph,
                    "one_way": segment.one_way,
                    "category": "road_segment"
                },
                "id": segment.segment_id
            })
        
        # Add intersections as Points
        for intersection in self.INTERSECTIONS:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [intersection.lon, intersection.lat]
                },
                "properties": {
                    "node_id": intersection.node_id,
                    "signal_type": intersection.signal_type,
                    "connected_segments": intersection.connected_segments,
                    "category": "intersection"
                },
                "id": intersection.node_id
            })
        
        self._network_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "OpenStreetMap / Palm Beach County GIS",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_segments(self) -> list[RoadSegment]:
        """Get road segments."""
        return self.ROAD_SEGMENTS
    
    def get_intersections(self) -> list[Intersection]:
        """Get intersections."""
        return self.INTERSECTIONS
    
    def get_statistics(self) -> dict[str, Any]:
        """Get network statistics."""
        return self.STATISTICS
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of road network data."""
        return {
            "sample_segments": len(self.ROAD_SEGMENTS),
            "sample_intersections": len(self.INTERSECTIONS),
            "total_road_miles": self.STATISTICS["total_road_miles"],
            "signalized_intersections": self.STATISTICS["signalized_intersections"],
            "network_loaded": self._network_loaded
        }
