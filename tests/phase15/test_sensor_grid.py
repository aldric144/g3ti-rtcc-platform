"""Tests for Sensor Grid Integration Layer"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.sensor_grid.registry import (
    SensorRegistry,
    Sensor,
    SensorType,
    SensorStatus,
    SensorReading,
)
from app.sensor_grid.event_ingestor import (
    SensorEventIngestor,
    SensorEvent,
    EventSeverity,
    EventCategory,
    GunshotEvent,
)
from app.sensor_grid.grid_fusion import (
    GridFusionEngine,
    DataSource,
    FusedEvent,
    CorrelationType,
)
from app.sensor_grid.crowd_forecast import (
    CrowdForecastModel,
    CrowdZone,
    CrowdDensity,
    CrowdPrediction,
)
from app.sensor_grid.health_monitor import (
    SensorHealthMonitor,
    SensorHealthStatus,
    SensorHealth,
)


class TestSensorRegistry:
    """Test suite for SensorRegistry"""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry"""
        return SensorRegistry()

    @pytest.fixture
    def sample_sensor(self):
        """Create a sample sensor"""
        return Sensor(
            sensor_id="sensor-001",
            sensor_type=SensorType.GUNSHOT,
            name="Downtown Gunshot Sensor 1",
            status=SensorStatus.ONLINE,
            latitude=33.749,
            longitude=-84.388,
            coverage_radius_m=500,
        )

    def test_register_sensor(self, registry, sample_sensor):
        """Test sensor registration"""
        result = registry.register_sensor(sample_sensor)
        assert result is True
        assert sample_sensor.sensor_id in registry._sensors

    def test_get_sensors_by_type(self, registry, sample_sensor):
        """Test filtering sensors by type"""
        registry.register_sensor(sample_sensor)
        gunshot_sensors = registry.get_sensors_by_type(SensorType.GUNSHOT)
        assert len(gunshot_sensors) == 1

    def test_get_sensors_by_status(self, registry, sample_sensor):
        """Test filtering sensors by status"""
        registry.register_sensor(sample_sensor)
        online_sensors = registry.get_sensors_by_status(SensorStatus.ONLINE)
        assert len(online_sensors) == 1

    def test_record_reading(self, registry, sample_sensor):
        """Test recording a sensor reading"""
        registry.register_sensor(sample_sensor)
        reading = SensorReading(
            reading_id="reading-001",
            sensor_id=sample_sensor.sensor_id,
            timestamp=datetime.utcnow(),
            value=85.5,
            unit="dB",
            quality=0.95,
        )
        result = registry.record_reading(reading)
        assert result is True


class TestSensorEventIngestor:
    """Test suite for SensorEventIngestor"""

    @pytest.fixture
    def ingestor(self):
        """Create an event ingestor"""
        return SensorEventIngestor()

    @pytest.fixture
    def gunshot_event(self):
        """Create a sample gunshot event"""
        return GunshotEvent(
            event_id="gs-001",
            sensor_id="sensor-001",
            timestamp=datetime.utcnow(),
            latitude=33.749,
            longitude=-84.388,
            confidence=0.95,
            caliber_estimate="9mm",
            shot_count=3,
            direction_deg=45,
            distance_m=150,
        )

    def test_ingest_gunshot_event(self, ingestor, gunshot_event):
        """Test ingesting a gunshot event"""
        result = ingestor.ingest_gunshot_event(gunshot_event)
        assert result is True

    def test_get_events_by_category(self, ingestor, gunshot_event):
        """Test getting events by category"""
        ingestor.ingest_gunshot_event(gunshot_event)
        events = ingestor.get_events_by_category(EventCategory.GUNSHOT)
        assert len(events) >= 1

    def test_acknowledge_event(self, ingestor, gunshot_event):
        """Test acknowledging an event"""
        ingestor.ingest_gunshot_event(gunshot_event)
        result = ingestor.acknowledge_event(gunshot_event.event_id, "op-001")
        assert result is True


class TestGridFusionEngine:
    """Test suite for GridFusionEngine"""

    @pytest.fixture
    def fusion_engine(self):
        """Create a fusion engine"""
        return GridFusionEngine()

    @pytest.fixture
    def sensor_source(self):
        """Create a sample sensor data source"""
        return DataSource(
            source_id="sensor-001",
            source_type="SENSOR",
            timestamp=datetime.utcnow(),
            latitude=33.749,
            longitude=-84.388,
            data={"event_type": "GUNSHOT", "confidence": 0.95},
            confidence=0.95,
        )

    @pytest.fixture
    def lpr_source(self):
        """Create a sample LPR data source"""
        return DataSource(
            source_id="lpr-001",
            source_type="LPR",
            timestamp=datetime.utcnow(),
            latitude=33.750,
            longitude=-84.389,
            data={"plate": "ABC123", "vehicle_type": "sedan"},
            confidence=0.98,
        )

    def test_add_source(self, fusion_engine, sensor_source):
        """Test adding a data source"""
        result = fusion_engine.add_source(sensor_source)
        assert result is True

    def test_correlate_sources(self, fusion_engine, sensor_source, lpr_source):
        """Test correlating multiple sources"""
        fusion_engine.add_source(sensor_source)
        fusion_engine.add_source(lpr_source)
        fused_events = fusion_engine.process_correlations()
        assert isinstance(fused_events, list)

    def test_get_fused_events(self, fusion_engine):
        """Test getting fused events"""
        events = fusion_engine.get_fused_events()
        assert isinstance(events, list)


class TestCrowdForecastModel:
    """Test suite for CrowdForecastModel"""

    @pytest.fixture
    def forecast_model(self):
        """Create a forecast model"""
        return CrowdForecastModel()

    @pytest.fixture
    def crowd_zone(self):
        """Create a sample crowd zone"""
        return CrowdZone(
            zone_id="zone-001",
            name="Downtown Plaza",
            boundary_coords=[
                (33.748, -84.390),
                (33.750, -84.390),
                (33.750, -84.386),
                (33.748, -84.386),
            ],
            center_lat=33.749,
            center_lon=-84.388,
            area_sq_m=10000,
            capacity=5000,
        )

    def test_register_zone(self, forecast_model, crowd_zone):
        """Test registering a crowd zone"""
        result = forecast_model.register_zone(crowd_zone)
        assert result is True

    def test_update_zone_count(self, forecast_model, crowd_zone):
        """Test updating zone crowd count"""
        forecast_model.register_zone(crowd_zone)
        result = forecast_model.update_zone_count(crowd_zone.zone_id, 1500)
        assert result is True
        
        zone = forecast_model.get_zone(crowd_zone.zone_id)
        assert zone.current_count == 1500

    def test_generate_prediction(self, forecast_model, crowd_zone):
        """Test generating a crowd prediction"""
        forecast_model.register_zone(crowd_zone)
        forecast_model.update_zone_count(crowd_zone.zone_id, 1500)
        prediction = forecast_model.generate_prediction(crowd_zone.zone_id, hours_ahead=2)
        assert prediction is not None
        assert prediction.zone_id == crowd_zone.zone_id


class TestSensorHealthMonitor:
    """Test suite for SensorHealthMonitor"""

    @pytest.fixture
    def health_monitor(self):
        """Create a health monitor"""
        return SensorHealthMonitor()

    def test_register_sensor(self, health_monitor):
        """Test registering a sensor for monitoring"""
        result = health_monitor.register_sensor(
            sensor_id="sensor-001",
            sensor_name="Test Sensor",
            sensor_type=SensorType.GUNSHOT,
        )
        assert result is True

    def test_check_sensor_health(self, health_monitor):
        """Test checking sensor health"""
        health_monitor.register_sensor(
            sensor_id="sensor-001",
            sensor_name="Test Sensor",
            sensor_type=SensorType.GUNSHOT,
        )
        health = health_monitor.check_sensor_health("sensor-001")
        assert health is not None
        assert health.sensor_id == "sensor-001"

    def test_record_reading(self, health_monitor):
        """Test recording a reading for health tracking"""
        health_monitor.register_sensor(
            sensor_id="sensor-001",
            sensor_name="Test Sensor",
            sensor_type=SensorType.GUNSHOT,
        )
        result = health_monitor.record_reading("sensor-001")
        assert result is True

    def test_get_unhealthy_sensors(self, health_monitor):
        """Test getting unhealthy sensors"""
        unhealthy = health_monitor.get_unhealthy_sensors()
        assert isinstance(unhealthy, list)
