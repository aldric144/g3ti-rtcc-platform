"""
Drone Telemetry Ingestor.

Handles real-time telemetry data ingestion from drones including
position, battery, sensors, and video streams.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class TelemetryType(str, Enum):
    """Types of telemetry data."""
    POSITION = "position"
    BATTERY = "battery"
    SENSORS = "sensors"
    VIDEO = "video"
    AUDIO = "audio"
    SYSTEM = "system"
    WEATHER = "weather"
    OBSTACLE = "obstacle"
    TARGET = "target"


class VideoStreamStatus(str, Enum):
    """Video stream status."""
    OFFLINE = "offline"
    CONNECTING = "connecting"
    STREAMING = "streaming"
    BUFFERING = "buffering"
    ERROR = "error"


class TelemetryData(BaseModel):
    """Telemetry data packet."""
    telemetry_id: str
    drone_id: str
    timestamp: datetime
    telemetry_type: TelemetryType
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = None
    heading_deg: Optional[float] = None
    speed_mps: Optional[float] = None
    vertical_speed_mps: Optional[float] = None
    battery_percent: Optional[float] = None
    battery_voltage: Optional[float] = None
    battery_temperature_c: Optional[float] = None
    flight_time_remaining_min: Optional[float] = None
    motor_temps: Optional[list[float]] = None
    gps_satellites: Optional[int] = None
    gps_accuracy_m: Optional[float] = None
    signal_strength_dbm: Optional[int] = None
    wind_speed_mps: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    ambient_temp_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    obstacle_distance_m: Optional[float] = None
    obstacle_direction_deg: Optional[float] = None
    gimbal_pitch_deg: Optional[float] = None
    gimbal_roll_deg: Optional[float] = None
    gimbal_yaw_deg: Optional[float] = None
    zoom_level: Optional[float] = None
    is_recording: bool = False
    storage_used_gb: Optional[float] = None
    storage_total_gb: Optional[float] = None
    error_codes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VideoStream(BaseModel):
    """Video stream information."""
    stream_id: str
    drone_id: str
    status: VideoStreamStatus = VideoStreamStatus.OFFLINE
    stream_url: Optional[str] = None
    webrtc_offer: Optional[str] = None
    resolution: str = "1080p"
    fps: int = 30
    bitrate_kbps: int = 4000
    codec: str = "h264"
    latency_ms: float = 0.0
    started_at: Optional[datetime] = None
    viewers_count: int = 0


class TelemetryConfig(BaseModel):
    """Configuration for telemetry ingestor."""
    max_telemetry_stored: int = 100000
    telemetry_retention_hours: int = 24
    position_update_interval_ms: int = 100
    battery_update_interval_ms: int = 1000
    sensor_update_interval_ms: int = 500
    stale_threshold_seconds: int = 5
    enable_video_streaming: bool = True
    max_concurrent_streams: int = 20


class TelemetryMetrics(BaseModel):
    """Metrics for telemetry ingestor."""
    total_packets_received: int = 0
    packets_per_second: float = 0.0
    active_streams: int = 0
    total_data_bytes: int = 0
    drones_reporting: int = 0
    stale_drones: int = 0
    error_count: int = 0


class DroneTelemetryIngestor:
    """
    Drone Telemetry Ingestor.
    
    Handles real-time telemetry data ingestion from drones including
    position, battery, sensors, and video streams.
    """
    
    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or TelemetryConfig()
        self._telemetry: dict[str, deque[TelemetryData]] = {}
        self._latest_telemetry: dict[str, TelemetryData] = {}
        self._video_streams: dict[str, VideoStream] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = TelemetryMetrics()
        self._last_update: dict[str, datetime] = {}
    
    async def start(self) -> None:
        """Start the telemetry ingestor."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the telemetry ingestor."""
        self._running = False
        for stream in self._video_streams.values():
            stream.status = VideoStreamStatus.OFFLINE
    
    async def ingest_telemetry(self, data: TelemetryData) -> bool:
        """Ingest a telemetry data packet."""
        if not self._running:
            return False
        
        drone_id = data.drone_id
        
        if drone_id not in self._telemetry:
            self._telemetry[drone_id] = deque(maxlen=1000)
        
        self._telemetry[drone_id].append(data)
        self._latest_telemetry[drone_id] = data
        self._last_update[drone_id] = datetime.now(timezone.utc)
        
        self._metrics.total_packets_received += 1
        self._update_metrics()
        
        await self._notify_callbacks(data)
        
        return True
    
    async def ingest_position(
        self,
        drone_id: str,
        latitude: float,
        longitude: float,
        altitude_m: float,
        heading_deg: float = 0.0,
        speed_mps: float = 0.0,
        vertical_speed_mps: float = 0.0,
    ) -> TelemetryData:
        """Ingest position telemetry."""
        data = TelemetryData(
            telemetry_id=f"tel-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            timestamp=datetime.now(timezone.utc),
            telemetry_type=TelemetryType.POSITION,
            latitude=latitude,
            longitude=longitude,
            altitude_m=altitude_m,
            heading_deg=heading_deg,
            speed_mps=speed_mps,
            vertical_speed_mps=vertical_speed_mps,
        )
        await self.ingest_telemetry(data)
        return data
    
    async def ingest_battery(
        self,
        drone_id: str,
        battery_percent: float,
        battery_voltage: float,
        battery_temperature_c: float,
        flight_time_remaining_min: float,
    ) -> TelemetryData:
        """Ingest battery telemetry."""
        data = TelemetryData(
            telemetry_id=f"tel-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            timestamp=datetime.now(timezone.utc),
            telemetry_type=TelemetryType.BATTERY,
            battery_percent=battery_percent,
            battery_voltage=battery_voltage,
            battery_temperature_c=battery_temperature_c,
            flight_time_remaining_min=flight_time_remaining_min,
        )
        await self.ingest_telemetry(data)
        return data
    
    async def ingest_sensors(
        self,
        drone_id: str,
        gps_satellites: int,
        gps_accuracy_m: float,
        signal_strength_dbm: int,
        motor_temps: Optional[list[float]] = None,
        obstacle_distance_m: Optional[float] = None,
        obstacle_direction_deg: Optional[float] = None,
    ) -> TelemetryData:
        """Ingest sensor telemetry."""
        data = TelemetryData(
            telemetry_id=f"tel-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            timestamp=datetime.now(timezone.utc),
            telemetry_type=TelemetryType.SENSORS,
            gps_satellites=gps_satellites,
            gps_accuracy_m=gps_accuracy_m,
            signal_strength_dbm=signal_strength_dbm,
            motor_temps=motor_temps,
            obstacle_distance_m=obstacle_distance_m,
            obstacle_direction_deg=obstacle_direction_deg,
        )
        await self.ingest_telemetry(data)
        return data
    
    async def ingest_weather(
        self,
        drone_id: str,
        wind_speed_mps: float,
        wind_direction_deg: float,
        ambient_temp_c: float,
        humidity_percent: float,
    ) -> TelemetryData:
        """Ingest weather telemetry."""
        data = TelemetryData(
            telemetry_id=f"tel-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            timestamp=datetime.now(timezone.utc),
            telemetry_type=TelemetryType.WEATHER,
            wind_speed_mps=wind_speed_mps,
            wind_direction_deg=wind_direction_deg,
            ambient_temp_c=ambient_temp_c,
            humidity_percent=humidity_percent,
        )
        await self.ingest_telemetry(data)
        return data
    
    def get_latest_telemetry(self, drone_id: str) -> Optional[TelemetryData]:
        """Get latest telemetry for a drone."""
        return self._latest_telemetry.get(drone_id)
    
    def get_telemetry_history(
        self,
        drone_id: str,
        limit: int = 100,
    ) -> list[TelemetryData]:
        """Get telemetry history for a drone."""
        if drone_id not in self._telemetry:
            return []
        
        history = list(self._telemetry[drone_id])
        history.reverse()
        return history[:limit]
    
    def get_all_latest_telemetry(self) -> dict[str, TelemetryData]:
        """Get latest telemetry for all drones."""
        return dict(self._latest_telemetry)
    
    def get_reporting_drones(self) -> list[str]:
        """Get list of drones currently reporting telemetry."""
        now = datetime.now(timezone.utc)
        reporting = []
        
        for drone_id, last_update in self._last_update.items():
            delta = (now - last_update).total_seconds()
            if delta <= self.config.stale_threshold_seconds:
                reporting.append(drone_id)
        
        return reporting
    
    def get_stale_drones(self) -> list[str]:
        """Get list of drones with stale telemetry."""
        now = datetime.now(timezone.utc)
        stale = []
        
        for drone_id, last_update in self._last_update.items():
            delta = (now - last_update).total_seconds()
            if delta > self.config.stale_threshold_seconds:
                stale.append(drone_id)
        
        return stale
    
    async def start_video_stream(
        self,
        drone_id: str,
        resolution: str = "1080p",
        fps: int = 30,
    ) -> VideoStream:
        """Start a video stream from a drone."""
        stream_id = f"stream-{uuid.uuid4().hex[:12]}"
        
        stream = VideoStream(
            stream_id=stream_id,
            drone_id=drone_id,
            status=VideoStreamStatus.CONNECTING,
            resolution=resolution,
            fps=fps,
            started_at=datetime.now(timezone.utc),
        )
        
        self._video_streams[drone_id] = stream
        
        stream.status = VideoStreamStatus.STREAMING
        stream.stream_url = f"rtsp://drones.rtcc.local/{drone_id}/live"
        
        self._metrics.active_streams = len([
            s for s in self._video_streams.values()
            if s.status == VideoStreamStatus.STREAMING
        ])
        
        return stream
    
    async def stop_video_stream(self, drone_id: str) -> bool:
        """Stop a video stream from a drone."""
        if drone_id not in self._video_streams:
            return False
        
        stream = self._video_streams[drone_id]
        stream.status = VideoStreamStatus.OFFLINE
        
        self._metrics.active_streams = len([
            s for s in self._video_streams.values()
            if s.status == VideoStreamStatus.STREAMING
        ])
        
        return True
    
    def get_video_stream(self, drone_id: str) -> Optional[VideoStream]:
        """Get video stream for a drone."""
        return self._video_streams.get(drone_id)
    
    def get_all_video_streams(self) -> list[VideoStream]:
        """Get all video streams."""
        return list(self._video_streams.values())
    
    def get_active_streams(self) -> list[VideoStream]:
        """Get active video streams."""
        return [
            s for s in self._video_streams.values()
            if s.status == VideoStreamStatus.STREAMING
        ]
    
    def get_metrics(self) -> TelemetryMetrics:
        """Get telemetry metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get ingestor status."""
        return {
            "running": self._running,
            "drones_reporting": len(self.get_reporting_drones()),
            "stale_drones": len(self.get_stale_drones()),
            "active_streams": self._metrics.active_streams,
            "total_packets": self._metrics.total_packets_received,
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for telemetry events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update telemetry metrics."""
        self._metrics.drones_reporting = len(self.get_reporting_drones())
        self._metrics.stale_drones = len(self.get_stale_drones())
    
    async def _notify_callbacks(self, data: TelemetryData) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(data)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                self._metrics.error_count += 1
