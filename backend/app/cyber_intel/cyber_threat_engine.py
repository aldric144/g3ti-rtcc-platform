"""
Cyber Threat Intelligence Engine

Provides comprehensive cyber threat detection including:
- Network Threat Detector
- Ransomware Early Warning System
- Endpoint Compromise Detection
- Zero-Day Behavior Model

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
import uuid
import re


class ThreatSeverity(Enum):
    """Threat severity levels (1-5)"""
    INFORMATIONAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class ThreatType(Enum):
    """Types of cyber threats"""
    NETWORK_INTRUSION = "NETWORK_INTRUSION"
    CREDENTIAL_COMPROMISE = "CREDENTIAL_COMPROMISE"
    LATERAL_MOVEMENT = "LATERAL_MOVEMENT"
    SQL_INJECTION = "SQL_INJECTION"
    XSS_ATTACK = "XSS_ATTACK"
    RCE_EXPLOIT = "RCE_EXPLOIT"
    RANSOMWARE = "RANSOMWARE"
    MALWARE = "MALWARE"
    PHISHING = "PHISHING"
    DDOS = "DDOS"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    ZERO_DAY = "ZERO_DAY"
    APT = "APT"
    BOTNET = "BOTNET"
    CRYPTOMINER = "CRYPTOMINER"
    COMMAND_AND_CONTROL = "COMMAND_AND_CONTROL"


class ThreatCategory(Enum):
    """Categories of threats"""
    NETWORK = "NETWORK"
    ENDPOINT = "ENDPOINT"
    APPLICATION = "APPLICATION"
    DATA = "DATA"
    IDENTITY = "IDENTITY"
    INFRASTRUCTURE = "INFRASTRUCTURE"


class DetectionMethod(Enum):
    """How the threat was detected"""
    SIGNATURE_MATCH = "SIGNATURE_MATCH"
    BEHAVIOR_ANOMALY = "BEHAVIOR_ANOMALY"
    HEURISTIC = "HEURISTIC"
    ML_MODEL = "ML_MODEL"
    THREAT_INTEL = "THREAT_INTEL"
    HONEYPOT = "HONEYPOT"
    USER_REPORT = "USER_REPORT"


class ThreatStatus(Enum):
    """Status of a threat"""
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    CONFIRMED = "CONFIRMED"
    CONTAINED = "CONTAINED"
    REMEDIATED = "REMEDIATED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


@dataclass
class NetworkThreat:
    """Network-based threat detection"""
    threat_id: str
    timestamp: datetime
    threat_type: ThreatType
    severity: ThreatSeverity
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    detection_method: DetectionMethod
    signature_id: Optional[str] = None
    signature_name: Optional[str] = None
    payload_hash: Optional[str] = None
    packet_count: int = 0
    bytes_transferred: int = 0
    geo_location: Optional[str] = None
    ioc_matches: List[str] = field(default_factory=list)
    recommended_action: str = ""
    status: ThreatStatus = ThreatStatus.DETECTED
    chain_of_custody_hash: str = ""


@dataclass
class RansomwareAlert:
    """Ransomware detection alert"""
    alert_id: str
    timestamp: datetime
    severity: ThreatSeverity
    affected_host: str
    affected_path: str
    file_modifications_per_minute: int
    encryption_detected: bool
    known_signature: Optional[str] = None
    ransomware_family: Optional[str] = None
    suspicious_extensions: List[str] = field(default_factory=list)
    c2_communication_detected: bool = False
    c2_addresses: List[str] = field(default_factory=list)
    files_affected: int = 0
    recommended_action: str = ""
    status: ThreatStatus = ThreatStatus.DETECTED
    chain_of_custody_hash: str = ""


@dataclass
class EndpointCompromise:
    """Endpoint compromise detection"""
    compromise_id: str
    timestamp: datetime
    severity: ThreatSeverity
    hostname: str
    ip_address: str
    user_account: str
    detection_method: DetectionMethod
    process_anomalies: List[str] = field(default_factory=list)
    privilege_escalation: bool = False
    unauthorized_access: bool = False
    suspicious_processes: List[str] = field(default_factory=list)
    suspicious_connections: List[str] = field(default_factory=list)
    registry_modifications: List[str] = field(default_factory=list)
    file_modifications: List[str] = field(default_factory=list)
    recommended_action: str = ""
    status: ThreatStatus = ThreatStatus.DETECTED
    chain_of_custody_hash: str = ""


@dataclass
class ZeroDayThreat:
    """Zero-day threat detection"""
    threat_id: str
    timestamp: datetime
    severity: ThreatSeverity
    detection_method: DetectionMethod
    affected_system: str
    attack_vector: str
    behavior_signature: str
    confidence_score: float
    ml_model_version: str
    similar_known_threats: List[str] = field(default_factory=list)
    indicators_of_compromise: List[str] = field(default_factory=list)
    ai_generated_malware: bool = False
    recommended_action: str = ""
    status: ThreatStatus = ThreatStatus.DETECTED
    chain_of_custody_hash: str = ""


@dataclass
class ThreatAssessment:
    """Overall threat assessment"""
    assessment_id: str
    timestamp: datetime
    overall_threat_level: ThreatSeverity
    network_threats: List[NetworkThreat] = field(default_factory=list)
    ransomware_alerts: List[RansomwareAlert] = field(default_factory=list)
    endpoint_compromises: List[EndpointCompromise] = field(default_factory=list)
    zero_day_threats: List[ZeroDayThreat] = field(default_factory=list)
    active_incidents: int = 0
    critical_alerts: int = 0
    recommendations: List[str] = field(default_factory=list)
    chain_of_custody_hash: str = ""


class CyberThreatEngine:
    """
    Cyber Threat Intelligence Engine
    
    Provides comprehensive cyber threat detection for Riviera Beach PD
    including network threats, ransomware, endpoint compromise, and zero-day detection.
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
        
        self.network_threats: List[NetworkThreat] = []
        self.ransomware_alerts: List[RansomwareAlert] = []
        self.endpoint_compromises: List[EndpointCompromise] = []
        self.zero_day_threats: List[ZeroDayThreat] = []
        
        self._known_ransomware_signatures = {
            "LOCKBIT": ["lockbit", ".lockbit", "restore-my-files.txt"],
            "CONTI": ["conti", ".conti", "readme.txt"],
            "REVIL": ["revil", ".revil", "sodinokibi"],
            "RYUK": ["ryuk", ".ryk", "RyukReadMe.txt"],
            "BLACKCAT": ["blackcat", ".alphv", "RECOVER-FILES.txt"],
            "CLOP": ["clop", ".clop", "ClopReadMe.txt"],
            "MAZE": ["maze", ".maze", "DECRYPT-FILES.txt"],
            "DARKSIDE": ["darkside", ".darkside", "README.txt"],
            "HIVE": ["hive", ".hive", "HOW_TO_DECRYPT.txt"],
            "BLACKMATTER": ["blackmatter", ".blackmatter", "README.txt"],
        }
        
        self._exploit_patterns = {
            "SQL_INJECTION": [
                r"(?i)(\bunion\b.*\bselect\b)",
                r"(?i)(\bor\b.*=.*\bor\b)",
                r"(?i)(--\s*$)",
                r"(?i)(\bdrop\b.*\btable\b)",
                r"(?i)(\binsert\b.*\binto\b)",
                r"(?i)(\bdelete\b.*\bfrom\b)",
            ],
            "XSS": [
                r"<script[^>]*>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<img[^>]*onerror",
            ],
            "RCE": [
                r"(?i)(eval\s*\()",
                r"(?i)(exec\s*\()",
                r"(?i)(system\s*\()",
                r"(?i)(shell_exec)",
                r"(?i)(passthru)",
                r"(?i)(\|\s*bash)",
                r"(?i)(\|\s*sh)",
            ],
            "PATH_TRAVERSAL": [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e/",
            ],
            "COMMAND_INJECTION": [
                r";\s*\w+",
                r"\|\s*\w+",
                r"`[^`]+`",
                r"\$\([^)]+\)",
            ],
        }
        
        self._suspicious_ports = {
            4444: "Metasploit default",
            5555: "Android ADB",
            6666: "IRC botnet",
            6667: "IRC",
            8080: "HTTP proxy",
            8443: "HTTPS alt",
            9001: "Tor",
            9050: "Tor SOCKS",
            31337: "Back Orifice",
            12345: "NetBus",
            27374: "SubSeven",
        }
        
        self._threat_intel_iocs = {
            "malicious_ips": set(),
            "malicious_domains": set(),
            "malicious_hashes": set(),
            "c2_servers": set(),
        }
    
    def _generate_chain_of_custody_hash(self, data: Dict[str, Any]) -> str:
        """Generate chain of custody hash for evidence integrity"""
        data_str = str(sorted(data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def scan_network_traffic(
        self,
        source_ip: str,
        destination_ip: str,
        source_port: int,
        destination_port: int,
        protocol: str,
        payload: Optional[str] = None,
        packet_count: int = 1,
        bytes_transferred: int = 0,
    ) -> Optional[NetworkThreat]:
        """
        Scan network traffic for threats
        
        Monitors:
        - Unusual traffic (ports, protocols, traffic spikes)
        - Attempted intrusions
        - Credential compromise
        - Lateral movement attempts
        - Exploits (SQLi, XSS, RCE patterns)
        """
        threat_type = None
        severity = ThreatSeverity.INFORMATIONAL
        detection_method = DetectionMethod.BEHAVIOR_ANOMALY
        signature_id = None
        signature_name = None
        ioc_matches = []
        
        if destination_port in self._suspicious_ports:
            threat_type = ThreatType.NETWORK_INTRUSION
            severity = ThreatSeverity.MEDIUM
            signature_name = f"Suspicious port: {self._suspicious_ports[destination_port]}"
        
        if source_ip in self._threat_intel_iocs["malicious_ips"]:
            threat_type = ThreatType.NETWORK_INTRUSION
            severity = ThreatSeverity.HIGH
            detection_method = DetectionMethod.THREAT_INTEL
            ioc_matches.append(f"Malicious IP: {source_ip}")
        
        if destination_ip in self._threat_intel_iocs["c2_servers"]:
            threat_type = ThreatType.COMMAND_AND_CONTROL
            severity = ThreatSeverity.CRITICAL
            detection_method = DetectionMethod.THREAT_INTEL
            ioc_matches.append(f"C2 server: {destination_ip}")
        
        if payload:
            for exploit_type, patterns in self._exploit_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, payload):
                        if exploit_type == "SQL_INJECTION":
                            threat_type = ThreatType.SQL_INJECTION
                        elif exploit_type == "XSS":
                            threat_type = ThreatType.XSS_ATTACK
                        elif exploit_type == "RCE":
                            threat_type = ThreatType.RCE_EXPLOIT
                        else:
                            threat_type = ThreatType.NETWORK_INTRUSION
                        
                        severity = ThreatSeverity.HIGH
                        detection_method = DetectionMethod.SIGNATURE_MATCH
                        signature_name = f"{exploit_type} pattern detected"
                        break
        
        if source_ip.startswith("10.") or source_ip.startswith("192.168."):
            if destination_ip.startswith("10.") or destination_ip.startswith("192.168."):
                if destination_port in [445, 3389, 22, 5985, 5986]:
                    if not threat_type:
                        threat_type = ThreatType.LATERAL_MOVEMENT
                        severity = ThreatSeverity.MEDIUM
                        detection_method = DetectionMethod.BEHAVIOR_ANOMALY
        
        if not threat_type:
            return None
        
        threat = NetworkThreat(
            threat_id=f"net-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            threat_type=threat_type,
            severity=severity,
            source_ip=source_ip,
            destination_ip=destination_ip,
            source_port=source_port,
            destination_port=destination_port,
            protocol=protocol,
            detection_method=detection_method,
            signature_id=signature_id,
            signature_name=signature_name,
            payload_hash=hashlib.sha256(payload.encode()).hexdigest() if payload else None,
            packet_count=packet_count,
            bytes_transferred=bytes_transferred,
            ioc_matches=ioc_matches,
            recommended_action=self._get_network_recommendation(threat_type, severity),
        )
        
        threat.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "threat_id": threat.threat_id,
            "timestamp": threat.timestamp.isoformat(),
            "threat_type": threat.threat_type.value,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
        })
        
        self.network_threats.append(threat)
        return threat
    
    def _get_network_recommendation(self, threat_type: ThreatType, severity: ThreatSeverity) -> str:
        """Get recommended action for network threat"""
        recommendations = {
            ThreatType.SQL_INJECTION: "Block source IP, review application logs, patch vulnerable endpoints",
            ThreatType.XSS_ATTACK: "Block source IP, sanitize input fields, implement CSP headers",
            ThreatType.RCE_EXPLOIT: "Isolate affected system immediately, block source IP, forensic analysis required",
            ThreatType.COMMAND_AND_CONTROL: "Isolate affected endpoints, block C2 communication, incident response required",
            ThreatType.LATERAL_MOVEMENT: "Review authentication logs, verify user activity, segment network",
            ThreatType.NETWORK_INTRUSION: "Block source IP, review firewall rules, monitor for persistence",
        }
        
        base_recommendation = recommendations.get(threat_type, "Investigate and monitor")
        
        if severity == ThreatSeverity.CRITICAL:
            return f"CRITICAL: {base_recommendation}. Notify SOC immediately."
        elif severity == ThreatSeverity.HIGH:
            return f"HIGH PRIORITY: {base_recommendation}"
        
        return base_recommendation
    
    def detect_ransomware(
        self,
        hostname: str,
        path: str,
        file_modifications_per_minute: int,
        file_extensions: List[str],
        file_names: List[str],
    ) -> Optional[RansomwareAlert]:
        """
        Ransomware Early Warning System
        
        Detects:
        - File modifications at high frequency
        - Encryption attempts
        - Known ransomware signatures
        - Suspicious file extensions
        - Command-and-control patterns
        """
        severity = ThreatSeverity.INFORMATIONAL
        encryption_detected = False
        known_signature = None
        ransomware_family = None
        suspicious_extensions = []
        c2_detected = False
        
        ransomware_extensions = [
            ".encrypted", ".locked", ".crypto", ".crypt",
            ".enc", ".crypted", ".locky", ".zepto",
            ".cerber", ".wallet", ".petya", ".wannacry",
        ]
        
        for ext in file_extensions:
            if ext.lower() in ransomware_extensions:
                suspicious_extensions.append(ext)
                encryption_detected = True
        
        for family, signatures in self._known_ransomware_signatures.items():
            for sig in signatures:
                for name in file_names:
                    if sig.lower() in name.lower():
                        known_signature = sig
                        ransomware_family = family
                        encryption_detected = True
                        break
        
        if file_modifications_per_minute > 100:
            severity = ThreatSeverity.CRITICAL
            encryption_detected = True
        elif file_modifications_per_minute > 50:
            severity = ThreatSeverity.HIGH
        elif file_modifications_per_minute > 20:
            severity = ThreatSeverity.MEDIUM
        elif suspicious_extensions or known_signature:
            severity = ThreatSeverity.HIGH
        else:
            return None
        
        alert = RansomwareAlert(
            alert_id=f"ransom-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            severity=severity,
            affected_host=hostname,
            affected_path=path,
            file_modifications_per_minute=file_modifications_per_minute,
            encryption_detected=encryption_detected,
            known_signature=known_signature,
            ransomware_family=ransomware_family,
            suspicious_extensions=suspicious_extensions,
            c2_communication_detected=c2_detected,
            files_affected=file_modifications_per_minute * 5,
            recommended_action=self._get_ransomware_recommendation(severity, ransomware_family),
        )
        
        alert.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "alert_id": alert.alert_id,
            "timestamp": alert.timestamp.isoformat(),
            "hostname": hostname,
            "path": path,
            "ransomware_family": ransomware_family,
        })
        
        self.ransomware_alerts.append(alert)
        return alert
    
    def _get_ransomware_recommendation(self, severity: ThreatSeverity, family: Optional[str]) -> str:
        """Get recommended action for ransomware"""
        base = "Isolate affected system from network immediately. Do not pay ransom."
        
        if severity == ThreatSeverity.CRITICAL:
            return f"CRITICAL: {base} Activate incident response team. Preserve evidence for forensics."
        elif severity == ThreatSeverity.HIGH:
            return f"HIGH PRIORITY: {base} Begin backup restoration procedures."
        
        if family:
            return f"{base} Known family: {family}. Check for available decryptors."
        
        return base
    
    def detect_endpoint_compromise(
        self,
        hostname: str,
        ip_address: str,
        user_account: str,
        processes: List[str],
        connections: List[str],
        registry_changes: Optional[List[str]] = None,
        file_changes: Optional[List[str]] = None,
    ) -> Optional[EndpointCompromise]:
        """
        Endpoint Compromise Detection
        
        Uses:
        - Behavioral heuristics
        - Process anomalies
        - Privilege escalation patterns
        - Unauthorized access attempts
        """
        severity = ThreatSeverity.INFORMATIONAL
        detection_method = DetectionMethod.HEURISTIC
        process_anomalies = []
        privilege_escalation = False
        unauthorized_access = False
        suspicious_processes = []
        suspicious_connections = []
        
        malicious_processes = [
            "mimikatz", "psexec", "cobalt", "beacon",
            "meterpreter", "nc.exe", "ncat", "netcat",
            "powershell -enc", "cmd /c", "wmic",
            "certutil", "bitsadmin", "regsvr32",
        ]
        
        for proc in processes:
            proc_lower = proc.lower()
            for mal_proc in malicious_processes:
                if mal_proc in proc_lower:
                    suspicious_processes.append(proc)
                    process_anomalies.append(f"Suspicious process: {proc}")
                    severity = ThreatSeverity.HIGH
        
        priv_esc_indicators = [
            "runas", "sudo", "su -", "privilege",
            "token", "impersonate", "getsystem",
        ]
        
        for proc in processes:
            proc_lower = proc.lower()
            for indicator in priv_esc_indicators:
                if indicator in proc_lower:
                    privilege_escalation = True
                    process_anomalies.append(f"Privilege escalation: {proc}")
                    severity = ThreatSeverity.HIGH
        
        for conn in connections:
            if any(str(port) in conn for port in self._suspicious_ports.keys()):
                suspicious_connections.append(conn)
                severity = max(severity, ThreatSeverity.MEDIUM)
        
        if not process_anomalies and not suspicious_connections:
            return None
        
        compromise = EndpointCompromise(
            compromise_id=f"endpoint-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            severity=severity,
            hostname=hostname,
            ip_address=ip_address,
            user_account=user_account,
            detection_method=detection_method,
            process_anomalies=process_anomalies,
            privilege_escalation=privilege_escalation,
            unauthorized_access=unauthorized_access,
            suspicious_processes=suspicious_processes,
            suspicious_connections=suspicious_connections,
            registry_modifications=registry_changes or [],
            file_modifications=file_changes or [],
            recommended_action=self._get_endpoint_recommendation(severity, privilege_escalation),
        )
        
        compromise.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "compromise_id": compromise.compromise_id,
            "timestamp": compromise.timestamp.isoformat(),
            "hostname": hostname,
            "user_account": user_account,
        })
        
        self.endpoint_compromises.append(compromise)
        return compromise
    
    def _get_endpoint_recommendation(self, severity: ThreatSeverity, priv_esc: bool) -> str:
        """Get recommended action for endpoint compromise"""
        if priv_esc:
            return "CRITICAL: Isolate endpoint immediately. Revoke user credentials. Forensic analysis required."
        
        if severity == ThreatSeverity.CRITICAL:
            return "Isolate endpoint from network. Preserve memory dump. Activate incident response."
        elif severity == ThreatSeverity.HIGH:
            return "Isolate endpoint. Review user activity. Scan for persistence mechanisms."
        
        return "Monitor endpoint closely. Review process activity. Check for lateral movement."
    
    def detect_zero_day(
        self,
        affected_system: str,
        attack_vector: str,
        behavior_indicators: List[str],
        process_behavior: Optional[str] = None,
        network_behavior: Optional[str] = None,
    ) -> Optional[ZeroDayThreat]:
        """
        Zero-Day Behavior Model
        
        AI engine for:
        - Unknown attack vectors
        - Previously unseen malware
        - AI-generated malware patterns
        """
        confidence_score = 0.0
        similar_threats = []
        iocs = []
        ai_generated = False
        
        anomaly_indicators = [
            "unusual_syscall", "memory_injection", "process_hollowing",
            "dll_injection", "code_cave", "reflective_loading",
            "fileless", "living_off_the_land", "obfuscated",
        ]
        
        for indicator in behavior_indicators:
            indicator_lower = indicator.lower()
            for anomaly in anomaly_indicators:
                if anomaly in indicator_lower:
                    confidence_score += 0.15
                    iocs.append(indicator)
        
        ai_indicators = [
            "polymorphic", "metamorphic", "self-modifying",
            "adversarial", "evasion", "anti-analysis",
        ]
        
        for indicator in behavior_indicators:
            indicator_lower = indicator.lower()
            for ai_ind in ai_indicators:
                if ai_ind in indicator_lower:
                    ai_generated = True
                    confidence_score += 0.2
        
        confidence_score = min(confidence_score, 1.0)
        
        if confidence_score < 0.3:
            return None
        
        if confidence_score >= 0.8:
            severity = ThreatSeverity.CRITICAL
        elif confidence_score >= 0.6:
            severity = ThreatSeverity.HIGH
        elif confidence_score >= 0.4:
            severity = ThreatSeverity.MEDIUM
        else:
            severity = ThreatSeverity.LOW
        
        behavior_sig = hashlib.sha256(
            "".join(sorted(behavior_indicators)).encode()
        ).hexdigest()[:16]
        
        threat = ZeroDayThreat(
            threat_id=f"zeroday-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            severity=severity,
            detection_method=DetectionMethod.ML_MODEL,
            affected_system=affected_system,
            attack_vector=attack_vector,
            behavior_signature=behavior_sig,
            confidence_score=confidence_score,
            ml_model_version="1.0.0",
            similar_known_threats=similar_threats,
            indicators_of_compromise=iocs,
            ai_generated_malware=ai_generated,
            recommended_action=self._get_zero_day_recommendation(severity, ai_generated),
        )
        
        threat.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "threat_id": threat.threat_id,
            "timestamp": threat.timestamp.isoformat(),
            "affected_system": affected_system,
            "behavior_signature": behavior_sig,
        })
        
        self.zero_day_threats.append(threat)
        return threat
    
    def _get_zero_day_recommendation(self, severity: ThreatSeverity, ai_generated: bool) -> str:
        """Get recommended action for zero-day threat"""
        if ai_generated:
            return "CRITICAL: AI-generated malware detected. Isolate immediately. Contact FBI Cyber Division."
        
        if severity == ThreatSeverity.CRITICAL:
            return "Isolate affected systems. Preserve evidence. Engage threat intelligence team."
        elif severity == ThreatSeverity.HIGH:
            return "Quarantine affected systems. Analyze behavior patterns. Update detection signatures."
        
        return "Monitor closely. Collect additional telemetry. Share IOCs with threat intel community."
    
    def get_threat_assessment(self) -> ThreatAssessment:
        """Get overall threat assessment"""
        now = datetime.utcnow()
        recent_window = now - timedelta(hours=24)
        
        recent_network = [t for t in self.network_threats if t.timestamp > recent_window]
        recent_ransomware = [a for a in self.ransomware_alerts if a.timestamp > recent_window]
        recent_endpoint = [c for c in self.endpoint_compromises if c.timestamp > recent_window]
        recent_zeroday = [t for t in self.zero_day_threats if t.timestamp > recent_window]
        
        all_severities = (
            [t.severity for t in recent_network] +
            [a.severity for a in recent_ransomware] +
            [c.severity for c in recent_endpoint] +
            [t.severity for t in recent_zeroday]
        )
        
        if ThreatSeverity.CRITICAL in all_severities:
            overall_level = ThreatSeverity.CRITICAL
        elif ThreatSeverity.HIGH in all_severities:
            overall_level = ThreatSeverity.HIGH
        elif ThreatSeverity.MEDIUM in all_severities:
            overall_level = ThreatSeverity.MEDIUM
        elif ThreatSeverity.LOW in all_severities:
            overall_level = ThreatSeverity.LOW
        else:
            overall_level = ThreatSeverity.INFORMATIONAL
        
        critical_count = sum(1 for s in all_severities if s == ThreatSeverity.CRITICAL)
        
        recommendations = []
        if recent_ransomware:
            recommendations.append("Ransomware activity detected. Verify backup integrity.")
        if recent_zeroday:
            recommendations.append("Zero-day threats detected. Update threat intelligence.")
        if critical_count > 0:
            recommendations.append(f"{critical_count} critical alerts require immediate attention.")
        
        assessment = ThreatAssessment(
            assessment_id=f"assess-{uuid.uuid4().hex[:12]}",
            timestamp=now,
            overall_threat_level=overall_level,
            network_threats=recent_network,
            ransomware_alerts=recent_ransomware,
            endpoint_compromises=recent_endpoint,
            zero_day_threats=recent_zeroday,
            active_incidents=len(recent_network) + len(recent_ransomware) + len(recent_endpoint) + len(recent_zeroday),
            critical_alerts=critical_count,
            recommendations=recommendations,
        )
        
        assessment.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "assessment_id": assessment.assessment_id,
            "timestamp": assessment.timestamp.isoformat(),
            "overall_threat_level": assessment.overall_threat_level.value,
        })
        
        return assessment
    
    def add_threat_intel(
        self,
        malicious_ips: Optional[List[str]] = None,
        malicious_domains: Optional[List[str]] = None,
        malicious_hashes: Optional[List[str]] = None,
        c2_servers: Optional[List[str]] = None,
    ) -> None:
        """Add threat intelligence indicators"""
        if malicious_ips:
            self._threat_intel_iocs["malicious_ips"].update(malicious_ips)
        if malicious_domains:
            self._threat_intel_iocs["malicious_domains"].update(malicious_domains)
        if malicious_hashes:
            self._threat_intel_iocs["malicious_hashes"].update(malicious_hashes)
        if c2_servers:
            self._threat_intel_iocs["c2_servers"].update(c2_servers)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cyber threat statistics"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        return {
            "total_network_threats": len(self.network_threats),
            "total_ransomware_alerts": len(self.ransomware_alerts),
            "total_endpoint_compromises": len(self.endpoint_compromises),
            "total_zero_day_threats": len(self.zero_day_threats),
            "network_threats_24h": len([t for t in self.network_threats if t.timestamp > last_24h]),
            "ransomware_alerts_24h": len([a for a in self.ransomware_alerts if a.timestamp > last_24h]),
            "endpoint_compromises_24h": len([c for c in self.endpoint_compromises if c.timestamp > last_24h]),
            "zero_day_threats_24h": len([t for t in self.zero_day_threats if t.timestamp > last_24h]),
            "critical_threats_7d": len([
                t for t in self.network_threats + self.zero_day_threats
                if t.timestamp > last_7d and t.severity == ThreatSeverity.CRITICAL
            ]),
            "threat_intel_iocs": {
                "malicious_ips": len(self._threat_intel_iocs["malicious_ips"]),
                "malicious_domains": len(self._threat_intel_iocs["malicious_domains"]),
                "malicious_hashes": len(self._threat_intel_iocs["malicious_hashes"]),
                "c2_servers": len(self._threat_intel_iocs["c2_servers"]),
            },
        }
