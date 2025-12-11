"""
Phase 23: Governance KPI Engine Module

Generates city performance dashboards with metrics for response time,
patrol efficiency, budget impact, overtime forecasting, utility uptime,
traffic congestion, fire/EMS readiness, and city-wide health index.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import uuid
import math
import random


class KPICategory(Enum):
    """Categories of KPIs."""
    RESPONSE_TIME = "response_time"
    PATROL_EFFICIENCY = "patrol_efficiency"
    BUDGET = "budget"
    OVERTIME = "overtime"
    UTILITY_UPTIME = "utility_uptime"
    TRAFFIC = "traffic"
    FIRE_EMS_READINESS = "fire_ems_readiness"
    CITY_HEALTH = "city_health"
    CRIME = "crime"
    PUBLIC_WORKS = "public_works"
    CITIZEN_SATISFACTION = "citizen_satisfaction"


class ReportPeriod(Enum):
    """Report time periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendDirection(Enum):
    """Direction of KPI trends."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL = "critical"


@dataclass
class KPIMetric:
    """A single KPI metric."""
    metric_id: str
    name: str
    category: KPICategory
    value: float
    unit: str
    target: float
    threshold_warning: float
    threshold_critical: float
    trend: TrendDirection
    change_percent: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "category": self.category.value,
            "value": self.value,
            "unit": self.unit,
            "target": self.target,
            "threshold_warning": self.threshold_warning,
            "threshold_critical": self.threshold_critical,
            "trend": self.trend.value,
            "change_percent": self.change_percent,
            "timestamp": self.timestamp.isoformat(),
            "status": self._get_status(),
        }

    def _get_status(self) -> str:
        """Get status based on value and thresholds."""
        if self.value <= self.target:
            return "on_target"
        elif self.value <= self.threshold_warning:
            return "warning"
        elif self.value <= self.threshold_critical:
            return "critical"
        return "critical"


@dataclass
class KPITimeSeries:
    """Time series data for a KPI."""
    metric_id: str
    metric_name: str
    data_points: list[tuple[datetime, float]]
    period: ReportPeriod

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "data_points": [
                {"timestamp": ts.isoformat(), "value": val}
                for ts, val in self.data_points
            ],
            "period": self.period.value,
        }


@dataclass
class DepartmentScore:
    """Performance score for a department."""
    department: str
    overall_score: float
    metrics: list[KPIMetric]
    trend: TrendDirection
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "department": self.department,
            "overall_score": self.overall_score,
            "metrics": [m.to_dict() for m in self.metrics],
            "trend": self.trend.value,
            "recommendations": self.recommendations,
        }


@dataclass
class CityHealthIndex:
    """Overall city health index."""
    index_id: str
    overall_score: float
    component_scores: dict[str, float]
    trend: TrendDirection
    change_from_previous: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index_id": self.index_id,
            "overall_score": self.overall_score,
            "component_scores": self.component_scores,
            "trend": self.trend.value,
            "change_from_previous": self.change_from_previous,
            "timestamp": self.timestamp.isoformat(),
            "grade": self._get_grade(),
        }

    def _get_grade(self) -> str:
        """Get letter grade based on score."""
        if self.overall_score >= 90:
            return "A"
        elif self.overall_score >= 80:
            return "B"
        elif self.overall_score >= 70:
            return "C"
        elif self.overall_score >= 60:
            return "D"
        return "F"


@dataclass
class BudgetMetrics:
    """Budget-related metrics."""
    total_budget: float
    spent_to_date: float
    projected_spend: float
    variance: float
    overtime_cost: float
    overtime_hours: float
    projected_overtime: float
    savings_opportunities: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_budget": self.total_budget,
            "spent_to_date": self.spent_to_date,
            "projected_spend": self.projected_spend,
            "variance": self.variance,
            "variance_percent": (self.variance / self.total_budget * 100) if self.total_budget > 0 else 0,
            "overtime_cost": self.overtime_cost,
            "overtime_hours": self.overtime_hours,
            "projected_overtime": self.projected_overtime,
            "savings_opportunities": self.savings_opportunities,
            "budget_health": "healthy" if self.variance >= 0 else "at_risk",
        }


@dataclass
class PerformanceReport:
    """Comprehensive performance report."""
    report_id: str
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    city_health_index: CityHealthIndex
    department_scores: list[DepartmentScore]
    key_metrics: list[KPIMetric]
    budget_metrics: BudgetMetrics
    highlights: list[str]
    concerns: list[str]
    recommendations: list[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "period": self.period.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "city_health_index": self.city_health_index.to_dict(),
            "department_scores": [d.to_dict() for d in self.department_scores],
            "key_metrics": [m.to_dict() for m in self.key_metrics],
            "budget_metrics": self.budget_metrics.to_dict(),
            "highlights": self.highlights,
            "concerns": self.concerns,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at.isoformat(),
        }


class ResponseTimeAnalyzer:
    """Analyzes response time metrics."""

    def __init__(self):
        self._target_police = 5.0
        self._target_fire = 4.0
        self._target_ems = 6.0

    def analyze(self) -> list[KPIMetric]:
        """Analyze response time metrics."""
        metrics = []

        police_avg = 4.8 + random.uniform(-0.5, 0.5)
        metrics.append(KPIMetric(
            metric_id="rt-police",
            name="Police Response Time",
            category=KPICategory.RESPONSE_TIME,
            value=police_avg,
            unit="minutes",
            target=self._target_police,
            threshold_warning=6.0,
            threshold_critical=8.0,
            trend=TrendDirection.IMPROVING if police_avg < self._target_police else TrendDirection.STABLE,
            change_percent=-2.5,
        ))

        fire_avg = 3.9 + random.uniform(-0.3, 0.3)
        metrics.append(KPIMetric(
            metric_id="rt-fire",
            name="Fire Response Time",
            category=KPICategory.RESPONSE_TIME,
            value=fire_avg,
            unit="minutes",
            target=self._target_fire,
            threshold_warning=5.0,
            threshold_critical=7.0,
            trend=TrendDirection.IMPROVING if fire_avg < self._target_fire else TrendDirection.STABLE,
            change_percent=-1.8,
        ))

        ems_avg = 5.5 + random.uniform(-0.4, 0.4)
        metrics.append(KPIMetric(
            metric_id="rt-ems",
            name="EMS Response Time",
            category=KPICategory.RESPONSE_TIME,
            value=ems_avg,
            unit="minutes",
            target=self._target_ems,
            threshold_warning=7.0,
            threshold_critical=9.0,
            trend=TrendDirection.STABLE,
            change_percent=0.5,
        ))

        return metrics

    def get_time_series(self, period: ReportPeriod) -> list[KPITimeSeries]:
        """Get response time trends."""
        series = []
        now = datetime.utcnow()

        if period == ReportPeriod.DAILY:
            points = 24
            delta = timedelta(hours=1)
        elif period == ReportPeriod.WEEKLY:
            points = 7
            delta = timedelta(days=1)
        elif period == ReportPeriod.MONTHLY:
            points = 30
            delta = timedelta(days=1)
        else:
            points = 12
            delta = timedelta(days=30)

        for service, base_value in [("Police", 4.8), ("Fire", 3.9), ("EMS", 5.5)]:
            data_points = []
            for i in range(points):
                ts = now - delta * (points - i - 1)
                value = base_value + random.uniform(-0.5, 0.5) + math.sin(i / 5) * 0.3
                data_points.append((ts, max(1.0, value)))

            series.append(KPITimeSeries(
                metric_id=f"rt-{service.lower()}-series",
                metric_name=f"{service} Response Time",
                data_points=data_points,
                period=period,
            ))

        return series


class PatrolEfficiencyAnalyzer:
    """Analyzes patrol efficiency metrics."""

    def analyze(self) -> list[KPIMetric]:
        """Analyze patrol efficiency metrics."""
        metrics = []

        coverage = 87.5 + random.uniform(-3, 3)
        metrics.append(KPIMetric(
            metric_id="pe-coverage",
            name="Zone Coverage",
            category=KPICategory.PATROL_EFFICIENCY,
            value=coverage,
            unit="percent",
            target=90.0,
            threshold_warning=85.0,
            threshold_critical=75.0,
            trend=TrendDirection.IMPROVING if coverage > 85 else TrendDirection.DECLINING,
            change_percent=1.5,
        ))

        calls_per_unit = 8.2 + random.uniform(-1, 1)
        metrics.append(KPIMetric(
            metric_id="pe-calls",
            name="Calls per Unit per Shift",
            category=KPICategory.PATROL_EFFICIENCY,
            value=calls_per_unit,
            unit="calls",
            target=10.0,
            threshold_warning=12.0,
            threshold_critical=15.0,
            trend=TrendDirection.STABLE,
            change_percent=-0.8,
        ))

        proactive_time = 32.5 + random.uniform(-5, 5)
        metrics.append(KPIMetric(
            metric_id="pe-proactive",
            name="Proactive Patrol Time",
            category=KPICategory.PATROL_EFFICIENCY,
            value=proactive_time,
            unit="percent",
            target=35.0,
            threshold_warning=25.0,
            threshold_critical=15.0,
            trend=TrendDirection.STABLE,
            change_percent=2.1,
        ))

        return metrics


class TrafficAnalyzer:
    """Analyzes traffic-related KPIs."""

    def analyze(self) -> list[KPIMetric]:
        """Analyze traffic metrics."""
        metrics = []

        congestion = 28.5 + random.uniform(-5, 5)
        metrics.append(KPIMetric(
            metric_id="tr-congestion",
            name="Traffic Congestion Score",
            category=KPICategory.TRAFFIC,
            value=congestion,
            unit="score",
            target=25.0,
            threshold_warning=35.0,
            threshold_critical=50.0,
            trend=TrendDirection.STABLE,
            change_percent=-1.2,
        ))

        incidents = 3.2 + random.uniform(-1, 1)
        metrics.append(KPIMetric(
            metric_id="tr-incidents",
            name="Daily Traffic Incidents",
            category=KPICategory.TRAFFIC,
            value=incidents,
            unit="incidents",
            target=3.0,
            threshold_warning=5.0,
            threshold_critical=8.0,
            trend=TrendDirection.IMPROVING if incidents < 3.5 else TrendDirection.STABLE,
            change_percent=-5.0,
        ))

        signal_efficiency = 82.3 + random.uniform(-3, 3)
        metrics.append(KPIMetric(
            metric_id="tr-signals",
            name="Signal Timing Efficiency",
            category=KPICategory.TRAFFIC,
            value=signal_efficiency,
            unit="percent",
            target=85.0,
            threshold_warning=75.0,
            threshold_critical=65.0,
            trend=TrendDirection.IMPROVING,
            change_percent=3.5,
        ))

        return metrics


class UtilityAnalyzer:
    """Analyzes utility uptime metrics."""

    def analyze(self) -> list[KPIMetric]:
        """Analyze utility metrics."""
        metrics = []

        power_uptime = 99.7 + random.uniform(-0.2, 0.1)
        metrics.append(KPIMetric(
            metric_id="ut-power",
            name="Power Grid Uptime",
            category=KPICategory.UTILITY_UPTIME,
            value=power_uptime,
            unit="percent",
            target=99.9,
            threshold_warning=99.5,
            threshold_critical=99.0,
            trend=TrendDirection.STABLE,
            change_percent=0.1,
        ))

        water_uptime = 99.85 + random.uniform(-0.1, 0.05)
        metrics.append(KPIMetric(
            metric_id="ut-water",
            name="Water System Uptime",
            category=KPICategory.UTILITY_UPTIME,
            value=water_uptime,
            unit="percent",
            target=99.9,
            threshold_warning=99.5,
            threshold_critical=99.0,
            trend=TrendDirection.STABLE,
            change_percent=0.05,
        ))

        outage_response = 45.0 + random.uniform(-10, 10)
        metrics.append(KPIMetric(
            metric_id="ut-response",
            name="Outage Response Time",
            category=KPICategory.UTILITY_UPTIME,
            value=outage_response,
            unit="minutes",
            target=30.0,
            threshold_warning=60.0,
            threshold_critical=90.0,
            trend=TrendDirection.IMPROVING if outage_response < 45 else TrendDirection.STABLE,
            change_percent=-8.0,
        ))

        return metrics


class FireEMSReadinessAnalyzer:
    """Analyzes fire and EMS readiness metrics."""

    def analyze(self) -> list[KPIMetric]:
        """Analyze fire/EMS readiness metrics."""
        metrics = []

        unit_availability = 92.5 + random.uniform(-3, 3)
        metrics.append(KPIMetric(
            metric_id="fe-availability",
            name="Unit Availability",
            category=KPICategory.FIRE_EMS_READINESS,
            value=unit_availability,
            unit="percent",
            target=95.0,
            threshold_warning=90.0,
            threshold_critical=85.0,
            trend=TrendDirection.STABLE,
            change_percent=0.5,
        ))

        equipment_ready = 98.2 + random.uniform(-1, 0.5)
        metrics.append(KPIMetric(
            metric_id="fe-equipment",
            name="Equipment Readiness",
            category=KPICategory.FIRE_EMS_READINESS,
            value=equipment_ready,
            unit="percent",
            target=99.0,
            threshold_warning=97.0,
            threshold_critical=95.0,
            trend=TrendDirection.STABLE,
            change_percent=0.2,
        ))

        training_compliance = 95.0 + random.uniform(-2, 2)
        metrics.append(KPIMetric(
            metric_id="fe-training",
            name="Training Compliance",
            category=KPICategory.FIRE_EMS_READINESS,
            value=training_compliance,
            unit="percent",
            target=100.0,
            threshold_warning=95.0,
            threshold_critical=90.0,
            trend=TrendDirection.IMPROVING,
            change_percent=2.0,
        ))

        return metrics


class BudgetAnalyzer:
    """Analyzes budget and overtime metrics."""

    def __init__(self):
        self._annual_budget = 45000000
        self._ytd_days = (datetime.utcnow() - datetime(datetime.utcnow().year, 1, 1)).days

    def analyze(self) -> BudgetMetrics:
        """Analyze budget metrics."""
        expected_spend_rate = self._ytd_days / 365
        expected_spend = self._annual_budget * expected_spend_rate

        actual_spend = expected_spend * (0.95 + random.uniform(-0.05, 0.05))
        projected_spend = actual_spend / expected_spend_rate if expected_spend_rate > 0 else actual_spend

        overtime_hours = 2500 + random.uniform(-200, 200)
        overtime_cost = overtime_hours * 65

        return BudgetMetrics(
            total_budget=self._annual_budget,
            spent_to_date=actual_spend,
            projected_spend=projected_spend,
            variance=self._annual_budget - projected_spend,
            overtime_cost=overtime_cost,
            overtime_hours=overtime_hours,
            projected_overtime=overtime_hours * (365 / max(self._ytd_days, 1)),
            savings_opportunities=[
                {"area": "Fleet fuel efficiency", "potential_savings": 25000},
                {"area": "Preventive maintenance scheduling", "potential_savings": 15000},
                {"area": "Shift optimization", "potential_savings": 35000},
            ],
        )

    def get_overtime_forecast(self, months_ahead: int = 3) -> list[dict[str, Any]]:
        """Forecast overtime for upcoming months."""
        forecast = []
        now = datetime.utcnow()

        for i in range(months_ahead):
            month = now + timedelta(days=30 * (i + 1))
            base_hours = 800 + random.uniform(-100, 100)

            if month.month in [6, 7, 8]:
                base_hours *= 1.2
            elif month.month in [11, 12]:
                base_hours *= 1.15

            forecast.append({
                "month": month.strftime("%Y-%m"),
                "projected_hours": base_hours,
                "projected_cost": base_hours * 65,
                "confidence": 0.85 - (i * 0.1),
            })

        return forecast


class GovernanceKPIEngine:
    """
    Main KPI engine that generates city performance dashboards and reports.
    """

    def __init__(self):
        self._response_time_analyzer = ResponseTimeAnalyzer()
        self._patrol_analyzer = PatrolEfficiencyAnalyzer()
        self._traffic_analyzer = TrafficAnalyzer()
        self._utility_analyzer = UtilityAnalyzer()
        self._fire_ems_analyzer = FireEMSReadinessAnalyzer()
        self._budget_analyzer = BudgetAnalyzer()
        self._reports: dict[str, PerformanceReport] = {}
        self._kpi_cache: dict[str, KPIMetric] = {}
        self._last_refresh = datetime.utcnow()

    def get_all_kpis(self) -> list[KPIMetric]:
        """Get all current KPI metrics."""
        self._refresh_if_needed()
        return list(self._kpi_cache.values())

    def get_kpis_by_category(self, category: KPICategory) -> list[KPIMetric]:
        """Get KPIs for a specific category."""
        self._refresh_if_needed()
        return [m for m in self._kpi_cache.values() if m.category == category]

    def get_city_health_index(self) -> CityHealthIndex:
        """Calculate and return the city health index."""
        self._refresh_if_needed()

        component_scores = {}

        response_metrics = self.get_kpis_by_category(KPICategory.RESPONSE_TIME)
        if response_metrics:
            avg_performance = sum(
                100 * (1 - (m.value - m.target) / m.target) for m in response_metrics
            ) / len(response_metrics)
            component_scores["response_time"] = min(100, max(0, avg_performance))

        patrol_metrics = self.get_kpis_by_category(KPICategory.PATROL_EFFICIENCY)
        if patrol_metrics:
            component_scores["patrol_efficiency"] = sum(
                m.value for m in patrol_metrics if m.unit == "percent"
            ) / len([m for m in patrol_metrics if m.unit == "percent"])

        traffic_metrics = self.get_kpis_by_category(KPICategory.TRAFFIC)
        if traffic_metrics:
            congestion = next((m for m in traffic_metrics if "congestion" in m.name.lower()), None)
            if congestion:
                component_scores["traffic"] = 100 - congestion.value

        utility_metrics = self.get_kpis_by_category(KPICategory.UTILITY_UPTIME)
        if utility_metrics:
            component_scores["utilities"] = sum(
                m.value for m in utility_metrics if m.unit == "percent"
            ) / len([m for m in utility_metrics if m.unit == "percent"])

        fire_ems_metrics = self.get_kpis_by_category(KPICategory.FIRE_EMS_READINESS)
        if fire_ems_metrics:
            component_scores["fire_ems"] = sum(
                m.value for m in fire_ems_metrics
            ) / len(fire_ems_metrics)

        overall_score = sum(component_scores.values()) / len(component_scores) if component_scores else 0

        trend = TrendDirection.STABLE
        if overall_score > 85:
            trend = TrendDirection.IMPROVING
        elif overall_score < 70:
            trend = TrendDirection.DECLINING

        return CityHealthIndex(
            index_id=f"chi-{uuid.uuid4().hex[:8]}",
            overall_score=overall_score,
            component_scores=component_scores,
            trend=trend,
            change_from_previous=random.uniform(-2, 3),
        )

    def get_department_scores(self) -> list[DepartmentScore]:
        """Get performance scores for each department."""
        self._refresh_if_needed()
        scores = []

        police_metrics = (
            self.get_kpis_by_category(KPICategory.RESPONSE_TIME)[:1] +
            self.get_kpis_by_category(KPICategory.PATROL_EFFICIENCY)
        )
        police_score = sum(
            100 if m.value <= m.target else 100 * m.target / m.value
            for m in police_metrics
        ) / len(police_metrics) if police_metrics else 0

        scores.append(DepartmentScore(
            department="Police",
            overall_score=police_score,
            metrics=police_metrics,
            trend=TrendDirection.IMPROVING if police_score > 85 else TrendDirection.STABLE,
            recommendations=[
                "Continue proactive patrol initiatives",
                "Focus on response time in Zone 3",
            ],
        ))

        fire_metrics = (
            [m for m in self.get_kpis_by_category(KPICategory.RESPONSE_TIME) if "fire" in m.name.lower()] +
            self.get_kpis_by_category(KPICategory.FIRE_EMS_READINESS)[:2]
        )
        fire_score = sum(
            100 if m.value <= m.target else 100 * m.target / m.value
            for m in fire_metrics
        ) / len(fire_metrics) if fire_metrics else 0

        scores.append(DepartmentScore(
            department="Fire",
            overall_score=fire_score,
            metrics=fire_metrics,
            trend=TrendDirection.STABLE,
            recommendations=[
                "Maintain equipment readiness protocols",
                "Schedule additional training sessions",
            ],
        ))

        ems_metrics = [
            m for m in self.get_kpis_by_category(KPICategory.RESPONSE_TIME)
            if "ems" in m.name.lower()
        ] + self.get_kpis_by_category(KPICategory.FIRE_EMS_READINESS)[2:]
        ems_score = sum(
            100 if m.value <= m.target else 100 * m.target / m.value
            for m in ems_metrics
        ) / len(ems_metrics) if ems_metrics else 85

        scores.append(DepartmentScore(
            department="EMS",
            overall_score=ems_score,
            metrics=ems_metrics,
            trend=TrendDirection.STABLE,
            recommendations=[
                "Monitor peak hour coverage",
                "Review mutual aid agreements",
            ],
        ))

        pw_metrics = self.get_kpis_by_category(KPICategory.UTILITY_UPTIME)
        pw_score = sum(m.value for m in pw_metrics) / len(pw_metrics) if pw_metrics else 0

        scores.append(DepartmentScore(
            department="Public Works",
            overall_score=pw_score,
            metrics=pw_metrics,
            trend=TrendDirection.STABLE,
            recommendations=[
                "Accelerate preventive maintenance schedule",
                "Review outage response procedures",
            ],
        ))

        return scores

    def get_budget_metrics(self) -> BudgetMetrics:
        """Get current budget metrics."""
        return self._budget_analyzer.analyze()

    def get_overtime_forecast(self, months: int = 3) -> list[dict[str, Any]]:
        """Get overtime forecast."""
        return self._budget_analyzer.get_overtime_forecast(months)

    def get_time_series(
        self,
        category: KPICategory,
        period: ReportPeriod,
    ) -> list[KPITimeSeries]:
        """Get time series data for a category."""
        if category == KPICategory.RESPONSE_TIME:
            return self._response_time_analyzer.get_time_series(period)

        now = datetime.utcnow()
        if period == ReportPeriod.DAILY:
            points = 24
            delta = timedelta(hours=1)
        elif period == ReportPeriod.WEEKLY:
            points = 7
            delta = timedelta(days=1)
        elif period == ReportPeriod.MONTHLY:
            points = 30
            delta = timedelta(days=1)
        else:
            points = 12
            delta = timedelta(days=30)

        metrics = self.get_kpis_by_category(category)
        series = []

        for metric in metrics[:3]:
            data_points = []
            for i in range(points):
                ts = now - delta * (points - i - 1)
                variation = random.uniform(-0.1, 0.1) * metric.value
                value = metric.value + variation + math.sin(i / 5) * (metric.value * 0.05)
                data_points.append((ts, max(0, value)))

            series.append(KPITimeSeries(
                metric_id=f"{metric.metric_id}-series",
                metric_name=metric.name,
                data_points=data_points,
                period=period,
            ))

        return series

    def generate_report(self, period: ReportPeriod) -> PerformanceReport:
        """Generate a comprehensive performance report."""
        report_id = f"report-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        if period == ReportPeriod.DAILY:
            start_date = now - timedelta(days=1)
        elif period == ReportPeriod.WEEKLY:
            start_date = now - timedelta(weeks=1)
        elif period == ReportPeriod.MONTHLY:
            start_date = now - timedelta(days=30)
        elif period == ReportPeriod.QUARTERLY:
            start_date = now - timedelta(days=90)
        else:
            start_date = now - timedelta(days=365)

        city_health = self.get_city_health_index()
        department_scores = self.get_department_scores()
        key_metrics = self.get_all_kpis()[:10]
        budget_metrics = self.get_budget_metrics()

        highlights = self._generate_highlights(city_health, department_scores)
        concerns = self._generate_concerns(key_metrics)
        recommendations = self._generate_recommendations(department_scores, budget_metrics)

        report = PerformanceReport(
            report_id=report_id,
            period=period,
            start_date=start_date,
            end_date=now,
            city_health_index=city_health,
            department_scores=department_scores,
            key_metrics=key_metrics,
            budget_metrics=budget_metrics,
            highlights=highlights,
            concerns=concerns,
            recommendations=recommendations,
        )

        self._reports[report_id] = report
        return report

    def _generate_highlights(
        self,
        city_health: CityHealthIndex,
        department_scores: list[DepartmentScore],
    ) -> list[str]:
        """Generate report highlights."""
        highlights = []

        if city_health.overall_score >= 85:
            highlights.append(f"City Health Index at {city_health.overall_score:.1f}% - Excellent performance")

        for dept in department_scores:
            if dept.overall_score >= 90:
                highlights.append(f"{dept.department} department achieving {dept.overall_score:.1f}% performance")

        if city_health.change_from_previous > 0:
            highlights.append(f"Overall performance improved by {city_health.change_from_previous:.1f}%")

        return highlights[:5]

    def _generate_concerns(self, metrics: list[KPIMetric]) -> list[str]:
        """Generate report concerns."""
        concerns = []

        for metric in metrics:
            if metric.value > metric.threshold_warning:
                concerns.append(f"{metric.name} at {metric.value:.1f} {metric.unit} - above warning threshold")

        declining = [m for m in metrics if m.trend == TrendDirection.DECLINING]
        for metric in declining[:3]:
            concerns.append(f"{metric.name} showing declining trend ({metric.change_percent:.1f}%)")

        return concerns[:5]

    def _generate_recommendations(
        self,
        department_scores: list[DepartmentScore],
        budget_metrics: BudgetMetrics,
    ) -> list[str]:
        """Generate report recommendations."""
        recommendations = []

        for dept in department_scores:
            if dept.overall_score < 85:
                recommendations.extend(dept.recommendations[:1])

        if budget_metrics.variance < 0:
            recommendations.append("Review budget allocation to address projected overspend")

        if budget_metrics.projected_overtime > budget_metrics.overtime_hours * 1.1:
            recommendations.append("Implement overtime reduction strategies")

        for opp in budget_metrics.savings_opportunities[:2]:
            recommendations.append(f"Consider {opp['area']} for potential ${opp['potential_savings']:,} savings")

        return recommendations[:7]

    def get_report(self, report_id: str) -> Optional[PerformanceReport]:
        """Get a specific report."""
        return self._reports.get(report_id)

    def get_reports(self, period: Optional[ReportPeriod] = None) -> list[PerformanceReport]:
        """Get all reports, optionally filtered by period."""
        reports = list(self._reports.values())
        if period:
            reports = [r for r in reports if r.period == period]
        return sorted(reports, key=lambda r: r.generated_at, reverse=True)

    def _refresh_if_needed(self):
        """Refresh KPI cache if stale."""
        if (datetime.utcnow() - self._last_refresh).total_seconds() > 300:
            self._refresh_kpis()

    def _refresh_kpis(self):
        """Refresh all KPI metrics."""
        self._kpi_cache.clear()

        for metric in self._response_time_analyzer.analyze():
            self._kpi_cache[metric.metric_id] = metric

        for metric in self._patrol_analyzer.analyze():
            self._kpi_cache[metric.metric_id] = metric

        for metric in self._traffic_analyzer.analyze():
            self._kpi_cache[metric.metric_id] = metric

        for metric in self._utility_analyzer.analyze():
            self._kpi_cache[metric.metric_id] = metric

        for metric in self._fire_ems_analyzer.analyze():
            self._kpi_cache[metric.metric_id] = metric

        self._last_refresh = datetime.utcnow()

    def get_statistics(self) -> dict[str, Any]:
        """Get KPI engine statistics."""
        self._refresh_if_needed()
        return {
            "total_kpis": len(self._kpi_cache),
            "total_reports": len(self._reports),
            "kpis_by_category": {
                cat.value: len([m for m in self._kpi_cache.values() if m.category == cat])
                for cat in KPICategory
            },
            "last_refresh": self._last_refresh.isoformat(),
        }


_kpi_engine: Optional[GovernanceKPIEngine] = None


def get_kpi_engine() -> GovernanceKPIEngine:
    """Get the singleton KPI engine instance."""
    global _kpi_engine
    if _kpi_engine is None:
        _kpi_engine = GovernanceKPIEngine()
    return _kpi_engine
