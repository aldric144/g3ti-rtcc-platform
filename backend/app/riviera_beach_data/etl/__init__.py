"""
ETL (Extract, Transform, Load) Module for Riviera Beach Data Lake.

Provides data pipelines for:
- GIS shapefiles → GeoJSON → PostGIS
- Public APIs → JSON ingestion → Data Lake
- Scheduled NOAA/NWS updates
- Census → static load
- UCR crime → analytics tables
- Hydrant maps → geospatial overlay
"""

from app.riviera_beach_data.etl.pipeline_manager import ETLPipelineManager
from app.riviera_beach_data.etl.gis_importer import GISShapefileImporter
from app.riviera_beach_data.etl.api_ingester import APIDataIngester
from app.riviera_beach_data.etl.scheduled_updater import ScheduledDataUpdater

__all__ = [
    "ETLPipelineManager",
    "GISShapefileImporter",
    "APIDataIngester",
    "ScheduledDataUpdater",
]
