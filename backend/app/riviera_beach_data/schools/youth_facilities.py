"""
Youth Facility Service for Riviera Beach.

Manages youth centers, parks, recreation facilities, and playgrounds.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class FacilityType(str, Enum):
    """Youth facility types."""
    YOUTH_CENTER = "youth_center"
    PARK = "park"
    RECREATION_CENTER = "recreation_center"
    PLAYGROUND = "playground"
    SPORTS_FIELD = "sports_field"
    COMMUNITY_CENTER = "community_center"
    AFTER_SCHOOL = "after_school"


class YouthFacility(BaseModel):
    """Youth facility information."""
    facility_id: str
    name: str
    facility_type: FacilityType
    address: str | None = None
    lat: float
    lon: float
    phone: str | None = None
    hours: str | None = None
    amenities: list[str] = Field(default_factory=list)
    programs: list[str] = Field(default_factory=list)


class YouthFacilityService:
    """
    Service for managing youth facility data for Riviera Beach.
    """
    
    FACILITIES = [
        YouthFacility(
            facility_id="wells_rec",
            name="Wells Recreation Center",
            facility_type=FacilityType.RECREATION_CENTER,
            address="1000 W 10th St",
            lat=26.7680,
            lon=-80.0680,
            phone="(561) 845-4070",
            hours="Mon-Fri 9AM-9PM, Sat 9AM-5PM",
            amenities=["Basketball Courts", "Fitness Center", "Meeting Rooms"],
            programs=["Youth Basketball", "Summer Camp", "After School Program"]
        ),
        YouthFacility(
            facility_id="barracuda_bay",
            name="Barracuda Bay Aquatic Complex",
            facility_type=FacilityType.RECREATION_CENTER,
            address="1621 W Blue Heron Blvd",
            lat=26.7753,
            lon=-80.0750,
            phone="(561) 845-4075",
            hours="Daily 10AM-6PM (seasonal)",
            amenities=["Swimming Pool", "Water Slides", "Splash Pad"],
            programs=["Swim Lessons", "Water Aerobics", "Pool Parties"]
        ),
        YouthFacility(
            facility_id="marina_park",
            name="Riviera Beach Marina Event Park",
            facility_type=FacilityType.PARK,
            address="200 E 13th St",
            lat=26.7800,
            lon=-80.0460,
            amenities=["Waterfront Views", "Walking Paths", "Event Space", "Playground"],
            programs=["Community Events", "Concerts"]
        ),
        YouthFacility(
            facility_id="bicentennial_park",
            name="Bicentennial Park",
            facility_type=FacilityType.PARK,
            address="1500 N Ocean Dr",
            lat=26.7850,
            lon=-80.0350,
            amenities=["Beach Access", "Picnic Areas", "Playground", "Restrooms"],
            programs=["Beach Programs"]
        ),
        YouthFacility(
            facility_id="youth_empowerment",
            name="Youth Empowerment Center",
            facility_type=FacilityType.YOUTH_CENTER,
            address="600 W Blue Heron Blvd",
            lat=26.7753,
            lon=-80.0620,
            phone="(561) 845-4080",
            hours="Mon-Fri 3PM-8PM",
            amenities=["Computer Lab", "Study Rooms", "Game Room"],
            programs=["Homework Help", "Mentoring", "Career Readiness"]
        ),
        YouthFacility(
            facility_id="cunningham_park",
            name="Cunningham Park",
            facility_type=FacilityType.SPORTS_FIELD,
            address="800 W 28th St",
            lat=26.7830,
            lon=-80.0650,
            amenities=["Baseball Fields", "Soccer Fields", "Concession Stand"],
            programs=["Little League", "Youth Soccer"]
        ),
        YouthFacility(
            facility_id="lincoln_playground",
            name="Lincoln Park Playground",
            facility_type=FacilityType.PLAYGROUND,
            address="1200 W 10th St",
            lat=26.7680,
            lon=-80.0690,
            amenities=["Playground Equipment", "Benches", "Shade Structures"]
        ),
        YouthFacility(
            facility_id="after_school_1",
            name="Riviera Beach After School Program - Washington",
            facility_type=FacilityType.AFTER_SCHOOL,
            address="1700 Avenue G",
            lat=26.7700,
            lon=-80.0550,
            hours="Mon-Fri 3PM-6PM",
            programs=["Homework Help", "Snacks", "Recreation"]
        ),
    ]
    
    def __init__(self) -> None:
        """Initialize the Youth Facility Service."""
        self._facilities_loaded = False
    
    async def load_facilities(self) -> dict[str, Any]:
        """Load youth facility data."""
        logger.info("loading_youth_facilities", city="Riviera Beach")
        
        features = []
        for facility in self.FACILITIES:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [facility.lon, facility.lat]
                },
                "properties": {
                    "facility_id": facility.facility_id,
                    "name": facility.name,
                    "facility_type": facility.facility_type.value,
                    "address": facility.address,
                    "phone": facility.phone,
                    "hours": facility.hours,
                    "amenities": facility.amenities,
                    "programs": facility.programs,
                    "category": "youth_facility"
                },
                "id": facility.facility_id
            })
        
        self._facilities_loaded = True
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "source": "City of Riviera Beach Parks & Recreation",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_facilities(self) -> list[YouthFacility]:
        """Get list of youth facilities."""
        return self.FACILITIES
    
    def get_facilities_by_type(self, facility_type: FacilityType) -> list[YouthFacility]:
        """Get facilities by type."""
        return [f for f in self.FACILITIES if f.facility_type == facility_type]
    
    def get_facilities_geojson(self) -> dict[str, Any]:
        """Get facilities as GeoJSON."""
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [f.lon, f.lat]},
                "properties": {
                    "facility_id": f.facility_id,
                    "name": f.name,
                    "facility_type": f.facility_type.value,
                    "category": "youth_facility"
                },
                "id": f.facility_id
            }
            for f in self.FACILITIES
        ]
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of youth facility data."""
        return {
            "total_facilities": len(self.FACILITIES),
            "by_type": {ft.value: len(self.get_facilities_by_type(ft)) for ft in FacilityType},
            "facilities_loaded": self._facilities_loaded
        }
