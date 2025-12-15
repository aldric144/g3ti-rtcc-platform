"""
Camera Ingestion Engine for G3TI RTCC-UIP Platform.

This module provides a unified camera ingestion system that aggregates
cameras from multiple sources with proper priority ordering:

1. RBPD mock cameras (highest priority)
2. Manual admin cameras
3. FDOT cameras
4. Public cameras (lowest priority)

The engine ensures no duplicate cameras and maintains consistent
metadata across all sources.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


# Import camera loaders
from app.cameras.rbpd_mock_loader import (
    load_rbpd_mock_cameras,
    get_cached_rbpd_cameras,
)
from app.cameras.fdot_scraper import (
    get_fdot_scraper,
)
from app.cameras.public_camera_catalog import (
    get_public_camera_catalog,
)


class CameraIngestionEngine:
    """
    Unified camera ingestion engine.
    
    Aggregates cameras from multiple sources with priority ordering:
    1. RBPD mock cameras (highest priority)
    2. Manual admin cameras
    3. FDOT cameras
    4. Public cameras (lowest priority)
    """
    
    _instance: Optional["CameraIngestionEngine"] = None
    
    def __new__(cls) -> "CameraIngestionEngine":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the camera ingestion engine."""
        if self._initialized:
            return
        
        self._manual_cameras: List[Dict[str, Any]] = []
        self._last_refresh: Optional[datetime] = None
        self._initialized = True
    
    def add_manual_camera(self, camera: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a manually configured camera.
        
        Args:
            camera: Camera dictionary with required fields.
            
        Returns:
            The added camera with generated ID if not provided.
        """
        import uuid
        
        if "id" not in camera:
            camera["id"] = str(uuid.uuid4())[:8]
        
        camera["source"] = "manual_admin"
        camera["created_at"] = datetime.utcnow().isoformat()
        
        self._manual_cameras.append(camera)
        return camera
    
    def remove_manual_camera(self, camera_id: str) -> bool:
        """
        Remove a manually configured camera.
        
        Args:
            camera_id: The ID of the camera to remove.
            
        Returns:
            True if camera was removed, False if not found.
        """
        for i, camera in enumerate(self._manual_cameras):
            if camera.get("id") == camera_id:
                self._manual_cameras.pop(i)
                return True
        return False
    
    def get_manual_cameras(self) -> List[Dict[str, Any]]:
        """Get all manually configured cameras."""
        return self._manual_cameras.copy()
    
    def get_rbpd_cameras(self) -> List[Dict[str, Any]]:
        """Get all RBPD mock cameras (highest priority)."""
        return get_cached_rbpd_cameras()
    
    def get_fdot_cameras(self) -> List[Dict[str, Any]]:
        """Get all FDOT cameras."""
        try:
            scraper = get_fdot_scraper()
            return scraper.get_all_cameras()
        except Exception as e:
            print(f"[INGESTION] Failed to load FDOT cameras: {e}")
            return []
    
    def get_public_cameras(self) -> List[Dict[str, Any]]:
        """Get all public cameras (lowest priority)."""
        try:
            catalog = get_public_camera_catalog()
            return catalog.get_all_cameras()
        except Exception as e:
            print(f"[INGESTION] Failed to load public cameras: {e}")
            return []
    
    def get_all_cameras(
        self,
        include_rbpd: bool = True,
        include_manual: bool = True,
        include_fdot: bool = True,
        include_public: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get all cameras from all sources with priority ordering.
        
        Priority order (highest to lowest):
        1. RBPD mock cameras
        2. Manual admin cameras
        3. FDOT cameras
        4. Public cameras
        
        Args:
            include_rbpd: Include RBPD mock cameras.
            include_manual: Include manually added cameras.
            include_fdot: Include FDOT cameras.
            include_public: Include public cameras.
            
        Returns:
            List of all cameras from enabled sources.
        """
        all_cameras = []
        seen_ids = set()
        
        # 1. RBPD mock cameras (highest priority)
        if include_rbpd:
            for camera in self.get_rbpd_cameras():
                cam_id = camera.get("id")
                if cam_id and cam_id not in seen_ids:
                    all_cameras.append(camera)
                    seen_ids.add(cam_id)
        
        # 2. Manual admin cameras
        if include_manual:
            for camera in self.get_manual_cameras():
                cam_id = camera.get("id")
                if cam_id and cam_id not in seen_ids:
                    all_cameras.append(camera)
                    seen_ids.add(cam_id)
        
        # 3. FDOT cameras
        if include_fdot:
            for camera in self.get_fdot_cameras():
                cam_id = camera.get("fdot_id") or camera.get("id")
                if cam_id and cam_id not in seen_ids:
                    all_cameras.append(camera)
                    seen_ids.add(cam_id)
        
        # 4. Public cameras (lowest priority)
        if include_public:
            for camera in self.get_public_cameras():
                cam_id = camera.get("id")
                if cam_id and cam_id not in seen_ids:
                    all_cameras.append(camera)
                    seen_ids.add(cam_id)
        
        self._last_refresh = datetime.utcnow()
        return all_cameras
    
    def get_cameras_by_sector(self, sector: str) -> List[Dict[str, Any]]:
        """
        Get all cameras in a specific sector.
        
        Args:
            sector: Sector name to filter by.
            
        Returns:
            List of cameras in the specified sector.
        """
        all_cameras = self.get_all_cameras()
        return [
            c for c in all_cameras
            if c.get("sector") == sector or c.get("assigned_sector") == sector
        ]
    
    def get_cameras_by_source(self, source: str) -> List[Dict[str, Any]]:
        """
        Get all cameras from a specific source.
        
        Args:
            source: Source name to filter by.
            
        Returns:
            List of cameras from the specified source.
        """
        all_cameras = self.get_all_cameras()
        return [c for c in all_cameras if c.get("source") == source]
    
    def get_camera_stats(self) -> Dict[str, Any]:
        """
        Get statistics about all ingested cameras.
        
        Returns:
            Dictionary with camera statistics.
        """
        rbpd = self.get_rbpd_cameras()
        manual = self.get_manual_cameras()
        fdot = self.get_fdot_cameras()
        public = self.get_public_cameras()
        
        all_cameras = self.get_all_cameras()
        
        # Count by sector
        sectors = {}
        for camera in all_cameras:
            sector = camera.get("sector") or camera.get("assigned_sector") or "Unknown"
            sectors[sector] = sectors.get(sector, 0) + 1
        
        # Count by type
        types = {}
        for camera in all_cameras:
            cam_type = camera.get("type") or camera.get("camera_type") or "Unknown"
            types[cam_type] = types.get(cam_type, 0) + 1
        
        return {
            "total_cameras": len(all_cameras),
            "by_source": {
                "rbpd_mock": len(rbpd),
                "manual_admin": len(manual),
                "fdot": len(fdot),
                "public": len(public),
            },
            "by_sector": sectors,
            "by_type": types,
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None,
        }
    
    def refresh(self) -> Dict[str, Any]:
        """
        Refresh all camera sources.
        
        Returns:
            Statistics after refresh.
        """
        # Force refresh of all sources
        from app.cameras.rbpd_mock_loader import refresh_rbpd_cameras
        refresh_rbpd_cameras()
        
        try:
            scraper = get_fdot_scraper()
            scraper.refresh_cameras()
        except Exception as e:
            print(f"[INGESTION] Failed to refresh FDOT cameras: {e}")
        
        self._last_refresh = datetime.utcnow()
        return self.get_camera_stats()


# Singleton accessor
_engine_instance: Optional[CameraIngestionEngine] = None


def get_camera_ingestion_engine() -> CameraIngestionEngine:
    """
    Get the camera ingestion engine singleton.
    
    Returns:
        CameraIngestionEngine instance.
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = CameraIngestionEngine()
    return _engine_instance
