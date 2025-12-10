"""
Phase 20: Case Theory Engine Module

Provides hypothesis generation, contradiction checking, evidence weighting,
and case narrative building for the Autonomous Detective AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import uuid


class HypothesisStatus(str, Enum):
    PROPOSED = "proposed"
    UNDER_INVESTIGATION = "under_investigation"
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    ELIMINATED = "eliminated"
    CONFIRMED = "confirmed"


class EvidenceStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    CONCLUSIVE = "conclusive"


class NarrativeSection(str, Enum):
    SUMMARY = "summary"
    BACKGROUND = "background"
    TIMELINE = "timeline"
    EVIDENCE_ANALYSIS = "evidence_analysis"
    SUSPECT_ANALYSIS = "suspect_analysis"
    THEORY = "theory"
    CONCLUSIONS = "conclusions"
    RECOMMENDATIONS = "recommendations"


@dataclass
class Hypothesis:
    hypothesis_id: str
    case_id: str
    title: str
    description: str
    hypothesis_type: str
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    confidence_score: float = 0.0
    supporting_evidence: List[Dict[str, Any]] = field(default_factory=list)
    contradicting_evidence: List[Dict[str, Any]] = field(default_factory=list)
    related_suspects: List[str] = field(default_factory=list)
    related_hypotheses: List[str] = field(default_factory=list)
    generated_by: str = "ada_hypothesis_generator"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    review_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Contradiction:
    contradiction_id: str
    case_id: str
    hypothesis_id: str
    contradiction_type: str
    description: str
    evidence_items: List[str] = field(default_factory=list)
    severity: str = "moderate"
    resolution_status: str = "unresolved"
    resolution_notes: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceWeight:
    weight_id: str
    case_id: str
    evidence_id: str
    suspect_id: Optional[str]
    weight_score: float
    strength: EvidenceStrength
    relevance_score: float
    reliability_score: float
    probative_value: float
    factors: List[Dict[str, Any]] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""


@dataclass
class CaseNarrative:
    narrative_id: str
    case_id: str
    title: str
    version: int = 1
    sections: Dict[str, str] = field(default_factory=dict)
    hypotheses_included: List[str] = field(default_factory=list)
    evidence_cited: List[str] = field(default_factory=list)
    suspects_discussed: List[str] = field(default_factory=list)
    word_count: int = 0
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: str = "ada_narrative_builder"
    reviewed: bool = False
    reviewer: Optional[str] = None
    review_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HypothesisGenerator:
    """Generates investigative hypotheses using AI analysis."""

    def __init__(self):
        self._hypotheses: Dict[str, Hypothesis] = {}
        self._case_hypotheses: Dict[str, List[str]] = {}

    def generate_hypotheses(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Hypothesis]:
        hypotheses = []

        suspect_hypotheses = self._generate_suspect_hypotheses(
            case_id, case_data, evidence_items, suspects or []
        )
        hypotheses.extend(suspect_hypotheses)

        motive_hypotheses = self._generate_motive_hypotheses(
            case_id, case_data, evidence_items
        )
        hypotheses.extend(motive_hypotheses)

        timeline_hypotheses = self._generate_timeline_hypotheses(
            case_id, case_data, evidence_items
        )
        hypotheses.extend(timeline_hypotheses)

        method_hypotheses = self._generate_method_hypotheses(
            case_id, case_data, evidence_items
        )
        hypotheses.extend(method_hypotheses)

        if case_id not in self._case_hypotheses:
            self._case_hypotheses[case_id] = []
        self._case_hypotheses[case_id].extend([h.hypothesis_id for h in hypotheses])

        return hypotheses

    def _generate_suspect_hypotheses(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
    ) -> List[Hypothesis]:
        hypotheses = []

        for suspect in suspects:
            hypothesis_id = f"hyp-sus-{uuid.uuid4().hex[:12]}"

            supporting = []
            for evidence in evidence_items:
                if suspect.get("id") in evidence.get("linked_suspects", []):
                    supporting.append({
                        "evidence_id": evidence.get("id"),
                        "type": evidence.get("type"),
                        "relevance": "direct_link",
                    })

            confidence = min(0.9, 0.3 + len(supporting) * 0.15)

            hypothesis = Hypothesis(
                hypothesis_id=hypothesis_id,
                case_id=case_id,
                title=f"Suspect: {suspect.get('name', 'Unknown')}",
                description=f"Hypothesis that {suspect.get('name', 'the suspect')} committed the offense based on available evidence and connections.",
                hypothesis_type="suspect_identification",
                confidence_score=confidence,
                supporting_evidence=supporting,
                related_suspects=[suspect.get("id")],
            )
            self._hypotheses[hypothesis_id] = hypothesis
            hypotheses.append(hypothesis)

        if not suspects:
            hypothesis_id = f"hyp-unk-{uuid.uuid4().hex[:12]}"
            hypothesis = Hypothesis(
                hypothesis_id=hypothesis_id,
                case_id=case_id,
                title="Unknown Suspect",
                description="The perpetrator is currently unknown. Further investigation and evidence analysis required to identify potential suspects.",
                hypothesis_type="suspect_identification",
                confidence_score=0.2,
            )
            self._hypotheses[hypothesis_id] = hypothesis
            hypotheses.append(hypothesis)

        return hypotheses

    def _generate_motive_hypotheses(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
    ) -> List[Hypothesis]:
        hypotheses = []
        offense_type = case_data.get("offense_type", "")

        motive_templates = {
            "homicide": [
                ("Financial Gain", "The offense was motivated by financial benefit, such as inheritance, insurance, or debt elimination."),
                ("Personal Conflict", "The offense resulted from an interpersonal dispute, jealousy, or revenge."),
                ("Concealment", "The offense was committed to conceal another crime or prevent testimony."),
            ],
            "robbery": [
                ("Financial Need", "The offense was motivated by immediate financial need or desperation."),
                ("Opportunistic", "The offense was opportunistic, targeting a vulnerable victim or location."),
                ("Organized Crime", "The offense was part of organized criminal activity."),
            ],
            "burglary": [
                ("Theft for Resale", "Items were stolen for resale or pawning."),
                ("Personal Use", "Items were stolen for personal use, possibly indicating substance abuse."),
                ("Targeted Items", "Specific items were targeted, suggesting inside knowledge."),
            ],
        }

        templates = motive_templates.get(offense_type.lower(), [
            ("Unknown Motive", "The motive for the offense is currently unclear and requires further investigation."),
        ])

        for title, description in templates:
            hypothesis_id = f"hyp-mot-{uuid.uuid4().hex[:12]}"

            supporting = []
            for evidence in evidence_items:
                if self._evidence_supports_motive(evidence, title):
                    supporting.append({
                        "evidence_id": evidence.get("id"),
                        "type": evidence.get("type"),
                        "relevance": "supports_motive",
                    })

            confidence = 0.3 + len(supporting) * 0.1

            hypothesis = Hypothesis(
                hypothesis_id=hypothesis_id,
                case_id=case_id,
                title=f"Motive: {title}",
                description=description,
                hypothesis_type="motive",
                confidence_score=min(0.85, confidence),
                supporting_evidence=supporting,
            )
            self._hypotheses[hypothesis_id] = hypothesis
            hypotheses.append(hypothesis)

        return hypotheses

    def _generate_timeline_hypotheses(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
    ) -> List[Hypothesis]:
        hypotheses = []

        hypothesis_id = f"hyp-tl-{uuid.uuid4().hex[:12]}"

        time_evidence = [
            e for e in evidence_items
            if e.get("type") in ["witness_statement", "surveillance", "digital", "forensic_timeline"]
        ]

        earliest = case_data.get("earliest_time")
        latest = case_data.get("latest_time")

        if earliest and latest:
            description = f"The offense occurred between {earliest} and {latest} based on available evidence."
        else:
            description = "The exact timeline of the offense is being reconstructed from available evidence."

        hypothesis = Hypothesis(
            hypothesis_id=hypothesis_id,
            case_id=case_id,
            title="Primary Timeline",
            description=description,
            hypothesis_type="timeline",
            confidence_score=0.5 + len(time_evidence) * 0.1,
            supporting_evidence=[
                {"evidence_id": e.get("id"), "type": e.get("type"), "relevance": "timeline"}
                for e in time_evidence
            ],
        )
        self._hypotheses[hypothesis_id] = hypothesis
        hypotheses.append(hypothesis)

        return hypotheses

    def _generate_method_hypotheses(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
    ) -> List[Hypothesis]:
        hypotheses = []

        weapon = case_data.get("weapon_used")
        entry_method = case_data.get("entry_method")

        if weapon:
            hypothesis_id = f"hyp-wpn-{uuid.uuid4().hex[:12]}"

            weapon_evidence = [
                e for e in evidence_items
                if e.get("type") in ["weapon", "ballistics", "tool_mark"]
            ]

            hypothesis = Hypothesis(
                hypothesis_id=hypothesis_id,
                case_id=case_id,
                title=f"Weapon: {weapon}",
                description=f"The offense was committed using a {weapon}. Analysis of weapon-related evidence may identify the source or owner.",
                hypothesis_type="method",
                confidence_score=0.7 + len(weapon_evidence) * 0.1,
                supporting_evidence=[
                    {"evidence_id": e.get("id"), "type": e.get("type"), "relevance": "weapon"}
                    for e in weapon_evidence
                ],
            )
            self._hypotheses[hypothesis_id] = hypothesis
            hypotheses.append(hypothesis)

        if entry_method:
            hypothesis_id = f"hyp-ent-{uuid.uuid4().hex[:12]}"

            entry_evidence = [
                e for e in evidence_items
                if e.get("type") in ["entry_point", "tool_mark", "fingerprint"]
            ]

            hypothesis = Hypothesis(
                hypothesis_id=hypothesis_id,
                case_id=case_id,
                title=f"Entry Method: {entry_method}",
                description=f"The perpetrator gained entry via {entry_method}. This method may indicate skill level and planning.",
                hypothesis_type="method",
                confidence_score=0.6 + len(entry_evidence) * 0.1,
                supporting_evidence=[
                    {"evidence_id": e.get("id"), "type": e.get("type"), "relevance": "entry"}
                    for e in entry_evidence
                ],
            )
            self._hypotheses[hypothesis_id] = hypothesis
            hypotheses.append(hypothesis)

        return hypotheses

    def _evidence_supports_motive(self, evidence: Dict[str, Any], motive: str) -> bool:
        evidence_type = evidence.get("type", "")
        motive_lower = motive.lower()

        if "financial" in motive_lower:
            return evidence_type in ["financial_record", "insurance", "will", "debt"]
        if "personal" in motive_lower or "conflict" in motive_lower:
            return evidence_type in ["witness_statement", "communication", "social_media"]
        if "concealment" in motive_lower:
            return evidence_type in ["prior_crime", "witness_statement"]

        return False

    def update_hypothesis(
        self,
        hypothesis_id: str,
        status: Optional[HypothesisStatus] = None,
        confidence_score: Optional[float] = None,
        supporting_evidence: Optional[List[Dict[str, Any]]] = None,
        contradicting_evidence: Optional[List[Dict[str, Any]]] = None,
        review_notes: Optional[str] = None,
        reviewed_by: Optional[str] = None,
    ) -> Optional[Hypothesis]:
        hypothesis = self._hypotheses.get(hypothesis_id)
        if not hypothesis:
            return None

        if status is not None:
            hypothesis.status = status
        if confidence_score is not None:
            hypothesis.confidence_score = confidence_score
        if supporting_evidence is not None:
            hypothesis.supporting_evidence.extend(supporting_evidence)
        if contradicting_evidence is not None:
            hypothesis.contradicting_evidence.extend(contradicting_evidence)
        if review_notes is not None:
            hypothesis.review_notes = review_notes
        if reviewed_by is not None:
            hypothesis.reviewed_by = reviewed_by

        hypothesis.updated_at = datetime.utcnow()
        return hypothesis

    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        return self._hypotheses.get(hypothesis_id)

    def get_case_hypotheses(
        self,
        case_id: str,
        status: Optional[HypothesisStatus] = None,
        hypothesis_type: Optional[str] = None,
    ) -> List[Hypothesis]:
        hyp_ids = self._case_hypotheses.get(case_id, [])
        results = [self._hypotheses[hid] for hid in hyp_ids if hid in self._hypotheses]

        if status:
            results = [h for h in results if h.status == status]
        if hypothesis_type:
            results = [h for h in results if h.hypothesis_type == hypothesis_type]

        return results

    def rank_hypotheses(self, case_id: str) -> List[Tuple[Hypothesis, float]]:
        hypotheses = self.get_case_hypotheses(case_id)

        ranked = []
        for h in hypotheses:
            score = h.confidence_score

            if h.status == HypothesisStatus.SUPPORTED:
                score *= 1.2
            elif h.status == HypothesisStatus.CONTRADICTED:
                score *= 0.5
            elif h.status == HypothesisStatus.ELIMINATED:
                score *= 0.1

            evidence_bonus = len(h.supporting_evidence) * 0.05
            contradiction_penalty = len(h.contradicting_evidence) * 0.1

            final_score = min(1.0, max(0.0, score + evidence_bonus - contradiction_penalty))
            ranked.append((h, final_score))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked


class ContradictionChecker:
    """Validates hypotheses and identifies contradictions."""

    def __init__(self, hypothesis_generator: HypothesisGenerator):
        self._hypothesis_generator = hypothesis_generator
        self._contradictions: Dict[str, Contradiction] = {}

    def check_hypothesis(
        self,
        hypothesis_id: str,
        evidence_items: List[Dict[str, Any]],
        case_data: Dict[str, Any],
    ) -> List[Contradiction]:
        hypothesis = self._hypothesis_generator.get_hypothesis(hypothesis_id)
        if not hypothesis:
            return []

        contradictions = []

        temporal = self._check_temporal_contradictions(hypothesis, evidence_items, case_data)
        contradictions.extend(temporal)

        physical = self._check_physical_contradictions(hypothesis, evidence_items, case_data)
        contradictions.extend(physical)

        logical = self._check_logical_contradictions(hypothesis, evidence_items, case_data)
        contradictions.extend(logical)

        if contradictions:
            self._hypothesis_generator.update_hypothesis(
                hypothesis_id,
                contradicting_evidence=[
                    {"contradiction_id": c.contradiction_id, "type": c.contradiction_type}
                    for c in contradictions
                ],
            )

            if len(contradictions) >= 3:
                self._hypothesis_generator.update_hypothesis(
                    hypothesis_id,
                    status=HypothesisStatus.CONTRADICTED,
                )

        return contradictions

    def _check_temporal_contradictions(
        self,
        hypothesis: Hypothesis,
        evidence_items: List[Dict[str, Any]],
        case_data: Dict[str, Any],
    ) -> List[Contradiction]:
        contradictions = []

        if hypothesis.hypothesis_type == "suspect_identification":
            for suspect_id in hypothesis.related_suspects:
                alibi_evidence = [
                    e for e in evidence_items
                    if e.get("type") == "alibi" and suspect_id in e.get("subjects", [])
                ]

                for alibi in alibi_evidence:
                    if alibi.get("verified"):
                        contradiction = Contradiction(
                            contradiction_id=f"contra-temp-{uuid.uuid4().hex[:12]}",
                            case_id=hypothesis.case_id,
                            hypothesis_id=hypothesis.hypothesis_id,
                            contradiction_type="temporal_alibi",
                            description=f"Suspect has a verified alibi for the time of the offense.",
                            evidence_items=[alibi.get("id")],
                            severity="critical",
                        )
                        self._contradictions[contradiction.contradiction_id] = contradiction
                        contradictions.append(contradiction)

        return contradictions

    def _check_physical_contradictions(
        self,
        hypothesis: Hypothesis,
        evidence_items: List[Dict[str, Any]],
        case_data: Dict[str, Any],
    ) -> List[Contradiction]:
        contradictions = []

        if hypothesis.hypothesis_type == "suspect_identification":
            for suspect_id in hypothesis.related_suspects:
                exclusion_evidence = [
                    e for e in evidence_items
                    if e.get("type") in ["dna", "fingerprint", "ballistics"]
                    and e.get("excludes_suspect") == suspect_id
                ]

                for evidence in exclusion_evidence:
                    contradiction = Contradiction(
                        contradiction_id=f"contra-phys-{uuid.uuid4().hex[:12]}",
                        case_id=hypothesis.case_id,
                        hypothesis_id=hypothesis.hypothesis_id,
                        contradiction_type="physical_exclusion",
                        description=f"Physical evidence ({evidence.get('type')}) excludes the suspect.",
                        evidence_items=[evidence.get("id")],
                        severity="critical",
                    )
                    self._contradictions[contradiction.contradiction_id] = contradiction
                    contradictions.append(contradiction)

        return contradictions

    def _check_logical_contradictions(
        self,
        hypothesis: Hypothesis,
        evidence_items: List[Dict[str, Any]],
        case_data: Dict[str, Any],
    ) -> List[Contradiction]:
        contradictions = []

        if hypothesis.hypothesis_type == "method":
            for evidence in evidence_items:
                if evidence.get("type") == "forensic_analysis":
                    if evidence.get("contradicts_method"):
                        contradiction = Contradiction(
                            contradiction_id=f"contra-log-{uuid.uuid4().hex[:12]}",
                            case_id=hypothesis.case_id,
                            hypothesis_id=hypothesis.hypothesis_id,
                            contradiction_type="logical_inconsistency",
                            description=f"Forensic analysis contradicts the proposed method.",
                            evidence_items=[evidence.get("id")],
                            severity="moderate",
                        )
                        self._contradictions[contradiction.contradiction_id] = contradiction
                        contradictions.append(contradiction)

        return contradictions

    def resolve_contradiction(
        self,
        contradiction_id: str,
        resolution_notes: str,
        resolved_by: str,
    ) -> Optional[Contradiction]:
        contradiction = self._contradictions.get(contradiction_id)
        if not contradiction:
            return None

        contradiction.resolution_status = "resolved"
        contradiction.resolution_notes = resolution_notes
        contradiction.resolved_at = datetime.utcnow()

        return contradiction

    def get_contradiction(self, contradiction_id: str) -> Optional[Contradiction]:
        return self._contradictions.get(contradiction_id)

    def get_hypothesis_contradictions(self, hypothesis_id: str) -> List[Contradiction]:
        return [
            c for c in self._contradictions.values()
            if c.hypothesis_id == hypothesis_id
        ]

    def get_unresolved_contradictions(self, case_id: str) -> List[Contradiction]:
        return [
            c for c in self._contradictions.values()
            if c.case_id == case_id and c.resolution_status == "unresolved"
        ]


class EvidenceWeightingEngine:
    """Calculates probabilistic weights for evidence linking to suspects."""

    def __init__(self):
        self._weights: Dict[str, EvidenceWeight] = {}

    def calculate_weight(
        self,
        case_id: str,
        evidence_id: str,
        evidence_data: Dict[str, Any],
        suspect_id: Optional[str] = None,
    ) -> EvidenceWeight:
        weight_id = f"weight-{uuid.uuid4().hex[:12]}"

        relevance = self._calculate_relevance(evidence_data)
        reliability = self._calculate_reliability(evidence_data)
        probative = self._calculate_probative_value(evidence_data, suspect_id)

        weight_score = (relevance * 0.3 + reliability * 0.3 + probative * 0.4)

        if weight_score >= 0.8:
            strength = EvidenceStrength.CONCLUSIVE
        elif weight_score >= 0.6:
            strength = EvidenceStrength.STRONG
        elif weight_score >= 0.4:
            strength = EvidenceStrength.MODERATE
        else:
            strength = EvidenceStrength.WEAK

        factors = [
            {"factor": "evidence_type", "value": evidence_data.get("type"), "impact": self._get_type_impact(evidence_data.get("type"))},
            {"factor": "chain_of_custody", "value": evidence_data.get("chain_intact", True), "impact": 0.1 if evidence_data.get("chain_intact", True) else -0.2},
            {"factor": "analysis_complete", "value": evidence_data.get("analyzed", False), "impact": 0.1 if evidence_data.get("analyzed") else 0},
            {"factor": "corroborated", "value": evidence_data.get("corroborated", False), "impact": 0.15 if evidence_data.get("corroborated") else 0},
        ]

        weight = EvidenceWeight(
            weight_id=weight_id,
            case_id=case_id,
            evidence_id=evidence_id,
            suspect_id=suspect_id,
            weight_score=weight_score,
            strength=strength,
            relevance_score=relevance,
            reliability_score=reliability,
            probative_value=probative,
            factors=factors,
        )
        self._weights[weight_id] = weight
        return weight

    def _calculate_relevance(self, evidence_data: Dict[str, Any]) -> float:
        base_relevance = 0.5

        evidence_type = evidence_data.get("type", "")
        high_relevance_types = ["dna", "fingerprint", "weapon", "surveillance", "confession"]
        medium_relevance_types = ["witness_statement", "digital", "document", "forensic"]

        if evidence_type in high_relevance_types:
            base_relevance = 0.8
        elif evidence_type in medium_relevance_types:
            base_relevance = 0.6

        if evidence_data.get("directly_links_suspect"):
            base_relevance += 0.15

        return min(1.0, base_relevance)

    def _calculate_reliability(self, evidence_data: Dict[str, Any]) -> float:
        base_reliability = 0.5

        if evidence_data.get("chain_intact", True):
            base_reliability += 0.1

        if evidence_data.get("analyzed"):
            base_reliability += 0.15

        if evidence_data.get("expert_verified"):
            base_reliability += 0.2

        if evidence_data.get("contamination_risk"):
            base_reliability -= 0.2

        if evidence_data.get("type") == "witness_statement":
            if evidence_data.get("witness_credibility", 0.5) < 0.5:
                base_reliability -= 0.15

        return max(0.1, min(1.0, base_reliability))

    def _calculate_probative_value(
        self,
        evidence_data: Dict[str, Any],
        suspect_id: Optional[str],
    ) -> float:
        base_probative = 0.3

        if suspect_id:
            if suspect_id in evidence_data.get("linked_suspects", []):
                base_probative += 0.4

            if evidence_data.get("type") == "dna" and evidence_data.get("dna_match") == suspect_id:
                base_probative = 0.95

            if evidence_data.get("type") == "fingerprint" and evidence_data.get("print_match") == suspect_id:
                base_probative = 0.9

        if evidence_data.get("unique_identifier"):
            base_probative += 0.2

        return min(1.0, base_probative)

    def _get_type_impact(self, evidence_type: str) -> float:
        impacts = {
            "dna": 0.3,
            "fingerprint": 0.25,
            "weapon": 0.2,
            "surveillance": 0.2,
            "confession": 0.25,
            "witness_statement": 0.1,
            "digital": 0.15,
            "document": 0.1,
            "forensic": 0.15,
        }
        return impacts.get(evidence_type, 0.05)

    def get_weight(self, weight_id: str) -> Optional[EvidenceWeight]:
        return self._weights.get(weight_id)

    def get_evidence_weights(
        self,
        case_id: str,
        suspect_id: Optional[str] = None,
        min_strength: Optional[EvidenceStrength] = None,
    ) -> List[EvidenceWeight]:
        results = [w for w in self._weights.values() if w.case_id == case_id]

        if suspect_id:
            results = [w for w in results if w.suspect_id == suspect_id]

        if min_strength:
            strength_order = [EvidenceStrength.WEAK, EvidenceStrength.MODERATE, EvidenceStrength.STRONG, EvidenceStrength.CONCLUSIVE]
            min_index = strength_order.index(min_strength)
            results = [w for w in results if strength_order.index(w.strength) >= min_index]

        return results

    def calculate_cumulative_weight(
        self,
        case_id: str,
        suspect_id: str,
    ) -> Dict[str, Any]:
        weights = self.get_evidence_weights(case_id, suspect_id)

        if not weights:
            return {
                "suspect_id": suspect_id,
                "cumulative_score": 0.0,
                "evidence_count": 0,
                "strength_distribution": {},
                "recommendation": "insufficient_evidence",
            }

        cumulative = sum(w.weight_score for w in weights) / len(weights)

        strength_dist = {}
        for w in weights:
            strength_dist[w.strength.value] = strength_dist.get(w.strength.value, 0) + 1

        if cumulative >= 0.8:
            recommendation = "strong_case"
        elif cumulative >= 0.6:
            recommendation = "moderate_case"
        elif cumulative >= 0.4:
            recommendation = "weak_case"
        else:
            recommendation = "insufficient_evidence"

        return {
            "suspect_id": suspect_id,
            "cumulative_score": cumulative,
            "evidence_count": len(weights),
            "strength_distribution": strength_dist,
            "recommendation": recommendation,
        }


class CaseNarrativeBuilder:
    """Builds structured detective narratives from case data."""

    def __init__(
        self,
        hypothesis_generator: HypothesisGenerator,
        evidence_weighting: EvidenceWeightingEngine,
    ):
        self._hypothesis_generator = hypothesis_generator
        self._evidence_weighting = evidence_weighting
        self._narratives: Dict[str, CaseNarrative] = {}

    def build_narrative(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
    ) -> CaseNarrative:
        narrative_id = f"narr-{uuid.uuid4().hex[:12]}"

        sections = {}

        sections[NarrativeSection.SUMMARY.value] = self._build_summary(case_data)
        sections[NarrativeSection.BACKGROUND.value] = self._build_background(case_data)
        sections[NarrativeSection.TIMELINE.value] = self._build_timeline(case_data, evidence_items)
        sections[NarrativeSection.EVIDENCE_ANALYSIS.value] = self._build_evidence_analysis(case_id, evidence_items)
        sections[NarrativeSection.SUSPECT_ANALYSIS.value] = self._build_suspect_analysis(case_id, suspects)
        sections[NarrativeSection.THEORY.value] = self._build_theory_section(case_id)
        sections[NarrativeSection.CONCLUSIONS.value] = self._build_conclusions(case_id, case_data)
        sections[NarrativeSection.RECOMMENDATIONS.value] = self._build_recommendations(case_id)

        hypotheses = self._hypothesis_generator.get_case_hypotheses(case_id)
        hypothesis_ids = [h.hypothesis_id for h in hypotheses]

        word_count = sum(len(s.split()) for s in sections.values())

        narrative = CaseNarrative(
            narrative_id=narrative_id,
            case_id=case_id,
            title=f"Investigative Narrative: Case {case_id}",
            sections=sections,
            hypotheses_included=hypothesis_ids,
            evidence_cited=[e.get("id") for e in evidence_items],
            suspects_discussed=[s.get("id") for s in suspects],
            word_count=word_count,
        )
        self._narratives[narrative_id] = narrative
        return narrative

    def _build_summary(self, case_data: Dict[str, Any]) -> str:
        offense_type = case_data.get("offense_type", "offense")
        location = case_data.get("location", {}).get("address", "unknown location")
        date = case_data.get("date", "unknown date")
        victim = case_data.get("victim", {}).get("name", "the victim")

        return f"""EXECUTIVE SUMMARY

This investigative narrative documents the {offense_type} that occurred at {location} on {date}. The incident involved {victim} and has been subject to comprehensive investigation by the Autonomous Detective AI system.

This report synthesizes all available evidence, witness statements, forensic analysis, and investigative hypotheses to provide a complete picture of the offense and identify potential suspects."""

    def _build_background(self, case_data: Dict[str, Any]) -> str:
        victim_info = case_data.get("victim", {})
        location_info = case_data.get("location", {})

        background = """BACKGROUND

"""
        if victim_info:
            background += f"Victim Profile: {victim_info.get('name', 'Unknown')} - {victim_info.get('description', 'No additional information available.')}\n\n"

        if location_info:
            background += f"Location: {location_info.get('address', 'Unknown')} - {location_info.get('description', 'No additional information available.')}\n\n"

        background += f"Initial Report: {case_data.get('initial_report', 'Case initiated based on reported incident.')}"

        return background

    def _build_timeline(
        self,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
    ) -> str:
        timeline = """TIMELINE OF EVENTS

"""
        events = case_data.get("timeline_events", [])

        if events:
            for event in sorted(events, key=lambda x: x.get("timestamp", "")):
                timeline += f"- {event.get('timestamp', 'Unknown time')}: {event.get('description', 'Event')}\n"
        else:
            timeline += "Timeline reconstruction is ongoing. Key temporal markers:\n"
            timeline += f"- Earliest possible time: {case_data.get('earliest_time', 'Unknown')}\n"
            timeline += f"- Latest possible time: {case_data.get('latest_time', 'Unknown')}\n"
            timeline += f"- Discovery time: {case_data.get('discovery_time', 'Unknown')}\n"

        return timeline

    def _build_evidence_analysis(
        self,
        case_id: str,
        evidence_items: List[Dict[str, Any]],
    ) -> str:
        analysis = """EVIDENCE ANALYSIS

"""
        if not evidence_items:
            return analysis + "No evidence items have been catalogued for this case."

        by_type: Dict[str, List[Dict[str, Any]]] = {}
        for item in evidence_items:
            item_type = item.get("type", "other")
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)

        for evidence_type, items in by_type.items():
            analysis += f"\n{evidence_type.upper().replace('_', ' ')} ({len(items)} items):\n"
            for item in items[:5]:
                analysis += f"  - {item.get('description', 'No description')}\n"
            if len(items) > 5:
                analysis += f"  ... and {len(items) - 5} additional items\n"

        return analysis

    def _build_suspect_analysis(
        self,
        case_id: str,
        suspects: List[Dict[str, Any]],
    ) -> str:
        analysis = """SUSPECT ANALYSIS

"""
        if not suspects:
            return analysis + "No suspects have been identified at this time. The investigation continues to develop leads."

        for suspect in suspects:
            analysis += f"\nSUSPECT: {suspect.get('name', 'Unknown')}\n"
            analysis += f"Status: {suspect.get('status', 'Person of Interest')}\n"

            cumulative = self._evidence_weighting.calculate_cumulative_weight(
                case_id, suspect.get("id", "")
            )
            analysis += f"Evidence Strength: {cumulative.get('recommendation', 'Unknown').replace('_', ' ').title()}\n"
            analysis += f"Evidence Items: {cumulative.get('evidence_count', 0)}\n"

            if suspect.get("connection"):
                analysis += f"Connection to Case: {suspect.get('connection')}\n"

        return analysis

    def _build_theory_section(self, case_id: str) -> str:
        theory = """INVESTIGATIVE THEORIES

"""
        ranked = self._hypothesis_generator.rank_hypotheses(case_id)

        if not ranked:
            return theory + "Hypotheses are being developed based on available evidence."

        theory += "The following theories have been generated and ranked by confidence:\n\n"

        for i, (hypothesis, score) in enumerate(ranked[:5], 1):
            theory += f"{i}. {hypothesis.title} (Confidence: {score:.0%})\n"
            theory += f"   Status: {hypothesis.status.value.replace('_', ' ').title()}\n"
            theory += f"   {hypothesis.description}\n\n"

        return theory

    def _build_conclusions(
        self,
        case_id: str,
        case_data: Dict[str, Any],
    ) -> str:
        conclusions = """CONCLUSIONS

"""
        ranked = self._hypothesis_generator.rank_hypotheses(case_id)

        if ranked:
            top_hypothesis, top_score = ranked[0]
            if top_score >= 0.7:
                conclusions += f"Primary Theory: {top_hypothesis.title} is strongly supported by available evidence.\n\n"
            elif top_score >= 0.5:
                conclusions += f"Leading Theory: {top_hypothesis.title} shows moderate support but requires additional investigation.\n\n"
            else:
                conclusions += "No theory has achieved sufficient confidence. Additional investigation is required.\n\n"

        conclusions += "Case Status: " + case_data.get("status", "Active Investigation")

        return conclusions

    def _build_recommendations(self, case_id: str) -> str:
        recommendations = """RECOMMENDATIONS

Based on the analysis conducted, the following investigative actions are recommended:

1. Continue evidence collection and analysis
2. Conduct additional witness interviews
3. Review surveillance footage from surrounding areas
4. Cross-reference with similar cases in the database
5. Monitor for additional leads through intelligence channels

Priority Actions:
"""
        ranked = self._hypothesis_generator.rank_hypotheses(case_id)

        if ranked:
            top_hypothesis, _ = ranked[0]
            if top_hypothesis.hypothesis_type == "suspect_identification":
                recommendations += "- Focus investigation on identified suspect(s)\n"
                recommendations += "- Verify alibis and establish timeline\n"
            elif top_hypothesis.hypothesis_type == "motive":
                recommendations += "- Investigate potential motives further\n"
                recommendations += "- Identify individuals with matching motives\n"

        return recommendations

    def get_narrative(self, narrative_id: str) -> Optional[CaseNarrative]:
        return self._narratives.get(narrative_id)

    def get_case_narratives(self, case_id: str) -> List[CaseNarrative]:
        return [n for n in self._narratives.values() if n.case_id == case_id]

    def update_narrative(
        self,
        narrative_id: str,
        section: NarrativeSection,
        content: str,
    ) -> Optional[CaseNarrative]:
        narrative = self._narratives.get(narrative_id)
        if not narrative:
            return None

        narrative.sections[section.value] = content
        narrative.word_count = sum(len(s.split()) for s in narrative.sections.values())
        narrative.version += 1

        return narrative

    def export_narrative(
        self,
        narrative_id: str,
        format: str = "text",
    ) -> Optional[str]:
        narrative = self._narratives.get(narrative_id)
        if not narrative:
            return None

        if format == "text":
            output = f"{'='*60}\n"
            output += f"{narrative.title}\n"
            output += f"Generated: {narrative.generated_at.isoformat()}\n"
            output += f"{'='*60}\n\n"

            section_order = [
                NarrativeSection.SUMMARY,
                NarrativeSection.BACKGROUND,
                NarrativeSection.TIMELINE,
                NarrativeSection.EVIDENCE_ANALYSIS,
                NarrativeSection.SUSPECT_ANALYSIS,
                NarrativeSection.THEORY,
                NarrativeSection.CONCLUSIONS,
                NarrativeSection.RECOMMENDATIONS,
            ]

            for section in section_order:
                if section.value in narrative.sections:
                    output += narrative.sections[section.value]
                    output += "\n\n" + "-"*40 + "\n\n"

            return output

        return None


__all__ = [
    "HypothesisStatus",
    "EvidenceStrength",
    "NarrativeSection",
    "Hypothesis",
    "Contradiction",
    "EvidenceWeight",
    "CaseNarrative",
    "HypothesisGenerator",
    "ContradictionChecker",
    "EvidenceWeightingEngine",
    "CaseNarrativeBuilder",
]
