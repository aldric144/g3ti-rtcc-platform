"""
Unified Alert Stream - Aggregates alerts from all RTCC modules.
Phase 37: Master UI Integration & System Orchestration Shell
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid
import hashlib
import json


class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertSource(Enum):
    OFFICER_ASSIST = "officer_assist"
    MORAL_COMPASS = "moral_compass"
    HUMAN_STABILITY = "human_stability"
    GLOBAL_THREAT = "global_threat"
    FUSION_CLOUD = "fusion_cloud"
    DRONE_OPS = "drone_ops"
    ROBOTICS = "robotics"
    TACTICAL_ANALYTICS = "tactical_analytics"
    INVESTIGATIONS = "investigations"
    CITY_AUTONOMY = "city_autonomy"
    CYBER_INTEL = "cyber_intel"
    EMERGENCY_MGMT = "emergency_mgmt"
    PREDICTIVE_INTEL = "predictive_intel"
    SENTINEL_SUPERVISOR = "sentinel_supervisor"
    ETHICS_GUARDIAN = "ethics_guardian"
    PUBLIC_GUARDIAN = "public_guardian"
    CONSTITUTION_ENGINE = "constitution_engine"
    AI_CITY_BRAIN = "ai_city_brain"
    GOVERNANCE_ENGINE = "governance_engine"
    NATIONAL_SECURITY = "national_security"
    DETECTIVE_AI = "detective_ai"
    DIGITAL_TWIN = "digital_twin"
    OPS_CONTINUITY = "ops_continuity"
    SYSTEM = "system"


@dataclass
class UnifiedAlert:
    alert_id: str = field(default_factory=lambda: f"alert-{uuid.uuid4().hex[:12]}")
    severity: AlertSeverity = AlertSeverity.MEDIUM
    source: AlertSource = AlertSource.SYSTEM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    title: str = ""
    summary: str = ""
    full_details: Dict[str, Any] = field(default_factory=dict)
    geolocation: Optional[Dict[str, float]] = None
    constitutional_compliance_tag: bool = True
    moral_compass_tag: Optional[str] = None
    public_safety_audit_ref: Optional[str] = None
    affected_areas: List[str] = field(default_factory=list)
    affected_officers: List[str] = field(default_factory=list)
    requires_action: bool = False
    action_taken: bool = False
    action_by: Optional[str] = None
    action_at: Optional[datetime] = None
    action_notes: Optional[str] = None
    expires_at: Optional[datetime] = None
    active: bool = True
    escalated: bool = False
    escalation_level: int = 0
    related_alerts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    alert_hash: str = ""

    def __post_init__(self):
        if not self.alert_hash:
            self.alert_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.severity.value}:{self.source.value}:{self.title}:{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "source": self.source.value,
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "summary": self.summary,
            "full_details": self.full_details,
            "geolocation": self.geolocation,
            "constitutional_compliance_tag": self.constitutional_compliance_tag,
            "moral_compass_tag": self.moral_compass_tag,
            "public_safety_audit_ref": self.public_safety_audit_ref,
            "affected_areas": self.affected_areas,
            "affected_officers": self.affected_officers,
            "requires_action": self.requires_action,
            "action_taken": self.action_taken,
            "action_by": self.action_by,
            "action_at": self.action_at.isoformat() if self.action_at else None,
            "action_notes": self.action_notes,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "active": self.active,
            "escalated": self.escalated,
            "escalation_level": self.escalation_level,
            "related_alerts": self.related_alerts,
            "metadata": self.metadata,
            "alert_hash": self.alert_hash,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class AlertFilter:
    severities: Optional[List[AlertSeverity]] = None
    sources: Optional[List[AlertSource]] = None
    active_only: bool = True
    requires_action_only: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    affected_areas: Optional[List[str]] = None
    constitutional_compliance: Optional[bool] = None
    escalated_only: bool = False

    def matches(self, alert: UnifiedAlert) -> bool:
        if self.severities and alert.severity not in self.severities:
            return False

        if self.sources and alert.source not in self.sources:
            return False

        if self.active_only and not alert.active:
            return False

        if self.requires_action_only and not alert.requires_action:
            return False

        if self.start_time and alert.timestamp < self.start_time:
            return False

        if self.end_time and alert.timestamp > self.end_time:
            return False

        if self.affected_areas:
            if not any(area in alert.affected_areas for area in self.affected_areas):
                return False

        if self.constitutional_compliance is not None:
            if alert.constitutional_compliance_tag != self.constitutional_compliance:
                return False

        if self.escalated_only and not alert.escalated:
            return False

        return True


class UnifiedAlertStream:
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

        self._alerts: Dict[str, UnifiedAlert] = {}
        self._alert_history: List[UnifiedAlert] = []
        self._max_history = 10000
        self._statistics = {
            "alerts_created": 0,
            "alerts_resolved": 0,
            "alerts_escalated": 0,
            "actions_taken": 0,
        }
        self._severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3,
            AlertSeverity.INFO: 4,
        }
        self._initialize_sample_alerts()

    def _initialize_sample_alerts(self):
        sample_alerts = [
            UnifiedAlert(
                severity=AlertSeverity.HIGH,
                source=AlertSource.OFFICER_ASSIST,
                title="Officer Safety Alert - High Risk Stop",
                summary="Officer approaching vehicle with known armed suspect",
                geolocation={"lat": 26.7753, "lng": -80.0589},
                affected_areas=["Downtown Riviera Beach"],
                requires_action=True,
            ),
            UnifiedAlert(
                severity=AlertSeverity.MEDIUM,
                source=AlertSource.TACTICAL_ANALYTICS,
                title="Crime Pattern Detected",
                summary="Increased burglary activity in Singer Island area",
                geolocation={"lat": 26.7850, "lng": -80.0350},
                affected_areas=["Singer Island"],
            ),
            UnifiedAlert(
                severity=AlertSeverity.LOW,
                source=AlertSource.PUBLIC_GUARDIAN,
                title="Community Event Reminder",
                summary="Town Hall meeting scheduled for tomorrow",
                affected_areas=["All Neighborhoods"],
            ),
        ]
        for alert in sample_alerts:
            self._alerts[alert.alert_id] = alert
            self._alert_history.append(alert)
            self._statistics["alerts_created"] += 1

    def create_alert(
        self,
        severity: AlertSeverity,
        source: AlertSource,
        title: str,
        summary: str = "",
        full_details: Optional[Dict[str, Any]] = None,
        geolocation: Optional[Dict[str, float]] = None,
        constitutional_compliance_tag: bool = True,
        moral_compass_tag: Optional[str] = None,
        public_safety_audit_ref: Optional[str] = None,
        affected_areas: Optional[List[str]] = None,
        affected_officers: Optional[List[str]] = None,
        requires_action: bool = False,
        expires_at: Optional[datetime] = None,
    ) -> UnifiedAlert:
        alert = UnifiedAlert(
            severity=severity,
            source=source,
            title=title,
            summary=summary,
            full_details=full_details or {},
            geolocation=geolocation,
            constitutional_compliance_tag=constitutional_compliance_tag,
            moral_compass_tag=moral_compass_tag,
            public_safety_audit_ref=public_safety_audit_ref,
            affected_areas=affected_areas or [],
            affected_officers=affected_officers or [],
            requires_action=requires_action,
            expires_at=expires_at,
        )
        self._alerts[alert.alert_id] = alert
        self._alert_history.append(alert)
        self._statistics["alerts_created"] += 1

        if len(self._alert_history) > self._max_history:
            self._alert_history = self._alert_history[-self._max_history:]

        return alert

    def get_alert(self, alert_id: str) -> Optional[UnifiedAlert]:
        return self._alerts.get(alert_id)

    def get_active_alerts(
        self,
        limit: int = 100,
        filter_obj: Optional[AlertFilter] = None,
    ) -> List[UnifiedAlert]:
        alerts = [a for a in self._alerts.values() if a.active]

        if filter_obj:
            alerts = [a for a in alerts if filter_obj.matches(a)]

        alerts.sort(key=lambda a: (self._severity_order[a.severity], a.timestamp), reverse=False)
        return alerts[:limit]

    def get_alerts_by_severity(self, severity: AlertSeverity, limit: int = 100) -> List[UnifiedAlert]:
        alerts = [a for a in self._alerts.values() if a.severity == severity and a.active]
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        return alerts[:limit]

    def get_alerts_by_source(self, source: AlertSource, limit: int = 100) -> List[UnifiedAlert]:
        alerts = [a for a in self._alerts.values() if a.source == source and a.active]
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        return alerts[:limit]

    def get_critical_alerts(self, limit: int = 50) -> List[UnifiedAlert]:
        return self.get_alerts_by_severity(AlertSeverity.CRITICAL, limit)

    def get_alerts_requiring_action(self, limit: int = 100) -> List[UnifiedAlert]:
        alerts = [a for a in self._alerts.values() if a.requires_action and not a.action_taken and a.active]
        alerts.sort(key=lambda a: (self._severity_order[a.severity], a.timestamp))
        return alerts[:limit]

    def take_action(
        self,
        alert_id: str,
        action_by: str,
        action_notes: Optional[str] = None,
    ) -> Optional[UnifiedAlert]:
        alert = self._alerts.get(alert_id)
        if alert:
            alert.action_taken = True
            alert.action_by = action_by
            alert.action_at = datetime.utcnow()
            alert.action_notes = action_notes
            self._statistics["actions_taken"] += 1
            return alert
        return None

    def resolve_alert(self, alert_id: str, resolved_by: str, notes: Optional[str] = None) -> bool:
        alert = self._alerts.get(alert_id)
        if alert:
            alert.active = False
            if not alert.action_taken:
                alert.action_taken = True
                alert.action_by = resolved_by
                alert.action_at = datetime.utcnow()
                alert.action_notes = notes or "Alert resolved"
            self._statistics["alerts_resolved"] += 1
            return True
        return False

    def escalate_alert(self, alert_id: str, escalation_notes: Optional[str] = None) -> Optional[UnifiedAlert]:
        alert = self._alerts.get(alert_id)
        if alert:
            alert.escalated = True
            alert.escalation_level += 1
            if escalation_notes:
                alert.metadata["escalation_notes"] = escalation_notes
            self._statistics["alerts_escalated"] += 1
            return alert
        return None

    def link_alerts(self, alert_id: str, related_alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        related = self._alerts.get(related_alert_id)
        if alert and related:
            if related_alert_id not in alert.related_alerts:
                alert.related_alerts.append(related_alert_id)
            if alert_id not in related.related_alerts:
                related.related_alerts.append(alert_id)
            return True
        return False

    def get_alert_history(
        self,
        limit: int = 100,
        source: Optional[AlertSource] = None,
        severity: Optional[AlertSeverity] = None,
    ) -> List[UnifiedAlert]:
        alerts = list(reversed(self._alert_history))

        if source:
            alerts = [a for a in alerts if a.source == source]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts[:limit]

    def get_alerts_by_area(self, area: str, limit: int = 100) -> List[UnifiedAlert]:
        alerts = [a for a in self._alerts.values() if area in a.affected_areas and a.active]
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        return alerts[:limit]

    def get_alerts_for_officer(self, officer_id: str, limit: int = 100) -> List[UnifiedAlert]:
        alerts = [a for a in self._alerts.values() if officer_id in a.affected_officers and a.active]
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        return alerts[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        active_alerts = [a for a in self._alerts.values() if a.active]
        return {
            **self._statistics,
            "total_alerts": len(self._alerts),
            "active_alerts": len(active_alerts),
            "critical_active": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
            "high_active": len([a for a in active_alerts if a.severity == AlertSeverity.HIGH]),
            "medium_active": len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]),
            "low_active": len([a for a in active_alerts if a.severity == AlertSeverity.LOW]),
            "info_active": len([a for a in active_alerts if a.severity == AlertSeverity.INFO]),
            "requiring_action": len([a for a in active_alerts if a.requires_action and not a.action_taken]),
            "escalated": len([a for a in active_alerts if a.escalated]),
            "alerts_by_source": self._count_by_source(),
        }

    def _count_by_source(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for alert in self._alerts.values():
            if alert.active:
                key = alert.source.value
                counts[key] = counts.get(key, 0) + 1
        return counts

    def cleanup_expired_alerts(self) -> int:
        now = datetime.utcnow()
        count = 0
        for alert in self._alerts.values():
            if alert.expires_at and alert.expires_at < now and alert.active:
                alert.active = False
                count += 1
        return count

    def get_unified_feed(self, limit: int = 50) -> List[Dict[str, Any]]:
        alerts = self.get_active_alerts(limit=limit)
        return [alert.to_dict() for alert in alerts]
