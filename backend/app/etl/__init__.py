"""
ETL Pipeline Module for G3TI RTCC-UIP Data Lake.

This module provides Extract-Transform-Load capabilities including:
- Real-time incident ingestion pipelines
- Batch processing for historical data imports
- Data transformation and normalization
- Data validation and quality checks
- Pipeline monitoring and alerting

The ETL module integrates with:
- Multiple source systems (CAD, RMS, ShotSpotter, LPR)
- Data Lake storage layer
- Quality monitoring systems
"""

from .pipeline import ETLPipeline, PipelineConfig, PipelineStatus
from .processors import (
    CADProcessor,
    DataProcessor,
    LPRProcessor,
    RMSProcessor,
    ShotSpotterProcessor,
)
from .scheduler import ETLScheduler, ScheduledJob
from .transformers import (
    DataTransformer,
    GeoEnricher,
    IncidentNormalizer,
    TimeNormalizer,
)
from .validators import DataValidator, ValidationResult, ValidationRule

__all__ = [
    "CADProcessor",
    "DataProcessor",
    "DataTransformer",
    "DataValidator",
    "ETLPipeline",
    "ETLScheduler",
    "GeoEnricher",
    "IncidentNormalizer",
    "LPRProcessor",
    "PipelineConfig",
    "PipelineStatus",
    "RMSProcessor",
    "ScheduledJob",
    "ShotSpotterProcessor",
    "TimeNormalizer",
    "ValidationResult",
    "ValidationRule",
]
