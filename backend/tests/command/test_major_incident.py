"""Tests for Major Incident Engine."""


import pytest

from app.command.major_incident import (
    IncidentLocation,
    IncidentPriority,
    IncidentStatus,
    IncidentType,
    MajorIncidentManager,
)


class TestMajorIncidentManager:
    """Test cases for MajorIncidentManager."""

    @pytest.fixture
    def manager(self):
        """Create a MajorIncidentManager instance."""
        return MajorIncidentManager()

    @pytest.fixture
    def sample_location(self):
        """Create a sample location."""
        return IncidentLocation(
            latitude=33.7490,
            longitude=-84.3880,
            address="123 Main St, Atlanta, GA 30303",
            city="Atlanta",
            state="GA",
            zip_code="30303",
        )

    @pytest.mark.asyncio
    async def test_create_incident(self, manager, sample_location):
        """Test creating a new major incident."""
        incident = await manager.create_incident(
            incident_type=IncidentType.ACTIVE_SHOOTER,
            title="Active Shooter at Mall",
            description="Reports of active shooter at downtown mall",
            location=sample_location,
            priority=IncidentPriority.CRITICAL,
            created_by="user-001",
        )

        assert incident is not None
        assert incident.incident_type == IncidentType.ACTIVE_SHOOTER
        assert incident.title == "Active Shooter at Mall"
        assert incident.status == IncidentStatus.PENDING
        assert incident.priority == IncidentPriority.CRITICAL
        assert incident.location == sample_location
        assert incident.incident_number.startswith("MI-")

    @pytest.mark.asyncio
    async def test_activate_incident(self, manager, sample_location):
        """Test activating an incident."""
        incident = await manager.create_incident(
            incident_type=IncidentType.BARRICADED_SUBJECT,
            title="Barricaded Subject",
            description="Armed subject barricaded in residence",
            location=sample_location,
            priority=IncidentPriority.HIGH,
            created_by="user-001",
        )

        activated = await manager.activate_incident(
            incident_id=incident.id,
            activated_by="commander-001",
        )

        assert activated is not None
        assert activated.status == IncidentStatus.ACTIVE
        assert activated.activated_at is not None
        assert activated.activated_by == "commander-001"

    @pytest.mark.asyncio
    async def test_close_incident(self, manager, sample_location):
        """Test closing an incident."""
        incident = await manager.create_incident(
            incident_type=IncidentType.PURSUIT,
            title="Vehicle Pursuit",
            description="High-speed pursuit on I-85",
            location=sample_location,
            priority=IncidentPriority.HIGH,
            created_by="user-001",
        )

        await manager.activate_incident(
            incident_id=incident.id,
            activated_by="commander-001",
        )

        closed = await manager.close_incident(
            incident_id=incident.id,
            closed_by="commander-001",
            resolution="Suspect apprehended",
        )

        assert closed is not None
        assert closed.status == IncidentStatus.CLOSED
        assert closed.closed_at is not None
        assert closed.closed_by == "commander-001"

    @pytest.mark.asyncio
    async def test_assign_commander(self, manager, sample_location):
        """Test assigning a commander to an incident."""
        incident = await manager.create_incident(
            incident_type=IncidentType.HOSTAGE_SITUATION,
            title="Hostage Situation",
            description="Multiple hostages at bank",
            location=sample_location,
            priority=IncidentPriority.CRITICAL,
            created_by="user-001",
        )

        updated = await manager.assign_commander(
            incident_id=incident.id,
            commander_badge="CMD-001",
            commander_name="Captain Rodriguez",
            assigned_by="admin-001",
        )

        assert updated is not None
        assert updated.commander_badge == "CMD-001"
        assert updated.commander_name == "Captain Rodriguez"

    @pytest.mark.asyncio
    async def test_get_active_incidents(self, manager, sample_location):
        """Test getting all active incidents."""
        # Create and activate multiple incidents
        incident1 = await manager.create_incident(
            incident_type=IncidentType.ACTIVE_SHOOTER,
            title="Incident 1",
            description="Description 1",
            location=sample_location,
            priority=IncidentPriority.CRITICAL,
            created_by="user-001",
        )
        await manager.activate_incident(incident1.id, "commander-001")

        incident2 = await manager.create_incident(
            incident_type=IncidentType.RIOT,
            title="Incident 2",
            description="Description 2",
            location=sample_location,
            priority=IncidentPriority.HIGH,
            created_by="user-001",
        )
        await manager.activate_incident(incident2.id, "commander-002")

        active = await manager.get_active_incidents()

        assert len(active) >= 2
        assert all(i.status == IncidentStatus.ACTIVE for i in active)

    @pytest.mark.asyncio
    async def test_incident_types(self, manager, sample_location):
        """Test all incident types can be created."""
        for incident_type in IncidentType:
            incident = await manager.create_incident(
                incident_type=incident_type,
                title=f"Test {incident_type.value}",
                description=f"Testing {incident_type.value} incident type",
                location=sample_location,
                priority=IncidentPriority.MEDIUM,
                created_by="user-001",
            )
            assert incident.incident_type == incident_type

    @pytest.mark.asyncio
    async def test_add_agency(self, manager, sample_location):
        """Test adding an agency to an incident."""
        incident = await manager.create_incident(
            incident_type=IncidentType.MASS_CASUALTY,
            title="Mass Casualty Event",
            description="Multiple casualties reported",
            location=sample_location,
            priority=IncidentPriority.CRITICAL,
            created_by="user-001",
        )

        updated = await manager.add_agency(
            incident_id=incident.id,
            agency_name="County EMS",
            added_by="commander-001",
        )

        assert "County EMS" in updated.agencies

    @pytest.mark.asyncio
    async def test_add_unit(self, manager, sample_location):
        """Test adding a unit to an incident."""
        incident = await manager.create_incident(
            incident_type=IncidentType.BOMB_THREAT,
            title="Bomb Threat",
            description="Bomb threat at courthouse",
            location=sample_location,
            priority=IncidentPriority.CRITICAL,
            created_by="user-001",
        )

        updated = await manager.add_unit(
            incident_id=incident.id,
            unit_id="SWAT-01",
            added_by="commander-001",
        )

        assert "SWAT-01" in updated.units
