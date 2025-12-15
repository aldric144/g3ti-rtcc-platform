"""
Phase 39 Test Suite: Module Integrity Validation
Tests for verifying all 60+ RTCC modules are properly loaded and initialized.
"""

import pytest
from typing import Dict, List, Any


class TestModuleIntegrity:
    """Test suite for module integrity validation."""

    def test_prelaunch_integrator_singleton(self):
        """Test PrelaunchIntegrator singleton pattern."""
        from app.system.prelaunch_integrator import PrelaunchIntegrator

        integrator1 = PrelaunchIntegrator()
        integrator2 = PrelaunchIntegrator()
        assert integrator1 is integrator2

    def test_prelaunch_integrator_initialization(self):
        """Test PrelaunchIntegrator initializes with default modules."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        assert integrator is not None
        assert integrator.get_module_count() > 0

    def test_module_count_minimum(self):
        """Test that at least 60 modules are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        assert integrator.get_module_count() >= 60

    def test_module_categories_present(self):
        """Test that all expected module categories are present."""
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
            assert cat in categories, f"Missing category: {cat}"

    def test_orchestration_modules_present(self):
        """Test that orchestration modules from Phase 38 are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        orchestration_modules = [m for m in modules if m["category"] == "orchestration"]
        assert len(orchestration_modules) >= 6

        module_names = [m["name"] for m in orchestration_modules]
        assert "Orchestration Kernel" in module_names
        assert "Event Router" in module_names
        assert "Workflow Engine" in module_names

    def test_module_validation_structure(self):
        """Test ModuleValidation dataclass structure."""
        from app.system.prelaunch_integrator import ModuleValidation, ModuleStatus

        validation = ModuleValidation(
            module_name="Test Module",
            module_path="app.test",
            category="test",
        )

        assert validation.module_name == "Test Module"
        assert validation.module_path == "app.test"
        assert validation.category == "test"
        assert validation.status == ModuleStatus.OK

    def test_module_validation_to_dict(self):
        """Test ModuleValidation serialization."""
        from app.system.prelaunch_integrator import ModuleValidation

        validation = ModuleValidation(
            module_name="Test Module",
            module_path="app.test",
            category="test",
        )

        data = validation.to_dict()
        assert "module_id" in data
        assert data["module_name"] == "Test Module"
        assert data["module_path"] == "app.test"
        assert data["category"] == "test"
        assert data["status"] == "ok"

    def test_module_status_enum(self):
        """Test ModuleStatus enum values."""
        from app.system.prelaunch_integrator import ModuleStatus

        assert ModuleStatus.OK.value == "ok"
        assert ModuleStatus.WARNING.value == "warning"
        assert ModuleStatus.ERROR.value == "error"
        assert ModuleStatus.NOT_FOUND.value == "not_found"
        assert ModuleStatus.TIMEOUT.value == "timeout"

    @pytest.mark.asyncio
    async def test_validate_single_module(self):
        """Test validating a single module."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        module = {"name": "Test", "path": "app.test", "category": "test"}

        validation = await integrator.validate_module(module)
        assert validation.module_name == "Test"
        assert validation.response_time_ms >= 0

    @pytest.mark.asyncio
    async def test_full_validation_returns_status(self):
        """Test full validation returns PrelaunchStatus."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator, PrelaunchStatus

        integrator = get_prelaunch_integrator()
        status = await integrator.run_full_validation()

        assert isinstance(status, PrelaunchStatus)
        assert len(status.module_validations) > 0

    def test_validation_history_tracking(self):
        """Test that validation history is tracked."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        history = integrator.get_validation_history()

        assert isinstance(history, list)

    def test_statistics_retrieval(self):
        """Test statistics retrieval."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        stats = integrator.get_statistics()

        assert "total_modules" in stats
        assert "total_websockets" in stats
        assert "total_endpoints" in stats
        assert stats["total_modules"] >= 60

    def test_data_lake_modules_present(self):
        """Test Data Lake modules are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        data_modules = [m for m in modules if m["category"] == "data"]
        assert len(data_modules) >= 3

    def test_ai_modules_present(self):
        """Test AI modules are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        ai_modules = [m for m in modules if m["category"] == "ai"]
        assert len(ai_modules) >= 2

    def test_ethics_modules_present(self):
        """Test Ethics modules are registered."""
        from app.system.prelaunch_integrator import get_prelaunch_integrator

        integrator = get_prelaunch_integrator()
        modules = integrator._modules

        ethics_modules = [m for m in modules if m["category"] == "ethics"]
        assert len(ethics_modules) >= 3
