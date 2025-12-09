"""
G3TI RTCC-UIP Mobile Module
Officer Mobile API Gateway with authentication, rate limiting, and event streaming.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """Mobile device types."""
    IOS = "ios"
    ANDROID = "android"
    MDT = "mdt"
    TABLET = "tablet"
    UNKNOWN = "unknown"


class DeviceStatus(str, Enum):
    """Device registration status."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class AlertPriority(str, Enum):
    """Mobile alert priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(str, Enum):
    """Mobile alert types."""
    DISPATCH = "dispatch"
    OFFICER_SAFETY = "officer_safety"
    BOLO = "bolo"
    INTEL = "intel"
    MESSAGE = "message"
    AMBUSH = "ambush"
    HOTZONE = "hotzone"
    THREAT = "threat"
    SYSTEM = "system"


class UnitStatus(str, Enum):
    """Unit status codes."""
    AVAILABLE = "available"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    TRANSPORTING = "transporting"
    AT_HOSPITAL = "at_hospital"
    REPORTS = "reports"
    OUT_OF_SERVICE = "out_of_service"
    OFF_DUTY = "off_duty"


class DeviceFingerprint(BaseModel):
    """Device fingerprint for security validation."""
    device_id: str
    device_type: DeviceType
    os_version: str | None = None
    app_version: str | None = None
    hardware_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    fingerprint_hash: str | None = None

    class Config:
        use_enum_values = True


class RegisteredDevice(BaseModel):
    """Registered mobile device."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    badge_number: str
    officer_id: str
    device_fingerprint: DeviceFingerprint
    device_token: str | None = None
    push_token: str | None = None
    status: DeviceStatus = DeviceStatus.PENDING
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    last_ip: str | None = None
    failed_attempts: int = 0
    locked_until: datetime | None = None

    class Config:
        use_enum_values = True


class MobileSession(BaseModel):
    """Mobile authentication session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    badge_number: str
    officer_id: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str | None = None
    is_active: bool = True


class MobileAlert(BaseModel):
    """Mobile alert notification."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: AlertType
    priority: AlertPriority
    title: str
    body: str
    data: dict[str, Any] = Field(default_factory=dict)
    target_badges: list[str] = Field(default_factory=list)
    target_units: list[str] = Field(default_factory=list)
    target_all: bool = False
    geo_fence: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    read_by: list[str] = Field(default_factory=list)
    acknowledged_by: list[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class DispatchCall(BaseModel):
    """Active dispatch call for mobile."""
    id: str
    call_number: str
    call_type: str
    priority: int
    location: str
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    assigned_units: list[str] = Field(default_factory=list)
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: list[str] = Field(default_factory=list)
    hazards: list[str] = Field(default_factory=list)


class MobileMessage(BaseModel):
    """Mobile messaging."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_badge: str
    sender_name: str
    recipient_badges: list[str] = Field(default_factory=list)
    recipient_units: list[str] = Field(default_factory=list)
    channel: str | None = None
    content: str
    attachments: list[str] = Field(default_factory=list)
    priority: AlertPriority = AlertPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_by: list[str] = Field(default_factory=list)
    is_rtcc: bool = False

    class Config:
        use_enum_values = True


class UnitStatusUpdate(BaseModel):
    """Unit status update."""
    badge_number: str
    unit_id: str
    status: UnitStatus
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    call_id: str | None = None
    notes: str | None = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class IntelFeedItem(BaseModel):
    """Intelligence feed item for mobile."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    intel_type: str
    title: str
    summary: str
    entity_id: str | None = None
    entity_type: str | None = None
    priority: AlertPriority = AlertPriority.MEDIUM
    images: list[str] = Field(default_factory=list)
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    related_calls: list[str] = Field(default_factory=list)
    related_entities: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    source: str = "rtcc"

    class Config:
        use_enum_values = True


class RateLimitEntry(BaseModel):
    """Rate limit tracking entry."""
    key: str
    requests: int = 0
    window_start: datetime = Field(default_factory=datetime.utcnow)
    blocked_until: datetime | None = None


class MobileGatewayManager:
    """
    Officer Mobile API Gateway Manager.
    Handles authentication, device registration, rate limiting, and event streaming.
    """

    def __init__(self) -> None:
        """Initialize the mobile gateway manager."""
        self._devices: dict[str, RegisteredDevice] = {}
        self._sessions: dict[str, MobileSession] = {}
        self._alerts: dict[str, MobileAlert] = {}
        self._dispatch_calls: dict[str, DispatchCall] = {}
        self._messages: dict[str, MobileMessage] = {}
        self._unit_statuses: dict[str, UnitStatusUpdate] = {}
        self._intel_feed: dict[str, IntelFeedItem] = {}
        self._rate_limits: dict[str, RateLimitEntry] = {}
        self._event_subscribers: dict[str, list[str]] = {}

        # Configuration
        self._token_expiry_hours = 24
        self._refresh_token_expiry_days = 30
        self._rate_limit_requests = 100
        self._rate_limit_window_seconds = 60
        self._max_failed_attempts = 5
        self._lockout_minutes = 30

    def _generate_token(self) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)

    def _generate_fingerprint_hash(self, fingerprint: DeviceFingerprint) -> str:
        """Generate a hash from device fingerprint."""
        data = f"{fingerprint.device_id}:{fingerprint.device_type}:{fingerprint.hardware_id}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _check_rate_limit(self, key: str) -> tuple[bool, int]:
        """
        Check if request is rate limited.

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = datetime.utcnow()
        entry = self._rate_limits.get(key)

        if not entry:
            entry = RateLimitEntry(key=key)
            self._rate_limits[key] = entry

        # Check if blocked
        if entry.blocked_until and now < entry.blocked_until:
            return False, 0

        # Reset window if expired
        window_end = entry.window_start + timedelta(seconds=self._rate_limit_window_seconds)
        if now > window_end:
            entry.requests = 0
            entry.window_start = now
            entry.blocked_until = None

        # Check limit
        if entry.requests >= self._rate_limit_requests:
            entry.blocked_until = now + timedelta(seconds=self._rate_limit_window_seconds)
            return False, 0

        entry.requests += 1
        remaining = self._rate_limit_requests - entry.requests
        return True, remaining

    async def register_device(
        self,
        badge_number: str,
        officer_id: str,
        fingerprint: DeviceFingerprint,
        push_token: str | None = None,
    ) -> RegisteredDevice | None:
        """
        Register a new mobile device.

        Args:
            badge_number: Officer badge number
            officer_id: Officer ID
            fingerprint: Device fingerprint
            push_token: Push notification token

        Returns:
            Registered device or None if failed
        """
        # Generate fingerprint hash
        fingerprint.fingerprint_hash = self._generate_fingerprint_hash(fingerprint)

        # Check for existing device with same fingerprint
        for device in self._devices.values():
            if device.device_fingerprint.fingerprint_hash == fingerprint.fingerprint_hash:
                # Update existing device
                device.badge_number = badge_number
                device.officer_id = officer_id
                device.push_token = push_token
                device.status = DeviceStatus.ACTIVE
                device.last_active = datetime.utcnow()
                return device

        # Create new device
        device = RegisteredDevice(
            badge_number=badge_number,
            officer_id=officer_id,
            device_fingerprint=fingerprint,
            device_token=self._generate_token(),
            push_token=push_token,
            status=DeviceStatus.ACTIVE,
        )

        self._devices[device.id] = device
        return device

    async def authenticate(
        self,
        badge_number: str,
        password: str,
        device_id: str,
        ip_address: str | None = None,
    ) -> MobileSession | None:
        """
        Authenticate officer and create session.

        Args:
            badge_number: Officer badge number
            password: Officer password (placeholder - would integrate with auth system)
            device_id: Registered device ID
            ip_address: Request IP address

        Returns:
            Mobile session or None if failed
        """
        # Find device
        device = self._devices.get(device_id)
        if not device:
            return None

        # Check if device is locked
        if device.locked_until and datetime.utcnow() < device.locked_until:
            return None

        # Check device status
        if device.status != DeviceStatus.ACTIVE:
            return None

        # Verify badge matches device
        if device.badge_number != badge_number:
            device.failed_attempts += 1
            if device.failed_attempts >= self._max_failed_attempts:
                device.locked_until = datetime.utcnow() + timedelta(minutes=self._lockout_minutes)
            return None

        # Reset failed attempts on success
        device.failed_attempts = 0
        device.locked_until = None
        device.last_active = datetime.utcnow()
        device.last_ip = ip_address

        # Create session
        session = MobileSession(
            device_id=device_id,
            badge_number=badge_number,
            officer_id=device.officer_id,
            access_token=self._generate_token(),
            refresh_token=self._generate_token(),
            expires_at=datetime.utcnow() + timedelta(hours=self._token_expiry_hours),
            ip_address=ip_address,
        )

        self._sessions[session.id] = session
        return session

    async def validate_token(self, access_token: str) -> MobileSession | None:
        """
        Validate access token and return session.

        Args:
            access_token: Access token to validate

        Returns:
            Session if valid, None otherwise
        """
        for session in self._sessions.values():
            if session.access_token == access_token:
                if not session.is_active:
                    return None
                if datetime.utcnow() > session.expires_at:
                    session.is_active = False
                    return None
                session.last_activity = datetime.utcnow()
                return session
        return None

    async def refresh_session(self, refresh_token: str) -> MobileSession | None:
        """
        Refresh session using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New session or None if failed
        """
        for session in self._sessions.values():
            if session.refresh_token == refresh_token and session.is_active:
                # Invalidate old session
                session.is_active = False

                # Create new session
                new_session = MobileSession(
                    device_id=session.device_id,
                    badge_number=session.badge_number,
                    officer_id=session.officer_id,
                    access_token=self._generate_token(),
                    refresh_token=self._generate_token(),
                    expires_at=datetime.utcnow() + timedelta(hours=self._token_expiry_hours),
                    ip_address=session.ip_address,
                )

                self._sessions[new_session.id] = new_session
                return new_session
        return None

    async def logout(self, session_id: str) -> bool:
        """
        Logout and invalidate session.

        Args:
            session_id: Session ID to invalidate

        Returns:
            True if successful
        """
        session = self._sessions.get(session_id)
        if session:
            session.is_active = False
            return True
        return False

    async def create_alert(
        self,
        alert_type: AlertType,
        priority: AlertPriority,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
        target_badges: list[str] | None = None,
        target_units: list[str] | None = None,
        target_all: bool = False,
        geo_fence: dict[str, Any] | None = None,
        expires_hours: int | None = None,
    ) -> MobileAlert:
        """
        Create a new mobile alert.

        Args:
            alert_type: Type of alert
            priority: Alert priority
            title: Alert title
            body: Alert body
            data: Additional data
            target_badges: Target badge numbers
            target_units: Target unit IDs
            target_all: Send to all officers
            geo_fence: Geographic fence for targeting
            expires_hours: Hours until expiration

        Returns:
            Created alert
        """
        alert = MobileAlert(
            alert_type=alert_type,
            priority=priority,
            title=title,
            body=body,
            data=data or {},
            target_badges=target_badges or [],
            target_units=target_units or [],
            target_all=target_all,
            geo_fence=geo_fence,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours) if expires_hours else None,
        )

        self._alerts[alert.id] = alert
        return alert

    async def get_alerts(
        self,
        badge_number: str,
        unit_id: str | None = None,
        limit: int = 50,
        include_read: bool = False,
    ) -> list[MobileAlert]:
        """
        Get alerts for an officer.

        Args:
            badge_number: Officer badge number
            unit_id: Unit ID
            limit: Maximum alerts to return
            include_read: Include already read alerts

        Returns:
            List of alerts
        """
        now = datetime.utcnow()
        alerts = []

        for alert in sorted(self._alerts.values(), key=lambda a: a.created_at, reverse=True):
            # Check expiration
            if alert.expires_at and now > alert.expires_at:
                continue

            # Check if already read
            if not include_read and badge_number in alert.read_by:
                continue

            # Check targeting
            if alert.target_all:
                alerts.append(alert)
            elif badge_number in alert.target_badges:
                alerts.append(alert)
            elif unit_id and unit_id in alert.target_units:
                alerts.append(alert)

            if len(alerts) >= limit:
                break

        return alerts

    async def mark_alert_read(self, alert_id: str, badge_number: str) -> bool:
        """Mark an alert as read."""
        alert = self._alerts.get(alert_id)
        if alert and badge_number not in alert.read_by:
            alert.read_by.append(badge_number)
            return True
        return False

    async def acknowledge_alert(self, alert_id: str, badge_number: str) -> bool:
        """Acknowledge an alert."""
        alert = self._alerts.get(alert_id)
        if alert and badge_number not in alert.acknowledged_by:
            alert.acknowledged_by.append(badge_number)
            if badge_number not in alert.read_by:
                alert.read_by.append(badge_number)
            return True
        return False

    async def add_dispatch_call(self, call: DispatchCall) -> DispatchCall:
        """Add or update a dispatch call."""
        self._dispatch_calls[call.id] = call
        return call

    async def get_active_dispatch(
        self,
        badge_number: str | None = None,
        unit_id: str | None = None,
    ) -> list[DispatchCall]:
        """
        Get active dispatch calls.

        Args:
            badge_number: Filter by assigned badge
            unit_id: Filter by assigned unit

        Returns:
            List of active dispatch calls
        """
        calls = []
        for call in self._dispatch_calls.values():
            if call.status in ["closed", "cancelled"]:
                continue
            if unit_id and unit_id not in call.assigned_units:
                continue
            calls.append(call)
        return sorted(calls, key=lambda c: (c.priority, c.created_at))

    async def send_message(
        self,
        sender_badge: str,
        sender_name: str,
        content: str,
        recipient_badges: list[str] | None = None,
        recipient_units: list[str] | None = None,
        channel: str | None = None,
        priority: AlertPriority = AlertPriority.MEDIUM,
        attachments: list[str] | None = None,
        is_rtcc: bool = False,
    ) -> MobileMessage:
        """
        Send a mobile message.

        Args:
            sender_badge: Sender badge number
            sender_name: Sender name
            content: Message content
            recipient_badges: Recipient badge numbers
            recipient_units: Recipient unit IDs
            channel: Channel name
            priority: Message priority
            attachments: Attachment URLs
            is_rtcc: Is from RTCC

        Returns:
            Created message
        """
        message = MobileMessage(
            sender_badge=sender_badge,
            sender_name=sender_name,
            content=content,
            recipient_badges=recipient_badges or [],
            recipient_units=recipient_units or [],
            channel=channel,
            priority=priority,
            attachments=attachments or [],
            is_rtcc=is_rtcc,
        )

        self._messages[message.id] = message
        return message

    async def get_messages(
        self,
        badge_number: str,
        unit_id: str | None = None,
        channel: str | None = None,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[MobileMessage]:
        """
        Get messages for an officer.

        Args:
            badge_number: Officer badge number
            unit_id: Unit ID
            channel: Filter by channel
            limit: Maximum messages
            since: Only messages after this time

        Returns:
            List of messages
        """
        messages = []

        for msg in sorted(self._messages.values(), key=lambda m: m.created_at, reverse=True):
            if since and msg.created_at < since:
                continue

            if channel and msg.channel != channel:
                continue

            # Check if officer should see message
            if (
                badge_number in msg.recipient_badges
                or msg.sender_badge == badge_number
                or (unit_id and unit_id in msg.recipient_units)
                or (msg.channel and not msg.recipient_badges and not msg.recipient_units)
            ):
                messages.append(msg)

            if len(messages) >= limit:
                break

        return messages

    async def update_unit_status(
        self,
        badge_number: str,
        unit_id: str,
        status: UnitStatus,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        call_id: str | None = None,
        notes: str | None = None,
    ) -> UnitStatusUpdate:
        """
        Update unit status.

        Args:
            badge_number: Officer badge number
            unit_id: Unit ID
            status: New status
            location: Location description
            latitude: GPS latitude
            longitude: GPS longitude
            call_id: Associated call ID
            notes: Status notes

        Returns:
            Status update
        """
        update = UnitStatusUpdate(
            badge_number=badge_number,
            unit_id=unit_id,
            status=status,
            location=location,
            latitude=latitude,
            longitude=longitude,
            call_id=call_id,
            notes=notes,
        )

        self._unit_statuses[badge_number] = update
        return update

    async def get_unit_status(self, badge_number: str) -> UnitStatusUpdate | None:
        """Get unit status for a badge."""
        return self._unit_statuses.get(badge_number)

    async def add_intel_item(self, item: IntelFeedItem) -> IntelFeedItem:
        """Add an intelligence feed item."""
        self._intel_feed[item.id] = item
        return item

    async def get_intel_feed(
        self,
        badge_number: str,
        limit: int = 50,
        intel_type: str | None = None,
        since: datetime | None = None,
    ) -> list[IntelFeedItem]:
        """
        Get intelligence feed items.

        Args:
            badge_number: Officer badge number
            limit: Maximum items
            intel_type: Filter by type
            since: Only items after this time

        Returns:
            List of intel items
        """
        now = datetime.utcnow()
        items = []

        for item in sorted(self._intel_feed.values(), key=lambda i: i.created_at, reverse=True):
            if item.expires_at and now > item.expires_at:
                continue
            if intel_type and item.intel_type != intel_type:
                continue
            if since and item.created_at < since:
                continue

            items.append(item)
            if len(items) >= limit:
                break

        return items

    async def subscribe_events(
        self,
        badge_number: str,
        event_types: list[str],
    ) -> str:
        """
        Subscribe to event types.

        Args:
            badge_number: Officer badge number
            event_types: Event types to subscribe to

        Returns:
            Subscription ID
        """
        sub_id = str(uuid.uuid4())
        self._event_subscribers[sub_id] = event_types
        return sub_id

    async def unsubscribe_events(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        if subscription_id in self._event_subscribers:
            del self._event_subscribers[subscription_id]
            return True
        return False

    async def get_device(self, device_id: str) -> RegisteredDevice | None:
        """Get a registered device."""
        return self._devices.get(device_id)

    async def get_devices_for_badge(self, badge_number: str) -> list[RegisteredDevice]:
        """Get all devices for a badge number."""
        return [d for d in self._devices.values() if d.badge_number == badge_number]

    async def revoke_device(self, device_id: str) -> bool:
        """Revoke a device registration."""
        device = self._devices.get(device_id)
        if device:
            device.status = DeviceStatus.REVOKED
            # Invalidate all sessions for this device
            for session in self._sessions.values():
                if session.device_id == device_id:
                    session.is_active = False
            return True
        return False

    async def get_active_sessions(self, badge_number: str) -> list[MobileSession]:
        """Get active sessions for a badge."""
        return [
            s for s in self._sessions.values()
            if s.badge_number == badge_number and s.is_active
        ]


# Global instance
mobile_gateway = MobileGatewayManager()
