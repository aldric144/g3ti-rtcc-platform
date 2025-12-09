"""
Tactical Analytics API endpoints for G3TI RTCC-UIP.

This module provides REST API endpoints for:
- Predictive heatmaps
- Tactical risk scoring
- Patrol route optimization
- Zone analysis
- Shift briefings
- Forecasting
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...core.security import get_current_user, require_roles
from ...tactical_engine import TacticalManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tactical", tags=["tactical"])


# ==================== Request/Response Models ====================


class PatrolRouteRequest(BaseModel):
    """Request model for patrol route optimization."""

    unit: str = Field(..., description="Unit identifier")
    shift: str = Field(..., description="Shift time range (e.g., '2300-0700' or 'A', 'B', 'C')")
    starting_point: list[float] = Field(
        ..., description="Starting coordinates [lat, lon]", min_length=2, max_length=2
    )
    max_distance: float = Field(
        default=15.0, description="Maximum route distance in km", ge=1.0, le=50.0
    )
    priority_zones: list[str] | None = Field(
        default=None, description="Optional list of priority zone IDs"
    )
    waypoint_count: int = Field(
        default=10, description="Number of waypoints to include", ge=3, le=20
    )


class HeatmapResponse(BaseModel):
    """Response model for heatmap endpoints."""

    geojson: dict
    clusters: list[dict]
    hot_zones: list[dict]
    confidence: float
    explanation: str
    generated_at: str


class RiskMapResponse(BaseModel):
    """Response model for risk map endpoints."""

    zones: list[dict]
    summary: dict
    level: str
    generated_at: str
    total_zones: int


class ZoneResponse(BaseModel):
    """Response model for zone endpoints."""

    id: str
    level: str
    bounds: dict
    center: dict
    risk_score: float | None = None
    risk_level: str | None = None
    activity_score: float | None = None
    status: str | None = None


class ForecastResponse(BaseModel):
    """Response model for forecast endpoints."""

    forecast_window: dict
    forecast_type: str
    predictions: dict
    zone_predictions: list[dict]
    high_risk_areas: list[dict]
    expected_incidents: float
    confidence: float
    model_info: dict
    generated_at: str


class ShiftBriefingResponse(BaseModel):
    """Response model for shift briefing endpoints."""

    briefing_id: str
    shift: dict
    generated_at: str
    valid_until: str
    zones_of_concern: list[dict]
    entity_highlights: dict
    case_developments: list[dict]
    ai_anomalies: list[dict]
    tactical_advisories: list[dict]
    overnight_summary: str
    statistics: dict


# ==================== Dependency ====================


def get_tactical_manager() -> TacticalManager:
    """Get tactical manager instance."""
    return TacticalManager()


# ==================== Heatmap Endpoints ====================


@router.get(
    "/heatmap/current",
    response_model=HeatmapResponse,
    summary="Get current heatmap",
    description="Generate current state heatmap based on recent incidents",
)
async def get_current_heatmap(
    type: str = Query(
        default="all",
        description="Heatmap type: gunfire, vehicles, crime, all",
    ),
    resolution: str = Query(
        default="medium",
        description="Grid resolution: low, medium, high",
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get current heatmap for specified type.

    Generates a heatmap showing current incident density and hotspots.
    """
    try:
        logger.info(f"Generating current heatmap: type={type}, resolution={resolution}")

        result = await tactical.get_current_heatmap(
            heatmap_type=type,
            resolution=resolution,
        )

        return HeatmapResponse(
            geojson=result.get("geojson", {}),
            clusters=result.get("clusters", []),
            hot_zones=result.get("hot_zones", []),
            confidence=result.get("confidence", 0.0),
            explanation=result.get("explanation", ""),
            generated_at=result.get("generated_at", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error(f"Failed to generate current heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/heatmap/predict",
    response_model=HeatmapResponse,
    summary="Get predictive heatmap",
    description="Generate predictive heatmap for future time window",
)
async def get_predictive_heatmap(
    hours: int | None = Query(
        default=None,
        description="Prediction window in hours (1-168)",
        ge=1,
        le=168,
    ),
    days: int | None = Query(
        default=None,
        description="Prediction window in days (1-7)",
        ge=1,
        le=7,
    ),
    type: str = Query(
        default="all",
        description="Heatmap type: gunfire, vehicles, crime, all",
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get predictive heatmap for future time window.

    Uses temporal and spatial models to predict future incident locations.
    """
    # Determine prediction window
    if days:
        prediction_hours = days * 24
    elif hours:
        prediction_hours = hours
    else:
        prediction_hours = 24  # Default to 24 hours

    try:
        logger.info(f"Generating predictive heatmap: hours={prediction_hours}, type={type}")

        result = await tactical.get_predictive_heatmap(
            hours=prediction_hours,
            heatmap_type=type,
        )

        return HeatmapResponse(
            geojson=result.get("geojson", {}),
            clusters=result.get("clusters", []),
            hot_zones=result.get("hot_zones", []),
            confidence=result.get("confidence", 0.0),
            explanation=result.get("explanation", ""),
            generated_at=result.get("generated_at", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error(f"Failed to generate predictive heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== Risk Map Endpoints ====================


@router.get(
    "/riskmap",
    response_model=RiskMapResponse,
    summary="Get tactical risk map",
    description="Generate risk map for zones with scoring breakdown",
)
async def get_risk_map(
    zone: str | None = Query(
        default=None,
        description="Specific zone ID or None for all zones",
    ),
    level: str = Query(
        default="micro",
        description="Risk level granularity: address, micro, district",
    ),
    include_factors: bool = Query(
        default=True,
        description="Include detailed risk factor breakdown",
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get tactical risk map for zones.

    Returns risk scores and contributing factors for each zone.
    """
    try:
        logger.info(f"Generating risk map: zone={zone}, level={level}")

        result = await tactical.get_risk_map(
            zone_id=zone,
            level=level,
            include_factors=include_factors,
        )

        return RiskMapResponse(
            zones=result.get("zones", []),
            summary=result.get("summary", {}),
            level=result.get("level", level),
            generated_at=result.get("generated_at", datetime.utcnow().isoformat()),
            total_zones=result.get("total_zones", 0),
        )
    except Exception as e:
        logger.error(f"Failed to generate risk map: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/riskmap/entity/{entity_type}/{entity_id}",
    summary="Get entity risk score",
    description="Get risk score for a specific entity",
)
async def get_entity_risk(
    entity_type: str,
    entity_id: str,
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get risk score for a specific entity.

    Supports person, vehicle, and address entity types.
    """
    if entity_type not in ["person", "vehicle", "address"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid entity type. Must be: person, vehicle, address",
        )

    try:
        logger.info(f"Getting entity risk: {entity_type}/{entity_id}")

        result = await tactical.get_entity_risk_score(
            entity_id=entity_id,
            entity_type=entity_type,
        )

        return result
    except Exception as e:
        logger.error(f"Failed to get entity risk: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== Patrol Route Endpoints ====================


@router.post(
    "/patrol/route",
    summary="Generate patrol route",
    description="Generate optimized patrol route based on risk and activity",
)
async def generate_patrol_route(
    request: PatrolRouteRequest,
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Generate optimized patrol route.

    Uses risk zones, predicted hotspots, and historical patterns
    to generate an optimal patrol route.
    """
    try:
        logger.info(f"Generating patrol route for unit {request.unit}")

        result = await tactical.generate_patrol_route(
            unit=request.unit,
            shift=request.shift,
            starting_point=tuple(request.starting_point),
            max_distance=request.max_distance,
            priority_zones=request.priority_zones,
            waypoint_count=request.waypoint_count,
        )

        return result
    except Exception as e:
        logger.error(f"Failed to generate patrol route: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/patrol/coverage",
    summary="Get patrol coverage analysis",
    description="Analyze patrol coverage for zones",
)
async def get_patrol_coverage(
    zone_id: str | None = Query(
        default=None,
        description="Specific zone ID or None for all zones",
    ),
    hours_back: int = Query(
        default=24,
        description="Hours of history to analyze",
        ge=1,
        le=168,
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get patrol coverage analysis.

    Identifies coverage gaps and provides recommendations.
    """
    try:
        logger.info(f"Getting patrol coverage: zone={zone_id}, hours={hours_back}")

        # Access patrol optimizer through tactical manager
        if tactical._patrol_optimizer:
            result = await tactical._patrol_optimizer.get_coverage_analysis(
                zone_id=zone_id,
                hours_back=hours_back,
            )
            return result

        return {
            "zones": [],
            "gaps": [],
            "recommendations": ["Coverage analysis unavailable"],
            "analysis_period_hours": hours_back,
        }
    except Exception as e:
        logger.error(f"Failed to get patrol coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== Zone Endpoints ====================


@router.get(
    "/zones",
    summary="Get all tactical zones",
    description="Get all tactical zones with optional enrichment",
)
async def get_zones(
    include_risk: bool = Query(
        default=True,
        description="Include risk scores",
    ),
    include_predictions: bool = Query(
        default=False,
        description="Include prediction data",
    ),
    level: str = Query(
        default="micro",
        description="Zone level: micro, district",
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get all tactical zones.

    Returns zone data with optional risk and prediction enrichment.
    """
    try:
        logger.info(f"Getting zones: level={level}")

        result = await tactical.get_zones(
            include_risk=include_risk,
            include_predictions=include_predictions,
            level=level,
        )

        return {
            "zones": result,
            "total": len(result),
            "level": level,
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get zones: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/zones/{zone_id}",
    summary="Get zone details",
    description="Get detailed information for a specific zone",
)
async def get_zone_details(
    zone_id: str,
    include_history: bool = Query(
        default=True,
        description="Include historical data",
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get detailed zone information.

    Returns comprehensive zone data including risk, predictions, and history.
    """
    try:
        logger.info(f"Getting zone details: {zone_id}")

        result = await tactical.get_zone(
            zone_id=zone_id,
            include_history=include_history,
        )

        if result.get("error"):
            raise HTTPException(status_code=404, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get zone details: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== Forecast Endpoints ====================


@router.get(
    "/forecast",
    response_model=ForecastResponse,
    summary="Get tactical forecast",
    description="Generate tactical forecast for specified time window",
)
async def get_forecast(
    hours: int | None = Query(
        default=None,
        description="Forecast window in hours (1-168)",
        ge=1,
        le=168,
    ),
    days: int | None = Query(
        default=None,
        description="Forecast window in days (1-7)",
        ge=1,
        le=7,
    ),
    type: str = Query(
        default="all",
        description="Forecast type: crime, gunfire, vehicles, all",
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get tactical forecast.

    Uses temporal, spatial, and Markov models to predict future activity.
    """
    # Determine forecast window
    if days:
        forecast_hours = days * 24
    elif hours:
        forecast_hours = hours
    else:
        forecast_hours = 24  # Default to 24 hours

    try:
        logger.info(f"Generating forecast: hours={forecast_hours}, type={type}")

        result = await tactical.get_forecast(
            hours=forecast_hours,
            forecast_type=type,
        )

        return ForecastResponse(
            forecast_window=result.get("forecast_window", {}),
            forecast_type=result.get("forecast_type", type),
            predictions=result.get("predictions", {}),
            zone_predictions=result.get("zone_predictions", []),
            high_risk_areas=result.get("high_risk_areas", []),
            expected_incidents=result.get("expected_incidents", 0),
            confidence=result.get("confidence", 0),
            model_info=result.get("model_info", {}),
            generated_at=result.get("generated_at", datetime.utcnow().isoformat()),
        )
    except Exception as e:
        logger.error(f"Failed to generate forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== Shift Briefing Endpoints ====================


@router.get(
    "/shiftbrief",
    response_model=ShiftBriefingResponse,
    summary="Get shift briefing",
    description="Generate shift briefing intelligence pack",
)
async def get_shift_briefing(
    shift: str = Query(
        ...,
        description="Shift identifier: A (day), B (evening), C (night)",
    ),
    include_routes: bool = Query(
        default=True,
        description="Include patrol route recommendations",
    ),
    include_heatmaps: bool = Query(
        default=True,
        description="Include heatmap snapshots",
    ),
    district: str | None = Query(
        default=None,
        description="Optional district filter",
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get shift briefing intelligence pack.

    Generates comprehensive briefing with zones of concern, entities of interest,
    case developments, AI anomalies, and tactical advisories.
    """
    if shift.upper() not in ["A", "B", "C"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid shift. Must be: A, B, or C",
        )

    try:
        logger.info(f"Generating shift briefing: shift={shift}")

        result = await tactical.get_shift_briefing(
            shift=shift.upper(),
            include_routes=include_routes,
            include_heatmaps=include_heatmaps,
            district=district,
        )

        return ShiftBriefingResponse(
            briefing_id=result.get("briefing_id", ""),
            shift=result.get("shift", {}),
            generated_at=result.get("generated_at", datetime.utcnow().isoformat()),
            valid_until=result.get("valid_until", ""),
            zones_of_concern=result.get("zones_of_concern", []),
            entity_highlights=result.get("entity_highlights", {}),
            case_developments=result.get("case_developments", []),
            ai_anomalies=result.get("ai_anomalies", []),
            tactical_advisories=result.get("tactical_advisories", []),
            overnight_summary=result.get("overnight_summary", ""),
            statistics=result.get("statistics", {}),
        )
    except Exception as e:
        logger.error(f"Failed to generate shift briefing: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== Audit Endpoints ====================


@router.get(
    "/audit/logs",
    summary="Get tactical audit logs",
    description="Get audit logs for tactical operations (Command Staff only)",
    dependencies=[Depends(require_roles(["admin", "supervisor"]))],
)
async def get_audit_logs(
    hours_back: int = Query(
        default=24,
        description="Hours of logs to retrieve",
        ge=1,
        le=168,
    ),
    action_type: str | None = Query(
        default=None,
        description="Filter by action type",
    ),
    current_user: dict = Depends(get_current_user),
    tactical: TacticalManager = Depends(get_tactical_manager),
):
    """
    Get tactical audit logs.

    Returns audit trail of tactical operations for compliance.
    """
    try:
        logger.info(f"Getting audit logs: hours={hours_back}, type={action_type}")

        # Query audit logs from Elasticsearch
        query = {
            "bool": {
                "must": [
                    {"range": {"timestamp": {"gte": f"now-{hours_back}h"}}},
                ]
            }
        }

        if action_type:
            query["bool"]["must"].append({"term": {"action": action_type}})

        # This would query the tactical_audit_logs index
        # For now, return placeholder
        return {
            "logs": [],
            "total": 0,
            "hours_back": hours_back,
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
