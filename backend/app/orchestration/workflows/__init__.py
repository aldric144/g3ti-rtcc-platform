"""
Phase 38: Workflow Library
Pre-built workflows for automated cross-subsystem orchestration.

Critical Workflows:
1. Gunfire Response - Auto-drone dispatch, tactical recommendations, suspect prediction
2. School Threat - Youth crisis engine, digital twin lockdown, PD command center
3. Missing Person - LPR sweep, drone grid, human stability engine, alerts
4. Hot Vehicle - Multi-agency fusion cloud, automated BOLO, patrol rerouting
5. Crisis Escalation - Co-responder routing, investigations pre-fill
6. Officer Distress - Robotics + drones + dispatch coordination
7. DV Risk Escalation - Human stability engine, supervisor alerts, case generation
8. LPR Hot Hit - Tactical engine, predictive risk, fusion cloud alert
9. Active Shooter - Full tactical response, lockdown, emergency broadcast
10. Pursuit Coordination - Multi-unit coordination, air support, spike deployment
11. Mass Casualty - Emergency management, resource allocation, hospital coordination
12. Cyber Attack - Cyber intel, system isolation, incident response
13. Natural Disaster - Emergency management, evacuation, resource deployment
14. Civil Unrest - Tactical deployment, de-escalation, public safety
15. Amber Alert - Multi-agency coordination, public broadcast, search grid
16. Terrorist Threat - National security engine, fusion cloud, tactical response
17. Drug Operation - Investigations, surveillance, tactical coordination
18. Gang Activity - Intel fusion, predictive analytics, patrol coordination
19. Mental Health Crisis - Human stability, co-responder, de-escalation
20. Traffic Fatality - Investigations, traffic management, notifications
"""

from .gunfire_response import GunfireResponseWorkflow
from .school_threat import SchoolThreatWorkflow
from .missing_person import MissingPersonWorkflow
from .hot_vehicle import HotVehicleWorkflow
from .crisis_escalation import CrisisEscalationWorkflow
from .officer_distress import OfficerDistressWorkflow
from .dv_risk_escalation import DVRiskEscalationWorkflow
from .lpr_hot_hit import LPRHotHitWorkflow
from .active_shooter import ActiveShooterWorkflow
from .pursuit_coordination import PursuitCoordinationWorkflow
from .mass_casualty import MassCasualtyWorkflow
from .cyber_attack import CyberAttackWorkflow
from .natural_disaster import NaturalDisasterWorkflow
from .civil_unrest import CivilUnrestWorkflow
from .amber_alert import AmberAlertWorkflow
from .terrorist_threat import TerroristThreatWorkflow
from .drug_operation import DrugOperationWorkflow
from .gang_activity import GangActivityWorkflow
from .mental_health_crisis import MentalHealthCrisisWorkflow
from .traffic_fatality import TrafficFatalityWorkflow

ALL_WORKFLOWS = [
    GunfireResponseWorkflow,
    SchoolThreatWorkflow,
    MissingPersonWorkflow,
    HotVehicleWorkflow,
    CrisisEscalationWorkflow,
    OfficerDistressWorkflow,
    DVRiskEscalationWorkflow,
    LPRHotHitWorkflow,
    ActiveShooterWorkflow,
    PursuitCoordinationWorkflow,
    MassCasualtyWorkflow,
    CyberAttackWorkflow,
    NaturalDisasterWorkflow,
    CivilUnrestWorkflow,
    AmberAlertWorkflow,
    TerroristThreatWorkflow,
    DrugOperationWorkflow,
    GangActivityWorkflow,
    MentalHealthCrisisWorkflow,
    TrafficFatalityWorkflow,
]

__all__ = [
    "GunfireResponseWorkflow",
    "SchoolThreatWorkflow",
    "MissingPersonWorkflow",
    "HotVehicleWorkflow",
    "CrisisEscalationWorkflow",
    "OfficerDistressWorkflow",
    "DVRiskEscalationWorkflow",
    "LPRHotHitWorkflow",
    "ActiveShooterWorkflow",
    "PursuitCoordinationWorkflow",
    "MassCasualtyWorkflow",
    "CyberAttackWorkflow",
    "NaturalDisasterWorkflow",
    "CivilUnrestWorkflow",
    "AmberAlertWorkflow",
    "TerroristThreatWorkflow",
    "DrugOperationWorkflow",
    "GangActivityWorkflow",
    "MentalHealthCrisisWorkflow",
    "TrafficFatalityWorkflow",
    "ALL_WORKFLOWS",
]
