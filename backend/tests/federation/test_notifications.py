"""
Tests for Multi-Agency Notification Engine
Phase 10: Notifications, BOLOs, and bulletins tests
"""

from datetime import datetime

from app.federation.notifications import (
    BOLOBroadcast,
    DeliveryChannel,
    MultiAgencyNotification,
    MultiAgencyNotificationEngine,
    NotificationPriority,
    NotificationType,
)


class TestMultiAgencyNotification:
    """Tests for MultiAgencyNotification"""

    def test_create_notification(self):
        """Test creating notification"""
        notification = MultiAgencyNotification(
            notification_type=NotificationType.OFFICER_SAFETY,
            priority=NotificationPriority.CRITICAL,
            title="Officer Safety Alert",
            content="Armed suspect in area",
            sender_agency="local_pd",
            sender_user="dispatcher_1",
            target_agencies=["sheriff", "state_police"],
        )

        assert notification.notification_type == NotificationType.OFFICER_SAFETY
        assert notification.priority == NotificationPriority.CRITICAL
        assert len(notification.target_agencies) == 2

    def test_notification_has_id(self):
        """Test notification has unique ID"""
        notif1 = MultiAgencyNotification(
            notification_type=NotificationType.GENERAL_BROADCAST,
            priority=NotificationPriority.LOW,
            title="Test 1",
            content="Content 1",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2"],
        )
        notif2 = MultiAgencyNotification(
            notification_type=NotificationType.GENERAL_BROADCAST,
            priority=NotificationPriority.LOW,
            title="Test 2",
            content="Content 2",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2"],
        )

        assert notif1.id != notif2.id


class TestBOLOBroadcast:
    """Tests for BOLOBroadcast"""

    def test_create_bolo(self):
        """Test creating BOLO"""
        bolo = BOLOBroadcast(
            bolo_type="wanted_person",
            priority=NotificationPriority.CRITICAL,
            title="Wanted - Armed Robbery Suspect",
            description="Male, 30s, armed with handgun",
            sender_agency="local_pd",
            sender_user="detective_1",
            target_agencies=["all"],
            armed_dangerous=True,
            case_number="2024-12345",
        )

        assert bolo.bolo_type == "wanted_person"
        assert bolo.armed_dangerous is True
        assert bolo.is_active is True

    def test_bolo_with_vehicle_description(self):
        """Test BOLO with vehicle description"""
        bolo = BOLOBroadcast(
            bolo_type="stolen_vehicle",
            priority=NotificationPriority.HIGH,
            title="Stolen Vehicle",
            description="Blue Honda Accord",
            sender_agency="local_pd",
            sender_user="officer_1",
            target_agencies=["sheriff", "highway_patrol"],
            vehicle_description={
                "make": "Honda",
                "model": "Accord",
                "color": "Blue",
                "plate": "ABC1234",
            },
        )

        assert bolo.vehicle_description is not None
        assert bolo.vehicle_description["make"] == "Honda"


class TestMultiAgencyNotificationEngine:
    """Tests for MultiAgencyNotificationEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = MultiAgencyNotificationEngine()

    def test_send_notification(self):
        """Test sending notification"""
        notification = self.engine.send_notification(
            notification_type=NotificationType.INCIDENT_UPDATE,
            priority=NotificationPriority.MEDIUM,
            title="Incident Update",
            content="Highway closure due to accident",
            sender_agency="highway_patrol",
            sender_user="dispatcher_1",
            target_agencies=["local_pd", "sheriff"],
        )

        assert notification is not None
        assert notification.id in self.engine.notifications

    def test_broadcast_bolo(self):
        """Test broadcasting BOLO"""
        bolo = self.engine.broadcast_bolo(
            bolo_type="missing_person",
            priority=NotificationPriority.HIGH,
            title="Missing Person",
            description="Elderly male with dementia",
            sender_agency="local_pd",
            sender_user="officer_1",
            target_agencies=["all_agencies"],
        )

        assert bolo is not None
        assert bolo.id in self.engine.bolos
        assert bolo.is_active is True

    def test_cancel_bolo(self):
        """Test cancelling BOLO"""
        bolo = self.engine.broadcast_bolo(
            bolo_type="wanted_person",
            priority=NotificationPriority.HIGH,
            title="Wanted Person",
            description="Test description",
            sender_agency="local_pd",
            sender_user="officer_1",
            target_agencies=["all"],
        )

        cancelled = self.engine.cancel_bolo(
            bolo_id=bolo.id,
            cancelled_by="supervisor_1",
            cancel_reason="Suspect apprehended",
        )

        assert cancelled is not None
        assert cancelled.is_active is False
        assert cancelled.cancel_reason == "Suspect apprehended"

    def test_send_bulletin(self):
        """Test sending secure bulletin"""
        bulletin = self.engine.send_bulletin(
            bulletin_type="intelligence",
            classification="law_enforcement_sensitive",
            title="Gang Activity Update",
            content="Increased gang activity in downtown area",
            sender_agency="fusion_center",
            sender_user="analyst_1",
            target_agencies=["local_pd", "sheriff"],
            effective_date=datetime.utcnow(),
        )

        assert bulletin is not None
        assert bulletin.id in self.engine.bulletins

    def test_acknowledge_bulletin(self):
        """Test acknowledging bulletin"""
        bulletin = self.engine.send_bulletin(
            bulletin_type="intelligence",
            classification="unclassified",
            title="Test Bulletin",
            content="Test content",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2"],
            effective_date=datetime.utcnow(),
        )

        result = self.engine.acknowledge_bulletin(
            bulletin_id=bulletin.id,
            agency="agency-2",
            user="user-2",
        )

        assert result is True
        assert len(bulletin.acknowledgments) == 1

    def test_get_notifications_for_agency(self):
        """Test getting notifications for specific agency"""
        self.engine.send_notification(
            notification_type=NotificationType.GENERAL_BROADCAST,
            priority=NotificationPriority.LOW,
            title="Test 1",
            content="Content 1",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2", "agency-3"],
        )
        self.engine.send_notification(
            notification_type=NotificationType.GENERAL_BROADCAST,
            priority=NotificationPriority.LOW,
            title="Test 2",
            content="Content 2",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2"],
        )

        agency_2_notifs = self.engine.get_notifications_for_agency("agency-2")
        agency_3_notifs = self.engine.get_notifications_for_agency("agency-3")

        assert len(agency_2_notifs) == 2
        assert len(agency_3_notifs) == 1

    def test_get_active_bolos(self):
        """Test getting active BOLOs"""
        self.engine.broadcast_bolo(
            bolo_type="wanted_person",
            priority=NotificationPriority.HIGH,
            title="Active BOLO 1",
            description="Description 1",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2"],
        )
        bolo2 = self.engine.broadcast_bolo(
            bolo_type="wanted_person",
            priority=NotificationPriority.HIGH,
            title="Active BOLO 2",
            description="Description 2",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2"],
        )
        self.engine.cancel_bolo(bolo2.id, "user-1", "Cancelled")

        active_bolos = self.engine.get_active_bolos()
        assert len(active_bolos) == 1

    def test_acknowledge_notification(self):
        """Test acknowledging notification"""
        notification = self.engine.send_notification(
            notification_type=NotificationType.OFFICER_SAFETY,
            priority=NotificationPriority.CRITICAL,
            title="Safety Alert",
            content="Alert content",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2"],
            requires_acknowledgment=True,
        )

        result = self.engine.acknowledge_notification(
            notification_id=notification.id,
            agency="agency-2",
            user="user-2",
        )

        assert result is True

    def test_create_notification_rule(self):
        """Test creating notification rule"""
        rule = self.engine.create_notification_rule(
            name="High Priority Incidents",
            description="Auto-notify on high priority incidents",
            trigger_type="incident_created",
            trigger_conditions={"priority": "high"},
            notification_type=NotificationType.INCIDENT_UPDATE,
            priority=NotificationPriority.HIGH,
            target_agencies=["all"],
            target_roles=["supervisor", "commander"],
            channels=[DeliveryChannel.WEBSOCKET, DeliveryChannel.PUSH],
        )

        assert rule is not None
        assert rule.id in self.engine.rules

    def test_get_delivery_stats(self):
        """Test getting delivery statistics"""
        self.engine.send_notification(
            notification_type=NotificationType.GENERAL_BROADCAST,
            priority=NotificationPriority.LOW,
            title="Test",
            content="Content",
            sender_agency="agency-1",
            sender_user="user-1",
            target_agencies=["agency-2"],
        )

        stats = self.engine.get_delivery_stats()
        assert "total" in stats
        assert "by_status" in stats
        assert "by_channel" in stats
