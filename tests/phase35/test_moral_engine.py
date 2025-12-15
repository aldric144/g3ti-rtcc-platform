"""
Test Suite: Moral Compass Core Engine

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for the core moral assessment and decision-making engine.
"""

import pytest
from datetime import datetime

from backend.app.moral_compass.moral_engine import (
    MoralEngine,
    MoralDecisionType,
    EthicalPrinciple,
    HarmLevel,
    RiskCategory,
    LegalFramework,
    ReasoningStep,
    ReasoningChain,
    HarmAssessment,
    LegalCompliance,
    MoralAssessment,
    MoralDecision,
)


class TestMoralDecisionType:
    """Tests for MoralDecisionType enum."""

    def test_decision_types_exist(self):
        assert MoralDecisionType.ALLOW is not None
        assert MoralDecisionType.ALLOW_WITH_CAUTION is not None
        assert MoralDecisionType.HUMAN_APPROVAL_NEEDED is not None
        assert MoralDecisionType.DENY is not None

    def test_decision_type_values(self):
        assert MoralDecisionType.ALLOW.value == "allow"
        assert MoralDecisionType.DENY.value == "deny"


class TestEthicalPrinciple:
    """Tests for EthicalPrinciple enum."""

    def test_all_principles_exist(self):
        principles = [
            EthicalPrinciple.BENEFICENCE,
            EthicalPrinciple.NON_MALEFICENCE,
            EthicalPrinciple.AUTONOMY,
            EthicalPrinciple.JUSTICE,
            EthicalPrinciple.DIGNITY,
            EthicalPrinciple.TRANSPARENCY,
            EthicalPrinciple.ACCOUNTABILITY,
            EthicalPrinciple.PRIVACY,
            EthicalPrinciple.FAIRNESS,
            EthicalPrinciple.PROPORTIONALITY,
        ]
        assert len(principles) == 10


class TestHarmLevel:
    """Tests for HarmLevel enum."""

    def test_harm_levels_ordered(self):
        levels = [
            HarmLevel.NONE,
            HarmLevel.MINIMAL,
            HarmLevel.LOW,
            HarmLevel.MODERATE,
            HarmLevel.HIGH,
            HarmLevel.SEVERE,
            HarmLevel.CATASTROPHIC,
        ]
        assert len(levels) == 7


class TestMoralEngine:
    """Tests for MoralEngine singleton."""

    def test_singleton_pattern(self):
        engine1 = MoralEngine()
        engine2 = MoralEngine()
        assert engine1 is engine2

    def test_engine_initialization(self):
        engine = MoralEngine()
        assert engine._initialized is True
        assert len(engine.legal_rules) > 0
        assert len(engine.ethical_principles) > 0

    def test_assess_basic_action(self):
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="community_engagement",
            action_description="Attend neighborhood meeting",
            requester_id="officer_001",
        )
        assert assessment is not None
        assert assessment.assessment_id is not None
        assert assessment.action_type == "community_engagement"

    def test_assess_high_risk_action(self):
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="use_of_force",
            action_description="Deploy force against suspect",
            requester_id="officer_002",
        )
        assert assessment is not None
        assert assessment.decision in [
            MoralDecisionType.ALLOW_WITH_CAUTION,
            MoralDecisionType.HUMAN_APPROVAL_NEEDED,
            MoralDecisionType.DENY,
        ]

    def test_make_decision(self):
        engine = MoralEngine()
        decision = engine.make_decision(
            action_type="traffic_stop",
            action_description="Routine traffic stop for speeding",
            requester_id="officer_003",
        )
        assert decision is not None
        assert decision.decision_type is not None
        assert decision.explanation is not None
        assert decision.confidence > 0

    def test_veto_action(self):
        engine = MoralEngine()
        decision = engine.veto_action(
            action_type="warrantless_search",
            reason="Constitutional violation",
            requester_id="supervisor_001",
        )
        assert decision.decision_type == MoralDecisionType.DENY
        assert "veto" in decision.explanation.lower()

    def test_get_statistics(self):
        engine = MoralEngine()
        stats = engine.get_statistics()
        assert "total_assessments" in stats
        assert "decisions_made" in stats
        assert "vetoes_issued" in stats

    def test_get_audit_trail(self):
        engine = MoralEngine()
        engine.assess(
            action_type="patrol",
            action_description="Routine patrol",
            requester_id="officer_004",
        )
        trail = engine.get_audit_trail()
        assert isinstance(trail, list)

    def test_assessment_hash_integrity(self):
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="investigation",
            action_description="Follow up on lead",
            requester_id="detective_001",
        )
        assert assessment.assessment_hash is not None
        assert len(assessment.assessment_hash) == 16


class TestReasoningChain:
    """Tests for ReasoningChain dataclass."""

    def test_reasoning_chain_creation(self):
        chain = ReasoningChain(
            steps=[],
            final_conclusion="Action is permitted",
            confidence=0.9,
        )
        assert chain.chain_id is not None
        assert chain.confidence == 0.9

    def test_reasoning_chain_to_dict(self):
        chain = ReasoningChain(
            steps=[],
            final_conclusion="Test conclusion",
            confidence=0.85,
        )
        data = chain.to_dict()
        assert "chain_id" in data
        assert "final_conclusion" in data
        assert data["confidence"] == 0.85


class TestHarmAssessment:
    """Tests for HarmAssessment dataclass."""

    def test_harm_assessment_creation(self):
        assessment = HarmAssessment(
            harm_level=HarmLevel.LOW,
            risk_categories=[RiskCategory.PHYSICAL],
            affected_parties=["suspect"],
            mitigation_strategies=["de-escalation"],
        )
        assert assessment.harm_level == HarmLevel.LOW
        assert len(assessment.risk_categories) == 1

    def test_harm_assessment_to_dict(self):
        assessment = HarmAssessment(
            harm_level=HarmLevel.MODERATE,
            risk_categories=[RiskCategory.PSYCHOLOGICAL],
            affected_parties=["victim"],
            mitigation_strategies=["counseling referral"],
        )
        data = assessment.to_dict()
        assert data["harm_level"] == "moderate"


class TestLegalCompliance:
    """Tests for LegalCompliance dataclass."""

    def test_legal_compliance_creation(self):
        compliance = LegalCompliance(
            framework=LegalFramework.CONSTITUTIONAL,
            compliant=True,
            relevant_laws=["4th Amendment"],
            violations=[],
        )
        assert compliance.compliant is True
        assert compliance.framework == LegalFramework.CONSTITUTIONAL

    def test_legal_compliance_violation(self):
        compliance = LegalCompliance(
            framework=LegalFramework.FEDERAL_LAW,
            compliant=False,
            relevant_laws=["Civil Rights Act"],
            violations=["Discrimination"],
        )
        assert compliance.compliant is False
        assert len(compliance.violations) == 1


class TestMoralAssessment:
    """Tests for MoralAssessment dataclass."""

    def test_moral_assessment_hash(self):
        assessment = MoralAssessment(
            action_type="test",
            requester_id="test_user",
            decision=MoralDecisionType.ALLOW,
            reasoning_chain=ReasoningChain(
                steps=[],
                final_conclusion="Test",
                confidence=0.9,
            ),
            harm_assessment=HarmAssessment(
                harm_level=HarmLevel.NONE,
                risk_categories=[],
                affected_parties=[],
                mitigation_strategies=[],
            ),
            legal_compliance=[],
            principles_evaluated=[],
            community_impact_score=10.0,
            risk_to_community=5.0,
            required_approvals=[],
            conditions=[],
        )
        assert assessment.assessment_hash is not None


class TestMoralDecision:
    """Tests for MoralDecision dataclass."""

    def test_moral_decision_creation(self):
        assessment = MoralAssessment(
            action_type="test",
            requester_id="test_user",
            decision=MoralDecisionType.ALLOW,
            reasoning_chain=ReasoningChain(
                steps=[],
                final_conclusion="Test",
                confidence=0.9,
            ),
            harm_assessment=HarmAssessment(
                harm_level=HarmLevel.NONE,
                risk_categories=[],
                affected_parties=[],
                mitigation_strategies=[],
            ),
            legal_compliance=[],
            principles_evaluated=[],
            community_impact_score=10.0,
            risk_to_community=5.0,
            required_approvals=[],
            conditions=[],
        )
        decision = MoralDecision(
            decision_type=MoralDecisionType.ALLOW,
            assessment=assessment,
            explanation="Action permitted",
            confidence=0.9,
            alternatives=[],
        )
        assert decision.decision_id is not None
        assert decision.decision_type == MoralDecisionType.ALLOW
