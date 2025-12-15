"""
API Router for Riviera Beach Public Data.

Provides REST API endpoints for all Riviera Beach public data layers.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.riviera_beach_data.gis import GISBoundaryLoader
from app.riviera_beach_data.public_safety import PublicSafetyDataLoader
from app.riviera_beach_data.infrastructure import InfrastructureDataLoader
from app.riviera_beach_data.schools import SchoolsDataLoader
from app.riviera_beach_data.demographics import DemographicsDataLoader
from app.riviera_beach_data.environmental import EnvironmentalDataLoader
from app.riviera_beach_data.marina import MarinaDataLoader
from app.riviera_beach_data.city_services import CityServicesDataLoader
from app.riviera_beach_data.digital_twin import DigitalTwinInitializer
from app.riviera_beach_data.etl import ETLPipelineManager

logger = get_logger(__name__)

router = APIRouter(prefix="/riviera-beach", tags=["Riviera Beach Public Data"])

# Initialize data loaders
gis_loader = GISBoundaryLoader()
public_safety_loader = PublicSafetyDataLoader()
infrastructure_loader = InfrastructureDataLoader()
schools_loader = SchoolsDataLoader()
demographics_loader = DemographicsDataLoader()
environmental_loader = EnvironmentalDataLoader()
marina_loader = MarinaDataLoader()
city_services_loader = CityServicesDataLoader()
digital_twin = DigitalTwinInitializer()
etl_manager = ETLPipelineManager()


@router.get("/summary")
async def get_data_summary() -> dict[str, Any]:
    """Get summary of all Riviera Beach public data."""
    return {
        "city": "Riviera Beach",
        "state": "Florida",
        "county": "Palm Beach",
        "data_layers": {
            "gis": gis_loader.get_summary(),
            "public_safety": public_safety_loader.get_summary(),
            "infrastructure": infrastructure_loader.get_summary(),
            "schools": schools_loader.get_summary(),
            "demographics": demographics_loader.get_summary(),
            "environmental": environmental_loader.get_summary(),
            "marina": marina_loader.get_summary(),
            "city_services": city_services_loader.get_summary(),
            "digital_twin": digital_twin.get_summary(),
        },
        "etl_status": etl_manager.get_summary(),
        "generated_at": datetime.now(UTC).isoformat()
    }


# GIS Endpoints
@router.get("/gis/boundaries")
async def get_all_boundaries() -> dict[str, Any]:
    """Get all GIS boundary data."""
    return await gis_loader.load_all_boundaries()


@router.get("/gis/city-boundary")
async def get_city_boundary() -> dict[str, Any]:
    """Get Riviera Beach city boundary."""
    return await gis_loader.load_city_boundary()


@router.get("/gis/council-districts")
async def get_council_districts() -> dict[str, Any]:
    """Get city council districts."""
    return await gis_loader.load_council_districts()


@router.get("/gis/census-tracts")
async def get_census_tracts() -> dict[str, Any]:
    """Get census tracts."""
    return await gis_loader.load_census_tracts()


@router.get("/gis/roads")
async def get_road_centerlines() -> dict[str, Any]:
    """Get road centerlines."""
    return await gis_loader.load_road_centerlines()


# Public Safety Endpoints
@router.get("/public-safety")
async def get_public_safety_data() -> dict[str, Any]:
    """Get all public safety data."""
    return await public_safety_loader.load_all()


@router.get("/public-safety/police")
async def get_police_locations() -> dict[str, Any]:
    """Get police facility locations."""
    return public_safety_loader.police_service.get_locations_geojson()


@router.get("/public-safety/fire-stations")
async def get_fire_stations() -> dict[str, Any]:
    """Get fire station locations."""
    return public_safety_loader.fire_service.get_stations_geojson()


@router.get("/public-safety/hydrants")
async def get_hydrants() -> dict[str, Any]:
    """Get fire hydrant locations."""
    return public_safety_loader.hydrant_service.get_hydrants_geojson()


# Infrastructure Endpoints
@router.get("/infrastructure")
async def get_infrastructure_data() -> dict[str, Any]:
    """Get all infrastructure data."""
    return await infrastructure_loader.load_all()


@router.get("/infrastructure/utilities")
async def get_utilities() -> dict[str, Any]:
    """Get utility infrastructure."""
    return infrastructure_loader.utilities_service.get_utilities_geojson()


@router.get("/infrastructure/transportation")
async def get_transportation() -> dict[str, Any]:
    """Get transportation infrastructure."""
    return infrastructure_loader.transportation_service.get_transportation_geojson()


@router.get("/infrastructure/hazard-zones")
async def get_hazard_zones() -> dict[str, Any]:
    """Get hazard zones (flood, storm surge, evacuation)."""
    return infrastructure_loader.hazard_service.get_hazard_zones_geojson()


# Schools Endpoints
@router.get("/schools")
async def get_schools_data() -> dict[str, Any]:
    """Get all schools and youth facility data."""
    return await schools_loader.load_all()


@router.get("/schools/locations")
async def get_school_locations() -> dict[str, Any]:
    """Get school locations."""
    return schools_loader.school_service.get_schools_geojson()


@router.get("/schools/youth-facilities")
async def get_youth_facilities() -> dict[str, Any]:
    """Get youth facility locations."""
    return schools_loader.youth_service.get_facilities_geojson()


# Demographics Endpoints
@router.get("/demographics")
async def get_demographics_data() -> dict[str, Any]:
    """Get all demographic data."""
    return await demographics_loader.load_all()


@router.get("/demographics/census")
async def get_census_data() -> dict[str, Any]:
    """Get census demographic data."""
    return await demographics_loader.census_service.load_census_data()


@router.get("/demographics/crime")
async def get_crime_statistics() -> dict[str, Any]:
    """Get crime statistics."""
    return await demographics_loader.crime_service.load_crime_statistics()


@router.get("/demographics/social")
async def get_social_indicators() -> dict[str, Any]:
    """Get social indicator data."""
    return await demographics_loader.social_service.load_social_indicators()


# Environmental Endpoints
@router.get("/environmental")
async def get_environmental_data() -> dict[str, Any]:
    """Get all environmental data."""
    return await environmental_loader.load_all()


@router.get("/environmental/weather")
async def get_weather() -> dict[str, Any]:
    """Get current weather and forecast."""
    return await environmental_loader.weather_service.load_weather_data()


@router.get("/environmental/alerts")
async def get_weather_alerts() -> dict[str, Any]:
    """Get active weather alerts."""
    return await environmental_loader.alert_service.load_alerts()


@router.get("/environmental/tides")
async def get_tides() -> dict[str, Any]:
    """Get tide predictions."""
    return await environmental_loader.tide_service.load_tide_data()


# Marina Endpoints
@router.get("/marina")
async def get_marina_data() -> dict[str, Any]:
    """Get all marina and waterway data."""
    return await marina_loader.load_all()


@router.get("/marina/layout")
async def get_marina_layout() -> dict[str, Any]:
    """Get marina layout and facilities."""
    return await marina_loader.marina_service.load_marina_data()


@router.get("/marina/waterways")
async def get_waterways() -> dict[str, Any]:
    """Get waterway and navigation data."""
    return await marina_loader.waterway_service.load_waterways()


@router.get("/marina/traffic")
async def get_marine_traffic() -> dict[str, Any]:
    """Get marine traffic data."""
    return await marina_loader.traffic_service.load_traffic_data()


# City Services Endpoints
@router.get("/city-services")
async def get_city_services_data() -> dict[str, Any]:
    """Get all city services data."""
    return await city_services_loader.load_all()


@router.get("/city-services/trash-pickup")
async def get_trash_pickup() -> dict[str, Any]:
    """Get trash pickup zones and schedules."""
    return await city_services_loader.trash_service.load_pickup_zones()


@router.get("/city-services/stormwater")
async def get_stormwater() -> dict[str, Any]:
    """Get stormwater infrastructure."""
    return await city_services_loader.stormwater_service.load_infrastructure()


@router.get("/city-services/streetlights")
async def get_streetlights() -> dict[str, Any]:
    """Get streetlight locations."""
    return await city_services_loader.streetlight_service.load_streetlights()


# Digital Twin Endpoints
@router.get("/digital-twin")
async def get_digital_twin_status() -> dict[str, Any]:
    """Get Digital Twin status and configuration."""
    return {
        "config": digital_twin.get_config(),
        "layers": digital_twin.get_layers(),
        "layer_status": digital_twin.get_layer_status(),
        "summary": digital_twin.get_summary()
    }


@router.post("/digital-twin/initialize")
async def initialize_digital_twin() -> dict[str, Any]:
    """Initialize the Digital Twin with all public data."""
    return await digital_twin.initialize()


# ETL Endpoints
@router.get("/etl/status")
async def get_etl_status() -> dict[str, Any]:
    """Get ETL pipeline status."""
    return {
        "pipelines": etl_manager.get_pipelines(),
        "status": etl_manager.get_pipeline_status(),
        "summary": etl_manager.get_summary()
    }


@router.post("/etl/run-all")
async def run_all_etl_pipelines() -> dict[str, Any]:
    """Run all ETL pipelines."""
    return await etl_manager.run_all_pipelines()


@router.post("/etl/run/{pipeline_id}")
async def run_etl_pipeline(pipeline_id: str) -> dict[str, Any]:
    """Run a specific ETL pipeline."""
    try:
        return await etl_manager.run_pipeline(pipeline_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# GeoJSON Combined Endpoint
@router.get("/geojson/all")
async def get_all_geojson() -> dict[str, Any]:
    """Get all data as a combined GeoJSON FeatureCollection."""
    features = []
    
    # Collect features from all loaders
    features.extend(public_safety_loader.get_all_geojson().get("features", []))
    features.extend(infrastructure_loader.get_all_geojson().get("features", []))
    features.extend(schools_loader.get_all_geojson().get("features", []))
    features.extend(marina_loader.get_all_geojson().get("features", []))
    features.extend(city_services_loader.get_all_geojson().get("features", []))
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "city": "Riviera Beach",
            "total_features": len(features),
            "generated_at": datetime.now(UTC).isoformat()
        }
    }
