"""
G3TI Real Time Crime Center Unified Intelligence Platform (RTCC-UIP) Backend

This package contains the core backend API for the RTCC-UIP system, providing:
- Real-time event processing and WebSocket communication
- Investigation management and search capabilities
- Entity graph management via Neo4j
- Authentication and role-based access control
- Integration interfaces for external systems (Milestone, Flock, ShotSpotter, etc.)

Architecture:
- FastAPI for REST API and WebSocket endpoints
- Neo4j for entity graph database
- Elasticsearch for full-text search and narrative indexing
- Redis for caching and message brokering
- Celery for background task processing
"""

__version__ = "1.0.0"
__author__ = "G3TI Development Team"
