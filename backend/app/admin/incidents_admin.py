"""
Incidents Admin Module - CRUD operations for incident feed management
Tab 10: Incident Feed
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint


class IncidentType(str, Enum):
    CRIME = "crime"
    TRAFFIC = "traffic"
    MEDICAL = "medical"
    FIRE = "fire"
    HAZMAT = "hazmat"
    SUSPICIOUS = "suspicious"
    DOMESTIC = "domestic"
    ASSAULT = "assault"
    ROBBERY = "robbery"
    BURGLARY = "burglary"
    SHOTS_FIRED = "shots_fired"
    OTHER = "other"


class IncidentPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    DISPATCHED = "dispatched"
    ON_SCENE = "on_scene"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentModel(BaseAdminModel):
    """Incident database model"""
    incident_type: IncidentType = Field(...)
    priority: IncidentPriority = Field(default=IncidentPriority.MEDIUM)
    status: IncidentStatus = Field(default=IncidentStatus.OPEN)
    location: str = Field(..., min_length=1, max_length=500)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    incident_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    description: str = Field(..., min_length=1, max_length=2000)
    officer: Optional[str] = Field(None, max_length=200)
    unit: Optional[str] = Field(None, max_length=50)
    case_number: Optional[str] = Field(None, max_length=50)
    sector: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)
    resolved_at: Optional[datetime] = None


class IncidentCreate(BaseAdminCreate):
    """Schema for creating an incident"""
    incident_type: IncidentType = Field(...)
    priority: IncidentPriority = Field(default=IncidentPriority.MEDIUM)
    status: IncidentStatus = Field(default=IncidentStatus.OPEN)
    location: str = Field(..., min_length=1, max_length=500)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    incident_time: Optional[datetime] = None
    description: str = Field(..., min_length=1, max_length=2000)
    officer: Optional[str] = Field(None, max_length=200)
    unit: Optional[str] = Field(None, max_length=50)
    case_number: Optional[str] = Field(None, max_length=50)
    sector: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)


class IncidentUpdate(BaseAdminUpdate):
    """Schema for updating an incident"""
    incident_type: Optional[IncidentType] = None
    priority: Optional[IncidentPriority] = None
    status: Optional[IncidentStatus] = None
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    officer: Optional[str] = Field(None, max_length=200)
    unit: Optional[str] = Field(None, max_length=50)
    case_number: Optional[str] = Field(None, max_length=50)
    sector: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=2000)


class IncidentAdmin(BaseAdminService[IncidentModel, IncidentCreate, IncidentUpdate]):
    """Incident admin service with CRUD operations"""
    
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
        """Initialize with demo incident data"""
        demo_incidents = [
            {
                "incident_type": IncidentType.SHOTS_FIRED,
                "priority": IncidentPriority.CRITICAL,
                "status": IncidentStatus.DISPATCHED,
                "location": "1200 Main St, Riviera Beach",
                "lat": 26.7755,
                "lng": -80.0565,
                "description": "Multiple shots fired reported by neighbors",
                "officer": "Officer Johnson",
                "unit": "Unit 12",
                "sector": "SECTOR-1",
            },
            {
                "incident_type": IncidentType.TRAFFIC,
                "priority": IncidentPriority.MEDIUM,
                "status": IncidentStatus.ON_SCENE,
                "location": "Blue Heron Blvd & Congress Ave",
                "lat": 26.7765,
                "lng": -80.0558,
                "description": "Two-vehicle accident, minor injuries",
                "officer": "Officer Smith",
                "unit": "Unit 7",
                "sector": "SECTOR-1",
            },
            {
                "incident_type": IncidentType.SUSPICIOUS,
                "priority": IncidentPriority.LOW,
                "status": IncidentStatus.OPEN,
                "location": "Marina Village",
                "lat": 26.7801,
                "lng": -80.0512,
                "description": "Suspicious vehicle parked for extended period",
                "sector": "SECTOR-2",
            },
        ]
        
        for incident_data in demo_incidents:
            incident = IncidentModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **incident_data
            )
            self._storage[incident.id] = incident
    
    async def create(self, data: IncidentCreate, user_id: str) -> IncidentModel:
        """Create a new incident"""
        incident = IncidentModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            incident_time=data.incident_time or datetime.now(UTC),
            **data.model_dump(exclude={'incident_time'})
        )
        self._storage[incident.id] = incident
        return incident
    
    async def update(self, item_id: str, data: IncidentUpdate, user_id: str) -> Optional[IncidentModel]:
        """Update an existing incident"""
        incident = self._storage.get(item_id)
        if not incident:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Track status changes
        if 'status' in update_data:
            if update_data['status'] == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.now(UTC)
        
        for key, value in update_data.items():
            setattr(incident, key, value)
        
        incident.updated_at = datetime.now(UTC)
        incident.updated_by = user_id
        self._storage[item_id] = incident
        return incident
    
    async def get_active(self) -> List[IncidentModel]:
        """Get all active (non-closed) incidents"""
        return [i for i in self._storage.values() if i.status != IncidentStatus.CLOSED]
    
    async def get_by_type(self, incident_type: IncidentType) -> List[IncidentModel]:
        """Get incidents by type"""
        return [i for i in self._storage.values() if i.incident_type == incident_type]
    
    async def get_by_sector(self, sector: str) -> List[IncidentModel]:
        """Get incidents by sector"""
        return [i for i in self._storage.values() if i.sector == sector]
    
    async def get_critical(self) -> List[IncidentModel]:
        """Get critical priority incidents"""
        return [i for i in self._storage.values() 
                if i.priority == IncidentPriority.CRITICAL and i.status != IncidentStatus.CLOSED]


# Singleton instance
incident_admin = IncidentAdmin()
