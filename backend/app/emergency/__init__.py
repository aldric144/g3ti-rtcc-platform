"""
Phase 21: AI Emergency Management & Disaster Response Engine (AEMDRE)

Complete AI-driven Emergency Operations Center (EOC) system with:
- Real-time crisis detection (storms, floods, fires, earthquakes, explosions)
- Predictive disaster modeling
- Dynamic evacuation route optimization
- Shelter capacity tracking and resource logistics
- Multi-incident command structure
- Medical surge forecasting
- Damage assessment and recovery management
"""

from backend.app.emergency.crisis_detection_engine import (
    CrisisDetectionEngine,
    StormTracker,
    FloodPredictor,
    FireSpreadModel,
    EarthquakeShakeModel,
    ExplosionImpactModel,
    CrisisType,
    CrisisSeverity,
    AlertLevel,
)

from backend.app.emergency.evacuation_ai import (
    EvacuationManager,
    EvacRouteOptimizer,
    PopulationMovementPredictor,
    SpecialNeedsEvacuationPlanner,
    TrafficSimulationEngine,
    EvacuationZone,
    EvacuationPriority,
)

from backend.app.emergency.resource_logistics import (
    ResourceLogisticsManager,
    ShelterRegistry,
    SupplyChainOptimizer,
    DeploymentAllocator,
    CriticalInfrastructureMonitor,
    ShelterStatus,
    ShelterType,
)

from backend.app.emergency.medical_surge_ai import (
    MedicalSurgeManager,
    HospitalLoadPredictor,
    EMSDemandForecaster,
    TriagePriorityModel,
    MedicalSupplyTracker,
    HospitalStatus,
    TriageLevel,
)

from backend.app.emergency.multi_incident_command import (
    MultiIncidentCommandManager,
    IncidentRoomManager,
    AIIncidentBriefBuilder,
    TaskAssignmentEngine,
    TimelineSync,
    MultiAgencyEOCCoordinator,
    IncidentStatus,
    IncidentPriority,
)

from backend.app.emergency.damage_assessment import (
    DamageAssessmentManager,
    DroneImageDamageClassifier,
    StructuralRiskScorer,
    CostEstimationModel,
    RecoveryTimelineEngine,
    DamageLevel,
    AssessmentStatus,
)

__all__ = [
    "CrisisDetectionEngine",
    "StormTracker",
    "FloodPredictor",
    "FireSpreadModel",
    "EarthquakeShakeModel",
    "ExplosionImpactModel",
    "CrisisType",
    "CrisisSeverity",
    "AlertLevel",
    "EvacuationManager",
    "EvacRouteOptimizer",
    "PopulationMovementPredictor",
    "SpecialNeedsEvacuationPlanner",
    "TrafficSimulationEngine",
    "EvacuationZone",
    "EvacuationPriority",
    "ResourceLogisticsManager",
    "ShelterRegistry",
    "SupplyChainOptimizer",
    "DeploymentAllocator",
    "CriticalInfrastructureMonitor",
    "ShelterStatus",
    "ShelterType",
    "MedicalSurgeManager",
    "HospitalLoadPredictor",
    "EMSDemandForecaster",
    "TriagePriorityModel",
    "MedicalSupplyTracker",
    "HospitalStatus",
    "TriageLevel",
    "MultiIncidentCommandManager",
    "IncidentRoomManager",
    "AIIncidentBriefBuilder",
    "TaskAssignmentEngine",
    "TimelineSync",
    "MultiAgencyEOCCoordinator",
    "IncidentStatus",
    "IncidentPriority",
    "DamageAssessmentManager",
    "DroneImageDamageClassifier",
    "StructuralRiskScorer",
    "CostEstimationModel",
    "RecoveryTimelineEngine",
    "DamageLevel",
    "AssessmentStatus",
]
