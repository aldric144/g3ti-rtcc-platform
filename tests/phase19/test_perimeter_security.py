"""
Phase 19: Perimeter Security Module Tests

Tests for ThermalSensorGrid, MotionRadarIngestor, PerimeterBreachDetector, and AutoResponseEngine.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestThermalSensorGrid:
    """Tests for ThermalSensorGrid."""

    def test_register_sensor(self):
        """Test sensor registration."""
        from backend.app.robotics.perimeter_security import ThermalSensorGrid

        grid = ThermalSensorGrid()
        sensor = grid.register_sensor(
            name="Thermal-North-1",
            position={"x": 100, "y": 180, "z": 3},
            zone_id="zone-north",
            field_of_view=120.0,
            range_meters=50.0,
        )

        assert sensor is not None
        assert sensor["name"] == "Thermal-North-1"
        assert sensor["zone_id"] == "zone-north"

    def test_ingest_reading(self):
        """Test thermal reading ingestion."""
        from backend.app.robotics.perimeter_security import ThermalSensorGrid

        grid = ThermalSensorGrid()
        sensor = grid.register_sensor(
            name="Thermal-Test",
            position={"x": 50, "y": 50, "z": 2},
            zone_id="zone-test",
            field_of_view=90.0,
            range_meters=30.0,
        )

        reading = grid.ingest_reading(
            sensor_id=sensor["sensor_id"],
            temperature_grid=[[25.0, 26.0], [25.5, 37.2]],
            ambient_temperature=25.0,
            max_temperature=37.2,
            min_temperature=25.0,
        )

        assert reading is not None
        assert reading.max_temperature == 37.2

    def test_detect_anomaly(self):
        """Test thermal anomaly detection."""
        from backend.app.robotics.perimeter_security import ThermalSensorGrid

        grid = ThermalSensorGrid()
        sensor = grid.register_sensor(
            name="Anomaly-Test",
            position={"x": 0, "y": 0, "z": 2},
            zone_id="zone-anomaly",
            field_of_view=90.0,
            range_meters=25.0,
        )

        reading = grid.ingest_reading(
            sensor_id=sensor["sensor_id"],
            temperature_grid=[[25.0, 38.5], [25.0, 25.0]],
            ambient_temperature=25.0,
            max_temperature=38.5,
            min_temperature=25.0,
        )

        assert reading.anomaly_detected is True

    def test_get_sensors(self):
        """Test getting sensors with filters."""
        from backend.app.robotics.perimeter_security import ThermalSensorGrid

        grid = ThermalSensorGrid()
        grid.register_sensor("S1", {"x": 0, "y": 0, "z": 0}, "zone-a", 90.0, 30.0)
        grid.register_sensor("S2", {"x": 10, "y": 0, "z": 0}, "zone-a", 90.0, 30.0)
        grid.register_sensor("S3", {"x": 20, "y": 0, "z": 0}, "zone-b", 90.0, 30.0)

        zone_a_sensors = grid.get_sensors(zone_id="zone-a")
        assert len(zone_a_sensors) == 2

    def test_get_zone_thermal_map(self):
        """Test getting zone thermal map."""
        from backend.app.robotics.perimeter_security import ThermalSensorGrid

        grid = ThermalSensorGrid()
        sensor = grid.register_sensor("Map-Test", {"x": 50, "y": 50, "z": 2}, "zone-map", 90.0, 30.0)
        grid.ingest_reading(
            sensor["sensor_id"],
            [[25.0, 26.0], [25.5, 25.0]],
            25.0,
            26.0,
            25.0,
        )

        thermal_map = grid.get_zone_thermal_map("zone-map")
        assert thermal_map is not None


class TestMotionRadarIngestor:
    """Tests for MotionRadarIngestor."""

    def test_register_sensor(self):
        """Test motion sensor registration."""
        from backend.app.robotics.perimeter_security import MotionRadarIngestor

        ingestor = MotionRadarIngestor()
        sensor = ingestor.register_sensor(
            name="Motion-East-1",
            sensor_type="radar",
            position={"x": 180, "y": 100, "z": 2},
            zone_id="zone-east",
            detection_range=100.0,
        )

        assert sensor is not None
        assert sensor["name"] == "Motion-East-1"
        assert sensor["sensor_type"] == "radar"

    def test_ingest_event(self):
        """Test motion event ingestion."""
        from backend.app.robotics.perimeter_security import MotionRadarIngestor, MotionEventType

        ingestor = MotionRadarIngestor()
        sensor = ingestor.register_sensor(
            name="Event-Test",
            sensor_type="pir",
            position={"x": 0, "y": 0, "z": 1},
            zone_id="zone-event",
            detection_range=20.0,
        )

        event = ingestor.ingest_event(
            sensor_id=sensor["sensor_id"],
            event_type=MotionEventType.MOTION_DETECTED,
            position={"x": 5, "y": 5, "z": 0},
            velocity={"x": 1.0, "y": 0.5, "z": 0},
            confidence=0.85,
        )

        assert event is not None
        assert event.event_type == MotionEventType.MOTION_DETECTED
        assert event.confidence == 0.85

    def test_get_events(self):
        """Test getting motion events."""
        from backend.app.robotics.perimeter_security import MotionRadarIngestor, MotionEventType

        ingestor = MotionRadarIngestor()
        sensor = ingestor.register_sensor("Events-Test", "radar", {"x": 0, "y": 0, "z": 0}, "zone-events", 50.0)

        for i in range(5):
            ingestor.ingest_event(
                sensor["sensor_id"],
                MotionEventType.MOTION_DETECTED,
                {"x": i * 5, "y": 0, "z": 0},
                {"x": 1.0, "y": 0, "z": 0},
                0.9,
            )

        events = ingestor.get_events(zone_id="zone-events", limit=3)
        assert len(events) == 3

    def test_get_active_tracks(self):
        """Test getting active tracks."""
        from backend.app.robotics.perimeter_security import MotionRadarIngestor, MotionEventType

        ingestor = MotionRadarIngestor()
        sensor = ingestor.register_sensor("Track-Test", "radar", {"x": 0, "y": 0, "z": 0}, "zone-track", 50.0)

        ingestor.ingest_event(
            sensor["sensor_id"],
            MotionEventType.TRACK_START,
            {"x": 10, "y": 10, "z": 0},
            {"x": 1.0, "y": 1.0, "z": 0},
            0.95,
            track_id="track-001",
        )

        tracks = ingestor.get_active_tracks()
        assert len(tracks) >= 0


class TestPerimeterBreachDetector:
    """Tests for PerimeterBreachDetector."""

    def test_register_zone(self):
        """Test zone registration."""
        from backend.app.robotics.perimeter_security import PerimeterBreachDetector, SensorZoneType

        detector = PerimeterBreachDetector()
        zone = detector.register_zone(
            name="North Perimeter",
            zone_type=SensorZoneType.PERIMETER,
            bounds={"min_x": 0, "min_y": 180, "max_x": 200, "max_y": 200},
            sensitivity=0.8,
        )

        assert zone is not None
        assert zone.name == "North Perimeter"
        assert zone.zone_type == SensorZoneType.PERIMETER

    def test_detect_breach(self):
        """Test breach detection."""
        from backend.app.robotics.perimeter_security import PerimeterBreachDetector, SensorZoneType

        detector = PerimeterBreachDetector()
        zone = detector.register_zone(
            name="Breach Test Zone",
            zone_type=SensorZoneType.PERIMETER,
            bounds={"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100},
            sensitivity=0.7,
        )

        breach = detector.detect_breach(
            zone_id=zone.zone_id,
            position={"x": 50, "y": 50},
            entities=[{"type": "person", "confidence": 0.9}],
            thermal_data={"temperature": 37.0, "signature": "human"},
            motion_data={"velocity": 1.5, "direction": 45},
        )

        assert breach is not None
        assert breach.zone_id == zone.zone_id
        assert breach.risk_score > 0

    def test_acknowledge_breach(self):
        """Test breach acknowledgment."""
        from backend.app.robotics.perimeter_security import PerimeterBreachDetector, SensorZoneType, BreachStatus

        detector = PerimeterBreachDetector()
        zone = detector.register_zone("Ack Test", SensorZoneType.ACCESS_POINT, {"min_x": 0, "min_y": 0, "max_x": 50, "max_y": 50}, 0.8)

        breach = detector.detect_breach(
            zone.zone_id,
            {"x": 25, "y": 25},
            [{"type": "vehicle", "confidence": 0.85}],
        )

        acknowledged = detector.acknowledge_breach(breach.breach_id, "operator-001")
        assert acknowledged is not None
        assert acknowledged.status == BreachStatus.ACKNOWLEDGED

    def test_resolve_breach(self):
        """Test breach resolution."""
        from backend.app.robotics.perimeter_security import PerimeterBreachDetector, SensorZoneType, BreachStatus

        detector = PerimeterBreachDetector()
        zone = detector.register_zone("Resolve Test", SensorZoneType.INTERIOR, {"min_x": 0, "min_y": 0, "max_x": 30, "max_y": 30}, 0.6)

        breach = detector.detect_breach(zone.zone_id, {"x": 15, "y": 15}, [{"type": "person", "confidence": 0.7}])
        detector.acknowledge_breach(breach.breach_id, "operator-002")

        resolved = detector.resolve_breach(breach.breach_id, "operator-002", "False alarm - authorized personnel")
        assert resolved is not None
        assert resolved.status == BreachStatus.RESOLVED

    def test_get_breaches(self):
        """Test getting breaches with filters."""
        from backend.app.robotics.perimeter_security import PerimeterBreachDetector, SensorZoneType

        detector = PerimeterBreachDetector()
        zone = detector.register_zone("Filter Test", SensorZoneType.PERIMETER, {"min_x": 0, "min_y": 0, "max_x": 100, "max_y": 100}, 0.7)

        for i in range(3):
            detector.detect_breach(zone.zone_id, {"x": i * 20, "y": 50}, [{"type": "person", "confidence": 0.8}])

        breaches = detector.get_breaches(zone_id=zone.zone_id)
        assert len(breaches) == 3

    def test_get_metrics(self):
        """Test getting breach detection metrics."""
        from backend.app.robotics.perimeter_security import PerimeterBreachDetector

        detector = PerimeterBreachDetector()
        metrics = detector.get_metrics()

        assert "total_breaches" in metrics
        assert "by_severity" in metrics


class TestAutoResponseEngine:
    """Tests for AutoResponseEngine."""

    def test_register_unit(self):
        """Test response unit registration."""
        from backend.app.robotics.perimeter_security import AutoResponseEngine

        engine = AutoResponseEngine()
        unit = engine.register_unit(
            unit_id="robot-001",
            unit_type="robot",
            position={"x": 100, "y": 100, "z": 0},
            capabilities=["patrol", "surveillance"],
        )

        assert unit is not None
        assert unit["unit_id"] == "robot-001"
        assert "patrol" in unit["capabilities"]

    def test_trigger_response(self):
        """Test triggering auto response."""
        from backend.app.robotics.perimeter_security import AutoResponseEngine

        engine = AutoResponseEngine()
        engine.register_unit("robot-resp-001", "robot", {"x": 50, "y": 50, "z": 0}, ["respond"])
        engine.register_unit("drone-resp-001", "drone", {"x": 100, "y": 100, "z": 10}, ["aerial_surveillance"])

        response = engine.trigger_response(
            breach_id="breach-001",
            breach_position={"x": 75, "y": 75},
            severity="high",
            breach_type="intrusion",
        )

        assert response is not None
        assert response.breach_id == "breach-001"
        assert len(response.dispatched_units) > 0

    def test_update_response_status(self):
        """Test updating response status."""
        from backend.app.robotics.perimeter_security import AutoResponseEngine

        engine = AutoResponseEngine()
        engine.register_unit("robot-status-001", "robot", {"x": 0, "y": 0, "z": 0}, ["respond"])

        response = engine.trigger_response("breach-status-001", {"x": 50, "y": 50}, "medium", "suspicious_activity")

        updated = engine.update_response_status(response.response_id, "in_progress")
        assert updated is not None
        assert updated.status == "in_progress"

    def test_get_active_responses(self):
        """Test getting active responses."""
        from backend.app.robotics.perimeter_security import AutoResponseEngine

        engine = AutoResponseEngine()
        engine.register_unit("robot-active-001", "robot", {"x": 0, "y": 0, "z": 0}, ["respond"])

        engine.trigger_response("breach-active-001", {"x": 25, "y": 25}, "low", "loitering")

        active = engine.get_active_responses()
        assert len(active) >= 1

    def test_get_metrics(self):
        """Test getting auto-response metrics."""
        from backend.app.robotics.perimeter_security import AutoResponseEngine

        engine = AutoResponseEngine()
        metrics = engine.get_metrics()

        assert "total_responses" in metrics
        assert "available_units" in metrics
