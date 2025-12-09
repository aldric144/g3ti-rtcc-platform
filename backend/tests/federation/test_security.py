"""
Tests for Zero Trust Security & Data Segregation
Phase 10: Row-level access, query-time masking, and audit logging tests
"""

from datetime import datetime, timedelta

from app.federation.security import (
    AccessDecision,
    AccessRequest,
    AuditEventType,
    FederatedAuditEntry,
    MaskingRule,
    RowLevelAccessRule,
    SecurityLevel,
    ZeroTrustSecurityManager,
)


class TestRowLevelAccessRule:
    """Tests for RowLevelAccessRule"""

    def test_create_rule(self):
        """Test creating row-level access rule"""
        rule = RowLevelAccessRule(
            rule_id="rule-1",
            agency_id="agency-1",
            resource_type="person",
            conditions={"jurisdiction": "local"},
            allowed_fields=["name", "dob", "address"],
            denied_fields=["ssn"],
        )

        assert rule.id == "rule-1"
        assert rule.agency_id == "agency-1"
        assert "ssn" in rule.denied_fields
        assert rule.is_active is True


class TestMaskingRule:
    """Tests for MaskingRule"""

    def test_create_masking_rule(self):
        """Test creating masking rule"""
        rule = MaskingRule(
            rule_id="mask-1",
            field_name="ssn",
            resource_type="person",
            masking_type="partial",
            applies_to_agencies=["agency-2", "agency-3"],
            exceptions=["agency-1"],
        )

        assert rule.id == "mask-1"
        assert rule.field_name == "ssn"
        assert "agency-1" in rule.exceptions


class TestZeroTrustSecurityManager:
    """Tests for ZeroTrustSecurityManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ZeroTrustSecurityManager()

    def test_create_data_domain(self):
        """Test creating data domain for agency"""
        domain = self.manager.create_data_domain(
            agency_id="agency-1",
            domain_name="Agency 1 Domain",
            security_level=SecurityLevel.LAW_ENFORCEMENT_SENSITIVE,
            allowed_data_types=["incidents", "persons", "vehicles"],
            encryption_required=True,
            audit_all_access=True,
        )

        assert domain is not None
        assert domain.agency_id == "agency-1"
        assert domain.encryption_required is True

    def test_get_data_domain(self):
        """Test getting data domain"""
        self.manager.create_data_domain(
            agency_id="agency-1",
            domain_name="Test Domain",
            security_level=SecurityLevel.CONFIDENTIAL,
            allowed_data_types=["incidents"],
        )

        domain = self.manager.get_data_domain("agency-1")
        assert domain is not None
        assert domain.agency_id == "agency-1"

    def test_create_row_level_rule(self):
        """Test creating row-level access rule"""
        rule = self.manager.create_row_level_rule(
            agency_id="agency-1",
            resource_type="person",
            conditions={"jurisdiction": "local"},
            allowed_fields=["name", "address"],
            denied_fields=["ssn", "dob"],
        )

        assert rule is not None
        assert rule.id in self.manager.row_level_rules

    def test_create_masking_rule(self):
        """Test creating masking rule"""
        rule = self.manager.create_masking_rule(
            field_name="ssn",
            resource_type="person",
            masking_type="partial",
            applies_to_agencies=["agency-2"],
        )

        assert rule is not None
        assert rule.id in self.manager.masking_rules

    def test_grant_agency_permission(self):
        """Test granting agency permission"""
        self.manager.grant_agency_permission(
            requesting_agency="agency-2",
            target_agency="agency-1",
            resource_types=["incidents", "persons"],
            granted_by="admin",
        )

        permissions = self.manager.agency_permissions.get("agency-2", {})
        assert "agency-1" in permissions
        assert "incidents" in permissions["agency-1"]

    def test_revoke_agency_permission(self):
        """Test revoking agency permission"""
        self.manager.grant_agency_permission(
            requesting_agency="agency-2",
            target_agency="agency-1",
            resource_types=["incidents"],
            granted_by="admin",
        )

        self.manager.revoke_agency_permission(
            requesting_agency="agency-2",
            target_agency="agency-1",
            revoked_by="admin",
        )

        permissions = self.manager.agency_permissions.get("agency-2", {})
        assert "agency-1" not in permissions

    def test_evaluate_access_allowed(self):
        """Test access evaluation - allowed"""
        self.manager.grant_agency_permission(
            requesting_agency="agency-2",
            target_agency="agency-1",
            resource_types=["incidents"],
            granted_by="admin",
        )

        request = AccessRequest(
            requesting_agency="agency-2",
            requesting_user="user-2",
            target_agency="agency-1",
            resource_type="incidents",
            resource_id="incident-123",
            action="read",
            fields_requested=["incident_number", "type", "location"],
        )

        response = self.manager.evaluate_access(request)
        assert response.decision in [AccessDecision.ALLOW, AccessDecision.ALLOW_PARTIAL, AccessDecision.ALLOW_MASKED]

    def test_evaluate_access_denied_no_permission(self):
        """Test access evaluation - denied due to no permission"""
        request = AccessRequest(
            requesting_agency="agency-2",
            requesting_user="user-2",
            target_agency="agency-1",
            resource_type="incidents",
            resource_id="incident-123",
            action="read",
        )

        response = self.manager.evaluate_access(request)
        assert response.decision == AccessDecision.DENY

    def test_evaluate_access_denied_revoked_user(self):
        """Test access evaluation - denied due to revoked user"""
        self.manager.grant_agency_permission(
            requesting_agency="agency-2",
            target_agency="agency-1",
            resource_types=["incidents"],
            granted_by="admin",
        )

        self.manager.revoke_user_access(
            agency_id="agency-2",
            user_id="user-2",
            revoked_by="admin",
            reason="Policy violation",
        )

        request = AccessRequest(
            requesting_agency="agency-2",
            requesting_user="user-2",
            target_agency="agency-1",
            resource_type="incidents",
            resource_id="incident-123",
            action="read",
        )

        response = self.manager.evaluate_access(request)
        assert response.decision == AccessDecision.DENY

    def test_restore_user_access(self):
        """Test restoring user access"""
        self.manager.revoke_user_access(
            agency_id="agency-1",
            user_id="user-1",
            revoked_by="admin",
            reason="Test",
        )

        self.manager.restore_user_access(
            agency_id="agency-1",
            user_id="user-1",
            restored_by="admin",
        )

        assert "user-1" not in self.manager.revoked_access.get("agency-1", [])

    def test_apply_masking(self):
        """Test applying masking to data"""
        data = {
            "name": "John Doe",
            "ssn": "123-45-6789",
            "phone": "555-123-4567",
            "address": "123 Main St",
        }

        masked = self.manager.apply_masking(data, ["ssn", "phone"])

        assert masked["name"] == "John Doe"  # Not masked
        assert masked["ssn"] != "123-45-6789"  # Masked
        assert masked["phone"] != "555-123-4567"  # Masked

    def test_log_data_query(self):
        """Test logging data query"""
        entry = self.manager.log_data_query(
            agency_id="agency-1",
            user_id="user-1",
            user_name="Officer Smith",
            query_text="SELECT * FROM persons WHERE name = 'John'",
            resource_type="person",
            result_count=5,
            ip_address="192.168.1.100",
        )

        assert entry is not None
        assert entry.event_type == AuditEventType.DATA_QUERY
        assert len(self.manager.audit_log) == 1

    def test_log_data_export(self):
        """Test logging data export"""
        entry = self.manager.log_data_export(
            agency_id="agency-1",
            user_id="user-1",
            user_name="Detective Jones",
            resource_type="incident",
            record_count=100,
            export_format="csv",
        )

        assert entry is not None
        assert entry.event_type == AuditEventType.DATA_EXPORT

    def test_log_data_share(self):
        """Test logging data share"""
        entry = self.manager.log_data_share(
            from_agency="agency-1",
            to_agency="agency-2",
            user_id="user-1",
            user_name="Analyst Chen",
            resource_type="intelligence",
            record_count=10,
        )

        assert entry is not None
        assert entry.event_type == AuditEventType.DATA_SHARE

    def test_get_audit_log(self):
        """Test getting audit log with filters"""
        self.manager.log_data_query(
            agency_id="agency-1",
            user_id="user-1",
            user_name="User 1",
            query_text="query 1",
            resource_type="person",
            result_count=5,
        )
        self.manager.log_data_query(
            agency_id="agency-2",
            user_id="user-2",
            user_name="User 2",
            query_text="query 2",
            resource_type="person",
            result_count=3,
        )

        all_entries = self.manager.get_audit_log()
        assert len(all_entries) == 2

        agency_1_entries = self.manager.get_audit_log(agency_id="agency-1")
        assert len(agency_1_entries) == 1

    def test_get_compliance_report(self):
        """Test generating compliance report"""
        # Add some audit entries
        self.manager.log_data_query(
            agency_id="agency-1",
            user_id="user-1",
            user_name="User 1",
            query_text="query",
            resource_type="person",
            result_count=5,
        )
        self.manager.log_data_export(
            agency_id="agency-1",
            user_id="user-1",
            user_name="User 1",
            resource_type="incident",
            record_count=10,
            export_format="csv",
        )

        report = self.manager.get_compliance_report(
            agency_id="agency-1",
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=1),
        )

        assert report is not None
        assert report["agency_id"] == "agency-1"
        assert "statistics" in report
        assert report["statistics"]["total_events"] == 2

    def test_cleanup_expired_logs(self):
        """Test cleaning up expired audit logs"""
        # Create an entry with past retention date
        entry = FederatedAuditEntry(
            event_type=AuditEventType.DATA_ACCESS,
            agency_id="agency-1",
            user_id="user-1",
            user_name="User 1",
            resource_type="person",
            resource_id="person-1",
            action="read",
            details={},
        )
        # Manually set retention to past
        entry.retention_until = datetime.utcnow() - timedelta(days=1)
        self.manager.audit_log.append(entry)

        # Create a valid entry
        self.manager.log_data_query(
            agency_id="agency-1",
            user_id="user-1",
            user_name="User 1",
            query_text="query",
            resource_type="person",
            result_count=5,
        )

        removed = self.manager.cleanup_expired_logs()
        assert removed == 1
        assert len(self.manager.audit_log) == 1


class TestFederatedAuditEntry:
    """Tests for FederatedAuditEntry"""

    def test_create_audit_entry(self):
        """Test creating audit entry"""
        entry = FederatedAuditEntry(
            event_type=AuditEventType.DATA_ACCESS,
            agency_id="agency-1",
            user_id="user-1",
            user_name="Officer Smith",
            resource_type="person",
            resource_id="person-123",
            action="read",
            details={"fields": ["name", "address"]},
            ip_address="192.168.1.100",
            access_decision=AccessDecision.ALLOW,
        )

        assert entry.event_type == AuditEventType.DATA_ACCESS
        assert entry.agency_id == "agency-1"
        assert entry.access_decision == AccessDecision.ALLOW
        assert entry.retention_until > datetime.utcnow()

    def test_audit_entry_retention_calculation(self):
        """Test audit entry retention calculation"""
        # Data access should have 3 year retention
        access_entry = FederatedAuditEntry(
            event_type=AuditEventType.DATA_ACCESS,
            agency_id="agency-1",
            user_id="user-1",
            user_name="User 1",
            resource_type="person",
            resource_id="person-1",
            action="read",
            details={},
        )

        # Policy violation should have 7 year retention
        violation_entry = FederatedAuditEntry(
            event_type=AuditEventType.POLICY_VIOLATION,
            agency_id="agency-1",
            user_id="user-1",
            user_name="User 1",
            resource_type="person",
            resource_id="person-1",
            action="unauthorized_access",
            details={},
        )

        # Verify retention periods are different
        access_retention_days = (access_entry.retention_until - access_entry.timestamp).days
        violation_retention_days = (violation_entry.retention_until - violation_entry.timestamp).days

        assert access_retention_days >= 365 * 3 - 1  # ~3 years
        assert violation_retention_days >= 365 * 7 - 1  # ~7 years
