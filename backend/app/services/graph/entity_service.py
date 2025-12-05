"""
Entity graph service for the G3TI RTCC-UIP Backend.

This service provides Neo4j graph operations for managing entities
and their relationships in the RTCC intelligence graph.

Supported entity types:
- Person
- Vehicle
- Incident
- Weapon
- ShellCasing
- Address
- Camera
- LicensePlate

Relationship types:
- SUSPECT_IN, VICTIM_IN, WITNESS_IN (Person -> Incident)
- OWNS, DRIVES (Person -> Vehicle)
- RESIDES_AT, WORKS_AT (Person -> Address)
- OCCURRED_AT (Incident -> Address)
- ASSOCIATED_WITH (Person -> Person)
- LINKED_TO (ShellCasing -> ShellCasing)
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import EntityNotFoundError, ValidationError
from app.core.logging import audit_logger, get_logger
from app.db.neo4j import Neo4jManager, get_neo4j

logger = get_logger(__name__)


class EntityGraphService:
    """
    Service for entity graph operations in Neo4j.

    Provides methods for creating, querying, and managing entities
    and their relationships in the graph database.
    """

    # Valid entity labels
    ENTITY_LABELS = {
        "Person",
        "Vehicle",
        "Incident",
        "Weapon",
        "ShellCasing",
        "Address",
        "Camera",
        "LicensePlate",
    }

    # Valid relationship types
    RELATIONSHIP_TYPES = {
        "SUSPECT_IN",
        "VICTIM_IN",
        "WITNESS_IN",
        "OWNS",
        "DRIVES",
        "PASSENGER_IN",
        "RESIDES_AT",
        "WORKS_AT",
        "VISITED",
        "OCCURRED_AT",
        "REPORTED_AT",
        "ASSOCIATED_WITH",
        "FAMILY_OF",
        "KNOWN_ASSOCIATE",
        "LINKED_TO",
        "MATCHED_WITH",
        "CAPTURED_BY",
        "SEEN_AT",
        "USED_IN",
        "RECOVERED_AT",
    }

    def __init__(self, neo4j_manager: Neo4jManager | None = None) -> None:
        """
        Initialize the entity graph service.

        Args:
            neo4j_manager: Neo4j manager instance (optional)
        """
        self._neo4j = neo4j_manager

    async def _get_neo4j(self) -> Neo4jManager:
        """Get Neo4j manager, initializing if needed."""
        if self._neo4j is None:
            self._neo4j = await get_neo4j()
        return self._neo4j

    async def create_node(
        self, label: str, properties: dict[str, Any], user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Create a new node in the graph.

        Args:
            label: Node label (entity type)
            properties: Node properties
            user_id: ID of user creating the node

        Returns:
            dict: Created node with ID

        Raises:
            ValidationError: If label is invalid
        """
        if label not in self.ENTITY_LABELS:
            raise ValidationError(
                f"Invalid entity label: {label}",
                field="label",
                details={"valid_labels": list(self.ENTITY_LABELS)},
            )

        # Generate ID if not provided
        if "id" not in properties:
            properties["id"] = str(uuid.uuid4())

        # Add timestamps
        now = datetime.now(UTC).isoformat()
        properties["created_at"] = now
        properties["updated_at"] = now
        if user_id:
            properties["created_by"] = user_id

        neo4j = await self._get_neo4j()

        # Build Cypher query
        query = f"""
        CREATE (n:{label} $properties)
        RETURN n, id(n) as node_id
        """

        try:
            result = await neo4j.execute_query(query, {"properties": properties})

            if result:
                node_data = dict(result[0]["n"])
                node_data["_neo4j_id"] = result[0]["node_id"]

                # Audit log
                if user_id:
                    audit_logger.log_data_access(
                        user_id=user_id,
                        entity_type=label,
                        entity_id=properties["id"],
                        action="create",
                    )

                logger.info("node_created", label=label, entity_id=properties["id"])

                return node_data

            return properties

        except Exception as e:
            logger.error("create_node_error", label=label, error=str(e))
            raise

    async def get_node(
        self, label: str, entity_id: str, user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get a node by ID.

        Args:
            label: Node label
            entity_id: Entity ID
            user_id: ID of user accessing the node

        Returns:
            dict: Node properties

        Raises:
            EntityNotFoundError: If node not found
        """
        neo4j = await self._get_neo4j()

        query = f"""
        MATCH (n:{label} {{id: $entity_id}})
        RETURN n
        """

        result = await neo4j.execute_query(query, {"entity_id": entity_id})

        if not result:
            raise EntityNotFoundError(label, entity_id)

        node_data = dict(result[0]["n"])

        # Audit log
        if user_id:
            audit_logger.log_data_access(
                user_id=user_id, entity_type=label, entity_id=entity_id, action="read"
            )

        return node_data

    async def update_node(
        self, label: str, entity_id: str, properties: dict[str, Any], user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Update a node's properties.

        Args:
            label: Node label
            entity_id: Entity ID
            properties: Properties to update
            user_id: ID of user updating the node

        Returns:
            dict: Updated node properties

        Raises:
            EntityNotFoundError: If node not found
        """
        # Don't allow updating ID or created_at
        properties.pop("id", None)
        properties.pop("created_at", None)
        properties.pop("created_by", None)

        # Update timestamp
        properties["updated_at"] = datetime.now(UTC).isoformat()
        if user_id:
            properties["updated_by"] = user_id

        neo4j = await self._get_neo4j()

        # Build SET clause
        set_clauses = [f"n.{key} = ${key}" for key in properties.keys()]
        set_clause = ", ".join(set_clauses)

        query = f"""
        MATCH (n:{label} {{id: $entity_id}})
        SET {set_clause}
        RETURN n
        """

        params = {"entity_id": entity_id, **properties}
        result = await neo4j.execute_query(query, params)

        if not result:
            raise EntityNotFoundError(label, entity_id)

        node_data = dict(result[0]["n"])

        # Audit log
        if user_id:
            audit_logger.log_data_access(
                user_id=user_id,
                entity_type=label,
                entity_id=entity_id,
                action="update",
                fields_accessed=list(properties.keys()),
            )

        logger.info(
            "node_updated", label=label, entity_id=entity_id, updated_fields=list(properties.keys())
        )

        return node_data

    async def delete_node(self, label: str, entity_id: str, user_id: str | None = None) -> bool:
        """
        Delete a node and its relationships.

        Args:
            label: Node label
            entity_id: Entity ID
            user_id: ID of user deleting the node

        Returns:
            bool: True if deleted

        Raises:
            EntityNotFoundError: If node not found
        """
        neo4j = await self._get_neo4j()

        # First check if node exists
        check_query = f"""
        MATCH (n:{label} {{id: $entity_id}})
        RETURN count(n) as count
        """

        result = await neo4j.execute_query(check_query, {"entity_id": entity_id})

        if not result or result[0]["count"] == 0:
            raise EntityNotFoundError(label, entity_id)

        # Delete node and relationships
        delete_query = f"""
        MATCH (n:{label} {{id: $entity_id}})
        DETACH DELETE n
        """

        await neo4j.execute_query(delete_query, {"entity_id": entity_id})

        # Audit log
        if user_id:
            audit_logger.log_data_access(
                user_id=user_id, entity_type=label, entity_id=entity_id, action="delete"
            )

        logger.info("node_deleted", label=label, entity_id=entity_id)

        return True

    async def link_nodes(
        self,
        source_label: str,
        source_id: str,
        target_label: str,
        target_id: str,
        relationship_type: str,
        properties: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a relationship between two nodes.

        Args:
            source_label: Source node label
            source_id: Source entity ID
            target_label: Target node label
            target_id: Target entity ID
            relationship_type: Type of relationship
            properties: Relationship properties
            user_id: ID of user creating the relationship

        Returns:
            dict: Relationship details

        Raises:
            ValidationError: If relationship type is invalid
            EntityNotFoundError: If either node not found
        """
        if relationship_type not in self.RELATIONSHIP_TYPES:
            raise ValidationError(
                f"Invalid relationship type: {relationship_type}",
                field="relationship_type",
                details={"valid_types": list(self.RELATIONSHIP_TYPES)},
            )

        properties = properties or {}
        properties["id"] = str(uuid.uuid4())
        properties["created_at"] = datetime.now(UTC).isoformat()
        if user_id:
            properties["created_by"] = user_id

        neo4j = await self._get_neo4j()

        query = f"""
        MATCH (source:{source_label} {{id: $source_id}})
        MATCH (target:{target_label} {{id: $target_id}})
        CREATE (source)-[r:{relationship_type} $properties]->(target)
        RETURN source, target, r, type(r) as rel_type
        """

        params = {"source_id": source_id, "target_id": target_id, "properties": properties}

        result = await neo4j.execute_query(query, params)

        if not result:
            # Check which node is missing
            check_source = await neo4j.execute_query(
                f"MATCH (n:{source_label} {{id: $id}}) RETURN n", {"id": source_id}
            )
            if not check_source:
                raise EntityNotFoundError(source_label, source_id)
            raise EntityNotFoundError(target_label, target_id)

        rel_data = {
            "id": properties["id"],
            "type": relationship_type,
            "source_id": source_id,
            "source_label": source_label,
            "target_id": target_id,
            "target_label": target_label,
            "properties": dict(result[0]["r"]),
        }

        logger.info(
            "relationship_created",
            relationship_type=relationship_type,
            source=f"{source_label}:{source_id}",
            target=f"{target_label}:{target_id}",
        )

        return rel_data

    async def unlink_nodes(
        self,
        source_label: str,
        source_id: str,
        target_label: str,
        target_id: str,
        relationship_type: str | None = None,
        user_id: str | None = None,
    ) -> int:
        """
        Remove relationship(s) between two nodes.

        Args:
            source_label: Source node label
            source_id: Source entity ID
            target_label: Target node label
            target_id: Target entity ID
            relationship_type: Specific relationship type (optional)
            user_id: ID of user removing the relationship

        Returns:
            int: Number of relationships removed
        """
        neo4j = await self._get_neo4j()

        if relationship_type:
            query = f"""
            MATCH (source:{source_label} {{id: $source_id}})
                  -[r:{relationship_type}]->
                  (target:{target_label} {{id: $target_id}})
            DELETE r
            RETURN count(r) as deleted_count
            """
        else:
            query = f"""
            MATCH (source:{source_label} {{id: $source_id}})
                  -[r]->
                  (target:{target_label} {{id: $target_id}})
            DELETE r
            RETURN count(r) as deleted_count
            """

        params = {"source_id": source_id, "target_id": target_id}
        result = await neo4j.execute_query(query, params)

        deleted_count = result[0]["deleted_count"] if result else 0

        logger.info(
            "relationships_deleted",
            count=deleted_count,
            source=f"{source_label}:{source_id}",
            target=f"{target_label}:{target_id}",
        )

        return deleted_count

    async def search_by_property(
        self, label: str, property_name: str, property_value: Any, limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Search nodes by property value.

        Args:
            label: Node label to search
            property_name: Property to match
            property_value: Value to match
            limit: Maximum results

        Returns:
            list: Matching nodes
        """
        neo4j = await self._get_neo4j()

        query = f"""
        MATCH (n:{label})
        WHERE n.{property_name} = $value
        RETURN n
        LIMIT $limit
        """

        result = await neo4j.execute_query(query, {"value": property_value, "limit": limit})

        return [dict(r["n"]) for r in result]

    async def find_relationships(
        self,
        entity_label: str,
        entity_id: str,
        relationship_type: str | None = None,
        direction: str = "both",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Find relationships for an entity.

        Args:
            entity_label: Entity label
            entity_id: Entity ID
            relationship_type: Filter by relationship type
            direction: "outgoing", "incoming", or "both"
            limit: Maximum results

        Returns:
            list: Related entities with relationship info
        """
        neo4j = await self._get_neo4j()

        rel_pattern = f":{relationship_type}" if relationship_type else ""

        if direction == "outgoing":
            query = f"""
            MATCH (n:{entity_label} {{id: $entity_id}})-[r{rel_pattern}]->(related)
            RETURN n, r, related, type(r) as rel_type, labels(related) as related_labels
            LIMIT $limit
            """
        elif direction == "incoming":
            query = f"""
            MATCH (n:{entity_label} {{id: $entity_id}})<-[r{rel_pattern}]-(related)
            RETURN n, r, related, type(r) as rel_type, labels(related) as related_labels
            LIMIT $limit
            """
        else:
            query = f"""
            MATCH (n:{entity_label} {{id: $entity_id}})-[r{rel_pattern}]-(related)
            RETURN n, r, related, type(r) as rel_type, labels(related) as related_labels
            LIMIT $limit
            """

        result = await neo4j.execute_query(query, {"entity_id": entity_id, "limit": limit})

        relationships = []
        for record in result:
            relationships.append(
                {
                    "relationship_type": record["rel_type"],
                    "relationship_properties": dict(record["r"]),
                    "related_entity": dict(record["related"]),
                    "related_labels": record["related_labels"],
                }
            )

        return relationships

    async def get_entity_network(
        self, entity_label: str, entity_id: str, depth: int = 2, limit: int = 100
    ) -> dict[str, Any]:
        """
        Get the network of entities connected to a given entity.

        Args:
            entity_label: Starting entity label
            entity_id: Starting entity ID
            depth: Maximum relationship depth
            limit: Maximum nodes to return

        Returns:
            dict: Network with nodes and edges
        """
        neo4j = await self._get_neo4j()

        query = f"""
        MATCH path = (start:{entity_label} {{id: $entity_id}})-[*1..{depth}]-(connected)
        WITH start, connected, relationships(path) as rels
        UNWIND rels as r
        WITH start, connected, r, startNode(r) as source, endNode(r) as target
        RETURN DISTINCT
            start,
            connected,
            type(r) as rel_type,
            properties(r) as rel_props,
            source.id as source_id,
            target.id as target_id,
            labels(connected) as connected_labels
        LIMIT $limit
        """

        result = await neo4j.execute_query(query, {"entity_id": entity_id, "limit": limit})

        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, Any]] = []

        for record in result:
            # Add start node
            start_data = dict(record["start"])
            if start_data.get("id") not in nodes:
                nodes[start_data["id"]] = {
                    "id": start_data["id"],
                    "label": entity_label,
                    "properties": start_data,
                }

            # Add connected node
            connected_data = dict(record["connected"])
            connected_id = connected_data.get("id")
            if connected_id and connected_id not in nodes:
                nodes[connected_id] = {
                    "id": connected_id,
                    "label": (
                        record["connected_labels"][0] if record["connected_labels"] else "Unknown"
                    ),
                    "properties": connected_data,
                }

            # Add edge
            edges.append(
                {
                    "source": record["source_id"],
                    "target": record["target_id"],
                    "type": record["rel_type"],
                    "properties": record["rel_props"],
                }
            )

        return {"nodes": list(nodes.values()), "edges": edges, "center_node_id": entity_id}


# Global entity graph service instance
_entity_graph_service: EntityGraphService | None = None


async def get_entity_graph_service() -> EntityGraphService:
    """Get the entity graph service instance."""
    global _entity_graph_service
    if _entity_graph_service is None:
        _entity_graph_service = EntityGraphService()
    return _entity_graph_service
