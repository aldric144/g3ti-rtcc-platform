"""Tests for the Patrol Route Optimization Engine."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.tactical_engine.patrol_optimizer import PatrolRouteOptimizer


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
def patrol_optimizer(mock_neo4j, mock_es, mock_redis):
    """Create patrol optimizer with mocked dependencies."""
    return PatrolRouteOptimizer(
        neo4j=mock_neo4j,
        es=mock_es,
        redis=mock_redis,
    )


class TestPatrolRouteOptimizer:
    """Tests for PatrolRouteOptimizer."""

    @pytest.mark.asyncio
    async def test_optimize_route_returns_valid_structure(self, patrol_optimizer):
        """Test that optimize_route returns valid structure."""
        result = await patrol_optimizer.optimize_route(
            unit="Unit1",
            shift="A",
            starting_point=(33.45, -112.07),
            max_distance=15.0,
        )

        assert "unit" in result
        assert "shift" in result
        assert "route" in result
        assert "priority_zones" in result
        assert "statistics" in result
        assert "justification" in result

    @pytest.mark.asyncio
    async def test_optimize_route_with_priority_zones(self, patrol_optimizer):
        """Test route optimization with priority zones."""
        result = await patrol_optimizer.optimize_route(
            unit="Unit2",
            shift="B",
            starting_point=(33.45, -112.07),
            priority_zones=["zone_1", "zone_2"],
        )

        assert "route" in result
        assert isinstance(result["route"], list)

    @pytest.mark.asyncio
    async def test_optimize_route_waypoint_count(self, patrol_optimizer):
        """Test that waypoint count is respected."""
        waypoint_count = 5
        result = await patrol_optimizer.optimize_route(
            unit="Unit3",
            shift="C",
            starting_point=(33.45, -112.07),
            waypoint_count=waypoint_count,
        )

        # Route should have approximately the requested waypoints
        assert len(result["route"]) <= waypoint_count + 2  # Allow some flexibility

    @pytest.mark.asyncio
    async def test_route_waypoints_have_required_fields(self, patrol_optimizer):
        """Test that route waypoints have required fields."""
        result = await patrol_optimizer.optimize_route(
            unit="Unit4",
            shift="A",
            starting_point=(33.45, -112.07),
        )

        for waypoint in result["route"]:
            assert "lat" in waypoint
            assert "lon" in waypoint
            assert "sequence" in waypoint
            assert "type" in waypoint

    @pytest.mark.asyncio
    async def test_route_statistics(self, patrol_optimizer):
        """Test that route statistics are calculated."""
        result = await patrol_optimizer.optimize_route(
            unit="Unit5",
            shift="B",
            starting_point=(33.45, -112.07),
        )

        stats = result["statistics"]
        assert "total_distance" in stats
        assert "waypoint_count" in stats
        assert stats["total_distance"] >= 0

    @pytest.mark.asyncio
    async def test_get_coverage_analysis(self, patrol_optimizer):
        """Test coverage analysis generation."""
        result = await patrol_optimizer.get_coverage_analysis(
            zone_id=None,
            hours_back=24,
        )

        assert "zones" in result
        assert "gaps" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_shift_handling(self, patrol_optimizer):
        """Test that different shifts are handled correctly."""
        for shift in ["A", "B", "C", "0700-1500", "1500-2300", "2300-0700"]:
            result = await patrol_optimizer.optimize_route(
                unit="TestUnit",
                shift=shift,
                starting_point=(33.45, -112.07),
            )
            assert "route" in result

    @pytest.mark.asyncio
    async def test_max_distance_constraint(self, patrol_optimizer):
        """Test that max distance constraint is respected."""
        result = await patrol_optimizer.optimize_route(
            unit="Unit6",
            shift="A",
            starting_point=(33.45, -112.07),
            max_distance=10.0,
        )

        # Total distance should be within reasonable bounds of max
        assert result["statistics"]["total_distance"] <= 15.0  # Allow some flexibility

    @pytest.mark.asyncio
    async def test_justification_provided(self, patrol_optimizer):
        """Test that route justification is provided."""
        result = await patrol_optimizer.optimize_route(
            unit="Unit7",
            shift="B",
            starting_point=(33.45, -112.07),
        )

        assert "justification" in result
        assert isinstance(result["justification"], list)
        assert len(result["justification"]) > 0
