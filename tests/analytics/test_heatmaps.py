"""
Tests for Multi-Year Heatmap module.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.analytics.heatmaps import (
    MultiYearHeatmapEngine,
    HeatmapCell,
    HeatmapData,
    HotspotEvolution,
    HeatmapComparison,
)


class TestHeatmapCell:
    """Tests for HeatmapCell model."""

    def test_create_cell(self):
        """Test creating a heatmap cell."""
        cell = HeatmapCell(
            h3_index="8828308280fffff",
            latitude=33.749,
            longitude=-84.388,
            count=150,
            intensity=0.85,
        )

        assert cell.h3_index == "8828308280fffff"
        assert cell.count == 150
        assert cell.intensity == 0.85

    def test_cell_with_metadata(self):
        """Test cell with additional metadata."""
        cell = HeatmapCell(
            h3_index="8828308280fffff",
            latitude=33.749,
            longitude=-84.388,
            count=150,
            intensity=0.85,
            crime_categories={"property": 80, "violent": 70},
            peak_hour=22,
        )

        assert cell.crime_categories["property"] == 80
        assert cell.peak_hour == 22


class TestHeatmapData:
    """Tests for HeatmapData model."""

    def test_create_heatmap_data(self):
        """Test creating heatmap data."""
        cells = [
            HeatmapCell(
                h3_index="8828308280fffff",
                latitude=33.749,
                longitude=-84.388,
                count=150,
                intensity=0.85,
            ),
            HeatmapCell(
                h3_index="8828308281fffff",
                latitude=33.750,
                longitude=-84.389,
                count=100,
                intensity=0.65,
            ),
        ]

        heatmap = HeatmapData(
            jurisdiction="ATL",
            year=2024,
            resolution=8,
            cells=cells,
            total_incidents=250,
            hotspot_count=2,
        )

        assert heatmap.jurisdiction == "ATL"
        assert heatmap.year == 2024
        assert len(heatmap.cells) == 2
        assert heatmap.total_incidents == 250


class TestHotspotEvolution:
    """Tests for HotspotEvolution model."""

    def test_create_evolution(self):
        """Test creating hotspot evolution."""
        evolution = HotspotEvolution(
            h3_index="8828308280fffff",
            latitude=33.749,
            longitude=-84.388,
            years=[2020, 2021, 2022, 2023, 2024],
            counts=[100, 120, 150, 180, 200],
            trend="increasing",
            growth_rate=0.15,
        )

        assert evolution.h3_index == "8828308280fffff"
        assert evolution.trend == "increasing"
        assert evolution.growth_rate == 0.15
        assert len(evolution.years) == 5

    def test_evolution_with_status(self):
        """Test evolution with status classification."""
        evolution = HotspotEvolution(
            h3_index="8828308280fffff",
            latitude=33.749,
            longitude=-84.388,
            years=[2020, 2021, 2022, 2023, 2024],
            counts=[200, 180, 150, 120, 100],
            trend="decreasing",
            growth_rate=-0.15,
            status="improving",
        )

        assert evolution.trend == "decreasing"
        assert evolution.status == "improving"


class TestHeatmapComparison:
    """Tests for HeatmapComparison model."""

    def test_create_comparison(self):
        """Test creating heatmap comparison."""
        comparison = HeatmapComparison(
            jurisdiction="ATL",
            year1=2023,
            year2=2024,
            resolution=8,
            new_hotspots=5,
            resolved_hotspots=3,
            persistent_hotspots=10,
            intensified_hotspots=4,
            reduced_hotspots=6,
        )

        assert comparison.year1 == 2023
        assert comparison.year2 == 2024
        assert comparison.new_hotspots == 5
        assert comparison.resolved_hotspots == 3


class TestMultiYearHeatmapEngine:
    """Tests for MultiYearHeatmapEngine class."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = MultiYearHeatmapEngine()

        assert engine is not None
        assert engine.default_resolution == 8

    @pytest.mark.asyncio
    async def test_generate_heatmap(self):
        """Test heatmap generation."""
        engine = MultiYearHeatmapEngine()

        # Mock the data source
        engine._fetch_incident_locations = AsyncMock(return_value=[
            {"latitude": 33.749, "longitude": -84.388},
            {"latitude": 33.750, "longitude": -84.389},
            {"latitude": 33.749, "longitude": -84.388},
            {"latitude": 33.751, "longitude": -84.390},
        ])

        result = await engine.generate_heatmap(
            jurisdiction="ATL",
            year=2024,
            resolution=8,
        )

        assert result.jurisdiction == "ATL"
        assert result.year == 2024
        assert result.total_incidents == 4

    @pytest.mark.asyncio
    async def test_generate_yearly_heatmaps(self):
        """Test multi-year heatmap generation."""
        engine = MultiYearHeatmapEngine()

        # Mock the data source
        engine._fetch_incident_locations = AsyncMock(return_value=[
            {"latitude": 33.749, "longitude": -84.388},
            {"latitude": 33.750, "longitude": -84.389},
        ])

        result = await engine.generate_yearly_heatmaps(
            jurisdiction="ATL",
            years=[2022, 2023, 2024],
            resolution=8,
        )

        assert len(result) == 3
        assert 2022 in result
        assert 2023 in result
        assert 2024 in result

    @pytest.mark.asyncio
    async def test_compare_heatmaps(self):
        """Test heatmap comparison."""
        engine = MultiYearHeatmapEngine()

        # Mock heatmap data
        heatmap1 = HeatmapData(
            jurisdiction="ATL",
            year=2023,
            resolution=8,
            cells=[
                HeatmapCell(h3_index="cell1", latitude=33.749, longitude=-84.388, count=100, intensity=0.8),
                HeatmapCell(h3_index="cell2", latitude=33.750, longitude=-84.389, count=80, intensity=0.6),
            ],
            total_incidents=180,
            hotspot_count=2,
        )

        heatmap2 = HeatmapData(
            jurisdiction="ATL",
            year=2024,
            resolution=8,
            cells=[
                HeatmapCell(h3_index="cell1", latitude=33.749, longitude=-84.388, count=120, intensity=0.9),
                HeatmapCell(h3_index="cell3", latitude=33.751, longitude=-84.390, count=90, intensity=0.7),
            ],
            total_incidents=210,
            hotspot_count=2,
        )

        engine.generate_heatmap = AsyncMock(side_effect=[heatmap1, heatmap2])

        result = await engine.compare_heatmaps(
            jurisdiction="ATL",
            year1=2023,
            year2=2024,
            resolution=8,
        )

        assert result.year1 == 2023
        assert result.year2 == 2024
        assert result.new_hotspots >= 0
        assert result.resolved_hotspots >= 0

    @pytest.mark.asyncio
    async def test_track_hotspot_evolution(self):
        """Test hotspot evolution tracking."""
        engine = MultiYearHeatmapEngine()

        # Mock yearly data
        engine._fetch_yearly_cell_data = AsyncMock(return_value={
            "cell1": {2020: 100, 2021: 120, 2022: 150, 2023: 180, 2024: 200},
            "cell2": {2020: 80, 2021: 70, 2022: 60, 2023: 50, 2024: 40},
        })

        result = await engine.track_hotspot_evolution(
            jurisdiction="ATL",
            years=[2020, 2021, 2022, 2023, 2024],
            resolution=8,
        )

        assert len(result) == 2
        assert any(e.trend == "increasing" for e in result)
        assert any(e.trend == "decreasing" for e in result)

    def test_calculate_h3_index(self):
        """Test H3 index calculation."""
        engine = MultiYearHeatmapEngine()

        h3_index = engine._calculate_h3_index(33.749, -84.388, resolution=8)

        assert h3_index is not None
        assert len(h3_index) > 0

    def test_calculate_intensity(self):
        """Test intensity calculation."""
        engine = MultiYearHeatmapEngine()

        # High count relative to max
        intensity = engine._calculate_intensity(count=100, max_count=100)
        assert intensity == 1.0

        # Medium count
        intensity = engine._calculate_intensity(count=50, max_count=100)
        assert intensity == 0.5

        # Low count
        intensity = engine._calculate_intensity(count=10, max_count=100)
        assert intensity == 0.1

    def test_classify_hotspot_trend(self):
        """Test hotspot trend classification."""
        engine = MultiYearHeatmapEngine()

        # Increasing trend
        trend = engine._classify_trend([100, 120, 150, 180, 200])
        assert trend == "increasing"

        # Decreasing trend
        trend = engine._classify_trend([200, 180, 150, 120, 100])
        assert trend == "decreasing"

        # Stable trend
        trend = engine._classify_trend([100, 102, 98, 101, 99])
        assert trend == "stable"

    def test_calculate_growth_rate(self):
        """Test growth rate calculation."""
        engine = MultiYearHeatmapEngine()

        # Positive growth
        rate = engine._calculate_growth_rate([100, 110, 121, 133, 146])
        assert rate > 0

        # Negative growth
        rate = engine._calculate_growth_rate([100, 90, 81, 73, 66])
        assert rate < 0

        # No growth
        rate = engine._calculate_growth_rate([100, 100, 100, 100, 100])
        assert abs(rate) < 0.01

    def test_identify_hotspots(self):
        """Test hotspot identification."""
        engine = MultiYearHeatmapEngine()

        cells = [
            HeatmapCell(h3_index="cell1", latitude=33.749, longitude=-84.388, count=200, intensity=1.0),
            HeatmapCell(h3_index="cell2", latitude=33.750, longitude=-84.389, count=150, intensity=0.75),
            HeatmapCell(h3_index="cell3", latitude=33.751, longitude=-84.390, count=50, intensity=0.25),
            HeatmapCell(h3_index="cell4", latitude=33.752, longitude=-84.391, count=20, intensity=0.1),
        ]

        hotspots = engine._identify_hotspots(cells, threshold=0.5)

        assert len(hotspots) == 2
        assert all(h.intensity >= 0.5 for h in hotspots)
