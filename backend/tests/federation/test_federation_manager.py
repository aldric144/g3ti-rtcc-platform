"""
Tests for Multi-Agency Federation Engine
Phase 10: Federation Manager, Registry, and Access Policy tests
"""

from datetime import datetime, timedelta

import pytest

from app.federation import (
    AccessLevel,
    AccessPolicyManager,
    AgencyStatus,
    AgencyType,
    DataCategory,
    DataSharingLevel,
    FederationManager,
    FederationRegistry,
    PartnerAgencyDataMapper,
)


class TestFederationRegistry:
    """Tests for FederationRegistry"""

    def setup_method(self):
        """Set up test fixtures"""
        self.registry = FederationRegistry()

    def test_register_agency(self):
        """Test agency registration"""
        agency = self.registry.register_agency(
            agency_name="Test Sheriff's Office",
            agency_type=AgencyType.SHERIFF_OFFICE,
            jurisdiction="Test County",
            contact_email="test@sheriff.gov",
            contact_phone="555-1234",
            api_endpoint="https://api.sheriff.gov",
            data_sharing_level=DataSharingLevel.FULL,
        )

        assert agency is not None
        assert agency.name == "Test Sheriff's Office"
        assert agency.agency_type == AgencyType.SHERIFF_OFFICE
        assert agency.jurisdiction == "Test County"
        assert agency.status == AgencyStatus.PENDING

    def test_get_agency(self):
        """Test getting agency by ID"""
        agency = self.registry.register_agency(
            agency_name="Test Agency",
            agency_type=AgencyType.LOCAL_PD,
            jurisdiction="Test City",
            contact_email="test@pd.gov",
        )

        retrieved = self.registry.get_agency(agency.id)
        assert retrieved is not None
        assert retrieved.id == agency.id
        assert retrieved.name == agency.name

    def test_get_nonexistent_agency(self):
        """Test getting non-existent agency"""
        retrieved = self.registry.get_agency("nonexistent-id")
        assert retrieved is None

    def test_list_agencies(self):
        """Test listing agencies"""
        self.registry.register_agency(
            agency_name="Agency 1",
            agency_type=AgencyType.LOCAL_PD,
            jurisdiction="City 1",
            contact_email="test1@pd.gov",
        )
        self.registry.register_agency(
            agency_name="Agency 2",
            agency_type=AgencyType.SHERIFF_OFFICE,
            jurisdiction="County 1",
            contact_email="test2@sheriff.gov",
        )

        all_agencies = self.registry.list_agencies()
        assert len(all_agencies) == 2

        local_pd_only = self.registry.list_agencies(agency_type=AgencyType.LOCAL_PD)
        assert len(local_pd_only) == 1
        assert local_pd_only[0].agency_type == AgencyType.LOCAL_PD

    def test_update_agency_status(self):
        """Test updating agency status"""
        agency = self.registry.register_agency(
            agency_name="Test Agency",
            agency_type=AgencyType.LOCAL_PD,
            jurisdiction="Test City",
            contact_email="test@pd.gov",
        )

        updated = self.registry.update_agency_status(agency.id, AgencyStatus.ACTIVE)
        assert updated is not None
        assert updated.status == AgencyStatus.ACTIVE

    def test_deactivate_agency(self):
        """Test deactivating agency"""
        agency = self.registry.register_agency(
            agency_name="Test Agency",
            agency_type=AgencyType.LOCAL_PD,
            jurisdiction="Test City",
            contact_email="test@pd.gov",
        )
        self.registry.update_agency_status(agency.id, AgencyStatus.ACTIVE)

        result = self.registry.deactivate_agency(agency.id)
        assert result is True

        retrieved = self.registry.get_agency(agency.id)
        assert retrieved.status == AgencyStatus.INACTIVE


class TestAccessPolicyManager:
    """Tests for AccessPolicyManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.policy_manager = AccessPolicyManager()

    def test_create_data_sharing_agreement(self):
        """Test creating data sharing agreement"""
        agreement = self.policy_manager.create_data_sharing_agreement(
            agency_id="agency-1",
            partner_agency_id="agency-2",
            data_categories=[DataCategory.INCIDENTS, DataCategory.PERSONS],
            access_level=AccessLevel.READ,
            effective_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )

        assert agreement is not None
        assert agreement.agency_id == "agency-1"
        assert agreement.partner_agency_id == "agency-2"
        assert DataCategory.INCIDENTS in agreement.data_categories
        assert agreement.access_level == AccessLevel.READ

    def test_check_access_allowed(self):
        """Test access permission check"""
        self.policy_manager.create_data_sharing_agreement(
            agency_id="agency-1",
            partner_agency_id="agency-2",
            data_categories=[DataCategory.INCIDENTS],
            access_level=AccessLevel.READ,
            effective_date=datetime.utcnow(),
        )

        # Should be allowed
        allowed = self.policy_manager.check_access(
            requesting_agency="agency-2",
            target_agency="agency-1",
            data_category=DataCategory.INCIDENTS,
            access_level=AccessLevel.READ,
        )
        assert allowed is True

    def test_check_access_denied_wrong_category(self):
        """Test access denied for wrong category"""
        self.policy_manager.create_data_sharing_agreement(
            agency_id="agency-1",
            partner_agency_id="agency-2",
            data_categories=[DataCategory.INCIDENTS],
            access_level=AccessLevel.READ,
            effective_date=datetime.utcnow(),
        )

        # Should be denied - wrong category
        allowed = self.policy_manager.check_access(
            requesting_agency="agency-2",
            target_agency="agency-1",
            data_category=DataCategory.PERSONS,
            access_level=AccessLevel.READ,
        )
        assert allowed is False

    def test_check_access_denied_wrong_level(self):
        """Test access denied for wrong access level"""
        self.policy_manager.create_data_sharing_agreement(
            agency_id="agency-1",
            partner_agency_id="agency-2",
            data_categories=[DataCategory.INCIDENTS],
            access_level=AccessLevel.READ,
            effective_date=datetime.utcnow(),
        )

        # Should be denied - trying to write with read-only access
        allowed = self.policy_manager.check_access(
            requesting_agency="agency-2",
            target_agency="agency-1",
            data_category=DataCategory.INCIDENTS,
            access_level=AccessLevel.WRITE,
        )
        assert allowed is False

    def test_create_access_policy(self):
        """Test creating access policy"""
        policy = self.policy_manager.create_access_policy(
            name="Test Policy",
            description="Test access policy",
            agency_id="agency-1",
            allowed_data_categories=[DataCategory.INCIDENTS, DataCategory.VEHICLES],
            denied_fields=["ssn", "dob"],
            requires_audit=True,
        )

        assert policy is not None
        assert policy.name == "Test Policy"
        assert "ssn" in policy.denied_fields


class TestFederationManager:
    """Tests for FederationManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = FederationManager()

    def test_register_partner_agency(self):
        """Test registering partner agency through manager"""
        agency = self.manager.register_partner_agency(
            agency_name="Partner Agency",
            agency_type=AgencyType.STATE_FUSION_CENTER,
            jurisdiction="State",
            contact_email="partner@state.gov",
        )

        assert agency is not None
        assert agency.name == "Partner Agency"

    @pytest.mark.asyncio
    async def test_execute_federated_query(self):
        """Test executing federated query"""
        # Register an agency first
        agency = self.manager.register_partner_agency(
            agency_name="Query Target",
            agency_type=AgencyType.LOCAL_PD,
            jurisdiction="City",
            contact_email="target@pd.gov",
        )
        self.manager.registry.update_agency_status(agency.id, AgencyStatus.ACTIVE)

        result = await self.manager.execute_federated_query(
            query_type="person_search",
            parameters={"name": "John Doe"},
            requesting_agency="local",
            requesting_user="test_user",
            target_agencies=[agency.id],
        )

        assert result is not None
        assert result.query_type == "person_search"

    def test_generate_access_token(self):
        """Test generating access token for agency"""
        agency = self.manager.register_partner_agency(
            agency_name="Token Test Agency",
            agency_type=AgencyType.LOCAL_PD,
            jurisdiction="City",
            contact_email="token@pd.gov",
        )

        token = self.manager.generate_access_token(
            agency_id=agency.id,
            scopes=["read", "query"],
            expires_in_hours=24,
        )

        assert token is not None
        assert token.agency_id == agency.id
        assert "read" in token.scopes

    def test_log_audit_entry(self):
        """Test audit logging"""
        entry = self.manager.log_audit_entry(
            agency_id="agency-1",
            user_id="user-1",
            action="query",
            resource_type="person",
            resource_id="person-123",
            details={"query": "test query"},
        )

        assert entry is not None
        assert entry.agency_id == "agency-1"
        assert entry.action == "query"


class TestPartnerAgencyDataMapper:
    """Tests for PartnerAgencyDataMapper"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mapper = PartnerAgencyDataMapper()

    def test_map_person_data(self):
        """Test mapping person data"""
        source_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-15",
            "ssn": "123-45-6789",
        }

        mapped = self.mapper.map_person_data(source_data, "agency-1")
        assert mapped is not None
        assert "first_name" in mapped
        assert mapped["source_agency"] == "agency-1"

    def test_map_vehicle_data(self):
        """Test mapping vehicle data"""
        source_data = {
            "plate": "ABC1234",
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "1HGBH41JXMN109186",
        }

        mapped = self.mapper.map_vehicle_data(source_data, "agency-1")
        assert mapped is not None
        assert mapped["plate"] == "ABC1234"
        assert mapped["source_agency"] == "agency-1"

    def test_map_incident_data(self):
        """Test mapping incident data"""
        source_data = {
            "incident_number": "2024-12345",
            "incident_type": "Burglary",
            "location": "123 Main St",
            "date": "2024-12-01",
        }

        mapped = self.mapper.map_incident_data(source_data, "agency-1")
        assert mapped is not None
        assert mapped["incident_number"] == "2024-12345"
