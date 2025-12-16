"""
LPR Zones Admin Module - CRUD operations for LPR zone management
Tab 4: LPR Zones
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint, GeoPolygon


class AlertSensitivity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LPRZoneModel(BaseAdminModel):
    """LPR Zone database model"""
    zone_name: str = Field(..., min_length=1, max_length=200)
    boundary: List[GeoPoint] = Field(..., min_length=3)
    camera_ids: List[str] = Field(default_factory=list)
    bolo_rules: Optional[str] = Field(None, max_length=2000)
    alert_sensitivity: AlertSensitivity = Field(default=AlertSensitivity.MEDIUM)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('boundary')
    @classmethod
    def validate_boundary(cls, v: List[GeoPoint]) -> List[GeoPoint]:
        if len(v) < 3:
            raise ValueError('Boundary must have at least 3 points')
        return v


class LPRZoneCreate(BaseAdminCreate):
    """Schema for creating an LPR zone"""
    zone_name: str = Field(..., min_length=1, max_length=200)
    boundary: List[GeoPoint] = Field(..., min_length=3)
    camera_ids: List[str] = Field(default_factory=list)
    bolo_rules: Optional[str] = Field(None, max_length=2000)
    alert_sensitivity: AlertSensitivity = Field(default=AlertSensitivity.MEDIUM)
    notes: Optional[str] = Field(None, max_length=2000)


class LPRZoneUpdate(BaseAdminUpdate):
    """Schema for updating an LPR zone"""
    zone_name: Optional[str] = Field(None, min_length=1, max_length=200)
    boundary: Optional[List[GeoPoint]] = None
    camera_ids: Optional[List[str]] = None
    bolo_rules: Optional[str] = Field(None, max_length=2000)
    alert_sensitivity: Optional[AlertSensitivity] = None
    notes: Optional[str] = Field(None, max_length=2000)


class LPRZoneAdmin(BaseAdminService[LPRZoneModel, LPRZoneCreate, LPRZoneUpdate]):
    """LPR Zone admin service with CRUD operations"""
    
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
        """Initialize with demo LPR zone data"""
        demo_zones = [
            {
                "zone_name": "Downtown Entry Zone",
                "boundary": [
                    GeoPoint(lat=26.7750, lng=-80.0580),
                    GeoPoint(lat=26.7760, lng=-80.0550),
                    GeoPoint(lat=26.7740, lng=-80.0540),
                    GeoPoint(lat=26.7730, lng=-80.0570),
                    GeoPoint(lat=26.7750, lng=-80.0580),
                ],
                "camera_ids": ["cam-001", "cam-002"],
                "alert_sensitivity": AlertSensitivity.HIGH,
            },
        ]
        
        for zone_data in demo_zones:
            zone = LPRZoneModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **zone_data
            )
            self._storage[zone.id] = zone
    
    async def create(self, data: LPRZoneCreate, user_id: str) -> LPRZoneModel:
        """Create a new LPR zone"""
        zone = LPRZoneModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[zone.id] = zone
        return zone
    
    async def update(self, item_id: str, data: LPRZoneUpdate, user_id: str) -> Optional[LPRZoneModel]:
        """Update an existing LPR zone"""
        zone = self._storage.get(item_id)
        if not zone:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(zone, key, value)
        
        zone.updated_at = datetime.now(UTC)
        zone.updated_by = user_id
        self._storage[item_id] = zone
        return zone
    
    async def add_camera(self, zone_id: str, camera_id: str) -> Optional[LPRZoneModel]:
        """Add a camera to an LPR zone"""
        zone = self._storage.get(zone_id)
        if not zone:
            return None
        
        if camera_id not in zone.camera_ids:
            zone.camera_ids.append(camera_id)
            self._storage[zone_id] = zone
        return zone
    
    async def remove_camera(self, zone_id: str, camera_id: str) -> Optional[LPRZoneModel]:
        """Remove a camera from an LPR zone"""
        zone = self._storage.get(zone_id)
        if not zone:
            return None
        
        if camera_id in zone.camera_ids:
            zone.camera_ids.remove(camera_id)
            self._storage[zone_id] = zone
        return zone


# Singleton instance
lpr_zone_admin = LPRZoneAdmin()
