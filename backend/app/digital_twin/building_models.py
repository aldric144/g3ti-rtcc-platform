"""
Building Models Loader.

Loads and manages 3D building models for the city digital twin.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field


class BuildingType(str, Enum):
    """Types of buildings."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    GOVERNMENT = "government"
    EDUCATIONAL = "educational"
    HEALTHCARE = "healthcare"
    RELIGIOUS = "religious"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    MIXED_USE = "mixed_use"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    HIGH_RISK = "high_risk"


class RiskLevel(str, Enum):
    """Risk levels for buildings."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Room(BaseModel):
    """Room within a floor."""
    room_id: str
    name: str
    room_type: str = ""
    floor_number: int
    area_sq_m: float = 0.0
    capacity: int = 0
    boundary_coords: list[tuple[float, float]] = Field(default_factory=list)
    entry_points: list[str] = Field(default_factory=list)
    has_windows: bool = False
    is_secure: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class Floor(BaseModel):
    """Floor within a building."""
    floor_id: str
    floor_number: int
    name: str = ""
    elevation_m: float = 0.0
    height_m: float = 3.0
    area_sq_m: float = 0.0
    rooms: list[Room] = Field(default_factory=list)
    stairwells: list[str] = Field(default_factory=list)
    elevators: list[str] = Field(default_factory=list)
    emergency_exits: list[str] = Field(default_factory=list)
    floor_plan_url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Building(BaseModel):
    """Building model."""
    building_id: str
    name: str
    address: str = ""
    building_type: BuildingType
    risk_level: RiskLevel = RiskLevel.LOW
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    height_m: float = 10.0
    footprint_coords: list[tuple[float, float]] = Field(default_factory=list)
    floors: list[Floor] = Field(default_factory=list)
    floor_count: int = 1
    basement_count: int = 0
    year_built: Optional[int] = None
    occupancy_capacity: int = 0
    current_occupancy: int = 0
    owner: str = ""
    emergency_contact: str = ""
    has_interior_mapping: bool = False
    has_3d_model: bool = False
    model_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    last_inspection: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BuildingQuery(BaseModel):
    """Query parameters for building search."""
    building_types: Optional[list[BuildingType]] = None
    risk_levels: Optional[list[RiskLevel]] = None
    min_height_m: Optional[float] = None
    max_height_m: Optional[float] = None
    has_interior_mapping: Optional[bool] = None
    tags: Optional[list[str]] = None
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    radius_km: Optional[float] = None


class LoaderConfig(BaseModel):
    """Configuration for building models loader."""
    max_buildings: int = 100000
    cache_size: int = 1000
    default_floor_height_m: float = 3.0


class LoaderMetrics(BaseModel):
    """Metrics for building models loader."""
    total_buildings: int = 0
    buildings_by_type: dict[str, int] = Field(default_factory=dict)
    buildings_by_risk: dict[str, int] = Field(default_factory=dict)
    buildings_with_interior: int = 0
    buildings_with_3d: int = 0
    total_floors: int = 0
    total_rooms: int = 0


class BuildingModelsLoader:
    """
    Building Models Loader.
    
    Loads and manages 3D building models for the city digital twin.
    """
    
    def __init__(self, config: Optional[LoaderConfig] = None):
        self.config = config or LoaderConfig()
        self._buildings: dict[str, Building] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = LoaderMetrics()
    
    async def start(self) -> None:
        """Start the building models loader."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the building models loader."""
        self._running = False
    
    def add_building(
        self,
        name: str,
        building_type: BuildingType,
        latitude: float,
        longitude: float,
        height_m: float = 10.0,
        address: str = "",
        footprint_coords: Optional[list[tuple[float, float]]] = None,
        floor_count: int = 1,
        risk_level: RiskLevel = RiskLevel.LOW,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Building:
        """Add a building to the digital twin."""
        building_id = f"bldg-{uuid.uuid4().hex[:12]}"
        
        floors = []
        for i in range(floor_count):
            floor = Floor(
                floor_id=f"floor-{uuid.uuid4().hex[:8]}",
                floor_number=i + 1,
                name=f"Floor {i + 1}",
                elevation_m=i * self.config.default_floor_height_m,
                height_m=self.config.default_floor_height_m,
            )
            floors.append(floor)
        
        building = Building(
            building_id=building_id,
            name=name,
            address=address,
            building_type=building_type,
            risk_level=risk_level,
            latitude=latitude,
            longitude=longitude,
            height_m=height_m,
            footprint_coords=footprint_coords or [],
            floors=floors,
            floor_count=floor_count,
            metadata=metadata or {},
        )
        
        self._buildings[building_id] = building
        self._update_metrics()
        
        return building
    
    def remove_building(self, building_id: str) -> bool:
        """Remove a building from the digital twin."""
        if building_id not in self._buildings:
            return False
        
        del self._buildings[building_id]
        self._update_metrics()
        return True
    
    def get_building(self, building_id: str) -> Optional[Building]:
        """Get a building by ID."""
        return self._buildings.get(building_id)
    
    def get_all_buildings(self) -> list[Building]:
        """Get all buildings."""
        return list(self._buildings.values())
    
    def get_buildings_by_type(self, building_type: BuildingType) -> list[Building]:
        """Get buildings by type."""
        return [b for b in self._buildings.values() if b.building_type == building_type]
    
    def get_buildings_by_risk(self, risk_level: RiskLevel) -> list[Building]:
        """Get buildings by risk level."""
        return [b for b in self._buildings.values() if b.risk_level == risk_level]
    
    def get_high_risk_buildings(self) -> list[Building]:
        """Get all high-risk buildings."""
        return [
            b for b in self._buildings.values()
            if b.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]
    
    def get_buildings_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[Building]:
        """Get buildings within a geographic area."""
        result = []
        for building in self._buildings.values():
            distance = self._calculate_distance(
                center_lat, center_lon,
                building.latitude, building.longitude,
            )
            if distance <= radius_km:
                result.append(building)
        return result
    
    def search_buildings(self, query: BuildingQuery) -> list[Building]:
        """Search buildings with query parameters."""
        results = list(self._buildings.values())
        
        if query.building_types:
            results = [b for b in results if b.building_type in query.building_types]
        
        if query.risk_levels:
            results = [b for b in results if b.risk_level in query.risk_levels]
        
        if query.min_height_m is not None:
            results = [b for b in results if b.height_m >= query.min_height_m]
        
        if query.max_height_m is not None:
            results = [b for b in results if b.height_m <= query.max_height_m]
        
        if query.has_interior_mapping is not None:
            results = [b for b in results if b.has_interior_mapping == query.has_interior_mapping]
        
        if query.tags:
            results = [b for b in results if any(t in b.tags for t in query.tags)]
        
        if query.center_lat is not None and query.center_lon is not None and query.radius_km is not None:
            filtered = []
            for b in results:
                distance = self._calculate_distance(
                    query.center_lat, query.center_lon,
                    b.latitude, b.longitude,
                )
                if distance <= query.radius_km:
                    filtered.append(b)
            results = filtered
        
        return results
    
    def update_building(
        self,
        building_id: str,
        name: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        current_occupancy: Optional[int] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Building]:
        """Update building properties."""
        building = self._buildings.get(building_id)
        if not building:
            return None
        
        if name is not None:
            building.name = name
        if risk_level is not None:
            building.risk_level = risk_level
        if current_occupancy is not None:
            building.current_occupancy = current_occupancy
        if tags is not None:
            building.tags = tags
        if metadata is not None:
            building.metadata.update(metadata)
        
        building.updated_at = datetime.now(timezone.utc)
        self._update_metrics()
        
        return building
    
    def add_floor(
        self,
        building_id: str,
        floor_number: int,
        name: str = "",
        height_m: Optional[float] = None,
    ) -> Optional[Floor]:
        """Add a floor to a building."""
        building = self._buildings.get(building_id)
        if not building:
            return None
        
        elevation = sum(f.height_m for f in building.floors if f.floor_number < floor_number)
        
        floor = Floor(
            floor_id=f"floor-{uuid.uuid4().hex[:8]}",
            floor_number=floor_number,
            name=name or f"Floor {floor_number}",
            elevation_m=elevation,
            height_m=height_m or self.config.default_floor_height_m,
        )
        
        building.floors.append(floor)
        building.floors.sort(key=lambda f: f.floor_number)
        building.floor_count = len(building.floors)
        building.updated_at = datetime.now(timezone.utc)
        
        self._update_metrics()
        return floor
    
    def add_room(
        self,
        building_id: str,
        floor_number: int,
        name: str,
        room_type: str = "",
        area_sq_m: float = 0.0,
        capacity: int = 0,
    ) -> Optional[Room]:
        """Add a room to a floor."""
        building = self._buildings.get(building_id)
        if not building:
            return None
        
        floor = None
        for f in building.floors:
            if f.floor_number == floor_number:
                floor = f
                break
        
        if not floor:
            return None
        
        room = Room(
            room_id=f"room-{uuid.uuid4().hex[:8]}",
            name=name,
            room_type=room_type,
            floor_number=floor_number,
            area_sq_m=area_sq_m,
            capacity=capacity,
        )
        
        floor.rooms.append(room)
        building.has_interior_mapping = True
        building.updated_at = datetime.now(timezone.utc)
        
        self._update_metrics()
        return room
    
    def set_3d_model(
        self,
        building_id: str,
        model_url: str,
        thumbnail_url: Optional[str] = None,
    ) -> bool:
        """Set the 3D model URL for a building."""
        building = self._buildings.get(building_id)
        if not building:
            return False
        
        building.model_url = model_url
        building.thumbnail_url = thumbnail_url
        building.has_3d_model = True
        building.updated_at = datetime.now(timezone.utc)
        
        self._update_metrics()
        return True
    
    def get_metrics(self) -> LoaderMetrics:
        """Get loader metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get loader status."""
        return {
            "running": self._running,
            "total_buildings": len(self._buildings),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for building events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update loader metrics."""
        type_counts: dict[str, int] = {}
        risk_counts: dict[str, int] = {}
        with_interior = 0
        with_3d = 0
        total_floors = 0
        total_rooms = 0
        
        for building in self._buildings.values():
            type_counts[building.building_type.value] = type_counts.get(building.building_type.value, 0) + 1
            risk_counts[building.risk_level.value] = risk_counts.get(building.risk_level.value, 0) + 1
            
            if building.has_interior_mapping:
                with_interior += 1
            if building.has_3d_model:
                with_3d += 1
            
            total_floors += len(building.floors)
            for floor in building.floors:
                total_rooms += len(floor.rooms)
        
        self._metrics.total_buildings = len(self._buildings)
        self._metrics.buildings_by_type = type_counts
        self._metrics.buildings_by_risk = risk_counts
        self._metrics.buildings_with_interior = with_interior
        self._metrics.buildings_with_3d = with_3d
        self._metrics.total_floors = total_floors
        self._metrics.total_rooms = total_rooms
    
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
