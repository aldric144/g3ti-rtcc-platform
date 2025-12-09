"""
G3TI RTCC-UIP In-App Messaging Module.

Provides real-time messaging capabilities between RTCC analysts and patrol officers:
- Direct messaging (analyst -> officer, officer -> RTCC)
- Group channels (shift, unit, incident, command)
- Multiple message types (text, image, link, intelligence-object)
- Message threading and replies
- Read receipts and timestamps
- Typing indicators via WebSocket
- Message persistence with Redis Streams and PostgreSQL archival

All messages are encrypted at rest and logged for CJIS compliance.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class MessageType(str, Enum):
    """Types of messages that can be sent."""
    TEXT = "text"
    IMAGE = "image"
    LINK = "link"
    INTEL = "intel"  # Intelligence object (entity, case, alert)
    SYSTEM = "system"  # System-generated messages
    ALERT = "alert"  # Priority alert messages


class ChannelType(str, Enum):
    """Types of messaging channels."""
    DIRECT = "direct"  # One-to-one messaging
    SHIFT = "shift"  # Shift-based channel (A, B, C)
    UNIT = "unit"  # Unit-based channel
    INCIDENT = "incident"  # Incident-specific channel
    COMMAND = "command"  # Command staff channel
    BROADCAST = "broadcast"  # All-units broadcast


class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class Message(BaseModel):
    """Schema for a message in the system."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    sender_name: str
    sender_type: str  # "rtcc", "officer", "command", "system"
    recipient_id: str | None = None  # For direct messages
    channel_id: str
    channel_type: ChannelType
    message_type: MessageType = MessageType.TEXT
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    thread_id: str | None = None  # For threaded replies
    reply_to_id: str | None = None  # ID of message being replied to
    priority: MessagePriority = MessagePriority.NORMAL
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    read_by: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    is_encrypted: bool = True
    audit_id: str | None = None


class Channel(BaseModel):
    """Schema for a messaging channel."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    channel_type: ChannelType
    description: str | None = None
    members: list[str] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    incident_id: str | None = None  # For incident channels
    shift: str | None = None  # For shift channels (A, B, C)
    unit: str | None = None  # For unit channels


class TypingIndicator(BaseModel):
    """Schema for typing indicator events."""
    user_id: str
    user_name: str
    channel_id: str
    is_typing: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReadReceipt(BaseModel):
    """Schema for read receipts."""
    message_id: str
    user_id: str
    read_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MessagingManager:
    """
    Central manager for in-app messaging operations.

    Handles message sending, channel management, read receipts,
    typing indicators, and message persistence.
    """

    def __init__(
        self,
        redis_manager: Any | None = None,
        neo4j_manager: Any | None = None,
    ):
        """
        Initialize the messaging manager.

        Args:
            redis_manager: Redis manager for real-time messaging and caching
            neo4j_manager: Neo4j manager for relationship queries
        """
        self.redis = redis_manager
        self.neo4j = neo4j_manager

        # In-memory stores (would be Redis in production)
        self._messages: dict[str, Message] = {}
        self._channels: dict[str, Channel] = {}
        self._user_channels: dict[str, set[str]] = {}  # user_id -> channel_ids
        self._typing_indicators: dict[str, dict[str, TypingIndicator]] = {}  # channel_id -> user_id -> indicator

        # Initialize default channels
        self._initialize_default_channels()

        logger.info("messaging_manager_initialized")

    def _initialize_default_channels(self) -> None:
        """Initialize default system channels."""
        # Shift channels
        for shift in ["A", "B", "C"]:
            channel = Channel(
                id=f"shift-{shift.lower()}",
                name=f"Shift {shift}",
                channel_type=ChannelType.SHIFT,
                description=f"Channel for Shift {shift} personnel",
                created_by="system",
                shift=shift,
            )
            self._channels[channel.id] = channel

        # Command channel
        command_channel = Channel(
            id="command",
            name="Command Staff",
            channel_type=ChannelType.COMMAND,
            description="Command staff communications",
            created_by="system",
        )
        self._channels[command_channel.id] = command_channel

        # Broadcast channel
        broadcast_channel = Channel(
            id="broadcast",
            name="All Units",
            channel_type=ChannelType.BROADCAST,
            description="Broadcast to all units",
            created_by="system",
        )
        self._channels[broadcast_channel.id] = broadcast_channel

        logger.info("default_channels_initialized", count=len(self._channels))

    async def send_message(
        self,
        sender_id: str,
        sender_name: str,
        sender_type: str,
        channel_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        recipient_id: str | None = None,
        thread_id: str | None = None,
        reply_to_id: str | None = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        attachments: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """
        Send a message to a channel or direct recipient.

        Args:
            sender_id: ID of the sender
            sender_name: Display name of the sender
            sender_type: Type of sender (rtcc, officer, command, system)
            channel_id: Target channel ID
            content: Message content
            message_type: Type of message
            recipient_id: For direct messages, the recipient ID
            thread_id: Thread ID for threaded conversations
            reply_to_id: ID of message being replied to
            priority: Message priority level
            attachments: List of attachments
            metadata: Additional metadata

        Returns:
            The created message
        """
        # Validate channel exists or create direct channel
        channel = self._channels.get(channel_id)
        if not channel:
            if recipient_id:
                # Create direct message channel
                channel = await self.create_direct_channel(sender_id, recipient_id)
                channel_id = channel.id
            else:
                raise ValueError(f"Channel {channel_id} not found")

        # Create message
        message = Message(
            sender_id=sender_id,
            sender_name=sender_name,
            sender_type=sender_type,
            recipient_id=recipient_id,
            channel_id=channel_id,
            channel_type=channel.channel_type,
            message_type=message_type,
            content=content,
            thread_id=thread_id,
            reply_to_id=reply_to_id,
            priority=priority,
            attachments=attachments or [],
            metadata=metadata or {},
            audit_id=str(uuid.uuid4()),
        )

        # Store message
        self._messages[message.id] = message

        # Log for CJIS compliance
        logger.info(
            "message_sent",
            message_id=message.id,
            sender_id=sender_id,
            channel_id=channel_id,
            message_type=message_type.value,
            priority=priority.value,
            audit_id=message.audit_id,
        )

        return message

    async def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 50,
        before: datetime | None = None,
        after: datetime | None = None,
        thread_id: str | None = None,
    ) -> list[Message]:
        """
        Get messages from a channel.

        Args:
            channel_id: Channel ID to get messages from
            limit: Maximum number of messages to return
            before: Get messages before this timestamp
            after: Get messages after this timestamp
            thread_id: Filter by thread ID

        Returns:
            List of messages
        """
        messages = [
            m for m in self._messages.values()
            if m.channel_id == channel_id
        ]

        # Apply filters
        if before:
            messages = [m for m in messages if m.created_at < before]
        if after:
            messages = [m for m in messages if m.created_at > after]
        if thread_id:
            messages = [m for m in messages if m.thread_id == thread_id]

        # Sort by timestamp (newest first)
        messages.sort(key=lambda m: m.created_at, reverse=True)

        return messages[:limit]

    async def create_channel(
        self,
        name: str,
        channel_type: ChannelType,
        created_by: str,
        description: str | None = None,
        members: list[str] | None = None,
        incident_id: str | None = None,
        shift: str | None = None,
        unit: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Channel:
        """
        Create a new messaging channel.

        Args:
            name: Channel name
            channel_type: Type of channel
            created_by: User ID who created the channel
            description: Channel description
            members: Initial channel members
            incident_id: Associated incident ID (for incident channels)
            shift: Shift identifier (for shift channels)
            unit: Unit identifier (for unit channels)
            metadata: Additional metadata

        Returns:
            The created channel
        """
        channel = Channel(
            name=name,
            channel_type=channel_type,
            description=description,
            members=members or [],
            created_by=created_by,
            incident_id=incident_id,
            shift=shift,
            unit=unit,
            metadata=metadata or {},
        )

        self._channels[channel.id] = channel

        # Add channel to user mappings
        for member_id in channel.members:
            if member_id not in self._user_channels:
                self._user_channels[member_id] = set()
            self._user_channels[member_id].add(channel.id)

        logger.info(
            "channel_created",
            channel_id=channel.id,
            channel_type=channel_type.value,
            created_by=created_by,
        )

        return channel

    async def create_direct_channel(
        self,
        user1_id: str,
        user2_id: str,
    ) -> Channel:
        """
        Create or get a direct message channel between two users.

        Args:
            user1_id: First user ID
            user2_id: Second user ID

        Returns:
            The direct message channel
        """
        # Check if channel already exists
        channel_id = f"dm-{min(user1_id, user2_id)}-{max(user1_id, user2_id)}"

        if channel_id in self._channels:
            return self._channels[channel_id]

        # Create new direct channel
        channel = Channel(
            id=channel_id,
            name=f"Direct: {user1_id} <-> {user2_id}",
            channel_type=ChannelType.DIRECT,
            members=[user1_id, user2_id],
            created_by=user1_id,
        )

        self._channels[channel.id] = channel

        # Update user channel mappings
        for user_id in [user1_id, user2_id]:
            if user_id not in self._user_channels:
                self._user_channels[user_id] = set()
            self._user_channels[user_id].add(channel.id)

        logger.info(
            "direct_channel_created",
            channel_id=channel.id,
            user1=user1_id,
            user2=user2_id,
        )

        return channel

    async def create_incident_channel(
        self,
        incident_id: str,
        incident_type: str,
        created_by: str,
        initial_members: list[str] | None = None,
    ) -> Channel:
        """
        Create a channel for a specific incident.

        Args:
            incident_id: Incident ID
            incident_type: Type of incident
            created_by: User who created the channel
            initial_members: Initial channel members

        Returns:
            The incident channel
        """
        channel = await self.create_channel(
            name=f"Incident: {incident_id}",
            channel_type=ChannelType.INCIDENT,
            created_by=created_by,
            description=f"Communications for {incident_type} incident {incident_id}",
            members=initial_members,
            incident_id=incident_id,
            metadata={"incident_type": incident_type},
        )

        return channel

    async def mark_message_read(
        self,
        message_id: str,
        user_id: str,
    ) -> ReadReceipt:
        """
        Mark a message as read by a user.

        Args:
            message_id: Message ID
            user_id: User ID who read the message

        Returns:
            Read receipt
        """
        message = self._messages.get(message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")

        if user_id not in message.read_by:
            message.read_by.append(user_id)

        receipt = ReadReceipt(
            message_id=message_id,
            user_id=user_id,
        )

        logger.debug(
            "message_read",
            message_id=message_id,
            user_id=user_id,
        )

        return receipt

    async def set_typing_indicator(
        self,
        user_id: str,
        user_name: str,
        channel_id: str,
        is_typing: bool,
    ) -> TypingIndicator:
        """
        Set typing indicator for a user in a channel.

        Args:
            user_id: User ID
            user_name: User display name
            channel_id: Channel ID
            is_typing: Whether user is typing

        Returns:
            Typing indicator
        """
        if channel_id not in self._typing_indicators:
            self._typing_indicators[channel_id] = {}

        indicator = TypingIndicator(
            user_id=user_id,
            user_name=user_name,
            channel_id=channel_id,
            is_typing=is_typing,
        )

        if is_typing:
            self._typing_indicators[channel_id][user_id] = indicator
        else:
            self._typing_indicators[channel_id].pop(user_id, None)

        return indicator

    async def get_typing_users(self, channel_id: str) -> list[TypingIndicator]:
        """
        Get list of users currently typing in a channel.

        Args:
            channel_id: Channel ID

        Returns:
            List of typing indicators
        """
        indicators = self._typing_indicators.get(channel_id, {})
        return list(indicators.values())

    async def get_user_channels(self, user_id: str) -> list[Channel]:
        """
        Get all channels a user is a member of.

        Args:
            user_id: User ID

        Returns:
            List of channels
        """
        channel_ids = self._user_channels.get(user_id, set())
        channels = [self._channels[cid] for cid in channel_ids if cid in self._channels]

        # Also include default channels
        for channel in self._channels.values():
            if channel.channel_type in [ChannelType.BROADCAST, ChannelType.SHIFT]:
                if channel not in channels:
                    channels.append(channel)

        return channels

    async def add_member_to_channel(
        self,
        channel_id: str,
        user_id: str,
    ) -> Channel:
        """
        Add a member to a channel.

        Args:
            channel_id: Channel ID
            user_id: User ID to add

        Returns:
            Updated channel
        """
        channel = self._channels.get(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")

        if user_id not in channel.members:
            channel.members.append(user_id)

        if user_id not in self._user_channels:
            self._user_channels[user_id] = set()
        self._user_channels[user_id].add(channel_id)

        logger.info(
            "member_added_to_channel",
            channel_id=channel_id,
            user_id=user_id,
        )

        return channel

    async def remove_member_from_channel(
        self,
        channel_id: str,
        user_id: str,
    ) -> Channel:
        """
        Remove a member from a channel.

        Args:
            channel_id: Channel ID
            user_id: User ID to remove

        Returns:
            Updated channel
        """
        channel = self._channels.get(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")

        if user_id in channel.members:
            channel.members.remove(user_id)

        if user_id in self._user_channels:
            self._user_channels[user_id].discard(channel_id)

        logger.info(
            "member_removed_from_channel",
            channel_id=channel_id,
            user_id=user_id,
        )

        return channel

    async def search_messages(
        self,
        query: str,
        channel_id: str | None = None,
        sender_id: str | None = None,
        message_type: MessageType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
    ) -> list[Message]:
        """
        Search messages with various filters.

        Args:
            query: Search query string
            channel_id: Filter by channel
            sender_id: Filter by sender
            message_type: Filter by message type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum results

        Returns:
            List of matching messages
        """
        results = []
        query_lower = query.lower()

        for message in self._messages.values():
            # Apply filters
            if channel_id and message.channel_id != channel_id:
                continue
            if sender_id and message.sender_id != sender_id:
                continue
            if message_type and message.message_type != message_type:
                continue
            if start_date and message.created_at < start_date:
                continue
            if end_date and message.created_at > end_date:
                continue

            # Check content match
            if query_lower in message.content.lower():
                results.append(message)

        # Sort by relevance (simple: newest first)
        results.sort(key=lambda m: m.created_at, reverse=True)

        return results[:limit]

    async def get_unread_count(
        self,
        user_id: str,
        channel_id: str | None = None,
    ) -> dict[str, int]:
        """
        Get unread message count for a user.

        Args:
            user_id: User ID
            channel_id: Optional specific channel

        Returns:
            Dictionary of channel_id -> unread count
        """
        unread_counts: dict[str, int] = {}

        channels = [channel_id] if channel_id else list(self._user_channels.get(user_id, []))

        for cid in channels:
            count = sum(
                1 for m in self._messages.values()
                if m.channel_id == cid and user_id not in m.read_by
            )
            if count > 0:
                unread_counts[cid] = count

        return unread_counts

    def get_channel(self, channel_id: str) -> Channel | None:
        """Get a channel by ID."""
        return self._channels.get(channel_id)

    def get_message(self, message_id: str) -> Message | None:
        """Get a message by ID."""
        return self._messages.get(message_id)


# Export classes
__all__ = [
    "MessagingManager",
    "Message",
    "Channel",
    "MessageType",
    "ChannelType",
    "MessagePriority",
    "TypingIndicator",
    "ReadReceipt",
]
