"""
Interior Mapping Service.

Manages interior maps for high-risk buildings including schools, malls,
and critical infrastructure.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field


class POIType(str, Enum):
    """Types of points of interest."""
    ENTRANCE = "entrance"
    EXIT = "exit"
    EMERGENCY_EXIT = "emergency_exit"
    STAIRWELL = "stairwell"
    ELEVATOR = "elevator"
    RESTROOM = "restroom"
    SECURITY_OFFICE = "security_office"
    FIRST_AID = "first_aid"
    FIRE_EXTINGUISHER = "fire_extinguisher"
    AED = "aed"
    PANIC_BUTTON = "panic_button"
    CAMERA = "camera"
    ALARM_PANEL = "alarm_panel"
    UTILITY_ROOM = "utility_room"
    SERVER_ROOM = "server_room"
    SAFE_ROOM = "safe_room"
    HAZMAT_STORAGE = "hazmat_storage"
    ASSEMBLY_POINT = "assembly_point"


class AccessType(str, Enum):
    """Types of access points."""
    DOOR = "door"
    WINDOW = "window"
    GATE = "gate"
    LOADING_DOCK = "loading_dock"
    ROOF_ACCESS = "roof_access"
    BASEMENT_ACCESS = "basement_access"
    TUNNEL = "tunnel"
    SKYLIGHT = "skylight"


class AccessStatus(str, Enum):
    """Access point status."""
    OPEN = "open"
    CLOSED = "closed"
    LOCKED = "locked"
    SECURED = "secured"
    ALARMED = "alarmed"
    BLOCKED = "blocked"


class PointOfInterest(BaseModel):
    """Point of interest within a building."""
    poi_id: str
    building_id: str
    floor_number: int
    poi_type: POIType
    name: str
    description: str = ""
    latitude: float
    longitude: float
    x_offset_m: float = 0.0
    y_offset_m: float = 0.0
    is_accessible: bool = True
    requires_key: bool = False
    has_camera: bool = False
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AccessPoint(BaseModel):
    """Access point for a building."""
    access_id: str
    building_id: str
    floor_number: int
    access_type: AccessType
    status: AccessStatus = AccessStatus.CLOSED
    name: str
    latitude: float
    longitude: float
    x_offset_m: float = 0.0
    y_offset_m: float = 0.0
    width_m: float = 1.0
    height_m: float = 2.0
    is_primary: bool = False
    is_emergency: bool = False
    is_ada_compliant: bool = False
    has_keycard: bool = False
    has_camera: bool = False
    connects_to: Optional[str] = None
    last_status_change: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class FloorPlan(BaseModel):
    """Floor plan for a building floor."""
    plan_id: str
    building_id: str
    floor_number: int
    image_url: Optional[str] = None
    svg_url: Optional[str] = None
    geojson_url: Optional[str] = None
    width_m: float = 0.0
    height_m: float = 0.0
    scale: float = 1.0
    rotation_deg: float = 0.0
    origin_lat: float = 0.0
    origin_lon: float = 0.0
    rooms: list[dict[str, Any]] = Field(default_factory=list)
    walls: list[dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class InteriorMap(BaseModel):
    """Complete interior map for a building."""
    map_id: str
    building_id: str
    building_name: str
    floor_count: int
    floor_plans: list[FloorPlan] = Field(default_factory=list)
    points_of_interest: list[PointOfInterest] = Field(default_factory=list)
    access_points: list[AccessPoint] = Field(default_factory=list)
    evacuation_routes: list[dict[str, Any]] = Field(default_factory=list)
    safe_rooms: list[str] = Field(default_factory=list)
    hazard_zones: list[dict[str, Any]] = Field(default_factory=list)
    last_verified: Optional[datetime] = None
    verified_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class MappingConfig(BaseModel):
    """Configuration for interior mapping service."""
    max_maps: int = 10000
    max_pois_per_building: int = 500
    max_access_points_per_building: int = 200


class MappingMetrics(BaseModel):
    """Metrics for interior mapping service."""
    total_maps: int = 0
    total_pois: int = 0
    total_access_points: int = 0
    pois_by_type: dict[str, int] = Field(default_factory=dict)
    access_by_type: dict[str, int] = Field(default_factory=dict)


class InteriorMappingService:
    """
    Interior Mapping Service.
    
    Manages interior maps for high-risk buildings.
    """
    
    def __init__(self, config: Optional[MappingConfig] = None):
        self.config = config or MappingConfig()
        self._maps: dict[str, InteriorMap] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = MappingMetrics()
    
    async def start(self) -> None:
        """Start the interior mapping service."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the interior mapping service."""
        self._running = False
    
    def create_map(
        self,
        building_id: str,
        building_name: str,
        floor_count: int,
        metadata: Optional[dict[str, Any]] = None,
    ) -> InteriorMap:
        """Create an interior map for a building."""
        map_id = f"map-{uuid.uuid4().hex[:12]}"
        
        interior_map = InteriorMap(
            map_id=map_id,
            building_id=building_id,
            building_name=building_name,
            floor_count=floor_count,
            metadata=metadata or {},
        )
        
        self._maps[building_id] = interior_map
        self._update_metrics()
        
        return interior_map
    
    def delete_map(self, building_id: str) -> bool:
        """Delete an interior map."""
        if building_id not in self._maps:
            return False
        
        del self._maps[building_id]
        self._update_metrics()
        return True
    
    def get_map(self, building_id: str) -> Optional[InteriorMap]:
        """Get interior map for a building."""
        return self._maps.get(building_id)
    
    def get_all_maps(self) -> list[InteriorMap]:
        """Get all interior maps."""
        return list(self._maps.values())
    
    def add_floor_plan(
        self,
        building_id: str,
        floor_number: int,
        image_url: Optional[str] = None,
        svg_url: Optional[str] = None,
        width_m: float = 0.0,
        height_m: float = 0.0,
        origin_lat: float = 0.0,
        origin_lon: float = 0.0,
    ) -> Optional[FloorPlan]:
        """Add a floor plan to a building map."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return None
        
        floor_plan = FloorPlan(
            plan_id=f"plan-{uuid.uuid4().hex[:8]}",
            building_id=building_id,
            floor_number=floor_number,
            image_url=image_url,
            svg_url=svg_url,
            width_m=width_m,
            height_m=height_m,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
        )
        
        interior_map.floor_plans.append(floor_plan)
        interior_map.updated_at = datetime.now(timezone.utc)
        
        return floor_plan
    
    def add_poi(
        self,
        building_id: str,
        floor_number: int,
        poi_type: POIType,
        name: str,
        latitude: float,
        longitude: float,
        description: str = "",
        x_offset_m: float = 0.0,
        y_offset_m: float = 0.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[PointOfInterest]:
        """Add a point of interest to a building map."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return None
        
        if len(interior_map.points_of_interest) >= self.config.max_pois_per_building:
            return None
        
        poi = PointOfInterest(
            poi_id=f"poi-{uuid.uuid4().hex[:8]}",
            building_id=building_id,
            floor_number=floor_number,
            poi_type=poi_type,
            name=name,
            description=description,
            latitude=latitude,
            longitude=longitude,
            x_offset_m=x_offset_m,
            y_offset_m=y_offset_m,
            metadata=metadata or {},
        )
        
        interior_map.points_of_interest.append(poi)
        interior_map.updated_at = datetime.now(timezone.utc)
        
        self._update_metrics()
        return poi
    
    def remove_poi(self, building_id: str, poi_id: str) -> bool:
        """Remove a point of interest."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return False
        
        for i, poi in enumerate(interior_map.points_of_interest):
            if poi.poi_id == poi_id:
                interior_map.points_of_interest.pop(i)
                interior_map.updated_at = datetime.now(timezone.utc)
                self._update_metrics()
                return True
        
        return False
    
    def get_pois(
        self,
        building_id: str,
        floor_number: Optional[int] = None,
        poi_type: Optional[POIType] = None,
    ) -> list[PointOfInterest]:
        """Get points of interest for a building."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return []
        
        pois = interior_map.points_of_interest
        
        if floor_number is not None:
            pois = [p for p in pois if p.floor_number == floor_number]
        
        if poi_type is not None:
            pois = [p for p in pois if p.poi_type == poi_type]
        
        return pois
    
    def add_access_point(
        self,
        building_id: str,
        floor_number: int,
        access_type: AccessType,
        name: str,
        latitude: float,
        longitude: float,
        is_primary: bool = False,
        is_emergency: bool = False,
        status: AccessStatus = AccessStatus.CLOSED,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[AccessPoint]:
        """Add an access point to a building map."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return None
        
        if len(interior_map.access_points) >= self.config.max_access_points_per_building:
            return None
        
        access = AccessPoint(
            access_id=f"access-{uuid.uuid4().hex[:8]}",
            building_id=building_id,
            floor_number=floor_number,
            access_type=access_type,
            status=status,
            name=name,
            latitude=latitude,
            longitude=longitude,
            is_primary=is_primary,
            is_emergency=is_emergency,
            metadata=metadata or {},
        )
        
        interior_map.access_points.append(access)
        interior_map.updated_at = datetime.now(timezone.utc)
        
        self._update_metrics()
        return access
    
    def remove_access_point(self, building_id: str, access_id: str) -> bool:
        """Remove an access point."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return False
        
        for i, access in enumerate(interior_map.access_points):
            if access.access_id == access_id:
                interior_map.access_points.pop(i)
                interior_map.updated_at = datetime.now(timezone.utc)
                self._update_metrics()
                return True
        
        return False
    
    async def update_access_status(
        self,
        building_id: str,
        access_id: str,
        status: AccessStatus,
    ) -> Optional[AccessPoint]:
        """Update access point status."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return None
        
        for access in interior_map.access_points:
            if access.access_id == access_id:
                access.status = status
                access.last_status_change = datetime.now(timezone.utc)
                await self._notify_callbacks(access, "access_status_change")
                return access
        
        return None
    
    def get_access_points(
        self,
        building_id: str,
        floor_number: Optional[int] = None,
        access_type: Optional[AccessType] = None,
        is_emergency: Optional[bool] = None,
    ) -> list[AccessPoint]:
        """Get access points for a building."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return []
        
        access_points = interior_map.access_points
        
        if floor_number is not None:
            access_points = [a for a in access_points if a.floor_number == floor_number]
        
        if access_type is not None:
            access_points = [a for a in access_points if a.access_type == access_type]
        
        if is_emergency is not None:
            access_points = [a for a in access_points if a.is_emergency == is_emergency]
        
        return access_points
    
    def get_emergency_exits(self, building_id: str) -> list[AccessPoint]:
        """Get all emergency exits for a building."""
        return self.get_access_points(building_id, is_emergency=True)
    
    def add_evacuation_route(
        self,
        building_id: str,
        name: str,
        waypoints: list[dict[str, Any]],
        start_floor: int,
        end_floor: int,
        exit_access_id: str,
    ) -> bool:
        """Add an evacuation route to a building."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return False
        
        route = {
            "route_id": f"route-{uuid.uuid4().hex[:8]}",
            "name": name,
            "waypoints": waypoints,
            "start_floor": start_floor,
            "end_floor": end_floor,
            "exit_access_id": exit_access_id,
        }
        
        interior_map.evacuation_routes.append(route)
        interior_map.updated_at = datetime.now(timezone.utc)
        
        return True
    
    def get_evacuation_routes(
        self,
        building_id: str,
        floor_number: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Get evacuation routes for a building."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return []
        
        routes = interior_map.evacuation_routes
        
        if floor_number is not None:
            routes = [
                r for r in routes
                if r.get("start_floor", 0) <= floor_number <= r.get("end_floor", 0)
            ]
        
        return routes
    
    def add_safe_room(
        self,
        building_id: str,
        room_id: str,
    ) -> bool:
        """Mark a room as a safe room."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return False
        
        if room_id not in interior_map.safe_rooms:
            interior_map.safe_rooms.append(room_id)
            interior_map.updated_at = datetime.now(timezone.utc)
        
        return True
    
    def get_safe_rooms(self, building_id: str) -> list[str]:
        """Get safe rooms for a building."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return []
        
        return interior_map.safe_rooms
    
    def add_hazard_zone(
        self,
        building_id: str,
        name: str,
        floor_number: int,
        hazard_type: str,
        boundary_coords: list[tuple[float, float]],
    ) -> bool:
        """Add a hazard zone to a building."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return False
        
        hazard = {
            "hazard_id": f"hazard-{uuid.uuid4().hex[:8]}",
            "name": name,
            "floor_number": floor_number,
            "hazard_type": hazard_type,
            "boundary_coords": boundary_coords,
        }
        
        interior_map.hazard_zones.append(hazard)
        interior_map.updated_at = datetime.now(timezone.utc)
        
        return True
    
    def get_hazard_zones(
        self,
        building_id: str,
        floor_number: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Get hazard zones for a building."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return []
        
        zones = interior_map.hazard_zones
        
        if floor_number is not None:
            zones = [z for z in zones if z.get("floor_number") == floor_number]
        
        return zones
    
    def verify_map(
        self,
        building_id: str,
        verified_by: str,
    ) -> bool:
        """Mark a map as verified."""
        interior_map = self._maps.get(building_id)
        if not interior_map:
            return False
        
        interior_map.last_verified = datetime.now(timezone.utc)
        interior_map.verified_by = verified_by
        interior_map.updated_at = datetime.now(timezone.utc)
        
        return True
    
    def get_metrics(self) -> MappingMetrics:
        """Get mapping metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get service status."""
        return {
            "running": self._running,
            "total_maps": len(self._maps),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for mapping events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update mapping metrics."""
        poi_counts: dict[str, int] = {}
        access_counts: dict[str, int] = {}
        total_pois = 0
        total_access = 0
        
        for interior_map in self._maps.values():
            for poi in interior_map.points_of_interest:
                poi_counts[poi.poi_type.value] = poi_counts.get(poi.poi_type.value, 0) + 1
                total_pois += 1
            
            for access in interior_map.access_points:
                access_counts[access.access_type.value] = access_counts.get(access.access_type.value, 0) + 1
                total_access += 1
        
        self._metrics.total_maps = len(self._maps)
        self._metrics.total_pois = total_pois
        self._metrics.total_access_points = total_access
        self._metrics.pois_by_type = poi_counts
        self._metrics.access_by_type = access_counts
    
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
