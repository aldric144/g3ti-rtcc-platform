"""Tests for Crime Time Series Analysis Module."""

import pytest
from datetime import datetime, timedelta
from app.crime_analysis.crime_timeseries import (
    CrimeTimeseriesAnalyzer,
    TimeseriesPoint,
    TrendInfo,
    AnomalyAlert,
    TimeseriesResult,
    get_timeseries_analyzer,
)
from app.crime_analysis.crime_ingest import (
    NormalizedCrimeRecord,
    CrimeType,
    CrimePriority,
)


class TestCrimeTimeseriesAnalyzer:
    """Test suite for CrimeTimeseriesAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CrimeTimeseriesAnalyzer()
        self.analyzer.ingestor.clear_records()

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        assert self.analyzer.ANOMALY_THRESHOLD == 2.0
        assert self.analyzer.MIN_TREND_POINTS == 3

    def test_aggregate_hourly_empty(self):
        """Test hourly aggregation with no records."""
        now = datetime.utcnow()
        start = now - timedelta(hours=24)
        
        result = self.analyzer._aggregate_hourly([], start, now)
        
        assert len(result) >= 24  # Should have at least 24 hours

    def test_aggregate_hourly_with_records(self):
        """Test hourly aggregation with records."""
        now = datetime.utcnow()
        start = now - timedelta(hours=2)
        
        records = [
            self._create_mock_record(now - timedelta(hours=1), CrimeType.VIOLENT),
            self._create_mock_record(now - timedelta(hours=1), CrimeType.PROPERTY),
        ]
        
        result = self.analyzer._aggregate_hourly(records, start, now)
        
        # Find the hour with records
        hour_with_records = [p for p in result if p.count > 0]
        assert len(hour_with_records) >= 1

    def test_aggregate_daily_empty(self):
        """Test daily aggregation with no records."""
        now = datetime.utcnow()
        start = now - timedelta(days=7)
        
        result = self.analyzer._aggregate_daily([], start, now)
        
        assert len(result) >= 7  # Should have at least 7 days

    def test_aggregate_daily_with_records(self):
        """Test daily aggregation with records."""
        now = datetime.utcnow()
        start = now - timedelta(days=3)
        
        records = [
            self._create_mock_record(now - timedelta(days=1), CrimeType.VIOLENT),
            self._create_mock_record(now - timedelta(days=1), CrimeType.PROPERTY),
            self._create_mock_record(now - timedelta(days=2), CrimeType.VIOLENT),
        ]
        
        result = self.analyzer._aggregate_daily(records, start, now)
        
        # Find days with records
        days_with_records = [p for p in result if p.count > 0]
        assert len(days_with_records) >= 1

    def test_calculate_trend_insufficient_data(self):
        """Test trend calculation with insufficient data."""
        data = [
            TimeseriesPoint(timestamp="2024-01-01", count=5, violent_count=2, property_count=2, other_count=1),
            TimeseriesPoint(timestamp="2024-01-02", count=6, violent_count=3, property_count=2, other_count=1),
        ]
        
        trend = self.analyzer._calculate_trend(data)
        
        assert trend.direction == "stable"
        assert trend.confidence == 0.0

    def test_calculate_trend_increasing(self):
        """Test trend calculation for increasing trend."""
        data = [
            TimeseriesPoint(timestamp="2024-01-01", count=2, violent_count=1, property_count=1, other_count=0),
            TimeseriesPoint(timestamp="2024-01-02", count=4, violent_count=2, property_count=2, other_count=0),
            TimeseriesPoint(timestamp="2024-01-03", count=6, violent_count=3, property_count=3, other_count=0),
            TimeseriesPoint(timestamp="2024-01-04", count=8, violent_count=4, property_count=4, other_count=0),
        ]
        
        trend = self.analyzer._calculate_trend(data)
        
        assert trend.direction == "increasing"
        assert trend.slope > 0

    def test_calculate_trend_decreasing(self):
        """Test trend calculation for decreasing trend."""
        data = [
            TimeseriesPoint(timestamp="2024-01-01", count=8, violent_count=4, property_count=4, other_count=0),
            TimeseriesPoint(timestamp="2024-01-02", count=6, violent_count=3, property_count=3, other_count=0),
            TimeseriesPoint(timestamp="2024-01-03", count=4, violent_count=2, property_count=2, other_count=0),
            TimeseriesPoint(timestamp="2024-01-04", count=2, violent_count=1, property_count=1, other_count=0),
        ]
        
        trend = self.analyzer._calculate_trend(data)
        
        assert trend.direction == "decreasing"
        assert trend.slope < 0

    def test_detect_anomalies_empty(self):
        """Test anomaly detection with insufficient data."""
        data = [
            TimeseriesPoint(timestamp="2024-01-01", count=5, violent_count=2, property_count=2, other_count=1),
        ]
        
        anomalies = self.analyzer._detect_anomalies(data)
        
        assert anomalies == []

    def test_detect_anomalies_with_spike(self):
        """Test anomaly detection finds spikes."""
        data = [
            TimeseriesPoint(timestamp="2024-01-01", count=5, violent_count=2, property_count=2, other_count=1),
            TimeseriesPoint(timestamp="2024-01-02", count=5, violent_count=2, property_count=2, other_count=1),
            TimeseriesPoint(timestamp="2024-01-03", count=5, violent_count=2, property_count=2, other_count=1),
            TimeseriesPoint(timestamp="2024-01-04", count=5, violent_count=2, property_count=2, other_count=1),
            TimeseriesPoint(timestamp="2024-01-05", count=20, violent_count=10, property_count=8, other_count=2),  # Spike
        ]
        
        anomalies = self.analyzer._detect_anomalies(data)
        
        assert len(anomalies) >= 1
        assert anomalies[0].actual_count == 20

    def test_find_peak_hour(self):
        """Test finding peak hour."""
        now = datetime.utcnow()
        records = [
            self._create_mock_record(now.replace(hour=14)),
            self._create_mock_record(now.replace(hour=14)),
            self._create_mock_record(now.replace(hour=14)),
            self._create_mock_record(now.replace(hour=10)),
        ]
        
        peak_hour = self.analyzer._find_peak_hour(records)
        
        assert peak_hour == 14

    def test_find_peak_day(self):
        """Test finding peak day of week."""
        now = datetime.utcnow()
        # Create records on specific days
        records = []
        for i in range(7):
            day = now - timedelta(days=i)
            if day.weekday() == 4:  # Friday
                records.extend([
                    self._create_mock_record(day),
                    self._create_mock_record(day),
                    self._create_mock_record(day),
                ])
            else:
                records.append(self._create_mock_record(day))
        
        peak_day = self.analyzer._find_peak_day(records)
        
        assert peak_day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def test_analyze_empty(self):
        """Test analysis with no data."""
        result = self.analyzer.analyze(days=7)
        
        assert isinstance(result, TimeseriesResult)
        assert result.total_incidents == 0

    def test_analyze_with_data(self):
        """Test analysis with data."""
        self.analyzer.ingestor.ingest_json("""[
            {"subcategory": "Assault", "date": "2024-01-15", "time": "14:00:00", "latitude": 26.78, "longitude": -80.07, "type": "violent"},
            {"subcategory": "Theft", "date": "2024-01-15", "time": "10:00:00", "latitude": 26.79, "longitude": -80.08, "type": "property"}
        ]""")
        
        result = self.analyzer.analyze(days=30)
        
        assert isinstance(result, TimeseriesResult)
        assert result.total_incidents == 2

    def test_get_timeseries_analyzer_singleton(self):
        """Test global analyzer singleton."""
        analyzer1 = get_timeseries_analyzer()
        analyzer2 = get_timeseries_analyzer()
        
        assert analyzer1 is analyzer2

    def _create_mock_record(
        self,
        dt: datetime = None,
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
            latitude=26.78,
            longitude=-80.07,
            sector="Test Sector",
            priority=CrimePriority.MEDIUM,
            source="test",
        )
