"""
G3TI RTCC-UIP Mobile API Endpoints
REST API for Officer Mobile App and MDT integration.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.mobile import (
    AlertPriority,
    DeviceFingerprint,
    DeviceType,
    MobileAlert,
    MobileMessage,
    UnitStatus,
    UnitStatusUpdate,
    mobile_gateway,
)
from app.mobile.intellisend import (
    IntelPacket,
    intellisend,
)
from app.mobile.safety import (
    CheckIn,
    CheckInType,
    OfficerSafetyStatus,
    ProximityWarning,
    mobile_safety,
)
from app.mobile.telemetry import (
    TelemetryAlert,
    UnitTelemetry,
    telemetry_manager,
)

router = APIRouter(prefix="/api/mobile", tags=["mobile"])


# ============== Request/Response Models ==============

class DeviceRegisterRequest(BaseModel):
    """Device registration request."""
    badge_number: str
    officer_id: str
    device_id: str
    device_type: str = "unknown"
    os_version: str | None = None
    app_version: str | None = None
    hardware_id: str | None = None
    push_token: str | None = None


class LoginRequest(BaseModel):
    """Mobile login request."""
    badge_number: str
    password: str
    device_id: str


class LoginResponse(BaseModel):
    """Mobile login response."""
    success: bool
    session_id: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None
    error: str | None = None


class RefreshTokenRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class SendMessageRequest(BaseModel):
    """Send message request."""
    content: str
    recipient_badges: list[str] = Field(default_factory=list)
    recipient_units: list[str] = Field(default_factory=list)
    channel: str | None = None
    priority: str = "medium"
    attachments: list[str] = Field(default_factory=list)


class UpdateStatusRequest(BaseModel):
    """Unit status update request."""
    unit_id: str
    status: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    call_id: str | None = None
    notes: str | None = None


class CheckInRequest(BaseModel):
    """Officer check-in request."""
    check_in_type: str = "routine"
    latitude: float | None = None
    longitude: float | None = None
    location_description: str | None = None
    notes: str | None = None
    call_id: str | None = None


class GPSUpdateRequest(BaseModel):
    """GPS update request."""
    unit_id: str
    latitude: float
    longitude: float
    altitude: float | None = None
    accuracy_meters: float | None = None
    heading: float | None = None
    speed_mps: float | None = None


class SendIntelRequest(BaseModel):
    """Send intel packet request."""
    packet_id: str
    recipient_badges: list[str]


# ============== Authentication Endpoints ==============

@router.post("/auth/device-register", response_model=dict)
async def register_device(request: DeviceRegisterRequest) -> dict[str, Any]:
    """Register a mobile device."""
    fingerprint = DeviceFingerprint(
        device_id=request.device_id,
        device_type=DeviceType(request.device_type) if request.device_type in [e.value for e in DeviceType] else DeviceType.UNKNOWN,
        os_version=request.os_version,
        app_version=request.app_version,
        hardware_id=request.hardware_id,
    )

    device = await mobile_gateway.register_device(
        badge_number=request.badge_number,
        officer_id=request.officer_id,
        fingerprint=fingerprint,
        push_token=request.push_token,
    )

    if not device:
        raise HTTPException(status_code=400, detail="Failed to register device")

    return {
        "success": True,
        "device_id": device.id,
        "device_token": device.device_token,
        "status": device.status,
    }


@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Authenticate officer and create session."""
    # Find device by device_id in fingerprint
    devices = await mobile_gateway.get_devices_for_badge(request.badge_number)
    device = next((d for d in devices if d.device_fingerprint.device_id == request.device_id), None)

    if not device:
        return LoginResponse(success=False, error="Device not registered")

    session = await mobile_gateway.authenticate(
        badge_number=request.badge_number,
        password=request.password,
        device_id=device.id,
    )

    if not session:
        return LoginResponse(success=False, error="Authentication failed")

    return LoginResponse(
        success=True,
        session_id=session.id,
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expires_at=session.expires_at,
    )


@router.post("/auth/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshTokenRequest) -> LoginResponse:
    """Refresh authentication token."""
    session = await mobile_gateway.refresh_session(request.refresh_token)

    if not session:
        return LoginResponse(success=False, error="Invalid refresh token")

    return LoginResponse(
        success=True,
        session_id=session.id,
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expires_at=session.expires_at,
    )


@router.post("/auth/logout")
async def logout(session_id: str) -> dict[str, bool]:
    """Logout and invalidate session."""
    success = await mobile_gateway.logout(session_id)
    return {"success": success}


# ============== Alerts Endpoints ==============

@router.get("/alerts", response_model=list[MobileAlert])
async def get_alerts(
    badge_number: str,
    unit_id: str | None = None,
    limit: int = Query(default=50, le=100),
    include_read: bool = False,
) -> list[MobileAlert]:
    """Get alerts for an officer."""
    return await mobile_gateway.get_alerts(
        badge_number=badge_number,
        unit_id=unit_id,
        limit=limit,
        include_read=include_read,
    )


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str, badge_number: str) -> dict[str, bool]:
    """Mark an alert as read."""
    success = await mobile_gateway.mark_alert_read(alert_id, badge_number)
    return {"success": success}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, badge_number: str) -> dict[str, bool]:
    """Acknowledge an alert."""
    success = await mobile_gateway.acknowledge_alert(alert_id, badge_number)
    return {"success": success}


# ============== Dispatch Endpoints ==============

@router.get("/dispatch/active")
async def get_active_dispatch(
    badge_number: str | None = None,
    unit_id: str | None = None,
) -> list[dict[str, Any]]:
    """Get active dispatch calls."""
    calls = await mobile_gateway.get_active_dispatch(
        badge_number=badge_number,
        unit_id=unit_id,
    )
    return [call.model_dump() for call in calls]


# ============== Messaging Endpoints ==============

@router.get("/messages/feed", response_model=list[MobileMessage])
async def get_messages(
    badge_number: str,
    unit_id: str | None = None,
    channel: str | None = None,
    limit: int = Query(default=100, le=500),
    since: datetime | None = None,
) -> list[MobileMessage]:
    """Get messages for an officer."""
    return await mobile_gateway.get_messages(
        badge_number=badge_number,
        unit_id=unit_id,
        channel=channel,
        limit=limit,
        since=since,
    )


@router.post("/messages/send", response_model=MobileMessage)
async def send_message(
    badge_number: str,
    officer_name: str,
    request: SendMessageRequest,
) -> MobileMessage:
    """Send a message."""
    priority = AlertPriority(request.priority) if request.priority in [e.value for e in AlertPriority] else AlertPriority.MEDIUM

    return await mobile_gateway.send_message(
        sender_badge=badge_number,
        sender_name=officer_name,
        content=request.content,
        recipient_badges=request.recipient_badges,
        recipient_units=request.recipient_units,
        channel=request.channel,
        priority=priority,
        attachments=request.attachments,
    )


# ============== Unit Status Endpoints ==============

@router.get("/unit/status", response_model=UnitStatusUpdate | None)
async def get_unit_status(badge_number: str) -> UnitStatusUpdate | None:
    """Get unit status for a badge."""
    return await mobile_gateway.get_unit_status(badge_number)


@router.post("/unit/status/update", response_model=UnitStatusUpdate)
async def update_unit_status(
    badge_number: str,
    request: UpdateStatusRequest,
) -> UnitStatusUpdate:
    """Update unit status."""
    status = UnitStatus(request.status) if request.status in [e.value for e in UnitStatus] else UnitStatus.AVAILABLE

    return await mobile_gateway.update_unit_status(
        badge_number=badge_number,
        unit_id=request.unit_id,
        status=status,
        location=request.location,
        latitude=request.latitude,
        longitude=request.longitude,
        call_id=request.call_id,
        notes=request.notes,
    )


# ============== Intel Feed Endpoints ==============

@router.get("/intel/feed")
async def get_intel_feed(
    badge_number: str,
    limit: int = Query(default=50, le=100),
    intel_type: str | None = None,
    since: datetime | None = None,
) -> list[dict[str, Any]]:
    """Get intelligence feed items."""
    items = await mobile_gateway.get_intel_feed(
        badge_number=badge_number,
        limit=limit,
        intel_type=intel_type,
        since=since,
    )
    return [item.model_dump() for item in items]


@router.get("/intel/{packet_id}", response_model=IntelPacket | None)
async def get_intel_packet(packet_id: str) -> IntelPacket | None:
    """Get a specific intel packet."""
    return await intellisend.get_packet(packet_id)


@router.post("/intel/send")
async def send_intel_packet(request: SendIntelRequest) -> dict[str, Any]:
    """Send an intel packet to recipients."""
    deliveries = await intellisend.send_packet(
        packet_id=request.packet_id,
        recipient_badges=request.recipient_badges,
    )
    return {
        "success": len(deliveries) > 0,
        "delivery_count": len(deliveries),
    }


@router.post("/intel/{packet_id}/read")
async def mark_intel_read(packet_id: str, badge_number: str) -> dict[str, bool]:
    """Mark an intel packet as read."""
    delivery = await intellisend.mark_read(packet_id, badge_number)
    return {"success": delivery is not None}


@router.post("/intel/{packet_id}/acknowledge")
async def acknowledge_intel(packet_id: str, badge_number: str) -> dict[str, bool]:
    """Acknowledge an intel packet."""
    delivery = await intellisend.acknowledge_packet(packet_id, badge_number)
    return {"success": delivery is not None}


# ============== Safety Endpoints ==============

@router.get("/safety/status", response_model=OfficerSafetyStatus)
async def get_safety_status(badge_number: str) -> OfficerSafetyStatus:
    """Get officer safety status."""
    return await mobile_safety.get_safety_status(badge_number)


@router.post("/safety/checkin", response_model=CheckIn)
async def check_in(
    badge_number: str,
    request: CheckInRequest,
    device_id: str | None = None,
) -> CheckIn:
    """Record officer check-in."""
    check_in_type = CheckInType(request.check_in_type) if request.check_in_type in [e.value for e in CheckInType] else CheckInType.ROUTINE

    return await mobile_safety.check_in(
        badge_number=badge_number,
        check_in_type=check_in_type,
        latitude=request.latitude,
        longitude=request.longitude,
        location_description=request.location_description,
        notes=request.notes,
        call_id=request.call_id,
        device_id=device_id,
    )


@router.get("/safety/warnings", response_model=list[ProximityWarning])
async def get_proximity_warnings(
    badge_number: str,
    include_acknowledged: bool = False,
) -> list[ProximityWarning]:
    """Get proximity warnings for an officer."""
    return await mobile_safety.get_proximity_warnings(
        badge_number=badge_number,
        include_acknowledged=include_acknowledged,
    )


@router.post("/safety/warnings/{warning_id}/acknowledge")
async def acknowledge_warning(
    warning_id: str,
    badge_number: str,
) -> dict[str, bool]:
    """Acknowledge a proximity warning."""
    success = await mobile_safety.acknowledge_warning(badge_number, warning_id)
    return {"success": success}


# ============== Telemetry Endpoints ==============

@router.post("/telemetry/gps", response_model=dict)
async def update_gps(
    badge_number: str,
    request: GPSUpdateRequest,
    device_id: str = "",
) -> dict[str, Any]:
    """Update GPS location."""
    telemetry = await telemetry_manager.update_gps(
        badge_number=badge_number,
        unit_id=request.unit_id,
        device_id=device_id,
        latitude=request.latitude,
        longitude=request.longitude,
        altitude=request.altitude,
        accuracy_meters=request.accuracy_meters,
        heading=request.heading,
        speed_mps=request.speed_mps,
    )
    return {
        "success": True,
        "telemetry_id": telemetry.id,
        "last_update": telemetry.last_update.isoformat(),
    }


@router.get("/telemetry/unit/{badge_number}", response_model=UnitTelemetry | None)
async def get_unit_telemetry(badge_number: str) -> UnitTelemetry | None:
    """Get telemetry for a unit."""
    return await telemetry_manager.get_telemetry(badge_number)


@router.get("/telemetry/alerts", response_model=list[TelemetryAlert])
async def get_telemetry_alerts(
    badge_number: str,
    include_acknowledged: bool = False,
) -> list[TelemetryAlert]:
    """Get telemetry alerts for a unit."""
    return await telemetry_manager.get_alerts(
        badge_number=badge_number,
        include_acknowledged=include_acknowledged,
    )


# ============== Incident Endpoints (Phase 8 Integration) ==============

@router.get("/incident/{incident_id}")
async def get_incident_summary(incident_id: str) -> dict[str, Any]:
    """Get incident summary for mobile display."""
    # This would integrate with Phase 8 command module
    return {
        "incident_id": incident_id,
        "status": "active",
        "message": "Incident details would be fetched from Phase 8 command module",
    }


@router.get("/incident/timeline/{incident_id}")
async def get_incident_timeline(incident_id: str) -> dict[str, Any]:
    """Get incident timeline for mobile display."""
    # This would integrate with Phase 8 command module
    return {
        "incident_id": incident_id,
        "events": [],
        "message": "Timeline would be fetched from Phase 8 command module",
    }
