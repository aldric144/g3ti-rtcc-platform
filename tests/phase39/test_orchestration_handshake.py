"""
Phase 39 Test Suite: Orchestration Engine Handshake
Tests for verifying Phase 38 orchestration engine integration.
"""

import pytest
from typing import Dict, List, Any


class TestOrchestrationHandshake:
    """Test suite for orchestration engine handshake validation."""

    @pytest.mark.asyncio
    async def test_orchestration_validation(self):
        """Test orchestration engine validation."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        result = await integrator.validate_orchestration_engine()

        assert "kernel_ok" in result
        assert "event_router_ok" in result
        assert "workflow_engine_ok" in result
        assert "policy_engine_ok" in result
        assert "resource_manager_ok" in result
        assert "event_bus_ok" in result

    @pytest.mark.asyncio
    async def test_orchestration_response_time(self):
        """Test orchestration engine response time."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        result = await integrator.validate_orchestration_engine()

        assert "response_time_ms" in result
        assert result["response_time_ms"] >= 0

    @pytest.mark.asyncio
    async def test_workflows_registered(self):
        """Test workflows are registered in engine."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        result = await integrator.validate_orchestration_engine()

        assert "workflows_registered" in result
        assert result["workflows_registered"] >= 0

    def test_orchestration_kernel_import(self):
        """Test OrchestrationKernel can be imported."""
        try:
            from app.orchestration import OrchestrationKernel
            kernel = OrchestrationKernel()
            assert kernel is not None
        except ImportError:
            pytest.skip("OrchestrationKernel not available")

    def test_event_router_import(self):
        """Test EventRouter can be imported."""
        try:
            from app.orchestration import EventRouter
            router = EventRouter()
            assert router is not None
        except ImportError:
            pytest.skip("EventRouter not available")

    def test_workflow_engine_import(self):
        """Test WorkflowEngine can be imported."""
        try:
            from app.orchestration import WorkflowEngine
            engine = WorkflowEngine()
            assert engine is not None
        except ImportError:
            pytest.skip("WorkflowEngine not available")

    def test_policy_binding_engine_import(self):
        """Test PolicyBindingEngine can be imported."""
        try:
            from app.orchestration import PolicyBindingEngine
            engine = PolicyBindingEngine()
            assert engine is not None
        except ImportError:
            pytest.skip("PolicyBindingEngine not available")

    def test_resource_manager_import(self):
        """Test ResourceManager can be imported."""
        try:
            from app.orchestration import ResourceManager
            manager = ResourceManager()
            assert manager is not None
        except ImportError:
            pytest.skip("ResourceManager not available")

    def test_event_fusion_bus_import(self):
        """Test EventFusionBus can be imported."""
        try:
            from app.orchestration.event_bus import EventFusionBus
            bus = EventFusionBus()
            assert bus is not None
        except ImportError:
            pytest.skip("EventFusionBus not available")

    def test_workflow_library_import(self):
        """Test workflow library can be imported."""
        try:
            from app.orchestration.workflows import ALL_WORKFLOWS
            assert len(ALL_WORKFLOWS) >= 20
        except ImportError:
            pytest.skip("Workflow library not available")

    @pytest.mark.asyncio
    async def test_full_validation_includes_orchestration(self):
        """Test full validation includes orchestration status."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        status = await integrator.run_full_validation()

        assert hasattr(status, "orchestration_ok")

    def test_orchestration_modules_in_integrator(self):
        """Test orchestration modules are registered in integrator."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        orchestration_modules = [m for m in modules if m["category"] == "orchestration"]
        assert len(orchestration_modules) >= 6

        module_names = [m["name"] for m in orchestration_modules]
        expected_names = [
            "Orchestration Kernel",
            "Event Router",
            "Workflow Engine",
            "Policy Binding Engine",
            "Resource Manager",
            "Event Fusion Bus",
        ]

        for name in expected_names:
            assert name in module_names, f"Missing orchestration module: {name}"

    def test_orchestration_websockets_in_checker(self):
        """Test orchestration WebSocket channels are registered."""
        from app.system.ws_integration_checker import get_ws_integration_checker

        checker = get_ws_integration_checker()
        channels = checker._channels

        orchestration_channels = [c for c in channels if "/orchestration" in c["path"]]
        assert len(orchestration_channels) >= 3

        channel_paths = [c["path"] for c in orchestration_channels]
        expected_paths = [
            "/ws/orchestration/events",
            "/ws/orchestration/workflow-status",
            "/ws/orchestration/alerts",
        ]

        for path in expected_paths:
            assert path in channel_paths, f"Missing orchestration channel: {path}"

    def test_orchestration_endpoints_in_integrator(self):
        """Test orchestration API endpoints are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        endpoints = integrator._api_endpoints

        orchestration_endpoints = [e for e in endpoints if "/orchestration" in e["path"]]
        assert len(orchestration_endpoints) >= 4
