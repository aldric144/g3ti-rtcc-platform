"""Tests for Crime Heatmap Engine Module."""

import pytest
from datetime import datetime, timedelta
from app.crime_analysis.crime_heatmap_engine import (
    CrimeHeatmapEngine,
    TimeRange,
    HeatmapPoint,
    HotspotCluster,
    HeatmapResult,
    get_heatmap_engine,
)
from app.crime_analysis.crime_ingest import (
    CrimeDataIngestor,
    NormalizedCrimeRecord,
    CrimeType,
    CrimePriority,
)


class TestCrimeHeatmapEngine:
    """Test suite for CrimeHeatmapEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = CrimeHeatmapEngine()
        # Clear any existing records
        self.engine.ingestor.clear_records()

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine.DEFAULT_BANDWIDTH == 0.005
        assert self.engine.GRID_SIZE == 50
        assert self.engine.MIN_CLUSTER_SIZE == 3

    def test_time_range_enum(self):
        """Test TimeRange enum values."""
        assert TimeRange.HOURS_24.value == "24h"
        assert TimeRange.DAYS_7.value == "7d"
        assert TimeRange.DAYS_30.value == "30d"
        assert TimeRange.CUSTOM.value == "custom"

    def test_filter_by_time_range_24h(self):
        """Test filtering by 24 hour time range."""
        now = datetime.utcnow()
        records = [
            self._create_mock_record(now - timedelta(hours=12)),
            self._create_mock_record(now - timedelta(hours=36)),
        ]
        
        filtered, start, end = self.engine._filter_by_time_range(
            records, TimeRange.HOURS_24
        )
        
        assert len(filtered) == 1

    def test_filter_by_time_range_7d(self):
        """Test filtering by 7 day time range."""
        now = datetime.utcnow()
        records = [
            self._create_mock_record(now - timedelta(days=3)),
            self._create_mock_record(now - timedelta(days=10)),
        ]
        
        filtered, start, end = self.engine._filter_by_time_range(
            records, TimeRange.DAYS_7
        )
        
        assert len(filtered) == 1

    def test_filter_by_crime_type(self):
        """Test filtering by crime type."""
        records = [
            self._create_mock_record(crime_type=CrimeType.VIOLENT),
            self._create_mock_record(crime_type=CrimeType.PROPERTY),
            self._create_mock_record(crime_type=CrimeType.VIOLENT),
        ]
        
        filtered = self.engine._filter_by_crime_type(records, [CrimeType.VIOLENT])
        
        assert len(filtered) == 2

    def test_filter_by_crime_type_none(self):
        """Test filtering with no crime type filter."""
        records = [
            self._create_mock_record(crime_type=CrimeType.VIOLENT),
            self._create_mock_record(crime_type=CrimeType.PROPERTY),
        ]
        
        filtered = self.engine._filter_by_crime_type(records, None)
        
        assert len(filtered) == 2

    def test_gaussian_kernel(self):
        """Test Gaussian kernel calculation."""
        # At distance 0, kernel should be 1
        assert self.engine._gaussian_kernel(0, 1) == 1.0
        
        # Kernel should decrease with distance
        k1 = self.engine._gaussian_kernel(0.5, 1)
        k2 = self.engine._gaussian_kernel(1.0, 1)
        assert k1 > k2

    def test_calculate_distance(self):
        """Test distance calculation."""
        dist = self.engine._calculate_distance(0, 0, 3, 4)
        assert dist == 5.0  # 3-4-5 triangle

    def test_calculate_bounds_empty(self):
        """Test bounds calculation with no records."""
        bounds = self.engine._calculate_bounds([])
        
        # Should return default Riviera Beach bounds
        assert "north" in bounds
        assert "south" in bounds
        assert "east" in bounds
        assert "west" in bounds

    def test_calculate_bounds_with_records(self):
        """Test bounds calculation with records."""
        records = [
            self._create_mock_record(lat=26.78, lng=-80.07),
            self._create_mock_record(lat=26.80, lng=-80.05),
        ]
        
        bounds = self.engine._calculate_bounds(records)
        
        assert bounds["north"] > 26.80
        assert bounds["south"] < 26.78
        assert bounds["east"] > -80.05
        assert bounds["west"] < -80.07

    def test_simple_clustering_empty(self):
        """Test clustering with no records."""
        clusters = self.engine._simple_clustering([])
        assert clusters == []

    def test_simple_clustering_creates_clusters(self):
        """Test clustering creates clusters from nearby points."""
        # Create 5 nearby records (should form a cluster)
        records = [
            self._create_mock_record(lat=26.78, lng=-80.07),
            self._create_mock_record(lat=26.7801, lng=-80.0701),
            self._create_mock_record(lat=26.7802, lng=-80.0702),
            self._create_mock_record(lat=26.7803, lng=-80.0703),
            self._create_mock_record(lat=26.7804, lng=-80.0704),
        ]
        
        clusters = self.engine._simple_clustering(records, epsilon=0.01)
        
        assert len(clusters) >= 1

    def test_generate_heatmap_empty(self):
        """Test heatmap generation with no data."""
        result = self.engine.generate_heatmap()
        
        assert isinstance(result, HeatmapResult)
        assert result.total_incidents == 0
        assert result.points == []
        assert result.hotspots == []

    def test_generate_heatmap_with_data(self):
        """Test heatmap generation with data."""
        # Add some test data
        self.engine.ingestor.ingest_json("""[
            {"subcategory": "Assault", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07, "type": "violent"},
            {"subcategory": "Theft", "date": "2024-01-15", "latitude": 26.79, "longitude": -80.08, "type": "property"}
        ]""")
        
        result = self.engine.generate_heatmap(time_range=TimeRange.DAYS_30)
        
        assert isinstance(result, HeatmapResult)
        assert result.total_incidents == 2

    def test_get_heatmap_engine_singleton(self):
        """Test global engine singleton."""
        engine1 = get_heatmap_engine()
        engine2 = get_heatmap_engine()
        
        assert engine1 is engine2

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
            id=f"test-{dt.timestamp()}",
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
