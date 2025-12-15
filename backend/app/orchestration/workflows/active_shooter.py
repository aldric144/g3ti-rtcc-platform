"""
Workflow 9: Active Shooter Response
Active shooter → Full tactical response → Lockdown → Emergency broadcast
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_active_shooter_workflow() -> Workflow:
    return Workflow(
        name="Active Shooter Response",
        description="Full tactical response to active shooter incident",
        version="1.0.0",
        category="critical_incident",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["active_shooter", "mass_shooting", "active_threat"],
                event_sources=["911_dispatch", "gunshot_detection", "officer_safety"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Confirm Active Shooter",
                description="Verify active shooter situation",
                action_type="threat_assessment",
                target_subsystem="threat_intel",
                parameters={"threat_type": "active_shooter", "priority": "immediate"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["threat_verification"],
            ),
            WorkflowStep(
                name="Emergency Broadcast",
                description="Issue emergency broadcast to all units",
                action_type="emergency_broadcast",
                target_subsystem="dispatch",
                parameters={"code": "active_shooter", "all_units": True, "mutual_aid": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["emergency_protocol"],
            ),
            WorkflowStep(
                name="Initiate Lockdown",
                description="Trigger area lockdown protocols",
                action_type="lockdown_initiate",
                target_subsystem="digital_twin",
                parameters={"lockdown_type": "full", "radius_meters": 500},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["lockdown_protocol"],
            ),
            WorkflowStep(
                name="Deploy Tactical Team",
                description="Immediate SWAT/tactical deployment",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"unit_type": "tactical", "priority": "emergency"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["tactical_deployment"],
            ),
            WorkflowStep(
                name="Deploy All Drones",
                description="Deploy all available drones for surveillance",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "active_shooter_support", "deploy_all": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["emergency_airspace"],
            ),
            WorkflowStep(
                name="Deploy Tactical Robots",
                description="Deploy robots for reconnaissance and support",
                action_type="robot_dispatch",
                target_subsystem="robotics",
                parameters={"mission_type": "tactical_support", "capabilities": ["reconnaissance", "communication"]},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["robot_deployment"],
            ),
            WorkflowStep(
                name="Mass Casualty Staging",
                description="Stage mass casualty resources",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "mass_casualty", "hospitals_notified": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["mci_protocol"],
            ),
            WorkflowStep(
                name="Activate Command Post",
                description="Establish incident command post",
                action_type="emergency_broadcast",
                target_subsystem="emergency_mgmt",
                parameters={"action": "establish_command_post", "ics_activation": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["ics_protocol"],
            ),
            WorkflowStep(
                name="Public Warning",
                description="Issue public safety warning",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"alert_type": "emergency", "channels": ["wireless_emergency_alert", "social_media"]},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["public_alert_protocol"],
            ),
            WorkflowStep(
                name="Create Critical Incident Case",
                description="Initialize critical incident documentation",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "active_shooter", "priority": "critical"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["critical_incident_documentation"],
            ),
        ],
        required_inputs=["location", "shooter_description", "weapon_type"],
        guardrails=["active_shooter_protocol", "life_safety_priority"],
        legal_guardrails=["use_of_force_authorization"],
        ethical_guardrails=["life_preservation", "proportionality"],
        timeout_seconds=180,
        priority=1,
    )


ActiveShooterWorkflow = create_active_shooter_workflow()
