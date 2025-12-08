"""
Search service for the G3TI RTCC-UIP Backend.

This service provides investigative search capabilities using Elasticsearch,
including full-text search, filtering, and faceted results.

The search service supports:
- Multi-entity search (persons, vehicles, incidents, etc.)
- Geographic filtering
- Date range filtering
- Relevance scoring
- Result highlighting
"""

import time
from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import ElasticsearchManager, get_elasticsearch
from app.schemas.investigations import (
    SearchQuery,
    SearchResult,
    SearchResultItem,
)

logger = get_logger(__name__)


class SearchService:
    """
    Service for investigative search operations.

    Provides methods for searching across all entity types with
    support for filtering, faceting, and relevance scoring.
    """

    # Mapping of entity types to Elasticsearch indices
    ENTITY_INDEX_MAP = {
        "investigation": "investigations",
        "incident": "incidents",
        "person": "persons",
        "vehicle": "vehicles",
        "audit": "audit_logs",
    }

    # Fields to search for each entity type
    SEARCH_FIELDS = {
        "investigations": [
            "title^3",
            "narrative^2",
            "synopsis^2",
            "case_number^4",
            "tags",
        ],
        "incidents": [
            "incident_number^4",
            "title^3",
            "description^2",
            "address",
        ],
        "persons": [
            "full_name^4",
            "first_name^3",
            "last_name^3",
            "aliases^2",
            "identifiers",
        ],
    }

    def __init__(self, es_manager: ElasticsearchManager | None = None) -> None:
        """
        Initialize the search service.

        Args:
            es_manager: Elasticsearch manager instance (optional)
        """
        self._es_manager = es_manager

    async def _get_es(self) -> ElasticsearchManager:
        """Get Elasticsearch manager, initializing if needed."""
        if self._es_manager is None:
            self._es_manager = await get_elasticsearch()
        return self._es_manager

    async def search(self, query: SearchQuery) -> SearchResult:
        """
        Execute an investigative search.

        Args:
            query: Search query parameters

        Returns:
            SearchResult: Search results with facets and suggestions
        """
        start_time = time.time()

        try:
            es = await self._get_es()
        except Exception as e:
            logger.warning("elasticsearch_unavailable", error=str(e))
            # Return empty results if Elasticsearch is not available
            return SearchResult(
                query=query.query,
                total=0,
                page=query.page,
                page_size=query.page_size,
                pages=0,
                items=[],
                facets={},
                suggestions=[],
                took_ms=0,
            )

        # Determine which indices to search
        indices = self._get_search_indices(query.entity_types)

        # Build the search query
        es_query = self._build_query(query)

        # Calculate pagination
        from_offset = (query.page - 1) * query.page_size

        # Execute search across all relevant indices
        all_results: list[SearchResultItem] = []
        total_hits = 0
        facets: dict[str, dict[str, int]] = {}

        for index_name in indices:
            try:
                # Get search fields for this index (reserved for future field-specific search)
                _search_fields = self.SEARCH_FIELDS.get(index_name, ["*"])  # noqa: F841

                result = await es.search(
                    index_name=index_name,
                    query=es_query,
                    size=query.page_size,
                    from_=from_offset,
                    highlight={
                        "fields": {
                            "*": {
                                "pre_tags": ["<mark>"],
                                "post_tags": ["</mark>"],
                            }
                        }
                    },
                )

                # Process hits
                hits = result.get("hits", {})
                total_hits += hits.get("total", {}).get("value", 0)

                for hit in hits.get("hits", []):
                    item = self._hit_to_result_item(hit, index_name)
                    all_results.append(item)

                # Process aggregations for facets
                aggs = result.get("aggregations", {})
                for agg_name, agg_data in aggs.items():
                    if agg_name not in facets:
                        facets[agg_name] = {}
                    for bucket in agg_data.get("buckets", []):
                        key = bucket.get("key")
                        count = bucket.get("doc_count", 0)
                        facets[agg_name][key] = facets[agg_name].get(key, 0) + count

            except Exception as e:
                logger.warning("search_index_error", index=index_name, error=str(e))
                continue

        # Sort results by score
        all_results.sort(key=lambda x: x.score, reverse=True)

        # Calculate pagination info
        total_pages = (total_hits + query.page_size - 1) // query.page_size if total_hits > 0 else 0

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info("search_executed", query=query.query, total_hits=total_hits, took_ms=elapsed_ms)

        return SearchResult(
            query=query.query,
            total=total_hits,
            page=query.page,
            page_size=query.page_size,
            pages=total_pages,
            items=all_results[: query.page_size],
            facets=facets,
            suggestions=await self._get_suggestions(query.query),
            took_ms=elapsed_ms,
        )

    async def index_entity(self, entity_type: str, entity_id: str, data: dict[str, Any]) -> bool:
        """
        Index an entity for search.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            data: Entity data to index

        Returns:
            bool: True if indexed successfully
        """
        try:
            es = await self._get_es()
            index_name = self.ENTITY_INDEX_MAP.get(entity_type)

            if not index_name:
                logger.warning("unknown_entity_type", entity_type=entity_type)
                return False

            await es.index_document(
                index_name=index_name, document=data, doc_id=entity_id, refresh=True
            )

            logger.debug("entity_indexed", entity_type=entity_type, entity_id=entity_id)

            return True

        except Exception as e:
            logger.error(
                "index_entity_error", entity_type=entity_type, entity_id=entity_id, error=str(e)
            )
            return False

    async def delete_entity(self, entity_type: str, entity_id: str) -> bool:
        """
        Remove an entity from the search index.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier

        Returns:
            bool: True if deleted successfully
        """
        try:
            es = await self._get_es()
            index_name = self.ENTITY_INDEX_MAP.get(entity_type)

            if not index_name:
                return False

            return await es.delete_document(index_name=index_name, doc_id=entity_id, refresh=True)

        except Exception as e:
            logger.error(
                "delete_entity_error", entity_type=entity_type, entity_id=entity_id, error=str(e)
            )
            return False

    def _get_search_indices(self, entity_types: list[str]) -> list[str]:
        """Get list of indices to search based on entity types."""
        if not entity_types:
            # Search all indices
            return list(self.ENTITY_INDEX_MAP.values())

        indices = []
        for entity_type in entity_types:
            index = self.ENTITY_INDEX_MAP.get(entity_type.lower())
            if index:
                indices.append(index)

        return indices or list(self.ENTITY_INDEX_MAP.values())

    def _build_query(self, query: SearchQuery) -> dict[str, Any]:
        """Build Elasticsearch query from search parameters."""
        must_clauses: list[dict[str, Any]] = []
        filter_clauses: list[dict[str, Any]] = []

        # Main text query
        if query.query:
            must_clauses.append(
                {
                    "multi_match": {
                        "query": query.query,
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                        "operator": "or",
                    }
                }
            )

        # Date range filter
        if query.date_from or query.date_to:
            date_range: dict[str, Any] = {}
            if query.date_from:
                date_range["gte"] = query.date_from.isoformat()
            if query.date_to:
                date_range["lte"] = query.date_to.isoformat()

            filter_clauses.append({"range": {"created_at": date_range}})

        # Geographic filter
        if query.location and query.radius_miles:
            filter_clauses.append(
                {
                    "geo_distance": {
                        "distance": f"{query.radius_miles}mi",
                        "location": {
                            "lat": query.location.latitude,
                            "lon": query.location.longitude,
                        },
                    }
                }
            )

        # Additional filters
        for field, value in query.filters.items():
            if isinstance(value, list):
                filter_clauses.append({"terms": {field: value}})
            else:
                filter_clauses.append({"term": {field: value}})

        # Build final query
        if must_clauses or filter_clauses:
            return {
                "bool": {
                    "must": must_clauses or [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            }

        return {"match_all": {}}

    def _hit_to_result_item(self, hit: dict[str, Any], index_name: str) -> SearchResultItem:
        """Convert Elasticsearch hit to SearchResultItem."""
        source = hit.get("_source", {})
        highlights = hit.get("highlight", {})

        # Determine entity type from index
        entity_type = "unknown"
        for etype, idx in self.ENTITY_INDEX_MAP.items():
            if idx == index_name:
                entity_type = etype
                break

        # Get title based on entity type
        title = (
            source.get("title")
            or source.get("full_name")
            or source.get("case_number")
            or source.get("incident_number")
            or f"{entity_type} {hit['_id']}"
        )

        # Get description
        description = (
            source.get("description") or source.get("synopsis") or source.get("narrative", "")[:200]
        )

        # Get location if available
        location = None
        if "location" in source and source["location"]:
            from app.schemas.common import GeoLocation

            loc = source["location"]
            if isinstance(loc, dict) and "lat" in loc and "lon" in loc:
                location = GeoLocation(latitude=loc["lat"], longitude=loc["lon"])

        # Get timestamp
        timestamp = None
        for ts_field in ["created_at", "occurred_at", "timestamp"]:
            if ts_field in source and source[ts_field]:
                try:
                    timestamp = datetime.fromisoformat(source[ts_field].replace("Z", "+00:00"))
                    break
                except (ValueError, AttributeError):
                    pass

        return SearchResultItem(
            id=hit["_id"],
            entity_type=entity_type,
            title=title,
            description=description,
            score=hit.get("_score", 0.0),
            highlights=highlights,
            metadata={
                k: v
                for k, v in source.items()
                if k not in ["title", "description", "location", "narrative"]
            },
            location=location,
            timestamp=timestamp,
        )

    async def _get_suggestions(self, query: str) -> list[str]:
        """
        Get search suggestions based on query.

        Args:
            query: Search query

        Returns:
            list: Suggested search terms
        """
        # In a full implementation, this would use Elasticsearch's
        # suggest API or a custom suggestion index
        # For now, return empty list
        return []


# Global search service instance
_search_service: SearchService | None = None


async def get_search_service() -> SearchService:
    """Get the search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
