"""
Tests for Extremist Networks module.

Phase 17: Global Threat Intelligence Engine
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.threat_intel.extremist_networks import (
    ExtremistNetworkAnalyzer,
    NodeType,
    IdeologyType,
    ThreatLevel,
    ActivityLevel,
    RadicalizationStage,
    NetworkNode,
    NetworkEdge,
    NetworkCluster,
    InfluenceScore,
    RadicalizationTrajectory,
)


class TestExtremistNetworkAnalyzer:
    """Test suite for ExtremistNetworkAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create an ExtremistNetworkAnalyzer instance for testing."""
        return ExtremistNetworkAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly."""
        assert analyzer is not None
        assert isinstance(analyzer.nodes, dict)
        assert isinstance(analyzer.edges, dict)
        assert isinstance(analyzer.clusters, dict)

    def test_add_node(self, analyzer):
        """Test adding a network node."""
        node = analyzer.add_node(
            name="Test Subject",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.MODERATE,
        )
        
        assert node is not None
        assert node.name == "Test Subject"
        assert node.node_type == NodeType.INDIVIDUAL
        assert node.ideology == IdeologyType.MILITIA
        assert node.node_id in analyzer.nodes

    def test_add_node_with_details(self, analyzer):
        """Test adding a node with additional details."""
        node = analyzer.add_node(
            name="Extremist Channel",
            node_type=NodeType.CHANNEL,
            ideology=IdeologyType.WHITE_SUPREMACIST,
            threat_level=ThreatLevel.HIGH,
            platform="Telegram",
            follower_count=5000,
            description="Known extremist channel",
        )
        
        assert node is not None
        assert node.platform == "Telegram"
        assert node.follower_count == 5000

    def test_get_node(self, analyzer):
        """Test retrieving a node by ID."""
        node = analyzer.add_node(
            name="Test Node",
            node_type=NodeType.GROUP,
            ideology=IdeologyType.ANTI_GOVERNMENT,
            threat_level=ThreatLevel.LOW,
        )
        
        retrieved = analyzer.get_node(node.node_id)
        assert retrieved is not None
        assert retrieved.node_id == node.node_id

    def test_get_nodes(self, analyzer):
        """Test retrieving all nodes."""
        analyzer.add_node(
            name="Node 1",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.LOW,
        )
        analyzer.add_node(
            name="Node 2",
            node_type=NodeType.GROUP,
            ideology=IdeologyType.ANARCHIST,
            threat_level=ThreatLevel.MODERATE,
        )
        
        nodes = analyzer.get_nodes()
        assert len(nodes) >= 2

    def test_get_nodes_by_type(self, analyzer):
        """Test retrieving nodes by type."""
        analyzer.add_node(
            name="Individual",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.OTHER,
            threat_level=ThreatLevel.LOW,
        )
        
        nodes = analyzer.get_nodes(node_type=NodeType.INDIVIDUAL)
        for node in nodes:
            assert node.node_type == NodeType.INDIVIDUAL

    def test_get_nodes_by_ideology(self, analyzer):
        """Test retrieving nodes by ideology."""
        analyzer.add_node(
            name="Militia Member",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.MODERATE,
        )
        
        nodes = analyzer.get_nodes(ideology=IdeologyType.MILITIA)
        for node in nodes:
            assert node.ideology == IdeologyType.MILITIA

    def test_add_edge(self, analyzer):
        """Test adding an edge between nodes."""
        node1 = analyzer.add_node(
            name="Node 1",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.LOW,
        )
        node2 = analyzer.add_node(
            name="Node 2",
            node_type=NodeType.GROUP,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.MODERATE,
        )
        
        edge = analyzer.add_edge(
            source_node_id=node1.node_id,
            target_node_id=node2.node_id,
            relationship_type="member_of",
            confidence=0.9,
        )
        
        assert edge is not None
        assert edge.source_node_id == node1.node_id
        assert edge.target_node_id == node2.node_id
        assert edge.relationship_type == "member_of"

    def test_get_connected_nodes(self, analyzer):
        """Test getting connected nodes."""
        node1 = analyzer.add_node(
            name="Central Node",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.HIGH,
        )
        node2 = analyzer.add_node(
            name="Connected Node",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.LOW,
        )
        
        analyzer.add_edge(
            source_node_id=node1.node_id,
            target_node_id=node2.node_id,
            relationship_type="associate",
            confidence=0.8,
        )
        
        connected = analyzer.get_connected_nodes(node1.node_id)
        assert isinstance(connected, list)

    def test_calculate_influence_score(self, analyzer):
        """Test calculating influence score for a node."""
        node = analyzer.add_node(
            name="Influencer",
            node_type=NodeType.CHANNEL,
            ideology=IdeologyType.WHITE_SUPREMACIST,
            threat_level=ThreatLevel.HIGH,
            follower_count=10000,
        )
        
        for i in range(5):
            connected = analyzer.add_node(
                name=f"Follower {i}",
                node_type=NodeType.INDIVIDUAL,
                ideology=IdeologyType.WHITE_SUPREMACIST,
                threat_level=ThreatLevel.LOW,
            )
            analyzer.add_edge(
                source_node_id=node.node_id,
                target_node_id=connected.node_id,
                relationship_type="influences",
                confidence=0.7,
            )
        
        score = analyzer.calculate_influence_score(node.node_id)
        assert score is not None
        assert score.overall_score >= 0

    def test_analyze_radicalization_trajectory(self, analyzer):
        """Test analyzing radicalization trajectory."""
        node = analyzer.add_node(
            name="Subject",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.ACCELERATIONIST,
            threat_level=ThreatLevel.HIGH,
            activity_level=ActivityLevel.VERY_HIGH,
        )
        
        trajectory = analyzer.analyze_radicalization_trajectory(node.node_id)
        assert trajectory is not None
        assert trajectory.node_id == node.node_id
        assert trajectory.current_stage is not None

    def test_create_cluster(self, analyzer):
        """Test creating a network cluster."""
        nodes = []
        for i in range(3):
            node = analyzer.add_node(
                name=f"Cluster Member {i}",
                node_type=NodeType.INDIVIDUAL,
                ideology=IdeologyType.MILITIA,
                threat_level=ThreatLevel.MODERATE,
            )
            nodes.append(node.node_id)
        
        cluster = analyzer.create_cluster(
            name="Test Cluster",
            node_ids=nodes,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.MODERATE,
        )
        
        assert cluster is not None
        assert cluster.name == "Test Cluster"
        assert len(cluster.node_ids) == 3

    def test_get_clusters(self, analyzer):
        """Test retrieving clusters."""
        node = analyzer.add_node(
            name="Test",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.OTHER,
            threat_level=ThreatLevel.LOW,
        )
        
        analyzer.create_cluster(
            name="Cluster 1",
            node_ids=[node.node_id],
            ideology=IdeologyType.OTHER,
            threat_level=ThreatLevel.LOW,
        )
        
        clusters = analyzer.get_clusters()
        assert isinstance(clusters, list)

    def test_detect_clusters(self, analyzer):
        """Test automatic cluster detection."""
        for i in range(5):
            node = analyzer.add_node(
                name=f"Node {i}",
                node_type=NodeType.INDIVIDUAL,
                ideology=IdeologyType.MILITIA,
                threat_level=ThreatLevel.MODERATE,
            )
        
        detected = analyzer.detect_clusters()
        assert isinstance(detected, list)

    def test_get_high_risk_nodes(self, analyzer):
        """Test retrieving high risk nodes."""
        analyzer.add_node(
            name="High Risk",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.ACCELERATIONIST,
            threat_level=ThreatLevel.SEVERE,
            activity_level=ActivityLevel.VERY_HIGH,
        )
        analyzer.add_node(
            name="Low Risk",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.OTHER,
            threat_level=ThreatLevel.LOW,
            activity_level=ActivityLevel.LOW,
        )
        
        high_risk = analyzer.get_high_risk_nodes()
        for node in high_risk:
            assert node.threat_level.value >= ThreatLevel.HIGH.value

    def test_get_top_influencers(self, analyzer):
        """Test retrieving top influencers."""
        for i in range(5):
            analyzer.add_node(
                name=f"Influencer {i}",
                node_type=NodeType.CHANNEL,
                ideology=IdeologyType.WHITE_SUPREMACIST,
                threat_level=ThreatLevel.MODERATE,
                follower_count=1000 * (i + 1),
            )
        
        influencers = analyzer.get_top_influencers(limit=3)
        assert len(influencers) <= 3

    def test_export_network_graph(self, analyzer):
        """Test exporting network graph."""
        node1 = analyzer.add_node(
            name="Node 1",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.LOW,
        )
        node2 = analyzer.add_node(
            name="Node 2",
            node_type=NodeType.GROUP,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.MODERATE,
        )
        analyzer.add_edge(
            source_node_id=node1.node_id,
            target_node_id=node2.node_id,
            relationship_type="member_of",
            confidence=0.9,
        )
        
        graph = analyzer.export_network_graph()
        assert isinstance(graph, dict)
        assert "nodes" in graph
        assert "edges" in graph

    def test_get_metrics(self, analyzer):
        """Test retrieving metrics."""
        metrics = analyzer.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_nodes" in metrics
        assert "total_edges" in metrics
        assert "total_clusters" in metrics


class TestNetworkNode:
    """Test suite for NetworkNode dataclass."""

    def test_node_creation(self):
        """Test creating a NetworkNode."""
        node = NetworkNode(
            node_id="node-123",
            name="Test Node",
            node_type=NodeType.INDIVIDUAL,
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.MODERATE,
            activity_level=ActivityLevel.MODERATE,
            platform=None,
            follower_count=0,
            description="Test description",
            aliases=[],
            known_locations=[],
            is_monitored=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={},
        )
        
        assert node.node_id == "node-123"
        assert node.name == "Test Node"
        assert node.node_type == NodeType.INDIVIDUAL


class TestNetworkEdge:
    """Test suite for NetworkEdge dataclass."""

    def test_edge_creation(self):
        """Test creating a NetworkEdge."""
        edge = NetworkEdge(
            edge_id="edge-123",
            source_node_id="node-1",
            target_node_id="node-2",
            relationship_type="associate",
            confidence=0.85,
            first_observed=datetime.utcnow(),
            last_observed=datetime.utcnow(),
            evidence=[],
            metadata={},
        )
        
        assert edge.edge_id == "edge-123"
        assert edge.source_node_id == "node-1"
        assert edge.confidence == 0.85


class TestNetworkCluster:
    """Test suite for NetworkCluster dataclass."""

    def test_cluster_creation(self):
        """Test creating a NetworkCluster."""
        cluster = NetworkCluster(
            cluster_id="clust-123",
            name="Test Cluster",
            node_ids=["node-1", "node-2"],
            ideology=IdeologyType.MILITIA,
            threat_level=ThreatLevel.MODERATE,
            total_influence=100.0,
            created_at=datetime.utcnow(),
            metadata={},
        )
        
        assert cluster.cluster_id == "clust-123"
        assert cluster.name == "Test Cluster"
        assert len(cluster.node_ids) == 2


class TestInfluenceScore:
    """Test suite for InfluenceScore dataclass."""

    def test_influence_score_creation(self):
        """Test creating an InfluenceScore."""
        score = InfluenceScore(
            node_id="node-123",
            overall_score=75.0,
            reach_score=80.0,
            engagement_score=70.0,
            authority_score=75.0,
            network_centrality=0.65,
            calculated_at=datetime.utcnow(),
        )
        
        assert score.node_id == "node-123"
        assert score.overall_score == 75.0


class TestRadicalizationTrajectory:
    """Test suite for RadicalizationTrajectory dataclass."""

    def test_trajectory_creation(self):
        """Test creating a RadicalizationTrajectory."""
        trajectory = RadicalizationTrajectory(
            node_id="node-123",
            current_stage=RadicalizationStage.INDOCTRINATION,
            stage_history=[
                RadicalizationStage.PRE_RADICALIZATION,
                RadicalizationStage.SELF_IDENTIFICATION,
                RadicalizationStage.INDOCTRINATION,
            ],
            risk_score=78.0,
            velocity=2.5,
            predicted_next_stage=RadicalizationStage.ACTION,
            intervention_recommended=True,
            analyzed_at=datetime.utcnow(),
        )
        
        assert trajectory.node_id == "node-123"
        assert trajectory.current_stage == RadicalizationStage.INDOCTRINATION
        assert trajectory.intervention_recommended is True
