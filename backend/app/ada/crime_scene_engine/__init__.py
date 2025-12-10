"""
Phase 20: Crime Scene Engine Module

Provides crime scene reconstruction, spatial evidence mapping, trajectory rebuilding,
and 3D model generation capabilities for the Autonomous Detective AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import math


class EvidenceType(str, Enum):
    WEAPON = "weapon"
    CASING = "casing"
    BLOOD_SPATTER = "blood_spatter"
    FINGERPRINT = "fingerprint"
    DNA = "dna"
    FOOTPRINT = "footprint"
    TIRE_TRACK = "tire_track"
    FIBER = "fiber"
    HAIR = "hair"
    DOCUMENT = "document"
    DIGITAL = "digital"
    TOOL_MARK = "tool_mark"
    GLASS = "glass"
    PROJECTILE = "projectile"
    ENTRY_POINT = "entry_point"
    EXIT_POINT = "exit_point"
    IMPACT_POINT = "impact_point"
    OTHER = "other"


class SpatterPattern(str, Enum):
    CAST_OFF = "cast_off"
    IMPACT = "impact"
    ARTERIAL = "arterial"
    EXPIRATED = "expirated"
    TRANSFER = "transfer"
    DRIP = "drip"
    POOL = "pool"
    VOID = "void"
    SWIPE = "swipe"
    WIPE = "wipe"


class MovementType(str, Enum):
    ENTRY = "entry"
    EXIT = "exit"
    APPROACH = "approach"
    RETREAT = "retreat"
    STRUGGLE = "struggle"
    SEARCH = "search"
    CONCEALMENT = "concealment"
    STAGING = "staging"


class ReconstructionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


@dataclass
class EvidenceItem:
    evidence_id: str
    case_id: str
    evidence_type: EvidenceType
    position: Dict[str, float]
    description: str
    collected_at: datetime
    collected_by: str
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    linked_suspects: List[str] = field(default_factory=list)
    linked_victims: List[str] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)
    notes: str = ""
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BloodSpatterAnalysis:
    spatter_id: str
    case_id: str
    pattern_type: SpatterPattern
    position: Dict[str, float]
    area_of_origin: Dict[str, float]
    impact_angle: float
    directionality: float
    droplet_count: int
    average_droplet_size: float
    velocity_category: str
    source_height_estimate: float
    analysis_notes: str = ""
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrajectoryPoint:
    point_id: str
    position: Dict[str, float]
    timestamp_estimate: Optional[datetime]
    movement_type: MovementType
    confidence: float
    evidence_support: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class MovementTrajectory:
    trajectory_id: str
    case_id: str
    subject_type: str
    subject_id: Optional[str]
    points: List[TrajectoryPoint] = field(default_factory=list)
    total_distance: float = 0.0
    estimated_duration: Optional[float] = None
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""


@dataclass
class SceneReconstruction:
    reconstruction_id: str
    case_id: str
    scene_type: str
    location: Dict[str, Any]
    bounds: Dict[str, float]
    evidence_items: List[str] = field(default_factory=list)
    trajectories: List[str] = field(default_factory=list)
    spatter_analyses: List[str] = field(default_factory=list)
    timeline_events: List[Dict[str, Any]] = field(default_factory=list)
    status: ReconstructionStatus = ReconstructionStatus.PENDING
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Scene3DModel:
    model_id: str
    reconstruction_id: str
    case_id: str
    model_format: str
    model_url: str
    thumbnail_url: str
    vertices_count: int
    faces_count: int
    texture_maps: List[str] = field(default_factory=list)
    evidence_markers: List[Dict[str, Any]] = field(default_factory=list)
    camera_positions: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SceneReconstructionEngine:
    """Engine for reconstructing crime scenes from evidence and analysis."""

    def __init__(self):
        self._reconstructions: Dict[str, SceneReconstruction] = {}
        self._evidence_items: Dict[str, EvidenceItem] = {}

    def create_reconstruction(
        self,
        case_id: str,
        scene_type: str,
        location: Dict[str, Any],
        bounds: Dict[str, float],
        created_by: str = "",
        notes: str = "",
    ) -> SceneReconstruction:
        reconstruction_id = f"recon-{uuid.uuid4().hex[:12]}"
        reconstruction = SceneReconstruction(
            reconstruction_id=reconstruction_id,
            case_id=case_id,
            scene_type=scene_type,
            location=location,
            bounds=bounds,
            created_by=created_by,
            notes=notes,
        )
        self._reconstructions[reconstruction_id] = reconstruction
        return reconstruction

    def add_evidence_to_reconstruction(
        self,
        reconstruction_id: str,
        evidence_id: str,
    ) -> Optional[SceneReconstruction]:
        reconstruction = self._reconstructions.get(reconstruction_id)
        if not reconstruction:
            return None
        if evidence_id not in reconstruction.evidence_items:
            reconstruction.evidence_items.append(evidence_id)
            reconstruction.updated_at = datetime.utcnow()
        return reconstruction

    def analyze_scene(
        self,
        reconstruction_id: str,
    ) -> Optional[SceneReconstruction]:
        reconstruction = self._reconstructions.get(reconstruction_id)
        if not reconstruction:
            return None

        reconstruction.status = ReconstructionStatus.IN_PROGRESS
        reconstruction.updated_at = datetime.utcnow()

        evidence_count = len(reconstruction.evidence_items)
        trajectory_count = len(reconstruction.trajectories)
        spatter_count = len(reconstruction.spatter_analyses)

        base_confidence = 30.0
        evidence_bonus = min(evidence_count * 5, 30)
        trajectory_bonus = min(trajectory_count * 10, 20)
        spatter_bonus = min(spatter_count * 5, 20)

        reconstruction.confidence_score = min(
            100.0,
            base_confidence + evidence_bonus + trajectory_bonus + spatter_bonus
        )

        reconstruction.status = ReconstructionStatus.COMPLETED
        reconstruction.updated_at = datetime.utcnow()

        return reconstruction

    def generate_timeline(
        self,
        reconstruction_id: str,
    ) -> List[Dict[str, Any]]:
        reconstruction = self._reconstructions.get(reconstruction_id)
        if not reconstruction:
            return []

        timeline_events = []

        for i, evidence_id in enumerate(reconstruction.evidence_items):
            evidence = self._evidence_items.get(evidence_id)
            if evidence:
                timeline_events.append({
                    "event_id": f"evt-{uuid.uuid4().hex[:8]}",
                    "timestamp": evidence.collected_at.isoformat(),
                    "event_type": "evidence_placed",
                    "description": f"Evidence item: {evidence.description}",
                    "evidence_id": evidence_id,
                    "position": evidence.position,
                    "sequence_order": i,
                })

        reconstruction.timeline_events = timeline_events
        reconstruction.updated_at = datetime.utcnow()

        return timeline_events

    def get_reconstruction(self, reconstruction_id: str) -> Optional[SceneReconstruction]:
        return self._reconstructions.get(reconstruction_id)

    def get_reconstructions(
        self,
        case_id: Optional[str] = None,
        status: Optional[ReconstructionStatus] = None,
        limit: int = 100,
    ) -> List[SceneReconstruction]:
        results = list(self._reconstructions.values())

        if case_id:
            results = [r for r in results if r.case_id == case_id]
        if status:
            results = [r for r in results if r.status == status]

        return results[:limit]

    def get_metrics(self) -> Dict[str, Any]:
        reconstructions = list(self._reconstructions.values())
        return {
            "total_reconstructions": len(reconstructions),
            "by_status": {
                status.value: len([r for r in reconstructions if r.status == status])
                for status in ReconstructionStatus
            },
            "average_confidence": (
                sum(r.confidence_score for r in reconstructions) / len(reconstructions)
                if reconstructions else 0.0
            ),
        }


class SpatialEvidenceMapper:
    """Maps and analyzes spatial relationships between evidence items."""

    def __init__(self):
        self._evidence_items: Dict[str, EvidenceItem] = {}
        self._spatial_clusters: Dict[str, List[str]] = {}

    def register_evidence(
        self,
        case_id: str,
        evidence_type: EvidenceType,
        position: Dict[str, float],
        description: str,
        collected_by: str,
        analysis_results: Optional[Dict[str, Any]] = None,
        photos: Optional[List[str]] = None,
        notes: str = "",
    ) -> EvidenceItem:
        evidence_id = f"evd-{uuid.uuid4().hex[:12]}"
        evidence = EvidenceItem(
            evidence_id=evidence_id,
            case_id=case_id,
            evidence_type=evidence_type,
            position=position,
            description=description,
            collected_at=datetime.utcnow(),
            collected_by=collected_by,
            analysis_results=analysis_results or {},
            photos=photos or [],
            notes=notes,
        )
        self._evidence_items[evidence_id] = evidence
        return evidence

    def update_evidence(
        self,
        evidence_id: str,
        analysis_results: Optional[Dict[str, Any]] = None,
        linked_suspects: Optional[List[str]] = None,
        linked_victims: Optional[List[str]] = None,
        confidence_score: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Optional[EvidenceItem]:
        evidence = self._evidence_items.get(evidence_id)
        if not evidence:
            return None

        if analysis_results is not None:
            evidence.analysis_results.update(analysis_results)
        if linked_suspects is not None:
            evidence.linked_suspects = linked_suspects
        if linked_victims is not None:
            evidence.linked_victims = linked_victims
        if confidence_score is not None:
            evidence.confidence_score = confidence_score
        if notes is not None:
            evidence.notes = notes

        return evidence

    def add_chain_of_custody(
        self,
        evidence_id: str,
        handler: str,
        action: str,
        location: str,
        notes: str = "",
    ) -> Optional[EvidenceItem]:
        evidence = self._evidence_items.get(evidence_id)
        if not evidence:
            return None

        custody_entry = {
            "entry_id": f"coc-{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.utcnow().isoformat(),
            "handler": handler,
            "action": action,
            "location": location,
            "notes": notes,
        }
        evidence.chain_of_custody.append(custody_entry)
        return evidence

    def calculate_distance(
        self,
        pos1: Dict[str, float],
        pos2: Dict[str, float],
    ) -> float:
        dx = pos2.get("x", 0) - pos1.get("x", 0)
        dy = pos2.get("y", 0) - pos1.get("y", 0)
        dz = pos2.get("z", 0) - pos1.get("z", 0)
        return math.sqrt(dx**2 + dy**2 + dz**2)

    def find_nearby_evidence(
        self,
        position: Dict[str, float],
        radius: float,
        case_id: Optional[str] = None,
        evidence_type: Optional[EvidenceType] = None,
    ) -> List[EvidenceItem]:
        results = []
        for evidence in self._evidence_items.values():
            if case_id and evidence.case_id != case_id:
                continue
            if evidence_type and evidence.evidence_type != evidence_type:
                continue

            distance = self.calculate_distance(position, evidence.position)
            if distance <= radius:
                results.append(evidence)

        return results

    def cluster_evidence(
        self,
        case_id: str,
        cluster_radius: float = 2.0,
    ) -> Dict[str, List[str]]:
        case_evidence = [
            e for e in self._evidence_items.values()
            if e.case_id == case_id
        ]

        clusters: Dict[str, List[str]] = {}
        assigned = set()

        for evidence in case_evidence:
            if evidence.evidence_id in assigned:
                continue

            cluster_id = f"cluster-{uuid.uuid4().hex[:8]}"
            cluster_members = [evidence.evidence_id]
            assigned.add(evidence.evidence_id)

            for other in case_evidence:
                if other.evidence_id in assigned:
                    continue

                distance = self.calculate_distance(evidence.position, other.position)
                if distance <= cluster_radius:
                    cluster_members.append(other.evidence_id)
                    assigned.add(other.evidence_id)

            clusters[cluster_id] = cluster_members

        self._spatial_clusters[case_id] = list(clusters.keys())
        return clusters

    def analyze_entry_exit_points(
        self,
        case_id: str,
    ) -> Dict[str, List[EvidenceItem]]:
        case_evidence = [
            e for e in self._evidence_items.values()
            if e.case_id == case_id
        ]

        entry_points = [
            e for e in case_evidence
            if e.evidence_type == EvidenceType.ENTRY_POINT
        ]
        exit_points = [
            e for e in case_evidence
            if e.evidence_type == EvidenceType.EXIT_POINT
        ]

        return {
            "entry_points": entry_points,
            "exit_points": exit_points,
        }

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceItem]:
        return self._evidence_items.get(evidence_id)

    def get_case_evidence(
        self,
        case_id: str,
        evidence_type: Optional[EvidenceType] = None,
        limit: int = 100,
    ) -> List[EvidenceItem]:
        results = [
            e for e in self._evidence_items.values()
            if e.case_id == case_id
        ]

        if evidence_type:
            results = [e for e in results if e.evidence_type == evidence_type]

        return results[:limit]

    def get_spatial_heatmap(
        self,
        case_id: str,
        grid_size: float = 1.0,
    ) -> Dict[str, Any]:
        case_evidence = [
            e for e in self._evidence_items.values()
            if e.case_id == case_id
        ]

        if not case_evidence:
            return {"grid": [], "bounds": {}}

        min_x = min(e.position.get("x", 0) for e in case_evidence)
        max_x = max(e.position.get("x", 0) for e in case_evidence)
        min_y = min(e.position.get("y", 0) for e in case_evidence)
        max_y = max(e.position.get("y", 0) for e in case_evidence)

        grid = []
        y = min_y
        while y <= max_y:
            row = []
            x = min_x
            while x <= max_x:
                count = len(self.find_nearby_evidence(
                    {"x": x, "y": y, "z": 0},
                    grid_size / 2,
                    case_id=case_id,
                ))
                row.append(count)
                x += grid_size
            grid.append(row)
            y += grid_size

        return {
            "grid": grid,
            "bounds": {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y,
            },
            "grid_size": grid_size,
        }


class TrajectoryRebuilder:
    """Rebuilds movement trajectories from evidence and analysis."""

    def __init__(self, evidence_mapper: SpatialEvidenceMapper):
        self._evidence_mapper = evidence_mapper
        self._trajectories: Dict[str, MovementTrajectory] = {}
        self._spatter_analyses: Dict[str, BloodSpatterAnalysis] = {}

    def create_trajectory(
        self,
        case_id: str,
        subject_type: str,
        subject_id: Optional[str] = None,
        notes: str = "",
    ) -> MovementTrajectory:
        trajectory_id = f"traj-{uuid.uuid4().hex[:12]}"
        trajectory = MovementTrajectory(
            trajectory_id=trajectory_id,
            case_id=case_id,
            subject_type=subject_type,
            subject_id=subject_id,
            notes=notes,
        )
        self._trajectories[trajectory_id] = trajectory
        return trajectory

    def add_trajectory_point(
        self,
        trajectory_id: str,
        position: Dict[str, float],
        movement_type: MovementType,
        timestamp_estimate: Optional[datetime] = None,
        confidence: float = 0.5,
        evidence_support: Optional[List[str]] = None,
        notes: str = "",
    ) -> Optional[MovementTrajectory]:
        trajectory = self._trajectories.get(trajectory_id)
        if not trajectory:
            return None

        point = TrajectoryPoint(
            point_id=f"pt-{uuid.uuid4().hex[:8]}",
            position=position,
            timestamp_estimate=timestamp_estimate,
            movement_type=movement_type,
            confidence=confidence,
            evidence_support=evidence_support or [],
            notes=notes,
        )
        trajectory.points.append(point)

        if len(trajectory.points) > 1:
            total_distance = 0.0
            for i in range(1, len(trajectory.points)):
                p1 = trajectory.points[i - 1].position
                p2 = trajectory.points[i].position
                total_distance += self._evidence_mapper.calculate_distance(p1, p2)
            trajectory.total_distance = total_distance

        trajectory.confidence_score = (
            sum(p.confidence for p in trajectory.points) / len(trajectory.points)
            if trajectory.points else 0.0
        )

        return trajectory

    def analyze_blood_spatter(
        self,
        case_id: str,
        pattern_type: SpatterPattern,
        position: Dict[str, float],
        droplet_count: int,
        average_droplet_size: float,
        impact_angle: float = 0.0,
        directionality: float = 0.0,
        analysis_notes: str = "",
    ) -> BloodSpatterAnalysis:
        spatter_id = f"spatter-{uuid.uuid4().hex[:12]}"

        if impact_angle > 0:
            source_height = position.get("z", 0) + (
                average_droplet_size * 10 / math.tan(math.radians(impact_angle))
            )
        else:
            source_height = position.get("z", 0) + 1.5

        area_of_origin = {
            "x": position.get("x", 0) - math.cos(math.radians(directionality)) * 0.5,
            "y": position.get("y", 0) - math.sin(math.radians(directionality)) * 0.5,
            "z": source_height,
        }

        if average_droplet_size < 1.0:
            velocity_category = "high"
        elif average_droplet_size < 3.0:
            velocity_category = "medium"
        else:
            velocity_category = "low"

        confidence = 0.5
        if droplet_count > 50:
            confidence += 0.2
        if impact_angle > 0:
            confidence += 0.15
        if directionality > 0:
            confidence += 0.15

        analysis = BloodSpatterAnalysis(
            spatter_id=spatter_id,
            case_id=case_id,
            pattern_type=pattern_type,
            position=position,
            area_of_origin=area_of_origin,
            impact_angle=impact_angle,
            directionality=directionality,
            droplet_count=droplet_count,
            average_droplet_size=average_droplet_size,
            velocity_category=velocity_category,
            source_height_estimate=source_height,
            analysis_notes=analysis_notes,
            confidence_score=min(1.0, confidence),
        )
        self._spatter_analyses[spatter_id] = analysis
        return analysis

    def infer_movement_from_evidence(
        self,
        case_id: str,
        subject_type: str = "suspect",
    ) -> Optional[MovementTrajectory]:
        evidence_items = self._evidence_mapper.get_case_evidence(case_id)
        if not evidence_items:
            return None

        trajectory = self.create_trajectory(
            case_id=case_id,
            subject_type=subject_type,
            notes="Auto-generated from evidence analysis",
        )

        entry_exit = self._evidence_mapper.analyze_entry_exit_points(case_id)

        for entry in entry_exit["entry_points"]:
            self.add_trajectory_point(
                trajectory.trajectory_id,
                entry.position,
                MovementType.ENTRY,
                confidence=0.8,
                evidence_support=[entry.evidence_id],
            )

        footprints = [
            e for e in evidence_items
            if e.evidence_type == EvidenceType.FOOTPRINT
        ]
        for fp in footprints:
            self.add_trajectory_point(
                trajectory.trajectory_id,
                fp.position,
                MovementType.APPROACH,
                confidence=0.7,
                evidence_support=[fp.evidence_id],
            )

        for exit_pt in entry_exit["exit_points"]:
            self.add_trajectory_point(
                trajectory.trajectory_id,
                exit_pt.position,
                MovementType.EXIT,
                confidence=0.8,
                evidence_support=[exit_pt.evidence_id],
            )

        return trajectory

    def get_trajectory(self, trajectory_id: str) -> Optional[MovementTrajectory]:
        return self._trajectories.get(trajectory_id)

    def get_case_trajectories(
        self,
        case_id: str,
        subject_type: Optional[str] = None,
    ) -> List[MovementTrajectory]:
        results = [
            t for t in self._trajectories.values()
            if t.case_id == case_id
        ]
        if subject_type:
            results = [t for t in results if t.subject_type == subject_type]
        return results

    def get_spatter_analysis(self, spatter_id: str) -> Optional[BloodSpatterAnalysis]:
        return self._spatter_analyses.get(spatter_id)

    def get_case_spatter_analyses(self, case_id: str) -> List[BloodSpatterAnalysis]:
        return [
            s for s in self._spatter_analyses.values()
            if s.case_id == case_id
        ]


class CrimeScene3DModel:
    """Generates and manages 3D models of crime scenes (stub for future implementation)."""

    def __init__(self):
        self._models: Dict[str, Scene3DModel] = {}

    def generate_model(
        self,
        reconstruction_id: str,
        case_id: str,
        evidence_positions: List[Dict[str, Any]],
        scene_bounds: Dict[str, float],
        model_format: str = "gltf",
    ) -> Scene3DModel:
        model_id = f"model-{uuid.uuid4().hex[:12]}"

        vertices_count = 1000 + len(evidence_positions) * 100
        faces_count = vertices_count * 2

        model = Scene3DModel(
            model_id=model_id,
            reconstruction_id=reconstruction_id,
            case_id=case_id,
            model_format=model_format,
            model_url=f"/api/ada/models/{model_id}/download",
            thumbnail_url=f"/api/ada/models/{model_id}/thumbnail",
            vertices_count=vertices_count,
            faces_count=faces_count,
            evidence_markers=[
                {
                    "marker_id": f"marker-{i}",
                    "evidence_id": ep.get("evidence_id"),
                    "position": ep.get("position"),
                    "label": ep.get("label", f"Evidence {i+1}"),
                }
                for i, ep in enumerate(evidence_positions)
            ],
            camera_positions=[
                {"name": "overview", "position": {"x": 0, "y": 10, "z": 10}, "target": {"x": 0, "y": 0, "z": 0}},
                {"name": "top_down", "position": {"x": 0, "y": 20, "z": 0}, "target": {"x": 0, "y": 0, "z": 0}},
                {"name": "entry", "position": {"x": -10, "y": 2, "z": 0}, "target": {"x": 0, "y": 0, "z": 0}},
            ],
            metadata={
                "scene_bounds": scene_bounds,
                "generated_at": datetime.utcnow().isoformat(),
                "generator_version": "1.0.0",
            },
        )
        self._models[model_id] = model
        return model

    def add_evidence_marker(
        self,
        model_id: str,
        evidence_id: str,
        position: Dict[str, float],
        label: str,
        marker_type: str = "default",
    ) -> Optional[Scene3DModel]:
        model = self._models.get(model_id)
        if not model:
            return None

        marker = {
            "marker_id": f"marker-{uuid.uuid4().hex[:8]}",
            "evidence_id": evidence_id,
            "position": position,
            "label": label,
            "marker_type": marker_type,
        }
        model.evidence_markers.append(marker)
        return model

    def add_camera_position(
        self,
        model_id: str,
        name: str,
        position: Dict[str, float],
        target: Dict[str, float],
    ) -> Optional[Scene3DModel]:
        model = self._models.get(model_id)
        if not model:
            return None

        camera = {
            "name": name,
            "position": position,
            "target": target,
        }
        model.camera_positions.append(camera)
        return model

    def get_model(self, model_id: str) -> Optional[Scene3DModel]:
        return self._models.get(model_id)

    def get_reconstruction_model(self, reconstruction_id: str) -> Optional[Scene3DModel]:
        for model in self._models.values():
            if model.reconstruction_id == reconstruction_id:
                return model
        return None

    def export_model(
        self,
        model_id: str,
        export_format: str = "gltf",
    ) -> Optional[Dict[str, Any]]:
        model = self._models.get(model_id)
        if not model:
            return None

        return {
            "model_id": model.model_id,
            "format": export_format,
            "download_url": f"/api/ada/models/{model_id}/export/{export_format}",
            "file_size_estimate": model.vertices_count * 50,
            "includes_textures": len(model.texture_maps) > 0,
        }


__all__ = [
    "EvidenceType",
    "SpatterPattern",
    "MovementType",
    "ReconstructionStatus",
    "EvidenceItem",
    "BloodSpatterAnalysis",
    "TrajectoryPoint",
    "MovementTrajectory",
    "SceneReconstruction",
    "Scene3DModel",
    "SceneReconstructionEngine",
    "SpatialEvidenceMapper",
    "TrajectoryRebuilder",
    "CrimeScene3DModel",
]
