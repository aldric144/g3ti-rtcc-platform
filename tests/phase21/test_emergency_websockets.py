"""
Phase 21: Emergency WebSocket Tests

Tests for all emergency management WebSocket channels.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.websockets.emergency import (
    EmergencyWebSocketManager,
    CrisisChannel,
    EvacuationChannel,
    ResourcesChannel,
    MedicalChannel,
    IncidentsChannel,
    DamageChannel,
    EmergencyChannelType,
    MessageType,
    WebSocketConnection,
    ChannelMessage,
)


class TestCrisisChannel:
    """Tests for CrisisChannel class."""

    def test_channel_initialization(self):
        """Test CrisisChannel initializes correctly."""
        channel = CrisisChannel()
        assert channel is not None
        assert hasattr(channel, '_connections')
        assert hasattr(channel, '_message_handlers')

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting to crisis channel."""
        channel = CrisisChannel()
        connection = await channel.connect(
            connection_id="conn-001",
            user_id="user-001",
            subscriptions={"all", "storms"},
        )
        
        assert connection is not None
        assert connection.connection_id == "conn-001"
        assert connection.channel == EmergencyChannelType.CRISIS

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting from crisis channel."""
        channel = CrisisChannel()
        await channel.connect(connection_id="conn-002")
        await channel.disconnect("conn-002")
        
        connections = channel.get_connections()
        assert not any(c.connection_id == "conn-002" for c in connections)

    @pytest.mark.asyncio
    async def test_broadcast_alert(self):
        """Test broadcasting crisis alert."""
        channel = CrisisChannel()
        await channel.connect(connection_id="conn-003")
        
        message = await channel.broadcast_alert(
            alert_type="storm",
            alert_data={"name": "Hurricane Alpha", "category": "4"},
            priority=10,
        )
        
        assert message is not None
        assert message.message_type == MessageType.ALERT
        assert message.priority == 10

    @pytest.mark.asyncio
    async def test_broadcast_update(self):
        """Test broadcasting crisis update."""
        channel = CrisisChannel()
        
        message = await channel.broadcast_update(
            update_type="storm_position",
            update_data={"lat": 25.0, "lng": -80.0},
        )
        
        assert message is not None
        assert message.message_type == MessageType.UPDATE

    def test_register_handler(self):
        """Test registering message handler."""
        channel = CrisisChannel()
        handler = MagicMock()
        
        channel.register_handler(handler)
        assert handler in channel._message_handlers

    def test_get_recent_messages(self):
        """Test getting recent messages."""
        channel = CrisisChannel()
        messages = channel.get_recent_messages(limit=10)
        assert isinstance(messages, list)


class TestEvacuationChannel:
    """Tests for EvacuationChannel class."""

    def test_channel_initialization(self):
        """Test EvacuationChannel initializes correctly."""
        channel = EvacuationChannel()
        assert channel is not None

    @pytest.mark.asyncio
    async def test_connect_with_zone_subscriptions(self):
        """Test connecting with zone subscriptions."""
        channel = EvacuationChannel()
        connection = await channel.connect(
            connection_id="conn-001",
            zone_subscriptions={"zone-a", "zone-b"},
        )
        
        assert connection is not None
        assert "zone-a" in connection.subscriptions

    @pytest.mark.asyncio
    async def test_broadcast_evacuation_order(self):
        """Test broadcasting evacuation order."""
        channel = EvacuationChannel()
        
        message = await channel.broadcast_evacuation_order(
            order_data={
                "zone": "zone-a",
                "priority": "mandatory",
                "affected_population": 25000,
            },
        )
        
        assert message is not None
        assert message.message_type == MessageType.COMMAND

    @pytest.mark.asyncio
    async def test_broadcast_route_update(self):
        """Test broadcasting route update."""
        channel = EvacuationChannel()
        
        message = await channel.broadcast_route_update(
            route_id="route-001",
            route_data={"status": "congested", "delay_minutes": 30},
        )
        
        assert message is not None
        assert message.payload["route_id"] == "route-001"

    @pytest.mark.asyncio
    async def test_broadcast_traffic_update(self):
        """Test broadcasting traffic update."""
        channel = EvacuationChannel()
        
        message = await channel.broadcast_traffic_update(
            traffic_data={"average_speed": 25, "congestion_level": "high"},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_population_movement(self):
        """Test broadcasting population movement."""
        channel = EvacuationChannel()
        
        message = await channel.broadcast_population_movement(
            movement_data={"evacuated": 5000, "remaining": 20000},
        )
        
        assert message is not None
        assert message.message_type == MessageType.STATUS


class TestResourcesChannel:
    """Tests for ResourcesChannel class."""

    def test_channel_initialization(self):
        """Test ResourcesChannel initializes correctly."""
        channel = ResourcesChannel()
        assert channel is not None

    @pytest.mark.asyncio
    async def test_broadcast_shelter_update(self):
        """Test broadcasting shelter update."""
        channel = ResourcesChannel()
        
        message = await channel.broadcast_shelter_update(
            shelter_id="shelter-001",
            shelter_data={"occupancy": 150, "capacity": 500},
        )
        
        assert message is not None
        assert message.payload["shelter_id"] == "shelter-001"

    @pytest.mark.asyncio
    async def test_broadcast_supply_alert(self):
        """Test broadcasting supply alert."""
        channel = ResourcesChannel()
        
        message = await channel.broadcast_supply_alert(
            supply_data={"item": "water", "quantity": 100, "minimum": 500},
        )
        
        assert message is not None
        assert message.message_type == MessageType.ALERT

    @pytest.mark.asyncio
    async def test_broadcast_deployment_update(self):
        """Test broadcasting deployment update."""
        channel = ResourcesChannel()
        
        message = await channel.broadcast_deployment_update(
            unit_id="unit-001",
            deployment_data={"status": "deployed", "location": "Shelter A"},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_infrastructure_outage(self):
        """Test broadcasting infrastructure outage."""
        channel = ResourcesChannel()
        
        message = await channel.broadcast_infrastructure_outage(
            asset_id="power-001",
            outage_data={"type": "power", "affected": 10000},
        )
        
        assert message is not None
        assert message.priority == 8


class TestMedicalChannel:
    """Tests for MedicalChannel class."""

    def test_channel_initialization(self):
        """Test MedicalChannel initializes correctly."""
        channel = MedicalChannel()
        assert channel is not None

    @pytest.mark.asyncio
    async def test_broadcast_hospital_status(self):
        """Test broadcasting hospital status."""
        channel = MedicalChannel()
        
        message = await channel.broadcast_hospital_status(
            hospital_id="hosp-001",
            status_data={"beds_available": 50, "icu_available": 5},
        )
        
        assert message is not None
        assert message.message_type == MessageType.STATUS

    @pytest.mark.asyncio
    async def test_broadcast_surge_alert(self):
        """Test broadcasting surge alert."""
        channel = MedicalChannel()
        
        message = await channel.broadcast_surge_alert(
            surge_data={"level": "critical", "hospitals_affected": 3},
        )
        
        assert message is not None
        assert message.priority == 9

    @pytest.mark.asyncio
    async def test_broadcast_triage_update(self):
        """Test broadcasting triage update."""
        channel = MedicalChannel()
        
        message = await channel.broadcast_triage_update(
            triage_data={"immediate": 10, "delayed": 25, "minor": 50},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_ems_update(self):
        """Test broadcasting EMS update."""
        channel = MedicalChannel()
        
        message = await channel.broadcast_ems_update(
            ems_data={"available_units": 5, "on_call": 10},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_supply_critical(self):
        """Test broadcasting critical supply alert."""
        channel = MedicalChannel()
        
        message = await channel.broadcast_supply_critical(
            supply_data={"item": "blood_o_neg", "quantity": 10},
        )
        
        assert message is not None
        assert message.priority == 7


class TestIncidentsChannel:
    """Tests for IncidentsChannel class."""

    def test_channel_initialization(self):
        """Test IncidentsChannel initializes correctly."""
        channel = IncidentsChannel()
        assert channel is not None

    @pytest.mark.asyncio
    async def test_connect_with_room_subscriptions(self):
        """Test connecting with room subscriptions."""
        channel = IncidentsChannel()
        connection = await channel.connect(
            connection_id="conn-001",
            room_subscriptions={"room-001", "room-002"},
        )
        
        assert connection is not None
        assert "room-001" in connection.subscriptions

    @pytest.mark.asyncio
    async def test_broadcast_incident_created(self):
        """Test broadcasting incident creation."""
        channel = IncidentsChannel()
        
        message = await channel.broadcast_incident_created(
            room_id="room-001",
            incident_data={"name": "Hurricane Response", "priority": "critical"},
        )
        
        assert message is not None
        assert message.message_type == MessageType.NOTIFICATION

    @pytest.mark.asyncio
    async def test_broadcast_incident_update(self):
        """Test broadcasting incident update."""
        channel = IncidentsChannel()
        
        message = await channel.broadcast_incident_update(
            room_id="room-001",
            update_data={"status": "contained", "casualties": 5},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_task_update(self):
        """Test broadcasting task update."""
        channel = IncidentsChannel()
        
        message = await channel.broadcast_task_update(
            room_id="room-001",
            task_data={"task_id": "task-001", "status": "completed"},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_brief(self):
        """Test broadcasting incident brief."""
        channel = IncidentsChannel()
        
        message = await channel.broadcast_brief(
            room_id="room-001",
            brief_data={"summary": "Situation improving", "recommendations": []},
        )
        
        assert message is not None
        assert message.message_type == MessageType.BROADCAST

    @pytest.mark.asyncio
    async def test_broadcast_timeline_event(self):
        """Test broadcasting timeline event."""
        channel = IncidentsChannel()
        
        message = await channel.broadcast_timeline_event(
            room_id="room-001",
            event_data={"title": "Evacuation complete", "source": "Operations"},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_eoc_update(self):
        """Test broadcasting EOC update."""
        channel = IncidentsChannel()
        
        message = await channel.broadcast_eoc_update(
            eoc_data={"activation_level": 3, "agencies": 5},
        )
        
        assert message is not None


class TestDamageChannel:
    """Tests for DamageChannel class."""

    def test_channel_initialization(self):
        """Test DamageChannel initializes correctly."""
        channel = DamageChannel()
        assert channel is not None

    @pytest.mark.asyncio
    async def test_broadcast_assessment_complete(self):
        """Test broadcasting assessment completion."""
        channel = DamageChannel()
        
        message = await channel.broadcast_assessment_complete(
            assessment_data={"id": "assess-001", "damage_level": "major"},
        )
        
        assert message is not None
        assert message.message_type == MessageType.NOTIFICATION

    @pytest.mark.asyncio
    async def test_broadcast_drone_image_processed(self):
        """Test broadcasting drone image processed."""
        channel = DamageChannel()
        
        message = await channel.broadcast_drone_image_processed(
            image_data={"id": "img-001", "damage_detected": True},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_high_risk_alert(self):
        """Test broadcasting high risk alert."""
        channel = DamageChannel()
        
        message = await channel.broadcast_high_risk_alert(
            risk_data={"structure_id": "struct-001", "risk_score": 0.95},
        )
        
        assert message is not None
        assert message.priority == 7

    @pytest.mark.asyncio
    async def test_broadcast_recovery_update(self):
        """Test broadcasting recovery update."""
        channel = DamageChannel()
        
        message = await channel.broadcast_recovery_update(
            timeline_id="timeline-001",
            recovery_data={"phase": "short_term", "progress": 25},
        )
        
        assert message is not None

    @pytest.mark.asyncio
    async def test_broadcast_area_summary(self):
        """Test broadcasting area summary."""
        channel = DamageChannel()
        
        message = await channel.broadcast_area_summary(
            area_id="area-001",
            summary_data={"total_structures": 100, "damaged": 30},
        )
        
        assert message is not None
        assert message.message_type == MessageType.STATUS


class TestEmergencyWebSocketManager:
    """Tests for EmergencyWebSocketManager class."""

    def test_manager_initialization(self):
        """Test EmergencyWebSocketManager initializes correctly."""
        manager = EmergencyWebSocketManager()
        assert manager is not None
        assert hasattr(manager, 'crisis_channel')
        assert hasattr(manager, 'evac_channel')
        assert hasattr(manager, 'resources_channel')
        assert hasattr(manager, 'medical_channel')
        assert hasattr(manager, 'incidents_channel')
        assert hasattr(manager, 'damage_channel')

    def test_get_channel(self):
        """Test getting channel by type."""
        manager = EmergencyWebSocketManager()
        
        crisis = manager.get_channel(EmergencyChannelType.CRISIS)
        assert crisis is manager.crisis_channel
        
        evac = manager.get_channel(EmergencyChannelType.EVAC)
        assert evac is manager.evac_channel

    def test_get_all_connections(self):
        """Test getting all connections."""
        manager = EmergencyWebSocketManager()
        connections = manager.get_all_connections()
        
        assert isinstance(connections, dict)
        assert "crisis" in connections
        assert "evac" in connections
        assert "resources" in connections
        assert "medical" in connections
        assert "incidents" in connections
        assert "damage" in connections

    def test_get_connection_counts(self):
        """Test getting connection counts."""
        manager = EmergencyWebSocketManager()
        counts = manager.get_connection_counts()
        
        assert isinstance(counts, dict)
        assert all(isinstance(v, int) for v in counts.values())

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self):
        """Test broadcasting to all channels."""
        manager = EmergencyWebSocketManager()
        
        await manager.broadcast_to_all(
            message_type=MessageType.ALERT,
            payload={"message": "System-wide alert"},
            priority=10,
        )
