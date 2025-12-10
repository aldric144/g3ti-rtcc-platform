"""
Phase 21: Damage Assessment Tests

Tests for drone image classification, structural risk scoring,
cost estimation, and recovery timeline planning.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.emergency.damage_assessment import (
    DroneImageDamageClassifier,
    StructuralRiskScorer,
    CostEstimationModel,
    RecoveryTimelineEngine,
    DamageAssessmentManager,
    DamageLevel,
    StructureType,
    DamageType,
    RecoveryPhase,
)


class TestDroneImageDamageClassifier:
    """Tests for DroneImageDamageClassifier class."""

    def test_classifier_initialization(self):
        """Test DroneImageDamageClassifier initializes correctly."""
        classifier = DroneImageDamageClassifier()
        assert classifier is not None
        assert hasattr(classifier, '_images')

    def test_process_image(self):
        """Test processing a drone image."""
        classifier = DroneImageDamageClassifier()
        result = classifier.process_image(
            image_id="img-001",
            image_data=b"fake_image_data",
            location={"lat": 25.7617, "lng": -80.1918},
            capture_time=datetime.utcnow(),
        )
        
        assert result is not None
        assert result.processed is True
        assert hasattr(result, 'damage_detected')
        assert hasattr(result, 'damage_classifications')

    def test_classify_damage(self):
        """Test damage classification."""
        classifier = DroneImageDamageClassifier()
        result = classifier.process_image(
            image_id="img-002",
            image_data=b"fake_image_data",
            location={"lat": 25.7617, "lng": -80.1918},
        )
        
        classifications = result.damage_classifications
        assert isinstance(classifications, list)
        for cls in classifications:
            assert "damage_type" in cls
            assert "damage_level" in cls
            assert "confidence" in cls

    def test_get_processed_images(self):
        """Test getting processed images."""
        classifier = DroneImageDamageClassifier()
        classifier.process_image(
            image_id="img-003",
            image_data=b"fake_image_data",
            location={"lat": 25.7617, "lng": -80.1918},
        )
        
        images = classifier.get_processed_images()
        assert len(images) >= 1

    def test_get_images_with_damage(self):
        """Test getting images with damage detected."""
        classifier = DroneImageDamageClassifier()
        images = classifier.get_images_with_damage()
        assert isinstance(images, list)


class TestStructuralRiskScorer:
    """Tests for StructuralRiskScorer class."""

    def test_scorer_initialization(self):
        """Test StructuralRiskScorer initializes correctly."""
        scorer = StructuralRiskScorer()
        assert scorer is not None
        assert hasattr(scorer, '_assessments')

    def test_assess_structure(self):
        """Test assessing a structure."""
        scorer = StructuralRiskScorer()
        assessment = scorer.assess_structure(
            structure_id="struct-001",
            structure_type=StructureType.RESIDENTIAL,
            damage_level=DamageLevel.MAJOR,
            damage_types=[DamageType.STRUCTURAL, DamageType.ROOF],
            location={"lat": 25.7617, "lng": -80.1918},
        )
        
        assert assessment is not None
        assert hasattr(assessment, 'risk_score')
        assert 0 <= assessment.risk_score <= 1

    def test_calculate_risk_score(self):
        """Test risk score calculation."""
        scorer = StructuralRiskScorer()
        assessment = scorer.assess_structure(
            structure_id="struct-002",
            structure_type=StructureType.COMMERCIAL,
            damage_level=DamageLevel.DESTROYED,
            damage_types=[DamageType.STRUCTURAL, DamageType.FOUNDATION],
            location={"lat": 25.7617, "lng": -80.1918},
        )
        
        assert assessment.risk_score > 0.7

    def test_get_high_risk_structures(self):
        """Test getting high risk structures."""
        scorer = StructuralRiskScorer()
        scorer.assess_structure(
            structure_id="struct-003",
            structure_type=StructureType.RESIDENTIAL,
            damage_level=DamageLevel.DESTROYED,
            damage_types=[DamageType.STRUCTURAL],
            location={"lat": 25.7617, "lng": -80.1918},
        )
        
        high_risk = scorer.get_high_risk_structures(threshold=0.7)
        assert isinstance(high_risk, list)

    def test_evacuation_recommendation(self):
        """Test evacuation recommendation."""
        scorer = StructuralRiskScorer()
        assessment = scorer.assess_structure(
            structure_id="struct-004",
            structure_type=StructureType.RESIDENTIAL,
            damage_level=DamageLevel.MAJOR,
            damage_types=[DamageType.STRUCTURAL, DamageType.FOUNDATION],
            location={"lat": 25.7617, "lng": -80.1918},
        )
        
        assert hasattr(assessment, 'evacuation_required')
        assert hasattr(assessment, 'demolition_recommended')


class TestCostEstimationModel:
    """Tests for CostEstimationModel class."""

    def test_model_initialization(self):
        """Test CostEstimationModel initializes correctly."""
        model = CostEstimationModel()
        assert model is not None

    def test_estimate_cost(self):
        """Test cost estimation."""
        model = CostEstimationModel()
        estimate = model.estimate_cost(
            structure_type=StructureType.RESIDENTIAL,
            damage_level=DamageLevel.MODERATE,
            affected_area_sqft=2000,
            damage_types=[DamageType.ROOF, DamageType.WINDOWS],
        )
        
        assert estimate is not None
        assert hasattr(estimate, 'total_cost')
        assert hasattr(estimate, 'labor_cost')
        assert hasattr(estimate, 'materials_cost')
        assert estimate.total_cost > 0

    def test_estimate_destroyed_structure(self):
        """Test cost estimation for destroyed structure."""
        model = CostEstimationModel()
        estimate = model.estimate_cost(
            structure_type=StructureType.COMMERCIAL,
            damage_level=DamageLevel.DESTROYED,
            affected_area_sqft=10000,
            damage_types=[DamageType.STRUCTURAL, DamageType.FOUNDATION],
        )
        
        assert estimate.total_cost > 100000

    def test_get_cost_breakdown(self):
        """Test getting cost breakdown."""
        model = CostEstimationModel()
        estimate = model.estimate_cost(
            structure_type=StructureType.RESIDENTIAL,
            damage_level=DamageLevel.MINOR,
            affected_area_sqft=1500,
            damage_types=[DamageType.WINDOWS],
        )
        
        breakdown = model.get_cost_breakdown(estimate.estimate_id)
        assert breakdown is not None


class TestRecoveryTimelineEngine:
    """Tests for RecoveryTimelineEngine class."""

    def test_engine_initialization(self):
        """Test RecoveryTimelineEngine initializes correctly."""
        engine = RecoveryTimelineEngine()
        assert engine is not None
        assert hasattr(engine, '_timelines')

    def test_create_timeline(self):
        """Test creating recovery timeline."""
        engine = RecoveryTimelineEngine()
        timeline = engine.create_timeline(
            area_name="Downtown District",
            total_structures_affected=100,
            damage_distribution={
                "destroyed": 10,
                "major": 20,
                "moderate": 30,
                "minor": 40,
            },
        )
        
        assert timeline is not None
        assert timeline.area_name == "Downtown District"
        assert timeline.total_structures_affected == 100
        assert hasattr(timeline, 'estimated_completion')

    def test_update_progress(self):
        """Test updating recovery progress."""
        engine = RecoveryTimelineEngine()
        timeline = engine.create_timeline(
            area_name="Coastal Zone",
            total_structures_affected=50,
            damage_distribution={
                "destroyed": 5,
                "major": 15,
                "moderate": 20,
                "minor": 10,
            },
        )
        
        updated = engine.update_progress(
            timeline.timeline_id,
            structures_repaired=10,
            structures_demolished=3,
        )
        
        assert updated is not None
        assert updated.structures_repaired == 10
        assert updated.structures_demolished == 3

    def test_advance_phase(self):
        """Test advancing recovery phase."""
        engine = RecoveryTimelineEngine()
        timeline = engine.create_timeline(
            area_name="Industrial Area",
            total_structures_affected=30,
            damage_distribution={
                "major": 10,
                "moderate": 20,
            },
        )
        
        advanced = engine.advance_phase(timeline.timeline_id, RecoveryPhase.SHORT_TERM)
        assert advanced is not None
        assert advanced.current_phase == RecoveryPhase.SHORT_TERM

    def test_get_active_timelines(self):
        """Test getting active timelines."""
        engine = RecoveryTimelineEngine()
        engine.create_timeline(
            area_name="Test Area",
            total_structures_affected=20,
            damage_distribution={"minor": 20},
        )
        
        active = engine.get_active_timelines()
        assert len(active) >= 1


class TestDamageAssessmentManager:
    """Tests for DamageAssessmentManager class."""

    def test_manager_initialization(self):
        """Test DamageAssessmentManager initializes correctly."""
        manager = DamageAssessmentManager()
        assert manager is not None
        assert hasattr(manager, 'drone_classifier')
        assert hasattr(manager, 'risk_scorer')
        assert hasattr(manager, 'cost_model')
        assert hasattr(manager, 'recovery_engine')

    def test_create_assessment(self):
        """Test creating damage assessment."""
        manager = DamageAssessmentManager()
        assessment = manager.create_assessment(
            structure_type=StructureType.RESIDENTIAL,
            damage_level=DamageLevel.MODERATE,
            address={"street": "123 Main St", "city": "Miami", "state": "FL"},
            damage_description="Roof damage and broken windows",
            affected_area_sqft=1800,
            assessed_by="Inspector Smith",
        )
        
        assert assessment is not None
        assert assessment.damage_level == DamageLevel.MODERATE
        assert hasattr(assessment, 'habitability')

    def test_get_assessments(self):
        """Test getting all assessments."""
        manager = DamageAssessmentManager()
        manager.create_assessment(
            structure_type=StructureType.COMMERCIAL,
            damage_level=DamageLevel.MINOR,
            address={"street": "456 Oak Ave", "city": "Miami", "state": "FL"},
            damage_description="Minor facade damage",
            affected_area_sqft=5000,
            assessed_by="Inspector Jones",
        )
        
        assessments = manager.get_assessments()
        assert len(assessments) >= 1

    def test_get_area_summary(self):
        """Test getting area damage summary."""
        manager = DamageAssessmentManager()
        summary = manager.get_area_summary("area-001")
        
        assert summary is not None
        assert hasattr(summary, 'total_structures')
        assert hasattr(summary, 'damage_by_level')
        assert hasattr(summary, 'total_estimated_cost')

    def test_get_damage_metrics(self):
        """Test getting damage metrics."""
        manager = DamageAssessmentManager()
        metrics = manager.get_metrics()
        
        assert metrics is not None
        assert "assessments" in metrics
        assert "drone_images" in metrics
        assert "risk_assessments" in metrics
        assert "recovery" in metrics
