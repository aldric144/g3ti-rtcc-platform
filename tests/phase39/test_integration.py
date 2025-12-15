"""
Phase 39 Test Suite: Integration Tests
Tests for verifying integration between key modules.
"""

import pytest
from typing import Dict, List, Any


class TestIntegration:
    """Test suite for module integration validation."""

    def test_prelaunch_integrator_and_ws_checker_coexist(self):
        """Test PrelaunchIntegrator and WSIntegrationChecker can coexist."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator
        from app.system.ws_integration_checker import get_ws_integration_checker

        integrator = get_prelaunch_integrator()
        checker = get_ws_integration_checker()

        assert integrator is not None
        assert checker is not None

    def test_module_and_websocket_counts_consistent(self):
        """Test module and WebSocket counts are consistent."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator
        from app.system.ws_integration_checker import get_ws_integration_checker

        integrator = get_prelaunch_integrator()
        checker = get_ws_integration_checker()

        assert integrator.get_websocket_count() == checker.get_channel_count()

    @pytest.mark.asyncio
    async def test_full_validation_and_ws_check_together(self):
        """Test running full validation and WS check together."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator
        from app.system.ws_integration_checker import get_ws_integration_checker

        integrator = get_prelaunch_integrator()
        checker = get_ws_integration_checker()

        status = await integrator.run_full_validation()
        ws_status = await checker.run_full_check(include_stress_test=False)

        assert status is not None
        assert ws_status is not None

    def test_orchestration_modules_match_channels(self):
        """Test orchestration modules match WebSocket channels."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator
        from app.system.ws_integration_checker import get_ws_integration_checker

        integrator = get_prelaunch_integrator()
        checker = get_ws_integration_checker()

        orch_modules = [m for m in integrator._modules if m["category"] == "orchestration"]
        orch_channels = [c for c in checker._channels if "/orchestration" in c["path"]]

        assert len(orch_modules) >= 6
        assert len(orch_channels) >= 3

    def test_data_lake_to_prediction_pipeline(self):
        """Test Data Lake to Prediction pipeline modules exist."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        data_modules = [m for m in modules if m["category"] == "data"]
        analytics_modules = [m for m in modules if m["category"] == "analytics"]
        autonomous_modules = [m for m in modules if m["category"] == "autonomous"]

        assert len(data_modules) >= 3, "Data Lake modules missing"
        assert len(analytics_modules) >= 2, "Analytics modules missing"
        assert len(autonomous_modules) >= 4, "Autonomous/Prediction modules missing"

    def test_threat_intel_to_security_pipeline(self):
        """Test Threat Intel to Security pipeline modules exist."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        threat_modules = [m for m in modules if m["category"] == "threat"]
        security_modules = [m for m in modules if m["category"] == "security"]

        assert len(threat_modules) >= 3, "Threat Intel modules missing"
        assert len(security_modules) >= 1, "Security modules missing"

    def test_city_brain_to_governance_pipeline(self):
        """Test City Brain to Governance pipeline modules exist."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        city_modules = [m for m in modules if m["category"] == "city"]
        governance_modules = [m for m in modules if m["category"] == "governance"]
        autonomy_modules = [m for m in modules if m["category"] == "autonomy"]

        assert len(city_modules) >= 2, "City Brain modules missing"
        assert len(governance_modules) >= 2, "Governance modules missing"
        assert len(autonomy_modules) >= 2, "Autonomy modules missing"

    def test_officer_assist_to_ethics_pipeline(self):
        """Test Officer Assist to Ethics pipeline modules exist."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        officer_modules = [m for m in modules if m["category"] == "officer"]
        ethics_modules = [m for m in modules if m["category"] == "ethics"]

        assert len(officer_modules) >= 3, "Officer Assist modules missing"
        assert len(ethics_modules) >= 3, "Ethics modules missing"

    @pytest.mark.asyncio
    async def test_deployment_score_calculation(self):
        """Test deployment score is calculated correctly."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        status = await integrator.run_full_validation()

        assert 0 <= status.deployment_score <= 100
        assert status.deployment_score > 0

    @pytest.mark.asyncio
    async def test_load_factor_calculation(self):
        """Test load factor is calculated correctly."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        status = await integrator.run_full_validation()

        assert 0 <= status.load_factor <= 1.0

    def test_all_categories_have_modules(self):
        """Test all expected categories have at least one module."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        categories = set(m["category"] for m in modules)
        expected_categories = {
            "data", "analytics", "intelligence", "operations",
            "autonomous", "fusion", "threat", "security",
            "robotics", "ai", "emergency", "city",
            "governance", "autonomy", "ethics", "infrastructure",
            "officer", "cyber", "human", "orchestration"
        }

        for cat in expected_categories:
            cat_modules = [m for m in modules if m["category"] == cat]
            assert len(cat_modules) >= 1, f"Category {cat} has no modules"

    def test_critical_websockets_are_marked(self):
        """Test critical WebSocket channels are properly marked."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        critical = checker.get_critical_channels()

        critical_paths = [c["path"] for c in critical]
        expected_critical = [
            "/ws/incidents",
            "/ws/alerts",
            "/ws/dispatch",
            "/ws/emergency",
        ]

        for path in expected_critical:
            assert path in critical_paths, f"Critical channel {path} not marked as critical"

    @pytest.mark.asyncio
    async def test_validation_history_accumulates(self):
        """Test validation history accumulates over multiple runs."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        
        initial_count = len(integrator.get_validation_history())
        await integrator.run_full_validation()
        new_count = len(integrator.get_validation_history())

        assert new_count >= initial_count
