"""
Multi-Agency Coordination Interface for G3TI RTCC-UIP.

Provides coordination with external agencies including Fire, EMS,
County Sheriff, and regional partners with CJIS-compliant data sharing.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


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
    HOSPITAL = "hospital"
    UTILITIES = "utilities"
    TRANSPORTATION = "transportation"
    SCHOOL = "school"
    PRIVATE_SECURITY = "private_security"
    OTHER = "other"


class AccessLevel(str, Enum):
    """Access levels for agency participation."""

    FULL = "full"
    RESTRICTED = "restricted"
    READ_ONLY = "read_only"
    COMMUNICATIONS_ONLY = "communications_only"
    NONE = "none"


class DataCategory(str, Enum):
    """Categories of data that can be shared."""

    INCIDENT_OVERVIEW = "incident_overview"
    TIMELINE = "timeline"
    ICS_STRUCTURE = "ics_structure"
    RESOURCES = "resources"
    STRATEGY_MAP = "strategy_map"
    COMMUNICATIONS = "communications"
    INTELLIGENCE = "intelligence"
    OFFICER_SAFETY = "officer_safety"
    SENSITIVE = "sensitive"


class AgencyContact(BaseModel):
    """Contact information for an agency."""

    name: str
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    radio_channel: str | None = None
    is_primary: bool = False


class Agency(BaseModel):
    """Agency model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agency_type: AgencyType
    name: str
    abbreviation: str | None = None
    jurisdiction: str | None = None
    address: str | None = None
    dispatch_phone: str | None = None
    dispatch_radio: str | None = None
    contacts: list[AgencyContact] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    is_mutual_aid: bool = False
    mou_on_file: bool = False
    cjis_compliant: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    audit_id: str = Field(default_factory=lambda: f"AUDIT-AG-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class AgencyParticipation(BaseModel):
    """Agency participation in an incident."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    agency_id: str
    agency_name: str
    agency_type: AgencyType
    access_level: AccessLevel = AccessLevel.READ_ONLY
    allowed_data: list[DataCategory] = Field(default_factory=list)
    denied_data: list[DataCategory] = Field(default_factory=list)
    liaison_badge: str | None = None
    liaison_name: str | None = None
    liaison_contact: str | None = None
    radio_channel: str | None = None
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    added_by: str | None = None
    left_at: datetime | None = None
    is_active: bool = True
    notes: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-AP-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class SharedChannel(BaseModel):
    """Shared communication channel between agencies."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    name: str
    channel_type: str = "radio"
    frequency: str | None = None
    talk_group: str | None = None
    participating_agencies: list[str] = Field(default_factory=list)
    is_primary: bool = False
    is_encrypted: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None


class DataShareRequest(BaseModel):
    """Request to share data with an agency."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    requesting_agency_id: str
    data_category: DataCategory
    reason: str | None = None
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    requested_by: str | None = None
    approved: bool | None = None
    approved_at: datetime | None = None
    approved_by: str | None = None
    denial_reason: str | None = None
    expires_at: datetime | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-DSR-{uuid.uuid4().hex[:12].upper()}")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class MultiAgencyEvent(BaseModel):
    """Event related to multi-agency coordination."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    event_type: str
    agency_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    user_id: str | None = None
    audit_id: str = Field(default_factory=lambda: f"AUDIT-MAE-{uuid.uuid4().hex[:12].upper()}")


class MultiAgencyCoordinator:
    """
    Coordinator for multi-agency operations.

    Provides agency management, access control, data sharing,
    and communication channel coordination with CJIS compliance.
    """

    def __init__(self) -> None:
        """Initialize the multi-agency coordinator."""
        self._agencies: dict[str, Agency] = {}
        self._participations: dict[str, list[AgencyParticipation]] = {}  # incident_id -> participations
        self._channels: dict[str, list[SharedChannel]] = {}  # incident_id -> channels
        self._share_requests: dict[str, list[DataShareRequest]] = {}  # incident_id -> requests
        self._events: list[MultiAgencyEvent] = []

        # Initialize default agencies
        self._init_default_agencies()

        # Define default data access by agency type
        self._default_access = self._init_default_access()

        logger.info("multiagency_coordinator_initialized")

    def _init_default_agencies(self) -> None:
        """Initialize default agencies."""
        default_agencies = [
            Agency(
                agency_type=AgencyType.FIRE,
                name="City Fire Department",
                abbreviation="CFD",
                dispatch_phone="555-FIRE",
                capabilities=["fire_suppression", "rescue", "hazmat", "ems"],
            ),
            Agency(
                agency_type=AgencyType.EMS,
                name="County EMS",
                abbreviation="CEMS",
                dispatch_phone="555-EMS1",
                capabilities=["basic_life_support", "advanced_life_support", "critical_care"],
            ),
            Agency(
                agency_type=AgencyType.SHERIFF,
                name="County Sheriff's Office",
                abbreviation="CCSO",
                dispatch_phone="555-SHRF",
                capabilities=["patrol", "investigations", "swat", "k9", "aviation"],
                is_mutual_aid=True,
                mou_on_file=True,
            ),
            Agency(
                agency_type=AgencyType.STATE_POLICE,
                name="State Highway Patrol",
                abbreviation="SHP",
                dispatch_phone="555-STAT",
                capabilities=["traffic", "pursuit", "investigations", "aviation"],
                is_mutual_aid=True,
            ),
            Agency(
                agency_type=AgencyType.EMERGENCY_MANAGEMENT,
                name="County Emergency Management",
                abbreviation="CEM",
                dispatch_phone="555-EMGT",
                capabilities=["coordination", "shelters", "evacuation", "public_info"],
            ),
            Agency(
                agency_type=AgencyType.HOSPITAL,
                name="Regional Medical Center",
                abbreviation="RMC",
                dispatch_phone="555-HOSP",
                capabilities=["trauma", "burn", "pediatric"],
            ),
        ]

        for agency in default_agencies:
            self._agencies[agency.id] = agency

    def _init_default_access(self) -> dict[AgencyType, dict[str, Any]]:
        """Initialize default access levels by agency type."""
        return {
            AgencyType.FIRE: {
                "access_level": AccessLevel.RESTRICTED,
                "allowed_data": [
                    DataCategory.INCIDENT_OVERVIEW,
                    DataCategory.TIMELINE,
                    DataCategory.RESOURCES,
                    DataCategory.STRATEGY_MAP,
                    DataCategory.COMMUNICATIONS,
                ],
                "denied_data": [
                    DataCategory.INTELLIGENCE,
                    DataCategory.SENSITIVE,
                ],
            },
            AgencyType.EMS: {
                "access_level": AccessLevel.RESTRICTED,
                "allowed_data": [
                    DataCategory.INCIDENT_OVERVIEW,
                    DataCategory.TIMELINE,
                    DataCategory.RESOURCES,
                    DataCategory.COMMUNICATIONS,
                ],
                "denied_data": [
                    DataCategory.INTELLIGENCE,
                    DataCategory.SENSITIVE,
                    DataCategory.OFFICER_SAFETY,
                ],
            },
            AgencyType.SHERIFF: {
                "access_level": AccessLevel.FULL,
                "allowed_data": list(DataCategory),
                "denied_data": [],
            },
            AgencyType.STATE_POLICE: {
                "access_level": AccessLevel.FULL,
                "allowed_data": list(DataCategory),
                "denied_data": [],
            },
            AgencyType.FEDERAL: {
                "access_level": AccessLevel.RESTRICTED,
                "allowed_data": [
                    DataCategory.INCIDENT_OVERVIEW,
                    DataCategory.TIMELINE,
                    DataCategory.ICS_STRUCTURE,
                    DataCategory.RESOURCES,
                    DataCategory.COMMUNICATIONS,
                ],
                "denied_data": [
                    DataCategory.SENSITIVE,
                ],
            },
            AgencyType.EMERGENCY_MANAGEMENT: {
                "access_level": AccessLevel.RESTRICTED,
                "allowed_data": [
                    DataCategory.INCIDENT_OVERVIEW,
                    DataCategory.TIMELINE,
                    DataCategory.ICS_STRUCTURE,
                    DataCategory.RESOURCES,
                    DataCategory.STRATEGY_MAP,
                    DataCategory.COMMUNICATIONS,
                ],
                "denied_data": [
                    DataCategory.INTELLIGENCE,
                    DataCategory.SENSITIVE,
                    DataCategory.OFFICER_SAFETY,
                ],
            },
            AgencyType.HOSPITAL: {
                "access_level": AccessLevel.READ_ONLY,
                "allowed_data": [
                    DataCategory.INCIDENT_OVERVIEW,
                    DataCategory.TIMELINE,
                ],
                "denied_data": [
                    DataCategory.INTELLIGENCE,
                    DataCategory.SENSITIVE,
                    DataCategory.OFFICER_SAFETY,
                    DataCategory.STRATEGY_MAP,
                ],
            },
        }

    async def register_agency(
        self,
        agency_type: AgencyType,
        name: str,
        abbreviation: str | None = None,
        jurisdiction: str | None = None,
        dispatch_phone: str | None = None,
        dispatch_radio: str | None = None,
        capabilities: list[str] | None = None,
        is_mutual_aid: bool = False,
        mou_on_file: bool = False,
        cjis_compliant: bool = True,
    ) -> Agency:
        """
        Register a new agency.

        Args:
            agency_type: Type of agency
            name: Agency name
            abbreviation: Agency abbreviation
            jurisdiction: Jurisdiction area
            dispatch_phone: Dispatch phone number
            dispatch_radio: Dispatch radio channel
            capabilities: List of capabilities
            is_mutual_aid: Whether mutual aid partner
            mou_on_file: Whether MOU is on file
            cjis_compliant: Whether CJIS compliant

        Returns:
            Created Agency
        """
        agency = Agency(
            agency_type=agency_type,
            name=name,
            abbreviation=abbreviation,
            jurisdiction=jurisdiction,
            dispatch_phone=dispatch_phone,
            dispatch_radio=dispatch_radio,
            capabilities=capabilities or [],
            is_mutual_aid=is_mutual_aid,
            mou_on_file=mou_on_file,
            cjis_compliant=cjis_compliant,
        )

        self._agencies[agency.id] = agency

        logger.info(
            "agency_registered",
            agency_id=agency.id,
            agency_type=agency_type,
            name=name,
            audit_id=agency.audit_id,
        )

        return agency

    async def add_agency_contact(
        self,
        agency_id: str,
        name: str,
        title: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        radio_channel: str | None = None,
        is_primary: bool = False,
    ) -> Agency | None:
        """
        Add a contact to an agency.

        Args:
            agency_id: ID of agency
            name: Contact name
            title: Contact title
            phone: Phone number
            email: Email address
            radio_channel: Radio channel
            is_primary: Whether primary contact

        Returns:
            Updated Agency or None
        """
        agency = self._agencies.get(agency_id)
        if not agency:
            return None

        contact = AgencyContact(
            name=name,
            title=title,
            phone=phone,
            email=email,
            radio_channel=radio_channel,
            is_primary=is_primary,
        )

        # If this is primary, unset other primary contacts
        if is_primary:
            for c in agency.contacts:
                c.is_primary = False

        agency.contacts.append(contact)

        return agency

    async def add_agency_to_incident(
        self,
        incident_id: str,
        agency_id: str,
        access_level: AccessLevel | None = None,
        liaison_badge: str | None = None,
        liaison_name: str | None = None,
        liaison_contact: str | None = None,
        radio_channel: str | None = None,
        added_by: str | None = None,
        notes: str | None = None,
    ) -> AgencyParticipation | None:
        """
        Add an agency to an incident.

        Args:
            incident_id: ID of incident
            agency_id: ID of agency
            access_level: Access level (defaults based on agency type)
            liaison_badge: Liaison officer badge
            liaison_name: Liaison officer name
            liaison_contact: Liaison contact info
            radio_channel: Assigned radio channel
            added_by: User adding agency
            notes: Notes about participation

        Returns:
            Created AgencyParticipation or None
        """
        agency = self._agencies.get(agency_id)
        if not agency:
            return None

        # Get default access based on agency type
        agency_type = AgencyType(agency.agency_type) if isinstance(agency.agency_type, str) else agency.agency_type
        default_access = self._default_access.get(agency_type, {})

        # Determine access level
        if access_level is None:
            access_level = default_access.get("access_level", AccessLevel.READ_ONLY)

        # Determine allowed/denied data
        allowed_data = default_access.get("allowed_data", [DataCategory.INCIDENT_OVERVIEW])
        denied_data = default_access.get("denied_data", [DataCategory.SENSITIVE])

        participation = AgencyParticipation(
            incident_id=incident_id,
            agency_id=agency_id,
            agency_name=agency.name,
            agency_type=agency.agency_type,
            access_level=access_level,
            allowed_data=allowed_data,
            denied_data=denied_data,
            liaison_badge=liaison_badge,
            liaison_name=liaison_name,
            liaison_contact=liaison_contact,
            radio_channel=radio_channel,
            added_by=added_by,
            notes=notes,
        )

        if incident_id not in self._participations:
            self._participations[incident_id] = []
        self._participations[incident_id].append(participation)

        # Log event
        event = MultiAgencyEvent(
            incident_id=incident_id,
            event_type="agency_added",
            agency_id=agency_id,
            data={
                "agency_name": agency.name,
                "access_level": access_level,
            },
            user_id=added_by,
        )
        self._events.append(event)

        logger.info(
            "agency_added_to_incident",
            incident_id=incident_id,
            agency_id=agency_id,
            agency_name=agency.name,
            access_level=access_level,
            added_by=added_by,
            audit_id=participation.audit_id,
        )

        return participation

    async def remove_agency_from_incident(
        self,
        incident_id: str,
        agency_id: str,
        removed_by: str | None = None,
        reason: str | None = None,
    ) -> AgencyParticipation | None:
        """
        Remove an agency from an incident.

        Args:
            incident_id: ID of incident
            agency_id: ID of agency
            removed_by: User removing agency
            reason: Reason for removal

        Returns:
            Updated AgencyParticipation or None
        """
        participations = self._participations.get(incident_id, [])
        participation = next(
            (p for p in participations if p.agency_id == agency_id and p.is_active),
            None
        )

        if not participation:
            return None

        participation.is_active = False
        participation.left_at = datetime.now(UTC)
        if reason:
            participation.notes = (participation.notes or "") + f" | Removed: {reason}"

        # Log event
        event = MultiAgencyEvent(
            incident_id=incident_id,
            event_type="agency_removed",
            agency_id=agency_id,
            data={"reason": reason},
            user_id=removed_by,
        )
        self._events.append(event)

        logger.info(
            "agency_removed_from_incident",
            incident_id=incident_id,
            agency_id=agency_id,
            removed_by=removed_by,
            audit_id=participation.audit_id,
        )

        return participation

    async def update_agency_access(
        self,
        incident_id: str,
        agency_id: str,
        access_level: AccessLevel | None = None,
        allowed_data: list[DataCategory] | None = None,
        denied_data: list[DataCategory] | None = None,
        updated_by: str | None = None,
    ) -> AgencyParticipation | None:
        """
        Update agency access level.

        Args:
            incident_id: ID of incident
            agency_id: ID of agency
            access_level: New access level
            allowed_data: New allowed data categories
            denied_data: New denied data categories
            updated_by: User updating access

        Returns:
            Updated AgencyParticipation or None
        """
        participations = self._participations.get(incident_id, [])
        participation = next(
            (p for p in participations if p.agency_id == agency_id and p.is_active),
            None
        )

        if not participation:
            return None

        if access_level is not None:
            participation.access_level = access_level
        if allowed_data is not None:
            participation.allowed_data = allowed_data
        if denied_data is not None:
            participation.denied_data = denied_data

        # Log event
        event = MultiAgencyEvent(
            incident_id=incident_id,
            event_type="agency_access_updated",
            agency_id=agency_id,
            data={
                "access_level": access_level,
                "allowed_data": [d.value if isinstance(d, DataCategory) else d for d in (allowed_data or [])],
            },
            user_id=updated_by,
        )
        self._events.append(event)

        logger.info(
            "agency_access_updated",
            incident_id=incident_id,
            agency_id=agency_id,
            access_level=access_level,
            updated_by=updated_by,
        )

        return participation

    async def create_shared_channel(
        self,
        incident_id: str,
        name: str,
        channel_type: str = "radio",
        frequency: str | None = None,
        talk_group: str | None = None,
        participating_agencies: list[str] | None = None,
        is_primary: bool = False,
        is_encrypted: bool = True,
        created_by: str | None = None,
    ) -> SharedChannel:
        """
        Create a shared communication channel.

        Args:
            incident_id: ID of incident
            name: Channel name
            channel_type: Type of channel
            frequency: Radio frequency
            talk_group: Talk group ID
            participating_agencies: List of agency IDs
            is_primary: Whether primary channel
            is_encrypted: Whether encrypted
            created_by: User creating channel

        Returns:
            Created SharedChannel
        """
        channel = SharedChannel(
            incident_id=incident_id,
            name=name,
            channel_type=channel_type,
            frequency=frequency,
            talk_group=talk_group,
            participating_agencies=participating_agencies or [],
            is_primary=is_primary,
            is_encrypted=is_encrypted,
            created_by=created_by,
        )

        if incident_id not in self._channels:
            self._channels[incident_id] = []
        self._channels[incident_id].append(channel)

        # Log event
        event = MultiAgencyEvent(
            incident_id=incident_id,
            event_type="shared_channel_created",
            data={
                "channel_name": name,
                "channel_type": channel_type,
            },
            user_id=created_by,
        )
        self._events.append(event)

        logger.info(
            "shared_channel_created",
            incident_id=incident_id,
            channel_id=channel.id,
            name=name,
            created_by=created_by,
        )

        return channel

    async def request_data_share(
        self,
        incident_id: str,
        requesting_agency_id: str,
        data_category: DataCategory,
        reason: str | None = None,
        requested_by: str | None = None,
    ) -> DataShareRequest:
        """
        Request access to a data category.

        Args:
            incident_id: ID of incident
            requesting_agency_id: ID of requesting agency
            data_category: Category of data requested
            reason: Reason for request
            requested_by: User making request

        Returns:
            Created DataShareRequest
        """
        request = DataShareRequest(
            incident_id=incident_id,
            requesting_agency_id=requesting_agency_id,
            data_category=data_category,
            reason=reason,
            requested_by=requested_by,
        )

        if incident_id not in self._share_requests:
            self._share_requests[incident_id] = []
        self._share_requests[incident_id].append(request)

        # Log event
        event = MultiAgencyEvent(
            incident_id=incident_id,
            event_type="data_share_requested",
            agency_id=requesting_agency_id,
            data={
                "data_category": data_category,
                "reason": reason,
            },
            user_id=requested_by,
        )
        self._events.append(event)

        logger.info(
            "data_share_requested",
            incident_id=incident_id,
            agency_id=requesting_agency_id,
            data_category=data_category,
            audit_id=request.audit_id,
        )

        return request

    async def approve_data_share(
        self,
        incident_id: str,
        request_id: str,
        approved_by: str,
        expires_at: datetime | None = None,
    ) -> DataShareRequest | None:
        """
        Approve a data share request.

        Args:
            incident_id: ID of incident
            request_id: ID of request
            approved_by: User approving
            expires_at: Expiration time

        Returns:
            Updated DataShareRequest or None
        """
        requests = self._share_requests.get(incident_id, [])
        request = next((r for r in requests if r.id == request_id), None)

        if not request:
            return None

        request.approved = True
        request.approved_at = datetime.now(UTC)
        request.approved_by = approved_by
        request.expires_at = expires_at

        # Update agency participation to include this data category
        participations = self._participations.get(incident_id, [])
        participation = next(
            (p for p in participations if p.agency_id == request.requesting_agency_id and p.is_active),
            None
        )

        if participation:
            data_cat = DataCategory(request.data_category) if isinstance(request.data_category, str) else request.data_category
            if data_cat not in participation.allowed_data:
                participation.allowed_data.append(data_cat)
            if data_cat in participation.denied_data:
                participation.denied_data.remove(data_cat)

        # Log event
        event = MultiAgencyEvent(
            incident_id=incident_id,
            event_type="data_share_approved",
            agency_id=request.requesting_agency_id,
            data={
                "data_category": request.data_category,
            },
            user_id=approved_by,
        )
        self._events.append(event)

        logger.info(
            "data_share_approved",
            incident_id=incident_id,
            request_id=request_id,
            approved_by=approved_by,
            audit_id=request.audit_id,
        )

        return request

    async def deny_data_share(
        self,
        incident_id: str,
        request_id: str,
        denied_by: str,
        reason: str | None = None,
    ) -> DataShareRequest | None:
        """
        Deny a data share request.

        Args:
            incident_id: ID of incident
            request_id: ID of request
            denied_by: User denying
            reason: Denial reason

        Returns:
            Updated DataShareRequest or None
        """
        requests = self._share_requests.get(incident_id, [])
        request = next((r for r in requests if r.id == request_id), None)

        if not request:
            return None

        request.approved = False
        request.approved_at = datetime.now(UTC)
        request.approved_by = denied_by
        request.denial_reason = reason

        # Log event
        event = MultiAgencyEvent(
            incident_id=incident_id,
            event_type="data_share_denied",
            agency_id=request.requesting_agency_id,
            data={
                "data_category": request.data_category,
                "reason": reason,
            },
            user_id=denied_by,
        )
        self._events.append(event)

        logger.info(
            "data_share_denied",
            incident_id=incident_id,
            request_id=request_id,
            denied_by=denied_by,
            reason=reason,
            audit_id=request.audit_id,
        )

        return request

    def can_access_data(
        self,
        incident_id: str,
        agency_id: str,
        data_category: DataCategory,
    ) -> bool:
        """
        Check if an agency can access a data category.

        Args:
            incident_id: ID of incident
            agency_id: ID of agency
            data_category: Category to check

        Returns:
            True if agency can access
        """
        participations = self._participations.get(incident_id, [])
        participation = next(
            (p for p in participations if p.agency_id == agency_id and p.is_active),
            None
        )

        if not participation:
            return False

        # Check if explicitly denied
        data_cat_value = data_category.value if isinstance(data_category, DataCategory) else data_category
        denied_values = [d.value if isinstance(d, DataCategory) else d for d in participation.denied_data]
        if data_cat_value in denied_values:
            return False

        # Check if explicitly allowed
        allowed_values = [d.value if isinstance(d, DataCategory) else d for d in participation.allowed_data]
        if data_cat_value in allowed_values:
            return True

        # Check access level
        access = participation.access_level
        if access == AccessLevel.FULL.value or access == AccessLevel.FULL:
            return True

        return False

    def get_agency(self, agency_id: str) -> Agency | None:
        """Get agency by ID."""
        return self._agencies.get(agency_id)

    def get_agency_by_name(self, name: str) -> Agency | None:
        """Get agency by name."""
        for agency in self._agencies.values():
            if agency.name.lower() == name.lower():
                return agency
        return None

    async def get_all_agencies(
        self,
        agency_type: AgencyType | None = None,
    ) -> list[Agency]:
        """
        Get all registered agencies.

        Args:
            agency_type: Filter by type

        Returns:
            List of agencies
        """
        agencies = list(self._agencies.values())

        if agency_type:
            type_value = agency_type.value if isinstance(agency_type, AgencyType) else agency_type
            agencies = [a for a in agencies if a.agency_type == type_value]

        return agencies

    async def get_incident_agencies(
        self,
        incident_id: str,
        active_only: bool = True,
    ) -> list[AgencyParticipation]:
        """
        Get agencies participating in an incident.

        Args:
            incident_id: ID of incident
            active_only: Only return active participations

        Returns:
            List of AgencyParticipation
        """
        participations = self._participations.get(incident_id, [])
        if active_only:
            participations = [p for p in participations if p.is_active]
        return participations

    async def get_shared_channels(
        self,
        incident_id: str,
    ) -> list[SharedChannel]:
        """
        Get shared channels for an incident.

        Args:
            incident_id: ID of incident

        Returns:
            List of SharedChannel
        """
        return self._channels.get(incident_id, [])

    async def get_pending_share_requests(
        self,
        incident_id: str,
    ) -> list[DataShareRequest]:
        """
        Get pending data share requests.

        Args:
            incident_id: ID of incident

        Returns:
            List of pending DataShareRequest
        """
        requests = self._share_requests.get(incident_id, [])
        return [r for r in requests if r.approved is None]

    async def get_events(
        self,
        incident_id: str,
        event_type: str | None = None,
        agency_id: str | None = None,
        limit: int = 100,
    ) -> list[MultiAgencyEvent]:
        """
        Get multi-agency events.

        Args:
            incident_id: ID of incident
            event_type: Filter by event type
            agency_id: Filter by agency
            limit: Maximum number to return

        Returns:
            List of MultiAgencyEvent
        """
        events = [e for e in self._events if e.incident_id == incident_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if agency_id:
            events = [e for e in events if e.agency_id == agency_id]

        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]

    async def get_coordination_statistics(
        self,
        incident_id: str,
    ) -> dict[str, Any]:
        """
        Get statistics about multi-agency coordination.

        Args:
            incident_id: ID of incident

        Returns:
            Dictionary of statistics
        """
        participations = self._participations.get(incident_id, [])
        active_participations = [p for p in participations if p.is_active]
        channels = self._channels.get(incident_id, [])
        requests = self._share_requests.get(incident_id, [])

        # Count by agency type
        by_type: dict[str, int] = {}
        for p in active_participations:
            by_type[p.agency_type] = by_type.get(p.agency_type, 0) + 1

        # Count by access level
        by_access: dict[str, int] = {}
        for p in active_participations:
            by_access[p.access_level] = by_access.get(p.access_level, 0) + 1

        return {
            "total_agencies": len(active_participations),
            "total_channels": len(channels),
            "pending_requests": len([r for r in requests if r.approved is None]),
            "approved_requests": len([r for r in requests if r.approved is True]),
            "denied_requests": len([r for r in requests if r.approved is False]),
            "by_agency_type": by_type,
            "by_access_level": by_access,
        }
