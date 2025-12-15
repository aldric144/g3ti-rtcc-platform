"""
Camera Registry for G3TI RTCC-UIP Platform.

Central registry for ALL cameras in the system with full CRUD operations.
Stores camera metadata including location, stream URLs, type, jurisdiction, and status.
"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import math


class CameraType(str, Enum):
    """Camera type enumeration."""
    TRAFFIC = "traffic"
    CCTV = "cctv"
    LPR = "lpr"
    PTZ = "ptz"
    MARINE = "marine"
    PUBLIC = "public"
    BEACH = "beach"


class CameraJurisdiction(str, Enum):
    """Camera jurisdiction/ownership enumeration."""
    FDOT = "FDOT"
    RBPD = "RBPD"
    PBC = "PBC"  # Palm Beach County
    MANUAL = "Manual"
    PUBLIC = "Public"


class CameraStatus(str, Enum):
    """Camera operational status."""
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


# Source priority for conflict resolution (higher = more priority)
SOURCE_PRIORITY = {
    CameraJurisdiction.RBPD: 100,
    CameraJurisdiction.MANUAL: 80,
    CameraJurisdiction.PBC: 60,
    CameraJurisdiction.FDOT: 40,
    CameraJurisdiction.PUBLIC: 20,
}


@dataclass
class Camera:
    """
    Camera data class representing a single camera in the registry.
    """
    id: str
    name: str
    latitude: float
    longitude: float
    stream_url: str
    camera_type: CameraType
    jurisdiction: CameraJurisdiction
    address: str = ""
    sector: str = ""
    status: CameraStatus = CameraStatus.UNKNOWN
    last_ping: Optional[datetime] = None
    source_priority: int = 0
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set source priority based on jurisdiction."""
        if self.source_priority == 0:
            self.source_priority = SOURCE_PRIORITY.get(self.jurisdiction, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert camera to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "gps": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "stream_url": self.stream_url,
            "camera_type": self.camera_type.value if isinstance(self.camera_type, CameraType) else self.camera_type,
            "type": self.camera_type.value if isinstance(self.camera_type, CameraType) else self.camera_type,
            "jurisdiction": self.jurisdiction.value if isinstance(self.jurisdiction, CameraJurisdiction) else self.jurisdiction,
            "address": self.address,
            "sector": self.sector,
            "status": self.status.value if isinstance(self.status, CameraStatus) else self.status,
            "last_ping": self.last_ping.isoformat() if self.last_ping else None,
            "source_priority": self.source_priority,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Camera":
        """Create Camera from dictionary."""
        camera_type = data.get("camera_type") or data.get("type", "cctv")
        if isinstance(camera_type, str):
            try:
                camera_type = CameraType(camera_type.lower())
            except ValueError:
                camera_type = CameraType.CCTV
        
        jurisdiction = data.get("jurisdiction", "Manual")
        if isinstance(jurisdiction, str):
            try:
                jurisdiction = CameraJurisdiction(jurisdiction)
            except ValueError:
                jurisdiction = CameraJurisdiction.MANUAL
        
        status = data.get("status", "unknown")
        if isinstance(status, str):
            try:
                status = CameraStatus(status.lower())
            except ValueError:
                status = CameraStatus.UNKNOWN
        
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "Unknown Camera"),
            latitude=data.get("latitude") or data.get("gps", {}).get("latitude", 0.0),
            longitude=data.get("longitude") or data.get("gps", {}).get("longitude", 0.0),
            stream_url=data.get("stream_url", ""),
            camera_type=camera_type,
            jurisdiction=jurisdiction,
            address=data.get("address", ""),
            sector=data.get("sector", ""),
            status=status,
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )


class CameraRegistry:
    """
    Central camera registry with full CRUD operations.
    
    Singleton pattern ensures single source of truth for all cameras.
    """
    
    _instance: Optional["CameraRegistry"] = None
    
    def __new__(cls) -> "CameraRegistry":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the camera registry."""
        if self._initialized:
            return
        
        self._cameras: Dict[str, Camera] = {}
        self._initialized = True
    
    # ========================================================================
    # CRUD Operations
    # ========================================================================
    
    def add_camera(self, camera: Camera) -> Camera:
        """
        Add a camera to the registry.
        
        Args:
            camera: Camera object to add.
            
        Returns:
            The added camera.
        """
        camera.created_at = datetime.utcnow()
        camera.updated_at = datetime.utcnow()
        self._cameras[camera.id] = camera
        return camera
    
    def add_camera_from_dict(self, data: Dict[str, Any]) -> Camera:
        """
        Add a camera from dictionary data.
        
        Args:
            data: Camera data dictionary.
            
        Returns:
            The added camera.
        """
        if "id" not in data:
            data["id"] = str(uuid.uuid4())[:8]
        camera = Camera.from_dict(data)
        return self.add_camera(camera)
    
    def update_camera(self, camera_id: str, updates: Dict[str, Any]) -> Optional[Camera]:
        """
        Update an existing camera.
        
        Args:
            camera_id: ID of camera to update.
            updates: Dictionary of fields to update.
            
        Returns:
            Updated camera or None if not found.
        """
        if camera_id not in self._cameras:
            return None
        
        camera = self._cameras[camera_id]
        
        for key, value in updates.items():
            if hasattr(camera, key):
                if key == "camera_type" and isinstance(value, str):
                    try:
                        value = CameraType(value.lower())
                    except ValueError:
                        continue
                elif key == "jurisdiction" and isinstance(value, str):
                    try:
                        value = CameraJurisdiction(value)
                    except ValueError:
                        continue
                elif key == "status" and isinstance(value, str):
                    try:
                        value = CameraStatus(value.lower())
                    except ValueError:
                        continue
                setattr(camera, key, value)
        
        camera.updated_at = datetime.utcnow()
        return camera
    
    def delete_camera(self, camera_id: str) -> bool:
        """
        Delete a camera from the registry.
        
        Args:
            camera_id: ID of camera to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        if camera_id in self._cameras:
            del self._cameras[camera_id]
            return True
        return False
    
    def get_camera(self, camera_id: str) -> Optional[Camera]:
        """
        Get a camera by ID.
        
        Args:
            camera_id: Camera ID to retrieve.
            
        Returns:
            Camera object or None if not found.
        """
        return self._cameras.get(camera_id)
    
    # ========================================================================
    # List Operations
    # ========================================================================
    
    def list_all(self) -> List[Dict[str, Any]]:
        """Get all cameras as list of dictionaries."""
        return [cam.to_dict() for cam in self._cameras.values()]
    
    def list_by_sector(self, sector: str) -> List[Dict[str, Any]]:
        """Get cameras filtered by sector."""
        return [
            cam.to_dict() for cam in self._cameras.values()
            if cam.sector == sector
        ]
    
    def list_by_jurisdiction(self, jurisdiction: str) -> List[Dict[str, Any]]:
        """Get cameras filtered by jurisdiction."""
        try:
            jur = CameraJurisdiction(jurisdiction)
        except ValueError:
            return []
        
        return [
            cam.to_dict() for cam in self._cameras.values()
            if cam.jurisdiction == jur
        ]
    
    def list_by_type(self, camera_type: str) -> List[Dict[str, Any]]:
        """Get cameras filtered by type."""
        try:
            ct = CameraType(camera_type.lower())
        except ValueError:
            return []
        
        return [
            cam.to_dict() for cam in self._cameras.values()
            if cam.camera_type == ct
        ]
    
    def list_active_only(self) -> List[Dict[str, Any]]:
        """Get only online cameras."""
        return [
            cam.to_dict() for cam in self._cameras.values()
            if cam.status == CameraStatus.ONLINE
        ]
    
    def list_nearby(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
    ) -> List[Dict[str, Any]]:
        """
        Get cameras within radius of a point.
        
        Args:
            lat: Latitude of center point.
            lng: Longitude of center point.
            radius_km: Search radius in kilometers.
            
        Returns:
            List of cameras within radius, sorted by distance.
        """
        results = []
        
        for camera in self._cameras.values():
            distance = self._haversine_distance(
                lat, lng, camera.latitude, camera.longitude
            )
            if distance <= radius_km:
                cam_dict = camera.to_dict()
                cam_dict["distance_km"] = round(distance, 2)
                results.append(cam_dict)
        
        return sorted(results, key=lambda x: x["distance_km"])
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        cameras = list(self._cameras.values())
        
        by_jurisdiction = {}
        by_type = {}
        by_status = {}
        by_sector = {}
        
        for cam in cameras:
            # By jurisdiction
            jur = cam.jurisdiction.value if isinstance(cam.jurisdiction, CameraJurisdiction) else cam.jurisdiction
            by_jurisdiction[jur] = by_jurisdiction.get(jur, 0) + 1
            
            # By type
            ct = cam.camera_type.value if isinstance(cam.camera_type, CameraType) else cam.camera_type
            by_type[ct] = by_type.get(ct, 0) + 1
            
            # By status
            st = cam.status.value if isinstance(cam.status, CameraStatus) else cam.status
            by_status[st] = by_status.get(st, 0) + 1
            
            # By sector
            if cam.sector:
                by_sector[cam.sector] = by_sector.get(cam.sector, 0) + 1
        
        return {
            "total_cameras": len(cameras),
            "by_jurisdiction": by_jurisdiction,
            "by_type": by_type,
            "by_status": by_status,
            "by_sector": by_sector,
            "online_count": by_status.get("online", 0),
            "offline_count": by_status.get("offline", 0),
            "degraded_count": by_status.get("degraded", 0),
        }
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate distance between two GPS coordinates in kilometers."""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def clear(self):
        """Clear all cameras from registry."""
        self._cameras.clear()
    
    def count(self) -> int:
        """Get total camera count."""
        return len(self._cameras)


# Singleton accessor
_registry_instance: Optional[CameraRegistry] = None


def get_camera_registry() -> CameraRegistry:
    """
    Get the camera registry singleton.
    
    Returns:
        CameraRegistry instance.
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = CameraRegistry()
    return _registry_instance
