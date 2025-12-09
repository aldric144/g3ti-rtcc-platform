"""
G3TI RTCC-UIP MDT Integration Tests
Tests for the MDT (Mobile Data Terminal) Integration module
"""


import pytest

from app.mdt import (
    CADCallPriority,
    CADCallStatus,
    MDTManager,
    MDTUnitStatus,
    SceneRole,
)


class TestMDTManager:
    """Tests for MDTManager"""

    @pytest.fixture
    def manager(self):
        """Create a fresh manager instance for each test"""
        return MDTManager()

    def test_register_unit(self, manager):
        """Test unit registration"""
        unit = manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
            vehicle_id="V001",
        )

        assert unit is not None
        assert unit.unit_id == "A1"
        assert unit.badge_number == "1234"
        assert unit.status == MDTUnitStatus.AVAILABLE

    def test_update_unit_status(self, manager):
        """Test updating unit status"""
        # Register unit first
        manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
        )

        # Update status
        unit = manager.update_unit_status(
            unit_id="A1",
            status=MDTUnitStatus.EN_ROUTE,
            latitude=34.0522,
            longitude=-118.2437,
        )

        assert unit is not None
        assert unit.status == MDTUnitStatus.EN_ROUTE

    def test_get_unit_status(self, manager):
        """Test getting unit status"""
        # Register unit
        manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
        )

        # Get status
        unit = manager.get_unit_status("1234")

        assert unit is not None
        assert unit.badge_number == "1234"

    def test_get_unit_by_id(self, manager):
        """Test getting unit by ID"""
        # Register unit
        manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
        )

        # Get by ID
        unit = manager.get_unit_by_id("A1")

        assert unit is not None
        assert unit.unit_id == "A1"

    def test_get_all_units(self, manager):
        """Test getting all units"""
        # Register multiple units
        manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
        )
        manager.register_unit(
            unit_id="B2",
            badge_number="5678",
            officer_name="Officer Jones",
        )

        # Get all units
        units = manager.get_all_units()

        assert len(units) == 2

    def test_get_status_history(self, manager):
        """Test getting status history"""
        # Register unit
        manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
        )

        # Update status multiple times
        manager.update_unit_status("A1", MDTUnitStatus.EN_ROUTE)
        manager.update_unit_status("A1", MDTUnitStatus.ON_SCENE)
        manager.update_unit_status("A1", MDTUnitStatus.AVAILABLE)

        # Get history
        history = manager.get_status_history("A1")

        assert len(history) >= 3

    def test_add_cad_call(self, manager):
        """Test adding CAD call"""
        call = manager.add_cad_call(
            call_number="CAD-2024-001234",
            call_type="Burglary in Progress",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
            description="Caller reports break-in",
        )

        assert call is not None
        assert call.call_number == "CAD-2024-001234"
        assert call.priority == CADCallPriority.PRIORITY_1
        assert call.status == CADCallStatus.PENDING

    def test_get_cad_call(self, manager):
        """Test getting CAD call"""
        call = manager.add_cad_call(
            call_number="CAD-2024-001234",
            call_type="Burglary",
            priority=CADCallPriority.PRIORITY_2,
            location="123 Main St",
        )

        retrieved = manager.get_cad_call(call.id)

        assert retrieved is not None
        assert retrieved.id == call.id

    def test_get_active_dispatch(self, manager):
        """Test getting active dispatch calls"""
        # Add calls
        manager.add_cad_call(
            call_number="CAD-001",
            call_type="Burglary",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )
        manager.add_cad_call(
            call_number="CAD-002",
            call_type="Traffic",
            priority=CADCallPriority.PRIORITY_3,
            location="456 Oak Ave",
        )

        # Get active dispatch
        calls = manager.get_active_dispatch()

        assert len(calls) == 2

    def test_assign_unit_to_call(self, manager):
        """Test assigning unit to call"""
        # Register unit
        manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
        )

        # Add call
        call = manager.add_cad_call(
            call_number="CAD-001",
            call_type="Burglary",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )

        # Assign unit
        result = manager.assign_unit_to_call(call.id, "A1")

        assert result is True
        assert "A1" in call.assigned_units
        assert call.status == CADCallStatus.DISPATCHED

    def test_remove_unit_from_call(self, manager):
        """Test removing unit from call"""
        # Register unit
        manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
        )

        # Add call and assign unit
        call = manager.add_cad_call(
            call_number="CAD-001",
            call_type="Burglary",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )
        manager.assign_unit_to_call(call.id, "A1")

        # Remove unit
        result = manager.remove_unit_from_call(call.id, "A1")

        assert result is True
        assert "A1" not in call.assigned_units

    def test_clear_call(self, manager):
        """Test clearing a call"""
        call = manager.add_cad_call(
            call_number="CAD-001",
            call_type="Burglary",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )

        result = manager.clear_call(call.id, "Report taken")

        assert result is True
        assert call.status == CADCallStatus.CLEARED

    def test_add_call_note(self, manager):
        """Test adding note to call"""
        call = manager.add_cad_call(
            call_number="CAD-001",
            call_type="Burglary",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )

        note = manager.add_call_note(
            call_id=call.id,
            author_badge="1234",
            author_name="Officer Smith",
            content="Arrived on scene, securing perimeter",
        )

        assert note is not None
        assert note.content == "Arrived on scene, securing perimeter"

    def test_get_call_notes(self, manager):
        """Test getting call notes"""
        call = manager.add_cad_call(
            call_number="CAD-001",
            call_type="Burglary",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )

        # Add notes
        manager.add_call_note(call.id, "1234", "Officer Smith", "Note 1")
        manager.add_call_note(call.id, "5678", "Officer Jones", "Note 2")

        # Get notes
        notes = manager.get_call_notes(call.id)

        assert len(notes) == 2

    def test_create_scene_coordination(self, manager):
        """Test creating scene coordination"""
        call = manager.add_cad_call(
            call_number="CAD-001",
            call_type="Major Incident",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )

        coordination = manager.create_scene_coordination(
            call_id=call.id,
            incident_commander="Sgt. Johnson",
            staging_location="100 Main St Parking Lot",
        )

        assert coordination is not None
        assert coordination.incident_commander == "Sgt. Johnson"

    def test_assign_scene_role(self, manager):
        """Test assigning scene role"""
        # Register unit
        manager.register_unit(
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
        )

        # Add call and create coordination
        call = manager.add_cad_call(
            call_number="CAD-001",
            call_type="Major Incident",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )
        manager.create_scene_coordination(call.id)

        # Assign role
        result = manager.assign_scene_role(
            call_id=call.id,
            unit_id="A1",
            badge_number="1234",
            officer_name="Officer Smith",
            role=SceneRole.PERIMETER,
        )

        assert result is True

    def test_update_scene_coordination(self, manager):
        """Test updating scene coordination"""
        call = manager.add_cad_call(
            call_number="CAD-001",
            call_type="Major Incident",
            priority=CADCallPriority.PRIORITY_1,
            location="123 Main St",
        )
        manager.create_scene_coordination(call.id)

        # Update coordination
        coordination = manager.update_scene_coordination(
            call_id=call.id,
            perimeter_established=True,
            resources_on_scene=["K9", "Air Support"],
        )

        assert coordination is not None
        assert coordination.perimeter_established is True
        assert "K9" in coordination.resources_on_scene

    def test_send_mdt_message(self, manager):
        """Test sending MDT message"""
        message = manager.send_mdt_message(
            sender_badge="1234",
            sender_name="Officer Smith",
            content="Test message",
            recipient_badge="5678",
        )

        assert message is not None
        assert message.content == "Test message"

    def test_get_mdt_messages(self, manager):
        """Test getting MDT messages"""
        # Send messages
        manager.send_mdt_message("1234", "Officer Smith", "Message 1", "5678")
        manager.send_mdt_message("5678", "Officer Jones", "Message 2", "1234")

        # Get messages for badge
        messages = manager.get_mdt_messages("1234")

        assert len(messages) == 2

    def test_mark_message_read(self, manager):
        """Test marking message as read"""
        message = manager.send_mdt_message(
            sender_badge="1234",
            sender_name="Officer Smith",
            content="Test message",
            recipient_badge="5678",
        )

        result = manager.mark_message_read(message.id)

        assert result is True
        assert message.read is True

    def test_get_available_units(self, manager):
        """Test getting available units"""
        # Register units with different statuses
        manager.register_unit("A1", "1234", "Officer Smith")
        manager.register_unit("B2", "5678", "Officer Jones")
        manager.register_unit("C3", "9012", "Officer Davis")

        # Update one to unavailable
        manager.update_unit_status("B2", MDTUnitStatus.OUT_OF_SERVICE)

        # Get available units
        available = manager.get_available_units()

        assert len(available) == 2

    def test_get_premise_history(self, manager):
        """Test getting premise history"""
        # Add calls at same location
        manager.add_cad_call(
            call_number="CAD-001",
            call_type="Burglary",
            priority=CADCallPriority.PRIORITY_2,
            location="123 Main St",
        )
        manager.add_cad_call(
            call_number="CAD-002",
            call_type="Disturbance",
            priority=CADCallPriority.PRIORITY_3,
            location="123 Main St",
        )

        # Get premise history
        history = manager.get_premise_history("123 Main St")

        assert len(history) == 2
