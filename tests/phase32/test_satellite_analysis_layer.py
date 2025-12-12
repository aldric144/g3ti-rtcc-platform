"""
Test Suite 5: Satellite Analysis Layer Tests

Tests for Satellite Imagery Analysis Layer functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestImagerySource:
    """Tests for imagery source enumeration."""

    def test_imagery_source_sentinel_exists(self):
        """Test that SENTINEL_2 source is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ImagerySource
        assert hasattr(ImagerySource, "SENTINEL_2")

    def test_imagery_source_landsat_exists(self):
        """Test that LANDSAT_8 source is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ImagerySource
        assert hasattr(ImagerySource, "LANDSAT_8")

    def test_imagery_source_planet_exists(self):
        """Test that PLANET source is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ImagerySource
        assert hasattr(ImagerySource, "PLANET")

    def test_imagery_source_maxar_exists(self):
        """Test that MAXAR source is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ImagerySource
        assert hasattr(ImagerySource, "MAXAR")

    def test_all_seven_sources_defined(self):
        """Test that all 7 imagery sources are defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ImagerySource
        sources = list(ImagerySource)
        assert len(sources) == 7


class TestAnalysisType:
    """Tests for analysis type enumeration."""

    def test_analysis_type_change_detection_exists(self):
        """Test that CHANGE_DETECTION type is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import AnalysisType
        assert hasattr(AnalysisType, "CHANGE_DETECTION")

    def test_analysis_type_object_detection_exists(self):
        """Test that OBJECT_DETECTION type is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import AnalysisType
        assert hasattr(AnalysisType, "OBJECT_DETECTION")

    def test_analysis_type_damage_assessment_exists(self):
        """Test that DAMAGE_ASSESSMENT type is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import AnalysisType
        assert hasattr(AnalysisType, "DAMAGE_ASSESSMENT")

    def test_all_six_analysis_types_defined(self):
        """Test that all 6 analysis types are defined."""
        from backend.app.global_awareness.satellite_analysis_layer import AnalysisType
        types = list(AnalysisType)
        assert len(types) == 6


class TestChangeCategory:
    """Tests for change category enumeration."""

    def test_change_category_infrastructure_new_exists(self):
        """Test that INFRASTRUCTURE_NEW category is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ChangeCategory
        assert hasattr(ChangeCategory, "INFRASTRUCTURE_NEW")

    def test_change_category_infrastructure_damaged_exists(self):
        """Test that INFRASTRUCTURE_DAMAGED category is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ChangeCategory
        assert hasattr(ChangeCategory, "INFRASTRUCTURE_DAMAGED")

    def test_change_category_military_activity_exists(self):
        """Test that MILITARY_ACTIVITY category is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ChangeCategory
        assert hasattr(ChangeCategory, "MILITARY_ACTIVITY")

    def test_change_category_maritime_activity_exists(self):
        """Test that MARITIME_ACTIVITY category is defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ChangeCategory
        assert hasattr(ChangeCategory, "MARITIME_ACTIVITY")

    def test_all_nine_change_categories_defined(self):
        """Test that all 9 change categories are defined."""
        from backend.app.global_awareness.satellite_analysis_layer import ChangeCategory
        categories = list(ChangeCategory)
        assert len(categories) == 9


class TestSatelliteImage:
    """Tests for SatelliteImage data class."""

    def test_satellite_image_creation(self):
        """Test creating a SatelliteImage instance."""
        from backend.app.global_awareness.satellite_analysis_layer import (
            SatelliteImage,
            ImagerySource,
        )

        image = SatelliteImage(
            image_id="IMG-001",
            source=ImagerySource.SENTINEL_2,
            capture_time=datetime.utcnow(),
            location={"lat": 50.0, "lon": 36.0},
            region="Ukraine Border",
            resolution_meters=10.0,
            cloud_cover_percent=5.0,
            bands=["B2", "B3", "B4", "B8"],
            metadata={},
            chain_of_custody_hash="test_hash",
        )

        assert image.image_id == "IMG-001"
        assert image.source == ImagerySource.SENTINEL_2
        assert image.resolution_meters == 10.0


class TestChangeDetection:
    """Tests for ChangeDetection data class."""

    def test_change_detection_creation(self):
        """Test creating a ChangeDetection instance."""
        from backend.app.global_awareness.satellite_analysis_layer import (
            ChangeDetection,
            ChangeCategory,
            ConfidenceLevel,
        )

        detection = ChangeDetection(
            detection_id="CD-001",
            image_id="IMG-001",
            before_image_id="IMG-000",
            change_category=ChangeCategory.MILITARY_ACTIVITY,
            location={"lat": 50.0, "lon": 36.0},
            bounding_box={"min_lat": 49.9, "max_lat": 50.1, "min_lon": 35.9, "max_lon": 36.1},
            area_sq_km=2.5,
            change_magnitude=0.85,
            confidence=ConfidenceLevel.HIGH,
            description="Military activity detected",
            timestamp=datetime.utcnow(),
            chain_of_custody_hash="test_hash",
        )

        assert detection.detection_id == "CD-001"
        assert detection.change_category == ChangeCategory.MILITARY_ACTIVITY
        assert detection.confidence == ConfidenceLevel.HIGH


class TestSatelliteAnalysisLayer:
    """Tests for SatelliteAnalysisLayer class."""

    def test_satellite_analysis_singleton(self):
        """Test that SatelliteAnalysisLayer is a singleton."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer1 = SatelliteAnalysisLayer()
        layer2 = SatelliteAnalysisLayer()
        assert layer1 is layer2

    def test_satellite_analysis_has_images_storage(self):
        """Test that satellite analysis has images storage."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        assert hasattr(layer, "images")

    def test_satellite_analysis_has_detections_storage(self):
        """Test that satellite analysis has detections storage."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        assert hasattr(layer, "detections")

    def test_satellite_analysis_has_monitored_locations(self):
        """Test that satellite analysis has monitored locations."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        assert hasattr(layer, "monitored_locations")
        assert len(layer.monitored_locations) > 0


class TestImageIngestion:
    """Tests for image ingestion."""

    def test_ingest_image(self):
        """Test ingesting a satellite image."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        image = layer.ingest_image(
            source="sentinel_2",
            lat=50.0,
            lon=36.0,
            region="Ukraine Border",
            resolution_meters=10.0,
            cloud_cover_percent=5.0,
            bands=["B2", "B3", "B4", "B8"],
            metadata={},
        )

        assert image is not None
        assert image.image_id.startswith("IMG-")

    def test_ingest_image_generates_hash(self):
        """Test that image ingestion generates chain of custody hash."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        image = layer.ingest_image(
            source="maxar",
            lat=12.0,
            lon=114.0,
            region="South China Sea",
            resolution_meters=0.3,
            cloud_cover_percent=2.0,
            bands=["RGB"],
            metadata={},
        )

        assert image.chain_of_custody_hash is not None
        assert len(image.chain_of_custody_hash) == 64


class TestChangeDetectionAnalysis:
    """Tests for change detection analysis."""

    def test_detect_changes(self):
        """Test detecting changes between images."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        before_image = layer.ingest_image(
            source="sentinel_2",
            lat=50.0,
            lon=36.0,
            region="Test Region",
            resolution_meters=10.0,
            cloud_cover_percent=5.0,
            bands=["B2", "B3", "B4"],
            metadata={},
        )

        after_image = layer.ingest_image(
            source="sentinel_2",
            lat=50.0,
            lon=36.0,
            region="Test Region",
            resolution_meters=10.0,
            cloud_cover_percent=5.0,
            bands=["B2", "B3", "B4"],
            metadata={},
        )

        detections = layer.detect_changes(
            before_image_id=before_image.image_id,
            after_image_id=after_image.image_id,
        )

        assert isinstance(detections, list)

    def test_change_detection_has_chain_of_custody(self):
        """Test that change detection has chain of custody hash."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        before_image = layer.ingest_image(
            source="planet",
            lat=31.5,
            lon=34.5,
            region="Gaza",
            resolution_meters=3.0,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        after_image = layer.ingest_image(
            source="planet",
            lat=31.5,
            lon=34.5,
            region="Gaza",
            resolution_meters=3.0,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        detections = layer.detect_changes(
            before_image_id=before_image.image_id,
            after_image_id=after_image.image_id,
        )

        if detections:
            assert detections[0].chain_of_custody_hash is not None


class TestMaritimeAnalysis:
    """Tests for maritime activity analysis."""

    def test_analyze_maritime_activity(self):
        """Test analyzing maritime activity from satellite imagery."""
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


class TestInfrastructureAssessment:
    """Tests for infrastructure assessment."""

    def test_assess_infrastructure(self):
        """Test assessing infrastructure from satellite imagery."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()

        image = layer.ingest_image(
            source="maxar",
            lat=31.5,
            lon=34.5,
            region="Gaza",
            resolution_meters=0.3,
            cloud_cover_percent=0.0,
            bands=["RGB"],
            metadata={},
        )

        assessment = layer.assess_infrastructure(image.image_id)

        assert assessment is not None
        assert hasattr(assessment, "infrastructure_type")
        assert hasattr(assessment, "condition")
        assert hasattr(assessment, "damage_level")


class TestMilitaryDetection:
    """Tests for military activity detection."""

    def test_detect_military_activity(self):
        """Test detecting military activity from satellite imagery."""
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
        assert hasattr(detection, "unit_types")
        assert hasattr(detection, "estimated_personnel")
        assert hasattr(detection, "vehicle_count")


class TestSatelliteAlerts:
    """Tests for satellite alerts."""

    def test_get_active_alerts(self):
        """Test getting active satellite alerts."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        alerts = layer.get_active_alerts()
        assert isinstance(alerts, list)

    def test_get_recent_detections(self):
        """Test getting recent detections."""
        from backend.app.global_awareness.satellite_analysis_layer import SatelliteAnalysisLayer

        layer = SatelliteAnalysisLayer()
        detections = layer.get_recent_detections(hours=24)
        assert isinstance(detections, list)
