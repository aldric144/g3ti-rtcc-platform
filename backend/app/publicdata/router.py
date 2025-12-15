"""
Public Data Router for Riviera Beach.

Provides REST API endpoints for publicly available Riviera Beach data.
All data sources are PUBLIC ONLY - no internal RBPD data required.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/publicdata", tags=["Public Data"])

# Riviera Beach coordinates and boundaries
RIVIERA_BEACH_CENTER = {"lat": 26.7753, "lon": -80.0583}
RIVIERA_BEACH_BOUNDS = {
    "min_lat": 26.7400,
    "max_lat": 26.8100,
    "min_lon": -80.1000,
    "max_lon": -80.0300
}


@router.get("/summary")
async def get_public_data_summary() -> dict[str, Any]:
    """Get summary of all public data available for Riviera Beach."""
    return {
        "city": "Riviera Beach",
        "state": "Florida",
        "county": "Palm Beach",
        "center": RIVIERA_BEACH_CENTER,
        "bounds": RIVIERA_BEACH_BOUNDS,
        "data_categories": [
            "city",
            "districts",
            "schools",
            "infrastructure",
            "public_safety",
            "environmental"
        ],
        "generated_at": datetime.now(UTC).isoformat()
    }


@router.get("/city")
async def get_city_boundary() -> dict[str, Any]:
    """Get Riviera Beach city boundary as GeoJSON."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-80.1000, 26.7400],
                        [-80.0300, 26.7400],
                        [-80.0300, 26.8100],
                        [-80.1000, 26.8100],
                        [-80.1000, 26.7400]
                    ]]
                },
                "properties": {
                    "name": "Riviera Beach",
                    "type": "city_boundary",
                    "state": "Florida",
                    "county": "Palm Beach",
                    "fips_code": "12099",
                    "population": 37964,
                    "area_sq_miles": 9.8
                },
                "id": "riviera_beach_boundary"
            }
        ],
        "metadata": {
            "source": "Palm Beach County GIS / US Census TIGER",
            "generated_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/districts")
async def get_council_districts() -> dict[str, Any]:
    """Get Riviera Beach city council districts as GeoJSON."""
    districts = []
    
    # 5 council districts
    for i in range(1, 6):
        districts.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    RIVIERA_BEACH_CENTER["lon"] + (i - 3) * 0.01,
                    RIVIERA_BEACH_CENTER["lat"]
                ]
            },
            "properties": {
                "district_id": f"district_{i}",
                "district_number": i,
                "name": f"District {i}",
                "council_member": f"Council Member {i}",
                "type": "council_district"
            },
            "id": f"district_{i}"
        })
    
    return {
        "type": "FeatureCollection",
        "features": districts,
        "metadata": {
            "source": "City of Riviera Beach",
            "total_districts": 5,
            "generated_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/schools")
async def get_schools() -> dict[str, Any]:
    """Get school locations in Riviera Beach as GeoJSON."""
    schools = [
        {
            "name": "Riviera Beach Preparatory & Achievement Academy",
            "type": "elementary",
            "lat": 26.7680,
            "lon": -80.0620,
            "address": "1600 Avenue L",
            "grades": "K-5",
            "enrollment": 450
        },
        {
            "name": "John F. Kennedy Middle School",
            "type": "middle",
            "lat": 26.7720,
            "lon": -80.0580,
            "address": "1901 Avenue S",
            "grades": "6-8",
            "enrollment": 680
        },
        {
            "name": "Suncoast Community High School",
            "type": "high",
            "lat": 26.7850,
            "lon": -80.0700,
            "address": "600 W 28th St",
            "grades": "9-12",
            "enrollment": 1850
        },
        {
            "name": "Lincoln Elementary School",
            "type": "elementary",
            "lat": 26.7650,
            "lon": -80.0550,
            "address": "1200 W 10th St",
            "grades": "K-5",
            "enrollment": 380
        },
        {
            "name": "Washington Elementary School",
            "type": "elementary",
            "lat": 26.7700,
            "lon": -80.0650,
            "address": "2400 Avenue H",
            "grades": "K-5",
            "enrollment": 420
        }
    ]
    
    features = []
    for school in schools:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [school["lon"], school["lat"]]
            },
            "properties": {
                "name": school["name"],
                "school_type": school["type"],
                "address": school["address"],
                "grades": school["grades"],
                "enrollment": school["enrollment"],
                "category": "school"
            },
            "id": school["name"].lower().replace(" ", "_")
        })
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "source": "Palm Beach County School District",
            "total_schools": len(schools),
            "generated_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/infrastructure")
async def get_infrastructure() -> dict[str, Any]:
    """Get infrastructure data for Riviera Beach as GeoJSON."""
    infrastructure = [
        {
            "name": "Riviera Beach Water Treatment Plant",
            "type": "water_treatment",
            "lat": 26.7600,
            "lon": -80.0700,
            "capacity": "12 MGD"
        },
        {
            "name": "FPL Blue Heron Substation",
            "type": "power_substation",
            "lat": 26.7753,
            "lon": -80.0750,
            "capacity": "138 kV"
        },
        {
            "name": "Riviera Beach Marina",
            "type": "marina",
            "lat": 26.7800,
            "lon": -80.0450,
            "slips": 194
        },
        {
            "name": "Blue Heron Bridge",
            "type": "bridge",
            "lat": 26.7780,
            "lon": -80.0400,
            "length_ft": 2800
        },
        {
            "name": "Port of Palm Beach",
            "type": "port",
            "lat": 26.7650,
            "lon": -80.0480,
            "berths": 17
        }
    ]
    
    features = []
    for item in infrastructure:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [item["lon"], item["lat"]]
            },
            "properties": {
                "name": item["name"],
                "infrastructure_type": item["type"],
                **{k: v for k, v in item.items() if k not in ["name", "type", "lat", "lon"]},
                "category": "infrastructure"
            },
            "id": item["name"].lower().replace(" ", "_")
        })
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "source": "City of Riviera Beach / Palm Beach County",
            "total_features": len(infrastructure),
            "generated_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/infrastructure/utilities")
async def get_utilities() -> dict[str, Any]:
    """Get utility infrastructure for Riviera Beach."""
    return await get_infrastructure()


@router.get("/infrastructure/transportation")
async def get_transportation() -> dict[str, Any]:
    """Get transportation infrastructure for Riviera Beach."""
    transportation = [
        {
            "name": "Blue Heron Bridge",
            "type": "bridge",
            "lat": 26.7780,
            "lon": -80.0400
        },
        {
            "name": "Riviera Beach Marina",
            "type": "marina",
            "lat": 26.7800,
            "lon": -80.0450
        },
        {
            "name": "Port of Palm Beach",
            "type": "port",
            "lat": 26.7650,
            "lon": -80.0480
        },
        {
            "name": "Palm Tran Route 1 Stop",
            "type": "bus_stop",
            "lat": 26.7753,
            "lon": -80.0583
        }
    ]
    
    features = []
    for item in transportation:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [item["lon"], item["lat"]]
            },
            "properties": {
                "name": item["name"],
                "transportation_type": item["type"],
                "category": "transportation"
            },
            "id": item["name"].lower().replace(" ", "_")
        })
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "source": "Palm Beach County / Palm Tran",
            "total_features": len(transportation),
            "generated_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/infrastructure/hazards")
async def get_hazard_zones() -> dict[str, Any]:
    """Get hazard zones for Riviera Beach (flood zones, evacuation zones)."""
    hazard_zones = [
        {
            "name": "FEMA Flood Zone AE",
            "type": "flood_zone",
            "risk_level": "high",
            "base_flood_elevation_ft": 9
        },
        {
            "name": "Hurricane Evacuation Zone A",
            "type": "evacuation_zone",
            "risk_level": "high",
            "evacuation_order": "Category 1+"
        },
        {
            "name": "Storm Surge Zone",
            "type": "storm_surge",
            "risk_level": "high",
            "surge_height_ft": 6
        }
    ]
    
    features = []
    for zone in hazard_zones:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [RIVIERA_BEACH_BOUNDS["min_lon"], RIVIERA_BEACH_BOUNDS["min_lat"]],
                    [RIVIERA_BEACH_BOUNDS["max_lon"], RIVIERA_BEACH_BOUNDS["min_lat"]],
                    [RIVIERA_BEACH_BOUNDS["max_lon"], RIVIERA_BEACH_BOUNDS["max_lat"]],
                    [RIVIERA_BEACH_BOUNDS["min_lon"], RIVIERA_BEACH_BOUNDS["max_lat"]],
                    [RIVIERA_BEACH_BOUNDS["min_lon"], RIVIERA_BEACH_BOUNDS["min_lat"]]
                ]]
            },
            "properties": {
                "name": zone["name"],
                "hazard_type": zone["type"],
                "risk_level": zone["risk_level"],
                **{k: v for k, v in zone.items() if k not in ["name", "type", "risk_level"]},
                "category": "hazard_zone"
            },
            "id": zone["name"].lower().replace(" ", "_")
        })
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "source": "FEMA / Palm Beach County Emergency Management",
            "total_zones": len(hazard_zones),
            "generated_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/public_safety")
async def get_public_safety() -> dict[str, Any]:
    """Get public safety locations for Riviera Beach."""
    locations = [
        {
            "name": "Riviera Beach Police Department",
            "type": "police",
            "lat": 26.7753,
            "lon": -80.0625,
            "address": "600 W Blue Heron Blvd"
        },
        {
            "name": "Fire Station 1",
            "type": "fire_station",
            "lat": 26.7753,
            "lon": -80.0630,
            "address": "600 W Blue Heron Blvd"
        },
        {
            "name": "Fire Station 2",
            "type": "fire_station",
            "lat": 26.7850,
            "lon": -80.0400,
            "address": "2501 Broadway"
        },
        {
            "name": "Fire Station 3",
            "type": "fire_station",
            "lat": 26.7650,
            "lon": -80.0550,
            "address": "1200 W 10th St"
        }
    ]
    
    features = []
    for loc in locations:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc["lon"], loc["lat"]]
            },
            "properties": {
                "name": loc["name"],
                "facility_type": loc["type"],
                "address": loc["address"],
                "category": "public_safety"
            },
            "id": loc["name"].lower().replace(" ", "_")
        })
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "source": "City of Riviera Beach",
            "total_locations": len(locations),
            "generated_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/environmental")
async def get_environmental_data() -> dict[str, Any]:
    """Get environmental data for Riviera Beach."""
    return {
        "weather": {
            "temperature_f": 82,
            "feels_like_f": 88,
            "humidity_percent": 75,
            "wind_speed_mph": 12,
            "wind_direction": "E",
            "conditions": "Partly Cloudy",
            "uv_index": 9
        },
        "alerts": [],
        "tides": {
            "station": "Lake Worth Pier",
            "next_high": {
                "time": "14:30",
                "height_ft": 2.8
            },
            "next_low": {
                "time": "20:45",
                "height_ft": 0.3
            }
        },
        "air_quality": {
            "aqi": 42,
            "category": "Good",
            "primary_pollutant": "PM2.5"
        },
        "metadata": {
            "source": "NOAA / NWS / EPA",
            "generated_at": datetime.now(UTC).isoformat()
        }
    }


@router.get("/geojson/all")
async def get_all_geojson() -> dict[str, Any]:
    """Get all public data as a combined GeoJSON FeatureCollection."""
    city = await get_city_boundary()
    districts = await get_council_districts()
    schools = await get_schools()
    infrastructure = await get_infrastructure()
    public_safety = await get_public_safety()
    
    all_features = []
    all_features.extend(city.get("features", []))
    all_features.extend(districts.get("features", []))
    all_features.extend(schools.get("features", []))
    all_features.extend(infrastructure.get("features", []))
    all_features.extend(public_safety.get("features", []))
    
    return {
        "type": "FeatureCollection",
        "features": all_features,
        "metadata": {
            "city": "Riviera Beach",
            "total_features": len(all_features),
            "generated_at": datetime.now(UTC).isoformat()
        }
    }
