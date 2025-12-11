"""
Phase 26: Ethics Guardian API Router

Endpoints:
- POST /api/ethics/check-bias
- POST /api/ethics/force-risk
- POST /api/ethics/civil-rights
- POST /api/ethics/ethics-score
- GET /api/ethics/explain/{action_id}
- GET /api/ethics/audit
- POST /api/ethics/protected-community
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/ethics", tags=["Ethics Guardian"])


class AnalysisTypeEnum(str, Enum):
    PREDICTIVE_AI = "PREDICTIVE_AI"
    RISK_SCORE = "RISK_SCORE"
    PATROL_ROUTING = "PATROL_ROUTING"
    ENTITY_CORRELATION = "ENTITY_CORRELATION"
    SURVEILLANCE_TRIGGER = "SURVEILLANCE_TRIGGER"
    ENFORCEMENT_RECOMMENDATION = "ENFORCEMENT_RECOMMENDATION"


class BiasCheckRequest(BaseModel):
    analysis_type: AnalysisTypeEnum
    demographic_outcomes: Dict[str, Dict[str, float]]
    reference_group: str = "White"
    model_version: str = "1.0"
    geographic_scope: str = "Riviera Beach"
    data_source: str = "RTCC-UIP"


class BiasMetricResponse(BaseModel):
    metric_id: str
    name: str
    value: float
    threshold: float
    is_passing: bool
    protected_group: str
    reference_group: str


class BiasCheckResponse(BaseModel):
    result_id: str
    status: str
    metrics: List[BiasMetricResponse]
    affected_groups: List[str]
    recommendations: List[str]
    confidence_score: float
    requires_human_review: bool
    blocked: bool
    explanation: str
    timestamp: str


class ForceRiskRequest(BaseModel):
    action_id: str
    subject_armed: bool = False
    weapon_type: Optional[str] = None
    subject_aggressive: bool = False
    subject_fleeing: bool = False
    mental_health_crisis: bool = False
    suicidal_ideation: bool = False
    subject_age: int = 30
    juveniles_present: bool = False
    location_type: Optional[str] = None
    disability_apparent: bool = False
    crowd_size: int = 0
    media_present: bool = False
    has_warrant: bool = False
    consent_given: bool = False
    involves_search: bool = False


class DeescalationResponse(BaseModel):
    recommendation_id: str
    technique: str
    description: str
    effectiveness_rating: float
    success_rate: float


class ForceRiskResponse(BaseModel):
    assessment_id: str
    action_id: str
    total_risk_score: float
    risk_level: str
    requires_human_review: bool
    mandatory_review_reasons: List[str]
    deescalation_recommendations: List[DeescalationResponse]
    civil_rights_concerns: List[str]
    mental_health_flags: List[str]
    juvenile_flags: List[str]
    recommended_force_level: str
    max_authorized_force: str
    explanation: str
    timestamp: str


class CivilRightsRequest(BaseModel):
    action_id: str
    action_type: str
    has_warrant: bool = False
    consent: bool = False
    exigent_circumstances: bool = False
    targeting_speech: bool = False
    interfering_assembly: bool = False
    discriminatory_intent: bool = False
    disparate_impact: bool = False
    compelling_interest: bool = False
    mass_surveillance: bool = False
    surveillance_duration_hours: int = 0
    data_type: str = "general_records"
    retention_days: int = 0


class ViolationResponse(BaseModel):
    violation_id: str
    violation_type: str
    description: str
    legal_basis: str
    citation: str
    severity: str
    remediation: str
    blocked: bool


class CivilRightsResponse(BaseModel):
    result_id: str
    action_id: str
    status: str
    violations: List[ViolationResponse]
    constitutional_concerns: List[str]
    legal_citations: List[str]
    blocked: bool
    block_reason: str
    conditions: List[str]
    recommendations: List[str]
    explanation: str
    timestamp: str


class EthicsScoreRequest(BaseModel):
    action_id: str
    action_type: str
    bias_detected: bool = False
    disparate_impact_ratio: float = 1.0
    demographic_parity_diff: float = 0.0
    constitutional_violation: bool = False
    fourth_amendment_concern: bool = False
    first_amendment_concern: bool = False
    equal_protection_concern: bool = False
    force_risk_score: float = 0.0
    excessive_force_risk: bool = False
    historical_disparity: bool = False
    policy_violations: List[str] = []
    sop_compliance: bool = True
    explainability_score: float = 1.0
    audit_trail_complete: bool = True
    body_camera_active: bool = True
    community_impact_score: float = 0.0
    protected_community_affected: bool = False
    supervisor_notified: bool = True
    documentation_complete: bool = True


class ComponentScoreResponse(BaseModel):
    component: str
    score: float
    max_score: float
    weight: float
    contributing_factors: List[str]
    improvement_suggestions: List[str]


class EthicsScoreResponse(BaseModel):
    assessment_id: str
    action_id: str
    action_type: str
    total_score: float
    ethics_level: str
    color_code: str
    component_scores: List[ComponentScoreResponse]
    required_action: str
    action_conditions: List[str]
    improvement_recommendations: List[str]
    explanation: str
    audit_required: bool
    human_review_required: bool
    timestamp: str


class ExplanationResponse(BaseModel):
    explanation_id: str
    action_id: str
    explanation_type: str
    human_readable: str
    reasoning_steps: int
    legal_basis: List[str]
    data_sources: int
    bias_metrics_count: int
    risk_impacts_count: int
    safeguard_triggers_count: int
    confidence_score: float
    alternative_actions: List[str]
    limitations: List[str]
    timestamp: str


class AuditEntryResponse(BaseModel):
    entry_id: str
    timestamp: str
    action_id: str
    action_type: str
    actor_id: str
    actor_role: str
    severity: str
    explanation_id: str
    summary: str
    hash_chain: str
    retention_days: int


class ProtectedCommunityRequest(BaseModel):
    action_id: str
    action_type: str
    neighborhood: str = ""
    majority_black: bool = False
    majority_hispanic: bool = False
    subject_age: int = 30
    lgbtq_identified: bool = False
    disability: bool = False
    veteran: bool = False
    place_of_worship: bool = False
    disparity_ratio: float = 1.0
    surveillance_rate: float = 0.0
    bias_score: float = 0.0


class SafeguardRuleResponse(BaseModel):
    rule_id: str
    community_type: str
    name: str
    description: str
    action_required: str
    auto_review: bool
    escalation_level: str


class ProtectedCommunityResponse(BaseModel):
    check_id: str
    action_id: str
    community_types_affected: List[str]
    triggered_rules: List[SafeguardRuleResponse]
    safeguard_level: str
    requires_review: bool
    requires_community_liaison: bool
    recommendations: List[str]
    engagement_actions: List[str]
    explanation: str
    timestamp: str


@router.post("/check-bias", response_model=BiasCheckResponse)
async def check_bias(request: BiasCheckRequest):
    """
    Check AI output for potential bias.
    
    Analyzes demographic outcomes using fairness metrics:
    - Disparate Impact Ratio (80% rule)
    - Demographic Parity
    - Equal Opportunity Difference
    - Predictive Equality
    - Calibration Fairness
    """
    from app.ethics_guardian import get_bias_detection_engine, AnalysisType
    
    engine = get_bias_detection_engine()
    
    data = {
        "demographic_outcomes": request.demographic_outcomes,
        "reference_group": request.reference_group,
        "data_source": request.data_source,
    }
    
    result = engine.analyze_for_bias(
        analysis_type=AnalysisType(request.analysis_type.value),
        data=data,
        model_version=request.model_version,
        geographic_scope=request.geographic_scope,
    )
    
    return BiasCheckResponse(
        result_id=result.result_id,
        status=result.status.value,
        metrics=[
            BiasMetricResponse(
                metric_id=m.metric_id,
                name=m.name,
                value=m.value,
                threshold=m.threshold,
                is_passing=m.is_passing,
                protected_group=m.protected_group,
                reference_group=m.reference_group,
            )
            for m in result.metrics
        ],
        affected_groups=result.affected_groups,
        recommendations=result.recommendations,
        confidence_score=result.confidence_score,
        requires_human_review=result.requires_human_review,
        blocked=result.blocked,
        explanation=result.explanation,
        timestamp=result.timestamp.isoformat(),
    )


@router.post("/force-risk", response_model=ForceRiskResponse)
async def assess_force_risk(request: ForceRiskRequest):
    """
    Assess use-of-force risk for an action.
    
    Evaluates:
    - Civil rights exposure
    - Force escalation probability
    - Mental health indicators
    - Juvenile involvement
    - Proximity to sensitive locations
    - Protected classes
    """
    from app.ethics_guardian import get_force_risk_engine
    
    engine = get_force_risk_engine()
    
    context = {
        "subject_armed": request.subject_armed,
        "weapon_type": request.weapon_type,
        "subject_aggressive": request.subject_aggressive,
        "subject_fleeing": request.subject_fleeing,
        "mental_health_crisis": request.mental_health_crisis,
        "suicidal_ideation": request.suicidal_ideation,
        "subject_age": request.subject_age,
        "juveniles_present": request.juveniles_present,
        "location_type": request.location_type,
        "disability_apparent": request.disability_apparent,
        "crowd_size": request.crowd_size,
        "media_present": request.media_present,
        "has_warrant": request.has_warrant,
        "consent_given": request.consent_given,
        "involves_search": request.involves_search,
    }
    
    result = engine.assess_force_risk(request.action_id, context)
    
    return ForceRiskResponse(
        assessment_id=result.assessment_id,
        action_id=result.action_id,
        total_risk_score=result.total_risk_score,
        risk_level=result.risk_level,
        requires_human_review=result.requires_human_review,
        mandatory_review_reasons=result.mandatory_review_reasons,
        deescalation_recommendations=[
            DeescalationResponse(
                recommendation_id=d.recommendation_id,
                technique=d.technique,
                description=d.description,
                effectiveness_rating=d.effectiveness_rating,
                success_rate=d.success_rate,
            )
            for d in result.deescalation_recommendations
        ],
        civil_rights_concerns=result.civil_rights_concerns,
        mental_health_flags=result.mental_health_flags,
        juvenile_flags=result.juvenile_flags,
        recommended_force_level=result.recommended_force_level.value,
        max_authorized_force=result.max_authorized_force.value,
        explanation=result.explanation,
        timestamp=result.timestamp.isoformat(),
    )


@router.post("/civil-rights", response_model=CivilRightsResponse)
async def check_civil_rights(request: CivilRightsRequest):
    """
    Validate action against civil rights requirements.
    
    Checks compliance with:
    - U.S. Constitution (1st, 4th, 14th Amendments)
    - Florida Constitution
    - Riviera Beach municipal code
    - DOJ Guidelines
    - CJIS Security Policy
    """
    from app.ethics_guardian import get_civil_liberties_engine
    
    engine = get_civil_liberties_engine()
    
    context = {
        "has_warrant": request.has_warrant,
        "consent": request.consent,
        "exigent_circumstances": request.exigent_circumstances,
        "targeting_speech": request.targeting_speech,
        "interfering_assembly": request.interfering_assembly,
        "discriminatory_intent": request.discriminatory_intent,
        "disparate_impact": request.disparate_impact,
        "compelling_interest": request.compelling_interest,
        "mass_surveillance": request.mass_surveillance,
        "surveillance_duration_hours": request.surveillance_duration_hours,
        "data_type": request.data_type,
        "retention_days": request.retention_days,
    }
    
    result = engine.check_compliance(
        request.action_id,
        request.action_type,
        context,
    )
    
    return CivilRightsResponse(
        result_id=result.result_id,
        action_id=result.action_id,
        status=result.status.value,
        violations=[
            ViolationResponse(
                violation_id=v.violation_id,
                violation_type=v.violation_type.value,
                description=v.description,
                legal_basis=v.legal_basis.value,
                citation=v.citation,
                severity=v.severity,
                remediation=v.remediation,
                blocked=v.blocked,
            )
            for v in result.violations
        ],
        constitutional_concerns=result.constitutional_concerns,
        legal_citations=result.legal_citations,
        blocked=result.blocked,
        block_reason=result.block_reason,
        conditions=result.conditions,
        recommendations=result.recommendations,
        explanation=result.explanation,
        timestamp=result.timestamp.isoformat(),
    )


@router.post("/ethics-score", response_model=EthicsScoreResponse)
async def compute_ethics_score(request: EthicsScoreRequest):
    """
    Compute comprehensive ethics score for an action.
    
    Evaluates:
    - Fairness metrics
    - Civil rights exposure
    - Use-of-force risk
    - Historical disparities
    - Policy compliance
    - Transparency requirements
    """
    from app.ethics_guardian import get_ethics_score_engine
    
    engine = get_ethics_score_engine()
    
    context = {
        "bias_detected": request.bias_detected,
        "disparate_impact_ratio": request.disparate_impact_ratio,
        "demographic_parity_diff": request.demographic_parity_diff,
        "constitutional_violation": request.constitutional_violation,
        "fourth_amendment_concern": request.fourth_amendment_concern,
        "first_amendment_concern": request.first_amendment_concern,
        "equal_protection_concern": request.equal_protection_concern,
        "force_risk_score": request.force_risk_score,
        "excessive_force_risk": request.excessive_force_risk,
        "historical_disparity": request.historical_disparity,
        "policy_violations": request.policy_violations,
        "sop_compliance": request.sop_compliance,
        "explainability_score": request.explainability_score,
        "audit_trail_complete": request.audit_trail_complete,
        "body_camera_active": request.body_camera_active,
        "community_impact_score": request.community_impact_score,
        "protected_community_affected": request.protected_community_affected,
        "supervisor_notified": request.supervisor_notified,
        "documentation_complete": request.documentation_complete,
    }
    
    result = engine.compute_ethics_score(
        request.action_id,
        request.action_type,
        context,
    )
    
    return EthicsScoreResponse(
        assessment_id=result.assessment_id,
        action_id=result.action_id,
        action_type=result.action_type,
        total_score=result.total_score,
        ethics_level=result.ethics_level.value,
        color_code=result.color_code,
        component_scores=[
            ComponentScoreResponse(
                component=c.component.value,
                score=c.score,
                max_score=c.max_score,
                weight=c.weight,
                contributing_factors=c.contributing_factors,
                improvement_suggestions=c.improvement_suggestions,
            )
            for c in result.component_scores
        ],
        required_action=result.required_action.value,
        action_conditions=result.action_conditions,
        improvement_recommendations=result.improvement_recommendations,
        explanation=result.explanation,
        audit_required=result.audit_required,
        human_review_required=result.human_review_required,
        timestamp=result.timestamp.isoformat(),
    )


@router.get("/explain/{action_id}", response_model=ExplanationResponse)
async def get_explanation(action_id: str):
    """
    Get human-readable explanation for an action.
    
    Returns:
    - Chain of reasoning
    - Legal basis
    - Data sources
    - Bias metrics
    - Risk impacts
    - Safeguard triggers
    """
    from app.ethics_guardian import get_transparency_engine
    
    engine = get_transparency_engine()
    
    explanation = engine.get_explanation_by_action(action_id)
    
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Explanation not found for action {action_id}")
    
    return ExplanationResponse(
        explanation_id=explanation.explanation_id,
        action_id=explanation.action_id,
        explanation_type=explanation.explanation_type.value,
        human_readable=explanation.human_readable,
        reasoning_steps=len(explanation.reasoning_chain),
        legal_basis=explanation.legal_basis,
        data_sources=len(explanation.data_sources),
        bias_metrics_count=len(explanation.bias_metrics),
        risk_impacts_count=len(explanation.risk_impacts),
        safeguard_triggers_count=len(explanation.safeguard_triggers),
        confidence_score=explanation.confidence_score,
        alternative_actions=explanation.alternative_actions,
        limitations=explanation.limitations,
        timestamp=explanation.timestamp.isoformat(),
    )


@router.get("/audit", response_model=List[AuditEntryResponse])
async def get_audit_log(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum entries to return"),
):
    """
    Get ethics audit log entries.
    
    Supports filtering by severity and action type.
    All entries are encrypted and include hash chain for integrity.
    """
    from app.ethics_guardian import get_transparency_engine, AuditSeverity
    
    engine = get_transparency_engine()
    
    sev = None
    if severity:
        try:
            sev = AuditSeverity(severity)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
    
    entries = engine.get_audit_log(severity=sev, action_type=action_type, limit=limit)
    
    return [
        AuditEntryResponse(
            entry_id=e.entry_id,
            timestamp=e.timestamp.isoformat(),
            action_id=e.action_id,
            action_type=e.action_type,
            actor_id=e.actor_id,
            actor_role=e.actor_role,
            severity=e.severity.value,
            explanation_id=e.explanation_id,
            summary=e.summary,
            hash_chain=e.hash_chain,
            retention_days=e.retention_days,
        )
        for e in entries
    ]


@router.post("/protected-community", response_model=ProtectedCommunityResponse)
async def check_protected_community(request: ProtectedCommunityRequest):
    """
    Check if action triggers protected community safeguards.
    
    Evaluates safeguards for:
    - Black community
    - Hispanic community
    - LGBTQ+ youth
    - People with disabilities
    - Veterans
    - Faith communities
    - Aging population
    """
    from app.ethics_guardian import get_protected_community_safeguards
    
    engine = get_protected_community_safeguards()
    
    context = {
        "location": {"neighborhood": request.neighborhood},
        "demographics": {
            "majority_black": request.majority_black,
            "majority_hispanic": request.majority_hispanic,
        },
        "subject_info": {
            "age": request.subject_age,
            "lgbtq_identified": request.lgbtq_identified,
            "disability": request.disability,
            "veteran": request.veteran,
        },
        "place_of_worship": request.place_of_worship,
        "disparity_ratio": request.disparity_ratio,
        "surveillance_rate": request.surveillance_rate,
        "bias_score": request.bias_score,
    }
    
    result = engine.check_safeguards(
        request.action_id,
        request.action_type,
        context,
    )
    
    return ProtectedCommunityResponse(
        check_id=result.check_id,
        action_id=result.action_id,
        community_types_affected=[c.value for c in result.community_types_affected],
        triggered_rules=[
            SafeguardRuleResponse(
                rule_id=r.rule_id,
                community_type=r.community_type.value,
                name=r.name,
                description=r.description,
                action_required=r.action_required,
                auto_review=r.auto_review,
                escalation_level=r.escalation_level,
            )
            for r in result.triggered_rules
        ],
        safeguard_level=result.safeguard_level.value,
        requires_review=result.requires_review,
        requires_community_liaison=result.requires_community_liaison,
        recommendations=result.recommendations,
        engagement_actions=result.engagement_actions,
        explanation=result.explanation,
        timestamp=result.timestamp.isoformat(),
    )


@router.get("/bias-history")
async def get_bias_history(
    analysis_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get bias analysis history."""
    from app.ethics_guardian import get_bias_detection_engine, AnalysisType, BiasStatus
    
    engine = get_bias_detection_engine()
    
    at = None
    if analysis_type:
        try:
            at = AnalysisType(analysis_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid analysis type: {analysis_type}")
    
    st = None
    if status:
        try:
            st = BiasStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    results = engine.get_analysis_history(analysis_type=at, status=st, limit=limit)
    
    return [
        {
            "result_id": r.result_id,
            "analysis_type": r.analysis_type.value,
            "status": r.status.value,
            "affected_groups": r.affected_groups,
            "confidence_score": r.confidence_score,
            "blocked": r.blocked,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in results
    ]


@router.get("/force-risk-history")
async def get_force_risk_history(
    risk_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get use-of-force risk assessment history."""
    from app.ethics_guardian import get_force_risk_engine
    
    engine = get_force_risk_engine()
    results = engine.get_assessment_history(risk_level=risk_level, limit=limit)
    
    return [
        {
            "assessment_id": r.assessment_id,
            "action_id": r.action_id,
            "total_risk_score": r.total_risk_score,
            "risk_level": r.risk_level,
            "requires_human_review": r.requires_human_review,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in results
    ]


@router.get("/ethics-history")
async def get_ethics_history(
    level: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get ethics score assessment history."""
    from app.ethics_guardian import get_ethics_score_engine, EthicsLevel, RequiredAction
    
    engine = get_ethics_score_engine()
    
    lv = None
    if level:
        try:
            lv = EthicsLevel(level)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid level: {level}")
    
    act = None
    if action:
        try:
            act = RequiredAction(action)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
    
    results = engine.get_assessment_history(level=lv, action=act, limit=limit)
    
    return [
        {
            "assessment_id": r.assessment_id,
            "action_id": r.action_id,
            "total_score": r.total_score,
            "ethics_level": r.ethics_level.value,
            "required_action": r.required_action.value,
            "human_review_required": r.human_review_required,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in results
    ]


@router.get("/community-profiles")
async def get_community_profiles():
    """Get all protected community profiles for Riviera Beach."""
    from app.ethics_guardian import get_protected_community_safeguards
    
    engine = get_protected_community_safeguards()
    profiles = engine.get_all_community_profiles()
    
    return [
        {
            "community_type": p.community_type.value,
            "population_estimate": p.population_estimate,
            "population_percentage": p.population_percentage,
            "geographic_concentration": p.geographic_concentration,
            "safeguard_level": p.safeguard_level.value,
            "bias_sensitivity_multiplier": p.bias_sensitivity_multiplier,
            "engagement_requirements": p.engagement_requirements,
            "liaison_contacts": p.liaison_contacts,
        }
        for p in profiles.values()
    ]


@router.get("/retention-limits")
async def get_retention_limits():
    """Get data retention limits."""
    from app.ethics_guardian import get_civil_liberties_engine
    
    engine = get_civil_liberties_engine()
    return engine.get_retention_limits()


@router.get("/ethics-thresholds")
async def get_ethics_thresholds():
    """Get ethics level thresholds and component weights."""
    from app.ethics_guardian import get_ethics_score_engine
    
    engine = get_ethics_score_engine()
    
    thresholds = engine.get_level_thresholds()
    weights = engine.get_component_weights()
    
    return {
        "level_thresholds": {k.value: v for k, v in thresholds.items()},
        "component_weights": {k.value: v for k, v in weights.items()},
    }


@router.post("/generate-explanation")
async def generate_explanation(
    action_id: str,
    action_type: str,
    decision_data: Dict[str, Any],
):
    """Generate comprehensive explanation for a decision."""
    from app.ethics_guardian import get_transparency_engine
    
    engine = get_transparency_engine()
    
    explanation = engine.generate_explanation(action_id, action_type, decision_data)
    
    return {
        "explanation_id": explanation.explanation_id,
        "action_id": explanation.action_id,
        "human_readable": explanation.human_readable,
        "reasoning_steps": len(explanation.reasoning_chain),
        "legal_basis": explanation.legal_basis,
        "confidence_score": explanation.confidence_score,
        "timestamp": explanation.timestamp.isoformat(),
    }


@router.get("/verify-audit-chain")
async def verify_audit_chain():
    """Verify integrity of the audit chain."""
    from app.ethics_guardian import get_transparency_engine
    
    engine = get_transparency_engine()
    is_valid = engine.verify_audit_chain()
    
    return {
        "chain_valid": is_valid,
        "verified_at": datetime.now().isoformat(),
    }
