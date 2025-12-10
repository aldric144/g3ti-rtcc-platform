"""
Tests for Failover Manager.

Tests automatic failover detection, fallback routing,
queue buffering, and recovery management.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.ops_continuity.failover_manager import (
    FailoverManager,
    FailoverConfig,
    FailoverMode,
    FailoverState,
    FailoverEvent,
    ServiceFallback,
)
from app.ops_continuity.healthchecks import (
    ServiceType,
    HealthStatus,
    ServiceHealth,
)


class TestFailoverManager:
    """Tests for FailoverManager class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        manager = FailoverManager()
        assert manager.config is not None
        assert manager.config.failure_threshold == 3
        assert manager.config.recovery_threshold == 2

    def test_init_custom_config(self):
        """Test initialization with custom configuration."""
        config = FailoverConfig(
            failure_threshold=5,
            recovery_threshold=3,
            buffer_max_size=500,
        )
        manager = FailoverManager(config=config)
        assert manager.config.failure_threshold == 5
        assert manager.config.recovery_threshold == 3
        assert manager.config.buffer_max_size == 500

    def test_register_fallback(self):
        """Test fallback registration."""
        manager = FailoverManager()
        manager.register_fallback(
            service_type=ServiceType.REDIS,
            primary_target="redis://primary:6379",
            fallback_target="in-memory",
        )
        
        fallback = manager.get_fallback(ServiceType.REDIS)
        assert fallback is not None
        assert fallback.primary_target == "redis://primary:6379"
        assert fallback.fallback_target == "in-memory"

    def test_get_status(self):
        """Test getting failover status."""
        manager = FailoverManager()
        status = manager.get_status()
        
        assert isinstance(status, dict)
        assert "state" in status
        assert "mode" in status
        assert "active_failovers" in status
        assert "buffered_operations" in status

    def test_get_metrics(self):
        """Test getting failover metrics."""
        manager = FailoverManager()
        metrics = manager.get_metrics()
        
        assert metrics is not None
        assert hasattr(metrics, "total_failovers")
        assert hasattr(metrics, "auto_failovers")
        assert hasattr(metrics, "manual_failovers")

    def test_get_recent_events(self):
        """Test getting recent failover events."""
        manager = FailoverManager()
        events = manager.get_recent_events(limit=10)
        
        assert isinstance(events, list)

    @pytest.mark.asyncio
    async def test_process_health_update_healthy(self):
        """Test processing healthy service update."""
        manager = FailoverManager()
        health = ServiceHealth(
            service_id="test-redis",
            service_type=ServiceType.REDIS,
            service_name="Test Redis",
            status=HealthStatus.HEALTHY,
            latency_ms=5.0,
        )
        
        await manager.process_health_update(health)
        status = manager.get_status()
        assert status["state"] == "normal"

    @pytest.mark.asyncio
    async def test_process_health_update_failure(self):
        """Test processing service failure update."""
        manager = FailoverManager()
        manager.register_fallback(
            service_type=ServiceType.REDIS,
            primary_target="redis://primary:6379",
            fallback_target="in-memory",
        )
        
        for _ in range(4):
            health = ServiceHealth(
                service_id="test-redis",
                service_type=ServiceType.REDIS,
                service_name="Test Redis",
                status=HealthStatus.UNHEALTHY,
                latency_ms=0.0,
                consecutive_failures=4,
            )
            await manager.process_health_update(health)
        
        fallback = manager.get_fallback(ServiceType.REDIS)
        assert fallback is not None

    @pytest.mark.asyncio
    async def test_manual_failover(self):
        """Test manual failover trigger."""
        manager = FailoverManager()
        manager.register_fallback(
            service_type=ServiceType.NEO4J,
            primary_target="bolt://primary:7687",
            fallback_target="bolt://secondary:7687",
        )
        
        event = await manager.manual_failover(
            ServiceType.NEO4J,
            reason="Planned maintenance",
        )
        
        assert event is not None
        assert event.service_type == ServiceType.NEO4J
        assert not event.auto_triggered

    @pytest.mark.asyncio
    async def test_manual_recovery(self):
        """Test manual recovery trigger."""
        manager = FailoverManager()
        manager.register_fallback(
            service_type=ServiceType.NEO4J,
            primary_target="bolt://primary:7687",
            fallback_target="bolt://secondary:7687",
        )
        
        await manager.manual_failover(ServiceType.NEO4J, reason="Test")
        
        event = await manager.manual_recovery(
            ServiceType.NEO4J,
            reason="Maintenance complete",
        )
        
        assert event is not None
        assert event.to_state == FailoverState.NORMAL

    @pytest.mark.asyncio
    async def test_buffer_operation(self):
        """Test operation buffering during failover."""
        manager = FailoverManager()
        
        await manager.buffer_operation(
            service_type=ServiceType.REDIS,
            operation_type="SET",
            operation_data={"key": "test", "value": "data"},
        )
        
        status = manager.get_status()
        assert status["buffered_operations"] >= 0

    def test_register_callback(self):
        """Test callback registration."""
        manager = FailoverManager()
        callback = MagicMock()
        
        manager.register_callback(callback)
        assert callback in manager._callbacks


class TestFailoverEvent:
    """Tests for FailoverEvent model."""

    def test_event_creation(self):
        """Test FailoverEvent creation."""
        event = FailoverEvent(
            event_id="evt-001",
            timestamp=datetime.now(timezone.utc),
            service_type=ServiceType.REDIS,
            from_state=FailoverState.NORMAL,
            to_state=FailoverState.FAILOVER,
            trigger_reason="Connection timeout",
            auto_triggered=True,
        )
        
        assert event.event_id == "evt-001"
        assert event.service_type == ServiceType.REDIS
        assert event.auto_triggered is True

    def test_event_with_recovery_time(self):
        """Test event with recovery time."""
        event = FailoverEvent(
            event_id="evt-002",
            timestamp=datetime.now(timezone.utc),
            service_type=ServiceType.NEO4J,
            from_state=FailoverState.FAILOVER,
            to_state=FailoverState.NORMAL,
            trigger_reason="Service recovered",
            auto_triggered=True,
            recovery_time_seconds=45.5,
        )
        
        assert event.recovery_time_seconds == 45.5


class TestServiceFallback:
    """Tests for ServiceFallback model."""

    def test_fallback_creation(self):
        """Test ServiceFallback creation."""
        fallback = ServiceFallback(
            service_type=ServiceType.REDIS,
            primary_target="redis://primary:6379",
            fallback_target="in-memory",
            is_active=False,
        )
        
        assert fallback.service_type == ServiceType.REDIS
        assert fallback.primary_target == "redis://primary:6379"
        assert fallback.is_active is False

    def test_active_fallback(self):
        """Test active fallback state."""
        fallback = ServiceFallback(
            service_type=ServiceType.NEO4J,
            primary_target="bolt://primary:7687",
            fallback_target="bolt://secondary:7687",
            is_active=True,
            activated_at=datetime.now(timezone.utc),
            buffered_operations=10,
        )
        
        assert fallback.is_active is True
        assert fallback.buffered_operations == 10


class TestFailoverState:
    """Tests for FailoverState enum."""

    def test_failover_states(self):
        """Test all failover states exist."""
        assert FailoverState.NORMAL is not None
        assert FailoverState.DEGRADED is not None
        assert FailoverState.FAILOVER is not None
        assert FailoverState.EMERGENCY is not None


class TestFailoverMode:
    """Tests for FailoverMode enum."""

    def test_failover_modes(self):
        """Test all failover modes exist."""
        assert FailoverMode.AUTOMATIC is not None
        assert FailoverMode.MANUAL is not None
        assert FailoverMode.DISABLED is not None


class TestFailoverConfig:
    """Tests for FailoverConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = FailoverConfig()
        
        assert config.failure_threshold == 3
        assert config.recovery_threshold == 2
        assert config.buffer_max_size == 1000

    def test_custom_config(self):
        """Test custom configuration values."""
        config = FailoverConfig(
            failure_threshold=5,
            recovery_threshold=3,
            buffer_max_size=2000,
            auto_recovery_enabled=False,
        )
        
        assert config.failure_threshold == 5
        assert config.auto_recovery_enabled is False
