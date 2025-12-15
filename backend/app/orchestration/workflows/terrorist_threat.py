"""
Workflow 16: Terrorist Threat Response
National security engine → Fusion cloud → Tactical response
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_terrorist_threat_workflow() -> Workflow:
    return Workflow(
        name="Terrorist Threat Response",
        description="Coordinated response to terrorist threats and attacks",
        version="1.0.0",
        category="national_security",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["terrorist_threat", "terrorism_alert", "suspicious_activity_terrorism"],
                event_sources=["threat_intel", "fusion_cloud", "fbi_jttf"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Assess Threat Credibility",
                description="Evaluate terrorist threat credibility",
                action_type="threat_assessment",
                target_subsystem="threat_intel",
                parameters={"assessment_type": "terrorism", "include_intel_sources": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["threat_assessment_protocol"],
            ),
            WorkflowStep(
                name="Notify JTTF",
                description="Alert FBI Joint Terrorism Task Force",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"recipients": ["fbi_jttf", "dhs"], "priority": "critical"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["federal_notification"],
            ),
            WorkflowStep(
                name="Activate National Security Engine",
                description="Engage national security protocols",
                action_type="threat_broadcast",
                target_subsystem="threat_intel",
                parameters={"protocol": "national_security", "classification": "sensitive"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["national_security_protocol"],
            ),
            WorkflowStep(
                name="Deploy Tactical Response",
                description="Deploy tactical and bomb squad units",
                action_type="patrol_reroute",
                target_subsystem="dispatch",
                parameters={"unit_type": ["tactical", "bomb_squad"], "priority": "emergency"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["tactical_deployment"],
            ),
            WorkflowStep(
                name="Secure Critical Infrastructure",
                description="Enhance security at critical infrastructure",
                action_type="resource_allocate",
                target_subsystem="city_autonomy",
                parameters={"action": "infrastructure_security", "level": "elevated"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["infrastructure_protection"],
            ),
            WorkflowStep(
                name="Deploy Surveillance Assets",
                description="Deploy all available surveillance assets",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "security_surveillance", "deploy_all": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["surveillance_protocol"],
            ),
            WorkflowStep(
                name="Coordinate with State/Federal",
                description="Coordinate with state and federal agencies",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"coordination_level": "full", "include_military": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["inter_agency_coordination"],
            ),
            WorkflowStep(
                name="Public Warning",
                description="Issue public safety warning if appropriate",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"notification_type": "security_alert", "approval_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["public_communication"],
            ),
            WorkflowStep(
                name="Stage Mass Casualty Resources",
                description="Pre-position mass casualty resources",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "mass_casualty", "standby": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["mci_protocol"],
            ),
            WorkflowStep(
                name="Create Classified Case",
                description="Create investigation case with appropriate classification",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "terrorism", "classification": "sensitive"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["classified_handling"],
            ),
        ],
        required_inputs=["threat_type", "target", "source_intel"],
        guardrails=["national_security_protocol", "classified_handling"],
        legal_guardrails=["patriot_act", "fisa"],
        ethical_guardrails=["civil_liberties", "proportionality"],
        timeout_seconds=300,
        priority=1,
    )


TerroristThreatWorkflow = create_terrorist_threat_workflow()
