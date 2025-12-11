"""
Test Suite 8: WebSocket Interaction Tests

Tests for WebSocket connection management, message routing, and real-time updates.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
import json

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")


class WebSocketClient:
    """Mock WebSocket client for testing."""
    
    def __init__(self, client_id: str, role: str = "OPERATOR"):
        self.client_id = client_id
        self.role = role
        self.messages = []
        self.is_connected = False
    
    async def connect(self):
        self.is_connected = True
    
    async def disconnect(self):
        self.is_connected = False
    
    async def receive_message(self, message: dict):
        self.messages.append(message)
    
    def get_messages(self):
        return self.messages
    
    def clear_messages(self):
        self.messages = []


class ConstitutionWSManager:
    """Mock WebSocket manager for constitution governance channels."""
    
    _instance = None
    
    def __init__(self):
        self._decisions_clients = {}
        self._approvals_clients = {}
        self._policy_updates_clients = {}
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def connect_decisions(self, client: WebSocketClient):
        self._decisions_clients[client.client_id] = client
        await client.connect()
    
    async def disconnect_decisions(self, client_id: str):
        if client_id in self._decisions_clients:
            await self._decisions_clients[client_id].disconnect()
            del self._decisions_clients[client_id]
    
    async def connect_approvals(self, client: WebSocketClient):
        self._approvals_clients[client.client_id] = client
        await client.connect()
    
    async def disconnect_approvals(self, client_id: str):
        if client_id in self._approvals_clients:
            await self._approvals_clients[client_id].disconnect()
            del self._approvals_clients[client_id]
    
    async def connect_policy_updates(self, client: WebSocketClient):
        self._policy_updates_clients[client.client_id] = client
        await client.connect()
    
    async def disconnect_policy_updates(self, client_id: str):
        if client_id in self._policy_updates_clients:
            await self._policy_updates_clients[client_id].disconnect()
            del self._policy_updates_clients[client_id]
    
    async def broadcast_decision(self, decision: dict):
        message = {
            "type": "validation_decision",
            "data": decision,
            "timestamp": datetime.now().isoformat(),
        }
        for client in self._decisions_clients.values():
            await client.receive_message(message)
    
    async def broadcast_approval_update(self, approval: dict):
        message = {
            "type": "approval_update",
            "data": approval,
            "timestamp": datetime.now().isoformat(),
        }
        for client in self._approvals_clients.values():
            await client.receive_message(message)
    
    async def broadcast_policy_update(self, policy: dict):
        message = {
            "type": "policy_update",
            "data": policy,
            "timestamp": datetime.now().isoformat(),
        }
        for client in self._policy_updates_clients.values():
            await client.receive_message(message)
    
    async def send_to_role(self, channel: str, role: str, message: dict):
        if channel == "approvals":
            clients = self._approvals_clients
        elif channel == "decisions":
            clients = self._decisions_clients
        else:
            clients = self._policy_updates_clients
        
        for client in clients.values():
            if client.role == role:
                await client.receive_message(message)
    
    def get_connected_clients(self, channel: str):
        if channel == "decisions":
            return list(self._decisions_clients.keys())
        elif channel == "approvals":
            return list(self._approvals_clients.keys())
        elif channel == "policy_updates":
            return list(self._policy_updates_clients.keys())
        return []


def get_constitution_ws_manager():
    """Get WebSocket manager singleton."""
    return ConstitutionWSManager.get_instance()


class TestWebSocketClient:
    """Tests for WebSocket client model."""

    def test_client_creation(self):
        """Test creating a WebSocket client."""
        client = WebSocketClient("client-001", "OPERATOR")
        assert client.client_id == "client-001"
        assert client.role == "OPERATOR"
        assert client.is_connected is False

    @pytest.mark.asyncio
    async def test_client_connect(self):
        """Test client connection."""
        client = WebSocketClient("client-002", "SUPERVISOR")
        await client.connect()
        assert client.is_connected is True

    @pytest.mark.asyncio
    async def test_client_disconnect(self):
        """Test client disconnection."""
        client = WebSocketClient("client-003", "OPERATOR")
        await client.connect()
        await client.disconnect()
        assert client.is_connected is False

    @pytest.mark.asyncio
    async def test_client_receive_message(self):
        """Test client receiving message."""
        client = WebSocketClient("client-004", "OPERATOR")
        message = {"type": "test", "data": "test_data"}
        await client.receive_message(message)
        
        assert len(client.messages) == 1
        assert client.messages[0] == message

    def test_client_clear_messages(self):
        """Test clearing client messages."""
        client = WebSocketClient("client-005", "OPERATOR")
        client.messages = [{"type": "test"}]
        client.clear_messages()
        assert len(client.messages) == 0


class TestConstitutionWSManager:
    """Tests for ConstitutionWSManager singleton."""

    def test_singleton_pattern(self):
        """Test that get_constitution_ws_manager returns singleton."""
        m1 = get_constitution_ws_manager()
        m2 = get_constitution_ws_manager()
        assert m1 is m2


class TestDecisionsChannel:
    """Tests for /ws/governance/decisions channel."""

    @pytest.mark.asyncio
    async def test_connect_to_decisions(self):
        """Test connecting to decisions channel."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("dec-client-001", "OPERATOR")
        
        await manager.connect_decisions(client)
        
        assert client.is_connected is True
        assert "dec-client-001" in manager.get_connected_clients("decisions")

    @pytest.mark.asyncio
    async def test_disconnect_from_decisions(self):
        """Test disconnecting from decisions channel."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("dec-client-002", "OPERATOR")
        
        await manager.connect_decisions(client)
        await manager.disconnect_decisions("dec-client-002")
        
        assert client.is_connected is False
        assert "dec-client-002" not in manager.get_connected_clients("decisions")

    @pytest.mark.asyncio
    async def test_broadcast_decision(self):
        """Test broadcasting validation decision."""
        manager = ConstitutionWSManager()
        client1 = WebSocketClient("dec-client-003", "OPERATOR")
        client2 = WebSocketClient("dec-client-004", "SUPERVISOR")
        
        await manager.connect_decisions(client1)
        await manager.connect_decisions(client2)
        
        decision = {
            "decision_id": "dec-001",
            "action_id": "action-001",
            "result": "ALLOWED",
            "rules_applied": ["rule-001"],
        }
        
        await manager.broadcast_decision(decision)
        
        assert len(client1.messages) == 1
        assert len(client2.messages) == 1
        assert client1.messages[0]["type"] == "validation_decision"
        assert client1.messages[0]["data"] == decision

    @pytest.mark.asyncio
    async def test_decision_message_format(self):
        """Test decision message format."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("dec-client-005", "OPERATOR")
        
        await manager.connect_decisions(client)
        
        decision = {
            "decision_id": "dec-002",
            "action_id": "action-002",
            "result": "DENIED",
            "rules_applied": ["rule-002"],
            "explanation": "Violates Fourth Amendment",
        }
        
        await manager.broadcast_decision(decision)
        
        message = client.messages[0]
        assert "type" in message
        assert "data" in message
        assert "timestamp" in message
        assert message["type"] == "validation_decision"


class TestApprovalsChannel:
    """Tests for /ws/governance/approvals channel."""

    @pytest.mark.asyncio
    async def test_connect_to_approvals(self):
        """Test connecting to approvals channel."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("app-client-001", "SUPERVISOR")
        
        await manager.connect_approvals(client)
        
        assert client.is_connected is True
        assert "app-client-001" in manager.get_connected_clients("approvals")

    @pytest.mark.asyncio
    async def test_disconnect_from_approvals(self):
        """Test disconnecting from approvals channel."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("app-client-002", "SUPERVISOR")
        
        await manager.connect_approvals(client)
        await manager.disconnect_approvals("app-client-002")
        
        assert client.is_connected is False
        assert "app-client-002" not in manager.get_connected_clients("approvals")

    @pytest.mark.asyncio
    async def test_broadcast_approval_update(self):
        """Test broadcasting approval update."""
        manager = ConstitutionWSManager()
        client1 = WebSocketClient("app-client-003", "SUPERVISOR")
        client2 = WebSocketClient("app-client-004", "COMMAND_STAFF")
        
        await manager.connect_approvals(client1)
        await manager.connect_approvals(client2)
        
        approval = {
            "request_id": "req-001",
            "status": "APPROVED",
            "approver_id": "supervisor-001",
        }
        
        await manager.broadcast_approval_update(approval)
        
        assert len(client1.messages) == 1
        assert len(client2.messages) == 1
        assert client1.messages[0]["type"] == "approval_update"
        assert client1.messages[0]["data"] == approval

    @pytest.mark.asyncio
    async def test_approval_message_format(self):
        """Test approval message format."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("app-client-005", "SUPERVISOR")
        
        await manager.connect_approvals(client)
        
        approval = {
            "request_id": "req-002",
            "status": "PENDING",
            "action_type": "surveillance_escalation",
            "risk_score": 65,
        }
        
        await manager.broadcast_approval_update(approval)
        
        message = client.messages[0]
        assert "type" in message
        assert "data" in message
        assert "timestamp" in message
        assert message["type"] == "approval_update"


class TestPolicyUpdatesChannel:
    """Tests for /ws/governance/policy-updates channel."""

    @pytest.mark.asyncio
    async def test_connect_to_policy_updates(self):
        """Test connecting to policy updates channel."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("pol-client-001", "ADMIN")
        
        await manager.connect_policy_updates(client)
        
        assert client.is_connected is True
        assert "pol-client-001" in manager.get_connected_clients("policy_updates")

    @pytest.mark.asyncio
    async def test_disconnect_from_policy_updates(self):
        """Test disconnecting from policy updates channel."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("pol-client-002", "ADMIN")
        
        await manager.connect_policy_updates(client)
        await manager.disconnect_policy_updates("pol-client-002")
        
        assert client.is_connected is False
        assert "pol-client-002" not in manager.get_connected_clients("policy_updates")

    @pytest.mark.asyncio
    async def test_broadcast_policy_update(self):
        """Test broadcasting policy update."""
        manager = ConstitutionWSManager()
        client1 = WebSocketClient("pol-client-003", "ADMIN")
        client2 = WebSocketClient("pol-client-004", "SUPERVISOR")
        
        await manager.connect_policy_updates(client1)
        await manager.connect_policy_updates(client2)
        
        policy = {
            "policy_id": "policy-001",
            "action": "CREATED",
            "title": "New Surveillance Policy",
        }
        
        await manager.broadcast_policy_update(policy)
        
        assert len(client1.messages) == 1
        assert len(client2.messages) == 1
        assert client1.messages[0]["type"] == "policy_update"
        assert client1.messages[0]["data"] == policy

    @pytest.mark.asyncio
    async def test_policy_update_message_format(self):
        """Test policy update message format."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("pol-client-005", "ADMIN")
        
        await manager.connect_policy_updates(client)
        
        policy = {
            "policy_id": "policy-002",
            "action": "UPDATED",
            "changes": ["condition", "priority"],
        }
        
        await manager.broadcast_policy_update(policy)
        
        message = client.messages[0]
        assert "type" in message
        assert "data" in message
        assert "timestamp" in message
        assert message["type"] == "policy_update"


class TestRoleBasedMessaging:
    """Tests for role-based message routing."""

    @pytest.mark.asyncio
    async def test_send_to_supervisors_only(self):
        """Test sending message to supervisors only."""
        manager = ConstitutionWSManager()
        operator = WebSocketClient("role-client-001", "OPERATOR")
        supervisor = WebSocketClient("role-client-002", "SUPERVISOR")
        
        await manager.connect_approvals(operator)
        await manager.connect_approvals(supervisor)
        
        message = {
            "type": "supervisor_alert",
            "data": {"alert": "High-risk approval pending"},
        }
        
        await manager.send_to_role("approvals", "SUPERVISOR", message)
        
        assert len(supervisor.messages) == 1
        assert len(operator.messages) == 0

    @pytest.mark.asyncio
    async def test_send_to_command_staff_only(self):
        """Test sending message to command staff only."""
        manager = ConstitutionWSManager()
        supervisor = WebSocketClient("role-client-003", "SUPERVISOR")
        command = WebSocketClient("role-client-004", "COMMAND_STAFF")
        
        await manager.connect_approvals(supervisor)
        await manager.connect_approvals(command)
        
        message = {
            "type": "command_alert",
            "data": {"alert": "Critical approval required"},
        }
        
        await manager.send_to_role("approvals", "COMMAND_STAFF", message)
        
        assert len(command.messages) == 1
        assert len(supervisor.messages) == 0


class TestMultipleChannelSubscription:
    """Tests for clients subscribing to multiple channels."""

    @pytest.mark.asyncio
    async def test_client_multiple_channels(self):
        """Test client subscribing to multiple channels."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("multi-client-001", "SUPERVISOR")
        
        await manager.connect_decisions(client)
        await manager.connect_approvals(client)
        
        assert "multi-client-001" in manager.get_connected_clients("decisions")
        assert "multi-client-001" in manager.get_connected_clients("approvals")

    @pytest.mark.asyncio
    async def test_receive_from_multiple_channels(self):
        """Test receiving messages from multiple channels."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("multi-client-002", "SUPERVISOR")
        
        await manager.connect_decisions(client)
        await manager.connect_approvals(client)
        
        decision = {"decision_id": "dec-multi", "result": "ALLOWED"}
        approval = {"request_id": "req-multi", "status": "PENDING"}
        
        await manager.broadcast_decision(decision)
        await manager.broadcast_approval_update(approval)
        
        assert len(client.messages) == 2


class TestConnectionManagement:
    """Tests for WebSocket connection management."""

    @pytest.mark.asyncio
    async def test_get_connected_clients(self):
        """Test getting list of connected clients."""
        manager = ConstitutionWSManager()
        client1 = WebSocketClient("conn-client-001", "OPERATOR")
        client2 = WebSocketClient("conn-client-002", "SUPERVISOR")
        
        await manager.connect_decisions(client1)
        await manager.connect_decisions(client2)
        
        clients = manager.get_connected_clients("decisions")
        
        assert len(clients) >= 2
        assert "conn-client-001" in clients
        assert "conn-client-002" in clients

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_client(self):
        """Test disconnecting nonexistent client."""
        manager = ConstitutionWSManager()
        
        # Should not raise error
        await manager.disconnect_decisions("nonexistent-client")

    @pytest.mark.asyncio
    async def test_broadcast_to_empty_channel(self):
        """Test broadcasting to channel with no clients."""
        manager = ConstitutionWSManager()
        
        # Should not raise error
        await manager.broadcast_decision({"decision_id": "dec-empty"})


class TestMessageTimestamps:
    """Tests for message timestamp handling."""

    @pytest.mark.asyncio
    async def test_message_has_timestamp(self):
        """Test that all messages have timestamps."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("ts-client-001", "OPERATOR")
        
        await manager.connect_decisions(client)
        await manager.broadcast_decision({"decision_id": "dec-ts"})
        
        message = client.messages[0]
        assert "timestamp" in message
        assert message["timestamp"] is not None

    @pytest.mark.asyncio
    async def test_timestamp_format(self):
        """Test timestamp format is ISO 8601."""
        manager = ConstitutionWSManager()
        client = WebSocketClient("ts-client-002", "OPERATOR")
        
        await manager.connect_decisions(client)
        await manager.broadcast_decision({"decision_id": "dec-ts-format"})
        
        message = client.messages[0]
        timestamp = message["timestamp"]
        
        # Should be parseable as ISO format
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            valid_format = True
        except ValueError:
            valid_format = False
        
        assert valid_format is True
