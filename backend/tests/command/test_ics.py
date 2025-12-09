"""Tests for ICS Automation Engine."""


import pytest

from app.command.ics import (
    ICSChecklistItem,
    ICSManager,
    ICSRole,
    ICSSection,
)


class TestICSManager:
    """Test cases for ICSManager."""

    @pytest.fixture
    def manager(self):
        """Create an ICSManager instance."""
        return ICSManager()

    @pytest.mark.asyncio
    async def test_assign_role(self, manager):
        """Test assigning an ICS role."""
        assignment = await manager.assign_role(
            incident_id="inc-001",
            role=ICSRole.INCIDENT_COMMANDER,
            badge="CMD-001",
            name="Captain Rodriguez",
            assigned_by="admin-001",
        )

        assert assignment is not None
        assert assignment.role == ICSRole.INCIDENT_COMMANDER
        assert assignment.badge == "CMD-001"
        assert assignment.name == "Captain Rodriguez"
        assert assignment.assigned_at is not None

    @pytest.mark.asyncio
    async def test_reassign_role(self, manager):
        """Test reassigning an ICS role."""
        # First assignment
        await manager.assign_role(
            incident_id="inc-001",
            role=ICSRole.OPERATIONS_CHIEF,
            badge="OPS-001",
            name="Sergeant Thompson",
            assigned_by="admin-001",
        )

        # Reassignment
        reassignment = await manager.reassign_role(
            incident_id="inc-001",
            role=ICSRole.OPERATIONS_CHIEF,
            new_badge="OPS-002",
            new_name="Sergeant Williams",
            reassigned_by="commander-001",
            reason="Shift change",
        )

        assert reassignment is not None
        assert reassignment.badge == "OPS-002"
        assert reassignment.name == "Sergeant Williams"

    @pytest.mark.asyncio
    async def test_get_ics_structure(self, manager):
        """Test getting the ICS structure for an incident."""
        incident_id = "inc-002"

        # Assign multiple roles
        await manager.assign_role(
            incident_id=incident_id,
            role=ICSRole.INCIDENT_COMMANDER,
            badge="CMD-001",
            name="Captain Rodriguez",
            assigned_by="admin-001",
        )
        await manager.assign_role(
            incident_id=incident_id,
            role=ICSRole.OPERATIONS_CHIEF,
            badge="OPS-001",
            name="Sergeant Thompson",
            assigned_by="admin-001",
        )
        await manager.assign_role(
            incident_id=incident_id,
            role=ICSRole.PLANNING_CHIEF,
            badge="PLN-001",
            name="Detective Harris",
            assigned_by="admin-001",
        )

        structure = await manager.get_ics_structure(incident_id)

        assert structure is not None
        assert len(structure.assignments) >= 3
        assert any(a.role == ICSRole.INCIDENT_COMMANDER for a in structure.assignments)

    @pytest.mark.asyncio
    async def test_all_ics_roles(self, manager):
        """Test that all ICS roles can be assigned."""
        incident_id = "inc-003"

        for i, role in enumerate(ICSRole):
            assignment = await manager.assign_role(
                incident_id=incident_id,
                role=role,
                badge=f"BADGE-{i:03d}",
                name=f"Officer {i}",
                assigned_by="admin-001",
            )
            assert assignment.role == role

    @pytest.mark.asyncio
    async def test_get_role_checklist(self, manager):
        """Test getting the checklist for an ICS role."""
        checklist = await manager.get_role_checklist(
            incident_id="inc-001",
            role=ICSRole.INCIDENT_COMMANDER,
            incident_type="active_shooter",
        )

        assert checklist is not None
        assert len(checklist) > 0
        assert all(isinstance(item, ICSChecklistItem) for item in checklist)

    @pytest.mark.asyncio
    async def test_complete_checklist_item(self, manager):
        """Test completing a checklist item."""
        # Get checklist
        checklist = await manager.get_role_checklist(
            incident_id="inc-001",
            role=ICSRole.INCIDENT_COMMANDER,
            incident_type="active_shooter",
        )

        if checklist:
            item = checklist[0]
            completed = await manager.complete_checklist_item(
                incident_id="inc-001",
                role=ICSRole.INCIDENT_COMMANDER,
                item_id=item.id,
                completed_by="CMD-001",
            )
            assert completed.is_completed is True
            assert completed.completed_at is not None

    @pytest.mark.asyncio
    async def test_relieve_role(self, manager):
        """Test relieving someone from an ICS role."""
        incident_id = "inc-004"

        # Assign role
        await manager.assign_role(
            incident_id=incident_id,
            role=ICSRole.SAFETY_OFFICER,
            badge="SAF-001",
            name="Officer Davis",
            assigned_by="admin-001",
        )

        # Relieve role
        relieved = await manager.relieve_role(
            incident_id=incident_id,
            role=ICSRole.SAFETY_OFFICER,
            relieved_by="commander-001",
            reason="End of shift",
        )

        assert relieved is True

    @pytest.mark.asyncio
    async def test_get_section_roles(self, manager):
        """Test getting roles by section."""
        command_roles = manager.get_roles_by_section(ICSSection.COMMAND)
        operations_roles = manager.get_roles_by_section(ICSSection.OPERATIONS)
        planning_roles = manager.get_roles_by_section(ICSSection.PLANNING)
        logistics_roles = manager.get_roles_by_section(ICSSection.LOGISTICS)

        assert ICSRole.INCIDENT_COMMANDER in command_roles
        assert ICSRole.OPERATIONS_CHIEF in operations_roles
        assert ICSRole.PLANNING_CHIEF in planning_roles
        assert ICSRole.LOGISTICS_CHIEF in logistics_roles

    @pytest.mark.asyncio
    async def test_role_permissions(self, manager):
        """Test getting permissions for an ICS role."""
        ic_permissions = manager.get_role_permissions(ICSRole.INCIDENT_COMMANDER)
        officer_permissions = manager.get_role_permissions(ICSRole.SAFETY_OFFICER)

        assert "full_command" in ic_permissions or len(ic_permissions) > 0
        assert len(officer_permissions) > 0
