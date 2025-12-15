"""
Public Guardian API Router

Phase 36: Public Safety Guardian
REST API endpoints for transparency reports, community engagement,
trust scores, and public feedback.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.public_guardian.transparency_engine import (
    TransparencyReportEngine,
    ReportType,
    ReportPeriod,
)
from backend.app.public_guardian.community_engagement import (
    CommunityEngagementEngine,
    EventType,
    AlertType,
    AlertSeverity,
    NotificationChannel,
)
from backend.app.public_guardian.trust_score_engine import TrustScoreEngine
from backend.app.public_guardian.public_feedback_engine import (
    PublicFeedbackEngine,
    FeedbackType,
    FeedbackCategory,
    FeedbackStatus,
)
from backend.app.public_guardian.data_access_validator import (
    PublicDataAccessValidator,
    ComplianceFramework,
)


class APIRouter:
    def __init__(self, prefix: str = "", tags: Optional[List[str]] = None):
        self.prefix = prefix
        self.tags = tags or []
        self.routes = []

    def get(self, path: str):
        def decorator(func):
            self.routes.append(("GET", path, func))
            return func
        return decorator

    def post(self, path: str):
        def decorator(func):
            self.routes.append(("POST", path, func))
            return func
        return decorator


router = APIRouter(prefix="/api/public", tags=["public_guardian"])


class TransparencyReportRequest(BaseModel):
    report_type: str = Field(default="comprehensive", description="Type of report")
    period: str = Field(default="weekly", description="Report period")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class TransparencyReportResponse(BaseModel):
    report_id: str
    report_type: str
    period: str
    period_start: str
    period_end: str
    generated_at: str
    calls_for_service: Optional[Dict[str, Any]] = None
    response_times: Optional[Dict[str, Any]] = None
    use_of_force: Optional[Dict[str, Any]] = None
    safety_trends: Optional[Dict[str, Any]] = None
    heatmap: Optional[Dict[str, Any]] = None
    redactions_applied: List[str] = []
    compliance_frameworks: List[str] = []
    report_hash: str


class EventCreateRequest(BaseModel):
    name: str = Field(..., description="Event name")
    event_type: str = Field(..., description="Type of event")
    description: str = Field(default="", description="Event description")
    location: str = Field(..., description="Event location")
    address: str = Field(default="", description="Event address")
    start_time: datetime = Field(..., description="Event start time")
    end_time: Optional[datetime] = None
    expected_attendance: int = Field(default=0, description="Expected attendance")
    target_neighborhoods: List[str] = Field(default=[], description="Target neighborhoods")
    registration_required: bool = False
    registration_url: str = ""
    contact_email: str = ""
    contact_phone: str = ""


class EventResponse(BaseModel):
    event_id: str
    name: str
    event_type: str
    description: str
    location: str
    address: str
    start_time: str
    end_time: Optional[str] = None
    status: str
    organizer: str
    expected_attendance: int
    target_neighborhoods: List[str]


class AlertCreateRequest(BaseModel):
    alert_type: str = Field(..., description="Type of alert")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    severity: str = Field(default="medium", description="Alert severity")
    affected_areas: List[str] = Field(default=[], description="Affected areas")
    channels: List[str] = Field(default=["sms", "mobile_push"], description="Notification channels")
    end_time: Optional[datetime] = None


class AlertResponse(BaseModel):
    alert_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    affected_areas: List[str]
    active: bool
    channels: List[str]
    sent_count: int


class TrustScoreResponse(BaseModel):
    score_id: str
    overall_score: float
    trust_level: str
    calculated_at: str
    trend_vs_previous: float
    confidence: float
    fairness_audit_passed: bool
    bias_audit_passed: bool


class TrustScoreHistoryResponse(BaseModel):
    history_id: str
    start_date: str
    end_date: str
    average_score: float
    min_score: float
    max_score: float
    trend: float
    scores: List[Dict[str, Any]]


class FeedbackSubmitRequest(BaseModel):
    feedback_type: str = Field(..., description="Type of feedback")
    category: str = Field(..., description="Feedback category")
    title: str = Field(..., description="Feedback title")
    content: str = Field(..., description="Feedback content")
    neighborhood: str = Field(default="", description="Neighborhood")
    anonymous: bool = Field(default=True, description="Submit anonymously")
    contact_email: str = Field(default="", description="Contact email if not anonymous")
    tags: List[str] = Field(default=[], description="Tags")


class FeedbackResponse(BaseModel):
    feedback_id: str
    feedback_type: str
    category: str
    title: str
    sentiment: str
    sentiment_score: float
    status: str
    created_at: str


class FeedbackTrendsResponse(BaseModel):
    trends: List[Dict[str, Any]]
    common_concerns: List[Dict[str, Any]]
    sentiment_summary: Dict[str, Any]


transparency_engine = TransparencyReportEngine()
engagement_engine = CommunityEngagementEngine()
trust_engine = TrustScoreEngine()
feedback_engine = PublicFeedbackEngine()
validator = PublicDataAccessValidator()


@router.get("/transparency/report")
async def get_transparency_report(
    report_type: str = "comprehensive",
    period: str = "weekly",
) -> TransparencyReportResponse:
    rt = ReportType(report_type) if report_type in [e.value for e in ReportType] else ReportType.COMPREHENSIVE
    rp = ReportPeriod(period) if period in [e.value for e in ReportPeriod] else ReportPeriod.WEEKLY

    report = transparency_engine.generate_report(report_type=rt, period=rp)
    report_dict = report.to_dict()

    redacted_data, validation = validator.validate_and_redact(
        str(report_dict),
        data_type="transparency_report",
    )

    return TransparencyReportResponse(**report_dict)


@router.get("/transparency/weekly")
async def get_weekly_report() -> TransparencyReportResponse:
    report = transparency_engine.get_weekly_report()
    return TransparencyReportResponse(**report.to_dict())


@router.get("/transparency/monthly")
async def get_monthly_report() -> TransparencyReportResponse:
    report = transparency_engine.get_monthly_report()
    return TransparencyReportResponse(**report.to_dict())


@router.get("/transparency/quarterly")
async def get_quarterly_report() -> TransparencyReportResponse:
    report = transparency_engine.get_quarterly_report()
    return TransparencyReportResponse(**report.to_dict())


@router.get("/transparency/export/json/{report_id}")
async def export_report_json(report_id: str) -> Dict[str, Any]:
    json_data = transparency_engine.export_to_json(report_id)
    if json_data:
        return {"success": True, "data": json_data}
    return {"success": False, "error": "Report not found"}


@router.get("/transparency/export/pdf/{report_id}")
async def export_report_pdf(report_id: str) -> Dict[str, Any]:
    pdf_data = transparency_engine.export_to_pdf_data(report_id)
    if pdf_data:
        return {"success": True, "data": pdf_data}
    return {"success": False, "error": "Report not found"}


@router.get("/community/events")
async def get_community_events(limit: int = 10) -> Dict[str, Any]:
    events = engagement_engine.get_upcoming_events(limit=limit)
    return {
        "events": [e.to_dict() for e in events],
        "total": len(events),
    }


@router.post("/community/event")
async def create_community_event(request: EventCreateRequest) -> EventResponse:
    et = EventType(request.event_type) if request.event_type in [e.value for e in EventType] else EventType.OTHER

    event = engagement_engine.create_event(
        name=request.name,
        event_type=et,
        description=request.description,
        location=request.location,
        address=request.address,
        start_time=request.start_time,
        end_time=request.end_time,
        expected_attendance=request.expected_attendance,
        target_neighborhoods=request.target_neighborhoods,
        registration_required=request.registration_required,
        registration_url=request.registration_url,
        contact_email=request.contact_email,
        contact_phone=request.contact_phone,
    )

    return EventResponse(
        event_id=event.event_id,
        name=event.name,
        event_type=event.event_type.value,
        description=event.description,
        location=event.location,
        address=event.address,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat() if event.end_time else None,
        status=event.status.value,
        organizer=event.organizer,
        expected_attendance=event.expected_attendance,
        target_neighborhoods=event.target_neighborhoods,
    )


@router.get("/community/event/{event_id}")
async def get_community_event(event_id: str) -> Dict[str, Any]:
    event = engagement_engine.get_event(event_id)
    if event:
        return {"success": True, "event": event.to_dict()}
    return {"success": False, "error": "Event not found"}


@router.post("/community/event/{event_id}/cancel")
async def cancel_community_event(event_id: str, reason: str = "") -> Dict[str, Any]:
    success = engagement_engine.cancel_event(event_id, reason)
    return {"success": success}


@router.get("/community/alerts")
async def get_community_alerts() -> Dict[str, Any]:
    alerts = engagement_engine.get_active_alerts()
    return {
        "alerts": [a.to_dict() for a in alerts],
        "total": len(alerts),
    }


@router.post("/community/alert")
async def create_community_alert(request: AlertCreateRequest) -> AlertResponse:
    at = AlertType(request.alert_type) if request.alert_type in [e.value for e in AlertType] else AlertType.SAFETY_ALERT
    sev = AlertSeverity(request.severity) if request.severity in [e.value for e in AlertSeverity] else AlertSeverity.MEDIUM
    channels = [NotificationChannel(c) for c in request.channels if c in [e.value for e in NotificationChannel]]

    alert = engagement_engine.create_alert(
        alert_type=at,
        title=request.title,
        message=request.message,
        severity=sev,
        affected_areas=request.affected_areas,
        channels=channels or [NotificationChannel.SMS, NotificationChannel.MOBILE_PUSH],
        end_time=request.end_time,
    )

    return AlertResponse(
        alert_id=alert.alert_id,
        alert_type=alert.alert_type.value,
        severity=alert.severity.value,
        title=alert.title,
        message=alert.message,
        affected_areas=alert.affected_areas,
        active=alert.active,
        channels=[c.value for c in alert.channels],
        sent_count=alert.sent_count,
    )


@router.post("/community/alert/{alert_id}/deactivate")
async def deactivate_community_alert(alert_id: str) -> Dict[str, Any]:
    success = engagement_engine.deactivate_alert(alert_id)
    return {"success": success}


@router.get("/trust-score/current")
async def get_current_trust_score() -> TrustScoreResponse:
    score = trust_engine.get_current_score()
    if score:
        return TrustScoreResponse(
            score_id=score.score_id,
            overall_score=score.overall_score,
            trust_level=score.trust_level.value,
            calculated_at=score.calculated_at.isoformat(),
            trend_vs_previous=score.trend_vs_previous,
            confidence=score.confidence,
            fairness_audit_passed=score.fairness_audit_passed,
            bias_audit_passed=score.bias_audit_passed,
        )
    return TrustScoreResponse(
        score_id="",
        overall_score=0,
        trust_level="unknown",
        calculated_at="",
        trend_vs_previous=0,
        confidence=0,
        fairness_audit_passed=False,
        bias_audit_passed=False,
    )


@router.get("/trust-score/history")
async def get_trust_score_history(
    days: int = 30,
    limit: int = 30,
) -> TrustScoreHistoryResponse:
    history = trust_engine.get_score_history(limit=limit)
    return TrustScoreHistoryResponse(
        history_id=history.history_id,
        start_date=history.start_date.isoformat(),
        end_date=history.end_date.isoformat(),
        average_score=history.average_score,
        min_score=history.min_score,
        max_score=history.max_score,
        trend=history.trend,
        scores=[s.to_dict() for s in history.scores],
    )


@router.get("/trust-score/breakdown")
async def get_trust_score_breakdown() -> Dict[str, Any]:
    return trust_engine.get_metric_breakdown()


@router.get("/trust-score/neighborhoods")
async def get_neighborhood_trust_scores() -> Dict[str, Any]:
    neighborhoods = trust_engine.get_all_neighborhood_scores()
    return {
        "neighborhoods": [n.to_dict() for n in neighborhoods],
        "total": len(neighborhoods),
    }


@router.get("/trust-score/neighborhood/{neighborhood_id}")
async def get_neighborhood_trust_score(neighborhood_id: str) -> Dict[str, Any]:
    neighborhood = trust_engine.get_neighborhood_score(neighborhood_id)
    if neighborhood:
        return {"success": True, "neighborhood": neighborhood.to_dict()}
    return {"success": False, "error": "Neighborhood not found"}


@router.get("/trust-score/fairness-audit")
async def run_fairness_audit() -> Dict[str, Any]:
    return trust_engine.run_fairness_audit()


@router.get("/trust-score/bias-audit")
async def run_bias_audit() -> Dict[str, Any]:
    return trust_engine.run_bias_audit()


@router.post("/feedback")
async def submit_feedback(request: FeedbackSubmitRequest) -> FeedbackResponse:
    ft = FeedbackType(request.feedback_type) if request.feedback_type in [e.value for e in FeedbackType] else FeedbackType.GENERAL
    fc = FeedbackCategory(request.category) if request.category in [e.value for e in FeedbackCategory] else FeedbackCategory.OTHER

    feedback = feedback_engine.submit_feedback(
        feedback_type=ft,
        category=fc,
        title=request.title,
        content=request.content,
        neighborhood=request.neighborhood,
        anonymous=request.anonymous,
        contact_email=request.contact_email,
        tags=request.tags,
    )

    return FeedbackResponse(
        feedback_id=feedback.feedback_id,
        feedback_type=feedback.feedback_type.value,
        category=feedback.category.value,
        title=feedback.title,
        sentiment=feedback.sentiment.value,
        sentiment_score=feedback.sentiment_score,
        status=feedback.status.value,
        created_at=feedback.created_at.isoformat(),
    )


@router.get("/feedback/trends")
async def get_feedback_trends(period_days: int = 30) -> FeedbackTrendsResponse:
    trends = feedback_engine.detect_trends(period_days=period_days)
    common_concerns = feedback_engine.get_common_concerns()
    sentiment_summary = feedback_engine.get_sentiment_summary()

    return FeedbackTrendsResponse(
        trends=[t.to_dict() for t in trends],
        common_concerns=common_concerns,
        sentiment_summary=sentiment_summary,
    )


@router.get("/feedback/recent")
async def get_recent_feedback(limit: int = 20) -> Dict[str, Any]:
    feedback_list = feedback_engine.get_recent_feedback(limit=limit)
    return {
        "feedback": [f.to_dict() for f in feedback_list],
        "total": len(feedback_list),
    }


@router.get("/feedback/neighborhood/{neighborhood}")
async def get_neighborhood_feedback(neighborhood: str) -> Dict[str, Any]:
    insight = feedback_engine.get_neighborhood_insight(neighborhood)
    return {"success": True, "insight": insight.to_dict()}


@router.get("/feedback/sentiment")
async def get_sentiment_summary() -> Dict[str, Any]:
    return feedback_engine.get_sentiment_summary()


@router.post("/feedback/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: str,
    status: str,
    response: str = "",
) -> Dict[str, Any]:
    fs = FeedbackStatus(status) if status in [e.value for e in FeedbackStatus] else FeedbackStatus.RECEIVED
    feedback = feedback_engine.update_feedback_status(feedback_id, fs, response)
    if feedback:
        return {"success": True, "feedback": feedback.to_dict()}
    return {"success": False, "error": "Feedback not found"}


@router.get("/compliance/check")
async def check_compliance(data: str, data_type: str = "general") -> Dict[str, Any]:
    result = validator.check_public_release_eligibility(data, data_type)
    return result


@router.post("/compliance/redact")
async def redact_data(data: str) -> Dict[str, Any]:
    redacted, result = validator.validate_and_redact(data)
    return {
        "redacted_data": redacted,
        "validation": result.to_dict(),
    }


@router.get("/compliance/rules")
async def get_compliance_rules() -> Dict[str, Any]:
    rules = validator.get_all_rules()
    return {
        "rules": [r.to_dict() for r in rules],
        "total": len(rules),
    }


@router.get("/compliance/summary")
async def get_compliance_summary() -> Dict[str, Any]:
    return validator.get_compliance_summary()


@router.get("/statistics")
async def get_public_guardian_statistics() -> Dict[str, Any]:
    return {
        "transparency": transparency_engine.get_statistics(),
        "engagement": engagement_engine.get_statistics(),
        "trust_score": trust_engine.get_statistics(),
        "feedback": feedback_engine.get_statistics(),
        "compliance": validator.get_statistics(),
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "public_guardian",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
