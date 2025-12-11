"""
Test Suite 7: Cryptographic Attack Detection Tests

Tests for crypto vulnerability and attack detection.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestCryptoAttacks:
    """Tests for cryptographic attack detection"""
    
    def test_crypto_attack_type_enum(self):
        """Test CryptoAttackType enum values"""
        from backend.app.cyber_intel.quantum_detection_engine import CryptoAttackType
        
        assert CryptoAttackType.RSA_FACTORING is not None
        assert CryptoAttackType.ECDSA_BREAK is not None
        assert CryptoAttackType.DH_COMPROMISE is not None
        assert CryptoAttackType.LATTICE_ATTACK is not None
        assert CryptoAttackType.HARVEST_NOW_DECRYPT_LATER is not None
    
    def test_monitor_vulnerable_rsa(self):
        """Test detection of vulnerable RSA usage"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        attack = engine.monitor_crypto_traffic(
            source_system="web-server-01",
            algorithm="RSA",
            key_size=1024,
        )
        
        assert attack is not None
        assert attack.target_algorithm == "RSA"
        assert attack.target_key_size == 1024
    
    def test_monitor_vulnerable_ecdsa(self):
        """Test detection of vulnerable ECDSA usage"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        attack = engine.monitor_crypto_traffic(
            source_system="api-server-01",
            algorithm="ECDSA",
            key_size=256,
        )
        
        assert attack is not None
        assert attack.target_algorithm == "ECDSA"
    
    def test_detect_harvest_now_decrypt_later(self):
        """Test detection of harvest-now-decrypt-later attacks"""
        from backend.app.cyber_intel.quantum_detection_engine import (
            QuantumDetectionEngine, CryptoAttackType
        )
        
        engine = QuantumDetectionEngine()
        
        attack = engine.monitor_crypto_traffic(
            source_system="network-tap-01",
            algorithm="RSA",
            key_size=2048,
            traffic_volume_gb=100,
            harvesting_behavior=True,
        )
        
        assert attack is not None
        assert attack.attack_type == CryptoAttackType.HARVEST_NOW_DECRYPT_LATER
    
    def test_crypto_attack_dataclass(self):
        """Test CryptoAttack dataclass structure"""
        from backend.app.cyber_intel.quantum_detection_engine import (
            CryptoAttack, CryptoAttackType, QuantumSeverity, DetectionConfidence
        )
        
        attack = CryptoAttack(
            attack_id="crypto-123",
            timestamp=datetime.utcnow(),
            attack_type=CryptoAttackType.RSA_FACTORING,
            severity=QuantumSeverity.HIGH,
            target_algorithm="RSA",
            target_key_size=2048,
            source_system="server-01",
        )
        
        assert attack.attack_id == "crypto-123"
        assert attack.attack_type == CryptoAttackType.RSA_FACTORING
        assert attack.target_key_size == 2048
    
    def test_post_quantum_ready_flag(self):
        """Test post-quantum ready flag"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        attack = engine.monitor_crypto_traffic(
            source_system="legacy-server",
            algorithm="RSA",
            key_size=1024,
        )
        
        assert attack is not None
        assert attack.post_quantum_ready is False
    
    def test_estimated_decrypt_timeline(self):
        """Test estimated decryption timeline"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        attack = engine.monitor_crypto_traffic(
            source_system="critical-server",
            algorithm="RSA",
            key_size=2048,
        )
        
        assert attack is not None
        assert attack.estimated_decrypt_timeline is not None
    
    def test_crypto_chain_of_custody(self):
        """Test crypto attack has chain of custody hash"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        attack = engine.monitor_crypto_traffic(
            source_system="server-02",
            algorithm="ECDSA",
            key_size=256,
        )
        
        assert attack is not None
        assert attack.chain_of_custody_hash is not None
        assert len(attack.chain_of_custody_hash) == 64
    
    def test_crypto_recommended_action(self):
        """Test crypto attack has recommended action"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        attack = engine.monitor_crypto_traffic(
            source_system="server-03",
            algorithm="DH",
            key_size=1024,
        )
        
        assert attack is not None
        assert attack.recommended_action is not None
        assert len(attack.recommended_action) > 0
    
    def test_no_attack_for_pq_algorithm(self):
        """Test no attack for post-quantum algorithm"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        attack = engine.monitor_crypto_traffic(
            source_system="modern-server",
            algorithm="CRYSTALS-Kyber",
            key_size=768,
        )
        
        assert attack is None
    
    def test_vulnerable_algorithms_list(self):
        """Test vulnerable algorithms are tracked"""
        from backend.app.cyber_intel.quantum_detection_engine import QuantumDetectionEngine
        
        engine = QuantumDetectionEngine()
        
        vulnerable = engine._vulnerable_algorithms
        
        assert "RSA" in vulnerable
        assert "ECDSA" in vulnerable
        assert "DH" in vulnerable
        assert "DSA" in vulnerable
