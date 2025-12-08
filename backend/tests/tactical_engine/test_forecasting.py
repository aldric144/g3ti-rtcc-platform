"""Tests for the Tactical Forecasting Engine."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tactical_engine.forecasting import TacticalForecaster


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
def forecaster(mock_neo4j, mock_es, mock_redis):
    """Create forecaster with mocked dependencies."""
    return TacticalForecaster(
        neo4j=mock_neo4j,
        es=mock_es,
        redis=mock_redis,
    )


class TestTacticalForecaster:
    """Tests for TacticalForecaster."""

    @pytest.mark.asyncio
    async def test_generate_forecast_returns_valid_structure(self, forecaster):
        """Test that generate_forecast returns valid structure."""
        result = await forecaster.generate_forecast(
            hours=24,
            forecast_type="all",
        )

        assert "forecast_window" in result
        assert "forecast_type" in result
        assert "predictions" in result
        assert "zone_predictions" in result
        assert "high_risk_areas" in result
        assert "expected_incidents" in result
        assert "confidence" in result
        assert "model_info" in result
        assert "generated_at" in result

    @pytest.mark.asyncio
    async def test_generate_forecast_24h(self, forecaster):
        """Test 24-hour forecast generation."""
        result = await forecaster.generate_forecast(
            hours=24,
            forecast_type="all",
        )

        assert result["forecast_window"]["hours"] == 24
        assert result["confidence"] >= 0
        assert result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_generate_forecast_72h(self, forecaster):
        """Test 72-hour forecast generation."""
        result = await forecaster.generate_forecast(
            hours=72,
            forecast_type="crime",
        )

        assert result["forecast_window"]["hours"] == 72

    @pytest.mark.asyncio
    async def test_generate_forecast_7d(self, forecaster):
        """Test 7-day forecast generation."""
        result = await forecaster.generate_forecast(
            hours=168,
            forecast_type="gunfire",
        )

        assert result["forecast_window"]["hours"] == 168

    @pytest.mark.asyncio
    async def test_forecast_types(self, forecaster):
        """Test different forecast types."""
        for forecast_type in ["all", "crime", "gunfire", "vehicles"]:
            result = await forecaster.generate_forecast(
                hours=24,
                forecast_type=forecast_type,
            )
            assert result["forecast_type"] == forecast_type

    @pytest.mark.asyncio
    async def test_get_crime_forecast(self, forecaster):
        """Test crime-specific forecast."""
        result = await forecaster.get_crime_forecast(hours=24)

        assert "predictions" in result
        assert "zone_predictions" in result

    @pytest.mark.asyncio
    async def test_get_gunfire_forecast(self, forecaster):
        """Test gunfire-specific forecast."""
        result = await forecaster.get_gunfire_forecast(hours=24)

        assert "predictions" in result

    @pytest.mark.asyncio
    async def test_get_vehicle_forecast(self, forecaster):
        """Test vehicle recurrence forecast."""
        result = await forecaster.get_vehicle_forecast(hours=24)

        assert "predictions" in result

    @pytest.mark.asyncio
    async def test_predictions_structure(self, forecaster):
        """Test that predictions have proper structure."""
        result = await forecaster.generate_forecast(
            hours=24,
            forecast_type="all",
        )

        predictions = result["predictions"]
        assert "temporal" in predictions
        assert "spatial" in predictions
        assert "markov" in predictions

    @pytest.mark.asyncio
    async def test_temporal_predictions(self, forecaster):
        """Test temporal prediction structure."""
        result = await forecaster.generate_forecast(
            hours=24,
            forecast_type="all",
        )

        temporal = result["predictions"]["temporal"]
        assert "trend" in temporal
        assert "trend_direction" in temporal

    @pytest.mark.asyncio
    async def test_spatial_predictions(self, forecaster):
        """Test spatial prediction structure."""
        result = await forecaster.generate_forecast(
            hours=24,
            forecast_type="all",
        )

        spatial = result["predictions"]["spatial"]
        assert "hotspots" in spatial
        assert isinstance(spatial["hotspots"], list)

    @pytest.mark.asyncio
    async def test_markov_predictions(self, forecaster):
        """Test Markov chain prediction structure."""
        result = await forecaster.generate_forecast(
            hours=24,
            forecast_type="all",
        )

        markov = result["predictions"]["markov"]
        assert "current_state" in markov
        assert "predicted_states" in markov

    @pytest.mark.asyncio
    async def test_zone_predictions_format(self, forecaster):
        """Test zone predictions format."""
        result = await forecaster.generate_forecast(
            hours=24,
            forecast_type="all",
        )

        for zp in result["zone_predictions"]:
            assert "zone_id" in zp
            assert "predicted_incidents" in zp
            assert "confidence" in zp

    @pytest.mark.asyncio
    async def test_model_info(self, forecaster):
        """Test that model info is provided."""
        result = await forecaster.generate_forecast(
            hours=24,
            forecast_type="all",
        )

        model_info = result["model_info"]
        assert "models_used" in model_info
        assert isinstance(model_info["models_used"], list)
