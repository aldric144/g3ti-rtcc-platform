"""Tests for the Scene Coordination module."""


import pytest

from app.comms.scene_coordination import (
    Scene,
    SceneCoordinationManager,
    SceneStatus,
    SceneUnit,
    TacticalRole,
    UnitSafetyLevel,
)


@pytest.fixture
def scene_manager():
    """Create a scene coordination manager instance."""
    return SceneCoordinationManager()


class TestSceneCoordinationManager:
    """Tests for SceneCoordinationManager."""

    @pytest.mark.asyncio
    async def test_create_scene(self, scene_manager):
        """Test creating a scene."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-001",
            incident_type="Armed Robbery",
            address="123 Main St",
            latitude=33.7490,
            longitude=-84.3880,
            threat_level="high",
        )

        assert scene is not None
        assert scene.incident_id == "INC-2024-001"
        assert scene.incident_type == "Armed Robbery"
        assert scene.status == SceneStatus.ACTIVE
        assert scene.audit_id is not None

    @pytest.mark.asyncio
    async def test_assign_unit(self, scene_manager):
        """Test assigning a unit to a scene."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-002",
            incident_type="Burglary",
            address="456 Oak Ave",
        )

        updated_scene, unit = await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
            role=TacticalRole.CONTACT,
            badge="A1101",
            officer_name="Officer Johnson",
        )

        assert len(updated_scene.units) == 1
        assert unit.unit_id == "Alpha-11"
        assert unit.role == TacticalRole.CONTACT

    @pytest.mark.asyncio
    async def test_assign_multiple_units(self, scene_manager):
        """Test assigning multiple units to a scene."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-003",
            incident_type="Shots Fired",
            address="789 Pine St",
        )

        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
            role=TacticalRole.CONTACT,
        )
        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-12",
            role=TacticalRole.COVER,
        )
        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Bravo-21",
            role=TacticalRole.PERIMETER,
        )

        updated_scene = await scene_manager.get_scene(scene.id)

        assert len(updated_scene.units) == 3

    @pytest.mark.asyncio
    async def test_update_unit_role(self, scene_manager):
        """Test updating a unit's role."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-004",
            incident_type="Disturbance",
            address="321 Elm St",
        )

        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
            role=TacticalRole.PERIMETER,
        )

        updated_scene, unit = await scene_manager.update_unit_role(
            scene_id=scene.id,
            unit_id="Alpha-11",
            new_role=TacticalRole.CONTACT,
        )

        assert unit.role == TacticalRole.CONTACT

    @pytest.mark.asyncio
    async def test_update_unit_position(self, scene_manager):
        """Test updating a unit's position."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-005",
            incident_type="Welfare Check",
            address="654 Maple Dr",
        )

        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
            role=TacticalRole.CONTACT,
        )

        unit = await scene_manager.update_unit_position(
            scene_id=scene.id,
            unit_id="Alpha-11",
            latitude=33.7500,
            longitude=-84.3890,
            position_description="Front door",
        )

        assert unit.latitude == 33.7500
        assert unit.longitude == -84.3890
        assert unit.position_description == "Front door"

    @pytest.mark.asyncio
    async def test_update_unit_safety(self, scene_manager):
        """Test updating a unit's safety status."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-006",
            incident_type="Domestic",
            address="987 Cedar Ln",
        )

        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
            role=TacticalRole.CONTACT,
        )

        unit = await scene_manager.update_unit_safety(
            scene_id=scene.id,
            unit_id="Alpha-11",
            safety_level=UnitSafetyLevel.YELLOW,
            safety_score=75.0,
            threat_indicators=["Elevated risk area"],
        )

        assert unit.safety_level == UnitSafetyLevel.YELLOW
        assert unit.safety_score == 75.0

    @pytest.mark.asyncio
    async def test_remove_unit(self, scene_manager):
        """Test removing a unit from a scene."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-007",
            incident_type="Traffic Stop",
            address="111 First Ave",
        )

        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
            role=TacticalRole.CONTACT,
        )

        updated_scene = await scene_manager.remove_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
        )

        assert len(updated_scene.units) == 0

    @pytest.mark.asyncio
    async def test_set_commander(self, scene_manager):
        """Test setting the on-scene commander."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-008",
            incident_type="Active Shooter",
            address="222 Second St",
        )

        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Sgt-01",
            role=TacticalRole.UNASSIGNED,
            badge="S101",
            officer_name="Sgt. Taylor",
        )

        updated_scene = await scene_manager.set_commander(
            scene_id=scene.id,
            unit_id="Sgt-01",
        )

        assert updated_scene.commander_unit_id == "Sgt-01"

    @pytest.mark.asyncio
    async def test_update_scene_status(self, scene_manager):
        """Test updating scene status."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-009",
            incident_type="Burglary",
            address="333 Third Blvd",
        )

        updated_scene = await scene_manager.update_scene_status(
            scene_id=scene.id,
            status=SceneStatus.CONTAINED,
        )

        assert updated_scene.status == SceneStatus.CONTAINED

    @pytest.mark.asyncio
    async def test_add_tactical_note(self, scene_manager):
        """Test adding a tactical note."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-010",
            incident_type="Robbery",
            address="444 Fourth Way",
        )

        updated_scene = await scene_manager.add_tactical_note(
            scene_id=scene.id,
            note="Suspect fled on foot heading north",
        )

        assert len(updated_scene.tactical_notes) == 1

    @pytest.mark.asyncio
    async def test_add_hazard(self, scene_manager):
        """Test adding a hazard."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-011",
            incident_type="Structure Fire",
            address="555 Fifth Pl",
        )

        updated_scene = await scene_manager.add_hazard(
            scene_id=scene.id,
            hazard="Unstable structure",
        )

        assert "Unstable structure" in updated_scene.hazards

    @pytest.mark.asyncio
    async def test_get_scene_status(self, scene_manager):
        """Test getting comprehensive scene status."""
        scene = await scene_manager.create_scene(
            incident_id="INC-2024-012",
            incident_type="Hostage",
            address="666 Sixth Ave",
            threat_level="critical",
        )

        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
            role=TacticalRole.CONTACT,
        )
        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-12",
            role=TacticalRole.COVER,
        )

        status = await scene_manager.get_scene_status(scene.id)

        assert status["total_units"] == 2
        assert "units_by_role" in status
        assert "units_by_safety" in status

    @pytest.mark.asyncio
    async def test_get_active_scenes(self, scene_manager):
        """Test getting all active scenes."""
        await scene_manager.create_scene(
            incident_id="INC-ACTIVE-1",
            incident_type="Robbery",
            address="Active 1",
        )
        await scene_manager.create_scene(
            incident_id="INC-ACTIVE-2",
            incident_type="Assault",
            address="Active 2",
        )

        active_scenes = await scene_manager.get_active_scenes()

        assert len(active_scenes) >= 2

    @pytest.mark.asyncio
    async def test_get_scene_events(self, scene_manager):
        """Test getting scene events."""
        scene = await scene_manager.create_scene(
            incident_id="INC-EVENTS",
            incident_type="Test",
            address="Events Test",
        )

        await scene_manager.assign_unit(
            scene_id=scene.id,
            unit_id="Alpha-11",
            role=TacticalRole.CONTACT,
        )

        events = await scene_manager.get_scene_events(scene.id)

        assert len(events) >= 2  # scene_created + unit_assigned


class TestSceneModel:
    """Tests for Scene model."""

    def test_scene_creation(self):
        """Test creating a scene."""
        scene = Scene(
            incident_id="INC-001",
            incident_type="Robbery",
            address="123 Main St",
        )

        assert scene.id is not None
        assert scene.status == SceneStatus.ACTIVE
        assert scene.audit_id is not None

    def test_scene_with_units(self):
        """Test scene with units."""
        unit = SceneUnit(
            unit_id="Alpha-11",
            role=TacticalRole.CONTACT,
        )

        scene = Scene(
            incident_id="INC-002",
            incident_type="Burglary",
            address="456 Oak Ave",
            units=[unit],
        )

        assert len(scene.units) == 1


class TestSceneUnitModel:
    """Tests for SceneUnit model."""

    def test_scene_unit_creation(self):
        """Test creating a scene unit."""
        unit = SceneUnit(
            unit_id="Alpha-11",
            badge="A1101",
            officer_name="Officer Johnson",
            role=TacticalRole.CONTACT,
        )

        assert unit.id is not None
        assert unit.status == "on_scene"
        assert unit.safety_level == UnitSafetyLevel.GREEN
