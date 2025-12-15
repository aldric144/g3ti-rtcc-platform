"""
Camera Network API Router for G3TI RTCC-UIP Platform.

Provides comprehensive REST API endpoints for the Camera Intelligence Stack:
- Camera CRUD operations
- Map data endpoints
- Video wall management
- PTZ camera control
- Health monitoring
- Nearby camera search
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.camera_network import (
    get_camera_registry,
    get_ingestion_engine,
    get_health_monitor,
    get_streaming_adapter,
    get_video_wall_manager,
    CameraType,
    CameraJurisdiction,
    CameraStatus,
    VideoWallLayout,
)


router = APIRouter(prefix="/cameras", tags=["camera-network"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CameraCreateRequest(BaseModel):
    """Request model for creating a camera."""
    name: str = Field(..., description="Camera display name")
    latitude: float = Field(..., description="GPS latitude")
    longitude: float = Field(..., description="GPS longitude")
    stream_url: str = Field(..., description="Stream URL")
    camera_type: str = Field("cctv", description="Camera type")
    address: Optional[str] = Field(None, description="Physical address")
    sector: Optional[str] = Field(None, description="Patrol sector")
    description: Optional[str] = Field(None, description="Description")


class CameraUpdateRequest(BaseModel):
    """Request model for updating a camera."""
    name: Optional[str] = None
    stream_url: Optional[str] = None
    status: Optional[str] = None
    address: Optional[str] = None
    sector: Optional[str] = None
    description: Optional[str] = None


class VideoWallAddRequest(BaseModel):
    """Request model for adding camera to video wall."""
    session_id: str
    position: int
    camera_id: str
    camera_name: Optional[str] = None
    stream_url: Optional[str] = None


class VideoWallRemoveRequest(BaseModel):
    """Request model for removing camera from video wall."""
    session_id: str
    position: int


class PTZCommandRequest(BaseModel):
    """Request model for PTZ camera control."""
    command: str = Field(..., description="PTZ command (pan_left, pan_right, tilt_up, tilt_down, zoom_in, zoom_out, preset)")
    value: Optional[float] = Field(None, description="Command value/speed")
    preset: Optional[int] = Field(None, description="Preset number for preset command")


# ============================================================================
# Camera CRUD Endpoints
# ============================================================================

@router.get("")
async def list_cameras(
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    camera_type: Optional[str] = Query(None, description="Filter by camera type"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """
    List all cameras with optional filtering.
    """
    engine = get_ingestion_engine()
    
    # Ensure cameras are loaded
    if engine._registry.count() == 0:
        engine.ingest_all()
    
    cameras = engine.get_all_cameras()
    
    # Apply filters
    if jurisdiction:
        cameras = [c for c in cameras if c.get("jurisdiction") == jurisdiction]
    if camera_type:
        cameras = [c for c in cameras if c.get("camera_type") == camera_type or c.get("type") == camera_type]
    if sector:
        cameras = [c for c in cameras if c.get("sector") == sector]
    if status:
        cameras = [c for c in cameras if c.get("status") == status]
    
    return {
        "cameras": cameras,
        "total": len(cameras),
        "filters": {
            "jurisdiction": jurisdiction,
            "camera_type": camera_type,
            "sector": sector,
            "status": status,
        },
    }


@router.get("/map")
async def get_cameras_for_map():
    """
    Get cameras formatted for map display.
    
    Returns cameras with color coding based on jurisdiction:
    - RBPD = Blue
    - FDOT = Green
    - LPR = Red
    - PTZ = Gold
    """
    engine = get_ingestion_engine()
    
    if engine._registry.count() == 0:
        engine.ingest_all()
    
    cameras = engine.get_all_cameras()
    
    # Add map-specific properties
    map_cameras = []
    for cam in cameras:
        jurisdiction = cam.get("jurisdiction", "")
        cam_type = cam.get("camera_type") or cam.get("type", "")
        
        # Determine marker color
        if cam_type == "lpr":
            color = "red"
        elif cam_type == "ptz":
            color = "gold"
        elif jurisdiction == "RBPD":
            color = "blue"
        elif jurisdiction == "FDOT":
            color = "green"
        else:
            color = "gray"
        
        map_cameras.append({
            **cam,
            "marker_color": color,
            "popup_title": cam.get("name", "Camera"),
            "popup_content": f"{jurisdiction} - {cam_type.upper()}",
        })
    
    return {
        "cameras": map_cameras,
        "total": len(map_cameras),
        "legend": {
            "blue": "RBPD Internal",
            "green": "FDOT Traffic",
            "red": "LPR Camera",
            "gold": "PTZ Camera",
            "gray": "Other",
        },
    }


@router.get("/nearby")
async def get_nearby_cameras(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(5.0, description="Search radius in km"),
):
    """
    Get cameras within radius of a point.
    """
    engine = get_ingestion_engine()
    
    if engine._registry.count() == 0:
        engine.ingest_all()
    
    cameras = engine.get_cameras_nearby(lat, lng, radius)
    
    return {
        "cameras": cameras,
        "total": len(cameras),
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius,
    }


@router.get("/health")
async def get_camera_health():
    """
    Get health status for all cameras.
    """
    monitor = get_health_monitor()
    
    return {
        "summary": monitor.get_health_summary(),
        "cameras": monitor.get_all_health(),
    }


@router.get("/{camera_id}")
async def get_camera(camera_id: str):
    """
    Get a specific camera by ID.
    """
    engine = get_ingestion_engine()
    camera = engine.get_camera(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera not found: {camera_id}")
    
    return camera


@router.post("/add")
async def add_camera(request: CameraCreateRequest):
    """
    Add a new camera manually.
    """
    engine = get_ingestion_engine()
    
    camera_data = {
        "name": request.name,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "stream_url": request.stream_url,
        "camera_type": request.camera_type,
        "address": request.address or "",
        "sector": request.sector or "",
        "description": request.description or "",
    }
    
    camera = engine.add_manual_camera(camera_data)
    
    return {
        "message": "Camera added successfully",
        "camera": camera,
    }


@router.patch("/{camera_id}")
async def update_camera(camera_id: str, request: CameraUpdateRequest):
    """
    Update an existing camera.
    """
    registry = get_camera_registry()
    
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.stream_url is not None:
        updates["stream_url"] = request.stream_url
    if request.status is not None:
        updates["status"] = request.status
    if request.address is not None:
        updates["address"] = request.address
    if request.sector is not None:
        updates["sector"] = request.sector
    if request.description is not None:
        updates["description"] = request.description
    
    camera = registry.update_camera(camera_id, updates)
    
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera not found: {camera_id}")
    
    return {
        "message": "Camera updated successfully",
        "camera": camera.to_dict(),
    }


@router.delete("/{camera_id}")
async def delete_camera(camera_id: str):
    """
    Delete a camera.
    """
    engine = get_ingestion_engine()
    
    # Try to remove from manual cameras first
    if engine.remove_manual_camera(camera_id):
        return {"message": "Camera deleted successfully", "camera_id": camera_id}
    
    # Try to remove from registry
    registry = get_camera_registry()
    if registry.delete_camera(camera_id):
        return {"message": "Camera deleted successfully", "camera_id": camera_id}
    
    raise HTTPException(status_code=404, detail=f"Camera not found: {camera_id}")


# ============================================================================
# Video Wall Endpoints
# ============================================================================

@router.get("/video-wall")
async def get_video_wall(
    session_id: Optional[str] = Query(None, description="Session ID"),
    user_id: Optional[str] = Query(None, description="User ID"),
):
    """
    Get video wall state.
    """
    manager = get_video_wall_manager()
    
    if session_id:
        state = manager.get_wall_state(session_id)
        if state:
            return state
    
    if user_id:
        session = manager.get_user_session(user_id)
        if session:
            return session.to_dict()
    
    # Return available layouts if no session
    return {
        "layouts": manager.get_available_layouts(),
        "presets": manager.list_presets(),
    }


@router.post("/video-wall/create")
async def create_video_wall_session(
    user_id: str = Query(..., description="User ID"),
    layout: str = Query("2x2", description="Layout type"),
):
    """
    Create a new video wall session.
    """
    manager = get_video_wall_manager()
    session = manager.create_session(user_id, layout)
    
    return {
        "message": "Video wall session created",
        "session": session.to_dict(),
    }


@router.post("/video-wall/add")
async def add_camera_to_video_wall(request: VideoWallAddRequest):
    """
    Add a camera to the video wall.
    """
    manager = get_video_wall_manager()
    
    success = manager.add_camera_to_wall(
        session_id=request.session_id,
        position=request.position,
        camera_id=request.camera_id,
        camera_name=request.camera_name or "",
        stream_url=request.stream_url or "",
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add camera to video wall")
    
    state = manager.get_wall_state(request.session_id)
    return {
        "message": "Camera added to video wall",
        "state": state,
    }


@router.post("/video-wall/remove")
async def remove_camera_from_video_wall(request: VideoWallRemoveRequest):
    """
    Remove a camera from the video wall.
    """
    manager = get_video_wall_manager()
    
    success = manager.remove_camera_from_wall(
        session_id=request.session_id,
        position=request.position,
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove camera from video wall")
    
    state = manager.get_wall_state(request.session_id)
    return {
        "message": "Camera removed from video wall",
        "state": state,
    }


@router.post("/video-wall/clear")
async def clear_video_wall(session_id: str = Query(...)):
    """
    Clear all cameras from the video wall.
    """
    manager = get_video_wall_manager()
    
    success = manager.clear_wall(session_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to clear video wall")
    
    return {"message": "Video wall cleared"}


@router.post("/video-wall/layout")
async def change_video_wall_layout(
    session_id: str = Query(...),
    layout: str = Query(...),
):
    """
    Change the video wall layout.
    """
    manager = get_video_wall_manager()
    
    success = manager.change_layout(session_id, layout)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to change layout")
    
    state = manager.get_wall_state(session_id)
    return {
        "message": "Layout changed",
        "state": state,
    }


@router.get("/video-wall/presets")
async def list_video_wall_presets():
    """
    List all video wall presets.
    """
    manager = get_video_wall_manager()
    return {"presets": manager.list_presets()}


@router.post("/video-wall/presets/save")
async def save_video_wall_preset(
    session_id: str = Query(...),
    name: str = Query(...),
    created_by: Optional[str] = Query(None),
):
    """
    Save current video wall as a preset.
    """
    manager = get_video_wall_manager()
    
    preset = manager.save_preset(session_id, name, created_by)
    
    if not preset:
        raise HTTPException(status_code=400, detail="Failed to save preset")
    
    return {
        "message": "Preset saved",
        "preset": preset.to_dict(),
    }


@router.post("/video-wall/presets/load")
async def load_video_wall_preset(
    session_id: str = Query(...),
    preset_id: str = Query(...),
):
    """
    Load a preset into the video wall.
    """
    manager = get_video_wall_manager()
    
    success = manager.load_preset(session_id, preset_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to load preset")
    
    state = manager.get_wall_state(session_id)
    return {
        "message": "Preset loaded",
        "state": state,
    }


# ============================================================================
# PTZ Control Endpoints
# ============================================================================

@router.post("/ptz/{camera_id}/command")
async def send_ptz_command(camera_id: str, request: PTZCommandRequest):
    """
    Send a PTZ command to a camera.
    
    Note: This is a placeholder for actual PTZ integration.
    """
    # Verify camera exists and is PTZ type
    engine = get_ingestion_engine()
    camera = engine.get_camera(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera not found: {camera_id}")
    
    cam_type = camera.get("camera_type") or camera.get("type", "")
    if cam_type != "ptz":
        raise HTTPException(status_code=400, detail="Camera is not a PTZ camera")
    
    # Log the command (placeholder for actual PTZ control)
    return {
        "message": "PTZ command sent",
        "camera_id": camera_id,
        "command": request.command,
        "value": request.value,
        "preset": request.preset,
        "status": "simulated",  # In demo mode
    }


# ============================================================================
# Streaming Endpoints
# ============================================================================

@router.get("/{camera_id}/stream")
async def get_camera_stream(
    camera_id: str,
    refresh_interval: float = Query(2.0, ge=1.0, le=10.0),
):
    """
    Get MJPEG stream for a camera.
    """
    engine = get_ingestion_engine()
    camera = engine.get_camera(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera not found: {camera_id}")
    
    adapter = get_streaming_adapter()
    adapter.register_camera(
        camera_id=camera_id,
        stream_url=camera.get("stream_url", ""),
    )
    
    return StreamingResponse(
        adapter.generate_mjpeg_stream(camera_id, refresh_interval),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/{camera_id}/snapshot")
async def get_camera_snapshot(camera_id: str):
    """
    Get a single snapshot from a camera.
    """
    engine = get_ingestion_engine()
    camera = engine.get_camera(camera_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera not found: {camera_id}")
    
    adapter = get_streaming_adapter()
    adapter.register_camera(
        camera_id=camera_id,
        stream_url=camera.get("stream_url", ""),
    )
    
    snapshot = await adapter.get_snapshot(camera_id)
    
    if not snapshot:
        raise HTTPException(status_code=500, detail="Failed to get snapshot")
    
    return StreamingResponse(
        iter([snapshot]),
        media_type="image/jpeg",
    )


# ============================================================================
# Statistics Endpoints
# ============================================================================

@router.get("/stats/summary")
async def get_camera_stats():
    """
    Get camera statistics summary.
    """
    engine = get_ingestion_engine()
    
    if engine._registry.count() == 0:
        engine.ingest_all()
    
    return engine.get_stats()


@router.post("/refresh")
async def refresh_cameras():
    """
    Refresh all camera sources.
    """
    engine = get_ingestion_engine()
    stats = engine.refresh()
    
    return {
        "message": "Cameras refreshed",
        "stats": stats,
    }
