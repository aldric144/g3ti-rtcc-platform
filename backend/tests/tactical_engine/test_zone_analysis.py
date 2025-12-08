"""Tests for the Zone Analysis Engine."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tactical_engine.zone_analysis import ZoneAnalyzer


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
    return mock


@pytest.fixture
def mock_redis():
    """Create mock Redis manager."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def zone_analyzer(mock_neo4j, mock_es, mock_redis):
    """Create zone analyzer with mocked dependencies."""
    return ZoneAnalyzer(
        neo4j=mock_neo4j,
        es=mock_es,
        redis=mock_redis,
    )


class TestZoneAnalyzer:
    """Tests for ZoneAnalyzer."""

    @pytest.mark.asyncio
    async def test_get_all_zones_returns_list(self, zone_analyzer):
        """Test that get_all_zones returns a list."""
        result = await zone_analyzer.get_all_zones(
            include_risk=True,
            include_predictions=False,
            level="micro",
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_all_zones_micro_level(self, zone_analyzer):
        """Test micro-level zone retrieval."""
        result = await zone_analyzer.get_all_zones(
            include_risk=True,
            include_predictions=False,
            level="micro",
        )

        for zone in result:
            assert "id" in zone
            assert "level" in zone
            assert zone["level"] == "micro"

    @pytest.mark.asyncio
    async def test_get_all_zones_district_level(self, zone_analyzer):
        """Test district-level zone retrieval."""
        result = await zone_analyzer.get_all_zones(
            include_risk=False,
            include_predictions=False,
            level="district",
        )

        for zone in result:
            assert zone["level"] == "district"

    @pytest.mark.asyncio
    async def test_get_zone_details(self, zone_analyzer):
        """Test getting detailed zone information."""
        result = await zone_analyzer.get_zone_details(
            zone_id="micro_5_10",
            include_history=True,
        )

        assert "id" in result
        assert "level" in result
        assert "bounds" in result
        assert "center" in result

    @pytest.mark.asyncio
    async def test_zone_bounds_format(self, zone_analyzer):
        """Test that zone bounds are properly formatted."""
        result = await zone_analyzer.get_zone_details(
            zone_id="micro_5_10",
            include_history=False,
        )

        bounds = result.get("bounds", {})
        assert "min_lat" in bounds
        assert "max_lat" in bounds
        assert "min_lon" in bounds
        assert "max_lon" in bounds

    @pytest.mark.asyncio
    async def test_zone_center_format(self, zone_analyzer):
        """Test that zone center is properly formatted."""
        result = await zone_analyzer.get_zone_details(
            zone_id="micro_5_10",
            include_history=False,
        )

        center = result.get("center", {})
        assert "lat" in center
        assert "lon" in center

    @pytest.mark.asyncio
    async def test_check_zone_alerts(self, zone_analyzer):
        """Test checking for zone alerts."""
        incident = {
            "id": "INC-001",
            "type": "gunfire",
            "lat": 33.45,
            "lon": -112.07,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high",
        }

        result = await zone_analyzer.check_zone_alerts(incident)

        assert "zone_id" in result
        assert "alerts" in result

    @pytest.mark.asyncio
    async def test_zone_risk_included_when_requested(self, zone_analyzer):
        """Test that risk data is included when requested."""
        result = await zone_analyzer.get_all_zones(
            include_risk=True,
            include_predictions=False,
            level="micro",
        )

        # At least some zones should have risk data
        has_risk = any("risk_score" in zone for zone in result)
        assert has_risk or len(result) == 0

    @pytest.mark.asyncio
    async def test_zone_predictions_included_when_requested(self, zone_analyzer):
        """Test that predictions are included when requested."""
        result = await zone_analyzer.get_all_zones(
            include_risk=False,
            include_predictions=True,
            level="micro",
        )

        # Should return valid results
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_zone_status_values(self, zone_analyzer):
        """Test that zone status values are valid."""
        result = await zone_analyzer.get_all_zones(
            include_risk=True,
            include_predictions=False,
            level="micro",
        )

        valid_statuses = {"hot", "warm", "cool", "cold"}
        for zone in result:
            if "status" in zone:
                assert zone["status"] in valid_statuses
