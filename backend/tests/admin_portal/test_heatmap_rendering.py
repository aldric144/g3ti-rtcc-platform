"""
Test Suite 4: Heatmap Rendering Tests

Tests for heatmap data generation and visualization support.
"""

import pytest
import math

from app.patrol_insights.heatmap_engine import (
    HeatmapEngine,
    PatrolZone,
    GeoPoint,
    ZoneType,
    HeatmapData,
    SectorScore,
    PatrolStatus,
)


@pytest.fixture
def heatmap_engine():
    """Create a fresh heatmap engine for each test."""
    return HeatmapEngine()


def test_heatmap_data_structure(heatmap_engine):
    """Test that heatmap data has correct structure."""
    heatmap = heatmap_engine.generate_heatmap()
    
    assert isinstance(heatmap, HeatmapData)
    assert isinstance(heatmap.zones, list)
    assert isinstance(heatmap.sector_scores, list)
    assert isinstance(heatmap.overall_balance, float)
    assert heatmap.generated_at is not None


def test_sector_scores_structure(heatmap_engine):
    """Test that sector scores have correct structure."""
    scores = heatmap_engine.calculate_sector_scores()
    
    for score in scores:
        assert isinstance(score, SectorScore)
        assert score.sector_id is not None
        assert score.sector_name is not None
        assert 0 <= score.patrol_intensity <= 1
        assert score.status in [s for s in PatrolStatus]
        assert isinstance(score.hourly_visits, int)
        assert isinstance(score.daily_visits, int)
        assert isinstance(score.flags, list)


def test_all_sectors_included(heatmap_engine):
    """Test that all defined sectors are included in scores."""
    scores = heatmap_engine.calculate_sector_scores()
    sector_ids = {score.sector_id for score in scores}
    
    for sector in heatmap_engine.SECTORS:
        assert sector["id"] in sector_ids


def test_zone_visibility_in_heatmap(heatmap_engine):
    """Test that added zones appear in heatmap data."""
    zone = PatrolZone(
        zone_type=ZoneType.HOTSPOT,
        name="Test Hotspot",
        center=GeoPoint(lat=26.7754, lng=-80.0583),
        created_by="admin",
    )
    heatmap_engine.add_zone(zone)
    
    heatmap = heatmap_engine.generate_heatmap()
    
    assert len(heatmap.zones) == 1
    assert heatmap.zones[0].name == "Test Hotspot"


def test_inactive_zones_excluded(heatmap_engine):
    """Test that inactive zones are excluded from heatmap."""
    zone = PatrolZone(
        zone_type=ZoneType.HOTSPOT,
        name="Inactive Zone",
        center=GeoPoint(lat=26.7754, lng=-80.0583),
        created_by="admin",
        is_active=False,
    )
    heatmap_engine.add_zone(zone)
    
    heatmap = heatmap_engine.generate_heatmap()
    
    assert len(heatmap.zones) == 0


def test_overall_balance_calculation(heatmap_engine):
    """Test overall balance calculation."""
    heatmap = heatmap_engine.generate_heatmap()
    
    # Balance should be between 0 and 1
    assert 0 <= heatmap.overall_balance <= 1


def test_time_range_parameter(heatmap_engine):
    """Test that time range parameter is respected."""
    heatmap_1h = heatmap_engine.generate_heatmap(time_range_hours=1)
    heatmap_24h = heatmap_engine.generate_heatmap(time_range_hours=24)
    
    assert heatmap_1h.time_range_hours == 1
    assert heatmap_24h.time_range_hours == 24


def test_distance_calculation(heatmap_engine):
    """Test distance calculation between points."""
    p1 = GeoPoint(lat=26.7754, lng=-80.0583)
    p2 = {"lat": 26.7854, "lng": -80.0583}  # ~1.1km north
    
    distance = heatmap_engine._calculate_distance(p1, p2)
    
    # Should be approximately 1100 meters
    assert 1000 < distance < 1200


def test_sector_flags_generation(heatmap_engine):
    """Test that sector flags are generated based on zones."""
    # Add a high-calls zone
    zone = PatrolZone(
        zone_type=ZoneType.HIGH_CALLS,
        name="High Calls Area",
        center=GeoPoint(lat=26.7754, lng=-80.0583),  # Downtown/Marina
        created_by="admin",
    )
    heatmap_engine.add_zone(zone)
    
    scores = heatmap_engine.calculate_sector_scores()
    
    # At least one sector should have a flag about the high-calls zone
    all_flags = []
    for score in scores:
        all_flags.extend(score.flags)
    
    assert any("High-calls zone" in flag for flag in all_flags)


def test_patrol_status_assignment(heatmap_engine):
    """Test that patrol status is correctly assigned based on intensity."""
    scores = heatmap_engine.calculate_sector_scores()
    
    for score in scores:
        if score.patrol_intensity > 0.8:
            assert score.status == PatrolStatus.OVER_POLICED
        elif score.patrol_intensity < 0.2:
            assert score.status == PatrolStatus.UNDER_POLICED
        elif 0.4 <= score.patrol_intensity <= 0.6:
            assert score.status == PatrolStatus.BALANCED
