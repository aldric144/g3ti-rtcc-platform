"""Tests for City Digital Twin Engine"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.digital_twin.building_models import (
    BuildingModelsLoader,
    Building,
    BuildingType,
    RiskLevel,
    Floor,
    Room,
)
from app.digital_twin.road_network import (
    RoadNetworkModel,
    Road,
    RoadType,
    TrafficCondition,
    Intersection,
)
from app.digital_twin.interior_mapping import (
    InteriorMappingService,
    InteriorMap,
    PointOfInterest,
    POIType,
    AccessPoint,
    AccessType,
)
from app.digital_twin.entity_renderer import (
    EntityRenderer,
    EntityType,
    RenderedEntity,
    EntityPosition,
)
from app.digital_twin.overlay_engine import (
    OverlayEngine,
    OverlayType,
    WeatherOverlay,
    TrafficOverlay,
)
from app.digital_twin.time_travel import (
    TimeTravelEngine,
    HistoricalSnapshot,
    PlaybackState,
)


class TestBuildingModelsLoader:
    """Test suite for BuildingModelsLoader"""

    @pytest.fixture
    def loader(self):
        """Create a building models loader"""
        return BuildingModelsLoader()

    @pytest.fixture
    def sample_building(self):
        """Create a sample building"""
        return Building(
            building_id="bldg-001",
            name="City Hall",
            address="55 Trinity Ave SW",
            building_type=BuildingType.GOVERNMENT,
            risk_level=RiskLevel.HIGH,
            latitude=33.749,
            longitude=-84.388,
            height_m=50,
            floor_count=8,
            occupancy_capacity=2000,
        )

    def test_add_building(self, loader, sample_building):
        """Test adding a building"""
        result = loader.add_building(sample_building)
        assert result is True
        assert sample_building.building_id in loader._buildings

    def test_get_building(self, loader, sample_building):
        """Test getting a building by ID"""
        loader.add_building(sample_building)
        building = loader.get_building(sample_building.building_id)
        assert building is not None
        assert building.name == sample_building.name

    def test_search_buildings(self, loader, sample_building):
        """Test searching buildings"""
        loader.add_building(sample_building)
        results = loader.search_buildings(building_type=BuildingType.GOVERNMENT)
        assert len(results) >= 1

    def test_get_buildings_in_area(self, loader, sample_building):
        """Test getting buildings in an area"""
        loader.add_building(sample_building)
        buildings = loader.get_buildings_in_area(
            center_lat=33.749,
            center_lon=-84.388,
            radius_m=1000,
        )
        assert len(buildings) >= 1

    def test_add_floor(self, loader, sample_building):
        """Test adding a floor to a building"""
        loader.add_building(sample_building)
        floor = Floor(
            floor_id="floor-001",
            floor_number=1,
            name="Ground Floor",
            elevation_m=0,
            height_m=4,
            area_sq_m=500,
        )
        result = loader.add_floor(sample_building.building_id, floor)
        assert result is True


class TestRoadNetworkModel:
    """Test suite for RoadNetworkModel"""

    @pytest.fixture
    def road_network(self):
        """Create a road network model"""
        return RoadNetworkModel()

    @pytest.fixture
    def sample_road(self):
        """Create a sample road"""
        return Road(
            road_id="road-001",
            name="Peachtree Street",
            road_type=RoadType.ARTERIAL,
            start_lat=33.745,
            start_lon=-84.390,
            end_lat=33.755,
            end_lon=-84.385,
            length_m=1500,
            lanes=4,
            speed_limit_kmh=55,
        )

    def test_add_road(self, road_network, sample_road):
        """Test adding a road"""
        result = road_network.add_road(sample_road)
        assert result is True

    def test_get_road(self, road_network, sample_road):
        """Test getting a road by ID"""
        road_network.add_road(sample_road)
        road = road_network.get_road(sample_road.road_id)
        assert road is not None
        assert road.name == sample_road.name

    def test_update_traffic(self, road_network, sample_road):
        """Test updating traffic conditions"""
        road_network.add_road(sample_road)
        result = road_network.update_traffic(
            sample_road.road_id,
            TrafficCondition.HEAVY,
            current_speed_kmh=25,
        )
        assert result is True
        
        road = road_network.get_road(sample_road.road_id)
        assert road.traffic_condition == TrafficCondition.HEAVY

    def test_add_intersection(self, road_network):
        """Test adding an intersection"""
        intersection = Intersection(
            intersection_id="int-001",
            name="Peachtree & 10th",
            latitude=33.750,
            longitude=-84.388,
            has_traffic_light=True,
        )
        result = road_network.add_intersection(intersection)
        assert result is True


class TestEntityRenderer:
    """Test suite for EntityRenderer"""

    @pytest.fixture
    def renderer(self):
        """Create an entity renderer"""
        return EntityRenderer()

    @pytest.fixture
    def officer_entity(self):
        """Create a sample officer entity"""
        return RenderedEntity(
            entity_id="officer-001",
            entity_type=EntityType.OFFICER,
            position=EntityPosition(
                latitude=33.749,
                longitude=-84.388,
                altitude_m=0,
                heading_deg=90,
            ),
            label="Unit 12",
            visible=True,
        )

    def test_add_entity(self, renderer, officer_entity):
        """Test adding an entity"""
        result = renderer.add_entity(officer_entity)
        assert result is True

    def test_update_entity_position(self, renderer, officer_entity):
        """Test updating entity position"""
        renderer.add_entity(officer_entity)
        new_position = EntityPosition(
            latitude=33.750,
            longitude=-84.390,
            altitude_m=0,
            heading_deg=180,
        )
        result = renderer.update_entity_position(officer_entity.entity_id, new_position)
        assert result is True

    def test_get_entities_by_type(self, renderer, officer_entity):
        """Test getting entities by type"""
        renderer.add_entity(officer_entity)
        officers = renderer.get_entities_by_type(EntityType.OFFICER)
        assert len(officers) >= 1

    def test_remove_entity(self, renderer, officer_entity):
        """Test removing an entity"""
        renderer.add_entity(officer_entity)
        result = renderer.remove_entity(officer_entity.entity_id)
        assert result is True


class TestOverlayEngine:
    """Test suite for OverlayEngine"""

    @pytest.fixture
    def overlay_engine(self):
        """Create an overlay engine"""
        return OverlayEngine()

    def test_add_weather_overlay(self, overlay_engine):
        """Test adding a weather overlay"""
        weather = WeatherOverlay(
            overlay_id="weather-001",
            overlay_type=OverlayType.WEATHER,
            temperature_f=72,
            conditions="Clear",
            wind_speed_mph=5,
            wind_direction_deg=180,
            humidity_percent=45,
        )
        result = overlay_engine.add_overlay(weather)
        assert result is True

    def test_add_traffic_overlay(self, overlay_engine):
        """Test adding a traffic overlay"""
        traffic = TrafficOverlay(
            overlay_id="traffic-001",
            overlay_type=OverlayType.TRAFFIC,
            congestion_level="MODERATE",
            average_speed_kmh=35,
        )
        result = overlay_engine.add_overlay(traffic)
        assert result is True

    def test_get_active_overlays(self, overlay_engine):
        """Test getting active overlays"""
        overlays = overlay_engine.get_active_overlays()
        assert isinstance(overlays, list)


class TestTimeTravelEngine:
    """Test suite for TimeTravelEngine"""

    @pytest.fixture
    def time_travel(self):
        """Create a time travel engine"""
        return TimeTravelEngine()

    def test_get_snapshot(self, time_travel):
        """Test getting a historical snapshot"""
        snapshot = time_travel.get_snapshot(datetime.utcnow())
        assert snapshot is not None

    def test_start_playback(self, time_travel):
        """Test starting playback"""
        start_time = datetime(2024, 12, 9, 10, 0, 0)
        result = time_travel.start_playback(start_time)
        assert result is True
        assert time_travel.get_playback_state() == PlaybackState.PLAYING

    def test_pause_playback(self, time_travel):
        """Test pausing playback"""
        time_travel.start_playback(datetime.utcnow())
        result = time_travel.pause_playback()
        assert result is True
        assert time_travel.get_playback_state() == PlaybackState.PAUSED

    def test_stop_playback(self, time_travel):
        """Test stopping playback"""
        time_travel.start_playback(datetime.utcnow())
        result = time_travel.stop_playback()
        assert result is True
        assert time_travel.get_playback_state() == PlaybackState.STOPPED

    def test_set_playback_speed(self, time_travel):
        """Test setting playback speed"""
        result = time_travel.set_playback_speed(2.0)
        assert result is True
