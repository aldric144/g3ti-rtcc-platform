"""
Test Suite 8: Crisis Ingestion Tests

Tests for crisis feed ingestion functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestCrisisEventTypes:
    """Tests for crisis event type handling."""

    def test_earthquake_event_ingestion(self):
        """Test ingesting earthquake events."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="earthquake",
            severity=5,
            lat=35.0,
            lon=139.0,
            country="Japan",
            region="Kanto",
            affected_population=5000000,
            casualties=50,
            displaced=10000,
            description="Major earthquake",
            source="gdacs",
        )

        assert signal is not None
        assert "earthquake" in signal.title.lower() or signal.raw_data.get("event_type") == "earthquake"

    def test_flood_event_ingestion(self):
        """Test ingesting flood events."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="flood",
            severity=4,
            lat=20.0,
            lon=100.0,
            country="Thailand",
            region="Central",
            affected_population=100000,
            casualties=20,
            displaced=5000,
            description="Severe flooding",
            source="reliefweb",
        )

        assert signal is not None

    def test_cyclone_event_ingestion(self):
        """Test ingesting cyclone events."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="cyclone",
            severity=5,
            lat=22.0,
            lon=91.0,
            country="Bangladesh",
            region="Chittagong",
            affected_population=2000000,
            casualties=100,
            displaced=50000,
            description="Category 4 cyclone",
            source="gdacs",
        )

        assert signal is not None

    def test_drought_event_ingestion(self):
        """Test ingesting drought events."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="drought",
            severity=3,
            lat=-5.0,
            lon=35.0,
            country="Tanzania",
            region="East Africa",
            affected_population=500000,
            casualties=0,
            displaced=0,
            description="Prolonged drought",
            source="reliefweb",
        )

        assert signal is not None

    def test_wildfire_event_ingestion(self):
        """Test ingesting wildfire events."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="wildfire",
            severity=4,
            lat=34.0,
            lon=-118.0,
            country="USA",
            region="California",
            affected_population=50000,
            casualties=5,
            displaced=10000,
            description="Major wildfire",
            source="gdacs",
        )

        assert signal is not None


class TestCrisisDataSources:
    """Tests for crisis data source handling."""

    def test_gdacs_source_ingestion(self):
        """Test ingesting from GDACS source."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer, DataSource

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="earthquake",
            severity=4,
            lat=0.0,
            lon=0.0,
            country="Test",
            region="Test",
            affected_population=0,
            casualties=0,
            displaced=0,
            description="Test",
            source="gdacs",
        )

        assert signal.source == DataSource.GDACS

    def test_reliefweb_source_ingestion(self):
        """Test ingesting from ReliefWeb source."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer, DataSource

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="flood",
            severity=3,
            lat=0.0,
            lon=0.0,
            country="Test",
            region="Test",
            affected_population=0,
            casualties=0,
            displaced=0,
            description="Test",
            source="reliefweb",
        )

        assert signal.source == DataSource.RELIEFWEB

    def test_acled_source_ingestion(self):
        """Test ingesting from ACLED source."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer, DataSource

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="conflict",
            severity=5,
            lat=0.0,
            lon=0.0,
            country="Test",
            region="Test",
            affected_population=0,
            casualties=0,
            displaced=0,
            description="Test",
            source="acled",
        )

        assert signal.source == DataSource.ACLED


class TestCrisisSeverityMapping:
    """Tests for crisis severity mapping."""

    def test_severity_1_maps_to_informational(self):
        """Test that severity 1 maps to INFORMATIONAL."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer, SeverityLevel

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="test",
            severity=1,
            lat=0.0,
            lon=0.0,
            country="Test",
            region="Test",
            affected_population=0,
            casualties=0,
            displaced=0,
            description="Test",
            source="gdacs",
        )

        assert signal.severity == SeverityLevel.INFORMATIONAL

    def test_severity_5_maps_to_critical(self):
        """Test that severity 5 maps to CRITICAL."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer, SeverityLevel

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="test",
            severity=5,
            lat=0.0,
            lon=0.0,
            country="Test",
            region="Test",
            affected_population=0,
            casualties=0,
            displaced=0,
            description="Test",
            source="gdacs",
        )

        assert signal.severity == SeverityLevel.CRITICAL


class TestCrisisChainOfCustody:
    """Tests for crisis chain of custody."""

    def test_crisis_signal_has_hash(self):
        """Test that crisis signal has chain of custody hash."""
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
            casualties=10,
            displaced=5000,
            description="Test earthquake",
            source="gdacs",
        )

        assert signal.chain_of_custody_hash is not None
        assert len(signal.chain_of_custody_hash) == 64

    def test_crisis_hash_is_sha256(self):
        """Test that crisis hash is SHA256 format."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer
        import re

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="flood",
            severity=3,
            lat=20.0,
            lon=100.0,
            country="Thailand",
            region="Central",
            affected_population=50000,
            casualties=5,
            displaced=2000,
            description="Test flood",
            source="reliefweb",
        )

        assert re.match(r"^[a-f0-9]{64}$", signal.chain_of_custody_hash)


class TestCrisisSignalID:
    """Tests for crisis signal ID generation."""

    def test_crisis_signal_id_format(self):
        """Test that crisis signal ID has correct format."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal = layer.ingest_crisis_feed(
            event_type="earthquake",
            severity=4,
            lat=0.0,
            lon=0.0,
            country="Test",
            region="Test",
            affected_population=0,
            casualties=0,
            displaced=0,
            description="Test",
            source="gdacs",
        )

        assert signal.signal_id.startswith("CE-")

    def test_crisis_signal_ids_are_unique(self):
        """Test that crisis signal IDs are unique."""
        from backend.app.global_awareness.global_sensor_layer import GlobalSensorLayer

        layer = GlobalSensorLayer()
        signal1 = layer.ingest_crisis_feed(
            event_type="earthquake",
            severity=4,
            lat=0.0,
            lon=0.0,
            country="Test",
            region="Test",
            affected_population=0,
            casualties=0,
            displaced=0,
            description="Test 1",
            source="gdacs",
        )

        signal2 = layer.ingest_crisis_feed(
            event_type="earthquake",
            severity=4,
            lat=0.0,
            lon=0.0,
            country="Test",
            region="Test",
            affected_population=0,
            casualties=0,
            displaced=0,
            description="Test 2",
            source="gdacs",
        )

        assert signal1.signal_id != signal2.signal_id
