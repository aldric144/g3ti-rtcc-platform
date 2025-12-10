"""
Drone Command Engine.

Handles drone command execution including takeoff, land, orbit,
perimeter patrol, follow-unit, and other flight commands.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class CommandType(str, Enum):
    """Types of drone commands."""
    TAKEOFF = "takeoff"
    LAND = "land"
    RETURN_HOME = "return_home"
    HOVER = "hover"
    ORBIT = "orbit"
    PERIMETER_PATROL = "perimeter_patrol"
    FOLLOW_UNIT = "follow_unit"
    FOLLOW_VEHICLE = "follow_vehicle"
    GO_TO_WAYPOINT = "go_to_waypoint"
    GO_TO_COORDINATES = "go_to_coordinates"
    SEARCH_PATTERN = "search_pattern"
    TRACK_TARGET = "track_target"
    SPOTLIGHT_ON = "spotlight_on"
    SPOTLIGHT_OFF = "spotlight_off"
    SPEAKER_ANNOUNCE = "speaker_announce"
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"
    TAKE_PHOTO = "take_photo"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    GIMBAL_CONTROL = "gimbal_control"
    EMERGENCY_STOP = "emergency_stop"
    ABORT_MISSION = "abort_mission"


class CommandStatus(str, Enum):
    """Command execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class CommandPriority(str, Enum):
    """Command priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class Waypoint(BaseModel):
    """Waypoint for navigation."""
    waypoint_id: str
    latitude: float
    longitude: float
    altitude_m: float
    speed_mps: Optional[float] = None
    hover_time_seconds: float = 0.0
    gimbal_pitch_deg: Optional[float] = None
    action: Optional[str] = None


class DroneCommand(BaseModel):
    """Drone command model."""
    command_id: str
    drone_id: str
    command_type: CommandType
    status: CommandStatus = CommandStatus.PENDING
    priority: CommandPriority = CommandPriority.NORMAL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_seconds: float = 300.0
    target_latitude: Optional[float] = None
    target_longitude: Optional[float] = None
    target_altitude_m: Optional[float] = None
    target_heading_deg: Optional[float] = None
    target_speed_mps: Optional[float] = None
    orbit_radius_m: Optional[float] = None
    orbit_direction: Optional[str] = None
    patrol_waypoints: list[Waypoint] = Field(default_factory=list)
    follow_target_id: Optional[str] = None
    follow_distance_m: Optional[float] = None
    search_area_coords: list[tuple[float, float]] = Field(default_factory=list)
    gimbal_pitch_deg: Optional[float] = None
    gimbal_yaw_deg: Optional[float] = None
    zoom_level: Optional[float] = None
    announcement_text: Optional[str] = None
    operator_id: Optional[str] = None
    mission_id: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommandConfig(BaseModel):
    """Configuration for command engine."""
    max_queue_size: int = 1000
    default_timeout_seconds: float = 300.0
    max_concurrent_commands: int = 10
    command_history_size: int = 10000
    enable_emergency_override: bool = True
    min_altitude_m: float = 10.0
    max_altitude_m: float = 120.0
    max_speed_mps: float = 20.0
    geofence_enabled: bool = True


class CommandMetrics(BaseModel):
    """Metrics for command engine."""
    total_commands: int = 0
    commands_by_type: dict[str, int] = Field(default_factory=dict)
    commands_by_status: dict[str, int] = Field(default_factory=dict)
    pending_commands: int = 0
    executing_commands: int = 0
    completed_commands: int = 0
    failed_commands: int = 0
    avg_execution_time_ms: float = 0.0


class DroneCommandEngine:
    """
    Drone Command Engine.
    
    Handles drone command execution including takeoff, land, orbit,
    perimeter patrol, follow-unit, and other flight commands.
    """
    
    def __init__(self, config: Optional[CommandConfig] = None):
        self.config = config or CommandConfig()
        self._command_queue: dict[str, deque[DroneCommand]] = {}
        self._active_commands: dict[str, DroneCommand] = {}
        self._command_history: deque[DroneCommand] = deque(maxlen=self.config.command_history_size)
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = CommandMetrics()
    
    async def start(self) -> None:
        """Start the command engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the command engine."""
        self._running = False
    
    async def send_command(self, command: DroneCommand) -> DroneCommand:
        """Send a command to a drone."""
        drone_id = command.drone_id
        
        if drone_id not in self._command_queue:
            self._command_queue[drone_id] = deque(maxlen=100)
        
        if command.priority == CommandPriority.EMERGENCY:
            await self._handle_emergency_command(command)
        else:
            command.status = CommandStatus.QUEUED
            self._command_queue[drone_id].append(command)
        
        self._metrics.total_commands += 1
        self._update_metrics()
        
        await self._process_queue(drone_id)
        
        return command
    
    async def takeoff(
        self,
        drone_id: str,
        altitude_m: float = 30.0,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to takeoff."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.TAKEOFF,
            target_altitude_m=min(altitude_m, self.config.max_altitude_m),
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def land(
        self,
        drone_id: str,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to land."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.LAND,
            priority=CommandPriority.HIGH,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def return_home(
        self,
        drone_id: str,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to return to home base."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.RETURN_HOME,
            priority=CommandPriority.HIGH,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def orbit(
        self,
        drone_id: str,
        center_lat: float,
        center_lon: float,
        radius_m: float = 50.0,
        altitude_m: float = 30.0,
        direction: str = "clockwise",
        speed_mps: float = 5.0,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to orbit a point."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.ORBIT,
            target_latitude=center_lat,
            target_longitude=center_lon,
            target_altitude_m=altitude_m,
            orbit_radius_m=radius_m,
            orbit_direction=direction,
            target_speed_mps=speed_mps,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def perimeter_patrol(
        self,
        drone_id: str,
        waypoints: list[Waypoint],
        altitude_m: float = 30.0,
        speed_mps: float = 10.0,
        loops: int = -1,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to patrol a perimeter."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.PERIMETER_PATROL,
            patrol_waypoints=waypoints,
            target_altitude_m=altitude_m,
            target_speed_mps=speed_mps,
            operator_id=operator_id,
            metadata={"loops": loops},
        )
        return await self.send_command(command)
    
    async def follow_unit(
        self,
        drone_id: str,
        unit_id: str,
        distance_m: float = 30.0,
        altitude_m: float = 30.0,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to follow a unit (officer/vehicle)."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.FOLLOW_UNIT,
            follow_target_id=unit_id,
            follow_distance_m=distance_m,
            target_altitude_m=altitude_m,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def follow_vehicle(
        self,
        drone_id: str,
        vehicle_id: str,
        distance_m: float = 50.0,
        altitude_m: float = 40.0,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to follow a vehicle."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.FOLLOW_VEHICLE,
            follow_target_id=vehicle_id,
            follow_distance_m=distance_m,
            target_altitude_m=altitude_m,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def go_to_coordinates(
        self,
        drone_id: str,
        latitude: float,
        longitude: float,
        altitude_m: float = 30.0,
        speed_mps: Optional[float] = None,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to go to specific coordinates."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.GO_TO_COORDINATES,
            target_latitude=latitude,
            target_longitude=longitude,
            target_altitude_m=altitude_m,
            target_speed_mps=speed_mps,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def search_pattern(
        self,
        drone_id: str,
        area_coords: list[tuple[float, float]],
        altitude_m: float = 30.0,
        pattern: str = "grid",
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to execute a search pattern."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.SEARCH_PATTERN,
            search_area_coords=area_coords,
            target_altitude_m=altitude_m,
            operator_id=operator_id,
            metadata={"pattern": pattern},
        )
        return await self.send_command(command)
    
    async def track_target(
        self,
        drone_id: str,
        target_id: str,
        distance_m: float = 30.0,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to track a target."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.TRACK_TARGET,
            follow_target_id=target_id,
            follow_distance_m=distance_m,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def spotlight_control(
        self,
        drone_id: str,
        on: bool,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Control drone spotlight."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.SPOTLIGHT_ON if on else CommandType.SPOTLIGHT_OFF,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def speaker_announce(
        self,
        drone_id: str,
        text: str,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Command drone to make an announcement."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.SPEAKER_ANNOUNCE,
            announcement_text=text,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def gimbal_control(
        self,
        drone_id: str,
        pitch_deg: float,
        yaw_deg: float,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Control drone gimbal."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.GIMBAL_CONTROL,
            gimbal_pitch_deg=pitch_deg,
            gimbal_yaw_deg=yaw_deg,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def emergency_stop(
        self,
        drone_id: str,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Emergency stop command."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.EMERGENCY_STOP,
            priority=CommandPriority.EMERGENCY,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def abort_mission(
        self,
        drone_id: str,
        operator_id: Optional[str] = None,
    ) -> DroneCommand:
        """Abort current mission."""
        command = DroneCommand(
            command_id=f"cmd-{uuid.uuid4().hex[:12]}",
            drone_id=drone_id,
            command_type=CommandType.ABORT_MISSION,
            priority=CommandPriority.URGENT,
            operator_id=operator_id,
        )
        return await self.send_command(command)
    
    async def cancel_command(self, command_id: str) -> bool:
        """Cancel a pending or queued command."""
        for drone_id, queue in self._command_queue.items():
            for cmd in queue:
                if cmd.command_id == command_id:
                    if cmd.status in [CommandStatus.PENDING, CommandStatus.QUEUED]:
                        cmd.status = CommandStatus.CANCELLED
                        self._command_history.append(cmd)
                        self._update_metrics()
                        return True
        return False
    
    def get_command(self, command_id: str) -> Optional[DroneCommand]:
        """Get a command by ID."""
        for drone_id, queue in self._command_queue.items():
            for cmd in queue:
                if cmd.command_id == command_id:
                    return cmd
        
        if command_id in [c.command_id for c in self._command_history]:
            for cmd in self._command_history:
                if cmd.command_id == command_id:
                    return cmd
        
        return None
    
    def get_active_command(self, drone_id: str) -> Optional[DroneCommand]:
        """Get active command for a drone."""
        return self._active_commands.get(drone_id)
    
    def get_queued_commands(self, drone_id: str) -> list[DroneCommand]:
        """Get queued commands for a drone."""
        if drone_id not in self._command_queue:
            return []
        return list(self._command_queue[drone_id])
    
    def get_command_history(self, limit: int = 100) -> list[DroneCommand]:
        """Get command history."""
        history = list(self._command_history)
        history.reverse()
        return history[:limit]
    
    def get_metrics(self) -> CommandMetrics:
        """Get command metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get command engine status."""
        return {
            "running": self._running,
            "pending_commands": self._metrics.pending_commands,
            "executing_commands": self._metrics.executing_commands,
            "total_commands": self._metrics.total_commands,
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for command events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def _process_queue(self, drone_id: str) -> None:
        """Process command queue for a drone."""
        if drone_id not in self._command_queue:
            return
        
        if drone_id in self._active_commands:
            return
        
        queue = self._command_queue[drone_id]
        if not queue:
            return
        
        command = queue.popleft()
        await self._execute_command(command)
    
    async def _execute_command(self, command: DroneCommand) -> None:
        """Execute a command."""
        command.status = CommandStatus.EXECUTING
        command.started_at = datetime.now(timezone.utc)
        self._active_commands[command.drone_id] = command
        
        self._update_metrics()
        await self._notify_callbacks(command, "started")
        
        command.status = CommandStatus.COMPLETED
        command.completed_at = datetime.now(timezone.utc)
        command.result = {"success": True}
        
        del self._active_commands[command.drone_id]
        self._command_history.append(command)
        
        self._update_metrics()
        await self._notify_callbacks(command, "completed")
    
    async def _handle_emergency_command(self, command: DroneCommand) -> None:
        """Handle emergency command with override."""
        drone_id = command.drone_id
        
        if drone_id in self._active_commands:
            active = self._active_commands[drone_id]
            active.status = CommandStatus.CANCELLED
            active.error_message = "Cancelled by emergency command"
            self._command_history.append(active)
            del self._active_commands[drone_id]
        
        if drone_id in self._command_queue:
            for cmd in self._command_queue[drone_id]:
                cmd.status = CommandStatus.CANCELLED
                cmd.error_message = "Cancelled by emergency command"
                self._command_history.append(cmd)
            self._command_queue[drone_id].clear()
        
        await self._execute_command(command)
    
    def _update_metrics(self) -> None:
        """Update command metrics."""
        pending = 0
        executing = len(self._active_commands)
        
        for queue in self._command_queue.values():
            pending += len(queue)
        
        completed = 0
        failed = 0
        type_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        
        for cmd in self._command_history:
            type_counts[cmd.command_type.value] = type_counts.get(cmd.command_type.value, 0) + 1
            status_counts[cmd.status.value] = status_counts.get(cmd.status.value, 0) + 1
            if cmd.status == CommandStatus.COMPLETED:
                completed += 1
            elif cmd.status == CommandStatus.FAILED:
                failed += 1
        
        self._metrics.pending_commands = pending
        self._metrics.executing_commands = executing
        self._metrics.completed_commands = completed
        self._metrics.failed_commands = failed
        self._metrics.commands_by_type = type_counts
        self._metrics.commands_by_status = status_counts
    
    async def _notify_callbacks(self, command: DroneCommand, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(command, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
