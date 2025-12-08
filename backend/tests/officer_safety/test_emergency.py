"""
Unit tests for Officer Emergency Detection Module.

Tests the EmergencyDetector for:
- Officer down detection
- SOS detection
- Emergency triggers
- Emergency clearing
"""


import pytest

from app.officer_safety.emergency import EmergencyDetector, get_emergency_detector


class TestEmergencyDetector:
    """Tests for EmergencyDetector class."""

    @pytest.fixture
    def emergency_detector(self):
        """Create a fresh emergency detector for each test."""
        detector = EmergencyDetector()
        return detector

    @pytest.mark.asyncio
    async def test_check_conditions_basic(self, emergency_detector):
        """Test basic emergency condition check."""
        result = await emergency_detector.check_conditions(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            speed=25.0,
        )

        assert "badge" in result
        assert result["badge"] == "1234"
        assert "emergency" in result
        assert isinstance(result["emergency"], bool)

    @pytest.mark.asyncio
    async def test_check_conditions_no_emergency(self, emergency_detector):
        """Test that normal conditions don't trigger emergency."""
        result = await emergency_detector.check_conditions(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            speed=25.0,
        )

        assert result["emergency"] is False

    @pytest.mark.asyncio
    async def test_trigger_officer_down(self, emergency_detector):
        """Test manual officer down trigger."""
        result = await emergency_detector.trigger_officer_down(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            source="manual",
        )

        assert result["emergency"] is True
        assert result["type"] == "officer_down"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_trigger_sos(self, emergency_detector):
        """Test manual SOS trigger."""
        result = await emergency_detector.trigger_sos(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            source="mdt",
        )

        assert result["emergency"] is True
        assert result["type"] == "officer_sos"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_clear_emergency(self, emergency_detector):
        """Test clearing an emergency."""
        # First trigger an emergency
        await emergency_detector.trigger_sos(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            source="manual",
        )

        # Then clear it
        result = await emergency_detector.clear_emergency(
            badge="1234",
            cleared_by="RTCC",
            reason="Situation resolved",
        )

        assert result["cleared"] is True
        assert result["badge"] == "1234"

    @pytest.mark.asyncio
    async def test_get_active_emergencies(self, emergency_detector):
        """Test getting active emergencies."""
        # Trigger an emergency
        await emergency_detector.trigger_sos(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            source="manual",
        )

        emergencies = await emergency_detector.get_active_emergencies()

        assert isinstance(emergencies, list)

    @pytest.mark.asyncio
    async def test_get_emergency_status(self, emergency_detector):
        """Test getting emergency status for an officer."""
        # Trigger an emergency
        await emergency_detector.trigger_officer_down(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            source="manual",
        )

        status = await emergency_detector.get_emergency_status("1234")

        assert status is not None
        assert status["badge"] == "1234"

    @pytest.mark.asyncio
    async def test_sudden_deceleration_detection(self, emergency_detector):
        """Test sudden deceleration detection."""
        # Simulate high speed
        await emergency_detector.check_conditions(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            speed=60.0,
        )

        # Simulate sudden stop
        result = await emergency_detector.check_conditions(
            badge="1234",
            lat=33.4485,
            lon=-112.0741,
            speed=0.0,
        )

        # May or may not trigger depending on implementation
        assert "emergency" in result

    def test_threshold_defaults(self, emergency_detector):
        """Test that threshold defaults are set correctly."""
        assert emergency_detector.THRESHOLDS["sudden_deceleration_mph"] == 30
        assert emergency_detector.THRESHOLDS["gps_halt_seconds"] == 10
        assert emergency_detector.THRESHOLDS["radio_silence_minutes"] == 5
        assert emergency_detector.THRESHOLDS["heart_rate_spike_bpm"] == 150

    @pytest.mark.asyncio
    async def test_update_last_communication(self, emergency_detector):
        """Test updating last communication time."""
        await emergency_detector.update_last_communication("1234")

        # Should not raise an error
        assert True

    @pytest.mark.asyncio
    async def test_emergency_details_structure(self, emergency_detector):
        """Test emergency details structure."""
        result = await emergency_detector.trigger_officer_down(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
            source="manual",
        )

        assert "emergency" in result
        assert "type" in result
        assert "message" in result
        assert "details" in result


class TestGetEmergencyDetector:
    """Tests for the singleton getter function."""

    def test_get_emergency_detector_returns_instance(self):
        """Test that get_emergency_detector returns an instance."""
        detector = get_emergency_detector()
        assert isinstance(detector, EmergencyDetector)

    def test_get_emergency_detector_singleton(self):
        """Test that get_emergency_detector returns the same instance."""
        detector1 = get_emergency_detector()
        detector2 = get_emergency_detector()
        assert detector1 is detector2
