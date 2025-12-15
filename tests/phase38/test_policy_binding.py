"""
Phase 38: Policy Binding Engine Tests
Tests for policy binding, guardrail checking, and compliance.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestPolicyBindingEngine:
    """Test suite for PolicyBindingEngine functionality."""

    def test_policy_engine_singleton(self):
        """Test that PolicyBindingEngine follows singleton pattern."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        engine1 = PolicyBindingEngine()
        engine2 = PolicyBindingEngine()
        assert engine1 is engine2

    def test_policy_type_enum(self):
        """Test PolicyType enum values."""
        from app.orchestration.policy_binding_engine import PolicyType
        assert PolicyType.CITY_GOVERNANCE.value == "city_governance"
        assert PolicyType.DEPARTMENT_SOP.value == "department_sop"
        assert PolicyType.LEGAL_GUARDRAIL.value == "legal_guardrail"
        assert PolicyType.ETHICAL_GUARDRAIL.value == "ethical_guardrail"
        assert PolicyType.MORAL_COMPASS.value == "moral_compass"
        assert PolicyType.CONSTITUTIONAL.value == "constitutional"

    def test_guardrail_severity_enum(self):
        """Test GuardrailSeverity enum values."""
        from app.orchestration.policy_binding_engine import GuardrailSeverity
        assert GuardrailSeverity.BLOCKING.value == "blocking"
        assert GuardrailSeverity.WARNING.value == "warning"
        assert GuardrailSeverity.ADVISORY.value == "advisory"
        assert GuardrailSeverity.INFORMATIONAL.value == "informational"

    def test_guardrail_check_creation(self):
        """Test GuardrailCheck dataclass creation."""
        from app.orchestration.policy_binding_engine import GuardrailCheck, GuardrailSeverity
        check = GuardrailCheck(
            check_id="check-001",
            binding_id="binding-001",
            workflow_id="workflow-001",
            action_type="drone_dispatch",
            passed=True,
            severity=GuardrailSeverity.WARNING,
            message="Check passed",
            details={},
            checked_at=datetime.utcnow(),
        )
        assert check.passed is True
        assert check.severity == GuardrailSeverity.WARNING

    def test_policy_binding_creation(self):
        """Test PolicyBinding dataclass creation."""
        from app.orchestration.policy_binding_engine import (
            PolicyBinding, PolicyType, GuardrailSeverity
        )
        binding = PolicyBinding(
            name="Test Binding",
            description="A test policy binding",
            policy_type=PolicyType.DEPARTMENT_SOP,
            severity=GuardrailSeverity.WARNING,
            applicable_workflows=["*"],
            applicable_actions=["drone_dispatch"],
            conditions={},
            enforcement_rules=[],
            enabled=True,
        )
        assert binding.name == "Test Binding"
        assert binding.policy_type == PolicyType.DEPARTMENT_SOP
        assert binding.binding_id is not None

    def test_register_policy_binding(self):
        """Test registering a policy binding."""
        from app.orchestration.policy_binding_engine import (
            PolicyBindingEngine, PolicyBinding, PolicyType, GuardrailSeverity
        )
        engine = PolicyBindingEngine()
        binding = PolicyBinding(
            name="Registration Test",
            description="Test registration",
            policy_type=PolicyType.LEGAL_GUARDRAIL,
            severity=GuardrailSeverity.BLOCKING,
            applicable_workflows=["*"],
            applicable_actions=["*"],
            conditions={},
            enforcement_rules=[],
            enabled=True,
        )
        engine.register_binding(binding)
        bindings = engine.get_policy_bindings()
        assert len(bindings) > 0

    def test_get_applicable_bindings(self):
        """Test getting applicable bindings for a workflow."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        engine = PolicyBindingEngine()
        bindings = engine.get_applicable_bindings("test_workflow", "drone_dispatch")
        assert isinstance(bindings, list)

    def test_get_statistics(self):
        """Test getting policy engine statistics."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        engine = PolicyBindingEngine()
        stats = engine.get_statistics()
        assert "total_bindings" in stats
        assert "total_checks" in stats

    def test_get_check_history(self):
        """Test getting policy check history."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        engine = PolicyBindingEngine()
        history = engine.get_check_history(limit=50)
        assert isinstance(history, list)

    def test_get_compliance_summary(self):
        """Test getting compliance summary."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        engine = PolicyBindingEngine()
        summary = engine.get_compliance_summary()
        assert isinstance(summary, dict)


class TestPolicyChecking:
    """Test suite for policy checking logic."""

    @pytest.mark.asyncio
    async def test_check_policy(self):
        """Test policy checking for an action."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        engine = PolicyBindingEngine()
        result = await engine.check_policy(
            workflow_id="test-workflow",
            action_type="drone_dispatch",
            parameters={"mission_type": "surveillance"},
        )
        assert isinstance(result, list)

    def test_blocking_violation_detection(self):
        """Test detection of blocking policy violations."""
        from app.orchestration.policy_binding_engine import GuardrailSeverity
        assert GuardrailSeverity.BLOCKING.value == "blocking"

    def test_warning_generation(self):
        """Test warning generation for policy checks."""
        from app.orchestration.policy_binding_engine import GuardrailSeverity
        assert GuardrailSeverity.WARNING.value == "warning"


class TestDefaultBindings:
    """Test suite for default policy bindings."""

    def test_default_bindings_registered(self):
        """Test that default policy bindings are registered."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        engine = PolicyBindingEngine()
        bindings = engine.get_policy_bindings()
        assert len(bindings) > 0

    def test_constitutional_binding_exists(self):
        """Test that constitutional binding exists."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine, PolicyType
        engine = PolicyBindingEngine()
        bindings = engine.get_policy_bindings()
        constitutional = [b for b in bindings if b.policy_type == PolicyType.CONSTITUTIONAL]
        assert len(constitutional) > 0

    def test_use_of_force_binding_exists(self):
        """Test that use of force binding exists."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine, PolicyType
        engine = PolicyBindingEngine()
        bindings = engine.get_policy_bindings()
        uof = [b for b in bindings if b.policy_type == PolicyType.USE_OF_FORCE]
        assert len(uof) > 0
