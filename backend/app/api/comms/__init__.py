"""
G3TI RTCC-UIP Communications API Endpoints.

Phase 7: Notifications, Dispatch & Communication Suite

Provides REST API endpoints for:
- In-app messaging
- CAD dispatch overlay
- Push alerts
- Bulletins
- Scene coordination
- Notification rules
"""

from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.comms.alerts import (
    AlertPriority,
    AlertsManager,
    AlertType,
    DeliveryChannel,
)
from app.comms.bulletins import (
    BulletinManager,
    BulletinPriority,
    BulletinType,
    LinkedEntity,
)
from app.comms.dispatch_overlay import (
    CallPriority,
    CallType,
    DispatchOverlayEngine,
)
from app.comms.messaging import (
    ChannelType,
    MessagePriority,
    MessageType,
    MessagingManager,
)
from app.comms.rules_engine import (
    NotificationRulesEngine,
)
from app.comms.scene_coordination import (
    SceneCoordinationManager,
    TacticalRole,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/comms", tags=["communications"])

# Initialize managers (would be dependency injected in production)
_messaging_manager: MessagingManager | None = None
_dispatch_engine: DispatchOverlayEngine | None = None
_alerts_manager: AlertsManager | None = None
_bulletin_manager: BulletinManager | None = None
_scene_manager: SceneCoordinationManager | None = None
_rules_engine: NotificationRulesEngine | None = None


def get_messaging_manager() -> MessagingManager:
    global _messaging_manager
    if _messaging_manager is None:
        _messaging_manager = MessagingManager()
    return _messaging_manager


def get_dispatch_engine() -> DispatchOverlayEngine:
    global _dispatch_engine
    if _dispatch_engine is None:
        _dispatch_engine = DispatchOverlayEngine()
    return _dispatch_engine


def get_alerts_manager() -> AlertsManager:
    global _alerts_manager
    if _alerts_manager is None:
        _alerts_manager = AlertsManager()
    return _alerts_manager


def get_bulletin_manager() -> BulletinManager:
    global _bulletin_manager
    if _bulletin_manager is None:
        _bulletin_manager = BulletinManager()
    return _bulletin_manager


def get_scene_manager() -> SceneCoordinationManager:
    global _scene_manager
    if _scene_manager is None:
        _scene_manager = SceneCoordinationManager()
    return _scene_manager


def get_rules_engine() -> NotificationRulesEngine:
    global _rules_engine
    if _rules_engine is None:
        _rules_engine = NotificationRulesEngine()
    return _rules_engine


# ============================================================================
# Request/Response Models
# ============================================================================

class SendMessageRequest(BaseModel):
    """Request to send a message."""
    channel_id: str
    content: str
    message_type: str = "text"
    recipient_id: str | None = None
    thread_id: str | None = None
    reply_to_id: str | None = None
    priority: str = "normal"
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateChannelRequest(BaseModel):
    """Request to create a channel."""
    name: str
    channel_type: str
    description: str | None = None
    members: list[str] = Field(default_factory=list)
    incident_id: str | None = None
    shift: str | None = None
    unit: str | None = None


class PushAlertRequest(BaseModel):
    """Request to send a push alert."""
    alert_type: str
    title: str
    body: str
    priority: str = "normal"
    target_badges: list[str] = Field(default_factory=list)
    target_units: list[str] = Field(default_factory=list)
    target_shifts: list[str] = Field(default_factory=list)
    target_districts: list[str] = Field(default_factory=list)
    broadcast_all: bool = False
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    channels: list[str] = Field(default_factory=lambda: ["push"])
    requires_acknowledgment: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateBulletinRequest(BaseModel):
    """Request to create a bulletin."""
    bulletin_type: str
    title: str
    summary: str
    body: str | None = None
    priority: str = "normal"
    key_points: list[str] = Field(default_factory=list)
    entities: list[dict[str, Any]] = Field(default_factory=list)
    target_shifts: list[str] = Field(default_factory=list)
    target_districts: list[str] = Field(default_factory=list)
    recommended_units: list[str] = Field(default_factory=list)
    broadcast_all: bool = False
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    recommended_actions: list[str] = Field(default_factory=list)
    auto_publish: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateSceneRequest(BaseModel):
    """Request to create a coordinated scene."""
    incident_id: str
    incident_type: str
    address: str
    latitude: float | None = None
    longitude: float | None = None
    threat_level: str = "unknown"
    primary_radio_channel: str | None = None
    tactical_radio_channel: str | None = None


class AssignUnitRequest(BaseModel):
    """Request to assign a unit to a scene."""
    unit_id: str
    role: str = "unassigned"
    badge: str | None = None
    officer_name: str | None = None
    position_description: str | None = None


class UpdateRoleRequest(BaseModel):
    """Request to update a unit's role."""
    new_role: str
    position_description: str | None = None


class TestRuleRequest(BaseModel):
    """Request to test a rule."""
    context: dict[str, Any]


# ============================================================================
# Messaging Endpoints
# ============================================================================

@router.post("/message/send")
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Send a message to a channel or recipient."""
    manager = get_messaging_manager()

    message = await manager.send_message(
        sender_id=current_user.get("sub", "unknown"),
        sender_name=current_user.get("name", "Unknown User"),
        sender_type=current_user.get("role", "officer"),
        channel_id=request.channel_id,
        content=request.content,
        message_type=MessageType(request.message_type),
        recipient_id=request.recipient_id,
        thread_id=request.thread_id,
        reply_to_id=request.reply_to_id,
        priority=MessagePriority(request.priority),
        attachments=request.attachments,
        metadata=request.metadata,
    )

    return {"status": "sent", "message": message.model_dump()}


@router.get("/message/feed/{channel_id}")
async def get_message_feed(
    channel_id: str,
    limit: int = Query(default=50, le=100),
    before: datetime | None = None,
    after: datetime | None = None,
    thread_id: str | None = None,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get messages from a channel."""
    manager = get_messaging_manager()

    messages = await manager.get_channel_messages(
        channel_id=channel_id,
        limit=limit,
        before=before,
        after=after,
        thread_id=thread_id,
    )

    return {
        "channel_id": channel_id,
        "messages": [m.model_dump() for m in messages],
        "count": len(messages),
    }


@router.post("/channel/create")
async def create_channel(
    request: CreateChannelRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Create a new messaging channel."""
    manager = get_messaging_manager()

    channel = await manager.create_channel(
        name=request.name,
        channel_type=ChannelType(request.channel_type),
        created_by=current_user.get("sub", "unknown"),
        description=request.description,
        members=request.members,
        incident_id=request.incident_id,
        shift=request.shift,
        unit=request.unit,
    )

    return {"status": "created", "channel": channel.model_dump()}


@router.get("/channels")
async def get_user_channels(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get channels for the current user."""
    manager = get_messaging_manager()

    channels = await manager.get_user_channels(current_user.get("sub", "unknown"))

    return {
        "channels": [c.model_dump() for c in channels],
        "count": len(channels),
    }


@router.post("/message/{message_id}/read")
async def mark_message_read(
    message_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Mark a message as read."""
    manager = get_messaging_manager()

    receipt = await manager.mark_message_read(
        message_id=message_id,
        user_id=current_user.get("sub", "unknown"),
    )

    return {"status": "read", "receipt": receipt.model_dump()}


# ============================================================================
# Dispatch Endpoints
# ============================================================================

@router.get("/dispatch/active")
async def get_active_calls(
    priority: str | None = None,
    call_type: str | None = None,
    district: str | None = None,
    beat: str | None = None,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get active CAD calls."""
    engine = get_dispatch_engine()

    calls = await engine.get_active_calls(
        priority=CallPriority(priority) if priority else None,
        call_type=CallType(call_type) if call_type else None,
        district=district,
        beat=beat,
    )

    return {
        "calls": [c.model_dump() for c in calls],
        "count": len(calls),
    }


@router.get("/dispatch/call/{cad_id}")
async def get_call(
    cad_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get a specific CAD call."""
    engine = get_dispatch_engine()

    call = await engine.get_call_by_cad_id(cad_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    return {"call": call.model_dump()}


@router.get("/dispatch/units")
async def get_units(
    district: str | None = None,
    beat: str | None = None,
    shift: str | None = None,
    available_only: bool = False,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get dispatch units."""
    engine = get_dispatch_engine()

    if available_only:
        units = await engine.get_available_units(
            district=district,
            beat=beat,
            shift=shift,
        )
    else:
        units = await engine.get_all_units()
        if district:
            units = [u for u in units if u.district == district]
        if beat:
            units = [u for u in units if u.beat == beat]
        if shift:
            units = [u for u in units if u.shift == shift]

    return {
        "units": [u.model_dump() for u in units],
        "count": len(units),
    }


@router.get("/dispatch/statistics")
async def get_dispatch_statistics(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get dispatch statistics."""
    engine = get_dispatch_engine()
    return await engine.get_call_statistics()


# ============================================================================
# Alerts Endpoints
# ============================================================================

@router.post("/alerts/push")
async def push_alert(
    request: PushAlertRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Send a push alert."""
    manager = get_alerts_manager()

    alert = await manager.create_alert(
        alert_type=AlertType(request.alert_type),
        title=request.title,
        body=request.body,
        priority=AlertPriority(request.priority),
        target_badges=request.target_badges,
        target_units=request.target_units,
        target_shifts=request.target_shifts,
        target_districts=request.target_districts,
        broadcast_all=request.broadcast_all,
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address,
        channels=[DeliveryChannel(c) for c in request.channels],
        requires_acknowledgment=request.requires_acknowledgment,
        source=current_user.get("role", "rtcc"),
        metadata=request.metadata,
    )

    return {"status": "sent", "alert": alert.model_dump()}


@router.get("/alerts/history/{badge}")
async def get_alert_history(
    badge: str,
    limit: int = Query(default=50, le=100),
    include_read: bool = False,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get alert history for an officer."""
    manager = get_alerts_manager()

    alerts = await manager.get_alerts_for_badge(
        badge=badge,
        limit=limit,
        include_read=include_read,
    )

    return {
        "badge": badge,
        "alerts": [a.model_dump() for a in alerts],
        "count": len(alerts),
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Acknowledge an alert."""
    manager = get_alerts_manager()

    badge = current_user.get("badge", current_user.get("sub", "unknown"))
    alert = await manager.acknowledge_alert(alert_id, badge)

    return {"status": "acknowledged", "alert": alert.model_dump()}


# ============================================================================
# Bulletins Endpoints
# ============================================================================

@router.post("/bulletins/create")
async def create_bulletin(
    request: CreateBulletinRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Create a new bulletin."""
    manager = get_bulletin_manager()

    entities = [LinkedEntity(**e) for e in request.entities] if request.entities else None

    bulletin = await manager.create_bulletin(
        bulletin_type=BulletinType(request.bulletin_type),
        title=request.title,
        summary=request.summary,
        body=request.body,
        priority=BulletinPriority(request.priority),
        key_points=request.key_points,
        entities=entities,
        target_shifts=request.target_shifts,
        target_districts=request.target_districts,
        recommended_units=request.recommended_units,
        broadcast_all=request.broadcast_all,
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address,
        recommended_actions=request.recommended_actions,
        created_by=current_user.get("sub", "unknown"),
        auto_publish=request.auto_publish,
        metadata=request.metadata,
    )

    return {"status": "created", "bulletin": bulletin.model_dump()}


@router.get("/bulletins/feed")
async def get_bulletin_feed(
    bulletin_type: str | None = None,
    priority: str | None = None,
    shift: str | None = None,
    district: str | None = None,
    limit: int = Query(default=50, le=100),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get bulletin feed."""
    manager = get_bulletin_manager()

    bulletins = await manager.get_bulletin_feed(
        bulletin_type=BulletinType(bulletin_type) if bulletin_type else None,
        priority=BulletinPriority(priority) if priority else None,
        shift=shift,
        district=district,
        limit=limit,
    )

    return {
        "bulletins": [b.model_dump() for b in bulletins],
        "count": len(bulletins),
    }


@router.get("/bulletins/{bulletin_id}")
async def get_bulletin(
    bulletin_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get a specific bulletin."""
    manager = get_bulletin_manager()

    bulletin = await manager.get_bulletin(bulletin_id)
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin not found")

    # Increment view count
    await manager.increment_view_count(bulletin_id)

    return {"bulletin": bulletin.model_dump()}


@router.post("/bulletins/{bulletin_id}/publish")
async def publish_bulletin(
    bulletin_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Publish a bulletin."""
    manager = get_bulletin_manager()

    bulletin = await manager.publish_bulletin(
        bulletin_id=bulletin_id,
        approved_by=current_user.get("sub", "unknown"),
    )

    return {"status": "published", "bulletin": bulletin.model_dump()}


@router.post("/bulletins/{bulletin_id}/acknowledge")
async def acknowledge_bulletin(
    bulletin_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Acknowledge a bulletin."""
    manager = get_bulletin_manager()

    badge = current_user.get("badge", current_user.get("sub", "unknown"))
    bulletin = await manager.acknowledge_bulletin(bulletin_id, badge)

    return {"status": "acknowledged", "bulletin": bulletin.model_dump()}


# ============================================================================
# Scene Coordination Endpoints
# ============================================================================

@router.post("/scene/create")
async def create_scene(
    request: CreateSceneRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Create a coordinated scene."""
    manager = get_scene_manager()

    scene = await manager.create_scene(
        incident_id=request.incident_id,
        incident_type=request.incident_type,
        address=request.address,
        latitude=request.latitude,
        longitude=request.longitude,
        threat_level=request.threat_level,
        created_by=current_user.get("sub", "unknown"),
        primary_radio_channel=request.primary_radio_channel,
        tactical_radio_channel=request.tactical_radio_channel,
    )

    return {"status": "created", "scene": scene.model_dump()}


@router.post("/scene/{scene_id}/assign_unit")
async def assign_unit_to_scene(
    scene_id: str,
    request: AssignUnitRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Assign a unit to a scene."""
    manager = get_scene_manager()

    scene, unit = await manager.assign_unit(
        scene_id=scene_id,
        unit_id=request.unit_id,
        role=TacticalRole(request.role),
        badge=request.badge,
        officer_name=request.officer_name,
        position_description=request.position_description,
        assigned_by=current_user.get("sub", "unknown"),
    )

    return {
        "status": "assigned",
        "scene": scene.model_dump(),
        "unit": unit.model_dump(),
    }


@router.post("/scene/{scene_id}/update_role")
async def update_unit_role(
    scene_id: str,
    unit_id: str,
    request: UpdateRoleRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Update a unit's role on a scene."""
    manager = get_scene_manager()

    scene, unit = await manager.update_unit_role(
        scene_id=scene_id,
        unit_id=unit_id,
        new_role=TacticalRole(request.new_role),
        position_description=request.position_description,
        updated_by=current_user.get("sub", "unknown"),
    )

    return {
        "status": "updated",
        "scene": scene.model_dump(),
        "unit": unit.model_dump(),
    }


@router.get("/scene/status/{incident_id}")
async def get_scene_status(
    incident_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get scene status by incident ID."""
    manager = get_scene_manager()

    scene = await manager.get_scene_by_incident(incident_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    status = await manager.get_scene_status(scene.id)
    return status


@router.get("/scene/{scene_id}")
async def get_scene(
    scene_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get a specific scene."""
    manager = get_scene_manager()

    scene = await manager.get_scene(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    return {"scene": scene.model_dump()}


@router.get("/scenes/active")
async def get_active_scenes(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get all active scenes."""
    manager = get_scene_manager()

    scenes = await manager.get_active_scenes()

    return {
        "scenes": [s.model_dump() for s in scenes],
        "count": len(scenes),
    }


# ============================================================================
# Rules Engine Endpoints
# ============================================================================

@router.get("/rules")
async def get_rules(
    include_system: bool = True,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get all notification rules."""
    engine = get_rules_engine()

    rules = engine.get_all_rules(include_system=include_system)

    return {
        "rules": [r.model_dump() for r in rules],
        "count": len(rules),
    }


@router.get("/rules/{rule_id}")
async def get_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get a specific rule."""
    engine = get_rules_engine()

    rule = engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return {"rule": rule.model_dump()}


@router.post("/rules/test-trigger")
async def test_rule_trigger(
    rule_id: str,
    request: TestRuleRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Test a rule against a context without executing actions."""
    engine = get_rules_engine()

    result = await engine.test_rule(rule_id, request.context)

    return result


@router.post("/rules/{rule_id}/toggle")
async def toggle_rule(
    rule_id: str,
    is_active: bool,
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Toggle a rule's active status."""
    engine = get_rules_engine()

    rule = await engine.toggle_rule(rule_id, is_active)

    return {"status": "toggled", "rule": rule.model_dump()}


@router.get("/rules/history")
async def get_rule_trigger_history(
    rule_id: str | None = None,
    limit: int = Query(default=100, le=500),
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Get rule trigger history."""
    engine = get_rules_engine()

    events = engine.get_trigger_history(rule_id=rule_id, limit=limit)

    return {
        "events": [e.model_dump() for e in events],
        "count": len(events),
    }


# ============================================================================
# WebSocket Endpoints
# ============================================================================

# Store for WebSocket connections
_comms_connections: dict[str, set[WebSocket]] = {}
_dispatch_connections: set[WebSocket] = set()
_bulletin_connections: set[WebSocket] = set()
_scene_connections: dict[str, set[WebSocket]] = {}


@router.websocket("/ws/comms/{channel_id}")
async def websocket_comms(
    websocket: WebSocket,
    channel_id: str,
):
    """WebSocket endpoint for real-time messaging."""
    await websocket.accept()

    if channel_id not in _comms_connections:
        _comms_connections[channel_id] = set()
    _comms_connections[channel_id].add(websocket)

    logger.info("comms_websocket_connected", channel_id=channel_id)

    try:
        while True:
            data = await websocket.receive_json()

            # Handle typing indicators
            if data.get("type") == "typing":
                await broadcast_to_channel(
                    channel_id,
                    {
                        "type": "typing_indicator",
                        "user_id": data.get("user_id"),
                        "user_name": data.get("user_name"),
                        "is_typing": data.get("is_typing", True),
                    },
                    exclude=websocket,
                )

            # Handle read receipts
            elif data.get("type") == "read":
                await broadcast_to_channel(
                    channel_id,
                    {
                        "type": "read_receipt",
                        "message_id": data.get("message_id"),
                        "user_id": data.get("user_id"),
                    },
                    exclude=websocket,
                )

    except WebSocketDisconnect:
        _comms_connections[channel_id].discard(websocket)
        logger.info("comms_websocket_disconnected", channel_id=channel_id)


@router.websocket("/ws/dispatch")
async def websocket_dispatch(websocket: WebSocket):
    """WebSocket endpoint for dispatch updates."""
    await websocket.accept()
    _dispatch_connections.add(websocket)

    logger.info("dispatch_websocket_connected")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _dispatch_connections.discard(websocket)
        logger.info("dispatch_websocket_disconnected")


@router.websocket("/ws/bulletins")
async def websocket_bulletins(websocket: WebSocket):
    """WebSocket endpoint for bulletin updates."""
    await websocket.accept()
    _bulletin_connections.add(websocket)

    logger.info("bulletins_websocket_connected")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _bulletin_connections.discard(websocket)
        logger.info("bulletins_websocket_disconnected")


@router.websocket("/ws/scene/{scene_id}")
async def websocket_scene(
    websocket: WebSocket,
    scene_id: str,
):
    """WebSocket endpoint for scene coordination updates."""
    await websocket.accept()

    if scene_id not in _scene_connections:
        _scene_connections[scene_id] = set()
    _scene_connections[scene_id].add(websocket)

    logger.info("scene_websocket_connected", scene_id=scene_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _scene_connections[scene_id].discard(websocket)
        logger.info("scene_websocket_disconnected", scene_id=scene_id)


# ============================================================================
# Broadcast Functions
# ============================================================================

async def broadcast_to_channel(
    channel_id: str,
    message: dict[str, Any],
    exclude: WebSocket | None = None,
) -> None:
    """Broadcast a message to all connections in a channel."""
    connections = _comms_connections.get(channel_id, set())
    for conn in connections:
        if conn != exclude:
            try:
                await conn.send_json(message)
            except Exception:
                pass


async def broadcast_dispatch_event(event: dict[str, Any]) -> None:
    """Broadcast a dispatch event to all connections."""
    for conn in _dispatch_connections:
        try:
            await conn.send_json(event)
        except Exception:
            pass


async def broadcast_bulletin(bulletin: dict[str, Any]) -> None:
    """Broadcast a bulletin to all connections."""
    for conn in _bulletin_connections:
        try:
            await conn.send_json({"type": "new_bulletin", "bulletin": bulletin})
        except Exception:
            pass


async def broadcast_scene_event(
    scene_id: str,
    event: dict[str, Any],
) -> None:
    """Broadcast a scene event to all connections for that scene."""
    connections = _scene_connections.get(scene_id, set())
    for conn in connections:
        try:
            await conn.send_json(event)
        except Exception:
            pass


# Export router
__all__ = ["router"]
