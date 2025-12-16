"""
System Settings Admin Module - CRUD operations for system configuration
Tab 15: System Settings
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService


class MapStyle(str, Enum):
    DARK = "dark"
    LIGHT = "light"
    SATELLITE = "satellite"
    STREETS = "streets"
    TACTICAL = "tactical"


class SystemSettingsModel(BaseAdminModel):
    """System Settings database model"""
    setting_key: str = Field(..., min_length=1, max_length=100)
    setting_value: str = Field(..., max_length=5000)
    category: str = Field(default="general", max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_sensitive: bool = Field(default=False)
    requires_restart: bool = Field(default=False)


class SystemSettingsCreate(BaseAdminCreate):
    """Schema for creating a system setting"""
    setting_key: str = Field(..., min_length=1, max_length=100)
    setting_value: str = Field(..., max_length=5000)
    category: str = Field(default="general", max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_sensitive: bool = Field(default=False)
    requires_restart: bool = Field(default=False)


class SystemSettingsUpdate(BaseAdminUpdate):
    """Schema for updating a system setting"""
    setting_value: Optional[str] = Field(None, max_length=5000)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_sensitive: Optional[bool] = None
    requires_restart: Optional[bool] = None


class VideoWallConfig(BaseModel):
    """Video wall configuration"""
    layout: str = Field(default="2x2")  # 2x2, 3x3, 4x4, custom
    default_cameras: List[str] = Field(default_factory=list)
    rotation_interval: int = Field(default=30, ge=5, le=300)
    show_labels: bool = Field(default=True)
    show_timestamps: bool = Field(default=True)


class AlertThresholds(BaseModel):
    """Alert threshold configuration"""
    gunshot_confidence: float = Field(default=0.8, ge=0, le=1)
    lpr_alert_priority: str = Field(default="high")
    incident_auto_escalate_minutes: int = Field(default=30, ge=5)
    camera_offline_alert_minutes: int = Field(default=5, ge=1)


class SystemSettingsAdmin(BaseAdminService[SystemSettingsModel, SystemSettingsCreate, SystemSettingsUpdate]):
    """System Settings admin service with CRUD operations"""
    
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
        """Initialize with default system settings"""
        default_settings = [
            # Map Settings
            {
                "setting_key": "map.default_style",
                "setting_value": MapStyle.TACTICAL.value,
                "category": "map",
                "description": "Default map style for the platform",
            },
            {
                "setting_key": "map.default_center_lat",
                "setting_value": "26.7753",
                "category": "map",
                "description": "Default map center latitude",
            },
            {
                "setting_key": "map.default_center_lng",
                "setting_value": "-80.0569",
                "category": "map",
                "description": "Default map center longitude",
            },
            {
                "setting_key": "map.default_zoom",
                "setting_value": "14",
                "category": "map",
                "description": "Default map zoom level",
            },
            # Alert Thresholds
            {
                "setting_key": "alerts.gunshot_confidence",
                "setting_value": "0.8",
                "category": "alerts",
                "description": "Minimum confidence for gunshot alerts",
            },
            {
                "setting_key": "alerts.lpr_priority",
                "setting_value": "high",
                "category": "alerts",
                "description": "Default priority for LPR alerts",
            },
            {
                "setting_key": "alerts.incident_escalate_minutes",
                "setting_value": "30",
                "category": "alerts",
                "description": "Minutes before auto-escalating unacknowledged incidents",
            },
            {
                "setting_key": "alerts.camera_offline_minutes",
                "setting_value": "5",
                "category": "alerts",
                "description": "Minutes before alerting on offline cameras",
            },
            # Refresh Rates
            {
                "setting_key": "refresh.dashboard_seconds",
                "setting_value": "30",
                "category": "refresh",
                "description": "Dashboard refresh interval in seconds",
            },
            {
                "setting_key": "refresh.map_seconds",
                "setting_value": "10",
                "category": "refresh",
                "description": "Map refresh interval in seconds",
            },
            {
                "setting_key": "refresh.cameras_seconds",
                "setting_value": "5",
                "category": "refresh",
                "description": "Camera status refresh interval in seconds",
            },
            # Video Wall
            {
                "setting_key": "videowall.default_layout",
                "setting_value": "2x2",
                "category": "videowall",
                "description": "Default video wall layout",
            },
            {
                "setting_key": "videowall.rotation_seconds",
                "setting_value": "30",
                "category": "videowall",
                "description": "Camera rotation interval in seconds",
            },
            {
                "setting_key": "videowall.show_labels",
                "setting_value": "true",
                "category": "videowall",
                "description": "Show camera labels on video wall",
            },
            # Security
            {
                "setting_key": "security.session_timeout_minutes",
                "setting_value": "30",
                "category": "security",
                "description": "Session timeout in minutes",
                "requires_restart": True,
            },
            {
                "setting_key": "security.max_login_attempts",
                "setting_value": "5",
                "category": "security",
                "description": "Maximum failed login attempts before lockout",
            },
            {
                "setting_key": "security.lockout_minutes",
                "setting_value": "30",
                "category": "security",
                "description": "Account lockout duration in minutes",
            },
            # System
            {
                "setting_key": "system.agency_name",
                "setting_value": "Riviera Beach Police Department",
                "category": "system",
                "description": "Agency name displayed in the platform",
            },
            {
                "setting_key": "system.rtcc_name",
                "setting_value": "Real Time Crime Center",
                "category": "system",
                "description": "RTCC name displayed in the platform",
            },
            {
                "setting_key": "system.timezone",
                "setting_value": "America/New_York",
                "category": "system",
                "description": "System timezone",
                "requires_restart": True,
            },
        ]
        
        for setting_data in default_settings:
            setting = SystemSettingsModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **setting_data
            )
            self._storage[setting.id] = setting
    
    async def create(self, data: SystemSettingsCreate, user_id: str) -> SystemSettingsModel:
        """Create a new system setting"""
        # Check for duplicate key
        for existing in self._storage.values():
            if existing.setting_key == data.setting_key:
                raise ValueError(f"Setting key '{data.setting_key}' already exists")
        
        setting = SystemSettingsModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[setting.id] = setting
        return setting
    
    async def update(self, item_id: str, data: SystemSettingsUpdate, user_id: str) -> Optional[SystemSettingsModel]:
        """Update an existing system setting"""
        setting = self._storage.get(item_id)
        if not setting:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(setting, key, value)
        
        setting.updated_at = datetime.now(UTC)
        setting.updated_by = user_id
        self._storage[item_id] = setting
        return setting
    
    async def get_by_key(self, key: str) -> Optional[SystemSettingsModel]:
        """Get setting by key"""
        for setting in self._storage.values():
            if setting.setting_key == key:
                return setting
        return None
    
    async def get_by_category(self, category: str) -> List[SystemSettingsModel]:
        """Get all settings in a category"""
        return [s for s in self._storage.values() if s.category == category]
    
    async def get_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get setting value by key"""
        setting = await self.get_by_key(key)
        return setting.setting_value if setting else default
    
    async def set_value(self, key: str, value: str, user_id: str) -> Optional[SystemSettingsModel]:
        """Set setting value by key"""
        setting = await self.get_by_key(key)
        if not setting:
            return None
        
        setting.setting_value = value
        setting.updated_at = datetime.now(UTC)
        setting.updated_by = user_id
        self._storage[setting.id] = setting
        return setting
    
    async def get_video_wall_config(self) -> VideoWallConfig:
        """Get video wall configuration"""
        layout = await self.get_value("videowall.default_layout", "2x2")
        rotation = await self.get_value("videowall.rotation_seconds", "30")
        show_labels = await self.get_value("videowall.show_labels", "true")
        
        return VideoWallConfig(
            layout=layout,
            rotation_interval=int(rotation),
            show_labels=show_labels.lower() == "true",
        )
    
    async def get_alert_thresholds(self) -> AlertThresholds:
        """Get alert threshold configuration"""
        gunshot = await self.get_value("alerts.gunshot_confidence", "0.8")
        lpr = await self.get_value("alerts.lpr_priority", "high")
        escalate = await self.get_value("alerts.incident_escalate_minutes", "30")
        offline = await self.get_value("alerts.camera_offline_minutes", "5")
        
        return AlertThresholds(
            gunshot_confidence=float(gunshot),
            lpr_alert_priority=lpr,
            incident_auto_escalate_minutes=int(escalate),
            camera_offline_alert_minutes=int(offline),
        )


# Singleton instance
system_settings_admin = SystemSettingsAdmin()
