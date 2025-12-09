"""
G3TI RTCC-UIP Push Alerts Module.

Provides push notification capabilities for mobile devices and MDTs:
- Officer safety alerts (threat level, ambush detection)
- Gunfire alerts (ShotSpotter)
- LPR hit alerts
- High-risk suspect/location alerts
- Tactical surge notifications
- CAD priority calls
- RTCC automated bulletins

All alerts are logged for CJIS compliance.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class AlertType(str, Enum):
    """Types of push alerts."""
    OFFICER_SAFETY = "officer_safety"
    GUNFIRE = "gunfire"
    LPR_HIT = "lpr_hit"
    HIGH_RISK_SUSPECT = "high_risk_suspect"
    HIGH_RISK_LOCATION = "high_risk_location"
    TACTICAL_SURGE = "tactical_surge"
    CAD_PRIORITY = "cad_priority"
    BULLETIN = "bulletin"
    AMBUSH_WARNING = "ambush_warning"
    OFFICER_DOWN = "officer_down"
    BOLO = "bolo"
    WARRANT = "warrant"
    SYSTEM = "system"


class AlertPriority(str, Enum):
    """Alert priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"


class DeliveryChannel(str, Enum):
    """Alert delivery channels."""
    PUSH = "push"  # Mobile push notification
    MDT = "mdt"  # Mobile Data Terminal
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    RADIO = "radio"  # CAD/Radio integration


class PushAlert(BaseModel):
    """Schema for a push alert."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: AlertType
    priority: AlertPriority = AlertPriority.NORMAL

    # Content
    title: str
    body: str
    summary: str | None = None

    # Targeting
    target_badges: list[str] = Field(default_factory=list)  # Specific officers
    target_units: list[str] = Field(default_factory=list)  # Specific units
    target_shifts: list[str] = Field(default_factory=list)  # Shifts (A, B, C)
    target_districts: list[str] = Field(default_factory=list)  # Districts
    target_roles: list[str] = Field(default_factory=list)  # Roles
    broadcast_all: bool = False  # Send to all

    # Location context
    latitude: float | None = None
    longitude: float | None = None
    radius_meters: float | None = None  # For geo-targeted alerts
    address: str | None = None

    # Linked data
    linked_entity_id: str | None = None
    linked_entity_type: str | None = None
    linked_incident_id: str | None = None
    linked_call_id: str | None = None

    # Delivery
    channels: list[DeliveryChannel] = Field(default_factory=lambda: [DeliveryChannel.PUSH])
    status: AlertStatus = AlertStatus.PENDING
    delivery_results: dict[str, Any] = Field(default_factory=dict)

    # Actions
    action_url: str | None = None
    action_buttons: list[dict[str, str]] = Field(default_factory=list)
    requires_acknowledgment: bool = False
    acknowledged_by: list[str] = Field(default_factory=list)

    # Metadata
    source: str = "rtcc"  # rtcc, shotspotter, lpr, cad, etc.
    metadata: dict[str, Any] = Field(default_factory=dict)
    expires_at: datetime | None = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sent_at: datetime | None = None

    # CJIS compliance
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class AlertTemplate(BaseModel):
    """Template for generating alerts."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    alert_type: AlertType
    priority: AlertPriority = AlertPriority.NORMAL
    title_template: str
    body_template: str
    channels: list[DeliveryChannel] = Field(default_factory=lambda: [DeliveryChannel.PUSH])
    requires_acknowledgment: bool = False
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlertsManager:
    """
    Central manager for push alerts.

    Handles alert creation, delivery, tracking, and acknowledgment.
    """

    def __init__(
        self,
        redis_manager: Any | None = None,
        push_service: Any | None = None,
    ):
        """
        Initialize the alerts manager.

        Args:
            redis_manager: Redis manager for caching and pub/sub
            push_service: External push notification service
        """
        self.redis = redis_manager
        self.push_service = push_service

        # In-memory stores
        self._alerts: dict[str, PushAlert] = {}
        self._alert_history: list[PushAlert] = []
        self._templates: dict[str, AlertTemplate] = {}
        self._user_alerts: dict[str, list[str]] = {}  # badge -> alert_ids

        # Initialize default templates
        self._initialize_templates()

        logger.info("alerts_manager_initialized")

    def _initialize_templates(self) -> None:
        """Initialize default alert templates."""
        templates = [
            AlertTemplate(
                id="officer_safety",
                name="Officer Safety Alert",
                alert_type=AlertType.OFFICER_SAFETY,
                priority=AlertPriority.CRITICAL,
                title_template="OFFICER SAFETY: {threat_type}",
                body_template="{description} at {location}. Threat level: {threat_level}",
                channels=[DeliveryChannel.PUSH, DeliveryChannel.MDT],
                requires_acknowledgment=True,
            ),
            AlertTemplate(
                id="gunfire",
                name="Gunfire Detected",
                alert_type=AlertType.GUNFIRE,
                priority=AlertPriority.URGENT,
                title_template="GUNFIRE DETECTED",
                body_template="{rounds} rounds detected at {location}. {distance}m from your position.",
                channels=[DeliveryChannel.PUSH, DeliveryChannel.MDT],
                requires_acknowledgment=False,
            ),
            AlertTemplate(
                id="lpr_hit",
                name="LPR Hit Alert",
                alert_type=AlertType.LPR_HIT,
                priority=AlertPriority.HIGH,
                title_template="LPR HIT: {plate}",
                body_template="Vehicle {plate} ({reason}) spotted at {location}. {vehicle_description}",
                channels=[DeliveryChannel.PUSH, DeliveryChannel.MDT],
                requires_acknowledgment=False,
            ),
            AlertTemplate(
                id="ambush_warning",
                name="Ambush Warning",
                alert_type=AlertType.AMBUSH_WARNING,
                priority=AlertPriority.CRITICAL,
                title_template="AMBUSH WARNING",
                body_template="Potential ambush indicators detected at {location}. {indicators}",
                channels=[DeliveryChannel.PUSH, DeliveryChannel.MDT, DeliveryChannel.RADIO],
                requires_acknowledgment=True,
            ),
            AlertTemplate(
                id="officer_down",
                name="Officer Down",
                alert_type=AlertType.OFFICER_DOWN,
                priority=AlertPriority.CRITICAL,
                title_template="OFFICER DOWN - {badge}",
                body_template="Officer {badge} ({unit}) emergency at {location}. Immediate response required.",
                channels=[DeliveryChannel.PUSH, DeliveryChannel.MDT, DeliveryChannel.RADIO],
                requires_acknowledgment=True,
            ),
            AlertTemplate(
                id="bolo",
                name="BOLO Alert",
                alert_type=AlertType.BOLO,
                priority=AlertPriority.HIGH,
                title_template="BOLO: {subject_type}",
                body_template="{description}. Last seen: {last_seen}. {additional_info}",
                channels=[DeliveryChannel.PUSH, DeliveryChannel.MDT],
                requires_acknowledgment=False,
            ),
            AlertTemplate(
                id="cad_priority",
                name="Priority CAD Call",
                alert_type=AlertType.CAD_PRIORITY,
                priority=AlertPriority.URGENT,
                title_template="{priority} - {call_type}",
                body_template="{description} at {location}. Units needed: {units_needed}",
                channels=[DeliveryChannel.PUSH, DeliveryChannel.MDT],
                requires_acknowledgment=False,
            ),
        ]

        for template in templates:
            self._templates[template.id] = template

        logger.info("alert_templates_initialized", count=len(templates))

    async def create_alert(
        self,
        alert_type: AlertType,
        title: str,
        body: str,
        priority: AlertPriority = AlertPriority.NORMAL,
        target_badges: list[str] | None = None,
        target_units: list[str] | None = None,
        target_shifts: list[str] | None = None,
        target_districts: list[str] | None = None,
        broadcast_all: bool = False,
        latitude: float | None = None,
        longitude: float | None = None,
        radius_meters: float | None = None,
        address: str | None = None,
        linked_entity_id: str | None = None,
        linked_entity_type: str | None = None,
        linked_incident_id: str | None = None,
        linked_call_id: str | None = None,
        channels: list[DeliveryChannel] | None = None,
        requires_acknowledgment: bool = False,
        action_url: str | None = None,
        source: str = "rtcc",
        metadata: dict[str, Any] | None = None,
        expires_at: datetime | None = None,
    ) -> PushAlert:
        """
        Create and send a push alert.

        Args:
            alert_type: Type of alert
            title: Alert title
            body: Alert body text
            priority: Alert priority
            target_badges: Specific officer badges to target
            target_units: Specific units to target
            target_shifts: Shifts to target
            target_districts: Districts to target
            broadcast_all: Send to all officers
            latitude: Location latitude
            longitude: Location longitude
            radius_meters: Radius for geo-targeting
            address: Location address
            linked_entity_id: Linked entity ID
            linked_entity_type: Linked entity type
            linked_incident_id: Linked incident ID
            linked_call_id: Linked CAD call ID
            channels: Delivery channels
            requires_acknowledgment: Whether acknowledgment is required
            action_url: URL for alert action
            source: Alert source
            metadata: Additional metadata
            expires_at: Alert expiration time

        Returns:
            The created alert
        """
        alert = PushAlert(
            alert_type=alert_type,
            priority=priority,
            title=title,
            body=body,
            target_badges=target_badges or [],
            target_units=target_units or [],
            target_shifts=target_shifts or [],
            target_districts=target_districts or [],
            broadcast_all=broadcast_all,
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
            address=address,
            linked_entity_id=linked_entity_id,
            linked_entity_type=linked_entity_type,
            linked_incident_id=linked_incident_id,
            linked_call_id=linked_call_id,
            channels=channels or [DeliveryChannel.PUSH],
            requires_acknowledgment=requires_acknowledgment,
            action_url=action_url,
            source=source,
            metadata=metadata or {},
            expires_at=expires_at,
        )

        # Store alert
        self._alerts[alert.id] = alert

        # Send alert
        await self._send_alert(alert)

        # Log for CJIS compliance
        logger.info(
            "alert_created",
            alert_id=alert.id,
            alert_type=alert_type.value,
            priority=priority.value,
            source=source,
            audit_id=alert.audit_id,
        )

        return alert

    async def create_alert_from_template(
        self,
        template_id: str,
        variables: dict[str, Any],
        target_badges: list[str] | None = None,
        target_units: list[str] | None = None,
        target_shifts: list[str] | None = None,
        broadcast_all: bool = False,
        latitude: float | None = None,
        longitude: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PushAlert:
        """
        Create an alert from a template.

        Args:
            template_id: Template ID to use
            variables: Variables to substitute in template
            target_badges: Target officer badges
            target_units: Target units
            target_shifts: Target shifts
            broadcast_all: Send to all
            latitude: Location latitude
            longitude: Location longitude
            metadata: Additional metadata

        Returns:
            The created alert
        """
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Substitute variables in template
        title = template.title_template.format(**variables)
        body = template.body_template.format(**variables)

        return await self.create_alert(
            alert_type=template.alert_type,
            title=title,
            body=body,
            priority=template.priority,
            target_badges=target_badges,
            target_units=target_units,
            target_shifts=target_shifts,
            broadcast_all=broadcast_all,
            latitude=latitude,
            longitude=longitude,
            channels=template.channels,
            requires_acknowledgment=template.requires_acknowledgment,
            metadata=metadata,
        )

    async def _send_alert(self, alert: PushAlert) -> None:
        """
        Send an alert through configured channels.

        Args:
            alert: Alert to send
        """
        alert.sent_at = datetime.now(UTC)
        delivery_results = {}

        for channel in alert.channels:
            try:
                result = await self._send_to_channel(alert, channel)
                delivery_results[channel.value] = {
                    "status": "sent",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "result": result,
                }
            except Exception as e:
                logger.error(
                    "alert_delivery_failed",
                    alert_id=alert.id,
                    channel=channel.value,
                    error=str(e),
                )
                delivery_results[channel.value] = {
                    "status": "failed",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "error": str(e),
                }

        alert.delivery_results = delivery_results
        alert.status = AlertStatus.SENT

        # Track alerts per user
        for badge in alert.target_badges:
            if badge not in self._user_alerts:
                self._user_alerts[badge] = []
            self._user_alerts[badge].append(alert.id)

        logger.info(
            "alert_sent",
            alert_id=alert.id,
            channels=[c.value for c in alert.channels],
            target_count=len(alert.target_badges) + len(alert.target_units),
        )

    async def _send_to_channel(
        self,
        alert: PushAlert,
        channel: DeliveryChannel,
    ) -> dict[str, Any]:
        """
        Send alert to a specific channel.

        Args:
            alert: Alert to send
            channel: Delivery channel

        Returns:
            Delivery result
        """
        # Placeholder for actual push notification integration
        # In production, this would integrate with:
        # - Firebase Cloud Messaging (FCM) for mobile push
        # - MDT vendor API for MDT alerts
        # - Email service for email alerts
        # - SMS gateway for SMS alerts

        if channel == DeliveryChannel.PUSH:
            return await self._send_push_notification(alert)
        elif channel == DeliveryChannel.MDT:
            return await self._send_mdt_notification(alert)
        elif channel == DeliveryChannel.EMAIL:
            return await self._send_email_notification(alert)
        elif channel == DeliveryChannel.SMS:
            return await self._send_sms_notification(alert)
        elif channel == DeliveryChannel.IN_APP:
            return await self._send_in_app_notification(alert)
        elif channel == DeliveryChannel.RADIO:
            return await self._send_radio_notification(alert)
        else:
            return {"status": "unsupported_channel"}

    async def _send_push_notification(self, alert: PushAlert) -> dict[str, Any]:
        """Send mobile push notification."""
        # Placeholder - would integrate with FCM/APNS
        logger.debug("sending_push_notification", alert_id=alert.id)
        return {
            "provider": "fcm",
            "message_id": str(uuid.uuid4()),
            "recipients": len(alert.target_badges),
        }

    async def _send_mdt_notification(self, alert: PushAlert) -> dict[str, Any]:
        """Send MDT notification."""
        # Placeholder - would integrate with MDT vendor API
        logger.debug("sending_mdt_notification", alert_id=alert.id)
        return {
            "provider": "mdt",
            "message_id": str(uuid.uuid4()),
            "units": len(alert.target_units),
        }

    async def _send_email_notification(self, alert: PushAlert) -> dict[str, Any]:
        """Send email notification."""
        # Placeholder - would integrate with email service
        logger.debug("sending_email_notification", alert_id=alert.id)
        return {"provider": "email", "message_id": str(uuid.uuid4())}

    async def _send_sms_notification(self, alert: PushAlert) -> dict[str, Any]:
        """Send SMS notification."""
        # Placeholder - would integrate with SMS gateway
        logger.debug("sending_sms_notification", alert_id=alert.id)
        return {"provider": "sms", "message_id": str(uuid.uuid4())}

    async def _send_in_app_notification(self, alert: PushAlert) -> dict[str, Any]:
        """Send in-app notification."""
        # Would publish to WebSocket
        logger.debug("sending_in_app_notification", alert_id=alert.id)
        return {"provider": "websocket", "message_id": str(uuid.uuid4())}

    async def _send_radio_notification(self, alert: PushAlert) -> dict[str, Any]:
        """Send radio/CAD notification."""
        # Placeholder - would integrate with CAD system
        logger.debug("sending_radio_notification", alert_id=alert.id)
        return {"provider": "cad", "message_id": str(uuid.uuid4())}

    async def acknowledge_alert(
        self,
        alert_id: str,
        badge: str,
    ) -> PushAlert:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert ID
            badge: Officer badge acknowledging

        Returns:
            Updated alert
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        if badge not in alert.acknowledged_by:
            alert.acknowledged_by.append(badge)

        logger.info(
            "alert_acknowledged",
            alert_id=alert_id,
            badge=badge,
            audit_id=alert.audit_id,
        )

        return alert

    async def get_alert(self, alert_id: str) -> PushAlert | None:
        """Get an alert by ID."""
        return self._alerts.get(alert_id)

    async def get_alerts_for_badge(
        self,
        badge: str,
        limit: int = 50,
        include_read: bool = False,
    ) -> list[PushAlert]:
        """
        Get alerts for a specific officer.

        Args:
            badge: Officer badge
            limit: Maximum alerts to return
            include_read: Include read alerts

        Returns:
            List of alerts
        """
        alert_ids = self._user_alerts.get(badge, [])
        alerts = [self._alerts[aid] for aid in alert_ids if aid in self._alerts]

        if not include_read:
            alerts = [a for a in alerts if a.status != AlertStatus.READ]

        # Sort by priority and time
        priority_order = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.URGENT: 1,
            AlertPriority.HIGH: 2,
            AlertPriority.NORMAL: 3,
            AlertPriority.LOW: 4,
        }
        alerts.sort(key=lambda a: (priority_order.get(a.priority, 5), a.created_at), reverse=True)

        return alerts[:limit]

    async def get_recent_alerts(
        self,
        alert_type: AlertType | None = None,
        priority: AlertPriority | None = None,
        limit: int = 50,
    ) -> list[PushAlert]:
        """
        Get recent alerts with optional filters.

        Args:
            alert_type: Filter by type
            priority: Filter by priority
            limit: Maximum alerts

        Returns:
            List of alerts
        """
        alerts = list(self._alerts.values())

        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        if priority:
            alerts = [a for a in alerts if a.priority == priority]

        alerts.sort(key=lambda a: a.created_at, reverse=True)

        return alerts[:limit]

    async def mark_alert_read(self, alert_id: str, badge: str) -> PushAlert:
        """Mark an alert as read."""
        alert = self._alerts.get(alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        alert.status = AlertStatus.READ

        logger.debug("alert_marked_read", alert_id=alert_id, badge=badge)

        return alert

    def get_template(self, template_id: str) -> AlertTemplate | None:
        """Get an alert template."""
        return self._templates.get(template_id)

    def get_all_templates(self) -> list[AlertTemplate]:
        """Get all alert templates."""
        return list(self._templates.values())


# Convenience function for sending push notifications
async def send_push_notification(
    badge: str,
    payload: dict[str, Any],
    alerts_manager: AlertsManager | None = None,
) -> PushAlert | None:
    """
    Send a push notification to an officer.

    Args:
        badge: Officer badge
        payload: Notification payload
        alerts_manager: Alerts manager instance

    Returns:
        Created alert or None
    """
    if not alerts_manager:
        logger.warning("alerts_manager_not_configured")
        return None

    return await alerts_manager.create_alert(
        alert_type=AlertType(payload.get("type", "system")),
        title=payload.get("title", "Notification"),
        body=payload.get("body", ""),
        priority=AlertPriority(payload.get("priority", "normal")),
        target_badges=[badge],
        metadata=payload.get("metadata", {}),
    )


# Export classes
__all__ = [
    "AlertsManager",
    "PushAlert",
    "AlertTemplate",
    "AlertType",
    "AlertPriority",
    "AlertStatus",
    "DeliveryChannel",
    "send_push_notification",
]
