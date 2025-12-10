"""
Phase 21: Damage Assessment Module

Drone image damage classification, structural risk scoring,
cost estimation, and recovery timeline planning.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import math


class DamageLevel(Enum):
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    DESTROYED = "destroyed"


class StructureType(Enum):
    RESIDENTIAL_SINGLE = "residential_single"
    RESIDENTIAL_MULTI = "residential_multi"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    INFRASTRUCTURE = "infrastructure"
    GOVERNMENT = "government"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RELIGIOUS = "religious"
    UTILITY = "utility"


class DamageType(Enum):
    WIND = "wind"
    FLOOD = "flood"
    FIRE = "fire"
    EARTHQUAKE = "earthquake"
    EXPLOSION = "explosion"
    DEBRIS = "debris"
    STRUCTURAL = "structural"
    ROOF = "roof"
    FOUNDATION = "foundation"


class AssessmentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    DISPUTED = "disputed"


class RecoveryPhase(Enum):
    EMERGENCY = "emergency"
    SHORT_TERM = "short_term"
    INTERMEDIATE = "intermediate"
    LONG_TERM = "long_term"
    COMPLETED = "completed"


@dataclass
class DroneImage:
    image_id: str
    location: Dict[str, float]
    captured_at: datetime
    altitude_ft: float
    resolution: str
    file_path: str
    processed: bool
    damage_detected: bool
    damage_classifications: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    notes: str


@dataclass
class DamageAssessment:
    assessment_id: str
    structure_id: str
    address: Dict[str, Any]
    structure_type: StructureType
    damage_level: DamageLevel
    damage_types: List[DamageType]
    damage_description: str
    affected_area_sqft: float
    habitability: bool
    utilities_status: Dict[str, str]
    estimated_cost: float
    insurance_claim_filed: bool
    assessment_status: AssessmentStatus
    assessed_by: str
    drone_images: List[str]
    photos: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None


@dataclass
class StructuralRisk:
    risk_id: str
    structure_id: str
    address: Dict[str, Any]
    risk_score: float
    risk_factors: List[Dict[str, Any]]
    immediate_hazards: List[str]
    recommended_actions: List[str]
    evacuation_required: bool
    demolition_recommended: bool
    engineer_inspection_required: bool
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CostEstimate:
    estimate_id: str
    assessment_id: str
    structure_type: StructureType
    damage_level: DamageLevel
    repair_cost: float
    replacement_cost: float
    contents_loss: float
    business_interruption: float
    total_estimate: float
    confidence_level: str
    methodology: str
    assumptions: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RecoveryTimeline:
    timeline_id: str
    area_id: str
    area_name: str
    current_phase: RecoveryPhase
    phases: List[Dict[str, Any]]
    total_structures_affected: int
    structures_repaired: int
    structures_demolished: int
    estimated_completion: datetime
    milestones: List[Dict[str, Any]]
    blockers: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AreaDamageSummary:
    area_id: str
    area_name: str
    total_structures: int
    by_damage_level: Dict[str, int]
    by_structure_type: Dict[str, int]
    total_estimated_cost: float
    population_displaced: int
    businesses_affected: int
    critical_infrastructure_damaged: int
    created_at: datetime = field(default_factory=datetime.utcnow)


class DroneImageDamageClassifier:
    """
    Classifies damage from drone imagery (stub implementation).
    Uses computer vision models to detect and classify damage.
    """

    def __init__(self):
        self._images: Dict[str, DroneImage] = {}
        self._classifications: Dict[str, List[Dict[str, Any]]] = {}

    def upload_image(
        self,
        location: Dict[str, float],
        altitude_ft: float,
        file_path: str,
        resolution: str = "4K",
    ) -> DroneImage:
        """Upload a drone image for processing."""
        image_id = f"img-{uuid.uuid4().hex[:8]}"

        image = DroneImage(
            image_id=image_id,
            location=location,
            captured_at=datetime.utcnow(),
            altitude_ft=altitude_ft,
            resolution=resolution,
            file_path=file_path,
            processed=False,
            damage_detected=False,
            damage_classifications=[],
            confidence_scores={},
            notes="",
        )

        self._images[image_id] = image
        return image

    def process_image(self, image_id: str) -> DroneImage:
        """Process image and classify damage (stub)."""
        image = self._images.get(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        classifications = self._run_damage_detection(image)
        confidence_scores = self._calculate_confidence(classifications)

        image.processed = True
        image.damage_detected = len(classifications) > 0
        image.damage_classifications = classifications
        image.confidence_scores = confidence_scores

        return image

    def _run_damage_detection(self, image: DroneImage) -> List[Dict[str, Any]]:
        """Run damage detection model (stub)."""
        return [
            {
                "damage_type": "roof",
                "damage_level": "moderate",
                "bounding_box": {"x": 100, "y": 100, "width": 200, "height": 150},
                "confidence": 0.85,
            },
            {
                "damage_type": "structural",
                "damage_level": "minor",
                "bounding_box": {"x": 300, "y": 200, "width": 100, "height": 100},
                "confidence": 0.72,
            },
        ]

    def _calculate_confidence(self, classifications: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall confidence scores."""
        if not classifications:
            return {"overall": 0.0, "damage_detected": 0.0}

        avg_confidence = sum(c.get("confidence", 0) for c in classifications) / len(classifications)
        return {
            "overall": avg_confidence,
            "damage_detected": 0.95 if classifications else 0.1,
            "classification_accuracy": avg_confidence,
        }

    def batch_process(self, image_ids: List[str]) -> List[DroneImage]:
        """Process multiple images in batch."""
        results = []
        for image_id in image_ids:
            try:
                result = self.process_image(image_id)
                results.append(result)
            except ValueError:
                continue
        return results

    def get_image(self, image_id: str) -> Optional[DroneImage]:
        """Get image by ID."""
        return self._images.get(image_id)

    def get_images(self, processed_only: bool = False) -> List[DroneImage]:
        """Get all images, optionally filtered to processed only."""
        images = list(self._images.values())
        if processed_only:
            images = [i for i in images if i.processed]
        return images

    def get_damage_summary(self) -> Dict[str, Any]:
        """Get damage detection summary."""
        images = list(self._images.values())
        processed = [i for i in images if i.processed]
        with_damage = [i for i in processed if i.damage_detected]

        return {
            "total_images": len(images),
            "processed": len(processed),
            "damage_detected": len(with_damage),
            "pending_processing": len(images) - len(processed),
        }


class StructuralRiskScorer:
    """
    Scores structural risk based on damage assessments.
    """

    def __init__(self):
        self._risks: Dict[str, StructuralRisk] = {}

    def assess_risk(
        self,
        structure_id: str,
        address: Dict[str, Any],
        damage_assessment: DamageAssessment,
        building_age_years: int,
        construction_type: str,
        foundation_type: str,
    ) -> StructuralRisk:
        """Assess structural risk for a building."""
        risk_id = f"risk-{uuid.uuid4().hex[:8]}"

        risk_factors = self._identify_risk_factors(
            damage_assessment,
            building_age_years,
            construction_type,
            foundation_type,
        )

        risk_score = self._calculate_risk_score(risk_factors)
        hazards = self._identify_immediate_hazards(damage_assessment, risk_factors)
        actions = self._recommend_actions(risk_score, hazards)

        risk = StructuralRisk(
            risk_id=risk_id,
            structure_id=structure_id,
            address=address,
            risk_score=risk_score,
            risk_factors=risk_factors,
            immediate_hazards=hazards,
            recommended_actions=actions,
            evacuation_required=risk_score >= 0.7,
            demolition_recommended=risk_score >= 0.9,
            engineer_inspection_required=risk_score >= 0.5,
        )

        self._risks[risk_id] = risk
        return risk

    def _identify_risk_factors(
        self,
        assessment: DamageAssessment,
        age: int,
        construction: str,
        foundation: str,
    ) -> List[Dict[str, Any]]:
        """Identify structural risk factors."""
        factors = []

        damage_weights = {
            DamageLevel.NONE: 0,
            DamageLevel.MINOR: 0.2,
            DamageLevel.MODERATE: 0.5,
            DamageLevel.MAJOR: 0.8,
            DamageLevel.DESTROYED: 1.0,
        }

        factors.append({
            "factor": "damage_level",
            "value": assessment.damage_level.value,
            "weight": damage_weights.get(assessment.damage_level, 0.5),
        })

        if age > 50:
            factors.append({
                "factor": "building_age",
                "value": f"{age} years",
                "weight": min(0.3, age / 200),
            })

        if DamageType.FOUNDATION in assessment.damage_types:
            factors.append({
                "factor": "foundation_damage",
                "value": "detected",
                "weight": 0.4,
            })

        if DamageType.STRUCTURAL in assessment.damage_types:
            factors.append({
                "factor": "structural_damage",
                "value": "detected",
                "weight": 0.35,
            })

        if not assessment.habitability:
            factors.append({
                "factor": "uninhabitable",
                "value": "true",
                "weight": 0.25,
            })

        return factors

    def _calculate_risk_score(self, factors: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score (0-1)."""
        if not factors:
            return 0.0

        total_weight = sum(f.get("weight", 0) for f in factors)
        return min(1.0, total_weight)

    def _identify_immediate_hazards(
        self,
        assessment: DamageAssessment,
        factors: List[Dict[str, Any]],
    ) -> List[str]:
        """Identify immediate hazards."""
        hazards = []

        if assessment.damage_level in [DamageLevel.MAJOR, DamageLevel.DESTROYED]:
            hazards.append("Structural collapse risk")

        if DamageType.ROOF in assessment.damage_types:
            hazards.append("Roof instability")

        if assessment.utilities_status.get("gas") == "leak":
            hazards.append("Gas leak detected")

        if assessment.utilities_status.get("electrical") == "damaged":
            hazards.append("Electrical hazard")

        if DamageType.FIRE in assessment.damage_types:
            hazards.append("Fire damage - structural integrity compromised")

        return hazards

    def _recommend_actions(self, risk_score: float, hazards: List[str]) -> List[str]:
        """Recommend actions based on risk assessment."""
        actions = []

        if risk_score >= 0.9:
            actions.append("Immediate evacuation required")
            actions.append("Schedule demolition assessment")
            actions.append("Establish safety perimeter")
        elif risk_score >= 0.7:
            actions.append("Evacuate building immediately")
            actions.append("Request structural engineer inspection")
            actions.append("Do not enter until cleared")
        elif risk_score >= 0.5:
            actions.append("Limit occupancy")
            actions.append("Schedule professional inspection")
            actions.append("Monitor for changes")
        else:
            actions.append("Safe for occupancy with caution")
            actions.append("Document damage for insurance")

        if "Gas leak detected" in hazards:
            actions.insert(0, "Contact gas company immediately")

        return actions

    def get_risk(self, risk_id: str) -> Optional[StructuralRisk]:
        """Get risk assessment by ID."""
        return self._risks.get(risk_id)

    def get_high_risk_structures(self, threshold: float = 0.7) -> List[StructuralRisk]:
        """Get structures above risk threshold."""
        return [r for r in self._risks.values() if r.risk_score >= threshold]

    def get_metrics(self) -> Dict[str, Any]:
        """Get risk assessment metrics."""
        risks = list(self._risks.values())
        return {
            "total_assessed": len(risks),
            "high_risk": len([r for r in risks if r.risk_score >= 0.7]),
            "evacuation_required": len([r for r in risks if r.evacuation_required]),
            "demolition_recommended": len([r for r in risks if r.demolition_recommended]),
            "average_risk_score": sum(r.risk_score for r in risks) / len(risks) if risks else 0,
        }


class CostEstimationModel:
    """
    Estimates damage costs for structures.
    """

    def __init__(self):
        self._estimates: Dict[str, CostEstimate] = {}

        self._cost_per_sqft = {
            StructureType.RESIDENTIAL_SINGLE: 150,
            StructureType.RESIDENTIAL_MULTI: 175,
            StructureType.COMMERCIAL: 200,
            StructureType.INDUSTRIAL: 125,
            StructureType.INFRASTRUCTURE: 300,
            StructureType.GOVERNMENT: 250,
            StructureType.HEALTHCARE: 400,
            StructureType.EDUCATION: 225,
            StructureType.RELIGIOUS: 200,
            StructureType.UTILITY: 350,
        }

        self._damage_multipliers = {
            DamageLevel.NONE: 0,
            DamageLevel.MINOR: 0.1,
            DamageLevel.MODERATE: 0.35,
            DamageLevel.MAJOR: 0.7,
            DamageLevel.DESTROYED: 1.0,
        }

    def estimate_cost(
        self,
        assessment: DamageAssessment,
        structure_sqft: float,
        contents_value: float = 0,
        business_revenue_daily: float = 0,
        estimated_downtime_days: int = 0,
    ) -> CostEstimate:
        """Estimate damage costs."""
        estimate_id = f"est-{uuid.uuid4().hex[:8]}"

        base_cost = self._cost_per_sqft.get(assessment.structure_type, 150)
        damage_mult = self._damage_multipliers.get(assessment.damage_level, 0.5)

        replacement_cost = base_cost * structure_sqft
        repair_cost = replacement_cost * damage_mult

        contents_loss = contents_value * damage_mult * 0.8

        business_interruption = 0
        if business_revenue_daily > 0 and estimated_downtime_days > 0:
            business_interruption = business_revenue_daily * estimated_downtime_days

        total = repair_cost + contents_loss + business_interruption

        confidence = "high" if assessment.assessment_status == AssessmentStatus.VERIFIED else "medium"

        estimate = CostEstimate(
            estimate_id=estimate_id,
            assessment_id=assessment.assessment_id,
            structure_type=assessment.structure_type,
            damage_level=assessment.damage_level,
            repair_cost=repair_cost,
            replacement_cost=replacement_cost,
            contents_loss=contents_loss,
            business_interruption=business_interruption,
            total_estimate=total,
            confidence_level=confidence,
            methodology="Standard cost estimation using regional construction costs and damage multipliers",
            assumptions=[
                f"Base construction cost: ${base_cost}/sqft",
                f"Damage multiplier: {damage_mult * 100}%",
                "Contents depreciation: 20%",
            ],
        )

        self._estimates[estimate_id] = estimate
        return estimate

    def get_estimate(self, estimate_id: str) -> Optional[CostEstimate]:
        """Get cost estimate by ID."""
        return self._estimates.get(estimate_id)

    def get_area_total(self, assessment_ids: List[str]) -> Dict[str, float]:
        """Get total costs for an area."""
        estimates = [e for e in self._estimates.values() if e.assessment_id in assessment_ids]

        return {
            "total_repair_cost": sum(e.repair_cost for e in estimates),
            "total_replacement_cost": sum(e.replacement_cost for e in estimates),
            "total_contents_loss": sum(e.contents_loss for e in estimates),
            "total_business_interruption": sum(e.business_interruption for e in estimates),
            "grand_total": sum(e.total_estimate for e in estimates),
            "structure_count": len(estimates),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get cost estimation metrics."""
        estimates = list(self._estimates.values())
        return {
            "total_estimates": len(estimates),
            "total_estimated_damage": sum(e.total_estimate for e in estimates),
            "average_estimate": sum(e.total_estimate for e in estimates) / len(estimates) if estimates else 0,
            "by_damage_level": {
                level.value: sum(e.total_estimate for e in estimates if e.damage_level == level)
                for level in DamageLevel
            },
        }


class RecoveryTimelineEngine:
    """
    Plans and tracks recovery timelines.
    """

    def __init__(self):
        self._timelines: Dict[str, RecoveryTimeline] = {}

    def create_timeline(
        self,
        area_name: str,
        total_structures_affected: int,
        damage_summary: Dict[str, int],
    ) -> RecoveryTimeline:
        """Create a recovery timeline for an area."""
        timeline_id = f"timeline-{uuid.uuid4().hex[:8]}"
        area_id = f"area-{uuid.uuid4().hex[:6]}"

        phases = self._plan_phases(total_structures_affected, damage_summary)
        milestones = self._define_milestones(phases)
        estimated_completion = self._estimate_completion(phases)

        timeline = RecoveryTimeline(
            timeline_id=timeline_id,
            area_id=area_id,
            area_name=area_name,
            current_phase=RecoveryPhase.EMERGENCY,
            phases=phases,
            total_structures_affected=total_structures_affected,
            structures_repaired=0,
            structures_demolished=0,
            estimated_completion=estimated_completion,
            milestones=milestones,
            blockers=[],
        )

        self._timelines[timeline_id] = timeline
        return timeline

    def _plan_phases(
        self,
        structures: int,
        damage_summary: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """Plan recovery phases."""
        destroyed = damage_summary.get("destroyed", 0)
        major = damage_summary.get("major", 0)
        moderate = damage_summary.get("moderate", 0)
        minor = damage_summary.get("minor", 0)

        return [
            {
                "phase": RecoveryPhase.EMERGENCY.value,
                "name": "Emergency Response",
                "duration_days": 7,
                "objectives": [
                    "Search and rescue",
                    "Secure hazardous structures",
                    "Establish temporary shelter",
                ],
                "status": "in_progress",
            },
            {
                "phase": RecoveryPhase.SHORT_TERM.value,
                "name": "Short-Term Recovery",
                "duration_days": 30,
                "objectives": [
                    "Restore utilities",
                    "Begin debris removal",
                    f"Repair {minor} minor damage structures",
                ],
                "status": "pending",
            },
            {
                "phase": RecoveryPhase.INTERMEDIATE.value,
                "name": "Intermediate Recovery",
                "duration_days": 90,
                "objectives": [
                    f"Repair {moderate} moderate damage structures",
                    "Begin major repairs",
                    "Demolish unsafe structures",
                ],
                "status": "pending",
            },
            {
                "phase": RecoveryPhase.LONG_TERM.value,
                "name": "Long-Term Recovery",
                "duration_days": 365,
                "objectives": [
                    f"Complete {major} major repairs",
                    f"Rebuild {destroyed} destroyed structures",
                    "Full community restoration",
                ],
                "status": "pending",
            },
        ]

    def _define_milestones(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Define recovery milestones."""
        milestones = []
        cumulative_days = 0

        for phase in phases:
            cumulative_days += phase.get("duration_days", 0)
            milestones.append({
                "milestone": f"{phase.get('name')} Complete",
                "target_date": (datetime.utcnow() + timedelta(days=cumulative_days)).isoformat(),
                "status": "pending",
            })

        return milestones

    def _estimate_completion(self, phases: List[Dict[str, Any]]) -> datetime:
        """Estimate overall completion date."""
        total_days = sum(p.get("duration_days", 0) for p in phases)
        return datetime.utcnow() + timedelta(days=total_days)

    def update_progress(
        self,
        timeline_id: str,
        structures_repaired: Optional[int] = None,
        structures_demolished: Optional[int] = None,
        current_phase: Optional[str] = None,
    ) -> RecoveryTimeline:
        """Update recovery progress."""
        timeline = self._timelines.get(timeline_id)
        if not timeline:
            raise ValueError(f"Timeline {timeline_id} not found")

        if structures_repaired is not None:
            timeline.structures_repaired = structures_repaired
        if structures_demolished is not None:
            timeline.structures_demolished = structures_demolished
        if current_phase:
            timeline.current_phase = RecoveryPhase(current_phase)

        timeline.updated_at = datetime.utcnow()
        return timeline

    def add_blocker(self, timeline_id: str, blocker: str) -> RecoveryTimeline:
        """Add a blocker to the timeline."""
        timeline = self._timelines.get(timeline_id)
        if not timeline:
            raise ValueError(f"Timeline {timeline_id} not found")

        timeline.blockers.append(blocker)
        timeline.updated_at = datetime.utcnow()
        return timeline

    def get_timeline(self, timeline_id: str) -> Optional[RecoveryTimeline]:
        """Get timeline by ID."""
        return self._timelines.get(timeline_id)

    def get_timelines(self, phase: Optional[RecoveryPhase] = None) -> List[RecoveryTimeline]:
        """Get timelines, optionally filtered by phase."""
        timelines = list(self._timelines.values())
        if phase:
            timelines = [t for t in timelines if t.current_phase == phase]
        return timelines

    def get_metrics(self) -> Dict[str, Any]:
        """Get recovery timeline metrics."""
        timelines = list(self._timelines.values())
        return {
            "total_timelines": len(timelines),
            "total_structures_affected": sum(t.total_structures_affected for t in timelines),
            "total_repaired": sum(t.structures_repaired for t in timelines),
            "total_demolished": sum(t.structures_demolished for t in timelines),
            "by_phase": {
                p.value: len([t for t in timelines if t.current_phase == p])
                for p in RecoveryPhase
            },
            "total_blockers": sum(len(t.blockers) for t in timelines),
        }


class DamageAssessmentManager:
    """
    Main damage assessment coordinator.
    """

    def __init__(self):
        self.drone_classifier = DroneImageDamageClassifier()
        self.risk_scorer = StructuralRiskScorer()
        self.cost_model = CostEstimationModel()
        self.recovery_engine = RecoveryTimelineEngine()
        self._assessments: Dict[str, DamageAssessment] = {}

    def create_assessment(
        self,
        address: Dict[str, Any],
        structure_type: str,
        damage_level: str,
        damage_types: List[str],
        damage_description: str,
        affected_area_sqft: float,
        assessed_by: str,
    ) -> DamageAssessment:
        """Create a damage assessment."""
        assessment_id = f"assess-{uuid.uuid4().hex[:8]}"
        structure_id = f"struct-{uuid.uuid4().hex[:6]}"

        type_enum = StructureType(structure_type) if structure_type in [t.value for t in StructureType] else StructureType.RESIDENTIAL_SINGLE
        level_enum = DamageLevel(damage_level) if damage_level in [l.value for l in DamageLevel] else DamageLevel.MODERATE

        damage_type_enums = []
        for dt in damage_types:
            if dt in [t.value for t in DamageType]:
                damage_type_enums.append(DamageType(dt))

        assessment = DamageAssessment(
            assessment_id=assessment_id,
            structure_id=structure_id,
            address=address,
            structure_type=type_enum,
            damage_level=level_enum,
            damage_types=damage_type_enums,
            damage_description=damage_description,
            affected_area_sqft=affected_area_sqft,
            habitability=level_enum in [DamageLevel.NONE, DamageLevel.MINOR],
            utilities_status={"power": "unknown", "water": "unknown", "gas": "unknown"},
            estimated_cost=0,
            insurance_claim_filed=False,
            assessment_status=AssessmentStatus.COMPLETED,
            assessed_by=assessed_by,
            drone_images=[],
            photos=[],
        )

        self._assessments[assessment_id] = assessment
        return assessment

    def get_assessment(self, assessment_id: str) -> Optional[DamageAssessment]:
        """Get assessment by ID."""
        return self._assessments.get(assessment_id)

    def get_assessments(
        self,
        damage_level: Optional[DamageLevel] = None,
        structure_type: Optional[StructureType] = None,
    ) -> List[DamageAssessment]:
        """Get assessments, optionally filtered."""
        assessments = list(self._assessments.values())
        if damage_level:
            assessments = [a for a in assessments if a.damage_level == damage_level]
        if structure_type:
            assessments = [a for a in assessments if a.structure_type == structure_type]
        return assessments

    def create_area_summary(self, area_name: str) -> AreaDamageSummary:
        """Create damage summary for an area."""
        area_id = f"area-{uuid.uuid4().hex[:6]}"
        assessments = list(self._assessments.values())

        by_damage = {level.value: 0 for level in DamageLevel}
        by_type = {stype.value: 0 for stype in StructureType}

        for assessment in assessments:
            by_damage[assessment.damage_level.value] += 1
            by_type[assessment.structure_type.value] += 1

        total_cost = sum(a.estimated_cost for a in assessments)
        displaced = len([a for a in assessments if not a.habitability]) * 3

        return AreaDamageSummary(
            area_id=area_id,
            area_name=area_name,
            total_structures=len(assessments),
            by_damage_level=by_damage,
            by_structure_type=by_type,
            total_estimated_cost=total_cost,
            population_displaced=displaced,
            businesses_affected=len([
                a for a in assessments
                if a.structure_type in [StructureType.COMMERCIAL, StructureType.INDUSTRIAL]
            ]),
            critical_infrastructure_damaged=len([
                a for a in assessments
                if a.structure_type in [StructureType.INFRASTRUCTURE, StructureType.UTILITY, StructureType.HEALTHCARE]
                and a.damage_level in [DamageLevel.MAJOR, DamageLevel.DESTROYED]
            ]),
        )

    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall damage assessment metrics."""
        return {
            "assessments": {
                "total": len(self._assessments),
                "by_damage_level": {
                    level.value: len([a for a in self._assessments.values() if a.damage_level == level])
                    for level in DamageLevel
                },
            },
            "drone_images": self.drone_classifier.get_damage_summary(),
            "risk_assessments": self.risk_scorer.get_metrics(),
            "cost_estimates": self.cost_model.get_metrics(),
            "recovery": self.recovery_engine.get_metrics(),
        }
