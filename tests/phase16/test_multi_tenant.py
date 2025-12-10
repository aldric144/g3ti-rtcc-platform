"""
Tests for MultiTenantManager

Tests tenant registration, lifecycle management, data sources,
integrations, and federation partnerships.
"""

import pytest
from datetime import datetime

from app.fusion_cloud.multi_tenant import (
    MultiTenantManager,
    Tenant,
    TenantType,
    TenantStatus,
    TenantProfile,
    TenantPolicy,
    DataSource,
    DataSourceType,
    IntegrationConfig,
    IntegrationStatus,
)


@pytest.fixture
def tenant_manager():
    """Create a fresh MultiTenantManager for each test"""
    return MultiTenantManager()


@pytest.fixture
def sample_profile():
    """Create a sample tenant profile"""
    return TenantProfile(
        profile_id="profile-test",
        display_name="Test Police Department",
        description="Test PD for unit tests",
        primary_contact_name="John Smith",
        primary_contact_email="john.smith@testpd.gov",
        primary_contact_phone="555-123-4567",
        city="Test City",
        state="CA",
        zip_code="90210",
        timezone="America/Los_Angeles",
        ori_number="CA0123456",
    )


@pytest.fixture
def sample_policy():
    """Create a sample tenant policy"""
    return TenantPolicy(
        policy_id="policy-test",
        name="Standard Policy",
        data_retention_days=365,
        max_users=100,
        max_concurrent_sessions=50,
        federation_enabled=True,
        cross_agency_sharing_enabled=True,
        mfa_required=True,
    )


class TestTenantRegistration:
    """Tests for tenant registration"""

    def test_register_tenant_basic(self, tenant_manager):
        """Test basic tenant registration"""
        tenant = tenant_manager.register_tenant(
            name="Test Police Department",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        assert tenant is not None
        assert tenant.name == "Test Police Department"
        assert tenant.tenant_type == TenantType.POLICE_DEPARTMENT
        assert tenant.status == TenantStatus.PENDING
        assert tenant.tenant_id.startswith("tenant-")

    def test_register_tenant_with_profile(self, tenant_manager, sample_profile):
        """Test tenant registration with profile"""
        tenant = tenant_manager.register_tenant(
            name="Test Police Department",
            tenant_type=TenantType.POLICE_DEPARTMENT,
            profile=sample_profile,
        )

        assert tenant is not None
        assert tenant.profile is not None
        assert tenant.profile.display_name == "Test Police Department"
        assert tenant.profile.ori_number == "CA0123456"

    def test_register_tenant_with_policy(self, tenant_manager, sample_policy):
        """Test tenant registration with policy"""
        tenant = tenant_manager.register_tenant(
            name="Test Police Department",
            tenant_type=TenantType.POLICE_DEPARTMENT,
            policy=sample_policy,
        )

        assert tenant is not None
        assert tenant.policy is not None
        assert tenant.policy.data_retention_days == 365
        assert tenant.policy.federation_enabled is True

    def test_register_duplicate_tenant(self, tenant_manager):
        """Test that duplicate tenant names are rejected"""
        tenant_manager.register_tenant(
            name="Test Police Department",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        duplicate = tenant_manager.register_tenant(
            name="Test Police Department",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        assert duplicate is None

    def test_register_tenant_types(self, tenant_manager):
        """Test registration of different tenant types"""
        types = [
            TenantType.CITY,
            TenantType.COUNTY,
            TenantType.POLICE_DEPARTMENT,
            TenantType.SHERIFF_OFFICE,
            TenantType.TASK_FORCE,
            TenantType.FUSION_CENTER,
        ]

        for i, tenant_type in enumerate(types):
            tenant = tenant_manager.register_tenant(
                name=f"Test Tenant {i}",
                tenant_type=tenant_type,
            )
            assert tenant is not None
            assert tenant.tenant_type == tenant_type


class TestTenantLifecycle:
    """Tests for tenant lifecycle management"""

    def test_activate_tenant(self, tenant_manager):
        """Test tenant activation"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        success = tenant_manager.activate_tenant(tenant.tenant_id)
        assert success is True

        updated = tenant_manager.get_tenant(tenant.tenant_id)
        assert updated.status == TenantStatus.ACTIVE

    def test_suspend_tenant(self, tenant_manager):
        """Test tenant suspension"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )
        tenant_manager.activate_tenant(tenant.tenant_id)

        success = tenant_manager.suspend_tenant(tenant.tenant_id, "Policy violation")
        assert success is True

        updated = tenant_manager.get_tenant(tenant.tenant_id)
        assert updated.status == TenantStatus.SUSPENDED

    def test_reactivate_tenant(self, tenant_manager):
        """Test tenant reactivation"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )
        tenant_manager.activate_tenant(tenant.tenant_id)
        tenant_manager.suspend_tenant(tenant.tenant_id, "Test")

        success = tenant_manager.reactivate_tenant(tenant.tenant_id)
        assert success is True

        updated = tenant_manager.get_tenant(tenant.tenant_id)
        assert updated.status == TenantStatus.ACTIVE

    def test_archive_tenant(self, tenant_manager):
        """Test tenant archival"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        success = tenant_manager.archive_tenant(tenant.tenant_id)
        assert success is True

        updated = tenant_manager.get_tenant(tenant.tenant_id)
        assert updated.status == TenantStatus.ARCHIVED


class TestTenantRetrieval:
    """Tests for tenant retrieval"""

    def test_get_tenant(self, tenant_manager):
        """Test getting a tenant by ID"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        retrieved = tenant_manager.get_tenant(tenant.tenant_id)
        assert retrieved is not None
        assert retrieved.tenant_id == tenant.tenant_id

    def test_get_tenant_by_name(self, tenant_manager):
        """Test getting a tenant by name"""
        tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        retrieved = tenant_manager.get_tenant_by_name("Test PD")
        assert retrieved is not None
        assert retrieved.name == "Test PD"

    def test_get_all_tenants(self, tenant_manager):
        """Test getting all tenants"""
        for i in range(5):
            tenant_manager.register_tenant(
                name=f"Test PD {i}",
                tenant_type=TenantType.POLICE_DEPARTMENT,
            )

        tenants = tenant_manager.get_all_tenants()
        assert len(tenants) == 5

    def test_get_tenants_by_type(self, tenant_manager):
        """Test getting tenants by type"""
        tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )
        tenant_manager.register_tenant(
            name="Test SO",
            tenant_type=TenantType.SHERIFF_OFFICE,
        )

        pds = tenant_manager.get_tenants_by_type(TenantType.POLICE_DEPARTMENT)
        assert len(pds) == 1
        assert pds[0].tenant_type == TenantType.POLICE_DEPARTMENT

    def test_get_active_tenants(self, tenant_manager):
        """Test getting active tenants"""
        tenant1 = tenant_manager.register_tenant(
            name="Test PD 1",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )
        tenant2 = tenant_manager.register_tenant(
            name="Test PD 2",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        tenant_manager.activate_tenant(tenant1.tenant_id)

        active = tenant_manager.get_active_tenants()
        assert len(active) == 1
        assert active[0].tenant_id == tenant1.tenant_id


class TestDataSources:
    """Tests for data source management"""

    def test_add_data_source(self, tenant_manager):
        """Test adding a data source"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        data_source = DataSource(
            source_id="ds-001",
            source_type=DataSourceType.CAD,
            name="CAD System",
            endpoint_url="https://cad.testpd.gov/api",
            enabled=True,
        )

        success = tenant_manager.add_data_source(tenant.tenant_id, data_source)
        assert success is True

        sources = tenant_manager.get_data_sources(tenant.tenant_id)
        assert len(sources) == 1
        assert sources[0].source_type == DataSourceType.CAD

    def test_remove_data_source(self, tenant_manager):
        """Test removing a data source"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        data_source = DataSource(
            source_id="ds-001",
            source_type=DataSourceType.CAD,
            name="CAD System",
        )
        tenant_manager.add_data_source(tenant.tenant_id, data_source)

        success = tenant_manager.remove_data_source(tenant.tenant_id, "ds-001")
        assert success is True

        sources = tenant_manager.get_data_sources(tenant.tenant_id)
        assert len(sources) == 0


class TestIntegrations:
    """Tests for integration management"""

    def test_add_integration(self, tenant_manager):
        """Test adding an integration"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        integration = IntegrationConfig(
            integration_id="int-001",
            name="NCIC",
            integration_type="federal",
            status=IntegrationStatus.CONFIGURED,
            endpoint_url="https://ncic.fbi.gov/api",
            enabled=True,
        )

        success = tenant_manager.add_integration(tenant.tenant_id, integration)
        assert success is True

        integrations = tenant_manager.get_integrations(tenant.tenant_id)
        assert len(integrations) == 1
        assert integrations[0].name == "NCIC"

    def test_update_integration_status(self, tenant_manager):
        """Test updating integration status"""
        tenant = tenant_manager.register_tenant(
            name="Test PD",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        integration = IntegrationConfig(
            integration_id="int-001",
            name="NCIC",
            integration_type="federal",
            status=IntegrationStatus.CONFIGURED,
        )
        tenant_manager.add_integration(tenant.tenant_id, integration)

        success = tenant_manager.update_integration_status(
            tenant.tenant_id, "int-001", IntegrationStatus.CONNECTED
        )
        assert success is True


class TestFederationPartners:
    """Tests for federation partnership management"""

    def test_add_federation_partner(self, tenant_manager):
        """Test adding a federation partner"""
        tenant1 = tenant_manager.register_tenant(
            name="Test PD 1",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )
        tenant2 = tenant_manager.register_tenant(
            name="Test PD 2",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        success = tenant_manager.add_federation_partner(
            tenant1.tenant_id, tenant2.tenant_id
        )
        assert success is True

        partners = tenant_manager.get_federation_partners(tenant1.tenant_id)
        assert tenant2.tenant_id in partners

    def test_remove_federation_partner(self, tenant_manager):
        """Test removing a federation partner"""
        tenant1 = tenant_manager.register_tenant(
            name="Test PD 1",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )
        tenant2 = tenant_manager.register_tenant(
            name="Test PD 2",
            tenant_type=TenantType.POLICE_DEPARTMENT,
        )

        tenant_manager.add_federation_partner(tenant1.tenant_id, tenant2.tenant_id)

        success = tenant_manager.remove_federation_partner(
            tenant1.tenant_id, tenant2.tenant_id
        )
        assert success is True

        partners = tenant_manager.get_federation_partners(tenant1.tenant_id)
        assert tenant2.tenant_id not in partners


class TestMetrics:
    """Tests for tenant metrics"""

    def test_get_metrics(self, tenant_manager):
        """Test getting tenant metrics"""
        for i in range(3):
            tenant = tenant_manager.register_tenant(
                name=f"Test PD {i}",
                tenant_type=TenantType.POLICE_DEPARTMENT,
            )
            if i < 2:
                tenant_manager.activate_tenant(tenant.tenant_id)

        metrics = tenant_manager.get_metrics()
        assert metrics["total_tenants"] == 3
        assert metrics["active_tenants"] == 2
