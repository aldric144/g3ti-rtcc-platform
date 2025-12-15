"""
Phase 38: Policy Binding Engine
Binds workflows to city governance policies, department SOPs, legal guardrails,
ethical guardrails, Moral Compass, and Public Safety Guardian.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import uuid


class PolicyType(Enum):
    CITY_GOVERNANCE = "city_governance"
    DEPARTMENT_SOP = "department_sop"
    LEGAL_GUARDRAIL = "legal_guardrail"
    ETHICAL_GUARDRAIL = "ethical_guardrail"
    MORAL_COMPASS = "moral_compass"
    PUBLIC_SAFETY_GUARDIAN = "public_safety_guardian"
    CONSTITUTIONAL = "constitutional"
    CIVIL_RIGHTS = "civil_rights"
    USE_OF_FORCE = "use_of_force"
    PRIVACY = "privacy"
    DATA_GOVERNANCE = "data_governance"
    EMERGENCY_PROTOCOL = "emergency_protocol"


class GuardrailSeverity(Enum):
    BLOCKING = "blocking"
    WARNING = "warning"
    ADVISORY = "advisory"
    INFORMATIONAL = "informational"


@dataclass
class GuardrailCheck:
    check_id: str = field(default_factory=lambda: f"check-{uuid.uuid4().hex[:8]}")
    guardrail_id: str = ""
    policy_type: PolicyType = PolicyType.LEGAL_GUARDRAIL
    severity: GuardrailSeverity = GuardrailSeverity.WARNING
    passed: bool = True
    score: float = 100.0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checked_by: str = "policy_binding_engine"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "guardrail_id": self.guardrail_id,
            "policy_type": self.policy_type.value,
            "severity": self.severity.value,
            "passed": self.passed,
            "score": self.score,
            "message": self.message,
            "details": self.details,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
            "checked_by": self.checked_by,
        }


@dataclass
class PolicyBinding:
    binding_id: str = field(default_factory=lambda: f"binding-{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    policy_type: PolicyType = PolicyType.DEPARTMENT_SOP
    policy_reference: str = ""
    applicable_workflows: List[str] = field(default_factory=list)
    applicable_actions: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    prohibitions: List[str] = field(default_factory=list)
    severity: GuardrailSeverity = GuardrailSeverity.WARNING
    enforcement_mode: str = "enforce"
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def applies_to(self, workflow_name: str, action_type: str) -> bool:
        """Check if this binding applies to a workflow/action."""
        if not self.enabled:
            return False
        if self.applicable_workflows and workflow_name not in self.applicable_workflows:
            if "*" not in self.applicable_workflows:
                return False
        if self.applicable_actions and action_type not in self.applicable_actions:
            if "*" not in self.applicable_actions:
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "binding_id": self.binding_id,
            "name": self.name,
            "description": self.description,
            "policy_type": self.policy_type.value,
            "policy_reference": self.policy_reference,
            "applicable_workflows": self.applicable_workflows,
            "applicable_actions": self.applicable_actions,
            "conditions": self.conditions,
            "requirements": self.requirements,
            "prohibitions": self.prohibitions,
            "severity": self.severity.value,
            "enforcement_mode": self.enforcement_mode,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class PolicyBindingEngine:
    """
    Binds workflows to governance policies, SOPs, and guardrails.
    Ensures all orchestrated actions comply with legal, ethical, and operational requirements.
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

        self.policy_bindings: Dict[str, PolicyBinding] = {}
        self.policy_checkers: Dict[PolicyType, Callable] = {}
        self.check_history: List[GuardrailCheck] = []
        self.statistics: Dict[str, Any] = {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warnings_issued": 0,
            "blocks_issued": 0,
        }
        self._register_default_bindings()
        self._register_default_checkers()

    def _register_default_bindings(self):
        """Register default policy bindings."""
        default_bindings = [
            PolicyBinding(
                name="Constitutional Rights Protection",
                description="Ensures all actions respect constitutional rights",
                policy_type=PolicyType.CONSTITUTIONAL,
                applicable_workflows=["*"],
                applicable_actions=["*"],
                requirements=["fourth_amendment_compliance", "due_process"],
                severity=GuardrailSeverity.BLOCKING,
            ),
            PolicyBinding(
                name="Use of Force Policy",
                description="Governs use of force decisions",
                policy_type=PolicyType.USE_OF_FORCE,
                applicable_workflows=["*"],
                applicable_actions=["drone_dispatch", "robot_dispatch", "lockdown_initiate"],
                requirements=["proportionality", "necessity", "de_escalation_attempted"],
                severity=GuardrailSeverity.BLOCKING,
            ),
            PolicyBinding(
                name="Privacy Protection",
                description="Protects citizen privacy",
                policy_type=PolicyType.PRIVACY,
                applicable_workflows=["*"],
                applicable_actions=["lpr_sweep", "sensor_activate", "evidence_collection"],
                requirements=["data_minimization", "purpose_limitation"],
                severity=GuardrailSeverity.WARNING,
            ),
            PolicyBinding(
                name="Civil Rights Compliance",
                description="Ensures civil rights are protected",
                policy_type=PolicyType.CIVIL_RIGHTS,
                applicable_workflows=["*"],
                applicable_actions=["*"],
                requirements=["non_discrimination", "equal_protection"],
                prohibitions=["racial_profiling", "bias_based_targeting"],
                severity=GuardrailSeverity.BLOCKING,
            ),
            PolicyBinding(
                name="Moral Compass Alignment",
                description="Ensures actions align with ethical AI principles",
                policy_type=PolicyType.MORAL_COMPASS,
                applicable_workflows=["*"],
                applicable_actions=["*"],
                requirements=["ethical_alignment", "fairness", "transparency"],
                severity=GuardrailSeverity.WARNING,
            ),
            PolicyBinding(
                name="Public Safety Guardian Transparency",
                description="Ensures public transparency requirements",
                policy_type=PolicyType.PUBLIC_SAFETY_GUARDIAN,
                applicable_workflows=["*"],
                applicable_actions=["*"],
                requirements=["audit_trail", "public_accountability"],
                severity=GuardrailSeverity.ADVISORY,
            ),
            PolicyBinding(
                name="Emergency Protocol Compliance",
                description="Governs emergency response actions",
                policy_type=PolicyType.EMERGENCY_PROTOCOL,
                applicable_workflows=["emergency_response", "crisis_response"],
                applicable_actions=["emergency_broadcast", "lockdown_initiate"],
                requirements=["authorization_level", "notification_chain"],
                severity=GuardrailSeverity.BLOCKING,
            ),
            PolicyBinding(
                name="Data Governance",
                description="Governs data handling and retention",
                policy_type=PolicyType.DATA_GOVERNANCE,
                applicable_workflows=["*"],
                applicable_actions=["evidence_collection", "case_generation", "audit_log"],
                requirements=["data_classification", "retention_policy", "access_control"],
                severity=GuardrailSeverity.WARNING,
            ),
            PolicyBinding(
                name="Department SOP - Drone Operations",
                description="Standard operating procedures for drone deployment",
                policy_type=PolicyType.DEPARTMENT_SOP,
                applicable_workflows=["*"],
                applicable_actions=["drone_dispatch"],
                requirements=["airspace_clearance", "operator_certification", "mission_logging"],
                severity=GuardrailSeverity.BLOCKING,
            ),
            PolicyBinding(
                name="Department SOP - Robot Operations",
                description="Standard operating procedures for robot deployment",
                policy_type=PolicyType.DEPARTMENT_SOP,
                applicable_workflows=["*"],
                applicable_actions=["robot_dispatch"],
                requirements=["safety_perimeter", "operator_control", "mission_logging"],
                severity=GuardrailSeverity.BLOCKING,
            ),
            PolicyBinding(
                name="City Governance - Resource Allocation",
                description="City policies for resource allocation",
                policy_type=PolicyType.CITY_GOVERNANCE,
                applicable_workflows=["*"],
                applicable_actions=["resource_allocate", "patrol_reroute"],
                requirements=["budget_compliance", "equity_consideration"],
                severity=GuardrailSeverity.WARNING,
            ),
            PolicyBinding(
                name="Legal Guardrail - Surveillance",
                description="Legal requirements for surveillance activities",
                policy_type=PolicyType.LEGAL_GUARDRAIL,
                applicable_workflows=["*"],
                applicable_actions=["sensor_activate", "lpr_sweep", "grid_search"],
                requirements=["warrant_or_exception", "scope_limitation", "documentation"],
                severity=GuardrailSeverity.BLOCKING,
            ),
        ]
        for binding in default_bindings:
            self.policy_bindings[binding.binding_id] = binding

    def _register_default_checkers(self):
        """Register default policy checkers."""
        for policy_type in PolicyType:
            self.policy_checkers[policy_type] = self._default_policy_checker

    async def _default_policy_checker(
        self, binding: PolicyBinding, context: Dict[str, Any]
    ) -> GuardrailCheck:
        """Default policy checker implementation."""
        passed = True
        score = 100.0
        message = "Policy check passed"
        recommendations = []

        for requirement in binding.requirements:
            if requirement not in context.get("satisfied_requirements", []):
                if binding.severity == GuardrailSeverity.BLOCKING:
                    passed = False
                    score -= 25.0
                    message = f"Missing requirement: {requirement}"
                else:
                    score -= 10.0
                    recommendations.append(f"Consider satisfying: {requirement}")

        for prohibition in binding.prohibitions:
            if prohibition in context.get("detected_violations", []):
                passed = False
                score = 0.0
                message = f"Prohibition violated: {prohibition}"

        return GuardrailCheck(
            guardrail_id=binding.binding_id,
            policy_type=binding.policy_type,
            severity=binding.severity,
            passed=passed,
            score=max(0.0, score),
            message=message,
            recommendations=recommendations,
            details={"binding": binding.name, "context_keys": list(context.keys())},
        )

    async def check_policy(
        self,
        workflow_name: str,
        action_type: str,
        context: Dict[str, Any] = None,
    ) -> List[GuardrailCheck]:
        """Check all applicable policies for a workflow/action."""
        context = context or {}
        checks = []

        for binding in self.policy_bindings.values():
            if binding.applies_to(workflow_name, action_type):
                checker = self.policy_checkers.get(
                    binding.policy_type, self._default_policy_checker
                )
                check = await checker(binding, context)
                checks.append(check)
                self.check_history.append(check)

                self.statistics["total_checks"] += 1
                if check.passed:
                    self.statistics["passed_checks"] += 1
                else:
                    self.statistics["failed_checks"] += 1
                    if check.severity == GuardrailSeverity.BLOCKING:
                        self.statistics["blocks_issued"] += 1
                    elif check.severity == GuardrailSeverity.WARNING:
                        self.statistics["warnings_issued"] += 1

        return checks

    def check_policy_sync(
        self,
        workflow_name: str,
        action_type: str,
        context: Dict[str, Any] = None,
    ) -> List[GuardrailCheck]:
        """Check policies synchronously."""
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.check_policy(workflow_name, action_type, context)
            )
        finally:
            loop.close()

    def is_action_allowed(
        self,
        workflow_name: str,
        action_type: str,
        context: Dict[str, Any] = None,
    ) -> tuple[bool, List[GuardrailCheck]]:
        """Check if an action is allowed based on policies."""
        checks = self.check_policy_sync(workflow_name, action_type, context)
        blocking_failures = [
            c for c in checks
            if not c.passed and c.severity == GuardrailSeverity.BLOCKING
        ]
        return len(blocking_failures) == 0, checks

    def add_policy_binding(self, binding: PolicyBinding) -> bool:
        """Add a new policy binding."""
        self.policy_bindings[binding.binding_id] = binding
        return True

    def remove_policy_binding(self, binding_id: str) -> bool:
        """Remove a policy binding."""
        if binding_id in self.policy_bindings:
            del self.policy_bindings[binding_id]
            return True
        return False

    def enable_binding(self, binding_id: str) -> bool:
        """Enable a policy binding."""
        if binding_id in self.policy_bindings:
            self.policy_bindings[binding_id].enabled = True
            return True
        return False

    def disable_binding(self, binding_id: str) -> bool:
        """Disable a policy binding."""
        if binding_id in self.policy_bindings:
            self.policy_bindings[binding_id].enabled = False
            return True
        return False

    def register_policy_checker(
        self, policy_type: PolicyType, checker: Callable
    ) -> bool:
        """Register a custom policy checker."""
        self.policy_checkers[policy_type] = checker
        return True

    def get_policy_bindings(
        self, policy_type: PolicyType = None
    ) -> List[Dict[str, Any]]:
        """Get all policy bindings."""
        bindings = list(self.policy_bindings.values())
        if policy_type:
            bindings = [b for b in bindings if b.policy_type == policy_type]
        return [b.to_dict() for b in bindings]

    def get_applicable_bindings(
        self, workflow_name: str, action_type: str
    ) -> List[Dict[str, Any]]:
        """Get bindings applicable to a workflow/action."""
        return [
            b.to_dict() for b in self.policy_bindings.values()
            if b.applies_to(workflow_name, action_type)
        ]

    def get_check_history(
        self, limit: int = 100, policy_type: PolicyType = None
    ) -> List[Dict[str, Any]]:
        """Get policy check history."""
        history = self.check_history[-limit:]
        if policy_type:
            history = [c for c in history if c.policy_type == policy_type]
        return [c.to_dict() for c in history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get policy binding engine statistics."""
        return {
            **self.statistics,
            "total_bindings": len(self.policy_bindings),
            "enabled_bindings": len([b for b in self.policy_bindings.values() if b.enabled]),
            "bindings_by_type": {
                pt.value: len([b for b in self.policy_bindings.values() if b.policy_type == pt])
                for pt in PolicyType
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary across all policy types."""
        recent_checks = self.check_history[-1000:]
        summary = {}
        for policy_type in PolicyType:
            type_checks = [c for c in recent_checks if c.policy_type == policy_type]
            if type_checks:
                passed = len([c for c in type_checks if c.passed])
                total = len(type_checks)
                avg_score = sum(c.score for c in type_checks) / total
                summary[policy_type.value] = {
                    "total_checks": total,
                    "passed": passed,
                    "failed": total - passed,
                    "compliance_rate": (passed / total) * 100,
                    "average_score": avg_score,
                }
        return summary
