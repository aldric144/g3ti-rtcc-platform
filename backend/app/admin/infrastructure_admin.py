"""
Infrastructure Admin Module - CRUD operations for critical infrastructure management
Tab 7: Critical Infrastructure
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint


class InfrastructureType(str, Enum):
    WATER = "water"
    POWER = "power"
    GAS = "gas"
    COMMS = "comms"
    SEWER = "sewer"
    LIFT_STATION = "lift_station"
    SUBSTATION = "substation"
    PIPELINE = "pipeline"


class InfrastructureStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class InfrastructureModel(BaseAdminModel):
    """Infrastructure database model"""
    name: str = Field(..., min_length=1, max_length=200)
    infra_type: InfrastructureType = Field(...)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    status: InfrastructureStatus = Field(default=InfrastructureStatus.OPERATIONAL)
    address: Optional[str] = Field(None, max_length=500)
    operator: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    capacity: Optional[str] = Field(None, max_length=100)
    last_inspection: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)


class InfrastructureCreate(BaseAdminCreate):
    """Schema for creating infrastructure"""
    name: str = Field(..., min_length=1, max_length=200)
    infra_type: InfrastructureType = Field(...)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    status: InfrastructureStatus = Field(default=InfrastructureStatus.OPERATIONAL)
    address: Optional[str] = Field(None, max_length=500)
    operator: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    capacity: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=2000)


class InfrastructureUpdate(BaseAdminUpdate):
    """Schema for updating infrastructure"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    infra_type: Optional[InfrastructureType] = None
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    status: Optional[InfrastructureStatus] = None
    address: Optional[str] = Field(None, max_length=500)
    operator: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    capacity: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=2000)


class InfrastructureAdmin(BaseAdminService[InfrastructureModel, InfrastructureCreate, InfrastructureUpdate]):
    """Infrastructure admin service with CRUD operations"""
    
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
        """Initialize with demo infrastructure data"""
        demo_infra = [
            {
                "name": "Main Water Treatment Plant",
                "infra_type": InfrastructureType.WATER,
                "lat": 26.7720,
                "lng": -80.0590,
                "status": InfrastructureStatus.OPERATIONAL,
                "operator": "Riviera Beach Utilities",
                "capacity": "10 MGD",
            },
            {
                "name": "Downtown Lift Station #1",
                "infra_type": InfrastructureType.LIFT_STATION,
                "lat": 26.7755,
                "lng": -80.0565,
                "status": InfrastructureStatus.OPERATIONAL,
                "operator": "Riviera Beach Utilities",
            },
            {
                "name": "FPL Substation - Blue Heron",
                "infra_type": InfrastructureType.SUBSTATION,
                "lat": 26.7780,
                "lng": -80.0540,
                "status": InfrastructureStatus.OPERATIONAL,
                "operator": "Florida Power & Light",
            },
        ]
        
        for infra_data in demo_infra:
            infra = InfrastructureModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **infra_data
            )
            self._storage[infra.id] = infra
    
    async def create(self, data: InfrastructureCreate, user_id: str) -> InfrastructureModel:
        """Create new infrastructure"""
        infra = InfrastructureModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[infra.id] = infra
        return infra
    
    async def update(self, item_id: str, data: InfrastructureUpdate, user_id: str) -> Optional[InfrastructureModel]:
        """Update existing infrastructure"""
        infra = self._storage.get(item_id)
        if not infra:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(infra, key, value)
        
        infra.updated_at = datetime.now(UTC)
        infra.updated_by = user_id
        self._storage[item_id] = infra
        return infra
    
    async def get_by_type(self, infra_type: InfrastructureType) -> List[InfrastructureModel]:
        """Get all infrastructure of a specific type"""
        return [i for i in self._storage.values() if i.infra_type == infra_type]
    
    async def get_critical(self) -> List[InfrastructureModel]:
        """Get infrastructure with non-operational status"""
        return [i for i in self._storage.values() if i.status != InfrastructureStatus.OPERATIONAL]


# Singleton instance
infrastructure_admin = InfrastructureAdmin()
