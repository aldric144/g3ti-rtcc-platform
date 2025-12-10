"""
Phase 23: GovernanceKPIEngine Tests
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app.city_governance.kpi_engine import (
    GovernanceKPIEngine,
    get_kpi_engine,
    KPICategory,
    ReportPeriod,
    TrendDirection,
    KPIMetric,
    KPITimeSeries,
    DepartmentScore,
    CityHealthIndex,
    BudgetMetrics,
    PerformanceReport,
    ResponseTimeAnalyzer,
    PatrolEfficiencyAnalyzer,
    TrafficAnalyzer,
    UtilityAnalyzer,
    FireEMSReadinessAnalyzer,
    BudgetAnalyzer,
)


class TestGovernanceKPIEngine:
    """Tests for GovernanceKPIEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = GovernanceKPIEngine()

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        assert self.engine._response_time_analyzer is not None
        assert self.engine._patrol_analyzer is not None
        assert self.engine._traffic_analyzer is not None
        assert self.engine._utility_analyzer is not None
        assert self.engine._fire_ems_analyzer is not None
        assert self.engine._budget_analyzer is not None

    def test_get_singleton_instance(self):
        """Test singleton pattern returns same instance."""
        engine1 = get_kpi_engine()
        engine2 = get_kpi_engine()
        assert engine1 is engine2

    def test_get_all_kpis(self):
        """Test getting all KPI metrics."""
        kpis = self.engine.get_all_kpis()
        assert len(kpis) > 0
        assert all(isinstance(k, KPIMetric) for k in kpis)

    def test_get_kpis_by_category(self):
        """Test filtering KPIs by category."""
        response_kpis = self.engine.get_kpis_by_category(KPICategory.RESPONSE_TIME)
        assert len(response_kpis) > 0
        assert all(k.category == KPICategory.RESPONSE_TIME for k in response_kpis)

        patrol_kpis = self.engine.get_kpis_by_category(KPICategory.PATROL_EFFICIENCY)
        assert len(patrol_kpis) > 0
        assert all(k.category == KPICategory.PATROL_EFFICIENCY for k in patrol_kpis)

    def test_get_city_health_index(self):
        """Test getting city health index."""
        health = self.engine.get_city_health_index()

        assert health is not None
        assert isinstance(health, CityHealthIndex)
        assert 0 <= health.overall_score <= 100
        assert health.trend in [t for t in TrendDirection]
        assert len(health.component_scores) > 0

    def test_city_health_grade(self):
        """Test city health grade calculation."""
        health = self.engine.get_city_health_index()
        health_dict = health.to_dict()

        assert "grade" in health_dict
        assert health_dict["grade"] in ["A", "B", "C", "D", "F"]

    def test_get_department_scores(self):
        """Test getting department scores."""
        scores = self.engine.get_department_scores()

        assert len(scores) == 4
        departments = [s.department for s in scores]
        assert "Police" in departments
        assert "Fire" in departments
        assert "EMS" in departments
        assert "Public Works" in departments

        for score in scores:
            assert 0 <= score.overall_score <= 100
            assert len(score.recommendations) > 0

    def test_get_budget_metrics(self):
        """Test getting budget metrics."""
        budget = self.engine.get_budget_metrics()

        assert budget is not None
        assert isinstance(budget, BudgetMetrics)
        assert budget.total_budget > 0
        assert budget.spent_to_date >= 0
        assert budget.overtime_hours >= 0
        assert budget.budget_health in ["healthy", "at_risk"]

    def test_get_overtime_forecast(self):
        """Test getting overtime forecast."""
        forecast = self.engine.get_overtime_forecast(months=3)

        assert len(forecast) == 3
        for month in forecast:
            assert "month" in month
            assert "projected_hours" in month
            assert "projected_cost" in month
            assert "confidence" in month

    def test_get_time_series_response_time(self):
        """Test getting response time time series."""
        series = self.engine.get_time_series(
            KPICategory.RESPONSE_TIME,
            ReportPeriod.DAILY,
        )

        assert len(series) > 0
        for s in series:
            assert isinstance(s, KPITimeSeries)
            assert len(s.data_points) > 0

    def test_get_time_series_different_periods(self):
        """Test time series for different periods."""
        daily = self.engine.get_time_series(KPICategory.RESPONSE_TIME, ReportPeriod.DAILY)
        weekly = self.engine.get_time_series(KPICategory.RESPONSE_TIME, ReportPeriod.WEEKLY)
        monthly = self.engine.get_time_series(KPICategory.RESPONSE_TIME, ReportPeriod.MONTHLY)

        assert len(daily) > 0
        assert len(weekly) > 0
        assert len(monthly) > 0

    def test_generate_daily_report(self):
        """Test generating daily report."""
        report = self.engine.generate_report(ReportPeriod.DAILY)

        assert report is not None
        assert isinstance(report, PerformanceReport)
        assert report.period == ReportPeriod.DAILY
        assert report.city_health_index is not None
        assert len(report.department_scores) > 0
        assert len(report.key_metrics) > 0
        assert report.budget_metrics is not None

    def test_generate_weekly_report(self):
        """Test generating weekly report."""
        report = self.engine.generate_report(ReportPeriod.WEEKLY)

        assert report is not None
        assert report.period == ReportPeriod.WEEKLY
        assert report.end_date > report.start_date

    def test_generate_monthly_report(self):
        """Test generating monthly report."""
        report = self.engine.generate_report(ReportPeriod.MONTHLY)

        assert report is not None
        assert report.period == ReportPeriod.MONTHLY

    def test_report_highlights_and_concerns(self):
        """Test report highlights and concerns generation."""
        report = self.engine.generate_report(ReportPeriod.DAILY)

        assert isinstance(report.highlights, list)
        assert isinstance(report.concerns, list)
        assert isinstance(report.recommendations, list)

    def test_get_report(self):
        """Test getting a specific report."""
        report = self.engine.generate_report(ReportPeriod.DAILY)
        retrieved = self.engine.get_report(report.report_id)

        assert retrieved is not None
        assert retrieved.report_id == report.report_id

    def test_get_reports(self):
        """Test getting all reports."""
        self.engine.generate_report(ReportPeriod.DAILY)
        self.engine.generate_report(ReportPeriod.WEEKLY)

        reports = self.engine.get_reports()
        assert len(reports) >= 2

    def test_get_reports_filtered_by_period(self):
        """Test getting reports filtered by period."""
        self.engine.generate_report(ReportPeriod.DAILY)
        self.engine.generate_report(ReportPeriod.WEEKLY)

        daily_reports = self.engine.get_reports(period=ReportPeriod.DAILY)
        assert all(r.period == ReportPeriod.DAILY for r in daily_reports)

    def test_statistics(self):
        """Test statistics generation."""
        self.engine.get_all_kpis()
        self.engine.generate_report(ReportPeriod.DAILY)

        stats = self.engine.get_statistics()
        assert "total_kpis" in stats
        assert "total_reports" in stats
        assert "kpis_by_category" in stats
        assert "last_refresh" in stats

    def test_kpi_metric_to_dict(self):
        """Test KPI metric serialization."""
        kpis = self.engine.get_all_kpis()
        kpi_dict = kpis[0].to_dict()

        assert "metric_id" in kpi_dict
        assert "name" in kpi_dict
        assert "category" in kpi_dict
        assert "value" in kpi_dict
        assert "unit" in kpi_dict
        assert "target" in kpi_dict
        assert "trend" in kpi_dict
        assert "status" in kpi_dict

    def test_report_to_dict(self):
        """Test report serialization."""
        report = self.engine.generate_report(ReportPeriod.DAILY)
        report_dict = report.to_dict()

        assert "report_id" in report_dict
        assert "period" in report_dict
        assert "start_date" in report_dict
        assert "end_date" in report_dict
        assert "city_health_index" in report_dict
        assert "department_scores" in report_dict
        assert "key_metrics" in report_dict
        assert "budget_metrics" in report_dict


class TestKPICategories:
    """Tests for KPI category enumeration."""

    def test_all_categories_defined(self):
        """Test all expected categories are defined."""
        expected_categories = [
            "response_time",
            "patrol_efficiency",
            "budget",
            "overtime",
            "utility_uptime",
            "traffic",
            "fire_ems_readiness",
            "city_health",
            "crime",
            "public_works",
            "citizen_satisfaction",
        ]
        for category in expected_categories:
            assert KPICategory(category) is not None


class TestReportPeriod:
    """Tests for report period enumeration."""

    def test_periods_defined(self):
        """Test report periods are defined."""
        assert ReportPeriod.DAILY.value == "daily"
        assert ReportPeriod.WEEKLY.value == "weekly"
        assert ReportPeriod.MONTHLY.value == "monthly"
        assert ReportPeriod.QUARTERLY.value == "quarterly"
        assert ReportPeriod.YEARLY.value == "yearly"


class TestTrendDirection:
    """Tests for trend direction enumeration."""

    def test_trends_defined(self):
        """Test trend directions are defined."""
        assert TrendDirection.IMPROVING.value == "improving"
        assert TrendDirection.STABLE.value == "stable"
        assert TrendDirection.DECLINING.value == "declining"
        assert TrendDirection.CRITICAL.value == "critical"


class TestResponseTimeAnalyzer:
    """Tests for ResponseTimeAnalyzer."""

    def test_analyze(self):
        """Test response time analysis."""
        analyzer = ResponseTimeAnalyzer()
        metrics = analyzer.analyze()

        assert len(metrics) == 3
        metric_names = [m.name for m in metrics]
        assert "Police Response Time" in metric_names
        assert "Fire Response Time" in metric_names
        assert "EMS Response Time" in metric_names

    def test_get_time_series(self):
        """Test response time time series."""
        analyzer = ResponseTimeAnalyzer()
        series = analyzer.get_time_series(ReportPeriod.DAILY)

        assert len(series) == 3
        for s in series:
            assert len(s.data_points) == 24


class TestPatrolEfficiencyAnalyzer:
    """Tests for PatrolEfficiencyAnalyzer."""

    def test_analyze(self):
        """Test patrol efficiency analysis."""
        analyzer = PatrolEfficiencyAnalyzer()
        metrics = analyzer.analyze()

        assert len(metrics) == 3
        assert all(m.category == KPICategory.PATROL_EFFICIENCY for m in metrics)


class TestTrafficAnalyzer:
    """Tests for TrafficAnalyzer."""

    def test_analyze(self):
        """Test traffic analysis."""
        analyzer = TrafficAnalyzer()
        metrics = analyzer.analyze()

        assert len(metrics) == 3
        assert all(m.category == KPICategory.TRAFFIC for m in metrics)


class TestUtilityAnalyzer:
    """Tests for UtilityAnalyzer."""

    def test_analyze(self):
        """Test utility analysis."""
        analyzer = UtilityAnalyzer()
        metrics = analyzer.analyze()

        assert len(metrics) == 3
        assert all(m.category == KPICategory.UTILITY_UPTIME for m in metrics)


class TestFireEMSReadinessAnalyzer:
    """Tests for FireEMSReadinessAnalyzer."""

    def test_analyze(self):
        """Test fire/EMS readiness analysis."""
        analyzer = FireEMSReadinessAnalyzer()
        metrics = analyzer.analyze()

        assert len(metrics) == 3
        assert all(m.category == KPICategory.FIRE_EMS_READINESS for m in metrics)


class TestBudgetAnalyzer:
    """Tests for BudgetAnalyzer."""

    def test_analyze(self):
        """Test budget analysis."""
        analyzer = BudgetAnalyzer()
        metrics = analyzer.analyze()

        assert metrics is not None
        assert isinstance(metrics, BudgetMetrics)
        assert metrics.total_budget > 0

    def test_overtime_forecast(self):
        """Test overtime forecast."""
        analyzer = BudgetAnalyzer()
        forecast = analyzer.get_overtime_forecast(months=6)

        assert len(forecast) == 6
        for month in forecast:
            assert month["projected_hours"] > 0
            assert month["projected_cost"] > 0
