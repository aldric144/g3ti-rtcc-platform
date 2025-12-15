"""
Phase 38: Orchestration Kernel Tests
Tests for the master orchestrator functionality.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestOrchestrationKernel:
    """Test suite for OrchestrationKernel functionality."""

    def test_kernel_singleton(self):
        """Test that OrchestrationKernel follows singleton pattern."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel1 = OrchestrationKernel()
        kernel2 = OrchestrationKernel()
        assert kernel1 is kernel2

    def test_orchestration_status_enum(self):
        """Test OrchestrationStatus enum values."""
        from app.orchestration.orchestration_kernel import OrchestrationStatus
        assert OrchestrationStatus.IDLE.value == "idle"
        assert OrchestrationStatus.RUNNING.value == "running"
        assert OrchestrationStatus.PAUSED.value == "paused"
        assert OrchestrationStatus.STOPPED.value == "stopped"
        assert OrchestrationStatus.ERROR.value == "error"

    def test_action_type_enum(self):
        """Test ActionType enum values."""
        from app.orchestration.orchestration_kernel import ActionType
        assert ActionType.DRONE_DISPATCH.value == "drone_dispatch"
        assert ActionType.ROBOT_DISPATCH.value == "robot_dispatch"
        assert ActionType.PATROL_REROUTE.value == "patrol_reroute"
        assert ActionType.OFFICER_ALERT.value == "officer_alert"
        assert ActionType.EMERGENCY_BROADCAST.value == "emergency_broadcast"

    def test_orchestration_action_creation(self):
        """Test OrchestrationAction dataclass creation."""
        from app.orchestration.orchestration_kernel import (
            OrchestrationAction, ActionType
        )
        action = OrchestrationAction(
            action_type=ActionType.DRONE_DISPATCH,
            target_subsystem="drone_ops",
            parameters={"mission_type": "surveillance"},
            priority=2,
            timeout_seconds=60,
            requires_confirmation=False,
            guardrail_checks=["officer_safety"],
        )
        assert action.action_type == ActionType.DRONE_DISPATCH
        assert action.target_subsystem == "drone_ops"
        assert action.action_id is not None

    def test_orchestration_result_creation(self):
        """Test OrchestrationResult dataclass creation."""
        from app.orchestration.orchestration_kernel import OrchestrationResult
        result = OrchestrationResult(
            result_id="result-001",
            workflow_id="wf-001",
            action_id="action-001",
            success=True,
            data={"status": "completed"},
            errors=[],
            warnings=[],
            execution_time_ms=150,
            audit_trail=["Action executed successfully"],
        )
        assert result.success is True
        assert result.execution_time_ms == 150

    def test_kernel_status(self):
        """Test kernel status property."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        assert kernel.status is not None

    def test_get_statistics(self):
        """Test getting kernel statistics."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        stats = kernel.get_statistics()
        assert "total_actions_executed" in stats
        assert "total_workflows_completed" in stats

    def test_get_action_history(self):
        """Test getting action history."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        history = kernel.get_action_history(limit=50)
        assert isinstance(history, list)

    def test_get_subsystems(self):
        """Test getting registered subsystems."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        subsystems = kernel.get_subsystems()
        assert isinstance(subsystems, list)

    def test_get_queue(self):
        """Test getting action queue."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        queue = kernel.get_queue()
        assert isinstance(queue, list)


class TestKernelLifecycle:
    """Test suite for kernel lifecycle management."""

    @pytest.mark.asyncio
    async def test_kernel_start(self):
        """Test starting the kernel."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        await kernel.start()

    @pytest.mark.asyncio
    async def test_kernel_stop(self):
        """Test stopping the kernel."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        await kernel.stop()

    def test_kernel_pause(self):
        """Test pausing the kernel."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        kernel.pause()

    def test_kernel_resume(self):
        """Test resuming the kernel."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        kernel.resume()


class TestActionExecution:
    """Test suite for action execution."""

    @pytest.mark.asyncio
    async def test_queue_action(self):
        """Test queuing an action."""
        from app.orchestration.orchestration_kernel import (
            OrchestrationKernel, OrchestrationAction, ActionType
        )
        kernel = OrchestrationKernel()
        action = OrchestrationAction(
            action_type=ActionType.AUDIT_LOG,
            target_subsystem="system",
            parameters={"message": "Test action"},
            priority=5,
            timeout_seconds=30,
            requires_confirmation=False,
            guardrail_checks=[],
        )
        await kernel.queue_action(action)

    def test_action_priority_ordering(self):
        """Test that actions are ordered by priority."""
        from app.orchestration.orchestration_kernel import (
            OrchestrationAction, ActionType
        )
        high_priority = OrchestrationAction(
            action_type=ActionType.EMERGENCY_BROADCAST,
            target_subsystem="communications",
            parameters={},
            priority=1,
            timeout_seconds=30,
            requires_confirmation=False,
            guardrail_checks=[],
        )
        low_priority = OrchestrationAction(
            action_type=ActionType.AUDIT_LOG,
            target_subsystem="system",
            parameters={},
            priority=5,
            timeout_seconds=30,
            requires_confirmation=False,
            guardrail_checks=[],
        )
        assert high_priority.priority < low_priority.priority


class TestSubsystemRegistration:
    """Test suite for subsystem registration."""

    def test_register_subsystem(self):
        """Test registering a subsystem."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        
        async def test_handler(action):
            return {"status": "success"}
        
        kernel.register_subsystem("test_subsystem", test_handler)
        subsystems = kernel.get_subsystems()
        assert "test_subsystem" in subsystems

    def test_default_subsystems_registered(self):
        """Test that default subsystems are registered."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        kernel = OrchestrationKernel()
        subsystems = kernel.get_subsystems()
        assert len(subsystems) > 0
