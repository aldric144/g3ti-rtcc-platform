"""
Phase 38: End-to-End Orchestration Tests
Tests for complete orchestration flow from event to action.
"""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestE2EOrchestration:
    """Test suite for end-to-end orchestration."""

    def test_complete_orchestration_stack(self):
        """Test that complete orchestration stack is available."""
        from app.orchestration import (
            OrchestrationKernel,
            EventRouter,
            WorkflowEngine,
            PolicyBindingEngine,
            ResourceManager,
        )
        from app.orchestration.event_bus import EventFusionBus
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        kernel = OrchestrationKernel()
        event_router = EventRouter()
        workflow_engine = WorkflowEngine()
        policy_engine = PolicyBindingEngine()
        resource_manager = ResourceManager()
        event_bus = EventFusionBus()
        
        assert kernel is not None
        assert event_router is not None
        assert workflow_engine is not None
        assert policy_engine is not None
        assert resource_manager is not None
        assert event_bus is not None
        assert len(ALL_WORKFLOWS) >= 20

    @pytest.mark.asyncio
    async def test_event_to_workflow_flow(self):
        """Test event ingestion to workflow trigger flow."""
        from app.orchestration.event_bus import EventFusionBus
        from app.orchestration.event_router import EventRouter
        from app.orchestration.workflow_engine import WorkflowEngine
        
        event_bus = EventFusionBus()
        event_router = EventRouter()
        workflow_engine = WorkflowEngine()
        
        event = {
            "event_id": "e2e-001",
            "event_type": "gunshot_detected",
            "location": {"lat": 26.7753, "lng": -80.0589},
            "priority": 1,
        }
        
        result = event_bus.ingest_event("gunshot_detection", event)
        assert result is True
        
        normalized = await event_router.normalize_event("gunshot_detection", event)
        assert normalized is not None

    @pytest.mark.asyncio
    async def test_workflow_to_action_flow(self):
        """Test workflow execution to action dispatch flow."""
        from app.orchestration.workflow_engine import WorkflowEngine
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        from app.orchestration.workflows.gunfire_response import GunfireResponseWorkflow
        
        workflow_engine = WorkflowEngine()
        kernel = OrchestrationKernel()
        
        workflow = GunfireResponseWorkflow
        assert workflow is not None
        assert len(workflow.steps) >= 8
        
        subsystems = kernel.get_subsystems()
        assert len(subsystems) > 0

    @pytest.mark.asyncio
    async def test_policy_check_in_flow(self):
        """Test policy checking in orchestration flow."""
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        from app.orchestration.workflows.gunfire_response import GunfireResponseWorkflow
        
        policy_engine = PolicyBindingEngine()
        workflow = GunfireResponseWorkflow
        
        for step in workflow.steps:
            result = await policy_engine.check_policy(
                workflow_id=workflow.workflow_id,
                action_type=step.action_type,
                parameters=step.parameters,
            )
            assert isinstance(result, list)

    def test_resource_allocation_in_flow(self):
        """Test resource allocation in orchestration flow."""
        from app.orchestration.resource_manager import ResourceManager, ResourceType
        from app.orchestration.workflows.gunfire_response import GunfireResponseWorkflow
        
        resource_manager = ResourceManager()
        workflow = GunfireResponseWorkflow
        
        drone_steps = [s for s in workflow.steps if "drone" in s.action_type.lower()]
        if drone_steps:
            available = resource_manager.get_available_resources(ResourceType.DRONE)
            assert isinstance(available, list)


class TestE2EScenarios:
    """Test suite for end-to-end scenarios."""

    @pytest.mark.asyncio
    async def test_gunfire_response_scenario(self):
        """Test complete gunfire response scenario."""
        from app.orchestration.event_bus import EventFusionBus
        from app.orchestration.workflows.gunfire_response import GunfireResponseWorkflow
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        
        event_bus = EventFusionBus()
        policy_engine = PolicyBindingEngine()
        workflow = GunfireResponseWorkflow
        
        event = {
            "event_id": "gunfire-e2e",
            "event_type": "gunshot_detected",
            "location": {"lat": 26.7753, "lng": -80.0589},
            "confidence": 0.95,
        }
        event_bus.ingest_event("gunshot_detection", event)
        
        assert workflow.priority == 1
        assert len(workflow.steps) >= 8
        
        for step in workflow.steps[:3]:
            result = await policy_engine.check_policy(
                workflow_id=workflow.workflow_id,
                action_type=step.action_type,
                parameters={},
            )
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_officer_distress_scenario(self):
        """Test complete officer distress scenario."""
        from app.orchestration.event_bus import EventFusionBus
        from app.orchestration.workflows.officer_distress import OfficerDistressWorkflow
        from app.orchestration.resource_manager import ResourceManager, ResourceType
        
        event_bus = EventFusionBus()
        resource_manager = ResourceManager()
        workflow = OfficerDistressWorkflow
        
        event = {
            "event_id": "distress-e2e",
            "event_type": "officer_distress",
            "officer_id": "officer-001",
            "location": {"lat": 26.7753, "lng": -80.0589},
        }
        event_bus.ingest_event("officer_safety", event)
        
        assert workflow.priority == 1
        
        drones = resource_manager.get_available_resources(ResourceType.DRONE)
        assert isinstance(drones, list)

    @pytest.mark.asyncio
    async def test_amber_alert_scenario(self):
        """Test complete Amber Alert scenario."""
        from app.orchestration.event_bus import EventFusionBus
        from app.orchestration.workflows.amber_alert import AmberAlertWorkflow
        
        event_bus = EventFusionBus()
        workflow = AmberAlertWorkflow
        
        event = {
            "event_id": "amber-e2e",
            "event_type": "amber_alert",
            "child_description": "Test child",
            "last_seen_location": {"lat": 26.7753, "lng": -80.0589},
        }
        event_bus.ingest_event("dispatch", event)
        
        assert workflow.priority == 1
        assert len(workflow.steps) >= 8


class TestE2EIntegration:
    """Test suite for end-to-end integration."""

    def test_all_components_initialized(self):
        """Test that all components are properly initialized."""
        from app.orchestration import (
            OrchestrationKernel,
            EventRouter,
            WorkflowEngine,
            PolicyBindingEngine,
            ResourceManager,
        )
        
        kernel = OrchestrationKernel()
        assert kernel.get_statistics() is not None
        
        router = EventRouter()
        assert router.get_statistics() is not None
        
        engine = WorkflowEngine()
        assert engine.get_statistics() is not None
        
        policy = PolicyBindingEngine()
        assert policy.get_statistics() is not None
        
        resources = ResourceManager()
        assert resources.get_statistics() is not None

    def test_all_workflows_loadable(self):
        """Test that all workflows are loadable."""
        from app.orchestration.workflows import ALL_WORKFLOWS
        
        for workflow in ALL_WORKFLOWS:
            assert workflow.workflow_id is not None
            assert workflow.name is not None
            assert len(workflow.steps) >= 1
            assert len(workflow.triggers) >= 1

    def test_default_configurations_valid(self):
        """Test that default configurations are valid."""
        from app.orchestration.event_router import EventRouter
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        from app.orchestration.resource_manager import ResourceManager
        
        router = EventRouter()
        assert len(router.get_routing_rules()) > 0
        assert len(router.get_channels()) > 0
        
        policy = PolicyBindingEngine()
        assert len(policy.get_policy_bindings()) > 0
        
        resources = ResourceManager()
        assert len(resources.get_all_resources()) > 0


class TestE2EAudit:
    """Test suite for end-to-end audit trail."""

    def test_audit_trail_completeness(self):
        """Test audit trail completeness."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        from app.orchestration.policy_binding_engine import PolicyBindingEngine
        
        kernel = OrchestrationKernel()
        policy = PolicyBindingEngine()
        
        action_history = kernel.get_action_history(limit=100)
        assert isinstance(action_history, list)
        
        policy_history = policy.get_check_history(limit=100)
        assert isinstance(policy_history, list)

    def test_statistics_accuracy(self):
        """Test statistics accuracy."""
        from app.orchestration.orchestration_kernel import OrchestrationKernel
        from app.orchestration.event_bus import EventFusionBus
        
        kernel = OrchestrationKernel()
        bus = EventFusionBus()
        
        kernel_stats = kernel.get_statistics()
        bus_stats = bus.get_statistics()
        
        assert "total_actions_executed" in kernel_stats
        assert "total_events_received" in bus_stats
