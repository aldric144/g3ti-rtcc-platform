"""
Workflow 19: Mental Health Crisis Response
Human stability → Co-responder → De-escalation
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_mental_health_crisis_workflow() -> Workflow:
    return Workflow(
        name="Mental Health Crisis Response",
        description="Coordinated response to mental health crisis calls",
        version="1.0.0",
        category="crisis_intervention",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["mental_health_crisis", "psychiatric_emergency", "suicide_threat"],
                event_sources=["dispatch", "human_stability", "911_dispatch"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Assess Crisis Level",
                description="Evaluate mental health crisis severity",
                action_type="human_stability_alert",
                target_subsystem="human_stability",
                parameters={"assessment_type": "mental_health_crisis", "include_history": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["mental_health_protocol"],
            ),
            WorkflowStep(
                name="Deploy Co-Responder",
                description="Dispatch mental health co-responder team",
                action_type="co_responder_dispatch",
                target_subsystem="dispatch",
                parameters={"team_type": "mental_health", "priority": "high"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["co_responder_protocol"],
            ),
            WorkflowStep(
                name="Alert CIT Officers",
                description="Notify CIT-trained officers in area",
                action_type="officer_alert",
                target_subsystem="officer_safety",
                parameters={"certification_required": "CIT", "priority": "high"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["cit_protocol"],
            ),
            WorkflowStep(
                name="Gather Subject History",
                description="Retrieve mental health contact history",
                action_type="investigation_update",
                target_subsystem="human_stability",
                parameters={"gather_history": True, "include_treatment": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["hipaa_compliance"],
            ),
            WorkflowStep(
                name="Prepare De-escalation Resources",
                description="Stage de-escalation tools and resources",
                action_type="resource_allocate",
                target_subsystem="tactical_analytics",
                parameters={"resource_type": "de_escalation", "non_lethal_only": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["de_escalation_priority"],
            ),
            WorkflowStep(
                name="Contact Crisis Line",
                description="Coordinate with crisis hotline if applicable",
                action_type="notification_send",
                target_subsystem="human_stability",
                parameters={"recipients": ["crisis_hotline"], "warm_handoff": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["crisis_coordination"],
            ),
            WorkflowStep(
                name="Stage EMS",
                description="Pre-position EMS for potential transport",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "baker_act_capable": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Identify Treatment Options",
                description="Identify available treatment facilities",
                action_type="resource_allocate",
                target_subsystem="human_stability",
                parameters={"resource_type": "treatment_facility", "bed_availability": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["treatment_coordination"],
            ),
            WorkflowStep(
                name="Notify Supervisor",
                description="Alert supervisor of crisis response",
                action_type="supervisor_alert",
                target_subsystem="officer_safety",
                parameters={"alert_type": "mental_health_crisis", "monitoring": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["chain_of_command"],
            ),
            WorkflowStep(
                name="Document Intervention",
                description="Create crisis intervention documentation",
                action_type="case_generation",
                target_subsystem="human_stability",
                parameters={"case_type": "crisis_intervention", "include_outcome": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["documentation_requirements"],
            ),
        ],
        required_inputs=["location", "subject_description", "crisis_type"],
        guardrails=["mental_health_protocol", "de_escalation_priority"],
        legal_guardrails=["hipaa_compliance", "baker_act"],
        ethical_guardrails=["dignity_preservation", "least_restrictive_intervention"],
        timeout_seconds=300,
        priority=2,
    )


MentalHealthCrisisWorkflow = create_mental_health_crisis_workflow()
