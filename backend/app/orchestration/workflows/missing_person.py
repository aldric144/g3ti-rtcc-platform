"""
Workflow 3: Missing Person Response
Missing person → LPR sweep → Drone grid → Human stability engine → Alerts
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_missing_person_workflow() -> Workflow:
    return Workflow(
        name="Missing Person Response",
        description="Coordinated search for missing persons using LPR, drones, and multi-agency coordination",
        version="1.0.0",
        category="search_rescue",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["missing_person", "endangered_missing", "silver_alert"],
                event_sources=["911_dispatch", "investigations", "ncic"],
                conditions={},
            ),
        ],
        steps=[
            WorkflowStep(
                name="Gather Subject Information",
                description="Collect and verify missing person details",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"gather_photos": True, "gather_vehicle_info": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["data_accuracy"],
            ),
            WorkflowStep(
                name="Initiate LPR Sweep",
                description="Search LPR database for associated vehicles",
                action_type="lpr_sweep",
                target_subsystem="lpr_network",
                parameters={"search_radius_miles": 50, "time_window_hours": 24},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=60,
                guardrails=["privacy_protection"],
            ),
            WorkflowStep(
                name="Deploy Search Drones",
                description="Deploy drone grid for aerial search",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "grid_search", "search_pattern": "expanding_square"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=60,
                guardrails=["airspace_clearance"],
            ),
            WorkflowStep(
                name="Activate Human Stability Engine",
                description="Assess risk factors and behavioral patterns",
                action_type="human_stability_alert",
                target_subsystem="human_stability",
                parameters={"assessment_type": "missing_person_risk", "include_mental_health": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["mental_health_privacy"],
            ),
            WorkflowStep(
                name="Issue BOLO",
                description="Issue Be On Lookout alert to all units",
                action_type="bolo_issue",
                target_subsystem="dispatch",
                parameters={"distribution": "all_units", "include_photo": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["bolo_protocol"],
            ),
            WorkflowStep(
                name="Notify Fusion Cloud",
                description="Share missing person info with multi-agency fusion cloud",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"share_level": "regional", "include_ncic": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["inter_agency_sharing"],
            ),
            WorkflowStep(
                name="Activate Cell Phone Tracking",
                description="Request cell phone location data if authorized",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"tracking_type": "cell_location", "requires_authorization": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["warrant_requirement", "privacy_protection"],
            ),
            WorkflowStep(
                name="Check Known Locations",
                description="Cross-reference with known addresses and frequented locations",
                action_type="predictive_alert",
                target_subsystem="predictive_intel",
                parameters={"analysis_type": "location_prediction", "include_social_connections": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=45,
                guardrails=["privacy_protection"],
            ),
            WorkflowStep(
                name="Prepare Public Alert",
                description="Prepare public notification if criteria met",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"alert_type": "missing_person", "status": "pending_approval"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["public_alert_criteria"],
            ),
            WorkflowStep(
                name="Coordinate Search Teams",
                description="Organize and deploy ground search teams",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "search_team", "coordination_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["search_protocol"],
            ),
        ],
        required_inputs=["subject_name", "last_known_location", "physical_description"],
        guardrails=["missing_person_protocol", "privacy_protection"],
        legal_guardrails=["privacy_laws", "data_sharing_agreements"],
        ethical_guardrails=["family_sensitivity", "media_coordination"],
        timeout_seconds=600,
        priority=2,
    )


MissingPersonWorkflow = create_missing_person_workflow()
