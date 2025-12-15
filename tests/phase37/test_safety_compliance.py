"""
Phase 37: Safety and Compliance Tests
Tests for safety and compliance features in the Master Orchestration system.
"""

import pytest
import os
from datetime import datetime

from backend.app.master_orchestration.event_bus import (
    MasterEventBus,
    EventType,
    EventSource,
    MasterEvent,
)
from backend.app.master_orchestration.alert_aggregator import (
    UnifiedAlertStream,
    AlertSeverity,
    AlertSource,
    UnifiedAlert,
)
from backend.app.master_orchestration.permissions_manager import (
    GlobalPermissionsManager,
    PermissionAction,
)


class TestSafetyCompliance:
    """Test suite for safety and compliance features."""

    def setup_method(self):
        """Reset singletons for each test."""
        MasterEventBus._instance = None
        UnifiedAlertStream._instance = None
        GlobalPermissionsManager._instance = None

        self.event_bus = MasterEventBus()
        self.alert_stream = UnifiedAlertStream()
        self.permissions = GlobalPermissionsManager()

    def test_constitutional_compliance_tracking(self):
        """Test that constitutional compliance is tracked on events."""
        event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.OFFICER_SAFETY,
            title="Officer Action",
            constitutional_compliance=True,
        )

        assert event.constitutional_compliance is True

    def test_constitutional_compliance_on_alerts(self):
        """Test that constitutional compliance is tracked on alerts."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.OFFICER_ASSIST,
            title="Officer Alert",
            constitutional_compliance_tag=True,
        )

        assert alert.constitutional_compliance_tag is True

    def test_moral_compass_tag_tracking(self):
        """Test that moral compass tags are tracked."""
        event = self.event_bus.create_event(
            event_type=EventType.MORAL_COMPASS_ALERT,
            source=EventSource.MORAL_COMPASS,
            title="Ethics Review",
            moral_compass_tag="compliant",
        )

        assert event.moral_compass_tag == "compliant"

    def test_public_safety_audit_reference(self):
        """Test that public safety audit references are tracked."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.PUBLIC_GUARDIAN,
            title="Public Safety Alert",
            public_safety_audit_ref="audit-2025-001",
        )

        assert alert.public_safety_audit_ref == "audit-2025-001"

    def test_role_based_access_control(self):
        """Test RBAC enforcement."""
        self.permissions.assign_role("viewer-user", "viewer")
        self.permissions.assign_role("admin-user", "admin")

        viewer_can_delete = self.permissions.check_permission(
            user_id="viewer-user",
            module="investigations",
            feature="cases",
            action=PermissionAction.DELETE,
        )

        admin_can_delete = self.permissions.check_permission(
            user_id="admin-user",
            module="investigations",
            feature="cases",
            action=PermissionAction.DELETE,
        )

        assert viewer_can_delete is False
        assert admin_can_delete is True

    def test_sensitive_data_protection(self):
        """Test that sensitive data access is controlled."""
        self.permissions.assign_role("public-user", "public")

        can_view_officer_data = self.permissions.check_permission(
            user_id="public-user",
            module="officer_safety",
            feature="officer_locations",
            action=PermissionAction.VIEW,
        )

        can_view_intel = self.permissions.check_permission(
            user_id="public-user",
            module="investigations",
            feature="sensitive_intel",
            action=PermissionAction.VIEW,
        )

        assert can_view_officer_data is False
        assert can_view_intel is False

    def test_audit_trail_on_events(self):
        """Test that events include audit information."""
        event = self.event_bus.create_event(
            event_type=EventType.USER_ACTION,
            source=EventSource.USER,
            title="User Action",
            details={"action": "view_case", "case_id": "case-001"},
        )

        assert event.timestamp is not None
        assert event.event_id is not None
        assert "action" in event.details

    def test_alert_action_tracking(self):
        """Test that alert actions are tracked."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.HIGH,
            source=AlertSource.OFFICER_ASSIST,
            title="Action Required",
            requires_action=True,
        )

        self.alert_stream.take_action(
            alert.alert_id,
            action_by="operator-001",
            action_notes="Dispatched unit",
        )

        updated = self.alert_stream.get_alert(alert.alert_id)

        assert updated.action_taken is True
        assert updated.action_by == "operator-001"
        assert updated.action_at is not None
        assert updated.action_notes == "Dispatched unit"

    def test_escalation_tracking(self):
        """Test that escalations are tracked."""
        alert = self.alert_stream.create_alert(
            severity=AlertSeverity.MEDIUM,
            source=AlertSource.HUMAN_STABILITY,
            title="Escalation Test",
        )

        escalated = self.alert_stream.escalate_alert(
            alert.alert_id,
            escalation_notes="Requires supervisor review",
        )

        assert escalated.escalated is True
        assert escalated.escalation_level > 0

    def test_event_acknowledgment_tracking(self):
        """Test that event acknowledgments are tracked."""
        event = self.event_bus.create_event(
            event_type=EventType.ALERT,
            source=EventSource.SYSTEM,
            title="Acknowledgment Test",
            requires_acknowledgment=True,
        )
        self.event_bus.publish_sync(event)

        self.event_bus.acknowledge_event(event.event_id, "supervisor-001")

        updated = self.event_bus.get_event(event.event_id)

        assert updated.acknowledged_by == "supervisor-001"
        assert updated.acknowledged_at is not None

    def test_no_secrets_in_code(self):
        """Test that no secrets are exposed in code files."""
        code_paths = [
            "/home/ubuntu/repos/g3ti-rtcc-platform/backend/app/master_orchestration/event_bus.py",
            "/home/ubuntu/repos/g3ti-rtcc-platform/backend/app/master_orchestration/alert_aggregator.py",
            "/home/ubuntu/repos/g3ti-rtcc-platform/backend/app/master_orchestration/permissions_manager.py",
            "/home/ubuntu/repos/g3ti-rtcc-platform/backend/app/api/master/master_router.py",
        ]

        secret_patterns = [
            "password=",
            "api_key=",
            "secret_key=",
            "token=",
            "AWS_SECRET",
            "PRIVATE_KEY",
        ]

        for path in code_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read()

                for pattern in secret_patterns:
                    assert pattern not in content, f"Potential secret found in {path}"

    def test_documentation_exists(self):
        """Test that Phase 37 documentation exists."""
        doc_path = "/home/ubuntu/repos/g3ti-rtcc-platform/docs/PHASE37_MASTER_UI_INTEGRATION.md"
        assert os.path.exists(doc_path)

    def test_documentation_covers_security(self):
        """Test that documentation covers security considerations."""
        doc_path = "/home/ubuntu/repos/g3ti-rtcc-platform/docs/PHASE37_MASTER_UI_INTEGRATION.md"

        with open(doc_path, "r") as f:
            content = f.read()

        assert "Security" in content
        assert "RBAC" in content or "permission" in content.lower()
        assert "authentication" in content.lower() or "audit" in content.lower()

    def test_all_modules_have_permissions(self):
        """Test that all modules have permission definitions."""
        perm_map = self.permissions.get_permissions_map()

        expected_modules = [
            "real_time_ops",
            "investigations",
            "tactical_analytics",
            "officer_safety",
        ]

        for module in expected_modules:
            assert module in perm_map or any(
                module in str(v) for v in perm_map.values()
            )

    def test_action_count_meets_requirement(self):
        """Test that action count meets 2000+ requirement."""
        action_count = self.permissions.get_action_count()
        assert action_count >= 2000

    def test_all_roles_defined(self):
        """Test that all 11 roles are defined."""
        roles = self.permissions.get_all_roles()

        expected_roles = [
            "super_admin",
            "admin",
            "commander",
            "supervisor",
            "analyst",
            "investigator",
            "officer",
            "dispatcher",
            "operator",
            "viewer",
            "public",
        ]

        for role in expected_roles:
            assert role in roles

    def test_super_admin_has_full_access(self):
        """Test that super_admin has full system access."""
        self.permissions.assign_role("super-admin-user", "super_admin")

        modules = ["admin", "investigations", "officer_safety", "tactical_analytics"]
        actions = [
            PermissionAction.VIEW,
            PermissionAction.CREATE,
            PermissionAction.UPDATE,
            PermissionAction.DELETE,
            PermissionAction.ADMIN,
        ]

        for module in modules:
            for action in actions:
                allowed = self.permissions.check_permission(
                    user_id="super-admin-user",
                    module=module,
                    feature="any",
                    action=action,
                )
                assert allowed is True

    def test_public_role_restricted(self):
        """Test that public role has restricted access."""
        self.permissions.assign_role("public-user", "public")

        restricted_actions = [
            PermissionAction.CREATE,
            PermissionAction.UPDATE,
            PermissionAction.DELETE,
            PermissionAction.ADMIN,
            PermissionAction.CONFIGURE,
        ]

        for action in restricted_actions:
            allowed = self.permissions.check_permission(
                user_id="public-user",
                module="investigations",
                feature="cases",
                action=action,
            )
            assert allowed is False
