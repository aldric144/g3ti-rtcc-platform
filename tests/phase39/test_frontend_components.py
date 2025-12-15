"""
Phase 39 Test Suite: Frontend Components
Tests for verifying frontend PreLaunch components exist and are properly structured.
"""

import pytest
import os
from pathlib import Path


class TestFrontendComponents:
    """Test suite for frontend component validation."""

    @pytest.fixture
    def frontend_path(self):
        """Get frontend directory path."""
        return Path("/home/ubuntu/repos/g3ti-rtcc-platform/frontend")

    def test_live_system_check_page_exists(self, frontend_path):
        """Test live-system-check page exists."""
        page_path = frontend_path / "app" / "live-system-check" / "page.tsx"
        assert page_path.exists(), "live-system-check page.tsx not found"

    def test_system_prelaunch_page_exists(self, frontend_path):
        """Test system-prelaunch page exists."""
        page_path = frontend_path / "app" / "system-prelaunch" / "page.tsx"
        assert page_path.exists(), "system-prelaunch page.tsx not found"

    def test_prelaunch_checklist_panel_exists(self, frontend_path):
        """Test PreLaunchChecklistPanel component exists."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "PreLaunchChecklistPanel.tsx"
        assert component_path.exists(), "PreLaunchChecklistPanel.tsx not found"

    def test_deployment_summary_card_exists(self, frontend_path):
        """Test DeploymentSummaryCard component exists."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "DeploymentSummaryCard.tsx"
        assert component_path.exists(), "DeploymentSummaryCard.tsx not found"

    def test_prelaunch_checklist_panel_content(self, frontend_path):
        """Test PreLaunchChecklistPanel has required content."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "PreLaunchChecklistPanel.tsx"
        content = component_path.read_text()

        assert "PreLaunchChecklistPanel" in content
        assert "useState" in content
        assert "useEffect" in content
        assert "/api/system/prelaunch" in content

    def test_deployment_summary_card_content(self, frontend_path):
        """Test DeploymentSummaryCard has required content."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "DeploymentSummaryCard.tsx"
        content = component_path.read_text()

        assert "DeploymentSummaryCard" in content
        assert "deployment_score" in content
        assert "ready_for_deployment" in content

    def test_live_system_check_page_content(self, frontend_path):
        """Test live-system-check page has required content."""
        page_path = frontend_path / "app" / "live-system-check" / "page.tsx"
        content = page_path.read_text()

        assert "LiveSystemCheckPage" in content
        assert "PreLaunchChecklistPanel" in content
        assert "DeploymentSummaryCard" in content

    def test_system_prelaunch_page_content(self, frontend_path):
        """Test system-prelaunch page has required content."""
        page_path = frontend_path / "app" / "system-prelaunch" / "page.tsx"
        content = page_path.read_text()

        assert "SystemPrelaunchPage" in content
        assert "deployment_score" in content
        assert "orchestration" in content

    def test_gold_color_used(self, frontend_path):
        """Test gold color (#c9a227) is used in components."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "PreLaunchChecklistPanel.tsx"
        content = component_path.read_text()

        assert "#c9a227" in content or "c9a227" in content

    def test_navy_color_used(self, frontend_path):
        """Test navy color (#0a1628) is used in components."""
        component_path = frontend_path / "app" / "live-system-check" / "page.tsx"
        content = component_path.read_text()

        assert "#0a1628" in content or "0a1628" in content

    def test_api_endpoints_referenced(self, frontend_path):
        """Test API endpoints are referenced in components."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "PreLaunchChecklistPanel.tsx"
        content = component_path.read_text()

        expected_endpoints = [
            "/api/system/prelaunch/status",
            "/api/system/prelaunch/modules",
            "/api/system/prelaunch/websockets",
            "/api/system/prelaunch/endpoints",
        ]

        for endpoint in expected_endpoints:
            assert endpoint in content, f"Missing endpoint reference: {endpoint}"

    def test_module_status_grid_present(self, frontend_path):
        """Test Module Status Grid is present in component."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "PreLaunchChecklistPanel.tsx"
        content = component_path.read_text()

        assert "Module" in content
        assert "Status" in content

    def test_websocket_connectivity_matrix_present(self, frontend_path):
        """Test WebSocket Connectivity Matrix is present."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "PreLaunchChecklistPanel.tsx"
        content = component_path.read_text()

        assert "WebSocket" in content
        assert "Connectivity" in content or "channel" in content.lower()

    def test_api_endpoint_validator_present(self, frontend_path):
        """Test API Endpoint Validator is present."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "PreLaunchChecklistPanel.tsx"
        content = component_path.read_text()

        assert "API" in content or "Endpoint" in content

    def test_orchestration_signal_indicator_present(self, frontend_path):
        """Test Orchestration Engine Signal Indicator is present."""
        page_path = frontend_path / "app" / "system-prelaunch" / "page.tsx"
        content = page_path.read_text()

        assert "Orchestration" in content
        assert "kernel" in content.lower() or "engine" in content.lower()

    def test_deployment_score_display(self, frontend_path):
        """Test deployment score display is present."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "DeploymentSummaryCard.tsx"
        content = component_path.read_text()

        assert "deployment_score" in content
        assert "%" in content

    def test_use_client_directive(self, frontend_path):
        """Test 'use client' directive is present in components."""
        component_path = frontend_path / "app" / "live-system-check" / "components" / "PreLaunchChecklistPanel.tsx"
        content = component_path.read_text()

        assert "'use client'" in content or '"use client"' in content
