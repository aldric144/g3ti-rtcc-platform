"""
Case Report Exporter.

This module provides functionality for exporting investigation cases
to various formats including PDF and JSON.
"""

import importlib.util
import io
from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.investigations_engine.models import CaseFile

logger = get_logger(__name__)


class ReportGenerator:
    """
    Engine for generating case reports in various formats.

    Exports:
    - Full case summary
    - Key evidence
    - Incident chain
    - Entity profile cards
    - Maps (placeholder images)
    - Timeline
    - Recommendations
    """

    def __init__(self) -> None:
        """Initialize the Report Generator."""
        self._pdf_available = importlib.util.find_spec("reportlab") is not None
        if not self._pdf_available:
            logger.warning("reportlab not available, PDF export will be limited")

    async def export_pdf(self, case: CaseFile) -> bytes:
        """
        Export case as PDF document.

        Args:
            case: CaseFile to export

        Returns:
            PDF document as bytes
        """
        logger.info(f"Exporting case {case.case_id} as PDF")

        if self._pdf_available:
            return await self._generate_pdf_reportlab(case)
        else:
            return await self._generate_pdf_simple(case)

    async def export_json(self, case: CaseFile) -> dict[str, Any]:
        """
        Export case as JSON document.

        Args:
            case: CaseFile to export

        Returns:
            Case data as dictionary
        """
        logger.info(f"Exporting case {case.case_id} as JSON")

        export_data = {
            "export_metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "format_version": "1.0",
                "case_id": case.case_id,
                "case_number": case.case_number,
            },
            "case": case.to_dict(),
        }

        return export_data

    async def _generate_pdf_reportlab(self, case: CaseFile) -> bytes:
        """Generate PDF using reportlab library."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=12,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
        )
        normal_style = styles["Normal"]

        story = []

        story.append(Paragraph("INVESTIGATION CASE REPORT", title_style))
        story.append(Spacer(1, 12))

        case_info = [
            ["Case Number:", case.case_number],
            ["Case ID:", case.case_id],
            ["Title:", case.title],
            ["Status:", case.status.value.upper()],
            ["Priority:", case.priority.value.upper()],
            ["Created:", case.created_at.strftime("%Y-%m-%d %H:%M:%S")],
            ["Updated:", case.updated_at.strftime("%Y-%m-%d %H:%M:%S")],
        ]
        case_table = Table(case_info, colWidths=[1.5 * inch, 4.5 * inch])
        case_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(case_table)
        story.append(Spacer(1, 20))

        story.append(Paragraph("CASE SUMMARY", heading_style))
        story.append(Paragraph(case.summary or "No summary available.", normal_style))
        story.append(Spacer(1, 12))

        if case.risk_assessment:
            story.append(Paragraph("RISK ASSESSMENT", heading_style))
            risk_info = [
                ["Overall Score:", f"{case.risk_assessment.overall_score:.2f}"],
                ["Threat Level:", case.risk_assessment.threat_level.upper()],
            ]
            risk_table = Table(risk_info, colWidths=[1.5 * inch, 4.5 * inch])
            risk_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(risk_table)
            story.append(Spacer(1, 12))

        if case.suspects:
            story.append(Paragraph("SUSPECTS", heading_style))
            for i, suspect in enumerate(case.suspects, 1):
                story.append(
                    Paragraph(f"{i}. {suspect.name} (ID: {suspect.entity_id})", normal_style)
                )
                if suspect.prior_incidents:
                    story.append(
                        Paragraph(
                            f"   Prior Incidents: {len(suspect.prior_incidents)}", normal_style
                        )
                    )
                if suspect.risk_score > 0:
                    story.append(
                        Paragraph(f"   Risk Score: {suspect.risk_score:.2f}", normal_style)
                    )
            story.append(Spacer(1, 12))

        if case.vehicles:
            story.append(Paragraph("VEHICLES OF INTEREST", heading_style))
            for i, vehicle in enumerate(case.vehicles, 1):
                metadata = vehicle.metadata or {}
                desc = f"{metadata.get('year', '')} {metadata.get('make', '')} {metadata.get('model', '')}".strip()
                story.append(Paragraph(f"{i}. {vehicle.name} - {desc or 'Unknown'}", normal_style))
            story.append(Spacer(1, 12))

        if case.linked_incidents:
            story.append(Paragraph("LINKED INCIDENTS", heading_style))
            incident_data = [["Incident ID", "Type", "Date", "Location"]]
            for inc in case.linked_incidents[:10]:
                incident_data.append(
                    [
                        str(inc.get("incident_id", "Unknown"))[:20],
                        str(inc.get("incident_type", "Unknown"))[:15],
                        str(inc.get("timestamp", "Unknown"))[:19],
                        str(inc.get("location", "Unknown"))[:30],
                    ]
                )
            incident_table = Table(
                incident_data, colWidths=[1.2 * inch, 1.2 * inch, 1.5 * inch, 2.1 * inch]
            )
            incident_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(incident_table)
            story.append(Spacer(1, 12))

        if case.timeline:
            story.append(PageBreak())
            story.append(Paragraph("TIMELINE", heading_style))
            timeline_data = [["Time", "Event", "Source"]]
            for event in case.timeline[:20]:
                timeline_data.append(
                    [
                        event.timestamp.strftime("%Y-%m-%d %H:%M"),
                        event.description[:50],
                        event.source,
                    ]
                )
            timeline_table = Table(timeline_data, colWidths=[1.5 * inch, 3.5 * inch, 1 * inch])
            timeline_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(timeline_table)
            story.append(Spacer(1, 12))

        if case.evidence and case.evidence.total_items > 0:
            story.append(Paragraph("EVIDENCE SUMMARY", heading_style))
            evidence_info = [
                ["RMS Reports:", str(len(case.evidence.reports))],
                ["Audio Metadata:", str(len(case.evidence.audio_metadata))],
                ["Ballistics:", str(len(case.evidence.ballistics))],
                ["LPR Hits:", str(len(case.evidence.lpr_trail))],
                ["BWC Recordings:", str(len(case.evidence.bwc_interactions))],
                ["Camera Snapshots:", str(len(case.evidence.camera_positions))],
                ["Total Items:", str(case.evidence.total_items)],
            ]
            evidence_table = Table(evidence_info, colWidths=[1.5 * inch, 1 * inch])
            evidence_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(evidence_table)
            story.append(Spacer(1, 12))

        if case.leads:
            story.append(Paragraph("INVESTIGATIVE LEADS", heading_style))
            for i, lead in enumerate(case.leads, 1):
                story.append(
                    Paragraph(f"{i}. [{lead.priority.value.upper()}] {lead.title}", normal_style)
                )
                story.append(Paragraph(f"   {lead.description}", normal_style))
            story.append(Spacer(1, 12))

        if case.recommendations:
            story.append(Paragraph("RECOMMENDATIONS", heading_style))
            for i, rec in enumerate(case.recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", normal_style))
            story.append(Spacer(1, 12))

        story.append(Spacer(1, 30))
        story.append(
            Paragraph(
                f"Report generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                ParagraphStyle("Footer", parent=normal_style, fontSize=8, textColor=colors.grey),
            )
        )
        story.append(
            Paragraph(
                "CONFIDENTIAL - LAW ENFORCEMENT SENSITIVE",
                ParagraphStyle("Footer", parent=normal_style, fontSize=8, textColor=colors.red),
            )
        )

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    async def _generate_pdf_simple(self, case: CaseFile) -> bytes:
        """Generate simple text-based PDF when reportlab is not available."""
        content = []
        content.append("=" * 60)
        content.append("INVESTIGATION CASE REPORT")
        content.append("=" * 60)
        content.append("")
        content.append(f"Case Number: {case.case_number}")
        content.append(f"Case ID: {case.case_id}")
        content.append(f"Title: {case.title}")
        content.append(f"Status: {case.status.value.upper()}")
        content.append(f"Priority: {case.priority.value.upper()}")
        content.append(f"Created: {case.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Updated: {case.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        content.append("-" * 60)
        content.append("CASE SUMMARY")
        content.append("-" * 60)
        content.append(case.summary or "No summary available.")
        content.append("")

        if case.risk_assessment:
            content.append("-" * 60)
            content.append("RISK ASSESSMENT")
            content.append("-" * 60)
            content.append(f"Overall Score: {case.risk_assessment.overall_score:.2f}")
            content.append(f"Threat Level: {case.risk_assessment.threat_level.upper()}")
            content.append("")

        if case.suspects:
            content.append("-" * 60)
            content.append("SUSPECTS")
            content.append("-" * 60)
            for i, suspect in enumerate(case.suspects, 1):
                content.append(f"{i}. {suspect.name} (ID: {suspect.entity_id})")
            content.append("")

        if case.vehicles:
            content.append("-" * 60)
            content.append("VEHICLES OF INTEREST")
            content.append("-" * 60)
            for i, vehicle in enumerate(case.vehicles, 1):
                content.append(f"{i}. {vehicle.name}")
            content.append("")

        if case.recommendations:
            content.append("-" * 60)
            content.append("RECOMMENDATIONS")
            content.append("-" * 60)
            for i, rec in enumerate(case.recommendations, 1):
                content.append(f"{i}. {rec}")
            content.append("")

        content.append("")
        content.append(f"Report generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        content.append("CONFIDENTIAL - LAW ENFORCEMENT SENSITIVE")

        text_content = "\n".join(content)
        return text_content.encode("utf-8")


__all__ = [
    "ReportGenerator",
]
