"""
Phase 22: City Brain WebSocket Channels

WebSocket channels for real-time city brain updates:
- /ws/city/state - Unified city state updates
- /ws/city/weather - Weather condition updates
- /ws/city/traffic - Traffic condition updates
- /ws/city/digital-twin - Digital twin updates
- /ws/city/predictions - Prediction updates
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, Set
import asyncio
import json
import uuid


class CityBrainChannel(Enum):
    """City brain WebSocket channels."""
    STATE = "state"
    WEATHER = "weather"
    TRAFFIC = "traffic"
    DIGITAL_TWIN = "digital_twin"
    PREDICTIONS = "predictions"
    EVENTS = "events"
    ALERTS = "alerts"


class MessageType(Enum):
    """WebSocket message types."""
    STATE_UPDATE = "state_update"
    WEATHER_UPDATE = "weather_update"
    TRAFFIC_UPDATE = "traffic_update"
    INCIDENT_UPDATE = "incident_update"
    UTILITY_UPDATE = "utility_update"
    PREDICTION_UPDATE = "prediction_update"
    DIGITAL_TWIN_UPDATE = "digital_twin_update"
    OBJECT_POSITION_UPDATE = "object_position_update"
    OVERLAY_UPDATE = "overlay_update"
    EVENT_CREATED = "event_created"
    EVENT_UPDATED = "event_updated"
    EVENT_CLEARED = "event_cleared"
    ALERT = "alert"
    EMERGENCY = "emergency"
    SYSTEM_STATUS = "system_status"
    SUBSCRIPTION_CONFIRMED = "subscription_confirmed"
    ERROR = "error"


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    message_id: str
    message_type: MessageType
    channel: CityBrainChannel
    timestamp: datetime
    data: dict
    priority: int = 0
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps({
            "message_id": self.message_id,
            "type": self.message_type.value,
            "channel": self.channel.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "priority": self.priority,
        })


@dataclass
class Subscription:
    """Client subscription to a channel."""
    subscription_id: str
    client_id: str
    channel: CityBrainChannel
    filters: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class CityBrainWebSocketManager:
    """
    Manager for City Brain WebSocket connections.
    
    Handles:
    - Client connections and subscriptions
    - Channel-based message routing
    - Real-time updates for city state, weather, traffic, etc.
    - Digital twin object position updates
    - Event and alert broadcasting
    """
    
    def __init__(self):
        self._clients: dict[str, Any] = {}
        self._subscriptions: dict[str, list[Subscription]] = {
            channel.value: [] for channel in CityBrainChannel
        }
        self._message_handlers: dict[str, Callable] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._broadcast_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: Any, client_id: Optional[str] = None) -> str:
        """Register a new WebSocket connection."""
        if client_id is None:
            client_id = str(uuid.uuid4())
        
        self._clients[client_id] = websocket
        
        await self._send_to_client(
            client_id,
            WebSocketMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.SYSTEM_STATUS,
                channel=CityBrainChannel.STATE,
                timestamp=datetime.utcnow(),
                data={
                    "status": "connected",
                    "client_id": client_id,
                    "available_channels": [c.value for c in CityBrainChannel],
                },
            ),
        )
        
        return client_id
    
    async def disconnect(self, client_id: str) -> None:
        """Disconnect a client and remove all subscriptions."""
        if client_id in self._clients:
            del self._clients[client_id]
        
        for channel in self._subscriptions:
            self._subscriptions[channel] = [
                s for s in self._subscriptions[channel]
                if s.client_id != client_id
            ]
    
    async def subscribe(
        self,
        client_id: str,
        channel: CityBrainChannel,
        filters: Optional[dict] = None,
    ) -> Subscription:
        """Subscribe a client to a channel."""
        subscription = Subscription(
            subscription_id=str(uuid.uuid4()),
            client_id=client_id,
            channel=channel,
            filters=filters or {},
        )
        
        self._subscriptions[channel.value].append(subscription)
        
        await self._send_to_client(
            client_id,
            WebSocketMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.SUBSCRIPTION_CONFIRMED,
                channel=channel,
                timestamp=datetime.utcnow(),
                data={
                    "subscription_id": subscription.subscription_id,
                    "channel": channel.value,
                    "filters": filters or {},
                },
            ),
        )
        
        return subscription
    
    async def unsubscribe(self, client_id: str, channel: CityBrainChannel) -> bool:
        """Unsubscribe a client from a channel."""
        initial_count = len(self._subscriptions[channel.value])
        self._subscriptions[channel.value] = [
            s for s in self._subscriptions[channel.value]
            if s.client_id != client_id
        ]
        return len(self._subscriptions[channel.value]) < initial_count
    
    async def _send_to_client(self, client_id: str, message: WebSocketMessage) -> bool:
        """Send a message to a specific client."""
        if client_id not in self._clients:
            return False
        
        try:
            websocket = self._clients[client_id]
            await websocket.send_text(message.to_json())
            return True
        except Exception:
            await self.disconnect(client_id)
            return False
    
    async def broadcast_to_channel(
        self,
        channel: CityBrainChannel,
        message_type: MessageType,
        data: dict,
        priority: int = 0,
    ) -> int:
        """Broadcast a message to all subscribers of a channel."""
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            channel=channel,
            timestamp=datetime.utcnow(),
            data=data,
            priority=priority,
        )
        
        sent_count = 0
        for subscription in self._subscriptions[channel.value]:
            if await self._send_to_client(subscription.client_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_state_update(self, state_data: dict) -> int:
        """Broadcast city state update."""
        return await self.broadcast_to_channel(
            CityBrainChannel.STATE,
            MessageType.STATE_UPDATE,
            state_data,
        )
    
    async def broadcast_weather_update(self, weather_data: dict) -> int:
        """Broadcast weather update."""
        return await self.broadcast_to_channel(
            CityBrainChannel.WEATHER,
            MessageType.WEATHER_UPDATE,
            weather_data,
        )
    
    async def broadcast_traffic_update(self, traffic_data: dict) -> int:
        """Broadcast traffic update."""
        return await self.broadcast_to_channel(
            CityBrainChannel.TRAFFIC,
            MessageType.TRAFFIC_UPDATE,
            traffic_data,
        )
    
    async def broadcast_digital_twin_update(self, twin_data: dict) -> int:
        """Broadcast digital twin update."""
        return await self.broadcast_to_channel(
            CityBrainChannel.DIGITAL_TWIN,
            MessageType.DIGITAL_TWIN_UPDATE,
            twin_data,
        )
    
    async def broadcast_object_positions(self, objects: list[dict]) -> int:
        """Broadcast object position updates for digital twin."""
        return await self.broadcast_to_channel(
            CityBrainChannel.DIGITAL_TWIN,
            MessageType.OBJECT_POSITION_UPDATE,
            {"objects": objects},
        )
    
    async def broadcast_overlay_update(self, overlay_data: dict) -> int:
        """Broadcast overlay update for digital twin."""
        return await self.broadcast_to_channel(
            CityBrainChannel.DIGITAL_TWIN,
            MessageType.OVERLAY_UPDATE,
            overlay_data,
        )
    
    async def broadcast_prediction_update(self, prediction_data: dict) -> int:
        """Broadcast prediction update."""
        return await self.broadcast_to_channel(
            CityBrainChannel.PREDICTIONS,
            MessageType.PREDICTION_UPDATE,
            prediction_data,
        )
    
    async def broadcast_event(
        self,
        event_type: str,
        event_data: dict,
    ) -> int:
        """Broadcast city event."""
        message_type = {
            "created": MessageType.EVENT_CREATED,
            "updated": MessageType.EVENT_UPDATED,
            "cleared": MessageType.EVENT_CLEARED,
        }.get(event_type, MessageType.EVENT_CREATED)
        
        return await self.broadcast_to_channel(
            CityBrainChannel.EVENTS,
            message_type,
            event_data,
        )
    
    async def broadcast_alert(
        self,
        alert_data: dict,
        is_emergency: bool = False,
    ) -> int:
        """Broadcast alert or emergency."""
        message_type = MessageType.EMERGENCY if is_emergency else MessageType.ALERT
        priority = 10 if is_emergency else 5
        
        return await self.broadcast_to_channel(
            CityBrainChannel.ALERTS,
            message_type,
            alert_data,
            priority=priority,
        )
    
    async def handle_client_message(
        self,
        client_id: str,
        message: str,
    ) -> Optional[dict]:
        """Handle incoming message from client."""
        try:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "subscribe":
                channel_name = data.get("channel")
                filters = data.get("filters", {})
                
                try:
                    channel = CityBrainChannel(channel_name)
                    subscription = await self.subscribe(client_id, channel, filters)
                    return {
                        "status": "success",
                        "action": "subscribe",
                        "subscription_id": subscription.subscription_id,
                    }
                except ValueError:
                    return {
                        "status": "error",
                        "message": f"Invalid channel: {channel_name}",
                    }
            
            elif action == "unsubscribe":
                channel_name = data.get("channel")
                
                try:
                    channel = CityBrainChannel(channel_name)
                    success = await self.unsubscribe(client_id, channel)
                    return {
                        "status": "success" if success else "not_found",
                        "action": "unsubscribe",
                        "channel": channel_name,
                    }
                except ValueError:
                    return {
                        "status": "error",
                        "message": f"Invalid channel: {channel_name}",
                    }
            
            elif action == "ping":
                return {
                    "status": "success",
                    "action": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                }
        
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics."""
        return {
            "total_clients": len(self._clients),
            "subscriptions_by_channel": {
                channel: len(subs)
                for channel, subs in self._subscriptions.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_client_subscriptions(self, client_id: str) -> list[dict]:
        """Get all subscriptions for a client."""
        subscriptions = []
        for channel, subs in self._subscriptions.items():
            for sub in subs:
                if sub.client_id == client_id:
                    subscriptions.append({
                        "subscription_id": sub.subscription_id,
                        "channel": channel,
                        "filters": sub.filters,
                        "created_at": sub.created_at.isoformat(),
                    })
        return subscriptions


class CityBrainUpdateBroadcaster:
    """
    Automated broadcaster for city brain updates.
    
    Periodically fetches data and broadcasts to subscribers.
    """
    
    def __init__(
        self,
        ws_manager: CityBrainWebSocketManager,
        update_interval_seconds: int = 5,
    ):
        self._ws_manager = ws_manager
        self._update_interval = update_interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the broadcaster."""
        self._running = True
        self._task = asyncio.create_task(self._broadcast_loop())
    
    async def stop(self) -> None:
        """Stop the broadcaster."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _broadcast_loop(self) -> None:
        """Main broadcast loop."""
        while self._running:
            try:
                await self._broadcast_updates()
                await asyncio.sleep(self._update_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(self._update_interval)
    
    async def _broadcast_updates(self) -> None:
        """Broadcast all updates."""
        try:
            from backend.app.city_brain import get_city_brain
            from backend.app.city_brain.ingestion import DataIngestionManager
            from backend.app.city_brain.digital_twin import DigitalTwinManager
            from backend.app.city_brain.prediction import CityPredictionEngine
            
            city_brain = get_city_brain()
            state = city_brain.get_city_state()
            
            await self._ws_manager.broadcast_state_update({
                "timestamp": state.timestamp.isoformat(),
                "weather": state.weather,
                "traffic": state.traffic,
                "utilities": state.utilities,
                "incidents": state.incidents,
                "population_estimate": state.population_estimate,
                "overall_health": state.overall_health,
            })
            
        except Exception:
            pass


_ws_manager: Optional[CityBrainWebSocketManager] = None
_broadcaster: Optional[CityBrainUpdateBroadcaster] = None


def get_city_brain_ws_manager() -> CityBrainWebSocketManager:
    """Get the singleton WebSocket manager."""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = CityBrainWebSocketManager()
    return _ws_manager


async def get_city_brain_broadcaster() -> CityBrainUpdateBroadcaster:
    """Get the singleton broadcaster."""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = CityBrainUpdateBroadcaster(get_city_brain_ws_manager())
    return _broadcaster


__all__ = [
    "CityBrainWebSocketManager",
    "CityBrainUpdateBroadcaster",
    "CityBrainChannel",
    "MessageType",
    "WebSocketMessage",
    "Subscription",
    "get_city_brain_ws_manager",
    "get_city_brain_broadcaster",
]
