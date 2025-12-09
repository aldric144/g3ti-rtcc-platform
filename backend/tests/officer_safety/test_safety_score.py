"""
Unit tests for Officer Safety Score Engine.

Tests the OfficerSafetyScorer for:
- Safety score calculation
- Risk factor evaluation
- Risk level determination
- Factor weighting
"""

from unittest.mock import patch

import pytest

from app.officer_safety.safety_score import OfficerSafetyScorer, get_safety_scorer


class TestOfficerSafetyScorer:
    """Tests for OfficerSafetyScorer class."""

    @pytest.fixture
    def safety_scorer(self):
        """Create a fresh safety scorer for each test."""
        scorer = OfficerSafetyScorer()
        return scorer

    @pytest.mark.asyncio
    async def test_calculate_score_basic(self, safety_scorer):
        """Test basic safety score calculation."""
        result = await safety_scorer.calculate_score(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        assert "badge" in result
        assert result["badge"] == "1234"
        assert "score" in result
        assert 0.0 <= result["score"] <= 1.0
        assert "level" in result
        assert result["level"] in ["low", "moderate", "elevated", "high", "critical"]
        assert "factors" in result
        assert isinstance(result["factors"], list)

    @pytest.mark.asyncio
    async def test_calculate_score_with_context(self, safety_scorer):
        """Test safety score calculation with additional context."""
        result = await safety_scorer.calculate_score(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            context={
                "status": "on_scene",
                "call_type": "domestic",
            },
        )

        assert "badge" in result
        assert "score" in result
        assert "level" in result

    @pytest.mark.asyncio
    async def test_risk_level_low(self, safety_scorer):
        """Test that low scores result in 'low' risk level."""
        # Mock internal methods to return low scores
        with patch.object(safety_scorer, '_check_high_risk_zone_proximity', return_value=0.0):
            with patch.object(safety_scorer, '_check_recent_gunfire_proximity', return_value=0.0):
                with patch.object(safety_scorer, '_check_repeat_offender_proximity', return_value=0.0):
                    with patch.object(safety_scorer, '_check_vehicle_of_interest_proximity', return_value=0.0):
                        with patch.object(safety_scorer, '_check_active_cad_hazards', return_value=0.0):
                            with patch.object(safety_scorer, '_check_known_threats_at_location', return_value=0.0):
                                with patch.object(safety_scorer, '_check_time_of_day_patterns', return_value=0.0):
                                    with patch.object(safety_scorer, '_check_ai_anomalies', return_value=0.0):
                                        result = await safety_scorer.calculate_score(
                                            badge="1234", lat=33.4484, lon=-112.074
                                        )
                                        assert result["level"] == "low"

    @pytest.mark.asyncio
    async def test_risk_level_critical(self, safety_scorer):
        """Test that high scores result in 'critical' risk level."""
        # Mock internal methods to return high scores
        with patch.object(safety_scorer, '_check_high_risk_zone_proximity', return_value=1.0):
            with patch.object(safety_scorer, '_check_recent_gunfire_proximity', return_value=1.0):
                with patch.object(safety_scorer, '_check_repeat_offender_proximity', return_value=1.0):
                    with patch.object(safety_scorer, '_check_vehicle_of_interest_proximity', return_value=1.0):
                        with patch.object(safety_scorer, '_check_active_cad_hazards', return_value=1.0):
                            with patch.object(safety_scorer, '_check_known_threats_at_location', return_value=1.0):
                                with patch.object(safety_scorer, '_check_time_of_day_patterns', return_value=1.0):
                                    with patch.object(safety_scorer, '_check_ai_anomalies', return_value=1.0):
                                        result = await safety_scorer.calculate_score(
                                            badge="1234", lat=33.4484, lon=-112.074
                                        )
                                        assert result["level"] == "critical"

    @pytest.mark.asyncio
    async def test_factor_weights_sum_to_one(self, safety_scorer):
        """Test that factor weights sum to 1.0."""
        total_weight = sum(safety_scorer.FACTOR_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001

    @pytest.mark.asyncio
    async def test_factors_included_in_result(self, safety_scorer):
        """Test that all factors are included in result."""
        result = await safety_scorer.calculate_score(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        expected_factors = [
            "high_risk_zone_proximity",
            "recent_gunfire_proximity",
            "repeat_offender_proximity",
            "vehicle_of_interest_proximity",
            "active_cad_hazards",
            "known_threats_at_location",
            "time_of_day_patterns",
            "ai_anomalies",
        ]

        factor_names = [f["factor"] for f in result["factors"]]
        for expected in expected_factors:
            assert expected in factor_names

    @pytest.mark.asyncio
    async def test_factor_details_structure(self, safety_scorer):
        """Test that factor details have correct structure."""
        result = await safety_scorer.calculate_score(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        for factor in result["factors"]:
            assert "factor" in factor
            assert "score" in factor
            assert "weight" in factor
            assert "contribution" in factor
            assert 0.0 <= factor["score"] <= 1.0
            assert 0.0 <= factor["weight"] <= 1.0

    def test_determine_risk_level_low(self, safety_scorer):
        """Test risk level determination for low scores."""
        assert safety_scorer._determine_risk_level(0.0) == "low"
        assert safety_scorer._determine_risk_level(0.1) == "low"
        assert safety_scorer._determine_risk_level(0.19) == "low"

    def test_determine_risk_level_moderate(self, safety_scorer):
        """Test risk level determination for moderate scores."""
        assert safety_scorer._determine_risk_level(0.2) == "moderate"
        assert safety_scorer._determine_risk_level(0.3) == "moderate"
        assert safety_scorer._determine_risk_level(0.39) == "moderate"

    def test_determine_risk_level_elevated(self, safety_scorer):
        """Test risk level determination for elevated scores."""
        assert safety_scorer._determine_risk_level(0.4) == "elevated"
        assert safety_scorer._determine_risk_level(0.5) == "elevated"
        assert safety_scorer._determine_risk_level(0.59) == "elevated"

    def test_determine_risk_level_high(self, safety_scorer):
        """Test risk level determination for high scores."""
        assert safety_scorer._determine_risk_level(0.6) == "high"
        assert safety_scorer._determine_risk_level(0.7) == "high"
        assert safety_scorer._determine_risk_level(0.79) == "high"

    def test_determine_risk_level_critical(self, safety_scorer):
        """Test risk level determination for critical scores."""
        assert safety_scorer._determine_risk_level(0.8) == "critical"
        assert safety_scorer._determine_risk_level(0.9) == "critical"
        assert safety_scorer._determine_risk_level(1.0) == "critical"


class TestGetSafetyScorer:
    """Tests for the singleton getter function."""

    def test_get_safety_scorer_returns_instance(self):
        """Test that get_safety_scorer returns an instance."""
        scorer = get_safety_scorer()
        assert isinstance(scorer, OfficerSafetyScorer)

    def test_get_safety_scorer_singleton(self):
        """Test that get_safety_scorer returns the same instance."""
        scorer1 = get_safety_scorer()
        scorer2 = get_safety_scorer()
        assert scorer1 is scorer2
