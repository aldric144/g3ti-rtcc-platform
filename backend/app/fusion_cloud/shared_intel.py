"""
SharedIntelHub - Real-time intelligence sharing for G3TI Fusion Cloud

Manages:
- Real-time topic channels (pursuits, BOLOs, patterns, high-risk suspects, regional alerts)
- Cross-agency subscriptions
- Agency-level ACLs
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
import uuid


class ChannelType(str, Enum):
    """Types of intelligence channels"""
    PURSUITS = "pursuits"
    BOLOS = "bolos"
    PATTERNS = "patterns"
    HIGH_RISK_SUSPECTS = "high_risk_suspects"
    REGIONAL_ALERTS = "regional_alerts"
    OFFICER_SAFETY = "officer_safety"
    MISSING_PERSONS = "missing_persons"
    AMBER_ALERTS = "amber_alerts"
    SILVER_ALERTS = "silver_alerts"
    CRITICAL_INCIDENTS = "critical_incidents"
    GANG_ACTIVITY = "gang_activity"
    NARCOTICS = "narcotics"
    HUMAN_TRAFFICKING = "human_trafficking"
    TERRORISM = "terrorism"
    CYBER_THREATS = "cyber_threats"
    CUSTOM = "custom"


class MessagePriority(str, Enum):
    """Priority levels for intel messages"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"
    FLASH = "flash"


class MessageStatus(str, Enum):
    """Status of an intel message"""
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    UPDATED = "updated"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    RESOLVED = "resolved"


class ACLPermission(str, Enum):
    """ACL permission types"""
    READ = "read"
    WRITE = "write"
    PUBLISH = "publish"
    MODERATE = "moderate"
    ADMIN = "admin"


@dataclass
class AgencyACL:
    """Access control list for an agency"""
    acl_id: str
    tenant_id: str
    agency_name: str
    channel_id: str
    permissions: List[ACLPermission] = field(default_factory=list)
    can_publish: bool = True
    can_subscribe: bool = True
    can_moderate: bool = False
    max_priority: MessagePriority = MessagePriority.CRITICAL
    jurisdiction_filter: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubscriptionConfig:
    """Configuration for a channel subscription"""
    subscription_id: str
    tenant_id: str
    channel_id: str
    enabled: bool = True
    priority_filter: List[MessagePriority] = field(default_factory=list)
    jurisdiction_filter: List[str] = field(default_factory=list)
    keyword_filter: List[str] = field(default_factory=list)
    webhook_url: str = ""
    email_notifications: bool = False
    email_addresses: List[str] = field(default_factory=list)
    sms_notifications: bool = False
    sms_numbers: List[str] = field(default_factory=list)
    push_notifications: bool = True
    batch_delivery: bool = False
    batch_interval_minutes: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntelAttachment:
    """Attachment for an intel message"""
    attachment_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    storage_url: str
    thumbnail_url: str = ""
    description: str = ""
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    uploaded_by: str = ""


@dataclass
class IntelMessage:
    """An intelligence message in a channel"""
    message_id: str
    channel_id: str
    channel_type: ChannelType
    source_tenant_id: str
    source_agency_name: str
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PUBLISHED
    title: str = ""
    summary: str = ""
    content: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    attachments: List[IntelAttachment] = field(default_factory=list)
    jurisdiction_codes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    related_message_ids: List[str] = field(default_factory=list)
    related_case_ids: List[str] = field(default_factory=list)
    related_incident_ids: List[str] = field(default_factory=list)
    target_tenants: List[str] = field(default_factory=list)
    read_by_tenants: List[str] = field(default_factory=list)
    acknowledged_by: Dict[str, datetime] = field(default_factory=dict)
    view_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntelChannel:
    """An intelligence sharing channel"""
    channel_id: str
    channel_type: ChannelType
    name: str
    description: str = ""
    owner_tenant_id: str = ""
    is_public: bool = False
    is_regional: bool = True
    region_codes: List[str] = field(default_factory=list)
    member_tenant_ids: List[str] = field(default_factory=list)
    moderator_tenant_ids: List[str] = field(default_factory=list)
    acls: List[AgencyACL] = field(default_factory=list)
    subscriptions: List[SubscriptionConfig] = field(default_factory=list)
    message_count: int = 0
    subscriber_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChannelMetrics:
    """Metrics for a channel"""
    channel_id: str
    message_count_24h: int = 0
    message_count_7d: int = 0
    message_count_30d: int = 0
    active_subscribers: int = 0
    avg_response_time_minutes: float = 0.0
    messages_by_priority: Dict[MessagePriority, int] = field(default_factory=dict)


@dataclass
class HubMetrics:
    """Metrics for the shared intel hub"""
    total_channels: int = 0
    total_messages: int = 0
    total_subscriptions: int = 0
    active_channels: int = 0
    messages_24h: int = 0
    channels_by_type: Dict[ChannelType, int] = field(default_factory=dict)


class SharedIntelHub:
    """
    Manages real-time intelligence sharing across agencies.
    
    Provides:
    - Real-time topic channels (pursuits, BOLOs, patterns, etc.)
    - Cross-agency subscriptions
    - Agency-level ACLs
    - Message publishing and delivery
    """
    
    def __init__(self):
        self._channels: Dict[str, IntelChannel] = {}
        self._messages: Dict[str, IntelMessage] = {}
        self._messages_by_channel: Dict[str, List[str]] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._events: List[Dict[str, Any]] = []
        self._max_events = 10000
        self._max_messages_per_channel = 10000
        
        self._init_default_channels()
    
    def _init_default_channels(self) -> None:
        """Initialize default channels"""
        default_channels = [
            (ChannelType.PURSUITS, "Active Pursuits", "Real-time pursuit tracking and coordination"),
            (ChannelType.BOLOS, "Be On Lookout", "BOLO alerts for suspects, vehicles, and persons of interest"),
            (ChannelType.PATTERNS, "Crime Patterns", "Emerging crime patterns and trends"),
            (ChannelType.HIGH_RISK_SUSPECTS, "High-Risk Suspects", "High-risk suspect alerts and updates"),
            (ChannelType.REGIONAL_ALERTS, "Regional Alerts", "Regional law enforcement alerts"),
            (ChannelType.OFFICER_SAFETY, "Officer Safety", "Officer safety bulletins and alerts"),
            (ChannelType.MISSING_PERSONS, "Missing Persons", "Missing person alerts and updates"),
            (ChannelType.CRITICAL_INCIDENTS, "Critical Incidents", "Critical incident notifications"),
        ]
        
        for channel_type, name, description in default_channels:
            channel = IntelChannel(
                channel_id=f"channel-{channel_type.value}",
                channel_type=channel_type,
                name=name,
                description=description,
                is_public=True,
                is_regional=True,
            )
            self._channels[channel.channel_id] = channel
            self._messages_by_channel[channel.channel_id] = []
    
    def create_channel(
        self,
        channel_type: ChannelType,
        name: str,
        description: str = "",
        owner_tenant_id: str = "",
        is_public: bool = False,
        is_regional: bool = True,
        region_codes: List[str] = None,
        member_tenant_ids: List[str] = None,
    ) -> Optional[IntelChannel]:
        """Create a new intelligence channel"""
        channel_id = f"channel-{uuid.uuid4().hex[:12]}"
        
        channel = IntelChannel(
            channel_id=channel_id,
            channel_type=channel_type,
            name=name,
            description=description,
            owner_tenant_id=owner_tenant_id,
            is_public=is_public,
            is_regional=is_regional,
            region_codes=region_codes or [],
            member_tenant_ids=member_tenant_ids or [],
        )
        
        if owner_tenant_id and owner_tenant_id not in channel.member_tenant_ids:
            channel.member_tenant_ids.append(owner_tenant_id)
            channel.moderator_tenant_ids.append(owner_tenant_id)
        
        self._channels[channel_id] = channel
        self._messages_by_channel[channel_id] = []
        
        self._record_event("channel_created", {
            "channel_id": channel_id,
            "channel_type": channel_type.value,
            "name": name,
            "owner_tenant_id": owner_tenant_id,
        })
        self._notify_callbacks("channel_created", channel)
        
        return channel
    
    def get_channel(self, channel_id: str) -> Optional[IntelChannel]:
        """Get a channel by ID"""
        return self._channels.get(channel_id)
    
    def get_channel_by_type(self, channel_type: ChannelType) -> Optional[IntelChannel]:
        """Get the default channel for a type"""
        channel_id = f"channel-{channel_type.value}"
        return self._channels.get(channel_id)
    
    def get_all_channels(self) -> List[IntelChannel]:
        """Get all channels"""
        return list(self._channels.values())
    
    def get_channels_for_tenant(self, tenant_id: str) -> List[IntelChannel]:
        """Get channels accessible to a tenant"""
        channels = []
        for channel in self._channels.values():
            if channel.is_public:
                channels.append(channel)
            elif tenant_id in channel.member_tenant_ids:
                channels.append(channel)
            elif tenant_id == channel.owner_tenant_id:
                channels.append(channel)
        return channels
    
    def add_member_to_channel(
        self,
        channel_id: str,
        tenant_id: str,
        added_by: str = "",
    ) -> bool:
        """Add a member to a channel"""
        if channel_id not in self._channels:
            return False
        
        channel = self._channels[channel_id]
        
        if tenant_id not in channel.member_tenant_ids:
            channel.member_tenant_ids.append(tenant_id)
            channel.subscriber_count += 1
            channel.updated_at = datetime.utcnow()
            
            self._record_event("member_added", {
                "channel_id": channel_id,
                "tenant_id": tenant_id,
                "added_by": added_by,
            })
            
            return True
        
        return False
    
    def remove_member_from_channel(
        self,
        channel_id: str,
        tenant_id: str,
        removed_by: str = "",
    ) -> bool:
        """Remove a member from a channel"""
        if channel_id not in self._channels:
            return False
        
        channel = self._channels[channel_id]
        
        if tenant_id in channel.member_tenant_ids:
            channel.member_tenant_ids.remove(tenant_id)
            channel.subscriber_count = max(0, channel.subscriber_count - 1)
            channel.updated_at = datetime.utcnow()
            
            if tenant_id in channel.moderator_tenant_ids:
                channel.moderator_tenant_ids.remove(tenant_id)
            
            self._record_event("member_removed", {
                "channel_id": channel_id,
                "tenant_id": tenant_id,
                "removed_by": removed_by,
            })
            
            return True
        
        return False
    
    def add_moderator(
        self,
        channel_id: str,
        tenant_id: str,
        added_by: str = "",
    ) -> bool:
        """Add a moderator to a channel"""
        if channel_id not in self._channels:
            return False
        
        channel = self._channels[channel_id]
        
        if tenant_id not in channel.member_tenant_ids:
            channel.member_tenant_ids.append(tenant_id)
        
        if tenant_id not in channel.moderator_tenant_ids:
            channel.moderator_tenant_ids.append(tenant_id)
            channel.updated_at = datetime.utcnow()
            
            self._record_event("moderator_added", {
                "channel_id": channel_id,
                "tenant_id": tenant_id,
                "added_by": added_by,
            })
            
            return True
        
        return False
    
    def set_channel_acl(
        self,
        channel_id: str,
        tenant_id: str,
        agency_name: str,
        permissions: List[ACLPermission],
        can_publish: bool = True,
        can_subscribe: bool = True,
        can_moderate: bool = False,
        jurisdiction_filter: List[str] = None,
        created_by: str = "",
        expires_in_days: int = None,
    ) -> Optional[AgencyACL]:
        """Set ACL for an agency on a channel"""
        if channel_id not in self._channels:
            return None
        
        channel = self._channels[channel_id]
        
        acl_id = f"acl-{uuid.uuid4().hex[:8]}"
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        acl = AgencyACL(
            acl_id=acl_id,
            tenant_id=tenant_id,
            agency_name=agency_name,
            channel_id=channel_id,
            permissions=permissions,
            can_publish=can_publish,
            can_subscribe=can_subscribe,
            can_moderate=can_moderate,
            jurisdiction_filter=jurisdiction_filter or [],
            created_by=created_by,
            expires_at=expires_at,
        )
        
        channel.acls = [a for a in channel.acls if a.tenant_id != tenant_id]
        channel.acls.append(acl)
        channel.updated_at = datetime.utcnow()
        
        self._record_event("acl_set", {
            "channel_id": channel_id,
            "tenant_id": tenant_id,
            "acl_id": acl_id,
        })
        
        return acl
    
    def get_channel_acl(self, channel_id: str, tenant_id: str) -> Optional[AgencyACL]:
        """Get ACL for a tenant on a channel"""
        if channel_id not in self._channels:
            return None
        
        channel = self._channels[channel_id]
        
        for acl in channel.acls:
            if acl.tenant_id == tenant_id:
                return acl
        
        return None
    
    def subscribe_to_channel(
        self,
        channel_id: str,
        tenant_id: str,
        priority_filter: List[MessagePriority] = None,
        jurisdiction_filter: List[str] = None,
        keyword_filter: List[str] = None,
        webhook_url: str = "",
        email_notifications: bool = False,
        push_notifications: bool = True,
    ) -> Optional[SubscriptionConfig]:
        """Subscribe to a channel"""
        if channel_id not in self._channels:
            return None
        
        channel = self._channels[channel_id]
        
        if not channel.is_public and tenant_id not in channel.member_tenant_ids:
            return None
        
        subscription_id = f"sub-{uuid.uuid4().hex[:8]}"
        
        subscription = SubscriptionConfig(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            channel_id=channel_id,
            priority_filter=priority_filter or [],
            jurisdiction_filter=jurisdiction_filter or [],
            keyword_filter=keyword_filter or [],
            webhook_url=webhook_url,
            email_notifications=email_notifications,
            push_notifications=push_notifications,
        )
        
        channel.subscriptions = [s for s in channel.subscriptions if s.tenant_id != tenant_id]
        channel.subscriptions.append(subscription)
        channel.subscriber_count = len(channel.subscriptions)
        channel.updated_at = datetime.utcnow()
        
        self._record_event("subscription_created", {
            "channel_id": channel_id,
            "tenant_id": tenant_id,
            "subscription_id": subscription_id,
        })
        
        return subscription
    
    def unsubscribe_from_channel(
        self,
        channel_id: str,
        tenant_id: str,
    ) -> bool:
        """Unsubscribe from a channel"""
        if channel_id not in self._channels:
            return False
        
        channel = self._channels[channel_id]
        original_count = len(channel.subscriptions)
        channel.subscriptions = [s for s in channel.subscriptions if s.tenant_id != tenant_id]
        
        if len(channel.subscriptions) < original_count:
            channel.subscriber_count = len(channel.subscriptions)
            channel.updated_at = datetime.utcnow()
            
            self._record_event("subscription_removed", {
                "channel_id": channel_id,
                "tenant_id": tenant_id,
            })
            
            return True
        
        return False
    
    def publish_message(
        self,
        channel_id: str,
        source_tenant_id: str,
        source_agency_name: str,
        title: str,
        content: str,
        priority: MessagePriority = MessagePriority.NORMAL,
        summary: str = "",
        payload: Dict[str, Any] = None,
        jurisdiction_codes: List[str] = None,
        tags: List[str] = None,
        target_tenants: List[str] = None,
        related_case_ids: List[str] = None,
        related_incident_ids: List[str] = None,
        expires_in_hours: int = None,
        created_by: str = "",
    ) -> Optional[IntelMessage]:
        """Publish a message to a channel"""
        if channel_id not in self._channels:
            return None
        
        channel = self._channels[channel_id]
        
        if not channel.is_public and source_tenant_id not in channel.member_tenant_ids:
            return None
        
        message_id = f"msg-{uuid.uuid4().hex[:12]}"
        
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        message = IntelMessage(
            message_id=message_id,
            channel_id=channel_id,
            channel_type=channel.channel_type,
            source_tenant_id=source_tenant_id,
            source_agency_name=source_agency_name,
            priority=priority,
            status=MessageStatus.PUBLISHED,
            title=title,
            summary=summary,
            content=content,
            payload=payload or {},
            jurisdiction_codes=jurisdiction_codes or [],
            tags=tags or [],
            target_tenants=target_tenants or [],
            related_case_ids=related_case_ids or [],
            related_incident_ids=related_incident_ids or [],
            published_at=datetime.utcnow(),
            expires_at=expires_at,
            created_by=created_by,
        )
        
        self._messages[message_id] = message
        
        if channel_id not in self._messages_by_channel:
            self._messages_by_channel[channel_id] = []
        self._messages_by_channel[channel_id].append(message_id)
        
        if len(self._messages_by_channel[channel_id]) > self._max_messages_per_channel:
            old_message_id = self._messages_by_channel[channel_id].pop(0)
            if old_message_id in self._messages:
                del self._messages[old_message_id]
        
        channel.message_count += 1
        channel.updated_at = datetime.utcnow()
        
        self._notify_subscribers(message, channel)
        
        self._record_event("message_published", {
            "message_id": message_id,
            "channel_id": channel_id,
            "source_tenant_id": source_tenant_id,
            "priority": priority.value,
        })
        self._notify_callbacks("message_published", message)
        
        return message
    
    def update_message(
        self,
        message_id: str,
        title: str = None,
        content: str = None,
        summary: str = None,
        priority: MessagePriority = None,
        status: MessageStatus = None,
        updated_by: str = "",
    ) -> bool:
        """Update a message"""
        if message_id not in self._messages:
            return False
        
        message = self._messages[message_id]
        
        if title is not None:
            message.title = title
        if content is not None:
            message.content = content
        if summary is not None:
            message.summary = summary
        if priority is not None:
            message.priority = priority
        if status is not None:
            message.status = status
        
        message.updated_at = datetime.utcnow()
        message.status = MessageStatus.UPDATED
        
        self._record_event("message_updated", {
            "message_id": message_id,
            "updated_by": updated_by,
        })
        self._notify_callbacks("message_updated", message)
        
        return True
    
    def cancel_message(self, message_id: str, cancelled_by: str = "") -> bool:
        """Cancel a message"""
        if message_id not in self._messages:
            return False
        
        message = self._messages[message_id]
        message.status = MessageStatus.CANCELLED
        message.updated_at = datetime.utcnow()
        
        self._record_event("message_cancelled", {
            "message_id": message_id,
            "cancelled_by": cancelled_by,
        })
        self._notify_callbacks("message_cancelled", message)
        
        return True
    
    def resolve_message(self, message_id: str, resolved_by: str = "") -> bool:
        """Mark a message as resolved"""
        if message_id not in self._messages:
            return False
        
        message = self._messages[message_id]
        message.status = MessageStatus.RESOLVED
        message.updated_at = datetime.utcnow()
        
        self._record_event("message_resolved", {
            "message_id": message_id,
            "resolved_by": resolved_by,
        })
        self._notify_callbacks("message_resolved", message)
        
        return True
    
    def acknowledge_message(
        self,
        message_id: str,
        tenant_id: str,
        acknowledged_by: str = "",
    ) -> bool:
        """Acknowledge receipt of a message"""
        if message_id not in self._messages:
            return False
        
        message = self._messages[message_id]
        message.acknowledged_by[tenant_id] = datetime.utcnow()
        
        if tenant_id not in message.read_by_tenants:
            message.read_by_tenants.append(tenant_id)
        
        self._record_event("message_acknowledged", {
            "message_id": message_id,
            "tenant_id": tenant_id,
            "acknowledged_by": acknowledged_by,
        })
        
        return True
    
    def get_message(self, message_id: str) -> Optional[IntelMessage]:
        """Get a message by ID"""
        message = self._messages.get(message_id)
        if message:
            message.view_count += 1
        return message
    
    def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 100,
        priority_filter: List[MessagePriority] = None,
        status_filter: List[MessageStatus] = None,
        since: datetime = None,
    ) -> List[IntelMessage]:
        """Get messages from a channel"""
        if channel_id not in self._messages_by_channel:
            return []
        
        message_ids = self._messages_by_channel[channel_id]
        messages = []
        
        for message_id in reversed(message_ids):
            if message_id not in self._messages:
                continue
            
            message = self._messages[message_id]
            
            if priority_filter and message.priority not in priority_filter:
                continue
            
            if status_filter and message.status not in status_filter:
                continue
            
            if since and message.created_at < since:
                continue
            
            messages.append(message)
            
            if len(messages) >= limit:
                break
        
        return messages
    
    def get_messages_for_tenant(
        self,
        tenant_id: str,
        channel_types: List[ChannelType] = None,
        priority_filter: List[MessagePriority] = None,
        limit: int = 100,
        since: datetime = None,
    ) -> List[IntelMessage]:
        """Get messages accessible to a tenant"""
        accessible_channels = self.get_channels_for_tenant(tenant_id)
        
        if channel_types:
            accessible_channels = [c for c in accessible_channels if c.channel_type in channel_types]
        
        all_messages = []
        
        for channel in accessible_channels:
            messages = self.get_channel_messages(
                channel.channel_id,
                limit=limit,
                priority_filter=priority_filter,
                since=since,
            )
            all_messages.extend(messages)
        
        all_messages.sort(key=lambda m: m.created_at, reverse=True)
        
        return all_messages[:limit]
    
    def search_messages(
        self,
        query: str,
        channel_ids: List[str] = None,
        tenant_id: str = None,
        limit: int = 50,
    ) -> List[IntelMessage]:
        """Search messages by keyword"""
        results = []
        query_lower = query.lower()
        
        for message in self._messages.values():
            if channel_ids and message.channel_id not in channel_ids:
                continue
            
            if query_lower in message.title.lower() or \
               query_lower in message.content.lower() or \
               query_lower in message.summary.lower() or \
               any(query_lower in tag.lower() for tag in message.tags):
                results.append(message)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_channel_metrics(self, channel_id: str) -> Optional[ChannelMetrics]:
        """Get metrics for a channel"""
        if channel_id not in self._channels:
            return None
        
        channel = self._channels[channel_id]
        
        metrics = ChannelMetrics(channel_id=channel_id)
        metrics.active_subscribers = len(channel.subscriptions)
        
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        for message_id in self._messages_by_channel.get(channel_id, []):
            if message_id not in self._messages:
                continue
            
            message = self._messages[message_id]
            
            if message.created_at >= day_ago:
                metrics.message_count_24h += 1
            if message.created_at >= week_ago:
                metrics.message_count_7d += 1
            if message.created_at >= month_ago:
                metrics.message_count_30d += 1
            
            metrics.messages_by_priority[message.priority] = \
                metrics.messages_by_priority.get(message.priority, 0) + 1
        
        return metrics
    
    def get_hub_metrics(self) -> HubMetrics:
        """Get metrics for the entire hub"""
        metrics = HubMetrics()
        metrics.total_channels = len(self._channels)
        metrics.total_messages = len(self._messages)
        
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        
        for channel in self._channels.values():
            metrics.total_subscriptions += len(channel.subscriptions)
            
            if channel.message_count > 0:
                metrics.active_channels += 1
            
            metrics.channels_by_type[channel.channel_type] = \
                metrics.channels_by_type.get(channel.channel_type, 0) + 1
        
        for message in self._messages.values():
            if message.created_at >= day_ago:
                metrics.messages_24h += 1
        
        return metrics
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self._events[-limit:]
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type"""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
    
    def _notify_subscribers(self, message: IntelMessage, channel: IntelChannel) -> None:
        """Notify subscribers of a new message"""
        for subscription in channel.subscriptions:
            if not subscription.enabled:
                continue
            
            if subscription.priority_filter:
                if message.priority not in subscription.priority_filter:
                    continue
            
            if subscription.jurisdiction_filter:
                if not any(jc in message.jurisdiction_codes for jc in subscription.jurisdiction_filter):
                    continue
            
            if subscription.keyword_filter:
                content_lower = f"{message.title} {message.content} {message.summary}".lower()
                if not any(kw.lower() in content_lower for kw in subscription.keyword_filter):
                    continue
            
            self._notify_callbacks("subscription_notification", {
                "subscription": subscription,
                "message": message,
            })
    
    def _record_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record an event"""
        event = {
            "event_id": f"evt-{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        self._events.append(event)
        
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
    
    def _notify_callbacks(self, event_type: str, data: Any) -> None:
        """Notify registered callbacks"""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(data)
                except Exception:
                    pass
