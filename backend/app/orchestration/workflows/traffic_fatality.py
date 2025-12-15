"""
Workflow 20: Traffic Fatality Response
Investigations → Traffic management → Notifications
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_traffic_fatality_workflow() -> Workflow:
    return Workflow(
        name="Traffic Fatality Response",
        description="Coordinated response to traffic fatality incidents",
        version="1.0.0",
        category="traffic_investigation",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["traffic_fatality", "fatal_crash", "vehicular_homicide"],
                event_sources=["dispatch", "traffic_system", "ems"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Secure Scene",
                description="Dispatch units to secure crash scene",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"assignment": "scene_security", "perimeter": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["scene_security"],
            ),
            WorkflowStep(
                name="Dispatch Traffic Homicide",
                description="Alert traffic homicide investigators",
                action_type="notification_send",
                target_subsystem="investigations",
                parameters={"recipients": ["traffic_homicide"], "priority": "high"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["investigation_protocol"],
            ),
            WorkflowStep(
                name="Deploy Drone Documentation",
                description="Deploy drone for aerial scene documentation",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "crash_documentation", "photogrammetry": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["evidence_documentation"],
            ),
            WorkflowStep(
                name="Traffic Management",
                description="Implement traffic management around scene",
                action_type="sensor_activate",
                target_subsystem="traffic_system",
                parameters={"action": "detour", "signal_timing": "adjusted"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["traffic_management"],
            ),
            WorkflowStep(
                name="Notify Medical Examiner",
                description="Contact medical examiner's office",
                action_type="notification_send",
                target_subsystem="emergency_mgmt",
                parameters={"recipients": ["medical_examiner"], "response_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["death_investigation"],
            ),
            WorkflowStep(
                name="Evidence Collection",
                description="Deploy evidence collection team",
                action_type="evidence_collection",
                target_subsystem="investigations",
                parameters={"collection_type": "crash_scene", "comprehensive": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["evidence_protocol"],
            ),
            WorkflowStep(
                name="Witness Canvass",
                description="Coordinate witness canvass",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"action": "witness_canvass", "area_search": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["witness_protocol"],
            ),
            WorkflowStep(
                name="Check Nearby Cameras",
                description="Review nearby camera footage",
                action_type="sensor_activate",
                target_subsystem="cctv_network",
                parameters={"action": "footage_review", "time_window_minutes": 30},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["evidence_collection"],
            ),
            WorkflowStep(
                name="Victim Notification",
                description="Coordinate victim notification team",
                action_type="resource_allocate",
                target_subsystem="investigations",
                parameters={"resource_type": "victim_notification", "chaplain": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["death_notification_protocol"],
            ),
            WorkflowStep(
                name="Create Investigation Case",
                description="Create traffic homicide investigation case",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "traffic_fatality", "priority": "high"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["case_documentation"],
            ),
        ],
        required_inputs=["location", "vehicle_count", "fatality_count"],
        guardrails=["traffic_homicide_protocol", "evidence_preservation"],
        legal_guardrails=["death_investigation_law", "evidence_rules"],
        ethical_guardrails=["victim_dignity", "family_sensitivity"],
        timeout_seconds=600,
        priority=2,
    )


TrafficFatalityWorkflow = create_traffic_fatality_workflow()
