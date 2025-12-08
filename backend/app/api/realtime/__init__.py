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
