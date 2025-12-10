"""
National Security Alerts Module

Provides alert management capabilities including:
- REST endpoints for alert operations
- WebSocket channels for real-time alerts
- Automatic routing to Chief, Homeland Security Liaison, RTCC Director
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable
import uuid
import asyncio


class AlertPriority(Enum):
    """Priority levels for security alerts."""
    ROUTINE = "routine"
    PRIORITY = "priority"
    IMMEDIATE = "immediate"
    FLASH = "flash"
    EMERGENCY = "emergency"
    CRITICAL = "critical"


class AlertCategory(Enum):
    """Categories of security alerts."""
    CYBER_THREAT = "cyber_threat"
    INSIDER_THREAT = "insider_threat"
    GEOPOLITICAL = "geopolitical"
    FINANCIAL_CRIME = "financial_crime"
    TERRORISM = "terrorism"
    INFRASTRUCTURE = "infrastructure"
    NATIONAL_STABILITY = "national_stability"
    EARLY_WARNING = "early_warning"
    CROSS_DOMAIN = "cross_domain"
    OPERATIONAL = "operational"


class AlertDestination(Enum):
    """Destinations for alert routing."""
    CHIEF = "chief"
    HOMELAND_SECURITY_LIAISON = "homeland_security_liaison"
    RTCC_DIRECTOR = "rtcc_director"
    OPERATIONS_CENTER = "operations_center"
    CYBER_TEAM = "cyber_team"
    INTEL_TEAM = "intel_team"
    FINANCIAL_CRIMES_UNIT = "financial_crimes_unit"
    FUSION_CENTER = "fusion_center"
    COMMAND_CENTER = "command_center"
    ALL_STATIONS = "all_stations"


class AlertStatus(Enum):
    """Status of security alerts."""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    EXPIRED = "expired"


class EscalationLevel(Enum):
    """Escalation levels for alerts."""
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    EXECUTIVE = "executive"
    NATIONAL = "national"


@dataclass
class SecurityAlert:
    """Represents a national security alert."""
    alert_id: str
    title: str
    description: str
    priority: AlertPriority
    category: AlertCategory
    status: AlertStatus
    risk_score: float
    source_module: str
    source_signal_id: Optional[str]
    affected_domains: List[str]
    destinations: List[AlertDestination]
    escalation_level: EscalationLevel
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    resolution_notes: Optional[str]
    related_alerts: List[str]
    attachments: List[str]
    actions_taken: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertSubscription:
    """Represents a subscription to alerts."""
    subscription_id: str
    subscriber_id: str
    subscriber_name: str
    subscriber_role: str
    categories: List[AlertCategory]
    min_priority: AlertPriority
    destinations: List[AlertDestination]
    notification_methods: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingRule:
    """Represents a routing rule for alerts."""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    destinations: List[AlertDestination]
    priority_override: Optional[AlertPriority]
    auto_escalate: bool
    escalation_delay_minutes: int
    is_active: bool
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertAuditEntry:
    """Audit entry for alert actions."""
    entry_id: str
    alert_id: str
    action: str
    actor_id: str
    actor_name: str
    timestamp: datetime
    details: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class NationalSecurityAlertManager:
    """
    National Security Alert Manager.
    
    Provides capabilities for:
    - Alert creation and management
    - Automatic routing to appropriate personnel
    - WebSocket broadcasting
    - Escalation management
    - Audit logging
    """

    def __init__(self):
        self.alerts: Dict[str, SecurityAlert] = {}
        self.subscriptions: Dict[str, AlertSubscription] = {}
        self.routing_rules: Dict[str, RoutingRule] = {}
        self.audit_log: Dict[str, AlertAuditEntry] = {}
        self.websocket_handlers: List[Callable] = []
        self._initialize_default_routing_rules()

    def _initialize_default_routing_rules(self) -> None:
        """Initialize default routing rules."""
        default_rules = [
            {
                "name": "Critical to Leadership",
                "description": "Route critical alerts to leadership",
                "conditions": {"priority": ["critical", "emergency"]},
                "destinations": [
                    AlertDestination.CHIEF,
                    AlertDestination.HOMELAND_SECURITY_LIAISON,
                    AlertDestination.RTCC_DIRECTOR,
                ],
                "auto_escalate": True,
                "escalation_delay_minutes": 15,
            },
            {
                "name": "Cyber Threats to Cyber Team",
                "description": "Route cyber threats to cyber team",
                "conditions": {"category": ["cyber_threat"]},
                "destinations": [
                    AlertDestination.CYBER_TEAM,
                    AlertDestination.OPERATIONS_CENTER,
                ],
                "auto_escalate": False,
                "escalation_delay_minutes": 30,
            },
            {
                "name": "Financial Crimes to FCU",
                "description": "Route financial crimes to FCU",
                "conditions": {"category": ["financial_crime"]},
                "destinations": [
                    AlertDestination.FINANCIAL_CRIMES_UNIT,
                    AlertDestination.INTEL_TEAM,
                ],
                "auto_escalate": False,
                "escalation_delay_minutes": 60,
            },
            {
                "name": "Terrorism to All Leadership",
                "description": "Route terrorism alerts to all leadership",
                "conditions": {"category": ["terrorism"]},
                "destinations": [
                    AlertDestination.CHIEF,
                    AlertDestination.HOMELAND_SECURITY_LIAISON,
                    AlertDestination.RTCC_DIRECTOR,
                    AlertDestination.FUSION_CENTER,
                ],
                "auto_escalate": True,
                "escalation_delay_minutes": 5,
            },
            {
                "name": "National Stability to Command",
                "description": "Route national stability alerts to command",
                "conditions": {"category": ["national_stability"]},
                "destinations": [
                    AlertDestination.COMMAND_CENTER,
                    AlertDestination.RTCC_DIRECTOR,
                ],
                "auto_escalate": True,
                "escalation_delay_minutes": 10,
            },
        ]
        
        for rule_data in default_rules:
            self.create_routing_rule(
                name=rule_data["name"],
                description=rule_data["description"],
                conditions=rule_data["conditions"],
                destinations=rule_data["destinations"],
                auto_escalate=rule_data["auto_escalate"],
                escalation_delay_minutes=rule_data["escalation_delay_minutes"],
            )

    def create_alert(
        self,
        title: str,
        description: str,
        priority: AlertPriority,
        category: AlertCategory,
        risk_score: float,
        source_module: str,
        source_signal_id: Optional[str] = None,
        affected_domains: Optional[List[str]] = None,
        expires_in_hours: Optional[int] = None,
        related_alerts: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SecurityAlert:
        """Create a new security alert."""
        alert_id = f"nsa-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        destinations = self._determine_destinations(priority, category)
        
        escalation_level = self._determine_escalation_level(priority, risk_score)
        
        alert = SecurityAlert(
            alert_id=alert_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            status=AlertStatus.NEW,
            risk_score=risk_score,
            source_module=source_module,
            source_signal_id=source_signal_id,
            affected_domains=affected_domains or [],
            destinations=destinations,
            escalation_level=escalation_level,
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(hours=expires_in_hours) if expires_in_hours else None,
            acknowledged_at=None,
            acknowledged_by=None,
            resolved_at=None,
            resolved_by=None,
            resolution_notes=None,
            related_alerts=related_alerts or [],
            attachments=attachments or [],
            actions_taken=[],
            metadata=metadata or {},
        )
        
        self.alerts[alert_id] = alert
        
        self._log_audit(
            alert_id=alert_id,
            action="created",
            actor_id="system",
            actor_name="System",
            details={"priority": priority.value, "category": category.value},
        )
        
        self._broadcast_alert(alert)
        
        return alert

    def _determine_destinations(
        self,
        priority: AlertPriority,
        category: AlertCategory,
    ) -> List[AlertDestination]:
        """Determine alert destinations based on routing rules."""
        destinations: Set[AlertDestination] = set()
        
        for rule in self.routing_rules.values():
            if not rule.is_active:
                continue
            
            if self._rule_matches(rule, priority, category):
                destinations.update(rule.destinations)
        
        if not destinations:
            destinations.add(AlertDestination.OPERATIONS_CENTER)
        
        if priority in [AlertPriority.CRITICAL, AlertPriority.EMERGENCY]:
            destinations.add(AlertDestination.CHIEF)
            destinations.add(AlertDestination.RTCC_DIRECTOR)
        
        return list(destinations)

    def _rule_matches(
        self,
        rule: RoutingRule,
        priority: AlertPriority,
        category: AlertCategory,
    ) -> bool:
        """Check if a routing rule matches the alert."""
        conditions = rule.conditions
        
        if "priority" in conditions:
            if priority.value not in conditions["priority"]:
                return False
        
        if "category" in conditions:
            if category.value not in conditions["category"]:
                return False
        
        return True

    def _determine_escalation_level(
        self,
        priority: AlertPriority,
        risk_score: float,
    ) -> EscalationLevel:
        """Determine initial escalation level."""
        if priority == AlertPriority.CRITICAL or risk_score >= 90:
            return EscalationLevel.EXECUTIVE
        elif priority == AlertPriority.EMERGENCY or risk_score >= 75:
            return EscalationLevel.LEVEL_3
        elif priority in [AlertPriority.FLASH, AlertPriority.IMMEDIATE] or risk_score >= 60:
            return EscalationLevel.LEVEL_2
        else:
            return EscalationLevel.LEVEL_1

    def _broadcast_alert(self, alert: SecurityAlert) -> None:
        """Broadcast alert to WebSocket handlers."""
        for handler in self.websocket_handlers:
            try:
                handler(alert)
            except Exception:
                pass

    def register_websocket_handler(self, handler: Callable) -> None:
        """Register a WebSocket handler for alert broadcasts."""
        self.websocket_handlers.append(handler)

    def unregister_websocket_handler(self, handler: Callable) -> None:
        """Unregister a WebSocket handler."""
        if handler in self.websocket_handlers:
            self.websocket_handlers.remove(handler)

    def get_alert(self, alert_id: str) -> Optional[SecurityAlert]:
        """Get an alert by ID."""
        return self.alerts.get(alert_id)

    def get_alerts(
        self,
        priority: Optional[AlertPriority] = None,
        category: Optional[AlertCategory] = None,
        status: Optional[AlertStatus] = None,
        destination: Optional[AlertDestination] = None,
        min_risk_score: float = 0,
        active_only: bool = False,
        limit: int = 100,
    ) -> List[SecurityAlert]:
        """Retrieve alerts with optional filtering."""
        alerts = list(self.alerts.values())
        
        if priority:
            priority_order = list(AlertPriority)
            min_index = priority_order.index(priority)
            alerts = [a for a in alerts if priority_order.index(a.priority) >= min_index]
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        if destination:
            alerts = [a for a in alerts if destination in a.destinations]
        
        alerts = [a for a in alerts if a.risk_score >= min_risk_score]
        
        if active_only:
            now = datetime.utcnow()
            alerts = [
                a for a in alerts
                if a.status not in [AlertStatus.RESOLVED, AlertStatus.CLOSED, AlertStatus.EXPIRED]
                and (a.expires_at is None or a.expires_at > now)
            ]
        
        alerts.sort(key=lambda x: (list(AlertPriority).index(x.priority), -x.risk_score), reverse=True)
        return alerts[:limit]

    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        actor_name: str = "",
    ) -> bool:
        """Acknowledge an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        if alert.status != AlertStatus.NEW:
            return False
        
        now = datetime.utcnow()
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = now
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = now
        
        self._log_audit(
            alert_id=alert_id,
            action="acknowledged",
            actor_id=acknowledged_by,
            actor_name=actor_name or acknowledged_by,
            details={},
        )
        
        return True

    def escalate_alert(
        self,
        alert_id: str,
        escalated_by: str,
        actor_name: str = "",
        reason: str = "",
    ) -> bool:
        """Escalate an alert to the next level."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        escalation_order = list(EscalationLevel)
        current_index = escalation_order.index(alert.escalation_level)
        
        if current_index >= len(escalation_order) - 1:
            return False
        
        new_level = escalation_order[current_index + 1]
        alert.escalation_level = new_level
        alert.status = AlertStatus.ESCALATED
        alert.updated_at = datetime.utcnow()
        
        if new_level in [EscalationLevel.EXECUTIVE, EscalationLevel.NATIONAL]:
            alert.destinations.append(AlertDestination.CHIEF)
            alert.destinations.append(AlertDestination.HOMELAND_SECURITY_LIAISON)
        
        alert.actions_taken.append({
            "action": "escalated",
            "timestamp": datetime.utcnow().isoformat(),
            "actor": escalated_by,
            "new_level": new_level.value,
            "reason": reason,
        })
        
        self._log_audit(
            alert_id=alert_id,
            action="escalated",
            actor_id=escalated_by,
            actor_name=actor_name or escalated_by,
            details={"new_level": new_level.value, "reason": reason},
        )
        
        self._broadcast_alert(alert)
        
        return True

    def resolve_alert(
        self,
        alert_id: str,
        resolved_by: str,
        actor_name: str = "",
        resolution_notes: str = "",
    ) -> bool:
        """Resolve an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        if alert.status in [AlertStatus.RESOLVED, AlertStatus.CLOSED]:
            return False
        
        now = datetime.utcnow()
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = now
        alert.resolved_by = resolved_by
        alert.resolution_notes = resolution_notes
        alert.updated_at = now
        
        alert.actions_taken.append({
            "action": "resolved",
            "timestamp": now.isoformat(),
            "actor": resolved_by,
            "notes": resolution_notes,
        })
        
        self._log_audit(
            alert_id=alert_id,
            action="resolved",
            actor_id=resolved_by,
            actor_name=actor_name or resolved_by,
            details={"resolution_notes": resolution_notes},
        )
        
        return True

    def close_alert(
        self,
        alert_id: str,
        closed_by: str,
        actor_name: str = "",
        close_reason: str = "",
    ) -> bool:
        """Close an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        now = datetime.utcnow()
        alert.status = AlertStatus.CLOSED
        alert.updated_at = now
        
        alert.actions_taken.append({
            "action": "closed",
            "timestamp": now.isoformat(),
            "actor": closed_by,
            "reason": close_reason,
        })
        
        self._log_audit(
            alert_id=alert_id,
            action="closed",
            actor_id=closed_by,
            actor_name=actor_name or closed_by,
            details={"close_reason": close_reason},
        )
        
        return True

    def add_action(
        self,
        alert_id: str,
        action: str,
        actor_id: str,
        actor_name: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add an action to an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False
        
        now = datetime.utcnow()
        alert.actions_taken.append({
            "action": action,
            "timestamp": now.isoformat(),
            "actor": actor_id,
            "details": details or {},
        })
        alert.updated_at = now
        
        self._log_audit(
            alert_id=alert_id,
            action=action,
            actor_id=actor_id,
            actor_name=actor_name or actor_id,
            details=details or {},
        )
        
        return True

    def create_subscription(
        self,
        subscriber_id: str,
        subscriber_name: str,
        subscriber_role: str,
        categories: List[AlertCategory],
        min_priority: AlertPriority = AlertPriority.ROUTINE,
        destinations: Optional[List[AlertDestination]] = None,
        notification_methods: Optional[List[str]] = None,
    ) -> AlertSubscription:
        """Create an alert subscription."""
        subscription_id = f"sub-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        subscription = AlertSubscription(
            subscription_id=subscription_id,
            subscriber_id=subscriber_id,
            subscriber_name=subscriber_name,
            subscriber_role=subscriber_role,
            categories=categories,
            min_priority=min_priority,
            destinations=destinations or [],
            notification_methods=notification_methods or ["websocket"],
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        
        self.subscriptions[subscription_id] = subscription
        return subscription

    def get_subscriptions(
        self,
        subscriber_id: Optional[str] = None,
        active_only: bool = False,
    ) -> List[AlertSubscription]:
        """Get alert subscriptions."""
        subscriptions = list(self.subscriptions.values())
        
        if subscriber_id:
            subscriptions = [s for s in subscriptions if s.subscriber_id == subscriber_id]
        
        if active_only:
            subscriptions = [s for s in subscriptions if s.is_active]
        
        return subscriptions

    def create_routing_rule(
        self,
        name: str,
        description: str,
        conditions: Dict[str, Any],
        destinations: List[AlertDestination],
        priority_override: Optional[AlertPriority] = None,
        auto_escalate: bool = False,
        escalation_delay_minutes: int = 30,
    ) -> RoutingRule:
        """Create a routing rule."""
        rule_id = f"rule-{uuid.uuid4().hex[:12]}"
        
        rule = RoutingRule(
            rule_id=rule_id,
            name=name,
            description=description,
            conditions=conditions,
            destinations=destinations,
            priority_override=priority_override,
            auto_escalate=auto_escalate,
            escalation_delay_minutes=escalation_delay_minutes,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        
        self.routing_rules[rule_id] = rule
        return rule

    def get_routing_rules(
        self,
        active_only: bool = False,
    ) -> List[RoutingRule]:
        """Get routing rules."""
        rules = list(self.routing_rules.values())
        
        if active_only:
            rules = [r for r in rules if r.is_active]
        
        return rules

    def _log_audit(
        self,
        alert_id: str,
        action: str,
        actor_id: str,
        actor_name: str,
        details: Dict[str, Any],
    ) -> AlertAuditEntry:
        """Log an audit entry."""
        entry_id = f"audit-{uuid.uuid4().hex[:12]}"
        
        entry = AlertAuditEntry(
            entry_id=entry_id,
            alert_id=alert_id,
            action=action,
            actor_id=actor_id,
            actor_name=actor_name,
            timestamp=datetime.utcnow(),
            details=details,
        )
        
        self.audit_log[entry_id] = entry
        return entry

    def get_audit_log(
        self,
        alert_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> List[AlertAuditEntry]:
        """Get audit log entries."""
        entries = list(self.audit_log.values())
        
        if alert_id:
            entries = [e for e in entries if e.alert_id == alert_id]
        
        if actor_id:
            entries = [e for e in entries if e.actor_id == actor_id]
        
        if action:
            entries = [e for e in entries if e.action == action]
        
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        return entries[:limit]

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        alerts = list(self.alerts.values())
        now = datetime.utcnow()
        
        active_alerts = [
            a for a in alerts
            if a.status not in [AlertStatus.RESOLVED, AlertStatus.CLOSED, AlertStatus.EXPIRED]
        ]
        
        priority_distribution = {}
        for priority in AlertPriority:
            priority_distribution[priority.value] = len([a for a in alerts if a.priority == priority])
        
        category_distribution = {}
        for category in AlertCategory:
            category_distribution[category.value] = len([a for a in alerts if a.category == category])
        
        status_distribution = {}
        for status in AlertStatus:
            status_distribution[status.value] = len([a for a in alerts if a.status == status])
        
        alerts_24h = [a for a in alerts if (now - a.created_at).total_seconds() < 86400]
        
        return {
            "total_alerts": len(alerts),
            "active_alerts": len(active_alerts),
            "alerts_last_24h": len(alerts_24h),
            "unacknowledged": len([a for a in active_alerts if a.status == AlertStatus.NEW]),
            "escalated": len([a for a in active_alerts if a.status == AlertStatus.ESCALATED]),
            "priority_distribution": priority_distribution,
            "category_distribution": category_distribution,
            "status_distribution": status_distribution,
            "average_risk_score": sum(a.risk_score for a in alerts) / len(alerts) if alerts else 0,
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get alert manager metrics."""
        stats = self.get_alert_statistics()
        
        return {
            **stats,
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": len([s for s in self.subscriptions.values() if s.is_active]),
            "total_routing_rules": len(self.routing_rules),
            "active_routing_rules": len([r for r in self.routing_rules.values() if r.is_active]),
            "total_audit_entries": len(self.audit_log),
            "websocket_handlers": len(self.websocket_handlers),
        }
