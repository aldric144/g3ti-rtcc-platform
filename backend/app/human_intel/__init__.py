"""
Phase 30: Human Stability Intelligence Engine (HSI-E)

Community Mental Health + Suicide Prevention + Domestic Violence Risk + Behavioral Crisis Prediction

This engine uses AI to detect early human instability signals across the city — ethically, legally,
and with strict anonymization — to protect lives while respecting privacy.

Agency: Riviera Beach Police Department (ORI: FL0500400)
Location: Riviera Beach, Florida 33404
County: Palm Beach County
"""

from .behavioral_crisis_engine import (
    BehavioralCrisisEngine,
    SuicideRiskLevel,
    DVEscalationLevel,
    CrisisType,
    SuicideRiskAssessment,
    DVEscalationAssessment,
    CommunityTraumaPulse,
    StabilityIndex,
)

from .crisis_intervention_engine import (
    CrisisInterventionEngine,
    ResponderType,
    InterventionPriority,
    CoResponderRecommendation,
    TraumaInformedGuidance,
    RepeatCrisisFlag,
    CrisisRoutingDecision,
)

from .youth_crisis_engine import (
    YouthCrisisEngine,
    YouthRiskLevel,
    YouthRiskType,
    YouthRiskAssessment,
    SchoolIncidentCluster,
    GangExposureRisk,
    YouthInterventionPlan,
)

from .privacy_guard import (
    PrivacyGuard,
    PrivacyViolationType,
    AnonymizationLevel,
    PrivacyCheckResult,
    EthicsAuditResult,
)

__all__ = [
    "BehavioralCrisisEngine",
    "SuicideRiskLevel",
    "DVEscalationLevel",
    "CrisisType",
    "SuicideRiskAssessment",
    "DVEscalationAssessment",
    "CommunityTraumaPulse",
    "StabilityIndex",
    "CrisisInterventionEngine",
    "ResponderType",
    "InterventionPriority",
    "CoResponderRecommendation",
    "TraumaInformedGuidance",
    "RepeatCrisisFlag",
    "CrisisRoutingDecision",
    "YouthCrisisEngine",
    "YouthRiskLevel",
    "YouthRiskType",
    "YouthRiskAssessment",
    "SchoolIncidentCluster",
    "GangExposureRisk",
    "YouthInterventionPlan",
    "PrivacyGuard",
    "PrivacyViolationType",
    "AnonymizationLevel",
    "PrivacyCheckResult",
    "EthicsAuditResult",
]
