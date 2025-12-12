"""
Test Suite 10: Maritime Analysis Tests

Tests for maritime data analysis functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestMaritimeSignalCreation:
    """Tests for maritime signal creation."""

    def test_cargo_vessel_signal_creation(self):
        """Test creating signal for cargo vessel."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="123456789",
            vessel_name="Cargo Ship One",
            vessel_type="cargo",
            lat=12.0,
            lon=114.0,
            speed_knots=15.0,
            course=180.0,
            destination="Singapore",
            flag_country="Panama",
            last_port="Hong Kong",
        )

        assert signal is not None
        assert signal.signal_id.startswith("MAR-")

    def test_tanker_vessel_signal_creation(self):
        """Test creating signal for tanker vessel."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="987654321",
            vessel_name="Oil Tanker Alpha",
            vessel_type="tanker",
            lat=26.5,
            lon=51.0,
            speed_knots=12.0,
            course=270.0,
            destination="Rotterdam",
            flag_country="Liberia",
            last_port="Ras Tanura",
        )

        assert signal is not None

    def test_fishing_vessel_signal_creation(self):
        """Test creating signal for fishing vessel."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="111222333",
            vessel_name="Fishing Boat",
            vessel_type="fishing",
            lat=-5.0,
            lon=120.0,
            speed_knots=5.0,
            course=90.0,
            destination="Unknown",
            flag_country="Indonesia",
            last_port="Jakarta",
        )

        assert signal is not None


class TestMaritimeAnomalyTypes:
    """Tests for maritime anomaly type detection."""

    def test_dark_voyage_detection(self):
        """Test detection of dark voyage (AIS gap)."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="999888777",
            vessel_name="Suspicious Vessel",
            vessel_type="tanker",
            lat=26.5,
            lon=51.0,
            speed_knots=0.0,
            course=0.0,
            destination="Unknown",
            flag_country="Unknown",
            last_port="Unknown",
            ais_gap_hours=48,
        )

        assert signal is not None
        assert signal.anomaly_score > 0
        assert signal.anomaly_type == "dark_voyage"

    def test_ais_spoofing_detection(self):
        """Test detection of AIS spoofing."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="666555444",
            vessel_name="Spoofed Vessel",
            vessel_type="cargo",
            lat=50.0,
            lon=50.0,
            speed_knots=100.0,
            course=180.0,
            destination="Unknown",
            flag_country="Unknown",
            last_port="Unknown",
            position_jump_nm=500,
        )

        assert signal is not None
        assert signal.anomaly_score > 0

    def test_excessive_speed_detection(self):
        """Test detection of excessive speed."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="333222111",
            vessel_name="Fast Vessel",
            vessel_type="cargo",
            lat=12.0,
            lon=114.0,
            speed_knots=50.0,
            course=90.0,
            destination="Singapore",
            flag_country="Panama",
            last_port="Hong Kong",
        )

        assert signal is not None
        assert signal.anomaly_score > 0


class TestMaritimeLocations:
    """Tests for maritime location handling."""

    def test_south_china_sea_monitoring(self):
        """Test monitoring in South China Sea."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="123123123",
            vessel_name="Test Vessel",
            vessel_type="cargo",
            lat=12.0,
            lon=114.0,
            speed_knots=15.0,
            course=180.0,
            destination="Singapore",
            flag_country="China",
            last_port="Shenzhen",
        )

        assert signal is not None
        assert signal.location["lat"] == 12.0
        assert signal.location["lon"] == 114.0

    def test_persian_gulf_monitoring(self):
        """Test monitoring in Persian Gulf."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="456456456",
            vessel_name="Gulf Tanker",
            vessel_type="tanker",
            lat=26.5,
            lon=51.0,
            speed_knots=10.0,
            course=270.0,
            destination="Rotterdam",
            flag_country="Iran",
            last_port="Bandar Abbas",
        )

        assert signal is not None

    def test_taiwan_strait_monitoring(self):
        """Test monitoring in Taiwan Strait."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="789789789",
            vessel_name="Strait Vessel",
            vessel_type="cargo",
            lat=24.0,
            lon=119.0,
            speed_knots=12.0,
            course=0.0,
            destination="Kaohsiung",
            flag_country="Taiwan",
            last_port="Shanghai",
        )

        assert signal is not None


class TestMaritimeAnomalyScoring:
    """Tests for maritime anomaly scoring."""

    def test_normal_vessel_low_anomaly_score(self):
        """Test that normal vessel has low anomaly score."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="111111111",
            vessel_name="Normal Vessel",
            vessel_type="cargo",
            lat=12.0,
            lon=114.0,
            speed_knots=15.0,
            course=180.0,
            destination="Singapore",
            flag_country="Panama",
            last_port="Hong Kong",
        )

        assert signal.anomaly_score < 0.5

    def test_suspicious_vessel_high_anomaly_score(self):
        """Test that suspicious vessel has high anomaly score."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="222222222",
            vessel_name="Unknown",
            vessel_type="unknown",
            lat=26.5,
            lon=51.0,
            speed_knots=0.0,
            course=0.0,
            destination="Unknown",
            flag_country="Unknown",
            last_port="Unknown",
            ais_gap_hours=72,
        )

        assert signal.anomaly_score > 0.5


class TestMaritimeChainOfCustody:
    """Tests for maritime chain of custody."""

    def test_maritime_signal_has_hash(self):
        """Test that maritime signal has chain of custody hash."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="333333333",
            vessel_name="Test Vessel",
            vessel_type="cargo",
            lat=12.0,
            lon=114.0,
            speed_knots=15.0,
            course=180.0,
            destination="Singapore",
            flag_country="Panama",
            last_port="Hong Kong",
        )

        assert signal.chain_of_custody_hash is not None
        assert len(signal.chain_of_custody_hash) == 64


class TestSatelliteMaritimeAnalysis:
    """Tests for satellite-based maritime analysis."""

    def test_satellite_maritime_detection(self):
        """Test satellite-based maritime activity detection."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="sentinel_2",
            lat=12.0,
            lon=114.0,
            region="South China Sea",
            resolution_meters=10.0,
            cloud_cover_percent=5.0,
            bands=["B2", "B3", "B4", "B8"],
            metadata={},
        )

        detection = layer.analyze_maritime_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "vessel_count")
        assert hasattr(detection, "port_activity_level")
        assert hasattr(detection, "anomalies")
