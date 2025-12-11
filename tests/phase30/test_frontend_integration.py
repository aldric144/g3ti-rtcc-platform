"""
Phase 30: Frontend Integration Tests

Tests for:
- Human Intel Center page
- Component rendering
- API integration
- WebSocket connections
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestHumanIntelCenterPage:
    """Tests for Human Intel Center page"""
    
    def test_page_file_exists(self):
        """Test page.tsx file exists"""
        import os
        
        page_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'page.tsx'
        )
        
        assert os.path.exists(page_path)
    
    def test_page_has_required_imports(self):
        """Test page has required component imports"""
        import os
        
        page_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'page.tsx'
        )
        
        with open(page_path, 'r') as f:
            content = f.read()
        
        assert "CommunityStabilityDashboard" in content
        assert "SuicideRiskPanel" in content
        assert "DVHotspotPredictor" in content
        assert "YouthCrisisMonitor" in content
        assert "CrisisRoutingConsole" in content
        assert "MentalHealthPulseMap" in content


class TestCommunityStabilityDashboard:
    """Tests for CommunityStabilityDashboard component"""
    
    def test_component_file_exists(self):
        """Test component file exists"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'CommunityStabilityDashboard.tsx'
        )
        
        assert os.path.exists(component_path)
    
    def test_component_exports_default(self):
        """Test component exports default"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'CommunityStabilityDashboard.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "export default" in content


class TestSuicideRiskPanel:
    """Tests for SuicideRiskPanel component"""
    
    def test_component_file_exists(self):
        """Test component file exists"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'SuicideRiskPanel.tsx'
        )
        
        assert os.path.exists(component_path)
    
    def test_component_has_crisis_resources(self):
        """Test component has crisis resources"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'SuicideRiskPanel.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "988" in content or "Crisis" in content


class TestDVHotspotPredictor:
    """Tests for DVHotspotPredictor component"""
    
    def test_component_file_exists(self):
        """Test component file exists"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'DVHotspotPredictor.tsx'
        )
        
        assert os.path.exists(component_path)
    
    def test_component_has_vawa_notice(self):
        """Test component has VAWA compliance notice"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'DVHotspotPredictor.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "VAWA" in content


class TestYouthCrisisMonitor:
    """Tests for YouthCrisisMonitor component"""
    
    def test_component_file_exists(self):
        """Test component file exists"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'YouthCrisisMonitor.tsx'
        )
        
        assert os.path.exists(component_path)
    
    def test_component_has_ferpa_notice(self):
        """Test component has FERPA compliance notice"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'YouthCrisisMonitor.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "FERPA" in content


class TestCrisisRoutingConsole:
    """Tests for CrisisRoutingConsole component"""
    
    def test_component_file_exists(self):
        """Test component file exists"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'CrisisRoutingConsole.tsx'
        )
        
        assert os.path.exists(component_path)
    
    def test_component_has_call_types(self):
        """Test component has call types"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'CrisisRoutingConsole.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "welfare_check" in content
        assert "mental_health" in content
        assert "suicide_ideation" in content


class TestMentalHealthPulseMap:
    """Tests for MentalHealthPulseMap component"""
    
    def test_component_file_exists(self):
        """Test component file exists"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'MentalHealthPulseMap.tsx'
        )
        
        assert os.path.exists(component_path)
    
    def test_component_has_privacy_notice(self):
        """Test component has privacy notice"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'MentalHealthPulseMap.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "Privacy" in content or "HIPAA" in content


class TestAPIIntegration:
    """Tests for API integration"""
    
    def test_stability_map_endpoint_integration(self):
        """Test stability map endpoint integration"""
        import os
        
        page_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'page.tsx'
        )
        
        with open(page_path, 'r') as f:
            content = f.read()
        
        assert "/api/human-intel/stability-map" in content
    
    def test_community_pulse_endpoint_integration(self):
        """Test community pulse endpoint integration"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'MentalHealthPulseMap.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "/api/human-intel/community-pulse" in content
    
    def test_crisis_route_endpoint_integration(self):
        """Test crisis route endpoint integration"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'CrisisRoutingConsole.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "/api/human-intel/crisis-route" in content


class TestPrivacyNotices:
    """Tests for privacy notices in frontend"""
    
    def test_main_page_has_privacy_notice(self):
        """Test main page has privacy notice"""
        import os
        
        page_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'page.tsx'
        )
        
        with open(page_path, 'r') as f:
            content = f.read()
        
        assert "Privacy" in content or "anonymized" in content
    
    def test_suicide_panel_has_privacy_notice(self):
        """Test suicide panel has privacy notice"""
        import os
        
        component_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'frontend', 'app', 'human-intel-center', 'components',
            'SuicideRiskPanel.tsx'
        )
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        assert "Privacy" in content or "anonymized" in content
