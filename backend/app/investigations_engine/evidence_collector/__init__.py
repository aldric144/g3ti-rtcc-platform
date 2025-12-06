"""
Evidence Auto-Collection Module.

This module provides functionality for automatically collecting evidence
from multiple data sources including RMS, CAD, ShotSpotter, LPR, BWC,
NESS ballistics, and camera systems.
"""

import uuid
from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.investigations_engine.models import (
    EvidenceItem,
    EvidencePackage,
    EvidenceType,
)

logger = get_logger(__name__)


class EvidenceCollector:
    """
    Engine for automatically collecting evidence from multiple sources.

    Gathers evidence from:
    - RMS reports
    - CAD history
    - ShotSpotter audio metadata
    - LPR hits
    - BWC metadata
    - NESS ballistics
    - Camera snapshots
    """

    def __init__(
        self,
        neo4j_manager: Any = None,
        es_client: Any = None,
    ) -> None:
        """Initialize the Evidence Collector."""
        self._neo4j_manager = neo4j_manager
        self._es_client = es_client

    async def collect(
        self,
        incident_ids: list[str] | None = None,
        entity_ids: list[str] | None = None,
        case_id: str | None = None,
    ) -> EvidencePackage:
        """
        Collect all evidence related to incidents and entities.

        Args:
            incident_ids: List of incident IDs to collect evidence from
            entity_ids: List of entity IDs to collect evidence for
            case_id: Optional case ID for audit logging

        Returns:
            EvidencePackage with all collected evidence
        """
        logger.info(
            f"Collecting evidence for {len(incident_ids or [])} incidents "
            f"and {len(entity_ids or [])} entities"
        )

        package = EvidencePackage()

        if incident_ids:
            rms_reports = await self.gather_rms_reports(incident_ids)
            package.reports.extend(rms_reports)

            cad_records = await self.gather_cad_history(incident_ids)
            package.reports.extend(cad_records)

            audio_metadata = await self.gather_shotspotter_audio(incident_ids)
            package.audio_metadata.extend(audio_metadata)

            ballistics = await self.gather_ness_ballistics(incident_ids)
            package.ballistics.extend(ballistics)

        if entity_ids:
            lpr_hits = await self.gather_lpr_hits(entity_ids)
            package.lpr_trail.extend(lpr_hits)

            bwc_metadata = await self.gather_bwc_metadata(entity_ids)
            package.bwc_interactions.extend(bwc_metadata)

            camera_snapshots = await self.gather_camera_snapshots(entity_ids)
            package.camera_positions.extend(camera_snapshots)

        logger.info(f"Collected {package.total_items} evidence items")

        return package

    async def gather_rms_reports(self, incident_ids: list[str]) -> list[EvidenceItem]:
        """
        Gather RMS reports for incidents.

        Args:
            incident_ids: List of incident IDs

        Returns:
            List of EvidenceItem objects for RMS reports
        """
        logger.info(f"Gathering RMS reports for {len(incident_ids)} incidents")
        reports = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident)-[:HAS_REPORT]->(r:RMSReport)
                WHERE i.incident_id IN $incident_ids OR i.id IN $incident_ids
                RETURN r, i.incident_id as incident_id
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_ids": incident_ids}
                )

                for record in result:
                    report = dict(record["r"])
                    reports.append(
                        EvidenceItem(
                            evidence_id=report.get("report_id") or str(uuid.uuid4()),
                            evidence_type=EvidenceType.RMS_REPORT,
                            source="RMS",
                            title=f"RMS Report - {report.get('report_number', 'Unknown')}",
                            description=report.get("narrative", "")[:500],
                            collected_at=datetime.utcnow(),
                            metadata={
                                "report_number": report.get("report_number"),
                                "incident_id": record.get("incident_id"),
                                "report_type": report.get("report_type"),
                                "officer_id": report.get("officer_id"),
                                "created_at": report.get("created_at"),
                            },
                            confidence=1.0,
                            is_verified=True,
                        )
                    )

            except Exception as e:
                logger.warning(f"Error gathering RMS reports: {e}")

        if self._es_client and not reports:
            try:
                query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"terms": {"incident_id": incident_ids}},
                                {"term": {"document_type": "rms_report"}},
                            ]
                        }
                    },
                    "size": 100,
                }
                result = await self._es_client.search(index="reports", body=query)

                for hit in result.get("hits", {}).get("hits", []):
                    doc = hit["_source"]
                    reports.append(
                        EvidenceItem(
                            evidence_id=doc.get("report_id") or hit["_id"],
                            evidence_type=EvidenceType.RMS_REPORT,
                            source="RMS",
                            title=f"RMS Report - {doc.get('report_number', 'Unknown')}",
                            description=doc.get("narrative", "")[:500],
                            collected_at=datetime.utcnow(),
                            metadata=doc,
                            confidence=1.0,
                            is_verified=True,
                        )
                    )

            except Exception as e:
                logger.warning(f"Error gathering RMS reports from ES: {e}")

        return reports

    async def gather_cad_history(self, incident_ids: list[str]) -> list[EvidenceItem]:
        """
        Gather CAD history for incidents.

        Args:
            incident_ids: List of incident IDs

        Returns:
            List of EvidenceItem objects for CAD records
        """
        logger.info(f"Gathering CAD history for {len(incident_ids)} incidents")
        records = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident)-[:HAS_CAD_RECORD]->(c:CADRecord)
                WHERE i.incident_id IN $incident_ids OR i.id IN $incident_ids
                RETURN c, i.incident_id as incident_id
                ORDER BY c.timestamp DESC
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_ids": incident_ids}
                )

                for record in result:
                    cad = dict(record["c"])
                    records.append(
                        EvidenceItem(
                            evidence_id=cad.get("cad_id") or str(uuid.uuid4()),
                            evidence_type=EvidenceType.CAD_RECORD,
                            source="CAD",
                            title=f"CAD Record - {cad.get('call_number', 'Unknown')}",
                            description=cad.get("narrative", "") or cad.get("comments", ""),
                            collected_at=datetime.utcnow(),
                            metadata={
                                "call_number": cad.get("call_number"),
                                "incident_id": record.get("incident_id"),
                                "call_type": cad.get("call_type"),
                                "priority": cad.get("priority"),
                                "timestamp": cad.get("timestamp"),
                                "disposition": cad.get("disposition"),
                                "units_assigned": cad.get("units_assigned", []),
                            },
                            confidence=1.0,
                            is_verified=True,
                        )
                    )

            except Exception as e:
                logger.warning(f"Error gathering CAD history: {e}")

        return records

    async def gather_shotspotter_audio(self, incident_ids: list[str]) -> list[EvidenceItem]:
        """
        Gather ShotSpotter audio metadata for incidents.

        Args:
            incident_ids: List of incident IDs

        Returns:
            List of EvidenceItem objects for ShotSpotter audio metadata
        """
        logger.info(f"Gathering ShotSpotter audio for {len(incident_ids)} incidents")
        audio_items = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident)-[:HAS_GUNFIRE_ALERT]->(g:GunfireAlert)
                WHERE i.incident_id IN $incident_ids OR i.id IN $incident_ids
                RETURN g, i.incident_id as incident_id
                ORDER BY g.timestamp DESC
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_ids": incident_ids}
                )

                for record in result:
                    alert = dict(record["g"])
                    audio_items.append(
                        EvidenceItem(
                            evidence_id=alert.get("alert_id") or str(uuid.uuid4()),
                            evidence_type=EvidenceType.SHOTSPOTTER_AUDIO,
                            source="ShotSpotter",
                            title=f"Gunfire Alert - {alert.get('alert_id', 'Unknown')}",
                            description=f"Gunfire detected: {alert.get('round_count', 'Unknown')} rounds",
                            collected_at=datetime.utcnow(),
                            metadata={
                                "alert_id": alert.get("alert_id"),
                                "incident_id": record.get("incident_id"),
                                "timestamp": alert.get("timestamp"),
                                "latitude": alert.get("latitude"),
                                "longitude": alert.get("longitude"),
                                "round_count": alert.get("round_count"),
                                "confidence": alert.get("confidence"),
                                "audio_url": alert.get("audio_url"),
                                "sensor_ids": alert.get("sensor_ids", []),
                            },
                            confidence=alert.get("confidence", 0.9),
                            is_verified=False,
                        )
                    )

            except Exception as e:
                logger.warning(f"Error gathering ShotSpotter audio: {e}")

        return audio_items

    async def gather_lpr_hits(self, entity_ids: list[str]) -> list[EvidenceItem]:
        """
        Gather LPR hits for entities (vehicles/persons).

        Args:
            entity_ids: List of entity IDs

        Returns:
            List of EvidenceItem objects for LPR hits
        """
        logger.info(f"Gathering LPR hits for {len(entity_ids)} entities")
        lpr_items = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:OWNS|DRIVES|ASSOCIATED_WITH]-(v:Vehicle)-[:DETECTED_BY]-(lpr:LPRHit)
                WHERE e.entity_id IN $entity_ids OR e.id IN $entity_ids
                RETURN lpr, v.plate_number as plate, e.entity_id as entity_id
                ORDER BY lpr.timestamp DESC
                LIMIT 100
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_ids": entity_ids})

                for record in result:
                    hit = dict(record["lpr"])
                    lpr_items.append(
                        EvidenceItem(
                            evidence_id=hit.get("hit_id") or str(uuid.uuid4()),
                            evidence_type=EvidenceType.LPR_HIT,
                            source="LPR/Flock",
                            title=f"LPR Hit - {record.get('plate', 'Unknown')}",
                            description=f"Vehicle detected at {hit.get('location', 'Unknown location')}",
                            collected_at=datetime.utcnow(),
                            metadata={
                                "hit_id": hit.get("hit_id"),
                                "plate_number": record.get("plate"),
                                "entity_id": record.get("entity_id"),
                                "timestamp": hit.get("timestamp"),
                                "latitude": hit.get("latitude"),
                                "longitude": hit.get("longitude"),
                                "camera_id": hit.get("camera_id"),
                                "direction": hit.get("direction"),
                                "alert_type": hit.get("alert_type"),
                                "image_url": hit.get("image_url"),
                            },
                            confidence=0.95,
                            is_verified=True,
                        )
                    )

            except Exception as e:
                logger.warning(f"Error gathering LPR hits: {e}")

        return lpr_items

    async def gather_bwc_metadata(self, entity_ids: list[str]) -> list[EvidenceItem]:
        """
        Gather BWC metadata for entities.

        Args:
            entity_ids: List of entity IDs

        Returns:
            List of EvidenceItem objects for BWC metadata
        """
        logger.info(f"Gathering BWC metadata for {len(entity_ids)} entities")
        bwc_items = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:APPEARS_IN|INTERACTS_WITH]-(bwc:BWCRecording)
                WHERE e.entity_id IN $entity_ids OR e.id IN $entity_ids
                RETURN bwc, e.entity_id as entity_id
                ORDER BY bwc.timestamp DESC
                LIMIT 50
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_ids": entity_ids})

                for record in result:
                    bwc = dict(record["bwc"])
                    bwc_items.append(
                        EvidenceItem(
                            evidence_id=bwc.get("recording_id") or str(uuid.uuid4()),
                            evidence_type=EvidenceType.BWC_FOOTAGE,
                            source="BWC",
                            title=f"BWC Recording - {bwc.get('recording_id', 'Unknown')}",
                            description=f"Recording by Officer {bwc.get('officer_id', 'Unknown')}",
                            collected_at=datetime.utcnow(),
                            metadata={
                                "recording_id": bwc.get("recording_id"),
                                "entity_id": record.get("entity_id"),
                                "officer_id": bwc.get("officer_id"),
                                "timestamp": bwc.get("timestamp"),
                                "duration": bwc.get("duration"),
                                "incident_id": bwc.get("incident_id"),
                                "location": bwc.get("location"),
                                "tags": bwc.get("tags", []),
                                "video_url": bwc.get("video_url"),
                            },
                            confidence=1.0,
                            is_verified=True,
                        )
                    )

            except Exception as e:
                logger.warning(f"Error gathering BWC metadata: {e}")

        return bwc_items

    async def gather_ness_ballistics(self, incident_ids: list[str]) -> list[EvidenceItem]:
        """
        Gather NESS ballistics data for incidents.

        Args:
            incident_ids: List of incident IDs

        Returns:
            List of EvidenceItem objects for ballistics data
        """
        logger.info(f"Gathering NESS ballistics for {len(incident_ids)} incidents")
        ballistic_items = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (i:Incident)-[:HAS_EVIDENCE]->(b:BallisticEvidence)
                WHERE i.incident_id IN $incident_ids OR i.id IN $incident_ids
                OPTIONAL MATCH (b)-[:MATCHES]-(other_b:BallisticEvidence)
                RETURN b, i.incident_id as incident_id, collect(other_b.evidence_id) as matches
                """
                result = await self._neo4j_manager.execute_query(
                    query, {"incident_ids": incident_ids}
                )

                for record in result:
                    ballistic = dict(record["b"])
                    matches = record.get("matches", [])
                    ballistic_items.append(
                        EvidenceItem(
                            evidence_id=ballistic.get("evidence_id") or str(uuid.uuid4()),
                            evidence_type=EvidenceType.NESS_BALLISTICS,
                            source="NESS",
                            title=f"Ballistic Evidence - {ballistic.get('caliber', 'Unknown')} caliber",
                            description="Shell casing/projectile from incident",
                            collected_at=datetime.utcnow(),
                            metadata={
                                "evidence_id": ballistic.get("evidence_id"),
                                "incident_id": record.get("incident_id"),
                                "caliber": ballistic.get("caliber"),
                                "weapon_type": ballistic.get("weapon_type"),
                                "manufacturer": ballistic.get("manufacturer"),
                                "collection_date": ballistic.get("collection_date"),
                                "lab_case_number": ballistic.get("lab_case_number"),
                                "matches": matches,
                                "match_count": len(matches),
                            },
                            confidence=0.98,
                            is_verified=True,
                        )
                    )

            except Exception as e:
                logger.warning(f"Error gathering NESS ballistics: {e}")

        return ballistic_items

    async def gather_camera_snapshots(self, entity_ids: list[str]) -> list[EvidenceItem]:
        """
        Gather camera snapshot references for entities.

        Args:
            entity_ids: List of entity IDs

        Returns:
            List of EvidenceItem objects for camera snapshots (placeholder references)
        """
        logger.info(f"Gathering camera snapshots for {len(entity_ids)} entities")
        camera_items = []

        if self._neo4j_manager:
            try:
                query = """
                MATCH (e)-[:CAPTURED_BY|NEAR]-(c:Camera)
                WHERE e.entity_id IN $entity_ids OR e.id IN $entity_ids
                OPTIONAL MATCH (c)-[:HAS_SNAPSHOT]->(s:Snapshot)
                WHERE s.timestamp > datetime() - duration('P7D')
                RETURN c, e.entity_id as entity_id, collect(s)[0..5] as snapshots
                """
                result = await self._neo4j_manager.execute_query(query, {"entity_ids": entity_ids})

                for record in result:
                    camera = dict(record["c"])
                    snapshots = record.get("snapshots", [])

                    camera_items.append(
                        EvidenceItem(
                            evidence_id=camera.get("camera_id") or str(uuid.uuid4()),
                            evidence_type=EvidenceType.CAMERA_SNAPSHOT,
                            source="Milestone VMS",
                            title=f"Camera - {camera.get('name', camera.get('camera_id', 'Unknown'))}",
                            description=f"Camera at {camera.get('location', 'Unknown location')}",
                            collected_at=datetime.utcnow(),
                            metadata={
                                "camera_id": camera.get("camera_id"),
                                "entity_id": record.get("entity_id"),
                                "camera_name": camera.get("name"),
                                "location": camera.get("location"),
                                "latitude": camera.get("latitude"),
                                "longitude": camera.get("longitude"),
                                "snapshot_count": len(snapshots),
                                "snapshots": [dict(s) for s in snapshots if s],
                            },
                            confidence=0.85,
                            is_verified=False,
                        )
                    )

            except Exception as e:
                logger.warning(f"Error gathering camera snapshots: {e}")

        return camera_items


__all__ = [
    "EvidenceCollector",
]
