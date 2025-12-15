"""
Workflow 17: Drug Operation Response
Investigations → Surveillance → Tactical coordination
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_drug_operation_workflow() -> Workflow:
    return Workflow(
        name="Drug Operation Response",
        description="Coordinated response to drug trafficking and distribution operations",
        version="1.0.0",
        category="narcotics",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["drug_operation", "narcotics_intel", "drug_trafficking"],
                event_sources=["investigations", "threat_intel", "dea"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Verify Intelligence",
                description="Verify and assess drug operation intelligence",
                action_type="threat_assessment",
                target_subsystem="threat_intel",
                parameters={"assessment_type": "narcotics", "include_dea_intel": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["intel_verification"],
            ),
            WorkflowStep(
                name="Coordinate with DEA",
                description="Notify and coordinate with DEA if applicable",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"recipients": ["dea"], "case_type": "narcotics"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["federal_coordination"],
            ),
            WorkflowStep(
                name="Deploy Surveillance",
                description="Establish covert surveillance on targets",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "covert_surveillance", "low_profile": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["surveillance_protocol"],
            ),
            WorkflowStep(
                name="LPR Monitoring",
                description="Add target vehicles to LPR monitoring",
                action_type="sensor_activate",
                target_subsystem="lpr_network",
                parameters={"monitoring_type": "covert", "alert_mode": "silent"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=15,
                guardrails=["lpr_protocol"],
            ),
            WorkflowStep(
                name="Prepare Tactical Team",
                description="Brief and stage tactical team for potential raid",
                action_type="resource_allocate",
                target_subsystem="tactical_analytics",
                parameters={"resource_type": "tactical", "briefing_required": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["tactical_protocol"],
            ),
            WorkflowStep(
                name="Obtain Warrants",
                description="Coordinate warrant preparation",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"action": "warrant_preparation", "type": "search_arrest"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=45,
                guardrails=["warrant_requirement"],
            ),
            WorkflowStep(
                name="Asset Forfeiture Prep",
                description="Prepare asset forfeiture documentation",
                action_type="investigation_update",
                target_subsystem="investigations",
                parameters={"action": "asset_documentation", "include_financial": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["asset_forfeiture_protocol"],
            ),
            WorkflowStep(
                name="Stage EMS",
                description="Pre-position EMS for operation",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "ems", "staging_mode": "covert"},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["ems_protocol"],
            ),
            WorkflowStep(
                name="Evidence Team Standby",
                description="Stage evidence collection team",
                action_type="resource_allocate",
                target_subsystem="investigations",
                parameters={"resource_type": "evidence_team", "standby": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["evidence_protocol"],
            ),
            WorkflowStep(
                name="Document Operation",
                description="Create comprehensive operation documentation",
                action_type="investigation_create",
                target_subsystem="investigations",
                parameters={"case_type": "narcotics_operation", "multi_agency": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["case_documentation"],
            ),
        ],
        required_inputs=["target_location", "suspects", "operation_type"],
        guardrails=["narcotics_protocol", "warrant_compliance"],
        legal_guardrails=["fourth_amendment", "controlled_substances_act"],
        ethical_guardrails=["proportionality", "community_impact"],
        timeout_seconds=600,
        priority=3,
    )


DrugOperationWorkflow = create_drug_operation_workflow()
