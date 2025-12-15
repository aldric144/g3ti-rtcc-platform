"""
Workflow 4: Hot Vehicle Response
Hot vehicle → Multi-agency fusion cloud → Automated BOLO → Patrol rerouting
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_hot_vehicle_workflow() -> Workflow:
    return Workflow(
        name="Hot Vehicle Response",
        description="Coordinated response to stolen or wanted vehicle detection",
        version="1.0.0",
        category="vehicle_crime",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["lpr_hit", "stolen_vehicle", "wanted_vehicle", "bolo_match"],
                event_sources=["lpr_network", "ncic", "dispatch"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Verify LPR Hit",
                description="Confirm vehicle match and current status",
                action_type="lpr_verify",
                target_subsystem="lpr_network",
                parameters={"verify_ncic": True, "check_recent_activity": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["data_accuracy"],
            ),
            WorkflowStep(
                name="Alert Fusion Cloud",
                description="Share hit with multi-agency fusion cloud",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"alert_type": "hot_vehicle", "share_level": "regional"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["inter_agency_protocol"],
            ),
            WorkflowStep(
                name="Issue Automated BOLO",
                description="Generate and distribute BOLO to all units",
                action_type="bolo_issue",
                target_subsystem="dispatch",
                parameters={"distribution": "all_units", "include_photo": True, "include_direction": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["bolo_protocol"],
            ),
            WorkflowStep(
                name="Reroute Patrol Units",
                description="Redirect nearby patrol units to intercept",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"intercept_mode": True, "units_count": 3},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["pursuit_policy"],
            ),
            WorkflowStep(
                name="Deploy Surveillance Drone",
                description="Deploy drone for aerial tracking",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "vehicle_tracking", "maintain_visual": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["airspace_clearance"],
            ),
            WorkflowStep(
                name="Activate Traffic Cameras",
                description="Orient traffic cameras along predicted route",
                action_type="sensor_activate",
                target_subsystem="traffic_system",
                parameters={"tracking_mode": True, "record_high_priority": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["privacy_protection"],
            ),
            WorkflowStep(
                name="Run Predictive Route Analysis",
                description="Predict likely vehicle route and destination",
                action_type="predictive_alert",
                target_subsystem="predictive_intel",
                parameters={"analysis_type": "route_prediction", "include_known_addresses": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["bias_detection"],
            ),
            WorkflowStep(
                name="Prepare Spike Strip Deployment",
                description="Pre-position spike strip units if pursuit authorized",
                action_type="resource_allocate",
                target_subsystem="tactical_analytics",
                parameters={"resource_type": "spike_strip", "authorization_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["use_of_force_policy"],
            ),
            WorkflowStep(
                name="Notify Investigations",
                description="Alert investigations unit for case coordination",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"case_type": "vehicle_crime", "link_existing": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["case_management"],
            ),
            WorkflowStep(
                name="Log Audit Trail",
                description="Document all actions for accountability",
                action_type="audit_log",
                target_subsystem="compliance",
                parameters={"log_level": "detailed"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["audit_completeness"],
            ),
        ],
        required_inputs=["plate_number", "vehicle_description", "location", "direction"],
        guardrails=["pursuit_policy", "constitutional_compliance"],
        legal_guardrails=["fourth_amendment", "pursuit_liability"],
        ethical_guardrails=["public_safety_priority", "proportionality"],
        timeout_seconds=300,
        priority=2,
    )


HotVehicleWorkflow = create_hot_vehicle_workflow()
