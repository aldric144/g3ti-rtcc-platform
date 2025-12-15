"""
Workflow 12: Cyber Attack Response
Cyber intel → System isolation → Incident response
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_cyber_attack_workflow() -> Workflow:
    return Workflow(
        name="Cyber Attack Response",
        description="Coordinated response to cyber attacks on city infrastructure",
        version="1.0.0",
        category="cyber_security",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["cyber_attack", "ransomware", "network_intrusion", "data_breach"],
                event_sources=["cyber_intel", "it_security", "fusion_cloud"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Assess Attack Scope",
                description="Determine scope and severity of cyber attack",
                action_type="threat_assessment",
                target_subsystem="cyber_intel",
                parameters={"assessment_type": "cyber_attack", "include_iocs": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["cyber_assessment_protocol"],
            ),
            WorkflowStep(
                name="Isolate Affected Systems",
                description="Isolate compromised systems from network",
                action_type="emergency_broadcast",
                target_subsystem="cyber_intel",
                parameters={"action": "network_isolation", "preserve_evidence": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["system_isolation_protocol"],
            ),
            WorkflowStep(
                name="Alert IT Security Team",
                description="Notify IT security and incident response team",
                action_type="notification_send",
                target_subsystem="cyber_intel",
                parameters={"recipients": ["it_security", "incident_response"], "priority": "critical"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=10,
                guardrails=["notification_protocol"],
            ),
            WorkflowStep(
                name="Activate Backup Systems",
                description="Switch to backup systems if available",
                action_type="resource_allocate",
                target_subsystem="cyber_intel",
                parameters={"resource_type": "backup_systems", "failover": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["business_continuity"],
            ),
            WorkflowStep(
                name="Notify FBI Cyber Division",
                description="Report attack to federal authorities",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"report_type": "cyber_incident", "recipients": ["fbi_cyber", "cisa"]},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["federal_reporting"],
            ),
            WorkflowStep(
                name="Preserve Evidence",
                description="Capture forensic evidence",
                action_type="evidence_collection",
                target_subsystem="cyber_intel",
                parameters={"collection_type": "digital_forensics", "chain_of_custody": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=45,
                guardrails=["evidence_preservation"],
            ),
            WorkflowStep(
                name="Assess Critical Infrastructure Impact",
                description="Evaluate impact on critical city systems",
                action_type="digital_twin_update",
                target_subsystem="digital_twin",
                parameters={"assessment_type": "infrastructure_impact", "critical_systems": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["infrastructure_assessment"],
            ),
            WorkflowStep(
                name="Public Communication",
                description="Prepare public communication if needed",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"notification_type": "cyber_incident", "status": "pending_approval"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["public_communication"],
            ),
            WorkflowStep(
                name="Coordinate Recovery",
                description="Begin system recovery procedures",
                action_type="resource_allocate",
                target_subsystem="cyber_intel",
                parameters={"resource_type": "recovery_team", "priority": "high"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["recovery_protocol"],
            ),
            WorkflowStep(
                name="Create Incident Case",
                description="Document cyber incident for investigation",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "cyber_crime", "federal_coordination": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["incident_documentation"],
            ),
        ],
        required_inputs=["attack_type", "affected_systems", "initial_detection"],
        guardrails=["cyber_incident_response", "evidence_preservation"],
        legal_guardrails=["cfaa_compliance", "data_breach_notification"],
        ethical_guardrails=["transparency", "public_safety"],
        timeout_seconds=600,
        priority=1,
    )


CyberAttackWorkflow = create_cyber_attack_workflow()
