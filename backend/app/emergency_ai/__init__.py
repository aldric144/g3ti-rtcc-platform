"""
Phase 31: AI Emergency Management Command (AI-EMC)

Autonomous Disaster Prediction, Multi-Agency Response, Recovery Analytics,
and Humanitarian AI Logistics for Riviera Beach, Florida.

Modules:
- disaster_prediction_engine: Multi-hazard disaster prediction
- response_coordination_engine: Autonomous disaster response coordination
- recovery_planner: Recovery and logistics planning
- communication_intel_engine: Emergency communication intelligence
"""

from backend.app.emergency_ai.disaster_prediction_engine import (
    DisasterPredictionEngine,
    HazardType,
    ThreatLevel,
    WeatherHazard,
    FireHazard,
    HazmatHazard,
    InfrastructureHazard,
    HazardPrediction,
)

from backend.app.emergency_ai.response_coordination_engine import (
    ResponseCoordinationEngine,
    AgencyType,
    ResourceType,
    TaskPriority,
    AgencyTask,
    ResourceAllocation,
    EvacuationRoute,
    ResponsePlan,
)

from backend.app.emergency_ai.recovery_planner import (
    RecoveryPlanner,
    DamageTier,
    RecoveryPhase,
    FEMACategory,
    DamageAssessment,
    SupplyAllocation,
    RecoveryTimeline,
    RecoveryPlan,
)

from backend.app.emergency_ai.communication_intel_engine import (
    CommunicationIntelEngine,
    AlertType,
    AlertPriority,
    Language,
    EmergencyAlert,
    SocialSignal,
    MultilingualMessage,
)

__all__ = [
    "DisasterPredictionEngine",
    "HazardType",
    "ThreatLevel",
    "WeatherHazard",
    "FireHazard",
    "HazmatHazard",
    "InfrastructureHazard",
    "HazardPrediction",
    "ResponseCoordinationEngine",
    "AgencyType",
    "ResourceType",
    "TaskPriority",
    "AgencyTask",
    "ResourceAllocation",
    "EvacuationRoute",
    "ResponsePlan",
    "RecoveryPlanner",
    "DamageTier",
    "RecoveryPhase",
    "FEMACategory",
    "DamageAssessment",
    "SupplyAllocation",
    "RecoveryTimeline",
    "RecoveryPlan",
    "CommunicationIntelEngine",
    "AlertType",
    "AlertPriority",
    "Language",
    "EmergencyAlert",
    "SocialSignal",
    "MultilingualMessage",
]
