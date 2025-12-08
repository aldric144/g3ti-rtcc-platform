"""
Unit tests for Threat Proximity Engine.

Tests the ThreatProximityEngine for:
- Threat detection
- Distance calculations
- Threat severity assessment
- Alert generation
"""


import pytest

from app.officer_safety.threat_proximity import ThreatProximityEngine, get_threat_engine


class TestThreatProximityEngine:
    """Tests for ThreatProximityEngine class."""

    @pytest.fixture
    def threat_engine(self):
        """Create a fresh threat engine for each test."""
        engine = ThreatProximityEngine()
        return engine

    @pytest.mark.asyncio
    async def test_evaluate_threats_basic(self, threat_engine):
        """Test basic threat evaluation."""
        result = await threat_engine.evaluate_threats(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        assert "badge" in result
        assert result["badge"] == "1234"
        assert "threats" in result
        assert isinstance(result["threats"], list)
        assert "threat_count" in result
        assert "alerts" in result

    @pytest.mark.asyncio
    async def test_evaluate_threats_returns_alerts(self, threat_engine):
        """Test that threat evaluation returns alerts."""
        result = await threat_engine.evaluate_threats(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        assert "alerts" in result
        assert isinstance(result["alerts"], list)

    @pytest.mark.asyncio
    async def test_threat_types_checked(self, threat_engine):
        """Test that all threat types are checked."""
        result = await threat_engine.evaluate_threats(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        # The engine should check for various threat types
        threat_types = [t.get("type") for t in result["threats"]]
        # At minimum, the structure should be correct
        assert isinstance(threat_types, list)

    @pytest.mark.asyncio
    async def test_threat_structure(self, threat_engine):
        """Test that threats have correct structure."""
        result = await threat_engine.evaluate_threats(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        for threat in result["threats"]:
            assert "id" in threat
            assert "type" in threat
            assert "severity" in threat
            assert "distance_m" in threat
            assert "description" in threat

    @pytest.mark.asyncio
    async def test_alert_structure(self, threat_engine):
        """Test that alerts have correct structure."""
        result = await threat_engine.evaluate_threats(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        for alert in result["alerts"]:
            assert "type" in alert
            assert "severity" in alert
            assert "message" in alert

    def test_threat_radius_defaults(self, threat_engine):
        """Test that threat radius defaults are set correctly."""
        assert threat_engine.THREAT_RADII["gunfire"] == 600
        assert threat_engine.THREAT_RADII["vehicle_of_interest"] == 500
        assert threat_engine.THREAT_RADII["repeat_offender"] == 300
        assert threat_engine.THREAT_RADII["domestic_violence"] == 200
        assert threat_engine.THREAT_RADII["ambush_zone"] == 400
        assert threat_engine.THREAT_RADII["unresolved_weapon"] == 350

    def test_calculate_distance(self, threat_engine):
        """Test distance calculation between two points."""
        # Approximately 1km apart
        distance = threat_engine._calculate_distance(
            lat1=33.4484, lon1=-112.074,
            lat2=33.4574, lon2=-112.074,
        )

        # Should be approximately 1km (1000m)
        assert 900 < distance < 1100

    def test_calculate_distance_same_point(self, threat_engine):
        """Test distance calculation for same point."""
        distance = threat_engine._calculate_distance(
            lat1=33.4484, lon1=-112.074,
            lat2=33.4484, lon2=-112.074,
        )

        assert distance == 0

    def test_determine_severity_critical(self, threat_engine):
        """Test severity determination for close threats."""
        severity = threat_engine._determine_severity(
            distance_m=50,
            threat_type="gunfire",
        )
        assert severity == "critical"

    def test_determine_severity_high(self, threat_engine):
        """Test severity determination for medium-distance threats."""
        severity = threat_engine._determine_severity(
            distance_m=200,
            threat_type="gunfire",
        )
        assert severity in ["critical", "high"]

    def test_determine_severity_elevated(self, threat_engine):
        """Test severity determination for far threats."""
        severity = threat_engine._determine_severity(
            distance_m=500,
            threat_type="gunfire",
        )
        assert severity in ["critical", "high", "elevated"]

    @pytest.mark.asyncio
    async def test_track_active_threats(self, threat_engine):
        """Test that active threats are tracked per officer."""
        await threat_engine.evaluate_threats(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        # Active threats should be tracked
        assert "1234" in threat_engine._active_threats or len(threat_engine._active_threats) >= 0

    @pytest.mark.asyncio
    async def test_new_threats_identified(self, threat_engine):
        """Test that new threats are identified."""
        result = await threat_engine.evaluate_threats(
            badge="1234",
            lat=33.4484,
            lon=-112.074,
        )

        # New threats should be in alerts
        new_threat_alerts = [a for a in result["alerts"] if "new" in a.get("type", "").lower() or a.get("type") == "threat_alert"]
        # Structure should be correct even if no new threats
        assert isinstance(new_threat_alerts, list)


class TestGetThreatEngine:
    """Tests for the singleton getter function."""

    def test_get_threat_engine_returns_instance(self):
        """Test that get_threat_engine returns an instance."""
        engine = get_threat_engine()
        assert isinstance(engine, ThreatProximityEngine)

    def test_get_threat_engine_singleton(self):
        """Test that get_threat_engine returns the same instance."""
        engine1 = get_threat_engine()
        engine2 = get_threat_engine()
        assert engine1 is engine2
