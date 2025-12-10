"""
Phase 20: Autonomous Investigator Tests

Tests for AutoInvestigatePipeline and DailyCaseTriageEngine.
"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.ada.autonomous_investigator import (
    AutoInvestigatePipeline,
    DailyCaseTriageEngine,
    InvestigationStatus,
    TriagePriority,
    TriageReason,
)


class TestAutoInvestigatePipeline:
    def setup_method(self):
        self.pipeline = AutoInvestigatePipeline()

    def test_start_investigation(self):
        case_data = {
            "offense_type": "homicide",
            "incident_date": "2024-01-15",
            "location": {"address": "123 Main St", "lat": 33.749, "lng": -84.388},
            "victim": {"name": "John Doe", "age": 35},
        }
        evidence_items = [
            {"id": "ev-001", "type": "weapon", "description": "Knife"},
            {"id": "ev-002", "type": "dna", "description": "DNA sample"},
        ]
        suspects = [
            {"id": "sus-001", "name": "Jane Smith", "relationship": "spouse"},
        ]
        result = self.pipeline.start_investigation(
            case_id="case-001",
            case_data=case_data,
            evidence_items=evidence_items,
            suspects=suspects,
        )
        assert result is not None
        assert result.case_id == "case-001"
        assert result.status in [
            InvestigationStatus.PENDING,
            InvestigationStatus.IN_PROGRESS,
            InvestigationStatus.COMPLETED,
        ]

    def test_get_investigation_result(self):
        case_data = {"offense_type": "robbery"}
        result = self.pipeline.start_investigation(
            case_id="case-002",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        retrieved = self.pipeline.get_investigation_result(result.result_id)
        assert retrieved is not None
        assert retrieved.result_id == result.result_id

    def test_get_investigation_progress(self):
        case_data = {"offense_type": "burglary"}
        result = self.pipeline.start_investigation(
            case_id="case-003",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        progress = self.pipeline.get_investigation_progress(result.result_id)
        assert progress is not None
        assert "current_stage" in progress
        assert "progress_percent" in progress

    def test_investigation_has_suspects(self):
        case_data = {"offense_type": "assault"}
        evidence_items = [{"id": "ev-001", "type": "fingerprint"}]
        suspects = [{"id": "sus-001", "name": "Test Suspect"}]
        result = self.pipeline.start_investigation(
            case_id="case-004",
            case_data=case_data,
            evidence_items=evidence_items,
            suspects=suspects,
        )
        assert hasattr(result, "suspects_identified")

    def test_investigation_has_theories(self):
        case_data = {"offense_type": "theft"}
        result = self.pipeline.start_investigation(
            case_id="case-005",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        assert hasattr(result, "theories_generated")

    def test_investigation_has_linked_cases(self):
        case_data = {"offense_type": "burglary"}
        result = self.pipeline.start_investigation(
            case_id="case-006",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        assert hasattr(result, "linked_cases")

    def test_investigation_has_report(self):
        case_data = {"offense_type": "homicide"}
        result = self.pipeline.start_investigation(
            case_id="case-007",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        assert hasattr(result, "report_id")

    def test_get_case_investigations(self):
        case_data = {"offense_type": "robbery"}
        self.pipeline.start_investigation(
            case_id="case-008",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        investigations = self.pipeline.get_case_investigations("case-008")
        assert len(investigations) >= 1

    def test_get_metrics(self):
        metrics = self.pipeline.get_metrics()
        assert "total_investigations" in metrics
        assert "by_status" in metrics


class TestDailyCaseTriageEngine:
    def setup_method(self):
        self.engine = DailyCaseTriageEngine()

    def test_triage_case(self):
        case_data = {
            "status": "open",
            "days_since_last_activity": 30,
            "has_new_evidence": True,
            "suspect_identified": False,
        }
        triage_item = self.engine.triage_case(
            case_id="case-001",
            case_data=case_data,
        )
        assert triage_item is not None
        assert triage_item.case_id == "case-001"
        assert triage_item.priority in [
            TriagePriority.CRITICAL,
            TriagePriority.HIGH,
            TriagePriority.MEDIUM,
            TriagePriority.LOW,
            TriagePriority.ROUTINE,
        ]

    def test_get_triage_item(self):
        case_data = {"status": "open"}
        triage_item = self.engine.triage_case(
            case_id="case-002",
            case_data=case_data,
        )
        retrieved = self.engine.get_triage_item(triage_item.triage_id)
        assert retrieved is not None
        assert retrieved.triage_id == triage_item.triage_id

    def test_triage_has_reasons(self):
        case_data = {
            "status": "open",
            "has_new_evidence": True,
            "forensic_results_pending": True,
        }
        triage_item = self.engine.triage_case(
            case_id="case-003",
            case_data=case_data,
        )
        assert hasattr(triage_item, "reasons")
        assert isinstance(triage_item.reasons, list)

    def test_triage_has_recommended_actions(self):
        case_data = {"status": "open", "suspect_identified": True}
        triage_item = self.engine.triage_case(
            case_id="case-004",
            case_data=case_data,
        )
        assert hasattr(triage_item, "recommended_actions")
        assert isinstance(triage_item.recommended_actions, list)

    def test_run_daily_triage(self):
        cases = [
            {"case_id": "case-005", "data": {"status": "open"}},
            {"case_id": "case-006", "data": {"status": "open", "has_new_evidence": True}},
            {"case_id": "case-007", "data": {"status": "open", "days_since_last_activity": 60}},
        ]
        report = self.engine.run_daily_triage(cases)
        assert report is not None
        assert hasattr(report, "triage_items")
        assert len(report.triage_items) == 3

    def test_daily_triage_report_has_summary(self):
        cases = [
            {"case_id": "case-008", "data": {"status": "open"}},
        ]
        report = self.engine.run_daily_triage(cases)
        assert hasattr(report, "summary")
        assert "total_cases" in report.summary

    def test_get_critical_cases(self):
        case_data = {
            "status": "open",
            "has_new_evidence": True,
            "suspect_identified": True,
            "witness_available": True,
        }
        self.engine.triage_case(
            case_id="case-009",
            case_data=case_data,
        )
        critical = self.engine.get_critical_cases()
        assert isinstance(critical, list)

    def test_get_cases_by_priority(self):
        case_data = {"status": "open"}
        self.engine.triage_case(
            case_id="case-010",
            case_data=case_data,
        )
        cases = self.engine.get_cases_by_priority(TriagePriority.MEDIUM)
        assert isinstance(cases, list)

    def test_mark_reviewed(self):
        case_data = {"status": "open"}
        triage_item = self.engine.triage_case(
            case_id="case-011",
            case_data=case_data,
        )
        reviewed = self.engine.mark_reviewed(
            triage_id=triage_item.triage_id,
            reviewed_by="Detective Smith",
        )
        assert reviewed is not None
        assert reviewed.reviewed is True

    def test_triage_scoring(self):
        high_priority_data = {
            "status": "open",
            "has_new_evidence": True,
            "suspect_identified": True,
            "forensic_results_pending": True,
        }
        low_priority_data = {
            "status": "open",
            "days_since_last_activity": 5,
        }
        high_item = self.engine.triage_case(
            case_id="case-012",
            case_data=high_priority_data,
        )
        low_item = self.engine.triage_case(
            case_id="case-013",
            case_data=low_priority_data,
        )
        assert high_item.score >= low_item.score

    def test_get_metrics(self):
        metrics = self.engine.get_metrics()
        assert "total_triaged" in metrics
        assert "by_priority" in metrics
