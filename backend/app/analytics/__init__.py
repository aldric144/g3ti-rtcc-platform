"""
Analytics Module for G3TI RTCC-UIP Data Lake.

This module provides comprehensive analytics capabilities including:
- Historical trend analysis
- Multi-year heatmap generation
- Repeat offender analytics
- Predictive modeling
- Statistical analysis

The analytics module integrates with:
- Data Lake for historical data access
- Tactical Engine for real-time analytics
- AI Engine for predictive capabilities
"""

from .historical import HistoricalAnalyticsEngine, TrendAnalysis
from .heatmaps import MultiYearHeatmapEngine, HeatmapComparison
from .offender_analytics import RepeatOffenderAnalytics, RecidivismAnalysis

__all__ = [
    "HeatmapComparison",
    "HistoricalAnalyticsEngine",
    "MultiYearHeatmapEngine",
    "RecidivismAnalysis",
    "RepeatOffenderAnalytics",
    "TrendAnalysis",
]
