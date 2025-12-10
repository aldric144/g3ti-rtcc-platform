"""
Overlay Engine.

Manages weather, traffic, and incident overlays for the digital twin.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field


class OverlayType(str, Enum):
    """Types of overlays."""
    WEATHER = "weather"
    TRAFFIC = "traffic"
    INCIDENT = "incident"
    HEATMAP = "heatmap"
    ZONE = "zone"
    PERIMETER = "perimeter"
    SEARCH_AREA = "search_area"
    CROWD_DENSITY = "crowd_density"
    SENSOR_COVERAGE = "sensor_coverage"
    DRONE_COVERAGE = "drone_coverage"
    PATROL_ROUTE = "patrol_route"
    CUSTOM = "custom"


class WeatherCondition(str, Enum):
    """Weather conditions."""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    HEAVY_SNOW = "heavy_snow"
    FOG = "fog"
    HAZE = "haze"
    WIND = "wind"
    EXTREME_HEAT = "extreme_heat"
    EXTREME_COLD = "extreme_cold"


class TrafficLevel(str, Enum):
    """Traffic congestion levels."""
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    CONGESTED = "congested"
    BLOCKED = "blocked"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WeatherOverlay(BaseModel):
    """Weather overlay data."""
    overlay_id: str
    overlay_type: OverlayType = OverlayType.WEATHER
    condition: WeatherCondition
    temperature_c: float
    feels_like_c: Optional[float] = None
    humidity_percent: float = 50.0
    wind_speed_kmh: float = 0.0
    wind_direction_deg: float = 0.0
    visibility_km: float = 10.0
    precipitation_mm: float = 0.0
    uv_index: int = 0
    air_quality_index: Optional[int] = None
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    forecast_hours: list[dict[str, Any]] = Field(default_factory=list)
    alerts: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrafficOverlay(BaseModel):
    """Traffic overlay data."""
    overlay_id: str
    overlay_type: OverlayType = OverlayType.TRAFFIC
    segments: list[dict[str, Any]] = Field(default_factory=list)
    congestion_level: TrafficLevel = TrafficLevel.FREE_FLOW
    avg_speed_kmh: float = 50.0
    incidents: list[str] = Field(default_factory=list)
    road_closures: list[str] = Field(default_factory=list)
    construction_zones: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class IncidentOverlay(BaseModel):
    """Incident overlay data."""
    overlay_id: str
    overlay_type: OverlayType = OverlayType.INCIDENT
    incident_id: str
    incident_type: str
    severity: IncidentSeverity
    latitude: float
    longitude: float
    radius_m: float = 100.0
    perimeter_coords: list[tuple[float, float]] = Field(default_factory=list)
    color: str = "#EF4444"
    opacity: float = 0.5
    label: str = ""
    description: str = ""
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class HeatmapOverlay(BaseModel):
    """Heatmap overlay data."""
    overlay_id: str
    overlay_type: OverlayType = OverlayType.HEATMAP
    name: str
    data_points: list[dict[str, Any]] = Field(default_factory=list)
    gradient: dict[str, str] = Field(default_factory=lambda: {
        "0.0": "#00FF00",
        "0.5": "#FFFF00",
        "1.0": "#FF0000",
    })
    radius: int = 25
    blur: int = 15
    max_intensity: float = 1.0
    opacity: float = 0.6
    visible: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ZoneOverlay(BaseModel):
    """Zone overlay data."""
    overlay_id: str
    overlay_type: OverlayType = OverlayType.ZONE
    zone_id: str
    name: str
    zone_type: str
    boundary_coords: list[tuple[float, float]] = Field(default_factory=list)
    color: str = "#3B82F6"
    fill_color: str = "#3B82F640"
    stroke_width: int = 2
    opacity: float = 0.3
    label: str = ""
    visible: bool = True
    selectable: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class PerimeterOverlay(BaseModel):
    """Perimeter overlay data."""
    overlay_id: str
    overlay_type: OverlayType = OverlayType.PERIMETER
    perimeter_id: str
    name: str
    coords: list[tuple[float, float]] = Field(default_factory=list)
    is_closed: bool = True
    color: str = "#EF4444"
    stroke_width: int = 3
    dash_pattern: list[int] = Field(default_factory=lambda: [10, 5])
    animated: bool = True
    breach_points: list[dict[str, Any]] = Field(default_factory=list)
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class OverlayConfig(BaseModel):
    """Configuration for overlay engine."""
    max_overlays: int = 1000
    max_heatmap_points: int = 10000
    weather_update_interval_seconds: int = 300
    traffic_update_interval_seconds: int = 60


class OverlayMetrics(BaseModel):
    """Metrics for overlay engine."""
    total_overlays: int = 0
    overlays_by_type: dict[str, int] = Field(default_factory=dict)
    active_incidents: int = 0
    active_perimeters: int = 0


class OverlayEngine:
    """
    Overlay Engine.
    
    Manages weather, traffic, and incident overlays for the digital twin.
    """
    
    def __init__(self, config: Optional[OverlayConfig] = None):
        self.config = config or OverlayConfig()
        self._weather: Optional[WeatherOverlay] = None
        self._traffic: Optional[TrafficOverlay] = None
        self._incidents: dict[str, IncidentOverlay] = {}
        self._heatmaps: dict[str, HeatmapOverlay] = {}
        self._zones: dict[str, ZoneOverlay] = {}
        self._perimeters: dict[str, PerimeterOverlay] = {}
        self._custom_overlays: dict[str, dict[str, Any]] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = OverlayMetrics()
    
    async def start(self) -> None:
        """Start the overlay engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the overlay engine."""
        self._running = False
    
    async def update_weather(
        self,
        condition: WeatherCondition,
        temperature_c: float,
        humidity_percent: float = 50.0,
        wind_speed_kmh: float = 0.0,
        wind_direction_deg: float = 0.0,
        visibility_km: float = 10.0,
        precipitation_mm: float = 0.0,
        alerts: Optional[list[str]] = None,
    ) -> WeatherOverlay:
        """Update weather overlay."""
        overlay_id = "weather-main" if not self._weather else self._weather.overlay_id
        
        self._weather = WeatherOverlay(
            overlay_id=overlay_id,
            condition=condition,
            temperature_c=temperature_c,
            humidity_percent=humidity_percent,
            wind_speed_kmh=wind_speed_kmh,
            wind_direction_deg=wind_direction_deg,
            visibility_km=visibility_km,
            precipitation_mm=precipitation_mm,
            alerts=alerts or [],
        )
        
        await self._notify_callbacks(self._weather, "weather_update")
        return self._weather
    
    def get_weather(self) -> Optional[WeatherOverlay]:
        """Get current weather overlay."""
        return self._weather
    
    async def update_traffic(
        self,
        segments: list[dict[str, Any]],
        congestion_level: TrafficLevel = TrafficLevel.FREE_FLOW,
        avg_speed_kmh: float = 50.0,
        incidents: Optional[list[str]] = None,
        road_closures: Optional[list[str]] = None,
    ) -> TrafficOverlay:
        """Update traffic overlay."""
        overlay_id = "traffic-main" if not self._traffic else self._traffic.overlay_id
        
        self._traffic = TrafficOverlay(
            overlay_id=overlay_id,
            segments=segments,
            congestion_level=congestion_level,
            avg_speed_kmh=avg_speed_kmh,
            incidents=incidents or [],
            road_closures=road_closures or [],
        )
        
        await self._notify_callbacks(self._traffic, "traffic_update")
        return self._traffic
    
    def get_traffic(self) -> Optional[TrafficOverlay]:
        """Get current traffic overlay."""
        return self._traffic
    
    async def add_incident_overlay(
        self,
        incident_id: str,
        incident_type: str,
        severity: IncidentSeverity,
        latitude: float,
        longitude: float,
        radius_m: float = 100.0,
        perimeter_coords: Optional[list[tuple[float, float]]] = None,
        label: str = "",
        description: str = "",
    ) -> IncidentOverlay:
        """Add an incident overlay."""
        overlay_id = f"incident-{uuid.uuid4().hex[:8]}"
        
        color_map = {
            IncidentSeverity.LOW: "#10B981",
            IncidentSeverity.MEDIUM: "#F59E0B",
            IncidentSeverity.HIGH: "#EF4444",
            IncidentSeverity.CRITICAL: "#DC2626",
        }
        
        overlay = IncidentOverlay(
            overlay_id=overlay_id,
            incident_id=incident_id,
            incident_type=incident_type,
            severity=severity,
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
            perimeter_coords=perimeter_coords or [],
            color=color_map.get(severity, "#EF4444"),
            label=label,
            description=description,
        )
        
        self._incidents[incident_id] = overlay
        self._update_metrics()
        
        await self._notify_callbacks(overlay, "incident_added")
        return overlay
    
    async def update_incident_overlay(
        self,
        incident_id: str,
        severity: Optional[IncidentSeverity] = None,
        radius_m: Optional[float] = None,
        perimeter_coords: Optional[list[tuple[float, float]]] = None,
        active: Optional[bool] = None,
    ) -> Optional[IncidentOverlay]:
        """Update an incident overlay."""
        overlay = self._incidents.get(incident_id)
        if not overlay:
            return None
        
        if severity is not None:
            overlay.severity = severity
        if radius_m is not None:
            overlay.radius_m = radius_m
        if perimeter_coords is not None:
            overlay.perimeter_coords = perimeter_coords
        if active is not None:
            overlay.active = active
        
        overlay.updated_at = datetime.now(timezone.utc)
        self._update_metrics()
        
        await self._notify_callbacks(overlay, "incident_updated")
        return overlay
    
    async def remove_incident_overlay(self, incident_id: str) -> bool:
        """Remove an incident overlay."""
        if incident_id not in self._incidents:
            return False
        
        del self._incidents[incident_id]
        self._update_metrics()
        return True
    
    def get_incident_overlay(self, incident_id: str) -> Optional[IncidentOverlay]:
        """Get an incident overlay."""
        return self._incidents.get(incident_id)
    
    def get_all_incident_overlays(self) -> list[IncidentOverlay]:
        """Get all incident overlays."""
        return list(self._incidents.values())
    
    def get_active_incident_overlays(self) -> list[IncidentOverlay]:
        """Get all active incident overlays."""
        return [i for i in self._incidents.values() if i.active]
    
    def add_heatmap(
        self,
        name: str,
        data_points: list[dict[str, Any]],
        gradient: Optional[dict[str, str]] = None,
        radius: int = 25,
        opacity: float = 0.6,
    ) -> HeatmapOverlay:
        """Add a heatmap overlay."""
        overlay_id = f"heatmap-{uuid.uuid4().hex[:8]}"
        
        overlay = HeatmapOverlay(
            overlay_id=overlay_id,
            name=name,
            data_points=data_points[:self.config.max_heatmap_points],
            gradient=gradient or {},
            radius=radius,
            opacity=opacity,
        )
        
        self._heatmaps[overlay_id] = overlay
        self._update_metrics()
        
        return overlay
    
    def update_heatmap(
        self,
        overlay_id: str,
        data_points: list[dict[str, Any]],
    ) -> Optional[HeatmapOverlay]:
        """Update heatmap data points."""
        overlay = self._heatmaps.get(overlay_id)
        if not overlay:
            return None
        
        overlay.data_points = data_points[:self.config.max_heatmap_points]
        overlay.updated_at = datetime.now(timezone.utc)
        
        return overlay
    
    def remove_heatmap(self, overlay_id: str) -> bool:
        """Remove a heatmap overlay."""
        if overlay_id not in self._heatmaps:
            return False
        
        del self._heatmaps[overlay_id]
        self._update_metrics()
        return True
    
    def get_heatmap(self, overlay_id: str) -> Optional[HeatmapOverlay]:
        """Get a heatmap overlay."""
        return self._heatmaps.get(overlay_id)
    
    def get_all_heatmaps(self) -> list[HeatmapOverlay]:
        """Get all heatmap overlays."""
        return list(self._heatmaps.values())
    
    def add_zone(
        self,
        zone_id: str,
        name: str,
        zone_type: str,
        boundary_coords: list[tuple[float, float]],
        color: str = "#3B82F6",
        opacity: float = 0.3,
    ) -> ZoneOverlay:
        """Add a zone overlay."""
        overlay_id = f"zone-{uuid.uuid4().hex[:8]}"
        
        overlay = ZoneOverlay(
            overlay_id=overlay_id,
            zone_id=zone_id,
            name=name,
            zone_type=zone_type,
            boundary_coords=boundary_coords,
            color=color,
            fill_color=f"{color}40",
            opacity=opacity,
            label=name,
        )
        
        self._zones[zone_id] = overlay
        self._update_metrics()
        
        return overlay
    
    def remove_zone(self, zone_id: str) -> bool:
        """Remove a zone overlay."""
        if zone_id not in self._zones:
            return False
        
        del self._zones[zone_id]
        self._update_metrics()
        return True
    
    def get_zone(self, zone_id: str) -> Optional[ZoneOverlay]:
        """Get a zone overlay."""
        return self._zones.get(zone_id)
    
    def get_all_zones(self) -> list[ZoneOverlay]:
        """Get all zone overlays."""
        return list(self._zones.values())
    
    async def add_perimeter(
        self,
        perimeter_id: str,
        name: str,
        coords: list[tuple[float, float]],
        is_closed: bool = True,
        color: str = "#EF4444",
        animated: bool = True,
    ) -> PerimeterOverlay:
        """Add a perimeter overlay."""
        overlay_id = f"perimeter-{uuid.uuid4().hex[:8]}"
        
        overlay = PerimeterOverlay(
            overlay_id=overlay_id,
            perimeter_id=perimeter_id,
            name=name,
            coords=coords,
            is_closed=is_closed,
            color=color,
            animated=animated,
        )
        
        self._perimeters[perimeter_id] = overlay
        self._update_metrics()
        
        await self._notify_callbacks(overlay, "perimeter_added")
        return overlay
    
    async def add_breach_point(
        self,
        perimeter_id: str,
        latitude: float,
        longitude: float,
        breach_type: str = "unknown",
    ) -> bool:
        """Add a breach point to a perimeter."""
        overlay = self._perimeters.get(perimeter_id)
        if not overlay:
            return False
        
        breach = {
            "breach_id": f"breach-{uuid.uuid4().hex[:8]}",
            "latitude": latitude,
            "longitude": longitude,
            "breach_type": breach_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        overlay.breach_points.append(breach)
        
        await self._notify_callbacks(overlay, "perimeter_breach")
        return True
    
    async def remove_perimeter(self, perimeter_id: str) -> bool:
        """Remove a perimeter overlay."""
        if perimeter_id not in self._perimeters:
            return False
        
        del self._perimeters[perimeter_id]
        self._update_metrics()
        return True
    
    def get_perimeter(self, perimeter_id: str) -> Optional[PerimeterOverlay]:
        """Get a perimeter overlay."""
        return self._perimeters.get(perimeter_id)
    
    def get_all_perimeters(self) -> list[PerimeterOverlay]:
        """Get all perimeter overlays."""
        return list(self._perimeters.values())
    
    def get_active_perimeters(self) -> list[PerimeterOverlay]:
        """Get all active perimeter overlays."""
        return [p for p in self._perimeters.values() if p.active]
    
    def add_custom_overlay(
        self,
        overlay_id: str,
        overlay_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Add a custom overlay."""
        overlay = {
            "overlay_id": overlay_id,
            "overlay_type": overlay_type,
            "data": data,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        self._custom_overlays[overlay_id] = overlay
        self._update_metrics()
        
        return overlay
    
    def remove_custom_overlay(self, overlay_id: str) -> bool:
        """Remove a custom overlay."""
        if overlay_id not in self._custom_overlays:
            return False
        
        del self._custom_overlays[overlay_id]
        self._update_metrics()
        return True
    
    def get_custom_overlay(self, overlay_id: str) -> Optional[dict[str, Any]]:
        """Get a custom overlay."""
        return self._custom_overlays.get(overlay_id)
    
    def get_all_overlays(self) -> dict[str, Any]:
        """Get all overlays for rendering."""
        return {
            "weather": self._weather.model_dump() if self._weather else None,
            "traffic": self._traffic.model_dump() if self._traffic else None,
            "incidents": [i.model_dump() for i in self._incidents.values()],
            "heatmaps": [h.model_dump() for h in self._heatmaps.values()],
            "zones": [z.model_dump() for z in self._zones.values()],
            "perimeters": [p.model_dump() for p in self._perimeters.values()],
            "custom": list(self._custom_overlays.values()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def get_metrics(self) -> OverlayMetrics:
        """Get overlay metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get overlay engine status."""
        return {
            "running": self._running,
            "has_weather": self._weather is not None,
            "has_traffic": self._traffic is not None,
            "incident_count": len(self._incidents),
            "heatmap_count": len(self._heatmaps),
            "zone_count": len(self._zones),
            "perimeter_count": len(self._perimeters),
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for overlay events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update overlay metrics."""
        type_counts: dict[str, int] = {}
        
        if self._weather:
            type_counts["weather"] = 1
        if self._traffic:
            type_counts["traffic"] = 1
        
        type_counts["incident"] = len(self._incidents)
        type_counts["heatmap"] = len(self._heatmaps)
        type_counts["zone"] = len(self._zones)
        type_counts["perimeter"] = len(self._perimeters)
        type_counts["custom"] = len(self._custom_overlays)
        
        total = sum(type_counts.values())
        
        self._metrics.total_overlays = total
        self._metrics.overlays_by_type = type_counts
        self._metrics.active_incidents = len([i for i in self._incidents.values() if i.active])
        self._metrics.active_perimeters = len([p for p in self._perimeters.values() if p.active])
    
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
