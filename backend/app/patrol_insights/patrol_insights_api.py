"""
Patrol Insights API - REST Endpoints for Patrol Analysis

Provides CJIS-compliant API endpoints for patrol heatmaps and zone management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from .heatmap_engine import (
    PatrolZone,
    PatrolZoneCreate,
    HeatmapData,
)
from .patrol_insights_service import get_patrol_insights_service, PatrolInsightsService

router = APIRouter(prefix="/api/admin/patrol-insights", tags=["Patrol Insights"])


def get_current_user() -> str:
    """Get the current user from auth context."""
    return "admin"


@router.get("", response_model=HeatmapData)
async def get_patrol_insights(
    time_range_hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    service: PatrolInsightsService = Depends(get_patrol_insights_service),
):
    """Get patrol insights and heatmap data."""
    return await service.get_insights(time_range_hours)


@router.get("/zones", response_model=List[PatrolZone])
async def get_patrol_zones(
    active_only: bool = Query(True, description="Only return active zones"),
    service: PatrolInsightsService = Depends(get_patrol_insights_service),
):
    """Get all patrol zones."""
    return await service.get_all_zones(active_only)


@router.post("/manual-zone", response_model=PatrolZone, status_code=201)
async def create_manual_zone(
    data: PatrolZoneCreate,
    service: PatrolInsightsService = Depends(get_patrol_insights_service),
    user: str = Depends(get_current_user),
):
    """Create a manual patrol zone marker."""
    return await service.create_manual_zone(data, user)


@router.get("/manual-zone/{zone_id}", response_model=PatrolZone)
async def get_zone(
    zone_id: str,
    service: PatrolInsightsService = Depends(get_patrol_insights_service),
):
    """Get a specific patrol zone."""
    zone = await service.get_zone(zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.delete("/manual-zone/{zone_id}", status_code=204)
async def delete_manual_zone(
    zone_id: str,
    service: PatrolInsightsService = Depends(get_patrol_insights_service),
    user: str = Depends(get_current_user),
):
    """Delete a manual patrol zone."""
    success = await service.delete_manual_zone(zone_id, user)
    if not success:
        raise HTTPException(status_code=404, detail="Zone not found")
    return None


@router.post("/ping")
async def record_patrol_ping(
    officer_id: str = Query(..., description="Officer ID"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
    service: PatrolInsightsService = Depends(get_patrol_insights_service),
):
    """Record an officer location ping."""
    await service.record_patrol_ping(officer_id, lat, lng)
    return {"status": "recorded"}
