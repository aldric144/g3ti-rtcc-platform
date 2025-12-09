"""Tests for the Push Alerts module."""


import pytest

from app.comms.alerts import (
    AlertPriority,
    AlertsManager,
    AlertStatus,
    AlertTemplate,
    AlertType,
    PushAlert,
    send_push_notification,
)


@pytest.fixture
def alerts_manager():
    """Create an alerts manager instance."""
    return AlertsManager()


class TestAlertsManager:
    """Tests for AlertsManager."""

    @pytest.mark.asyncio
    async def test_create_alert(self, alerts_manager):
        """Test creating an alert."""
        alert = await alerts_manager.create_alert(
            alert_type=AlertType.OFFICER_SAFETY,
            title="Officer Safety Alert",
            body="High-risk individual in vicinity",
            priority=AlertPriority.URGENT,
            target_badges=["A1101", "A1201"],
        )

        assert alert is not None
        assert alert.alert_type == AlertType.OFFICER_SAFETY
        assert alert.priority == AlertPriority.URGENT
        assert alert.audit_id is not None

    @pytest.mark.asyncio
    async def test_create_alert_with_location(self, alerts_manager):
        """Test creating an alert with location."""
        alert = await alerts_manager.create_alert(
            alert_type=AlertType.GUNFIRE,
            title="Gunfire Detected",
            body="3 rounds detected",
            priority=AlertPriority.CRITICAL,
            latitude=33.7490,
            longitude=-84.3880,
            address="123 Main St",
            radius_meters=500,
        )

        assert alert.latitude == 33.7490
        assert alert.longitude == -84.3880
        assert alert.address == "123 Main St"

    @pytest.mark.asyncio
    async def test_create_alert_broadcast(self, alerts_manager):
        """Test creating a broadcast alert."""
        alert = await alerts_manager.create_alert(
            alert_type=AlertType.AMBUSH_WARNING,
            title="AMBUSH WARNING",
            body="Potential ambush detected",
            priority=AlertPriority.CRITICAL,
            broadcast_all=True,
        )

        assert alert.broadcast_all is True

    @pytest.mark.asyncio
    async def test_create_alert_from_template(self, alerts_manager):
        """Test creating an alert from a template."""
        # Get the gunfire template
        template = alerts_manager.get_template("gunfire")
        assert template is not None

        alert = await alerts_manager.create_alert_from_template(
            template_id="gunfire",
            variables={
                "rounds": 5,
                "address": "456 Oak Ave",
                "distance": 200,
            },
            target_badges=["B2101"],
        )

        assert alert is not None
        assert "5" in alert.body or "rounds" in alert.body.lower()

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, alerts_manager):
        """Test acknowledging an alert."""
        alert = await alerts_manager.create_alert(
            alert_type=AlertType.BOLO,
            title="BOLO Alert",
            body="Suspect vehicle spotted",
            priority=AlertPriority.HIGH,
            requires_acknowledgment=True,
        )

        updated_alert = await alerts_manager.acknowledge_alert(
            alert_id=alert.id,
            badge="A1101",
        )

        assert "A1101" in updated_alert.acknowledged_by

    @pytest.mark.asyncio
    async def test_get_alerts_for_badge(self, alerts_manager):
        """Test getting alerts for a specific badge."""
        # Create some alerts
        await alerts_manager.create_alert(
            alert_type=AlertType.OFFICER_SAFETY,
            title="Alert 1",
            body="Body 1",
            target_badges=["A1101"],
        )
        await alerts_manager.create_alert(
            alert_type=AlertType.OFFICER_SAFETY,
            title="Alert 2",
            body="Body 2",
            target_badges=["A1101", "A1201"],
        )

        alerts = await alerts_manager.get_alerts_for_badge("A1101")

        assert len(alerts) >= 2

    @pytest.mark.asyncio
    async def test_get_recent_alerts(self, alerts_manager):
        """Test getting recent alerts."""
        # Create some alerts
        for i in range(5):
            await alerts_manager.create_alert(
                alert_type=AlertType.SYSTEM,
                title=f"Alert {i}",
                body=f"Body {i}",
            )

        alerts = await alerts_manager.get_recent_alerts(limit=3)

        assert len(alerts) <= 3

    @pytest.mark.asyncio
    async def test_mark_alert_read(self, alerts_manager):
        """Test marking an alert as read."""
        alert = await alerts_manager.create_alert(
            alert_type=AlertType.BULLETIN,
            title="Bulletin Alert",
            body="New bulletin available",
        )

        updated_alert = await alerts_manager.mark_alert_read(
            alert_id=alert.id,
            badge="A1101",
        )

        assert updated_alert.status == AlertStatus.READ

    @pytest.mark.asyncio
    async def test_get_all_templates(self, alerts_manager):
        """Test getting all alert templates."""
        templates = alerts_manager.get_all_templates()

        assert len(templates) > 0
        assert any(t.id == "gunfire" for t in templates)
        assert any(t.id == "officer_safety" for t in templates)


class TestPushAlertModel:
    """Tests for PushAlert model."""

    def test_push_alert_creation(self):
        """Test creating a push alert."""
        alert = PushAlert(
            alert_type=AlertType.OFFICER_SAFETY,
            title="Test Alert",
            body="Test body",
            priority=AlertPriority.HIGH,
        )

        assert alert.id is not None
        assert alert.status == AlertStatus.PENDING
        assert alert.audit_id is not None

    def test_push_alert_with_targeting(self):
        """Test push alert with targeting."""
        alert = PushAlert(
            alert_type=AlertType.TACTICAL_SURGE,
            title="Tactical Alert",
            body="Surge requested",
            priority=AlertPriority.URGENT,
            target_badges=["A1101", "A1201"],
            target_shifts=["A"],
            target_districts=["Central"],
        )

        assert len(alert.target_badges) == 2
        assert "A" in alert.target_shifts
        assert "Central" in alert.target_districts


class TestAlertTemplateModel:
    """Tests for AlertTemplate model."""

    def test_alert_template_creation(self):
        """Test creating an alert template."""
        template = AlertTemplate(
            id="test_template",
            name="Test Template",
            alert_type=AlertType.SYSTEM,
            title_template="Test: {subject}",
            body_template="Details: {details}",
        )

        assert template.id == "test_template"
        assert template.is_active is True


class TestSendPushNotification:
    """Tests for send_push_notification function."""

    @pytest.mark.asyncio
    async def test_send_push_notification(self):
        """Test sending a push notification."""
        result = await send_push_notification(
            badge="A1101",
            title="Test Notification",
            body="This is a test",
            priority="high",
        )

        assert result is True
