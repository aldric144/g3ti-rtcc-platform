"""
Tests for FederationLayer

Tests cross-agency data sharing, permissions, subscriptions,
and forwarding rules.
"""

import pytest
from datetime import datetime, timedelta

from app.fusion_cloud.federation import (
    FederationLayer,
    FederatedData,
    FederatedDataType,
    DataClassification,
    SensitivityLevel,
    ClearanceLevel,
    JurisdictionTag,
    RetentionPolicy,
    FederationSubscription,
    FederationPermission,
    SubscriptionStatus,
)


@pytest.fixture
def federation_layer():
    """Create a fresh FederationLayer for each test"""
    return FederationLayer()


class TestDataPublishing:
    """Tests for federated data publishing"""

    def test_publish_data_basic(self, federation_layer):
        """Test basic data publishing"""
        data = federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.LPR_HIT,
            title="Hot Vehicle Hit",
            payload={"plate": "ABC123", "vehicle": "Black BMW"},
        )

        assert data is not None
        assert data.data_type == FederatedDataType.LPR_HIT
        assert data.source_tenant_id == "tenant-001"
        assert data.title == "Hot Vehicle Hit"

    def test_publish_data_with_classification(self, federation_layer):
        """Test data publishing with classification"""
        data = federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.INVESTIGATION,
            title="Active Investigation",
            payload={"case_number": "2024-001"},
            classification=DataClassification.CONFIDENTIAL,
            sensitivity=SensitivityLevel.HIGHLY_RESTRICTED,
        )

        assert data is not None
        assert data.classification == DataClassification.CONFIDENTIAL
        assert data.sensitivity == SensitivityLevel.HIGHLY_RESTRICTED

    def test_publish_data_with_sharing(self, federation_layer):
        """Test data publishing with tenant sharing"""
        data = federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.BOLO,
            title="BOLO - Armed Suspect",
            payload={"suspect": "John Doe"},
            share_with_tenants=["tenant-002", "tenant-003"],
        )

        assert data is not None
        assert "tenant-002" in data.shared_with_tenants
        assert "tenant-003" in data.shared_with_tenants

    def test_publish_data_with_expiration(self, federation_layer):
        """Test data publishing with expiration"""
        data = federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.ALERT,
            title="Time-Sensitive Alert",
            payload={"message": "Alert"},
            expires_in_days=7,
        )

        assert data is not None
        assert data.expires_at is not None
        assert data.expires_at > datetime.utcnow()


class TestDataRetrieval:
    """Tests for federated data retrieval"""

    def test_get_data(self, federation_layer):
        """Test getting data by ID"""
        data = federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.LPR_HIT,
            title="Test Hit",
            payload={},
        )

        retrieved = federation_layer.get_data(data.data_id)
        assert retrieved is not None
        assert retrieved.data_id == data.data_id

    def test_get_data_for_tenant(self, federation_layer):
        """Test getting data for a tenant"""
        federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.LPR_HIT,
            title="Hit 1",
            payload={},
            share_with_tenants=["tenant-002"],
        )
        federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.BOLO,
            title="BOLO 1",
            payload={},
            share_with_tenants=["tenant-002"],
        )

        data = federation_layer.get_data_for_tenant("tenant-002")
        assert len(data) == 2

    def test_get_data_for_tenant_by_type(self, federation_layer):
        """Test getting data for a tenant filtered by type"""
        federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.LPR_HIT,
            title="Hit 1",
            payload={},
            share_with_tenants=["tenant-002"],
        )
        federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.BOLO,
            title="BOLO 1",
            payload={},
            share_with_tenants=["tenant-002"],
        )

        data = federation_layer.get_data_for_tenant(
            "tenant-002", data_types=[FederatedDataType.LPR_HIT]
        )
        assert len(data) == 1
        assert data[0].data_type == FederatedDataType.LPR_HIT


class TestDataSharing:
    """Tests for data sharing"""

    def test_share_data_with_tenant(self, federation_layer):
        """Test sharing data with a tenant"""
        data = federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.LPR_HIT,
            title="Test Hit",
            payload={},
        )

        success = federation_layer.share_data_with_tenant(data.data_id, "tenant-002")
        assert success is True

        updated = federation_layer.get_data(data.data_id)
        assert "tenant-002" in updated.shared_with_tenants

    def test_revoke_data_sharing(self, federation_layer):
        """Test revoking data sharing"""
        data = federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.LPR_HIT,
            title="Test Hit",
            payload={},
            share_with_tenants=["tenant-002"],
        )

        success = federation_layer.revoke_data_sharing(data.data_id, "tenant-002")
        assert success is True

        updated = federation_layer.get_data(data.data_id)
        assert "tenant-002" not in updated.shared_with_tenants


class TestPermissions:
    """Tests for federation permissions"""

    def test_create_permission(self, federation_layer):
        """Test creating a permission"""
        permission = federation_layer.create_permission(
            source_tenant_id="tenant-001",
            target_tenant_id="tenant-002",
            data_types=[FederatedDataType.LPR_HIT, FederatedDataType.BOLO],
            max_classification=DataClassification.LAW_ENFORCEMENT_SENSITIVE,
        )

        assert permission is not None
        assert permission.source_tenant_id == "tenant-001"
        assert permission.target_tenant_id == "tenant-002"
        assert FederatedDataType.LPR_HIT in permission.data_types

    def test_revoke_permission(self, federation_layer):
        """Test revoking a permission"""
        permission = federation_layer.create_permission(
            source_tenant_id="tenant-001",
            target_tenant_id="tenant-002",
            data_types=[FederatedDataType.LPR_HIT],
        )

        success = federation_layer.revoke_permission(permission.permission_id)
        assert success is True

    def test_get_permissions_for_tenant(self, federation_layer):
        """Test getting permissions for a tenant"""
        federation_layer.create_permission(
            source_tenant_id="tenant-001",
            target_tenant_id="tenant-002",
            data_types=[FederatedDataType.LPR_HIT],
        )
        federation_layer.create_permission(
            source_tenant_id="tenant-001",
            target_tenant_id="tenant-003",
            data_types=[FederatedDataType.BOLO],
        )

        permissions = federation_layer.get_permissions_for_tenant("tenant-001")
        assert len(permissions) == 2

    def test_check_permission(self, federation_layer):
        """Test checking permission"""
        federation_layer.create_permission(
            source_tenant_id="tenant-001",
            target_tenant_id="tenant-002",
            data_types=[FederatedDataType.LPR_HIT],
            max_classification=DataClassification.LAW_ENFORCEMENT_SENSITIVE,
        )

        has_permission = federation_layer.check_permission(
            source_tenant_id="tenant-001",
            target_tenant_id="tenant-002",
            data_type=FederatedDataType.LPR_HIT,
            classification=DataClassification.LAW_ENFORCEMENT_SENSITIVE,
        )
        assert has_permission is True

        no_permission = federation_layer.check_permission(
            source_tenant_id="tenant-001",
            target_tenant_id="tenant-002",
            data_type=FederatedDataType.INVESTIGATION,
            classification=DataClassification.LAW_ENFORCEMENT_SENSITIVE,
        )
        assert no_permission is False


class TestSubscriptions:
    """Tests for federation subscriptions"""

    def test_create_subscription(self, federation_layer):
        """Test creating a subscription"""
        subscription = federation_layer.create_subscription(
            subscriber_tenant_id="tenant-002",
            publisher_tenant_id="tenant-001",
            data_types=[FederatedDataType.LPR_HIT, FederatedDataType.BOLO],
        )

        assert subscription is not None
        assert subscription.subscriber_tenant_id == "tenant-002"
        assert subscription.publisher_tenant_id == "tenant-001"
        assert subscription.status == SubscriptionStatus.PENDING

    def test_activate_subscription(self, federation_layer):
        """Test activating a subscription"""
        subscription = federation_layer.create_subscription(
            subscriber_tenant_id="tenant-002",
            publisher_tenant_id="tenant-001",
            data_types=[FederatedDataType.LPR_HIT],
        )

        success = federation_layer.activate_subscription(subscription.subscription_id)
        assert success is True

        subscriptions = federation_layer.get_active_subscriptions()
        assert len(subscriptions) == 1

    def test_pause_subscription(self, federation_layer):
        """Test pausing a subscription"""
        subscription = federation_layer.create_subscription(
            subscriber_tenant_id="tenant-002",
            publisher_tenant_id="tenant-001",
            data_types=[FederatedDataType.LPR_HIT],
        )
        federation_layer.activate_subscription(subscription.subscription_id)

        success = federation_layer.pause_subscription(subscription.subscription_id)
        assert success is True

    def test_get_subscriptions_for_tenant(self, federation_layer):
        """Test getting subscriptions for a tenant"""
        federation_layer.create_subscription(
            subscriber_tenant_id="tenant-002",
            publisher_tenant_id="tenant-001",
            data_types=[FederatedDataType.LPR_HIT],
        )

        subscriptions = federation_layer.get_subscriptions_for_tenant("tenant-002")
        assert len(subscriptions) == 1


class TestJurisdictions:
    """Tests for jurisdiction management"""

    def test_register_jurisdiction(self, federation_layer):
        """Test registering a jurisdiction"""
        jurisdiction = federation_layer.register_jurisdiction(
            jurisdiction_code="CA-METRO",
            jurisdiction_name="Metro City",
            jurisdiction_type="city",
            state="CA",
            city="Metro City",
        )

        assert jurisdiction is not None
        assert jurisdiction.jurisdiction_code == "CA-METRO"

    def test_get_jurisdiction(self, federation_layer):
        """Test getting a jurisdiction"""
        federation_layer.register_jurisdiction(
            jurisdiction_code="CA-METRO",
            jurisdiction_name="Metro City",
            jurisdiction_type="city",
            state="CA",
        )

        jurisdiction = federation_layer.get_jurisdiction("CA-METRO")
        assert jurisdiction is not None
        assert jurisdiction.jurisdiction_name == "Metro City"


class TestRetentionPolicies:
    """Tests for retention policy management"""

    def test_create_retention_policy(self, federation_layer):
        """Test creating a retention policy"""
        policy = federation_layer.create_retention_policy(
            name="Standard Retention",
            retention_days=365,
            auto_archive=True,
            archive_after_days=180,
        )

        assert policy is not None
        assert policy.retention_days == 365
        assert policy.auto_archive is True

    def test_get_retention_policy(self, federation_layer):
        """Test getting a retention policy"""
        policy = federation_layer.create_retention_policy(
            name="Standard Retention",
            retention_days=365,
        )

        retrieved = federation_layer.get_retention_policy(policy.policy_id)
        assert retrieved is not None
        assert retrieved.name == "Standard Retention"


class TestMetrics:
    """Tests for federation metrics"""

    def test_get_metrics(self, federation_layer):
        """Test getting federation metrics"""
        federation_layer.publish_data(
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            data_type=FederatedDataType.LPR_HIT,
            title="Test",
            payload={},
        )
        federation_layer.create_subscription(
            subscriber_tenant_id="tenant-002",
            publisher_tenant_id="tenant-001",
            data_types=[FederatedDataType.LPR_HIT],
        )

        metrics = federation_layer.get_metrics()
        assert metrics["total_data_items"] == 1
        assert metrics["total_subscriptions"] == 1
