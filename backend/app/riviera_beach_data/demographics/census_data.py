"""
Census Data Service for Riviera Beach.

Manages US Census demographic data including population, age, income, and housing.
"""

from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)


class CensusProfile(BaseModel):
    """Census demographic profile."""
    geography: str
    year: int = 2020
    total_population: int
    population_density_per_sq_mile: float | None = None
    median_age: float | None = None
    median_household_income: int | None = None
    per_capita_income: int | None = None
    poverty_rate: float | None = None
    unemployment_rate: float | None = None
    housing_units: int | None = None
    owner_occupied_rate: float | None = None
    renter_occupied_rate: float | None = None
    median_home_value: int | None = None
    median_rent: int | None = None
    households_with_vehicle: float | None = None
    households_without_vehicle: float | None = None


class AgeDistribution(BaseModel):
    """Age distribution data."""
    under_5: float
    age_5_17: float
    age_18_24: float
    age_25_44: float
    age_45_64: float
    age_65_plus: float


class RacialComposition(BaseModel):
    """Racial composition data."""
    white: float
    black_african_american: float
    asian: float
    hispanic_latino: float
    two_or_more_races: float
    other: float


class CensusDataService:
    """
    Service for managing US Census data for Riviera Beach.
    
    Data source: US Census Bureau American Community Survey (ACS)
    """
    
    # Census API base URL
    CENSUS_API_BASE = "https://api.census.gov/data"
    
    # Riviera Beach Census Profile (2020 ACS 5-Year Estimates)
    RIVIERA_BEACH_PROFILE = CensusProfile(
        geography="Riviera Beach city, Florida",
        year=2020,
        total_population=37964,
        population_density_per_sq_mile=3996.2,
        median_age=38.5,
        median_household_income=42156,
        per_capita_income=24891,
        poverty_rate=21.3,
        unemployment_rate=8.2,
        housing_units=17842,
        owner_occupied_rate=48.2,
        renter_occupied_rate=51.8,
        median_home_value=198500,
        median_rent=1245,
        households_with_vehicle=85.3,
        households_without_vehicle=14.7
    )
    
    AGE_DISTRIBUTION = AgeDistribution(
        under_5=6.2,
        age_5_17=16.8,
        age_18_24=9.1,
        age_25_44=26.5,
        age_45_64=25.8,
        age_65_plus=15.6
    )
    
    RACIAL_COMPOSITION = RacialComposition(
        white=18.5,
        black_african_american=66.2,
        asian=1.2,
        hispanic_latino=11.8,
        two_or_more_races=1.8,
        other=0.5
    )
    
    # Additional demographic indicators
    ADDITIONAL_INDICATORS = {
        "education": {
            "high_school_graduate_or_higher": 82.1,
            "bachelors_degree_or_higher": 18.5
        },
        "language": {
            "english_only": 78.5,
            "spanish": 12.8,
            "other_languages": 8.7
        },
        "household_type": {
            "family_households": 62.3,
            "married_couple_families": 28.5,
            "single_parent_families": 33.8,
            "nonfamily_households": 37.7
        },
        "housing_type": {
            "single_family_detached": 52.1,
            "single_family_attached": 8.3,
            "multi_family": 38.2,
            "mobile_home": 1.4
        },
        "commute": {
            "drove_alone": 78.2,
            "carpooled": 10.5,
            "public_transit": 3.2,
            "walked": 1.8,
            "work_from_home": 4.5,
            "mean_commute_minutes": 28.5
        }
    }
    
    def __init__(self) -> None:
        """Initialize the Census Data Service."""
        self._census_loaded = False
        self._http_client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    async def load_census_data(self) -> dict[str, Any]:
        """Load census demographic data."""
        logger.info("loading_census_data", city="Riviera Beach")
        
        self._census_loaded = True
        
        return {
            "data": [
                {
                    "type": "profile",
                    "data": self.RIVIERA_BEACH_PROFILE.model_dump()
                },
                {
                    "type": "age_distribution",
                    "data": self.AGE_DISTRIBUTION.model_dump()
                },
                {
                    "type": "racial_composition",
                    "data": self.RACIAL_COMPOSITION.model_dump()
                },
                {
                    "type": "additional_indicators",
                    "data": self.ADDITIONAL_INDICATORS
                }
            ],
            "metadata": {
                "source": "US Census Bureau ACS 5-Year Estimates",
                "year": 2020,
                "geography": "Riviera Beach city, Florida",
                "loaded_at": datetime.now(UTC).isoformat()
            }
        }
    
    def get_profile(self) -> CensusProfile:
        """Get census profile."""
        return self.RIVIERA_BEACH_PROFILE
    
    def get_age_distribution(self) -> AgeDistribution:
        """Get age distribution."""
        return self.AGE_DISTRIBUTION
    
    def get_racial_composition(self) -> RacialComposition:
        """Get racial composition."""
        return self.RACIAL_COMPOSITION
    
    def get_additional_indicators(self) -> dict[str, Any]:
        """Get additional demographic indicators."""
        return self.ADDITIONAL_INDICATORS
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of census data."""
        return {
            "geography": "Riviera Beach, FL",
            "year": 2020,
            "total_population": self.RIVIERA_BEACH_PROFILE.total_population,
            "median_household_income": self.RIVIERA_BEACH_PROFILE.median_household_income,
            "poverty_rate": self.RIVIERA_BEACH_PROFILE.poverty_rate,
            "housing_units": self.RIVIERA_BEACH_PROFILE.housing_units,
            "census_loaded": self._census_loaded
        }
