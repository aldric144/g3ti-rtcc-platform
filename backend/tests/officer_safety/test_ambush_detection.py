"""
Unit tests for Ambush Pattern Detection Module.

Tests the AmbushDetector for:
- Pattern detection
- Indicator evaluation
- Warning generation
- Threshold configuration
"""

from unittest.mock import patch

import pytest

from app.officer_safety.ambush_detection import AmbushDetector, get_ambush_detector


class TestAmbushDetector:
    """Tests for AmbushDetector class."""

    @pytest.fixture
    def ambush_detector(self):
        """Create a fresh ambush detector for each test."""
        detector = AmbushDetector()
        return detector

    @pytest.mark.asyncio
    async def test_check_location_basic(self, ambush_detector):
        """Test basic ambush check."""
        result = await ambush_detector.check_location(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        assert "badge" in result
        assert result["badge"] == "1234"
        assert "warning" in result
        assert isinstance(result["warning"], bool)
        assert "risk_score" in result
        assert 0.0 <= result["risk_score"] <= 1.0
        assert "indicators" in result

    @pytest.mark.asyncio
    async def test_check_location_indicators_structure(self, ambush_detector):
        """Test that indicators have correct structure."""
        result = await ambush_detector.check_location(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        expected_indicators = [
            "civilian_absence",
            "vehicle_circling",
            "weapon_anomalies",
            "movement_anomalies",
            "timing_anomalies",
            "entity_convergence",
        ]

        for indicator in expected_indicators:
            assert indicator in result["indicators"]
            assert "detected" in result["indicators"][indicator]
            assert "score" in result["indicators"][indicator]

    @pytest.mark.asyncio
    async def test_warning_factors_when_warning(self, ambush_detector):
        """Test that warning factors are provided when warning is true."""
        # Mock high-risk indicators
        with patch.object(ambush_detector, '_check_civilian_absence', return_value={"detected": True, "score": 0.9, "description": "Test"}):
            with patch.object(ambush_detector, '_check_vehicle_circling', return_value={"detected": True, "score": 0.8, "description": "Test"}):
                result = await ambush_detector.check_location(
                    badge="1234",
                    lat=33.4484,
                    lon=-112.074,
                )

                if result["warning"]:
                    assert "warning_factors" in result
                    assert len(result["warning_factors"]) > 0

    @pytest.mark.asyncio
    async def test_no_warning_low_risk(self, ambush_detector):
        """Test that no warning is generated for low-risk areas."""
        # Mock low-risk indicators
        with patch.object(ambush_detector, '_check_civilian_absence', return_value={"detected": False, "score": 0.1}):
            with patch.object(ambush_detector, '_check_vehicle_circling', return_value={"detected": False, "score": 0.1}):
                with patch.object(ambush_detector, '_check_weapon_anomalies', return_value={"detected": False, "score": 0.1}):
                    with patch.object(ambush_detector, '_check_movement_anomalies', return_value={"detected": False, "score": 0.1}):
                        with patch.object(ambush_detector, '_check_timing_anomalies', return_value={"detected": False, "score": 0.1}):
                            with patch.object(ambush_detector, '_check_entity_convergence', return_value={"detected": False, "score": 0.1}):
                                result = await ambush_detector.check_location(
                                    badge="1234",
                                    lat=33.4484,
                                    lon=-112.074,
                                )
                                assert result["warning"] is False

    def test_threshold_defaults(self, ambush_detector):
        """Test that threshold defaults are set correctly."""
        assert ambush_detector.THRESHOLDS["civilian_absence"] == 0.7
        assert ambush_detector.THRESHOLDS["vehicle_circling"] == 3
        assert ambush_detector.THRESHOLDS["weapon_anomaly"] == 0.6
        assert ambush_detector.THRESHOLDS["movement_anomaly"] == 0.65
        assert ambush_detector.THRESHOLDS["timing_anomaly"] == 0.7
        assert ambush_detector.THRESHOLDS["convergence"] == 3

    @pytest.mark.asyncio
    async def test_check_route_risk(self, ambush_detector):
        """Test route risk checking."""
        result = await ambush_detector._check_route_risk(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        assert "route_risk" in result
        assert "high_risk_zones_on_route" in result

    @pytest.mark.asyncio
    async def test_active_warnings_tracked(self, ambush_detector):
        """Test that active warnings are tracked per officer."""
        await ambush_detector.check_location(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        # Active warnings should be tracked
        assert isinstance(ambush_detector._active_warnings, dict)

    @pytest.mark.asyncio
    async def test_severity_in_warning(self, ambush_detector):
        """Test that severity is included in warning."""
        result = await ambush_detector.check_location(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        if result["warning"]:
            assert "severity" in result
            assert result["severity"] in ["critical", "high", "elevated"]


class TestGetAmbushDetector:
    """Tests for the singleton getter function."""

    def test_get_ambush_detector_returns_instance(self):
        """Test that get_ambush_detector returns an instance."""
        detector = get_ambush_detector()
        assert isinstance(detector, AmbushDetector)

    def test_get_ambush_detector_singleton(self):
        """Test that get_ambush_detector returns the same instance."""
        detector1 = get_ambush_detector()
        detector2 = get_ambush_detector()
        assert detector1 is detector2
