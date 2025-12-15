"""
Transparency Report Engine

Phase 36: Public Safety Guardian
Generates non-sensitive transparency dashboards and reports for public consumption.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json
import uuid


class ReportType(Enum):
    CALLS_FOR_SERVICE = "calls_for_service"
    RESPONSE_TIMES = "response_times"
    USE_OF_FORCE = "use_of_force"
    SAFETY_TRENDS = "safety_trends"
    HEATMAP = "heatmap"
    COMPREHENSIVE = "comprehensive"


class ReportPeriod(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class CallCategory(Enum):
    EMERGENCY = "emergency"
    NON_EMERGENCY = "non_emergency"
    TRAFFIC = "traffic"
    PROPERTY_CRIME = "property_crime"
    VIOLENT_CRIME = "violent_crime"
    DOMESTIC = "domestic"
    MENTAL_HEALTH = "mental_health"
    COMMUNITY_SERVICE = "community_service"
    WELFARE_CHECK = "welfare_check"
    OTHER = "other"


@dataclass
class CallsForServiceSummary:
    period_start: datetime
    period_end: datetime
    total_calls: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    by_day_of_week: Dict[str, int] = field(default_factory=dict)
    by_hour: Dict[int, int] = field(default_factory=dict)
    average_daily: float = 0.0
    trend_vs_previous: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_calls": self.total_calls,
            "by_category": self.by_category,
            "by_day_of_week": self.by_day_of_week,
            "by_hour": self.by_hour,
            "average_daily": self.average_daily,
            "trend_vs_previous": self.trend_vs_previous,
        }


@dataclass
class ResponseTimeSummary:
    period_start: datetime
    period_end: datetime
    average_response_time_seconds: float = 0.0
    median_response_time_seconds: float = 0.0
    emergency_avg_seconds: float = 0.0
    non_emergency_avg_seconds: float = 0.0
    by_priority: Dict[str, float] = field(default_factory=dict)
    by_district: Dict[str, float] = field(default_factory=dict)
    trend_vs_previous: float = 0.0
    target_met_percentage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "average_response_time_seconds": self.average_response_time_seconds,
            "median_response_time_seconds": self.median_response_time_seconds,
            "emergency_avg_seconds": self.emergency_avg_seconds,
            "non_emergency_avg_seconds": self.non_emergency_avg_seconds,
            "by_priority": self.by_priority,
            "by_district": self.by_district,
            "trend_vs_previous": self.trend_vs_previous,
            "target_met_percentage": self.target_met_percentage,
        }


@dataclass
class UseOfForceSummary:
    period_start: datetime
    period_end: datetime
    total_incidents: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_outcome: Dict[str, int] = field(default_factory=dict)
    de_escalation_success_rate: float = 0.0
    complaints_filed: int = 0
    complaints_sustained: int = 0
    trend_vs_previous: float = 0.0
    per_1000_contacts: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_incidents": self.total_incidents,
            "by_type": self.by_type,
            "by_outcome": self.by_outcome,
            "de_escalation_success_rate": self.de_escalation_success_rate,
            "complaints_filed": self.complaints_filed,
            "complaints_sustained": self.complaints_sustained,
            "trend_vs_previous": self.trend_vs_previous,
            "per_1000_contacts": self.per_1000_contacts,
        }


@dataclass
class SafetyTrendSummary:
    period_start: datetime
    period_end: datetime
    overall_crime_index: float = 0.0
    violent_crime_trend: float = 0.0
    property_crime_trend: float = 0.0
    by_neighborhood: Dict[str, float] = field(default_factory=dict)
    improvement_areas: List[str] = field(default_factory=list)
    concern_areas: List[str] = field(default_factory=list)
    year_over_year_change: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "overall_crime_index": self.overall_crime_index,
            "violent_crime_trend": self.violent_crime_trend,
            "property_crime_trend": self.property_crime_trend,
            "by_neighborhood": self.by_neighborhood,
            "improvement_areas": self.improvement_areas,
            "concern_areas": self.concern_areas,
            "year_over_year_change": self.year_over_year_change,
        }


@dataclass
class HeatmapCell:
    grid_id: str
    latitude_center: float
    longitude_center: float
    activity_level: str
    call_count: int
    blur_radius: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_id": self.grid_id,
            "latitude_center": round(self.latitude_center, 3),
            "longitude_center": round(self.longitude_center, 3),
            "activity_level": self.activity_level,
            "call_count": self.call_count,
            "blur_radius": self.blur_radius,
        }


@dataclass
class HeatmapSummary:
    period_start: datetime
    period_end: datetime
    grid_size_meters: int = 500
    cells: List[HeatmapCell] = field(default_factory=list)
    total_cells: int = 0
    high_activity_cells: int = 0
    low_activity_cells: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "grid_size_meters": self.grid_size_meters,
            "cells": [c.to_dict() for c in self.cells],
            "total_cells": self.total_cells,
            "high_activity_cells": self.high_activity_cells,
            "low_activity_cells": self.low_activity_cells,
        }


@dataclass
class TransparencyReport:
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_type: ReportType = ReportType.COMPREHENSIVE
    period: ReportPeriod = ReportPeriod.WEEKLY
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    calls_for_service: Optional[CallsForServiceSummary] = None
    response_times: Optional[ResponseTimeSummary] = None
    use_of_force: Optional[UseOfForceSummary] = None
    safety_trends: Optional[SafetyTrendSummary] = None
    heatmap: Optional[HeatmapSummary] = None
    redactions_applied: List[str] = field(default_factory=list)
    compliance_frameworks: List[str] = field(default_factory=list)
    report_hash: str = ""

    def __post_init__(self):
        if not self.report_hash:
            self.report_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.report_id}{self.report_type.value}{self.period.value}{self.generated_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "period": self.period.value,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "generated_at": self.generated_at.isoformat(),
            "calls_for_service": self.calls_for_service.to_dict() if self.calls_for_service else None,
            "response_times": self.response_times.to_dict() if self.response_times else None,
            "use_of_force": self.use_of_force.to_dict() if self.use_of_force else None,
            "safety_trends": self.safety_trends.to_dict() if self.safety_trends else None,
            "heatmap": self.heatmap.to_dict() if self.heatmap else None,
            "redactions_applied": self.redactions_applied,
            "compliance_frameworks": self.compliance_frameworks,
            "report_hash": self.report_hash,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class TransparencyReportEngine:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.reports: Dict[str, TransparencyReport] = {}
        self.statistics = {
            "reports_generated": 0,
            "weekly_reports": 0,
            "monthly_reports": 0,
            "quarterly_reports": 0,
            "pdf_exports": 0,
            "json_exports": 0,
            "redactions_applied": 0,
        }
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        self.riviera_beach_neighborhoods = [
            "Downtown Riviera Beach",
            "Singer Island",
            "West Riviera Beach",
            "Port of Palm Beach Area",
            "Riviera Beach Heights",
        ]
        self.call_categories = [c.value for c in CallCategory]

    def generate_report(
        self,
        report_type: ReportType = ReportType.COMPREHENSIVE,
        period: ReportPeriod = ReportPeriod.WEEKLY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> TransparencyReport:
        now = datetime.utcnow()
        if not end_date:
            end_date = now
        if not start_date:
            if period == ReportPeriod.DAILY:
                start_date = end_date - timedelta(days=1)
            elif period == ReportPeriod.WEEKLY:
                start_date = end_date - timedelta(weeks=1)
            elif period == ReportPeriod.MONTHLY:
                start_date = end_date - timedelta(days=30)
            elif period == ReportPeriod.QUARTERLY:
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=365)

        report = TransparencyReport(
            report_type=report_type,
            period=period,
            period_start=start_date,
            period_end=end_date,
            compliance_frameworks=["CJIS", "VAWA", "HIPAA", "Florida Public Records"],
        )

        if report_type in [ReportType.CALLS_FOR_SERVICE, ReportType.COMPREHENSIVE]:
            report.calls_for_service = self._generate_calls_summary(start_date, end_date)
            report.redactions_applied.append("juvenile_identifiers_removed")

        if report_type in [ReportType.RESPONSE_TIMES, ReportType.COMPREHENSIVE]:
            report.response_times = self._generate_response_summary(start_date, end_date)

        if report_type in [ReportType.USE_OF_FORCE, ReportType.COMPREHENSIVE]:
            report.use_of_force = self._generate_uof_summary(start_date, end_date)
            report.redactions_applied.append("officer_names_redacted")
            report.redactions_applied.append("victim_info_redacted")

        if report_type in [ReportType.SAFETY_TRENDS, ReportType.COMPREHENSIVE]:
            report.safety_trends = self._generate_safety_summary(start_date, end_date)

        if report_type in [ReportType.HEATMAP, ReportType.COMPREHENSIVE]:
            report.heatmap = self._generate_heatmap_summary(start_date, end_date)
            report.redactions_applied.append("exact_locations_blurred")
            report.redactions_applied.append("dv_locations_excluded")

        self.reports[report.report_id] = report
        self.statistics["reports_generated"] += 1
        self.statistics[f"{period.value}_reports"] = self.statistics.get(f"{period.value}_reports", 0) + 1
        self.statistics["redactions_applied"] += len(report.redactions_applied)

        return report

    def _generate_calls_summary(
        self, start_date: datetime, end_date: datetime
    ) -> CallsForServiceSummary:
        days = (end_date - start_date).days or 1
        total_calls = days * 45

        by_category = {
            "emergency": int(total_calls * 0.15),
            "non_emergency": int(total_calls * 0.25),
            "traffic": int(total_calls * 0.12),
            "property_crime": int(total_calls * 0.10),
            "violent_crime": int(total_calls * 0.05),
            "domestic": int(total_calls * 0.08),
            "mental_health": int(total_calls * 0.06),
            "community_service": int(total_calls * 0.10),
            "welfare_check": int(total_calls * 0.05),
            "other": int(total_calls * 0.04),
        }

        by_day = {
            "Monday": int(total_calls * 0.14),
            "Tuesday": int(total_calls * 0.13),
            "Wednesday": int(total_calls * 0.14),
            "Thursday": int(total_calls * 0.14),
            "Friday": int(total_calls * 0.16),
            "Saturday": int(total_calls * 0.15),
            "Sunday": int(total_calls * 0.14),
        }

        by_hour = {h: int(total_calls * (0.03 if 2 <= h <= 6 else 0.05)) for h in range(24)}

        return CallsForServiceSummary(
            period_start=start_date,
            period_end=end_date,
            total_calls=total_calls,
            by_category=by_category,
            by_day_of_week=by_day,
            by_hour=by_hour,
            average_daily=total_calls / days,
            trend_vs_previous=-3.2,
        )

    def _generate_response_summary(
        self, start_date: datetime, end_date: datetime
    ) -> ResponseTimeSummary:
        return ResponseTimeSummary(
            period_start=start_date,
            period_end=end_date,
            average_response_time_seconds=420,
            median_response_time_seconds=360,
            emergency_avg_seconds=240,
            non_emergency_avg_seconds=720,
            by_priority={
                "priority_1": 180,
                "priority_2": 360,
                "priority_3": 600,
                "priority_4": 900,
            },
            by_district={
                "Downtown": 300,
                "Singer Island": 420,
                "West": 480,
                "Port Area": 360,
                "Heights": 450,
            },
            trend_vs_previous=-5.5,
            target_met_percentage=87.3,
        )

    def _generate_uof_summary(
        self, start_date: datetime, end_date: datetime
    ) -> UseOfForceSummary:
        days = (end_date - start_date).days or 1
        base_incidents = max(1, days // 10)

        return UseOfForceSummary(
            period_start=start_date,
            period_end=end_date,
            total_incidents=base_incidents,
            by_type={
                "verbal_commands": int(base_incidents * 0.4),
                "physical_control": int(base_incidents * 0.3),
                "taser": int(base_incidents * 0.15),
                "oc_spray": int(base_incidents * 0.1),
                "firearm_displayed": int(base_incidents * 0.05),
            },
            by_outcome={
                "no_injury": int(base_incidents * 0.7),
                "minor_injury": int(base_incidents * 0.2),
                "medical_attention": int(base_incidents * 0.1),
            },
            de_escalation_success_rate=78.5,
            complaints_filed=max(0, base_incidents // 5),
            complaints_sustained=0,
            trend_vs_previous=-8.2,
            per_1000_contacts=1.2,
        )

    def _generate_safety_summary(
        self, start_date: datetime, end_date: datetime
    ) -> SafetyTrendSummary:
        return SafetyTrendSummary(
            period_start=start_date,
            period_end=end_date,
            overall_crime_index=72.5,
            violent_crime_trend=-4.2,
            property_crime_trend=-2.8,
            by_neighborhood={
                "Downtown Riviera Beach": 68.0,
                "Singer Island": 85.0,
                "West Riviera Beach": 65.0,
                "Port of Palm Beach Area": 78.0,
                "Riviera Beach Heights": 70.0,
            },
            improvement_areas=["Singer Island", "Port of Palm Beach Area"],
            concern_areas=["West Riviera Beach"],
            year_over_year_change=-6.5,
        )

    def _generate_heatmap_summary(
        self, start_date: datetime, end_date: datetime
    ) -> HeatmapSummary:
        cells = []
        base_lat, base_lon = 26.7753, -80.0586

        for i in range(5):
            for j in range(5):
                activity = "low" if (i + j) % 3 == 0 else "medium" if (i + j) % 2 == 0 else "high"
                cells.append(
                    HeatmapCell(
                        grid_id=f"GRID-{i}-{j}",
                        latitude_center=base_lat + (i * 0.01),
                        longitude_center=base_lon + (j * 0.01),
                        activity_level=activity,
                        call_count=10 + (i * j),
                        blur_radius=0.5,
                    )
                )

        high_count = sum(1 for c in cells if c.activity_level == "high")
        low_count = sum(1 for c in cells if c.activity_level == "low")

        return HeatmapSummary(
            period_start=start_date,
            period_end=end_date,
            grid_size_meters=500,
            cells=cells,
            total_cells=len(cells),
            high_activity_cells=high_count,
            low_activity_cells=low_count,
        )

    def get_weekly_report(self) -> TransparencyReport:
        return self.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.WEEKLY,
        )

    def get_monthly_report(self) -> TransparencyReport:
        return self.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.MONTHLY,
        )

    def get_quarterly_report(self) -> TransparencyReport:
        return self.generate_report(
            report_type=ReportType.COMPREHENSIVE,
            period=ReportPeriod.QUARTERLY,
        )

    def export_to_json(self, report_id: str) -> Optional[str]:
        report = self.reports.get(report_id)
        if report:
            self.statistics["json_exports"] += 1
            return report.to_json()
        return None

    def export_to_pdf_data(self, report_id: str) -> Optional[Dict[str, Any]]:
        report = self.reports.get(report_id)
        if report:
            self.statistics["pdf_exports"] += 1
            return {
                "title": f"Transparency Report - {report.period.value.title()}",
                "generated_at": report.generated_at.isoformat(),
                "period": f"{report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}",
                "content": report.to_dict(),
                "footer": "This report has been automatically redacted for public release.",
            }
        return None

    def get_report(self, report_id: str) -> Optional[TransparencyReport]:
        return self.reports.get(report_id)

    def get_recent_reports(self, limit: int = 10) -> List[TransparencyReport]:
        sorted_reports = sorted(
            self.reports.values(),
            key=lambda r: r.generated_at,
            reverse=True,
        )
        return sorted_reports[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "total_reports_stored": len(self.reports),
        }
