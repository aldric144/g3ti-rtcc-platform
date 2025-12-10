"""
Autonomous Drone Task Force Engine.

Phase 15: Provides autonomous drone operations for RTCC including
fleet management, telemetry ingestion, mission planning, and
auto-dispatch capabilities.
"""

from app.drones.registry import DroneRegistryService, DroneStatus, DroneType, Drone
from app.drones.telemetry import DroneTelemetryIngestor, TelemetryData, TelemetryConfig
from app.drones.commands import DroneCommandEngine, DroneCommand, CommandType, CommandStatus
from app.drones.auto_dispatch import AutoDispatchEngine, DispatchTrigger, DispatchConfig
from app.drones.mission_planner import DroneMissionPlanner, Mission, MissionType, MissionStatus

__all__ = [
    "DroneRegistryService",
    "DroneStatus",
    "DroneType",
    "Drone",
    "DroneTelemetryIngestor",
    "TelemetryData",
    "TelemetryConfig",
    "DroneCommandEngine",
    "DroneCommand",
    "CommandType",
    "CommandStatus",
    "AutoDispatchEngine",
    "DispatchTrigger",
    "DispatchConfig",
    "DroneMissionPlanner",
    "Mission",
    "MissionType",
    "MissionStatus",
]
