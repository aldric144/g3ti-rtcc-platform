"""
Tests for Digital Twin module.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestDigitalTwinManager:
    """Tests for DigitalTwinManager class."""

    def test_digital_twin_manager_initialization(self):
        """Test DigitalTwinManager initializes correctly."""
        from backend.app.city_brain.digital_twin import DigitalTwinManager
        
        manager = DigitalTwinManager()
        assert manager is not None

    def test_digital_twin_initialize(self):
        """Test DigitalTwinManager initialize method."""
        from backend.app.city_brain.digital_twin import DigitalTwinManager
        
        manager = DigitalTwinManager()
        manager.initialize()
        
        assert manager._initialized is True

    def test_create_snapshot(self):
        """Test creating a digital twin snapshot."""
        from backend.app.city_brain.digital_twin import DigitalTwinManager
        
        manager = DigitalTwinManager()
        manager.initialize()
        snapshot = manager.create_snapshot()
        
        assert snapshot is not None
        assert snapshot.timestamp is not None

    def test_get_render_data(self):
        """Test getting render data for frontend."""
        from backend.app.city_brain.digital_twin import DigitalTwinManager
        
        manager = DigitalTwinManager()
        manager.initialize()
        render_data = manager.get_render_data()
        
        assert render_data is not None
        assert "timestamp" in render_data
        assert "mode" in render_data


class TestDigitalTwinState:
    """Tests for DigitalTwinState class."""

    def test_digital_twin_state_initialization(self):
        """Test DigitalTwinState initializes correctly."""
        from backend.app.city_brain.digital_twin import DigitalTwinState
        
        state = DigitalTwinState()
        assert state is not None

    def test_update_traffic(self):
        """Test updating traffic data."""
        from backend.app.city_brain.digital_twin import DigitalTwinState, TrafficSegment, CongestionLevel
        
        state = DigitalTwinState()
        
        segment = TrafficSegment(
            segment_id="seg-001",
            road_name="Blue Heron Blvd",
            start_lat=26.7753,
            start_lng=-80.0583,
            end_lat=26.7800,
            end_lng=-80.0550,
            congestion=CongestionLevel.MODERATE,
            current_speed_mph=35.0,
            free_flow_speed_mph=45.0,
        )
        
        state.update_traffic([segment])
        
        assert len(state._traffic_segments) == 1

    def test_update_environmental(self):
        """Test updating environmental conditions."""
        from backend.app.city_brain.digital_twin import DigitalTwinState, EnvironmentalCondition
        
        state = DigitalTwinState()
        
        condition = EnvironmentalCondition(
            condition_id="env-001",
            condition_type="temperature",
            value=85.0,
            unit="fahrenheit",
            latitude=26.7753,
            longitude=-80.0583,
            timestamp=datetime.utcnow(),
        )
        
        state.update_environmental([condition])
        
        assert len(state._environmental_conditions) == 1


class TestDynamicObjectRenderer:
    """Tests for DynamicObjectRenderer class."""

    def test_renderer_initialization(self):
        """Test DynamicObjectRenderer initializes correctly."""
        from backend.app.city_brain.digital_twin import DynamicObjectRenderer
        
        renderer = DynamicObjectRenderer()
        assert renderer is not None

    def test_register_object(self):
        """Test registering a dynamic object."""
        from backend.app.city_brain.digital_twin import (
            DynamicObjectRenderer, DynamicObject, ObjectType, ObjectStatus, Location
        )
        
        renderer = DynamicObjectRenderer()
        
        obj = DynamicObject(
            object_id="unit-001",
            object_type=ObjectType.POLICE_UNIT,
            name="Unit 101",
            status=ObjectStatus.AVAILABLE,
            location=Location(latitude=26.7753, longitude=-80.0583),
            heading=90.0,
            speed_mph=0.0,
            last_update=datetime.utcnow(),
        )
        
        renderer.register_object(obj)
        
        assert "unit-001" in renderer._objects

    def test_update_object_location(self):
        """Test updating object location."""
        from backend.app.city_brain.digital_twin import (
            DynamicObjectRenderer, DynamicObject, ObjectType, ObjectStatus, Location
        )
        
        renderer = DynamicObjectRenderer()
        
        obj = DynamicObject(
            object_id="unit-001",
            object_type=ObjectType.POLICE_UNIT,
            name="Unit 101",
            status=ObjectStatus.AVAILABLE,
            location=Location(latitude=26.7753, longitude=-80.0583),
            heading=90.0,
            speed_mph=0.0,
            last_update=datetime.utcnow(),
        )
        
        renderer.register_object(obj)
        
        new_location = Location(latitude=26.7800, longitude=-80.0550)
        renderer.update_object("unit-001", location=new_location)
        
        updated_obj = renderer._objects["unit-001"]
        assert updated_obj.location.latitude == 26.7800

    def test_get_objects_by_type(self):
        """Test getting objects by type."""
        from backend.app.city_brain.digital_twin import (
            DynamicObjectRenderer, DynamicObject, ObjectType, ObjectStatus, Location
        )
        
        renderer = DynamicObjectRenderer()
        
        police_unit = DynamicObject(
            object_id="police-001",
            object_type=ObjectType.POLICE_UNIT,
            name="Unit 101",
            status=ObjectStatus.AVAILABLE,
            location=Location(latitude=26.7753, longitude=-80.0583),
            heading=90.0,
            speed_mph=0.0,
            last_update=datetime.utcnow(),
        )
        
        fire_unit = DynamicObject(
            object_id="fire-001",
            object_type=ObjectType.FIRE_UNIT,
            name="Engine 1",
            status=ObjectStatus.AVAILABLE,
            location=Location(latitude=26.7800, longitude=-80.0550),
            heading=180.0,
            speed_mph=0.0,
            last_update=datetime.utcnow(),
        )
        
        renderer.register_object(police_unit)
        renderer.register_object(fire_unit)
        
        police_units = renderer.get_objects_by_type(ObjectType.POLICE_UNIT)
        
        assert len(police_units) == 1
        assert police_units[0].object_id == "police-001"


class TestEventOverlayEngine:
    """Tests for EventOverlayEngine class."""

    def test_overlay_engine_initialization(self):
        """Test EventOverlayEngine initializes correctly."""
        from backend.app.city_brain.digital_twin import EventOverlayEngine
        
        engine = EventOverlayEngine()
        assert engine is not None

    def test_add_overlay(self):
        """Test adding an overlay."""
        from backend.app.city_brain.digital_twin import EventOverlayEngine, EventOverlay, OverlayType
        
        engine = EventOverlayEngine()
        
        overlay = EventOverlay(
            overlay_id="overlay-001",
            overlay_type=OverlayType.POWER_OUTAGE,
            title="Power Outage - Singer Island",
            description="500 customers affected",
            severity="medium",
            geometry={"type": "polygon", "coordinates": []},
            start_time=datetime.utcnow(),
            end_time=None,
            metadata={},
        )
        
        engine.add_overlay(overlay)
        
        assert "overlay-001" in engine._overlays

    def test_create_power_outage_overlay(self):
        """Test creating a power outage overlay."""
        from backend.app.city_brain.digital_twin import EventOverlayEngine
        
        engine = EventOverlayEngine()
        
        overlay = engine.create_power_outage_overlay(
            outage_id="out-001",
            area_name="Singer Island",
            customers_affected=500,
            center_lat=26.7850,
            center_lng=-80.0350,
        )
        
        assert overlay is not None
        assert "Singer Island" in overlay.title


class TestTimeWarpEngine:
    """Tests for TimeWarpEngine class."""

    def test_timewarp_engine_initialization(self):
        """Test TimeWarpEngine initializes correctly."""
        from backend.app.city_brain.digital_twin import TimeWarpEngine
        
        engine = TimeWarpEngine()
        assert engine is not None

    def test_set_mode_live(self):
        """Test setting live mode."""
        from backend.app.city_brain.digital_twin import TimeWarpEngine, TimelineMode
        
        engine = TimeWarpEngine()
        engine.set_mode(TimelineMode.LIVE)
        
        assert engine._mode == TimelineMode.LIVE

    def test_set_mode_historical(self):
        """Test setting historical mode."""
        from backend.app.city_brain.digital_twin import TimeWarpEngine, TimelineMode
        
        engine = TimeWarpEngine()
        engine.set_mode(TimelineMode.HISTORICAL)
        
        assert engine._mode == TimelineMode.HISTORICAL

    def test_simulate_future(self):
        """Test simulating future state."""
        from backend.app.city_brain.digital_twin import TimeWarpEngine
        
        engine = TimeWarpEngine()
        future_state = engine.simulate_future(hours_ahead=24)
        
        assert future_state is not None


class TestDigitalTwinEnums:
    """Tests for Digital Twin enums."""

    def test_object_type_enum(self):
        """Test ObjectType enum values."""
        from backend.app.city_brain.digital_twin import ObjectType
        
        assert ObjectType.POLICE_UNIT.value == "police_unit"
        assert ObjectType.FIRE_UNIT.value == "fire_unit"
        assert ObjectType.EMS_UNIT.value == "ems_unit"
        assert ObjectType.DRONE.value == "drone"

    def test_object_status_enum(self):
        """Test ObjectStatus enum values."""
        from backend.app.city_brain.digital_twin import ObjectStatus
        
        assert ObjectStatus.AVAILABLE.value == "available"
        assert ObjectStatus.BUSY.value == "busy"
        assert ObjectStatus.EN_ROUTE.value == "en_route"

    def test_overlay_type_enum(self):
        """Test OverlayType enum values."""
        from backend.app.city_brain.digital_twin import OverlayType
        
        assert OverlayType.POWER_OUTAGE.value == "power_outage"
        assert OverlayType.FLOOD_ZONE.value == "flood_zone"
        assert OverlayType.ROAD_CLOSURE.value == "road_closure"

    def test_congestion_level_enum(self):
        """Test CongestionLevel enum values."""
        from backend.app.city_brain.digital_twin import CongestionLevel
        
        assert CongestionLevel.FREE_FLOW.value == "free_flow"
        assert CongestionLevel.LIGHT.value == "light"
        assert CongestionLevel.MODERATE.value == "moderate"
        assert CongestionLevel.HEAVY.value == "heavy"
        assert CongestionLevel.GRIDLOCK.value == "gridlock"

    def test_timeline_mode_enum(self):
        """Test TimelineMode enum values."""
        from backend.app.city_brain.digital_twin import TimelineMode
        
        assert TimelineMode.LIVE.value == "live"
        assert TimelineMode.HISTORICAL.value == "historical"
        assert TimelineMode.SIMULATION.value == "simulation"
