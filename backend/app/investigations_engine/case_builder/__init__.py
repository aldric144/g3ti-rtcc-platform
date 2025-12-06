"""
Case Auto-Builder Engine.

This module provides functionality for automatically building investigation
cases from incidents or suspects, including linking incidents, correlating
entities, collecting evidence, and generating investigative leads.
"""

import uuid
from datetime import datetime
from typing import Any

from app.core.logging import audit_logger, get_logger
from app.investigations_engine.models import (
    CaseFile,
    CasePriority,
    CaseStatus,
    EntitySummary,
    EvidencePackage,
    InvestigativeLead,
    RiskAssessment,
    TimelineEvent,
)

logger = get_logger(__name__)


class CaseBuilder:
    """
    Engine for automatically building investigation cases.

    Given an incident or suspect:
    - Auto-creates a case file object
    - Pulls all linked incidents
    - Pulls all entities
    - Builds case synopsis
    - Builds timeline
    - Attaches evidence
    - Auto-generates investigative leads
    - Assigns risk scores
    - Stores case record in Neo4j and Elasticsearch
    """

    def __init__(
        self,
        neo4j_manager: Any = None,
        es_client: Any = None,
        incident_linker: Any = None,
        entity_correlator: Any = None,
        evidence_collector: Any = None,
    ) -> None:
        """Initialize the Case Builder."""
        self._neo4j_manager = neo4j_manager
        self._es_client = es_client
        self._incident_linker = incident_linker
        self._entity_correlator = entity_correlator
        self._evidence_collector = evidence_collector

    async def build(
        self,
        incident_id: str | None = None,
        suspect_id: str | None = None,
        title: str | None = None,
        user_id: str = "",
    ) -> CaseFile:
        """
        Build a complete case file from an incident or suspect.

        Args:
            incident_id: Optional incident ID to build case from
            suspect_id: Optional suspect ID to build case from
            title: Optional case title
            user_id: ID of the user creating the case

        Returns:
            Complete CaseFile with all correlations and evidence
        """
        logger.info(f"Building case from incident={incident_id}, suspect={suspect_id}")

        now = datetime.utcnow()
        case_id = str(uuid.uuid4())
        year = now.year
        case_number = f"CASE-{year}-{uuid.uuid4().hex[:5].upper()}"

        linked_incidents = await self._get_linked_incidents(incident_id)

        suspects = await self._get_suspects(incident_id, suspect_id)
        vehicles = await self._get_vehicles(incident_id, suspect_id)
        addresses = await self._get_addresses(incident_id, suspect_id)
        weapons = await self._get_weapons(incident_id)

        incident_ids = [incident_id] if incident_id else []
        incident_ids.extend(
            [inc.get("incident_id") for inc in linked_incidents if inc.get("incident_id")]
        )

        entity_ids = [s.entity_id for s in suspects]
        entity_ids.extend([v.entity_id for v in vehicles])

        evidence = await self._collect_evidence(incident_ids, entity_ids)

        timeline = await self._build_timeline(incident_ids, entity_ids)

        risk_assessment = await self._assess_risk(suspects, vehicles, linked_incidents)

        leads = await self._generate_leads(
            incident_id=incident_id,
            suspects=suspects,
            vehicles=vehicles,
            linked_incidents=linked_incidents,
        )

        case_title = title or await self._generate_title(incident_id, suspect_id)
        summary = await self._generate_summary(
            incident_id=incident_id,
            suspect_id=suspect_id,
            linked_incidents=linked_incidents,
            suspects=suspects,
            vehicles=vehicles,
        )

        recommendations = await self._generate_recommendations(
            suspects=suspects,
            vehicles=vehicles,
            evidence=evidence,
            risk_assessment=risk_assessment,
        )

        case = CaseFile(
            case_id=case_id,
            case_number=case_number,
            title=case_title,
            summary=summary,
            status=CaseStatus.OPEN,
            priority=self._determine_priority(risk_assessment),
            created_at=now,
            updated_at=now,
            assigned_to=[user_id] if user_id else [],
            linked_incidents=linked_incidents,
            suspects=suspects,
            vehicles=vehicles,
            addresses=addresses,
            weapons=weapons,
            timeline=timeline,
            evidence=evidence,
            risk_assessment=risk_assessment,
            leads=leads,
            recommendations=recommendations,
        )

        await self._store_case(case)

        audit_logger.info(
            "Case created",
            extra={
                "case_id": case_id,
                "case_number": case_number,
                "user_id": user_id,
                "incident_id": incident_id,
                "suspect_id": suspect_id,
                "action": "case_created",
            },
        )

        return case

    async def _get_linked_incidents(self, incident_id: str | None) -> list[dict[str, Any]]:
        """Get incidents linked to the primary incident."""
        if not incident_id:
            return []

        if self._incident_linker:
            try:
                result = await self._incident_linker.link([incident_id])
                return result.linked_incidents
            except Exception as e:
                logger.warning(f"Error getting linked incidents: {e}")

        return [{"incident_id": incident_id, "status": "primary"}]

    async def _get_suspects(
        self,
        incident_id: str | None,
        suspect_id: str | None,
    ) -> list[EntitySummary]:
        """Get suspects related to the incident or specified suspect."""
        suspects = []

        if suspect_id and self._entity_correlator:
            try:
                profile = await self._entity_correlator.get_profile(suspect_id)
                suspects.append(profile)
            except Exception as e:
                logger.warning(f"Error getting suspect profile: {e}")

        if incident_id and self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident {incident_id: $incident_id})-[:SUSPECT_IN|INVOLVES]-(p:Person)
                RETURN p
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_id": incident_id}
                )

                for record in result:
                    person = dict(record["p"])
                    entity_id = person.get("entity_id") or person.get("id")

                    if entity_id and entity_id != suspect_id:
                        if self._entity_correlator:
                            try:
                                profile = await self._entity_correlator.get_profile(entity_id)
                                suspects.append(profile)
                            except Exception:
                                suspects.append(
                                    EntitySummary(
                                        entity_id=entity_id,
                                        entity_type="person",
                                        name=self._extract_name(person),
                                    )
                                )
                        else:
                            suspects.append(
                                EntitySummary(
                                    entity_id=entity_id,
                                    entity_type="person",
                                    name=self._extract_name(person),
                                )
                            )

            except Exception as e:
                logger.warning(f"Error getting suspects from incident: {e}")

        return suspects

    async def _get_vehicles(
        self,
        incident_id: str | None,
        suspect_id: str | None,
    ) -> list[EntitySummary]:
        """Get vehicles related to the incident or suspect."""
        vehicles = []

        if self._neo4j_manager:
            try:
                if incident_id:
                    query = """
                    MATCH (i:Incident {incident_id: $incident_id})-[:INVOLVES]-(v:Vehicle)
                    RETURN v
                    """
                    result = await self._neo4j_manager.execute_query(
                        query, {"incident_id": incident_id}
                    )

                    for record in result:
                        vehicle = dict(record["v"])
                        entity_id = vehicle.get("entity_id") or vehicle.get("id")
                        vehicles.append(
                            EntitySummary(
                                entity_id=entity_id,
                                entity_type="vehicle",
                                name=vehicle.get("plate_number") or "Unknown Vehicle",
                                metadata={
                                    "plate_number": vehicle.get("plate_number"),
                                    "make": vehicle.get("make"),
                                    "model": vehicle.get("model"),
                                    "year": vehicle.get("year"),
                                    "color": vehicle.get("color"),
                                    "vin": vehicle.get("vin"),
                                },
                            )
                        )

                if suspect_id:
                    query = """
                    MATCH (p)-[:OWNS|DRIVES]-(v:Vehicle)
                    WHERE p.entity_id = $suspect_id OR p.id = $suspect_id
                    RETURN v
                    """
                    result = await self._neo4j_manager.execute_query(
                        query, {"suspect_id": suspect_id}
                    )

                    for record in result:
                        vehicle = dict(record["v"])
                        entity_id = vehicle.get("entity_id") or vehicle.get("id")

                        if not any(v.entity_id == entity_id for v in vehicles):
                            vehicles.append(
                                EntitySummary(
                                    entity_id=entity_id,
                                    entity_type="vehicle",
                                    name=vehicle.get("plate_number") or "Unknown Vehicle",
                                    metadata={
                                        "plate_number": vehicle.get("plate_number"),
                                        "make": vehicle.get("make"),
                                        "model": vehicle.get("model"),
                                        "year": vehicle.get("year"),
                                        "color": vehicle.get("color"),
                                    },
                                )
                            )

            except Exception as e:
                logger.warning(f"Error getting vehicles: {e}")

        return vehicles

    async def _get_addresses(
        self,
        incident_id: str | None,
        suspect_id: str | None,
    ) -> list[dict[str, Any]]:
        """Get addresses related to the incident or suspect."""
        addresses = []

        if self._neo4j_manager:
            try:
                if incident_id:
                    query = """
                    MATCH (i:Incident {incident_id: $incident_id})-[:OCCURRED_AT]-(a:Address)
                    RETURN a
                    """
                    result = await self._neo4j_manager.execute_query(
                        query, {"incident_id": incident_id}
                    )

                    for record in result:
                        address = dict(record["a"])
                        addresses.append(
                            {
                                "address_id": address.get("address_id") or address.get("id"),
                                "street": address.get("street") or address.get("address"),
                                "city": address.get("city"),
                                "state": address.get("state"),
                                "zip": address.get("zip_code"),
                                "latitude": address.get("latitude"),
                                "longitude": address.get("longitude"),
                                "type": "incident_location",
                            }
                        )

                if suspect_id:
                    query = """
                    MATCH (p)-[:RESIDES_AT|ASSOCIATED_WITH]-(a:Address)
                    WHERE p.entity_id = $suspect_id OR p.id = $suspect_id
                    RETURN a
                    """
                    result = await self._neo4j_manager.execute_query(
                        query, {"suspect_id": suspect_id}
                    )

                    for record in result:
                        address = dict(record["a"])
                        address_id = address.get("address_id") or address.get("id")

                        if not any(a.get("address_id") == address_id for a in addresses):
                            addresses.append(
                                {
                                    "address_id": address_id,
                                    "street": address.get("street") or address.get("address"),
                                    "city": address.get("city"),
                                    "state": address.get("state"),
                                    "zip": address.get("zip_code"),
                                    "latitude": address.get("latitude"),
                                    "longitude": address.get("longitude"),
                                    "type": "suspect_address",
                                }
                            )

            except Exception as e:
                logger.warning(f"Error getting addresses: {e}")

        return addresses

    async def _get_weapons(self, incident_id: str | None) -> list[dict[str, Any]]:
        """Get weapons related to the incident."""
        weapons = []

        if incident_id and self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident {incident_id: $incident_id})-[:INVOLVES|HAS_EVIDENCE]-(w:Weapon)
                OPTIONAL MATCH (w)-[:HAS_BALLISTIC]-(b:BallisticEvidence)
                RETURN w, collect(b) as ballistics
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_id": incident_id}
                )

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
                        }
                    )

            except Exception as e:
                logger.warning(f"Error getting weapons: {e}")

        return weapons

    async def _collect_evidence(
        self,
        incident_ids: list[str],
        entity_ids: list[str],
    ) -> EvidencePackage:
        """Collect all evidence for the case."""
        if self._evidence_collector:
            try:
                return await self._evidence_collector.collect(
                    incident_ids=incident_ids,
                    entity_ids=entity_ids,
                )
            except Exception as e:
                logger.warning(f"Error collecting evidence: {e}")

        return EvidencePackage()

    async def _build_timeline(
        self,
        incident_ids: list[str],
        entity_ids: list[str],
    ) -> list[TimelineEvent]:
        """Build timeline for the case."""
        from app.investigations_engine.timeline_generator import TimelineGenerator

        generator = TimelineGenerator(
            neo4j_manager=self._neo4j_manager,
            es_client=self._es_client,
        )

        return await generator.generate_from_data(
            incident_ids=incident_ids,
            entity_ids=entity_ids,
        )

    async def _assess_risk(
        self,
        suspects: list[EntitySummary],
        vehicles: list[EntitySummary],
        linked_incidents: list[dict[str, Any]],
    ) -> RiskAssessment:
        """Assess overall risk for the case."""
        factors = []
        overall_score = 0.0

        suspect_risk = sum(s.risk_score for s in suspects) / max(len(suspects), 1)
        if suspect_risk > 0:
            factors.append(
                {
                    "factor": "suspect_risk",
                    "score": suspect_risk,
                    "description": f"Average suspect risk score: {suspect_risk:.2f}",
                }
            )
            overall_score += suspect_risk * 0.4

        incident_count = len(linked_incidents)
        if incident_count > 1:
            incident_factor = min(1.0, incident_count * 0.1)
            factors.append(
                {
                    "factor": "linked_incidents",
                    "score": incident_factor,
                    "description": f"{incident_count} linked incidents",
                }
            )
            overall_score += incident_factor * 0.3

        vehicle_count = len(vehicles)
        if vehicle_count > 0:
            vehicle_factor = min(1.0, vehicle_count * 0.15)
            factors.append(
                {
                    "factor": "vehicle_involvement",
                    "score": vehicle_factor,
                    "description": f"{vehicle_count} vehicles involved",
                }
            )
            overall_score += vehicle_factor * 0.2

        high_risk_suspects = [s for s in suspects if s.risk_score > 0.7]
        if high_risk_suspects:
            factors.append(
                {
                    "factor": "high_risk_suspects",
                    "score": 0.8,
                    "description": f"{len(high_risk_suspects)} high-risk suspects identified",
                }
            )
            overall_score += 0.1

        overall_score = min(1.0, overall_score)

        if overall_score >= 0.8:
            threat_level = "critical"
        elif overall_score >= 0.6:
            threat_level = "high"
        elif overall_score >= 0.4:
            threat_level = "medium"
        else:
            threat_level = "low"

        recommendations = []
        if threat_level in ["critical", "high"]:
            recommendations.append("Prioritize immediate investigation")
            recommendations.append("Consider surveillance on high-risk suspects")
        if incident_count > 3:
            recommendations.append("Review pattern analysis for serial activity")
        if vehicle_count > 0:
            recommendations.append("Set up LPR alerts for involved vehicles")

        return RiskAssessment(
            overall_score=overall_score,
            threat_level=threat_level,
            factors=factors,
            recommendations=recommendations,
        )

    async def _generate_leads(
        self,
        incident_id: str | None,
        suspects: list[EntitySummary],
        vehicles: list[EntitySummary],
        linked_incidents: list[dict[str, Any]],
    ) -> list[InvestigativeLead]:
        """Generate investigative leads for the case."""
        leads = []

        for suspect in suspects:
            if suspect.known_associates:
                leads.append(
                    InvestigativeLead(
                        lead_id=str(uuid.uuid4()),
                        title=f"Interview associates of {suspect.name}",
                        description=f"Suspect has {len(suspect.known_associates)} known associates who may have information",
                        priority=CasePriority.HIGH,
                        source="entity_correlation",
                        confidence=0.7,
                        action_items=[
                            f"Contact associate: {a.get('name', 'Unknown')}"
                            for a in suspect.known_associates[:3]
                        ],
                        related_entities=[suspect.entity_id],
                    )
                )

            if suspect.lpr_activity:
                leads.append(
                    InvestigativeLead(
                        lead_id=str(uuid.uuid4()),
                        title=f"Review LPR activity for {suspect.name}",
                        description=f"Suspect has {len(suspect.lpr_activity)} recent LPR hits",
                        priority=CasePriority.MEDIUM,
                        source="lpr_analysis",
                        confidence=0.8,
                        action_items=[
                            "Map vehicle movement patterns",
                            "Identify frequent locations",
                            "Cross-reference with incident times",
                        ],
                        related_entities=[suspect.entity_id],
                    )
                )

        for vehicle in vehicles:
            leads.append(
                InvestigativeLead(
                    lead_id=str(uuid.uuid4()),
                    title=f"Set up LPR alert for {vehicle.name}",
                    description=f"Monitor vehicle {vehicle.name} for future sightings",
                    priority=CasePriority.MEDIUM,
                    source="vehicle_tracking",
                    confidence=0.9,
                    action_items=[
                        "Create Flock hotlist entry",
                        "Set up real-time alert",
                        "Review historical LPR data",
                    ],
                    related_entities=[vehicle.entity_id],
                )
            )

        if len(linked_incidents) > 2:
            leads.append(
                InvestigativeLead(
                    lead_id=str(uuid.uuid4()),
                    title="Analyze incident pattern",
                    description=f"Multiple linked incidents ({len(linked_incidents)}) suggest possible serial activity",
                    priority=CasePriority.HIGH,
                    source="pattern_analysis",
                    confidence=0.75,
                    action_items=[
                        "Review M.O. similarities",
                        "Map geographic pattern",
                        "Identify temporal patterns",
                        "Check for additional unreported incidents",
                    ],
                    related_entities=[],
                )
            )

        return leads

    async def _generate_title(
        self,
        incident_id: str | None,
        suspect_id: str | None,
    ) -> str:
        """Generate a title for the case."""
        if incident_id:
            if self._neo4j_manager:
                try:
                    query = """
                    MATCH (i:Incident {incident_id: $incident_id})
                    RETURN i.incident_type as type, i.location as location
                    """
                    result = await self._neo4j_manager.execute_query(
                        query, {"incident_id": incident_id}
                    )
                    if result:
                        inc_type = result[0].get("type", "Incident")
                        return f"{inc_type} Investigation - {incident_id}"
                except Exception:
                    pass

            return f"Investigation - {incident_id}"

        if suspect_id:
            return f"Suspect Investigation - {suspect_id}"

        return f"Investigation - {datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    async def _generate_summary(
        self,
        incident_id: str | None,
        suspect_id: str | None,
        linked_incidents: list[dict[str, Any]],
        suspects: list[EntitySummary],
        vehicles: list[EntitySummary],
    ) -> str:
        """Generate a summary for the case."""
        parts = []

        if incident_id:
            parts.append(f"Investigation initiated from incident {incident_id}.")

        if suspect_id:
            parts.append(f"Primary suspect: {suspect_id}.")

        if len(linked_incidents) > 1:
            parts.append(f"Analysis identified {len(linked_incidents)} linked incidents.")

        if suspects:
            suspect_names = [s.name for s in suspects[:3]]
            parts.append(f"Suspects identified: {', '.join(suspect_names)}.")

        if vehicles:
            vehicle_plates = [v.name for v in vehicles[:3]]
            parts.append(f"Vehicles of interest: {', '.join(vehicle_plates)}.")

        if not parts:
            parts.append("New investigation case created for analysis.")

        return " ".join(parts)

    async def _generate_recommendations(
        self,
        suspects: list[EntitySummary],
        vehicles: list[EntitySummary],
        evidence: EvidencePackage,
        risk_assessment: RiskAssessment,
    ) -> list[str]:
        """Generate recommendations for the case."""
        recommendations = []

        if risk_assessment.threat_level in ["critical", "high"]:
            recommendations.append("Escalate to supervisor for priority handling")

        if suspects:
            recommendations.append("Run background checks on all identified suspects")

        if vehicles:
            recommendations.append("Set up LPR alerts for all vehicles of interest")

        if evidence.total_items < 5:
            recommendations.append("Gather additional evidence from available sources")

        if evidence.bwc_interactions:
            recommendations.append("Review all BWC footage for additional leads")

        if evidence.ballistics:
            recommendations.append("Request NIBIN analysis for ballistic evidence")

        recommendations.extend(risk_assessment.recommendations)

        return list(set(recommendations))

    def _determine_priority(self, risk_assessment: RiskAssessment) -> CasePriority:
        """Determine case priority based on risk assessment."""
        if risk_assessment.threat_level == "critical":
            return CasePriority.CRITICAL
        elif risk_assessment.threat_level == "high":
            return CasePriority.HIGH
        elif risk_assessment.threat_level == "medium":
            return CasePriority.MEDIUM
        else:
            return CasePriority.LOW

    async def _store_case(self, case: CaseFile) -> None:
        """Store case in Neo4j and Elasticsearch."""
        if self._neo4j_manager:
            try:
                query = """
                CREATE (c:Case {
                    case_id: $case_id,
                    case_number: $case_number,
                    title: $title,
                    summary: $summary,
                    status: $status,
                    priority: $priority,
                    created_at: datetime($created_at),
                    updated_at: datetime($updated_at)
                })
                RETURN c
                """
                await self._neo4j_manager.execute_query(
                    query,
                    {
                        "case_id": case.case_id,
                        "case_number": case.case_number,
                        "title": case.title,
                        "summary": case.summary,
                        "status": case.status.value,
                        "priority": case.priority.value,
                        "created_at": case.created_at.isoformat(),
                        "updated_at": case.updated_at.isoformat(),
                    },
                )

                for incident in case.linked_incidents:
                    incident_id = incident.get("incident_id")
                    if incident_id:
                        link_query = """
                        MATCH (c:Case {case_id: $case_id})
                        MATCH (i:Incident {incident_id: $incident_id})
                        MERGE (c)-[:INCLUDES]->(i)
                        """
                        await self._neo4j_manager.execute_query(
                            link_query,
                            {"case_id": case.case_id, "incident_id": incident_id},
                        )

            except Exception as e:
                logger.warning(f"Error storing case in Neo4j: {e}")

        if self._es_client:
            try:
                await self._es_client.index(
                    index="cases",
                    id=case.case_id,
                    body=case.to_dict(),
                )
            except Exception as e:
                logger.warning(f"Error storing case in Elasticsearch: {e}")

    def _extract_name(self, entity_data: dict[str, Any]) -> str:
        """Extract display name from entity data."""
        if entity_data.get("name"):
            return entity_data["name"]

        if entity_data.get("first_name") or entity_data.get("last_name"):
            first = entity_data.get("first_name", "")
            last = entity_data.get("last_name", "")
            return f"{first} {last}".strip()

        return entity_data.get("entity_id") or entity_data.get("id") or "Unknown"


__all__ = [
    "CaseBuilder",
]
