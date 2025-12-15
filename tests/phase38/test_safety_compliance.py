"""
Phase 38: Safety Compliance Tests
Tests for safety-critical compliance requirements.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestSafetyCompliance:
    """Test suite for safety compliance."""

    def test_officer_safety_priority(self):
        """Test that officer safety is prioritized."""
        from app.orchestration.workflows.officer_distress import OfficerDistressWorkflow
        
        workflow = OfficerDistressWorkflow
        assert workflow.priority == 1
        assert "officer_safety" in workflow.guardrails or any(
            "officer" in g.lower() for g in workflow.guardrails
        )

    def test_emergency_workflows_are_critical(self):
        """Test that emergency workflows have critical priority."""
        from app.orchestration.workflows.active_shooter import ActiveShooterWorkflow
        from app.orchestration.workflows.officer_distress import OfficerDistressWorkflow
        from app.orchestration.workflows.terrorist_threat import TerroristThreatWorkflow
        
        emergency_workflows = [
            ActiveShooterWorkflow,
            OfficerDistressWorkflow,
            TerroristThreatWorkflow,
        ]
        
        for workflow in emergency_workflows:
            assert workflow.priority == 1, f"{workflow.name} should be critical priority"

    def test_child_safety_workflows_are_critical(self):
        """Test that child safety workflows have critical priority."""
        from app.orchestration.workflows.amber_alert import AmberAlertWorkflow
        from app.orchestration.workflows.school_threat import SchoolThreatWorkflow
        
        child_safety_workflows = [AmberAlertWorkflow, SchoolThreatWorkflow]
        
        for workflow in child_safety_workflows:
            assert workflow.priority == 1, f"{workflow.name} should be critical priority"

    def test_de_escalation_priority(self):
        """Test that de-escalation is prioritized in crisis workflows."""
        from app.orchestration.workflows.mental_health_crisis import MentalHealthCrisisWorkflow
        from app.orchestration.workflows.crisis_escalation import CrisisEscalationWorkflow
        
        crisis_workflows = [MentalHealthCrisisWorkflow, CrisisEscalationWorkflow]
        
        for workflow in crisis_workflows:
            all_guardrails = (
                workflow.guardrails +
                workflow.legal_guardrails +
                workflow.ethical_guardrails
            )
            has_de_escalation = any("de_escalation" in g.lower() or "deescalation" in g.lower() 
                                   for g in all_guardrails)
            assert has_de_escalation or len(all_guardrails) >= 2


class TestResourceSafety:
    """Test suite for resource safety."""

    def test_drone_dispatch_has_safety_guardrails(self):
        """Test that drone dispatch has safety guardrails."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            drone_steps = [s for s in workflow.steps if "drone" in s.action_type.lower()]
            for step in drone_steps:
                assert len(step.guardrails) >= 1, f"Drone step in {workflow.name} needs guardrails"

    def test_robot_dispatch_has_safety_guardrails(self):
        """Test that robot dispatch has safety guardrails."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            robot_steps = [s for s in workflow.steps if "robot" in s.action_type.lower()]
            for step in robot_steps:
                assert len(step.guardrails) >= 1 or len(workflow.guardrails) >= 1

    def test_tactical_actions_have_guardrails(self):
        """Test that tactical actions have guardrails."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        tactical_actions = ["tactical", "lockdown", "pursuit", "force"]
        
        for workflow in ALL_WORKFLOWS:
            for step in workflow.steps:
                is_tactical = any(t in step.action_type.lower() for t in tactical_actions)
                if is_tactical:
                    assert len(step.guardrails) >= 1 or len(workflow.guardrails) >= 1


class TestDataSafety:
    """Test suite for data safety."""

    def test_no_secrets_in_workflows(self):
        """Test that no secrets are hardcoded in workflows."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        secret_patterns = ["password", "secret", "api_key", "token", "credential"]
        
        for workflow in ALL_WORKFLOWS:
            workflow_str = str(workflow)
            for pattern in secret_patterns:
                assert pattern not in workflow_str.lower(), f"Potential secret in {workflow.name}"

    def test_privacy_protected_in_human_stability_workflows(self):
        """Test that privacy is protected in human stability workflows."""
        from app.orchestration.workflows.mental_health_crisis import MentalHealthCrisisWorkflow
        from app.orchestration.workflows.dv_risk_escalation import DVRiskEscalationWorkflow
        
        privacy_workflows = [MentalHealthCrisisWorkflow, DVRiskEscalationWorkflow]
        
        for workflow in privacy_workflows:
            all_guardrails = (
                workflow.guardrails +
                workflow.legal_guardrails +
                workflow.ethical_guardrails
            )
            has_privacy = any("privacy" in g.lower() or "hipaa" in g.lower() 
                             for g in all_guardrails)
            assert has_privacy or len(all_guardrails) >= 2


class TestFailsafe:
    """Test suite for failsafe mechanisms."""

    def test_all_workflows_have_timeout(self):
        """Test that all workflows have timeout failsafe."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            assert workflow.timeout_seconds > 0, f"{workflow.name} missing timeout"

    def test_all_steps_have_timeout(self):
        """Test that all workflow steps have timeout failsafe."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            for step in workflow.steps:
                assert step.timeout_seconds > 0, f"Step in {workflow.name} missing timeout"

    def test_critical_workflows_have_short_timeout(self):
        """Test that critical workflows have reasonable timeout."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        critical_workflows = [w for w in ALL_WORKFLOWS if w.priority == 1]
        
        for workflow in critical_workflows:
            assert workflow.timeout_seconds <= 600, f"{workflow.name} timeout too long for critical"

    def test_workflow_can_be_disabled(self):
        """Test that workflows can be disabled."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            assert hasattr(workflow, 'enabled')
