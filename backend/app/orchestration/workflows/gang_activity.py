"""
Workflow 18: Gang Activity Response
Intel fusion → Predictive analytics → Patrol coordination
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_gang_activity_workflow() -> Workflow:
    return Workflow(
        name="Gang Activity Response",
        description="Coordinated response to gang-related activity and violence",
        version="1.0.0",
        category="gang_violence",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["gang_activity", "gang_violence", "gang_retaliation"],
                event_sources=["investigations", "predictive_intel", "dispatch"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Assess Gang Intel",
                description="Analyze gang intelligence and threat level",
                action_type="threat_assessment",
                target_subsystem="threat_intel",
                parameters={"assessment_type": "gang", "include_social_media": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=25,
                guardrails=["gang_intel_protocol"],
            ),
            WorkflowStep(
                name="Run Predictive Analysis",
                description="Predict potential retaliation and hot spots",
                action_type="predictive_alert",
                target_subsystem="predictive_intel",
                parameters={"model": "gang_violence", "include_retaliation_risk": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["bias_detection"],
            ),
            WorkflowStep(
                name="Coordinate Patrol Deployment",
                description="Deploy patrols to predicted hot spots",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"deployment_type": "hot_spot", "visibility": "high"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["patrol_protocol"],
            ),
            WorkflowStep(
                name="Alert Gang Unit",
                description="Notify specialized gang unit",
                action_type="notification_send",
                target_subsystem="investigations",
                parameters={"recipients": ["gang_unit"], "priority": "high"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["notification_protocol"],
            ),
            WorkflowStep(
                name="Deploy Surveillance",
                description="Deploy surveillance on known gang locations",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "gang_surveillance", "covert": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["surveillance_protocol"],
            ),
            WorkflowStep(
                name="Monitor Social Media",
                description="Monitor gang-related social media activity",
                action_type="threat_broadcast",
                target_subsystem="cyber_intel",
                parameters={"monitoring_type": "gang_social_media", "real_time": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["first_amendment_protection"],
            ),
            WorkflowStep(
                name="Coordinate with Schools",
                description="Alert schools in affected areas",
                action_type="notification_send",
                target_subsystem="communications",
                parameters={"recipients": ["schools"], "alert_type": "security"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["school_notification"],
            ),
            WorkflowStep(
                name="Community Outreach",
                description="Coordinate community intervention resources",
                action_type="human_stability_alert",
                target_subsystem="human_stability",
                parameters={"action": "community_intervention", "gang_outreach": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["community_relations"],
            ),
            WorkflowStep(
                name="Share Regional Intel",
                description="Share intelligence with regional agencies",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"intel_type": "gang", "share_level": "regional"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["intel_sharing"],
            ),
            WorkflowStep(
                name="Update Investigation",
                description="Update gang investigation case files",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"case_type": "gang", "link_related": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["case_documentation"],
            ),
        ],
        required_inputs=["gang_involved", "location", "activity_type"],
        guardrails=["gang_protocol", "civil_rights_compliance"],
        legal_guardrails=["gang_documentation_law", "civil_rights"],
        ethical_guardrails=["bias_prevention", "community_trust"],
        timeout_seconds=400,
        priority=3,
    )


GangActivityWorkflow = create_gang_activity_workflow()
