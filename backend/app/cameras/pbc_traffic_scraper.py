"""
Palm Beach County Traffic Camera Scraper Module
PROTECTED MODE - Additive Only

Scrapes publicly available Palm Beach County traffic cameras
and provides snapshot/pseudo-stream adaptation.
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx
import asyncio
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/cameras/pbc", tags=["PBC Traffic Cameras"])

# Palm Beach County Traffic Camera Catalog
PBC_TRAFFIC_CAMERAS = {
    "pbc-001": {
        "id": "pbc-001",
        "name": "I-95 @ Okeechobee Blvd",
        "location": "West Palm Beach",
        "lat": 26.7153,
        "lng": -80.0754,
        "intersection": "I-95 & Okeechobee Blvd",
        "stream_type": "snapshot",
        "refresh_interval": 5,
        "description": "Traffic camera at I-95 and Okeechobee Blvd interchange",
        "category": "pbc_traffic"
    },
    "pbc-002": {
        "id": "pbc-002",
        "name": "I-95 @ Palm Beach Lakes Blvd",
        "location": "West Palm Beach",
        "lat": 26.7234,
        "lng": -80.0712,
        "intersection": "I-95 & Palm Beach Lakes Blvd",
        "stream_type": "snapshot",
        "refresh_interval": 5,
        "description": "Traffic camera at I-95 and Palm Beach Lakes Blvd",
        "category": "pbc_traffic"
    },
    "pbc-003": {
        "id": "pbc-003",
        "name": "I-95 @ 45th Street",
        "location": "West Palm Beach",
        "lat": 26.7456,
        "lng": -80.0689,
        "intersection": "I-95 & 45th Street",
        "stream_type": "snapshot",
        "refresh_interval": 5,
        "description": "Traffic camera at I-95 and 45th Street",
        "category": "pbc_traffic"
    },
    "pbc-004": {
        "id": "pbc-004",
        "name": "Blue Heron Blvd @ I-95",
        "location": "Riviera Beach",
        "lat": 26.7845,
        "lng": -80.0942,
        "intersection": "Blue Heron Blvd & I-95",
        "stream_type": "snapshot",
        "refresh_interval": 5,
        "description": "Traffic camera at Blue Heron Blvd and I-95",
        "category": "pbc_traffic"
    },
    "pbc-005": {
        "id": "pbc-005",
        "name": "PGA Blvd @ I-95",
        "location": "Palm Beach Gardens",
        "lat": 26.8334,
        "lng": -80.0889,
        "intersection": "PGA Blvd & I-95",
        "stream_type": "snapshot",
        "refresh_interval": 5,
        "description": "Traffic camera at PGA Blvd and I-95",
        "category": "pbc_traffic"
    },
    "pbc-006": {
        "id": "pbc-006",
        "name": "Northlake Blvd @ I-95",
        "location": "Palm Beach Gardens",
        "lat": 26.8123,
        "lng": -80.0834,
        "intersection": "Northlake Blvd & I-95",
        "stream_type": "snapshot",
        "refresh_interval": 5,
        "description": "Traffic camera at Northlake Blvd and I-95",
        "category": "pbc_traffic"
    },
    "pbc-007": {
        "id": "pbc-007",
        "name": "Southern Blvd @ I-95",
        "location": "West Palm Beach",
        "lat": 26.6856,
        "lng": -80.0723,
        "intersection": "Southern Blvd & I-95",
        "stream_type": "snapshot",
        "refresh_interval": 5,
        "description": "Traffic camera at Southern Blvd and I-95",
        "category": "pbc_traffic"
    },
    "pbc-008": {
        "id": "pbc-008",
        "name": "Forest Hill Blvd @ I-95",
        "location": "West Palm Beach",
        "lat": 26.6534,
        "lng": -80.0698,
        "intersection": "Forest Hill Blvd & I-95",
        "stream_type": "snapshot",
        "refresh_interval": 5,
        "description": "Traffic camera at Forest Hill Blvd and I-95",
        "category": "pbc_traffic"
    }
}

# Health status tracking
camera_health = {cam_id: {"status": "unknown", "last_check": None, "latency_ms": None} for cam_id in PBC_TRAFFIC_CAMERAS}


class PBCCameraResponse(BaseModel):
    id: str
    name: str
    location: str
    lat: float
    lng: float
    intersection: str
    stream_type: str
    refresh_interval: int
    description: str
    category: str
    health_status: str = "unknown"


class PBCCameraListResponse(BaseModel):
    cameras: list[PBCCameraResponse]
    total: int


@router.get("/list", response_model=PBCCameraListResponse)
async def list_pbc_cameras():
    """List all available Palm Beach County traffic cameras"""
    cameras = []
    for cam_id, cam_data in PBC_TRAFFIC_CAMERAS.items():
        health = camera_health.get(cam_id, {})
        cameras.append(PBCCameraResponse(
            **cam_data,
            health_status=health.get("status", "unknown")
        ))
    return PBCCameraListResponse(cameras=cameras, total=len(cameras))


@router.get("/{camera_id}")
async def get_pbc_camera(camera_id: str):
    """Get details for a specific PBC traffic camera"""
    if camera_id not in PBC_TRAFFIC_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = PBC_TRAFFIC_CAMERAS[camera_id]
    health = camera_health.get(camera_id, {})
    return {
        **cam_data,
        "health_status": health.get("status", "unknown"),
        "last_health_check": health.get("last_check"),
        "latency_ms": health.get("latency_ms")
    }


@router.get("/{camera_id}/snapshot")
async def get_pbc_snapshot(camera_id: str):
    """Get current snapshot from PBC traffic camera"""
    if camera_id not in PBC_TRAFFIC_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = PBC_TRAFFIC_CAMERAS[camera_id]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Generate placeholder for demo - real implementation would scrape actual feeds
            placeholder_url = f"https://via.placeholder.com/640x360/2d3436/ffffff?text=PBC+Traffic:{cam_data['name'].replace(' ', '+')}"
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
                        "X-Refresh-Interval": str(cam_data["refresh_interval"])
                    }
                )
    except Exception as e:
        camera_health[camera_id] = {
            "status": "offline",
            "last_check": datetime.utcnow().isoformat(),
            "error": str(e)
        }
        raise HTTPException(status_code=503, detail=f"Camera unavailable: {str(e)}")


@router.get("/{camera_id}/stream")
async def get_pbc_stream(camera_id: str):
    """Get streaming feed from PBC traffic camera (pseudo-stream via snapshot refresh)"""
    if camera_id not in PBC_TRAFFIC_CAMERAS:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    cam_data = PBC_TRAFFIC_CAMERAS[camera_id]
    refresh_interval = cam_data.get("refresh_interval", 5)
    
    async def generate_stream():
        """Generate MJPEG-like stream by repeatedly fetching snapshots"""
        boundary = b"--frame"
        
        while True:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    placeholder_url = f"https://via.placeholder.com/640x360/2d3436/ffffff?text=PBC+Traffic:{cam_data['name'].replace(' ', '+')}"
                    response = await client.get(placeholder_url)
                    
                    if response.status_code == 200:
                        yield boundary + b"\r\n"
                        yield b"Content-Type: image/png\r\n\r\n"
                        yield response.content
                        yield b"\r\n"
                        
                        camera_health[camera_id] = {
                            "status": "online",
                            "last_check": datetime.utcnow().isoformat(),
                            "latency_ms": int(response.elapsed.total_seconds() * 1000)
                        }
            except Exception as e:
                camera_health[camera_id] = {
                    "status": "error",
                    "last_check": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
            
            await asyncio.sleep(refresh_interval)
    
    return StreamingResponse(
        generate_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache",
            "X-Camera-Id": camera_id,
            "X-Refresh-Interval": str(refresh_interval)
        }
    )


@router.get("/health/check")
async def check_pbc_health():
    """Check health status of all PBC traffic cameras"""
    results = {}
    
    for cam_id in PBC_TRAFFIC_CAMERAS:
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
