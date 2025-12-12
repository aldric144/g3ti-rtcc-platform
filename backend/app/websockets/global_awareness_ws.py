"""
Phase 32: Global Awareness WebSocket Channels

Real-time WebSocket channels for global situation awareness updates.

Channels:
- /ws/global-awareness/signals - Real-time global signals
- /ws/global-awareness/risk - Risk assessment updates
- /ws/global-awareness/events - Event correlation updates
- /ws/global-awareness/satellite - Satellite detection alerts
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import WebSocket, WebSocketDisconnect


class GlobalAwarenessWSManager:
    """WebSocket connection manager for Global Awareness channels."""

    def __init__(self):
        self.active_connections: dict[str, dict[str, WebSocket]] = {
            "signals": {},
            "risk": {},
            "events": {},
            "satellite": {},
        }
        self.connection_metadata: dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, channel: str) -> str:
        """Accept a WebSocket connection and return connection ID."""
        await websocket.accept()

        prefix_map = {
            "signals": "SIG",
            "risk": "RSK",
            "events": "EVT",
            "satellite": "SAT",
        }
        prefix = prefix_map.get(channel, "GA")
        connection_id = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

        if channel in self.active_connections:
            self.active_connections[channel][connection_id] = websocket

        self.connection_metadata[connection_id] = {
            "channel": channel,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
        }

        await self._send_connection_message(websocket, channel, connection_id)
        return connection_id

    async def disconnect(self, connection_id: str, channel: str):
        """Remove a WebSocket connection."""
        if channel in self.active_connections:
            self.active_connections[channel].pop(connection_id, None)
        self.connection_metadata.pop(connection_id, None)

    async def _send_connection_message(
        self,
        websocket: WebSocket,
        channel: str,
        connection_id: str,
    ):
        """Send connection established message."""
        message = {
            "type": "connection_established",
            "channel": channel,
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to Global Awareness {channel.title()} channel",
        }
        await websocket.send_json(message)

    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast a message to all connections in a channel."""
        if channel not in self.active_connections:
            return

        disconnected = []
        for conn_id, websocket in self.active_connections[channel].items():
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(conn_id)

        for conn_id in disconnected:
            await self.disconnect(conn_id, channel)

    async def send_to_connection(self, connection_id: str, channel: str, message: dict):
        """Send a message to a specific connection."""
        if channel in self.active_connections:
            websocket = self.active_connections[channel].get(connection_id)
            if websocket:
                try:
                    await websocket.send_json(message)
                except Exception:
                    await self.disconnect(connection_id, channel)

    def get_connection_count(self, channel: str) -> int:
        """Get the number of active connections in a channel."""
        return len(self.active_connections.get(channel, {}))

    def get_all_connection_counts(self) -> dict[str, int]:
        """Get connection counts for all channels."""
        return {
            channel: len(connections)
            for channel, connections in self.active_connections.items()
        }


global_awareness_ws_manager = GlobalAwarenessWSManager()


async def broadcast_signal_update(signal_data: dict):
    """Broadcast a new global signal to all connected clients."""
    message = {
        "type": "signal_update",
        "timestamp": datetime.utcnow().isoformat(),
        "signal_id": signal_data.get("signal_id"),
        "domain": signal_data.get("domain"),
        "severity": signal_data.get("severity"),
        "title": signal_data.get("title"),
        "description": signal_data.get("description"),
        "location": signal_data.get("location"),
        "affected_regions": signal_data.get("affected_regions", []),
        "affected_countries": signal_data.get("affected_countries", []),
        "confidence_score": signal_data.get("confidence_score"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("signals", message)


async def broadcast_signal_alert(alert_data: dict):
    """Broadcast a signal alert to all connected clients."""
    message = {
        "type": "signal_alert",
        "timestamp": datetime.utcnow().isoformat(),
        "alert_id": alert_data.get("alert_id"),
        "domain": alert_data.get("domain"),
        "severity": alert_data.get("severity"),
        "title": alert_data.get("title"),
        "description": alert_data.get("description"),
        "recommended_action": alert_data.get("recommended_action"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("signals", message)


async def broadcast_maritime_anomaly(anomaly_data: dict):
    """Broadcast a maritime anomaly detection."""
    message = {
        "type": "maritime_anomaly",
        "timestamp": datetime.utcnow().isoformat(),
        "signal_id": anomaly_data.get("signal_id"),
        "vessel_mmsi": anomaly_data.get("vessel_mmsi"),
        "vessel_name": anomaly_data.get("vessel_name"),
        "anomaly_type": anomaly_data.get("anomaly_type"),
        "anomaly_score": anomaly_data.get("anomaly_score"),
        "position": anomaly_data.get("position"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("signals", message)


async def broadcast_cyber_threat(threat_data: dict):
    """Broadcast a cyber threat signal."""
    message = {
        "type": "cyber_threat",
        "timestamp": datetime.utcnow().isoformat(),
        "signal_id": threat_data.get("signal_id"),
        "threat_type": threat_data.get("threat_type"),
        "threat_actor": threat_data.get("threat_actor"),
        "target_sector": threat_data.get("target_sector"),
        "target_country": threat_data.get("target_country"),
        "severity": threat_data.get("severity"),
        "iocs": threat_data.get("iocs", []),
    }
    await global_awareness_ws_manager.broadcast_to_channel("signals", message)


async def broadcast_risk_update(risk_data: dict):
    """Broadcast a risk assessment update."""
    message = {
        "type": "risk_update",
        "timestamp": datetime.utcnow().isoformat(),
        "assessment_id": risk_data.get("assessment_id"),
        "region": risk_data.get("region"),
        "country": risk_data.get("country"),
        "overall_risk_score": risk_data.get("overall_risk_score"),
        "overall_risk_level": risk_data.get("overall_risk_level"),
        "primary_risk_domain": risk_data.get("primary_risk_domain"),
        "trend": risk_data.get("trend"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("risk", message)


async def broadcast_risk_alert(alert_data: dict):
    """Broadcast a risk alert."""
    message = {
        "type": "risk_alert",
        "timestamp": datetime.utcnow().isoformat(),
        "alert_id": alert_data.get("alert_id"),
        "domain": alert_data.get("domain"),
        "region": alert_data.get("region"),
        "title": alert_data.get("title"),
        "risk_level": alert_data.get("risk_level"),
        "trigger_factors": alert_data.get("trigger_factors", []),
        "recommended_response": alert_data.get("recommended_response"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("risk", message)


async def broadcast_domain_risk_change(domain_data: dict):
    """Broadcast a domain risk score change."""
    message = {
        "type": "domain_risk_change",
        "timestamp": datetime.utcnow().isoformat(),
        "score_id": domain_data.get("score_id"),
        "domain": domain_data.get("domain"),
        "region": domain_data.get("region"),
        "score": domain_data.get("score"),
        "level": domain_data.get("level"),
        "trend": domain_data.get("trend"),
        "contributing_factors": domain_data.get("contributing_factors", []),
    }
    await global_awareness_ws_manager.broadcast_to_channel("risk", message)


async def broadcast_event_created(event_data: dict):
    """Broadcast a new event creation."""
    message = {
        "type": "event_created",
        "timestamp": datetime.utcnow().isoformat(),
        "event_id": event_data.get("event_id"),
        "category": event_data.get("category"),
        "title": event_data.get("title"),
        "description": event_data.get("description"),
        "location": event_data.get("location"),
        "impact_magnitude": event_data.get("impact_magnitude"),
        "affected_regions": event_data.get("affected_regions", []),
        "affected_countries": event_data.get("affected_countries", []),
    }
    await global_awareness_ws_manager.broadcast_to_channel("events", message)


async def broadcast_correlation_detected(correlation_data: dict):
    """Broadcast a new event correlation."""
    message = {
        "type": "correlation_detected",
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": correlation_data.get("correlation_id"),
        "source_event_id": correlation_data.get("source_event_id"),
        "target_event_id": correlation_data.get("target_event_id"),
        "correlation_type": correlation_data.get("correlation_type"),
        "strength": correlation_data.get("strength"),
        "mechanism": correlation_data.get("mechanism"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("events", message)


async def broadcast_cascade_prediction(cascade_data: dict):
    """Broadcast a cascade effect prediction."""
    message = {
        "type": "cascade_prediction",
        "timestamp": datetime.utcnow().isoformat(),
        "cascade_id": cascade_data.get("cascade_id"),
        "trigger_event_id": cascade_data.get("trigger_event_id"),
        "cascade_type": cascade_data.get("cascade_type"),
        "total_impact_score": cascade_data.get("total_impact_score"),
        "probability": cascade_data.get("probability"),
        "propagation_path": cascade_data.get("propagation_path", []),
        "mitigation_options": cascade_data.get("mitigation_options", []),
    }
    await global_awareness_ws_manager.broadcast_to_channel("events", message)


async def broadcast_pattern_detected(pattern_data: dict):
    """Broadcast a detected event pattern."""
    message = {
        "type": "pattern_detected",
        "timestamp": datetime.utcnow().isoformat(),
        "pattern_id": pattern_data.get("pattern_id"),
        "pattern_name": pattern_data.get("pattern_name"),
        "pattern_type": pattern_data.get("pattern_type"),
        "frequency": pattern_data.get("frequency"),
        "confidence": pattern_data.get("confidence"),
        "description": pattern_data.get("description"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("events", message)


async def broadcast_satellite_detection(detection_data: dict):
    """Broadcast a satellite change detection."""
    message = {
        "type": "satellite_detection",
        "timestamp": datetime.utcnow().isoformat(),
        "detection_id": detection_data.get("detection_id"),
        "change_category": detection_data.get("change_category"),
        "location": detection_data.get("location"),
        "area_sq_km": detection_data.get("area_sq_km"),
        "change_magnitude": detection_data.get("change_magnitude"),
        "confidence": detection_data.get("confidence"),
        "description": detection_data.get("description"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("satellite", message)


async def broadcast_satellite_alert(alert_data: dict):
    """Broadcast a satellite alert."""
    message = {
        "type": "satellite_alert",
        "timestamp": datetime.utcnow().isoformat(),
        "alert_id": alert_data.get("alert_id"),
        "alert_type": alert_data.get("alert_type"),
        "priority": alert_data.get("priority"),
        "title": alert_data.get("title"),
        "description": alert_data.get("description"),
        "location": alert_data.get("location"),
        "recommended_action": alert_data.get("recommended_action"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("satellite", message)


async def broadcast_maritime_detection(detection_data: dict):
    """Broadcast a maritime detection from satellite imagery."""
    message = {
        "type": "maritime_detection",
        "timestamp": datetime.utcnow().isoformat(),
        "detection_id": detection_data.get("detection_id"),
        "image_id": detection_data.get("image_id"),
        "vessel_count": detection_data.get("vessel_count"),
        "port_activity_level": detection_data.get("port_activity_level"),
        "anomalies": detection_data.get("anomalies", []),
        "location": detection_data.get("location"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("satellite", message)


async def broadcast_military_detection(detection_data: dict):
    """Broadcast a military activity detection from satellite imagery."""
    message = {
        "type": "military_detection",
        "timestamp": datetime.utcnow().isoformat(),
        "detection_id": detection_data.get("detection_id"),
        "activity_type": detection_data.get("activity_type"),
        "unit_types": detection_data.get("unit_types", []),
        "estimated_personnel": detection_data.get("estimated_personnel"),
        "vehicle_count": detection_data.get("vehicle_count"),
        "aircraft_count": detection_data.get("aircraft_count"),
        "assessment": detection_data.get("assessment"),
        "location": detection_data.get("location"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("satellite", message)


async def broadcast_infrastructure_assessment(assessment_data: dict):
    """Broadcast an infrastructure assessment from satellite imagery."""
    message = {
        "type": "infrastructure_assessment",
        "timestamp": datetime.utcnow().isoformat(),
        "assessment_id": assessment_data.get("assessment_id"),
        "infrastructure_type": assessment_data.get("infrastructure_type"),
        "condition": assessment_data.get("condition"),
        "damage_level": assessment_data.get("damage_level"),
        "activity_level": assessment_data.get("activity_level"),
        "changes_detected": assessment_data.get("changes_detected", []),
        "location": assessment_data.get("location"),
    }
    await global_awareness_ws_manager.broadcast_to_channel("satellite", message)


async def handle_signals_websocket(websocket: WebSocket):
    """Handle WebSocket connection for global signals channel."""
    connection_id = await global_awareness_ws_manager.connect(websocket, "signals")
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "subscribe_domain":
                domain = data.get("domain")
                await websocket.send_json({
                    "type": "subscribed",
                    "domain": domain,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "subscribe_region":
                region = data.get("region")
                await websocket.send_json({
                    "type": "subscribed",
                    "region": region,
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        await global_awareness_ws_manager.disconnect(connection_id, "signals")


async def handle_risk_websocket(websocket: WebSocket):
    """Handle WebSocket connection for risk assessment channel."""
    connection_id = await global_awareness_ws_manager.connect(websocket, "risk")
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "subscribe_region":
                region = data.get("region")
                await websocket.send_json({
                    "type": "subscribed",
                    "region": region,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "subscribe_domain":
                domain = data.get("domain")
                await websocket.send_json({
                    "type": "subscribed",
                    "domain": domain,
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        await global_awareness_ws_manager.disconnect(connection_id, "risk")


async def handle_events_websocket(websocket: WebSocket):
    """Handle WebSocket connection for event correlation channel."""
    connection_id = await global_awareness_ws_manager.connect(websocket, "events")
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "subscribe_category":
                category = data.get("category")
                await websocket.send_json({
                    "type": "subscribed",
                    "category": category,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "track_event":
                event_id = data.get("event_id")
                await websocket.send_json({
                    "type": "tracking",
                    "event_id": event_id,
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        await global_awareness_ws_manager.disconnect(connection_id, "events")


async def handle_satellite_websocket(websocket: WebSocket):
    """Handle WebSocket connection for satellite detection channel."""
    connection_id = await global_awareness_ws_manager.connect(websocket, "satellite")
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "subscribe_location":
                location = data.get("location")
                await websocket.send_json({
                    "type": "subscribed",
                    "location": location,
                    "timestamp": datetime.utcnow().isoformat(),
                })
            elif data.get("type") == "subscribe_detection_type":
                detection_type = data.get("detection_type")
                await websocket.send_json({
                    "type": "subscribed",
                    "detection_type": detection_type,
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        await global_awareness_ws_manager.disconnect(connection_id, "satellite")
