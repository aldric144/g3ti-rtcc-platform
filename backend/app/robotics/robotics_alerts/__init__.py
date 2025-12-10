"""
Robotics Alerts Module

Provides alert management for robotics operations including:
- RoboticsAlertManager: Alert creation, routing, and management
- Alert categories and priorities
- Integration with WebSocket channels
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class AlertPriority(Enum):
    """Alert priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class AlertCategory(Enum):
    """Alert categories."""
    FLEET = "fleet"
    TELEMETRY = "telemetry"
    MISSION = "mission"
    PERIMETER = "perimeter"
    SWARM = "swarm"
    HEALTH = "health"
    COMMAND = "command"
    STREAMING = "streaming"
    SYSTEM = "system"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


@dataclass
class RoboticsAlert:
    """Robotics alert."""
    alert_id: str
    category: AlertCategory
    priority: AlertPriority
    status: AlertStatus
    title: str
    description: str
    robot_id: Optional[str]
    swarm_id: Optional[str]
    mission_id: Optional[str]
    position: Optional[Dict[str, float]]
    created_at: str
    acknowledged_at: Optional[str]
    acknowledged_by: Optional[str]
    resolved_at: Optional[str]
    resolved_by: Optional[str]
    expires_at: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertSubscription:
    """Alert subscription."""
    subscription_id: str
    subscriber_id: str
    categories: List[AlertCategory]
    priorities: List[AlertPriority]
    robot_ids: Optional[List[str]]
    swarm_ids: Optional[List[str]]
    is_active: bool
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Alert generation rule."""
    rule_id: str
    name: str
    category: AlertCategory
    priority: AlertPriority
    condition_type: str
    condition_params: Dict[str, Any]
    is_active: bool
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class RoboticsAlertManager:
    """Manager for robotics alerts."""

    def __init__(self):
        self.alerts: Dict[str, RoboticsAlert] = {}
        self.subscriptions: Dict[str, AlertSubscription] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.alert_history: List[RoboticsAlert] = []
        self._init_default_rules()

    def _init_default_rules(self):
        """Initialize default alert rules."""
        default_rules = [
            {
                "name": "Low Battery Alert",
                "category": AlertCategory.HEALTH,
                "priority": AlertPriority.HIGH,
                "condition_type": "battery_low",
                "condition_params": {"threshold": 20},
            },
            {
                "name": "Critical Battery Alert",
                "category": AlertCategory.HEALTH,
                "priority": AlertPriority.CRITICAL,
                "condition_type": "battery_critical",
                "condition_params": {"threshold": 10},
            },
            {
                "name": "Robot Offline Alert",
                "category": AlertCategory.FLEET,
                "priority": AlertPriority.HIGH,
                "condition_type": "robot_offline",
                "condition_params": {"timeout_seconds": 60},
            },
            {
                "name": "Mission Failed Alert",
                "category": AlertCategory.MISSION,
                "priority": AlertPriority.HIGH,
                "condition_type": "mission_failed",
                "condition_params": {},
            },
            {
                "name": "Perimeter Breach Alert",
                "category": AlertCategory.PERIMETER,
                "priority": AlertPriority.CRITICAL,
                "condition_type": "perimeter_breach",
                "condition_params": {},
            },
            {
                "name": "Swarm Disconnection Alert",
                "category": AlertCategory.SWARM,
                "priority": AlertPriority.HIGH,
                "condition_type": "swarm_unit_lost",
                "condition_params": {"timeout_seconds": 30},
            },
            {
                "name": "Motor Overheat Alert",
                "category": AlertCategory.HEALTH,
                "priority": AlertPriority.HIGH,
                "condition_type": "motor_overheat",
                "condition_params": {"threshold_celsius": 80},
            },
            {
                "name": "Command Timeout Alert",
                "category": AlertCategory.COMMAND,
                "priority": AlertPriority.MEDIUM,
                "condition_type": "command_timeout",
                "condition_params": {"timeout_seconds": 30},
            },
        ]

        for rule_data in default_rules:
            self.create_rule(
                name=rule_data["name"],
                category=rule_data["category"],
                priority=rule_data["priority"],
                condition_type=rule_data["condition_type"],
                condition_params=rule_data["condition_params"],
            )

    def create_alert(
        self,
        category: AlertCategory,
        priority: AlertPriority,
        title: str,
        description: str,
        robot_id: Optional[str] = None,
        swarm_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        data: Optional[Dict[str, Any]] = None,
        expires_in_seconds: Optional[int] = None,
    ) -> RoboticsAlert:
        """Create a new alert."""
        alert_id = f"alert-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        expires_at = None
        if expires_in_seconds:
            from datetime import timedelta
            expires_at = (datetime.utcnow() + timedelta(seconds=expires_in_seconds)).isoformat() + "Z"

        alert = RoboticsAlert(
            alert_id=alert_id,
            category=category,
            priority=priority,
            status=AlertStatus.ACTIVE,
            title=title,
            description=description,
            robot_id=robot_id,
            swarm_id=swarm_id,
            mission_id=mission_id,
            position=position,
            created_at=timestamp,
            acknowledged_at=None,
            acknowledged_by=None,
            resolved_at=None,
            resolved_by=None,
            expires_at=expires_at,
            data=data or {},
            metadata={},
        )

        self.alerts[alert_id] = alert
        self.alert_history.append(alert)

        return alert

    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
    ) -> bool:
        """Acknowledge an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False

        if alert.status != AlertStatus.ACTIVE:
            return False

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow().isoformat() + "Z"
        alert.acknowledged_by = acknowledged_by

        return True

    def resolve_alert(
        self,
        alert_id: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None,
    ) -> bool:
        """Resolve an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False

        if alert.status == AlertStatus.RESOLVED:
            return False

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow().isoformat() + "Z"
        alert.resolved_by = resolved_by

        if resolution_notes:
            alert.metadata["resolution_notes"] = resolution_notes

        return True

    def expire_alert(self, alert_id: str) -> bool:
        """Mark an alert as expired."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False

        if alert.status in [AlertStatus.RESOLVED, AlertStatus.EXPIRED]:
            return False

        alert.status = AlertStatus.EXPIRED

        return True

    def get_alert(self, alert_id: str) -> Optional[RoboticsAlert]:
        """Get an alert by ID."""
        return self.alerts.get(alert_id)

    def get_alerts(
        self,
        category: Optional[AlertCategory] = None,
        priority: Optional[AlertPriority] = None,
        status: Optional[AlertStatus] = None,
        robot_id: Optional[str] = None,
        swarm_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        active_only: bool = False,
        limit: int = 100,
    ) -> List[RoboticsAlert]:
        """Get alerts with filtering."""
        alerts = list(self.alerts.values())

        if category:
            alerts = [a for a in alerts if a.category == category]

        if priority:
            alerts = [a for a in alerts if a.priority == priority]

        if status:
            alerts = [a for a in alerts if a.status == status]

        if robot_id:
            alerts = [a for a in alerts if a.robot_id == robot_id]

        if swarm_id:
            alerts = [a for a in alerts if a.swarm_id == swarm_id]

        if mission_id:
            alerts = [a for a in alerts if a.mission_id == mission_id]

        if active_only:
            alerts = [a for a in alerts if a.status == AlertStatus.ACTIVE]

        alerts.sort(key=lambda a: a.created_at, reverse=True)
        return alerts[:limit]

    def get_active_alerts(
        self,
        priority: Optional[AlertPriority] = None,
    ) -> List[RoboticsAlert]:
        """Get all active alerts."""
        alerts = [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]

        if priority:
            alerts = [a for a in alerts if a.priority == priority]

        priority_order = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.LOW: 3,
            AlertPriority.INFORMATIONAL: 4,
        }
        alerts.sort(key=lambda a: (priority_order.get(a.priority, 5), a.created_at))

        return alerts

    def create_subscription(
        self,
        subscriber_id: str,
        categories: List[AlertCategory],
        priorities: List[AlertPriority],
        robot_ids: Optional[List[str]] = None,
        swarm_ids: Optional[List[str]] = None,
    ) -> AlertSubscription:
        """Create an alert subscription."""
        subscription_id = f"sub-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        subscription = AlertSubscription(
            subscription_id=subscription_id,
            subscriber_id=subscriber_id,
            categories=categories,
            priorities=priorities,
            robot_ids=robot_ids,
            swarm_ids=swarm_ids,
            is_active=True,
            created_at=timestamp,
            metadata={},
        )

        self.subscriptions[subscription_id] = subscription

        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[AlertSubscription]:
        """Get a subscription by ID."""
        return self.subscriptions.get(subscription_id)

    def get_subscriptions(
        self,
        subscriber_id: Optional[str] = None,
        active_only: bool = False,
    ) -> List[AlertSubscription]:
        """Get subscriptions with filtering."""
        subscriptions = list(self.subscriptions.values())

        if subscriber_id:
            subscriptions = [s for s in subscriptions if s.subscriber_id == subscriber_id]

        if active_only:
            subscriptions = [s for s in subscriptions if s.is_active]

        return subscriptions

    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return False

        subscription.is_active = False

        return True

    def get_subscribers_for_alert(self, alert: RoboticsAlert) -> List[str]:
        """Get subscribers who should receive an alert."""
        subscribers = []

        for subscription in self.subscriptions.values():
            if not subscription.is_active:
                continue

            if alert.category not in subscription.categories:
                continue

            if alert.priority not in subscription.priorities:
                continue

            if subscription.robot_ids and alert.robot_id:
                if alert.robot_id not in subscription.robot_ids:
                    continue

            if subscription.swarm_ids and alert.swarm_id:
                if alert.swarm_id not in subscription.swarm_ids:
                    continue

            subscribers.append(subscription.subscriber_id)

        return list(set(subscribers))

    def create_rule(
        self,
        name: str,
        category: AlertCategory,
        priority: AlertPriority,
        condition_type: str,
        condition_params: Dict[str, Any],
    ) -> AlertRule:
        """Create an alert rule."""
        rule_id = f"rule-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        rule = AlertRule(
            rule_id=rule_id,
            name=name,
            category=category,
            priority=priority,
            condition_type=condition_type,
            condition_params=condition_params,
            is_active=True,
            created_at=timestamp,
            metadata={},
        )

        self.rules[rule_id] = rule

        return rule

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get a rule by ID."""
        return self.rules.get(rule_id)

    def get_rules(
        self,
        category: Optional[AlertCategory] = None,
        active_only: bool = False,
    ) -> List[AlertRule]:
        """Get rules with filtering."""
        rules = list(self.rules.values())

        if category:
            rules = [r for r in rules if r.category == category]

        if active_only:
            rules = [r for r in rules if r.is_active]

        return rules

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule."""
        rule = self.rules.get(rule_id)
        if not rule:
            return False

        rule.is_active = True
        return True

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule."""
        rule = self.rules.get(rule_id)
        if not rule:
            return False

        rule.is_active = False
        return True

    def check_and_create_alerts(
        self,
        robot_id: str,
        telemetry_data: Dict[str, Any],
    ) -> List[RoboticsAlert]:
        """Check telemetry against rules and create alerts."""
        created_alerts = []

        for rule in self.rules.values():
            if not rule.is_active:
                continue

            should_alert = False
            alert_data = {}

            if rule.condition_type == "battery_low":
                threshold = rule.condition_params.get("threshold", 20)
                battery = telemetry_data.get("battery_level", 100)
                if battery <= threshold:
                    should_alert = True
                    alert_data = {"battery_level": battery, "threshold": threshold}

            elif rule.condition_type == "battery_critical":
                threshold = rule.condition_params.get("threshold", 10)
                battery = telemetry_data.get("battery_level", 100)
                if battery <= threshold:
                    should_alert = True
                    alert_data = {"battery_level": battery, "threshold": threshold}

            elif rule.condition_type == "motor_overheat":
                threshold = rule.condition_params.get("threshold_celsius", 80)
                motor_temps = telemetry_data.get("motor_temperatures", {})
                for motor, temp in motor_temps.items():
                    if temp >= threshold:
                        should_alert = True
                        alert_data = {"motor": motor, "temperature": temp, "threshold": threshold}
                        break

            if should_alert:
                alert = self.create_alert(
                    category=rule.category,
                    priority=rule.priority,
                    title=rule.name,
                    description=f"Alert triggered by rule: {rule.name}",
                    robot_id=robot_id,
                    data=alert_data,
                )
                created_alerts.append(alert)

        return created_alerts

    def cleanup_expired_alerts(self) -> int:
        """Clean up expired alerts."""
        now = datetime.utcnow().isoformat() + "Z"
        expired_count = 0

        for alert in self.alerts.values():
            if alert.expires_at and alert.expires_at < now:
                if alert.status == AlertStatus.ACTIVE:
                    alert.status = AlertStatus.EXPIRED
                    expired_count += 1

        return expired_count

    def get_alert_statistics(
        self,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """Get alert statistics."""
        from datetime import timedelta
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"

        recent_alerts = [a for a in self.alert_history if a.created_at >= cutoff]

        by_category = {}
        by_priority = {}
        by_status = {}

        for alert in recent_alerts:
            cat_key = alert.category.value
            by_category[cat_key] = by_category.get(cat_key, 0) + 1

            pri_key = alert.priority.value
            by_priority[pri_key] = by_priority.get(pri_key, 0) + 1

            status_key = alert.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

        return {
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "by_category": by_category,
            "by_priority": by_priority,
            "by_status": by_status,
            "active_count": len(self.get_active_alerts()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get alert manager metrics."""
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(self.get_active_alerts()),
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": len([s for s in self.subscriptions.values() if s.is_active]),
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules.values() if r.is_active]),
            "alert_history_size": len(self.alert_history),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


__all__ = [
    "RoboticsAlertManager",
    "RoboticsAlert",
    "AlertSubscription",
    "AlertRule",
    "AlertPriority",
    "AlertCategory",
    "AlertStatus",
]
