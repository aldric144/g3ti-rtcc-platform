"""
Workflow 2: School Threat Response
School threat → Youth crisis engine → Digital twin lockdown → PD command center
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_school_threat_workflow() -> Workflow:
    return Workflow(
        name="School Threat Response",
        description="Coordinated response to school threats including lockdown, crisis intervention, and command center activation",
        version="1.0.0",
        category="critical_incident",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["school_threat", "school_lockdown", "active_threat_school"],
                event_sources=["911_dispatch", "school_security", "threat_intel"],
                conditions={"location_type": "school"},
            ),
        ],
        steps=[
            WorkflowStep(
                name="Verify Threat",
                description="Verify and assess threat credibility",
                action_type="threat_assessment",
                target_subsystem="threat_intel",
                parameters={"assessment_type": "school_threat", "priority": "immediate"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["threat_verification_protocol"],
            ),
            WorkflowStep(
                name="Initiate School Lockdown",
                description="Trigger digital twin lockdown protocols for affected school",
                action_type="lockdown_initiate",
                target_subsystem="digital_twin",
                parameters={"lockdown_type": "full", "notify_staff": True, "secure_entrances": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["emergency_protocol"],
            ),
            WorkflowStep(
                name="Activate Youth Crisis Engine",
                description="Engage youth crisis intervention protocols",
                action_type="human_stability_alert",
                target_subsystem="human_stability",
                parameters={"crisis_type": "youth", "intervention_level": "immediate"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["youth_protection"],
            ),
            WorkflowStep(
                name="Alert Command Center",
                description="Activate PD command center for incident coordination",
                action_type="emergency_broadcast",
                target_subsystem="emergency_mgmt",
                parameters={"command_level": "tactical", "incident_type": "school_threat"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["command_protocol"],
            ),
            WorkflowStep(
                name="Deploy Tactical Units",
                description="Dispatch tactical response units to school",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"unit_type": "tactical", "staging_required": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["tactical_deployment_protocol"],
            ),
            WorkflowStep(
                name="Deploy Surveillance Assets",
                description="Deploy drones and activate cameras around school perimeter",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "perimeter_surveillance", "priority": "emergency"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["airspace_clearance"],
            ),
            WorkflowStep(
                name="Notify School District",
                description="Send notifications to school district officials",
                action_type="notification_send",
                target_subsystem="communications",
                parameters={"recipients": ["school_district", "superintendent"], "priority": "critical"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["notification_protocol"],
            ),
            WorkflowStep(
                name="Coordinate with EMS",
                description="Pre-stage EMS resources near school",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "staging_location": "nearby"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Parent Notification System",
                description="Prepare parent notification system for activation",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"notification_type": "parent_alert", "status": "standby"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["public_communication_protocol"],
            ),
            WorkflowStep(
                name="Create Incident Case",
                description="Create investigation case with all available data",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "school_threat", "priority": "critical"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["evidence_preservation"],
            ),
        ],
        required_inputs=["school_id", "threat_type", "location"],
        guardrails=["youth_protection", "emergency_response_protocol"],
        legal_guardrails=["student_privacy", "ferpa_compliance"],
        ethical_guardrails=["proportionality", "de_escalation_priority"],
        timeout_seconds=300,
        priority=1,
    )


SchoolThreatWorkflow = create_school_threat_workflow()
