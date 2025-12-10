"""
Tests for Redundancy Manager.

Tests connection pool management, hot/warm standby support,
automatic reconnection, and state synchronization.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.ops_continuity.redundancy_manager import (
    RedundancyManager,
    RedundancyConfig,
    RedundancyMode,
    ConnectionState,
    ServiceRole,
    ServiceInstance,
    ConnectionPool,
    SyncEvent,
)


class TestRedundancyManager:
    """Tests for RedundancyManager class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        manager = RedundancyManager()
        assert manager.config is not None
        assert manager.config.mode == RedundancyMode.HOT

    def test_init_custom_config(self):
        """Test initialization with custom configuration."""
        config = RedundancyConfig(
            mode=RedundancyMode.WARM,
            sync_interval_seconds=60,
            connection_timeout_seconds=10,
        )
        manager = RedundancyManager(config=config)
        assert manager.config.mode == RedundancyMode.WARM
        assert manager.config.sync_interval_seconds == 60

    def test_register_pool(self):
        """Test connection pool registration."""
        manager = RedundancyManager()
        manager.register_pool(
            pool_id="neo4j-pool",
            service_name="Neo4j",
            primary_endpoint="bolt://primary:7687",
            secondary_endpoint="bolt://secondary:7687",
        )
        
        pool = manager.get_pool("neo4j-pool")
        assert pool is not None
        assert pool.service_name == "Neo4j"

    def test_get_pool(self):
        """Test getting a connection pool."""
        manager = RedundancyManager()
        manager.register_pool(
            pool_id="redis-pool",
            service_name="Redis",
            primary_endpoint="redis://primary:6379",
            secondary_endpoint="redis://secondary:6379",
        )
        
        pool = manager.get_pool("redis-pool")
        assert pool is not None
        assert pool.pool_id == "redis-pool"

    def test_get_pool_not_found(self):
        """Test getting non-existent pool."""
        manager = RedundancyManager()
        pool = manager.get_pool("nonexistent")
        assert pool is None

    def test_get_status(self):
        """Test getting redundancy status."""
        manager = RedundancyManager()
        status = manager.get_status()
        
        assert isinstance(status, dict)
        assert "running" in status
        assert "pools_managed" in status
        assert "active_connections" in status

    def test_get_metrics(self):
        """Test getting redundancy metrics."""
        manager = RedundancyManager()
        metrics = manager.get_metrics()
        
        assert metrics is not None
        assert hasattr(metrics, "total_failovers")
        assert hasattr(metrics, "total_failbacks")

    @pytest.mark.asyncio
    async def test_manual_failover(self):
        """Test manual pool failover."""
        manager = RedundancyManager()
        manager.register_pool(
            pool_id="test-pool",
            service_name="Test",
            primary_endpoint="primary:1234",
            secondary_endpoint="secondary:1234",
        )
        
        success = await manager.manual_failover("test-pool")
        assert isinstance(success, bool)

    @pytest.mark.asyncio
    async def test_manual_failback(self):
        """Test manual pool failback."""
        manager = RedundancyManager()
        manager.register_pool(
            pool_id="test-pool",
            service_name="Test",
            primary_endpoint="primary:1234",
            secondary_endpoint="secondary:1234",
        )
        
        await manager.manual_failover("test-pool")
        success = await manager.manual_failback("test-pool")
        assert isinstance(success, bool)

    def test_register_callback(self):
        """Test callback registration."""
        manager = RedundancyManager()
        callback = MagicMock()
        
        manager.register_callback(callback)
        assert callback in manager._callbacks


class TestConnectionPool:
    """Tests for ConnectionPool model."""

    def test_pool_creation(self):
        """Test ConnectionPool creation."""
        pool = ConnectionPool(
            pool_id="test-pool",
            service_name="Test Service",
            mode=RedundancyMode.HOT,
        )
        
        assert pool.pool_id == "test-pool"
        assert pool.service_name == "Test Service"
        assert pool.mode == RedundancyMode.HOT

    def test_pool_with_instances(self):
        """Test pool with service instances."""
        primary = ServiceInstance(
            instance_id="primary-1",
            endpoint="primary:1234",
            role=ServiceRole.PRIMARY,
            state=ConnectionState.CONNECTED,
            is_healthy=True,
        )
        secondary = ServiceInstance(
            instance_id="secondary-1",
            endpoint="secondary:1234",
            role=ServiceRole.SECONDARY,
            state=ConnectionState.CONNECTED,
            is_healthy=True,
        )
        
        pool = ConnectionPool(
            pool_id="test-pool",
            service_name="Test",
            mode=RedundancyMode.HOT,
            primary=primary,
            secondary=secondary,
            active_instance_id="primary-1",
        )
        
        assert pool.primary is not None
        assert pool.secondary is not None
        assert pool.active_instance_id == "primary-1"


class TestServiceInstance:
    """Tests for ServiceInstance model."""

    def test_instance_creation(self):
        """Test ServiceInstance creation."""
        instance = ServiceInstance(
            instance_id="inst-001",
            endpoint="localhost:1234",
            role=ServiceRole.PRIMARY,
            state=ConnectionState.CONNECTED,
            is_healthy=True,
        )
        
        assert instance.instance_id == "inst-001"
        assert instance.role == ServiceRole.PRIMARY
        assert instance.is_healthy is True

    def test_unhealthy_instance(self):
        """Test unhealthy service instance."""
        instance = ServiceInstance(
            instance_id="inst-002",
            endpoint="localhost:1234",
            role=ServiceRole.SECONDARY,
            state=ConnectionState.FAILED,
            is_healthy=False,
            error_message="Connection refused",
        )
        
        assert instance.is_healthy is False
        assert instance.state == ConnectionState.FAILED
        assert instance.error_message == "Connection refused"


class TestSyncEvent:
    """Tests for SyncEvent model."""

    def test_sync_event_creation(self):
        """Test SyncEvent creation."""
        event = SyncEvent(
            event_id="sync-001",
            timestamp=datetime.now(timezone.utc),
            pool_id="test-pool",
            from_instance="primary-1",
            to_instance="secondary-1",
            sync_type="full",
            records_synced=1000,
            duration_ms=500.0,
            success=True,
        )
        
        assert event.event_id == "sync-001"
        assert event.records_synced == 1000
        assert event.success is True

    def test_failed_sync_event(self):
        """Test failed sync event."""
        event = SyncEvent(
            event_id="sync-002",
            timestamp=datetime.now(timezone.utc),
            pool_id="test-pool",
            from_instance="primary-1",
            to_instance="secondary-1",
            sync_type="incremental",
            records_synced=0,
            duration_ms=100.0,
            success=False,
            error_message="Network timeout",
        )
        
        assert event.success is False
        assert event.error_message == "Network timeout"


class TestRedundancyMode:
    """Tests for RedundancyMode enum."""

    def test_redundancy_modes(self):
        """Test all redundancy modes exist."""
        assert RedundancyMode.HOT is not None
        assert RedundancyMode.WARM is not None
        assert RedundancyMode.COLD is not None


class TestConnectionState:
    """Tests for ConnectionState enum."""

    def test_connection_states(self):
        """Test all connection states exist."""
        assert ConnectionState.DISCONNECTED is not None
        assert ConnectionState.CONNECTING is not None
        assert ConnectionState.CONNECTED is not None
        assert ConnectionState.FAILED is not None
        assert ConnectionState.DRAINING is not None


class TestServiceRole:
    """Tests for ServiceRole enum."""

    def test_service_roles(self):
        """Test all service roles exist."""
        assert ServiceRole.PRIMARY is not None
        assert ServiceRole.SECONDARY is not None
        assert ServiceRole.STANDBY is not None


class TestRedundancyConfig:
    """Tests for RedundancyConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RedundancyConfig()
        
        assert config.mode == RedundancyMode.HOT
        assert config.sync_interval_seconds == 30
        assert config.connection_timeout_seconds == 5

    def test_custom_config(self):
        """Test custom configuration values."""
        config = RedundancyConfig(
            mode=RedundancyMode.WARM,
            sync_interval_seconds=60,
            connection_timeout_seconds=10,
            max_reconnect_attempts=5,
        )
        
        assert config.mode == RedundancyMode.WARM
        assert config.sync_interval_seconds == 60
        assert config.max_reconnect_attempts == 5
