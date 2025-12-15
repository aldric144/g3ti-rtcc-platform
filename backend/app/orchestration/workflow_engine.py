"""
Phase 38: Workflow Engine
Implements multi-step automated workflows for cross-subsystem orchestration.
Supports sequential and parallel execution with guardrails and audit logging.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
import asyncio


class WorkflowStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class StepExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class TriggerType(Enum):
    EVENT = "event"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    API = "api"
    CONDITION = "condition"
    CHAIN = "chain"


@dataclass
class WorkflowTrigger:
    trigger_id: str = field(default_factory=lambda: f"trigger-{uuid.uuid4().hex[:8]}")
    trigger_type: TriggerType = TriggerType.EVENT
    event_types: List[str] = field(default_factory=list)
    event_sources: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[str] = None
    enabled: bool = True

    def matches(self, event: Dict[str, Any]) -> bool:
        """Check if event matches this trigger."""
        if not self.enabled:
            return False
        if self.event_types and event.get("event_type") not in self.event_types:
            return False
        if self.event_sources and event.get("source") not in self.event_sources:
            return False
        for key, value in self.conditions.items():
            if event.get(key) != value:
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_id": self.trigger_id,
            "trigger_type": self.trigger_type.value,
            "event_types": self.event_types,
            "event_sources": self.event_sources,
            "conditions": self.conditions,
            "schedule": self.schedule,
            "enabled": self.enabled,
        }


@dataclass
class WorkflowStep:
    step_id: str = field(default_factory=lambda: f"step-{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    action_type: str = ""
    target_subsystem: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_mode: StepExecutionMode = StepExecutionMode.SEQUENTIAL
    timeout_seconds: int = 60
    retry_count: int = 0
    max_retries: int = 3
    guardrails: List[str] = field(default_factory=list)
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "description": self.description,
            "action_type": self.action_type,
            "target_subsystem": self.target_subsystem,
            "parameters": self.parameters,
            "execution_mode": self.execution_mode.value,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "guardrails": self.guardrails,
            "on_success": self.on_success,
            "on_failure": self.on_failure,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class Workflow:
    workflow_id: str = field(default_factory=lambda: f"wf-{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    category: str = "general"
    triggers: List[WorkflowTrigger] = field(default_factory=list)
    steps: List[WorkflowStep] = field(default_factory=list)
    required_inputs: List[str] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)
    guardrails: List[str] = field(default_factory=list)
    legal_guardrails: List[str] = field(default_factory=list)
    ethical_guardrails: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    priority: int = 5
    enabled: bool = True
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    triggered_by: Optional[str] = None
    execution_context: Dict[str, Any] = field(default_factory=dict)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "triggers": [t.to_dict() for t in self.triggers],
            "steps": [s.to_dict() for s in self.steps],
            "required_inputs": self.required_inputs,
            "outputs": self.outputs,
            "guardrails": self.guardrails,
            "legal_guardrails": self.legal_guardrails,
            "ethical_guardrails": self.ethical_guardrails,
            "timeout_seconds": self.timeout_seconds,
            "priority": self.priority,
            "enabled": self.enabled,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "triggered_by": self.triggered_by,
            "execution_context": self.execution_context,
            "audit_log": self.audit_log,
        }

    def add_audit_entry(self, action: str, details: Dict[str, Any] = None):
        """Add an entry to the audit log."""
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details or {},
        })


class WorkflowEngine:
    """
    Executes multi-step workflows across RTCC subsystems.
    Supports sequential and parallel execution with guardrails.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.workflows: Dict[str, Workflow] = {}
        self.workflow_templates: Dict[str, Workflow] = {}
        self.active_executions: Dict[str, Workflow] = {}
        self.execution_history: List[Workflow] = []
        self.step_handlers: Dict[str, Callable] = {}
        self.guardrail_checkers: Dict[str, Callable] = {}
        self.statistics: Dict[str, Any] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "active_executions": 0,
            "average_execution_time_ms": 0.0,
        }
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default step handlers."""
        action_types = [
            "drone_dispatch", "robot_dispatch", "officer_alert",
            "supervisor_alert", "cad_update", "investigation_create",
            "investigation_update", "threat_broadcast", "bolo_issue",
            "patrol_reroute", "lockdown_initiate", "resource_allocate",
            "sensor_activate", "digital_twin_update", "predictive_alert",
            "human_stability_alert", "moral_compass_check", "policy_validation",
            "audit_log", "notification_send", "fusion_cloud_sync",
            "emergency_broadcast", "co_responder_dispatch", "case_generation",
            "evidence_collection", "lpr_sweep", "grid_search",
        ]
        for action_type in action_types:
            self.step_handlers[action_type] = self._default_step_handler

    async def _default_step_handler(
        self, step: WorkflowStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Default handler for workflow steps."""
        return {
            "success": True,
            "message": f"Step {step.name} executed successfully",
            "data": {"action": step.action_type, "target": step.target_subsystem},
        }

    def register_workflow_template(self, workflow: Workflow) -> bool:
        """Register a workflow template."""
        self.workflow_templates[workflow.workflow_id] = workflow
        return True

    def create_workflow_instance(
        self, template_id: str, inputs: Dict[str, Any] = None
    ) -> Optional[Workflow]:
        """Create a workflow instance from a template."""
        template = self.workflow_templates.get(template_id)
        if not template:
            return None

        instance = Workflow(
            name=template.name,
            description=template.description,
            version=template.version,
            category=template.category,
            triggers=[],
            steps=[
                WorkflowStep(
                    name=s.name,
                    description=s.description,
                    action_type=s.action_type,
                    target_subsystem=s.target_subsystem,
                    parameters={**s.parameters, **(inputs or {})},
                    execution_mode=s.execution_mode,
                    timeout_seconds=s.timeout_seconds,
                    max_retries=s.max_retries,
                    guardrails=s.guardrails,
                    on_success=s.on_success,
                    on_failure=s.on_failure,
                )
                for s in template.steps
            ],
            required_inputs=template.required_inputs,
            guardrails=template.guardrails,
            legal_guardrails=template.legal_guardrails,
            ethical_guardrails=template.ethical_guardrails,
            timeout_seconds=template.timeout_seconds,
            priority=template.priority,
            execution_context=inputs or {},
        )
        self.workflows[instance.workflow_id] = instance
        return instance

    async def execute_workflow(
        self, workflow: Workflow, context: Dict[str, Any] = None
    ) -> Workflow:
        """Execute a workflow."""
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        workflow.execution_context = {**workflow.execution_context, **(context or {})}
        workflow.add_audit_entry("workflow_started", {"context": context})

        self.active_executions[workflow.workflow_id] = workflow
        self.statistics["total_executions"] += 1
        self.statistics["active_executions"] += 1

        try:
            for guardrail in workflow.guardrails + workflow.legal_guardrails + workflow.ethical_guardrails:
                checker = self.guardrail_checkers.get(guardrail)
                if checker:
                    check_result = await checker(workflow, context)
                    if not check_result.get("passed", True):
                        workflow.status = WorkflowStatus.FAILED
                        workflow.add_audit_entry("guardrail_failed", {"guardrail": guardrail, "result": check_result})
                        raise Exception(f"Guardrail check failed: {guardrail}")

            sequential_steps = [s for s in workflow.steps if s.execution_mode == StepExecutionMode.SEQUENTIAL]
            parallel_steps = [s for s in workflow.steps if s.execution_mode == StepExecutionMode.PARALLEL]

            for step in sequential_steps:
                await self._execute_step(step, workflow)
                if step.status == WorkflowStatus.FAILED:
                    if step.on_failure:
                        pass
                    else:
                        workflow.status = WorkflowStatus.FAILED
                        break

            if parallel_steps and workflow.status != WorkflowStatus.FAILED:
                await asyncio.gather(*[
                    self._execute_step(step, workflow) for step in parallel_steps
                ])

            if workflow.status != WorkflowStatus.FAILED:
                workflow.status = WorkflowStatus.COMPLETED
                self.statistics["successful_executions"] += 1
            else:
                self.statistics["failed_executions"] += 1

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.add_audit_entry("workflow_error", {"error": str(e)})
            self.statistics["failed_executions"] += 1

        workflow.completed_at = datetime.utcnow()
        workflow.add_audit_entry("workflow_completed", {"status": workflow.status.value})

        del self.active_executions[workflow.workflow_id]
        self.statistics["active_executions"] -= 1
        self.execution_history.append(workflow)

        return workflow

    async def _execute_step(self, step: WorkflowStep, workflow: Workflow):
        """Execute a single workflow step."""
        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.utcnow()
        workflow.add_audit_entry("step_started", {"step_id": step.step_id, "name": step.name})

        try:
            for guardrail in step.guardrails:
                checker = self.guardrail_checkers.get(guardrail)
                if checker:
                    check_result = await checker(step, workflow.execution_context)
                    if not check_result.get("passed", True):
                        step.status = WorkflowStatus.FAILED
                        step.error = f"Guardrail check failed: {guardrail}"
                        return

            handler = self.step_handlers.get(step.action_type, self._default_step_handler)
            result = await handler(step, workflow.execution_context)

            step.result = result
            step.status = WorkflowStatus.COMPLETED if result.get("success") else WorkflowStatus.FAILED
            if not result.get("success"):
                step.error = result.get("error", "Step execution failed")

        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error = str(e)

        step.completed_at = datetime.utcnow()
        workflow.add_audit_entry("step_completed", {
            "step_id": step.step_id,
            "status": step.status.value,
            "error": step.error,
        })

    def execute_workflow_sync(
        self, workflow: Workflow, context: Dict[str, Any] = None
    ) -> Workflow:
        """Execute a workflow synchronously."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.execute_workflow(workflow, context))
        finally:
            loop.close()

    def register_step_handler(self, action_type: str, handler: Callable) -> bool:
        """Register a handler for a step action type."""
        self.step_handlers[action_type] = handler
        return True

    def register_guardrail_checker(self, guardrail: str, checker: Callable) -> bool:
        """Register a guardrail checker."""
        self.guardrail_checkers[guardrail] = checker
        return True

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id) or self.workflow_templates.get(workflow_id)

    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get all workflow templates."""
        return [w.to_dict() for w in self.workflow_templates.values()]

    def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get all active workflow executions."""
        return [w.to_dict() for w in self.active_executions.values()]

    def get_execution_history(
        self, limit: int = 100, status: WorkflowStatus = None
    ) -> List[Dict[str, Any]]:
        """Get workflow execution history."""
        history = self.execution_history[-limit:]
        if status:
            history = [w for w in history if w.status == status]
        return [w.to_dict() for w in history]

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id in self.active_executions:
            workflow = self.active_executions[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.utcnow()
            workflow.add_audit_entry("workflow_cancelled")
            return True
        return False

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        if workflow_id in self.active_executions:
            workflow = self.active_executions[workflow_id]
            workflow.status = WorkflowStatus.PAUSED
            workflow.add_audit_entry("workflow_paused")
            return True
        return False

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        if workflow_id in self.active_executions:
            workflow = self.active_executions[workflow_id]
            if workflow.status == WorkflowStatus.PAUSED:
                workflow.status = WorkflowStatus.RUNNING
                workflow.add_audit_entry("workflow_resumed")
                return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow engine statistics."""
        return {
            **self.statistics,
            "registered_templates": len(self.workflow_templates),
            "registered_handlers": len(self.step_handlers),
            "registered_guardrails": len(self.guardrail_checkers),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def check_trigger(self, event: Dict[str, Any]) -> List[Workflow]:
        """Check if any workflow triggers match the event."""
        triggered_workflows = []
        for template in self.workflow_templates.values():
            if not template.enabled:
                continue
            for trigger in template.triggers:
                if trigger.matches(event):
                    instance = self.create_workflow_instance(
                        template.workflow_id, event
                    )
                    if instance:
                        instance.triggered_by = event.get("event_id", "unknown")
                        triggered_workflows.append(instance)
                    break
        return triggered_workflows
