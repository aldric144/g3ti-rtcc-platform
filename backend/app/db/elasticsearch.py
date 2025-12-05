"""
Elasticsearch connection manager for the G3TI RTCC-UIP Backend.

This module provides connection management and query execution for Elasticsearch,
used for full-text search, narrative indexing, and investigative search capabilities.

Elasticsearch indices:
- rtcc_investigations: Investigation records and narratives
- rtcc_incidents: Incident reports with full-text search
- rtcc_persons: Person records for search
- rtcc_audit_logs: CJIS-compliant audit logs
"""

from typing import Any

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import AuthenticationException
from elasticsearch.exceptions import ConnectionError as ESConnectionError

from app.core.config import settings
from app.core.exceptions import ElasticsearchConnectionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ElasticsearchManager:
    """
    Manages Elasticsearch connections and provides search methods.

    This class implements the singleton pattern to ensure only one client
    instance is created per application lifecycle.

    Usage:
        manager = ElasticsearchManager()
        await manager.connect()

        results = await manager.search(
            index="rtcc_investigations",
            query={"match": {"narrative": "suspect vehicle"}}
        )

        await manager.close()
    """

    _instance: "ElasticsearchManager | None" = None
    _client: AsyncElasticsearch | None = None

    def __new__(cls) -> "ElasticsearchManager":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """
        Establish connection to Elasticsearch.

        Raises:
            ElasticsearchConnectionError: If connection fails
        """
        if self._client is not None:
            return

        try:
            # Build connection kwargs
            kwargs: dict[str, Any] = {
                "hosts": settings.elasticsearch_hosts,
                "retry_on_timeout": True,
                "max_retries": 3,
            }

            # Add authentication if configured
            if settings.elasticsearch_user and settings.elasticsearch_password:
                kwargs["basic_auth"] = (
                    settings.elasticsearch_user,
                    settings.elasticsearch_password,
                )

            self._client = AsyncElasticsearch(**kwargs)

            # Verify connectivity
            info = await self._client.info()

            logger.info(
                "elasticsearch_connected",
                hosts=settings.elasticsearch_hosts,
                cluster_name=info.get("cluster_name"),
                version=info.get("version", {}).get("number"),
            )

        except AuthenticationException as e:
            logger.error("elasticsearch_auth_error", error=str(e))
            raise ElasticsearchConnectionError(f"Elasticsearch authentication failed: {e}")
        except ESConnectionError as e:
            logger.error("elasticsearch_connection_error", error=str(e))
            raise ElasticsearchConnectionError(f"Failed to connect to Elasticsearch: {e}")
        except Exception as e:
            logger.error("elasticsearch_error", error=str(e))
            raise ElasticsearchConnectionError(f"Elasticsearch error: {e}")

    async def close(self) -> None:
        """Close the Elasticsearch client connection."""
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("elasticsearch_disconnected")

    @property
    def client(self) -> AsyncElasticsearch:
        """
        Get the Elasticsearch client.

        Returns:
            AsyncElasticsearch: The Elasticsearch client

        Raises:
            ElasticsearchConnectionError: If client is not connected
        """
        if self._client is None:
            raise ElasticsearchConnectionError(
                "Elasticsearch client not initialized. Call connect() first."
            )
        return self._client

    async def health_check(self) -> bool:
        """
        Check Elasticsearch connection health.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if self._client is None:
                return False
            health = await self._client.cluster.health()
            return health.get("status") in ("green", "yellow")
        except Exception as e:
            logger.warning("elasticsearch_health_check_failed", error=str(e))
            return False

    async def create_index(
        self,
        index_name: str,
        mappings: dict[str, Any],
        settings_config: dict[str, Any] | None = None,
    ) -> bool:
        """
        Create an Elasticsearch index with mappings.

        Args:
            index_name: Name of the index to create
            mappings: Index mappings configuration
            settings_config: Optional index settings

        Returns:
            bool: True if created successfully
        """
        full_index_name = f"{settings.elasticsearch_index_prefix}_{index_name}"

        try:
            exists = await self.client.indices.exists(index=full_index_name)
            if exists:
                logger.info("elasticsearch_index_exists", index=full_index_name)
                return True

            body: dict[str, Any] = {"mappings": mappings}
            if settings_config:
                body["settings"] = settings_config

            await self.client.indices.create(index=full_index_name, body=body)
            logger.info("elasticsearch_index_created", index=full_index_name)
            return True

        except Exception as e:
            logger.error("elasticsearch_index_creation_failed", index=full_index_name, error=str(e))
            return False

    async def search(
        self,
        index_name: str,
        query: dict[str, Any],
        size: int = 10,
        from_: int = 0,
        sort: list[dict[str, Any]] | None = None,
        source: list[str] | bool = True,
        highlight: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a search query.

        Args:
            index_name: Index to search
            query: Elasticsearch query DSL
            size: Number of results to return
            from_: Offset for pagination
            sort: Sort configuration
            source: Fields to return or boolean
            highlight: Highlight configuration

        Returns:
            dict: Search results
        """
        full_index_name = f"{settings.elasticsearch_index_prefix}_{index_name}"

        body: dict[str, Any] = {
            "query": query,
            "size": size,
            "from": from_,
        }

        if sort:
            body["sort"] = sort
        if highlight:
            body["highlight"] = highlight

        result = await self.client.search(index=full_index_name, body=body, source=source)

        return result.body

    async def index_document(
        self,
        index_name: str,
        document: dict[str, Any],
        doc_id: str | None = None,
        refresh: bool = False,
    ) -> str:
        """
        Index a document.

        Args:
            index_name: Index to store document
            document: Document to index
            doc_id: Optional document ID
            refresh: Whether to refresh index after indexing

        Returns:
            str: Document ID
        """
        full_index_name = f"{settings.elasticsearch_index_prefix}_{index_name}"

        result = await self.client.index(
            index=full_index_name, id=doc_id, document=document, refresh=refresh
        )

        return result["_id"]

    async def get_document(self, index_name: str, doc_id: str) -> dict[str, Any] | None:
        """
        Get a document by ID.

        Args:
            index_name: Index containing document
            doc_id: Document ID

        Returns:
            dict or None: Document if found
        """
        full_index_name = f"{settings.elasticsearch_index_prefix}_{index_name}"

        try:
            result = await self.client.get(index=full_index_name, id=doc_id)
            return result["_source"]
        except Exception:
            return None

    async def delete_document(self, index_name: str, doc_id: str, refresh: bool = False) -> bool:
        """
        Delete a document by ID.

        Args:
            index_name: Index containing document
            doc_id: Document ID
            refresh: Whether to refresh index after deletion

        Returns:
            bool: True if deleted successfully
        """
        full_index_name = f"{settings.elasticsearch_index_prefix}_{index_name}"

        try:
            await self.client.delete(index=full_index_name, id=doc_id, refresh=refresh)
            return True
        except Exception:
            return False

    async def bulk_index(
        self, index_name: str, documents: list[dict[str, Any]], id_field: str = "id"
    ) -> dict[str, Any]:
        """
        Bulk index documents.

        Args:
            index_name: Index to store documents
            documents: List of documents to index
            id_field: Field to use as document ID

        Returns:
            dict: Bulk operation results
        """
        full_index_name = f"{settings.elasticsearch_index_prefix}_{index_name}"

        operations = []
        for doc in documents:
            doc_id = doc.get(id_field)
            operations.append({"index": {"_index": full_index_name, "_id": doc_id}})
            operations.append(doc)

        result = await self.client.bulk(operations=operations, refresh=True)
        return result.body

    async def initialize_indices(self) -> None:
        """
        Initialize all required Elasticsearch indices.

        Creates indices with appropriate mappings for RTCC-UIP data.
        """
        # Investigations index
        await self.create_index(
            "investigations",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "case_number": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "standard"},
                    "narrative": {"type": "text", "analyzer": "standard"},
                    "status": {"type": "keyword"},
                    "priority": {"type": "keyword"},
                    "assigned_to": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "tags": {"type": "keyword"},
                    "location": {"type": "geo_point"},
                }
            },
            settings_config={"number_of_shards": 1, "number_of_replicas": 0},
        )

        # Incidents index
        await self.create_index(
            "incidents",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "incident_number": {"type": "keyword"},
                    "incident_type": {"type": "keyword"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "occurred_at": {"type": "date"},
                    "reported_at": {"type": "date"},
                    "location": {"type": "geo_point"},
                    "address": {"type": "text"},
                    "status": {"type": "keyword"},
                    "severity": {"type": "keyword"},
                }
            },
        )

        # Persons index
        await self.create_index(
            "persons",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "first_name": {"type": "text"},
                    "last_name": {"type": "text"},
                    "full_name": {"type": "text", "analyzer": "standard"},
                    "aliases": {"type": "text"},
                    "date_of_birth": {"type": "date"},
                    "gender": {"type": "keyword"},
                    "race": {"type": "keyword"},
                    "height": {"type": "integer"},
                    "weight": {"type": "integer"},
                    "identifiers": {"type": "keyword"},
                }
            },
        )

        # Audit logs index
        await self.create_index(
            "audit_logs",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "user_id": {"type": "keyword"},
                    "username": {"type": "keyword"},
                    "action": {"type": "keyword"},
                    "resource_type": {"type": "keyword"},
                    "resource_id": {"type": "keyword"},
                    "ip_address": {"type": "ip"},
                    "user_agent": {"type": "text"},
                    "details": {"type": "object", "enabled": False},
                    "success": {"type": "boolean"},
                }
            },
        )

        logger.info("elasticsearch_indices_initialized")


# Global Elasticsearch manager instance
_elasticsearch_manager: ElasticsearchManager | None = None


async def get_elasticsearch() -> ElasticsearchManager:
    """
    Get the Elasticsearch manager instance.

    This function is designed to be used as a FastAPI dependency.

    Returns:
        ElasticsearchManager: The Elasticsearch manager instance
    """
    global _elasticsearch_manager
    if _elasticsearch_manager is None:
        _elasticsearch_manager = ElasticsearchManager()
        await _elasticsearch_manager.connect()
    return _elasticsearch_manager


async def close_elasticsearch() -> None:
    """Close the Elasticsearch connection."""
    global _elasticsearch_manager
    if _elasticsearch_manager is not None:
        await _elasticsearch_manager.close()
        _elasticsearch_manager = None
