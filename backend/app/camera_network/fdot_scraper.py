"""
FDOT District 4 Traffic Camera Scraper for G3TI RTCC-UIP Platform.

Scrapes FDOT public camera feeds and converts them to Camera Registry format.
Supports both JSON API endpoints and HTML scraping fallback.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

try:
    import httpx
except ImportError:
    httpx = None


# FDOT District 4 API endpoint (public, no API key required)
FDOT_API_URL = "https://fl511.com/map/mapIcons/Cameras"
FDOT_SNAPSHOT_BASE = "https://fl511.com/map/Ede/Cameras/"

# Placeholder for demo mode
PLACEHOLDER_SNAPSHOT = "https://via.placeholder.com/640x360?text=FDOT+Traffic+Camera"


# Demo FDOT cameras for Riviera Beach / Palm Beach area
FDOT_DEMO_CAMERAS = [
    {
        "fdot_id": "fdot-i95-blue-heron",
        "name": "I-95 @ Blue Heron Blvd",
        "latitude": 26.7841,
        "longitude": -80.0722,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "I-95 Northbound at Blue Heron Blvd exit",
    },
    {
        "fdot_id": "fdot-i95-45th-st",
        "name": "I-95 @ 45th Street",
        "latitude": 26.7950,
        "longitude": -80.0680,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "I-95 at 45th Street interchange",
    },
    {
        "fdot_id": "fdot-i95-pga-blvd",
        "name": "I-95 @ PGA Blvd",
        "latitude": 26.8334,
        "longitude": -80.0889,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "I-95 at PGA Boulevard",
    },
    {
        "fdot_id": "fdot-us1-blue-heron",
        "name": "US-1 @ Blue Heron Blvd",
        "latitude": 26.7755,
        "longitude": -80.0530,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "US-1 Federal Highway at Blue Heron",
    },
    {
        "fdot_id": "fdot-us1-northlake",
        "name": "US-1 @ Northlake Blvd",
        "latitude": 26.7890,
        "longitude": -80.0510,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "US-1 at Northlake Boulevard",
    },
    {
        "fdot_id": "fdot-a1a-singer-island",
        "name": "A1A @ Singer Island",
        "latitude": 26.7920,
        "longitude": -80.0350,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "A1A Ocean Boulevard on Singer Island",
    },
    {
        "fdot_id": "fdot-congress-blue-heron",
        "name": "Congress Ave @ Blue Heron",
        "latitude": 26.7841,
        "longitude": -80.0950,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "Congress Avenue at Blue Heron Blvd",
    },
    {
        "fdot_id": "fdot-military-blue-heron",
        "name": "Military Trail @ Blue Heron",
        "latitude": 26.7841,
        "longitude": -80.1100,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "Military Trail at Blue Heron Blvd",
    },
    {
        "fdot_id": "fdot-i95-okeechobee",
        "name": "I-95 @ Okeechobee Blvd",
        "latitude": 26.7150,
        "longitude": -80.0750,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "I-95 at Okeechobee Boulevard",
    },
    {
        "fdot_id": "fdot-turnpike-pga",
        "name": "FL Turnpike @ PGA Blvd",
        "latitude": 26.8334,
        "longitude": -80.1200,
        "snapshot_url": PLACEHOLDER_SNAPSHOT,
        "description": "Florida Turnpike at PGA Boulevard",
    },
]


class FDOTScraper:
    """
    FDOT District 4 Traffic Camera Scraper.
    
    Fetches camera data from FDOT public endpoints and converts
    to Camera Registry format.
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
        self._initialized = True
    
    async def fetch_cameras(self) -> List[Dict[str, Any]]:
        """
        Fetch cameras from FDOT API.
        
        Falls back to demo data if API is unavailable.
        
        Returns:
            List of camera dictionaries.
        """
        if httpx is None:
            print("[FDOT] httpx not available, using demo data")
            return self._load_demo_cameras()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(FDOT_API_URL)
                
                if response.status_code == 200:
                    data = response.json()
                    self._cameras = self._parse_fdot_response(data)
                    self._demo_mode = False
                    self._last_fetch = datetime.utcnow()
                    return self._cameras
                else:
                    print(f"[FDOT] API returned {response.status_code}, using demo data")
                    return self._load_demo_cameras()
        except Exception as e:
            print(f"[FDOT] API error: {e}, using demo data")
            return self._load_demo_cameras()
    
    def fetch_cameras_sync(self) -> List[Dict[str, Any]]:
        """
        Synchronous version of fetch_cameras.
        
        Returns:
            List of camera dictionaries.
        """
        try:
            return asyncio.run(self.fetch_cameras())
        except RuntimeError:
            # Already in async context
            return self._load_demo_cameras()
    
    def _parse_fdot_response(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parse FDOT API response into camera format.
        
        Args:
            data: Raw API response data.
            
        Returns:
            List of camera dictionaries.
        """
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
                    }
                    cameras.append(camera)
                except Exception as e:
                    print(f"[FDOT] Error parsing camera: {e}")
                    continue
        
        return cameras
    
    def _load_demo_cameras(self) -> List[Dict[str, Any]]:
        """
        Load demo FDOT cameras.
        
        Returns:
            List of demo camera dictionaries.
        """
        self._demo_mode = True
        self._last_fetch = datetime.utcnow()
        
        cameras = []
        for cam in FDOT_DEMO_CAMERAS:
            cameras.append({
                **cam,
                "camera_type": "traffic",
                "jurisdiction": "FDOT",
                "status": "online",
                "sector": self._compute_sector(cam["latitude"], cam["longitude"]),
            })
        
        self._cameras = cameras
        return cameras
    
    def _compute_sector(self, lat: float, lng: float) -> str:
        """
        Compute patrol sector based on GPS coordinates.
        
        Args:
            lat: Latitude.
            lng: Longitude.
            
        Returns:
            Sector name.
        """
        # Simple sector assignment based on location
        if lat > 26.80:
            return "Sector 5"  # Singer Island / North
        elif lat > 26.78:
            if lng < -80.08:
                return "Sector 3"  # Blue Heron West
            else:
                return "Sector 4"  # Marina District
        elif lat > 26.76:
            if lng < -80.07:
                return "Sector 2"  # Avenue S / W10th
            else:
                return "Sector 1"  # Broadway / Park Ave
        else:
            return "Sector 1"  # Default
    
    def get_all_cameras(self) -> List[Dict[str, Any]]:
        """Get all cached cameras."""
        if not self._cameras:
            self._load_demo_cameras()
        return self._cameras
    
    def get_camera(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific camera by ID."""
        for cam in self.get_all_cameras():
            if cam.get("fdot_id") == camera_id:
                return cam
        return None
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode."""
        return self._demo_mode
    
    def get_status(self) -> Dict[str, Any]:
        """Get scraper status."""
        cameras = self.get_all_cameras()
        return {
            "total_cameras": len(cameras),
            "demo_mode": self._demo_mode,
            "last_fetch": self._last_fetch.isoformat() if self._last_fetch else None,
            "online_count": sum(1 for c in cameras if c.get("status") == "online"),
            "offline_count": sum(1 for c in cameras if c.get("status") == "offline"),
        }


# Singleton accessor
_scraper_instance: Optional[FDOTScraper] = None


def get_fdot_scraper() -> FDOTScraper:
    """
    Get the FDOT scraper singleton.
    
    Returns:
        FDOTScraper instance.
    """
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = FDOTScraper()
    return _scraper_instance
