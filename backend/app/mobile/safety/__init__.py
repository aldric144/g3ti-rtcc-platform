"""
G3TI RTCC-UIP Mobile Safety Module
Officer Safety integration for mobile devices.
Integrates with Phase 6 Officer Safety Engine.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ThreatLevel(str, Enum):
    """Officer threat levels."""
    CRITICAL = "critical"
    HIGH = "high"
    ELEVATED = "elevated"
    MODERATE = "moderate"
    LOW = "low"
    MINIMAL = "minimal"


class WarningType(str, Enum):
    """Warning types for mobile."""
    PROXIMITY = "proximity"
    AMBUSH = "ambush"
    HOTZONE = "hotzone"
    THREAT = "threat"
    GUNFIRE = "gunfire"
    OFFICER_DOWN = "officer_down"
    HAZARD = "hazard"
    WANTED_PERSON = "wanted_person"
    STOLEN_VEHICLE = "stolen_vehicle"


class CheckInType(str, Enum):
    """Check-in types."""
    ROUTINE = "routine"
    SAFE = "safe"
    EMERGENCY = "emergency"
    ARRIVED = "arrived"
    CLEARED = "cleared"


class FallDetectionStatus(str, Enum):
    """Fall detection status."""
    NORMAL = "normal"
    POSSIBLE_FALL = "possible_fall"
    CONFIRMED_FALL = "confirmed_fall"
    FALSE_ALARM = "false_alarm"
    ACKNOWLEDGED = "acknowledged"


class OfficerSafetyStatus(BaseModel):
    """Officer safety status for mobile."""
    badge_number: str
    officer_name: str
    threat_level: ThreatLevel = ThreatLevel.LOW
    threat_score: float = 0.0
    active_warnings: list[str] = Field(default_factory=list)
    nearby_threats: int = 0
    in_hotzone: bool = False
    hotzone_name: str | None = None
    last_check_in: datetime | None = None
    last_location: dict[str, float] | None = None
    fall_detection_status: FallDetectionStatus = FallDetectionStatus.NORMAL
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class ProximityWarning(BaseModel):
    """Proximity warning for mobile."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    warning_type: WarningType
    title: str
    description: str
    threat_level: ThreatLevel
    distance_meters: float
    direction: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    entity_id: str | None = None
    entity_type: str | None = None
    entity_name: str | None = None
    additional_info: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    acknowledged: bool = False

    class Config:
        use_enum_values = True


class AmbushAlert(BaseModel):
    """Ambush detection alert."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_level: ThreatLevel
    location: str
    latitude: float
    longitude: float
    indicators: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    affected_units: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_by: list[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class HotzoneWarning(BaseModel):
    """Hotzone warning for mobile."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    zone_id: str
    zone_name: str
    zone_type: str
    threat_level: ThreatLevel
    risk_score: float
    center_lat: float
    center_lng: float
    radius_meters: float
    recent_incidents: int = 0
    recent_gunfire: int = 0
    hazards: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class CheckIn(BaseModel):
    """Officer check-in record."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    badge_number: str
    check_in_type: CheckInType
    latitude: float | None = None
    longitude: float | None = None
    location_description: str | None = None
    notes: str | None = None
    call_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    device_id: str | None = None

    class Config:
        use_enum_values = True


class FallDetectionEvent(BaseModel):
    """Fall detection event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    badge_number: str
    status: FallDetectionStatus
    latitude: float | None = None
    longitude: float | None = None
    accelerometer_data: dict[str, Any] | None = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    false_alarm_reason: str | None = None

    class Config:
        use_enum_values = True


class MobileSafetyManager:
    """
    Mobile Officer Safety Manager.
    Integrates with Phase 6 Officer Safety Engine for mobile devices.
    """

    def __init__(self) -> None:
        """Initialize the mobile safety manager."""
        self._officer_statuses: dict[str, OfficerSafetyStatus] = {}
        self._proximity_warnings: dict[str, list[ProximityWarning]] = {}
        self._ambush_alerts: dict[str, AmbushAlert] = {}
        self._hotzone_warnings: dict[str, list[HotzoneWarning]] = {}
        self._check_ins: dict[str, list[CheckIn]] = {}
        self._fall_events: dict[str, FallDetectionEvent] = {}

        # Configuration
        self._proximity_radius_meters = 500
        self._warning_expiry_minutes = 30
        self._check_in_interval_minutes = 30

    async def get_safety_status(self, badge_number: str) -> OfficerSafetyStatus:
        """
        Get officer safety status.

        Args:
            badge_number: Officer badge number

        Returns:
            Officer safety status
        """
        status = self._officer_statuses.get(badge_number)
        if not status:
            status = OfficerSafetyStatus(
                badge_number=badge_number,
                officer_name=f"Officer {badge_number}",
            )
            self._officer_statuses[badge_number] = status
        return status

    async def update_safety_status(
        self,
        badge_number: str,
        threat_level: ThreatLevel | None = None,
        threat_score: float | None = None,
        in_hotzone: bool | None = None,
        hotzone_name: str | None = None,
        location: dict[str, float] | None = None,
    ) -> OfficerSafetyStatus:
        """
        Update officer safety status.

        Args:
            badge_number: Officer badge number
            threat_level: New threat level
            threat_score: New threat score
            in_hotzone: Whether in hotzone
            hotzone_name: Hotzone name
            location: Current location

        Returns:
            Updated status
        """
        status = await self.get_safety_status(badge_number)

        if threat_level is not None:
            status.threat_level = threat_level
        if threat_score is not None:
            status.threat_score = threat_score
        if in_hotzone is not None:
            status.in_hotzone = in_hotzone
        if hotzone_name is not None:
            status.hotzone_name = hotzone_name
        if location is not None:
            status.last_location = location

        status.updated_at = datetime.utcnow()

        # Count active warnings
        warnings = self._proximity_warnings.get(badge_number, [])
        status.active_warnings = [w.warning_type.value for w in warnings if not w.acknowledged]
        status.nearby_threats = len([w for w in warnings if w.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]])

        return status

    async def add_proximity_warning(
        self,
        badge_number: str,
        warning_type: WarningType,
        title: str,
        description: str,
        threat_level: ThreatLevel,
        distance_meters: float,
        direction: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        entity_id: str | None = None,
        entity_type: str | None = None,
        entity_name: str | None = None,
        additional_info: dict[str, Any] | None = None,
    ) -> ProximityWarning:
        """
        Add a proximity warning for an officer.

        Args:
            badge_number: Officer badge number
            warning_type: Type of warning
            title: Warning title
            description: Warning description
            threat_level: Threat level
            distance_meters: Distance to threat
            direction: Direction to threat
            latitude: Threat latitude
            longitude: Threat longitude
            entity_id: Related entity ID
            entity_type: Related entity type
            entity_name: Related entity name
            additional_info: Additional information

        Returns:
            Created warning
        """
        warning = ProximityWarning(
            warning_type=warning_type,
            title=title,
            description=description,
            threat_level=threat_level,
            distance_meters=distance_meters,
            direction=direction,
            latitude=latitude,
            longitude=longitude,
            entity_id=entity_id,
            entity_type=entity_type,
            entity_name=entity_name,
            additional_info=additional_info or {},
            expires_at=datetime.utcnow() + timedelta(minutes=self._warning_expiry_minutes),
        )

        if badge_number not in self._proximity_warnings:
            self._proximity_warnings[badge_number] = []
        self._proximity_warnings[badge_number].append(warning)

        # Update status
        await self.update_safety_status(badge_number)

        return warning

    async def get_proximity_warnings(
        self,
        badge_number: str,
        include_acknowledged: bool = False,
    ) -> list[ProximityWarning]:
        """
        Get proximity warnings for an officer.

        Args:
            badge_number: Officer badge number
            include_acknowledged: Include acknowledged warnings

        Returns:
            List of warnings
        """
        now = datetime.utcnow()
        warnings = self._proximity_warnings.get(badge_number, [])

        return [
            w for w in warnings
            if (include_acknowledged or not w.acknowledged)
            and (not w.expires_at or w.expires_at > now)
        ]

    async def acknowledge_warning(self, badge_number: str, warning_id: str) -> bool:
        """Acknowledge a proximity warning."""
        warnings = self._proximity_warnings.get(badge_number, [])
        for warning in warnings:
            if warning.id == warning_id:
                warning.acknowledged = True
                await self.update_safety_status(badge_number)
                return True
        return False

    async def create_ambush_alert(
        self,
        alert_level: ThreatLevel,
        location: str,
        latitude: float,
        longitude: float,
        indicators: list[str],
        recommended_actions: list[str],
        affected_units: list[str],
    ) -> AmbushAlert:
        """
        Create an ambush alert.

        Args:
            alert_level: Alert threat level
            location: Location description
            latitude: Alert latitude
            longitude: Alert longitude
            indicators: Ambush indicators
            recommended_actions: Recommended actions
            affected_units: Affected unit IDs

        Returns:
            Created alert
        """
        alert = AmbushAlert(
            alert_level=alert_level,
            location=location,
            latitude=latitude,
            longitude=longitude,
            indicators=indicators,
            recommended_actions=recommended_actions,
            affected_units=affected_units,
        )

        self._ambush_alerts[alert.id] = alert

        # Add proximity warnings to affected officers
        for unit_id in affected_units:
            await self.add_proximity_warning(
                badge_number=unit_id,
                warning_type=WarningType.AMBUSH,
                title="AMBUSH ALERT",
                description=f"Possible ambush detected at {location}",
                threat_level=alert_level,
                distance_meters=0,
                latitude=latitude,
                longitude=longitude,
                additional_info={"indicators": indicators, "actions": recommended_actions},
            )

        return alert

    async def get_ambush_alerts(
        self,
        badge_number: str | None = None,
        active_only: bool = True,
    ) -> list[AmbushAlert]:
        """
        Get ambush alerts.

        Args:
            badge_number: Filter by affected badge
            active_only: Only return unacknowledged alerts

        Returns:
            List of alerts
        """
        alerts = list(self._ambush_alerts.values())

        if badge_number:
            alerts = [a for a in alerts if badge_number in a.affected_units]

        if active_only:
            alerts = [a for a in alerts if badge_number not in a.acknowledged_by]

        return sorted(alerts, key=lambda a: a.created_at, reverse=True)

    async def acknowledge_ambush_alert(self, alert_id: str, badge_number: str) -> bool:
        """Acknowledge an ambush alert."""
        alert = self._ambush_alerts.get(alert_id)
        if alert and badge_number not in alert.acknowledged_by:
            alert.acknowledged_by.append(badge_number)
            return True
        return False

    async def add_hotzone_warning(
        self,
        badge_number: str,
        zone_id: str,
        zone_name: str,
        zone_type: str,
        threat_level: ThreatLevel,
        risk_score: float,
        center_lat: float,
        center_lng: float,
        radius_meters: float,
        recent_incidents: int = 0,
        recent_gunfire: int = 0,
        hazards: list[str] | None = None,
        recommendations: list[str] | None = None,
    ) -> HotzoneWarning:
        """
        Add a hotzone warning for an officer.

        Args:
            badge_number: Officer badge number
            zone_id: Zone ID
            zone_name: Zone name
            zone_type: Zone type
            threat_level: Threat level
            risk_score: Risk score
            center_lat: Zone center latitude
            center_lng: Zone center longitude
            radius_meters: Zone radius
            recent_incidents: Recent incident count
            recent_gunfire: Recent gunfire count
            hazards: Known hazards
            recommendations: Safety recommendations

        Returns:
            Created warning
        """
        warning = HotzoneWarning(
            zone_id=zone_id,
            zone_name=zone_name,
            zone_type=zone_type,
            threat_level=threat_level,
            risk_score=risk_score,
            center_lat=center_lat,
            center_lng=center_lng,
            radius_meters=radius_meters,
            recent_incidents=recent_incidents,
            recent_gunfire=recent_gunfire,
            hazards=hazards or [],
            recommendations=recommendations or [],
        )

        if badge_number not in self._hotzone_warnings:
            self._hotzone_warnings[badge_number] = []
        self._hotzone_warnings[badge_number].append(warning)

        # Update status
        await self.update_safety_status(
            badge_number,
            in_hotzone=True,
            hotzone_name=zone_name,
        )

        return warning

    async def get_hotzone_warnings(self, badge_number: str) -> list[HotzoneWarning]:
        """Get hotzone warnings for an officer."""
        return self._hotzone_warnings.get(badge_number, [])

    async def clear_hotzone_warning(self, badge_number: str, zone_id: str) -> bool:
        """Clear a hotzone warning when officer leaves zone."""
        warnings = self._hotzone_warnings.get(badge_number, [])
        self._hotzone_warnings[badge_number] = [w for w in warnings if w.zone_id != zone_id]

        # Update status if no more hotzones
        if not self._hotzone_warnings.get(badge_number):
            await self.update_safety_status(
                badge_number,
                in_hotzone=False,
                hotzone_name=None,
            )

        return True

    async def check_in(
        self,
        badge_number: str,
        check_in_type: CheckInType,
        latitude: float | None = None,
        longitude: float | None = None,
        location_description: str | None = None,
        notes: str | None = None,
        call_id: str | None = None,
        device_id: str | None = None,
    ) -> CheckIn:
        """
        Record officer check-in.

        Args:
            badge_number: Officer badge number
            check_in_type: Type of check-in
            latitude: GPS latitude
            longitude: GPS longitude
            location_description: Location description
            notes: Check-in notes
            call_id: Associated call ID
            device_id: Device ID

        Returns:
            Check-in record
        """
        check_in = CheckIn(
            badge_number=badge_number,
            check_in_type=check_in_type,
            latitude=latitude,
            longitude=longitude,
            location_description=location_description,
            notes=notes,
            call_id=call_id,
            device_id=device_id,
        )

        if badge_number not in self._check_ins:
            self._check_ins[badge_number] = []
        self._check_ins[badge_number].append(check_in)

        # Update status
        status = await self.get_safety_status(badge_number)
        status.last_check_in = check_in.created_at
        if latitude and longitude:
            status.last_location = {"lat": latitude, "lng": longitude}

        return check_in

    async def get_check_ins(
        self,
        badge_number: str,
        limit: int = 50,
        since: datetime | None = None,
    ) -> list[CheckIn]:
        """
        Get check-in history for an officer.

        Args:
            badge_number: Officer badge number
            limit: Maximum records
            since: Only records after this time

        Returns:
            List of check-ins
        """
        check_ins = self._check_ins.get(badge_number, [])

        if since:
            check_ins = [c for c in check_ins if c.created_at > since]

        return sorted(check_ins, key=lambda c: c.created_at, reverse=True)[:limit]

    async def report_fall_detection(
        self,
        badge_number: str,
        latitude: float | None = None,
        longitude: float | None = None,
        accelerometer_data: dict[str, Any] | None = None,
    ) -> FallDetectionEvent:
        """
        Report a fall detection event.

        Args:
            badge_number: Officer badge number
            latitude: GPS latitude
            longitude: GPS longitude
            accelerometer_data: Accelerometer data from device

        Returns:
            Fall detection event
        """
        event = FallDetectionEvent(
            badge_number=badge_number,
            status=FallDetectionStatus.POSSIBLE_FALL,
            latitude=latitude,
            longitude=longitude,
            accelerometer_data=accelerometer_data,
        )

        self._fall_events[badge_number] = event

        # Update status
        status = await self.get_safety_status(badge_number)
        status.fall_detection_status = FallDetectionStatus.POSSIBLE_FALL

        return event

    async def acknowledge_fall_detection(
        self,
        badge_number: str,
        acknowledged_by: str,
        is_false_alarm: bool = False,
        false_alarm_reason: str | None = None,
    ) -> FallDetectionEvent | None:
        """
        Acknowledge a fall detection event.

        Args:
            badge_number: Officer badge number
            acknowledged_by: Who acknowledged
            is_false_alarm: Whether it was a false alarm
            false_alarm_reason: Reason for false alarm

        Returns:
            Updated event or None
        """
        event = self._fall_events.get(badge_number)
        if not event:
            return None

        event.acknowledged_at = datetime.utcnow()
        event.acknowledged_by = acknowledged_by

        if is_false_alarm:
            event.status = FallDetectionStatus.FALSE_ALARM
            event.false_alarm_reason = false_alarm_reason
        else:
            event.status = FallDetectionStatus.ACKNOWLEDGED

        # Update status
        status = await self.get_safety_status(badge_number)
        status.fall_detection_status = event.status

        return event

    async def confirm_fall(self, badge_number: str) -> FallDetectionEvent | None:
        """Confirm a fall detection as real."""
        event = self._fall_events.get(badge_number)
        if event:
            event.status = FallDetectionStatus.CONFIRMED_FALL
            status = await self.get_safety_status(badge_number)
            status.fall_detection_status = FallDetectionStatus.CONFIRMED_FALL
        return event

    async def get_fall_detection_status(self, badge_number: str) -> FallDetectionEvent | None:
        """Get current fall detection status."""
        return self._fall_events.get(badge_number)

    async def get_officers_needing_checkin(
        self,
        threshold_minutes: int | None = None,
    ) -> list[OfficerSafetyStatus]:
        """
        Get officers who haven't checked in recently.

        Args:
            threshold_minutes: Minutes since last check-in

        Returns:
            List of officer statuses
        """
        threshold = threshold_minutes or self._check_in_interval_minutes
        cutoff = datetime.utcnow() - timedelta(minutes=threshold)

        return [
            status for status in self._officer_statuses.values()
            if not status.last_check_in or status.last_check_in < cutoff
        ]


# Global instance
mobile_safety = MobileSafetyManager()
