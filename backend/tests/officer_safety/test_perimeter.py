"""
Unit tests for Dynamic Perimeter & Approach Engine.

Tests the PerimeterEngine for:
- Perimeter generation
- Route calculation
- Risk multiplier calculation
- Staging area identification
"""


import pytest

from app.officer_safety.perimeter import PerimeterEngine, get_perimeter_engine


class TestPerimeterEngine:
    """Tests for PerimeterEngine class."""

    @pytest.fixture
    def perimeter_engine(self):
        """Create a fresh perimeter engine for each test."""
        engine = PerimeterEngine()
        return engine

    @pytest.mark.asyncio
    async def test_generate_perimeter_basic(self, perimeter_engine):
        """Test basic perimeter generation."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12", "Bravo-21"],
        )

        assert "perimeter_id" in result
        assert "incident_id" in result
        assert result["incident_id"] == "INC-12345"
        assert "center" in result
        assert "inner_perimeter" in result
        assert "outer_perimeter" in result

    @pytest.mark.asyncio
    async def test_generate_perimeter_with_incident_type(self, perimeter_engine):
        """Test perimeter generation with incident type."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
            incident_type="active_shooter",
        )

        # Active shooter should have larger perimeter
        assert result["inner_perimeter"]["radius_m"] >= 150

    @pytest.mark.asyncio
    async def test_perimeter_structure(self, perimeter_engine):
        """Test that perimeter has correct structure."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
        )

        expected_fields = [
            "perimeter_id",
            "incident_id",
            "center",
            "generated_at",
            "inner_perimeter",
            "outer_perimeter",
            "routes",
            "staging_areas",
            "escape_routes",
            "units_assigned",
            "risk_multiplier",
            "recommendations",
        ]

        for field in expected_fields:
            assert field in result

    @pytest.mark.asyncio
    async def test_inner_perimeter_structure(self, perimeter_engine):
        """Test inner perimeter structure."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
        )

        inner = result["inner_perimeter"]
        assert "radius_m" in inner
        assert "polygon" in inner
        assert "description" in inner
        assert isinstance(inner["polygon"], list)

    @pytest.mark.asyncio
    async def test_outer_perimeter_structure(self, perimeter_engine):
        """Test outer perimeter structure."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
        )

        outer = result["outer_perimeter"]
        assert "radius_m" in outer
        assert "polygon" in outer
        assert "description" in outer
        assert outer["radius_m"] > result["inner_perimeter"]["radius_m"]

    @pytest.mark.asyncio
    async def test_routes_structure(self, perimeter_engine):
        """Test routes structure."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
        )

        routes = result["routes"]
        assert "blue_routes" in routes
        assert "red_routes" in routes
        assert isinstance(routes["blue_routes"], list)
        assert isinstance(routes["red_routes"], list)

    @pytest.mark.asyncio
    async def test_blue_route_structure(self, perimeter_engine):
        """Test blue route structure."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
        )

        if result["routes"]["blue_routes"]:
            route = result["routes"]["blue_routes"][0]
            assert "direction" in route
            assert "approach_point" in route
            assert "distance_m" in route
            assert "cover_available" in route

    @pytest.mark.asyncio
    async def test_staging_areas_list(self, perimeter_engine):
        """Test staging areas is a list."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
        )

        assert isinstance(result["staging_areas"], list)

    @pytest.mark.asyncio
    async def test_escape_routes_list(self, perimeter_engine):
        """Test escape routes is a list."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
        )

        assert isinstance(result["escape_routes"], list)

    @pytest.mark.asyncio
    async def test_risk_multiplier_default(self, perimeter_engine):
        """Test default risk multiplier."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
        )

        assert result["risk_multiplier"] >= 1.0

    @pytest.mark.asyncio
    async def test_risk_multiplier_with_weapon(self, perimeter_engine):
        """Test risk multiplier with weapon context."""
        result = await perimeter_engine.generate_perimeter(
            incident_id="INC-12345",
            lat=33.4484,
            lon=-112.074,
            units=["Charlie-12"],
            context={"weapon_type": "firearm"},
        )

        assert result["risk_multiplier"] >= 1.0

    def test_base_radii_by_incident_type(self, perimeter_engine):
        """Test base radii configuration."""
        assert "active_shooter" in perimeter_engine.BASE_RADII
        assert "armed_robbery" in perimeter_engine.BASE_RADII
        assert "hostage" in perimeter_engine.BASE_RADII
        assert "default" in perimeter_engine.BASE_RADII


class TestGetPerimeterEngine:
    """Tests for the singleton getter function."""

    def test_get_perimeter_engine_returns_instance(self):
        """Test that get_perimeter_engine returns an instance."""
        engine = get_perimeter_engine()
        assert isinstance(engine, PerimeterEngine)

    def test_get_perimeter_engine_singleton(self):
        """Test that get_perimeter_engine returns the same instance."""
        engine1 = get_perimeter_engine()
        engine2 = get_perimeter_engine()
        assert engine1 is engine2
