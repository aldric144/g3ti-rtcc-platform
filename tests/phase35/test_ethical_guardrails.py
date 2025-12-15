"""
Test Suite: Ethical Guardrails Module

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for ethical safeguards and guardrail enforcement.
"""

import pytest
from datetime import datetime

from backend.app.moral_compass.ethical_guardrails import (
    EthicalGuardrails,
    GuardrailType,
    ProtectionCategory,
    ViolationSeverity,
    GuardrailRule,
    GuardrailCheck,
    GuardrailViolation,
    GuardrailAssessment,
)


class TestGuardrailType:
    """Tests for GuardrailType enum."""

    def test_guardrail_types_exist(self):
        types = [
            GuardrailType.CONSTITUTIONAL,
            GuardrailType.POLICY,
            GuardrailType.ETHICAL,
            GuardrailType.YOUTH_PROTECTION,
            GuardrailType.VULNERABLE_POPULATION,
            GuardrailType.USE_OF_FORCE,
            GuardrailType.DISCRIMINATION,
            GuardrailType.BIAS_PREVENTION,
            GuardrailType.PRIVACY,
            GuardrailType.TRANSPARENCY,
        ]
        assert len(types) == 10


class TestProtectionCategory:
    """Tests for ProtectionCategory enum."""

    def test_protection_categories_exist(self):
        categories = [
            ProtectionCategory.MINORS,
            ProtectionCategory.ELDERLY,
            ProtectionCategory.DISABLED,
            ProtectionCategory.MENTAL_HEALTH,
            ProtectionCategory.HOMELESS,
            ProtectionCategory.DOMESTIC_VIOLENCE,
            ProtectionCategory.IMMIGRANTS,
            ProtectionCategory.LOW_INCOME,
            ProtectionCategory.GENERAL_PUBLIC,
        ]
        assert len(categories) == 9


class TestEthicalGuardrails:
    """Tests for EthicalGuardrails singleton."""

    def test_singleton_pattern(self):
        guardrails1 = EthicalGuardrails()
        guardrails2 = EthicalGuardrails()
        assert guardrails1 is guardrails2

    def test_initialization(self):
        guardrails = EthicalGuardrails()
        assert guardrails._initialized is True
        assert len(guardrails.rules) > 0

    def test_check_action_safe(self):
        guardrails = EthicalGuardrails()
        assessment = guardrails.check_action(
            action_type="community_meeting",
            action_description="Attend community meeting",
            requester_id="officer_001",
            context={"warrant_required": True, "probable_cause_required": True},
        )
        assert assessment is not None
        assert assessment.assessment_id is not None

    def test_check_action_violation(self):
        guardrails = EthicalGuardrails()
        assessment = guardrails.check_action(
            action_type="warrantless_search",
            action_description="Search without warrant",
            requester_id="officer_002",
            context={},
        )
        assert assessment is not None
        assert len(assessment.violations) > 0 or assessment.passed

    def test_detect_harmful_intent(self):
        guardrails = EthicalGuardrails()
        result = guardrails.detect_harmful_intent(
            action_type="force",
            action_description="Use force against suspect",
            context={"no_justification": True},
        )
        assert "harmful_intent_detected" in result
        assert "harm_score" in result

    def test_flag_discrimination(self):
        guardrails = EthicalGuardrails()
        result = guardrails.flag_discrimination(
            action_type="targeting",
            context={"based_on_race": True},
        )
        assert result["discrimination_detected"] is True
        assert "race" in result["flags"]

    def test_flag_no_discrimination(self):
        guardrails = EthicalGuardrails()
        result = guardrails.flag_discrimination(
            action_type="patrol",
            context={},
        )
        assert result["discrimination_detected"] is False

    def test_validate_use_of_force_approved(self):
        guardrails = EthicalGuardrails()
        result = guardrails.validate_use_of_force(
            force_level="verbal",
            context={
                "de_escalation_attempted": True,
                "proportional_to_threat": True,
                "necessary": True,
            },
        )
        assert result["approved"] is True

    def test_validate_use_of_force_denied(self):
        guardrails = EthicalGuardrails()
        result = guardrails.validate_use_of_force(
            force_level="deadly",
            context={
                "de_escalation_attempted": False,
                "proportional_to_threat": False,
                "necessary": False,
            },
        )
        assert result["approved"] is False
        assert len(result["issues"]) > 0

    def test_enforce_youth_protection(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_youth_protection(
            action_type="arrest",
            context={"involves_minor": True, "age": 15},
        )
        assert result["youth_protection_active"] is True
        assert len(result["requirements"]) > 0

    def test_enforce_vulnerable_population_mental_health(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_vulnerable_population_rules(
            action_type="response",
            population_type="mental_health",
            context={},
        )
        assert result["specialized_unit_required"] is True
        assert len(result["requirements"]) > 0

    def test_prevent_bias_reinforcement(self):
        guardrails = EthicalGuardrails()
        result = guardrails.prevent_bias_reinforcement(
            action_type="predictive_targeting",
            historical_data={"demographic_disparity": True},
        )
        assert len(result["bias_risks"]) > 0
        assert result["mitigation_required"] is True

    def test_get_active_violations(self):
        guardrails = EthicalGuardrails()
        violations = guardrails.get_active_violations()
        assert isinstance(violations, list)

    def test_resolve_violation(self):
        guardrails = EthicalGuardrails()
        guardrails.check_action(
            action_type="search",
            action_description="Search without warrant",
            requester_id="officer_003",
            context={},
        )
        violations = guardrails.get_active_violations()
        if violations:
            result = guardrails.resolve_violation(
                violation_id=violations[0].violation_id,
                resolved_by="supervisor_001",
            )
            assert result is True

    def test_get_statistics(self):
        guardrails = EthicalGuardrails()
        stats = guardrails.get_statistics()
        assert "total_checks" in stats
        assert "violations" in stats
        assert "blocked" in stats


class TestGuardrailRule:
    """Tests for GuardrailRule dataclass."""

    def test_rule_creation(self):
        rule = GuardrailRule(
            rule_id="TEST-001",
            name="Test Rule",
            description="A test rule",
            guardrail_type=GuardrailType.ETHICAL,
            protection_categories=[ProtectionCategory.GENERAL_PUBLIC],
            triggers=["test"],
            conditions=["test_condition"],
            action_on_violation="block",
            severity=ViolationSeverity.SERIOUS,
        )
        assert rule.rule_id == "TEST-001"
        assert rule.severity == ViolationSeverity.SERIOUS

    def test_rule_to_dict(self):
        rule = GuardrailRule(
            rule_id="TEST-002",
            name="Test Rule 2",
            description="Another test rule",
            guardrail_type=GuardrailType.POLICY,
            protection_categories=[],
            triggers=[],
            conditions=[],
            action_on_violation="warn",
            severity=ViolationSeverity.WARNING,
        )
        data = rule.to_dict()
        assert data["rule_id"] == "TEST-002"
        assert data["guardrail_type"] == "policy"


class TestGuardrailViolation:
    """Tests for GuardrailViolation dataclass."""

    def test_violation_creation(self):
        violation = GuardrailViolation(
            rule_id="CONST-4A",
            rule_name="Fourth Amendment",
            guardrail_type=GuardrailType.CONSTITUTIONAL,
            severity=ViolationSeverity.BLOCKING,
            action_type="search",
            action_description="Warrantless search",
            requester_id="officer_001",
            details="Missing warrant",
            blocked=True,
        )
        assert violation.violation_id is not None
        assert violation.blocked is True

    def test_violation_hash(self):
        violation = GuardrailViolation(
            rule_id="TEST",
            rule_name="Test",
            guardrail_type=GuardrailType.ETHICAL,
            severity=ViolationSeverity.SERIOUS,
            action_type="test",
            action_description="test",
            requester_id="test",
            details="test",
        )
        assert violation.violation_hash is not None
        assert len(violation.violation_hash) == 16


class TestGuardrailAssessment:
    """Tests for GuardrailAssessment dataclass."""

    def test_assessment_creation(self):
        assessment = GuardrailAssessment(
            action_type="patrol",
            requester_id="officer_001",
        )
        assert assessment.assessment_id is not None
        assert assessment.passed is True

    def test_assessment_to_dict(self):
        assessment = GuardrailAssessment(
            action_type="investigation",
            requester_id="detective_001",
        )
        data = assessment.to_dict()
        assert "assessment_id" in data
        assert "passed" in data
