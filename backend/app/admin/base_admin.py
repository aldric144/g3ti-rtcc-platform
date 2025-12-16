"""
Base Admin Module - Common functionality for all admin modules
"""

from datetime import datetime, UTC
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
import uuid

# Type variables for generic CRUD operations
ModelType = TypeVar("ModelType", bound="BaseAdminModel")
CreateType = TypeVar("CreateType", bound="BaseAdminCreate")
UpdateType = TypeVar("UpdateType", bound="BaseAdminUpdate")


class BaseAdminModel(BaseModel):
    """Base model for all admin entities"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class BaseAdminCreate(BaseModel):
    """Base schema for creating admin entities"""
    pass


class BaseAdminUpdate(BaseModel):
    """Base schema for updating admin entities"""
    pass


class GeoPoint(BaseModel):
    """GPS coordinate point"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class GeoPolygon(BaseModel):
    """Geographic polygon boundary"""
    points: List[GeoPoint] = Field(..., min_length=3, description="Polygon vertices")
    
    def is_closed(self) -> bool:
        """Check if polygon is properly closed"""
        if len(self.points) < 3:
            return False
        first = self.points[0]
        last = self.points[-1]
        return first.lat == last.lat and first.lng == last.lng


class BaseAdminService(Generic[ModelType, CreateType, UpdateType]):
    """Base service class for admin CRUD operations"""
    
    def __init__(self):
        self._storage: Dict[str, ModelType] = {}
    
    async def get_all(self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[ModelType]:
        """Get all items with pagination and optional filters"""
        items = list(self._storage.values())
        
        if filters:
            for key, value in filters.items():
                items = [item for item in items if getattr(item, key, None) == value]
        
        return items[skip:skip + limit]
    
    async def get_by_id(self, item_id: str) -> Optional[ModelType]:
        """Get item by ID"""
        return self._storage.get(item_id)
    
    async def create(self, data: CreateType, user_id: str) -> ModelType:
        """Create new item"""
        raise NotImplementedError("Subclass must implement create method")
    
    async def update(self, item_id: str, data: UpdateType, user_id: str) -> Optional[ModelType]:
        """Update existing item"""
        raise NotImplementedError("Subclass must implement update method")
    
    async def delete(self, item_id: str, user_id: str) -> bool:
        """Delete item by ID"""
        if item_id in self._storage:
            del self._storage[item_id]
            return True
        return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count items with optional filters"""
        items = list(self._storage.values())
        if filters:
            for key, value in filters.items():
                items = [item for item in items if getattr(item, key, None) == value]
        return len(items)
