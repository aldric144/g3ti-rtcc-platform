"""Tests for the In-App Messaging module."""


import pytest

from app.comms.messaging import (
    Channel,
    ChannelType,
    Message,
    MessagePriority,
    MessageType,
    MessagingManager,
)


@pytest.fixture
def messaging_manager():
    """Create a messaging manager instance."""
    return MessagingManager()


class TestMessagingManager:
    """Tests for MessagingManager."""

    @pytest.mark.asyncio
    async def test_send_message(self, messaging_manager):
        """Test sending a message."""
        message = await messaging_manager.send_message(
            sender_id="user1",
            sender_name="Test User",
            sender_type="officer",
            channel_id="test-channel",
            content="Hello, world!",
            message_type=MessageType.TEXT,
        )

        assert message is not None
        assert message.sender_id == "user1"
        assert message.sender_name == "Test User"
        assert message.content == "Hello, world!"
        assert message.message_type == MessageType.TEXT
        assert message.audit_id is not None

    @pytest.mark.asyncio
    async def test_send_message_with_priority(self, messaging_manager):
        """Test sending a message with priority."""
        message = await messaging_manager.send_message(
            sender_id="user1",
            sender_name="Test User",
            sender_type="rtcc",
            channel_id="test-channel",
            content="Urgent message",
            message_type=MessageType.ALERT,
            priority=MessagePriority.URGENT,
        )

        assert message.priority == MessagePriority.URGENT

    @pytest.mark.asyncio
    async def test_create_channel(self, messaging_manager):
        """Test creating a channel."""
        channel = await messaging_manager.create_channel(
            name="Test Channel",
            channel_type=ChannelType.UNIT,
            created_by="user1",
            description="A test channel",
            members=["user1", "user2"],
        )

        assert channel is not None
        assert channel.name == "Test Channel"
        assert channel.channel_type == ChannelType.UNIT
        assert "user1" in channel.members
        assert "user2" in channel.members

    @pytest.mark.asyncio
    async def test_create_incident_channel(self, messaging_manager):
        """Test creating an incident channel."""
        channel = await messaging_manager.create_incident_channel(
            incident_id="INC-001",
            created_by="user1",
        )

        assert channel is not None
        assert channel.incident_id == "INC-001"
        assert channel.channel_type == ChannelType.INCIDENT

    @pytest.mark.asyncio
    async def test_create_direct_channel(self, messaging_manager):
        """Test creating a direct message channel."""
        channel = await messaging_manager.create_direct_channel(
            user1_id="user1",
            user2_id="user2",
        )

        assert channel is not None
        assert channel.channel_type == ChannelType.DIRECT
        assert "user1" in channel.members
        assert "user2" in channel.members

    @pytest.mark.asyncio
    async def test_get_channel_messages(self, messaging_manager):
        """Test getting messages from a channel."""
        # Send some messages
        await messaging_manager.send_message(
            sender_id="user1",
            sender_name="User 1",
            sender_type="officer",
            channel_id="test-channel",
            content="Message 1",
        )
        await messaging_manager.send_message(
            sender_id="user2",
            sender_name="User 2",
            sender_type="officer",
            channel_id="test-channel",
            content="Message 2",
        )

        messages = await messaging_manager.get_channel_messages("test-channel")

        assert len(messages) >= 2

    @pytest.mark.asyncio
    async def test_mark_message_read(self, messaging_manager):
        """Test marking a message as read."""
        message = await messaging_manager.send_message(
            sender_id="user1",
            sender_name="User 1",
            sender_type="officer",
            channel_id="test-channel",
            content="Test message",
        )

        receipt = await messaging_manager.mark_message_read(
            message_id=message.id,
            user_id="user2",
        )

        assert receipt is not None
        assert receipt.message_id == message.id
        assert receipt.user_id == "user2"

    @pytest.mark.asyncio
    async def test_typing_indicator(self, messaging_manager):
        """Test typing indicator."""
        await messaging_manager.set_typing_indicator(
            channel_id="test-channel",
            user_id="user1",
            user_name="User 1",
            is_typing=True,
        )

        typing_users = await messaging_manager.get_typing_users("test-channel")

        assert "user1" in typing_users

    @pytest.mark.asyncio
    async def test_add_member_to_channel(self, messaging_manager):
        """Test adding a member to a channel."""
        channel = await messaging_manager.create_channel(
            name="Test Channel",
            channel_type=ChannelType.UNIT,
            created_by="user1",
        )

        updated_channel = await messaging_manager.add_member_to_channel(
            channel_id=channel.id,
            user_id="user2",
        )

        assert "user2" in updated_channel.members

    @pytest.mark.asyncio
    async def test_search_messages(self, messaging_manager):
        """Test searching messages."""
        await messaging_manager.send_message(
            sender_id="user1",
            sender_name="User 1",
            sender_type="officer",
            channel_id="test-channel",
            content="Important intel about suspect",
        )

        results = await messaging_manager.search_messages(query="intel")

        assert len(results) >= 1
        assert any("intel" in m.content.lower() for m in results)


class TestMessageModel:
    """Tests for Message model."""

    def test_message_creation(self):
        """Test creating a message."""
        message = Message(
            sender_id="user1",
            sender_name="Test User",
            sender_type="officer",
            channel_id="test-channel",
            content="Hello",
            message_type=MessageType.TEXT,
        )

        assert message.id is not None
        assert message.audit_id is not None
        assert message.created_at is not None

    def test_message_with_attachments(self):
        """Test message with attachments."""
        message = Message(
            sender_id="user1",
            sender_name="Test User",
            sender_type="officer",
            channel_id="test-channel",
            content="See attached",
            message_type=MessageType.IMAGE,
            attachments=[{"type": "image", "url": "http://example.com/image.jpg"}],
        )

        assert len(message.attachments) == 1


class TestChannelModel:
    """Tests for Channel model."""

    def test_channel_creation(self):
        """Test creating a channel."""
        channel = Channel(
            name="Test Channel",
            channel_type=ChannelType.UNIT,
            created_by="user1",
        )

        assert channel.id is not None
        assert channel.is_active is True

    def test_incident_channel(self):
        """Test incident channel."""
        channel = Channel(
            name="Incident Channel",
            channel_type=ChannelType.INCIDENT,
            created_by="user1",
            incident_id="INC-001",
        )

        assert channel.incident_id == "INC-001"
