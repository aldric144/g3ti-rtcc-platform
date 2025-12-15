"""
ETL Pipeline Manager for Riviera Beach Data Lake.

Coordinates all data import pipelines.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from app.core.logging import get_logger
from app.riviera_beach_data.etl.gis_importer import GISShapefileImporter
from app.riviera_beach_data.etl.api_ingester import APIDataIngester
from app.riviera_beach_data.etl.scheduled_updater import ScheduledDataUpdater

logger = get_logger(__name__)


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class ETLPipelineManager:
    """
    Manages all ETL pipelines for Riviera Beach Data Lake.
    
    Pipelines:
    - GIS data import (shapefiles, GeoJSON)
    - Public API ingestion
    - Scheduled data updates (weather, alerts)
    - Static data loads (census, crime stats)
    """
    
    # Pipeline definitions
    PIPELINES = [
        {
            "pipeline_id": "gis_boundaries",
            "name": "GIS Boundary Import",
            "description": "Import city boundaries, districts, census tracts",
            "source": "Palm Beach County GIS / Census TIGER",
            "schedule": "weekly",
            "priority": 1
        },
        {
            "pipeline_id": "public_safety",
            "name": "Public Safety Data",
            "description": "Import police, fire, hydrant locations",
            "source": "City of Riviera Beach",
            "schedule": "daily",
            "priority": 1
        },
        {
            "pipeline_id": "infrastructure",
            "name": "Infrastructure Import",
            "description": "Import utilities, transportation, hazard zones",
            "source": "Multiple public sources",
            "schedule": "weekly",
            "priority": 2
        },
        {
            "pipeline_id": "weather_alerts",
            "name": "Weather & Alerts",
            "description": "NOAA weather, NWS alerts, tide data",
            "source": "NOAA / NWS APIs",
            "schedule": "hourly",
            "priority": 1
        },
        {
            "pipeline_id": "census_demographics",
            "name": "Census Demographics",
            "description": "US Census ACS demographic data",
            "source": "US Census Bureau",
            "schedule": "yearly",
            "priority": 3
        },
        {
            "pipeline_id": "crime_statistics",
            "name": "Crime Statistics",
            "description": "FBI UCR / FDLE crime data",
            "source": "FBI / FDLE",
            "schedule": "monthly",
            "priority": 2
        },
        {
            "pipeline_id": "marine_traffic",
            "name": "Marine Traffic",
            "description": "AIS vessel tracking, boating accidents",
            "source": "AIS / USCG",
            "schedule": "realtime",
            "priority": 1
        },
        {
            "pipeline_id": "city_services",
            "name": "City Services",
            "description": "Trash pickup, stormwater, streetlights",
            "source": "City of Riviera Beach",
            "schedule": "weekly",
            "priority": 2
        },
    ]
    
    def __init__(self) -> None:
        """Initialize the ETL Pipeline Manager."""
        self.gis_importer = GISShapefileImporter()
        self.api_ingester = APIDataIngester()
        self.scheduled_updater = ScheduledDataUpdater()
        self._pipeline_status: dict[str, PipelineStatus] = {
            p["pipeline_id"]: PipelineStatus.PENDING for p in self.PIPELINES
        }
        self._last_run: dict[str, datetime | None] = {
            p["pipeline_id"]: None for p in self.PIPELINES
        }
    
    async def run_all_pipelines(self) -> dict[str, Any]:
        """Run all ETL pipelines."""
        logger.info("etl_pipeline_manager_starting")
        
        results = {
            "pipelines_run": [],
            "pipelines_failed": [],
            "total_records_processed": 0,
            "started_at": datetime.now(UTC).isoformat()
        }
        
        for pipeline in sorted(self.PIPELINES, key=lambda p: p["priority"]):
            pipeline_id = pipeline["pipeline_id"]
            
            try:
                self._pipeline_status[pipeline_id] = PipelineStatus.RUNNING
                
                # Run the appropriate pipeline
                if pipeline_id == "gis_boundaries":
                    result = await self.gis_importer.import_all()
                elif pipeline_id == "weather_alerts":
                    result = await self.scheduled_updater.update_weather()
                else:
                    result = await self.api_ingester.ingest_data(pipeline_id)
                
                self._pipeline_status[pipeline_id] = PipelineStatus.COMPLETED
                self._last_run[pipeline_id] = datetime.now(UTC)
                
                results["pipelines_run"].append({
                    "pipeline_id": pipeline_id,
                    "name": pipeline["name"],
                    "records": result.get("records_processed", 0)
                })
                results["total_records_processed"] += result.get("records_processed", 0)
                
            except Exception as e:
                self._pipeline_status[pipeline_id] = PipelineStatus.FAILED
                results["pipelines_failed"].append({
                    "pipeline_id": pipeline_id,
                    "error": str(e)
                })
        
        results["completed_at"] = datetime.now(UTC).isoformat()
        
        logger.info(
            "etl_pipeline_manager_completed",
            pipelines_run=len(results["pipelines_run"]),
            pipelines_failed=len(results["pipelines_failed"])
        )
        
        return results
    
    async def run_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        """Run a specific pipeline."""
        pipeline = next((p for p in self.PIPELINES if p["pipeline_id"] == pipeline_id), None)
        if not pipeline:
            raise ValueError(f"Unknown pipeline: {pipeline_id}")
        
        self._pipeline_status[pipeline_id] = PipelineStatus.RUNNING
        
        try:
            if pipeline_id == "gis_boundaries":
                result = await self.gis_importer.import_all()
            elif pipeline_id == "weather_alerts":
                result = await self.scheduled_updater.update_weather()
            else:
                result = await self.api_ingester.ingest_data(pipeline_id)
            
            self._pipeline_status[pipeline_id] = PipelineStatus.COMPLETED
            self._last_run[pipeline_id] = datetime.now(UTC)
            
            return result
            
        except Exception as e:
            self._pipeline_status[pipeline_id] = PipelineStatus.FAILED
            raise
    
    def get_pipeline_status(self) -> dict[str, Any]:
        """Get status of all pipelines."""
        return {
            p["pipeline_id"]: {
                "name": p["name"],
                "status": self._pipeline_status[p["pipeline_id"]].value,
                "last_run": self._last_run[p["pipeline_id"]].isoformat() if self._last_run[p["pipeline_id"]] else None,
                "schedule": p["schedule"]
            }
            for p in self.PIPELINES
        }
    
    def get_pipelines(self) -> list[dict[str, Any]]:
        """Get pipeline definitions."""
        return self.PIPELINES
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of ETL pipelines."""
        completed = sum(1 for s in self._pipeline_status.values() if s == PipelineStatus.COMPLETED)
        failed = sum(1 for s in self._pipeline_status.values() if s == PipelineStatus.FAILED)
        
        return {
            "total_pipelines": len(self.PIPELINES),
            "completed": completed,
            "failed": failed,
            "pending": len(self.PIPELINES) - completed - failed
        }
