"""
Phase 21: Multi-Incident Command Module

Incident room management, AI incident brief building, task assignment,
timeline synchronization, and multi-agency EOC coordination.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class IncidentStatus(Enum):
    ACTIVE = "active"
    MONITORING = "monitoring"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgencyType(Enum):
    POLICE = "police"
    FIRE = "fire"
    EMS = "ems"
    EMERGENCY_MANAGEMENT = "emergency_management"
    PUBLIC_WORKS = "public_works"
    UTILITIES = "utilities"
    NATIONAL_GUARD = "national_guard"
    FEMA = "fema"
    RED_CROSS = "red_cross"
    HEALTH_DEPARTMENT = "health_department"
    TRANSPORTATION = "transportation"


class TimelineEventType(Enum):
    INCIDENT_CREATED = "incident_created"
    STATUS_CHANGE = "status_change"
    RESOURCE_DEPLOYED = "resource_deployed"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    BRIEFING = "briefing"
    SITUATION_UPDATE = "situation_update"
    EVACUATION_ORDER = "evacuation_order"
    SHELTER_OPENED = "shelter_opened"
    CASUALTY_REPORT = "casualty_report"
    INFRASTRUCTURE_UPDATE = "infrastructure_update"
    WEATHER_UPDATE = "weather_update"
    AGENCY_JOINED = "agency_joined"


@dataclass
class IncidentRoom:
    room_id: str
    incident_name: str
    incident_type: str
    status: IncidentStatus
    priority: IncidentPriority
    location: Dict[str, Any]
    description: str
    commander: str
    agencies_involved: List[str]
    affected_population: int
    casualties: Dict[str, int]
    resources_deployed: Dict[str, int]
    active_tasks: int
    completed_tasks: int
    created_at: datetime
    last_briefing: Optional[datetime]
    estimated_resolution: Optional[datetime]
    notes: str


@dataclass
class IncidentBrief:
    brief_id: str
    room_id: str
    brief_type: str
    title: str
    situation_summary: str
    current_status: Dict[str, Any]
    key_developments: List[str]
    resource_status: Dict[str, Any]
    casualties_summary: Dict[str, int]
    immediate_priorities: List[str]
    pending_decisions: List[str]
    next_briefing: Optional[datetime]
    generated_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Task:
    task_id: str
    room_id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to: Optional[str]
    assigned_agency: Optional[str]
    due_time: Optional[datetime]
    dependencies: List[str]
    resources_required: List[str]
    location: Optional[Dict[str, Any]]
    completion_criteria: str
    notes: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class TimelineEvent:
    event_id: str
    room_id: str
    event_type: TimelineEventType
    title: str
    description: str
    data: Dict[str, Any]
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Agency:
    agency_id: str
    name: str
    agency_type: AgencyType
    jurisdiction: str
    contact_info: Dict[str, str]
    resources_available: Dict[str, int]
    personnel_available: int
    capabilities: List[str]
    current_assignments: List[str]
    liaison_officer: Optional[str]
    joined_at: Optional[datetime]


@dataclass
class EOCStatus:
    eoc_id: str
    name: str
    activation_level: int
    status: str
    agencies_present: List[str]
    active_incidents: int
    personnel_on_duty: int
    last_briefing: Optional[datetime]
    next_briefing: Optional[datetime]
    communications_status: str
    backup_eoc_ready: bool


class IncidentRoomManager:
    """
    Manages incident command rooms for emergency operations.
    """

    def __init__(self):
        self._rooms: Dict[str, IncidentRoom] = {}
        self._briefs: Dict[str, IncidentBrief] = {}

    def create_room(
        self,
        incident_name: str,
        incident_type: str,
        priority: str,
        location: Dict[str, Any],
        description: str,
        commander: str,
    ) -> IncidentRoom:
        """Create a new incident command room."""
        room_id = f"room-{uuid.uuid4().hex[:8]}"

        prio_enum = IncidentPriority(priority) if priority in [p.value for p in IncidentPriority] else IncidentPriority.MEDIUM

        room = IncidentRoom(
            room_id=room_id,
            incident_name=incident_name,
            incident_type=incident_type,
            status=IncidentStatus.ACTIVE,
            priority=prio_enum,
            location=location,
            description=description,
            commander=commander,
            agencies_involved=[],
            affected_population=0,
            casualties={"fatalities": 0, "injuries": 0, "missing": 0},
            resources_deployed={"personnel": 0, "vehicles": 0, "equipment": 0},
            active_tasks=0,
            completed_tasks=0,
            created_at=datetime.utcnow(),
            last_briefing=None,
            estimated_resolution=None,
            notes="",
        )

        self._rooms[room_id] = room
        return room

    def update_room_status(
        self,
        room_id: str,
        status: str,
        affected_population: Optional[int] = None,
        casualties: Optional[Dict[str, int]] = None,
        resources_deployed: Optional[Dict[str, int]] = None,
    ) -> IncidentRoom:
        """Update incident room status."""
        room = self._rooms.get(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        if status:
            room.status = IncidentStatus(status) if status in [s.value for s in IncidentStatus] else room.status
        if affected_population is not None:
            room.affected_population = affected_population
        if casualties:
            room.casualties.update(casualties)
        if resources_deployed:
            room.resources_deployed.update(resources_deployed)

        return room

    def add_agency(self, room_id: str, agency_name: str) -> IncidentRoom:
        """Add an agency to the incident room."""
        room = self._rooms.get(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        if agency_name not in room.agencies_involved:
            room.agencies_involved.append(agency_name)

        return room

    def close_room(self, room_id: str) -> IncidentRoom:
        """Close an incident room."""
        room = self._rooms.get(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        room.status = IncidentStatus.CLOSED
        return room

    def get_room(self, room_id: str) -> Optional[IncidentRoom]:
        """Get incident room by ID."""
        return self._rooms.get(room_id)

    def get_rooms(
        self,
        status: Optional[IncidentStatus] = None,
        priority: Optional[IncidentPriority] = None,
    ) -> List[IncidentRoom]:
        """Get incident rooms, optionally filtered."""
        rooms = list(self._rooms.values())
        if status:
            rooms = [r for r in rooms if r.status == status]
        if priority:
            rooms = [r for r in rooms if r.priority == priority]
        return rooms

    def get_active_rooms(self) -> List[IncidentRoom]:
        """Get all active incident rooms."""
        return [r for r in self._rooms.values() if r.status == IncidentStatus.ACTIVE]

    def get_metrics(self) -> Dict[str, Any]:
        """Get incident room metrics."""
        rooms = list(self._rooms.values())
        return {
            "total_rooms": len(rooms),
            "active_rooms": len(self.get_active_rooms()),
            "by_status": {
                s.value: len([r for r in rooms if r.status == s])
                for s in IncidentStatus
            },
            "by_priority": {
                p.value: len([r for r in rooms if r.priority == p])
                for p in IncidentPriority
            },
            "total_affected_population": sum(r.affected_population for r in rooms),
            "total_casualties": sum(sum(r.casualties.values()) for r in rooms),
        }


class AIIncidentBriefBuilder:
    """
    AI-powered incident brief generation.
    """

    def __init__(self, room_manager: IncidentRoomManager):
        self._room_manager = room_manager
        self._briefs: Dict[str, IncidentBrief] = {}

    def generate_brief(
        self,
        room_id: str,
        brief_type: str = "situation",
    ) -> IncidentBrief:
        """Generate an AI-powered incident brief."""
        brief_id = f"brief-{uuid.uuid4().hex[:8]}"

        room = self._room_manager.get_room(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")

        situation_summary = self._generate_situation_summary(room)
        key_developments = self._identify_key_developments(room)
        immediate_priorities = self._determine_priorities(room)
        pending_decisions = self._identify_pending_decisions(room)

        brief = IncidentBrief(
            brief_id=brief_id,
            room_id=room_id,
            brief_type=brief_type,
            title=f"{room.incident_name} - {brief_type.title()} Brief",
            situation_summary=situation_summary,
            current_status={
                "incident_status": room.status.value,
                "priority": room.priority.value,
                "agencies_involved": len(room.agencies_involved),
                "active_tasks": room.active_tasks,
            },
            key_developments=key_developments,
            resource_status=room.resources_deployed,
            casualties_summary=room.casualties,
            immediate_priorities=immediate_priorities,
            pending_decisions=pending_decisions,
            next_briefing=datetime.utcnow() + timedelta(hours=2),
            generated_by="AI Brief Builder",
        )

        self._briefs[brief_id] = brief
        room.last_briefing = datetime.utcnow()

        return brief

    def _generate_situation_summary(self, room: IncidentRoom) -> str:
        """Generate situation summary."""
        return (
            f"{room.incident_name} ({room.incident_type}) is currently {room.status.value}. "
            f"Approximately {room.affected_population:,} people are affected. "
            f"{len(room.agencies_involved)} agencies are involved in the response. "
            f"Current casualties: {room.casualties.get('fatalities', 0)} fatalities, "
            f"{room.casualties.get('injuries', 0)} injuries, {room.casualties.get('missing', 0)} missing."
        )

    def _identify_key_developments(self, room: IncidentRoom) -> List[str]:
        """Identify key developments."""
        developments = []

        if room.casualties.get("fatalities", 0) > 0:
            developments.append(f"Confirmed {room.casualties['fatalities']} fatalities")

        if room.affected_population > 10000:
            developments.append(f"Large-scale impact: {room.affected_population:,} affected")

        if len(room.agencies_involved) > 3:
            developments.append(f"Multi-agency response activated with {len(room.agencies_involved)} agencies")

        if room.resources_deployed.get("personnel", 0) > 100:
            developments.append(f"{room.resources_deployed['personnel']} personnel deployed")

        return developments

    def _determine_priorities(self, room: IncidentRoom) -> List[str]:
        """Determine immediate priorities."""
        priorities = []

        if room.casualties.get("missing", 0) > 0:
            priorities.append("Search and rescue operations for missing persons")

        if room.casualties.get("injuries", 0) > 0:
            priorities.append("Medical treatment for injured")

        if room.affected_population > 5000:
            priorities.append("Shelter and evacuation support")

        priorities.append("Maintain situational awareness")
        priorities.append("Coordinate inter-agency communications")

        return priorities

    def _identify_pending_decisions(self, room: IncidentRoom) -> List[str]:
        """Identify pending decisions."""
        decisions = []

        if room.status == IncidentStatus.ACTIVE:
            decisions.append("Evaluate need for additional resources")
            decisions.append("Assess evacuation zone expansion")

        if room.priority == IncidentPriority.CRITICAL:
            decisions.append("Request state/federal assistance")

        return decisions

    def get_brief(self, brief_id: str) -> Optional[IncidentBrief]:
        """Get brief by ID."""
        return self._briefs.get(brief_id)

    def get_room_briefs(self, room_id: str) -> List[IncidentBrief]:
        """Get all briefs for a room."""
        return [b for b in self._briefs.values() if b.room_id == room_id]


class TaskAssignmentEngine:
    """
    Manages task assignment and tracking for incidents.
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def create_task(
        self,
        room_id: str,
        title: str,
        description: str,
        priority: str,
        due_time: Optional[datetime] = None,
        dependencies: Optional[List[str]] = None,
        resources_required: Optional[List[str]] = None,
        location: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Create a new task."""
        task_id = f"task-{uuid.uuid4().hex[:8]}"

        prio_enum = TaskPriority(priority) if priority in [p.value for p in TaskPriority] else TaskPriority.MEDIUM

        task = Task(
            task_id=task_id,
            room_id=room_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=prio_enum,
            assigned_to=None,
            assigned_agency=None,
            due_time=due_time,
            dependencies=dependencies or [],
            resources_required=resources_required or [],
            location=location,
            completion_criteria="",
            notes="",
        )

        self._tasks[task_id] = task
        return task

    def assign_task(
        self,
        task_id: str,
        assigned_to: str,
        assigned_agency: str,
    ) -> Task:
        """Assign a task to a person/agency."""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.assigned_to = assigned_to
        task.assigned_agency = assigned_agency
        task.status = TaskStatus.ASSIGNED

        return task

    def start_task(self, task_id: str) -> Task:
        """Mark task as in progress."""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()

        return task

    def complete_task(self, task_id: str, notes: str = "") -> Task:
        """Mark task as completed."""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.notes = notes

        return task

    def block_task(self, task_id: str, reason: str) -> Task:
        """Mark task as blocked."""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.BLOCKED
        task.notes = f"Blocked: {reason}"

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)

    def get_room_tasks(
        self,
        room_id: str,
        status: Optional[TaskStatus] = None,
    ) -> List[Task]:
        """Get tasks for a room, optionally filtered by status."""
        tasks = [t for t in self._tasks.values() if t.room_id == room_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def get_pending_tasks(self, room_id: str) -> List[Task]:
        """Get pending tasks for a room."""
        return self.get_room_tasks(room_id, TaskStatus.PENDING)

    def get_overdue_tasks(self, room_id: str) -> List[Task]:
        """Get overdue tasks for a room."""
        now = datetime.utcnow()
        return [
            t for t in self._tasks.values()
            if t.room_id == room_id
            and t.due_time
            and t.due_time < now
            and t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
        ]

    def auto_assign_tasks(
        self,
        room_id: str,
        available_resources: List[Dict[str, Any]],
    ) -> List[Task]:
        """Auto-assign pending tasks based on available resources."""
        pending = self.get_pending_tasks(room_id)
        assigned = []

        for task in pending:
            for resource in available_resources:
                if self._can_handle_task(resource, task):
                    self.assign_task(
                        task.task_id,
                        resource.get("name", ""),
                        resource.get("agency", ""),
                    )
                    assigned.append(task)
                    break

        return assigned

    def _can_handle_task(self, resource: Dict[str, Any], task: Task) -> bool:
        """Check if resource can handle task."""
        resource_capabilities = resource.get("capabilities", [])
        for req in task.resources_required:
            if req not in resource_capabilities:
                return False
        return True

    def get_metrics(self, room_id: Optional[str] = None) -> Dict[str, Any]:
        """Get task metrics."""
        tasks = list(self._tasks.values())
        if room_id:
            tasks = [t for t in tasks if t.room_id == room_id]

        return {
            "total_tasks": len(tasks),
            "by_status": {
                s.value: len([t for t in tasks if t.status == s])
                for s in TaskStatus
            },
            "by_priority": {
                p.value: len([t for t in tasks if t.priority == p])
                for p in TaskPriority
            },
            "overdue_count": len([
                t for t in tasks
                if t.due_time and t.due_time < datetime.utcnow()
                and t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
            ]),
        }


class TimelineSync:
    """
    Synchronizes incident timeline across all participants.
    """

    def __init__(self):
        self._events: Dict[str, TimelineEvent] = {}

    def add_event(
        self,
        room_id: str,
        event_type: str,
        title: str,
        description: str,
        data: Optional[Dict[str, Any]] = None,
        source: str = "System",
    ) -> TimelineEvent:
        """Add an event to the timeline."""
        event_id = f"event-{uuid.uuid4().hex[:8]}"

        type_enum = TimelineEventType(event_type) if event_type in [t.value for t in TimelineEventType] else TimelineEventType.SITUATION_UPDATE

        event = TimelineEvent(
            event_id=event_id,
            room_id=room_id,
            event_type=type_enum,
            title=title,
            description=description,
            data=data or {},
            source=source,
        )

        self._events[event_id] = event
        return event

    def get_event(self, event_id: str) -> Optional[TimelineEvent]:
        """Get event by ID."""
        return self._events.get(event_id)

    def get_room_timeline(
        self,
        room_id: str,
        event_type: Optional[TimelineEventType] = None,
        since: Optional[datetime] = None,
    ) -> List[TimelineEvent]:
        """Get timeline events for a room."""
        events = [e for e in self._events.values() if e.room_id == room_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    def get_recent_events(self, room_id: str, limit: int = 10) -> List[TimelineEvent]:
        """Get most recent events for a room."""
        events = self.get_room_timeline(room_id)
        return events[:limit]


class MultiAgencyEOCCoordinator:
    """
    Coordinates multi-agency Emergency Operations Center activities.
    """

    def __init__(self):
        self._agencies: Dict[str, Agency] = {}
        self._eoc_status: Optional[EOCStatus] = None

    def register_agency(
        self,
        name: str,
        agency_type: str,
        jurisdiction: str,
        contact_info: Dict[str, str],
        resources_available: Optional[Dict[str, int]] = None,
        personnel_available: int = 0,
        capabilities: Optional[List[str]] = None,
    ) -> Agency:
        """Register an agency for EOC coordination."""
        agency_id = f"agency-{uuid.uuid4().hex[:8]}"

        type_enum = AgencyType(agency_type) if agency_type in [t.value for t in AgencyType] else AgencyType.EMERGENCY_MANAGEMENT

        agency = Agency(
            agency_id=agency_id,
            name=name,
            agency_type=type_enum,
            jurisdiction=jurisdiction,
            contact_info=contact_info,
            resources_available=resources_available or {},
            personnel_available=personnel_available,
            capabilities=capabilities or [],
            current_assignments=[],
            liaison_officer=None,
            joined_at=None,
        )

        self._agencies[agency_id] = agency
        return agency

    def activate_eoc(
        self,
        name: str,
        activation_level: int,
    ) -> EOCStatus:
        """Activate the Emergency Operations Center."""
        eoc_id = f"eoc-{uuid.uuid4().hex[:8]}"

        self._eoc_status = EOCStatus(
            eoc_id=eoc_id,
            name=name,
            activation_level=activation_level,
            status="active",
            agencies_present=[],
            active_incidents=0,
            personnel_on_duty=0,
            last_briefing=None,
            next_briefing=datetime.utcnow() + timedelta(hours=2),
            communications_status="operational",
            backup_eoc_ready=True,
        )

        return self._eoc_status

    def join_eoc(
        self,
        agency_id: str,
        liaison_officer: str,
    ) -> Agency:
        """Add an agency to the EOC."""
        agency = self._agencies.get(agency_id)
        if not agency:
            raise ValueError(f"Agency {agency_id} not found")

        agency.liaison_officer = liaison_officer
        agency.joined_at = datetime.utcnow()

        if self._eoc_status and agency.name not in self._eoc_status.agencies_present:
            self._eoc_status.agencies_present.append(agency.name)

        return agency

    def update_eoc_status(
        self,
        activation_level: Optional[int] = None,
        personnel_on_duty: Optional[int] = None,
        active_incidents: Optional[int] = None,
    ) -> EOCStatus:
        """Update EOC status."""
        if not self._eoc_status:
            raise ValueError("EOC not activated")

        if activation_level is not None:
            self._eoc_status.activation_level = activation_level
        if personnel_on_duty is not None:
            self._eoc_status.personnel_on_duty = personnel_on_duty
        if active_incidents is not None:
            self._eoc_status.active_incidents = active_incidents

        return self._eoc_status

    def request_resources(
        self,
        requesting_agency: str,
        resource_type: str,
        quantity: int,
        priority: str,
    ) -> Dict[str, Any]:
        """Request resources from other agencies."""
        request_id = f"req-{uuid.uuid4().hex[:8]}"

        available_agencies = []
        for agency in self._agencies.values():
            if agency.resources_available.get(resource_type, 0) >= quantity:
                available_agencies.append({
                    "agency_id": agency.agency_id,
                    "agency_name": agency.name,
                    "available": agency.resources_available.get(resource_type, 0),
                })

        return {
            "request_id": request_id,
            "requesting_agency": requesting_agency,
            "resource_type": resource_type,
            "quantity": quantity,
            "priority": priority,
            "available_from": available_agencies,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

    def get_agency(self, agency_id: str) -> Optional[Agency]:
        """Get agency by ID."""
        return self._agencies.get(agency_id)

    def get_agencies(self, agency_type: Optional[AgencyType] = None) -> List[Agency]:
        """Get agencies, optionally filtered by type."""
        agencies = list(self._agencies.values())
        if agency_type:
            agencies = [a for a in agencies if a.agency_type == agency_type]
        return agencies

    def get_eoc_status(self) -> Optional[EOCStatus]:
        """Get current EOC status."""
        return self._eoc_status

    def get_metrics(self) -> Dict[str, Any]:
        """Get EOC coordination metrics."""
        agencies = list(self._agencies.values())
        return {
            "total_agencies": len(agencies),
            "agencies_in_eoc": len([a for a in agencies if a.joined_at]),
            "total_personnel": sum(a.personnel_available for a in agencies),
            "by_type": {
                t.value: len([a for a in agencies if a.agency_type == t])
                for t in AgencyType
            },
            "eoc_active": self._eoc_status is not None,
            "eoc_activation_level": self._eoc_status.activation_level if self._eoc_status else 0,
        }


class MultiIncidentCommandManager:
    """
    Main multi-incident command coordinator.
    """

    def __init__(self):
        self.room_manager = IncidentRoomManager()
        self.brief_builder = AIIncidentBriefBuilder(self.room_manager)
        self.task_engine = TaskAssignmentEngine()
        self.timeline = TimelineSync()
        self.eoc_coordinator = MultiAgencyEOCCoordinator()

    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall command metrics."""
        return {
            "incidents": self.room_manager.get_metrics(),
            "tasks": self.task_engine.get_metrics(),
            "eoc": self.eoc_coordinator.get_metrics(),
        }

    def get_command_summary(self) -> Dict[str, Any]:
        """Get command summary."""
        active_rooms = self.room_manager.get_active_rooms()
        return {
            "active_incidents": len(active_rooms),
            "critical_incidents": len([r for r in active_rooms if r.priority == IncidentPriority.CRITICAL]),
            "total_affected_population": sum(r.affected_population for r in active_rooms),
            "total_casualties": sum(sum(r.casualties.values()) for r in active_rooms),
            "agencies_involved": len(set(
                agency for room in active_rooms for agency in room.agencies_involved
            )),
            "eoc_status": self.eoc_coordinator.get_eoc_status(),
        }
