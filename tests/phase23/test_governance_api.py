"""
Phase 23: Governance API Endpoint Tests
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestGovernanceDecisionEndpoints:
    """Tests for governance decision API endpoints."""

    def test_create_decisions_request_model(self):
        """Test decision request model structure."""
        from app.api.city_governance.router import DecisionRequest

        request = DecisionRequest(
            city_state={
                "zones": {"downtown": {"crime_rate": 0.85}},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        assert request.city_state is not None
        assert "zones" in request.city_state

    def test_approval_request_model(self):
        """Test approval request model structure."""
        from app.api.city_governance.router import DecisionApprovalRequest

        request = DecisionApprovalRequest(
            approved_by="admin",
            notes="Approved for testing",
        )
        assert request.approved_by == "admin"
        assert request.notes == "Approved for testing"

    def test_rejection_request_model(self):
        """Test rejection request model structure."""
        from app.api.city_governance.router import DecisionRejectionRequest

        request = DecisionRejectionRequest(
            rejected_by="admin",
            reason="Not applicable",
        )
        assert request.rejected_by == "admin"
        assert request.reason == "Not applicable"


class TestResourceOptimizationEndpoints:
    """Tests for resource optimization API endpoints."""

    def test_optimization_request_model(self):
        """Test optimization request model structure."""
        from app.api.city_governance.router import OptimizationRequest

        request = OptimizationRequest(
            algorithm="linear_programming",
            objectives=["maximize_coverage", "minimize_response_time"],
            resource_types=["police_unit", "fire_unit"],
        )
        assert request.algorithm == "linear_programming"
        assert len(request.objectives) == 2
        assert len(request.resource_types) == 2

    def test_route_optimization_request_model(self):
        """Test route optimization request model structure."""
        from app.api.city_governance.router import RouteOptimizationRequest

        request = RouteOptimizationRequest(
            unit_id="unit-101",
            waypoints=[(26.7753, -80.0583), (26.7800, -80.0550)],
            priorities=[1, 2],
        )
        assert request.unit_id == "unit-101"
        assert len(request.waypoints) == 2
        assert len(request.priorities) == 2

    def test_maintenance_schedule_request_model(self):
        """Test maintenance schedule request model structure."""
        from app.api.city_governance.router import MaintenanceScheduleRequest

        request = MaintenanceScheduleRequest(
            tasks=[
                {
                    "task_id": "task-001",
                    "asset_id": "vehicle-001",
                    "asset_name": "Patrol Car 101",
                    "task_type": "oil_change",
                    "priority": 2,
                    "estimated_duration_hours": 2,
                },
            ]
        )
        assert len(request.tasks) == 1


class TestScenarioEndpoints:
    """Tests for scenario API endpoints."""

    def test_scenario_create_request_model(self):
        """Test scenario create request model structure."""
        from app.api.city_governance.router import ScenarioCreateRequest

        request = ScenarioCreateRequest(
            scenario_type="hurricane",
            name="Test Hurricane",
            description="Test hurricane scenario",
            variables=[
                {"name": "wind_speed", "min_value": 50, "max_value": 150, "default_value": 100},
            ],
            duration_hours=48,
            affected_zones=["downtown", "singer_island"],
            created_by="test_user",
        )
        assert request.scenario_type == "hurricane"
        assert request.name == "Test Hurricane"
        assert len(request.variables) == 1
        assert len(request.affected_zones) == 2

    def test_scenario_from_template_request_model(self):
        """Test scenario from template request model structure."""
        from app.api.city_governance.router import ScenarioFromTemplateRequest

        request = ScenarioFromTemplateRequest(
            template_id="template-hurricane-cat3",
            variable_overrides={"wind_speed": 125},
            created_by="test_user",
        )
        assert request.template_id == "template-hurricane-cat3"
        assert request.variable_overrides["wind_speed"] == 125

    def test_variable_update_request_model(self):
        """Test variable update request model structure."""
        from app.api.city_governance.router import VariableUpdateRequest

        request = VariableUpdateRequest(
            variable_name="wind_speed",
            new_value=130,
        )
        assert request.variable_name == "wind_speed"
        assert request.new_value == 130


class TestKPIEndpoints:
    """Tests for KPI API endpoints."""

    def test_report_generate_request_model(self):
        """Test report generate request model structure."""
        from app.api.city_governance.router import ReportGenerateRequest

        request = ReportGenerateRequest(period="daily")
        assert request.period == "daily"

        request = ReportGenerateRequest(period="weekly")
        assert request.period == "weekly"


class TestAuditLogger:
    """Tests for audit logger."""

    def test_log_entry(self):
        """Test audit log entry creation."""
        from app.api.city_governance.router import AuditLogger

        AuditLogger.log(
            action="test_action",
            resource_type="test_resource",
            resource_id="test-123",
            user_id="test_user",
            details={"key": "value"},
        )

        logs = AuditLogger.get_logs(limit=1)
        assert len(logs) >= 1

        latest = logs[-1]
        assert latest["action"] == "test_action"
        assert latest["resource_type"] == "test_resource"
        assert latest["resource_id"] == "test-123"
        assert latest["user_id"] == "test_user"

    def test_log_limit(self):
        """Test audit log limit."""
        from app.api.city_governance.router import AuditLogger

        for i in range(5):
            AuditLogger.log(
                action=f"action_{i}",
                resource_type="test",
                resource_id=f"id-{i}",
            )

        logs = AuditLogger.get_logs(limit=3)
        assert len(logs) <= 3


class TestRouterConfiguration:
    """Tests for router configuration."""

    def test_router_prefix(self):
        """Test router has correct prefix."""
        from app.api.city_governance.router import router

        assert router.prefix == "/governance"

    def test_router_tags(self):
        """Test router has correct tags."""
        from app.api.city_governance.router import router

        assert "City Governance" in router.tags


class TestEndpointImports:
    """Tests for endpoint imports and dependencies."""

    def test_governance_engine_import(self):
        """Test governance engine can be imported."""
        from app.city_governance import get_governance_engine

        engine = get_governance_engine()
        assert engine is not None

    def test_resource_optimizer_import(self):
        """Test resource optimizer can be imported."""
        from app.city_governance.resource_optimizer import get_resource_optimizer

        optimizer = get_resource_optimizer()
        assert optimizer is not None

    def test_scenario_simulator_import(self):
        """Test scenario simulator can be imported."""
        from app.city_governance.scenario_simulator import get_scenario_simulator

        simulator = get_scenario_simulator()
        assert simulator is not None

    def test_kpi_engine_import(self):
        """Test KPI engine can be imported."""
        from app.city_governance.kpi_engine import get_kpi_engine

        engine = get_kpi_engine()
        assert engine is not None
