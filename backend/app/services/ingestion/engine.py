"""
Real-time event ingestion engine for the G3TI RTCC-UIP Backend.

This module provides the core event ingestion pipeline that orchestrates:
- Event normalization from all sources
- Entity auto-creation in Neo4j
- Event indexing in Elasticsearch
- Real-time WebSocket broadcasting
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.logging import audit_logger, get_logger
from app.db.neo4j import get_neo4j_manager
from app.db.redis import get_redis_manager
from app.schemas.events import (
    EventCreate,
    EventResponse,
    EventSource,
    WebSocketMessage,
    WebSocketMessageType,
)
from app.services.events.websocket_manager import get_websocket_manager
from app.services.ingestion.entity_creator import EntityAutoCreator, get_entity_creator
from app.services.ingestion.indexer import EventIndexer, get_event_indexer
from app.services.ingestion.normalizer import EventNormalizer

logger = get_logger(__name__)


class EventIngestionEngine:
    """
    Core event ingestion engine that processes events from all sources.

    The engine provides a unified pipeline for:
    1. Receiving raw events from integrations
    2. Normalizing events to a standard format
    3. Creating/updating entities in Neo4j
    4. Indexing events in Elasticsearch
    5. Broadcasting events via WebSocket
    6. Publishing events to Redis for other services
    """

    def __init__(self) -> None:
        """Initialize the ingestion engine."""
        self._normalizer = EventNormalizer()
        self._entity_creator: EntityAutoCreator | None = None
        self._indexer: EventIndexer | None = None
        self._neo4j = get_neo4j_manager()
        self._redis = get_redis_manager()
        self._ws_manager = get_websocket_manager()

        # Statistics
        self._events_processed = 0
        self._events_failed = 0
        self._started_at: datetime | None = None
        self._is_running = False

    async def start(self) -> None:
        """Start the ingestion engine."""
        if self._is_running:
            return

        logger.info("ingestion_engine_starting")

        # Initialize components
        self._entity_creator = get_entity_creator()
        self._indexer = get_event_indexer()

        # Ensure Elasticsearch indices exist
        await self._indexer.ensure_indices()

        self._started_at = datetime.now(UTC)
        self._is_running = True

        logger.info("ingestion_engine_started")

    async def stop(self) -> None:
        """Stop the ingestion engine."""
        if not self._is_running:
            return

        logger.info(
            "ingestion_engine_stopping",
            events_processed=self._events_processed,
            events_failed=self._events_failed,
        )

        self._is_running = False

    async def ingest_raw_event(
        self, source: EventSource, raw_data: dict[str, Any]
    ) -> EventResponse | None:
        """
        Ingest a raw event from an integration source.

        This is the main entry point for all events. It:
        1. Normalizes the raw data
        2. Processes the normalized event
        3. Returns the processed event response

        Args:
            source: The event source
            raw_data: Raw event data from the source

        Returns:
            EventResponse | None: Processed event or None if failed
        """
        if not self._is_running:
            logger.warning("ingestion_engine_not_running")
            return None

        try:
            # Normalize the event
            normalized_event = await self._normalizer.normalize(source, raw_data)

            # Process the normalized event
            return await self.ingest_event(normalized_event)

        except Exception as e:
            self._events_failed += 1
            logger.error(
                "raw_event_ingestion_failed",
                source=source.value,
                error=str(e),
            )
            return None

    async def ingest_event(self, event: EventCreate) -> EventResponse | None:
        """
        Ingest a normalized event.

        Processes the event through the full pipeline:
        1. Assigns event ID and timestamps
        2. Stores event in Neo4j
        3. Creates/updates related entities
        4. Indexes event in Elasticsearch
        5. Broadcasts via WebSocket
        6. Publishes to Redis

        Args:
            event: Normalized event to ingest

        Returns:
            EventResponse | None: Processed event or None if failed
        """
        if not self._is_running:
            logger.warning("ingestion_engine_not_running")
            return None

        event_id = str(uuid.uuid4())
        created_at = datetime.now(UTC)

        try:
            # Store event in Neo4j
            await self._store_event_in_neo4j(event, event_id, created_at)

            # Create/update entities
            entity_ids = []
            if self._entity_creator:
                entity_ids = await self._entity_creator.process_event(event, event_id)

            # Index in Elasticsearch
            if self._indexer:
                await self._indexer.index_event(event, event_id)

            # Build response
            event_response = EventResponse(
                id=event_id,
                event_type=event.event_type,
                source=event.source,
                priority=event.priority,
                title=event.title,
                description=event.description,
                location=event.location,
                address=event.address,
                timestamp=event.timestamp,
                metadata=event.metadata,
                tags=event.tags,
                source_event_id=event.source_event_id,
                created_at=created_at,
                acknowledged=False,
                related_entity_ids=entity_ids,
                related_incident_id=event.related_incident_id,
            )

            # Broadcast via WebSocket
            await self._broadcast_event(event_response)

            # Publish to Redis for other services
            await self._publish_to_redis(event_response)

            # Update statistics
            self._events_processed += 1

            # Audit log
            audit_logger.log_system_event(
                event_type="event_ingested",
                details={
                    "event_id": event_id,
                    "event_type": event.event_type.value,
                    "source": event.source.value,
                    "entity_count": len(entity_ids),
                },
            )

            logger.info(
                "event_ingested",
                event_id=event_id,
                event_type=event.event_type.value,
                source=event.source.value,
                entity_count=len(entity_ids),
            )

            return event_response

        except Exception as e:
            self._events_failed += 1
            logger.error(
                "event_ingestion_failed",
                event_id=event_id,
                error=str(e),
            )
            return None

    async def _store_event_in_neo4j(
        self, event: EventCreate, event_id: str, created_at: datetime
    ) -> None:
        """Store event as a node in Neo4j."""
        query = """
        CREATE (e:Event {
            id: $id,
            event_type: $event_type,
            source: $source,
            priority: $priority,
            title: $title,
            description: $description,
            address: $address,
            latitude: $latitude,
            longitude: $longitude,
            timestamp: $timestamp,
            created_at: $created_at,
            source_event_id: $source_event_id,
            acknowledged: false,
            tags: $tags
        })
        RETURN e
        """

        params = {
            "id": event_id,
            "event_type": event.event_type.value,
            "source": event.source.value,
            "priority": event.priority.value,
            "title": event.title,
            "description": event.description,
            "address": event.address,
            "latitude": event.location.latitude if event.location else None,
            "longitude": event.location.longitude if event.location else None,
            "timestamp": event.timestamp.isoformat(),
            "created_at": created_at.isoformat(),
            "source_event_id": event.source_event_id,
            "tags": event.tags,
        }

        await self._neo4j.execute_query(query, params)

    async def _broadcast_event(self, event: EventResponse) -> None:
        """Broadcast event via WebSocket to connected clients."""
        try:
            message = WebSocketMessage(
                type=WebSocketMessageType.EVENT,
                payload={
                    "event": event.model_dump(mode="json"),
                },
                timestamp=datetime.now(UTC),
                message_id=str(uuid.uuid4()),
            )

            await self._ws_manager.broadcast_event(event, message)

        except Exception as e:
            logger.error("websocket_broadcast_failed", error=str(e))

    async def _publish_to_redis(self, event: EventResponse) -> None:
        """Publish event to Redis for other services."""
        try:
            channel = f"rtcc:events:{event.source.value}"
            message = event.model_dump_json()

            await self._redis.publish(channel, message)

            # Also publish to priority-based channels for filtering
            priority_channel = f"rtcc:events:priority:{event.priority.value}"
            await self._redis.publish(priority_channel, message)

        except Exception as e:
            logger.error("redis_publish_failed", error=str(e))

    async def ingest_batch(
        self, source: EventSource, events: list[dict[str, Any]]
    ) -> list[EventResponse]:
        """
        Ingest a batch of raw events.

        Args:
            source: The event source
            events: List of raw event data

        Returns:
            list[EventResponse]: Successfully processed events
        """
        results = []

        for raw_data in events:
            result = await self.ingest_raw_event(source, raw_data)
            if result:
                results.append(result)

        logger.info(
            "batch_ingestion_complete",
            source=source.value,
            total=len(events),
            successful=len(results),
        )

        return results

    def get_stats(self) -> dict[str, Any]:
        """Get ingestion engine statistics."""
        uptime = None
        if self._started_at:
            uptime = (datetime.now(UTC) - self._started_at).total_seconds()

        return {
            "is_running": self._is_running,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "uptime_seconds": uptime,
            "events_processed": self._events_processed,
            "events_failed": self._events_failed,
            "success_rate": (
                self._events_processed / (self._events_processed + self._events_failed)
                if (self._events_processed + self._events_failed) > 0
                else 1.0
            ),
        }


# Global instance
_ingestion_engine: EventIngestionEngine | None = None


def get_ingestion_engine() -> EventIngestionEngine:
    """Get the ingestion engine instance."""
    global _ingestion_engine
    if _ingestion_engine is None:
        _ingestion_engine = EventIngestionEngine()
    return _ingestion_engine
