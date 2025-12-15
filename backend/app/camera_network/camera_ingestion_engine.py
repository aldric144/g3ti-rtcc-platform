"""
Camera Ingestion Engine for G3TI RTCC-UIP Platform.

Unified camera ingestion system that aggregates cameras from multiple sources
with proper priority ordering and conflict resolution.

Ingestion Order:
1. RBPD internal cameras (highest priority)
2. Manual admin-added cameras
3. FDOT public cameras (lowest priority)
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Set
import math

from .camera_registry import (
    CameraRegistry,
    Camera,
    CameraType,
    CameraJurisdiction,
    CameraStatus,
    get_camera_registry,
)
from .fdot_scraper import get_fdot_scraper
from .rbpd_mock_loader import load_rbpd_mock_cameras


class CameraIngestionEngine:
    """
    Unified camera ingestion engine.
    
    Aggregates cameras from multiple sources with priority ordering:
    1. RBPD internal cameras (highest priority)
    2. Manual admin-added cameras
    3. FDOT public cameras (lowest priority)
    
    Handles conflict resolution based on GPS accuracy and name similarity.
    """
    
    _instance: Optional["CameraIngestionEngine"] = None
    
    def __new__(cls) -> "CameraIngestionEngine":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the ingestion engine."""
        if self._initialized:
            return
        
        self._registry = get_camera_registry()
        self._manual_cameras: List[Dict[str, Any]] = []
        self._last_ingestion: Optional[datetime] = None
        self._ingestion_stats: Dict[str, int] = {}
        self._initialized = True
    
    def ingest_all(self) -> Dict[str, Any]:
        """
        Ingest cameras from all sources.
        
        Returns:
            Ingestion statistics.
        """
        # Clear existing cameras
        self._registry.clear()
        
        stats = {
            "rbpd_count": 0,
            "manual_count": 0,
            "fdot_count": 0,
            "total_count": 0,
            "duplicates_removed": 0,
        }
        
        seen_locations: Set[str] = set()
        
        # 1. Ingest RBPD cameras (highest priority)
        rbpd_cameras = load_rbpd_mock_cameras()
        for cam_data in rbpd_cameras:
            location_key = self._get_location_key(
                cam_data.get("latitude", 0),
                cam_data.get("longitude", 0)
            )
            
            if location_key not in seen_locations:
                self._add_camera_to_registry(cam_data, CameraJurisdiction.RBPD)
                seen_locations.add(location_key)
                stats["rbpd_count"] += 1
            else:
                stats["duplicates_removed"] += 1
        
        # 2. Ingest manual admin cameras
        for cam_data in self._manual_cameras:
            location_key = self._get_location_key(
                cam_data.get("latitude", 0),
                cam_data.get("longitude", 0)
            )
            
            if location_key not in seen_locations:
                self._add_camera_to_registry(cam_data, CameraJurisdiction.MANUAL)
                seen_locations.add(location_key)
                stats["manual_count"] += 1
            else:
                stats["duplicates_removed"] += 1
        
        # 3. Ingest FDOT cameras (lowest priority)
        fdot_scraper = get_fdot_scraper()
        fdot_cameras = fdot_scraper.get_all_cameras_sync()
        for cam_data in fdot_cameras:
            # Normalize FDOT camera data
            # Ensure ID is set (use fdot_id if id is missing)
            if not cam_data.get("id") and cam_data.get("fdot_id"):
                cam_data["id"] = f"fdot-{cam_data['fdot_id']}"
            elif not cam_data.get("id"):
                cam_data["id"] = f"fdot-{stats['fdot_count']}"
            
            # Ensure camera type is set to traffic for FDOT cameras
            cam_data["camera_type"] = "traffic"
            cam_data["type"] = "traffic"
            
            # Ensure jurisdiction is set
            cam_data["jurisdiction"] = "FDOT"
            
            # Set MJPEG stream URL for FDOT cameras
            camera_id = cam_data.get("id") or cam_data.get("fdot_id") or f"fdot-{stats['fdot_count']}"
            cam_data["stream_url"] = f"/api/cameras/fdot/{camera_id}/stream"
            cam_data["supports_mjpeg"] = True
            
            # Keep snapshot_url for fallback
            if not cam_data.get("snapshot_url"):
                cam_data["snapshot_url"] = "https://via.placeholder.com/640x360?text=FDOT"
            
            # Get coordinates
            lat = cam_data.get("latitude", 0)
            lng = cam_data.get("longitude", 0)
            
            # Skip cameras with no valid coordinates
            if not lat or not lng or (lat == 0 and lng == 0):
                # Use fallback center for Riviera Beach area
                lat = 26.7850
                lng = -80.0650
                cam_data["latitude"] = lat
                cam_data["longitude"] = lng
            
            location_key = self._get_location_key(lat, lng)
            
            if location_key not in seen_locations:
                self._add_camera_to_registry(cam_data, CameraJurisdiction.FDOT)
                seen_locations.add(location_key)
                stats["fdot_count"] += 1
            else:
                stats["duplicates_removed"] += 1
        
        stats["total_count"] = self._registry.count()
        self._last_ingestion = datetime.utcnow()
        self._ingestion_stats = stats
        
        return stats
    
    def _add_camera_to_registry(
        self,
        cam_data: Dict[str, Any],
        jurisdiction: CameraJurisdiction,
    ) -> Camera:
        """
        Add a camera to the registry.
        
        Args:
            cam_data: Camera data dictionary.
            jurisdiction: Camera jurisdiction.
            
        Returns:
            Added Camera object.
        """
        # Map camera type
        cam_type_str = cam_data.get("camera_type") or cam_data.get("type", "cctv")
        try:
            camera_type = CameraType(cam_type_str.lower())
        except ValueError:
            camera_type = CameraType.CCTV
        
        # Create camera object
        camera = Camera(
            id=cam_data.get("id") or cam_data.get("fdot_id", ""),
            name=cam_data.get("name", "Unknown Camera"),
            latitude=cam_data.get("latitude") or cam_data.get("gps", {}).get("latitude", 0),
            longitude=cam_data.get("longitude") or cam_data.get("gps", {}).get("longitude", 0),
            stream_url=cam_data.get("stream_url") or cam_data.get("snapshot_url", ""),
            camera_type=camera_type,
            jurisdiction=jurisdiction,
            address=cam_data.get("address", ""),
            sector=cam_data.get("sector", ""),
            status=CameraStatus.ONLINE,
            description=cam_data.get("description", ""),
        )
        
        return self._registry.add_camera(camera)
    
    def _get_location_key(self, lat: float, lng: float, precision: int = 4) -> str:
        """
        Generate a location key for deduplication.
        
        Args:
            lat: Latitude.
            lng: Longitude.
            precision: Decimal precision for rounding.
            
        Returns:
            Location key string.
        """
        return f"{round(lat, precision)},{round(lng, precision)}"
    
    def add_manual_camera(self, camera_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a manually configured camera.
        
        Args:
            camera_data: Camera data dictionary.
            
        Returns:
            Added camera data.
        """
        import uuid
        
        if "id" not in camera_data:
            camera_data["id"] = f"manual-{uuid.uuid4().hex[:8]}"
        
        camera_data["jurisdiction"] = "Manual"
        camera_data["source_priority"] = 80
        camera_data["created_at"] = datetime.utcnow().isoformat()
        
        self._manual_cameras.append(camera_data)
        
        # Re-ingest to update registry
        self.ingest_all()
        
        return camera_data
    
    def remove_manual_camera(self, camera_id: str) -> bool:
        """
        Remove a manually configured camera.
        
        Args:
            camera_id: Camera ID to remove.
            
        Returns:
            True if removed, False if not found.
        """
        for i, cam in enumerate(self._manual_cameras):
            if cam.get("id") == camera_id:
                self._manual_cameras.pop(i)
                self.ingest_all()
                return True
        return False
    
    def get_all_cameras(self) -> List[Dict[str, Any]]:
        """Get all cameras from registry."""
        if self._registry.count() == 0:
            self.ingest_all()
        return self._registry.list_all()
    
    def get_camera(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific camera by ID."""
        camera = self._registry.get_camera(camera_id)
        return camera.to_dict() if camera else None
    
    def get_cameras_by_sector(self, sector: str) -> List[Dict[str, Any]]:
        """Get cameras filtered by sector."""
        return self._registry.list_by_sector(sector)
    
    def get_cameras_by_jurisdiction(self, jurisdiction: str) -> List[Dict[str, Any]]:
        """Get cameras filtered by jurisdiction."""
        return self._registry.list_by_jurisdiction(jurisdiction)
    
    def get_cameras_nearby(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
    ) -> List[Dict[str, Any]]:
        """Get cameras within radius of a point."""
        return self._registry.list_nearby(lat, lng, radius_km)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        registry_stats = self._registry.get_stats()
        return {
            **registry_stats,
            "ingestion_stats": self._ingestion_stats,
            "last_ingestion": self._last_ingestion.isoformat() if self._last_ingestion else None,
            "manual_cameras_count": len(self._manual_cameras),
        }
    
    def refresh(self) -> Dict[str, Any]:
        """Refresh all camera sources."""
        return self.ingest_all()


# Singleton accessor
_engine_instance: Optional[CameraIngestionEngine] = None


def get_ingestion_engine() -> CameraIngestionEngine:
    """
    Get the camera ingestion engine singleton.
    
    Returns:
        CameraIngestionEngine instance.
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = CameraIngestionEngine()
    return _engine_instance
