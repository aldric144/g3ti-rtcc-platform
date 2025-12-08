"""
Real-time API router for the G3TI RTCC-UIP Backend.

This module provides:
- WebSocket endpoint for real-time events
- Event management endpoints
- Subscription management
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from app.api.deps import (
    CurrentUserId,
    RequireOfficer,
)
from app.core.logging import get_logger
from app.schemas.events import (
    EventAcknowledge,
    EventResponse,
    EventSource,
    EventType,
)
from app.services.auth.auth_service import get_auth_service
from app.services.events.event_processor import EventProcessor, get_event_processor
from app.services.events.websocket_manager import WebSocketManager, get_websocket_manager

logger = get_logger(__name__)
router = APIRouter()


@router.websocket("/ws/events")
async def websocket_events(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for real-time events.

    Connect to receive real-time events from all sources.

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (client -> server):
    - subscribe: Subscribe to specific event types/sources
    - unsubscribe: Clear subscription filters
    - acknowledge: Acknowledge an event
    - ping: Heartbeat ping

    Message Types (server -> client):
    - connected: Connection established
    - event: Real-time event
    - subscribed: Subscription confirmed
    - unsubscribed: Unsubscription confirmed
    - acknowledged: Acknowledgment confirmed
    - pong: Heartbeat response
    - error: Error message
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    # Validate token if provided
    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    # Accept connection
    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("websocket_connection_rejected", error=str(e))
        return

    try:
        # Handle messages
        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_message(client_id, data)

    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("websocket_error", client_id=client_id, error=str(e))
    finally:
        await ws_manager.disconnect(client_id)


@router.get("/events", response_model=list[EventResponse])
async def get_recent_events(
    token: RequireOfficer,
    event_processor: Annotated[EventProcessor, Depends(get_event_processor)],
    limit: int = Query(default=100, le=500),
    event_type: EventType | None = None,
    source: EventSource | None = None,
    acknowledged: bool | None = None,
) -> list[EventResponse]:
    """
    Get recent events.

    - **limit**: Maximum events to return (default: 100, max: 500)
    - **event_type**: Filter by event type (optional)
    - **source**: Filter by source (optional)
    - **acknowledged**: Filter by acknowledgment status (optional)

    Returns list of recent events.
    """
    event_types = [event_type] if event_type else None
    sources = [source] if source else None

    events = await event_processor.get_recent_events(
        limit=limit, event_types=event_types, sources=sources, acknowledged=acknowledged
    )

    return events


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    token: RequireOfficer,
    event_processor: Annotated[EventProcessor, Depends(get_event_processor)],
) -> EventResponse:
    """
    Get a specific event by ID.

    - **event_id**: Event identifier
    """
    event = await event_processor.get_event(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


@router.post("/events/{event_id}/acknowledge")
async def acknowledge_event(
    event_id: str,
    acknowledge_data: EventAcknowledge,
    token: RequireOfficer,
    user_id: CurrentUserId,
    event_processor: Annotated[EventProcessor, Depends(get_event_processor)],
) -> dict[str, str]:
    """
    Acknowledge an event.

    - **event_id**: Event identifier
    - **notes**: Optional acknowledgment notes
    """
    success = await event_processor.acknowledge_event(
        event_id=event_id, user_id=user_id, notes=acknowledge_data.notes
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return {"message": "Event acknowledged successfully"}


@router.get("/stats")
async def get_realtime_stats(
    token: RequireOfficer,
    ws_manager: Annotated[WebSocketManager, Depends(get_websocket_manager)],
) -> dict:
    """
    Get real-time system statistics.

    Returns current connection counts and event statistics.
    """
    return {"active_connections": ws_manager.get_connection_count(), "status": "operational"}


# ============================================================================
# Phase 4: Case Updates WebSocket
# ============================================================================

# Store for case subscriptions: case_id -> set of client_ids
_case_subscriptions: dict[str, set[str]] = {}


@router.websocket("/ws/case-updates/{case_id}")
async def websocket_case_updates(
    websocket: WebSocket,
    case_id: str,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for real-time case updates.

    Connect to receive updates for a specific case including:
    - New entity correlations
    - New linked incidents
    - Risk score changes
    - Timeline updates
    - Evidence additions
    - Pattern/anomaly alerts relevant to the case

    Path Parameters:
    - **case_id**: The case ID to subscribe to

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - case_update: General case update
    - entity_correlation: New entity correlation found
    - incident_linked: New incident linked to case
    - risk_updated: Risk score changed
    - timeline_updated: New timeline event
    - evidence_added: New evidence added
    - pattern_alert: Pattern/anomaly relevant to case
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    # Validate token if provided
    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("case_websocket_auth_failed", case_id=case_id, error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    # Accept connection
    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("case_websocket_connection_rejected", case_id=case_id, error=str(e))
        return

    # Add to case subscriptions
    if case_id not in _case_subscriptions:
        _case_subscriptions[case_id] = set()
    _case_subscriptions[case_id].add(client_id)

    logger.info("case_websocket_connected", case_id=case_id, client_id=client_id, user_id=user_id)

    # Send connection confirmation
    await websocket.send_json(
        {
            "type": "connected",
            "case_id": case_id,
            "message": f"Subscribed to updates for case {case_id}",
        }
    )

    try:
        # Handle messages
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong for keepalive
            import json

            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        logger.info("case_websocket_disconnected", case_id=case_id, client_id=client_id)
    except Exception as e:
        logger.error("case_websocket_error", case_id=case_id, client_id=client_id, error=str(e))
    finally:
        # Remove from case subscriptions
        if case_id in _case_subscriptions:
            _case_subscriptions[case_id].discard(client_id)
            if not _case_subscriptions[case_id]:
                del _case_subscriptions[case_id]
        await ws_manager.disconnect(client_id)


async def broadcast_case_update(
    case_id: str,
    update_type: str,
    data: dict,
) -> None:
    """
    Broadcast an update to all clients subscribed to a case.

    Args:
        case_id: The case ID to broadcast to
        update_type: Type of update (entity_correlation, incident_linked, etc.)
        data: Update data to send
    """
    if case_id not in _case_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": update_type,
        "case_id": case_id,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_case_subscriptions[case_id]):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "case_broadcast_failed",
                case_id=case_id,
                client_id=client_id,
                error=str(e),
            )


def get_case_subscribers(case_id: str) -> set[str]:
    """Get the set of client IDs subscribed to a case."""
    return _case_subscriptions.get(case_id, set()).copy()


def get_subscribed_cases() -> list[str]:
    """Get list of all cases with active subscriptions."""
    return list(_case_subscriptions.keys())


# ============================================================================
# Phase 5: Tactical Analytics WebSocket Channels
# ============================================================================

# Store for tactical subscriptions
_tactical_alert_subscriptions: set[str] = set()
_tactical_zone_subscriptions: dict[str, set[str]] = {}  # zone_id -> client_ids
_tactical_prediction_subscriptions: set[str] = set()


@router.websocket("/ws/tactical/alerts")
async def websocket_tactical_alerts(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for real-time tactical alerts.

    Connect to receive tactical alerts including:
    - zone_risk_update: Zone risk score changed
    - new_hotspot: New hotspot detected
    - patrol_route_update: Patrol route recommendation updated
    - tactical_alert: General tactical alert
    - anomaly_relevant_to_zone: AI anomaly detected in zone
    - predicted_cluster: New predicted activity cluster

    Query Parameters:
    - **token**: JWT access token for authentication
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    # Validate token if provided
    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("tactical_alerts_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    # Accept connection
    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("tactical_alerts_websocket_connection_rejected", error=str(e))
        return

    # Add to tactical alert subscriptions
    _tactical_alert_subscriptions.add(client_id)

    logger.info("tactical_alerts_websocket_connected", client_id=client_id, user_id=user_id)

    # Send connection confirmation
    await websocket.send_json(
        {
            "type": "connected",
            "channel": "tactical_alerts",
            "message": "Subscribed to tactical alerts",
        }
    )

    try:
        # Handle messages
        while True:
            data = await websocket.receive_text()
            import json

            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        logger.info("tactical_alerts_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("tactical_alerts_websocket_error", client_id=client_id, error=str(e))
    finally:
        _tactical_alert_subscriptions.discard(client_id)
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/tactical/zones")
async def websocket_tactical_zones(
    websocket: WebSocket,
    zone_id: str | None = Query(default=None),
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for real-time zone updates.

    Connect to receive updates for tactical zones including:
    - zone_risk_update: Zone risk score changed
    - zone_activity_update: Zone activity level changed
    - zone_status_change: Zone status changed (hot/warm/cool/cold)
    - zone_incident: New incident in zone

    Query Parameters:
    - **zone_id**: Optional specific zone to subscribe to (all zones if not specified)
    - **token**: JWT access token for authentication
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    # Validate token if provided
    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("tactical_zones_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    # Accept connection
    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("tactical_zones_websocket_connection_rejected", error=str(e))
        return

    # Add to zone subscriptions
    subscription_key = zone_id or "__all__"
    if subscription_key not in _tactical_zone_subscriptions:
        _tactical_zone_subscriptions[subscription_key] = set()
    _tactical_zone_subscriptions[subscription_key].add(client_id)

    logger.info(
        "tactical_zones_websocket_connected",
        client_id=client_id,
        user_id=user_id,
        zone_id=zone_id,
    )

    # Send connection confirmation
    await websocket.send_json(
        {
            "type": "connected",
            "channel": "tactical_zones",
            "zone_id": zone_id,
            "message": f"Subscribed to zone updates{f' for {zone_id}' if zone_id else ''}",
        }
    )

    try:
        # Handle messages
        while True:
            data = await websocket.receive_text()
            import json

            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        logger.info("tactical_zones_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("tactical_zones_websocket_error", client_id=client_id, error=str(e))
    finally:
        if subscription_key in _tactical_zone_subscriptions:
            _tactical_zone_subscriptions[subscription_key].discard(client_id)
            if not _tactical_zone_subscriptions[subscription_key]:
                del _tactical_zone_subscriptions[subscription_key]
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/tactical/predictions")
async def websocket_tactical_predictions(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for real-time prediction updates.

    Connect to receive prediction updates including:
    - prediction_update: New prediction generated
    - hotspot_prediction: New hotspot predicted
    - forecast_update: Forecast model updated
    - risk_forecast: Risk forecast changed

    Query Parameters:
    - **token**: JWT access token for authentication
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    # Validate token if provided
    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("tactical_predictions_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    # Accept connection
    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("tactical_predictions_websocket_connection_rejected", error=str(e))
        return

    # Add to prediction subscriptions
    _tactical_prediction_subscriptions.add(client_id)

    logger.info("tactical_predictions_websocket_connected", client_id=client_id, user_id=user_id)

    # Send connection confirmation
    await websocket.send_json(
        {
            "type": "connected",
            "channel": "tactical_predictions",
            "message": "Subscribed to prediction updates",
        }
    )

    try:
        # Handle messages
        while True:
            data = await websocket.receive_text()
            import json

            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        logger.info("tactical_predictions_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("tactical_predictions_websocket_error", client_id=client_id, error=str(e))
    finally:
        _tactical_prediction_subscriptions.discard(client_id)
        await ws_manager.disconnect(client_id)


# ============================================================================
# Tactical Broadcast Functions
# ============================================================================


async def broadcast_tactical_alert(
    alert_type: str,
    data: dict,
    severity: str = "medium",
) -> None:
    """
    Broadcast a tactical alert to all subscribed clients.

    Args:
        alert_type: Type of alert (zone_risk_update, new_hotspot, etc.)
        data: Alert data to send
        severity: Alert severity (low, medium, high, critical)
    """
    if not _tactical_alert_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": alert_type,
        "severity": severity,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_tactical_alert_subscriptions):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "tactical_alert_broadcast_failed",
                client_id=client_id,
                error=str(e),
            )


async def broadcast_zone_update(
    zone_id: str,
    update_type: str,
    data: dict,
) -> None:
    """
    Broadcast a zone update to subscribed clients.

    Args:
        zone_id: The zone ID to broadcast for
        update_type: Type of update
        data: Update data to send
    """
    ws_manager = get_websocket_manager()
    message = {
        "type": update_type,
        "zone_id": zone_id,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    # Broadcast to zone-specific subscribers
    if zone_id in _tactical_zone_subscriptions:
        for client_id in list(_tactical_zone_subscriptions[zone_id]):
            try:
                await ws_manager.send_to_client(client_id, message)
            except Exception as e:
                logger.warning(
                    "zone_update_broadcast_failed",
                    zone_id=zone_id,
                    client_id=client_id,
                    error=str(e),
                )

    # Broadcast to all-zones subscribers
    if "__all__" in _tactical_zone_subscriptions:
        for client_id in list(_tactical_zone_subscriptions["__all__"]):
            try:
                await ws_manager.send_to_client(client_id, message)
            except Exception as e:
                logger.warning(
                    "zone_update_broadcast_failed",
                    zone_id=zone_id,
                    client_id=client_id,
                    error=str(e),
                )


async def broadcast_prediction_update(
    prediction_type: str,
    data: dict,
) -> None:
    """
    Broadcast a prediction update to subscribed clients.

    Args:
        prediction_type: Type of prediction update
        data: Prediction data to send
    """
    if not _tactical_prediction_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": prediction_type,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_tactical_prediction_subscriptions):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "prediction_update_broadcast_failed",
                client_id=client_id,
                error=str(e),
            )


def get_tactical_alert_subscribers() -> set[str]:
    """Get the set of client IDs subscribed to tactical alerts."""
    return _tactical_alert_subscriptions.copy()


def get_tactical_zone_subscribers(zone_id: str | None = None) -> set[str]:
    """Get the set of client IDs subscribed to zone updates."""
    if zone_id:
        return _tactical_zone_subscriptions.get(zone_id, set()).copy()
    return _tactical_zone_subscriptions.get("__all__", set()).copy()


def get_tactical_prediction_subscribers() -> set[str]:
    """Get the set of client IDs subscribed to prediction updates."""
    return _tactical_prediction_subscriptions.copy()
