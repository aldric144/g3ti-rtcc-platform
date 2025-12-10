"""
Road Network Model.

Manages road network data for the city digital twin including roads,
intersections, and traffic conditions.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field


class RoadType(str, Enum):
    """Types of roads."""
    HIGHWAY = "highway"
    ARTERIAL = "arterial"
    COLLECTOR = "collector"
    LOCAL = "local"
    RESIDENTIAL = "residential"
    ALLEY = "alley"
    PRIVATE = "private"
    SERVICE = "service"
    PEDESTRIAN = "pedestrian"
    BICYCLE = "bicycle"


class TrafficCondition(str, Enum):
    """Traffic condition levels."""
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    CONGESTED = "congested"
    BLOCKED = "blocked"


class RoadStatus(str, Enum):
    """Road operational status."""
    OPEN = "open"
    PARTIALLY_CLOSED = "partially_closed"
    CLOSED = "closed"
    CONSTRUCTION = "construction"
    ACCIDENT = "accident"
    EVENT = "event"


class Road(BaseModel):
    """Road segment model."""
    road_id: str
    name: str
    road_type: RoadType
    status: RoadStatus = RoadStatus.OPEN
    traffic_condition: TrafficCondition = TrafficCondition.FREE_FLOW
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    waypoints: list[tuple[float, float]] = Field(default_factory=list)
    length_m: float = 0.0
    lanes: int = 2
    speed_limit_kmh: int = 50
    current_speed_kmh: Optional[float] = None
    is_one_way: bool = False
    direction_deg: Optional[float] = None
    surface_type: str = "asphalt"
    has_sidewalk: bool = True
    has_bike_lane: bool = False
    has_parking: bool = False
    zone_id: Optional[str] = None
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class Intersection(BaseModel):
    """Intersection model."""
    intersection_id: str
    name: str = ""
    latitude: float
    longitude: float
    intersection_type: str = "standard"
    has_traffic_light: bool = False
    has_stop_sign: bool = False
    has_yield_sign: bool = False
    connected_roads: list[str] = Field(default_factory=list)
    is_roundabout: bool = False
    pedestrian_crossing: bool = True
    accident_prone: bool = False
    last_incident: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrafficUpdate(BaseModel):
    """Traffic condition update."""
    update_id: str
    road_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    previous_condition: TrafficCondition
    new_condition: TrafficCondition
    current_speed_kmh: Optional[float] = None
    cause: Optional[str] = None
    estimated_duration_min: Optional[int] = None


class RoadClosure(BaseModel):
    """Road closure information."""
    closure_id: str
    road_id: str
    road_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    reason: str
    severity: str = "partial"
    detour_roads: list[str] = Field(default_factory=list)
    affected_lanes: Optional[int] = None
    contact_info: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class NetworkConfig(BaseModel):
    """Configuration for road network model."""
    max_roads: int = 100000
    max_intersections: int = 50000
    traffic_update_interval_seconds: int = 60


class NetworkMetrics(BaseModel):
    """Metrics for road network model."""
    total_roads: int = 0
    roads_by_type: dict[str, int] = Field(default_factory=dict)
    roads_by_condition: dict[str, int] = Field(default_factory=dict)
    total_intersections: int = 0
    total_length_km: float = 0.0
    active_closures: int = 0
    congested_roads: int = 0


class RoadNetworkModel:
    """
    Road Network Model.
    
    Manages road network data for the city digital twin.
    """
    
    def __init__(self, config: Optional[NetworkConfig] = None):
        self.config = config or NetworkConfig()
        self._roads: dict[str, Road] = {}
        self._intersections: dict[str, Intersection] = {}
        self._closures: dict[str, RoadClosure] = {}
        self._traffic_history: list[TrafficUpdate] = []
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = NetworkMetrics()
    
    async def start(self) -> None:
        """Start the road network model."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the road network model."""
        self._running = False
    
    def add_road(
        self,
        name: str,
        road_type: RoadType,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        waypoints: Optional[list[tuple[float, float]]] = None,
        lanes: int = 2,
        speed_limit_kmh: int = 50,
        is_one_way: bool = False,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Road:
        """Add a road to the network."""
        road_id = f"road-{uuid.uuid4().hex[:12]}"
        
        length_m = self._calculate_road_length(
            start_lat, start_lon, end_lat, end_lon, waypoints or [],
        )
        
        road = Road(
            road_id=road_id,
            name=name,
            road_type=road_type,
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            waypoints=waypoints or [],
            length_m=length_m,
            lanes=lanes,
            speed_limit_kmh=speed_limit_kmh,
            is_one_way=is_one_way,
            metadata=metadata or {},
        )
        
        self._roads[road_id] = road
        self._update_metrics()
        
        return road
    
    def remove_road(self, road_id: str) -> bool:
        """Remove a road from the network."""
        if road_id not in self._roads:
            return False
        
        del self._roads[road_id]
        
        for intersection in self._intersections.values():
            if road_id in intersection.connected_roads:
                intersection.connected_roads.remove(road_id)
        
        self._update_metrics()
        return True
    
    def get_road(self, road_id: str) -> Optional[Road]:
        """Get a road by ID."""
        return self._roads.get(road_id)
    
    def get_all_roads(self) -> list[Road]:
        """Get all roads."""
        return list(self._roads.values())
    
    def get_roads_by_type(self, road_type: RoadType) -> list[Road]:
        """Get roads by type."""
        return [r for r in self._roads.values() if r.road_type == road_type]
    
    def get_roads_by_condition(self, condition: TrafficCondition) -> list[Road]:
        """Get roads by traffic condition."""
        return [r for r in self._roads.values() if r.traffic_condition == condition]
    
    def get_congested_roads(self) -> list[Road]:
        """Get all congested roads."""
        return [
            r for r in self._roads.values()
            if r.traffic_condition in [TrafficCondition.HEAVY, TrafficCondition.CONGESTED, TrafficCondition.BLOCKED]
        ]
    
    def get_roads_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[Road]:
        """Get roads within a geographic area."""
        result = []
        for road in self._roads.values():
            mid_lat = (road.start_lat + road.end_lat) / 2
            mid_lon = (road.start_lon + road.end_lon) / 2
            distance = self._calculate_distance(center_lat, center_lon, mid_lat, mid_lon)
            if distance <= radius_km:
                result.append(road)
        return result
    
    async def update_traffic_condition(
        self,
        road_id: str,
        condition: TrafficCondition,
        current_speed_kmh: Optional[float] = None,
        cause: Optional[str] = None,
    ) -> Optional[Road]:
        """Update traffic condition for a road."""
        road = self._roads.get(road_id)
        if not road:
            return None
        
        previous_condition = road.traffic_condition
        road.traffic_condition = condition
        road.current_speed_kmh = current_speed_kmh
        road.last_updated = datetime.now(timezone.utc)
        
        update = TrafficUpdate(
            update_id=f"update-{uuid.uuid4().hex[:8]}",
            road_id=road_id,
            previous_condition=previous_condition,
            new_condition=condition,
            current_speed_kmh=current_speed_kmh,
            cause=cause,
        )
        self._traffic_history.append(update)
        
        self._update_metrics()
        await self._notify_callbacks(road, "traffic_update")
        
        return road
    
    async def update_road_status(
        self,
        road_id: str,
        status: RoadStatus,
    ) -> Optional[Road]:
        """Update road status."""
        road = self._roads.get(road_id)
        if not road:
            return None
        
        road.status = status
        road.last_updated = datetime.now(timezone.utc)
        
        self._update_metrics()
        await self._notify_callbacks(road, "status_update")
        
        return road
    
    def add_intersection(
        self,
        latitude: float,
        longitude: float,
        name: str = "",
        intersection_type: str = "standard",
        has_traffic_light: bool = False,
        connected_roads: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Intersection:
        """Add an intersection to the network."""
        intersection_id = f"int-{uuid.uuid4().hex[:12]}"
        
        intersection = Intersection(
            intersection_id=intersection_id,
            name=name,
            latitude=latitude,
            longitude=longitude,
            intersection_type=intersection_type,
            has_traffic_light=has_traffic_light,
            connected_roads=connected_roads or [],
            metadata=metadata or {},
        )
        
        self._intersections[intersection_id] = intersection
        self._update_metrics()
        
        return intersection
    
    def remove_intersection(self, intersection_id: str) -> bool:
        """Remove an intersection from the network."""
        if intersection_id not in self._intersections:
            return False
        
        del self._intersections[intersection_id]
        self._update_metrics()
        return True
    
    def get_intersection(self, intersection_id: str) -> Optional[Intersection]:
        """Get an intersection by ID."""
        return self._intersections.get(intersection_id)
    
    def get_all_intersections(self) -> list[Intersection]:
        """Get all intersections."""
        return list(self._intersections.values())
    
    def get_intersections_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[Intersection]:
        """Get intersections within a geographic area."""
        result = []
        for intersection in self._intersections.values():
            distance = self._calculate_distance(
                center_lat, center_lon,
                intersection.latitude, intersection.longitude,
            )
            if distance <= radius_km:
                result.append(intersection)
        return result
    
    def connect_road_to_intersection(
        self,
        road_id: str,
        intersection_id: str,
    ) -> bool:
        """Connect a road to an intersection."""
        if road_id not in self._roads or intersection_id not in self._intersections:
            return False
        
        intersection = self._intersections[intersection_id]
        if road_id not in intersection.connected_roads:
            intersection.connected_roads.append(road_id)
        
        return True
    
    async def add_closure(
        self,
        road_id: str,
        reason: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: str = "partial",
        detour_roads: Optional[list[str]] = None,
    ) -> Optional[RoadClosure]:
        """Add a road closure."""
        road = self._roads.get(road_id)
        if not road:
            return None
        
        closure = RoadClosure(
            closure_id=f"closure-{uuid.uuid4().hex[:8]}",
            road_id=road_id,
            road_name=road.name,
            start_time=start_time or datetime.now(timezone.utc),
            end_time=end_time,
            reason=reason,
            severity=severity,
            detour_roads=detour_roads or [],
        )
        
        self._closures[closure.closure_id] = closure
        
        if severity == "full":
            road.status = RoadStatus.CLOSED
            road.traffic_condition = TrafficCondition.BLOCKED
        else:
            road.status = RoadStatus.PARTIALLY_CLOSED
        
        self._update_metrics()
        await self._notify_callbacks(closure, "closure_added")
        
        return closure
    
    async def remove_closure(self, closure_id: str) -> bool:
        """Remove a road closure."""
        if closure_id not in self._closures:
            return False
        
        closure = self._closures[closure_id]
        road = self._roads.get(closure.road_id)
        
        if road:
            road.status = RoadStatus.OPEN
            road.traffic_condition = TrafficCondition.FREE_FLOW
        
        del self._closures[closure_id]
        self._update_metrics()
        
        return True
    
    def get_active_closures(self) -> list[RoadClosure]:
        """Get all active road closures."""
        now = datetime.now(timezone.utc)
        return [
            c for c in self._closures.values()
            if c.end_time is None or c.end_time > now
        ]
    
    def get_traffic_history(
        self,
        road_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[TrafficUpdate]:
        """Get traffic update history."""
        history = self._traffic_history
        if road_id:
            history = [u for u in history if u.road_id == road_id]
        
        return history[-limit:]
    
    def find_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
    ) -> list[Road]:
        """Find a simple route between two points (basic implementation)."""
        start_road = self._find_nearest_road(start_lat, start_lon)
        end_road = self._find_nearest_road(end_lat, end_lon)
        
        if not start_road or not end_road:
            return []
        
        if start_road.road_id == end_road.road_id:
            return [start_road]
        
        return [start_road, end_road]
    
    def _find_nearest_road(self, lat: float, lon: float) -> Optional[Road]:
        """Find the nearest road to a point."""
        nearest = None
        min_distance = float("inf")
        
        for road in self._roads.values():
            mid_lat = (road.start_lat + road.end_lat) / 2
            mid_lon = (road.start_lon + road.end_lon) / 2
            distance = self._calculate_distance(lat, lon, mid_lat, mid_lon)
            
            if distance < min_distance:
                min_distance = distance
                nearest = road
        
        return nearest
    
    def get_metrics(self) -> NetworkMetrics:
        """Get network metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get network status."""
        return {
            "running": self._running,
            "total_roads": len(self._roads),
            "total_intersections": len(self._intersections),
            "active_closures": len(self.get_active_closures()),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for network events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update network metrics."""
        type_counts: dict[str, int] = {}
        condition_counts: dict[str, int] = {}
        total_length = 0.0
        congested = 0
        
        for road in self._roads.values():
            type_counts[road.road_type.value] = type_counts.get(road.road_type.value, 0) + 1
            condition_counts[road.traffic_condition.value] = condition_counts.get(road.traffic_condition.value, 0) + 1
            total_length += road.length_m
            
            if road.traffic_condition in [TrafficCondition.HEAVY, TrafficCondition.CONGESTED, TrafficCondition.BLOCKED]:
                congested += 1
        
        self._metrics.total_roads = len(self._roads)
        self._metrics.roads_by_type = type_counts
        self._metrics.roads_by_condition = condition_counts
        self._metrics.total_intersections = len(self._intersections)
        self._metrics.total_length_km = total_length / 1000
        self._metrics.active_closures = len(self.get_active_closures())
        self._metrics.congested_roads = congested
    
    def _calculate_road_length(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        waypoints: list[tuple[float, float]],
    ) -> float:
        """Calculate total road length in meters."""
        points = [(start_lat, start_lon)] + waypoints + [(end_lat, end_lon)]
        total = 0.0
        
        for i in range(len(points) - 1):
            total += self._calculate_distance(
                points[i][0], points[i][1],
                points[i + 1][0], points[i + 1][1],
            ) * 1000
        
        return total
    
    async def _notify_callbacks(self, data: Any, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(data, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        import math
        
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
