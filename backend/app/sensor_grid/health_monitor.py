"""
Sensor Health Monitor.

Monitors the health and status of all sensors in the smart sensor grid.
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class SensorHealthStatus(str, Enum):
    """Health status levels for sensors."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Severity levels for health alerts."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SensorHealth(BaseModel):
    """Health status for a sensor."""
    sensor_id: str
    sensor_name: str
    sensor_type: str
    status: SensorHealthStatus = SensorHealthStatus.UNKNOWN
    last_reading_at: Optional[datetime] = None
    last_check_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_percent: float = 0.0
    response_time_ms: Optional[float] = None
    battery_percent: Optional[float] = None
    signal_strength_dbm: Optional[int] = None
    error_count_24h: int = 0
    warning_count_24h: int = 0
    readings_24h: int = 0
    expected_readings_24h: int = 0
    data_quality_score: float = 1.0
    issues: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthAlert(BaseModel):
    """Health alert for a sensor."""
    alert_id: str
    sensor_id: str
    sensor_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: AlertSeverity
    alert_type: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class HealthCheckResult(BaseModel):
    """Result of a health check."""
    check_id: str
    sensor_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: SensorHealthStatus
    response_time_ms: Optional[float] = None
    checks_passed: list[str] = Field(default_factory=list)
    checks_failed: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class MonitorConfig(BaseModel):
    """Configuration for sensor health monitor."""
    check_interval_seconds: int = 60
    offline_threshold_seconds: int = 300
    degraded_threshold_seconds: int = 120
    max_alerts: int = 10000
    max_check_history: int = 1000
    battery_warning_threshold: float = 20.0
    battery_critical_threshold: float = 10.0
    signal_warning_threshold: int = -80
    signal_critical_threshold: int = -90
    data_quality_warning_threshold: float = 0.8
    data_quality_critical_threshold: float = 0.5


class MonitorMetrics(BaseModel):
    """Metrics for sensor health monitor."""
    total_sensors: int = 0
    sensors_by_status: dict[str, int] = Field(default_factory=dict)
    healthy_count: int = 0
    degraded_count: int = 0
    unhealthy_count: int = 0
    offline_count: int = 0
    total_alerts: int = 0
    active_alerts: int = 0
    avg_uptime_percent: float = 0.0
    avg_data_quality: float = 0.0


class SensorHealthMonitor:
    """
    Sensor Health Monitor.
    
    Monitors the health and status of all sensors in the smart sensor grid.
    """
    
    def __init__(self, config: Optional[MonitorConfig] = None):
        self.config = config or MonitorConfig()
        self._sensor_health: dict[str, SensorHealth] = {}
        self._alerts: deque[HealthAlert] = deque(maxlen=self.config.max_alerts)
        self._check_history: dict[str, deque[HealthCheckResult]] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = MonitorMetrics()
    
    async def start(self) -> None:
        """Start the health monitor."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the health monitor."""
        self._running = False
    
    def register_sensor(
        self,
        sensor_id: str,
        sensor_name: str,
        sensor_type: str,
        expected_readings_24h: int = 1440,
    ) -> SensorHealth:
        """Register a sensor for health monitoring."""
        health = SensorHealth(
            sensor_id=sensor_id,
            sensor_name=sensor_name,
            sensor_type=sensor_type,
            expected_readings_24h=expected_readings_24h,
        )
        
        self._sensor_health[sensor_id] = health
        self._check_history[sensor_id] = deque(maxlen=self.config.max_check_history)
        
        self._update_metrics()
        
        return health
    
    def unregister_sensor(self, sensor_id: str) -> bool:
        """Unregister a sensor from health monitoring."""
        if sensor_id not in self._sensor_health:
            return False
        
        del self._sensor_health[sensor_id]
        if sensor_id in self._check_history:
            del self._check_history[sensor_id]
        
        self._update_metrics()
        return True
    
    async def check_sensor_health(
        self,
        sensor_id: str,
        response_time_ms: Optional[float] = None,
        battery_percent: Optional[float] = None,
        signal_strength_dbm: Optional[int] = None,
    ) -> Optional[HealthCheckResult]:
        """Perform a health check on a sensor."""
        health = self._sensor_health.get(sensor_id)
        if not health:
            return None
        
        checks_passed = []
        checks_failed = []
        issues = []
        
        now = datetime.now(timezone.utc)
        
        if health.last_reading_at:
            time_since_reading = (now - health.last_reading_at).total_seconds()
            
            if time_since_reading > self.config.offline_threshold_seconds:
                checks_failed.append("reading_freshness")
                issues.append(f"No reading for {int(time_since_reading)}s")
            elif time_since_reading > self.config.degraded_threshold_seconds:
                checks_failed.append("reading_freshness_warning")
                issues.append(f"Reading delayed by {int(time_since_reading)}s")
            else:
                checks_passed.append("reading_freshness")
        else:
            checks_failed.append("no_readings")
            issues.append("No readings received")
        
        if battery_percent is not None:
            health.battery_percent = battery_percent
            if battery_percent < self.config.battery_critical_threshold:
                checks_failed.append("battery_critical")
                issues.append(f"Battery critical: {battery_percent:.0f}%")
            elif battery_percent < self.config.battery_warning_threshold:
                checks_failed.append("battery_warning")
                issues.append(f"Battery low: {battery_percent:.0f}%")
            else:
                checks_passed.append("battery")
        
        if signal_strength_dbm is not None:
            health.signal_strength_dbm = signal_strength_dbm
            if signal_strength_dbm < self.config.signal_critical_threshold:
                checks_failed.append("signal_critical")
                issues.append(f"Signal critical: {signal_strength_dbm} dBm")
            elif signal_strength_dbm < self.config.signal_warning_threshold:
                checks_failed.append("signal_warning")
                issues.append(f"Signal weak: {signal_strength_dbm} dBm")
            else:
                checks_passed.append("signal")
        
        if health.data_quality_score < self.config.data_quality_critical_threshold:
            checks_failed.append("data_quality_critical")
            issues.append(f"Data quality critical: {health.data_quality_score:.0%}")
        elif health.data_quality_score < self.config.data_quality_warning_threshold:
            checks_failed.append("data_quality_warning")
            issues.append(f"Data quality degraded: {health.data_quality_score:.0%}")
        else:
            checks_passed.append("data_quality")
        
        if any("critical" in c for c in checks_failed):
            status = SensorHealthStatus.UNHEALTHY
        elif "no_readings" in checks_failed or "reading_freshness" in checks_failed:
            status = SensorHealthStatus.OFFLINE
        elif checks_failed:
            status = SensorHealthStatus.DEGRADED
        else:
            status = SensorHealthStatus.HEALTHY
        
        health.status = status
        health.last_check_at = now
        health.response_time_ms = response_time_ms
        health.issues = issues
        
        result = HealthCheckResult(
            check_id=f"check-{uuid.uuid4().hex[:12]}",
            sensor_id=sensor_id,
            status=status,
            response_time_ms=response_time_ms,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            details={
                "battery_percent": battery_percent,
                "signal_strength_dbm": signal_strength_dbm,
                "data_quality_score": health.data_quality_score,
            },
        )
        
        self._check_history[sensor_id].append(result)
        
        if status in [SensorHealthStatus.UNHEALTHY, SensorHealthStatus.OFFLINE]:
            await self._generate_alert(health, status, issues)
        
        self._update_metrics()
        await self._notify_callbacks(health, "health_check")
        
        return result
    
    async def record_reading(
        self,
        sensor_id: str,
        quality: float = 1.0,
    ) -> bool:
        """Record that a reading was received from a sensor."""
        health = self._sensor_health.get(sensor_id)
        if not health:
            return False
        
        health.last_reading_at = datetime.now(timezone.utc)
        health.readings_24h += 1
        
        n = health.readings_24h
        health.data_quality_score = (health.data_quality_score * (n - 1) + quality) / n
        
        if health.status == SensorHealthStatus.OFFLINE:
            health.status = SensorHealthStatus.HEALTHY
            await self._notify_callbacks(health, "back_online")
        
        return True
    
    async def record_error(
        self,
        sensor_id: str,
        error_message: str,
    ) -> bool:
        """Record an error from a sensor."""
        health = self._sensor_health.get(sensor_id)
        if not health:
            return False
        
        health.error_count_24h += 1
        
        if health.error_count_24h >= 5:
            health.status = SensorHealthStatus.UNHEALTHY
            await self._generate_alert(
                health,
                SensorHealthStatus.UNHEALTHY,
                [f"Multiple errors: {error_message}"],
            )
        elif health.error_count_24h >= 2:
            health.status = SensorHealthStatus.DEGRADED
        
        self._update_metrics()
        return True
    
    async def _generate_alert(
        self,
        health: SensorHealth,
        status: SensorHealthStatus,
        issues: list[str],
    ) -> HealthAlert:
        """Generate a health alert."""
        if status == SensorHealthStatus.UNHEALTHY:
            severity = AlertSeverity.CRITICAL
            alert_type = "sensor_unhealthy"
        elif status == SensorHealthStatus.OFFLINE:
            severity = AlertSeverity.ERROR
            alert_type = "sensor_offline"
        else:
            severity = AlertSeverity.WARNING
            alert_type = "sensor_degraded"
        
        message = f"Sensor '{health.sensor_name}' is {status.value}: {', '.join(issues)}"
        
        alert = HealthAlert(
            alert_id=f"alert-{uuid.uuid4().hex[:12]}",
            sensor_id=health.sensor_id,
            sensor_name=health.sensor_name,
            severity=severity,
            alert_type=alert_type,
            message=message,
            details={
                "status": status.value,
                "issues": issues,
                "battery_percent": health.battery_percent,
                "signal_strength_dbm": health.signal_strength_dbm,
            },
        )
        
        self._alerts.append(alert)
        self._metrics.total_alerts += 1
        self._metrics.active_alerts = len([a for a in self._alerts if not a.acknowledged])
        
        await self._notify_callbacks(alert, "alert")
        
        return alert
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
    ) -> bool:
        """Acknowledge a health alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now(timezone.utc)
                self._metrics.active_alerts = len([a for a in self._alerts if not a.acknowledged])
                return True
        return False
    
    async def resolve_alert(
        self,
        alert_id: str,
    ) -> bool:
        """Resolve a health alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now(timezone.utc)
                return True
        return False
    
    def get_sensor_health(self, sensor_id: str) -> Optional[SensorHealth]:
        """Get health status for a sensor."""
        return self._sensor_health.get(sensor_id)
    
    def get_all_sensor_health(self) -> list[SensorHealth]:
        """Get health status for all sensors."""
        return list(self._sensor_health.values())
    
    def get_sensors_by_status(self, status: SensorHealthStatus) -> list[SensorHealth]:
        """Get sensors by health status."""
        return [h for h in self._sensor_health.values() if h.status == status]
    
    def get_unhealthy_sensors(self) -> list[SensorHealth]:
        """Get all unhealthy sensors."""
        return [
            h for h in self._sensor_health.values()
            if h.status in [SensorHealthStatus.UNHEALTHY, SensorHealthStatus.OFFLINE]
        ]
    
    def get_check_history(
        self,
        sensor_id: str,
        limit: int = 100,
    ) -> list[HealthCheckResult]:
        """Get health check history for a sensor."""
        if sensor_id not in self._check_history:
            return []
        
        history = list(self._check_history[sensor_id])
        history.reverse()
        return history[:limit]
    
    def get_active_alerts(self) -> list[HealthAlert]:
        """Get active (unacknowledged) alerts."""
        return [a for a in self._alerts if not a.acknowledged]
    
    def get_recent_alerts(self, limit: int = 100) -> list[HealthAlert]:
        """Get recent alerts."""
        alerts = list(self._alerts)
        alerts.reverse()
        return alerts[:limit]
    
    def get_alerts_for_sensor(self, sensor_id: str) -> list[HealthAlert]:
        """Get alerts for a specific sensor."""
        return [a for a in self._alerts if a.sensor_id == sensor_id]
    
    def calculate_uptime(
        self,
        sensor_id: str,
        hours: int = 24,
    ) -> float:
        """Calculate uptime percentage for a sensor."""
        if sensor_id not in self._check_history:
            return 0.0
        
        history = list(self._check_history[sensor_id])
        if not history:
            return 0.0
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_checks = [c for c in history if c.timestamp >= cutoff]
        
        if not recent_checks:
            return 0.0
        
        healthy_checks = len([
            c for c in recent_checks
            if c.status in [SensorHealthStatus.HEALTHY, SensorHealthStatus.DEGRADED]
        ])
        
        return (healthy_checks / len(recent_checks)) * 100
    
    def get_metrics(self) -> MonitorMetrics:
        """Get monitor metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get monitor status."""
        return {
            "running": self._running,
            "total_sensors": len(self._sensor_health),
            "healthy_count": self._metrics.healthy_count,
            "unhealthy_count": self._metrics.unhealthy_count,
            "active_alerts": self._metrics.active_alerts,
            "metrics": self._metrics.model_dump(),
        }
    
    def get_summary(self) -> dict[str, Any]:
        """Get health summary for all sensors."""
        return {
            "total_sensors": len(self._sensor_health),
            "by_status": self._metrics.sensors_by_status,
            "healthy_percent": (
                self._metrics.healthy_count / len(self._sensor_health) * 100
                if self._sensor_health else 0
            ),
            "avg_uptime_percent": self._metrics.avg_uptime_percent,
            "avg_data_quality": self._metrics.avg_data_quality,
            "active_alerts": self._metrics.active_alerts,
            "critical_sensors": [
                h.sensor_name for h in self._sensor_health.values()
                if h.status == SensorHealthStatus.UNHEALTHY
            ],
            "offline_sensors": [
                h.sensor_name for h in self._sensor_health.values()
                if h.status == SensorHealthStatus.OFFLINE
            ],
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for health events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _update_metrics(self) -> None:
        """Update monitor metrics."""
        status_counts: dict[str, int] = {}
        healthy = 0
        degraded = 0
        unhealthy = 0
        offline = 0
        total_uptime = 0.0
        total_quality = 0.0
        
        for health in self._sensor_health.values():
            status_counts[health.status.value] = status_counts.get(health.status.value, 0) + 1
            
            if health.status == SensorHealthStatus.HEALTHY:
                healthy += 1
            elif health.status == SensorHealthStatus.DEGRADED:
                degraded += 1
            elif health.status == SensorHealthStatus.UNHEALTHY:
                unhealthy += 1
            elif health.status == SensorHealthStatus.OFFLINE:
                offline += 1
            
            total_uptime += health.uptime_percent
            total_quality += health.data_quality_score
        
        n = len(self._sensor_health)
        
        self._metrics.total_sensors = n
        self._metrics.sensors_by_status = status_counts
        self._metrics.healthy_count = healthy
        self._metrics.degraded_count = degraded
        self._metrics.unhealthy_count = unhealthy
        self._metrics.offline_count = offline
        self._metrics.avg_uptime_percent = total_uptime / n if n > 0 else 0.0
        self._metrics.avg_data_quality = total_quality / n if n > 0 else 0.0
    
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
