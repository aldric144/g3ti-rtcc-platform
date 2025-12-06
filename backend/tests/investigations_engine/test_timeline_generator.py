"""
Unit tests for the Timeline Generator module.

Tests cover:
- Timeline event creation
- Event ordering by timestamp
- Source reliability scoring
- Event deduplication
- Multi-source timeline generation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.investigations_engine.timeline_generator import TimelineGenerator
from app.investigations_engine.models import TimelineEvent


class TestTimelineGenerator:
    """Test suite for TimelineGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a TimelineGenerator instance for testing."""
        return TimelineGenerator()

    @pytest.fixture
    def sample_events(self):
        """Create sample timeline events for testing."""
        base_time = datetime.utcnow()
        return [
            {
                "timestamp": base_time.isoformat(),
                "event_type": "CAD",
                "description": "911 call received",
                "source": "CAD",
            },
            {
                "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
                "event_type": "CAD",
                "description": "Units dispatched",
                "source": "CAD",
            },
            {
                "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
                "event_type": "LPR",
                "description": "Vehicle spotted on camera",
                "source": "LPR",
            },
            {
                "timestamp": (base_time + timedelta(minutes=15)).isoformat(),
                "event_type": "BWC",
                "description": "Officer arrived on scene",
                "source": "BWC",
            },
        ]

    def test_generator_initialization(self, generator):
        """Test that TimelineGenerator initializes correctly."""
        assert generator is not None
        assert hasattr(generator, "generate")

    @pytest.mark.asyncio
    async def test_generate_empty_case(self, generator):
        """Test timeline generation for empty case."""
        timeline = await generator.generate(case_id="CASE001")
        assert isinstance(timeline, list)

    @pytest.mark.asyncio
    async def test_generate_from_data(self, generator, sample_events):
        """Test timeline generation from provided data."""
        timeline = await generator.generate_from_data(
            incidents=[],
            cad_events=sample_events[:2],
            lpr_events=[sample_events[2]],
            bwc_events=[sample_events[3]],
        )

        assert isinstance(timeline, list)
        assert len(timeline) == 4

    def test_create_timeline_event(self, generator):
        """Test timeline event creation."""
        event = generator._create_event(
            timestamp=datetime.utcnow(),
            event_type="CAD",
            description="Test event",
            source="CAD",
        )

        assert isinstance(event, TimelineEvent)
        assert event.event_type == "CAD"
        assert event.source == "CAD"

    def test_sort_events_by_timestamp(self, generator, sample_events):
        """Test that events are sorted by timestamp."""
        events = [
            generator._create_event(
                timestamp=datetime.fromisoformat(e["timestamp"]),
                event_type=e["event_type"],
                description=e["description"],
                source=e["source"],
            )
            for e in sample_events
        ]

        # Shuffle events
        shuffled = [events[2], events[0], events[3], events[1]]

        sorted_events = generator._sort_and_deduplicate(shuffled)

        # Verify chronological order
        for i in range(len(sorted_events) - 1):
            assert sorted_events[i].timestamp <= sorted_events[i + 1].timestamp

    def test_get_reliability_score_cad(self, generator):
        """Test reliability score for CAD events."""
        score = generator._get_reliability_score("CAD")
        assert score == 0.95

    def test_get_reliability_score_rms(self, generator):
        """Test reliability score for RMS events."""
        score = generator._get_reliability_score("RMS")
        assert score == 0.98

    def test_get_reliability_score_lpr(self, generator):
        """Test reliability score for LPR events."""
        score = generator._get_reliability_score("LPR")
        assert score == 0.90

    def test_get_reliability_score_shotspotter(self, generator):
        """Test reliability score for ShotSpotter events."""
        score = generator._get_reliability_score("ShotSpotter")
        assert score == 0.85

    def test_get_reliability_score_bwc(self, generator):
        """Test reliability score for BWC events."""
        score = generator._get_reliability_score("BWC")
        assert score == 0.95

    def test_get_reliability_score_unknown(self, generator):
        """Test reliability score for unknown source."""
        score = generator._get_reliability_score("Unknown")
        assert score == 0.50

    def test_deduplicate_events(self, generator):
        """Test event deduplication."""
        base_time = datetime.utcnow()
        events = [
            generator._create_event(
                timestamp=base_time,
                event_type="CAD",
                description="911 call received",
                source="CAD",
            ),
            generator._create_event(
                timestamp=base_time,
                event_type="CAD",
                description="911 call received",
                source="CAD",
            ),
        ]

        deduplicated = generator._sort_and_deduplicate(events)

        # Should remove duplicate
        assert len(deduplicated) == 1


class TestTimelineGeneratorIntegration:
    """Integration tests for TimelineGenerator with mocked dependencies."""

    @pytest.fixture
    def generator_with_mocks(self):
        """Create a TimelineGenerator with mocked dependencies."""
        generator = TimelineGenerator()
        generator.neo4j_manager = MagicMock()
        generator.es_client = MagicMock()
        return generator

    @pytest.mark.asyncio
    async def test_generate_with_neo4j(self, generator_with_mocks):
        """Test timeline generation with Neo4j integration."""
        generator_with_mocks.neo4j_manager.execute_query = AsyncMock(return_value=[])

        timeline = await generator_with_mocks.generate(case_id="CASE001")
        assert isinstance(timeline, list)

    @pytest.mark.asyncio
    async def test_generate_handles_neo4j_error(self, generator_with_mocks):
        """Test that generation handles Neo4j errors gracefully."""
        generator_with_mocks.neo4j_manager.execute_query = AsyncMock(
            side_effect=Exception("Neo4j connection failed")
        )

        # Should not raise, should return empty list
        timeline = await generator_with_mocks.generate(case_id="CASE001")
        assert isinstance(timeline, list)
