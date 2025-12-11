"""
Officer Assist API Router

Provides REST API endpoints for the AI Officer Assist Suite:
- POST /api/officer-assist/guardrails/check
- POST /api/officer-assist/use-of-force/risk
- POST /api/officer-assist/tactical-advice
- POST /api/officer-assist/intent
- GET  /api/officer-assist/officer/{id}/status
- GET  /api/officer-assist/alerts
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ..officer_assist import (
    ConstitutionalGuardrailEngine,
    GuardrailResult,
    GuardrailStatus,
    ActionContext,
    ActionType,
    UseOfForceRiskMonitor,
    ForceRiskAssessment,
    RiskLevel,
    SuspectBehaviorClass,
    SceneEscalationPattern,
    WeaponType,
    OfficerVitals,
    SceneContext,
    OfficerBehavioralSafetyEngine,
    OfficerSafetyStatus,
    OfficerWorkload,
    OfficerHistory,
    StressIndicator,
    TacticalAdvisorEngine,
    TacticalAdvice,
    TacticalScenario,
    ThreatLevel,
    SceneLocation,
    OfficerIntentInterpreter,
    OfficerIntent,
    InputSource,
)


class GuardrailCheckRequest(BaseModel):
    """Request for constitutional guardrail check"""
    action_type: str
    officer_id: str
    incident_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    subject_demographics: Optional[Dict[str, Any]] = None
    probable_cause: Optional[str] = None
    reasonable_suspicion: Optional[str] = None
    consent_obtained: bool = False
    consent_voluntary: Optional[bool] = None
    miranda_given: bool = False
    custodial: bool = False
    weapon_involved: bool = False
    force_level: Optional[str] = None
    pursuit_speed: Optional[float] = None
    pursuit_reason: Optional[str] = None
    search_scope: Optional[str] = None
    detention_duration_minutes: Optional[int] = None
    prior_contacts_24h: int = 0


class GuardrailCheckResponse(BaseModel):
    """Response from guardrail check"""
    result_id: str
    timestamp: datetime
    action_type: str
    overall_status: str
    risk_level: str
    guardrail_status: str
    reason: str
    recommended_action: Optional[str] = None
    citations: List[str] = []
    constitutional_issues: List[str] = []
    policy_issues: List[str] = []
    recommendations: List[str] = []
    supervisor_alert_required: bool = False
    command_staff_alert_required: bool = False
    legal_risk_score: float = 0.0
    civil_liability_risk: str = "LOW"


class UseOfForceRiskRequest(BaseModel):
    """Request for use-of-force risk assessment"""
    incident_id: str
    officer_id: str
    suspect_behavior: str
    escalation_pattern: str = "STABLE"
    weapon_type: str = "NONE"
    weapon_probability: float = 0.0
    officer_proximity_feet: Optional[float] = None
    officer_vitals: Optional[Dict[str, Any]] = None
    scene_context: Optional[Dict[str, Any]] = None


class UseOfForceRiskResponse(BaseModel):
    """Response from use-of-force risk assessment"""
    assessment_id: str
    timestamp: datetime
    incident_id: str
    officer_id: str
    risk_level: str
    risk_score: float
    reason: str
    recommended_action: str
    risk_factors: List[str] = []
    protective_factors: List[str] = []
    recommended_actions: List[str] = []
    supervisor_notified: bool = False
    rtcc_notified: bool = False
    backup_requested: bool = False
    de_escalation_recommended: bool = False


class TacticalAdviceRequest(BaseModel):
    """Request for tactical advice"""
    incident_id: str
    officer_id: str
    scenario: str
    location: Optional[Dict[str, Any]] = None
    threat_level: str = "MODERATE"
    suspect_armed: bool = False
    suspect_count: int = 1
    officer_count: int = 1


class TacticalAdviceResponse(BaseModel):
    """Response with tactical advice"""
    advice_id: str
    timestamp: datetime
    incident_id: str
    scenario: str
    threat_level: str
    risk_level: str
    reason: str
    recommended_action: str
    primary_recommendation: str
    tactical_notes: List[str] = []
    warnings: List[str] = []
    de_escalation_options: List[str] = []
    cover_positions: List[Dict[str, Any]] = []
    escape_routes: List[Dict[str, Any]] = []
    backup_units: List[Dict[str, Any]] = []
    building_entries: List[Dict[str, Any]] = []
    communication_plan: Optional[str] = None
    containment_strategy: Optional[str] = None
    lethal_cover_required: bool = False
    k9_recommended: bool = False
    air_support_recommended: bool = False


class IntentRequest(BaseModel):
    """Request for intent interpretation"""
    officer_id: str
    raw_input: str
    input_source: str = "RADIO"
    incident_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class IntentResponse(BaseModel):
    """Response from intent interpretation"""
    intent_id: str
    timestamp: datetime
    officer_id: str
    intent_type: str
    confidence: str
    confidence_score: float
    risk_level: str
    guardrail_status: str
    reason: str
    recommended_action: Optional[str] = None
    citation: Optional[str] = None
    extracted_entities: Dict[str, Any] = {}
    guardrail_triggered: bool = False
    guardrail_result: Optional[Dict[str, Any]] = None
    tactical_advice_generated: bool = False
    requires_supervisor_review: bool = False
    notes: List[str] = []


class OfficerStatusResponse(BaseModel):
    """Response with officer status"""
    status_id: str
    timestamp: datetime
    officer_id: str
    overall_risk_score: float
    risk_level: str
    guardrail_status: str
    reason: str
    recommended_action: str
    fatigue_level: str
    fatigue_score: float
    stress_score: float
    stress_indicators: List[str] = []
    workload_score: float
    trauma_exposure_score: float
    pattern_flags: List[str] = []
    recommendations: List[str] = []
    fit_for_duty: bool = True
    supervisor_review_required: bool = False


class AlertsResponse(BaseModel):
    """Response with alerts"""
    total_alerts: int
    unacknowledged: int
    high_severity: int
    alerts: List[Dict[str, Any]] = []


class OfficerAssistRouter:
    """
    Officer Assist API Router
    
    Provides REST API endpoints for the AI Officer Assist Suite.
    """
    
    def __init__(self):
        self.guardrail_engine = ConstitutionalGuardrailEngine()
        self.force_monitor = UseOfForceRiskMonitor()
        self.safety_engine = OfficerBehavioralSafetyEngine()
        self.tactical_advisor = TacticalAdvisorEngine()
        self.intent_interpreter = OfficerIntentInterpreter()
    
    def check_guardrails(self, request: GuardrailCheckRequest) -> GuardrailCheckResponse:
        """
        POST /api/officer-assist/guardrails/check
        
        Check constitutional and policy guardrails for an action.
        """
        try:
            action_type = ActionType(request.action_type)
        except ValueError:
            action_type = ActionType.TRAFFIC_STOP
        
        context = ActionContext(
            action_type=action_type,
            officer_id=request.officer_id,
            incident_id=request.incident_id,
            location=request.location,
            subject_demographics=request.subject_demographics,
            probable_cause=request.probable_cause,
            reasonable_suspicion=request.reasonable_suspicion,
            consent_obtained=request.consent_obtained,
            consent_voluntary=request.consent_voluntary,
            miranda_given=request.miranda_given,
            custodial=request.custodial,
            weapon_involved=request.weapon_involved,
            force_level=request.force_level,
            pursuit_speed=request.pursuit_speed,
            pursuit_reason=request.pursuit_reason,
            search_scope=request.search_scope,
            detention_duration_minutes=request.detention_duration_minutes,
            prior_contacts_24h=request.prior_contacts_24h,
        )
        
        result = self.guardrail_engine.evaluate_action(context)
        
        citations = []
        for check in result.checks:
            if check.legal_citation:
                citations.append(check.legal_citation)
            if check.policy_reference:
                citations.append(check.policy_reference)
        
        reason = "Action complies with constitutional and policy requirements"
        if result.overall_status == GuardrailStatus.WARNING:
            reason = f"Legal/policy concerns detected: {'; '.join(result.constitutional_issues + result.policy_issues)[:200]}"
        elif result.overall_status == GuardrailStatus.BLOCKED:
            reason = f"Action blocked due to: {'; '.join(result.constitutional_issues + result.policy_issues)[:200]}"
        
        recommended_action = result.recommendations[0] if result.recommendations else None
        
        return GuardrailCheckResponse(
            result_id=result.result_id,
            timestamp=result.timestamp,
            action_type=result.action_type.value,
            overall_status=result.overall_status.value,
            risk_level=result.civil_liability_risk,
            guardrail_status=result.overall_status.value,
            reason=reason,
            recommended_action=recommended_action,
            citations=list(set(citations)),
            constitutional_issues=result.constitutional_issues,
            policy_issues=result.policy_issues,
            recommendations=result.recommendations,
            supervisor_alert_required=result.supervisor_alert_required,
            command_staff_alert_required=result.command_staff_alert_required,
            legal_risk_score=result.legal_risk_score,
            civil_liability_risk=result.civil_liability_risk,
        )
    
    def assess_use_of_force_risk(self, request: UseOfForceRiskRequest) -> UseOfForceRiskResponse:
        """
        POST /api/officer-assist/use-of-force/risk
        
        Assess use-of-force risk level for a situation.
        """
        try:
            suspect_behavior = SuspectBehaviorClass(request.suspect_behavior)
        except ValueError:
            suspect_behavior = SuspectBehaviorClass.COMPLIANT
        
        try:
            escalation_pattern = SceneEscalationPattern(request.escalation_pattern)
        except ValueError:
            escalation_pattern = SceneEscalationPattern.STABLE
        
        try:
            weapon_type = WeaponType(request.weapon_type)
        except ValueError:
            weapon_type = WeaponType.NONE
        
        officer_vitals = None
        if request.officer_vitals:
            officer_vitals = OfficerVitals(**request.officer_vitals)
        
        scene_context = None
        if request.scene_context:
            scene_context = SceneContext(**request.scene_context)
        
        assessment = self.force_monitor.assess_risk(
            incident_id=request.incident_id,
            officer_id=request.officer_id,
            suspect_behavior=suspect_behavior,
            escalation_pattern=escalation_pattern,
            weapon_type=weapon_type,
            weapon_probability=request.weapon_probability,
            officer_proximity_feet=request.officer_proximity_feet,
            officer_vitals=officer_vitals,
            scene_context=scene_context,
        )
        
        reason = f"Risk level {assessment.risk_level.value} based on suspect behavior and scene factors"
        recommended_action = assessment.recommended_actions[0] if assessment.recommended_actions else "Maintain situational awareness"
        
        return UseOfForceRiskResponse(
            assessment_id=assessment.assessment_id,
            timestamp=assessment.timestamp,
            incident_id=assessment.incident_id,
            officer_id=assessment.officer_id,
            risk_level=assessment.risk_level.value,
            risk_score=assessment.risk_score,
            reason=reason,
            recommended_action=recommended_action,
            risk_factors=assessment.risk_factors,
            protective_factors=assessment.protective_factors,
            recommended_actions=assessment.recommended_actions,
            supervisor_notified=assessment.supervisor_notified,
            rtcc_notified=assessment.rtcc_notified,
            backup_requested=assessment.backup_requested,
            de_escalation_recommended=assessment.de_escalation_recommended,
        )
    
    def get_tactical_advice(self, request: TacticalAdviceRequest) -> TacticalAdviceResponse:
        """
        POST /api/officer-assist/tactical-advice
        
        Get tactical advice for a scenario.
        """
        try:
            scenario = TacticalScenario(request.scenario)
        except ValueError:
            scenario = TacticalScenario.TRAFFIC_STOP
        
        try:
            threat_level = ThreatLevel(request.threat_level)
        except ValueError:
            threat_level = ThreatLevel.MODERATE
        
        location = None
        if request.location:
            location = SceneLocation(**request.location)
        
        advice = self.tactical_advisor.get_tactical_advice(
            incident_id=request.incident_id,
            officer_id=request.officer_id,
            scenario=scenario,
            location=location,
            threat_level=threat_level,
            suspect_armed=request.suspect_armed,
            suspect_count=request.suspect_count,
            officer_count=request.officer_count,
        )
        
        reason = f"Tactical advice for {scenario.value} scenario at {threat_level.value} threat level"
        recommended_action = advice.primary_recommendation
        
        cover_positions = [
            {
                "position_id": cp.position_id,
                "description": cp.description,
                "cover_type": cp.cover_type.value,
                "distance_feet": cp.distance_feet,
                "direction": cp.direction,
                "effectiveness_score": cp.effectiveness_score,
            }
            for cp in advice.cover_positions
        ]
        
        escape_routes = [
            {
                "route_id": er.route_id,
                "description": er.description,
                "probability": er.probability,
                "direction": er.direction,
                "vehicle_accessible": er.vehicle_accessible,
                "intercept_points": er.intercept_points,
            }
            for er in advice.escape_routes
        ]
        
        backup_units = [
            {
                "unit_id": bu.unit_id,
                "unit_type": bu.unit_type,
                "eta_minutes": bu.eta_minutes,
                "distance_miles": bu.distance_miles,
                "current_status": bu.current_status,
            }
            for bu in advice.backup_units
        ]
        
        building_entries = [
            {
                "entry_id": be.entry_id,
                "entry_point": be.entry_point,
                "direction": be.direction,
                "risk_level": be.risk_level,
                "recommended": be.recommended,
                "notes": be.notes,
            }
            for be in advice.building_entries
        ]
        
        return TacticalAdviceResponse(
            advice_id=advice.advice_id,
            timestamp=advice.timestamp,
            incident_id=advice.incident_id,
            scenario=advice.scenario.value,
            threat_level=advice.threat_level.value,
            risk_level=advice.threat_level.value,
            reason=reason,
            recommended_action=recommended_action,
            primary_recommendation=advice.primary_recommendation,
            tactical_notes=advice.tactical_notes,
            warnings=advice.warnings,
            de_escalation_options=advice.de_escalation_options,
            cover_positions=cover_positions,
            escape_routes=escape_routes,
            backup_units=backup_units,
            building_entries=building_entries,
            communication_plan=advice.communication_plan,
            containment_strategy=advice.containment_strategy,
            lethal_cover_required=advice.lethal_cover_required,
            k9_recommended=advice.k9_recommended,
            air_support_recommended=advice.air_support_recommended,
        )
    
    def interpret_intent(self, request: IntentRequest) -> IntentResponse:
        """
        POST /api/officer-assist/intent
        
        Interpret officer intent from input.
        """
        try:
            input_source = InputSource(request.input_source)
        except ValueError:
            input_source = InputSource.RADIO
        
        intent = self.intent_interpreter.interpret_input(
            officer_id=request.officer_id,
            raw_input=request.raw_input,
            input_source=input_source,
            incident_id=request.incident_id,
            context=request.context,
        )
        
        risk_level = "LOW"
        if intent.requires_supervisor_review:
            risk_level = "HIGH"
        elif intent.guardrail_triggered:
            risk_level = "MEDIUM"
        
        guardrail_status = "PASS"
        if intent.guardrail_result:
            guardrail_status = intent.guardrail_result.get("status", "PASS")
        
        reason = f"Detected intent: {intent.intent_type.value} with {intent.confidence.value} confidence"
        recommended_action = intent.notes[0] if intent.notes else None
        
        citation = None
        if intent.guardrail_result and intent.guardrail_result.get("checks_performed"):
            citation = f"Checks: {', '.join(intent.guardrail_result['checks_performed'])}"
        
        return IntentResponse(
            intent_id=intent.intent_id,
            timestamp=intent.timestamp,
            officer_id=intent.officer_id,
            intent_type=intent.intent_type.value,
            confidence=intent.confidence.value,
            confidence_score=intent.confidence_score,
            risk_level=risk_level,
            guardrail_status=guardrail_status,
            reason=reason,
            recommended_action=recommended_action,
            citation=citation,
            extracted_entities=intent.extracted_entities,
            guardrail_triggered=intent.guardrail_triggered,
            guardrail_result=intent.guardrail_result,
            tactical_advice_generated=intent.tactical_advice_generated,
            requires_supervisor_review=intent.requires_supervisor_review,
            notes=intent.notes,
        )
    
    def get_officer_status(self, officer_id: str) -> OfficerStatusResponse:
        """
        GET /api/officer-assist/officer/{id}/status
        
        Get officer safety status.
        """
        status = self.safety_engine.get_officer_status(officer_id)
        
        if not status:
            status = self.safety_engine.assess_officer_safety(officer_id=officer_id)
        
        risk_level = "LOW"
        if status.overall_risk_score > 0.7:
            risk_level = "HIGH"
        elif status.overall_risk_score > 0.4:
            risk_level = "MEDIUM"
        
        guardrail_status = "PASS"
        if not status.fit_for_duty:
            guardrail_status = "BLOCKED"
        elif status.supervisor_review_required:
            guardrail_status = "WARNING"
        
        reason = f"Officer safety score: {status.overall_risk_score:.2f}, Fatigue: {status.fatigue_level.value}"
        recommended_action = status.recommendations[0] if status.recommendations else "Continue normal duties"
        
        return OfficerStatusResponse(
            status_id=status.status_id,
            timestamp=status.timestamp,
            officer_id=status.officer_id,
            overall_risk_score=status.overall_risk_score,
            risk_level=risk_level,
            guardrail_status=guardrail_status,
            reason=reason,
            recommended_action=recommended_action,
            fatigue_level=status.fatigue_level.value,
            fatigue_score=status.fatigue_score,
            stress_score=status.stress_score,
            stress_indicators=[si.value for si in status.stress_indicators],
            workload_score=status.workload_score,
            trauma_exposure_score=status.trauma_exposure_score,
            pattern_flags=status.pattern_flags,
            recommendations=status.recommendations,
            fit_for_duty=status.fit_for_duty,
            supervisor_review_required=status.supervisor_review_required,
        )
    
    def get_alerts(
        self,
        limit: int = 100,
        unacknowledged_only: bool = False,
        severity_filter: Optional[str] = None,
    ) -> AlertsResponse:
        """
        GET /api/officer-assist/alerts
        
        Get officer assist alerts.
        """
        safety_alerts = self.safety_engine.get_all_alerts(
            limit=limit,
            unresolved_only=unacknowledged_only,
            severity_filter=severity_filter,
        )
        
        force_alerts = self.force_monitor.get_supervisor_alerts(
            limit=limit,
            unacknowledged_only=unacknowledged_only,
        )
        
        all_alerts = []
        
        for alert in safety_alerts:
            all_alerts.append({
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp.isoformat(),
                "officer_id": alert.officer_id,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity,
                "description": alert.description,
                "risk_score": alert.risk_score,
                "recommended_action": alert.recommended_action,
                "acknowledged": alert.acknowledged,
                "resolved": alert.resolved,
                "source": "safety_engine",
            })
        
        for alert in force_alerts:
            all_alerts.append({
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp.isoformat(),
                "officer_id": alert.officer_id,
                "incident_id": alert.incident_id,
                "alert_type": "USE_OF_FORCE_RISK",
                "severity": "HIGH" if alert.risk_level.value == "RED" else "MEDIUM",
                "description": alert.alert_reason,
                "risk_score": alert.risk_score,
                "recommended_action": alert.recommended_response,
                "acknowledged": alert.acknowledged,
                "source": "force_monitor",
            })
        
        all_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        all_alerts = all_alerts[:limit]
        
        unacknowledged = sum(1 for a in all_alerts if not a.get("acknowledged", False))
        high_severity = sum(1 for a in all_alerts if a.get("severity") == "HIGH")
        
        return AlertsResponse(
            total_alerts=len(all_alerts),
            unacknowledged=unacknowledged,
            high_severity=high_severity,
            alerts=all_alerts,
        )
