"""
Crime Analysis Engine for G3TI RTCC-UIP.

This module provides comprehensive crime analysis capabilities including:
- Data ingestion from multiple sources (CSV, Excel, JSON, FBI NIBRS, etc.)
- Heatmap generation with kernel density estimation
- Time series analysis and trend prediction
- Crime forecasting with ARIMA/Prophet
- Sector risk analysis and scoring
- Repeat location detection
"""

from app.crime_analysis.api_router import router as crime_router
from app.crime_analysis.crime_ingest import CrimeDataIngestor
from app.crime_analysis.crime_heatmap_engine import CrimeHeatmapEngine
from app.crime_analysis.crime_timeseries import CrimeTimeseriesAnalyzer
from app.crime_analysis.crime_forecast import CrimeForecastEngine
from app.crime_analysis.sector_risk_analysis import SectorRiskAnalyzer
from app.crime_analysis.repeat_location_detector import RepeatLocationDetector

__all__ = [
    "crime_router",
    "CrimeDataIngestor",
    "CrimeHeatmapEngine",
    "CrimeTimeseriesAnalyzer",
    "CrimeForecastEngine",
    "SectorRiskAnalyzer",
    "RepeatLocationDetector",
]
