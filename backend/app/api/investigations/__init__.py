"""
Investigations API router for the G3TI RTCC-UIP Backend.

This module provides endpoints for:
- Investigation CRUD operations
- Investigative search
- Case management
- Incident linking
- Entity correlation
- Case auto-building
- Timeline generation
- Report export (PDF/JSON)
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from app.api.deps import (
    RequireDetective,
    RequireOfficer,
)
from app.core.logging import audit_logger, get_logger
from app.schemas.investigations import (
    SearchQuery,
    SearchResult,
)
from app.services.search.search_service import SearchService, get_search_service

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models for Phase 4 Investigations Engine


class LinkIncidentsRequest(BaseModel):
    """Request model for incident linking."""

    incident_ids: list[str] = Field(
        ...,
        description="List of incident IDs to analyze for linkages",
        min_length=1,
    )


class LinkIncidentsResponse(BaseModel):
    """Response model for incident linking."""

    linked_incidents: list[dict[str, Any]]
    confidence_scores: dict[str, float]
    explanations: list[str]


class CreateCaseRequest(BaseModel):
    """Request model for case creation."""

    incident_id: str | None = Field(None, description="Incident ID to build case from")
    suspect_id: str | None = Field(None, description="Suspect ID to build case from")
    title: str | None = Field(None, description="Optional case title")


class CreateCaseResponse(BaseModel):
    """Response model for case creation."""

    case_id: str
    case_number: str
    summary: str
    timeline: list[dict[str, Any]]
    evidence: dict[str, Any]
    linked_incidents: list[dict[str, Any]]
    suspects: list[dict[str, Any]]
    vehicles: list[dict[str, Any]]
    addresses: list[dict[str, Any]]
    risk_assessment: dict[str, Any] | None
    recommendations: list[str]


class EntityProfileResponse(BaseModel):
    """Response model for entity profile."""

    entity_id: str
    entity_type: str
    name: str
    prior_incidents: list[dict[str, Any]]
    address_history: list[dict[str, Any]]
    vehicle_connections: list[dict[str, Any]]
    weapon_matches: list[dict[str, Any]]
    lpr_activity: list[dict[str, Any]]
    bwc_interactions: list[dict[str, Any]]
    known_associates: list[dict[str, Any]]
    risk_score: float


@router.post("/search", response_model=SearchResult)
async def search_investigations(
    query: SearchQuery,
    token: RequireOfficer,
    search_service: Annotated[SearchService, Depends(get_search_service)],
) -> SearchResult:
    """
    Execute an investigative search.

    Searches across all entity types with support for:
    - Full-text search
    - Date range filtering
    - Geographic filtering
    - Entity type filtering

    - **query**: Search query string
    - **entity_types**: Filter by entity types (optional)
    - **date_from**: Start date filter (optional)
    - **date_to**: End date filter (optional)
    - **location**: Center point for geo search (optional)
    - **radius_miles**: Search radius in miles (optional)
    - **filters**: Additional filters (optional)
    - **page**: Page number (default: 1)
    - **page_size**: Results per page (default: 20)

    Returns search results with facets and suggestions.
    """
    try:
        results = await search_service.search(query)
        return results
    except Exception as e:
        logger.error("search_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search error occurred",
        ) from e


@router.get("/")
async def list_investigations(
    token: RequireOfficer,
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    assigned_to: str | None = None,
) -> dict:
    """
    List investigations with pagination.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20)
    - **status_filter**: Filter by status (optional)
    - **assigned_to**: Filter by assigned user (optional)

    Note: Full implementation requires database integration.
    Returns placeholder response for now.
    """
    # Placeholder - would query database in full implementation
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "pages": 0,
        "message": "Investigation listing requires database integration",
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_investigation(
    token: RequireDetective,
) -> dict:
    """
    Create a new investigation.

    Note: Full implementation requires database integration.
    """
    return {"message": "Investigation creation requires database integration", "id": None}


@router.get("/{investigation_id}")
async def get_investigation(
    investigation_id: str,
    token: RequireOfficer,
) -> dict:
    """
    Get investigation details.

    - **investigation_id**: Investigation identifier

    Note: Full implementation requires database integration.
    """
    return {
        "message": "Investigation retrieval requires database integration",
        "id": investigation_id,
    }


@router.put("/{investigation_id}")
async def update_investigation(
    investigation_id: str,
    token: RequireDetective,
) -> dict:
    """
    Update an investigation.

    - **investigation_id**: Investigation identifier

    Note: Full implementation requires database integration.
    """
    return {"message": "Investigation update requires database integration", "id": investigation_id}


# ============================================================================
# Phase 4: Investigations Engine Endpoints
# ============================================================================


@router.post(
    "/link",
    response_model=LinkIncidentsResponse,
    summary="Link related incidents",
    description="Analyze incidents for linkages based on time, location, entities, and other factors",
)
async def link_incidents(
    request: LinkIncidentsRequest,
    token: RequireDetective,
) -> LinkIncidentsResponse:
    """
    Link incidents based on various correlation factors.

    Analyzes incidents for relationships including:
    - Temporal proximity
    - Geographic proximity
    - Entity overlap (persons, vehicles, addresses)
    - Narrative similarity
    - Ballistic matches
    - Vehicle recurrence
    - M.O. similarity
    """
    from app.investigations_engine import InvestigationsManager

    logger.info(f"Linking incidents: {request.incident_ids}")

    audit_logger.info(
        "Incident linking requested",
        extra={
            "user_id": (
                token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
            ),
            "incident_ids": request.incident_ids,
            "action": "link_incidents",
        },
    )

    try:
        manager = InvestigationsManager()
        user_id = token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
        user_role = token.get("role") if isinstance(token, dict) else getattr(token, "role", "")
        result = await manager.link_incidents(
            incident_ids=request.incident_ids,
            user_id=user_id,
            user_role=user_role,
        )

        return LinkIncidentsResponse(
            linked_incidents=result.linked_incidents,
            confidence_scores=result.confidence_scores,
            explanations=result.explanations,
        )

    except Exception as e:
        logger.error(f"Error linking incidents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error linking incidents: {str(e)}",
        ) from e


@router.get(
    "/entities/{entity_id}",
    response_model=EntityProfileResponse,
    summary="Get entity investigative profile",
    description="Get comprehensive entity profile with all correlations",
)
async def get_entity_profile(
    entity_id: str,
    token: RequireOfficer,
) -> EntityProfileResponse:
    """
    Get comprehensive entity profile.

    Returns:
    - Prior incidents
    - Address history
    - Vehicle connections
    - Weapon/ballistic matches
    - LPR activity trail
    - BWC interactions
    - Known associates
    - Risk score
    """
    from app.investigations_engine import InvestigationsManager

    logger.info(f"Getting entity profile: {entity_id}")

    audit_logger.info(
        "Entity profile requested",
        extra={
            "user_id": (
                token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
            ),
            "entity_id": entity_id,
            "action": "get_entity_profile",
        },
    )

    try:
        manager = InvestigationsManager()
        user_id = token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
        user_role = token.get("role") if isinstance(token, dict) else getattr(token, "role", "")
        profile = await manager.get_entity_profile(
            entity_id=entity_id,
            user_id=user_id,
            user_role=user_role,
        )

        return EntityProfileResponse(
            entity_id=profile.entity_id,
            entity_type=profile.entity_type,
            name=profile.name,
            prior_incidents=profile.prior_incidents,
            address_history=profile.address_history,
            vehicle_connections=profile.vehicle_connections,
            weapon_matches=profile.weapon_matches,
            lpr_activity=profile.lpr_activity,
            bwc_interactions=profile.bwc_interactions,
            known_associates=profile.known_associates,
            risk_score=profile.risk_score,
        )

    except Exception as e:
        logger.error(f"Error getting entity profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting entity profile: {str(e)}",
        ) from e


@router.post(
    "/case/create",
    response_model=CreateCaseResponse,
    summary="Auto-create investigation case",
    description="Automatically build a case from an incident or suspect",
)
async def create_case(
    request: CreateCaseRequest,
    token: RequireDetective,
) -> CreateCaseResponse:
    """
    Auto-create a case file.

    Given an incident or suspect:
    - Auto-creates a case file object
    - Pulls all linked incidents
    - Pulls all entities
    - Builds case synopsis
    - Builds timeline
    - Attaches evidence
    - Auto-generates investigative leads
    - Assigns risk scores
    """
    from app.investigations_engine import InvestigationsManager

    if not request.incident_id and not request.suspect_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either incident_id or suspect_id must be provided",
        )

    logger.info(f"Creating case from incident={request.incident_id}, suspect={request.suspect_id}")

    audit_logger.info(
        "Case creation requested",
        extra={
            "user_id": (
                token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
            ),
            "incident_id": request.incident_id,
            "suspect_id": request.suspect_id,
            "action": "create_case",
        },
    )

    try:
        manager = InvestigationsManager()
        user_id = token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
        user_role = token.get("role") if isinstance(token, dict) else getattr(token, "role", "")
        case = await manager.create_case(
            incident_id=request.incident_id,
            suspect_id=request.suspect_id,
            title=request.title,
            user_id=user_id,
            user_role=user_role,
        )

        return CreateCaseResponse(
            case_id=case.case_id,
            case_number=case.case_number,
            summary=case.summary,
            timeline=[t.to_dict() for t in case.timeline],
            evidence=case.evidence.to_dict(),
            linked_incidents=case.linked_incidents,
            suspects=[s.to_dict() for s in case.suspects],
            vehicles=[v.to_dict() for v in case.vehicles],
            addresses=case.addresses,
            risk_assessment=case.risk_assessment.to_dict() if case.risk_assessment else None,
            recommendations=case.recommendations,
        )

    except Exception as e:
        logger.error(f"Error creating case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating case: {str(e)}",
        ) from e


@router.get(
    "/case/{case_id}",
    response_model=CreateCaseResponse,
    summary="Get case details",
    description="Get full details of an investigation case",
)
async def get_case(
    case_id: str,
    token: RequireOfficer,
) -> CreateCaseResponse:
    """Get case details by ID."""
    from app.investigations_engine import InvestigationsManager

    logger.info(f"Getting case: {case_id}")

    audit_logger.info(
        "Case retrieval requested",
        extra={
            "user_id": (
                token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
            ),
            "case_id": case_id,
            "action": "get_case",
        },
    )

    try:
        manager = InvestigationsManager()
        case = await manager._get_case(case_id)

        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found",
            )

        return CreateCaseResponse(
            case_id=case.case_id,
            case_number=case.case_number,
            summary=case.summary,
            timeline=[t.to_dict() for t in case.timeline],
            evidence=case.evidence.to_dict(),
            linked_incidents=case.linked_incidents,
            suspects=[s.to_dict() for s in case.suspects],
            vehicles=[v.to_dict() for v in case.vehicles],
            addresses=case.addresses,
            risk_assessment=case.risk_assessment.to_dict() if case.risk_assessment else None,
            recommendations=case.recommendations,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting case: {str(e)}",
        ) from e


@router.get(
    "/case/{case_id}/timeline",
    summary="Get case timeline",
    description="Get timeline events for a case",
)
async def get_case_timeline(
    case_id: str,
    token: RequireOfficer,
) -> list[dict[str, Any]]:
    """Get timeline for a case."""
    from app.investigations_engine import InvestigationsManager

    logger.info(f"Getting timeline for case: {case_id}")

    try:
        manager = InvestigationsManager()
        user_id = token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
        user_role = token.get("role") if isinstance(token, dict) else getattr(token, "role", "")
        timeline = await manager.generate_timeline(
            case_id=case_id,
            user_id=user_id,
            user_role=user_role,
        )

        return [t.to_dict() for t in timeline]

    except Exception as e:
        logger.error(f"Error getting case timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting case timeline: {str(e)}",
        ) from e


@router.get(
    "/case/{case_id}/export/pdf",
    summary="Export case as PDF",
    description="Export case report as PDF document",
)
async def export_case_pdf(
    case_id: str,
    token: RequireDetective,
) -> Response:
    """Export case as PDF document."""
    from app.investigations_engine import InvestigationsManager

    logger.info(f"Exporting case as PDF: {case_id}")

    audit_logger.info(
        "Case PDF export requested",
        extra={
            "user_id": (
                token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
            ),
            "case_id": case_id,
            "action": "export_case_pdf",
        },
    )

    try:
        manager = InvestigationsManager()
        user_id = token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
        user_role = token.get("role") if isinstance(token, dict) else getattr(token, "role", "")
        pdf_bytes = await manager.export_case_pdf(
            case_id=case_id,
            user_id=user_id,
            user_role=user_role,
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="case_{case_id}.pdf"'},
        )

    except Exception as e:
        logger.error(f"Error exporting case as PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting case as PDF: {str(e)}",
        ) from e


@router.get(
    "/case/{case_id}/export/json",
    summary="Export case as JSON",
    description="Export case report as JSON document",
)
async def export_case_json(
    case_id: str,
    token: RequireDetective,
) -> dict[str, Any]:
    """Export case as JSON document."""
    from app.investigations_engine import InvestigationsManager

    logger.info(f"Exporting case as JSON: {case_id}")

    audit_logger.info(
        "Case JSON export requested",
        extra={
            "user_id": (
                token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
            ),
            "case_id": case_id,
            "action": "export_case_json",
        },
    )

    try:
        manager = InvestigationsManager()
        user_id = token.get("user_id") if isinstance(token, dict) else getattr(token, "user_id", "")
        user_role = token.get("role") if isinstance(token, dict) else getattr(token, "role", "")
        json_data = await manager.export_case_json(
            case_id=case_id,
            user_id=user_id,
            user_role=user_role,
        )

        return json_data

    except Exception as e:
        logger.error(f"Error exporting case as JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting case as JSON: {str(e)}",
        ) from e


@router.get(
    "/entities/{entity_id}/graph",
    summary="Get entity relationship graph",
    description="Get graph data for entity relationships",
)
async def get_entity_graph(
    entity_id: str,
    token: RequireOfficer,
    depth: int = Query(2, ge=1, le=4, description="Graph traversal depth"),
    max_nodes: int = Query(50, ge=10, le=200, description="Maximum nodes to return"),
) -> dict[str, Any]:
    """Get entity relationship graph for visualization."""
    from app.investigations_engine.entity_correlation import EntityCorrelator

    logger.info(f"Getting entity graph: {entity_id}")

    try:
        correlator = EntityCorrelator()
        graph = await correlator.expand_graph(
            entity_id=entity_id,
            depth=depth,
            max_nodes=max_nodes,
        )

        return graph

    except Exception as e:
        logger.error(f"Error getting entity graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting entity graph: {str(e)}",
        ) from e
