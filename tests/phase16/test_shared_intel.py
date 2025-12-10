"""
Tests for SharedIntelHub

Tests intelligence channels, message publishing, subscriptions,
and ACL management.
"""

import pytest
from datetime import datetime

from app.fusion_cloud.shared_intel import (
    SharedIntelHub,
    IntelChannel,
    ChannelType,
    IntelMessage,
    MessagePriority,
    MessageStatus,
    AgencyACL,
    ACLPermission,
    SubscriptionConfig,
)


@pytest.fixture
def intel_hub():
    """Create a fresh SharedIntelHub for each test"""
    return SharedIntelHub()


class TestChannelManagement:
    """Tests for channel management"""

    def test_create_channel(self, intel_hub):
        """Test creating a channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Active Pursuits",
            description="Real-time pursuit coordination",
            owner_tenant_id="tenant-001",
        )

        assert channel is not None
        assert channel.channel_type == ChannelType.PURSUITS
        assert channel.name == "Active Pursuits"
        assert channel.owner_tenant_id == "tenant-001"

    def test_create_public_channel(self, intel_hub):
        """Test creating a public channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.REGIONAL_ALERTS,
            name="Regional Alerts",
            owner_tenant_id="tenant-001",
            is_public=True,
        )

        assert channel is not None
        assert channel.is_public is True

    def test_create_regional_channel(self, intel_hub):
        """Test creating a regional channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.BOLOS,
            name="Regional BOLOs",
            owner_tenant_id="tenant-001",
            is_regional=True,
            region_codes=["CA-METRO", "CA-COUNTY"],
        )

        assert channel is not None
        assert channel.is_regional is True
        assert "CA-METRO" in channel.region_codes

    def test_get_channel(self, intel_hub):
        """Test getting a channel by ID"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Test Channel",
            owner_tenant_id="tenant-001",
        )

        retrieved = intel_hub.get_channel(channel.channel_id)
        assert retrieved is not None
        assert retrieved.channel_id == channel.channel_id

    def test_get_channel_by_type(self, intel_hub):
        """Test getting a channel by type"""
        intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        channel = intel_hub.get_channel_by_type(ChannelType.PURSUITS)
        assert channel is not None
        assert channel.channel_type == ChannelType.PURSUITS

    def test_get_all_channels(self, intel_hub):
        """Test getting all channels"""
        intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )
        intel_hub.create_channel(
            channel_type=ChannelType.BOLOS,
            name="BOLOs",
            owner_tenant_id="tenant-001",
        )

        channels = intel_hub.get_all_channels()
        assert len(channels) == 2

    def test_get_channels_for_tenant(self, intel_hub):
        """Test getting channels for a tenant"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )
        intel_hub.add_member_to_channel(channel.channel_id, "tenant-002")

        channels = intel_hub.get_channels_for_tenant("tenant-002")
        assert len(channels) == 1


class TestMemberManagement:
    """Tests for channel member management"""

    def test_add_member_to_channel(self, intel_hub):
        """Test adding a member to a channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        success = intel_hub.add_member_to_channel(channel.channel_id, "tenant-002")
        assert success is True

        updated = intel_hub.get_channel(channel.channel_id)
        assert "tenant-002" in updated.member_tenant_ids

    def test_remove_member_from_channel(self, intel_hub):
        """Test removing a member from a channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )
        intel_hub.add_member_to_channel(channel.channel_id, "tenant-002")

        success = intel_hub.remove_member_from_channel(channel.channel_id, "tenant-002")
        assert success is True

        updated = intel_hub.get_channel(channel.channel_id)
        assert "tenant-002" not in updated.member_tenant_ids

    def test_add_moderator(self, intel_hub):
        """Test adding a moderator to a channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        success = intel_hub.add_moderator(channel.channel_id, "tenant-002")
        assert success is True

        updated = intel_hub.get_channel(channel.channel_id)
        assert "tenant-002" in updated.moderator_tenant_ids


class TestACLManagement:
    """Tests for ACL management"""

    def test_set_channel_acl(self, intel_hub):
        """Test setting channel ACL"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        acl = AgencyACL(
            acl_id="acl-001",
            tenant_id="tenant-002",
            agency_name="Test PD",
            channel_id=channel.channel_id,
            permissions=[ACLPermission.READ, ACLPermission.WRITE],
            can_publish=True,
            can_subscribe=True,
        )

        success = intel_hub.set_channel_acl(channel.channel_id, acl)
        assert success is True

    def test_get_channel_acl(self, intel_hub):
        """Test getting channel ACL"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        acl = AgencyACL(
            acl_id="acl-001",
            tenant_id="tenant-002",
            agency_name="Test PD",
            channel_id=channel.channel_id,
            permissions=[ACLPermission.READ],
        )
        intel_hub.set_channel_acl(channel.channel_id, acl)

        retrieved = intel_hub.get_channel_acl(channel.channel_id, "tenant-002")
        assert retrieved is not None
        assert ACLPermission.READ in retrieved.permissions


class TestSubscriptions:
    """Tests for channel subscriptions"""

    def test_subscribe_to_channel(self, intel_hub):
        """Test subscribing to a channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        subscription = intel_hub.subscribe_to_channel(
            channel_id=channel.channel_id,
            tenant_id="tenant-002",
        )

        assert subscription is not None
        assert subscription.tenant_id == "tenant-002"
        assert subscription.channel_id == channel.channel_id

    def test_subscribe_with_filters(self, intel_hub):
        """Test subscribing with priority filters"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        subscription = intel_hub.subscribe_to_channel(
            channel_id=channel.channel_id,
            tenant_id="tenant-002",
            priority_filter=[MessagePriority.CRITICAL, MessagePriority.URGENT],
        )

        assert subscription is not None
        assert MessagePriority.CRITICAL in subscription.priority_filter

    def test_unsubscribe_from_channel(self, intel_hub):
        """Test unsubscribing from a channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )
        intel_hub.subscribe_to_channel(
            channel_id=channel.channel_id,
            tenant_id="tenant-002",
        )

        success = intel_hub.unsubscribe_from_channel(channel.channel_id, "tenant-002")
        assert success is True


class TestMessagePublishing:
    """Tests for message publishing"""

    def test_publish_message(self, intel_hub):
        """Test publishing a message"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        message = intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Active Pursuit",
            content="High-speed pursuit in progress",
        )

        assert message is not None
        assert message.title == "Active Pursuit"
        assert message.status == MessageStatus.PUBLISHED

    def test_publish_message_with_priority(self, intel_hub):
        """Test publishing a message with priority"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.OFFICER_SAFETY,
            name="Officer Safety",
            owner_tenant_id="tenant-001",
        )

        message = intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Officer Safety Alert",
            content="Known violent offender released",
            priority=MessagePriority.CRITICAL,
        )

        assert message is not None
        assert message.priority == MessagePriority.CRITICAL

    def test_publish_message_with_tags(self, intel_hub):
        """Test publishing a message with tags"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PATTERNS,
            name="Patterns",
            owner_tenant_id="tenant-001",
        )

        message = intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Crime Pattern",
            content="Emerging pattern detected",
            tags=["burglary", "vehicle", "pattern"],
        )

        assert message is not None
        assert "burglary" in message.tags


class TestMessageRetrieval:
    """Tests for message retrieval"""

    def test_get_message(self, intel_hub):
        """Test getting a message by ID"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )
        message = intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Test",
            content="Test content",
        )

        retrieved = intel_hub.get_message(message.message_id)
        assert retrieved is not None
        assert retrieved.message_id == message.message_id

    def test_get_channel_messages(self, intel_hub):
        """Test getting messages from a channel"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        for i in range(5):
            intel_hub.publish_message(
                channel_id=channel.channel_id,
                source_tenant_id="tenant-001",
                source_agency_name="Test PD",
                title=f"Message {i}",
                content=f"Content {i}",
            )

        messages = intel_hub.get_channel_messages(channel.channel_id)
        assert len(messages) == 5

    def test_get_channel_messages_with_priority_filter(self, intel_hub):
        """Test getting messages with priority filter"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Normal",
            content="Normal priority",
            priority=MessagePriority.NORMAL,
        )
        intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Critical",
            content="Critical priority",
            priority=MessagePriority.CRITICAL,
        )

        messages = intel_hub.get_channel_messages(
            channel.channel_id,
            priority_filter=[MessagePriority.CRITICAL],
        )
        assert len(messages) == 1
        assert messages[0].priority == MessagePriority.CRITICAL


class TestMessageActions:
    """Tests for message actions"""

    def test_update_message(self, intel_hub):
        """Test updating a message"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )
        message = intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Original",
            content="Original content",
        )

        success = intel_hub.update_message(
            message_id=message.message_id,
            content="Updated content",
        )
        assert success is True

        updated = intel_hub.get_message(message.message_id)
        assert updated.content == "Updated content"
        assert updated.status == MessageStatus.UPDATED

    def test_cancel_message(self, intel_hub):
        """Test cancelling a message"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.BOLOS,
            name="BOLOs",
            owner_tenant_id="tenant-001",
        )
        message = intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="BOLO",
            content="BOLO content",
        )

        success = intel_hub.cancel_message(message.message_id)
        assert success is True

        updated = intel_hub.get_message(message.message_id)
        assert updated.status == MessageStatus.CANCELLED

    def test_resolve_message(self, intel_hub):
        """Test resolving a message"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )
        message = intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Pursuit",
            content="Active pursuit",
        )

        success = intel_hub.resolve_message(message.message_id)
        assert success is True

        updated = intel_hub.get_message(message.message_id)
        assert updated.status == MessageStatus.RESOLVED

    def test_acknowledge_message(self, intel_hub):
        """Test acknowledging a message"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.OFFICER_SAFETY,
            name="Officer Safety",
            owner_tenant_id="tenant-001",
        )
        message = intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Alert",
            content="Safety alert",
        )

        success = intel_hub.acknowledge_message(message.message_id, "tenant-002")
        assert success is True

        updated = intel_hub.get_message(message.message_id)
        assert "tenant-002" in updated.acknowledged_by


class TestMetrics:
    """Tests for intel hub metrics"""

    def test_get_channel_metrics(self, intel_hub):
        """Test getting channel metrics"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )

        for i in range(3):
            intel_hub.publish_message(
                channel_id=channel.channel_id,
                source_tenant_id="tenant-001",
                source_agency_name="Test PD",
                title=f"Message {i}",
                content=f"Content {i}",
            )

        metrics = intel_hub.get_channel_metrics(channel.channel_id)
        assert metrics["message_count"] == 3

    def test_get_hub_metrics(self, intel_hub):
        """Test getting hub metrics"""
        channel = intel_hub.create_channel(
            channel_type=ChannelType.PURSUITS,
            name="Pursuits",
            owner_tenant_id="tenant-001",
        )
        intel_hub.publish_message(
            channel_id=channel.channel_id,
            source_tenant_id="tenant-001",
            source_agency_name="Test PD",
            title="Test",
            content="Test",
        )

        metrics = intel_hub.get_hub_metrics()
        assert metrics["total_channels"] == 1
        assert metrics["total_messages"] == 1
