"""
Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine

This module provides the ethical reasoning layer for all AI systems in the
G3TI RTCC-UIP ecosystem, ensuring constitutional compliance, non-discrimination,
bias prevention, and community trust alignment.

Components:
- MoralEngine: Core ethical reasoning and decision-making
- EthicalGuardrails: Safeguards against harmful actions
- FairnessAnalyzer: Bias detection and fairness scoring
- CultureContextEngine: Community and cultural awareness
- MoralGraph: Reasoning chain visualization
"""

from backend.app.moral_compass.moral_engine import (
    MoralEngine,
    MoralDecision,
    MoralDecisionType,
    EthicalPrinciple,
    HarmLevel,
    RiskCategory,
    MoralAssessment,
    ReasoningChain,
)

from backend.app.moral_compass.ethical_guardrails import (
    EthicalGuardrails,
    GuardrailType,
    GuardrailViolation,
    GuardrailCheck,
    ProtectionCategory,
)

from backend.app.moral_compass.fairness_analyzer import (
    FairnessAnalyzer,
    FairnessMetric,
    BiasType,
    DisparityAlert,
    FairnessScore,
    FairnessAssessment,
)

from backend.app.moral_compass.culture_context_engine import (
    CultureContextEngine,
    CommunityContext,
    CulturalFactor,
    LocalEvent,
    TrustLevel,
    VulnerabilityFactor,
)

from backend.app.moral_compass.moral_graph import (
    MoralGraph,
    GraphNode,
    GraphEdge,
    NodeType,
    ReasoningPath,
    ExplainabilityCapsule,
)

__all__ = [
    "MoralEngine",
    "MoralDecision",
    "MoralDecisionType",
    "EthicalPrinciple",
    "HarmLevel",
    "RiskCategory",
    "MoralAssessment",
    "ReasoningChain",
    "EthicalGuardrails",
    "GuardrailType",
    "GuardrailViolation",
    "GuardrailCheck",
    "ProtectionCategory",
    "FairnessAnalyzer",
    "FairnessMetric",
    "BiasType",
    "DisparityAlert",
    "FairnessScore",
    "FairnessAssessment",
    "CultureContextEngine",
    "CommunityContext",
    "CulturalFactor",
    "LocalEvent",
    "TrustLevel",
    "VulnerabilityFactor",
    "MoralGraph",
    "GraphNode",
    "GraphEdge",
    "NodeType",
    "ReasoningPath",
    "ExplainabilityCapsule",
]
