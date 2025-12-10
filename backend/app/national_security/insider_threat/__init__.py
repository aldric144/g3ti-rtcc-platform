"""
Insider Threat Module

Provides insider threat detection capabilities including:
- Employee risk profiling
- Behavior deviation engine
- Access anomaly detection
- Role-based threat scoring
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import uuid
import statistics


class RiskLevel(Enum):
    """Risk levels for insider threats."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class BehaviorType(Enum):
    """Types of monitored behaviors."""
    ACCESS_PATTERN = "access_pattern"
    DATA_TRANSFER = "data_transfer"
    COMMUNICATION = "communication"
    WORK_HOURS = "work_hours"
    SYSTEM_USAGE = "system_usage"
    NETWORK_ACTIVITY = "network_activity"
    PHYSICAL_ACCESS = "physical_access"
    POLICY_VIOLATION = "policy_violation"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    RESIGNATION_INDICATOR = "resignation_indicator"
    FINANCIAL_STRESS = "financial_stress"
    PERFORMANCE_CHANGE = "performance_change"


class AnomalyType(Enum):
    """Types of access anomalies."""
    UNUSUAL_TIME = "unusual_time"
    UNUSUAL_LOCATION = "unusual_location"
    UNUSUAL_DEVICE = "unusual_device"
    EXCESSIVE_ACCESS = "excessive_access"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PRIVILEGE_ABUSE = "privilege_abuse"
    DATA_EXFILTRATION = "data_exfiltration"
    CREDENTIAL_SHARING = "credential_sharing"
    FAILED_AUTHENTICATION = "failed_authentication"
    POLICY_BYPASS = "policy_bypass"
    SUSPICIOUS_QUERY = "suspicious_query"
    BULK_DOWNLOAD = "bulk_download"


class DepartmentType(Enum):
    """Department types for role-based analysis."""
    EXECUTIVE = "executive"
    FINANCE = "finance"
    HR = "human_resources"
    IT = "information_technology"
    SECURITY = "security"
    LEGAL = "legal"
    OPERATIONS = "operations"
    RESEARCH = "research"
    SALES = "sales"
    MARKETING = "marketing"
    ENGINEERING = "engineering"
    SUPPORT = "support"
    CONTRACTOR = "contractor"
    OTHER = "other"


class ClearanceLevel(Enum):
    """Security clearance levels."""
    UNCLASSIFIED = "unclassified"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    SCI = "sensitive_compartmented_information"


@dataclass
class EmployeeRiskProfile:
    """Risk profile for an employee."""
    profile_id: str
    employee_id: str
    employee_name: str
    department: DepartmentType
    clearance_level: ClearanceLevel
    role: str
    hire_date: datetime
    risk_level: RiskLevel
    risk_score: float
    risk_factors: List[str]
    behavior_baseline: Dict[str, Any]
    recent_deviations: List[str]
    access_level: int
    is_privileged: bool
    is_contractor: bool
    manager_id: Optional[str]
    last_assessment: datetime
    next_assessment: datetime
    notes: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehaviorDeviation:
    """Represents a detected behavior deviation."""
    deviation_id: str
    employee_id: str
    behavior_type: BehaviorType
    description: str
    baseline_value: Any
    observed_value: Any
    deviation_score: float
    severity: RiskLevel
    detected_at: datetime
    context: Dict[str, Any]
    is_acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    resolution: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessAnomaly:
    """Represents a detected access anomaly."""
    anomaly_id: str
    employee_id: str
    anomaly_type: AnomalyType
    description: str
    resource_accessed: str
    access_time: datetime
    source_ip: Optional[str]
    source_device: Optional[str]
    source_location: Optional[str]
    expected_pattern: Dict[str, Any]
    observed_pattern: Dict[str, Any]
    risk_score: float
    severity: RiskLevel
    is_false_positive: bool
    investigation_status: str
    detected_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatAssessment:
    """Comprehensive threat assessment for an employee."""
    assessment_id: str
    employee_id: str
    assessment_date: datetime
    overall_risk_level: RiskLevel
    overall_risk_score: float
    behavior_score: float
    access_score: float
    role_score: float
    historical_score: float
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    deviations_count: int
    anomalies_count: int
    trend: str
    assessor_id: Optional[str]
    next_review: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class InsiderThreatEngine:
    """
    Insider Threat Detection Engine.
    
    Provides capabilities for:
    - Employee risk profiling
    - Behavior deviation detection
    - Access anomaly detection
    - Role-based threat scoring
    """

    def __init__(self):
        self.risk_profiles: Dict[str, EmployeeRiskProfile] = {}
        self.behavior_deviations: Dict[str, BehaviorDeviation] = {}
        self.access_anomalies: Dict[str, AccessAnomaly] = {}
        self.threat_assessments: Dict[str, ThreatAssessment] = {}
        self.behavior_baselines: Dict[str, Dict[str, Any]] = {}
        self.risk_weights: Dict[str, float] = {
            "behavior": 0.30,
            "access": 0.25,
            "role": 0.20,
            "historical": 0.15,
            "external": 0.10,
        }

    def create_risk_profile(
        self,
        employee_id: str,
        employee_name: str,
        department: DepartmentType,
        role: str,
        clearance_level: ClearanceLevel = ClearanceLevel.UNCLASSIFIED,
        hire_date: Optional[datetime] = None,
        access_level: int = 1,
        is_privileged: bool = False,
        is_contractor: bool = False,
        manager_id: Optional[str] = None,
    ) -> EmployeeRiskProfile:
        """Create a risk profile for an employee."""
        profile_id = f"rp-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        initial_risk_score = self._calculate_initial_risk_score(
            department, clearance_level, access_level, is_privileged, is_contractor
        )
        
        risk_level = self._score_to_risk_level(initial_risk_score)
        
        profile = EmployeeRiskProfile(
            profile_id=profile_id,
            employee_id=employee_id,
            employee_name=employee_name,
            department=department,
            clearance_level=clearance_level,
            role=role,
            hire_date=hire_date or now,
            risk_level=risk_level,
            risk_score=initial_risk_score,
            risk_factors=[],
            behavior_baseline={},
            recent_deviations=[],
            access_level=access_level,
            is_privileged=is_privileged,
            is_contractor=is_contractor,
            manager_id=manager_id,
            last_assessment=now,
            next_assessment=now + timedelta(days=30),
            notes=[],
        )
        
        self.risk_profiles[employee_id] = profile
        return profile

    def _calculate_initial_risk_score(
        self,
        department: DepartmentType,
        clearance_level: ClearanceLevel,
        access_level: int,
        is_privileged: bool,
        is_contractor: bool,
    ) -> float:
        """Calculate initial risk score based on role factors."""
        score = 10.0
        
        high_risk_departments = [
            DepartmentType.IT, DepartmentType.FINANCE, 
            DepartmentType.SECURITY, DepartmentType.EXECUTIVE
        ]
        if department in high_risk_departments:
            score += 10
        
        clearance_scores = {
            ClearanceLevel.UNCLASSIFIED: 0,
            ClearanceLevel.CONFIDENTIAL: 5,
            ClearanceLevel.SECRET: 10,
            ClearanceLevel.TOP_SECRET: 15,
            ClearanceLevel.SCI: 20,
        }
        score += clearance_scores.get(clearance_level, 0)
        
        score += min(15, access_level * 3)
        
        if is_privileged:
            score += 15
        
        if is_contractor:
            score += 10
        
        return min(100, score)

    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score < 20:
            return RiskLevel.MINIMAL
        elif score < 35:
            return RiskLevel.LOW
        elif score < 50:
            return RiskLevel.MODERATE
        elif score < 65:
            return RiskLevel.ELEVATED
        elif score < 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def get_risk_profile(self, employee_id: str) -> Optional[EmployeeRiskProfile]:
        """Get risk profile for an employee."""
        return self.risk_profiles.get(employee_id)

    def get_risk_profiles(
        self,
        department: Optional[DepartmentType] = None,
        risk_level: Optional[RiskLevel] = None,
        min_risk_score: float = 0,
        privileged_only: bool = False,
        limit: int = 100,
    ) -> List[EmployeeRiskProfile]:
        """Retrieve risk profiles with optional filtering."""
        profiles = list(self.risk_profiles.values())
        
        if department:
            profiles = [p for p in profiles if p.department == department]
        
        if risk_level:
            risk_order = list(RiskLevel)
            min_index = risk_order.index(risk_level)
            profiles = [p for p in profiles if risk_order.index(p.risk_level) >= min_index]
        
        profiles = [p for p in profiles if p.risk_score >= min_risk_score]
        
        if privileged_only:
            profiles = [p for p in profiles if p.is_privileged]
        
        profiles.sort(key=lambda x: x.risk_score, reverse=True)
        return profiles[:limit]

    def set_behavior_baseline(
        self,
        employee_id: str,
        baseline_data: Dict[str, Any],
    ) -> bool:
        """Set behavior baseline for an employee."""
        if employee_id not in self.risk_profiles:
            return False
        
        self.behavior_baselines[employee_id] = {
            "data": baseline_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        self.risk_profiles[employee_id].behavior_baseline = baseline_data
        return True

    def detect_behavior_deviation(
        self,
        employee_id: str,
        behavior_type: BehaviorType,
        observed_value: Any,
        description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[BehaviorDeviation]:
        """Detect and record a behavior deviation."""
        profile = self.risk_profiles.get(employee_id)
        if not profile:
            return None
        
        baseline = self.behavior_baselines.get(employee_id, {}).get("data", {})
        baseline_value = baseline.get(behavior_type.value)
        
        deviation_score = self._calculate_deviation_score(
            behavior_type, baseline_value, observed_value
        )
        
        if deviation_score < 20:
            return None
        
        deviation_id = f"bd-{uuid.uuid4().hex[:12]}"
        severity = self._score_to_risk_level(deviation_score)
        
        deviation = BehaviorDeviation(
            deviation_id=deviation_id,
            employee_id=employee_id,
            behavior_type=behavior_type,
            description=description,
            baseline_value=baseline_value,
            observed_value=observed_value,
            deviation_score=deviation_score,
            severity=severity,
            detected_at=datetime.utcnow(),
            context=context or {},
            is_acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None,
            resolution=None,
        )
        
        self.behavior_deviations[deviation_id] = deviation
        
        profile.recent_deviations.append(deviation_id)
        if len(profile.recent_deviations) > 10:
            profile.recent_deviations = profile.recent_deviations[-10:]
        
        self._update_risk_score(employee_id)
        
        return deviation

    def _calculate_deviation_score(
        self,
        behavior_type: BehaviorType,
        baseline_value: Any,
        observed_value: Any,
    ) -> float:
        """Calculate deviation score based on behavior type."""
        if baseline_value is None:
            return 30.0
        
        high_risk_behaviors = [
            BehaviorType.DATA_TRANSFER,
            BehaviorType.PRIVILEGE_ESCALATION,
            BehaviorType.POLICY_VIOLATION,
            BehaviorType.RESIGNATION_INDICATOR,
        ]
        
        base_score = 40.0 if behavior_type in high_risk_behaviors else 25.0
        
        if isinstance(baseline_value, (int, float)) and isinstance(observed_value, (int, float)):
            if baseline_value > 0:
                ratio = abs(observed_value - baseline_value) / baseline_value
                base_score += min(40, ratio * 20)
        
        return min(100, base_score)

    def get_behavior_deviations(
        self,
        employee_id: Optional[str] = None,
        behavior_type: Optional[BehaviorType] = None,
        severity: Optional[RiskLevel] = None,
        unacknowledged_only: bool = False,
        limit: int = 100,
    ) -> List[BehaviorDeviation]:
        """Retrieve behavior deviations with optional filtering."""
        deviations = list(self.behavior_deviations.values())
        
        if employee_id:
            deviations = [d for d in deviations if d.employee_id == employee_id]
        
        if behavior_type:
            deviations = [d for d in deviations if d.behavior_type == behavior_type]
        
        if severity:
            risk_order = list(RiskLevel)
            min_index = risk_order.index(severity)
            deviations = [d for d in deviations if risk_order.index(d.severity) >= min_index]
        
        if unacknowledged_only:
            deviations = [d for d in deviations if not d.is_acknowledged]
        
        deviations.sort(key=lambda x: x.detected_at, reverse=True)
        return deviations[:limit]

    def detect_access_anomaly(
        self,
        employee_id: str,
        anomaly_type: AnomalyType,
        resource_accessed: str,
        description: str,
        source_ip: Optional[str] = None,
        source_device: Optional[str] = None,
        source_location: Optional[str] = None,
        expected_pattern: Optional[Dict[str, Any]] = None,
        observed_pattern: Optional[Dict[str, Any]] = None,
    ) -> Optional[AccessAnomaly]:
        """Detect and record an access anomaly."""
        profile = self.risk_profiles.get(employee_id)
        if not profile:
            return None
        
        risk_score = self._calculate_anomaly_risk_score(
            anomaly_type, profile.clearance_level, profile.is_privileged
        )
        
        anomaly_id = f"aa-{uuid.uuid4().hex[:12]}"
        severity = self._score_to_risk_level(risk_score)
        
        anomaly = AccessAnomaly(
            anomaly_id=anomaly_id,
            employee_id=employee_id,
            anomaly_type=anomaly_type,
            description=description,
            resource_accessed=resource_accessed,
            access_time=datetime.utcnow(),
            source_ip=source_ip,
            source_device=source_device,
            source_location=source_location,
            expected_pattern=expected_pattern or {},
            observed_pattern=observed_pattern or {},
            risk_score=risk_score,
            severity=severity,
            is_false_positive=False,
            investigation_status="open",
            detected_at=datetime.utcnow(),
        )
        
        self.access_anomalies[anomaly_id] = anomaly
        
        self._update_risk_score(employee_id)
        
        return anomaly

    def _calculate_anomaly_risk_score(
        self,
        anomaly_type: AnomalyType,
        clearance_level: ClearanceLevel,
        is_privileged: bool,
    ) -> float:
        """Calculate risk score for an access anomaly."""
        type_scores = {
            AnomalyType.UNUSUAL_TIME: 25,
            AnomalyType.UNUSUAL_LOCATION: 35,
            AnomalyType.UNUSUAL_DEVICE: 30,
            AnomalyType.EXCESSIVE_ACCESS: 45,
            AnomalyType.UNAUTHORIZED_ACCESS: 70,
            AnomalyType.PRIVILEGE_ABUSE: 75,
            AnomalyType.DATA_EXFILTRATION: 90,
            AnomalyType.CREDENTIAL_SHARING: 60,
            AnomalyType.FAILED_AUTHENTICATION: 40,
            AnomalyType.POLICY_BYPASS: 55,
            AnomalyType.SUSPICIOUS_QUERY: 50,
            AnomalyType.BULK_DOWNLOAD: 65,
        }
        
        score = type_scores.get(anomaly_type, 40)
        
        clearance_multipliers = {
            ClearanceLevel.UNCLASSIFIED: 1.0,
            ClearanceLevel.CONFIDENTIAL: 1.1,
            ClearanceLevel.SECRET: 1.2,
            ClearanceLevel.TOP_SECRET: 1.3,
            ClearanceLevel.SCI: 1.4,
        }
        score *= clearance_multipliers.get(clearance_level, 1.0)
        
        if is_privileged:
            score *= 1.2
        
        return min(100, score)

    def get_access_anomalies(
        self,
        employee_id: Optional[str] = None,
        anomaly_type: Optional[AnomalyType] = None,
        severity: Optional[RiskLevel] = None,
        investigation_status: Optional[str] = None,
        limit: int = 100,
    ) -> List[AccessAnomaly]:
        """Retrieve access anomalies with optional filtering."""
        anomalies = list(self.access_anomalies.values())
        
        if employee_id:
            anomalies = [a for a in anomalies if a.employee_id == employee_id]
        
        if anomaly_type:
            anomalies = [a for a in anomalies if a.anomaly_type == anomaly_type]
        
        if severity:
            risk_order = list(RiskLevel)
            min_index = risk_order.index(severity)
            anomalies = [a for a in anomalies if risk_order.index(a.severity) >= min_index]
        
        if investigation_status:
            anomalies = [a for a in anomalies if a.investigation_status == investigation_status]
        
        anomalies.sort(key=lambda x: x.risk_score, reverse=True)
        return anomalies[:limit]

    def _update_risk_score(self, employee_id: str) -> None:
        """Update risk score for an employee based on recent activity."""
        profile = self.risk_profiles.get(employee_id)
        if not profile:
            return
        
        recent_deviations = [
            self.behavior_deviations[d_id]
            for d_id in profile.recent_deviations
            if d_id in self.behavior_deviations
        ]
        
        recent_anomalies = [
            a for a in self.access_anomalies.values()
            if a.employee_id == employee_id
            and (datetime.utcnow() - a.detected_at).days < 30
        ]
        
        behavior_score = sum(d.deviation_score for d in recent_deviations) / max(1, len(recent_deviations))
        access_score = sum(a.risk_score for a in recent_anomalies) / max(1, len(recent_anomalies))
        
        role_score = self._calculate_initial_risk_score(
            profile.department, profile.clearance_level,
            profile.access_level, profile.is_privileged, profile.is_contractor
        )
        
        historical_score = profile.risk_score
        
        new_score = (
            behavior_score * self.risk_weights["behavior"] +
            access_score * self.risk_weights["access"] +
            role_score * self.risk_weights["role"] +
            historical_score * self.risk_weights["historical"]
        )
        
        profile.risk_score = min(100, new_score)
        profile.risk_level = self._score_to_risk_level(profile.risk_score)

    def create_threat_assessment(
        self,
        employee_id: str,
        assessor_id: Optional[str] = None,
    ) -> Optional[ThreatAssessment]:
        """Create a comprehensive threat assessment for an employee."""
        profile = self.risk_profiles.get(employee_id)
        if not profile:
            return None
        
        assessment_id = f"ta-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        recent_deviations = [
            self.behavior_deviations[d_id]
            for d_id in profile.recent_deviations
            if d_id in self.behavior_deviations
        ]
        
        recent_anomalies = [
            a for a in self.access_anomalies.values()
            if a.employee_id == employee_id
            and (now - a.detected_at).days < 30
        ]
        
        behavior_score = sum(d.deviation_score for d in recent_deviations) / max(1, len(recent_deviations)) if recent_deviations else 0
        access_score = sum(a.risk_score for a in recent_anomalies) / max(1, len(recent_anomalies)) if recent_anomalies else 0
        role_score = self._calculate_initial_risk_score(
            profile.department, profile.clearance_level,
            profile.access_level, profile.is_privileged, profile.is_contractor
        )
        historical_score = profile.risk_score
        
        overall_score = (
            behavior_score * self.risk_weights["behavior"] +
            access_score * self.risk_weights["access"] +
            role_score * self.risk_weights["role"] +
            historical_score * self.risk_weights["historical"]
        )
        
        risk_factors = self._identify_risk_factors(profile, recent_deviations, recent_anomalies)
        recommendations = self._generate_recommendations(profile, risk_factors)
        
        trend = self._calculate_trend(employee_id)
        
        assessment = ThreatAssessment(
            assessment_id=assessment_id,
            employee_id=employee_id,
            assessment_date=now,
            overall_risk_level=self._score_to_risk_level(overall_score),
            overall_risk_score=overall_score,
            behavior_score=behavior_score,
            access_score=access_score,
            role_score=role_score,
            historical_score=historical_score,
            risk_factors=risk_factors,
            recommendations=recommendations,
            deviations_count=len(recent_deviations),
            anomalies_count=len(recent_anomalies),
            trend=trend,
            assessor_id=assessor_id,
            next_review=now + timedelta(days=30),
        )
        
        self.threat_assessments[assessment_id] = assessment
        
        profile.last_assessment = now
        profile.next_assessment = now + timedelta(days=30)
        profile.risk_factors = [f["description"] for f in risk_factors]
        
        return assessment

    def _identify_risk_factors(
        self,
        profile: EmployeeRiskProfile,
        deviations: List[BehaviorDeviation],
        anomalies: List[AccessAnomaly],
    ) -> List[Dict[str, Any]]:
        """Identify risk factors for an employee."""
        factors = []
        
        if profile.is_privileged:
            factors.append({
                "type": "role",
                "description": "Privileged access user",
                "weight": 0.15,
            })
        
        if profile.is_contractor:
            factors.append({
                "type": "role",
                "description": "External contractor",
                "weight": 0.10,
            })
        
        if profile.clearance_level in [ClearanceLevel.TOP_SECRET, ClearanceLevel.SCI]:
            factors.append({
                "type": "clearance",
                "description": f"High clearance level: {profile.clearance_level.value}",
                "weight": 0.15,
            })
        
        high_severity_deviations = [d for d in deviations if d.severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if high_severity_deviations:
            factors.append({
                "type": "behavior",
                "description": f"{len(high_severity_deviations)} high-severity behavior deviations",
                "weight": 0.20,
            })
        
        high_risk_anomalies = [a for a in anomalies if a.severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if high_risk_anomalies:
            factors.append({
                "type": "access",
                "description": f"{len(high_risk_anomalies)} high-risk access anomalies",
                "weight": 0.25,
            })
        
        data_exfil = [a for a in anomalies if a.anomaly_type == AnomalyType.DATA_EXFILTRATION]
        if data_exfil:
            factors.append({
                "type": "critical",
                "description": "Potential data exfiltration detected",
                "weight": 0.30,
            })
        
        return factors

    def _generate_recommendations(
        self,
        profile: EmployeeRiskProfile,
        risk_factors: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate recommendations based on risk factors."""
        recommendations = []
        
        factor_types = [f["type"] for f in risk_factors]
        
        if "critical" in factor_types:
            recommendations.append("Immediate investigation required")
            recommendations.append("Consider temporary access suspension")
        
        if "access" in factor_types:
            recommendations.append("Review and audit access permissions")
            recommendations.append("Enable enhanced monitoring")
        
        if "behavior" in factor_types:
            recommendations.append("Schedule manager review meeting")
            recommendations.append("Increase behavior monitoring frequency")
        
        if profile.is_privileged:
            recommendations.append("Verify privileged access necessity")
            recommendations.append("Implement additional access controls")
        
        if not recommendations:
            recommendations.append("Continue standard monitoring")
        
        return recommendations

    def _calculate_trend(self, employee_id: str) -> str:
        """Calculate risk trend for an employee."""
        assessments = [
            a for a in self.threat_assessments.values()
            if a.employee_id == employee_id
        ]
        
        if len(assessments) < 2:
            return "stable"
        
        assessments.sort(key=lambda x: x.assessment_date)
        recent = assessments[-3:] if len(assessments) >= 3 else assessments
        
        scores = [a.overall_risk_score for a in recent]
        if len(scores) >= 2:
            if scores[-1] > scores[0] * 1.1:
                return "increasing"
            elif scores[-1] < scores[0] * 0.9:
                return "decreasing"
        
        return "stable"

    def get_threat_assessments(
        self,
        employee_id: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        limit: int = 100,
    ) -> List[ThreatAssessment]:
        """Retrieve threat assessments with optional filtering."""
        assessments = list(self.threat_assessments.values())
        
        if employee_id:
            assessments = [a for a in assessments if a.employee_id == employee_id]
        
        if risk_level:
            risk_order = list(RiskLevel)
            min_index = risk_order.index(risk_level)
            assessments = [a for a in assessments if risk_order.index(a.overall_risk_level) >= min_index]
        
        assessments.sort(key=lambda x: x.overall_risk_score, reverse=True)
        return assessments[:limit]

    def acknowledge_deviation(
        self,
        deviation_id: str,
        acknowledged_by: str,
        resolution: Optional[str] = None,
    ) -> bool:
        """Acknowledge a behavior deviation."""
        deviation = self.behavior_deviations.get(deviation_id)
        if not deviation:
            return False
        
        deviation.is_acknowledged = True
        deviation.acknowledged_by = acknowledged_by
        deviation.acknowledged_at = datetime.utcnow()
        deviation.resolution = resolution
        return True

    def update_anomaly_status(
        self,
        anomaly_id: str,
        status: str,
        is_false_positive: bool = False,
    ) -> bool:
        """Update investigation status of an access anomaly."""
        anomaly = self.access_anomalies.get(anomaly_id)
        if not anomaly:
            return False
        
        anomaly.investigation_status = status
        anomaly.is_false_positive = is_false_positive
        return True

    def get_high_risk_employees(
        self,
        min_risk_score: float = 65,
        limit: int = 50,
    ) -> List[EmployeeRiskProfile]:
        """Get employees with high risk scores."""
        profiles = [p for p in self.risk_profiles.values() if p.risk_score >= min_risk_score]
        profiles.sort(key=lambda x: x.risk_score, reverse=True)
        return profiles[:limit]

    def get_metrics(self) -> Dict[str, Any]:
        """Get insider threat metrics."""
        profiles = list(self.risk_profiles.values())
        
        risk_distribution = {}
        for level in RiskLevel:
            risk_distribution[level.value] = len([p for p in profiles if p.risk_level == level])
        
        department_distribution = {}
        for dept in DepartmentType:
            count = len([p for p in profiles if p.department == dept])
            if count > 0:
                department_distribution[dept.value] = count
        
        return {
            "total_profiles": len(profiles),
            "privileged_users": len([p for p in profiles if p.is_privileged]),
            "contractors": len([p for p in profiles if p.is_contractor]),
            "total_deviations": len(self.behavior_deviations),
            "unacknowledged_deviations": len([d for d in self.behavior_deviations.values() if not d.is_acknowledged]),
            "total_anomalies": len(self.access_anomalies),
            "open_investigations": len([a for a in self.access_anomalies.values() if a.investigation_status == "open"]),
            "total_assessments": len(self.threat_assessments),
            "risk_distribution": risk_distribution,
            "department_distribution": department_distribution,
            "average_risk_score": statistics.mean([p.risk_score for p in profiles]) if profiles else 0,
        }
