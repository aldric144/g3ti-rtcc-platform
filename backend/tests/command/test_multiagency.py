"""Tests for Multi-Agency Coordination Interface."""


import pytest

from app.command.multiagency import (
    AccessLevel,
    AgencyType,
    DataCategory,
    MultiAgencyCoordinator,
)


class TestMultiAgencyCoordinator:
    """Test cases for MultiAgencyCoordinator."""

    @pytest.fixture
    def coordinator(self):
        """Create a MultiAgencyCoordinator instance."""
        return MultiAgencyCoordinator()

    @pytest.mark.asyncio
    async def test_register_agency(self, coordinator):
        """Test registering a new agency."""
        agency = await coordinator.register_agency(
            name="County Sheriff",
            agency_type=AgencyType.SHERIFF,
            jurisdiction="Fulton County",
            contact_name="Sheriff Johnson",
            contact_email="sheriff@fulton.gov",
            contact_phone="555-0100",
        )

        assert agency is not None
        assert agency.name == "County Sheriff"
        assert agency.agency_type == AgencyType.SHERIFF

    @pytest.mark.asyncio
    async def test_add_agency_to_incident(self, coordinator):
        """Test adding an agency to an incident."""
        agency = await coordinator.register_agency(
            name="County EMS",
            agency_type=AgencyType.EMS,
            jurisdiction="Fulton County",
            contact_name="EMS Director",
            contact_email="ems@fulton.gov",
            contact_phone="555-0200",
        )

        participation = await coordinator.add_agency_to_incident(
            incident_id="inc-001",
            agency_id=agency.id,
            access_level=AccessLevel.OPERATIONAL,
            added_by="commander-001",
        )

        assert participation is not None
        assert participation.agency_id == agency.id
        assert participation.access_level == AccessLevel.OPERATIONAL

    @pytest.mark.asyncio
    async def test_remove_agency_from_incident(self, coordinator):
        """Test removing an agency from an incident."""
        agency = await coordinator.register_agency(
            name="State Police",
            agency_type=AgencyType.STATE_POLICE,
            jurisdiction="Georgia",
            contact_name="Captain Smith",
            contact_email="gsp@georgia.gov",
            contact_phone="555-0300",
        )

        await coordinator.add_agency_to_incident(
            incident_id="inc-001",
            agency_id=agency.id,
            access_level=AccessLevel.READ_ONLY,
            added_by="commander-001",
        )

        result = await coordinator.remove_agency_from_incident(
            incident_id="inc-001",
            agency_id=agency.id,
            removed_by="commander-001",
            reason="No longer needed",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_update_agency_access(self, coordinator):
        """Test updating agency access level."""
        agency = await coordinator.register_agency(
            name="FBI",
            agency_type=AgencyType.FEDERAL,
            jurisdiction="Federal",
            contact_name="Agent Brown",
            contact_email="agent@fbi.gov",
            contact_phone="555-0400",
        )

        await coordinator.add_agency_to_incident(
            incident_id="inc-001",
            agency_id=agency.id,
            access_level=AccessLevel.READ_ONLY,
            added_by="commander-001",
        )

        updated = await coordinator.update_agency_access(
            incident_id="inc-001",
            agency_id=agency.id,
            access_level=AccessLevel.FULL,
            updated_by="commander-001",
        )

        assert updated.access_level == AccessLevel.FULL

    @pytest.mark.asyncio
    async def test_get_incident_agencies(self, coordinator):
        """Test getting all agencies for an incident."""
        incident_id = "inc-002"

        agency1 = await coordinator.register_agency(
            name="Agency 1",
            agency_type=AgencyType.POLICE,
            jurisdiction="City",
            contact_name="Contact 1",
            contact_email="a1@test.gov",
            contact_phone="555-0001",
        )
        agency2 = await coordinator.register_agency(
            name="Agency 2",
            agency_type=AgencyType.FIRE,
            jurisdiction="County",
            contact_name="Contact 2",
            contact_email="a2@test.gov",
            contact_phone="555-0002",
        )

        await coordinator.add_agency_to_incident(
            incident_id, agency1.id, AccessLevel.OPERATIONAL, "cmd-001"
        )
        await coordinator.add_agency_to_incident(
            incident_id, agency2.id, AccessLevel.READ_ONLY, "cmd-001"
        )

        agencies = await coordinator.get_incident_agencies(incident_id)

        assert len(agencies) >= 2

    @pytest.mark.asyncio
    async def test_create_shared_channel(self, coordinator):
        """Test creating a shared communication channel."""
        channel = await coordinator.create_shared_channel(
            incident_id="inc-001",
            channel_name="Command Channel",
            channel_type="tactical",
            created_by="commander-001",
        )

        assert channel is not None
        assert channel.channel_name == "Command Channel"

    @pytest.mark.asyncio
    async def test_request_data_share(self, coordinator):
        """Test requesting data share between agencies."""
        agency = await coordinator.register_agency(
            name="Partner Agency",
            agency_type=AgencyType.POLICE,
            jurisdiction="Neighboring City",
            contact_name="Chief",
            contact_email="chief@partner.gov",
            contact_phone="555-0500",
        )

        await coordinator.add_agency_to_incident(
            incident_id="inc-001",
            agency_id=agency.id,
            access_level=AccessLevel.READ_ONLY,
            added_by="commander-001",
        )

        request = await coordinator.request_data_share(
            incident_id="inc-001",
            requesting_agency_id=agency.id,
            data_category=DataCategory.SUSPECT_INFO,
            justification="Need suspect information for investigation",
            requested_by="agent-001",
        )

        assert request is not None
        assert request.data_category == DataCategory.SUSPECT_INFO
        assert request.status == "pending"

    @pytest.mark.asyncio
    async def test_approve_data_share(self, coordinator):
        """Test approving a data share request."""
        agency = await coordinator.register_agency(
            name="Requesting Agency",
            agency_type=AgencyType.POLICE,
            jurisdiction="City",
            contact_name="Detective",
            contact_email="det@city.gov",
            contact_phone="555-0600",
        )

        await coordinator.add_agency_to_incident(
            incident_id="inc-001",
            agency_id=agency.id,
            access_level=AccessLevel.READ_ONLY,
            added_by="commander-001",
        )

        request = await coordinator.request_data_share(
            incident_id="inc-001",
            requesting_agency_id=agency.id,
            data_category=DataCategory.VEHICLE_INFO,
            justification="Vehicle tracking needed",
            requested_by="det-001",
        )

        approved = await coordinator.approve_data_share(
            incident_id="inc-001",
            request_id=request.id,
            approved_by="commander-001",
        )

        assert approved.status == "approved"

    @pytest.mark.asyncio
    async def test_deny_data_share(self, coordinator):
        """Test denying a data share request."""
        agency = await coordinator.register_agency(
            name="External Agency",
            agency_type=AgencyType.OTHER,
            jurisdiction="External",
            contact_name="Agent",
            contact_email="agent@external.gov",
            contact_phone="555-0700",
        )

        await coordinator.add_agency_to_incident(
            incident_id="inc-001",
            agency_id=agency.id,
            access_level=AccessLevel.RESTRICTED,
            added_by="commander-001",
        )

        request = await coordinator.request_data_share(
            incident_id="inc-001",
            requesting_agency_id=agency.id,
            data_category=DataCategory.OFFICER_INFO,
            justification="Need officer details",
            requested_by="agent-001",
        )

        denied = await coordinator.deny_data_share(
            incident_id="inc-001",
            request_id=request.id,
            denied_by="commander-001",
            reason="CJIS compliance restriction",
        )

        assert denied.status == "denied"

    @pytest.mark.asyncio
    async def test_agency_types(self, coordinator):
        """Test all agency types can be registered."""
        for i, agency_type in enumerate(AgencyType):
            agency = await coordinator.register_agency(
                name=f"Agency {i}",
                agency_type=agency_type,
                jurisdiction=f"Jurisdiction {i}",
                contact_name=f"Contact {i}",
                contact_email=f"contact{i}@test.gov",
                contact_phone=f"555-{i:04d}",
            )
            assert agency.agency_type == agency_type

    @pytest.mark.asyncio
    async def test_access_levels(self, coordinator):
        """Test all access levels can be assigned."""
        agency = await coordinator.register_agency(
            name="Test Agency",
            agency_type=AgencyType.POLICE,
            jurisdiction="Test",
            contact_name="Test Contact",
            contact_email="test@test.gov",
            contact_phone="555-9999",
        )

        for access_level in AccessLevel:
            participation = await coordinator.add_agency_to_incident(
                incident_id=f"inc-{access_level.value}",
                agency_id=agency.id,
                access_level=access_level,
                added_by="commander-001",
            )
            assert participation.access_level == access_level

    @pytest.mark.asyncio
    async def test_can_access_data(self, coordinator):
        """Test checking if agency can access specific data."""
        agency = await coordinator.register_agency(
            name="Limited Agency",
            agency_type=AgencyType.POLICE,
            jurisdiction="City",
            contact_name="Officer",
            contact_email="officer@city.gov",
            contact_phone="555-8888",
        )

        await coordinator.add_agency_to_incident(
            incident_id="inc-001",
            agency_id=agency.id,
            access_level=AccessLevel.READ_ONLY,
            added_by="commander-001",
        )

        can_access = await coordinator.can_access_data(
            incident_id="inc-001",
            agency_id=agency.id,
            data_category=DataCategory.INCIDENT_INFO,
        )

        assert isinstance(can_access, bool)

    @pytest.mark.asyncio
    async def test_add_agency_contact(self, coordinator):
        """Test adding a contact to an agency."""
        agency = await coordinator.register_agency(
            name="Multi-Contact Agency",
            agency_type=AgencyType.POLICE,
            jurisdiction="City",
            contact_name="Primary Contact",
            contact_email="primary@agency.gov",
            contact_phone="555-1111",
        )

        updated = await coordinator.add_agency_contact(
            agency_id=agency.id,
            contact_name="Secondary Contact",
            contact_email="secondary@agency.gov",
            contact_phone="555-2222",
            contact_role="Operations",
        )

        assert len(updated.contacts) >= 2
