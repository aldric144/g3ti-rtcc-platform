"""
Test Suite 14: Frontend Integration Tests

Tests for frontend component integration.
"""

import pytest
import os
import sys


class TestFrontendIntegration:
    """Tests for frontend component integration"""
    
    def test_cyber_intel_center_page_exists(self):
        """Test cyber-intel-center page exists"""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", "page.tsx"
        )
        assert os.path.exists(page_path)
    
    def test_cyber_threat_map_component_exists(self):
        """Test CyberThreatMap component exists"""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", 
            "components", "CyberThreatMap.tsx"
        )
        assert os.path.exists(component_path)
    
    def test_quantum_anomaly_dashboard_exists(self):
        """Test QuantumAnomalyDashboard component exists"""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center",
            "components", "QuantumAnomalyDashboard.tsx"
        )
        assert os.path.exists(component_path)
    
    def test_deepfake_detection_panel_exists(self):
        """Test DeepfakeDetectionPanel component exists"""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center",
            "components", "DeepfakeDetectionPanel.tsx"
        )
        assert os.path.exists(component_path)
    
    def test_disinformation_radar_exists(self):
        """Test DisinformationRadar component exists"""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center",
            "components", "DisinformationRadar.tsx"
        )
        assert os.path.exists(component_path)
    
    def test_ransomware_shield_panel_exists(self):
        """Test RansomwareShieldPanel component exists"""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center",
            "components", "RansomwareShieldPanel.tsx"
        )
        assert os.path.exists(component_path)
    
    def test_system_hardening_console_exists(self):
        """Test SystemHardeningConsole component exists"""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center",
            "components", "SystemHardeningConsole.tsx"
        )
        assert os.path.exists(component_path)
    
    def test_page_has_use_client_directive(self):
        """Test page has 'use client' directive"""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", "page.tsx"
        )
        with open(page_path, "r") as f:
            content = f.read()
        assert '"use client"' in content or "'use client'" in content
    
    def test_cyber_threat_map_has_use_client(self):
        """Test CyberThreatMap has 'use client' directive"""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center",
            "components", "CyberThreatMap.tsx"
        )
        with open(component_path, "r") as f:
            content = f.read()
        assert '"use client"' in content or "'use client'" in content
    
    def test_page_imports_react(self):
        """Test page imports React"""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", "page.tsx"
        )
        with open(page_path, "r") as f:
            content = f.read()
        assert "import React" in content or "from \"react\"" in content
    
    def test_page_has_default_export(self):
        """Test page has default export"""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", "page.tsx"
        )
        with open(page_path, "r") as f:
            content = f.read()
        assert "export default" in content
    
    def test_cyber_threat_map_has_default_export(self):
        """Test CyberThreatMap has default export"""
        component_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center",
            "components", "CyberThreatMap.tsx"
        )
        with open(component_path, "r") as f:
            content = f.read()
        assert "export default" in content
    
    def test_page_uses_state_hooks(self):
        """Test page uses React state hooks"""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", "page.tsx"
        )
        with open(page_path, "r") as f:
            content = f.read()
        assert "useState" in content
    
    def test_page_uses_effect_hooks(self):
        """Test page uses React effect hooks"""
        page_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", "page.tsx"
        )
        with open(page_path, "r") as f:
            content = f.read()
        assert "useEffect" in content
    
    def test_components_directory_exists(self):
        """Test components directory exists"""
        components_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", "components"
        )
        assert os.path.isdir(components_dir)
    
    def test_all_six_components_exist(self):
        """Test all six required components exist"""
        components_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "frontend", "app", "cyber-intel-center", "components"
        )
        
        required_components = [
            "CyberThreatMap.tsx",
            "QuantumAnomalyDashboard.tsx",
            "DeepfakeDetectionPanel.tsx",
            "DisinformationRadar.tsx",
            "RansomwareShieldPanel.tsx",
            "SystemHardeningConsole.tsx",
        ]
        
        for component in required_components:
            component_path = os.path.join(components_dir, component)
            assert os.path.exists(component_path), f"Missing component: {component}"
