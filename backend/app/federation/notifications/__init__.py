"""
G3TI RTCC-UIP Multi-Agency Notification Engine
Phase 10: Cross-jurisdiction alerts, bulletins, and notifications
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class NotificationType(str, Enum):
    """Types of multi-agency notifications"""
    BOLO_BROADCAST = "bolo_broadcast"
    OFFICER_SAFETY = "officer_safety"
    TACTICAL_ALERT = "tactical_alert"
    INTELLIGENCE_BULLETIN = "intelligence_bulletin"
    INCIDENT_UPDATE = "incident_update"
    RESOURCE_REQUEST = "resource_request"
    MUTUAL_AID = "mutual_aid"
    AMBER_ALERT = "amber_alert"
    SILVER_ALERT = "silver_alert"
    WEATHER_ALERT = "weather_alert"
    HAZMAT_ALERT = "hazmat_alert"
    ACTIVE_SHOOTER = "active_shooter"
    PURSUIT_NOTIFICATION = "pursuit_notification"
    GENERAL_BROADCAST = "general_broadcast"


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    EXPIRED = "expired"


class DeliveryChannel(str, Enum):
    """Notification delivery channels"""
    WEBSOCKET = "websocket"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    MDT = "mdt"
    CAD = "cad"
    API = "api"


class MultiAgencyNotification:
    """Multi-agency notification"""

    def __init__(
        self,
        notification_type: NotificationType,
        priority: NotificationPriority,
        title: str,
        content: str,
        sender_agency: str,
        sender_user: str,
        target_agencies: list[str],
        target_roles: list[str] | None = None,
        target_users: list[str] | None = None,
        location: dict[str, Any] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        expires_at: datetime | None = None,
        requires_acknowledgment: bool = False,
        related_incident_id: str | None = None,
        related_case_id: str | None = None,
    ):
        self.id = str(uuid4())
        self.notification_type = notification_type
        self.priority = priority
        self.title = title
        self.content = content
        self.sender_agency = sender_agency
        self.sender_user = sender_user
        self.target_agencies = target_agencies
        self.target_roles = target_roles or []
        self.target_users = target_users or []
        self.location = location
        self.attachments = attachments or []
        self.expires_at = expires_at
        self.requires_acknowledgment = requires_acknowledgment
        self.related_incident_id = related_incident_id
        self.related_case_id = related_case_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.deliveries: list[NotificationDelivery] = []


class NotificationDelivery:
    """Delivery record for a notification to a specific recipient"""

    def __init__(
        self,
        notification_id: str,
        recipient_agency: str,
        recipient_user: str | None,
        channel: DeliveryChannel,
    ):
        self.id = str(uuid4())
        self.notification_id = notification_id
        self.recipient_agency = recipient_agency
        self.recipient_user = recipient_user
        self.channel = channel
        self.status = NotificationStatus.PENDING
        self.sent_at: datetime | None = None
        self.delivered_at: datetime | None = None
        self.read_at: datetime | None = None
        self.acknowledged_at: datetime | None = None
        self.acknowledged_by: str | None = None
        self.error_message: str | None = None


class BOLOBroadcast:
    """BOLO (Be On the Lookout) broadcast"""

    def __init__(
        self,
        bolo_type: str,
        priority: NotificationPriority,
        title: str,
        description: str,
        sender_agency: str,
        sender_user: str,
        target_agencies: list[str],
        person_description: dict[str, Any] | None = None,
        vehicle_description: dict[str, Any] | None = None,
        last_known_location: dict[str, Any] | None = None,
        direction_of_travel: str | None = None,
        armed_dangerous: bool = False,
        case_number: str | None = None,
        contact_info: str | None = None,
        expires_at: datetime | None = None,
    ):
        self.id = str(uuid4())
        self.bolo_type = bolo_type
        self.priority = priority
        self.title = title
        self.description = description
        self.sender_agency = sender_agency
        self.sender_user = sender_user
        self.target_agencies = target_agencies
        self.person_description = person_description
        self.vehicle_description = vehicle_description
        self.last_known_location = last_known_location
        self.direction_of_travel = direction_of_travel
        self.armed_dangerous = armed_dangerous
        self.case_number = case_number
        self.contact_info = contact_info
        self.expires_at = expires_at
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.cancelled_at: datetime | None = None
        self.cancelled_by: str | None = None
        self.cancel_reason: str | None = None


class SecureBulletin:
    """Secure cross-jurisdiction bulletin"""

    def __init__(
        self,
        bulletin_type: str,
        classification: str,
        title: str,
        content: str,
        sender_agency: str,
        sender_user: str,
        target_agencies: list[str],
        effective_date: datetime,
        expiration_date: datetime | None = None,
        attachments: list[dict[str, Any]] | None = None,
        requires_acknowledgment: bool = True,
        distribution_list: list[str] | None = None,
    ):
        self.id = str(uuid4())
        self.bulletin_type = bulletin_type
        self.classification = classification
        self.title = title
        self.content = content
        self.sender_agency = sender_agency
        self.sender_user = sender_user
        self.target_agencies = target_agencies
        self.effective_date = effective_date
        self.expiration_date = expiration_date
        self.attachments = attachments or []
        self.requires_acknowledgment = requires_acknowledgment
        self.distribution_list = distribution_list or []
        self.created_at = datetime.utcnow()
        self.acknowledgments: list[dict[str, Any]] = []


class NotificationRule:
    """Rule for automatic notification routing"""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        trigger_type: str,
        trigger_conditions: dict[str, Any],
        notification_type: NotificationType,
        priority: NotificationPriority,
        target_agencies: list[str],
        target_roles: list[str],
        channels: list[DeliveryChannel],
        is_active: bool = True,
    ):
        self.id = rule_id
        self.name = name
        self.description = description
        self.trigger_type = trigger_type
        self.trigger_conditions = trigger_conditions
        self.notification_type = notification_type
        self.priority = priority
        self.target_agencies = target_agencies
        self.target_roles = target_roles
        self.channels = channels
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.triggered_count = 0
        self.last_triggered_at: datetime | None = None


class MultiAgencyNotificationEngine:
    """Engine for multi-agency notifications"""

    def __init__(self):
        self.notifications: dict[str, MultiAgencyNotification] = {}
        self.bolos: dict[str, BOLOBroadcast] = {}
        self.bulletins: dict[str, SecureBulletin] = {}
        self.rules: dict[str, NotificationRule] = {}
        self.agency_subscriptions: dict[str, list[NotificationType]] = {}
        self.delivery_log: list[NotificationDelivery] = []

    def send_notification(
        self,
        notification_type: NotificationType,
        priority: NotificationPriority,
        title: str,
        content: str,
        sender_agency: str,
        sender_user: str,
        target_agencies: list[str],
        target_roles: list[str] | None = None,
        target_users: list[str] | None = None,
        location: dict[str, Any] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        expires_at: datetime | None = None,
        requires_acknowledgment: bool = False,
        related_incident_id: str | None = None,
        related_case_id: str | None = None,
        channels: list[DeliveryChannel] | None = None,
    ) -> MultiAgencyNotification:
        """Send a multi-agency notification"""
        notification = MultiAgencyNotification(
            notification_type=notification_type,
            priority=priority,
            title=title,
            content=content,
            sender_agency=sender_agency,
            sender_user=sender_user,
            target_agencies=target_agencies,
            target_roles=target_roles,
            target_users=target_users,
            location=location,
            attachments=attachments,
            expires_at=expires_at,
            requires_acknowledgment=requires_acknowledgment,
            related_incident_id=related_incident_id,
            related_case_id=related_case_id,
        )
        self.notifications[notification.id] = notification

        # Create deliveries for each target agency
        delivery_channels = channels or [DeliveryChannel.WEBSOCKET, DeliveryChannel.API]
        for agency in target_agencies:
            for channel in delivery_channels:
                delivery = NotificationDelivery(
                    notification_id=notification.id,
                    recipient_agency=agency,
                    recipient_user=None,
                    channel=channel,
                )
                delivery.status = NotificationStatus.SENT
                delivery.sent_at = datetime.utcnow()
                notification.deliveries.append(delivery)
                self.delivery_log.append(delivery)

        return notification

    def broadcast_bolo(
        self,
        bolo_type: str,
        priority: NotificationPriority,
        title: str,
        description: str,
        sender_agency: str,
        sender_user: str,
        target_agencies: list[str],
        person_description: dict[str, Any] | None = None,
        vehicle_description: dict[str, Any] | None = None,
        last_known_location: dict[str, Any] | None = None,
        direction_of_travel: str | None = None,
        armed_dangerous: bool = False,
        case_number: str | None = None,
        contact_info: str | None = None,
        expires_at: datetime | None = None,
    ) -> BOLOBroadcast:
        """Broadcast a BOLO to multiple agencies"""
        bolo = BOLOBroadcast(
            bolo_type=bolo_type,
            priority=priority,
            title=title,
            description=description,
            sender_agency=sender_agency,
            sender_user=sender_user,
            target_agencies=target_agencies,
            person_description=person_description,
            vehicle_description=vehicle_description,
            last_known_location=last_known_location,
            direction_of_travel=direction_of_travel,
            armed_dangerous=armed_dangerous,
            case_number=case_number,
            contact_info=contact_info,
            expires_at=expires_at,
        )
        self.bolos[bolo.id] = bolo

        # Create notification for the BOLO
        self.send_notification(
            notification_type=NotificationType.BOLO_BROADCAST,
            priority=priority,
            title=f"BOLO: {title}",
            content=description,
            sender_agency=sender_agency,
            sender_user=sender_user,
            target_agencies=target_agencies,
            location=last_known_location,
            expires_at=expires_at,
            requires_acknowledgment=True,
        )

        return bolo

    def cancel_bolo(
        self,
        bolo_id: str,
        cancelled_by: str,
        cancel_reason: str,
    ) -> BOLOBroadcast | None:
        """Cancel an active BOLO"""
        bolo = self.bolos.get(bolo_id)
        if bolo and bolo.is_active:
            bolo.is_active = False
            bolo.cancelled_at = datetime.utcnow()
            bolo.cancelled_by = cancelled_by
            bolo.cancel_reason = cancel_reason

            # Send cancellation notification
            self.send_notification(
                notification_type=NotificationType.BOLO_BROADCAST,
                priority=NotificationPriority.HIGH,
                title=f"BOLO CANCELLED: {bolo.title}",
                content=f"BOLO has been cancelled. Reason: {cancel_reason}",
                sender_agency=bolo.sender_agency,
                sender_user=cancelled_by,
                target_agencies=bolo.target_agencies,
            )

            return bolo
        return None

    def send_bulletin(
        self,
        bulletin_type: str,
        classification: str,
        title: str,
        content: str,
        sender_agency: str,
        sender_user: str,
        target_agencies: list[str],
        effective_date: datetime,
        expiration_date: datetime | None = None,
        attachments: list[dict[str, Any]] | None = None,
        requires_acknowledgment: bool = True,
    ) -> SecureBulletin:
        """Send a secure cross-jurisdiction bulletin"""
        bulletin = SecureBulletin(
            bulletin_type=bulletin_type,
            classification=classification,
            title=title,
            content=content,
            sender_agency=sender_agency,
            sender_user=sender_user,
            target_agencies=target_agencies,
            effective_date=effective_date,
            expiration_date=expiration_date,
            attachments=attachments,
            requires_acknowledgment=requires_acknowledgment,
        )
        self.bulletins[bulletin.id] = bulletin

        # Create notification for the bulletin
        self.send_notification(
            notification_type=NotificationType.INTELLIGENCE_BULLETIN,
            priority=NotificationPriority.MEDIUM,
            title=f"Bulletin: {title}",
            content=content,
            sender_agency=sender_agency,
            sender_user=sender_user,
            target_agencies=target_agencies,
            attachments=attachments,
            expires_at=expiration_date,
            requires_acknowledgment=requires_acknowledgment,
        )

        return bulletin

    def acknowledge_bulletin(
        self,
        bulletin_id: str,
        agency: str,
        user: str,
    ) -> bool:
        """Acknowledge receipt of a bulletin"""
        bulletin = self.bulletins.get(bulletin_id)
        if bulletin:
            bulletin.acknowledgments.append({
                "agency": agency,
                "user": user,
                "acknowledged_at": datetime.utcnow().isoformat(),
            })
            return True
        return False

    def get_notification(
        self,
        notification_id: str,
    ) -> MultiAgencyNotification | None:
        """Get a notification by ID"""
        return self.notifications.get(notification_id)

    def get_notifications_for_agency(
        self,
        agency_id: str,
        notification_type: NotificationType | None = None,
        priority: NotificationPriority | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[MultiAgencyNotification]:
        """Get notifications for a specific agency"""
        notifications = [
            n for n in self.notifications.values()
            if agency_id in n.target_agencies
        ]

        if notification_type:
            notifications = [
                n for n in notifications
                if n.notification_type == notification_type
            ]
        if priority:
            notifications = [n for n in notifications if n.priority == priority]
        if since:
            notifications = [n for n in notifications if n.created_at >= since]

        # Sort by created_at descending
        notifications.sort(key=lambda n: n.created_at, reverse=True)
        return notifications[:limit]

    def get_active_bolos(
        self,
        agency_id: str | None = None,
    ) -> list[BOLOBroadcast]:
        """Get active BOLOs"""
        bolos = [b for b in self.bolos.values() if b.is_active]
        if agency_id:
            bolos = [b for b in bolos if agency_id in b.target_agencies]
        return bolos

    def get_bulletins_for_agency(
        self,
        agency_id: str,
        since: datetime | None = None,
    ) -> list[SecureBulletin]:
        """Get bulletins for a specific agency"""
        bulletins = [
            b for b in self.bulletins.values()
            if agency_id in b.target_agencies
        ]
        if since:
            bulletins = [b for b in bulletins if b.created_at >= since]
        return bulletins

    def acknowledge_notification(
        self,
        notification_id: str,
        agency: str,
        user: str,
    ) -> bool:
        """Acknowledge a notification"""
        notification = self.notifications.get(notification_id)
        if notification:
            for delivery in notification.deliveries:
                if delivery.recipient_agency == agency:
                    delivery.status = NotificationStatus.ACKNOWLEDGED
                    delivery.acknowledged_at = datetime.utcnow()
                    delivery.acknowledged_by = user
            return True
        return False

    def mark_notification_read(
        self,
        notification_id: str,
        agency: str,
        user: str,
    ) -> bool:
        """Mark a notification as read"""
        notification = self.notifications.get(notification_id)
        if notification:
            for delivery in notification.deliveries:
                if delivery.recipient_agency == agency:
                    if delivery.status != NotificationStatus.ACKNOWLEDGED:
                        delivery.status = NotificationStatus.READ
                    delivery.read_at = datetime.utcnow()
            return True
        return False

    def create_notification_rule(
        self,
        name: str,
        description: str,
        trigger_type: str,
        trigger_conditions: dict[str, Any],
        notification_type: NotificationType,
        priority: NotificationPriority,
        target_agencies: list[str],
        target_roles: list[str],
        channels: list[DeliveryChannel],
    ) -> NotificationRule:
        """Create a notification routing rule"""
        rule = NotificationRule(
            rule_id=str(uuid4()),
            name=name,
            description=description,
            trigger_type=trigger_type,
            trigger_conditions=trigger_conditions,
            notification_type=notification_type,
            priority=priority,
            target_agencies=target_agencies,
            target_roles=target_roles,
            channels=channels,
        )
        self.rules[rule.id] = rule
        return rule

    def evaluate_rules(
        self,
        event_type: str,
        event_data: dict[str, Any],
        sender_agency: str,
        sender_user: str,
    ) -> list[MultiAgencyNotification]:
        """Evaluate notification rules against an event"""
        triggered_notifications = []

        for rule in self.rules.values():
            if not rule.is_active:
                continue
            if rule.trigger_type != event_type:
                continue

            # Check trigger conditions
            if self._check_conditions(rule.trigger_conditions, event_data):
                notification = self.send_notification(
                    notification_type=rule.notification_type,
                    priority=rule.priority,
                    title=f"Auto-notification: {rule.name}",
                    content=str(event_data),
                    sender_agency=sender_agency,
                    sender_user=sender_user,
                    target_agencies=rule.target_agencies,
                    target_roles=rule.target_roles,
                    channels=rule.channels,
                )
                triggered_notifications.append(notification)

                # Update rule stats
                rule.triggered_count += 1
                rule.last_triggered_at = datetime.utcnow()

        return triggered_notifications

    def _check_conditions(
        self,
        conditions: dict[str, Any],
        data: dict[str, Any],
    ) -> bool:
        """Check if data matches conditions"""
        for key, expected in conditions.items():
            if key not in data:
                return False
            if isinstance(expected, dict):
                if "min" in expected and data[key] < expected["min"]:
                    return False
                if "max" in expected and data[key] > expected["max"]:
                    return False
                if "equals" in expected and data[key] != expected["equals"]:
                    return False
                if "contains" in expected and expected["contains"] not in str(data[key]):
                    return False
            elif data[key] != expected:
                return False
        return True

    def subscribe_agency(
        self,
        agency_id: str,
        notification_types: list[NotificationType],
    ) -> None:
        """Subscribe an agency to notification types"""
        self.agency_subscriptions[agency_id] = notification_types

    def unsubscribe_agency(
        self,
        agency_id: str,
        notification_types: list[NotificationType] | None = None,
    ) -> None:
        """Unsubscribe an agency from notification types"""
        if notification_types is None:
            self.agency_subscriptions.pop(agency_id, None)
        elif agency_id in self.agency_subscriptions:
            self.agency_subscriptions[agency_id] = [
                nt for nt in self.agency_subscriptions[agency_id]
                if nt not in notification_types
            ]

    def get_delivery_stats(
        self,
        agency_id: str | None = None,
        since: datetime | None = None,
    ) -> dict[str, Any]:
        """Get delivery statistics"""
        deliveries = self.delivery_log.copy()

        if agency_id:
            deliveries = [
                d for d in deliveries
                if d.recipient_agency == agency_id
            ]
        if since:
            deliveries = [
                d for d in deliveries
                if d.sent_at and d.sent_at >= since
            ]

        stats = {
            "total": len(deliveries),
            "by_status": {},
            "by_channel": {},
        }

        for delivery in deliveries:
            status = delivery.status.value
            channel = delivery.channel.value

            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            stats["by_channel"][channel] = stats["by_channel"].get(channel, 0) + 1

        return stats


# Create singleton instance
notification_engine = MultiAgencyNotificationEngine()
