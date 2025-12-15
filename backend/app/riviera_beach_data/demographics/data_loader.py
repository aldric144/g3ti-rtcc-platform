"""
Demographics Data Loader for Riviera Beach.

Coordinates loading of all demographic and social data.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.demographics.census_data import CensusDataService
from app.riviera_beach_data.demographics.crime_statistics import CrimeStatisticsService
from app.riviera_beach_data.demographics.social_indicators import SocialIndicatorService

logger = get_logger(__name__)


class DemographicsDataLoader:
    """Coordinates loading of all demographic data for Riviera Beach."""
    
    def __init__(self) -> None:
        """Initialize the Demographics Data Loader."""
        self.census_service = CensusDataService()
        self.crime_service = CrimeStatisticsService()
        self.social_service = SocialIndicatorService()
        self._loaded = False
    
    async def load_all(self) -> dict[str, Any]:
        """Load all demographic data."""
        logger.info("demographics_data_loader_starting", city="Riviera Beach")
        
        results = {
            "loaded": [],
            "failed": [],
            "total_records": 0,
            "loaded_at": datetime.now(UTC).isoformat()
        }
        
        try:
            census_data = await self.census_service.load_census_data()
            results["loaded"].append("census")
            results["total_records"] += len(census_data.get("data", []))
        except Exception as e:
            results["failed"].append({"type": "census", "error": str(e)})
        
        try:
            crime_data = await self.crime_service.load_crime_statistics()
            results["loaded"].append("crime_statistics")
            results["total_records"] += len(crime_data.get("data", []))
        except Exception as e:
            results["failed"].append({"type": "crime_statistics", "error": str(e)})
        
        try:
            social_data = await self.social_service.load_social_indicators()
            results["loaded"].append("social_indicators")
            results["total_records"] += len(social_data.get("data", []))
        except Exception as e:
            results["failed"].append({"type": "social_indicators", "error": str(e)})
        
        self._loaded = True
        return results
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all demographic data."""
        return {
            "city": "Riviera Beach",
            "loaded": self._loaded,
            "census": self.census_service.get_summary(),
            "crime": self.crime_service.get_summary(),
            "social": self.social_service.get_summary()
        }
