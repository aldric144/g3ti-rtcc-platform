"""
Phase 38: Resource Manager Tests
Tests for resource allocation, scheduling, and management.
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))


class TestResourceManager:
    """Test suite for ResourceManager functionality."""

    def test_resource_manager_singleton(self):
        """Test that ResourceManager follows singleton pattern."""
        from app.orchestration.resource_manager import ResourceManager
        manager1 = ResourceManager()
        manager2 = ResourceManager()
        assert manager1 is manager2

    def test_resource_type_enum(self):
        """Test ResourceType enum values."""
        from app.orchestration.resource_manager import ResourceType
        assert ResourceType.DRONE.value == "drone"
        assert ResourceType.ROBOT.value == "robot"
        assert ResourceType.DISPATCH_UNIT.value == "dispatch_unit"
        assert ResourceType.OFFICER.value == "officer"
        assert ResourceType.VEHICLE.value == "vehicle"

    def test_resource_status_enum(self):
        """Test ResourceStatus enum values."""
        from app.orchestration.resource_manager import ResourceStatus
        assert ResourceStatus.AVAILABLE.value == "available"
        assert ResourceStatus.ALLOCATED.value == "allocated"
        assert ResourceStatus.IN_USE.value == "in_use"
        assert ResourceStatus.MAINTENANCE.value == "maintenance"
        assert ResourceStatus.OFFLINE.value == "offline"

    def test_allocation_priority_enum(self):
        """Test AllocationPriority enum values."""
        from app.orchestration.resource_manager import AllocationPriority
        assert AllocationPriority.EMERGENCY.value == 1
        assert AllocationPriority.CRITICAL.value == 2
        assert AllocationPriority.HIGH.value == 3
        assert AllocationPriority.MEDIUM.value == 4
        assert AllocationPriority.LOW.value == 5

    def test_resource_creation(self):
        """Test Resource dataclass creation."""
        from app.orchestration.resource_manager import (
            Resource, ResourceType, ResourceStatus
        )
        resource = Resource(
            resource_type=ResourceType.DRONE,
            name="Drone Alpha",
            description="Surveillance drone",
            status=ResourceStatus.AVAILABLE,
            location={"lat": 26.7753, "lng": -80.0589},
            capabilities=["surveillance", "thermal"],
            health_score=100,
        )
        assert resource.name == "Drone Alpha"
        assert resource.resource_type == ResourceType.DRONE
        assert resource.resource_id is not None

    def test_resource_availability_check(self):
        """Test resource availability checking."""
        from app.orchestration.resource_manager import (
            Resource, ResourceType, ResourceStatus
        )
        available = Resource(
            resource_type=ResourceType.DRONE,
            name="Available Drone",
            description="Test",
            status=ResourceStatus.AVAILABLE,
            location={},
            capabilities=[],
            health_score=100,
        )
        allocated = Resource(
            resource_type=ResourceType.DRONE,
            name="Allocated Drone",
            description="Test",
            status=ResourceStatus.ALLOCATED,
            location={},
            capabilities=[],
            health_score=100,
        )
        assert available.is_available() is True
        assert allocated.is_available() is False

    def test_register_resource(self):
        """Test registering a resource."""
        from app.orchestration.resource_manager import (
            ResourceManager, Resource, ResourceType, ResourceStatus
        )
        manager = ResourceManager()
        resource = Resource(
            resource_type=ResourceType.SENSOR,
            name="Test Sensor",
            description="Test sensor",
            status=ResourceStatus.AVAILABLE,
            location={"lat": 26.7753, "lng": -80.0589},
            capabilities=["motion_detection"],
            health_score=100,
        )
        manager.register_resource(resource)
        all_resources = manager.get_all_resources()
        assert len(all_resources) > 0

    def test_get_available_resources(self):
        """Test getting available resources by type."""
        from app.orchestration.resource_manager import ResourceManager, ResourceType
        manager = ResourceManager()
        available = manager.get_available_resources(ResourceType.DRONE)
        assert isinstance(available, list)

    def test_get_all_resources(self):
        """Test getting all resources."""
        from app.orchestration.resource_manager import ResourceManager
        manager = ResourceManager()
        resources = manager.get_all_resources()
        assert isinstance(resources, list)

    def test_get_statistics(self):
        """Test getting resource manager statistics."""
        from app.orchestration.resource_manager import ResourceManager
        manager = ResourceManager()
        stats = manager.get_statistics()
        assert "total_resources" in stats
        assert "active_allocations" in stats

    def test_get_resource_utilization(self):
        """Test getting resource utilization."""
        from app.orchestration.resource_manager import ResourceManager
        manager = ResourceManager()
        utilization = manager.get_resource_utilization()
        assert isinstance(utilization, dict)


class TestResourceAllocation:
    """Test suite for resource allocation."""

    def test_resource_allocation_creation(self):
        """Test ResourceAllocation dataclass creation."""
        from app.orchestration.resource_manager import (
            ResourceAllocation, ResourceType, AllocationPriority
        )
        allocation = ResourceAllocation(
            resource_id="res-001",
            resource_type=ResourceType.DRONE,
            workflow_id="wf-001",
            requester_id="user-001",
            priority=AllocationPriority.HIGH,
            purpose="Surveillance mission",
            start_time=datetime.utcnow(),
            duration_minutes=60,
        )
        assert allocation.resource_id == "res-001"
        assert allocation.priority == AllocationPriority.HIGH
        assert allocation.allocation_id is not None

    def test_allocate_resource(self):
        """Test allocating a resource."""
        from app.orchestration.resource_manager import (
            ResourceManager, ResourceType, AllocationPriority
        )
        manager = ResourceManager()
        available = manager.get_available_resources(ResourceType.DRONE)
        if available:
            allocation = manager.allocate_resource(
                resource_id=available[0].resource_id,
                workflow_id="test-workflow",
                requester_id="test-user",
                priority=AllocationPriority.MEDIUM,
                purpose="Test allocation",
                duration_minutes=30,
            )
            if allocation:
                assert allocation.workflow_id == "test-workflow"

    def test_release_resource(self):
        """Test releasing an allocated resource."""
        from app.orchestration.resource_manager import ResourceManager
        manager = ResourceManager()
        result = manager.release_resource("nonexistent-resource")
        assert result is False

    def test_get_nearest_resource(self):
        """Test getting nearest resource by location."""
        from app.orchestration.resource_manager import ResourceManager, ResourceType
        manager = ResourceManager()
        nearest = manager.get_nearest_resource(
            ResourceType.DRONE,
            lat=26.7753,
            lng=-80.0589,
        )


class TestDefaultResources:
    """Test suite for default resources."""

    def test_default_resources_registered(self):
        """Test that default resources are registered."""
        from app.orchestration.resource_manager import ResourceManager
        manager = ResourceManager()
        resources = manager.get_all_resources()
        assert len(resources) > 0

    def test_drone_resources_exist(self):
        """Test that drone resources exist."""
        from app.orchestration.resource_manager import ResourceManager, ResourceType
        manager = ResourceManager()
        drones = manager.get_available_resources(ResourceType.DRONE)
        assert isinstance(drones, list)
