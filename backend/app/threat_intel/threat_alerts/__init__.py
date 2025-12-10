"""
Threat Alerts Module

Provides capabilities for:
- REST endpoints for threat alerts
- WebSocket channels for real-time alerts
- Auto-routing to RTCC dashboards and command ops rooms
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import uuid


class AlertPriority(Enum):
    """Priority levels for threat alerts"""
    P1_CRITICAL = "p1_critical"
    P2_HIGH = "p2_high"
    P3_MODERATE = "p3_moderate"
    P4_LOW = "p4_low"
    P5_INFORMATIONAL = "p5_informational"


class AlertStatus(Enum):
    """Status of a threat alert"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    EXPIRED = "expired"


class AlertCategory(Enum):
    """Categories of threat alerts"""
    DARK_WEB = "dark_web"
    OSINT = "osint"
    EXTREMIST = "extremist"
    GLOBAL_INCIDENT = "global_incident"
    CYBER = "cyber"
    TERRORISM = "terrorism"
    GANG = "gang"
    DRUG = "drug"
    WEAPONS = "weapons"
    OFFICER_SAFETY = "officer_safety"
    PUBLIC_SAFETY = "public_safety"
    INFRASTRUCTURE = "infrastructure"
    COMPOSITE = "composite"


class AlertDestination(Enum):
    """Destinations for alert routing"""
    RTCC_DASHBOARD = "rtcc_dashboard"
    TACTICAL_DASHBOARD = "tactical_dashboard"
    COMMAND_CENTER = "command_center"
    DISPATCH = "dispatch"
    MOBILE_UNITS = "mobile_units"
    INVESTIGATIONS = "investigations"
    INTEL_HUB = "intel_hub"
    FUSION_CENTER = "fusion_center"
    EXTERNAL_AGENCY = "external_agency"


class EscalationLevel(Enum):
    """Escalation levels for alerts"""
    ANALYST = "analyst"
    SUPERVISOR = "supervisor"
    COMMANDER = "commander"
    CHIEF = "chief"
    EXTERNAL = "external"


@dataclass
class ThreatAlert:
    """A threat alert for distribution"""
    alert_id: str = ""
    title: str = ""
    description: str = ""
    priority: AlertPriority = AlertPriority.P3_MODERATE
    status: AlertStatus = AlertStatus.NEW
    category: AlertCategory = AlertCategory.COMPOSITE
    source_module: str = ""
    source_signal_ids: list[str] = field(default_factory=list)
    threat_score: float = 0.0
    threat_level: str = ""
    entity_id: str = ""
    entity_type: str = ""
    entity_name: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float = 0.0
    jurisdiction_codes: list[str] = field(default_factory=list)
    affected_areas: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    destinations: list[AlertDestination] = field(default_factory=list)
    routed_to: list[str] = field(default_factory=list)
    escalation_level: EscalationLevel = EscalationLevel.ANALYST
    assigned_to: str = ""
    acknowledged_by: str = ""
    acknowledged_at: Optional[datetime] = None
    resolved_by: str = ""
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    related_alerts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.alert_id:
            self.alert_id = f"alert-{uuid.uuid4().hex[:12]}"


@dataclass
class AlertSubscription:
    """A subscription to receive alerts"""
    subscription_id: str = ""
    subscriber_id: str = ""
    subscriber_type: str = ""
    subscriber_name: str = ""
    categories: list[AlertCategory] = field(default_factory=list)
    min_priority: AlertPriority = AlertPriority.P3_MODERATE
    jurisdiction_codes: list[str] = field(default_factory=list)
    destinations: list[AlertDestination] = field(default_factory=list)
    webhook_url: str = ""
    websocket_channel: str = ""
    email: str = ""
    sms: str = ""
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.subscription_id:
            self.subscription_id = f"sub-{uuid.uuid4().hex[:12]}"


@dataclass
class RoutingRule:
    """A rule for routing alerts to destinations"""
    rule_id: str = ""
    name: str = ""
    description: str = ""
    categories: list[AlertCategory] = field(default_factory=list)
    min_priority: AlertPriority = AlertPriority.P3_MODERATE
    jurisdiction_codes: list[str] = field(default_factory=list)
    destinations: list[AlertDestination] = field(default_factory=list)
    escalation_threshold_minutes: int = 30
    auto_escalate: bool = False
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = f"route-{uuid.uuid4().hex[:12]}"


@dataclass
class AlertAuditEntry:
    """An audit entry for alert actions"""
    entry_id: str = ""
    alert_id: str = ""
    action: str = ""
    actor_id: str = ""
    actor_name: str = ""
    previous_status: Optional[AlertStatus] = None
    new_status: Optional[AlertStatus] = None
    notes: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.entry_id:
            self.entry_id = f"audit-{uuid.uuid4().hex[:12]}"


class ThreatAlertManager:
    """
    Threat Alert Manager for creating, routing, and managing
    threat intelligence alerts across the RTCC platform.
    """

    def __init__(self):
        self._alerts: dict[str, ThreatAlert] = {}
        self._subscriptions: dict[str, AlertSubscription] = {}
        self._routing_rules: dict[str, RoutingRule] = {}
        self._audit_log: list[AlertAuditEntry] = []
        self._callbacks: list[Callable[[ThreatAlert], None]] = []
        self._websocket_handlers: dict[str, Callable[[ThreatAlert], None]] = {}
        self._events: list[dict[str, Any]] = []
        
        self._priority_order = [
            AlertPriority.P5_INFORMATIONAL,
            AlertPriority.P4_LOW,
            AlertPriority.P3_MODERATE,
            AlertPriority.P2_HIGH,
            AlertPriority.P1_CRITICAL,
        ]
        
        self._default_expiration_hours = {
            AlertPriority.P1_CRITICAL: 24,
            AlertPriority.P2_HIGH: 48,
            AlertPriority.P3_MODERATE: 72,
            AlertPriority.P4_LOW: 168,
            AlertPriority.P5_INFORMATIONAL: 336,
        }

    def register_callback(self, callback: Callable[[ThreatAlert], None]) -> None:
        """Register a callback for new alerts"""
        self._callbacks.append(callback)

    def register_websocket_handler(
        self,
        channel: str,
        handler: Callable[[ThreatAlert], None],
    ) -> None:
        """Register a WebSocket handler for a channel"""
        self._websocket_handlers[channel] = handler

    def _notify_callbacks(self, alert: ThreatAlert) -> None:
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception:
                pass

    def _notify_websocket(self, channel: str, alert: ThreatAlert) -> None:
        """Notify WebSocket handler for a channel"""
        handler = self._websocket_handlers.get(channel)
        if handler:
            try:
                handler(alert)
            except Exception:
                pass

    def _record_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Record an event for audit purposes"""
        self._events.append({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    def _add_audit_entry(
        self,
        alert_id: str,
        action: str,
        actor_id: str = "system",
        actor_name: str = "System",
        previous_status: Optional[AlertStatus] = None,
        new_status: Optional[AlertStatus] = None,
        notes: str = "",
    ) -> AlertAuditEntry:
        """Add an audit entry for an alert action"""
        entry = AlertAuditEntry(
            alert_id=alert_id,
            action=action,
            actor_id=actor_id,
            actor_name=actor_name,
            previous_status=previous_status,
            new_status=new_status,
            notes=notes,
        )
        self._audit_log.append(entry)
        return entry

    def create_alert(
        self,
        title: str,
        description: str,
        priority: AlertPriority,
        category: AlertCategory,
        source_module: str = "",
        source_signal_ids: Optional[list[str]] = None,
        threat_score: float = 0.0,
        threat_level: str = "",
        entity_id: str = "",
        entity_type: str = "",
        entity_name: str = "",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        jurisdiction_codes: Optional[list[str]] = None,
        recommended_actions: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        expires_in_hours: Optional[int] = None,
    ) -> ThreatAlert:
        """Create a new threat alert"""
        if expires_in_hours is None:
            expires_in_hours = self._default_expiration_hours.get(priority, 72)
        
        alert = ThreatAlert(
            title=title,
            description=description,
            priority=priority,
            category=category,
            source_module=source_module,
            source_signal_ids=source_signal_ids or [],
            threat_score=threat_score,
            threat_level=threat_level,
            entity_id=entity_id,
            entity_type=entity_type,
            entity_name=entity_name,
            latitude=latitude,
            longitude=longitude,
            jurisdiction_codes=jurisdiction_codes or [],
            recommended_actions=recommended_actions or [],
            tags=tags or [],
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
        )
        
        self._alerts[alert.alert_id] = alert
        self._add_audit_entry(alert.alert_id, "created", notes=f"Priority: {priority.value}")
        self._record_event("alert_created", {
            "alert_id": alert.alert_id,
            "priority": priority.value,
        })
        
        self._route_alert(alert)
        self._notify_callbacks(alert)
        
        return alert

    def _route_alert(self, alert: ThreatAlert) -> None:
        """Route an alert to appropriate destinations"""
        destinations = set()
        
        for rule in self._routing_rules.values():
            if not rule.enabled:
                continue
            
            if rule.categories and alert.category not in rule.categories:
                continue
            
            rule_priority_index = self._priority_order.index(rule.min_priority)
            alert_priority_index = self._priority_order.index(alert.priority)
            if alert_priority_index < rule_priority_index:
                continue
            
            if rule.jurisdiction_codes:
                if not any(j in alert.jurisdiction_codes for j in rule.jurisdiction_codes):
                    continue
            
            destinations.update(rule.destinations)
        
        if alert.priority == AlertPriority.P1_CRITICAL:
            destinations.add(AlertDestination.COMMAND_CENTER)
            destinations.add(AlertDestination.RTCC_DASHBOARD)
        elif alert.priority == AlertPriority.P2_HIGH:
            destinations.add(AlertDestination.RTCC_DASHBOARD)
        
        alert.destinations = list(destinations)
        
        for dest in destinations:
            alert.routed_to.append(dest.value)
            self._notify_websocket(f"/ws/global-threats/{dest.value}", alert)
        
        self._notify_websocket("/ws/global-threats", alert)
        
        for subscription in self._subscriptions.values():
            if not subscription.enabled:
                continue
            
            if subscription.categories and alert.category not in subscription.categories:
                continue
            
            sub_priority_index = self._priority_order.index(subscription.min_priority)
            alert_priority_index = self._priority_order.index(alert.priority)
            if alert_priority_index < sub_priority_index:
                continue
            
            if subscription.jurisdiction_codes:
                if not any(j in alert.jurisdiction_codes for j in subscription.jurisdiction_codes):
                    continue
            
            if subscription.websocket_channel:
                self._notify_websocket(subscription.websocket_channel, alert)
        
        self._record_event("alert_routed", {
            "alert_id": alert.alert_id,
            "destinations": [d.value for d in destinations],
        })

    def get_alert(self, alert_id: str) -> Optional[ThreatAlert]:
        """Get an alert by ID"""
        return self._alerts.get(alert_id)

    def get_all_alerts(
        self,
        status: Optional[AlertStatus] = None,
        priority: Optional[AlertPriority] = None,
        category: Optional[AlertCategory] = None,
        jurisdiction: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
    ) -> list[ThreatAlert]:
        """Get all alerts with optional filtering"""
        alerts = list(self._alerts.values())
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        if priority:
            alerts = [a for a in alerts if a.priority == priority]
        if category:
            alerts = [a for a in alerts if a.category == category]
        if jurisdiction:
            alerts = [a for a in alerts if jurisdiction in a.jurisdiction_codes]
        if active_only:
            now = datetime.utcnow()
            alerts = [
                a for a in alerts
                if a.status not in [AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE, AlertStatus.EXPIRED]
                and (not a.expires_at or a.expires_at > now)
            ]
        
        alerts.sort(
            key=lambda a: (self._priority_order.index(a.priority), a.created_at),
            reverse=True
        )
        return alerts[:limit]

    def get_alerts_for_destination(
        self,
        destination: AlertDestination,
        active_only: bool = True,
        limit: int = 50,
    ) -> list[ThreatAlert]:
        """Get alerts routed to a specific destination"""
        alerts = [
            a for a in self._alerts.values()
            if destination in a.destinations
        ]
        
        if active_only:
            now = datetime.utcnow()
            alerts = [
                a for a in alerts
                if a.status not in [AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE, AlertStatus.EXPIRED]
                and (not a.expires_at or a.expires_at > now)
            ]
        
        alerts.sort(
            key=lambda a: (self._priority_order.index(a.priority), a.created_at),
            reverse=True
        )
        return alerts[:limit]

    def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str,
        user_name: str,
    ) -> bool:
        """Acknowledge an alert"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return False
        
        previous_status = alert.status
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()
        
        self._add_audit_entry(
            alert_id, "acknowledged",
            actor_id=user_id, actor_name=user_name,
            previous_status=previous_status, new_status=AlertStatus.ACKNOWLEDGED,
        )
        self._record_event("alert_acknowledged", {"alert_id": alert_id, "user_id": user_id})
        
        return True

    def update_alert_status(
        self,
        alert_id: str,
        status: AlertStatus,
        user_id: str = "system",
        user_name: str = "System",
        notes: str = "",
    ) -> bool:
        """Update an alert's status"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return False
        
        previous_status = alert.status
        alert.status = status
        alert.updated_at = datetime.utcnow()
        
        if status == AlertStatus.RESOLVED:
            alert.resolved_by = user_id
            alert.resolved_at = datetime.utcnow()
            alert.resolution_notes = notes
        
        self._add_audit_entry(
            alert_id, f"status_changed_to_{status.value}",
            actor_id=user_id, actor_name=user_name,
            previous_status=previous_status, new_status=status,
            notes=notes,
        )
        self._record_event("alert_status_updated", {
            "alert_id": alert_id,
            "status": status.value,
        })
        
        return True

    def escalate_alert(
        self,
        alert_id: str,
        escalation_level: EscalationLevel,
        user_id: str,
        user_name: str,
        reason: str = "",
    ) -> bool:
        """Escalate an alert to a higher level"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return False
        
        previous_status = alert.status
        alert.status = AlertStatus.ESCALATED
        alert.escalation_level = escalation_level
        alert.updated_at = datetime.utcnow()
        
        if escalation_level in [EscalationLevel.COMMANDER, EscalationLevel.CHIEF]:
            if AlertDestination.COMMAND_CENTER not in alert.destinations:
                alert.destinations.append(AlertDestination.COMMAND_CENTER)
                alert.routed_to.append(AlertDestination.COMMAND_CENTER.value)
        
        self._add_audit_entry(
            alert_id, f"escalated_to_{escalation_level.value}",
            actor_id=user_id, actor_name=user_name,
            previous_status=previous_status, new_status=AlertStatus.ESCALATED,
            notes=reason,
        )
        self._record_event("alert_escalated", {
            "alert_id": alert_id,
            "level": escalation_level.value,
        })
        
        self._notify_websocket(f"/ws/global-threats/escalations", alert)
        
        return True

    def assign_alert(
        self,
        alert_id: str,
        assignee_id: str,
        assignee_name: str,
        assigner_id: str,
        assigner_name: str,
    ) -> bool:
        """Assign an alert to a user"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return False
        
        alert.assigned_to = assignee_id
        alert.status = AlertStatus.INVESTIGATING
        alert.updated_at = datetime.utcnow()
        
        self._add_audit_entry(
            alert_id, f"assigned_to_{assignee_name}",
            actor_id=assigner_id, actor_name=assigner_name,
            new_status=AlertStatus.INVESTIGATING,
        )
        self._record_event("alert_assigned", {
            "alert_id": alert_id,
            "assignee_id": assignee_id,
        })
        
        return True

    def resolve_alert(
        self,
        alert_id: str,
        user_id: str,
        user_name: str,
        resolution_notes: str = "",
        is_false_positive: bool = False,
    ) -> bool:
        """Resolve an alert"""
        status = AlertStatus.FALSE_POSITIVE if is_false_positive else AlertStatus.RESOLVED
        return self.update_alert_status(
            alert_id, status,
            user_id=user_id, user_name=user_name,
            notes=resolution_notes,
        )

    def create_routing_rule(
        self,
        name: str,
        destinations: list[AlertDestination],
        categories: Optional[list[AlertCategory]] = None,
        min_priority: AlertPriority = AlertPriority.P3_MODERATE,
        jurisdiction_codes: Optional[list[str]] = None,
        description: str = "",
        auto_escalate: bool = False,
        escalation_threshold_minutes: int = 30,
    ) -> RoutingRule:
        """Create a routing rule"""
        rule = RoutingRule(
            name=name,
            description=description,
            categories=categories or [],
            min_priority=min_priority,
            jurisdiction_codes=jurisdiction_codes or [],
            destinations=destinations,
            auto_escalate=auto_escalate,
            escalation_threshold_minutes=escalation_threshold_minutes,
        )
        
        self._routing_rules[rule.rule_id] = rule
        self._record_event("routing_rule_created", {"rule_id": rule.rule_id})
        
        return rule

    def get_routing_rule(self, rule_id: str) -> Optional[RoutingRule]:
        """Get a routing rule by ID"""
        return self._routing_rules.get(rule_id)

    def get_all_routing_rules(self) -> list[RoutingRule]:
        """Get all routing rules"""
        return list(self._routing_rules.values())

    def update_routing_rule(
        self,
        rule_id: str,
        enabled: Optional[bool] = None,
        destinations: Optional[list[AlertDestination]] = None,
    ) -> bool:
        """Update a routing rule"""
        rule = self._routing_rules.get(rule_id)
        if not rule:
            return False
        
        if enabled is not None:
            rule.enabled = enabled
        if destinations is not None:
            rule.destinations = destinations
        
        self._record_event("routing_rule_updated", {"rule_id": rule_id})
        return True

    def delete_routing_rule(self, rule_id: str) -> bool:
        """Delete a routing rule"""
        if rule_id in self._routing_rules:
            del self._routing_rules[rule_id]
            self._record_event("routing_rule_deleted", {"rule_id": rule_id})
            return True
        return False

    def create_subscription(
        self,
        subscriber_id: str,
        subscriber_type: str,
        subscriber_name: str,
        categories: Optional[list[AlertCategory]] = None,
        min_priority: AlertPriority = AlertPriority.P3_MODERATE,
        jurisdiction_codes: Optional[list[str]] = None,
        websocket_channel: str = "",
        webhook_url: str = "",
        email: str = "",
    ) -> AlertSubscription:
        """Create an alert subscription"""
        subscription = AlertSubscription(
            subscriber_id=subscriber_id,
            subscriber_type=subscriber_type,
            subscriber_name=subscriber_name,
            categories=categories or [],
            min_priority=min_priority,
            jurisdiction_codes=jurisdiction_codes or [],
            websocket_channel=websocket_channel,
            webhook_url=webhook_url,
            email=email,
        )
        
        self._subscriptions[subscription.subscription_id] = subscription
        self._record_event("subscription_created", {
            "subscription_id": subscription.subscription_id,
        })
        
        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[AlertSubscription]:
        """Get a subscription by ID"""
        return self._subscriptions.get(subscription_id)

    def get_subscriptions_for_subscriber(
        self,
        subscriber_id: str,
    ) -> list[AlertSubscription]:
        """Get all subscriptions for a subscriber"""
        return [
            s for s in self._subscriptions.values()
            if s.subscriber_id == subscriber_id
        ]

    def update_subscription(
        self,
        subscription_id: str,
        enabled: Optional[bool] = None,
        categories: Optional[list[AlertCategory]] = None,
    ) -> bool:
        """Update a subscription"""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        if enabled is not None:
            subscription.enabled = enabled
        if categories is not None:
            subscription.categories = categories
        
        self._record_event("subscription_updated", {
            "subscription_id": subscription_id,
        })
        return True

    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a subscription"""
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            self._record_event("subscription_deleted", {
                "subscription_id": subscription_id,
            })
            return True
        return False

    def get_audit_log(
        self,
        alert_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[AlertAuditEntry]:
        """Get audit log entries"""
        entries = self._audit_log
        
        if alert_id:
            entries = [e for e in entries if e.alert_id == alert_id]
        
        entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def check_expired_alerts(self) -> list[ThreatAlert]:
        """Check and mark expired alerts"""
        now = datetime.utcnow()
        expired = []
        
        for alert in self._alerts.values():
            if alert.status in [AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE, AlertStatus.EXPIRED]:
                continue
            
            if alert.expires_at and alert.expires_at < now:
                alert.status = AlertStatus.EXPIRED
                alert.updated_at = now
                expired.append(alert)
                
                self._add_audit_entry(
                    alert.alert_id, "expired",
                    notes="Alert expired automatically",
                )
        
        return expired

    def get_alert_statistics(
        self,
        since: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """Get alert statistics"""
        alerts = list(self._alerts.values())
        
        if since:
            alerts = [a for a in alerts if a.created_at >= since]
        
        priority_counts = {}
        for priority in AlertPriority:
            priority_counts[priority.value] = len([
                a for a in alerts if a.priority == priority
            ])
        
        status_counts = {}
        for status in AlertStatus:
            status_counts[status.value] = len([
                a for a in alerts if a.status == status
            ])
        
        category_counts = {}
        for category in AlertCategory:
            category_counts[category.value] = len([
                a for a in alerts if a.category == category
            ])
        
        avg_resolution_time = None
        resolved_alerts = [
            a for a in alerts
            if a.resolved_at and a.created_at
        ]
        if resolved_alerts:
            total_time = sum(
                (a.resolved_at - a.created_at).total_seconds()
                for a in resolved_alerts
            )
            avg_resolution_time = total_time / len(resolved_alerts) / 3600
        
        return {
            "total_alerts": len(alerts),
            "by_priority": priority_counts,
            "by_status": status_counts,
            "by_category": category_counts,
            "average_resolution_hours": avg_resolution_time,
            "escalated_count": len([a for a in alerts if a.status == AlertStatus.ESCALATED]),
            "false_positive_count": len([a for a in alerts if a.status == AlertStatus.FALSE_POSITIVE]),
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get threat alert manager metrics"""
        alerts = list(self._alerts.values())
        now = datetime.utcnow()
        
        active_alerts = [
            a for a in alerts
            if a.status not in [AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE, AlertStatus.EXPIRED]
            and (not a.expires_at or a.expires_at > now)
        ]
        
        return {
            "total_alerts": len(alerts),
            "active_alerts": len(active_alerts),
            "total_routing_rules": len(self._routing_rules),
            "total_subscriptions": len(self._subscriptions),
            "total_audit_entries": len(self._audit_log),
            "critical_alerts": len([a for a in active_alerts if a.priority == AlertPriority.P1_CRITICAL]),
            "high_alerts": len([a for a in active_alerts if a.priority == AlertPriority.P2_HIGH]),
            "escalated_alerts": len([a for a in active_alerts if a.status == AlertStatus.ESCALATED]),
            "unacknowledged_alerts": len([a for a in active_alerts if a.status == AlertStatus.NEW]),
            "active_routing_rules": len([r for r in self._routing_rules.values() if r.enabled]),
            "active_subscriptions": len([s for s in self._subscriptions.values() if s.enabled]),
            "total_events": len(self._events),
        }
