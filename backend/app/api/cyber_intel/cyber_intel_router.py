"""
Cyber Intelligence API Router

Provides REST API endpoints for cyber threat detection, quantum threat analysis,
and information warfare monitoring.

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/cyber-intel", tags=["Cyber Intelligence"])


class ThreatSeverityEnum(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DisinfoSourceEnum(str, Enum):
    FACEBOOK = "FACEBOOK"
    TWITTER_X = "TWITTER_X"
    INSTAGRAM = "INSTAGRAM"
    TIKTOK = "TIKTOK"
    YOUTUBE = "YOUTUBE"
    TELEGRAM = "TELEGRAM"
    WHATSAPP = "WHATSAPP"
    NEXTDOOR = "NEXTDOOR"
    REDDIT = "REDDIT"
    LOCAL_NEWS_COMMENTS = "LOCAL_NEWS_COMMENTS"
    EMAIL = "EMAIL"
    SMS = "SMS"
    WEBSITE = "WEBSITE"
    UNKNOWN = "UNKNOWN"


class NetworkScanRequest(BaseModel):
    source_ip: str = Field(..., description="Source IP address")
    destination_ip: str = Field(..., description="Destination IP address")
    source_port: int = Field(..., ge=0, le=65535, description="Source port")
    destination_port: int = Field(..., ge=0, le=65535, description="Destination port")
    protocol: str = Field(..., description="Network protocol (TCP, UDP, etc.)")
    payload: Optional[str] = Field(None, description="Optional payload data")
    packet_count: int = Field(1, ge=1, description="Number of packets")
    bytes_transferred: int = Field(0, ge=0, description="Bytes transferred")


class NetworkScanResponse(BaseModel):
    threat_detected: bool
    threat_id: Optional[str] = None
    threat_type: Optional[str] = None
    severity: Optional[ThreatSeverityEnum] = None
    detection_method: Optional[str] = None
    signature_name: Optional[str] = None
    recommended_action: Optional[str] = None
    chain_of_custody_hash: Optional[str] = None
    timestamp: datetime


class RansomwareScanRequest(BaseModel):
    hostname: str = Field(..., description="Affected hostname")
    path: str = Field(..., description="Affected file path")
    file_modifications_per_minute: int = Field(..., ge=0, description="File modifications per minute")
    file_extensions: List[str] = Field(default_factory=list, description="File extensions observed")
    file_names: List[str] = Field(default_factory=list, description="File names observed")


class RansomwareScanResponse(BaseModel):
    ransomware_detected: bool
    alert_id: Optional[str] = None
    severity: Optional[ThreatSeverityEnum] = None
    ransomware_family: Optional[str] = None
    encryption_detected: bool = False
    files_affected: int = 0
    recommended_action: Optional[str] = None
    chain_of_custody_hash: Optional[str] = None
    timestamp: datetime


class QuantumScanRequest(BaseModel):
    algorithm: str = Field(..., description="Cryptographic algorithm")
    key_size: int = Field(..., ge=0, description="Key size in bits")
    operation_type: str = Field(..., description="Operation type (encrypt, decrypt, key_exchange)")
    source_system: str = Field(..., description="Source system identifier")
    data_classification: Optional[str] = Field(None, description="Data classification level")


class QuantumScanResponse(BaseModel):
    threat_detected: bool
    attack_id: Optional[str] = None
    attack_type: Optional[str] = None
    severity: Optional[str] = None
    target_algorithm: Optional[str] = None
    post_quantum_ready: bool = False
    estimated_decrypt_timeline: Optional[str] = None
    recommended_action: Optional[str] = None
    chain_of_custody_hash: Optional[str] = None
    timestamp: datetime


class DeepfakeScanRequest(BaseModel):
    media_type: str = Field(..., description="Media type (audio, video, image, document, bodycam)")
    source_file: Optional[str] = Field(None, description="Source file path")
    source_url: Optional[str] = Field(None, description="Source URL")
    claimed_identity: Optional[str] = Field(None, description="Claimed identity in media")
    officer_id: Optional[str] = Field(None, description="Officer ID if officer-related")
    is_evidence: bool = Field(False, description="Whether this is evidence material")
    analysis_features: Optional[Dict[str, Any]] = Field(None, description="Analysis feature flags")


class DeepfakeScanResponse(BaseModel):
    deepfake_detected: bool
    alert_id: Optional[str] = None
    deepfake_type: Optional[str] = None
    severity: Optional[str] = None
    confidence_score: float = 0.0
    manipulation_indicators: List[str] = Field(default_factory=list)
    ai_model_detected: Optional[str] = None
    officer_involved: bool = False
    evidence_integrity_compromised: bool = False
    recommended_action: Optional[str] = None
    chain_of_custody_hash: Optional[str] = None
    timestamp: datetime


class InfoWarfareScanRequest(BaseModel):
    scan_type: str = Field(..., description="Type of scan (rumor, impersonation, election, crisis)")
    content: Optional[str] = Field(None, description="Content to analyze")
    content_samples: Optional[List[str]] = Field(None, description="Multiple content samples")
    source_platform: Optional[DisinfoSourceEnum] = Field(None, description="Source platform")
    source_platforms: Optional[List[DisinfoSourceEnum]] = Field(None, description="Multiple source platforms")
    account_name: Optional[str] = Field(None, description="Account name for impersonation check")
    account_url: Optional[str] = Field(None, description="Account URL")
    share_count: int = Field(0, ge=0, description="Share count")
    reach_estimate: int = Field(0, ge=0, description="Estimated reach")
    hashtags: Optional[List[str]] = Field(None, description="Hashtags")
    account_metadata: Optional[List[Dict[str, Any]]] = Field(None, description="Account metadata for bot detection")
    crisis_type: Optional[str] = Field(None, description="Crisis type for crisis manipulation")


class InfoWarfareScanResponse(BaseModel):
    threat_detected: bool
    alert_id: Optional[str] = None
    disinfo_type: Optional[str] = None
    severity: Optional[str] = None
    viral_velocity: Optional[float] = None
    bot_network_detected: bool = False
    community_tension_score: float = 0.0
    recommended_action: Optional[str] = None
    chain_of_custody_hash: Optional[str] = None
    timestamp: datetime


class ThreatOverview(BaseModel):
    overall_threat_level: str
    network_threats_24h: int
    ransomware_alerts_24h: int
    quantum_threats_24h: int
    deepfake_alerts_24h: int
    disinfo_alerts_24h: int
    critical_alerts: int
    active_incidents: int
    post_quantum_readiness: float
    community_tension_index: float
    recommendations: List[str]
    timestamp: datetime


class AlertItem(BaseModel):
    alert_id: str
    alert_type: str
    severity: str
    description: str
    source: Optional[str] = None
    timestamp: datetime
    recommended_action: str
    chain_of_custody_hash: str


class AlertsResponse(BaseModel):
    total_alerts: int
    critical_alerts: int
    alerts: List[AlertItem]
    timestamp: datetime


class ThreatItem(BaseModel):
    threat_id: str
    threat_type: str
    category: str
    severity: str
    source: str
    target: Optional[str] = None
    description: str
    timestamp: datetime
    status: str
    chain_of_custody_hash: str


class ThreatsResponse(BaseModel):
    total_threats: int
    threats: List[ThreatItem]
    timestamp: datetime


def _get_cyber_threat_engine():
    """Get CyberThreatEngine instance"""
    from ...cyber_intel.cyber_threat_engine import CyberThreatEngine
    return CyberThreatEngine()


def _get_quantum_detection_engine():
    """Get QuantumDetectionEngine instance"""
    from ...cyber_intel.quantum_detection_engine import QuantumDetectionEngine
    return QuantumDetectionEngine()


def _get_info_warfare_engine():
    """Get InfoWarfareEngine instance"""
    from ...cyber_intel.info_warfare_engine import InfoWarfareEngine
    return InfoWarfareEngine()


@router.get("/overview", response_model=ThreatOverview)
async def get_cyber_intel_overview():
    """
    Get overall cyber intelligence overview
    
    Returns aggregated threat assessment across all cyber intel engines.
    """
    cyber_engine = _get_cyber_threat_engine()
    quantum_engine = _get_quantum_detection_engine()
    info_engine = _get_info_warfare_engine()
    
    cyber_stats = cyber_engine.get_statistics()
    quantum_stats = quantum_engine.get_statistics()
    info_stats = info_engine.get_statistics()
    
    cyber_assessment = cyber_engine.get_threat_assessment()
    quantum_assessment = quantum_engine.get_quantum_assessment()
    info_assessment = info_engine.get_disinfo_assessment()
    
    severity_order = ["INFORMATIONAL", "LOW", "MEDIUM", "HIGH", "CRITICAL", "CATASTROPHIC", "EMERGENCY"]
    
    all_levels = [
        cyber_assessment.overall_threat_level.name,
        quantum_assessment.overall_threat_level.name,
        info_assessment.overall_threat_level.name,
    ]
    
    overall_level = max(all_levels, key=lambda x: severity_order.index(x) if x in severity_order else 0)
    
    recommendations = (
        cyber_assessment.recommendations +
        quantum_assessment.recommendations +
        info_assessment.recommendations
    )
    
    return ThreatOverview(
        overall_threat_level=overall_level,
        network_threats_24h=cyber_stats["network_threats_24h"],
        ransomware_alerts_24h=cyber_stats["ransomware_alerts_24h"],
        quantum_threats_24h=quantum_stats["quantum_anomalies_24h"] + quantum_stats["crypto_attacks_24h"],
        deepfake_alerts_24h=quantum_stats["deepfake_alerts_24h"],
        disinfo_alerts_24h=info_stats["rumor_alerts_24h"] + info_stats["impersonation_alerts_24h"],
        critical_alerts=cyber_assessment.critical_alerts,
        active_incidents=cyber_assessment.active_incidents,
        post_quantum_readiness=quantum_assessment.post_quantum_readiness_score,
        community_tension_index=info_assessment.community_tension_index,
        recommendations=recommendations[:10],
        timestamp=datetime.utcnow(),
    )


@router.get("/threats", response_model=ThreatsResponse)
async def get_threats(
    category: Optional[str] = Query(None, description="Filter by category (network, quantum, disinfo)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of threats to return"),
):
    """
    Get list of detected threats
    
    Returns threats from all cyber intel engines with optional filtering.
    """
    cyber_engine = _get_cyber_threat_engine()
    quantum_engine = _get_quantum_detection_engine()
    info_engine = _get_info_warfare_engine()
    
    threats = []
    
    if category is None or category == "network":
        for threat in cyber_engine.network_threats[-limit:]:
            threats.append(ThreatItem(
                threat_id=threat.threat_id,
                threat_type=threat.threat_type.value,
                category="NETWORK",
                severity=threat.severity.name,
                source=threat.source_ip,
                target=threat.destination_ip,
                description=threat.signature_name or f"{threat.threat_type.value} detected",
                timestamp=threat.timestamp,
                status=threat.status.value,
                chain_of_custody_hash=threat.chain_of_custody_hash,
            ))
        
        for alert in cyber_engine.ransomware_alerts[-limit:]:
            threats.append(ThreatItem(
                threat_id=alert.alert_id,
                threat_type="RANSOMWARE",
                category="ENDPOINT",
                severity=alert.severity.name,
                source=alert.affected_host,
                target=alert.affected_path,
                description=f"Ransomware: {alert.ransomware_family or 'Unknown'}",
                timestamp=alert.timestamp,
                status=alert.status.value,
                chain_of_custody_hash=alert.chain_of_custody_hash,
            ))
    
    if category is None or category == "quantum":
        for anomaly in quantum_engine.quantum_anomalies[-limit:]:
            threats.append(ThreatItem(
                threat_id=anomaly.anomaly_id,
                threat_type=anomaly.threat_type.value,
                category="QUANTUM",
                severity=anomaly.severity.name,
                source=anomaly.source_identifier,
                description=anomaly.anomaly_description,
                timestamp=anomaly.timestamp,
                status="DETECTED",
                chain_of_custody_hash=anomaly.chain_of_custody_hash,
            ))
        
        for attack in quantum_engine.crypto_attacks[-limit:]:
            threats.append(ThreatItem(
                threat_id=attack.attack_id,
                threat_type=attack.attack_type.value,
                category="CRYPTO",
                severity=attack.severity.name,
                source=attack.target_algorithm,
                description=attack.attack_vector,
                timestamp=attack.timestamp,
                status="DETECTED",
                chain_of_custody_hash=attack.chain_of_custody_hash,
            ))
    
    if category is None or category == "disinfo":
        for alert in info_engine.rumor_alerts[-limit:]:
            threats.append(ThreatItem(
                threat_id=alert.alert_id,
                threat_type=alert.disinfo_type.value,
                category="DISINFO",
                severity=alert.severity.name,
                source=alert.source_platform.value,
                description=alert.content_summary[:100],
                timestamp=alert.timestamp,
                status="DETECTED",
                chain_of_custody_hash=alert.chain_of_custody_hash,
            ))
    
    if severity:
        threats = [t for t in threats if t.severity == severity.upper()]
    
    threats.sort(key=lambda x: x.timestamp, reverse=True)
    threats = threats[:limit]
    
    return ThreatsResponse(
        total_threats=len(threats),
        threats=threats,
        timestamp=datetime.utcnow(),
    )


@router.post("/scan/network", response_model=NetworkScanResponse)
async def scan_network_traffic(request: NetworkScanRequest):
    """
    Scan network traffic for threats
    
    Analyzes network traffic for intrusions, exploits, and malicious activity.
    """
    engine = _get_cyber_threat_engine()
    
    threat = engine.scan_network_traffic(
        source_ip=request.source_ip,
        destination_ip=request.destination_ip,
        source_port=request.source_port,
        destination_port=request.destination_port,
        protocol=request.protocol,
        payload=request.payload,
        packet_count=request.packet_count,
        bytes_transferred=request.bytes_transferred,
    )
    
    if threat:
        return NetworkScanResponse(
            threat_detected=True,
            threat_id=threat.threat_id,
            threat_type=threat.threat_type.value,
            severity=ThreatSeverityEnum(threat.severity.name),
            detection_method=threat.detection_method.value,
            signature_name=threat.signature_name,
            recommended_action=threat.recommended_action,
            chain_of_custody_hash=threat.chain_of_custody_hash,
            timestamp=threat.timestamp,
        )
    
    return NetworkScanResponse(
        threat_detected=False,
        timestamp=datetime.utcnow(),
    )


@router.post("/scan/ransomware", response_model=RansomwareScanResponse)
async def scan_for_ransomware(request: RansomwareScanRequest):
    """
    Scan for ransomware activity
    
    Detects ransomware based on file modification patterns and signatures.
    """
    engine = _get_cyber_threat_engine()
    
    alert = engine.detect_ransomware(
        hostname=request.hostname,
        path=request.path,
        file_modifications_per_minute=request.file_modifications_per_minute,
        file_extensions=request.file_extensions,
        file_names=request.file_names,
    )
    
    if alert:
        return RansomwareScanResponse(
            ransomware_detected=True,
            alert_id=alert.alert_id,
            severity=ThreatSeverityEnum(alert.severity.name),
            ransomware_family=alert.ransomware_family,
            encryption_detected=alert.encryption_detected,
            files_affected=alert.files_affected,
            recommended_action=alert.recommended_action,
            chain_of_custody_hash=alert.chain_of_custody_hash,
            timestamp=alert.timestamp,
        )
    
    return RansomwareScanResponse(
        ransomware_detected=False,
        timestamp=datetime.utcnow(),
    )


@router.post("/scan/quantum", response_model=QuantumScanResponse)
async def scan_quantum_threats(request: QuantumScanRequest):
    """
    Scan for quantum-related threats
    
    Monitors cryptographic operations for quantum vulnerability.
    """
    engine = _get_quantum_detection_engine()
    
    attack = engine.monitor_crypto_traffic(
        algorithm=request.algorithm,
        key_size=request.key_size,
        operation_type=request.operation_type,
        source_system=request.source_system,
        data_classification=request.data_classification,
    )
    
    if attack:
        return QuantumScanResponse(
            threat_detected=True,
            attack_id=attack.attack_id,
            attack_type=attack.attack_type.value,
            severity=attack.severity.name,
            target_algorithm=attack.target_algorithm,
            post_quantum_ready=attack.post_quantum_ready,
            estimated_decrypt_timeline=attack.estimated_decrypt_timeline,
            recommended_action=attack.recommended_action,
            chain_of_custody_hash=attack.chain_of_custody_hash,
            timestamp=attack.timestamp,
        )
    
    return QuantumScanResponse(
        threat_detected=False,
        timestamp=datetime.utcnow(),
    )


@router.post("/scan/deepfake", response_model=DeepfakeScanResponse)
async def scan_for_deepfake(request: DeepfakeScanRequest):
    """
    Scan media for deepfake manipulation
    
    Analyzes audio, video, and images for synthetic manipulation.
    """
    engine = _get_quantum_detection_engine()
    
    alert = engine.scan_for_deepfake(
        media_type=request.media_type,
        source_file=request.source_file,
        source_url=request.source_url,
        claimed_identity=request.claimed_identity,
        analysis_features=request.analysis_features,
        officer_id=request.officer_id,
        is_evidence=request.is_evidence,
    )
    
    if alert:
        return DeepfakeScanResponse(
            deepfake_detected=True,
            alert_id=alert.alert_id,
            deepfake_type=alert.deepfake_type.value,
            severity=alert.severity.name,
            confidence_score=alert.confidence_score,
            manipulation_indicators=alert.manipulation_indicators,
            ai_model_detected=alert.ai_model_detected,
            officer_involved=alert.officer_involved,
            evidence_integrity_compromised=alert.evidence_integrity_compromised,
            recommended_action=alert.recommended_action,
            chain_of_custody_hash=alert.chain_of_custody_hash,
            timestamp=alert.timestamp,
        )
    
    return DeepfakeScanResponse(
        deepfake_detected=False,
        timestamp=datetime.utcnow(),
    )


@router.post("/scan/info-warfare", response_model=InfoWarfareScanResponse)
async def scan_info_warfare(request: InfoWarfareScanRequest):
    """
    Scan for information warfare and disinformation
    
    Detects rumors, impersonation, election interference, and crisis manipulation.
    """
    engine = _get_info_warfare_engine()
    
    alert = None
    
    if request.scan_type == "rumor" and request.content:
        from ...cyber_intel.info_warfare_engine import DisinfoSource
        platform = DisinfoSource[request.source_platform.value] if request.source_platform else DisinfoSource.UNKNOWN
        
        alert = engine.detect_rumor_panic(
            content=request.content,
            source_platform=platform,
            share_count=request.share_count,
            reach_estimate=request.reach_estimate,
            hashtags=request.hashtags,
        )
        
        if alert:
            return InfoWarfareScanResponse(
                threat_detected=True,
                alert_id=alert.alert_id,
                disinfo_type=alert.disinfo_type.value,
                severity=alert.severity.name,
                viral_velocity=alert.viral_velocity,
                recommended_action=alert.recommended_action,
                chain_of_custody_hash=alert.chain_of_custody_hash,
                timestamp=alert.timestamp,
            )
    
    elif request.scan_type == "impersonation" and request.account_name:
        from ...cyber_intel.info_warfare_engine import DisinfoSource
        platform = DisinfoSource[request.source_platform.value] if request.source_platform else DisinfoSource.UNKNOWN
        
        alert = engine.detect_police_impersonation(
            account_name=request.account_name,
            account_url=request.account_url,
            source_platform=platform,
            content_samples=request.content_samples or [],
        )
        
        if alert:
            return InfoWarfareScanResponse(
                threat_detected=True,
                alert_id=alert.alert_id,
                disinfo_type=alert.disinfo_type.value,
                severity=alert.severity.name,
                recommended_action=alert.recommended_action,
                chain_of_custody_hash=alert.chain_of_custody_hash,
                timestamp=alert.timestamp,
            )
    
    elif request.scan_type == "election" and request.content_samples:
        from ...cyber_intel.info_warfare_engine import DisinfoSource
        platforms = [DisinfoSource[p.value] for p in (request.source_platforms or [])]
        
        alert = engine.detect_election_interference(
            content_samples=request.content_samples,
            source_platforms=platforms,
            account_metadata=request.account_metadata or [],
        )
        
        if alert:
            return InfoWarfareScanResponse(
                threat_detected=True,
                alert_id=alert.threat_id,
                disinfo_type=alert.disinfo_type.value,
                severity=alert.severity.name,
                bot_network_detected=alert.bot_network_detected,
                recommended_action=alert.recommended_action,
                chain_of_custody_hash=alert.chain_of_custody_hash,
                timestamp=alert.timestamp,
            )
    
    elif request.scan_type == "crisis" and request.content_samples and request.crisis_type:
        from ...cyber_intel.info_warfare_engine import DisinfoSource
        platforms = [DisinfoSource[p.value] for p in (request.source_platforms or [])]
        
        alert = engine.detect_crisis_manipulation(
            crisis_type=request.crisis_type,
            content_samples=request.content_samples,
            source_platforms=platforms,
        )
        
        if alert:
            return InfoWarfareScanResponse(
                threat_detected=True,
                alert_id=alert.manipulation_id,
                disinfo_type=alert.disinfo_type.value,
                severity=alert.severity.name,
                community_tension_score=alert.community_tension_score,
                recommended_action=alert.recommended_action,
                chain_of_custody_hash=alert.chain_of_custody_hash,
                timestamp=alert.timestamp,
            )
    
    return InfoWarfareScanResponse(
        threat_detected=False,
        timestamp=datetime.utcnow(),
    )


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts"),
):
    """
    Get all active alerts
    
    Returns alerts from all cyber intel engines.
    """
    cyber_engine = _get_cyber_threat_engine()
    quantum_engine = _get_quantum_detection_engine()
    info_engine = _get_info_warfare_engine()
    
    alerts = []
    
    for threat in cyber_engine.network_threats[-limit:]:
        alerts.append(AlertItem(
            alert_id=threat.threat_id,
            alert_type="NETWORK_THREAT",
            severity=threat.severity.name,
            description=f"{threat.threat_type.value}: {threat.signature_name or 'Detected'}",
            source=threat.source_ip,
            timestamp=threat.timestamp,
            recommended_action=threat.recommended_action,
            chain_of_custody_hash=threat.chain_of_custody_hash,
        ))
    
    for alert in cyber_engine.ransomware_alerts[-limit:]:
        alerts.append(AlertItem(
            alert_id=alert.alert_id,
            alert_type="RANSOMWARE",
            severity=alert.severity.name,
            description=f"Ransomware detected: {alert.ransomware_family or 'Unknown'}",
            source=alert.affected_host,
            timestamp=alert.timestamp,
            recommended_action=alert.recommended_action,
            chain_of_custody_hash=alert.chain_of_custody_hash,
        ))
    
    for alert in quantum_engine.deepfake_alerts[-limit:]:
        alerts.append(AlertItem(
            alert_id=alert.alert_id,
            alert_type="DEEPFAKE",
            severity=alert.severity.name,
            description=f"Deepfake detected: {alert.deepfake_type.value}",
            source=alert.source_url or alert.source_file,
            timestamp=alert.timestamp,
            recommended_action=alert.recommended_action,
            chain_of_custody_hash=alert.chain_of_custody_hash,
        ))
    
    for alert in info_engine.rumor_alerts[-limit:]:
        alerts.append(AlertItem(
            alert_id=alert.alert_id,
            alert_type="DISINFORMATION",
            severity=alert.severity.name,
            description=f"{alert.disinfo_type.value}: {alert.content_summary[:50]}...",
            source=alert.source_platform.value,
            timestamp=alert.timestamp,
            recommended_action=alert.recommended_action,
            chain_of_custody_hash=alert.chain_of_custody_hash,
        ))
    
    for alert in info_engine.impersonation_alerts[-limit:]:
        alerts.append(AlertItem(
            alert_id=alert.alert_id,
            alert_type="IMPERSONATION",
            severity=alert.severity.name,
            description=f"Police impersonation: {alert.fake_page_name}",
            source=alert.source_platform.value,
            timestamp=alert.timestamp,
            recommended_action=alert.recommended_action,
            chain_of_custody_hash=alert.chain_of_custody_hash,
        ))
    
    if severity:
        alerts = [a for a in alerts if a.severity == severity.upper()]
    
    if alert_type:
        alerts = [a for a in alerts if a.alert_type == alert_type.upper()]
    
    alerts.sort(key=lambda x: x.timestamp, reverse=True)
    alerts = alerts[:limit]
    
    critical_count = sum(1 for a in alerts if a.severity in ["CRITICAL", "EMERGENCY", "CATASTROPHIC"])
    
    return AlertsResponse(
        total_alerts=len(alerts),
        critical_alerts=critical_count,
        alerts=alerts,
        timestamp=datetime.utcnow(),
    )
