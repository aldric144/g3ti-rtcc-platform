"""
Entity auto-creator for the G3TI RTCC-UIP Backend.

This module automatically creates and links entities in Neo4j
based on ingested events. It extracts entity information from
events and creates/updates the corresponding graph nodes.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.logging import audit_logger, get_logger
from app.db.neo4j import get_neo4j_manager
from app.schemas.entities import EntityType
from app.schemas.events import EventCreate, EventSource

logger = get_logger(__name__)


class EntityAutoCreator:
    """
    Automatically creates entities in Neo4j from ingested events.

    Extracts entity information (persons, vehicles, incidents, etc.)
    from events and creates or updates the corresponding graph nodes
    with relationships to the source event.
    """

    def __init__(self) -> None:
        """Initialize the entity auto-creator."""
        self._neo4j = get_neo4j_manager()
        self._entity_extractors = {
            EventSource.FLOCK: self._extract_from_flock,
            EventSource.SHOTSPOTTER: self._extract_from_shotspotter,
            EventSource.MILESTONE: self._extract_from_milestone,
            EventSource.ONESOLUTION: self._extract_from_onesolution,
            EventSource.NESS: self._extract_from_ness,
            EventSource.BWC: self._extract_from_bwc,
            EventSource.HOTSHEETS: self._extract_from_hotsheets,
        }

    async def process_event(self, event: EventCreate, event_id: str) -> list[str]:
        """
        Process an event and create/update entities.

        Args:
            event: The normalized event
            event_id: The assigned event ID

        Returns:
            list[str]: IDs of created/updated entities
        """
        entity_ids = []

        try:
            # Get the appropriate extractor for this source
            extractor = self._entity_extractors.get(event.source)
            if not extractor:
                logger.debug("no_entity_extractor", source=event.source.value)
                return entity_ids

            # Extract entities from the event
            entities = await extractor(event)

            # Create/update each entity in Neo4j
            for entity_data in entities:
                entity_id = await self._create_or_update_entity(entity_data, event_id)
                if entity_id:
                    entity_ids.append(entity_id)

            logger.info(
                "entities_created_from_event",
                event_id=event_id,
                source=event.source.value,
                entity_count=len(entity_ids),
            )

        except Exception as e:
            logger.error(
                "entity_creation_failed",
                event_id=event_id,
                error=str(e),
            )

        return entity_ids

    async def _create_or_update_entity(
        self, entity_data: dict[str, Any], event_id: str
    ) -> str | None:
        """
        Create or update an entity in Neo4j.

        Args:
            entity_data: Entity data including type and properties
            event_id: Source event ID for linking

        Returns:
            str | None: Entity ID if created/updated
        """
        entity_type = entity_data.pop("entity_type")
        match_key = entity_data.pop("match_key", None)
        match_value = entity_data.pop("match_value", None)

        try:
            # Check if entity already exists
            existing_entity = None
            if match_key and match_value:
                existing_entity = await self._find_existing_entity(
                    entity_type, match_key, match_value
                )

            if existing_entity:
                # Update existing entity
                entity_id = existing_entity["id"]
                await self._update_entity(entity_id, entity_type, entity_data)
                logger.debug(
                    "entity_updated",
                    entity_id=entity_id,
                    entity_type=entity_type.value,
                )
            else:
                # Create new entity
                entity_id = str(uuid.uuid4())
                entity_data["id"] = entity_id
                entity_data["created_at"] = datetime.now(UTC).isoformat()
                entity_data["source_event_id"] = event_id

                await self._create_entity(entity_type, entity_data)
                logger.debug(
                    "entity_created",
                    entity_id=entity_id,
                    entity_type=entity_type.value,
                )

            # Link entity to event
            await self._link_entity_to_event(entity_id, entity_type, event_id)

            # Log audit event
            audit_logger.log_entity_access(
                entity_type=entity_type.value,
                entity_id=entity_id,
                action="auto_create" if not existing_entity else "auto_update",
                user_id="system",
                details={"source_event_id": event_id},
            )

            return entity_id

        except Exception as e:
            logger.error(
                "entity_operation_failed",
                entity_type=entity_type.value,
                error=str(e),
            )
            return None

    async def _find_existing_entity(
        self, entity_type: EntityType, match_key: str, match_value: Any
    ) -> dict[str, Any] | None:
        """Find an existing entity by a unique key."""
        query = f"""
        MATCH (n:{entity_type.value})
        WHERE n.{match_key} = $match_value
        RETURN n
        LIMIT 1
        """

        result = await self._neo4j.execute_query(query, {"match_value": match_value})

        if result and len(result) > 0:
            return dict(result[0]["n"])
        return None

    async def _create_entity(self, entity_type: EntityType, properties: dict[str, Any]) -> None:
        """Create a new entity node in Neo4j."""
        # Filter out None values
        props = {k: v for k, v in properties.items() if v is not None}

        query = f"""
        CREATE (n:{entity_type.value} $props)
        RETURN n
        """

        await self._neo4j.execute_query(query, {"props": props})

    async def _update_entity(
        self, entity_id: str, entity_type: EntityType, properties: dict[str, Any]
    ) -> None:
        """Update an existing entity node."""
        # Filter out None values and add updated timestamp
        props = {k: v for k, v in properties.items() if v is not None}
        props["updated_at"] = datetime.now(UTC).isoformat()

        set_clauses = ", ".join([f"n.{k} = ${k}" for k in props.keys()])

        query = f"""
        MATCH (n:{entity_type.value} {{id: $entity_id}})
        SET {set_clauses}
        RETURN n
        """

        params = {"entity_id": entity_id, **props}
        await self._neo4j.execute_query(query, params)

    async def _link_entity_to_event(
        self, entity_id: str, entity_type: EntityType, event_id: str
    ) -> None:
        """Create a relationship between entity and source event."""
        query = f"""
        MATCH (e:Event {{id: $event_id}})
        MATCH (n:{entity_type.value} {{id: $entity_id}})
        MERGE (n)-[r:MENTIONED_IN]->(e)
        SET r.created_at = $timestamp
        RETURN r
        """

        await self._neo4j.execute_query(
            query,
            {
                "event_id": event_id,
                "entity_id": entity_id,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    async def _extract_from_flock(self, event: EventCreate) -> list[dict[str, Any]]:
        """Extract entities from Flock LPR events."""
        entities = []
        metadata = event.metadata

        # Extract vehicle entity
        plate_number = metadata.get("plate_number")
        if plate_number:
            vehicle_entity = {
                "entity_type": EntityType.VEHICLE,
                "match_key": "plate_number",
                "match_value": plate_number,
                "plate_number": plate_number,
                "plate_state": metadata.get("plate_state"),
                "make": metadata.get("vehicle_make"),
                "model": metadata.get("vehicle_model"),
                "color": metadata.get("vehicle_color"),
                "year": metadata.get("vehicle_year"),
                "last_seen_at": event.timestamp.isoformat(),
                "last_seen_location": event.address,
                "last_seen_latitude": event.location.latitude if event.location else None,
                "last_seen_longitude": event.location.longitude if event.location else None,
            }
            entities.append(vehicle_entity)

            # Create license plate entity
            plate_entity = {
                "entity_type": EntityType.LICENSE_PLATE,
                "match_key": "plate_number",
                "match_value": plate_number,
                "plate_number": plate_number,
                "plate_state": metadata.get("plate_state"),
                "last_seen_at": event.timestamp.isoformat(),
            }
            entities.append(plate_entity)

        # Extract camera entity
        camera_id = metadata.get("camera_id")
        if camera_id:
            camera_entity = {
                "entity_type": EntityType.CAMERA,
                "match_key": "camera_id",
                "match_value": camera_id,
                "camera_id": camera_id,
                "camera_name": metadata.get("camera_name"),
                "source": "flock",
                "latitude": event.location.latitude if event.location else None,
                "longitude": event.location.longitude if event.location else None,
                "address": event.address,
            }
            entities.append(camera_entity)

        return entities

    async def _extract_from_shotspotter(self, event: EventCreate) -> list[dict[str, Any]]:
        """Extract entities from ShotSpotter events."""
        entities = []
        metadata = event.metadata

        # Create incident entity for gunshot event
        incident_entity = {
            "entity_type": EntityType.INCIDENT,
            "match_key": "source_event_id",
            "match_value": event.source_event_id,
            "source_event_id": event.source_event_id,
            "incident_type": "gunshot",
            "status": "active",
            "reported_at": event.timestamp.isoformat(),
            "latitude": event.location.latitude if event.location else None,
            "longitude": event.location.longitude if event.location else None,
            "address": event.address,
            "rounds_detected": metadata.get("rounds_detected"),
            "confidence": metadata.get("confidence"),
            "source": "shotspotter",
        }
        entities.append(incident_entity)

        # Create address entity if available
        if event.address:
            address_entity = {
                "entity_type": EntityType.ADDRESS,
                "match_key": "full_address",
                "match_value": event.address,
                "full_address": event.address,
                "latitude": event.location.latitude if event.location else None,
                "longitude": event.location.longitude if event.location else None,
                "last_incident_at": event.timestamp.isoformat(),
                "incident_count": 1,  # Will be incremented on updates
            }
            entities.append(address_entity)

        return entities

    async def _extract_from_milestone(self, event: EventCreate) -> list[dict[str, Any]]:
        """Extract entities from Milestone camera events."""
        entities = []
        metadata = event.metadata

        # Extract camera entity
        camera_id = metadata.get("camera_id")
        if camera_id:
            camera_entity = {
                "entity_type": EntityType.CAMERA,
                "match_key": "camera_id",
                "match_value": camera_id,
                "camera_id": camera_id,
                "camera_name": metadata.get("camera_name"),
                "source": "milestone",
                "latitude": event.location.latitude if event.location else None,
                "longitude": event.location.longitude if event.location else None,
                "address": event.address,
                "last_alert_at": event.timestamp.isoformat(),
            }
            entities.append(camera_entity)

        return entities

    async def _extract_from_onesolution(self, event: EventCreate) -> list[dict[str, Any]]:
        """Extract entities from OneSolution CAD/RMS events."""
        entities = []
        metadata = event.metadata

        # Create incident entity
        incident_id = metadata.get("incident_id")
        if incident_id:
            incident_entity = {
                "entity_type": EntityType.INCIDENT,
                "match_key": "incident_number",
                "match_value": metadata.get("incident_number"),
                "incident_id": incident_id,
                "incident_number": metadata.get("incident_number"),
                "incident_type": metadata.get("incident_type"),
                "call_type": metadata.get("call_type"),
                "status": metadata.get("status"),
                "priority_code": metadata.get("priority_code"),
                "reported_at": event.timestamp.isoformat(),
                "latitude": event.location.latitude if event.location else None,
                "longitude": event.location.longitude if event.location else None,
                "address": event.address,
                "beat": metadata.get("beat"),
                "district": metadata.get("district"),
                "disposition": metadata.get("disposition"),
                "source": "onesolution",
            }
            entities.append(incident_entity)

        # Create address entity
        if event.address:
            address_entity = {
                "entity_type": EntityType.ADDRESS,
                "match_key": "full_address",
                "match_value": event.address,
                "full_address": event.address,
                "latitude": event.location.latitude if event.location else None,
                "longitude": event.location.longitude if event.location else None,
                "last_incident_at": event.timestamp.isoformat(),
            }
            entities.append(address_entity)

        return entities

    async def _extract_from_ness(self, event: EventCreate) -> list[dict[str, Any]]:
        """Extract entities from NESS RMS events."""
        entities = []
        metadata = event.metadata

        # Extract person entity if present
        person_id = metadata.get("person_id")
        if person_id:
            person_entity = {
                "entity_type": EntityType.PERSON,
                "match_key": "ness_person_id",
                "match_value": person_id,
                "ness_person_id": person_id,
                "has_warrant": metadata.get("has_warrant", False),
                "alert_flag": metadata.get("alert_flag", False),
                "alert_reason": metadata.get("alert_reason"),
                "last_updated_at": event.timestamp.isoformat(),
                "source": "ness",
            }
            entities.append(person_entity)

        return entities

    async def _extract_from_bwc(self, event: EventCreate) -> list[dict[str, Any]]:
        """Extract entities from BWC events."""
        entities: list[dict[str, Any]] = []

        # BWC events don't typically create new entities
        # but we could track officer locations if needed
        # Access event.metadata if needed for future entity extraction

        return entities

    async def _extract_from_hotsheets(self, event: EventCreate) -> list[dict[str, Any]]:
        """Extract entities from HotSheets events."""
        entities = []
        metadata = event.metadata

        # Extract vehicle entity if plate present
        plate_number = metadata.get("plate_number")
        if plate_number:
            vehicle_entity = {
                "entity_type": EntityType.VEHICLE,
                "match_key": "plate_number",
                "match_value": plate_number,
                "plate_number": plate_number,
                "plate_state": metadata.get("plate_state"),
                "description": metadata.get("vehicle_description"),
                "is_wanted": True,
                "wanted_reason": metadata.get("reason"),
                "ncic_number": metadata.get("ncic_number"),
                "case_number": metadata.get("case_number"),
                "hotsheet_entered_at": metadata.get("entered_date"),
                "hotsheet_expires_at": metadata.get("expiration_date"),
                "source": "hotsheets",
            }
            entities.append(vehicle_entity)

        # Extract person entity if present
        person_name = metadata.get("person_name")
        if person_name:
            person_entity = {
                "entity_type": EntityType.PERSON,
                "match_key": "hotsheet_name",
                "match_value": person_name,
                "hotsheet_name": person_name,
                "description": metadata.get("person_description"),
                "is_wanted": True,
                "wanted_reason": metadata.get("reason"),
                "ncic_number": metadata.get("ncic_number"),
                "case_number": metadata.get("case_number"),
                "hotsheet_entered_at": metadata.get("entered_date"),
                "hotsheet_expires_at": metadata.get("expiration_date"),
                "source": "hotsheets",
            }
            entities.append(person_entity)

        return entities


# Global instance
_entity_creator: EntityAutoCreator | None = None


def get_entity_creator() -> EntityAutoCreator:
    """Get the entity auto-creator instance."""
    global _entity_creator
    if _entity_creator is None:
        _entity_creator = EntityAutoCreator()
    return _entity_creator
