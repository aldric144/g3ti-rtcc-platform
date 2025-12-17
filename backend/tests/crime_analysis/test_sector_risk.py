"""Tests for Sector Risk Analysis Module."""

import pytest
from datetime import datetime, timedelta
from app.crime_analysis.sector_risk_analysis import (
    SectorRiskAnalyzer,
    RiskFactor,
    SectorRiskScore,
    SectorComparisonResult,
    get_risk_analyzer,
)
from app.crime_analysis.crime_ingest import (
    NormalizedCrimeRecord,
    CrimeType,
    CrimePriority,
)


class TestSectorRiskAnalyzer:
    """Test suite for SectorRiskAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SectorRiskAnalyzer()
        self.analyzer.ingestor.clear_records()

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        assert "violent_crime" in self.analyzer.FACTOR_WEIGHTS
        assert "property_crime" in self.analyzer.FACTOR_WEIGHTS
        assert "gunfire" in self.analyzer.FACTOR_WEIGHTS
        assert "critical" in self.analyzer.RISK_LEVELS

    def test_count_violent_crimes(self):
        """Test counting violent crimes."""
        records = [
            self._create_mock_record(crime_type=CrimeType.VIOLENT),
            self._create_mock_record(crime_type=CrimeType.VIOLENT),
            self._create_mock_record(crime_type=CrimeType.PROPERTY),
        ]
        
        count = self.analyzer._count_violent_crimes(records)
        
        assert count == 2

    def test_count_property_crimes(self):
        """Test counting property crimes."""
        records = [
            self._create_mock_record(crime_type=CrimeType.VIOLENT),
            self._create_mock_record(crime_type=CrimeType.PROPERTY),
            self._create_mock_record(crime_type=CrimeType.PROPERTY),
        ]
        
        count = self.analyzer._count_property_crimes(records)
        
        assert count == 2

    def test_count_gunfire(self):
        """Test counting gunfire incidents."""
        records = [
            self._create_mock_record(subcategory="Shooting incident"),
            self._create_mock_record(subcategory="Gunshot detected"),
            self._create_mock_record(subcategory="Theft"),
        ]
        
        count = self.analyzer._count_gunfire(records)
        
        assert count == 2

    def test_count_domestic_violence(self):
        """Test counting domestic violence incidents."""
        records = [
            self._create_mock_record(domestic_flag=True),
            self._create_mock_record(domestic_flag=True),
            self._create_mock_record(domestic_flag=False),
        ]
        
        count = self.analyzer._count_domestic_violence(records)
        
        assert count == 2

    def test_count_repeat_locations(self):
        """Test counting repeat locations."""
        records = [
            self._create_mock_record(lat=26.7800, lng=-80.0700),
            self._create_mock_record(lat=26.7800, lng=-80.0700),  # Same location
            self._create_mock_record(lat=26.7900, lng=-80.0800),  # Different location
        ]
        
        count = self.analyzer._count_repeat_locations(records)
        
        assert count >= 1

    def test_calculate_trend_stable(self):
        """Test trend calculation for stable crime."""
        now = datetime.utcnow()
        records = [
            self._create_mock_record(dt=now - timedelta(days=5)),
            self._create_mock_record(dt=now - timedelta(days=20)),
        ]
        
        trend = self.analyzer._calculate_trend(records, days=30)
        
        assert trend in ["increasing", "decreasing", "stable"]

    def test_get_risk_level_critical(self):
        """Test risk level for critical score."""
        assert self.analyzer._get_risk_level(4.8) == "critical"

    def test_get_risk_level_high(self):
        """Test risk level for high score."""
        assert self.analyzer._get_risk_level(4.0) == "high"

    def test_get_risk_level_elevated(self):
        """Test risk level for elevated score."""
        assert self.analyzer._get_risk_level(3.0) == "elevated"

    def test_get_risk_level_moderate(self):
        """Test risk level for moderate score."""
        assert self.analyzer._get_risk_level(2.0) == "moderate"

    def test_get_risk_level_low(self):
        """Test risk level for low score."""
        assert self.analyzer._get_risk_level(1.0) == "low"

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        risk_factors = [
            RiskFactor(factor_name="violent_crime", count=10, weight=3.0, contribution=30.0, trend="increasing"),
            RiskFactor(factor_name="gunfire", count=5, weight=4.0, contribution=20.0, trend="stable"),
        ]
        
        recommendations = self.analyzer._generate_recommendations(risk_factors, 4.0)
        
        assert len(recommendations) >= 1
        assert any("patrol" in r.lower() for r in recommendations)

    def test_analyze_sector_empty(self):
        """Test sector analysis with no data."""
        result = self.analyzer.analyze_sector("Test Sector")
        
        assert isinstance(result, SectorRiskScore)
        assert result.sector == "Test Sector"
        assert result.total_incidents == 0

    def test_analyze_sector_with_data(self):
        """Test sector analysis with data."""
        self.analyzer.ingestor.ingest_json("""[
            {"subcategory": "Assault", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07, "type": "violent", "sector": "Sector 1"},
            {"subcategory": "Theft", "date": "2024-01-15", "latitude": 26.79, "longitude": -80.08, "type": "property", "sector": "Sector 1"}
        ]""")
        
        result = self.analyzer.analyze_sector("Sector 1", days=30)
        
        assert isinstance(result, SectorRiskScore)
        assert result.sector == "Sector 1"
        assert result.total_incidents == 2

    def test_analyze_all_sectors_empty(self):
        """Test all sectors analysis with no data."""
        result = self.analyzer.analyze_all_sectors()
        
        assert isinstance(result, SectorComparisonResult)
        assert result.sectors == []

    def test_analyze_all_sectors_with_data(self):
        """Test all sectors analysis with data."""
        self.analyzer.ingestor.ingest_json("""[
            {"subcategory": "Assault", "date": "2024-01-15", "latitude": 26.78, "longitude": -80.07, "type": "violent", "sector": "Sector 1"},
            {"subcategory": "Theft", "date": "2024-01-15", "latitude": 26.79, "longitude": -80.08, "type": "property", "sector": "Sector 2"}
        ]""")
        
        result = self.analyzer.analyze_all_sectors(days=30)
        
        assert isinstance(result, SectorComparisonResult)
        assert len(result.sectors) == 2

    def test_get_risk_analyzer_singleton(self):
        """Test global analyzer singleton."""
        analyzer1 = get_risk_analyzer()
        analyzer2 = get_risk_analyzer()
        
        assert analyzer1 is analyzer2

    def _create_mock_record(
        self,
        dt: datetime = None,
        lat: float = 26.78,
        lng: float = -80.07,
        crime_type: CrimeType = CrimeType.VIOLENT,
        subcategory: str = "Test Crime",
        domestic_flag: bool = False,
    ) -> NormalizedCrimeRecord:
        """Create a mock crime record for testing."""
        if dt is None:
            dt = datetime.utcnow()
        
        return NormalizedCrimeRecord(
            id=f"test-{dt.timestamp()}-{lat}-{lng}",
            type=crime_type,
            subcategory=subcategory,
            time=dt.strftime("%H:%M:%S"),
            date=dt.strftime("%Y-%m-%d"),
            datetime_utc=dt,
            latitude=lat,
            longitude=lng,
            sector="Test Sector",
            priority=CrimePriority.MEDIUM,
            domestic_flag=domestic_flag,
            source="test",
        )
