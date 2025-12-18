"""
Unified Camera Registry Extension Module
PROTECTED MODE - Additive Only (Append new categories only)

Extends the camera registry with new camera network categories:
- marina_live
- singer_island
- pbc_traffic
- rbpd_rtsp
- fdot_mjpeg_sim
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/camera-registry", tags=["Camera Registry"])

# Extended Camera Categories
CAMERA_CATEGORIES = {
    "marina_live": {
        "name": "Marina Live Cameras",
        "description": "Live video feeds from Riviera Beach Marina and Port of Palm Beach",
        "icon": "anchor",
        "color": "#0984e3",
        "api_base": "/api/cameras/marina"
    },
    "singer_island": {
        "name": "Singer Island Cameras",
        "description": "Beach and weather cameras from Singer Island",
        "icon": "umbrella-beach",
        "color": "#00b894",
        "api_base": "/api/cameras/marina"
    },
    "pbc_traffic": {
        "name": "Palm Beach County Traffic",
        "description": "Traffic cameras from Palm Beach County intersections",
        "icon": "traffic-light",
        "color": "#fdcb6e",
        "api_base": "/api/cameras/pbc"
    },
    "rbpd_rtsp": {
        "name": "RBPD Internal Cameras",
        "description": "Internal RTSP cameras from RBPD facilities",
        "icon": "shield-alt",
        "color": "#6c5ce7",
        "api_base": "/api/cameras/rtsp"
    },
    "fdot_mjpeg_sim": {
        "name": "FDOT Live Motion",
        "description": "FDOT cameras with MJPEG motion simulation",
        "icon": "road",
        "color": "#e17055",
        "api_base": "/api/cameras/fdot"
    }
}

# Unified camera registry (aggregates all camera networks)
UNIFIED_REGISTRY: Dict[str, dict] = {}


class CameraRegistryEntry(BaseModel):
    id: str
    name: str
    location: str
    lat: float
    lng: float
    category: str
    stream_type: str
    description: Optional[str] = None
    health_status: str = "unknown"
    snapshot_url: Optional[str] = None
    stream_url: Optional[str] = None


class CategoryInfo(BaseModel):
    name: str
    description: str
    icon: str
    color: str
    api_base: str
    camera_count: int = 0


@router.get("/categories")
async def list_categories():
    """List all available camera categories"""
    categories = []
    for cat_id, cat_info in CAMERA_CATEGORIES.items():
        categories.append({
            "id": cat_id,
            **cat_info,
            "camera_count": sum(1 for cam in UNIFIED_REGISTRY.values() if cam.get("category") == cat_id)
        })
    return {"categories": categories, "total": len(categories)}


@router.get("/categories/{category_id}")
async def get_category(category_id: str):
    """Get details for a specific camera category"""
    if category_id not in CAMERA_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")
    
    cat_info = CAMERA_CATEGORIES[category_id]
    cameras = [cam for cam in UNIFIED_REGISTRY.values() if cam.get("category") == category_id]
    
    return {
        "id": category_id,
        **cat_info,
        "cameras": cameras,
        "camera_count": len(cameras)
    }


@router.get("/unified")
async def get_unified_registry():
    """Get all cameras from all networks in unified format"""
    # Aggregate cameras from all networks
    all_cameras = []
    
    # Marina cameras
    marina_cameras = [
        {"id": "marina-001", "name": "Riviera Beach Marina HD Live", "location": "Riviera Beach Marina", "lat": 26.7754, "lng": -80.0517, "category": "marina_live", "stream_type": "snapshot"},
        {"id": "marina-002", "name": "Singer Island Marriott Beach Cam", "location": "Singer Island", "lat": 26.7876, "lng": -80.0345, "category": "singer_island", "stream_type": "snapshot"},
        {"id": "marina-003", "name": "Port of Palm Beach - North Dock", "location": "Port of Palm Beach", "lat": 26.7668, "lng": -80.0489, "category": "marina_live", "stream_type": "snapshot"},
        {"id": "marina-004", "name": "Port of Palm Beach - South Basin", "location": "Port of Palm Beach", "lat": 26.7652, "lng": -80.0501, "category": "marina_live", "stream_type": "snapshot"},
        {"id": "marina-005", "name": "Peanut Island View", "location": "Lake Worth Inlet", "lat": 26.7712, "lng": -80.0398, "category": "marina_live", "stream_type": "snapshot"},
    ]
    all_cameras.extend(marina_cameras)
    
    # PBC Traffic cameras
    pbc_cameras = [
        {"id": "pbc-001", "name": "I-95 @ Okeechobee Blvd", "location": "West Palm Beach", "lat": 26.7153, "lng": -80.0754, "category": "pbc_traffic", "stream_type": "snapshot"},
        {"id": "pbc-002", "name": "I-95 @ Palm Beach Lakes Blvd", "location": "West Palm Beach", "lat": 26.7234, "lng": -80.0712, "category": "pbc_traffic", "stream_type": "snapshot"},
        {"id": "pbc-003", "name": "I-95 @ 45th Street", "location": "West Palm Beach", "lat": 26.7456, "lng": -80.0689, "category": "pbc_traffic", "stream_type": "snapshot"},
        {"id": "pbc-004", "name": "Blue Heron Blvd @ I-95", "location": "Riviera Beach", "lat": 26.7845, "lng": -80.0942, "category": "pbc_traffic", "stream_type": "snapshot"},
        {"id": "pbc-005", "name": "PGA Blvd @ I-95", "location": "Palm Beach Gardens", "lat": 26.8334, "lng": -80.0889, "category": "pbc_traffic", "stream_type": "snapshot"},
        {"id": "pbc-006", "name": "Northlake Blvd @ I-95", "location": "Palm Beach Gardens", "lat": 26.8123, "lng": -80.0834, "category": "pbc_traffic", "stream_type": "snapshot"},
        {"id": "pbc-007", "name": "Southern Blvd @ I-95", "location": "West Palm Beach", "lat": 26.6856, "lng": -80.0723, "category": "pbc_traffic", "stream_type": "snapshot"},
        {"id": "pbc-008", "name": "Forest Hill Blvd @ I-95", "location": "West Palm Beach", "lat": 26.6534, "lng": -80.0698, "category": "pbc_traffic", "stream_type": "snapshot"},
    ]
    all_cameras.extend(pbc_cameras)
    
    # RTSP cameras
    rtsp_cameras = [
        {"id": "rtsp-001", "name": "RBPD HQ - Main Entrance", "location": "RBPD Headquarters", "lat": 26.7754, "lng": -80.0517, "category": "rbpd_rtsp", "stream_type": "rtsp"},
        {"id": "rtsp-002", "name": "RBPD HQ - Parking Lot", "location": "RBPD Headquarters", "lat": 26.7756, "lng": -80.0519, "category": "rbpd_rtsp", "stream_type": "rtsp"},
        {"id": "rtsp-003", "name": "RBPD - Sector 1 Patrol", "location": "Sector 1", "lat": 26.7812, "lng": -80.0534, "category": "rbpd_rtsp", "stream_type": "rtsp"},
        {"id": "rtsp-004", "name": "RBPD - Sector 2 Intersection", "location": "Sector 2", "lat": 26.7789, "lng": -80.0612, "category": "rbpd_rtsp", "stream_type": "rtsp"},
    ]
    all_cameras.extend(rtsp_cameras)
    
    # FDOT MJPEG cameras
    fdot_cameras = [
        {"id": "fdot-stream-001", "name": "I-95 @ Blue Heron Blvd", "location": "Blue Heron Blvd & I-95", "lat": 26.784945, "lng": -80.094221, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-002", "name": "I-95 @ Palm Beach Lakes Blvd", "location": "Palm Beach Lakes Blvd & I-95", "lat": 26.715, "lng": -80.075, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-003", "name": "Blue Heron @ Broadway (US-1)", "location": "Blue Heron Blvd & US-1", "lat": 26.7846, "lng": -80.0597, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-004", "name": "I-95 @ 45th Street", "location": "45th Street & I-95", "lat": 26.795, "lng": -80.068, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-005", "name": "Southern Blvd @ I-95", "location": "Southern Blvd & I-95", "lat": 26.685, "lng": -80.072, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-006", "name": "I-95 @ PGA Blvd", "location": "PGA Blvd & I-95", "lat": 26.8334, "lng": -80.0889, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-007", "name": "Military Trail @ Blue Heron", "location": "Military Trail & Blue Heron Blvd", "lat": 26.785, "lng": -80.116, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-008", "name": "Congress Ave @ Blue Heron", "location": "Congress Ave & Blue Heron Blvd", "lat": 26.7845, "lng": -80.0999, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-009", "name": "US-1 @ Silver Beach Rd", "location": "US-1 & Silver Beach Rd", "lat": 26.7929, "lng": -80.0569, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
        {"id": "fdot-stream-010", "name": "I-95 @ Okeechobee Blvd", "location": "Okeechobee Blvd & I-95", "lat": 26.715, "lng": -80.075, "category": "fdot_mjpeg_sim", "stream_type": "mjpeg"},
    ]
    all_cameras.extend(fdot_cameras)
    
    # Update unified registry
    for cam in all_cameras:
        UNIFIED_REGISTRY[cam["id"]] = cam
    
    return {
        "cameras": all_cameras,
        "total": len(all_cameras),
        "by_category": {
            cat_id: sum(1 for cam in all_cameras if cam.get("category") == cat_id)
            for cat_id in CAMERA_CATEGORIES.keys()
        }
    }


@router.get("/unified/{camera_id}")
async def get_unified_camera(camera_id: str):
    """Get a specific camera from the unified registry"""
    # First try to find in unified registry
    if camera_id in UNIFIED_REGISTRY:
        return UNIFIED_REGISTRY[camera_id]
    
    # If not found, refresh registry and try again
    await get_unified_registry()
    
    if camera_id in UNIFIED_REGISTRY:
        return UNIFIED_REGISTRY[camera_id]
    
    raise HTTPException(status_code=404, detail="Camera not found in unified registry")


@router.get("/search")
async def search_cameras(
    q: Optional[str] = None,
    category: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: Optional[float] = 5.0
):
    """Search cameras by name, category, or location"""
    # Ensure registry is populated
    await get_unified_registry()
    
    results = list(UNIFIED_REGISTRY.values())
    
    # Filter by search query
    if q:
        q_lower = q.lower()
        results = [cam for cam in results if q_lower in cam.get("name", "").lower() or q_lower in cam.get("location", "").lower()]
    
    # Filter by category
    if category:
        results = [cam for cam in results if cam.get("category") == category]
    
    # Filter by location (simple distance calculation)
    if lat is not None and lng is not None:
        def distance(cam):
            import math
            cam_lat = cam.get("lat", 0)
            cam_lng = cam.get("lng", 0)
            # Haversine formula approximation
            dlat = math.radians(cam_lat - lat)
            dlng = math.radians(cam_lng - lng)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(cam_lat)) * math.sin(dlng/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return 6371 * c  # Earth radius in km
        
        results = [cam for cam in results if distance(cam) <= radius_km]
        results.sort(key=distance)
    
    return {
        "cameras": results,
        "total": len(results),
        "query": q,
        "category": category,
        "location_filter": {"lat": lat, "lng": lng, "radius_km": radius_km} if lat and lng else None
    }


@router.get("/stats")
async def get_registry_stats():
    """Get statistics about the camera registry"""
    # Ensure registry is populated
    await get_unified_registry()
    
    return {
        "total_cameras": len(UNIFIED_REGISTRY),
        "by_category": {
            cat_id: {
                "name": cat_info["name"],
                "count": sum(1 for cam in UNIFIED_REGISTRY.values() if cam.get("category") == cat_id),
                "color": cat_info["color"]
            }
            for cat_id, cat_info in CAMERA_CATEGORIES.items()
        },
        "by_stream_type": {
            stream_type: sum(1 for cam in UNIFIED_REGISTRY.values() if cam.get("stream_type") == stream_type)
            for stream_type in set(cam.get("stream_type") for cam in UNIFIED_REGISTRY.values())
        },
        "last_updated": datetime.utcnow().isoformat()
    }
