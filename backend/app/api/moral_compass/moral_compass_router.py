"""
Moral Compass API Router

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
REST API endpoints for moral assessment, fairness analysis, and ethical reasoning.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.moral_compass.moral_engine import (
    MoralEngine,
    MoralDecisionType,
)
from backend.app.moral_compass.ethical_guardrails import (
    EthicalGuardrails,
    GuardrailType,
)
from backend.app.moral_compass.fairness_analyzer import (
    FairnessAnalyzer,
    FairnessMetric,
)
from backend.app.moral_compass.culture_context_engine import (
    CultureContextEngine,
    EventType,
    TrustLevel,
)
from backend.app.moral_compass.moral_graph import (
    MoralGraph,
)

router = APIRouter(prefix="/api/moral", tags=["moral_compass"])


class MoralAssessRequest(BaseModel):
    """Request for moral assessment."""
    action_type: str = Field(..., description="Type of action to assess")
    action_description: str = Field(..., description="Description of the action")
    requester_id: str = Field(..., description="ID of the requester")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    cultural_context: Optional[Dict[str, Any]] = Field(default=None, description="Cultural context")


class MoralAssessResponse(BaseModel):
    """Response for moral assessment."""
    assessment_id: str
    action_type: str
    decision: str
    reasoning_summary: str
    community_impact_score: float
    risk_to_community: float
    required_approvals: List[str]
    conditions: List[str]
    confidence: float
    assessment_hash: str


class FairnessRequest(BaseModel):
    """Request for fairness assessment."""
    action_type: str = Field(..., description="Type of action")
    requester_id: str = Field(..., description="ID of requester")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context")
    historical_data: Optional[Dict[str, Any]] = Field(default=None, description="Historical data")


class FairnessResponse(BaseModel):
    """Response for fairness assessment."""
    assessment_id: str
    overall_fairness_score: float
    passed: bool
    requires_review: bool
    bias_detected: bool
    disparity_count: int
    recommendations: List[str]


class ReasoningRequest(BaseModel):
    """Request for moral reasoning."""
    action_type: str = Field(..., description="Type of action")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context")


class ReasoningResponse(BaseModel):
    """Response for moral reasoning."""
    capsule_id: str
    action_type: str
    decision: str
    key_factors: List[str]
    constraints_applied: List[str]
    ethical_principles: List[str]
    human_readable_explanation: str
    confidence: float


class ContextRequest(BaseModel):
    """Request for cultural context."""
    location: str = Field(..., description="Location identifier")
    action_type: Optional[str] = Field(default=None, description="Type of action")
    additional_factors: Optional[Dict[str, Any]] = Field(default=None, description="Additional factors")


class ContextResponse(BaseModel):
    """Response for cultural context."""
    context_id: str
    location: str
    trust_level: str
    sentiment: str
    historical_trauma_present: bool
    special_considerations: List[str]
    recommended_approach: str


class GuardrailCheckRequest(BaseModel):
    """Request for guardrail check."""
    action_type: str = Field(..., description="Type of action")
    action_description: str = Field(..., description="Description")
    requester_id: str = Field(..., description="Requester ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context")


class GuardrailCheckResponse(BaseModel):
    """Response for guardrail check."""
    assessment_id: str
    passed: bool
    blocked: bool
    requires_review: bool
    violation_count: int
    recommendations: List[str]


class EventCreateRequest(BaseModel):
    """Request to create a local event."""
    name: str = Field(..., description="Event name")
    event_type: str = Field(..., description="Type of event")
    location: str = Field(..., description="Event location")
    start_time: datetime = Field(..., description="Start time")
    end_time: Optional[datetime] = Field(default=None, description="End time")
    expected_attendance: int = Field(default=0, description="Expected attendance")
    community_significance: str = Field(default="normal", description="Significance level")
    special_considerations: Optional[List[str]] = Field(default=None, description="Special considerations")


class ViolationResolveRequest(BaseModel):
    """Request to resolve a violation."""
    resolved_by: str = Field(..., description="ID of resolver")
    notes: Optional[str] = Field(default=None, description="Resolution notes")


@router.post("/assess", response_model=MoralAssessResponse)
async def assess_action(request: MoralAssessRequest):
    """
    Perform moral assessment of an action.
    
    Evaluates the action against ethical principles, legal constraints,
    and community impact considerations.
    """
    engine = MoralEngine()
    
    assessment = engine.assess(
        action_type=request.action_type,
        action_description=request.action_description,
        requester_id=request.requester_id,
        context=request.context,
        cultural_context=request.cultural_context,
    )
    
    return MoralAssessResponse(
        assessment_id=assessment.assessment_id,
        action_type=assessment.action_type,
        decision=assessment.decision.value,
        reasoning_summary=assessment.reasoning_chain.final_conclusion,
        community_impact_score=assessment.community_impact_score,
        risk_to_community=assessment.risk_to_community,
        required_approvals=assessment.required_approvals,
        conditions=assessment.conditions,
        confidence=assessment.reasoning_chain.confidence,
        assessment_hash=assessment.assessment_hash,
    )


@router.post("/fairness", response_model=FairnessResponse)
async def assess_fairness(request: FairnessRequest):
    """
    Perform fairness assessment.
    
    Evaluates the action for bias, disparity, and fairness metrics.
    """
    analyzer = FairnessAnalyzer()
    
    assessment = analyzer.assess_fairness(
        action_type=request.action_type,
        requester_id=request.requester_id,
        context=request.context,
        historical_data=request.historical_data,
    )
    
    return FairnessResponse(
        assessment_id=assessment.assessment_id,
        overall_fairness_score=assessment.overall_fairness_score,
        passed=assessment.passed,
        requires_review=assessment.requires_review,
        bias_detected=any(b.detected for b in assessment.bias_detections),
        disparity_count=len(assessment.disparity_alerts),
        recommendations=assessment.recommendations,
    )


@router.post("/reason", response_model=ReasoningResponse)
async def generate_reasoning(request: ReasoningRequest):
    """
    Generate moral reasoning explanation.
    
    Creates an explainability capsule with full reasoning chain.
    """
    engine = MoralEngine()
    graph = MoralGraph()
    
    decision = engine.make_decision(
        action_type=request.action_type,
        action_description=f"Reasoning request for {request.action_type}",
        requester_id="reasoning_api",
        context=request.context,
    )
    
    capsule = graph.generate_explainability_capsule(
        action_type=request.action_type,
        decision=decision.decision_type.value,
        context={
            "key_factors": decision.assessment.conditions,
            "risk_factors": [r.value for r in decision.assessment.harm_assessment.risk_categories],
            "community_considerations": decision.assessment.required_approvals,
            "confidence": decision.confidence,
        },
    )
    
    return ReasoningResponse(
        capsule_id=capsule.capsule_id,
        action_type=capsule.action_type,
        decision=capsule.decision,
        key_factors=capsule.key_factors,
        constraints_applied=capsule.constraints_applied,
        ethical_principles=capsule.ethical_principles,
        human_readable_explanation=capsule.human_readable_explanation,
        confidence=capsule.confidence,
    )


@router.get("/context")
async def get_cultural_context(
    location: str = Query(..., description="Location identifier"),
    action_type: Optional[str] = Query(default=None, description="Action type"),
):
    """
    Get cultural context for a location.
    
    Returns community sentiment, trust level, and cultural considerations.
    """
    engine = CultureContextEngine()
    
    context = engine.get_context(
        location=location,
        action_type=action_type,
    )
    
    return {
        "context_id": context.context_id,
        "location": context.location,
        "neighborhood": context.neighborhood.to_dict() if context.neighborhood else None,
        "trust_level": context.trust_level.value,
        "sentiment": context.sentiment.value,
        "active_events": [e.to_dict() for e in context.active_events],
        "vulnerability_factors": [v.value for v in context.vulnerability_factors],
        "cultural_factors": [f.to_dict() for f in context.cultural_factors],
        "historical_trauma_present": context.historical_trauma_present,
        "special_considerations": context.special_considerations,
        "recommended_approach": context.recommended_approach,
        "context_hash": context.context_hash,
    }


@router.get("/audit")
async def get_audit_trail(
    requester_id: Optional[str] = Query(default=None, description="Filter by requester"),
    limit: int = Query(default=50, description="Maximum results"),
):
    """
    Get audit trail of moral assessments.
    
    Returns chronological list of assessments for transparency.
    """
    engine = MoralEngine()
    
    trail = engine.get_audit_trail(requester_id=requester_id)
    
    return {
        "audit_trail": trail[:limit],
        "total_count": len(trail),
    }


@router.post("/guardrails/check", response_model=GuardrailCheckResponse)
async def check_guardrails(request: GuardrailCheckRequest):
    """
    Check action against ethical guardrails.
    
    Validates action against constitutional, policy, and ethical constraints.
    """
    guardrails = EthicalGuardrails()
    
    assessment = guardrails.check_action(
        action_type=request.action_type,
        action_description=request.action_description,
        requester_id=request.requester_id,
        context=request.context,
    )
    
    return GuardrailCheckResponse(
        assessment_id=assessment.assessment_id,
        passed=assessment.passed,
        blocked=assessment.blocked,
        requires_review=assessment.requires_review,
        violation_count=len(assessment.violations),
        recommendations=assessment.recommendations,
    )


@router.get("/guardrails/violations")
async def get_active_violations():
    """
    Get active guardrail violations.
    
    Returns unresolved violations requiring attention.
    """
    guardrails = EthicalGuardrails()
    
    violations = guardrails.get_active_violations()
    
    return {
        "violations": [v.to_dict() for v in violations],
        "count": len(violations),
    }


@router.post("/guardrails/violations/{violation_id}/resolve")
async def resolve_violation(
    violation_id: str,
    request: ViolationResolveRequest,
):
    """
    Resolve a guardrail violation.
    """
    guardrails = EthicalGuardrails()
    
    success = guardrails.resolve_violation(
        violation_id=violation_id,
        resolved_by=request.resolved_by,
        notes=request.notes,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    return {"status": "resolved", "violation_id": violation_id}


@router.get("/fairness/alerts")
async def get_fairness_alerts():
    """
    Get active fairness/disparity alerts.
    """
    analyzer = FairnessAnalyzer()
    
    alerts = analyzer.get_active_alerts()
    
    return {
        "alerts": [a.to_dict() for a in alerts],
        "count": len(alerts),
    }


@router.post("/fairness/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """
    Acknowledge a fairness alert.
    """
    analyzer = FairnessAnalyzer()
    
    success = analyzer.acknowledge_alert(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"status": "acknowledged", "alert_id": alert_id}


@router.post("/context/events")
async def create_event(request: EventCreateRequest):
    """
    Create a local event for cultural context.
    """
    engine = CultureContextEngine()
    
    try:
        event_type = EventType(request.event_type)
    except ValueError:
        event_type = EventType.COMMUNITY_MEETING
    
    event = engine.add_event(
        name=request.name,
        event_type=event_type,
        location=request.location,
        start_time=request.start_time,
        end_time=request.end_time,
        expected_attendance=request.expected_attendance,
        community_significance=request.community_significance,
        special_considerations=request.special_considerations,
    )
    
    return event.to_dict()


@router.get("/context/events")
async def get_active_events():
    """
    Get all active local events.
    """
    engine = CultureContextEngine()
    
    events = engine.get_active_events_all()
    
    return {
        "events": [e.to_dict() for e in events],
        "count": len(events),
    }


@router.delete("/context/events/{event_id}")
async def deactivate_event(event_id: str):
    """
    Deactivate a local event.
    """
    engine = CultureContextEngine()
    
    success = engine.deactivate_event(event_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"status": "deactivated", "event_id": event_id}


@router.get("/context/neighborhoods")
async def get_neighborhoods():
    """
    Get all neighborhood profiles.
    """
    engine = CultureContextEngine()
    
    neighborhoods = engine.get_all_neighborhoods()
    
    return {
        "neighborhoods": [n.to_dict() for n in neighborhoods],
        "count": len(neighborhoods),
    }


@router.get("/context/neighborhoods/{neighborhood_id}")
async def get_neighborhood(neighborhood_id: str):
    """
    Get a specific neighborhood profile.
    """
    engine = CultureContextEngine()
    
    neighborhood = engine.get_neighborhood(neighborhood_id)
    
    if not neighborhood:
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    
    return neighborhood.to_dict()


@router.put("/context/neighborhoods/{neighborhood_id}/trust")
async def update_neighborhood_trust(
    neighborhood_id: str,
    trust_level: str = Query(..., description="New trust level"),
    reason: Optional[str] = Query(default=None, description="Reason for update"),
):
    """
    Update neighborhood trust level.
    """
    engine = CultureContextEngine()
    
    try:
        level = TrustLevel(trust_level)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trust level")
    
    success = engine.update_neighborhood_trust(
        neighborhood_id=neighborhood_id,
        trust_level=level,
        reason=reason,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    
    return {"status": "updated", "neighborhood_id": neighborhood_id, "trust_level": trust_level}


@router.get("/context/youth/{location}")
async def get_youth_context(location: str):
    """
    Get youth vulnerability context for a location.
    """
    engine = CultureContextEngine()
    
    context = engine.get_youth_vulnerability_context(location)
    
    return context


@router.get("/context/domestic-violence/{location}")
async def get_domestic_violence_context(location: str):
    """
    Get domestic violence cultural context.
    """
    engine = CultureContextEngine()
    
    context = engine.get_domestic_violence_context(location)
    
    return context


@router.get("/context/trauma/{location}")
async def get_trauma_context(location: str):
    """
    Get historical trauma context.
    """
    engine = CultureContextEngine()
    
    context = engine.get_historical_trauma_context(location)
    
    return context


@router.post("/graph/build")
async def build_reasoning_graph(request: ReasoningRequest):
    """
    Build a moral reasoning graph for an action.
    """
    graph = MoralGraph()
    
    result = graph.build_reasoning_graph(
        action_type=request.action_type,
        context=request.context or {},
    )
    
    return result


@router.get("/graph/export")
async def export_graph():
    """
    Export the entire moral reasoning graph.
    """
    graph = MoralGraph()
    
    return graph.export_graph()


@router.post("/graph/capsule")
async def generate_capsule(request: ReasoningRequest):
    """
    Generate an explainability capsule.
    """
    engine = MoralEngine()
    graph = MoralGraph()
    
    decision = engine.make_decision(
        action_type=request.action_type,
        action_description=f"Capsule generation for {request.action_type}",
        requester_id="capsule_api",
        context=request.context,
    )
    
    capsule = graph.generate_explainability_capsule(
        action_type=request.action_type,
        decision=decision.decision_type.value,
        context=request.context or {},
    )
    
    return capsule.to_dict()


@router.get("/graph/capsule/{capsule_id}")
async def get_capsule(capsule_id: str):
    """
    Get an explainability capsule by ID.
    """
    graph = MoralGraph()
    
    capsule = graph.get_capsule(capsule_id)
    
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    
    return capsule.to_dict()


@router.post("/graph/responsible-plan")
async def generate_responsible_plan(request: ReasoningRequest):
    """
    Generate a responsible AI action plan.
    """
    graph = MoralGraph()
    
    plan = graph.generate_responsible_ai_plan(
        action_type=request.action_type,
        context=request.context or {},
    )
    
    return plan


@router.post("/veto")
async def veto_action(
    action_type: str = Query(..., description="Action type to veto"),
    reason: str = Query(..., description="Reason for veto"),
    requester_id: str = Query(..., description="Requester ID"),
):
    """
    Veto a high-risk action.
    """
    engine = MoralEngine()
    
    decision = engine.veto_action(
        action_type=action_type,
        reason=reason,
        requester_id=requester_id,
    )
    
    return {
        "decision_id": decision.decision_id,
        "decision_type": decision.decision_type.value,
        "explanation": decision.explanation,
        "alternatives": decision.alternatives,
    }


@router.get("/statistics")
async def get_statistics():
    """
    Get comprehensive statistics from all moral compass components.
    """
    engine = MoralEngine()
    guardrails = EthicalGuardrails()
    analyzer = FairnessAnalyzer()
    context_engine = CultureContextEngine()
    graph = MoralGraph()
    
    return {
        "moral_engine": engine.get_statistics(),
        "ethical_guardrails": guardrails.get_statistics(),
        "fairness_analyzer": analyzer.get_statistics(),
        "culture_context": context_engine.get_statistics(),
        "moral_graph": graph.get_statistics(),
    }


@router.get("/assessment/{assessment_id}")
async def get_assessment(assessment_id: str):
    """
    Get a specific moral assessment by ID.
    """
    engine = MoralEngine()
    
    assessment = engine.get_assessment(assessment_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessment.to_dict()


@router.get("/decision/{decision_id}")
async def get_decision(decision_id: str):
    """
    Get a specific moral decision by ID.
    """
    engine = MoralEngine()
    
    decision = engine.get_decision(decision_id)
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    return decision.to_dict()


@router.post("/harmful-intent")
async def detect_harmful_intent(request: GuardrailCheckRequest):
    """
    Detect potential harmful intent in an action.
    """
    guardrails = EthicalGuardrails()
    
    result = guardrails.detect_harmful_intent(
        action_type=request.action_type,
        action_description=request.action_description,
        context=request.context,
    )
    
    return result


@router.post("/discrimination-check")
async def check_discrimination(
    action_type: str = Query(..., description="Action type"),
    context: Optional[Dict[str, Any]] = None,
):
    """
    Check for potential discrimination in an action.
    """
    guardrails = EthicalGuardrails()
    
    result = guardrails.flag_discrimination(
        action_type=action_type,
        context=context or {},
    )
    
    return result


@router.post("/use-of-force/validate")
async def validate_use_of_force(
    force_level: str = Query(..., description="Proposed force level"),
    context: Optional[Dict[str, Any]] = None,
):
    """
    Validate a use of force recommendation.
    """
    guardrails = EthicalGuardrails()
    
    result = guardrails.validate_use_of_force(
        force_level=force_level,
        context=context or {},
    )
    
    return result


@router.post("/bias-prevention")
async def prevent_bias_reinforcement(
    action_type: str = Query(..., description="Action type"),
    historical_data: Optional[Dict[str, Any]] = None,
):
    """
    Check for bias reinforcement patterns.
    """
    guardrails = EthicalGuardrails()
    
    result = guardrails.prevent_bias_reinforcement(
        action_type=action_type,
        historical_data=historical_data,
    )
    
    return result


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the moral compass service.
    """
    return {
        "status": "healthy",
        "service": "moral_compass",
        "timestamp": datetime.utcnow().isoformat(),
    }
