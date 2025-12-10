"""
Phase 18: Autonomous National Security Engine (AI-NSE)

This module provides national-level autonomous security capabilities including:
- Cyber threat intelligence and malware detection
- Insider threat profiling and behavior analysis
- Geopolitical risk assessment and conflict monitoring
- Financial crime intelligence and fraud detection
- National risk fusion and stability scoring
- Real-time security alerts and routing

All modules are designed to integrate with the G3TI RTCC-UIP platform
and provide actionable intelligence for national security operations.
"""

from app.national_security.cyber_intel import (
    CyberIntelEngine,
    MalwareType,
    ThreatSeverity,
    AttackVector,
    MalwareSignal,
    BotnetActivity,
    RansomwareAlert,
    VulnerabilityReport,
)

from app.national_security.insider_threat import (
    InsiderThreatEngine,
    RiskLevel,
    BehaviorType,
    AnomalyType,
    EmployeeRiskProfile,
    BehaviorDeviation,
    AccessAnomaly,
    ThreatAssessment,
)

from app.national_security.geopolitical_risk import (
    GeopoliticalRiskEngine,
    ConflictIntensity,
    ThreatActorType,
    RegionStability,
    ConflictEvent,
    NationStateThreat,
    SanctionsEvent,
    GeoEconomicRisk,
)

from app.national_security.financial_crime_intel import (
    FinancialCrimeEngine,
    FraudType,
    RiskCategory,
    TransactionFlag,
    FraudPattern,
    CryptoWalletRisk,
    TransactionAnomaly,
    MoneyFlowNetwork,
)

from app.national_security.national_risk_fusion import (
    NationalRiskFusionEngine,
    StabilityLevel,
    RiskDomain,
    FusionMethod,
    NationalStabilityScore,
    RiskFusionResult,
    EarlyWarningSignal,
    TrendPrediction,
)

from app.national_security.national_security_alerts import (
    NationalSecurityAlertManager,
    AlertPriority,
    AlertCategory,
    AlertDestination,
    SecurityAlert,
    AlertSubscription,
    RoutingRule,
)

__all__ = [
    "CyberIntelEngine",
    "MalwareType",
    "ThreatSeverity",
    "AttackVector",
    "MalwareSignal",
    "BotnetActivity",
    "RansomwareAlert",
    "VulnerabilityReport",
    "InsiderThreatEngine",
    "RiskLevel",
    "BehaviorType",
    "AnomalyType",
    "EmployeeRiskProfile",
    "BehaviorDeviation",
    "AccessAnomaly",
    "ThreatAssessment",
    "GeopoliticalRiskEngine",
    "ConflictIntensity",
    "ThreatActorType",
    "RegionStability",
    "ConflictEvent",
    "NationStateThreat",
    "SanctionsEvent",
    "GeoEconomicRisk",
    "FinancialCrimeEngine",
    "FraudType",
    "RiskCategory",
    "TransactionFlag",
    "FraudPattern",
    "CryptoWalletRisk",
    "TransactionAnomaly",
    "MoneyFlowNetwork",
    "NationalRiskFusionEngine",
    "StabilityLevel",
    "RiskDomain",
    "FusionMethod",
    "NationalStabilityScore",
    "RiskFusionResult",
    "EarlyWarningSignal",
    "TrendPrediction",
    "NationalSecurityAlertManager",
    "AlertPriority",
    "AlertCategory",
    "AlertDestination",
    "SecurityAlert",
    "AlertSubscription",
    "RoutingRule",
]
