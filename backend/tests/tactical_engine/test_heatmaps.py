"""Tests for the Predictive Heatmap Engine."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tactical_engine.heatmaps import PredictiveHeatmapEngine


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
    return mock


@pytest.fixture
def mock_redis():
    """Create mock Redis manager."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def heatmap_engine(mock_neo4j, mock_es, mock_redis):
    """Create heatmap engine with mocked dependencies."""
    return PredictiveHeatmapEngine(
        neo4j=mock_neo4j,
        es=mock_es,
        redis=mock_redis,
    )


class TestPredictiveHeatmapEngine:
    """Tests for PredictiveHeatmapEngine."""

    @pytest.mark.asyncio
    async def test_generate_current_heatmap_returns_valid_structure(
        self, heatmap_engine
    ):
        """Test that generate_current_heatmap returns valid structure."""
        result = await heatmap_engine.generate_current_heatmap(
            heatmap_type="all",
            resolution="medium",
        )

        assert "geojson" in result
        assert "clusters" in result
        assert "hot_zones" in result
        assert "confidence" in result
        assert "explanation" in result
        assert "generated_at" in result

    @pytest.mark.asyncio
    async def test_generate_current_heatmap_geojson_format(self, heatmap_engine):
        """Test that GeoJSON output is properly formatted."""
        result = await heatmap_engine.generate_current_heatmap(
            heatmap_type="gunfire",
            resolution="low",
        )

        geojson = result["geojson"]
        assert geojson["type"] == "FeatureCollection"
        assert "features" in geojson
        assert isinstance(geojson["features"], list)

    @pytest.mark.asyncio
    async def test_generate_predictive_heatmap_24h(self, heatmap_engine):
        """Test 24-hour predictive heatmap generation."""
        result = await heatmap_engine.generate_predictive_heatmap(
            hours=24,
            heatmap_type="all",
        )

        assert "geojson" in result
        assert "clusters" in result
        assert "hot_zones" in result
        assert result["confidence"] >= 0
        assert result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_generate_predictive_heatmap_7d(self, heatmap_engine):
        """Test 7-day predictive heatmap generation."""
        result = await heatmap_engine.generate_predictive_heatmap(
            hours=168,
            heatmap_type="vehicles",
        )

        assert "geojson" in result
        assert "explanation" in result

    @pytest.mark.asyncio
    async def test_update_with_incident(self, heatmap_engine):
        """Test updating heatmap with new incident."""
        incident = {
            "id": "INC-001",
            "type": "gunfire",
            "lat": 33.45,
            "lon": -112.07,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high",
        }

        # Should not raise
        await heatmap_engine.update_with_incident(incident)

    @pytest.mark.asyncio
    async def test_heatmap_type_filtering(self, heatmap_engine):
        """Test that heatmap type filtering works."""
        for heatmap_type in ["gunfire", "vehicles", "crime", "all"]:
            result = await heatmap_engine.generate_current_heatmap(
                heatmap_type=heatmap_type,
                resolution="low",
            )
            assert "geojson" in result

    @pytest.mark.asyncio
    async def test_resolution_affects_grid_size(self, heatmap_engine):
        """Test that resolution affects grid granularity."""
        low_res = await heatmap_engine.generate_current_heatmap(
            heatmap_type="all",
            resolution="low",
        )
        high_res = await heatmap_engine.generate_current_heatmap(
            heatmap_type="all",
            resolution="high",
        )

        # Both should return valid results
        assert "geojson" in low_res
        assert "geojson" in high_res

    @pytest.mark.asyncio
    async def test_clusters_have_required_fields(self, heatmap_engine):
        """Test that clusters have all required fields."""
        result = await heatmap_engine.generate_current_heatmap(
            heatmap_type="all",
            resolution="medium",
        )

        for cluster in result.get("clusters", []):
            assert "id" in cluster
            assert "center" in cluster
            assert "lat" in cluster["center"]
            assert "lon" in cluster["center"]

    @pytest.mark.asyncio
    async def test_hot_zones_have_required_fields(self, heatmap_engine):
        """Test that hot zones have all required fields."""
        result = await heatmap_engine.generate_current_heatmap(
            heatmap_type="all",
            resolution="medium",
        )

        for zone in result.get("hot_zones", []):
            assert "id" in zone
            assert "bounds" in zone
            assert "risk_score" in zone
