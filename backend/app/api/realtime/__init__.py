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
# Phase 6: Officer Safety WebSocket Channels
# ============================================================================

# Store for officer safety subscriptions
_officer_location_subscriptions: dict[str, set[str]] = {}  # badge -> client_ids
_officer_threat_subscriptions: set[str] = set()  # client_ids subscribed to all threats
_officer_ambush_subscriptions: set[str] = set()  # client_ids subscribed to ambush alerts
_officer_perimeter_subscriptions: dict[str, set[str]] = {}  # incident_id -> client_ids
_officer_safety_score_subscriptions: set[str] = set()  # client_ids subscribed to safety scores
_officer_down_subscriptions: set[str] = set()  # client_ids subscribed to officer down alerts


@router.websocket("/ws/officer/location")
async def websocket_officer_location(
    websocket: WebSocket,
    badge: str | None = Query(default=None),
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for officer location updates.

    Connect to receive real-time officer location telemetry.

    Query Parameters:
    - **badge**: Optional badge number to subscribe to specific officer
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - location_update: Officer position update
    - status_change: Officer status changed
    - all_positions: Periodic broadcast of all officer positions
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
            logger.warning("officer_location_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    # Accept connection
    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("officer_location_websocket_rejected", error=str(e))
        return

    # Add to subscriptions
    subscription_key = badge or "all"
    if subscription_key not in _officer_location_subscriptions:
        _officer_location_subscriptions[subscription_key] = set()
    _officer_location_subscriptions[subscription_key].add(client_id)

    logger.info(
        "officer_location_websocket_connected",
        client_id=client_id,
        badge=badge,
        user_id=user_id,
    )

    # Send connection confirmation
    await websocket.send_json(
        {
            "type": "connected",
            "subscription": subscription_key,
            "message": "Subscribed to officer location updates"
            + (f" for badge {badge}" if badge else " for all officers"),
        }
    )

    try:
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
        logger.info("officer_location_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("officer_location_websocket_error", client_id=client_id, error=str(e))
    finally:
        if subscription_key in _officer_location_subscriptions:
            _officer_location_subscriptions[subscription_key].discard(client_id)
            if not _officer_location_subscriptions[subscription_key]:
                del _officer_location_subscriptions[subscription_key]
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/officer/threats")
async def websocket_officer_threats(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for officer threat alerts.

    Connect to receive real-time threat proximity alerts.

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - threat_alert: New threat detected near officer
    - threat_resolved: Threat no longer in proximity
    - threat_update: Threat status changed
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("officer_threats_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("officer_threats_websocket_rejected", error=str(e))
        return

    _officer_threat_subscriptions.add(client_id)

    logger.info("officer_threats_websocket_connected", client_id=client_id, user_id=user_id)

    await websocket.send_json(
        {"type": "connected", "message": "Subscribed to officer threat alerts"}
    )

    try:
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
        logger.info("officer_threats_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("officer_threats_websocket_error", client_id=client_id, error=str(e))
    finally:
        _officer_threat_subscriptions.discard(client_id)
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/officer/ambush")
async def websocket_officer_ambush(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for ambush warning alerts.

    Connect to receive real-time ambush pattern detection alerts.

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - ambush_warning: Potential ambush pattern detected
    - ambush_cleared: Ambush warning cleared
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("officer_ambush_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("officer_ambush_websocket_rejected", error=str(e))
        return

    _officer_ambush_subscriptions.add(client_id)

    logger.info("officer_ambush_websocket_connected", client_id=client_id, user_id=user_id)

    await websocket.send_json(
        {"type": "connected", "message": "Subscribed to ambush warning alerts"}
    )

    try:
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
        logger.info("officer_ambush_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("officer_ambush_websocket_error", client_id=client_id, error=str(e))
    finally:
        _officer_ambush_subscriptions.discard(client_id)
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/officer/perimeter/{incident_id}")
async def websocket_officer_perimeter(
    websocket: WebSocket,
    incident_id: str,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for perimeter updates.

    Connect to receive real-time perimeter updates for an incident.

    Path Parameters:
    - **incident_id**: Incident ID to subscribe to

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - perimeter_update: Perimeter boundaries changed
    - route_update: Approach routes updated
    - unit_position: Unit position within perimeter
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("officer_perimeter_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("officer_perimeter_websocket_rejected", error=str(e))
        return

    if incident_id not in _officer_perimeter_subscriptions:
        _officer_perimeter_subscriptions[incident_id] = set()
    _officer_perimeter_subscriptions[incident_id].add(client_id)

    logger.info(
        "officer_perimeter_websocket_connected",
        client_id=client_id,
        incident_id=incident_id,
        user_id=user_id,
    )

    await websocket.send_json(
        {
            "type": "connected",
            "incident_id": incident_id,
            "message": f"Subscribed to perimeter updates for incident {incident_id}",
        }
    )

    try:
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
        logger.info("officer_perimeter_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("officer_perimeter_websocket_error", client_id=client_id, error=str(e))
    finally:
        if incident_id in _officer_perimeter_subscriptions:
            _officer_perimeter_subscriptions[incident_id].discard(client_id)
            if not _officer_perimeter_subscriptions[incident_id]:
                del _officer_perimeter_subscriptions[incident_id]
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/officer/safetyscore")
async def websocket_officer_safety_score(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for officer safety score updates.

    Connect to receive real-time safety score changes.

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - safety_score_update: Officer safety score changed
    - risk_level_change: Risk level threshold crossed
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("officer_safety_score_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("officer_safety_score_websocket_rejected", error=str(e))
        return

    _officer_safety_score_subscriptions.add(client_id)

    logger.info("officer_safety_score_websocket_connected", client_id=client_id, user_id=user_id)

    await websocket.send_json(
        {"type": "connected", "message": "Subscribed to officer safety score updates"}
    )

    try:
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
        logger.info("officer_safety_score_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("officer_safety_score_websocket_error", client_id=client_id, error=str(e))
    finally:
        _officer_safety_score_subscriptions.discard(client_id)
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/officer/down")
async def websocket_officer_down(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for officer down / SOS alerts.

    Connect to receive critical officer emergency alerts.

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - officer_down: Officer down alert triggered
    - officer_sos: SOS alert triggered
    - emergency_cleared: Emergency cleared
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("officer_down_websocket_auth_failed", error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("officer_down_websocket_rejected", error=str(e))
        return

    _officer_down_subscriptions.add(client_id)

    logger.info("officer_down_websocket_connected", client_id=client_id, user_id=user_id)

    await websocket.send_json(
        {"type": "connected", "message": "Subscribed to officer down / SOS alerts"}
    )

    try:
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
        logger.info("officer_down_websocket_disconnected", client_id=client_id)
    except Exception as e:
        logger.error("officer_down_websocket_error", client_id=client_id, error=str(e))
    finally:
        _officer_down_subscriptions.discard(client_id)
        await ws_manager.disconnect(client_id)


# Broadcast functions for officer safety events
async def broadcast_officer_location(
    badge: str,
    location_data: dict,
) -> None:
    """Broadcast officer location update to subscribers."""
    ws_manager = get_websocket_manager()
    message = {
        "type": "location_update",
        "badge": badge,
        "data": location_data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    # Send to badge-specific subscribers
    if badge in _officer_location_subscriptions:
        for client_id in list(_officer_location_subscriptions[badge]):
            try:
                await ws_manager.send_to_client(client_id, message)
            except Exception as e:
                logger.warning("officer_location_broadcast_failed", client_id=client_id, error=str(e))

    # Send to all-officers subscribers
    if "all" in _officer_location_subscriptions:
        for client_id in list(_officer_location_subscriptions["all"]):
            try:
                await ws_manager.send_to_client(client_id, message)
            except Exception as e:
                logger.warning("officer_location_broadcast_failed", client_id=client_id, error=str(e))


async def broadcast_threat_alert(
    badge: str,
    threat_data: dict,
) -> None:
    """Broadcast threat alert to subscribers."""
    ws_manager = get_websocket_manager()
    message = {
        "type": "threat_alert",
        "badge": badge,
        "data": threat_data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_officer_threat_subscriptions):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning("threat_alert_broadcast_failed", client_id=client_id, error=str(e))


async def broadcast_ambush_warning(
    badge: str,
    ambush_data: dict,
) -> None:
    """Broadcast ambush warning to subscribers."""
    ws_manager = get_websocket_manager()
    message = {
        "type": "ambush_warning",
        "badge": badge,
        "data": ambush_data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_officer_ambush_subscriptions):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning("ambush_warning_broadcast_failed", client_id=client_id, error=str(e))


async def broadcast_perimeter_update(
    incident_id: str,
    perimeter_data: dict,
) -> None:
    """Broadcast perimeter update to subscribers."""
    if incident_id not in _officer_perimeter_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": "perimeter_update",
        "incident_id": incident_id,
        "data": perimeter_data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_officer_perimeter_subscriptions[incident_id]):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning("perimeter_update_broadcast_failed", client_id=client_id, error=str(e))


async def broadcast_safety_score_update(
    badge: str,
    score_data: dict,
) -> None:
    """Broadcast safety score update to subscribers."""
    ws_manager = get_websocket_manager()
    message = {
        "type": "safety_score_update",
        "badge": badge,
        "data": score_data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_officer_safety_score_subscriptions):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning("safety_score_broadcast_failed", client_id=client_id, error=str(e))


async def broadcast_officer_down(
    badge: str,
    emergency_data: dict,
) -> None:
    """Broadcast officer down alert to all subscribers."""
    ws_manager = get_websocket_manager()
    message = {
        "type": "officer_down",
        "badge": badge,
        "data": emergency_data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "priority": "critical",
    }

    for client_id in list(_officer_down_subscriptions):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning("officer_down_broadcast_failed", client_id=client_id, error=str(e))


async def broadcast_officer_sos(
    badge: str,
    sos_data: dict,
) -> None:
    """Broadcast SOS alert to all subscribers."""
    ws_manager = get_websocket_manager()
    message = {
        "type": "officer_sos",
        "badge": badge,
        "data": sos_data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "priority": "critical",
    }

    for client_id in list(_officer_down_subscriptions):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning("officer_sos_broadcast_failed", client_id=client_id, error=str(e))


# Subscription info functions
def get_officer_location_subscribers() -> dict[str, int]:
    """Get count of subscribers per badge/all."""
    return {k: len(v) for k, v in _officer_location_subscriptions.items()}


def get_officer_threat_subscriber_count() -> int:
    """Get count of threat alert subscribers."""
    return len(_officer_threat_subscriptions)


def get_officer_down_subscriber_count() -> int:
    """Get count of officer down alert subscribers."""
    return len(_officer_down_subscriptions)


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


# ============================================================================
# Phase 8: Command Operations WebSocket Channels
# ============================================================================

# Store for command operations subscriptions
_incident_subscriptions: dict[str, set[str]] = {}  # incident_id -> client_ids
_ics_subscriptions: dict[str, set[str]] = {}  # incident_id -> client_ids
_strategy_map_subscriptions: dict[str, set[str]] = {}  # incident_id -> client_ids
_resources_subscriptions: dict[str, set[str]] = {}  # incident_id -> client_ids
_timeline_subscriptions: dict[str, set[str]] = {}  # incident_id -> client_ids
_briefing_subscriptions: dict[str, set[str]] = {}  # incident_id -> client_ids
_command_subscriptions: set[str] = set()  # client_ids subscribed to all command events


@router.websocket("/ws/command/incident/{incident_id}")
async def websocket_command_incident(
    websocket: WebSocket,
    incident_id: str,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for incident updates.

    Connect to receive real-time updates for a specific major incident.

    Path Parameters:
    - **incident_id**: The incident ID to subscribe to

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - incident_update: Incident status/details changed
    - incident_activated: Incident activated
    - incident_closed: Incident closed
    - commander_assigned: New commander assigned
    - agency_added: Agency added to incident
    - unit_assigned: Unit assigned to incident
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("command_incident_websocket_auth_failed", incident_id=incident_id, error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("command_incident_websocket_rejected", incident_id=incident_id, error=str(e))
        return

    if incident_id not in _incident_subscriptions:
        _incident_subscriptions[incident_id] = set()
    _incident_subscriptions[incident_id].add(client_id)

    logger.info("command_incident_websocket_connected", incident_id=incident_id, client_id=client_id, user_id=user_id)

    await websocket.send_json({
        "type": "connected",
        "incident_id": incident_id,
        "message": f"Subscribed to updates for incident {incident_id}",
    })

    try:
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
        logger.info("command_incident_websocket_disconnected", incident_id=incident_id, client_id=client_id)
    except Exception as e:
        logger.error("command_incident_websocket_error", incident_id=incident_id, client_id=client_id, error=str(e))
    finally:
        if incident_id in _incident_subscriptions:
            _incident_subscriptions[incident_id].discard(client_id)
            if not _incident_subscriptions[incident_id]:
                del _incident_subscriptions[incident_id]
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/command/ics/{incident_id}")
async def websocket_command_ics(
    websocket: WebSocket,
    incident_id: str,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for ICS structure updates.

    Connect to receive real-time ICS role assignments and changes.

    Path Parameters:
    - **incident_id**: The incident ID to subscribe to

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - ics_role_assigned: New role assignment
    - ics_role_updated: Role reassigned
    - ics_role_relieved: Role relieved
    - ics_checklist_updated: Checklist item completed
    - ics_structure_changed: Org chart changed
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("command_ics_websocket_auth_failed", incident_id=incident_id, error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("command_ics_websocket_rejected", incident_id=incident_id, error=str(e))
        return

    if incident_id not in _ics_subscriptions:
        _ics_subscriptions[incident_id] = set()
    _ics_subscriptions[incident_id].add(client_id)

    logger.info("command_ics_websocket_connected", incident_id=incident_id, client_id=client_id, user_id=user_id)

    await websocket.send_json({
        "type": "connected",
        "incident_id": incident_id,
        "message": f"Subscribed to ICS updates for incident {incident_id}",
    })

    try:
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
        logger.info("command_ics_websocket_disconnected", incident_id=incident_id, client_id=client_id)
    except Exception as e:
        logger.error("command_ics_websocket_error", incident_id=incident_id, client_id=client_id, error=str(e))
    finally:
        if incident_id in _ics_subscriptions:
            _ics_subscriptions[incident_id].discard(client_id)
            if not _ics_subscriptions[incident_id]:
                del _ics_subscriptions[incident_id]
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/command/strategy-map/{incident_id}")
async def websocket_command_strategy_map(
    websocket: WebSocket,
    incident_id: str,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for strategy map updates.

    Connect to receive real-time map overlays and drawing updates.

    Path Parameters:
    - **incident_id**: The incident ID to subscribe to

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - map_updated: Map center/zoom changed
    - marker_added: New marker added
    - shape_added: New shape drawn
    - perimeter_updated: Perimeter changed
    - unit_position_updated: Unit position changed
    - camera_added: Camera overlay added
    - gunfire_added: Gunfire detection added
    - threat_zone_added: Threat zone added
    - element_removed: Element removed from map
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("command_strategy_map_websocket_auth_failed", incident_id=incident_id, error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("command_strategy_map_websocket_rejected", incident_id=incident_id, error=str(e))
        return

    if incident_id not in _strategy_map_subscriptions:
        _strategy_map_subscriptions[incident_id] = set()
    _strategy_map_subscriptions[incident_id].add(client_id)

    logger.info("command_strategy_map_websocket_connected", incident_id=incident_id, client_id=client_id, user_id=user_id)

    await websocket.send_json({
        "type": "connected",
        "incident_id": incident_id,
        "message": f"Subscribed to strategy map updates for incident {incident_id}",
    })

    try:
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
        logger.info("command_strategy_map_websocket_disconnected", incident_id=incident_id, client_id=client_id)
    except Exception as e:
        logger.error("command_strategy_map_websocket_error", incident_id=incident_id, client_id=client_id, error=str(e))
    finally:
        if incident_id in _strategy_map_subscriptions:
            _strategy_map_subscriptions[incident_id].discard(client_id)
            if not _strategy_map_subscriptions[incident_id]:
                del _strategy_map_subscriptions[incident_id]
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/command/resources/{incident_id}")
async def websocket_command_resources(
    websocket: WebSocket,
    incident_id: str,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for resource assignment updates.

    Connect to receive real-time resource assignment changes.

    Path Parameters:
    - **incident_id**: The incident ID to subscribe to

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - resource_assigned: Resource assigned to incident
    - resource_released: Resource released from incident
    - resource_arrived: Resource arrived on scene
    - resource_status_changed: Resource status updated
    - resource_requested: New resource request
    - resource_request_fulfilled: Request fulfilled
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("command_resources_websocket_auth_failed", incident_id=incident_id, error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("command_resources_websocket_rejected", incident_id=incident_id, error=str(e))
        return

    if incident_id not in _resources_subscriptions:
        _resources_subscriptions[incident_id] = set()
    _resources_subscriptions[incident_id].add(client_id)

    logger.info("command_resources_websocket_connected", incident_id=incident_id, client_id=client_id, user_id=user_id)

    await websocket.send_json({
        "type": "connected",
        "incident_id": incident_id,
        "message": f"Subscribed to resource updates for incident {incident_id}",
    })

    try:
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
        logger.info("command_resources_websocket_disconnected", incident_id=incident_id, client_id=client_id)
    except Exception as e:
        logger.error("command_resources_websocket_error", incident_id=incident_id, client_id=client_id, error=str(e))
    finally:
        if incident_id in _resources_subscriptions:
            _resources_subscriptions[incident_id].discard(client_id)
            if not _resources_subscriptions[incident_id]:
                del _resources_subscriptions[incident_id]
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/command/timeline/{incident_id}")
async def websocket_command_timeline(
    websocket: WebSocket,
    incident_id: str,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for timeline updates.

    Connect to receive real-time timeline events.

    Path Parameters:
    - **incident_id**: The incident ID to subscribe to

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - timeline_event: New event added to timeline
    - timeline_event_pinned: Event pinned
    - timeline_event_redacted: Event redacted
    - critical_event: Critical priority event
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("command_timeline_websocket_auth_failed", incident_id=incident_id, error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("command_timeline_websocket_rejected", incident_id=incident_id, error=str(e))
        return

    if incident_id not in _timeline_subscriptions:
        _timeline_subscriptions[incident_id] = set()
    _timeline_subscriptions[incident_id].add(client_id)

    logger.info("command_timeline_websocket_connected", incident_id=incident_id, client_id=client_id, user_id=user_id)

    await websocket.send_json({
        "type": "connected",
        "incident_id": incident_id,
        "message": f"Subscribed to timeline updates for incident {incident_id}",
    })

    try:
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
        logger.info("command_timeline_websocket_disconnected", incident_id=incident_id, client_id=client_id)
    except Exception as e:
        logger.error("command_timeline_websocket_error", incident_id=incident_id, client_id=client_id, error=str(e))
    finally:
        if incident_id in _timeline_subscriptions:
            _timeline_subscriptions[incident_id].discard(client_id)
            if not _timeline_subscriptions[incident_id]:
                del _timeline_subscriptions[incident_id]
        await ws_manager.disconnect(client_id)


@router.websocket("/ws/command/briefing/{incident_id}")
async def websocket_command_briefing(
    websocket: WebSocket,
    incident_id: str,
    token: str | None = Query(default=None),
):
    """
    WebSocket endpoint for briefing updates.

    Connect to receive real-time briefing and note updates.

    Path Parameters:
    - **incident_id**: The incident ID to subscribe to

    Query Parameters:
    - **token**: JWT access token for authentication

    Message Types (server -> client):
    - note_added: New command note added
    - note_updated: Note updated
    - note_pinned: Note pinned
    - briefing_generated: New briefing generated
    - briefing_approved: Briefing approved
    """
    ws_manager = get_websocket_manager()
    auth_service = get_auth_service()

    user_id = None
    user_role = None

    if token:
        try:
            payload = await auth_service.validate_token(token)
            user_id = payload.sub
            user_role = payload.role.value
        except Exception as e:
            logger.warning("command_briefing_websocket_auth_failed", incident_id=incident_id, error=str(e))
            await websocket.close(code=4001, reason="Authentication failed")
            return

    try:
        client_id = await ws_manager.connect(
            websocket=websocket, user_id=user_id, user_role=user_role
        )
    except ConnectionError as e:
        logger.warning("command_briefing_websocket_rejected", incident_id=incident_id, error=str(e))
        return

    if incident_id not in _briefing_subscriptions:
        _briefing_subscriptions[incident_id] = set()
    _briefing_subscriptions[incident_id].add(client_id)

    logger.info("command_briefing_websocket_connected", incident_id=incident_id, client_id=client_id, user_id=user_id)

    await websocket.send_json({
        "type": "connected",
        "incident_id": incident_id,
        "message": f"Subscribed to briefing updates for incident {incident_id}",
    })

    try:
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
        logger.info("command_briefing_websocket_disconnected", incident_id=incident_id, client_id=client_id)
    except Exception as e:
        logger.error("command_briefing_websocket_error", incident_id=incident_id, client_id=client_id, error=str(e))
    finally:
        if incident_id in _briefing_subscriptions:
            _briefing_subscriptions[incident_id].discard(client_id)
            if not _briefing_subscriptions[incident_id]:
                del _briefing_subscriptions[incident_id]
        await ws_manager.disconnect(client_id)


# ============================================================================
# Command Operations Broadcast Functions
# ============================================================================


async def broadcast_incident_update(
    incident_id: str,
    update_type: str,
    data: dict,
) -> None:
    """
    Broadcast an incident update to all subscribed clients.

    Args:
        incident_id: The incident ID to broadcast to
        update_type: Type of update
        data: Update data to send
    """
    if incident_id not in _incident_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": update_type,
        "incident_id": incident_id,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_incident_subscriptions[incident_id]):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "incident_update_broadcast_failed",
                incident_id=incident_id,
                client_id=client_id,
                error=str(e),
            )


async def broadcast_ics_update(
    incident_id: str,
    update_type: str,
    data: dict,
) -> None:
    """
    Broadcast an ICS update to all subscribed clients.

    Args:
        incident_id: The incident ID to broadcast to
        update_type: Type of update (ics_role_assigned, ics_role_updated, etc.)
        data: Update data to send
    """
    if incident_id not in _ics_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": update_type,
        "incident_id": incident_id,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_ics_subscriptions[incident_id]):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "ics_update_broadcast_failed",
                incident_id=incident_id,
                client_id=client_id,
                error=str(e),
            )


async def broadcast_strategy_map_update(
    incident_id: str,
    update_type: str,
    data: dict,
) -> None:
    """
    Broadcast a strategy map update to all subscribed clients.

    Args:
        incident_id: The incident ID to broadcast to
        update_type: Type of update
        data: Update data to send
    """
    if incident_id not in _strategy_map_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": update_type,
        "incident_id": incident_id,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_strategy_map_subscriptions[incident_id]):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "strategy_map_update_broadcast_failed",
                incident_id=incident_id,
                client_id=client_id,
                error=str(e),
            )


async def broadcast_resource_update(
    incident_id: str,
    update_type: str,
    data: dict,
) -> None:
    """
    Broadcast a resource update to all subscribed clients.

    Args:
        incident_id: The incident ID to broadcast to
        update_type: Type of update (resource_assigned, resource_released, etc.)
        data: Update data to send
    """
    if incident_id not in _resources_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": update_type,
        "incident_id": incident_id,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_resources_subscriptions[incident_id]):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "resource_update_broadcast_failed",
                incident_id=incident_id,
                client_id=client_id,
                error=str(e),
            )


async def broadcast_timeline_update(
    incident_id: str,
    update_type: str,
    data: dict,
) -> None:
    """
    Broadcast a timeline update to all subscribed clients.

    Args:
        incident_id: The incident ID to broadcast to
        update_type: Type of update (timeline_event, critical_event, etc.)
        data: Update data to send
    """
    if incident_id not in _timeline_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": update_type,
        "incident_id": incident_id,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_timeline_subscriptions[incident_id]):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "timeline_update_broadcast_failed",
                incident_id=incident_id,
                client_id=client_id,
                error=str(e),
            )


async def broadcast_briefing_update(
    incident_id: str,
    update_type: str,
    data: dict,
) -> None:
    """
    Broadcast a briefing update to all subscribed clients.

    Args:
        incident_id: The incident ID to broadcast to
        update_type: Type of update (note_added, briefing_generated, etc.)
        data: Update data to send
    """
    if incident_id not in _briefing_subscriptions:
        return

    ws_manager = get_websocket_manager()
    message = {
        "type": update_type,
        "incident_id": incident_id,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    for client_id in list(_briefing_subscriptions[incident_id]):
        try:
            await ws_manager.send_to_client(client_id, message)
        except Exception as e:
            logger.warning(
                "briefing_update_broadcast_failed",
                incident_id=incident_id,
                client_id=client_id,
                error=str(e),
            )


# ============================================================================
# Command Operations Subscription Helpers
# ============================================================================


def get_incident_subscribers(incident_id: str) -> set[str]:
    """Get the set of client IDs subscribed to an incident."""
    return _incident_subscriptions.get(incident_id, set()).copy()


def get_ics_subscribers(incident_id: str) -> set[str]:
    """Get the set of client IDs subscribed to ICS updates for an incident."""
    return _ics_subscriptions.get(incident_id, set()).copy()


def get_strategy_map_subscribers(incident_id: str) -> set[str]:
    """Get the set of client IDs subscribed to strategy map updates for an incident."""
    return _strategy_map_subscriptions.get(incident_id, set()).copy()


def get_resource_subscribers(incident_id: str) -> set[str]:
    """Get the set of client IDs subscribed to resource updates for an incident."""
    return _resources_subscriptions.get(incident_id, set()).copy()


def get_timeline_subscribers(incident_id: str) -> set[str]:
    """Get the set of client IDs subscribed to timeline updates for an incident."""
    return _timeline_subscriptions.get(incident_id, set()).copy()


def get_briefing_subscribers(incident_id: str) -> set[str]:
    """Get the set of client IDs subscribed to briefing updates for an incident."""
    return _briefing_subscriptions.get(incident_id, set()).copy()


def get_all_command_subscribed_incidents() -> list[str]:
    """Get list of all incidents with active command subscriptions."""
    all_incidents = set()
    all_incidents.update(_incident_subscriptions.keys())
    all_incidents.update(_ics_subscriptions.keys())
    all_incidents.update(_strategy_map_subscriptions.keys())
    all_incidents.update(_resources_subscriptions.keys())
    all_incidents.update(_timeline_subscriptions.keys())
    all_incidents.update(_briefing_subscriptions.keys())
    return list(all_incidents)
