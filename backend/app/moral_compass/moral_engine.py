"""
Moral Compass Core Engine

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Core ethical reasoning model for all AI systems in the RTCC-UIP ecosystem.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class MoralDecisionType(Enum):
    """Types of moral decisions."""
    ALLOW = "allow"
    ALLOW_WITH_CAUTION = "allow_with_caution"
    HUMAN_APPROVAL_NEEDED = "human_approval_needed"
    DENY = "deny"


class EthicalPrinciple(Enum):
    """Core ethical principles."""
    BENEFICENCE = "beneficence"
    NON_MALEFICENCE = "non_maleficence"
    AUTONOMY = "autonomy"
    JUSTICE = "justice"
    DIGNITY = "dignity"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    PROPORTIONALITY = "proportionality"


class HarmLevel(Enum):
    """Levels of potential harm."""
    NONE = "none"
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class RiskCategory(Enum):
    """Categories of risk."""
    PHYSICAL = "physical"
    PSYCHOLOGICAL = "psychological"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"
    LEGAL = "legal"
    CIVIL_RIGHTS = "civil_rights"
    COMMUNITY = "community"
    INSTITUTIONAL = "institutional"


class LegalFramework(Enum):
    """Legal frameworks for compliance."""
    FEDERAL_LAW = "federal_law"
    FLORIDA_STATE_LAW = "florida_state_law"
    RBPD_POLICY = "rbpd_policy"
    CONSTITUTIONAL = "constitutional"
    HUMAN_RIGHTS = "human_rights"
    LOCAL_ORDINANCE = "local_ordinance"


@dataclass
class ReasoningStep:
    """A single step in the moral reasoning chain."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    step_number: int = 0
    principle: EthicalPrinciple = EthicalPrinciple.JUSTICE
    consideration: str = ""
    weight: float = 1.0
    outcome: str = ""
    supporting_factors: List[str] = field(default_factory=list)
    opposing_factors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_number": self.step_number,
            "principle": self.principle.value,
            "consideration": self.consideration,
            "weight": self.weight,
            "outcome": self.outcome,
            "supporting_factors": self.supporting_factors,
            "opposing_factors": self.opposing_factors,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReasoningChain:
    """Complete chain of moral reasoning."""
    chain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: List[ReasoningStep] = field(default_factory=list)
    final_conclusion: str = ""
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    chain_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_hash:
            self.chain_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        content = f"{self.chain_id}:{len(self.steps)}:{self.final_conclusion}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def add_step(self, step: ReasoningStep) -> None:
        step.step_number = len(self.steps) + 1
        self.steps.append(step)
        self.chain_hash = self._compute_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "steps": [s.to_dict() for s in self.steps],
            "final_conclusion": self.final_conclusion,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "chain_hash": self.chain_hash,
        }


@dataclass
class HarmAssessment:
    """Assessment of potential harm."""
    harm_level: HarmLevel = HarmLevel.NONE
    risk_categories: List[RiskCategory] = field(default_factory=list)
    affected_parties: List[str] = field(default_factory=list)
    mitigation_possible: bool = True
    mitigation_strategies: List[str] = field(default_factory=list)
    reversibility: str = "reversible"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "harm_level": self.harm_level.value,
            "risk_categories": [r.value for r in self.risk_categories],
            "affected_parties": self.affected_parties,
            "mitigation_possible": self.mitigation_possible,
            "mitigation_strategies": self.mitigation_strategies,
            "reversibility": self.reversibility,
        }


@dataclass
class LegalCompliance:
    """Legal compliance assessment."""
    framework: LegalFramework = LegalFramework.FEDERAL_LAW
    compliant: bool = True
    relevant_laws: List[str] = field(default_factory=list)
    potential_violations: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "framework": self.framework.value,
            "compliant": self.compliant,
            "relevant_laws": self.relevant_laws,
            "potential_violations": self.potential_violations,
            "notes": self.notes,
        }


@dataclass
class MoralAssessment:
    """Complete moral assessment of an action."""
    assessment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = ""
    action_description: str = ""
    requester_id: str = ""
    decision: MoralDecisionType = MoralDecisionType.ALLOW
    reasoning_chain: ReasoningChain = field(default_factory=ReasoningChain)
    harm_assessment: HarmAssessment = field(default_factory=HarmAssessment)
    legal_compliance: List[LegalCompliance] = field(default_factory=list)
    principles_evaluated: List[EthicalPrinciple] = field(default_factory=list)
    community_impact_score: float = 0.0
    risk_to_community: float = 0.0
    required_approvals: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    assessment_hash: str = ""
    
    def __post_init__(self):
        if not self.assessment_hash:
            self.assessment_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        content = f"{self.assessment_id}:{self.action_type}:{self.decision.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "action_type": self.action_type,
            "action_description": self.action_description,
            "requester_id": self.requester_id,
            "decision": self.decision.value,
            "reasoning_chain": self.reasoning_chain.to_dict(),
            "harm_assessment": self.harm_assessment.to_dict(),
            "legal_compliance": [lc.to_dict() for lc in self.legal_compliance],
            "principles_evaluated": [p.value for p in self.principles_evaluated],
            "community_impact_score": self.community_impact_score,
            "risk_to_community": self.risk_to_community,
            "required_approvals": self.required_approvals,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat(),
            "assessment_hash": self.assessment_hash,
        }


@dataclass
class MoralDecision:
    """Final moral decision with full context."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: MoralDecisionType = MoralDecisionType.ALLOW
    assessment: MoralAssessment = field(default_factory=MoralAssessment)
    explanation: str = ""
    confidence: float = 0.0
    alternatives: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "assessment": self.assessment.to_dict(),
            "explanation": self.explanation,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
            "created_at": self.created_at.isoformat(),
        }


class MoralEngine:
    """
    Core Moral Compass Engine.
    
    Provides ethical reasoning for all AI systems in the RTCC-UIP ecosystem.
    Ensures constitutional compliance, non-discrimination, bias prevention,
    and community trust alignment.
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
        self.assessments: Dict[str, MoralAssessment] = {}
        self.decisions: Dict[str, MoralDecision] = {}
        self.statistics = {
            "total_assessments": 0,
            "allowed": 0,
            "allowed_with_caution": 0,
            "human_approval_needed": 0,
            "denied": 0,
        }
        
        self._legal_rules = self._initialize_legal_rules()
        self._ethical_principles = self._initialize_ethical_principles()
        self._harm_thresholds = self._initialize_harm_thresholds()
        self._high_risk_actions = self._initialize_high_risk_actions()
    
    def _initialize_legal_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize legal compliance rules."""
        return {
            "4th_amendment": {
                "framework": LegalFramework.CONSTITUTIONAL,
                "description": "Protection against unreasonable searches and seizures",
                "triggers": ["search", "seizure", "surveillance", "tracking"],
                "requirements": ["warrant", "probable_cause", "consent"],
            },
            "5th_amendment": {
                "framework": LegalFramework.CONSTITUTIONAL,
                "description": "Due process and self-incrimination protection",
                "triggers": ["interrogation", "questioning", "detention"],
                "requirements": ["miranda_rights", "due_process"],
            },
            "14th_amendment": {
                "framework": LegalFramework.CONSTITUTIONAL,
                "description": "Equal protection under the law",
                "triggers": ["profiling", "discrimination", "targeting"],
                "requirements": ["equal_treatment", "no_profiling"],
            },
            "florida_use_of_force": {
                "framework": LegalFramework.FLORIDA_STATE_LAW,
                "description": "Florida use of force guidelines",
                "triggers": ["force", "restraint", "weapon"],
                "requirements": ["proportionality", "necessity", "documentation"],
            },
            "rbpd_pursuit_policy": {
                "framework": LegalFramework.RBPD_POLICY,
                "description": "RBPD vehicle pursuit policy",
                "triggers": ["pursuit", "chase", "vehicle_follow"],
                "requirements": ["supervisor_approval", "risk_assessment"],
            },
            "youth_protection": {
                "framework": LegalFramework.FEDERAL_LAW,
                "description": "Juvenile justice and protection laws",
                "triggers": ["minor", "juvenile", "youth", "child"],
                "requirements": ["guardian_notification", "special_handling"],
            },
            "vulnerable_population": {
                "framework": LegalFramework.HUMAN_RIGHTS,
                "description": "Protection for vulnerable populations",
                "triggers": ["elderly", "disabled", "mental_health", "homeless"],
                "requirements": ["specialized_response", "dignity_preservation"],
            },
        }
    
    def _initialize_ethical_principles(self) -> Dict[EthicalPrinciple, Dict[str, Any]]:
        """Initialize ethical principle definitions."""
        return {
            EthicalPrinciple.BENEFICENCE: {
                "description": "Act in the best interest of individuals and community",
                "weight": 1.0,
                "considerations": ["public_safety", "community_welfare", "individual_wellbeing"],
            },
            EthicalPrinciple.NON_MALEFICENCE: {
                "description": "Do no harm",
                "weight": 1.2,
                "considerations": ["physical_harm", "psychological_harm", "social_harm"],
            },
            EthicalPrinciple.AUTONOMY: {
                "description": "Respect individual autonomy and rights",
                "weight": 1.0,
                "considerations": ["consent", "choice", "self_determination"],
            },
            EthicalPrinciple.JUSTICE: {
                "description": "Fair and equal treatment",
                "weight": 1.1,
                "considerations": ["fairness", "equality", "non_discrimination"],
            },
            EthicalPrinciple.DIGNITY: {
                "description": "Preserve human dignity",
                "weight": 1.0,
                "considerations": ["respect", "privacy", "humane_treatment"],
            },
            EthicalPrinciple.TRANSPARENCY: {
                "description": "Be transparent in actions and reasoning",
                "weight": 0.9,
                "considerations": ["explainability", "accountability", "openness"],
            },
            EthicalPrinciple.ACCOUNTABILITY: {
                "description": "Take responsibility for actions",
                "weight": 1.0,
                "considerations": ["documentation", "oversight", "review"],
            },
            EthicalPrinciple.PRIVACY: {
                "description": "Protect individual privacy",
                "weight": 1.0,
                "considerations": ["data_protection", "surveillance_limits", "information_security"],
            },
            EthicalPrinciple.FAIRNESS: {
                "description": "Ensure fair outcomes",
                "weight": 1.1,
                "considerations": ["bias_prevention", "equal_opportunity", "proportionality"],
            },
            EthicalPrinciple.PROPORTIONALITY: {
                "description": "Response proportional to situation",
                "weight": 1.0,
                "considerations": ["necessity", "minimum_force", "appropriate_response"],
            },
        }
    
    def _initialize_harm_thresholds(self) -> Dict[HarmLevel, float]:
        """Initialize harm level thresholds."""
        return {
            HarmLevel.NONE: 0.0,
            HarmLevel.MINIMAL: 0.1,
            HarmLevel.LOW: 0.25,
            HarmLevel.MODERATE: 0.5,
            HarmLevel.HIGH: 0.75,
            HarmLevel.SEVERE: 0.9,
            HarmLevel.CATASTROPHIC: 1.0,
        }
    
    def _initialize_high_risk_actions(self) -> List[str]:
        """Initialize list of high-risk action types."""
        return [
            "use_of_force",
            "vehicle_pursuit",
            "warrantless_search",
            "detention",
            "arrest",
            "drone_surveillance",
            "facial_recognition",
            "predictive_targeting",
            "autonomous_response",
            "weapon_deployment",
            "crowd_control",
            "emergency_override",
        ]
    
    def assess(
        self,
        action_type: str,
        action_description: str,
        requester_id: str,
        context: Optional[Dict[str, Any]] = None,
        cultural_context: Optional[Dict[str, Any]] = None,
    ) -> MoralAssessment:
        """
        Perform comprehensive moral assessment of an action.
        
        Args:
            action_type: Type of action being assessed
            action_description: Description of the action
            requester_id: ID of the entity requesting the action
            context: Additional context for the assessment
            cultural_context: Cultural and community context
        
        Returns:
            MoralAssessment with decision and reasoning
        """
        context = context or {}
        cultural_context = cultural_context or {}
        
        assessment = MoralAssessment(
            action_type=action_type,
            action_description=action_description,
            requester_id=requester_id,
        )
        
        legal_compliance = self._check_legal_compliance(action_type, context)
        assessment.legal_compliance = legal_compliance
        
        harm_assessment = self._assess_harm(action_type, context)
        assessment.harm_assessment = harm_assessment
        
        reasoning_chain = self._build_reasoning_chain(
            action_type, context, legal_compliance, harm_assessment
        )
        assessment.reasoning_chain = reasoning_chain
        
        assessment.principles_evaluated = list(self._ethical_principles.keys())
        
        assessment.community_impact_score = self._calculate_community_impact(
            action_type, context, cultural_context
        )
        assessment.risk_to_community = self._calculate_community_risk(
            harm_assessment, cultural_context
        )
        
        decision, required_approvals, conditions = self._make_decision(
            action_type, legal_compliance, harm_assessment, reasoning_chain, context
        )
        assessment.decision = decision
        assessment.required_approvals = required_approvals
        assessment.conditions = conditions
        
        assessment.assessment_hash = assessment._compute_hash()
        
        self.assessments[assessment.assessment_id] = assessment
        self._update_statistics(decision)
        
        return assessment
    
    def _check_legal_compliance(
        self,
        action_type: str,
        context: Dict[str, Any],
    ) -> List[LegalCompliance]:
        """Check action against legal frameworks."""
        compliance_results = []
        
        for rule_id, rule in self._legal_rules.items():
            triggered = any(
                trigger in action_type.lower() or trigger in str(context).lower()
                for trigger in rule["triggers"]
            )
            
            if triggered:
                compliant = True
                violations = []
                
                for req in rule["requirements"]:
                    if not context.get(req, False):
                        if context.get("override_" + req, False):
                            continue
                        compliant = False
                        violations.append(f"Missing requirement: {req}")
                
                compliance_results.append(LegalCompliance(
                    framework=rule["framework"],
                    compliant=compliant,
                    relevant_laws=[rule_id],
                    potential_violations=violations,
                    notes=rule["description"],
                ))
        
        if not compliance_results:
            compliance_results.append(LegalCompliance(
                framework=LegalFramework.FEDERAL_LAW,
                compliant=True,
                relevant_laws=[],
                potential_violations=[],
                notes="No specific legal triggers identified",
            ))
        
        return compliance_results
    
    def _assess_harm(
        self,
        action_type: str,
        context: Dict[str, Any],
    ) -> HarmAssessment:
        """Assess potential harm from action."""
        harm_level = HarmLevel.NONE
        risk_categories = []
        affected_parties = []
        mitigation_strategies = []
        
        if action_type in self._high_risk_actions:
            harm_level = HarmLevel.HIGH
            risk_categories.append(RiskCategory.PHYSICAL)
            risk_categories.append(RiskCategory.CIVIL_RIGHTS)
        
        if "force" in action_type.lower():
            harm_level = max(harm_level, HarmLevel.HIGH, key=lambda x: self._harm_thresholds[x])
            risk_categories.append(RiskCategory.PHYSICAL)
            affected_parties.append("subject")
            mitigation_strategies.append("Use minimum necessary force")
            mitigation_strategies.append("Document all actions")
        
        if "surveillance" in action_type.lower():
            harm_level = max(harm_level, HarmLevel.MODERATE, key=lambda x: self._harm_thresholds[x])
            risk_categories.append(RiskCategory.CIVIL_RIGHTS)
            affected_parties.append("public")
            mitigation_strategies.append("Limit scope and duration")
            mitigation_strategies.append("Ensure proper authorization")
        
        if "pursuit" in action_type.lower():
            harm_level = max(harm_level, HarmLevel.HIGH, key=lambda x: self._harm_thresholds[x])
            risk_categories.append(RiskCategory.PHYSICAL)
            risk_categories.append(RiskCategory.COMMUNITY)
            affected_parties.extend(["subject", "bystanders", "officers"])
            mitigation_strategies.append("Continuous risk assessment")
            mitigation_strategies.append("Supervisor oversight")
        
        if context.get("involves_minor", False):
            harm_level = max(harm_level, HarmLevel.HIGH, key=lambda x: self._harm_thresholds[x])
            risk_categories.append(RiskCategory.PSYCHOLOGICAL)
            affected_parties.append("minor")
            mitigation_strategies.append("Specialized juvenile handling")
            mitigation_strategies.append("Guardian notification")
        
        if context.get("mental_health_crisis", False):
            harm_level = max(harm_level, HarmLevel.HIGH, key=lambda x: self._harm_thresholds[x])
            risk_categories.append(RiskCategory.PSYCHOLOGICAL)
            affected_parties.append("individual_in_crisis")
            mitigation_strategies.append("Crisis intervention training")
            mitigation_strategies.append("Mental health professional involvement")
        
        return HarmAssessment(
            harm_level=harm_level,
            risk_categories=list(set(risk_categories)),
            affected_parties=list(set(affected_parties)),
            mitigation_possible=True,
            mitigation_strategies=mitigation_strategies,
            reversibility="partially_reversible" if harm_level.value in ["high", "severe"] else "reversible",
        )
    
    def _build_reasoning_chain(
        self,
        action_type: str,
        context: Dict[str, Any],
        legal_compliance: List[LegalCompliance],
        harm_assessment: HarmAssessment,
    ) -> ReasoningChain:
        """Build the moral reasoning chain."""
        chain = ReasoningChain()
        
        chain.add_step(ReasoningStep(
            principle=EthicalPrinciple.JUSTICE,
            consideration="Legal compliance evaluation",
            weight=1.2,
            outcome="compliant" if all(lc.compliant for lc in legal_compliance) else "non_compliant",
            supporting_factors=[lc.notes for lc in legal_compliance if lc.compliant],
            opposing_factors=[v for lc in legal_compliance for v in lc.potential_violations],
        ))
        
        chain.add_step(ReasoningStep(
            principle=EthicalPrinciple.NON_MALEFICENCE,
            consideration="Harm assessment",
            weight=1.3,
            outcome=harm_assessment.harm_level.value,
            supporting_factors=harm_assessment.mitigation_strategies,
            opposing_factors=[f"Risk: {r.value}" for r in harm_assessment.risk_categories],
        ))
        
        chain.add_step(ReasoningStep(
            principle=EthicalPrinciple.BENEFICENCE,
            consideration="Public safety benefit",
            weight=1.0,
            outcome="beneficial" if context.get("public_safety_benefit", True) else "questionable",
            supporting_factors=["Serves public safety mission"] if context.get("public_safety_benefit", True) else [],
            opposing_factors=[],
        ))
        
        chain.add_step(ReasoningStep(
            principle=EthicalPrinciple.FAIRNESS,
            consideration="Equal treatment evaluation",
            weight=1.1,
            outcome="fair" if not context.get("potential_bias", False) else "requires_review",
            supporting_factors=["No bias indicators detected"] if not context.get("potential_bias", False) else [],
            opposing_factors=["Potential bias detected"] if context.get("potential_bias", False) else [],
        ))
        
        chain.add_step(ReasoningStep(
            principle=EthicalPrinciple.PROPORTIONALITY,
            consideration="Response proportionality",
            weight=1.0,
            outcome="proportional" if harm_assessment.harm_level.value in ["none", "minimal", "low"] else "review_needed",
            supporting_factors=[],
            opposing_factors=[],
        ))
        
        all_compliant = all(lc.compliant for lc in legal_compliance)
        low_harm = harm_assessment.harm_level.value in ["none", "minimal", "low"]
        
        if all_compliant and low_harm:
            chain.final_conclusion = "Action is ethically permissible"
            chain.confidence = 0.9
        elif all_compliant and not low_harm:
            chain.final_conclusion = "Action requires caution and oversight"
            chain.confidence = 0.7
        elif not all_compliant:
            chain.final_conclusion = "Action has legal/ethical concerns requiring review"
            chain.confidence = 0.5
        
        return chain
    
    def _calculate_community_impact(
        self,
        action_type: str,
        context: Dict[str, Any],
        cultural_context: Dict[str, Any],
    ) -> float:
        """Calculate community impact score (0-100)."""
        base_score = 50.0
        
        if context.get("public_safety_benefit", False):
            base_score += 20
        
        if cultural_context.get("community_event", False):
            base_score -= 10
        
        if cultural_context.get("high_trust_area", False):
            base_score += 10
        elif cultural_context.get("low_trust_area", False):
            base_score -= 15
        
        if action_type in self._high_risk_actions:
            base_score -= 20
        
        return max(0, min(100, base_score))
    
    def _calculate_community_risk(
        self,
        harm_assessment: HarmAssessment,
        cultural_context: Dict[str, Any],
    ) -> float:
        """Calculate risk to community (0-100)."""
        base_risk = self._harm_thresholds[harm_assessment.harm_level] * 100
        
        if RiskCategory.COMMUNITY in harm_assessment.risk_categories:
            base_risk += 15
        
        if cultural_context.get("vulnerable_population", False):
            base_risk += 20
        
        if cultural_context.get("historical_trauma", False):
            base_risk += 10
        
        return max(0, min(100, base_risk))
    
    def _make_decision(
        self,
        action_type: str,
        legal_compliance: List[LegalCompliance],
        harm_assessment: HarmAssessment,
        reasoning_chain: ReasoningChain,
        context: Dict[str, Any],
    ) -> Tuple[MoralDecisionType, List[str], List[str]]:
        """Make the final moral decision."""
        required_approvals = []
        conditions = []
        
        all_compliant = all(lc.compliant for lc in legal_compliance)
        
        if not all_compliant:
            for lc in legal_compliance:
                if not lc.compliant:
                    if lc.framework == LegalFramework.CONSTITUTIONAL:
                        return MoralDecisionType.DENY, [], ["Constitutional violation detected"]
                    else:
                        required_approvals.append(f"Legal review for {lc.framework.value}")
        
        if harm_assessment.harm_level == HarmLevel.CATASTROPHIC:
            return MoralDecisionType.DENY, [], ["Catastrophic harm potential"]
        
        if harm_assessment.harm_level == HarmLevel.SEVERE:
            return MoralDecisionType.HUMAN_APPROVAL_NEEDED, ["commander", "legal"], harm_assessment.mitigation_strategies
        
        if action_type in self._high_risk_actions:
            required_approvals.append("supervisor")
            conditions.extend(harm_assessment.mitigation_strategies)
            
            if harm_assessment.harm_level.value in ["high"]:
                return MoralDecisionType.HUMAN_APPROVAL_NEEDED, required_approvals, conditions
            else:
                return MoralDecisionType.ALLOW_WITH_CAUTION, required_approvals, conditions
        
        if harm_assessment.harm_level.value in ["moderate"]:
            conditions.extend(harm_assessment.mitigation_strategies)
            return MoralDecisionType.ALLOW_WITH_CAUTION, [], conditions
        
        if context.get("involves_minor", False) or context.get("mental_health_crisis", False):
            required_approvals.append("specialized_unit")
            conditions.append("Follow specialized protocols")
            return MoralDecisionType.ALLOW_WITH_CAUTION, required_approvals, conditions
        
        return MoralDecisionType.ALLOW, [], []
    
    def _update_statistics(self, decision: MoralDecisionType) -> None:
        """Update engine statistics."""
        self.statistics["total_assessments"] += 1
        
        if decision == MoralDecisionType.ALLOW:
            self.statistics["allowed"] += 1
        elif decision == MoralDecisionType.ALLOW_WITH_CAUTION:
            self.statistics["allowed_with_caution"] += 1
        elif decision == MoralDecisionType.HUMAN_APPROVAL_NEEDED:
            self.statistics["human_approval_needed"] += 1
        elif decision == MoralDecisionType.DENY:
            self.statistics["denied"] += 1
    
    def make_decision(
        self,
        action_type: str,
        action_description: str,
        requester_id: str,
        context: Optional[Dict[str, Any]] = None,
        cultural_context: Optional[Dict[str, Any]] = None,
    ) -> MoralDecision:
        """
        Make a complete moral decision with full reasoning.
        
        Args:
            action_type: Type of action
            action_description: Description of the action
            requester_id: ID of requester
            context: Additional context
            cultural_context: Cultural context
        
        Returns:
            MoralDecision with full assessment and reasoning
        """
        assessment = self.assess(
            action_type, action_description, requester_id, context, cultural_context
        )
        
        decision = MoralDecision(
            decision_type=assessment.decision,
            assessment=assessment,
            explanation=assessment.reasoning_chain.final_conclusion,
            confidence=assessment.reasoning_chain.confidence,
            alternatives=self._generate_alternatives(assessment),
        )
        
        self.decisions[decision.decision_id] = decision
        
        return decision
    
    def _generate_alternatives(self, assessment: MoralAssessment) -> List[str]:
        """Generate alternative actions if original is denied or cautioned."""
        alternatives = []
        
        if assessment.decision in [MoralDecisionType.DENY, MoralDecisionType.HUMAN_APPROVAL_NEEDED]:
            alternatives.append("Request supervisor approval before proceeding")
            alternatives.append("Consider de-escalation approach")
            alternatives.append("Gather additional information before action")
        
        if assessment.decision == MoralDecisionType.ALLOW_WITH_CAUTION:
            alternatives.append("Proceed with documented oversight")
            alternatives.append("Implement all mitigation strategies")
        
        return alternatives
    
    def veto_action(
        self,
        action_type: str,
        reason: str,
        requester_id: str,
    ) -> MoralDecision:
        """
        Veto a high-risk action.
        
        Args:
            action_type: Type of action being vetoed
            reason: Reason for veto
            requester_id: ID of requester
        
        Returns:
            MoralDecision with DENY status
        """
        assessment = MoralAssessment(
            action_type=action_type,
            action_description=f"VETOED: {reason}",
            requester_id=requester_id,
            decision=MoralDecisionType.DENY,
        )
        
        assessment.reasoning_chain.final_conclusion = f"Action vetoed: {reason}"
        assessment.reasoning_chain.confidence = 1.0
        
        self.assessments[assessment.assessment_id] = assessment
        self.statistics["denied"] += 1
        self.statistics["total_assessments"] += 1
        
        decision = MoralDecision(
            decision_type=MoralDecisionType.DENY,
            assessment=assessment,
            explanation=f"Action vetoed: {reason}",
            confidence=1.0,
            alternatives=["Seek alternative approach", "Request command review"],
        )
        
        self.decisions[decision.decision_id] = decision
        
        return decision
    
    def get_assessment(self, assessment_id: str) -> Optional[MoralAssessment]:
        """Get assessment by ID."""
        return self.assessments.get(assessment_id)
    
    def get_decision(self, decision_id: str) -> Optional[MoralDecision]:
        """Get decision by ID."""
        return self.decisions.get(decision_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            **self.statistics,
            "approval_rate": (
                (self.statistics["allowed"] + self.statistics["allowed_with_caution"]) /
                max(1, self.statistics["total_assessments"])
            ) * 100,
            "denial_rate": (
                self.statistics["denied"] / max(1, self.statistics["total_assessments"])
            ) * 100,
        }
    
    def get_audit_trail(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        requester_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get audit trail of assessments."""
        trail = []
        
        for assessment in self.assessments.values():
            if start_time and assessment.created_at < start_time:
                continue
            if end_time and assessment.created_at > end_time:
                continue
            if requester_id and assessment.requester_id != requester_id:
                continue
            
            trail.append({
                "assessment_id": assessment.assessment_id,
                "action_type": assessment.action_type,
                "decision": assessment.decision.value,
                "requester_id": assessment.requester_id,
                "created_at": assessment.created_at.isoformat(),
                "assessment_hash": assessment.assessment_hash,
            })
        
        return sorted(trail, key=lambda x: x["created_at"], reverse=True)
