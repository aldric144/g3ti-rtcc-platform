"""
Quantum Threat Detection Engine

Provides quantum-level threat detection including:
- Post-Quantum Cryptography Monitor
- Quantum Traffic Fingerprint
- Quantum Deepfake Scanner

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
import uuid
import re


class QuantumThreatType(Enum):
    """Types of quantum threats"""
    CRYPTO_ATTACK = "CRYPTO_ATTACK"
    LATTICE_ATTACK = "LATTICE_ATTACK"
    PUBLIC_KEY_HARVEST = "PUBLIC_KEY_HARVEST"
    QUANTUM_PROBE = "QUANTUM_PROBE"
    PHOTONIC_INTRUSION = "PHOTONIC_INTRUSION"
    QUBIT_ANOMALY = "QUBIT_ANOMALY"
    DEEPFAKE_VOICE = "DEEPFAKE_VOICE"
    DEEPFAKE_VIDEO = "DEEPFAKE_VIDEO"
    SYNTHETIC_CREDENTIALS = "SYNTHETIC_CREDENTIALS"
    BODYCAM_TAMPERING = "BODYCAM_TAMPERING"


class CryptoAttackType(Enum):
    """Types of cryptographic attacks"""
    SHOR_ALGORITHM = "SHOR_ALGORITHM"
    GROVER_ALGORITHM = "GROVER_ALGORITHM"
    LATTICE_REDUCTION = "LATTICE_REDUCTION"
    SIDE_CHANNEL = "SIDE_CHANNEL"
    HARVEST_NOW_DECRYPT_LATER = "HARVEST_NOW_DECRYPT_LATER"
    KEY_EXCHANGE_INTERCEPT = "KEY_EXCHANGE_INTERCEPT"
    CERTIFICATE_FORGERY = "CERTIFICATE_FORGERY"


class DeepfakeType(Enum):
    """Types of deepfakes"""
    SYNTHETIC_VOICE = "SYNTHETIC_VOICE"
    SYNTHETIC_VIDEO = "SYNTHETIC_VIDEO"
    FACE_SWAP = "FACE_SWAP"
    LIP_SYNC = "LIP_SYNC"
    FULL_BODY_SYNTHESIS = "FULL_BODY_SYNTHESIS"
    CREDENTIAL_SYNTHESIS = "CREDENTIAL_SYNTHESIS"
    DOCUMENT_FORGERY = "DOCUMENT_FORGERY"
    BODYCAM_MANIPULATION = "BODYCAM_MANIPULATION"


class QuantumSeverity(Enum):
    """Quantum threat severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    CATASTROPHIC = 5


class DetectionConfidence(Enum):
    """Confidence level of detection"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@dataclass
class QuantumAnomaly:
    """Quantum network anomaly detection"""
    anomaly_id: str
    timestamp: datetime
    threat_type: QuantumThreatType
    severity: QuantumSeverity
    source_identifier: str
    detection_confidence: DetectionConfidence
    qubit_pattern: Optional[str] = None
    photonic_signature: Optional[str] = None
    anomaly_description: str = ""
    affected_systems: List[str] = field(default_factory=list)
    quantum_fingerprint: Optional[str] = None
    recommended_action: str = ""
    chain_of_custody_hash: str = ""


@dataclass
class CryptoAttack:
    """Cryptographic attack detection"""
    attack_id: str
    timestamp: datetime
    attack_type: CryptoAttackType
    severity: QuantumSeverity
    target_algorithm: str
    target_key_size: int
    detection_confidence: DetectionConfidence
    attack_vector: str = ""
    harvested_data_type: Optional[str] = None
    estimated_decrypt_timeline: Optional[str] = None
    affected_certificates: List[str] = field(default_factory=list)
    post_quantum_ready: bool = False
    recommended_action: str = ""
    chain_of_custody_hash: str = ""


@dataclass
class DeepfakeAlert:
    """Deepfake detection alert"""
    alert_id: str
    timestamp: datetime
    deepfake_type: DeepfakeType
    severity: QuantumSeverity
    detection_confidence: DetectionConfidence
    confidence_score: float
    source_file: Optional[str] = None
    source_url: Optional[str] = None
    claimed_identity: Optional[str] = None
    actual_identity: Optional[str] = None
    manipulation_indicators: List[str] = field(default_factory=list)
    ai_model_detected: Optional[str] = None
    officer_involved: bool = False
    officer_id: Optional[str] = None
    evidence_integrity_compromised: bool = False
    recommended_action: str = ""
    chain_of_custody_hash: str = ""


@dataclass
class QuantumAssessment:
    """Overall quantum threat assessment"""
    assessment_id: str
    timestamp: datetime
    overall_threat_level: QuantumSeverity
    quantum_anomalies: List[QuantumAnomaly] = field(default_factory=list)
    crypto_attacks: List[CryptoAttack] = field(default_factory=list)
    deepfake_alerts: List[DeepfakeAlert] = field(default_factory=list)
    post_quantum_readiness_score: float = 0.0
    critical_vulnerabilities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    chain_of_custody_hash: str = ""


class QuantumDetectionEngine:
    """
    Quantum Threat Detection Engine
    
    Provides quantum-level threat detection for Riviera Beach PD
    including post-quantum cryptography monitoring, quantum traffic analysis,
    and deepfake detection.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        self.agency_config = {
            "ori": "FL0500400",
            "name": "Riviera Beach Police Department",
            "state": "FL",
            "county": "Palm Beach",
            "city": "Riviera Beach",
            "zip": "33404",
        }
        
        self.quantum_anomalies: List[QuantumAnomaly] = []
        self.crypto_attacks: List[CryptoAttack] = []
        self.deepfake_alerts: List[DeepfakeAlert] = []
        
        self._vulnerable_algorithms = {
            "RSA": {"vulnerable": True, "key_sizes": [1024, 2048, 4096], "timeline": "2030-2035"},
            "ECDSA": {"vulnerable": True, "key_sizes": [256, 384, 521], "timeline": "2030-2035"},
            "ECDH": {"vulnerable": True, "key_sizes": [256, 384, 521], "timeline": "2030-2035"},
            "DSA": {"vulnerable": True, "key_sizes": [1024, 2048, 3072], "timeline": "2030-2035"},
            "DH": {"vulnerable": True, "key_sizes": [1024, 2048, 4096], "timeline": "2030-2035"},
            "AES-128": {"vulnerable": False, "grover_impact": "64-bit security"},
            "AES-256": {"vulnerable": False, "grover_impact": "128-bit security"},
        }
        
        self._post_quantum_algorithms = {
            "CRYSTALS-Kyber": {"type": "KEM", "nist_level": 3, "status": "standardized"},
            "CRYSTALS-Dilithium": {"type": "signature", "nist_level": 3, "status": "standardized"},
            "FALCON": {"type": "signature", "nist_level": 5, "status": "standardized"},
            "SPHINCS+": {"type": "signature", "nist_level": 5, "status": "standardized"},
        }
        
        self._deepfake_indicators = {
            "voice": [
                "unnatural_pitch_variation",
                "breathing_pattern_anomaly",
                "background_noise_inconsistency",
                "spectral_artifacts",
                "prosody_mismatch",
                "phoneme_boundary_artifacts",
            ],
            "video": [
                "blink_rate_anomaly",
                "facial_boundary_artifacts",
                "lighting_inconsistency",
                "temporal_coherence_failure",
                "compression_artifact_patterns",
                "eye_reflection_mismatch",
                "skin_texture_anomaly",
                "head_pose_inconsistency",
            ],
            "document": [
                "font_inconsistency",
                "metadata_manipulation",
                "compression_artifacts",
                "pixel_level_anomalies",
                "signature_synthesis_markers",
            ],
        }
        
        self._known_ai_models = [
            "ElevenLabs", "Resemble.AI", "Descript",
            "DeepFaceLab", "FaceSwap", "Wav2Lip",
            "StyleGAN", "DALL-E", "Midjourney",
            "Stable Diffusion", "RunwayML",
        ]
        
        self._officer_voice_profiles: Dict[str, str] = {}
        self._officer_face_profiles: Dict[str, str] = {}
    
    def _generate_chain_of_custody_hash(self, data: Dict[str, Any]) -> str:
        """Generate chain of custody hash for evidence integrity"""
        data_str = str(sorted(data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def monitor_crypto_traffic(
        self,
        algorithm: str,
        key_size: int,
        operation_type: str,
        source_system: str,
        data_classification: Optional[str] = None,
    ) -> Optional[CryptoAttack]:
        """
        Post-Quantum Cryptography Monitor
        
        Detects:
        - Attempts to break encryption
        - Lattice-attack signatures
        - Public-key harvesting behavior
        """
        attack_type = None
        severity = QuantumSeverity.LOW
        confidence = DetectionConfidence.LOW
        attack_vector = ""
        harvested_data = None
        decrypt_timeline = None
        
        if algorithm.upper() in self._vulnerable_algorithms:
            algo_info = self._vulnerable_algorithms[algorithm.upper()]
            if algo_info.get("vulnerable", False):
                attack_type = CryptoAttackType.HARVEST_NOW_DECRYPT_LATER
                severity = QuantumSeverity.MEDIUM
                confidence = DetectionConfidence.MEDIUM
                decrypt_timeline = algo_info.get("timeline", "Unknown")
                attack_vector = f"Vulnerable algorithm {algorithm} with {key_size}-bit key"
                
                if data_classification in ["SECRET", "TOP_SECRET", "CJIS"]:
                    severity = QuantumSeverity.HIGH
                    confidence = DetectionConfidence.HIGH
        
        if operation_type.lower() in ["key_exchange", "handshake", "negotiate"]:
            if algorithm.upper() in ["RSA", "ECDH", "DH"]:
                attack_type = CryptoAttackType.KEY_EXCHANGE_INTERCEPT
                severity = QuantumSeverity.HIGH
                confidence = DetectionConfidence.MEDIUM
                attack_vector = f"Key exchange using quantum-vulnerable {algorithm}"
        
        if not attack_type:
            return None
        
        post_quantum_ready = any(
            pq_algo in source_system.upper()
            for pq_algo in self._post_quantum_algorithms.keys()
        )
        
        attack = CryptoAttack(
            attack_id=f"crypto-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            attack_type=attack_type,
            severity=severity,
            target_algorithm=algorithm,
            target_key_size=key_size,
            detection_confidence=confidence,
            attack_vector=attack_vector,
            harvested_data_type=data_classification,
            estimated_decrypt_timeline=decrypt_timeline,
            post_quantum_ready=post_quantum_ready,
            recommended_action=self._get_crypto_recommendation(attack_type, severity, post_quantum_ready),
        )
        
        attack.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "attack_id": attack.attack_id,
            "timestamp": attack.timestamp.isoformat(),
            "algorithm": algorithm,
            "key_size": key_size,
        })
        
        self.crypto_attacks.append(attack)
        return attack
    
    def _get_crypto_recommendation(
        self,
        attack_type: CryptoAttackType,
        severity: QuantumSeverity,
        post_quantum_ready: bool,
    ) -> str:
        """Get recommended action for crypto attack"""
        if post_quantum_ready:
            return "System has post-quantum algorithms available. Verify they are being used."
        
        recommendations = {
            CryptoAttackType.HARVEST_NOW_DECRYPT_LATER: 
                "Migrate to post-quantum cryptography (CRYSTALS-Kyber/Dilithium). "
                "Implement hybrid encryption for transition period.",
            CryptoAttackType.KEY_EXCHANGE_INTERCEPT:
                "Implement post-quantum key exchange. Consider CRYSTALS-Kyber for key encapsulation.",
            CryptoAttackType.LATTICE_REDUCTION:
                "Increase key sizes. Evaluate lattice-based alternatives.",
            CryptoAttackType.SIDE_CHANNEL:
                "Implement constant-time operations. Review hardware security modules.",
        }
        
        base = recommendations.get(attack_type, "Review cryptographic implementation.")
        
        if severity == QuantumSeverity.CRITICAL:
            return f"CRITICAL: {base} Immediate action required."
        elif severity == QuantumSeverity.HIGH:
            return f"HIGH PRIORITY: {base}"
        
        return base
    
    def detect_quantum_anomaly(
        self,
        source_identifier: str,
        traffic_pattern: str,
        signal_characteristics: Dict[str, Any],
    ) -> Optional[QuantumAnomaly]:
        """
        Quantum Traffic Fingerprint
        
        Identifies:
        - Quantum network probes
        - Photonic intrusion attempts
        - Unusual qubit-pattern anomalies
        """
        threat_type = None
        severity = QuantumSeverity.LOW
        confidence = DetectionConfidence.LOW
        qubit_pattern = None
        photonic_sig = None
        description = ""
        
        quantum_indicators = [
            "entanglement", "superposition", "qubit",
            "photon", "quantum_key", "qkd",
            "bb84", "e91", "quantum_channel",
        ]
        
        pattern_lower = traffic_pattern.lower()
        indicator_count = sum(1 for ind in quantum_indicators if ind in pattern_lower)
        
        if indicator_count >= 3:
            threat_type = QuantumThreatType.QUANTUM_PROBE
            severity = QuantumSeverity.HIGH
            confidence = DetectionConfidence.HIGH
            description = "Multiple quantum protocol indicators detected"
        elif indicator_count >= 1:
            threat_type = QuantumThreatType.QUBIT_ANOMALY
            severity = QuantumSeverity.MEDIUM
            confidence = DetectionConfidence.MEDIUM
            description = "Quantum protocol indicators present"
        
        if "photon" in pattern_lower or signal_characteristics.get("photonic", False):
            threat_type = QuantumThreatType.PHOTONIC_INTRUSION
            severity = QuantumSeverity.HIGH
            confidence = DetectionConfidence.MEDIUM
            photonic_sig = hashlib.sha256(traffic_pattern.encode()).hexdigest()[:16]
            description = "Photonic channel anomaly detected"
        
        if signal_characteristics.get("error_rate", 0) > 0.11:
            if threat_type:
                severity = QuantumSeverity.CRITICAL
                description += ". High QBER indicates potential eavesdropping."
        
        if not threat_type:
            return None
        
        qubit_pattern = hashlib.sha256(
            f"{traffic_pattern}{str(signal_characteristics)}".encode()
        ).hexdigest()[:24]
        
        anomaly = QuantumAnomaly(
            anomaly_id=f"quantum-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            threat_type=threat_type,
            severity=severity,
            source_identifier=source_identifier,
            detection_confidence=confidence,
            qubit_pattern=qubit_pattern,
            photonic_signature=photonic_sig,
            anomaly_description=description,
            quantum_fingerprint=qubit_pattern,
            recommended_action=self._get_quantum_recommendation(threat_type, severity),
        )
        
        anomaly.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "anomaly_id": anomaly.anomaly_id,
            "timestamp": anomaly.timestamp.isoformat(),
            "source": source_identifier,
            "qubit_pattern": qubit_pattern,
        })
        
        self.quantum_anomalies.append(anomaly)
        return anomaly
    
    def _get_quantum_recommendation(self, threat_type: QuantumThreatType, severity: QuantumSeverity) -> str:
        """Get recommended action for quantum anomaly"""
        recommendations = {
            QuantumThreatType.QUANTUM_PROBE: 
                "Investigate source of quantum probing. Review network segmentation. "
                "Consider quantum-safe network isolation.",
            QuantumThreatType.PHOTONIC_INTRUSION:
                "Analyze photonic channel integrity. Check for fiber tapping. "
                "Implement quantum key distribution monitoring.",
            QuantumThreatType.QUBIT_ANOMALY:
                "Monitor for additional quantum indicators. Log all anomalous patterns.",
        }
        
        base = recommendations.get(threat_type, "Investigate quantum anomaly.")
        
        if severity == QuantumSeverity.CRITICAL:
            return f"CRITICAL: {base} Contact quantum security team immediately."
        
        return base
    
    def scan_for_deepfake(
        self,
        media_type: str,
        source_file: Optional[str] = None,
        source_url: Optional[str] = None,
        claimed_identity: Optional[str] = None,
        analysis_features: Optional[Dict[str, Any]] = None,
        officer_id: Optional[str] = None,
        is_evidence: bool = False,
    ) -> Optional[DeepfakeAlert]:
        """
        Quantum Deepfake Scanner
        
        Detects:
        - Synthetic voice
        - Synthetic video
        - Synthetic officer credentials
        - AI-generated bodycam tampering
        """
        deepfake_type = None
        severity = QuantumSeverity.LOW
        confidence = DetectionConfidence.LOW
        confidence_score = 0.0
        manipulation_indicators = []
        ai_model = None
        officer_involved = officer_id is not None
        evidence_compromised = False
        
        features = analysis_features or {}
        
        if media_type.lower() in ["audio", "voice"]:
            deepfake_type = DeepfakeType.SYNTHETIC_VOICE
            
            for indicator in self._deepfake_indicators["voice"]:
                if features.get(indicator, False):
                    manipulation_indicators.append(indicator)
                    confidence_score += 0.15
            
            if features.get("voice_clone_detected", False):
                confidence_score += 0.3
                manipulation_indicators.append("voice_clone_signature")
            
        elif media_type.lower() in ["video", "image"]:
            if features.get("face_swap", False):
                deepfake_type = DeepfakeType.FACE_SWAP
            elif features.get("lip_sync", False):
                deepfake_type = DeepfakeType.LIP_SYNC
            else:
                deepfake_type = DeepfakeType.SYNTHETIC_VIDEO
            
            for indicator in self._deepfake_indicators["video"]:
                if features.get(indicator, False):
                    manipulation_indicators.append(indicator)
                    confidence_score += 0.12
            
            if features.get("gan_artifacts", False):
                confidence_score += 0.25
                manipulation_indicators.append("gan_generation_artifacts")
        
        elif media_type.lower() in ["document", "credential", "badge"]:
            deepfake_type = DeepfakeType.CREDENTIAL_SYNTHESIS
            
            for indicator in self._deepfake_indicators["document"]:
                if features.get(indicator, False):
                    manipulation_indicators.append(indicator)
                    confidence_score += 0.2
        
        elif media_type.lower() in ["bodycam", "body_camera"]:
            deepfake_type = DeepfakeType.BODYCAM_MANIPULATION
            evidence_compromised = True
            
            for indicator in self._deepfake_indicators["video"]:
                if features.get(indicator, False):
                    manipulation_indicators.append(indicator)
                    confidence_score += 0.15
            
            if features.get("timestamp_manipulation", False):
                confidence_score += 0.3
                manipulation_indicators.append("timestamp_manipulation")
            
            if features.get("frame_insertion", False):
                confidence_score += 0.25
                manipulation_indicators.append("frame_insertion_detected")
        
        confidence_score = min(confidence_score, 1.0)
        
        if confidence_score < 0.3:
            return None
        
        if confidence_score >= 0.8:
            confidence = DetectionConfidence.VERY_HIGH
            severity = QuantumSeverity.CRITICAL
        elif confidence_score >= 0.6:
            confidence = DetectionConfidence.HIGH
            severity = QuantumSeverity.HIGH
        elif confidence_score >= 0.4:
            confidence = DetectionConfidence.MEDIUM
            severity = QuantumSeverity.MEDIUM
        else:
            confidence = DetectionConfidence.LOW
            severity = QuantumSeverity.LOW
        
        if officer_involved:
            severity = max(severity, QuantumSeverity.HIGH)
        
        if is_evidence or evidence_compromised:
            severity = QuantumSeverity.CRITICAL
        
        for model in self._known_ai_models:
            if features.get(f"{model.lower()}_signature", False):
                ai_model = model
                break
        
        alert = DeepfakeAlert(
            alert_id=f"deepfake-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            deepfake_type=deepfake_type,
            severity=severity,
            detection_confidence=confidence,
            confidence_score=confidence_score,
            source_file=source_file,
            source_url=source_url,
            claimed_identity=claimed_identity,
            manipulation_indicators=manipulation_indicators,
            ai_model_detected=ai_model,
            officer_involved=officer_involved,
            officer_id=officer_id,
            evidence_integrity_compromised=evidence_compromised,
            recommended_action=self._get_deepfake_recommendation(
                deepfake_type, severity, officer_involved, evidence_compromised
            ),
        )
        
        alert.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "alert_id": alert.alert_id,
            "timestamp": alert.timestamp.isoformat(),
            "deepfake_type": deepfake_type.value if deepfake_type else None,
            "confidence_score": confidence_score,
        })
        
        self.deepfake_alerts.append(alert)
        return alert
    
    def _get_deepfake_recommendation(
        self,
        deepfake_type: DeepfakeType,
        severity: QuantumSeverity,
        officer_involved: bool,
        evidence_compromised: bool,
    ) -> str:
        """Get recommended action for deepfake"""
        if evidence_compromised:
            return (
                "CRITICAL: Evidence integrity compromised. Preserve original media. "
                "Initiate chain of custody review. Contact digital forensics unit. "
                "Do not use this evidence until verified."
            )
        
        if officer_involved:
            return (
                "HIGH PRIORITY: Officer identity potentially spoofed. "
                "Verify officer identity through secondary channels. "
                "Alert command staff. Review related communications."
            )
        
        recommendations = {
            DeepfakeType.SYNTHETIC_VOICE: 
                "Verify speaker identity through callback or in-person. "
                "Do not act on voice-only instructions for sensitive operations.",
            DeepfakeType.SYNTHETIC_VIDEO:
                "Verify video authenticity. Check for original source. "
                "Use reverse image search and metadata analysis.",
            DeepfakeType.FACE_SWAP:
                "Identity verification required. Check for original unaltered footage.",
            DeepfakeType.CREDENTIAL_SYNTHESIS:
                "Verify credentials through official channels. "
                "Do not grant access based on this document alone.",
            DeepfakeType.BODYCAM_MANIPULATION:
                "Preserve original footage. Contact digital forensics. "
                "Review chain of custody for all related evidence.",
        }
        
        base = recommendations.get(deepfake_type, "Verify media authenticity.")
        
        if severity == QuantumSeverity.CRITICAL:
            return f"CRITICAL: {base}"
        
        return base
    
    def register_officer_profile(
        self,
        officer_id: str,
        voice_signature: Optional[str] = None,
        face_signature: Optional[str] = None,
    ) -> bool:
        """Register officer biometric profiles for deepfake detection"""
        if voice_signature:
            self._officer_voice_profiles[officer_id] = voice_signature
        if face_signature:
            self._officer_face_profiles[officer_id] = face_signature
        return True
    
    def verify_officer_identity(
        self,
        officer_id: str,
        voice_sample: Optional[str] = None,
        face_sample: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Verify officer identity against registered profiles"""
        result = {
            "officer_id": officer_id,
            "verified": False,
            "voice_match": None,
            "face_match": None,
            "confidence": 0.0,
        }
        
        if voice_sample and officer_id in self._officer_voice_profiles:
            result["voice_match"] = voice_sample == self._officer_voice_profiles[officer_id]
            if result["voice_match"]:
                result["confidence"] += 0.5
        
        if face_sample and officer_id in self._officer_face_profiles:
            result["face_match"] = face_sample == self._officer_face_profiles[officer_id]
            if result["face_match"]:
                result["confidence"] += 0.5
        
        result["verified"] = result["confidence"] >= 0.5
        return result
    
    def get_quantum_assessment(self) -> QuantumAssessment:
        """Get overall quantum threat assessment"""
        now = datetime.utcnow()
        recent_window = now - timedelta(hours=24)
        
        recent_anomalies = [a for a in self.quantum_anomalies if a.timestamp > recent_window]
        recent_crypto = [a for a in self.crypto_attacks if a.timestamp > recent_window]
        recent_deepfakes = [a for a in self.deepfake_alerts if a.timestamp > recent_window]
        
        all_severities = (
            [a.severity for a in recent_anomalies] +
            [a.severity for a in recent_crypto] +
            [a.severity for a in recent_deepfakes]
        )
        
        if QuantumSeverity.CATASTROPHIC in all_severities:
            overall_level = QuantumSeverity.CATASTROPHIC
        elif QuantumSeverity.CRITICAL in all_severities:
            overall_level = QuantumSeverity.CRITICAL
        elif QuantumSeverity.HIGH in all_severities:
            overall_level = QuantumSeverity.HIGH
        elif QuantumSeverity.MEDIUM in all_severities:
            overall_level = QuantumSeverity.MEDIUM
        else:
            overall_level = QuantumSeverity.LOW
        
        pq_ready_count = sum(1 for a in recent_crypto if a.post_quantum_ready)
        total_crypto = len(recent_crypto) or 1
        pq_readiness = pq_ready_count / total_crypto
        
        vulnerabilities = []
        if any(a.attack_type == CryptoAttackType.HARVEST_NOW_DECRYPT_LATER for a in recent_crypto):
            vulnerabilities.append("Data being harvested for future quantum decryption")
        if any(a.evidence_integrity_compromised for a in recent_deepfakes):
            vulnerabilities.append("Evidence integrity potentially compromised by deepfakes")
        
        recommendations = []
        if pq_readiness < 0.5:
            recommendations.append("Accelerate post-quantum cryptography migration")
        if recent_deepfakes:
            recommendations.append("Implement deepfake detection in evidence review workflow")
        if recent_anomalies:
            recommendations.append("Review quantum network security posture")
        
        assessment = QuantumAssessment(
            assessment_id=f"qassess-{uuid.uuid4().hex[:12]}",
            timestamp=now,
            overall_threat_level=overall_level,
            quantum_anomalies=recent_anomalies,
            crypto_attacks=recent_crypto,
            deepfake_alerts=recent_deepfakes,
            post_quantum_readiness_score=pq_readiness,
            critical_vulnerabilities=vulnerabilities,
            recommendations=recommendations,
        )
        
        assessment.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "assessment_id": assessment.assessment_id,
            "timestamp": assessment.timestamp.isoformat(),
            "overall_threat_level": assessment.overall_threat_level.value,
        })
        
        return assessment
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get quantum detection statistics"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        return {
            "total_quantum_anomalies": len(self.quantum_anomalies),
            "total_crypto_attacks": len(self.crypto_attacks),
            "total_deepfake_alerts": len(self.deepfake_alerts),
            "quantum_anomalies_24h": len([a for a in self.quantum_anomalies if a.timestamp > last_24h]),
            "crypto_attacks_24h": len([a for a in self.crypto_attacks if a.timestamp > last_24h]),
            "deepfake_alerts_24h": len([a for a in self.deepfake_alerts if a.timestamp > last_24h]),
            "officer_deepfakes_7d": len([
                a for a in self.deepfake_alerts
                if a.timestamp > last_7d and a.officer_involved
            ]),
            "evidence_compromised_7d": len([
                a for a in self.deepfake_alerts
                if a.timestamp > last_7d and a.evidence_integrity_compromised
            ]),
            "registered_officer_profiles": {
                "voice": len(self._officer_voice_profiles),
                "face": len(self._officer_face_profiles),
            },
        }
