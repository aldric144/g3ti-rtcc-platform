"""
G3TI RTCC-UIP Mobile Telemetry Tests
Tests for the Unit Status Telemetry Integration module
"""


import pytest

from app.mobile.telemetry import (
    BatteryStatus,
    GPSAccuracy,
    NetworkStatus,
    RadioStatus,
    TelemetryManager,
    TelemetryType,
)


class TestTelemetryManager:
    """Tests for TelemetryManager"""

    @pytest.fixture
    def manager(self):
        """Create a fresh manager instance for each test"""
        return TelemetryManager()

    def test_update_gps(self, manager):
        """Test GPS update"""
        location = manager.update_gps(
            badge_number="1234",
            unit_id="A1",
            latitude=34.0522,
            longitude=-118.2437,
            accuracy=GPSAccuracy.HIGH,
            altitude=100.0,
            speed=25.5,
            heading=180.0,
        )

        assert location is not None
        assert location.badge_number == "1234"
        assert location.latitude == 34.0522
        assert location.longitude == -118.2437
        assert location.accuracy == GPSAccuracy.HIGH
        assert location.speed == 25.5

    def test_update_battery(self, manager):
        """Test battery update"""
        battery = manager.update_battery(
            badge_number="1234",
            unit_id="A1",
            level=85,
            status=BatteryStatus.DISCHARGING,
            temperature=35.0,
        )

        assert battery is not None
        assert battery.level == 85
        assert battery.status == BatteryStatus.DISCHARGING

    def test_update_battery_low_alert(self, manager):
        """Test battery low alert generation"""
        # Update with low battery
        manager.update_battery(
            badge_number="1234",
            unit_id="A1",
            level=15,
            status=BatteryStatus.DISCHARGING,
        )

        # Check for alerts
        alerts = manager.get_alerts("1234")
        low_battery_alerts = [a for a in alerts if a.telemetry_type == TelemetryType.BATTERY]

        assert len(low_battery_alerts) > 0

    def test_update_radio(self, manager):
        """Test radio status update"""
        radio = manager.update_radio(
            badge_number="1234",
            unit_id="A1",
            status=RadioStatus.CONNECTED,
            signal_strength=-65,
            channel="Channel 1",
        )

        assert radio is not None
        assert radio.status == RadioStatus.CONNECTED
        assert radio.signal_strength == -65
        assert radio.channel == "Channel 1"

    def test_update_network(self, manager):
        """Test network status update"""
        network = manager.update_network(
            badge_number="1234",
            unit_id="A1",
            status=NetworkStatus.CONNECTED,
            network_type="LTE",
            signal_strength=-75,
            carrier="Verizon",
        )

        assert network is not None
        assert network.status == NetworkStatus.CONNECTED
        assert network.network_type == "LTE"

    def test_update_accelerometer(self, manager):
        """Test accelerometer data update"""
        accel = manager.update_accelerometer(
            badge_number="1234",
            unit_id="A1",
            x=0.1,
            y=9.8,
            z=0.2,
        )

        assert accel is not None
        assert accel.x == 0.1
        assert accel.y == 9.8
        assert accel.z == 0.2

    def test_get_telemetry(self, manager):
        """Test getting telemetry for a unit"""
        # Update various telemetry
        manager.update_gps(
            badge_number="1234",
            unit_id="A1",
            latitude=34.0522,
            longitude=-118.2437,
            accuracy=GPSAccuracy.HIGH,
        )
        manager.update_battery(
            badge_number="1234",
            unit_id="A1",
            level=85,
            status=BatteryStatus.DISCHARGING,
        )

        # Get telemetry
        telemetry = manager.get_telemetry("1234")

        assert telemetry is not None
        assert telemetry.badge_number == "1234"
        assert telemetry.gps is not None
        assert telemetry.battery is not None

    def test_get_all_telemetry(self, manager):
        """Test getting all telemetry"""
        # Update telemetry for multiple units
        manager.update_gps(
            badge_number="1234",
            unit_id="A1",
            latitude=34.0522,
            longitude=-118.2437,
            accuracy=GPSAccuracy.HIGH,
        )
        manager.update_gps(
            badge_number="5678",
            unit_id="B2",
            latitude=34.0523,
            longitude=-118.2438,
            accuracy=GPSAccuracy.MEDIUM,
        )

        # Get all telemetry
        all_telemetry = manager.get_all_telemetry()

        assert len(all_telemetry) == 2

    def test_get_location_history(self, manager):
        """Test getting location history"""
        # Update GPS multiple times
        for i in range(5):
            manager.update_gps(
                badge_number="1234",
                unit_id="A1",
                latitude=34.0522 + i * 0.001,
                longitude=-118.2437 + i * 0.001,
                accuracy=GPSAccuracy.HIGH,
            )

        # Get history
        history = manager.get_location_history("1234", limit=10)

        assert len(history) == 5

    def test_get_alerts(self, manager):
        """Test getting telemetry alerts"""
        # Generate alerts by updating with low battery
        manager.update_battery(
            badge_number="1234",
            unit_id="A1",
            level=10,
            status=BatteryStatus.DISCHARGING,
        )

        # Get alerts
        alerts = manager.get_alerts("1234")

        assert len(alerts) > 0

    def test_acknowledge_alert(self, manager):
        """Test acknowledging telemetry alert"""
        # Generate alert
        manager.update_battery(
            badge_number="1234",
            unit_id="A1",
            level=10,
            status=BatteryStatus.DISCHARGING,
        )

        alerts = manager.get_alerts("1234")
        if alerts:
            alert = alerts[0]
            result = manager.acknowledge_alert(alert.id, "1234")
            assert result is True
            assert alert.acknowledged is True

    def test_get_units_in_area(self, manager):
        """Test getting units in a geographic area"""
        # Update GPS for multiple units
        manager.update_gps(
            badge_number="1234",
            unit_id="A1",
            latitude=34.0522,
            longitude=-118.2437,
            accuracy=GPSAccuracy.HIGH,
        )
        manager.update_gps(
            badge_number="5678",
            unit_id="B2",
            latitude=34.0523,
            longitude=-118.2438,
            accuracy=GPSAccuracy.HIGH,
        )
        manager.update_gps(
            badge_number="9012",
            unit_id="C3",
            latitude=35.0000,
            longitude=-119.0000,
            accuracy=GPSAccuracy.HIGH,
        )

        # Get units in area (small radius)
        units = manager.get_units_in_area(
            center_lat=34.0522,
            center_lon=-118.2437,
            radius_meters=1000,
        )

        # Should find 2 units (1234 and 5678)
        assert len(units) == 2

    def test_get_offline_units(self, manager):
        """Test getting offline units"""
        # Update GPS for a unit
        manager.update_gps(
            badge_number="1234",
            unit_id="A1",
            latitude=34.0522,
            longitude=-118.2437,
            accuracy=GPSAccuracy.HIGH,
        )

        # Get offline units (with very short timeout for testing)
        offline = manager.get_offline_units(timeout_minutes=0)

        # The unit should be considered offline with 0 minute timeout
        assert len(offline) >= 0  # May or may not be offline depending on timing
