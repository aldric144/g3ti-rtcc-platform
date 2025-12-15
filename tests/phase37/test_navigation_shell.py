"""
Phase 37: Navigation Shell Tests
Tests for the Global Navigation Shell components.
"""

import pytest
import os


class TestNavigationShellComponents:
    """Test suite for Navigation Shell components."""

    def test_top_nav_bar_exists(self):
        """Test that TopNavBar component file exists."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/TopNavBar.tsx"
        assert os.path.exists(component_path)

    def test_left_sidebar_exists(self):
        """Test that LeftSidebar component file exists."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/LeftSidebar.tsx"
        assert os.path.exists(component_path)

    def test_master_layout_exists(self):
        """Test that MasterLayout component file exists."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/MasterLayout.tsx"
        assert os.path.exists(component_path)

    def test_top_nav_bar_content(self):
        """Test TopNavBar component content."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/TopNavBar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "TopNavBar" in content
        assert "onMenuToggle" in content
        assert "alertCount" in content
        assert "operatorName" in content
        assert "operatorStatus" in content
        assert "G3TI RTCC-UIP" in content
        assert "Riviera Beach" in content

    def test_left_sidebar_content(self):
        """Test LeftSidebar component content."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/LeftSidebar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "LeftSidebar" in content
        assert "isCollapsed" in content
        assert "currentPath" in content
        assert "navSections" in content
        assert "Operational Modules" in content
        assert "Advanced Systems" in content
        assert "Developer / Admin Tools" in content

    def test_master_layout_content(self):
        """Test MasterLayout component content."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/MasterLayout.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "MasterLayout" in content
        assert "TopNavBar" in content
        assert "LeftSidebar" in content
        assert "children" in content

    def test_sidebar_has_all_modules(self):
        """Test that sidebar includes all RTCC modules."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/LeftSidebar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        expected_modules = [
            "Master Dashboard",
            "Real-Time Operations",
            "Investigations",
            "Tactical Analytics",
            "Officer Safety",
            "Communications",
            "Robotics",
            "Drone Ops",
            "Digital Twin",
            "Predictive Intelligence",
            "Human Stability",
            "Moral Compass",
            "Global Awareness",
            "AI City Brain",
            "Governance Engine",
            "Fusion Cloud",
            "Autonomous Ops",
            "City Autonomy",
            "Public Safety Guardian",
            "Officer Assist",
            "Cyber Intelligence",
            "Emergency Management",
            "AI Sentinel Supervisor",
            "AI Personas",
        ]

        for module in expected_modules:
            assert module in content, f"Module '{module}' not found in sidebar"

    def test_top_nav_has_required_elements(self):
        """Test that top nav has all required elements."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/TopNavBar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "RBPD" in content
        assert "UTC" in content
        assert "EST" in content
        assert "searchQuery" in content
        assert "showAlerts" in content

    def test_sidebar_has_admin_section(self):
        """Test that sidebar has admin/developer section."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/LeftSidebar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "Logs" in content
        assert "System Health" in content
        assert "Redundancy" in content
        assert "Failover" in content
        assert "Configurations" in content

    def test_sidebar_collapsible_functionality(self):
        """Test that sidebar has collapsible functionality."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/LeftSidebar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "expandedSections" in content
        assert "toggleSection" in content
        assert "isCollapsed" in content

    def test_theme_colors_applied(self):
        """Test that G3TI theme colors are applied."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/TopNavBar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "#c9a227" in content
        assert "#0a1628" in content
        assert "#1e3a5f" in content

    def test_navigation_links_defined(self):
        """Test that navigation links are properly defined."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/LeftSidebar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "/master-dashboard" in content
        assert "/real-time-ops" in content
        assert "/investigations" in content
        assert "/tactical-analytics" in content

    def test_icon_paths_defined(self):
        """Test that icon paths are defined for navigation items."""
        component_path = "/home/ubuntu/repos/g3ti-rtcc-platform/frontend/components/navigation/LeftSidebar.tsx"

        with open(component_path, "r") as f:
            content = f.read()

        assert "iconPaths" in content
        assert "dashboard" in content
        assert "shield" in content
        assert "brain" in content
