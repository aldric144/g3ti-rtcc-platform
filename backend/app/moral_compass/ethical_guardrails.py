"""
Ethical Safeguards Module

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Safeguards against harmful actions and ensures ethical compliance.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class GuardrailType(Enum):
    """Types of ethical guardrails."""
    CONSTITUTIONAL = "constitutional"
    POLICY = "policy"
    ETHICAL = "ethical"
    YOUTH_PROTECTION = "youth_protection"
    VULNERABLE_POPULATION = "vulnerable_population"
    USE_OF_FORCE = "use_of_force"
    DISCRIMINATION = "discrimination"
    BIAS_PREVENTION = "bias_prevention"
    PRIVACY = "privacy"
    TRANSPARENCY = "transparency"


class ProtectionCategory(Enum):
    """Categories of protection."""
    MINORS = "minors"
    ELDERLY = "elderly"
    DISABLED = "disabled"
    MENTAL_HEALTH = "mental_health"
    HOMELESS = "homeless"
    DOMESTIC_VIOLENCE = "domestic_violence"
    IMMIGRANTS = "immigrants"
    LOW_INCOME = "low_income"
    GENERAL_PUBLIC = "general_public"


class ViolationSeverity(Enum):
    """Severity levels for violations."""
    INFO = "info"
    WARNING = "warning"
    SERIOUS = "serious"
    CRITICAL = "critical"
    BLOCKING = "blocking"


@dataclass
class GuardrailRule:
    """Definition of a guardrail rule."""
    rule_id: str = ""
    name: str = ""
    description: str = ""
    guardrail_type: GuardrailType = GuardrailType.ETHICAL
    protection_categories: List[ProtectionCategory] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    action_on_violation: str = "block"
    severity: ViolationSeverity = ViolationSeverity.SERIOUS
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "guardrail_type": self.guardrail_type.value,
            "protection_categories": [p.value for p in self.protection_categories],
            "triggers": self.triggers,
            "conditions": self.conditions,
            "action_on_violation": self.action_on_violation,
            "severity": self.severity.value,
        }


@dataclass
class GuardrailCheck:
    """Result of a guardrail check."""
    check_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    rule_id: str = ""
    rule_name: str = ""
    guardrail_type: GuardrailType = GuardrailType.ETHICAL
    passed: bool = True
    details: str = ""
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "guardrail_type": self.guardrail_type.value,
            "passed": self.passed,
            "details": self.details,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class GuardrailViolation:
    """Record of a guardrail violation."""
    violation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    rule_name: str = ""
    guardrail_type: GuardrailType = GuardrailType.ETHICAL
    severity: ViolationSeverity = ViolationSeverity.SERIOUS
    action_type: str = ""
    action_description: str = ""
    requester_id: str = ""
    details: str = ""
    blocked: bool = False
    remediation_required: bool = True
    remediation_steps: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    violation_hash: str = ""
    
    def __post_init__(self):
        if not self.violation_hash:
            self.violation_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        content = f"{self.violation_id}:{self.rule_id}:{self.action_type}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "guardrail_type": self.guardrail_type.value,
            "severity": self.severity.value,
            "action_type": self.action_type,
            "action_description": self.action_description,
            "requester_id": self.requester_id,
            "details": self.details,
            "blocked": self.blocked,
            "remediation_required": self.remediation_required,
            "remediation_steps": self.remediation_steps,
            "created_at": self.created_at.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "violation_hash": self.violation_hash,
        }


@dataclass
class GuardrailAssessment:
    """Complete guardrail assessment result."""
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = ""
    requester_id: str = ""
    checks: List[GuardrailCheck] = field(default_factory=list)
    violations: List[GuardrailViolation] = field(default_factory=list)
    passed: bool = True
    blocked: bool = False
    requires_review: bool = False
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    assessment_hash: str = ""
    
    def __post_init__(self):
        if not self.assessment_hash:
            self.assessment_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        content = f"{self.assessment_id}:{self.action_type}:{len(self.violations)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "action_type": self.action_type,
            "requester_id": self.requester_id,
            "checks": [c.to_dict() for c in self.checks],
            "violations": [v.to_dict() for v in self.violations],
            "passed": self.passed,
            "blocked": self.blocked,
            "requires_review": self.requires_review,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
            "assessment_hash": self.assessment_hash,
        }


class EthicalGuardrails:
    """
    Ethical Safeguards Module.
    
    Provides guardrails against harmful actions, discrimination,
    and ensures protection for vulnerable populations.
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
        self.rules: Dict[str, GuardrailRule] = {}
        self.violations: Dict[str, GuardrailViolation] = {}
        self.assessments: Dict[str, GuardrailAssessment] = {}
        self.statistics = {
            "total_checks": 0,
            "passed": 0,
            "violations": 0,
            "blocked": 0,
        }
        
        self._initialize_rules()
    
    def _initialize_rules(self) -> None:
        """Initialize default guardrail rules."""
        default_rules = [
            GuardrailRule(
                rule_id="CONST-4A",
                name="Fourth Amendment Protection",
                description="Prevent warrantless searches and seizures",
                guardrail_type=GuardrailType.CONSTITUTIONAL,
                protection_categories=[ProtectionCategory.GENERAL_PUBLIC],
                triggers=["search", "seizure", "surveillance", "tracking", "monitoring"],
                conditions=["warrant_required", "probable_cause_required"],
                action_on_violation="block",
                severity=ViolationSeverity.BLOCKING,
            ),
            GuardrailRule(
                rule_id="CONST-5A",
                name="Fifth Amendment Protection",
                description="Ensure due process and self-incrimination protection",
                guardrail_type=GuardrailType.CONSTITUTIONAL,
                protection_categories=[ProtectionCategory.GENERAL_PUBLIC],
                triggers=["interrogation", "questioning", "detention", "arrest"],
                conditions=["miranda_required", "due_process_required"],
                action_on_violation="block",
                severity=ViolationSeverity.BLOCKING,
            ),
            GuardrailRule(
                rule_id="CONST-14A",
                name="Fourteenth Amendment Protection",
                description="Ensure equal protection under the law",
                guardrail_type=GuardrailType.CONSTITUTIONAL,
                protection_categories=[ProtectionCategory.GENERAL_PUBLIC],
                triggers=["profiling", "targeting", "discrimination", "bias"],
                conditions=["equal_treatment_required"],
                action_on_violation="block",
                severity=ViolationSeverity.BLOCKING,
            ),
            GuardrailRule(
                rule_id="YOUTH-001",
                name="Youth Protection",
                description="Special protections for minors",
                guardrail_type=GuardrailType.YOUTH_PROTECTION,
                protection_categories=[ProtectionCategory.MINORS],
                triggers=["minor", "juvenile", "youth", "child", "teen"],
                conditions=["guardian_notification", "specialized_handling"],
                action_on_violation="require_approval",
                severity=ViolationSeverity.CRITICAL,
            ),
            GuardrailRule(
                rule_id="VULN-001",
                name="Elderly Protection",
                description="Special protections for elderly individuals",
                guardrail_type=GuardrailType.VULNERABLE_POPULATION,
                protection_categories=[ProtectionCategory.ELDERLY],
                triggers=["elderly", "senior", "aged"],
                conditions=["specialized_response", "dignity_preservation"],
                action_on_violation="require_approval",
                severity=ViolationSeverity.SERIOUS,
            ),
            GuardrailRule(
                rule_id="VULN-002",
                name="Mental Health Protection",
                description="Special protections for individuals in mental health crisis",
                guardrail_type=GuardrailType.VULNERABLE_POPULATION,
                protection_categories=[ProtectionCategory.MENTAL_HEALTH],
                triggers=["mental_health", "crisis", "suicide", "psychiatric", "emotional_distress"],
                conditions=["crisis_intervention", "mental_health_professional"],
                action_on_violation="require_approval",
                severity=ViolationSeverity.CRITICAL,
            ),
            GuardrailRule(
                rule_id="VULN-003",
                name="Domestic Violence Protection",
                description="Special protections for domestic violence situations",
                guardrail_type=GuardrailType.VULNERABLE_POPULATION,
                protection_categories=[ProtectionCategory.DOMESTIC_VIOLENCE],
                triggers=["domestic", "abuse", "violence", "intimate_partner"],
                conditions=["victim_safety_priority", "specialized_unit"],
                action_on_violation="require_approval",
                severity=ViolationSeverity.CRITICAL,
            ),
            GuardrailRule(
                rule_id="VULN-004",
                name="Homeless Population Protection",
                description="Special protections for homeless individuals",
                guardrail_type=GuardrailType.VULNERABLE_POPULATION,
                protection_categories=[ProtectionCategory.HOMELESS],
                triggers=["homeless", "unhoused", "transient"],
                conditions=["dignity_preservation", "social_services_referral"],
                action_on_violation="warn",
                severity=ViolationSeverity.SERIOUS,
            ),
            GuardrailRule(
                rule_id="FORCE-001",
                name="Use of Force Guidelines",
                description="Ensure proportional and necessary use of force",
                guardrail_type=GuardrailType.USE_OF_FORCE,
                protection_categories=[ProtectionCategory.GENERAL_PUBLIC],
                triggers=["force", "restraint", "weapon", "taser", "firearm"],
                conditions=["proportionality", "necessity", "de_escalation_attempted"],
                action_on_violation="block",
                severity=ViolationSeverity.BLOCKING,
            ),
            GuardrailRule(
                rule_id="DISC-001",
                name="Anti-Discrimination",
                description="Prevent discrimination based on protected characteristics",
                guardrail_type=GuardrailType.DISCRIMINATION,
                protection_categories=[ProtectionCategory.GENERAL_PUBLIC],
                triggers=["race", "ethnicity", "religion", "gender", "orientation", "disability"],
                conditions=["no_profiling", "equal_treatment"],
                action_on_violation="block",
                severity=ViolationSeverity.BLOCKING,
            ),
            GuardrailRule(
                rule_id="BIAS-001",
                name="Bias Prevention",
                description="Prevent reinforcement of biased patterns",
                guardrail_type=GuardrailType.BIAS_PREVENTION,
                protection_categories=[ProtectionCategory.GENERAL_PUBLIC],
                triggers=["prediction", "targeting", "pattern", "algorithm"],
                conditions=["bias_audit", "fairness_check"],
                action_on_violation="require_review",
                severity=ViolationSeverity.SERIOUS,
            ),
            GuardrailRule(
                rule_id="PRIV-001",
                name="Privacy Protection",
                description="Protect individual privacy rights",
                guardrail_type=GuardrailType.PRIVACY,
                protection_categories=[ProtectionCategory.GENERAL_PUBLIC],
                triggers=["surveillance", "data_collection", "tracking", "monitoring"],
                conditions=["data_minimization", "purpose_limitation"],
                action_on_violation="require_approval",
                severity=ViolationSeverity.SERIOUS,
            ),
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
    
    def check_action(
        self,
        action_type: str,
        action_description: str,
        requester_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> GuardrailAssessment:
        """
        Check an action against all guardrails.
        
        Args:
            action_type: Type of action
            action_description: Description of the action
            requester_id: ID of requester
            context: Additional context
        
        Returns:
            GuardrailAssessment with all checks and violations
        """
        context = context or {}
        
        assessment = GuardrailAssessment(
            action_type=action_type,
            requester_id=requester_id,
        )
        
        for rule_id, rule in self.rules.items():
            check = self._check_rule(rule, action_type, action_description, context)
            assessment.checks.append(check)
            
            if not check.passed:
                violation = self._create_violation(
                    rule, action_type, action_description, requester_id, check.details
                )
                assessment.violations.append(violation)
                self.violations[violation.violation_id] = violation
                
                if rule.severity == ViolationSeverity.BLOCKING:
                    assessment.blocked = True
                elif rule.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.SERIOUS]:
                    assessment.requires_review = True
        
        assessment.passed = len(assessment.violations) == 0
        assessment.recommendations = self._generate_recommendations(assessment)
        assessment.assessment_hash = assessment._compute_hash()
        
        self.assessments[assessment.assessment_id] = assessment
        self._update_statistics(assessment)
        
        return assessment
    
    def _check_rule(
        self,
        rule: GuardrailRule,
        action_type: str,
        action_description: str,
        context: Dict[str, Any],
    ) -> GuardrailCheck:
        """Check a single rule against the action."""
        check = GuardrailCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            guardrail_type=rule.guardrail_type,
        )
        
        triggered = any(
            trigger in action_type.lower() or trigger in action_description.lower()
            for trigger in rule.triggers
        )
        
        if not triggered:
            check.passed = True
            check.details = "Rule not triggered"
            return check
        
        missing_conditions = []
        for condition in rule.conditions:
            if not context.get(condition, False):
                if not context.get(f"override_{condition}", False):
                    missing_conditions.append(condition)
        
        if missing_conditions:
            check.passed = False
            check.details = f"Missing conditions: {', '.join(missing_conditions)}"
            check.recommendations = [
                f"Ensure {cond} is satisfied" for cond in missing_conditions
            ]
        else:
            check.passed = True
            check.details = "All conditions satisfied"
        
        return check
    
    def _create_violation(
        self,
        rule: GuardrailRule,
        action_type: str,
        action_description: str,
        requester_id: str,
        details: str,
    ) -> GuardrailViolation:
        """Create a violation record."""
        remediation_steps = []
        
        if rule.guardrail_type == GuardrailType.CONSTITUTIONAL:
            remediation_steps = [
                "Obtain proper legal authorization",
                "Consult with legal counsel",
                "Document justification",
            ]
        elif rule.guardrail_type == GuardrailType.YOUTH_PROTECTION:
            remediation_steps = [
                "Contact guardian/parent",
                "Engage juvenile specialist",
                "Follow juvenile procedures",
            ]
        elif rule.guardrail_type == GuardrailType.VULNERABLE_POPULATION:
            remediation_steps = [
                "Engage specialized unit",
                "Ensure appropriate support services",
                "Document special handling",
            ]
        elif rule.guardrail_type == GuardrailType.USE_OF_FORCE:
            remediation_steps = [
                "Attempt de-escalation",
                "Use minimum necessary force",
                "Document all actions",
                "Obtain supervisor approval",
            ]
        elif rule.guardrail_type == GuardrailType.DISCRIMINATION:
            remediation_steps = [
                "Review action for bias",
                "Ensure equal treatment",
                "Document non-discriminatory basis",
            ]
        else:
            remediation_steps = [
                "Review action against policy",
                "Obtain appropriate approval",
                "Document justification",
            ]
        
        return GuardrailViolation(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            guardrail_type=rule.guardrail_type,
            severity=rule.severity,
            action_type=action_type,
            action_description=action_description,
            requester_id=requester_id,
            details=details,
            blocked=rule.severity == ViolationSeverity.BLOCKING,
            remediation_required=rule.severity in [ViolationSeverity.BLOCKING, ViolationSeverity.CRITICAL],
            remediation_steps=remediation_steps,
        )
    
    def _generate_recommendations(self, assessment: GuardrailAssessment) -> List[str]:
        """Generate recommendations based on assessment."""
        recommendations = []
        
        if assessment.blocked:
            recommendations.append("Action blocked - obtain proper authorization before proceeding")
        
        if assessment.requires_review:
            recommendations.append("Action requires supervisor review before proceeding")
        
        for violation in assessment.violations:
            recommendations.extend(violation.remediation_steps[:2])
        
        return list(set(recommendations))
    
    def _update_statistics(self, assessment: GuardrailAssessment) -> None:
        """Update statistics."""
        self.statistics["total_checks"] += len(assessment.checks)
        self.statistics["passed"] += sum(1 for c in assessment.checks if c.passed)
        self.statistics["violations"] += len(assessment.violations)
        if assessment.blocked:
            self.statistics["blocked"] += 1
    
    def detect_harmful_intent(
        self,
        action_type: str,
        action_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Detect potential harmful intent in an action.
        
        Args:
            action_type: Type of action
            action_description: Description
            context: Additional context
        
        Returns:
            Dict with harmful intent analysis
        """
        context = context or {}
        
        harmful_indicators = []
        harm_score = 0.0
        
        harmful_keywords = [
            "force", "weapon", "harm", "injure", "damage",
            "target", "profile", "discriminate", "bias",
        ]
        
        for keyword in harmful_keywords:
            if keyword in action_type.lower() or keyword in action_description.lower():
                harmful_indicators.append(keyword)
                harm_score += 0.15
        
        if context.get("involves_minor", False):
            harmful_indicators.append("involves_minor")
            harm_score += 0.2
        
        if context.get("vulnerable_population", False):
            harmful_indicators.append("vulnerable_population")
            harm_score += 0.15
        
        if context.get("no_justification", False):
            harmful_indicators.append("no_justification")
            harm_score += 0.25
        
        return {
            "harmful_intent_detected": harm_score > 0.3,
            "harm_score": min(1.0, harm_score),
            "indicators": harmful_indicators,
            "recommendation": "Review action carefully" if harm_score > 0.3 else "Proceed with caution",
        }
    
    def flag_discrimination(
        self,
        action_type: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Flag potential discrimination in an action.
        
        Args:
            action_type: Type of action
            context: Context including demographic info
        
        Returns:
            Dict with discrimination analysis
        """
        discrimination_flags = []
        
        protected_characteristics = [
            "race", "ethnicity", "religion", "gender",
            "sexual_orientation", "disability", "national_origin", "age",
        ]
        
        for characteristic in protected_characteristics:
            if context.get(f"based_on_{characteristic}", False):
                discrimination_flags.append(characteristic)
        
        if context.get("disproportionate_impact", False):
            discrimination_flags.append("disproportionate_impact")
        
        if context.get("no_legitimate_basis", False):
            discrimination_flags.append("no_legitimate_basis")
        
        return {
            "discrimination_detected": len(discrimination_flags) > 0,
            "flags": discrimination_flags,
            "severity": "critical" if len(discrimination_flags) > 1 else "serious" if discrimination_flags else "none",
            "action_required": "Block and review" if discrimination_flags else "None",
        }
    
    def validate_use_of_force(
        self,
        force_level: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate use of force recommendation.
        
        Args:
            force_level: Level of force proposed
            context: Situational context
        
        Returns:
            Dict with validation result
        """
        force_levels = ["verbal", "presence", "soft_hands", "hard_hands", "intermediate", "deadly"]
        
        if force_level not in force_levels:
            force_level = "unknown"
        
        issues = []
        approved = True
        
        if not context.get("de_escalation_attempted", False):
            issues.append("De-escalation not attempted")
            if force_level in ["hard_hands", "intermediate", "deadly"]:
                approved = False
        
        if not context.get("proportional_to_threat", False):
            issues.append("Force may not be proportional to threat")
            approved = False
        
        if not context.get("necessary", False):
            issues.append("Necessity not established")
            approved = False
        
        if context.get("involves_minor", False) and force_level in ["intermediate", "deadly"]:
            issues.append("High force level against minor")
            approved = False
        
        if context.get("mental_health_crisis", False) and force_level in ["hard_hands", "intermediate", "deadly"]:
            issues.append("High force level in mental health crisis")
            approved = False
        
        return {
            "force_level": force_level,
            "approved": approved,
            "issues": issues,
            "recommendations": [
                "Attempt de-escalation first",
                "Use minimum necessary force",
                "Document all actions",
            ] if not approved else [],
            "requires_supervisor": force_level in ["intermediate", "deadly"] or not approved,
        }
    
    def enforce_youth_protection(
        self,
        action_type: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Enforce youth protection rules.
        
        Args:
            action_type: Type of action
            context: Context including youth info
        
        Returns:
            Dict with youth protection requirements
        """
        requirements = []
        blocked = False
        
        if context.get("involves_minor", False):
            requirements.append("Guardian/parent notification required")
            requirements.append("Juvenile specialist involvement recommended")
            requirements.append("Age-appropriate communication required")
            
            if action_type in ["arrest", "detention", "interrogation"]:
                requirements.append("Juvenile procedures must be followed")
                requirements.append("Separate from adult detainees")
            
            if action_type in ["force", "restraint"]:
                requirements.append("Minimal force only")
                requirements.append("Immediate supervisor notification")
            
            if context.get("age", 18) < 13:
                requirements.append("Enhanced protections for child under 13")
                if action_type in ["interrogation", "detention"]:
                    blocked = True
        
        return {
            "youth_protection_active": context.get("involves_minor", False),
            "requirements": requirements,
            "blocked": blocked,
            "specialized_handling": True if requirements else False,
        }
    
    def enforce_vulnerable_population_rules(
        self,
        action_type: str,
        population_type: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Enforce vulnerable population protection rules.
        
        Args:
            action_type: Type of action
            population_type: Type of vulnerable population
            context: Additional context
        
        Returns:
            Dict with protection requirements
        """
        requirements = []
        specialized_unit = False
        
        if population_type == "mental_health":
            requirements.append("Crisis intervention team recommended")
            requirements.append("Mental health professional involvement")
            requirements.append("De-escalation priority")
            specialized_unit = True
        
        elif population_type == "elderly":
            requirements.append("Patient and respectful communication")
            requirements.append("Consider physical limitations")
            requirements.append("Family notification if appropriate")
        
        elif population_type == "disabled":
            requirements.append("Accommodate disability needs")
            requirements.append("Ensure effective communication")
            requirements.append("ADA compliance required")
        
        elif population_type == "domestic_violence":
            requirements.append("Victim safety is priority")
            requirements.append("Domestic violence unit involvement")
            requirements.append("Safety planning required")
            specialized_unit = True
        
        elif population_type == "homeless":
            requirements.append("Dignity preservation")
            requirements.append("Social services referral")
            requirements.append("Avoid criminalization of homelessness")
        
        return {
            "population_type": population_type,
            "requirements": requirements,
            "specialized_unit_required": specialized_unit,
            "enhanced_documentation": True,
        }
    
    def prevent_bias_reinforcement(
        self,
        action_type: str,
        historical_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Prevent reinforcement of biased patterns.
        
        Args:
            action_type: Type of action
            historical_data: Historical pattern data
        
        Returns:
            Dict with bias prevention analysis
        """
        historical_data = historical_data or {}
        
        bias_risks = []
        
        if historical_data.get("geographic_concentration", False):
            bias_risks.append("Geographic concentration may indicate bias")
        
        if historical_data.get("demographic_disparity", False):
            bias_risks.append("Demographic disparity detected in historical data")
        
        if historical_data.get("pattern_based_targeting", False):
            bias_risks.append("Pattern-based targeting may reinforce bias")
        
        if action_type in ["predictive_targeting", "risk_scoring", "pattern_analysis"]:
            bias_risks.append("Action type has inherent bias risk")
        
        return {
            "bias_risks": bias_risks,
            "risk_level": "high" if len(bias_risks) > 2 else "medium" if bias_risks else "low",
            "mitigation_required": len(bias_risks) > 0,
            "recommendations": [
                "Review for disparate impact",
                "Ensure evidence-based justification",
                "Document non-discriminatory basis",
            ] if bias_risks else [],
        }
    
    def get_violation(self, violation_id: str) -> Optional[GuardrailViolation]:
        """Get violation by ID."""
        return self.violations.get(violation_id)
    
    def get_active_violations(self) -> List[GuardrailViolation]:
        """Get all unresolved violations."""
        return [v for v in self.violations.values() if not v.resolved]
    
    def resolve_violation(
        self,
        violation_id: str,
        resolved_by: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Resolve a violation."""
        violation = self.violations.get(violation_id)
        if not violation:
            return False
        
        violation.resolved = True
        violation.resolved_at = datetime.utcnow()
        violation.resolved_by = resolved_by
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get guardrail statistics."""
        return {
            **self.statistics,
            "active_violations": len(self.get_active_violations()),
            "total_rules": len(self.rules),
        }
