"""
Phase 19: Autonomous Tactical Robotics Engine (ATRE)

This module provides national-level autonomous robotics capabilities including:
- Robotics Fleet Management (registration, telemetry, health, commands)
- Autonomy Engine (pathfinding, obstacle avoidance, navigation, patrol patterns)
- Perimeter Security (thermal sensors, motion/radar, breach detection, auto-response)
- Swarm Coordination (routing, formations, task allocation, synchronization)
- Robotics Mission Engine (planning, auto-dispatch, timeline, streaming)
- Robotics Alerts (REST endpoints, WebSocket channels)
"""

from app.robotics.robotics_fleet import (
    FleetRegistryService,
    TelemetryIngestor,
    RoboticsHealthMonitor,
    RoboticsCommandEngine,
    Robot,
    RobotTelemetry,
    RobotHealth,
    RobotCommand,
    RobotType,
    RobotStatus,
    SensorType,
    CommandType,
    HealthStatus,
)

from app.robotics.autonomy_engine import (
    PathfindingEngine,
    ObstacleAvoidanceEngine,
    IndoorNavigationMap,
    PatrolPatternGenerator,
    PathResult,
    Obstacle,
    NavigationMap,
    PatrolPattern,
    PathfindingAlgorithm,
    PatrolPatternType,
)

from app.robotics.perimeter_security import (
    ThermalSensorGrid,
    MotionRadarIngestor,
    PerimeterBreachDetector,
    AutoResponseEngine,
    ThermalReading,
    MotionEvent,
    PerimeterBreach,
    AutoResponse,
    SensorZone,
    BreachSeverity,
)

from app.robotics.swarm_coordination import (
    SwarmRouter,
    SwarmFormationEngine,
    TaskAllocator,
    SwarmTelemetrySynchronizer,
    SwarmUnit,
    SwarmFormation,
    SwarmTask,
    SwarmRole,
    FormationType,
)

from app.robotics.robotics_mission_engine import (
    MissionPlanner,
    MissionAutoDispatcher,
    RoboticsTimelineBuilder,
    StreamingEndpoints,
    Mission,
    MissionWaypoint,
    MissionEvent,
    MissionStatus,
    MissionType,
    DispatchTrigger,
)

from app.robotics.robotics_alerts import (
    RoboticsAlertManager,
    RoboticsAlert,
    AlertPriority,
    AlertCategory,
)

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
    "PathfindingEngine",
    "ObstacleAvoidanceEngine",
    "IndoorNavigationMap",
    "PatrolPatternGenerator",
    "PathResult",
    "Obstacle",
    "NavigationMap",
    "PatrolPattern",
    "PathfindingAlgorithm",
    "PatrolPatternType",
    "ThermalSensorGrid",
    "MotionRadarIngestor",
    "PerimeterBreachDetector",
    "AutoResponseEngine",
    "ThermalReading",
    "MotionEvent",
    "PerimeterBreach",
    "AutoResponse",
    "SensorZone",
    "BreachSeverity",
    "SwarmRouter",
    "SwarmFormationEngine",
    "TaskAllocator",
    "SwarmTelemetrySynchronizer",
    "SwarmUnit",
    "SwarmFormation",
    "SwarmTask",
    "SwarmRole",
    "FormationType",
    "MissionPlanner",
    "MissionAutoDispatcher",
    "RoboticsTimelineBuilder",
    "StreamingEndpoints",
    "Mission",
    "MissionWaypoint",
    "MissionEvent",
    "MissionStatus",
    "MissionType",
    "DispatchTrigger",
    "RoboticsAlertManager",
    "RoboticsAlert",
    "AlertPriority",
    "AlertCategory",
]
