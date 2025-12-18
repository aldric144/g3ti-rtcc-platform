"""
FDOT MJPEG Simulation Mode Module
PROTECTED MODE - Additive Only (Extends existing FDOT module)

Converts FDOT PNG snapshots to MJPEG-like motion stream.
Repeatedly fetches FDOT PNG snapshots and converts to MJPEG stream.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import asyncio
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/cameras/fdot", tags=["FDOT MJPEG Simulator"])

# Import FDOT camera catalog from existing module
FDOT_CAMERAS = {
    "fdot-stream-001": {
        "id": "fdot-stream-001",
        "name": "I-95 @ Blue Heron Blvd",
        "location": "Blue Heron Blvd & I-95",
        "lat": 26.784945,
        "lng": -80.094221,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-026.5-N--1",
        "description": "FDOT District 4 - I-95 Northbound at Blue Heron Blvd",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-002": {
        "id": "fdot-stream-002",
        "name": "I-95 @ Palm Beach Lakes Blvd",
        "location": "Palm Beach Lakes Blvd & I-95",
        "lat": 26.715,
        "lng": -80.075,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-021.0-N--1",
        "description": "FDOT District 4 - I-95 at Palm Beach Lakes Blvd",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-003": {
        "id": "fdot-stream-003",
        "name": "Blue Heron @ Broadway (US-1)",
        "location": "Blue Heron Blvd & US-1",
        "lat": 26.7846,
        "lng": -80.0597,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-US1-076.0-N--1",
        "description": "FDOT District 4 - Blue Heron at Broadway (US-1)",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-004": {
        "id": "fdot-stream-004",
        "name": "I-95 @ 45th Street",
        "location": "45th Street & I-95",
        "lat": 26.795,
        "lng": -80.068,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-028.0-N--1",
        "description": "FDOT District 4 - I-95 at 45th Street",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-005": {
        "id": "fdot-stream-005",
        "name": "Southern Blvd @ I-95",
        "location": "Southern Blvd & I-95",
        "lat": 26.685,
        "lng": -80.072,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-018.0-N--1",
        "description": "FDOT District 4 - Southern Blvd at I-95",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-006": {
        "id": "fdot-stream-006",
        "name": "I-95 @ PGA Blvd",
        "location": "PGA Blvd & I-95",
        "lat": 26.8334,
        "lng": -80.0889,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-031.0-N--1",
        "description": "FDOT District 4 - I-95 at PGA Blvd",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-007": {
        "id": "fdot-stream-007",
        "name": "Military Trail @ Blue Heron",
        "location": "Military Trail & Blue Heron Blvd",
        "lat": 26.785,
        "lng": -80.116,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-SR710-001.0-E--1",
        "description": "FDOT District 4 - Military Trail at Blue Heron",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-008": {
        "id": "fdot-stream-008",
        "name": "Congress Ave @ Blue Heron",
        "location": "Congress Ave & Blue Heron Blvd",
        "lat": 26.7845,
        "lng": -80.0999,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-SR807-026.5-N--1",
        "description": "FDOT District 4 - Congress Ave at Blue Heron",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-009": {
        "id": "fdot-stream-009",
        "name": "US-1 @ Silver Beach Rd",
        "location": "US-1 & Silver Beach Rd",
        "lat": 26.7929,
        "lng": -80.0569,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-US1-077.0-N--1",
        "description": "FDOT District 4 - US-1 at Silver Beach Rd",
        "category": "fdot_mjpeg_sim"
    },
    "fdot-stream-010": {
        "id": "fdot-stream-010",
        "name": "I-95 @ Okeechobee Blvd",
        "location": "Okeechobee Blvd & I-95",
        "lat": 26.715,
        "lng": -80.075,
        "stream_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-021.0-N--1",
        "description": "FDOT District 4 - I-95 at Okeechobee Blvd",
        "category": "fdot_mjpeg_sim"
    }
}

# Health status tracking
camera_health = {cam_id: {"status": "unknown", "last_check": None, "latency_ms": None} for cam_id in FDOT_CAMERAS}


@router.get("/mjpeg/list")
async def list_fdot_mjpeg_cameras():
    """List all FDOT cameras available for MJPEG simulation"""
    cameras = []
    for cam_id, cam_data in FDOT_CAMERAS.items():
        health = camera_health.get(cam_id, {})
        cameras.append({
            **cam_data,
            "mjpeg_url": f"/api/cameras/fdot/{cam_id}/live",
            "health_status": health.get("status", "unknown")
        })
    return {"cameras": cameras, "total": len(cameras)}


@router.get("/{camera_id}/live")
async def get_fdot_live_stream(camera_id: str, interval: Optional[int] = 2):
    """
    Get MJPEG-like live stream from FDOT camera.
    Repeatedly fetches PNG snapshots and streams as MJPEG.
    
    Args:
        camera_id: FDOT camera ID
        interval: Refresh interval in seconds (1-5, default 2)
    """
    if camera_id not in FDOT_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = FDOT_CAMERAS[camera_id]
    stream_url = cam_data["stream_url"]
    
    # Clamp interval between 1 and 5 seconds
    refresh_interval = max(1, min(5, interval))
    
    async def generate_mjpeg_stream():
        """Generate MJPEG stream by repeatedly fetching FDOT PNG snapshots"""
        boundary = b"--frame"
        
        while True:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    # Add cache-busting timestamp
                    timestamp = datetime.utcnow().timestamp()
                    url_with_cache_bust = f"{stream_url}?t={timestamp}"
                    
                    response = await client.get(url_with_cache_bust, follow_redirects=True)
                    
                    if response.status_code == 200 and len(response.content) > 0:
                        yield boundary + b"\r\n"
                        yield b"Content-Type: image/png\r\n"
                        yield f"Content-Length: {len(response.content)}\r\n\r\n".encode()
                        yield response.content
                        yield b"\r\n"
                        
                        camera_health[camera_id] = {
                            "status": "online",
                            "last_check": datetime.utcnow().isoformat(),
                            "latency_ms": int(response.elapsed.total_seconds() * 1000)
                        }
                    else:
                        # Return placeholder if FDOT returns empty response
                        placeholder_url = f"https://via.placeholder.com/640x360/636e72/ffffff?text=FDOT+Camera+Offline"
                        placeholder_response = await client.get(placeholder_url)
                        if placeholder_response.status_code == 200:
                            yield boundary + b"\r\n"
                            yield b"Content-Type: image/png\r\n"
                            yield f"Content-Length: {len(placeholder_response.content)}\r\n\r\n".encode()
                            yield placeholder_response.content
                            yield b"\r\n"
                        
                        camera_health[camera_id] = {
                            "status": "degraded",
                            "last_check": datetime.utcnow().isoformat(),
                            "message": "FDOT source returning empty response"
                        }
            except Exception as e:
                camera_health[camera_id] = {
                    "status": "error",
                    "last_check": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
                # Try to send error placeholder
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        placeholder_url = f"https://via.placeholder.com/640x360/d63031/ffffff?text=Stream+Error"
                        placeholder_response = await client.get(placeholder_url)
                        if placeholder_response.status_code == 200:
                            yield boundary + b"\r\n"
                            yield b"Content-Type: image/png\r\n"
                            yield f"Content-Length: {len(placeholder_response.content)}\r\n\r\n".encode()
                            yield placeholder_response.content
                            yield b"\r\n"
                except:
                    pass
            
            await asyncio.sleep(refresh_interval)
    
    return StreamingResponse(
        generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Camera-Id": camera_id,
            "X-Camera-Name": cam_data["name"],
            "X-Refresh-Interval": str(refresh_interval)
        }
    )


@router.get("/{camera_id}/status")
async def get_fdot_camera_status(camera_id: str):
    """Get current status of FDOT camera"""
    if camera_id not in FDOT_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = FDOT_CAMERAS[camera_id]
    health = camera_health.get(camera_id, {})
    
    return {
        "camera_id": camera_id,
        "name": cam_data["name"],
        "location": cam_data["location"],
        "health_status": health.get("status", "unknown"),
        "last_check": health.get("last_check"),
        "latency_ms": health.get("latency_ms"),
        "mjpeg_url": f"/api/cameras/fdot/{camera_id}/live",
        "snapshot_url": f"/api/v1/fdot/snapshot/{camera_id}"
    }


@router.get("/mjpeg/health")
async def check_fdot_mjpeg_health():
    """Check health status of all FDOT MJPEG cameras"""
    results = {}
    
    for cam_id, cam_data in FDOT_CAMERAS.items():
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                start = datetime.utcnow()
                response = await client.get(cam_data["stream_url"], follow_redirects=True)
                latency = (datetime.utcnow() - start).total_seconds() * 1000
                
                if response.status_code == 200 and len(response.content) > 0:
                    status = "online"
                elif response.status_code == 200:
                    status = "degraded"
                else:
                    status = "offline"
                
                camera_health[cam_id] = {
                    "status": status,
                    "last_check": datetime.utcnow().isoformat(),
                    "latency_ms": int(latency),
                    "content_length": len(response.content)
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
        "degraded": sum(1 for r in results.values() if r["status"] == "degraded"),
        "offline": sum(1 for r in results.values() if r["status"] == "offline")
    }
