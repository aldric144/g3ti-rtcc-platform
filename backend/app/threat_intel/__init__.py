"""
Phase 17: Global Threat Intelligence Engine (GTIE)

This module provides national-level intelligence capabilities including:
- Dark Web monitoring and analysis
- OSINT harvesting (news, social, forums)
- Extremist network mapping and analysis
- Global incident monitoring
- ML-based threat scoring
- Real-time threat alerting
"""

from app.threat_intel.dark_web_monitor import (
    DarkWebMonitor,
    DarkWebSignal,
    MarketListing,
    ThreatSentiment,
)
from app.threat_intel.osint_harvester import (
    OSINTHarvester,
    NewsArticle,
    SocialSignal,
    KeywordSpike,
    EventPrediction,
)
from app.threat_intel.extremist_networks import (
    ExtremistNetworkAnalyzer,
    NetworkNode,
    NetworkEdge,
    InfluenceScore,
    RadicalizationTrajectory,
)
from app.threat_intel.global_incidents import (
    GlobalIncidentMonitor,
    GlobalIncident,
    CrisisAlert,
    GeoThreatCorrelation,
)
from app.threat_intel.threat_scoring_engine import (
    ThreatScoringEngine,
    ThreatScore,
    ThreatLevel,
    ScoringRule,
    FusionResult,
)
from app.threat_intel.threat_alerts import (
    ThreatAlertManager,
    ThreatAlert,
    AlertPriority,
    AlertStatus,
)

__all__ = [
    "DarkWebMonitor",
    "DarkWebSignal",
    "MarketListing",
    "ThreatSentiment",
    "OSINTHarvester",
    "NewsArticle",
    "SocialSignal",
    "KeywordSpike",
    "EventPrediction",
    "ExtremistNetworkAnalyzer",
    "NetworkNode",
    "NetworkEdge",
    "InfluenceScore",
    "RadicalizationTrajectory",
    "GlobalIncidentMonitor",
    "GlobalIncident",
    "CrisisAlert",
    "GeoThreatCorrelation",
    "ThreatScoringEngine",
    "ThreatScore",
    "ThreatLevel",
    "ScoringRule",
    "FusionResult",
    "ThreatAlertManager",
    "ThreatAlert",
    "AlertPriority",
    "AlertStatus",
]
