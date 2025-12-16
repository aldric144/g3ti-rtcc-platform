"""
Fire Preplans Admin Module - CRUD operations for fire preplan management
Tab 6: Fire Preplans
"""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint


class FirePreplanModel(BaseAdminModel):
    """Fire Preplan database model"""
    building_name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=500)
    pdf_url: Optional[str] = Field(None, max_length=1000)
    hazmat_notes: Optional[str] = Field(None, max_length=2000)
    knox_box_location: Optional[str] = Field(None, max_length=500)
    riser_location: Optional[str] = Field(None, max_length=500)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    contact_name: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    occupancy_type: Optional[str] = Field(None, max_length=100)
    floors: Optional[int] = Field(None, ge=1, le=200)
    notes: Optional[str] = Field(None, max_length=2000)


class FirePreplanCreate(BaseAdminCreate):
    """Schema for creating a fire preplan"""
    building_name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=500)
    pdf_url: Optional[str] = Field(None, max_length=1000)
    hazmat_notes: Optional[str] = Field(None, max_length=2000)
    knox_box_location: Optional[str] = Field(None, max_length=500)
    riser_location: Optional[str] = Field(None, max_length=500)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    contact_name: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    occupancy_type: Optional[str] = Field(None, max_length=100)
    floors: Optional[int] = Field(None, ge=1, le=200)
    notes: Optional[str] = Field(None, max_length=2000)


class FirePreplanUpdate(BaseAdminUpdate):
    """Schema for updating a fire preplan"""
    building_name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    pdf_url: Optional[str] = Field(None, max_length=1000)
    hazmat_notes: Optional[str] = Field(None, max_length=2000)
    knox_box_location: Optional[str] = Field(None, max_length=500)
    riser_location: Optional[str] = Field(None, max_length=500)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    contact_name: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    occupancy_type: Optional[str] = Field(None, max_length=100)
    floors: Optional[int] = Field(None, ge=1, le=200)
    notes: Optional[str] = Field(None, max_length=2000)


class FirePreplanAdmin(BaseAdminService[FirePreplanModel, FirePreplanCreate, FirePreplanUpdate]):
    """Fire Preplan admin service with CRUD operations"""
    
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
        """Initialize with demo fire preplan data"""
        demo_preplans = [
            {
                "building_name": "Riviera Beach City Hall",
                "address": "600 W Blue Heron Blvd, Riviera Beach, FL 33404",
                "lat": 26.7753,
                "lng": -80.0569,
                "knox_box_location": "Main entrance, east side",
                "riser_location": "Mechanical room, ground floor",
                "occupancy_type": "Government",
                "floors": 3,
            },
            {
                "building_name": "Marina Village Shopping Center",
                "address": "1100 Marina Blvd, Riviera Beach, FL 33404",
                "lat": 26.7801,
                "lng": -80.0512,
                "hazmat_notes": "Pool chemicals stored in maintenance area",
                "knox_box_location": "North entrance",
                "occupancy_type": "Commercial",
                "floors": 2,
            },
        ]
        
        for preplan_data in demo_preplans:
            preplan = FirePreplanModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **preplan_data
            )
            self._storage[preplan.id] = preplan
    
    async def create(self, data: FirePreplanCreate, user_id: str) -> FirePreplanModel:
        """Create a new fire preplan"""
        preplan = FirePreplanModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[preplan.id] = preplan
        return preplan
    
    async def update(self, item_id: str, data: FirePreplanUpdate, user_id: str) -> Optional[FirePreplanModel]:
        """Update an existing fire preplan"""
        preplan = self._storage.get(item_id)
        if not preplan:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(preplan, key, value)
        
        preplan.updated_at = datetime.now(UTC)
        preplan.updated_by = user_id
        self._storage[item_id] = preplan
        return preplan
    
    async def get_nearby(self, lat: float, lng: float, radius_km: float = 1.0) -> List[FirePreplanModel]:
        """Get fire preplans within a radius of a point"""
        nearby = []
        for preplan in self._storage.values():
            if preplan.lat and preplan.lng:
                # Simple distance calculation (Haversine would be more accurate)
                dist = ((preplan.lat - lat) ** 2 + (preplan.lng - lng) ** 2) ** 0.5
                if dist * 111 <= radius_km:  # Rough conversion to km
                    nearby.append(preplan)
        return nearby


# Singleton instance
fire_preplan_admin = FirePreplanAdmin()
