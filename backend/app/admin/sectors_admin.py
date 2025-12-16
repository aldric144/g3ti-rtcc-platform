"""
Sectors Admin Module - CRUD operations for patrol sector/beat management
Tab 5: Sectors (Beats)
"""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint, GeoPolygon


class SectorModel(BaseAdminModel):
    """Sector database model"""
    sector_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    polygon: List[GeoPoint] = Field(..., min_length=3)
    assigned_officers: List[str] = Field(default_factory=list)
    color: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('polygon')
    @classmethod
    def validate_polygon(cls, v: List[GeoPoint]) -> List[GeoPoint]:
        if len(v) < 3:
            raise ValueError('Polygon must have at least 3 points')
        # Check if polygon is closed
        if v[0].lat != v[-1].lat or v[0].lng != v[-1].lng:
            # Auto-close the polygon
            v.append(v[0])
        return v


class SectorCreate(BaseAdminCreate):
    """Schema for creating a sector"""
    sector_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    polygon: List[GeoPoint] = Field(..., min_length=3)
    assigned_officers: List[str] = Field(default_factory=list)
    color: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=2000)


class SectorUpdate(BaseAdminUpdate):
    """Schema for updating a sector"""
    sector_id: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    polygon: Optional[List[GeoPoint]] = None
    assigned_officers: Optional[List[str]] = None
    color: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=2000)


class SectorAdmin(BaseAdminService[SectorModel, SectorCreate, SectorUpdate]):
    """Sector admin service with CRUD operations"""
    
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
        """Initialize with demo sector data"""
        demo_sectors = [
            {
                "sector_id": "SECTOR-1",
                "name": "Downtown District",
                "polygon": [
                    GeoPoint(lat=26.7750, lng=-80.0600),
                    GeoPoint(lat=26.7800, lng=-80.0600),
                    GeoPoint(lat=26.7800, lng=-80.0500),
                    GeoPoint(lat=26.7750, lng=-80.0500),
                    GeoPoint(lat=26.7750, lng=-80.0600),
                ],
                "assigned_officers": ["Officer Johnson", "Officer Smith"],
                "color": "#0050ff",
            },
            {
                "sector_id": "SECTOR-2",
                "name": "Marina District",
                "polygon": [
                    GeoPoint(lat=26.7800, lng=-80.0600),
                    GeoPoint(lat=26.7850, lng=-80.0600),
                    GeoPoint(lat=26.7850, lng=-80.0500),
                    GeoPoint(lat=26.7800, lng=-80.0500),
                    GeoPoint(lat=26.7800, lng=-80.0600),
                ],
                "assigned_officers": ["Officer Williams"],
                "color": "#00ff50",
            },
        ]
        
        for sector_data in demo_sectors:
            sector = SectorModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **sector_data
            )
            self._storage[sector.id] = sector
    
    async def create(self, data: SectorCreate, user_id: str) -> SectorModel:
        """Create a new sector"""
        # Check for overlapping sectors
        # (In production, implement proper polygon intersection check)
        
        sector = SectorModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[sector.id] = sector
        return sector
    
    async def update(self, item_id: str, data: SectorUpdate, user_id: str) -> Optional[SectorModel]:
        """Update an existing sector"""
        sector = self._storage.get(item_id)
        if not sector:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(sector, key, value)
        
        sector.updated_at = datetime.now(UTC)
        sector.updated_by = user_id
        self._storage[item_id] = sector
        return sector
    
    async def find_sector_for_point(self, lat: float, lng: float) -> Optional[SectorModel]:
        """Find which sector contains a given GPS point"""
        # Simple point-in-polygon check (ray casting algorithm)
        for sector in self._storage.values():
            if self._point_in_polygon(lat, lng, sector.polygon):
                return sector
        return None
    
    def _point_in_polygon(self, lat: float, lng: float, polygon: List[GeoPoint]) -> bool:
        """Check if point is inside polygon using ray casting"""
        n = len(polygon)
        inside = False
        
        j = n - 1
        for i in range(n):
            if ((polygon[i].lng > lng) != (polygon[j].lng > lng) and
                lat < (polygon[j].lat - polygon[i].lat) * (lng - polygon[i].lng) / 
                (polygon[j].lng - polygon[i].lng) + polygon[i].lat):
                inside = not inside
            j = i
        
        return inside
    
    async def assign_officer(self, sector_id: str, officer: str) -> Optional[SectorModel]:
        """Assign an officer to a sector"""
        sector = self._storage.get(sector_id)
        if not sector:
            return None
        
        if officer not in sector.assigned_officers:
            sector.assigned_officers.append(officer)
            self._storage[sector_id] = sector
        return sector
    
    async def remove_officer(self, sector_id: str, officer: str) -> Optional[SectorModel]:
        """Remove an officer from a sector"""
        sector = self._storage.get(sector_id)
        if not sector:
            return None
        
        if officer in sector.assigned_officers:
            sector.assigned_officers.remove(officer)
            self._storage[sector_id] = sector
        return sector


# Singleton instance
sector_admin = SectorAdmin()
