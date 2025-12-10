"""
Phase 23: City Governance WebSocket Channels

Real-time WebSocket channels for governance decisions, optimizations,
KPIs, and scenario playback.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client."""
    client_id: str
    channel: str
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_message: Optional[datetime] = None
    subscriptions: list[str] = field(default_factory=list)


class GovernanceWebSocketManager:
    """
    WebSocket manager for city governance real-time updates.
    
    Channels:
    - /ws/governance/decisions - Live recommendation updates
    - /ws/governance/optimizations - Real-time optimization recalculation
    - /ws/governance/kpi - KPI metric updates
    - /ws/governance/scenario/{scenario_id} - Scenario playback streams
    """

    def __init__(self):
        self._clients: dict[str, list[Any]] = {
            "decisions": [],
            "optimizations": [],
            "kpi": [],
        }
        self._scenario_clients: dict[str, list[Any]] = {}
        self._client_info: dict[str, WebSocketClient] = {}
        self._message_queue: list[dict[str, Any]] = []
        self._running = False
        self._broadcast_interval = 1.0

    async def connect(self, websocket: Any, channel: str, scenario_id: Optional[str] = None):
        """Connect a client to a channel."""
        client_id = f"client-{uuid.uuid4().hex[:12]}"

        if channel == "scenario" and scenario_id:
            if scenario_id not in self._scenario_clients:
                self._scenario_clients[scenario_id] = []
            self._scenario_clients[scenario_id].append(websocket)
            full_channel = f"scenario/{scenario_id}"
        else:
            if channel in self._clients:
                self._clients[channel].append(websocket)
            full_channel = channel

        self._client_info[client_id] = WebSocketClient(
            client_id=client_id,
            channel=full_channel,
        )

        await self._send_welcome(websocket, client_id, full_channel)
        return client_id

    async def disconnect(self, websocket: Any, channel: str, scenario_id: Optional[str] = None):
        """Disconnect a client from a channel."""
        if channel == "scenario" and scenario_id:
            if scenario_id in self._scenario_clients:
                if websocket in self._scenario_clients[scenario_id]:
                    self._scenario_clients[scenario_id].remove(websocket)
        else:
            if channel in self._clients:
                if websocket in self._clients[channel]:
                    self._clients[channel].remove(websocket)

        client_id = None
        for cid, info in self._client_info.items():
            if info.channel == channel or info.channel == f"scenario/{scenario_id}":
                client_id = cid
                break

        if client_id:
            del self._client_info[client_id]

    async def _send_welcome(self, websocket: Any, client_id: str, channel: str):
        """Send welcome message to newly connected client."""
        message = {
            "type": "welcome",
            "client_id": client_id,
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to governance {channel} channel",
        }
        await self._send_to_client(websocket, message)

    async def _send_to_client(self, websocket: Any, message: dict[str, Any]):
        """Send a message to a specific client."""
        try:
            if hasattr(websocket, "send_json"):
                await websocket.send_json(message)
            elif hasattr(websocket, "send"):
                await websocket.send(json.dumps(message))
        except Exception:
            pass

    async def broadcast_decision(self, decision: dict[str, Any]):
        """Broadcast a new decision to all connected clients."""
        message = {
            "type": "decision_update",
            "data": decision,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("decisions", message)

    async def broadcast_decision_status_change(
        self,
        decision_id: str,
        old_status: str,
        new_status: str,
        changed_by: Optional[str] = None,
    ):
        """Broadcast a decision status change."""
        message = {
            "type": "decision_status_change",
            "decision_id": decision_id,
            "old_status": old_status,
            "new_status": new_status,
            "changed_by": changed_by,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("decisions", message)

    async def broadcast_optimization_result(self, result: dict[str, Any]):
        """Broadcast an optimization result."""
        message = {
            "type": "optimization_result",
            "data": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("optimizations", message)

    async def broadcast_optimization_progress(
        self,
        optimization_id: str,
        progress: float,
        status: str,
    ):
        """Broadcast optimization progress."""
        message = {
            "type": "optimization_progress",
            "optimization_id": optimization_id,
            "progress": progress,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("optimizations", message)

    async def broadcast_resource_update(self, resource: dict[str, Any]):
        """Broadcast a resource update."""
        message = {
            "type": "resource_update",
            "data": resource,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("optimizations", message)

    async def broadcast_kpi_update(self, kpi: dict[str, Any]):
        """Broadcast a KPI update."""
        message = {
            "type": "kpi_update",
            "data": kpi,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("kpi", message)

    async def broadcast_city_health_update(self, health_index: dict[str, Any]):
        """Broadcast city health index update."""
        message = {
            "type": "city_health_update",
            "data": health_index,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("kpi", message)

    async def broadcast_department_score_update(self, department: str, score: dict[str, Any]):
        """Broadcast department score update."""
        message = {
            "type": "department_score_update",
            "department": department,
            "data": score,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("kpi", message)

    async def broadcast_budget_alert(self, alert: dict[str, Any]):
        """Broadcast budget alert."""
        message = {
            "type": "budget_alert",
            "data": alert,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_channel("kpi", message)

    async def broadcast_scenario_event(self, scenario_id: str, event: dict[str, Any]):
        """Broadcast a scenario timeline event."""
        message = {
            "type": "scenario_event",
            "scenario_id": scenario_id,
            "data": event,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_scenario(scenario_id, message)

    async def broadcast_scenario_progress(
        self,
        scenario_id: str,
        progress: float,
        current_time: str,
    ):
        """Broadcast scenario simulation progress."""
        message = {
            "type": "scenario_progress",
            "scenario_id": scenario_id,
            "progress": progress,
            "current_time": current_time,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_scenario(scenario_id, message)

    async def broadcast_scenario_metrics(self, scenario_id: str, metrics: dict[str, float]):
        """Broadcast scenario metrics snapshot."""
        message = {
            "type": "scenario_metrics",
            "scenario_id": scenario_id,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_scenario(scenario_id, message)

    async def broadcast_scenario_complete(self, scenario_id: str, result: dict[str, Any]):
        """Broadcast scenario completion."""
        message = {
            "type": "scenario_complete",
            "scenario_id": scenario_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_scenario(scenario_id, message)

    async def _broadcast_to_channel(self, channel: str, message: dict[str, Any]):
        """Broadcast message to all clients in a channel."""
        if channel not in self._clients:
            return

        disconnected = []
        for websocket in self._clients[channel]:
            try:
                await self._send_to_client(websocket, message)
            except Exception:
                disconnected.append(websocket)

        for ws in disconnected:
            self._clients[channel].remove(ws)

    async def _broadcast_to_scenario(self, scenario_id: str, message: dict[str, Any]):
        """Broadcast message to all clients watching a scenario."""
        if scenario_id not in self._scenario_clients:
            return

        disconnected = []
        for websocket in self._scenario_clients[scenario_id]:
            try:
                await self._send_to_client(websocket, message)
            except Exception:
                disconnected.append(websocket)

        for ws in disconnected:
            self._scenario_clients[scenario_id].remove(ws)

    async def start_scenario_playback(
        self,
        scenario_id: str,
        timeline: list[dict[str, Any]],
        playback_speed: float = 1.0,
    ):
        """Start scenario timeline playback."""
        if scenario_id not in self._scenario_clients:
            return

        total_events = len(timeline)
        for i, event in enumerate(timeline):
            progress = (i + 1) / total_events

            await self.broadcast_scenario_progress(
                scenario_id,
                progress,
                event.get("timestamp", datetime.utcnow().isoformat()),
            )

            await self.broadcast_scenario_event(scenario_id, event)

            if "metrics_snapshot" in event:
                await self.broadcast_scenario_metrics(
                    scenario_id,
                    event["metrics_snapshot"],
                )

            await asyncio.sleep(0.5 / playback_speed)

    def get_channel_stats(self) -> dict[str, Any]:
        """Get statistics for all channels."""
        return {
            "decisions": {
                "connected_clients": len(self._clients.get("decisions", [])),
            },
            "optimizations": {
                "connected_clients": len(self._clients.get("optimizations", [])),
            },
            "kpi": {
                "connected_clients": len(self._clients.get("kpi", [])),
            },
            "scenarios": {
                "active_scenarios": len(self._scenario_clients),
                "total_clients": sum(
                    len(clients) for clients in self._scenario_clients.values()
                ),
            },
            "total_clients": len(self._client_info),
        }

    def get_client_info(self, client_id: str) -> Optional[dict[str, Any]]:
        """Get information about a specific client."""
        client = self._client_info.get(client_id)
        if client:
            return {
                "client_id": client.client_id,
                "channel": client.channel,
                "connected_at": client.connected_at.isoformat(),
                "last_message": client.last_message.isoformat() if client.last_message else None,
                "subscriptions": client.subscriptions,
            }
        return None


_governance_ws_manager: Optional[GovernanceWebSocketManager] = None


def get_governance_ws_manager() -> GovernanceWebSocketManager:
    """Get the singleton WebSocket manager instance."""
    global _governance_ws_manager
    if _governance_ws_manager is None:
        _governance_ws_manager = GovernanceWebSocketManager()
    return _governance_ws_manager


async def handle_decisions_websocket(websocket: Any):
    """Handle WebSocket connection for decisions channel."""
    manager = get_governance_ws_manager()
    client_id = await manager.connect(websocket, "decisions")

    try:
        while True:
            try:
                if hasattr(websocket, "receive_json"):
                    data = await websocket.receive_json()
                elif hasattr(websocket, "recv"):
                    raw = await websocket.recv()
                    data = json.loads(raw)
                else:
                    await asyncio.sleep(1)
                    continue

                if data.get("type") == "ping":
                    await manager._send_to_client(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            except Exception:
                break
    finally:
        await manager.disconnect(websocket, "decisions")


async def handle_optimizations_websocket(websocket: Any):
    """Handle WebSocket connection for optimizations channel."""
    manager = get_governance_ws_manager()
    client_id = await manager.connect(websocket, "optimizations")

    try:
        while True:
            try:
                if hasattr(websocket, "receive_json"):
                    data = await websocket.receive_json()
                elif hasattr(websocket, "recv"):
                    raw = await websocket.recv()
                    data = json.loads(raw)
                else:
                    await asyncio.sleep(1)
                    continue

                if data.get("type") == "ping":
                    await manager._send_to_client(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "request_update":
                    from ..city_governance.resource_optimizer import get_resource_optimizer
                    optimizer = get_resource_optimizer()
                    stats = optimizer.get_statistics()
                    await manager._send_to_client(websocket, {
                        "type": "optimization_stats",
                        "data": stats,
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            except Exception:
                break
    finally:
        await manager.disconnect(websocket, "optimizations")


async def handle_kpi_websocket(websocket: Any):
    """Handle WebSocket connection for KPI channel."""
    manager = get_governance_ws_manager()
    client_id = await manager.connect(websocket, "kpi")

    try:
        while True:
            try:
                if hasattr(websocket, "receive_json"):
                    data = await websocket.receive_json()
                elif hasattr(websocket, "recv"):
                    raw = await websocket.recv()
                    data = json.loads(raw)
                else:
                    await asyncio.sleep(1)
                    continue

                if data.get("type") == "ping":
                    await manager._send_to_client(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "request_city_health":
                    from ..city_governance.kpi_engine import get_kpi_engine
                    engine = get_kpi_engine()
                    health = engine.get_city_health_index()
                    await manager._send_to_client(websocket, {
                        "type": "city_health_update",
                        "data": health.to_dict(),
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "request_kpis":
                    from ..city_governance.kpi_engine import get_kpi_engine
                    engine = get_kpi_engine()
                    kpis = engine.get_all_kpis()
                    await manager._send_to_client(websocket, {
                        "type": "kpi_batch_update",
                        "data": [k.to_dict() for k in kpis],
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            except Exception:
                break
    finally:
        await manager.disconnect(websocket, "kpi")


async def handle_scenario_websocket(websocket: Any, scenario_id: str):
    """Handle WebSocket connection for scenario playback channel."""
    manager = get_governance_ws_manager()
    client_id = await manager.connect(websocket, "scenario", scenario_id)

    try:
        while True:
            try:
                if hasattr(websocket, "receive_json"):
                    data = await websocket.receive_json()
                elif hasattr(websocket, "recv"):
                    raw = await websocket.recv()
                    data = json.loads(raw)
                else:
                    await asyncio.sleep(1)
                    continue

                if data.get("type") == "ping":
                    await manager._send_to_client(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif data.get("type") == "start_playback":
                    from ..city_governance.scenario_simulator import get_scenario_simulator
                    simulator = get_scenario_simulator()
                    result = simulator.get_result(data.get("result_id", ""))

                    if result:
                        most_likely = next(
                            (p for p in result.outcome_paths if p.name == "Most Likely"),
                            result.outcome_paths[0] if result.outcome_paths else None,
                        )
                        if most_likely:
                            timeline = [e.to_dict() for e in most_likely.timeline]
                            speed = data.get("speed", 1.0)
                            asyncio.create_task(
                                manager.start_scenario_playback(scenario_id, timeline, speed)
                            )

                elif data.get("type") == "get_scenario_info":
                    from ..city_governance.scenario_simulator import get_scenario_simulator
                    simulator = get_scenario_simulator()
                    scenario = simulator.get_scenario(scenario_id)

                    if scenario:
                        await manager._send_to_client(websocket, {
                            "type": "scenario_info",
                            "data": scenario.to_dict(),
                            "timestamp": datetime.utcnow().isoformat(),
                        })

            except Exception:
                break
    finally:
        await manager.disconnect(websocket, "scenario", scenario_id)
