"""
Officer Behavioral Safety Engine

Monitors officer behavior for:
- Fatigue indicators
- Stress indicators
- Repeated high-stress events in 24 hours
- Excessive CAD calls without break
- Known trauma patterns
- Prior complaints or IA red flags (anonymized)

Outputs: Risk score, early warning flags, supervisor notification
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class FatigueLevel(str, Enum):
    """Officer fatigue levels"""
    NORMAL = "NORMAL"
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"


class StressIndicator(str, Enum):
    """Stress indicator types"""
    ELEVATED_HEART_RATE = "ELEVATED_HEART_RATE"
    VOICE_STRESS = "VOICE_STRESS"
    RAPID_DECISION_MAKING = "RAPID_DECISION_MAKING"
    COMMUNICATION_BREAKDOWN = "COMMUNICATION_BREAKDOWN"
    PHYSICAL_SYMPTOMS = "PHYSICAL_SYMPTOMS"
    BEHAVIORAL_CHANGE = "BEHAVIORAL_CHANGE"
    ISOLATION = "ISOLATION"
    IRRITABILITY = "IRRITABILITY"


class TraumaPattern(str, Enum):
    """Known trauma patterns"""
    OFFICER_INVOLVED_SHOOTING = "OFFICER_INVOLVED_SHOOTING"
    LINE_OF_DUTY_DEATH = "LINE_OF_DUTY_DEATH"
    CHILD_FATALITY = "CHILD_FATALITY"
    MASS_CASUALTY = "MASS_CASUALTY"
    ASSAULT_ON_OFFICER = "ASSAULT_ON_OFFICER"
    DOMESTIC_VIOLENCE_CHILD = "DOMESTIC_VIOLENCE_CHILD"
    SUICIDE_RESPONSE = "SUICIDE_RESPONSE"
    FATAL_ACCIDENT = "FATAL_ACCIDENT"


class SafetyAlertType(str, Enum):
    """Safety alert types"""
    FATIGUE_WARNING = "FATIGUE_WARNING"
    STRESS_WARNING = "STRESS_WARNING"
    WORKLOAD_WARNING = "WORKLOAD_WARNING"
    TRAUMA_EXPOSURE = "TRAUMA_EXPOSURE"
    PATTERN_DETECTED = "PATTERN_DETECTED"
    WELLNESS_CHECK = "WELLNESS_CHECK"
    MANDATORY_BREAK = "MANDATORY_BREAK"


class OfficerWorkload(BaseModel):
    """Officer workload metrics"""
    officer_id: str
    shift_start: datetime
    hours_on_duty: float = 0.0
    calls_handled: int = 0
    high_stress_calls: int = 0
    arrests_made: int = 0
    reports_written: int = 0
    breaks_taken: int = 0
    last_break_time: Optional[datetime] = None
    overtime_hours: float = 0.0
    consecutive_days_worked: int = 1


class OfficerHistory(BaseModel):
    """Officer history for pattern detection (anonymized)"""
    officer_id: str
    high_stress_events_30d: int = 0
    trauma_exposures_90d: int = 0
    complaints_12m: int = 0
    use_of_force_incidents_12m: int = 0
    sick_days_30d: int = 0
    counseling_referrals: int = 0
    peer_support_contacts: int = 0
    last_wellness_check: Optional[datetime] = None
    last_training_date: Optional[datetime] = None


class SafetyAlert(BaseModel):
    """Safety alert for officer"""
    alert_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    officer_id: str
    alert_type: SafetyAlertType
    severity: str
    description: str
    risk_score: float
    recommended_action: str
    supervisor_notified: bool = False
    acknowledged: bool = False
    resolved: bool = False


class OfficerSafetyStatus(BaseModel):
    """Complete officer safety status"""
    status_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    officer_id: str
    overall_risk_score: float
    fatigue_level: FatigueLevel
    fatigue_score: float
    stress_score: float
    stress_indicators: List[StressIndicator] = []
    workload_score: float
    workload: Optional[OfficerWorkload] = None
    trauma_exposure_score: float
    recent_trauma_events: List[str] = []
    pattern_flags: List[str] = []
    active_alerts: List[SafetyAlert] = []
    recommendations: List[str] = []
    fit_for_duty: bool = True
    supervisor_review_required: bool = False


class OfficerBehavioralSafetyEngine:
    """
    Officer Behavioral Safety Engine
    
    Monitors officer behavior and wellness indicators to identify
    potential safety concerns and provide early intervention.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        self.agency_config = {
            "ori": "FL0500400",
            "name": "Riviera Beach Police Department",
            "state": "FL",
            "city": "Riviera Beach",
        }
        
        self.fatigue_thresholds = {
            "hours_mild": 8,
            "hours_moderate": 10,
            "hours_severe": 12,
            "hours_critical": 14,
            "max_consecutive_days": 6,
            "mandatory_break_hours": 4,
        }
        
        self.stress_thresholds = {
            "high_stress_calls_warning": 3,
            "high_stress_calls_critical": 5,
            "calls_without_break_warning": 8,
            "calls_without_break_critical": 12,
        }
        
        self.workload_thresholds = {
            "calls_per_shift_warning": 15,
            "calls_per_shift_critical": 20,
            "arrests_per_shift_warning": 5,
            "overtime_hours_warning": 4,
            "overtime_hours_critical": 8,
        }
        
        self.pattern_thresholds = {
            "high_stress_events_30d_warning": 5,
            "trauma_exposures_90d_warning": 2,
            "complaints_12m_warning": 2,
            "use_of_force_12m_warning": 3,
            "sick_days_30d_warning": 3,
        }
        
        self.high_stress_call_types = [
            "SHOTS_FIRED",
            "OFFICER_DOWN",
            "PURSUIT",
            "DOMESTIC_VIOLENCE",
            "ARMED_ROBBERY",
            "HOSTAGE",
            "BARRICADED_SUBJECT",
            "SUICIDE_ATTEMPT",
            "CHILD_ABUSE",
            "FATAL_ACCIDENT",
            "HOMICIDE",
            "ASSAULT_ON_OFFICER",
        ]
        
        self.officer_statuses: Dict[str, OfficerSafetyStatus] = {}
        self.officer_workloads: Dict[str, OfficerWorkload] = {}
        self.officer_histories: Dict[str, OfficerHistory] = {}
        self.safety_alerts: List[SafetyAlert] = []
        self.wellness_checks_due: List[str] = []
    
    def assess_officer_safety(
        self,
        officer_id: str,
        workload: Optional[OfficerWorkload] = None,
        history: Optional[OfficerHistory] = None,
        stress_indicators: Optional[List[StressIndicator]] = None,
        recent_call_type: Optional[str] = None,
    ) -> OfficerSafetyStatus:
        """
        Assess officer safety status
        
        Args:
            officer_id: Officer identifier
            workload: Current workload metrics
            history: Officer history for pattern detection
            stress_indicators: Currently observed stress indicators
            recent_call_type: Type of most recent call handled
            
        Returns:
            OfficerSafetyStatus with risk assessment and recommendations
        """
        if workload:
            self.officer_workloads[officer_id] = workload
        else:
            workload = self.officer_workloads.get(officer_id, OfficerWorkload(officer_id=officer_id, shift_start=datetime.utcnow()))
        
        if history:
            self.officer_histories[officer_id] = history
        else:
            history = self.officer_histories.get(officer_id, OfficerHistory(officer_id=officer_id))
        
        if stress_indicators is None:
            stress_indicators = []
        
        if recent_call_type and recent_call_type.upper() in self.high_stress_call_types:
            workload.high_stress_calls += 1
        
        fatigue_score, fatigue_level = self._assess_fatigue(workload)
        stress_score = self._assess_stress(workload, stress_indicators)
        workload_score = self._assess_workload(workload)
        trauma_score, recent_trauma = self._assess_trauma_exposure(history, recent_call_type)
        pattern_flags = self._detect_patterns(history, workload)
        
        overall_risk = (
            fatigue_score * 0.25 +
            stress_score * 0.30 +
            workload_score * 0.20 +
            trauma_score * 0.25
        )
        
        alerts = []
        recommendations = []
        
        if fatigue_level in [FatigueLevel.SEVERE, FatigueLevel.CRITICAL]:
            alert = self._create_alert(
                officer_id,
                SafetyAlertType.FATIGUE_WARNING,
                "HIGH" if fatigue_level == FatigueLevel.CRITICAL else "MEDIUM",
                f"Officer fatigue level: {fatigue_level.value}",
                fatigue_score,
                "Consider mandatory rest period",
            )
            alerts.append(alert)
            recommendations.append("Take mandatory rest break")
        
        if stress_score > 0.7:
            alert = self._create_alert(
                officer_id,
                SafetyAlertType.STRESS_WARNING,
                "HIGH",
                f"Elevated stress indicators detected",
                stress_score,
                "Peer support or supervisor check-in recommended",
            )
            alerts.append(alert)
            recommendations.append("Peer support contact recommended")
        
        if workload_score > 0.8:
            alert = self._create_alert(
                officer_id,
                SafetyAlertType.WORKLOAD_WARNING,
                "MEDIUM",
                f"Excessive workload detected",
                workload_score,
                "Redistribute calls or provide break",
            )
            alerts.append(alert)
            recommendations.append("Reduce call volume or take break")
        
        if trauma_score > 0.5:
            alert = self._create_alert(
                officer_id,
                SafetyAlertType.TRAUMA_EXPOSURE,
                "HIGH" if trauma_score > 0.7 else "MEDIUM",
                f"Recent trauma exposure detected",
                trauma_score,
                "Wellness check and counseling referral",
            )
            alerts.append(alert)
            recommendations.append("Schedule wellness check")
            recommendations.append("Consider counseling referral")
        
        if pattern_flags:
            alert = self._create_alert(
                officer_id,
                SafetyAlertType.PATTERN_DETECTED,
                "MEDIUM",
                f"Behavioral patterns detected: {', '.join(pattern_flags[:3])}",
                overall_risk,
                "Supervisor review recommended",
            )
            alerts.append(alert)
        
        fit_for_duty = overall_risk < 0.8 and fatigue_level != FatigueLevel.CRITICAL
        supervisor_review = overall_risk > 0.6 or len(alerts) > 2
        
        if not fit_for_duty:
            recommendations.insert(0, "IMMEDIATE: Remove from active duty pending review")
        
        status = OfficerSafetyStatus(
            status_id=f"oss-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{officer_id}",
            officer_id=officer_id,
            overall_risk_score=overall_risk,
            fatigue_level=fatigue_level,
            fatigue_score=fatigue_score,
            stress_score=stress_score,
            stress_indicators=stress_indicators,
            workload_score=workload_score,
            workload=workload,
            trauma_exposure_score=trauma_score,
            recent_trauma_events=recent_trauma,
            pattern_flags=pattern_flags,
            active_alerts=alerts,
            recommendations=recommendations,
            fit_for_duty=fit_for_duty,
            supervisor_review_required=supervisor_review,
        )
        
        self.officer_statuses[officer_id] = status
        self.safety_alerts.extend(alerts)
        
        return status
    
    def _assess_fatigue(self, workload: OfficerWorkload) -> tuple[float, FatigueLevel]:
        """Assess fatigue level based on workload"""
        hours = workload.hours_on_duty + workload.overtime_hours
        
        if hours >= self.fatigue_thresholds["hours_critical"]:
            level = FatigueLevel.CRITICAL
            score = 1.0
        elif hours >= self.fatigue_thresholds["hours_severe"]:
            level = FatigueLevel.SEVERE
            score = 0.8
        elif hours >= self.fatigue_thresholds["hours_moderate"]:
            level = FatigueLevel.MODERATE
            score = 0.6
        elif hours >= self.fatigue_thresholds["hours_mild"]:
            level = FatigueLevel.MILD
            score = 0.4
        else:
            level = FatigueLevel.NORMAL
            score = 0.2
        
        if workload.consecutive_days_worked >= self.fatigue_thresholds["max_consecutive_days"]:
            score = min(1.0, score + 0.2)
            if level.value < FatigueLevel.SEVERE.value:
                level = FatigueLevel.SEVERE
        
        if workload.last_break_time:
            hours_since_break = (datetime.utcnow() - workload.last_break_time).total_seconds() / 3600
            if hours_since_break > self.fatigue_thresholds["mandatory_break_hours"]:
                score = min(1.0, score + 0.15)
        
        return score, level
    
    def _assess_stress(
        self,
        workload: OfficerWorkload,
        indicators: List[StressIndicator],
    ) -> float:
        """Assess stress level"""
        score = 0.0
        
        if workload.high_stress_calls >= self.stress_thresholds["high_stress_calls_critical"]:
            score += 0.4
        elif workload.high_stress_calls >= self.stress_thresholds["high_stress_calls_warning"]:
            score += 0.25
        
        if workload.calls_handled >= self.stress_thresholds["calls_without_break_critical"] and workload.breaks_taken == 0:
            score += 0.3
        elif workload.calls_handled >= self.stress_thresholds["calls_without_break_warning"] and workload.breaks_taken == 0:
            score += 0.2
        
        indicator_weight = 0.1
        score += len(indicators) * indicator_weight
        
        return min(1.0, score)
    
    def _assess_workload(self, workload: OfficerWorkload) -> float:
        """Assess workload level"""
        score = 0.0
        
        if workload.calls_handled >= self.workload_thresholds["calls_per_shift_critical"]:
            score += 0.4
        elif workload.calls_handled >= self.workload_thresholds["calls_per_shift_warning"]:
            score += 0.25
        
        if workload.arrests_made >= self.workload_thresholds["arrests_per_shift_warning"]:
            score += 0.2
        
        if workload.overtime_hours >= self.workload_thresholds["overtime_hours_critical"]:
            score += 0.3
        elif workload.overtime_hours >= self.workload_thresholds["overtime_hours_warning"]:
            score += 0.15
        
        return min(1.0, score)
    
    def _assess_trauma_exposure(
        self,
        history: OfficerHistory,
        recent_call_type: Optional[str],
    ) -> tuple[float, List[str]]:
        """Assess trauma exposure"""
        score = 0.0
        recent_trauma = []
        
        if history.trauma_exposures_90d >= self.pattern_thresholds["trauma_exposures_90d_warning"]:
            score += 0.4
            recent_trauma.append(f"{history.trauma_exposures_90d} trauma exposures in 90 days")
        
        if recent_call_type:
            trauma_call_types = [
                "OFFICER_INVOLVED_SHOOTING",
                "LINE_OF_DUTY_DEATH",
                "CHILD_FATALITY",
                "MASS_CASUALTY",
                "SUICIDE_ATTEMPT",
                "HOMICIDE",
            ]
            if recent_call_type.upper() in trauma_call_types:
                score += 0.3
                recent_trauma.append(f"Recent {recent_call_type} call")
        
        if history.counseling_referrals > 0:
            score += 0.1
        
        return min(1.0, score), recent_trauma
    
    def _detect_patterns(
        self,
        history: OfficerHistory,
        workload: OfficerWorkload,
    ) -> List[str]:
        """Detect concerning behavioral patterns"""
        flags = []
        
        if history.high_stress_events_30d >= self.pattern_thresholds["high_stress_events_30d_warning"]:
            flags.append(f"High stress events: {history.high_stress_events_30d} in 30 days")
        
        if history.complaints_12m >= self.pattern_thresholds["complaints_12m_warning"]:
            flags.append(f"Complaints: {history.complaints_12m} in 12 months")
        
        if history.use_of_force_incidents_12m >= self.pattern_thresholds["use_of_force_12m_warning"]:
            flags.append(f"Use of force incidents: {history.use_of_force_incidents_12m} in 12 months")
        
        if history.sick_days_30d >= self.pattern_thresholds["sick_days_30d_warning"]:
            flags.append(f"Sick days: {history.sick_days_30d} in 30 days")
        
        if history.last_wellness_check:
            days_since = (datetime.utcnow() - history.last_wellness_check).days
            if days_since > 90:
                flags.append(f"Wellness check overdue: {days_since} days")
        
        return flags
    
    def _create_alert(
        self,
        officer_id: str,
        alert_type: SafetyAlertType,
        severity: str,
        description: str,
        risk_score: float,
        recommended_action: str,
    ) -> SafetyAlert:
        """Create a safety alert"""
        return SafetyAlert(
            alert_id=f"sa-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{officer_id}",
            officer_id=officer_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            risk_score=risk_score,
            recommended_action=recommended_action,
            supervisor_notified=severity == "HIGH",
        )
    
    def record_call(
        self,
        officer_id: str,
        call_type: str,
        duration_minutes: float = 0,
    ) -> OfficerSafetyStatus:
        """Record a call handled by officer"""
        if officer_id not in self.officer_workloads:
            self.officer_workloads[officer_id] = OfficerWorkload(
                officer_id=officer_id,
                shift_start=datetime.utcnow(),
            )
        
        workload = self.officer_workloads[officer_id]
        workload.calls_handled += 1
        
        return self.assess_officer_safety(
            officer_id=officer_id,
            workload=workload,
            recent_call_type=call_type,
        )
    
    def record_break(self, officer_id: str) -> bool:
        """Record a break taken by officer"""
        if officer_id in self.officer_workloads:
            self.officer_workloads[officer_id].breaks_taken += 1
            self.officer_workloads[officer_id].last_break_time = datetime.utcnow()
            return True
        return False
    
    def get_officer_status(self, officer_id: str) -> Optional[OfficerSafetyStatus]:
        """Get current safety status for officer"""
        return self.officer_statuses.get(officer_id)
    
    def get_all_alerts(
        self,
        limit: int = 100,
        unresolved_only: bool = False,
        severity_filter: Optional[str] = None,
    ) -> List[SafetyAlert]:
        """Get safety alerts"""
        alerts = self.safety_alerts
        
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]
        
        return alerts[-limit:]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a safety alert"""
        for alert in self.safety_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a safety alert"""
        for alert in self.safety_alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False
    
    def get_officers_requiring_review(self) -> List[str]:
        """Get list of officers requiring supervisor review"""
        return [
            officer_id for officer_id, status in self.officer_statuses.items()
            if status.supervisor_review_required
        ]
    
    def get_safety_statistics(self) -> Dict[str, Any]:
        """Get safety monitoring statistics"""
        if not self.officer_statuses:
            return {
                "officers_monitored": 0,
                "average_risk_score": 0.0,
                "high_risk_officers": 0,
                "active_alerts": 0,
            }
        
        risk_scores = [s.overall_risk_score for s in self.officer_statuses.values()]
        high_risk = sum(1 for s in self.officer_statuses.values() if s.overall_risk_score > 0.6)
        unresolved_alerts = sum(1 for a in self.safety_alerts if not a.resolved)
        
        return {
            "officers_monitored": len(self.officer_statuses),
            "average_risk_score": sum(risk_scores) / len(risk_scores),
            "high_risk_officers": high_risk,
            "active_alerts": unresolved_alerts,
            "fit_for_duty_count": sum(1 for s in self.officer_statuses.values() if s.fit_for_duty),
            "review_required_count": sum(1 for s in self.officer_statuses.values() if s.supervisor_review_required),
        }
