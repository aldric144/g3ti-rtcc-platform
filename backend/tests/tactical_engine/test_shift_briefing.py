"""Tests for the Shift Briefing Builder."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tactical_engine.shift_briefing import ShiftBriefingBuilder


@pytest.fixture
def mock_neo4j():
    """Create mock Neo4j manager."""
    mock = MagicMock()
    mock.execute_query = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_es():
    """Create mock Elasticsearch manager."""
    mock = MagicMock()
    mock.search = AsyncMock(return_value={"hits": {"hits": []}})
    mock.count = AsyncMock(return_value={"count": 0})
    mock.index = AsyncMock(return_value={"result": "created"})
    return mock


@pytest.fixture
def mock_redis():
    """Create mock Redis manager."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def briefing_builder(mock_neo4j, mock_es, mock_redis):
    """Create briefing builder with mocked dependencies."""
    return ShiftBriefingBuilder(
        neo4j=mock_neo4j,
        es=mock_es,
        redis=mock_redis,
    )


class TestShiftBriefingBuilder:
    """Tests for ShiftBriefingBuilder."""

    @pytest.mark.asyncio
    async def test_build_briefing_returns_valid_structure(self, briefing_builder):
        """Test that build_briefing returns valid structure."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=False,
        )

        assert "briefing_id" in result
        assert "shift" in result
        assert "generated_at" in result
        assert "valid_until" in result
        assert "zones_of_concern" in result
        assert "entity_highlights" in result
        assert "case_developments" in result
        assert "ai_anomalies" in result
        assert "tactical_advisories" in result
        assert "overnight_summary" in result
        assert "statistics" in result

    @pytest.mark.asyncio
    async def test_build_briefing_shift_a(self, briefing_builder):
        """Test briefing for Shift A (Day)."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=False,
        )

        assert result["shift"]["code"] == "A"
        assert result["shift"]["name"] == "Day Shift"

    @pytest.mark.asyncio
    async def test_build_briefing_shift_b(self, briefing_builder):
        """Test briefing for Shift B (Evening)."""
        result = await briefing_builder.build_briefing(
            shift="B",
            include_routes=False,
            include_heatmaps=False,
        )

        assert result["shift"]["code"] == "B"
        assert result["shift"]["name"] == "Evening Shift"

    @pytest.mark.asyncio
    async def test_build_briefing_shift_c(self, briefing_builder):
        """Test briefing for Shift C (Night)."""
        result = await briefing_builder.build_briefing(
            shift="C",
            include_routes=False,
            include_heatmaps=False,
        )

        assert result["shift"]["code"] == "C"
        assert result["shift"]["name"] == "Night Shift"

    @pytest.mark.asyncio
    async def test_entity_highlights_structure(self, briefing_builder):
        """Test entity highlights structure."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=False,
        )

        highlights = result["entity_highlights"]
        assert "vehicles_of_interest" in highlights
        assert "persons_of_interest" in highlights
        assert isinstance(highlights["vehicles_of_interest"], list)
        assert isinstance(highlights["persons_of_interest"], list)

    @pytest.mark.asyncio
    async def test_statistics_structure(self, briefing_builder):
        """Test statistics structure."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=False,
        )

        stats = result["statistics"]
        assert "zones_of_concern_count" in stats
        assert "critical_zones" in stats
        assert "vehicles_of_interest_count" in stats
        assert "persons_of_interest_count" in stats

    @pytest.mark.asyncio
    async def test_tactical_advisories_format(self, briefing_builder):
        """Test tactical advisories format."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=False,
        )

        for advisory in result["tactical_advisories"]:
            assert "priority" in advisory
            assert "type" in advisory
            assert "title" in advisory
            assert "description" in advisory
            assert "action" in advisory

    @pytest.mark.asyncio
    async def test_briefing_id_format(self, briefing_builder):
        """Test briefing ID format."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=False,
        )

        assert result["briefing_id"].startswith("BRIEF-A-")

    @pytest.mark.asyncio
    async def test_valid_until_is_future(self, briefing_builder):
        """Test that valid_until is in the future."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=False,
        )

        generated = datetime.fromisoformat(result["generated_at"])
        valid_until = datetime.fromisoformat(result["valid_until"])
        assert valid_until > generated

    @pytest.mark.asyncio
    async def test_overnight_summary_is_string(self, briefing_builder):
        """Test that overnight summary is a string."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=False,
        )

        assert isinstance(result["overnight_summary"], str)
        assert len(result["overnight_summary"]) > 0

    @pytest.mark.asyncio
    async def test_include_routes_option(self, briefing_builder):
        """Test that routes are included when requested."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=True,
            include_heatmaps=False,
        )

        assert "patrol_routes" in result

    @pytest.mark.asyncio
    async def test_include_heatmaps_option(self, briefing_builder):
        """Test that heatmaps are included when requested."""
        result = await briefing_builder.build_briefing(
            shift="A",
            include_routes=False,
            include_heatmaps=True,
        )

        assert "tactical_map" in result
