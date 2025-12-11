"""
Phase 25: AI Constitution Engine

A hierarchical rules engine that validates all AI actions against:
- Constitutional Layer (US & Florida Constitutions)
- Statutory Layer (Florida Statutes)
- Local Ordinance Layer (Riviera Beach Code)
- Agency SOP Layer (RBPD + Fire/EMS)
- Ethics Layer (Bias prevention, accountability, fairness)
- Autonomy Layer (Level 0/1/2 action permissions)
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4

from .legislative_kb import (
    LegislativeKnowledgeBase,
    LegalSource,
    LegalCategory,
    LegalDocument,
    get_legislative_knowledge_base,
)


class ConstitutionalLayer(Enum):
    """Constitutional hierarchy layers (in order of precedence)."""
    FEDERAL_CONSTITUTIONAL = 1
    STATE_CONSTITUTIONAL = 2
    STATUTORY = 3
    LOCAL_ORDINANCE = 4
    AGENCY_SOP = 5
    ETHICS = 6
    AUTONOMY = 7


class ValidationResult(Enum):
    """Action validation results."""
    ALLOWED = "allowed"
    DENIED = "denied"
    ALLOWED_WITH_HUMAN_REVIEW = "allowed_with_human_review"


class ActionCategory(Enum):
    """Categories of AI actions."""
    SURVEILLANCE = "surveillance"
    DRONE_OPERATION = "drone_operation"
    ROBOTICS_DEPLOYMENT = "robotics_deployment"
    USE_OF_FORCE = "use_of_force"
    TRAFFIC_CONTROL = "traffic_control"
    PATROL_DEPLOYMENT = "patrol_deployment"
    PREDICTIVE_POLICING = "predictive_policing"
    EMERGENCY_RESPONSE = "emergency_response"
    EVACUATION = "evacuation"
    MASS_ALERT = "mass_alert"
    DATA_ACCESS = "data_access"
    RESOURCE_ALLOCATION = "resource_allocation"
    CROWD_MANAGEMENT = "crowd_management"
    PROPERTY_ENTRY = "property_entry"


class AutonomyLevel(Enum):
    """Autonomy levels for actions."""
    LEVEL_0 = 0  # Read-only, observation
    LEVEL_1 = 1  # Automated low-risk
    LEVEL_2 = 2  # Human-confirmed medium/high-risk


@dataclass
class ConstitutionalRule:
    """Represents a rule in the AI Constitution."""
    rule_id: str
    layer: ConstitutionalLayer
    name: str
    description: str
    action_categories: List[ActionCategory]
    condition: Callable[[Dict[str, Any]], bool]
    result: ValidationResult
    priority: int
    source_documents: List[str]
    rationale: str
    exceptions: List[str]
    required_approvals: List[str]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def evaluate(self, action_context: Dict[str, Any]) -> bool:
        """Evaluate if this rule applies to the given action context."""
        try:
            return self.condition(action_context)
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "layer": self.layer.name,
            "layer_priority": self.layer.value,
            "name": self.name,
            "description": self.description,
            "action_categories": [c.value for c in self.action_categories],
            "result": self.result.value,
            "priority": self.priority,
            "source_documents": self.source_documents,
            "rationale": self.rationale,
            "exceptions": self.exceptions,
            "required_approvals": self.required_approvals,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RuleEvaluation:
    """Result of evaluating a single rule."""
    rule: ConstitutionalRule
    triggered: bool
    context_matched: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule.to_dict(),
            "triggered": self.triggered,
            "context_matched": self.context_matched,
        }


@dataclass
class ValidationDecision:
    """Represents a validation decision from the Constitution Engine."""
    decision_id: str
    action_type: str
    action_category: ActionCategory
    action_details: Dict[str, Any]
    result: ValidationResult
    autonomy_level: AutonomyLevel
    triggered_rules: List[RuleEvaluation]
    blocking_rules: List[RuleEvaluation]
    explanation: str
    precedence_chain: List[str]
    required_approvals: List[str]
    risk_factors: List[str]
    applicable_documents: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "action_type": self.action_type,
            "action_category": self.action_category.value,
            "action_details": self.action_details,
            "result": self.result.value,
            "autonomy_level": self.autonomy_level.value,
            "triggered_rules": [r.to_dict() for r in self.triggered_rules],
            "blocking_rules": [r.to_dict() for r in self.blocking_rules],
            "explanation": self.explanation,
            "precedence_chain": self.precedence_chain,
            "required_approvals": self.required_approvals,
            "risk_factors": self.risk_factors,
            "applicable_documents": self.applicable_documents,
            "timestamp": self.timestamp.isoformat(),
        }


class AIConstitutionEngine:
    """
    AI Constitution Engine
    
    A hierarchical rules engine that validates all AI actions against
    constitutional, statutory, local, SOP, ethics, and autonomy rules.
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
        
        self._rules: Dict[str, ConstitutionalRule] = {}
        self._rules_by_layer: Dict[ConstitutionalLayer, List[str]] = {
            layer: [] for layer in ConstitutionalLayer
        }
        self._rules_by_category: Dict[ActionCategory, List[str]] = {
            cat: [] for cat in ActionCategory
        }
        self._decision_history: List[ValidationDecision] = []
        self._audit_log: List[Dict[str, Any]] = []
        self._kb = get_legislative_knowledge_base()
        
        self._initialize_constitutional_rules()
        self._initialized = True
    
    def _initialize_constitutional_rules(self):
        """Initialize the constitutional rules hierarchy."""
        
        # === FEDERAL CONSTITUTIONAL LAYER ===
        
        # 4th Amendment - Unreasonable Search
        self._add_rule(ConstitutionalRule(
            rule_id="const-fed-4th-search",
            layer=ConstitutionalLayer.FEDERAL_CONSTITUTIONAL,
            name="Fourth Amendment - Unreasonable Search Protection",
            description="Prohibits unreasonable searches without warrant or probable cause",
            action_categories=[
                ActionCategory.SURVEILLANCE,
                ActionCategory.DRONE_OPERATION,
                ActionCategory.PROPERTY_ENTRY,
                ActionCategory.DATA_ACCESS,
            ],
            condition=lambda ctx: (
                ctx.get("requires_warrant", False) and
                not ctx.get("has_warrant", False) and
                not ctx.get("exigent_circumstances", False) and
                not ctx.get("consent_given", False)
            ),
            result=ValidationResult.DENIED,
            priority=100,
            source_documents=["us-const-4th"],
            rationale="The Fourth Amendment protects against unreasonable searches and seizures",
            exceptions=["exigent_circumstances", "consent", "plain_view", "hot_pursuit"],
            required_approvals=[],
        ))
        
        # 1st Amendment - Assembly Protection
        self._add_rule(ConstitutionalRule(
            rule_id="const-fed-1st-assembly",
            layer=ConstitutionalLayer.FEDERAL_CONSTITUTIONAL,
            name="First Amendment - Assembly Protection",
            description="Protects peaceful assembly and protest activities",
            action_categories=[
                ActionCategory.CROWD_MANAGEMENT,
                ActionCategory.SURVEILLANCE,
                ActionCategory.PATROL_DEPLOYMENT,
            ],
            condition=lambda ctx: (
                ctx.get("is_peaceful_assembly", False) and
                ctx.get("action_would_disperse", False) and
                not ctx.get("imminent_violence", False)
            ),
            result=ValidationResult.DENIED,
            priority=100,
            source_documents=["us-const-1st"],
            rationale="The First Amendment protects the right to peacefully assemble",
            exceptions=["imminent_violence", "unlawful_activity", "public_safety_emergency"],
            required_approvals=[],
        ))
        
        # 14th Amendment - Due Process / Equal Protection
        self._add_rule(ConstitutionalRule(
            rule_id="const-fed-14th-equal",
            layer=ConstitutionalLayer.FEDERAL_CONSTITUTIONAL,
            name="Fourteenth Amendment - Equal Protection",
            description="Prohibits discriminatory enforcement actions",
            action_categories=[
                ActionCategory.PREDICTIVE_POLICING,
                ActionCategory.PATROL_DEPLOYMENT,
                ActionCategory.SURVEILLANCE,
            ],
            condition=lambda ctx: (
                ctx.get("targets_protected_class", False) or
                ctx.get("discriminatory_pattern", False)
            ),
            result=ValidationResult.DENIED,
            priority=100,
            source_documents=["us-const-14th"],
            rationale="The Fourteenth Amendment requires equal protection under the law",
            exceptions=[],
            required_approvals=[],
        ))
        
        # === STATE CONSTITUTIONAL LAYER ===
        
        # Florida Privacy Right
        self._add_rule(ConstitutionalRule(
            rule_id="const-fl-privacy",
            layer=ConstitutionalLayer.STATE_CONSTITUTIONAL,
            name="Florida Right of Privacy",
            description="Florida's explicit constitutional right to privacy",
            action_categories=[
                ActionCategory.SURVEILLANCE,
                ActionCategory.DRONE_OPERATION,
                ActionCategory.DATA_ACCESS,
            ],
            condition=lambda ctx: (
                ctx.get("invades_privacy", False) and
                not ctx.get("compelling_state_interest", False) and
                not ctx.get("least_intrusive_means", False)
            ),
            result=ValidationResult.DENIED,
            priority=90,
            source_documents=["florida-const-art1-s23"],
            rationale="Florida Constitution provides explicit right to privacy",
            exceptions=["compelling_state_interest", "consent"],
            required_approvals=[],
        ))
        
        # Florida Search and Seizure
        self._add_rule(ConstitutionalRule(
            rule_id="const-fl-search",
            layer=ConstitutionalLayer.STATE_CONSTITUTIONAL,
            name="Florida Search and Seizure Protection",
            description="Florida's protection against unreasonable searches including communications",
            action_categories=[
                ActionCategory.SURVEILLANCE,
                ActionCategory.DATA_ACCESS,
            ],
            condition=lambda ctx: (
                ctx.get("intercepts_communications", False) and
                not ctx.get("has_court_order", False)
            ),
            result=ValidationResult.DENIED,
            priority=90,
            source_documents=["florida-const-art1-s12"],
            rationale="Florida Constitution protects against unreasonable interception of communications",
            exceptions=["court_order", "one_party_consent"],
            required_approvals=[],
        ))
        
        # === STATUTORY LAYER ===
        
        # Florida Wiretap Law
        self._add_rule(ConstitutionalRule(
            rule_id="stat-fl-wiretap",
            layer=ConstitutionalLayer.STATUTORY,
            name="Florida Wiretap Statute",
            description="Florida's two-party consent requirement for communications interception",
            action_categories=[
                ActionCategory.SURVEILLANCE,
            ],
            condition=lambda ctx: (
                ctx.get("records_audio", False) and
                not ctx.get("all_parties_consent", False) and
                not ctx.get("has_court_order", False)
            ),
            result=ValidationResult.DENIED,
            priority=80,
            source_documents=["fss-934"],
            rationale="Florida requires all-party consent for audio recording",
            exceptions=["court_order", "law_enforcement_exception"],
            required_approvals=[],
        ))
        
        # Florida Use of Force
        self._add_rule(ConstitutionalRule(
            rule_id="stat-fl-force",
            layer=ConstitutionalLayer.STATUTORY,
            name="Florida Use of Force Standards",
            description="Statutory requirements for law enforcement use of force",
            action_categories=[
                ActionCategory.USE_OF_FORCE,
                ActionCategory.ROBOTICS_DEPLOYMENT,
            ],
            condition=lambda ctx: (
                ctx.get("involves_force", True) and
                ctx.get("force_level", "none") != "none"
            ),
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            priority=80,
            source_documents=["fss-776"],
            rationale="Use of force requires human authorization and review",
            exceptions=[],
            required_approvals=["supervisor", "command_staff"],
        ))
        
        # Florida Emergency Powers
        self._add_rule(ConstitutionalRule(
            rule_id="stat-fl-emergency",
            layer=ConstitutionalLayer.STATUTORY,
            name="Florida Emergency Management Powers",
            description="Emergency powers during declared emergencies",
            action_categories=[
                ActionCategory.EVACUATION,
                ActionCategory.MASS_ALERT,
                ActionCategory.EMERGENCY_RESPONSE,
            ],
            condition=lambda ctx: (
                ctx.get("is_emergency_action", False) and
                ctx.get("emergency_declared", False)
            ),
            result=ValidationResult.ALLOWED,
            priority=80,
            source_documents=["fss-252"],
            rationale="Emergency actions are authorized during declared emergencies",
            exceptions=[],
            required_approvals=[],
        ))
        
        # === LOCAL ORDINANCE LAYER ===
        
        # Riviera Beach Drone Property Entry
        self._add_rule(ConstitutionalRule(
            rule_id="local-rb-drone-property",
            layer=ConstitutionalLayer.LOCAL_ORDINANCE,
            name="Riviera Beach Drone Property Entry",
            description="Restrictions on drone entry to private property",
            action_categories=[
                ActionCategory.DRONE_OPERATION,
                ActionCategory.PROPERTY_ENTRY,
            ],
            condition=lambda ctx: (
                ctx.get("is_drone_operation", False) and
                ctx.get("enters_private_property", False) and
                not ctx.get("exigent_circumstances", False) and
                not ctx.get("has_warrant", False)
            ),
            result=ValidationResult.DENIED,
            priority=70,
            source_documents=["rb-code-drones"],
            rationale="Drones cannot enter private property without exigent circumstances or warrant",
            exceptions=["exigent_circumstances", "warrant", "consent", "hot_pursuit"],
            required_approvals=[],
        ))
        
        # Riviera Beach Robotics Entry
        self._add_rule(ConstitutionalRule(
            rule_id="local-rb-robotics-entry",
            layer=ConstitutionalLayer.LOCAL_ORDINANCE,
            name="Riviera Beach Tactical Robotics Entry",
            description="Restrictions on robotic entry to private property",
            action_categories=[
                ActionCategory.ROBOTICS_DEPLOYMENT,
                ActionCategory.PROPERTY_ENTRY,
            ],
            condition=lambda ctx: (
                ctx.get("is_robotics_operation", False) and
                ctx.get("enters_private_property", False)
            ),
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            priority=70,
            source_documents=["rb-code-robotics"],
            rationale="Tactical robotics entry requires human authorization",
            exceptions=["active_shooter", "hostage_situation"],
            required_approvals=["command_staff", "legal_review"],
        ))
        
        # Riviera Beach Emergency Evacuation
        self._add_rule(ConstitutionalRule(
            rule_id="local-rb-evacuation",
            layer=ConstitutionalLayer.LOCAL_ORDINANCE,
            name="Riviera Beach Evacuation Authority",
            description="Authority to order evacuations during emergencies",
            action_categories=[
                ActionCategory.EVACUATION,
            ],
            condition=lambda ctx: (
                ctx.get("is_evacuation_order", False) and
                ctx.get("emergency_declared", False)
            ),
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            priority=70,
            source_documents=["rb-emergency"],
            rationale="Evacuation orders require emergency declaration and authorization",
            exceptions=["imminent_threat_to_life"],
            required_approvals=["city_manager", "emergency_director"],
        ))
        
        # === AGENCY SOP LAYER ===
        
        # RBPD Use of Force SOP
        self._add_rule(ConstitutionalRule(
            rule_id="sop-rbpd-force",
            layer=ConstitutionalLayer.AGENCY_SOP,
            name="RBPD Use of Force Policy",
            description="RBPD standard operating procedures for use of force",
            action_categories=[
                ActionCategory.USE_OF_FORCE,
            ],
            condition=lambda ctx: (
                ctx.get("involves_force", False)
            ),
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            priority=60,
            source_documents=["rbpd-sop"],
            rationale="All use of force must comply with RBPD SOP",
            exceptions=[],
            required_approvals=["supervisor"],
        ))
        
        # RBPD Surveillance SOP
        self._add_rule(ConstitutionalRule(
            rule_id="sop-rbpd-surveillance",
            layer=ConstitutionalLayer.AGENCY_SOP,
            name="RBPD Surveillance Operations Policy",
            description="RBPD standard operating procedures for surveillance",
            action_categories=[
                ActionCategory.SURVEILLANCE,
                ActionCategory.DRONE_OPERATION,
            ],
            condition=lambda ctx: (
                ctx.get("is_surveillance", False) and
                ctx.get("duration_hours", 0) > 4
            ),
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            priority=60,
            source_documents=["rbpd-sop"],
            rationale="Extended surveillance requires supervisor approval",
            exceptions=["active_investigation"],
            required_approvals=["supervisor"],
        ))
        
        # RBPD Predictive Policing SOP
        self._add_rule(ConstitutionalRule(
            rule_id="sop-rbpd-predictive",
            layer=ConstitutionalLayer.AGENCY_SOP,
            name="RBPD Predictive Policing Policy",
            description="RBPD guidelines for predictive policing tools",
            action_categories=[
                ActionCategory.PREDICTIVE_POLICING,
                ActionCategory.PATROL_DEPLOYMENT,
            ],
            condition=lambda ctx: (
                ctx.get("uses_predictive_model", False)
            ),
            result=ValidationResult.ALLOWED,
            priority=60,
            source_documents=["rbpd-sop"],
            rationale="Predictive policing tools may be used per SOP guidelines",
            exceptions=[],
            required_approvals=[],
        ))
        
        # Fire/EMS MCI Protocol
        self._add_rule(ConstitutionalRule(
            rule_id="sop-fire-mci",
            layer=ConstitutionalLayer.AGENCY_SOP,
            name="Fire/EMS Mass Casualty Protocol",
            description="Fire/EMS protocols for mass casualty incidents",
            action_categories=[
                ActionCategory.EMERGENCY_RESPONSE,
            ],
            condition=lambda ctx: (
                ctx.get("is_mci", False)
            ),
            result=ValidationResult.ALLOWED,
            priority=60,
            source_documents=["rb-fire-ems"],
            rationale="MCI protocols authorize emergency response actions",
            exceptions=[],
            required_approvals=[],
        ))
        
        # === ETHICS LAYER ===
        
        # Bias Prevention
        self._add_rule(ConstitutionalRule(
            rule_id="ethics-bias",
            layer=ConstitutionalLayer.ETHICS,
            name="Bias Prevention",
            description="Prevents actions that exhibit algorithmic bias",
            action_categories=[
                ActionCategory.PREDICTIVE_POLICING,
                ActionCategory.PATROL_DEPLOYMENT,
                ActionCategory.SURVEILLANCE,
            ],
            condition=lambda ctx: (
                ctx.get("bias_score", 0) > 0.3 or
                ctx.get("disparate_impact", False)
            ),
            result=ValidationResult.DENIED,
            priority=50,
            source_documents=["nist-ai-rmf", "dhs-st-guidelines"],
            rationale="Actions exhibiting algorithmic bias are prohibited",
            exceptions=["bias_mitigated"],
            required_approvals=[],
        ))
        
        # Accountability Requirement
        self._add_rule(ConstitutionalRule(
            rule_id="ethics-accountability",
            layer=ConstitutionalLayer.ETHICS,
            name="Accountability Requirement",
            description="Ensures all AI actions have clear accountability chain",
            action_categories=[cat for cat in ActionCategory],
            condition=lambda ctx: (
                not ctx.get("has_accountability_chain", True)
            ),
            result=ValidationResult.DENIED,
            priority=50,
            source_documents=["nist-ai-rmf"],
            rationale="All AI actions must have clear accountability",
            exceptions=[],
            required_approvals=[],
        ))
        
        # Fairness Requirement
        self._add_rule(ConstitutionalRule(
            rule_id="ethics-fairness",
            layer=ConstitutionalLayer.ETHICS,
            name="Fairness Requirement",
            description="Ensures fair treatment across all demographics",
            action_categories=[
                ActionCategory.PREDICTIVE_POLICING,
                ActionCategory.PATROL_DEPLOYMENT,
                ActionCategory.ENFORCEMENT,
            ] if hasattr(ActionCategory, 'ENFORCEMENT') else [
                ActionCategory.PREDICTIVE_POLICING,
                ActionCategory.PATROL_DEPLOYMENT,
            ],
            condition=lambda ctx: (
                ctx.get("fairness_score", 1.0) < 0.7
            ),
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            priority=50,
            source_documents=["nist-ai-rmf", "dhs-st-guidelines"],
            rationale="Actions with low fairness scores require human review",
            exceptions=[],
            required_approvals=["supervisor"],
        ))
        
        # Transparency Requirement
        self._add_rule(ConstitutionalRule(
            rule_id="ethics-transparency",
            layer=ConstitutionalLayer.ETHICS,
            name="Transparency Requirement",
            description="Ensures AI decision-making is explainable",
            action_categories=[cat for cat in ActionCategory],
            condition=lambda ctx: (
                not ctx.get("is_explainable", True)
            ),
            result=ValidationResult.DENIED,
            priority=50,
            source_documents=["nist-ai-rmf"],
            rationale="AI decisions must be explainable",
            exceptions=["emergency_override"],
            required_approvals=[],
        ))
        
        # === AUTONOMY LAYER ===
        
        # Level 0 - Observation Only
        self._add_rule(ConstitutionalRule(
            rule_id="autonomy-level-0",
            layer=ConstitutionalLayer.AUTONOMY,
            name="Level 0 - Observation Only",
            description="Read-only actions that do not affect the physical world",
            action_categories=[
                ActionCategory.SURVEILLANCE,
                ActionCategory.DATA_ACCESS,
            ],
            condition=lambda ctx: (
                ctx.get("autonomy_level", 0) == 0 and
                not ctx.get("affects_physical_world", False)
            ),
            result=ValidationResult.ALLOWED,
            priority=40,
            source_documents=[],
            rationale="Level 0 observation actions are automatically allowed",
            exceptions=[],
            required_approvals=[],
        ))
        
        # Level 1 - Automated Low-Risk
        self._add_rule(ConstitutionalRule(
            rule_id="autonomy-level-1",
            layer=ConstitutionalLayer.AUTONOMY,
            name="Level 1 - Automated Low-Risk",
            description="Low-risk actions that can be automated",
            action_categories=[
                ActionCategory.TRAFFIC_CONTROL,
                ActionCategory.PATROL_DEPLOYMENT,
                ActionCategory.RESOURCE_ALLOCATION,
            ],
            condition=lambda ctx: (
                ctx.get("autonomy_level", 0) == 1 and
                ctx.get("risk_score", 0) < 0.3
            ),
            result=ValidationResult.ALLOWED,
            priority=40,
            source_documents=[],
            rationale="Level 1 low-risk actions can be automated",
            exceptions=[],
            required_approvals=[],
        ))
        
        # Level 2 - Human Confirmation Required
        self._add_rule(ConstitutionalRule(
            rule_id="autonomy-level-2",
            layer=ConstitutionalLayer.AUTONOMY,
            name="Level 2 - Human Confirmation Required",
            description="Medium/high-risk actions requiring human confirmation",
            action_categories=[
                ActionCategory.USE_OF_FORCE,
                ActionCategory.DRONE_OPERATION,
                ActionCategory.ROBOTICS_DEPLOYMENT,
                ActionCategory.EVACUATION,
                ActionCategory.MASS_ALERT,
                ActionCategory.PROPERTY_ENTRY,
            ],
            condition=lambda ctx: (
                ctx.get("autonomy_level", 0) == 2 or
                ctx.get("risk_score", 0) >= 0.3
            ),
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            priority=40,
            source_documents=[],
            rationale="Level 2 actions require human confirmation",
            exceptions=["imminent_threat_to_life"],
            required_approvals=["operator"],
        ))
        
        # High-Risk Action Override
        self._add_rule(ConstitutionalRule(
            rule_id="autonomy-high-risk",
            layer=ConstitutionalLayer.AUTONOMY,
            name="High-Risk Action Override",
            description="High-risk actions always require human review",
            action_categories=[
                ActionCategory.USE_OF_FORCE,
                ActionCategory.PROPERTY_ENTRY,
                ActionCategory.EVACUATION,
            ],
            condition=lambda ctx: (
                ctx.get("risk_score", 0) >= 0.7
            ),
            result=ValidationResult.ALLOWED_WITH_HUMAN_REVIEW,
            priority=40,
            source_documents=[],
            rationale="High-risk actions always require human review regardless of autonomy level",
            exceptions=[],
            required_approvals=["supervisor", "command_staff"],
        ))
    
    def _add_rule(self, rule: ConstitutionalRule):
        """Add a rule to the constitution."""
        self._rules[rule.rule_id] = rule
        self._rules_by_layer[rule.layer].append(rule.rule_id)
        for category in rule.action_categories:
            self._rules_by_category[category].append(rule.rule_id)
    
    def validate_action(
        self,
        action_type: str,
        action_category: ActionCategory,
        action_details: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ValidationDecision:
        """
        Validate an action against the AI Constitution.
        
        Returns a ValidationDecision with the result and full explanation.
        """
        decision_id = f"decision-{uuid4().hex[:12]}"
        
        # Merge action details with context
        full_context = {**context, **action_details}
        
        # Get applicable rules for this action category
        applicable_rule_ids = set(self._rules_by_category.get(action_category, []))
        
        # Evaluate rules in order of layer precedence
        triggered_rules: List[RuleEvaluation] = []
        blocking_rules: List[RuleEvaluation] = []
        all_required_approvals: List[str] = []
        precedence_chain: List[str] = []
        
        # Process layers in order of precedence
        for layer in ConstitutionalLayer:
            layer_rule_ids = self._rules_by_layer.get(layer, [])
            
            for rule_id in layer_rule_ids:
                if rule_id not in applicable_rule_ids and rule_id not in self._rules:
                    continue
                
                rule = self._rules.get(rule_id)
                if not rule or not rule.is_active:
                    continue
                
                # Check if rule applies to this action category
                if action_category not in rule.action_categories:
                    continue
                
                # Evaluate the rule
                triggered = rule.evaluate(full_context)
                
                if triggered:
                    evaluation = RuleEvaluation(
                        rule=rule,
                        triggered=True,
                        context_matched={
                            k: v for k, v in full_context.items()
                            if k in str(rule.condition)
                        },
                    )
                    triggered_rules.append(evaluation)
                    precedence_chain.append(f"{layer.name}: {rule.name}")
                    
                    if rule.result == ValidationResult.DENIED:
                        blocking_rules.append(evaluation)
                    
                    all_required_approvals.extend(rule.required_approvals)
        
        # Determine final result based on triggered rules
        final_result = self._determine_final_result(triggered_rules, blocking_rules)
        
        # Determine autonomy level
        autonomy_level = self._determine_autonomy_level(action_category, full_context, final_result)
        
        # Get applicable documents
        applicable_docs = self._kb.get_applicable_documents(action_type, full_context)
        
        # Generate explanation
        explanation = self._generate_explanation(
            action_type,
            action_category,
            final_result,
            triggered_rules,
            blocking_rules,
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(full_context, triggered_rules)
        
        # Create decision
        decision = ValidationDecision(
            decision_id=decision_id,
            action_type=action_type,
            action_category=action_category,
            action_details=action_details,
            result=final_result,
            autonomy_level=autonomy_level,
            triggered_rules=triggered_rules,
            blocking_rules=blocking_rules,
            explanation=explanation,
            precedence_chain=precedence_chain,
            required_approvals=list(set(all_required_approvals)),
            risk_factors=risk_factors,
            applicable_documents=[d.document_id for d in applicable_docs],
        )
        
        # Log decision
        self._decision_history.append(decision)
        self._log_audit("validation_decision", decision.decision_id, decision.to_dict())
        
        return decision
    
    def _determine_final_result(
        self,
        triggered_rules: List[RuleEvaluation],
        blocking_rules: List[RuleEvaluation],
    ) -> ValidationResult:
        """Determine the final validation result based on triggered rules."""
        
        # If any blocking rule was triggered, deny
        if blocking_rules:
            return ValidationResult.DENIED
        
        # Check for human review requirements
        for evaluation in triggered_rules:
            if evaluation.rule.result == ValidationResult.ALLOWED_WITH_HUMAN_REVIEW:
                return ValidationResult.ALLOWED_WITH_HUMAN_REVIEW
        
        # Default to allowed if no blocking rules
        return ValidationResult.ALLOWED
    
    def _determine_autonomy_level(
        self,
        action_category: ActionCategory,
        context: Dict[str, Any],
        result: ValidationResult,
    ) -> AutonomyLevel:
        """Determine the appropriate autonomy level for an action."""
        
        # If denied, no autonomy
        if result == ValidationResult.DENIED:
            return AutonomyLevel.LEVEL_0
        
        # High-risk categories always require human review
        high_risk_categories = [
            ActionCategory.USE_OF_FORCE,
            ActionCategory.PROPERTY_ENTRY,
            ActionCategory.EVACUATION,
            ActionCategory.ROBOTICS_DEPLOYMENT,
        ]
        
        if action_category in high_risk_categories:
            return AutonomyLevel.LEVEL_2
        
        # Check risk score
        risk_score = context.get("risk_score", 0)
        if risk_score >= 0.5:
            return AutonomyLevel.LEVEL_2
        elif risk_score >= 0.2:
            return AutonomyLevel.LEVEL_1
        
        # Low-risk observation actions
        if action_category in [ActionCategory.SURVEILLANCE, ActionCategory.DATA_ACCESS]:
            if not context.get("affects_physical_world", False):
                return AutonomyLevel.LEVEL_0
        
        # Default based on result
        if result == ValidationResult.ALLOWED_WITH_HUMAN_REVIEW:
            return AutonomyLevel.LEVEL_2
        
        return AutonomyLevel.LEVEL_1
    
    def _generate_explanation(
        self,
        action_type: str,
        action_category: ActionCategory,
        result: ValidationResult,
        triggered_rules: List[RuleEvaluation],
        blocking_rules: List[RuleEvaluation],
    ) -> str:
        """Generate a human-readable explanation of the decision."""
        
        if result == ValidationResult.DENIED:
            blocking_names = [r.rule.name for r in blocking_rules]
            return (
                f"Action '{action_type}' ({action_category.value}) was DENIED. "
                f"Blocking rules: {', '.join(blocking_names)}. "
                f"Rationale: {blocking_rules[0].rule.rationale if blocking_rules else 'Unknown'}"
            )
        
        elif result == ValidationResult.ALLOWED_WITH_HUMAN_REVIEW:
            review_rules = [r for r in triggered_rules if r.rule.result == ValidationResult.ALLOWED_WITH_HUMAN_REVIEW]
            rule_names = [r.rule.name for r in review_rules]
            return (
                f"Action '{action_type}' ({action_category.value}) requires HUMAN REVIEW. "
                f"Triggered rules requiring review: {', '.join(rule_names)}."
            )
        
        else:
            return (
                f"Action '{action_type}' ({action_category.value}) is ALLOWED. "
                f"No blocking rules triggered. {len(triggered_rules)} rules evaluated."
            )
    
    def _identify_risk_factors(
        self,
        context: Dict[str, Any],
        triggered_rules: List[RuleEvaluation],
    ) -> List[str]:
        """Identify risk factors from the context and triggered rules."""
        risk_factors = []
        
        if context.get("involves_force", False):
            risk_factors.append("Involves use of force")
        
        if context.get("enters_private_property", False):
            risk_factors.append("Enters private property")
        
        if context.get("invades_privacy", False):
            risk_factors.append("Privacy implications")
        
        if context.get("targets_individual", False):
            risk_factors.append("Targets specific individual")
        
        if context.get("risk_score", 0) >= 0.5:
            risk_factors.append(f"High risk score: {context.get('risk_score', 0):.2f}")
        
        if context.get("bias_score", 0) > 0.1:
            risk_factors.append(f"Potential bias detected: {context.get('bias_score', 0):.2f}")
        
        for evaluation in triggered_rules:
            if evaluation.rule.layer in [ConstitutionalLayer.FEDERAL_CONSTITUTIONAL, ConstitutionalLayer.STATE_CONSTITUTIONAL]:
                risk_factors.append(f"Constitutional concern: {evaluation.rule.name}")
        
        return risk_factors
    
    def get_rule(self, rule_id: str) -> Optional[ConstitutionalRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)
    
    def get_rules_by_layer(self, layer: ConstitutionalLayer) -> List[ConstitutionalRule]:
        """Get all rules for a specific layer."""
        rule_ids = self._rules_by_layer.get(layer, [])
        return [self._rules[rid] for rid in rule_ids if rid in self._rules]
    
    def get_rules_by_category(self, category: ActionCategory) -> List[ConstitutionalRule]:
        """Get all rules for a specific action category."""
        rule_ids = self._rules_by_category.get(category, [])
        return [self._rules[rid] for rid in rule_ids if rid in self._rules]
    
    def get_all_rules(self) -> List[ConstitutionalRule]:
        """Get all rules."""
        return list(self._rules.values())
    
    def get_constitution_hierarchy(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the full constitution hierarchy."""
        hierarchy = {}
        for layer in ConstitutionalLayer:
            rules = self.get_rules_by_layer(layer)
            hierarchy[layer.name] = [r.to_dict() for r in rules]
        return hierarchy
    
    def get_decision(self, decision_id: str) -> Optional[ValidationDecision]:
        """Get a decision by ID."""
        for decision in self._decision_history:
            if decision.decision_id == decision_id:
                return decision
        return None
    
    def get_decision_history(
        self,
        limit: int = 100,
        result_filter: Optional[ValidationResult] = None,
    ) -> List[ValidationDecision]:
        """Get decision history with optional filtering."""
        decisions = self._decision_history[-limit:]
        if result_filter:
            decisions = [d for d in decisions if d.result == result_filter]
        return decisions
    
    def _log_audit(self, event_type: str, entity_id: str, data: Dict[str, Any]):
        """Log an audit event."""
        self._audit_log.append({
            "event_type": event_type,
            "entity_id": entity_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the audit log."""
        return self._audit_log[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get constitution engine statistics."""
        return {
            "total_rules": len(self._rules),
            "rules_by_layer": {
                layer.name: len(ids) for layer, ids in self._rules_by_layer.items()
            },
            "rules_by_category": {
                cat.value: len(ids) for cat, ids in self._rules_by_category.items()
            },
            "total_decisions": len(self._decision_history),
            "decisions_by_result": {
                result.value: len([d for d in self._decision_history if d.result == result])
                for result in ValidationResult
            },
        }


# Singleton accessor
_constitution_engine_instance: Optional[AIConstitutionEngine] = None


def get_constitution_engine() -> AIConstitutionEngine:
    """Get the singleton AIConstitutionEngine instance."""
    global _constitution_engine_instance
    if _constitution_engine_instance is None:
        _constitution_engine_instance = AIConstitutionEngine()
    return _constitution_engine_instance
