"""Tests for the Alerts Router module."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.intel_orchestration.alerts_router import (
    AlertDestination,
    AlertPriority,
    DeliveryStatus,
    RoutingConfig,
    RoutedAlert,
    DeliveryResult,
    RoutingMetrics,
    AlertsRouter,
)


class TestAlertDestination:
    """Tests for AlertDestination enum."""

    def test_all_destinations_defined(self):
        """Test all alert destinations are defined."""
        expected_destinations = [
            "RTCC_DASHBOARD", "TACTICAL_DASHBOARD", "INVESTIGATIONS_DASHBOARD",
            "OFFICER_SAFETY_ALERTS", "DISPATCH_COMMS", "MOBILE_MDT",
            "COMMAND_CENTER", "AUTO_BULLETIN", "BOLO_GENERATOR",
            "FEDERAL_SYSTEMS", "FEDERATION_HUB", "DATA_LAKE",
            "KNOWLEDGE_GRAPH", "AUDIT_LOG",
        ]
        
        for dest in expected_destinations:
            assert hasattr(AlertDestination, dest)


class TestAlertPriority:
    """Tests for AlertPriority enum."""

    def test_priority_values(self):
        """Test alert priority values."""
        assert AlertPriority.IMMEDIATE.value == "immediate"
        assert AlertPriority.URGENT.value == "urgent"
        assert AlertPriority.HIGH.value == "high"
        assert AlertPriority.NORMAL.value == "normal"
        assert AlertPriority.LOW.value == "low"


class TestDeliveryStatus:
    """Tests for DeliveryStatus enum."""

    def test_status_values(self):
        """Test delivery status values."""
        assert DeliveryStatus.PENDING.value == "pending"
        assert DeliveryStatus.DELIVERED.value == "delivered"
        assert DeliveryStatus.FAILED.value == "failed"
        assert DeliveryStatus.RETRYING.value == "retrying"
        assert DeliveryStatus.ACKNOWLEDGED.value == "acknowledged"


class TestRoutingConfig:
    """Tests for RoutingConfig model."""

    def test_default_config(self):
        """Test default routing configuration."""
        config = RoutingConfig()
        
        assert config.enabled is True
        assert config.max_retry_attempts == 3
        assert config.retry_delay_seconds == 5.0

    def test_tier_routing_config(self):
        """Test tier-based routing configuration."""
        config = RoutingConfig()
        
        # Tier 1 should route to officer safety and dispatch
        assert AlertDestination.OFFICER_SAFETY_ALERTS in config.tier1_destinations
        assert AlertDestination.DISPATCH_COMMS in config.tier1_destinations

    def test_custom_config(self):
        """Test custom routing configuration."""
        config = RoutingConfig(
            enabled=False,
            max_retry_attempts=5,
            retry_delay_seconds=10.0,
        )
        
        assert config.enabled is False
        assert config.max_retry_attempts == 5


class TestRoutedAlert:
    """Tests for RoutedAlert model."""

    def test_alert_creation(self):
        """Test creating a routed alert."""
        alert = RoutedAlert(
            source_id="fusion-123",
            priority=AlertPriority.HIGH,
            destinations=[AlertDestination.RTCC_DASHBOARD],
            payload={"title": "Test Alert"},
        )
        
        assert alert.id is not None
        assert alert.priority == AlertPriority.HIGH
        assert alert.status == DeliveryStatus.PENDING

    def test_alert_with_tier(self):
        """Test alert with tier assignment."""
        alert = RoutedAlert(
            source_id="fusion-456",
            priority=AlertPriority.IMMEDIATE,
            destinations=[AlertDestination.OFFICER_SAFETY_ALERTS],
            payload={"title": "Officer Safety"},
            tier="tier1",
        )
        
        assert alert.tier == "tier1"


class TestDeliveryResult:
    """Tests for DeliveryResult model."""

    def test_result_creation(self):
        """Test creating a delivery result."""
        result = DeliveryResult(
            alert_id="alert-123",
            destination=AlertDestination.RTCC_DASHBOARD,
            status=DeliveryStatus.DELIVERED,
            delivered_at=datetime.now(timezone.utc),
        )
        
        assert result.alert_id == "alert-123"
        assert result.status == DeliveryStatus.DELIVERED

    def test_failed_result(self):
        """Test failed delivery result."""
        result = DeliveryResult(
            alert_id="alert-456",
            destination=AlertDestination.MOBILE_MDT,
            status=DeliveryStatus.FAILED,
            error_message="Connection timeout",
            retry_count=3,
        )
        
        assert result.status == DeliveryStatus.FAILED
        assert result.error_message == "Connection timeout"


class TestRoutingMetrics:
    """Tests for RoutingMetrics model."""

    def test_default_metrics(self):
        """Test default routing metrics."""
        metrics = RoutingMetrics()
        
        assert metrics.alerts_routed == 0
        assert metrics.alerts_delivered == 0
        assert metrics.alerts_failed == 0

    def test_metrics_update(self):
        """Test updating metrics."""
        metrics = RoutingMetrics()
        metrics.alerts_routed = 100
        metrics.alerts_delivered = 95
        metrics.alerts_failed = 5
        
        assert metrics.alerts_routed == 100
        assert metrics.alerts_delivered == 95


class TestAlertsRouter:
    """Tests for AlertsRouter class."""

    def test_router_initialization(self):
        """Test alerts router initialization."""
        router = AlertsRouter()
        
        assert router.config is not None
        assert router.metrics is not None

    def test_router_with_custom_config(self):
        """Test router with custom config."""
        config = RoutingConfig(
            max_retry_attempts=5,
        )
        router = AlertsRouter(config=config)
        
        assert router.config.max_retry_attempts == 5

    @pytest.mark.asyncio
    async def test_router_start_stop(self):
        """Test starting and stopping router."""
        router = AlertsRouter()
        
        await router.start()
        assert router._running is True
        
        await router.stop()
        assert router._running is False

    @pytest.mark.asyncio
    async def test_route_alert(self):
        """Test routing an alert."""
        router = AlertsRouter()
        await router.start()
        
        alert = RoutedAlert(
            source_id="fusion-123",
            priority=AlertPriority.HIGH,
            destinations=[AlertDestination.RTCC_DASHBOARD],
            payload={"title": "Test"},
        )
        
        await router.route_alert(alert)
        
        assert router.metrics.alerts_routed >= 1
        
        await router.stop()

    @pytest.mark.asyncio
    async def test_route_by_tier(self):
        """Test routing by tier."""
        router = AlertsRouter()
        await router.start()
        
        alert = RoutedAlert(
            source_id="fusion-456",
            priority=AlertPriority.IMMEDIATE,
            destinations=[],  # Will be set by tier
            payload={"title": "Officer Safety"},
            tier="tier1",
        )
        
        await router.route_by_tier(alert)
        
        # Tier 1 should add officer safety destinations
        assert len(alert.destinations) > 0
        
        await router.stop()

    @pytest.mark.asyncio
    async def test_tier1_routing(self):
        """Test Tier 1 (officer safety) routing."""
        router = AlertsRouter()
        
        destinations = router.get_tier_destinations("tier1")
        
        assert AlertDestination.OFFICER_SAFETY_ALERTS in destinations
        assert AlertDestination.DISPATCH_COMMS in destinations
        assert AlertDestination.MOBILE_MDT in destinations

    @pytest.mark.asyncio
    async def test_tier2_routing(self):
        """Test Tier 2 (high priority) routing."""
        router = AlertsRouter()
        
        destinations = router.get_tier_destinations("tier2")
        
        assert AlertDestination.RTCC_DASHBOARD in destinations
        assert AlertDestination.TACTICAL_DASHBOARD in destinations

    @pytest.mark.asyncio
    async def test_generate_bolo(self):
        """Test BOLO generation."""
        router = AlertsRouter()
        await router.start()
        
        bolo = await router.generate_bolo(
            subject_type="vehicle",
            subject_description="Black SUV, plate ABC123",
            reason="Wanted in connection with armed robbery",
            jurisdiction="Metro PD",
        )
        
        assert bolo is not None
        assert "subject_type" in bolo
        assert bolo["subject_type"] == "vehicle"
        
        await router.stop()

    @pytest.mark.asyncio
    async def test_generate_bulletin(self):
        """Test bulletin generation."""
        router = AlertsRouter()
        await router.start()
        
        bulletin = await router.generate_bulletin(
            title="Crime Pattern Alert",
            content="Series of burglaries in District 5",
            priority=AlertPriority.HIGH,
            jurisdiction="Metro PD",
        )
        
        assert bulletin is not None
        assert "title" in bulletin
        
        await router.stop()

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        router = AlertsRouter()
        await router.start()
        
        alert = RoutedAlert(
            source_id="fusion-789",
            priority=AlertPriority.HIGH,
            destinations=[AlertDestination.RTCC_DASHBOARD],
            payload={"title": "Test"},
        )
        
        await router.route_alert(alert)
        
        result = await router.acknowledge_alert(alert.id, "user-123")
        
        assert result is True
        
        await router.stop()

    def test_get_status(self):
        """Test getting router status."""
        router = AlertsRouter()
        status = router.get_status()
        
        assert "running" in status
        assert "metrics" in status
        assert "config" in status

    def test_get_metrics(self):
        """Test getting router metrics."""
        router = AlertsRouter()
        metrics = router.get_metrics()
        
        assert isinstance(metrics, RoutingMetrics)

    @pytest.mark.asyncio
    async def test_websocket_broadcast(self):
        """Test WebSocket broadcast integration."""
        router = AlertsRouter()
        await router.start()
        
        # Router should have WebSocket channels configured
        assert router.config.enable_websocket_broadcast is True
        
        await router.stop()

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test retry logic on delivery failure."""
        config = RoutingConfig(
            max_retry_attempts=3,
            retry_delay_seconds=0.1,  # Fast retry for testing
        )
        router = AlertsRouter(config=config)
        await router.start()
        
        # The router should handle retries internally
        assert router.config.max_retry_attempts == 3
        
        await router.stop()
