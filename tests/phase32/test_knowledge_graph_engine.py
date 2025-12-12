"""
Test Suite 2: Knowledge Graph Engine Tests

Tests for Global Knowledge Graph Engine functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestEntityTypes:
    """Tests for entity type enumeration."""

    def test_entity_type_country_exists(self):
        """Test that COUNTRY entity type is defined."""
        from backend.app.global_awareness.knowledge_graph_engine import EntityType
        assert hasattr(EntityType, "COUNTRY")

    def test_entity_type_organization_exists(self):
        """Test that ORGANIZATION entity type is defined."""
        from backend.app.global_awareness.knowledge_graph_engine import EntityType
        assert hasattr(EntityType, "ORGANIZATION")

    def test_entity_type_person_exists(self):
        """Test that PERSON entity type is defined."""
        from backend.app.global_awareness.knowledge_graph_engine import EntityType
        assert hasattr(EntityType, "PERSON")

    def test_entity_type_threat_actor_exists(self):
        """Test that THREAT_ACTOR entity type is defined."""
        from backend.app.global_awareness.knowledge_graph_engine import EntityType
        assert hasattr(EntityType, "THREAT_ACTOR")

    def test_all_ten_entity_types_defined(self):
        """Test that all 10 entity types are defined."""
        from backend.app.global_awareness.knowledge_graph_engine import EntityType
        types = list(EntityType)
        assert len(types) == 10


class TestRelationshipTypes:
    """Tests for relationship type enumeration."""

    def test_relationship_ally_exists(self):
        """Test that ALLY relationship type is defined."""
        from backend.app.global_awareness.knowledge_graph_engine import RelationshipType
        assert hasattr(RelationshipType, "ALLY")

    def test_relationship_adversary_exists(self):
        """Test that ADVERSARY relationship type is defined."""
        from backend.app.global_awareness.knowledge_graph_engine import RelationshipType
        assert hasattr(RelationshipType, "ADVERSARY")

    def test_relationship_member_of_exists(self):
        """Test that MEMBER_OF relationship type is defined."""
        from backend.app.global_awareness.knowledge_graph_engine import RelationshipType
        assert hasattr(RelationshipType, "MEMBER_OF")

    def test_relationship_controls_exists(self):
        """Test that CONTROLS relationship type is defined."""
        from backend.app.global_awareness.knowledge_graph_engine import RelationshipType
        assert hasattr(RelationshipType, "CONTROLS")

    def test_all_sixteen_relationship_types_defined(self):
        """Test that all 16 relationship types are defined."""
        from backend.app.global_awareness.knowledge_graph_engine import RelationshipType
        types = list(RelationshipType)
        assert len(types) == 16


class TestEntity:
    """Tests for Entity data class."""

    def test_entity_creation(self):
        """Test creating an Entity instance."""
        from backend.app.global_awareness.knowledge_graph_engine import Entity, EntityType

        entity = Entity(
            entity_id="ENT-001",
            entity_type=EntityType.COUNTRY,
            name="United States",
            aliases=["USA", "US", "America"],
            attributes={"population": 330000000, "gdp": 25000000000000},
            metadata={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            chain_of_custody_hash="test_hash",
        )

        assert entity.entity_id == "ENT-001"
        assert entity.entity_type == EntityType.COUNTRY
        assert entity.name == "United States"
        assert "USA" in entity.aliases

    def test_entity_has_chain_of_custody(self):
        """Test that Entity includes chain of custody hash."""
        from backend.app.global_awareness.knowledge_graph_engine import Entity, EntityType

        entity = Entity(
            entity_id="ENT-002",
            entity_type=EntityType.ORGANIZATION,
            name="NATO",
            aliases=["North Atlantic Treaty Organization"],
            attributes={},
            metadata={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            chain_of_custody_hash="sha256_hash_value",
        )

        assert entity.chain_of_custody_hash is not None


class TestRelationship:
    """Tests for Relationship data class."""

    def test_relationship_creation(self):
        """Test creating a Relationship instance."""
        from backend.app.global_awareness.knowledge_graph_engine import (
            Relationship,
            RelationshipType,
        )

        relationship = Relationship(
            relationship_id="REL-001",
            source_entity_id="ENT-001",
            target_entity_id="ENT-002",
            relationship_type=RelationshipType.MEMBER_OF,
            strength=0.95,
            attributes={},
            evidence=[],
            created_at=datetime.utcnow(),
            chain_of_custody_hash="test_hash",
        )

        assert relationship.relationship_id == "REL-001"
        assert relationship.relationship_type == RelationshipType.MEMBER_OF
        assert relationship.strength == 0.95


class TestKnowledgeGraphEngine:
    """Tests for KnowledgeGraphEngine class."""

    def test_knowledge_graph_singleton(self):
        """Test that KnowledgeGraphEngine is a singleton."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine1 = KnowledgeGraphEngine()
        engine2 = KnowledgeGraphEngine()
        assert engine1 is engine2

    def test_knowledge_graph_has_entities_storage(self):
        """Test that knowledge graph has entities storage."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        assert hasattr(engine, "entities")

    def test_knowledge_graph_has_relationships_storage(self):
        """Test that knowledge graph has relationships storage."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        assert hasattr(engine, "relationships")

    def test_knowledge_graph_has_base_entities(self):
        """Test that knowledge graph initializes with base entities."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        assert len(engine.entities) > 0


class TestEntityOperations:
    """Tests for entity CRUD operations."""

    def test_create_entity(self):
        """Test creating a new entity."""
        from backend.app.global_awareness.knowledge_graph_engine import (
            KnowledgeGraphEngine,
            EntityType,
        )

        engine = KnowledgeGraphEngine()
        entity = engine.create_entity(
            entity_type=EntityType.ORGANIZATION,
            name="Test Organization",
            aliases=["Test Org"],
            attributes={"founded": 2020},
        )

        assert entity is not None
        assert entity.entity_id.startswith("ENT-")
        assert entity.name == "Test Organization"

    def test_get_entity_by_id(self):
        """Test retrieving entity by ID."""
        from backend.app.global_awareness.knowledge_graph_engine import (
            KnowledgeGraphEngine,
            EntityType,
        )

        engine = KnowledgeGraphEngine()
        created = engine.create_entity(
            entity_type=EntityType.PERSON,
            name="Test Person",
            aliases=[],
            attributes={},
        )

        retrieved = engine.get_entity(created.entity_id)
        assert retrieved is not None
        assert retrieved.entity_id == created.entity_id

    def test_get_entity_by_name(self):
        """Test retrieving entity by name."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        entity = engine.get_entity_by_name("United States")
        assert entity is not None

    def test_get_entity_by_alias(self):
        """Test retrieving entity by alias."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        entity = engine.get_entity_by_alias("USA")
        assert entity is not None
        assert entity.name == "United States"


class TestRelationshipOperations:
    """Tests for relationship operations."""

    def test_create_relationship(self):
        """Test creating a new relationship."""
        from backend.app.global_awareness.knowledge_graph_engine import (
            KnowledgeGraphEngine,
            RelationshipType,
        )

        engine = KnowledgeGraphEngine()
        usa = engine.get_entity_by_name("United States")
        nato = engine.get_entity_by_name("NATO")

        if usa and nato:
            relationship = engine.create_relationship(
                source_entity_id=usa.entity_id,
                target_entity_id=nato.entity_id,
                relationship_type=RelationshipType.MEMBER_OF,
                strength=1.0,
                attributes={},
                evidence=["Treaty of Washington 1949"],
            )

            assert relationship is not None
            assert relationship.relationship_id.startswith("REL-")

    def test_get_relationships_for_entity(self):
        """Test getting relationships for an entity."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        usa = engine.get_entity_by_name("United States")

        if usa:
            relationships = engine.get_relationships_for_entity(usa.entity_id)
            assert isinstance(relationships, list)


class TestInfluenceScoring:
    """Tests for influence scoring."""

    def test_calculate_influence_score(self):
        """Test calculating influence score for an entity."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        usa = engine.get_entity_by_name("United States")

        if usa:
            score = engine.calculate_influence_score(usa.entity_id)
            assert score is not None
            assert hasattr(score, "overall_score")
            assert 0 <= score.overall_score <= 100


class TestCausalInference:
    """Tests for causal inference."""

    def test_create_causal_link(self):
        """Test creating a causal link."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        link = engine.create_causal_link(
            cause_entity_id="ENT-001",
            effect_entity_id="ENT-002",
            mechanism="Economic sanctions",
            strength=0.75,
            time_lag_days=30,
            evidence=["Historical precedent"],
        )

        assert link is not None
        assert link.strength == 0.75

    def test_infer_causal_chain(self):
        """Test inferring causal chain."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        usa = engine.get_entity_by_name("United States")

        if usa:
            chain = engine.infer_causal_chain(usa.entity_id, max_depth=3)
            assert isinstance(chain, list)


class TestEntityNetwork:
    """Tests for entity network analysis."""

    def test_get_entity_network(self):
        """Test getting entity network."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        usa = engine.get_entity_by_name("United States")

        if usa:
            network = engine.get_entity_network(usa.entity_id, depth=2)
            assert "entities" in network
            assert "relationships" in network

    def test_search_entities(self):
        """Test searching entities."""
        from backend.app.global_awareness.knowledge_graph_engine import KnowledgeGraphEngine

        engine = KnowledgeGraphEngine()
        results = engine.search_entities("United")
        assert isinstance(results, list)
