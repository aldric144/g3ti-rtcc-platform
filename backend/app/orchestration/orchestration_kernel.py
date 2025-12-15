"""
Phase 38: Orchestration Kernel
Master orchestrator that manages workflows triggered by events, AI insights, or officer actions.
Executes actions across all RTCC subsystems.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
import asyncio


class OrchestrationStatus(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class ActionType(Enum):
    DRONE_DISPATCH = "drone_dispatch"
    ROBOT_DISPATCH = "robot_dispatch"
    OFFICER_ALERT = "officer_alert"
    SUPERVISOR_ALERT = "supervisor_alert"
    CAD_UPDATE = "cad_update"
    INVESTIGATION_CREATE = "investigation_create"
    INVESTIGATION_UPDATE = "investigation_update"
    THREAT_BROADCAST = "threat_broadcast"
    BOLO_ISSUE = "bolo_issue"
    PATROL_REROUTE = "patrol_reroute"
    LOCKDOWN_INITIATE = "lockdown_initiate"
    RESOURCE_ALLOCATE = "resource_allocate"
    SENSOR_ACTIVATE = "sensor_activate"
    DIGITAL_TWIN_UPDATE = "digital_twin_update"
    PREDICTIVE_ALERT = "predictive_alert"
    HUMAN_STABILITY_ALERT = "human_stability_alert"
    MORAL_COMPASS_CHECK = "moral_compass_check"
    POLICY_VALIDATION = "policy_validation"
    AUDIT_LOG = "audit_log"
    NOTIFICATION_SEND = "notification_send"
    FUSION_CLOUD_SYNC = "fusion_cloud_sync"
    EMERGENCY_BROADCAST = "emergency_broadcast"
    CO_RESPONDER_DISPATCH = "co_responder_dispatch"
    CASE_GENERATION = "case_generation"
    EVIDENCE_COLLECTION = "evidence_collection"


@dataclass
class OrchestrationAction:
    action_id: str = field(default_factory=lambda: f"action-{uuid.uuid4().hex[:12]}")
    action_type: ActionType = ActionType.AUDIT_LOG
    target_subsystem: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    timeout_seconds: int = 30
    retry_count: int = 0
    max_retries: int = 3
    requires_confirmation: bool = False
    guardrail_checks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "target_subsystem": self.target_subsystem,
            "parameters": self.parameters,
            "priority": self.priority,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "requires_confirmation": self.requires_confirmation,
            "guardrail_checks": self.guardrail_checks,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class OrchestrationResult:
    result_id: str = field(default_factory=lambda: f"result-{uuid.uuid4().hex[:12]}")
    workflow_id: str = ""
    action_id: str = ""
    success: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "workflow_id": self.workflow_id,
            "action_id": self.action_id,
            "success": self.success,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "audit_trail": self.audit_trail,
        }


class OrchestrationKernel:
    """
    Master orchestrator for the RTCC platform.
    Manages workflows triggered by events, AI insights, or officer actions.
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

        self.status = OrchestrationStatus.IDLE
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.action_queue: List[OrchestrationAction] = []
        self.action_history: List[OrchestrationAction] = []
        self.subsystem_handlers: Dict[str, Callable] = {}
        self.event_subscriptions: Dict[str, List[str]] = {}
        self.execution_stats: Dict[str, Any] = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_workflows": 0,
            "active_workflows": 0,
            "average_execution_time_ms": 0.0,
        }
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default subsystem handlers."""
        subsystems = [
            "drone_ops", "robotics", "dispatch", "investigations",
            "tactical_analytics", "officer_safety", "threat_intel",
            "digital_twin", "predictive_intel", "human_stability",
            "moral_compass", "city_autonomy", "fusion_cloud",
            "emergency_mgmt", "public_guardian", "officer_assist",
            "cyber_intel", "ai_sentinel", "ai_personas",
            "cad_system", "sensor_grid", "communications",
        ]
        for subsystem in subsystems:
            self.subsystem_handlers[subsystem] = self._default_handler

    async def _default_handler(
        self, action: OrchestrationAction
    ) -> OrchestrationResult:
        """Default handler for subsystem actions."""
        return OrchestrationResult(
            workflow_id=action.parameters.get("workflow_id", ""),
            action_id=action.action_id,
            success=True,
            data={"message": f"Action {action.action_type.value} executed on {action.target_subsystem}"},
            execution_time_ms=10.0,
        )

    def start(self) -> bool:
        """Start the orchestration kernel."""
        if self.status == OrchestrationStatus.RUNNING:
            return True
        self.status = OrchestrationStatus.INITIALIZING
        self.status = OrchestrationStatus.RUNNING
        return True

    def stop(self) -> bool:
        """Stop the orchestration kernel."""
        self.status = OrchestrationStatus.STOPPING
        self.status = OrchestrationStatus.STOPPED
        return True

    def pause(self) -> bool:
        """Pause the orchestration kernel."""
        if self.status == OrchestrationStatus.RUNNING:
            self.status = OrchestrationStatus.PAUSED
            return True
        return False

    def resume(self) -> bool:
        """Resume the orchestration kernel."""
        if self.status == OrchestrationStatus.PAUSED:
            self.status = OrchestrationStatus.RUNNING
            return True
        return False

    def register_subsystem_handler(
        self, subsystem: str, handler: Callable
    ) -> bool:
        """Register a handler for a subsystem."""
        self.subsystem_handlers[subsystem] = handler
        return True

    def create_action(
        self,
        action_type: ActionType,
        target_subsystem: str,
        parameters: Dict[str, Any] = None,
        priority: int = 5,
        timeout_seconds: int = 30,
        requires_confirmation: bool = False,
        guardrail_checks: List[str] = None,
    ) -> OrchestrationAction:
        """Create a new orchestration action."""
        action = OrchestrationAction(
            action_type=action_type,
            target_subsystem=target_subsystem,
            parameters=parameters or {},
            priority=priority,
            timeout_seconds=timeout_seconds,
            requires_confirmation=requires_confirmation,
            guardrail_checks=guardrail_checks or [],
        )
        return action

    def queue_action(self, action: OrchestrationAction) -> bool:
        """Add an action to the execution queue."""
        self.action_queue.append(action)
        self.action_queue.sort(key=lambda a: a.priority, reverse=True)
        return True

    async def execute_action(
        self, action: OrchestrationAction
    ) -> OrchestrationResult:
        """Execute a single orchestration action."""
        start_time = datetime.utcnow()
        action.executed_at = start_time
        action.status = "executing"

        try:
            handler = self.subsystem_handlers.get(
                action.target_subsystem, self._default_handler
            )
            result = await handler(action)

            action.completed_at = datetime.utcnow()
            action.status = "completed" if result.success else "failed"
            action.result = result.data
            
            if not result.success:
                action.error = "; ".join(result.errors)

            self.execution_stats["total_actions"] += 1
            if result.success:
                self.execution_stats["successful_actions"] += 1
            else:
                self.execution_stats["failed_actions"] += 1

            self.action_history.append(action)
            return result

        except Exception as e:
            action.completed_at = datetime.utcnow()
            action.status = "error"
            action.error = str(e)
            self.execution_stats["total_actions"] += 1
            self.execution_stats["failed_actions"] += 1
            self.action_history.append(action)

            return OrchestrationResult(
                action_id=action.action_id,
                success=False,
                errors=[str(e)],
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            )

    def execute_action_sync(
        self, action: OrchestrationAction
    ) -> OrchestrationResult:
        """Execute an action synchronously."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.execute_action(action))
        finally:
            loop.close()

    async def execute_workflow(
        self, workflow_id: str, actions: List[OrchestrationAction]
    ) -> List[OrchestrationResult]:
        """Execute a sequence of actions as a workflow."""
        results = []
        self.active_workflows[workflow_id] = {
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "actions_total": len(actions),
            "actions_completed": 0,
        }
        self.execution_stats["total_workflows"] += 1
        self.execution_stats["active_workflows"] += 1

        for action in actions:
            action.parameters["workflow_id"] = workflow_id
            result = await self.execute_action(action)
            results.append(result)
            self.active_workflows[workflow_id]["actions_completed"] += 1

            if not result.success and action.retry_count < action.max_retries:
                action.retry_count += 1
                retry_result = await self.execute_action(action)
                results.append(retry_result)

        self.active_workflows[workflow_id]["status"] = "completed"
        self.active_workflows[workflow_id]["completed_at"] = datetime.utcnow().isoformat()
        self.execution_stats["active_workflows"] -= 1

        return results

    def register_workflow(
        self, workflow_id: str, workflow_config: Dict[str, Any]
    ) -> bool:
        """Register a workflow configuration."""
        self.active_workflows[workflow_id] = {
            "config": workflow_config,
            "status": "registered",
            "registered_at": datetime.utcnow().isoformat(),
        }
        return True

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow."""
        return self.active_workflows.get(workflow_id)

    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows."""
        return [
            {"workflow_id": wid, **wdata}
            for wid, wdata in self.active_workflows.items()
            if wdata.get("status") == "running"
        ]

    def get_action_history(
        self, limit: int = 100, subsystem: str = None
    ) -> List[Dict[str, Any]]:
        """Get action execution history."""
        history = self.action_history[-limit:]
        if subsystem:
            history = [a for a in history if a.target_subsystem == subsystem]
        return [a.to_dict() for a in history]

    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestration statistics."""
        return {
            **self.execution_stats,
            "status": self.status.value,
            "queued_actions": len(self.action_queue),
            "registered_subsystems": len(self.subsystem_handlers),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_subsystems(self) -> List[str]:
        """Get list of registered subsystems."""
        return list(self.subsystem_handlers.keys())

    def clear_queue(self) -> int:
        """Clear the action queue."""
        count = len(self.action_queue)
        self.action_queue.clear()
        return count

    def get_queue(self) -> List[Dict[str, Any]]:
        """Get current action queue."""
        return [a.to_dict() for a in self.action_queue]

    async def process_queue(self) -> List[OrchestrationResult]:
        """Process all actions in the queue."""
        results = []
        while self.action_queue:
            action = self.action_queue.pop(0)
            result = await self.execute_action(action)
            results.append(result)
        return results
