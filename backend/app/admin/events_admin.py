"""
Events Admin Module - CRUD operations for special event management
Tab 12: Special Events
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint


class EventType(str, Enum):
    PARADE = "parade"
    CONCERT = "concert"
    FESTIVAL = "festival"
    SPORTS = "sports"
    PROTEST = "protest"
    VIP = "vip"
    CONSTRUCTION = "construction"
    EMERGENCY = "emergency"
    OTHER = "other"


class EventStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventModel(BaseAdminModel):
    """Event database model"""
    event_name: str = Field(..., min_length=1, max_length=200)
    event_type: EventType = Field(default=EventType.OTHER)
    status: EventStatus = Field(default=EventStatus.PLANNED)
    boundary: List[GeoPoint] = Field(..., min_length=3)
    start_time: datetime = Field(...)
    end_time: datetime = Field(...)
    expected_attendance: Optional[int] = Field(None, ge=0)
    organizer: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    permit_number: Optional[str] = Field(None, max_length=50)
    assigned_units: List[str] = Field(default_factory=list)
    road_closures: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)


class EventCreate(BaseAdminCreate):
    """Schema for creating an event"""
    event_name: str = Field(..., min_length=1, max_length=200)
    event_type: EventType = Field(default=EventType.OTHER)
    status: EventStatus = Field(default=EventStatus.PLANNED)
    boundary: List[GeoPoint] = Field(..., min_length=3)
    start_time: datetime = Field(...)
    end_time: datetime = Field(...)
    expected_attendance: Optional[int] = Field(None, ge=0)
    organizer: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    permit_number: Optional[str] = Field(None, max_length=50)
    assigned_units: List[str] = Field(default_factory=list)
    road_closures: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('boundary')
    @classmethod
    def validate_boundary(cls, v: List[GeoPoint]) -> List[GeoPoint]:
        if len(v) < 3:
            raise ValueError('Boundary must have at least 3 points')
        return v

    @model_validator(mode='after')
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError('End time must be after start time')
        return self


class EventUpdate(BaseAdminUpdate):
    """Schema for updating an event"""
    event_name: Optional[str] = Field(None, min_length=1, max_length=200)
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    boundary: Optional[List[GeoPoint]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    expected_attendance: Optional[int] = Field(None, ge=0)
    organizer: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=50)
    permit_number: Optional[str] = Field(None, max_length=50)
    assigned_units: Optional[List[str]] = None
    road_closures: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)


class EventAdmin(BaseAdminService[EventModel, EventCreate, EventUpdate]):
    """Event admin service with CRUD operations"""
    
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
        """Initialize with demo event data"""
        now = datetime.now(UTC)
        demo_events = [
            {
                "event_name": "Riviera Beach Jazz Festival",
                "event_type": EventType.FESTIVAL,
                "status": EventStatus.PLANNED,
                "boundary": [
                    GeoPoint(lat=26.7750, lng=-80.0580),
                    GeoPoint(lat=26.7770, lng=-80.0580),
                    GeoPoint(lat=26.7770, lng=-80.0550),
                    GeoPoint(lat=26.7750, lng=-80.0550),
                    GeoPoint(lat=26.7750, lng=-80.0580),
                ],
                "start_time": now.replace(hour=14, minute=0),
                "end_time": now.replace(hour=22, minute=0),
                "expected_attendance": 5000,
                "organizer": "City of Riviera Beach",
                "assigned_units": ["Unit 1", "Unit 2", "Unit 5"],
                "road_closures": "Blue Heron Blvd closed from Congress to Broadway",
            },
        ]
        
        for event_data in demo_events:
            event = EventModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **event_data
            )
            self._storage[event.id] = event
    
    async def create(self, data: EventCreate, user_id: str) -> EventModel:
        """Create a new event"""
        event = EventModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[event.id] = event
        return event
    
    async def update(self, item_id: str, data: EventUpdate, user_id: str) -> Optional[EventModel]:
        """Update an existing event"""
        event = self._storage.get(item_id)
        if not event:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(event, key, value)
        
        event.updated_at = datetime.now(UTC)
        event.updated_by = user_id
        self._storage[item_id] = event
        return event
    
    async def get_active(self) -> List[EventModel]:
        """Get all active events"""
        now = datetime.now(UTC)
        return [e for e in self._storage.values() 
                if e.status == EventStatus.ACTIVE or 
                (e.status == EventStatus.PLANNED and e.start_time <= now <= e.end_time)]
    
    async def get_upcoming(self, days: int = 7) -> List[EventModel]:
        """Get upcoming events within specified days"""
        now = datetime.now(UTC)
        from datetime import timedelta
        future = now + timedelta(days=days)
        return [e for e in self._storage.values() 
                if e.status == EventStatus.PLANNED and now <= e.start_time <= future]


# Singleton instance
event_admin = EventAdmin()
