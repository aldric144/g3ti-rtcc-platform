"""
Cyber Intelligence Module

Provides cyber threat intelligence capabilities including:
- Malware signal detection (stubbed)
- Botnet activity prediction
- Ransomware early warning engine
- Cross-sector vulnerability scanning (API stubs)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import hashlib


class MalwareType(Enum):
    """Types of malware detected."""
    VIRUS = "virus"
    WORM = "worm"
    TROJAN = "trojan"
    RANSOMWARE = "ransomware"
    SPYWARE = "spyware"
    ADWARE = "adware"
    ROOTKIT = "rootkit"
    KEYLOGGER = "keylogger"
    BACKDOOR = "backdoor"
    BOTNET = "botnet"
    RAT = "remote_access_trojan"
    CRYPTOMINER = "cryptominer"
    FILELESS = "fileless"
    APT = "advanced_persistent_threat"
    ZERO_DAY = "zero_day"
    OTHER = "other"


class ThreatSeverity(Enum):
    """Severity levels for cyber threats."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AttackVector(Enum):
    """Attack vectors for cyber threats."""
    PHISHING = "phishing"
    SPEAR_PHISHING = "spear_phishing"
    DRIVE_BY = "drive_by_download"
    WATERING_HOLE = "watering_hole"
    SUPPLY_CHAIN = "supply_chain"
    ZERO_DAY_EXPLOIT = "zero_day_exploit"
    SOCIAL_ENGINEERING = "social_engineering"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    MAN_IN_MIDDLE = "man_in_the_middle"
    DNS_SPOOFING = "dns_spoofing"
    INSIDER = "insider_threat"
    PHYSICAL = "physical_access"
    USB = "usb_device"
    EMAIL_ATTACHMENT = "email_attachment"
    MALVERTISING = "malvertising"
    OTHER = "other"


class SectorType(Enum):
    """Critical infrastructure sectors."""
    ENERGY = "energy"
    WATER = "water"
    TRANSPORTATION = "transportation"
    COMMUNICATIONS = "communications"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    GOVERNMENT = "government"
    DEFENSE = "defense"
    EMERGENCY_SERVICES = "emergency_services"
    FOOD_AGRICULTURE = "food_agriculture"
    CHEMICAL = "chemical"
    NUCLEAR = "nuclear"
    MANUFACTURING = "manufacturing"
    IT = "information_technology"
    OTHER = "other"


class BotnetStatus(Enum):
    """Status of botnet activity."""
    DORMANT = "dormant"
    SCANNING = "scanning"
    RECRUITING = "recruiting"
    ACTIVE = "active"
    ATTACKING = "attacking"
    COMMAND_CONTROL = "command_and_control"
    UNKNOWN = "unknown"


@dataclass
class MalwareSignal:
    """Represents a detected malware signal."""
    signal_id: str
    malware_type: MalwareType
    severity: ThreatSeverity
    name: str
    description: str
    hash_md5: Optional[str]
    hash_sha256: Optional[str]
    file_name: Optional[str]
    file_path: Optional[str]
    source_ip: Optional[str]
    destination_ip: Optional[str]
    attack_vector: AttackVector
    affected_sectors: List[SectorType]
    indicators_of_compromise: List[str]
    detection_method: str
    confidence_score: float
    is_active: bool
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BotnetActivity:
    """Represents detected botnet activity."""
    activity_id: str
    botnet_name: str
    status: BotnetStatus
    estimated_size: int
    command_control_ips: List[str]
    target_sectors: List[SectorType]
    attack_type: str
    geographic_distribution: Dict[str, int]
    communication_protocol: str
    encryption_used: bool
    threat_score: float
    predicted_attack_time: Optional[datetime]
    confidence_score: float
    detected_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RansomwareAlert:
    """Represents a ransomware early warning alert."""
    alert_id: str
    ransomware_family: str
    severity: ThreatSeverity
    attack_vector: AttackVector
    target_sectors: List[SectorType]
    ransom_demand: Optional[float]
    ransom_currency: str
    payment_deadline: Optional[datetime]
    decryption_available: bool
    known_victims: List[str]
    geographic_targets: List[str]
    indicators_of_compromise: List[str]
    mitigation_steps: List[str]
    threat_score: float
    is_active: bool
    first_detected: datetime
    last_activity: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VulnerabilityReport:
    """Represents a vulnerability scan report."""
    report_id: str
    cve_id: Optional[str]
    vulnerability_name: str
    description: str
    severity: ThreatSeverity
    cvss_score: float
    affected_systems: List[str]
    affected_sectors: List[SectorType]
    exploit_available: bool
    patch_available: bool
    patch_url: Optional[str]
    workaround: Optional[str]
    affected_vendors: List[str]
    affected_products: List[str]
    references: List[str]
    discovered_at: datetime
    published_at: Optional[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)


class CyberIntelEngine:
    """
    Cyber Intelligence Engine for detecting and analyzing cyber threats.
    
    Provides capabilities for:
    - Malware signal detection
    - Botnet activity prediction
    - Ransomware early warning
    - Cross-sector vulnerability scanning
    """

    def __init__(self):
        self.malware_signals: Dict[str, MalwareSignal] = {}
        self.botnet_activities: Dict[str, BotnetActivity] = {}
        self.ransomware_alerts: Dict[str, RansomwareAlert] = {}
        self.vulnerability_reports: Dict[str, VulnerabilityReport] = {}
        self.known_iocs: Dict[str, List[str]] = {}
        self.threat_feeds: Dict[str, Dict[str, Any]] = {}

    def detect_malware_signal(
        self,
        malware_type: MalwareType,
        name: str,
        description: str,
        severity: ThreatSeverity = ThreatSeverity.MEDIUM,
        attack_vector: AttackVector = AttackVector.OTHER,
        hash_md5: Optional[str] = None,
        hash_sha256: Optional[str] = None,
        file_name: Optional[str] = None,
        file_path: Optional[str] = None,
        source_ip: Optional[str] = None,
        destination_ip: Optional[str] = None,
        affected_sectors: Optional[List[SectorType]] = None,
        indicators_of_compromise: Optional[List[str]] = None,
        detection_method: str = "signature_based",
        confidence_score: float = 0.8,
    ) -> MalwareSignal:
        """Detect and record a malware signal (stubbed implementation)."""
        signal_id = f"mal-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        signal = MalwareSignal(
            signal_id=signal_id,
            malware_type=malware_type,
            severity=severity,
            name=name,
            description=description,
            hash_md5=hash_md5,
            hash_sha256=hash_sha256,
            file_name=file_name,
            file_path=file_path,
            source_ip=source_ip,
            destination_ip=destination_ip,
            attack_vector=attack_vector,
            affected_sectors=affected_sectors or [],
            indicators_of_compromise=indicators_of_compromise or [],
            detection_method=detection_method,
            confidence_score=confidence_score,
            is_active=True,
            first_seen=now,
            last_seen=now,
        )
        
        self.malware_signals[signal_id] = signal
        
        if indicators_of_compromise:
            for ioc in indicators_of_compromise:
                if ioc not in self.known_iocs:
                    self.known_iocs[ioc] = []
                self.known_iocs[ioc].append(signal_id)
        
        return signal

    def get_malware_signals(
        self,
        malware_type: Optional[MalwareType] = None,
        severity: Optional[ThreatSeverity] = None,
        sector: Optional[SectorType] = None,
        active_only: bool = False,
        limit: int = 100,
    ) -> List[MalwareSignal]:
        """Retrieve malware signals with optional filtering."""
        signals = list(self.malware_signals.values())
        
        if malware_type:
            signals = [s for s in signals if s.malware_type == malware_type]
        
        if severity:
            signals = [s for s in signals if s.severity.value >= severity.value]
        
        if sector:
            signals = [s for s in signals if sector in s.affected_sectors]
        
        if active_only:
            signals = [s for s in signals if s.is_active]
        
        signals.sort(key=lambda x: x.last_seen, reverse=True)
        return signals[:limit]

    def predict_botnet_activity(
        self,
        botnet_name: str,
        command_control_ips: List[str],
        estimated_size: int = 0,
        target_sectors: Optional[List[SectorType]] = None,
        attack_type: str = "ddos",
        communication_protocol: str = "http",
        encryption_used: bool = True,
        geographic_distribution: Optional[Dict[str, int]] = None,
    ) -> BotnetActivity:
        """Predict and track botnet activity."""
        activity_id = f"bot-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        threat_score = self._calculate_botnet_threat_score(
            estimated_size, len(command_control_ips), target_sectors or []
        )
        
        confidence_score = min(0.9, 0.5 + (len(command_control_ips) * 0.05))
        
        status = BotnetStatus.ACTIVE if estimated_size > 1000 else BotnetStatus.SCANNING
        
        activity = BotnetActivity(
            activity_id=activity_id,
            botnet_name=botnet_name,
            status=status,
            estimated_size=estimated_size,
            command_control_ips=command_control_ips,
            target_sectors=target_sectors or [],
            attack_type=attack_type,
            geographic_distribution=geographic_distribution or {},
            communication_protocol=communication_protocol,
            encryption_used=encryption_used,
            threat_score=threat_score,
            predicted_attack_time=None,
            confidence_score=confidence_score,
            detected_at=now,
            updated_at=now,
        )
        
        self.botnet_activities[activity_id] = activity
        return activity

    def _calculate_botnet_threat_score(
        self,
        size: int,
        cc_count: int,
        sectors: List[SectorType],
    ) -> float:
        """Calculate threat score for botnet activity."""
        score = 0.0
        
        if size > 100000:
            score += 40
        elif size > 10000:
            score += 30
        elif size > 1000:
            score += 20
        else:
            score += 10
        
        score += min(20, cc_count * 2)
        
        critical_sectors = [
            SectorType.ENERGY, SectorType.WATER, SectorType.NUCLEAR,
            SectorType.DEFENSE, SectorType.GOVERNMENT
        ]
        for sector in sectors:
            if sector in critical_sectors:
                score += 10
            else:
                score += 5
        
        return min(100, score)

    def get_botnet_activities(
        self,
        status: Optional[BotnetStatus] = None,
        sector: Optional[SectorType] = None,
        min_threat_score: float = 0,
        limit: int = 100,
    ) -> List[BotnetActivity]:
        """Retrieve botnet activities with optional filtering."""
        activities = list(self.botnet_activities.values())
        
        if status:
            activities = [a for a in activities if a.status == status]
        
        if sector:
            activities = [a for a in activities if sector in a.target_sectors]
        
        activities = [a for a in activities if a.threat_score >= min_threat_score]
        
        activities.sort(key=lambda x: x.threat_score, reverse=True)
        return activities[:limit]

    def create_ransomware_alert(
        self,
        ransomware_family: str,
        severity: ThreatSeverity,
        attack_vector: AttackVector,
        target_sectors: Optional[List[SectorType]] = None,
        ransom_demand: Optional[float] = None,
        ransom_currency: str = "BTC",
        payment_deadline: Optional[datetime] = None,
        decryption_available: bool = False,
        known_victims: Optional[List[str]] = None,
        geographic_targets: Optional[List[str]] = None,
        indicators_of_compromise: Optional[List[str]] = None,
        mitigation_steps: Optional[List[str]] = None,
    ) -> RansomwareAlert:
        """Create a ransomware early warning alert."""
        alert_id = f"rw-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        threat_score = self._calculate_ransomware_threat_score(
            severity, target_sectors or [], len(known_victims or [])
        )
        
        alert = RansomwareAlert(
            alert_id=alert_id,
            ransomware_family=ransomware_family,
            severity=severity,
            attack_vector=attack_vector,
            target_sectors=target_sectors or [],
            ransom_demand=ransom_demand,
            ransom_currency=ransom_currency,
            payment_deadline=payment_deadline,
            decryption_available=decryption_available,
            known_victims=known_victims or [],
            geographic_targets=geographic_targets or [],
            indicators_of_compromise=indicators_of_compromise or [],
            mitigation_steps=mitigation_steps or [],
            threat_score=threat_score,
            is_active=True,
            first_detected=now,
            last_activity=now,
        )
        
        self.ransomware_alerts[alert_id] = alert
        return alert

    def _calculate_ransomware_threat_score(
        self,
        severity: ThreatSeverity,
        sectors: List[SectorType],
        victim_count: int,
    ) -> float:
        """Calculate threat score for ransomware."""
        severity_scores = {
            ThreatSeverity.INFO: 10,
            ThreatSeverity.LOW: 20,
            ThreatSeverity.MEDIUM: 40,
            ThreatSeverity.HIGH: 60,
            ThreatSeverity.CRITICAL: 80,
            ThreatSeverity.EMERGENCY: 95,
        }
        
        score = severity_scores.get(severity, 40)
        
        critical_sectors = [
            SectorType.HEALTHCARE, SectorType.ENERGY, SectorType.WATER,
            SectorType.GOVERNMENT, SectorType.EMERGENCY_SERVICES
        ]
        for sector in sectors:
            if sector in critical_sectors:
                score += 5
        
        score += min(15, victim_count * 3)
        
        return min(100, score)

    def get_ransomware_alerts(
        self,
        severity: Optional[ThreatSeverity] = None,
        sector: Optional[SectorType] = None,
        active_only: bool = False,
        limit: int = 100,
    ) -> List[RansomwareAlert]:
        """Retrieve ransomware alerts with optional filtering."""
        alerts = list(self.ransomware_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity.value >= severity.value]
        
        if sector:
            alerts = [a for a in alerts if sector in a.target_sectors]
        
        if active_only:
            alerts = [a for a in alerts if a.is_active]
        
        alerts.sort(key=lambda x: x.threat_score, reverse=True)
        return alerts[:limit]

    def scan_vulnerability(
        self,
        vulnerability_name: str,
        description: str,
        severity: ThreatSeverity,
        cvss_score: float,
        cve_id: Optional[str] = None,
        affected_systems: Optional[List[str]] = None,
        affected_sectors: Optional[List[SectorType]] = None,
        exploit_available: bool = False,
        patch_available: bool = False,
        patch_url: Optional[str] = None,
        workaround: Optional[str] = None,
        affected_vendors: Optional[List[str]] = None,
        affected_products: Optional[List[str]] = None,
        references: Optional[List[str]] = None,
    ) -> VulnerabilityReport:
        """Scan and report a vulnerability (API stub)."""
        report_id = f"vuln-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        report = VulnerabilityReport(
            report_id=report_id,
            cve_id=cve_id,
            vulnerability_name=vulnerability_name,
            description=description,
            severity=severity,
            cvss_score=cvss_score,
            affected_systems=affected_systems or [],
            affected_sectors=affected_sectors or [],
            exploit_available=exploit_available,
            patch_available=patch_available,
            patch_url=patch_url,
            workaround=workaround,
            affected_vendors=affected_vendors or [],
            affected_products=affected_products or [],
            references=references or [],
            discovered_at=now,
            published_at=now if cve_id else None,
        )
        
        self.vulnerability_reports[report_id] = report
        return report

    def get_vulnerability_reports(
        self,
        severity: Optional[ThreatSeverity] = None,
        sector: Optional[SectorType] = None,
        exploit_available: Optional[bool] = None,
        patch_available: Optional[bool] = None,
        limit: int = 100,
    ) -> List[VulnerabilityReport]:
        """Retrieve vulnerability reports with optional filtering."""
        reports = list(self.vulnerability_reports.values())
        
        if severity:
            reports = [r for r in reports if r.severity.value >= severity.value]
        
        if sector:
            reports = [r for r in reports if sector in r.affected_sectors]
        
        if exploit_available is not None:
            reports = [r for r in reports if r.exploit_available == exploit_available]
        
        if patch_available is not None:
            reports = [r for r in reports if r.patch_available == patch_available]
        
        reports.sort(key=lambda x: x.cvss_score, reverse=True)
        return reports[:limit]

    def check_ioc(self, indicator: str) -> List[MalwareSignal]:
        """Check if an indicator of compromise is known."""
        signal_ids = self.known_iocs.get(indicator, [])
        return [self.malware_signals[sid] for sid in signal_ids if sid in self.malware_signals]

    def add_threat_feed(
        self,
        feed_name: str,
        feed_url: str,
        feed_type: str = "stix",
        enabled: bool = True,
    ) -> Dict[str, Any]:
        """Add a threat intelligence feed (stub)."""
        feed_id = f"feed-{uuid.uuid4().hex[:8]}"
        feed = {
            "feed_id": feed_id,
            "name": feed_name,
            "url": feed_url,
            "type": feed_type,
            "enabled": enabled,
            "last_updated": None,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.threat_feeds[feed_id] = feed
        return feed

    def get_threat_feeds(self) -> List[Dict[str, Any]]:
        """Get all configured threat feeds."""
        return list(self.threat_feeds.values())

    def get_metrics(self) -> Dict[str, Any]:
        """Get cyber intelligence metrics."""
        active_malware = len([s for s in self.malware_signals.values() if s.is_active])
        active_botnets = len([b for b in self.botnet_activities.values() 
                            if b.status in [BotnetStatus.ACTIVE, BotnetStatus.ATTACKING]])
        active_ransomware = len([r for r in self.ransomware_alerts.values() if r.is_active])
        unpatched_vulns = len([v for v in self.vulnerability_reports.values() 
                              if not v.patch_available])
        
        return {
            "total_malware_signals": len(self.malware_signals),
            "active_malware_signals": active_malware,
            "total_botnet_activities": len(self.botnet_activities),
            "active_botnets": active_botnets,
            "total_ransomware_alerts": len(self.ransomware_alerts),
            "active_ransomware": active_ransomware,
            "total_vulnerability_reports": len(self.vulnerability_reports),
            "unpatched_vulnerabilities": unpatched_vulns,
            "total_iocs": len(self.known_iocs),
            "total_threat_feeds": len(self.threat_feeds),
            "by_malware_type": self._count_by_malware_type(),
            "by_severity": self._count_by_severity(),
            "by_sector": self._count_by_sector(),
        }

    def _count_by_malware_type(self) -> Dict[str, int]:
        """Count signals by malware type."""
        counts: Dict[str, int] = {}
        for signal in self.malware_signals.values():
            key = signal.malware_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _count_by_severity(self) -> Dict[str, int]:
        """Count all threats by severity."""
        counts: Dict[str, int] = {}
        for signal in self.malware_signals.values():
            key = signal.severity.value
            counts[key] = counts.get(key, 0) + 1
        for alert in self.ransomware_alerts.values():
            key = alert.severity.value
            counts[key] = counts.get(key, 0) + 1
        for report in self.vulnerability_reports.values():
            key = report.severity.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _count_by_sector(self) -> Dict[str, int]:
        """Count threats by affected sector."""
        counts: Dict[str, int] = {}
        for signal in self.malware_signals.values():
            for sector in signal.affected_sectors:
                key = sector.value
                counts[key] = counts.get(key, 0) + 1
        for alert in self.ransomware_alerts.values():
            for sector in alert.target_sectors:
                key = sector.value
                counts[key] = counts.get(key, 0) + 1
        return counts
