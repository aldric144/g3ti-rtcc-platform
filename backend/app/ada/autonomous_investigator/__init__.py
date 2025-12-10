"""
Phase 20: Autonomous Investigator Module

Provides full-case auto-investigation pipeline and daily case triage engine
for the Autonomous Detective AI.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import uuid

from ..crime_scene_engine import (
    SceneReconstructionEngine,
    SpatialEvidenceMapper,
    TrajectoryRebuilder,
)
from ..offender_modeling import (
    BehavioralSignatureEngine,
    OffenderPredictionModel,
    ModusOperandiClusterer,
    UnknownSuspectProfiler,
)
from ..case_theory_engine import (
    HypothesisGenerator,
    ContradictionChecker,
    EvidenceWeightingEngine,
    CaseNarrativeBuilder,
)
from ..evidence_graph import (
    EvidenceGraphExpander,
    SimilarityScoreEngine,
    UnsolvedCaseLinker,
)
from ..reporting_engine import (
    DraftReportBuilder,
    DetectiveBriefGenerator,
    ReportType,
)


class InvestigationStatus(str, Enum):
    QUEUED = "queued"
    INITIALIZING = "initializing"
    ANALYZING_SCENE = "analyzing_scene"
    PROFILING_OFFENDER = "profiling_offender"
    GENERATING_THEORIES = "generating_theories"
    LINKING_CASES = "linking_cases"
    BUILDING_REPORT = "building_report"
    COMPLETED = "completed"
    FAILED = "failed"


class TriagePriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ROUTINE = "routine"


class TriageReason(str, Enum):
    NEW_EVIDENCE = "new_evidence"
    STALE_CASE = "stale_case"
    PATTERN_MATCH = "pattern_match"
    WITNESS_AVAILABLE = "witness_available"
    SUSPECT_IDENTIFIED = "suspect_identified"
    FORENSIC_RESULTS = "forensic_results"
    LINKED_CASE_UPDATE = "linked_case_update"
    SCHEDULED_REVIEW = "scheduled_review"
    SUPERVISOR_REQUEST = "supervisor_request"


@dataclass
class InvestigationResult:
    result_id: str
    case_id: str
    status: InvestigationStatus
    suspects: List[Dict[str, Any]] = field(default_factory=list)
    theories: List[Dict[str, Any]] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    evidence_map: Dict[str, Any] = field(default_factory=dict)
    linked_cases: List[str] = field(default_factory=list)
    report_id: Optional[str] = None
    brief_id: Optional[str] = None
    confidence_score: float = 0.0
    processing_time_seconds: float = 0.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriageItem:
    triage_id: str
    case_id: str
    priority: TriagePriority
    reasons: List[TriageReason] = field(default_factory=list)
    score: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)
    last_activity: Optional[datetime] = None
    days_since_activity: int = 0
    evidence_pending: int = 0
    leads_pending: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    reviewed: bool = False
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriageReport:
    report_id: str
    report_date: datetime
    total_cases_reviewed: int
    critical_cases: List[TriageItem] = field(default_factory=list)
    high_priority_cases: List[TriageItem] = field(default_factory=list)
    medium_priority_cases: List[TriageItem] = field(default_factory=list)
    low_priority_cases: List[TriageItem] = field(default_factory=list)
    routine_cases: List[TriageItem] = field(default_factory=list)
    summary: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AutoInvestigatePipeline:
    """Full-case autonomous investigation pipeline."""

    def __init__(self):
        self._evidence_mapper = SpatialEvidenceMapper()
        self._trajectory_rebuilder = TrajectoryRebuilder(self._evidence_mapper)
        self._scene_engine = SceneReconstructionEngine()

        self._signature_engine = BehavioralSignatureEngine()
        self._prediction_model = OffenderPredictionModel(self._signature_engine)
        self._mo_clusterer = ModusOperandiClusterer(self._signature_engine)
        self._suspect_profiler = UnknownSuspectProfiler(self._signature_engine)

        self._hypothesis_generator = HypothesisGenerator()
        self._contradiction_checker = ContradictionChecker(self._hypothesis_generator)
        self._evidence_weighting = EvidenceWeightingEngine()
        self._narrative_builder = CaseNarrativeBuilder(
            self._hypothesis_generator,
            self._evidence_weighting,
        )

        self._graph_expander = EvidenceGraphExpander()
        self._similarity_engine = SimilarityScoreEngine(self._graph_expander)
        self._case_linker = UnsolvedCaseLinker(
            self._graph_expander,
            self._similarity_engine,
        )

        self._report_builder = DraftReportBuilder()
        self._brief_generator = DetectiveBriefGenerator()

        self._results: Dict[str, InvestigationResult] = {}

    def investigate(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: Optional[List[Dict[str, Any]]] = None,
        related_cases: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
    ) -> InvestigationResult:
        result_id = f"inv-{uuid.uuid4().hex[:12]}"
        start_time = datetime.utcnow()

        result = InvestigationResult(
            result_id=result_id,
            case_id=case_id,
            status=InvestigationStatus.INITIALIZING,
        )
        self._results[result_id] = result

        try:
            result.status = InvestigationStatus.ANALYZING_SCENE
            scene_analysis = self._analyze_scene(case_id, case_data, evidence_items)
            result.evidence_map = scene_analysis
            result.timeline = scene_analysis.get("timeline", [])

            result.status = InvestigationStatus.PROFILING_OFFENDER
            offender_analysis = self._profile_offender(
                case_id, case_data, evidence_items, suspects
            )
            result.suspects = offender_analysis.get("suspects", [])

            result.status = InvestigationStatus.GENERATING_THEORIES
            theory_analysis = self._generate_theories(
                case_id, case_data, evidence_items, suspects or []
            )
            result.theories = theory_analysis.get("theories", [])

            result.status = InvestigationStatus.LINKING_CASES
            if related_cases:
                linked = self._link_cases(case_id, case_data, related_cases)
                result.linked_cases = linked

            result.status = InvestigationStatus.BUILDING_REPORT
            report_data = self._build_reports(
                case_id, case_data, evidence_items, suspects or [], result.theories
            )
            result.report_id = report_data.get("report_id")
            result.brief_id = report_data.get("brief_id")

            result.confidence_score = self._calculate_confidence(result)
            result.status = InvestigationStatus.COMPLETED
            result.completed_at = datetime.utcnow()
            result.processing_time_seconds = (
                result.completed_at - start_time
            ).total_seconds()

        except Exception as e:
            result.status = InvestigationStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()

        return result

    def _analyze_scene(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        for item in evidence_items:
            self._evidence_mapper.register_evidence(
                case_id=case_id,
                evidence_type=item.get("type", "other"),
                position=item.get("position", {"x": 0, "y": 0, "z": 0}),
                description=item.get("description", ""),
                collected_by=item.get("collected_by", "unknown"),
            )

        clusters = self._evidence_mapper.cluster_evidence(case_id)

        entry_exit = self._evidence_mapper.analyze_entry_exit_points(case_id)

        trajectory = self._trajectory_rebuilder.infer_movement_from_evidence(case_id)

        location = case_data.get("location", {})
        reconstruction = self._scene_engine.create_reconstruction(
            case_id=case_id,
            scene_type=case_data.get("scene_type", "indoor"),
            location=location,
            bounds={"min_x": 0, "max_x": 100, "min_y": 0, "max_y": 100},
        )

        self._scene_engine.analyze_scene(reconstruction.reconstruction_id)
        timeline = self._scene_engine.generate_timeline(reconstruction.reconstruction_id)

        return {
            "reconstruction_id": reconstruction.reconstruction_id,
            "evidence_clusters": clusters,
            "entry_points": [
                {"position": e.position, "type": e.evidence_type.value}
                for e in entry_exit.get("entry_points", [])
            ],
            "exit_points": [
                {"position": e.position, "type": e.evidence_type.value}
                for e in entry_exit.get("exit_points", [])
            ],
            "trajectory": {
                "trajectory_id": trajectory.trajectory_id if trajectory else None,
                "points": [
                    {"position": p.position, "type": p.movement_type.value}
                    for p in (trajectory.points if trajectory else [])
                ],
                "total_distance": trajectory.total_distance if trajectory else 0,
            },
            "timeline": timeline,
            "confidence": reconstruction.confidence_score,
        }

    def _profile_offender(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        signatures = self._signature_engine.analyze_case(case_id, case_data)

        suspect_profiles = []

        if suspects:
            for suspect in suspects:
                weights = []
                for item in evidence_items:
                    weight = self._evidence_weighting.calculate_weight(
                        case_id=case_id,
                        evidence_id=item.get("id", ""),
                        evidence_data=item,
                        suspect_id=suspect.get("id"),
                    )
                    weights.append(weight)

                cumulative = self._evidence_weighting.calculate_cumulative_weight(
                    case_id, suspect.get("id", "")
                )

                suspect_profiles.append({
                    "suspect_id": suspect.get("id"),
                    "name": suspect.get("name", "Unknown"),
                    "evidence_strength": cumulative.get("recommendation"),
                    "cumulative_score": cumulative.get("cumulative_score"),
                    "evidence_count": cumulative.get("evidence_count"),
                })
        else:
            profile = self._suspect_profiler.generate_profile(
                case_ids=[case_id],
                case_data=[case_data],
            )
            suspect_profiles.append({
                "profile_id": profile.profile_id,
                "type": "unknown_suspect_profile",
                "demographics": profile.demographics,
                "psychological_traits": profile.psychological_traits,
                "behavioral_indicators": profile.behavioral_indicators,
                "confidence": profile.confidence.value,
            })

        predictions = []
        for sig in signatures:
            if sig.overall_score > 0.5:
                prediction = self._prediction_model.predict_next_offense(
                    signature_id=sig.signature_id
                )
                if prediction:
                    predictions.append({
                        "prediction_id": prediction.prediction_id,
                        "predicted_type": prediction.predicted_offense_type.value,
                        "risk_level": prediction.risk_level.value,
                        "confidence": prediction.confidence_score,
                    })

        return {
            "suspects": suspect_profiles,
            "signatures": [
                {
                    "signature_id": s.signature_id,
                    "category": s.category.value,
                    "patterns": s.patterns,
                    "score": s.overall_score,
                }
                for s in signatures
            ],
            "predictions": predictions,
        }

    def _generate_theories(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        hypotheses = self._hypothesis_generator.generate_hypotheses(
            case_id=case_id,
            case_data=case_data,
            evidence_items=evidence_items,
            suspects=suspects,
        )

        for hypothesis in hypotheses:
            self._contradiction_checker.check_hypothesis(
                hypothesis.hypothesis_id,
                evidence_items,
                case_data,
            )

        ranked = self._hypothesis_generator.rank_hypotheses(case_id)

        theories = []
        for hypothesis, score in ranked:
            contradictions = self._contradiction_checker.get_hypothesis_contradictions(
                hypothesis.hypothesis_id
            )
            theories.append({
                "hypothesis_id": hypothesis.hypothesis_id,
                "title": hypothesis.title,
                "description": hypothesis.description,
                "type": hypothesis.hypothesis_type,
                "status": hypothesis.status.value,
                "confidence": score,
                "supporting_evidence": len(hypothesis.supporting_evidence),
                "contradictions": len(contradictions),
            })

        return {
            "theories": theories,
            "top_theory": theories[0] if theories else None,
            "total_hypotheses": len(hypotheses),
        }

    def _link_cases(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        related_cases: List[Tuple[str, Dict[str, Any]]],
    ) -> List[str]:
        self._graph_expander.expand_from_case(case_id, case_data)

        for related_id, related_data in related_cases:
            self._graph_expander.expand_from_case(related_id, related_data)

        similar = self._similarity_engine.find_similar_cases(
            case_id=case_id,
            case_data=case_data,
            candidate_cases=related_cases,
            min_similarity=0.5,
        )

        linked_ids = []
        for result in similar:
            link = self._case_linker._create_link(
                case_id,
                result.target_case_id,
                result,
            )
            linked_ids.append(result.target_case_id)

        return linked_ids

    def _build_reports(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
        theories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        report = self._report_builder.create_report(
            case_id=case_id,
            report_type=ReportType.INVESTIGATIVE,
            case_data=case_data,
            evidence_items=evidence_items,
            suspects=suspects,
        )

        brief = self._brief_generator.generate_brief(
            case_id=case_id,
            case_data=case_data,
            evidence_items=evidence_items,
            suspects=suspects,
            hypotheses=theories,
        )

        return {
            "report_id": report.report_id,
            "brief_id": brief.brief_id,
        }

    def _calculate_confidence(self, result: InvestigationResult) -> float:
        confidence = 0.3

        if result.suspects:
            confidence += min(0.2, len(result.suspects) * 0.1)

        if result.theories:
            top_theory = result.theories[0] if result.theories else None
            if top_theory:
                confidence += top_theory.get("confidence", 0) * 0.3

        if result.evidence_map:
            confidence += 0.1

        if result.linked_cases:
            confidence += min(0.1, len(result.linked_cases) * 0.02)

        return min(1.0, confidence)

    def get_result(self, result_id: str) -> Optional[InvestigationResult]:
        return self._results.get(result_id)

    def get_case_results(self, case_id: str) -> List[InvestigationResult]:
        return [r for r in self._results.values() if r.case_id == case_id]


class DailyCaseTriageEngine:
    """Flags cases needing attention through daily triage."""

    def __init__(self):
        self._triage_items: Dict[str, TriageItem] = {}
        self._triage_reports: Dict[str, TriageReport] = {}

    def triage_case(
        self,
        case_id: str,
        case_data: Dict[str, Any],
    ) -> TriageItem:
        triage_id = f"triage-{uuid.uuid4().hex[:12]}"

        reasons = self._identify_triage_reasons(case_data)
        score = self._calculate_triage_score(case_data, reasons)
        priority = self._determine_priority(score, reasons)
        actions = self._recommend_actions(case_data, reasons)

        last_activity = case_data.get("last_activity")
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))

        days_since = 0
        if last_activity:
            days_since = (datetime.utcnow() - last_activity).days

        item = TriageItem(
            triage_id=triage_id,
            case_id=case_id,
            priority=priority,
            reasons=reasons,
            score=score,
            recommended_actions=actions,
            last_activity=last_activity,
            days_since_activity=days_since,
            evidence_pending=case_data.get("evidence_pending", 0),
            leads_pending=case_data.get("leads_pending", 0),
        )
        self._triage_items[triage_id] = item
        return item

    def _identify_triage_reasons(
        self,
        case_data: Dict[str, Any],
    ) -> List[TriageReason]:
        reasons = []

        if case_data.get("new_evidence"):
            reasons.append(TriageReason.NEW_EVIDENCE)

        last_activity = case_data.get("last_activity")
        if last_activity:
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
            days_since = (datetime.utcnow() - last_activity).days
            if days_since > 30:
                reasons.append(TriageReason.STALE_CASE)

        if case_data.get("pattern_match"):
            reasons.append(TriageReason.PATTERN_MATCH)

        if case_data.get("witness_available"):
            reasons.append(TriageReason.WITNESS_AVAILABLE)

        if case_data.get("suspect_identified"):
            reasons.append(TriageReason.SUSPECT_IDENTIFIED)

        if case_data.get("forensic_results_pending") is False and case_data.get("forensic_submitted"):
            reasons.append(TriageReason.FORENSIC_RESULTS)

        if case_data.get("linked_case_updated"):
            reasons.append(TriageReason.LINKED_CASE_UPDATE)

        if case_data.get("scheduled_review"):
            reasons.append(TriageReason.SCHEDULED_REVIEW)

        if case_data.get("supervisor_flagged"):
            reasons.append(TriageReason.SUPERVISOR_REQUEST)

        return reasons

    def _calculate_triage_score(
        self,
        case_data: Dict[str, Any],
        reasons: List[TriageReason],
    ) -> float:
        score = 0.0

        reason_weights = {
            TriageReason.NEW_EVIDENCE: 20,
            TriageReason.SUSPECT_IDENTIFIED: 25,
            TriageReason.FORENSIC_RESULTS: 20,
            TriageReason.WITNESS_AVAILABLE: 15,
            TriageReason.PATTERN_MATCH: 15,
            TriageReason.LINKED_CASE_UPDATE: 10,
            TriageReason.SUPERVISOR_REQUEST: 30,
            TriageReason.STALE_CASE: 10,
            TriageReason.SCHEDULED_REVIEW: 5,
        }

        for reason in reasons:
            score += reason_weights.get(reason, 5)

        offense_type = case_data.get("offense_type", "")
        if offense_type in ["homicide", "kidnapping", "sexual_assault"]:
            score += 30
        elif offense_type in ["robbery", "assault", "arson"]:
            score += 20
        elif offense_type in ["burglary", "theft"]:
            score += 10

        if case_data.get("public_safety_concern"):
            score += 25

        if case_data.get("media_attention"):
            score += 15

        evidence_pending = case_data.get("evidence_pending", 0)
        score += min(20, evidence_pending * 5)

        return min(100, score)

    def _determine_priority(
        self,
        score: float,
        reasons: List[TriageReason],
    ) -> TriagePriority:
        if score >= 80 or TriageReason.SUPERVISOR_REQUEST in reasons:
            return TriagePriority.CRITICAL
        elif score >= 60:
            return TriagePriority.HIGH
        elif score >= 40:
            return TriagePriority.MEDIUM
        elif score >= 20:
            return TriagePriority.LOW
        else:
            return TriagePriority.ROUTINE

    def _recommend_actions(
        self,
        case_data: Dict[str, Any],
        reasons: List[TriageReason],
    ) -> List[str]:
        actions = []

        if TriageReason.NEW_EVIDENCE in reasons:
            actions.append("Review and process new evidence")
            actions.append("Update case timeline with new findings")

        if TriageReason.SUSPECT_IDENTIFIED in reasons:
            actions.append("Verify suspect information")
            actions.append("Prepare interview strategy")
            actions.append("Check for additional evidence linking suspect")

        if TriageReason.FORENSIC_RESULTS in reasons:
            actions.append("Review forensic analysis results")
            actions.append("Update evidence weights based on results")

        if TriageReason.WITNESS_AVAILABLE in reasons:
            actions.append("Schedule witness interview")
            actions.append("Prepare interview questions")

        if TriageReason.PATTERN_MATCH in reasons:
            actions.append("Review linked cases for common elements")
            actions.append("Cross-reference suspect information")

        if TriageReason.STALE_CASE in reasons:
            actions.append("Review case for new investigative angles")
            actions.append("Consider cold case protocols")
            actions.append("Re-canvass for witnesses")

        if TriageReason.SUPERVISOR_REQUEST in reasons:
            actions.append("Prepare case summary for supervisor review")
            actions.append("Address specific supervisor concerns")

        if not actions:
            actions.append("Continue routine investigation")
            actions.append("Monitor for new developments")

        return actions

    def run_daily_triage(
        self,
        cases: List[Tuple[str, Dict[str, Any]]],
    ) -> TriageReport:
        report_id = f"triage-rpt-{uuid.uuid4().hex[:12]}"

        triage_items = []
        for case_id, case_data in cases:
            item = self.triage_case(case_id, case_data)
            triage_items.append(item)

        triage_items.sort(key=lambda x: x.score, reverse=True)

        critical = [i for i in triage_items if i.priority == TriagePriority.CRITICAL]
        high = [i for i in triage_items if i.priority == TriagePriority.HIGH]
        medium = [i for i in triage_items if i.priority == TriagePriority.MEDIUM]
        low = [i for i in triage_items if i.priority == TriagePriority.LOW]
        routine = [i for i in triage_items if i.priority == TriagePriority.ROUTINE]

        summary = self._generate_summary(len(cases), critical, high, medium, low, routine)

        report = TriageReport(
            report_id=report_id,
            report_date=datetime.utcnow(),
            total_cases_reviewed=len(cases),
            critical_cases=critical,
            high_priority_cases=high,
            medium_priority_cases=medium,
            low_priority_cases=low,
            routine_cases=routine,
            summary=summary,
        )
        self._triage_reports[report_id] = report
        return report

    def _generate_summary(
        self,
        total: int,
        critical: List[TriageItem],
        high: List[TriageItem],
        medium: List[TriageItem],
        low: List[TriageItem],
        routine: List[TriageItem],
    ) -> str:
        return f"""DAILY CASE TRIAGE SUMMARY
Date: {datetime.utcnow().strftime('%Y-%m-%d')}

Total Cases Reviewed: {total}

Priority Distribution:
- Critical: {len(critical)} cases
- High: {len(high)} cases
- Medium: {len(medium)} cases
- Low: {len(low)} cases
- Routine: {len(routine)} cases

Immediate Attention Required: {len(critical) + len(high)} cases

Key Actions:
- {len(critical)} cases require immediate supervisor attention
- {len(high)} cases have significant developments
- {len([i for i in critical + high if TriageReason.NEW_EVIDENCE in i.reasons])} cases have new evidence to process
- {len([i for i in critical + high if TriageReason.SUSPECT_IDENTIFIED in i.reasons])} cases have newly identified suspects

Recommendation: Prioritize critical and high-priority cases for today's investigative resources."""

    def mark_reviewed(
        self,
        triage_id: str,
        reviewer: str,
    ) -> Optional[TriageItem]:
        item = self._triage_items.get(triage_id)
        if not item:
            return None

        item.reviewed = True
        item.reviewed_by = reviewer
        item.reviewed_at = datetime.utcnow()

        return item

    def get_triage_item(self, triage_id: str) -> Optional[TriageItem]:
        return self._triage_items.get(triage_id)

    def get_case_triage_history(self, case_id: str) -> List[TriageItem]:
        return [i for i in self._triage_items.values() if i.case_id == case_id]

    def get_triage_report(self, report_id: str) -> Optional[TriageReport]:
        return self._triage_reports.get(report_id)

    def get_pending_critical_cases(self) -> List[TriageItem]:
        return [
            i for i in self._triage_items.values()
            if i.priority == TriagePriority.CRITICAL and not i.reviewed
        ]

    def get_metrics(self) -> Dict[str, Any]:
        items = list(self._triage_items.values())
        reviewed = [i for i in items if i.reviewed]

        priority_counts = {}
        for item in items:
            priority_counts[item.priority.value] = priority_counts.get(item.priority.value, 0) + 1

        reason_counts = {}
        for item in items:
            for reason in item.reasons:
                reason_counts[reason.value] = reason_counts.get(reason.value, 0) + 1

        return {
            "total_triaged": len(items),
            "reviewed": len(reviewed),
            "pending_review": len(items) - len(reviewed),
            "by_priority": priority_counts,
            "by_reason": reason_counts,
            "average_score": sum(i.score for i in items) / len(items) if items else 0,
            "reports_generated": len(self._triage_reports),
        }


__all__ = [
    "InvestigationStatus",
    "TriagePriority",
    "TriageReason",
    "InvestigationResult",
    "TriageItem",
    "TriageReport",
    "AutoInvestigatePipeline",
    "DailyCaseTriageEngine",
]
