"""
Persona WebSocket Channels

WebSocket channels for real-time AI Persona interactions:
- /ws/personas/{persona_id}/chat - Real-time chat with persona
- /ws/personas/alerts - System-wide persona alerts
- /ws/personas/reasoning - Mission reasoning updates
- /ws/personas/missions - Mission status updates
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field

from backend.app.personas.persona_engine import (
    PersonaEngine,
    PersonaType,
    PersonaStatus,
)
from backend.app.personas.interaction_engine import (
    InteractionEngine,
    InteractionType,
)
from backend.app.personas.mission_reasoner import (
    MissionReasoner,
    MissionStatus,
)
from backend.app.personas.compliance_layer import (
    ComplianceIntegrationLayer,
)


@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection."""
    connection_id: str
    channel: str
    user_id: str
    persona_id: Optional[str] = None
    session_id: Optional[str] = None
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    message_id: str
    channel: str
    message_type: str
    payload: Dict[str, Any]
    sender: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "channel": self.channel,
            "message_type": self.message_type,
            "payload": self.payload,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class PersonaWSManager:
    """
    WebSocket Manager for AI Personas.
    
    Manages connections and broadcasts for:
    - Chat channels (per persona)
    - Alert channels
    - Reasoning channels
    - Mission channels
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.persona_engine = PersonaEngine()
        self.interaction_engine = InteractionEngine()
        self.mission_reasoner = MissionReasoner()
        self.compliance_layer = ComplianceIntegrationLayer()
        
        self.connections: Dict[str, WebSocketConnection] = {}
        self.chat_channels: Dict[str, Set[str]] = {}
        self.alert_subscribers: Set[str] = set()
        self.reasoning_subscribers: Set[str] = set()
        self.mission_subscribers: Set[str] = set()
        
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: Dict[str, List[WebSocketMessage]] = {}
        
        self._initialized = True
    
    async def connect_chat(
        self,
        connection_id: str,
        persona_id: str,
        user_id: str,
        websocket: Any,
    ) -> WebSocketConnection:
        """Connect to a persona chat channel."""
        persona = self.persona_engine.get_persona(persona_id)
        if not persona:
            raise ValueError(f"Persona not found: {persona_id}")
        
        session = self.interaction_engine.create_session(
            persona_id=persona_id,
            user_id=user_id,
            interaction_type=InteractionType.WEBSOCKET,
        )
        
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel=f"chat:{persona_id}",
            user_id=user_id,
            persona_id=persona_id,
            session_id=session.session_id,
            metadata={"websocket": websocket},
        )
        
        self.connections[connection_id] = connection
        
        if persona_id not in self.chat_channels:
            self.chat_channels[persona_id] = set()
        self.chat_channels[persona_id].add(connection_id)
        
        await self._send_welcome_message(connection, persona)
        
        return connection
    
    async def connect_alerts(
        self,
        connection_id: str,
        user_id: str,
        websocket: Any,
    ) -> WebSocketConnection:
        """Connect to alerts channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel="alerts",
            user_id=user_id,
            metadata={"websocket": websocket},
        )
        
        self.connections[connection_id] = connection
        self.alert_subscribers.add(connection_id)
        
        return connection
    
    async def connect_reasoning(
        self,
        connection_id: str,
        user_id: str,
        websocket: Any,
    ) -> WebSocketConnection:
        """Connect to reasoning channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel="reasoning",
            user_id=user_id,
            metadata={"websocket": websocket},
        )
        
        self.connections[connection_id] = connection
        self.reasoning_subscribers.add(connection_id)
        
        return connection
    
    async def connect_missions(
        self,
        connection_id: str,
        user_id: str,
        websocket: Any,
    ) -> WebSocketConnection:
        """Connect to missions channel."""
        connection = WebSocketConnection(
            connection_id=connection_id,
            channel="missions",
            user_id=user_id,
            metadata={"websocket": websocket},
        )
        
        self.connections[connection_id] = connection
        self.mission_subscribers.add(connection_id)
        
        return connection
    
    async def disconnect(self, connection_id: str) -> None:
        """Disconnect a WebSocket connection."""
        connection = self.connections.get(connection_id)
        if not connection:
            return
        
        if connection.session_id:
            self.interaction_engine.end_session(connection.session_id)
        
        if connection.persona_id and connection.persona_id in self.chat_channels:
            self.chat_channels[connection.persona_id].discard(connection_id)
        
        self.alert_subscribers.discard(connection_id)
        self.reasoning_subscribers.discard(connection_id)
        self.mission_subscribers.discard(connection_id)
        
        del self.connections[connection_id]
    
    async def handle_chat_message(
        self,
        connection_id: str,
        message: str,
    ) -> WebSocketMessage:
        """Handle incoming chat message."""
        connection = self.connections.get(connection_id)
        if not connection or not connection.session_id:
            raise ValueError(f"Invalid connection: {connection_id}")
        
        response = self.interaction_engine.process_input(
            connection.session_id,
            message,
        )
        
        ws_message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            channel=connection.channel,
            message_type="chat_response",
            payload={
                "response_id": response.response_id,
                "content": response.content,
                "emotional_tone": response.emotional_tone.value,
                "confidence": response.confidence,
                "action_items": response.action_items,
                "follow_up_questions": response.follow_up_questions,
                "escalation_required": response.escalation_required,
                "escalation_reason": response.escalation_reason,
                "response_time_ms": response.response_time_ms,
            },
            sender=connection.persona_id or "system",
        )
        
        await self._send_to_connection(connection_id, ws_message)
        
        if response.escalation_required:
            await self.broadcast_alert({
                "alert_type": "escalation_required",
                "persona_id": connection.persona_id,
                "session_id": connection.session_id,
                "reason": response.escalation_reason,
            })
        
        return ws_message
    
    async def _send_welcome_message(
        self,
        connection: WebSocketConnection,
        persona: Any,
    ) -> None:
        """Send welcome message to new chat connection."""
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            channel=connection.channel,
            message_type="welcome",
            payload={
                "persona_id": persona.persona_id,
                "persona_name": persona.name,
                "persona_type": persona.persona_type.value,
                "role": persona.role.value,
                "status": persona.status.value,
                "emotional_state": persona.emotional_state.value,
                "session_id": connection.session_id,
                "message": f"Connected to {persona.name}. How can I assist you?",
            },
            sender=persona.persona_id,
        )
        
        await self._send_to_connection(connection.connection_id, message)
    
    async def _send_to_connection(
        self,
        connection_id: str,
        message: WebSocketMessage,
    ) -> bool:
        """Send message to a specific connection."""
        connection = self.connections.get(connection_id)
        if not connection:
            return False
        
        websocket = connection.metadata.get("websocket")
        if websocket:
            try:
                await websocket.send_text(message.to_json())
                connection.last_activity = datetime.utcnow()
                return True
            except Exception:
                await self.disconnect(connection_id)
                return False
        
        return False
    
    async def broadcast_to_chat(
        self,
        persona_id: str,
        message_type: str,
        payload: Dict[str, Any],
    ) -> int:
        """Broadcast message to all connections in a chat channel."""
        connections = self.chat_channels.get(persona_id, set())
        sent_count = 0
        
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            channel=f"chat:{persona_id}",
            message_type=message_type,
            payload=payload,
            sender=persona_id,
        )
        
        for connection_id in list(connections):
            if await self._send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]) -> int:
        """Broadcast alert to all alert subscribers."""
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            channel="alerts",
            message_type="alert",
            payload=alert_data,
            sender="system",
        )
        
        sent_count = 0
        for connection_id in list(self.alert_subscribers):
            if await self._send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_reasoning_update(
        self,
        mission_id: str,
        reasoning_data: Dict[str, Any],
    ) -> int:
        """Broadcast reasoning update to subscribers."""
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            channel="reasoning",
            message_type="reasoning_update",
            payload={
                "mission_id": mission_id,
                **reasoning_data,
            },
            sender="system",
        )
        
        sent_count = 0
        for connection_id in list(self.reasoning_subscribers):
            if await self._send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_mission_update(
        self,
        mission_id: str,
        update_type: str,
        mission_data: Dict[str, Any],
    ) -> int:
        """Broadcast mission update to subscribers."""
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            channel="missions",
            message_type=update_type,
            payload={
                "mission_id": mission_id,
                **mission_data,
            },
            sender="system",
        )
        
        sent_count = 0
        for connection_id in list(self.mission_subscribers):
            if await self._send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_persona_status_change(
        self,
        persona_id: str,
        old_status: str,
        new_status: str,
    ) -> int:
        """Broadcast persona status change."""
        return await self.broadcast_alert({
            "alert_type": "persona_status_change",
            "persona_id": persona_id,
            "old_status": old_status,
            "new_status": new_status,
        })
    
    async def broadcast_compliance_violation(
        self,
        violation_data: Dict[str, Any],
    ) -> int:
        """Broadcast compliance violation alert."""
        return await self.broadcast_alert({
            "alert_type": "compliance_violation",
            **violation_data,
        })
    
    async def broadcast_mission_created(
        self,
        mission_id: str,
        mission_data: Dict[str, Any],
    ) -> int:
        """Broadcast mission created event."""
        return await self.broadcast_mission_update(
            mission_id,
            "mission_created",
            mission_data,
        )
    
    async def broadcast_mission_started(
        self,
        mission_id: str,
        mission_data: Dict[str, Any],
    ) -> int:
        """Broadcast mission started event."""
        return await self.broadcast_mission_update(
            mission_id,
            "mission_started",
            mission_data,
        )
    
    async def broadcast_mission_completed(
        self,
        mission_id: str,
        mission_data: Dict[str, Any],
    ) -> int:
        """Broadcast mission completed event."""
        return await self.broadcast_mission_update(
            mission_id,
            "mission_completed",
            mission_data,
        )
    
    async def broadcast_task_update(
        self,
        mission_id: str,
        task_id: str,
        task_data: Dict[str, Any],
    ) -> int:
        """Broadcast task update event."""
        return await self.broadcast_mission_update(
            mission_id,
            "task_update",
            {
                "task_id": task_id,
                **task_data,
            },
        )
    
    async def broadcast_approval_request(
        self,
        request_data: Dict[str, Any],
    ) -> int:
        """Broadcast approval request alert."""
        return await self.broadcast_alert({
            "alert_type": "approval_request",
            **request_data,
        })
    
    async def broadcast_approval_response(
        self,
        request_id: str,
        status: str,
        response_data: Dict[str, Any],
    ) -> int:
        """Broadcast approval response."""
        return await self.broadcast_alert({
            "alert_type": "approval_response",
            "request_id": request_id,
            "status": status,
            **response_data,
        })
    
    def get_connection_count(self) -> Dict[str, int]:
        """Get connection counts by channel."""
        chat_count = sum(len(conns) for conns in self.chat_channels.values())
        
        return {
            "total": len(self.connections),
            "chat": chat_count,
            "alerts": len(self.alert_subscribers),
            "reasoning": len(self.reasoning_subscribers),
            "missions": len(self.mission_subscribers),
        }
    
    def get_active_chat_personas(self) -> List[str]:
        """Get list of personas with active chat connections."""
        return [
            persona_id
            for persona_id, connections in self.chat_channels.items()
            if len(connections) > 0
        ]
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a connection."""
        connection = self.connections.get(connection_id)
        if not connection:
            return None
        
        return {
            "connection_id": connection.connection_id,
            "channel": connection.channel,
            "user_id": connection.user_id,
            "persona_id": connection.persona_id,
            "session_id": connection.session_id,
            "connected_at": connection.connected_at.isoformat(),
            "last_activity": connection.last_activity.isoformat(),
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        return {
            "connections": self.get_connection_count(),
            "active_chat_personas": self.get_active_chat_personas(),
            "total_chat_channels": len(self.chat_channels),
        }


persona_ws_manager = PersonaWSManager()
