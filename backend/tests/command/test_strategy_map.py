"""Tests for Strategy Map Engine."""

from datetime import datetime

import pytest

from app.command.strategy_map import (
    MapLayer,
    MarkerType,
    PerimeterType,
    ShapeType,
    StrategyMapManager,
)


class TestStrategyMapManager:
    """Test cases for StrategyMapManager."""

    @pytest.fixture
    def manager(self):
        """Create a StrategyMapManager instance."""
        return StrategyMapManager()

    @pytest.mark.asyncio
    async def test_create_map(self, manager):
        """Test creating a strategy map for an incident."""
        strategy_map = await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        assert strategy_map is not None
        assert strategy_map.incident_id == "inc-001"
        assert strategy_map.center_lat == 33.7490
        assert strategy_map.center_lng == -84.3880

    @pytest.mark.asyncio
    async def test_add_marker(self, manager):
        """Test adding a marker to the map."""
        await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        marker = await manager.add_marker(
            incident_id="inc-001",
            marker_type=MarkerType.UNIT,
            latitude=33.7495,
            longitude=-84.3885,
            label="Alpha-11",
            description="Patrol unit on scene",
            added_by="user-001",
        )

        assert marker is not None
        assert marker.marker_type == MarkerType.UNIT
        assert marker.label == "Alpha-11"

    @pytest.mark.asyncio
    async def test_add_shape(self, manager):
        """Test adding a shape to the map."""
        await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        shape = await manager.add_shape(
            incident_id="inc-001",
            shape_type=ShapeType.POLYGON,
            coordinates=[
                (33.7490, -84.3880),
                (33.7500, -84.3880),
                (33.7500, -84.3870),
                (33.7490, -84.3870),
            ],
            label="Hot Zone",
            color="#FF0000",
            added_by="user-001",
        )

        assert shape is not None
        assert shape.shape_type == ShapeType.POLYGON
        assert shape.label == "Hot Zone"

    @pytest.mark.asyncio
    async def test_draw_perimeter(self, manager):
        """Test drawing a perimeter."""
        await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        perimeter = await manager.draw_perimeter(
            incident_id="inc-001",
            perimeter_type=PerimeterType.OUTER,
            coordinates=[
                (33.7480, -84.3890),
                (33.7510, -84.3890),
                (33.7510, -84.3860),
                (33.7480, -84.3860),
            ],
            drawn_by="commander-001",
        )

        assert perimeter is not None
        assert perimeter.perimeter_type == PerimeterType.OUTER
        assert len(perimeter.coordinates) == 4

    @pytest.mark.asyncio
    async def test_toggle_layer(self, manager):
        """Test toggling a map layer."""
        await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        result = await manager.toggle_layer(
            incident_id="inc-001",
            layer=MapLayer.CAMERAS,
            visible=True,
            toggled_by="user-001",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_get_map(self, manager):
        """Test getting a strategy map."""
        await manager.create_map(
            incident_id="inc-002",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        # Add some elements
        await manager.add_marker(
            incident_id="inc-002",
            marker_type=MarkerType.CAMERA,
            latitude=33.7495,
            longitude=-84.3885,
            label="Camera 1",
            description="Street camera",
            added_by="user-001",
        )

        strategy_map = await manager.get_map(incident_id="inc-002")

        assert strategy_map is not None
        assert len(strategy_map.markers) >= 1

    @pytest.mark.asyncio
    async def test_update_unit_position(self, manager):
        """Test updating a unit's position on the map."""
        await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        result = await manager.update_unit_position(
            incident_id="inc-001",
            unit_id="Alpha-11",
            latitude=33.7492,
            longitude=-84.3882,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_add_gunfire_detection(self, manager):
        """Test adding a gunfire detection marker."""
        await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        marker = await manager.add_gunfire_detection(
            incident_id="inc-001",
            latitude=33.7493,
            longitude=-84.3878,
            rounds_detected=3,
            confidence=0.95,
            timestamp=datetime.utcnow(),
        )

        assert marker is not None
        assert marker.marker_type == MarkerType.GUNFIRE

    @pytest.mark.asyncio
    async def test_add_threat_zone(self, manager):
        """Test adding a threat zone."""
        await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        shape = await manager.add_threat_zone(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            radius_meters=100,
            threat_level="high",
            description="Active threat area",
            added_by="intel-001",
        )

        assert shape is not None
        assert shape.shape_type == ShapeType.CIRCLE

    @pytest.mark.asyncio
    async def test_remove_element(self, manager):
        """Test removing an element from the map."""
        await manager.create_map(
            incident_id="inc-001",
            center_lat=33.7490,
            center_lng=-84.3880,
            zoom_level=15,
            created_by="user-001",
        )

        marker = await manager.add_marker(
            incident_id="inc-001",
            marker_type=MarkerType.UNIT,
            latitude=33.7495,
            longitude=-84.3885,
            label="Test Unit",
            description="Test",
            added_by="user-001",
        )

        result = await manager.remove_element(
            incident_id="inc-001",
            element_id=marker.id,
            removed_by="user-001",
        )

        assert result is True
