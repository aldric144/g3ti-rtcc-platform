"""
Event indexer for the G3TI RTCC-UIP Backend.

This module indexes events in Elasticsearch for full-text search
and analytics capabilities.
"""

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import get_elasticsearch_manager
from app.schemas.events import EventCreate

logger = get_logger(__name__)

# Elasticsearch index names
EVENTS_INDEX = "rtcc_events"
INCIDENTS_INDEX = "rtcc_incidents"
ENTITIES_INDEX = "rtcc_entities"


class EventIndexer:
    """
    Indexes events in Elasticsearch for search and analytics.

    Provides methods for indexing events, searching, and
    managing the event indices.
    """

    def __init__(self) -> None:
        """Initialize the event indexer."""
        self._es = get_elasticsearch_manager()
        self._indices_created = False

    async def ensure_indices(self) -> None:
        """Ensure all required indices exist with proper mappings."""
        if self._indices_created:
            return

        try:
            # Create events index
            await self._create_events_index()

            # Create incidents index
            await self._create_incidents_index()

            # Create entities index
            await self._create_entities_index()

            self._indices_created = True
            logger.info("elasticsearch_indices_created")

        except Exception as e:
            logger.error("index_creation_failed", error=str(e))

    async def _create_events_index(self) -> None:
        """Create the events index with mappings."""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "priority": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "standard",
                    },
                    "address": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "location": {"type": "geo_point"},
                    "timestamp": {"type": "date"},
                    "created_at": {"type": "date"},
                    "source_event_id": {"type": "keyword"},
                    "acknowledged": {"type": "boolean"},
                    "acknowledged_by": {"type": "keyword"},
                    "acknowledged_at": {"type": "date"},
                    "related_entity_ids": {"type": "keyword"},
                    "related_incident_id": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "metadata": {
                        "type": "object",
                        "enabled": True,
                        "dynamic": True,
                    },
                }
            },
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "refresh_interval": "1s",
            },
        }

        await self._es.create_index(EVENTS_INDEX, mapping)

    async def _create_incidents_index(self) -> None:
        """Create the incidents index with mappings."""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "incident_number": {"type": "keyword"},
                    "incident_type": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "priority": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "narrative": {
                        "type": "text",
                        "analyzer": "standard",
                    },
                    "address": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "location": {"type": "geo_point"},
                    "reported_at": {"type": "date"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "closed_at": {"type": "date"},
                    "source": {"type": "keyword"},
                    "responding_units": {"type": "keyword"},
                    "related_entity_ids": {"type": "keyword"},
                    "related_event_ids": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                }
            },
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
            },
        }

        await self._es.create_index(INCIDENTS_INDEX, mapping)

    async def _create_entities_index(self) -> None:
        """Create the entities index with mappings."""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "entity_type": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "standard",
                    },
                    "identifiers": {"type": "keyword"},
                    "aliases": {"type": "keyword"},
                    "location": {"type": "geo_point"},
                    "address": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "source": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "is_wanted": {"type": "boolean"},
                    "has_warrant": {"type": "boolean"},
                    # Vehicle-specific fields
                    "plate_number": {"type": "keyword"},
                    "plate_state": {"type": "keyword"},
                    "vehicle_make": {"type": "keyword"},
                    "vehicle_model": {"type": "keyword"},
                    "vehicle_color": {"type": "keyword"},
                    "vehicle_year": {"type": "integer"},
                    # Person-specific fields
                    "first_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "last_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "date_of_birth": {"type": "date"},
                }
            },
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
            },
        }

        await self._es.create_index(ENTITIES_INDEX, mapping)

    async def index_event(self, event: EventCreate, event_id: str) -> bool:
        """
        Index an event in Elasticsearch.

        Args:
            event: The event to index
            event_id: The assigned event ID

        Returns:
            bool: True if indexed successfully
        """
        try:
            await self.ensure_indices()

            # Build document
            doc = {
                "id": event_id,
                "event_type": event.event_type.value,
                "source": event.source.value,
                "priority": event.priority.value,
                "title": event.title,
                "description": event.description,
                "address": event.address,
                "timestamp": event.timestamp.isoformat(),
                "created_at": datetime.now(UTC).isoformat(),
                "source_event_id": event.source_event_id,
                "acknowledged": False,
                "related_entity_ids": event.related_entity_ids,
                "related_incident_id": event.related_incident_id,
                "tags": event.tags,
                "metadata": event.metadata,
            }

            # Add location if present
            if event.location:
                doc["location"] = {
                    "lat": event.location.latitude,
                    "lon": event.location.longitude,
                }

            # Index the document
            await self._es.index_document(EVENTS_INDEX, event_id, doc)

            logger.debug(
                "event_indexed",
                event_id=event_id,
                event_type=event.event_type.value,
            )

            return True

        except Exception as e:
            logger.error(
                "event_indexing_failed",
                event_id=event_id,
                error=str(e),
            )
            return False

    async def index_entity(
        self, entity_type: str, entity_id: str, entity_data: dict[str, Any]
    ) -> bool:
        """
        Index an entity in Elasticsearch.

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            entity_data: Entity data to index

        Returns:
            bool: True if indexed successfully
        """
        try:
            await self.ensure_indices()

            # Build document
            doc = {
                "id": entity_id,
                "entity_type": entity_type,
                **entity_data,
            }

            # Handle location
            if "latitude" in entity_data and "longitude" in entity_data:
                lat = entity_data.get("latitude")
                lon = entity_data.get("longitude")
                if lat is not None and lon is not None:
                    doc["location"] = {"lat": lat, "lon": lon}

            # Index the document
            await self._es.index_document(ENTITIES_INDEX, entity_id, doc)

            logger.debug(
                "entity_indexed",
                entity_id=entity_id,
                entity_type=entity_type,
            )

            return True

        except Exception as e:
            logger.error(
                "entity_indexing_failed",
                entity_id=entity_id,
                error=str(e),
            )
            return False

    async def search_events(
        self,
        query: str | None = None,
        event_types: list[str] | None = None,
        sources: list[str] | None = None,
        priorities: list[str] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        location: dict[str, float] | None = None,
        radius_km: float = 5.0,
        acknowledged: bool | None = None,
        tags: list[str] | None = None,
        size: int = 50,
        from_: int = 0,
    ) -> dict[str, Any]:
        """
        Search events in Elasticsearch.

        Args:
            query: Full-text search query
            event_types: Filter by event types
            sources: Filter by sources
            priorities: Filter by priorities
            start_time: Filter by start time
            end_time: Filter by end time
            location: Center point for geo search
            radius_km: Radius for geo search
            acknowledged: Filter by acknowledgment status
            tags: Filter by tags
            size: Number of results to return
            from_: Offset for pagination

        Returns:
            dict: Search results with hits and total count
        """
        try:
            # Build query
            must = []
            filter_clauses = []

            # Full-text search
            if query:
                must.append(
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^2", "description", "address", "tags"],
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                        }
                    }
                )

            # Event type filter
            if event_types:
                filter_clauses.append({"terms": {"event_type": event_types}})

            # Source filter
            if sources:
                filter_clauses.append({"terms": {"source": sources}})

            # Priority filter
            if priorities:
                filter_clauses.append({"terms": {"priority": priorities}})

            # Time range filter
            if start_time or end_time:
                range_filter = {"range": {"timestamp": {}}}
                if start_time:
                    range_filter["range"]["timestamp"]["gte"] = start_time.isoformat()
                if end_time:
                    range_filter["range"]["timestamp"]["lte"] = end_time.isoformat()
                filter_clauses.append(range_filter)

            # Geo filter
            if location:
                filter_clauses.append(
                    {
                        "geo_distance": {
                            "distance": f"{radius_km}km",
                            "location": {
                                "lat": location["latitude"],
                                "lon": location["longitude"],
                            },
                        }
                    }
                )

            # Acknowledged filter
            if acknowledged is not None:
                filter_clauses.append({"term": {"acknowledged": acknowledged}})

            # Tags filter
            if tags:
                filter_clauses.append({"terms": {"tags": tags}})

            # Build final query
            es_query = {
                "bool": {
                    "must": must if must else [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            }

            # Execute search
            result = await self._es.search(
                index=EVENTS_INDEX,
                query=es_query,
                size=size,
                from_=from_,
                sort=[{"timestamp": {"order": "desc"}}],
            )

            return result

        except Exception as e:
            logger.error("event_search_failed", error=str(e))
            return {"hits": {"hits": [], "total": {"value": 0}}}

    async def search_entities(
        self,
        query: str | None = None,
        entity_types: list[str] | None = None,
        plate_number: str | None = None,
        is_wanted: bool | None = None,
        location: dict[str, float] | None = None,
        radius_km: float = 5.0,
        size: int = 50,
        from_: int = 0,
    ) -> dict[str, Any]:
        """
        Search entities in Elasticsearch.

        Args:
            query: Full-text search query
            entity_types: Filter by entity types
            plate_number: Search by plate number
            is_wanted: Filter by wanted status
            location: Center point for geo search
            radius_km: Radius for geo search
            size: Number of results to return
            from_: Offset for pagination

        Returns:
            dict: Search results with hits and total count
        """
        try:
            must = []
            filter_clauses = []

            # Full-text search
            if query:
                must.append(
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "name^2",
                                "description",
                                "aliases",
                                "plate_number^3",
                                "first_name",
                                "last_name",
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                        }
                    }
                )

            # Entity type filter
            if entity_types:
                filter_clauses.append({"terms": {"entity_type": entity_types}})

            # Plate number search
            if plate_number:
                must.append({"wildcard": {"plate_number": f"*{plate_number.upper()}*"}})

            # Wanted filter
            if is_wanted is not None:
                filter_clauses.append({"term": {"is_wanted": is_wanted}})

            # Geo filter
            if location:
                filter_clauses.append(
                    {
                        "geo_distance": {
                            "distance": f"{radius_km}km",
                            "location": {
                                "lat": location["latitude"],
                                "lon": location["longitude"],
                            },
                        }
                    }
                )

            # Build final query
            es_query = {
                "bool": {
                    "must": must if must else [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            }

            # Execute search
            result = await self._es.search(
                index=ENTITIES_INDEX,
                query=es_query,
                size=size,
                from_=from_,
            )

            return result

        except Exception as e:
            logger.error("entity_search_failed", error=str(e))
            return {"hits": {"hits": [], "total": {"value": 0}}}

    async def update_event_acknowledgment(
        self, event_id: str, acknowledged: bool, acknowledged_by: str | None = None
    ) -> bool:
        """Update event acknowledgment status."""
        try:
            doc = {
                "acknowledged": acknowledged,
                "acknowledged_at": datetime.now(UTC).isoformat() if acknowledged else None,
                "acknowledged_by": acknowledged_by,
            }

            await self._es.update_document(EVENTS_INDEX, event_id, doc)
            return True

        except Exception as e:
            logger.error(
                "acknowledgment_update_failed",
                event_id=event_id,
                error=str(e),
            )
            return False


# Global instance
_event_indexer: EventIndexer | None = None


def get_event_indexer() -> EventIndexer:
    """Get the event indexer instance."""
    global _event_indexer
    if _event_indexer is None:
        _event_indexer = EventIndexer()
    return _event_indexer
