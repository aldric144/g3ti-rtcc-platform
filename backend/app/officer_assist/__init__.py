"""
Phase 28: AI Officer Assist Suite & Real-Time Constitutional Guardrails

This module provides real-time protection for officers, the city, and the RTCC
from policy violations, unlawful actions, and use-of-force escalation mistakes.

Components:
- ConstitutionalGuardrailEngine: Real-time constitutional and policy compliance
- UseOfForceRiskMonitor: Risk level classification and supervisor alerts
- OfficerBehavioralSafetyEngine: Fatigue, stress, and safety monitoring
- TacticalAdvisorEngine: Live tactical guidance and recommendations
- OfficerIntentInterpreter: Intent detection from radio/MDT/voice inputs

Riviera Beach Police Department Configuration:
- Agency ORI: FL0500400
- State: Florida
- City: Riviera Beach, FL 33404
"""

from .constitutional_guardrails import (
    ConstitutionalGuardrailEngine,
    GuardrailResult,
    GuardrailStatus,
    ConstitutionalViolationType,
    PolicyViolationType,
    GuardrailCheck,
)

from .use_of_force_monitor import (
    UseOfForceRiskMonitor,
    RiskLevel,
    ForceRiskAssessment,
    SceneEscalationPattern,
    SuspectBehaviorClass,
)

from .officer_behavioral_safety import (
    OfficerBehavioralSafetyEngine,
    OfficerSafetyStatus,
    FatigueLevel,
    StressIndicator,
    SafetyAlert,
)

from .tactical_advisor import (
    TacticalAdvisorEngine,
    TacticalAdvice,
    TacticalScenario,
    CoverPosition,
    EscapeRoute,
)

from .intent_interpreter import (
    OfficerIntentInterpreter,
    OfficerIntent,
    IntentType,
    IntentConfidence,
)

__all__ = [
    "ConstitutionalGuardrailEngine",
    "GuardrailResult",
    "GuardrailStatus",
    "ConstitutionalViolationType",
    "PolicyViolationType",
    "GuardrailCheck",
    "UseOfForceRiskMonitor",
    "RiskLevel",
    "ForceRiskAssessment",
    "SceneEscalationPattern",
    "SuspectBehaviorClass",
    "OfficerBehavioralSafetyEngine",
    "OfficerSafetyStatus",
    "FatigueLevel",
    "StressIndicator",
    "SafetyAlert",
    "TacticalAdvisorEngine",
    "TacticalAdvice",
    "TacticalScenario",
    "CoverPosition",
    "EscapeRoute",
    "OfficerIntentInterpreter",
    "OfficerIntent",
    "IntentType",
    "IntentConfidence",
]
