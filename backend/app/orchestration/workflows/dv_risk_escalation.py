"""
Workflow 7: DV Risk Escalation
DV risk escalation → Human stability engine → Supervisor alerts → Case generation
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_dv_risk_escalation_workflow() -> Workflow:
    return Workflow(
        name="DV Risk Escalation Response",
        description="Coordinated response to domestic violence risk escalation",
        version="1.0.0",
        category="domestic_violence",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["dv_risk_elevated", "dv_repeat_call", "protective_order_violation"],
                event_sources=["human_stability", "dispatch", "investigations"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Assess DV Risk Level",
                description="Evaluate domestic violence risk using predictive model",
                action_type="human_stability_alert",
                target_subsystem="human_stability",
                parameters={"assessment_type": "dv_risk", "include_lethality_assessment": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["dv_protocol"],
            ),
            WorkflowStep(
                name="Check Prior History",
                description="Retrieve prior DV calls and protective orders",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"gather_dv_history": True, "check_protective_orders": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["victim_privacy"],
            ),
            WorkflowStep(
                name="Alert Supervisor",
                description="Notify supervisor of elevated DV risk",
                action_type="supervisor_alert",
                target_subsystem="officer_safety",
                parameters={"alert_type": "dv_escalation", "response_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["chain_of_command"],
            ),
            WorkflowStep(
                name="Dispatch DV-Trained Officers",
                description="Ensure responding officers have DV training",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"certification_required": "DV_trained", "minimum_units": 2},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["officer_certification"],
            ),
            WorkflowStep(
                name="Notify Victim Advocate",
                description="Alert victim advocate for potential response",
                action_type="co_responder_dispatch",
                target_subsystem="dispatch",
                parameters={"responder_type": "victim_advocate", "standby": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["victim_services_protocol"],
            ),
            WorkflowStep(
                name="Check Weapons Access",
                description="Review subject's known weapons access",
                action_type="threat_broadcast",
                target_subsystem="threat_intel",
                parameters={"check_type": "weapons_access", "include_permits": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["officer_safety_priority"],
            ),
            WorkflowStep(
                name="Generate Case File",
                description="Create comprehensive DV case file",
                action_type="case_generation",
                target_subsystem="investigations",
                parameters={"case_type": "domestic_violence", "include_risk_assessment": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["case_documentation"],
            ),
            WorkflowStep(
                name="Prepare Safety Planning",
                description="Generate victim safety planning resources",
                action_type="human_stability_alert",
                target_subsystem="human_stability",
                parameters={"action": "safety_planning", "include_resources": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["victim_safety"],
            ),
            WorkflowStep(
                name="Stage EMS",
                description="Pre-position EMS for potential injuries",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "staging_mode": "standby"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Document Response",
                description="Create detailed audit trail of response",
                action_type="audit_log",
                target_subsystem="compliance",
                parameters={"log_type": "dv_response", "include_risk_factors": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["documentation_requirements"],
            ),
        ],
        required_inputs=["location", "parties_involved", "call_history"],
        guardrails=["dv_protocol", "victim_safety_priority"],
        legal_guardrails=["vawa_compliance", "mandatory_arrest_policy"],
        ethical_guardrails=["victim_centered_approach", "trauma_informed"],
        timeout_seconds=300,
        priority=2,
    )


DVRiskEscalationWorkflow = create_dv_risk_escalation_workflow()
