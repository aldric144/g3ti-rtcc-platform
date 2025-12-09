"""
G3TI RTCC-UIP IntelliSend Tests
Tests for the Mobile Intelligence Packet Delivery module
"""


import pytest

from app.mobile.intellisend import (
    DeliveryStatus,
    IntelliSendManager,
    IntelPacketType,
    IntelPriority,
)


class TestIntelliSendManager:
    """Tests for IntelliSendManager"""

    @pytest.fixture
    def manager(self):
        """Create a fresh manager instance for each test"""
        return IntelliSendManager()

    def test_create_vehicle_intel(self, manager):
        """Test creating vehicle intel packet"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Stolen Vehicle Alert",
            summary="Black Honda Accord reported stolen",
            plate="ABC-1234",
            make="Honda",
            model="Accord",
            color="Black",
            year=2020,
            priority=IntelPriority.HIGH,
            is_critical=True,
        )

        assert packet is not None
        assert packet.packet_type == IntelPacketType.VEHICLE
        assert packet.title == "Stolen Vehicle Alert"
        assert packet.priority == IntelPriority.HIGH
        assert packet.is_critical is True
        assert packet.details["plate"] == "ABC-1234"

    def test_create_person_intel(self, manager):
        """Test creating person intel packet"""
        packet = manager.create_person_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Wanted Person",
            summary="John Doe wanted for robbery",
            name="John Doe",
            description="White male, 6ft, brown hair",
            priority=IntelPriority.HIGH,
        )

        assert packet is not None
        assert packet.packet_type == IntelPacketType.PERSON
        assert packet.details["name"] == "John Doe"

    def test_create_location_intel(self, manager):
        """Test creating location intel packet"""
        packet = manager.create_location_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Location Alert",
            summary="Known drug house",
            address="123 Main St",
            latitude=34.0522,
            longitude=-118.2437,
            priority=IntelPriority.MEDIUM,
        )

        assert packet is not None
        assert packet.packet_type == IntelPacketType.LOCATION
        assert packet.location == "123 Main St"

    def test_create_officer_safety_packet(self, manager):
        """Test creating officer safety intel packet"""
        packet = manager.create_officer_safety_packet(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Officer Safety Alert",
            summary="Armed suspect in area",
            threat_description="Suspect armed with handgun",
            threat_level="high",
            priority=IntelPriority.CRITICAL,
            is_critical=True,
        )

        assert packet is not None
        assert packet.packet_type == IntelPacketType.OFFICER_SAFETY
        assert packet.priority == IntelPriority.CRITICAL
        assert packet.is_critical is True

    def test_create_bulletin_packet(self, manager):
        """Test creating bulletin intel packet"""
        packet = manager.create_bulletin_packet(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Daily Bulletin",
            summary="Morning briefing information",
            bulletin_type="daily",
            content="Full bulletin content here",
            priority=IntelPriority.MEDIUM,
        )

        assert packet is not None
        assert packet.packet_type == IntelPacketType.BULLETIN

    def test_create_command_note_packet(self, manager):
        """Test creating command note intel packet"""
        packet = manager.create_command_note_packet(
            sender_badge="CMD001",
            sender_name="Commander Smith",
            title="Command Directive",
            summary="New patrol assignments",
            note_content="All units report to staging area",
            priority=IntelPriority.HIGH,
        )

        assert packet is not None
        assert packet.packet_type == IntelPacketType.COMMAND_NOTE

    def test_send_packet_to_single_recipient(self, manager):
        """Test sending packet to single recipient"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Test Alert",
            summary="Test summary",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )

        deliveries = manager.send_packet(packet.id, ["1234"])

        assert len(deliveries) == 1
        assert deliveries[0].recipient_badge == "1234"
        assert deliveries[0].status == DeliveryStatus.PENDING

    def test_send_packet_to_multiple_recipients(self, manager):
        """Test sending packet to multiple recipients"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Test Alert",
            summary="Test summary",
            plate="ABC-1234",
            priority=IntelPriority.HIGH,
        )

        deliveries = manager.send_packet(packet.id, ["1234", "5678", "9012"])

        assert len(deliveries) == 3

    def test_get_packet(self, manager):
        """Test getting a packet by ID"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Test Alert",
            summary="Test summary",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )

        retrieved = manager.get_packet(packet.id)

        assert retrieved is not None
        assert retrieved.id == packet.id

    def test_get_packets_for_badge(self, manager):
        """Test getting packets for a badge"""
        # Create and send packets
        packet1 = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Alert 1",
            summary="Summary 1",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )
        packet2 = manager.create_person_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Alert 2",
            summary="Summary 2",
            name="John Doe",
            priority=IntelPriority.HIGH,
        )

        manager.send_packet(packet1.id, ["1234"])
        manager.send_packet(packet2.id, ["1234"])

        # Get packets for badge
        packets = manager.get_packets_for_badge("1234")

        assert len(packets) == 2

    def test_mark_delivered(self, manager):
        """Test marking packet as delivered"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Test Alert",
            summary="Test summary",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )
        deliveries = manager.send_packet(packet.id, ["1234"])

        result = manager.mark_delivered(deliveries[0].id)

        assert result is True
        assert deliveries[0].status == DeliveryStatus.DELIVERED

    def test_mark_read(self, manager):
        """Test marking packet as read"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Test Alert",
            summary="Test summary",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )
        deliveries = manager.send_packet(packet.id, ["1234"])

        result = manager.mark_read(deliveries[0].id)

        assert result is True
        assert deliveries[0].status == DeliveryStatus.READ

    def test_acknowledge_packet(self, manager):
        """Test acknowledging packet"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Test Alert",
            summary="Test summary",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )
        deliveries = manager.send_packet(packet.id, ["1234"])

        result = manager.acknowledge_packet(deliveries[0].id)

        assert result is True
        assert deliveries[0].status == DeliveryStatus.ACKNOWLEDGED

    def test_get_delivery_status(self, manager):
        """Test getting delivery status"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Test Alert",
            summary="Test summary",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )
        _deliveries = manager.send_packet(packet.id, ["1234", "5678"])

        status = manager.get_delivery_status(packet.id)

        assert len(status) == 2

    def test_get_unread_count(self, manager):
        """Test getting unread count"""
        # Create and send packets
        packet1 = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Alert 1",
            summary="Summary 1",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )
        packet2 = manager.create_person_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Alert 2",
            summary="Summary 2",
            name="John Doe",
            priority=IntelPriority.HIGH,
        )

        deliveries1 = manager.send_packet(packet1.id, ["1234"])
        _deliveries2 = manager.send_packet(packet2.id, ["1234"])

        # Mark one as read
        manager.mark_read(deliveries1[0].id)

        # Get unread count
        count = manager.get_unread_count("1234")

        assert count == 1

    def test_add_nearby_cameras(self, manager):
        """Test adding nearby cameras to packet"""
        packet = manager.create_location_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Location Alert",
            summary="Test location",
            address="123 Main St",
            latitude=34.0522,
            longitude=-118.2437,
            priority=IntelPriority.MEDIUM,
        )

        cameras = [
            {"camera_id": "CAM001", "name": "Main St Camera", "distance": 50},
            {"camera_id": "CAM002", "name": "Corner Camera", "distance": 100},
        ]

        result = manager.add_nearby_cameras(packet.id, cameras)

        assert result is True
        assert len(packet.nearby_cameras) == 2

    def test_add_related_calls(self, manager):
        """Test adding related CAD calls to packet"""
        packet = manager.create_vehicle_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Test Alert",
            summary="Test summary",
            plate="ABC-1234",
            priority=IntelPriority.MEDIUM,
        )

        calls = [
            {"call_id": "CAD001", "call_type": "Traffic Stop", "status": "Active"},
        ]

        result = manager.add_related_calls(packet.id, calls)

        assert result is True
        assert len(packet.related_calls) == 1

    def test_add_safety_note(self, manager):
        """Test adding safety note to packet"""
        packet = manager.create_person_intel(
            sender_badge="RTCC001",
            sender_name="RTCC Analyst",
            title="Wanted Person",
            summary="Test summary",
            name="John Doe",
            priority=IntelPriority.HIGH,
        )

        result = manager.add_safety_note(
            packet_id=packet.id,
            note_type="warning",
            content="Subject known to carry weapons",
            severity="high",
        )

        assert result is True
        assert len(packet.safety_notes) == 1
        assert packet.safety_notes[0].content == "Subject known to carry weapons"
