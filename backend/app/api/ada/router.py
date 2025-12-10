"""
Phase 20: Autonomous Detective AI (ADA) API Router

Comprehensive REST API endpoints for all ADA modules.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from ...ada.crime_scene_engine import (
    SceneReconstructionEngine,
    SpatialEvidenceMapper,
    TrajectoryRebuilder,
    CrimeScene3DModel,
    EvidenceType,
    SpatterPattern,
    ReconstructionStatus,
)
from ...ada.offender_modeling import (
    BehavioralSignatureEngine,
    OffenderPredictionModel,
    ModusOperandiClusterer,
    UnknownSuspectProfiler,
    OffenseType,
    RiskLevel,
    ProfileConfidence,
)
from ...ada.case_theory_engine import (
    HypothesisGenerator,
    ContradictionChecker,
    EvidenceWeightingEngine,
    CaseNarrativeBuilder,
    HypothesisStatus,
    EvidenceStrength,
)
from ...ada.evidence_graph import (
    EvidenceGraphExpander,
    BehavioralEdgeBuilder,
    SimilarityScoreEngine,
    UnsolvedCaseLinker,
    NodeType,
    EdgeType,
)
from ...ada.reporting_engine import (
    DraftReportBuilder,
    DetectiveBriefGenerator,
    CourtReadyEvidencePacketGenerator,
    SupervisorReviewMode,
    ReportType,
    ReportStatus,
    ReviewDecision,
)
from ...ada.autonomous_investigator import (
    AutoInvestigatePipeline,
    DailyCaseTriageEngine,
    InvestigationStatus,
    TriagePriority,
)

router = APIRouter(prefix="/ada", tags=["Autonomous Detective AI"])

scene_engine = SceneReconstructionEngine()
evidence_mapper = SpatialEvidenceMapper()
trajectory_rebuilder = TrajectoryRebuilder(evidence_mapper)
scene_3d_model = CrimeScene3DModel()

signature_engine = BehavioralSignatureEngine()
prediction_model = OffenderPredictionModel(signature_engine)
mo_clusterer = ModusOperandiClusterer(signature_engine)
suspect_profiler = UnknownSuspectProfiler(signature_engine)

hypothesis_generator = HypothesisGenerator()
contradiction_checker = ContradictionChecker(hypothesis_generator)
evidence_weighting = EvidenceWeightingEngine()
narrative_builder = CaseNarrativeBuilder(hypothesis_generator, evidence_weighting)

graph_expander = EvidenceGraphExpander()
edge_builder = BehavioralEdgeBuilder(graph_expander)
similarity_engine = SimilarityScoreEngine(graph_expander)
case_linker = UnsolvedCaseLinker(graph_expander, similarity_engine)

report_builder = DraftReportBuilder()
brief_generator = DetectiveBriefGenerator()
court_packet_generator = CourtReadyEvidencePacketGenerator()
supervisor_review = SupervisorReviewMode(report_builder)

auto_investigate = AutoInvestigatePipeline()
triage_engine = DailyCaseTriageEngine()


class CreateReconstructionRequest(BaseModel):
    case_id: str
    scene_type: str = "indoor"
    location: Dict[str, Any] = Field(default_factory=dict)
    bounds: Dict[str, float] = Field(default_factory=dict)


class RegisterEvidenceRequest(BaseModel):
    case_id: str
    evidence_type: str
    position: Dict[str, float]
    description: str = ""
    collected_by: str = "unknown"


class CreateTrajectoryRequest(BaseModel):
    case_id: str
    subject_type: str = "suspect"
    subject_id: Optional[str] = None


class AnalyzeBloodSpatterRequest(BaseModel):
    case_id: str
    spatter_id: str
    pattern_type: str
    position: Dict[str, float]
    area_cm2: float = 0.0
    droplet_count: int = 0


class AnalyzeCaseRequest(BaseModel):
    case_id: str
    case_data: Dict[str, Any]
    offender_id: Optional[str] = None


class PredictOffenseRequest(BaseModel):
    offender_id: Optional[str] = None
    signature_id: Optional[str] = None


class ClusterCasesRequest(BaseModel):
    case_ids: List[str]
    offense_type: str
    similarity_threshold: float = 0.6


class GenerateProfileRequest(BaseModel):
    case_ids: List[str]
    case_data: List[Dict[str, Any]]


class GenerateHypothesesRequest(BaseModel):
    case_id: str
    case_data: Dict[str, Any]
    evidence_items: List[Dict[str, Any]]
    suspects: Optional[List[Dict[str, Any]]] = None


class CheckContradictionsRequest(BaseModel):
    hypothesis_id: str
    evidence_items: List[Dict[str, Any]]
    case_data: Dict[str, Any]


class CalculateWeightRequest(BaseModel):
    case_id: str
    evidence_id: str
    evidence_data: Dict[str, Any]
    suspect_id: Optional[str] = None


class BuildNarrativeRequest(BaseModel):
    case_id: str
    case_data: Dict[str, Any]
    evidence_items: List[Dict[str, Any]]
    suspects: List[Dict[str, Any]]


class AddNodeRequest(BaseModel):
    node_type: str
    label: str
    properties: Optional[Dict[str, Any]] = None
    case_ids: Optional[List[str]] = None


class AddEdgeRequest(BaseModel):
    edge_type: str
    source_id: str
    target_id: str
    weight: float = 1.0
    confidence: float = 0.5
    properties: Optional[Dict[str, Any]] = None


class ExpandFromCaseRequest(BaseModel):
    case_id: str
    case_data: Dict[str, Any]


class CalculateSimilarityRequest(BaseModel):
    case_id_1: str
    case_id_2: str
    case_data_1: Dict[str, Any]
    case_data_2: Dict[str, Any]


class LinkCasesRequest(BaseModel):
    unsolved_cases: List[Dict[str, Any]]
    min_similarity: float = 0.6


class CreateReportRequest(BaseModel):
    case_id: str
    report_type: str
    case_data: Dict[str, Any]
    evidence_items: List[Dict[str, Any]]
    suspects: List[Dict[str, Any]]


class GenerateBriefRequest(BaseModel):
    case_id: str
    case_data: Dict[str, Any]
    evidence_items: List[Dict[str, Any]]
    suspects: List[Dict[str, Any]]
    hypotheses: Optional[List[Dict[str, Any]]] = None


class GenerateCourtPacketRequest(BaseModel):
    case_id: str
    case_number: str
    defendant_name: str
    charges: List[str]
    evidence_items: List[Dict[str, Any]]
    witnesses: List[Dict[str, Any]]
    expert_witnesses: Optional[List[Dict[str, Any]]] = None


class StartReviewRequest(BaseModel):
    report_id: str
    reviewer: str


class AddCommentRequest(BaseModel):
    session_id: str
    comment: str
    comment_type: str = "general"
    section_id: Optional[str] = None


class CompleteReviewRequest(BaseModel):
    session_id: str
    decision: str
    overall_notes: str = ""


class InvestigateRequest(BaseModel):
    case_id: str
    case_data: Dict[str, Any]
    evidence_items: List[Dict[str, Any]]
    suspects: Optional[List[Dict[str, Any]]] = None
    related_cases: Optional[List[Dict[str, Any]]] = None


class TriageCaseRequest(BaseModel):
    case_id: str
    case_data: Dict[str, Any]


class RunTriageRequest(BaseModel):
    cases: List[Dict[str, Any]]


@router.post("/scene/reconstruction")
async def create_reconstruction(request: CreateReconstructionRequest):
    reconstruction = scene_engine.create_reconstruction(
        case_id=request.case_id,
        scene_type=request.scene_type,
        location=request.location,
        bounds=request.bounds,
    )
    return {
        "reconstruction_id": reconstruction.reconstruction_id,
        "case_id": reconstruction.case_id,
        "status": reconstruction.status.value,
        "created_at": reconstruction.created_at.isoformat(),
    }


@router.get("/scene/reconstruction/{reconstruction_id}")
async def get_reconstruction(reconstruction_id: str):
    reconstruction = scene_engine.get_reconstruction(reconstruction_id)
    if not reconstruction:
        raise HTTPException(status_code=404, detail="Reconstruction not found")
    return {
        "reconstruction_id": reconstruction.reconstruction_id,
        "case_id": reconstruction.case_id,
        "scene_type": reconstruction.scene_type,
        "status": reconstruction.status.value,
        "confidence_score": reconstruction.confidence_score,
        "evidence_count": len(reconstruction.evidence_items),
        "created_at": reconstruction.created_at.isoformat(),
    }


@router.get("/scene/reconstructions")
async def list_reconstructions(
    case_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=100, le=500),
):
    reconstructions = scene_engine.get_reconstructions(
        case_id=case_id,
        status=ReconstructionStatus(status) if status else None,
        limit=limit,
    )
    return {
        "count": len(reconstructions),
        "reconstructions": [
            {
                "reconstruction_id": r.reconstruction_id,
                "case_id": r.case_id,
                "status": r.status.value,
                "confidence_score": r.confidence_score,
            }
            for r in reconstructions
        ],
    }


@router.post("/scene/reconstruction/{reconstruction_id}/analyze")
async def analyze_scene(reconstruction_id: str):
    reconstruction = scene_engine.analyze_scene(reconstruction_id)
    if not reconstruction:
        raise HTTPException(status_code=404, detail="Reconstruction not found")
    return {
        "reconstruction_id": reconstruction.reconstruction_id,
        "status": reconstruction.status.value,
        "confidence_score": reconstruction.confidence_score,
        "analysis_notes": reconstruction.analysis_notes,
    }


@router.get("/scene/reconstruction/{reconstruction_id}/timeline")
async def get_scene_timeline(reconstruction_id: str):
    timeline = scene_engine.generate_timeline(reconstruction_id)
    return {"reconstruction_id": reconstruction_id, "timeline": timeline}


@router.get("/scene/metrics")
async def get_scene_metrics():
    return scene_engine.get_metrics()


@router.post("/evidence/register")
async def register_evidence(request: RegisterEvidenceRequest):
    evidence = evidence_mapper.register_evidence(
        case_id=request.case_id,
        evidence_type=request.evidence_type,
        position=request.position,
        description=request.description,
        collected_by=request.collected_by,
    )
    return {
        "evidence_id": evidence.evidence_id,
        "case_id": evidence.case_id,
        "evidence_type": evidence.evidence_type.value,
        "position": evidence.position,
    }


@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    evidence = evidence_mapper.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {
        "evidence_id": evidence.evidence_id,
        "case_id": evidence.case_id,
        "evidence_type": evidence.evidence_type.value,
        "position": evidence.position,
        "description": evidence.description,
        "chain_of_custody": evidence.chain_of_custody,
    }


@router.get("/evidence/case/{case_id}")
async def get_case_evidence(case_id: str):
    evidence_list = evidence_mapper.get_case_evidence(case_id)
    return {
        "case_id": case_id,
        "count": len(evidence_list),
        "evidence": [
            {
                "evidence_id": e.evidence_id,
                "evidence_type": e.evidence_type.value,
                "position": e.position,
                "description": e.description,
            }
            for e in evidence_list
        ],
    }


@router.get("/evidence/case/{case_id}/clusters")
async def get_evidence_clusters(case_id: str, num_clusters: int = 3):
    clusters = evidence_mapper.cluster_evidence(case_id, num_clusters)
    return {"case_id": case_id, "clusters": clusters}


@router.get("/evidence/case/{case_id}/heatmap")
async def get_evidence_heatmap(case_id: str, resolution: int = 10):
    heatmap = evidence_mapper.get_spatial_heatmap(case_id, resolution)
    return {"case_id": case_id, "heatmap": heatmap}


@router.get("/evidence/case/{case_id}/entry-exit")
async def analyze_entry_exit(case_id: str):
    analysis = evidence_mapper.analyze_entry_exit_points(case_id)
    return {
        "case_id": case_id,
        "entry_points": [
            {"evidence_id": e.evidence_id, "position": e.position}
            for e in analysis.get("entry_points", [])
        ],
        "exit_points": [
            {"evidence_id": e.evidence_id, "position": e.position}
            for e in analysis.get("exit_points", [])
        ],
    }


@router.post("/trajectory/create")
async def create_trajectory(request: CreateTrajectoryRequest):
    trajectory = trajectory_rebuilder.create_trajectory(
        case_id=request.case_id,
        subject_type=request.subject_type,
        subject_id=request.subject_id,
    )
    return {
        "trajectory_id": trajectory.trajectory_id,
        "case_id": trajectory.case_id,
        "subject_type": trajectory.subject_type,
    }


@router.get("/trajectory/{trajectory_id}")
async def get_trajectory(trajectory_id: str):
    trajectory = trajectory_rebuilder.get_trajectory(trajectory_id)
    if not trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")
    return {
        "trajectory_id": trajectory.trajectory_id,
        "case_id": trajectory.case_id,
        "subject_type": trajectory.subject_type,
        "points": [
            {"position": p.position, "movement_type": p.movement_type.value}
            for p in trajectory.points
        ],
        "total_distance": trajectory.total_distance,
        "confidence_score": trajectory.confidence_score,
    }


@router.get("/trajectory/case/{case_id}")
async def get_case_trajectories(case_id: str):
    trajectories = trajectory_rebuilder.get_case_trajectories(case_id)
    return {
        "case_id": case_id,
        "count": len(trajectories),
        "trajectories": [
            {
                "trajectory_id": t.trajectory_id,
                "subject_type": t.subject_type,
                "total_distance": t.total_distance,
            }
            for t in trajectories
        ],
    }


@router.post("/trajectory/infer/{case_id}")
async def infer_trajectory(case_id: str):
    trajectory = trajectory_rebuilder.infer_movement_from_evidence(case_id)
    if not trajectory:
        raise HTTPException(status_code=404, detail="Could not infer trajectory")
    return {
        "trajectory_id": trajectory.trajectory_id,
        "points_count": len(trajectory.points),
        "total_distance": trajectory.total_distance,
    }


@router.post("/spatter/analyze")
async def analyze_blood_spatter(request: AnalyzeBloodSpatterRequest):
    analysis = trajectory_rebuilder.analyze_blood_spatter(
        case_id=request.case_id,
        spatter_id=request.spatter_id,
        pattern_type=SpatterPattern(request.pattern_type),
        position=request.position,
        area_cm2=request.area_cm2,
        droplet_count=request.droplet_count,
    )
    return {
        "analysis_id": analysis.analysis_id,
        "case_id": analysis.case_id,
        "pattern_type": analysis.pattern_type.value,
        "impact_angle": analysis.impact_angle,
        "origin_point": analysis.origin_point,
        "confidence_score": analysis.confidence_score,
    }


@router.post("/3d-model/generate/{reconstruction_id}")
async def generate_3d_model(reconstruction_id: str):
    model = scene_3d_model.generate_model(reconstruction_id)
    return {
        "model_id": model.model_id,
        "reconstruction_id": model.reconstruction_id,
        "format": model.format,
        "evidence_markers": len(model.evidence_markers),
    }


@router.get("/3d-model/{model_id}")
async def get_3d_model(model_id: str):
    model = scene_3d_model.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="3D model not found")
    return {
        "model_id": model.model_id,
        "reconstruction_id": model.reconstruction_id,
        "format": model.format,
        "evidence_markers": model.evidence_markers,
        "camera_positions": model.camera_positions,
    }


@router.post("/signature/analyze")
async def analyze_behavioral_signature(request: AnalyzeCaseRequest):
    signatures = signature_engine.analyze_case(
        case_id=request.case_id,
        case_data=request.case_data,
        offender_id=request.offender_id,
    )
    return {
        "case_id": request.case_id,
        "signatures_count": len(signatures),
        "signatures": [
            {
                "signature_id": s.signature_id,
                "category": s.category.value,
                "patterns": s.patterns,
                "overall_score": s.overall_score,
            }
            for s in signatures
        ],
    }


@router.get("/signature/{signature_id}")
async def get_signature(signature_id: str):
    signature = signature_engine.get_signature(signature_id)
    if not signature:
        raise HTTPException(status_code=404, detail="Signature not found")
    return {
        "signature_id": signature.signature_id,
        "case_id": signature.case_id,
        "category": signature.category.value,
        "behaviors": signature.behaviors,
        "patterns": signature.patterns,
        "overall_score": signature.overall_score,
        "linked_cases": signature.linked_cases,
    }


@router.get("/signature/{signature_id}/similar")
async def find_similar_signatures(signature_id: str, threshold: float = 0.5):
    similar = signature_engine.find_similar_signatures(signature_id, threshold)
    return {
        "signature_id": signature_id,
        "similar_count": len(similar),
        "similar": [{"signature_id": sid, "similarity": sim} for sid, sim in similar],
    }


@router.post("/signature/{signature_id}/link-cases")
async def link_cases_by_signature(signature_id: str, threshold: float = 0.6):
    linked = signature_engine.link_cases_by_signature(signature_id, threshold)
    return {"signature_id": signature_id, "linked_cases": linked}


@router.get("/signature/metrics")
async def get_signature_metrics():
    return signature_engine.get_metrics()


@router.post("/prediction/predict")
async def predict_next_offense(request: PredictOffenseRequest):
    prediction = prediction_model.predict_next_offense(
        offender_id=request.offender_id,
        signature_id=request.signature_id,
    )
    if not prediction:
        raise HTTPException(status_code=404, detail="Could not generate prediction")
    return {
        "prediction_id": prediction.prediction_id,
        "predicted_offense_type": prediction.predicted_offense_type.value,
        "predicted_location": prediction.predicted_location,
        "predicted_timeframe": prediction.predicted_timeframe,
        "risk_level": prediction.risk_level.value,
        "confidence_score": prediction.confidence_score,
        "recommended_actions": prediction.recommended_actions,
    }


@router.get("/prediction/{prediction_id}")
async def get_prediction(prediction_id: str):
    prediction = prediction_model.get_prediction(prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {
        "prediction_id": prediction.prediction_id,
        "offender_id": prediction.offender_id,
        "predicted_offense_type": prediction.predicted_offense_type.value,
        "risk_level": prediction.risk_level.value,
        "confidence_score": prediction.confidence_score,
    }


@router.get("/prediction/high-risk")
async def get_high_risk_predictions():
    predictions = prediction_model.get_high_risk_predictions()
    return {
        "count": len(predictions),
        "predictions": [
            {
                "prediction_id": p.prediction_id,
                "offender_id": p.offender_id,
                "risk_level": p.risk_level.value,
                "confidence_score": p.confidence_score,
            }
            for p in predictions
        ],
    }


@router.post("/mo-cluster/cluster")
async def cluster_cases_by_mo(request: ClusterCasesRequest):
    clusters = mo_clusterer.cluster_cases(
        case_ids=request.case_ids,
        offense_type=OffenseType(request.offense_type),
        similarity_threshold=request.similarity_threshold,
    )
    return {
        "clusters_count": len(clusters),
        "clusters": [
            {
                "cluster_id": c.cluster_id,
                "cluster_name": c.cluster_name,
                "case_count": len(c.case_ids),
                "common_behaviors": c.common_behaviors,
                "cluster_confidence": c.cluster_confidence,
            }
            for c in clusters
        ],
    }


@router.get("/mo-cluster/{cluster_id}")
async def get_mo_cluster(cluster_id: str):
    cluster = mo_clusterer.get_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {
        "cluster_id": cluster.cluster_id,
        "cluster_name": cluster.cluster_name,
        "offense_type": cluster.offense_type.value,
        "case_ids": cluster.case_ids,
        "common_behaviors": cluster.common_behaviors,
        "cluster_confidence": cluster.cluster_confidence,
    }


@router.get("/mo-cluster")
async def list_mo_clusters(offense_type: Optional[str] = None, min_cases: int = 2):
    clusters = mo_clusterer.get_clusters(
        offense_type=OffenseType(offense_type) if offense_type else None,
        min_cases=min_cases,
    )
    return {
        "count": len(clusters),
        "clusters": [
            {
                "cluster_id": c.cluster_id,
                "cluster_name": c.cluster_name,
                "case_count": len(c.case_ids),
            }
            for c in clusters
        ],
    }


@router.post("/profile/generate")
async def generate_suspect_profile(request: GenerateProfileRequest):
    profile = suspect_profiler.generate_profile(
        case_ids=request.case_ids,
        case_data=request.case_data,
    )
    return {
        "profile_id": profile.profile_id,
        "case_ids": profile.case_ids,
        "demographics": profile.demographics,
        "psychological_traits": profile.psychological_traits,
        "behavioral_indicators": profile.behavioral_indicators,
        "geographic_profile": profile.geographic_profile,
        "risk_assessment": profile.risk_assessment,
        "confidence": profile.confidence.value,
        "confidence_score": profile.confidence_score,
    }


@router.get("/profile/{profile_id}")
async def get_suspect_profile(profile_id: str):
    profile = suspect_profiler.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "profile_id": profile.profile_id,
        "case_ids": profile.case_ids,
        "demographics": profile.demographics,
        "psychological_traits": profile.psychological_traits,
        "modus_operandi": profile.modus_operandi,
        "confidence": profile.confidence.value,
    }


@router.get("/profile")
async def list_profiles(confidence: Optional[str] = None, limit: int = 100):
    profiles = suspect_profiler.get_profiles(
        confidence=ProfileConfidence(confidence) if confidence else None,
        limit=limit,
    )
    return {
        "count": len(profiles),
        "profiles": [
            {
                "profile_id": p.profile_id,
                "case_count": len(p.case_ids),
                "confidence": p.confidence.value,
            }
            for p in profiles
        ],
    }


@router.post("/hypothesis/generate")
async def generate_hypotheses(request: GenerateHypothesesRequest):
    hypotheses = hypothesis_generator.generate_hypotheses(
        case_id=request.case_id,
        case_data=request.case_data,
        evidence_items=request.evidence_items,
        suspects=request.suspects,
    )
    return {
        "case_id": request.case_id,
        "hypotheses_count": len(hypotheses),
        "hypotheses": [
            {
                "hypothesis_id": h.hypothesis_id,
                "title": h.title,
                "hypothesis_type": h.hypothesis_type,
                "confidence_score": h.confidence_score,
                "status": h.status.value,
            }
            for h in hypotheses
        ],
    }


@router.get("/hypothesis/{hypothesis_id}")
async def get_hypothesis(hypothesis_id: str):
    hypothesis = hypothesis_generator.get_hypothesis(hypothesis_id)
    if not hypothesis:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return {
        "hypothesis_id": hypothesis.hypothesis_id,
        "case_id": hypothesis.case_id,
        "title": hypothesis.title,
        "description": hypothesis.description,
        "hypothesis_type": hypothesis.hypothesis_type,
        "status": hypothesis.status.value,
        "confidence_score": hypothesis.confidence_score,
        "supporting_evidence": hypothesis.supporting_evidence,
        "contradicting_evidence": hypothesis.contradicting_evidence,
    }


@router.get("/hypothesis/case/{case_id}")
async def get_case_hypotheses(
    case_id: str,
    status: Optional[str] = None,
    hypothesis_type: Optional[str] = None,
):
    hypotheses = hypothesis_generator.get_case_hypotheses(
        case_id=case_id,
        status=HypothesisStatus(status) if status else None,
        hypothesis_type=hypothesis_type,
    )
    return {
        "case_id": case_id,
        "count": len(hypotheses),
        "hypotheses": [
            {
                "hypothesis_id": h.hypothesis_id,
                "title": h.title,
                "status": h.status.value,
                "confidence_score": h.confidence_score,
            }
            for h in hypotheses
        ],
    }


@router.get("/hypothesis/case/{case_id}/ranked")
async def get_ranked_hypotheses(case_id: str):
    ranked = hypothesis_generator.rank_hypotheses(case_id)
    return {
        "case_id": case_id,
        "ranked": [
            {
                "hypothesis_id": h.hypothesis_id,
                "title": h.title,
                "rank_score": score,
            }
            for h, score in ranked
        ],
    }


@router.post("/contradiction/check")
async def check_contradictions(request: CheckContradictionsRequest):
    contradictions = contradiction_checker.check_hypothesis(
        hypothesis_id=request.hypothesis_id,
        evidence_items=request.evidence_items,
        case_data=request.case_data,
    )
    return {
        "hypothesis_id": request.hypothesis_id,
        "contradictions_count": len(contradictions),
        "contradictions": [
            {
                "contradiction_id": c.contradiction_id,
                "contradiction_type": c.contradiction_type,
                "description": c.description,
                "severity": c.severity,
            }
            for c in contradictions
        ],
    }


@router.get("/contradiction/{contradiction_id}")
async def get_contradiction(contradiction_id: str):
    contradiction = contradiction_checker.get_contradiction(contradiction_id)
    if not contradiction:
        raise HTTPException(status_code=404, detail="Contradiction not found")
    return {
        "contradiction_id": contradiction.contradiction_id,
        "hypothesis_id": contradiction.hypothesis_id,
        "contradiction_type": contradiction.contradiction_type,
        "description": contradiction.description,
        "severity": contradiction.severity,
        "resolution_status": contradiction.resolution_status,
    }


@router.get("/contradiction/case/{case_id}/unresolved")
async def get_unresolved_contradictions(case_id: str):
    contradictions = contradiction_checker.get_unresolved_contradictions(case_id)
    return {
        "case_id": case_id,
        "count": len(contradictions),
        "contradictions": [
            {
                "contradiction_id": c.contradiction_id,
                "hypothesis_id": c.hypothesis_id,
                "severity": c.severity,
            }
            for c in contradictions
        ],
    }


@router.post("/evidence-weight/calculate")
async def calculate_evidence_weight(request: CalculateWeightRequest):
    weight = evidence_weighting.calculate_weight(
        case_id=request.case_id,
        evidence_id=request.evidence_id,
        evidence_data=request.evidence_data,
        suspect_id=request.suspect_id,
    )
    return {
        "weight_id": weight.weight_id,
        "evidence_id": weight.evidence_id,
        "weight_score": weight.weight_score,
        "strength": weight.strength.value,
        "relevance_score": weight.relevance_score,
        "reliability_score": weight.reliability_score,
        "probative_value": weight.probative_value,
    }


@router.get("/evidence-weight/case/{case_id}")
async def get_case_evidence_weights(
    case_id: str,
    suspect_id: Optional[str] = None,
    min_strength: Optional[str] = None,
):
    weights = evidence_weighting.get_evidence_weights(
        case_id=case_id,
        suspect_id=suspect_id,
        min_strength=EvidenceStrength(min_strength) if min_strength else None,
    )
    return {
        "case_id": case_id,
        "count": len(weights),
        "weights": [
            {
                "weight_id": w.weight_id,
                "evidence_id": w.evidence_id,
                "weight_score": w.weight_score,
                "strength": w.strength.value,
            }
            for w in weights
        ],
    }


@router.get("/evidence-weight/cumulative/{case_id}/{suspect_id}")
async def get_cumulative_weight(case_id: str, suspect_id: str):
    result = evidence_weighting.calculate_cumulative_weight(case_id, suspect_id)
    return result


@router.post("/narrative/build")
async def build_case_narrative(request: BuildNarrativeRequest):
    narrative = narrative_builder.build_narrative(
        case_id=request.case_id,
        case_data=request.case_data,
        evidence_items=request.evidence_items,
        suspects=request.suspects,
    )
    return {
        "narrative_id": narrative.narrative_id,
        "case_id": narrative.case_id,
        "title": narrative.title,
        "version": narrative.version,
        "word_count": narrative.word_count,
        "sections": list(narrative.sections.keys()),
    }


@router.get("/narrative/{narrative_id}")
async def get_narrative(narrative_id: str):
    narrative = narrative_builder.get_narrative(narrative_id)
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return {
        "narrative_id": narrative.narrative_id,
        "case_id": narrative.case_id,
        "title": narrative.title,
        "sections": narrative.sections,
        "word_count": narrative.word_count,
        "reviewed": narrative.reviewed,
    }


@router.get("/narrative/{narrative_id}/export")
async def export_narrative(narrative_id: str, format: str = "text"):
    content = narrative_builder.export_narrative(narrative_id, format)
    if not content:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return {"narrative_id": narrative_id, "format": format, "content": content}


@router.post("/graph/node")
async def add_graph_node(request: AddNodeRequest):
    node = graph_expander.add_node(
        node_type=NodeType(request.node_type),
        label=request.label,
        properties=request.properties,
        case_ids=request.case_ids,
    )
    return {
        "node_id": node.node_id,
        "node_type": node.node_type.value,
        "label": node.label,
    }


@router.get("/graph/node/{node_id}")
async def get_graph_node(node_id: str):
    node = graph_expander.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {
        "node_id": node.node_id,
        "node_type": node.node_type.value,
        "label": node.label,
        "properties": node.properties,
        "case_ids": node.case_ids,
    }


@router.post("/graph/edge")
async def add_graph_edge(request: AddEdgeRequest):
    edge = graph_expander.add_edge(
        edge_type=EdgeType(request.edge_type),
        source_id=request.source_id,
        target_id=request.target_id,
        weight=request.weight,
        confidence=request.confidence,
        properties=request.properties,
    )
    if not edge:
        raise HTTPException(status_code=400, detail="Could not create edge")
    return {
        "edge_id": edge.edge_id,
        "edge_type": edge.edge_type.value,
        "source_id": edge.source_id,
        "target_id": edge.target_id,
        "weight": edge.weight,
    }


@router.post("/graph/expand")
async def expand_graph_from_case(request: ExpandFromCaseRequest):
    nodes = graph_expander.expand_from_case(
        case_id=request.case_id,
        case_data=request.case_data,
    )
    return {
        "case_id": request.case_id,
        "nodes_created": len(nodes),
        "nodes": [{"node_id": n.node_id, "node_type": n.node_type.value} for n in nodes],
    }


@router.get("/graph/case/{case_id}/nodes")
async def get_case_graph_nodes(case_id: str):
    nodes = graph_expander.get_case_nodes(case_id)
    return {
        "case_id": case_id,
        "count": len(nodes),
        "nodes": [
            {"node_id": n.node_id, "node_type": n.node_type.value, "label": n.label}
            for n in nodes
        ],
    }


@router.get("/graph/node/{node_id}/connected")
async def get_connected_nodes(node_id: str, max_depth: int = 1):
    connected = graph_expander.get_connected_nodes(node_id, max_depth=max_depth)
    return {
        "node_id": node_id,
        "connected_count": len(connected),
        "connected": [
            {
                "node_id": n.node_id,
                "node_type": n.node_type.value,
                "edge_type": e.edge_type.value,
                "depth": d,
            }
            for n, e, d in connected
        ],
    }


@router.get("/graph/statistics")
async def get_graph_statistics():
    return graph_expander.get_graph_statistics()


@router.post("/similarity/calculate")
async def calculate_case_similarity(request: CalculateSimilarityRequest):
    result = similarity_engine.calculate_similarity(
        case_id_1=request.case_id_1,
        case_id_2=request.case_id_2,
        case_data_1=request.case_data_1,
        case_data_2=request.case_data_2,
    )
    return {
        "result_id": result.result_id,
        "source_case_id": result.source_case_id,
        "target_case_id": result.target_case_id,
        "overall_similarity": result.overall_similarity,
        "behavioral_similarity": result.behavioral_similarity,
        "temporal_similarity": result.temporal_similarity,
        "geographic_similarity": result.geographic_similarity,
        "mo_similarity": result.mo_similarity,
        "common_entities": result.common_entities,
        "matching_patterns": result.matching_patterns,
    }


@router.post("/case-link/analyze")
async def analyze_and_link_cases(request: LinkCasesRequest):
    unsolved = [(c["case_id"], c) for c in request.unsolved_cases]
    links = case_linker.analyze_and_link(unsolved, request.min_similarity)
    return {
        "links_created": len(links),
        "links": [
            {
                "link_id": l.link_id,
                "case_id_1": l.case_id_1,
                "case_id_2": l.case_id_2,
                "link_type": l.link_type,
                "strength": l.strength,
            }
            for l in links
        ],
    }


@router.get("/case-link/{link_id}")
async def get_case_link(link_id: str):
    link = case_linker.get_link(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {
        "link_id": link.link_id,
        "case_id_1": link.case_id_1,
        "case_id_2": link.case_id_2,
        "link_type": link.link_type,
        "strength": link.strength,
        "confirmed": link.confirmed,
        "evidence_basis": link.evidence_basis,
    }


@router.post("/case-link/{link_id}/confirm")
async def confirm_case_link(link_id: str, confirmed_by: str, notes: str = ""):
    link = case_linker.confirm_link(link_id, confirmed_by, notes)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"link_id": link.link_id, "confirmed": link.confirmed}


@router.get("/case-link/case/{case_id}")
async def get_case_links(case_id: str, confirmed_only: bool = False):
    links = case_linker.get_case_links(case_id, confirmed_only)
    return {
        "case_id": case_id,
        "count": len(links),
        "links": [
            {"link_id": l.link_id, "linked_case": l.case_id_2 if l.case_id_1 == case_id else l.case_id_1}
            for l in links
        ],
    }


@router.get("/case-link/clusters")
async def find_case_clusters(min_cluster_size: int = 3):
    clusters = case_linker.find_case_clusters(min_cluster_size)
    return {
        "cluster_count": len(clusters),
        "clusters": [{"case_ids": c, "size": len(c)} for c in clusters],
    }


@router.get("/case-link/metrics")
async def get_case_link_metrics():
    return case_linker.get_metrics()


@router.post("/report/create")
async def create_report(request: CreateReportRequest):
    report = report_builder.create_report(
        case_id=request.case_id,
        report_type=ReportType(request.report_type),
        case_data=request.case_data,
        evidence_items=request.evidence_items,
        suspects=request.suspects,
    )
    return {
        "report_id": report.report_id,
        "case_id": report.case_id,
        "report_type": report.report_type.value,
        "title": report.title,
        "status": report.status.value,
        "word_count": report.word_count,
    }


@router.get("/report/{report_id}")
async def get_report(report_id: str):
    report = report_builder.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "report_id": report.report_id,
        "case_id": report.case_id,
        "report_type": report.report_type.value,
        "title": report.title,
        "status": report.status.value,
        "version": report.version,
        "sections": [{"section_id": s.section_id, "title": s.title} for s in report.sections],
        "word_count": report.word_count,
    }


@router.get("/report/{report_id}/export")
async def export_report(report_id: str, format: str = "text"):
    content = report_builder.export_report(report_id, format)
    if not content:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"report_id": report_id, "format": format, "content": content}


@router.get("/report/case/{case_id}")
async def get_case_reports(case_id: str, report_type: Optional[str] = None):
    reports = report_builder.get_case_reports(
        case_id=case_id,
        report_type=ReportType(report_type) if report_type else None,
    )
    return {
        "case_id": case_id,
        "count": len(reports),
        "reports": [
            {
                "report_id": r.report_id,
                "report_type": r.report_type.value,
                "status": r.status.value,
            }
            for r in reports
        ],
    }


@router.post("/brief/generate")
async def generate_detective_brief(request: GenerateBriefRequest):
    brief = brief_generator.generate_brief(
        case_id=request.case_id,
        case_data=request.case_data,
        evidence_items=request.evidence_items,
        suspects=request.suspects,
        hypotheses=request.hypotheses,
    )
    return {
        "brief_id": brief.brief_id,
        "case_id": brief.case_id,
        "title": brief.title,
        "key_findings": brief.key_findings,
        "recommended_actions": brief.recommended_actions,
        "risk_assessment": brief.risk_assessment,
        "page_count": brief.page_count,
    }


@router.get("/brief/{brief_id}")
async def get_detective_brief(brief_id: str):
    brief = brief_generator.get_brief(brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return {
        "brief_id": brief.brief_id,
        "case_id": brief.case_id,
        "title": brief.title,
        "executive_summary": brief.executive_summary,
        "key_findings": brief.key_findings,
        "suspects_summary": brief.suspects_summary,
        "evidence_highlights": brief.evidence_highlights,
        "recommended_actions": brief.recommended_actions,
    }


@router.post("/court-packet/generate")
async def generate_court_packet(request: GenerateCourtPacketRequest):
    packet = court_packet_generator.generate_packet(
        case_id=request.case_id,
        case_number=request.case_number,
        defendant_name=request.defendant_name,
        charges=request.charges,
        evidence_items=request.evidence_items,
        witnesses=request.witnesses,
        expert_witnesses=request.expert_witnesses,
    )
    return {
        "packet_id": packet.packet_id,
        "case_id": packet.case_id,
        "case_number": packet.case_number,
        "defendant_name": packet.defendant_name,
        "evidence_items_count": len(packet.evidence_items),
        "total_pages": packet.total_pages,
        "pdf_url": packet.pdf_url,
        "status": packet.status,
    }


@router.get("/court-packet/{packet_id}")
async def get_court_packet(packet_id: str):
    packet = court_packet_generator.get_packet(packet_id)
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    return {
        "packet_id": packet.packet_id,
        "case_id": packet.case_id,
        "case_number": packet.case_number,
        "defendant_name": packet.defendant_name,
        "charges": packet.charges,
        "evidence_items": [
            {"item_id": i.item_id, "description": i.description}
            for i in packet.evidence_items
        ],
        "legal_standards_met": packet.legal_standards_met,
        "status": packet.status,
    }


@router.post("/court-packet/{packet_id}/finalize")
async def finalize_court_packet(packet_id: str, prosecutor_approval: str):
    packet = court_packet_generator.finalize_packet(packet_id, prosecutor_approval)
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    return {"packet_id": packet.packet_id, "status": packet.status}


@router.post("/review/start")
async def start_review(request: StartReviewRequest):
    session = supervisor_review.start_review(
        report_id=request.report_id,
        reviewer=request.reviewer,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "session_id": session.session_id,
        "report_id": session.report_id,
        "reviewer": session.reviewer,
        "started_at": session.started_at.isoformat(),
    }


@router.post("/review/comment")
async def add_review_comment(request: AddCommentRequest):
    comment = supervisor_review.add_comment(
        session_id=request.session_id,
        comment=request.comment,
        comment_type=request.comment_type,
        section_id=request.section_id,
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "comment_id": comment.comment_id,
        "comment": comment.comment,
        "comment_type": comment.comment_type,
    }


@router.post("/review/complete")
async def complete_review(request: CompleteReviewRequest):
    session = supervisor_review.complete_review(
        session_id=request.session_id,
        decision=ReviewDecision(request.decision),
        overall_notes=request.overall_notes,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session.session_id,
        "decision": session.decision.value if session.decision else None,
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
    }


@router.get("/review/{session_id}")
async def get_review_session(session_id: str):
    session = supervisor_review.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session.session_id,
        "report_id": session.report_id,
        "reviewer": session.reviewer,
        "decision": session.decision.value if session.decision else None,
        "comments_count": len(session.comments),
    }


@router.get("/review/statistics")
async def get_review_statistics():
    return supervisor_review.get_review_statistics()


@router.post("/investigate")
async def auto_investigate(request: InvestigateRequest):
    related = None
    if request.related_cases:
        related = [(c["case_id"], c) for c in request.related_cases]

    result = auto_investigate.investigate(
        case_id=request.case_id,
        case_data=request.case_data,
        evidence_items=request.evidence_items,
        suspects=request.suspects,
        related_cases=related,
    )
    return {
        "result_id": result.result_id,
        "case_id": result.case_id,
        "status": result.status.value,
        "suspects_count": len(result.suspects),
        "theories_count": len(result.theories),
        "linked_cases_count": len(result.linked_cases),
        "confidence_score": result.confidence_score,
        "processing_time_seconds": result.processing_time_seconds,
        "report_id": result.report_id,
        "brief_id": result.brief_id,
    }


@router.get("/investigate/{result_id}")
async def get_investigation_result(result_id: str):
    result = auto_investigate.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return {
        "result_id": result.result_id,
        "case_id": result.case_id,
        "status": result.status.value,
        "suspects": result.suspects,
        "theories": result.theories,
        "timeline": result.timeline,
        "linked_cases": result.linked_cases,
        "confidence_score": result.confidence_score,
        "error_message": result.error_message,
    }


@router.get("/investigate/case/{case_id}")
async def get_case_investigations(case_id: str):
    results = auto_investigate.get_case_results(case_id)
    return {
        "case_id": case_id,
        "count": len(results),
        "results": [
            {
                "result_id": r.result_id,
                "status": r.status.value,
                "confidence_score": r.confidence_score,
            }
            for r in results
        ],
    }


@router.post("/triage/case")
async def triage_case(request: TriageCaseRequest):
    item = triage_engine.triage_case(
        case_id=request.case_id,
        case_data=request.case_data,
    )
    return {
        "triage_id": item.triage_id,
        "case_id": item.case_id,
        "priority": item.priority.value,
        "score": item.score,
        "reasons": [r.value for r in item.reasons],
        "recommended_actions": item.recommended_actions,
    }


@router.post("/triage/daily")
async def run_daily_triage(request: RunTriageRequest):
    cases = [(c["case_id"], c) for c in request.cases]
    report = triage_engine.run_daily_triage(cases)
    return {
        "report_id": report.report_id,
        "report_date": report.report_date.isoformat(),
        "total_cases_reviewed": report.total_cases_reviewed,
        "critical_count": len(report.critical_cases),
        "high_priority_count": len(report.high_priority_cases),
        "medium_priority_count": len(report.medium_priority_cases),
        "low_priority_count": len(report.low_priority_cases),
        "routine_count": len(report.routine_cases),
        "summary": report.summary,
    }


@router.get("/triage/{triage_id}")
async def get_triage_item(triage_id: str):
    item = triage_engine.get_triage_item(triage_id)
    if not item:
        raise HTTPException(status_code=404, detail="Triage item not found")
    return {
        "triage_id": item.triage_id,
        "case_id": item.case_id,
        "priority": item.priority.value,
        "score": item.score,
        "reasons": [r.value for r in item.reasons],
        "recommended_actions": item.recommended_actions,
        "reviewed": item.reviewed,
    }


@router.post("/triage/{triage_id}/reviewed")
async def mark_triage_reviewed(triage_id: str, reviewer: str):
    item = triage_engine.mark_reviewed(triage_id, reviewer)
    if not item:
        raise HTTPException(status_code=404, detail="Triage item not found")
    return {"triage_id": item.triage_id, "reviewed": item.reviewed}


@router.get("/triage/critical/pending")
async def get_pending_critical_cases():
    items = triage_engine.get_pending_critical_cases()
    return {
        "count": len(items),
        "items": [
            {"triage_id": i.triage_id, "case_id": i.case_id, "score": i.score}
            for i in items
        ],
    }


@router.get("/triage/metrics")
async def get_triage_metrics():
    return triage_engine.get_metrics()


@router.get("/triage/report/{report_id}")
async def get_triage_report(report_id: str):
    report = triage_engine.get_triage_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "report_id": report.report_id,
        "report_date": report.report_date.isoformat(),
        "total_cases_reviewed": report.total_cases_reviewed,
        "summary": report.summary,
    }
