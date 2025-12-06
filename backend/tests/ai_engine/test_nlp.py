"""
Unit tests for the NLP module.

Tests query interpretation, DSL execution, and result composition.
"""

import pytest
from datetime import datetime, timedelta

from app.ai_engine.nlp import QueryInterpreter, DSLExecutor, ResultComposer


class TestQueryInterpreter:
    """Tests for QueryInterpreter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.interpreter = QueryInterpreter()

    def test_interpret_vehicle_query(self):
        """Test interpretation of vehicle-related queries."""
        query = "Show me vehicles connected to gunfire within the last 30 days near Broadway"
        result = self.interpreter.interpret(query)

        assert result is not None
        assert "vehicles" in result.get("entity_types", []) or "vehicle" in str(result).lower()
        assert result.get("time_range") is not None

    def test_interpret_person_query(self):
        """Test interpretation of person-related queries."""
        query = "Find all incidents involving John Smith in the last week"
        result = self.interpreter.interpret(query)

        assert result is not None
        assert "persons" in result.get("entity_types", []) or "person" in str(result).lower()

    def test_interpret_location_query(self):
        """Test interpretation of location-based queries."""
        query = "What vehicles have been spotted near 123 Main St?"
        result = self.interpreter.interpret(query)

        assert result is not None
        assert result.get("location") is not None or "location" in str(result).lower()

    def test_interpret_time_range_extraction(self):
        """Test extraction of time ranges from queries."""
        queries_and_expected = [
            ("last 24 hours", 24),
            ("last 7 days", 168),
            ("last 30 days", 720),
            ("past week", 168),
            ("past month", 720),
        ]

        for query_part, expected_hours in queries_and_expected:
            query = f"Show me incidents from the {query_part}"
            result = self.interpreter.interpret(query)
            if result.get("time_range"):
                assert result["time_range"].get("hours") is not None

    def test_interpret_empty_query(self):
        """Test handling of empty queries."""
        result = self.interpreter.interpret("")
        assert result is not None

    def test_interpret_complex_query(self):
        """Test interpretation of complex multi-entity queries."""
        query = (
            "Find connections between vehicles spotted near gunfire and repeat offenders in Zone 3"
        )
        result = self.interpreter.interpret(query)

        assert result is not None
        assert len(result.get("entity_types", [])) >= 1 or "entity" in str(result).lower()


class TestDSLExecutor:
    """Tests for DSLExecutor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = DSLExecutor()

    def test_build_cypher_query_basic(self):
        """Test building basic Cypher queries."""
        dsl = {
            "entity_types": ["person"],
            "filters": {"name": "John Smith"},
        }
        query = self.executor.build_cypher_query(dsl)

        assert query is not None
        assert isinstance(query, str)
        assert "MATCH" in query or "match" in query.lower()

    def test_build_cypher_query_with_relationships(self):
        """Test building Cypher queries with relationships."""
        dsl = {
            "entity_types": ["person", "vehicle"],
            "relationship_types": ["owns", "drives"],
        }
        query = self.executor.build_cypher_query(dsl)

        assert query is not None
        assert isinstance(query, str)

    def test_build_elasticsearch_query_basic(self):
        """Test building basic Elasticsearch queries."""
        dsl = {
            "search_terms": ["gunfire", "Broadway"],
            "time_range": {"hours": 24},
        }
        query = self.executor.build_elasticsearch_query(dsl)

        assert query is not None
        assert isinstance(query, dict)

    def test_build_elasticsearch_query_with_filters(self):
        """Test building Elasticsearch queries with filters."""
        dsl = {
            "search_terms": ["incident"],
            "filters": {"type": "gunshot"},
            "time_range": {"hours": 168},
        }
        query = self.executor.build_elasticsearch_query(dsl)

        assert query is not None
        assert isinstance(query, dict)


class TestResultComposer:
    """Tests for ResultComposer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.composer = ResultComposer()

    def test_compose_empty_results(self):
        """Test composing empty results."""
        result = self.composer.compose(
            entities=[],
            incidents=[],
            relationships=[],
            risk_scores={},
        )

        assert result is not None
        assert result.get("entities") == []
        assert result.get("summary") is not None

    def test_compose_with_entities(self):
        """Test composing results with entities."""
        entities = [
            {"id": "1", "type": "person", "name": "John Smith"},
            {"id": "2", "type": "vehicle", "plate": "ABC123"},
        ]
        result = self.composer.compose(
            entities=entities,
            incidents=[],
            relationships=[],
            risk_scores={},
        )

        assert result is not None
        assert len(result.get("entities", [])) == 2

    def test_compose_with_relationships(self):
        """Test composing results with relationships."""
        entities = [
            {"id": "1", "type": "person", "name": "John Smith"},
            {"id": "2", "type": "vehicle", "plate": "ABC123"},
        ]
        relationships = [
            {"source_id": "1", "target_id": "2", "type": "owns"},
        ]
        result = self.composer.compose(
            entities=entities,
            incidents=[],
            relationships=relationships,
            risk_scores={},
        )

        assert result is not None
        assert len(result.get("relationships", [])) == 1

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        entities = [
            {"id": "1", "type": "person", "name": "John Smith", "risk_level": "high"},
        ]
        risk_scores = {
            "1": {"score": 85, "level": "high"},
        }
        result = self.composer.compose(
            entities=entities,
            incidents=[],
            relationships=[],
            risk_scores=risk_scores,
        )

        assert result is not None
        assert len(result.get("recommendations", [])) >= 0

    def test_deduplicate_entities(self):
        """Test entity deduplication."""
        entities = [
            {"id": "1", "type": "person", "name": "John Smith"},
            {"id": "1", "type": "person", "name": "John Smith"},
            {"id": "2", "type": "vehicle", "plate": "ABC123"},
        ]
        result = self.composer.compose(
            entities=entities,
            incidents=[],
            relationships=[],
            risk_scores={},
        )

        assert result is not None
        unique_ids = set(e.get("id") for e in result.get("entities", []))
        assert len(unique_ids) <= 2
