"""
Patrol Route Optimization Engine.

Optimizes patrol routes based on risk terrain, violence clusters, and resource availability.
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field


class PatrolPriority(str, Enum):
    """Priority levels for patrol zones."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class PatrolType(str, Enum):
    """Types of patrol."""
    ROUTINE = "routine"
    DIRECTED = "directed"
    SATURATION = "saturation"
    COMMUNITY = "community"
    TRAFFIC = "traffic"
    SPECIAL_EVENT = "special_event"
    EMERGENCY = "emergency"


class UnitType(str, Enum):
    """Types of patrol units."""
    PATROL_CAR = "patrol_car"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    FOOT = "foot"
    K9 = "k9"
    MOUNTED = "mounted"
    DRONE = "drone"


class PatrolZone(BaseModel):
    """Zone for patrol coverage."""
    zone_id: str
    name: str
    boundary_coords: list[tuple[float, float]] = Field(default_factory=list)
    center_lat: float
    center_lon: float
    area_sq_km: float = 0.0
    priority: PatrolPriority = PatrolPriority.NORMAL
    risk_score: float = 0.0
    incident_count_30d: int = 0
    required_coverage_percent: float = 80.0
    current_coverage_percent: float = 0.0
    assigned_units: list[str] = Field(default_factory=list)
    recommended_units: int = 1
    patrol_frequency_per_hour: float = 1.0
    special_instructions: str = ""
    active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class PatrolUnit(BaseModel):
    """Patrol unit for route assignment."""
    unit_id: str
    call_sign: str
    unit_type: UnitType
    latitude: float
    longitude: float
    available: bool = True
    current_zone_id: Optional[str] = None
    current_route_id: Optional[str] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    capabilities: list[str] = Field(default_factory=list)
    speed_kmh: float = 40.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class Waypoint(BaseModel):
    """Waypoint in a patrol route."""
    waypoint_id: str
    sequence: int
    latitude: float
    longitude: float
    name: str = ""
    dwell_time_minutes: int = 0
    priority: PatrolPriority = PatrolPriority.NORMAL
    instructions: str = ""
    poi_type: Optional[str] = None
    risk_score: float = 0.0


class PatrolRoute(BaseModel):
    """Optimized patrol route."""
    route_id: str
    name: str
    patrol_type: PatrolType = PatrolType.ROUTINE
    zone_id: Optional[str] = None
    assigned_unit_id: Optional[str] = None
    waypoints: list[Waypoint] = Field(default_factory=list)
    total_distance_km: float = 0.0
    estimated_duration_minutes: int = 0
    coverage_score: float = 0.0
    risk_coverage_score: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"
    completed_waypoints: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class OptimizationResult(BaseModel):
    """Result of patrol route optimization."""
    optimization_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    zones_optimized: int = 0
    routes_generated: int = 0
    units_assigned: int = 0
    total_coverage_percent: float = 0.0
    risk_coverage_percent: float = 0.0
    optimization_score: float = 0.0
    recommendations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    routes: list[PatrolRoute] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OptimizerConfig(BaseModel):
    """Configuration for patrol optimizer."""
    max_zones: int = 1000
    max_units: int = 500
    max_waypoints_per_route: int = 50
    default_patrol_duration_hours: float = 2.0
    min_coverage_percent: float = 60.0
    high_risk_weight: float = 2.0
    distance_weight: float = 0.3
    coverage_weight: float = 0.4
    risk_weight: float = 0.3


class OptimizerMetrics(BaseModel):
    """Metrics for patrol optimizer."""
    total_zones: int = 0
    zones_by_priority: dict[str, int] = Field(default_factory=dict)
    total_units: int = 0
    available_units: int = 0
    total_routes: int = 0
    active_routes: int = 0
    avg_coverage_percent: float = 0.0
    avg_risk_coverage: float = 0.0


class PatrolOptimizer:
    """
    Patrol Route Optimization Engine.
    
    Optimizes patrol routes based on risk terrain, violence clusters, and resource availability.
    """
    
    def __init__(self, config: Optional[OptimizerConfig] = None):
        self.config = config or OptimizerConfig()
        self._zones: dict[str, PatrolZone] = {}
        self._units: dict[str, PatrolUnit] = {}
        self._routes: dict[str, PatrolRoute] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = OptimizerMetrics()
    
    async def start(self) -> None:
        """Start the patrol optimizer."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the patrol optimizer."""
        self._running = False
    
    def add_zone(
        self,
        name: str,
        center_lat: float,
        center_lon: float,
        boundary_coords: Optional[list[tuple[float, float]]] = None,
        priority: PatrolPriority = PatrolPriority.NORMAL,
        risk_score: float = 0.0,
        required_coverage_percent: float = 80.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> PatrolZone:
        """Add a patrol zone."""
        zone_id = f"zone-{uuid.uuid4().hex[:12]}"
        
        zone = PatrolZone(
            zone_id=zone_id,
            name=name,
            center_lat=center_lat,
            center_lon=center_lon,
            boundary_coords=boundary_coords or [],
            priority=priority,
            risk_score=risk_score,
            required_coverage_percent=required_coverage_percent,
            metadata=metadata or {},
        )
        
        if boundary_coords:
            zone.area_sq_km = self._calculate_area(boundary_coords)
        
        self._zones[zone_id] = zone
        self._update_metrics()
        
        return zone
    
    def remove_zone(self, zone_id: str) -> bool:
        """Remove a patrol zone."""
        if zone_id not in self._zones:
            return False
        
        del self._zones[zone_id]
        self._update_metrics()
        return True
    
    def get_zone(self, zone_id: str) -> Optional[PatrolZone]:
        """Get a zone by ID."""
        return self._zones.get(zone_id)
    
    def get_all_zones(self) -> list[PatrolZone]:
        """Get all zones."""
        return list(self._zones.values())
    
    def get_zones_by_priority(self, priority: PatrolPriority) -> list[PatrolZone]:
        """Get zones by priority."""
        return [z for z in self._zones.values() if z.priority == priority]
    
    def update_zone_risk(
        self,
        zone_id: str,
        risk_score: float,
        incident_count_30d: Optional[int] = None,
    ) -> Optional[PatrolZone]:
        """Update zone risk score."""
        zone = self._zones.get(zone_id)
        if not zone:
            return None
        
        zone.risk_score = risk_score
        if incident_count_30d is not None:
            zone.incident_count_30d = incident_count_30d
        
        if risk_score >= 0.8:
            zone.priority = PatrolPriority.CRITICAL
        elif risk_score >= 0.6:
            zone.priority = PatrolPriority.HIGH
        elif risk_score >= 0.3:
            zone.priority = PatrolPriority.NORMAL
        else:
            zone.priority = PatrolPriority.LOW
        
        self._update_metrics()
        return zone
    
    def register_unit(
        self,
        call_sign: str,
        unit_type: UnitType,
        latitude: float,
        longitude: float,
        capabilities: Optional[list[str]] = None,
        speed_kmh: float = 40.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> PatrolUnit:
        """Register a patrol unit."""
        unit_id = f"unit-{uuid.uuid4().hex[:12]}"
        
        unit = PatrolUnit(
            unit_id=unit_id,
            call_sign=call_sign,
            unit_type=unit_type,
            latitude=latitude,
            longitude=longitude,
            capabilities=capabilities or [],
            speed_kmh=speed_kmh,
            metadata=metadata or {},
        )
        
        self._units[unit_id] = unit
        self._update_metrics()
        
        return unit
    
    def unregister_unit(self, unit_id: str) -> bool:
        """Unregister a patrol unit."""
        if unit_id not in self._units:
            return False
        
        del self._units[unit_id]
        self._update_metrics()
        return True
    
    def get_unit(self, unit_id: str) -> Optional[PatrolUnit]:
        """Get a unit by ID."""
        return self._units.get(unit_id)
    
    def get_all_units(self) -> list[PatrolUnit]:
        """Get all units."""
        return list(self._units.values())
    
    def get_available_units(self) -> list[PatrolUnit]:
        """Get all available units."""
        return [u for u in self._units.values() if u.available]
    
    def update_unit_position(
        self,
        unit_id: str,
        latitude: float,
        longitude: float,
    ) -> Optional[PatrolUnit]:
        """Update unit position."""
        unit = self._units.get(unit_id)
        if not unit:
            return None
        
        unit.latitude = latitude
        unit.longitude = longitude
        
        return unit
    
    def set_unit_availability(
        self,
        unit_id: str,
        available: bool,
    ) -> bool:
        """Set unit availability."""
        unit = self._units.get(unit_id)
        if not unit:
            return False
        
        unit.available = available
        self._update_metrics()
        return True
    
    async def optimize_routes(
        self,
        zone_ids: Optional[list[str]] = None,
        duration_hours: Optional[float] = None,
    ) -> OptimizationResult:
        """Optimize patrol routes for zones."""
        duration = duration_hours or self.config.default_patrol_duration_hours
        
        zones_to_optimize = []
        if zone_ids:
            zones_to_optimize = [self._zones[zid] for zid in zone_ids if zid in self._zones]
        else:
            zones_to_optimize = [z for z in self._zones.values() if z.active]
        
        zones_to_optimize.sort(key=lambda z: (
            -self._priority_to_score(z.priority),
            -z.risk_score,
        ))
        
        available_units = self.get_available_units()
        
        routes = []
        units_assigned = 0
        total_coverage = 0.0
        risk_coverage = 0.0
        recommendations = []
        warnings = []
        
        for zone in zones_to_optimize:
            if not available_units:
                warnings.append(f"No available units for zone {zone.name}")
                continue
            
            best_unit = self._find_best_unit_for_zone(zone, available_units)
            if not best_unit:
                warnings.append(f"No suitable unit for zone {zone.name}")
                continue
            
            route = await self._generate_route_for_zone(zone, best_unit, duration)
            
            routes.append(route)
            self._routes[route.route_id] = route
            
            best_unit.available = False
            best_unit.current_zone_id = zone.zone_id
            best_unit.current_route_id = route.route_id
            available_units.remove(best_unit)
            
            zone.assigned_units.append(best_unit.unit_id)
            zone.current_coverage_percent = route.coverage_score * 100
            
            units_assigned += 1
            total_coverage += route.coverage_score
            risk_coverage += route.risk_coverage_score
        
        if zones_to_optimize:
            avg_coverage = total_coverage / len(zones_to_optimize)
            avg_risk_coverage = risk_coverage / len(zones_to_optimize)
        else:
            avg_coverage = 0.0
            avg_risk_coverage = 0.0
        
        if avg_coverage < self.config.min_coverage_percent / 100:
            recommendations.append("Consider adding more patrol units to improve coverage")
        
        high_risk_zones = [z for z in zones_to_optimize if z.priority == PatrolPriority.CRITICAL]
        if high_risk_zones and units_assigned < len(high_risk_zones):
            recommendations.append("Critical zones may need additional resources")
        
        result = OptimizationResult(
            optimization_id=f"opt-{uuid.uuid4().hex[:8]}",
            zones_optimized=len(zones_to_optimize),
            routes_generated=len(routes),
            units_assigned=units_assigned,
            total_coverage_percent=avg_coverage * 100,
            risk_coverage_percent=avg_risk_coverage * 100,
            optimization_score=self._calculate_optimization_score(routes),
            recommendations=recommendations,
            warnings=warnings,
            routes=routes,
        )
        
        self._update_metrics()
        await self._notify_callbacks(result, "optimization_complete")
        
        return result
    
    def _find_best_unit_for_zone(
        self,
        zone: PatrolZone,
        available_units: list[PatrolUnit],
    ) -> Optional[PatrolUnit]:
        """Find the best unit for a zone."""
        if not available_units:
            return None
        
        scored_units = []
        for unit in available_units:
            distance = self._calculate_distance(
                unit.latitude, unit.longitude,
                zone.center_lat, zone.center_lon,
            )
            
            distance_score = max(0, 1 - distance / 10)
            
            type_score = 0.5
            if zone.priority == PatrolPriority.CRITICAL:
                if unit.unit_type == UnitType.PATROL_CAR:
                    type_score = 1.0
            elif zone.area_sq_km < 1:
                if unit.unit_type in [UnitType.BICYCLE, UnitType.FOOT]:
                    type_score = 1.0
            
            total_score = distance_score * 0.6 + type_score * 0.4
            scored_units.append((unit, total_score))
        
        scored_units.sort(key=lambda x: -x[1])
        return scored_units[0][0] if scored_units else None
    
    async def _generate_route_for_zone(
        self,
        zone: PatrolZone,
        unit: PatrolUnit,
        duration_hours: float,
    ) -> PatrolRoute:
        """Generate an optimized route for a zone."""
        route_id = f"route-{uuid.uuid4().hex[:12]}"
        
        waypoints = self._generate_waypoints(zone, unit, duration_hours)
        
        total_distance = self._calculate_route_distance(waypoints)
        estimated_duration = int((total_distance / unit.speed_kmh) * 60)
        
        for wp in waypoints:
            estimated_duration += wp.dwell_time_minutes
        
        coverage_score = min(len(waypoints) / 10, 1.0)
        risk_coverage_score = self._calculate_risk_coverage(waypoints, zone)
        
        route = PatrolRoute(
            route_id=route_id,
            name=f"Patrol Route - {zone.name}",
            zone_id=zone.zone_id,
            assigned_unit_id=unit.unit_id,
            waypoints=waypoints,
            total_distance_km=total_distance,
            estimated_duration_minutes=estimated_duration,
            coverage_score=coverage_score,
            risk_coverage_score=risk_coverage_score,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(hours=duration_hours),
            status="active",
        )
        
        return route
    
    def _generate_waypoints(
        self,
        zone: PatrolZone,
        unit: PatrolUnit,
        duration_hours: float,
    ) -> list[Waypoint]:
        """Generate waypoints for a patrol route."""
        waypoints = []
        
        waypoints.append(Waypoint(
            waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
            sequence=0,
            latitude=unit.latitude,
            longitude=unit.longitude,
            name="Start Position",
            priority=PatrolPriority.NORMAL,
        ))
        
        num_waypoints = min(
            int(duration_hours * zone.patrol_frequency_per_hour * 4),
            self.config.max_waypoints_per_route - 2,
        )
        
        if zone.boundary_coords:
            for i in range(num_waypoints):
                idx = i % len(zone.boundary_coords)
                coord = zone.boundary_coords[idx]
                
                waypoints.append(Waypoint(
                    waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
                    sequence=i + 1,
                    latitude=coord[0],
                    longitude=coord[1],
                    name=f"Patrol Point {i + 1}",
                    dwell_time_minutes=2,
                    priority=zone.priority,
                    risk_score=zone.risk_score,
                ))
        else:
            import math
            for i in range(num_waypoints):
                angle = (2 * math.pi * i) / num_waypoints
                radius = 0.005
                
                lat = zone.center_lat + radius * math.cos(angle)
                lon = zone.center_lon + radius * math.sin(angle)
                
                waypoints.append(Waypoint(
                    waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
                    sequence=i + 1,
                    latitude=lat,
                    longitude=lon,
                    name=f"Patrol Point {i + 1}",
                    dwell_time_minutes=2,
                    priority=zone.priority,
                    risk_score=zone.risk_score,
                ))
        
        waypoints.append(Waypoint(
            waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
            sequence=len(waypoints),
            latitude=zone.center_lat,
            longitude=zone.center_lon,
            name="End Position",
            priority=PatrolPriority.NORMAL,
        ))
        
        return waypoints
    
    def _calculate_route_distance(self, waypoints: list[Waypoint]) -> float:
        """Calculate total route distance in kilometers."""
        total = 0.0
        for i in range(len(waypoints) - 1):
            total += self._calculate_distance(
                waypoints[i].latitude, waypoints[i].longitude,
                waypoints[i + 1].latitude, waypoints[i + 1].longitude,
            )
        return total
    
    def _calculate_risk_coverage(
        self,
        waypoints: list[Waypoint],
        zone: PatrolZone,
    ) -> float:
        """Calculate risk coverage score for a route."""
        if not waypoints:
            return 0.0
        
        high_risk_waypoints = len([w for w in waypoints if w.risk_score >= 0.5])
        return min(high_risk_waypoints / max(len(waypoints), 1), 1.0)
    
    def _calculate_optimization_score(self, routes: list[PatrolRoute]) -> float:
        """Calculate overall optimization score."""
        if not routes:
            return 0.0
        
        coverage_avg = sum(r.coverage_score for r in routes) / len(routes)
        risk_avg = sum(r.risk_coverage_score for r in routes) / len(routes)
        
        return (
            coverage_avg * self.config.coverage_weight
            + risk_avg * self.config.risk_weight
            + (1 - sum(r.total_distance_km for r in routes) / (len(routes) * 50)) * self.config.distance_weight
        )
    
    def _priority_to_score(self, priority: PatrolPriority) -> float:
        """Convert priority to numeric score."""
        scores = {
            PatrolPriority.LOW: 0.25,
            PatrolPriority.NORMAL: 0.5,
            PatrolPriority.HIGH: 0.75,
            PatrolPriority.CRITICAL: 1.0,
        }
        return scores.get(priority, 0.5)
    
    def _calculate_area(self, coords: list[tuple[float, float]]) -> float:
        """Calculate area of polygon in square kilometers (approximate)."""
        if len(coords) < 3:
            return 0.0
        
        n = len(coords)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        
        area = abs(area) / 2.0
        
        return area * 111.32 * 111.32
    
    def get_route(self, route_id: str) -> Optional[PatrolRoute]:
        """Get a route by ID."""
        return self._routes.get(route_id)
    
    def get_all_routes(self) -> list[PatrolRoute]:
        """Get all routes."""
        return list(self._routes.values())
    
    def get_active_routes(self) -> list[PatrolRoute]:
        """Get all active routes."""
        return [r for r in self._routes.values() if r.status == "active"]
    
    def complete_waypoint(
        self,
        route_id: str,
        waypoint_id: str,
    ) -> bool:
        """Mark a waypoint as completed."""
        route = self._routes.get(route_id)
        if not route:
            return False
        
        for wp in route.waypoints:
            if wp.waypoint_id == waypoint_id:
                route.completed_waypoints += 1
                route.updated_at = datetime.now(timezone.utc)
                return True
        
        return False
    
    def complete_route(self, route_id: str) -> bool:
        """Mark a route as completed."""
        route = self._routes.get(route_id)
        if not route:
            return False
        
        route.status = "completed"
        route.updated_at = datetime.now(timezone.utc)
        
        if route.assigned_unit_id:
            unit = self._units.get(route.assigned_unit_id)
            if unit:
                unit.available = True
                unit.current_route_id = None
        
        self._update_metrics()
        return True
    
    def get_metrics(self) -> OptimizerMetrics:
        """Get optimizer metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get optimizer status."""
        return {
            "running": self._running,
            "total_zones": len(self._zones),
            "total_units": len(self._units),
            "available_units": len(self.get_available_units()),
            "active_routes": len(self.get_active_routes()),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for optimizer events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update optimizer metrics."""
        priority_counts: dict[str, int] = {}
        for zone in self._zones.values():
            priority_counts[zone.priority.value] = priority_counts.get(zone.priority.value, 0) + 1
        
        available = len([u for u in self._units.values() if u.available])
        active_routes = len([r for r in self._routes.values() if r.status == "active"])
        
        if self._zones:
            avg_coverage = sum(z.current_coverage_percent for z in self._zones.values()) / len(self._zones)
        else:
            avg_coverage = 0.0
        
        if self._routes:
            avg_risk = sum(r.risk_coverage_score for r in self._routes.values()) / len(self._routes) * 100
        else:
            avg_risk = 0.0
        
        self._metrics.total_zones = len(self._zones)
        self._metrics.zones_by_priority = priority_counts
        self._metrics.total_units = len(self._units)
        self._metrics.available_units = available
        self._metrics.total_routes = len(self._routes)
        self._metrics.active_routes = active_routes
        self._metrics.avg_coverage_percent = avg_coverage
        self._metrics.avg_risk_coverage = avg_risk
    
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
