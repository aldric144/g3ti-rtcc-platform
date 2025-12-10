"""
Drone Registry Service.

Manages drone fleet registration, status tracking, and capabilities.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class DroneStatus(str, Enum):
    """Drone operational status."""
    OFFLINE = "offline"
    STANDBY = "standby"
    PREFLIGHT = "preflight"
    AIRBORNE = "airborne"
    ON_MISSION = "on_mission"
    RETURNING = "returning"
    LANDING = "landing"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


class DroneType(str, Enum):
    """Types of drones in the fleet."""
    SURVEILLANCE = "surveillance"
    TACTICAL = "tactical"
    SEARCH_RESCUE = "search_rescue"
    TRAFFIC = "traffic"
    HAZMAT = "hazmat"
    COMMUNICATIONS = "communications"
    CARGO = "cargo"


class DroneCapability(str, Enum):
    """Drone capabilities."""
    HD_CAMERA = "hd_camera"
    THERMAL_CAMERA = "thermal_camera"
    NIGHT_VISION = "night_vision"
    ZOOM_30X = "zoom_30x"
    ZOOM_60X = "zoom_60x"
    SPOTLIGHT = "spotlight"
    SPEAKER = "speaker"
    MICROPHONE = "microphone"
    LPR_CAMERA = "lpr_camera"
    FACIAL_RECOGNITION = "facial_recognition"
    OBJECT_TRACKING = "object_tracking"
    GPS_RTK = "gps_rtk"
    OBSTACLE_AVOIDANCE = "obstacle_avoidance"
    WEATHER_RESISTANT = "weather_resistant"
    EXTENDED_RANGE = "extended_range"
    CARGO_DROP = "cargo_drop"
    CHEMICAL_SENSOR = "chemical_sensor"
    RADIATION_SENSOR = "radiation_sensor"


class GeoPosition(BaseModel):
    """Geographic position."""
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    heading_deg: float = 0.0
    speed_mps: float = 0.0


class Drone(BaseModel):
    """Drone entity model."""
    drone_id: str
    call_sign: str
    drone_type: DroneType
    status: DroneStatus = DroneStatus.OFFLINE
    capabilities: list[DroneCapability] = Field(default_factory=list)
    position: Optional[GeoPosition] = None
    home_base: Optional[GeoPosition] = None
    battery_percent: float = 100.0
    flight_time_remaining_min: float = 0.0
    max_flight_time_min: float = 30.0
    max_range_km: float = 10.0
    max_speed_mps: float = 20.0
    max_altitude_m: float = 120.0
    current_mission_id: Optional[str] = None
    current_operator_id: Optional[str] = None
    firmware_version: str = "1.0.0"
    last_maintenance: Optional[datetime] = None
    total_flight_hours: float = 0.0
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DroneEvent(BaseModel):
    """Drone event for audit trail."""
    event_id: str
    timestamp: datetime
    drone_id: str
    event_type: str
    previous_status: Optional[DroneStatus] = None
    new_status: Optional[DroneStatus] = None
    details: dict[str, Any] = Field(default_factory=dict)
    operator_id: Optional[str] = None


class RegistryConfig(BaseModel):
    """Configuration for drone registry."""
    max_drones: int = 100
    offline_threshold_seconds: int = 60
    low_battery_threshold: float = 20.0
    critical_battery_threshold: float = 10.0
    max_events_stored: int = 10000


class RegistryMetrics(BaseModel):
    """Metrics for drone registry."""
    total_drones: int = 0
    drones_by_status: dict[str, int] = Field(default_factory=dict)
    drones_by_type: dict[str, int] = Field(default_factory=dict)
    airborne_count: int = 0
    available_count: int = 0
    low_battery_count: int = 0
    total_events: int = 0


class DroneRegistryService:
    """
    Drone Registry Service.
    
    Manages drone fleet registration, status tracking, and capabilities.
    Provides real-time fleet visibility and event logging.
    """
    
    def __init__(self, config: Optional[RegistryConfig] = None):
        self.config = config or RegistryConfig()
        self._drones: dict[str, Drone] = {}
        self._events: deque[DroneEvent] = deque(maxlen=self.config.max_events_stored)
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = RegistryMetrics()
        
    def register_drone(
        self,
        call_sign: str,
        drone_type: DroneType,
        capabilities: list[DroneCapability],
        home_base: Optional[GeoPosition] = None,
        max_flight_time_min: float = 30.0,
        max_range_km: float = 10.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Drone:
        """Register a new drone in the fleet."""
        drone_id = f"drone-{uuid.uuid4().hex[:12]}"
        
        drone = Drone(
            drone_id=drone_id,
            call_sign=call_sign,
            drone_type=drone_type,
            capabilities=capabilities,
            home_base=home_base,
            position=home_base,
            max_flight_time_min=max_flight_time_min,
            max_range_km=max_range_km,
            metadata=metadata or {},
        )
        
        self._drones[drone_id] = drone
        self._log_event(drone_id, "registered", details={"call_sign": call_sign})
        self._update_metrics()
        
        return drone
    
    def unregister_drone(self, drone_id: str) -> bool:
        """Unregister a drone from the fleet."""
        if drone_id not in self._drones:
            return False
        
        drone = self._drones[drone_id]
        if drone.status == DroneStatus.AIRBORNE or drone.status == DroneStatus.ON_MISSION:
            return False
        
        del self._drones[drone_id]
        self._log_event(drone_id, "unregistered")
        self._update_metrics()
        
        return True
    
    def get_drone(self, drone_id: str) -> Optional[Drone]:
        """Get drone by ID."""
        return self._drones.get(drone_id)
    
    def get_drone_by_call_sign(self, call_sign: str) -> Optional[Drone]:
        """Get drone by call sign."""
        for drone in self._drones.values():
            if drone.call_sign == call_sign:
                return drone
        return None
    
    def get_all_drones(self) -> list[Drone]:
        """Get all registered drones."""
        return list(self._drones.values())
    
    def get_drones_by_status(self, status: DroneStatus) -> list[Drone]:
        """Get drones by status."""
        return [d for d in self._drones.values() if d.status == status]
    
    def get_drones_by_type(self, drone_type: DroneType) -> list[Drone]:
        """Get drones by type."""
        return [d for d in self._drones.values() if d.drone_type == drone_type]
    
    def get_available_drones(self) -> list[Drone]:
        """Get drones available for dispatch."""
        available_statuses = [DroneStatus.STANDBY]
        return [
            d for d in self._drones.values()
            if d.status in available_statuses
            and d.battery_percent >= self.config.low_battery_threshold
        ]
    
    def get_airborne_drones(self) -> list[Drone]:
        """Get all airborne drones."""
        airborne_statuses = [
            DroneStatus.AIRBORNE,
            DroneStatus.ON_MISSION,
            DroneStatus.RETURNING,
        ]
        return [d for d in self._drones.values() if d.status in airborne_statuses]
    
    def get_drones_with_capability(self, capability: DroneCapability) -> list[Drone]:
        """Get drones with a specific capability."""
        return [d for d in self._drones.values() if capability in d.capabilities]
    
    def get_drones_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[Drone]:
        """Get drones within a geographic area."""
        result = []
        for drone in self._drones.values():
            if drone.position:
                distance = self._calculate_distance(
                    center_lat, center_lon,
                    drone.position.latitude, drone.position.longitude,
                )
                if distance <= radius_km:
                    result.append(drone)
        return result
    
    def update_status(
        self,
        drone_id: str,
        new_status: DroneStatus,
        operator_id: Optional[str] = None,
    ) -> bool:
        """Update drone status."""
        drone = self._drones.get(drone_id)
        if not drone:
            return False
        
        previous_status = drone.status
        drone.status = new_status
        drone.last_seen = datetime.now(timezone.utc)
        
        self._log_event(
            drone_id,
            "status_change",
            previous_status=previous_status,
            new_status=new_status,
            operator_id=operator_id,
        )
        self._update_metrics()
        self._notify_callbacks(drone, "status_change")
        
        return True
    
    def update_position(
        self,
        drone_id: str,
        position: GeoPosition,
    ) -> bool:
        """Update drone position."""
        drone = self._drones.get(drone_id)
        if not drone:
            return False
        
        drone.position = position
        drone.last_seen = datetime.now(timezone.utc)
        
        return True
    
    def update_battery(
        self,
        drone_id: str,
        battery_percent: float,
        flight_time_remaining_min: float,
    ) -> bool:
        """Update drone battery status."""
        drone = self._drones.get(drone_id)
        if not drone:
            return False
        
        previous_battery = drone.battery_percent
        drone.battery_percent = battery_percent
        drone.flight_time_remaining_min = flight_time_remaining_min
        drone.last_seen = datetime.now(timezone.utc)
        
        if (
            previous_battery >= self.config.critical_battery_threshold
            and battery_percent < self.config.critical_battery_threshold
        ):
            self._log_event(
                drone_id,
                "critical_battery",
                details={"battery_percent": battery_percent},
            )
            self._notify_callbacks(drone, "critical_battery")
        elif (
            previous_battery >= self.config.low_battery_threshold
            and battery_percent < self.config.low_battery_threshold
        ):
            self._log_event(
                drone_id,
                "low_battery",
                details={"battery_percent": battery_percent},
            )
            self._notify_callbacks(drone, "low_battery")
        
        self._update_metrics()
        return True
    
    def assign_mission(
        self,
        drone_id: str,
        mission_id: str,
        operator_id: Optional[str] = None,
    ) -> bool:
        """Assign a mission to a drone."""
        drone = self._drones.get(drone_id)
        if not drone:
            return False
        
        drone.current_mission_id = mission_id
        drone.current_operator_id = operator_id
        
        self._log_event(
            drone_id,
            "mission_assigned",
            details={"mission_id": mission_id},
            operator_id=operator_id,
        )
        
        return True
    
    def clear_mission(self, drone_id: str) -> bool:
        """Clear mission assignment from a drone."""
        drone = self._drones.get(drone_id)
        if not drone:
            return False
        
        mission_id = drone.current_mission_id
        drone.current_mission_id = None
        drone.current_operator_id = None
        
        self._log_event(
            drone_id,
            "mission_cleared",
            details={"mission_id": mission_id},
        )
        
        return True
    
    def get_recent_events(self, limit: int = 100) -> list[DroneEvent]:
        """Get recent drone events."""
        events = list(self._events)
        events.reverse()
        return events[:limit]
    
    def get_events_for_drone(self, drone_id: str, limit: int = 50) -> list[DroneEvent]:
        """Get events for a specific drone."""
        events = [e for e in self._events if e.drone_id == drone_id]
        events.reverse()
        return events[:limit]
    
    def get_metrics(self) -> RegistryMetrics:
        """Get registry metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get registry status."""
        return {
            "total_drones": len(self._drones),
            "airborne_count": len(self.get_airborne_drones()),
            "available_count": len(self.get_available_drones()),
            "events_count": len(self._events),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for drone events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _log_event(
        self,
        drone_id: str,
        event_type: str,
        previous_status: Optional[DroneStatus] = None,
        new_status: Optional[DroneStatus] = None,
        details: Optional[dict[str, Any]] = None,
        operator_id: Optional[str] = None,
    ) -> DroneEvent:
        """Log a drone event."""
        event = DroneEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc),
            drone_id=drone_id,
            event_type=event_type,
            previous_status=previous_status,
            new_status=new_status,
            details=details or {},
            operator_id=operator_id,
        )
        self._events.append(event)
        return event
    
    def _update_metrics(self) -> None:
        """Update registry metrics."""
        self._metrics.total_drones = len(self._drones)
        
        status_counts: dict[str, int] = {}
        type_counts: dict[str, int] = {}
        airborne = 0
        available = 0
        low_battery = 0
        
        for drone in self._drones.values():
            status_counts[drone.status.value] = status_counts.get(drone.status.value, 0) + 1
            type_counts[drone.drone_type.value] = type_counts.get(drone.drone_type.value, 0) + 1
            
            if drone.status in [DroneStatus.AIRBORNE, DroneStatus.ON_MISSION, DroneStatus.RETURNING]:
                airborne += 1
            if drone.status == DroneStatus.STANDBY and drone.battery_percent >= self.config.low_battery_threshold:
                available += 1
            if drone.battery_percent < self.config.low_battery_threshold:
                low_battery += 1
        
        self._metrics.drones_by_status = status_counts
        self._metrics.drones_by_type = type_counts
        self._metrics.airborne_count = airborne
        self._metrics.available_count = available
        self._metrics.low_battery_count = low_battery
        self._metrics.total_events = len(self._events)
    
    def _notify_callbacks(self, drone: Drone, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                callback(drone, event_type)
            except Exception:
                pass
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers (Haversine formula)."""
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
