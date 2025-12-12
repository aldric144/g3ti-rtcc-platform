"""
Test Suite 11: Military Detection Tests

Tests for military activity detection functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestMilitaryActivityTypes:
    """Tests for military activity type detection."""

    def test_deployment_detection(self):
        """Test detection of military deployment."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "activity_type")

    def test_buildup_detection(self):
        """Test detection of military buildup."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=24.0,
            lon=119.0,
            region="Taiwan Strait",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None

    def test_exercise_detection(self):
        """Test detection of military exercise."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="planet",
            lat=38.0,
            lon=127.0,
            region="Korean DMZ",
            resolution_meters=3.0,
            cloud_cover_percent=5.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None


class TestMilitaryUnitTypes:
    """Tests for military unit type detection."""

    def test_armor_unit_detection(self):
        """Test detection of armor units."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "unit_types")
        assert isinstance(detection.unit_types, list)

    def test_artillery_unit_detection(self):
        """Test detection of artillery units."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "unit_types")


class TestMilitaryPersonnelEstimation:
    """Tests for military personnel estimation."""

    def test_personnel_estimation(self):
        """Test estimation of military personnel."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "estimated_personnel")
        assert isinstance(detection.estimated_personnel, int)
        assert detection.estimated_personnel >= 0


class TestMilitaryVehicleCount:
    """Tests for military vehicle counting."""

    def test_vehicle_count(self):
        """Test counting of military vehicles."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "vehicle_count")
        assert isinstance(detection.vehicle_count, int)
        assert detection.vehicle_count >= 0


class TestMilitaryAircraftCount:
    """Tests for military aircraft counting."""

    def test_aircraft_count(self):
        """Test counting of military aircraft."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "aircraft_count")
        assert isinstance(detection.aircraft_count, int)
        assert detection.aircraft_count >= 0


class TestMilitaryConfidence:
    """Tests for military detection confidence."""

    def test_detection_has_confidence(self):
        """Test that detection has confidence level."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "confidence")


class TestMilitaryAssessment:
    """Tests for military activity assessment."""

    def test_detection_has_assessment(self):
        """Test that detection has assessment text."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "assessment")
        assert isinstance(detection.assessment, str)


class TestMilitaryAlerts:
    """Tests for military activity alerts."""

    def test_military_alert_generation(self):
        """Test that military detections generate alerts."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        alerts = layer.get_active_alerts()
        assert isinstance(alerts, list)


class TestMilitaryChainOfCustody:
    """Tests for military detection chain of custody."""

    def test_military_detection_has_hash(self):
        """Test that military detection has chain of custody hash."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detection = layer.detect_military_activity(image.image_id)

        assert detection is not None
        assert hasattr(detection, "chain_of_custody_hash")
        assert detection.chain_of_custody_hash is not None


class TestMilitaryMonitoredLocations:
    """Tests for military monitored locations."""

    def test_ukraine_border_monitoring(self):
        """Test monitoring of Ukraine border."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        assert any(loc["name"] == "Ukraine Border" for loc in layer.monitored_locations)

    def test_korean_dmz_monitoring(self):
        """Test monitoring of Korean DMZ."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        assert any(loc["name"] == "Korean DMZ" for loc in layer.monitored_locations)

    def test_taiwan_strait_monitoring(self):
        """Test monitoring of Taiwan Strait."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        assert any(loc["name"] == "Taiwan Strait" for loc in layer.monitored_locations)
