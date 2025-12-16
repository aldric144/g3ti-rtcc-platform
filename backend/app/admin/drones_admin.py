"""
Drone Admin Module - CRUD operations for drone management
Tab 2: Drones Admin
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint


class DroneStatus(str, Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    MAINTENANCE = "maintenance"
    DEPLOYED = "deployed"
    OFFLINE = "offline"


class DroneModel(BaseAdminModel):
    """Drone database model"""
    drone_id: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=100)
    serial: str = Field(..., min_length=1, max_length=100)
    assigned_officer: Optional[str] = Field(None, max_length=100)
    max_flight_time: int = Field(default=30, ge=1, le=120, description="Max flight time in minutes")
    battery_count: int = Field(default=2, ge=1, le=10)
    home_lat: Optional[float] = Field(None, ge=-90, le=90)
    home_lng: Optional[float] = Field(None, ge=-180, le=180)
    stream_url: Optional[str] = Field(None, max_length=1000)
    status: DroneStatus = Field(default=DroneStatus.STANDBY)
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    current_altitude: Optional[float] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    last_telemetry: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)


class DroneCreate(BaseAdminCreate):
    """Schema for creating a drone"""
    drone_id: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=100)
    serial: str = Field(..., min_length=1, max_length=100)
    assigned_officer: Optional[str] = Field(None, max_length=100)
    max_flight_time: int = Field(default=30, ge=1, le=120)
    battery_count: int = Field(default=2, ge=1, le=10)
    home_lat: Optional[float] = Field(None, ge=-90, le=90)
    home_lng: Optional[float] = Field(None, ge=-180, le=180)
    stream_url: Optional[str] = Field(None, max_length=1000)
    status: DroneStatus = Field(default=DroneStatus.STANDBY)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('battery_count')
    @classmethod
    def validate_battery_count(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Battery count must be at least 1')
        return v


class DroneUpdate(BaseAdminUpdate):
    """Schema for updating a drone"""
    drone_id: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    serial: Optional[str] = Field(None, min_length=1, max_length=100)
    assigned_officer: Optional[str] = Field(None, max_length=100)
    max_flight_time: Optional[int] = Field(None, ge=1, le=120)
    battery_count: Optional[int] = Field(None, ge=1, le=10)
    home_lat: Optional[float] = Field(None, ge=-90, le=90)
    home_lng: Optional[float] = Field(None, ge=-180, le=180)
    stream_url: Optional[str] = Field(None, max_length=1000)
    status: Optional[DroneStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)


class DroneAdmin(BaseAdminService[DroneModel, DroneCreate, DroneUpdate]):
    """Drone admin service with CRUD operations"""
    
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
        """Initialize with demo drone data"""
        demo_drones = [
            {
                "drone_id": "RBPD-UAV-001",
                "model": "DJI Matrice 300 RTK",
                "serial": "DJI-M300-001234",
                "assigned_officer": "Officer Johnson",
                "max_flight_time": 55,
                "battery_count": 4,
                "home_lat": 26.7753,
                "home_lng": -80.0569,
                "status": DroneStatus.STANDBY,
            },
            {
                "drone_id": "RBPD-UAV-002",
                "model": "DJI Mavic 3 Enterprise",
                "serial": "DJI-M3E-005678",
                "assigned_officer": "Officer Smith",
                "max_flight_time": 45,
                "battery_count": 3,
                "home_lat": 26.7801,
                "home_lng": -80.0512,
                "status": DroneStatus.ACTIVE,
            },
        ]
        
        for drone_data in demo_drones:
            drone = DroneModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **drone_data
            )
            self._storage[drone.id] = drone
    
    async def create(self, data: DroneCreate, user_id: str) -> DroneModel:
        """Create a new drone"""
        drone = DroneModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[drone.id] = drone
        return drone
    
    async def update(self, item_id: str, data: DroneUpdate, user_id: str) -> Optional[DroneModel]:
        """Update an existing drone"""
        drone = self._storage.get(item_id)
        if not drone:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(drone, key, value)
        
        drone.updated_at = datetime.now(UTC)
        drone.updated_by = user_id
        self._storage[item_id] = drone
        return drone
    
    async def update_telemetry(self, drone_id: str, lat: float, lng: float, altitude: float, battery: int) -> Optional[DroneModel]:
        """Update drone telemetry data"""
        drone = self._storage.get(drone_id)
        if not drone:
            return None
        
        drone.current_lat = lat
        drone.current_lng = lng
        drone.current_altitude = altitude
        drone.battery_level = battery
        drone.last_telemetry = datetime.now(UTC)
        self._storage[drone_id] = drone
        return drone
    
    async def get_active_drones(self) -> List[DroneModel]:
        """Get all active/deployed drones"""
        return [d for d in self._storage.values() if d.status in [DroneStatus.ACTIVE, DroneStatus.DEPLOYED]]
    
    async def get_by_officer(self, officer: str) -> List[DroneModel]:
        """Get drones assigned to an officer"""
        return [d for d in self._storage.values() if d.assigned_officer == officer]


# Singleton instance
drone_admin = DroneAdmin()
