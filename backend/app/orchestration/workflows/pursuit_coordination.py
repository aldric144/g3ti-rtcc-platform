"""
Workflow 10: Pursuit Coordination
Multi-unit coordination → Air support → Spike deployment
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_pursuit_coordination_workflow() -> Workflow:
    return Workflow(
        name="Pursuit Coordination",
        description="Coordinated vehicle pursuit management",
        version="1.0.0",
        category="vehicle_pursuit",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["pursuit_initiated", "vehicle_pursuit", "fleeing_vehicle"],
                event_sources=["dispatch", "officer_safety", "lpr_network"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Authorize Pursuit",
                description="Verify pursuit authorization criteria",
                action_type="policy_validation",
                target_subsystem="compliance",
                parameters={"policy_type": "pursuit", "check_criteria": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["pursuit_policy"],
            ),
            WorkflowStep(
                name="Assign Pursuit Supervisor",
                description="Designate pursuit supervisor",
                action_type="supervisor_alert",
                target_subsystem="officer_safety",
                parameters={"role": "pursuit_supervisor", "immediate": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["chain_of_command"],
            ),
            WorkflowStep(
                name="Coordinate Units",
                description="Coordinate pursuing and support units",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"coordination_mode": "pursuit", "limit_units": 3},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["pursuit_unit_limit"],
            ),
            WorkflowStep(
                name="Deploy Air Support",
                description="Deploy drone for aerial pursuit support",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "pursuit_support", "tracking_mode": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["airspace_clearance"],
            ),
            WorkflowStep(
                name="Track Vehicle Route",
                description="Monitor and predict vehicle route",
                action_type="predictive_alert",
                target_subsystem="predictive_intel",
                parameters={"analysis_type": "pursuit_route", "real_time": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["route_prediction"],
            ),
            WorkflowStep(
                name="Position Spike Strips",
                description="Pre-position spike strip units",
                action_type="resource_allocate",
                target_subsystem="tactical_analytics",
                parameters={"resource_type": "spike_strip", "positions": "predicted_route"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["spike_strip_policy"],
            ),
            WorkflowStep(
                name="Alert Traffic Control",
                description="Coordinate with traffic control",
                action_type="sensor_activate",
                target_subsystem="traffic_system",
                parameters={"action": "clear_route", "signal_preemption": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["traffic_safety"],
            ),
            WorkflowStep(
                name="Stage EMS",
                description="Pre-position EMS along pursuit route",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "staging_mode": "pursuit"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Notify Neighboring Jurisdictions",
                description="Alert neighboring agencies",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"alert_type": "pursuit", "mutual_aid_request": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["inter_agency_protocol"],
            ),
            WorkflowStep(
                name="Document Pursuit",
                description="Real-time pursuit documentation",
                action_type="audit_log",
                target_subsystem="compliance",
                parameters={"log_type": "pursuit", "real_time": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["pursuit_documentation"],
            ),
        ],
        required_inputs=["vehicle_description", "direction", "speed", "reason"],
        guardrails=["pursuit_policy", "public_safety"],
        legal_guardrails=["pursuit_liability", "use_of_force"],
        ethical_guardrails=["proportionality", "public_safety_priority"],
        timeout_seconds=600,
        priority=2,
    )


PursuitCoordinationWorkflow = create_pursuit_coordination_workflow()
