"""
Test Suite: Youth Protection

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for youth protection rules and safeguards.
"""

import pytest

from backend.app.moral_compass.ethical_guardrails import (
    EthicalGuardrails,
    GuardrailType,
    ProtectionCategory,
    ViolationSeverity,
)
from backend.app.moral_compass.culture_context_engine import (
    CultureContextEngine,
    VulnerabilityFactor,
)


class TestYouthProtectionGuardrails:
    """Tests for youth protection guardrails."""

    def test_youth_protection_rule_exists(self):
        guardrails = EthicalGuardrails()
        youth_rules = [
            r for r in guardrails.rules.values()
            if r.guardrail_type == GuardrailType.YOUTH_PROTECTION
        ]
        assert len(youth_rules) > 0

    def test_enforce_youth_protection_minor(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_youth_protection(
            action_type="arrest",
            context={"involves_minor": True, "age": 14},
        )
        assert result["youth_protection_active"] is True
        assert "parent_notification" in result["requirements"] or len(result["requirements"]) > 0

    def test_enforce_youth_protection_teenager(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_youth_protection(
            action_type="interrogation",
            context={"involves_minor": True, "age": 16},
        )
        assert result["youth_protection_active"] is True
        assert len(result["requirements"]) > 0

    def test_enforce_youth_protection_adult(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_youth_protection(
            action_type="arrest",
            context={"involves_minor": False, "age": 25},
        )
        assert result["youth_protection_active"] is False

    def test_youth_protection_school_context(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_youth_protection(
            action_type="investigation",
            context={
                "involves_minor": True,
                "age": 15,
                "location": "school",
            },
        )
        assert result["youth_protection_active"] is True
        assert "school_liaison" in result["requirements"] or len(result["requirements"]) > 0

    def test_youth_protection_detention(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_youth_protection(
            action_type="detention",
            context={"involves_minor": True, "age": 13},
        )
        assert result["youth_protection_active"] is True
        assert result["specialized_handling_required"] is True


class TestYouthVulnerabilityContext:
    """Tests for youth vulnerability context."""

    def test_get_youth_vulnerability_context(self):
        engine = CultureContextEngine()
        context = engine.get_youth_vulnerability_context("Downtown Riviera Beach")
        assert context is not None
        assert "youth_vulnerability_score" in context
        assert "risk_factors" in context
        assert "protective_factors" in context
        assert "recommended_interventions" in context

    def test_youth_vulnerability_score_range(self):
        engine = CultureContextEngine()
        context = engine.get_youth_vulnerability_context("West Riviera Beach")
        score = context["youth_vulnerability_score"]
        assert 0 <= score <= 1

    def test_youth_risk_factors(self):
        engine = CultureContextEngine()
        context = engine.get_youth_vulnerability_context("Riviera Beach Heights")
        risk_factors = context["risk_factors"]
        assert isinstance(risk_factors, list)

    def test_youth_protective_factors(self):
        engine = CultureContextEngine()
        context = engine.get_youth_vulnerability_context("Singer Island")
        protective_factors = context["protective_factors"]
        assert isinstance(protective_factors, list)


class TestYouthProtectionViolations:
    """Tests for youth protection violation detection."""

    def test_detect_youth_protection_violation(self):
        guardrails = EthicalGuardrails()
        assessment = guardrails.check_action(
            action_type="interrogation",
            action_description="Interrogate minor without parent present",
            requester_id="officer_001",
            context={
                "involves_minor": True,
                "age": 14,
                "parent_present": False,
            },
        )
        assert assessment is not None

    def test_youth_protection_severity(self):
        guardrails = EthicalGuardrails()
        youth_rules = [
            r for r in guardrails.rules.values()
            if r.guardrail_type == GuardrailType.YOUTH_PROTECTION
        ]
        for rule in youth_rules:
            assert rule.severity in [
                ViolationSeverity.SERIOUS,
                ViolationSeverity.CRITICAL,
                ViolationSeverity.BLOCKING,
            ]


class TestYouthProtectionIntegration:
    """Integration tests for youth protection."""

    def test_youth_protection_with_moral_assessment(self):
        from backend.app.moral_compass.moral_engine import MoralEngine
        
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="arrest",
            action_description="Arrest juvenile suspect",
            requester_id="officer_001",
            context={"involves_minor": True, "age": 15},
        )
        assert assessment is not None
        assert len(assessment.required_approvals) > 0 or len(assessment.conditions) > 0

    def test_youth_protection_with_cultural_context(self):
        context_engine = CultureContextEngine()
        guardrails = EthicalGuardrails()
        
        youth_context = context_engine.get_youth_vulnerability_context("Downtown Riviera Beach")
        
        result = guardrails.enforce_youth_protection(
            action_type="intervention",
            context={
                "involves_minor": True,
                "age": 16,
                "vulnerability_score": youth_context["youth_vulnerability_score"],
            },
        )
        assert result["youth_protection_active"] is True
