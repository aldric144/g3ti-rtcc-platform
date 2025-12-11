"""
Real-Time Use-of-Force Risk Monitor

Monitors and classifies use-of-force risk levels based on:
- Officer proximity
- Suspect behavior classification
- Weapon probability
- Officer vital signs (if available)
- Scene escalation patterns

Risk Levels: Green, Yellow, Red (auto-notify supervisors)
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Use-of-force risk levels"""
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class SuspectBehaviorClass(str, Enum):
    """Suspect behavior classifications"""
    COMPLIANT = "COMPLIANT"
    PASSIVE_RESISTANT = "PASSIVE_RESISTANT"
    ACTIVE_RESISTANT = "ACTIVE_RESISTANT"
    AGGRESSIVE = "AGGRESSIVE"
    ASSAULTIVE = "ASSAULTIVE"
    LIFE_THREATENING = "LIFE_THREATENING"


class SceneEscalationPattern(str, Enum):
    """Scene escalation patterns"""
    STABLE = "STABLE"
    DE_ESCALATING = "DE_ESCALATING"
    SLOWLY_ESCALATING = "SLOWLY_ESCALATING"
    RAPIDLY_ESCALATING = "RAPIDLY_ESCALATING"
    CRITICAL = "CRITICAL"


class WeaponType(str, Enum):
    """Weapon types detected"""
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"
    BLUNT_OBJECT = "BLUNT_OBJECT"
    EDGED_WEAPON = "EDGED_WEAPON"
    FIREARM = "FIREARM"
    VEHICLE = "VEHICLE"
    EXPLOSIVE = "EXPLOSIVE"


class OfficerVitals(BaseModel):
    """Officer vital signs data"""
    heart_rate: Optional[int] = None
    heart_rate_variability: Optional[float] = None
    stress_index: Optional[float] = None
    fatigue_index: Optional[float] = None
    body_temperature: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SceneContext(BaseModel):
    """Scene context for risk assessment"""
    incident_id: str
    officer_id: str
    officer_count: int = 1
    suspect_count: int = 1
    bystander_count: int = 0
    location_type: str = "UNKNOWN"
    lighting_conditions: str = "DAYLIGHT"
    weather_conditions: str = "CLEAR"
    confined_space: bool = False
    escape_routes_available: bool = True
    backup_eta_minutes: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ForceRiskAssessment(BaseModel):
    """Complete force risk assessment"""
    assessment_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    incident_id: str
    officer_id: str
    risk_level: RiskLevel
    risk_score: float
    suspect_behavior: SuspectBehaviorClass
    escalation_pattern: SceneEscalationPattern
    weapon_detected: bool = False
    weapon_type: WeaponType = WeaponType.NONE
    weapon_probability: float = 0.0
    officer_proximity_feet: Optional[float] = None
    officer_vitals: Optional[OfficerVitals] = None
    scene_context: Optional[SceneContext] = None
    risk_factors: List[str] = []
    protective_factors: List[str] = []
    recommended_actions: List[str] = []
    supervisor_notified: bool = False
    rtcc_notified: bool = False
    backup_requested: bool = False
    de_escalation_recommended: bool = False


class SupervisorAlert(BaseModel):
    """Alert sent to supervisor"""
    alert_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    incident_id: str
    officer_id: str
    risk_level: RiskLevel
    risk_score: float
    alert_reason: str
    scene_summary: str
    recommended_response: str
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class UseOfForceRiskMonitor:
    """
    Real-Time Use-of-Force Risk Monitor
    
    Continuously monitors and classifies use-of-force risk levels
    with automatic supervisor notification for red-level risks.
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
        
        self.risk_thresholds = {
            "green_max": 0.3,
            "yellow_max": 0.7,
            "red_min": 0.7,
        }
        
        self.behavior_risk_weights = {
            SuspectBehaviorClass.COMPLIANT: 0.0,
            SuspectBehaviorClass.PASSIVE_RESISTANT: 0.15,
            SuspectBehaviorClass.ACTIVE_RESISTANT: 0.35,
            SuspectBehaviorClass.AGGRESSIVE: 0.55,
            SuspectBehaviorClass.ASSAULTIVE: 0.75,
            SuspectBehaviorClass.LIFE_THREATENING: 1.0,
        }
        
        self.escalation_risk_weights = {
            SceneEscalationPattern.STABLE: 0.0,
            SceneEscalationPattern.DE_ESCALATING: -0.1,
            SceneEscalationPattern.SLOWLY_ESCALATING: 0.15,
            SceneEscalationPattern.RAPIDLY_ESCALATING: 0.35,
            SceneEscalationPattern.CRITICAL: 0.5,
        }
        
        self.weapon_risk_weights = {
            WeaponType.NONE: 0.0,
            WeaponType.UNKNOWN: 0.2,
            WeaponType.BLUNT_OBJECT: 0.3,
            WeaponType.EDGED_WEAPON: 0.5,
            WeaponType.FIREARM: 0.8,
            WeaponType.VEHICLE: 0.6,
            WeaponType.EXPLOSIVE: 1.0,
        }
        
        self.proximity_thresholds = {
            "danger_zone_feet": 21,
            "caution_zone_feet": 50,
            "safe_zone_feet": 100,
        }
        
        self.vitals_thresholds = {
            "heart_rate_elevated": 120,
            "heart_rate_critical": 150,
            "stress_index_elevated": 0.6,
            "stress_index_critical": 0.8,
        }
        
        self.active_assessments: Dict[str, ForceRiskAssessment] = {}
        self.assessment_history: List[ForceRiskAssessment] = []
        self.supervisor_alerts: List[SupervisorAlert] = []
        self.red_level_incidents: List[str] = []
    
    def assess_risk(
        self,
        incident_id: str,
        officer_id: str,
        suspect_behavior: SuspectBehaviorClass,
        escalation_pattern: SceneEscalationPattern = SceneEscalationPattern.STABLE,
        weapon_type: WeaponType = WeaponType.NONE,
        weapon_probability: float = 0.0,
        officer_proximity_feet: Optional[float] = None,
        officer_vitals: Optional[OfficerVitals] = None,
        scene_context: Optional[SceneContext] = None,
    ) -> ForceRiskAssessment:
        """
        Assess use-of-force risk level
        
        Args:
            incident_id: Incident identifier
            officer_id: Officer identifier
            suspect_behavior: Current suspect behavior classification
            escalation_pattern: Scene escalation pattern
            weapon_type: Type of weapon detected
            weapon_probability: Probability of weapon presence (0-1)
            officer_proximity_feet: Distance between officer and suspect
            officer_vitals: Officer vital signs if available
            scene_context: Additional scene context
            
        Returns:
            ForceRiskAssessment with risk level and recommendations
        """
        risk_factors = []
        protective_factors = []
        recommended_actions = []
        
        base_risk = self.behavior_risk_weights.get(suspect_behavior, 0.3)
        
        escalation_modifier = self.escalation_risk_weights.get(escalation_pattern, 0.0)
        
        weapon_risk = self.weapon_risk_weights.get(weapon_type, 0.0) * weapon_probability
        
        if suspect_behavior in [SuspectBehaviorClass.AGGRESSIVE, SuspectBehaviorClass.ASSAULTIVE, SuspectBehaviorClass.LIFE_THREATENING]:
            risk_factors.append(f"Suspect behavior: {suspect_behavior.value}")
        
        if escalation_pattern in [SceneEscalationPattern.RAPIDLY_ESCALATING, SceneEscalationPattern.CRITICAL]:
            risk_factors.append(f"Scene escalation: {escalation_pattern.value}")
        elif escalation_pattern == SceneEscalationPattern.DE_ESCALATING:
            protective_factors.append("Scene is de-escalating")
        
        if weapon_type != WeaponType.NONE and weapon_probability > 0.5:
            risk_factors.append(f"Weapon detected: {weapon_type.value} ({weapon_probability*100:.0f}% confidence)")
        
        proximity_risk = 0.0
        if officer_proximity_feet is not None:
            if officer_proximity_feet <= self.proximity_thresholds["danger_zone_feet"]:
                proximity_risk = 0.3
                risk_factors.append(f"Officer in danger zone ({officer_proximity_feet:.0f} ft)")
                recommended_actions.append("Increase distance if tactically feasible")
            elif officer_proximity_feet <= self.proximity_thresholds["caution_zone_feet"]:
                proximity_risk = 0.15
                risk_factors.append(f"Officer in caution zone ({officer_proximity_feet:.0f} ft)")
            else:
                protective_factors.append(f"Safe distance maintained ({officer_proximity_feet:.0f} ft)")
        
        vitals_risk = 0.0
        if officer_vitals:
            if officer_vitals.heart_rate:
                if officer_vitals.heart_rate >= self.vitals_thresholds["heart_rate_critical"]:
                    vitals_risk += 0.2
                    risk_factors.append(f"Officer heart rate critical ({officer_vitals.heart_rate} bpm)")
                elif officer_vitals.heart_rate >= self.vitals_thresholds["heart_rate_elevated"]:
                    vitals_risk += 0.1
                    risk_factors.append(f"Officer heart rate elevated ({officer_vitals.heart_rate} bpm)")
            
            if officer_vitals.stress_index:
                if officer_vitals.stress_index >= self.vitals_thresholds["stress_index_critical"]:
                    vitals_risk += 0.15
                    risk_factors.append(f"Officer stress index critical ({officer_vitals.stress_index:.2f})")
                elif officer_vitals.stress_index >= self.vitals_thresholds["stress_index_elevated"]:
                    vitals_risk += 0.08
        
        scene_risk = 0.0
        if scene_context:
            if scene_context.suspect_count > scene_context.officer_count:
                scene_risk += 0.15
                risk_factors.append(f"Outnumbered: {scene_context.suspect_count} suspects vs {scene_context.officer_count} officers")
                recommended_actions.append("Request additional units")
            
            if scene_context.confined_space:
                scene_risk += 0.1
                risk_factors.append("Confined space limits tactical options")
            
            if not scene_context.escape_routes_available:
                scene_risk += 0.1
                risk_factors.append("Limited escape routes")
            
            if scene_context.backup_eta_minutes and scene_context.backup_eta_minutes <= 2:
                protective_factors.append(f"Backup arriving in {scene_context.backup_eta_minutes:.1f} minutes")
        
        total_risk = min(1.0, max(0.0, 
            base_risk + 
            escalation_modifier + 
            weapon_risk + 
            proximity_risk + 
            vitals_risk + 
            scene_risk
        ))
        
        if total_risk <= self.risk_thresholds["green_max"]:
            risk_level = RiskLevel.GREEN
        elif total_risk <= self.risk_thresholds["yellow_max"]:
            risk_level = RiskLevel.YELLOW
        else:
            risk_level = RiskLevel.RED
        
        if risk_level == RiskLevel.YELLOW:
            recommended_actions.append("Continue de-escalation efforts")
            recommended_actions.append("Maintain situational awareness")
        elif risk_level == RiskLevel.RED:
            recommended_actions.append("Request immediate backup")
            recommended_actions.append("Notify supervisor immediately")
            recommended_actions.append("Prepare for potential force application")
            if weapon_type == WeaponType.FIREARM:
                recommended_actions.append("Seek cover immediately")
        
        de_escalation_recommended = risk_level in [RiskLevel.YELLOW, RiskLevel.RED]
        if de_escalation_recommended:
            recommended_actions.insert(0, "Attempt verbal de-escalation")
        
        supervisor_notified = False
        rtcc_notified = False
        backup_requested = False
        
        if risk_level == RiskLevel.RED:
            supervisor_notified = True
            rtcc_notified = True
            backup_requested = True
            self._send_supervisor_alert(incident_id, officer_id, risk_level, total_risk, risk_factors)
            self.red_level_incidents.append(incident_id)
        
        assessment = ForceRiskAssessment(
            assessment_id=f"fra-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{officer_id}",
            incident_id=incident_id,
            officer_id=officer_id,
            risk_level=risk_level,
            risk_score=total_risk,
            suspect_behavior=suspect_behavior,
            escalation_pattern=escalation_pattern,
            weapon_detected=weapon_type != WeaponType.NONE,
            weapon_type=weapon_type,
            weapon_probability=weapon_probability,
            officer_proximity_feet=officer_proximity_feet,
            officer_vitals=officer_vitals,
            scene_context=scene_context,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            recommended_actions=recommended_actions,
            supervisor_notified=supervisor_notified,
            rtcc_notified=rtcc_notified,
            backup_requested=backup_requested,
            de_escalation_recommended=de_escalation_recommended,
        )
        
        self.active_assessments[incident_id] = assessment
        self.assessment_history.append(assessment)
        
        return assessment
    
    def _send_supervisor_alert(
        self,
        incident_id: str,
        officer_id: str,
        risk_level: RiskLevel,
        risk_score: float,
        risk_factors: List[str],
    ) -> SupervisorAlert:
        """Send alert to supervisor for red-level risk"""
        alert = SupervisorAlert(
            alert_id=f"sa-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{incident_id}",
            incident_id=incident_id,
            officer_id=officer_id,
            risk_level=risk_level,
            risk_score=risk_score,
            alert_reason="Use-of-force risk level RED - immediate attention required",
            scene_summary="; ".join(risk_factors[:5]),
            recommended_response="Respond to scene immediately or dispatch additional units",
        )
        
        self.supervisor_alerts.append(alert)
        return alert
    
    def update_assessment(
        self,
        incident_id: str,
        **kwargs,
    ) -> Optional[ForceRiskAssessment]:
        """Update existing risk assessment with new data"""
        if incident_id not in self.active_assessments:
            return None
        
        current = self.active_assessments[incident_id]
        
        return self.assess_risk(
            incident_id=incident_id,
            officer_id=current.officer_id,
            suspect_behavior=kwargs.get("suspect_behavior", current.suspect_behavior),
            escalation_pattern=kwargs.get("escalation_pattern", current.escalation_pattern),
            weapon_type=kwargs.get("weapon_type", current.weapon_type),
            weapon_probability=kwargs.get("weapon_probability", current.weapon_probability),
            officer_proximity_feet=kwargs.get("officer_proximity_feet", current.officer_proximity_feet),
            officer_vitals=kwargs.get("officer_vitals", current.officer_vitals),
            scene_context=kwargs.get("scene_context", current.scene_context),
        )
    
    def get_active_assessment(self, incident_id: str) -> Optional[ForceRiskAssessment]:
        """Get active assessment for incident"""
        return self.active_assessments.get(incident_id)
    
    def get_assessment_history(
        self,
        limit: int = 100,
        risk_level_filter: Optional[RiskLevel] = None,
        officer_id: Optional[str] = None,
    ) -> List[ForceRiskAssessment]:
        """Get assessment history with optional filters"""
        history = self.assessment_history
        
        if risk_level_filter:
            history = [a for a in history if a.risk_level == risk_level_filter]
        
        if officer_id:
            history = [a for a in history if a.officer_id == officer_id]
        
        return history[-limit:]
    
    def get_supervisor_alerts(
        self,
        limit: int = 50,
        unacknowledged_only: bool = False,
    ) -> List[SupervisorAlert]:
        """Get supervisor alerts"""
        alerts = self.supervisor_alerts
        
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        
        return alerts[-limit:]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge a supervisor alert"""
        for alert in self.supervisor_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.utcnow()
                return True
        return False
    
    def get_red_level_incidents(self) -> List[str]:
        """Get list of incidents that reached red level"""
        return self.red_level_incidents.copy()
    
    def close_incident(self, incident_id: str) -> bool:
        """Close an incident and remove from active assessments"""
        if incident_id in self.active_assessments:
            del self.active_assessments[incident_id]
            return True
        return False
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """Get risk assessment statistics"""
        if not self.assessment_history:
            return {
                "total_assessments": 0,
                "green_count": 0,
                "yellow_count": 0,
                "red_count": 0,
                "average_risk_score": 0.0,
            }
        
        green_count = sum(1 for a in self.assessment_history if a.risk_level == RiskLevel.GREEN)
        yellow_count = sum(1 for a in self.assessment_history if a.risk_level == RiskLevel.YELLOW)
        red_count = sum(1 for a in self.assessment_history if a.risk_level == RiskLevel.RED)
        avg_score = sum(a.risk_score for a in self.assessment_history) / len(self.assessment_history)
        
        return {
            "total_assessments": len(self.assessment_history),
            "green_count": green_count,
            "yellow_count": yellow_count,
            "red_count": red_count,
            "green_percentage": green_count / len(self.assessment_history) * 100,
            "yellow_percentage": yellow_count / len(self.assessment_history) * 100,
            "red_percentage": red_count / len(self.assessment_history) * 100,
            "average_risk_score": avg_score,
            "active_incidents": len(self.active_assessments),
            "unacknowledged_alerts": sum(1 for a in self.supervisor_alerts if not a.acknowledged),
        }
