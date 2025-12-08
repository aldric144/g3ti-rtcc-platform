"""
Unit tests for Officer Location Telemetry Ingestion.

Tests the OfficerTelemetryManager for:
- GPS position updates
- Position smoothing
- Officer state tracking
- Status change events
- History tracking
"""

from datetime import datetime

import pytest

from app.officer_safety.telemetry import OfficerTelemetryManager, get_telemetry_manager


class TestOfficerTelemetryManager:
    """Tests for OfficerTelemetryManager class."""

    @pytest.fixture
    def telemetry_manager(self):
        """Create a fresh telemetry manager for each test."""
        manager = OfficerTelemetryManager()
        return manager

    @pytest.mark.asyncio
    async def test_update_position_new_officer(self, telemetry_manager):
        """Test updating position for a new officer."""
        result = await telemetry_manager.update_position(
            badge="1234",
            unit="Charlie-12",
            lat=33.4484,
            lon=-112.074,
            speed=25.0,
            heading=180,
            status="on_patrol",
        )

        assert result["badge"] == "1234"
        assert result["unit"] == "Charlie-12"
        assert result["status"] == "on_patrol"
        assert "smoothed_lat" in result
        assert "smoothed_lon" in result

    @pytest.mark.asyncio
    async def test_update_position_existing_officer(self, telemetry_manager):
        """Test updating position for an existing officer."""
        # First update
        await telemetry_manager.update_position(
            badge="1234",
            unit="Charlie-12",
            lat=33.4484,
            lon=-112.074,
            speed=25.0,
            heading=180,
            status="on_patrol",
        )

        # Second update
        result = await telemetry_manager.update_position(
            badge="1234",
            unit="Charlie-12",
            lat=33.4485,
            lon=-112.0741,
            speed=30.0,
            heading=185,
            status="on_patrol",
        )

        assert result["badge"] == "1234"
        assert result["status"] == "on_patrol"

    @pytest.mark.asyncio
    async def test_update_position_status_change(self, telemetry_manager):
        """Test status change detection."""
        # Initial status
        await telemetry_manager.update_position(
            badge="1234",
            unit="Charlie-12",
            lat=33.4484,
            lon=-112.074,
            speed=25.0,
            heading=180,
            status="on_patrol",
        )

        # Change status
        result = await telemetry_manager.update_position(
            badge="1234",
            unit="Charlie-12",
            lat=33.4485,
            lon=-112.0741,
            speed=0.0,
            heading=180,
            status="on_scene",
        )

        assert result["status"] == "on_scene"
        assert result.get("status_changed") is True

    @pytest.mark.asyncio
    async def test_get_officer_position(self, telemetry_manager):
        """Test retrieving officer position."""
        await telemetry_manager.update_position(
            badge="1234",
            unit="Charlie-12",
            lat=33.4484,
            lon=-112.074,
            speed=25.0,
            heading=180,
            status="on_patrol",
        )

        position = await telemetry_manager.get_officer_position("1234")

        assert position is not None
        assert position["badge"] == "1234"
        assert position["unit"] == "Charlie-12"

    @pytest.mark.asyncio
    async def test_get_officer_position_not_found(self, telemetry_manager):
        """Test retrieving position for non-existent officer."""
        position = await telemetry_manager.get_officer_position("9999")
        assert position is None

    @pytest.mark.asyncio
    async def test_get_all_officers(self, telemetry_manager):
        """Test retrieving all officer positions."""
        # Add multiple officers
        await telemetry_manager.update_position(
            badge="1234", unit="Charlie-12", lat=33.4484, lon=-112.074,
            speed=25.0, heading=180, status="on_patrol"
        )
        await telemetry_manager.update_position(
            badge="5678", unit="Bravo-21", lat=33.4512, lon=-112.068,
            speed=0.0, heading=90, status="on_scene"
        )

        officers = await telemetry_manager.get_all_officers()

        assert len(officers) >= 2
        badges = [o["badge"] for o in officers]
        assert "1234" in badges
        assert "5678" in badges

    @pytest.mark.asyncio
    async def test_get_officers_by_status(self, telemetry_manager):
        """Test filtering officers by status."""
        await telemetry_manager.update_position(
            badge="1234", unit="Charlie-12", lat=33.4484, lon=-112.074,
            speed=25.0, heading=180, status="on_patrol"
        )
        await telemetry_manager.update_position(
            badge="5678", unit="Bravo-21", lat=33.4512, lon=-112.068,
            speed=0.0, heading=90, status="on_scene"
        )

        on_patrol = await telemetry_manager.get_officers_by_status("on_patrol")
        on_scene = await telemetry_manager.get_officers_by_status("on_scene")

        assert any(o["badge"] == "1234" for o in on_patrol)
        assert any(o["badge"] == "5678" for o in on_scene)

    @pytest.mark.asyncio
    async def test_get_nearby_officers(self, telemetry_manager):
        """Test finding officers near a location."""
        await telemetry_manager.update_position(
            badge="1234", unit="Charlie-12", lat=33.4484, lon=-112.074,
            speed=25.0, heading=180, status="on_patrol"
        )
        await telemetry_manager.update_position(
            badge="5678", unit="Bravo-21", lat=33.4512, lon=-112.068,
            speed=0.0, heading=90, status="on_scene"
        )

        nearby = await telemetry_manager.get_nearby_officers(
            lat=33.4484, lon=-112.074, radius_km=1.0
        )

        assert len(nearby) >= 1

    @pytest.mark.asyncio
    async def test_get_officer_history(self, telemetry_manager):
        """Test retrieving officer position history."""
        # Add multiple positions
        for i in range(5):
            await telemetry_manager.update_position(
                badge="1234", unit="Charlie-12",
                lat=33.4484 + i * 0.001, lon=-112.074 + i * 0.001,
                speed=25.0, heading=180, status="on_patrol"
            )

        history = await telemetry_manager.get_officer_history("1234", limit=10)

        assert len(history) >= 1

    def test_smooth_position_single_point(self, telemetry_manager):
        """Test position smoothing with single point."""
        smoothed = telemetry_manager._smooth_position(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        assert smoothed["lat"] == 33.4484
        assert smoothed["lon"] == -112.074

    def test_smooth_position_multiple_points(self, telemetry_manager):
        """Test position smoothing with multiple points."""
        # Add some history
        telemetry_manager._position_history["1234"] = [
            {"lat": 33.4480, "lon": -112.0740, "timestamp": datetime.utcnow()},
            {"lat": 33.4482, "lon": -112.0741, "timestamp": datetime.utcnow()},
            {"lat": 33.4484, "lon": -112.0742, "timestamp": datetime.utcnow()},
        ]

        smoothed = telemetry_manager._smooth_position(
            badge="1234",
            lat=33.4486,
            lon=-112.0743,
        )

        # Smoothed position should be between raw and historical average
        assert 33.4480 <= smoothed["lat"] <= 33.4490
        assert -112.0750 <= smoothed["lon"] <= -112.0740

    def test_calculate_distance(self, telemetry_manager):
        """Test distance calculation between two points."""
        # Approximately 1km apart
        distance = telemetry_manager._calculate_distance(
            lat1=33.4484, lon1=-112.074,
            lat2=33.4574, lon2=-112.074,
        )

        # Should be approximately 1km (1000m)
        assert 900 < distance < 1100


class TestGetTelemetryManager:
    """Tests for the singleton getter function."""

    def test_get_telemetry_manager_returns_instance(self):
        """Test that get_telemetry_manager returns an instance."""
        manager = get_telemetry_manager()
        assert isinstance(manager, OfficerTelemetryManager)

    def test_get_telemetry_manager_singleton(self):
        """Test that get_telemetry_manager returns the same instance."""
        manager1 = get_telemetry_manager()
        manager2 = get_telemetry_manager()
        assert manager1 is manager2
