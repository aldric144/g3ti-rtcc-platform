"""
AI Intelligence API Endpoints.

This module provides the REST API endpoints for the AI Intelligence Engine,
including natural language queries, anomaly detection, pattern recognition,
and risk scoring.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.ai_engine import get_ai_manager
from app.api.deps import get_current_user
from app.core.logging import audit_logger, get_logger
from app.schemas.auth import UserInDB

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])


class AIQueryRequest(BaseModel):
    """Request model for natural language AI queries."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language investigative query",
        examples=["Show me vehicles connected to gunfire within the last 30 days near Broadway."],
    )
    role: str | None = Field(
        default=None,
        description="User role for access control filtering",
    )


class AIQueryResponse(BaseModel):
    """Response model for AI queries."""

    query_id: str
    original_query: str
    summary: str
    entities: list[dict[str, Any]] = Field(default_factory=list)
    incidents: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    risk_scores: dict[str, Any] = Field(default_factory=dict)
    anomalies: list[dict[str, Any]] = Field(default_factory=list)
    patterns: list[dict[str, Any]] = Field(default_factory=list)
    predictions: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    processed_at: str
    processing_time_ms: float
    confidence: float


class AnomalyResponse(BaseModel):
    """Response model for anomaly detection."""

    anomalies: list[dict[str, Any]]
    total_count: int
    time_window_hours: int
    generated_at: str


class PatternResponse(BaseModel):
    """Response model for pattern recognition."""

    patterns: list[dict[str, Any]]
    total_count: int
    pattern_type: str | None
    time_window_hours: int
    generated_at: str


class PredictionRequest(BaseModel):
    """Request model for predictions."""

    prediction_type: str = Field(
        ...,
        description="Type of prediction: vehicle_trajectory, crime_heat, gunfire_recurrence, offender_pathway",
    )
    input_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for the prediction",
    )


class PredictionResponse(BaseModel):
    """Response model for predictions."""

    prediction: dict[str, Any]
    generated_at: str


class RiskScoreRequest(BaseModel):
    """Request model for risk score calculation."""

    entities: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="List of entities to calculate risk scores for",
    )


class RiskScoreResponse(BaseModel):
    """Response model for risk scores."""

    risk_scores: dict[str, dict[str, Any]]
    total_count: int
    high_risk_count: int
    generated_at: str


class EntityResolutionRequest(BaseModel):
    """Request model for entity resolution."""

    entities: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="List of entities to resolve",
    )


class EntityResolutionResponse(BaseModel):
    """Response model for entity resolution."""

    resolved_entities: list[dict[str, Any]]
    total_count: int
    merge_candidates_found: int
    generated_at: str


class AIStatisticsResponse(BaseModel):
    """Response model for AI engine statistics."""

    initialized: bool
    cached_queries: int
    insight_subscribers: int
    components: dict[str, str]


@router.post(
    "/query",
    response_model=AIQueryResponse,
    summary="Natural Language Investigative Query",
    description="Process a natural language query to search across all data sources and return unified intelligence.",
)
async def process_ai_query(
    request: AIQueryRequest,
    current_user: UserInDB = Depends(get_current_user),
) -> AIQueryResponse:
    """
    Process a natural language investigative query.

    This endpoint converts natural language queries into structured searches
    across Neo4j and Elasticsearch, resolves entities, calculates risk scores,
    and returns a unified intelligence response.

    Example queries:
    - "Show me vehicles connected to gunfire within the last 30 days near Broadway"
    - "Find all incidents involving John Smith in the last week"
    - "What vehicles have been spotted near 123 Main St?"
    """
    logger.info(
        "ai_query_request",
        user_id=current_user.id,
        query_length=len(request.query),
    )

    audit_logger.log_system_event(
        event_type="ai_query_api_request",
        details={
            "user_id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "query_preview": request.query[:100],
        },
    )

    try:
        ai_manager = get_ai_manager()

        result = await ai_manager.process_query(
            query=request.query,
            user_id=current_user.id,
            role=request.role or current_user.role,
        )

        return AIQueryResponse(
            query_id=result.query_id,
            original_query=result.original_query,
            summary=result.summary,
            entities=[e.to_dict() if hasattr(e, "to_dict") else e for e in result.entities],
            incidents=result.incidents,
            relationships=[
                r.to_dict() if hasattr(r, "to_dict") else r for r in result.relationships
            ],
            risk_scores={
                k: v.to_dict() if hasattr(v, "to_dict") else v
                for k, v in result.risk_scores.items()
            },
            anomalies=[a.to_dict() if hasattr(a, "to_dict") else a for a in result.anomalies],
            patterns=[p.to_dict() if hasattr(p, "to_dict") else p for p in result.patterns],
            predictions=[p.to_dict() if hasattr(p, "to_dict") else p for p in result.predictions],
            recommendations=result.recommendations,
            processed_at=result.processed_at.isoformat(),
            processing_time_ms=result.processing_time_ms,
            confidence=result.confidence,
        )

    except Exception as e:
        logger.error("ai_query_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI query processing failed: {str(e)}",
        ) from e


@router.get(
    "/anomalies",
    response_model=AnomalyResponse,
    summary="Detect Anomalies",
    description="Detect anomalies in recent data including vehicle behavior, gunfire density, and crime patterns.",
)
async def get_anomalies(
    hours: int = Query(
        default=24,
        ge=1,
        le=720,
        description="Time window in hours to analyze",
    ),
    current_user: UserInDB = Depends(get_current_user),
) -> AnomalyResponse:
    """
    Detect anomalies in recent data.

    Analyzes data from the specified time window for:
    - Out-of-pattern vehicle behavior
    - Unusual gunfire density changes
    - Sudden clustering of related offenders
    - Timeline deviations
    - Crime signature shifts
    - Repeat caller anomalies
    """
    logger.info(
        "anomaly_detection_request",
        user_id=current_user.id,
        hours=hours,
    )

    try:
        ai_manager = get_ai_manager()

        anomalies = await ai_manager.detect_anomalies(
            hours=hours,
            user_id=current_user.id,
        )

        anomaly_dicts = [a.to_dict() if hasattr(a, "to_dict") else a for a in anomalies]

        return AnomalyResponse(
            anomalies=anomaly_dicts,
            total_count=len(anomalies),
            time_window_hours=hours,
            generated_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error("anomaly_detection_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection failed: {str(e)}",
        ) from e


@router.get(
    "/patterns",
    response_model=PatternResponse,
    summary="Get Recognized Patterns",
    description="Get recognized patterns including vehicle trajectories, crime heat, and offender pathways.",
)
async def get_patterns(
    type: str | None = Query(
        default=None,
        description="Pattern type filter: vehicles, gunfire, offenders, temporal, geographic",
    ),
    hours: int = Query(
        default=168,
        ge=1,
        le=2160,
        description="Time window in hours (default 7 days)",
    ),
    current_user: UserInDB = Depends(get_current_user),
) -> PatternResponse:
    """
    Get recognized patterns from the data.

    Identifies patterns including:
    - Repeat offender pathways
    - Vehicle trajectory patterns
    - Crime heat forecasting
    - Gunfire recurrence mapping
    - Temporal patterns (peak hours, days)
    - Geographic clustering
    """
    logger.info(
        "pattern_recognition_request",
        user_id=current_user.id,
        pattern_type=type,
        hours=hours,
    )

    try:
        ai_manager = get_ai_manager()

        patterns = await ai_manager.get_patterns(
            pattern_type=type,
            hours=hours,
            user_id=current_user.id,
        )

        pattern_dicts = [p.to_dict() if hasattr(p, "to_dict") else p for p in patterns]

        return PatternResponse(
            patterns=pattern_dicts,
            total_count=len(patterns),
            pattern_type=type,
            time_window_hours=hours,
            generated_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error("pattern_recognition_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern recognition failed: {str(e)}",
        ) from e


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Get Predictions",
    description="Get predictions from AI models including vehicle trajectories and crime forecasts.",
)
async def get_prediction(
    request: PredictionRequest,
    current_user: UserInDB = Depends(get_current_user),
) -> PredictionResponse:
    """
    Get predictions from AI models.

    Supported prediction types:
    - vehicle_trajectory: Predict likely next location for a vehicle
    - crime_heat: Predict crime hotspots for an area
    - gunfire_recurrence: Predict gunfire recurrence probability
    - offender_pathway: Predict likely pathway for a repeat offender
    """
    logger.info(
        "prediction_request",
        user_id=current_user.id,
        prediction_type=request.prediction_type,
    )

    try:
        ai_manager = get_ai_manager()

        prediction = await ai_manager.get_predictions(
            prediction_type=request.prediction_type,
            input_data=request.input_data,
            user_id=current_user.id,
        )

        prediction_dict = prediction.to_dict() if hasattr(prediction, "to_dict") else prediction

        return PredictionResponse(
            prediction=prediction_dict,
            generated_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error("prediction_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        ) from e


@router.post(
    "/risk-scores",
    response_model=RiskScoreResponse,
    summary="Calculate Risk Scores",
    description="Calculate risk scores for entities including persons, vehicles, and addresses.",
)
async def calculate_risk_scores(
    request: RiskScoreRequest,
    current_user: UserInDB = Depends(get_current_user),
) -> RiskScoreResponse:
    """
    Calculate risk scores for entities.

    Calculates weighted risk scores based on:
    - Criminal history
    - Recent activity
    - Association count
    - Incident involvement
    - Location risk
    - Warrant status
    - Weapon involvement
    """
    logger.info(
        "risk_score_request",
        user_id=current_user.id,
        entity_count=len(request.entities),
    )

    try:
        ai_manager = get_ai_manager()

        scores = await ai_manager.calculate_risk_scores(
            entities=request.entities,
            user_id=current_user.id,
        )

        score_dicts = {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in scores.items()}

        high_risk_count = sum(
            1
            for v in scores.values()
            if hasattr(v, "level") and v.level.value in ["critical", "high"]
        )

        return RiskScoreResponse(
            risk_scores=score_dicts,
            total_count=len(scores),
            high_risk_count=high_risk_count,
            generated_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error("risk_score_calculation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk score calculation failed: {str(e)}",
        ) from e


@router.post(
    "/resolve-entities",
    response_model=EntityResolutionResponse,
    summary="Resolve Entities",
    description="Resolve and match entities across data sources using probabilistic matching.",
)
async def resolve_entities(
    request: EntityResolutionRequest,
    current_user: UserInDB = Depends(get_current_user),
) -> EntityResolutionResponse:
    """
    Resolve and match entities.

    Uses probabilistic matching including:
    - Edit distance similarity
    - Phonetic matching (Soundex)
    - Tag similarity
    - Cross-source matching
    """
    logger.info(
        "entity_resolution_request",
        user_id=current_user.id,
        entity_count=len(request.entities),
    )

    try:
        ai_manager = get_ai_manager()

        resolved = await ai_manager.resolve_entities(
            entities=request.entities,
            user_id=current_user.id,
        )

        resolved_dicts = [e.to_dict() if hasattr(e, "to_dict") else e for e in resolved]

        merge_candidates_count = sum(
            len(
                e.get("merge_candidates", [])
                if isinstance(e, dict)
                else getattr(e, "merge_candidates", [])
            )
            for e in resolved
        )

        return EntityResolutionResponse(
            resolved_entities=resolved_dicts,
            total_count=len(resolved),
            merge_candidates_found=merge_candidates_count,
            generated_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error("entity_resolution_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Entity resolution failed: {str(e)}",
        ) from e


@router.get(
    "/statistics",
    response_model=AIStatisticsResponse,
    summary="Get AI Engine Statistics",
    description="Get statistics about the AI engine including component status and cache info.",
)
async def get_ai_statistics(
    current_user: UserInDB = Depends(get_current_user),
) -> AIStatisticsResponse:
    """Get AI engine statistics."""
    try:
        ai_manager = get_ai_manager()
        stats = await ai_manager.get_statistics()

        return AIStatisticsResponse(
            initialized=stats["initialized"],
            cached_queries=stats["cached_queries"],
            insight_subscribers=stats["insight_subscribers"],
            components=stats["components"],
        )

    except Exception as e:
        logger.error("ai_statistics_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI statistics: {str(e)}",
        ) from e


__all__ = ["router"]
