"""Tests for Repeat Location Detector Module."""

import pytest
from datetime import datetime, timedelta
from app.crime_analysis.repeat_location_detector import (
    RepeatLocationDetector,
    RepeatLocation,
    LocationCluster,
    RepeatLocationResult,
    get_repeat_detector,
)
from app.crime_analysis.crime_ingest import (
    NormalizedCrimeRecord,
    CrimeType,
    CrimePriority,
)


class TestRepeatLocationDetector:
    """Test suite for RepeatLocationDetector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = RepeatLocationDetector()
        self.detector.ingestor.clear_records()

    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        assert self.detector.COORD_PRECISION == 4
        assert self.detector.MIN_REPEAT_COUNT == 2
        assert len(self.detector.BUSINESS_INDICATORS) > 0

    def test_round_coords(self):
        """Test coordinate rounding."""
        lat, lng = self.detector._round_coords(26.78456789, -80.07123456)
        
        assert lat == 26.7846
        assert lng == -80.0712

    def test_is_business_true(self):
        """Test business detection for business addresses."""
        assert self.detector._is_business("123 Main St Plaza") is True
        assert self.detector._is_business("Walmart Supercenter") is True
        assert self.detector._is_business("7-Eleven Store") is True
        assert self.detector._is_business("Gas Station on Broadway") is True

    def test_is_business_false(self):
        """Test business detection for residential addresses."""
        assert self.detector._is_business("123 Oak Street") is False
        assert self.detector._is_business("456 Elm Avenue") is False
        assert self.detector._is_business(None) is False

    def test_calculate_severity_empty(self):
        """Test severity calculation with no records."""
        severity = self.detector._calculate_severity([])
        assert severity == 0.0

    def test_calculate_severity_with_records(self):
        """Test severity calculation with records."""
        records = [
            self._create_mock_record(crime_type=CrimeType.VIOLENT),
            self._create_mock_record(crime_type=CrimeType.PROPERTY),
        ]
        
        severity = self.detector._calculate_severity(records)
        
        assert severity > 0
        assert severity <= 5.0

    def test_group_by_location(self):
        """Test grouping records by location."""
        records = [
            self._create_mock_record(lat=26.7800, lng=-80.0700),
            self._create_mock_record(lat=26.7800, lng=-80.0700),
            self._create_mock_record(lat=26.7900, lng=-80.0800),
        ]
        
        groups = self.detector._group_by_location(records)
        
        assert len(groups) == 2
        # One location should have 2 records
        counts = [len(v) for v in groups.values()]
        assert 2 in counts

    def test_create_repeat_location(self):
        """Test creating a repeat location from records."""
        now = datetime.utcnow()
        records = [
            self._create_mock_record(dt=now - timedelta(days=5), crime_type=CrimeType.VIOLENT),
            self._create_mock_record(dt=now - timedelta(days=2), crime_type=CrimeType.PROPERTY),
        ]
        
        loc = self.detector._create_repeat_location((26.78, -80.07), records)
        
        assert isinstance(loc, RepeatLocation)
        assert loc.incident_count == 2
        assert len(loc.crime_types) == 2

    def test_cluster_locations_empty(self):
        """Test clustering with no locations."""
        clusters = self.detector._cluster_locations([])
        assert clusters == []

    def test_cluster_locations_creates_clusters(self):
        """Test clustering creates clusters from nearby locations."""
        locations = [
            RepeatLocation(
                location_id="loc-1",
                latitude=26.7800,
                longitude=-80.0700,
                address="123 Main St",
                incident_count=5,
                first_incident="2024-01-01T00:00:00",
                last_incident="2024-01-15T00:00:00",
                crime_types=["violent"],
                severity_score=3.0,
                is_business=False,
                sector="Sector 1",
                incidents=[],
            ),
            RepeatLocation(
                location_id="loc-2",
                latitude=26.7801,
                longitude=-80.0701,
                address="125 Main St",
                incident_count=3,
                first_incident="2024-01-02T00:00:00",
                last_incident="2024-01-14T00:00:00",
                crime_types=["property"],
                severity_score=2.0,
                is_business=False,
                sector="Sector 1",
                incidents=[],
            ),
        ]
        
        clusters = self.detector._cluster_locations(locations, epsilon=0.01)
        
        assert len(clusters) >= 1

    def test_detect_empty(self):
        """Test detection with no data."""
        result = self.detector.detect()
        
        assert isinstance(result, RepeatLocationResult)
        assert result.total_repeat_locations == 0

    def test_detect_with_data(self):
        """Test detection with data."""
        # Add records at same location
        self.detector.ingestor.ingest_json("""[
            {"subcategory": "Assault", "date": "2024-01-15", "latitude": 26.7800, "longitude": -80.0700, "type": "violent", "sector": "Sector 1"},
            {"subcategory": "Theft", "date": "2024-01-16", "latitude": 26.7800, "longitude": -80.0700, "type": "property", "sector": "Sector 1"},
            {"subcategory": "Burglary", "date": "2024-01-17", "latitude": 26.7800, "longitude": -80.0700, "type": "property", "sector": "Sector 1"}
        ]""")
        
        result = self.detector.detect(days=30, min_incidents=2)
        
        assert isinstance(result, RepeatLocationResult)
        assert result.total_repeat_locations >= 1

    def test_get_business_hotspots(self):
        """Test getting business hotspots."""
        self.detector.ingestor.ingest_json("""[
            {"subcategory": "Theft", "date": "2024-01-15", "latitude": 26.7800, "longitude": -80.0700, "type": "property", "sector": "Sector 1", "address": "Walmart Store"},
            {"subcategory": "Theft", "date": "2024-01-16", "latitude": 26.7800, "longitude": -80.0700, "type": "property", "sector": "Sector 1", "address": "Walmart Store"}
        ]""")
        
        hotspots = self.detector.get_business_hotspots(days=30)
        
        assert isinstance(hotspots, list)

    def test_get_residential_hotspots(self):
        """Test getting residential hotspots."""
        self.detector.ingestor.ingest_json("""[
            {"subcategory": "Assault", "date": "2024-01-15", "latitude": 26.7900, "longitude": -80.0800, "type": "violent", "sector": "Sector 2", "address": "123 Oak Street"},
            {"subcategory": "Assault", "date": "2024-01-16", "latitude": 26.7900, "longitude": -80.0800, "type": "violent", "sector": "Sector 2", "address": "123 Oak Street"}
        ]""")
        
        hotspots = self.detector.get_residential_hotspots(days=30)
        
        assert isinstance(hotspots, list)

    def test_get_repeat_detector_singleton(self):
        """Test global detector singleton."""
        detector1 = get_repeat_detector()
        detector2 = get_repeat_detector()
        
        assert detector1 is detector2

    def _create_mock_record(
        self,
        dt: datetime = None,
        lat: float = 26.78,
        lng: float = -80.07,
        crime_type: CrimeType = CrimeType.VIOLENT,
    ) -> NormalizedCrimeRecord:
        """Create a mock crime record for testing."""
        if dt is None:
            dt = datetime.utcnow()
        
        return NormalizedCrimeRecord(
            id=f"test-{dt.timestamp()}-{lat}-{lng}",
            type=crime_type,
            subcategory="Test Crime",
            time=dt.strftime("%H:%M:%S"),
            date=dt.strftime("%Y-%m-%d"),
            datetime_utc=dt,
            latitude=lat,
            longitude=lng,
            sector="Test Sector",
            priority=CrimePriority.MEDIUM,
            source="test",
        )
