"""
MJPEG Streaming Router for FDOT Cameras.

Provides MJPEG pseudo-live video streaming endpoints for FDOT traffic cameras.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.cameras.mjpeg_streamer import MJPEGStreamer
from app.camera_network.fdot_scraper import get_fdot_scraper
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["MJPEG Streaming"])

# FDOT Camera Registry - populated from scraper
FDOT_CAMERA_REGISTRY: dict = {}


async def _ensure_registry_loaded():
    """Ensure the FDOT camera registry is loaded."""
    global FDOT_CAMERA_REGISTRY
    if not FDOT_CAMERA_REGISTRY:
        scraper = get_fdot_scraper()
        cameras = await scraper.get_all_cameras()
        for cam in cameras:
            cam_id = cam.get("fdot_id") or cam.get("id")
            if cam_id:
                FDOT_CAMERA_REGISTRY[cam_id] = cam


@router.get("/api/cameras/fdot/{camera_id}/stream", response_class=StreamingResponse)
async def fdot_mjpeg_stream(camera_id: str):
    """
    Stream FDOT camera as MJPEG pseudo-live video.
    
    This endpoint provides a real video-like stream from FDOT snapshots
    by continuously refreshing at 1.0 second intervals.
    
    Args:
        camera_id: The FDOT camera ID
        
    Returns:
        StreamingResponse: MJPEG multipart stream
    """
    await _ensure_registry_loaded()
    
    camera = FDOT_CAMERA_REGISTRY.get(camera_id)
    
    if not camera:
        # Try to find by fdot_id prefix
        for key, cam in FDOT_CAMERA_REGISTRY.items():
            if key.endswith(camera_id) or camera_id in key:
                camera = cam
                break
    
    if not camera:
        raise HTTPException(
            status_code=404,
            detail=f"FDOT camera not found: {camera_id}"
        )
    
    snapshot_url = camera.get("snapshot_url", "")
    if not snapshot_url:
        raise HTTPException(
            status_code=400,
            detail=f"No snapshot URL available for camera: {camera_id}"
        )
    
    streamer = MJPEGStreamer(snapshot_url=snapshot_url, refresh_rate=1.0)
    
    return StreamingResponse(
        streamer.stream(),
        media_type="multipart/x-mixed-replace; boundary=frameboundary",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )
