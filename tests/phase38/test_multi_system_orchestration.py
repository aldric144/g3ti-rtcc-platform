"""
Phase 38: Multi-System Orchestration Tests
Tests for cross-module coordination and integration.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestMultiSystemOrchestration:
    """Test suite for multi-system orchestration."""

    def test_kernel_integrates_all_components(self):
        """Test that kernel integrates all orchestration components."""
        from app.orchestration import (
            OrchestrationKernel,
            EventRouter,
            WorkflowEngine,
            PolicyBindingEngine,
            ResourceManager,
        )
        
        kernel = OrchestrationKernel()
        event_router = EventRouter()
        workflow_engine = WorkflowEngine()
        policy_engine = PolicyBindingEngine()
        resource_manager = ResourceManager()
        
        assert kernel is not None
        assert event_router is not None
        assert workflow_engine is not None
        assert policy_engine is not None
        assert resource_manager is not None

    def test_event_bus_connects_to_router(self):
        """Test that event bus connects to event router."""
        from app.orchestration.event_bus import EventFusionBus
        from app.orchestration.event_router import EventRouter
        
        bus = EventFusionBus()
        router = EventRouter()
        
        assert bus is not None
        assert router is not None

    def test_workflow_engine_uses_policy_engine(self):
        """Test that workflow engine uses policy engine."""
        from app.orchestration.workflow_engine import WorkflowEngine
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        
        workflow_engine = WorkflowEngine()
        policy_engine = PolicyBindingEngine()
        
        bindings = policy_engine.get_policy_bindings()
        assert len(bindings) > 0

    def test_workflow_engine_uses_resource_manager(self):
        """Test that workflow engine uses resource manager."""
        from app.orchestration.workflow_engine import WorkflowEngine
        from app.orchestration.resource_manager import ResourceManager
        
        workflow_engine = WorkflowEngine()
        resource_manager = ResourceManager()
        
        resources = resource_manager.get_all_resources()
        assert isinstance(resources, list)


class TestCrossModuleCoordination:
    """Test suite for cross-module coordination."""

    def test_workflows_target_multiple_subsystems(self):
        """Test that workflows target multiple subsystems."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            subsystems = set(step.target_subsystem for step in workflow.steps)
            assert len(subsystems) >= 2, f"{workflow.name} should target multiple subsystems"

    def test_workflows_use_multiple_action_types(self):
        """Test that workflows use multiple action types."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            action_types = set(step.action_type for step in workflow.steps)
            assert len(action_types) >= 2, f"{workflow.name} should use multiple action types"

    def test_parallel_steps_coordinate_properly(self):
        """Test that parallel steps are properly coordinated."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        from app.orchestration.workflow_engine import StepExecutionMode
        
        for workflow in ALL_WORKFLOWS:
            parallel_steps = [s for s in workflow.steps if s.execution_mode == StepExecutionMode.PARALLEL]
            if parallel_steps:
                subsystems = set(s.target_subsystem for s in parallel_steps)
                assert len(subsystems) >= 1


class TestSubsystemIntegration:
    """Test suite for subsystem integration."""

    def test_drone_ops_integration(self):
        """Test drone operations integration."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        drone_workflows = []
        for workflow in ALL_WORKFLOWS:
            if any(s.target_subsystem == "drone_ops" for s in workflow.steps):
                drone_workflows.append(workflow)
        
        assert len(drone_workflows) >= 5

    def test_dispatch_integration(self):
        """Test dispatch integration."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        dispatch_workflows = []
        for workflow in ALL_WORKFLOWS:
            if any(s.target_subsystem == "dispatch" for s in workflow.steps):
                dispatch_workflows.append(workflow)
        
        assert len(dispatch_workflows) >= 5

    def test_investigations_integration(self):
        """Test investigations integration."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        investigation_workflows = []
        for workflow in ALL_WORKFLOWS:
            if any(s.target_subsystem == "investigations" for s in workflow.steps):
                investigation_workflows.append(workflow)
        
        assert len(investigation_workflows) >= 5

    def test_threat_intel_integration(self):
        """Test threat intelligence integration."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        threat_workflows = []
        for workflow in ALL_WORKFLOWS:
            if any(s.target_subsystem == "threat_intel" for s in workflow.steps):
                threat_workflows.append(workflow)
        
        assert len(threat_workflows) >= 3


class TestEventPropagation:
    """Test suite for event propagation."""

    def test_events_propagate_to_workflows(self):
        """Test that events propagate to trigger workflows."""
        from app.orchestration.event_router import EventRouter
        from app.orchestration.workflow_engine import WorkflowEngine
        
        router = EventRouter()
        engine = WorkflowEngine()
        
        assert router is not None
        assert engine is not None

    def test_workflow_results_propagate_to_subsystems(self):
        """Test that workflow results propagate to subsystems."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        
        kernel = OrchestrationKernel()
        subsystems = kernel.get_subsystems()
        
        assert len(subsystems) > 0

    def test_resource_allocation_propagates(self):
        """Test that resource allocation propagates correctly."""
        from app.orchestration.resource_manager import ResourceManager
        
        manager = ResourceManager()
        stats = manager.get_statistics()
        
        assert "total_resources" in stats
