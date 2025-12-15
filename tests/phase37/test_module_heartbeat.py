"""
Phase 37: Module Heartbeat Checker Tests
Tests for the Module Heartbeat Checker functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from backend.app.master_orchestration.module_heartbeat import (
    ModuleHeartbeatChecker,
    ModuleStatus,
    ModuleHealth,
    HeartbeatResult,
)


class TestModuleHeartbeatChecker:
    """Test suite for ModuleHeartbeatChecker."""

    def setup_method(self):
        """Reset singleton for each test."""
        ModuleHeartbeatChecker._instance = None
        self.checker = ModuleHeartbeatChecker()

    def test_singleton_pattern(self):
        """Test that ModuleHeartbeatChecker follows singleton pattern."""
        checker1 = ModuleHeartbeatChecker()
        checker2 = ModuleHeartbeatChecker()
        assert checker1 is checker2

    def test_pre_registered_modules(self):
        """Test that all RTCC modules are pre-registered."""
        all_health = self.checker.get_all_module_health()
        assert len(all_health) >= 33

    def test_register_module(self):
        """Test module registration."""
        self.checker.register_module(
            module_id="test-module",
            module_name="Test Module",
            version="1.0.0",
            dependencies=["core"],
            endpoints_total=5,
        )

        health = self.checker.get_module_health("test-module")
        assert health is not None
        assert health.module_name == "Test Module"
        assert health.version == "1.0.0"

    def test_unregister_module(self):
        """Test module unregistration."""
        self.checker.register_module(
            module_id="temp-module",
            module_name="Temporary Module",
        )

        result = self.checker.unregister_module("temp-module")
        assert result is True

        health = self.checker.get_module_health("temp-module")
        assert health is None

    def test_update_heartbeat(self):
        """Test heartbeat update."""
        self.checker.register_module(
            module_id="heartbeat-test",
            module_name="Heartbeat Test Module",
        )

        health = self.checker.update_heartbeat(
            module_id="heartbeat-test",
            response_time_ms=45.5,
            cpu_usage=25.0,
            memory_usage=512.0,
            error_count=0,
            warning_count=2,
            endpoints_healthy=5,
            endpoints_total=5,
            websocket_connections=10,
        )

        assert health is not None
        assert health.response_time_ms == 45.5
        assert health.cpu_usage == 25.0
        assert health.status == ModuleStatus.HEALTHY

    def test_module_status_transitions(self):
        """Test module status transitions based on metrics."""
        self.checker.register_module(
            module_id="status-test",
            module_name="Status Test Module",
            endpoints_total=10,
        )

        self.checker.update_heartbeat(
            module_id="status-test",
            response_time_ms=50.0,
            error_count=0,
            endpoints_healthy=10,
            endpoints_total=10,
        )
        health = self.checker.get_module_health("status-test")
        assert health.status == ModuleStatus.HEALTHY

        self.checker.update_heartbeat(
            module_id="status-test",
            response_time_ms=150.0,
            error_count=3,
            endpoints_healthy=7,
            endpoints_total=10,
        )
        health = self.checker.get_module_health("status-test")
        assert health.status in [ModuleStatus.DEGRADED, ModuleStatus.HEALTHY]

    def test_perform_heartbeat_check_sync(self):
        """Test synchronous heartbeat check."""
        result = self.checker.perform_heartbeat_check_sync()

        assert isinstance(result, HeartbeatResult)
        assert result.modules_checked > 0
        assert result.overall_status is not None

    @pytest.mark.asyncio
    async def test_perform_heartbeat_check_async(self):
        """Test asynchronous heartbeat check."""
        result = await self.checker.perform_heartbeat_check()

        assert isinstance(result, HeartbeatResult)
        assert result.modules_checked > 0

    def test_get_modules_by_status(self):
        """Test filtering modules by status."""
        healthy = self.checker.get_modules_by_status(ModuleStatus.HEALTHY)
        assert all(m.status == ModuleStatus.HEALTHY for m in healthy)

    def test_get_healthy_modules(self):
        """Test retrieving healthy modules."""
        healthy = self.checker.get_healthy_modules()
        assert all(m.status == ModuleStatus.HEALTHY for m in healthy)

    def test_get_unhealthy_modules(self):
        """Test retrieving unhealthy modules."""
        unhealthy = self.checker.get_unhealthy_modules()
        assert all(
            m.status in [ModuleStatus.UNHEALTHY, ModuleStatus.OFFLINE]
            for m in unhealthy
        )

    def test_get_degraded_modules(self):
        """Test retrieving degraded modules."""
        degraded = self.checker.get_degraded_modules()
        assert all(m.status == ModuleStatus.DEGRADED for m in degraded)

    def test_get_heartbeat_history(self):
        """Test heartbeat history retrieval."""
        history = self.checker.get_heartbeat_history(limit=10)
        assert isinstance(history, list)

    def test_get_module_dependencies(self):
        """Test module dependency retrieval."""
        self.checker.register_module(
            module_id="dep-test",
            module_name="Dependency Test",
            dependencies=["core", "database"],
        )

        deps = self.checker.get_module_dependencies("dep-test")
        assert "core" in deps
        assert "database" in deps

    def test_get_dependent_modules(self):
        """Test finding modules that depend on a given module."""
        self.checker.register_module(
            module_id="base-module",
            module_name="Base Module",
        )
        self.checker.register_module(
            module_id="dependent-module",
            module_name="Dependent Module",
            dependencies=["base-module"],
        )

        dependents = self.checker.get_dependent_modules("base-module")
        assert "dependent-module" in dependents

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.checker.get_statistics()

        assert "total_modules" in stats
        assert "healthy_count" in stats
        assert "degraded_count" in stats
        assert "unhealthy_count" in stats
        assert "offline_count" in stats

    def test_get_system_overview(self):
        """Test system overview retrieval."""
        overview = self.checker.get_system_overview()

        assert "total_modules" in overview
        assert "status_summary" in overview
        assert "overall_health" in overview

    def test_module_health_to_dict(self):
        """Test ModuleHealth serialization."""
        health = ModuleHealth(
            module_id="test-module",
            module_name="Test Module",
            status=ModuleStatus.HEALTHY,
            response_time_ms=50.0,
            cpu_usage=25.0,
            memory_usage=512.0,
            error_count=0,
            warning_count=0,
        )

        health_dict = health.to_dict()

        assert health_dict["module_id"] == "test-module"
        assert health_dict["status"] == "healthy"
        assert health_dict["response_time_ms"] == 50.0

    def test_heartbeat_result_to_dict(self):
        """Test HeartbeatResult serialization."""
        result = HeartbeatResult(
            modules_checked=33,
            modules_healthy=30,
            modules_degraded=2,
            modules_unhealthy=1,
            modules_offline=0,
            overall_status=ModuleStatus.HEALTHY,
            duration_ms=150.0,
        )

        result_dict = result.to_dict()

        assert result_dict["modules_checked"] == 33
        assert result_dict["overall_status"] == "healthy"

    def test_module_status_enum(self):
        """Test all module statuses are defined."""
        assert len(ModuleStatus) == 5
        assert ModuleStatus.HEALTHY.value == "healthy"
        assert ModuleStatus.DEGRADED.value == "degraded"
        assert ModuleStatus.UNHEALTHY.value == "unhealthy"
        assert ModuleStatus.OFFLINE.value == "offline"
        assert ModuleStatus.UNKNOWN.value == "unknown"
