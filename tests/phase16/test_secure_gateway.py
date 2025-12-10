"""
Tests for SecureAccessGateway

Tests ABAC policies, access evaluation, encryption, domain separation,
clearance filtering, and audit logging.
"""

import pytest
from datetime import datetime

from app.fusion_cloud.secure_gateway import (
    SecureAccessGateway,
    AccessPolicy,
    AccessDecision,
    AttributeBasedAccess,
    ClearanceFilter,
    TenantEncryption,
    DomainSeparation,
    DataSensitivity,
    AccessRequest,
    AccessResult,
    ClearanceLevel,
    AttributeType,
    EncryptionAlgorithm,
)


@pytest.fixture
def secure_gateway():
    """Create a fresh SecureAccessGateway for each test"""
    return SecureAccessGateway()


class TestTenantEncryption:
    """Tests for tenant encryption configuration"""

    def test_configure_tenant_encryption(self, secure_gateway):
        """Test configuring tenant encryption"""
        encryption = secure_gateway.configure_tenant_encryption(
            tenant_id="tenant-001",
            algorithm=EncryptionAlgorithm.AES_256_GCM,
        )

        assert encryption is not None
        assert encryption.tenant_id == "tenant-001"
        assert encryption.algorithm == EncryptionAlgorithm.AES_256_GCM

    def test_get_tenant_encryption(self, secure_gateway):
        """Test getting tenant encryption config"""
        secure_gateway.configure_tenant_encryption(
            tenant_id="tenant-001",
            algorithm=EncryptionAlgorithm.AES_256_GCM,
        )

        encryption = secure_gateway.get_tenant_encryption("tenant-001")
        assert encryption is not None
        assert encryption.tenant_id == "tenant-001"

    def test_rotate_encryption_key(self, secure_gateway):
        """Test rotating encryption key"""
        secure_gateway.configure_tenant_encryption(
            tenant_id="tenant-001",
            algorithm=EncryptionAlgorithm.AES_256_GCM,
        )

        success = secure_gateway.rotate_encryption_key("tenant-001")
        assert success is True

        encryption = secure_gateway.get_tenant_encryption("tenant-001")
        assert encryption.key_version > 1


class TestDomainSeparation:
    """Tests for domain separation configuration"""

    def test_configure_domain_separation(self, secure_gateway):
        """Test configuring domain separation"""
        domain = secure_gateway.configure_domain_separation(
            tenant_id="tenant-001",
            domain_name="metro-pd-domain",
            isolation_level="strict",
        )

        assert domain is not None
        assert domain.tenant_id == "tenant-001"
        assert domain.domain_name == "metro-pd-domain"

    def test_get_domain_separation(self, secure_gateway):
        """Test getting domain separation config"""
        secure_gateway.configure_domain_separation(
            tenant_id="tenant-001",
            domain_name="metro-pd-domain",
            isolation_level="strict",
        )

        domain = secure_gateway.get_domain_separation("tenant-001")
        assert domain is not None
        assert domain.domain_name == "metro-pd-domain"

    def test_add_allowed_domain(self, secure_gateway):
        """Test adding an allowed domain for cross-domain access"""
        secure_gateway.configure_domain_separation(
            tenant_id="tenant-001",
            domain_name="metro-pd-domain",
            isolation_level="moderate",
        )

        success = secure_gateway.add_allowed_domain("tenant-001", "county-so-domain")
        assert success is True


class TestAccessPolicies:
    """Tests for access policy management"""

    def test_create_policy(self, secure_gateway):
        """Test creating an access policy"""
        policy = secure_gateway.create_policy(
            name="Read LPR Data",
            resource_type="lpr_data",
            action="read",
            effect="allow",
            conditions={
                "user.clearance_level": {"gte": "law_enforcement_sensitive"},
                "user.tenant_id": {"in": "resource.shared_with_tenants"},
            },
        )

        assert policy is not None
        assert policy.name == "Read LPR Data"
        assert policy.effect == "allow"

    def test_get_policy(self, secure_gateway):
        """Test getting a policy by ID"""
        policy = secure_gateway.create_policy(
            name="Test Policy",
            resource_type="test_resource",
            action="read",
            effect="allow",
        )

        retrieved = secure_gateway.get_policy(policy.policy_id)
        assert retrieved is not None
        assert retrieved.policy_id == policy.policy_id

    def test_get_policies_for_resource(self, secure_gateway):
        """Test getting policies for a resource type"""
        secure_gateway.create_policy(
            name="Policy 1",
            resource_type="lpr_data",
            action="read",
            effect="allow",
        )
        secure_gateway.create_policy(
            name="Policy 2",
            resource_type="lpr_data",
            action="write",
            effect="allow",
        )

        policies = secure_gateway.get_policies_for_resource("lpr_data")
        assert len(policies) == 2

    def test_update_policy(self, secure_gateway):
        """Test updating a policy"""
        policy = secure_gateway.create_policy(
            name="Test Policy",
            resource_type="test_resource",
            action="read",
            effect="allow",
        )

        success = secure_gateway.update_policy(
            policy_id=policy.policy_id,
            effect="deny",
        )
        assert success is True

        updated = secure_gateway.get_policy(policy.policy_id)
        assert updated.effect == "deny"

    def test_delete_policy(self, secure_gateway):
        """Test deleting a policy"""
        policy = secure_gateway.create_policy(
            name="Test Policy",
            resource_type="test_resource",
            action="read",
            effect="allow",
        )

        success = secure_gateway.delete_policy(policy.policy_id)
        assert success is True


class TestABAC:
    """Tests for Attribute-Based Access Control"""

    def test_configure_abac(self, secure_gateway):
        """Test configuring ABAC for a tenant"""
        abac = secure_gateway.configure_abac(
            tenant_id="tenant-001",
            attributes=[
                {
                    "name": "clearance_level",
                    "type": AttributeType.STRING,
                    "required": True,
                },
                {
                    "name": "jurisdiction",
                    "type": AttributeType.STRING,
                    "required": True,
                },
                {
                    "name": "role",
                    "type": AttributeType.STRING,
                    "required": False,
                },
            ],
        )

        assert abac is not None
        assert abac.tenant_id == "tenant-001"
        assert len(abac.attributes) == 3

    def test_get_abac_config(self, secure_gateway):
        """Test getting ABAC configuration"""
        secure_gateway.configure_abac(
            tenant_id="tenant-001",
            attributes=[
                {
                    "name": "clearance_level",
                    "type": AttributeType.STRING,
                    "required": True,
                },
            ],
        )

        abac = secure_gateway.get_abac_config("tenant-001")
        assert abac is not None
        assert abac.tenant_id == "tenant-001"


class TestAccessEvaluation:
    """Tests for access evaluation"""

    def test_evaluate_access_allow(self, secure_gateway):
        """Test access evaluation that allows"""
        secure_gateway.create_policy(
            name="Allow Read",
            resource_type="lpr_data",
            action="read",
            effect="allow",
            conditions={
                "user.clearance_level": {"eq": "law_enforcement_sensitive"},
            },
        )

        request = AccessRequest(
            request_id="req-001",
            user_id="user-001",
            tenant_id="tenant-001",
            resource_type="lpr_data",
            resource_id="lpr-001",
            action="read",
            user_attributes={
                "clearance_level": "law_enforcement_sensitive",
            },
        )

        result = secure_gateway.evaluate_access(request)
        assert result is not None
        assert result.decision == AccessDecision.ALLOW

    def test_evaluate_access_deny(self, secure_gateway):
        """Test access evaluation that denies"""
        secure_gateway.create_policy(
            name="Deny Read",
            resource_type="secret_data",
            action="read",
            effect="deny",
        )

        request = AccessRequest(
            request_id="req-001",
            user_id="user-001",
            tenant_id="tenant-001",
            resource_type="secret_data",
            resource_id="secret-001",
            action="read",
            user_attributes={},
        )

        result = secure_gateway.evaluate_access(request)
        assert result is not None
        assert result.decision == AccessDecision.DENY

    def test_evaluate_access_partial(self, secure_gateway):
        """Test access evaluation with partial access"""
        secure_gateway.create_policy(
            name="Partial Read",
            resource_type="investigation",
            action="read",
            effect="allow_partial",
            conditions={
                "user.clearance_level": {"lt": "confidential"},
            },
            redaction_fields=["suspect_ssn", "witness_names"],
        )

        request = AccessRequest(
            request_id="req-001",
            user_id="user-001",
            tenant_id="tenant-001",
            resource_type="investigation",
            resource_id="inv-001",
            action="read",
            user_attributes={
                "clearance_level": "law_enforcement_sensitive",
            },
        )

        result = secure_gateway.evaluate_access(request)
        assert result is not None
        assert result.decision == AccessDecision.ALLOW_PARTIAL


class TestClearanceFiltering:
    """Tests for clearance-based filtering"""

    def test_configure_clearance_filter(self, secure_gateway):
        """Test configuring clearance filter"""
        filter_config = secure_gateway.configure_clearance_filter(
            tenant_id="tenant-001",
            default_clearance=ClearanceLevel.LAW_ENFORCEMENT_SENSITIVE,
            clearance_hierarchy=[
                ClearanceLevel.UNCLASSIFIED,
                ClearanceLevel.LAW_ENFORCEMENT_SENSITIVE,
                ClearanceLevel.OFFICIAL_USE_ONLY,
                ClearanceLevel.CONFIDENTIAL,
                ClearanceLevel.SECRET,
            ],
        )

        assert filter_config is not None
        assert filter_config.tenant_id == "tenant-001"

    def test_filter_by_clearance(self, secure_gateway):
        """Test filtering data by clearance level"""
        secure_gateway.configure_clearance_filter(
            tenant_id="tenant-001",
            default_clearance=ClearanceLevel.LAW_ENFORCEMENT_SENSITIVE,
            clearance_hierarchy=[
                ClearanceLevel.UNCLASSIFIED,
                ClearanceLevel.LAW_ENFORCEMENT_SENSITIVE,
                ClearanceLevel.CONFIDENTIAL,
            ],
        )

        data = [
            {"id": "1", "clearance": ClearanceLevel.UNCLASSIFIED},
            {"id": "2", "clearance": ClearanceLevel.LAW_ENFORCEMENT_SENSITIVE},
            {"id": "3", "clearance": ClearanceLevel.CONFIDENTIAL},
        ]

        filtered = secure_gateway.filter_by_clearance(
            tenant_id="tenant-001",
            data=data,
            user_clearance=ClearanceLevel.LAW_ENFORCEMENT_SENSITIVE,
        )
        assert len(filtered) == 2


class TestDataRedaction:
    """Tests for data redaction"""

    def test_apply_data_redaction(self, secure_gateway):
        """Test applying data redaction"""
        data = {
            "case_number": "2024-001",
            "suspect_name": "John Doe",
            "suspect_ssn": "123-45-6789",
            "witness_names": ["Jane Smith", "Bob Johnson"],
            "summary": "Case summary",
        }

        redacted = secure_gateway.apply_data_redaction(
            data=data,
            redaction_fields=["suspect_ssn", "witness_names"],
        )

        assert redacted["case_number"] == "2024-001"
        assert redacted["suspect_ssn"] == "[REDACTED]"
        assert redacted["witness_names"] == "[REDACTED]"


class TestAuditLogging:
    """Tests for audit logging"""

    def test_log_access_request(self, secure_gateway):
        """Test logging an access request"""
        request = AccessRequest(
            request_id="req-001",
            user_id="user-001",
            tenant_id="tenant-001",
            resource_type="lpr_data",
            resource_id="lpr-001",
            action="read",
            user_attributes={},
        )

        result = AccessResult(
            request_id="req-001",
            decision=AccessDecision.ALLOW,
            policy_ids=["policy-001"],
        )

        entry = secure_gateway.log_access_request(request, result)
        assert entry is not None
        assert entry.request_id == "req-001"
        assert entry.decision == AccessDecision.ALLOW

    def test_get_audit_log(self, secure_gateway):
        """Test getting audit log"""
        request = AccessRequest(
            request_id="req-001",
            user_id="user-001",
            tenant_id="tenant-001",
            resource_type="lpr_data",
            resource_id="lpr-001",
            action="read",
            user_attributes={},
        )
        result = AccessResult(
            request_id="req-001",
            decision=AccessDecision.ALLOW,
            policy_ids=[],
        )
        secure_gateway.log_access_request(request, result)

        log = secure_gateway.get_audit_log(tenant_id="tenant-001")
        assert len(log) == 1

    def test_get_audit_log_for_user(self, secure_gateway):
        """Test getting audit log for a user"""
        for i in range(3):
            request = AccessRequest(
                request_id=f"req-{i}",
                user_id="user-001",
                tenant_id="tenant-001",
                resource_type="lpr_data",
                resource_id=f"lpr-{i}",
                action="read",
                user_attributes={},
            )
            result = AccessResult(
                request_id=f"req-{i}",
                decision=AccessDecision.ALLOW,
                policy_ids=[],
            )
            secure_gateway.log_access_request(request, result)

        log = secure_gateway.get_audit_log(tenant_id="tenant-001", user_id="user-001")
        assert len(log) == 3

    def test_verify_audit_chain(self, secure_gateway):
        """Test verifying audit chain integrity"""
        for i in range(5):
            request = AccessRequest(
                request_id=f"req-{i}",
                user_id="user-001",
                tenant_id="tenant-001",
                resource_type="lpr_data",
                resource_id=f"lpr-{i}",
                action="read",
                user_attributes={},
            )
            result = AccessResult(
                request_id=f"req-{i}",
                decision=AccessDecision.ALLOW,
                policy_ids=[],
            )
            secure_gateway.log_access_request(request, result)

        is_valid = secure_gateway.verify_audit_chain("tenant-001")
        assert is_valid is True


class TestMetrics:
    """Tests for security metrics"""

    def test_get_metrics(self, secure_gateway):
        """Test getting security metrics"""
        secure_gateway.create_policy(
            name="Test Policy",
            resource_type="test",
            action="read",
            effect="allow",
        )

        request = AccessRequest(
            request_id="req-001",
            user_id="user-001",
            tenant_id="tenant-001",
            resource_type="test",
            resource_id="test-001",
            action="read",
            user_attributes={},
        )
        result = AccessResult(
            request_id="req-001",
            decision=AccessDecision.ALLOW,
            policy_ids=[],
        )
        secure_gateway.log_access_request(request, result)

        metrics = secure_gateway.get_metrics()
        assert metrics["total_policies"] == 1
        assert metrics["total_access_requests"] == 1
