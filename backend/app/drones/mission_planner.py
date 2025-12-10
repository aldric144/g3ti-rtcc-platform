"""
Drone Mission Planner.

Handles mission planning, waypoint generation, and mission execution
for autonomous drone operations.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class MissionType(str, Enum):
    """Types of drone missions."""
    SURVEILLANCE = "surveillance"
    PATROL = "patrol"
    PURSUIT = "pursuit"
    SEARCH = "search"
    PERIMETER = "perimeter"
    ESCORT = "escort"
    OVERWATCH = "overwatch"
    RECONNAISSANCE = "reconnaissance"
    TRAFFIC = "traffic"
    EVENT_COVERAGE = "event_coverage"
    EMERGENCY_RESPONSE = "emergency_response"
    TRAINING = "training"


class MissionStatus(str, Enum):
    """Mission execution status."""
    DRAFT = "draft"
    PLANNED = "planned"
    APPROVED = "approved"
    QUEUED = "queued"
    PREFLIGHT = "preflight"
    ACTIVE = "active"
    PAUSED = "paused"
    RETURNING = "returning"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class MissionPriority(str, Enum):
    """Mission priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class MissionWaypoint(BaseModel):
    """Waypoint in a mission plan."""
    waypoint_id: str
    sequence: int
    latitude: float
    longitude: float
    altitude_m: float
    speed_mps: Optional[float] = None
    hover_time_seconds: float = 0.0
    heading_deg: Optional[float] = None
    gimbal_pitch_deg: Optional[float] = None
    gimbal_yaw_deg: Optional[float] = None
    action: Optional[str] = None
    action_params: dict[str, Any] = Field(default_factory=dict)
    poi_id: Optional[str] = None
    reached: bool = False
    reached_at: Optional[datetime] = None


class MissionObjective(BaseModel):
    """Mission objective."""
    objective_id: str
    description: str
    priority: int = 1
    completed: bool = False
    completed_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MissionArea(BaseModel):
    """Geographic area for mission operations."""
    area_id: str
    name: str
    boundary_coords: list[tuple[float, float]]
    center_lat: float
    center_lon: float
    radius_m: Optional[float] = None
    min_altitude_m: float = 10.0
    max_altitude_m: float = 120.0
    restricted: bool = False


class Mission(BaseModel):
    """Drone mission model."""
    mission_id: str
    mission_type: MissionType
    status: MissionStatus = MissionStatus.DRAFT
    priority: MissionPriority = MissionPriority.NORMAL
    name: str
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    planned_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    assigned_drone_id: Optional[str] = None
    operator_id: Optional[str] = None
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    waypoints: list[MissionWaypoint] = Field(default_factory=list)
    objectives: list[MissionObjective] = Field(default_factory=list)
    area: Optional[MissionArea] = None
    target_id: Optional[str] = None
    target_type: Optional[str] = None
    follow_distance_m: Optional[float] = None
    orbit_radius_m: Optional[float] = None
    search_pattern: Optional[str] = None
    patrol_loops: int = 1
    current_waypoint_index: int = 0
    total_distance_km: float = 0.0
    estimated_duration_min: float = 0.0
    actual_duration_min: float = 0.0
    battery_consumed_percent: float = 0.0
    incident_id: Optional[str] = None
    dispatch_request_id: Optional[str] = None
    recordings: list[str] = Field(default_factory=list)
    photos: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MissionTemplate(BaseModel):
    """Reusable mission template."""
    template_id: str
    name: str
    mission_type: MissionType
    description: str = ""
    default_altitude_m: float = 30.0
    default_speed_mps: float = 10.0
    waypoint_templates: list[dict[str, Any]] = Field(default_factory=list)
    objectives_templates: list[dict[str, Any]] = Field(default_factory=list)
    area_template: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MissionConfig(BaseModel):
    """Configuration for mission planner."""
    max_missions_stored: int = 10000
    max_waypoints_per_mission: int = 100
    default_altitude_m: float = 30.0
    default_speed_mps: float = 10.0
    min_altitude_m: float = 10.0
    max_altitude_m: float = 120.0
    max_mission_duration_min: float = 60.0
    require_approval: bool = False
    auto_return_on_low_battery: bool = True
    low_battery_threshold: float = 20.0


class MissionMetrics(BaseModel):
    """Metrics for mission planner."""
    total_missions: int = 0
    missions_by_type: dict[str, int] = Field(default_factory=dict)
    missions_by_status: dict[str, int] = Field(default_factory=dict)
    active_missions: int = 0
    completed_missions: int = 0
    aborted_missions: int = 0
    total_flight_time_min: float = 0.0
    total_distance_km: float = 0.0


class DroneMissionPlanner:
    """
    Drone Mission Planner.
    
    Handles mission planning, waypoint generation, and mission execution
    for autonomous drone operations.
    """
    
    def __init__(self, config: Optional[MissionConfig] = None):
        self.config = config or MissionConfig()
        self._missions: dict[str, Mission] = {}
        self._mission_history: deque[Mission] = deque(maxlen=self.config.max_missions_stored)
        self._templates: dict[str, MissionTemplate] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = MissionMetrics()
    
    async def start(self) -> None:
        """Start the mission planner."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the mission planner."""
        self._running = False
    
    def create_mission(
        self,
        mission_type: MissionType,
        name: str,
        description: str = "",
        priority: MissionPriority = MissionPriority.NORMAL,
        operator_id: Optional[str] = None,
    ) -> Mission:
        """Create a new mission."""
        mission = Mission(
            mission_id=f"mission-{uuid.uuid4().hex[:12]}",
            mission_type=mission_type,
            name=name,
            description=description,
            priority=priority,
            operator_id=operator_id,
        )
        
        self._missions[mission.mission_id] = mission
        self._metrics.total_missions += 1
        self._update_metrics()
        
        return mission
    
    def create_surveillance_mission(
        self,
        name: str,
        center_lat: float,
        center_lon: float,
        radius_m: float = 100.0,
        altitude_m: float = 30.0,
        duration_min: float = 15.0,
        operator_id: Optional[str] = None,
    ) -> Mission:
        """Create a surveillance mission with orbit pattern."""
        mission = self.create_mission(
            mission_type=MissionType.SURVEILLANCE,
            name=name,
            description=f"Surveillance orbit at radius {radius_m}m",
            operator_id=operator_id,
        )
        
        mission.orbit_radius_m = radius_m
        mission.estimated_duration_min = duration_min
        
        waypoints = self._generate_orbit_waypoints(
            center_lat, center_lon, radius_m, altitude_m,
        )
        mission.waypoints = waypoints
        mission.total_distance_km = self._calculate_total_distance(waypoints)
        
        mission.area = MissionArea(
            area_id=f"area-{uuid.uuid4().hex[:8]}",
            name=f"Surveillance area - {name}",
            boundary_coords=[(center_lat, center_lon)],
            center_lat=center_lat,
            center_lon=center_lon,
            radius_m=radius_m,
        )
        
        return mission
    
    def create_patrol_mission(
        self,
        name: str,
        waypoints: list[tuple[float, float, float]],
        loops: int = 1,
        speed_mps: float = 10.0,
        operator_id: Optional[str] = None,
    ) -> Mission:
        """Create a patrol mission with specified waypoints."""
        mission = self.create_mission(
            mission_type=MissionType.PATROL,
            name=name,
            description=f"Patrol route with {len(waypoints)} waypoints, {loops} loops",
            operator_id=operator_id,
        )
        
        mission.patrol_loops = loops
        
        mission_waypoints = []
        for i, (lat, lon, alt) in enumerate(waypoints):
            wp = MissionWaypoint(
                waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
                sequence=i,
                latitude=lat,
                longitude=lon,
                altitude_m=alt,
                speed_mps=speed_mps,
            )
            mission_waypoints.append(wp)
        
        mission.waypoints = mission_waypoints
        mission.total_distance_km = self._calculate_total_distance(mission_waypoints) * loops
        mission.estimated_duration_min = (mission.total_distance_km / (speed_mps * 0.06)) if speed_mps > 0 else 0
        
        return mission
    
    def create_search_mission(
        self,
        name: str,
        area_coords: list[tuple[float, float]],
        altitude_m: float = 30.0,
        pattern: str = "grid",
        spacing_m: float = 50.0,
        operator_id: Optional[str] = None,
    ) -> Mission:
        """Create a search mission with specified pattern."""
        mission = self.create_mission(
            mission_type=MissionType.SEARCH,
            name=name,
            description=f"Search pattern: {pattern}, spacing: {spacing_m}m",
            operator_id=operator_id,
        )
        
        mission.search_pattern = pattern
        
        center_lat = sum(c[0] for c in area_coords) / len(area_coords)
        center_lon = sum(c[1] for c in area_coords) / len(area_coords)
        
        mission.area = MissionArea(
            area_id=f"area-{uuid.uuid4().hex[:8]}",
            name=f"Search area - {name}",
            boundary_coords=area_coords,
            center_lat=center_lat,
            center_lon=center_lon,
        )
        
        waypoints = self._generate_search_pattern(
            area_coords, altitude_m, pattern, spacing_m,
        )
        mission.waypoints = waypoints
        mission.total_distance_km = self._calculate_total_distance(waypoints)
        
        return mission
    
    def create_pursuit_mission(
        self,
        name: str,
        target_id: str,
        target_type: str,
        initial_lat: float,
        initial_lon: float,
        follow_distance_m: float = 50.0,
        altitude_m: float = 40.0,
        operator_id: Optional[str] = None,
    ) -> Mission:
        """Create a pursuit/follow mission."""
        mission = self.create_mission(
            mission_type=MissionType.PURSUIT,
            name=name,
            description=f"Pursuit of {target_type}: {target_id}",
            priority=MissionPriority.URGENT,
            operator_id=operator_id,
        )
        
        mission.target_id = target_id
        mission.target_type = target_type
        mission.follow_distance_m = follow_distance_m
        
        initial_wp = MissionWaypoint(
            waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
            sequence=0,
            latitude=initial_lat,
            longitude=initial_lon,
            altitude_m=altitude_m,
            action="intercept",
        )
        mission.waypoints = [initial_wp]
        
        return mission
    
    def create_emergency_response_mission(
        self,
        name: str,
        incident_lat: float,
        incident_lon: float,
        incident_id: str,
        altitude_m: float = 30.0,
        orbit_radius_m: float = 50.0,
        operator_id: Optional[str] = None,
    ) -> Mission:
        """Create an emergency response mission."""
        mission = self.create_mission(
            mission_type=MissionType.EMERGENCY_RESPONSE,
            name=name,
            description=f"Emergency response to incident {incident_id}",
            priority=MissionPriority.CRITICAL,
            operator_id=operator_id,
        )
        
        mission.incident_id = incident_id
        mission.orbit_radius_m = orbit_radius_m
        
        approach_wp = MissionWaypoint(
            waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
            sequence=0,
            latitude=incident_lat,
            longitude=incident_lon,
            altitude_m=altitude_m,
            action="approach",
        )
        
        orbit_wps = self._generate_orbit_waypoints(
            incident_lat, incident_lon, orbit_radius_m, altitude_m,
        )
        for i, wp in enumerate(orbit_wps):
            wp.sequence = i + 1
        
        mission.waypoints = [approach_wp] + orbit_wps
        mission.total_distance_km = self._calculate_total_distance(mission.waypoints)
        
        return mission
    
    def add_waypoint(
        self,
        mission_id: str,
        latitude: float,
        longitude: float,
        altitude_m: float,
        speed_mps: Optional[float] = None,
        hover_time_seconds: float = 0.0,
        action: Optional[str] = None,
    ) -> Optional[MissionWaypoint]:
        """Add a waypoint to a mission."""
        mission = self._missions.get(mission_id)
        if not mission:
            return None
        
        if len(mission.waypoints) >= self.config.max_waypoints_per_mission:
            return None
        
        waypoint = MissionWaypoint(
            waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
            sequence=len(mission.waypoints),
            latitude=latitude,
            longitude=longitude,
            altitude_m=altitude_m,
            speed_mps=speed_mps or self.config.default_speed_mps,
            hover_time_seconds=hover_time_seconds,
            action=action,
        )
        
        mission.waypoints.append(waypoint)
        mission.total_distance_km = self._calculate_total_distance(mission.waypoints)
        
        return waypoint
    
    def add_objective(
        self,
        mission_id: str,
        description: str,
        priority: int = 1,
    ) -> Optional[MissionObjective]:
        """Add an objective to a mission."""
        mission = self._missions.get(mission_id)
        if not mission:
            return None
        
        objective = MissionObjective(
            objective_id=f"obj-{uuid.uuid4().hex[:8]}",
            description=description,
            priority=priority,
        )
        
        mission.objectives.append(objective)
        return objective
    
    def assign_drone(
        self,
        mission_id: str,
        drone_id: str,
    ) -> bool:
        """Assign a drone to a mission."""
        mission = self._missions.get(mission_id)
        if not mission:
            return False
        
        mission.assigned_drone_id = drone_id
        return True
    
    async def approve_mission(
        self,
        mission_id: str,
        approver_id: str,
    ) -> bool:
        """Approve a mission for execution."""
        mission = self._missions.get(mission_id)
        if not mission:
            return False
        
        if mission.status not in [MissionStatus.DRAFT, MissionStatus.PLANNED]:
            return False
        
        mission.status = MissionStatus.APPROVED
        mission.approver_id = approver_id
        mission.approved_at = datetime.now(timezone.utc)
        
        await self._notify_callbacks(mission, "approved")
        return True
    
    async def start_mission(
        self,
        mission_id: str,
    ) -> bool:
        """Start mission execution."""
        mission = self._missions.get(mission_id)
        if not mission:
            return False
        
        if not mission.assigned_drone_id:
            return False
        
        if self.config.require_approval and mission.status != MissionStatus.APPROVED:
            return False
        
        mission.status = MissionStatus.ACTIVE
        mission.actual_start = datetime.now(timezone.utc)
        mission.current_waypoint_index = 0
        
        self._update_metrics()
        await self._notify_callbacks(mission, "started")
        return True
    
    async def pause_mission(
        self,
        mission_id: str,
    ) -> bool:
        """Pause mission execution."""
        mission = self._missions.get(mission_id)
        if not mission or mission.status != MissionStatus.ACTIVE:
            return False
        
        mission.status = MissionStatus.PAUSED
        await self._notify_callbacks(mission, "paused")
        return True
    
    async def resume_mission(
        self,
        mission_id: str,
    ) -> bool:
        """Resume paused mission."""
        mission = self._missions.get(mission_id)
        if not mission or mission.status != MissionStatus.PAUSED:
            return False
        
        mission.status = MissionStatus.ACTIVE
        await self._notify_callbacks(mission, "resumed")
        return True
    
    async def complete_mission(
        self,
        mission_id: str,
    ) -> bool:
        """Mark mission as completed."""
        mission = self._missions.get(mission_id)
        if not mission:
            return False
        
        mission.status = MissionStatus.COMPLETED
        mission.actual_end = datetime.now(timezone.utc)
        
        if mission.actual_start:
            mission.actual_duration_min = (
                mission.actual_end - mission.actual_start
            ).total_seconds() / 60.0
        
        self._mission_history.append(mission)
        del self._missions[mission_id]
        
        self._metrics.completed_missions += 1
        self._metrics.total_flight_time_min += mission.actual_duration_min
        self._metrics.total_distance_km += mission.total_distance_km
        self._update_metrics()
        
        await self._notify_callbacks(mission, "completed")
        return True
    
    async def abort_mission(
        self,
        mission_id: str,
        reason: str,
    ) -> bool:
        """Abort mission execution."""
        mission = self._missions.get(mission_id)
        if not mission:
            return False
        
        mission.status = MissionStatus.ABORTED
        mission.actual_end = datetime.now(timezone.utc)
        mission.notes.append(f"Aborted: {reason}")
        
        if mission.actual_start:
            mission.actual_duration_min = (
                mission.actual_end - mission.actual_start
            ).total_seconds() / 60.0
        
        self._mission_history.append(mission)
        del self._missions[mission_id]
        
        self._metrics.aborted_missions += 1
        self._update_metrics()
        
        await self._notify_callbacks(mission, "aborted")
        return True
    
    def update_waypoint_reached(
        self,
        mission_id: str,
        waypoint_index: int,
    ) -> bool:
        """Mark a waypoint as reached."""
        mission = self._missions.get(mission_id)
        if not mission:
            return False
        
        if waypoint_index >= len(mission.waypoints):
            return False
        
        waypoint = mission.waypoints[waypoint_index]
        waypoint.reached = True
        waypoint.reached_at = datetime.now(timezone.utc)
        mission.current_waypoint_index = waypoint_index + 1
        
        return True
    
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Get a mission by ID."""
        if mission_id in self._missions:
            return self._missions[mission_id]
        
        for mission in self._mission_history:
            if mission.mission_id == mission_id:
                return mission
        
        return None
    
    def get_active_missions(self) -> list[Mission]:
        """Get all active missions."""
        return [
            m for m in self._missions.values()
            if m.status == MissionStatus.ACTIVE
        ]
    
    def get_missions_by_status(self, status: MissionStatus) -> list[Mission]:
        """Get missions by status."""
        return [m for m in self._missions.values() if m.status == status]
    
    def get_missions_by_drone(self, drone_id: str) -> list[Mission]:
        """Get missions assigned to a drone."""
        return [m for m in self._missions.values() if m.assigned_drone_id == drone_id]
    
    def get_mission_history(self, limit: int = 100) -> list[Mission]:
        """Get mission history."""
        history = list(self._mission_history)
        history.reverse()
        return history[:limit]
    
    def get_metrics(self) -> MissionMetrics:
        """Get mission metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get planner status."""
        return {
            "running": self._running,
            "total_missions": len(self._missions),
            "active_missions": len(self.get_active_missions()),
            "completed_missions": self._metrics.completed_missions,
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for mission events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _generate_orbit_waypoints(
        self,
        center_lat: float,
        center_lon: float,
        radius_m: float,
        altitude_m: float,
        points: int = 8,
    ) -> list[MissionWaypoint]:
        """Generate waypoints for an orbit pattern."""
        import math
        
        waypoints = []
        radius_deg = radius_m / 111320.0
        
        for i in range(points):
            angle = (2 * math.pi * i) / points
            lat = center_lat + radius_deg * math.cos(angle)
            lon = center_lon + radius_deg * math.sin(angle) / math.cos(math.radians(center_lat))
            
            wp = MissionWaypoint(
                waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
                sequence=i,
                latitude=lat,
                longitude=lon,
                altitude_m=altitude_m,
                heading_deg=math.degrees(angle) + 90,
            )
            waypoints.append(wp)
        
        return waypoints
    
    def _generate_search_pattern(
        self,
        area_coords: list[tuple[float, float]],
        altitude_m: float,
        pattern: str,
        spacing_m: float,
    ) -> list[MissionWaypoint]:
        """Generate waypoints for a search pattern."""
        if not area_coords:
            return []
        
        min_lat = min(c[0] for c in area_coords)
        max_lat = max(c[0] for c in area_coords)
        min_lon = min(c[1] for c in area_coords)
        max_lon = max(c[1] for c in area_coords)
        
        waypoints = []
        spacing_deg = spacing_m / 111320.0
        
        lat = min_lat
        direction = 1
        seq = 0
        
        while lat <= max_lat:
            if direction == 1:
                lon_start, lon_end = min_lon, max_lon
            else:
                lon_start, lon_end = max_lon, min_lon
            
            wp_start = MissionWaypoint(
                waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
                sequence=seq,
                latitude=lat,
                longitude=lon_start,
                altitude_m=altitude_m,
            )
            waypoints.append(wp_start)
            seq += 1
            
            wp_end = MissionWaypoint(
                waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
                sequence=seq,
                latitude=lat,
                longitude=lon_end,
                altitude_m=altitude_m,
            )
            waypoints.append(wp_end)
            seq += 1
            
            lat += spacing_deg
            direction *= -1
        
        return waypoints
    
    def _calculate_total_distance(self, waypoints: list[MissionWaypoint]) -> float:
        """Calculate total distance of waypoints in kilometers."""
        if len(waypoints) < 2:
            return 0.0
        
        import math
        
        total = 0.0
        for i in range(len(waypoints) - 1):
            wp1 = waypoints[i]
            wp2 = waypoints[i + 1]
            
            R = 6371.0
            lat1_rad = math.radians(wp1.latitude)
            lat2_rad = math.radians(wp2.latitude)
            delta_lat = math.radians(wp2.latitude - wp1.latitude)
            delta_lon = math.radians(wp2.longitude - wp1.longitude)
            
            a = (
                math.sin(delta_lat / 2) ** 2
                + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            total += R * c
        
        return total
    
    def _update_metrics(self) -> None:
        """Update mission metrics."""
        type_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        active = 0
        
        for mission in self._missions.values():
            type_counts[mission.mission_type.value] = type_counts.get(mission.mission_type.value, 0) + 1
            status_counts[mission.status.value] = status_counts.get(mission.status.value, 0) + 1
            if mission.status == MissionStatus.ACTIVE:
                active += 1
        
        self._metrics.missions_by_type = type_counts
        self._metrics.missions_by_status = status_counts
        self._metrics.active_missions = active
    
    async def _notify_callbacks(self, mission: Mission, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(mission, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
