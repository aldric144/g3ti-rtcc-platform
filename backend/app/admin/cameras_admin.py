"""
Camera Admin Module - CRUD operations for camera management
Tab 1: Camera Admin
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
import re

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint


class CameraType(str, Enum):
    TRAFFIC = "traffic"
    CCTV = "cctv"
    LPR = "lpr"
    PTZ = "ptz"
    MARINE = "marine"
    TACTICAL = "tactical"
    FDOT = "fdot"
    RBPD = "rbpd"


class CameraStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class CameraModel(BaseAdminModel):
    """Camera database model"""
    name: str = Field(..., min_length=1, max_length=200)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=500)
    camera_type: CameraType = Field(default=CameraType.CCTV)
    jurisdiction: Optional[str] = Field(None, max_length=100)
    sector: Optional[str] = Field(None, max_length=50)
    stream_url: Optional[str] = Field(None, max_length=1000)
    fallback_url: Optional[str] = Field(None, max_length=1000)
    status: CameraStatus = Field(default=CameraStatus.UNKNOWN)
    notes: Optional[str] = Field(None, max_length=2000)
    thumbnail_url: Optional[str] = None
    last_health_check: Optional[datetime] = None
    health_status: Optional[str] = None


class CameraCreate(BaseAdminCreate):
    """Schema for creating a camera"""
    name: str = Field(..., min_length=1, max_length=200)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=500)
    camera_type: CameraType = Field(default=CameraType.CCTV)
    jurisdiction: Optional[str] = Field(None, max_length=100)
    sector: Optional[str] = Field(None, max_length=50)
    stream_url: Optional[str] = Field(None, max_length=1000)
    fallback_url: Optional[str] = Field(None, max_length=1000)
    status: CameraStatus = Field(default=CameraStatus.UNKNOWN)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('stream_url', 'fallback_url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Validate RTSP or HTTP URL
        url_pattern = r'^(rtsp|http|https)://[^\s]+$'
        if not re.match(url_pattern, v):
            raise ValueError('Invalid URL format. Must be rtsp://, http://, or https://')
        return v


class CameraUpdate(BaseAdminUpdate):
    """Schema for updating a camera"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=500)
    camera_type: Optional[CameraType] = None
    jurisdiction: Optional[str] = Field(None, max_length=100)
    sector: Optional[str] = Field(None, max_length=50)
    stream_url: Optional[str] = Field(None, max_length=1000)
    fallback_url: Optional[str] = Field(None, max_length=1000)
    status: Optional[CameraStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('stream_url', 'fallback_url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        url_pattern = r'^(rtsp|http|https)://[^\s]+$'
        if not re.match(url_pattern, v):
            raise ValueError('Invalid URL format. Must be rtsp://, http://, or https://')
        return v


class CameraAdmin(BaseAdminService[CameraModel, CameraCreate, CameraUpdate]):
    """Camera admin service with CRUD operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize with demo camera data"""
        demo_cameras = [
            {
                "name": "FDOT I-95 @ Blue Heron Blvd",
                "lat": 26.7765,
                "lng": -80.0558,
                "camera_type": CameraType.FDOT,
                "jurisdiction": "FDOT",
                "sector": "SECTOR-1",
                "status": CameraStatus.ONLINE,
                "stream_url": "https://fl511.com/cameras/fdot/i95-blue-heron"
            },
            {
                "name": "RBPD City Hall",
                "lat": 26.7753,
                "lng": -80.0569,
                "camera_type": CameraType.CCTV,
                "jurisdiction": "RBPD",
                "sector": "SECTOR-1",
                "status": CameraStatus.ONLINE,
            },
            {
                "name": "Marina LPR Entry",
                "lat": 26.7801,
                "lng": -80.0512,
                "camera_type": CameraType.LPR,
                "jurisdiction": "RBPD",
                "sector": "SECTOR-2",
                "status": CameraStatus.ONLINE,
            },
        ]
        
        for cam_data in demo_cameras:
            camera = CameraModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **cam_data
            )
            self._storage[camera.id] = camera
    
    async def create(self, data: CameraCreate, user_id: str) -> CameraModel:
        """Create a new camera"""
        camera = CameraModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[camera.id] = camera
        return camera
    
    async def update(self, item_id: str, data: CameraUpdate, user_id: str) -> Optional[CameraModel]:
        """Update an existing camera"""
        camera = self._storage.get(item_id)
        if not camera:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(camera, key, value)
        
        camera.updated_at = datetime.now(UTC)
        camera.updated_by = user_id
        self._storage[item_id] = camera
        return camera
    
    async def check_camera_health(self, camera_id: str) -> Dict[str, Any]:
        """Check camera stream health"""
        camera = self._storage.get(camera_id)
        if not camera:
            return {"error": "Camera not found"}
        
        # Simulate health check
        health_result = {
            "camera_id": camera_id,
            "stream_url": camera.stream_url,
            "status": "healthy" if camera.status == CameraStatus.ONLINE else "unhealthy",
            "latency_ms": 45,
            "checked_at": datetime.now(UTC).isoformat()
        }
        
        camera.last_health_check = datetime.now(UTC)
        camera.health_status = health_result["status"]
        self._storage[camera_id] = camera
        
        return health_result
    
    async def auto_assign_sector(self, lat: float, lng: float) -> Optional[str]:
        """Auto-assign sector based on GPS coordinates"""
        # This would integrate with sectors_admin to find nearest sector
        # For now, return a default sector
        return "SECTOR-1"
    
    async def get_by_sector(self, sector: str) -> List[CameraModel]:
        """Get all cameras in a sector"""
        return [cam for cam in self._storage.values() if cam.sector == sector]
    
    async def get_by_type(self, camera_type: CameraType) -> List[CameraModel]:
        """Get all cameras of a specific type"""
        return [cam for cam in self._storage.values() if cam.camera_type == camera_type]


# Singleton instance
camera_admin = CameraAdmin()
