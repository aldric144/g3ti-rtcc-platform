"""
Test Suite 3: Patrol Insight Calculation Tests

Tests for patrol intensity calculations, sector scoring, and balance metrics.
"""

import pytest
from datetime import datetime, UTC

from app.patrol_insights.heatmap_engine import (
    HeatmapEngine,
    PatrolZone,
    PatrolZoneCreate,
    GeoPoint,
    ZoneType,
    PatrolStatus,
)
from app.patrol_insights.patrol_insights_service import PatrolInsightsService


@pytest.fixture
def patrol_service():
    """Create a fresh patrol insights service for each test."""
    return PatrolInsightsService()


@pytest.fixture
def heatmap_engine():
    """Create a fresh heatmap engine for each test."""
    return HeatmapEngine()


@pytest.mark.asyncio
async def test_create_manual_zone(patrol_service):
    """Test creating a manual patrol zone."""
    data = PatrolZoneCreate(
        zone_type=ZoneType.HOTSPOT,
        name="Test Hotspot",
        description="High activity area",
        center=GeoPoint(lat=26.7754, lng=-80.0583),
        radius_meters=500,
        intensity=0.8,
    )
    
    zone = await patrol_service.create_manual_zone(data, "admin")
    
    assert zone.id is not None
    assert zone.zone_type == ZoneType.HOTSPOT
    assert zone.name == "Test Hotspot"
    assert zone.is_active is True


@pytest.mark.asyncio
async def test_delete_manual_zone(patrol_service):
    """Test deleting a manual patrol zone."""
    data = PatrolZoneCreate(
        zone_type=ZoneType.HIGH_CALLS,
        name="High Calls Zone",
        center=GeoPoint(lat=26.7754, lng=-80.0583),
    )
    zone = await patrol_service.create_manual_zone(data, "admin")
    
    success = await patrol_service.delete_manual_zone(zone.id, "admin")
    assert success is True
    
    deleted_zone = await patrol_service.get_zone(zone.id)
    assert deleted_zone is None


@pytest.mark.asyncio
async def test_get_all_zones(patrol_service):
    """Test retrieving all patrol zones."""
    # Create multiple zones
    for i in range(3):
        data = PatrolZoneCreate(
            zone_type=ZoneType.MANUAL,
            name=f"Zone {i}",
            center=GeoPoint(lat=26.7754 + i * 0.01, lng=-80.0583),
        )
        await patrol_service.create_manual_zone(data, "admin")
    
    zones = await patrol_service.get_all_zones()
    assert len(zones) == 3


@pytest.mark.asyncio
async def test_get_insights(patrol_service):
    """Test getting patrol insights and heatmap data."""
    insights = await patrol_service.get_insights(time_range_hours=24)
    
    assert insights is not None
    assert insights.sector_scores is not None
    assert insights.overall_balance >= 0
    assert insights.overall_balance <= 1
    assert insights.time_range_hours == 24


def test_sector_score_calculation(heatmap_engine):
    """Test sector score calculation."""
    scores = heatmap_engine.calculate_sector_scores()
    
    assert len(scores) == len(heatmap_engine.SECTORS)
    for score in scores:
        assert score.patrol_intensity >= 0
        assert score.patrol_intensity <= 1
        assert score.status in [s for s in PatrolStatus]


def test_heatmap_generation(heatmap_engine):
    """Test heatmap data generation."""
    heatmap = heatmap_engine.generate_heatmap(time_range_hours=24)
    
    assert heatmap is not None
    assert heatmap.overall_balance >= 0
    assert heatmap.overall_balance <= 1
    assert heatmap.time_range_hours == 24


def test_zone_types(heatmap_engine):
    """Test all zone types can be created."""
    for zone_type in ZoneType:
        zone = PatrolZone(
            zone_type=zone_type,
            name=f"Test {zone_type.value}",
            center=GeoPoint(lat=26.7754, lng=-80.0583),
            created_by="admin",
        )
        heatmap_engine.add_zone(zone)
    
    zones = heatmap_engine.get_all_zones()
    assert len(zones) == len(ZoneType)


def test_patrol_ping_recording(heatmap_engine):
    """Test recording patrol pings."""
    # Record some pings
    for i in range(10):
        heatmap_engine.record_patrol_ping(
            f"officer_{i}",
            GeoPoint(lat=26.7754 + i * 0.001, lng=-80.0583)
        )
    
    # Pings should affect sector scores
    scores = heatmap_engine.calculate_sector_scores()
    assert len(scores) > 0


def test_zone_radius_validation():
    """Test zone radius validation."""
    # Valid radius
    zone = PatrolZone(
        zone_type=ZoneType.HOTSPOT,
        name="Valid Zone",
        center=GeoPoint(lat=26.7754, lng=-80.0583),
        radius_meters=500,
        created_by="admin",
    )
    assert zone.radius_meters == 500


def test_intensity_bounds():
    """Test intensity value bounds."""
    zone = PatrolZone(
        zone_type=ZoneType.HOTSPOT,
        name="Test Zone",
        center=GeoPoint(lat=26.7754, lng=-80.0583),
        intensity=0.5,
        created_by="admin",
    )
    assert 0 <= zone.intensity <= 1
