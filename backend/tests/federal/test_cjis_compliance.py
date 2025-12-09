"""
Unit tests for CJIS Compliance module.
"""

from datetime import datetime


class TestCJISAuditLogger:
    """Tests for CJISAuditLogger class."""

    def test_log_action(self):
        """Test logging an action."""
        from app.federal.cjis import (
            CJISAuditAction,
            CJISResourceType,
            cjis_audit_logger,
        )

        entry = cjis_audit_logger.log(
            user_id="user-001",
            user_name="John Smith",
            agency_id="FL0000000",
            action=CJISAuditAction.QUERY,
            resource_type=CJISResourceType.PERSON,
            resource_id="person-123",
            success=True,
            ip_address="192.168.1.100",
        )

        assert entry is not None
        assert entry.user_id == "user-001"
        assert entry.action == CJISAuditAction.QUERY
        assert entry.success is True

    def test_log_federal_export(self):
        """Test logging a federal export."""
        from app.federal.cjis import cjis_audit_logger

        entry = cjis_audit_logger.log_federal_export(
            user_id="user-002",
            user_name="Jane Doe",
            agency_id="FL0000000",
            export_type="ndex",
            resource_id="export-123",
            ip_address="192.168.1.101",
            success=True,
        )

        assert entry is not None
        assert entry.action.value == "export"
        assert "8" in entry.policy_areas  # Auditing policy area

    def test_log_access_denied(self):
        """Test logging access denied."""
        from app.federal.cjis import CJISResourceType, cjis_audit_logger

        entry = cjis_audit_logger.log_access_denied(
            user_id="user-003",
            user_name="Bob Wilson",
            agency_id="FL0000000",
            resource_type=CJISResourceType.FEDERAL_DATA,
            resource_id=None,
            reason="Missing permission: federal_access",
            ip_address="192.168.1.102",
        )

        assert entry is not None
        assert entry.action.value == "access_denied"
        assert entry.success is False

    def test_get_audit_log(self):
        """Test getting audit log entries."""
        from app.federal.cjis import cjis_audit_logger

        entries = cjis_audit_logger.get_audit_log(
            agency_id="FL0000000",
            limit=10,
        )

        assert isinstance(entries, list)

    def test_get_failed_access_attempts(self):
        """Test getting failed access attempts."""
        from app.federal.cjis import cjis_audit_logger

        entries = cjis_audit_logger.get_failed_access_attempts(
            agency_id="FL0000000",
        )

        assert isinstance(entries, list)

    def test_generate_compliance_report(self):
        """Test generating compliance report."""
        from app.federal.cjis import cjis_audit_logger

        report = cjis_audit_logger.generate_compliance_report(
            agency_id="FL0000000",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
        )

        assert report is not None
        assert "total_events" in report
        assert "compliance_status" in report


class TestCJISFieldMasker:
    """Tests for CJISFieldMasker class."""

    def test_mask_ssn(self):
        """Test SSN masking."""
        from app.federal.cjis import cjis_field_masker

        masked = cjis_field_masker.mask_ssn("123-45-6789")

        assert masked is not None
        assert "6789" in masked  # Last 4 visible
        assert "123" not in masked  # First 3 hidden

    def test_mask_dob(self):
        """Test DOB masking."""
        from app.federal.cjis import cjis_field_masker

        masked = cjis_field_masker.mask_dob("1990-01-15")

        assert masked is not None
        assert "15" in masked  # Day visible
        assert "1990" not in masked  # Year hidden

    def test_mask_drivers_license(self):
        """Test driver's license masking."""
        from app.federal.cjis import cjis_field_masker

        masked = cjis_field_masker.mask_drivers_license("D123456789")

        assert masked is not None
        assert "6789" in masked  # Last 4 visible
        assert "D123" not in masked  # First part hidden

    def test_mask_phone(self):
        """Test phone masking."""
        from app.federal.cjis import cjis_field_masker

        masked = cjis_field_masker.mask_phone("555-123-4567")

        assert masked is not None
        assert "4567" in masked  # Last 4 visible

    def test_mask_email(self):
        """Test email masking."""
        from app.federal.cjis import cjis_field_masker

        masked = cjis_field_masker.mask_email("john@example.com")

        assert masked is not None
        assert "john" not in masked.lower()
        assert "REDACTED" in masked or "***" in masked

    def test_mask_dict(self):
        """Test dictionary masking."""
        from app.federal.cjis import cjis_field_masker

        data = {
            "name": "John Smith",
            "ssn": "123-45-6789",
            "date_of_birth": "1990-01-15",
            "phone": "555-123-4567",
        }

        masked = cjis_field_masker.mask_dict(data)

        assert masked is not None
        assert masked["name"] == "John Smith"  # Not sensitive
        assert "6789" in masked.get("ssn", "")  # SSN masked
        assert "15" in masked.get("date_of_birth", "")  # DOB masked

    def test_mask_narrative(self):
        """Test narrative masking."""
        from app.federal.cjis import cjis_field_masker

        narrative = "Subject John Smith, SSN 123-45-6789, phone 555-123-4567"

        masked = cjis_field_masker.mask_narrative(narrative)

        assert masked is not None
        assert "123-45-6789" not in masked
        assert "555-123-4567" not in masked

    def test_hash_identifier(self):
        """Test identifier hashing."""
        from app.federal.cjis import cjis_field_masker

        hash1 = cjis_field_masker.hash_identifier("123-45-6789")
        hash2 = cjis_field_masker.hash_identifier("123-45-6789")
        hash3 = cjis_field_masker.hash_identifier("987-65-4321")

        assert hash1 == hash2  # Same input = same hash
        assert hash1 != hash3  # Different input = different hash


class TestCJISAccessControl:
    """Tests for CJISAccessControl class."""

    def test_has_permission(self):
        """Test permission checking."""
        from app.federal.cjis import cjis_access_control

        # Set up user role
        cjis_access_control.set_user_role("user-001", "supervisor")

        has_perm = cjis_access_control.has_permission("user-001", "can_export_ndex")

        assert has_perm is True

    def test_has_federal_access(self):
        """Test federal access checking."""
        from app.federal.cjis import cjis_access_control

        # Set up user role
        cjis_access_control.set_user_role("user-002", "detective")

        has_access = cjis_access_control.has_federal_access("user-002")

        assert has_access is True

    def test_officer_no_federal_access(self):
        """Test officer role has no federal access."""
        from app.federal.cjis import cjis_access_control

        # Set up user role
        cjis_access_control.set_user_role("user-003", "officer")

        has_access = cjis_access_control.has_federal_access("user-003")

        assert has_access is False

    def test_can_export_ndex(self):
        """Test N-DEx export permission."""
        from app.federal.cjis import cjis_access_control

        cjis_access_control.set_user_role("user-004", "supervisor")

        can_export = cjis_access_control.can_export_ndex("user-004")

        assert can_export is True

    def test_can_query_ncic(self):
        """Test NCIC query permission."""
        from app.federal.cjis import cjis_access_control

        cjis_access_control.set_user_role("user-005", "detective")

        can_query = cjis_access_control.can_query_ncic("user-005")

        assert can_query is True

    def test_can_view_audit_logs(self):
        """Test audit log viewing permission."""
        from app.federal.cjis import cjis_access_control

        cjis_access_control.set_user_role("user-006", "supervisor")
        cjis_access_control.set_user_role("user-007", "detective")

        # Supervisor can view
        assert cjis_access_control.can_view_audit_logs("user-006") is True
        # Detective cannot view
        assert cjis_access_control.can_view_audit_logs("user-007") is False

    def test_grant_permission(self):
        """Test granting specific permission."""
        from app.federal.cjis import cjis_access_control

        cjis_access_control.set_user_role("user-008", "detective")
        cjis_access_control.grant_permission("user-008", "can_view_audit_logs")

        can_view = cjis_access_control.can_view_audit_logs("user-008")

        assert can_view is True

    def test_revoke_permission(self):
        """Test revoking specific permission."""
        from app.federal.cjis import cjis_access_control

        cjis_access_control.set_user_role("user-009", "supervisor")
        cjis_access_control.revoke_permission("user-009", "can_query_ncic")

        can_query = cjis_access_control.can_query_ncic("user-009")

        assert can_query is False


class TestCJISComplianceManager:
    """Tests for CJISComplianceManager class."""

    def test_check_federal_access(self):
        """Test federal access check."""
        # Set up user with access
        from app.federal.cjis import CJISResourceType, cjis_access_control, cjis_compliance_manager
        cjis_access_control.set_user_role("user-010", "supervisor")

        has_access, error = cjis_compliance_manager.check_federal_access(
            user_id="user-010",
            user_name="Test Supervisor",
            agency_id="FL0000000",
            operation="ndex_export",
            resource_type=CJISResourceType.NDEX_EXPORT,
            resource_id="export-123",
            ip_address="192.168.1.100",
        )

        assert has_access is True
        assert error is None

    def test_check_federal_access_denied(self):
        """Test federal access denied."""
        # Set up user without access
        from app.federal.cjis import CJISResourceType, cjis_access_control, cjis_compliance_manager
        cjis_access_control.set_user_role("user-011", "officer")

        has_access, error = cjis_compliance_manager.check_federal_access(
            user_id="user-011",
            user_name="Test Officer",
            agency_id="FL0000000",
            operation="ndex_export",
            resource_type=CJISResourceType.NDEX_EXPORT,
            resource_id="export-456",
            ip_address="192.168.1.101",
        )

        assert has_access is False
        assert error is not None

    def test_get_compliance_status(self):
        """Test getting compliance status."""
        from app.federal.cjis import cjis_compliance_manager

        status = cjis_compliance_manager.get_compliance_status()

        assert status is not None
        assert "status" in status
        assert "policy_areas" in status


class TestCJISAuditEntry:
    """Tests for CJISAuditEntry class."""

    def test_retention_period(self):
        """Test audit entry retention period."""
        from app.federal.cjis import CJISAuditAction, CJISAuditEntry, CJISResourceType

        entry = CJISAuditEntry(
            user_id="user-012",
            user_name="Test User",
            agency_id="FL0000000",
            action=CJISAuditAction.QUERY,
            resource_type=CJISResourceType.PERSON,
        )

        assert entry.retention_years == 7
        assert entry.retention_until is not None
        # Retention should be ~7 years from now
        years_diff = (entry.retention_until - entry.timestamp).days / 365
        assert 6.9 < years_diff < 7.1
