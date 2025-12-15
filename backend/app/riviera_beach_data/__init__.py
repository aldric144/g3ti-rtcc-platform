"""
Riviera Beach Public Data Integration Package.

Phase RIV-PUBDATA-01: Comprehensive integration of publicly available
Riviera Beach, Palm Beach County, and State of Florida datasets into
the RTCC Data Lake and GIS Engine.

This package provides:
- GIS & Boundary Data (city boundary, council districts, census tracts)
- Public Safety Infrastructure (RBPD locations, fire stations, hydrants)
- Critical Infrastructure Layers (utilities, transportation, hazards)
- Schools & Youth Infrastructure
- Demographics, Crime Context & Social Data
- Environmental & Emergency Data (NOAA, NWS, weather)
- Marina, Coastline & Waterway Safety Data
- City Services Data
- Digital Twin Initialization
- Data Lake Import Pipelines (ETL jobs)

All data sources are PUBLIC ONLY - no internal RBPD data required.
"""

from app.riviera_beach_data.gis import (
    GISBoundaryLoader,
    CityBoundaryService,
    CouncilDistrictService,
    CensusTractService,
    RoadCenterlineService,
)
from app.riviera_beach_data.public_safety import (
    PublicSafetyDataLoader,
    FireStationService,
    HydrantService,
    PoliceLocationService,
)
from app.riviera_beach_data.infrastructure import (
    InfrastructureDataLoader,
    UtilityService,
    TransportationService,
    HazardZoneService,
)
from app.riviera_beach_data.schools import (
    SchoolsDataLoader,
    SchoolLocationService,
    YouthFacilityService,
)
from app.riviera_beach_data.demographics import (
    DemographicsDataLoader,
    CensusDataService,
    CrimeStatisticsService,
    SocialIndicatorService,
)
from app.riviera_beach_data.environmental import (
    EnvironmentalDataLoader,
    NOAAWeatherService,
    NWSAlertService,
    TideChartService,
)
from app.riviera_beach_data.marina import (
    MarinaDataLoader,
    MarinaLayoutService,
    WaterwayService,
    MarineTrafficService,
)
from app.riviera_beach_data.city_services import (
    CityServicesDataLoader,
    TrashPickupService,
    StormwaterService,
    StreetlightService,
)
from app.riviera_beach_data.digital_twin import (
    DigitalTwinInitializer,
    BuildingFootprintService,
    RoadNetworkService,
)
from app.riviera_beach_data.etl import (
    ETLPipelineManager,
    GISShapefileImporter,
    APIDataIngester,
    ScheduledDataUpdater,
)
from app.riviera_beach_data.api import router as riviera_beach_router

__all__ = [
    # GIS
    "GISBoundaryLoader",
    "CityBoundaryService",
    "CouncilDistrictService",
    "CensusTractService",
    "RoadCenterlineService",
    # Public Safety
    "PublicSafetyDataLoader",
    "FireStationService",
    "HydrantService",
    "PoliceLocationService",
    # Infrastructure
    "InfrastructureDataLoader",
    "UtilityService",
    "TransportationService",
    "HazardZoneService",
    # Schools
    "SchoolsDataLoader",
    "SchoolLocationService",
    "YouthFacilityService",
    # Demographics
    "DemographicsDataLoader",
    "CensusDataService",
    "CrimeStatisticsService",
    "SocialIndicatorService",
    # Environmental
    "EnvironmentalDataLoader",
    "NOAAWeatherService",
    "NWSAlertService",
    "TideChartService",
    # Marina
    "MarinaDataLoader",
    "MarinaLayoutService",
    "WaterwayService",
    "MarineTrafficService",
    # City Services
    "CityServicesDataLoader",
    "TrashPickupService",
    "StormwaterService",
    "StreetlightService",
    # Digital Twin
    "DigitalTwinInitializer",
    "BuildingFootprintService",
    "RoadNetworkService",
    # ETL
    "ETLPipelineManager",
    "GISShapefileImporter",
    "APIDataIngester",
    "ScheduledDataUpdater",
    # API Router
    "riviera_beach_router",
]
