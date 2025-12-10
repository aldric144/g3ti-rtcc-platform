"""
Fusion Cloud WebSocket Channels

Provides real-time WebSocket channels for:
- /ws/fusion/tenants - Tenant events
- /ws/fusion/intel/{channel} - Intelligence channel messages
- /ws/fusion/jointops/{room_id} - Joint operations room
- /ws/fusion/analytics - Analytics updates
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
import json
import asyncio
import uuid


@dataclass
class WebSocketConnection:
    """A WebSocket connection"""
    connection_id: str
    tenant_id: str
    user_id: str
    channel: str
    room_id: str = ""
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChannelMessage:
    """A message for a WebSocket channel"""
    message_id: str
    channel: str
    event_type: str
    payload: Dict[str, Any]
    source_tenant_id: str = ""
    target_tenants: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FusionCloudWebSocketManager:
    """
    Manages WebSocket connections for the Fusion Cloud.
    
    Channels:
    - /ws/fusion/tenants - Tenant lifecycle events
    - /ws/fusion/intel/{channel_id} - Intelligence channel messages
    - /ws/fusion/jointops/{room_id} - Joint operations room updates
    - /ws/fusion/analytics - Analytics updates and alerts
    """
    
    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._connections_by_channel: Dict[str, Set[str]] = {}
        self._connections_by_tenant: Dict[str, Set[str]] = {}
        self._connections_by_room: Dict[str, Set[str]] = {}
        self._message_queue: List[ChannelMessage] = []
        self._max_queue_size = 10000
        self._subscribers: Dict[str, List[callable]] = {}
    
    async def connect(
        self,
        websocket: Any,
        channel: str,
        tenant_id: str,
        user_id: str,
        room_id: str = "",
    ) -> str:
        """Register a new WebSocket connection"""
        connection_id = f"ws-{uuid.uuid4().hex[:12]}"
        
        connection = WebSocketConnection(
            connection_id=connection_id,
            tenant_id=tenant_id,
            user_id=user_id,
            channel=channel,
            room_id=room_id,
        )
        
        self._connections[connection_id] = connection
        
        if channel not in self._connections_by_channel:
            self._connections_by_channel[channel] = set()
        self._connections_by_channel[channel].add(connection_id)
        
        if tenant_id not in self._connections_by_tenant:
            self._connections_by_tenant[tenant_id] = set()
        self._connections_by_tenant[tenant_id].add(connection_id)
        
        if room_id:
            if room_id not in self._connections_by_room:
                self._connections_by_room[room_id] = set()
            self._connections_by_room[room_id].add(connection_id)
        
        await self._broadcast_to_channel(channel, {
            "event": "user_connected",
            "connection_id": connection_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return connection_id
    
    async def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection"""
        if connection_id not in self._connections:
            return
        
        connection = self._connections[connection_id]
        
        if connection.channel in self._connections_by_channel:
            self._connections_by_channel[connection.channel].discard(connection_id)
        
        if connection.tenant_id in self._connections_by_tenant:
            self._connections_by_tenant[connection.tenant_id].discard(connection_id)
        
        if connection.room_id and connection.room_id in self._connections_by_room:
            self._connections_by_room[connection.room_id].discard(connection_id)
        
        await self._broadcast_to_channel(connection.channel, {
            "event": "user_disconnected",
            "connection_id": connection_id,
            "tenant_id": connection.tenant_id,
            "user_id": connection.user_id,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        del self._connections[connection_id]
    
    async def broadcast_tenant_event(
        self,
        event_type: str,
        tenant_id: str,
        data: Dict[str, Any],
    ) -> None:
        """Broadcast a tenant event"""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel="tenants",
            event_type=event_type,
            payload={
                "event": event_type,
                "tenant_id": tenant_id,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            },
            source_tenant_id=tenant_id,
        )
        
        await self._broadcast_to_channel("tenants", message.payload)
        self._queue_message(message)
    
    async def broadcast_intel_message(
        self,
        channel_id: str,
        event_type: str,
        source_tenant_id: str,
        data: Dict[str, Any],
        target_tenants: List[str] = None,
    ) -> None:
        """Broadcast an intelligence message"""
        channel = f"intel/{channel_id}"
        
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=channel,
            event_type=event_type,
            payload={
                "event": event_type,
                "channel_id": channel_id,
                "source_tenant_id": source_tenant_id,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            },
            source_tenant_id=source_tenant_id,
            target_tenants=target_tenants or [],
        )
        
        if target_tenants:
            await self._broadcast_to_tenants(channel, message.payload, target_tenants)
        else:
            await self._broadcast_to_channel(channel, message.payload)
        
        self._queue_message(message)
    
    async def broadcast_jointops_event(
        self,
        room_id: str,
        event_type: str,
        source_tenant_id: str,
        data: Dict[str, Any],
    ) -> None:
        """Broadcast a joint operations event"""
        channel = f"jointops/{room_id}"
        
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel=channel,
            event_type=event_type,
            payload={
                "event": event_type,
                "room_id": room_id,
                "source_tenant_id": source_tenant_id,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            },
            source_tenant_id=source_tenant_id,
        )
        
        await self._broadcast_to_room(room_id, message.payload)
        self._queue_message(message)
    
    async def broadcast_analytics_update(
        self,
        event_type: str,
        data: Dict[str, Any],
        target_tenants: List[str] = None,
    ) -> None:
        """Broadcast an analytics update"""
        message = ChannelMessage(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            channel="analytics",
            event_type=event_type,
            payload={
                "event": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            },
            target_tenants=target_tenants or [],
        )
        
        if target_tenants:
            await self._broadcast_to_tenants("analytics", message.payload, target_tenants)
        else:
            await self._broadcast_to_channel("analytics", message.payload)
        
        self._queue_message(message)
    
    async def send_to_connection(
        self,
        connection_id: str,
        data: Dict[str, Any],
    ) -> bool:
        """Send a message to a specific connection"""
        if connection_id not in self._connections:
            return False
        
        connection = self._connections[connection_id]
        connection.last_activity = datetime.utcnow()
        
        await self._notify_subscribers(connection.channel, data, [connection_id])
        
        return True
    
    async def send_to_tenant(
        self,
        tenant_id: str,
        channel: str,
        data: Dict[str, Any],
    ) -> int:
        """Send a message to all connections for a tenant"""
        if tenant_id not in self._connections_by_tenant:
            return 0
        
        connection_ids = self._connections_by_tenant[tenant_id]
        
        channel_connections = self._connections_by_channel.get(channel, set())
        target_connections = connection_ids.intersection(channel_connections)
        
        await self._notify_subscribers(channel, data, list(target_connections))
        
        return len(target_connections)
    
    def get_connection_count(self, channel: str = None, tenant_id: str = None) -> int:
        """Get the number of active connections"""
        if channel:
            return len(self._connections_by_channel.get(channel, set()))
        if tenant_id:
            return len(self._connections_by_tenant.get(tenant_id, set()))
        return len(self._connections)
    
    def get_connections_in_room(self, room_id: str) -> List[WebSocketConnection]:
        """Get all connections in a room"""
        connection_ids = self._connections_by_room.get(room_id, set())
        return [self._connections[cid] for cid in connection_ids if cid in self._connections]
    
    def get_recent_messages(self, channel: str = None, limit: int = 100) -> List[ChannelMessage]:
        """Get recent messages"""
        if channel:
            messages = [m for m in self._message_queue if m.channel == channel]
        else:
            messages = self._message_queue
        return messages[-limit:]
    
    def subscribe(self, channel: str, callback: callable) -> None:
        """Subscribe to channel messages"""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)
    
    def unsubscribe(self, channel: str, callback: callable) -> bool:
        """Unsubscribe from channel messages"""
        if channel in self._subscribers and callback in self._subscribers[channel]:
            self._subscribers[channel].remove(callback)
            return True
        return False
    
    async def _broadcast_to_channel(self, channel: str, data: Dict[str, Any]) -> None:
        """Broadcast to all connections on a channel"""
        connection_ids = list(self._connections_by_channel.get(channel, set()))
        await self._notify_subscribers(channel, data, connection_ids)
    
    async def _broadcast_to_tenants(
        self,
        channel: str,
        data: Dict[str, Any],
        tenant_ids: List[str],
    ) -> None:
        """Broadcast to connections for specific tenants"""
        target_connections = set()
        
        for tenant_id in tenant_ids:
            tenant_connections = self._connections_by_tenant.get(tenant_id, set())
            channel_connections = self._connections_by_channel.get(channel, set())
            target_connections.update(tenant_connections.intersection(channel_connections))
        
        await self._notify_subscribers(channel, data, list(target_connections))
    
    async def _broadcast_to_room(self, room_id: str, data: Dict[str, Any]) -> None:
        """Broadcast to all connections in a room"""
        connection_ids = list(self._connections_by_room.get(room_id, set()))
        channel = f"jointops/{room_id}"
        await self._notify_subscribers(channel, data, connection_ids)
    
    async def _notify_subscribers(
        self,
        channel: str,
        data: Dict[str, Any],
        connection_ids: List[str],
    ) -> None:
        """Notify subscribers of a message"""
        if channel in self._subscribers:
            for callback in self._subscribers[channel]:
                try:
                    await callback(data, connection_ids)
                except Exception:
                    pass
    
    def _queue_message(self, message: ChannelMessage) -> None:
        """Queue a message for history"""
        self._message_queue.append(message)
        
        if len(self._message_queue) > self._max_queue_size:
            self._message_queue = self._message_queue[-self._max_queue_size:]


fusion_ws_manager = FusionCloudWebSocketManager()


async def handle_tenant_websocket(websocket: Any, tenant_id: str, user_id: str):
    """Handle WebSocket connection for tenant events"""
    connection_id = await fusion_ws_manager.connect(
        websocket=websocket,
        channel="tenants",
        tenant_id=tenant_id,
        user_id=user_id,
    )
    
    try:
        await websocket.send_json({
            "event": "connected",
            "connection_id": connection_id,
            "channel": "tenants",
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            elif data.get("type") == "subscribe":
                pass
            
    except Exception:
        pass
    finally:
        await fusion_ws_manager.disconnect(connection_id)


async def handle_intel_websocket(
    websocket: Any,
    channel_id: str,
    tenant_id: str,
    user_id: str,
):
    """Handle WebSocket connection for intelligence channel"""
    channel = f"intel/{channel_id}"
    
    connection_id = await fusion_ws_manager.connect(
        websocket=websocket,
        channel=channel,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    
    try:
        await websocket.send_json({
            "event": "connected",
            "connection_id": connection_id,
            "channel": channel,
            "channel_id": channel_id,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            elif data.get("type") == "message":
                await fusion_ws_manager.broadcast_intel_message(
                    channel_id=channel_id,
                    event_type="new_message",
                    source_tenant_id=tenant_id,
                    data=data.get("payload", {}),
                )
            elif data.get("type") == "acknowledge":
                await fusion_ws_manager.broadcast_intel_message(
                    channel_id=channel_id,
                    event_type="message_acknowledged",
                    source_tenant_id=tenant_id,
                    data={"message_id": data.get("message_id")},
                )
            
    except Exception:
        pass
    finally:
        await fusion_ws_manager.disconnect(connection_id)


async def handle_jointops_websocket(
    websocket: Any,
    room_id: str,
    tenant_id: str,
    user_id: str,
):
    """Handle WebSocket connection for joint operations room"""
    channel = f"jointops/{room_id}"
    
    connection_id = await fusion_ws_manager.connect(
        websocket=websocket,
        channel=channel,
        tenant_id=tenant_id,
        user_id=user_id,
        room_id=room_id,
    )
    
    try:
        await websocket.send_json({
            "event": "connected",
            "connection_id": connection_id,
            "channel": channel,
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        participants = fusion_ws_manager.get_connections_in_room(room_id)
        await websocket.send_json({
            "event": "room_state",
            "participants": [
                {"tenant_id": p.tenant_id, "user_id": p.user_id}
                for p in participants
            ],
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            elif data.get("type") == "timeline_event":
                await fusion_ws_manager.broadcast_jointops_event(
                    room_id=room_id,
                    event_type="timeline_event",
                    source_tenant_id=tenant_id,
                    data=data.get("payload", {}),
                )
            elif data.get("type") == "unit_position":
                await fusion_ws_manager.broadcast_jointops_event(
                    room_id=room_id,
                    event_type="unit_position_update",
                    source_tenant_id=tenant_id,
                    data=data.get("payload", {}),
                )
            elif data.get("type") == "whiteboard_update":
                await fusion_ws_manager.broadcast_jointops_event(
                    room_id=room_id,
                    event_type="whiteboard_update",
                    source_tenant_id=tenant_id,
                    data=data.get("payload", {}),
                )
            elif data.get("type") == "chat":
                await fusion_ws_manager.broadcast_jointops_event(
                    room_id=room_id,
                    event_type="chat_message",
                    source_tenant_id=tenant_id,
                    data={
                        "user_id": user_id,
                        "message": data.get("message", ""),
                    },
                )
            
    except Exception:
        pass
    finally:
        await fusion_ws_manager.disconnect(connection_id)


async def handle_analytics_websocket(
    websocket: Any,
    tenant_id: str,
    user_id: str,
):
    """Handle WebSocket connection for analytics updates"""
    connection_id = await fusion_ws_manager.connect(
        websocket=websocket,
        channel="analytics",
        tenant_id=tenant_id,
        user_id=user_id,
    )
    
    try:
        await websocket.send_json({
            "event": "connected",
            "connection_id": connection_id,
            "channel": "analytics",
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
            elif data.get("type") == "subscribe_heatmap":
                pass
            elif data.get("type") == "subscribe_cluster":
                pass
            elif data.get("type") == "subscribe_riskmap":
                pass
            
    except Exception:
        pass
    finally:
        await fusion_ws_manager.disconnect(connection_id)
