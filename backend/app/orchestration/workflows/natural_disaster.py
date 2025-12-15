"""
Workflow 13: Natural Disaster Response
Emergency management → Evacuation → Resource deployment
"""

from ..workflow_engine import Workflow, WorkflowStep, WorkflowTrigger, WorkflowStatus, StepExecutionMode, TriggerType


def create_natural_disaster_workflow() -> Workflow:
    return Workflow(
        name="Natural Disaster Response",
        description="Coordinated response to natural disasters",
        version="1.0.0",
        category="emergency_management",
        triggers=[
            WorkflowTrigger(
                trigger_type=TriggerType.EVENT,
                event_types=["hurricane", "tornado", "flood", "earthquake", "wildfire"],
                event_sources=["weather_service", "emergency_mgmt", "nws"],
            ),
        ],
        steps=[
            WorkflowStep(
                name="Assess Disaster Scope",
                description="Evaluate disaster impact and affected areas",
                action_type="threat_assessment",
                target_subsystem="emergency_mgmt",
                parameters={"assessment_type": "disaster", "include_projections": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["disaster_assessment"],
            ),
            WorkflowStep(
                name="Activate EOC",
                description="Activate Emergency Operations Center",
                action_type="emergency_broadcast",
                target_subsystem="emergency_mgmt",
                parameters={"action": "eoc_activation", "staffing_level": "full"},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=15,
                guardrails=["eoc_protocol"],
            ),
            WorkflowStep(
                name="Issue Evacuation Orders",
                description="Issue evacuation orders for affected zones",
                action_type="notification_send",
                target_subsystem="public_guardian",
                parameters={"notification_type": "evacuation", "channels": ["wea", "sirens", "social_media"]},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=20,
                guardrails=["evacuation_protocol"],
            ),
            WorkflowStep(
                name="Deploy Search and Rescue",
                description="Deploy SAR teams to affected areas",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "search_rescue", "mutual_aid": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["sar_protocol"],
            ),
            WorkflowStep(
                name="Deploy Drones for Assessment",
                description="Deploy drones for damage assessment",
                action_type="drone_dispatch",
                target_subsystem="drone_ops",
                parameters={"mission_type": "damage_assessment", "grid_coverage": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=25,
                guardrails=["airspace_clearance"],
            ),
            WorkflowStep(
                name="Open Shelters",
                description="Activate emergency shelters",
                action_type="resource_allocate",
                target_subsystem="emergency_mgmt",
                parameters={"resource_type": "shelters", "capacity_tracking": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=30,
                guardrails=["shelter_protocol"],
            ),
            WorkflowStep(
                name="Coordinate Utilities",
                description="Coordinate with utility companies",
                action_type="notification_send",
                target_subsystem="city_autonomy",
                parameters={"recipients": ["power_company", "water_utility", "gas_company"]},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["utility_coordination"],
            ),
            WorkflowStep(
                name="Traffic Management",
                description="Implement evacuation traffic management",
                action_type="sensor_activate",
                target_subsystem="traffic_system",
                parameters={"mode": "evacuation", "contraflow": True},
                execution_mode=StepExecutionMode.PARALLEL,
                timeout_seconds=20,
                guardrails=["traffic_management"],
            ),
            WorkflowStep(
                name="Request State/Federal Aid",
                description="Request state and federal disaster assistance",
                action_type="fusion_cloud_sync",
                target_subsystem="fusion_cloud",
                parameters={"request_type": "disaster_assistance", "fema_notification": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=30,
                guardrails=["disaster_declaration"],
            ),
            WorkflowStep(
                name="Document Response",
                description="Document disaster response for FEMA reimbursement",
                action_type="audit_log",
                target_subsystem="compliance",
                parameters={"log_type": "disaster_response", "fema_compliant": True},
                execution_mode=StepExecutionMode.SEQUENTIAL,
                timeout_seconds=10,
                guardrails=["documentation_requirements"],
            ),
        ],
        required_inputs=["disaster_type", "affected_area", "severity"],
        guardrails=["disaster_response_protocol", "life_safety"],
        legal_guardrails=["emergency_powers", "stafford_act"],
        ethical_guardrails=["equitable_response", "vulnerable_populations"],
        timeout_seconds=900,
        priority=1,
    )


NaturalDisasterWorkflow = create_natural_disaster_workflow()
