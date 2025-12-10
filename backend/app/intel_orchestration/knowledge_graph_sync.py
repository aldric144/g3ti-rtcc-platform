"""
Knowledge Graph Sync for G3TI RTCC-UIP.

This module synchronizes intelligence output back to Neo4j knowledge graph
for relationship analysis and pattern discovery.
"""

import asyncio
import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SyncOperation(str, Enum):
    """Types of sync operations."""
    CREATE_NODE = "create_node"
    UPDATE_NODE = "update_node"
    DELETE_NODE = "delete_node"
    CREATE_RELATIONSHIP = "create_relationship"
    UPDATE_RELATIONSHIP = "update_relationship"
    DELETE_RELATIONSHIP = "delete_relationship"
    MERGE_NODE = "merge_node"
    MERGE_RELATIONSHIP = "merge_relationship"


class NodeType(str, Enum):
    """Types of nodes in the knowledge graph."""
    PERSON = "Person"
    VEHICLE = "Vehicle"
    WEAPON = "Weapon"
    INCIDENT = "Incident"
    LOCATION = "Location"
    ORGANIZATION = "Organization"
    CASE = "Case"
    INTELLIGENCE = "Intelligence"
    PATTERN = "Pattern"
    ALERT = "Alert"


class RelationshipType(str, Enum):
    """Types of relationships in the knowledge graph."""
    INVOLVED_IN = "INVOLVED_IN"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    LOCATED_AT = "LOCATED_AT"
    OWNS = "OWNS"
    RELATED_TO = "RELATED_TO"
    CORRELATED_WITH = "CORRELATED_WITH"
    PART_OF = "PART_OF"
    GENERATED_FROM = "GENERATED_FROM"
    TRIGGERED = "TRIGGERED"
    LINKED_TO = "LINKED_TO"


class GraphSyncConfig(BaseModel):
    """Configuration for knowledge graph sync."""
    enabled: bool = True
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    database: str = "neo4j"
    batch_size: int = 100
    batch_interval_seconds: float = 5.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    enable_relationship_inference: bool = True
    enable_pattern_detection: bool = True
    sync_timeout_seconds: float = 30.0


class GraphNode(BaseModel):
    """A node in the knowledge graph."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    node_type: NodeType
    properties: dict[str, Any] = Field(default_factory=dict)
    labels: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: str = "intel_orchestration"
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphRelationship(BaseModel):
    """A relationship in the knowledge graph."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    relationship_type: RelationshipType
    source_node_id: str
    target_node_id: str
    properties: dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class SyncResult(BaseModel):
    """Result of a sync operation."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    operation: SyncOperation
    success: bool
    node_id: str | None = None
    relationship_id: str | None = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SyncMetrics(BaseModel):
    """Metrics for sync operations."""
    nodes_created: int = 0
    nodes_updated: int = 0
    nodes_deleted: int = 0
    relationships_created: int = 0
    relationships_updated: int = 0
    relationships_deleted: int = 0
    sync_errors: int = 0
    last_sync_time: datetime | None = None
    avg_sync_time_ms: float = 0.0


class KnowledgeGraphSync:
    """
    Synchronizes intelligence output to Neo4j knowledge graph.

    Maintains entity relationships and enables graph-based analysis
    and pattern discovery.
    """

    def __init__(self, config: GraphSyncConfig | None = None):
        self.config = config or GraphSyncConfig()
        self.metrics = SyncMetrics()
        self._sync_queue: asyncio.Queue[tuple[SyncOperation, Any]] = asyncio.Queue()
        self._batch_buffer: list[tuple[SyncOperation, Any]] = []
        self._running = False
        self._worker_task: asyncio.Task | None = None
        self._driver = None  # Neo4j driver (lazy initialization)
        self._node_cache: dict[str, GraphNode] = {}
        self._relationship_cache: dict[str, GraphRelationship] = {}

        logger.info("KnowledgeGraphSync initialized")

    async def start(self):
        """Start the sync service."""
        if self._running:
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._sync_worker())

        logger.info("KnowledgeGraphSync started")

    async def stop(self):
        """Stop the sync service."""
        self._running = False

        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        # Flush remaining items
        await self._flush_batch()

        # Close driver
        if self._driver:
            await self._close_driver()

        logger.info("KnowledgeGraphSync stopped")

    async def sync_intelligence(self, intelligence: Any) -> list[SyncResult]:
        """
        Sync fused intelligence to knowledge graph.

        Creates/updates nodes and relationships based on intelligence content.
        """
        if not self.config.enabled:
            return []

        results = []

        # Create intelligence node
        intel_node = self._create_intelligence_node(intelligence)
        result = await self.create_node(intel_node)
        results.append(result)

        # Extract and sync entities
        entities = self._extract_entities(intelligence)
        for entity_node in entities:
            result = await self.merge_node(entity_node)
            results.append(result)

            # Create relationship to intelligence
            relationship = GraphRelationship(
                relationship_type=RelationshipType.GENERATED_FROM,
                source_node_id=entity_node.id,
                target_node_id=intel_node.id,
                confidence=intelligence.confidence if hasattr(intelligence, "confidence") else 1.0,
            )
            result = await self.create_relationship(relationship)
            results.append(result)

        # Sync correlations
        if hasattr(intelligence, "correlations"):
            for correlation in intelligence.correlations:
                rel_results = await self._sync_correlation(correlation, intel_node.id)
                results.extend(rel_results)

        # Infer additional relationships
        if self.config.enable_relationship_inference:
            inferred = await self._infer_relationships(entities)
            for relationship in inferred:
                result = await self.create_relationship(relationship)
                results.append(result)

        return results

    def _create_intelligence_node(self, intelligence: Any) -> GraphNode:
        """Create a graph node from intelligence."""
        intel_id = intelligence.id if hasattr(intelligence, "id") else str(uuid4())

        properties = {
            "intel_id": intel_id,
            "tier": intelligence.tier.value if hasattr(intelligence, "tier") and hasattr(intelligence.tier, "value") else "unknown",
            "priority_score": intelligence.priority_score if hasattr(intelligence, "priority_score") else 0,
            "title": intelligence.title if hasattr(intelligence, "title") else "",
            "summary": intelligence.summary if hasattr(intelligence, "summary") else "",
            "confidence": intelligence.confidence if hasattr(intelligence, "confidence") else 1.0,
            "jurisdiction": intelligence.jurisdiction if hasattr(intelligence, "jurisdiction") else "",
        }

        return GraphNode(
            id=intel_id,
            node_type=NodeType.INTELLIGENCE,
            properties=properties,
            labels=["Intelligence", "FusedIntel"],
        )

    def _extract_entities(self, intelligence: Any) -> list[GraphNode]:
        """Extract entity nodes from intelligence."""
        entities = []

        if not hasattr(intelligence, "entities"):
            return entities

        intel_entities = intelligence.entities
        if not isinstance(intel_entities, dict):
            return entities

        # Extract person entities
        if "person" in intel_entities:
            person_data = intel_entities["person"]
            if isinstance(person_data, dict):
                entities.append(GraphNode(
                    id=person_data.get("id", str(uuid4())),
                    node_type=NodeType.PERSON,
                    properties=person_data,
                    labels=["Person", "Entity"],
                ))

        # Extract vehicle entities
        if "vehicle" in intel_entities:
            vehicle_data = intel_entities["vehicle"]
            if isinstance(vehicle_data, dict):
                entities.append(GraphNode(
                    id=vehicle_data.get("id", str(uuid4())),
                    node_type=NodeType.VEHICLE,
                    properties=vehicle_data,
                    labels=["Vehicle", "Entity"],
                ))

        # Extract weapon entities
        if "weapon" in intel_entities:
            weapon_data = intel_entities["weapon"]
            if isinstance(weapon_data, dict):
                entities.append(GraphNode(
                    id=weapon_data.get("id", str(uuid4())),
                    node_type=NodeType.WEAPON,
                    properties=weapon_data,
                    labels=["Weapon", "Entity"],
                ))

        # Extract location entities
        if "location" in intel_entities:
            location_data = intel_entities["location"]
            if isinstance(location_data, dict):
                entities.append(GraphNode(
                    id=location_data.get("id", str(uuid4())),
                    node_type=NodeType.LOCATION,
                    properties=location_data,
                    labels=["Location", "Entity"],
                ))

        return entities

    async def _sync_correlation(
        self, correlation: dict[str, Any], intel_node_id: str
    ) -> list[SyncResult]:
        """Sync a correlation to the graph."""
        results = []

        entity1_id = correlation.get("entity1_id")
        entity2_id = correlation.get("entity2_id")

        if entity1_id and entity2_id:
            relationship = GraphRelationship(
                relationship_type=RelationshipType.CORRELATED_WITH,
                source_node_id=entity1_id,
                target_node_id=entity2_id,
                properties={
                    "correlation_type": correlation.get("correlation_type", "unknown"),
                    "score": correlation.get("score", 0),
                    "strength": correlation.get("strength", "unknown"),
                },
                confidence=correlation.get("score", 1.0),
            )
            result = await self.create_relationship(relationship)
            results.append(result)

        return results

    async def _infer_relationships(
        self, entities: list[GraphNode]
    ) -> list[GraphRelationship]:
        """Infer relationships between entities."""
        relationships = []

        # Find location relationships
        locations = [e for e in entities if e.node_type == NodeType.LOCATION]
        non_locations = [e for e in entities if e.node_type != NodeType.LOCATION]

        for entity in non_locations:
            for location in locations:
                relationships.append(GraphRelationship(
                    relationship_type=RelationshipType.LOCATED_AT,
                    source_node_id=entity.id,
                    target_node_id=location.id,
                    confidence=0.8,
                ))

        # Find person-vehicle relationships
        persons = [e for e in entities if e.node_type == NodeType.PERSON]
        vehicles = [e for e in entities if e.node_type == NodeType.VEHICLE]

        for person in persons:
            for vehicle in vehicles:
                relationships.append(GraphRelationship(
                    relationship_type=RelationshipType.ASSOCIATED_WITH,
                    source_node_id=person.id,
                    target_node_id=vehicle.id,
                    confidence=0.7,
                ))

        return relationships

    async def create_node(self, node: GraphNode) -> SyncResult:
        """Create a node in the graph."""
        await self._queue_operation(SyncOperation.CREATE_NODE, node)
        self._node_cache[node.id] = node
        self.metrics.nodes_created += 1

        return SyncResult(
            operation=SyncOperation.CREATE_NODE,
            success=True,
            node_id=node.id,
        )

    async def update_node(self, node: GraphNode) -> SyncResult:
        """Update a node in the graph."""
        node.updated_at = datetime.now(UTC)
        await self._queue_operation(SyncOperation.UPDATE_NODE, node)
        self._node_cache[node.id] = node
        self.metrics.nodes_updated += 1

        return SyncResult(
            operation=SyncOperation.UPDATE_NODE,
            success=True,
            node_id=node.id,
        )

    async def merge_node(self, node: GraphNode) -> SyncResult:
        """Merge (create or update) a node in the graph."""
        await self._queue_operation(SyncOperation.MERGE_NODE, node)
        self._node_cache[node.id] = node

        return SyncResult(
            operation=SyncOperation.MERGE_NODE,
            success=True,
            node_id=node.id,
        )

    async def delete_node(self, node_id: str) -> SyncResult:
        """Delete a node from the graph."""
        await self._queue_operation(SyncOperation.DELETE_NODE, {"id": node_id})
        self._node_cache.pop(node_id, None)
        self.metrics.nodes_deleted += 1

        return SyncResult(
            operation=SyncOperation.DELETE_NODE,
            success=True,
            node_id=node_id,
        )

    async def create_relationship(
        self, relationship: GraphRelationship
    ) -> SyncResult:
        """Create a relationship in the graph."""
        await self._queue_operation(SyncOperation.CREATE_RELATIONSHIP, relationship)
        self._relationship_cache[relationship.id] = relationship
        self.metrics.relationships_created += 1

        return SyncResult(
            operation=SyncOperation.CREATE_RELATIONSHIP,
            success=True,
            relationship_id=relationship.id,
        )

    async def update_relationship(
        self, relationship: GraphRelationship
    ) -> SyncResult:
        """Update a relationship in the graph."""
        await self._queue_operation(SyncOperation.UPDATE_RELATIONSHIP, relationship)
        self._relationship_cache[relationship.id] = relationship
        self.metrics.relationships_updated += 1

        return SyncResult(
            operation=SyncOperation.UPDATE_RELATIONSHIP,
            success=True,
            relationship_id=relationship.id,
        )

    async def delete_relationship(self, relationship_id: str) -> SyncResult:
        """Delete a relationship from the graph."""
        await self._queue_operation(
            SyncOperation.DELETE_RELATIONSHIP,
            {"id": relationship_id},
        )
        self._relationship_cache.pop(relationship_id, None)
        self.metrics.relationships_deleted += 1

        return SyncResult(
            operation=SyncOperation.DELETE_RELATIONSHIP,
            success=True,
            relationship_id=relationship_id,
        )

    async def _queue_operation(self, operation: SyncOperation, data: Any):
        """Queue an operation for batch processing."""
        self._batch_buffer.append((operation, data))

        if len(self._batch_buffer) >= self.config.batch_size:
            await self._flush_batch()

    async def _sync_worker(self):
        """Background worker for batch sync operations."""
        while self._running:
            try:
                await asyncio.sleep(self.config.batch_interval_seconds)
                await self._flush_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Sync worker error: %s", e)
                self.metrics.sync_errors += 1

    async def _flush_batch(self):
        """Flush batch buffer to Neo4j."""
        if not self._batch_buffer:
            return

        start_time = datetime.now(UTC)
        batch = self._batch_buffer.copy()
        self._batch_buffer.clear()

        try:
            # Execute batch operations
            for operation, data in batch:
                await self._execute_operation(operation, data)

            self.metrics.last_sync_time = datetime.now(UTC)
            elapsed_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.metrics.avg_sync_time_ms = (
                self.metrics.avg_sync_time_ms * 0.9 + elapsed_ms * 0.1
            )

        except Exception as e:
            logger.error("Batch flush error: %s", e)
            self.metrics.sync_errors += 1
            # Re-queue failed operations
            self._batch_buffer.extend(batch)

    async def _execute_operation(self, operation: SyncOperation, data: Any):
        """Execute a single sync operation."""
        # In production, this would execute Cypher queries against Neo4j
        # For now, we just log the operation
        logger.debug("Executing %s: %s", operation.value, data)

        # Simulate Neo4j operation
        if operation == SyncOperation.CREATE_NODE:
            cypher = self._build_create_node_cypher(data)
        elif operation == SyncOperation.UPDATE_NODE:
            cypher = self._build_update_node_cypher(data)
        elif operation == SyncOperation.MERGE_NODE:
            cypher = self._build_merge_node_cypher(data)
        elif operation == SyncOperation.DELETE_NODE:
            cypher = self._build_delete_node_cypher(data)
        elif operation == SyncOperation.CREATE_RELATIONSHIP:
            cypher = self._build_create_relationship_cypher(data)
        elif operation == SyncOperation.UPDATE_RELATIONSHIP:
            cypher = self._build_update_relationship_cypher(data)
        elif operation == SyncOperation.DELETE_RELATIONSHIP:
            cypher = self._build_delete_relationship_cypher(data)
        else:
            cypher = ""

        logger.debug("Generated Cypher: %s", cypher)

    def _build_create_node_cypher(self, node: GraphNode) -> str:
        """Build Cypher query for creating a node."""
        labels = ":".join([node.node_type.value] + node.labels)
        props = self._format_properties(node.properties)
        return f"CREATE (n:{labels} {props}) RETURN n"

    def _build_update_node_cypher(self, node: GraphNode) -> str:
        """Build Cypher query for updating a node."""
        props = self._format_properties(node.properties)
        return f"MATCH (n) WHERE n.id = '{node.id}' SET n += {props} RETURN n"

    def _build_merge_node_cypher(self, node: GraphNode) -> str:
        """Build Cypher query for merging a node."""
        labels = ":".join([node.node_type.value] + node.labels)
        props = self._format_properties(node.properties)
        return f"MERGE (n:{labels} {{id: '{node.id}'}}) SET n += {props} RETURN n"

    def _build_delete_node_cypher(self, data: dict) -> str:
        """Build Cypher query for deleting a node."""
        return f"MATCH (n) WHERE n.id = '{data['id']}' DETACH DELETE n"

    def _build_create_relationship_cypher(
        self, relationship: GraphRelationship
    ) -> str:
        """Build Cypher query for creating a relationship."""
        rel_type = relationship.relationship_type.value
        props = self._format_properties(relationship.properties)
        return (
            f"MATCH (a), (b) WHERE a.id = '{relationship.source_node_id}' "
            f"AND b.id = '{relationship.target_node_id}' "
            f"CREATE (a)-[r:{rel_type} {props}]->(b) RETURN r"
        )

    def _build_update_relationship_cypher(
        self, relationship: GraphRelationship
    ) -> str:
        """Build Cypher query for updating a relationship."""
        props = self._format_properties(relationship.properties)
        return (
            f"MATCH ()-[r]->() WHERE r.id = '{relationship.id}' "
            f"SET r += {props} RETURN r"
        )

    def _build_delete_relationship_cypher(self, data: dict) -> str:
        """Build Cypher query for deleting a relationship."""
        return f"MATCH ()-[r]->() WHERE r.id = '{data['id']}' DELETE r"

    def _format_properties(self, properties: dict[str, Any]) -> str:
        """Format properties for Cypher query."""
        import json

        formatted = {}
        for key, value in properties.items():
            if isinstance(value, datetime):
                formatted[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                formatted[key] = json.dumps(value)
            else:
                formatted[key] = value

        return json.dumps(formatted)

    async def _close_driver(self):
        """Close Neo4j driver."""
        if self._driver:
            # In production: await self._driver.close()
            self._driver = None

    def get_node(self, node_id: str) -> GraphNode | None:
        """Get a node from cache."""
        return self._node_cache.get(node_id)

    def get_relationship(self, relationship_id: str) -> GraphRelationship | None:
        """Get a relationship from cache."""
        return self._relationship_cache.get(relationship_id)

    def get_metrics(self) -> SyncMetrics:
        """Get sync metrics."""
        return self.metrics

    def get_status(self) -> dict[str, Any]:
        """Get sync service status."""
        return {
            "running": self._running,
            "batch_buffer_size": len(self._batch_buffer),
            "nodes_cached": len(self._node_cache),
            "relationships_cached": len(self._relationship_cache),
            "metrics": self.metrics.model_dump(),
            "config": {
                "enabled": self.config.enabled,
                "batch_size": self.config.batch_size,
                "batch_interval_seconds": self.config.batch_interval_seconds,
            },
        }
