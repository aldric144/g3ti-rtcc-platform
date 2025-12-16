"""
Robot Admin Module - CRUD operations for quadruped robot management
Tab 3: Quadruped Robot Admin
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint, GeoPolygon


class RobotStatus(str, Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    MAINTENANCE = "maintenance"
    DEPLOYED = "deployed"
    OFFLINE = "offline"
    CHARGING = "charging"


class RobotModel(BaseAdminModel):
    """Robot database model"""
    robot_id: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=100)
    serial: str = Field(..., min_length=1, max_length=100)
    assigned_unit: Optional[str] = Field(None, max_length=100)
    patrol_area: Optional[List[GeoPoint]] = None
    stream_url: Optional[str] = Field(None, max_length=1000)
    status: RobotStatus = Field(default=RobotStatus.STANDBY)
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    last_telemetry: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)


class RobotCreate(BaseAdminCreate):
    """Schema for creating a robot"""
    robot_id: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=100)
    serial: str = Field(..., min_length=1, max_length=100)
    assigned_unit: Optional[str] = Field(None, max_length=100)
    patrol_area: Optional[List[GeoPoint]] = None
    stream_url: Optional[str] = Field(None, max_length=1000)
    status: RobotStatus = Field(default=RobotStatus.STANDBY)
    notes: Optional[str] = Field(None, max_length=2000)


class RobotUpdate(BaseAdminUpdate):
    """Schema for updating a robot"""
    robot_id: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    serial: Optional[str] = Field(None, min_length=1, max_length=100)
    assigned_unit: Optional[str] = Field(None, max_length=100)
    patrol_area: Optional[List[GeoPoint]] = None
    stream_url: Optional[str] = Field(None, max_length=1000)
    status: Optional[RobotStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)


class RobotAdmin(BaseAdminService[RobotModel, RobotCreate, RobotUpdate]):
    """Robot admin service with CRUD operations"""
    
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
        """Initialize with demo robot data"""
        demo_robots = [
            {
                "robot_id": "RBPD-K9R-001",
                "model": "Boston Dynamics Spot",
                "serial": "BD-SPOT-001234",
                "assigned_unit": "K9 Unit",
                "status": RobotStatus.STANDBY,
                "patrol_area": [
                    GeoPoint(lat=26.7753, lng=-80.0569),
                    GeoPoint(lat=26.7763, lng=-80.0559),
                    GeoPoint(lat=26.7773, lng=-80.0569),
                    GeoPoint(lat=26.7753, lng=-80.0569),
                ],
            },
        ]
        
        for robot_data in demo_robots:
            robot = RobotModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **robot_data
            )
            self._storage[robot.id] = robot
    
    async def create(self, data: RobotCreate, user_id: str) -> RobotModel:
        """Create a new robot"""
        robot = RobotModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[robot.id] = robot
        return robot
    
    async def update(self, item_id: str, data: RobotUpdate, user_id: str) -> Optional[RobotModel]:
        """Update an existing robot"""
        robot = self._storage.get(item_id)
        if not robot:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(robot, key, value)
        
        robot.updated_at = datetime.now(UTC)
        robot.updated_by = user_id
        self._storage[item_id] = robot
        return robot
    
    async def update_telemetry(self, robot_id: str, lat: float, lng: float, battery: int) -> Optional[RobotModel]:
        """Update robot telemetry data"""
        robot = self._storage.get(robot_id)
        if not robot:
            return None
        
        robot.current_lat = lat
        robot.current_lng = lng
        robot.battery_level = battery
        robot.last_telemetry = datetime.now(UTC)
        self._storage[robot_id] = robot
        return robot
    
    async def get_active_robots(self) -> List[RobotModel]:
        """Get all active/deployed robots"""
        return [r for r in self._storage.values() if r.status in [RobotStatus.ACTIVE, RobotStatus.DEPLOYED]]


# Singleton instance
robot_admin = RobotAdmin()
