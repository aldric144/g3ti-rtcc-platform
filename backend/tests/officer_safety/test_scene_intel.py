"""
Unit tests for Scene Intelligence Engine.

Tests the SceneIntelligenceEngine for:
- RTCC Field Packet generation
- Location history gathering
- Risk level calculation
- Recommendations generation
"""


import pytest

from app.officer_safety.scene_intel import SceneIntelligenceEngine, get_scene_intel


class TestSceneIntelligenceEngine:
    """Tests for SceneIntelligenceEngine class."""

    @pytest.fixture
    def scene_intel(self):
        """Create a fresh scene intel engine for each test."""
        engine = SceneIntelligenceEngine()
        return engine

    @pytest.mark.asyncio
    async def test_get_intelligence_by_address(self, scene_intel):
        """Test getting intelligence by address."""
        result = await scene_intel.get_intelligence(
            address="123 Main Street, Phoenix, AZ 85001"
        )

        assert "packet_id" in result
        assert "location" in result
        assert "risk_level" in result
        assert "history" in result
        assert "recommendations" in result
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_get_intelligence_by_coordinates(self, scene_intel):
        """Test getting intelligence by coordinates."""
        result = await scene_intel.get_intelligence(
            lat=33.4484,
            lon=-112.074,
        )

        assert "packet_id" in result
        assert "location" in result
        assert "risk_level" in result

    @pytest.mark.asyncio
    async def test_get_intelligence_by_incident(self, scene_intel):
        """Test getting intelligence by incident ID."""
        result = await scene_intel.get_intelligence(
            incident_id="INC-12345"
        )

        assert "packet_id" in result
        assert "location" in result

    @pytest.mark.asyncio
    async def test_field_packet_structure(self, scene_intel):
        """Test that field packet has correct structure."""
        result = await scene_intel.get_intelligence(
            address="123 Main Street"
        )

        expected_fields = [
            "packet_id",
            "location",
            "generated_at",
            "risk_level",
            "history",
            "known_associates",
            "prior_violence",
            "weapons_associated",
            "vehicles_of_interest",
            "nearby_offenders",
            "recommendations",
            "summary",
        ]

        for field in expected_fields:
            assert field in result

    @pytest.mark.asyncio
    async def test_risk_level_values(self, scene_intel):
        """Test that risk level is valid."""
        result = await scene_intel.get_intelligence(
            address="123 Main Street"
        )

        valid_levels = ["low", "moderate", "elevated", "high", "critical"]
        assert result["risk_level"] in valid_levels

    @pytest.mark.asyncio
    async def test_recommendations_list(self, scene_intel):
        """Test that recommendations is a list."""
        result = await scene_intel.get_intelligence(
            address="123 Main Street"
        )

        assert isinstance(result["recommendations"], list)

    @pytest.mark.asyncio
    async def test_history_list(self, scene_intel):
        """Test that history is a list."""
        result = await scene_intel.get_intelligence(
            address="123 Main Street"
        )

        assert isinstance(result["history"], list)

    @pytest.mark.asyncio
    async def test_known_associates_list(self, scene_intel):
        """Test that known associates is a list."""
        result = await scene_intel.get_intelligence(
            address="123 Main Street"
        )

        assert isinstance(result["known_associates"], list)

    @pytest.mark.asyncio
    async def test_weapons_associated_list(self, scene_intel):
        """Test that weapons associated is a list."""
        result = await scene_intel.get_intelligence(
            address="123 Main Street"
        )

        assert isinstance(result["weapons_associated"], list)

    @pytest.mark.asyncio
    async def test_prior_violence_boolean(self, scene_intel):
        """Test that prior violence is a boolean."""
        result = await scene_intel.get_intelligence(
            address="123 Main Street"
        )

        assert isinstance(result["prior_violence"], bool)


class TestGetSceneIntel:
    """Tests for the singleton getter function."""

    def test_get_scene_intel_returns_instance(self):
        """Test that get_scene_intel returns an instance."""
        engine = get_scene_intel()
        assert isinstance(engine, SceneIntelligenceEngine)

    def test_get_scene_intel_singleton(self):
        """Test that get_scene_intel returns the same instance."""
        engine1 = get_scene_intel()
        engine2 = get_scene_intel()
        assert engine1 is engine2
