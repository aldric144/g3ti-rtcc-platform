"""
Phase 38: Workflow Library Tests
Tests for validating all pre-built workflows.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestWorkflowLibrary:
    """Test suite for workflow library validation."""

    def test_all_workflows_imported(self):
        """Test that all workflows are properly imported."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        assert len(ALL_WORKFLOWS) >= 20

    def test_workflow_count(self):
        """Test that we have at least 20 workflows."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        assert len(ALL_WORKFLOWS) >= 20

    def test_all_workflows_have_required_fields(self):
        """Test that all workflows have required fields."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            assert workflow.name is not None
            assert workflow.description is not None
            assert workflow.version is not None
            assert workflow.category is not None
            assert workflow.workflow_id is not None

    def test_all_workflows_have_triggers(self):
        """Test that all workflows have at least one trigger."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            assert len(workflow.triggers) >= 1, f"{workflow.name} has no triggers"

    def test_all_workflows_have_steps(self):
        """Test that all workflows have steps."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            assert len(workflow.steps) >= 1, f"{workflow.name} has no steps"

    def test_all_workflows_have_guardrails(self):
        """Test that all workflows have guardrails defined."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            total_guardrails = (
                len(workflow.guardrails) +
                len(workflow.legal_guardrails) +
                len(workflow.ethical_guardrails)
            )
            assert total_guardrails >= 1, f"{workflow.name} has no guardrails"

    def test_all_workflows_have_valid_priority(self):
        """Test that all workflows have valid priority (1-5)."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            assert 1 <= workflow.priority <= 5, f"{workflow.name} has invalid priority"

    def test_all_workflows_have_timeout(self):
        """Test that all workflows have timeout defined."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            assert workflow.timeout_seconds > 0, f"{workflow.name} has no timeout"


class TestSpecificWorkflows:
    """Test suite for specific workflow validation."""

    def test_gunfire_response_workflow(self):
        """Test Gunfire Response workflow."""
        from app.orchestration.workflows.gunfire_response import GunfireResponseWorkflow
        assert GunfireResponseWorkflow.name == "Gunfire Response"
        assert GunfireResponseWorkflow.priority == 1
        assert len(GunfireResponseWorkflow.steps) >= 8

    def test_school_threat_workflow(self):
        """Test School Threat Response workflow."""
        from app.orchestration.workflows.school_threat import SchoolThreatWorkflow
        assert SchoolThreatWorkflow.name == "School Threat Response"
        assert SchoolThreatWorkflow.priority == 1

    def test_missing_person_workflow(self):
        """Test Missing Person Response workflow."""
        from app.orchestration.workflows.missing_person import MissingPersonWorkflow
        assert MissingPersonWorkflow.name == "Missing Person Response"

    def test_hot_vehicle_workflow(self):
        """Test Hot Vehicle Response workflow."""
        from app.orchestration.workflows.hot_vehicle import HotVehicleWorkflow
        assert HotVehicleWorkflow.name == "Hot Vehicle Response"

    def test_crisis_escalation_workflow(self):
        """Test Crisis Escalation Response workflow."""
        from app.orchestration.workflows.crisis_escalation import CrisisEscalationWorkflow
        assert CrisisEscalationWorkflow.name == "Crisis Escalation Response"

    def test_officer_distress_workflow(self):
        """Test Officer Distress Response workflow."""
        from app.orchestration.workflows.officer_distress import OfficerDistressWorkflow
        assert OfficerDistressWorkflow.name == "Officer Distress Response"
        assert OfficerDistressWorkflow.priority == 1

    def test_active_shooter_workflow(self):
        """Test Active Shooter Response workflow."""
        from app.orchestration.workflows.active_shooter import ActiveShooterWorkflow
        assert ActiveShooterWorkflow.name == "Active Shooter Response"
        assert ActiveShooterWorkflow.priority == 1

    def test_amber_alert_workflow(self):
        """Test Amber Alert Response workflow."""
        from app.orchestration.workflows.amber_alert import AmberAlertWorkflow
        assert AmberAlertWorkflow.name == "Amber Alert Response"
        assert AmberAlertWorkflow.priority == 1

    def test_terrorist_threat_workflow(self):
        """Test Terrorist Threat Response workflow."""
        from app.orchestration.workflows.terrorist_threat import TerroristThreatWorkflow
        assert TerroristThreatWorkflow.name == "Terrorist Threat Response"
        assert TerroristThreatWorkflow.priority == 1

    def test_mental_health_crisis_workflow(self):
        """Test Mental Health Crisis Response workflow."""
        from app.orchestration.workflows.mental_health_crisis import MentalHealthCrisisWorkflow
        assert MentalHealthCrisisWorkflow.name == "Mental Health Crisis Response"


class TestWorkflowSteps:
    """Test suite for workflow step validation."""

    def test_all_steps_have_action_type(self):
        """Test that all workflow steps have action type."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            for step in workflow.steps:
                assert step.action_type is not None, f"Step in {workflow.name} missing action_type"

    def test_all_steps_have_target_subsystem(self):
        """Test that all workflow steps have target subsystem."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            for step in workflow.steps:
                assert step.target_subsystem is not None, f"Step in {workflow.name} missing target_subsystem"

    def test_all_steps_have_timeout(self):
        """Test that all workflow steps have timeout."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            for step in workflow.steps:
                assert step.timeout_seconds > 0, f"Step in {workflow.name} has no timeout"

    def test_all_steps_have_execution_mode(self):
        """Test that all workflow steps have execution mode."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        from app.orchestration.workflow_engine import StepExecutionMode
        for workflow in ALL_WORKFLOWS:
            for step in workflow.steps:
                assert step.execution_mode in [StepExecutionMode.SEQUENTIAL, StepExecutionMode.PARALLEL]
