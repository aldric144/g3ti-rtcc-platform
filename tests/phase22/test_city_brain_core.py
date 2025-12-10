"""
Tests for City Brain Core module.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestCityBrainCore:
    """Tests for CityBrainCore class."""

    def test_city_brain_initialization(self):
        """Test CityBrainCore initializes correctly."""
        from backend.app.city_brain import CityBrainCore
        
        brain = CityBrainCore()
        assert brain is not None
        assert brain._running is False

    def test_city_profile_loader(self):
        """Test CityProfileLoader loads Riviera Beach profile."""
        from backend.app.city_brain import CityProfileLoader
        
        loader = CityProfileLoader()
        profile = loader.get_profile()
        
        assert profile is not None
        assert profile.get("city_name") == "Riviera Beach"
        assert profile.get("state") == "Florida"
        assert profile.get("zip_code") == "33404"

    def test_city_profile_districts(self):
        """Test CityProfileLoader returns districts."""
        from backend.app.city_brain import CityProfileLoader
        
        loader = CityProfileLoader()
        districts = loader.get_districts()
        
        assert districts is not None
        assert len(districts) > 0
        assert any(d.get("name") == "Downtown/Marina" for d in districts)

    def test_city_profile_infrastructure(self):
        """Test CityProfileLoader returns critical infrastructure."""
        from backend.app.city_brain import CityProfileLoader
        
        loader = CityProfileLoader()
        infrastructure = loader.get_critical_infrastructure()
        
        assert infrastructure is not None
        assert len(infrastructure) > 0

    def test_city_profile_flood_zones(self):
        """Test CityProfileLoader returns flood zones."""
        from backend.app.city_brain import CityProfileLoader
        
        loader = CityProfileLoader()
        flood_zones = loader.get_flood_zones()
        
        assert flood_zones is not None
        assert len(flood_zones) > 0

    def test_city_profile_hurricane_zones(self):
        """Test CityProfileLoader returns hurricane evacuation zones."""
        from backend.app.city_brain import CityProfileLoader
        
        loader = CityProfileLoader()
        hurricane_zones = loader.get_hurricane_zones()
        
        assert hurricane_zones is not None
        assert len(hurricane_zones) > 0

    def test_event_bus_publish_subscribe(self):
        """Test EventBus publish/subscribe functionality."""
        from backend.app.city_brain import EventBus, CityEvent, CityEventType, EventPriority
        
        bus = EventBus()
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        bus.subscribe(CityEventType.WEATHER_UPDATE, handler)
        
        event = CityEvent(
            event_id="test-1",
            event_type=CityEventType.WEATHER_UPDATE,
            timestamp=datetime.utcnow(),
            data={"temperature": 85},
            priority=EventPriority.NORMAL,
        )
        
        bus.publish(event)
        
        assert len(received_events) == 1
        assert received_events[0].event_id == "test-1"

    def test_city_state_snapshot(self):
        """Test CityState snapshot creation."""
        from backend.app.city_brain import CityState
        
        state = CityState(
            timestamp=datetime.utcnow(),
            weather={},
            traffic={},
            utilities={},
            incidents={},
            predictions={},
            population_estimate=37964,
            active_events=[],
            module_statuses={},
            overall_health=0.95,
        )
        
        assert state is not None
        assert state.population_estimate == 37964
        assert state.overall_health == 0.95

    def test_module_status(self):
        """Test ModuleStatus dataclass."""
        from backend.app.city_brain import ModuleStatus, CityModuleType
        
        status = ModuleStatus(
            module_type=CityModuleType.WEATHER,
            status="running",
            health=0.98,
            last_update=datetime.utcnow(),
            error_count=0,
            message="Operational",
        )
        
        assert status.module_type == CityModuleType.WEATHER
        assert status.status == "running"
        assert status.health == 0.98


class TestCityBrainModuleTypes:
    """Tests for City Brain module type enums."""

    def test_city_module_types(self):
        """Test CityModuleType enum values."""
        from backend.app.city_brain import CityModuleType
        
        assert CityModuleType.WEATHER.value == "weather"
        assert CityModuleType.TRAFFIC.value == "traffic"
        assert CityModuleType.UTILITIES.value == "utilities"
        assert CityModuleType.INCIDENTS.value == "incidents"
        assert CityModuleType.DIGITAL_TWIN.value == "digital_twin"
        assert CityModuleType.PREDICTIONS.value == "predictions"

    def test_city_event_types(self):
        """Test CityEventType enum values."""
        from backend.app.city_brain import CityEventType
        
        assert CityEventType.WEATHER_UPDATE.value == "weather_update"
        assert CityEventType.TRAFFIC_UPDATE.value == "traffic_update"
        assert CityEventType.UTILITY_UPDATE.value == "utility_update"
        assert CityEventType.INCIDENT_UPDATE.value == "incident_update"

    def test_event_priority(self):
        """Test EventPriority enum values."""
        from backend.app.city_brain import EventPriority
        
        assert EventPriority.LOW.value == 0
        assert EventPriority.NORMAL.value == 1
        assert EventPriority.HIGH.value == 2
        assert EventPriority.CRITICAL.value == 3
