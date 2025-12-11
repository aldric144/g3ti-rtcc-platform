"""
Phase 26: AI Ethics, Bias Safeguards & Civil Rights Protection Layer

This module implements the full civil rights protection stack for:
- Riviera Beach, Florida 33404
- Florida state law compliance
- Federal constitutional compliance

Components:
- BiasDetectionEngine: Detect bias in AI outputs
- UseOfForceRiskEngine: Evaluate force escalation risks
- CivilLibertiesEngine: Validate constitutional compliance
- ProtectedCommunitySafeguards: Safeguards for protected communities
- EthicsScoreEngine: Compute combined ethics scores
- TransparencyEngine: Explainability and audit logging
"""

from app.ethics_guardian.bias_detection import (
    get_bias_detection_engine,
    BiasDetectionEngine,
    BiasResult,
    BiasMetric,
    BiasStatus,
    AnalysisType,
)
from app.ethics_guardian.force_risk import (
    get_force_risk_engine,
    UseOfForceRiskEngine,
    ForceRiskAssessment,
    DeescalationRecommendation,
)
from app.ethics_guardian.civil_liberties import (
    get_civil_liberties_engine,
    CivilLibertiesEngine,
    ComplianceResult,
    ConstitutionalBasis,
)
from app.ethics_guardian.protected_communities import (
    get_protected_community_safeguards,
    ProtectedCommunitySafeguards,
    CommunityType,
    SafeguardRule,
)
from app.ethics_guardian.ethics_score import (
    get_ethics_score_engine,
    EthicsScoreEngine,
    EthicsAssessment,
    EthicsLevel,
    RequiredAction,
)
from app.ethics_guardian.transparency import (
    get_transparency_engine,
    TransparencyEngine,
    Explanation,
    AuditEntry,
    AuditSeverity,
)

__all__ = [
    "get_bias_detection_engine",
    "BiasDetectionEngine",
    "BiasResult",
    "BiasMetric",
    "BiasStatus",
    "AnalysisType",
    "get_force_risk_engine",
    "UseOfForceRiskEngine",
    "ForceRiskAssessment",
    "DeescalationRecommendation",
    "get_civil_liberties_engine",
    "CivilLibertiesEngine",
    "ComplianceResult",
    "ConstitutionalBasis",
    "get_protected_community_safeguards",
    "ProtectedCommunitySafeguards",
    "CommunityType",
    "SafeguardRule",
    "get_ethics_score_engine",
    "EthicsScoreEngine",
    "EthicsAssessment",
    "EthicsLevel",
    "RequiredAction",
    "get_transparency_engine",
    "TransparencyEngine",
    "Explanation",
    "AuditEntry",
    "AuditSeverity",
]
