"""
Phase 39 Test Suite: API Schema Validation
Tests for verifying all API endpoints return valid schemas.
"""

import pytest
from typing import Dict, List, Any


class TestAPISchemaValidation:
    """Test suite for API schema validation."""

    def test_prelaunch_integrator_endpoints_registered(self):
        """Test that API endpoints are registered in integrator."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        assert integrator.get_endpoint_count() > 0

    def test_endpoint_count_minimum(self):
        """Test that at least 40 endpoints are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        assert integrator.get_endpoint_count() >= 40

    def test_api_validation_structure(self):
        """Test APIValidation dataclass structure."""
        from app.system.prelaunch_integrator import APIValidation, ModuleStatus

        validation = APIValidation(
            endpoint_path="/api/test",
            method="GET",
        )

        assert validation.endpoint_path == "/api/test"
        assert validation.method == "GET"
        assert validation.status == ModuleStatus.OK

    def test_api_validation_to_dict(self):
        """Test APIValidation serialization."""
        from app.system.prelaunch_integrator import APIValidation

        validation = APIValidation(
            endpoint_path="/api/test",
            method="GET",
            schema_valid=True,
        )

        data = validation.to_dict()
        assert "endpoint_id" in data
        assert data["endpoint_path"] == "/api/test"
        assert data["method"] == "GET"
        assert data["schema_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_single_endpoint(self):
        """Test validating a single endpoint."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoint = {"path": "/api/test", "method": "GET"}

        validation = await integrator.validate_endpoint(endpoint)
        assert validation.endpoint_path == "/api/test"
        assert validation.response_time_ms >= 0

    def test_health_endpoint_registered(self):
        """Test health endpoint is registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        health_endpoints = [e for e in endpoints if "/health" in e["path"]]
        assert len(health_endpoints) >= 1

    def test_orchestration_endpoints_registered(self):
        """Test orchestration endpoints are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        orchestration_endpoints = [e for e in endpoints if "/orchestration" in e["path"]]
        assert len(orchestration_endpoints) >= 4

    def test_prelaunch_endpoint_registered(self):
        """Test prelaunch endpoint is registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        prelaunch_endpoints = [e for e in endpoints if "/prelaunch" in e["path"]]
        assert len(prelaunch_endpoints) >= 1

    def test_all_endpoints_have_method(self):
        """Test all endpoints have a method defined."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        for endpoint in endpoints:
            assert "method" in endpoint
            assert endpoint["method"] in ["GET", "POST", "PUT", "DELETE", "PATCH"]

    def test_all_endpoints_have_path(self):
        """Test all endpoints have a path defined."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        for endpoint in endpoints:
            assert "path" in endpoint
            assert endpoint["path"].startswith("/api")

    @pytest.mark.asyncio
    async def test_full_validation_includes_endpoints(self):
        """Test full validation includes endpoint validations."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        status = await integrator.run_full_validation()

        assert len(status.api_validations) > 0
        assert hasattr(status, "endpoints_ok")

    def test_data_lake_endpoints_registered(self):
        """Test Data Lake endpoints are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        data_lake_endpoints = [e for e in endpoints if "/data-lake" in e["path"]]
        assert len(data_lake_endpoints) >= 1

    def test_incidents_endpoint_registered(self):
        """Test incidents endpoint is registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        incident_endpoints = [e for e in endpoints if "/incidents" in e["path"]]
        assert len(incident_endpoints) >= 1

    def test_alerts_endpoint_registered(self):
        """Test alerts endpoint is registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        alert_endpoints = [e for e in endpoints if "/alerts" in e["path"]]
        assert len(alert_endpoints) >= 1

    def test_drones_endpoint_registered(self):
        """Test drones endpoint is registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        drone_endpoints = [e for e in endpoints if "/drones" in e["path"]]
        assert len(drone_endpoints) >= 1

    def test_robots_endpoint_registered(self):
        """Test robots endpoint is registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        robot_endpoints = [e for e in endpoints if "/robots" in e["path"]]
        assert len(robot_endpoints) >= 1
