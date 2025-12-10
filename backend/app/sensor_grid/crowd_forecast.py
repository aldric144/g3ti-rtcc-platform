"""
Crowd Forecast Model.

Predicts crowd density and movement patterns for proactive resource allocation.
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class CrowdDensity(str, Enum):
    """Crowd density levels."""
    EMPTY = "empty"
    SPARSE = "sparse"
    MODERATE = "moderate"
    DENSE = "dense"
    CRITICAL = "critical"


class CrowdTrend(str, Enum):
    """Crowd movement trends."""
    DECREASING_FAST = "decreasing_fast"
    DECREASING = "decreasing"
    STABLE = "stable"
    INCREASING = "increasing"
    INCREASING_FAST = "increasing_fast"


class RiskLevel(str, Enum):
    """Risk levels for crowd situations."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class CrowdZone(BaseModel):
    """Geographic zone for crowd monitoring."""
    zone_id: str
    name: str
    boundary_coords: list[tuple[float, float]]
    center_lat: float
    center_lon: float
    area_sq_m: float
    capacity: int
    current_count: int = 0
    density: CrowdDensity = CrowdDensity.EMPTY
    density_per_sq_m: float = 0.0
    trend: CrowdTrend = CrowdTrend.STABLE
    risk_level: RiskLevel = RiskLevel.MINIMAL
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sensors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CrowdPrediction(BaseModel):
    """Crowd prediction for a zone."""
    prediction_id: str
    zone_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    prediction_time: datetime
    predicted_count: int
    predicted_density: CrowdDensity
    predicted_trend: CrowdTrend
    predicted_risk: RiskLevel
    confidence: float = 0.5
    factors: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CrowdAlert(BaseModel):
    """Alert for crowd situations."""
    alert_id: str
    zone_id: str
    zone_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    alert_type: str
    severity: str
    current_count: int
    threshold: int
    message: str
    recommendations: list[str] = Field(default_factory=list)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class HistoricalPattern(BaseModel):
    """Historical crowd pattern."""
    pattern_id: str
    zone_id: str
    day_of_week: int
    hour: int
    avg_count: float
    std_dev: float
    peak_count: int
    samples: int = 0


class ForecastConfig(BaseModel):
    """Configuration for crowd forecast model."""
    max_zones: int = 1000
    max_predictions_per_zone: int = 100
    max_alerts: int = 10000
    prediction_horizon_hours: int = 4
    update_interval_seconds: int = 60
    density_thresholds: dict[str, float] = Field(default_factory=lambda: {
        "sparse": 0.5,
        "moderate": 1.0,
        "dense": 2.5,
        "critical": 4.0,
    })


class ForecastMetrics(BaseModel):
    """Metrics for crowd forecast model."""
    total_zones: int = 0
    zones_by_density: dict[str, int] = Field(default_factory=dict)
    zones_by_risk: dict[str, int] = Field(default_factory=dict)
    total_predictions: int = 0
    total_alerts: int = 0
    active_alerts: int = 0
    prediction_accuracy: float = 0.0


class CrowdForecastModel:
    """
    Crowd Forecast Model.
    
    Predicts crowd density and movement patterns for proactive resource allocation.
    """
    
    def __init__(self, config: Optional[ForecastConfig] = None):
        self.config = config or ForecastConfig()
        self._zones: dict[str, CrowdZone] = {}
        self._predictions: dict[str, deque[CrowdPrediction]] = {}
        self._alerts: deque[CrowdAlert] = deque(maxlen=self.config.max_alerts)
        self._historical_patterns: dict[str, list[HistoricalPattern]] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = ForecastMetrics()
    
    async def start(self) -> None:
        """Start the forecast model."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the forecast model."""
        self._running = False
    
    def register_zone(
        self,
        name: str,
        boundary_coords: list[tuple[float, float]],
        capacity: int,
        sensors: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> CrowdZone:
        """Register a crowd monitoring zone."""
        zone_id = f"zone-{uuid.uuid4().hex[:12]}"
        
        center_lat = sum(c[0] for c in boundary_coords) / len(boundary_coords)
        center_lon = sum(c[1] for c in boundary_coords) / len(boundary_coords)
        
        area_sq_m = self._calculate_polygon_area(boundary_coords)
        
        zone = CrowdZone(
            zone_id=zone_id,
            name=name,
            boundary_coords=boundary_coords,
            center_lat=center_lat,
            center_lon=center_lon,
            area_sq_m=area_sq_m,
            capacity=capacity,
            sensors=sensors or [],
            metadata=metadata or {},
        )
        
        self._zones[zone_id] = zone
        self._predictions[zone_id] = deque(maxlen=self.config.max_predictions_per_zone)
        self._historical_patterns[zone_id] = []
        
        self._update_metrics()
        
        return zone
    
    def unregister_zone(self, zone_id: str) -> bool:
        """Unregister a crowd monitoring zone."""
        if zone_id not in self._zones:
            return False
        
        del self._zones[zone_id]
        if zone_id in self._predictions:
            del self._predictions[zone_id]
        if zone_id in self._historical_patterns:
            del self._historical_patterns[zone_id]
        
        self._update_metrics()
        return True
    
    async def update_zone_count(
        self,
        zone_id: str,
        count: int,
        source: str = "sensor",
    ) -> Optional[CrowdZone]:
        """Update the crowd count for a zone."""
        zone = self._zones.get(zone_id)
        if not zone:
            return None
        
        previous_count = zone.current_count
        zone.current_count = count
        zone.last_updated = datetime.now(timezone.utc)
        
        zone.density_per_sq_m = count / zone.area_sq_m if zone.area_sq_m > 0 else 0
        zone.density = self._calculate_density_level(zone.density_per_sq_m)
        
        zone.trend = self._calculate_trend(previous_count, count)
        
        zone.risk_level = self._calculate_risk_level(zone)
        
        if zone.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            await self._generate_alert(zone)
        
        self._update_metrics()
        await self._notify_callbacks(zone, "updated")
        
        return zone
    
    async def generate_predictions(
        self,
        zone_id: str,
        hours_ahead: int = 4,
    ) -> list[CrowdPrediction]:
        """Generate crowd predictions for a zone."""
        zone = self._zones.get(zone_id)
        if not zone:
            return []
        
        predictions = []
        now = datetime.now(timezone.utc)
        
        for hour_offset in range(1, hours_ahead + 1):
            prediction_time = now + timedelta(hours=hour_offset)
            
            historical = self._get_historical_pattern(
                zone_id,
                prediction_time.weekday(),
                prediction_time.hour,
            )
            
            if historical:
                base_count = int(historical.avg_count)
                confidence = min(0.9, 0.5 + (historical.samples / 100) * 0.4)
            else:
                base_count = zone.current_count
                confidence = 0.3
            
            if zone.trend == CrowdTrend.INCREASING_FAST:
                base_count = int(base_count * 1.3)
            elif zone.trend == CrowdTrend.INCREASING:
                base_count = int(base_count * 1.15)
            elif zone.trend == CrowdTrend.DECREASING:
                base_count = int(base_count * 0.85)
            elif zone.trend == CrowdTrend.DECREASING_FAST:
                base_count = int(base_count * 0.7)
            
            predicted_density_per_sq_m = base_count / zone.area_sq_m if zone.area_sq_m > 0 else 0
            predicted_density = self._calculate_density_level(predicted_density_per_sq_m)
            
            predicted_trend = zone.trend
            
            temp_zone = CrowdZone(
                zone_id=zone_id,
                name=zone.name,
                boundary_coords=zone.boundary_coords,
                center_lat=zone.center_lat,
                center_lon=zone.center_lon,
                area_sq_m=zone.area_sq_m,
                capacity=zone.capacity,
                current_count=base_count,
                density=predicted_density,
                density_per_sq_m=predicted_density_per_sq_m,
            )
            predicted_risk = self._calculate_risk_level(temp_zone)
            
            factors = self._identify_factors(zone, prediction_time)
            recommendations = self._generate_recommendations(predicted_density, predicted_risk)
            
            prediction = CrowdPrediction(
                prediction_id=f"pred-{uuid.uuid4().hex[:12]}",
                zone_id=zone_id,
                prediction_time=prediction_time,
                predicted_count=base_count,
                predicted_density=predicted_density,
                predicted_trend=predicted_trend,
                predicted_risk=predicted_risk,
                confidence=confidence,
                factors=factors,
                recommendations=recommendations,
            )
            
            predictions.append(prediction)
            self._predictions[zone_id].append(prediction)
        
        self._metrics.total_predictions += len(predictions)
        
        return predictions
    
    async def _generate_alert(self, zone: CrowdZone) -> CrowdAlert:
        """Generate an alert for a zone."""
        if zone.risk_level == RiskLevel.CRITICAL:
            alert_type = "critical_density"
            severity = "critical"
            message = f"CRITICAL: Zone '{zone.name}' has reached critical crowd density"
        else:
            alert_type = "high_density"
            severity = "high"
            message = f"WARNING: Zone '{zone.name}' has high crowd density"
        
        recommendations = self._generate_recommendations(zone.density, zone.risk_level)
        
        alert = CrowdAlert(
            alert_id=f"alert-{uuid.uuid4().hex[:12]}",
            zone_id=zone.zone_id,
            zone_name=zone.name,
            alert_type=alert_type,
            severity=severity,
            current_count=zone.current_count,
            threshold=zone.capacity,
            message=message,
            recommendations=recommendations,
        )
        
        self._alerts.append(alert)
        self._metrics.total_alerts += 1
        self._metrics.active_alerts = len([a for a in self._alerts if not a.acknowledged])
        
        await self._notify_callbacks(alert, "alert")
        
        return alert
    
    def record_historical_data(
        self,
        zone_id: str,
        timestamp: datetime,
        count: int,
    ) -> None:
        """Record historical data for pattern learning."""
        if zone_id not in self._historical_patterns:
            return
        
        day_of_week = timestamp.weekday()
        hour = timestamp.hour
        
        existing = None
        for pattern in self._historical_patterns[zone_id]:
            if pattern.day_of_week == day_of_week and pattern.hour == hour:
                existing = pattern
                break
        
        if existing:
            n = existing.samples
            old_avg = existing.avg_count
            new_avg = (old_avg * n + count) / (n + 1)
            
            old_var = existing.std_dev ** 2
            new_var = ((n - 1) * old_var + (count - old_avg) * (count - new_avg)) / n if n > 0 else 0
            
            existing.avg_count = new_avg
            existing.std_dev = new_var ** 0.5
            existing.peak_count = max(existing.peak_count, count)
            existing.samples = n + 1
        else:
            pattern = HistoricalPattern(
                pattern_id=f"pattern-{uuid.uuid4().hex[:8]}",
                zone_id=zone_id,
                day_of_week=day_of_week,
                hour=hour,
                avg_count=float(count),
                std_dev=0.0,
                peak_count=count,
                samples=1,
            )
            self._historical_patterns[zone_id].append(pattern)
    
    def _get_historical_pattern(
        self,
        zone_id: str,
        day_of_week: int,
        hour: int,
    ) -> Optional[HistoricalPattern]:
        """Get historical pattern for a specific time."""
        if zone_id not in self._historical_patterns:
            return None
        
        for pattern in self._historical_patterns[zone_id]:
            if pattern.day_of_week == day_of_week and pattern.hour == hour:
                return pattern
        
        return None
    
    def _calculate_density_level(self, density_per_sq_m: float) -> CrowdDensity:
        """Calculate density level from density per square meter."""
        thresholds = self.config.density_thresholds
        
        if density_per_sq_m >= thresholds["critical"]:
            return CrowdDensity.CRITICAL
        if density_per_sq_m >= thresholds["dense"]:
            return CrowdDensity.DENSE
        if density_per_sq_m >= thresholds["moderate"]:
            return CrowdDensity.MODERATE
        if density_per_sq_m >= thresholds["sparse"]:
            return CrowdDensity.SPARSE
        return CrowdDensity.EMPTY
    
    def _calculate_trend(self, previous: int, current: int) -> CrowdTrend:
        """Calculate trend from count change."""
        if previous == 0:
            return CrowdTrend.STABLE
        
        change_pct = (current - previous) / previous
        
        if change_pct >= 0.3:
            return CrowdTrend.INCREASING_FAST
        if change_pct >= 0.1:
            return CrowdTrend.INCREASING
        if change_pct <= -0.3:
            return CrowdTrend.DECREASING_FAST
        if change_pct <= -0.1:
            return CrowdTrend.DECREASING
        return CrowdTrend.STABLE
    
    def _calculate_risk_level(self, zone: CrowdZone) -> RiskLevel:
        """Calculate risk level for a zone."""
        capacity_ratio = zone.current_count / zone.capacity if zone.capacity > 0 else 0
        
        if zone.density == CrowdDensity.CRITICAL or capacity_ratio >= 1.0:
            return RiskLevel.CRITICAL
        if zone.density == CrowdDensity.DENSE or capacity_ratio >= 0.8:
            return RiskLevel.HIGH
        if zone.density == CrowdDensity.MODERATE or capacity_ratio >= 0.6:
            return RiskLevel.MODERATE
        if zone.density == CrowdDensity.SPARSE or capacity_ratio >= 0.3:
            return RiskLevel.LOW
        return RiskLevel.MINIMAL
    
    def _identify_factors(self, zone: CrowdZone, prediction_time: datetime) -> list[str]:
        """Identify factors affecting crowd prediction."""
        factors = []
        
        if prediction_time.weekday() >= 5:
            factors.append("weekend")
        
        hour = prediction_time.hour
        if 7 <= hour <= 9:
            factors.append("morning_rush")
        elif 11 <= hour <= 13:
            factors.append("lunch_hour")
        elif 16 <= hour <= 18:
            factors.append("evening_rush")
        elif 20 <= hour <= 23:
            factors.append("nightlife")
        
        if zone.trend in [CrowdTrend.INCREASING, CrowdTrend.INCREASING_FAST]:
            factors.append("increasing_trend")
        elif zone.trend in [CrowdTrend.DECREASING, CrowdTrend.DECREASING_FAST]:
            factors.append("decreasing_trend")
        
        return factors
    
    def _generate_recommendations(
        self,
        density: CrowdDensity,
        risk: RiskLevel,
    ) -> list[str]:
        """Generate recommendations based on density and risk."""
        recommendations = []
        
        if risk == RiskLevel.CRITICAL:
            recommendations.extend([
                "Deploy additional officers immediately",
                "Consider crowd control measures",
                "Prepare evacuation routes",
                "Alert emergency services",
            ])
        elif risk == RiskLevel.HIGH:
            recommendations.extend([
                "Increase patrol presence",
                "Monitor entry/exit points",
                "Prepare crowd management resources",
            ])
        elif risk == RiskLevel.MODERATE:
            recommendations.extend([
                "Maintain situational awareness",
                "Monitor crowd flow patterns",
            ])
        
        return recommendations
    
    def _calculate_polygon_area(self, coords: list[tuple[float, float]]) -> float:
        """Calculate approximate area of a polygon in square meters."""
        if len(coords) < 3:
            return 0.0
        
        n = len(coords)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][1] * coords[j][0]
            area -= coords[j][1] * coords[i][0]
        
        area = abs(area) / 2.0
        
        center_lat = sum(c[0] for c in coords) / n
        meters_per_degree = 111320 * abs(center_lat)
        
        return area * meters_per_degree * meters_per_degree
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
    ) -> bool:
        """Acknowledge an alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now(timezone.utc)
                self._metrics.active_alerts = len([a for a in self._alerts if not a.acknowledged])
                return True
        return False
    
    def get_zone(self, zone_id: str) -> Optional[CrowdZone]:
        """Get a zone by ID."""
        return self._zones.get(zone_id)
    
    def get_all_zones(self) -> list[CrowdZone]:
        """Get all registered zones."""
        return list(self._zones.values())
    
    def get_zones_by_density(self, density: CrowdDensity) -> list[CrowdZone]:
        """Get zones by density level."""
        return [z for z in self._zones.values() if z.density == density]
    
    def get_zones_by_risk(self, risk: RiskLevel) -> list[CrowdZone]:
        """Get zones by risk level."""
        return [z for z in self._zones.values() if z.risk_level == risk]
    
    def get_predictions(self, zone_id: str, limit: int = 10) -> list[CrowdPrediction]:
        """Get predictions for a zone."""
        if zone_id not in self._predictions:
            return []
        
        predictions = list(self._predictions[zone_id])
        predictions.reverse()
        return predictions[:limit]
    
    def get_active_alerts(self) -> list[CrowdAlert]:
        """Get active (unacknowledged) alerts."""
        return [a for a in self._alerts if not a.acknowledged]
    
    def get_recent_alerts(self, limit: int = 100) -> list[CrowdAlert]:
        """Get recent alerts."""
        alerts = list(self._alerts)
        alerts.reverse()
        return alerts[:limit]
    
    def get_metrics(self) -> ForecastMetrics:
        """Get forecast metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get forecast model status."""
        return {
            "running": self._running,
            "total_zones": len(self._zones),
            "active_alerts": self._metrics.active_alerts,
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update forecast metrics."""
        density_counts: dict[str, int] = {}
        risk_counts: dict[str, int] = {}
        
        for zone in self._zones.values():
            density_counts[zone.density.value] = density_counts.get(zone.density.value, 0) + 1
            risk_counts[zone.risk_level.value] = risk_counts.get(zone.risk_level.value, 0) + 1
        
        self._metrics.total_zones = len(self._zones)
        self._metrics.zones_by_density = density_counts
        self._metrics.zones_by_risk = risk_counts
    
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
