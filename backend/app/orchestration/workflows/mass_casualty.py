"""
Workflow 11: Mass Casualty Incident
Emergency management → Resource allocation → Hospital coordination
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_mass_casualty_workflow() -> Workflow:
    return Workflow(
        name="Mass Casualty Incident Response",
        description="Coordinated response to mass casualty incidents",
        version="1.0.0",
        category="emergency_management",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["mass_casualty", "mci_declared", "major_accident"],
                event_sources=["emergency_mgmt", "dispatch", "hospital_network"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Declare MCI",
                description="Officially declare mass casualty incident",
                action_type="emergency_broadcast",
                target_subsystem="emergency_mgmt",
                parameters={"declaration_type": "mci", "ics_level": "full"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["mci_protocol"],
            ),
            WorkflowStep(
                name="Activate ICS",
                description="Activate Incident Command System",
                action_type="emergency_broadcast",
                target_subsystem="emergency_mgmt",
                parameters={"action": "ics_activation", "command_structure": "unified"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["ics_protocol"],
            ),
            WorkflowStep(
                name="Deploy All EMS",
                description="Deploy all available EMS resources",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "deploy_all": True, "mutual_aid": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Notify Hospitals",
                description="Alert all area hospitals of incoming casualties",
                action_type="notification_send",
                target_subsystem="emergency_mgmt",
                parameters={"recipients": "all_hospitals", "trauma_alert": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["hospital_notification"],
            ),
            WorkflowStep(
                name="Establish Triage Area",
                description="Coordinate triage area setup",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "triage", "setup_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["triage_protocol"],
            ),
            WorkflowStep(
                name="Deploy Drones for Assessment",
                description="Deploy drones for scene assessment",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "scene_assessment", "thermal": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["airspace_clearance"],
            ),
            WorkflowStep(
                name="Coordinate Traffic Control",
                description="Establish traffic control for emergency access",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"assignment": "traffic_control", "perimeter": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["traffic_control"],
            ),
            WorkflowStep(
                name="Activate Family Reunification",
                description="Set up family reunification center",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "reunification_center", "staff_required": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["reunification_protocol"],
            ),
            WorkflowStep(
                name="Public Information",
                description="Coordinate public information release",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"notification_type": "mci_update", "media_coordination": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["public_information"],
            ),
            WorkflowStep(
                name="Document Incident",
                description="Comprehensive incident documentation",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "mci", "multi_agency": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["incident_documentation"],
            ),
        ],
        required_inputs=["location", "estimated_casualties", "incident_type"],
        guardrails=["mci_protocol", "ics_compliance"],
        legal_guardrails=["hipaa_compliance", "emergency_powers"],
        ethical_guardrails=["triage_ethics", "resource_allocation_fairness"],
        timeout_seconds=600,
        priority=1,
    )


MassCasualtyWorkflow = create_mass_casualty_workflow()
