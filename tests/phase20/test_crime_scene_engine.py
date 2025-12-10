"""
Phase 20: Crime Scene Engine Tests

Tests for SceneReconstructionEngine, SpatialEvidenceMapper,
TrajectoryRebuilder, and CrimeScene3DModel.
"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.ada.crime_scene_engine import (
    SceneReconstructionEngine,
    SpatialEvidenceMapper,
    TrajectoryRebuilder,
    CrimeScene3DModel,
    EvidenceType,
    SpatterPattern,
    ReconstructionStatus,
    MovementType,
)


class TestSceneReconstructionEngine:
    def setup_method(self):
        self.engine = SceneReconstructionEngine()

    def test_create_reconstruction(self):
        reconstruction = self.engine.create_reconstruction(
            case_id="case-001",
            scene_type="indoor",
            location={"address": "123 Main St", "lat": 33.749, "lng": -84.388},
            bounds={"min_x": 0, "max_x": 100, "min_y": 0, "max_y": 100},
        )
        assert reconstruction is not None
        assert reconstruction.case_id == "case-001"
        assert reconstruction.scene_type == "indoor"
        assert reconstruction.status == ReconstructionStatus.PENDING

    def test_get_reconstruction(self):
        reconstruction = self.engine.create_reconstruction(
            case_id="case-002",
            scene_type="outdoor",
            location={},
            bounds={},
        )
        retrieved = self.engine.get_reconstruction(reconstruction.reconstruction_id)
        assert retrieved is not None
        assert retrieved.reconstruction_id == reconstruction.reconstruction_id

    def test_analyze_scene(self):
        reconstruction = self.engine.create_reconstruction(
            case_id="case-003",
            scene_type="indoor",
            location={},
            bounds={},
        )
        analyzed = self.engine.analyze_scene(reconstruction.reconstruction_id)
        assert analyzed is not None
        assert analyzed.status == ReconstructionStatus.ANALYZED

    def test_generate_timeline(self):
        reconstruction = self.engine.create_reconstruction(
            case_id="case-004",
            scene_type="indoor",
            location={},
            bounds={},
        )
        self.engine.analyze_scene(reconstruction.reconstruction_id)
        timeline = self.engine.generate_timeline(reconstruction.reconstruction_id)
        assert isinstance(timeline, list)

    def test_get_reconstructions_by_case(self):
        self.engine.create_reconstruction(
            case_id="case-005",
            scene_type="indoor",
            location={},
            bounds={},
        )
        reconstructions = self.engine.get_reconstructions(case_id="case-005")
        assert len(reconstructions) >= 1

    def test_get_metrics(self):
        metrics = self.engine.get_metrics()
        assert "total_reconstructions" in metrics
        assert "by_status" in metrics


class TestSpatialEvidenceMapper:
    def setup_method(self):
        self.mapper = SpatialEvidenceMapper()

    def test_register_evidence(self):
        evidence = self.mapper.register_evidence(
            case_id="case-001",
            evidence_type="blood_spatter",
            position={"x": 10, "y": 20, "z": 0},
            description="Blood spatter on wall",
            collected_by="Officer Smith",
        )
        assert evidence is not None
        assert evidence.case_id == "case-001"
        assert evidence.evidence_type == EvidenceType.BLOOD_SPATTER

    def test_get_evidence(self):
        evidence = self.mapper.register_evidence(
            case_id="case-002",
            evidence_type="fingerprint",
            position={"x": 5, "y": 10, "z": 1},
            description="Latent fingerprint",
            collected_by="CSI Tech",
        )
        retrieved = self.mapper.get_evidence(evidence.evidence_id)
        assert retrieved is not None
        assert retrieved.evidence_id == evidence.evidence_id

    def test_get_case_evidence(self):
        self.mapper.register_evidence(
            case_id="case-003",
            evidence_type="weapon",
            position={"x": 30, "y": 40, "z": 0},
            description="Knife",
            collected_by="Detective Jones",
        )
        evidence_list = self.mapper.get_case_evidence("case-003")
        assert len(evidence_list) >= 1

    def test_cluster_evidence(self):
        for i in range(5):
            self.mapper.register_evidence(
                case_id="case-004",
                evidence_type="fiber",
                position={"x": i * 10, "y": i * 10, "z": 0},
                description=f"Fiber sample {i}",
                collected_by="CSI",
            )
        clusters = self.mapper.cluster_evidence("case-004", num_clusters=2)
        assert isinstance(clusters, list)

    def test_analyze_entry_exit_points(self):
        self.mapper.register_evidence(
            case_id="case-005",
            evidence_type="footprint",
            position={"x": 0, "y": 50, "z": 0},
            description="Entry footprint",
            collected_by="CSI",
        )
        analysis = self.mapper.analyze_entry_exit_points("case-005")
        assert "entry_points" in analysis
        assert "exit_points" in analysis

    def test_get_spatial_heatmap(self):
        for i in range(3):
            self.mapper.register_evidence(
                case_id="case-006",
                evidence_type="dna",
                position={"x": i * 20, "y": i * 20, "z": 0},
                description=f"DNA sample {i}",
                collected_by="Lab Tech",
            )
        heatmap = self.mapper.get_spatial_heatmap("case-006", resolution=5)
        assert isinstance(heatmap, list)


class TestTrajectoryRebuilder:
    def setup_method(self):
        self.mapper = SpatialEvidenceMapper()
        self.rebuilder = TrajectoryRebuilder(self.mapper)

    def test_create_trajectory(self):
        trajectory = self.rebuilder.create_trajectory(
            case_id="case-001",
            subject_type="suspect",
            subject_id="suspect-001",
        )
        assert trajectory is not None
        assert trajectory.case_id == "case-001"
        assert trajectory.subject_type == "suspect"

    def test_add_point(self):
        trajectory = self.rebuilder.create_trajectory(
            case_id="case-002",
            subject_type="victim",
        )
        point = self.rebuilder.add_point(
            trajectory_id=trajectory.trajectory_id,
            position={"x": 10, "y": 20, "z": 0},
            movement_type="walking",
            timestamp=datetime.utcnow(),
        )
        assert point is not None
        assert point.movement_type == MovementType.WALKING

    def test_get_trajectory(self):
        trajectory = self.rebuilder.create_trajectory(
            case_id="case-003",
            subject_type="suspect",
        )
        retrieved = self.rebuilder.get_trajectory(trajectory.trajectory_id)
        assert retrieved is not None
        assert retrieved.trajectory_id == trajectory.trajectory_id

    def test_infer_movement_from_evidence(self):
        self.mapper.register_evidence(
            case_id="case-004",
            evidence_type="footprint",
            position={"x": 10, "y": 10, "z": 0},
            description="Footprint 1",
            collected_by="CSI",
        )
        self.mapper.register_evidence(
            case_id="case-004",
            evidence_type="footprint",
            position={"x": 30, "y": 30, "z": 0},
            description="Footprint 2",
            collected_by="CSI",
        )
        trajectory = self.rebuilder.infer_movement_from_evidence("case-004")
        assert trajectory is not None

    def test_analyze_blood_spatter(self):
        analysis = self.rebuilder.analyze_blood_spatter(
            case_id="case-005",
            spatter_id="spatter-001",
            pattern_type=SpatterPattern.IMPACT,
            position={"x": 50, "y": 50, "z": 0},
            area_cm2=100,
            droplet_count=50,
        )
        assert analysis is not None
        assert analysis.pattern_type == SpatterPattern.IMPACT


class TestCrimeScene3DModel:
    def setup_method(self):
        self.model_generator = CrimeScene3DModel()

    def test_generate_model(self):
        model = self.model_generator.generate_model("recon-001")
        assert model is not None
        assert model.reconstruction_id == "recon-001"

    def test_get_model(self):
        model = self.model_generator.generate_model("recon-002")
        retrieved = self.model_generator.get_model(model.model_id)
        assert retrieved is not None
        assert retrieved.model_id == model.model_id

    def test_add_evidence_marker(self):
        model = self.model_generator.generate_model("recon-003")
        marker = self.model_generator.add_evidence_marker(
            model_id=model.model_id,
            evidence_id="ev-001",
            position={"x": 10, "y": 20, "z": 0},
            marker_type="blood",
        )
        assert marker is not None

    def test_add_camera_position(self):
        model = self.model_generator.generate_model("recon-004")
        camera = self.model_generator.add_camera_position(
            model_id=model.model_id,
            name="Overview",
            position={"x": 50, "y": 50, "z": 100},
            target={"x": 50, "y": 50, "z": 0},
        )
        assert camera is not None
