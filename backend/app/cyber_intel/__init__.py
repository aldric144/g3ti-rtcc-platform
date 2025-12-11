"""
Phase 29: Cyber Intelligence Shield & Quantum Threat Detection Engine

This module provides comprehensive cyber threat detection, quantum threat analysis,
and information warfare monitoring for the G3TI RTCC-UIP platform.

Components:
- CyberThreatEngine: Network threats, ransomware, endpoint compromise, zero-day detection
- QuantumDetectionEngine: Post-quantum cryptography, quantum traffic, deepfake scanning
- InfoWarfareEngine: Disinformation, rumor detection, police impersonation, crisis manipulation

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from .cyber_threat_engine import (
    CyberThreatEngine,
    ThreatSeverity,
    ThreatType,
    ThreatCategory,
    NetworkThreat,
    RansomwareAlert,
    EndpointCompromise,
    ZeroDayThreat,
    ThreatAssessment,
)

from .quantum_detection_engine import (
    QuantumDetectionEngine,
    QuantumThreatType,
    CryptoAttackType,
    DeepfakeType,
    QuantumAnomaly,
    CryptoAttack,
    DeepfakeAlert,
    QuantumAssessment,
)

from .info_warfare_engine import (
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

__all__ = [
    # Cyber Threat Engine
    "CyberThreatEngine",
    "ThreatSeverity",
    "ThreatType",
    "ThreatCategory",
    "NetworkThreat",
    "RansomwareAlert",
    "EndpointCompromise",
    "ZeroDayThreat",
    "ThreatAssessment",
    # Quantum Detection Engine
    "QuantumDetectionEngine",
    "QuantumThreatType",
    "CryptoAttackType",
    "DeepfakeType",
    "QuantumAnomaly",
    "CryptoAttack",
    "DeepfakeAlert",
    "QuantumAssessment",
    # Info Warfare Engine
    "InfoWarfareEngine",
    "DisinfoType",
    "DisinfoSeverity",
    "DisinfoSource",
    "RumorAlert",
    "ImpersonationAlert",
    "ElectionThreat",
    "CrisisManipulation",
    "DisinfoAssessment",
]
