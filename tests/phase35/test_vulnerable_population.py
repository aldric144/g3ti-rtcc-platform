"""
Test Suite: Vulnerable Population Protection

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for vulnerable population safeguards.
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


class TestVulnerablePopulationGuardrails:
    """Tests for vulnerable population guardrails."""

    def test_vulnerable_population_rule_exists(self):
        guardrails = EthicalGuardrails()
        vp_rules = [
            r for r in guardrails.rules.values()
            if r.guardrail_type == GuardrailType.VULNERABLE_POPULATION
        ]
        assert len(vp_rules) > 0

    def test_enforce_mental_health_rules(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_vulnerable_population_rules(
            action_type="response",
            population_type="mental_health",
            context={},
        )
        assert result["specialized_unit_required"] is True
        assert len(result["requirements"]) > 0

    def test_enforce_elderly_rules(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_vulnerable_population_rules(
            action_type="welfare_check",
            population_type="elderly",
            context={"age": 85},
        )
        assert result["specialized_handling_required"] is True

    def test_enforce_homeless_rules(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_vulnerable_population_rules(
            action_type="response",
            population_type="homeless",
            context={},
        )
        assert result["social_services_referral"] is True

    def test_enforce_disabled_rules(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_vulnerable_population_rules(
            action_type="interaction",
            population_type="disabled",
            context={"disability_type": "hearing_impaired"},
        )
        assert result["accommodation_required"] is True

    def test_enforce_domestic_violence_rules(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_vulnerable_population_rules(
            action_type="response",
            population_type="domestic_violence",
            context={},
        )
        assert result["victim_advocate_required"] is True

    def test_enforce_immigrant_rules(self):
        guardrails = EthicalGuardrails()
        result = guardrails.enforce_vulnerable_population_rules(
            action_type="interaction",
            population_type="immigrant",
            context={},
        )
        assert result["language_services_available"] is True


class TestProtectionCategories:
    """Tests for protection categories."""

    def test_all_protection_categories(self):
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

    def test_protection_category_in_rules(self):
        guardrails = EthicalGuardrails()
        all_categories = set()
        for rule in guardrails.rules.values():
            all_categories.update(rule.protection_categories)
        assert len(all_categories) > 0


class TestDomesticViolenceContext:
    """Tests for domestic violence cultural context."""

    def test_get_domestic_violence_context(self):
        engine = CultureContextEngine()
        context = engine.get_domestic_violence_context("Downtown Riviera Beach")
        assert context is not None
        assert "cultural_barriers" in context
        assert "recommended_approach" in context
        assert "resources_available" in context

    def test_domestic_violence_cultural_barriers(self):
        engine = CultureContextEngine()
        context = engine.get_domestic_violence_context("West Riviera Beach")
        barriers = context["cultural_barriers"]
        assert isinstance(barriers, list)

    def test_domestic_violence_recommended_approach(self):
        engine = CultureContextEngine()
        context = engine.get_domestic_violence_context("Singer Island")
        approach = context["recommended_approach"]
        assert approach is not None
        assert len(approach) > 0


class TestVulnerabilityFactors:
    """Tests for vulnerability factors."""

    def test_vulnerability_factors_exist(self):
        factors = [
            VulnerabilityFactor.YOUTH,
            VulnerabilityFactor.ELDERLY,
            VulnerabilityFactor.ECONOMIC,
            VulnerabilityFactor.HEALTH,
            VulnerabilityFactor.HOUSING,
            VulnerabilityFactor.EDUCATION,
            VulnerabilityFactor.EMPLOYMENT,
            VulnerabilityFactor.FAMILY,
            VulnerabilityFactor.MENTAL_HEALTH,
            VulnerabilityFactor.SUBSTANCE,
        ]
        assert len(factors) == 10

    def test_vulnerability_factors_in_neighborhoods(self):
        engine = CultureContextEngine()
        neighborhoods = engine.get_all_neighborhoods()
        for neighborhood in neighborhoods:
            assert isinstance(neighborhood.vulnerability_factors, list)


class TestVulnerablePopulationViolations:
    """Tests for vulnerable population violation detection."""

    def test_detect_vulnerable_population_violation(self):
        guardrails = EthicalGuardrails()
        assessment = guardrails.check_action(
            action_type="force",
            action_description="Use force against mentally ill individual",
            requester_id="officer_001",
            context={
                "vulnerable_population": True,
                "population_type": "mental_health",
                "crisis_intervention_trained": False,
            },
        )
        assert assessment is not None

    def test_vulnerable_population_severity(self):
        guardrails = EthicalGuardrails()
        vp_rules = [
            r for r in guardrails.rules.values()
            if r.guardrail_type == GuardrailType.VULNERABLE_POPULATION
        ]
        for rule in vp_rules:
            assert rule.severity in [
                ViolationSeverity.SERIOUS,
                ViolationSeverity.CRITICAL,
                ViolationSeverity.BLOCKING,
            ]


class TestVulnerablePopulationIntegration:
    """Integration tests for vulnerable population protection."""

    def test_vulnerable_population_with_moral_assessment(self):
        from backend.app.moral_compass.moral_engine import MoralEngine
        
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="response",
            action_description="Respond to mental health crisis",
            requester_id="officer_001",
            context={
                "vulnerable_population": True,
                "population_type": "mental_health",
            },
        )
        assert assessment is not None
        assert len(assessment.required_approvals) > 0 or len(assessment.conditions) > 0

    def test_vulnerable_population_with_fairness(self):
        from backend.app.moral_compass.fairness_analyzer import FairnessAnalyzer
        
        analyzer = FairnessAnalyzer()
        assessment = analyzer.assess_fairness(
            action_type="resource_allocation",
            requester_id="system_001",
            context={"target_population": "homeless"},
        )
        assert assessment is not None
        assert assessment.overall_fairness_score >= 0
