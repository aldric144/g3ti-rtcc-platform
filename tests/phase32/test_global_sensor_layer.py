"""
Test Suite 1: Global Sensor Layer Tests

Tests for Multi-Domain Global Sensor Layer functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestSensorDomains:
    """Tests for sensor domain enumeration."""

    def test_sensor_domain_crisis_exists(self):
        """Test that CRISIS domain is defined."""
        from backend.app.global_awareness.global_sensor_layer import SensorDomain
        assert hasattr(SensorDomain, "CRISIS")
        assert SensorDomain.CRISIS.value == "crisis"

    def test_sensor_domain_conflict_exists(self):
        """Test that CONFLICT domain is defined."""
        from backend.app.global_awareness.global_sensor_layer import SensorDomain
        assert hasattr(SensorDomain, "CONFLICT")
        assert SensorDomain.CONFLICT.value == "conflict"

    def test_sensor_domain_maritime_exists(self):
        """Test that MARITIME domain is defined."""
        from backend.app.global_awareness.global_sensor_layer import SensorDomain
        assert hasattr(SensorDomain, "MARITIME")
        assert SensorDomain.MARITIME.value == "maritime"

    def test_sensor_domain_aviation_exists(self):
        """Test that AVIATION domain is defined."""
        from backend.app.global_awareness.global_sensor_layer import SensorDomain
        assert hasattr(SensorDomain, "AVIATION")
        assert SensorDomain.AVIATION.value == "aviation"

    def test_sensor_domain_cyber_exists(self):
        """Test that CYBER domain is defined."""
        from backend.app.global_awareness.global_sensor_layer import SensorDomain
        assert hasattr(SensorDomain, "CYBER")
        assert SensorDomain.CYBER.value == "cyber"

    def test_all_ten_domains_defined(self):
        """Test that all 10 sensor domains are defined."""
        from backend.app.global_awareness.global_sensor_layer import SensorDomain
        domains = list(SensorDomain)
        assert len(domains) == 10


class TestDataSources:
    """Tests for data source enumeration."""

    def test_data_source_gdacs_exists(self):
        """Test that GDACS source is defined."""
        from backend.app.global_awareness.global_sensor_layer import DataSource
        assert hasattr(DataSource, "GDACS")

    def test_data_source_reliefweb_exists(self):
        """Test that RELIEFWEB source is defined."""
        from backend.app.global_awareness.global_sensor_layer import DataSource
        assert hasattr(DataSource, "RELIEFWEB")

    def test_data_source_acled_exists(self):
        """Test that ACLED source is defined."""
        from backend.app.global_awareness.global_sensor_layer import DataSource
        assert hasattr(DataSource, "ACLED")

    def test_data_source_ais_exists(self):
        """Test that AIS source is defined."""
        from backend.app.global_awareness.global_sensor_layer import DataSource
        assert hasattr(DataSource, "AIS")

    def test_data_source_adsb_exists(self):
        """Test that ADSB source is defined."""
        from backend.app.global_awareness.global_sensor_layer import DataSource
        assert hasattr(DataSource, "ADSB")

    def test_all_fourteen_sources_defined(self):
        """Test that all 14 data sources are defined."""
        from backend.app.global_awareness.global_sensor_layer import DataSource
        sources = list(DataSource)
        assert len(sources) == 14


class TestSeverityLevels:
    """Tests for severity level enumeration."""

    def test_severity_informational(self):
        """Test INFORMATIONAL severity level."""
        from backend.app.global_awareness.global_sensor_layer import SeverityLevel
        assert SeverityLevel.INFORMATIONAL.value == 1

    def test_severity_low(self):
        """Test LOW severity level."""
        from backend.app.global_awareness.global_sensor_layer import SeverityLevel
        assert SeverityLevel.LOW.value == 2

    def test_severity_moderate(self):
        """Test MODERATE severity level."""
        from backend.app.global_awareness.global_sensor_layer import SeverityLevel
        assert SeverityLevel.MODERATE.value == 3

    def test_severity_high(self):
        """Test HIGH severity level."""
        from backend.app.global_awareness.global_sensor_layer import SeverityLevel
        assert SeverityLevel.HIGH.value == 4

    def test_severity_critical(self):
        """Test CRITICAL severity level."""
        from backend.app.global_awareness.global_sensor_layer import SeverityLevel
        assert SeverityLevel.CRITICAL.value == 5


class TestGlobalSignal:
    """Tests for GlobalSignal data class."""

    def test_global_signal_creation(self):
        """Test creating a GlobalSignal instance."""
        from backend.app.global_awareness.global_sensor_layer import (
            GlobalSignal,
            SensorDomain,
            DataSource,
            SeverityLevel,
            SignalStatus,
        )

        signal = GlobalSignal(
            signal_id="TEST-001",
            domain=SensorDomain.CRISIS,
            source=DataSource.GDACS,
            severity=SeverityLevel.HIGH,
            status=SignalStatus.RAW,
            title="Test Crisis Event",
            description="Test description",
            timestamp=datetime.utcnow(),
            location={"lat": 0.0, "lon": 0.0},
            affected_regions=["Test Region"],
            affected_countries=["Test Country"],
            raw_data={},
            confidence_score=0.85,
            chain_of_custody_hash="test_hash",
        )

        assert signal.signal_id == "TEST-001"
        assert signal.domain == SensorDomain.CRISIS
        assert signal.severity == SeverityLevel.HIGH

    def test_global_signal_has_chain_of_custody(self):
        """Test that GlobalSignal includes chain of custody hash."""
        from backend.app.global_awareness.global_sensor_layer import (
            GlobalSignal,
            SensorDomain,
            DataSource,
            SeverityLevel,
            SignalStatus,
        )

        signal = GlobalSignal(
            signal_id="TEST-002",
            domain=SensorDomain.CYBER,
            source=DataSource.THREAT_INTEL,
            severity=SeverityLevel.CRITICAL,
            status=SignalStatus.VALIDATED,
            title="Test Cyber Threat",
            description="Test description",
            timestamp=datetime.utcnow(),
            location={"lat": 0.0, "lon": 0.0},
            affected_regions=[],
            affected_countries=["USA"],
            raw_data={},
            confidence_score=0.90,
            chain_of_custody_hash="sha256_hash_value",
        )

        assert signal.chain_of_custody_hash is not None
        assert len(signal.chain_of_custody_hash) > 0


class TestGlobalSensorLayer:
    """Tests for GlobalSensorLayer class."""

    def test_sensor_layer_singleton(self):
        """Test that GlobalSensorLayer is a singleton."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer1 = GlobalSensorLayer()
        layer2 = GlobalSensorLayer()
        assert layer1 is layer2

    def test_sensor_layer_has_signals_storage(self):
        """Test that sensor layer has signals storage."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        assert hasattr(layer, "signals")

    def test_sensor_layer_has_statistics(self):
        """Test that sensor layer tracks statistics."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        stats = layer.get_statistics()
        assert "total_signals" in stats
        assert "signals_by_domain" in stats


class TestCrisisIngestion:
    """Tests for crisis feed ingestion."""

    def test_ingest_crisis_feed_returns_signal(self):
        """Test that ingesting crisis feed returns a signal."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="earthquake",
            severity=4,
            lat=35.0,
            lon=139.0,
            country="Japan",
            region="Kanto",
            affected_population=1000000,
            casualties=0,
            displaced=5000,
            description="Magnitude 6.5 earthquake",
            source="gdacs",
        )

        assert signal is not None
        assert signal.signal_id.startswith("CE-")

    def test_ingest_crisis_feed_generates_hash(self):
        """Test that crisis ingestion generates chain of custody hash."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="flood",
            severity=3,
            lat=20.0,
            lon=100.0,
            country="Thailand",
            region="Central",
            affected_population=50000,
            casualties=10,
            displaced=2000,
            description="Severe flooding",
            source="reliefweb",
        )

        assert signal.chain_of_custody_hash is not None
        assert len(signal.chain_of_custody_hash) == 64


class TestMaritimeAnomalyDetection:
    """Tests for maritime anomaly detection."""

    def test_maritime_signal_creation(self):
        """Test creating a maritime signal."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="123456789",
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

        assert signal is not None
        assert signal.signal_id.startswith("MAR-")

    def test_maritime_anomaly_detection_dark_voyage(self):
        """Test detection of dark voyage anomaly."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_maritime_data(
            mmsi="987654321",
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


class TestAviationAnomalyDetection:
    """Tests for aviation anomaly detection."""

    def test_aviation_signal_creation(self):
        """Test creating an aviation signal."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_aviation_data(
            icao24="abc123",
            callsign="TEST123",
            origin_country="USA",
            lat=40.0,
            lon=-74.0,
            altitude_meters=10000,
            velocity_mps=250.0,
            heading=90.0,
            squawk="1200",
        )

        assert signal is not None
        assert signal.signal_id.startswith("AVI-")

    def test_aviation_emergency_squawk_detection(self):
        """Test detection of emergency squawk codes."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_aviation_data(
            icao24="def456",
            callsign="EMERG01",
            origin_country="UK",
            lat=51.5,
            lon=-0.1,
            altitude_meters=5000,
            velocity_mps=200.0,
            heading=270.0,
            squawk="7700",
        )

        assert signal is not None
        assert signal.anomaly_type == "emergency"


class TestSignalQueries:
    """Tests for signal query methods."""

    def test_get_signals_by_domain(self):
        """Test filtering signals by domain."""
        from backend.app.global_awareness.global_sensor_layer import (
            GlobalSensorLayer,
            SensorDomain,
        )

        layer = GlobalSensorLayer()
        signals = layer.get_signals_by_domain(SensorDomain.CRISIS)
        assert isinstance(signals, list)

    def test_get_signals_by_severity(self):
        """Test filtering signals by severity."""
        from backend.app.global_awareness.global_sensor_layer import (
            GlobalSensorLayer,
            SeverityLevel,
        )

        layer = GlobalSensorLayer()
        signals = layer.get_signals_by_severity(SeverityLevel.CRITICAL)
        assert isinstance(signals, list)

    def test_get_actionable_signals(self):
        """Test getting actionable signals."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signals = layer.get_actionable_signals()
        assert isinstance(signals, list)

    def test_get_recent_signals(self):
        """Test getting recent signals."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signals = layer.get_recent_signals(hours=24)
        assert isinstance(signals, list)
