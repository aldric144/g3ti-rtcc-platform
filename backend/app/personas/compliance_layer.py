"""
Compliance Integration Layer

Integrates AI Personas with governance frameworks:
- Phase 28 Constitutional Guardrails
- Phase 33 AI Sentinel Supervisor
- Phase 24 City Autonomy Policy Engine

Every persona decision must run through:
- supervisor.validate_action()
- guardrails.check_legality()
- policy_engine.evaluate()

Any violation triggers auto-block + alert.
"""

import hashlib
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from backend.app.personas.persona_engine import PersonaEngine, PersonaType, Persona


class ComplianceStatus(Enum):
    """Status of compliance check."""
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    WARNING = "warning"
    PENDING_REVIEW = "pending_review"
    BLOCKED = "blocked"


class ComplianceFramework(Enum):
    """Compliance frameworks for validation."""
    CONSTITUTIONAL_GUARDRAILS = "constitutional_guardrails"
    AI_SENTINEL_SUPERVISOR = "ai_sentinel_supervisor"
    CITY_AUTONOMY_POLICY = "city_autonomy_policy"
    ETHICS_GOVERNANCE = "ethics_governance"
    CJIS_SECURITY = "cjis_security"
    FLORIDA_STATUTES = "florida_statutes"
    RBPD_POLICY = "rbpd_policy"


class ViolationType(Enum):
    """Types of compliance violations."""
    CONSTITUTIONAL = "constitutional"
    POLICY = "policy"
    ETHICAL = "ethical"
    LEGAL = "legal"
    PROCEDURAL = "procedural"
    SAFETY = "safety"
    PRIVACY = "privacy"


@dataclass
class ComplianceCheck:
    """Result of a compliance check."""
    check_id: str
    framework: ComplianceFramework
    status: ComplianceStatus
    action_type: str
    persona_id: str
    details: Dict[str, Any]
    violations: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.check_id}:{self.framework.value}:{self.persona_id}:{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "framework": self.framework.value,
            "status": self.status.value,
            "action_type": self.action_type,
            "persona_id": self.persona_id,
            "details": self.details,
            "violations": self.violations,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


@dataclass
class ComplianceViolation:
    """Detailed compliance violation record."""
    violation_id: str
    violation_type: ViolationType
    framework: ComplianceFramework
    persona_id: str
    action_type: str
    description: str
    severity: str
    blocking: bool
    remediation: Optional[str]
    escalated: bool = False
    escalated_to: Optional[str] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.violation_id}:{self.violation_type.value}:{self.persona_id}:{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def escalate(self, escalated_to: str) -> None:
        """Escalate the violation."""
        self.escalated = True
        self.escalated_to = escalated_to
    
    def resolve(self, resolved_by: str, notes: str) -> None:
        """Resolve the violation."""
        self.resolved = True
        self.resolved_by = resolved_by
        self.resolution_notes = notes
        self.resolved_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type.value,
            "framework": self.framework.value,
            "persona_id": self.persona_id,
            "action_type": self.action_type,
            "description": self.description,
            "severity": self.severity,
            "blocking": self.blocking,
            "remediation": self.remediation,
            "escalated": self.escalated,
            "escalated_to": self.escalated_to,
            "resolved": self.resolved,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
            "timestamp": self.timestamp.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


@dataclass
class ComplianceAlert:
    """Alert generated from compliance check."""
    alert_id: str
    alert_type: str
    severity: str
    persona_id: str
    action_type: str
    message: str
    details: Dict[str, Any]
    requires_action: bool
    auto_blocked: bool
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def acknowledge(self, acknowledged_by: str) -> None:
        """Acknowledge the alert."""
        self.acknowledged = True
        self.acknowledged_by = acknowledged_by
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "persona_id": self.persona_id,
            "action_type": self.action_type,
            "message": self.message,
            "details": self.details,
            "requires_action": self.requires_action,
            "auto_blocked": self.auto_blocked,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ActionValidationResult:
    """Result of validating a persona action."""
    validation_id: str
    persona_id: str
    action_type: str
    action_parameters: Dict[str, Any]
    allowed: bool
    compliance_checks: List[ComplianceCheck]
    violations: List[ComplianceViolation]
    alerts: List[ComplianceAlert]
    conditions: List[str]
    requires_approval: bool
    approval_authority: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.validation_id}:{self.persona_id}:{self.action_type}:{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "persona_id": self.persona_id,
            "action_type": self.action_type,
            "action_parameters": self.action_parameters,
            "allowed": self.allowed,
            "compliance_checks": [c.to_dict() for c in self.compliance_checks],
            "violations": [v.to_dict() for v in self.violations],
            "alerts": [a.to_dict() for a in self.alerts],
            "conditions": self.conditions,
            "requires_approval": self.requires_approval,
            "approval_authority": self.approval_authority,
            "timestamp": self.timestamp.isoformat(),
            "chain_of_custody_hash": self.chain_of_custody_hash,
        }


class ComplianceIntegrationLayer:
    """
    Compliance Integration Layer for AI Personas.
    
    Integrates with:
    - Phase 28 Constitutional Guardrails
    - Phase 33 AI Sentinel Supervisor
    - Phase 24 City Autonomy Policy Engine
    
    Every persona decision runs through validation.
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
        
        self.persona_engine = PersonaEngine()
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self.alerts: Dict[str, ComplianceAlert] = {}
        self.validation_results: Dict[str, ActionValidationResult] = {}
        
        self.constitutional_rules: List[Dict[str, Any]] = []
        self.policy_rules: List[Dict[str, Any]] = []
        self.ethics_rules: List[Dict[str, Any]] = []
        
        self._initialize_rules()
        self._initialized = True
    
    def _initialize_rules(self) -> None:
        """Initialize compliance rules from all frameworks."""
        self.constitutional_rules = [
            {
                "rule_id": "4A-001",
                "amendment": "4th",
                "description": "No warrantless searches or seizures",
                "applicable_actions": ["surveillance", "search", "data_collection", "reconnaissance"],
                "conditions": {"requires_warrant": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "4A-002",
                "amendment": "4th",
                "description": "Probable cause required for searches",
                "applicable_actions": ["search", "arrest_recommendation"],
                "conditions": {"requires_probable_cause": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "5A-001",
                "amendment": "5th",
                "description": "Due process required",
                "applicable_actions": ["arrest_recommendation", "detention_recommendation"],
                "conditions": {"requires_due_process": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "5A-002",
                "amendment": "5th",
                "description": "Miranda rights must be respected",
                "applicable_actions": ["interrogation_assist", "interview_assist"],
                "conditions": {"miranda_required": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "14A-001",
                "amendment": "14th",
                "description": "Equal protection - no profiling",
                "applicable_actions": ["targeting", "prediction", "assessment", "surveillance"],
                "conditions": {"no_protected_class_targeting": True},
                "severity": "critical",
                "blocking": True,
            },
        ]
        
        self.policy_rules = [
            {
                "rule_id": "POL-001",
                "policy": "Use of Force",
                "description": "Force recommendations require supervisor approval",
                "applicable_actions": ["force_recommendation", "tactical_action"],
                "conditions": {"requires_supervisor_approval": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "POL-002",
                "policy": "Pursuit Policy",
                "description": "Vehicle pursuits require authorization",
                "applicable_actions": ["pursuit_recommendation", "pursuit_coordination"],
                "conditions": {"requires_authorization": True},
                "severity": "high",
                "blocking": True,
            },
            {
                "rule_id": "POL-003",
                "policy": "Drone Operations",
                "description": "Drone deployment requires approval and FAA compliance",
                "applicable_actions": ["drone_deployment", "aerial_surveillance"],
                "conditions": {"requires_faa_compliance": True, "requires_approval": True},
                "severity": "high",
                "blocking": True,
            },
            {
                "rule_id": "POL-004",
                "policy": "Data Retention",
                "description": "Data must comply with retention policies",
                "applicable_actions": ["data_storage", "evidence_collection"],
                "conditions": {"retention_policy_compliant": True},
                "severity": "medium",
                "blocking": False,
            },
        ]
        
        self.ethics_rules = [
            {
                "rule_id": "ETH-001",
                "principle": "Bias Prevention",
                "description": "Actions must not exhibit bias against protected classes",
                "applicable_actions": ["prediction", "assessment", "recommendation", "targeting"],
                "conditions": {"bias_check_required": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "ETH-002",
                "principle": "Transparency",
                "description": "AI decisions must be explainable",
                "applicable_actions": ["all"],
                "conditions": {"explainability_required": True},
                "severity": "medium",
                "blocking": False,
            },
            {
                "rule_id": "ETH-003",
                "principle": "Human Oversight",
                "description": "Critical decisions require human oversight",
                "applicable_actions": ["arrest_recommendation", "force_recommendation", "tactical_action"],
                "conditions": {"human_oversight_required": True},
                "severity": "critical",
                "blocking": True,
            },
            {
                "rule_id": "ETH-004",
                "principle": "Privacy Protection",
                "description": "Personal privacy must be protected",
                "applicable_actions": ["surveillance", "data_collection", "facial_recognition"],
                "conditions": {"privacy_impact_assessment": True},
                "severity": "high",
                "blocking": False,
            },
        ]
    
    def validate_action(
        self,
        persona_id: str,
        action_type: str,
        parameters: Dict[str, Any],
    ) -> ActionValidationResult:
        """
        Validate a persona action against all compliance frameworks.
        
        Runs through:
        - Constitutional guardrails
        - AI Sentinel Supervisor
        - City Autonomy Policy Engine
        - Ethics Governance
        """
        persona = self.persona_engine.get_persona(persona_id)
        if not persona:
            raise ValueError(f"Persona not found: {persona_id}")
        
        compliance_checks = []
        violations = []
        alerts = []
        conditions = []
        requires_approval = False
        approval_authority = None
        
        const_check = self._check_constitutional_guardrails(persona, action_type, parameters)
        compliance_checks.append(const_check)
        if const_check.status == ComplianceStatus.VIOLATION:
            violations.extend(self._create_violations_from_check(const_check, persona_id, action_type))
        
        sentinel_check = self._check_sentinel_supervisor(persona, action_type, parameters)
        compliance_checks.append(sentinel_check)
        if sentinel_check.status == ComplianceStatus.VIOLATION:
            violations.extend(self._create_violations_from_check(sentinel_check, persona_id, action_type))
        
        policy_check = self._check_city_autonomy_policy(persona, action_type, parameters)
        compliance_checks.append(policy_check)
        if policy_check.status == ComplianceStatus.VIOLATION:
            violations.extend(self._create_violations_from_check(policy_check, persona_id, action_type))
        
        ethics_check = self._check_ethics_governance(persona, action_type, parameters)
        compliance_checks.append(ethics_check)
        if ethics_check.status == ComplianceStatus.VIOLATION:
            violations.extend(self._create_violations_from_check(ethics_check, persona_id, action_type))
        
        blocking_violations = [v for v in violations if v.blocking]
        allowed = len(blocking_violations) == 0
        
        if not allowed:
            alert = self._create_blocking_alert(persona_id, action_type, blocking_violations)
            alerts.append(alert)
            self.alerts[alert.alert_id] = alert
        
        for check in compliance_checks:
            if check.recommendations:
                conditions.extend(check.recommendations)
        
        if action_type in ["force_recommendation", "tactical_action", "arrest_recommendation"]:
            requires_approval = True
            approval_authority = "supervisor"
        elif action_type in ["drone_deployment", "surveillance"]:
            requires_approval = True
            approval_authority = "command"
        
        for violation in violations:
            self.violations[violation.violation_id] = violation
        
        for check in compliance_checks:
            self.compliance_checks[check.check_id] = check
        
        result = ActionValidationResult(
            validation_id=str(uuid.uuid4()),
            persona_id=persona_id,
            action_type=action_type,
            action_parameters=parameters,
            allowed=allowed,
            compliance_checks=compliance_checks,
            violations=violations,
            alerts=alerts,
            conditions=conditions,
            requires_approval=requires_approval,
            approval_authority=approval_authority,
        )
        
        self.validation_results[result.validation_id] = result
        
        return result
    
    def _check_constitutional_guardrails(
        self,
        persona: Persona,
        action_type: str,
        parameters: Dict[str, Any],
    ) -> ComplianceCheck:
        """Check action against constitutional guardrails."""
        violations = []
        warnings = []
        recommendations = []
        
        for rule in self.constitutional_rules:
            if action_type in rule["applicable_actions"]:
                conditions = rule["conditions"]
                
                if conditions.get("requires_warrant"):
                    if not parameters.get("warrant_obtained", False):
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "blocking": rule["blocking"],
                        })
                        recommendations.append("Obtain valid warrant before proceeding")
                
                if conditions.get("no_protected_class_targeting"):
                    if parameters.get("protected_class_involved", False):
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "blocking": rule["blocking"],
                        })
                
                if conditions.get("requires_probable_cause"):
                    if not parameters.get("probable_cause_established", False):
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "blocking": rule["blocking"],
                        })
                        recommendations.append("Establish probable cause before proceeding")
        
        status = ComplianceStatus.VIOLATION if violations else ComplianceStatus.COMPLIANT
        
        return ComplianceCheck(
            check_id=str(uuid.uuid4()),
            framework=ComplianceFramework.CONSTITUTIONAL_GUARDRAILS,
            status=status,
            action_type=action_type,
            persona_id=persona.persona_id,
            details={"rules_checked": len(self.constitutional_rules)},
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
        )
    
    def _check_sentinel_supervisor(
        self,
        persona: Persona,
        action_type: str,
        parameters: Dict[str, Any],
    ) -> ComplianceCheck:
        """Check action against AI Sentinel Supervisor rules."""
        violations = []
        warnings = []
        recommendations = []
        
        autonomy_level = persona.behavior_model.autonomy_level
        high_autonomy_actions = ["tactical_action", "force_recommendation", "pursuit_coordination"]
        
        if action_type in high_autonomy_actions and autonomy_level < 3:
            violations.append({
                "rule_id": "SENT-001",
                "description": f"Action '{action_type}' requires autonomy level 3+, persona has level {autonomy_level}",
                "severity": "high",
                "blocking": True,
            })
            recommendations.append("Escalate to higher autonomy persona or human operator")
        
        if parameters.get("risk_score", 0) > 0.8:
            warnings.append({
                "rule_id": "SENT-002",
                "description": "High risk action detected",
                "severity": "medium",
            })
            recommendations.append("Consider additional safety measures")
        
        if persona.get_compliance_score() < 90:
            warnings.append({
                "rule_id": "SENT-003",
                "description": f"Persona compliance score ({persona.get_compliance_score()}) below threshold",
                "severity": "medium",
            })
        
        status = ComplianceStatus.VIOLATION if violations else (
            ComplianceStatus.WARNING if warnings else ComplianceStatus.COMPLIANT
        )
        
        return ComplianceCheck(
            check_id=str(uuid.uuid4()),
            framework=ComplianceFramework.AI_SENTINEL_SUPERVISOR,
            status=status,
            action_type=action_type,
            persona_id=persona.persona_id,
            details={
                "autonomy_level": autonomy_level,
                "compliance_score": persona.get_compliance_score(),
            },
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
        )
    
    def _check_city_autonomy_policy(
        self,
        persona: Persona,
        action_type: str,
        parameters: Dict[str, Any],
    ) -> ComplianceCheck:
        """Check action against City Autonomy Policy Engine rules."""
        violations = []
        warnings = []
        recommendations = []
        
        for rule in self.policy_rules:
            if action_type in rule["applicable_actions"]:
                conditions = rule["conditions"]
                
                if conditions.get("requires_supervisor_approval"):
                    if not parameters.get("supervisor_approved", False):
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "blocking": rule["blocking"],
                        })
                        recommendations.append("Obtain supervisor approval before proceeding")
                
                if conditions.get("requires_authorization"):
                    if not parameters.get("authorized", False):
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "blocking": rule["blocking"],
                        })
                        recommendations.append("Obtain proper authorization")
                
                if conditions.get("requires_faa_compliance"):
                    if not parameters.get("faa_compliant", False):
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "blocking": rule["blocking"],
                        })
                        recommendations.append("Ensure FAA compliance for drone operations")
        
        status = ComplianceStatus.VIOLATION if violations else ComplianceStatus.COMPLIANT
        
        return ComplianceCheck(
            check_id=str(uuid.uuid4()),
            framework=ComplianceFramework.CITY_AUTONOMY_POLICY,
            status=status,
            action_type=action_type,
            persona_id=persona.persona_id,
            details={"rules_checked": len(self.policy_rules)},
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
        )
    
    def _check_ethics_governance(
        self,
        persona: Persona,
        action_type: str,
        parameters: Dict[str, Any],
    ) -> ComplianceCheck:
        """Check action against Ethics Governance rules."""
        violations = []
        warnings = []
        recommendations = []
        
        for rule in self.ethics_rules:
            applicable = rule["applicable_actions"]
            if action_type in applicable or "all" in applicable:
                conditions = rule["conditions"]
                
                if conditions.get("bias_check_required"):
                    if parameters.get("bias_detected", False):
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "blocking": rule["blocking"],
                        })
                        recommendations.append("Review and address detected bias")
                
                if conditions.get("human_oversight_required"):
                    if not parameters.get("human_oversight", False):
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "description": rule["description"],
                            "severity": rule["severity"],
                            "blocking": rule["blocking"],
                        })
                        recommendations.append("Ensure human oversight for this action")
                
                if conditions.get("explainability_required"):
                    if not parameters.get("explainability_trace", False):
                        warnings.append({
                            "rule_id": rule["rule_id"],
                            "description": "Action should include explainability trace",
                            "severity": "low",
                        })
                        recommendations.append("Include explainability trace for transparency")
        
        status = ComplianceStatus.VIOLATION if violations else (
            ComplianceStatus.WARNING if warnings else ComplianceStatus.COMPLIANT
        )
        
        return ComplianceCheck(
            check_id=str(uuid.uuid4()),
            framework=ComplianceFramework.ETHICS_GOVERNANCE,
            status=status,
            action_type=action_type,
            persona_id=persona.persona_id,
            details={"rules_checked": len(self.ethics_rules)},
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
        )
    
    def _create_violations_from_check(
        self,
        check: ComplianceCheck,
        persona_id: str,
        action_type: str,
    ) -> List[ComplianceViolation]:
        """Create violation records from compliance check."""
        violations = []
        
        for v in check.violations:
            violation = ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                violation_type=self._determine_violation_type(check.framework),
                framework=check.framework,
                persona_id=persona_id,
                action_type=action_type,
                description=v["description"],
                severity=v["severity"],
                blocking=v.get("blocking", False),
                remediation=check.recommendations[0] if check.recommendations else None,
            )
            violations.append(violation)
        
        return violations
    
    def _determine_violation_type(self, framework: ComplianceFramework) -> ViolationType:
        """Determine violation type from framework."""
        mapping = {
            ComplianceFramework.CONSTITUTIONAL_GUARDRAILS: ViolationType.CONSTITUTIONAL,
            ComplianceFramework.AI_SENTINEL_SUPERVISOR: ViolationType.PROCEDURAL,
            ComplianceFramework.CITY_AUTONOMY_POLICY: ViolationType.POLICY,
            ComplianceFramework.ETHICS_GOVERNANCE: ViolationType.ETHICAL,
            ComplianceFramework.CJIS_SECURITY: ViolationType.LEGAL,
            ComplianceFramework.FLORIDA_STATUTES: ViolationType.LEGAL,
            ComplianceFramework.RBPD_POLICY: ViolationType.POLICY,
        }
        return mapping.get(framework, ViolationType.PROCEDURAL)
    
    def _create_blocking_alert(
        self,
        persona_id: str,
        action_type: str,
        violations: List[ComplianceViolation],
    ) -> ComplianceAlert:
        """Create alert for blocking violations."""
        return ComplianceAlert(
            alert_id=str(uuid.uuid4()),
            alert_type="compliance_block",
            severity="critical",
            persona_id=persona_id,
            action_type=action_type,
            message=f"Action '{action_type}' blocked due to {len(violations)} compliance violation(s)",
            details={
                "violation_ids": [v.violation_id for v in violations],
                "violation_types": [v.violation_type.value for v in violations],
            },
            requires_action=True,
            auto_blocked=True,
        )
    
    def get_active_violations(self) -> List[ComplianceViolation]:
        """Get all unresolved violations."""
        return [v for v in self.violations.values() if not v.resolved]
    
    def get_violations_by_persona(self, persona_id: str) -> List[ComplianceViolation]:
        """Get violations for a specific persona."""
        return [v for v in self.violations.values() if v.persona_id == persona_id]
    
    def resolve_violation(self, violation_id: str, resolved_by: str, notes: str) -> bool:
        """Resolve a violation."""
        violation = self.violations.get(violation_id)
        if not violation:
            return False
        
        violation.resolve(resolved_by, notes)
        return True
    
    def escalate_violation(self, violation_id: str, escalated_to: str) -> bool:
        """Escalate a violation."""
        violation = self.violations.get(violation_id)
        if not violation:
            return False
        
        violation.escalate(escalated_to)
        return True
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        alert.acknowledge(acknowledged_by)
        return True
    
    def get_unacknowledged_alerts(self) -> List[ComplianceAlert]:
        """Get all unacknowledged alerts."""
        return [a for a in self.alerts.values() if not a.acknowledged]
    
    def get_compliance_summary(self, persona_id: Optional[str] = None) -> Dict[str, Any]:
        """Get compliance summary."""
        if persona_id:
            checks = [c for c in self.compliance_checks.values() if c.persona_id == persona_id]
            violations = [v for v in self.violations.values() if v.persona_id == persona_id]
        else:
            checks = list(self.compliance_checks.values())
            violations = list(self.violations.values())
        
        total_checks = len(checks)
        compliant = len([c for c in checks if c.status == ComplianceStatus.COMPLIANT])
        total_violations = len(violations)
        unresolved = len([v for v in violations if not v.resolved])
        blocking = len([v for v in violations if v.blocking and not v.resolved])
        
        return {
            "total_checks": total_checks,
            "compliant_checks": compliant,
            "compliance_rate": compliant / total_checks * 100 if total_checks > 0 else 100,
            "total_violations": total_violations,
            "unresolved_violations": unresolved,
            "blocking_violations": blocking,
            "unacknowledged_alerts": len(self.get_unacknowledged_alerts()),
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get compliance layer statistics."""
        return {
            "total_validations": len(self.validation_results),
            "total_checks": len(self.compliance_checks),
            "total_violations": len(self.violations),
            "total_alerts": len(self.alerts),
            "compliance_summary": self.get_compliance_summary(),
        }
