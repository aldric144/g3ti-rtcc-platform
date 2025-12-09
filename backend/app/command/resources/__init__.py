"""
Resource Assignment & Deployment Manager for G3TI RTCC-UIP.

Provides assignment and tracking of units, equipment, vehicles,
drones, K9, SWAT assets, and multi-agency resources.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class ResourceType(str, Enum):
    """Types of resources."""

    PATROL_UNIT = "patrol_unit"
    SUPERVISOR = "supervisor"
    DETECTIVE = "detective"
    SWAT = "swat"
    K9 = "k9"
    DRONE = "drone"
    HELICOPTER = "helicopter"
    VEHICLE = "vehicle"
    EQUIPMENT = "equipment"
    FIRE = "fire"
    EMS = "ems"
    HAZMAT = "hazmat"
    BOMB_SQUAD = "bomb_squad"
    NEGOTIATOR = "negotiator"
    CRIME_SCENE = "crime_scene"
    TRAFFIC = "traffic"
    MARINE = "marine"
    MOUNTED = "mounted"
    EXTERNAL_AGENCY = "external_agency"


class ResourceStatus(str, Enum):
    """Status of a resource."""

    AVAILABLE = "available"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    STAGING = "staging"
    BUSY = "busy"
    OUT_OF_SERVICE = "out_of_service"
    OFF_DUTY = "off_duty"


class AgencyType(str, Enum):
    """Types of agencies."""

    POLICE = "police"
    FIRE = "fire"
    EMS = "ems"
    SHERIFF = "sheriff"
    STATE_POLICE = "state_police"
    FEDERAL = "federal"
    EMERGENCY_MANAGEMENT = "emergency_management"
    REGIONAL = "regional"
    PRIVATE = "private"


class GeoLocation(BaseModel):
    """Geographic location."""

    latitude: float
    longitude: float
    address: str | None = None


class Resource(BaseModel):
    """Resource model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType
    name: str
    call_sign: str | None = None
    badge: str | None = None
    agency: str | None = None
    agency_type: AgencyType = AgencyType.POLICE
    status: ResourceStatus = ResourceStatus.AVAILABLE
    location: GeoLocation | None = None
    capabilities: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    personnel_count: int = 1
    contact: str | None = None
    notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    audit_id: str = Field(default_factory=lambda: f"AUDIT-RES-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class ResourceAssignment(BaseModel):
    """Assignment of a resource to an incident."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    resource_id: str
    resource_type: ResourceType
    resource_name: str
    role: str | None = None
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    assigned_by: str | None = None
    released_at: datetime | None = None
    released_by: str | None = None
    is_active: bool = True
    arrival_time: datetime | None = None
    departure_time: datetime | None = None
    notes: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-RA-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class ResourceRequest(BaseModel):
    """Request for resources."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    resource_type: ResourceType
    quantity: int = 1
    priority: str = "normal"
    reason: str | None = None
    requested_by: str | None = None
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    fulfilled: bool = False
    fulfilled_at: datetime | None = None
    fulfilled_by: str | None = None
    assigned_resources: list[str] = Field(default_factory=list)
    notes: str | None = None

    class Config:
        """Pydantic config."""

        use_enum_values = True


class ResourceEvent(BaseModel):
    """Event related to resource changes."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str | None = None
    resource_id: str
    event_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    user_id: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-RE-{uuid.uuid4().hex[:12].upper()}")


class ResourceManager:
    """
    Manager for resource assignment and deployment.

    Provides tracking, assignment, and coordination of
    all resources for incident command operations.
    """

    def __init__(self) -> None:
        """Initialize the resource manager."""
        self._resources: dict[str, Resource] = {}
        self._assignments: dict[str, list[ResourceAssignment]] = {}  # incident_id -> assignments
        self._requests: dict[str, list[ResourceRequest]] = {}  # incident_id -> requests
        self._events: list[ResourceEvent] = []

        # Initialize some default resources for demo
        self._init_default_resources()

        logger.info("resource_manager_initialized")

    def _init_default_resources(self) -> None:
        """Initialize default resources."""
        # This would typically be loaded from a database
        default_resources = [
            Resource(
                resource_type=ResourceType.SWAT,
                name="SWAT Team Alpha",
                call_sign="SWAT-1",
                agency="Police Department",
                capabilities=["tactical_entry", "hostage_rescue", "high_risk_warrant"],
                personnel_count=8,
            ),
            Resource(
                resource_type=ResourceType.K9,
                name="K9 Unit - Rex",
                call_sign="K9-1",
                badge="K901",
                agency="Police Department",
                capabilities=["tracking", "narcotics", "apprehension"],
                personnel_count=1,
            ),
            Resource(
                resource_type=ResourceType.DRONE,
                name="Aerial Drone Unit 1",
                call_sign="DRONE-1",
                agency="Police Department",
                capabilities=["aerial_surveillance", "thermal_imaging", "live_feed"],
                personnel_count=2,
            ),
            Resource(
                resource_type=ResourceType.HELICOPTER,
                name="Air Support 1",
                call_sign="AIR-1",
                agency="Police Department",
                capabilities=["aerial_surveillance", "pursuit_support", "search_rescue"],
                personnel_count=2,
            ),
            Resource(
                resource_type=ResourceType.NEGOTIATOR,
                name="Crisis Negotiation Team",
                call_sign="CNT-1",
                agency="Police Department",
                capabilities=["hostage_negotiation", "crisis_intervention", "suicide_prevention"],
                personnel_count=4,
            ),
            Resource(
                resource_type=ResourceType.BOMB_SQUAD,
                name="Bomb Disposal Unit",
                call_sign="EOD-1",
                agency="Police Department",
                capabilities=["bomb_disposal", "hazardous_device", "x_ray"],
                personnel_count=4,
            ),
        ]

        for resource in default_resources:
            self._resources[resource.id] = resource

    async def register_resource(
        self,
        resource_type: ResourceType,
        name: str,
        call_sign: str | None = None,
        badge: str | None = None,
        agency: str | None = None,
        agency_type: AgencyType = AgencyType.POLICE,
        capabilities: list[str] | None = None,
        equipment: list[str] | None = None,
        personnel_count: int = 1,
        contact: str | None = None,
        location: GeoLocation | None = None,
    ) -> Resource:
        """
        Register a new resource.

        Args:
            resource_type: Type of resource
            name: Resource name
            call_sign: Radio call sign
            badge: Badge number (for personnel)
            agency: Agency name
            agency_type: Type of agency
            capabilities: List of capabilities
            equipment: List of equipment
            personnel_count: Number of personnel
            contact: Contact information
            location: Current location

        Returns:
            Created Resource
        """
        resource = Resource(
            resource_type=resource_type,
            name=name,
            call_sign=call_sign,
            badge=badge,
            agency=agency,
            agency_type=agency_type,
            capabilities=capabilities or [],
            equipment=equipment or [],
            personnel_count=personnel_count,
            contact=contact,
            location=location,
        )

        self._resources[resource.id] = resource

        # Log event
        event = ResourceEvent(
            resource_id=resource.id,
            event_type="resource_registered",
            data={
                "resource_type": resource_type,
                "name": name,
                "agency": agency,
            },
        )
        self._events.append(event)

        logger.info(
            "resource_registered",
            resource_id=resource.id,
            resource_type=resource_type,
            name=name,
            audit_id=resource.audit_id,
        )

        return resource

    async def update_resource_status(
        self,
        resource_id: str,
        status: ResourceStatus,
        location: GeoLocation | None = None,
        updated_by: str | None = None,
    ) -> Resource | None:
        """
        Update resource status.

        Args:
            resource_id: ID of resource
            status: New status
            location: Updated location
            updated_by: User updating status

        Returns:
            Updated Resource or None
        """
        resource = self._resources.get(resource_id)
        if not resource:
            return None

        old_status = resource.status
        resource.status = status
        resource.updated_at = datetime.now(UTC)

        if location:
            resource.location = location

        # Log event
        event = ResourceEvent(
            resource_id=resource_id,
            event_type="resource_status_changed",
            data={
                "old_status": old_status,
                "new_status": status,
            },
            user_id=updated_by,
        )
        self._events.append(event)

        logger.info(
            "resource_status_updated",
            resource_id=resource_id,
            old_status=old_status,
            new_status=status,
            updated_by=updated_by,
        )

        return resource

    async def assign_resource(
        self,
        incident_id: str,
        resource_id: str,
        role: str | None = None,
        assigned_by: str | None = None,
        notes: str | None = None,
    ) -> ResourceAssignment | None:
        """
        Assign a resource to an incident.

        Args:
            incident_id: ID of incident
            resource_id: ID of resource
            role: Role for this assignment
            assigned_by: User making assignment
            notes: Assignment notes

        Returns:
            Created ResourceAssignment or None
        """
        resource = self._resources.get(resource_id)
        if not resource:
            return None

        # Check if resource is available
        if resource.status not in [ResourceStatus.AVAILABLE, ResourceStatus.STAGING]:
            logger.warning(
                "resource_not_available",
                resource_id=resource_id,
                status=resource.status,
            )
            # Allow assignment anyway but log warning

        # Create assignment
        assignment = ResourceAssignment(
            incident_id=incident_id,
            resource_id=resource_id,
            resource_type=resource.resource_type,
            resource_name=resource.name,
            role=role,
            assigned_by=assigned_by,
            notes=notes,
        )

        if incident_id not in self._assignments:
            self._assignments[incident_id] = []
        self._assignments[incident_id].append(assignment)

        # Update resource status
        resource.status = ResourceStatus.ASSIGNED
        resource.updated_at = datetime.now(UTC)

        # Log event
        event = ResourceEvent(
            incident_id=incident_id,
            resource_id=resource_id,
            event_type="resource_assigned",
            data={
                "role": role,
                "resource_type": resource.resource_type,
            },
            user_id=assigned_by,
        )
        self._events.append(event)

        logger.info(
            "resource_assigned",
            incident_id=incident_id,
            resource_id=resource_id,
            resource_name=resource.name,
            role=role,
            assigned_by=assigned_by,
            audit_id=assignment.audit_id,
        )

        return assignment

    async def release_resource(
        self,
        incident_id: str,
        resource_id: str,
        released_by: str | None = None,
        notes: str | None = None,
    ) -> ResourceAssignment | None:
        """
        Release a resource from an incident.

        Args:
            incident_id: ID of incident
            resource_id: ID of resource
            released_by: User releasing resource
            notes: Release notes

        Returns:
            Updated ResourceAssignment or None
        """
        assignments = self._assignments.get(incident_id, [])
        assignment = next(
            (a for a in assignments if a.resource_id == resource_id and a.is_active),
            None
        )

        if not assignment:
            return None

        assignment.is_active = False
        assignment.released_at = datetime.now(UTC)
        assignment.released_by = released_by
        assignment.departure_time = datetime.now(UTC)
        if notes:
            assignment.notes = (assignment.notes or "") + f" | Released: {notes}"

        # Update resource status
        resource = self._resources.get(resource_id)
        if resource:
            resource.status = ResourceStatus.AVAILABLE
            resource.updated_at = datetime.now(UTC)

        # Log event
        event = ResourceEvent(
            incident_id=incident_id,
            resource_id=resource_id,
            event_type="resource_released",
            data={"notes": notes},
            user_id=released_by,
        )
        self._events.append(event)

        logger.info(
            "resource_released",
            incident_id=incident_id,
            resource_id=resource_id,
            released_by=released_by,
            audit_id=assignment.audit_id,
        )

        return assignment

    async def mark_resource_arrived(
        self,
        incident_id: str,
        resource_id: str,
        location: GeoLocation | None = None,
        updated_by: str | None = None,
    ) -> ResourceAssignment | None:
        """
        Mark a resource as arrived on scene.

        Args:
            incident_id: ID of incident
            resource_id: ID of resource
            location: Arrival location
            updated_by: User updating status

        Returns:
            Updated ResourceAssignment or None
        """
        assignments = self._assignments.get(incident_id, [])
        assignment = next(
            (a for a in assignments if a.resource_id == resource_id and a.is_active),
            None
        )

        if not assignment:
            return None

        assignment.arrival_time = datetime.now(UTC)

        # Update resource status
        resource = self._resources.get(resource_id)
        if resource:
            resource.status = ResourceStatus.ON_SCENE
            resource.updated_at = datetime.now(UTC)
            if location:
                resource.location = location

        # Log event
        event = ResourceEvent(
            incident_id=incident_id,
            resource_id=resource_id,
            event_type="resource_arrived",
            data={"location": location.model_dump() if location else None},
            user_id=updated_by,
        )
        self._events.append(event)

        logger.info(
            "resource_arrived",
            incident_id=incident_id,
            resource_id=resource_id,
            updated_by=updated_by,
        )

        return assignment

    async def create_resource_request(
        self,
        incident_id: str,
        resource_type: ResourceType,
        quantity: int = 1,
        priority: str = "normal",
        reason: str | None = None,
        requested_by: str | None = None,
    ) -> ResourceRequest:
        """
        Create a request for resources.

        Args:
            incident_id: ID of incident
            resource_type: Type of resource needed
            quantity: Number needed
            priority: Request priority
            reason: Reason for request
            requested_by: User making request

        Returns:
            Created ResourceRequest
        """
        request = ResourceRequest(
            incident_id=incident_id,
            resource_type=resource_type,
            quantity=quantity,
            priority=priority,
            reason=reason,
            requested_by=requested_by,
        )

        if incident_id not in self._requests:
            self._requests[incident_id] = []
        self._requests[incident_id].append(request)

        # Log event
        event = ResourceEvent(
            incident_id=incident_id,
            resource_id=request.id,
            event_type="resource_requested",
            data={
                "resource_type": resource_type,
                "quantity": quantity,
                "priority": priority,
            },
            user_id=requested_by,
        )
        self._events.append(event)

        logger.info(
            "resource_requested",
            incident_id=incident_id,
            resource_type=resource_type,
            quantity=quantity,
            requested_by=requested_by,
        )

        return request

    async def fulfill_resource_request(
        self,
        request_id: str,
        resource_ids: list[str],
        fulfilled_by: str | None = None,
    ) -> ResourceRequest | None:
        """
        Fulfill a resource request.

        Args:
            request_id: ID of request
            resource_ids: IDs of resources to assign
            fulfilled_by: User fulfilling request

        Returns:
            Updated ResourceRequest or None
        """
        # Find request
        request = None
        for requests in self._requests.values():
            for r in requests:
                if r.id == request_id:
                    request = r
                    break
            if request:
                break

        if not request:
            return None

        # Assign resources
        for resource_id in resource_ids:
            await self.assign_resource(
                incident_id=request.incident_id,
                resource_id=resource_id,
                assigned_by=fulfilled_by,
            )
            request.assigned_resources.append(resource_id)

        request.fulfilled = True
        request.fulfilled_at = datetime.now(UTC)
        request.fulfilled_by = fulfilled_by

        logger.info(
            "resource_request_fulfilled",
            request_id=request_id,
            resource_ids=resource_ids,
            fulfilled_by=fulfilled_by,
        )

        return request

    def get_resource(self, resource_id: str) -> Resource | None:
        """Get resource by ID."""
        return self._resources.get(resource_id)

    def get_resource_by_call_sign(self, call_sign: str) -> Resource | None:
        """Get resource by call sign."""
        for resource in self._resources.values():
            if resource.call_sign == call_sign:
                return resource
        return None

    async def get_available_resources(
        self,
        resource_type: ResourceType | None = None,
        agency_type: AgencyType | None = None,
        capability: str | None = None,
    ) -> list[Resource]:
        """
        Get available resources.

        Args:
            resource_type: Filter by type
            agency_type: Filter by agency type
            capability: Filter by capability

        Returns:
            List of available resources
        """
        resources = [
            r for r in self._resources.values()
            if r.status == ResourceStatus.AVAILABLE
        ]

        if resource_type:
            type_value = resource_type.value if isinstance(resource_type, ResourceType) else resource_type
            resources = [r for r in resources if r.resource_type == type_value]

        if agency_type:
            agency_value = agency_type.value if isinstance(agency_type, AgencyType) else agency_type
            resources = [r for r in resources if r.agency_type == agency_value]

        if capability:
            resources = [r for r in resources if capability in r.capabilities]

        return resources

    async def get_incident_resources(
        self,
        incident_id: str,
        active_only: bool = True,
    ) -> list[ResourceAssignment]:
        """
        Get resources assigned to an incident.

        Args:
            incident_id: ID of incident
            active_only: Only return active assignments

        Returns:
            List of ResourceAssignment
        """
        assignments = self._assignments.get(incident_id, [])
        if active_only:
            assignments = [a for a in assignments if a.is_active]
        return assignments

    async def get_incident_requests(
        self,
        incident_id: str,
        pending_only: bool = False,
    ) -> list[ResourceRequest]:
        """
        Get resource requests for an incident.

        Args:
            incident_id: ID of incident
            pending_only: Only return unfulfilled requests

        Returns:
            List of ResourceRequest
        """
        requests = self._requests.get(incident_id, [])
        if pending_only:
            requests = [r for r in requests if not r.fulfilled]
        return requests

    async def get_all_resources(
        self,
        status: ResourceStatus | None = None,
        resource_type: ResourceType | None = None,
    ) -> list[Resource]:
        """
        Get all resources.

        Args:
            status: Filter by status
            resource_type: Filter by type

        Returns:
            List of resources
        """
        resources = list(self._resources.values())

        if status:
            status_value = status.value if isinstance(status, ResourceStatus) else status
            resources = [r for r in resources if r.status == status_value]

        if resource_type:
            type_value = resource_type.value if isinstance(resource_type, ResourceType) else resource_type
            resources = [r for r in resources if r.resource_type == type_value]

        return resources

    async def get_resource_statistics(
        self,
        incident_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get resource statistics.

        Args:
            incident_id: Optional incident ID for incident-specific stats

        Returns:
            Dictionary of statistics
        """
        all_resources = list(self._resources.values())

        # Count by status
        by_status: dict[str, int] = {}
        for resource in all_resources:
            status = resource.status
            by_status[status] = by_status.get(status, 0) + 1

        # Count by type
        by_type: dict[str, int] = {}
        for resource in all_resources:
            rtype = resource.resource_type
            by_type[rtype] = by_type.get(rtype, 0) + 1

        # Count by agency type
        by_agency: dict[str, int] = {}
        for resource in all_resources:
            agency = resource.agency_type
            by_agency[agency] = by_agency.get(agency, 0) + 1

        stats = {
            "total_resources": len(all_resources),
            "by_status": by_status,
            "by_type": by_type,
            "by_agency_type": by_agency,
            "available_count": by_status.get(ResourceStatus.AVAILABLE.value, 0),
            "assigned_count": by_status.get(ResourceStatus.ASSIGNED.value, 0) + by_status.get(ResourceStatus.ON_SCENE.value, 0),
        }

        if incident_id:
            assignments = self._assignments.get(incident_id, [])
            active_assignments = [a for a in assignments if a.is_active]
            requests = self._requests.get(incident_id, [])
            pending_requests = [r for r in requests if not r.fulfilled]

            stats["incident_assigned"] = len(active_assignments)
            stats["incident_pending_requests"] = len(pending_requests)
            stats["incident_total_personnel"] = sum(
                self._resources.get(a.resource_id, Resource(resource_type=ResourceType.PATROL_UNIT, name="")).personnel_count
                for a in active_assignments
                if self._resources.get(a.resource_id)
            )

        return stats

    async def get_events(
        self,
        incident_id: str | None = None,
        resource_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[ResourceEvent]:
        """
        Get resource events.

        Args:
            incident_id: Filter by incident
            resource_id: Filter by resource
            event_type: Filter by event type
            limit: Maximum number to return

        Returns:
            List of ResourceEvent
        """
        events = self._events.copy()

        if incident_id:
            events = [e for e in events if e.incident_id == incident_id]

        if resource_id:
            events = [e for e in events if e.resource_id == resource_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]
