"""
Cameras API Router for G3TI RTCC-UIP Platform.

Provides REST API endpoints for camera management, including:
- Public camera catalog access
- Camera CRUD operations
- Camera filtering by type, source, and sector
- FDOT traffic camera integration with live snapshots
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.cameras import (
    get_public_camera_catalog,
    PublicCamera,
    CameraType,
    CameraSource,
    PLACEHOLDER_STREAM_URL,
)

# Import FDOT router
from app.api.cameras.fdot_router import router as fdot_router

# Import RBPD router
from app.api.cameras.rbpd_router import router as rbpd_router

# Import MJPEG streaming router
from app.api.cameras.mjpeg_router import router as mjpeg_router

router = APIRouter(prefix="/cameras", tags=["cameras"])

# Include FDOT sub-router (routes will be at /cameras/fdot/*)
router.include_router(fdot_router)

# Include RBPD sub-router (routes will be at /cameras/rbpd/*)
router.include_router(rbpd_router)

# Include MJPEG streaming router
router.include_router(mjpeg_router)


class CameraCreateRequest(BaseModel):
    """Request model for creating a new camera."""
    name: str = Field(..., description="Camera display name")
    latitude: float = Field(..., description="GPS latitude")
    longitude: float = Field(..., description="GPS longitude")
    camera_type: str = Field(..., description="Camera type (traffic, marine, public, beach, cctv)")
    source: str = Field(..., description="Data source")
    stream_url: Optional[str] = Field(None, description="Video stream URL")
    description: Optional[str] = Field(None, description="Camera description")


class CameraUpdateRequest(BaseModel):
    """Request model for updating a camera."""
    name: Optional[str] = Field(None, description="Camera display name")
    stream_url: Optional[str] = Field(None, description="Video stream URL")
    status: Optional[str] = Field(None, description="Camera status (online, offline)")
    description: Optional[str] = Field(None, description="Camera description")


class CameraResponse(BaseModel):
    """Response model for camera data."""
    id: str
    name: str
    gps: dict
    stream_url: str
    type: str
    source: str
    sector: str
    status: str
    last_updated: str
    description: Optional[str]


class CameraListResponse(BaseModel):
    """Response model for camera list."""
    cameras: list[dict]
    total: int
    demo_mode: bool = True


class CameraStatsResponse(BaseModel):
    """Response model for camera statistics."""
    total_cameras: int
    online_cameras: int
    offline_cameras: int
    by_type: dict
    by_source: dict
    by_sector: dict


@router.get("")
async def get_all_cameras(
    camera_type: Optional[str] = Query(None, description="Filter by camera type"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    sector: Optional[str] = Query(None, description="Filter by patrol sector"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction (FDOT, RBPD, public)"),
    status: Optional[str] = Query(None, description="Filter by status (online, offline)"),
) -> dict:
    """
    Get all cameras from all sources (unified camera directory).
    
    Returns the full catalog of cameras including FDOT traffic cameras,
    RBPD internal cameras, and public cameras.
    
    Supports filtering by type, source, sector, jurisdiction, and status.
    """
    from app.camera_network.camera_ingestion_engine import get_ingestion_engine
    
    ingestion_engine = get_ingestion_engine()
    
    # Get all cameras from the unified registry
    all_cameras = ingestion_engine.get_all_cameras()
    
    # Apply filters
    if camera_type:
        all_cameras = [c for c in all_cameras if c.get("camera_type") == camera_type or c.get("type") == camera_type]
    if source:
        all_cameras = [c for c in all_cameras if c.get("source") == source]
    if sector:
        all_cameras = [c for c in all_cameras if c.get("sector") == sector]
    if jurisdiction:
        all_cameras = [c for c in all_cameras if c.get("jurisdiction") == jurisdiction]
    if status:
        all_cameras = [c for c in all_cameras if c.get("status") == status]
    
    return {
        "cameras": all_cameras,
        "total": len(all_cameras),
        "filters": {
            "jurisdiction": jurisdiction,
            "camera_type": camera_type,
            "sector": sector,
            "status": status,
        }
    }


@router.get("/map")
async def get_cameras_for_map() -> dict:
    """
    Get all cameras formatted for map display.
    
    Returns cameras with GPS coordinates for map markers.
    """
    from app.camera_network.camera_ingestion_engine import get_ingestion_engine
    
    ingestion_engine = get_ingestion_engine()
    all_cameras = ingestion_engine.get_all_cameras()
    
    # Format for map display
    map_cameras = []
    for cam in all_cameras:
        gps = cam.get("gps", {})
        if not gps:
            gps = {"latitude": cam.get("latitude"), "longitude": cam.get("longitude")}
        
        map_cameras.append({
            "id": cam.get("id"),
            "name": cam.get("name"),
            "latitude": gps.get("latitude"),
            "longitude": gps.get("longitude"),
            "type": cam.get("type") or cam.get("camera_type"),
            "status": cam.get("status", "online"),
            "jurisdiction": cam.get("jurisdiction", "public"),
            "sector": cam.get("sector"),
        })
    
    return {
        "cameras": map_cameras,
        "total": len(map_cameras),
    }


@router.get("/test")
async def camera_api_test() -> dict:
    """
    Test endpoint to verify camera API is online.
    
    Returns:
        Status message confirming camera API is operational.
    """
    return {"status": "camera-api-online"}


@router.get("/public", response_model=CameraListResponse)
async def get_public_cameras(
    camera_type: Optional[str] = Query(None, description="Filter by camera type"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    sector: Optional[str] = Query(None, description="Filter by patrol sector"),
) -> CameraListResponse:
    """
    Get all public cameras in the Riviera Beach area.
    
    Returns the full catalog of publicly available cameras including
    FDOT traffic cameras, Port of Palm Beach cameras, Singer Island
    public cameras, and Marina cameras.
    
    Supports filtering by type, source, and sector.
    """
    catalog = get_public_camera_catalog()
    
    if camera_type:
        try:
            ct = CameraType(camera_type)
            cameras = catalog.get_by_type(ct)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid camera type: {camera_type}. Valid types: {[t.value for t in CameraType]}"
            )
    elif source:
        try:
            cs = CameraSource(source)
            cameras = catalog.get_by_source(cs)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source: {source}. Valid sources: {[s.value for s in CameraSource]}"
            )
    elif sector:
        cameras = catalog.get_by_sector(sector)
    else:
        cameras = catalog.get_all()
    
    return CameraListResponse(
        cameras=cameras,
        total=len(cameras),
        demo_mode=True,
    )


@router.get("/public/{camera_id}")
async def get_public_camera(camera_id: str) -> dict:
    """
    Get a specific public camera by ID.
    """
    catalog = get_public_camera_catalog()
    camera = catalog.get_by_id(camera_id)
    
    if not camera:
        raise HTTPException(
            status_code=404,
            detail=f"Camera not found: {camera_id}"
        )
    
    return camera


@router.get("/public/stats/summary", response_model=CameraStatsResponse)
async def get_camera_stats() -> CameraStatsResponse:
    """
    Get statistics about the public camera catalog.
    """
    catalog = get_public_camera_catalog()
    stats = catalog.get_stats()
    return CameraStatsResponse(**stats)


@router.post("/manual-add")
async def add_camera_manually(request: CameraCreateRequest) -> dict:
    """
    Manually add a new camera to the catalog.
    
    This endpoint allows administrators to add custom cameras
    that are not part of the default public catalog.
    """
    catalog = get_public_camera_catalog()
    
    # Generate a unique ID
    import uuid
    camera_id = f"manual-{uuid.uuid4().hex[:8]}"
    
    # Map string type to enum
    try:
        camera_type = CameraType(request.camera_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid camera type: {request.camera_type}. Valid types: {[t.value for t in CameraType]}"
        )
    
    # Map string source to enum (or use custom source)
    try:
        source = CameraSource(request.source)
    except ValueError:
        # Allow custom sources for manually added cameras
        source = CameraSource.FDOT  # Default fallback
    
    camera = PublicCamera(
        id=camera_id,
        name=request.name,
        latitude=request.latitude,
        longitude=request.longitude,
        camera_type=camera_type,
        source=source,
        stream_url=request.stream_url or PLACEHOLDER_STREAM_URL,
        description=request.description,
    )
    
    result = catalog.add_camera(camera)
    return {
        "message": "Camera added successfully",
        "camera": result,
    }


@router.put("/manual-add/{camera_id}")
async def update_camera(camera_id: str, request: CameraUpdateRequest) -> dict:
    """
    Update an existing camera in the catalog.
    """
    catalog = get_public_camera_catalog()
    
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.stream_url is not None:
        updates["stream_url"] = request.stream_url
    if request.status is not None:
        updates["status"] = request.status
    if request.description is not None:
        updates["description"] = request.description
    
    result = catalog.update_camera(camera_id, updates)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Camera not found: {camera_id}"
        )
    
    return {
        "message": "Camera updated successfully",
        "camera": result,
    }


@router.delete("/manual-add/{camera_id}")
async def delete_camera(camera_id: str) -> dict:
    """
    Delete a camera from the catalog.
    """
    catalog = get_public_camera_catalog()
    
    if not catalog.delete_camera(camera_id):
        raise HTTPException(
            status_code=404,
            detail=f"Camera not found: {camera_id}"
        )
    
    return {
        "message": "Camera deleted successfully",
        "camera_id": camera_id,
    }


@router.get("/types")
async def get_camera_types() -> dict:
    """
    Get all available camera types.
    """
    return {
        "types": [t.value for t in CameraType],
    }


@router.get("/sources")
async def get_camera_sources() -> dict:
    """
    Get all available camera sources.
    """
    return {
        "sources": [s.value for s in CameraSource],
    }
