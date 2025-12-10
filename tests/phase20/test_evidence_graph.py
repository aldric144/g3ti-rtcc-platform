"""
Phase 20: Evidence Graph Tests

Tests for EvidenceGraphExpander, BehavioralEdgeBuilder,
SimilarityScoreEngine, and UnsolvedCaseLinker.
"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.ada.evidence_graph import (
    EvidenceGraphExpander,
    BehavioralEdgeBuilder,
    SimilarityScoreEngine,
    UnsolvedCaseLinker,
    NodeType,
    EdgeType,
)


class TestEvidenceGraphExpander:
    def setup_method(self):
        self.expander = EvidenceGraphExpander()

    def test_add_node(self):
        node = self.expander.add_node(
            node_type="case",
            label="Case #2024-001",
            case_ids=["case-001"],
            properties={"offense_type": "burglary"},
        )
        assert node is not None
        assert node.node_type == NodeType.CASE
        assert node.label == "Case #2024-001"

    def test_get_node(self):
        node = self.expander.add_node(
            node_type="suspect",
            label="John Doe",
            case_ids=["case-001"],
        )
        retrieved = self.expander.get_node(node.node_id)
        assert retrieved is not None
        assert retrieved.node_id == node.node_id

    def test_add_edge(self):
        node1 = self.expander.add_node(
            node_type="case",
            label="Case #2024-001",
            case_ids=["case-001"],
        )
        node2 = self.expander.add_node(
            node_type="suspect",
            label="Jane Smith",
            case_ids=["case-001"],
        )
        edge = self.expander.add_edge(
            source_id=node1.node_id,
            target_id=node2.node_id,
            edge_type="suspect_link",
            weight=0.85,
        )
        assert edge is not None
        assert edge.edge_type == EdgeType.SUSPECT_LINK

    def test_get_edge(self):
        node1 = self.expander.add_node(
            node_type="evidence",
            label="Knife",
            case_ids=["case-002"],
        )
        node2 = self.expander.add_node(
            node_type="case",
            label="Case #2024-002",
            case_ids=["case-002"],
        )
        edge = self.expander.add_edge(
            source_id=node1.node_id,
            target_id=node2.node_id,
            edge_type="evidence_link",
            weight=1.0,
        )
        retrieved = self.expander.get_edge(edge.edge_id)
        assert retrieved is not None
        assert retrieved.edge_id == edge.edge_id

    def test_expand_from_case(self):
        case_data = {
            "case_id": "case-003",
            "suspects": [{"id": "sus-001", "name": "Test Suspect"}],
            "victims": [{"id": "vic-001", "name": "Test Victim"}],
            "evidence": [{"id": "ev-001", "type": "weapon"}],
        }
        nodes, edges = self.expander.expand_from_case("case-003", case_data)
        assert len(nodes) > 0
        assert isinstance(edges, list)

    def test_get_connected_nodes(self):
        node1 = self.expander.add_node(
            node_type="case",
            label="Case #2024-004",
            case_ids=["case-004"],
        )
        node2 = self.expander.add_node(
            node_type="suspect",
            label="Connected Suspect",
            case_ids=["case-004"],
        )
        self.expander.add_edge(
            source_id=node1.node_id,
            target_id=node2.node_id,
            edge_type="suspect_link",
            weight=0.9,
        )
        connected = self.expander.get_connected_nodes(node1.node_id)
        assert len(connected) > 0

    def test_get_case_subgraph(self):
        self.expander.add_node(
            node_type="case",
            label="Case #2024-005",
            case_ids=["case-005"],
        )
        subgraph = self.expander.get_case_subgraph("case-005")
        assert "nodes" in subgraph
        assert "edges" in subgraph


class TestBehavioralEdgeBuilder:
    def setup_method(self):
        self.expander = EvidenceGraphExpander()
        self.builder = BehavioralEdgeBuilder(self.expander)

    def test_build_behavioral_edge(self):
        node1 = self.expander.add_node(
            node_type="case",
            label="Case #2024-001",
            case_ids=["case-001"],
        )
        node2 = self.expander.add_node(
            node_type="case",
            label="Case #2024-002",
            case_ids=["case-002"],
        )
        edge = self.builder.build_behavioral_edge(
            source_id=node1.node_id,
            target_id=node2.node_id,
            behavior_type="mo_similarity",
            similarity_score=0.75,
        )
        assert edge is not None
        assert edge.edge_type == EdgeType.BEHAVIORAL

    def test_build_temporal_edge(self):
        node1 = self.expander.add_node(
            node_type="case",
            label="Case #2024-003",
            case_ids=["case-003"],
        )
        node2 = self.expander.add_node(
            node_type="case",
            label="Case #2024-004",
            case_ids=["case-004"],
        )
        edge = self.builder.build_temporal_edge(
            source_id=node1.node_id,
            target_id=node2.node_id,
            time_delta_hours=24,
        )
        assert edge is not None
        assert edge.edge_type == EdgeType.TEMPORAL

    def test_build_geographic_edge(self):
        node1 = self.expander.add_node(
            node_type="location",
            label="123 Main St",
            case_ids=["case-005"],
        )
        node2 = self.expander.add_node(
            node_type="location",
            label="125 Main St",
            case_ids=["case-006"],
        )
        edge = self.builder.build_geographic_edge(
            source_id=node1.node_id,
            target_id=node2.node_id,
            distance_meters=50,
        )
        assert edge is not None
        assert edge.edge_type == EdgeType.GEOGRAPHIC

    def test_auto_build_edges(self):
        node1 = self.expander.add_node(
            node_type="case",
            label="Case #2024-007",
            case_ids=["case-007"],
            properties={"offense_type": "burglary", "time": "night"},
        )
        node2 = self.expander.add_node(
            node_type="case",
            label="Case #2024-008",
            case_ids=["case-008"],
            properties={"offense_type": "burglary", "time": "night"},
        )
        edges = self.builder.auto_build_edges([node1.node_id, node2.node_id])
        assert isinstance(edges, list)


class TestSimilarityScoreEngine:
    def setup_method(self):
        self.engine = SimilarityScoreEngine()

    def test_calculate_similarity(self):
        case1_data = {
            "offense_type": "burglary",
            "entry_method": "forced_rear",
            "time_of_day": "night",
            "target_type": "residential",
        }
        case2_data = {
            "offense_type": "burglary",
            "entry_method": "forced_rear",
            "time_of_day": "night",
            "target_type": "residential",
        }
        similarity = self.engine.calculate_similarity(
            case_id_1="case-001",
            case_id_2="case-002",
            case1_data=case1_data,
            case2_data=case2_data,
        )
        assert similarity is not None
        assert similarity.overall_score >= 0
        assert similarity.overall_score <= 1

    def test_get_similarity(self):
        case1_data = {"offense_type": "robbery"}
        case2_data = {"offense_type": "robbery"}
        similarity = self.engine.calculate_similarity(
            case_id_1="case-003",
            case_id_2="case-004",
            case1_data=case1_data,
            case2_data=case2_data,
        )
        retrieved = self.engine.get_similarity(similarity.similarity_id)
        assert retrieved is not None
        assert retrieved.similarity_id == similarity.similarity_id

    def test_similarity_has_factor_scores(self):
        case1_data = {"offense_type": "assault", "weapon": "knife"}
        case2_data = {"offense_type": "assault", "weapon": "knife"}
        similarity = self.engine.calculate_similarity(
            case_id_1="case-005",
            case_id_2="case-006",
            case1_data=case1_data,
            case2_data=case2_data,
        )
        assert hasattr(similarity, "factor_scores")
        assert "behavioral" in similarity.factor_scores

    def test_find_similar_cases(self):
        case_data = {"offense_type": "burglary"}
        similar = self.engine.find_similar_cases(
            case_id="case-007",
            case_data=case_data,
            threshold=0.3,
        )
        assert isinstance(similar, list)

    def test_get_high_similarity_pairs(self):
        case1_data = {"offense_type": "homicide"}
        case2_data = {"offense_type": "homicide"}
        self.engine.calculate_similarity(
            case_id_1="case-008",
            case_id_2="case-009",
            case1_data=case1_data,
            case2_data=case2_data,
        )
        high_pairs = self.engine.get_high_similarity_pairs(threshold=0.5)
        assert isinstance(high_pairs, list)


class TestUnsolvedCaseLinker:
    def setup_method(self):
        self.similarity_engine = SimilarityScoreEngine()
        self.linker = UnsolvedCaseLinker(self.similarity_engine)

    def test_analyze_and_link(self):
        case_ids = ["case-001", "case-002", "case-003"]
        case_data_map = {
            "case-001": {"offense_type": "burglary", "status": "unsolved"},
            "case-002": {"offense_type": "burglary", "status": "unsolved"},
            "case-003": {"offense_type": "burglary", "status": "unsolved"},
        }
        links = self.linker.analyze_and_link(case_ids, case_data_map)
        assert isinstance(links, list)

    def test_get_link(self):
        case_ids = ["case-004", "case-005"]
        case_data_map = {
            "case-004": {"offense_type": "robbery"},
            "case-005": {"offense_type": "robbery"},
        }
        links = self.linker.analyze_and_link(case_ids, case_data_map)
        if links:
            retrieved = self.linker.get_link(links[0].link_id)
            assert retrieved is not None

    def test_confirm_link(self):
        case_ids = ["case-006", "case-007"]
        case_data_map = {
            "case-006": {"offense_type": "assault"},
            "case-007": {"offense_type": "assault"},
        }
        links = self.linker.analyze_and_link(case_ids, case_data_map)
        if links:
            confirmed = self.linker.confirm_link(
                links[0].link_id,
                confirmed_by="Detective Smith",
            )
            assert confirmed is not None
            assert confirmed.confirmed is True

    def test_reject_link(self):
        case_ids = ["case-008", "case-009"]
        case_data_map = {
            "case-008": {"offense_type": "theft"},
            "case-009": {"offense_type": "theft"},
        }
        links = self.linker.analyze_and_link(case_ids, case_data_map)
        if links:
            rejected = self.linker.reject_link(
                links[0].link_id,
                rejected_by="Detective Jones",
                reason="Different MO patterns",
            )
            assert rejected is not None

    def test_get_pending_links(self):
        case_ids = ["case-010", "case-011"]
        case_data_map = {
            "case-010": {"offense_type": "burglary"},
            "case-011": {"offense_type": "burglary"},
        }
        self.linker.analyze_and_link(case_ids, case_data_map)
        pending = self.linker.get_pending_links()
        assert isinstance(pending, list)

    def test_cluster_linked_cases(self):
        case_ids = ["case-012", "case-013", "case-014"]
        case_data_map = {
            "case-012": {"offense_type": "burglary"},
            "case-013": {"offense_type": "burglary"},
            "case-014": {"offense_type": "burglary"},
        }
        self.linker.analyze_and_link(case_ids, case_data_map)
        clusters = self.linker.cluster_linked_cases()
        assert isinstance(clusters, list)
