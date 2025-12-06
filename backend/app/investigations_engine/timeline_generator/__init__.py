"""
Timeline Generation Engine.

This module provides functionality for generating comprehensive timelines
for investigation cases, including events from CAD, RMS, LPR, ShotSpotter,
BWC, and entity interactions.
"""

import uuid
from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.investigations_engine.models import TimelineEvent, TimelineEventType

logger = get_logger(__name__)


class TimelineGenerator:
    """
    Engine for generating investigation timelines.

    Timeline includes:
    - CAD events
    - RMS report times
    - LPR timestamps
    - Gunfire alerts
    - BWC encounters
    - Vehicle travel paths
    - Entity-to-entity interactions

    Events are automatically ordered by time and source reliability.
    """

    SOURCE_RELIABILITY = {
        "CAD": 0.95,
        "RMS": 0.98,
        "LPR": 0.90,
        "ShotSpotter": 0.85,
        "BWC": 0.95,
        "NESS": 0.98,
        "Witness": 0.60,
        "Unknown": 0.50,
    }

    def __init__(
        self,
        neo4j_manager: Any = None,
        es_client: Any = None,
    ) -> None:
        """Initialize the Timeline Generator."""
        self._neo4j_manager = neo4j_manager
        self._es_client = es_client

    async def generate(self, case_id: str) -> list[TimelineEvent]:
        """
        Generate timeline for a case.

        Args:
            case_id: ID of the case

        Returns:
            List of TimelineEvent objects ordered by time
        """
        logger.info(f"Generating timeline for case: {case_id}")

        incident_ids = await self._get_case_incidents(case_id)
        entity_ids = await self._get_case_entities(case_id)

        return await self.generate_from_data(
            incident_ids=incident_ids,
            entity_ids=entity_ids,
        )

    async def generate_from_data(
        self,
        incident_ids: list[str],
        entity_ids: list[str],
    ) -> list[TimelineEvent]:
        """
        Generate timeline from incident and entity IDs.

        Args:
            incident_ids: List of incident IDs
            entity_ids: List of entity IDs

        Returns:
            List of TimelineEvent objects ordered by time
        """
        logger.info(
            f"Generating timeline from {len(incident_ids)} incidents "
            f"and {len(entity_ids)} entities"
        )

        events: list[TimelineEvent] = []

        cad_events = await self._get_cad_events(incident_ids)
        events.extend(cad_events)

        rms_events = await self._get_rms_events(incident_ids)
        events.extend(rms_events)

        lpr_events = await self._get_lpr_events(entity_ids)
        events.extend(lpr_events)

        gunfire_events = await self._get_gunfire_events(incident_ids)
        events.extend(gunfire_events)

        bwc_events = await self._get_bwc_events(entity_ids)
        events.extend(bwc_events)

        interaction_events = await self._get_entity_interactions(entity_ids)
        events.extend(interaction_events)

        events = self._sort_and_deduplicate(events)

        logger.info(f"Generated timeline with {len(events)} events")

        return events

    async def _get_case_incidents(self, case_id: str) -> list[str]:
        """Get incident IDs for a case."""
        incident_ids = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (c:Case {case_id: $case_id})-[:INCLUDES]->(i:Incident)
                RETURN i.incident_id as incident_id
                """
                result = await self._neo4j_manager.execute_query(query, {"case_id": case_id})
                incident_ids = [r["incident_id"] for r in result if r.get("incident_id")]
            except Exception as e:
                logger.warning(f"Error getting case incidents: {e}")

        return incident_ids

    async def _get_case_entities(self, case_id: str) -> list[str]:
        """Get entity IDs for a case."""
        entity_ids = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (c:Case {case_id: $case_id})-[:INCLUDES]->(i:Incident)
                MATCH (i)-[:INVOLVES|SUSPECT_IN|VICTIM_IN]-(e)
                WHERE e:Person OR e:Vehicle
                RETURN DISTINCT e.entity_id as entity_id
                """
                result = await self._neo4j_manager.execute_query(query, {"case_id": case_id})
                entity_ids = [r["entity_id"] for r in result if r.get("entity_id")]
            except Exception as e:
                logger.warning(f"Error getting case entities: {e}")

        return entity_ids

    async def _get_cad_events(self, incident_ids: list[str]) -> list[TimelineEvent]:
        """Get CAD events for incidents."""
        events = []

        if not incident_ids:
            return events

        if self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident)-[:HAS_CAD_RECORD]->(c:CADRecord)
                WHERE i.incident_id IN $incident_ids OR i.id IN $incident_ids
                RETURN c, i.incident_id as incident_id
                ORDER BY c.timestamp
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_ids": incident_ids}
                )

                for record in result:
                    cad = dict(record["c"])
                    timestamp = self._parse_timestamp(cad.get("timestamp"))

                    if timestamp:
                        events.append(
                            TimelineEvent(
                                event_id=cad.get("cad_id") or str(uuid.uuid4()),
                                timestamp=timestamp,
                                event_type=TimelineEventType.CAD_DISPATCH,
                                description=self._format_cad_description(cad),
                                source="CAD",
                                location=self._extract_location(cad),
                                entities_involved=[record.get("incident_id")],
                                metadata={
                                    "call_number": cad.get("call_number"),
                                    "call_type": cad.get("call_type"),
                                    "priority": cad.get("priority"),
                                    "disposition": cad.get("disposition"),
                                },
                                reliability_score=self.SOURCE_RELIABILITY["CAD"],
                            )
                        )

                        for update in cad.get("updates", []):
                            update_time = self._parse_timestamp(update.get("timestamp"))
                            if update_time:
                                events.append(
                                    TimelineEvent(
                                        event_id=str(uuid.uuid4()),
                                        timestamp=update_time,
                                        event_type=TimelineEventType.CAD_UPDATE,
                                        description=update.get("narrative", "CAD update"),
                                        source="CAD",
                                        location=self._extract_location(cad),
                                        entities_involved=[record.get("incident_id")],
                                        metadata={"update_type": update.get("type")},
                                        reliability_score=self.SOURCE_RELIABILITY["CAD"],
                                    )
                                )

            except Exception as e:
                logger.warning(f"Error getting CAD events: {e}")

        return events

    async def _get_rms_events(self, incident_ids: list[str]) -> list[TimelineEvent]:
        """Get RMS report events for incidents."""
        events = []

        if not incident_ids:
            return events

        if self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident)-[:HAS_REPORT]->(r:RMSReport)
                WHERE i.incident_id IN $incident_ids OR i.id IN $incident_ids
                RETURN r, i.incident_id as incident_id
                ORDER BY r.created_at
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_ids": incident_ids}
                )

                for record in result:
                    report = dict(record["r"])
                    timestamp = self._parse_timestamp(
                        report.get("created_at") or report.get("report_date")
                    )

                    if timestamp:
                        events.append(
                            TimelineEvent(
                                event_id=report.get("report_id") or str(uuid.uuid4()),
                                timestamp=timestamp,
                                event_type=TimelineEventType.RMS_REPORT,
                                description=f"RMS Report filed: {report.get('report_number', 'Unknown')}",
                                source="RMS",
                                location=self._extract_location(report),
                                entities_involved=[record.get("incident_id")],
                                metadata={
                                    "report_number": report.get("report_number"),
                                    "report_type": report.get("report_type"),
                                    "officer_id": report.get("officer_id"),
                                },
                                reliability_score=self.SOURCE_RELIABILITY["RMS"],
                            )
                        )

            except Exception as e:
                logger.warning(f"Error getting RMS events: {e}")

        return events

    async def _get_lpr_events(self, entity_ids: list[str]) -> list[TimelineEvent]:
        """Get LPR detection events for entities."""
        events = []

        if not entity_ids:
            return events

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:OWNS|DRIVES]-(v:Vehicle)-[:DETECTED_BY]-(lpr:LPRHit)
                WHERE e.entity_id IN $entity_ids OR e.id IN $entity_ids
                RETURN lpr, v.plate_number as plate, e.entity_id as entity_id
                ORDER BY lpr.timestamp
                LIMIT 100
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_ids": entity_ids})

                for record in result:
                    hit = dict(record["lpr"])
                    timestamp = self._parse_timestamp(hit.get("timestamp"))

                    if timestamp:
                        events.append(
                            TimelineEvent(
                                event_id=hit.get("hit_id") or str(uuid.uuid4()),
                                timestamp=timestamp,
                                event_type=TimelineEventType.LPR_DETECTION,
                                description=f"Vehicle {record.get('plate', 'Unknown')} detected by LPR",
                                source="LPR",
                                location={
                                    "latitude": hit.get("latitude"),
                                    "longitude": hit.get("longitude"),
                                    "address": hit.get("location"),
                                },
                                entities_involved=[record.get("entity_id")],
                                metadata={
                                    "plate_number": record.get("plate"),
                                    "camera_id": hit.get("camera_id"),
                                    "direction": hit.get("direction"),
                                    "alert_type": hit.get("alert_type"),
                                },
                                reliability_score=self.SOURCE_RELIABILITY["LPR"],
                            )
                        )

            except Exception as e:
                logger.warning(f"Error getting LPR events: {e}")

        return events

    async def _get_gunfire_events(self, incident_ids: list[str]) -> list[TimelineEvent]:
        """Get gunfire alert events for incidents."""
        events = []

        if not incident_ids:
            return events

        if self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident)-[:HAS_GUNFIRE_ALERT]->(g:GunfireAlert)
                WHERE i.incident_id IN $incident_ids OR i.id IN $incident_ids
                RETURN g, i.incident_id as incident_id
                ORDER BY g.timestamp
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_ids": incident_ids}
                )

                for record in result:
                    alert = dict(record["g"])
                    timestamp = self._parse_timestamp(alert.get("timestamp"))

                    if timestamp:
                        round_count = alert.get("round_count", "Unknown")
                        events.append(
                            TimelineEvent(
                                event_id=alert.get("alert_id") or str(uuid.uuid4()),
                                timestamp=timestamp,
                                event_type=TimelineEventType.GUNFIRE_ALERT,
                                description=f"Gunfire detected: {round_count} rounds",
                                source="ShotSpotter",
                                location={
                                    "latitude": alert.get("latitude"),
                                    "longitude": alert.get("longitude"),
                                    "address": alert.get("address"),
                                },
                                entities_involved=[record.get("incident_id")],
                                metadata={
                                    "alert_id": alert.get("alert_id"),
                                    "round_count": round_count,
                                    "confidence": alert.get("confidence"),
                                },
                                reliability_score=self.SOURCE_RELIABILITY["ShotSpotter"],
                            )
                        )

            except Exception as e:
                logger.warning(f"Error getting gunfire events: {e}")

        return events

    async def _get_bwc_events(self, entity_ids: list[str]) -> list[TimelineEvent]:
        """Get BWC encounter events for entities."""
        events = []

        if not entity_ids:
            return events

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:APPEARS_IN|INTERACTS_WITH]-(bwc:BWCRecording)
                WHERE e.entity_id IN $entity_ids OR e.id IN $entity_ids
                RETURN bwc, e.entity_id as entity_id
                ORDER BY bwc.timestamp
                LIMIT 50
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_ids": entity_ids})

                for record in result:
                    bwc = dict(record["bwc"])
                    timestamp = self._parse_timestamp(bwc.get("timestamp"))

                    if timestamp:
                        events.append(
                            TimelineEvent(
                                event_id=bwc.get("recording_id") or str(uuid.uuid4()),
                                timestamp=timestamp,
                                event_type=TimelineEventType.BWC_ACTIVATION,
                                description=f"BWC recording by Officer {bwc.get('officer_id', 'Unknown')}",
                                source="BWC",
                                location=self._extract_location(bwc),
                                entities_involved=[record.get("entity_id")],
                                metadata={
                                    "recording_id": bwc.get("recording_id"),
                                    "officer_id": bwc.get("officer_id"),
                                    "duration": bwc.get("duration"),
                                    "incident_id": bwc.get("incident_id"),
                                },
                                reliability_score=self.SOURCE_RELIABILITY["BWC"],
                            )
                        )

            except Exception as e:
                logger.warning(f"Error getting BWC events: {e}")

        return events

    async def _get_entity_interactions(self, entity_ids: list[str]) -> list[TimelineEvent]:
        """Get entity-to-entity interaction events."""
        events = []

        if not entity_ids or len(entity_ids) < 2:
            return events

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e1)-[r:INTERACTED_WITH|MET_WITH|CONTACTED]-(e2)
                WHERE (e1.entity_id IN $entity_ids OR e1.id IN $entity_ids)
                  AND (e2.entity_id IN $entity_ids OR e2.id IN $entity_ids)
                  AND e1.entity_id < e2.entity_id
                RETURN e1, e2, r, type(r) as rel_type
                ORDER BY r.timestamp
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_ids": entity_ids})

                for record in result:
                    e1 = dict(record["e1"])
                    e2 = dict(record["e2"])
                    rel = dict(record["r"]) if record["r"] else {}
                    timestamp = self._parse_timestamp(rel.get("timestamp"))

                    if timestamp:
                        e1_name = self._extract_name(e1)
                        e2_name = self._extract_name(e2)
                        events.append(
                            TimelineEvent(
                                event_id=str(uuid.uuid4()),
                                timestamp=timestamp,
                                event_type=TimelineEventType.ENTITY_INTERACTION,
                                description=f"Interaction between {e1_name} and {e2_name}",
                                source="Graph Analysis",
                                location=self._extract_location(rel),
                                entities_involved=[
                                    e1.get("entity_id") or e1.get("id"),
                                    e2.get("entity_id") or e2.get("id"),
                                ],
                                metadata={
                                    "relationship_type": record.get("rel_type"),
                                },
                                reliability_score=0.70,
                            )
                        )

            except Exception as e:
                logger.warning(f"Error getting entity interactions: {e}")

        return events

    def _sort_and_deduplicate(self, events: list[TimelineEvent]) -> list[TimelineEvent]:
        """Sort events by timestamp and remove duplicates."""
        seen_ids: set[str] = set()
        unique_events = []

        for event in events:
            if event.event_id not in seen_ids:
                seen_ids.add(event.event_id)
                unique_events.append(event)

        unique_events.sort(key=lambda e: (e.timestamp, -e.reliability_score))

        return unique_events

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

    def _extract_location(self, data: dict[str, Any]) -> dict[str, Any] | None:
        """Extract location from data."""
        location = data.get("location")
        if isinstance(location, dict):
            return location

        lat = data.get("latitude")
        lon = data.get("longitude")
        address = data.get("address") or data.get("location")

        if lat or lon or address:
            return {
                "latitude": lat,
                "longitude": lon,
                "address": address if isinstance(address, str) else None,
            }

        return None

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

        return entity_data.get("entity_id") or entity_data.get("id") or "Unknown"

    def _format_cad_description(self, cad: dict[str, Any]) -> str:
        """Format CAD event description."""
        call_type = cad.get("call_type", "Unknown")
        priority = cad.get("priority", "")
        location = cad.get("location") or cad.get("address") or ""

        parts = [f"CAD Dispatch: {call_type}"]
        if priority:
            parts.append(f"(Priority {priority})")
        if location and isinstance(location, str):
            parts.append(f"at {location}")

        return " ".join(parts)


__all__ = [
    "TimelineGenerator",
]
