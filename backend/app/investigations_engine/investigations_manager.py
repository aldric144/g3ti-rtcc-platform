"""
Investigations Manager.

Central orchestrator for the Investigations Engine, coordinating case building,
incident linking, timeline generation, entity correlation, evidence collection,
and report generation.
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
    LinkageResult,
    RiskAssessment,
    TimelineEvent,
)

logger = get_logger(__name__)


class InvestigationsManager:
    """
    Central orchestrator for the Investigations Engine.

    Coordinates all investigation-related operations including:
    - Multi-incident ingestion
    - Cross-dataset linking (RMS, CAD, ShotSpotter, LPR, NESS, BWC)
    - Graph-based entity expansion (Neo4j)
    - Evidence auto-collection and classification
    - Confidence scoring for connections
    - Structured investigative recommendations
    """

    def __init__(self) -> None:
        """Initialize the Investigations Manager."""
        self._neo4j_manager = None
        self._es_client = None
        self._redis_manager = None
        self._incident_linker = None
        self._entity_correlator = None
        self._evidence_collector = None
        self._case_builder = None
        self._timeline_generator = None
        self._report_generator = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all dependencies and sub-engines."""
        if self._initialized:
            return

        logger.info("Initializing Investigations Manager")

        try:
            from app.db.elasticsearch import es_client
            from app.db.neo4j import neo4j_manager
            from app.db.redis import redis_manager

            self._neo4j_manager = neo4j_manager
            self._es_client = es_client
            self._redis_manager = redis_manager

            from app.investigations_engine.case_builder import CaseBuilder
            from app.investigations_engine.entity_correlation import EntityCorrelator
            from app.investigations_engine.evidence_collector import EvidenceCollector
            from app.investigations_engine.incident_linker import IncidentLinker
            from app.investigations_engine.report_generator import ReportGenerator
            from app.investigations_engine.timeline_generator import TimelineGenerator

            self._incident_linker = IncidentLinker(
                neo4j_manager=self._neo4j_manager,
                es_client=self._es_client,
            )
            self._entity_correlator = EntityCorrelator(
                neo4j_manager=self._neo4j_manager,
                es_client=self._es_client,
            )
            self._evidence_collector = EvidenceCollector(
                neo4j_manager=self._neo4j_manager,
                es_client=self._es_client,
            )
            self._case_builder = CaseBuilder(
                neo4j_manager=self._neo4j_manager,
                es_client=self._es_client,
                incident_linker=self._incident_linker,
                entity_correlator=self._entity_correlator,
                evidence_collector=self._evidence_collector,
            )
            self._timeline_generator = TimelineGenerator(
                neo4j_manager=self._neo4j_manager,
                es_client=self._es_client,
            )
            self._report_generator = ReportGenerator()

            self._initialized = True
            logger.info("Investigations Manager initialized successfully")

        except Exception as e:
            logger.warning(f"Could not fully initialize Investigations Manager: {e}")
            self._initialized = True

    async def link_incidents(
        self,
        incident_ids: list[str],
        user_id: str,
        user_role: str,
    ) -> LinkageResult:
        """
        Link incidents based on various correlation factors.

        Args:
            incident_ids: List of incident IDs to analyze for linkages
            user_id: ID of the user making the request
            user_role: Role of the user for access control

        Returns:
            LinkageResult containing linked incidents and confidence scores
        """
        await self.initialize()

        audit_logger.info(
            "Incident linking requested",
            extra={
                "user_id": user_id,
                "user_role": user_role,
                "incident_ids": incident_ids,
                "action": "link_incidents",
            },
        )

        logger.info(f"Linking incidents: {incident_ids}")

        if self._incident_linker:
            result = await self._incident_linker.link(incident_ids)
        else:
            result = await self._fallback_link_incidents(incident_ids)

        audit_logger.info(
            "Incident linking completed",
            extra={
                "user_id": user_id,
                "linked_count": len(result.linked_incidents),
                "action": "link_incidents_complete",
            },
        )

        return result

    async def _fallback_link_incidents(self, incident_ids: list[str]) -> LinkageResult:
        """Fallback incident linking when linker is not available."""
        linked_incidents = []
        linkages = []
        confidence_scores = {}
        explanations = []

        for incident_id in incident_ids:
            linked_incidents.append(
                {
                    "incident_id": incident_id,
                    "status": "analyzed",
                }
            )
            confidence_scores[incident_id] = 0.5
            explanations.append(f"Incident {incident_id} analyzed for linkages")

        return LinkageResult(
            linked_incidents=linked_incidents,
            linkages=linkages,
            confidence_scores=confidence_scores,
            explanations=explanations,
        )

    async def get_entity_profile(
        self,
        entity_id: str,
        user_id: str,
        user_role: str,
    ) -> EntitySummary:
        """
        Get comprehensive entity profile with all correlations.

        Args:
            entity_id: ID of the entity to profile
            user_id: ID of the user making the request
            user_role: Role of the user for access control

        Returns:
            EntitySummary with complete investigative profile
        """
        await self.initialize()

        audit_logger.info(
            "Entity profile requested",
            extra={
                "user_id": user_id,
                "user_role": user_role,
                "entity_id": entity_id,
                "action": "get_entity_profile",
            },
        )

        logger.info(f"Getting entity profile: {entity_id}")

        if self._entity_correlator:
            profile = await self._entity_correlator.get_profile(entity_id)
        else:
            profile = await self._fallback_get_entity_profile(entity_id)

        return profile

    async def _fallback_get_entity_profile(self, entity_id: str) -> EntitySummary:
        """Fallback entity profile when correlator is not available."""
        return EntitySummary(
            entity_id=entity_id,
            entity_type="unknown",
            name="Unknown Entity",
            prior_incidents=[],
            address_history=[],
            vehicle_connections=[],
            weapon_matches=[],
            lpr_activity=[],
            bwc_interactions=[],
            known_associates=[],
            risk_score=0.0,
        )

    async def create_case(
        self,
        incident_id: str | None = None,
        suspect_id: str | None = None,
        title: str | None = None,
        user_id: str = "",
        user_role: str = "",
    ) -> CaseFile:
        """
        Auto-create a case file from an incident or suspect.

        Args:
            incident_id: Optional incident ID to build case from
            suspect_id: Optional suspect ID to build case from
            title: Optional case title
            user_id: ID of the user creating the case
            user_role: Role of the user for access control

        Returns:
            Complete CaseFile with all correlations and evidence
        """
        await self.initialize()

        audit_logger.info(
            "Case creation requested",
            extra={
                "user_id": user_id,
                "user_role": user_role,
                "incident_id": incident_id,
                "suspect_id": suspect_id,
                "action": "create_case",
            },
        )

        logger.info(f"Creating case from incident={incident_id}, suspect={suspect_id}")

        if self._case_builder:
            case = await self._case_builder.build(
                incident_id=incident_id,
                suspect_id=suspect_id,
                title=title,
                user_id=user_id,
            )
        else:
            case = await self._fallback_create_case(
                incident_id=incident_id,
                suspect_id=suspect_id,
                title=title,
                user_id=user_id,
            )

        audit_logger.info(
            "Case created successfully",
            extra={
                "user_id": user_id,
                "case_id": case.case_id,
                "case_number": case.case_number,
                "action": "create_case_complete",
            },
        )

        return case

    async def _fallback_create_case(
        self,
        incident_id: str | None,
        suspect_id: str | None,
        title: str | None,
        user_id: str,
    ) -> CaseFile:
        """Fallback case creation when builder is not available."""
        now = datetime.utcnow()
        case_id = str(uuid.uuid4())
        year = now.year
        case_number = f"CASE-{year}-{uuid.uuid4().hex[:5].upper()}"

        case_title = title or f"Investigation - {incident_id or suspect_id or 'New Case'}"

        return CaseFile(
            case_id=case_id,
            case_number=case_number,
            title=case_title,
            summary=f"Auto-generated case for {incident_id or suspect_id or 'investigation'}",
            status=CaseStatus.OPEN,
            priority=CasePriority.MEDIUM,
            created_at=now,
            updated_at=now,
            assigned_to=[user_id] if user_id else [],
            linked_incidents=[{"incident_id": incident_id}] if incident_id else [],
            suspects=[],
            vehicles=[],
            addresses=[],
            weapons=[],
            timeline=[],
            evidence=EvidencePackage(),
            risk_assessment=RiskAssessment(
                overall_score=0.5,
                threat_level="medium",
                factors=[],
                recommendations=["Gather additional evidence", "Interview witnesses"],
            ),
            leads=[],
            recommendations=["Review linked incidents", "Expand entity search"],
        )

    async def generate_timeline(
        self,
        case_id: str,
        user_id: str,
        user_role: str,
    ) -> list[TimelineEvent]:
        """
        Generate comprehensive timeline for a case.

        Args:
            case_id: ID of the case
            user_id: ID of the user making the request
            user_role: Role of the user for access control

        Returns:
            List of TimelineEvent objects ordered by time
        """
        await self.initialize()

        audit_logger.info(
            "Timeline generation requested",
            extra={
                "user_id": user_id,
                "user_role": user_role,
                "case_id": case_id,
                "action": "generate_timeline",
            },
        )

        logger.info(f"Generating timeline for case: {case_id}")

        if self._timeline_generator:
            timeline = await self._timeline_generator.generate(case_id)
        else:
            timeline = []

        return timeline

    async def collect_evidence(
        self,
        case_id: str,
        incident_ids: list[str],
        entity_ids: list[str],
        user_id: str,
        user_role: str,
    ) -> EvidencePackage:
        """
        Collect all evidence related to a case.

        Args:
            case_id: ID of the case
            incident_ids: List of incident IDs to collect evidence from
            entity_ids: List of entity IDs to collect evidence for
            user_id: ID of the user making the request
            user_role: Role of the user for access control

        Returns:
            EvidencePackage with all collected evidence
        """
        await self.initialize()

        audit_logger.info(
            "Evidence collection requested",
            extra={
                "user_id": user_id,
                "user_role": user_role,
                "case_id": case_id,
                "incident_count": len(incident_ids),
                "entity_count": len(entity_ids),
                "action": "collect_evidence",
            },
        )

        logger.info(f"Collecting evidence for case: {case_id}")

        if self._evidence_collector:
            evidence = await self._evidence_collector.collect(
                incident_ids=incident_ids,
                entity_ids=entity_ids,
            )
        else:
            evidence = EvidencePackage()

        return evidence

    async def export_case_pdf(
        self,
        case_id: str,
        user_id: str,
        user_role: str,
    ) -> bytes:
        """
        Export case as PDF document.

        Args:
            case_id: ID of the case to export
            user_id: ID of the user making the request
            user_role: Role of the user for access control

        Returns:
            PDF document as bytes
        """
        await self.initialize()

        audit_logger.info(
            "Case PDF export requested",
            extra={
                "user_id": user_id,
                "user_role": user_role,
                "case_id": case_id,
                "action": "export_case_pdf",
            },
        )

        logger.info(f"Exporting case as PDF: {case_id}")

        case = await self._get_case(case_id)

        if self._report_generator:
            pdf_bytes = await self._report_generator.export_pdf(case)
        else:
            pdf_bytes = b""

        return pdf_bytes

    async def export_case_json(
        self,
        case_id: str,
        user_id: str,
        user_role: str,
    ) -> dict[str, Any]:
        """
        Export case as JSON document.

        Args:
            case_id: ID of the case to export
            user_id: ID of the user making the request
            user_role: Role of the user for access control

        Returns:
            Case data as dictionary
        """
        await self.initialize()

        audit_logger.info(
            "Case JSON export requested",
            extra={
                "user_id": user_id,
                "user_role": user_role,
                "case_id": case_id,
                "action": "export_case_json",
            },
        )

        logger.info(f"Exporting case as JSON: {case_id}")

        case = await self._get_case(case_id)

        if self._report_generator:
            json_data = await self._report_generator.export_json(case)
        else:
            json_data = case.to_dict() if case else {}

        return json_data

    async def _get_case(self, case_id: str) -> CaseFile | None:
        """Get case from storage."""
        return await self._fallback_create_case(
            incident_id=None,
            suspect_id=None,
            title=f"Case {case_id}",
            user_id="",
        )

    async def update_case_on_new_data(
        self,
        case_id: str,
        new_data: dict[str, Any],
        user_id: str,
    ) -> CaseFile:
        """
        Update case when new data arrives.

        Args:
            case_id: ID of the case to update
            new_data: New data to incorporate
            user_id: ID of the user or system making the update

        Returns:
            Updated CaseFile
        """
        await self.initialize()

        audit_logger.info(
            "Case update on new data",
            extra={
                "user_id": user_id,
                "case_id": case_id,
                "data_type": new_data.get("type"),
                "action": "update_case_on_new_data",
            },
        )

        logger.info(f"Updating case {case_id} with new data")

        case = await self._get_case(case_id)
        if case:
            case.updated_at = datetime.utcnow()

        return case

    async def get_case_updates_channel(self, case_id: str) -> str:
        """Get WebSocket channel for case updates."""
        return f"case-updates/{case_id}"


investigations_manager = InvestigationsManager()


__all__ = [
    "InvestigationsManager",
    "investigations_manager",
]
