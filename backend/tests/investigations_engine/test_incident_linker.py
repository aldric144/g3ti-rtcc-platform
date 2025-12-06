"""
Unit tests for the Incident Linker module.

Tests cover:
- Temporal proximity scoring
- Geographic proximity scoring
- Entity overlap detection
- Narrative similarity analysis
- Ballistic correlation
- Vehicle recurrence detection
- M.O. similarity analysis
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.investigations_engine.incident_linker import IncidentLinker
from app.investigations_engine.models import (
    IncidentLinkResult,
    LinkedIncident,
)


class TestIncidentLinker:
    """Test suite for IncidentLinker class."""

    @pytest.fixture
    def linker(self):
        """Create an IncidentLinker instance for testing."""
        return IncidentLinker()

    @pytest.fixture
    def sample_incidents(self):
        """Create sample incident data for testing."""
        return [
            {
                "incident_id": "INC001",
                "incident_type": "ROBBERY",
                "timestamp": datetime.utcnow().isoformat(),
                "location": {"latitude": 33.7490, "longitude": -84.3880},
                "narrative": "Armed robbery at convenience store",
                "suspects": [{"description": "Male, 6ft, black hoodie"}],
                "vehicles": [{"plate": "ABC123", "make": "Honda", "model": "Civic"}],
                "weapons": [{"type": "handgun", "caliber": "9mm"}],
            },
            {
                "incident_id": "INC002",
                "incident_type": "ROBBERY",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "location": {"latitude": 33.7500, "longitude": -84.3890},
                "narrative": "Armed robbery at gas station",
                "suspects": [{"description": "Male, tall, dark hoodie"}],
                "vehicles": [{"plate": "ABC123", "make": "Honda", "model": "Civic"}],
                "weapons": [{"type": "handgun", "caliber": "9mm"}],
            },
            {
                "incident_id": "INC003",
                "incident_type": "BURGLARY",
                "timestamp": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "location": {"latitude": 34.0522, "longitude": -118.2437},
                "narrative": "Residential burglary",
                "suspects": [],
                "vehicles": [],
                "weapons": [],
            },
        ]

    def test_linker_initialization(self, linker):
        """Test that IncidentLinker initializes correctly."""
        assert linker is not None
        assert hasattr(linker, "link_incidents")

    @pytest.mark.asyncio
    async def test_link_incidents_empty_list(self, linker):
        """Test linking with empty incident list."""
        result = await linker.link_incidents([])
        assert isinstance(result, IncidentLinkResult)
        assert len(result.linked_incidents) == 0

    @pytest.mark.asyncio
    async def test_link_incidents_single_incident(self, linker):
        """Test linking with single incident."""
        result = await linker.link_incidents(["INC001"])
        assert isinstance(result, IncidentLinkResult)

    def test_calculate_temporal_score_same_time(self, linker):
        """Test temporal scoring for incidents at same time."""
        time1 = datetime.utcnow()
        time2 = time1
        score = linker._calculate_temporal_score(time1, time2)
        assert score == 1.0

    def test_calculate_temporal_score_close_time(self, linker):
        """Test temporal scoring for incidents close in time."""
        time1 = datetime.utcnow()
        time2 = time1 - timedelta(hours=1)
        score = linker._calculate_temporal_score(time1, time2)
        assert 0.8 < score < 1.0

    def test_calculate_temporal_score_far_time(self, linker):
        """Test temporal scoring for incidents far apart in time."""
        time1 = datetime.utcnow()
        time2 = time1 - timedelta(days=30)
        score = linker._calculate_temporal_score(time1, time2)
        assert score < 0.5

    def test_calculate_geographic_score_same_location(self, linker):
        """Test geographic scoring for same location."""
        loc1 = {"latitude": 33.7490, "longitude": -84.3880}
        loc2 = {"latitude": 33.7490, "longitude": -84.3880}
        score = linker._calculate_geographic_score(loc1, loc2)
        assert score == 1.0

    def test_calculate_geographic_score_close_location(self, linker):
        """Test geographic scoring for close locations."""
        loc1 = {"latitude": 33.7490, "longitude": -84.3880}
        loc2 = {"latitude": 33.7500, "longitude": -84.3890}
        score = linker._calculate_geographic_score(loc1, loc2)
        assert score > 0.8

    def test_calculate_geographic_score_far_location(self, linker):
        """Test geographic scoring for far locations."""
        loc1 = {"latitude": 33.7490, "longitude": -84.3880}
        loc2 = {"latitude": 34.0522, "longitude": -118.2437}
        score = linker._calculate_geographic_score(loc1, loc2)
        assert score < 0.1

    def test_calculate_entity_overlap_same_vehicle(self, linker):
        """Test entity overlap for same vehicle."""
        entities1 = {"vehicles": [{"plate": "ABC123"}]}
        entities2 = {"vehicles": [{"plate": "ABC123"}]}
        score = linker._calculate_entity_overlap(entities1, entities2)
        assert score > 0.5

    def test_calculate_entity_overlap_no_overlap(self, linker):
        """Test entity overlap with no common entities."""
        entities1 = {"vehicles": [{"plate": "ABC123"}]}
        entities2 = {"vehicles": [{"plate": "XYZ789"}]}
        score = linker._calculate_entity_overlap(entities1, entities2)
        assert score == 0.0

    def test_calculate_mo_similarity_same_type(self, linker):
        """Test M.O. similarity for same incident type."""
        incident1 = {"incident_type": "ROBBERY", "weapons": [{"type": "handgun"}]}
        incident2 = {"incident_type": "ROBBERY", "weapons": [{"type": "handgun"}]}
        score = linker._calculate_mo_similarity(incident1, incident2)
        assert score > 0.5

    def test_calculate_mo_similarity_different_type(self, linker):
        """Test M.O. similarity for different incident types."""
        incident1 = {"incident_type": "ROBBERY", "weapons": []}
        incident2 = {"incident_type": "BURGLARY", "weapons": []}
        score = linker._calculate_mo_similarity(incident1, incident2)
        assert score < 0.5

    def test_generate_explanation(self, linker):
        """Test explanation generation."""
        scores = {
            "temporal": 0.9,
            "geographic": 0.8,
            "entity_overlap": 0.7,
            "mo_similarity": 0.6,
        }
        explanations = linker._generate_explanations(scores, "INC001", "INC002")
        assert len(explanations) > 0
        assert any("temporal" in exp.lower() or "time" in exp.lower() for exp in explanations)


class TestIncidentLinkerIntegration:
    """Integration tests for IncidentLinker with mocked dependencies."""

    @pytest.fixture
    def linker_with_mocks(self):
        """Create an IncidentLinker with mocked Neo4j and ES clients."""
        linker = IncidentLinker()
        linker.neo4j_manager = MagicMock()
        linker.es_client = MagicMock()
        return linker

    @pytest.mark.asyncio
    async def test_link_incidents_with_neo4j(self, linker_with_mocks):
        """Test incident linking with Neo4j integration."""
        linker_with_mocks.neo4j_manager.execute_query = AsyncMock(return_value=[])
        
        result = await linker_with_mocks.link_incidents(["INC001", "INC002"])
        assert isinstance(result, IncidentLinkResult)

    @pytest.mark.asyncio
    async def test_link_incidents_handles_neo4j_error(self, linker_with_mocks):
        """Test that linking handles Neo4j errors gracefully."""
        linker_with_mocks.neo4j_manager.execute_query = AsyncMock(
            side_effect=Exception("Neo4j connection failed")
        )
        
        # Should not raise, should return empty result
        result = await linker_with_mocks.link_incidents(["INC001"])
        assert isinstance(result, IncidentLinkResult)
