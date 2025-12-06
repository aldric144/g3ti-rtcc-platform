"""
Incident Linking Engine.

This module provides functionality for linking incidents based on various
correlation factors including time, location, M.O., suspect description,
vehicle description, weapon type, ballistic match, repeat callers, and
shared entities.
"""

import math
from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.investigations_engine.models import (
    IncidentLinkage,
    LinkageResult,
    LinkageType,
)

logger = get_logger(__name__)


class IncidentLinker:
    """
    Engine for linking related incidents.

    Uses multiple correlation factors to identify relationships between
    incidents including temporal, geographic, entity overlap, narrative
    similarity, ballistic correlation, and vehicle recurrence.
    """

    TEMPORAL_WINDOW_HOURS = 72
    GEOGRAPHIC_RADIUS_KM = 2.0
    MIN_CONFIDENCE_THRESHOLD = 0.3

    LINKAGE_WEIGHTS = {
        LinkageType.BALLISTIC_MATCH: 0.95,
        LinkageType.ENTITY_OVERLAP: 0.85,
        LinkageType.VEHICLE_RECURRENCE: 0.80,
        LinkageType.MO_SIMILARITY: 0.75,
        LinkageType.SUSPECT_DESCRIPTION: 0.70,
        LinkageType.WEAPON_TYPE: 0.65,
        LinkageType.GEOGRAPHIC: 0.60,
        LinkageType.TEMPORAL: 0.50,
        LinkageType.NARRATIVE_SIMILARITY: 0.55,
        LinkageType.REPEAT_CALLER: 0.45,
    }

    def __init__(
        self,
        neo4j_manager: Any = None,
        es_client: Any = None,
    ) -> None:
        """Initialize the Incident Linker."""
        self._neo4j_manager = neo4j_manager
        self._es_client = es_client

    async def link(self, incident_ids: list[str]) -> LinkageResult:
        """
        Link incidents based on various correlation factors.

        Args:
            incident_ids: List of incident IDs to analyze

        Returns:
            LinkageResult with linked incidents and confidence scores
        """
        logger.info(f"Linking {len(incident_ids)} incidents")

        incidents = await self._fetch_incidents(incident_ids)

        if not incidents:
            return LinkageResult(
                linked_incidents=[],
                linkages=[],
                confidence_scores={},
                explanations=["No incidents found for the provided IDs"],
            )

        all_linkages: list[IncidentLinkage] = []
        linked_incident_ids: set[str] = set(incident_ids)
        confidence_scores: dict[str, float] = {}
        explanations: list[str] = []

        for incident in incidents:
            incident_id = incident.get("incident_id") or incident.get("id")

            temporal_links = await self._find_temporal_links(incident, incidents)
            all_linkages.extend(temporal_links)

            geographic_links = await self._find_geographic_links(incident, incidents)
            all_linkages.extend(geographic_links)

            entity_links = await self._find_entity_overlap_links(incident)
            all_linkages.extend(entity_links)
            for link in entity_links:
                linked_incident_ids.add(link.target_incident_id)

            narrative_links = await self._find_narrative_similarity_links(incident)
            all_linkages.extend(narrative_links)
            for link in narrative_links:
                linked_incident_ids.add(link.target_incident_id)

            ballistic_links = await self._find_ballistic_links(incident)
            all_linkages.extend(ballistic_links)
            for link in ballistic_links:
                linked_incident_ids.add(link.target_incident_id)

            vehicle_links = await self._find_vehicle_recurrence_links(incident)
            all_linkages.extend(vehicle_links)
            for link in vehicle_links:
                linked_incident_ids.add(link.target_incident_id)

            mo_links = await self._find_mo_similarity_links(incident)
            all_linkages.extend(mo_links)
            for link in mo_links:
                linked_incident_ids.add(link.target_incident_id)

            max_confidence = 0.0
            for link in all_linkages:
                if link.source_incident_id == incident_id:
                    max_confidence = max(max_confidence, link.confidence)

            confidence_scores[incident_id] = max_confidence

        all_linkages = self._deduplicate_linkages(all_linkages)

        linked_incidents = await self._fetch_incidents(list(linked_incident_ids))

        for linkage in all_linkages:
            explanations.append(
                f"{linkage.linkage_type.value}: {linkage.source_incident_id} -> "
                f"{linkage.target_incident_id} (confidence: {linkage.confidence:.2f}) - "
                f"{linkage.explanation}"
            )

        logger.info(f"Found {len(all_linkages)} linkages across {len(linked_incidents)} incidents")

        return LinkageResult(
            linked_incidents=[
                {
                    "incident_id": inc.get("incident_id") or inc.get("id"),
                    "incident_type": inc.get("incident_type") or inc.get("type"),
                    "timestamp": inc.get("timestamp") or inc.get("occurred_at"),
                    "location": inc.get("location") or inc.get("address"),
                    "summary": inc.get("summary") or inc.get("narrative", "")[:200],
                }
                for inc in linked_incidents
            ],
            linkages=all_linkages,
            confidence_scores=confidence_scores,
            explanations=explanations,
        )

    async def _fetch_incidents(self, incident_ids: list[str]) -> list[dict[str, Any]]:
        """Fetch incident details from Neo4j and Elasticsearch."""
        incidents = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident)
                WHERE i.incident_id IN $incident_ids OR i.id IN $incident_ids
                RETURN i
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_ids": incident_ids}
                )
                for record in result:
                    incidents.append(dict(record["i"]))
            except Exception as e:
                logger.warning(f"Error fetching incidents from Neo4j: {e}")

        if not incidents and self._es_client:
            try:
                query = {
                    "query": {"terms": {"incident_id": incident_ids}},
                    "size": len(incident_ids),
                }
                result = await self._es_client.search(index="incidents", body=query)
                for hit in result.get("hits", {}).get("hits", []):
                    incidents.append(hit["_source"])
            except Exception as e:
                logger.warning(f"Error fetching incidents from Elasticsearch: {e}")

        if not incidents:
            for incident_id in incident_ids:
                incidents.append(
                    {
                        "incident_id": incident_id,
                        "id": incident_id,
                        "incident_type": "unknown",
                        "timestamp": datetime.utcnow().isoformat(),
                        "location": {},
                        "summary": f"Incident {incident_id}",
                    }
                )

        return incidents

    async def _find_temporal_links(
        self,
        incident: dict[str, Any],
        all_incidents: list[dict[str, Any]],
    ) -> list[IncidentLinkage]:
        """Find incidents linked by temporal proximity."""
        linkages = []
        incident_id = incident.get("incident_id") or incident.get("id")
        incident_time = self._parse_timestamp(
            incident.get("timestamp") or incident.get("occurred_at")
        )

        if not incident_time:
            return linkages

        for other in all_incidents:
            other_id = other.get("incident_id") or other.get("id")
            if other_id == incident_id:
                continue

            other_time = self._parse_timestamp(other.get("timestamp") or other.get("occurred_at"))
            if not other_time:
                continue

            time_diff = abs((incident_time - other_time).total_seconds() / 3600)

            if time_diff <= self.TEMPORAL_WINDOW_HOURS:
                confidence = max(0, 1 - (time_diff / self.TEMPORAL_WINDOW_HOURS))
                confidence *= self.LINKAGE_WEIGHTS[LinkageType.TEMPORAL]

                if confidence >= self.MIN_CONFIDENCE_THRESHOLD:
                    linkages.append(
                        IncidentLinkage(
                            source_incident_id=incident_id,
                            target_incident_id=other_id,
                            linkage_type=LinkageType.TEMPORAL,
                            confidence=confidence,
                            explanation=f"Incidents occurred within {time_diff:.1f} hours of each other",
                            metadata={"time_diff_hours": time_diff},
                        )
                    )

        return linkages

    async def _find_geographic_links(
        self,
        incident: dict[str, Any],
        all_incidents: list[dict[str, Any]],
    ) -> list[IncidentLinkage]:
        """Find incidents linked by geographic proximity."""
        linkages = []
        incident_id = incident.get("incident_id") or incident.get("id")

        lat1 = self._get_latitude(incident)
        lon1 = self._get_longitude(incident)

        if lat1 is None or lon1 is None:
            return linkages

        for other in all_incidents:
            other_id = other.get("incident_id") or other.get("id")
            if other_id == incident_id:
                continue

            lat2 = self._get_latitude(other)
            lon2 = self._get_longitude(other)

            if lat2 is None or lon2 is None:
                continue

            distance = self._haversine_distance(lat1, lon1, lat2, lon2)

            if distance <= self.GEOGRAPHIC_RADIUS_KM:
                confidence = max(0, 1 - (distance / self.GEOGRAPHIC_RADIUS_KM))
                confidence *= self.LINKAGE_WEIGHTS[LinkageType.GEOGRAPHIC]

                if confidence >= self.MIN_CONFIDENCE_THRESHOLD:
                    linkages.append(
                        IncidentLinkage(
                            source_incident_id=incident_id,
                            target_incident_id=other_id,
                            linkage_type=LinkageType.GEOGRAPHIC,
                            confidence=confidence,
                            explanation=f"Incidents occurred within {distance:.2f} km of each other",
                            metadata={"distance_km": distance},
                        )
                    )

        return linkages

    async def _find_entity_overlap_links(self, incident: dict[str, Any]) -> list[IncidentLinkage]:
        """Find incidents linked by shared entities (persons, vehicles, addresses)."""
        linkages = []
        incident_id = incident.get("incident_id") or incident.get("id")

        if not self._neo4j_manager:
            return linkages

        try:
            query = """
            MATCH (i:Incident {incident_id: $incident_id})-[:INVOLVES|OCCURRED_AT|ASSOCIATED_WITH]-(e)
            MATCH (e)-[:INVOLVES|OCCURRED_AT|ASSOCIATED_WITH]-(other:Incident)
            WHERE other.incident_id <> $incident_id
            WITH other, collect(DISTINCT type(e)) as entity_types, count(DISTINCT e) as shared_count
            RETURN other.incident_id as other_id, entity_types, shared_count
            ORDER BY shared_count DESC
            LIMIT 20
            """
            result = await self._neo4j_manager.execute_query(query, {"incident_id": incident_id})

            for record in result:
                other_id = record["other_id"]
                shared_count = record["shared_count"]
                entity_types = record["entity_types"]

                confidence = min(1.0, shared_count * 0.2)
                confidence *= self.LINKAGE_WEIGHTS[LinkageType.ENTITY_OVERLAP]

                if confidence >= self.MIN_CONFIDENCE_THRESHOLD:
                    linkages.append(
                        IncidentLinkage(
                            source_incident_id=incident_id,
                            target_incident_id=other_id,
                            linkage_type=LinkageType.ENTITY_OVERLAP,
                            confidence=confidence,
                            explanation=f"Incidents share {shared_count} entities ({', '.join(entity_types)})",
                            metadata={
                                "shared_count": shared_count,
                                "entity_types": entity_types,
                            },
                        )
                    )

        except Exception as e:
            logger.warning(f"Error finding entity overlap links: {e}")

        return linkages

    async def _find_narrative_similarity_links(
        self, incident: dict[str, Any]
    ) -> list[IncidentLinkage]:
        """Find incidents linked by narrative/description similarity."""
        linkages = []
        incident_id = incident.get("incident_id") or incident.get("id")
        narrative = incident.get("narrative") or incident.get("summary") or ""

        if not narrative or not self._es_client:
            return linkages

        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "more_like_this": {
                                    "fields": ["narrative", "summary", "description"],
                                    "like": narrative,
                                    "min_term_freq": 1,
                                    "min_doc_freq": 1,
                                }
                            }
                        ],
                        "must_not": [{"term": {"incident_id": incident_id}}],
                    }
                },
                "size": 10,
            }
            result = await self._es_client.search(index="incidents", body=query)

            for hit in result.get("hits", {}).get("hits", []):
                other_id = hit["_source"].get("incident_id")
                score = hit.get("_score", 0)

                confidence = min(1.0, score / 10)
                confidence *= self.LINKAGE_WEIGHTS[LinkageType.NARRATIVE_SIMILARITY]

                if confidence >= self.MIN_CONFIDENCE_THRESHOLD:
                    linkages.append(
                        IncidentLinkage(
                            source_incident_id=incident_id,
                            target_incident_id=other_id,
                            linkage_type=LinkageType.NARRATIVE_SIMILARITY,
                            confidence=confidence,
                            explanation=f"Incident narratives have similar content (score: {score:.2f})",
                            metadata={"similarity_score": score},
                        )
                    )

        except Exception as e:
            logger.warning(f"Error finding narrative similarity links: {e}")

        return linkages

    async def _find_ballistic_links(self, incident: dict[str, Any]) -> list[IncidentLinkage]:
        """Find incidents linked by ballistic evidence matches."""
        linkages = []
        incident_id = incident.get("incident_id") or incident.get("id")

        if not self._neo4j_manager:
            return linkages

        try:
            query = """
            MATCH (i:Incident {incident_id: $incident_id})-[:HAS_EVIDENCE]->(b:BallisticEvidence)
            MATCH (b)-[:MATCHES]-(other_b:BallisticEvidence)<-[:HAS_EVIDENCE]-(other:Incident)
            WHERE other.incident_id <> $incident_id
            WITH other, b, other_b,
                 CASE WHEN b.weapon_id = other_b.weapon_id THEN 1.0
                      WHEN b.caliber = other_b.caliber THEN 0.7
                      ELSE 0.5 END as match_strength
            RETURN other.incident_id as other_id, match_strength,
                   b.caliber as caliber, b.weapon_type as weapon_type
            """
            result = await self._neo4j_manager.execute_query(query, {"incident_id": incident_id})

            for record in result:
                other_id = record["other_id"]
                match_strength = record["match_strength"]

                confidence = match_strength * self.LINKAGE_WEIGHTS[LinkageType.BALLISTIC_MATCH]

                if confidence >= self.MIN_CONFIDENCE_THRESHOLD:
                    linkages.append(
                        IncidentLinkage(
                            source_incident_id=incident_id,
                            target_incident_id=other_id,
                            linkage_type=LinkageType.BALLISTIC_MATCH,
                            confidence=confidence,
                            explanation=f"Ballistic evidence match ({record.get('caliber', 'unknown')} caliber)",
                            metadata={
                                "match_strength": match_strength,
                                "caliber": record.get("caliber"),
                                "weapon_type": record.get("weapon_type"),
                            },
                        )
                    )

        except Exception as e:
            logger.warning(f"Error finding ballistic links: {e}")

        return linkages

    async def _find_vehicle_recurrence_links(
        self, incident: dict[str, Any]
    ) -> list[IncidentLinkage]:
        """Find incidents linked by vehicle recurrence (LPR data)."""
        linkages = []
        incident_id = incident.get("incident_id") or incident.get("id")

        if not self._neo4j_manager:
            return linkages

        try:
            query = """
            MATCH (i:Incident {incident_id: $incident_id})-[:INVOLVES]->(v:Vehicle)
            MATCH (v)<-[:INVOLVES]-(other:Incident)
            WHERE other.incident_id <> $incident_id
            WITH other, v, count(*) as occurrence_count
            RETURN other.incident_id as other_id,
                   v.plate_number as plate,
                   occurrence_count
            ORDER BY occurrence_count DESC
            """
            result = await self._neo4j_manager.execute_query(query, {"incident_id": incident_id})

            for record in result:
                other_id = record["other_id"]
                plate = record["plate"]
                occurrence_count = record["occurrence_count"]

                confidence = min(1.0, occurrence_count * 0.3)
                confidence *= self.LINKAGE_WEIGHTS[LinkageType.VEHICLE_RECURRENCE]

                if confidence >= self.MIN_CONFIDENCE_THRESHOLD:
                    linkages.append(
                        IncidentLinkage(
                            source_incident_id=incident_id,
                            target_incident_id=other_id,
                            linkage_type=LinkageType.VEHICLE_RECURRENCE,
                            confidence=confidence,
                            explanation=f"Vehicle {plate} appears in both incidents",
                            metadata={
                                "plate_number": plate,
                                "occurrence_count": occurrence_count,
                            },
                        )
                    )

        except Exception as e:
            logger.warning(f"Error finding vehicle recurrence links: {e}")

        return linkages

    async def _find_mo_similarity_links(self, incident: dict[str, Any]) -> list[IncidentLinkage]:
        """Find incidents linked by similar modus operandi."""
        linkages = []
        incident_id = incident.get("incident_id") or incident.get("id")
        incident_type = incident.get("incident_type") or incident.get("type")
        mo_factors = incident.get("mo_factors") or {}

        if not incident_type:
            return linkages

        if self._es_client:
            try:
                query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"incident_type": incident_type}},
                            ],
                            "must_not": [{"term": {"incident_id": incident_id}}],
                            "should": [
                                {
                                    "match": {
                                        "mo_factors.entry_method": mo_factors.get(
                                            "entry_method", ""
                                        )
                                    }
                                },
                                {
                                    "match": {
                                        "mo_factors.weapon_used": mo_factors.get("weapon_used", "")
                                    }
                                },
                                {
                                    "match": {
                                        "mo_factors.target_type": mo_factors.get("target_type", "")
                                    }
                                },
                                {"range": {"timestamp": {"gte": "now-30d"}}},
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                    "size": 10,
                }
                result = await self._es_client.search(index="incidents", body=query)

                for hit in result.get("hits", {}).get("hits", []):
                    other_id = hit["_source"].get("incident_id")
                    score = hit.get("_score", 0)

                    confidence = min(1.0, score / 5)
                    confidence *= self.LINKAGE_WEIGHTS[LinkageType.MO_SIMILARITY]

                    if confidence >= self.MIN_CONFIDENCE_THRESHOLD:
                        linkages.append(
                            IncidentLinkage(
                                source_incident_id=incident_id,
                                target_incident_id=other_id,
                                linkage_type=LinkageType.MO_SIMILARITY,
                                confidence=confidence,
                                explanation=f"Similar M.O. pattern for {incident_type} incidents",
                                metadata={"mo_score": score},
                            )
                        )

            except Exception as e:
                logger.warning(f"Error finding M.O. similarity links: {e}")

        return linkages

    def _deduplicate_linkages(self, linkages: list[IncidentLinkage]) -> list[IncidentLinkage]:
        """Remove duplicate linkages, keeping highest confidence."""
        seen: dict[tuple[str, str, str], IncidentLinkage] = {}

        for linkage in linkages:
            key = (
                linkage.source_incident_id,
                linkage.target_incident_id,
                linkage.linkage_type.value,
            )

            if key not in seen or linkage.confidence > seen[key].confidence:
                seen[key] = linkage

        return list(seen.values())

    def _parse_timestamp(self, timestamp: Any) -> datetime | None:
        """Parse timestamp from various formats."""
        if timestamp is None:
            return None

        if isinstance(timestamp, datetime):
            return timestamp

        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                pass

            try:
                return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        return None

    def _get_latitude(self, incident: dict[str, Any]) -> float | None:
        """Extract latitude from incident."""
        if incident.get("latitude"):
            return float(incident["latitude"])

        location = incident.get("location") or {}
        if isinstance(location, dict) and location.get("latitude"):
            return float(location["latitude"])

        return None

    def _get_longitude(self, incident: dict[str, Any]) -> float | None:
        """Extract longitude from incident."""
        if incident.get("longitude"):
            return float(incident["longitude"])

        location = incident.get("location") or {}
        if isinstance(location, dict) and location.get("longitude"):
            return float(location["longitude"])

        return None

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c


__all__ = [
    "IncidentLinker",
]
