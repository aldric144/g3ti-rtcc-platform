"""
Workflow 15: Amber Alert Response
Multi-agency coordination → Public broadcast → Search grid
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_amber_alert_workflow() -> Workflow:
    return Workflow(
        name="Amber Alert Response",
        description="Coordinated response to child abduction with Amber Alert activation",
        version="1.0.0",
        category="missing_child",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["amber_alert", "child_abduction", "endangered_child"],
                event_sources=["dispatch", "investigations", "ncic"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Verify Amber Alert Criteria",
                description="Confirm case meets Amber Alert criteria",
                action_type="policy_validation",
                target_subsystem="compliance",
                parameters={"policy_type": "amber_alert", "criteria_check": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["amber_alert_criteria"],
            ),
            WorkflowStep(
                name="Issue Amber Alert",
                description="Activate Amber Alert through all channels",
                action_type="emergency_broadcast",
                target_subsystem="public_guardian",
                parameters={"alert_type": "amber_alert", "channels": ["wea", "eas", "highway_signs", "social_media"]},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["amber_alert_protocol"],
            ),
            WorkflowStep(
                name="Notify Multi-Agency",
                description="Alert all regional law enforcement agencies",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"alert_type": "amber_alert", "share_level": "statewide", "ncic_entry": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["inter_agency_protocol"],
            ),
            WorkflowStep(
                name="Deploy Search Grid",
                description="Establish search grid with drones and ground units",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "search_grid", "pattern": "expanding_square"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["search_protocol"],
            ),
            WorkflowStep(
                name="LPR Network Alert",
                description="Add suspect vehicle to LPR hot list",
                action_type="bolo_issue",
                target_subsystem="lpr_network",
                parameters={"alert_type": "amber_alert", "priority": "critical"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["lpr_protocol"],
            ),
            WorkflowStep(
                name="Activate Tip Line",
                description="Set up dedicated tip line",
                action_type="resource_allocate",
                target_subsystem="communications",
                parameters={"resource_type": "tip_line", "staffing": "dedicated"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["tip_line_protocol"],
            ),
            WorkflowStep(
                name="Coordinate Media",
                description="Coordinate with media for maximum exposure",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"notification_type": "media_alert", "press_conference": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=25,
                guardrails=["media_protocol"],
            ),
            WorkflowStep(
                name="FBI Notification",
                description="Notify FBI for potential federal involvement",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"recipients": ["fbi_cac"], "case_type": "child_abduction"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["federal_notification"],
            ),
            WorkflowStep(
                name="Family Liaison",
                description="Assign family liaison officer",
                action_type="resource_allocate",
                target_subsystem="investigations",
                parameters={"resource_type": "family_liaison", "immediate": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["victim_services"],
            ),
            WorkflowStep(
                name="Create Investigation Case",
                description="Create comprehensive investigation case",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "child_abduction", "priority": "critical"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["case_documentation"],
            ),
        ],
        required_inputs=["child_description", "suspect_description", "vehicle_description", "last_seen_location"],
        guardrails=["amber_alert_protocol", "child_safety_priority"],
        legal_guardrails=["amber_alert_law", "ncmec_coordination"],
        ethical_guardrails=["child_protection", "family_sensitivity"],
        timeout_seconds=300,
        priority=1,
    )


AmberAlertWorkflow = create_amber_alert_workflow()
