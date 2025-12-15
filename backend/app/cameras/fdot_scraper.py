"""
FDOT Live Snapshot Scraper Module.

This module provides integration with FDOT District 4 public traffic camera endpoints,
allowing the RTCC platform to pull live snapshots and generate pseudo-streams.

Features:
- Pull live traffic camera snapshots from FDOT public endpoints
- Parse FDOT public metadata feed
- Extract camera name, FDOT ID, coordinates, snapshot URL, status
- Generate MJPEG-style pseudo-stream for video wall integration
- Match cameras to nearest patrol sector/beat
"""

import asyncio
import math
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Optional
import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


# FDOT District 4 public API endpoint
FDOT_API_URL = "https://api.smartraffic.org/public/cameras"

# Fallback FDOT camera data for demo mode
FDOT_DEMO_CAMERAS = [
    {
        "fdot_id": "FDOT-D4-001",
        "name": "Blue Heron @ I-95 EB",
        "latitude": 26.784945,
        "longitude": -80.094221,
        "snapshot_url": "https://via.placeholder.com/640x360?text=FDOT+Blue+Heron+I-95+EB",
        "status": "online",
    },
    {
        "fdot_id": "FDOT-D4-002",
        "name": "Blue Heron @ I-95 WB",
        "latitude": 26.784820,
        "longitude": -80.095600,
        "snapshot_url": "https://via.placeholder.com/640x360?text=FDOT+Blue+Heron+I-95+WB",
        "status": "online",
    },
    {
        "fdot_id": "FDOT-D4-003",
        "name": "Blue Heron @ Broadway (US-1)",
        "latitude": 26.784600,
        "longitude": -80.059700,
        "snapshot_url": "https://via.placeholder.com/640x360?text=FDOT+Blue+Heron+Broadway",
        "status": "online",
    },
    {
        "fdot_id": "FDOT-D4-004",
        "name": "Military Trl @ Blue Heron",
        "latitude": 26.785000,
        "longitude": -80.116000,
        "snapshot_url": "https://via.placeholder.com/640x360?text=FDOT+Military+Blue+Heron",
        "status": "online",
    },
    {
        "fdot_id": "FDOT-D4-005",
        "name": "US-1 @ Silver Beach Rd",
        "latitude": 26.792900,
        "longitude": -80.056900,
        "snapshot_url": "https://via.placeholder.com/640x360?text=FDOT+US1+Silver+Beach",
        "status": "online",
    },
    {
        "fdot_id": "FDOT-D4-006",
        "name": "US-1 @ Park Ave",
        "latitude": 26.778600,
        "longitude": -80.056700,
        "snapshot_url": "https://via.placeholder.com/640x360?text=FDOT+US1+Park+Ave",
        "status": "online",
    },
    {
        "fdot_id": "FDOT-D4-007",
        "name": "Congress Ave @ Blue Heron",
        "latitude": 26.784500,
        "longitude": -80.099900,
        "snapshot_url": "https://via.placeholder.com/640x360?text=FDOT+Congress+Blue+Heron",
        "status": "online",
    },
]

# Patrol zone centers for sector computation
PATROL_ZONES = {
    "Zone-1-Downtown": (26.7753, -80.0589),
    "Zone-2-Marina": (26.7789, -80.0512),
    "Zone-3-Commercial": (26.7748, -80.0721),
    "Zone-4-Residential": (26.7698, -80.0612),
    "Zone-5-Port": (26.7634, -80.0534),
    "Zone-6-Beach": (26.7912, -80.0345),
}


class CameraStatus(str, Enum):
    """Camera status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


def compute_closest_sector(lat: float, lng: float) -> str:
    """
    Compute the closest patrol zone/sector for a given GPS coordinate.
    
    Uses Haversine distance formula to find the nearest patrol zone center.
    """
    min_distance = float('inf')
    closest_zone = "Zone-1-Downtown"
    
    for zone_name, (zone_lat, zone_lng) in PATROL_ZONES.items():
        lat1, lat2 = math.radians(lat), math.radians(zone_lat)
        dlat = math.radians(zone_lat - lat)
        dlng = math.radians(zone_lng - lng)
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = 6371 * c
        
        if distance < min_distance:
            min_distance = distance
            closest_zone = zone_name
    
    return closest_zone


@dataclass
class FDOTCamera:
    """FDOT traffic camera data model."""
    fdot_id: str
    name: str
    latitude: float
    longitude: float
    snapshot_url: str
    status: CameraStatus = CameraStatus.ONLINE
    sector: str = ""
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))
    description: Optional[str] = None
    
    def __post_init__(self):
        """Auto-compute sector if not provided."""
        if not self.sector:
            self.sector = compute_closest_sector(self.latitude, self.longitude)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "fdot_id": self.fdot_id,
            "name": self.name,
            "gps": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "snapshot_url": self.snapshot_url,
            "status": self.status.value if isinstance(self.status, CameraStatus) else self.status,
            "sector": self.sector,
            "last_updated": self.last_updated.isoformat(),
            "description": self.description,
            "source": "FDOT",
            "type": "traffic",
        }


class FDOTScraper:
    """
    FDOT Live Snapshot Scraper.
    
    Pulls live traffic camera data from FDOT District 4 public endpoints
    and provides methods to access camera information and snapshots.
    """
    
    def __init__(self):
        self.cameras: dict[str, FDOTCamera] = {}
        self._client: Optional[httpx.AsyncClient] = None
        self._last_fetch: Optional[datetime] = None
        self._fetch_interval = 60  # Refresh camera list every 60 seconds
        self._demo_mode = True  # Start in demo mode
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def fetch_cameras(self) -> list[FDOTCamera]:
        """
        Fetch camera list from FDOT API.
        
        Falls back to demo data if API is unavailable.
        """
        try:
            client = await self._get_client()
            response = await client.get(FDOT_API_URL)
            
            if response.status_code == 200:
                data = response.json()
                self._demo_mode = False
                return self._parse_fdot_response(data)
            else:
                logger.warning(
                    "fdot_api_error",
                    status_code=response.status_code,
                    message="Falling back to demo data"
                )
                return self._load_demo_cameras()
                
        except Exception as e:
            logger.warning(
                "fdot_api_exception",
                error=str(e),
                message="Falling back to demo data"
            )
            return self._load_demo_cameras()
    
    def _parse_fdot_response(self, data: dict) -> list[FDOTCamera]:
        """Parse FDOT API response into camera objects."""
        cameras = []
        
        # Handle different possible response formats
        camera_list = data.get("cameras", data.get("data", []))
        
        for cam_data in camera_list:
            try:
                camera = FDOTCamera(
                    fdot_id=cam_data.get("id", cam_data.get("camera_id", "")),
                    name=cam_data.get("name", cam_data.get("description", "Unknown")),
                    latitude=float(cam_data.get("latitude", cam_data.get("lat", 0))),
                    longitude=float(cam_data.get("longitude", cam_data.get("lon", 0))),
                    snapshot_url=cam_data.get("snapshot_url", cam_data.get("image_url", "")),
                    status=CameraStatus.ONLINE if cam_data.get("status", "online") == "online" else CameraStatus.OFFLINE,
                    description=cam_data.get("description"),
                )
                cameras.append(camera)
            except Exception as e:
                logger.warning("fdot_parse_error", error=str(e), camera_data=cam_data)
        
        return cameras
    
    def _load_demo_cameras(self) -> list[FDOTCamera]:
        """Load demo camera data for fallback."""
        self._demo_mode = True
        cameras = []
        
        for cam_data in FDOT_DEMO_CAMERAS:
            camera = FDOTCamera(
                fdot_id=cam_data["fdot_id"],
                name=cam_data["name"],
                latitude=cam_data["latitude"],
                longitude=cam_data["longitude"],
                snapshot_url=cam_data["snapshot_url"],
                status=CameraStatus(cam_data["status"]),
                description=f"FDOT District 4 traffic camera - {cam_data['name']}",
            )
            cameras.append(camera)
        
        return cameras
    
    async def refresh_cameras(self) -> None:
        """Refresh camera list from FDOT API."""
        cameras = await self.fetch_cameras()
        self.cameras = {cam.fdot_id: cam for cam in cameras}
        self._last_fetch = datetime.now(UTC)
        logger.info(
            "fdot_cameras_refreshed",
            count=len(self.cameras),
            demo_mode=self._demo_mode
        )
    
    async def get_all_cameras(self) -> list[dict]:
        """Get all FDOT cameras."""
        # Refresh if needed
        if not self.cameras or (
            self._last_fetch and 
            (datetime.now(UTC) - self._last_fetch).seconds > self._fetch_interval
        ):
            await self.refresh_cameras()
        
        return [cam.to_dict() for cam in self.cameras.values()]
    
    async def get_camera(self, camera_id: str) -> Optional[dict]:
        """Get a specific camera by ID."""
        if not self.cameras:
            await self.refresh_cameras()
        
        camera = self.cameras.get(camera_id)
        return camera.to_dict() if camera else None
    
    async def get_snapshot(self, camera_id: str) -> Optional[bytes]:
        """
        Fetch the latest snapshot image for a camera.
        
        Returns the raw image bytes.
        """
        camera = self.cameras.get(camera_id)
        if not camera:
            return None
        
        try:
            client = await self._get_client()
            response = await client.get(camera.snapshot_url)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.warning(
                    "fdot_snapshot_error",
                    camera_id=camera_id,
                    status_code=response.status_code
                )
                return None
                
        except Exception as e:
            logger.warning(
                "fdot_snapshot_exception",
                camera_id=camera_id,
                error=str(e)
            )
            return None
    
    async def get_status(self) -> dict:
        """Get overall FDOT camera system status."""
        if not self.cameras:
            await self.refresh_cameras()
        
        online_count = sum(
            1 for cam in self.cameras.values()
            if cam.status == CameraStatus.ONLINE
        )
        
        return {
            "total_cameras": len(self.cameras),
            "online_cameras": online_count,
            "offline_cameras": len(self.cameras) - online_count,
            "demo_mode": self._demo_mode,
            "last_updated": self._last_fetch.isoformat() if self._last_fetch else None,
        }
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode."""
        return self._demo_mode


# Singleton instance
_scraper_instance: Optional[FDOTScraper] = None


def get_fdot_scraper() -> FDOTScraper:
    """Get the singleton FDOT scraper instance."""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = FDOTScraper()
    return _scraper_instance


async def generate_mjpeg_stream(camera_id: str, refresh_interval: float = 2.0):
    """
    Generate MJPEG-style pseudo-stream for a camera.
    
    This is an async generator that yields MJPEG frames at the specified interval.
    Each frame is a complete JPEG image with MJPEG boundary markers.
    
    Args:
        camera_id: The FDOT camera ID
        refresh_interval: Seconds between frame refreshes (1-3 seconds recommended)
    
    Yields:
        bytes: MJPEG frame data with boundary markers
    """
    scraper = get_fdot_scraper()
    boundary = b"--frame"
    
    while True:
        try:
            snapshot = await scraper.get_snapshot(camera_id)
            
            if snapshot:
                # Yield MJPEG frame with boundary
                yield boundary + b"\r\n"
                yield b"Content-Type: image/jpeg\r\n"
                yield f"Content-Length: {len(snapshot)}\r\n".encode()
                yield b"\r\n"
                yield snapshot
                yield b"\r\n"
            
            await asyncio.sleep(refresh_interval)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning("mjpeg_stream_error", camera_id=camera_id, error=str(e))
            await asyncio.sleep(refresh_interval)
