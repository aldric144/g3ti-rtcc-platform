"""
Phase 37: Global Permissions Manager Tests
Tests for the Global Permissions Manager functionality.
"""

import pytest
from datetime import datetime

from backend.app.master_orchestration.permissions_manager import (
    GlobalPermissionsManager,
    PermissionAction,
    PermissionScope,
    RolePermission,
)


class TestGlobalPermissionsManager:
    """Test suite for GlobalPermissionsManager."""

    def setup_method(self):
        """Reset singleton for each test."""
        GlobalPermissionsManager._instance = None
        self.manager = GlobalPermissionsManager()

    def test_singleton_pattern(self):
        """Test that GlobalPermissionsManager follows singleton pattern."""
        manager1 = GlobalPermissionsManager()
        manager2 = GlobalPermissionsManager()
        assert manager1 is manager2

    def test_predefined_roles(self):
        """Test that all predefined roles exist."""
        roles = self.manager.get_all_roles()

        expected_roles = [
            "super_admin", "admin", "commander", "supervisor",
            "analyst", "investigator", "officer", "dispatcher",
            "operator", "viewer", "public"
        ]

        for role in expected_roles:
            assert role in roles

    def test_role_hierarchy(self):
        """Test role hierarchy levels."""
        super_admin = self.manager.get_role("super_admin")
        admin = self.manager.get_role("admin")
        viewer = self.manager.get_role("viewer")
        public = self.manager.get_role("public")

        assert super_admin["level"] > admin["level"]
        assert admin["level"] > viewer["level"]
        assert viewer["level"] > public["level"]

    def test_assign_role(self):
        """Test role assignment to user."""
        result = self.manager.assign_role("user-001", "analyst")
        assert result is True

        roles = self.manager.get_user_roles("user-001")
        assert "analyst" in roles

    def test_remove_role(self):
        """Test role removal from user."""
        self.manager.assign_role("user-002", "officer")
        result = self.manager.remove_role("user-002", "officer")
        assert result is True

        roles = self.manager.get_user_roles("user-002")
        assert "officer" not in roles

    def test_check_permission_allowed(self):
        """Test permission check for allowed action."""
        self.manager.assign_role("admin-user", "admin")

        allowed = self.manager.check_permission(
            user_id="admin-user",
            module="real_time_ops",
            feature="incidents",
            action=PermissionAction.VIEW,
        )

        assert allowed is True

    def test_check_permission_denied(self):
        """Test permission check for denied action."""
        self.manager.assign_role("viewer-user", "viewer")

        allowed = self.manager.check_permission(
            user_id="viewer-user",
            module="admin",
            feature="system_config",
            action=PermissionAction.ADMIN,
        )

        assert allowed is False

    def test_check_permission_by_role(self):
        """Test permission check by role directly."""
        allowed = self.manager.check_permission_by_role(
            role="super_admin",
            module="any_module",
            feature="any_feature",
            action=PermissionAction.ADMIN,
        )

        assert allowed is True

    def test_get_user_permissions(self):
        """Test retrieving all permissions for a user."""
        self.manager.assign_role("perm-user", "analyst")

        permissions = self.manager.get_user_permissions("perm-user")

        assert isinstance(permissions, list)
        assert len(permissions) > 0

    def test_get_role_permissions(self):
        """Test retrieving permissions for a role."""
        permissions = self.manager.get_role_permissions("officer")

        assert isinstance(permissions, list)

    def test_get_module_permissions(self):
        """Test retrieving permissions for a module."""
        permissions = self.manager.get_module_permissions("investigations")

        assert isinstance(permissions, list)

    def test_add_permission(self):
        """Test adding a new permission."""
        result = self.manager.add_permission(
            role="analyst",
            module="custom_module",
            feature="custom_feature",
            action=PermissionAction.VIEW,
            scope=PermissionScope.MODULE,
        )

        assert result is True

    def test_revoke_permission(self):
        """Test revoking a permission."""
        self.manager.add_permission(
            role="analyst",
            module="revoke_test",
            feature="test_feature",
            action=PermissionAction.CREATE,
        )

        result = self.manager.revoke_permission(
            role="analyst",
            module="revoke_test",
            feature="test_feature",
            action=PermissionAction.CREATE,
        )

        assert result is True

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.manager.get_statistics()

        assert "total_roles" in stats
        assert "total_permissions" in stats
        assert "users_with_roles" in stats

    def test_get_permissions_map(self):
        """Test permissions map retrieval."""
        perm_map = self.manager.get_permissions_map()

        assert isinstance(perm_map, dict)
        assert len(perm_map) > 0

    def test_get_action_count(self):
        """Test action count retrieval."""
        count = self.manager.get_action_count()

        assert count >= 2000

    def test_permission_action_enum(self):
        """Test all permission actions are defined."""
        assert len(PermissionAction) == 10
        assert PermissionAction.VIEW.value == "view"
        assert PermissionAction.CREATE.value == "create"
        assert PermissionAction.UPDATE.value == "update"
        assert PermissionAction.DELETE.value == "delete"
        assert PermissionAction.EXECUTE.value == "execute"
        assert PermissionAction.APPROVE.value == "approve"
        assert PermissionAction.EXPORT.value == "export"
        assert PermissionAction.IMPORT.value == "import"
        assert PermissionAction.CONFIGURE.value == "configure"
        assert PermissionAction.ADMIN.value == "admin"

    def test_permission_scope_enum(self):
        """Test all permission scopes are defined."""
        assert len(PermissionScope) == 5
        assert PermissionScope.GLOBAL.value == "global"
        assert PermissionScope.MODULE.value == "module"
        assert PermissionScope.FEATURE.value == "feature"
        assert PermissionScope.DATA.value == "data"
        assert PermissionScope.ACTION.value == "action"

    def test_role_permission_dataclass(self):
        """Test RolePermission dataclass."""
        permission = RolePermission(
            role="analyst",
            module="investigations",
            feature="cases",
            action=PermissionAction.VIEW,
            scope=PermissionScope.MODULE,
            allowed=True,
        )

        assert permission.role == "analyst"
        assert permission.allowed is True

    def test_multiple_roles_per_user(self):
        """Test user with multiple roles."""
        self.manager.assign_role("multi-role-user", "analyst")
        self.manager.assign_role("multi-role-user", "investigator")

        roles = self.manager.get_user_roles("multi-role-user")

        assert "analyst" in roles
        assert "investigator" in roles

    def test_super_admin_has_all_permissions(self):
        """Test that super_admin has all permissions."""
        self.manager.assign_role("super-user", "super_admin")

        modules = ["real_time_ops", "investigations", "admin", "tactical"]
        actions = [PermissionAction.VIEW, PermissionAction.ADMIN, PermissionAction.DELETE]

        for module in modules:
            for action in actions:
                allowed = self.manager.check_permission(
                    user_id="super-user",
                    module=module,
                    feature="any",
                    action=action,
                )
                assert allowed is True

    def test_public_role_limited_access(self):
        """Test that public role has limited access."""
        self.manager.assign_role("public-user", "public")

        admin_allowed = self.manager.check_permission(
            user_id="public-user",
            module="admin",
            feature="system",
            action=PermissionAction.ADMIN,
        )
        assert admin_allowed is False

        delete_allowed = self.manager.check_permission(
            user_id="public-user",
            module="investigations",
            feature="cases",
            action=PermissionAction.DELETE,
        )
        assert delete_allowed is False
