"""
Data Lake API Module for G3TI RTCC-UIP.

This module provides REST API endpoints for:
- Data Lake operations (incidents, aggregates, partitions)
- Historical analytics (trends, comparisons, seasonal patterns)
- Multi-year heatmaps (generation, comparison, evolution)
- Repeat offender analytics (profiles, recidivism, networks)
- ETL pipeline management (jobs, executions, monitoring)
- Data governance (quality metrics, lineage, retention)
"""

from .router import router

__all__ = ["router"]
