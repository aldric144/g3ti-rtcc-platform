"""Tests for Resource Assignment & Deployment Manager."""


import pytest

from app.command.resources import (
    ResourceManager,
    ResourceStatus,
    ResourceType,
)


class TestResourceManager:
    """Test cases for ResourceManager."""

    @pytest.fixture
    def manager(self):
        """Create a ResourceManager instance."""
        return ResourceManager()

    @pytest.mark.asyncio
    async def test_register_resource(self, manager):
        """Test registering a new resource."""
        resource = await manager.register_resource(
            name="Alpha-11",
            resource_type=ResourceType.PATROL_UNIT,
            agency="Atlanta PD",
            call_sign="A-11",
            capabilities=["patrol", "traffic"],
        )

        assert resource is not None
        assert resource.name == "Alpha-11"
        assert resource.resource_type == ResourceType.PATROL_UNIT
        assert resource.status == ResourceStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_assign_resource(self, manager):
        """Test assigning a resource to an incident."""
        resource = await manager.register_resource(
            name="SWAT-01",
            resource_type=ResourceType.SWAT,
            agency="Atlanta PD",
            call_sign="SWAT-1",
            capabilities=["tactical", "entry"],
        )

        assignment = await manager.assign_resource(
            incident_id="inc-001",
            resource_id=resource.id,
            role="entry_team",
            assigned_by="commander-001",
        )

        assert assignment is not None
        assert assignment.resource_id == resource.id
        assert assignment.incident_id == "inc-001"
        assert assignment.role == "entry_team"

    @pytest.mark.asyncio
    async def test_release_resource(self, manager):
        """Test releasing a resource from an incident."""
        resource = await manager.register_resource(
            name="K9-01",
            resource_type=ResourceType.K9,
            agency="Atlanta PD",
            call_sign="K9-1",
            capabilities=["tracking", "detection"],
        )

        await manager.assign_resource(
            incident_id="inc-001",
            resource_id=resource.id,
            role="tracking",
            assigned_by="commander-001",
        )

        result = await manager.release_resource(
            incident_id="inc-001",
            resource_id=resource.id,
            released_by="commander-001",
            reason="Task complete",
        )

        assert result is True

        # Verify resource is available again
        updated = await manager.get_resource(resource.id)
        assert updated.status == ResourceStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_get_incident_resources(self, manager):
        """Test getting all resources assigned to an incident."""
        incident_id = "inc-002"

        # Register and assign multiple resources
        r1 = await manager.register_resource(
            name="Unit-1",
            resource_type=ResourceType.PATROL_UNIT,
            agency="Atlanta PD",
            call_sign="U-1",
            capabilities=["patrol"],
        )
        r2 = await manager.register_resource(
            name="Unit-2",
            resource_type=ResourceType.PATROL_UNIT,
            agency="Atlanta PD",
            call_sign="U-2",
            capabilities=["patrol"],
        )

        await manager.assign_resource(incident_id, r1.id, "perimeter", "cmd-001")
        await manager.assign_resource(incident_id, r2.id, "perimeter", "cmd-001")

        resources = await manager.get_incident_resources(incident_id)

        assert len(resources) >= 2

    @pytest.mark.asyncio
    async def test_get_available_resources(self, manager):
        """Test getting available resources."""
        # Register some resources
        await manager.register_resource(
            name="Available-1",
            resource_type=ResourceType.PATROL_UNIT,
            agency="Atlanta PD",
            call_sign="AV-1",
            capabilities=["patrol"],
        )

        available = await manager.get_available_resources()

        assert len(available) >= 1
        assert all(r.status == ResourceStatus.AVAILABLE for r in available)

    @pytest.mark.asyncio
    async def test_update_resource_status(self, manager):
        """Test updating resource status."""
        resource = await manager.register_resource(
            name="EMS-01",
            resource_type=ResourceType.EMS,
            agency="County EMS",
            call_sign="M-01",
            capabilities=["medical", "transport"],
        )

        updated = await manager.update_resource_status(
            resource_id=resource.id,
            status=ResourceStatus.EN_ROUTE,
            updated_by="dispatch-001",
        )

        assert updated.status == ResourceStatus.EN_ROUTE

    @pytest.mark.asyncio
    async def test_resource_types(self, manager):
        """Test all resource types can be registered."""
        for i, resource_type in enumerate(ResourceType):
            resource = await manager.register_resource(
                name=f"Resource-{i}",
                resource_type=resource_type,
                agency="Test Agency",
                call_sign=f"R-{i}",
                capabilities=["test"],
            )
            assert resource.resource_type == resource_type

    @pytest.mark.asyncio
    async def test_update_resource_location(self, manager):
        """Test updating resource location."""
        resource = await manager.register_resource(
            name="Mobile-01",
            resource_type=ResourceType.PATROL_UNIT,
            agency="Atlanta PD",
            call_sign="MOB-1",
            capabilities=["patrol"],
        )

        updated = await manager.update_resource_location(
            resource_id=resource.id,
            latitude=33.7490,
            longitude=-84.3880,
        )

        assert updated.latitude == 33.7490
        assert updated.longitude == -84.3880

    @pytest.mark.asyncio
    async def test_mark_resource_arrived(self, manager):
        """Test marking a resource as arrived."""
        resource = await manager.register_resource(
            name="Fire-01",
            resource_type=ResourceType.FIRE,
            agency="Atlanta Fire",
            call_sign="E-01",
            capabilities=["fire", "rescue"],
        )

        await manager.assign_resource(
            incident_id="inc-001",
            resource_id=resource.id,
            role="standby",
            assigned_by="commander-001",
        )

        await manager.update_resource_status(
            resource_id=resource.id,
            status=ResourceStatus.EN_ROUTE,
            updated_by="dispatch-001",
        )

        arrived = await manager.mark_resource_arrived(
            incident_id="inc-001",
            resource_id=resource.id,
        )

        assert arrived.status == ResourceStatus.ON_SCENE
        assert arrived.arrived_at is not None

    @pytest.mark.asyncio
    async def test_get_resources_by_agency(self, manager):
        """Test getting resources by agency."""
        await manager.register_resource(
            name="APD-01",
            resource_type=ResourceType.PATROL_UNIT,
            agency="Atlanta PD",
            call_sign="APD-1",
            capabilities=["patrol"],
        )
        await manager.register_resource(
            name="EMS-01",
            resource_type=ResourceType.EMS,
            agency="County EMS",
            call_sign="EMS-1",
            capabilities=["medical"],
        )

        apd_resources = await manager.get_resources_by_agency("Atlanta PD")
        ems_resources = await manager.get_resources_by_agency("County EMS")

        assert len(apd_resources) >= 1
        assert all(r.agency == "Atlanta PD" for r in apd_resources)
        assert len(ems_resources) >= 1
        assert all(r.agency == "County EMS" for r in ems_resources)
