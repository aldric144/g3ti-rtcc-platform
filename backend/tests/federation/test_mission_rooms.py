"""
Tests for Interagency Mission Rooms
Phase 10: Mission rooms, messaging, and incident handoff tests
"""


from app.federation.mission_rooms import (
    HandoffStatus,
    MessageType,
    MissionRoom,
    MissionRoomManager,
    MissionRoomStatus,
    MissionType,
    ParticipantRole,
)


class TestMissionRoom:
    """Tests for MissionRoom"""

    def test_create_mission_room(self):
        """Test creating mission room"""
        room = MissionRoom(
            name="Operation Crossroads",
            mission_type=MissionType.JOINT_OPERATION,
            description="Multi-agency joint operation",
            lead_agency="local_pd",
            created_by="commander_1",
            participating_agencies=["local_pd", "sheriff", "dea"],
        )

        assert room.name == "Operation Crossroads"
        assert room.mission_type == MissionType.JOINT_OPERATION
        assert room.status == MissionRoomStatus.PLANNING
        assert len(room.participating_agencies) == 3

    def test_mission_room_has_id(self):
        """Test mission room has unique ID"""
        room1 = MissionRoom(
            name="Mission 1",
            mission_type=MissionType.TASK_FORCE,
            description="Description 1",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )
        room2 = MissionRoom(
            name="Mission 2",
            mission_type=MissionType.TASK_FORCE,
            description="Description 2",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        assert room1.id != room2.id


class TestMissionRoomManager:
    """Tests for MissionRoomManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = MissionRoomManager()

    def test_create_mission(self):
        """Test creating mission"""
        mission = self.manager.create_mission(
            name="Test Operation",
            mission_type=MissionType.JOINT_OPERATION,
            description="Test description",
            lead_agency="local_pd",
            created_by="commander_1",
            participating_agencies=["local_pd", "sheriff"],
        )

        assert mission is not None
        assert mission.id in self.manager.missions
        assert mission.name == "Test Operation"

    def test_get_mission(self):
        """Test getting mission by ID"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.TASK_FORCE,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        retrieved = self.manager.get_mission(mission.id)
        assert retrieved is not None
        assert retrieved.id == mission.id

    def test_list_missions(self):
        """Test listing missions"""
        self.manager.create_mission(
            name="Mission 1",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description 1",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1", "agency-2"],
        )
        self.manager.create_mission(
            name="Mission 2",
            mission_type=MissionType.SPECIAL_EVENT,
            description="Description 2",
            lead_agency="agency-2",
            created_by="user-2",
            participating_agencies=["agency-2", "agency-3"],
        )

        all_missions = self.manager.list_missions()
        assert len(all_missions) == 2

        agency_1_missions = self.manager.list_missions(agency_id="agency-1")
        assert len(agency_1_missions) == 1

    def test_add_participant(self):
        """Test adding participant to mission"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        participant = self.manager.add_participant(
            mission_id=mission.id,
            agency_id="agency-2",
            user_id="user-2",
            user_name="Officer Smith",
            role=ParticipantRole.LIAISON,
        )

        assert participant is not None
        assert len(mission.participants) == 1

    def test_send_message(self):
        """Test sending message in mission room"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        message = self.manager.send_message(
            mission_id=mission.id,
            sender_agency="agency-1",
            sender_user="user-1",
            sender_name="Commander Smith",
            message_type=MessageType.CHAT,
            content="Test message content",
        )

        assert message is not None
        assert len(mission.messages) == 1
        assert message.content == "Test message content"

    def test_get_messages(self):
        """Test getting messages from mission room"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        self.manager.send_message(
            mission_id=mission.id,
            sender_agency="agency-1",
            sender_user="user-1",
            sender_name="User 1",
            message_type=MessageType.CHAT,
            content="Message 1",
        )
        self.manager.send_message(
            mission_id=mission.id,
            sender_agency="agency-2",
            sender_user="user-2",
            sender_name="User 2",
            message_type=MessageType.CHAT,
            content="Message 2",
        )

        messages = self.manager.get_messages(mission.id)
        assert len(messages) == 2

    def test_add_note(self):
        """Test adding note to mission"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        note = self.manager.add_note(
            mission_id=mission.id,
            author_agency="agency-1",
            author_user="user-1",
            author_name="Commander Smith",
            title="Important Note",
            content="Note content here",
            note_type="tactical",
            is_pinned=True,
        )

        assert note is not None
        assert len(mission.notes) == 1
        assert note.is_pinned is True

    def test_upload_file(self):
        """Test uploading file to mission"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        file = self.manager.upload_file(
            mission_id=mission.id,
            uploader_agency="agency-1",
            uploader_user="user-1",
            uploader_name="User 1",
            file_name="operation_plan.pdf",
            file_type="application/pdf",
            file_size=1024000,
            file_path="/files/operation_plan.pdf",
        )

        assert file is not None
        assert len(mission.files) == 1

    def test_add_map_overlay(self):
        """Test adding map overlay to mission"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        overlay = self.manager.add_map_overlay(
            mission_id=mission.id,
            name="Perimeter",
            overlay_type="polygon",
            geometry={"type": "Polygon", "coordinates": [[[-122.4, 37.8], [-122.4, 37.7], [-122.3, 37.7], [-122.3, 37.8], [-122.4, 37.8]]]},
            created_by_agency="agency-1",
            created_by_user="user-1",
        )

        assert overlay is not None
        assert len(mission.map_overlays) == 1

    def test_assign_ics_role(self):
        """Test assigning ICS role"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.EMERGENCY_RESPONSE,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        assignment = self.manager.assign_ics_role(
            mission_id=mission.id,
            role="incident_commander",
            agency_id="agency-1",
            user_id="user-1",
            user_name="Chief Johnson",
            assigned_by="user-1",
        )

        assert assignment is not None
        assert len(mission.ics_assignments) == 1
        assert assignment.role == "incident_commander"

    def test_initiate_handoff(self):
        """Test initiating incident handoff"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1", "agency-2"],
        )

        handoff = self.manager.initiate_handoff(
            mission_id=mission.id,
            incident_id="incident-123",
            from_agency="agency-1",
            to_agency="agency-2",
            initiated_by="user-1",
            reason="Jurisdiction change",
            handoff_notes="All resources transferred",
        )

        assert handoff is not None
        assert handoff.status == HandoffStatus.PENDING
        assert len(mission.handoffs) == 1

    def test_accept_handoff(self):
        """Test accepting incident handoff"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1", "agency-2"],
        )

        handoff = self.manager.initiate_handoff(
            mission_id=mission.id,
            incident_id="incident-123",
            from_agency="agency-1",
            to_agency="agency-2",
            initiated_by="user-1",
            reason="Jurisdiction change",
        )

        accepted = self.manager.accept_handoff(
            handoff_id=handoff.id,
            accepted_by="user-2",
        )

        assert accepted is not None
        assert accepted.status == HandoffStatus.ACCEPTED

    def test_reject_handoff(self):
        """Test rejecting incident handoff"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1", "agency-2"],
        )

        handoff = self.manager.initiate_handoff(
            mission_id=mission.id,
            incident_id="incident-123",
            from_agency="agency-1",
            to_agency="agency-2",
            initiated_by="user-1",
            reason="Jurisdiction change",
        )

        rejected = self.manager.reject_handoff(
            handoff_id=handoff.id,
            rejected_by="user-2",
            rejection_reason="Insufficient resources",
        )

        assert rejected is not None
        assert rejected.status == HandoffStatus.REJECTED

    def test_update_mission_status(self):
        """Test updating mission status"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        updated = self.manager.update_mission_status(
            mission_id=mission.id,
            status=MissionRoomStatus.ACTIVE,
        )

        assert updated is not None
        assert updated.status == MissionRoomStatus.ACTIVE

    def test_close_mission(self):
        """Test closing mission"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        closed = self.manager.close_mission(
            mission_id=mission.id,
            closed_by="user-1",
            close_reason="Operation completed successfully",
        )

        assert closed is not None
        assert closed.status == MissionRoomStatus.CLOSED

    def test_invite_agency(self):
        """Test inviting agency to mission"""
        mission = self.manager.create_mission(
            name="Test Mission",
            mission_type=MissionType.JOINT_OPERATION,
            description="Description",
            lead_agency="agency-1",
            created_by="user-1",
            participating_agencies=["agency-1"],
        )

        result = self.manager.invite_agency(
            mission_id=mission.id,
            agency_id="agency-2",
            invited_by="user-1",
        )

        assert result is True
        assert "agency-2" in mission.participating_agencies
