"""
FDOT District 4 Traffic Camera Scraper for G3TI RTCC-UIP Platform.

Scrapes FDOT public camera feeds and converts them to Camera Registry format.
Supports live snapshot fetching and MJPEG pseudo-streaming.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, AsyncGenerator
from enum import Enum

try:
    import httpx
except ImportError:
    httpx = None


# SmartTraffic.org public API (no API key required)
SMARTTRAFFIC_API_URL = "https://api.smartraffic.org/public/cameras"

# FDOT District 4 API endpoint (fallback)
FDOT_API_URL = "https://fl511.com/map/mapIcons/Cameras"
FDOT_SNAPSHOT_BASE = "https://fl511.com/map/Ede/Cameras/"

# Placeholder for demo mode
PLACEHOLDER_SNAPSHOT = "https://via.placeholder.com/640x360?text=FDOT+Traffic+Camera"

# Demo placeholder image bytes (1x1 gray pixel JPEG) - minimal valid JPEG
DEMO_JPEG_BYTES = bytes([
    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
    0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
    0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
    0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
    0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
    0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
    0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
    0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
    0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
    0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
    0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
    0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
    0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
    0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
    0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
    0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
    0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
    0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
    0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
    0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
    0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
    0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
    0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
    0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
    0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
    0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
    0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD5, 0xDB, 0x20, 0xA8, 0xF1, 0x4C, 0xA3,
    0x18, 0xC6, 0x31, 0x8C, 0x63, 0x18, 0xC6, 0x31, 0x8C, 0x63, 0x18, 0xC6,
    0x31, 0x8C, 0x63, 0x18, 0xC6, 0x31, 0x8C, 0x63, 0x18, 0xC6, 0x31, 0x8C,
    0x63, 0x18, 0xC6, 0x31, 0x8C, 0x63, 0x18, 0xC6, 0x31, 0x8C, 0x63, 0x18,
    0xFF, 0xD9
])


# Demo FDOT cameras for Riviera Beach / Palm Beach area with real FDOT snapshot URLs
FDOT_DEMO_CAMERAS = [
    {
        "fdot_id": "FDOT-D4-001",
        "name": "Blue Heron @ I-95 EB",
        "latitude": 26.784945,
        "longitude": -80.094221,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-026.5-N--1",
        "description": "FDOT District 4 traffic camera - Blue Heron @ I-95 EB",
    },
    {
        "fdot_id": "FDOT-D4-002",
        "name": "Blue Heron @ I-95 WB",
        "latitude": 26.78482,
        "longitude": -80.0956,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-026.5-S--1",
        "description": "FDOT District 4 traffic camera - Blue Heron @ I-95 WB",
    },
    {
        "fdot_id": "FDOT-D4-003",
        "name": "Blue Heron @ Broadway (US-1)",
        "latitude": 26.7846,
        "longitude": -80.0597,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-US1-076.0-N--1",
        "description": "FDOT District 4 traffic camera - Blue Heron @ Broadway (US-1)",
    },
    {
        "fdot_id": "FDOT-D4-004",
        "name": "Military Trl @ Blue Heron",
        "latitude": 26.785,
        "longitude": -80.116,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-SR710-001.0-E--1",
        "description": "FDOT District 4 traffic camera - Military Trl @ Blue Heron",
    },
    {
        "fdot_id": "FDOT-D4-005",
        "name": "US-1 @ Silver Beach Rd",
        "latitude": 26.7929,
        "longitude": -80.0569,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-US1-077.0-N--1",
        "description": "FDOT District 4 traffic camera - US-1 @ Silver Beach Rd",
    },
    {
        "fdot_id": "FDOT-D4-006",
        "name": "US-1 @ Park Ave",
        "latitude": 26.7786,
        "longitude": -80.0567,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-US1-075.5-N--1",
        "description": "FDOT District 4 traffic camera - US-1 @ Park Ave",
    },
    {
        "fdot_id": "FDOT-D4-007",
        "name": "Congress Ave @ Blue Heron",
        "latitude": 26.7845,
        "longitude": -80.0999,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-SR807-026.5-N--1",
        "description": "FDOT District 4 traffic camera - Congress Ave @ Blue Heron",
    },
    {
        "fdot_id": "FDOT-D4-008",
        "name": "I-95 @ 45th Street",
        "latitude": 26.7950,
        "longitude": -80.0680,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-028.0-N--1",
        "description": "FDOT District 4 traffic camera - I-95 @ 45th Street",
    },
    {
        "fdot_id": "FDOT-D4-009",
        "name": "I-95 @ PGA Blvd",
        "latitude": 26.8334,
        "longitude": -80.0889,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-031.0-N--1",
        "description": "FDOT District 4 traffic camera - I-95 @ PGA Blvd",
    },
    {
        "fdot_id": "FDOT-D4-010",
        "name": "I-95 @ Okeechobee Blvd",
        "latitude": 26.7150,
        "longitude": -80.0750,
        "snapshot_url": "https://fl511.com/map/Cctv/CCTV-D4-I95-021.0-N--1",
        "description": "FDOT District 4 traffic camera - I-95 @ Okeechobee Blvd",
    },
]


class FDOTScraper:
    """
    FDOT District 4 Traffic Camera Scraper.
    
    Fetches camera data from FDOT public endpoints and converts
    to Camera Registry format. Supports live snapshot fetching
    and MJPEG pseudo-streaming.
    """
    
    _instance: Optional["FDOTScraper"] = None
    
    def __new__(cls) -> "FDOTScraper":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the FDOT scraper."""
        if self._initialized:
            return
        
        self._cameras: List[Dict[str, Any]] = []
        self._last_fetch: Optional[datetime] = None
        self._demo_mode: bool = True
        self._http_client: Optional[Any] = None
        self._snapshot_cache: Dict[str, tuple] = {}
        self._cache_ttl_seconds: float = 1.0
        self._initialized = True
    
    async def _get_http_client(self) -> Optional[Any]:
        """Get or create HTTP client."""
        if httpx is None:
            return None
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=10.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "G3TI-RTCC-UIP/1.0 (Traffic Camera Monitor)"
                }
            )
        return self._http_client
    
    async def fetch_cameras_from_smarttraffic(self) -> List[Dict[str, Any]]:
        """Fetch cameras from SmartTraffic.org public API."""
        client = await self._get_http_client()
        if client is None:
            return []
        
        try:
            response = await client.get(SMARTTRAFFIC_API_URL)
            if response.status_code == 200:
                data = response.json()
                return self._parse_smarttraffic_response(data)
        except Exception as e:
            print(f"[FDOT] SmartTraffic API error: {e}")
        return []
    
    def _parse_smarttraffic_response(self, data: Any) -> List[Dict[str, Any]]:
        """Parse SmartTraffic API response."""
        cameras = []
        if isinstance(data, dict) and "cameras" in data:
            data = data["cameras"]
        
        if isinstance(data, list):
            for item in data:
                try:
                    camera = {
                        "fdot_id": f"smarttraffic-{item.get('id', '')}",
                        "name": item.get("name", "Traffic Camera"),
                        "latitude": float(item.get("latitude", 0)),
                        "longitude": float(item.get("longitude", 0)),
                        "snapshot_url": item.get("snapshotUrl") or item.get("imageUrl", PLACEHOLDER_SNAPSHOT),
                        "description": item.get("description", ""),
                        "camera_type": "traffic",
                        "jurisdiction": "FDOT",
                        "status": "online" if item.get("active", True) else "offline",
                        "source": "smarttraffic",
                    }
                    cameras.append(camera)
                except Exception as e:
                    print(f"[FDOT] Error parsing SmartTraffic camera: {e}")
        return cameras
    
    async def fetch_cameras(self) -> List[Dict[str, Any]]:
        """
        Fetch cameras from FDOT API.
        Falls back to demo data if API is unavailable.
        """
        # Try SmartTraffic first
        cameras = await self.fetch_cameras_from_smarttraffic()
        if cameras:
            self._cameras = cameras
            self._demo_mode = False
            self._last_fetch = datetime.now(timezone.utc)
            return self._cameras
        
        # Try FDOT API
        client = await self._get_http_client()
        if client is not None:
            try:
                response = await client.get(FDOT_API_URL)
                if response.status_code == 200:
                    data = response.json()
                    self._cameras = self._parse_fdot_response(data)
                    self._demo_mode = False
                    self._last_fetch = datetime.now(timezone.utc)
                    return self._cameras
            except Exception as e:
                print(f"[FDOT] API error: {e}")
        
        return self._load_demo_cameras()
    
    def fetch_cameras_sync(self) -> List[Dict[str, Any]]:
        """Synchronous version of fetch_cameras."""
        try:
            return asyncio.run(self.fetch_cameras())
        except RuntimeError:
            return self._load_demo_cameras()
    
    def _parse_fdot_response(self, data: Any) -> List[Dict[str, Any]]:
        """Parse FDOT API response into camera format."""
        cameras = []
        if isinstance(data, list):
            for item in data:
                try:
                    camera = {
                        "fdot_id": f"fdot-{item.get('id', '')}",
                        "name": item.get("name", "FDOT Camera"),
                        "latitude": float(item.get("latitude", 0)),
                        "longitude": float(item.get("longitude", 0)),
                        "snapshot_url": item.get("imageUrl", PLACEHOLDER_SNAPSHOT),
                        "description": item.get("description", ""),
                        "camera_type": "traffic",
                        "jurisdiction": "FDOT",
                        "status": "online" if item.get("active", True) else "offline",
                        "source": "fdot_api",
                    }
                    cameras.append(camera)
                except Exception as e:
                    print(f"[FDOT] Error parsing camera: {e}")
        return cameras
    
    def _load_demo_cameras(self) -> List[Dict[str, Any]]:
        """Load demo FDOT cameras."""
        self._demo_mode = True
        self._last_fetch = datetime.now(timezone.utc)
        
        cameras = []
        for cam in FDOT_DEMO_CAMERAS:
            cameras.append({
                **cam,
                "gps": {"latitude": cam["latitude"], "longitude": cam["longitude"]},
                "camera_type": "traffic",
                "type": "traffic",
                "jurisdiction": "FDOT",
                "status": "online",
                "sector": self._compute_sector(cam["latitude"], cam["longitude"]),
                "source": "FDOT",
                "last_updated": datetime.now(timezone.utc).isoformat(),
            })
        
        self._cameras = cameras
        return cameras
    
    def _compute_sector(self, lat: float, lng: float) -> str:
        """Compute patrol sector based on GPS coordinates."""
        if lat > 26.80:
            return "Zone-5-Beach"
        elif lat > 26.78:
            if lng < -80.08:
                return "Zone-3-Commercial"
            else:
                return "Zone-2-Marina"
        elif lat > 26.76:
            if lng < -80.07:
                return "Zone-4-Residential"
            else:
                return "Zone-1-Downtown"
        else:
            return "Zone-1-Downtown"
    
    async def get_all_cameras(self) -> List[Dict[str, Any]]:
        """Get all cached cameras (async)."""
        if not self._cameras:
            await self.fetch_cameras()
        return self._cameras
    
    async def get_camera(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific camera by ID (async)."""
        cameras = await self.get_all_cameras()
        for cam in cameras:
            if cam.get("fdot_id") == camera_id:
                return cam
        return None
    
    async def fetch_snapshot(self, snapshot_url: str) -> Optional[bytes]:
        """
        Fetch a fresh snapshot from the given URL.
        Returns raw JPEG bytes or demo bytes if fetch failed.
        """
        now = datetime.now(timezone.utc)
        if snapshot_url in self._snapshot_cache:
            cached_bytes, cached_time = self._snapshot_cache[snapshot_url]
            age = (now - cached_time).total_seconds()
            if age < self._cache_ttl_seconds:
                return cached_bytes
        
        client = await self._get_http_client()
        if client is None:
            return DEMO_JPEG_BYTES
        
        try:
            response = await client.get(snapshot_url, timeout=5.0)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "image" in content_type or snapshot_url.endswith((".jpg", ".jpeg", ".png")):
                    image_bytes = response.content
                    self._snapshot_cache[snapshot_url] = (image_bytes, now)
                    return image_bytes
        except Exception as e:
            print(f"[FDOT] Snapshot fetch error: {e}")
        
        return DEMO_JPEG_BYTES
    
    async def get_snapshot(self, camera_id: str) -> Optional[bytes]:
        """Get a snapshot for a specific camera."""
        camera = await self.get_camera(camera_id)
        if not camera:
            return None
        snapshot_url = camera.get("snapshot_url", PLACEHOLDER_SNAPSHOT)
        return await self.fetch_snapshot(snapshot_url)
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode."""
        return self._demo_mode
    
    async def get_status(self) -> Dict[str, Any]:
        """Get scraper status (async)."""
        cameras = await self.get_all_cameras()
        return {
            "total_cameras": len(cameras),
            "online_cameras": sum(1 for c in cameras if c.get("status") == "online"),
            "offline_cameras": sum(1 for c in cameras if c.get("status") == "offline"),
            "demo_mode": self._demo_mode,
            "last_updated": self._last_fetch.isoformat() if self._last_fetch else None,
        }
    
    async def check_camera_health(self, camera_id: str) -> Dict[str, Any]:
        """Check health of a specific camera by testing snapshot availability."""
        camera = await self.get_camera(camera_id)
        if not camera:
            return {
                "camera_id": camera_id,
                "status": "not_found",
                "latency_ms": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        
        snapshot_url = camera.get("snapshot_url", "")
        start_time = datetime.now(timezone.utc)
        
        client = await self._get_http_client()
        if client is None:
            return {
                "camera_id": camera_id,
                "status": "offline",
                "latency_ms": None,
                "timestamp": start_time.isoformat(),
                "error": "HTTP client not available",
            }
        
        try:
            response = await client.get(snapshot_url, timeout=2.0)
            latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return {
                    "camera_id": camera_id,
                    "status": "online",
                    "latency_ms": round(latency_ms, 2),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            else:
                return {
                    "camera_id": camera_id,
                    "status": "offline",
                    "latency_ms": round(latency_ms, 2),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": f"HTTP {response.status_code}",
                }
        except asyncio.TimeoutError:
            return {
                "camera_id": camera_id,
                "status": "offline",
                "latency_ms": 2000,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "Timeout",
            }
        except Exception as e:
            return {
                "camera_id": camera_id,
                "status": "offline",
                "latency_ms": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
            }


# Singleton accessor
_scraper_instance: Optional[FDOTScraper] = None


def get_fdot_scraper() -> FDOTScraper:
    """Get the FDOT scraper singleton."""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = FDOTScraper()
    return _scraper_instance


async def generate_mjpeg_stream(
    camera_id: str,
    refresh_interval: float = 2.0,
) -> AsyncGenerator[bytes, None]:
    """
    Generate an MJPEG pseudo-stream for a camera.
    Yields JPEG frames at the specified interval.
    """
    scraper = get_fdot_scraper()
    
    while True:
        try:
            snapshot = await scraper.get_snapshot(camera_id)
            if snapshot:
                yield b"--frame\r\n"
                yield b"Content-Type: image/jpeg\r\n"
                yield f"Content-Length: {len(snapshot)}\r\n".encode()
                yield b"\r\n"
                yield snapshot
                yield b"\r\n"
            
            await asyncio.sleep(refresh_interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[FDOT] MJPEG stream error: {e}")
            await asyncio.sleep(refresh_interval)
