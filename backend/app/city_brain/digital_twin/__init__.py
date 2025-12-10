"""
Phase 22: Digital Twin Upgrade for Riviera Beach

Enhanced digital twin system with:
- DigitalTwinState: Real-time city state snapshot
- DynamicObjectRenderer: Render police, fire, EMS, drones, boats
- EventOverlayEngine: Display overlays for incidents, outages, weather
- TimeWarpEngine: Historical playback and future simulation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import uuid
import random


class ObjectType(Enum):
    """Types of dynamic objects in the digital twin."""
    POLICE_UNIT = "police_unit"
    FIRE_UNIT = "fire_unit"
    EMS_UNIT = "ems_unit"
    CITY_VEHICLE = "city_vehicle"
    DRONE = "drone"
    ROBOT = "robot"
    BOAT = "boat"
    BUS = "bus"
    SCHOOL_BUS = "school_bus"


class ObjectStatus(Enum):
    """Status of dynamic objects."""
    AVAILABLE = "available"
    BUSY = "busy"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    OUT_OF_SERVICE = "out_of_service"
    RETURNING = "returning"


class OverlayType(Enum):
    """Types of event overlays."""
    POWER_OUTAGE = "power_outage"
    FLOOD_ZONE = "flood_zone"
    ROAD_CLOSURE = "road_closure"
    POLICE_INCIDENT = "police_incident"
    FIRE_INCIDENT = "fire_incident"
    WEATHER_ALERT = "weather_alert"
    EVACUATION_ROUTE = "evacuation_route"
    TRAFFIC_CONGESTION = "traffic_congestion"
    CONSTRUCTION_ZONE = "construction_zone"
    SPECIAL_EVENT = "special_event"


class CongestionLevel(Enum):
    """Traffic congestion levels."""
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    GRIDLOCK = "gridlock"


class TimelineMode(Enum):
    """Timeline modes for TimeWarp engine."""
    LIVE = "live"
    HISTORICAL = "historical"
    SIMULATION = "simulation"


@dataclass
class Location:
    """Geographic location."""
    latitude: float
    longitude: float
    altitude_ft: Optional[float] = None
    heading: Optional[float] = None
    speed_mph: Optional[float] = None


@dataclass
class DynamicObject:
    """A dynamic object in the digital twin."""
    object_id: str
    object_type: ObjectType
    name: str
    status: ObjectStatus
    location: Location
    destination: Optional[Location] = None
    assigned_incident: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrafficSegment:
    """Traffic conditions for a road segment."""
    segment_id: str
    road_name: str
    start_location: Location
    end_location: Location
    congestion_level: CongestionLevel
    current_speed_mph: float
    free_flow_speed_mph: float
    travel_time_minutes: float
    incident_count: int = 0


@dataclass
class EnvironmentalCondition:
    """Environmental conditions at a location."""
    location: Location
    temperature_f: float
    humidity_percent: float
    wind_speed_mph: float
    wind_direction: str
    precipitation: bool
    visibility_miles: float
    air_quality_index: int
    flood_risk: str
    updated_at: datetime


@dataclass
class InfrastructureStatus:
    """Status of infrastructure element."""
    element_id: str
    element_type: str
    name: str
    status: str
    location: Location
    capacity_percent: Optional[float] = None
    alerts: list[str] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CrimeHotspot:
    """Crime hotspot data."""
    hotspot_id: str
    location: Location
    radius_meters: float
    crime_types: list[str]
    incident_count_24h: int
    incident_count_7d: int
    risk_score: float
    trend: str


@dataclass
class PopulationDensity:
    """Population density estimate for an area."""
    area_id: str
    area_name: str
    location: Location
    current_estimate: int
    typical_estimate: int
    deviation_percent: float
    factors: list[str]


@dataclass
class EventOverlay:
    """An overlay to display on the digital twin."""
    overlay_id: str
    overlay_type: OverlayType
    title: str
    description: str
    geometry: dict
    severity: str
    active: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DigitalTwinSnapshot:
    """Complete snapshot of the digital twin state."""
    snapshot_id: str
    timestamp: datetime
    mode: TimelineMode
    dynamic_objects: list[DynamicObject]
    traffic_segments: list[TrafficSegment]
    environmental_conditions: list[EnvironmentalCondition]
    infrastructure_status: list[InfrastructureStatus]
    crime_hotspots: list[CrimeHotspot]
    population_density: list[PopulationDensity]
    active_overlays: list[EventOverlay]
    statistics: dict


class DigitalTwinState:
    """
    Real-time city state snapshot manager.
    
    Maintains the current state of all city systems including:
    - Traffic density grid
    - Environmental conditions
    - Infrastructure status
    - Crime hotspots
    - Population movement estimates
    """
    
    def __init__(self):
        self._current_snapshot: Optional[DigitalTwinSnapshot] = None
        self._traffic_grid: dict[str, TrafficSegment] = {}
        self._environmental_grid: dict[str, EnvironmentalCondition] = {}
        self._infrastructure: dict[str, InfrastructureStatus] = {}
        self._crime_hotspots: dict[str, CrimeHotspot] = {}
        self._population_grid: dict[str, PopulationDensity] = {}
        self._last_update: Optional[datetime] = None
    
    def update_traffic(self, segments: list[TrafficSegment]) -> None:
        """Update traffic conditions."""
        for segment in segments:
            self._traffic_grid[segment.segment_id] = segment
        self._last_update = datetime.utcnow()
    
    def update_environmental(self, conditions: list[EnvironmentalCondition]) -> None:
        """Update environmental conditions."""
        for condition in conditions:
            key = f"{condition.location.latitude:.4f},{condition.location.longitude:.4f}"
            self._environmental_grid[key] = condition
        self._last_update = datetime.utcnow()
    
    def update_infrastructure(self, statuses: list[InfrastructureStatus]) -> None:
        """Update infrastructure status."""
        for status in statuses:
            self._infrastructure[status.element_id] = status
        self._last_update = datetime.utcnow()
    
    def update_crime_hotspots(self, hotspots: list[CrimeHotspot]) -> None:
        """Update crime hotspots."""
        for hotspot in hotspots:
            self._crime_hotspots[hotspot.hotspot_id] = hotspot
        self._last_update = datetime.utcnow()
    
    def update_population(self, densities: list[PopulationDensity]) -> None:
        """Update population density estimates."""
        for density in densities:
            self._population_grid[density.area_id] = density
        self._last_update = datetime.utcnow()
    
    def get_traffic_grid(self) -> list[TrafficSegment]:
        """Get current traffic grid."""
        return list(self._traffic_grid.values())
    
    def get_environmental_grid(self) -> list[EnvironmentalCondition]:
        """Get current environmental conditions."""
        return list(self._environmental_grid.values())
    
    def get_infrastructure_status(self) -> list[InfrastructureStatus]:
        """Get current infrastructure status."""
        return list(self._infrastructure.values())
    
    def get_crime_hotspots(self) -> list[CrimeHotspot]:
        """Get current crime hotspots."""
        return list(self._crime_hotspots.values())
    
    def get_population_grid(self) -> list[PopulationDensity]:
        """Get current population density estimates."""
        return list(self._population_grid.values())
    
    def get_statistics(self) -> dict:
        """Get summary statistics."""
        traffic_segments = list(self._traffic_grid.values())
        avg_congestion = sum(
            1 if s.congestion_level == CongestionLevel.FREE_FLOW else
            2 if s.congestion_level == CongestionLevel.LIGHT else
            3 if s.congestion_level == CongestionLevel.MODERATE else
            4 if s.congestion_level == CongestionLevel.HEAVY else 5
            for s in traffic_segments
        ) / max(len(traffic_segments), 1)
        
        infrastructure = list(self._infrastructure.values())
        healthy_infra = sum(1 for i in infrastructure if i.status == "operational")
        
        return {
            "traffic_segments": len(traffic_segments),
            "average_congestion_level": avg_congestion,
            "environmental_sensors": len(self._environmental_grid),
            "infrastructure_elements": len(infrastructure),
            "healthy_infrastructure_percent": (healthy_infra / max(len(infrastructure), 1)) * 100,
            "crime_hotspots": len(self._crime_hotspots),
            "population_zones": len(self._population_grid),
            "last_update": self._last_update.isoformat() if self._last_update else None,
        }


class DynamicObjectRenderer:
    """
    Renders dynamic objects in the digital twin.
    
    Supports:
    - Police units
    - Fire units
    - EMS units
    - City vehicles
    - Drones
    - Robotics
    - Boats (marine integration)
    """
    
    def __init__(self):
        self._objects: dict[str, DynamicObject] = {}
        self._object_history: dict[str, list[Location]] = {}
        self._max_history_points = 100
    
    def register_object(self, obj: DynamicObject) -> None:
        """Register a new dynamic object."""
        self._objects[obj.object_id] = obj
        self._object_history[obj.object_id] = [obj.location]
    
    def update_object(
        self,
        object_id: str,
        location: Optional[Location] = None,
        status: Optional[ObjectStatus] = None,
        destination: Optional[Location] = None,
        assigned_incident: Optional[str] = None,
    ) -> Optional[DynamicObject]:
        """Update a dynamic object's state."""
        if object_id not in self._objects:
            return None
        
        obj = self._objects[object_id]
        
        if location:
            obj.location = location
            if object_id in self._object_history:
                self._object_history[object_id].append(location)
                if len(self._object_history[object_id]) > self._max_history_points:
                    self._object_history[object_id] = self._object_history[object_id][-self._max_history_points:]
        
        if status:
            obj.status = status
        
        if destination is not None:
            obj.destination = destination
        
        if assigned_incident is not None:
            obj.assigned_incident = assigned_incident
        
        obj.last_update = datetime.utcnow()
        
        return obj
    
    def remove_object(self, object_id: str) -> bool:
        """Remove a dynamic object."""
        if object_id in self._objects:
            del self._objects[object_id]
            if object_id in self._object_history:
                del self._object_history[object_id]
            return True
        return False
    
    def get_object(self, object_id: str) -> Optional[DynamicObject]:
        """Get a specific object."""
        return self._objects.get(object_id)
    
    def get_all_objects(self) -> list[DynamicObject]:
        """Get all dynamic objects."""
        return list(self._objects.values())
    
    def get_objects_by_type(self, object_type: ObjectType) -> list[DynamicObject]:
        """Get objects of a specific type."""
        return [o for o in self._objects.values() if o.object_type == object_type]
    
    def get_objects_by_status(self, status: ObjectStatus) -> list[DynamicObject]:
        """Get objects with a specific status."""
        return [o for o in self._objects.values() if o.status == status]
    
    def get_objects_in_area(
        self,
        center: Location,
        radius_miles: float,
    ) -> list[DynamicObject]:
        """Get objects within a radius of a location."""
        result = []
        for obj in self._objects.values():
            lat_diff = abs(obj.location.latitude - center.latitude)
            lon_diff = abs(obj.location.longitude - center.longitude)
            approx_miles = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 69
            if approx_miles <= radius_miles:
                result.append(obj)
        return result
    
    def get_object_trail(self, object_id: str) -> list[Location]:
        """Get the location history trail for an object."""
        return self._object_history.get(object_id, [])
    
    def get_render_data(self) -> dict:
        """Get data for rendering all objects."""
        objects_by_type = {}
        for obj in self._objects.values():
            type_key = obj.object_type.value
            if type_key not in objects_by_type:
                objects_by_type[type_key] = []
            objects_by_type[type_key].append({
                "id": obj.object_id,
                "name": obj.name,
                "status": obj.status.value,
                "location": {
                    "lat": obj.location.latitude,
                    "lng": obj.location.longitude,
                    "heading": obj.location.heading,
                    "speed": obj.location.speed_mph,
                },
                "destination": {
                    "lat": obj.destination.latitude,
                    "lng": obj.destination.longitude,
                } if obj.destination else None,
                "incident": obj.assigned_incident,
                "last_update": obj.last_update.isoformat(),
            })
        
        return {
            "objects": objects_by_type,
            "total_count": len(self._objects),
            "by_status": {
                status.value: len([o for o in self._objects.values() if o.status == status])
                for status in ObjectStatus
            },
        }


class EventOverlayEngine:
    """
    Manages event overlays for the digital twin.
    
    Displays overlays for:
    - Power outages
    - Floods
    - Road closures
    - Active police incidents
    - Weather alerts
    - Evacuation routes
    """
    
    def __init__(self):
        self._overlays: dict[str, EventOverlay] = {}
        self._overlay_history: list[EventOverlay] = []
        self._max_history = 500
    
    def add_overlay(self, overlay: EventOverlay) -> None:
        """Add a new overlay."""
        self._overlays[overlay.overlay_id] = overlay
    
    def update_overlay(
        self,
        overlay_id: str,
        active: Optional[bool] = None,
        severity: Optional[str] = None,
        end_time: Optional[datetime] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[EventOverlay]:
        """Update an existing overlay."""
        if overlay_id not in self._overlays:
            return None
        
        overlay = self._overlays[overlay_id]
        
        if active is not None:
            overlay.active = active
        if severity:
            overlay.severity = severity
        if end_time:
            overlay.end_time = end_time
        if metadata:
            overlay.metadata.update(metadata)
        
        return overlay
    
    def remove_overlay(self, overlay_id: str) -> bool:
        """Remove an overlay."""
        if overlay_id in self._overlays:
            overlay = self._overlays.pop(overlay_id)
            self._overlay_history.append(overlay)
            if len(self._overlay_history) > self._max_history:
                self._overlay_history = self._overlay_history[-self._max_history:]
            return True
        return False
    
    def get_overlay(self, overlay_id: str) -> Optional[EventOverlay]:
        """Get a specific overlay."""
        return self._overlays.get(overlay_id)
    
    def get_active_overlays(self) -> list[EventOverlay]:
        """Get all active overlays."""
        now = datetime.utcnow()
        return [
            o for o in self._overlays.values()
            if o.active and (o.end_time is None or o.end_time > now)
        ]
    
    def get_overlays_by_type(self, overlay_type: OverlayType) -> list[EventOverlay]:
        """Get overlays of a specific type."""
        return [o for o in self._overlays.values() if o.overlay_type == overlay_type]
    
    def get_overlays_by_severity(self, severity: str) -> list[EventOverlay]:
        """Get overlays with a specific severity."""
        return [o for o in self._overlays.values() if o.severity == severity]
    
    def cleanup_expired(self) -> int:
        """Remove expired overlays."""
        now = datetime.utcnow()
        expired = [
            oid for oid, o in self._overlays.items()
            if o.end_time and o.end_time < now
        ]
        for oid in expired:
            self.remove_overlay(oid)
        return len(expired)
    
    def create_power_outage_overlay(
        self,
        outage_id: str,
        area_name: str,
        affected_customers: int,
        center: Location,
        radius_miles: float,
        estimated_restoration: Optional[datetime] = None,
    ) -> EventOverlay:
        """Create a power outage overlay."""
        overlay = EventOverlay(
            overlay_id=f"outage-{outage_id}",
            overlay_type=OverlayType.POWER_OUTAGE,
            title=f"Power Outage - {area_name}",
            description=f"{affected_customers} customers affected",
            geometry={
                "type": "circle",
                "center": {"lat": center.latitude, "lng": center.longitude},
                "radius_miles": radius_miles,
            },
            severity="high" if affected_customers > 500 else "medium",
            active=True,
            start_time=datetime.utcnow(),
            end_time=estimated_restoration,
            metadata={
                "customers_affected": affected_customers,
                "outage_id": outage_id,
            },
        )
        self.add_overlay(overlay)
        return overlay
    
    def create_flood_zone_overlay(
        self,
        zone_id: str,
        zone_name: str,
        water_level_inches: float,
        polygon: list[dict],
    ) -> EventOverlay:
        """Create a flood zone overlay."""
        severity = "low" if water_level_inches < 3 else "medium" if water_level_inches < 6 else "high"
        
        overlay = EventOverlay(
            overlay_id=f"flood-{zone_id}",
            overlay_type=OverlayType.FLOOD_ZONE,
            title=f"Flooding - {zone_name}",
            description=f"Water level: {water_level_inches:.1f} inches",
            geometry={
                "type": "polygon",
                "coordinates": polygon,
            },
            severity=severity,
            active=True,
            start_time=datetime.utcnow(),
            metadata={
                "water_level_inches": water_level_inches,
                "zone_id": zone_id,
            },
        )
        self.add_overlay(overlay)
        return overlay
    
    def create_road_closure_overlay(
        self,
        closure_id: str,
        road_name: str,
        reason: str,
        start_point: Location,
        end_point: Location,
        detour_available: bool = False,
    ) -> EventOverlay:
        """Create a road closure overlay."""
        overlay = EventOverlay(
            overlay_id=f"closure-{closure_id}",
            overlay_type=OverlayType.ROAD_CLOSURE,
            title=f"Road Closure - {road_name}",
            description=reason,
            geometry={
                "type": "line",
                "start": {"lat": start_point.latitude, "lng": start_point.longitude},
                "end": {"lat": end_point.latitude, "lng": end_point.longitude},
            },
            severity="medium",
            active=True,
            start_time=datetime.utcnow(),
            metadata={
                "road_name": road_name,
                "reason": reason,
                "detour_available": detour_available,
            },
        )
        self.add_overlay(overlay)
        return overlay
    
    def create_incident_overlay(
        self,
        incident_id: str,
        incident_type: str,
        location: Location,
        priority: str,
        description: str,
    ) -> EventOverlay:
        """Create a police/fire incident overlay."""
        overlay_type = OverlayType.FIRE_INCIDENT if "fire" in incident_type.lower() else OverlayType.POLICE_INCIDENT
        
        severity_map = {"1": "critical", "2": "high", "3": "medium", "4": "low"}
        severity = severity_map.get(priority, "medium")
        
        overlay = EventOverlay(
            overlay_id=f"incident-{incident_id}",
            overlay_type=overlay_type,
            title=f"{incident_type} - Priority {priority}",
            description=description,
            geometry={
                "type": "point",
                "location": {"lat": location.latitude, "lng": location.longitude},
            },
            severity=severity,
            active=True,
            start_time=datetime.utcnow(),
            metadata={
                "incident_id": incident_id,
                "incident_type": incident_type,
                "priority": priority,
            },
        )
        self.add_overlay(overlay)
        return overlay
    
    def create_weather_alert_overlay(
        self,
        alert_id: str,
        event_type: str,
        headline: str,
        polygon: list[dict],
        severity: str,
        expires: datetime,
    ) -> EventOverlay:
        """Create a weather alert overlay."""
        overlay = EventOverlay(
            overlay_id=f"weather-{alert_id}",
            overlay_type=OverlayType.WEATHER_ALERT,
            title=event_type,
            description=headline,
            geometry={
                "type": "polygon",
                "coordinates": polygon,
            },
            severity=severity,
            active=True,
            start_time=datetime.utcnow(),
            end_time=expires,
            metadata={
                "alert_id": alert_id,
                "event_type": event_type,
            },
        )
        self.add_overlay(overlay)
        return overlay
    
    def get_render_data(self) -> dict:
        """Get data for rendering all overlays."""
        active = self.get_active_overlays()
        
        by_type = {}
        for overlay in active:
            type_key = overlay.overlay_type.value
            if type_key not in by_type:
                by_type[type_key] = []
            by_type[type_key].append({
                "id": overlay.overlay_id,
                "title": overlay.title,
                "description": overlay.description,
                "geometry": overlay.geometry,
                "severity": overlay.severity,
                "start_time": overlay.start_time.isoformat(),
                "end_time": overlay.end_time.isoformat() if overlay.end_time else None,
                "metadata": overlay.metadata,
            })
        
        return {
            "overlays": by_type,
            "total_active": len(active),
            "by_severity": {
                sev: len([o for o in active if o.severity == sev])
                for sev in ["critical", "high", "medium", "low"]
            },
        }


class TimeWarpEngine:
    """
    Enables historical playback and future simulation.
    
    Features:
    - Historical playback of city state
    - Future simulation up to 72 hours
    - Toggle between timelines
    """
    
    def __init__(self):
        self._mode = TimelineMode.LIVE
        self._current_time: datetime = datetime.utcnow()
        self._playback_speed: float = 1.0
        self._snapshots: dict[str, DigitalTwinSnapshot] = {}
        self._simulation_data: dict = {}
        self._max_snapshots = 1000
    
    def set_mode(self, mode: TimelineMode) -> None:
        """Set the timeline mode."""
        self._mode = mode
        if mode == TimelineMode.LIVE:
            self._current_time = datetime.utcnow()
    
    def get_mode(self) -> TimelineMode:
        """Get current timeline mode."""
        return self._mode
    
    def set_playback_time(self, time: datetime) -> None:
        """Set the playback time for historical mode."""
        if self._mode == TimelineMode.HISTORICAL:
            self._current_time = time
    
    def set_simulation_time(self, hours_ahead: int) -> None:
        """Set the simulation time for future mode."""
        if self._mode == TimelineMode.SIMULATION:
            self._current_time = datetime.utcnow() + timedelta(hours=hours_ahead)
    
    def get_current_time(self) -> datetime:
        """Get the current time in the timeline."""
        if self._mode == TimelineMode.LIVE:
            return datetime.utcnow()
        return self._current_time
    
    def set_playback_speed(self, speed: float) -> None:
        """Set playback speed (1.0 = real-time, 2.0 = 2x, etc.)."""
        self._playback_speed = max(0.1, min(100.0, speed))
    
    def get_playback_speed(self) -> float:
        """Get current playback speed."""
        return self._playback_speed
    
    def store_snapshot(self, snapshot: DigitalTwinSnapshot) -> None:
        """Store a snapshot for historical playback."""
        key = snapshot.timestamp.isoformat()
        self._snapshots[key] = snapshot
        
        if len(self._snapshots) > self._max_snapshots:
            oldest_key = min(self._snapshots.keys())
            del self._snapshots[oldest_key]
    
    def get_snapshot_at_time(self, time: datetime) -> Optional[DigitalTwinSnapshot]:
        """Get the snapshot closest to a specific time."""
        if not self._snapshots:
            return None
        
        target_ts = time.timestamp()
        closest_key = min(
            self._snapshots.keys(),
            key=lambda k: abs(datetime.fromisoformat(k).timestamp() - target_ts)
        )
        return self._snapshots.get(closest_key)
    
    def get_available_time_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """Get the available time range for historical playback."""
        if not self._snapshots:
            return None, None
        
        times = [datetime.fromisoformat(k) for k in self._snapshots.keys()]
        return min(times), max(times)
    
    def simulate_future(self, hours: int) -> dict:
        """Generate simulation data for future hours."""
        if hours > 72:
            hours = 72
        
        base_time = datetime.utcnow()
        simulation = {
            "start_time": base_time.isoformat(),
            "end_time": (base_time + timedelta(hours=hours)).isoformat(),
            "hours": hours,
            "predictions": [],
        }
        
        for h in range(hours):
            hour_time = base_time + timedelta(hours=h)
            
            hour_of_day = hour_time.hour
            is_rush_hour = 7 <= hour_of_day <= 9 or 16 <= hour_of_day <= 18
            is_night = hour_of_day < 6 or hour_of_day > 22
            
            traffic_factor = 1.5 if is_rush_hour else 0.5 if is_night else 1.0
            crime_factor = 1.3 if is_night else 0.8 if 6 <= hour_of_day <= 12 else 1.0
            
            prediction = {
                "time": hour_time.isoformat(),
                "traffic": {
                    "congestion_index": 50 * traffic_factor + random.uniform(-10, 10),
                    "expected_incidents": int(2 * traffic_factor + random.uniform(-1, 2)),
                },
                "crime": {
                    "risk_index": 40 * crime_factor + random.uniform(-10, 10),
                    "expected_calls": int(5 * crime_factor + random.uniform(-2, 3)),
                },
                "weather": {
                    "temperature_f": 82 + random.uniform(-5, 5) + (5 if 10 <= hour_of_day <= 16 else -5),
                    "precipitation_chance": 30 + random.uniform(-20, 40),
                },
                "utilities": {
                    "power_load_percent": 60 + (20 if 12 <= hour_of_day <= 20 else 0) + random.uniform(-5, 5),
                    "water_demand_percent": 70 + (15 if 6 <= hour_of_day <= 9 else 0) + random.uniform(-5, 5),
                },
            }
            simulation["predictions"].append(prediction)
        
        self._simulation_data = simulation
        return simulation
    
    def get_simulation_data(self) -> dict:
        """Get current simulation data."""
        return self._simulation_data
    
    def get_status(self) -> dict:
        """Get TimeWarp engine status."""
        start_time, end_time = self.get_available_time_range()
        
        return {
            "mode": self._mode.value,
            "current_time": self.get_current_time().isoformat(),
            "playback_speed": self._playback_speed,
            "snapshots_stored": len(self._snapshots),
            "historical_range": {
                "start": start_time.isoformat() if start_time else None,
                "end": end_time.isoformat() if end_time else None,
            },
            "simulation_available": bool(self._simulation_data),
        }


class DigitalTwinManager:
    """
    Main manager for the Riviera Beach Digital Twin.
    
    Coordinates all digital twin components:
    - State management
    - Object rendering
    - Event overlays
    - Time manipulation
    """
    
    def __init__(self):
        self.state = DigitalTwinState()
        self.objects = DynamicObjectRenderer()
        self.overlays = EventOverlayEngine()
        self.timewarp = TimeWarpEngine()
        
        self._initialized = False
        self._last_snapshot: Optional[DigitalTwinSnapshot] = None
    
    def initialize(self) -> None:
        """Initialize the digital twin with default data."""
        self._initialize_default_objects()
        self._initialize_default_traffic()
        self._initialized = True
    
    def _initialize_default_objects(self) -> None:
        """Initialize default dynamic objects."""
        for i in range(1, 11):
            self.objects.register_object(DynamicObject(
                object_id=f"police-{i}",
                object_type=ObjectType.POLICE_UNIT,
                name=f"Unit {i}",
                status=ObjectStatus.AVAILABLE if random.random() > 0.3 else ObjectStatus.BUSY,
                location=Location(
                    latitude=26.7753 + random.uniform(-0.02, 0.02),
                    longitude=-80.0583 + random.uniform(-0.03, 0.03),
                    heading=random.uniform(0, 360),
                    speed_mph=random.uniform(0, 35),
                ),
            ))
        
        for i in range(1, 4):
            self.objects.register_object(DynamicObject(
                object_id=f"fire-{i}",
                object_type=ObjectType.FIRE_UNIT,
                name=f"Engine {i}",
                status=ObjectStatus.AVAILABLE,
                location=Location(
                    latitude=26.7756 + (i * 0.005),
                    longitude=-80.0718 + (i * 0.008),
                ),
            ))
        
        for i in range(1, 3):
            self.objects.register_object(DynamicObject(
                object_id=f"ems-{i}",
                object_type=ObjectType.EMS_UNIT,
                name=f"Rescue {i}",
                status=ObjectStatus.AVAILABLE,
                location=Location(
                    latitude=26.7756 + (i * 0.003),
                    longitude=-80.0718 + (i * 0.005),
                ),
            ))
        
        self.objects.register_object(DynamicObject(
            object_id="marine-1",
            object_type=ObjectType.BOAT,
            name="Marine 1",
            status=ObjectStatus.AVAILABLE,
            location=Location(
                latitude=26.7712,
                longitude=-80.0478,
            ),
        ))
    
    def _initialize_default_traffic(self) -> None:
        """Initialize default traffic segments."""
        roads = [
            ("blue-heron-1", "Blue Heron Blvd", 26.7753, -80.0800, 26.7753, -80.0600, 45),
            ("blue-heron-2", "Blue Heron Blvd", 26.7753, -80.0600, 26.7753, -80.0400, 45),
            ("broadway-1", "Broadway", 26.7650, -80.0567, 26.7850, -80.0567, 35),
            ("i95-1", "I-95", 26.7500, -80.0850, 26.8000, -80.0850, 70),
            ("military-1", "Military Trail", 26.7600, -80.0900, 26.7900, -80.0900, 45),
        ]
        
        segments = []
        for road_id, name, start_lat, start_lng, end_lat, end_lng, free_flow in roads:
            current_speed = free_flow * random.uniform(0.6, 1.0)
            
            if current_speed >= free_flow * 0.8:
                congestion = CongestionLevel.FREE_FLOW
            elif current_speed >= free_flow * 0.6:
                congestion = CongestionLevel.LIGHT
            elif current_speed >= free_flow * 0.4:
                congestion = CongestionLevel.MODERATE
            else:
                congestion = CongestionLevel.HEAVY
            
            segments.append(TrafficSegment(
                segment_id=road_id,
                road_name=name,
                start_location=Location(latitude=start_lat, longitude=start_lng),
                end_location=Location(latitude=end_lat, longitude=end_lng),
                congestion_level=congestion,
                current_speed_mph=current_speed,
                free_flow_speed_mph=free_flow,
                travel_time_minutes=5.0 * (free_flow / current_speed),
            ))
        
        self.state.update_traffic(segments)
    
    def create_snapshot(self) -> DigitalTwinSnapshot:
        """Create a snapshot of the current digital twin state."""
        snapshot = DigitalTwinSnapshot(
            snapshot_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            mode=self.timewarp.get_mode(),
            dynamic_objects=self.objects.get_all_objects(),
            traffic_segments=self.state.get_traffic_grid(),
            environmental_conditions=self.state.get_environmental_grid(),
            infrastructure_status=self.state.get_infrastructure_status(),
            crime_hotspots=self.state.get_crime_hotspots(),
            population_density=self.state.get_population_grid(),
            active_overlays=self.overlays.get_active_overlays(),
            statistics=self.state.get_statistics(),
        )
        
        self._last_snapshot = snapshot
        self.timewarp.store_snapshot(snapshot)
        
        return snapshot
    
    def get_render_data(self) -> dict:
        """Get complete render data for the digital twin."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "mode": self.timewarp.get_mode().value,
            "current_time": self.timewarp.get_current_time().isoformat(),
            "objects": self.objects.get_render_data(),
            "overlays": self.overlays.get_render_data(),
            "traffic": [
                {
                    "id": s.segment_id,
                    "road": s.road_name,
                    "congestion": s.congestion_level.value,
                    "speed": s.current_speed_mph,
                    "start": {"lat": s.start_location.latitude, "lng": s.start_location.longitude},
                    "end": {"lat": s.end_location.latitude, "lng": s.end_location.longitude},
                }
                for s in self.state.get_traffic_grid()
            ],
            "statistics": self.state.get_statistics(),
            "timewarp": self.timewarp.get_status(),
        }
    
    def get_status(self) -> dict:
        """Get digital twin status."""
        return {
            "initialized": self._initialized,
            "objects_count": len(self.objects.get_all_objects()),
            "active_overlays": len(self.overlays.get_active_overlays()),
            "traffic_segments": len(self.state.get_traffic_grid()),
            "mode": self.timewarp.get_mode().value,
            "last_snapshot": self._last_snapshot.timestamp.isoformat() if self._last_snapshot else None,
        }


__all__ = [
    "DigitalTwinManager",
    "DigitalTwinState",
    "DynamicObjectRenderer",
    "EventOverlayEngine",
    "TimeWarpEngine",
    "DigitalTwinSnapshot",
    "DynamicObject",
    "EventOverlay",
    "TrafficSegment",
    "EnvironmentalCondition",
    "InfrastructureStatus",
    "CrimeHotspot",
    "PopulationDensity",
    "Location",
    "ObjectType",
    "ObjectStatus",
    "OverlayType",
    "CongestionLevel",
    "TimelineMode",
]
