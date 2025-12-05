"""
Database connection managers for the G3TI RTCC-UIP Backend.

This module provides connection management for:
- Neo4j: Graph database for entity relationships
- Elasticsearch: Full-text search and narrative indexing
- Redis: Caching and message brokering

All connections are managed as singletons with proper lifecycle management
for use with FastAPI's dependency injection system.
"""

from app.db.elasticsearch import ElasticsearchManager, get_elasticsearch
from app.db.neo4j import Neo4jManager, get_neo4j
from app.db.redis import RedisManager, get_redis

__all__ = [
    "Neo4jManager",
    "get_neo4j",
    "ElasticsearchManager",
    "get_elasticsearch",
    "RedisManager",
    "get_redis",
]
