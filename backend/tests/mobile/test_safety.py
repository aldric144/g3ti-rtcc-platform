"""
G3TI RTCC-UIP Mobile Safety Tests
Tests for the Officer Safety Mobile Module
"""


import pytest

from app.mobile.safety import (
    CheckInType,
    FallDetectionStatus,
    MobileSafetyManager,
    ThreatLevel,
    WarningType,
)


class TestMobileSafetyManager:
    """Tests for MobileSafetyManager"""

    @pytest.fixture
    def manager(self):
        """Create a fresh manager instance for each test"""
        return MobileSafetyManager()

    def test_get_safety_status_new_officer(self, manager):
        """Test getting safety status for new officer"""
        status = manager.get_safety_status("1234")

        assert status is not None
        assert status.badge_number == "1234"
        assert status.threat_level == ThreatLevel.MINIMAL
        assert status.threat_score == 0.0

    def test_update_safety_status(self, manager):
        """Test updating safety status"""
        status = manager.update_safety_status(
            badge_number="1234",
            threat_level=ThreatLevel.ELEVATED,
            threat_score=0.65,
            in_hotzone=True,
            hotzone_name="Downtown District",
        )

        assert status is not None
        assert status.threat_level == ThreatLevel.ELEVATED
        assert status.threat_score == 0.65
        assert status.in_hotzone is True
        assert status.hotzone_name == "Downtown District"

    def test_add_proximity_warning(self, manager):
        """Test adding proximity warning"""
        warning = manager.add_proximity_warning(
            badge_number="1234",
            warning_type=WarningType.KNOWN_OFFENDER,
            title="Known Violent Offender",
            description="John Doe - Prior assault charges",
            threat_level=ThreatLevel.HIGH,
            latitude=34.0522,
            longitude=-118.2437,
            distance_meters=150.0,
        )

        assert warning is not None
        assert warning.badge_number == "1234"
        assert warning.warning_type == WarningType.KNOWN_OFFENDER
        assert warning.threat_level == ThreatLevel.HIGH
        assert warning.distance_meters == 150.0
        assert warning.acknowledged is False

    def test_get_proximity_warnings(self, manager):
        """Test getting proximity warnings"""
        # Add warnings
        manager.add_proximity_warning(
            badge_number="1234",
            warning_type=WarningType.KNOWN_OFFENDER,
            title="Warning 1",
            description="Description 1",
            threat_level=ThreatLevel.HIGH,
            latitude=34.0522,
            longitude=-118.2437,
            distance_meters=100.0,
        )
        manager.add_proximity_warning(
            badge_number="1234",
            warning_type=WarningType.HOTZONE,
            title="Warning 2",
            description="Description 2",
            threat_level=ThreatLevel.ELEVATED,
            latitude=34.0522,
            longitude=-118.2437,
            distance_meters=200.0,
        )

        # Get warnings
        warnings = manager.get_proximity_warnings("1234")

        assert len(warnings) == 2

    def test_acknowledge_warning(self, manager):
        """Test acknowledging a warning"""
        warning = manager.add_proximity_warning(
            badge_number="1234",
            warning_type=WarningType.KNOWN_OFFENDER,
            title="Test Warning",
            description="Test description",
            threat_level=ThreatLevel.HIGH,
            latitude=34.0522,
            longitude=-118.2437,
            distance_meters=100.0,
        )

        result = manager.acknowledge_warning(warning.id, "1234")

        assert result is True
        assert warning.acknowledged is True
        assert warning.acknowledged_at is not None

    def test_create_ambush_alert(self, manager):
        """Test creating ambush alert"""
        alert = manager.create_ambush_alert(
            badge_number="1234",
            latitude=34.0522,
            longitude=-118.2437,
            description="Possible ambush detected",
            confidence_score=0.85,
        )

        assert alert is not None
        assert alert.badge_number == "1234"
        assert alert.confidence_score == 0.85
        assert alert.acknowledged is False

    def test_get_ambush_alerts(self, manager):
        """Test getting ambush alerts"""
        # Create alerts
        manager.create_ambush_alert(
            badge_number="1234",
            latitude=34.0522,
            longitude=-118.2437,
            description="Alert 1",
            confidence_score=0.8,
        )
        manager.create_ambush_alert(
            badge_number="1234",
            latitude=34.0523,
            longitude=-118.2438,
            description="Alert 2",
            confidence_score=0.9,
        )

        # Get alerts
        alerts = manager.get_ambush_alerts("1234")

        assert len(alerts) == 2

    def test_acknowledge_ambush_alert(self, manager):
        """Test acknowledging ambush alert"""
        alert = manager.create_ambush_alert(
            badge_number="1234",
            latitude=34.0522,
            longitude=-118.2437,
            description="Test alert",
            confidence_score=0.85,
        )

        result = manager.acknowledge_ambush_alert(alert.id, "1234")

        assert result is True
        assert alert.acknowledged is True

    def test_add_hotzone_warning(self, manager):
        """Test adding hotzone warning"""
        warning = manager.add_hotzone_warning(
            badge_number="1234",
            hotzone_id="hz-001",
            hotzone_name="Downtown District",
            threat_level=ThreatLevel.HIGH,
            description="High crime area",
            latitude=34.0522,
            longitude=-118.2437,
        )

        assert warning is not None
        assert warning.hotzone_name == "Downtown District"
        assert warning.threat_level == ThreatLevel.HIGH

    def test_get_hotzone_warnings(self, manager):
        """Test getting hotzone warnings"""
        # Add warnings
        manager.add_hotzone_warning(
            badge_number="1234",
            hotzone_id="hz-001",
            hotzone_name="Zone 1",
            threat_level=ThreatLevel.HIGH,
            description="Description 1",
            latitude=34.0522,
            longitude=-118.2437,
        )
        manager.add_hotzone_warning(
            badge_number="1234",
            hotzone_id="hz-002",
            hotzone_name="Zone 2",
            threat_level=ThreatLevel.ELEVATED,
            description="Description 2",
            latitude=34.0523,
            longitude=-118.2438,
        )

        # Get warnings
        warnings = manager.get_hotzone_warnings("1234")

        assert len(warnings) == 2

    def test_check_in_safe(self, manager):
        """Test safe check-in"""
        checkin = manager.check_in(
            badge_number="1234",
            check_in_type=CheckInType.SAFE,
            latitude=34.0522,
            longitude=-118.2437,
        )

        assert checkin is not None
        assert checkin.badge_number == "1234"
        assert checkin.check_in_type == CheckInType.SAFE

        # Verify status updated
        status = manager.get_safety_status("1234")
        assert status.last_check_in is not None

    def test_check_in_routine(self, manager):
        """Test routine check-in"""
        checkin = manager.check_in(
            badge_number="1234",
            check_in_type=CheckInType.ROUTINE,
        )

        assert checkin is not None
        assert checkin.check_in_type == CheckInType.ROUTINE

    def test_check_in_emergency(self, manager):
        """Test emergency check-in"""
        checkin = manager.check_in(
            badge_number="1234",
            check_in_type=CheckInType.EMERGENCY,
            latitude=34.0522,
            longitude=-118.2437,
            notes="Officer needs assistance",
        )

        assert checkin is not None
        assert checkin.check_in_type == CheckInType.EMERGENCY
        assert checkin.notes == "Officer needs assistance"

    def test_get_check_ins(self, manager):
        """Test getting check-ins"""
        # Create check-ins
        manager.check_in(
            badge_number="1234",
            check_in_type=CheckInType.SAFE,
        )
        manager.check_in(
            badge_number="1234",
            check_in_type=CheckInType.ROUTINE,
        )

        # Get check-ins
        checkins = manager.get_check_ins("1234")

        assert len(checkins) == 2

    def test_report_fall_detection(self, manager):
        """Test reporting fall detection"""
        event = manager.report_fall_detection(
            badge_number="1234",
            latitude=34.0522,
            longitude=-118.2437,
            accelerometer_data={"x": 0.1, "y": 9.8, "z": 0.2},
            confidence_score=0.92,
        )

        assert event is not None
        assert event.badge_number == "1234"
        assert event.status == FallDetectionStatus.DETECTED
        assert event.confidence_score == 0.92

    def test_acknowledge_fall_detection(self, manager):
        """Test acknowledging fall detection"""
        event = manager.report_fall_detection(
            badge_number="1234",
            latitude=34.0522,
            longitude=-118.2437,
            accelerometer_data={"x": 0.1, "y": 9.8, "z": 0.2},
            confidence_score=0.92,
        )

        result = manager.acknowledge_fall_detection(event.id, "1234")

        assert result is True
        assert event.status == FallDetectionStatus.ACKNOWLEDGED

    def test_confirm_fall(self, manager):
        """Test confirming fall"""
        event = manager.report_fall_detection(
            badge_number="1234",
            latitude=34.0522,
            longitude=-118.2437,
            accelerometer_data={"x": 0.1, "y": 9.8, "z": 0.2},
            confidence_score=0.92,
        )

        result = manager.confirm_fall(event.id, "1234", is_false_alarm=False)

        assert result is True
        assert event.status == FallDetectionStatus.CONFIRMED

    def test_confirm_fall_false_alarm(self, manager):
        """Test confirming fall as false alarm"""
        event = manager.report_fall_detection(
            badge_number="1234",
            latitude=34.0522,
            longitude=-118.2437,
            accelerometer_data={"x": 0.1, "y": 9.8, "z": 0.2},
            confidence_score=0.92,
        )

        result = manager.confirm_fall(event.id, "1234", is_false_alarm=True)

        assert result is True
        assert event.status == FallDetectionStatus.FALSE_ALARM

    def test_get_officers_needing_checkin(self, manager):
        """Test getting officers needing check-in"""
        # Create status for officers
        manager.get_safety_status("1234")
        manager.get_safety_status("5678")

        # Check in one officer
        manager.check_in(
            badge_number="1234",
            check_in_type=CheckInType.ROUTINE,
        )

        # Get officers needing check-in (with very short interval for testing)
        officers = manager.get_officers_needing_checkin(check_in_interval_minutes=0)

        # Both should need check-in since interval is 0
        assert len(officers) >= 1
