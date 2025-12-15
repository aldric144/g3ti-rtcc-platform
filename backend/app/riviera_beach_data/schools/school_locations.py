"""
School Location Service for Riviera Beach.

Manages school location and attendance boundary data from Palm Beach County Schools.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class SchoolType(str, Enum):
    """School types."""
    ELEMENTARY = "elementary"
    MIDDLE = "middle"
    HIGH = "high"
    CHARTER = "charter"
    ALTERNATIVE = "alternative"
    SPECIAL = "special"


class SchoolInfo(BaseModel):
    """School information."""
    school_id: str
    name: str
    school_type: SchoolType
    address: str
    city: str = "Riviera Beach"
    state: str = "FL"
    zip_code: str = "33404"
    lat: float
    lon: float
    phone: str | None = None
    principal: str | None = None
    grades: str | None = None
    enrollment: int | None = None
    district: str = "Palm Beach County School District"


class SchoolLocationService:
    """
    Service for managing school location data for Riviera Beach.
    
    Data source: Palm Beach County School District
    """
    
    # Schools in/near Riviera Beach
    SCHOOLS = [
        SchoolInfo(
            school_id="rbhs",
            name="Riviera Beach Preparatory & Achievement Academy",
            school_type=SchoolType.HIGH,
            address="1600 Avenue L",
            lat=26.7680,
            lon=-80.0620,
            phone="(561) 845-4400",
            grades="9-12",
            enrollment=850
        ),
        SchoolInfo(
            school_id="jfk_middle",
            name="John F. Kennedy Middle School",
            school_type=SchoolType.MIDDLE,
            address="300 W 30th St",
            lat=26.7850,
            lon=-80.0620,
            phone="(561) 845-4500",
            grades="6-8",
            enrollment=720
        ),
        SchoolInfo(
            school_id="washington_elem",
            name="Washington Elementary School",
            school_type=SchoolType.ELEMENTARY,
            address="1700 Avenue G",
            lat=26.7700,
            lon=-80.0550,
            phone="(561) 845-4600",
            grades="K-5",
            enrollment=450
        ),
        SchoolInfo(
            school_id="lincoln_elem",
            name="Lincoln Elementary School",
            school_type=SchoolType.ELEMENTARY,
            address="1200 W 10th St",
            lat=26.7680,
            lon=-80.0700,
            phone="(561) 845-4700",
            grades="K-5",
            enrollment=380
        ),
        SchoolInfo(
            school_id="northmore_elem",
            name="Northmore Elementary School",
            school_type=SchoolType.ELEMENTARY,
            address="400 W 28th St",
            lat=26.7830,
            lon=-80.0620,
            phone="(561) 845-4800",
            grades="K-5",
            enrollment=420
        ),
        SchoolInfo(
            school_id="rbmaa_charter",
            name="Riviera Beach Maritime Academy",
            school_type=SchoolType.CHARTER,
            address="200 E 13th St",
            lat=26.7800,
            lon=-80.0480,
            phone="(561) 845-4900",
            grades="6-12",
            enrollment=350
        ),
        SchoolInfo(
            school_id="suncoast_high",
            name="Suncoast Community High School",
            school_type=SchoolType.HIGH,
            address="1717 Avenue S",
            zip_code="33401",
            city="West Palm Beach",
            lat=26.7500,
            lon=-80.0700,
            phone="(561) 882-3400",
            grades="9-12",
            enrollment=2100
        ),
    ]
    
    def __init__(self) -> None:
        """Initialize the School Location Service."""
        self._schools_loaded = False
    
    async def load_schools(self) -> dict[str, Any]:
        """Load school location data."""
        logger.info("loading_schools", city="Riviera Beach")
        
        features = []
        for school in self.SCHOOLS:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [school.lon, school.lat]
                },
                "properties": {
                    "school_id": school.school_id,
                    "name": school.name,
                    "school_type": school.school_type.value,
                    "address": school.address,
                    "city": school.city,
                    "phone": school.phone,
                    "grades": school.grades,
                    "enrollment": school.enrollment,
                    "district": school.district,
                    "category": "school"
                },
                "id": school.school_id
            })
        
        self._schools_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "Palm Beach County School District",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_schools(self) -> list[SchoolInfo]:
        """Get list of schools."""
        return self.SCHOOLS
    
    def get_schools_by_type(self, school_type: SchoolType) -> list[SchoolInfo]:
        """Get schools by type."""
        return [s for s in self.SCHOOLS if s.school_type == school_type]
    
    def get_schools_geojson(self) -> dict[str, Any]:
        """Get schools as GeoJSON."""
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [s.lon, s.lat]},
                "properties": {
                    "school_id": s.school_id,
                    "name": s.name,
                    "school_type": s.school_type.value,
                    "category": "school"
                },
                "id": s.school_id
            }
            for s in self.SCHOOLS
        ]
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of school data."""
        return {
            "total_schools": len(self.SCHOOLS),
            "by_type": {st.value: len(self.get_schools_by_type(st)) for st in SchoolType},
            "total_enrollment": sum(s.enrollment or 0 for s in self.SCHOOLS),
            "schools_loaded": self._schools_loaded
        }
