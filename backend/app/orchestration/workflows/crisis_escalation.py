"""
Workflow 5: Crisis Escalation Response
Crisis escalation → Co-responder routing → Investigations pre-fill
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_crisis_escalation_workflow() -> Workflow:
    return Workflow(
        name="Crisis Escalation Response",
        description="Coordinated response to escalating crisis situations with co-responder deployment",
        version="1.0.0",
        category="crisis_response",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["crisis_escalation", "mental_health_crisis", "behavioral_emergency"],
                event_sources=["911_dispatch", "human_stability", "officer_safety"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Assess Crisis Level",
                description="Evaluate crisis severity and escalation risk",
                action_type="human_stability_alert",
                target_subsystem="human_stability",
                parameters={"assessment_type": "crisis_level", "include_history": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["mental_health_protocol"],
            ),
            WorkflowStep(
                name="Deploy Co-Responder Team",
                description="Dispatch mental health co-responder with officer",
                action_type="co_responder_dispatch",
                target_subsystem="dispatch",
                parameters={"team_type": "mental_health", "priority": "high"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["co_responder_protocol"],
            ),
            WorkflowStep(
                name="Alert Crisis Intervention Team",
                description="Notify CIT-trained officers in area",
                action_type="officer_alert",
                target_subsystem="officer_safety",
                parameters={"alert_type": "cit_request", "certification_required": "CIT"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["officer_certification"],
            ),
            WorkflowStep(
                name="Gather Subject History",
                description="Retrieve relevant mental health and contact history",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"gather_history": True, "include_prior_contacts": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["hipaa_compliance", "privacy_protection"],
            ),
            WorkflowStep(
                name="Prepare De-escalation Resources",
                description="Stage de-escalation tools and resources",
                action_type="resource_allocate",
                target_subsystem="tactical_analytics",
                parameters={"resource_type": "de_escalation", "include_less_lethal": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["use_of_force_policy"],
            ),
            WorkflowStep(
                name="Notify Supervisor",
                description="Alert supervisor of escalating situation",
                action_type="supervisor_alert",
                target_subsystem="officer_safety",
                parameters={"alert_level": "elevated", "response_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["chain_of_command"],
            ),
            WorkflowStep(
                name="Pre-fill Investigation Case",
                description="Create case with available information",
                action_type="case_generation",
                target_subsystem="investigations",
                parameters={"case_type": "crisis_intervention", "auto_populate": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["case_documentation"],
            ),
            WorkflowStep(
                name="Stage EMS Resources",
                description="Pre-position EMS for potential medical needs",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "staging_distance": "safe"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Activate Body Cameras",
                description="Ensure all responding officers have active body cameras",
                action_type="officer_alert",
                target_subsystem="officer_safety",
                parameters={"action": "activate_body_camera", "mandatory": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["body_camera_policy"],
            ),
            WorkflowStep(
                name="Log Intervention",
                description="Document crisis intervention for review",
                action_type="audit_log",
                target_subsystem="compliance",
                parameters={"log_type": "crisis_intervention", "include_outcomes": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=5,
                guardrails=["documentation_requirements"],
            ),
        ],
        required_inputs=["location", "subject_description", "crisis_type"],
        guardrails=["de_escalation_priority", "mental_health_protocol"],
        legal_guardrails=["hipaa_compliance", "ada_compliance"],
        ethical_guardrails=["dignity_preservation", "least_restrictive_intervention"],
        timeout_seconds=300,
        priority=2,
    )


CrisisEscalationWorkflow = create_crisis_escalation_workflow()
