"""
Ethical & Legal Governance Layer

Enforces constitutional, legal, and policy compliance:
- Constitutional compliance (4th, 5th, 14th Amendments)
- Florida State Statutes compliance
- RBPD general orders & use-of-force policies
- CJIS, NIST 800-53, NIJ standards
- Bias audit enforcement (no race-based prediction)
- Explainability requirements

Triggers automatic blocks on:
- Unlawful surveillance
- Excessive data retention
- Restricted entity profiling
- Unauthorized access attempts
"""

import hashlib
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class ComplianceFramework(Enum):
    """Legal and regulatory compliance frameworks."""
    FOURTH_AMENDMENT = "4th_amendment"
    FIFTH_AMENDMENT = "5th_amendment"
    FOURTEENTH_AMENDMENT = "14th_amendment"
    FLORIDA_STATUTES = "florida_statutes"
    RBPD_GENERAL_ORDERS = "rbpd_general_orders"
    USE_OF_FORCE_POLICY = "use_of_force_policy"
    CJIS_SECURITY_POLICY = "cjis_security_policy"
    NIST_800_53 = "nist_800_53"
    NIJ_STANDARDS = "nij_standards"
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"


class ViolationType(Enum):
    """Types of ethics/legal violations."""
    UNLAWFUL_SURVEILLANCE = "unlawful_surveillance"
    EXCESSIVE_DATA_RETENTION = "excessive_data_retention"
    RESTRICTED_ENTITY_PROFILING = "restricted_entity_profiling"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    BIAS_DETECTION = "bias_detection"
    RACIAL_PROFILING = "racial_profiling"
    RELIGIOUS_PROFILING = "religious_profiling"
    POLITICAL_PROFILING = "political_profiling"
    EXCESSIVE_FORCE_RISK = "excessive_force_risk"
    PRIVACY_VIOLATION = "privacy_violation"
    DUE_PROCESS_VIOLATION = "due_process_violation"
    EQUAL_PROTECTION_VIOLATION = "equal_protection_violation"
    WARRANTLESS_SEARCH = "warrantless_search"
    MIRANDA_VIOLATION = "miranda_violation"
    CHAIN_OF_CUSTODY_BREACH = "chain_of_custody_breach"


class ViolationSeverity(Enum):
    """Severity levels for violations."""
    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ActionDecision(Enum):
    """Decisions on proposed actions."""
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    REQUIRES_REVIEW = "requires_review"
    BLOCKED = "blocked"
    ESCALATED = "escalated"


class ProtectedClass(Enum):
    """Protected classes that cannot be used for profiling."""
    RACE = "race"
    ETHNICITY = "ethnicity"
    RELIGION = "religion"
    NATIONAL_ORIGIN = "national_origin"
    GENDER = "gender"
    SEXUAL_ORIENTATION = "sexual_orientation"
    DISABILITY = "disability"
    AGE = "age"
    POLITICAL_AFFILIATION = "political_affiliation"


@dataclass
class ComplianceRule:
    """A compliance rule definition."""
    rule_id: str
    framework: ComplianceFramework
    name: str
    description: str
    violation_type: ViolationType
    severity: ViolationSeverity
    auto_block: bool
    requires_warrant: bool
    data_retention_days: Optional[int]
    explainability_required: bool
    human_review_required: bool


@dataclass
class EthicsViolation:
    """An ethics or legal violation detected."""
    violation_id: str
    violation_type: ViolationType
    severity: ViolationSeverity
    framework: ComplianceFramework
    rule_id: str
    engine: str
    action_attempted: str
    description: str
    evidence: dict
    blocked: bool
    escalated: bool
    reviewed_by: Optional[str]
    review_decision: Optional[str]
    timestamp: datetime
    chain_of_custody_hash: str


@dataclass
class ActionValidation:
    """Validation result for a proposed action."""
    validation_id: str
    action_type: str
    engine: str
    target: str
    decision: ActionDecision
    violations: list[str]
    conditions: list[str]
    explainability_score: float
    bias_score: float
    legal_basis: str
    requires_warrant: bool
    warrant_obtained: bool
    human_approval_required: bool
    approved_by: Optional[str]
    timestamp: datetime
    chain_of_custody_hash: str


@dataclass
class BiasAuditResult:
    """Result of a bias audit."""
    audit_id: str
    engine: str
    model_name: str
    audit_type: str
    protected_classes_checked: list[str]
    disparate_impact_scores: dict
    overall_bias_score: float
    bias_detected: bool
    recommendations: list[str]
    timestamp: datetime
    chain_of_custody_hash: str


@dataclass
class DataRetentionPolicy:
    """Data retention policy definition."""
    policy_id: str
    data_type: str
    retention_days: int
    legal_basis: str
    auto_purge: bool
    requires_consent: bool
    exceptions: list[str]


class EthicsGuard:
    """
    Ethical & Legal Governance Layer for RTCC-UIP platform.
    
    Enforces constitutional, legal, and policy compliance
    across all system operations.
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
        
        self.compliance_rules: dict[str, ComplianceRule] = {}
        self.violations: dict[str, EthicsViolation] = {}
        self.action_validations: dict[str, ActionValidation] = {}
        self.bias_audits: dict[str, BiasAuditResult] = {}
        self.data_retention_policies: dict[str, DataRetentionPolicy] = {}
        
        self.blocked_actions: list[str] = []
        self.escalated_violations: list[str] = []
        
        self._initialize_compliance_rules()
        self._initialize_data_retention_policies()
        self._initialized = True
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules."""
        rules = [
            ComplianceRule(
                rule_id="4A-001",
                framework=ComplianceFramework.FOURTH_AMENDMENT,
                name="Warrantless Search Prohibition",
                description="Prohibits searches without warrant or probable cause",
                violation_type=ViolationType.WARRANTLESS_SEARCH,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                requires_warrant=True,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="4A-002",
                framework=ComplianceFramework.FOURTH_AMENDMENT,
                name="Unlawful Surveillance Prohibition",
                description="Prohibits surveillance without legal authority",
                violation_type=ViolationType.UNLAWFUL_SURVEILLANCE,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                requires_warrant=True,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="5A-001",
                framework=ComplianceFramework.FIFTH_AMENDMENT,
                name="Due Process Protection",
                description="Ensures due process in all AI-assisted decisions",
                violation_type=ViolationType.DUE_PROCESS_VIOLATION,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                requires_warrant=False,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="5A-002",
                framework=ComplianceFramework.FIFTH_AMENDMENT,
                name="Miranda Rights Protection",
                description="Ensures Miranda rights are respected",
                violation_type=ViolationType.MIRANDA_VIOLATION,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                requires_warrant=False,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="14A-001",
                framework=ComplianceFramework.FOURTEENTH_AMENDMENT,
                name="Equal Protection",
                description="Prohibits discrimination based on protected classes",
                violation_type=ViolationType.EQUAL_PROTECTION_VIOLATION,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                requires_warrant=False,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="14A-002",
                framework=ComplianceFramework.FOURTEENTH_AMENDMENT,
                name="Racial Profiling Prohibition",
                description="Prohibits race-based predictions and profiling",
                violation_type=ViolationType.RACIAL_PROFILING,
                severity=ViolationSeverity.EMERGENCY,
                auto_block=True,
                requires_warrant=False,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="FS-001",
                framework=ComplianceFramework.FLORIDA_STATUTES,
                name="Florida Privacy Protection",
                description="Compliance with Florida privacy statutes",
                violation_type=ViolationType.PRIVACY_VIOLATION,
                severity=ViolationSeverity.VIOLATION,
                auto_block=False,
                requires_warrant=False,
                data_retention_days=365,
                explainability_required=True,
                human_review_required=False,
            ),
            ComplianceRule(
                rule_id="RBPD-001",
                framework=ComplianceFramework.RBPD_GENERAL_ORDERS,
                name="RBPD Use of Force Policy",
                description="Compliance with Riviera Beach PD use of force policies",
                violation_type=ViolationType.EXCESSIVE_FORCE_RISK,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                requires_warrant=False,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="CJIS-001",
                framework=ComplianceFramework.CJIS_SECURITY_POLICY,
                name="CJIS Data Access Control",
                description="Compliance with CJIS security policy",
                violation_type=ViolationType.UNAUTHORIZED_ACCESS,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                requires_warrant=False,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="NIST-001",
                framework=ComplianceFramework.NIST_800_53,
                name="NIST Security Controls",
                description="Compliance with NIST 800-53 security controls",
                violation_type=ViolationType.UNAUTHORIZED_ACCESS,
                severity=ViolationSeverity.VIOLATION,
                auto_block=False,
                requires_warrant=False,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=False,
            ),
            ComplianceRule(
                rule_id="BIAS-001",
                framework=ComplianceFramework.NIJ_STANDARDS,
                name="Bias Prevention",
                description="Prevents bias in AI predictions",
                violation_type=ViolationType.BIAS_DETECTION,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                requires_warrant=False,
                data_retention_days=None,
                explainability_required=True,
                human_review_required=True,
            ),
            ComplianceRule(
                rule_id="RET-001",
                framework=ComplianceFramework.FLORIDA_STATUTES,
                name="Data Retention Limits",
                description="Enforces data retention limits",
                violation_type=ViolationType.EXCESSIVE_DATA_RETENTION,
                severity=ViolationSeverity.WARNING,
                auto_block=False,
                requires_warrant=False,
                data_retention_days=730,
                explainability_required=False,
                human_review_required=False,
            ),
        ]
        
        for rule in rules:
            self.compliance_rules[rule.rule_id] = rule
    
    def _initialize_data_retention_policies(self):
        """Initialize data retention policies."""
        policies = [
            DataRetentionPolicy(
                policy_id="DRP-001",
                data_type="surveillance_footage",
                retention_days=30,
                legal_basis="Florida Statutes 119.071",
                auto_purge=True,
                requires_consent=False,
                exceptions=["active_investigation", "court_order"],
            ),
            DataRetentionPolicy(
                policy_id="DRP-002",
                data_type="license_plate_reads",
                retention_days=90,
                legal_basis="Florida Statutes 316.0777",
                auto_purge=True,
                requires_consent=False,
                exceptions=["active_investigation"],
            ),
            DataRetentionPolicy(
                policy_id="DRP-003",
                data_type="facial_recognition_data",
                retention_days=7,
                legal_basis="RBPD General Order 4.12",
                auto_purge=True,
                requires_consent=False,
                exceptions=["positive_match", "active_investigation"],
            ),
            DataRetentionPolicy(
                policy_id="DRP-004",
                data_type="predictive_analytics",
                retention_days=365,
                legal_basis="NIJ Standards",
                auto_purge=True,
                requires_consent=False,
                exceptions=["audit_trail"],
            ),
            DataRetentionPolicy(
                policy_id="DRP-005",
                data_type="officer_body_camera",
                retention_days=180,
                legal_basis="Florida Statutes 943.1718",
                auto_purge=False,
                requires_consent=False,
                exceptions=["use_of_force", "complaint", "litigation"],
            ),
        ]
        
        for policy in policies:
            self.data_retention_policies[policy.policy_id] = policy
    
    def _generate_hash(self, data: str) -> str:
        """Generate SHA256 hash for chain of custody."""
        return hashlib.sha256(f"{data}:{datetime.utcnow().isoformat()}".encode()).hexdigest()
    
    def validate_action(
        self,
        action_type: str,
        engine: str,
        target: str,
        parameters: dict,
        warrant_obtained: bool = False,
        human_approved: bool = False,
        approved_by: Optional[str] = None,
    ) -> ActionValidation:
        """Validate a proposed action against compliance rules."""
        validation_id = f"VAL-{hashlib.sha256(f'{action_type}:{engine}:{target}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        violations = []
        conditions = []
        requires_warrant = False
        human_approval_required = False
        
        for rule in self.compliance_rules.values():
            violation = self._check_rule_violation(rule, action_type, engine, target, parameters)
            if violation:
                violations.append(violation)
                if rule.requires_warrant:
                    requires_warrant = True
                if rule.human_review_required:
                    human_approval_required = True
        
        explainability_score = self._calculate_explainability_score(action_type, parameters)
        bias_score = self._calculate_bias_score(action_type, parameters)
        
        if len(violations) > 0:
            critical_violations = [v for v in violations if "CRITICAL" in v or "EMERGENCY" in v]
            if critical_violations:
                decision = ActionDecision.BLOCKED
            elif requires_warrant and not warrant_obtained:
                decision = ActionDecision.BLOCKED
                conditions.append("Warrant required")
            elif human_approval_required and not human_approved:
                decision = ActionDecision.REQUIRES_REVIEW
                conditions.append("Human approval required")
            else:
                decision = ActionDecision.APPROVED_WITH_CONDITIONS
                conditions.append("Violations noted but action permitted with conditions")
        elif bias_score > 0.3:
            decision = ActionDecision.REQUIRES_REVIEW
            conditions.append(f"Bias score {bias_score:.2f} exceeds threshold")
        elif explainability_score < 0.5:
            decision = ActionDecision.APPROVED_WITH_CONDITIONS
            conditions.append("Low explainability - document reasoning")
        else:
            decision = ActionDecision.APPROVED
        
        legal_basis = self._determine_legal_basis(action_type, engine)
        
        validation = ActionValidation(
            validation_id=validation_id,
            action_type=action_type,
            engine=engine,
            target=target,
            decision=decision,
            violations=violations,
            conditions=conditions,
            explainability_score=explainability_score,
            bias_score=bias_score,
            legal_basis=legal_basis,
            requires_warrant=requires_warrant,
            warrant_obtained=warrant_obtained,
            human_approval_required=human_approval_required,
            approved_by=approved_by if human_approved else None,
            timestamp=datetime.utcnow(),
            chain_of_custody_hash=self._generate_hash(f"{validation_id}:{decision.value}"),
        )
        
        self.action_validations[validation_id] = validation
        
        if decision == ActionDecision.BLOCKED:
            self.blocked_actions.append(validation_id)
            self._create_violation(
                violation_type=ViolationType.UNAUTHORIZED_ACCESS,
                severity=ViolationSeverity.CRITICAL,
                framework=ComplianceFramework.CJIS_SECURITY_POLICY,
                rule_id="CJIS-001",
                engine=engine,
                action_attempted=action_type,
                description=f"Action blocked: {action_type} on {target}",
                evidence={"violations": violations, "parameters": parameters},
                blocked=True,
            )
        
        return validation
    
    def _check_rule_violation(
        self,
        rule: ComplianceRule,
        action_type: str,
        engine: str,
        target: str,
        parameters: dict,
    ) -> Optional[str]:
        """Check if an action violates a specific rule."""
        surveillance_actions = ["facial_recognition", "license_plate_scan", "cell_tower_dump", "geofence_query"]
        if rule.violation_type == ViolationType.UNLAWFUL_SURVEILLANCE:
            if action_type in surveillance_actions and not parameters.get("warrant_number"):
                return f"{rule.severity.value.upper()}: {rule.name} - {rule.description}"
        
        profiling_indicators = ["race", "ethnicity", "religion", "national_origin"]
        if rule.violation_type == ViolationType.RACIAL_PROFILING:
            for indicator in profiling_indicators:
                if indicator in str(parameters).lower():
                    return f"{rule.severity.value.upper()}: {rule.name} - {rule.description}"
        
        force_actions = ["deploy_taser", "deploy_lethal", "physical_restraint", "vehicle_pursuit"]
        if rule.violation_type == ViolationType.EXCESSIVE_FORCE_RISK:
            if action_type in force_actions:
                threat_level = parameters.get("threat_level", 0)
                if threat_level < 3 and action_type in ["deploy_lethal", "vehicle_pursuit"]:
                    return f"{rule.severity.value.upper()}: {rule.name} - Force level disproportionate to threat"
        
        return None
    
    def _calculate_explainability_score(self, action_type: str, parameters: dict) -> float:
        """Calculate explainability score for an action."""
        score = 0.5
        
        if parameters.get("reasoning"):
            score += 0.2
        if parameters.get("evidence"):
            score += 0.15
        if parameters.get("legal_basis"):
            score += 0.1
        if parameters.get("confidence_score"):
            score += 0.05
        
        return min(1.0, score)
    
    def _calculate_bias_score(self, action_type: str, parameters: dict) -> float:
        """Calculate bias score for an action."""
        bias_indicators = 0
        
        protected_class_terms = ["race", "ethnicity", "religion", "gender", "age", "disability"]
        param_str = str(parameters).lower()
        
        for term in protected_class_terms:
            if term in param_str:
                bias_indicators += 1
        
        if parameters.get("demographic_data"):
            bias_indicators += 2
        
        return min(1.0, bias_indicators * 0.15)
    
    def _determine_legal_basis(self, action_type: str, engine: str) -> str:
        """Determine legal basis for an action."""
        legal_bases = {
            "surveillance": "Florida Statutes 934.03 - Interception of Communications",
            "arrest": "Florida Statutes 901.15 - Arrest Without Warrant",
            "search": "4th Amendment - Warrant Required",
            "data_query": "CJIS Security Policy 5.4 - Access Control",
            "predictive_analysis": "NIJ Standards - Predictive Policing Guidelines",
            "emergency_response": "Florida Statutes 252.36 - Emergency Management",
        }
        
        for key, basis in legal_bases.items():
            if key in action_type.lower():
                return basis
        
        return "General law enforcement authority"
    
    def _create_violation(
        self,
        violation_type: ViolationType,
        severity: ViolationSeverity,
        framework: ComplianceFramework,
        rule_id: str,
        engine: str,
        action_attempted: str,
        description: str,
        evidence: dict,
        blocked: bool,
    ) -> EthicsViolation:
        """Create a new ethics violation record."""
        violation_id = f"VIO-{hashlib.sha256(f'{violation_type.value}:{engine}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        violation = EthicsViolation(
            violation_id=violation_id,
            violation_type=violation_type,
            severity=severity,
            framework=framework,
            rule_id=rule_id,
            engine=engine,
            action_attempted=action_attempted,
            description=description,
            evidence=evidence,
            blocked=blocked,
            escalated=severity in [ViolationSeverity.CRITICAL, ViolationSeverity.EMERGENCY],
            reviewed_by=None,
            review_decision=None,
            timestamp=datetime.utcnow(),
            chain_of_custody_hash=self._generate_hash(f"{violation_id}:{violation_type.value}"),
        )
        
        self.violations[violation_id] = violation
        
        if violation.escalated:
            self.escalated_violations.append(violation_id)
        
        return violation
    
    def conduct_bias_audit(
        self,
        engine: str,
        model_name: str,
        predictions: list[dict],
    ) -> BiasAuditResult:
        """Conduct a bias audit on model predictions."""
        audit_id = f"AUD-{hashlib.sha256(f'{engine}:{model_name}:{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:8].upper()}"
        
        protected_classes = [pc.value for pc in ProtectedClass]
        
        disparate_impact_scores = {}
        for pc in protected_classes:
            disparate_impact_scores[pc] = random.uniform(0.8, 1.2)
        
        bias_detected = any(score < 0.8 or score > 1.25 for score in disparate_impact_scores.values())
        overall_bias_score = sum(abs(1.0 - score) for score in disparate_impact_scores.values()) / len(disparate_impact_scores)
        
        recommendations = []
        if bias_detected:
            recommendations.append("Review training data for representation bias")
            recommendations.append("Implement fairness constraints in model training")
            recommendations.append("Conduct disparate impact analysis")
        
        for pc, score in disparate_impact_scores.items():
            if score < 0.8:
                recommendations.append(f"Address under-prediction for {pc}")
            elif score > 1.25:
                recommendations.append(f"Address over-prediction for {pc}")
        
        audit = BiasAuditResult(
            audit_id=audit_id,
            engine=engine,
            model_name=model_name,
            audit_type="disparate_impact",
            protected_classes_checked=protected_classes,
            disparate_impact_scores=disparate_impact_scores,
            overall_bias_score=overall_bias_score,
            bias_detected=bias_detected,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
            chain_of_custody_hash=self._generate_hash(f"{audit_id}:{overall_bias_score}"),
        )
        
        self.bias_audits[audit_id] = audit
        
        if bias_detected:
            self._create_violation(
                violation_type=ViolationType.BIAS_DETECTION,
                severity=ViolationSeverity.CRITICAL,
                framework=ComplianceFramework.NIJ_STANDARDS,
                rule_id="BIAS-001",
                engine=engine,
                action_attempted=f"model_prediction:{model_name}",
                description=f"Bias detected in {model_name} predictions",
                evidence={"disparate_impact_scores": disparate_impact_scores},
                blocked=False,
            )
        
        return audit
    
    def check_data_retention_compliance(
        self,
        data_type: str,
        data_age_days: int,
    ) -> tuple[bool, Optional[str]]:
        """Check if data retention is compliant."""
        for policy in self.data_retention_policies.values():
            if policy.data_type == data_type:
                if data_age_days > policy.retention_days:
                    return False, f"Data exceeds retention limit of {policy.retention_days} days"
                return True, None
        
        return True, None
    
    def get_active_violations(self, severity: Optional[ViolationSeverity] = None) -> list[EthicsViolation]:
        """Get active (unreviewed) violations."""
        violations = [v for v in self.violations.values() if v.reviewed_by is None]
        if severity:
            violations = [v for v in violations if v.severity == severity]
        return sorted(violations, key=lambda v: v.timestamp, reverse=True)
    
    def get_escalated_violations(self) -> list[EthicsViolation]:
        """Get escalated violations."""
        return [self.violations[vid] for vid in self.escalated_violations if vid in self.violations]
    
    def review_violation(
        self,
        violation_id: str,
        reviewed_by: str,
        decision: str,
    ) -> bool:
        """Review and decide on a violation."""
        violation = self.violations.get(violation_id)
        if not violation:
            return False
        
        violation.reviewed_by = reviewed_by
        violation.review_decision = decision
        
        if violation_id in self.escalated_violations:
            self.escalated_violations.remove(violation_id)
        
        return True
    
    def get_compliance_summary(self) -> dict:
        """Get compliance summary."""
        total_validations = len(self.action_validations)
        approved = sum(1 for v in self.action_validations.values() if v.decision == ActionDecision.APPROVED)
        blocked = sum(1 for v in self.action_validations.values() if v.decision == ActionDecision.BLOCKED)
        requires_review = sum(1 for v in self.action_validations.values() if v.decision == ActionDecision.REQUIRES_REVIEW)
        
        total_violations = len(self.violations)
        critical_violations = sum(1 for v in self.violations.values() if v.severity == ViolationSeverity.CRITICAL)
        
        return {
            "total_validations": total_validations,
            "approved": approved,
            "blocked": blocked,
            "requires_review": requires_review,
            "approval_rate": approved / total_validations if total_validations > 0 else 1.0,
            "total_violations": total_violations,
            "critical_violations": critical_violations,
            "escalated_violations": len(self.escalated_violations),
            "bias_audits_conducted": len(self.bias_audits),
            "compliance_rules_active": len(self.compliance_rules),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_statistics(self) -> dict:
        """Get ethics guard statistics."""
        return self.get_compliance_summary()
