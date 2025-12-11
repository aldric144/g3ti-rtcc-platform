"""
Test Suite 1: Cyber Threat Intelligence Engine Tests

Tests for core cyber threat detection functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestCyberThreatEngine:
    """Tests for CyberThreatEngine class"""
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        assert engine is not None
        assert engine.agency_config["ori"] == "FL0500400"
        assert engine.agency_config["name"] == "Riviera Beach Police Department"
        assert engine.agency_config["state"] == "FL"
    
    def test_singleton_pattern(self):
        """Test engine follows singleton pattern"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine1 = CyberThreatEngine()
        engine2 = CyberThreatEngine()
        
        assert engine1 is engine2
    
    def test_threat_severity_enum(self):
        """Test ThreatSeverity enum values"""
        from backend.app.cyber_intel.cyber_threat_engine import ThreatSeverity
        
        assert ThreatSeverity.INFORMATIONAL.value == 1
        assert ThreatSeverity.LOW.value == 2
        assert ThreatSeverity.MEDIUM.value == 3
        assert ThreatSeverity.HIGH.value == 4
        assert ThreatSeverity.CRITICAL.value == 5
    
    def test_threat_type_enum(self):
        """Test ThreatType enum has required values"""
        from backend.app.cyber_intel.cyber_threat_engine import ThreatType
        
        assert ThreatType.NETWORK_INTRUSION is not None
        assert ThreatType.CREDENTIAL_COMPROMISE is not None
        assert ThreatType.SQL_INJECTION is not None
        assert ThreatType.XSS_ATTACK is not None
        assert ThreatType.RCE_EXPLOIT is not None
        assert ThreatType.RANSOMWARE is not None
    
    def test_detection_method_enum(self):
        """Test DetectionMethod enum values"""
        from backend.app.cyber_intel.cyber_threat_engine import DetectionMethod
        
        assert DetectionMethod.SIGNATURE_MATCH is not None
        assert DetectionMethod.BEHAVIOR_ANOMALY is not None
        assert DetectionMethod.HEURISTIC is not None
        assert DetectionMethod.ML_MODEL is not None
        assert DetectionMethod.THREAT_INTEL is not None
    
    def test_network_threat_dataclass(self):
        """Test NetworkThreat dataclass structure"""
        from backend.app.cyber_intel.cyber_threat_engine import (
            NetworkThreat, ThreatType, ThreatSeverity, 
            DetectionMethod, ThreatStatus
        )
        
        threat = NetworkThreat(
            threat_id="test-123",
            timestamp=datetime.utcnow(),
            threat_type=ThreatType.NETWORK_INTRUSION,
            severity=ThreatSeverity.HIGH,
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=12345,
            destination_port=443,
            protocol="TCP",
            detection_method=DetectionMethod.SIGNATURE_MATCH,
        )
        
        assert threat.threat_id == "test-123"
        assert threat.threat_type == ThreatType.NETWORK_INTRUSION
        assert threat.severity == ThreatSeverity.HIGH
    
    def test_scan_network_traffic_suspicious_port(self):
        """Test network scan detects suspicious ports"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        threat = engine.scan_network_traffic(
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=12345,
            destination_port=4444,
            protocol="TCP",
        )
        
        assert threat is not None
        assert threat.destination_port == 4444
    
    def test_scan_network_traffic_sql_injection(self):
        """Test network scan detects SQL injection"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine, ThreatType
        
        engine = CyberThreatEngine()
        
        threat = engine.scan_network_traffic(
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            payload="SELECT * FROM users WHERE id=1 OR 1=1--",
        )
        
        assert threat is not None
        assert threat.threat_type == ThreatType.SQL_INJECTION
    
    def test_scan_network_traffic_xss(self):
        """Test network scan detects XSS attacks"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine, ThreatType
        
        engine = CyberThreatEngine()
        
        threat = engine.scan_network_traffic(
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=12345,
            destination_port=80,
            protocol="TCP",
            payload="<script>alert('xss')</script>",
        )
        
        assert threat is not None
        assert threat.threat_type == ThreatType.XSS_ATTACK
    
    def test_chain_of_custody_hash(self):
        """Test chain of custody hash is generated"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        threat = engine.scan_network_traffic(
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=12345,
            destination_port=4444,
            protocol="TCP",
        )
        
        assert threat is not None
        assert threat.chain_of_custody_hash is not None
        assert len(threat.chain_of_custody_hash) == 64
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        stats = engine.get_statistics()
        
        assert "total_network_threats" in stats
        assert "total_ransomware_alerts" in stats
        assert "total_endpoint_compromises" in stats
        assert "total_zero_day_threats" in stats
    
    def test_get_threat_assessment(self):
        """Test threat assessment retrieval"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        assessment = engine.get_threat_assessment()
        
        assert assessment is not None
        assert assessment.assessment_id is not None
        assert assessment.timestamp is not None
        assert assessment.overall_threat_level is not None
        assert assessment.chain_of_custody_hash is not None
    
    def test_add_threat_intel(self):
        """Test adding threat intelligence"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        result = engine.add_threat_intel(
            ioc_type="malicious_ip",
            value="203.0.113.100",
            source="test",
        )
        
        assert result is True
