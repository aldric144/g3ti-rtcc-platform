"""
Entity Correlation Engine.

This module provides functionality for expanding and correlating entities
across multiple data sources to build comprehensive investigative profiles.
"""

from typing import Any

from app.core.logging import get_logger
from app.investigations_engine.models import EntitySummary

logger = get_logger(__name__)


class EntityCorrelator:
    """
    Engine for correlating entities across data sources.

    Expands entity relationships through:
    - Persons -> Associates -> Vehicles -> Locations
    - Past gunfire incidents -> Warrants
    - CAD/RMS connections
    - LPR activity trails
    - BWC interactions
    """

    def __init__(
        self,
        neo4j_manager: Any = None,
        es_client: Any = None,
    ) -> None:
        """Initialize the Entity Correlator."""
        self._neo4j_manager = neo4j_manager
        self._es_client = es_client

    async def get_profile(self, entity_id: str) -> EntitySummary:
        """
        Get comprehensive entity profile with all correlations.

        Args:
            entity_id: ID of the entity to profile

        Returns:
            EntitySummary with complete investigative profile
        """
        logger.info(f"Building profile for entity: {entity_id}")

        entity_data = await self._fetch_entity(entity_id)
        entity_type = entity_data.get("entity_type") or entity_data.get("type") or "unknown"
        name = self._extract_name(entity_data)

        prior_incidents = await self._get_prior_incidents(entity_id)
        address_history = await self._get_address_history(entity_id)
        vehicle_connections = await self._get_vehicle_connections(entity_id)
        weapon_matches = await self._get_weapon_matches(entity_id)
        lpr_activity = await self._get_lpr_activity(entity_id)
        bwc_interactions = await self._get_bwc_interactions(entity_id)
        known_associates = await self._get_known_associates(entity_id)
        risk_score = await self._calculate_risk_score(entity_id, entity_data)

        return EntitySummary(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            prior_incidents=prior_incidents,
            address_history=address_history,
            vehicle_connections=vehicle_connections,
            weapon_matches=weapon_matches,
            lpr_activity=lpr_activity,
            bwc_interactions=bwc_interactions,
            known_associates=known_associates,
            risk_score=risk_score,
            metadata=entity_data,
        )

    async def expand_graph(
        self,
        entity_id: str,
        depth: int = 2,
        max_nodes: int = 50,
    ) -> dict[str, Any]:
        """
        Expand entity graph to find related entities.

        Args:
            entity_id: Starting entity ID
            depth: How many relationship hops to traverse
            max_nodes: Maximum number of nodes to return

        Returns:
            Graph data with nodes and edges
        """
        logger.info(f"Expanding graph for entity {entity_id} with depth {depth}")

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH path = (start)-[*1..$depth]-(related)
                WHERE start.entity_id = $entity_id OR start.id = $entity_id
                WITH start, related, relationships(path) as rels
                LIMIT $max_nodes
                RETURN start, related, rels
                """
                result = await self._neo4j_manager.execute_query(
                    query,
                    {"entity_id": entity_id, "depth": depth, "max_nodes": max_nodes},
                )

                seen_nodes: set[str] = set()
                for record in result:
                    start_node = dict(record["start"])
                    start_id = start_node.get("entity_id") or start_node.get("id")
                    if start_id not in seen_nodes:
                        nodes.append(
                            {
                                "id": start_id,
                                "type": start_node.get("entity_type") or "unknown",
                                "label": self._extract_name(start_node),
                                "data": start_node,
                            }
                        )
                        seen_nodes.add(start_id)

                    related_node = dict(record["related"])
                    related_id = related_node.get("entity_id") or related_node.get("id")
                    if related_id not in seen_nodes:
                        nodes.append(
                            {
                                "id": related_id,
                                "type": related_node.get("entity_type") or "unknown",
                                "label": self._extract_name(related_node),
                                "data": related_node,
                            }
                        )
                        seen_nodes.add(related_id)

                    for rel in record["rels"]:
                        edges.append(
                            {
                                "source": start_id,
                                "target": related_id,
                                "type": type(rel).__name__,
                            }
                        )

            except Exception as e:
                logger.warning(f"Error expanding graph: {e}")

        if not nodes:
            nodes.append(
                {
                    "id": entity_id,
                    "type": "unknown",
                    "label": f"Entity {entity_id}",
                    "data": {},
                }
            )

        return {
            "nodes": nodes,
            "edges": edges,
            "center_entity_id": entity_id,
        }

    async def _fetch_entity(self, entity_id: str) -> dict[str, Any]:
        """Fetch entity data from Neo4j."""
        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)
                WHERE e.entity_id = $entity_id OR e.id = $entity_id
                RETURN e, labels(e) as labels
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_id": entity_id})
                if result:
                    entity = dict(result[0]["e"])
                    entity["entity_type"] = (
                        result[0]["labels"][0] if result[0]["labels"] else "unknown"
                    )
                    return entity
            except Exception as e:
                logger.warning(f"Error fetching entity: {e}")

        return {"entity_id": entity_id, "entity_type": "unknown"}

    async def _get_prior_incidents(self, entity_id: str) -> list[dict[str, Any]]:
        """Get prior incidents involving the entity."""
        incidents = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:INVOLVES|SUSPECT_IN|VICTIM_IN|WITNESS_IN]-(i:Incident)
                WHERE e.entity_id = $entity_id OR e.id = $entity_id
                RETURN i
                ORDER BY i.timestamp DESC
                LIMIT 20
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_id": entity_id})
                for record in result:
                    incident = dict(record["i"])
                    incidents.append(
                        {
                            "incident_id": incident.get("incident_id") or incident.get("id"),
                            "incident_type": incident.get("incident_type") or incident.get("type"),
                            "timestamp": incident.get("timestamp"),
                            "location": incident.get("location"),
                            "summary": incident.get("summary")
                            or incident.get("narrative", "")[:200],
                            "role": "involved",
                        }
                    )
            except Exception as e:
                logger.warning(f"Error getting prior incidents: {e}")

        return incidents

    async def _get_address_history(self, entity_id: str) -> list[dict[str, Any]]:
        """Get address history for the entity."""
        addresses = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[r:RESIDES_AT|LOCATED_AT|ASSOCIATED_WITH]-(a:Address)
                WHERE e.entity_id = $entity_id OR e.id = $entity_id
                RETURN a, r.start_date as start_date, r.end_date as end_date
                ORDER BY r.start_date DESC
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_id": entity_id})
                for record in result:
                    address = dict(record["a"])
                    addresses.append(
                        {
                            "address_id": address.get("address_id") or address.get("id"),
                            "street": address.get("street") or address.get("address"),
                            "city": address.get("city"),
                            "state": address.get("state"),
                            "zip": address.get("zip_code") or address.get("zip"),
                            "start_date": record.get("start_date"),
                            "end_date": record.get("end_date"),
                            "latitude": address.get("latitude"),
                            "longitude": address.get("longitude"),
                        }
                    )
            except Exception as e:
                logger.warning(f"Error getting address history: {e}")

        return addresses

    async def _get_vehicle_connections(self, entity_id: str) -> list[dict[str, Any]]:
        """Get vehicles connected to the entity."""
        vehicles = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[r:OWNS|DRIVES|ASSOCIATED_WITH]-(v:Vehicle)
                WHERE e.entity_id = $entity_id OR e.id = $entity_id
                RETURN v, type(r) as relationship_type
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_id": entity_id})
                for record in result:
                    vehicle = dict(record["v"])
                    vehicles.append(
                        {
                            "vehicle_id": vehicle.get("vehicle_id") or vehicle.get("id"),
                            "plate_number": vehicle.get("plate_number")
                            or vehicle.get("license_plate"),
                            "make": vehicle.get("make"),
                            "model": vehicle.get("model"),
                            "year": vehicle.get("year"),
                            "color": vehicle.get("color"),
                            "vin": vehicle.get("vin"),
                            "relationship": record.get("relationship_type"),
                        }
                    )
            except Exception as e:
                logger.warning(f"Error getting vehicle connections: {e}")

        return vehicles

    async def _get_weapon_matches(self, entity_id: str) -> list[dict[str, Any]]:
        """Get weapon/ballistic matches for the entity."""
        weapons = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:OWNS|USED|ASSOCIATED_WITH]-(w:Weapon)
                WHERE e.entity_id = $entity_id OR e.id = $entity_id
                OPTIONAL MATCH (w)-[:HAS_BALLISTIC]-(b:BallisticEvidence)
                RETURN w, collect(b) as ballistics
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_id": entity_id})
                for record in result:
                    weapon = dict(record["w"])
                    ballistics = [dict(b) for b in record["ballistics"] if b]
                    weapons.append(
                        {
                            "weapon_id": weapon.get("weapon_id") or weapon.get("id"),
                            "weapon_type": weapon.get("weapon_type") or weapon.get("type"),
                            "caliber": weapon.get("caliber"),
                            "make": weapon.get("make"),
                            "model": weapon.get("model"),
                            "serial_number": weapon.get("serial_number"),
                            "ballistic_matches": len(ballistics),
                            "ballistics": ballistics[:5],
                        }
                    )
            except Exception as e:
                logger.warning(f"Error getting weapon matches: {e}")

        return weapons

    async def _get_lpr_activity(self, entity_id: str) -> list[dict[str, Any]]:
        """Get LPR activity trail for the entity."""
        lpr_hits = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:OWNS|DRIVES]-(v:Vehicle)-[:DETECTED_BY]-(lpr:LPRHit)
                WHERE e.entity_id = $entity_id OR e.id = $entity_id
                RETURN lpr, v.plate_number as plate
                ORDER BY lpr.timestamp DESC
                LIMIT 50
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_id": entity_id})
                for record in result:
                    hit = dict(record["lpr"])
                    lpr_hits.append(
                        {
                            "hit_id": hit.get("hit_id") or hit.get("id"),
                            "plate_number": record.get("plate"),
                            "timestamp": hit.get("timestamp"),
                            "location": hit.get("location"),
                            "latitude": hit.get("latitude"),
                            "longitude": hit.get("longitude"),
                            "camera_id": hit.get("camera_id"),
                            "alert_type": hit.get("alert_type"),
                        }
                    )
            except Exception as e:
                logger.warning(f"Error getting LPR activity: {e}")

        return lpr_hits

    async def _get_bwc_interactions(self, entity_id: str) -> list[dict[str, Any]]:
        """Get body-worn camera interactions for the entity."""
        interactions = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:APPEARS_IN|INTERACTS_WITH]-(bwc:BWCRecording)
                WHERE e.entity_id = $entity_id OR e.id = $entity_id
                RETURN bwc
                ORDER BY bwc.timestamp DESC
                LIMIT 20
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_id": entity_id})
                for record in result:
                    bwc = dict(record["bwc"])
                    interactions.append(
                        {
                            "recording_id": bwc.get("recording_id") or bwc.get("id"),
                            "timestamp": bwc.get("timestamp"),
                            "duration": bwc.get("duration"),
                            "officer_id": bwc.get("officer_id"),
                            "incident_id": bwc.get("incident_id"),
                            "location": bwc.get("location"),
                            "tags": bwc.get("tags", []),
                        }
                    )
            except Exception as e:
                logger.warning(f"Error getting BWC interactions: {e}")

        return interactions

    async def _get_known_associates(self, entity_id: str) -> list[dict[str, Any]]:
        """Get known associates for the entity."""
        associates = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[r:ASSOCIATED_WITH|RELATED_TO|KNOWN_ASSOCIATE]-(a:Person)
                WHERE (e.entity_id = $entity_id OR e.id = $entity_id)
                  AND (a.entity_id <> $entity_id AND a.id <> $entity_id)
                OPTIONAL MATCH (a)-[:SUSPECT_IN]-(i:Incident)
                WITH a, type(r) as relationship, count(DISTINCT i) as incident_count
                RETURN a, relationship, incident_count
                ORDER BY incident_count DESC
                LIMIT 20
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_id": entity_id})
                for record in result:
                    associate = dict(record["a"])
                    associates.append(
                        {
                            "entity_id": associate.get("entity_id") or associate.get("id"),
                            "name": self._extract_name(associate),
                            "relationship": record.get("relationship"),
                            "incident_count": record.get("incident_count", 0),
                            "dob": associate.get("dob") or associate.get("date_of_birth"),
                            "last_known_address": associate.get("address"),
                        }
                    )
            except Exception as e:
                logger.warning(f"Error getting known associates: {e}")

        return associates

    async def _calculate_risk_score(self, entity_id: str, entity_data: dict[str, Any]) -> float:
        """Calculate risk score for the entity."""
        risk_score = 0.0
        factors = []

        if entity_data.get("risk_score"):
            return float(entity_data["risk_score"])

        prior_incidents = await self._get_prior_incidents(entity_id)
        incident_count = len(prior_incidents)
        if incident_count > 0:
            risk_score += min(0.3, incident_count * 0.05)
            factors.append(f"Prior incidents: {incident_count}")

        weapon_matches = await self._get_weapon_matches(entity_id)
        if weapon_matches:
            risk_score += 0.2
            factors.append(f"Weapon associations: {len(weapon_matches)}")

        associates = await self._get_known_associates(entity_id)
        high_risk_associates = [a for a in associates if a.get("incident_count", 0) > 3]
        if high_risk_associates:
            risk_score += min(0.2, len(high_risk_associates) * 0.05)
            factors.append(f"High-risk associates: {len(high_risk_associates)}")

        if entity_data.get("has_warrant") or entity_data.get("warrant_status"):
            risk_score += 0.3
            factors.append("Active warrant")

        logger.debug(f"Risk score for {entity_id}: {risk_score} (factors: {factors})")

        return min(1.0, risk_score)

    def _extract_name(self, entity_data: dict[str, Any]) -> str:
        """Extract display name from entity data."""
        if entity_data.get("name"):
            return entity_data["name"]

        if entity_data.get("first_name") or entity_data.get("last_name"):
            first = entity_data.get("first_name", "")
            last = entity_data.get("last_name", "")
            return f"{first} {last}".strip()

        if entity_data.get("plate_number"):
            return entity_data["plate_number"]

        if entity_data.get("street") or entity_data.get("address"):
            return entity_data.get("street") or entity_data.get("address")

        return entity_data.get("entity_id") or entity_data.get("id") or "Unknown"


__all__ = [
    "EntityCorrelator",
]
