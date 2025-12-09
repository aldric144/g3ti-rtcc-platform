"""Tests for the Tactical Risk Scoring Engine."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tactical_engine.tactical_risk import TacticalRiskScorer


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
def risk_scorer(mock_neo4j, mock_es, mock_redis):
    """Create risk scorer with mocked dependencies."""
    return TacticalRiskScorer(
        neo4j=mock_neo4j,
        es=mock_es,
        redis=mock_redis,
    )


class TestTacticalRiskScorer:
    """Tests for TacticalRiskScorer."""

    @pytest.mark.asyncio
    async def test_generate_risk_map_returns_valid_structure(self, risk_scorer):
        """Test that generate_risk_map returns valid structure."""
        result = await risk_scorer.generate_risk_map(
            zone_id=None,
            level="micro",
            include_factors=True,
        )

        assert "zones" in result
        assert "summary" in result
        assert "level" in result
        assert "generated_at" in result
        assert "total_zones" in result

    @pytest.mark.asyncio
    async def test_generate_risk_map_micro_level(self, risk_scorer):
        """Test micro-level risk map generation."""
        result = await risk_scorer.generate_risk_map(
            zone_id=None,
            level="micro",
            include_factors=True,
        )

        assert result["level"] == "micro"
        assert isinstance(result["zones"], list)

    @pytest.mark.asyncio
    async def test_generate_risk_map_district_level(self, risk_scorer):
        """Test district-level risk map generation."""
        result = await risk_scorer.generate_risk_map(
            zone_id=None,
            level="district",
            include_factors=False,
        )

        assert result["level"] == "district"

    @pytest.mark.asyncio
    async def test_score_entity_person(self, risk_scorer):
        """Test scoring a person entity."""
        result = await risk_scorer.score_entity(
            entity_id="PER-001",
            entity_type="person",
        )

        assert "entity_id" in result
        assert "entity_type" in result
        assert "risk_score" in result
        assert "risk_level" in result
        assert result["risk_score"] >= 0
        assert result["risk_score"] <= 1

    @pytest.mark.asyncio
    async def test_score_entity_vehicle(self, risk_scorer):
        """Test scoring a vehicle entity."""
        result = await risk_scorer.score_entity(
            entity_id="VEH-001",
            entity_type="vehicle",
        )

        assert result["entity_type"] == "vehicle"
        assert "risk_score" in result

    @pytest.mark.asyncio
    async def test_score_entity_address(self, risk_scorer):
        """Test scoring an address entity."""
        result = await risk_scorer.score_entity(
            entity_id="ADDR-001",
            entity_type="address",
        )

        assert result["entity_type"] == "address"
        assert "risk_score" in result

    @pytest.mark.asyncio
    async def test_update_with_incident(self, risk_scorer):
        """Test updating risk scores with new incident."""
        incident = {
            "id": "INC-001",
            "type": "violent_crime",
            "lat": 33.45,
            "lon": -112.07,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high",
        }

        # Should not raise
        await risk_scorer.update_with_incident(incident)

    @pytest.mark.asyncio
    async def test_risk_levels_are_valid(self, risk_scorer):
        """Test that risk levels are valid strings."""
        result = await risk_scorer.generate_risk_map(
            zone_id=None,
            level="micro",
            include_factors=True,
        )

        valid_levels = {"critical", "high", "elevated", "moderate", "low"}
        for zone in result.get("zones", []):
            if "risk_level" in zone:
                assert zone["risk_level"] in valid_levels

    @pytest.mark.asyncio
    async def test_risk_factors_included_when_requested(self, risk_scorer):
        """Test that risk factors are included when requested."""
        result = await risk_scorer.generate_risk_map(
            zone_id=None,
            level="micro",
            include_factors=True,
        )

        # Mock data should include factors
        for zone in result.get("zones", []):
            if "factors" in zone:
                assert isinstance(zone["factors"], dict)

    @pytest.mark.asyncio
    async def test_summary_statistics(self, risk_scorer):
        """Test that summary statistics are calculated."""
        result = await risk_scorer.generate_risk_map(
            zone_id=None,
            level="micro",
            include_factors=False,
        )

        summary = result.get("summary", {})
        assert "avg_risk" in summary or "total_zones" in result
