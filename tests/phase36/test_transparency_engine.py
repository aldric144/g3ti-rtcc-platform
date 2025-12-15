"""
Test Suite: Transparency Report Engine
Phase 36: Public Safety Guardian
"""

import pytest
from datetime import datetime, timedelta

from backend.app.public_guardian.transparency_engine import (
    TransparencyReportEngine,
    ReportType,
    ReportPeriod,
    CallCategory,
    TransparencyReport,
    CallsForServiceSummary,
    ResponseTimeSummary,
    UseOfForceSummary,
    SafetyTrendSummary,
    HeatmapSummary,
    HeatmapCell,
)


class TestTransparencyReportEngine:
    def setup_method(self):
        self.engine = TransparencyReportEngine()

    def test_engine_singleton(self):
        engine2 = TransparencyReportEngine()
        assert self.engine is engine2

    def test_generate_comprehensive_report(self):
        report = self.engine.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        assert report is not None
        assert report.report_id is not None
        assert report.report_type == ReportType.COMPREHENSIVE
        assert report.period == ReportPeriod.WEEKLY

    def test_generate_calls_for_service_report(self):
        report = self.engine.generate_report(
            report_type=ReportType.CALLS_FOR_SERVICE,
            period=ReportPeriod.WEEKLY
        )
        assert report is not None
        assert report.calls_for_service is not None
        assert report.calls_for_service.total_calls >= 0

    def test_generate_response_times_report(self):
        report = self.engine.generate_report(
            report_type=ReportType.RESPONSE_TIMES,
            period=ReportPeriod.WEEKLY
        )
        assert report is not None
        assert report.response_times is not None
        assert report.response_times.average_response_time_seconds >= 0

    def test_generate_use_of_force_report(self):
        report = self.engine.generate_report(
            report_type=ReportType.USE_OF_FORCE,
            period=ReportPeriod.MONTHLY
        )
        assert report is not None
        assert report.use_of_force is not None
        assert report.use_of_force.total_incidents >= 0

    def test_generate_safety_trends_report(self):
        report = self.engine.generate_report(
            report_type=ReportType.SAFETY_TRENDS,
            period=ReportPeriod.QUARTERLY
        )
        assert report is not None
        assert report.safety_trends is not None

    def test_generate_heatmap_report(self):
        report = self.engine.generate_report(
            report_type=ReportType.HEATMAP,
            period=ReportPeriod.WEEKLY
        )
        assert report is not None
        assert report.heatmap is not None
        assert len(report.heatmap.cells) > 0

    def test_heatmap_blur_radius(self):
        report = self.engine.generate_report(
            report_type=ReportType.HEATMAP,
            period=ReportPeriod.WEEKLY
        )
        for cell in report.heatmap.cells:
            assert cell.blur_radius >= 100, "Blur radius must be at least 100m for privacy"

    def test_weekly_report(self):
        report = self.engine.get_weekly_report()
        assert report is not None
        assert report.period == ReportPeriod.WEEKLY

    def test_monthly_report(self):
        report = self.engine.get_monthly_report()
        assert report is not None
        assert report.period == ReportPeriod.MONTHLY

    def test_quarterly_report(self):
        report = self.engine.get_quarterly_report()
        assert report is not None
        assert report.period == ReportPeriod.QUARTERLY

    def test_report_compliance_frameworks(self):
        report = self.engine.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        assert len(report.compliance_frameworks) > 0
        assert "CJIS" in report.compliance_frameworks or "cjis" in [f.lower() for f in report.compliance_frameworks]

    def test_report_redactions_applied(self):
        report = self.engine.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        assert isinstance(report.redactions_applied, list)

    def test_export_to_json(self):
        report = self.engine.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        json_data = self.engine.export_to_json(report.report_id)
        assert json_data is not None

    def test_export_to_pdf_data(self):
        report = self.engine.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        pdf_data = self.engine.export_to_pdf_data(report.report_id)
        assert pdf_data is not None

    def test_get_report(self):
        report = self.engine.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        retrieved = self.engine.get_report(report.report_id)
        assert retrieved is not None
        assert retrieved.report_id == report.report_id

    def test_get_recent_reports(self):
        self.engine.generate_report(ReportType.COMPREHENSIVE, ReportPeriod.WEEKLY)
        reports = self.engine.get_recent_reports(limit=5)
        assert len(reports) > 0

    def test_get_statistics(self):
        stats = self.engine.get_statistics()
        assert "reports_generated" in stats
        assert "weekly_reports" in stats
        assert "monthly_reports" in stats

    def test_report_to_dict(self):
        report = self.engine.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        report_dict = report.to_dict()
        assert "report_id" in report_dict
        assert "report_type" in report_dict
        assert "period" in report_dict

    def test_report_hash_generation(self):
        report = self.engine.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY
        )
        assert report.report_hash is not None
        assert len(report.report_hash) > 0


class TestCallCategory:
    def test_all_categories_exist(self):
        expected = [
            "emergency", "non_emergency", "traffic", "property_crime",
            "violent_crime", "domestic", "mental_health", "community_service",
            "welfare_check", "other"
        ]
        for cat in expected:
            assert hasattr(CallCategory, cat.upper())


class TestReportPeriod:
    def test_all_periods_exist(self):
        expected = ["daily", "weekly", "monthly", "quarterly", "annual"]
        for period in expected:
            assert hasattr(ReportPeriod, period.upper())


class TestReportType:
    def test_all_types_exist(self):
        expected = [
            "calls_for_service", "response_times", "use_of_force",
            "safety_trends", "heatmap", "comprehensive"
        ]
        for rt in expected:
            assert hasattr(ReportType, rt.upper())
