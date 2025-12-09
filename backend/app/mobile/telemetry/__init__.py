"""
G3TI RTCC-UIP Mobile Telemetry Module
GPS location tracking, battery status, and radio status for mobile devices.
Integrates with Phase 5 Tactical Map and Phase 6 Officer Safety Engine.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TelemetryType(str, Enum):
    """Telemetry data types."""
    GPS = "gps"
    BATTERY = "battery"
    RADIO = "radio"
    NETWORK = "network"
    DEVICE = "device"
    ACCELEROMETER = "accelerometer"


class BatteryStatus(str, Enum):
    """Battery status levels."""
    FULL = "full"
    GOOD = "good"
    LOW = "low"
    CRITICAL = "critical"
    CHARGING = "charging"
    UNKNOWN = "unknown"


class RadioStatus(str, Enum):
    """Radio status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    WEAK_SIGNAL = "weak_signal"
    NO_SIGNAL = "no_signal"
    EMERGENCY = "emergency"
    UNKNOWN = "unknown"


class NetworkStatus(str, Enum):
    """Network connection status."""
    WIFI = "wifi"
    CELLULAR_5G = "5g"
    CELLULAR_4G = "4g"
    CELLULAR_3G = "3g"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class GPSAccuracy(str, Enum):
    """GPS accuracy levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"
    UNKNOWN = "unknown"


class GPSLocation(BaseModel):
    """GPS location data."""
    latitude: float
    longitude: float
    altitude: float | None = None
    accuracy_meters: float | None = None
    accuracy_level: GPSAccuracy = GPSAccuracy.UNKNOWN
    heading: float | None = None
    speed_mps: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "device"

    class Config:
        use_enum_values = True


class BatteryInfo(BaseModel):
    """Battery information."""
    level_percent: int
    status: BatteryStatus
    is_charging: bool = False
    temperature_celsius: float | None = None
    voltage: float | None = None
    health: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class RadioInfo(BaseModel):
    """Radio information."""
    status: RadioStatus
    signal_strength: int | None = None
    channel: str | None = None
    talkgroup: str | None = None
    last_transmission: datetime | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class NetworkInfo(BaseModel):
    """Network information."""
    status: NetworkStatus
    signal_strength: int | None = None
    carrier: str | None = None
    ip_address: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class AccelerometerData(BaseModel):
    """Accelerometer data for fall detection."""
    x: float
    y: float
    z: float
    magnitude: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UnitTelemetry(BaseModel):
    """Complete unit telemetry data."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    badge_number: str
    unit_id: str
    device_id: str
    gps: GPSLocation | None = None
    battery: BatteryInfo | None = None
    radio: RadioInfo | None = None
    network: NetworkInfo | None = None
    accelerometer: AccelerometerData | None = None
    last_update: datetime = Field(default_factory=datetime.utcnow)
    is_online: bool = True


class TelemetryAlert(BaseModel):
    """Telemetry-based alert."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    badge_number: str
    alert_type: str
    severity: str
    title: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None


class LocationHistory(BaseModel):
    """Location history entry."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    badge_number: str
    location: GPSLocation
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


class TelemetryManager:
    """
    Mobile Telemetry Manager.
    Handles GPS tracking, battery monitoring, and radio status.
    """

    def __init__(self) -> None:
        """Initialize the telemetry manager."""
        self._telemetry: dict[str, UnitTelemetry] = {}
        self._location_history: dict[str, list[LocationHistory]] = {}
        self._alerts: dict[str, list[TelemetryAlert]] = {}

        # Configuration
        self._battery_low_threshold = 20
        self._battery_critical_threshold = 10
        self._location_history_max = 1000
        self._offline_threshold_minutes = 5

    async def update_gps(
        self,
        badge_number: str,
        unit_id: str,
        device_id: str,
        latitude: float,
        longitude: float,
        altitude: float | None = None,
        accuracy_meters: float | None = None,
        heading: float | None = None,
        speed_mps: float | None = None,
    ) -> UnitTelemetry:
        """
        Update GPS location for a unit.

        Args:
            badge_number: Officer badge number
            unit_id: Unit ID
            device_id: Device ID
            latitude: GPS latitude
            longitude: GPS longitude
            altitude: GPS altitude
            accuracy_meters: Accuracy in meters
            heading: Heading in degrees
            speed_mps: Speed in meters per second

        Returns:
            Updated telemetry
        """
        # Determine accuracy level
        accuracy_level = GPSAccuracy.UNKNOWN
        if accuracy_meters is not None:
            if accuracy_meters <= 5:
                accuracy_level = GPSAccuracy.HIGH
            elif accuracy_meters <= 20:
                accuracy_level = GPSAccuracy.MEDIUM
            elif accuracy_meters <= 50:
                accuracy_level = GPSAccuracy.LOW
            else:
                accuracy_level = GPSAccuracy.VERY_LOW

        gps = GPSLocation(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            accuracy_meters=accuracy_meters,
            accuracy_level=accuracy_level,
            heading=heading,
            speed_mps=speed_mps,
        )

        telemetry = self._telemetry.get(badge_number)
        if not telemetry:
            telemetry = UnitTelemetry(
                badge_number=badge_number,
                unit_id=unit_id,
                device_id=device_id,
            )
            self._telemetry[badge_number] = telemetry

        telemetry.gps = gps
        telemetry.last_update = datetime.utcnow()
        telemetry.is_online = True

        # Record location history
        await self._record_location_history(badge_number, gps)

        return telemetry

    async def _record_location_history(
        self,
        badge_number: str,
        location: GPSLocation,
    ) -> None:
        """Record location in history."""
        if badge_number not in self._location_history:
            self._location_history[badge_number] = []

        history = LocationHistory(
            badge_number=badge_number,
            location=location,
        )
        self._location_history[badge_number].append(history)

        # Trim history if too long
        if len(self._location_history[badge_number]) > self._location_history_max:
            self._location_history[badge_number] = self._location_history[badge_number][-self._location_history_max:]

    async def update_battery(
        self,
        badge_number: str,
        level_percent: int,
        is_charging: bool = False,
        temperature_celsius: float | None = None,
        voltage: float | None = None,
        health: str | None = None,
    ) -> UnitTelemetry | None:
        """
        Update battery status for a unit.

        Args:
            badge_number: Officer badge number
            level_percent: Battery level percentage
            is_charging: Whether charging
            temperature_celsius: Battery temperature
            voltage: Battery voltage
            health: Battery health

        Returns:
            Updated telemetry or None
        """
        telemetry = self._telemetry.get(badge_number)
        if not telemetry:
            return None

        # Determine battery status
        if is_charging:
            status = BatteryStatus.CHARGING
        elif level_percent <= self._battery_critical_threshold:
            status = BatteryStatus.CRITICAL
        elif level_percent <= self._battery_low_threshold:
            status = BatteryStatus.LOW
        elif level_percent >= 80:
            status = BatteryStatus.FULL
        else:
            status = BatteryStatus.GOOD

        battery = BatteryInfo(
            level_percent=level_percent,
            status=status,
            is_charging=is_charging,
            temperature_celsius=temperature_celsius,
            voltage=voltage,
            health=health,
        )

        telemetry.battery = battery
        telemetry.last_update = datetime.utcnow()

        # Create alert if battery is low or critical
        if status in [BatteryStatus.LOW, BatteryStatus.CRITICAL]:
            await self._create_battery_alert(badge_number, battery)

        return telemetry

    async def _create_battery_alert(
        self,
        badge_number: str,
        battery: BatteryInfo,
    ) -> TelemetryAlert:
        """Create a battery alert."""
        severity = "critical" if battery.status == BatteryStatus.CRITICAL else "warning"
        alert = TelemetryAlert(
            badge_number=badge_number,
            alert_type="battery",
            severity=severity,
            title=f"Battery {battery.status.value.upper()}",
            message=f"Device battery at {battery.level_percent}%",
            data={"level": battery.level_percent, "status": battery.status.value},
        )

        if badge_number not in self._alerts:
            self._alerts[badge_number] = []
        self._alerts[badge_number].append(alert)

        return alert

    async def update_radio(
        self,
        badge_number: str,
        status: RadioStatus,
        signal_strength: int | None = None,
        channel: str | None = None,
        talkgroup: str | None = None,
    ) -> UnitTelemetry | None:
        """
        Update radio status for a unit.

        Args:
            badge_number: Officer badge number
            status: Radio status
            signal_strength: Signal strength
            channel: Radio channel
            talkgroup: Talkgroup

        Returns:
            Updated telemetry or None
        """
        telemetry = self._telemetry.get(badge_number)
        if not telemetry:
            return None

        radio = RadioInfo(
            status=status,
            signal_strength=signal_strength,
            channel=channel,
            talkgroup=talkgroup,
        )

        telemetry.radio = radio
        telemetry.last_update = datetime.utcnow()

        # Create alert if radio has issues
        if status in [RadioStatus.DISCONNECTED, RadioStatus.NO_SIGNAL]:
            await self._create_radio_alert(badge_number, radio)

        return telemetry

    async def _create_radio_alert(
        self,
        badge_number: str,
        radio: RadioInfo,
    ) -> TelemetryAlert:
        """Create a radio alert."""
        alert = TelemetryAlert(
            badge_number=badge_number,
            alert_type="radio",
            severity="warning",
            title=f"Radio {radio.status.value.upper()}",
            message=f"Radio status: {radio.status.value}",
            data={"status": radio.status.value},
        )

        if badge_number not in self._alerts:
            self._alerts[badge_number] = []
        self._alerts[badge_number].append(alert)

        return alert

    async def update_network(
        self,
        badge_number: str,
        status: NetworkStatus,
        signal_strength: int | None = None,
        carrier: str | None = None,
        ip_address: str | None = None,
    ) -> UnitTelemetry | None:
        """
        Update network status for a unit.

        Args:
            badge_number: Officer badge number
            status: Network status
            signal_strength: Signal strength
            carrier: Network carrier
            ip_address: IP address

        Returns:
            Updated telemetry or None
        """
        telemetry = self._telemetry.get(badge_number)
        if not telemetry:
            return None

        network = NetworkInfo(
            status=status,
            signal_strength=signal_strength,
            carrier=carrier,
            ip_address=ip_address,
        )

        telemetry.network = network
        telemetry.last_update = datetime.utcnow()

        return telemetry

    async def update_accelerometer(
        self,
        badge_number: str,
        x: float,
        y: float,
        z: float,
    ) -> UnitTelemetry | None:
        """
        Update accelerometer data for fall detection.

        Args:
            badge_number: Officer badge number
            x: X-axis acceleration
            y: Y-axis acceleration
            z: Z-axis acceleration

        Returns:
            Updated telemetry or None
        """
        telemetry = self._telemetry.get(badge_number)
        if not telemetry:
            return None

        magnitude = (x**2 + y**2 + z**2) ** 0.5

        accelerometer = AccelerometerData(
            x=x,
            y=y,
            z=z,
            magnitude=magnitude,
        )

        telemetry.accelerometer = accelerometer
        telemetry.last_update = datetime.utcnow()

        return telemetry

    async def get_telemetry(self, badge_number: str) -> UnitTelemetry | None:
        """Get telemetry for a unit."""
        return self._telemetry.get(badge_number)

    async def get_all_telemetry(
        self,
        online_only: bool = False,
    ) -> list[UnitTelemetry]:
        """
        Get all unit telemetry.

        Args:
            online_only: Only return online units

        Returns:
            List of telemetry
        """
        # Update online status
        cutoff = datetime.utcnow() - timedelta(minutes=self._offline_threshold_minutes)
        for telemetry in self._telemetry.values():
            telemetry.is_online = telemetry.last_update > cutoff

        telemetry_list = list(self._telemetry.values())

        if online_only:
            telemetry_list = [t for t in telemetry_list if t.is_online]

        return telemetry_list

    async def get_location_history(
        self,
        badge_number: str,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[LocationHistory]:
        """
        Get location history for a unit.

        Args:
            badge_number: Officer badge number
            limit: Maximum records
            since: Only records after this time

        Returns:
            List of location history
        """
        history = self._location_history.get(badge_number, [])

        if since:
            history = [h for h in history if h.recorded_at > since]

        return sorted(history, key=lambda h: h.recorded_at, reverse=True)[:limit]

    async def get_alerts(
        self,
        badge_number: str,
        include_acknowledged: bool = False,
    ) -> list[TelemetryAlert]:
        """
        Get telemetry alerts for a unit.

        Args:
            badge_number: Officer badge number
            include_acknowledged: Include acknowledged alerts

        Returns:
            List of alerts
        """
        alerts = self._alerts.get(badge_number, [])

        if not include_acknowledged:
            alerts = [a for a in alerts if not a.acknowledged]

        return sorted(alerts, key=lambda a: a.created_at, reverse=True)

    async def acknowledge_alert(
        self,
        badge_number: str,
        alert_id: str,
        acknowledged_by: str,
    ) -> TelemetryAlert | None:
        """
        Acknowledge a telemetry alert.

        Args:
            badge_number: Officer badge number
            alert_id: Alert ID
            acknowledged_by: Who acknowledged

        Returns:
            Updated alert or None
        """
        alerts = self._alerts.get(badge_number, [])
        for alert in alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = acknowledged_by
                return alert
        return None

    async def get_units_in_area(
        self,
        center_lat: float,
        center_lng: float,
        radius_meters: float,
    ) -> list[UnitTelemetry]:
        """
        Get units within a geographic area.

        Args:
            center_lat: Center latitude
            center_lng: Center longitude
            radius_meters: Radius in meters

        Returns:
            List of units in area
        """
        units = []

        for telemetry in self._telemetry.values():
            if not telemetry.gps:
                continue

            # Simple distance calculation (Haversine would be more accurate)
            lat_diff = abs(telemetry.gps.latitude - center_lat) * 111000
            lng_diff = abs(telemetry.gps.longitude - center_lng) * 111000 * 0.85
            distance = (lat_diff**2 + lng_diff**2) ** 0.5

            if distance <= radius_meters:
                units.append(telemetry)

        return units

    async def get_offline_units(self) -> list[UnitTelemetry]:
        """Get units that are offline."""
        cutoff = datetime.utcnow() - timedelta(minutes=self._offline_threshold_minutes)
        return [
            t for t in self._telemetry.values()
            if t.last_update < cutoff
        ]


# Global instance
telemetry_manager = TelemetryManager()
