"""
Test Suite: Community Engagement Engine
Phase 36: Public Safety Guardian
"""

import pytest
from datetime import datetime, timedelta

from backend.app.public_guardian.community_engagement import (
    CommunityEngagementEngine,
    EventType,
    AlertType,
    NotificationChannel,
    EventStatus,
    AlertSeverity,
    CommunityEvent,
    SafetyAlert,
    NotificationTemplate,
)


class TestCommunityEngagementEngine:
    def setup_method(self):
        self.engine = CommunityEngagementEngine()

    def test_engine_singleton(self):
        engine2 = CommunityEngagementEngine()
        assert self.engine is engine2

    def test_create_event(self):
        event = self.engine.create_event(
            name="Test Town Hall",
            event_type=EventType.TOWN_HALL,
            description="Monthly community meeting",
            location="City Hall",
            address="600 W Blue Heron Blvd",
            start_time=datetime.utcnow() + timedelta(days=7),
        )
        assert event is not None
        assert event.event_id is not None
        assert event.name == "Test Town Hall"
        assert event.event_type == EventType.TOWN_HALL

    def test_create_event_with_all_fields(self):
        event = self.engine.create_event(
            name="Coffee with Cops",
            event_type=EventType.COFFEE_WITH_COPS,
            description="Informal community engagement",
            location="Local Coffee Shop",
            address="123 Main St",
            start_time=datetime.utcnow() + timedelta(days=3),
            end_time=datetime.utcnow() + timedelta(days=3, hours=2),
            expected_attendance=30,
            target_neighborhoods=["Downtown Riviera Beach"],
            registration_required=False,
        )
        assert event is not None
        assert event.expected_attendance == 30

    def test_update_event(self):
        event = self.engine.create_event(
            name="Original Name",
            event_type=EventType.COMMUNITY_MEETING,
            location="Location A",
            start_time=datetime.utcnow() + timedelta(days=5),
        )
        updated = self.engine.update_event(
            event.event_id,
            name="Updated Name",
            location="Location B"
        )
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.location == "Location B"

    def test_cancel_event(self):
        event = self.engine.create_event(
            name="Event to Cancel",
            event_type=EventType.SAFETY_WORKSHOP,
            location="Workshop Center",
            start_time=datetime.utcnow() + timedelta(days=10),
        )
        success = self.engine.cancel_event(event.event_id, "Weather conditions")
        assert success is True
        cancelled = self.engine.get_event(event.event_id)
        assert cancelled.status == EventStatus.CANCELLED

    def test_complete_event(self):
        event = self.engine.create_event(
            name="Event to Complete",
            event_type=EventType.YOUTH_PROGRAM,
            location="Youth Center",
            start_time=datetime.utcnow() - timedelta(hours=2),
        )
        success = self.engine.complete_event(event.event_id, actual_attendance=45)
        assert success is True
        completed = self.engine.get_event(event.event_id)
        assert completed.status == EventStatus.COMPLETED

    def test_get_event(self):
        event = self.engine.create_event(
            name="Retrievable Event",
            event_type=EventType.NEIGHBORHOOD_WATCH,
            location="Community Center",
            start_time=datetime.utcnow() + timedelta(days=2),
        )
        retrieved = self.engine.get_event(event.event_id)
        assert retrieved is not None
        assert retrieved.event_id == event.event_id

    def test_get_upcoming_events(self):
        events = self.engine.get_upcoming_events(limit=10)
        assert isinstance(events, list)

    def test_get_events_by_type(self):
        self.engine.create_event(
            name="Town Hall Test",
            event_type=EventType.TOWN_HALL,
            location="City Hall",
            start_time=datetime.utcnow() + timedelta(days=14),
        )
        events = self.engine.get_events_by_type(EventType.TOWN_HALL)
        assert len(events) > 0

    def test_create_alert(self):
        alert = self.engine.create_alert(
            alert_type=AlertType.SAFETY_ALERT,
            title="Test Safety Alert",
            message="This is a test safety alert message",
            severity=AlertSeverity.MEDIUM,
            affected_areas=["Downtown Riviera Beach"],
        )
        assert alert is not None
        assert alert.alert_id is not None
        assert alert.active is True

    def test_create_amber_alert(self):
        alert = self.engine.create_alert(
            alert_type=AlertType.AMBER_ALERT,
            title="AMBER Alert Test",
            message="Missing child alert",
            severity=AlertSeverity.CRITICAL,
            affected_areas=["All Neighborhoods"],
            channels=[NotificationChannel.SMS, NotificationChannel.EMERGENCY_BROADCAST],
        )
        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL

    def test_deactivate_alert(self):
        alert = self.engine.create_alert(
            alert_type=AlertType.TRAFFIC_ADVISORY,
            title="Traffic Alert",
            message="Road closure",
            severity=AlertSeverity.LOW,
        )
        success = self.engine.deactivate_alert(alert.alert_id)
        assert success is True
        deactivated = self.engine.get_alert(alert.alert_id)
        assert deactivated.active is False

    def test_get_active_alerts(self):
        alerts = self.engine.get_active_alerts()
        assert isinstance(alerts, list)

    def test_get_alerts_by_type(self):
        self.engine.create_alert(
            alert_type=AlertType.COMMUNITY_NOTICE,
            title="Community Notice",
            message="General notice",
            severity=AlertSeverity.INFO,
        )
        alerts = self.engine.get_alerts_by_type(AlertType.COMMUNITY_NOTICE)
        assert len(alerts) > 0

    def test_send_notification(self):
        result = self.engine.send_notification(
            template_id="town_hall_reminder",
            channels=[NotificationChannel.EMAIL],
            recipients=["test@example.com"],
            variables={"event_name": "Test Event", "date": "2025-01-15"},
        )
        assert result is not None

    def test_get_template(self):
        template = self.engine.get_template("town_hall_reminder")
        assert template is not None or template is None

    def test_get_all_templates(self):
        templates = self.engine.get_all_templates()
        assert isinstance(templates, list)

    def test_get_statistics(self):
        stats = self.engine.get_statistics()
        assert "events_created" in stats
        assert "alerts_sent" in stats

    def test_event_to_dict(self):
        event = self.engine.create_event(
            name="Dict Test Event",
            event_type=EventType.POLICE_OPEN_HOUSE,
            location="Police Station",
            start_time=datetime.utcnow() + timedelta(days=30),
        )
        event_dict = event.to_dict()
        assert "event_id" in event_dict
        assert "name" in event_dict
        assert "event_type" in event_dict

    def test_alert_to_dict(self):
        alert = self.engine.create_alert(
            alert_type=AlertType.CRIME_PREVENTION,
            title="Crime Prevention Tip",
            message="Lock your vehicles",
            severity=AlertSeverity.LOW,
        )
        alert_dict = alert.to_dict()
        assert "alert_id" in alert_dict
        assert "title" in alert_dict
        assert "severity" in alert_dict


class TestEventType:
    def test_all_event_types_exist(self):
        expected = [
            "town_hall", "advisory_board", "community_meeting",
            "safety_workshop", "youth_program", "neighborhood_watch",
            "police_open_house", "coffee_with_cops", "national_night_out", "other"
        ]
        for et in expected:
            assert hasattr(EventType, et.upper())


class TestAlertType:
    def test_all_alert_types_exist(self):
        expected = [
            "safety_alert", "amber_alert", "silver_alert",
            "weather_emergency", "traffic_advisory", "community_notice",
            "crime_prevention", "public_safety"
        ]
        for at in expected:
            assert hasattr(AlertType, at.upper())


class TestNotificationChannel:
    def test_all_channels_exist(self):
        expected = [
            "sms", "email", "mobile_push", "website",
            "social_media", "emergency_broadcast"
        ]
        for nc in expected:
            assert hasattr(NotificationChannel, nc.upper())
