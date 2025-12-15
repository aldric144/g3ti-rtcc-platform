"""
Demographics, Crime Context & Social Data Module for Riviera Beach.

Loads and manages demographic and social indicator data including:
- US Census demographics (population, age, income, housing)
- FBI UCR crime statistics
- Florida DCF data
- Social indicators (poverty, overdose, DV shelters)
"""

from app.riviera_beach_data.demographics.data_loader import DemographicsDataLoader
from app.riviera_beach_data.demographics.census_data import CensusDataService
from app.riviera_beach_data.demographics.crime_statistics import CrimeStatisticsService
from app.riviera_beach_data.demographics.social_indicators import SocialIndicatorService

__all__ = [
    "DemographicsDataLoader",
    "CensusDataService",
    "CrimeStatisticsService",
    "SocialIndicatorService",
]
