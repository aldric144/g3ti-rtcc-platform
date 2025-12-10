"""
Tests for City Brain API endpoints.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock


class TestCityBrainAPIEndpoints:
    """Tests for City Brain API endpoints."""

    def test_router_import(self):
        """Test that the router can be imported."""
        from backend.app.api.city_brain.router import router
        assert router is not None

    def test_event_type_enum(self):
        """Test EventType enum values."""
        from backend.app.api.city_brain.router import EventType
        
        assert EventType.FESTIVAL.value == "festival"
        assert EventType.PARADE.value == "parade"
        assert EventType.SCHOOL_DISMISSAL.value == "school_dismissal"
        assert EventType.UTILITY_MAINTENANCE.value == "utility_maintenance"
        assert EventType.VIP_VISIT.value == "vip_visit"
        assert EventType.POLICE_OPERATION.value == "police_operation"

    def test_event_priority_enum(self):
        """Test EventPriority enum values."""
        from backend.app.api.city_brain.router import EventPriority
        
        assert EventPriority.LOW.value == "low"
        assert EventPriority.MEDIUM.value == "medium"
        assert EventPriority.HIGH.value == "high"
        assert EventPriority.CRITICAL.value == "critical"

    def test_timeline_mode_enum(self):
        """Test TimelineMode enum values."""
        from backend.app.api.city_brain.router import TimelineMode
        
        assert TimelineMode.LIVE.value == "live"
        assert TimelineMode.HISTORICAL.value == "historical"
        assert TimelineMode.SIMULATION.value == "simulation"


class TestCityEventInput:
    """Tests for CityEventInput Pydantic model."""

    def test_city_event_input_valid(self):
        """Test valid CityEventInput creation."""
        from backend.app.api.city_brain.router import CityEventInput, EventType, EventPriority
        
        event = CityEventInput(
            event_type=EventType.FESTIVAL,
            title="Summer Festival",
            description="Annual summer festival at the marina",
            start_time=datetime.utcnow(),
            end_time=None,
            expected_attendance=5000,
            location_lat=26.7753,
            location_lng=-80.0583,
            affected_zones=["downtown", "marina"],
            priority=EventPriority.MEDIUM,
            notify_patrol=True,
            update_predictions=True,
        )
        
        assert event.title == "Summer Festival"
        assert event.expected_attendance == 5000

    def test_city_event_input_minimal(self):
        """Test minimal CityEventInput creation."""
        from backend.app.api.city_brain.router import CityEventInput, EventType, EventPriority
        
        event = CityEventInput(
            event_type=EventType.COMMUNITY_EVENT,
            title="Community Meeting",
            description="Monthly community meeting",
            start_time=datetime.utcnow(),
            priority=EventPriority.LOW,
        )
        
        assert event.title == "Community Meeting"
        assert event.expected_attendance is None


class TestRoadClosureInput:
    """Tests for RoadClosureInput Pydantic model."""

    def test_road_closure_input_valid(self):
        """Test valid RoadClosureInput creation."""
        from backend.app.api.city_brain.router import RoadClosureInput
        
        closure = RoadClosureInput(
            road_name="Blue Heron Blvd",
            segment_start={"latitude": 26.7753, "longitude": -80.0583},
            segment_end={"latitude": 26.7800, "longitude": -80.0550},
            reason="Road construction",
            start_time=datetime.utcnow(),
            end_time=None,
            detour_available=True,
            detour_route="Use Military Trail",
            notify_traffic=True,
        )
        
        assert closure.road_name == "Blue Heron Blvd"
        assert closure.detour_available is True


class TestEmergencyDeclarationInput:
    """Tests for EmergencyDeclarationInput Pydantic model."""

    def test_emergency_declaration_input_valid(self):
        """Test valid EmergencyDeclarationInput creation."""
        from backend.app.api.city_brain.router import EmergencyDeclarationInput
        
        declaration = EmergencyDeclarationInput(
            emergency_type="Hurricane",
            severity="severe",
            affected_areas=["Singer Island", "Marina District"],
            description="Category 3 hurricane approaching",
            evacuation_required=True,
            evacuation_zones=["A", "B"],
            shelter_activation=True,
            effective_time=datetime.utcnow(),
            expected_duration_hours=48,
        )
        
        assert declaration.emergency_type == "Hurricane"
        assert declaration.evacuation_required is True
        assert len(declaration.evacuation_zones) == 2


class TestSimulationRequest:
    """Tests for SimulationRequest Pydantic model."""

    def test_simulation_request_live(self):
        """Test SimulationRequest for live mode."""
        from backend.app.api.city_brain.router import SimulationRequest, TimelineMode
        
        request = SimulationRequest(
            mode=TimelineMode.LIVE,
        )
        
        assert request.mode == TimelineMode.LIVE

    def test_simulation_request_historical(self):
        """Test SimulationRequest for historical mode."""
        from backend.app.api.city_brain.router import SimulationRequest, TimelineMode
        
        request = SimulationRequest(
            mode=TimelineMode.HISTORICAL,
            target_time=datetime(2024, 6, 1, 12, 0, 0),
            playback_speed=2.0,
        )
        
        assert request.mode == TimelineMode.HISTORICAL
        assert request.playback_speed == 2.0

    def test_simulation_request_simulation(self):
        """Test SimulationRequest for simulation mode."""
        from backend.app.api.city_brain.router import SimulationRequest, TimelineMode
        
        request = SimulationRequest(
            mode=TimelineMode.SIMULATION,
            hours_ahead=24,
        )
        
        assert request.mode == TimelineMode.SIMULATION
        assert request.hours_ahead == 24


class TestAPIHelperFunctions:
    """Tests for API helper functions."""

    def test_get_city_brain(self):
        """Test get_city_brain helper function."""
        from backend.app.api.city_brain.router import get_city_brain
        
        brain = get_city_brain()
        assert brain is not None

    def test_get_ingestion_manager(self):
        """Test get_ingestion_manager helper function."""
        from backend.app.api.city_brain.router import get_ingestion_manager
        
        manager = get_ingestion_manager()
        assert manager is not None

    def test_get_digital_twin(self):
        """Test get_digital_twin helper function."""
        from backend.app.api.city_brain.router import get_digital_twin
        
        twin = get_digital_twin()
        assert twin is not None

    def test_get_prediction_engine(self):
        """Test get_prediction_engine helper function."""
        from backend.app.api.city_brain.router import get_prediction_engine
        
        engine = get_prediction_engine()
        assert engine is not None


class TestCityBrainRouterEndpoints:
    """Tests for City Brain router endpoint definitions."""

    def test_router_has_city_state_endpoint(self):
        """Test router has city state endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/city/state" in routes

    def test_router_has_weather_endpoint(self):
        """Test router has weather endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/city/weather" in routes

    def test_router_has_traffic_endpoint(self):
        """Test router has traffic endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/city/traffic" in routes

    def test_router_has_utility_endpoint(self):
        """Test router has utility endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/city/utility" in routes

    def test_router_has_predictions_endpoint(self):
        """Test router has predictions endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/city/predictions" in routes

    def test_router_has_digital_twin_endpoint(self):
        """Test router has digital twin endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/city/digital-twin" in routes

    def test_router_has_admin_events_endpoint(self):
        """Test router has admin events endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/admin/events" in routes

    def test_router_has_admin_road_closures_endpoint(self):
        """Test router has admin road closures endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/admin/road-closures" in routes

    def test_router_has_admin_emergency_endpoint(self):
        """Test router has admin emergency declaration endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/admin/emergency-declaration" in routes

    def test_router_has_health_endpoint(self):
        """Test router has health endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/health" in routes

    def test_router_has_profile_endpoint(self):
        """Test router has profile endpoint."""
        from backend.app.api.city_brain.router import router
        
        routes = [route.path for route in router.routes]
        assert "/profile" in routes
