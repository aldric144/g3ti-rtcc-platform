"""Tests for the CAD Dispatch Overlay Engine module."""


import pytest

from app.comms.dispatch_overlay import (
    CADCall,
    CADEvent,
    CallPriority,
    CallStatus,
    CallType,
    DispatchOverlayEngine,
    DispatchUnit,
    UnitStatus,
)


@pytest.fixture
def dispatch_engine():
    """Create a dispatch overlay engine instance."""
    return DispatchOverlayEngine()


class TestDispatchOverlayEngine:
    """Tests for DispatchOverlayEngine."""

    @pytest.mark.asyncio
    async def test_process_new_call_event(self, dispatch_engine):
        """Test processing a new CAD call event."""
        event = CADEvent(
            event_type="cad_call_created",
            cad_id="CAD-2024-001",
            data={
                "call_type": "shots_fired",
                "priority": "P1",
                "address": "123 Main St",
                "latitude": 33.7490,
                "longitude": -84.3880,
                "description": "Multiple shots heard",
            },
        )

        result = await dispatch_engine.process_cad_event(event)

        assert result is not None
        assert result.cad_id == "CAD-2024-001"
        assert result.priority == CallPriority.P1

    @pytest.mark.asyncio
    async def test_process_call_update_event(self, dispatch_engine):
        """Test processing a call update event."""
        # First create a call
        create_event = CADEvent(
            event_type="cad_call_created",
            cad_id="CAD-2024-002",
            data={
                "call_type": "robbery",
                "priority": "P1",
                "address": "456 Oak Ave",
            },
        )
        await dispatch_engine.process_cad_event(create_event)

        # Then update it
        update_event = CADEvent(
            event_type="cad_call_updated",
            cad_id="CAD-2024-002",
            data={
                "status": "on_scene",
                "notes": "Officers on scene",
            },
        )

        result = await dispatch_engine.process_cad_event(update_event)

        assert result is not None
        assert result.status == CallStatus.ON_SCENE

    @pytest.mark.asyncio
    async def test_process_unit_status_event(self, dispatch_engine):
        """Test processing a unit status event."""
        event = CADEvent(
            event_type="unit_status_changed",
            unit_id="Alpha-11",
            data={
                "status": "en_route",
                "latitude": 33.7500,
                "longitude": -84.3890,
            },
        )

        result = await dispatch_engine.process_cad_event(event)

        assert result is not None

    @pytest.mark.asyncio
    async def test_get_active_calls(self, dispatch_engine):
        """Test getting active calls."""
        # Create some calls
        for i in range(3):
            event = CADEvent(
                event_type="cad_call_created",
                cad_id=f"CAD-2024-{100 + i}",
                data={
                    "call_type": "disturbance",
                    "priority": "P2",
                    "address": f"{i} Test St",
                },
            )
            await dispatch_engine.process_cad_event(event)

        calls = await dispatch_engine.get_active_calls()

        assert len(calls) >= 3

    @pytest.mark.asyncio
    async def test_get_active_calls_by_priority(self, dispatch_engine):
        """Test filtering active calls by priority."""
        # Create P1 call
        p1_event = CADEvent(
            event_type="cad_call_created",
            cad_id="CAD-2024-P1",
            data={
                "call_type": "shots_fired",
                "priority": "P1",
                "address": "P1 Location",
            },
        )
        await dispatch_engine.process_cad_event(p1_event)

        # Create P3 call
        p3_event = CADEvent(
            event_type="cad_call_created",
            cad_id="CAD-2024-P3",
            data={
                "call_type": "welfare_check",
                "priority": "P3",
                "address": "P3 Location",
            },
        )
        await dispatch_engine.process_cad_event(p3_event)

        p1_calls = await dispatch_engine.get_active_calls(priority=CallPriority.P1)

        assert all(c.priority == CallPriority.P1 for c in p1_calls)

    @pytest.mark.asyncio
    async def test_get_available_units(self, dispatch_engine):
        """Test getting available units."""
        # Add some units
        dispatch_engine._units["Alpha-11"] = DispatchUnit(
            unit_id="Alpha-11",
            status=UnitStatus.AVAILABLE,
            district="Central",
        )
        dispatch_engine._units["Alpha-12"] = DispatchUnit(
            unit_id="Alpha-12",
            status=UnitStatus.ON_SCENE,
            district="Central",
        )

        available = await dispatch_engine.get_available_units()

        assert any(u.unit_id == "Alpha-11" for u in available)
        assert not any(u.unit_id == "Alpha-12" for u in available)

    @pytest.mark.asyncio
    async def test_assign_unit_to_call(self, dispatch_engine):
        """Test assigning a unit to a call."""
        # Create a call
        event = CADEvent(
            event_type="cad_call_created",
            cad_id="CAD-2024-ASSIGN",
            data={
                "call_type": "burglary",
                "priority": "P2",
                "address": "789 Pine St",
            },
        )
        call = await dispatch_engine.process_cad_event(event)

        # Add a unit
        dispatch_engine._units["Bravo-21"] = DispatchUnit(
            unit_id="Bravo-21",
            status=UnitStatus.AVAILABLE,
        )

        # Assign unit
        updated_call = await dispatch_engine.assign_unit_to_call(
            call_id=call.id,
            unit_id="Bravo-21",
        )

        assert "Bravo-21" in updated_call.assigned_units

    @pytest.mark.asyncio
    async def test_get_call_statistics(self, dispatch_engine):
        """Test getting call statistics."""
        # Create some calls
        for i in range(5):
            event = CADEvent(
                event_type="cad_call_created",
                cad_id=f"CAD-STATS-{i}",
                data={
                    "call_type": "disturbance",
                    "priority": "P2",
                    "address": f"{i} Stats St",
                },
            )
            await dispatch_engine.process_cad_event(event)

        stats = await dispatch_engine.get_call_statistics()

        assert "total_active" in stats
        assert "by_priority" in stats
        assert "by_status" in stats


class TestCADCallModel:
    """Tests for CADCall model."""

    def test_cad_call_creation(self):
        """Test creating a CAD call."""
        call = CADCall(
            cad_id="CAD-001",
            call_type=CallType.SHOTS_FIRED,
            priority=CallPriority.P1,
            address="123 Main St",
        )

        assert call.id is not None
        assert call.status == CallStatus.PENDING
        assert call.audit_id is not None

    def test_cad_call_with_location(self):
        """Test CAD call with location."""
        call = CADCall(
            cad_id="CAD-002",
            call_type=CallType.ROBBERY,
            priority=CallPriority.P1,
            address="456 Oak Ave",
            latitude=33.7490,
            longitude=-84.3880,
        )

        assert call.latitude == 33.7490
        assert call.longitude == -84.3880


class TestDispatchUnitModel:
    """Tests for DispatchUnit model."""

    def test_dispatch_unit_creation(self):
        """Test creating a dispatch unit."""
        unit = DispatchUnit(
            unit_id="Alpha-11",
            status=UnitStatus.AVAILABLE,
        )

        assert unit.id is not None
        assert unit.status == UnitStatus.AVAILABLE

    def test_dispatch_unit_with_officer(self):
        """Test dispatch unit with officer info."""
        unit = DispatchUnit(
            unit_id="Alpha-11",
            badge="A1101",
            officer_name="Officer Johnson",
            status=UnitStatus.AVAILABLE,
            district="Central",
            beat="Beat 1",
        )

        assert unit.badge == "A1101"
        assert unit.officer_name == "Officer Johnson"
