"""
Robotics Mission Engine Module

Provides mission planning and execution capabilities including:
- MissionPlanner: Waypoint-based mission planning
- MissionAutoDispatcher: Automatic dispatch based on triggers
- RoboticsTimelineBuilder: Mission replay and logging
- StreamingEndpoints: Video/audio streaming stubs
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class MissionStatus(Enum):
    """Mission status."""
    DRAFT = "draft"
    PLANNED = "planned"
    QUEUED = "queued"
    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class MissionType(Enum):
    """Types of missions."""
    PATROL = "patrol"
    SEARCH = "search"
    INVESTIGATE = "investigate"
    RESPOND = "respond"
    ESCORT = "escort"
    SURVEILLANCE = "surveillance"
    PERIMETER_CHECK = "perimeter_check"
    DELIVERY = "delivery"
    CUSTOM = "custom"


class DispatchTrigger(Enum):
    """Triggers for auto-dispatch."""
    SHOTSPOTTER = "shotspotter"
    CRASH_DETECTION = "crash_detection"
    DANGEROUS_KEYWORD_911 = "dangerous_keyword_911"
    OFFICER_DISTRESS = "officer_distress"
    AMBUSH_WARNING = "ambush_warning"
    PERIMETER_BREACH = "perimeter_breach"
    HOT_VEHICLE_LPR = "hot_vehicle_lpr"
    MISSING_PERSON = "missing_person"
    ALARM_ACTIVATION = "alarm_activation"
    MANUAL = "manual"


class WaypointType(Enum):
    """Types of waypoints."""
    NAVIGATE = "navigate"
    SCAN = "scan"
    HOLD = "hold"
    INVESTIGATE = "investigate"
    RECORD = "record"
    RETURN = "return"


class TimelineEventType(Enum):
    """Types of timeline events."""
    MISSION_CREATED = "mission_created"
    MISSION_STARTED = "mission_started"
    WAYPOINT_REACHED = "waypoint_reached"
    WAYPOINT_COMPLETED = "waypoint_completed"
    DETECTION = "detection"
    ALERT = "alert"
    COMMAND_RECEIVED = "command_received"
    STATUS_CHANGE = "status_change"
    MISSION_COMPLETED = "mission_completed"
    MISSION_ABORTED = "mission_aborted"
    ERROR = "error"


@dataclass
class MissionWaypoint:
    """Waypoint in a mission."""
    waypoint_id: str
    sequence: int
    waypoint_type: WaypointType
    position: Dict[str, float]
    heading: Optional[float]
    duration_seconds: Optional[float]
    actions: List[str]
    parameters: Dict[str, Any]
    is_completed: bool
    completed_at: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Mission:
    """Robotics mission."""
    mission_id: str
    name: str
    mission_type: MissionType
    status: MissionStatus
    assigned_robots: List[str]
    assigned_swarm: Optional[str]
    waypoints: List[MissionWaypoint]
    trigger: DispatchTrigger
    trigger_event_id: Optional[str]
    priority: int
    start_position: Dict[str, float]
    end_position: Optional[Dict[str, float]]
    created_at: str
    created_by: str
    started_at: Optional[str]
    completed_at: Optional[str]
    estimated_duration_minutes: float
    actual_duration_minutes: Optional[float]
    result: Optional[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MissionEvent:
    """Event in mission timeline."""
    event_id: str
    mission_id: str
    event_type: TimelineEventType
    timestamp: str
    robot_id: Optional[str]
    waypoint_id: Optional[str]
    position: Optional[Dict[str, float]]
    description: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DispatchRule:
    """Rule for auto-dispatch."""
    rule_id: str
    name: str
    trigger: DispatchTrigger
    mission_type: MissionType
    priority: int
    robot_requirements: Dict[str, Any]
    is_active: bool
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamingSession:
    """Video/audio streaming session."""
    session_id: str
    robot_id: str
    mission_id: Optional[str]
    stream_type: str
    status: str
    started_at: str
    ended_at: Optional[str]
    endpoint_url: str
    viewers: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class MissionPlanner:
    """Service for planning robotics missions."""

    def __init__(self):
        self.missions: Dict[str, Mission] = {}
        self.mission_templates: Dict[str, Dict[str, Any]] = {}

    def create_mission(
        self,
        name: str,
        mission_type: MissionType,
        start_position: Dict[str, float],
        waypoints: List[Dict[str, Any]],
        assigned_robots: Optional[List[str]] = None,
        assigned_swarm: Optional[str] = None,
        trigger: DispatchTrigger = DispatchTrigger.MANUAL,
        trigger_event_id: Optional[str] = None,
        priority: int = 5,
        created_by: str = "system",
    ) -> Mission:
        """Create a new mission."""
        mission_id = f"mission-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        mission_waypoints = []
        for i, wp_data in enumerate(waypoints):
            waypoint = MissionWaypoint(
                waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
                sequence=i,
                waypoint_type=wp_data.get("type", WaypointType.NAVIGATE),
                position=wp_data.get("position", {}),
                heading=wp_data.get("heading"),
                duration_seconds=wp_data.get("duration"),
                actions=wp_data.get("actions", []),
                parameters=wp_data.get("parameters", {}),
                is_completed=False,
                completed_at=None,
                metadata={},
            )
            mission_waypoints.append(waypoint)

        estimated_duration = self._estimate_duration(mission_waypoints)

        end_position = None
        if mission_waypoints:
            end_position = mission_waypoints[-1].position

        mission = Mission(
            mission_id=mission_id,
            name=name,
            mission_type=mission_type,
            status=MissionStatus.PLANNED,
            assigned_robots=assigned_robots or [],
            assigned_swarm=assigned_swarm,
            waypoints=mission_waypoints,
            trigger=trigger,
            trigger_event_id=trigger_event_id,
            priority=priority,
            start_position=start_position,
            end_position=end_position,
            created_at=timestamp,
            created_by=created_by,
            started_at=None,
            completed_at=None,
            estimated_duration_minutes=estimated_duration,
            actual_duration_minutes=None,
            result=None,
            metadata={},
        )

        self.missions[mission_id] = mission

        return mission

    def _estimate_duration(self, waypoints: List[MissionWaypoint]) -> float:
        """Estimate mission duration in minutes."""
        total_seconds = 0.0
        avg_speed = 1.0

        for i, wp in enumerate(waypoints):
            if wp.duration_seconds:
                total_seconds += wp.duration_seconds

            if i > 0:
                prev_wp = waypoints[i - 1]
                dx = wp.position.get('x', 0) - prev_wp.position.get('x', 0)
                dy = wp.position.get('y', 0) - prev_wp.position.get('y', 0)
                distance = (dx**2 + dy**2) ** 0.5
                total_seconds += distance / avg_speed

        return total_seconds / 60.0

    def start_mission(self, mission_id: str) -> bool:
        """Start a mission."""
        mission = self.missions.get(mission_id)
        if not mission:
            return False

        if mission.status not in [MissionStatus.PLANNED, MissionStatus.QUEUED]:
            return False

        mission.status = MissionStatus.IN_PROGRESS
        mission.started_at = datetime.utcnow().isoformat() + "Z"

        return True

    def pause_mission(self, mission_id: str) -> bool:
        """Pause a mission."""
        mission = self.missions.get(mission_id)
        if not mission:
            return False

        if mission.status != MissionStatus.IN_PROGRESS:
            return False

        mission.status = MissionStatus.PAUSED

        return True

    def resume_mission(self, mission_id: str) -> bool:
        """Resume a paused mission."""
        mission = self.missions.get(mission_id)
        if not mission:
            return False

        if mission.status != MissionStatus.PAUSED:
            return False

        mission.status = MissionStatus.IN_PROGRESS

        return True

    def complete_waypoint(
        self,
        mission_id: str,
        waypoint_id: str,
    ) -> bool:
        """Mark a waypoint as completed."""
        mission = self.missions.get(mission_id)
        if not mission:
            return False

        for wp in mission.waypoints:
            if wp.waypoint_id == waypoint_id:
                wp.is_completed = True
                wp.completed_at = datetime.utcnow().isoformat() + "Z"
                return True

        return False

    def complete_mission(
        self,
        mission_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Complete a mission."""
        mission = self.missions.get(mission_id)
        if not mission:
            return False

        mission.status = MissionStatus.COMPLETED
        mission.completed_at = datetime.utcnow().isoformat() + "Z"
        mission.result = result

        if mission.started_at:
            start = datetime.fromisoformat(mission.started_at.replace('Z', ''))
            end = datetime.fromisoformat(mission.completed_at.replace('Z', ''))
            mission.actual_duration_minutes = (end - start).total_seconds() / 60.0

        return True

    def abort_mission(
        self,
        mission_id: str,
        reason: str,
    ) -> bool:
        """Abort a mission."""
        mission = self.missions.get(mission_id)
        if not mission:
            return False

        if mission.status in [MissionStatus.COMPLETED, MissionStatus.ABORTED]:
            return False

        mission.status = MissionStatus.ABORTED
        mission.completed_at = datetime.utcnow().isoformat() + "Z"
        mission.result = {"abort_reason": reason}

        return True

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Get a mission by ID."""
        return self.missions.get(mission_id)

    def get_missions(
        self,
        status: Optional[MissionStatus] = None,
        mission_type: Optional[MissionType] = None,
        robot_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Mission]:
        """Get missions with filtering."""
        missions = list(self.missions.values())

        if status:
            missions = [m for m in missions if m.status == status]

        if mission_type:
            missions = [m for m in missions if m.mission_type == mission_type]

        if robot_id:
            missions = [m for m in missions if robot_id in m.assigned_robots]

        missions.sort(key=lambda m: m.created_at, reverse=True)
        return missions[:limit]

    def get_active_missions(self) -> List[Mission]:
        """Get currently active missions."""
        active_statuses = [MissionStatus.IN_PROGRESS, MissionStatus.DISPATCHED]
        return [m for m in self.missions.values() if m.status in active_statuses]

    def add_waypoint(
        self,
        mission_id: str,
        waypoint_type: WaypointType,
        position: Dict[str, float],
        sequence: Optional[int] = None,
        heading: Optional[float] = None,
        duration_seconds: Optional[float] = None,
        actions: Optional[List[str]] = None,
    ) -> Optional[MissionWaypoint]:
        """Add a waypoint to a mission."""
        mission = self.missions.get(mission_id)
        if not mission:
            return None

        if mission.status not in [MissionStatus.DRAFT, MissionStatus.PLANNED]:
            return None

        waypoint = MissionWaypoint(
            waypoint_id=f"wp-{uuid.uuid4().hex[:8]}",
            sequence=sequence if sequence is not None else len(mission.waypoints),
            waypoint_type=waypoint_type,
            position=position,
            heading=heading,
            duration_seconds=duration_seconds,
            actions=actions or [],
            parameters={},
            is_completed=False,
            completed_at=None,
            metadata={},
        )

        if sequence is not None and sequence < len(mission.waypoints):
            mission.waypoints.insert(sequence, waypoint)
            for i, wp in enumerate(mission.waypoints):
                wp.sequence = i
        else:
            mission.waypoints.append(waypoint)

        mission.estimated_duration_minutes = self._estimate_duration(mission.waypoints)

        return waypoint

    def create_template(
        self,
        name: str,
        mission_type: MissionType,
        waypoint_offsets: List[Dict[str, Any]],
    ) -> str:
        """Create a mission template."""
        template_id = f"template-{uuid.uuid4().hex[:8]}"

        self.mission_templates[template_id] = {
            "name": name,
            "mission_type": mission_type,
            "waypoint_offsets": waypoint_offsets,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        return template_id

    def create_from_template(
        self,
        template_id: str,
        name: str,
        center_position: Dict[str, float],
        assigned_robots: Optional[List[str]] = None,
        created_by: str = "system",
    ) -> Optional[Mission]:
        """Create a mission from a template."""
        template = self.mission_templates.get(template_id)
        if not template:
            return None

        waypoints = []
        for offset in template["waypoint_offsets"]:
            position = {
                'x': center_position.get('x', 0) + offset.get('offset_x', 0),
                'y': center_position.get('y', 0) + offset.get('offset_y', 0),
                'z': center_position.get('z', 0) + offset.get('offset_z', 0),
            }
            waypoints.append({
                "type": offset.get("type", WaypointType.NAVIGATE),
                "position": position,
                "heading": offset.get("heading"),
                "duration": offset.get("duration"),
                "actions": offset.get("actions", []),
            })

        return self.create_mission(
            name=name,
            mission_type=template["mission_type"],
            start_position=center_position,
            waypoints=waypoints,
            assigned_robots=assigned_robots,
            created_by=created_by,
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get mission planner metrics."""
        total = len(self.missions)
        by_status = {}
        by_type = {}
        avg_duration = 0.0
        completed_count = 0

        for mission in self.missions.values():
            status_key = mission.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            type_key = mission.mission_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            if mission.actual_duration_minutes:
                avg_duration += mission.actual_duration_minutes
                completed_count += 1

        return {
            "total_missions": total,
            "by_status": by_status,
            "by_type": by_type,
            "average_duration_minutes": avg_duration / max(1, completed_count),
            "active_missions": len(self.get_active_missions()),
            "templates_count": len(self.mission_templates),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class MissionAutoDispatcher:
    """Service for automatic mission dispatch based on triggers."""

    def __init__(self, mission_planner: MissionPlanner):
        self.mission_planner = mission_planner
        self.dispatch_rules: Dict[str, DispatchRule] = {}
        self.dispatch_history: List[Dict[str, Any]] = []
        self._init_default_rules()

    def _init_default_rules(self):
        """Initialize default dispatch rules."""
        default_rules = [
            {
                "name": "ShotSpotter Response",
                "trigger": DispatchTrigger.SHOTSPOTTER,
                "mission_type": MissionType.RESPOND,
                "priority": 10,
                "robot_requirements": {"capabilities": ["camera", "audio"]},
            },
            {
                "name": "Crash Investigation",
                "trigger": DispatchTrigger.CRASH_DETECTION,
                "mission_type": MissionType.INVESTIGATE,
                "priority": 8,
                "robot_requirements": {"capabilities": ["camera"]},
            },
            {
                "name": "911 Dangerous Keyword",
                "trigger": DispatchTrigger.DANGEROUS_KEYWORD_911,
                "mission_type": MissionType.RESPOND,
                "priority": 9,
                "robot_requirements": {"capabilities": ["camera", "audio"]},
            },
            {
                "name": "Officer Distress",
                "trigger": DispatchTrigger.OFFICER_DISTRESS,
                "mission_type": MissionType.RESPOND,
                "priority": 10,
                "robot_requirements": {"capabilities": ["camera", "audio", "lights"]},
            },
            {
                "name": "Ambush Warning",
                "trigger": DispatchTrigger.AMBUSH_WARNING,
                "mission_type": MissionType.SURVEILLANCE,
                "priority": 10,
                "robot_requirements": {"capabilities": ["camera", "thermal"]},
            },
            {
                "name": "Perimeter Breach",
                "trigger": DispatchTrigger.PERIMETER_BREACH,
                "mission_type": MissionType.INVESTIGATE,
                "priority": 8,
                "robot_requirements": {"capabilities": ["camera"]},
            },
            {
                "name": "Hot Vehicle LPR",
                "trigger": DispatchTrigger.HOT_VEHICLE_LPR,
                "mission_type": MissionType.SURVEILLANCE,
                "priority": 7,
                "robot_requirements": {"capabilities": ["camera"]},
            },
            {
                "name": "Missing Person Search",
                "trigger": DispatchTrigger.MISSING_PERSON,
                "mission_type": MissionType.SEARCH,
                "priority": 8,
                "robot_requirements": {"capabilities": ["camera", "thermal"]},
            },
        ]

        for rule_data in default_rules:
            self.create_rule(
                name=rule_data["name"],
                trigger=rule_data["trigger"],
                mission_type=rule_data["mission_type"],
                priority=rule_data["priority"],
                robot_requirements=rule_data["robot_requirements"],
            )

    def create_rule(
        self,
        name: str,
        trigger: DispatchTrigger,
        mission_type: MissionType,
        priority: int,
        robot_requirements: Dict[str, Any],
    ) -> DispatchRule:
        """Create a dispatch rule."""
        rule_id = f"rule-{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        rule = DispatchRule(
            rule_id=rule_id,
            name=name,
            trigger=trigger,
            mission_type=mission_type,
            priority=priority,
            robot_requirements=robot_requirements,
            is_active=True,
            created_at=timestamp,
            metadata={},
        )

        self.dispatch_rules[rule_id] = rule

        return rule

    def process_trigger(
        self,
        trigger: DispatchTrigger,
        event_id: str,
        position: Dict[str, float],
        event_data: Dict[str, Any],
        available_robots: List[str],
    ) -> Optional[Mission]:
        """Process a trigger event and dispatch if rules match."""
        matching_rules = [
            r for r in self.dispatch_rules.values()
            if r.trigger == trigger and r.is_active
        ]

        if not matching_rules:
            return None

        best_rule = max(matching_rules, key=lambda r: r.priority)

        waypoints = self._generate_response_waypoints(
            position,
            best_rule.mission_type,
            event_data,
        )

        mission = self.mission_planner.create_mission(
            name=f"Auto: {best_rule.name}",
            mission_type=best_rule.mission_type,
            start_position=position,
            waypoints=waypoints,
            assigned_robots=available_robots[:2],
            trigger=trigger,
            trigger_event_id=event_id,
            priority=best_rule.priority,
            created_by="auto_dispatcher",
        )

        mission.status = MissionStatus.DISPATCHED

        self.dispatch_history.append({
            "mission_id": mission.mission_id,
            "rule_id": best_rule.rule_id,
            "trigger": trigger.value,
            "event_id": event_id,
            "position": position,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        return mission

    def _generate_response_waypoints(
        self,
        position: Dict[str, float],
        mission_type: MissionType,
        event_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate waypoints for a response mission."""
        waypoints = []

        waypoints.append({
            "type": WaypointType.NAVIGATE,
            "position": position,
            "actions": ["approach"],
        })

        if mission_type == MissionType.INVESTIGATE:
            waypoints.append({
                "type": WaypointType.SCAN,
                "position": position,
                "duration": 30,
                "actions": ["scan_360", "record"],
            })
        elif mission_type == MissionType.SEARCH:
            search_radius = event_data.get("search_radius", 50)
            for angle in [0, 90, 180, 270]:
                import math
                offset_x = search_radius * math.cos(math.radians(angle))
                offset_y = search_radius * math.sin(math.radians(angle))
                waypoints.append({
                    "type": WaypointType.SCAN,
                    "position": {
                        'x': position.get('x', 0) + offset_x,
                        'y': position.get('y', 0) + offset_y,
                        'z': position.get('z', 0),
                    },
                    "duration": 15,
                    "actions": ["scan", "record"],
                })
        elif mission_type == MissionType.SURVEILLANCE:
            waypoints.append({
                "type": WaypointType.HOLD,
                "position": {
                    'x': position.get('x', 0) - 10,
                    'y': position.get('y', 0),
                    'z': position.get('z', 0),
                },
                "duration": 120,
                "actions": ["observe", "record"],
            })
        else:
            waypoints.append({
                "type": WaypointType.HOLD,
                "position": position,
                "duration": 60,
                "actions": ["standby"],
            })

        return waypoints

    def get_rule(self, rule_id: str) -> Optional[DispatchRule]:
        """Get a dispatch rule by ID."""
        return self.dispatch_rules.get(rule_id)

    def get_rules(
        self,
        trigger: Optional[DispatchTrigger] = None,
        active_only: bool = False,
    ) -> List[DispatchRule]:
        """Get dispatch rules with filtering."""
        rules = list(self.dispatch_rules.values())

        if trigger:
            rules = [r for r in rules if r.trigger == trigger]

        if active_only:
            rules = [r for r in rules if r.is_active]

        return rules

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a dispatch rule."""
        rule = self.dispatch_rules.get(rule_id)
        if not rule:
            return False

        rule.is_active = True
        return True

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a dispatch rule."""
        rule = self.dispatch_rules.get(rule_id)
        if not rule:
            return False

        rule.is_active = False
        return True

    def get_dispatch_history(
        self,
        trigger: Optional[DispatchTrigger] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get dispatch history."""
        history = self.dispatch_history

        if trigger:
            history = [h for h in history if h["trigger"] == trigger.value]

        return history[-limit:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get auto-dispatcher metrics."""
        by_trigger = {}
        for entry in self.dispatch_history:
            trigger = entry["trigger"]
            by_trigger[trigger] = by_trigger.get(trigger, 0) + 1

        return {
            "total_dispatches": len(self.dispatch_history),
            "by_trigger": by_trigger,
            "active_rules": len([r for r in self.dispatch_rules.values() if r.is_active]),
            "total_rules": len(self.dispatch_rules),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class RoboticsTimelineBuilder:
    """Service for building and managing mission timelines."""

    def __init__(self):
        self.events: Dict[str, List[MissionEvent]] = {}
        self.event_index: Dict[str, MissionEvent] = {}

    def record_event(
        self,
        mission_id: str,
        event_type: TimelineEventType,
        description: str,
        robot_id: Optional[str] = None,
        waypoint_id: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> MissionEvent:
        """Record an event in the mission timeline."""
        event_id = f"event-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        event = MissionEvent(
            event_id=event_id,
            mission_id=mission_id,
            event_type=event_type,
            timestamp=timestamp,
            robot_id=robot_id,
            waypoint_id=waypoint_id,
            position=position,
            description=description,
            data=data or {},
            metadata={},
        )

        if mission_id not in self.events:
            self.events[mission_id] = []

        self.events[mission_id].append(event)
        self.event_index[event_id] = event

        return event

    def get_timeline(
        self,
        mission_id: str,
        event_type: Optional[TimelineEventType] = None,
        robot_id: Optional[str] = None,
    ) -> List[MissionEvent]:
        """Get timeline for a mission."""
        events = self.events.get(mission_id, [])

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if robot_id:
            events = [e for e in events if e.robot_id == robot_id]

        events.sort(key=lambda e: e.timestamp)
        return events

    def get_event(self, event_id: str) -> Optional[MissionEvent]:
        """Get an event by ID."""
        return self.event_index.get(event_id)

    def get_events_in_range(
        self,
        mission_id: str,
        start_time: str,
        end_time: str,
    ) -> List[MissionEvent]:
        """Get events within a time range."""
        events = self.events.get(mission_id, [])

        filtered = [
            e for e in events
            if start_time <= e.timestamp <= end_time
        ]

        filtered.sort(key=lambda e: e.timestamp)
        return filtered

    def get_replay_data(
        self,
        mission_id: str,
        playback_speed: float = 1.0,
    ) -> Dict[str, Any]:
        """Get data for mission replay."""
        events = self.get_timeline(mission_id)

        if not events:
            return {
                "mission_id": mission_id,
                "events": [],
                "duration_seconds": 0,
                "playback_speed": playback_speed,
            }

        start_time = datetime.fromisoformat(events[0].timestamp.replace('Z', ''))
        end_time = datetime.fromisoformat(events[-1].timestamp.replace('Z', ''))
        duration = (end_time - start_time).total_seconds()

        replay_events = []
        for event in events:
            event_time = datetime.fromisoformat(event.timestamp.replace('Z', ''))
            offset = (event_time - start_time).total_seconds()

            replay_events.append({
                "offset_seconds": offset / playback_speed,
                "event_type": event.event_type.value,
                "description": event.description,
                "position": event.position,
                "robot_id": event.robot_id,
                "data": event.data,
            })

        return {
            "mission_id": mission_id,
            "events": replay_events,
            "duration_seconds": duration / playback_speed,
            "playback_speed": playback_speed,
            "start_time": events[0].timestamp,
            "end_time": events[-1].timestamp,
        }

    def export_timeline(
        self,
        mission_id: str,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Export timeline data."""
        events = self.get_timeline(mission_id)

        return {
            "mission_id": mission_id,
            "format": format,
            "event_count": len(events),
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.value,
                    "timestamp": e.timestamp,
                    "robot_id": e.robot_id,
                    "waypoint_id": e.waypoint_id,
                    "position": e.position,
                    "description": e.description,
                    "data": e.data,
                }
                for e in events
            ],
            "exported_at": datetime.utcnow().isoformat() + "Z",
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get timeline metrics."""
        total_events = sum(len(events) for events in self.events.values())
        by_type = {}

        for events in self.events.values():
            for event in events:
                type_key = event.event_type.value
                by_type[type_key] = by_type.get(type_key, 0) + 1

        return {
            "total_missions_tracked": len(self.events),
            "total_events": total_events,
            "by_event_type": by_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class StreamingEndpoints:
    """Service for robot video/audio streaming (stub implementation)."""

    def __init__(self):
        self.sessions: Dict[str, StreamingSession] = {}
        self.active_streams: Dict[str, str] = {}

    def start_stream(
        self,
        robot_id: str,
        stream_type: str = "video",
        mission_id: Optional[str] = None,
    ) -> StreamingSession:
        """Start a streaming session (stub)."""
        session_id = f"stream-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        endpoint_url = f"rtsp://localhost:8554/robot/{robot_id}/{stream_type}"

        session = StreamingSession(
            session_id=session_id,
            robot_id=robot_id,
            mission_id=mission_id,
            stream_type=stream_type,
            status="active",
            started_at=timestamp,
            ended_at=None,
            endpoint_url=endpoint_url,
            viewers=[],
            metadata={},
        )

        self.sessions[session_id] = session
        self.active_streams[robot_id] = session_id

        return session

    def stop_stream(self, session_id: str) -> bool:
        """Stop a streaming session."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.status = "ended"
        session.ended_at = datetime.utcnow().isoformat() + "Z"

        if session.robot_id in self.active_streams:
            if self.active_streams[session.robot_id] == session_id:
                del self.active_streams[session.robot_id]

        return True

    def add_viewer(self, session_id: str, viewer_id: str) -> bool:
        """Add a viewer to a stream."""
        session = self.sessions.get(session_id)
        if not session or session.status != "active":
            return False

        if viewer_id not in session.viewers:
            session.viewers.append(viewer_id)

        return True

    def remove_viewer(self, session_id: str, viewer_id: str) -> bool:
        """Remove a viewer from a stream."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        if viewer_id in session.viewers:
            session.viewers.remove(viewer_id)

        return True

    def get_session(self, session_id: str) -> Optional[StreamingSession]:
        """Get a streaming session by ID."""
        return self.sessions.get(session_id)

    def get_robot_stream(self, robot_id: str) -> Optional[StreamingSession]:
        """Get active stream for a robot."""
        session_id = self.active_streams.get(robot_id)
        if session_id:
            return self.sessions.get(session_id)
        return None

    def get_active_sessions(self) -> List[StreamingSession]:
        """Get all active streaming sessions."""
        return [s for s in self.sessions.values() if s.status == "active"]

    def get_stream_url(
        self,
        robot_id: str,
        stream_type: str = "video",
    ) -> Optional[str]:
        """Get streaming URL for a robot (stub)."""
        session = self.get_robot_stream(robot_id)
        if session and session.stream_type == stream_type:
            return session.endpoint_url

        return f"rtsp://localhost:8554/robot/{robot_id}/{stream_type}"

    def get_metrics(self) -> Dict[str, Any]:
        """Get streaming metrics."""
        active = self.get_active_sessions()
        total_viewers = sum(len(s.viewers) for s in active)

        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len(active),
            "total_viewers": total_viewers,
            "by_stream_type": {
                "video": len([s for s in active if s.stream_type == "video"]),
                "audio": len([s for s in active if s.stream_type == "audio"]),
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


__all__ = [
    "MissionPlanner",
    "MissionAutoDispatcher",
    "RoboticsTimelineBuilder",
    "StreamingEndpoints",
    "Mission",
    "MissionWaypoint",
    "MissionEvent",
    "DispatchRule",
    "StreamingSession",
    "MissionStatus",
    "MissionType",
    "DispatchTrigger",
    "WaypointType",
    "TimelineEventType",
]
