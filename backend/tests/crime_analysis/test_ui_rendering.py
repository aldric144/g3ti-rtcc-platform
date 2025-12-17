"""Tests for Crime Analysis UI Data Rendering."""

import pytest
from datetime import datetime
from app.crime_analysis.crime_heatmap_engine import HeatmapPoint, HotspotCluster, HeatmapResult
from app.crime_analysis.crime_timeseries import TimeseriesPoint, TrendInfo, AnomalyAlert, TimeseriesResult
from app.crime_analysis.crime_forecast import HourlyForecast, DailyForecast, SeasonalPattern, PatrolRecommendation, ForecastResult
from app.crime_analysis.sector_risk_analysis import RiskFactor, SectorRiskScore, SectorComparisonResult
from app.crime_analysis.repeat_location_detector import RepeatLocation, LocationCluster, RepeatLocationResult


class TestHeatmapUIData:
    """Test suite for heatmap UI data structures."""

    def test_heatmap_point_serialization(self):
        """Test HeatmapPoint can be serialized for UI."""
        point = HeatmapPoint(
            latitude=26.78,
            longitude=-80.07,
            intensity=5.5,
            weight=1.0,
        )
        
        data = point.model_dump()
        
        assert "latitude" in data
        assert "longitude" in data
        assert "intensity" in data
        assert data["intensity"] == 5.5

    def test_hotspot_cluster_serialization(self):
        """Test HotspotCluster can be serialized for UI."""
        cluster = HotspotCluster(
            cluster_id=1,
            center_lat=26.78,
            center_lng=-80.07,
            radius_meters=500.0,
            incident_count=10,
            crime_types=["violent", "property"],
            severity_score=3.5,
            top_crimes=["Assault", "Theft"],
        )
        
        data = cluster.model_dump()
        
        assert "cluster_id" in data
        assert "center_lat" in data
        assert "severity_score" in data
        assert len(data["crime_types"]) == 2

    def test_heatmap_result_serialization(self):
        """Test HeatmapResult can be serialized for UI."""
        result = HeatmapResult(
            points=[],
            hotspots=[],
            time_range="7d",
            start_date="2024-01-01",
            end_date="2024-01-07",
            total_incidents=100,
            bounds={"north": 26.82, "south": 26.75, "east": -80.03, "west": -80.12},
        )
        
        data = result.model_dump()
        
        assert "points" in data
        assert "hotspots" in data
        assert "bounds" in data
        assert data["total_incidents"] == 100


class TestTimeseriesUIData:
    """Test suite for timeseries UI data structures."""

    def test_timeseries_point_serialization(self):
        """Test TimeseriesPoint can be serialized for UI."""
        point = TimeseriesPoint(
            timestamp="2024-01-15",
            count=10,
            violent_count=3,
            property_count=5,
            other_count=2,
        )
        
        data = point.model_dump()
        
        assert "timestamp" in data
        assert "count" in data
        assert data["violent_count"] == 3

    def test_trend_info_serialization(self):
        """Test TrendInfo can be serialized for UI."""
        trend = TrendInfo(
            direction="increasing",
            slope=0.5,
            change_percent=15.0,
            confidence=0.85,
        )
        
        data = trend.model_dump()
        
        assert data["direction"] == "increasing"
        assert data["confidence"] == 0.85

    def test_anomaly_alert_serialization(self):
        """Test AnomalyAlert can be serialized for UI."""
        anomaly = AnomalyAlert(
            timestamp="2024-01-15 14:00",
            expected_count=5.0,
            actual_count=15,
            deviation=3.5,
            severity="high",
            description="Unusual spike in crime activity",
        )
        
        data = anomaly.model_dump()
        
        assert data["severity"] == "high"
        assert data["actual_count"] == 15


class TestForecastUIData:
    """Test suite for forecast UI data structures."""

    def test_hourly_forecast_serialization(self):
        """Test HourlyForecast can be serialized for UI."""
        forecast = HourlyForecast(
            hour=14,
            date="2024-01-15",
            predicted_count=5.5,
            confidence_low=3.0,
            confidence_high=8.0,
            risk_level="medium",
        )
        
        data = forecast.model_dump()
        
        assert data["hour"] == 14
        assert data["risk_level"] == "medium"

    def test_daily_forecast_serialization(self):
        """Test DailyForecast can be serialized for UI."""
        forecast = DailyForecast(
            date="2024-01-15",
            day_of_week="Monday",
            predicted_count=25.0,
            confidence_low=20.0,
            confidence_high=30.0,
            risk_level="high",
            violent_predicted=8.0,
            property_predicted=12.0,
        )
        
        data = forecast.model_dump()
        
        assert data["day_of_week"] == "Monday"
        assert data["violent_predicted"] == 8.0

    def test_seasonal_pattern_serialization(self):
        """Test SeasonalPattern can be serialized for UI."""
        pattern = SeasonalPattern(
            pattern_type="hourly",
            description="Crime peaks during evening hours",
            peak_periods=["18:00-22:00"],
            low_periods=["06:00-10:00"],
            strength=0.75,
        )
        
        data = pattern.model_dump()
        
        assert data["pattern_type"] == "hourly"
        assert data["strength"] == 0.75

    def test_patrol_recommendation_serialization(self):
        """Test PatrolRecommendation can be serialized for UI."""
        rec = PatrolRecommendation(
            sector="Sector 1",
            start_time="18:00",
            end_time="02:00",
            priority="high",
            reason="High violent crime rate during evening hours",
            expected_incidents=8,
            recommended_units=3,
        )
        
        data = rec.model_dump()
        
        assert data["sector"] == "Sector 1"
        assert data["recommended_units"] == 3


class TestSectorRiskUIData:
    """Test suite for sector risk UI data structures."""

    def test_risk_factor_serialization(self):
        """Test RiskFactor can be serialized for UI."""
        factor = RiskFactor(
            factor_name="violent_crime",
            count=15,
            weight=3.0,
            contribution=45.0,
            trend="increasing",
        )
        
        data = factor.model_dump()
        
        assert data["factor_name"] == "violent_crime"
        assert data["contribution"] == 45.0

    def test_sector_risk_score_serialization(self):
        """Test SectorRiskScore can be serialized for UI."""
        score = SectorRiskScore(
            sector="Sector 1",
            risk_score=4.2,
            risk_level="high",
            total_incidents=50,
            risk_factors=[],
            recommendations=["Increase patrol presence"],
            trend="increasing",
            analysis_period="30 days",
        )
        
        data = score.model_dump()
        
        assert data["risk_score"] == 4.2
        assert data["risk_level"] == "high"


class TestRepeatLocationUIData:
    """Test suite for repeat location UI data structures."""

    def test_repeat_location_serialization(self):
        """Test RepeatLocation can be serialized for UI."""
        location = RepeatLocation(
            location_id="loc-001",
            latitude=26.78,
            longitude=-80.07,
            address="123 Main St",
            incident_count=8,
            first_incident="2024-01-01T00:00:00",
            last_incident="2024-01-15T00:00:00",
            crime_types=["violent", "property"],
            severity_score=3.5,
            is_business=False,
            sector="Sector 1",
            incidents=[],
        )
        
        data = location.model_dump()
        
        assert data["location_id"] == "loc-001"
        assert data["incident_count"] == 8
        assert data["is_business"] is False

    def test_location_cluster_serialization(self):
        """Test LocationCluster can be serialized for UI."""
        cluster = LocationCluster(
            cluster_id="cluster-001",
            center_lat=26.78,
            center_lng=-80.07,
            radius_meters=250.0,
            total_incidents=25,
            location_count=5,
            sector="Sector 1",
        )
        
        data = cluster.model_dump()
        
        assert data["cluster_id"] == "cluster-001"
        assert data["location_count"] == 5


class TestUIDataValidation:
    """Test suite for UI data validation."""

    def test_risk_level_values(self):
        """Test valid risk level values for UI."""
        valid_levels = ["critical", "high", "elevated", "moderate", "low"]
        
        for level in valid_levels:
            score = SectorRiskScore(
                sector="Test",
                risk_score=3.0,
                risk_level=level,
                total_incidents=10,
                risk_factors=[],
                recommendations=[],
                trend="stable",
                analysis_period="30 days",
            )
            assert score.risk_level == level

    def test_trend_direction_values(self):
        """Test valid trend direction values for UI."""
        valid_directions = ["increasing", "decreasing", "stable"]
        
        for direction in valid_directions:
            trend = TrendInfo(
                direction=direction,
                slope=0.0,
                change_percent=0.0,
                confidence=0.5,
            )
            assert trend.direction == direction

    def test_severity_values(self):
        """Test valid severity values for UI."""
        valid_severities = ["critical", "high", "medium", "low"]
        
        for severity in valid_severities:
            anomaly = AnomalyAlert(
                timestamp="2024-01-15",
                expected_count=5.0,
                actual_count=10,
                deviation=2.0,
                severity=severity,
                description="Test",
            )
            assert anomaly.severity == severity

    def test_coordinate_precision_for_ui(self):
        """Test coordinate precision is suitable for UI display."""
        point = HeatmapPoint(
            latitude=26.78456789,
            longitude=-80.07123456,
            intensity=5.0,
            weight=1.0,
        )
        
        # Coordinates should be preserved with full precision
        assert point.latitude == 26.78456789
        assert point.longitude == -80.07123456

    def test_percentage_values_for_ui(self):
        """Test percentage values are in correct range for UI."""
        trend = TrendInfo(
            direction="increasing",
            slope=0.5,
            change_percent=150.0,  # Can exceed 100%
            confidence=0.95,  # Should be 0-1
        )
        
        assert 0 <= trend.confidence <= 1
        # change_percent can be any value
