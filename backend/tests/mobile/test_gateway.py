"""
G3TI RTCC-UIP Mobile Gateway Tests
Tests for the Officer Mobile API Gateway module
"""

from datetime import datetime, timedelta

import pytest

from app.mobile import (
    AlertPriority,
    AlertType,
    DeviceFingerprint,
    DeviceStatus,
    DeviceType,
    MobileGatewayManager,
    UnitStatus,
)


class TestMobileGatewayManager:
    """Tests for MobileGatewayManager"""

    @pytest.fixture
    def manager(self):
        """Create a fresh manager instance for each test"""
        return MobileGatewayManager()

    @pytest.fixture
    def sample_fingerprint(self):
        """Sample device fingerprint"""
        return DeviceFingerprint(
            device_id="test-device-001",
            platform="ios",
            os_version="17.0",
            app_version="1.0.0",
            hardware_id="hw-12345",
        )

    def test_register_device(self, manager, sample_fingerprint):
        """Test device registration"""
        device = manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )

        assert device is not None
        assert device.badge_number == "1234"
        assert device.officer_name == "Officer Smith"
        assert device.device_type == DeviceType.SMARTPHONE
        assert device.status == DeviceStatus.ACTIVE
        assert device.fingerprint == sample_fingerprint

    def test_authenticate_success(self, manager, sample_fingerprint):
        """Test successful authentication"""
        # Register device first
        manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )

        # Authenticate
        session = manager.authenticate(
            badge_number="1234",
            password="test_password",
            device_id=sample_fingerprint.device_id,
        )

        assert session is not None
        assert session.badge_number == "1234"
        assert session.access_token is not None
        assert session.refresh_token is not None
        assert session.is_active is True

    def test_authenticate_unregistered_device(self, manager):
        """Test authentication with unregistered device"""
        session = manager.authenticate(
            badge_number="1234",
            password="test_password",
            device_id="unknown-device",
        )

        assert session is None

    def test_validate_token(self, manager, sample_fingerprint):
        """Test token validation"""
        # Register and authenticate
        manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )
        session = manager.authenticate(
            badge_number="1234",
            password="test_password",
            device_id=sample_fingerprint.device_id,
        )

        # Validate token
        is_valid = manager.validate_token(
            session.access_token,
            sample_fingerprint.device_id,
        )

        assert is_valid is True

    def test_validate_expired_token(self, manager, sample_fingerprint):
        """Test validation of expired token"""
        # Register and authenticate
        manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )
        session = manager.authenticate(
            badge_number="1234",
            password="test_password",
            device_id=sample_fingerprint.device_id,
        )

        # Manually expire the session
        session.expires_at = datetime.utcnow() - timedelta(hours=1)

        # Validate token
        is_valid = manager.validate_token(
            session.access_token,
            sample_fingerprint.device_id,
        )

        assert is_valid is False

    def test_refresh_session(self, manager, sample_fingerprint):
        """Test session refresh"""
        # Register and authenticate
        manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )
        session = manager.authenticate(
            badge_number="1234",
            password="test_password",
            device_id=sample_fingerprint.device_id,
        )

        old_token = session.access_token

        # Refresh session
        new_session = manager.refresh_session(
            session.refresh_token,
            sample_fingerprint.device_id,
        )

        assert new_session is not None
        assert new_session.access_token != old_token

    def test_logout(self, manager, sample_fingerprint):
        """Test logout"""
        # Register and authenticate
        manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )
        session = manager.authenticate(
            badge_number="1234",
            password="test_password",
            device_id=sample_fingerprint.device_id,
        )

        # Logout
        result = manager.logout(session.access_token)

        assert result is True

        # Token should no longer be valid
        is_valid = manager.validate_token(
            session.access_token,
            sample_fingerprint.device_id,
        )
        assert is_valid is False

    def test_create_alert(self, manager):
        """Test alert creation"""
        alert = manager.create_alert(
            badge_number="1234",
            title="Test Alert",
            body="This is a test alert",
            priority=AlertPriority.HIGH,
            alert_type=AlertType.DISPATCH,
        )

        assert alert is not None
        assert alert.title == "Test Alert"
        assert alert.priority == AlertPriority.HIGH
        assert alert.alert_type == AlertType.DISPATCH
        assert alert.read is False
        assert alert.acknowledged is False

    def test_get_alerts(self, manager):
        """Test getting alerts for a badge"""
        # Create multiple alerts
        manager.create_alert(
            badge_number="1234",
            title="Alert 1",
            body="Body 1",
            priority=AlertPriority.HIGH,
            alert_type=AlertType.DISPATCH,
        )
        manager.create_alert(
            badge_number="1234",
            title="Alert 2",
            body="Body 2",
            priority=AlertPriority.MEDIUM,
            alert_type=AlertType.SAFETY,
        )
        manager.create_alert(
            badge_number="5678",
            title="Alert 3",
            body="Body 3",
            priority=AlertPriority.LOW,
            alert_type=AlertType.MESSAGE,
        )

        # Get alerts for badge 1234
        alerts = manager.get_alerts("1234")

        assert len(alerts) == 2
        assert all(a.badge_number == "1234" for a in alerts)

    def test_mark_alert_read(self, manager):
        """Test marking alert as read"""
        alert = manager.create_alert(
            badge_number="1234",
            title="Test Alert",
            body="Body",
            priority=AlertPriority.HIGH,
            alert_type=AlertType.DISPATCH,
        )

        result = manager.mark_alert_read(alert.id, "1234")

        assert result is True
        assert alert.read is True

    def test_acknowledge_alert(self, manager):
        """Test acknowledging alert"""
        alert = manager.create_alert(
            badge_number="1234",
            title="Test Alert",
            body="Body",
            priority=AlertPriority.HIGH,
            alert_type=AlertType.DISPATCH,
        )

        result = manager.acknowledge_alert(alert.id, "1234")

        assert result is True
        assert alert.acknowledged is True
        assert alert.acknowledged_at is not None

    def test_send_message(self, manager):
        """Test sending a message"""
        message = manager.send_message(
            sender_badge="1234",
            sender_name="Officer Smith",
            content="Test message",
            recipient_badge="5678",
        )

        assert message is not None
        assert message.sender_badge == "1234"
        assert message.content == "Test message"
        assert message.recipient_badge == "5678"

    def test_get_messages(self, manager):
        """Test getting messages"""
        # Send messages
        manager.send_message(
            sender_badge="1234",
            sender_name="Officer Smith",
            content="Message 1",
            recipient_badge="5678",
        )
        manager.send_message(
            sender_badge="5678",
            sender_name="Officer Jones",
            content="Message 2",
            recipient_badge="1234",
        )

        # Get messages for badge 1234
        messages = manager.get_messages("1234")

        assert len(messages) == 2

    def test_update_unit_status(self, manager):
        """Test updating unit status"""
        status_update = manager.update_unit_status(
            badge_number="1234",
            unit_id="A1",
            status=UnitStatus.EN_ROUTE,
        )

        assert status_update is not None
        assert status_update.badge_number == "1234"
        assert status_update.unit_id == "A1"
        assert status_update.status == UnitStatus.EN_ROUTE

    def test_get_unit_status(self, manager):
        """Test getting unit status"""
        # Update status first
        manager.update_unit_status(
            badge_number="1234",
            unit_id="A1",
            status=UnitStatus.ON_SCENE,
        )

        # Get status
        status = manager.get_unit_status("1234")

        assert status is not None
        assert status.status == UnitStatus.ON_SCENE

    def test_rate_limiting(self, manager, sample_fingerprint):
        """Test rate limiting"""
        # Register device
        manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )

        # Check rate limit
        is_allowed = manager.check_rate_limit(sample_fingerprint.device_id)
        assert is_allowed is True

    def test_revoke_device(self, manager, sample_fingerprint):
        """Test device revocation"""
        # Register device
        device = manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )

        # Revoke device
        result = manager.revoke_device(device.id)

        assert result is True
        assert device.status == DeviceStatus.REVOKED

    def test_get_devices_for_badge(self, manager, sample_fingerprint):
        """Test getting devices for a badge"""
        # Register multiple devices
        manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=sample_fingerprint,
            device_type=DeviceType.SMARTPHONE,
        )

        fingerprint2 = DeviceFingerprint(
            device_id="test-device-002",
            platform="android",
            os_version="14.0",
            app_version="1.0.0",
            hardware_id="hw-67890",
        )
        manager.register_device(
            badge_number="1234",
            officer_name="Officer Smith",
            fingerprint=fingerprint2,
            device_type=DeviceType.TABLET,
        )

        # Get devices
        devices = manager.get_devices_for_badge("1234")

        assert len(devices) == 2
        assert all(d.badge_number == "1234" for d in devices)
