"""
Tactical Analytics Engine for G3TI RTCC-UIP.

This module provides tactical intelligence capabilities including:
- Predictive heatmaps (KDE, DBSCAN, Bayesian spatial grids)
- Tactical risk scoring for addresses, zones, and districts
- Patrol route optimization
- Zone analysis and operational grids
- Shift briefing intelligence packs
- 24-hour and 7-day forecasting

The tactical engine integrates with:
- Neo4j for entity and relationship data
- Elasticsearch for narrative and temporal patterns
- Vendor data (LPR, ShotSpotter, RMS, CAD, BWC)
- AI Engine outputs (patterns, anomalies, risk scores)
"""

from .tactical_manager import TacticalManager

__all__ = ["TacticalManager"]
