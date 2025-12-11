"""
Test Suite 2: Ransomware Detection Tests

Tests for ransomware early warning system.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestRansomwareDetection:
    """Tests for ransomware detection functionality"""
    
    def test_detect_high_file_modification_rate(self):
        """Test detection of high file modification rate"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="workstation-01",
            path="C:\\Users\\Documents",
            file_modifications_per_minute=150,
        )
        
        assert alert is not None
        assert alert.file_modifications_per_minute == 150
        assert alert.severity.value >= 3
    
    def test_detect_known_ransomware_signature(self):
        """Test detection of known ransomware signatures"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="server-01",
            path="D:\\Data",
            file_modifications_per_minute=50,
            file_names=["readme_lockbit.txt"],
        )
        
        assert alert is not None
        assert alert.ransomware_family == "LOCKBIT"
    
    def test_detect_suspicious_extensions(self):
        """Test detection of suspicious file extensions"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="workstation-02",
            path="C:\\Users\\Documents",
            file_modifications_per_minute=80,
            file_extensions=[".encrypted", ".locked", ".crypted"],
        )
        
        assert alert is not None
        assert alert.encryption_detected is True
    
    def test_detect_conti_ransomware(self):
        """Test detection of CONTI ransomware"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="server-02",
            path="E:\\Shares",
            file_modifications_per_minute=100,
            file_names=["conti_readme.txt"],
        )
        
        assert alert is not None
        assert alert.ransomware_family == "CONTI"
    
    def test_detect_revil_ransomware(self):
        """Test detection of REVIL ransomware"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="server-03",
            path="F:\\Data",
            file_modifications_per_minute=120,
            file_names=["revil-decrypt.txt"],
        )
        
        assert alert is not None
        assert alert.ransomware_family == "REVIL"
    
    def test_ransomware_alert_chain_of_custody(self):
        """Test ransomware alert has chain of custody hash"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="workstation-03",
            path="C:\\Users\\Documents",
            file_modifications_per_minute=200,
        )
        
        assert alert is not None
        assert alert.chain_of_custody_hash is not None
        assert len(alert.chain_of_custody_hash) == 64
    
    def test_ransomware_recommended_action(self):
        """Test ransomware alert has recommended action"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="server-04",
            path="G:\\Critical",
            file_modifications_per_minute=300,
            file_names=["readme_lockbit.txt"],
        )
        
        assert alert is not None
        assert alert.recommended_action is not None
        assert len(alert.recommended_action) > 0
    
    def test_no_alert_for_normal_activity(self):
        """Test no alert for normal file activity"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="workstation-04",
            path="C:\\Users\\Documents",
            file_modifications_per_minute=5,
        )
        
        assert alert is None
    
    def test_ransomware_alert_dataclass(self):
        """Test RansomwareAlert dataclass structure"""
        from backend.app.cyber_intel.cyber_threat_engine import (
            RansomwareAlert, ThreatSeverity, ThreatStatus
        )
        
        alert = RansomwareAlert(
            alert_id="ransomware-123",
            timestamp=datetime.utcnow(),
            severity=ThreatSeverity.CRITICAL,
            affected_host="server-01",
            affected_path="D:\\Data",
            file_modifications_per_minute=200,
        )
        
        assert alert.alert_id == "ransomware-123"
        assert alert.severity == ThreatSeverity.CRITICAL
        assert alert.affected_host == "server-01"
    
    def test_multiple_ransomware_families(self):
        """Test detection of multiple ransomware families"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        families = ["lockbit", "conti", "revil", "ryuk", "blackcat"]
        detected_families = []
        
        for family in families:
            alert = engine.detect_ransomware(
                hostname=f"server-{family}",
                path="D:\\Data",
                file_modifications_per_minute=100,
                file_names=[f"{family}_readme.txt"],
            )
            if alert and alert.ransomware_family:
                detected_families.append(alert.ransomware_family.lower())
        
        assert len(detected_families) >= 3
