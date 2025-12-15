"""
Workflow 1: Gunfire Response
Gunfire → Auto-drone dispatch → Tactical recommendations → Suspect prediction
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_gunfire_response_workflow() -> Workflow:
    return Workflow(
        name="Gunfire Response",
        description="Automated response to gunfire detection including drone dispatch, tactical recommendations, and suspect prediction",
        version="1.0.0",
        category="critical_incident",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["gunshot_detected", "shots_fired", "gunfire_alert"],
                event_sources=["gunshot_detection", "sensor_grid", "911_dispatch"],
                conditions={"confirmed": True},
            ),
        ],
        steps=[
            WorkflowStep(
                name="Verify Gunshot Detection",
                description="Confirm gunshot detection from multiple sensors",
                action_type="sensor_verify",
                target_subsystem="sensor_grid",
                parameters={"verification_threshold": 0.85, "multi_sensor_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["data_accuracy"],
            ),
            WorkflowStep(
                name="Alert Dispatch",
                description="Notify dispatch of confirmed gunfire",
                action_type="cad_update",
                target_subsystem="dispatch",
                parameters={"priority": "critical", "call_type": "shots_fired"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["notification_protocol"],
            ),
            WorkflowStep(
                name="Deploy Surveillance Drone",
                description="Dispatch nearest available drone to location",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "surveillance", "priority": "emergency", "capabilities": ["thermal", "spotlight"]},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["airspace_clearance", "operator_certification"],
            ),
            WorkflowStep(
                name="Activate Area Cameras",
                description="Activate and orient nearby cameras to incident location",
                action_type="sensor_activate",
                target_subsystem="cctv_network",
                parameters={"radius_meters": 500, "recording_mode": "high_priority"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["privacy_protection"],
            ),
            WorkflowStep(
                name="Generate Tactical Recommendations",
                description="AI-generated tactical approach recommendations",
                action_type="tactical_analysis",
                target_subsystem="tactical_analytics",
                parameters={"include_cover_positions": True, "include_approach_routes": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["officer_safety_priority"],
            ),
            WorkflowStep(
                name="Run Suspect Prediction",
                description="Predictive analysis for potential suspects based on location and patterns",
                action_type="predictive_alert",
                target_subsystem="predictive_intel",
                parameters={"model": "suspect_prediction", "include_known_offenders": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["bias_detection", "civil_rights_compliance"],
            ),
            WorkflowStep(
                name="Alert Officer Safety System",
                description="Update officer safety system with threat information",
                action_type="officer_alert",
                target_subsystem="officer_safety",
                parameters={"alert_type": "active_gunfire", "radius_miles": 1},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["officer_notification_protocol"],
            ),
            WorkflowStep(
                name="Update Digital Twin",
                description="Update city digital twin with incident data",
                action_type="digital_twin_update",
                target_subsystem="digital_twin",
                parameters={"incident_type": "gunfire", "update_heatmap": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["data_accuracy"],
            ),
            WorkflowStep(
                name="Create Investigation Case",
                description="Pre-fill investigation case with available data",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "shooting", "auto_attach_evidence": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["evidence_chain_of_custody"],
            ),
            WorkflowStep(
                name="Log Audit Trail",
                description="Create comprehensive audit trail for all actions",
                action_type="audit_log",
                target_subsystem="compliance",
                parameters={"log_level": "detailed", "include_timestamps": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["audit_completeness"],
            ),
        ],
        required_inputs=["location", "timestamp", "sensor_id"],
        guardrails=["constitutional_compliance", "use_of_force_policy"],
        legal_guardrails=["fourth_amendment", "due_process"],
        ethical_guardrails=["proportionality", "necessity"],
        timeout_seconds=180,
        priority=1,
    )


GunfireResponseWorkflow = create_gunfire_response_workflow()
