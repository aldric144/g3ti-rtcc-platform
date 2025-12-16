"""
Schools Admin Module - CRUD operations for school management
Tab 8: Schools
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid

from .base_admin import BaseAdminModel, BaseAdminCreate, BaseAdminUpdate, BaseAdminService, GeoPoint


class GradeLevel(str, Enum):
    ELEMENTARY = "elementary"
    MIDDLE = "middle"
    HIGH = "high"
    K12 = "k12"
    CHARTER = "charter"
    PRIVATE = "private"


class AccessPoint(BaseModel):
    """School access point"""
    name: str = Field(..., max_length=100)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    access_type: str = Field(default="main", max_length=50)  # main, emergency, service


class SchoolModel(BaseAdminModel):
    """School database model"""
    school_name: str = Field(..., min_length=1, max_length=200)
    grade_level: GradeLevel = Field(...)
    address: str = Field(..., min_length=1, max_length=500)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    perimeter: Optional[List[GeoPoint]] = None
    pickup_routes: Optional[List[List[GeoPoint]]] = None
    access_points: Optional[List[AccessPoint]] = None
    sro_name: Optional[str] = Field(None, max_length=200)
    sro_phone: Optional[str] = Field(None, max_length=50)
    principal_name: Optional[str] = Field(None, max_length=200)
    principal_phone: Optional[str] = Field(None, max_length=50)
    student_count: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class SchoolCreate(BaseAdminCreate):
    """Schema for creating a school"""
    school_name: str = Field(..., min_length=1, max_length=200)
    grade_level: GradeLevel = Field(...)
    address: str = Field(..., min_length=1, max_length=500)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    perimeter: Optional[List[GeoPoint]] = None
    pickup_routes: Optional[List[List[GeoPoint]]] = None
    access_points: Optional[List[AccessPoint]] = None
    sro_name: Optional[str] = Field(None, max_length=200)
    sro_phone: Optional[str] = Field(None, max_length=50)
    principal_name: Optional[str] = Field(None, max_length=200)
    principal_phone: Optional[str] = Field(None, max_length=50)
    student_count: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('perimeter')
    @classmethod
    def validate_perimeter(cls, v: Optional[List[GeoPoint]]) -> Optional[List[GeoPoint]]:
        if v is not None and len(v) < 3:
            raise ValueError('Perimeter must have at least 3 points')
        return v


class SchoolUpdate(BaseAdminUpdate):
    """Schema for updating a school"""
    school_name: Optional[str] = Field(None, min_length=1, max_length=200)
    grade_level: Optional[GradeLevel] = None
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    perimeter: Optional[List[GeoPoint]] = None
    pickup_routes: Optional[List[List[GeoPoint]]] = None
    access_points: Optional[List[AccessPoint]] = None
    sro_name: Optional[str] = Field(None, max_length=200)
    sro_phone: Optional[str] = Field(None, max_length=50)
    principal_name: Optional[str] = Field(None, max_length=200)
    principal_phone: Optional[str] = Field(None, max_length=50)
    student_count: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class SchoolAdmin(BaseAdminService[SchoolModel, SchoolCreate, SchoolUpdate]):
    """School admin service with CRUD operations"""
    
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
        """Initialize with demo school data"""
        demo_schools = [
            {
                "school_name": "Riviera Beach Elementary",
                "grade_level": GradeLevel.ELEMENTARY,
                "address": "1200 W 13th St, Riviera Beach, FL 33404",
                "lat": 26.7730,
                "lng": -80.0580,
                "sro_name": "Officer Martinez",
                "student_count": 450,
                "perimeter": [
                    GeoPoint(lat=26.7725, lng=-80.0590),
                    GeoPoint(lat=26.7735, lng=-80.0590),
                    GeoPoint(lat=26.7735, lng=-80.0570),
                    GeoPoint(lat=26.7725, lng=-80.0570),
                    GeoPoint(lat=26.7725, lng=-80.0590),
                ],
                "access_points": [
                    AccessPoint(name="Main Entrance", lat=26.7730, lng=-80.0580, access_type="main"),
                    AccessPoint(name="Bus Loop", lat=26.7728, lng=-80.0575, access_type="service"),
                ],
            },
            {
                "school_name": "Riviera Beach High School",
                "grade_level": GradeLevel.HIGH,
                "address": "1600 Avenue L, Riviera Beach, FL 33404",
                "lat": 26.7810,
                "lng": -80.0520,
                "sro_name": "Officer Thompson",
                "student_count": 1200,
            },
        ]
        
        for school_data in demo_schools:
            school = SchoolModel(
                id=str(uuid.uuid4()),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                **school_data
            )
            self._storage[school.id] = school
    
    async def create(self, data: SchoolCreate, user_id: str) -> SchoolModel:
        """Create a new school"""
        school = SchoolModel(
            id=str(uuid.uuid4()),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_id,
            updated_by=user_id,
            **data.model_dump()
        )
        self._storage[school.id] = school
        return school
    
    async def update(self, item_id: str, data: SchoolUpdate, user_id: str) -> Optional[SchoolModel]:
        """Update an existing school"""
        school = self._storage.get(item_id)
        if not school:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(school, key, value)
        
        school.updated_at = datetime.now(UTC)
        school.updated_by = user_id
        self._storage[item_id] = school
        return school
    
    async def get_by_grade_level(self, grade_level: GradeLevel) -> List[SchoolModel]:
        """Get all schools of a specific grade level"""
        return [s for s in self._storage.values() if s.grade_level == grade_level]
    
    async def get_schools_with_sro(self) -> List[SchoolModel]:
        """Get all schools with assigned SRO"""
        return [s for s in self._storage.values() if s.sro_name]


# Singleton instance
school_admin = SchoolAdmin()
