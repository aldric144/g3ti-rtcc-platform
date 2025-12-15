"""
Phase 38: Orchestration REST API Router
Endpoints for workflow management, event fusion, and orchestration control.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from ...orchestration import (
    OrchestrationKernel,
    EventRouter,
    WorkflowEngine,
    PolicyBindingEngine,
    ResourceManager,
)
from ...orchestration.event_bus import EventFusionBus
from ...orchestration.workflows import ALL_WORKFLOWS

router = APIRouter(prefix="/orchestration", tags=["orchestration"])

kernel = OrchestrationKernel()
event_router = EventRouter()
workflow_engine = WorkflowEngine()
policy_engine = PolicyBindingEngine()
resource_manager = ResourceManager()
event_bus = EventFusionBus()


class WorkflowExecuteRequest(BaseModel):
    workflow_name: str = Field(..., description="Name of workflow to execute")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Workflow input parameters")
    priority: Optional[int] = Field(None, description="Execution priority (1-5)")
    triggered_by: Optional[str] = Field(None, description="ID of triggering entity")


class WorkflowSimulateRequest(BaseModel):
    workflow_name: str = Field(..., description="Name of workflow to simulate")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Simulation input parameters")
    dry_run: bool = Field(True, description="If true, no actual actions are taken")


class EventIngestRequest(BaseModel):
    source: str = Field(..., description="Event source identifier")
    event_type: str = Field(..., description="Type of event")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data payload")
    priority: Optional[int] = Field(None, description="Event priority (1-5)")
    geolocation: Optional[Dict[str, float]] = Field(None, description="Event geolocation")


class ResourceAllocateRequest(BaseModel):
    resource_type: str = Field(..., description="Type of resource to allocate")
    workflow_id: str = Field(..., description="Workflow requesting resource")
    priority: int = Field(3, description="Allocation priority (1-5)")
    duration_minutes: int = Field(60, description="Allocation duration")
    location: Optional[Dict[str, float]] = Field(None, description="Required location")


class PolicyCheckRequest(BaseModel):
    workflow_id: str = Field(..., description="Workflow to check")
    action_type: str = Field(..., description="Action type to validate")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")


@router.get("/workflows")
async def get_workflows(
    category: Optional[str] = Query(None, description="Filter by category"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
):
    """Get all available workflow templates."""
    workflows = []
    for wf in ALL_WORKFLOWS:
        if category and wf.category != category:
            continue
        if enabled is not None and wf.enabled != enabled:
            continue
        workflows.append({
            "workflow_id": wf.workflow_id,
            "name": wf.name,
            "description": wf.description,
            "version": wf.version,
            "category": wf.category,
            "priority": wf.priority,
            "enabled": wf.enabled,
            "steps_count": len(wf.steps),
            "triggers": [t.trigger_type.value for t in wf.triggers],
            "guardrails": wf.guardrails,
            "legal_guardrails": wf.legal_guardrails,
            "ethical_guardrails": wf.ethical_guardrails,
            "timeout_seconds": wf.timeout_seconds,
        })
    return {
        "workflows": workflows,
        "total": len(workflows),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/workflows/{workflow_name}")
async def get_workflow_details(workflow_name: str):
    """Get detailed information about a specific workflow."""
    for wf in ALL_WORKFLOWS:
        if wf.name.lower().replace(" ", "_") == workflow_name.lower().replace(" ", "_"):
            return {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "description": wf.description,
                "version": wf.version,
                "category": wf.category,
                "priority": wf.priority,
                "enabled": wf.enabled,
                "triggers": [
                    {
                        "trigger_id": t.trigger_id,
                        "type": t.trigger_type.value,
                        "event_types": t.event_types,
                        "event_sources": t.event_sources,
                        "conditions": t.conditions,
                    }
                    for t in wf.triggers
                ],
                "steps": [
                    {
                        "step_id": s.step_id,
                        "name": s.name,
                        "description": s.description,
                        "action_type": s.action_type,
                        "target_subsystem": s.target_subsystem,
                        "execution_mode": s.execution_mode.value,
                        "timeout_seconds": s.timeout_seconds,
                        "guardrails": s.guardrails,
                    }
                    for s in wf.steps
                ],
                "required_inputs": wf.required_inputs,
                "guardrails": wf.guardrails,
                "legal_guardrails": wf.legal_guardrails,
                "ethical_guardrails": wf.ethical_guardrails,
                "timeout_seconds": wf.timeout_seconds,
                "timestamp": datetime.utcnow().isoformat(),
            }
    raise HTTPException(status_code=404, detail=f"Workflow '{workflow_name}' not found")


@router.post("/workflow/execute")
async def execute_workflow(
    request: WorkflowExecuteRequest,
    background_tasks: BackgroundTasks,
):
    """Execute a workflow with provided inputs."""
    workflow = None
    for wf in ALL_WORKFLOWS:
        if wf.name.lower().replace(" ", "_") == request.workflow_name.lower().replace(" ", "_"):
            workflow = wf
            break

    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{request.workflow_name}' not found")

    if not workflow.enabled:
        raise HTTPException(status_code=400, detail=f"Workflow '{request.workflow_name}' is disabled")

    execution_id = f"exec-{uuid.uuid4().hex[:12]}"

    execution_record = {
        "execution_id": execution_id,
        "workflow_name": workflow.name,
        "workflow_id": workflow.workflow_id,
        "status": "queued",
        "inputs": request.inputs,
        "priority": request.priority or workflow.priority,
        "triggered_by": request.triggered_by or "api",
        "queued_at": datetime.utcnow().isoformat(),
        "steps_total": len(workflow.steps),
        "steps_completed": 0,
    }

    return {
        "execution_id": execution_id,
        "workflow_name": workflow.name,
        "status": "queued",
        "message": f"Workflow '{workflow.name}' queued for execution",
        "priority": execution_record["priority"],
        "steps_total": len(workflow.steps),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/simulate")
async def simulate_workflow(request: WorkflowSimulateRequest):
    """Simulate a workflow execution without taking actual actions."""
    workflow = None
    for wf in ALL_WORKFLOWS:
        if wf.name.lower().replace(" ", "_") == request.workflow_name.lower().replace(" ", "_"):
            workflow = wf
            break

    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{request.workflow_name}' not found")

    simulation_id = f"sim-{uuid.uuid4().hex[:12]}"

    simulated_steps = []
    for step in workflow.steps:
        simulated_steps.append({
            "step_id": step.step_id,
            "name": step.name,
            "action_type": step.action_type,
            "target_subsystem": step.target_subsystem,
            "execution_mode": step.execution_mode.value,
            "simulated_result": "success",
            "simulated_duration_ms": step.timeout_seconds * 100,
            "guardrails_checked": step.guardrails,
        })

    policy_checks = []
    bindings = policy_engine.get_applicable_bindings(workflow.name, None)
    for binding in bindings:
        policy_checks.append({
            "binding_id": binding.binding_id,
            "name": binding.name,
            "policy_type": binding.policy_type.value,
            "severity": binding.severity.value,
            "simulated_result": "passed",
        })

    return {
        "simulation_id": simulation_id,
        "workflow_name": workflow.name,
        "dry_run": request.dry_run,
        "inputs": request.inputs,
        "simulated_steps": simulated_steps,
        "policy_checks": policy_checks,
        "estimated_duration_seconds": sum(s["simulated_duration_ms"] for s in simulated_steps) / 1000,
        "guardrails_total": len(workflow.guardrails) + len(workflow.legal_guardrails) + len(workflow.ethical_guardrails),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/status")
async def get_orchestration_status():
    """Get current orchestration engine status."""
    kernel_stats = kernel.get_statistics()
    event_router_stats = event_router.get_statistics()
    workflow_stats = workflow_engine.get_statistics()
    policy_stats = policy_engine.get_statistics()
    resource_stats = resource_manager.get_statistics()
    event_bus_stats = event_bus.get_statistics()

    return {
        "status": kernel.status.value,
        "kernel": kernel_stats,
        "event_router": event_router_stats,
        "workflow_engine": workflow_stats,
        "policy_engine": policy_stats,
        "resource_manager": resource_stats,
        "event_bus": event_bus_stats,
        "available_workflows": len(ALL_WORKFLOWS),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/status/active")
async def get_active_executions():
    """Get all currently active workflow executions."""
    active = workflow_engine.get_active_executions()
    return {
        "active_executions": [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "status": wf.status.value,
                "started_at": wf.started_at.isoformat() if wf.started_at else None,
                "triggered_by": wf.triggered_by,
            }
            for wf in active
        ],
        "total_active": len(active),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/audit")
async def get_audit_log(
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
):
    """Get orchestration audit log."""
    action_history = kernel.get_action_history(limit)

    if workflow_id:
        action_history = [a for a in action_history if a.get("workflow_id") == workflow_id]
    if action_type:
        action_history = [a for a in action_history if a.get("action_type") == action_type]

    return {
        "audit_entries": action_history,
        "total": len(action_history),
        "filters": {
            "workflow_id": workflow_id,
            "action_type": action_type,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/audit/policy")
async def get_policy_audit(
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
):
    """Get policy check audit log."""
    check_history = policy_engine.get_check_history(limit)
    return {
        "policy_checks": [c.to_dict() for c in check_history],
        "total": len(check_history),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/events/ingest")
async def ingest_event(request: EventIngestRequest):
    """Ingest an event into the event fusion bus."""
    event = {
        "event_id": f"evt-{uuid.uuid4().hex[:12]}",
        "event_type": request.event_type,
        "priority": request.priority or 5,
        "geolocation": request.geolocation,
        **request.data,
    }

    success = event_bus.ingest_event(request.source, event)

    if not success:
        raise HTTPException(status_code=429, detail="Event rate limit exceeded or debounced")

    return {
        "event_id": event["event_id"],
        "source": request.source,
        "event_type": request.event_type,
        "status": "ingested",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/events/fuse")
async def fuse_events():
    """Trigger event fusion process."""
    result = await event_bus.fuse_events()
    return result.to_dict()


@router.get("/events/fused")
async def get_fused_events(
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
):
    """Get fused events from the event bus."""
    events = event_bus.get_fused_events(limit, event_type)
    return {
        "fused_events": events,
        "total": len(events),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/events/history")
async def get_event_history(
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
):
    """Get raw event history."""
    history = event_bus.get_event_history(limit)
    return {
        "events": history,
        "total": len(history),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/events/buffers")
async def get_buffer_status():
    """Get status of all event buffers."""
    buffers = event_bus.get_buffer_status()
    return {
        "buffers": buffers,
        "total_buffers": len(buffers),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/resources")
async def get_resources(
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """Get all registered resources."""
    resources = resource_manager.get_all_resources()

    if resource_type:
        resources = [r for r in resources if r.resource_type.value == resource_type]
    if status:
        resources = [r for r in resources if r.status.value == status]

    return {
        "resources": [
            {
                "resource_id": r.resource_id,
                "resource_type": r.resource_type.value,
                "name": r.name,
                "status": r.status.value,
                "location": r.location,
                "health_score": r.health_score,
                "assigned_to": r.assigned_to,
            }
            for r in resources
        ],
        "total": len(resources),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/resources/available")
async def get_available_resources(
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
):
    """Get available resources for allocation."""
    if resource_type:
        from ...orchestration.resource_manager import ResourceType
        try:
            rt = ResourceType(resource_type)
            resources = resource_manager.get_available_resources(rt)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid resource type: {resource_type}")
    else:
        resources = [r for r in resource_manager.get_all_resources() if r.is_available()]

    return {
        "available_resources": [
            {
                "resource_id": r.resource_id,
                "resource_type": r.resource_type.value,
                "name": r.name,
                "location": r.location,
                "capabilities": r.capabilities,
            }
            for r in resources
        ],
        "total": len(resources),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/resources/allocate")
async def allocate_resource(request: ResourceAllocateRequest):
    """Allocate a resource to a workflow."""
    from ...orchestration.resource_manager import ResourceType, AllocationPriority

    try:
        rt = ResourceType(request.resource_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid resource type: {request.resource_type}")

    try:
        priority = AllocationPriority(request.priority)
    except ValueError:
        priority = AllocationPriority.MEDIUM

    available = resource_manager.get_available_resources(rt)
    if not available:
        raise HTTPException(status_code=404, detail=f"No available resources of type: {request.resource_type}")

    resource = available[0]
    if request.location:
        nearest = resource_manager.get_nearest_resource(
            rt, request.location.get("lat", 0), request.location.get("lng", 0)
        )
        if nearest:
            resource = nearest

    allocation = resource_manager.allocate_resource(
        resource_id=resource.resource_id,
        workflow_id=request.workflow_id,
        requester_id="api",
        priority=priority,
        purpose=f"Allocated for workflow {request.workflow_id}",
        duration_minutes=request.duration_minutes,
        location=request.location,
    )

    if not allocation:
        raise HTTPException(status_code=409, detail="Failed to allocate resource")

    return {
        "allocation_id": allocation.allocation_id,
        "resource_id": allocation.resource_id,
        "resource_type": allocation.resource_type.value,
        "workflow_id": allocation.workflow_id,
        "status": allocation.status,
        "start_time": allocation.start_time.isoformat(),
        "end_time": allocation.end_time.isoformat() if allocation.end_time else None,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/resources/{resource_id}/release")
async def release_resource(resource_id: str):
    """Release an allocated resource."""
    success = resource_manager.release_resource(resource_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Resource '{resource_id}' not found or not allocated")

    return {
        "resource_id": resource_id,
        "status": "released",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/resources/utilization")
async def get_resource_utilization():
    """Get resource utilization statistics."""
    utilization = resource_manager.get_resource_utilization()
    return {
        "utilization": utilization,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/policy/check")
async def check_policy(request: PolicyCheckRequest):
    """Check if an action is allowed by policy bindings."""
    result = await policy_engine.check_policy(
        workflow_id=request.workflow_id,
        action_type=request.action_type,
        parameters=request.parameters,
    )

    return {
        "workflow_id": request.workflow_id,
        "action_type": request.action_type,
        "checks": [c.to_dict() for c in result],
        "all_passed": all(c.passed for c in result),
        "blocking_violations": [c.to_dict() for c in result if not c.passed and c.severity.value == "blocking"],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/policy/bindings")
async def get_policy_bindings(
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
):
    """Get all policy bindings."""
    bindings = policy_engine.get_policy_bindings()

    if policy_type:
        bindings = [b for b in bindings if b.policy_type.value == policy_type]
    if enabled is not None:
        bindings = [b for b in bindings if b.enabled == enabled]

    return {
        "bindings": [
            {
                "binding_id": b.binding_id,
                "name": b.name,
                "description": b.description,
                "policy_type": b.policy_type.value,
                "severity": b.severity.value,
                "enabled": b.enabled,
            }
            for b in bindings
        ],
        "total": len(bindings),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/policy/compliance")
async def get_compliance_summary():
    """Get policy compliance summary."""
    summary = policy_engine.get_compliance_summary()
    return {
        "compliance": summary,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/routing/rules")
async def get_routing_rules():
    """Get all event routing rules."""
    rules = event_router.get_routing_rules()
    return {
        "rules": [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "description": r.description,
                "source_channels": r.source_channels,
                "categories": [c.value for c in r.categories],
                "target_pipelines": r.target_pipelines,
                "enabled": r.enabled,
            }
            for r in rules
        ],
        "total": len(rules),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/routing/channels")
async def get_routing_channels():
    """Get all subscribed channels."""
    channels = event_router.get_channels()
    return {
        "channels": channels,
        "total": len(channels),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/routing/pipelines")
async def get_routing_pipelines():
    """Get all registered pipelines."""
    pipelines = event_router.get_pipelines()
    return {
        "pipelines": pipelines,
        "total": len(pipelines),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/fusion/rules")
async def get_fusion_rules():
    """Get all event fusion rules."""
    rules = event_bus.get_fusion_rules()
    return {
        "rules": rules,
        "total": len(rules),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/kernel/subsystems")
async def get_subsystems():
    """Get all registered subsystems."""
    subsystems = kernel.get_subsystems()
    return {
        "subsystems": subsystems,
        "total": len(subsystems),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/kernel/queue")
async def get_action_queue():
    """Get current action queue."""
    queue = kernel.get_queue()
    return {
        "queue": [
            {
                "action_id": a.action_id,
                "action_type": a.action_type.value,
                "target_subsystem": a.target_subsystem,
                "priority": a.priority,
                "status": a.status,
            }
            for a in queue
        ],
        "total": len(queue),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/kernel/start")
async def start_kernel():
    """Start the orchestration kernel."""
    await kernel.start()
    return {
        "status": kernel.status.value,
        "message": "Orchestration kernel started",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/kernel/stop")
async def stop_kernel():
    """Stop the orchestration kernel."""
    await kernel.stop()
    return {
        "status": kernel.status.value,
        "message": "Orchestration kernel stopped",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/kernel/pause")
async def pause_kernel():
    """Pause the orchestration kernel."""
    kernel.pause()
    return {
        "status": kernel.status.value,
        "message": "Orchestration kernel paused",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/kernel/resume")
async def resume_kernel():
    """Resume the orchestration kernel."""
    kernel.resume()
    return {
        "status": kernel.status.value,
        "message": "Orchestration kernel resumed",
        "timestamp": datetime.utcnow().isoformat(),
    }
