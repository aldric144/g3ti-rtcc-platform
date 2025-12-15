"""
Test Suite: Reasoning Chain

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for reasoning chain generation and explainability.
"""

import pytest

from backend.app.moral_compass.moral_engine import (
    MoralEngine,
    ReasoningStep,
    ReasoningChain,
)
from backend.app.moral_compass.moral_graph import (
    MoralGraph,
    ReasoningPath,
    ExplainabilityCapsule,
)


class TestReasoningStep:
    """Tests for ReasoningStep dataclass."""

    def test_reasoning_step_creation(self):
        step = ReasoningStep(
            step_number=1,
            description="Evaluate legal compliance",
            factors_considered=["4th Amendment", "probable cause"],
            supporting_factors=["warrant present"],
            opposing_factors=[],
            conclusion="Legally compliant",
            confidence=0.95,
        )
        assert step.step_number == 1
        assert step.confidence == 0.95

    def test_reasoning_step_to_dict(self):
        step = ReasoningStep(
            step_number=2,
            description="Assess harm potential",
            factors_considered=["physical risk"],
            supporting_factors=[],
            opposing_factors=["high risk"],
            conclusion="Moderate harm potential",
            confidence=0.7,
        )
        data = step.to_dict()
        assert data["step_number"] == 2
        assert data["conclusion"] == "Moderate harm potential"


class TestReasoningChain:
    """Tests for ReasoningChain dataclass."""

    def test_reasoning_chain_creation(self):
        steps = [
            ReasoningStep(
                step_number=1,
                description="Step 1",
                factors_considered=[],
                supporting_factors=[],
                opposing_factors=[],
                conclusion="Conclusion 1",
                confidence=0.9,
            ),
            ReasoningStep(
                step_number=2,
                description="Step 2",
                factors_considered=[],
                supporting_factors=[],
                opposing_factors=[],
                conclusion="Conclusion 2",
                confidence=0.85,
            ),
        ]
        chain = ReasoningChain(
            steps=steps,
            final_conclusion="Action permitted",
            confidence=0.87,
        )
        assert chain.chain_id is not None
        assert len(chain.steps) == 2
        assert chain.confidence == 0.87

    def test_reasoning_chain_to_dict(self):
        chain = ReasoningChain(
            steps=[],
            final_conclusion="Test conclusion",
            confidence=0.8,
        )
        data = chain.to_dict()
        assert "chain_id" in data
        assert data["final_conclusion"] == "Test conclusion"


class TestReasoningPath:
    """Tests for ReasoningPath dataclass."""

    def test_reasoning_path_creation(self):
        path = ReasoningPath(
            nodes=[],
            edges=[],
            total_weight=0.85,
            conclusion="Path leads to approval",
            confidence=0.9,
        )
        assert path.path_id is not None
        assert path.total_weight == 0.85

    def test_reasoning_path_to_dict(self):
        path = ReasoningPath(
            nodes=[],
            edges=[],
            total_weight=0.7,
            conclusion="Test path",
            confidence=0.75,
        )
        data = path.to_dict()
        assert "path_id" in data
        assert data["total_weight"] == 0.7


class TestExplainabilityCapsule:
    """Tests for ExplainabilityCapsule dataclass."""

    def test_capsule_creation(self):
        capsule = ExplainabilityCapsule(
            action_type="arrest",
            decision="allow_with_caution",
            reasoning_paths=[],
            key_factors=["probable_cause", "witness_statement"],
            constraints_applied=["4th_amendment"],
            ethical_principles=["justice", "proportionality"],
            risk_factors=["physical_risk"],
            community_considerations=["high_visibility_area"],
            human_readable_explanation="The arrest is permitted with caution due to...",
            confidence=0.85,
        )
        assert capsule.capsule_id is not None
        assert capsule.decision == "allow_with_caution"

    def test_capsule_hash_integrity(self):
        capsule = ExplainabilityCapsule(
            action_type="test",
            decision="allow",
            reasoning_paths=[],
            key_factors=[],
            constraints_applied=[],
            ethical_principles=[],
            risk_factors=[],
            community_considerations=[],
            human_readable_explanation="Test",
            confidence=0.9,
        )
        assert capsule.capsule_hash is not None
        assert len(capsule.capsule_hash) == 16


class TestMoralEngineReasoningChain:
    """Tests for reasoning chain generation in MoralEngine."""

    def test_assess_generates_reasoning_chain(self):
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="search",
            action_description="Search vehicle with consent",
            requester_id="officer_001",
        )
        assert assessment.reasoning_chain is not None
        assert assessment.reasoning_chain.chain_id is not None
        assert assessment.reasoning_chain.final_conclusion is not None

    def test_reasoning_chain_has_steps(self):
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="arrest",
            action_description="Arrest suspect with warrant",
            requester_id="officer_002",
        )
        assert len(assessment.reasoning_chain.steps) > 0

    def test_reasoning_chain_confidence(self):
        engine = MoralEngine()
        assessment = engine.assess(
            action_type="patrol",
            action_description="Routine patrol",
            requester_id="officer_003",
        )
        assert 0 <= assessment.reasoning_chain.confidence <= 1


class TestMoralGraphReasoningPath:
    """Tests for reasoning path generation in MoralGraph."""

    def test_build_reasoning_graph(self):
        graph = MoralGraph()
        result = graph.build_reasoning_graph(
            action_type="surveillance",
            context={"duration": "short"},
        )
        assert "nodes" in result
        assert "edges" in result
        assert "reasoning_paths" in result

    def test_generate_explainability_capsule(self):
        graph = MoralGraph()
        capsule = graph.generate_explainability_capsule(
            action_type="use_of_force",
            decision="human_approval_needed",
            context={
                "key_factors": ["threat_level"],
                "risk_factors": ["physical"],
                "community_considerations": ["high_trust_area"],
            },
        )
        assert capsule is not None
        assert capsule.human_readable_explanation is not None
        assert len(capsule.human_readable_explanation) > 0

    def test_generate_responsible_ai_plan(self):
        graph = MoralGraph()
        plan = graph.generate_responsible_ai_plan(
            action_type="predictive_targeting",
            context={"historical_data_used": True},
        )
        assert plan is not None
        assert "plan_id" in plan
        assert "steps" in plan
        assert "safeguards" in plan


class TestReasoningChainIntegration:
    """Integration tests for reasoning chain."""

    def test_full_reasoning_flow(self):
        engine = MoralEngine()
        graph = MoralGraph()
        
        assessment = engine.assess(
            action_type="detention",
            action_description="Detain suspect for questioning",
            requester_id="officer_001",
        )
        
        capsule = graph.generate_explainability_capsule(
            action_type=assessment.action_type,
            decision=assessment.decision.value,
            context={
                "key_factors": assessment.conditions,
                "risk_factors": [r.value for r in assessment.harm_assessment.risk_categories],
                "community_considerations": assessment.required_approvals,
            },
        )
        
        assert assessment.reasoning_chain is not None
        assert capsule is not None
        assert capsule.human_readable_explanation is not None

    def test_reasoning_chain_audit_trail(self):
        engine = MoralEngine()
        
        engine.assess(
            action_type="investigation",
            action_description="Investigate lead",
            requester_id="detective_001",
        )
        
        trail = engine.get_audit_trail()
        assert isinstance(trail, list)
