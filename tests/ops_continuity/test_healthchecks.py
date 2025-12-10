"""
Tests for Health Check Service.

Tests service monitoring, latency detection, uptime tracking,
and health snapshot management.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.ops_continuity.healthchecks import (
    HealthCheckService,
    HealthConfig,
    HealthStatus,
    ServiceType,
    ServiceHealth,
    HealthSnapshot,
)


class TestHealthCheckService:
    """Tests for HealthCheckService class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        service = HealthCheckService()
        assert service.config is not None
        assert service.config.check_interval_seconds == 30
        assert service.config.latency_threshold_ms == 1000
        assert service.config.failure_threshold == 3

    def test_init_custom_config(self):
        """Test initialization with custom configuration."""
        config = HealthConfig(
            check_interval_seconds=60,
            latency_threshold_ms=500,
            failure_threshold=5,
        )
        service = HealthCheckService(config=config)
        assert service.config.check_interval_seconds == 60
        assert service.config.latency_threshold_ms == 500
        assert service.config.failure_threshold == 5

    def test_register_service(self):
        """Test service registration."""
        service = HealthCheckService()
        service.register_service(
            service_id="test-neo4j",
            service_type=ServiceType.NEO4J,
            service_name="Test Neo4j",
            endpoint="bolt://localhost:7687",
        )
        
        services = service.get_services_by_type(ServiceType.NEO4J)
        assert len(services) >= 1
        assert any(s.service_id == "test-neo4j" for s in services)

    def test_unregister_service(self):
        """Test service unregistration."""
        service = HealthCheckService()
        service.register_service(
            service_id="temp-service",
            service_type=ServiceType.REDIS,
            service_name="Temp Redis",
            endpoint="redis://localhost:6379",
        )
        
        service.unregister_service("temp-service")
        services = service.get_services_by_type(ServiceType.REDIS)
        assert not any(s.service_id == "temp-service" for s in services)

    @pytest.mark.asyncio
    async def test_perform_full_check(self):
        """Test performing a full health check."""
        service = HealthCheckService()
        snapshot = await service.perform_full_check()
        
        assert snapshot is not None
        assert isinstance(snapshot, HealthSnapshot)
        assert snapshot.snapshot_id is not None
        assert snapshot.timestamp is not None
        assert snapshot.overall_status in HealthStatus

    def test_get_current_snapshot(self):
        """Test getting current snapshot."""
        service = HealthCheckService()
        snapshot = service.get_current_snapshot()
        
        assert snapshot is not None
        assert isinstance(snapshot, HealthSnapshot)

    def test_get_1h_snapshots(self):
        """Test getting 1-hour snapshots."""
        service = HealthCheckService()
        snapshots = service.get_1h_snapshots()
        
        assert isinstance(snapshots, list)

    def test_get_24h_snapshots(self):
        """Test getting 24-hour snapshots."""
        service = HealthCheckService()
        snapshots = service.get_24h_snapshots()
        
        assert isinstance(snapshots, list)

    def test_get_uptime_report(self):
        """Test getting uptime report."""
        service = HealthCheckService()
        report = service.get_uptime_report(hours=24)
        
        assert isinstance(report, dict)
        assert "period_hours" in report
        assert "services" in report

    def test_get_metrics(self):
        """Test getting health metrics."""
        service = HealthCheckService()
        metrics = service.get_metrics()
        
        assert metrics is not None
        assert hasattr(metrics, "total_checks")
        assert hasattr(metrics, "failed_checks")

    def test_get_status(self):
        """Test getting service status."""
        service = HealthCheckService()
        status = service.get_status()
        
        assert isinstance(status, dict)
        assert "running" in status
        assert "overall_status" in status
        assert "services_count" in status

    def test_register_callback(self):
        """Test callback registration."""
        service = HealthCheckService()
        callback = MagicMock()
        
        service.register_callback(callback)
        assert callback in service._callbacks

    def test_unregister_callback(self):
        """Test callback unregistration."""
        service = HealthCheckService()
        callback = MagicMock()
        
        service.register_callback(callback)
        service.unregister_callback(callback)
        assert callback not in service._callbacks


class TestServiceHealth:
    """Tests for ServiceHealth model."""

    def test_service_health_creation(self):
        """Test ServiceHealth model creation."""
        health = ServiceHealth(
            service_id="test-service",
            service_type=ServiceType.NEO4J,
            service_name="Test Service",
            status=HealthStatus.HEALTHY,
            latency_ms=50.0,
        )
        
        assert health.service_id == "test-service"
        assert health.service_type == ServiceType.NEO4J
        assert health.status == HealthStatus.HEALTHY
        assert health.latency_ms == 50.0

    def test_service_health_with_error(self):
        """Test ServiceHealth with error message."""
        health = ServiceHealth(
            service_id="failed-service",
            service_type=ServiceType.REDIS,
            service_name="Failed Service",
            status=HealthStatus.UNHEALTHY,
            latency_ms=0.0,
            error_message="Connection refused",
            consecutive_failures=3,
        )
        
        assert health.status == HealthStatus.UNHEALTHY
        assert health.error_message == "Connection refused"
        assert health.consecutive_failures == 3


class TestHealthSnapshot:
    """Tests for HealthSnapshot model."""

    def test_snapshot_creation(self):
        """Test HealthSnapshot creation."""
        snapshot = HealthSnapshot(
            snapshot_id="snap-001",
            timestamp=datetime.now(timezone.utc),
            overall_status=HealthStatus.HEALTHY,
            services={},
            healthy_count=10,
            degraded_count=0,
            unhealthy_count=0,
            offline_count=0,
            avg_latency_ms=45.0,
        )
        
        assert snapshot.snapshot_id == "snap-001"
        assert snapshot.overall_status == HealthStatus.HEALTHY
        assert snapshot.healthy_count == 10

    def test_snapshot_with_degraded_services(self):
        """Test snapshot with degraded services."""
        snapshot = HealthSnapshot(
            snapshot_id="snap-002",
            timestamp=datetime.now(timezone.utc),
            overall_status=HealthStatus.DEGRADED,
            services={},
            healthy_count=8,
            degraded_count=2,
            unhealthy_count=0,
            offline_count=0,
            avg_latency_ms=120.0,
        )
        
        assert snapshot.overall_status == HealthStatus.DEGRADED
        assert snapshot.degraded_count == 2


class TestHealthConfig:
    """Tests for HealthConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = HealthConfig()
        
        assert config.check_interval_seconds == 30
        assert config.latency_threshold_ms == 1000
        assert config.failure_threshold == 3
        assert config.snapshot_retention_hours == 24

    def test_custom_config(self):
        """Test custom configuration values."""
        config = HealthConfig(
            check_interval_seconds=15,
            latency_threshold_ms=500,
            failure_threshold=5,
            snapshot_retention_hours=48,
        )
        
        assert config.check_interval_seconds == 15
        assert config.latency_threshold_ms == 500
        assert config.failure_threshold == 5
        assert config.snapshot_retention_hours == 48


class TestServiceType:
    """Tests for ServiceType enum."""

    def test_service_types(self):
        """Test all service types exist."""
        assert ServiceType.NEO4J is not None
        assert ServiceType.ELASTICSEARCH is not None
        assert ServiceType.REDIS is not None
        assert ServiceType.POSTGRES is not None
        assert ServiceType.WEBSOCKET_BROKER is not None
        assert ServiceType.FEDERAL_NDEX is not None
        assert ServiceType.FEDERAL_NCIC is not None
        assert ServiceType.FEDERAL_ETRACE is not None
        assert ServiceType.FEDERAL_DHS_SAR is not None


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_statuses(self):
        """Test all health statuses exist."""
        assert HealthStatus.HEALTHY is not None
        assert HealthStatus.DEGRADED is not None
        assert HealthStatus.UNHEALTHY is not None
        assert HealthStatus.OFFLINE is not None
