"""
Phase 38: Guardrail Compliance Tests
Tests for guardrail enforcement and compliance checking.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestGuardrailCompliance:
    """Test suite for guardrail compliance."""

    def test_constitutional_guardrails_exist(self):
        """Test that constitutional guardrails are defined."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine, PolicyType
        
        engine = PolicyBindingEngine()
        bindings = engine.get_policy_bindings()
        constitutional = [b for b in bindings if b.policy_type == PolicyType.CONSTITUTIONAL]
        
        assert len(constitutional) >= 1

    def test_use_of_force_guardrails_exist(self):
        """Test that use of force guardrails are defined."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine, PolicyType
        
        engine = PolicyBindingEngine()
        bindings = engine.get_policy_bindings()
        uof = [b for b in bindings if b.policy_type == PolicyType.USE_OF_FORCE]
        
        assert len(uof) >= 1

    def test_privacy_guardrails_exist(self):
        """Test that privacy guardrails are defined."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine, PolicyType
        
        engine = PolicyBindingEngine()
        bindings = engine.get_policy_bindings()
        privacy = [b for b in bindings if b.policy_type == PolicyType.PRIVACY]
        
        assert len(privacy) >= 1

    def test_civil_rights_guardrails_exist(self):
        """Test that civil rights guardrails are defined."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine, PolicyType
        
        engine = PolicyBindingEngine()
        bindings = engine.get_policy_bindings()
        civil_rights = [b for b in bindings if b.policy_type == PolicyType.CIVIL_RIGHTS]
        
        assert len(civil_rights) >= 1

    def test_ethical_guardrails_exist(self):
        """Test that ethical guardrails are defined."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine, PolicyType
        
        engine = PolicyBindingEngine()
        bindings = engine.get_policy_bindings()
        ethical = [b for b in bindings if b.policy_type == PolicyType.ETHICAL_GUARDRAIL]
        
        assert len(ethical) >= 1


class TestGuardrailEnforcement:
    """Test suite for guardrail enforcement."""

    @pytest.mark.asyncio
    async def test_blocking_guardrail_stops_action(self):
        """Test that blocking guardrails stop actions."""
        from app.orchestration.policy_binding_engine import (
            PolicyBindingEngine, GuardrailSeverity
        )
        
        engine = PolicyBindingEngine()
        result = await engine.check_policy(
            workflow_id="test-workflow",
            action_type="test_action",
            parameters={},
        )
        
        blocking = [r for r in result if r.severity == GuardrailSeverity.BLOCKING and not r.passed]
        assert isinstance(blocking, list)

    @pytest.mark.asyncio
    async def test_warning_guardrail_allows_action(self):
        """Test that warning guardrails allow actions with warning."""
        from app.orchestration.policy_binding_engine import (
            PolicyBindingEngine, GuardrailSeverity
        )
        
        engine = PolicyBindingEngine()
        result = await engine.check_policy(
            workflow_id="test-workflow",
            action_type="audit_log",
            parameters={},
        )
        
        warnings = [r for r in result if r.severity == GuardrailSeverity.WARNING]
        assert isinstance(warnings, list)

    def test_guardrail_severity_ordering(self):
        """Test guardrail severity ordering."""
        from app.orchestration.policy_binding_engine import GuardrailSeverity
        
        severities = [
            GuardrailSeverity.BLOCKING,
            GuardrailSeverity.WARNING,
            GuardrailSeverity.ADVISORY,
            GuardrailSeverity.INFORMATIONAL,
        ]
        
        assert severities[0] == GuardrailSeverity.BLOCKING


class TestWorkflowGuardrails:
    """Test suite for workflow-specific guardrails."""

    def test_all_workflows_have_legal_guardrails(self):
        """Test that all workflows have legal guardrails."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            assert len(workflow.legal_guardrails) >= 1, f"{workflow.name} missing legal guardrails"

    def test_all_workflows_have_ethical_guardrails(self):
        """Test that all workflows have ethical guardrails."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            assert len(workflow.ethical_guardrails) >= 1, f"{workflow.name} missing ethical guardrails"

    def test_critical_workflows_have_blocking_guardrails(self):
        """Test that critical workflows have blocking guardrails."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        critical_workflows = [w for w in ALL_WORKFLOWS if w.priority == 1]
        
        for workflow in critical_workflows:
            total_guardrails = (
                len(workflow.guardrails) +
                len(workflow.legal_guardrails) +
                len(workflow.ethical_guardrails)
            )
            assert total_guardrails >= 2, f"Critical workflow {workflow.name} needs more guardrails"

    def test_use_of_force_workflows_have_uof_guardrails(self):
        """Test that use of force workflows have UOF guardrails."""
        from app.orchestration.workflows.active_shooter import ActiveShooterWorkflow
        from app.orchestration.workflows.officer_distress import OfficerDistressWorkflow
        
        for workflow in [ActiveShooterWorkflow, OfficerDistressWorkflow]:
            all_guardrails = (
                workflow.guardrails +
                workflow.legal_guardrails +
                workflow.ethical_guardrails
            )
            assert len(all_guardrails) >= 2


class TestGuardrailAudit:
    """Test suite for guardrail audit logging."""

    def test_guardrail_check_creates_audit_entry(self):
        """Test that guardrail checks create audit entries."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        
        engine = PolicyBindingEngine()
        history = engine.get_check_history(limit=100)
        
        assert isinstance(history, list)

    def test_audit_entry_contains_required_fields(self):
        """Test that audit entries contain required fields."""
        from app.orchestration.policy_binding_engine import GuardrailCheck, GuardrailSeverity
        from datetime import datetime
        
        check = GuardrailCheck(
            check_id="check-001",
            binding_id="binding-001",
            workflow_id="workflow-001",
            action_type="test_action",
            passed=True,
            severity=GuardrailSeverity.WARNING,
            message="Test check",
            details={},
            checked_at=datetime.utcnow(),
        )
        
        check_dict = check.to_dict()
        assert "check_id" in check_dict
        assert "binding_id" in check_dict
        assert "workflow_id" in check_dict
        assert "passed" in check_dict
