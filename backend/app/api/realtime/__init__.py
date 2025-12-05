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
