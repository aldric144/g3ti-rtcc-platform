"""
Major Incident Engine for G3TI RTCC-UIP.

Provides creation, activation, and management of major incidents
including Active Shooter, Pursuit, Barricaded Subject, Natural Disaster,
Missing Person, SWAT Operation, Multi-Agency Operations, and Critical Events.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class IncidentType(str, Enum):
    """Types of major incidents."""

    ACTIVE_SHOOTER = "active_shooter"
    PURSUIT = "pursuit"
    BARRICADED_SUBJECT = "barricaded_subject"
    NATURAL_DISASTER = "natural_disaster"
    MISSING_PERSON = "missing_person"
    SWAT_OPERATION = "swat_operation"
    MULTI_AGENCY = "multi_agency"
    CRITICAL_EVENT = "critical_event"
    HOSTAGE = "hostage"
    BOMB_THREAT = "bomb_threat"
    CIVIL_UNREST = "civil_unrest"
    HAZMAT = "hazmat"


class IncidentStatus(str, Enum):
    """Status of a major incident."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    STABILIZED = "stabilized"
    DEMOBILIZING = "demobilizing"
    CLOSED = "closed"
    ARCHIVED = "archived"


class IncidentPriority(str, Enum):
    """Priority level of incident."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GeoLocation(BaseModel):
    """Geographic location model."""

    latitude: float
    longitude: float
    address: str | None = None
    city: str | None = None
    zone: str | None = None
    radius_meters: float | None = None


class ICSStructure(BaseModel):
    """ICS organizational structure for incident."""

    incident_commander: str | None = None
    operations_chief: str | None = None
    planning_chief: str | None = None
    logistics_chief: str | None = None
    intelligence_officer: str | None = None
    safety_officer: str | None = None
    public_info_officer: str | None = None
    liaison_officer: str | None = None
    additional_roles: dict[str, str] = Field(default_factory=dict)


class MajorIncident(BaseModel):
    """Major incident model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_number: str = Field(
        default_factory=lambda: f"MI-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    )
    incident_type: IncidentType
    status: IncidentStatus = IncidentStatus.DRAFT
    priority: IncidentPriority = IncidentPriority.HIGH
    title: str
    description: str | None = None
    location: GeoLocation | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    activated_at: datetime | None = None
    closed_at: datetime | None = None
    assigned_commander: str | None = None
    assigned_rtcc_analyst: str | None = None
    agencies_involved: list[str] = Field(default_factory=list)
    ics_structure: ICSStructure = Field(default_factory=ICSStructure)
    assigned_units: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    related_cad_ids: list[str] = Field(default_factory=list)
    related_case_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)
    is_frozen: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-MI-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class IncidentEvent(BaseModel):
    """Event related to an incident."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    event_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    user_id: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-IE-{uuid.uuid4().hex[:12].upper()}")


class MajorIncidentEngine:
    """
    Engine for managing major incidents.

    Provides creation, activation, status management, and
    coordination of major incidents with ICS integration.
    """

    def __init__(self) -> None:
        """Initialize the major incident engine."""
        self._incidents: dict[str, MajorIncident] = {}
        self._events: list[IncidentEvent] = []
        self._incident_checklists: dict[IncidentType, list[str]] = self._init_checklists()

        logger.info("major_incident_engine_initialized")

    def _init_checklists(self) -> dict[IncidentType, list[str]]:
        """Initialize incident type checklists."""
        return {
            IncidentType.ACTIVE_SHOOTER: [
                "Establish incident command",
                "Request SWAT activation",
                "Establish perimeter",
                "Coordinate with dispatch for unit staging",
                "Notify hospitals for mass casualty",
                "Request air support if available",
                "Establish media staging area",
                "Coordinate with school/facility security",
                "Begin evacuation procedures",
                "Document all unit positions",
            ],
            IncidentType.PURSUIT: [
                "Establish incident command",
                "Notify air support",
                "Coordinate with neighboring jurisdictions",
                "Establish spike strip locations",
                "Monitor traffic conditions",
                "Prepare for termination tactics",
                "Notify hospitals if injuries",
                "Document pursuit path",
            ],
            IncidentType.BARRICADED_SUBJECT: [
                "Establish incident command",
                "Request SWAT/HNT activation",
                "Establish inner and outer perimeter",
                "Evacuate adjacent structures",
                "Gather intelligence on subject",
                "Establish negotiation contact",
                "Position tactical teams",
                "Coordinate with utilities",
            ],
            IncidentType.NATURAL_DISASTER: [
                "Establish incident command",
                "Assess damage and casualties",
                "Coordinate with emergency management",
                "Request mutual aid if needed",
                "Establish evacuation routes",
                "Set up shelters",
                "Coordinate with utilities",
                "Establish media briefing schedule",
            ],
            IncidentType.MISSING_PERSON: [
                "Establish incident command",
                "Gather subject information",
                "Issue BOLO/Amber Alert if applicable",
                "Coordinate search teams",
                "Check known locations",
                "Review camera footage",
                "Coordinate with family",
                "Establish tip line",
            ],
            IncidentType.SWAT_OPERATION: [
                "Establish incident command",
                "Brief SWAT team",
                "Establish perimeter",
                "Position tactical teams",
                "Coordinate with intelligence",
                "Establish medical staging",
                "Document all positions",
                "Prepare contingency plans",
            ],
            IncidentType.MULTI_AGENCY: [
                "Establish unified command",
                "Identify agency representatives",
                "Establish communication protocols",
                "Define roles and responsibilities",
                "Coordinate resource sharing",
                "Establish joint information center",
            ],
            IncidentType.CRITICAL_EVENT: [
                "Establish incident command",
                "Assess situation",
                "Request appropriate resources",
                "Establish perimeter if needed",
                "Coordinate with relevant agencies",
                "Document all actions",
            ],
            IncidentType.HOSTAGE: [
                "Establish incident command",
                "Request HNT activation",
                "Establish perimeter",
                "Gather intelligence on hostage taker",
                "Identify hostages",
                "Establish negotiation contact",
                "Position tactical teams",
                "Coordinate with family liaison",
            ],
            IncidentType.BOMB_THREAT: [
                "Establish incident command",
                "Request bomb squad",
                "Evacuate affected area",
                "Establish perimeter",
                "Search for secondary devices",
                "Coordinate with facility management",
                "Document all findings",
            ],
            IncidentType.CIVIL_UNREST: [
                "Establish incident command",
                "Assess crowd size and mood",
                "Request additional units",
                "Establish perimeter",
                "Coordinate with public affairs",
                "Document all incidents",
                "Prepare arrest teams if needed",
            ],
            IncidentType.HAZMAT: [
                "Establish incident command",
                "Request hazmat team",
                "Establish hot/warm/cold zones",
                "Evacuate affected area",
                "Identify substance if possible",
                "Coordinate with fire department",
                "Establish decontamination area",
            ],
        }

    async def create_incident(
        self,
        incident_type: IncidentType,
        title: str,
        description: str | None = None,
        location: GeoLocation | None = None,
        priority: IncidentPriority = IncidentPriority.HIGH,
        assigned_commander: str | None = None,
        assigned_rtcc_analyst: str | None = None,
        agencies: list[str] | None = None,
        related_cad_ids: list[str] | None = None,
        created_by: str | None = None,
        auto_activate: bool = False,
    ) -> MajorIncident:
        """
        Create a new major incident.

        Args:
            incident_type: Type of incident
            title: Incident title
            description: Detailed description
            location: Geographic location
            priority: Priority level
            assigned_commander: Badge of assigned commander
            assigned_rtcc_analyst: Badge of assigned RTCC analyst
            agencies: List of agencies involved
            related_cad_ids: Related CAD call IDs
            created_by: User who created the incident
            auto_activate: Whether to automatically activate

        Returns:
            Created MajorIncident
        """
        incident = MajorIncident(
            incident_type=incident_type,
            title=title,
            description=description,
            location=location,
            priority=priority,
            assigned_commander=assigned_commander,
            assigned_rtcc_analyst=assigned_rtcc_analyst,
            agencies_involved=agencies or [],
            related_cad_ids=related_cad_ids or [],
            created_by=created_by,
        )

        # Set commander in ICS structure if provided
        if assigned_commander:
            incident.ics_structure.incident_commander = assigned_commander

        self._incidents[incident.id] = incident

        # Log event
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="incident_created",
            data={
                "incident_type": incident_type.value if isinstance(incident_type, IncidentType) else incident_type,
                "title": title,
                "priority": priority.value if isinstance(priority, IncidentPriority) else priority,
            },
            user_id=created_by,
        )
        self._events.append(event)

        logger.info(
            "major_incident_created",
            incident_id=incident.id,
            incident_number=incident.incident_number,
            incident_type=incident_type,
            title=title,
            audit_id=incident.audit_id,
        )

        if auto_activate:
            incident = await self.activate_incident(incident.id, activated_by=created_by)

        return incident

    async def activate_incident(
        self,
        incident_id: str,
        activated_by: str | None = None,
    ) -> MajorIncident:
        """
        Activate a major incident.

        Args:
            incident_id: ID of incident to activate
            activated_by: User activating the incident

        Returns:
            Activated MajorIncident

        Raises:
            ValueError: If incident not found or already active
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.status == IncidentStatus.ACTIVE:
            raise ValueError(f"Incident {incident_id} is already active")

        if incident.status in [IncidentStatus.CLOSED, IncidentStatus.ARCHIVED]:
            raise ValueError(f"Cannot activate closed/archived incident {incident_id}")

        incident.status = IncidentStatus.ACTIVE
        incident.activated_at = datetime.now(UTC)
        incident.start_time = incident.start_time or incident.activated_at
        incident.updated_at = datetime.now(UTC)

        # Log event
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="incident_activated",
            data={"previous_status": "draft"},
            user_id=activated_by,
        )
        self._events.append(event)

        logger.info(
            "major_incident_activated",
            incident_id=incident.id,
            incident_number=incident.incident_number,
            activated_by=activated_by,
            audit_id=incident.audit_id,
        )

        return incident

    async def update_status(
        self,
        incident_id: str,
        status: IncidentStatus,
        updated_by: str | None = None,
        notes: str | None = None,
    ) -> MajorIncident:
        """
        Update incident status.

        Args:
            incident_id: ID of incident
            status: New status
            updated_by: User updating status
            notes: Optional notes about status change

        Returns:
            Updated MajorIncident
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.is_frozen:
            raise ValueError(f"Incident {incident_id} is frozen and cannot be modified")

        old_status = incident.status
        incident.status = status
        incident.updated_at = datetime.now(UTC)

        if notes:
            incident.notes.append(f"[{datetime.now(UTC).isoformat()}] Status change: {notes}")

        # Handle special status transitions
        if status == IncidentStatus.CLOSED:
            incident.closed_at = datetime.now(UTC)
            incident.end_time = incident.closed_at
            incident.is_frozen = True

        # Log event
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="incident_status_changed",
            data={
                "old_status": old_status,
                "new_status": status,
                "notes": notes,
            },
            user_id=updated_by,
        )
        self._events.append(event)

        logger.info(
            "major_incident_status_changed",
            incident_id=incident.id,
            old_status=old_status,
            new_status=status,
            updated_by=updated_by,
            audit_id=incident.audit_id,
        )

        return incident

    async def close_incident(
        self,
        incident_id: str,
        closed_by: str | None = None,
        closing_notes: str | None = None,
    ) -> MajorIncident:
        """
        Close a major incident.

        Args:
            incident_id: ID of incident to close
            closed_by: User closing the incident
            closing_notes: Notes about closure

        Returns:
            Closed MajorIncident
        """
        incident = await self.update_status(
            incident_id=incident_id,
            status=IncidentStatus.CLOSED,
            updated_by=closed_by,
            notes=closing_notes or "Incident closed",
        )

        logger.info(
            "major_incident_closed",
            incident_id=incident.id,
            incident_number=incident.incident_number,
            closed_by=closed_by,
            audit_id=incident.audit_id,
        )

        return incident

    async def assign_commander(
        self,
        incident_id: str,
        commander_badge: str,
        assigned_by: str | None = None,
    ) -> MajorIncident:
        """
        Assign incident commander.

        Args:
            incident_id: ID of incident
            commander_badge: Badge of commander
            assigned_by: User making assignment

        Returns:
            Updated MajorIncident
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.is_frozen:
            raise ValueError(f"Incident {incident_id} is frozen")

        old_commander = incident.assigned_commander
        incident.assigned_commander = commander_badge
        incident.ics_structure.incident_commander = commander_badge
        incident.updated_at = datetime.now(UTC)

        # Log event
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="commander_assigned",
            data={
                "old_commander": old_commander,
                "new_commander": commander_badge,
            },
            user_id=assigned_by,
        )
        self._events.append(event)

        logger.info(
            "incident_commander_assigned",
            incident_id=incident.id,
            commander=commander_badge,
            assigned_by=assigned_by,
            audit_id=incident.audit_id,
        )

        return incident

    async def assign_rtcc_analyst(
        self,
        incident_id: str,
        analyst_badge: str,
        assigned_by: str | None = None,
    ) -> MajorIncident:
        """
        Assign RTCC analyst to incident.

        Args:
            incident_id: ID of incident
            analyst_badge: Badge of analyst
            assigned_by: User making assignment

        Returns:
            Updated MajorIncident
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.is_frozen:
            raise ValueError(f"Incident {incident_id} is frozen")

        old_analyst = incident.assigned_rtcc_analyst
        incident.assigned_rtcc_analyst = analyst_badge
        incident.ics_structure.intelligence_officer = analyst_badge
        incident.updated_at = datetime.now(UTC)

        # Log event
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="rtcc_analyst_assigned",
            data={
                "old_analyst": old_analyst,
                "new_analyst": analyst_badge,
            },
            user_id=assigned_by,
        )
        self._events.append(event)

        logger.info(
            "rtcc_analyst_assigned",
            incident_id=incident.id,
            analyst=analyst_badge,
            assigned_by=assigned_by,
            audit_id=incident.audit_id,
        )

        return incident

    async def add_agency(
        self,
        incident_id: str,
        agency: str,
        added_by: str | None = None,
    ) -> MajorIncident:
        """
        Add agency to incident.

        Args:
            incident_id: ID of incident
            agency: Agency name/code
            added_by: User adding agency

        Returns:
            Updated MajorIncident
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.is_frozen:
            raise ValueError(f"Incident {incident_id} is frozen")

        if agency not in incident.agencies_involved:
            incident.agencies_involved.append(agency)
            incident.updated_at = datetime.now(UTC)

            # Log event
            event = IncidentEvent(
                incident_id=incident.id,
                event_type="agency_added",
                data={"agency": agency},
                user_id=added_by,
            )
            self._events.append(event)

            logger.info(
                "agency_added_to_incident",
                incident_id=incident.id,
                agency=agency,
                added_by=added_by,
                audit_id=incident.audit_id,
            )

        return incident

    async def add_unit(
        self,
        incident_id: str,
        unit_id: str,
        added_by: str | None = None,
    ) -> MajorIncident:
        """
        Add unit to incident.

        Args:
            incident_id: ID of incident
            unit_id: Unit identifier
            added_by: User adding unit

        Returns:
            Updated MajorIncident
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.is_frozen:
            raise ValueError(f"Incident {incident_id} is frozen")

        if unit_id not in incident.assigned_units:
            incident.assigned_units.append(unit_id)
            incident.updated_at = datetime.now(UTC)

            # Log event
            event = IncidentEvent(
                incident_id=incident.id,
                event_type="unit_added",
                data={"unit_id": unit_id},
                user_id=added_by,
            )
            self._events.append(event)

            logger.info(
                "unit_added_to_incident",
                incident_id=incident.id,
                unit_id=unit_id,
                added_by=added_by,
                audit_id=incident.audit_id,
            )

        return incident

    async def remove_unit(
        self,
        incident_id: str,
        unit_id: str,
        removed_by: str | None = None,
    ) -> MajorIncident:
        """
        Remove unit from incident.

        Args:
            incident_id: ID of incident
            unit_id: Unit identifier
            removed_by: User removing unit

        Returns:
            Updated MajorIncident
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.is_frozen:
            raise ValueError(f"Incident {incident_id} is frozen")

        if unit_id in incident.assigned_units:
            incident.assigned_units.remove(unit_id)
            incident.updated_at = datetime.now(UTC)

            # Log event
            event = IncidentEvent(
                incident_id=incident.id,
                event_type="unit_removed",
                data={"unit_id": unit_id},
                user_id=removed_by,
            )
            self._events.append(event)

            logger.info(
                "unit_removed_from_incident",
                incident_id=incident.id,
                unit_id=unit_id,
                removed_by=removed_by,
                audit_id=incident.audit_id,
            )

        return incident

    async def add_note(
        self,
        incident_id: str,
        note: str,
        added_by: str | None = None,
    ) -> MajorIncident:
        """
        Add note to incident.

        Args:
            incident_id: ID of incident
            note: Note text
            added_by: User adding note

        Returns:
            Updated MajorIncident
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if incident.is_frozen:
            raise ValueError(f"Incident {incident_id} is frozen")

        timestamp = datetime.now(UTC).isoformat()
        formatted_note = f"[{timestamp}] [{added_by or 'SYSTEM'}] {note}"
        incident.notes.append(formatted_note)
        incident.updated_at = datetime.now(UTC)

        # Log event
        event = IncidentEvent(
            incident_id=incident.id,
            event_type="note_added",
            data={"note": note},
            user_id=added_by,
        )
        self._events.append(event)

        logger.info(
            "note_added_to_incident",
            incident_id=incident.id,
            added_by=added_by,
            audit_id=incident.audit_id,
        )

        return incident

    async def link_cad_call(
        self,
        incident_id: str,
        cad_id: str,
        linked_by: str | None = None,
    ) -> MajorIncident:
        """
        Link CAD call to incident.

        Args:
            incident_id: ID of incident
            cad_id: CAD call ID
            linked_by: User linking call

        Returns:
            Updated MajorIncident
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        if cad_id not in incident.related_cad_ids:
            incident.related_cad_ids.append(cad_id)
            incident.updated_at = datetime.now(UTC)

            # Log event
            event = IncidentEvent(
                incident_id=incident.id,
                event_type="cad_call_linked",
                data={"cad_id": cad_id},
                user_id=linked_by,
            )
            self._events.append(event)

            logger.info(
                "cad_call_linked_to_incident",
                incident_id=incident.id,
                cad_id=cad_id,
                linked_by=linked_by,
                audit_id=incident.audit_id,
            )

        return incident

    def get_incident(self, incident_id: str) -> MajorIncident | None:
        """Get incident by ID."""
        return self._incidents.get(incident_id)

    def get_incident_by_number(self, incident_number: str) -> MajorIncident | None:
        """Get incident by incident number."""
        for incident in self._incidents.values():
            if incident.incident_number == incident_number:
                return incident
        return None

    async def get_active_incidents(
        self,
        incident_type: IncidentType | None = None,
        priority: IncidentPriority | None = None,
    ) -> list[MajorIncident]:
        """
        Get all active incidents.

        Args:
            incident_type: Filter by type
            priority: Filter by priority

        Returns:
            List of active incidents
        """
        incidents = [
            i for i in self._incidents.values()
            if i.status == IncidentStatus.ACTIVE
        ]

        if incident_type:
            type_value = incident_type.value if isinstance(incident_type, IncidentType) else incident_type
            incidents = [i for i in incidents if i.incident_type == type_value]

        if priority:
            priority_value = priority.value if isinstance(priority, IncidentPriority) else priority
            incidents = [i for i in incidents if i.priority == priority_value]

        # Sort by priority and start time
        priority_order = {
            IncidentPriority.CRITICAL.value: 0,
            IncidentPriority.HIGH.value: 1,
            IncidentPriority.MEDIUM.value: 2,
            IncidentPriority.LOW.value: 3,
        }
        incidents.sort(
            key=lambda x: (
                priority_order.get(x.priority, 4),
                x.start_time or x.created_at,
            )
        )

        return incidents

    async def get_all_incidents(
        self,
        status: IncidentStatus | None = None,
        limit: int = 100,
    ) -> list[MajorIncident]:
        """
        Get all incidents with optional filtering.

        Args:
            status: Filter by status
            limit: Maximum number to return

        Returns:
            List of incidents
        """
        incidents = list(self._incidents.values())

        if status:
            status_value = status.value if isinstance(status, IncidentStatus) else status
            incidents = [i for i in incidents if i.status == status_value]

        # Sort by created_at descending
        incidents.sort(key=lambda x: x.created_at, reverse=True)

        return incidents[:limit]

    def get_checklist(self, incident_type: IncidentType) -> list[str]:
        """
        Get checklist for incident type.

        Args:
            incident_type: Type of incident

        Returns:
            List of checklist items
        """
        return self._incident_checklists.get(incident_type, [])

    async def get_incident_events(
        self,
        incident_id: str,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[IncidentEvent]:
        """
        Get events for an incident.

        Args:
            incident_id: ID of incident
            event_type: Filter by event type
            limit: Maximum number to return

        Returns:
            List of incident events
        """
        events = [e for e in self._events if e.incident_id == incident_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Sort by timestamp descending
        events.sort(key=lambda x: x.timestamp, reverse=True)

        return events[:limit]

    async def get_incident_statistics(self) -> dict[str, Any]:
        """
        Get statistics about incidents.

        Returns:
            Dictionary of statistics
        """
        all_incidents = list(self._incidents.values())
        active_incidents = [i for i in all_incidents if i.status == IncidentStatus.ACTIVE]

        # Count by type
        by_type: dict[str, int] = {}
        for incident in active_incidents:
            incident_type = incident.incident_type
            by_type[incident_type] = by_type.get(incident_type, 0) + 1

        # Count by priority
        by_priority: dict[str, int] = {}
        for incident in active_incidents:
            priority = incident.priority
            by_priority[priority] = by_priority.get(priority, 0) + 1

        return {
            "total_incidents": len(all_incidents),
            "active_incidents": len(active_incidents),
            "by_type": by_type,
            "by_priority": by_priority,
            "total_units_assigned": sum(len(i.assigned_units) for i in active_incidents),
            "total_agencies_involved": len({
                agency
                for i in active_incidents
                for agency in i.agencies_involved
            }),
        }
