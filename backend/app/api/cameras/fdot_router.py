"""
FDOT Camera API Router.

Provides REST API endpoints for FDOT traffic camera integration:
- List all FDOT cameras
- Get individual camera details
- Stream camera snapshots as MJPEG
- Get system status
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio

from app.cameras.fdot_scraper import (
    get_fdot_scraper,
    generate_mjpeg_stream,
    FDOTScraper,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/fdot", tags=["FDOT Cameras"])


class FDOTCameraResponse(BaseModel):
    """Response model for FDOT camera data."""
    fdot_id: str
    name: str
    gps: dict
    snapshot_url: str
    status: str
    sector: str
    last_updated: str
    description: Optional[str]
    source: str
    type: str


class FDOTCameraListResponse(BaseModel):
    """Response model for FDOT camera list."""
    cameras: list[dict]
    total: int
    demo_mode: bool


class FDOTStatusResponse(BaseModel):
    """Response model for FDOT system status."""
    total_cameras: int
    online_cameras: int
    offline_cameras: int
    demo_mode: bool
    last_updated: Optional[str]


@router.get("", response_model=FDOTCameraListResponse)
async def get_fdot_cameras_root(
    sector: Optional[str] = None,
) -> FDOTCameraListResponse:
    """
    Get all FDOT traffic cameras (root endpoint).
    
    Optionally filter by patrol sector.
    """
    scraper = get_fdot_scraper()
    cameras = await scraper.get_all_cameras()
    
    if sector:
        cameras = [cam for cam in cameras if cam.get("sector") == sector]
    
    return FDOTCameraListResponse(
        cameras=cameras,
        total=len(cameras),
        demo_mode=scraper.is_demo_mode(),
    )


@router.get("/list", response_model=FDOTCameraListResponse)
async def list_fdot_cameras(
    sector: Optional[str] = None,
) -> FDOTCameraListResponse:
    """
    Get all FDOT traffic cameras.
    
    Optionally filter by patrol sector.
    """
    scraper = get_fdot_scraper()
    cameras = await scraper.get_all_cameras()
    
    if sector:
        cameras = [cam for cam in cameras if cam.get("sector") == sector]
    
    return FDOTCameraListResponse(
        cameras=cameras,
        total=len(cameras),
        demo_mode=scraper.is_demo_mode(),
    )


@router.get("/{camera_id}")
async def get_fdot_camera(camera_id: str) -> dict:
    """
    Get a specific FDOT camera by ID.
    """
    scraper = get_fdot_scraper()
    camera = await scraper.get_camera(camera_id)
    
    if not camera:
        raise HTTPException(
            status_code=404,
            detail=f"FDOT camera not found: {camera_id}"
        )
    
    return camera


@router.get("/{camera_id}/stream")
async def stream_fdot_camera(
    camera_id: str,
    refresh: float = 2.0,
) -> StreamingResponse:
    """
    Stream FDOT camera as MJPEG pseudo-stream.
    
    This endpoint provides a continuous MJPEG stream that refreshes
    the camera snapshot at the specified interval (1-3 seconds).
    
    Args:
        camera_id: The FDOT camera ID
        refresh: Refresh interval in seconds (default: 2.0, range: 1.0-3.0)
    """
    scraper = get_fdot_scraper()
    camera = await scraper.get_camera(camera_id)
    
    if not camera:
        raise HTTPException(
            status_code=404,
            detail=f"FDOT camera not found: {camera_id}"
        )
    
    # Clamp refresh interval to 1-3 seconds
    refresh_interval = max(1.0, min(3.0, refresh))
    
    return StreamingResponse(
        generate_mjpeg_stream(camera_id, refresh_interval),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


@router.get("/{camera_id}/snapshot")
async def get_fdot_snapshot(camera_id: str) -> StreamingResponse:
    """
    Get a single snapshot from an FDOT camera.
    
    Returns the latest JPEG image from the camera.
    """
    scraper = get_fdot_scraper()
    snapshot = await scraper.get_snapshot(camera_id)
    
    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"Snapshot not available for camera: {camera_id}"
        )
    
    return StreamingResponse(
        iter([snapshot]),
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
        }
    )


@router.get("/status", response_model=FDOTStatusResponse)
async def get_fdot_status() -> FDOTStatusResponse:
    """
    Get FDOT camera system status.
    
    Returns overall status including camera counts and demo mode indicator.
    """
    scraper = get_fdot_scraper()
    status = await scraper.get_status()
    return FDOTStatusResponse(**status)


# WebSocket connections for status updates
_ws_connections: set[WebSocket] = set()


@router.websocket("/status/ws")
async def fdot_status_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time FDOT camera status updates.
    
    Emits online/offline status changes for all FDOT cameras.
    """
    await websocket.accept()
    _ws_connections.add(websocket)
    
    logger.info("fdot_ws_connected", total_connections=len(_ws_connections))
    
    try:
        scraper = get_fdot_scraper()
        
        # Send initial status
        status = await scraper.get_status()
        await websocket.send_json({
            "type": "status_update",
            "data": status,
        })
        
        # Keep connection alive and send periodic updates
        while True:
            await asyncio.sleep(30)  # Update every 30 seconds
            
            status = await scraper.get_status()
            await websocket.send_json({
                "type": "status_update",
                "data": status,
            })
            
    except WebSocketDisconnect:
        logger.info("fdot_ws_disconnected")
    except Exception as e:
        logger.warning("fdot_ws_error", error=str(e))
    finally:
        _ws_connections.discard(websocket)


async def broadcast_status_update(status: dict):
    """Broadcast status update to all connected WebSocket clients."""
    if not _ws_connections:
        return
    
    message = {
        "type": "status_update",
        "data": status,
    }
    
    disconnected = set()
    for ws in _ws_connections:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.add(ws)
    
    # Remove disconnected clients
    _ws_connections.difference_update(disconnected)


async def broadcast_camera_event(event_type: str, camera_data: dict):
    """Broadcast camera event to all connected WebSocket clients."""
    if not _ws_connections:
        return
    
    message = {
        "type": event_type,
        "data": camera_data,
    }
    
    disconnected = set()
    for ws in _ws_connections:
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.add(ws)
    
    _ws_connections.difference_update(disconnected)
