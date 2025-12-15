"""
Workflow 8: LPR Hot Hit Response
LPR hot hit → Tactical engine → Predictive risk → Fusion cloud alert
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_lpr_hot_hit_workflow() -> Workflow:
    return Workflow(
        name="LPR Hot Hit Response",
        description="Coordinated response to license plate reader hot list match",
        version="1.0.0",
        category="vehicle_crime",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["lpr_hot_hit", "ncic_hit", "wanted_plate"],
                event_sources=["lpr_network", "ncic", "fusion_cloud"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Verify Hit",
                description="Confirm LPR hit accuracy and current status",
                action_type="lpr_verify",
                target_subsystem="lpr_network",
                parameters={"verify_ncic": True, "check_image_quality": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["data_accuracy"],
            ),
            WorkflowStep(
                name="Tactical Risk Assessment",
                description="Assess tactical risk based on hit type",
                action_type="tactical_analysis",
                target_subsystem="tactical_analytics",
                parameters={"assessment_type": "vehicle_stop", "include_subject_history": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["officer_safety_priority"],
            ),
            WorkflowStep(
                name="Run Predictive Risk Analysis",
                description="Analyze predictive risk factors",
                action_type="predictive_alert",
                target_subsystem="predictive_intel",
                parameters={"analysis_type": "encounter_risk", "include_patterns": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["bias_detection"],
            ),
            WorkflowStep(
                name="Alert Fusion Cloud",
                description="Share hit with regional fusion cloud",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"alert_type": "lpr_hit", "share_level": "regional"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["inter_agency_protocol"],
            ),
            WorkflowStep(
                name="Dispatch Units",
                description="Dispatch appropriate units based on risk level",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"risk_based_dispatch": True, "minimum_units": 2},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["dispatch_protocol"],
            ),
            WorkflowStep(
                name="Deploy Surveillance",
                description="Deploy drone for vehicle tracking",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "vehicle_surveillance", "maintain_distance": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["airspace_clearance"],
            ),
            WorkflowStep(
                name="Track Vehicle Route",
                description="Monitor vehicle movement through camera network",
                action_type="sensor_activate",
                target_subsystem="traffic_system",
                parameters={"tracking_mode": True, "predict_route": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["privacy_protection"],
            ),
            WorkflowStep(
                name="Prepare Officer Briefing",
                description="Generate tactical briefing for responding officers",
                action_type="officer_alert",
                target_subsystem="officer_safety",
                parameters={"briefing_type": "vehicle_stop", "include_cautions": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["officer_safety_priority"],
            ),
            WorkflowStep(
                name="Link to Investigations",
                description="Connect hit to any related investigations",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"link_related_cases": True, "notify_detectives": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["case_management"],
            ),
            WorkflowStep(
                name="Log Activity",
                description="Document LPR hit and response",
                action_type="audit_log",
                target_subsystem="compliance",
                parameters={"log_type": "lpr_hit", "include_outcome": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["audit_completeness"],
            ),
        ],
        required_inputs=["plate_number", "hit_type", "location", "camera_id"],
        guardrails=["lpr_policy", "constitutional_compliance"],
        legal_guardrails=["fourth_amendment", "reasonable_suspicion"],
        ethical_guardrails=["proportionality", "bias_prevention"],
        timeout_seconds=240,
        priority=3,
    )


LPRHotHitWorkflow = create_lpr_hot_hit_workflow()
