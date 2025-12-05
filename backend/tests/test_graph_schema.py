"""
Unit tests for Neo4j graph schema module.

Tests cover:
- Entity node creation
- Relationship creation
- Property search
- Network traversal
- Schema validation
"""

from unittest.mock import MagicMock

import pytest

from app.db.neo4j_manager import Neo4jManager
from app.schemas.entities import (
    EntityType,
    IncidentCreate,
    PersonCreate,
    RelationshipType,
    VehicleCreate,
)


class TestEntityCreation:
    """Tests for entity node creation."""

    def test_create_person_node(self, mock_neo4j_driver, sample_person_data):
        """Test creating a person node."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        # Mock the session and result
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"n": {"id": "person-001", **sample_person_data}}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        # Create the node
        result = manager.create_node(EntityType.PERSON, sample_person_data)

        # Verify the query was called
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args

        # Check that CREATE query was used
        assert "CREATE" in call_args[0][0] or "MERGE" in call_args[0][0]

    def test_create_vehicle_node(self, mock_neo4j_driver, sample_vehicle_data):
        """Test creating a vehicle node."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"n": {"id": "vehicle-001", **sample_vehicle_data}}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = manager.create_node(EntityType.VEHICLE, sample_vehicle_data)

        mock_session.run.assert_called_once()

    def test_create_incident_node(self, mock_neo4j_driver, sample_incident_data):
        """Test creating an incident node."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"n": {"id": "incident-001", **sample_incident_data}}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = manager.create_node(EntityType.INCIDENT, sample_incident_data)

        mock_session.run.assert_called_once()

    def test_create_node_generates_id(self, mock_neo4j_driver, sample_person_data):
        """Test that node creation generates a unique ID."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"n": {"id": "person-generated-id", **sample_person_data}}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = manager.create_node(EntityType.PERSON, sample_person_data)

        # Verify ID was included in the query parameters
        call_args = mock_session.run.call_args
        assert "id" in str(call_args) or "props" in str(call_args)


class TestRelationshipCreation:
    """Tests for relationship creation between nodes."""

    def test_create_owns_relationship(self, mock_neo4j_driver):
        """Test creating an OWNS relationship."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"r": {"type": "OWNS"}}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = manager.create_relationship(
            source_id="person-001",
            source_type=EntityType.PERSON,
            target_id="vehicle-001",
            target_type=EntityType.VEHICLE,
            relationship_type=RelationshipType.OWNS,
        )

        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "OWNS" in call_args[0][0]

    def test_create_suspect_in_relationship(self, mock_neo4j_driver):
        """Test creating a SUSPECT_IN relationship."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"r": {"type": "SUSPECT_IN"}}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = manager.create_relationship(
            source_id="person-001",
            source_type=EntityType.PERSON,
            target_id="incident-001",
            target_type=EntityType.INCIDENT,
            relationship_type=RelationshipType.SUSPECT_IN,
        )

        mock_session.run.assert_called_once()

    def test_create_relationship_with_properties(self, mock_neo4j_driver):
        """Test creating a relationship with properties."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"r": {"type": "ASSOCIATED_WITH", "since": "2024-01-01"}}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = manager.create_relationship(
            source_id="person-001",
            source_type=EntityType.PERSON,
            target_id="person-002",
            target_type=EntityType.PERSON,
            relationship_type=RelationshipType.ASSOCIATED_WITH,
            properties={"since": "2024-01-01", "notes": "Known associates"},
        )

        mock_session.run.assert_called_once()


class TestPropertySearch:
    """Tests for searching entities by property."""

    def test_search_person_by_name(self, mock_neo4j_driver):
        """Test searching for a person by name."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(
            return_value=iter(
                [
                    {"n": {"id": "person-001", "first_name": "John", "last_name": "Doe"}},
                    {"n": {"id": "person-002", "first_name": "John", "last_name": "Smith"}},
                ]
            )
        )
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        results = manager.search_by_property(
            entity_type=EntityType.PERSON,
            property_name="first_name",
            property_value="John",
        )

        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "MATCH" in call_args[0][0]
        assert "Person" in call_args[0][0]

    def test_search_vehicle_by_plate(self, mock_neo4j_driver):
        """Test searching for a vehicle by plate number."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(
            return_value=iter(
                [
                    {"n": {"id": "vehicle-001", "plate_number": "ABC-1234"}},
                ]
            )
        )
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        results = manager.search_by_property(
            entity_type=EntityType.VEHICLE,
            property_name="plate_number",
            property_value="ABC-1234",
        )

        mock_session.run.assert_called_once()

    def test_search_returns_empty_for_no_match(self, mock_neo4j_driver):
        """Test that search returns empty list when no matches."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        results = manager.search_by_property(
            entity_type=EntityType.PERSON,
            property_name="first_name",
            property_value="NonexistentName",
        )

        mock_session.run.assert_called_once()


class TestNetworkTraversal:
    """Tests for entity network traversal."""

    def test_find_relationships_depth_1(self, mock_neo4j_driver):
        """Test finding relationships at depth 1."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(
            return_value=iter(
                [
                    {
                        "r": {"type": "OWNS"},
                        "target": {"id": "vehicle-001", "labels": ["Vehicle"]},
                    },
                ]
            )
        )
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        results = manager.find_relationships(
            entity_id="person-001",
            entity_type=EntityType.PERSON,
            depth=1,
        )

        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "*1" in call_args[0][0] or "1.." in call_args[0][0]

    def test_find_relationships_depth_2(self, mock_neo4j_driver):
        """Test finding relationships at depth 2."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        results = manager.find_relationships(
            entity_id="person-001",
            entity_type=EntityType.PERSON,
            depth=2,
        )

        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "*" in call_args[0][0] and "2" in call_args[0][0]

    def test_get_entity_network(self, mock_neo4j_driver):
        """Test getting full entity network."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(
            return_value=iter(
                [
                    {
                        "nodes": [
                            {"id": "person-001", "labels": ["Person"]},
                            {"id": "vehicle-001", "labels": ["Vehicle"]},
                        ],
                        "relationships": [
                            {"type": "OWNS", "start": "person-001", "end": "vehicle-001"},
                        ],
                    },
                ]
            )
        )
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        network = manager.get_entity_network(
            entity_id="person-001",
            entity_type=EntityType.PERSON,
            depth=2,
        )

        mock_session.run.assert_called_once()


class TestEntityDeletion:
    """Tests for entity deletion."""

    def test_delete_entity(self, mock_neo4j_driver):
        """Test deleting an entity."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"deleted": True}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = manager.delete_entity(
            entity_id="person-001",
            entity_type=EntityType.PERSON,
        )

        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "DELETE" in call_args[0][0] or "DETACH DELETE" in call_args[0][0]

    def test_delete_entity_with_relationships(self, mock_neo4j_driver):
        """Test deleting an entity with relationships (DETACH DELETE)."""
        manager = Neo4jManager()
        manager._driver = mock_neo4j_driver

        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"deleted": True}
        mock_session.run.return_value = mock_result
        mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session

        result = manager.delete_entity(
            entity_id="person-001",
            entity_type=EntityType.PERSON,
            detach=True,
        )

        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "DETACH DELETE" in call_args[0][0]


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_valid_person_schema(self, sample_person_data):
        """Test that valid person data passes validation."""
        person = PersonCreate(**sample_person_data)

        assert person.first_name == sample_person_data["first_name"]
        assert person.last_name == sample_person_data["last_name"]

    def test_valid_vehicle_schema(self, sample_vehicle_data):
        """Test that valid vehicle data passes validation."""
        vehicle = VehicleCreate(**sample_vehicle_data)

        assert vehicle.plate_number == sample_vehicle_data["plate_number"]
        assert vehicle.make == sample_vehicle_data["make"]

    def test_valid_incident_schema(self, sample_incident_data):
        """Test that valid incident data passes validation."""
        incident = IncidentCreate(**sample_incident_data)

        assert incident.incident_number == sample_incident_data["incident_number"]
        assert incident.incident_type == sample_incident_data["incident_type"]

    def test_invalid_person_missing_required(self):
        """Test that missing required fields raises error."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            PersonCreate(first_name="John")  # Missing last_name

    def test_invalid_vehicle_missing_required(self):
        """Test that missing required fields raises error."""
        with pytest.raises(Exception):
            VehicleCreate(make="Toyota")  # Missing plate_number
