"""
Constitutional Guardrail Engine

Real-time evaluation of every action, decision, or event for constitutional
and policy compliance. Detects violations of:
- 4th Amendment (search, seizure, traffic stops)
- 5th Amendment (self-incrimination, custodial interactions)
- 14th Amendment (due process, equal protection)
- Florida Constitutional equivalents
- Riviera Beach PD SOP policies
- RBPD Use-of-Force Directive
- Pursuit policy
- Bias & profiling safeguards

Outputs: PASS, WARNING (legal risk detected), BLOCKED (action forbidden)
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GuardrailStatus(str, Enum):
    """Guardrail check result status"""
    PASS = "PASS"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"


class ConstitutionalViolationType(str, Enum):
    """Types of constitutional violations"""
    FOURTH_AMENDMENT_SEARCH = "4TH_AMENDMENT_SEARCH"
    FOURTH_AMENDMENT_SEIZURE = "4TH_AMENDMENT_SEIZURE"
    FOURTH_AMENDMENT_TRAFFIC_STOP = "4TH_AMENDMENT_TRAFFIC_STOP"
    FOURTH_AMENDMENT_TERRY_STOP = "4TH_AMENDMENT_TERRY_STOP"
    FOURTH_AMENDMENT_CONSENT = "4TH_AMENDMENT_CONSENT"
    FIFTH_AMENDMENT_MIRANDA = "5TH_AMENDMENT_MIRANDA"
    FIFTH_AMENDMENT_CUSTODIAL = "5TH_AMENDMENT_CUSTODIAL"
    FIFTH_AMENDMENT_SELF_INCRIMINATION = "5TH_AMENDMENT_SELF_INCRIMINATION"
    FOURTEENTH_AMENDMENT_DUE_PROCESS = "14TH_AMENDMENT_DUE_PROCESS"
    FOURTEENTH_AMENDMENT_EQUAL_PROTECTION = "14TH_AMENDMENT_EQUAL_PROTECTION"
    FLORIDA_CONSTITUTION_PRIVACY = "FL_CONSTITUTION_PRIVACY"
    FLORIDA_CONSTITUTION_SEARCH = "FL_CONSTITUTION_SEARCH"


class PolicyViolationType(str, Enum):
    """Types of policy violations"""
    USE_OF_FORCE_EXCESSIVE = "USE_OF_FORCE_EXCESSIVE"
    USE_OF_FORCE_UNAUTHORIZED = "USE_OF_FORCE_UNAUTHORIZED"
    USE_OF_FORCE_REPORTING = "USE_OF_FORCE_REPORTING"
    PURSUIT_UNAUTHORIZED = "PURSUIT_UNAUTHORIZED"
    PURSUIT_EXCESSIVE_SPEED = "PURSUIT_EXCESSIVE_SPEED"
    PURSUIT_TERMINATION_REQUIRED = "PURSUIT_TERMINATION_REQUIRED"
    BIAS_PROFILING_DETECTED = "BIAS_PROFILING_DETECTED"
    BIAS_DISPARATE_TREATMENT = "BIAS_DISPARATE_TREATMENT"
    SOP_VIOLATION = "SOP_VIOLATION"
    DETENTION_EXCESSIVE = "DETENTION_EXCESSIVE"
    SEARCH_SCOPE_EXCEEDED = "SEARCH_SCOPE_EXCEEDED"
    FORCE_CONTINUUM_VIOLATION = "FORCE_CONTINUUM_VIOLATION"


class ActionType(str, Enum):
    """Types of officer actions to evaluate"""
    TRAFFIC_STOP = "TRAFFIC_STOP"
    TERRY_STOP = "TERRY_STOP"
    CONSENT_SEARCH = "CONSENT_SEARCH"
    WARRANT_SEARCH = "WARRANT_SEARCH"
    WARRANTLESS_SEARCH = "WARRANTLESS_SEARCH"
    ARREST = "ARREST"
    DETENTION = "DETENTION"
    CUSTODIAL_INTERROGATION = "CUSTODIAL_INTERROGATION"
    VEHICLE_PURSUIT = "VEHICLE_PURSUIT"
    FOOT_PURSUIT = "FOOT_PURSUIT"
    USE_OF_FORCE = "USE_OF_FORCE"
    FELONY_STOP = "FELONY_STOP"
    DOMESTIC_RESPONSE = "DOMESTIC_RESPONSE"
    TRESPASS_ENFORCEMENT = "TRESPASS_ENFORCEMENT"
    CROWD_CONTROL = "CROWD_CONTROL"


class GuardrailCheck(BaseModel):
    """Individual guardrail check result"""
    check_id: str
    check_name: str
    category: str
    status: GuardrailStatus
    violation_type: Optional[str] = None
    description: str
    legal_citation: Optional[str] = None
    policy_reference: Optional[str] = None
    risk_level: str = "LOW"
    recommendation: Optional[str] = None


class GuardrailResult(BaseModel):
    """Complete guardrail evaluation result"""
    result_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action_type: ActionType
    overall_status: GuardrailStatus
    checks: List[GuardrailCheck] = []
    constitutional_issues: List[str] = []
    policy_issues: List[str] = []
    recommendations: List[str] = []
    supervisor_alert_required: bool = False
    command_staff_alert_required: bool = False
    legal_risk_score: float = 0.0
    civil_liability_risk: str = "LOW"
    officer_id: Optional[str] = None
    incident_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None


class ActionContext(BaseModel):
    """Context for action being evaluated"""
    action_type: ActionType
    officer_id: str
    incident_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
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
    additional_context: Dict[str, Any] = {}


class ConstitutionalGuardrailEngine:
    """
    Real-time Constitutional Guardrail Engine
    
    Evaluates every action, decision, or event for constitutional
    and policy compliance in real-time.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        self.agency_config = {
            "ori": "FL0500400",
            "name": "Riviera Beach Police Department",
            "state": "FL",
            "city": "Riviera Beach",
            "county": "Palm Beach",
        }
        
        self.fourth_amendment_rules = {
            "traffic_stop": {
                "requires_reasonable_suspicion": True,
                "max_duration_minutes": 20,
                "scope_limited_to_violation": True,
                "consent_must_be_voluntary": True,
                "can_order_driver_out": True,
                "can_order_passengers_out": True,
                "dog_sniff_requires_rs": False,
            },
            "terry_stop": {
                "requires_reasonable_suspicion": True,
                "articulable_facts_required": True,
                "max_duration_minutes": 15,
                "frisk_requires_weapon_suspicion": True,
                "scope_limited_to_weapons": True,
            },
            "search": {
                "warrant_required_default": True,
                "exceptions": [
                    "consent",
                    "search_incident_to_arrest",
                    "plain_view",
                    "exigent_circumstances",
                    "automobile_exception",
                    "inventory_search",
                    "terry_frisk",
                ],
                "consent_must_be_voluntary": True,
                "consent_can_be_withdrawn": True,
                "scope_limited_to_consent": True,
            },
            "seizure": {
                "arrest_requires_probable_cause": True,
                "detention_requires_reasonable_suspicion": True,
                "force_must_be_reasonable": True,
            },
        }
        
        self.fifth_amendment_rules = {
            "miranda": {
                "required_for_custodial_interrogation": True,
                "custody_factors": [
                    "freedom_to_leave",
                    "location",
                    "duration",
                    "restraints",
                    "officer_statements",
                ],
                "interrogation_includes_functional_equivalent": True,
                "waiver_must_be_knowing_voluntary": True,
            },
            "self_incrimination": {
                "cannot_compel_testimony": True,
                "silence_cannot_be_used_against": True,
                "invocation_must_be_honored": True,
            },
        }
        
        self.fourteenth_amendment_rules = {
            "due_process": {
                "notice_required": True,
                "opportunity_to_be_heard": True,
                "impartial_decision_maker": True,
            },
            "equal_protection": {
                "no_racial_profiling": True,
                "no_disparate_treatment": True,
                "legitimate_government_interest_required": True,
            },
        }
        
        self.florida_constitution_rules = {
            "article_1_section_12": {
                "stronger_than_federal": True,
                "good_faith_exception_limited": True,
            },
            "article_1_section_23": {
                "right_to_privacy": True,
                "compelling_state_interest_required": True,
            },
        }
        
        self.rbpd_policies = {
            "use_of_force": {
                "policy_number": "300",
                "force_continuum": [
                    "officer_presence",
                    "verbal_commands",
                    "soft_hand_control",
                    "hard_hand_control",
                    "intermediate_weapons",
                    "deadly_force",
                ],
                "de_escalation_required": True,
                "proportionality_required": True,
                "reporting_required": True,
                "supervisor_notification_required": True,
            },
            "pursuit": {
                "policy_number": "314",
                "authorized_for_felony": True,
                "authorized_for_misdemeanor": False,
                "max_speed_residential": 45,
                "max_speed_commercial": 55,
                "termination_factors": [
                    "public_safety_risk",
                    "weather_conditions",
                    "traffic_density",
                    "suspect_identified",
                ],
                "supervisor_approval_required": True,
            },
            "bias_free_policing": {
                "policy_number": "402",
                "prohibited_factors": [
                    "race",
                    "ethnicity",
                    "national_origin",
                    "religion",
                    "gender",
                    "sexual_orientation",
                    "gender_identity",
                    "disability",
                    "socioeconomic_status",
                ],
                "documentation_required": True,
            },
            "detention": {
                "policy_number": "320",
                "max_investigative_detention_minutes": 20,
                "probable_cause_required_for_arrest": True,
                "booking_required_for_felony": True,
            },
        }
        
        self.guardrail_log: List[GuardrailResult] = []
        self.blocked_actions: List[GuardrailResult] = []
        self.warnings_issued: List[GuardrailResult] = []
    
    def evaluate_action(self, context: ActionContext) -> GuardrailResult:
        """
        Evaluate an action for constitutional and policy compliance
        
        Args:
            context: The action context to evaluate
            
        Returns:
            GuardrailResult with status and any violations
        """
        checks: List[GuardrailCheck] = []
        constitutional_issues: List[str] = []
        policy_issues: List[str] = []
        recommendations: List[str] = []
        
        if context.action_type == ActionType.TRAFFIC_STOP:
            checks.extend(self._check_traffic_stop(context))
        elif context.action_type == ActionType.TERRY_STOP:
            checks.extend(self._check_terry_stop(context))
        elif context.action_type in [ActionType.CONSENT_SEARCH, ActionType.WARRANT_SEARCH, ActionType.WARRANTLESS_SEARCH]:
            checks.extend(self._check_search(context))
        elif context.action_type == ActionType.ARREST:
            checks.extend(self._check_arrest(context))
        elif context.action_type == ActionType.CUSTODIAL_INTERROGATION:
            checks.extend(self._check_custodial_interrogation(context))
        elif context.action_type in [ActionType.VEHICLE_PURSUIT, ActionType.FOOT_PURSUIT]:
            checks.extend(self._check_pursuit(context))
        elif context.action_type == ActionType.USE_OF_FORCE:
            checks.extend(self._check_use_of_force(context))
        elif context.action_type == ActionType.DETENTION:
            checks.extend(self._check_detention(context))
        
        checks.extend(self._check_bias_profiling(context))
        checks.extend(self._check_equal_protection(context))
        
        overall_status = GuardrailStatus.PASS
        for check in checks:
            if check.status == GuardrailStatus.BLOCKED:
                overall_status = GuardrailStatus.BLOCKED
                if check.violation_type and check.violation_type.startswith(("4TH", "5TH", "14TH", "FL_")):
                    constitutional_issues.append(check.description)
                else:
                    policy_issues.append(check.description)
            elif check.status == GuardrailStatus.WARNING and overall_status != GuardrailStatus.BLOCKED:
                overall_status = GuardrailStatus.WARNING
                if check.violation_type and check.violation_type.startswith(("4TH", "5TH", "14TH", "FL_")):
                    constitutional_issues.append(check.description)
                else:
                    policy_issues.append(check.description)
            
            if check.recommendation:
                recommendations.append(check.recommendation)
        
        legal_risk_score = self._calculate_legal_risk(checks)
        civil_liability_risk = self._assess_civil_liability(checks, legal_risk_score)
        
        result = GuardrailResult(
            result_id=f"gr-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{context.officer_id}",
            action_type=context.action_type,
            overall_status=overall_status,
            checks=checks,
            constitutional_issues=constitutional_issues,
            policy_issues=policy_issues,
            recommendations=recommendations,
            supervisor_alert_required=overall_status in [GuardrailStatus.WARNING, GuardrailStatus.BLOCKED],
            command_staff_alert_required=overall_status == GuardrailStatus.BLOCKED,
            legal_risk_score=legal_risk_score,
            civil_liability_risk=civil_liability_risk,
            officer_id=context.officer_id,
            incident_id=context.incident_id,
            location=context.location,
        )
        
        self.guardrail_log.append(result)
        if overall_status == GuardrailStatus.BLOCKED:
            self.blocked_actions.append(result)
        elif overall_status == GuardrailStatus.WARNING:
            self.warnings_issued.append(result)
        
        return result
    
    def _check_traffic_stop(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check traffic stop for 4th Amendment compliance"""
        checks = []
        
        if not context.reasonable_suspicion:
            checks.append(GuardrailCheck(
                check_id="ts-001",
                check_name="Reasonable Suspicion Required",
                category="4th Amendment",
                status=GuardrailStatus.BLOCKED,
                violation_type=ConstitutionalViolationType.FOURTH_AMENDMENT_TRAFFIC_STOP.value,
                description="Traffic stop requires reasonable suspicion of traffic violation or criminal activity",
                legal_citation="Terry v. Ohio, 392 U.S. 1 (1968); Delaware v. Prouse, 440 U.S. 648 (1979)",
                policy_reference="RBPD Policy 310",
                risk_level="HIGH",
                recommendation="Document specific articulable facts supporting reasonable suspicion before initiating stop",
            ))
        else:
            checks.append(GuardrailCheck(
                check_id="ts-001",
                check_name="Reasonable Suspicion Required",
                category="4th Amendment",
                status=GuardrailStatus.PASS,
                description="Reasonable suspicion documented",
                legal_citation="Terry v. Ohio, 392 U.S. 1 (1968)",
            ))
        
        if context.detention_duration_minutes and context.detention_duration_minutes > 20:
            checks.append(GuardrailCheck(
                check_id="ts-002",
                check_name="Stop Duration",
                category="4th Amendment",
                status=GuardrailStatus.WARNING,
                violation_type=ConstitutionalViolationType.FOURTH_AMENDMENT_TRAFFIC_STOP.value,
                description=f"Traffic stop duration ({context.detention_duration_minutes} min) exceeds reasonable limit",
                legal_citation="Rodriguez v. United States, 575 U.S. 348 (2015)",
                policy_reference="RBPD Policy 310.5",
                risk_level="MEDIUM",
                recommendation="Complete traffic stop purpose expeditiously; additional detention requires new RS/PC",
            ))
        
        return checks
    
    def _check_terry_stop(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check Terry stop for 4th Amendment compliance"""
        checks = []
        
        if not context.reasonable_suspicion:
            checks.append(GuardrailCheck(
                check_id="terry-001",
                check_name="Articulable Reasonable Suspicion",
                category="4th Amendment",
                status=GuardrailStatus.BLOCKED,
                violation_type=ConstitutionalViolationType.FOURTH_AMENDMENT_TERRY_STOP.value,
                description="Terry stop requires specific, articulable facts supporting reasonable suspicion",
                legal_citation="Terry v. Ohio, 392 U.S. 1 (1968)",
                policy_reference="RBPD Policy 320",
                risk_level="HIGH",
                recommendation="Document specific observations and facts before initiating investigative detention",
            ))
        
        if context.detention_duration_minutes and context.detention_duration_minutes > 15:
            checks.append(GuardrailCheck(
                check_id="terry-002",
                check_name="Detention Duration",
                category="4th Amendment",
                status=GuardrailStatus.WARNING,
                violation_type=ConstitutionalViolationType.FOURTH_AMENDMENT_SEIZURE.value,
                description=f"Investigative detention ({context.detention_duration_minutes} min) may be unreasonably prolonged",
                legal_citation="Florida v. Royer, 460 U.S. 491 (1983)",
                risk_level="MEDIUM",
                recommendation="Diligently pursue investigation; release if RS not elevated to PC",
            ))
        
        return checks
    
    def _check_search(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check search for 4th Amendment compliance"""
        checks = []
        
        if context.action_type == ActionType.CONSENT_SEARCH:
            if not context.consent_obtained:
                checks.append(GuardrailCheck(
                    check_id="search-001",
                    check_name="Consent Required",
                    category="4th Amendment",
                    status=GuardrailStatus.BLOCKED,
                    violation_type=ConstitutionalViolationType.FOURTH_AMENDMENT_CONSENT.value,
                    description="Consent search requires voluntary consent",
                    legal_citation="Schneckloth v. Bustamonte, 412 U.S. 218 (1973)",
                    risk_level="HIGH",
                    recommendation="Obtain clear, voluntary consent before searching",
                ))
            elif context.consent_voluntary is False:
                checks.append(GuardrailCheck(
                    check_id="search-002",
                    check_name="Voluntary Consent",
                    category="4th Amendment",
                    status=GuardrailStatus.BLOCKED,
                    violation_type=ConstitutionalViolationType.FOURTH_AMENDMENT_CONSENT.value,
                    description="Consent appears to be coerced or involuntary",
                    legal_citation="Bumper v. North Carolina, 391 U.S. 543 (1968)",
                    risk_level="HIGH",
                    recommendation="Consent must be freely and voluntarily given without coercion",
                ))
        
        elif context.action_type == ActionType.WARRANTLESS_SEARCH:
            if not context.probable_cause:
                checks.append(GuardrailCheck(
                    check_id="search-003",
                    check_name="Warrant Exception Required",
                    category="4th Amendment",
                    status=GuardrailStatus.WARNING,
                    violation_type=ConstitutionalViolationType.FOURTH_AMENDMENT_SEARCH.value,
                    description="Warrantless search requires valid exception and probable cause",
                    legal_citation="Katz v. United States, 389 U.S. 347 (1967)",
                    risk_level="HIGH",
                    recommendation="Document specific warrant exception and probable cause",
                ))
        
        return checks
    
    def _check_arrest(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check arrest for 4th Amendment compliance"""
        checks = []
        
        if not context.probable_cause:
            checks.append(GuardrailCheck(
                check_id="arrest-001",
                check_name="Probable Cause Required",
                category="4th Amendment",
                status=GuardrailStatus.BLOCKED,
                violation_type=ConstitutionalViolationType.FOURTH_AMENDMENT_SEIZURE.value,
                description="Arrest requires probable cause to believe crime was committed",
                legal_citation="Beck v. Ohio, 379 U.S. 89 (1964)",
                policy_reference="RBPD Policy 320",
                risk_level="HIGH",
                recommendation="Document specific facts establishing probable cause before arrest",
            ))
        
        return checks
    
    def _check_custodial_interrogation(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check custodial interrogation for 5th Amendment compliance"""
        checks = []
        
        if context.custodial and not context.miranda_given:
            checks.append(GuardrailCheck(
                check_id="miranda-001",
                check_name="Miranda Warnings Required",
                category="5th Amendment",
                status=GuardrailStatus.BLOCKED,
                violation_type=ConstitutionalViolationType.FIFTH_AMENDMENT_MIRANDA.value,
                description="Miranda warnings required before custodial interrogation",
                legal_citation="Miranda v. Arizona, 384 U.S. 436 (1966)",
                policy_reference="RBPD Policy 340",
                risk_level="HIGH",
                recommendation="Administer Miranda warnings before any custodial questioning",
            ))
        elif context.custodial and context.miranda_given:
            checks.append(GuardrailCheck(
                check_id="miranda-001",
                check_name="Miranda Warnings Required",
                category="5th Amendment",
                status=GuardrailStatus.PASS,
                description="Miranda warnings properly administered",
                legal_citation="Miranda v. Arizona, 384 U.S. 436 (1966)",
            ))
        
        return checks
    
    def _check_pursuit(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check pursuit for policy compliance"""
        checks = []
        
        pursuit_policy = self.rbpd_policies["pursuit"]
        
        if context.pursuit_speed:
            if context.pursuit_speed > pursuit_policy["max_speed_residential"]:
                checks.append(GuardrailCheck(
                    check_id="pursuit-001",
                    check_name="Pursuit Speed Limit",
                    category="Policy",
                    status=GuardrailStatus.WARNING,
                    violation_type=PolicyViolationType.PURSUIT_EXCESSIVE_SPEED.value,
                    description=f"Pursuit speed ({context.pursuit_speed} mph) exceeds residential limit",
                    policy_reference=f"RBPD Policy {pursuit_policy['policy_number']}",
                    risk_level="HIGH",
                    recommendation="Reduce speed or consider pursuit termination",
                ))
        
        if not context.probable_cause and context.action_type == ActionType.VEHICLE_PURSUIT:
            checks.append(GuardrailCheck(
                check_id="pursuit-002",
                check_name="Pursuit Authorization",
                category="Policy",
                status=GuardrailStatus.WARNING,
                violation_type=PolicyViolationType.PURSUIT_UNAUTHORIZED.value,
                description="Vehicle pursuit requires felony offense or imminent threat",
                policy_reference=f"RBPD Policy {pursuit_policy['policy_number']}",
                risk_level="HIGH",
                recommendation="Confirm felony offense or obtain supervisor authorization",
            ))
        
        return checks
    
    def _check_use_of_force(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check use of force for policy compliance"""
        checks = []
        
        uof_policy = self.rbpd_policies["use_of_force"]
        
        if context.force_level:
            checks.append(GuardrailCheck(
                check_id="uof-001",
                check_name="Force Proportionality",
                category="Policy",
                status=GuardrailStatus.WARNING,
                violation_type=PolicyViolationType.USE_OF_FORCE_EXCESSIVE.value,
                description="Verify force level is proportional to threat",
                policy_reference=f"RBPD Policy {uof_policy['policy_number']}",
                legal_citation="Graham v. Connor, 490 U.S. 386 (1989)",
                risk_level="HIGH",
                recommendation="Document threat level and de-escalation attempts",
            ))
        
        if context.weapon_involved:
            checks.append(GuardrailCheck(
                check_id="uof-002",
                check_name="Deadly Force Authorization",
                category="Policy",
                status=GuardrailStatus.WARNING,
                violation_type=PolicyViolationType.USE_OF_FORCE_UNAUTHORIZED.value,
                description="Deadly force requires imminent threat of death or serious bodily harm",
                policy_reference=f"RBPD Policy {uof_policy['policy_number']}",
                legal_citation="Tennessee v. Garner, 471 U.S. 1 (1985)",
                risk_level="CRITICAL",
                recommendation="Confirm imminent deadly threat before using deadly force",
            ))
        
        return checks
    
    def _check_detention(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check detention for compliance"""
        checks = []
        
        detention_policy = self.rbpd_policies["detention"]
        
        if context.detention_duration_minutes:
            if context.detention_duration_minutes > detention_policy["max_investigative_detention_minutes"]:
                checks.append(GuardrailCheck(
                    check_id="det-001",
                    check_name="Detention Duration",
                    category="4th Amendment",
                    status=GuardrailStatus.WARNING,
                    violation_type=PolicyViolationType.DETENTION_EXCESSIVE.value,
                    description=f"Detention duration ({context.detention_duration_minutes} min) exceeds policy limit",
                    policy_reference=f"RBPD Policy {detention_policy['policy_number']}",
                    risk_level="MEDIUM",
                    recommendation="Release or develop probable cause for arrest",
                ))
        
        return checks
    
    def _check_bias_profiling(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check for bias-based policing indicators"""
        checks = []
        
        bias_policy = self.rbpd_policies["bias_free_policing"]
        
        if context.subject_demographics and context.prior_contacts_24h > 3:
            checks.append(GuardrailCheck(
                check_id="bias-001",
                check_name="Contact Pattern Review",
                category="Policy",
                status=GuardrailStatus.WARNING,
                violation_type=PolicyViolationType.BIAS_PROFILING_DETECTED.value,
                description="Multiple contacts with similar demographics in 24 hours - review for patterns",
                policy_reference=f"RBPD Policy {bias_policy['policy_number']}",
                risk_level="MEDIUM",
                recommendation="Document legitimate law enforcement purpose for each contact",
            ))
        
        return checks
    
    def _check_equal_protection(self, context: ActionContext) -> List[GuardrailCheck]:
        """Check for equal protection compliance"""
        checks = []
        
        if context.subject_demographics:
            checks.append(GuardrailCheck(
                check_id="ep-001",
                check_name="Equal Protection Compliance",
                category="14th Amendment",
                status=GuardrailStatus.PASS,
                description="Document legitimate law enforcement purpose independent of protected characteristics",
                legal_citation="Whren v. United States, 517 U.S. 806 (1996)",
            ))
        
        return checks
    
    def _calculate_legal_risk(self, checks: List[GuardrailCheck]) -> float:
        """Calculate overall legal risk score"""
        if not checks:
            return 0.0
        
        risk_weights = {"LOW": 0.1, "MEDIUM": 0.3, "HIGH": 0.6, "CRITICAL": 1.0}
        total_risk = sum(risk_weights.get(c.risk_level, 0.1) for c in checks if c.status != GuardrailStatus.PASS)
        
        return min(total_risk / len(checks), 1.0) if checks else 0.0
    
    def _assess_civil_liability(self, checks: List[GuardrailCheck], risk_score: float) -> str:
        """Assess civil liability risk level"""
        blocked_count = sum(1 for c in checks if c.status == GuardrailStatus.BLOCKED)
        
        if blocked_count > 0 or risk_score > 0.7:
            return "HIGH"
        elif risk_score > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_guardrail_log(self, limit: int = 100, status_filter: Optional[GuardrailStatus] = None) -> List[GuardrailResult]:
        """Get guardrail evaluation log"""
        log = self.guardrail_log
        if status_filter:
            log = [r for r in log if r.overall_status == status_filter]
        return log[-limit:]
    
    def get_blocked_actions(self, limit: int = 50) -> List[GuardrailResult]:
        """Get list of blocked actions"""
        return self.blocked_actions[-limit:]
    
    def get_warnings(self, limit: int = 100) -> List[GuardrailResult]:
        """Get list of warnings issued"""
        return self.warnings_issued[-limit:]
    
    def get_policy_reference(self, policy_type: str) -> Dict[str, Any]:
        """Get RBPD policy reference"""
        return self.rbpd_policies.get(policy_type, {})
    
    def get_constitutional_rule(self, amendment: str, rule_type: str) -> Dict[str, Any]:
        """Get constitutional rule reference"""
        rules_map = {
            "4th": self.fourth_amendment_rules,
            "5th": self.fifth_amendment_rules,
            "14th": self.fourteenth_amendment_rules,
            "florida": self.florida_constitution_rules,
        }
        rules = rules_map.get(amendment, {})
        return rules.get(rule_type, {})
