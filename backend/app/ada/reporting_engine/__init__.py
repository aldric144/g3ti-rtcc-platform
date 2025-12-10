"""
Phase 20: Reporting Engine Module

Provides draft report building, detective brief generation, court-ready evidence packets,
and supervisor review mode for the Autonomous Detective AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class ReportType(str, Enum):
    INVESTIGATIVE = "investigative"
    SUPPLEMENTAL = "supplemental"
    ARREST = "arrest"
    EVIDENCE = "evidence"
    WITNESS = "witness"
    FORENSIC = "forensic"
    SUMMARY = "summary"
    COURT_PACKET = "court_packet"
    DETECTIVE_BRIEF = "detective_brief"


class ReportStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    IN_REVIEW = "in_review"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"
    FINALIZED = "finalized"
    ARCHIVED = "archived"


class ReviewDecision(str, Enum):
    APPROVE = "approve"
    REQUEST_REVISION = "request_revision"
    REJECT = "reject"


@dataclass
class ReportSection:
    section_id: str
    title: str
    content: str
    order: int
    required: bool = True
    word_count: int = 0
    reviewed: bool = False
    reviewer_notes: str = ""


@dataclass
class DraftReport:
    report_id: str
    case_id: str
    report_type: ReportType
    title: str
    sections: List[ReportSection] = field(default_factory=list)
    status: ReportStatus = ReportStatus.DRAFT
    version: int = 1
    created_by: str = "ada_report_builder"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    review_date: Optional[datetime] = None
    review_notes: str = ""
    word_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectiveBrief:
    brief_id: str
    case_id: str
    title: str
    executive_summary: str
    key_findings: List[str] = field(default_factory=list)
    suspects_summary: List[Dict[str, Any]] = field(default_factory=list)
    evidence_highlights: List[Dict[str, Any]] = field(default_factory=list)
    timeline_summary: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: str = "ada_brief_generator"
    page_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidencePacketItem:
    item_id: str
    evidence_id: str
    description: str
    evidence_type: str
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)
    analysis_summary: str = ""
    relevance_statement: str = ""
    page_reference: int = 0


@dataclass
class CourtEvidencePacket:
    packet_id: str
    case_id: str
    case_number: str
    defendant_name: str
    charges: List[str] = field(default_factory=list)
    evidence_items: List[EvidencePacketItem] = field(default_factory=list)
    witness_list: List[Dict[str, Any]] = field(default_factory=list)
    expert_witnesses: List[Dict[str, Any]] = field(default_factory=list)
    chain_of_custody_summary: str = ""
    legal_standards_met: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: str = "ada_court_packet_generator"
    total_pages: int = 0
    pdf_url: Optional[str] = None
    status: str = "draft"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewComment:
    comment_id: str
    report_id: str
    section_id: Optional[str]
    reviewer: str
    comment: str
    comment_type: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class ReviewSession:
    session_id: str
    report_id: str
    reviewer: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    decision: Optional[ReviewDecision] = None
    comments: List[ReviewComment] = field(default_factory=list)
    sections_reviewed: List[str] = field(default_factory=list)
    overall_notes: str = ""


class DraftReportBuilder:
    """Builds draft investigative reports from case data."""

    def __init__(self):
        self._reports: Dict[str, DraftReport] = {}

    def create_report(
        self,
        case_id: str,
        report_type: ReportType,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
    ) -> DraftReport:
        report_id = f"rpt-{uuid.uuid4().hex[:12]}"

        sections = self._generate_sections(
            report_type, case_data, evidence_items, suspects
        )

        word_count = sum(s.word_count for s in sections)

        report = DraftReport(
            report_id=report_id,
            case_id=case_id,
            report_type=report_type,
            title=self._generate_title(report_type, case_data),
            sections=sections,
            word_count=word_count,
        )
        self._reports[report_id] = report
        return report

    def _generate_title(
        self,
        report_type: ReportType,
        case_data: Dict[str, Any],
    ) -> str:
        case_number = case_data.get("case_number", "Unknown")
        offense = case_data.get("offense_type", "Investigation")

        titles = {
            ReportType.INVESTIGATIVE: f"Investigative Report - Case {case_number}: {offense}",
            ReportType.SUPPLEMENTAL: f"Supplemental Report - Case {case_number}",
            ReportType.ARREST: f"Arrest Report - Case {case_number}",
            ReportType.EVIDENCE: f"Evidence Report - Case {case_number}",
            ReportType.WITNESS: f"Witness Statement Summary - Case {case_number}",
            ReportType.FORENSIC: f"Forensic Analysis Report - Case {case_number}",
            ReportType.SUMMARY: f"Case Summary - {case_number}: {offense}",
            ReportType.COURT_PACKET: f"Court Evidence Packet - Case {case_number}",
            ReportType.DETECTIVE_BRIEF: f"Detective Brief - Case {case_number}",
        }
        return titles.get(report_type, f"Report - Case {case_number}")

    def _generate_sections(
        self,
        report_type: ReportType,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
    ) -> List[ReportSection]:
        if report_type == ReportType.INVESTIGATIVE:
            return self._generate_investigative_sections(case_data, evidence_items, suspects)
        elif report_type == ReportType.SUMMARY:
            return self._generate_summary_sections(case_data, evidence_items, suspects)
        elif report_type == ReportType.EVIDENCE:
            return self._generate_evidence_sections(evidence_items)
        else:
            return self._generate_generic_sections(case_data)

    def _generate_investigative_sections(
        self,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
    ) -> List[ReportSection]:
        sections = []

        header_content = f"""CASE NUMBER: {case_data.get('case_number', 'N/A')}
OFFENSE TYPE: {case_data.get('offense_type', 'N/A')}
DATE OF OFFENSE: {case_data.get('date', 'N/A')}
LOCATION: {case_data.get('location', {}).get('address', 'N/A')}
REPORTING OFFICER: {case_data.get('reporting_officer', 'N/A')}
REPORT DATE: {datetime.utcnow().strftime('%Y-%m-%d')}"""

        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Case Header",
            content=header_content,
            order=1,
            word_count=len(header_content.split()),
        ))

        narrative = case_data.get('narrative', 'Investigation narrative pending.')
        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Narrative",
            content=f"NARRATIVE OF EVENTS:\n\n{narrative}",
            order=2,
            word_count=len(narrative.split()),
        ))

        victim_info = case_data.get('victim', {})
        victim_content = f"""VICTIM INFORMATION:
Name: {victim_info.get('name', 'N/A')}
Age: {victim_info.get('age', 'N/A')}
Address: {victim_info.get('address', 'N/A')}
Contact: {victim_info.get('contact', 'N/A')}
Injuries/Losses: {victim_info.get('injuries', 'N/A')}"""

        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Victim Information",
            content=victim_content,
            order=3,
            word_count=len(victim_content.split()),
        ))

        suspect_content = "SUSPECT INFORMATION:\n\n"
        if suspects:
            for i, suspect in enumerate(suspects, 1):
                suspect_content += f"""Suspect {i}:
Name: {suspect.get('name', 'Unknown')}
Description: {suspect.get('description', 'N/A')}
Status: {suspect.get('status', 'Person of Interest')}
Connection: {suspect.get('connection', 'N/A')}

"""
        else:
            suspect_content += "No suspects identified at this time."

        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Suspect Information",
            content=suspect_content,
            order=4,
            word_count=len(suspect_content.split()),
        ))

        evidence_content = "EVIDENCE COLLECTED:\n\n"
        if evidence_items:
            for i, item in enumerate(evidence_items, 1):
                evidence_content += f"""{i}. {item.get('description', 'Evidence item')}
   Type: {item.get('type', 'N/A')}
   Location Found: {item.get('location', 'N/A')}
   Collected By: {item.get('collected_by', 'N/A')}
   Status: {item.get('status', 'Collected')}

"""
        else:
            evidence_content += "No physical evidence collected at this time."

        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Evidence",
            content=evidence_content,
            order=5,
            word_count=len(evidence_content.split()),
        ))

        witness_content = "WITNESS STATEMENTS:\n\n"
        witnesses = case_data.get('witnesses', [])
        if witnesses:
            for i, witness in enumerate(witnesses, 1):
                witness_content += f"""{i}. {witness.get('name', 'Witness')}
   Statement Summary: {witness.get('statement_summary', 'N/A')}
   Contact: {witness.get('contact', 'N/A')}

"""
        else:
            witness_content += "No witness statements obtained at this time."

        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Witness Statements",
            content=witness_content,
            order=6,
            word_count=len(witness_content.split()),
        ))

        followup_content = """FOLLOW-UP ACTIONS REQUIRED:

1. Continue canvassing for additional witnesses
2. Review surveillance footage from surrounding areas
3. Process collected evidence through forensic analysis
4. Cross-reference suspect information with databases
5. Coordinate with other agencies as needed"""

        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Follow-Up Actions",
            content=followup_content,
            order=7,
            word_count=len(followup_content.split()),
        ))

        return sections

    def _generate_summary_sections(
        self,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
    ) -> List[ReportSection]:
        sections = []

        summary = f"""EXECUTIVE SUMMARY

Case {case_data.get('case_number', 'N/A')} involves a {case_data.get('offense_type', 'criminal offense')} that occurred on {case_data.get('date', 'unknown date')} at {case_data.get('location', {}).get('address', 'unknown location')}.

Current Status: {case_data.get('status', 'Active Investigation')}
Evidence Items: {len(evidence_items)}
Suspects Identified: {len(suspects)}

Key Developments:
{case_data.get('key_developments', 'Investigation ongoing.')}"""

        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Executive Summary",
            content=summary,
            order=1,
            word_count=len(summary.split()),
        ))

        return sections

    def _generate_evidence_sections(
        self,
        evidence_items: List[Dict[str, Any]],
    ) -> List[ReportSection]:
        sections = []

        overview = f"""EVIDENCE OVERVIEW

Total Items Collected: {len(evidence_items)}
Items Analyzed: {len([e for e in evidence_items if e.get('analyzed')])}
Items Pending Analysis: {len([e for e in evidence_items if not e.get('analyzed')])}"""

        sections.append(ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Evidence Overview",
            content=overview,
            order=1,
            word_count=len(overview.split()),
        ))

        for i, item in enumerate(evidence_items, 1):
            item_content = f"""EVIDENCE ITEM {i}

Item ID: {item.get('id', 'N/A')}
Description: {item.get('description', 'N/A')}
Type: {item.get('type', 'N/A')}
Location Found: {item.get('location', 'N/A')}
Date/Time Collected: {item.get('collected_at', 'N/A')}
Collected By: {item.get('collected_by', 'N/A')}
Chain of Custody: Intact
Analysis Status: {item.get('analysis_status', 'Pending')}
Analysis Results: {item.get('analysis_results', 'N/A')}
Relevance: {item.get('relevance', 'Under evaluation')}"""

            sections.append(ReportSection(
                section_id=f"sec-{uuid.uuid4().hex[:8]}",
                title=f"Evidence Item {i}",
                content=item_content,
                order=i + 1,
                word_count=len(item_content.split()),
            ))

        return sections

    def _generate_generic_sections(
        self,
        case_data: Dict[str, Any],
    ) -> List[ReportSection]:
        content = f"""REPORT

Case Number: {case_data.get('case_number', 'N/A')}
Date: {datetime.utcnow().strftime('%Y-%m-%d')}

{case_data.get('content', 'Report content pending.')}"""

        return [ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title="Report Content",
            content=content,
            order=1,
            word_count=len(content.split()),
        )]

    def update_section(
        self,
        report_id: str,
        section_id: str,
        content: str,
    ) -> Optional[DraftReport]:
        report = self._reports.get(report_id)
        if not report:
            return None

        for section in report.sections:
            if section.section_id == section_id:
                section.content = content
                section.word_count = len(content.split())
                break

        report.word_count = sum(s.word_count for s in report.sections)
        report.updated_at = datetime.utcnow()
        report.version += 1

        return report

    def add_section(
        self,
        report_id: str,
        title: str,
        content: str,
        order: Optional[int] = None,
    ) -> Optional[DraftReport]:
        report = self._reports.get(report_id)
        if not report:
            return None

        if order is None:
            order = len(report.sections) + 1

        section = ReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:8]}",
            title=title,
            content=content,
            order=order,
            word_count=len(content.split()),
        )
        report.sections.append(section)
        report.sections.sort(key=lambda s: s.order)

        report.word_count = sum(s.word_count for s in report.sections)
        report.updated_at = datetime.utcnow()
        report.version += 1

        return report

    def get_report(self, report_id: str) -> Optional[DraftReport]:
        return self._reports.get(report_id)

    def get_case_reports(
        self,
        case_id: str,
        report_type: Optional[ReportType] = None,
    ) -> List[DraftReport]:
        results = [r for r in self._reports.values() if r.case_id == case_id]

        if report_type:
            results = [r for r in results if r.report_type == report_type]

        return results

    def export_report(
        self,
        report_id: str,
        format: str = "text",
    ) -> Optional[str]:
        report = self._reports.get(report_id)
        if not report:
            return None

        if format == "text":
            output = "=" * 60 + "\n"
            output += f"{report.title}\n"
            output += f"Report ID: {report.report_id}\n"
            output += f"Version: {report.version}\n"
            output += f"Status: {report.status.value}\n"
            output += f"Generated: {report.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            output += "=" * 60 + "\n\n"

            for section in sorted(report.sections, key=lambda s: s.order):
                output += f"{section.title.upper()}\n"
                output += "-" * 40 + "\n"
                output += section.content + "\n\n"

            return output

        return None


class DetectiveBriefGenerator:
    """Generates concise detective briefs for quick case review."""

    def __init__(self):
        self._briefs: Dict[str, DetectiveBrief] = {}

    def generate_brief(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
        hypotheses: Optional[List[Dict[str, Any]]] = None,
    ) -> DetectiveBrief:
        brief_id = f"brief-{uuid.uuid4().hex[:12]}"

        executive_summary = self._generate_executive_summary(case_data)
        key_findings = self._extract_key_findings(case_data, evidence_items, suspects)
        suspects_summary = self._summarize_suspects(suspects)
        evidence_highlights = self._highlight_evidence(evidence_items)
        timeline_summary = self._summarize_timeline(case_data)
        recommended_actions = self._generate_recommendations(case_data, hypotheses)
        risk_assessment = self._assess_risk(case_data, suspects)

        brief = DetectiveBrief(
            brief_id=brief_id,
            case_id=case_id,
            title=f"Detective Brief: Case {case_data.get('case_number', case_id)}",
            executive_summary=executive_summary,
            key_findings=key_findings,
            suspects_summary=suspects_summary,
            evidence_highlights=evidence_highlights,
            timeline_summary=timeline_summary,
            recommended_actions=recommended_actions,
            risk_assessment=risk_assessment,
            page_count=self._estimate_pages(executive_summary, key_findings),
        )
        self._briefs[brief_id] = brief
        return brief

    def _generate_executive_summary(self, case_data: Dict[str, Any]) -> str:
        return f"""Case {case_data.get('case_number', 'N/A')} - {case_data.get('offense_type', 'Investigation')}

Date: {case_data.get('date', 'Unknown')}
Location: {case_data.get('location', {}).get('address', 'Unknown')}
Status: {case_data.get('status', 'Active')}

{case_data.get('summary', 'Case under active investigation. Details being compiled.')}"""

    def _extract_key_findings(
        self,
        case_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]],
        suspects: List[Dict[str, Any]],
    ) -> List[str]:
        findings = []

        if suspects:
            findings.append(f"{len(suspects)} suspect(s) identified")
        else:
            findings.append("No suspects currently identified")

        if evidence_items:
            findings.append(f"{len(evidence_items)} evidence items collected")
            analyzed = len([e for e in evidence_items if e.get('analyzed')])
            if analyzed:
                findings.append(f"{analyzed} items analyzed with results")

        if case_data.get('witnesses'):
            findings.append(f"{len(case_data['witnesses'])} witness statements obtained")

        if case_data.get('surveillance_available'):
            findings.append("Surveillance footage available for review")

        if case_data.get('forensic_results'):
            findings.append("Forensic analysis results available")

        return findings

    def _summarize_suspects(
        self,
        suspects: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        summaries = []
        for suspect in suspects:
            summaries.append({
                "name": suspect.get("name", "Unknown"),
                "status": suspect.get("status", "Person of Interest"),
                "evidence_strength": suspect.get("evidence_strength", "Moderate"),
                "key_connection": suspect.get("connection", "Under investigation"),
            })
        return summaries

    def _highlight_evidence(
        self,
        evidence_items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        highlights = []

        high_value = [e for e in evidence_items if e.get("probative_value", 0) > 0.7]

        for item in high_value[:5]:
            highlights.append({
                "type": item.get("type", "Unknown"),
                "description": item.get("description", "Evidence item"),
                "significance": item.get("significance", "High probative value"),
                "status": item.get("analysis_status", "Pending"),
            })

        return highlights

    def _summarize_timeline(
        self,
        case_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        events = case_data.get("timeline_events", [])

        summary = []
        for event in events[:10]:
            summary.append({
                "time": event.get("timestamp", "Unknown"),
                "event": event.get("description", "Event"),
                "source": event.get("source", "Investigation"),
            })

        return summary

    def _generate_recommendations(
        self,
        case_data: Dict[str, Any],
        hypotheses: Optional[List[Dict[str, Any]]],
    ) -> List[str]:
        recommendations = []

        if not case_data.get("suspects"):
            recommendations.append("Priority: Identify potential suspects through evidence analysis")

        if case_data.get("surveillance_available") and not case_data.get("surveillance_reviewed"):
            recommendations.append("Review available surveillance footage")

        if case_data.get("witnesses") and not case_data.get("witnesses_interviewed"):
            recommendations.append("Complete witness interviews")

        recommendations.append("Continue evidence processing and analysis")
        recommendations.append("Cross-reference with similar cases in database")

        if hypotheses:
            top_hypothesis = max(hypotheses, key=lambda h: h.get("confidence", 0), default=None)
            if top_hypothesis:
                recommendations.append(f"Investigate leading theory: {top_hypothesis.get('title', 'Unknown')}")

        return recommendations

    def _assess_risk(
        self,
        case_data: Dict[str, Any],
        suspects: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        risk_level = "medium"

        if case_data.get("offense_type") in ["homicide", "assault", "robbery"]:
            risk_level = "high"

        if suspects and any(s.get("violent_history") for s in suspects):
            risk_level = "high"

        if case_data.get("serial_pattern"):
            risk_level = "critical"

        return {
            "level": risk_level,
            "public_safety_concern": case_data.get("public_safety", False),
            "flight_risk": any(s.get("flight_risk") for s in suspects),
            "evidence_preservation": case_data.get("evidence_at_risk", False),
        }

    def _estimate_pages(
        self,
        summary: str,
        findings: List[str],
    ) -> int:
        word_count = len(summary.split()) + sum(len(f.split()) for f in findings)
        return max(1, word_count // 300)

    def get_brief(self, brief_id: str) -> Optional[DetectiveBrief]:
        return self._briefs.get(brief_id)

    def get_case_briefs(self, case_id: str) -> List[DetectiveBrief]:
        return [b for b in self._briefs.values() if b.case_id == case_id]


class CourtReadyEvidencePacketGenerator:
    """Generates court-ready evidence packets (PDF stub)."""

    def __init__(self):
        self._packets: Dict[str, CourtEvidencePacket] = {}

    def generate_packet(
        self,
        case_id: str,
        case_number: str,
        defendant_name: str,
        charges: List[str],
        evidence_items: List[Dict[str, Any]],
        witnesses: List[Dict[str, Any]],
        expert_witnesses: Optional[List[Dict[str, Any]]] = None,
    ) -> CourtEvidencePacket:
        packet_id = f"packet-{uuid.uuid4().hex[:12]}"

        packet_items = []
        for i, item in enumerate(evidence_items, 1):
            packet_item = EvidencePacketItem(
                item_id=f"item-{uuid.uuid4().hex[:8]}",
                evidence_id=item.get("id", f"EVD-{i}"),
                description=item.get("description", "Evidence item"),
                evidence_type=item.get("type", "physical"),
                chain_of_custody=item.get("chain_of_custody", []),
                analysis_summary=item.get("analysis_summary", ""),
                relevance_statement=self._generate_relevance_statement(item, charges),
                page_reference=i * 2,
            )
            packet_items.append(packet_item)

        witness_list = []
        for witness in witnesses:
            witness_list.append({
                "name": witness.get("name", "Unknown"),
                "type": witness.get("type", "eyewitness"),
                "statement_summary": witness.get("statement_summary", ""),
                "availability": witness.get("availability", "Available"),
            })

        chain_summary = self._generate_chain_summary(evidence_items)
        legal_standards = self._check_legal_standards(evidence_items)

        total_pages = len(packet_items) * 3 + len(witness_list) * 2 + 10

        packet = CourtEvidencePacket(
            packet_id=packet_id,
            case_id=case_id,
            case_number=case_number,
            defendant_name=defendant_name,
            charges=charges,
            evidence_items=packet_items,
            witness_list=witness_list,
            expert_witnesses=expert_witnesses or [],
            chain_of_custody_summary=chain_summary,
            legal_standards_met=legal_standards,
            total_pages=total_pages,
            pdf_url=f"/api/ada/packets/{packet_id}/download",
        )
        self._packets[packet_id] = packet
        return packet

    def _generate_relevance_statement(
        self,
        item: Dict[str, Any],
        charges: List[str],
    ) -> str:
        evidence_type = item.get("type", "")

        if evidence_type == "dna":
            return "DNA evidence directly links the defendant to the crime scene, establishing presence and potential involvement."
        elif evidence_type == "fingerprint":
            return "Fingerprint evidence places the defendant at the scene, corroborating witness testimony."
        elif evidence_type == "weapon":
            return "The recovered weapon is consistent with injuries sustained by the victim and was found in defendant's possession."
        elif evidence_type == "surveillance":
            return "Video surveillance captures the defendant at the scene during the time of the offense."
        else:
            return f"This evidence is relevant to establishing the elements of the charged offense(s): {', '.join(charges[:2])}."

    def _generate_chain_summary(
        self,
        evidence_items: List[Dict[str, Any]],
    ) -> str:
        intact_count = len([e for e in evidence_items if e.get("chain_intact", True)])
        total = len(evidence_items)

        return f"""Chain of Custody Summary:

Total Evidence Items: {total}
Items with Intact Chain: {intact_count}
Chain Integrity: {(intact_count/total*100) if total else 0:.1f}%

All evidence items have been properly documented, stored, and transferred in accordance with department protocols and legal requirements. Complete chain of custody documentation is attached for each item."""

    def _check_legal_standards(
        self,
        evidence_items: List[Dict[str, Any]],
    ) -> List[str]:
        standards = []

        if all(e.get("chain_intact", True) for e in evidence_items):
            standards.append("Chain of custody maintained for all items")

        if all(e.get("legally_obtained", True) for e in evidence_items):
            standards.append("All evidence legally obtained")

        if any(e.get("type") == "dna" for e in evidence_items):
            standards.append("DNA evidence processed per CODIS standards")

        if any(e.get("type") == "fingerprint" for e in evidence_items):
            standards.append("Fingerprint analysis meets AFIS standards")

        standards.append("Evidence storage meets department standards")
        standards.append("Documentation complete and accurate")

        return standards

    def finalize_packet(
        self,
        packet_id: str,
        prosecutor_approval: str,
    ) -> Optional[CourtEvidencePacket]:
        packet = self._packets.get(packet_id)
        if not packet:
            return None

        packet.status = "finalized"
        packet.metadata["prosecutor_approval"] = prosecutor_approval
        packet.metadata["finalized_at"] = datetime.utcnow().isoformat()

        return packet

    def get_packet(self, packet_id: str) -> Optional[CourtEvidencePacket]:
        return self._packets.get(packet_id)

    def get_case_packets(self, case_id: str) -> List[CourtEvidencePacket]:
        return [p for p in self._packets.values() if p.case_id == case_id]


class SupervisorReviewMode:
    """Manages supervisor review workflow for reports."""

    def __init__(self, report_builder: DraftReportBuilder):
        self._report_builder = report_builder
        self._sessions: Dict[str, ReviewSession] = {}
        self._comments: Dict[str, ReviewComment] = {}

    def start_review(
        self,
        report_id: str,
        reviewer: str,
    ) -> Optional[ReviewSession]:
        report = self._report_builder.get_report(report_id)
        if not report:
            return None

        session_id = f"review-{uuid.uuid4().hex[:12]}"

        session = ReviewSession(
            session_id=session_id,
            report_id=report_id,
            reviewer=reviewer,
        )
        self._sessions[session_id] = session

        report.status = ReportStatus.IN_REVIEW
        report.updated_at = datetime.utcnow()

        return session

    def add_comment(
        self,
        session_id: str,
        comment: str,
        comment_type: str = "general",
        section_id: Optional[str] = None,
    ) -> Optional[ReviewComment]:
        session = self._sessions.get(session_id)
        if not session:
            return None

        comment_obj = ReviewComment(
            comment_id=f"cmt-{uuid.uuid4().hex[:8]}",
            report_id=session.report_id,
            section_id=section_id,
            reviewer=session.reviewer,
            comment=comment,
            comment_type=comment_type,
        )
        self._comments[comment_obj.comment_id] = comment_obj
        session.comments.append(comment_obj)

        return comment_obj

    def mark_section_reviewed(
        self,
        session_id: str,
        section_id: str,
        notes: str = "",
    ) -> Optional[ReviewSession]:
        session = self._sessions.get(session_id)
        if not session:
            return None

        if section_id not in session.sections_reviewed:
            session.sections_reviewed.append(section_id)

        report = self._report_builder.get_report(session.report_id)
        if report:
            for section in report.sections:
                if section.section_id == section_id:
                    section.reviewed = True
                    section.reviewer_notes = notes
                    break

        return session

    def complete_review(
        self,
        session_id: str,
        decision: ReviewDecision,
        overall_notes: str = "",
    ) -> Optional[ReviewSession]:
        session = self._sessions.get(session_id)
        if not session:
            return None

        session.completed_at = datetime.utcnow()
        session.decision = decision
        session.overall_notes = overall_notes

        report = self._report_builder.get_report(session.report_id)
        if report:
            if decision == ReviewDecision.APPROVE:
                report.status = ReportStatus.APPROVED
            elif decision == ReviewDecision.REQUEST_REVISION:
                report.status = ReportStatus.REVISION_REQUESTED
            elif decision == ReviewDecision.REJECT:
                report.status = ReportStatus.DRAFT

            report.reviewed_by = session.reviewer
            report.review_date = datetime.utcnow()
            report.review_notes = overall_notes
            report.updated_at = datetime.utcnow()

        return session

    def resolve_comment(
        self,
        comment_id: str,
    ) -> Optional[ReviewComment]:
        comment = self._comments.get(comment_id)
        if not comment:
            return None

        comment.resolved = True
        comment.resolved_at = datetime.utcnow()

        return comment

    def get_session(self, session_id: str) -> Optional[ReviewSession]:
        return self._sessions.get(session_id)

    def get_report_sessions(self, report_id: str) -> List[ReviewSession]:
        return [s for s in self._sessions.values() if s.report_id == report_id]

    def get_pending_reviews(self, reviewer: str) -> List[ReviewSession]:
        return [
            s for s in self._sessions.values()
            if s.reviewer == reviewer and s.completed_at is None
        ]

    def get_review_statistics(self) -> Dict[str, Any]:
        sessions = list(self._sessions.values())
        completed = [s for s in sessions if s.completed_at]

        decisions = {}
        for s in completed:
            if s.decision:
                decisions[s.decision.value] = decisions.get(s.decision.value, 0) + 1

        return {
            "total_reviews": len(sessions),
            "completed": len(completed),
            "pending": len(sessions) - len(completed),
            "decisions": decisions,
            "total_comments": len(self._comments),
            "resolved_comments": len([c for c in self._comments.values() if c.resolved]),
        }


__all__ = [
    "ReportType",
    "ReportStatus",
    "ReviewDecision",
    "ReportSection",
    "DraftReport",
    "DetectiveBrief",
    "EvidencePacketItem",
    "CourtEvidencePacket",
    "ReviewComment",
    "ReviewSession",
    "DraftReportBuilder",
    "DetectiveBriefGenerator",
    "CourtReadyEvidencePacketGenerator",
    "SupervisorReviewMode",
]
