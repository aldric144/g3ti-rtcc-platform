"""
Hydrants Admin Module - CRUD operations for fire hydrant management
Tab 13: Hydrants
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService


class HydrantStatus(str, Enum):
    OPERATIONAL = "operational"
    OUT_OF_SERVICE = "out_of_service"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class HydrantType(str, Enum):
    STANDARD = "standard"
    HIGH_FLOW = "high_flow"
    DRY_BARREL = "dry_barrel"
    WET_BARREL = "wet_barrel"


class HydrantModel(BaseAdminModel):
    """Hydrant database model"""
    hydrant_id: str = Field(..., min_length=1, max_length=50)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    psi: Optional[int] = Field(None, ge=0, le=300, description="Pressure in PSI")
    status: HydrantStatus = Field(default=HydrantStatus.OPERATIONAL)
    hydrant_type: HydrantType = Field(default=HydrantType.STANDARD)
    flow_rate: Optional[int] = Field(None, ge=0, description="Flow rate in GPM")
    last_inspection: Optional[datetime] = None
    last_flow_test: Optional[datetime] = None
    address: Optional[str] = Field(None, max_length=500)
    sector: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)


class HydrantCreate(BaseAdminCreate):
    """Schema for creating a hydrant"""
    hydrant_id: str = Field(..., min_length=1, max_length=50)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    psi: Optional[int] = Field(None, ge=0, le=300)
    status: HydrantStatus = Field(default=HydrantStatus.OPERATIONAL)
    hydrant_type: HydrantType = Field(default=HydrantType.STANDARD)
    flow_rate: Optional[int] = Field(None, ge=0)
    address: Optional[str] = Field(None, max_length=500)
    sector: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)


class HydrantUpdate(BaseAdminUpdate):
    """Schema for updating a hydrant"""
    hydrant_id: Optional[str] = Field(None, min_length=1, max_length=50)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    psi: Optional[int] = Field(None, ge=0, le=300)
    status: Optional[HydrantStatus] = None
    hydrant_type: Optional[HydrantType] = None
    flow_rate: Optional[int] = Field(None, ge=0)
    address: Optional[str] = Field(None, max_length=500)
    sector: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)


class HydrantAdmin(BaseAdminService[HydrantModel, HydrantCreate, HydrantUpdate]):
    """Hydrant admin service with CRUD operations"""
    
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
        """Initialize with demo hydrant data"""
        demo_hydrants = [
            {
                "hydrant_id": "HYD-001",
                "lat": 26.7755,
                "lng": -80.0565,
                "psi": 85,
                "status": HydrantStatus.OPERATIONAL,
                "hydrant_type": HydrantType.STANDARD,
                "flow_rate": 1500,
                "address": "600 W Blue Heron Blvd",
                "sector": "SECTOR-1",
            },
            {
                "hydrant_id": "HYD-002",
                "lat": 26.7765,
                "lng": -80.0558,
                "psi": 90,
                "status": HydrantStatus.OPERATIONAL,
                "hydrant_type": HydrantType.HIGH_FLOW,
                "flow_rate": 2500,
                "address": "700 W Blue Heron Blvd",
                "sector": "SECTOR-1",
            },
            {
                "hydrant_id": "HYD-003",
                "lat": 26.7801,
                "lng": -80.0512,
                "psi": 75,
                "status": HydrantStatus.MAINTENANCE,
                "hydrant_type": HydrantType.STANDARD,
                "address": "Marina Village",
                "sector": "SECTOR-2",
                "notes": "Scheduled for repair - valve issue",
            },
        ]
        
        for hydrant_data in demo_hydrants:
            hydrant = HydrantModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **hydrant_data
            )
            self._storage[hydrant.id] = hydrant
    
    async def create(self, data: HydrantCreate, user_id: str) -> HydrantModel:
        """Create a new hydrant"""
        hydrant = HydrantModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[hydrant.id] = hydrant
        return hydrant
    
    async def update(self, item_id: str, data: HydrantUpdate, user_id: str) -> Optional[HydrantModel]:
        """Update an existing hydrant"""
        hydrant = self._storage.get(item_id)
        if not hydrant:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(hydrant, key, value)
        
        hydrant.updated_at = datetime.now(UTC)
        hydrant.updated_by = user_id
        self._storage[item_id] = hydrant
        return hydrant
    
    async def record_inspection(self, hydrant_id: str, user_id: str, psi: Optional[int] = None) -> Optional[HydrantModel]:
        """Record a hydrant inspection"""
        hydrant = self._storage.get(hydrant_id)
        if not hydrant:
            return None
        
        hydrant.last_inspection = datetime.now(UTC)
        if psi is not None:
            hydrant.psi = psi
        hydrant.updated_at = datetime.now(UTC)
        hydrant.updated_by = user_id
        self._storage[hydrant_id] = hydrant
        return hydrant
    
    async def record_flow_test(self, hydrant_id: str, user_id: str, flow_rate: int, psi: int) -> Optional[HydrantModel]:
        """Record a hydrant flow test"""
        hydrant = self._storage.get(hydrant_id)
        if not hydrant:
            return None
        
        hydrant.last_flow_test = datetime.now(UTC)
        hydrant.flow_rate = flow_rate
        hydrant.psi = psi
        hydrant.updated_at = datetime.now(UTC)
        hydrant.updated_by = user_id
        self._storage[hydrant_id] = hydrant
        return hydrant
    
    async def get_by_sector(self, sector: str) -> List[HydrantModel]:
        """Get all hydrants in a sector"""
        return [h for h in self._storage.values() if h.sector == sector]
    
    async def get_out_of_service(self) -> List[HydrantModel]:
        """Get all out of service hydrants"""
        return [h for h in self._storage.values() if h.status != HydrantStatus.OPERATIONAL]
    
    async def get_nearby(self, lat: float, lng: float, radius_km: float = 0.5) -> List[HydrantModel]:
        """Get hydrants within a radius of a point"""
        nearby = []
        for hydrant in self._storage.values():
            dist = ((hydrant.lat - lat) ** 2 + (hydrant.lng - lng) ** 2) ** 0.5
            if dist * 111 <= radius_km:  # Rough conversion to km
                nearby.append(hydrant)
        return nearby


# Singleton instance
hydrant_admin = HydrantAdmin()
