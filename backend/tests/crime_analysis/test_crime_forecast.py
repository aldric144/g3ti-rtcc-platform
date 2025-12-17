"""Tests for Crime Forecast Engine Module."""

import pytest
from datetime import datetime, timedelta
from app.crime_analysis.crime_forecast import (
    CrimeForecastEngine,
    HourlyForecast,
    DailyForecast,
    SeasonalPattern,
    PatrolRecommendation,
    ForecastResult,
    get_forecast_engine,
)
from app.crime_analysis.crime_ingest import (
    NormalizedCrimeRecord,
    CrimeType,
    CrimePriority,
)


class TestCrimeForecastEngine:
    """Test suite for CrimeForecastEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = CrimeForecastEngine()
        self.engine.ingestor.clear_records()

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert len(self.engine.DAY_NAMES) == 7
        assert "critical" in self.engine.RISK_THRESHOLDS
        assert "high" in self.engine.RISK_THRESHOLDS

    def test_calculate_hourly_averages_empty(self):
        """Test hourly averages with no records."""
        result = self.engine._calculate_hourly_averages([])
        
        assert len(result) == 24
        for hour in range(24):
            assert result[hour]["average"] == 0

    def test_calculate_hourly_averages_with_records(self):
        """Test hourly averages with records."""
        now = datetime.utcnow()
        records = [
            self._create_mock_record(now.replace(hour=14)),
            self._create_mock_record(now.replace(hour=14)),
            self._create_mock_record(now.replace(hour=10)),
        ]
        
        result = self.engine._calculate_hourly_averages(records)
        
        # Hour 14 should have higher average
        assert result[14]["average"] >= result[10]["average"]

    def test_calculate_daily_averages_empty(self):
        """Test daily averages with no records."""
        result = self.engine._calculate_daily_averages([])
        
        assert len(result) == 7
        for day in range(7):
            assert result[day]["average"] == 0

    def test_get_risk_level_critical(self):
        """Test risk level classification for critical."""
        assert self.engine._get_risk_level(15) == "critical"

    def test_get_risk_level_high(self):
        """Test risk level classification for high."""
        assert self.engine._get_risk_level(7) == "high"

    def test_get_risk_level_medium(self):
        """Test risk level classification for medium."""
        assert self.engine._get_risk_level(4) == "medium"

    def test_get_risk_level_low(self):
        """Test risk level classification for low."""
        assert self.engine._get_risk_level(1) == "low"

    def test_generate_hourly_forecast(self):
        """Test hourly forecast generation."""
        hourly_averages = {h: {"average": 2.0, "std": 0.5} for h in range(24)}
        
        forecast = self.engine._generate_hourly_forecast(hourly_averages, hours_ahead=24)
        
        assert len(forecast) == 24
        assert all(isinstance(f, HourlyForecast) for f in forecast)

    def test_generate_daily_forecast(self):
        """Test daily forecast generation."""
        daily_averages = {
            d: {"average": 5.0, "std": 1.0, "violent_avg": 1.0, "property_avg": 2.0}
            for d in range(7)
        }
        
        forecast = self.engine._generate_daily_forecast(daily_averages, days_ahead=7)
        
        assert len(forecast) == 7
        assert all(isinstance(f, DailyForecast) for f in forecast)

    def test_identify_seasonal_patterns(self):
        """Test seasonal pattern identification."""
        records = [self._create_mock_record() for _ in range(10)]
        hourly_averages = {h: {"average": float(h % 5), "std": 0.5} for h in range(24)}
        daily_averages = {d: {"average": float(d % 3), "std": 0.5} for d in range(7)}
        
        patterns = self.engine._identify_seasonal_patterns(records, hourly_averages, daily_averages)
        
        assert len(patterns) >= 2  # Hourly and weekly patterns
        assert all(isinstance(p, SeasonalPattern) for p in patterns)

    def test_generate_patrol_recommendations_empty(self):
        """Test patrol recommendations with no data."""
        hourly_forecast = [
            HourlyForecast(
                hour=h, date="2024-01-15", predicted_count=2.0,
                confidence_low=1.0, confidence_high=3.0, risk_level="low"
            )
            for h in range(24)
        ]
        
        recommendations = self.engine._generate_patrol_recommendations([], hourly_forecast)
        
        assert recommendations == []

    def test_generate_patrol_recommendations_with_data(self):
        """Test patrol recommendations with data."""
        records = [
            self._create_mock_record(sector="Sector 1", crime_type=CrimeType.VIOLENT)
            for _ in range(10)
        ]
        hourly_forecast = [
            HourlyForecast(
                hour=h, date="2024-01-15", predicted_count=5.0,
                confidence_low=3.0, confidence_high=7.0, risk_level="high"
            )
            for h in range(24)
        ]
        
        recommendations = self.engine._generate_patrol_recommendations(records, hourly_forecast)
        
        assert len(recommendations) >= 1
        assert all(isinstance(r, PatrolRecommendation) for r in recommendations)

    def test_forecast_empty(self):
        """Test forecast with no data."""
        result = self.engine.forecast()
        
        assert isinstance(result, ForecastResult)
        assert len(result.hourly_forecast) == 24
        assert len(result.daily_forecast) == 7

    def test_forecast_with_data(self):
        """Test forecast with data."""
        self.engine.ingestor.ingest_json("""[
            {"subcategory": "Assault", "date": "2024-01-15", "time": "14:00:00", "latitude": 26.78, "longitude": -80.07, "type": "violent", "sector": "Sector 1"},
            {"subcategory": "Theft", "date": "2024-01-15", "time": "10:00:00", "latitude": 26.79, "longitude": -80.08, "type": "property", "sector": "Sector 2"}
        ]""")
        
        result = self.engine.forecast(hours_ahead=48, days_ahead=7)
        
        assert isinstance(result, ForecastResult)
        assert len(result.hourly_forecast) == 48
        assert len(result.daily_forecast) == 7

    def test_get_forecast_engine_singleton(self):
        """Test global engine singleton."""
        engine1 = get_forecast_engine()
        engine2 = get_forecast_engine()
        
        assert engine1 is engine2

    def _create_mock_record(
        self,
        dt: datetime = None,
        sector: str = "Test Sector",
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
            sector=sector,
            priority=CrimePriority.MEDIUM,
            source="test",
        )
