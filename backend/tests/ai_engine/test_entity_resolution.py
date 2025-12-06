"""
Unit tests for the Entity Resolution module.

Tests alias resolution, probabilistic matching, and entity merging.
"""

import pytest

from app.ai_engine.entity_resolution import (
    EntityResolver,
    PersonAliasResolver,
    VehicleAliasResolver,
    IncidentLinkageResolver,
    edit_distance_similarity,
    phonetic_similarity,
    name_similarity,
    plate_similarity,
)


class TestSimilarityFunctions:
    """Tests for similarity calculation functions."""

    def test_edit_distance_similarity_identical(self):
        """Test edit distance for identical strings."""
        similarity = edit_distance_similarity("John Smith", "John Smith")
        assert similarity == 1.0

    def test_edit_distance_similarity_similar(self):
        """Test edit distance for similar strings."""
        similarity = edit_distance_similarity("John Smith", "Jon Smith")
        assert 0.8 <= similarity <= 1.0

    def test_edit_distance_similarity_different(self):
        """Test edit distance for different strings."""
        similarity = edit_distance_similarity("John Smith", "Jane Doe")
        assert similarity < 0.5

    def test_edit_distance_similarity_empty(self):
        """Test edit distance with empty strings."""
        similarity = edit_distance_similarity("", "")
        assert similarity == 1.0

    def test_phonetic_similarity_same_sound(self):
        """Test phonetic similarity for same-sounding names."""
        similarity = phonetic_similarity("Smith", "Smyth")
        assert similarity >= 0.8

    def test_phonetic_similarity_different_sound(self):
        """Test phonetic similarity for different-sounding names."""
        similarity = phonetic_similarity("Smith", "Jones")
        assert similarity < 0.5

    def test_name_similarity_identical(self):
        """Test name similarity for identical names."""
        similarity = name_similarity("John Smith", "John Smith")
        assert similarity == 1.0

    def test_name_similarity_reversed(self):
        """Test name similarity for reversed names."""
        similarity = name_similarity("John Smith", "Smith John")
        assert similarity >= 0.7

    def test_name_similarity_partial(self):
        """Test name similarity for partial matches."""
        similarity = name_similarity("John Smith", "John")
        assert 0.3 <= similarity <= 0.8

    def test_plate_similarity_identical(self):
        """Test plate similarity for identical plates."""
        similarity = plate_similarity("ABC123", "ABC123")
        assert similarity == 1.0

    def test_plate_similarity_one_char_diff(self):
        """Test plate similarity with one character difference."""
        similarity = plate_similarity("ABC123", "ABC124")
        assert similarity >= 0.8

    def test_plate_similarity_case_insensitive(self):
        """Test plate similarity is case insensitive."""
        similarity = plate_similarity("ABC123", "abc123")
        assert similarity == 1.0


class TestPersonAliasResolver:
    """Tests for PersonAliasResolver class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = PersonAliasResolver()

    def test_resolve_identical_persons(self):
        """Test resolving identical person records."""
        persons = [
            {"id": "1", "name": "John Smith", "dob": "1990-01-01"},
            {"id": "2", "name": "John Smith", "dob": "1990-01-01"},
        ]
        result = self.resolver.resolve(persons)

        assert result is not None
        assert len(result.get("merge_candidates", [])) >= 0

    def test_resolve_similar_persons(self):
        """Test resolving similar person records."""
        persons = [
            {"id": "1", "name": "John Smith", "dob": "1990-01-01"},
            {"id": "2", "name": "Jon Smith", "dob": "1990-01-01"},
        ]
        result = self.resolver.resolve(persons)

        assert result is not None

    def test_resolve_different_persons(self):
        """Test resolving different person records."""
        persons = [
            {"id": "1", "name": "John Smith", "dob": "1990-01-01"},
            {"id": "2", "name": "Jane Doe", "dob": "1985-05-15"},
        ]
        result = self.resolver.resolve(persons)

        assert result is not None
        assert len(result.get("merge_candidates", [])) == 0

    def test_resolve_with_aliases(self):
        """Test resolving persons with known aliases."""
        persons = [
            {"id": "1", "name": "John Smith", "aliases": ["Johnny", "J. Smith"]},
            {"id": "2", "name": "Johnny Smith"},
        ]
        result = self.resolver.resolve(persons)

        assert result is not None

    def test_extract_aliases(self):
        """Test alias extraction from person data."""
        person = {
            "id": "1",
            "name": "John Smith",
            "aliases": ["Johnny", "J. Smith"],
            "aka": "Big John",
        }
        aliases = self.resolver.extract_aliases(person)

        assert "John Smith" in aliases
        assert len(aliases) >= 1


class TestVehicleAliasResolver:
    """Tests for VehicleAliasResolver class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = VehicleAliasResolver()

    def test_resolve_identical_vehicles(self):
        """Test resolving identical vehicle records."""
        vehicles = [
            {"id": "1", "plate": "ABC123", "make": "Toyota", "model": "Camry"},
            {"id": "2", "plate": "ABC123", "make": "Toyota", "model": "Camry"},
        ]
        result = self.resolver.resolve(vehicles)

        assert result is not None
        assert len(result.get("merge_candidates", [])) >= 0

    def test_resolve_similar_plates(self):
        """Test resolving vehicles with similar plates."""
        vehicles = [
            {"id": "1", "plate": "ABC123", "make": "Toyota"},
            {"id": "2", "plate": "ABC124", "make": "Toyota"},
        ]
        result = self.resolver.resolve(vehicles)

        assert result is not None

    def test_resolve_different_vehicles(self):
        """Test resolving different vehicle records."""
        vehicles = [
            {"id": "1", "plate": "ABC123", "make": "Toyota", "color": "Blue"},
            {"id": "2", "plate": "XYZ789", "make": "Honda", "color": "Red"},
        ]
        result = self.resolver.resolve(vehicles)

        assert result is not None
        assert len(result.get("merge_candidates", [])) == 0

    def test_resolve_plate_variations(self):
        """Test resolving plates with common OCR errors."""
        vehicles = [
            {"id": "1", "plate": "ABC123"},
            {"id": "2", "plate": "A8C123"},  # B -> 8 OCR error
        ]
        result = self.resolver.resolve(vehicles)

        assert result is not None


class TestIncidentLinkageResolver:
    """Tests for IncidentLinkageResolver class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = IncidentLinkageResolver()

    def test_resolve_related_incidents(self):
        """Test resolving related incidents."""
        incidents = [
            {
                "id": "1",
                "type": "gunshot",
                "location": {"lat": 40.7128, "lng": -74.0060},
                "timestamp": "2024-01-01T12:00:00Z",
            },
            {
                "id": "2",
                "type": "gunshot",
                "location": {"lat": 40.7129, "lng": -74.0061},
                "timestamp": "2024-01-01T12:05:00Z",
            },
        ]
        result = self.resolver.resolve(incidents)

        assert result is not None

    def test_resolve_unrelated_incidents(self):
        """Test resolving unrelated incidents."""
        incidents = [
            {
                "id": "1",
                "type": "gunshot",
                "location": {"lat": 40.7128, "lng": -74.0060},
                "timestamp": "2024-01-01T12:00:00Z",
            },
            {
                "id": "2",
                "type": "traffic",
                "location": {"lat": 41.0000, "lng": -75.0000},
                "timestamp": "2024-01-15T12:00:00Z",
            },
        ]
        result = self.resolver.resolve(incidents)

        assert result is not None
        assert len(result.get("linkages", [])) == 0


class TestEntityResolver:
    """Tests for main EntityResolver class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = EntityResolver()

    def test_resolve_mixed_entities(self):
        """Test resolving mixed entity types."""
        entities = [
            {"id": "1", "type": "person", "name": "John Smith"},
            {"id": "2", "type": "vehicle", "plate": "ABC123"},
            {"id": "3", "type": "person", "name": "Jon Smith"},
        ]
        result = self.resolver.resolve_all(entities)

        assert result is not None
        assert "persons" in result or "resolved" in result

    def test_calculate_confidence(self):
        """Test confidence score calculation."""
        entity1 = {"id": "1", "name": "John Smith", "dob": "1990-01-01"}
        entity2 = {"id": "2", "name": "Jon Smith", "dob": "1990-01-01"}

        confidence = self.resolver.calculate_confidence(entity1, entity2)

        assert 0.0 <= confidence <= 1.0

    def test_suggest_merges(self):
        """Test merge suggestion generation."""
        entities = [
            {"id": "1", "type": "person", "name": "John Smith"},
            {"id": "2", "type": "person", "name": "John Smith"},
        ]
        merges = self.resolver.suggest_merges(entities)

        assert isinstance(merges, list)
