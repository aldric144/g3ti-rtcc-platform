"""
Entities API router for the G3TI RTCC-UIP Backend.

This module provides CRUD endpoints for graph entities:
- Person
- Vehicle
- Incident
- Weapon
- ShellCasing
- Address
- Camera
- LicensePlate
- Associations (relationships)
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import (
    RequireAnalyst,
    RequireDetective,
    RequireOfficer,
)
from app.core.exceptions import EntityNotFoundError, ValidationError
from app.core.logging import get_logger
from app.schemas.entities import (
    AssociationCreate,
)
from app.services.graph.entity_service import EntityGraphService, get_entity_graph_service

logger = get_logger(__name__)
router = APIRouter()


# Generic entity operations


@router.post("/{entity_type}", status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_type: str,
    properties: dict[str, Any],
    token: RequireAnalyst,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
) -> dict[str, Any]:
    """
    Create a new entity in the graph.

    - **entity_type**: Type of entity (Person, Vehicle, Incident, etc.)
    - **properties**: Entity properties

    Returns the created entity with its ID.
    """
    try:
        # Capitalize entity type to match Neo4j labels
        label = entity_type.capitalize()

        entity = await graph_service.create_node(
            label=label, properties=properties, user_id=token.sub
        )
        return entity
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get("/{entity_type}/{entity_id}")
async def get_entity(
    entity_type: str,
    entity_id: str,
    token: RequireOfficer,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
) -> dict[str, Any]:
    """
    Get an entity by ID.

    - **entity_type**: Type of entity
    - **entity_id**: Entity identifier

    Returns the entity properties.
    """
    try:
        label = entity_type.capitalize()
        entity = await graph_service.get_node(label=label, entity_id=entity_id, user_id=token.sub)
        return entity
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type} not found",
        )


@router.put("/{entity_type}/{entity_id}")
async def update_entity(
    entity_type: str,
    entity_id: str,
    properties: dict[str, Any],
    token: RequireAnalyst,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
) -> dict[str, Any]:
    """
    Update an entity's properties.

    - **entity_type**: Type of entity
    - **entity_id**: Entity identifier
    - **properties**: Properties to update

    Returns the updated entity.
    """
    try:
        label = entity_type.capitalize()
        entity = await graph_service.update_node(
            label=label, entity_id=entity_id, properties=properties, user_id=token.sub
        )
        return entity
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type} not found",
        )


@router.delete("/{entity_type}/{entity_id}")
async def delete_entity(
    entity_type: str,
    entity_id: str,
    token: RequireDetective,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
) -> dict[str, str]:
    """
    Delete an entity and its relationships.

    - **entity_type**: Type of entity
    - **entity_id**: Entity identifier

    Note: This operation cannot be undone.
    """
    try:
        label = entity_type.capitalize()
        await graph_service.delete_node(label=label, entity_id=entity_id, user_id=token.sub)
        return {"message": f"{entity_type} deleted successfully"}
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type} not found",
        )


@router.get("/{entity_type}/{entity_id}/relationships")
async def get_entity_relationships(
    entity_type: str,
    entity_id: str,
    token: RequireOfficer,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
    relationship_type: str | None = None,
    direction: str = "both",
    limit: int = Query(default=100, le=500),
) -> list[dict[str, Any]]:
    """
    Get relationships for an entity.

    - **entity_type**: Type of entity
    - **entity_id**: Entity identifier
    - **relationship_type**: Filter by relationship type (optional)
    - **direction**: Relationship direction (outgoing, incoming, both)
    - **limit**: Maximum results (default: 100, max: 500)

    Returns list of related entities with relationship info.
    """
    try:
        label = entity_type.capitalize()
        relationships = await graph_service.find_relationships(
            entity_label=label,
            entity_id=entity_id,
            relationship_type=relationship_type,
            direction=direction,
            limit=limit,
        )
        return relationships
    except Exception as e:
        logger.error("get_relationships_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving relationships",
        )


@router.get("/{entity_type}/{entity_id}/network")
async def get_entity_network(
    entity_type: str,
    entity_id: str,
    token: RequireOfficer,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
    depth: int = Query(default=2, ge=1, le=4),
    limit: int = Query(default=100, le=500),
) -> dict[str, Any]:
    """
    Get the network graph for an entity.

    Returns nodes and edges for visualization.

    - **entity_type**: Type of entity
    - **entity_id**: Entity identifier
    - **depth**: Maximum relationship depth (default: 2, max: 4)
    - **limit**: Maximum nodes (default: 100, max: 500)
    """
    try:
        label = entity_type.capitalize()
        network = await graph_service.get_entity_network(
            entity_label=label, entity_id=entity_id, depth=depth, limit=limit
        )
        return network
    except Exception as e:
        logger.error("get_network_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving network",
        )


# Association (relationship) endpoints


@router.post("/associations", status_code=status.HTTP_201_CREATED)
async def create_association(
    association: AssociationCreate,
    token: RequireAnalyst,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
) -> dict[str, Any]:
    """
    Create a relationship between two entities.

    - **source_type**: Source entity type
    - **source_id**: Source entity ID
    - **target_type**: Target entity type
    - **target_id**: Target entity ID
    - **association_type**: Type of relationship
    - **properties**: Additional relationship properties
    """
    try:
        relationship = await graph_service.link_nodes(
            source_label=association.source_type.capitalize(),
            source_id=association.source_id,
            target_label=association.target_type.capitalize(),
            target_id=association.target_id,
            relationship_type=association.association_type.value.upper(),
            properties={
                "confidence": association.confidence,
                "start_date": (
                    association.start_date.isoformat() if association.start_date else None
                ),
                "end_date": association.end_date.isoformat() if association.end_date else None,
                "notes": association.notes,
            },
            user_id=token.sub,
        )
        return relationship
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.delete("/associations")
async def delete_association(
    source_type: str,
    source_id: str,
    target_type: str,
    target_id: str,
    token: RequireDetective,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
    relationship_type: str | None = None,
) -> dict[str, Any]:
    """
    Delete relationship(s) between two entities.

    - **source_type**: Source entity type
    - **source_id**: Source entity ID
    - **target_type**: Target entity type
    - **target_id**: Target entity ID
    - **relationship_type**: Specific relationship type (optional)
    """
    deleted_count = await graph_service.unlink_nodes(
        source_label=source_type.capitalize(),
        source_id=source_id,
        target_label=target_type.capitalize(),
        target_id=target_id,
        relationship_type=relationship_type.upper() if relationship_type else None,
        user_id=token.sub,
    )

    return {"message": f"Deleted {deleted_count} relationship(s)", "deleted_count": deleted_count}


# Search endpoint


@router.get("/{entity_type}/search")
async def search_entities(
    entity_type: str,
    token: RequireOfficer,
    graph_service: Annotated[EntityGraphService, Depends(get_entity_graph_service)],
    property_name: str = Query(..., description="Property to search"),
    property_value: str = Query(..., description="Value to match"),
    limit: int = Query(default=100, le=500),
) -> list[dict[str, Any]]:
    """
    Search entities by property value.

    - **entity_type**: Type of entity to search
    - **property_name**: Property to match
    - **property_value**: Value to search for
    - **limit**: Maximum results
    """
    label = entity_type.capitalize()
    results = await graph_service.search_by_property(
        label=label, property_name=property_name, property_value=property_value, limit=limit
    )
    return results
