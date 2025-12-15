"""
Community Engagement Engine

Phase 36: Public Safety Guardian
Tracks community events and manages public notifications for safety alerts,
town halls, and community engagement activities.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json
import uuid


class EventType(Enum):
    TOWN_HALL = "town_hall"
    ADVISORY_BOARD = "advisory_board"
    COMMUNITY_MEETING = "community_meeting"
    SAFETY_WORKSHOP = "safety_workshop"
    YOUTH_PROGRAM = "youth_program"
    NEIGHBORHOOD_WATCH = "neighborhood_watch"
    POLICE_OPEN_HOUSE = "police_open_house"
    COFFEE_WITH_COPS = "coffee_with_cops"
    NATIONAL_NIGHT_OUT = "national_night_out"
    OTHER = "other"


class AlertType(Enum):
    SAFETY_ALERT = "safety_alert"
    AMBER_ALERT = "amber_alert"
    SILVER_ALERT = "silver_alert"
    WEATHER_EMERGENCY = "weather_emergency"
    TRAFFIC_ADVISORY = "traffic_advisory"
    COMMUNITY_NOTICE = "community_notice"
    CRIME_PREVENTION = "crime_prevention"
    PUBLIC_SAFETY = "public_safety"


class NotificationChannel(Enum):
    SMS = "sms"
    EMAIL = "email"
    MOBILE_PUSH = "mobile_push"
    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    EMERGENCY_BROADCAST = "emergency_broadcast"


class EventStatus(Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class AlertSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CommunityEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    event_type: EventType = EventType.COMMUNITY_MEETING
    description: str = ""
    location: str = ""
    address: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: EventStatus = EventStatus.SCHEDULED
    organizer: str = "Riviera Beach Police Department"
    contact_email: str = ""
    contact_phone: str = ""
    expected_attendance: int = 0
    actual_attendance: int = 0
    target_neighborhoods: List[str] = field(default_factory=list)
    registration_required: bool = False
    registration_url: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "name": self.name,
            "event_type": self.event_type.value,
            "description": self.description,
            "location": self.location,
            "address": self.address,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "organizer": self.organizer,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "expected_attendance": self.expected_attendance,
            "actual_attendance": self.actual_attendance,
            "target_neighborhoods": self.target_neighborhoods,
            "registration_required": self.registration_required,
            "registration_url": self.registration_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class SafetyAlert:
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: AlertType = AlertType.SAFETY_ALERT
    severity: AlertSeverity = AlertSeverity.MEDIUM
    title: str = ""
    message: str = ""
    affected_areas: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    active: bool = True
    channels: List[NotificationChannel] = field(default_factory=list)
    sent_count: int = 0
    acknowledged_count: int = 0
    source: str = "RBPD"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    alert_hash: str = ""

    def __post_init__(self):
        if not self.alert_hash:
            self.alert_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        content = f"{self.alert_id}{self.title}{self.created_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "affected_areas": self.affected_areas,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "active": self.active,
            "channels": [c.value for c in self.channels],
            "sent_count": self.sent_count,
            "acknowledged_count": self.acknowledged_count,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "alert_hash": self.alert_hash,
        }


@dataclass
class NotificationTemplate:
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    template_type: str = ""
    subject: str = ""
    body: str = ""
    channels: List[NotificationChannel] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "template_type": self.template_type,
            "subject": self.subject,
            "body": self.body,
            "channels": [c.value for c in self.channels],
            "variables": self.variables,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
        }

    def render(self, variables: Dict[str, str]) -> Dict[str, str]:
        rendered_subject = self.subject
        rendered_body = self.body
        for key, value in variables.items():
            rendered_subject = rendered_subject.replace(f"{{{{{key}}}}}", value)
            rendered_body = rendered_body.replace(f"{{{{{key}}}}}", value)
        return {"subject": rendered_subject, "body": rendered_body}


class CommunityEngagementEngine:
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
        self.events: Dict[str, CommunityEvent] = {}
        self.alerts: Dict[str, SafetyAlert] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.statistics = {
            "events_created": 0,
            "events_completed": 0,
            "total_attendance": 0,
            "alerts_sent": 0,
            "notifications_delivered": 0,
            "sms_sent": 0,
            "emails_sent": 0,
            "push_notifications_sent": 0,
        }
        self._initialize_templates()
        self._initialize_sample_events()

    def _initialize_templates(self):
        templates = [
            NotificationTemplate(
                name="Town Hall Announcement",
                template_type="event",
                subject="Upcoming Town Hall Meeting - {{date}}",
                body="Join us for a community town hall meeting on {{date}} at {{location}}. Topics include {{topics}}. Your voice matters!",
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
                variables=["date", "location", "topics"],
            ),
            NotificationTemplate(
                name="Advisory Board Meeting",
                template_type="event",
                subject="Police Advisory Board Meeting - {{date}}",
                body="The Riviera Beach Police Advisory Board will meet on {{date}} at {{location}}. Public attendance is welcome.",
                channels=[NotificationChannel.EMAIL, NotificationChannel.WEBSITE],
                variables=["date", "location"],
            ),
            NotificationTemplate(
                name="Safety Alert",
                template_type="alert",
                subject="Safety Alert: {{title}}",
                body="{{message}} Affected areas: {{areas}}. Stay safe and report any suspicious activity to RBPD.",
                channels=[NotificationChannel.SMS, NotificationChannel.MOBILE_PUSH],
                variables=["title", "message", "areas"],
            ),
            NotificationTemplate(
                name="Missing Child Alert",
                template_type="amber",
                subject="AMBER ALERT: Missing Child - {{name}}",
                body="AMBER ALERT: {{name}}, {{age}} years old, last seen {{location}} at {{time}}. Description: {{description}}. If seen, call 911 immediately.",
                channels=[NotificationChannel.SMS, NotificationChannel.MOBILE_PUSH, NotificationChannel.EMERGENCY_BROADCAST],
                variables=["name", "age", "location", "time", "description"],
            ),
            NotificationTemplate(
                name="Weather Emergency",
                template_type="weather",
                subject="Weather Emergency: {{type}}",
                body="{{type}} warning for Riviera Beach. {{instructions}}. Monitor local news for updates.",
                channels=[NotificationChannel.SMS, NotificationChannel.MOBILE_PUSH, NotificationChannel.EMERGENCY_BROADCAST],
                variables=["type", "instructions"],
            ),
        ]
        for template in templates:
            self.templates[template.template_id] = template

    def _initialize_sample_events(self):
        now = datetime.utcnow()
        sample_events = [
            CommunityEvent(
                name="Monthly Town Hall Meeting",
                event_type=EventType.TOWN_HALL,
                description="Monthly community town hall to discuss public safety concerns and initiatives.",
                location="Riviera Beach City Hall",
                address="600 W Blue Heron Blvd, Riviera Beach, FL 33404",
                start_time=now + timedelta(days=7),
                end_time=now + timedelta(days=7, hours=2),
                expected_attendance=100,
                target_neighborhoods=["Downtown Riviera Beach", "West Riviera Beach"],
            ),
            CommunityEvent(
                name="Police Advisory Board Meeting",
                event_type=EventType.ADVISORY_BOARD,
                description="Quarterly meeting of the Police Advisory Board.",
                location="RBPD Headquarters",
                address="600 W Blue Heron Blvd, Riviera Beach, FL 33404",
                start_time=now + timedelta(days=14),
                end_time=now + timedelta(days=14, hours=2),
                expected_attendance=50,
            ),
            CommunityEvent(
                name="Coffee with Cops",
                event_type=EventType.COFFEE_WITH_COPS,
                description="Informal community engagement event at local coffee shop.",
                location="Starbucks - Singer Island",
                address="2401 PGA Blvd, Palm Beach Gardens, FL 33410",
                start_time=now + timedelta(days=3),
                end_time=now + timedelta(days=3, hours=2),
                expected_attendance=30,
                target_neighborhoods=["Singer Island"],
            ),
        ]
        for event in sample_events:
            self.events[event.event_id] = event

    def create_event(
        self,
        name: str,
        event_type: EventType,
        description: str,
        location: str,
        address: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        expected_attendance: int = 0,
        target_neighborhoods: Optional[List[str]] = None,
        registration_required: bool = False,
        registration_url: str = "",
        contact_email: str = "",
        contact_phone: str = "",
    ) -> CommunityEvent:
        event = CommunityEvent(
            name=name,
            event_type=event_type,
            description=description,
            location=location,
            address=address,
            start_time=start_time,
            end_time=end_time,
            expected_attendance=expected_attendance,
            target_neighborhoods=target_neighborhoods or [],
            registration_required=registration_required,
            registration_url=registration_url,
            contact_email=contact_email,
            contact_phone=contact_phone,
        )
        self.events[event.event_id] = event
        self.statistics["events_created"] += 1
        return event

    def update_event(
        self,
        event_id: str,
        **kwargs,
    ) -> Optional[CommunityEvent]:
        event = self.events.get(event_id)
        if not event:
            return None
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
        event.updated_at = datetime.utcnow()
        return event

    def cancel_event(self, event_id: str, reason: str = "") -> bool:
        event = self.events.get(event_id)
        if event:
            event.status = EventStatus.CANCELLED
            event.updated_at = datetime.utcnow()
            return True
        return False

    def complete_event(self, event_id: str, actual_attendance: int = 0) -> bool:
        event = self.events.get(event_id)
        if event:
            event.status = EventStatus.COMPLETED
            event.actual_attendance = actual_attendance
            event.updated_at = datetime.utcnow()
            self.statistics["events_completed"] += 1
            self.statistics["total_attendance"] += actual_attendance
            return True
        return False

    def get_event(self, event_id: str) -> Optional[CommunityEvent]:
        return self.events.get(event_id)

    def get_upcoming_events(self, limit: int = 10) -> List[CommunityEvent]:
        now = datetime.utcnow()
        upcoming = [
            e for e in self.events.values()
            if e.start_time > now and e.status in [EventStatus.SCHEDULED, EventStatus.CONFIRMED]
        ]
        return sorted(upcoming, key=lambda e: e.start_time)[:limit]

    def get_events_by_type(self, event_type: EventType) -> List[CommunityEvent]:
        return [e for e in self.events.values() if e.event_type == event_type]

    def get_events_by_neighborhood(self, neighborhood: str) -> List[CommunityEvent]:
        return [
            e for e in self.events.values()
            if neighborhood in e.target_neighborhoods or not e.target_neighborhoods
        ]

    def create_alert(
        self,
        alert_type: AlertType,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        affected_areas: Optional[List[str]] = None,
        channels: Optional[List[NotificationChannel]] = None,
        end_time: Optional[datetime] = None,
    ) -> SafetyAlert:
        alert = SafetyAlert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            affected_areas=affected_areas or [],
            channels=channels or [NotificationChannel.SMS, NotificationChannel.MOBILE_PUSH],
            end_time=end_time,
        )
        self.alerts[alert.alert_id] = alert
        self.statistics["alerts_sent"] += 1
        return alert

    def deactivate_alert(self, alert_id: str) -> bool:
        alert = self.alerts.get(alert_id)
        if alert:
            alert.active = False
            alert.updated_at = datetime.utcnow()
            return True
        return False

    def get_alert(self, alert_id: str) -> Optional[SafetyAlert]:
        return self.alerts.get(alert_id)

    def get_active_alerts(self) -> List[SafetyAlert]:
        return [a for a in self.alerts.values() if a.active]

    def get_alerts_by_type(self, alert_type: AlertType) -> List[SafetyAlert]:
        return [a for a in self.alerts.values() if a.alert_type == alert_type]

    def send_notification(
        self,
        template_id: str,
        variables: Dict[str, str],
        channels: Optional[List[NotificationChannel]] = None,
        recipients: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        template = self.templates.get(template_id)
        if not template:
            return {"success": False, "error": "Template not found"}

        rendered = template.render(variables)
        target_channels = channels or template.channels

        result = {
            "success": True,
            "template_id": template_id,
            "rendered_subject": rendered["subject"],
            "rendered_body": rendered["body"],
            "channels_used": [c.value for c in target_channels],
            "sent_count": 0,
        }

        for channel in target_channels:
            if channel == NotificationChannel.SMS:
                self.statistics["sms_sent"] += 1
                result["sent_count"] += 1
            elif channel == NotificationChannel.EMAIL:
                self.statistics["emails_sent"] += 1
                result["sent_count"] += 1
            elif channel == NotificationChannel.MOBILE_PUSH:
                self.statistics["push_notifications_sent"] += 1
                result["sent_count"] += 1

        self.statistics["notifications_delivered"] += result["sent_count"]
        return result

    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        return self.templates.get(template_id)

    def get_all_templates(self) -> List[NotificationTemplate]:
        return list(self.templates.values())

    def get_statistics(self) -> Dict[str, Any]:
        return {
            **self.statistics,
            "total_events": len(self.events),
            "total_alerts": len(self.alerts),
            "active_alerts": len(self.get_active_alerts()),
            "upcoming_events": len(self.get_upcoming_events()),
            "total_templates": len(self.templates),
        }
