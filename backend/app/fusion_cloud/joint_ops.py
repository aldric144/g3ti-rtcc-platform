"""
JointOpsManager - Multi-agency joint operations for G3TI Fusion Cloud

Manages:
- Multi-agency operation rooms
- Role assignment per jurisdiction
- Shared whiteboard & timeline
- Inter-department unit tracking
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
import uuid


class OperationStatus(str, Enum):
    """Status of a joint operation"""
    PLANNING = "planning"
    BRIEFING = "briefing"
    ACTIVE = "active"
    PAUSED = "paused"
    CONCLUDING = "concluding"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class OperationType(str, Enum):
    """Types of joint operations"""
    PURSUIT = "pursuit"
    INVESTIGATION = "investigation"
    SURVEILLANCE = "surveillance"
    RAID = "raid"
    SEARCH = "search"
    RESCUE = "rescue"
    DISASTER_RESPONSE = "disaster_response"
    CROWD_CONTROL = "crowd_control"
    VIP_PROTECTION = "vip_protection"
    TASK_FORCE = "task_force"
    TRAINING = "training"
    SPECIAL_EVENT = "special_event"
    FUGITIVE_APPREHENSION = "fugitive_apprehension"
    NARCOTICS = "narcotics"
    HUMAN_TRAFFICKING = "human_trafficking"
    CYBER = "cyber"
    TERRORISM = "terrorism"
    CUSTOM = "custom"


class OperationRole(str, Enum):
    """Roles in a joint operation"""
    COMMANDER = "commander"
    DEPUTY_COMMANDER = "deputy_commander"
    OPERATIONS_CHIEF = "operations_chief"
    PLANNING_CHIEF = "planning_chief"
    LOGISTICS_CHIEF = "logistics_chief"
    INTELLIGENCE_OFFICER = "intelligence_officer"
    COMMUNICATIONS_OFFICER = "communications_officer"
    SAFETY_OFFICER = "safety_officer"
    PUBLIC_INFORMATION = "public_information"
    LIAISON_OFFICER = "liaison_officer"
    TEAM_LEADER = "team_leader"
    UNIT_MEMBER = "unit_member"
    OBSERVER = "observer"
    ANALYST = "analyst"
    DISPATCHER = "dispatcher"


class TimelineEventType(str, Enum):
    """Types of timeline events"""
    OPERATION_CREATED = "operation_created"
    OPERATION_STARTED = "operation_started"
    OPERATION_PAUSED = "operation_paused"
    OPERATION_RESUMED = "operation_resumed"
    OPERATION_COMPLETED = "operation_completed"
    AGENCY_JOINED = "agency_joined"
    AGENCY_LEFT = "agency_left"
    UNIT_DEPLOYED = "unit_deployed"
    UNIT_REPOSITIONED = "unit_repositioned"
    UNIT_WITHDRAWN = "unit_withdrawn"
    OBJECTIVE_ADDED = "objective_added"
    OBJECTIVE_COMPLETED = "objective_completed"
    INTEL_RECEIVED = "intel_received"
    SUSPECT_LOCATED = "suspect_located"
    ARREST_MADE = "arrest_made"
    EVIDENCE_COLLECTED = "evidence_collected"
    INCIDENT_REPORTED = "incident_reported"
    COMMUNICATION = "communication"
    DECISION = "decision"
    NOTE = "note"
    ALERT = "alert"
    CUSTOM = "custom"


class WhiteboardItemType(str, Enum):
    """Types of whiteboard items"""
    TEXT = "text"
    IMAGE = "image"
    MAP_MARKER = "map_marker"
    DRAWING = "drawing"
    LINK = "link"
    FILE = "file"
    SUSPECT_CARD = "suspect_card"
    VEHICLE_CARD = "vehicle_card"
    LOCATION_CARD = "location_card"
    TASK = "task"
    CHECKLIST = "checklist"


@dataclass
class OperationObjective:
    """An objective in a joint operation"""
    objective_id: str
    name: str
    description: str = ""
    priority: int = 1
    status: str = "pending"
    assigned_agencies: List[str] = field(default_factory=list)
    assigned_units: List[str] = field(default_factory=list)
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completed_by: str = ""
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationUnit:
    """A unit participating in a joint operation"""
    unit_id: str
    tenant_id: str
    agency_name: str
    call_sign: str
    unit_type: str = ""
    personnel_count: int = 1
    role: OperationRole = OperationRole.UNIT_MEMBER
    status: str = "standby"
    latitude: float = 0.0
    longitude: float = 0.0
    last_position_update: Optional[datetime] = None
    assigned_objective_id: str = ""
    radio_channel: str = ""
    contact_info: str = ""
    capabilities: List[str] = field(default_factory=list)
    notes: str = ""
    joined_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgencyParticipation:
    """Agency participation in a joint operation"""
    participation_id: str
    tenant_id: str
    agency_name: str
    role: OperationRole = OperationRole.UNIT_MEMBER
    lead_contact_name: str = ""
    lead_contact_phone: str = ""
    lead_contact_email: str = ""
    units: List[OperationUnit] = field(default_factory=list)
    personnel_count: int = 0
    resources_committed: List[str] = field(default_factory=list)
    jurisdiction_codes: List[str] = field(default_factory=list)
    joined_at: datetime = field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = None
    is_active: bool = True
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineEvent:
    """An event in the operation timeline"""
    event_id: str
    operation_id: str
    event_type: TimelineEventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_tenant_id: str = ""
    source_agency_name: str = ""
    source_user_id: str = ""
    title: str = ""
    description: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    related_unit_ids: List[str] = field(default_factory=list)
    related_objective_ids: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    is_critical: bool = False
    is_private: bool = False
    visible_to_tenants: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WhiteboardItem:
    """An item on the shared whiteboard"""
    item_id: str
    operation_id: str
    item_type: WhiteboardItemType
    content: str = ""
    title: str = ""
    x_position: float = 0.0
    y_position: float = 0.0
    width: float = 200.0
    height: float = 100.0
    color: str = "#ffffff"
    z_index: int = 0
    created_by_tenant_id: str = ""
    created_by_user_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_locked: bool = False
    locked_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedTimeline:
    """Shared timeline for a joint operation"""
    timeline_id: str
    operation_id: str
    events: List[TimelineEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OperationRoom:
    """A virtual operation room for coordination"""
    room_id: str
    operation_id: str
    name: str
    description: str = ""
    whiteboard_items: List[WhiteboardItem] = field(default_factory=list)
    chat_enabled: bool = True
    video_enabled: bool = True
    map_center_lat: float = 0.0
    map_center_lon: float = 0.0
    map_zoom: int = 12
    active_users: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JointOperation:
    """A joint multi-agency operation"""
    operation_id: str
    name: str
    operation_type: OperationType
    status: OperationStatus = OperationStatus.PLANNING
    description: str = ""
    lead_tenant_id: str = ""
    lead_agency_name: str = ""
    commander_name: str = ""
    commander_contact: str = ""
    participating_agencies: List[AgencyParticipation] = field(default_factory=list)
    objectives: List[OperationObjective] = field(default_factory=list)
    timeline: Optional[SharedTimeline] = None
    room: Optional[OperationRoom] = None
    jurisdiction_codes: List[str] = field(default_factory=list)
    area_of_operations: List[Dict[str, float]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    radio_channels: List[str] = field(default_factory=list)
    encryption_key_ref: str = ""
    classification: str = "law_enforcement_sensitive"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JointOpsMetrics:
    """Metrics for joint operations"""
    total_operations: int = 0
    active_operations: int = 0
    operations_by_type: Dict[OperationType, int] = field(default_factory=dict)
    operations_by_status: Dict[OperationStatus, int] = field(default_factory=dict)
    total_participating_agencies: int = 0
    total_units_deployed: int = 0
    avg_agencies_per_operation: float = 0.0


class JointOpsManager:
    """
    Manages multi-agency joint operations for the G3TI Fusion Cloud.
    
    Provides:
    - Multi-agency operation rooms
    - Role assignment per jurisdiction
    - Shared whiteboard & timeline
    - Inter-department unit tracking
    """
    
    def __init__(self):
        self._operations: Dict[str, JointOperation] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._events: List[Dict[str, Any]] = []
        self._max_events = 10000
    
    def create_operation(
        self,
        name: str,
        operation_type: OperationType,
        lead_tenant_id: str,
        lead_agency_name: str,
        description: str = "",
        commander_name: str = "",
        commander_contact: str = "",
        jurisdiction_codes: List[str] = None,
        planned_start: datetime = None,
        planned_end: datetime = None,
        classification: str = "law_enforcement_sensitive",
        created_by: str = "",
    ) -> Optional[JointOperation]:
        """Create a new joint operation"""
        operation_id = f"op-{uuid.uuid4().hex[:12]}"
        
        timeline = SharedTimeline(
            timeline_id=f"timeline-{uuid.uuid4().hex[:8]}",
            operation_id=operation_id,
        )
        
        room = OperationRoom(
            room_id=f"room-{uuid.uuid4().hex[:8]}",
            operation_id=operation_id,
            name=f"{name} Operations Room",
        )
        
        operation = JointOperation(
            operation_id=operation_id,
            name=name,
            operation_type=operation_type,
            status=OperationStatus.PLANNING,
            description=description,
            lead_tenant_id=lead_tenant_id,
            lead_agency_name=lead_agency_name,
            commander_name=commander_name,
            commander_contact=commander_contact,
            jurisdiction_codes=jurisdiction_codes or [],
            planned_start=planned_start,
            planned_end=planned_end,
            classification=classification,
            timeline=timeline,
            room=room,
            created_by=created_by,
        )
        
        lead_participation = AgencyParticipation(
            participation_id=f"part-{uuid.uuid4().hex[:8]}",
            tenant_id=lead_tenant_id,
            agency_name=lead_agency_name,
            role=OperationRole.COMMANDER,
            lead_contact_name=commander_name,
        )
        operation.participating_agencies.append(lead_participation)
        
        self._add_timeline_event(
            operation,
            TimelineEventType.OPERATION_CREATED,
            lead_tenant_id,
            lead_agency_name,
            "Operation Created",
            f"Joint operation '{name}' created by {lead_agency_name}",
        )
        
        self._operations[operation_id] = operation
        
        self._record_event("operation_created", {
            "operation_id": operation_id,
            "name": name,
            "operation_type": operation_type.value,
            "lead_tenant_id": lead_tenant_id,
        })
        self._notify_callbacks("operation_created", operation)
        
        return operation
    
    def get_operation(self, operation_id: str) -> Optional[JointOperation]:
        """Get an operation by ID"""
        return self._operations.get(operation_id)
    
    def get_all_operations(self) -> List[JointOperation]:
        """Get all operations"""
        return list(self._operations.values())
    
    def get_operations_by_status(self, status: OperationStatus) -> List[JointOperation]:
        """Get operations by status"""
        return [op for op in self._operations.values() if op.status == status]
    
    def get_active_operations(self) -> List[JointOperation]:
        """Get all active operations"""
        return self.get_operations_by_status(OperationStatus.ACTIVE)
    
    def get_operations_for_tenant(self, tenant_id: str) -> List[JointOperation]:
        """Get operations a tenant is participating in"""
        operations = []
        for op in self._operations.values():
            if op.lead_tenant_id == tenant_id:
                operations.append(op)
                continue
            
            for agency in op.participating_agencies:
                if agency.tenant_id == tenant_id and agency.is_active:
                    operations.append(op)
                    break
        
        return operations
    
    def start_operation(self, operation_id: str, started_by: str = "") -> bool:
        """Start an operation"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        if operation.status not in [OperationStatus.PLANNING, OperationStatus.BRIEFING]:
            return False
        
        operation.status = OperationStatus.ACTIVE
        operation.start_time = datetime.utcnow()
        operation.updated_at = datetime.utcnow()
        
        self._add_timeline_event(
            operation,
            TimelineEventType.OPERATION_STARTED,
            operation.lead_tenant_id,
            operation.lead_agency_name,
            "Operation Started",
            f"Operation '{operation.name}' is now active",
            is_critical=True,
        )
        
        self._record_event("operation_started", {
            "operation_id": operation_id,
            "started_by": started_by,
        })
        self._notify_callbacks("operation_started", operation)
        
        return True
    
    def pause_operation(self, operation_id: str, reason: str = "", paused_by: str = "") -> bool:
        """Pause an operation"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        if operation.status != OperationStatus.ACTIVE:
            return False
        
        operation.status = OperationStatus.PAUSED
        operation.updated_at = datetime.utcnow()
        
        self._add_timeline_event(
            operation,
            TimelineEventType.OPERATION_PAUSED,
            operation.lead_tenant_id,
            operation.lead_agency_name,
            "Operation Paused",
            f"Operation paused: {reason}" if reason else "Operation paused",
            is_critical=True,
        )
        
        self._record_event("operation_paused", {
            "operation_id": operation_id,
            "reason": reason,
            "paused_by": paused_by,
        })
        self._notify_callbacks("operation_paused", operation)
        
        return True
    
    def resume_operation(self, operation_id: str, resumed_by: str = "") -> bool:
        """Resume a paused operation"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        if operation.status != OperationStatus.PAUSED:
            return False
        
        operation.status = OperationStatus.ACTIVE
        operation.updated_at = datetime.utcnow()
        
        self._add_timeline_event(
            operation,
            TimelineEventType.OPERATION_RESUMED,
            operation.lead_tenant_id,
            operation.lead_agency_name,
            "Operation Resumed",
            "Operation has resumed",
            is_critical=True,
        )
        
        self._record_event("operation_resumed", {
            "operation_id": operation_id,
            "resumed_by": resumed_by,
        })
        self._notify_callbacks("operation_resumed", operation)
        
        return True
    
    def complete_operation(self, operation_id: str, summary: str = "", completed_by: str = "") -> bool:
        """Complete an operation"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        if operation.status not in [OperationStatus.ACTIVE, OperationStatus.PAUSED, OperationStatus.CONCLUDING]:
            return False
        
        operation.status = OperationStatus.COMPLETED
        operation.end_time = datetime.utcnow()
        operation.updated_at = datetime.utcnow()
        
        self._add_timeline_event(
            operation,
            TimelineEventType.OPERATION_COMPLETED,
            operation.lead_tenant_id,
            operation.lead_agency_name,
            "Operation Completed",
            summary if summary else f"Operation '{operation.name}' completed",
            is_critical=True,
        )
        
        self._record_event("operation_completed", {
            "operation_id": operation_id,
            "summary": summary,
            "completed_by": completed_by,
        })
        self._notify_callbacks("operation_completed", operation)
        
        return True
    
    def cancel_operation(self, operation_id: str, reason: str = "", cancelled_by: str = "") -> bool:
        """Cancel an operation"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        operation.status = OperationStatus.CANCELLED
        operation.end_time = datetime.utcnow()
        operation.updated_at = datetime.utcnow()
        operation.metadata["cancellation_reason"] = reason
        
        self._record_event("operation_cancelled", {
            "operation_id": operation_id,
            "reason": reason,
            "cancelled_by": cancelled_by,
        })
        self._notify_callbacks("operation_cancelled", operation)
        
        return True
    
    def add_agency(
        self,
        operation_id: str,
        tenant_id: str,
        agency_name: str,
        role: OperationRole = OperationRole.UNIT_MEMBER,
        lead_contact_name: str = "",
        lead_contact_phone: str = "",
        jurisdiction_codes: List[str] = None,
        added_by: str = "",
    ) -> Optional[AgencyParticipation]:
        """Add an agency to an operation"""
        if operation_id not in self._operations:
            return None
        
        operation = self._operations[operation_id]
        
        for agency in operation.participating_agencies:
            if agency.tenant_id == tenant_id:
                return None
        
        participation = AgencyParticipation(
            participation_id=f"part-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            agency_name=agency_name,
            role=role,
            lead_contact_name=lead_contact_name,
            lead_contact_phone=lead_contact_phone,
            jurisdiction_codes=jurisdiction_codes or [],
        )
        
        operation.participating_agencies.append(participation)
        operation.updated_at = datetime.utcnow()
        
        self._add_timeline_event(
            operation,
            TimelineEventType.AGENCY_JOINED,
            tenant_id,
            agency_name,
            "Agency Joined",
            f"{agency_name} joined the operation",
        )
        
        self._record_event("agency_added", {
            "operation_id": operation_id,
            "tenant_id": tenant_id,
            "agency_name": agency_name,
            "added_by": added_by,
        })
        self._notify_callbacks("agency_added", {
            "operation": operation,
            "participation": participation,
        })
        
        return participation
    
    def remove_agency(
        self,
        operation_id: str,
        tenant_id: str,
        reason: str = "",
        removed_by: str = "",
    ) -> bool:
        """Remove an agency from an operation"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        for agency in operation.participating_agencies:
            if agency.tenant_id == tenant_id:
                agency.is_active = False
                agency.left_at = datetime.utcnow()
                operation.updated_at = datetime.utcnow()
                
                self._add_timeline_event(
                    operation,
                    TimelineEventType.AGENCY_LEFT,
                    tenant_id,
                    agency.agency_name,
                    "Agency Left",
                    f"{agency.agency_name} left the operation" + (f": {reason}" if reason else ""),
                )
                
                self._record_event("agency_removed", {
                    "operation_id": operation_id,
                    "tenant_id": tenant_id,
                    "reason": reason,
                    "removed_by": removed_by,
                })
                
                return True
        
        return False
    
    def assign_role(
        self,
        operation_id: str,
        tenant_id: str,
        role: OperationRole,
        assigned_by: str = "",
    ) -> bool:
        """Assign a role to an agency"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        for agency in operation.participating_agencies:
            if agency.tenant_id == tenant_id:
                agency.role = role
                operation.updated_at = datetime.utcnow()
                
                self._record_event("role_assigned", {
                    "operation_id": operation_id,
                    "tenant_id": tenant_id,
                    "role": role.value,
                    "assigned_by": assigned_by,
                })
                
                return True
        
        return False
    
    def deploy_unit(
        self,
        operation_id: str,
        tenant_id: str,
        agency_name: str,
        call_sign: str,
        unit_type: str = "",
        personnel_count: int = 1,
        role: OperationRole = OperationRole.UNIT_MEMBER,
        latitude: float = 0.0,
        longitude: float = 0.0,
        capabilities: List[str] = None,
    ) -> Optional[OperationUnit]:
        """Deploy a unit to an operation"""
        if operation_id not in self._operations:
            return None
        
        operation = self._operations[operation_id]
        
        unit = OperationUnit(
            unit_id=f"unit-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            agency_name=agency_name,
            call_sign=call_sign,
            unit_type=unit_type,
            personnel_count=personnel_count,
            role=role,
            status="deployed",
            latitude=latitude,
            longitude=longitude,
            last_position_update=datetime.utcnow() if latitude != 0 else None,
            capabilities=capabilities or [],
        )
        
        for agency in operation.participating_agencies:
            if agency.tenant_id == tenant_id:
                agency.units.append(unit)
                agency.personnel_count += personnel_count
                break
        
        operation.updated_at = datetime.utcnow()
        
        self._add_timeline_event(
            operation,
            TimelineEventType.UNIT_DEPLOYED,
            tenant_id,
            agency_name,
            "Unit Deployed",
            f"Unit {call_sign} deployed to operation",
            latitude=latitude,
            longitude=longitude,
            related_unit_ids=[unit.unit_id],
        )
        
        self._record_event("unit_deployed", {
            "operation_id": operation_id,
            "unit_id": unit.unit_id,
            "call_sign": call_sign,
            "tenant_id": tenant_id,
        })
        self._notify_callbacks("unit_deployed", {
            "operation": operation,
            "unit": unit,
        })
        
        return unit
    
    def update_unit_position(
        self,
        operation_id: str,
        unit_id: str,
        latitude: float,
        longitude: float,
    ) -> bool:
        """Update a unit's position"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        for agency in operation.participating_agencies:
            for unit in agency.units:
                if unit.unit_id == unit_id:
                    unit.latitude = latitude
                    unit.longitude = longitude
                    unit.last_position_update = datetime.utcnow()
                    
                    self._notify_callbacks("unit_position_updated", {
                        "operation": operation,
                        "unit": unit,
                    })
                    
                    return True
        
        return False
    
    def withdraw_unit(
        self,
        operation_id: str,
        unit_id: str,
        reason: str = "",
    ) -> bool:
        """Withdraw a unit from an operation"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        for agency in operation.participating_agencies:
            for unit in agency.units:
                if unit.unit_id == unit_id:
                    unit.status = "withdrawn"
                    agency.personnel_count -= unit.personnel_count
                    operation.updated_at = datetime.utcnow()
                    
                    self._add_timeline_event(
                        operation,
                        TimelineEventType.UNIT_WITHDRAWN,
                        unit.tenant_id,
                        unit.agency_name,
                        "Unit Withdrawn",
                        f"Unit {unit.call_sign} withdrawn" + (f": {reason}" if reason else ""),
                        related_unit_ids=[unit_id],
                    )
                    
                    self._record_event("unit_withdrawn", {
                        "operation_id": operation_id,
                        "unit_id": unit_id,
                        "reason": reason,
                    })
                    
                    return True
        
        return False
    
    def add_objective(
        self,
        operation_id: str,
        name: str,
        description: str = "",
        priority: int = 1,
        assigned_agencies: List[str] = None,
        due_at: datetime = None,
        added_by: str = "",
    ) -> Optional[OperationObjective]:
        """Add an objective to an operation"""
        if operation_id not in self._operations:
            return None
        
        operation = self._operations[operation_id]
        
        objective = OperationObjective(
            objective_id=f"obj-{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            priority=priority,
            assigned_agencies=assigned_agencies or [],
            due_at=due_at,
        )
        
        operation.objectives.append(objective)
        operation.updated_at = datetime.utcnow()
        
        self._add_timeline_event(
            operation,
            TimelineEventType.OBJECTIVE_ADDED,
            operation.lead_tenant_id,
            operation.lead_agency_name,
            "Objective Added",
            f"New objective: {name}",
            related_objective_ids=[objective.objective_id],
        )
        
        self._record_event("objective_added", {
            "operation_id": operation_id,
            "objective_id": objective.objective_id,
            "name": name,
            "added_by": added_by,
        })
        
        return objective
    
    def complete_objective(
        self,
        operation_id: str,
        objective_id: str,
        completed_by: str = "",
        notes: str = "",
    ) -> bool:
        """Mark an objective as completed"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        for objective in operation.objectives:
            if objective.objective_id == objective_id:
                objective.status = "completed"
                objective.completed_at = datetime.utcnow()
                objective.completed_by = completed_by
                objective.notes = notes
                operation.updated_at = datetime.utcnow()
                
                self._add_timeline_event(
                    operation,
                    TimelineEventType.OBJECTIVE_COMPLETED,
                    operation.lead_tenant_id,
                    operation.lead_agency_name,
                    "Objective Completed",
                    f"Objective completed: {objective.name}",
                    related_objective_ids=[objective_id],
                )
                
                self._record_event("objective_completed", {
                    "operation_id": operation_id,
                    "objective_id": objective_id,
                    "completed_by": completed_by,
                })
                
                return True
        
        return False
    
    def add_timeline_event(
        self,
        operation_id: str,
        event_type: TimelineEventType,
        source_tenant_id: str,
        source_agency_name: str,
        title: str,
        description: str = "",
        latitude: float = 0.0,
        longitude: float = 0.0,
        is_critical: bool = False,
        is_private: bool = False,
        visible_to_tenants: List[str] = None,
        attachments: List[str] = None,
        source_user_id: str = "",
    ) -> Optional[TimelineEvent]:
        """Add an event to the operation timeline"""
        if operation_id not in self._operations:
            return None
        
        operation = self._operations[operation_id]
        
        return self._add_timeline_event(
            operation,
            event_type,
            source_tenant_id,
            source_agency_name,
            title,
            description,
            latitude,
            longitude,
            is_critical,
            is_private,
            visible_to_tenants,
            attachments,
            source_user_id,
        )
    
    def get_timeline(
        self,
        operation_id: str,
        tenant_id: str = None,
        limit: int = 100,
        since: datetime = None,
    ) -> List[TimelineEvent]:
        """Get timeline events for an operation"""
        if operation_id not in self._operations:
            return []
        
        operation = self._operations[operation_id]
        
        if not operation.timeline:
            return []
        
        events = operation.timeline.events
        
        if tenant_id:
            events = [
                e for e in events
                if not e.is_private or tenant_id in e.visible_to_tenants or e.source_tenant_id == tenant_id
            ]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        return events[-limit:]
    
    def add_whiteboard_item(
        self,
        operation_id: str,
        item_type: WhiteboardItemType,
        content: str,
        title: str = "",
        x_position: float = 0.0,
        y_position: float = 0.0,
        created_by_tenant_id: str = "",
        created_by_user_id: str = "",
    ) -> Optional[WhiteboardItem]:
        """Add an item to the operation whiteboard"""
        if operation_id not in self._operations:
            return None
        
        operation = self._operations[operation_id]
        
        if not operation.room:
            return None
        
        item = WhiteboardItem(
            item_id=f"wb-{uuid.uuid4().hex[:8]}",
            operation_id=operation_id,
            item_type=item_type,
            content=content,
            title=title,
            x_position=x_position,
            y_position=y_position,
            created_by_tenant_id=created_by_tenant_id,
            created_by_user_id=created_by_user_id,
        )
        
        operation.room.whiteboard_items.append(item)
        
        self._notify_callbacks("whiteboard_item_added", {
            "operation": operation,
            "item": item,
        })
        
        return item
    
    def update_whiteboard_item(
        self,
        operation_id: str,
        item_id: str,
        content: str = None,
        x_position: float = None,
        y_position: float = None,
        width: float = None,
        height: float = None,
    ) -> bool:
        """Update a whiteboard item"""
        if operation_id not in self._operations:
            return False
        
        operation = self._operations[operation_id]
        
        if not operation.room:
            return False
        
        for item in operation.room.whiteboard_items:
            if item.item_id == item_id:
                if content is not None:
                    item.content = content
                if x_position is not None:
                    item.x_position = x_position
                if y_position is not None:
                    item.y_position = y_position
                if width is not None:
                    item.width = width
                if height is not None:
                    item.height = height
                item.updated_at = datetime.utcnow()
                
                self._notify_callbacks("whiteboard_item_updated", {
                    "operation": operation,
                    "item": item,
                })
                
                return True
        
        return False
    
    def get_metrics(self) -> JointOpsMetrics:
        """Get metrics for joint operations"""
        metrics = JointOpsMetrics()
        metrics.total_operations = len(self._operations)
        
        total_agencies = 0
        total_units = 0
        
        for op in self._operations.values():
            if op.status == OperationStatus.ACTIVE:
                metrics.active_operations += 1
            
            metrics.operations_by_type[op.operation_type] = \
                metrics.operations_by_type.get(op.operation_type, 0) + 1
            metrics.operations_by_status[op.status] = \
                metrics.operations_by_status.get(op.status, 0) + 1
            
            active_agencies = [a for a in op.participating_agencies if a.is_active]
            total_agencies += len(active_agencies)
            
            for agency in active_agencies:
                total_units += len([u for u in agency.units if u.status != "withdrawn"])
        
        metrics.total_participating_agencies = total_agencies
        metrics.total_units_deployed = total_units
        
        if metrics.total_operations > 0:
            metrics.avg_agencies_per_operation = total_agencies / metrics.total_operations
        
        return metrics
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self._events[-limit:]
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type"""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
    
    def _add_timeline_event(
        self,
        operation: JointOperation,
        event_type: TimelineEventType,
        source_tenant_id: str,
        source_agency_name: str,
        title: str,
        description: str = "",
        latitude: float = 0.0,
        longitude: float = 0.0,
        is_critical: bool = False,
        is_private: bool = False,
        visible_to_tenants: List[str] = None,
        attachments: List[str] = None,
        source_user_id: str = "",
    ) -> TimelineEvent:
        """Add an event to the operation timeline"""
        event = TimelineEvent(
            event_id=f"evt-{uuid.uuid4().hex[:8]}",
            operation_id=operation.operation_id,
            event_type=event_type,
            source_tenant_id=source_tenant_id,
            source_agency_name=source_agency_name,
            source_user_id=source_user_id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
            is_critical=is_critical,
            is_private=is_private,
            visible_to_tenants=visible_to_tenants or [],
            attachments=attachments or [],
        )
        
        if operation.timeline:
            operation.timeline.events.append(event)
            operation.timeline.updated_at = datetime.utcnow()
        
        self._notify_callbacks("timeline_event_added", {
            "operation": operation,
            "event": event,
        })
        
        return event
    
    def _record_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record an event"""
        event = {
            "event_id": f"evt-{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        self._events.append(event)
        
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
    
    def _notify_callbacks(self, event_type: str, data: Any) -> None:
        """Notify registered callbacks"""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(data)
                except Exception:
                    pass
