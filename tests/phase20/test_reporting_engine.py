"""
Phase 20: Reporting Engine Tests

Tests for DraftReportBuilder, DetectiveBriefGenerator,
CourtReadyEvidencePacketGenerator, and SupervisorReviewMode.
"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.ada.reporting_engine import (
    DraftReportBuilder,
    DetectiveBriefGenerator,
    CourtReadyEvidencePacketGenerator,
    SupervisorReviewMode,
    ReportType,
    ReportStatus,
    ReviewDecision,
)


class TestDraftReportBuilder:
    def setup_method(self):
        self.builder = DraftReportBuilder()

    def test_create_report(self):
        report = self.builder.create_report(
            case_id="case-001",
            report_type="investigative",
            title="Initial Investigation Report",
            author="Detective Smith",
        )
        assert report is not None
        assert report.case_id == "case-001"
        assert report.report_type == ReportType.INVESTIGATIVE
        assert report.status == ReportStatus.DRAFT

    def test_get_report(self):
        report = self.builder.create_report(
            case_id="case-002",
            report_type="supplemental",
            title="Supplemental Report",
            author="Detective Jones",
        )
        retrieved = self.builder.get_report(report.report_id)
        assert retrieved is not None
        assert retrieved.report_id == report.report_id

    def test_add_section(self):
        report = self.builder.create_report(
            case_id="case-003",
            report_type="investigative",
            title="Test Report",
            author="Detective Test",
        )
        section = self.builder.add_section(
            report_id=report.report_id,
            section_type="executive_summary",
            content="This is the executive summary of the case.",
        )
        assert section is not None
        assert section.section_type == "executive_summary"

    def test_update_section(self):
        report = self.builder.create_report(
            case_id="case-004",
            report_type="investigative",
            title="Test Report",
            author="Detective Test",
        )
        section = self.builder.add_section(
            report_id=report.report_id,
            section_type="incident_details",
            content="Original content",
        )
        updated = self.builder.update_section(
            section_id=section.section_id,
            content="Updated content",
        )
        assert updated is not None
        assert updated.content == "Updated content"

    def test_finalize_report(self):
        report = self.builder.create_report(
            case_id="case-005",
            report_type="investigative",
            title="Test Report",
            author="Detective Test",
        )
        self.builder.add_section(
            report_id=report.report_id,
            section_type="executive_summary",
            content="Summary",
        )
        finalized = self.builder.finalize_report(report.report_id)
        assert finalized is not None
        assert finalized.status == ReportStatus.PENDING_REVIEW

    def test_export_report_text(self):
        report = self.builder.create_report(
            case_id="case-006",
            report_type="investigative",
            title="Export Test Report",
            author="Detective Test",
        )
        self.builder.add_section(
            report_id=report.report_id,
            section_type="executive_summary",
            content="Test summary",
        )
        exported = self.builder.export_report(report.report_id, "text")
        assert exported is not None
        assert isinstance(exported, str)

    def test_get_case_reports(self):
        self.builder.create_report(
            case_id="case-007",
            report_type="investigative",
            title="Report 1",
            author="Detective Test",
        )
        reports = self.builder.get_case_reports("case-007")
        assert len(reports) >= 1


class TestDetectiveBriefGenerator:
    def setup_method(self):
        self.generator = DetectiveBriefGenerator()

    def test_generate_brief(self):
        case_data = {
            "offense_type": "homicide",
            "incident_date": "2024-01-15",
            "location": "123 Main St",
            "victim": {"name": "John Doe"},
        }
        evidence_items = [
            {"id": "ev-001", "type": "weapon", "description": "Knife"},
        ]
        suspects = [
            {"id": "sus-001", "name": "Jane Smith", "status": "person_of_interest"},
        ]
        brief = self.generator.generate_brief(
            case_id="case-001",
            case_data=case_data,
            evidence_items=evidence_items,
            suspects=suspects,
        )
        assert brief is not None
        assert brief.case_id == "case-001"

    def test_get_brief(self):
        case_data = {"offense_type": "robbery"}
        brief = self.generator.generate_brief(
            case_id="case-002",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        retrieved = self.generator.get_brief(brief.brief_id)
        assert retrieved is not None
        assert retrieved.brief_id == brief.brief_id

    def test_brief_has_key_findings(self):
        case_data = {"offense_type": "burglary"}
        brief = self.generator.generate_brief(
            case_id="case-003",
            case_data=case_data,
            evidence_items=[{"id": "ev-001", "type": "fingerprint"}],
            suspects=[],
        )
        assert hasattr(brief, "key_findings")
        assert isinstance(brief.key_findings, list)

    def test_brief_has_recommended_actions(self):
        case_data = {"offense_type": "assault"}
        brief = self.generator.generate_brief(
            case_id="case-004",
            case_data=case_data,
            evidence_items=[],
            suspects=[{"id": "sus-001", "name": "Test"}],
        )
        assert hasattr(brief, "recommended_actions")
        assert isinstance(brief.recommended_actions, list)

    def test_export_brief(self):
        case_data = {"offense_type": "theft"}
        brief = self.generator.generate_brief(
            case_id="case-005",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        exported = self.generator.export_brief(brief.brief_id, "text")
        assert exported is not None
        assert isinstance(exported, str)


class TestCourtReadyEvidencePacketGenerator:
    def setup_method(self):
        self.generator = CourtReadyEvidencePacketGenerator()

    def test_generate_packet(self):
        case_data = {
            "case_number": "2024-CR-001234",
            "defendant_name": "John Doe",
            "charges": ["Murder in the First Degree"],
        }
        evidence_items = [
            {
                "id": "ev-001",
                "type": "weapon",
                "description": "Murder weapon",
                "chain_of_custody": [
                    {"officer": "Smith", "date": "2024-01-15", "action": "collected"},
                ],
            },
        ]
        packet = self.generator.generate_packet(
            case_id="case-001",
            case_data=case_data,
            evidence_items=evidence_items,
        )
        assert packet is not None
        assert packet.case_id == "case-001"
        assert packet.case_number == "2024-CR-001234"

    def test_get_packet(self):
        case_data = {"case_number": "2024-CR-001235", "defendant_name": "Jane Doe"}
        packet = self.generator.generate_packet(
            case_id="case-002",
            case_data=case_data,
            evidence_items=[],
        )
        retrieved = self.generator.get_packet(packet.packet_id)
        assert retrieved is not None
        assert retrieved.packet_id == packet.packet_id

    def test_packet_has_evidence_list(self):
        case_data = {"case_number": "2024-CR-001236", "defendant_name": "Test"}
        packet = self.generator.generate_packet(
            case_id="case-003",
            case_data=case_data,
            evidence_items=[{"id": "ev-001", "type": "dna"}],
        )
        assert hasattr(packet, "evidence_list")
        assert isinstance(packet.evidence_list, list)

    def test_packet_has_chain_of_custody(self):
        case_data = {"case_number": "2024-CR-001237", "defendant_name": "Test"}
        evidence_items = [
            {
                "id": "ev-001",
                "type": "weapon",
                "chain_of_custody": [
                    {"officer": "Smith", "date": "2024-01-15", "action": "collected"},
                ],
            },
        ]
        packet = self.generator.generate_packet(
            case_id="case-004",
            case_data=case_data,
            evidence_items=evidence_items,
        )
        assert hasattr(packet, "chain_of_custody_docs")

    def test_finalize_packet(self):
        case_data = {"case_number": "2024-CR-001238", "defendant_name": "Test"}
        packet = self.generator.generate_packet(
            case_id="case-005",
            case_data=case_data,
            evidence_items=[],
        )
        finalized = self.generator.finalize_packet(packet.packet_id)
        assert finalized is not None
        assert finalized.status == "finalized"

    def test_export_packet(self):
        case_data = {"case_number": "2024-CR-001239", "defendant_name": "Test"}
        packet = self.generator.generate_packet(
            case_id="case-006",
            case_data=case_data,
            evidence_items=[],
        )
        exported = self.generator.export_packet(packet.packet_id, "pdf_metadata")
        assert exported is not None


class TestSupervisorReviewMode:
    def setup_method(self):
        self.report_builder = DraftReportBuilder()
        self.reviewer = SupervisorReviewMode(self.report_builder)

    def test_start_review(self):
        report = self.report_builder.create_report(
            case_id="case-001",
            report_type="investigative",
            title="Test Report",
            author="Detective Test",
        )
        self.report_builder.finalize_report(report.report_id)
        review = self.reviewer.start_review(
            report_id=report.report_id,
            reviewer_id="supervisor-001",
            reviewer_name="Sgt. Johnson",
        )
        assert review is not None
        assert review.report_id == report.report_id

    def test_get_review(self):
        report = self.report_builder.create_report(
            case_id="case-002",
            report_type="supplemental",
            title="Test Report",
            author="Detective Test",
        )
        self.report_builder.finalize_report(report.report_id)
        review = self.reviewer.start_review(
            report_id=report.report_id,
            reviewer_id="supervisor-002",
            reviewer_name="Lt. Smith",
        )
        retrieved = self.reviewer.get_review(review.review_id)
        assert retrieved is not None
        assert retrieved.review_id == review.review_id

    def test_add_comment(self):
        report = self.report_builder.create_report(
            case_id="case-003",
            report_type="investigative",
            title="Test Report",
            author="Detective Test",
        )
        self.report_builder.finalize_report(report.report_id)
        review = self.reviewer.start_review(
            report_id=report.report_id,
            reviewer_id="supervisor-003",
            reviewer_name="Capt. Jones",
        )
        comment = self.reviewer.add_comment(
            review_id=review.review_id,
            section_id="section-001",
            comment_text="Please clarify this section.",
        )
        assert comment is not None

    def test_submit_decision_approve(self):
        report = self.report_builder.create_report(
            case_id="case-004",
            report_type="investigative",
            title="Test Report",
            author="Detective Test",
        )
        self.report_builder.finalize_report(report.report_id)
        review = self.reviewer.start_review(
            report_id=report.report_id,
            reviewer_id="supervisor-004",
            reviewer_name="Chief Brown",
        )
        decision = self.reviewer.submit_decision(
            review_id=review.review_id,
            decision=ReviewDecision.APPROVED,
            notes="Report is complete and accurate.",
        )
        assert decision is not None
        assert decision.decision == ReviewDecision.APPROVED

    def test_submit_decision_revise(self):
        report = self.report_builder.create_report(
            case_id="case-005",
            report_type="investigative",
            title="Test Report",
            author="Detective Test",
        )
        self.report_builder.finalize_report(report.report_id)
        review = self.reviewer.start_review(
            report_id=report.report_id,
            reviewer_id="supervisor-005",
            reviewer_name="Sgt. Wilson",
        )
        decision = self.reviewer.submit_decision(
            review_id=review.review_id,
            decision=ReviewDecision.REVISE,
            notes="Needs more detail in evidence section.",
        )
        assert decision is not None
        assert decision.decision == ReviewDecision.REVISE

    def test_get_pending_reviews(self):
        report = self.report_builder.create_report(
            case_id="case-006",
            report_type="investigative",
            title="Test Report",
            author="Detective Test",
        )
        self.report_builder.finalize_report(report.report_id)
        self.reviewer.start_review(
            report_id=report.report_id,
            reviewer_id="supervisor-006",
            reviewer_name="Lt. Davis",
        )
        pending = self.reviewer.get_pending_reviews()
        assert isinstance(pending, list)
