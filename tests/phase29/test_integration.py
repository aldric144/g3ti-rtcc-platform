"""
Test Suite 15: End-to-End Integration Tests

Tests for complete Phase 29 integration.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestPhase29Integration:
    """End-to-end integration tests for Phase 29"""
    
    def test_all_engines_initialize(self):
        """Test all three engines initialize correctly"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        cyber_engine = CyberThreatEngine()
        quantum_engine = QuantumDetectionEngine()
        info_engine = InfoWarfareEngine()
        
        assert cyber_engine is not None
        assert quantum_engine is not None
        assert info_engine is not None
    
    def test_all_engines_same_agency_config(self):
        """Test all engines use same agency configuration"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        cyber_engine = CyberThreatEngine()
        quantum_engine = QuantumDetectionEngine()
        info_engine = InfoWarfareEngine()
        
        assert cyber_engine.agency_config["ori"] == "FL0500400"
        assert quantum_engine.agency_config["ori"] == "FL0500400"
        assert info_engine.agency_config["ori"] == "FL0500400"
    
    def test_cyber_threat_to_alert_flow(self):
        """Test cyber threat detection to alert flow"""
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
        assert threat.threat_id is not None
        assert threat.chain_of_custody_hash is not None
        assert threat.recommended_action is not None
    
    def test_quantum_threat_to_alert_flow(self):
        """Test quantum threat detection to alert flow"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        anomaly = engine.detect_quantum_anomaly(
            source_identifier="quantum-sensor-01",
            qubit_pattern="suspicious_pattern",
            qber_value=0.20,
        )
        
        assert anomaly is not None
        assert anomaly.anomaly_id is not None
        assert anomaly.chain_of_custody_hash is not None
        assert anomaly.recommended_action is not None
    
    def test_disinfo_to_alert_flow(self):
        """Test disinformation detection to alert flow"""
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        engine = InfoWarfareEngine()
        
        alert = engine.detect_rumor_panic(
            source_platform="FACEBOOK",
            content="False emergency alert",
            share_count=5000,
            viral_velocity=0.8,
        )
        
        assert alert is not None
        assert alert.alert_id is not None
        assert alert.chain_of_custody_hash is not None
        assert alert.recommended_action is not None
    
    def test_deepfake_to_alert_flow(self):
        """Test deepfake detection to alert flow"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        alert = engine.scan_for_deepfake(
            media_type="video",
            source_url="https://example.com/video.mp4",
            analysis_features={
                "blink_rate_anomaly": True,
                "facial_boundary_artifacts": True,
            },
        )
        
        assert alert is not None
        assert alert.alert_id is not None
        assert alert.chain_of_custody_hash is not None
        assert alert.recommended_action is not None
    
    def test_ransomware_to_alert_flow(self):
        """Test ransomware detection to alert flow"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        alert = engine.detect_ransomware(
            hostname="workstation-01",
            path="C:\\Users\\Documents",
            file_modifications_per_minute=150,
        )
        
        assert alert is not None
        assert alert.alert_id is not None
        assert alert.chain_of_custody_hash is not None
        assert alert.recommended_action is not None
    
    def test_all_assessments_available(self):
        """Test all assessment methods work"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        cyber_engine = CyberThreatEngine()
        quantum_engine = QuantumDetectionEngine()
        info_engine = InfoWarfareEngine()
        
        cyber_assessment = cyber_engine.get_threat_assessment()
        quantum_assessment = quantum_engine.get_quantum_assessment()
        disinfo_assessment = info_engine.get_disinfo_assessment()
        
        assert cyber_assessment is not None
        assert quantum_assessment is not None
        assert disinfo_assessment is not None
    
    def test_all_statistics_available(self):
        """Test all statistics methods work"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        from backend.app.cyber_intel.info_warfare_engine import InfoWarfareEngine
        
        cyber_engine = CyberThreatEngine()
        quantum_engine = QuantumDetectionEngine()
        info_engine = InfoWarfareEngine()
        
        cyber_stats = cyber_engine.get_statistics()
        quantum_stats = quantum_engine.get_statistics()
        disinfo_stats = info_engine.get_statistics()
        
        assert cyber_stats is not None
        assert quantum_stats is not None
        assert disinfo_stats is not None
    
    def test_api_router_integration(self):
        """Test API router integrates with engines"""
        from backend.app.api.cyber_intel.cyber_intel_router import router
        
        assert router is not None
        assert router.prefix == "/api/cyber-intel"
    
    def test_websocket_router_integration(self):
        """Test WebSocket router integrates with engines"""
        from backend.app.websockets.cyber_intel_ws import router, manager
        
        assert router is not None
        assert manager is not None
    
    def test_chain_of_custody_consistency(self):
        """Test chain of custody hashes are consistent"""
        from backend.app.cyber_intel.cyber_threat_engine import CyberThreatEngine
        
        engine = CyberThreatEngine()
        
        threat1 = engine.scan_network_traffic(
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=12345,
            destination_port=4444,
            protocol="TCP",
        )
        
        threat2 = engine.scan_network_traffic(
            source_ip="192.168.1.101",
            destination_ip="10.0.0.2",
            source_port=12346,
            destination_port=4445,
            protocol="TCP",
        )
        
        assert threat1.chain_of_custody_hash != threat2.chain_of_custody_hash
        assert len(threat1.chain_of_custody_hash) == 64
        assert len(threat2.chain_of_custody_hash) == 64
    
    def test_module_exports(self):
        """Test module exports all required classes"""
        from backend.app.cyber_intel import (
            CyberThreatEngine,
            ThreatSeverity,
            ThreatType,
            NetworkThreat,
            RansomwareAlert,
            EndpointCompromise,
            ZeroDayThreat,
            ThreatAssessment,
            QuantumDetectionEngine,
            QuantumThreatType,
            CryptoAttackType,
            DeepfakeType,
            QuantumAnomaly,
            CryptoAttack,
            DeepfakeAlert,
            QuantumAssessment,
            InfoWarfareEngine,
            DisinfoType,
            DisinfoSeverity,
            DisinfoSource,
            RumorAlert,
            ImpersonationAlert,
            ElectionThreat,
            CrisisManipulation,
            DisinfoAssessment,
        )
        
        assert CyberThreatEngine is not None
        assert QuantumDetectionEngine is not None
        assert InfoWarfareEngine is not None
    
    def test_documentation_exists(self):
        """Test Phase 29 documentation exists"""
        doc_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "docs", "PHASE29_CYBER_INTEL_QUANTUM_LAYER.md"
        )
        assert os.path.exists(doc_path)
    
    def test_devops_workflow_exists(self):
        """Test DevOps workflow exists"""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", ".github", "workflows", "cyber-intel-hardening.yml"
        )
        assert os.path.exists(workflow_path)
    
    def test_backend_module_structure(self):
        """Test backend module structure is correct"""
        backend_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "backend", "app", "cyber_intel"
        )
        
        assert os.path.exists(os.path.join(backend_path, "__init__.py"))
        assert os.path.exists(os.path.join(backend_path, "cyber_threat_engine.py"))
        assert os.path.exists(os.path.join(backend_path, "quantum_detection_engine.py"))
        assert os.path.exists(os.path.join(backend_path, "info_warfare_engine.py"))
    
    def test_api_module_structure(self):
        """Test API module structure is correct"""
        api_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "backend", "app", "api", "cyber_intel"
        )
        
        assert os.path.exists(os.path.join(api_path, "__init__.py"))
        assert os.path.exists(os.path.join(api_path, "cyber_intel_router.py"))
