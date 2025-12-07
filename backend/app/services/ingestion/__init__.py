"""
Real-time event ingestion engine for the G3TI RTCC-UIP Backend.

This module provides the core event ingestion pipeline that:
- Receives events from all integration sources
- Normalizes events to a common format
- Creates/updates entities in Neo4j automatically
- Indexes events in Elasticsearch
- Broadcasts events via WebSocket
"""

from app.services.ingestion.engine import (
    EventIngestionEngine,
    get_ingestion_engine,
)
from app.services.ingestion.entity_creator import EntityAutoCreator
from app.services.ingestion.indexer import EventIndexer
from app.services.ingestion.normalizer import EventNormalizer

__all__ = [
    "EventIngestionEngine",
    "get_ingestion_engine",
    "EventNormalizer",
    "EntityAutoCreator",
    "EventIndexer",
]
