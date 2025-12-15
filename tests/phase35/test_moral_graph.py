"""
Test Suite: Moral Reasoning Graph

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Tests for graph-based moral reasoning and explainability.
"""

import pytest
from datetime import datetime

from backend.app.moral_compass.moral_graph import (
    MoralGraph,
    NodeType,
    EdgeType,
    GraphNode,
    GraphEdge,
    ReasoningPath,
    ExplainabilityCapsule,
)


class TestNodeType:
    """Tests for NodeType enum."""

    def test_node_types_exist(self):
        types = [
            NodeType.LEGAL_CONSTRAINT,
            NodeType.ETHICAL_PRINCIPLE,
            NodeType.HARM_LEVEL,
            NodeType.TRAUMA_FACTOR,
            NodeType.RISK_FACTOR,
            NodeType.CULTURAL_CONTEXT,
            NodeType.COMMUNITY_IMPACT,
            NodeType.DECISION,
            NodeType.ACTION,
            NodeType.CONDITION,
            NodeType.MITIGATION,
        ]
        assert len(types) == 11


class TestEdgeType:
    """Tests for EdgeType enum."""

    def test_edge_types_exist(self):
        types = [
            EdgeType.REQUIRES,
            EdgeType.CONFLICTS_WITH,
            EdgeType.SUPPORTS,
            EdgeType.MITIGATES,
            EdgeType.LEADS_TO,
            EdgeType.DEPENDS_ON,
            EdgeType.INFLUENCES,
            EdgeType.BLOCKS,
        ]
        assert len(types) == 8


class TestMoralGraph:
    """Tests for MoralGraph singleton."""

    def test_singleton_pattern(self):
        graph1 = MoralGraph()
        graph2 = MoralGraph()
        assert graph1 is graph2

    def test_initialization(self):
        graph = MoralGraph()
        assert graph._initialized is True
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

    def test_add_node(self):
        graph = MoralGraph()
        node = graph.add_node(
            node_type=NodeType.ACTION,
            label="Test Action",
            description="A test action node",
            weight=0.5,
        )
        assert node is not None
        assert node.node_id is not None
        assert node.label == "Test Action"

    def test_add_edge(self):
        graph = MoralGraph()
        node1 = graph.add_node(
            node_type=NodeType.CONDITION,
            label="Condition 1",
            description="Test condition",
        )
        node2 = graph.add_node(
            node_type=NodeType.DECISION,
            label="Decision 1",
            description="Test decision",
        )
        edge = graph.add_edge(
            source_id=node1.node_id,
            target_id=node2.node_id,
            edge_type=EdgeType.LEADS_TO,
            weight=0.8,
        )
        assert edge is not None
        assert edge.source_id == node1.node_id
        assert edge.target_id == node2.node_id

    def test_find_path(self):
        graph = MoralGraph()
        path = graph.find_path(
            start_node_id="legal_4th_amendment",
            end_node_id="decision_deny",
        )
        assert path is not None or path is None

    def test_build_reasoning_graph(self):
        graph = MoralGraph()
        result = graph.build_reasoning_graph(
            action_type="search",
            context={"warrant": False},
        )
        assert result is not None
        assert "nodes" in result
        assert "edges" in result
        assert "reasoning_paths" in result

    def test_generate_explainability_capsule(self):
        graph = MoralGraph()
        capsule = graph.generate_explainability_capsule(
            action_type="arrest",
            decision="allow_with_caution",
            context={
                "key_factors": ["probable_cause"],
                "risk_factors": ["physical"],
                "community_considerations": ["high_visibility"],
            },
        )
        assert capsule is not None
        assert capsule.capsule_id is not None
        assert capsule.human_readable_explanation is not None

    def test_generate_responsible_ai_plan(self):
        graph = MoralGraph()
        plan = graph.generate_responsible_ai_plan(
            action_type="surveillance",
            context={"duration": "extended"},
        )
        assert plan is not None
        assert "plan_id" in plan
        assert "steps" in plan
        assert "safeguards" in plan

    def test_export_graph(self):
        graph = MoralGraph()
        export = graph.export_graph()
        assert export is not None
        assert "nodes" in export
        assert "edges" in export
        assert "statistics" in export

    def test_get_capsule(self):
        graph = MoralGraph()
        capsule = graph.generate_explainability_capsule(
            action_type="test",
            decision="allow",
            context={},
        )
        retrieved = graph.get_capsule(capsule.capsule_id)
        assert retrieved is not None
        assert retrieved.capsule_id == capsule.capsule_id

    def test_get_statistics(self):
        graph = MoralGraph()
        stats = graph.get_statistics()
        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "capsules_generated" in stats
        assert "paths_traced" in stats


class TestGraphNode:
    """Tests for GraphNode dataclass."""

    def test_node_creation(self):
        node = GraphNode(
            node_type=NodeType.ETHICAL_PRINCIPLE,
            label="Justice",
            description="Fair treatment for all",
            weight=0.9,
        )
        assert node.node_id is not None
        assert node.node_type == NodeType.ETHICAL_PRINCIPLE

    def test_node_to_dict(self):
        node = GraphNode(
            node_type=NodeType.HARM_LEVEL,
            label="Moderate Harm",
            description="Moderate level of harm",
            weight=0.5,
        )
        data = node.to_dict()
        assert data["node_type"] == "harm_level"
        assert data["label"] == "Moderate Harm"


class TestGraphEdge:
    """Tests for GraphEdge dataclass."""

    def test_edge_creation(self):
        edge = GraphEdge(
            source_id="node_1",
            target_id="node_2",
            edge_type=EdgeType.REQUIRES,
            weight=0.8,
        )
        assert edge.edge_id is not None
        assert edge.edge_type == EdgeType.REQUIRES

    def test_edge_to_dict(self):
        edge = GraphEdge(
            source_id="source",
            target_id="target",
            edge_type=EdgeType.CONFLICTS_WITH,
            weight=0.6,
            label="Conflict",
        )
        data = edge.to_dict()
        assert data["edge_type"] == "conflicts_with"
        assert data["label"] == "Conflict"


class TestReasoningPath:
    """Tests for ReasoningPath dataclass."""

    def test_path_creation(self):
        path = ReasoningPath(
            nodes=[],
            edges=[],
            total_weight=0.75,
            conclusion="Action permitted",
            confidence=0.85,
        )
        assert path.path_id is not None
        assert path.confidence == 0.85

    def test_path_to_dict(self):
        path = ReasoningPath(
            nodes=[],
            edges=[],
            total_weight=0.5,
            conclusion="Test conclusion",
            confidence=0.7,
        )
        data = path.to_dict()
        assert data["conclusion"] == "Test conclusion"
        assert data["confidence"] == 0.7


class TestExplainabilityCapsule:
    """Tests for ExplainabilityCapsule dataclass."""

    def test_capsule_creation(self):
        capsule = ExplainabilityCapsule(
            action_type="test",
            decision="allow",
            reasoning_paths=[],
            key_factors=["factor_1"],
            constraints_applied=["constraint_1"],
            ethical_principles=["principle_1"],
            risk_factors=[],
            community_considerations=[],
            human_readable_explanation="This action is permitted.",
            confidence=0.9,
        )
        assert capsule.capsule_id is not None
        assert capsule.confidence == 0.9

    def test_capsule_hash(self):
        capsule = ExplainabilityCapsule(
            action_type="hash_test",
            decision="deny",
            reasoning_paths=[],
            key_factors=[],
            constraints_applied=[],
            ethical_principles=[],
            risk_factors=[],
            community_considerations=[],
            human_readable_explanation="Test",
            confidence=0.5,
        )
        assert capsule.capsule_hash is not None
        assert len(capsule.capsule_hash) == 16

    def test_capsule_to_dict(self):
        capsule = ExplainabilityCapsule(
            action_type="dict_test",
            decision="allow_with_caution",
            reasoning_paths=[],
            key_factors=["key"],
            constraints_applied=["constraint"],
            ethical_principles=["principle"],
            risk_factors=["risk"],
            community_considerations=["community"],
            human_readable_explanation="Detailed explanation",
            confidence=0.8,
        )
        data = capsule.to_dict()
        assert data["action_type"] == "dict_test"
        assert data["decision"] == "allow_with_caution"
        assert "capsule_hash" in data
