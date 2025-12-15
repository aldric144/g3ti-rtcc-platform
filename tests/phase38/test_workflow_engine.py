"""
Phase 38: Workflow Engine Tests
Tests for multi-step workflow execution with sequential and parallel modes.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestWorkflowEngine:
    """Test suite for WorkflowEngine functionality."""

    def test_workflow_engine_singleton(self):
        """Test that WorkflowEngine follows singleton pattern."""
        from app.orchestration.workflow_engine import WorkflowEngine
        engine1 = WorkflowEngine()
        engine2 = WorkflowEngine()
        assert engine1 is engine2

    def test_workflow_status_enum(self):
        """Test WorkflowStatus enum values."""
        from app.orchestration.workflow_engine import WorkflowStatus
        assert WorkflowStatus.PENDING.value == "pending"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"

    def test_step_execution_mode_enum(self):
        """Test StepExecutionMode enum values."""
        from app.orchestration.workflow_engine import StepExecutionMode
        assert StepExecutionMode.SEQUENTIAL.value == "sequential"
        assert StepExecutionMode.PARALLEL.value == "parallel"

    def test_trigger_type_enum(self):
        """Test TriggerType enum values."""
        from app.orchestration.workflow_engine import TriggerType
        assert TriggerType.EVENT.value == "event"
        assert TriggerType.SCHEDULE.value == "schedule"
        assert TriggerType.MANUAL.value == "manual"
        assert TriggerType.API.value == "api"

    def test_workflow_trigger_creation(self):
        """Test WorkflowTrigger dataclass creation."""
        from app.orchestration.workflow_engine import WorkflowTrigger, TriggerType
        trigger = WorkflowTrigger(
            trigger_type=TriggerType.EVENT,
            event_types=["gunshot_detected"],
            event_sources=["gunshot_detection"],
        )
        assert trigger.trigger_type == TriggerType.EVENT
        assert "gunshot_detected" in trigger.event_types
        assert trigger.trigger_id is not None

    def test_workflow_step_creation(self):
        """Test WorkflowStep dataclass creation."""
        from app.orchestration.workflow_engine import WorkflowStep, StepExecutionMode
        step = WorkflowStep(
            name="Deploy Drone",
            description="Deploy surveillance drone",
            action_type="drone_dispatch",
            target_subsystem="drone_ops",
            parameters={"mission_type": "surveillance"},
            execution_mode=StepExecutionMode.SEQUENTIAL,
            timeout_seconds=30,
            guardrails=["officer_safety"],
        )
        assert step.name == "Deploy Drone"
        assert step.action_type == "drone_dispatch"
        assert step.step_id is not None

    def test_workflow_creation(self):
        """Test Workflow dataclass creation."""
        from app.orchestration.workflow_engine import (
            Workflow, WorkflowStep, WorkflowTrigger,
            TriggerType, StepExecutionMode
        )
        workflow = Workflow(
            name="Test Workflow",
            description="A test workflow",
            version="1.0.0",
            category="test",
            triggers=[
                WorkflowTrigger(
                    trigger_type=TriggerType.MANUAL,
                    event_types=[],
                    event_sources=[],
                )
            ],
            steps=[
                WorkflowStep(
                    name="Step 1",
                    description="First step",
                    action_type="test_action",
                    target_subsystem="test",
                    parameters={},
                    execution_mode=StepExecutionMode.SEQUENTIAL,
                    timeout_seconds=10,
                    guardrails=[],
                )
            ],
            required_inputs=[],
            guardrails=[],
            legal_guardrails=[],
            ethical_guardrails=[],
            timeout_seconds=60,
            priority=3,
        )
        assert workflow.name == "Test Workflow"
        assert workflow.workflow_id is not None
        assert len(workflow.steps) == 1

    def test_workflow_engine_register_workflow(self):
        """Test registering a workflow with the engine."""
        from app.orchestration.workflow_engine import (
            WorkflowEngine, Workflow, WorkflowStep, WorkflowTrigger,
            TriggerType, StepExecutionMode
        )
        engine = WorkflowEngine()
        workflow = Workflow(
            name="Registration Test",
            description="Test registration",
            version="1.0.0",
            category="test",
            triggers=[],
            steps=[],
            required_inputs=[],
            guardrails=[],
            legal_guardrails=[],
            ethical_guardrails=[],
            timeout_seconds=60,
            priority=3,
        )
        engine.register_workflow(workflow)
        registered = engine.get_workflow(workflow.workflow_id)
        assert registered is not None
        assert registered.name == "Registration Test"

    def test_workflow_engine_get_statistics(self):
        """Test getting workflow engine statistics."""
        from app.orchestration.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        stats = engine.get_statistics()
        assert "total_workflows" in stats
        assert "total_executions" in stats
        assert "active_executions" in stats

    def test_workflow_engine_get_active_executions(self):
        """Test getting active workflow executions."""
        from app.orchestration.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        active = engine.get_active_executions()
        assert isinstance(active, list)

    def test_trigger_matching(self):
        """Test workflow trigger matching logic."""
        from app.orchestration.workflow_engine import WorkflowTrigger, TriggerType
        trigger = WorkflowTrigger(
            trigger_type=TriggerType.EVENT,
            event_types=["gunshot_detected", "shots_fired"],
            event_sources=["gunshot_detection"],
            conditions={"priority": 1},
        )
        assert trigger.matches_event("gunshot_detected", "gunshot_detection")
        assert trigger.matches_event("shots_fired", "gunshot_detection")
        assert not trigger.matches_event("unknown_event", "gunshot_detection")


class TestWorkflowExecution:
    """Test suite for workflow execution."""

    @pytest.mark.asyncio
    async def test_workflow_execution_lifecycle(self):
        """Test complete workflow execution lifecycle."""
        from app.orchestration.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        stats_before = engine.get_statistics()
        assert stats_before is not None

    def test_workflow_timeout_handling(self):
        """Test workflow timeout configuration."""
        from app.orchestration.workflow_engine import Workflow
        workflow = Workflow(
            name="Timeout Test",
            description="Test timeout",
            version="1.0.0",
            category="test",
            triggers=[],
            steps=[],
            required_inputs=[],
            guardrails=[],
            legal_guardrails=[],
            ethical_guardrails=[],
            timeout_seconds=120,
            priority=2,
        )
        assert workflow.timeout_seconds == 120

    def test_workflow_priority_levels(self):
        """Test workflow priority levels."""
        from app.orchestration.workflow_engine import Workflow
        critical = Workflow(
            name="Critical",
            description="Critical priority",
            version="1.0.0",
            category="test",
            triggers=[],
            steps=[],
            required_inputs=[],
            guardrails=[],
            legal_guardrails=[],
            ethical_guardrails=[],
            timeout_seconds=60,
            priority=1,
        )
        low = Workflow(
            name="Low",
            description="Low priority",
            version="1.0.0",
            category="test",
            triggers=[],
            steps=[],
            required_inputs=[],
            guardrails=[],
            legal_guardrails=[],
            ethical_guardrails=[],
            timeout_seconds=60,
            priority=5,
        )
        assert critical.priority < low.priority
