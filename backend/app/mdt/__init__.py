"""
G3TI RTCC-UIP MDT (Mobile Data Terminal) Module
CAD call visibility, unit assignment, scene coordination, and officer status management.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MDTUnitStatus(str, Enum):
    """MDT unit status codes."""
    AVAILABLE = "available"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    TRANSPORTING = "transporting"
    AT_HOSPITAL = "at_hospital"
    REPORTS = "reports"
    OUT_OF_SERVICE = "out_of_service"
    OFF_DUTY = "off_duty"
    MEAL = "meal"
    TRAINING = "training"
    COURT = "court"
    ADMINISTRATIVE = "administrative"


class CADCallPriority(str, Enum):
    """CAD call priority levels."""
    PRIORITY_1 = "1"
    PRIORITY_2 = "2"
    PRIORITY_3 = "3"
    PRIORITY_4 = "4"
    PRIORITY_5 = "5"


class CADCallStatus(str, Enum):
    """CAD call status."""
    PENDING = "pending"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    TRANSPORTING = "transporting"
    CLEARED = "cleared"
    CANCELLED = "cancelled"


class SceneRole(str, Enum):
    """Scene coordination roles."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    BACKUP = "backup"
    SUPERVISOR = "supervisor"
    INVESTIGATOR = "investigator"
    TRAFFIC = "traffic"
    PERIMETER = "perimeter"
    MEDICAL = "medical"
    FIRE = "fire"
    OTHER = "other"


class MDTUnit(BaseModel):
    """MDT unit information."""
    unit_id: str
    badge_number: str
    officer_name: str
    call_sign: str
    status: MDTUnitStatus = MDTUnitStatus.AVAILABLE
    current_call_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_description: str | None = None
    vehicle_id: str | None = None
    radio_id: str | None = None
    district: str | None = None
    beat: str | None = None
    shift: str | None = None
    last_status_change: datetime = Field(default_factory=datetime.utcnow)
    status_notes: str | None = None

    class Config:
        use_enum_values = True


class CADCall(BaseModel):
    """CAD call for MDT display."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    call_number: str
    call_type: str
    call_type_code: str | None = None
    priority: CADCallPriority
    status: CADCallStatus = CADCallStatus.PENDING
    location: str
    address: str | None = None
    apartment: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    cross_streets: str | None = None
    common_place: str | None = None
    description: str | None = None
    caller_name: str | None = None
    caller_phone: str | None = None
    caller_location: str | None = None
    assigned_units: list[str] = Field(default_factory=list)
    primary_unit: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    dispatched_at: datetime | None = None
    en_route_at: datetime | None = None
    on_scene_at: datetime | None = None
    cleared_at: datetime | None = None
    disposition: str | None = None
    notes: list[dict[str, Any]] = Field(default_factory=list)
    hazards: list[str] = Field(default_factory=list)
    premise_history: list[str] = Field(default_factory=list)
    related_calls: list[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class CADNote(BaseModel):
    """CAD call note."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    call_id: str
    author_badge: str
    author_name: str
    content: str
    note_type: str = "general"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_rtcc: bool = False


class SceneAssignment(BaseModel):
    """Scene unit assignment."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    call_id: str
    unit_id: str
    badge_number: str
    officer_name: str
    role: SceneRole
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_by: str | None = None
    notes: str | None = None

    class Config:
        use_enum_values = True


class SceneCoordination(BaseModel):
    """Scene coordination information."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    call_id: str
    incident_commander: str | None = None
    staging_location: str | None = None
    staging_lat: float | None = None
    staging_lng: float | None = None
    perimeter_established: bool = False
    perimeter_notes: str | None = None
    assignments: list[SceneAssignment] = Field(default_factory=list)
    resources_requested: list[str] = Field(default_factory=list)
    resources_on_scene: list[str] = Field(default_factory=list)
    tactical_notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UnitStatusHistory(BaseModel):
    """Unit status change history."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    unit_id: str
    badge_number: str
    previous_status: MDTUnitStatus
    new_status: MDTUnitStatus
    call_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    changed_by: str | None = None

    class Config:
        use_enum_values = True


class MDTMessage(BaseModel):
    """MDT messaging."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_badge: str
    sender_name: str
    sender_type: str = "officer"
    recipient_badges: list[str] = Field(default_factory=list)
    recipient_units: list[str] = Field(default_factory=list)
    call_id: str | None = None
    content: str
    priority: str = "normal"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_by: list[str] = Field(default_factory=list)
    is_broadcast: bool = False


class MDTManager:
    """
    MDT (Mobile Data Terminal) Manager.
    Handles CAD call visibility, unit status, and scene coordination.
    """

    def __init__(self) -> None:
        """Initialize the MDT manager."""
        self._units: dict[str, MDTUnit] = {}
        self._calls: dict[str, CADCall] = {}
        self._call_notes: dict[str, list[CADNote]] = {}
        self._scene_coordination: dict[str, SceneCoordination] = {}
        self._status_history: dict[str, list[UnitStatusHistory]] = {}
        self._messages: dict[str, MDTMessage] = {}

    async def register_unit(
        self,
        unit_id: str,
        badge_number: str,
        officer_name: str,
        call_sign: str,
        vehicle_id: str | None = None,
        radio_id: str | None = None,
        district: str | None = None,
        beat: str | None = None,
        shift: str | None = None,
    ) -> MDTUnit:
        """
        Register or update an MDT unit.

        Args:
            unit_id: Unit ID
            badge_number: Officer badge number
            officer_name: Officer name
            call_sign: Radio call sign
            vehicle_id: Vehicle ID
            radio_id: Radio ID
            district: Patrol district
            beat: Patrol beat
            shift: Shift assignment

        Returns:
            Registered unit
        """
        unit = MDTUnit(
            unit_id=unit_id,
            badge_number=badge_number,
            officer_name=officer_name,
            call_sign=call_sign,
            vehicle_id=vehicle_id,
            radio_id=radio_id,
            district=district,
            beat=beat,
            shift=shift,
        )

        self._units[badge_number] = unit
        return unit

    async def update_unit_status(
        self,
        badge_number: str,
        status: MDTUnitStatus,
        call_id: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        location_description: str | None = None,
        notes: str | None = None,
        changed_by: str | None = None,
    ) -> MDTUnit | None:
        """
        Update unit status.

        Args:
            badge_number: Officer badge number
            status: New status
            call_id: Associated call ID
            latitude: GPS latitude
            longitude: GPS longitude
            location_description: Location description
            notes: Status notes
            changed_by: Who changed the status

        Returns:
            Updated unit or None
        """
        unit = self._units.get(badge_number)
        if not unit:
            return None

        # Record history
        history = UnitStatusHistory(
            unit_id=unit.unit_id,
            badge_number=badge_number,
            previous_status=unit.status,
            new_status=status,
            call_id=call_id,
            latitude=latitude,
            longitude=longitude,
            notes=notes,
            changed_by=changed_by,
        )

        if badge_number not in self._status_history:
            self._status_history[badge_number] = []
        self._status_history[badge_number].append(history)

        # Update unit
        unit.status = status
        unit.current_call_id = call_id
        unit.latitude = latitude
        unit.longitude = longitude
        unit.location_description = location_description
        unit.status_notes = notes
        unit.last_status_change = datetime.utcnow()

        # Update call timestamps if applicable
        if call_id:
            call = self._calls.get(call_id)
            if call:
                if status == MDTUnitStatus.EN_ROUTE and not call.en_route_at:
                    call.en_route_at = datetime.utcnow()
                    call.status = CADCallStatus.EN_ROUTE
                elif status == MDTUnitStatus.ON_SCENE and not call.on_scene_at:
                    call.on_scene_at = datetime.utcnow()
                    call.status = CADCallStatus.ON_SCENE

        return unit

    async def get_unit_status(self, badge_number: str) -> MDTUnit | None:
        """Get unit status by badge number."""
        return self._units.get(badge_number)

    async def get_unit_by_id(self, unit_id: str) -> MDTUnit | None:
        """Get unit by unit ID."""
        for unit in self._units.values():
            if unit.unit_id == unit_id:
                return unit
        return None

    async def get_all_units(
        self,
        status: MDTUnitStatus | None = None,
        district: str | None = None,
    ) -> list[MDTUnit]:
        """
        Get all units with optional filters.

        Args:
            status: Filter by status
            district: Filter by district

        Returns:
            List of units
        """
        units = list(self._units.values())

        if status:
            units = [u for u in units if u.status == status]
        if district:
            units = [u for u in units if u.district == district]

        return units

    async def get_status_history(
        self,
        badge_number: str,
        limit: int = 50,
        since: datetime | None = None,
    ) -> list[UnitStatusHistory]:
        """
        Get unit status history.

        Args:
            badge_number: Officer badge number
            limit: Maximum records
            since: Only records after this time

        Returns:
            List of status history
        """
        history = self._status_history.get(badge_number, [])

        if since:
            history = [h for h in history if h.changed_at > since]

        return sorted(history, key=lambda h: h.changed_at, reverse=True)[:limit]

    async def add_cad_call(self, call: CADCall) -> CADCall:
        """Add or update a CAD call."""
        self._calls[call.id] = call
        return call

    async def get_cad_call(self, call_id: str) -> CADCall | None:
        """Get a CAD call by ID."""
        return self._calls.get(call_id)

    async def get_active_dispatch(
        self,
        badge_number: str | None = None,
        unit_id: str | None = None,
        district: str | None = None,
        priority: CADCallPriority | None = None,
    ) -> list[CADCall]:
        """
        Get active dispatch calls.

        Args:
            badge_number: Filter by assigned badge
            unit_id: Filter by assigned unit
            district: Filter by district
            priority: Filter by priority

        Returns:
            List of active calls
        """
        calls = []

        for call in self._calls.values():
            if call.status in [CADCallStatus.CLEARED, CADCallStatus.CANCELLED]:
                continue

            if priority and call.priority != priority:
                continue

            if unit_id and unit_id not in call.assigned_units:
                continue

            if badge_number:
                # Check if badge is assigned to this call
                unit = self._units.get(badge_number)
                if unit and unit.unit_id not in call.assigned_units:
                    continue

            calls.append(call)

        return sorted(calls, key=lambda c: (c.priority.value, c.created_at))

    async def assign_unit_to_call(
        self,
        call_id: str,
        unit_id: str,
        is_primary: bool = False,
    ) -> CADCall | None:
        """
        Assign a unit to a call.

        Args:
            call_id: Call ID
            unit_id: Unit ID to assign
            is_primary: Whether this is the primary unit

        Returns:
            Updated call or None
        """
        call = self._calls.get(call_id)
        if not call:
            return None

        if unit_id not in call.assigned_units:
            call.assigned_units.append(unit_id)

        if is_primary:
            call.primary_unit = unit_id

        if call.status == CADCallStatus.PENDING:
            call.status = CADCallStatus.DISPATCHED
            call.dispatched_at = datetime.utcnow()

        return call

    async def remove_unit_from_call(
        self,
        call_id: str,
        unit_id: str,
    ) -> CADCall | None:
        """Remove a unit from a call."""
        call = self._calls.get(call_id)
        if not call:
            return None

        if unit_id in call.assigned_units:
            call.assigned_units.remove(unit_id)

        if call.primary_unit == unit_id:
            call.primary_unit = call.assigned_units[0] if call.assigned_units else None

        return call

    async def clear_call(
        self,
        call_id: str,
        disposition: str,
        cleared_by: str | None = None,
    ) -> CADCall | None:
        """
        Clear a CAD call.

        Args:
            call_id: Call ID
            disposition: Disposition code
            cleared_by: Who cleared the call

        Returns:
            Updated call or None
        """
        call = self._calls.get(call_id)
        if not call:
            return None

        call.status = CADCallStatus.CLEARED
        call.disposition = disposition
        call.cleared_at = datetime.utcnow()

        # Clear units from call
        for unit_id in call.assigned_units:
            for unit in self._units.values():
                if unit.unit_id == unit_id and unit.current_call_id == call_id:
                    unit.current_call_id = None
                    unit.status = MDTUnitStatus.AVAILABLE

        return call

    async def add_call_note(
        self,
        call_id: str,
        author_badge: str,
        author_name: str,
        content: str,
        note_type: str = "general",
        is_rtcc: bool = False,
    ) -> CADNote | None:
        """
        Add a note to a CAD call.

        Args:
            call_id: Call ID
            author_badge: Author badge number
            author_name: Author name
            content: Note content
            note_type: Type of note
            is_rtcc: Is from RTCC

        Returns:
            Created note or None
        """
        call = self._calls.get(call_id)
        if not call:
            return None

        note = CADNote(
            call_id=call_id,
            author_badge=author_badge,
            author_name=author_name,
            content=content,
            note_type=note_type,
            is_rtcc=is_rtcc,
        )

        if call_id not in self._call_notes:
            self._call_notes[call_id] = []
        self._call_notes[call_id].append(note)

        # Also add to call notes list
        call.notes.append({
            "id": note.id,
            "author": author_name,
            "content": content,
            "type": note_type,
            "time": note.created_at.isoformat(),
        })

        return note

    async def get_call_notes(self, call_id: str) -> list[CADNote]:
        """Get notes for a call."""
        return self._call_notes.get(call_id, [])

    async def get_scene_coordination(self, call_id: str) -> SceneCoordination | None:
        """Get scene coordination for a call."""
        return self._scene_coordination.get(call_id)

    async def create_scene_coordination(
        self,
        call_id: str,
        incident_commander: str | None = None,
        staging_location: str | None = None,
        staging_lat: float | None = None,
        staging_lng: float | None = None,
    ) -> SceneCoordination | None:
        """
        Create scene coordination for a call.

        Args:
            call_id: Call ID
            incident_commander: IC badge number
            staging_location: Staging location
            staging_lat: Staging latitude
            staging_lng: Staging longitude

        Returns:
            Created coordination or None
        """
        call = self._calls.get(call_id)
        if not call:
            return None

        coordination = SceneCoordination(
            call_id=call_id,
            incident_commander=incident_commander,
            staging_location=staging_location,
            staging_lat=staging_lat,
            staging_lng=staging_lng,
        )

        self._scene_coordination[call_id] = coordination
        return coordination

    async def assign_scene_role(
        self,
        call_id: str,
        unit_id: str,
        badge_number: str,
        officer_name: str,
        role: SceneRole,
        assigned_by: str | None = None,
        notes: str | None = None,
    ) -> SceneAssignment | None:
        """
        Assign a scene role to a unit.

        Args:
            call_id: Call ID
            unit_id: Unit ID
            badge_number: Officer badge number
            officer_name: Officer name
            role: Scene role
            assigned_by: Who assigned
            notes: Assignment notes

        Returns:
            Created assignment or None
        """
        coordination = self._scene_coordination.get(call_id)
        if not coordination:
            coordination = await self.create_scene_coordination(call_id)

        if not coordination:
            return None

        assignment = SceneAssignment(
            call_id=call_id,
            unit_id=unit_id,
            badge_number=badge_number,
            officer_name=officer_name,
            role=role,
            assigned_by=assigned_by,
            notes=notes,
        )

        # Remove existing assignment for this unit
        coordination.assignments = [
            a for a in coordination.assignments if a.unit_id != unit_id
        ]
        coordination.assignments.append(assignment)
        coordination.updated_at = datetime.utcnow()

        return assignment

    async def update_scene_coordination(
        self,
        call_id: str,
        incident_commander: str | None = None,
        staging_location: str | None = None,
        staging_lat: float | None = None,
        staging_lng: float | None = None,
        perimeter_established: bool | None = None,
        perimeter_notes: str | None = None,
        resources_requested: list[str] | None = None,
        resources_on_scene: list[str] | None = None,
        tactical_notes: list[str] | None = None,
    ) -> SceneCoordination | None:
        """
        Update scene coordination.

        Args:
            call_id: Call ID
            incident_commander: IC badge number
            staging_location: Staging location
            staging_lat: Staging latitude
            staging_lng: Staging longitude
            perimeter_established: Whether perimeter is established
            perimeter_notes: Perimeter notes
            resources_requested: Requested resources
            resources_on_scene: Resources on scene
            tactical_notes: Tactical notes

        Returns:
            Updated coordination or None
        """
        coordination = self._scene_coordination.get(call_id)
        if not coordination:
            return None

        if incident_commander is not None:
            coordination.incident_commander = incident_commander
        if staging_location is not None:
            coordination.staging_location = staging_location
        if staging_lat is not None:
            coordination.staging_lat = staging_lat
        if staging_lng is not None:
            coordination.staging_lng = staging_lng
        if perimeter_established is not None:
            coordination.perimeter_established = perimeter_established
        if perimeter_notes is not None:
            coordination.perimeter_notes = perimeter_notes
        if resources_requested is not None:
            coordination.resources_requested = resources_requested
        if resources_on_scene is not None:
            coordination.resources_on_scene = resources_on_scene
        if tactical_notes is not None:
            coordination.tactical_notes = tactical_notes

        coordination.updated_at = datetime.utcnow()
        return coordination

    async def send_mdt_message(
        self,
        sender_badge: str,
        sender_name: str,
        content: str,
        recipient_badges: list[str] | None = None,
        recipient_units: list[str] | None = None,
        call_id: str | None = None,
        priority: str = "normal",
        is_broadcast: bool = False,
        sender_type: str = "officer",
    ) -> MDTMessage:
        """
        Send an MDT message.

        Args:
            sender_badge: Sender badge number
            sender_name: Sender name
            content: Message content
            recipient_badges: Recipient badge numbers
            recipient_units: Recipient unit IDs
            call_id: Associated call ID
            priority: Message priority
            is_broadcast: Is broadcast message
            sender_type: Type of sender

        Returns:
            Created message
        """
        message = MDTMessage(
            sender_badge=sender_badge,
            sender_name=sender_name,
            sender_type=sender_type,
            content=content,
            recipient_badges=recipient_badges or [],
            recipient_units=recipient_units or [],
            call_id=call_id,
            priority=priority,
            is_broadcast=is_broadcast,
        )

        self._messages[message.id] = message
        return message

    async def get_mdt_messages(
        self,
        badge_number: str,
        unit_id: str | None = None,
        call_id: str | None = None,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[MDTMessage]:
        """
        Get MDT messages for a unit.

        Args:
            badge_number: Officer badge number
            unit_id: Unit ID
            call_id: Filter by call ID
            limit: Maximum messages
            since: Only messages after this time

        Returns:
            List of messages
        """
        messages = []

        for msg in sorted(self._messages.values(), key=lambda m: m.created_at, reverse=True):
            if since and msg.created_at < since:
                continue

            if call_id and msg.call_id != call_id:
                continue

            # Check if officer should see message
            if (
                msg.is_broadcast
                or badge_number in msg.recipient_badges
                or msg.sender_badge == badge_number
                or (unit_id and unit_id in msg.recipient_units)
            ):
                messages.append(msg)

            if len(messages) >= limit:
                break

        return messages

    async def mark_message_read(self, message_id: str, badge_number: str) -> bool:
        """Mark a message as read."""
        message = self._messages.get(message_id)
        if message and badge_number not in message.read_by:
            message.read_by.append(badge_number)
            return True
        return False

    async def get_premise_history(
        self,
        address: str,
        limit: int = 10,
    ) -> list[str]:
        """
        Get premise history for an address.

        Args:
            address: Address to check
            limit: Maximum records

        Returns:
            List of premise history notes
        """
        history = []
        for call in self._calls.values():
            if call.address and address.lower() in call.address.lower():
                history.append(
                    f"{call.created_at.strftime('%Y-%m-%d')}: {call.call_type} - {call.disposition or 'No disposition'}"
                )
            if len(history) >= limit:
                break
        return history

    async def get_available_units(
        self,
        district: str | None = None,
        exclude_units: list[str] | None = None,
    ) -> list[MDTUnit]:
        """
        Get available units for dispatch.

        Args:
            district: Filter by district
            exclude_units: Units to exclude

        Returns:
            List of available units
        """
        exclude = exclude_units or []
        units = []

        for unit in self._units.values():
            if unit.status != MDTUnitStatus.AVAILABLE:
                continue
            if unit.unit_id in exclude:
                continue
            if district and unit.district != district:
                continue
            units.append(unit)

        return units


# Global instance
mdt_manager = MDTManager()
