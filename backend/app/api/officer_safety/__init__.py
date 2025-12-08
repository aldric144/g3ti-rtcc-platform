"""
Officer Safety API Endpoints

REST API endpoints for officer safety and situational awareness operations.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.officer_safety import OfficerSafetyManager
from app.officer_safety.officer_safety_manager import get_officer_safety_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/officer", tags=["Officer Safety"])


# Request/Response Models
class LocationUpdate(BaseModel):
    """Officer location update request."""
    badge: str = Field(..., description="Officer badge number")
    unit: str = Field(..., description="Unit identifier")
    location: list[float] = Field(..., description="[latitude, longitude]")
    speed: float | None = Field(None, description="Speed in mph")
    heading: float | None = Field(None, description="Heading in degrees")
    status: str = Field("on_patrol", description="Officer status")


class SafetyScoreResponse(BaseModel):
    """Officer safety score response."""
    badge: str
    score: float
    level: str
    factors: list[str]
    location: dict[str, float]
    calculated_at: str


class PerimeterRequest(BaseModel):
    """Perimeter generation request."""
    incident_id: str = Field(..., description="Incident identifier")
    units: list[str] = Field(..., description="List of unit identifiers")
    location: list[float] = Field(..., description="[latitude, longitude]")
    incident_type: str | None = Field(None, description="Type of incident")
    suspect_info: dict | None = Field(None, description="Suspect information")
    weapons_info: list[dict] | None = Field(None, description="Weapons information")


class EmergencyTrigger(BaseModel):
    """Emergency trigger request."""
    badge: str = Field(..., description="Officer badge number")
    source: str = Field("manual", description="Source of trigger")
    details: dict | None = Field(None, description="Additional details")


class EmergencyClear(BaseModel):
    """Emergency clear request."""
    badge: str = Field(..., description="Officer badge number")
    cleared_by: str | None = Field(None, description="Who cleared the emergency")
    reason: str | None = Field(None, description="Reason for clearing")


# Dependency
def get_manager() -> OfficerSafetyManager:
    """Get officer safety manager instance."""
    return get_officer_safety_manager()


# Endpoints
@router.get("/safety/{badge}")
async def get_officer_safety(
    badge: str,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get safety score for an officer.

    Returns safety score with risk level and contributing factors.
    """
    logger.info("get_officer_safety_request", badge=badge)

    try:
        # Get officer's current position
        position = await manager.telemetry.get_position(badge)

        if not position:
            raise HTTPException(
                status_code=404,
                detail=f"No position data for officer {badge}",
            )

        # Calculate safety score
        result = await manager.safety_scorer.calculate_score(
            badge=badge,
            lat=position["lat"],
            lon=position["lon"],
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_officer_safety_error", badge=badge, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status/{badge}")
async def get_officer_status(
    badge: str,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get comprehensive status for an officer.

    Returns location, safety score, and active threats.
    """
    logger.info("get_officer_status_request", badge=badge)

    try:
        result = await manager.get_officer_status(badge)
        return result

    except Exception as e:
        logger.error("get_officer_status_error", badge=badge, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/all")
async def get_all_officers(
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get status for all active officers.

    Returns list of all officers with their current status.
    """
    logger.info("get_all_officers_request")

    try:
        officers = await manager.get_all_officers()
        return {
            "officers": officers,
            "count": len(officers),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("get_all_officers_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/threats/{badge}")
async def get_officer_threats(
    badge: str,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get threats for an officer.

    Returns all threats within proximity of the officer.
    """
    logger.info("get_officer_threats_request", badge=badge)

    try:
        # Get officer's current position
        position = await manager.telemetry.get_position(badge)

        if not position:
            raise HTTPException(
                status_code=404,
                detail=f"No position data for officer {badge}",
            )

        # Evaluate threats
        result = await manager.threat_engine.evaluate_threats(
            badge=badge,
            lat=position["lat"],
            lon=position["lon"],
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_officer_threats_error", badge=badge, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sceneintel")
async def get_scene_intelligence_by_address(
    address: str = Query(..., description="Street address"),
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get scene intelligence for an address.

    Returns RTCC Field Packet with comprehensive scene intelligence.
    """
    logger.info("get_scene_intel_request", address=address)

    try:
        result = await manager.get_scene_intelligence(address=address)
        return result

    except Exception as e:
        logger.error("get_scene_intel_error", address=address, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sceneintel/incident/{incident_id}")
async def get_scene_intelligence_by_incident(
    incident_id: str,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get scene intelligence for an incident.

    Returns RTCC Field Packet with comprehensive scene intelligence.
    """
    logger.info("get_scene_intel_incident_request", incident_id=incident_id)

    try:
        result = await manager.get_scene_intelligence(incident_id=incident_id)
        return result

    except Exception as e:
        logger.error("get_scene_intel_incident_error", incident_id=incident_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sceneintel/location")
async def get_scene_intelligence_by_location(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get scene intelligence for coordinates.

    Returns RTCC Field Packet with comprehensive scene intelligence.
    """
    logger.info("get_scene_intel_location_request", lat=lat, lon=lon)

    try:
        result = await manager.get_scene_intelligence(lat=lat, lon=lon)
        return result

    except Exception as e:
        logger.error("get_scene_intel_location_error", lat=lat, lon=lon, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/perimeter")
async def generate_perimeter(
    request: PerimeterRequest,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Generate tactical perimeter for an incident.

    Returns perimeter boundaries, approach routes, and staging areas.
    """
    logger.info(
        "generate_perimeter_request",
        incident_id=request.incident_id,
        location=request.location,
    )

    try:
        result = await manager.generate_perimeter(
            incident_id=request.incident_id,
            units=request.units,
            location=(request.location[0], request.location[1]),
            incident_type=request.incident_type,
        )
        return result

    except Exception as e:
        logger.error("generate_perimeter_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/ambush/{badge}")
async def check_ambush_patterns(
    badge: str,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Check for ambush patterns at officer's location.

    Returns ambush risk assessment and indicators.
    """
    logger.info("check_ambush_request", badge=badge)

    try:
        # Get officer's current position
        position = await manager.telemetry.get_position(badge)

        if not position:
            raise HTTPException(
                status_code=404,
                detail=f"No position data for officer {badge}",
            )

        # Check for ambush patterns
        result = await manager.ambush_detector.check_location(
            badge=badge,
            lat=position["lat"],
            lon=position["lon"],
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("check_ambush_error", badge=badge, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/emergency/officer-down")
async def trigger_officer_down(
    request: EmergencyTrigger,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Trigger officer down alert.

    Broadcasts emergency alert to all connected clients.
    """
    logger.critical("officer_down_trigger_request", badge=request.badge)

    try:
        result = await manager.trigger_officer_down(
            badge=request.badge,
            source=request.source,
            details=request.details,
        )
        return result

    except Exception as e:
        logger.error("officer_down_trigger_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/emergency/sos")
async def trigger_sos(
    request: EmergencyTrigger,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Trigger SOS alert.

    Broadcasts SOS alert to all connected clients.
    """
    logger.critical("sos_trigger_request", badge=request.badge)

    try:
        result = await manager.trigger_sos(
            badge=request.badge,
            source=request.source,
            details=request.details,
        )
        return result

    except Exception as e:
        logger.error("sos_trigger_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/emergency/clear")
async def clear_emergency(
    request: EmergencyClear,
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Clear an active emergency.

    Clears the emergency and notifies all connected clients.
    """
    logger.info("clear_emergency_request", badge=request.badge)

    try:
        result = await manager.emergency_detector.clear_emergency(
            badge=request.badge,
            cleared_by=request.cleared_by,
            reason=request.reason,
        )
        return result

    except Exception as e:
        logger.error("clear_emergency_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/emergency/active")
async def get_active_emergencies(
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get all active emergencies.

    Returns list of all active officer emergencies.
    """
    logger.info("get_active_emergencies_request")

    try:
        emergencies = await manager.emergency_detector.get_active_emergencies()
        return {
            "emergencies": emergencies,
            "count": len(emergencies),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error("get_active_emergencies_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/history/{badge}")
async def get_officer_history(
    badge: str,
    limit: int = Query(100, description="Maximum number of points"),
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get position history for an officer.

    Returns historical positions for trajectory analysis.
    """
    logger.info("get_officer_history_request", badge=badge, limit=limit)

    try:
        history = await manager.telemetry.get_history(badge, limit=limit)
        return {
            "badge": badge,
            "history": history,
            "count": len(history),
        }

    except Exception as e:
        logger.error("get_officer_history_error", badge=badge, error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/nearby")
async def get_officers_nearby(
    lat: float = Query(..., description="Center latitude"),
    lon: float = Query(..., description="Center longitude"),
    radius_km: float = Query(1.0, description="Search radius in km"),
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get officers within a radius of a location.

    Returns list of officers sorted by distance.
    """
    logger.info("get_officers_nearby_request", lat=lat, lon=lon, radius_km=radius_km)

    try:
        officers = await manager.telemetry.get_officers_in_area(
            lat=lat,
            lon=lon,
            radius_km=radius_km,
        )
        return {
            "officers": officers,
            "count": len(officers),
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
        }

    except Exception as e:
        logger.error("get_officers_nearby_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/threats/area")
async def get_threats_in_area(
    lat: float = Query(..., description="Center latitude"),
    lon: float = Query(..., description="Center longitude"),
    radius_km: float = Query(1.0, description="Search radius in km"),
    manager: OfficerSafetyManager = Depends(get_manager),
) -> dict[str, Any]:
    """
    Get all threats in an area.

    Returns list of threats for map display.
    """
    logger.info("get_threats_in_area_request", lat=lat, lon=lon, radius_km=radius_km)

    try:
        threats = await manager.threat_engine.get_threats_in_area(
            lat=lat,
            lon=lon,
            radius_km=radius_km,
        )
        return {
            "threats": threats,
            "count": len(threats),
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
        }

    except Exception as e:
        logger.error("get_threats_in_area_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e
