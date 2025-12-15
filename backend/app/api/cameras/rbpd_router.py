"""
RBPD Internal Camera API Router for G3TI RTCC-UIP Platform.

Provides REST API endpoints for RBPD internal mock cameras:
- List all RBPD cameras
- Filter by sector and type
- Get camera statistics
"""

from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.cameras.rbpd_mock_loader import (
    load_rbpd_mock_cameras,
    get_rbpd_cameras_by_sector,
    get_rbpd_cameras_by_type,
    get_rbpd_camera_stats,
    get_cached_rbpd_cameras,
)


router = APIRouter(prefix="/rbpd", tags=["rbpd-cameras"])


# ============================================================================
# Response Models
# ============================================================================

class RBPDCameraResponse(BaseModel):
    """Response model for a single RBPD camera."""
    id: str
    name: str
    latitude: float
    longitude: float
    gps: dict
    assigned_sector: str
    sector: str
    camera_type: str
    type: str
    jurisdiction: str
    stream_url: str
    status: str
    source: str
    description: str
    created_at: str


class RBPDCameraListResponse(BaseModel):
    """Response model for RBPD camera list."""
    cameras: List[dict]
    total: int
    jurisdiction: str = "RBPD"
    source: str = "rbpd_mock"


class RBPDCameraStatsResponse(BaseModel):
    """Response model for RBPD camera statistics."""
    total_cameras: int
    by_sector: dict
    by_type: dict
    jurisdiction: str
    source: str


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("", response_model=RBPDCameraListResponse)
async def get_rbpd_cameras_root(
    sector: Optional[str] = Query(None, description="Filter by sector (e.g., 'Sector 1', 'HQ')"),
    camera_type: Optional[str] = Query(None, description="Filter by camera type ('CCTV', 'PTZ', 'LPR')"),
):
    """
    Get all RBPD internal mock cameras (root endpoint).
    
    Optionally filter by sector or camera type.
    
    Returns:
        List of RBPD cameras with metadata.
    """
    cameras = get_cached_rbpd_cameras()
    
    # Apply sector filter
    if sector:
        cameras = [c for c in cameras if c.get("assigned_sector") == sector]
    
    # Apply type filter
    if camera_type:
        cameras = [c for c in cameras if c.get("camera_type") == camera_type]
    
    return RBPDCameraListResponse(
        cameras=cameras,
        total=len(cameras),
    )


@router.get("/list", response_model=RBPDCameraListResponse)
async def list_rbpd_cameras(
    sector: Optional[str] = Query(None, description="Filter by sector (e.g., 'Sector 1', 'HQ')"),
    camera_type: Optional[str] = Query(None, description="Filter by camera type ('CCTV', 'PTZ', 'LPR')"),
):
    """
    List all RBPD internal mock cameras.
    
    Optionally filter by sector or camera type.
    
    Returns:
        List of RBPD cameras with metadata.
    """
    cameras = get_cached_rbpd_cameras()
    
    # Apply sector filter
    if sector:
        cameras = [c for c in cameras if c.get("assigned_sector") == sector]
    
    # Apply type filter
    if camera_type:
        cameras = [c for c in cameras if c.get("camera_type") == camera_type]
    
    return RBPDCameraListResponse(
        cameras=cameras,
        total=len(cameras),
    )


@router.get("/sectors")
async def list_rbpd_sectors():
    """
    List all available RBPD sectors.
    
    Returns:
        List of sector names with camera counts.
    """
    cameras = get_cached_rbpd_cameras()
    
    sectors = {}
    for camera in cameras:
        sector = camera.get("assigned_sector", "Unknown")
        sectors[sector] = sectors.get(sector, 0) + 1
    
    return {
        "sectors": [
            {"name": name, "camera_count": count}
            for name, count in sorted(sectors.items())
        ],
        "total_sectors": len(sectors),
    }


@router.get("/types")
async def list_rbpd_camera_types():
    """
    List all available RBPD camera types.
    
    Returns:
        List of camera types with counts.
    """
    cameras = get_cached_rbpd_cameras()
    
    types = {}
    for camera in cameras:
        cam_type = camera.get("camera_type", "Unknown")
        types[cam_type] = types.get(cam_type, 0) + 1
    
    return {
        "types": [
            {"name": name, "camera_count": count}
            for name, count in sorted(types.items())
        ],
        "total_types": len(types),
    }


@router.get("/stats", response_model=RBPDCameraStatsResponse)
async def get_rbpd_stats():
    """
    Get RBPD camera statistics.
    
    Returns:
        Statistics including total cameras, counts by sector and type.
    """
    stats = get_rbpd_camera_stats()
    return RBPDCameraStatsResponse(**stats)


@router.get("/{camera_id}")
async def get_rbpd_camera(camera_id: str):
    """
    Get a specific RBPD camera by ID.
    
    Args:
        camera_id: The camera ID to retrieve.
        
    Returns:
        Camera details or 404 if not found.
    """
    cameras = get_cached_rbpd_cameras()
    
    for camera in cameras:
        if camera.get("id") == camera_id:
            return camera
    
    return {"error": "Camera not found", "camera_id": camera_id}
