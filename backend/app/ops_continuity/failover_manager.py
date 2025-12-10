"""
Failover Manager Module for G3TI RTCC-UIP Operational Continuity.

Provides automatic detection of failing services, fallback routing,
queue buffering during outages, and health-based service switching.
"""

import asyncio
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from collections import deque
import uuid

from pydantic import BaseModel, Field

from app.ops_continuity.healthchecks import HealthStatus, ServiceType, ServiceHealth


class FailoverMode(str, Enum):
    """Failover operation modes."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    DISABLED = "disabled"


class FailoverState(str, Enum):
    """Current failover state."""
    NORMAL = "normal"
    DEGRADED = "degraded"
    FAILOVER_ACTIVE = "failover_active"
    RECOVERY = "recovery"
    EMERGENCY = "emergency"


class FailoverEvent(BaseModel):
    """Record of a failover event."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    service_type: ServiceType
    service_name: str
    from_state: FailoverState
    to_state: FailoverState
    trigger_reason: str
    fallback_target: Optional[str] = None
    auto_triggered: bool = True
    recovery_time_seconds: Optional[float] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ServiceFallback(BaseModel):
    """Fallback configuration for a service."""
    service_type: ServiceType
    primary_target: str
    fallback_target: str
    fallback_mode: str
    is_active: bool = False
    activated_at: Optional[datetime] = None
    buffered_operations: int = 0


class FailoverConfig(BaseModel):
    """Configuration for failover manager."""
    enabled: bool = True
    mode: FailoverMode = FailoverMode.AUTOMATIC
    detection_threshold_seconds: float = 10.0
    recovery_check_interval_seconds: float = 30.0
    max_buffer_size: int = 10000
    buffer_flush_batch_size: int = 100
    auto_recovery_enabled: bool = True
    emergency_threshold_failures: int = 2

    redis_fallback_enabled: bool = True
    redis_fallback_mode: str = "in_memory"

    investigation_fallback_enabled: bool = True
    investigation_fallback_mode: str = "degraded"

    tactical_fallback_enabled: bool = True
    tactical_fallback_mode: str = "degraded"

    federal_fallback_enabled: bool = True
    federal_fallback_mode: str = "cached"

    escalation_endpoints: list[str] = Field(default_factory=lambda: [
        "rtcc_dashboard", "ops_center", "tactical_dashboard", "command_center"
    ])


class FailoverMetrics(BaseModel):
    """Metrics for failover manager."""
    failovers_triggered: int = 0
    failovers_recovered: int = 0
    current_active_failovers: int = 0
    operations_buffered: int = 0
    operations_flushed: int = 0
    avg_recovery_time_seconds: float = 0.0
    last_failover_event: Optional[datetime] = None
    emergency_events: int = 0


class FailoverManager:
    """
    Manages automatic failover and recovery for RTCC services.

    Detects failing services, activates fallback routing, buffers
    operations during outages, and coordinates recovery.
    """

    def __init__(self, config: Optional[FailoverConfig] = None):
        self.config = config or FailoverConfig()
        self.metrics = FailoverMetrics()
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._state = FailoverState.NORMAL
        self._fallbacks: dict[ServiceType, ServiceFallback] = {}
        self._events: deque[FailoverEvent] = deque(maxlen=1000)
        self._operation_buffer: deque[dict[str, Any]] = deque(maxlen=self.config.max_buffer_size)
        self._callbacks: list[callable] = []
        self._service_states: dict[str, HealthStatus] = {}
        self._initialize_fallbacks()

    def _initialize_fallbacks(self) -> None:
        """Initialize fallback configurations."""
        if self.config.redis_fallback_enabled:
            self._fallbacks[ServiceType.REDIS] = ServiceFallback(
                service_type=ServiceType.REDIS,
                primary_target="redis://primary:6379",
                fallback_target="in_memory_cache",
                fallback_mode=self.config.redis_fallback_mode,
            )

        if self.config.investigation_fallback_enabled:
            self._fallbacks[ServiceType.INVESTIGATIONS_ENGINE] = ServiceFallback(
                service_type=ServiceType.INVESTIGATIONS_ENGINE,
                primary_target="investigations_engine",
                fallback_target="investigations_degraded",
                fallback_mode=self.config.investigation_fallback_mode,
            )

        if self.config.tactical_fallback_enabled:
            self._fallbacks[ServiceType.TACTICAL_ENGINE] = ServiceFallback(
                service_type=ServiceType.TACTICAL_ENGINE,
                primary_target="tactical_engine",
                fallback_target="tactical_degraded",
                fallback_mode=self.config.tactical_fallback_mode,
            )

        if self.config.federal_fallback_enabled:
            self._fallbacks[ServiceType.FEDERAL_ENDPOINT] = ServiceFallback(
                service_type=ServiceType.FEDERAL_ENDPOINT,
                primary_target="federal_live",
                fallback_target="federal_cached",
                fallback_mode=self.config.federal_fallback_mode,
            )

        self._fallbacks[ServiceType.NEO4J] = ServiceFallback(
            service_type=ServiceType.NEO4J,
            primary_target="neo4j://primary:7687",
            fallback_target="neo4j://secondary:7687",
            fallback_mode="secondary",
        )

        self._fallbacks[ServiceType.ELASTICSEARCH] = ServiceFallback(
            service_type=ServiceType.ELASTICSEARCH,
            primary_target="http://es-primary:9200",
            fallback_target="http://es-secondary:9200",
            fallback_mode="secondary",
        )

        self._fallbacks[ServiceType.WEBSOCKET_BROKER] = ServiceFallback(
            service_type=ServiceType.WEBSOCKET_BROKER,
            primary_target="ws://broker-primary",
            fallback_target="ws://broker-secondary",
            fallback_mode="secondary",
        )

    async def start(self) -> None:
        """Start the failover manager."""
        if self._running:
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        """Stop the failover manager."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_recovery()
                await asyncio.sleep(self.config.recovery_check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5.0)

    async def process_health_update(self, service: ServiceHealth) -> None:
        """Process a health update from the health check service."""
        if self.config.mode == FailoverMode.DISABLED:
            return

        previous_status = self._service_states.get(service.service_id)
        self._service_states[service.service_id] = service.status

        if previous_status == service.status:
            return

        if service.status in [HealthStatus.UNHEALTHY, HealthStatus.OFFLINE]:
            await self._handle_service_failure(service)
        elif service.status == HealthStatus.HEALTHY and previous_status in [HealthStatus.UNHEALTHY, HealthStatus.OFFLINE]:
            await self._handle_service_recovery(service)
        elif service.status == HealthStatus.DEGRADED:
            await self._handle_service_degraded(service)

    async def _handle_service_failure(self, service: ServiceHealth) -> None:
        """Handle a service failure."""
        fallback = self._fallbacks.get(service.service_type)
        if not fallback:
            return

        if fallback.is_active:
            return

        event = FailoverEvent(
            service_type=service.service_type,
            service_name=service.service_name,
            from_state=self._state,
            to_state=FailoverState.FAILOVER_ACTIVE,
            trigger_reason=service.error_message or "Service unhealthy",
            fallback_target=fallback.fallback_target,
            auto_triggered=self.config.mode == FailoverMode.AUTOMATIC,
        )

        if self.config.mode == FailoverMode.AUTOMATIC:
            await self._activate_failover(fallback, event)

        self._events.append(event)
        self.metrics.failovers_triggered += 1
        self.metrics.last_failover_event = datetime.now(timezone.utc)

        await self._update_state()
        await self._notify_callbacks(event)

    async def _handle_service_recovery(self, service: ServiceHealth) -> None:
        """Handle a service recovery."""
        fallback = self._fallbacks.get(service.service_type)
        if not fallback or not fallback.is_active:
            return

        if not self.config.auto_recovery_enabled:
            return

        event = FailoverEvent(
            service_type=service.service_type,
            service_name=service.service_name,
            from_state=self._state,
            to_state=FailoverState.RECOVERY,
            trigger_reason="Service recovered",
            fallback_target=fallback.primary_target,
            auto_triggered=True,
        )

        if fallback.activated_at:
            event.recovery_time_seconds = (
                datetime.now(timezone.utc) - fallback.activated_at
            ).total_seconds()

        await self._deactivate_failover(fallback, event)

        self._events.append(event)
        self.metrics.failovers_recovered += 1

        self._update_avg_recovery_time(event.recovery_time_seconds)

        await self._update_state()
        await self._notify_callbacks(event)

    async def _handle_service_degraded(self, service: ServiceHealth) -> None:
        """Handle a degraded service."""
        if self._state == FailoverState.NORMAL:
            self._state = FailoverState.DEGRADED

    async def _activate_failover(self, fallback: ServiceFallback, event: FailoverEvent) -> None:
        """Activate failover for a service."""
        fallback.is_active = True
        fallback.activated_at = datetime.now(timezone.utc)
        self.metrics.current_active_failovers += 1

    async def _deactivate_failover(self, fallback: ServiceFallback, event: FailoverEvent) -> None:
        """Deactivate failover for a service."""
        fallback.is_active = False
        fallback.activated_at = None
        self.metrics.current_active_failovers = max(0, self.metrics.current_active_failovers - 1)

        await self._flush_buffer(fallback.service_type)

    async def _check_recovery(self) -> None:
        """Check if any failed services have recovered."""
        pass

    async def _update_state(self) -> None:
        """Update overall failover state."""
        active_failovers = sum(1 for f in self._fallbacks.values() if f.is_active)

        if active_failovers == 0:
            self._state = FailoverState.NORMAL
        elif active_failovers >= self.config.emergency_threshold_failures:
            self._state = FailoverState.EMERGENCY
            self.metrics.emergency_events += 1
        else:
            self._state = FailoverState.FAILOVER_ACTIVE

    def _update_avg_recovery_time(self, recovery_time: Optional[float]) -> None:
        """Update average recovery time."""
        if recovery_time is None:
            return

        if self.metrics.failovers_recovered == 1:
            self.metrics.avg_recovery_time_seconds = recovery_time
        else:
            self.metrics.avg_recovery_time_seconds = (
                self.metrics.avg_recovery_time_seconds * 0.9 + recovery_time * 0.1
            )

    async def _notify_callbacks(self, event: FailoverEvent) -> None:
        """Notify registered callbacks of failover event."""
        for callback in self._callbacks:
            try:
                await callback(event)
            except Exception:
                pass

    async def buffer_operation(self, service_type: ServiceType, operation: dict[str, Any]) -> bool:
        """Buffer an operation during failover."""
        fallback = self._fallbacks.get(service_type)
        if not fallback or not fallback.is_active:
            return False

        if len(self._operation_buffer) >= self.config.max_buffer_size:
            return False

        operation["_buffered_at"] = datetime.now(timezone.utc).isoformat()
        operation["_service_type"] = service_type.value
        self._operation_buffer.append(operation)
        fallback.buffered_operations += 1
        self.metrics.operations_buffered += 1

        return True

    async def _flush_buffer(self, service_type: ServiceType) -> int:
        """Flush buffered operations for a service."""
        flushed = 0
        remaining = deque()

        while self._operation_buffer:
            operation = self._operation_buffer.popleft()
            if operation.get("_service_type") == service_type.value:
                flushed += 1
            else:
                remaining.append(operation)

        self._operation_buffer = remaining
        self.metrics.operations_flushed += flushed

        fallback = self._fallbacks.get(service_type)
        if fallback:
            fallback.buffered_operations = 0

        return flushed

    async def manual_failover(self, service_type: ServiceType, reason: str) -> FailoverEvent:
        """Manually trigger failover for a service."""
        fallback = self._fallbacks.get(service_type)
        if not fallback:
            raise ValueError(f"No fallback configured for {service_type}")

        event = FailoverEvent(
            service_type=service_type,
            service_name=service_type.value,
            from_state=self._state,
            to_state=FailoverState.FAILOVER_ACTIVE,
            trigger_reason=reason,
            fallback_target=fallback.fallback_target,
            auto_triggered=False,
        )

        await self._activate_failover(fallback, event)
        self._events.append(event)
        self.metrics.failovers_triggered += 1
        self.metrics.last_failover_event = datetime.now(timezone.utc)

        await self._update_state()
        await self._notify_callbacks(event)

        return event

    async def manual_recovery(self, service_type: ServiceType, reason: str) -> FailoverEvent:
        """Manually trigger recovery for a service."""
        fallback = self._fallbacks.get(service_type)
        if not fallback or not fallback.is_active:
            raise ValueError(f"No active failover for {service_type}")

        event = FailoverEvent(
            service_type=service_type,
            service_name=service_type.value,
            from_state=self._state,
            to_state=FailoverState.RECOVERY,
            trigger_reason=reason,
            fallback_target=fallback.primary_target,
            auto_triggered=False,
        )

        if fallback.activated_at:
            event.recovery_time_seconds = (
                datetime.now(timezone.utc) - fallback.activated_at
            ).total_seconds()

        await self._deactivate_failover(fallback, event)
        self._events.append(event)
        self.metrics.failovers_recovered += 1

        await self._update_state()
        await self._notify_callbacks(event)

        return event

    def register_callback(self, callback: callable) -> None:
        """Register a callback for failover events."""
        self._callbacks.append(callback)

    def get_fallback_status(self, service_type: ServiceType) -> Optional[ServiceFallback]:
        """Get fallback status for a service."""
        return self._fallbacks.get(service_type)

    def get_all_fallback_status(self) -> dict[str, ServiceFallback]:
        """Get all fallback statuses."""
        return {st.value: fb for st, fb in self._fallbacks.items()}

    def get_recent_events(self, limit: int = 100) -> list[FailoverEvent]:
        """Get recent failover events."""
        return list(self._events)[-limit:]

    def get_status(self) -> dict[str, Any]:
        """Get failover manager status."""
        return {
            "running": self._running,
            "state": self._state.value,
            "mode": self.config.mode.value,
            "active_failovers": self.metrics.current_active_failovers,
            "buffered_operations": len(self._operation_buffer),
            "fallbacks": {
                st.value: {
                    "is_active": fb.is_active,
                    "fallback_target": fb.fallback_target,
                    "fallback_mode": fb.fallback_mode,
                    "buffered_operations": fb.buffered_operations,
                }
                for st, fb in self._fallbacks.items()
            },
            "metrics": self.metrics.model_dump(),
        }

    def get_metrics(self) -> FailoverMetrics:
        """Get failover metrics."""
        return self.metrics
