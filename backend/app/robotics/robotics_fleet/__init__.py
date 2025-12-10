"""
Robotics Fleet Module

Provides fleet management capabilities including:
- FleetRegistryService: Robot registration, types, sensors, capabilities
- TelemetryIngestor: Real-time telemetry data (lidar, gps, imu, battery, thermal)
- RoboticsHealthMonitor: Component-level diagnostics, failure prediction
- RoboticsCommandEngine: Movement and action commands
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class RobotType(Enum):
    """Types of autonomous robots."""
    ROBOT_DOG = "robot_dog"
    UGV = "ugv"
    INDOOR_ROBOT = "indoor_robot"
    TRACKED_ROBOT = "tracked_robot"
    WHEELED_ROBOT = "wheeled_robot"
    QUADRUPED = "quadruped"
    HEXAPOD = "hexapod"
    INSPECTION_ROBOT = "inspection_robot"


class RobotStatus(Enum):
    """Robot operational status."""
    IDLE = "idle"
    ACTIVE = "active"
    PATROLLING = "patrolling"
    RESPONDING = "responding"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    ERROR = "error"
    RETURNING = "returning"


class SensorType(Enum):
    """Types of sensors on robots."""
    LIDAR = "lidar"
    GPS = "gps"
    IMU = "imu"
    CAMERA_RGB = "camera_rgb"
    CAMERA_THERMAL = "camera_thermal"
    CAMERA_NIGHT_VISION = "camera_night_vision"
    ULTRASONIC = "ultrasonic"
    RADAR = "radar"
    MICROPHONE = "microphone"
    GAS_DETECTOR = "gas_detector"
    RADIATION_DETECTOR = "radiation_detector"


class CommandType(Enum):
    """Types of robot commands."""
    MOVE = "move"
    STOP = "stop"
    FOLLOW = "follow"
    SEARCH = "search"
    ROOM_SCAN = "room_scan"
    PERIMETER_SWEEP = "perimeter_sweep"
    RETURN_HOME = "return_home"
    CHARGE = "charge"
    PATROL = "patrol"
    INVESTIGATE = "investigate"
    HOLD_POSITION = "hold_position"
    EMERGENCY_STOP = "emergency_stop"


class HealthStatus(Enum):
    """Robot health status levels."""
    OPTIMAL = "optimal"
    GOOD = "good"
    DEGRADED = "degraded"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"


@dataclass
class Robot:
    """Robot registration data."""
    robot_id: str
    name: str
    robot_type: RobotType
    status: RobotStatus
    model: str
    manufacturer: str
    serial_number: str
    firmware_version: str
    sensors: List[SensorType]
    capabilities: List[str]
    max_speed: float
    battery_capacity: float
    current_battery: float
    home_location: Dict[str, float]
    current_location: Optional[Dict[str, float]]
    assigned_zone: Optional[str]
    last_maintenance: str
    next_maintenance: str
    registered_at: str
    last_seen: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RobotTelemetry:
    """Real-time robot telemetry data."""
    telemetry_id: str
    robot_id: str
    timestamp: str
    location: Dict[str, float]
    heading: float
    speed: float
    battery_level: float
    battery_voltage: float
    battery_temperature: float
    motor_temperatures: Dict[str, float]
    lidar_data: Optional[Dict[str, Any]]
    imu_data: Optional[Dict[str, Any]]
    gps_accuracy: float
    signal_strength: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    active_sensors: List[SensorType]
    error_codes: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RobotHealth:
    """Robot health diagnostics."""
    health_id: str
    robot_id: str
    timestamp: str
    overall_status: HealthStatus
    overall_score: float
    component_health: Dict[str, Dict[str, Any]]
    battery_health: float
    motor_health: Dict[str, float]
    sensor_health: Dict[str, float]
    communication_health: float
    software_health: float
    predicted_failures: List[Dict[str, Any]]
    maintenance_recommendations: List[str]
    uptime_hours: float
    total_distance_km: float
    mission_count: int
    last_error: Optional[str]
    last_error_time: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RobotCommand:
    """Robot command data."""
    command_id: str
    robot_id: str
    command_type: CommandType
    parameters: Dict[str, Any]
    priority: int
    issued_by: str
    issued_at: str
    acknowledged_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    status: str
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class FleetRegistryService:
    """Service for managing robot fleet registration."""

    def __init__(self):
        self.robots: Dict[str, Robot] = {}
        self.robot_capabilities: Dict[str, List[str]] = {}

    def register_robot(
        self,
        name: str,
        robot_type: RobotType,
        model: str,
        manufacturer: str,
        serial_number: str,
        firmware_version: str,
        sensors: List[SensorType],
        capabilities: List[str],
        max_speed: float,
        battery_capacity: float,
        home_location: Dict[str, float],
        assigned_zone: Optional[str] = None,
    ) -> Robot:
        """Register a new robot in the fleet."""
        robot_id = f"robot-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        robot = Robot(
            robot_id=robot_id,
            name=name,
            robot_type=robot_type,
            status=RobotStatus.IDLE,
            model=model,
            manufacturer=manufacturer,
            serial_number=serial_number,
            firmware_version=firmware_version,
            sensors=sensors,
            capabilities=capabilities,
            max_speed=max_speed,
            battery_capacity=battery_capacity,
            current_battery=battery_capacity,
            home_location=home_location,
            current_location=home_location.copy(),
            assigned_zone=assigned_zone,
            last_maintenance=timestamp,
            next_maintenance=timestamp,
            registered_at=timestamp,
            last_seen=timestamp,
            metadata={},
        )

        self.robots[robot_id] = robot
        self.robot_capabilities[robot_id] = capabilities

        return robot

    def get_robot(self, robot_id: str) -> Optional[Robot]:
        """Get a robot by ID."""
        return self.robots.get(robot_id)

    def get_robots(
        self,
        robot_type: Optional[RobotType] = None,
        status: Optional[RobotStatus] = None,
        zone: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> List[Robot]:
        """Get robots with optional filtering."""
        robots = list(self.robots.values())

        if robot_type:
            robots = [r for r in robots if r.robot_type == robot_type]

        if status:
            robots = [r for r in robots if r.status == status]

        if zone:
            robots = [r for r in robots if r.assigned_zone == zone]

        if capability:
            robots = [
                r for r in robots
                if capability in self.robot_capabilities.get(r.robot_id, [])
            ]

        return robots

    def update_robot_status(
        self,
        robot_id: str,
        status: RobotStatus,
        location: Optional[Dict[str, float]] = None,
    ) -> bool:
        """Update robot status and optionally location."""
        robot = self.robots.get(robot_id)
        if not robot:
            return False

        robot.status = status
        robot.last_seen = datetime.utcnow().isoformat() + "Z"

        if location:
            robot.current_location = location

        return True

    def update_robot_battery(self, robot_id: str, battery_level: float) -> bool:
        """Update robot battery level."""
        robot = self.robots.get(robot_id)
        if not robot:
            return False

        robot.current_battery = battery_level
        robot.last_seen = datetime.utcnow().isoformat() + "Z"

        return True

    def deregister_robot(self, robot_id: str) -> bool:
        """Remove a robot from the fleet."""
        if robot_id in self.robots:
            del self.robots[robot_id]
            if robot_id in self.robot_capabilities:
                del self.robot_capabilities[robot_id]
            return True
        return False

    def get_available_robots(
        self,
        capability: Optional[str] = None,
        near_location: Optional[Dict[str, float]] = None,
        max_distance: float = 1000.0,
    ) -> List[Robot]:
        """Get available robots, optionally filtered by capability and location."""
        available_statuses = [RobotStatus.IDLE, RobotStatus.PATROLLING]
        robots = [r for r in self.robots.values() if r.status in available_statuses]

        if capability:
            robots = [
                r for r in robots
                if capability in self.robot_capabilities.get(r.robot_id, [])
            ]

        if near_location and robots:
            def distance(r: Robot) -> float:
                if not r.current_location:
                    return float('inf')
                dx = r.current_location.get('x', 0) - near_location.get('x', 0)
                dy = r.current_location.get('y', 0) - near_location.get('y', 0)
                return (dx ** 2 + dy ** 2) ** 0.5

            robots = [r for r in robots if distance(r) <= max_distance]
            robots.sort(key=distance)

        return robots

    def get_fleet_summary(self) -> Dict[str, Any]:
        """Get summary of the entire fleet."""
        total = len(self.robots)
        by_type = {}
        by_status = {}
        low_battery = 0
        needs_maintenance = 0

        for robot in self.robots.values():
            type_key = robot.robot_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            status_key = robot.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            if robot.current_battery < robot.battery_capacity * 0.2:
                low_battery += 1

        return {
            "total_robots": total,
            "by_type": by_type,
            "by_status": by_status,
            "low_battery_count": low_battery,
            "needs_maintenance_count": needs_maintenance,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class TelemetryIngestor:
    """Service for ingesting robot telemetry data."""

    def __init__(self):
        self.telemetry_history: Dict[str, List[RobotTelemetry]] = {}
        self.latest_telemetry: Dict[str, RobotTelemetry] = {}
        self.max_history_per_robot = 1000

    def ingest_telemetry(
        self,
        robot_id: str,
        location: Dict[str, float],
        heading: float,
        speed: float,
        battery_level: float,
        battery_voltage: float,
        battery_temperature: float,
        motor_temperatures: Dict[str, float],
        lidar_data: Optional[Dict[str, Any]] = None,
        imu_data: Optional[Dict[str, Any]] = None,
        gps_accuracy: float = 1.0,
        signal_strength: float = 100.0,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        disk_usage: float = 0.0,
        network_latency: float = 0.0,
        active_sensors: Optional[List[SensorType]] = None,
        error_codes: Optional[List[str]] = None,
    ) -> RobotTelemetry:
        """Ingest telemetry data from a robot."""
        telemetry_id = f"telem-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        telemetry = RobotTelemetry(
            telemetry_id=telemetry_id,
            robot_id=robot_id,
            timestamp=timestamp,
            location=location,
            heading=heading,
            speed=speed,
            battery_level=battery_level,
            battery_voltage=battery_voltage,
            battery_temperature=battery_temperature,
            motor_temperatures=motor_temperatures,
            lidar_data=lidar_data,
            imu_data=imu_data,
            gps_accuracy=gps_accuracy,
            signal_strength=signal_strength,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_latency=network_latency,
            active_sensors=active_sensors or [],
            error_codes=error_codes or [],
            metadata={},
        )

        if robot_id not in self.telemetry_history:
            self.telemetry_history[robot_id] = []

        self.telemetry_history[robot_id].append(telemetry)
        self.latest_telemetry[robot_id] = telemetry

        if len(self.telemetry_history[robot_id]) > self.max_history_per_robot:
            self.telemetry_history[robot_id] = self.telemetry_history[robot_id][-self.max_history_per_robot:]

        return telemetry

    def get_latest_telemetry(self, robot_id: str) -> Optional[RobotTelemetry]:
        """Get the latest telemetry for a robot."""
        return self.latest_telemetry.get(robot_id)

    def get_telemetry_history(
        self,
        robot_id: str,
        limit: int = 100,
        since: Optional[str] = None,
    ) -> List[RobotTelemetry]:
        """Get telemetry history for a robot."""
        history = self.telemetry_history.get(robot_id, [])

        if since:
            history = [t for t in history if t.timestamp >= since]

        return history[-limit:]

    def get_fleet_telemetry(self) -> Dict[str, RobotTelemetry]:
        """Get latest telemetry for all robots."""
        return self.latest_telemetry.copy()


class RoboticsHealthMonitor:
    """Service for monitoring robot health and predicting failures."""

    def __init__(self):
        self.health_records: Dict[str, List[RobotHealth]] = {}
        self.latest_health: Dict[str, RobotHealth] = {}
        self.failure_thresholds = {
            "battery": 0.15,
            "motor": 0.3,
            "sensor": 0.4,
            "communication": 0.5,
        }

    def assess_health(
        self,
        robot_id: str,
        battery_level: float,
        battery_voltage: float,
        motor_temperatures: Dict[str, float],
        sensor_readings: Dict[str, float],
        communication_latency: float,
        cpu_usage: float,
        memory_usage: float,
        uptime_hours: float,
        total_distance_km: float,
        mission_count: int,
        error_codes: Optional[List[str]] = None,
    ) -> RobotHealth:
        """Assess robot health and predict failures."""
        health_id = f"health-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        battery_health = min(1.0, battery_level / 100.0)
        if battery_voltage < 22.0:
            battery_health *= 0.8

        motor_health = {}
        for motor, temp in motor_temperatures.items():
            if temp > 80:
                motor_health[motor] = 0.3
            elif temp > 60:
                motor_health[motor] = 0.6
            elif temp > 40:
                motor_health[motor] = 0.85
            else:
                motor_health[motor] = 1.0

        sensor_health = {}
        for sensor, reading in sensor_readings.items():
            sensor_health[sensor] = min(1.0, max(0.0, reading))

        communication_health = 1.0 - min(1.0, communication_latency / 1000.0)

        software_health = 1.0
        if cpu_usage > 90:
            software_health *= 0.7
        if memory_usage > 90:
            software_health *= 0.8

        component_health = {
            "battery": {"score": battery_health, "status": self._get_status(battery_health)},
            "motors": {"score": sum(motor_health.values()) / max(1, len(motor_health)), "details": motor_health},
            "sensors": {"score": sum(sensor_health.values()) / max(1, len(sensor_health)), "details": sensor_health},
            "communication": {"score": communication_health, "latency_ms": communication_latency},
            "software": {"score": software_health, "cpu": cpu_usage, "memory": memory_usage},
        }

        overall_score = (
            battery_health * 0.25 +
            (sum(motor_health.values()) / max(1, len(motor_health))) * 0.25 +
            (sum(sensor_health.values()) / max(1, len(sensor_health))) * 0.2 +
            communication_health * 0.15 +
            software_health * 0.15
        ) * 100

        overall_status = self._get_health_status(overall_score)

        predicted_failures = []
        maintenance_recommendations = []

        if battery_health < self.failure_thresholds["battery"]:
            predicted_failures.append({
                "component": "battery",
                "probability": 0.8,
                "time_to_failure_hours": 2,
                "severity": "critical",
            })
            maintenance_recommendations.append("Replace or charge battery immediately")

        for motor, health in motor_health.items():
            if health < self.failure_thresholds["motor"]:
                predicted_failures.append({
                    "component": f"motor_{motor}",
                    "probability": 0.6,
                    "time_to_failure_hours": 24,
                    "severity": "high",
                })
                maintenance_recommendations.append(f"Inspect motor {motor} - overheating detected")

        health = RobotHealth(
            health_id=health_id,
            robot_id=robot_id,
            timestamp=timestamp,
            overall_status=overall_status,
            overall_score=overall_score,
            component_health=component_health,
            battery_health=battery_health,
            motor_health=motor_health,
            sensor_health=sensor_health,
            communication_health=communication_health,
            software_health=software_health,
            predicted_failures=predicted_failures,
            maintenance_recommendations=maintenance_recommendations,
            uptime_hours=uptime_hours,
            total_distance_km=total_distance_km,
            mission_count=mission_count,
            last_error=error_codes[0] if error_codes else None,
            last_error_time=timestamp if error_codes else None,
            metadata={},
        )

        if robot_id not in self.health_records:
            self.health_records[robot_id] = []

        self.health_records[robot_id].append(health)
        self.latest_health[robot_id] = health

        return health

    def _get_status(self, score: float) -> str:
        """Get status string from score."""
        if score >= 0.9:
            return "optimal"
        elif score >= 0.7:
            return "good"
        elif score >= 0.5:
            return "degraded"
        elif score >= 0.3:
            return "warning"
        else:
            return "critical"

    def _get_health_status(self, score: float) -> HealthStatus:
        """Get HealthStatus from score."""
        if score >= 90:
            return HealthStatus.OPTIMAL
        elif score >= 70:
            return HealthStatus.GOOD
        elif score >= 50:
            return HealthStatus.DEGRADED
        elif score >= 30:
            return HealthStatus.WARNING
        elif score >= 10:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.FAILED

    def get_latest_health(self, robot_id: str) -> Optional[RobotHealth]:
        """Get latest health assessment for a robot."""
        return self.latest_health.get(robot_id)

    def get_health_history(
        self,
        robot_id: str,
        limit: int = 100,
    ) -> List[RobotHealth]:
        """Get health history for a robot."""
        history = self.health_records.get(robot_id, [])
        return history[-limit:]

    def get_fleet_health_summary(self) -> Dict[str, Any]:
        """Get health summary for the entire fleet."""
        total = len(self.latest_health)
        by_status = {}
        critical_robots = []
        avg_score = 0.0

        for robot_id, health in self.latest_health.items():
            status_key = health.overall_status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            avg_score += health.overall_score

            if health.overall_status in [HealthStatus.CRITICAL, HealthStatus.FAILED]:
                critical_robots.append(robot_id)

        return {
            "total_assessed": total,
            "by_status": by_status,
            "average_score": avg_score / max(1, total),
            "critical_robots": critical_robots,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class RoboticsCommandEngine:
    """Service for issuing and managing robot commands."""

    def __init__(self):
        self.commands: Dict[str, RobotCommand] = {}
        self.command_queue: Dict[str, List[RobotCommand]] = {}
        self.active_commands: Dict[str, RobotCommand] = {}

    def issue_command(
        self,
        robot_id: str,
        command_type: CommandType,
        parameters: Dict[str, Any],
        priority: int = 5,
        issued_by: str = "system",
    ) -> RobotCommand:
        """Issue a command to a robot."""
        command_id = f"cmd-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        command = RobotCommand(
            command_id=command_id,
            robot_id=robot_id,
            command_type=command_type,
            parameters=parameters,
            priority=priority,
            issued_by=issued_by,
            issued_at=timestamp,
            acknowledged_at=None,
            started_at=None,
            completed_at=None,
            status="pending",
            result=None,
            error_message=None,
            metadata={},
        )

        self.commands[command_id] = command

        if robot_id not in self.command_queue:
            self.command_queue[robot_id] = []

        self.command_queue[robot_id].append(command)
        self.command_queue[robot_id].sort(key=lambda c: -c.priority)

        return command

    def acknowledge_command(self, command_id: str) -> bool:
        """Mark a command as acknowledged by the robot."""
        command = self.commands.get(command_id)
        if not command:
            return False

        command.acknowledged_at = datetime.utcnow().isoformat() + "Z"
        command.status = "acknowledged"

        return True

    def start_command(self, command_id: str) -> bool:
        """Mark a command as started."""
        command = self.commands.get(command_id)
        if not command:
            return False

        command.started_at = datetime.utcnow().isoformat() + "Z"
        command.status = "executing"
        self.active_commands[command.robot_id] = command

        return True

    def complete_command(
        self,
        command_id: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Mark a command as completed."""
        command = self.commands.get(command_id)
        if not command:
            return False

        command.completed_at = datetime.utcnow().isoformat() + "Z"
        command.result = result
        command.error_message = error_message
        command.status = "completed" if not error_message else "failed"

        if command.robot_id in self.active_commands:
            if self.active_commands[command.robot_id].command_id == command_id:
                del self.active_commands[command.robot_id]

        if command.robot_id in self.command_queue:
            self.command_queue[command.robot_id] = [
                c for c in self.command_queue[command.robot_id]
                if c.command_id != command_id
            ]

        return True

    def cancel_command(self, command_id: str, reason: str = "cancelled") -> bool:
        """Cancel a pending or executing command."""
        command = self.commands.get(command_id)
        if not command:
            return False

        if command.status in ["completed", "failed", "cancelled"]:
            return False

        command.status = "cancelled"
        command.error_message = reason
        command.completed_at = datetime.utcnow().isoformat() + "Z"

        if command.robot_id in self.active_commands:
            if self.active_commands[command.robot_id].command_id == command_id:
                del self.active_commands[command.robot_id]

        return True

    def get_command(self, command_id: str) -> Optional[RobotCommand]:
        """Get a command by ID."""
        return self.commands.get(command_id)

    def get_robot_commands(
        self,
        robot_id: str,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[RobotCommand]:
        """Get commands for a robot."""
        commands = [c for c in self.commands.values() if c.robot_id == robot_id]

        if status:
            commands = [c for c in commands if c.status == status]

        commands.sort(key=lambda c: c.issued_at, reverse=True)
        return commands[:limit]

    def get_active_command(self, robot_id: str) -> Optional[RobotCommand]:
        """Get the currently active command for a robot."""
        return self.active_commands.get(robot_id)

    def get_command_queue(self, robot_id: str) -> List[RobotCommand]:
        """Get the command queue for a robot."""
        return self.command_queue.get(robot_id, [])

    def emergency_stop_all(self, issued_by: str = "system") -> List[RobotCommand]:
        """Issue emergency stop to all robots."""
        commands = []
        for robot_id in set(self.active_commands.keys()):
            cmd = self.issue_command(
                robot_id=robot_id,
                command_type=CommandType.EMERGENCY_STOP,
                parameters={},
                priority=10,
                issued_by=issued_by,
            )
            commands.append(cmd)
        return commands

    def get_metrics(self) -> Dict[str, Any]:
        """Get command engine metrics."""
        total = len(self.commands)
        by_status = {}
        by_type = {}

        for cmd in self.commands.values():
            by_status[cmd.status] = by_status.get(cmd.status, 0) + 1
            type_key = cmd.command_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

        return {
            "total_commands": total,
            "by_status": by_status,
            "by_type": by_type,
            "active_commands": len(self.active_commands),
            "queued_commands": sum(len(q) for q in self.command_queue.values()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


__all__ = [
    "FleetRegistryService",
    "TelemetryIngestor",
    "RoboticsHealthMonitor",
    "RoboticsCommandEngine",
    "Robot",
    "RobotTelemetry",
    "RobotHealth",
    "RobotCommand",
    "RobotType",
    "RobotStatus",
    "SensorType",
    "CommandType",
    "HealthStatus",
]
