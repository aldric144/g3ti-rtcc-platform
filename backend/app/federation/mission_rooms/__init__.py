"""
G3TI RTCC-UIP Interagency Mission Rooms
Phase 10: Shared command rooms between agencies for joint operations
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class MissionRoomStatus(str, Enum):
    """Mission room status"""
    PLANNING = "planning"
    ACTIVE = "active"
    STANDBY = "standby"
    CLOSED = "closed"
    ARCHIVED = "archived"


class MissionType(str, Enum):
    """Types of joint missions"""
    JOINT_OPERATION = "joint_operation"
    MUTUAL_AID = "mutual_aid"
    TASK_FORCE = "task_force"
    SPECIAL_EVENT = "special_event"
    EMERGENCY_RESPONSE = "emergency_response"
    INVESTIGATION = "investigation"
    SURVEILLANCE = "surveillance"
    TRAINING = "training"


class ParticipantRole(str, Enum):
    """Roles for mission room participants"""
    COMMANDER = "commander"
    OPERATIONS_CHIEF = "operations_chief"
    PLANNING_CHIEF = "planning_chief"
    LOGISTICS_CHIEF = "logistics_chief"
    LIAISON = "liaison"
    OBSERVER = "observer"
    PARTICIPANT = "participant"
    ANALYST = "analyst"
    COMMUNICATIONS = "communications"


class MessageType(str, Enum):
    """Types of mission room messages"""
    CHAT = "chat"
    ANNOUNCEMENT = "announcement"
    ALERT = "alert"
    STATUS_UPDATE = "status_update"
    RESOURCE_REQUEST = "resource_request"
    INTEL_SHARE = "intel_share"
    FILE_SHARE = "file_share"
    SYSTEM = "system"


class HandoffStatus(str, Enum):
    """Incident handoff status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MissionRoom:
    """Shared mission room between agencies"""

    def __init__(
        self,
        name: str,
        mission_type: MissionType,
        description: str,
        lead_agency: str,
        created_by: str,
        participating_agencies: list[str],
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        location: dict[str, Any] | None = None,
        related_incident_id: str | None = None,
    ):
        self.id = str(uuid4())
        self.name = name
        self.mission_type = mission_type
        self.description = description
        self.lead_agency = lead_agency
        self.created_by = created_by
        self.participating_agencies = participating_agencies
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.related_incident_id = related_incident_id
        self.status = MissionRoomStatus.PLANNING
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.participants: list[MissionParticipant] = []
        self.messages: list[MissionMessage] = []
        self.files: list[MissionFile] = []
        self.notes: list[MissionNote] = []
        self.map_overlays: list[MapOverlay] = []
        self.ics_assignments: list[ICSAssignment] = []
        self.handoffs: list[IncidentHandoff] = []


class MissionParticipant:
    """Participant in a mission room"""

    def __init__(
        self,
        mission_id: str,
        agency_id: str,
        user_id: str,
        user_name: str,
        role: ParticipantRole,
        badge_number: str | None = None,
        contact_info: str | None = None,
    ):
        self.id = str(uuid4())
        self.mission_id = mission_id
        self.agency_id = agency_id
        self.user_id = user_id
        self.user_name = user_name
        self.role = role
        self.badge_number = badge_number
        self.contact_info = contact_info
        self.joined_at = datetime.utcnow()
        self.left_at: datetime | None = None
        self.is_active = True
        self.last_seen_at = datetime.utcnow()


class MissionMessage:
    """Message in a mission room"""

    def __init__(
        self,
        mission_id: str,
        sender_agency: str,
        sender_user: str,
        sender_name: str,
        message_type: MessageType,
        content: str,
        priority: str = "normal",
        attachments: list[str] | None = None,
        mentions: list[str] | None = None,
    ):
        self.id = str(uuid4())
        self.mission_id = mission_id
        self.sender_agency = sender_agency
        self.sender_user = sender_user
        self.sender_name = sender_name
        self.message_type = message_type
        self.content = content
        self.priority = priority
        self.attachments = attachments or []
        self.mentions = mentions or []
        self.created_at = datetime.utcnow()
        self.edited_at: datetime | None = None
        self.is_deleted = False
        self.read_by: list[dict[str, Any]] = []


class MissionFile:
    """File shared in a mission room"""

    def __init__(
        self,
        mission_id: str,
        uploader_agency: str,
        uploader_user: str,
        file_name: str,
        file_type: str,
        file_size: int,
        file_path: str,
        description: str | None = None,
        classification: str = "unclassified",
    ):
        self.id = str(uuid4())
        self.mission_id = mission_id
        self.uploader_agency = uploader_agency
        self.uploader_user = uploader_user
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.file_path = file_path
        self.description = description
        self.classification = classification
        self.uploaded_at = datetime.utcnow()
        self.download_count = 0
        self.accessed_by: list[dict[str, Any]] = []


class MissionNote:
    """Note in a mission room"""

    def __init__(
        self,
        mission_id: str,
        author_agency: str,
        author_user: str,
        author_name: str,
        title: str,
        content: str,
        note_type: str = "general",
        is_pinned: bool = False,
    ):
        self.id = str(uuid4())
        self.mission_id = mission_id
        self.author_agency = author_agency
        self.author_user = author_user
        self.author_name = author_name
        self.title = title
        self.content = content
        self.note_type = note_type
        self.is_pinned = is_pinned
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class MapOverlay:
    """Map overlay for mission room strategy map"""

    def __init__(
        self,
        mission_id: str,
        creator_agency: str,
        creator_user: str,
        overlay_type: str,
        name: str,
        geometry: dict[str, Any],
        properties: dict[str, Any] | None = None,
        color: str = "#FF0000",
        is_visible: bool = True,
    ):
        self.id = str(uuid4())
        self.mission_id = mission_id
        self.creator_agency = creator_agency
        self.creator_user = creator_user
        self.overlay_type = overlay_type
        self.name = name
        self.geometry = geometry
        self.properties = properties or {}
        self.color = color
        self.is_visible = is_visible
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class ICSAssignment:
    """ICS role assignment for interagency operations"""

    def __init__(
        self,
        mission_id: str,
        ics_role: str,
        assigned_agency: str,
        assigned_user: str,
        assigned_name: str,
        assigned_by: str,
        responsibilities: list[str] | None = None,
    ):
        self.id = str(uuid4())
        self.mission_id = mission_id
        self.ics_role = ics_role
        self.assigned_agency = assigned_agency
        self.assigned_user = assigned_user
        self.assigned_name = assigned_name
        self.assigned_by = assigned_by
        self.responsibilities = responsibilities or []
        self.assigned_at = datetime.utcnow()
        self.relieved_at: datetime | None = None
        self.is_active = True


class IncidentHandoff:
    """Incident handoff between agencies"""

    def __init__(
        self,
        mission_id: str,
        incident_id: str,
        from_agency: str,
        to_agency: str,
        initiated_by: str,
        reason: str,
        handoff_notes: str | None = None,
        resources_transferred: list[str] | None = None,
    ):
        self.id = str(uuid4())
        self.mission_id = mission_id
        self.incident_id = incident_id
        self.from_agency = from_agency
        self.to_agency = to_agency
        self.initiated_by = initiated_by
        self.reason = reason
        self.handoff_notes = handoff_notes
        self.resources_transferred = resources_transferred or []
        self.status = HandoffStatus.PENDING
        self.initiated_at = datetime.utcnow()
        self.responded_at: datetime | None = None
        self.responded_by: str | None = None
        self.completed_at: datetime | None = None


class MissionRoomManager:
    """Manager for interagency mission rooms"""

    def __init__(self):
        self.rooms: dict[str, MissionRoom] = {}
        self.active_participants: dict[str, list[str]] = {}  # room_id -> user_ids

    def create_mission(
        self,
        name: str,
        mission_type: MissionType,
        description: str,
        lead_agency: str,
        created_by: str,
        participating_agencies: list[str],
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        location: dict[str, Any] | None = None,
        related_incident_id: str | None = None,
    ) -> MissionRoom:
        """Create a new mission room"""
        room = MissionRoom(
            name=name,
            mission_type=mission_type,
            description=description,
            lead_agency=lead_agency,
            created_by=created_by,
            participating_agencies=participating_agencies,
            start_time=start_time,
            end_time=end_time,
            location=location,
            related_incident_id=related_incident_id,
        )
        self.rooms[room.id] = room
        self.active_participants[room.id] = []

        # Add system message
        self._add_system_message(
            room.id,
            f"Mission room '{name}' created by {lead_agency}",
        )

        return room

    def get_mission(self, mission_id: str) -> MissionRoom | None:
        """Get a mission room by ID"""
        return self.rooms.get(mission_id)

    def list_missions(
        self,
        agency_id: str | None = None,
        status: MissionRoomStatus | None = None,
        mission_type: MissionType | None = None,
    ) -> list[MissionRoom]:
        """List mission rooms with optional filtering"""
        rooms = list(self.rooms.values())

        if agency_id:
            rooms = [
                r for r in rooms
                if agency_id in r.participating_agencies or r.lead_agency == agency_id
            ]
        if status:
            rooms = [r for r in rooms if r.status == status]
        if mission_type:
            rooms = [r for r in rooms if r.mission_type == mission_type]

        return rooms

    def update_mission_status(
        self,
        mission_id: str,
        status: MissionRoomStatus,
        updated_by: str,
    ) -> MissionRoom | None:
        """Update mission room status"""
        room = self.rooms.get(mission_id)
        if room:
            old_status = room.status
            room.status = status
            room.updated_at = datetime.utcnow()

            self._add_system_message(
                mission_id,
                f"Mission status changed from {old_status.value} to {status.value} by {updated_by}",
            )

            return room
        return None

    def invite_agency(
        self,
        mission_id: str,
        agency_id: str,
        invited_by: str,
    ) -> bool:
        """Invite an agency to join the mission"""
        room = self.rooms.get(mission_id)
        if room and agency_id not in room.participating_agencies:
            room.participating_agencies.append(agency_id)
            room.updated_at = datetime.utcnow()

            self._add_system_message(
                mission_id,
                f"Agency {agency_id} invited to mission by {invited_by}",
            )

            return True
        return False

    def join_mission(
        self,
        mission_id: str,
        agency_id: str,
        user_id: str,
        user_name: str,
        role: ParticipantRole,
        badge_number: str | None = None,
        contact_info: str | None = None,
    ) -> MissionParticipant | None:
        """Join a mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return None

        if agency_id not in room.participating_agencies:
            return None

        participant = MissionParticipant(
            mission_id=mission_id,
            agency_id=agency_id,
            user_id=user_id,
            user_name=user_name,
            role=role,
            badge_number=badge_number,
            contact_info=contact_info,
        )
        room.participants.append(participant)

        if user_id not in self.active_participants[mission_id]:
            self.active_participants[mission_id].append(user_id)

        self._add_system_message(
            mission_id,
            f"{user_name} ({agency_id}) joined the mission as {role.value}",
        )

        return participant

    def leave_mission(
        self,
        mission_id: str,
        user_id: str,
    ) -> bool:
        """Leave a mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return False

        for participant in room.participants:
            if participant.user_id == user_id and participant.is_active:
                participant.is_active = False
                participant.left_at = datetime.utcnow()

                if user_id in self.active_participants.get(mission_id, []):
                    self.active_participants[mission_id].remove(user_id)

                self._add_system_message(
                    mission_id,
                    f"{participant.user_name} ({participant.agency_id}) left the mission",
                )

                return True
        return False

    def send_message(
        self,
        mission_id: str,
        sender_agency: str,
        sender_user: str,
        sender_name: str,
        message_type: MessageType,
        content: str,
        priority: str = "normal",
        attachments: list[str] | None = None,
        mentions: list[str] | None = None,
    ) -> MissionMessage | None:
        """Send a message to the mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return None

        message = MissionMessage(
            mission_id=mission_id,
            sender_agency=sender_agency,
            sender_user=sender_user,
            sender_name=sender_name,
            message_type=message_type,
            content=content,
            priority=priority,
            attachments=attachments,
            mentions=mentions,
        )
        room.messages.append(message)
        return message

    def _add_system_message(
        self,
        mission_id: str,
        content: str,
    ) -> None:
        """Add a system message to the mission room"""
        room = self.rooms.get(mission_id)
        if room:
            message = MissionMessage(
                mission_id=mission_id,
                sender_agency="system",
                sender_user="system",
                sender_name="System",
                message_type=MessageType.SYSTEM,
                content=content,
            )
            room.messages.append(message)

    def get_messages(
        self,
        mission_id: str,
        since: datetime | None = None,
        message_type: MessageType | None = None,
        limit: int = 100,
    ) -> list[MissionMessage]:
        """Get messages from a mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return []

        messages = [m for m in room.messages if not m.is_deleted]

        if since:
            messages = [m for m in messages if m.created_at >= since]
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        return messages[-limit:]

    def upload_file(
        self,
        mission_id: str,
        uploader_agency: str,
        uploader_user: str,
        file_name: str,
        file_type: str,
        file_size: int,
        file_path: str,
        description: str | None = None,
        classification: str = "unclassified",
    ) -> MissionFile | None:
        """Upload a file to the mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return None

        file = MissionFile(
            mission_id=mission_id,
            uploader_agency=uploader_agency,
            uploader_user=uploader_user,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            description=description,
            classification=classification,
        )
        room.files.append(file)

        self._add_system_message(
            mission_id,
            f"File '{file_name}' uploaded by {uploader_agency}",
        )

        return file

    def get_files(
        self,
        mission_id: str,
    ) -> list[MissionFile]:
        """Get files from a mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return []
        return room.files

    def add_note(
        self,
        mission_id: str,
        author_agency: str,
        author_user: str,
        author_name: str,
        title: str,
        content: str,
        note_type: str = "general",
        is_pinned: bool = False,
    ) -> MissionNote | None:
        """Add a note to the mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return None

        note = MissionNote(
            mission_id=mission_id,
            author_agency=author_agency,
            author_user=author_user,
            author_name=author_name,
            title=title,
            content=content,
            note_type=note_type,
            is_pinned=is_pinned,
        )
        room.notes.append(note)
        return note

    def get_notes(
        self,
        mission_id: str,
        pinned_only: bool = False,
    ) -> list[MissionNote]:
        """Get notes from a mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return []

        notes = room.notes
        if pinned_only:
            notes = [n for n in notes if n.is_pinned]
        return notes

    def add_map_overlay(
        self,
        mission_id: str,
        creator_agency: str,
        creator_user: str,
        overlay_type: str,
        name: str,
        geometry: dict[str, Any],
        properties: dict[str, Any] | None = None,
        color: str = "#FF0000",
    ) -> MapOverlay | None:
        """Add a map overlay to the mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return None

        overlay = MapOverlay(
            mission_id=mission_id,
            creator_agency=creator_agency,
            creator_user=creator_user,
            overlay_type=overlay_type,
            name=name,
            geometry=geometry,
            properties=properties,
            color=color,
        )
        room.map_overlays.append(overlay)
        return overlay

    def get_map_overlays(
        self,
        mission_id: str,
        visible_only: bool = True,
    ) -> list[MapOverlay]:
        """Get map overlays from a mission room"""
        room = self.rooms.get(mission_id)
        if not room:
            return []

        overlays = room.map_overlays
        if visible_only:
            overlays = [o for o in overlays if o.is_visible]
        return overlays

    def assign_ics_role(
        self,
        mission_id: str,
        ics_role: str,
        assigned_agency: str,
        assigned_user: str,
        assigned_name: str,
        assigned_by: str,
        responsibilities: list[str] | None = None,
    ) -> ICSAssignment | None:
        """Assign an ICS role in the mission"""
        room = self.rooms.get(mission_id)
        if not room:
            return None

        # Deactivate any existing assignment for this role
        for assignment in room.ics_assignments:
            if assignment.ics_role == ics_role and assignment.is_active:
                assignment.is_active = False
                assignment.relieved_at = datetime.utcnow()

        assignment = ICSAssignment(
            mission_id=mission_id,
            ics_role=ics_role,
            assigned_agency=assigned_agency,
            assigned_user=assigned_user,
            assigned_name=assigned_name,
            assigned_by=assigned_by,
            responsibilities=responsibilities,
        )
        room.ics_assignments.append(assignment)

        self._add_system_message(
            mission_id,
            f"ICS role '{ics_role}' assigned to {assigned_name} ({assigned_agency})",
        )

        return assignment

    def get_ics_assignments(
        self,
        mission_id: str,
        active_only: bool = True,
    ) -> list[ICSAssignment]:
        """Get ICS assignments for a mission"""
        room = self.rooms.get(mission_id)
        if not room:
            return []

        assignments = room.ics_assignments
        if active_only:
            assignments = [a for a in assignments if a.is_active]
        return assignments

    def initiate_handoff(
        self,
        mission_id: str,
        incident_id: str,
        from_agency: str,
        to_agency: str,
        initiated_by: str,
        reason: str,
        handoff_notes: str | None = None,
        resources_transferred: list[str] | None = None,
    ) -> IncidentHandoff | None:
        """Initiate an incident handoff between agencies"""
        room = self.rooms.get(mission_id)
        if not room:
            return None

        handoff = IncidentHandoff(
            mission_id=mission_id,
            incident_id=incident_id,
            from_agency=from_agency,
            to_agency=to_agency,
            initiated_by=initiated_by,
            reason=reason,
            handoff_notes=handoff_notes,
            resources_transferred=resources_transferred,
        )
        room.handoffs.append(handoff)

        self._add_system_message(
            mission_id,
            f"Incident handoff initiated from {from_agency} to {to_agency}",
        )

        return handoff

    def respond_to_handoff(
        self,
        handoff_id: str,
        response: HandoffStatus,
        responded_by: str,
    ) -> IncidentHandoff | None:
        """Respond to an incident handoff"""
        for room in self.rooms.values():
            for handoff in room.handoffs:
                if handoff.id == handoff_id:
                    handoff.status = response
                    handoff.responded_at = datetime.utcnow()
                    handoff.responded_by = responded_by

                    if response == HandoffStatus.ACCEPTED:
                        handoff.completed_at = datetime.utcnow()

                    self._add_system_message(
                        room.id,
                        f"Handoff {response.value} by {responded_by}",
                    )

                    return handoff
        return None

    def get_handoffs(
        self,
        mission_id: str,
        status: HandoffStatus | None = None,
    ) -> list[IncidentHandoff]:
        """Get handoffs for a mission"""
        room = self.rooms.get(mission_id)
        if not room:
            return []

        handoffs = room.handoffs
        if status:
            handoffs = [h for h in handoffs if h.status == status]
        return handoffs

    def get_active_participants(
        self,
        mission_id: str,
    ) -> list[MissionParticipant]:
        """Get active participants in a mission"""
        room = self.rooms.get(mission_id)
        if not room:
            return []
        return [p for p in room.participants if p.is_active]

    def update_participant_presence(
        self,
        mission_id: str,
        user_id: str,
    ) -> bool:
        """Update participant's last seen timestamp"""
        room = self.rooms.get(mission_id)
        if not room:
            return False

        for participant in room.participants:
            if participant.user_id == user_id and participant.is_active:
                participant.last_seen_at = datetime.utcnow()
                return True
        return False


# Create singleton instance
mission_room_manager = MissionRoomManager()
