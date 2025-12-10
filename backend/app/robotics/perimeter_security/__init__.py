"""
Perimeter Security Module

Provides perimeter security capabilities including:
- ThermalSensorGrid: Thermal sensor integration
- MotionRadarIngestor: Motion and radar event processing
- PerimeterBreachDetector: AI-powered breach detection and scoring
- AutoResponseEngine: Automatic dispatch of robots and drones
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
import math


class SensorZoneType(Enum):
    """Types of sensor zones."""
    PERIMETER = "perimeter"
    ENTRY_POINT = "entry_point"
    RESTRICTED = "restricted"
    HIGH_SECURITY = "high_security"
    PARKING = "parking"
    BUILDING = "building"
    OUTDOOR = "outdoor"


class BreachSeverity(Enum):
    """Severity levels for perimeter breaches."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class ResponseType(Enum):
    """Types of auto-responses."""
    DISPATCH_ROBOT = "dispatch_robot"
    DISPATCH_DRONE = "dispatch_drone"
    DISPATCH_BOTH = "dispatch_both"
    ALERT_ONLY = "alert_only"
    LOCKDOWN = "lockdown"
    ESCALATE = "escalate"


class MotionEventType(Enum):
    """Types of motion events."""
    HUMAN = "human"
    VEHICLE = "vehicle"
    ANIMAL = "animal"
    UNKNOWN = "unknown"
    MULTIPLE = "multiple"


class ThermalSignatureType(Enum):
    """Types of thermal signatures."""
    HUMAN = "human"
    VEHICLE_ENGINE = "vehicle_engine"
    ANIMAL = "animal"
    FIRE = "fire"
    EQUIPMENT = "equipment"
    UNKNOWN = "unknown"


@dataclass
class SensorZone:
    """Sensor zone definition."""
    zone_id: str
    name: str
    zone_type: SensorZoneType
    bounds: Dict[str, float]
    sensors: List[str]
    sensitivity: float
    is_active: bool
    alert_threshold: float
    response_type: ResponseType
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThermalReading:
    """Thermal sensor reading."""
    reading_id: str
    sensor_id: str
    zone_id: str
    timestamp: str
    temperature: float
    signature_type: ThermalSignatureType
    position: Dict[str, float]
    confidence: float
    size_estimate: Dict[str, float]
    velocity_estimate: Optional[Dict[str, float]]
    is_anomaly: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MotionEvent:
    """Motion or radar detection event."""
    event_id: str
    sensor_id: str
    zone_id: str
    timestamp: str
    event_type: MotionEventType
    position: Dict[str, float]
    velocity: Dict[str, float]
    heading: float
    size_estimate: float
    confidence: float
    radar_cross_section: Optional[float]
    doppler_signature: Optional[Dict[str, Any]]
    is_tracked: bool
    track_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerimeterBreach:
    """Detected perimeter breach."""
    breach_id: str
    zone_id: str
    timestamp: str
    severity: BreachSeverity
    breach_type: str
    position: Dict[str, float]
    confidence: float
    risk_score: float
    detected_entities: List[Dict[str, Any]]
    supporting_evidence: List[str]
    is_confirmed: bool
    is_resolved: bool
    response_triggered: bool
    response_id: Optional[str]
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[str]
    resolved_by: Optional[str]
    resolved_at: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AutoResponse:
    """Automatic response to breach."""
    response_id: str
    breach_id: str
    response_type: ResponseType
    timestamp: str
    dispatched_units: List[str]
    target_position: Dict[str, float]
    priority: int
    status: str
    eta_seconds: Optional[float]
    arrival_time: Optional[str]
    completion_time: Optional[str]
    result: Optional[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ThermalSensorGrid:
    """Service for thermal sensor grid integration."""

    def __init__(self):
        self.sensors: Dict[str, Dict[str, Any]] = {}
        self.readings: Dict[str, List[ThermalReading]] = {}
        self.latest_readings: Dict[str, ThermalReading] = {}
        self.zones: Dict[str, SensorZone] = {}

    def register_sensor(
        self,
        sensor_id: str,
        name: str,
        position: Dict[str, float],
        zone_id: str,
        field_of_view: float = 90.0,
        range_meters: float = 100.0,
        resolution: str = "640x480",
    ) -> Dict[str, Any]:
        """Register a thermal sensor."""
        sensor = {
            "sensor_id": sensor_id,
            "name": name,
            "position": position,
            "zone_id": zone_id,
            "field_of_view": field_of_view,
            "range_meters": range_meters,
            "resolution": resolution,
            "is_active": True,
            "last_reading": None,
            "registered_at": datetime.utcnow().isoformat() + "Z",
        }

        self.sensors[sensor_id] = sensor
        self.readings[sensor_id] = []

        return sensor

    def ingest_reading(
        self,
        sensor_id: str,
        temperature: float,
        signature_type: ThermalSignatureType,
        position: Dict[str, float],
        confidence: float,
        size_estimate: Dict[str, float],
        velocity_estimate: Optional[Dict[str, float]] = None,
    ) -> Optional[ThermalReading]:
        """Ingest a thermal reading from a sensor."""
        sensor = self.sensors.get(sensor_id)
        if not sensor:
            return None

        reading_id = f"thermal-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        is_anomaly = self._detect_anomaly(temperature, signature_type, sensor)

        reading = ThermalReading(
            reading_id=reading_id,
            sensor_id=sensor_id,
            zone_id=sensor["zone_id"],
            timestamp=timestamp,
            temperature=temperature,
            signature_type=signature_type,
            position=position,
            confidence=confidence,
            size_estimate=size_estimate,
            velocity_estimate=velocity_estimate,
            is_anomaly=is_anomaly,
            metadata={},
        )

        self.readings[sensor_id].append(reading)
        self.latest_readings[sensor_id] = reading
        sensor["last_reading"] = timestamp

        if len(self.readings[sensor_id]) > 1000:
            self.readings[sensor_id] = self.readings[sensor_id][-1000:]

        return reading

    def _detect_anomaly(
        self,
        temperature: float,
        signature_type: ThermalSignatureType,
        sensor: Dict[str, Any],
    ) -> bool:
        """Detect if a reading is anomalous."""
        if signature_type == ThermalSignatureType.FIRE:
            return True
        if temperature > 100:
            return True
        if signature_type == ThermalSignatureType.HUMAN and temperature > 40:
            return True
        return False

    def get_sensor(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Get sensor by ID."""
        return self.sensors.get(sensor_id)

    def get_sensors(
        self,
        zone_id: Optional[str] = None,
        active_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get sensors with optional filtering."""
        sensors = list(self.sensors.values())

        if zone_id:
            sensors = [s for s in sensors if s["zone_id"] == zone_id]

        if active_only:
            sensors = [s for s in sensors if s["is_active"]]

        return sensors

    def get_readings(
        self,
        sensor_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        anomalies_only: bool = False,
        limit: int = 100,
    ) -> List[ThermalReading]:
        """Get thermal readings with filtering."""
        if sensor_id:
            readings = self.readings.get(sensor_id, [])
        else:
            readings = []
            for sensor_readings in self.readings.values():
                readings.extend(sensor_readings)

        if zone_id:
            readings = [r for r in readings if r.zone_id == zone_id]

        if anomalies_only:
            readings = [r for r in readings if r.is_anomaly]

        readings.sort(key=lambda r: r.timestamp, reverse=True)
        return readings[:limit]

    def get_zone_thermal_map(self, zone_id: str) -> Dict[str, Any]:
        """Get thermal map for a zone."""
        readings = self.get_readings(zone_id=zone_id, limit=50)

        return {
            "zone_id": zone_id,
            "readings_count": len(readings),
            "readings": [
                {
                    "position": r.position,
                    "temperature": r.temperature,
                    "signature_type": r.signature_type.value,
                }
                for r in readings
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class MotionRadarIngestor:
    """Service for motion and radar event ingestion."""

    def __init__(self):
        self.sensors: Dict[str, Dict[str, Any]] = {}
        self.events: Dict[str, List[MotionEvent]] = {}
        self.tracks: Dict[str, List[MotionEvent]] = {}
        self.latest_events: Dict[str, MotionEvent] = {}

    def register_sensor(
        self,
        sensor_id: str,
        name: str,
        sensor_type: str,
        position: Dict[str, float],
        zone_id: str,
        range_meters: float = 200.0,
        detection_angle: float = 360.0,
    ) -> Dict[str, Any]:
        """Register a motion/radar sensor."""
        sensor = {
            "sensor_id": sensor_id,
            "name": name,
            "sensor_type": sensor_type,
            "position": position,
            "zone_id": zone_id,
            "range_meters": range_meters,
            "detection_angle": detection_angle,
            "is_active": True,
            "last_event": None,
            "registered_at": datetime.utcnow().isoformat() + "Z",
        }

        self.sensors[sensor_id] = sensor
        self.events[sensor_id] = []

        return sensor

    def ingest_event(
        self,
        sensor_id: str,
        event_type: MotionEventType,
        position: Dict[str, float],
        velocity: Dict[str, float],
        heading: float,
        size_estimate: float,
        confidence: float,
        radar_cross_section: Optional[float] = None,
        doppler_signature: Optional[Dict[str, Any]] = None,
        track_id: Optional[str] = None,
    ) -> Optional[MotionEvent]:
        """Ingest a motion/radar event."""
        sensor = self.sensors.get(sensor_id)
        if not sensor:
            return None

        event_id = f"motion-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        is_tracked = track_id is not None

        event = MotionEvent(
            event_id=event_id,
            sensor_id=sensor_id,
            zone_id=sensor["zone_id"],
            timestamp=timestamp,
            event_type=event_type,
            position=position,
            velocity=velocity,
            heading=heading,
            size_estimate=size_estimate,
            confidence=confidence,
            radar_cross_section=radar_cross_section,
            doppler_signature=doppler_signature,
            is_tracked=is_tracked,
            track_id=track_id,
            metadata={},
        )

        self.events[sensor_id].append(event)
        self.latest_events[sensor_id] = event
        sensor["last_event"] = timestamp

        if track_id:
            if track_id not in self.tracks:
                self.tracks[track_id] = []
            self.tracks[track_id].append(event)

        if len(self.events[sensor_id]) > 1000:
            self.events[sensor_id] = self.events[sensor_id][-1000:]

        return event

    def get_events(
        self,
        sensor_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        event_type: Optional[MotionEventType] = None,
        limit: int = 100,
    ) -> List[MotionEvent]:
        """Get motion events with filtering."""
        if sensor_id:
            events = self.events.get(sensor_id, [])
        else:
            events = []
            for sensor_events in self.events.values():
                events.extend(sensor_events)

        if zone_id:
            events = [e for e in events if e.zone_id == zone_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    def get_track(self, track_id: str) -> List[MotionEvent]:
        """Get all events for a track."""
        return self.tracks.get(track_id, [])

    def get_active_tracks(self, max_age_seconds: int = 60) -> List[Dict[str, Any]]:
        """Get currently active tracks."""
        active_tracks = []
        cutoff = datetime.utcnow()

        for track_id, events in self.tracks.items():
            if not events:
                continue

            latest = events[-1]
            latest_time = datetime.fromisoformat(latest.timestamp.replace('Z', ''))
            age = (cutoff - latest_time).total_seconds()

            if age <= max_age_seconds:
                active_tracks.append({
                    "track_id": track_id,
                    "event_count": len(events),
                    "latest_position": latest.position,
                    "latest_velocity": latest.velocity,
                    "event_type": latest.event_type.value,
                    "age_seconds": age,
                })

        return active_tracks


class PerimeterBreachDetector:
    """Service for detecting and scoring perimeter breaches."""

    def __init__(self):
        self.zones: Dict[str, SensorZone] = {}
        self.breaches: Dict[str, PerimeterBreach] = {}
        self.breach_rules: List[Dict[str, Any]] = []
        self._init_default_rules()

    def _init_default_rules(self):
        """Initialize default breach detection rules."""
        self.breach_rules = [
            {
                "name": "human_in_restricted",
                "zone_types": [SensorZoneType.RESTRICTED, SensorZoneType.HIGH_SECURITY],
                "event_types": [MotionEventType.HUMAN],
                "severity": BreachSeverity.HIGH,
                "score_multiplier": 1.5,
            },
            {
                "name": "vehicle_in_perimeter",
                "zone_types": [SensorZoneType.PERIMETER],
                "event_types": [MotionEventType.VEHICLE],
                "severity": BreachSeverity.MEDIUM,
                "score_multiplier": 1.2,
            },
            {
                "name": "multiple_entities",
                "zone_types": [SensorZoneType.PERIMETER, SensorZoneType.RESTRICTED],
                "event_types": [MotionEventType.MULTIPLE],
                "severity": BreachSeverity.CRITICAL,
                "score_multiplier": 2.0,
            },
            {
                "name": "thermal_anomaly",
                "zone_types": [SensorZoneType.HIGH_SECURITY],
                "thermal_types": [ThermalSignatureType.HUMAN, ThermalSignatureType.FIRE],
                "severity": BreachSeverity.HIGH,
                "score_multiplier": 1.8,
            },
        ]

    def register_zone(
        self,
        name: str,
        zone_type: SensorZoneType,
        bounds: Dict[str, float],
        sensors: List[str],
        sensitivity: float = 0.7,
        alert_threshold: float = 50.0,
        response_type: ResponseType = ResponseType.DISPATCH_ROBOT,
    ) -> SensorZone:
        """Register a sensor zone."""
        zone_id = f"zone-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        zone = SensorZone(
            zone_id=zone_id,
            name=name,
            zone_type=zone_type,
            bounds=bounds,
            sensors=sensors,
            sensitivity=sensitivity,
            is_active=True,
            alert_threshold=alert_threshold,
            response_type=response_type,
            created_at=timestamp,
            metadata={},
        )

        self.zones[zone_id] = zone

        return zone

    def detect_breach(
        self,
        zone_id: str,
        position: Dict[str, float],
        detected_entities: List[Dict[str, Any]],
        supporting_evidence: List[str],
        confidence: float = 0.8,
    ) -> Optional[PerimeterBreach]:
        """Detect and score a potential breach."""
        zone = self.zones.get(zone_id)
        if not zone or not zone.is_active:
            return None

        severity, risk_score = self._calculate_breach_score(
            zone, detected_entities, confidence
        )

        if risk_score < zone.alert_threshold:
            return None

        breach_id = f"breach-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        breach_type = self._determine_breach_type(detected_entities)

        breach = PerimeterBreach(
            breach_id=breach_id,
            zone_id=zone_id,
            timestamp=timestamp,
            severity=severity,
            breach_type=breach_type,
            position=position,
            confidence=confidence,
            risk_score=risk_score,
            detected_entities=detected_entities,
            supporting_evidence=supporting_evidence,
            is_confirmed=False,
            is_resolved=False,
            response_triggered=False,
            response_id=None,
            acknowledged_by=None,
            acknowledged_at=None,
            resolved_by=None,
            resolved_at=None,
            metadata={},
        )

        self.breaches[breach_id] = breach

        return breach

    def _calculate_breach_score(
        self,
        zone: SensorZone,
        entities: List[Dict[str, Any]],
        confidence: float,
    ) -> tuple:
        """Calculate breach severity and risk score."""
        base_score = 50.0
        multiplier = 1.0

        if zone.zone_type == SensorZoneType.HIGH_SECURITY:
            multiplier *= 2.0
        elif zone.zone_type == SensorZoneType.RESTRICTED:
            multiplier *= 1.5
        elif zone.zone_type == SensorZoneType.PERIMETER:
            multiplier *= 1.2

        entity_count = len(entities)
        if entity_count > 3:
            multiplier *= 1.5
        elif entity_count > 1:
            multiplier *= 1.2

        for entity in entities:
            entity_type = entity.get("type", "unknown")
            if entity_type == "human":
                base_score += 20
            elif entity_type == "vehicle":
                base_score += 15
            elif entity_type == "multiple":
                base_score += 30

        base_score *= zone.sensitivity
        risk_score = min(100.0, base_score * multiplier * confidence)

        if risk_score >= 80:
            severity = BreachSeverity.CRITICAL
        elif risk_score >= 60:
            severity = BreachSeverity.HIGH
        elif risk_score >= 40:
            severity = BreachSeverity.MEDIUM
        elif risk_score >= 20:
            severity = BreachSeverity.LOW
        else:
            severity = BreachSeverity.INFORMATIONAL

        return severity, risk_score

    def _determine_breach_type(self, entities: List[Dict[str, Any]]) -> str:
        """Determine the type of breach based on entities."""
        if not entities:
            return "unknown"

        types = [e.get("type", "unknown") for e in entities]

        if "multiple" in types or len(types) > 2:
            return "coordinated_intrusion"
        elif "vehicle" in types and "human" in types:
            return "vehicle_assisted_intrusion"
        elif "vehicle" in types:
            return "vehicle_intrusion"
        elif "human" in types:
            return "human_intrusion"
        else:
            return "unknown_intrusion"

    def acknowledge_breach(
        self,
        breach_id: str,
        acknowledged_by: str,
    ) -> bool:
        """Acknowledge a breach."""
        breach = self.breaches.get(breach_id)
        if not breach:
            return False

        breach.acknowledged_by = acknowledged_by
        breach.acknowledged_at = datetime.utcnow().isoformat() + "Z"

        return True

    def confirm_breach(self, breach_id: str) -> bool:
        """Confirm a breach as valid."""
        breach = self.breaches.get(breach_id)
        if not breach:
            return False

        breach.is_confirmed = True

        return True

    def resolve_breach(
        self,
        breach_id: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None,
    ) -> bool:
        """Resolve a breach."""
        breach = self.breaches.get(breach_id)
        if not breach:
            return False

        breach.is_resolved = True
        breach.resolved_by = resolved_by
        breach.resolved_at = datetime.utcnow().isoformat() + "Z"

        if resolution_notes:
            breach.metadata["resolution_notes"] = resolution_notes

        return True

    def get_breach(self, breach_id: str) -> Optional[PerimeterBreach]:
        """Get a breach by ID."""
        return self.breaches.get(breach_id)

    def get_breaches(
        self,
        zone_id: Optional[str] = None,
        severity: Optional[BreachSeverity] = None,
        unresolved_only: bool = False,
        limit: int = 100,
    ) -> List[PerimeterBreach]:
        """Get breaches with filtering."""
        breaches = list(self.breaches.values())

        if zone_id:
            breaches = [b for b in breaches if b.zone_id == zone_id]

        if severity:
            breaches = [b for b in breaches if b.severity == severity]

        if unresolved_only:
            breaches = [b for b in breaches if not b.is_resolved]

        breaches.sort(key=lambda b: b.timestamp, reverse=True)
        return breaches[:limit]

    def get_zone(self, zone_id: str) -> Optional[SensorZone]:
        """Get a zone by ID."""
        return self.zones.get(zone_id)

    def get_zones(
        self,
        zone_type: Optional[SensorZoneType] = None,
        active_only: bool = False,
    ) -> List[SensorZone]:
        """Get zones with filtering."""
        zones = list(self.zones.values())

        if zone_type:
            zones = [z for z in zones if z.zone_type == zone_type]

        if active_only:
            zones = [z for z in zones if z.is_active]

        return zones

    def get_metrics(self) -> Dict[str, Any]:
        """Get breach detection metrics."""
        total = len(self.breaches)
        by_severity = {}
        unresolved = 0
        confirmed = 0

        for breach in self.breaches.values():
            sev_key = breach.severity.value
            by_severity[sev_key] = by_severity.get(sev_key, 0) + 1

            if not breach.is_resolved:
                unresolved += 1
            if breach.is_confirmed:
                confirmed += 1

        return {
            "total_breaches": total,
            "by_severity": by_severity,
            "unresolved_count": unresolved,
            "confirmed_count": confirmed,
            "total_zones": len(self.zones),
            "active_zones": len([z for z in self.zones.values() if z.is_active]),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class AutoResponseEngine:
    """Engine for automatic response to breaches."""

    def __init__(self):
        self.responses: Dict[str, AutoResponse] = {}
        self.response_rules: Dict[str, Dict[str, Any]] = {}
        self.available_units: Dict[str, List[str]] = {
            "robots": [],
            "drones": [],
        }

    def register_unit(self, unit_id: str, unit_type: str) -> bool:
        """Register an available response unit."""
        if unit_type == "robot":
            if unit_id not in self.available_units["robots"]:
                self.available_units["robots"].append(unit_id)
            return True
        elif unit_type == "drone":
            if unit_id not in self.available_units["drones"]:
                self.available_units["drones"].append(unit_id)
            return True
        return False

    def unregister_unit(self, unit_id: str) -> bool:
        """Unregister a response unit."""
        if unit_id in self.available_units["robots"]:
            self.available_units["robots"].remove(unit_id)
            return True
        if unit_id in self.available_units["drones"]:
            self.available_units["drones"].remove(unit_id)
            return True
        return False

    def trigger_response(
        self,
        breach: PerimeterBreach,
        zone: SensorZone,
        robot_positions: Optional[Dict[str, Dict[str, float]]] = None,
        drone_positions: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> Optional[AutoResponse]:
        """Trigger automatic response to a breach."""
        response_id = f"response-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        response_type = zone.response_type
        dispatched_units = []
        priority = self._calculate_priority(breach)

        if response_type in [ResponseType.DISPATCH_ROBOT, ResponseType.DISPATCH_BOTH]:
            nearest_robot = self._find_nearest_unit(
                breach.position,
                self.available_units["robots"],
                robot_positions or {},
            )
            if nearest_robot:
                dispatched_units.append(nearest_robot)

        if response_type in [ResponseType.DISPATCH_DRONE, ResponseType.DISPATCH_BOTH]:
            nearest_drone = self._find_nearest_unit(
                breach.position,
                self.available_units["drones"],
                drone_positions or {},
            )
            if nearest_drone:
                dispatched_units.append(nearest_drone)

        if not dispatched_units and response_type != ResponseType.ALERT_ONLY:
            response_type = ResponseType.ALERT_ONLY

        eta = self._estimate_eta(breach.position, dispatched_units, robot_positions, drone_positions)

        response = AutoResponse(
            response_id=response_id,
            breach_id=breach.breach_id,
            response_type=response_type,
            timestamp=timestamp,
            dispatched_units=dispatched_units,
            target_position=breach.position,
            priority=priority,
            status="dispatched" if dispatched_units else "alert_only",
            eta_seconds=eta,
            arrival_time=None,
            completion_time=None,
            result=None,
            metadata={},
        )

        self.responses[response_id] = response

        breach.response_triggered = True
        breach.response_id = response_id

        return response

    def _find_nearest_unit(
        self,
        target_position: Dict[str, float],
        available_units: List[str],
        unit_positions: Dict[str, Dict[str, float]],
    ) -> Optional[str]:
        """Find the nearest available unit to a position."""
        if not available_units:
            return None

        nearest = None
        min_distance = float('inf')

        for unit_id in available_units:
            position = unit_positions.get(unit_id)
            if not position:
                continue

            dx = position.get('x', 0) - target_position.get('x', 0)
            dy = position.get('y', 0) - target_position.get('y', 0)
            distance = math.sqrt(dx**2 + dy**2)

            if distance < min_distance:
                min_distance = distance
                nearest = unit_id

        return nearest or (available_units[0] if available_units else None)

    def _calculate_priority(self, breach: PerimeterBreach) -> int:
        """Calculate response priority (1-10, 10 being highest)."""
        if breach.severity == BreachSeverity.CRITICAL:
            return 10
        elif breach.severity == BreachSeverity.HIGH:
            return 8
        elif breach.severity == BreachSeverity.MEDIUM:
            return 5
        elif breach.severity == BreachSeverity.LOW:
            return 3
        else:
            return 1

    def _estimate_eta(
        self,
        target: Dict[str, float],
        units: List[str],
        robot_positions: Optional[Dict[str, Dict[str, float]]],
        drone_positions: Optional[Dict[str, Dict[str, float]]],
    ) -> Optional[float]:
        """Estimate time of arrival for dispatched units."""
        if not units:
            return None

        min_eta = float('inf')
        robot_speed = 2.0
        drone_speed = 10.0

        for unit_id in units:
            position = None
            speed = robot_speed

            if robot_positions and unit_id in robot_positions:
                position = robot_positions[unit_id]
                speed = robot_speed
            elif drone_positions and unit_id in drone_positions:
                position = drone_positions[unit_id]
                speed = drone_speed

            if position:
                dx = position.get('x', 0) - target.get('x', 0)
                dy = position.get('y', 0) - target.get('y', 0)
                distance = math.sqrt(dx**2 + dy**2)
                eta = distance / speed

                if eta < min_eta:
                    min_eta = eta

        return min_eta if min_eta != float('inf') else None

    def update_response_status(
        self,
        response_id: str,
        status: str,
        arrival_time: Optional[str] = None,
        completion_time: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update response status."""
        response = self.responses.get(response_id)
        if not response:
            return False

        response.status = status

        if arrival_time:
            response.arrival_time = arrival_time
        if completion_time:
            response.completion_time = completion_time
        if result:
            response.result = result

        return True

    def get_response(self, response_id: str) -> Optional[AutoResponse]:
        """Get a response by ID."""
        return self.responses.get(response_id)

    def get_responses(
        self,
        breach_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[AutoResponse]:
        """Get responses with filtering."""
        responses = list(self.responses.values())

        if breach_id:
            responses = [r for r in responses if r.breach_id == breach_id]

        if status:
            responses = [r for r in responses if r.status == status]

        responses.sort(key=lambda r: r.timestamp, reverse=True)
        return responses[:limit]

    def get_active_responses(self) -> List[AutoResponse]:
        """Get currently active responses."""
        active_statuses = ["dispatched", "en_route", "on_scene"]
        return [r for r in self.responses.values() if r.status in active_statuses]

    def get_metrics(self) -> Dict[str, Any]:
        """Get auto-response metrics."""
        total = len(self.responses)
        by_type = {}
        by_status = {}
        avg_eta = 0.0
        eta_count = 0

        for response in self.responses.values():
            type_key = response.response_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            by_status[response.status] = by_status.get(response.status, 0) + 1

            if response.eta_seconds:
                avg_eta += response.eta_seconds
                eta_count += 1

        return {
            "total_responses": total,
            "by_type": by_type,
            "by_status": by_status,
            "average_eta_seconds": avg_eta / max(1, eta_count),
            "available_robots": len(self.available_units["robots"]),
            "available_drones": len(self.available_units["drones"]),
            "active_responses": len(self.get_active_responses()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


__all__ = [
    "ThermalSensorGrid",
    "MotionRadarIngestor",
    "PerimeterBreachDetector",
    "AutoResponseEngine",
    "ThermalReading",
    "MotionEvent",
    "PerimeterBreach",
    "AutoResponse",
    "SensorZone",
    "SensorZoneType",
    "BreachSeverity",
    "ResponseType",
    "MotionEventType",
    "ThermalSignatureType",
]
