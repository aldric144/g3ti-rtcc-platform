"""
Search services for the G3TI RTCC-UIP Backend.

This module provides Elasticsearch-based search functionality including:
- Full-text search across all entities
- Investigative search with filters
- Narrative indexing and retrieval
- Search suggestions and faceting
"""

from app.services.search.search_service import SearchService

__all__ = ["SearchService"]
