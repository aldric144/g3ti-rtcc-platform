"""
Sensor Registry Service.

Manages sensor registration, status tracking, and readings for
the smart sensor grid integration layer.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class SensorType(str, Enum):
    """Types of sensors in the grid."""
    GUNSHOT = "gunshot"
    ENVIRONMENTAL_GAS = "environmental_gas"
    ENVIRONMENTAL_SMOKE = "environmental_smoke"
    ENVIRONMENTAL_AIR = "environmental_air"
    CROWD_DENSITY = "crowd_density"
    SMART_STREETLIGHT = "smart_streetlight"
    BRIDGE_STRUCTURAL = "bridge_structural"
    TUNNEL_STRUCTURAL = "tunnel_structural"
    PANIC_BEACON = "panic_beacon"
    BLUETOOTH_PRESENCE = "bluetooth_presence"
    WIFI_PRESENCE = "wifi_presence"
    CELL_TOWER = "cell_tower"
    TRAFFIC_FLOW = "traffic_flow"
    WEATHER_STATION = "weather_station"
    FLOOD_SENSOR = "flood_sensor"
    SEISMIC = "seismic"
    RADIATION = "radiation"
    CHEMICAL = "chemical"


class SensorStatus(str, Enum):
    """Sensor operational status."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    CALIBRATING = "calibrating"


class SensorReading(BaseModel):
    """Sensor reading data."""
    reading_id: str
    sensor_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: float = 1.0
    raw_value: Optional[float] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Sensor(BaseModel):
    """Sensor entity model."""
    sensor_id: str
    sensor_type: SensorType
    name: str
    description: str = ""
    status: SensorStatus = SensorStatus.OFFLINE
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    installation_date: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    last_reading: Optional[datetime] = None
    last_reading_value: Optional[float] = None
    reading_unit: str = ""
    reading_interval_seconds: int = 60
    alert_threshold_low: Optional[float] = None
    alert_threshold_high: Optional[float] = None
    manufacturer: str = ""
    model: str = ""
    firmware_version: str = ""
    battery_percent: Optional[float] = None
    signal_strength_dbm: Optional[int] = None
    coverage_radius_m: float = 100.0
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class SensorEvent(BaseModel):
    """Sensor event for audit trail."""
    event_id: str
    timestamp: datetime
    sensor_id: str
    event_type: str
    previous_status: Optional[SensorStatus] = None
    new_status: Optional[SensorStatus] = None
    details: dict[str, Any] = Field(default_factory=dict)


class RegistryConfig(BaseModel):
    """Configuration for sensor registry."""
    max_sensors: int = 10000
    max_readings_per_sensor: int = 1000
    offline_threshold_seconds: int = 300
    max_events_stored: int = 50000


class RegistryMetrics(BaseModel):
    """Metrics for sensor registry."""
    total_sensors: int = 0
    sensors_by_type: dict[str, int] = Field(default_factory=dict)
    sensors_by_status: dict[str, int] = Field(default_factory=dict)
    online_count: int = 0
    offline_count: int = 0
    total_readings: int = 0
    readings_per_minute: float = 0.0


class SensorRegistry:
    """
    Sensor Registry Service.
    
    Manages sensor registration, status tracking, and readings for
    the smart sensor grid integration layer.
    """
    
    def __init__(self, config: Optional[RegistryConfig] = None):
        self.config = config or RegistryConfig()
        self._sensors: dict[str, Sensor] = {}
        self._readings: dict[str, deque[SensorReading]] = {}
        self._events: deque[SensorEvent] = deque(maxlen=self.config.max_events_stored)
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = RegistryMetrics()
    
    def register_sensor(
        self,
        sensor_type: SensorType,
        name: str,
        latitude: float,
        longitude: float,
        description: str = "",
        reading_unit: str = "",
        reading_interval_seconds: int = 60,
        coverage_radius_m: float = 100.0,
        zone_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Sensor:
        """Register a new sensor in the grid."""
        sensor_id = f"sensor-{uuid.uuid4().hex[:12]}"
        
        sensor = Sensor(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            name=name,
            description=description,
            latitude=latitude,
            longitude=longitude,
            reading_unit=reading_unit,
            reading_interval_seconds=reading_interval_seconds,
            coverage_radius_m=coverage_radius_m,
            zone_id=zone_id,
            metadata=metadata or {},
        )
        
        self._sensors[sensor_id] = sensor
        self._readings[sensor_id] = deque(maxlen=self.config.max_readings_per_sensor)
        self._log_event(sensor_id, "registered", details={"name": name, "type": sensor_type.value})
        self._update_metrics()
        
        return sensor
    
    def unregister_sensor(self, sensor_id: str) -> bool:
        """Unregister a sensor from the grid."""
        if sensor_id not in self._sensors:
            return False
        
        del self._sensors[sensor_id]
        if sensor_id in self._readings:
            del self._readings[sensor_id]
        
        self._log_event(sensor_id, "unregistered")
        self._update_metrics()
        
        return True
    
    def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        """Get sensor by ID."""
        return self._sensors.get(sensor_id)
    
    def get_all_sensors(self) -> list[Sensor]:
        """Get all registered sensors."""
        return list(self._sensors.values())
    
    def get_sensors_by_type(self, sensor_type: SensorType) -> list[Sensor]:
        """Get sensors by type."""
        return [s for s in self._sensors.values() if s.sensor_type == sensor_type]
    
    def get_sensors_by_status(self, status: SensorStatus) -> list[Sensor]:
        """Get sensors by status."""
        return [s for s in self._sensors.values() if s.status == status]
    
    def get_sensors_in_zone(self, zone_id: str) -> list[Sensor]:
        """Get sensors in a specific zone."""
        return [s for s in self._sensors.values() if s.zone_id == zone_id]
    
    def get_sensors_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> list[Sensor]:
        """Get sensors within a geographic area."""
        result = []
        for sensor in self._sensors.values():
            distance = self._calculate_distance(
                center_lat, center_lon,
                sensor.latitude, sensor.longitude,
            )
            if distance <= radius_km:
                result.append(sensor)
        return result
    
    def get_online_sensors(self) -> list[Sensor]:
        """Get all online sensors."""
        return [s for s in self._sensors.values() if s.status == SensorStatus.ONLINE]
    
    def update_status(
        self,
        sensor_id: str,
        new_status: SensorStatus,
    ) -> bool:
        """Update sensor status."""
        sensor = self._sensors.get(sensor_id)
        if not sensor:
            return False
        
        previous_status = sensor.status
        sensor.status = new_status
        
        self._log_event(
            sensor_id,
            "status_change",
            previous_status=previous_status,
            new_status=new_status,
        )
        self._update_metrics()
        self._notify_callbacks(sensor, "status_change")
        
        return True
    
    def record_reading(
        self,
        sensor_id: str,
        value: float,
        unit: Optional[str] = None,
        quality: float = 1.0,
        raw_value: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[SensorReading]:
        """Record a sensor reading."""
        sensor = self._sensors.get(sensor_id)
        if not sensor:
            return None
        
        reading = SensorReading(
            reading_id=f"reading-{uuid.uuid4().hex[:12]}",
            sensor_id=sensor_id,
            timestamp=datetime.now(timezone.utc),
            value=value,
            unit=unit or sensor.reading_unit,
            quality=quality,
            raw_value=raw_value,
            metadata=metadata or {},
        )
        
        self._readings[sensor_id].append(reading)
        
        sensor.last_reading = reading.timestamp
        sensor.last_reading_value = value
        if sensor.status == SensorStatus.OFFLINE:
            sensor.status = SensorStatus.ONLINE
        
        self._metrics.total_readings += 1
        
        if sensor.alert_threshold_high and value > sensor.alert_threshold_high:
            self._notify_callbacks(sensor, "threshold_high", reading)
        elif sensor.alert_threshold_low and value < sensor.alert_threshold_low:
            self._notify_callbacks(sensor, "threshold_low", reading)
        
        return reading
    
    def get_latest_reading(self, sensor_id: str) -> Optional[SensorReading]:
        """Get latest reading for a sensor."""
        if sensor_id not in self._readings or not self._readings[sensor_id]:
            return None
        return self._readings[sensor_id][-1]
    
    def get_readings(
        self,
        sensor_id: str,
        limit: int = 100,
    ) -> list[SensorReading]:
        """Get readings for a sensor."""
        if sensor_id not in self._readings:
            return []
        
        readings = list(self._readings[sensor_id])
        readings.reverse()
        return readings[:limit]
    
    def get_recent_events(self, limit: int = 100) -> list[SensorEvent]:
        """Get recent sensor events."""
        events = list(self._events)
        events.reverse()
        return events[:limit]
    
    def get_metrics(self) -> RegistryMetrics:
        """Get registry metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get registry status."""
        return {
            "total_sensors": len(self._sensors),
            "online_count": len(self.get_online_sensors()),
            "offline_count": len(self.get_sensors_by_status(SensorStatus.OFFLINE)),
            "total_readings": self._metrics.total_readings,
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for sensor events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _log_event(
        self,
        sensor_id: str,
        event_type: str,
        previous_status: Optional[SensorStatus] = None,
        new_status: Optional[SensorStatus] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> SensorEvent:
        """Log a sensor event."""
        event = SensorEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc),
            sensor_id=sensor_id,
            event_type=event_type,
            previous_status=previous_status,
            new_status=new_status,
            details=details or {},
        )
        self._events.append(event)
        return event
    
    def _update_metrics(self) -> None:
        """Update registry metrics."""
        self._metrics.total_sensors = len(self._sensors)
        
        type_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        online = 0
        offline = 0
        
        for sensor in self._sensors.values():
            type_counts[sensor.sensor_type.value] = type_counts.get(sensor.sensor_type.value, 0) + 1
            status_counts[sensor.status.value] = status_counts.get(sensor.status.value, 0) + 1
            
            if sensor.status == SensorStatus.ONLINE:
                online += 1
            elif sensor.status == SensorStatus.OFFLINE:
                offline += 1
        
        self._metrics.sensors_by_type = type_counts
        self._metrics.sensors_by_status = status_counts
        self._metrics.online_count = online
        self._metrics.offline_count = offline
    
    def _notify_callbacks(
        self,
        sensor: Sensor,
        event_type: str,
        reading: Optional[SensorReading] = None,
    ) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                callback(sensor, event_type, reading)
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
