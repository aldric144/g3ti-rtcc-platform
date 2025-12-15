"""
Workflow 14: Civil Unrest Response
Tactical deployment → De-escalation → Public safety
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_civil_unrest_workflow() -> Workflow:
    return Workflow(
        name="Civil Unrest Response",
        description="Coordinated response to civil unrest and large gatherings",
        version="1.0.0",
        category="public_order",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["civil_unrest", "riot", "large_protest", "unlawful_assembly"],
                event_sources=["dispatch", "social_media_intel", "officer_safety"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Assess Situation",
                description="Evaluate crowd size, mood, and potential for violence",
                action_type="threat_assessment",
                target_subsystem="tactical_analytics",
                parameters={"assessment_type": "crowd", "include_social_media": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["crowd_assessment"],
            ),
            WorkflowStep(
                name="Activate Mobile Field Force",
                description="Deploy trained civil disturbance units",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"unit_type": "mobile_field_force", "staging_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["civil_disturbance_protocol"],
            ),
            WorkflowStep(
                name="Deploy Surveillance",
                description="Deploy drones for crowd monitoring",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "crowd_monitoring", "altitude": "high"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["first_amendment_protection"],
            ),
            WorkflowStep(
                name="Establish Communication",
                description="Attempt communication with crowd leaders",
                action_type="notification_send",
                target_subsystem="communications",
                parameters={"action": "crowd_communication", "de_escalation": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["de_escalation_priority"],
            ),
            WorkflowStep(
                name="Prepare De-escalation Resources",
                description="Stage de-escalation and less-lethal options",
                action_type="resource_allocate",
                target_subsystem="tactical_analytics",
                parameters={"resource_type": "civil_disturbance", "less_lethal": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["use_of_force_policy"],
            ),
            WorkflowStep(
                name="Traffic Control",
                description="Implement traffic control around area",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"assignment": "traffic_control", "perimeter": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["traffic_safety"],
            ),
            WorkflowStep(
                name="Stage EMS",
                description="Pre-position EMS resources",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "staging_mode": "standby"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Monitor Social Media",
                description="Real-time social media monitoring",
                action_type="threat_broadcast",
                target_subsystem="cyber_intel",
                parameters={"monitoring_type": "social_media", "keywords": ["protest", "riot"]},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["first_amendment_protection"],
            ),
            WorkflowStep(
                name="Public Information",
                description="Coordinate public information release",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"notification_type": "public_safety", "avoid_area": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["public_information"],
            ),
            WorkflowStep(
                name="Document Response",
                description="Document all actions for review",
                action_type="audit_log",
                target_subsystem="compliance",
                parameters={"log_type": "civil_disturbance", "body_camera_review": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["documentation_requirements"],
            ),
        ],
        required_inputs=["location", "crowd_size", "nature_of_gathering"],
        guardrails=["first_amendment_protection", "de_escalation_priority"],
        legal_guardrails=["constitutional_rights", "use_of_force_law"],
        ethical_guardrails=["proportionality", "peaceful_assembly_rights"],
        timeout_seconds=600,
        priority=2,
    )


CivilUnrestWorkflow = create_civil_unrest_workflow()
