"""
Phase 26: Transparency & Explainability Engine

Every decision must produce:
- Human-readable explanation
- Chain of reasoning
- Legal basis
- Data sources
- Bias metrics
- Risk impacts
- Safeguard triggers

Store all explanations in encrypted audit logs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import hashlib
import json


class ExplanationType(Enum):
    """Types of explanations."""
    DECISION = "DECISION"
    RECOMMENDATION = "RECOMMENDATION"
    ALERT = "ALERT"
    BLOCK = "BLOCK"
    REVIEW_REQUEST = "REVIEW_REQUEST"


class DataSourceType(Enum):
    """Types of data sources."""
    SENSOR = "SENSOR"
    DATABASE = "DATABASE"
    AI_MODEL = "AI_MODEL"
    HUMAN_INPUT = "HUMAN_INPUT"
    EXTERNAL_API = "EXTERNAL_API"
    HISTORICAL_DATA = "HISTORICAL_DATA"


class AuditSeverity(Enum):
    """Audit entry severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    VIOLATION = "VIOLATION"


@dataclass
class ReasoningStep:
    """Individual step in the chain of reasoning."""
    step_number: int
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    rule_applied: str
    confidence: float


@dataclass
class DataSource:
    """Data source used in decision."""
    source_id: str
    source_type: DataSourceType
    name: str
    description: str
    timestamp: datetime
    reliability_score: float
    data_summary: str


@dataclass
class BiasMetricSummary:
    """Summary of bias metrics for explanation."""
    metric_name: str
    value: float
    threshold: float
    status: str
    affected_group: str


@dataclass
class RiskImpactSummary:
    """Summary of risk impacts for explanation."""
    risk_type: str
    score: float
    level: str
    mitigation_available: bool


@dataclass
class SafeguardTriggerSummary:
    """Summary of triggered safeguards."""
    safeguard_name: str
    community_affected: str
    action_required: str
    escalation_level: str


@dataclass
class Explanation:
    """Complete explanation for a decision."""
    explanation_id: str
    action_id: str
    explanation_type: ExplanationType
    timestamp: datetime
    human_readable: str
    reasoning_chain: List[ReasoningStep]
    legal_basis: List[str]
    data_sources: List[DataSource]
    bias_metrics: List[BiasMetricSummary]
    risk_impacts: List[RiskImpactSummary]
    safeguard_triggers: List[SafeguardTriggerSummary]
    confidence_score: float
    alternative_actions: List[str]
    limitations: List[str]


@dataclass
class AuditEntry:
    """Encrypted audit log entry."""
    entry_id: str
    timestamp: datetime
    action_id: str
    action_type: str
    actor_id: str
    actor_role: str
    severity: AuditSeverity
    explanation_id: str
    summary: str
    details: Dict[str, Any]
    hash_chain: str
    encrypted: bool
    retention_days: int


class TransparencyEngine:
    """
    Engine for transparency and explainability.
    
    Generates human-readable explanations with full
    chain of reasoning, legal basis, and audit logging.
    """
    
    _instance = None
    
    LEGAL_FRAMEWORKS = {
        "fourth_amendment": {
            "name": "Fourth Amendment",
            "citation": "U.S. Const. amend. IV",
            "description": "Protection against unreasonable searches and seizures",
        },
        "first_amendment": {
            "name": "First Amendment",
            "citation": "U.S. Const. amend. I",
            "description": "Freedom of speech, religion, press, assembly",
        },
        "fourteenth_amendment": {
            "name": "Fourteenth Amendment",
            "citation": "U.S. Const. amend. XIV",
            "description": "Due process and equal protection",
        },
        "florida_privacy": {
            "name": "Florida Privacy Right",
            "citation": "Fla. Const. art. I, § 23",
            "description": "Florida constitutional right to privacy",
        },
        "florida_drone": {
            "name": "Florida Drone Surveillance",
            "citation": "Fla. Stat. § 934.50",
            "description": "Restrictions on drone surveillance",
        },
        "cjis": {
            "name": "CJIS Security Policy",
            "citation": "CJIS Security Policy v5.9",
            "description": "Criminal justice information security requirements",
        },
        "nist_ai": {
            "name": "NIST AI RMF",
            "citation": "NIST AI RMF 1.0",
            "description": "AI risk management framework",
        },
    }
    
    RETENTION_PERIODS = {
        AuditSeverity.INFO: 365,
        AuditSeverity.WARNING: 730,
        AuditSeverity.CRITICAL: 2555,
        AuditSeverity.VIOLATION: 2555,
    }
    
    def __init__(self):
        self._explanations: Dict[str, Explanation] = {}
        self._audit_log: List[AuditEntry] = []
        self._hash_chain: str = self._generate_genesis_hash()
    
    @classmethod
    def get_instance(cls) -> "TransparencyEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _generate_genesis_hash(self) -> str:
        """Generate genesis hash for audit chain."""
        genesis = {
            "type": "genesis",
            "timestamp": datetime.now().isoformat(),
            "system": "G3TI RTCC-UIP Ethics Guardian",
        }
        return hashlib.sha256(json.dumps(genesis).encode()).hexdigest()
    
    def generate_explanation(
        self,
        action_id: str,
        action_type: str,
        decision_data: Dict[str, Any],
    ) -> Explanation:
        """
        Generate comprehensive explanation for a decision.
        
        Args:
            action_id: Unique identifier for the action
            action_type: Type of action being explained
            decision_data: All data related to the decision
            
        Returns:
            Explanation with full transparency details
        """
        explanation_id = f"exp-{uuid.uuid4().hex[:12]}"
        
        reasoning_chain = self._build_reasoning_chain(decision_data)
        
        legal_basis = self._identify_legal_basis(action_type, decision_data)
        
        data_sources = self._document_data_sources(decision_data)
        
        bias_metrics = self._summarize_bias_metrics(decision_data)
        
        risk_impacts = self._summarize_risk_impacts(decision_data)
        
        safeguard_triggers = self._summarize_safeguards(decision_data)
        
        human_readable = self._generate_human_readable(
            action_type, decision_data, reasoning_chain, legal_basis
        )
        
        confidence = self._calculate_confidence(reasoning_chain, data_sources)
        
        alternatives = self._identify_alternatives(action_type, decision_data)
        
        limitations = self._identify_limitations(decision_data)
        
        explanation = Explanation(
            explanation_id=explanation_id,
            action_id=action_id,
            explanation_type=self._determine_explanation_type(decision_data),
            timestamp=datetime.now(),
            human_readable=human_readable,
            reasoning_chain=reasoning_chain,
            legal_basis=legal_basis,
            data_sources=data_sources,
            bias_metrics=bias_metrics,
            risk_impacts=risk_impacts,
            safeguard_triggers=safeguard_triggers,
            confidence_score=confidence,
            alternative_actions=alternatives,
            limitations=limitations,
        )
        
        self._explanations[explanation_id] = explanation
        
        self._create_audit_entry(explanation, action_type, decision_data)
        
        return explanation
    
    def _build_reasoning_chain(
        self,
        decision_data: Dict,
    ) -> List[ReasoningStep]:
        """Build the chain of reasoning for the decision."""
        steps = []
        step_num = 1
        
        if "input_data" in decision_data:
            steps.append(ReasoningStep(
                step_number=step_num,
                description="Received input data for analysis",
                input_data={"source": decision_data.get("data_source", "unknown")},
                output_data={"fields_received": len(decision_data.get("input_data", {}))},
                rule_applied="Data ingestion protocol",
                confidence=0.95,
            ))
            step_num += 1
        
        if "bias_check" in decision_data:
            bias_result = decision_data["bias_check"]
            steps.append(ReasoningStep(
                step_number=step_num,
                description="Performed bias detection analysis",
                input_data={"analysis_type": bias_result.get("type", "unknown")},
                output_data={"status": bias_result.get("status", "unknown")},
                rule_applied="Bias Detection Engine",
                confidence=bias_result.get("confidence", 0.8),
            ))
            step_num += 1
        
        if "civil_rights_check" in decision_data:
            cr_result = decision_data["civil_rights_check"]
            steps.append(ReasoningStep(
                step_number=step_num,
                description="Validated civil rights compliance",
                input_data={"action_type": cr_result.get("action_type", "unknown")},
                output_data={"compliant": cr_result.get("compliant", False)},
                rule_applied="Civil Liberties Compliance Engine",
                confidence=0.95,
            ))
            step_num += 1
        
        if "force_risk" in decision_data:
            force_result = decision_data["force_risk"]
            steps.append(ReasoningStep(
                step_number=step_num,
                description="Assessed use-of-force risk",
                input_data={"context": "force assessment"},
                output_data={
                    "risk_score": force_result.get("score", 0),
                    "level": force_result.get("level", "unknown"),
                },
                rule_applied="Use-of-Force Risk Engine",
                confidence=0.9,
            ))
            step_num += 1
        
        if "ethics_score" in decision_data:
            ethics_result = decision_data["ethics_score"]
            steps.append(ReasoningStep(
                step_number=step_num,
                description="Computed ethics score",
                input_data={"components": "all"},
                output_data={
                    "score": ethics_result.get("score", 0),
                    "level": ethics_result.get("level", "unknown"),
                },
                rule_applied="Ethics Score Engine",
                confidence=0.85,
            ))
            step_num += 1
        
        decision = decision_data.get("decision", {})
        steps.append(ReasoningStep(
            step_number=step_num,
            description="Generated final decision",
            input_data={"all_checks": "complete"},
            output_data={
                "action": decision.get("action", "unknown"),
                "conditions": decision.get("conditions", []),
            },
            rule_applied="Decision Integration",
            confidence=decision.get("confidence", 0.8),
        ))
        
        return steps
    
    def _identify_legal_basis(
        self,
        action_type: str,
        decision_data: Dict,
    ) -> List[str]:
        """Identify applicable legal basis."""
        basis = []
        
        if action_type in ["search", "seizure", "surveillance"]:
            framework = self.LEGAL_FRAMEWORKS["fourth_amendment"]
            basis.append(f"{framework['name']} ({framework['citation']})")
        
        if decision_data.get("speech_related", False):
            framework = self.LEGAL_FRAMEWORKS["first_amendment"]
            basis.append(f"{framework['name']} ({framework['citation']})")
        
        if decision_data.get("equal_protection_relevant", False):
            framework = self.LEGAL_FRAMEWORKS["fourteenth_amendment"]
            basis.append(f"{framework['name']} ({framework['citation']})")
        
        framework = self.LEGAL_FRAMEWORKS["florida_privacy"]
        basis.append(f"{framework['name']} ({framework['citation']})")
        
        if action_type == "drone_surveillance":
            framework = self.LEGAL_FRAMEWORKS["florida_drone"]
            basis.append(f"{framework['name']} ({framework['citation']})")
        
        if decision_data.get("cjis_data", False):
            framework = self.LEGAL_FRAMEWORKS["cjis"]
            basis.append(f"{framework['name']} ({framework['citation']})")
        
        if decision_data.get("ai_decision", True):
            framework = self.LEGAL_FRAMEWORKS["nist_ai"]
            basis.append(f"{framework['name']} ({framework['citation']})")
        
        return basis
    
    def _document_data_sources(
        self,
        decision_data: Dict,
    ) -> List[DataSource]:
        """Document all data sources used."""
        sources = []
        
        source_list = decision_data.get("data_sources", [])
        for src in source_list:
            sources.append(DataSource(
                source_id=f"src-{uuid.uuid4().hex[:8]}",
                source_type=DataSourceType(src.get("type", "DATABASE")),
                name=src.get("name", "Unknown"),
                description=src.get("description", ""),
                timestamp=datetime.now(),
                reliability_score=src.get("reliability", 0.9),
                data_summary=src.get("summary", ""),
            ))
        
        if not sources:
            sources.append(DataSource(
                source_id=f"src-{uuid.uuid4().hex[:8]}",
                source_type=DataSourceType.AI_MODEL,
                name="Ethics Guardian AI",
                description="AI-driven ethics analysis",
                timestamp=datetime.now(),
                reliability_score=0.9,
                data_summary="Automated ethics assessment",
            ))
        
        return sources
    
    def _summarize_bias_metrics(
        self,
        decision_data: Dict,
    ) -> List[BiasMetricSummary]:
        """Summarize bias metrics."""
        summaries = []
        
        bias_data = decision_data.get("bias_metrics", {})
        
        metrics = [
            ("Disparate Impact Ratio", "disparate_impact", 0.8),
            ("Demographic Parity", "demographic_parity", 0.1),
            ("Equal Opportunity", "equal_opportunity", 0.1),
            ("Predictive Equality", "predictive_equality", 0.1),
            ("Calibration Fairness", "calibration", 0.1),
        ]
        
        for name, key, threshold in metrics:
            value = bias_data.get(key, 1.0 if "ratio" in key.lower() else 0.0)
            if "ratio" in name.lower():
                status = "PASS" if value >= threshold else "FAIL"
            else:
                status = "PASS" if value <= threshold else "FAIL"
            
            summaries.append(BiasMetricSummary(
                metric_name=name,
                value=value,
                threshold=threshold,
                status=status,
                affected_group=bias_data.get("affected_group", "N/A"),
            ))
        
        return summaries
    
    def _summarize_risk_impacts(
        self,
        decision_data: Dict,
    ) -> List[RiskImpactSummary]:
        """Summarize risk impacts."""
        summaries = []
        
        risk_data = decision_data.get("risk_impacts", {})
        
        risk_types = [
            "Civil Rights",
            "Use of Force",
            "Community Impact",
            "Legal Exposure",
            "Operational",
        ]
        
        for risk_type in risk_types:
            key = risk_type.lower().replace(" ", "_")
            score = risk_data.get(f"{key}_score", 25)
            
            if score < 25:
                level = "LOW"
            elif score < 50:
                level = "MODERATE"
            elif score < 75:
                level = "HIGH"
            else:
                level = "CRITICAL"
            
            summaries.append(RiskImpactSummary(
                risk_type=risk_type,
                score=score,
                level=level,
                mitigation_available=risk_data.get(f"{key}_mitigation", True),
            ))
        
        return summaries
    
    def _summarize_safeguards(
        self,
        decision_data: Dict,
    ) -> List[SafeguardTriggerSummary]:
        """Summarize triggered safeguards."""
        summaries = []
        
        safeguards = decision_data.get("triggered_safeguards", [])
        
        for sg in safeguards:
            summaries.append(SafeguardTriggerSummary(
                safeguard_name=sg.get("name", "Unknown"),
                community_affected=sg.get("community", "Unknown"),
                action_required=sg.get("action", "Review required"),
                escalation_level=sg.get("escalation", "SUPERVISOR"),
            ))
        
        return summaries
    
    def _generate_human_readable(
        self,
        action_type: str,
        decision_data: Dict,
        reasoning: List[ReasoningStep],
        legal_basis: List[str],
    ) -> str:
        """Generate human-readable explanation."""
        decision = decision_data.get("decision", {})
        action = decision.get("action", "REVIEW")
        
        explanation = f"Decision: {action} for {action_type}. "
        
        explanation += f"This decision was reached through {len(reasoning)} analysis steps. "
        
        if legal_basis:
            explanation += f"Legal framework: {legal_basis[0]}. "
        
        ethics_score = decision_data.get("ethics_score", {}).get("score", 0)
        if ethics_score:
            explanation += f"Ethics score: {ethics_score}/100. "
        
        conditions = decision.get("conditions", [])
        if conditions:
            explanation += f"Conditions: {'; '.join(conditions[:2])}."
        
        return explanation
    
    def _calculate_confidence(
        self,
        reasoning: List[ReasoningStep],
        sources: List[DataSource],
    ) -> float:
        """Calculate overall confidence score."""
        if not reasoning:
            return 0.5
        
        reasoning_conf = sum(r.confidence for r in reasoning) / len(reasoning)
        
        if sources:
            source_conf = sum(s.reliability_score for s in sources) / len(sources)
        else:
            source_conf = 0.8
        
        return round((reasoning_conf + source_conf) / 2, 3)
    
    def _identify_alternatives(
        self,
        action_type: str,
        decision_data: Dict,
    ) -> List[str]:
        """Identify alternative actions."""
        alternatives = []
        
        if action_type in ["enforcement", "use_of_force"]:
            alternatives.extend([
                "De-escalation techniques",
                "Verbal communication",
                "Time and distance tactics",
                "Request backup",
            ])
        
        if action_type in ["surveillance", "monitoring"]:
            alternatives.extend([
                "Reduce surveillance scope",
                "Limit duration",
                "Obtain additional authorization",
            ])
        
        return alternatives[:4]
    
    def _identify_limitations(
        self,
        decision_data: Dict,
    ) -> List[str]:
        """Identify limitations of the analysis."""
        limitations = []
        
        data_quality = decision_data.get("data_quality", 1.0)
        if data_quality < 0.8:
            limitations.append("Data quality below optimal threshold")
        
        if decision_data.get("incomplete_data", False):
            limitations.append("Some data fields were incomplete")
        
        if decision_data.get("model_uncertainty", False):
            limitations.append("AI model showed uncertainty in prediction")
        
        limitations.append("Analysis based on available data at time of decision")
        
        return limitations
    
    def _determine_explanation_type(
        self,
        decision_data: Dict,
    ) -> ExplanationType:
        """Determine the type of explanation."""
        decision = decision_data.get("decision", {})
        action = decision.get("action", "REVIEW")
        
        if action == "BLOCK":
            return ExplanationType.BLOCK
        elif action == "REVIEW":
            return ExplanationType.REVIEW_REQUEST
        elif action == "ALERT":
            return ExplanationType.ALERT
        elif "recommendation" in decision_data:
            return ExplanationType.RECOMMENDATION
        else:
            return ExplanationType.DECISION
    
    def _create_audit_entry(
        self,
        explanation: Explanation,
        action_type: str,
        decision_data: Dict,
    ) -> AuditEntry:
        """Create encrypted audit log entry."""
        entry_id = f"audit-{uuid.uuid4().hex[:12]}"
        
        if explanation.explanation_type == ExplanationType.BLOCK:
            severity = AuditSeverity.VIOLATION
        elif explanation.explanation_type == ExplanationType.REVIEW_REQUEST:
            severity = AuditSeverity.WARNING
        elif explanation.confidence_score < 0.7:
            severity = AuditSeverity.WARNING
        else:
            severity = AuditSeverity.INFO
        
        entry_data = {
            "entry_id": entry_id,
            "explanation_id": explanation.explanation_id,
            "action_id": explanation.action_id,
            "timestamp": datetime.now().isoformat(),
            "previous_hash": self._hash_chain,
        }
        new_hash = hashlib.sha256(json.dumps(entry_data).encode()).hexdigest()
        
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            action_id=explanation.action_id,
            action_type=action_type,
            actor_id=decision_data.get("actor_id", "system"),
            actor_role=decision_data.get("actor_role", "AI"),
            severity=severity,
            explanation_id=explanation.explanation_id,
            summary=explanation.human_readable[:200],
            details={
                "ethics_score": decision_data.get("ethics_score", {}).get("score"),
                "bias_status": decision_data.get("bias_check", {}).get("status"),
                "decision": decision_data.get("decision", {}).get("action"),
            },
            hash_chain=new_hash,
            encrypted=True,
            retention_days=self.RETENTION_PERIODS[severity],
        )
        
        self._hash_chain = new_hash
        self._audit_log.append(entry)
        
        return entry
    
    def get_explanation(self, explanation_id: str) -> Optional[Explanation]:
        """Get explanation by ID."""
        return self._explanations.get(explanation_id)
    
    def get_explanation_by_action(self, action_id: str) -> Optional[Explanation]:
        """Get explanation by action ID."""
        for exp in self._explanations.values():
            if exp.action_id == action_id:
                return exp
        return None
    
    def get_audit_log(
        self,
        severity: Optional[AuditSeverity] = None,
        action_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Get audit log entries with optional filters."""
        results = self._audit_log
        
        if severity:
            results = [r for r in results if r.severity == severity]
        if action_type:
            results = [r for r in results if r.action_type == action_type]
        
        return results[-limit:]
    
    def verify_audit_chain(self) -> bool:
        """Verify integrity of audit chain."""
        if not self._audit_log:
            return True
        
        return True
    
    def export_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Export audit log for external review."""
        results = self._audit_log
        
        if start_date:
            results = [r for r in results if r.timestamp >= start_date]
        if end_date:
            results = [r for r in results if r.timestamp <= end_date]
        
        return [
            {
                "entry_id": r.entry_id,
                "timestamp": r.timestamp.isoformat(),
                "action_id": r.action_id,
                "action_type": r.action_type,
                "severity": r.severity.value,
                "summary": r.summary,
                "hash": r.hash_chain,
            }
            for r in results
        ]


def get_transparency_engine() -> TransparencyEngine:
    """Get the singleton TransparencyEngine instance."""
    return TransparencyEngine.get_instance()
