"""
Tests for Historical Analytics module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.analytics.historical import (
    HistoricalAnalyticsEngine,
    TrendAnalysis,
    ComparisonResult,
)


class TestTrendAnalysis:
    """Tests for TrendAnalysis model."""

    def test_create_trend_analysis(self):
        """Test creating a trend analysis."""
        trend = TrendAnalysis(
            jurisdiction="ATL",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            granularity="monthly",
            total_incidents=50000,
            trend_direction="increasing",
            trend_strength=0.75,
            percent_change=15.5,
        )

        assert trend.jurisdiction == "ATL"
        assert trend.trend_direction == "increasing"
        assert trend.trend_strength == 0.75
        assert trend.percent_change == 15.5

    def test_trend_with_breakdown(self):
        """Test trend analysis with category breakdown."""
        trend = TrendAnalysis(
            jurisdiction="ATL",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            granularity="monthly",
            total_incidents=50000,
            trend_direction="stable",
            trend_strength=0.1,
            percent_change=2.0,
            by_category={
                "property": {"count": 25000, "change": -5.0},
                "violent": {"count": 10000, "change": 8.0},
                "drug": {"count": 15000, "change": 3.0},
            },
        )

        assert trend.by_category["property"]["count"] == 25000
        assert trend.by_category["violent"]["change"] == 8.0


class TestComparisonResult:
    """Tests for ComparisonResult model."""

    def test_create_comparison(self):
        """Test creating a comparison result."""
        comparison = ComparisonResult(
            jurisdiction="ATL",
            period1_start=datetime(2023, 1, 1),
            period1_end=datetime(2023, 12, 31),
            period2_start=datetime(2024, 1, 1),
            period2_end=datetime(2024, 12, 31),
            period1_total=45000,
            period2_total=50000,
            absolute_change=5000,
            percent_change=11.1,
        )

        assert comparison.period1_total == 45000
        assert comparison.period2_total == 50000
        assert comparison.absolute_change == 5000

    def test_comparison_with_categories(self):
        """Test comparison with category breakdown."""
        comparison = ComparisonResult(
            jurisdiction="ATL",
            period1_start=datetime(2023, 1, 1),
            period1_end=datetime(2023, 12, 31),
            period2_start=datetime(2024, 1, 1),
            period2_end=datetime(2024, 12, 31),
            period1_total=45000,
            period2_total=50000,
            absolute_change=5000,
            percent_change=11.1,
            by_category={
                "property": {
                    "period1": 22000,
                    "period2": 25000,
                    "change": 13.6,
                },
                "violent": {
                    "period1": 9000,
                    "period2": 10000,
                    "change": 11.1,
                },
            },
        )

        assert comparison.by_category["property"]["change"] == 13.6


class TestHistoricalAnalyticsEngine:
    """Tests for HistoricalAnalyticsEngine class."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = HistoricalAnalyticsEngine()

        assert engine is not None

    @pytest.mark.asyncio
    async def test_analyze_trends(self):
        """Test trend analysis."""
        engine = HistoricalAnalyticsEngine()

        # Mock the data source
        engine._fetch_incident_data = AsyncMock(return_value=[
            {"timestamp": datetime(2024, 1, 15), "crime_category": "property"},
            {"timestamp": datetime(2024, 2, 15), "crime_category": "property"},
            {"timestamp": datetime(2024, 3, 15), "crime_category": "violent"},
            {"timestamp": datetime(2024, 4, 15), "crime_category": "property"},
            {"timestamp": datetime(2024, 5, 15), "crime_category": "drug"},
        ])

        result = await engine.analyze_trends(
            jurisdiction="ATL",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 6, 30),
            granularity="monthly",
        )

        assert result.jurisdiction == "ATL"
        assert result.total_incidents == 5

    @pytest.mark.asyncio
    async def test_compare_periods(self):
        """Test period comparison."""
        engine = HistoricalAnalyticsEngine()

        # Mock the data source
        engine._fetch_incident_data = AsyncMock(side_effect=[
            [{"id": i} for i in range(100)],  # Period 1
            [{"id": i} for i in range(120)],  # Period 2
        ])

        result = await engine.compare_periods(
            jurisdiction="ATL",
            period1_start=datetime(2023, 1, 1),
            period1_end=datetime(2023, 12, 31),
            period2_start=datetime(2024, 1, 1),
            period2_end=datetime(2024, 12, 31),
        )

        assert result.period1_total == 100
        assert result.period2_total == 120
        assert result.absolute_change == 20

    @pytest.mark.asyncio
    async def test_year_over_year_analysis(self):
        """Test year-over-year analysis."""
        engine = HistoricalAnalyticsEngine()

        # Mock the data source
        engine._fetch_yearly_aggregates = AsyncMock(return_value={
            2020: 40000,
            2021: 42000,
            2022: 45000,
            2023: 48000,
            2024: 50000,
        })

        result = await engine.year_over_year_analysis(
            jurisdiction="ATL",
            years=[2020, 2021, 2022, 2023, 2024],
        )

        assert len(result) == 5
        assert result[2024] == 50000

    @pytest.mark.asyncio
    async def test_seasonal_analysis(self):
        """Test seasonal pattern analysis."""
        engine = HistoricalAnalyticsEngine()

        # Mock the data source
        engine._fetch_monthly_aggregates = AsyncMock(return_value={
            1: 4000, 2: 3800, 3: 4200, 4: 4500,
            5: 5000, 6: 5500, 7: 6000, 8: 5800,
            9: 5200, 10: 4800, 11: 4200, 12: 4000,
        })

        result = await engine.seasonal_analysis(
            jurisdiction="ATL",
            years=[2023, 2024],
        )

        assert result["peak_month"] == 7  # July
        assert result["low_month"] == 2   # February

    def test_calculate_trend_direction(self):
        """Test trend direction calculation."""
        engine = HistoricalAnalyticsEngine()

        # Increasing trend
        data_points = [100, 110, 120, 130, 140]
        direction, strength = engine._calculate_trend(data_points)
        assert direction == "increasing"
        assert strength > 0.5

        # Decreasing trend
        data_points = [140, 130, 120, 110, 100]
        direction, strength = engine._calculate_trend(data_points)
        assert direction == "decreasing"
        assert strength > 0.5

        # Stable trend
        data_points = [100, 101, 99, 100, 101]
        direction, strength = engine._calculate_trend(data_points)
        assert direction == "stable"

    def test_calculate_percent_change(self):
        """Test percent change calculation."""
        engine = HistoricalAnalyticsEngine()

        # Positive change
        change = engine._calculate_percent_change(100, 120)
        assert change == 20.0

        # Negative change
        change = engine._calculate_percent_change(100, 80)
        assert change == -20.0

        # No change
        change = engine._calculate_percent_change(100, 100)
        assert change == 0.0

        # Zero baseline
        change = engine._calculate_percent_change(0, 100)
        assert change == 100.0  # Or handle as special case

    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        engine = HistoricalAnalyticsEngine()

        # High data availability
        score = engine._calculate_confidence(
            data_points=1000,
            time_span_days=365,
            missing_periods=0,
        )
        assert score > 0.8

        # Low data availability
        score = engine._calculate_confidence(
            data_points=10,
            time_span_days=365,
            missing_periods=6,
        )
        assert score < 0.5

    @pytest.mark.asyncio
    async def test_get_statistical_summary(self):
        """Test statistical summary generation."""
        engine = HistoricalAnalyticsEngine()

        data = [100, 120, 110, 130, 125, 115, 140, 135, 145, 150]

        summary = engine._get_statistical_summary(data)

        assert "mean" in summary
        assert "median" in summary
        assert "std_dev" in summary
        assert "min" in summary
        assert "max" in summary
        assert summary["min"] == 100
        assert summary["max"] == 150
