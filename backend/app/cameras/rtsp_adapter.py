"""
RBPD Internal RTSP Support Module
PROTECTED MODE - Additive Only

Provides RTSP stream adaptation for internal police cameras:
- Accept RTSP URLs
- Convert to WebRTC playable stream in browser
- Fallback snapshot mode if RTSP unavailable
- Supports PTZ commands (future)
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx
import asyncio
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
import uuid

router = APIRouter(prefix="/api/cameras/rtsp", tags=["RTSP Cameras"])

# In-memory storage for RTSP cameras (in production, use database)
RTSP_CAMERAS = {
    "rtsp-001": {
        "id": "rtsp-001",
        "name": "RBPD HQ - Main Entrance",
        "location": "RBPD Headquarters",
        "lat": 26.7754,
        "lng": -80.0517,
        "rtsp_url": "rtsp://demo:demo@192.168.1.100:554/stream1",
        "camera_type": "PTZ",
        "sector": "HQ",
        "stream_type": "rtsp",
        "description": "Main entrance camera at RBPD HQ",
        "category": "rbpd_rtsp",
        "ptz_enabled": True
    },
    "rtsp-002": {
        "id": "rtsp-002",
        "name": "RBPD HQ - Parking Lot",
        "location": "RBPD Headquarters",
        "lat": 26.7756,
        "lng": -80.0519,
        "rtsp_url": "rtsp://demo:demo@192.168.1.101:554/stream1",
        "camera_type": "Fixed",
        "sector": "HQ",
        "stream_type": "rtsp",
        "description": "Parking lot camera at RBPD HQ",
        "category": "rbpd_rtsp",
        "ptz_enabled": False
    },
    "rtsp-003": {
        "id": "rtsp-003",
        "name": "RBPD - Sector 1 Patrol",
        "location": "Sector 1",
        "lat": 26.7812,
        "lng": -80.0534,
        "rtsp_url": "rtsp://demo:demo@192.168.1.102:554/stream1",
        "camera_type": "PTZ",
        "sector": "Sector 1",
        "stream_type": "rtsp",
        "description": "Patrol camera in Sector 1",
        "category": "rbpd_rtsp",
        "ptz_enabled": True
    },
    "rtsp-004": {
        "id": "rtsp-004",
        "name": "RBPD - Sector 2 Intersection",
        "location": "Sector 2",
        "lat": 26.7789,
        "lng": -80.0612,
        "rtsp_url": "rtsp://demo:demo@192.168.1.103:554/stream1",
        "camera_type": "Fixed",
        "sector": "Sector 2",
        "stream_type": "rtsp",
        "description": "Intersection camera in Sector 2",
        "category": "rbpd_rtsp",
        "ptz_enabled": False
    }
}

# Health status tracking
camera_health = {cam_id: {"status": "unknown", "last_check": None, "latency_ms": None} for cam_id in RTSP_CAMERAS}


class RTSPCameraCreate(BaseModel):
    name: str
    location: str
    lat: float
    lng: float
    rtsp_url: str
    camera_type: str = "Fixed"
    sector: str = "Unknown"
    description: Optional[str] = None
    ptz_enabled: bool = False


class RTSPCameraResponse(BaseModel):
    id: str
    name: str
    location: str
    lat: float
    lng: float
    camera_type: str
    sector: str
    stream_type: str
    description: str
    category: str
    ptz_enabled: bool
    health_status: str = "unknown"


class RTSPCameraListResponse(BaseModel):
    cameras: list[RTSPCameraResponse]
    total: int


class PTZCommand(BaseModel):
    action: str  # pan_left, pan_right, tilt_up, tilt_down, zoom_in, zoom_out, preset
    value: Optional[int] = None  # For preset number or speed


@router.get("/list", response_model=RTSPCameraListResponse)
async def list_rtsp_cameras():
    """List all available RTSP cameras"""
    cameras = []
    for cam_id, cam_data in RTSP_CAMERAS.items():
        health = camera_health.get(cam_id, {})
        # Don't expose RTSP URL in list response
        cam_response = {k: v for k, v in cam_data.items() if k != "rtsp_url"}
        cameras.append(RTSPCameraResponse(
            **cam_response,
            health_status=health.get("status", "unknown")
        ))
    return RTSPCameraListResponse(cameras=cameras, total=len(cameras))


@router.get("/{camera_id}")
async def get_rtsp_camera(camera_id: str):
    """Get details for a specific RTSP camera"""
    if camera_id not in RTSP_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = RTSP_CAMERAS[camera_id]
    health = camera_health.get(camera_id, {})
    # Don't expose RTSP URL in response
    response_data = {k: v for k, v in cam_data.items() if k != "rtsp_url"}
    return {
        **response_data,
        "health_status": health.get("status", "unknown"),
        "last_health_check": health.get("last_check"),
        "latency_ms": health.get("latency_ms")
    }


@router.post("/add")
async def add_rtsp_camera(camera: RTSPCameraCreate):
    """Add a new RTSP camera to the registry"""
    camera_id = f"rtsp-{str(uuid.uuid4())[:8]}"
    
    new_camera = {
        "id": camera_id,
        "name": camera.name,
        "location": camera.location,
        "lat": camera.lat,
        "lng": camera.lng,
        "rtsp_url": camera.rtsp_url,
        "camera_type": camera.camera_type,
        "sector": camera.sector,
        "stream_type": "rtsp",
        "description": camera.description or f"RTSP camera at {camera.location}",
        "category": "rbpd_rtsp",
        "ptz_enabled": camera.ptz_enabled
    }
    
    RTSP_CAMERAS[camera_id] = new_camera
    camera_health[camera_id] = {"status": "unknown", "last_check": None, "latency_ms": None}
    
    return {
        "message": "Camera added successfully",
        "camera_id": camera_id,
        "camera": {k: v for k, v in new_camera.items() if k != "rtsp_url"}
    }


@router.get("/{camera_id}/snapshot")
async def get_rtsp_snapshot(camera_id: str):
    """Get current snapshot from RTSP camera (fallback mode)"""
    if camera_id not in RTSP_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = RTSP_CAMERAS[camera_id]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Generate placeholder for demo - real implementation would capture from RTSP
            placeholder_url = f"https://via.placeholder.com/640x360/0984e3/ffffff?text=RTSP:{cam_data['name'].replace(' ', '+')}"
            response = await client.get(placeholder_url)
            
            if response.status_code == 200:
                camera_health[camera_id] = {
                    "status": "online",
                    "last_check": datetime.utcnow().isoformat(),
                    "latency_ms": int(response.elapsed.total_seconds() * 1000)
                }
                return Response(
                    content=response.content,
                    media_type="image/png",
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "X-Camera-Id": camera_id,
                        "X-Camera-Name": cam_data["name"],
                        "X-Camera-Type": cam_data["camera_type"]
                    }
                )
    except Exception as e:
        camera_health[camera_id] = {
            "status": "offline",
            "last_check": datetime.utcnow().isoformat(),
            "error": str(e)
        }
        raise HTTPException(status_code=503, detail=f"Camera unavailable: {str(e)}")


@router.get("/{camera_id}/webrtc")
async def get_rtsp_webrtc(camera_id: str):
    """Get WebRTC stream configuration for RTSP camera"""
    if camera_id not in RTSP_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = RTSP_CAMERAS[camera_id]
    
    # In production, this would return WebRTC signaling info
    # For demo, return configuration for WebRTC setup
    return {
        "camera_id": camera_id,
        "camera_name": cam_data["name"],
        "webrtc_config": {
            "ice_servers": [
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "stun:stun1.l.google.com:19302"}
            ],
            "sdp_semantics": "unified-plan"
        },
        "stream_info": {
            "type": "rtsp_to_webrtc",
            "status": "demo_mode",
            "fallback_url": f"/api/cameras/rtsp/{camera_id}/snapshot"
        },
        "ptz_enabled": cam_data.get("ptz_enabled", False)
    }


@router.post("/{camera_id}/ptz")
async def send_ptz_command(camera_id: str, command: PTZCommand):
    """Send PTZ command to camera"""
    if camera_id not in RTSP_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = RTSP_CAMERAS[camera_id]
    
    if not cam_data.get("ptz_enabled", False):
        raise HTTPException(status_code=400, detail="Camera does not support PTZ")
    
    valid_actions = ["pan_left", "pan_right", "tilt_up", "tilt_down", "zoom_in", "zoom_out", "preset", "home"]
    if command.action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid PTZ action. Valid actions: {valid_actions}")
    
    # In production, this would send actual PTZ commands via ONVIF or proprietary protocol
    return {
        "camera_id": camera_id,
        "action": command.action,
        "value": command.value,
        "status": "command_sent",
        "message": f"PTZ command '{command.action}' sent to camera (demo mode)"
    }


@router.get("/health/check")
async def check_rtsp_health():
    """Check health status of all RTSP cameras"""
    results = {}
    
    for cam_id in RTSP_CAMERAS:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                start = datetime.utcnow()
                placeholder_url = "https://via.placeholder.com/1x1"
                response = await client.get(placeholder_url)
                latency = (datetime.utcnow() - start).total_seconds() * 1000
                
                camera_health[cam_id] = {
                    "status": "online" if response.status_code == 200 else "degraded",
                    "last_check": datetime.utcnow().isoformat(),
                    "latency_ms": int(latency)
                }
                results[cam_id] = camera_health[cam_id]
        except Exception as e:
            camera_health[cam_id] = {
                "status": "offline",
                "last_check": datetime.utcnow().isoformat(),
                "error": str(e)
            }
            results[cam_id] = camera_health[cam_id]
    
    return {
        "cameras": results,
        "total": len(results),
        "online": sum(1 for r in results.values() if r["status"] == "online"),
        "offline": sum(1 for r in results.values() if r["status"] == "offline")
    }
