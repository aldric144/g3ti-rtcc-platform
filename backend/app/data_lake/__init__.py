"""
Data Lake Module for G3TI RTCC-UIP.

This module provides comprehensive data lake capabilities including:
- Partitioned storage for crime/incident data
- Data retention and lifecycle management
- Historical data aggregation
- Multi-year analytics support
- CJIS-compliant data governance

The data lake integrates with:
- PostgreSQL/TimescaleDB for time-series data
- Elasticsearch for full-text search
- Neo4j for relationship graphs
- Redis for caching aggregations
"""

from .models import (
    CrimeDataPartition,
    DataLakeConfig,
    DataRetentionPolicy,
    HistoricalAggregate,
    IncidentRecord,
    OffenderProfile,
    PartitionMetadata,
)
from .repository import DataLakeRepository
from .service import DataLakeService

__all__ = [
    "CrimeDataPartition",
    "DataLakeConfig",
    "DataLakeRepository",
    "DataLakeService",
    "DataRetentionPolicy",
    "HistoricalAggregate",
    "IncidentRecord",
    "OffenderProfile",
    "PartitionMetadata",
]
