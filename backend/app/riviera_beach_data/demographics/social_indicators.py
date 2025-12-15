"""
Social Indicators Service for Riviera Beach.

Manages social indicator data including poverty, overdose, DV, and homeless services.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class ServiceType(str, Enum):
    """Social service types."""
    DV_SHELTER = "dv_shelter"
    HOMELESS_SHELTER = "homeless_shelter"
    FOOD_BANK = "food_bank"
    MENTAL_HEALTH = "mental_health"
    SUBSTANCE_ABUSE = "substance_abuse"
    FAMILY_SERVICES = "family_services"


class SocialServiceLocation(BaseModel):
    """Social service location."""
    service_id: str
    name: str
    service_type: ServiceType
    address: str | None = None
    lat: float
    lon: float
    phone: str | None = None
    hours: str | None = None
    services_offered: list[str] = Field(default_factory=list)


class SocialIndicatorService:
    """
    Service for managing social indicator data for Riviera Beach.
    
    Data sources:
    - Florida DCF
    - Palm Beach County Human Services
    - Public health data
    """
    
    # Social indicators for Riviera Beach
    SOCIAL_INDICATORS = {
        "poverty": {
            "poverty_rate": 21.3,
            "child_poverty_rate": 32.5,
            "senior_poverty_rate": 14.2,
            "snap_recipients": 8500,
            "medicaid_recipients": 12000
        },
        "health": {
            "uninsured_rate": 15.8,
            "mental_health_providers_per_100k": 85.0,
            "substance_abuse_treatment_facilities": 3
        },
        "domestic_violence": {
            "dv_incidents_2022": 245,
            "dv_shelters_nearby": 2,
            "protective_orders_issued": 85
        },
        "homelessness": {
            "homeless_count_2023": 125,
            "sheltered_homeless": 85,
            "unsheltered_homeless": 40,
            "homeless_families": 15
        },
        "substance_abuse": {
            "overdose_deaths_2022": 18,
            "naloxone_administrations": 145,
            "treatment_admissions": 320
        },
        "child_welfare": {
            "child_abuse_reports": 185,
            "children_in_foster_care": 45,
            "dcf_investigations": 120
        }
    }
    
    # Social service locations
    SERVICE_LOCATIONS = [
        SocialServiceLocation(
            service_id="aid_victims_dv",
            name="Aid to Victims of Domestic Abuse (AVDA)",
            service_type=ServiceType.DV_SHELTER,
            address="Confidential Location, Palm Beach County",
            lat=26.7100,
            lon=-80.0800,
            phone="(561) 265-3797",
            hours="24/7 Hotline",
            services_offered=["Emergency Shelter", "Counseling", "Legal Advocacy", "Safety Planning"]
        ),
        SocialServiceLocation(
            service_id="palm_beach_dv",
            name="Palm Beach County Victim Services",
            service_type=ServiceType.DV_SHELTER,
            address="205 N Dixie Hwy, West Palm Beach, FL",
            lat=26.7150,
            lon=-80.0550,
            phone="(561) 833-7273",
            hours="Mon-Fri 8AM-5PM",
            services_offered=["Victim Advocacy", "Court Accompaniment", "Referrals"]
        ),
        SocialServiceLocation(
            service_id="salvation_army_shelter",
            name="Salvation Army Center of Hope",
            service_type=ServiceType.HOMELESS_SHELTER,
            address="1001 Fern St, West Palm Beach, FL",
            lat=26.7050,
            lon=-80.0600,
            phone="(561) 686-3530",
            hours="24/7",
            services_offered=["Emergency Shelter", "Meals", "Case Management"]
        ),
        SocialServiceLocation(
            service_id="lord_place_shelter",
            name="The Lord's Place",
            service_type=ServiceType.HOMELESS_SHELTER,
            address="2808 N Australian Ave, West Palm Beach, FL",
            lat=26.7400,
            lon=-80.0650,
            phone="(561) 494-0125",
            hours="24/7",
            services_offered=["Transitional Housing", "Job Training", "Case Management"]
        ),
        SocialServiceLocation(
            service_id="palm_beach_food_bank",
            name="Palm Beach County Food Bank",
            service_type=ServiceType.FOOD_BANK,
            address="8645 W Boynton Beach Blvd, Boynton Beach, FL",
            lat=26.5250,
            lon=-80.1200,
            phone="(561) 670-2518",
            hours="Mon-Fri 8AM-4PM",
            services_offered=["Food Distribution", "SNAP Assistance", "Nutrition Education"]
        ),
        SocialServiceLocation(
            service_id="riviera_beach_food_pantry",
            name="Riviera Beach Community Food Pantry",
            service_type=ServiceType.FOOD_BANK,
            address="600 W Blue Heron Blvd, Riviera Beach, FL",
            lat=26.7753,
            lon=-80.0620,
            phone="(561) 845-4100",
            hours="Tue, Thu 10AM-2PM",
            services_offered=["Food Distribution", "Emergency Food Assistance"]
        ),
        SocialServiceLocation(
            service_id="jerome_golden_center",
            name="Jerome Golden Center for Behavioral Health",
            service_type=ServiceType.MENTAL_HEALTH,
            address="1041 45th St, West Palm Beach, FL",
            lat=26.7600,
            lon=-80.0900,
            phone="(561) 383-5800",
            hours="24/7 Crisis Line",
            services_offered=["Mental Health Services", "Crisis Intervention", "Outpatient Treatment"]
        ),
        SocialServiceLocation(
            service_id="drug_abuse_foundation",
            name="Drug Abuse Foundation of Palm Beach County",
            service_type=ServiceType.SUBSTANCE_ABUSE,
            address="400 S Swinton Ave, Delray Beach, FL",
            lat=26.4550,
            lon=-80.0750,
            phone="(561) 278-0000",
            hours="24/7",
            services_offered=["Detox", "Residential Treatment", "Outpatient Services"]
        ),
        SocialServiceLocation(
            service_id="dcf_riviera_beach",
            name="Florida DCF - Riviera Beach Service Center",
            service_type=ServiceType.FAMILY_SERVICES,
            address="111 S Sapodilla Ave, West Palm Beach, FL",
            lat=26.7100,
            lon=-80.0550,
            phone="(561) 837-5000",
            hours="Mon-Fri 8AM-5PM",
            services_offered=["Child Welfare", "SNAP", "TANF", "Medicaid"]
        ),
    ]
    
    def __init__(self) -> None:
        """Initialize the Social Indicator Service."""
        self._social_loaded = False
    
    async def load_social_indicators(self) -> dict[str, Any]:
        """Load social indicator data."""
        logger.info("loading_social_indicators", city="Riviera Beach")
        
        self._social_loaded = True
        
        return {
            "data": [
                {"type": "indicators", "data": self.SOCIAL_INDICATORS},
                {"type": "service_locations", "data": [s.model_dump() for s in self.SERVICE_LOCATIONS]}
            ],
            "metadata": {
                "source": "Florida DCF / Palm Beach County Human Services",
                "geography": "Riviera Beach / Palm Beach County",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_indicators(self) -> dict[str, Any]:
        """Get social indicators."""
        return self.SOCIAL_INDICATORS
    
    def get_service_locations(self) -> list[SocialServiceLocation]:
        """Get social service locations."""
        return self.SERVICE_LOCATIONS
    
    def get_services_by_type(self, service_type: ServiceType) -> list[SocialServiceLocation]:
        """Get services by type."""
        return [s for s in self.SERVICE_LOCATIONS if s.service_type == service_type]
    
    def get_services_geojson(self) -> dict[str, Any]:
        """Get service locations as GeoJSON."""
        features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [s.lon, s.lat]},
                "properties": {
                    "service_id": s.service_id,
                    "name": s.name,
                    "service_type": s.service_type.value,
                    "phone": s.phone,
                    "category": "social_service"
                },
                "id": s.service_id
            }
            for s in self.SERVICE_LOCATIONS
        ]
        return {"type": "FeatureCollection", "features": features}
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of social indicator data."""
        return {
            "geography": "Riviera Beach / Palm Beach County",
            "poverty_rate": self.SOCIAL_INDICATORS["poverty"]["poverty_rate"],
            "homeless_count": self.SOCIAL_INDICATORS["homelessness"]["homeless_count_2023"],
            "service_locations": len(self.SERVICE_LOCATIONS),
            "by_service_type": {
                st.value: len(self.get_services_by_type(st))
                for st in ServiceType
            },
            "social_loaded": self._social_loaded
        }
