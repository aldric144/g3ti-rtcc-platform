"""
Phase 21: Crisis Detection Engine Tests

Tests for storm tracking, flood prediction, fire modeling,
earthquake monitoring, and explosion detection.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.emergency.crisis_detection_engine import (
    StormTracker,
    FloodPredictor,
    FireSpreadModel,
    EarthquakeMonitor,
    ExplosionDetector,
    CrisisAlertManager,
    CrisisDetectionEngine,
    CrisisType,
    CrisisSeverity,
    AlertLevel,
)


class TestStormTracker:
    """Tests for StormTracker class."""

    def test_storm_tracker_initialization(self):
        """Test StormTracker initializes correctly."""
        tracker = StormTracker()
        assert tracker is not None
        assert hasattr(tracker, '_active_storms')

    def test_track_storm(self):
        """Test tracking a new storm."""
        tracker = StormTracker()
        storm = tracker.track_storm(
            name="Hurricane Alpha",
            category="4",
            wind_speed_mph=145,
            current_position={"lat": 25.0, "lng": -80.0},
            predicted_path=[
                {"lat": 25.5, "lng": -79.5},
                {"lat": 26.0, "lng": -79.0},
            ],
        )
        
        assert storm is not None
        assert storm.name == "Hurricane Alpha"
        assert storm.category == "4"
        assert storm.wind_speed_mph == 145

    def test_get_active_storms(self):
        """Test getting active storms."""
        tracker = StormTracker()
        tracker.track_storm(
            name="Storm A",
            category="2",
            wind_speed_mph=100,
            current_position={"lat": 25.0, "lng": -80.0},
        )
        
        storms = tracker.get_active_storms()
        assert len(storms) >= 1

    def test_predict_landfall(self):
        """Test landfall prediction."""
        tracker = StormTracker()
        storm = tracker.track_storm(
            name="Hurricane Beta",
            category="3",
            wind_speed_mph=120,
            current_position={"lat": 24.0, "lng": -82.0},
            predicted_path=[
                {"lat": 25.0, "lng": -81.0},
                {"lat": 26.0, "lng": -80.0},
            ],
        )
        
        landfall = tracker.predict_landfall(storm.storm_id)
        assert landfall is not None


class TestFloodPredictor:
    """Tests for FloodPredictor class."""

    def test_flood_predictor_initialization(self):
        """Test FloodPredictor initializes correctly."""
        predictor = FloodPredictor()
        assert predictor is not None

    def test_predict_flood_risk(self):
        """Test flood risk prediction."""
        predictor = FloodPredictor()
        prediction = predictor.predict_flood_risk(
            location={"lat": 29.7604, "lng": -95.3698},
            rainfall_inches=10.0,
            duration_hours=6,
        )
        
        assert prediction is not None
        assert hasattr(prediction, 'risk_level')
        assert hasattr(prediction, 'flood_depth_feet')

    def test_get_flood_zones(self):
        """Test getting flood zones."""
        predictor = FloodPredictor()
        zones = predictor.get_flood_zones(
            center={"lat": 29.7604, "lng": -95.3698},
            radius_miles=10,
        )
        
        assert isinstance(zones, list)


class TestFireSpreadModel:
    """Tests for FireSpreadModel class."""

    def test_fire_spread_model_initialization(self):
        """Test FireSpreadModel initializes correctly."""
        model = FireSpreadModel()
        assert model is not None

    def test_model_fire_spread(self):
        """Test fire spread modeling."""
        model = FireSpreadModel()
        spread = model.model_spread(
            origin={"lat": 34.0522, "lng": -118.2437},
            area_acres=100,
            wind_speed_mph=20,
            wind_direction=45,
            fuel_type="brush",
            humidity_percent=15,
        )
        
        assert spread is not None
        assert hasattr(spread, 'predicted_spread_rate')
        assert hasattr(spread, 'containment_probability')

    def test_calculate_containment_time(self):
        """Test containment time calculation."""
        model = FireSpreadModel()
        fire = model.model_spread(
            origin={"lat": 34.0522, "lng": -118.2437},
            area_acres=50,
            wind_speed_mph=10,
            wind_direction=90,
            fuel_type="grass",
            humidity_percent=30,
        )
        
        time = model.calculate_containment_time(fire.fire_id)
        assert time is not None


class TestEarthquakeMonitor:
    """Tests for EarthquakeMonitor class."""

    def test_earthquake_monitor_initialization(self):
        """Test EarthquakeMonitor initializes correctly."""
        monitor = EarthquakeMonitor()
        assert monitor is not None

    def test_detect_earthquake(self):
        """Test earthquake detection."""
        monitor = EarthquakeMonitor()
        event = monitor.detect_earthquake(
            epicenter={"lat": 37.7749, "lng": -122.4194},
            magnitude=5.5,
            depth_km=10,
        )
        
        assert event is not None
        assert event.magnitude == 5.5
        assert hasattr(event, 'intensity_scale')

    def test_calculate_impact_zone(self):
        """Test impact zone calculation."""
        monitor = EarthquakeMonitor()
        event = monitor.detect_earthquake(
            epicenter={"lat": 37.7749, "lng": -122.4194},
            magnitude=6.0,
            depth_km=15,
        )
        
        zone = monitor.calculate_impact_zone(event.event_id)
        assert zone is not None
        assert hasattr(zone, 'radius_km')


class TestExplosionDetector:
    """Tests for ExplosionDetector class."""

    def test_explosion_detector_initialization(self):
        """Test ExplosionDetector initializes correctly."""
        detector = ExplosionDetector()
        assert detector is not None

    def test_detect_explosion(self):
        """Test explosion detection."""
        detector = ExplosionDetector()
        event = detector.detect_explosion(
            location={"lat": 40.7128, "lng": -74.0060},
            blast_radius_meters=100,
            estimated_yield="medium",
        )
        
        assert event is not None
        assert hasattr(event, 'explosion_type')
        assert hasattr(event, 'casualties_estimate')

    def test_assess_structural_damage(self):
        """Test structural damage assessment."""
        detector = ExplosionDetector()
        event = detector.detect_explosion(
            location={"lat": 40.7128, "lng": -74.0060},
            blast_radius_meters=50,
            estimated_yield="small",
        )
        
        damage = detector.assess_structural_damage(event.event_id)
        assert damage is not None


class TestCrisisAlertManager:
    """Tests for CrisisAlertManager class."""

    def test_alert_manager_initialization(self):
        """Test CrisisAlertManager initializes correctly."""
        manager = CrisisAlertManager()
        assert manager is not None
        assert hasattr(manager, '_alerts')

    def test_create_alert(self):
        """Test creating a crisis alert."""
        manager = CrisisAlertManager()
        alert = manager.create_alert(
            crisis_type=CrisisType.STORM,
            severity=CrisisSeverity.CRITICAL,
            title="Hurricane Warning",
            description="Category 4 hurricane approaching",
            location={"lat": 25.7617, "lng": -80.1918},
            affected_area_km2=500,
            population_at_risk=150000,
        )
        
        assert alert is not None
        assert alert.title == "Hurricane Warning"
        assert alert.severity == CrisisSeverity.CRITICAL

    def test_get_active_alerts(self):
        """Test getting active alerts."""
        manager = CrisisAlertManager()
        manager.create_alert(
            crisis_type=CrisisType.FLOOD,
            severity=CrisisSeverity.SEVERE,
            title="Flash Flood Warning",
            description="Flash flooding expected",
            location={"lat": 29.7604, "lng": -95.3698},
            affected_area_km2=100,
            population_at_risk=50000,
        )
        
        alerts = manager.get_active_alerts()
        assert len(alerts) >= 1

    def test_get_critical_alerts(self):
        """Test getting critical alerts only."""
        manager = CrisisAlertManager()
        manager.create_alert(
            crisis_type=CrisisType.EARTHQUAKE,
            severity=CrisisSeverity.CRITICAL,
            title="Major Earthquake",
            description="7.0 magnitude earthquake",
            location={"lat": 37.7749, "lng": -122.4194},
            affected_area_km2=1000,
            population_at_risk=500000,
        )
        
        critical = manager.get_critical_alerts()
        assert all(a.severity == CrisisSeverity.CRITICAL for a in critical)

    def test_update_alert_status(self):
        """Test updating alert status."""
        manager = CrisisAlertManager()
        alert = manager.create_alert(
            crisis_type=CrisisType.FIRE,
            severity=CrisisSeverity.MODERATE,
            title="Wildfire Alert",
            description="Wildfire spreading",
            location={"lat": 34.0522, "lng": -118.2437},
            affected_area_km2=200,
            population_at_risk=25000,
        )
        
        updated = manager.update_alert_status(alert.alert_id, "resolved")
        assert updated is not None


class TestCrisisDetectionEngine:
    """Tests for CrisisDetectionEngine class."""

    def test_engine_initialization(self):
        """Test CrisisDetectionEngine initializes correctly."""
        engine = CrisisDetectionEngine()
        assert engine is not None
        assert hasattr(engine, 'storm_tracker')
        assert hasattr(engine, 'flood_predictor')
        assert hasattr(engine, 'fire_model')
        assert hasattr(engine, 'earthquake_monitor')
        assert hasattr(engine, 'explosion_detector')
        assert hasattr(engine, 'alert_manager')

    def test_process_crisis_event(self):
        """Test processing a crisis event."""
        engine = CrisisDetectionEngine()
        result = engine.process_crisis_event(
            crisis_type="storm",
            data={
                "name": "Tropical Storm",
                "category": "1",
                "wind_speed_mph": 75,
                "current_position": {"lat": 25.0, "lng": -80.0},
            },
        )
        
        assert result is not None

    def test_get_all_active_crises(self):
        """Test getting all active crises."""
        engine = CrisisDetectionEngine()
        crises = engine.get_all_active_crises()
        assert isinstance(crises, dict)
        assert "storms" in crises
        assert "floods" in crises
        assert "fires" in crises
        assert "earthquakes" in crises
        assert "explosions" in crises
