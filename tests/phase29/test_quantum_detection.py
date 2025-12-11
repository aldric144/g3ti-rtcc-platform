"""
Test Suite 6: Quantum Threat Detection Tests

Tests for quantum anomaly detection functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestQuantumDetection:
    """Tests for QuantumDetectionEngine class"""
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        assert engine is not None
        assert engine.agency_config["ori"] == "FL0500400"
        assert engine.agency_config["name"] == "Riviera Beach Police Department"
    
    def test_singleton_pattern(self):
        """Test engine follows singleton pattern"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine1 = QuantumDetectionEngine()
        engine2 = QuantumDetectionEngine()
        
        assert engine1 is engine2
    
    def test_quantum_threat_type_enum(self):
        """Test QuantumThreatType enum values"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumThreatType
        
        assert QuantumThreatType.QUANTUM_NETWORK_PROBE is not None
        assert QuantumThreatType.PHOTONIC_INTRUSION is not None
        assert QuantumThreatType.QUBIT_ANOMALY is not None
        assert QuantumThreatType.QUANTUM_KEY_HARVEST is not None
    
    def test_quantum_severity_enum(self):
        """Test QuantumSeverity enum values"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumSeverity
        
        assert QuantumSeverity.INFORMATIONAL.value == 1
        assert QuantumSeverity.LOW.value == 2
        assert QuantumSeverity.MEDIUM.value == 3
        assert QuantumSeverity.HIGH.value == 4
        assert QuantumSeverity.CRITICAL.value == 5
        assert QuantumSeverity.CATASTROPHIC.value == 6
    
    def test_detect_quantum_anomaly(self):
        """Test quantum anomaly detection"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        anomaly = engine.detect_quantum_anomaly(
            source_identifier="quantum-sensor-01",
            qubit_pattern="unusual_entanglement_pattern",
            qber_value=0.15,
        )
        
        assert anomaly is not None
        assert anomaly.qubit_pattern == "unusual_entanglement_pattern"
    
    def test_detect_high_qber(self):
        """Test detection of high Quantum Bit Error Rate"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        anomaly = engine.detect_quantum_anomaly(
            source_identifier="qkd-channel-01",
            qber_value=0.25,
        )
        
        assert anomaly is not None
        assert anomaly.qber_value == 0.25
    
    def test_quantum_anomaly_dataclass(self):
        """Test QuantumAnomaly dataclass structure"""
        from backend.app.cyber_intel.quantum_detection_engine import (
            QuantumAnomaly, QuantumThreatType, QuantumSeverity, DetectionConfidence
        )
        
        anomaly = QuantumAnomaly(
            anomaly_id="quantum-123",
            timestamp=datetime.utcnow(),
            threat_type=QuantumThreatType.QUBIT_ANOMALY,
            severity=QuantumSeverity.HIGH,
            source_identifier="sensor-01",
            qubit_pattern="test_pattern",
        )
        
        assert anomaly.anomaly_id == "quantum-123"
        assert anomaly.threat_type == QuantumThreatType.QUBIT_ANOMALY
        assert anomaly.severity == QuantumSeverity.HIGH
    
    def test_quantum_chain_of_custody(self):
        """Test quantum anomaly has chain of custody hash"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        anomaly = engine.detect_quantum_anomaly(
            source_identifier="quantum-sensor-02",
            qubit_pattern="suspicious_pattern",
            qber_value=0.20,
        )
        
        assert anomaly is not None
        assert anomaly.chain_of_custody_hash is not None
        assert len(anomaly.chain_of_custody_hash) == 64
    
    def test_quantum_recommended_action(self):
        """Test quantum anomaly has recommended action"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        anomaly = engine.detect_quantum_anomaly(
            source_identifier="quantum-sensor-03",
            qubit_pattern="critical_anomaly",
            qber_value=0.30,
        )
        
        assert anomaly is not None
        assert anomaly.recommended_action is not None
        assert len(anomaly.recommended_action) > 0
    
    def test_get_quantum_assessment(self):
        """Test quantum assessment retrieval"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        assessment = engine.get_quantum_assessment()
        
        assert assessment is not None
        assert assessment.assessment_id is not None
        assert assessment.timestamp is not None
        assert assessment.post_quantum_readiness_score is not None
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        stats = engine.get_statistics()
        
        assert "total_quantum_anomalies" in stats
        assert "total_crypto_attacks" in stats
        assert "total_deepfake_alerts" in stats
    
    def test_post_quantum_algorithms(self):
        """Test post-quantum algorithm support"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        pq_algos = engine._post_quantum_algorithms
        
        assert "CRYSTALS-Kyber" in pq_algos
        assert "CRYSTALS-Dilithium" in pq_algos
        assert "FALCON" in pq_algos
        assert "SPHINCS+" in pq_algos
