"""
Auto Dispatch Engine.

Handles automatic drone dispatch based on various triggers including
ShotSpotter, crash detection, 911 keywords, officer distress, and more.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from collections import deque
from pydantic import BaseModel, Field


class DispatchTrigger(str, Enum):
    """Types of auto-dispatch triggers."""
    SHOTSPOTTER = "shotspotter"
    CRASH_DETECTION = "crash_detection"
    DANGEROUS_KEYWORD_911 = "dangerous_keyword_911"
    OFFICER_DISTRESS = "officer_distress"
    AMBUSH_WARNING = "ambush_warning"
    PERIMETER_BREACH = "perimeter_breach"
    HOT_VEHICLE_LPR = "hot_vehicle_lpr"
    MISSING_PERSON = "missing_person"
    PURSUIT = "pursuit"
    STRUCTURE_FIRE = "structure_fire"
    HAZMAT_INCIDENT = "hazmat_incident"
    CROWD_EMERGENCY = "crowd_emergency"
    ACTIVE_SHOOTER = "active_shooter"
    MANUAL_REQUEST = "manual_request"


class DispatchPriority(str, Enum):
    """Dispatch priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class DispatchStatus(str, Enum):
    """Dispatch request status."""
    PENDING = "pending"
    EVALUATING = "evaluating"
    DISPATCHING = "dispatching"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    NO_DRONES_AVAILABLE = "no_drones_available"


class TriggerEvent(BaseModel):
    """Trigger event that initiates auto-dispatch."""
    event_id: str
    trigger_type: DispatchTrigger
    timestamp: datetime
    latitude: float
    longitude: float
    priority: DispatchPriority = DispatchPriority.NORMAL
    source_system: str
    source_event_id: Optional[str] = None
    description: str
    keywords: list[str] = Field(default_factory=list)
    affected_units: list[str] = Field(default_factory=list)
    threat_level: Optional[int] = None
    radius_m: float = 100.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class DispatchRequest(BaseModel):
    """Auto-dispatch request."""
    request_id: str
    trigger_event: TriggerEvent
    status: DispatchStatus = DispatchStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    dispatched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_drone_id: Optional[str] = None
    assigned_mission_id: Optional[str] = None
    drone_eta_seconds: Optional[float] = None
    response_time_seconds: Optional[float] = None
    evaluation_score: float = 0.0
    evaluation_factors: dict[str, float] = Field(default_factory=dict)
    operator_override: bool = False
    operator_id: Optional[str] = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DispatchRule(BaseModel):
    """Rule for auto-dispatch evaluation."""
    rule_id: str
    trigger_type: DispatchTrigger
    enabled: bool = True
    min_priority: DispatchPriority = DispatchPriority.NORMAL
    auto_dispatch: bool = True
    require_approval: bool = False
    max_response_radius_km: float = 5.0
    preferred_drone_types: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    altitude_m: float = 30.0
    orbit_on_arrival: bool = True
    orbit_radius_m: float = 50.0
    follow_target: bool = False
    notify_dispatch: bool = True
    notify_tactical: bool = False
    escalation_threshold_seconds: float = 300.0


class DispatchConfig(BaseModel):
    """Configuration for auto-dispatch engine."""
    enabled: bool = True
    max_concurrent_dispatches: int = 10
    evaluation_timeout_seconds: float = 5.0
    default_response_radius_km: float = 5.0
    min_battery_for_dispatch: float = 30.0
    require_operator_approval: bool = False
    dangerous_keywords: list[str] = Field(default_factory=lambda: [
        "gun", "shot", "shooting", "weapon", "knife", "stabbing",
        "hostage", "bomb", "explosive", "active shooter", "officer down",
        "ambush", "pursuit", "shots fired", "armed", "robbery",
    ])
    max_requests_stored: int = 10000


class DispatchMetrics(BaseModel):
    """Metrics for auto-dispatch engine."""
    total_requests: int = 0
    requests_by_trigger: dict[str, int] = Field(default_factory=dict)
    requests_by_status: dict[str, int] = Field(default_factory=dict)
    dispatched_count: int = 0
    failed_count: int = 0
    avg_response_time_seconds: float = 0.0
    avg_evaluation_score: float = 0.0


class AutoDispatchEngine:
    """
    Auto Dispatch Engine.
    
    Handles automatic drone dispatch based on various triggers including
    ShotSpotter, crash detection, 911 keywords, officer distress, and more.
    """
    
    def __init__(self, config: Optional[DispatchConfig] = None):
        self.config = config or DispatchConfig()
        self._requests: deque[DispatchRequest] = deque(maxlen=self.config.max_requests_stored)
        self._active_requests: dict[str, DispatchRequest] = {}
        self._rules: dict[DispatchTrigger, DispatchRule] = {}
        self._callbacks: list[Callable] = []
        self._running = False
        self._metrics = DispatchMetrics()
        
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default dispatch rules."""
        default_rules = [
            DispatchRule(
                rule_id="rule-shotspotter",
                trigger_type=DispatchTrigger.SHOTSPOTTER,
                auto_dispatch=True,
                min_priority=DispatchPriority.HIGH,
                required_capabilities=["hd_camera", "thermal_camera"],
                orbit_on_arrival=True,
                notify_tactical=True,
            ),
            DispatchRule(
                rule_id="rule-officer-distress",
                trigger_type=DispatchTrigger.OFFICER_DISTRESS,
                auto_dispatch=True,
                min_priority=DispatchPriority.CRITICAL,
                required_capabilities=["hd_camera", "spotlight"],
                orbit_on_arrival=True,
                follow_target=True,
                notify_tactical=True,
            ),
            DispatchRule(
                rule_id="rule-ambush",
                trigger_type=DispatchTrigger.AMBUSH_WARNING,
                auto_dispatch=True,
                min_priority=DispatchPriority.CRITICAL,
                required_capabilities=["hd_camera", "thermal_camera", "spotlight"],
                orbit_on_arrival=True,
                notify_tactical=True,
            ),
            DispatchRule(
                rule_id="rule-hot-vehicle",
                trigger_type=DispatchTrigger.HOT_VEHICLE_LPR,
                auto_dispatch=True,
                min_priority=DispatchPriority.HIGH,
                required_capabilities=["hd_camera", "lpr_camera"],
                follow_target=True,
            ),
            DispatchRule(
                rule_id="rule-missing-person",
                trigger_type=DispatchTrigger.MISSING_PERSON,
                auto_dispatch=True,
                min_priority=DispatchPriority.NORMAL,
                required_capabilities=["hd_camera", "thermal_camera"],
                orbit_on_arrival=False,
            ),
            DispatchRule(
                rule_id="rule-pursuit",
                trigger_type=DispatchTrigger.PURSUIT,
                auto_dispatch=True,
                min_priority=DispatchPriority.URGENT,
                required_capabilities=["hd_camera", "zoom_30x"],
                follow_target=True,
                notify_tactical=True,
            ),
            DispatchRule(
                rule_id="rule-active-shooter",
                trigger_type=DispatchTrigger.ACTIVE_SHOOTER,
                auto_dispatch=True,
                min_priority=DispatchPriority.CRITICAL,
                required_capabilities=["hd_camera", "thermal_camera", "speaker"],
                orbit_on_arrival=True,
                notify_tactical=True,
            ),
            DispatchRule(
                rule_id="rule-crash",
                trigger_type=DispatchTrigger.CRASH_DETECTION,
                auto_dispatch=True,
                min_priority=DispatchPriority.NORMAL,
                required_capabilities=["hd_camera"],
                orbit_on_arrival=True,
            ),
            DispatchRule(
                rule_id="rule-911-keyword",
                trigger_type=DispatchTrigger.DANGEROUS_KEYWORD_911,
                auto_dispatch=False,
                require_approval=True,
                min_priority=DispatchPriority.HIGH,
            ),
            DispatchRule(
                rule_id="rule-perimeter",
                trigger_type=DispatchTrigger.PERIMETER_BREACH,
                auto_dispatch=True,
                min_priority=DispatchPriority.HIGH,
                required_capabilities=["hd_camera", "thermal_camera"],
                orbit_on_arrival=True,
            ),
        ]
        
        for rule in default_rules:
            self._rules[rule.trigger_type] = rule
    
    async def start(self) -> None:
        """Start the auto-dispatch engine."""
        self._running = True
    
    async def stop(self) -> None:
        """Stop the auto-dispatch engine."""
        self._running = False
    
    async def process_trigger(self, event: TriggerEvent) -> DispatchRequest:
        """Process a trigger event and potentially dispatch a drone."""
        request = DispatchRequest(
            request_id=f"dispatch-{uuid.uuid4().hex[:12]}",
            trigger_event=event,
            status=DispatchStatus.EVALUATING,
        )
        
        self._requests.append(request)
        self._active_requests[request.request_id] = request
        self._metrics.total_requests += 1
        
        rule = self._rules.get(event.trigger_type)
        if not rule or not rule.enabled:
            request.status = DispatchStatus.CANCELLED
            request.notes.append("No active rule for trigger type")
            del self._active_requests[request.request_id]
            return request
        
        score, factors = self._evaluate_dispatch(event, rule)
        request.evaluation_score = score
        request.evaluation_factors = factors
        
        if score < 0.5:
            request.status = DispatchStatus.CANCELLED
            request.notes.append(f"Evaluation score too low: {score:.2f}")
            del self._active_requests[request.request_id]
            return request
        
        if rule.require_approval and not request.operator_override:
            request.status = DispatchStatus.PENDING
            request.notes.append("Awaiting operator approval")
            await self._notify_callbacks(request, "approval_required")
            return request
        
        if rule.auto_dispatch:
            await self._dispatch_drone(request, rule)
        
        self._update_metrics()
        return request
    
    async def process_shotspotter(
        self,
        latitude: float,
        longitude: float,
        confidence: float,
        rounds_detected: int,
        source_event_id: Optional[str] = None,
    ) -> DispatchRequest:
        """Process a ShotSpotter activation."""
        priority = DispatchPriority.HIGH
        if rounds_detected >= 10:
            priority = DispatchPriority.CRITICAL
        elif rounds_detected >= 5:
            priority = DispatchPriority.URGENT
        
        event = TriggerEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            trigger_type=DispatchTrigger.SHOTSPOTTER,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            priority=priority,
            source_system="shotspotter",
            source_event_id=source_event_id,
            description=f"ShotSpotter: {rounds_detected} rounds detected",
            threat_level=min(10, rounds_detected),
            metadata={"confidence": confidence, "rounds": rounds_detected},
        )
        return await self.process_trigger(event)
    
    async def process_officer_distress(
        self,
        officer_id: str,
        latitude: float,
        longitude: float,
        distress_type: str,
        source_event_id: Optional[str] = None,
    ) -> DispatchRequest:
        """Process an officer distress signal."""
        event = TriggerEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            trigger_type=DispatchTrigger.OFFICER_DISTRESS,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            priority=DispatchPriority.CRITICAL,
            source_system="officer_safety",
            source_event_id=source_event_id,
            description=f"Officer distress: {distress_type}",
            affected_units=[officer_id],
            threat_level=10,
            metadata={"distress_type": distress_type},
        )
        return await self.process_trigger(event)
    
    async def process_hot_vehicle(
        self,
        plate: str,
        latitude: float,
        longitude: float,
        alert_type: str,
        vehicle_description: str,
        source_event_id: Optional[str] = None,
    ) -> DispatchRequest:
        """Process a hot vehicle LPR hit."""
        priority = DispatchPriority.HIGH
        if alert_type in ["stolen_armed", "felony_vehicle", "amber_alert"]:
            priority = DispatchPriority.CRITICAL
        
        event = TriggerEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            trigger_type=DispatchTrigger.HOT_VEHICLE_LPR,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            priority=priority,
            source_system="lpr",
            source_event_id=source_event_id,
            description=f"Hot vehicle: {plate} - {alert_type}",
            keywords=[plate, alert_type],
            metadata={"plate": plate, "alert_type": alert_type, "vehicle": vehicle_description},
        )
        return await self.process_trigger(event)
    
    async def process_911_call(
        self,
        call_id: str,
        latitude: float,
        longitude: float,
        transcript: str,
        call_type: str,
    ) -> Optional[DispatchRequest]:
        """Process a 911 call for dangerous keywords."""
        detected_keywords = []
        transcript_lower = transcript.lower()
        
        for keyword in self.config.dangerous_keywords:
            if keyword.lower() in transcript_lower:
                detected_keywords.append(keyword)
        
        if not detected_keywords:
            return None
        
        priority = DispatchPriority.HIGH
        critical_keywords = ["active shooter", "officer down", "hostage", "bomb"]
        if any(kw in transcript_lower for kw in critical_keywords):
            priority = DispatchPriority.CRITICAL
        
        event = TriggerEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            trigger_type=DispatchTrigger.DANGEROUS_KEYWORD_911,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            priority=priority,
            source_system="cad",
            source_event_id=call_id,
            description=f"911 call with keywords: {', '.join(detected_keywords)}",
            keywords=detected_keywords,
            metadata={"call_type": call_type, "keywords_count": len(detected_keywords)},
        )
        return await self.process_trigger(event)
    
    async def process_missing_person(
        self,
        case_id: str,
        last_known_lat: float,
        last_known_lon: float,
        person_description: str,
        search_radius_km: float = 2.0,
    ) -> DispatchRequest:
        """Process a missing person alert."""
        event = TriggerEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            trigger_type=DispatchTrigger.MISSING_PERSON,
            timestamp=datetime.now(timezone.utc),
            latitude=last_known_lat,
            longitude=last_known_lon,
            priority=DispatchPriority.NORMAL,
            source_system="investigations",
            source_event_id=case_id,
            description=f"Missing person search: {person_description[:100]}",
            radius_m=search_radius_km * 1000,
            metadata={"search_radius_km": search_radius_km},
        )
        return await self.process_trigger(event)
    
    async def process_pursuit(
        self,
        pursuit_id: str,
        latitude: float,
        longitude: float,
        vehicle_description: str,
        pursuing_units: list[str],
    ) -> DispatchRequest:
        """Process a vehicle pursuit."""
        event = TriggerEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            trigger_type=DispatchTrigger.PURSUIT,
            timestamp=datetime.now(timezone.utc),
            latitude=latitude,
            longitude=longitude,
            priority=DispatchPriority.URGENT,
            source_system="cad",
            source_event_id=pursuit_id,
            description=f"Vehicle pursuit: {vehicle_description}",
            affected_units=pursuing_units,
            metadata={"vehicle": vehicle_description},
        )
        return await self.process_trigger(event)
    
    async def approve_dispatch(
        self,
        request_id: str,
        operator_id: str,
    ) -> bool:
        """Approve a pending dispatch request."""
        request = self._active_requests.get(request_id)
        if not request or request.status != DispatchStatus.PENDING:
            return False
        
        request.operator_override = True
        request.operator_id = operator_id
        request.notes.append(f"Approved by operator {operator_id}")
        
        rule = self._rules.get(request.trigger_event.trigger_type)
        if rule:
            await self._dispatch_drone(request, rule)
        
        return True
    
    async def cancel_dispatch(
        self,
        request_id: str,
        operator_id: str,
        reason: str,
    ) -> bool:
        """Cancel a dispatch request."""
        request = self._active_requests.get(request_id)
        if not request:
            return False
        
        request.status = DispatchStatus.CANCELLED
        request.operator_id = operator_id
        request.notes.append(f"Cancelled by {operator_id}: {reason}")
        request.completed_at = datetime.now(timezone.utc)
        
        del self._active_requests[request_id]
        self._update_metrics()
        
        return True
    
    def get_request(self, request_id: str) -> Optional[DispatchRequest]:
        """Get a dispatch request by ID."""
        if request_id in self._active_requests:
            return self._active_requests[request_id]
        
        for req in self._requests:
            if req.request_id == request_id:
                return req
        
        return None
    
    def get_active_requests(self) -> list[DispatchRequest]:
        """Get all active dispatch requests."""
        return list(self._active_requests.values())
    
    def get_pending_approvals(self) -> list[DispatchRequest]:
        """Get requests pending approval."""
        return [
            r for r in self._active_requests.values()
            if r.status == DispatchStatus.PENDING
        ]
    
    def get_recent_requests(self, limit: int = 100) -> list[DispatchRequest]:
        """Get recent dispatch requests."""
        requests = list(self._requests)
        requests.reverse()
        return requests[:limit]
    
    def get_rule(self, trigger_type: DispatchTrigger) -> Optional[DispatchRule]:
        """Get dispatch rule for a trigger type."""
        return self._rules.get(trigger_type)
    
    def update_rule(self, rule: DispatchRule) -> None:
        """Update a dispatch rule."""
        self._rules[rule.trigger_type] = rule
    
    def get_metrics(self) -> DispatchMetrics:
        """Get dispatch metrics."""
        return self._metrics
    
    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        return {
            "running": self._running,
            "enabled": self.config.enabled,
            "active_requests": len(self._active_requests),
            "pending_approvals": len(self.get_pending_approvals()),
            "total_requests": self._metrics.total_requests,
            "metrics": self._metrics.model_dump(),
        }
    
    def register_callback(self, callback: Callable) -> None:
        """Register a callback for dispatch events."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _evaluate_dispatch(
        self,
        event: TriggerEvent,
        rule: DispatchRule,
    ) -> tuple[float, dict[str, float]]:
        """Evaluate whether to dispatch based on event and rule."""
        factors: dict[str, float] = {}
        
        priority_scores = {
            DispatchPriority.LOW: 0.3,
            DispatchPriority.NORMAL: 0.5,
            DispatchPriority.HIGH: 0.7,
            DispatchPriority.URGENT: 0.85,
            DispatchPriority.CRITICAL: 1.0,
        }
        factors["priority"] = priority_scores.get(event.priority, 0.5)
        
        if event.threat_level is not None:
            factors["threat_level"] = min(1.0, event.threat_level / 10.0)
        else:
            factors["threat_level"] = 0.5
        
        factors["rule_enabled"] = 1.0 if rule.enabled else 0.0
        
        score = sum(factors.values()) / len(factors)
        
        return score, factors
    
    async def _dispatch_drone(
        self,
        request: DispatchRequest,
        rule: DispatchRule,
    ) -> None:
        """Dispatch a drone for the request."""
        request.status = DispatchStatus.DISPATCHING
        request.dispatched_at = datetime.now(timezone.utc)
        
        request.assigned_drone_id = f"drone-simulated-{uuid.uuid4().hex[:8]}"
        request.assigned_mission_id = f"mission-{uuid.uuid4().hex[:12]}"
        request.drone_eta_seconds = 120.0
        
        request.status = DispatchStatus.DISPATCHED
        request.notes.append(f"Dispatched drone {request.assigned_drone_id}")
        
        if request.dispatched_at and request.created_at:
            request.response_time_seconds = (
                request.dispatched_at - request.created_at
            ).total_seconds()
        
        self._metrics.dispatched_count += 1
        await self._notify_callbacks(request, "dispatched")
    
    def _update_metrics(self) -> None:
        """Update dispatch metrics."""
        trigger_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        
        for req in self._requests:
            trigger = req.trigger_event.trigger_type.value
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
            status_counts[req.status.value] = status_counts.get(req.status.value, 0) + 1
        
        self._metrics.requests_by_trigger = trigger_counts
        self._metrics.requests_by_status = status_counts
    
    async def _notify_callbacks(self, request: DispatchRequest, event_type: str) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                if callable(callback):
                    result = callback(request, event_type)
                    if hasattr(result, "__await__"):
                        await result
            except Exception:
                pass
