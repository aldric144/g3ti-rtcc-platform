"""
Phase 30: Human Intel API Router

API endpoints for Human Stability Intelligence Engine:
- POST /api/human-intel/mental-health/check
- POST /api/human-intel/suicide-risk
- POST /api/human-intel/dv-escalation
- POST /api/human-intel/crisis-route
- POST /api/human-intel/youth-risk
- GET  /api/human-intel/stability-map
- GET  /api/human-intel/community-pulse

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/human-intel", tags=["Human Intelligence"])


class MentalHealthCheckRequest(BaseModel):
    """Request model for mental health check"""
    call_narrative: str = Field(..., description="911 call narrative or crisis report")
    caller_type: str = Field(default="unknown", description="Type of caller (self, family, neighbor, etc.)")
    location_type: str = Field(default="unknown", description="Type of location")
    prior_crisis_calls: int = Field(default=0, description="Number of prior crisis calls")
    additional_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class MentalHealthCheckResponse(BaseModel):
    """Response model for mental health check"""
    check_id: str
    timestamp: str
    risk_level: str
    confidence_score: float
    risk_factors: List[str]
    protective_factors: List[str]
    recommended_actions: List[str]
    data_sources_used: List[str]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str


class SuicideRiskRequest(BaseModel):
    """Request model for suicide risk assessment"""
    call_narrative: str = Field(..., description="911 call narrative")
    caller_type: str = Field(default="unknown", description="Type of caller")
    prior_welfare_checks: int = Field(default=0, description="Number of prior welfare checks")
    prior_crisis_calls: int = Field(default=0, description="Number of prior crisis calls")
    location_type: str = Field(default="unknown", description="Type of location")
    time_of_day: Optional[str] = Field(default=None, description="Time of day category")
    additional_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class SuicideRiskResponse(BaseModel):
    """Response model for suicide risk assessment"""
    assessment_id: str
    timestamp: str
    risk_level: str
    confidence_score: float
    risk_factors: List[str]
    protective_factors: List[str]
    crisis_phrases_detected: List[str]
    recommended_actions: List[str]
    auto_alert_triggered: bool
    alert_recipients: List[str]
    data_sources_used: List[str]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str


class DVEscalationRequest(BaseModel):
    """Request model for DV escalation assessment"""
    incident_narrative: str = Field(..., description="Incident narrative")
    repeat_call_count: int = Field(default=0, description="Number of repeat calls")
    alcohol_involved: bool = Field(default=False, description="Whether alcohol is involved")
    weapons_present: bool = Field(default=False, description="Whether weapons are present")
    prior_threats: bool = Field(default=False, description="Whether prior threats were made")
    children_present: bool = Field(default=False, description="Whether children are present")
    victim_pregnant: bool = Field(default=False, description="Whether victim is pregnant")
    separation_attempt: bool = Field(default=False, description="Whether separation was attempted")
    strangulation_history: bool = Field(default=False, description="History of strangulation")
    additional_indicators: Optional[List[str]] = Field(default=None, description="Additional Campbell indicators")


class DVEscalationResponse(BaseModel):
    """Response model for DV escalation assessment"""
    assessment_id: str
    timestamp: str
    escalation_level: str
    lethality_risk_score: float
    confidence_score: float
    risk_factors: List[str]
    campbell_danger_indicators: List[str]
    intervention_pathway: str
    recommended_actions: List[str]
    data_sources_used: List[str]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str


class CrisisRouteRequest(BaseModel):
    """Request model for crisis routing"""
    call_narrative: str = Field(..., description="Call narrative")
    call_type: str = Field(..., description="Type of call")
    location_type: str = Field(default="unknown", description="Type of location")
    caller_relationship: str = Field(default="unknown", description="Caller relationship")
    prior_calls_count: int = Field(default=0, description="Number of prior calls")
    weapons_mentioned: bool = Field(default=False, description="Whether weapons are mentioned")
    violence_mentioned: bool = Field(default=False, description="Whether violence is mentioned")
    substance_involved: bool = Field(default=False, description="Whether substances are involved")
    youth_involved: bool = Field(default=False, description="Whether youth are involved")
    elderly_involved: bool = Field(default=False, description="Whether elderly are involved")


class CrisisRouteResponse(BaseModel):
    """Response model for crisis routing"""
    decision_id: str
    timestamp: str
    call_type: str
    priority: str
    primary_responder: str
    co_responders: List[str]
    routing_rationale: str
    de_escalation_prompts: List[str]
    communication_strategies: List[str]
    clinician_involvement: str
    recommended_actions: List[str]
    risk_level: str
    data_sources_used: List[str]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str


class YouthRiskRequest(BaseModel):
    """Request model for youth risk assessment"""
    school_zone: str = Field(..., description="School zone identifier")
    age_group: str = Field(..., description="Age group (elementary, middle, high)")
    incident_history: Optional[List[str]] = Field(default=None, description="Incident history indicators")
    truancy_indicators: Optional[List[str]] = Field(default=None, description="Truancy indicators")
    family_factors: Optional[List[str]] = Field(default=None, description="Family factors")
    peer_factors: Optional[List[str]] = Field(default=None, description="Peer factors")
    protective_factors: Optional[List[str]] = Field(default=None, description="Protective factors")


class YouthRiskResponse(BaseModel):
    """Response model for youth risk assessment"""
    assessment_id: str
    timestamp: str
    risk_level: str
    risk_types: List[str]
    confidence_score: float
    risk_factors: List[str]
    protective_factors: List[str]
    recommended_interventions: List[str]
    urgency: str
    data_sources_used: List[str]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str


class StabilityMapResponse(BaseModel):
    """Response model for stability map"""
    map_id: str
    timestamp: str
    overall_stability_score: float
    mental_health_score: float
    violence_score: float
    community_cohesion_score: float
    youth_stability_score: float
    trend_7_day: float
    trend_30_day: float
    high_risk_areas: List[Dict[str, Any]]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str


class CommunityPulseResponse(BaseModel):
    """Response model for community pulse"""
    pulse_id: str
    timestamp: str
    stability_index: float
    community_shock_level: float
    trauma_clusters: List[Dict[str, Any]]
    school_disturbances: List[Dict[str, Any]]
    youth_violence_warnings: List[str]
    at_risk_polygons: List[Dict[str, Any]]
    trend_direction: str
    recommended_interventions: List[str]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str


@router.post("/mental-health/check", response_model=MentalHealthCheckResponse)
async def check_mental_health(request: MentalHealthCheckRequest) -> MentalHealthCheckResponse:
    """
    Perform mental health crisis check
    
    Analyzes call narrative for mental health crisis indicators
    and provides recommended response actions.
    """
    from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
    from backend.app.human_intel.privacy_guard import PrivacyGuard
    
    privacy_guard = PrivacyGuard()
    privacy_check = privacy_guard.check_query(
        query_type="mental_health_check",
        data_sources=["911_call"],
        contains_pii=False,
    )
    
    if not privacy_check.approved:
        raise HTTPException(
            status_code=403,
            detail=f"Privacy check failed: {[v.value for v in privacy_check.violations]}"
        )
    
    engine = BehavioralCrisisEngine()
    
    assessment = engine.assess_suicide_risk(
        call_narrative=request.call_narrative,
        caller_type=request.caller_type,
        prior_welfare_checks=0,
        prior_crisis_calls=request.prior_crisis_calls,
        location_type=request.location_type,
        additional_context=request.additional_context,
    )
    
    if not assessment:
        raise HTTPException(status_code=500, detail="Assessment failed")
    
    return MentalHealthCheckResponse(
        check_id=assessment.assessment_id,
        timestamp=assessment.timestamp.isoformat(),
        risk_level=assessment.risk_level.name,
        confidence_score=assessment.confidence_score,
        risk_factors=assessment.risk_factors,
        protective_factors=assessment.protective_factors,
        recommended_actions=assessment.recommended_actions,
        data_sources_used=assessment.data_sources_used,
        anonymization_level=assessment.anonymization_level,
        privacy_protections=assessment.privacy_protections,
        chain_of_custody_hash=assessment.chain_of_custody_hash,
    )


@router.post("/suicide-risk", response_model=SuicideRiskResponse)
async def assess_suicide_risk(request: SuicideRiskRequest) -> SuicideRiskResponse:
    """
    Assess suicide risk from 911 call or crisis report
    
    Uses crisis phrase detection, prior welfare check history,
    and CAD call escalation patterns.
    """
    from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
    from backend.app.human_intel.privacy_guard import PrivacyGuard
    
    privacy_guard = PrivacyGuard()
    privacy_check = privacy_guard.check_query(
        query_type="suicide_risk_assessment",
        data_sources=["911_call", "cad_history"],
        contains_pii=False,
    )
    
    if not privacy_check.approved:
        raise HTTPException(
            status_code=403,
            detail=f"Privacy check failed: {[v.value for v in privacy_check.violations]}"
        )
    
    engine = BehavioralCrisisEngine()
    
    assessment = engine.assess_suicide_risk(
        call_narrative=request.call_narrative,
        caller_type=request.caller_type,
        prior_welfare_checks=request.prior_welfare_checks,
        prior_crisis_calls=request.prior_crisis_calls,
        location_type=request.location_type,
        time_of_day=request.time_of_day,
        additional_context=request.additional_context,
    )
    
    if not assessment:
        raise HTTPException(status_code=500, detail="Assessment failed")
    
    return SuicideRiskResponse(
        assessment_id=assessment.assessment_id,
        timestamp=assessment.timestamp.isoformat(),
        risk_level=assessment.risk_level.name,
        confidence_score=assessment.confidence_score,
        risk_factors=assessment.risk_factors,
        protective_factors=assessment.protective_factors,
        crisis_phrases_detected=assessment.crisis_phrases_detected,
        recommended_actions=assessment.recommended_actions,
        auto_alert_triggered=assessment.auto_alert_triggered,
        alert_recipients=assessment.alert_recipients,
        data_sources_used=assessment.data_sources_used,
        anonymization_level=assessment.anonymization_level,
        privacy_protections=assessment.privacy_protections,
        chain_of_custody_hash=assessment.chain_of_custody_hash,
    )


@router.post("/dv-escalation", response_model=DVEscalationResponse)
async def assess_dv_escalation(request: DVEscalationRequest) -> DVEscalationResponse:
    """
    Assess domestic violence escalation risk
    
    Uses Campbell Danger Assessment methodology to evaluate
    lethality risk and recommend intervention pathways.
    """
    from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
    from backend.app.human_intel.privacy_guard import PrivacyGuard
    
    privacy_guard = PrivacyGuard()
    privacy_check = privacy_guard.check_query(
        query_type="dv_escalation_assessment",
        data_sources=["911_call", "incident_reports"],
        contains_pii=False,
    )
    
    if not privacy_check.approved:
        raise HTTPException(
            status_code=403,
            detail=f"Privacy check failed: {[v.value for v in privacy_check.violations]}"
        )
    
    engine = BehavioralCrisisEngine()
    
    assessment = engine.assess_dv_escalation(
        incident_narrative=request.incident_narrative,
        repeat_call_count=request.repeat_call_count,
        alcohol_involved=request.alcohol_involved,
        weapons_present=request.weapons_present,
        prior_threats=request.prior_threats,
        children_present=request.children_present,
        victim_pregnant=request.victim_pregnant,
        separation_attempt=request.separation_attempt,
        strangulation_history=request.strangulation_history,
        additional_indicators=request.additional_indicators,
    )
    
    if not assessment:
        raise HTTPException(status_code=500, detail="Assessment failed")
    
    return DVEscalationResponse(
        assessment_id=assessment.assessment_id,
        timestamp=assessment.timestamp.isoformat(),
        escalation_level=assessment.escalation_level.name,
        lethality_risk_score=assessment.lethality_risk_score,
        confidence_score=assessment.confidence_score,
        risk_factors=assessment.risk_factors,
        campbell_danger_indicators=assessment.campbell_danger_indicators,
        intervention_pathway=assessment.intervention_pathway,
        recommended_actions=assessment.recommended_actions,
        data_sources_used=assessment.data_sources_used,
        anonymization_level=assessment.anonymization_level,
        privacy_protections=assessment.privacy_protections,
        chain_of_custody_hash=assessment.chain_of_custody_hash,
    )


@router.post("/crisis-route", response_model=CrisisRouteResponse)
async def route_crisis_call(request: CrisisRouteRequest) -> CrisisRouteResponse:
    """
    Route a crisis call to appropriate responders
    
    Determines optimal responder combinations and provides
    trauma-informed guidance for crisis calls.
    """
    from backend.app.human_intel.crisis_intervention_engine import CrisisInterventionEngine
    from backend.app.human_intel.privacy_guard import PrivacyGuard
    
    privacy_guard = PrivacyGuard()
    privacy_check = privacy_guard.check_query(
        query_type="crisis_routing",
        data_sources=["911_call", "cad_history"],
        contains_pii=False,
    )
    
    if not privacy_check.approved:
        raise HTTPException(
            status_code=403,
            detail=f"Privacy check failed: {[v.value for v in privacy_check.violations]}"
        )
    
    engine = CrisisInterventionEngine()
    
    decision = engine.route_crisis_call(
        call_narrative=request.call_narrative,
        call_type=request.call_type,
        location_type=request.location_type,
        caller_relationship=request.caller_relationship,
        prior_calls_count=request.prior_calls_count,
        weapons_mentioned=request.weapons_mentioned,
        violence_mentioned=request.violence_mentioned,
        substance_involved=request.substance_involved,
        youth_involved=request.youth_involved,
        elderly_involved=request.elderly_involved,
    )
    
    return CrisisRouteResponse(
        decision_id=decision.decision_id,
        timestamp=decision.timestamp.isoformat(),
        call_type=decision.call_type,
        priority=decision.priority.name,
        primary_responder=decision.co_responder_recommendation.primary_responder.value,
        co_responders=[r.value for r in decision.co_responder_recommendation.co_responders],
        routing_rationale=decision.co_responder_recommendation.rationale,
        de_escalation_prompts=decision.trauma_informed_guidance.de_escalation_prompts,
        communication_strategies=decision.trauma_informed_guidance.communication_strategies,
        clinician_involvement=decision.trauma_informed_guidance.clinician_involvement,
        recommended_actions=decision.recommended_actions,
        risk_level=decision.risk_level,
        data_sources_used=decision.data_sources_used,
        anonymization_level=decision.anonymization_level,
        privacy_protections=decision.privacy_protections,
        chain_of_custody_hash=decision.chain_of_custody_hash,
    )


@router.post("/youth-risk", response_model=YouthRiskResponse)
async def assess_youth_risk(request: YouthRiskRequest) -> YouthRiskResponse:
    """
    Assess youth risk level
    
    Uses aggregated, anonymized data to identify risk patterns
    without individual identification.
    """
    from backend.app.human_intel.youth_crisis_engine import YouthCrisisEngine
    from backend.app.human_intel.privacy_guard import PrivacyGuard
    
    privacy_guard = PrivacyGuard()
    privacy_check = privacy_guard.check_query(
        query_type="youth_risk_assessment",
        data_sources=["aggregated_school_data", "aggregated_incident_data"],
        contains_pii=False,
    )
    
    if not privacy_check.approved:
        raise HTTPException(
            status_code=403,
            detail=f"Privacy check failed: {[v.value for v in privacy_check.violations]}"
        )
    
    engine = YouthCrisisEngine()
    
    assessment = engine.assess_youth_risk(
        school_zone=request.school_zone,
        age_group=request.age_group,
        incident_history=request.incident_history,
        truancy_indicators=request.truancy_indicators,
        family_factors=request.family_factors,
        peer_factors=request.peer_factors,
        protective_factors=request.protective_factors,
    )
    
    if not assessment:
        raise HTTPException(status_code=500, detail="Assessment failed")
    
    return YouthRiskResponse(
        assessment_id=assessment.assessment_id,
        timestamp=assessment.timestamp.isoformat(),
        risk_level=assessment.risk_level.name,
        risk_types=[rt.value for rt in assessment.risk_types],
        confidence_score=assessment.confidence_score,
        risk_factors=assessment.risk_factors,
        protective_factors=assessment.protective_factors,
        recommended_interventions=[i.value for i in assessment.recommended_interventions],
        urgency=assessment.urgency,
        data_sources_used=assessment.data_sources_used,
        anonymization_level=assessment.anonymization_level,
        privacy_protections=assessment.privacy_protections,
        chain_of_custody_hash=assessment.chain_of_custody_hash,
    )


@router.get("/stability-map", response_model=StabilityMapResponse)
async def get_stability_map() -> StabilityMapResponse:
    """
    Get city stability map
    
    Returns zone-level stability scores and risk indicators.
    """
    from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
    from backend.app.human_intel.privacy_guard import PrivacyGuard
    
    privacy_guard = PrivacyGuard()
    privacy_check = privacy_guard.check_query(
        query_type="stability_map",
        data_sources=["aggregated_data"],
        contains_pii=False,
    )
    
    if not privacy_check.approved:
        raise HTTPException(
            status_code=403,
            detail=f"Privacy check failed: {[v.value for v in privacy_check.violations]}"
        )
    
    engine = BehavioralCrisisEngine()
    index = engine.get_stability_index()
    
    return StabilityMapResponse(
        map_id=index.index_id,
        timestamp=index.timestamp.isoformat(),
        overall_stability_score=index.overall_score,
        mental_health_score=index.mental_health_score,
        violence_score=index.violence_score,
        community_cohesion_score=index.community_cohesion_score,
        youth_stability_score=index.youth_stability_score,
        trend_7_day=index.trend_7_day,
        trend_30_day=index.trend_30_day,
        high_risk_areas=index.high_risk_areas,
        anonymization_level="AGGREGATED",
        privacy_protections=[
            "Zone-level data only",
            "No individual identification",
            "Aggregated statistics",
        ],
        chain_of_custody_hash=index.chain_of_custody_hash,
    )


@router.get("/community-pulse", response_model=CommunityPulseResponse)
async def get_community_pulse(
    time_window_hours: int = Query(default=72, description="Time window in hours"),
) -> CommunityPulseResponse:
    """
    Get community trauma pulse
    
    Returns community-level trauma indicators and stability metrics.
    """
    from backend.app.human_intel.behavioral_crisis_engine import BehavioralCrisisEngine
    from backend.app.human_intel.privacy_guard import PrivacyGuard
    
    privacy_guard = PrivacyGuard()
    privacy_check = privacy_guard.check_query(
        query_type="community_pulse",
        data_sources=["aggregated_incidents", "public_records"],
        contains_pii=False,
    )
    
    if not privacy_check.approved:
        raise HTTPException(
            status_code=403,
            detail=f"Privacy check failed: {[v.value for v in privacy_check.violations]}"
        )
    
    engine = BehavioralCrisisEngine()
    pulse = engine.get_community_trauma_pulse(time_window_hours=time_window_hours)
    
    return CommunityPulseResponse(
        pulse_id=pulse.pulse_id,
        timestamp=pulse.timestamp.isoformat(),
        stability_index=pulse.stability_index,
        community_shock_level=pulse.community_shock_level,
        trauma_clusters=pulse.trauma_clusters,
        school_disturbances=pulse.school_disturbances,
        youth_violence_warnings=pulse.youth_violence_warnings,
        at_risk_polygons=pulse.at_risk_polygons,
        trend_direction=pulse.trend_direction,
        recommended_interventions=pulse.recommended_interventions,
        anonymization_level=pulse.anonymization_level,
        privacy_protections=pulse.privacy_protections,
        chain_of_custody_hash=pulse.chain_of_custody_hash,
    )
