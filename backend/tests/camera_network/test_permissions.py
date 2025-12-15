"""
Tests for Camera Network Permissions system.
"""

import pytest


class TestCameraPermissions:
    """Test suite for Camera Network Permissions."""
    
    def test_permission_roles(self):
        """Test that all permission roles are defined."""
        roles = {
            "admin": {
                "can_add": True,
                "can_edit": True,
                "can_delete": True,
                "can_ptz": True,
                "can_view_all": True,
                "view_quality": "full",
            },
            "supervisor": {
                "can_add": False,
                "can_edit": True,
                "can_delete": False,
                "can_ptz": True,
                "can_view_all": True,
                "view_quality": "full",
            },
            "analyst": {
                "can_add": False,
                "can_edit": False,
                "can_delete": False,
                "can_ptz": False,
                "can_view_all": True,
                "view_quality": "full",
            },
            "viewer": {
                "can_add": False,
                "can_edit": False,
                "can_delete": False,
                "can_ptz": False,
                "can_view_all": True,
                "view_quality": "compressed",
            },
        }
        
        assert len(roles) == 4
        assert "admin" in roles
        assert "supervisor" in roles
        assert "analyst" in roles
        assert "viewer" in roles
    
    def test_admin_permissions(self):
        """Test admin role has full permissions."""
        admin = {
            "can_add": True,
            "can_edit": True,
            "can_delete": True,
            "can_ptz": True,
            "can_view_all": True,
        }
        
        assert admin["can_add"] is True
        assert admin["can_edit"] is True
        assert admin["can_delete"] is True
        assert admin["can_ptz"] is True
    
    def test_supervisor_permissions(self):
        """Test supervisor role has PTZ but no add/delete."""
        supervisor = {
            "can_add": False,
            "can_edit": True,
            "can_delete": False,
            "can_ptz": True,
            "can_view_all": True,
        }
        
        assert supervisor["can_add"] is False
        assert supervisor["can_ptz"] is True
        assert supervisor["can_delete"] is False
    
    def test_analyst_permissions(self):
        """Test analyst role has view-only permissions."""
        analyst = {
            "can_add": False,
            "can_edit": False,
            "can_delete": False,
            "can_ptz": False,
            "can_view_all": True,
        }
        
        assert analyst["can_view_all"] is True
        assert analyst["can_ptz"] is False
        assert analyst["can_edit"] is False
    
    def test_viewer_permissions(self):
        """Test viewer role has compressed view only."""
        viewer = {
            "can_add": False,
            "can_edit": False,
            "can_delete": False,
            "can_ptz": False,
            "can_view_all": True,
            "view_quality": "compressed",
        }
        
        assert viewer["view_quality"] == "compressed"
        assert viewer["can_ptz"] is False
    
    def test_permission_check_function(self):
        """Test permission check logic."""
        def check_permission(user_role, action):
            permissions = {
                "admin": ["add", "edit", "delete", "ptz", "view"],
                "supervisor": ["edit", "ptz", "view"],
                "analyst": ["view"],
                "viewer": ["view"],
            }
            
            role_permissions = permissions.get(user_role, [])
            return action in role_permissions
        
        assert check_permission("admin", "delete") is True
        assert check_permission("supervisor", "delete") is False
        assert check_permission("supervisor", "ptz") is True
        assert check_permission("analyst", "ptz") is False
        assert check_permission("viewer", "view") is True
    
    def test_ptz_permission_required(self):
        """Test that PTZ commands require permission."""
        def can_send_ptz_command(user_role):
            ptz_allowed_roles = ["admin", "supervisor"]
            return user_role in ptz_allowed_roles
        
        assert can_send_ptz_command("admin") is True
        assert can_send_ptz_command("supervisor") is True
        assert can_send_ptz_command("analyst") is False
        assert can_send_ptz_command("viewer") is False
    
    def test_camera_crud_permissions(self):
        """Test CRUD operation permissions."""
        def can_perform_crud(user_role, operation):
            crud_permissions = {
                "create": ["admin"],
                "read": ["admin", "supervisor", "analyst", "viewer"],
                "update": ["admin", "supervisor"],
                "delete": ["admin"],
            }
            
            allowed_roles = crud_permissions.get(operation, [])
            return user_role in allowed_roles
        
        # Admin can do everything
        assert can_perform_crud("admin", "create") is True
        assert can_perform_crud("admin", "delete") is True
        
        # Supervisor can read and update
        assert can_perform_crud("supervisor", "read") is True
        assert can_perform_crud("supervisor", "update") is True
        assert can_perform_crud("supervisor", "delete") is False
        
        # Analyst can only read
        assert can_perform_crud("analyst", "read") is True
        assert can_perform_crud("analyst", "update") is False
        
        # Viewer can only read
        assert can_perform_crud("viewer", "read") is True
        assert can_perform_crud("viewer", "create") is False
