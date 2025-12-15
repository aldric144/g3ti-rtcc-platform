"""
Test Suite: End-to-End Moral Compass

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
End-to-end integration tests for the complete moral compass system.
"""

import pytest
from datetime import datetime, timedelta

from backend.app.moral_compass.moral_engine import (
    MoralEngine,
    MoralDecisionType,
)
from backend.app.moral_compass.ethical_guardrails import (
    EthicalGuardrails,
    GuardrailType,
)
from backend.app.moral_compass.fairness_analyzer import (
    FairnessAnalyzer,
)
from backend.app.moral_compass.culture_context_engine import (
    CultureContextEngine,
    EventType,
    TrustLevel,
)
from backend.app.moral_compass.moral_graph import (
    MoralGraph,
)


class TestE2EMoralAssessment:
    """End-to-end tests for moral assessment flow."""

    def test_complete_assessment_flow(self):
        engine = MoralEngine()
        guardrails = EthicalGuardrails()
        analyzer = FairnessAnalyzer()
        context_engine = CultureContextEngine()
        graph = MoralGraph()
        
        cultural_context = context_engine.get_context(
            location="Downtown Riviera Beach",
            action_type="patrol",
        )
        
        guardrail_check = guardrails.check_action(
            action_type="patrol",
            action_description="Routine patrol in downtown area",
            requester_id="officer_001",
            context={},
        )
        
        fairness_check = analyzer.assess_fairness(
            action_type="patrol",
            requester_id="officer_001",
        )
        
        moral_assessment = engine.assess(
            action_type="patrol",
            action_description="Routine patrol in downtown area",
            requester_id="officer_001",
            cultural_context={"trust_level": cultural_context.trust_level.value},
        )
        
        capsule = graph.generate_explainability_capsule(
            action_type="patrol",
            decision=moral_assessment.decision.value,
            context={},
        )
        
        assert cultural_context is not None
        assert guardrail_check is not None
        assert fairness_check is not None
        assert moral_assessment is not None
        assert capsule is not None

    def test_high_risk_action_flow(self):
        engine = MoralEngine()
        guardrails = EthicalGuardrails()
        
        guardrail_check = guardrails.check_action(
            action_type="use_of_force",
            action_description="Deploy force against armed suspect",
            requester_id="officer_001",
            context={
                "threat_level": "high",
                "de_escalation_attempted": True,
            },
        )
        
        moral_assessment = engine.assess(
            action_type="use_of_force",
            action_description="Deploy force against armed suspect",
            requester_id="officer_001",
            context={
                "threat_level": "high",
                "de_escalation_attempted": True,
            },
        )
        
        assert guardrail_check is not None
        assert moral_assessment is not None
        assert moral_assessment.decision in [
            MoralDecisionType.ALLOW_WITH_CAUTION,
            MoralDecisionType.HUMAN_APPROVAL_NEEDED,
        ]


class TestE2EYouthProtection:
    """End-to-end tests for youth protection."""

    def test_youth_arrest_flow(self):
        engine = MoralEngine()
        guardrails = EthicalGuardrails()
        context_engine = CultureContextEngine()
        
        youth_context = context_engine.get_youth_vulnerability_context("Downtown Riviera Beach")
        
        youth_protection = guardrails.enforce_youth_protection(
            action_type="arrest",
            context={"involves_minor": True, "age": 15},
        )
        
        moral_assessment = engine.assess(
            action_type="arrest",
            action_description="Arrest juvenile suspect",
            requester_id="officer_001",
            context={"involves_minor": True, "age": 15},
        )
        
        assert youth_context is not None
        assert youth_protection["youth_protection_active"] is True
        assert moral_assessment is not None
        assert len(moral_assessment.required_approvals) > 0 or len(moral_assessment.conditions) > 0


class TestE2EVulnerablePopulation:
    """End-to-end tests for vulnerable population protection."""

    def test_mental_health_response_flow(self):
        engine = MoralEngine()
        guardrails = EthicalGuardrails()
        
        vp_rules = guardrails.enforce_vulnerable_population_rules(
            action_type="response",
            population_type="mental_health",
            context={},
        )
        
        moral_assessment = engine.assess(
            action_type="response",
            action_description="Respond to mental health crisis",
            requester_id="officer_001",
            context={"vulnerable_population": True, "population_type": "mental_health"},
        )
        
        assert vp_rules["specialized_unit_required"] is True
        assert moral_assessment is not None


class TestE2EBiasDetection:
    """End-to-end tests for bias detection."""

    def test_predictive_targeting_bias_flow(self):
        analyzer = FairnessAnalyzer()
        guardrails = EthicalGuardrails()
        engine = MoralEngine()
        
        fairness_check = analyzer.assess_fairness(
            action_type="predictive_targeting",
            requester_id="system_001",
            historical_data={"demographic_disparity": True},
        )
        
        bias_prevention = guardrails.prevent_bias_reinforcement(
            action_type="predictive_targeting",
            historical_data={"demographic_disparity": True},
        )
        
        moral_assessment = engine.assess(
            action_type="predictive_targeting",
            action_description="Target area based on predictive model",
            requester_id="system_001",
            context={"bias_detected": any(b.detected for b in fairness_check.bias_detections)},
        )
        
        assert fairness_check is not None
        assert bias_prevention["bias_risks_identified"] is True
        assert moral_assessment is not None


class TestE2ECulturalContext:
    """End-to-end tests for cultural context integration."""

    def test_community_event_context_flow(self):
        context_engine = CultureContextEngine()
        engine = MoralEngine()
        
        event = context_engine.add_event(
            name="Community Vigil",
            event_type=EventType.VIGIL,
            location="Downtown Riviera Beach",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=2),
            expected_attendance=100,
            community_significance="high",
        )
        
        context = context_engine.get_context(
            location="Downtown Riviera Beach",
            action_type="patrol",
        )
        
        moral_assessment = engine.assess(
            action_type="patrol",
            action_description="Patrol near community vigil",
            requester_id="officer_001",
            cultural_context={
                "active_events": [event.name],
                "trust_level": context.trust_level.value,
            },
        )
        
        assert event is not None
        assert context is not None
        assert len(context.active_events) > 0
        assert moral_assessment is not None


class TestE2EReasoningChain:
    """End-to-end tests for reasoning chain generation."""

    def test_full_reasoning_chain_flow(self):
        engine = MoralEngine()
        graph = MoralGraph()
        
        moral_assessment = engine.assess(
            action_type="search",
            action_description="Search vehicle with consent",
            requester_id="officer_001",
            context={"consent_given": True},
        )
        
        reasoning_graph = graph.build_reasoning_graph(
            action_type="search",
            context={"consent_given": True},
        )
        
        capsule = graph.generate_explainability_capsule(
            action_type="search",
            decision=moral_assessment.decision.value,
            context={
                "key_factors": moral_assessment.conditions,
                "risk_factors": [r.value for r in moral_assessment.harm_assessment.risk_categories],
                "community_considerations": moral_assessment.required_approvals,
            },
        )
        
        plan = graph.generate_responsible_ai_plan(
            action_type="search",
            context={"consent_given": True},
        )
        
        assert moral_assessment.reasoning_chain is not None
        assert reasoning_graph is not None
        assert capsule is not None
        assert plan is not None


class TestE2EVetoFlow:
    """End-to-end tests for veto functionality."""

    def test_veto_unconstitutional_action(self):
        engine = MoralEngine()
        guardrails = EthicalGuardrails()
        
        guardrail_check = guardrails.check_action(
            action_type="warrantless_search",
            action_description="Search without warrant or consent",
            requester_id="officer_001",
            context={},
        )
        
        veto_decision = engine.veto_action(
            action_type="warrantless_search",
            reason="Constitutional violation - 4th Amendment",
            requester_id="supervisor_001",
        )
        
        assert guardrail_check is not None
        assert veto_decision.decision_type == MoralDecisionType.DENY
        assert "veto" in veto_decision.explanation.lower()


class TestE2EAuditTrail:
    """End-to-end tests for audit trail."""

    def test_complete_audit_trail(self):
        engine = MoralEngine()
        guardrails = EthicalGuardrails()
        analyzer = FairnessAnalyzer()
        
        engine.assess(
            action_type="patrol",
            action_description="Routine patrol",
            requester_id="officer_001",
        )
        
        guardrails.check_action(
            action_type="patrol",
            action_description="Routine patrol",
            requester_id="officer_001",
            context={},
        )
        
        analyzer.assess_fairness(
            action_type="patrol",
            requester_id="officer_001",
        )
        
        moral_trail = engine.get_audit_trail()
        moral_stats = engine.get_statistics()
        guardrail_stats = guardrails.get_statistics()
        fairness_stats = analyzer.get_statistics()
        
        assert isinstance(moral_trail, list)
        assert moral_stats["total_assessments"] > 0
        assert guardrail_stats["total_checks"] > 0
        assert fairness_stats["total_assessments"] > 0


class TestE2EStatistics:
    """End-to-end tests for statistics collection."""

    def test_comprehensive_statistics(self):
        engine = MoralEngine()
        guardrails = EthicalGuardrails()
        analyzer = FairnessAnalyzer()
        context_engine = CultureContextEngine()
        graph = MoralGraph()
        
        moral_stats = engine.get_statistics()
        guardrail_stats = guardrails.get_statistics()
        fairness_stats = analyzer.get_statistics()
        context_stats = context_engine.get_statistics()
        graph_stats = graph.get_statistics()
        
        assert "total_assessments" in moral_stats
        assert "total_checks" in guardrail_stats
        assert "total_assessments" in fairness_stats
        assert "contexts_generated" in context_stats
        assert "total_nodes" in graph_stats
