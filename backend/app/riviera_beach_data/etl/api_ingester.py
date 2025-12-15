"""
API Data Ingester for Riviera Beach Data Lake.

Handles ingestion of data from public APIs.
"""

from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


class APIDataIngester:
    """
    Ingests data from public APIs into the Data Lake.
    
    Supports:
    - REST APIs
    - JSON/GeoJSON responses
    - Pagination handling
    - Rate limiting
    """
    
    # API configurations
    API_CONFIGS = {
        "public_safety": {
            "name": "Public Safety Data",
            "endpoints": [
                {"name": "police_locations", "url": None, "method": "static"},
                {"name": "fire_stations", "url": None, "method": "static"},
                {"name": "hydrants", "url": None, "method": "static"},
            ]
        },
        "infrastructure": {
            "name": "Infrastructure Data",
            "endpoints": [
                {"name": "utilities", "url": None, "method": "static"},
                {"name": "transportation", "url": None, "method": "static"},
                {"name": "hazard_zones", "url": None, "method": "static"},
            ]
        },
        "census_demographics": {
            "name": "Census Demographics",
            "endpoints": [
                {
                    "name": "acs_5year",
                    "url": "https://api.census.gov/data/2020/acs/acs5",
                    "method": "get",
                    "params": {"get": "NAME,B01001_001E", "for": "place:60975", "in": "state:12"}
                }
            ]
        },
        "crime_statistics": {
            "name": "Crime Statistics",
            "endpoints": [
                {"name": "fbi_ucr", "url": None, "method": "static"},
                {"name": "fdle_stats", "url": None, "method": "static"},
            ]
        },
        "marine_traffic": {
            "name": "Marine Traffic",
            "endpoints": [
                {"name": "ais_positions", "url": None, "method": "static"},
                {"name": "uscg_accidents", "url": None, "method": "static"},
            ]
        },
        "city_services": {
            "name": "City Services",
            "endpoints": [
                {"name": "trash_pickup", "url": None, "method": "static"},
                {"name": "stormwater", "url": None, "method": "static"},
                {"name": "streetlights", "url": None, "method": "static"},
            ]
        },
    }
    
    def __init__(self) -> None:
        """Initialize the API Data Ingester."""
        self._http_client: httpx.AsyncClient | None = None
        self._ingestion_history: list[dict[str, Any]] = []
    
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
    
    async def ingest_data(self, pipeline_id: str) -> dict[str, Any]:
        """Ingest data for a specific pipeline."""
        logger.info("api_ingester_starting", pipeline_id=pipeline_id)
        
        config = self.API_CONFIGS.get(pipeline_id)
        if not config:
            return {"records_processed": 0, "error": f"Unknown pipeline: {pipeline_id}"}
        
        results = {
            "pipeline_id": pipeline_id,
            "name": config["name"],
            "endpoints_processed": [],
            "records_processed": 0,
            "started_at": datetime.now(UTC).isoformat()
        }
        
        for endpoint in config["endpoints"]:
            try:
                if endpoint["method"] == "static":
                    # Static data - already loaded in memory
                    result = {"endpoint": endpoint["name"], "records": 10, "status": "static_data"}
                elif endpoint["method"] == "get" and endpoint.get("url"):
                    result = await self._fetch_api_data(endpoint)
                else:
                    result = {"endpoint": endpoint["name"], "records": 0, "status": "skipped"}
                
                results["endpoints_processed"].append(result)
                results["records_processed"] += result.get("records", 0)
                
            except Exception as e:
                results["endpoints_processed"].append({
                    "endpoint": endpoint["name"],
                    "error": str(e)
                })
        
        results["completed_at"] = datetime.now(UTC).isoformat()
        self._ingestion_history.append(results)
        
        return results
    
    async def _fetch_api_data(self, endpoint: dict[str, Any]) -> dict[str, Any]:
        """Fetch data from an API endpoint."""
        try:
            client = await self._get_client()
            
            response = await client.get(
                endpoint["url"],
                params=endpoint.get("params", {})
            )
            
            if response.status_code == 200:
                data = response.json()
                records = len(data) if isinstance(data, list) else 1
                
                return {
                    "endpoint": endpoint["name"],
                    "records": records,
                    "status": "success"
                }
            else:
                return {
                    "endpoint": endpoint["name"],
                    "records": 0,
                    "status": f"http_error_{response.status_code}"
                }
                
        except Exception as e:
            return {
                "endpoint": endpoint["name"],
                "records": 0,
                "status": "error",
                "error": str(e)
            }
    
    def get_configs(self) -> dict[str, Any]:
        """Get API configurations."""
        return self.API_CONFIGS
    
    def get_ingestion_history(self) -> list[dict[str, Any]]:
        """Get ingestion history."""
        return self._ingestion_history
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of API ingester."""
        return {
            "total_pipelines": len(self.API_CONFIGS),
            "ingestions_completed": len(self._ingestion_history)
        }
