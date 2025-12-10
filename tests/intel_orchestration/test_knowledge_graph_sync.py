"""Tests for the Knowledge Graph Sync module."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.intel_orchestration.knowledge_graph_sync import (
    SyncOperation,
    NodeType,
    RelationshipType,
    GraphSyncConfig,
    GraphNode,
    GraphRelationship,
    SyncResult,
    SyncMetrics,
    KnowledgeGraphSync,
)


class TestSyncOperation:
    """Tests for SyncOperation enum."""

    def test_all_operations_defined(self):
        """Test all sync operations are defined."""
        expected_ops = [
            "CREATE_NODE", "UPDATE_NODE", "DELETE_NODE",
            "CREATE_RELATIONSHIP", "UPDATE_RELATIONSHIP", "DELETE_RELATIONSHIP",
            "MERGE_NODE", "MERGE_RELATIONSHIP",
        ]
        
        for op in expected_ops:
            assert hasattr(SyncOperation, op)


class TestNodeType:
    """Tests for NodeType enum."""

    def test_all_node_types_defined(self):
        """Test all node types are defined."""
        expected_types = [
            "PERSON", "VEHICLE", "WEAPON", "INCIDENT", "LOCATION",
            "PATTERN", "ORGANIZATION", "CASE", "ALERT", "INTELLIGENCE",
        ]
        
        for ntype in expected_types:
            assert hasattr(NodeType, ntype)


class TestRelationshipType:
    """Tests for RelationshipType enum."""

    def test_all_relationship_types_defined(self):
        """Test all relationship types are defined."""
        expected_types = [
            "OWNS", "DRIVES", "POSSESSES", "INVOLVED_IN", "LOCATED_AT",
            "ASSOCIATED_WITH", "RELATED_TO", "CORRELATED_WITH",
            "PART_OF", "GENERATED",
        ]
        
        for rtype in expected_types:
            assert hasattr(RelationshipType, rtype)


class TestGraphSyncConfig:
    """Tests for GraphSyncConfig model."""

    def test_default_config(self):
        """Test default graph sync configuration."""
        config = GraphSyncConfig()
        
        assert config.enabled is True
        assert config.batch_size == 100
        assert config.flush_interval_seconds == 5.0

    def test_custom_config(self):
        """Test custom graph sync configuration."""
        config = GraphSyncConfig(
            enabled=False,
            batch_size=50,
            neo4j_uri="bolt://custom:7687",
        )
        
        assert config.enabled is False
        assert config.batch_size == 50


class TestGraphNode:
    """Tests for GraphNode model."""

    def test_node_creation(self):
        """Test creating a graph node."""
        node = GraphNode(
            node_id="person-123",
            node_type=NodeType.PERSON,
            properties={"name": "John Doe", "dob": "1985-03-15"},
        )
        
        assert node.node_id == "person-123"
        assert node.node_type == NodeType.PERSON
        assert node.properties["name"] == "John Doe"

    def test_node_with_labels(self):
        """Test node with additional labels."""
        node = GraphNode(
            node_id="person-456",
            node_type=NodeType.PERSON,
            properties={},
            labels=["Suspect", "HighRisk"],
        )
        
        assert "Suspect" in node.labels
        assert "HighRisk" in node.labels


class TestGraphRelationship:
    """Tests for GraphRelationship model."""

    def test_relationship_creation(self):
        """Test creating a graph relationship."""
        rel = GraphRelationship(
            source_id="person-123",
            target_id="vehicle-456",
            relationship_type=RelationshipType.OWNS,
            properties={"since": "2020-01-01"},
        )
        
        assert rel.source_id == "person-123"
        assert rel.target_id == "vehicle-456"
        assert rel.relationship_type == RelationshipType.OWNS

    def test_relationship_with_confidence(self):
        """Test relationship with confidence score."""
        rel = GraphRelationship(
            source_id="person-123",
            target_id="incident-789",
            relationship_type=RelationshipType.INVOLVED_IN,
            properties={"confidence": 0.85, "role": "suspect"},
        )
        
        assert rel.properties["confidence"] == 0.85


class TestSyncResult:
    """Tests for SyncResult model."""

    def test_result_creation(self):
        """Test creating a sync result."""
        result = SyncResult(
            operation=SyncOperation.CREATE_NODE,
            success=True,
            node_id="person-123",
        )
        
        assert result.operation == SyncOperation.CREATE_NODE
        assert result.success is True

    def test_failed_result(self):
        """Test failed sync result."""
        result = SyncResult(
            operation=SyncOperation.CREATE_NODE,
            success=False,
            error_message="Connection refused",
        )
        
        assert result.success is False
        assert result.error_message == "Connection refused"


class TestSyncMetrics:
    """Tests for SyncMetrics model."""

    def test_default_metrics(self):
        """Test default sync metrics."""
        metrics = SyncMetrics()
        
        assert metrics.nodes_created == 0
        assert metrics.nodes_updated == 0
        assert metrics.relationships_created == 0
        assert metrics.sync_errors == 0

    def test_metrics_update(self):
        """Test updating metrics."""
        metrics = SyncMetrics()
        metrics.nodes_created = 100
        metrics.relationships_created = 50
        
        assert metrics.nodes_created == 100
        assert metrics.relationships_created == 50


class TestKnowledgeGraphSync:
    """Tests for KnowledgeGraphSync class."""

    def test_sync_initialization(self):
        """Test knowledge graph sync initialization."""
        sync = KnowledgeGraphSync()
        
        assert sync.config is not None
        assert sync.metrics is not None

    def test_sync_with_custom_config(self):
        """Test sync with custom config."""
        config = GraphSyncConfig(
            batch_size=200,
        )
        sync = KnowledgeGraphSync(config=config)
        
        assert sync.config.batch_size == 200

    @pytest.mark.asyncio
    async def test_sync_start_stop(self):
        """Test starting and stopping sync service."""
        sync = KnowledgeGraphSync()
        
        await sync.start()
        assert sync._running is True
        
        await sync.stop()
        assert sync._running is False

    @pytest.mark.asyncio
    async def test_sync_node(self):
        """Test syncing a node."""
        sync = KnowledgeGraphSync()
        await sync.start()
        
        node = GraphNode(
            node_id="person-123",
            node_type=NodeType.PERSON,
            properties={"name": "John Doe"},
        )
        
        result = await sync.sync_node(node)
        
        assert result is not None
        
        await sync.stop()

    @pytest.mark.asyncio
    async def test_sync_relationship(self):
        """Test syncing a relationship."""
        sync = KnowledgeGraphSync()
        await sync.start()
        
        rel = GraphRelationship(
            source_id="person-123",
            target_id="vehicle-456",
            relationship_type=RelationshipType.OWNS,
            properties={},
        )
        
        result = await sync.sync_relationship(rel)
        
        assert result is not None
        
        await sync.stop()

    @pytest.mark.asyncio
    async def test_sync_intelligence(self):
        """Test syncing fused intelligence."""
        sync = KnowledgeGraphSync()
        await sync.start()
        
        intelligence = {
            "id": "intel-123",
            "tier": "tier2",
            "title": "Pattern Match",
            "entities": [
                {"type": "person", "id": "person-123"},
                {"type": "vehicle", "id": "vehicle-456"},
            ],
            "correlations": [
                {"source": "person-123", "target": "vehicle-456", "type": "owns"},
            ],
        }
        
        results = await sync.sync_intelligence(intelligence)
        
        assert results is not None
        
        await sync.stop()

    @pytest.mark.asyncio
    async def test_sync_correlation(self):
        """Test syncing a correlation."""
        sync = KnowledgeGraphSync()
        await sync.start()
        
        correlation = {
            "source_entity": {"id": "person-123", "type": "person"},
            "target_entity": {"id": "vehicle-456", "type": "vehicle"},
            "correlation_type": "ownership",
            "confidence": 0.95,
        }
        
        result = await sync.sync_correlation(correlation)
        
        assert result is not None
        
        await sync.stop()

    @pytest.mark.asyncio
    async def test_batch_sync(self):
        """Test batch syncing."""
        sync = KnowledgeGraphSync()
        await sync.start()
        
        nodes = [
            GraphNode(
                node_id=f"person-{i}",
                node_type=NodeType.PERSON,
                properties={"index": i},
            )
            for i in range(5)
        ]
        
        results = await sync.batch_sync_nodes(nodes)
        
        assert len(results) == 5
        
        await sync.stop()

    @pytest.mark.asyncio
    async def test_extract_entities(self):
        """Test entity extraction from intelligence."""
        sync = KnowledgeGraphSync()
        
        intelligence = {
            "entities": [
                {"type": "person", "id": "p-1", "name": "John"},
                {"type": "vehicle", "id": "v-1", "plate": "ABC123"},
            ],
        }
        
        nodes = sync.extract_entities(intelligence)
        
        assert len(nodes) == 2

    @pytest.mark.asyncio
    async def test_infer_relationships(self):
        """Test relationship inference."""
        sync = KnowledgeGraphSync()
        
        intelligence = {
            "entities": [
                {"type": "person", "id": "p-1"},
                {"type": "location", "id": "loc-1"},
            ],
        }
        
        relationships = sync.infer_relationships(intelligence)
        
        # Should infer LOCATED_AT relationship
        assert relationships is not None

    def test_generate_cypher_create_node(self):
        """Test Cypher query generation for node creation."""
        sync = KnowledgeGraphSync()
        
        node = GraphNode(
            node_id="person-123",
            node_type=NodeType.PERSON,
            properties={"name": "John Doe"},
        )
        
        cypher = sync.generate_cypher(SyncOperation.CREATE_NODE, node=node)
        
        assert "MERGE" in cypher or "CREATE" in cypher
        assert "Person" in cypher

    def test_generate_cypher_create_relationship(self):
        """Test Cypher query generation for relationship creation."""
        sync = KnowledgeGraphSync()
        
        rel = GraphRelationship(
            source_id="person-123",
            target_id="vehicle-456",
            relationship_type=RelationshipType.OWNS,
            properties={},
        )
        
        cypher = sync.generate_cypher(SyncOperation.CREATE_RELATIONSHIP, relationship=rel)
        
        assert "MATCH" in cypher
        assert "OWNS" in cypher

    def test_get_status(self):
        """Test getting sync status."""
        sync = KnowledgeGraphSync()
        status = sync.get_status()
        
        assert "running" in status
        assert "metrics" in status
        assert "config" in status

    def test_get_metrics(self):
        """Test getting sync metrics."""
        sync = KnowledgeGraphSync()
        metrics = sync.get_metrics()
        
        assert isinstance(metrics, SyncMetrics)

    @pytest.mark.asyncio
    async def test_node_caching(self):
        """Test node caching."""
        sync = KnowledgeGraphSync()
        await sync.start()
        
        node = GraphNode(
            node_id="person-123",
            node_type=NodeType.PERSON,
            properties={},
        )
        
        await sync.sync_node(node)
        
        # Node should be cached
        cached = sync.get_cached_node("person-123")
        assert cached is not None
        
        await sync.stop()

    @pytest.mark.asyncio
    async def test_clear_cache(self):
        """Test clearing cache."""
        sync = KnowledgeGraphSync()
        await sync.start()
        
        node = GraphNode(
            node_id="person-123",
            node_type=NodeType.PERSON,
            properties={},
        )
        
        await sync.sync_node(node)
        await sync.clear_cache()
        
        stats = sync.get_status()
        assert stats["nodes_cached"] == 0
        
        await sync.stop()
