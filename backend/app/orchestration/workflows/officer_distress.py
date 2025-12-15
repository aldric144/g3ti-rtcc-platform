"""
Workflow 6: Officer Distress Response
Officer distress → Robotics + Drones + Dispatch coordination
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_officer_distress_workflow() -> Workflow:
    return Workflow(
        name="Officer Distress Response",
        description="Immediate coordinated response to officer distress signals",
        version="1.0.0",
        category="officer_safety",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["officer_distress", "panic_button", "man_down", "shots_fired_officer"],
                event_sources=["officer_safety", "dispatch", "radio_system"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Verify Distress Signal",
                description="Confirm officer distress and location",
                action_type="officer_alert",
                target_subsystem="officer_safety",
                parameters={"verification_type": "distress", "attempt_contact": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["officer_safety_priority"],
            ),
            WorkflowStep(
                name="Emergency Dispatch All Units",
                description="Dispatch all available units to officer location",
                action_type="emergency_broadcast",
                target_subsystem="dispatch",
                parameters={"priority": "emergency", "all_units": True, "code": "officer_needs_help"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["emergency_protocol"],
            ),
            WorkflowStep(
                name="Deploy Emergency Drone",
                description="Immediate drone deployment for situational awareness",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "emergency_response", "priority": "critical", "capabilities": ["thermal", "spotlight", "speaker"]},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["emergency_airspace"],
            ),
            WorkflowStep(
                name="Deploy Support Robot",
                description="Deploy tactical robot for officer support",
                action_type="robot_dispatch",
                target_subsystem="robotics",
                parameters={"mission_type": "officer_support", "capabilities": ["communication", "shield"]},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["robot_deployment_protocol"],
            ),
            WorkflowStep(
                name="Alert Tactical Team",
                description="Notify SWAT/tactical team for potential deployment",
                action_type="supervisor_alert",
                target_subsystem="tactical_analytics",
                parameters={"team": "tactical", "standby": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["tactical_protocol"],
            ),
            WorkflowStep(
                name="Dispatch EMS",
                description="Immediate EMS dispatch to location",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "priority": "emergency", "trauma_capable": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Activate Area Cameras",
                description="Orient all nearby cameras to officer location",
                action_type="sensor_activate",
                target_subsystem="cctv_network",
                parameters={"priority": "emergency", "recording_mode": "continuous"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["surveillance_protocol"],
            ),
            WorkflowStep(
                name="Notify Command Staff",
                description="Alert command staff of officer emergency",
                action_type="supervisor_alert",
                target_subsystem="officer_safety",
                parameters={"level": "command", "notification_type": "emergency"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["notification_protocol"],
            ),
            WorkflowStep(
                name="Track Officer Vitals",
                description="Monitor officer biometrics if available",
                action_type="officer_alert",
                target_subsystem="officer_safety",
                parameters={"monitor_vitals": True, "alert_on_anomaly": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["health_monitoring"],
            ),
            WorkflowStep(
                name="Create Critical Incident Case",
                description="Initialize critical incident documentation",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "officer_involved", "priority": "critical"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["critical_incident_protocol"],
            ),
        ],
        required_inputs=["officer_id", "location", "signal_type"],
        guardrails=["officer_safety_priority", "emergency_response"],
        legal_guardrails=["use_of_force_documentation"],
        ethical_guardrails=["life_preservation_priority"],
        timeout_seconds=120,
        priority=1,
    )


OfficerDistressWorkflow = create_officer_distress_workflow()
