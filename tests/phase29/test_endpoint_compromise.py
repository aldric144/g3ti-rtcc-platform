"""
Test Suite 4: Endpoint Compromise Detection Tests

Tests for endpoint security monitoring.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestEndpointCompromise:
    """Tests for endpoint compromise detection"""
    
    def test_detect_privilege_escalation(self):
        """Test detection of privilege escalation"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="workstation-01",
            ip_address="192.168.1.100",
            user_account="jsmith",
            process_anomalies=["cmd.exe spawned from excel.exe"],
            privilege_escalation=True,
        )
        
        assert compromise is not None
        assert compromise.privilege_escalation is True
    
    def test_detect_unauthorized_access(self):
        """Test detection of unauthorized access"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="server-01",
            ip_address="10.0.0.1",
            user_account="admin",
            unauthorized_access=True,
        )
        
        assert compromise is not None
        assert compromise.unauthorized_access is True
    
    def test_detect_suspicious_processes(self):
        """Test detection of suspicious processes"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="workstation-02",
            ip_address="192.168.1.101",
            user_account="jdoe",
            suspicious_processes=["mimikatz.exe", "procdump.exe"],
        )
        
        assert compromise is not None
        assert len(compromise.suspicious_processes) >= 2
    
    def test_detect_suspicious_connections(self):
        """Test detection of suspicious network connections"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="workstation-03",
            ip_address="192.168.1.102",
            user_account="asmith",
            suspicious_connections=["203.0.113.100:4444", "198.51.100.50:8080"],
        )
        
        assert compromise is not None
        assert len(compromise.suspicious_connections) >= 2
    
    def test_detect_process_anomalies(self):
        """Test detection of process anomalies"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="workstation-04",
            ip_address="192.168.1.103",
            user_account="bwilson",
            process_anomalies=[
                "powershell.exe with encoded command",
                "svchost.exe running from temp folder",
            ],
        )
        
        assert compromise is not None
        assert len(compromise.process_anomalies) >= 2
    
    def test_endpoint_compromise_dataclass(self):
        """Test EndpointCompromise dataclass structure"""
        from backend.app.cyber_intel.cyber_threat_engine import (
            EndpointCompromise, ThreatSeverity, DetectionMethod, ThreatStatus
        )
        
        compromise = EndpointCompromise(
            compromise_id="endpoint-123",
            timestamp=datetime.utcnow(),
            severity=ThreatSeverity.HIGH,
            hostname="server-01",
            ip_address="10.0.0.1",
            user_account="admin",
            detection_method=DetectionMethod.BEHAVIOR_ANOMALY,
        )
        
        assert compromise.compromise_id == "endpoint-123"
        assert compromise.severity == ThreatSeverity.HIGH
        assert compromise.hostname == "server-01"
    
    def test_endpoint_chain_of_custody(self):
        """Test endpoint compromise has chain of custody hash"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="workstation-05",
            ip_address="192.168.1.104",
            user_account="cjones",
            privilege_escalation=True,
        )
        
        assert compromise is not None
        assert compromise.chain_of_custody_hash is not None
        assert len(compromise.chain_of_custody_hash) == 64
    
    def test_endpoint_recommended_action(self):
        """Test endpoint compromise has recommended action"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="server-02",
            ip_address="10.0.0.2",
            user_account="svc_account",
            privilege_escalation=True,
            unauthorized_access=True,
        )
        
        assert compromise is not None
        assert compromise.recommended_action is not None
        assert len(compromise.recommended_action) > 0
    
    def test_no_compromise_for_normal_activity(self):
        """Test no compromise detected for normal activity"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="workstation-06",
            ip_address="192.168.1.105",
            user_account="dsmith",
        )
        
        assert compromise is None
    
    def test_registry_modifications_detection(self):
        """Test detection of suspicious registry modifications"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        compromise = engine.detect_endpoint_compromise(
            hostname="workstation-07",
            ip_address="192.168.1.106",
            user_account="ewhite",
            registry_modifications=[
                "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            ],
        )
        
        assert compromise is not None
