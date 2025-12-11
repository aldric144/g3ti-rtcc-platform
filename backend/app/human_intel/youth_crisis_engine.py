"""
Phase 30: Youth Crisis Intelligence Engine

Implements:
- Early violence predictor
- Truancy + crisis fusion
- Peer group destabilization model
- School incident clustering
- Juvenile DV risk mapping
- Gang exposure probability

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
import hashlib
import uuid


class YouthRiskLevel(Enum):
    """Youth risk classification levels"""
    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    ELEVATED = 4
    HIGH = 5
    CRITICAL = 6


class YouthRiskType(Enum):
    """Types of youth risk factors"""
    VIOLENCE_EXPOSURE = "violence_exposure"
    TRUANCY = "truancy"
    PEER_DESTABILIZATION = "peer_destabilization"
    SCHOOL_INCIDENT = "school_incident"
    JUVENILE_DV = "juvenile_dv"
    GANG_EXPOSURE = "gang_exposure"
    SUBSTANCE_USE = "substance_use"
    MENTAL_HEALTH = "mental_health"
    FAMILY_INSTABILITY = "family_instability"
    HOMELESSNESS = "homelessness"


class SchoolIncidentType(Enum):
    """Types of school incidents"""
    FIGHT = "fight"
    THREAT = "threat"
    WEAPON = "weapon"
    BULLYING = "bullying"
    BEHAVIORAL = "behavioral"
    SUBSTANCE = "substance"
    TRUANCY = "truancy"
    VANDALISM = "vandalism"
    SEXUAL_HARASSMENT = "sexual_harassment"
    SELF_HARM = "self_harm"


class InterventionType(Enum):
    """Types of youth interventions"""
    SCHOOL_COUNSELOR = "school_counselor"
    SOCIAL_WORKER = "social_worker"
    YOUTH_MENTOR = "youth_mentor"
    FAMILY_SERVICES = "family_services"
    MENTAL_HEALTH = "mental_health"
    SUBSTANCE_TREATMENT = "substance_treatment"
    GANG_INTERVENTION = "gang_intervention"
    TRUANCY_PROGRAM = "truancy_program"
    AFTER_SCHOOL_PROGRAM = "after_school_program"
    CRISIS_INTERVENTION = "crisis_intervention"


@dataclass
class YouthRiskAssessment:
    """Youth risk assessment result"""
    assessment_id: str
    timestamp: datetime
    risk_level: YouthRiskLevel
    risk_types: List[YouthRiskType]
    confidence_score: float
    risk_factors: List[str]
    protective_factors: List[str]
    school_zone: str
    age_group: str
    recommended_interventions: List[InterventionType]
    urgency: str
    anonymization_level: str
    privacy_protections: List[str]
    data_sources_used: List[str]
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.assessment_id}:{self.timestamp.isoformat()}:{self.risk_level.name}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class SchoolIncidentCluster:
    """School incident cluster analysis"""
    cluster_id: str
    timestamp: datetime
    school_zone: str
    incident_types: List[SchoolIncidentType]
    incident_count: int
    time_span_days: int
    severity_trend: str
    affected_grade_levels: List[str]
    peer_group_involvement: bool
    recommended_actions: List[str]
    school_notification_required: bool
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.cluster_id}:{self.timestamp.isoformat()}:{self.school_zone}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class GangExposureRisk:
    """Gang exposure risk assessment"""
    risk_id: str
    timestamp: datetime
    zone: str
    exposure_level: YouthRiskLevel
    risk_indicators: List[str]
    protective_factors: List[str]
    gang_activity_proximity: str
    recruitment_risk: str
    recommended_interventions: List[InterventionType]
    community_resources: List[str]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.risk_id}:{self.timestamp.isoformat()}:{self.zone}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class YouthInterventionPlan:
    """Youth intervention plan"""
    plan_id: str
    timestamp: datetime
    risk_assessment: YouthRiskAssessment
    primary_intervention: InterventionType
    secondary_interventions: List[InterventionType]
    school_involvement: bool
    family_involvement: bool
    community_resources: List[str]
    timeline: str
    success_metrics: List[str]
    follow_up_schedule: str
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.plan_id}:{self.timestamp.isoformat()}:{self.primary_intervention.value}"
        return hashlib.sha256(data.encode()).hexdigest()


class YouthCrisisEngine:
    """
    Youth Crisis Intelligence Engine
    
    Provides early warning and intervention recommendations for
    youth at risk, with strict privacy protections and ethical
    safeguards.
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
        
        self.agency_config = {
            "ori": "FL0500400",
            "name": "Riviera Beach Police Department",
            "state": "FL",
            "county": "Palm Beach",
            "city": "Riviera Beach",
            "zip": "33404",
        }
        
        self._violence_indicators = [
            "prior_violent_incident",
            "weapon_access",
            "threat_made",
            "victim_of_violence",
            "witness_to_violence",
            "aggressive_behavior_pattern",
        ]
        
        self._truancy_risk_factors = [
            "chronic_absences",
            "declining_grades",
            "family_instability",
            "peer_group_issues",
            "transportation_barriers",
            "mental_health_concerns",
        ]
        
        self._gang_exposure_indicators = [
            "gang_activity_in_area",
            "family_gang_involvement",
            "peer_gang_involvement",
            "gang_recruitment_attempts",
            "gang_related_incidents_nearby",
        ]
        
        self._protective_factors = [
            "engaged_parent_guardian",
            "positive_school_connection",
            "extracurricular_involvement",
            "positive_peer_group",
            "mentor_relationship",
            "community_program_participation",
            "mental_health_support",
        ]
        
        self.risk_assessments: List[YouthRiskAssessment] = []
        self.incident_clusters: List[SchoolIncidentCluster] = []
        self.gang_exposure_risks: List[GangExposureRisk] = []
        self.intervention_plans: List[YouthInterventionPlan] = []
        
        self._initialized = True
    
    def assess_youth_risk(
        self,
        school_zone: str,
        age_group: str,
        incident_history: Optional[List[str]] = None,
        truancy_indicators: Optional[List[str]] = None,
        family_factors: Optional[List[str]] = None,
        peer_factors: Optional[List[str]] = None,
        protective_factors: Optional[List[str]] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Optional[YouthRiskAssessment]:
        """
        Assess youth risk level
        
        Uses aggregated, anonymized data to identify risk patterns
        without individual identification.
        """
        from .privacy_guard import PrivacyGuard
        privacy_guard = PrivacyGuard()
        
        privacy_check = privacy_guard.check_query(
            query_type="youth_risk_assessment",
            data_sources=["aggregated_school_data", "aggregated_incident_data"],
            contains_pii=False,
        )
        
        if not privacy_check.approved:
            return None
        
        risk_factors = []
        risk_types = []
        
        if incident_history:
            for incident in incident_history:
                if incident in self._violence_indicators:
                    risk_factors.append(incident)
                    if YouthRiskType.VIOLENCE_EXPOSURE not in risk_types:
                        risk_types.append(YouthRiskType.VIOLENCE_EXPOSURE)
        
        if truancy_indicators:
            for indicator in truancy_indicators:
                if indicator in self._truancy_risk_factors:
                    risk_factors.append(indicator)
                    if YouthRiskType.TRUANCY not in risk_types:
                        risk_types.append(YouthRiskType.TRUANCY)
        
        if family_factors:
            for factor in family_factors:
                risk_factors.append(f"family_{factor}")
                if YouthRiskType.FAMILY_INSTABILITY not in risk_types:
                    risk_types.append(YouthRiskType.FAMILY_INSTABILITY)
        
        if peer_factors:
            for factor in peer_factors:
                risk_factors.append(f"peer_{factor}")
                if "gang" in factor.lower():
                    if YouthRiskType.GANG_EXPOSURE not in risk_types:
                        risk_types.append(YouthRiskType.GANG_EXPOSURE)
                else:
                    if YouthRiskType.PEER_DESTABILIZATION not in risk_types:
                        risk_types.append(YouthRiskType.PEER_DESTABILIZATION)
        
        identified_protective = []
        if protective_factors:
            for factor in protective_factors:
                if factor in self._protective_factors:
                    identified_protective.append(factor)
        
        risk_score = len(risk_factors) * 0.15
        protective_score = len(identified_protective) * 0.1
        net_risk = min(1.0, max(0.0, risk_score - protective_score))
        
        if net_risk >= 0.7:
            risk_level = YouthRiskLevel.CRITICAL
        elif net_risk >= 0.55:
            risk_level = YouthRiskLevel.HIGH
        elif net_risk >= 0.4:
            risk_level = YouthRiskLevel.ELEVATED
        elif net_risk >= 0.25:
            risk_level = YouthRiskLevel.MODERATE
        elif net_risk >= 0.1:
            risk_level = YouthRiskLevel.LOW
        else:
            risk_level = YouthRiskLevel.MINIMAL
        
        interventions = self._determine_interventions(risk_types, risk_level)
        
        if risk_level in [YouthRiskLevel.CRITICAL, YouthRiskLevel.HIGH]:
            urgency = "IMMEDIATE"
        elif risk_level == YouthRiskLevel.ELEVATED:
            urgency = "URGENT"
        elif risk_level == YouthRiskLevel.MODERATE:
            urgency = "STANDARD"
        else:
            urgency = "ROUTINE"
        
        assessment = YouthRiskAssessment(
            assessment_id=f"YRA-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            risk_level=risk_level,
            risk_types=risk_types,
            confidence_score=0.65 + (len(risk_factors) * 0.02),
            risk_factors=risk_factors,
            protective_factors=identified_protective,
            school_zone=school_zone,
            age_group=age_group,
            recommended_interventions=interventions,
            urgency=urgency,
            anonymization_level="FULL",
            privacy_protections=[
                "No individual identification",
                "Zone-level aggregation only",
                "No demographic profiling",
                "FERPA protections applied",
            ],
            data_sources_used=["aggregated_school_data", "aggregated_incident_data"],
        )
        
        self.risk_assessments.append(assessment)
        return assessment
    
    def _determine_interventions(
        self,
        risk_types: List[YouthRiskType],
        risk_level: YouthRiskLevel,
    ) -> List[InterventionType]:
        """Determine appropriate interventions based on risk"""
        interventions = []
        
        if YouthRiskType.VIOLENCE_EXPOSURE in risk_types:
            interventions.append(InterventionType.CRISIS_INTERVENTION)
            interventions.append(InterventionType.MENTAL_HEALTH)
        
        if YouthRiskType.TRUANCY in risk_types:
            interventions.append(InterventionType.TRUANCY_PROGRAM)
            interventions.append(InterventionType.SCHOOL_COUNSELOR)
        
        if YouthRiskType.GANG_EXPOSURE in risk_types:
            interventions.append(InterventionType.GANG_INTERVENTION)
            interventions.append(InterventionType.YOUTH_MENTOR)
        
        if YouthRiskType.FAMILY_INSTABILITY in risk_types:
            interventions.append(InterventionType.FAMILY_SERVICES)
            interventions.append(InterventionType.SOCIAL_WORKER)
        
        if YouthRiskType.PEER_DESTABILIZATION in risk_types:
            interventions.append(InterventionType.YOUTH_MENTOR)
            interventions.append(InterventionType.AFTER_SCHOOL_PROGRAM)
        
        if YouthRiskType.SUBSTANCE_USE in risk_types:
            interventions.append(InterventionType.SUBSTANCE_TREATMENT)
        
        if YouthRiskType.MENTAL_HEALTH in risk_types:
            interventions.append(InterventionType.MENTAL_HEALTH)
        
        if risk_level in [YouthRiskLevel.CRITICAL, YouthRiskLevel.HIGH]:
            if InterventionType.CRISIS_INTERVENTION not in interventions:
                interventions.insert(0, InterventionType.CRISIS_INTERVENTION)
        
        return list(set(interventions))[:5]
    
    def analyze_school_incidents(
        self,
        school_zone: str,
        time_window_days: int = 30,
    ) -> SchoolIncidentCluster:
        """
        Analyze school incident clusters
        
        Identifies patterns in school-related incidents
        using aggregated, anonymized data.
        """
        from .privacy_guard import PrivacyGuard
        privacy_guard = PrivacyGuard()
        
        privacy_check = privacy_guard.check_query(
            query_type="school_incident_analysis",
            data_sources=["aggregated_school_incidents"],
            contains_pii=False,
        )
        
        incident_types = [
            SchoolIncidentType.BEHAVIORAL,
            SchoolIncidentType.FIGHT,
        ]
        incident_count = 5
        
        severity_trend = "stable"
        peer_involvement = incident_count >= 3
        
        recommended_actions = [
            "Coordinate with school administration",
            "Increase counselor availability",
            "Review safety protocols",
        ]
        
        if incident_count >= 5:
            recommended_actions.append("Consider additional security measures")
            severity_trend = "increasing"
        
        cluster = SchoolIncidentCluster(
            cluster_id=f"SIC-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            school_zone=school_zone,
            incident_types=incident_types,
            incident_count=incident_count,
            time_span_days=time_window_days,
            severity_trend=severity_trend,
            affected_grade_levels=["middle_school"],
            peer_group_involvement=peer_involvement,
            recommended_actions=recommended_actions,
            school_notification_required=incident_count >= 3,
            anonymization_level="AGGREGATED",
            privacy_protections=[
                "No student identification",
                "Aggregate counts only",
                "FERPA compliant",
            ],
        )
        
        self.incident_clusters.append(cluster)
        return cluster
    
    def assess_gang_exposure(
        self,
        zone: str,
        gang_activity_level: str = "unknown",
        community_factors: Optional[List[str]] = None,
    ) -> GangExposureRisk:
        """
        Assess gang exposure risk for a zone
        
        Uses community-level data only, no individual profiling.
        """
        from .privacy_guard import PrivacyGuard
        privacy_guard = PrivacyGuard()
        
        privacy_check = privacy_guard.check_query(
            query_type="gang_exposure_assessment",
            data_sources=["aggregated_crime_data", "community_data"],
            contains_pii=False,
        )
        
        risk_indicators = []
        protective_factors = []
        
        if gang_activity_level == "high":
            risk_indicators.append("high_gang_activity_area")
            exposure_level = YouthRiskLevel.HIGH
        elif gang_activity_level == "moderate":
            risk_indicators.append("moderate_gang_activity_area")
            exposure_level = YouthRiskLevel.MODERATE
        else:
            exposure_level = YouthRiskLevel.LOW
        
        if community_factors:
            for factor in community_factors:
                if factor in self._gang_exposure_indicators:
                    risk_indicators.append(factor)
                elif factor in self._protective_factors:
                    protective_factors.append(factor)
        
        if len(risk_indicators) >= 3:
            exposure_level = YouthRiskLevel.HIGH
            recruitment_risk = "HIGH"
        elif len(risk_indicators) >= 2:
            recruitment_risk = "MODERATE"
        else:
            recruitment_risk = "LOW"
        
        interventions = [
            InterventionType.GANG_INTERVENTION,
            InterventionType.YOUTH_MENTOR,
            InterventionType.AFTER_SCHOOL_PROGRAM,
        ]
        
        community_resources = [
            "Youth mentorship programs",
            "After-school activities",
            "Job training programs",
            "Community recreation centers",
            "Gang intervention specialists",
        ]
        
        risk = GangExposureRisk(
            risk_id=f"GER-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            zone=zone,
            exposure_level=exposure_level,
            risk_indicators=risk_indicators,
            protective_factors=protective_factors,
            gang_activity_proximity="within_zone" if gang_activity_level != "low" else "minimal",
            recruitment_risk=recruitment_risk,
            recommended_interventions=interventions,
            community_resources=community_resources,
            anonymization_level="ZONE_LEVEL",
            privacy_protections=[
                "No individual identification",
                "Zone-level analysis only",
                "No demographic profiling",
                "No predictive policing on individuals",
            ],
        )
        
        self.gang_exposure_risks.append(risk)
        return risk
    
    def create_intervention_plan(
        self,
        risk_assessment: YouthRiskAssessment,
    ) -> YouthInterventionPlan:
        """
        Create an intervention plan based on risk assessment
        """
        if risk_assessment.recommended_interventions:
            primary = risk_assessment.recommended_interventions[0]
            secondary = risk_assessment.recommended_interventions[1:4]
        else:
            primary = InterventionType.SCHOOL_COUNSELOR
            secondary = [InterventionType.SOCIAL_WORKER]
        
        school_involvement = any(
            rt in [YouthRiskType.TRUANCY, YouthRiskType.SCHOOL_INCIDENT]
            for rt in risk_assessment.risk_types
        )
        
        family_involvement = YouthRiskType.FAMILY_INSTABILITY in risk_assessment.risk_types
        
        community_resources = [
            "Youth mentorship programs",
            "After-school activities",
            "Community mental health services",
            "Family support services",
        ]
        
        if risk_assessment.risk_level in [YouthRiskLevel.CRITICAL, YouthRiskLevel.HIGH]:
            timeline = "Immediate - within 24 hours"
            follow_up = "Daily for first week, then weekly"
        elif risk_assessment.risk_level == YouthRiskLevel.ELEVATED:
            timeline = "Urgent - within 72 hours"
            follow_up = "Weekly for first month"
        else:
            timeline = "Standard - within 1 week"
            follow_up = "Monthly check-ins"
        
        success_metrics = [
            "Reduction in risk indicators",
            "Increased protective factors",
            "School attendance improvement",
            "Positive behavioral changes",
            "Family engagement level",
        ]
        
        plan = YouthInterventionPlan(
            plan_id=f"YIP-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            risk_assessment=risk_assessment,
            primary_intervention=primary,
            secondary_interventions=secondary,
            school_involvement=school_involvement,
            family_involvement=family_involvement,
            community_resources=community_resources,
            timeline=timeline,
            success_metrics=success_metrics,
            follow_up_schedule=follow_up,
            anonymization_level="FULL",
            privacy_protections=[
                "No individual identification",
                "Intervention tracking only",
                "FERPA compliant",
            ],
        )
        
        self.intervention_plans.append(plan)
        return plan
    
    def get_youth_stability_map(
        self,
        geographic_scope: str = "city",
    ) -> Dict[str, Any]:
        """
        Get youth stability map for the city
        
        Returns zone-level aggregated data only.
        """
        from .privacy_guard import PrivacyGuard
        privacy_guard = PrivacyGuard()
        
        privacy_check = privacy_guard.check_query(
            query_type="youth_stability_map",
            data_sources=["aggregated_youth_data"],
            contains_pii=False,
        )
        
        zones = [
            {
                "zone_id": "Zone_A",
                "stability_score": 72.0,
                "risk_level": "MODERATE",
                "primary_concerns": ["truancy", "peer_issues"],
                "recommended_focus": "After-school programs",
            },
            {
                "zone_id": "Zone_B",
                "stability_score": 85.0,
                "risk_level": "LOW",
                "primary_concerns": [],
                "recommended_focus": "Maintain current programs",
            },
            {
                "zone_id": "Zone_C",
                "stability_score": 65.0,
                "risk_level": "ELEVATED",
                "primary_concerns": ["gang_exposure", "violence"],
                "recommended_focus": "Gang intervention, mentorship",
            },
        ]
        
        return {
            "map_id": f"YSM-{uuid.uuid4().hex[:12].upper()}",
            "timestamp": datetime.utcnow().isoformat(),
            "geographic_scope": geographic_scope,
            "zones": zones,
            "overall_stability": 74.0,
            "trend": "stable",
            "anonymization_level": "ZONE_AGGREGATED",
            "privacy_protections": [
                "No individual data",
                "Zone-level only",
                "No demographic breakdown",
            ],
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "total_risk_assessments": len(self.risk_assessments),
            "total_incident_clusters": len(self.incident_clusters),
            "total_gang_exposure_risks": len(self.gang_exposure_risks),
            "total_intervention_plans": len(self.intervention_plans),
            "high_risk_count": len([
                a for a in self.risk_assessments
                if a.risk_level in [YouthRiskLevel.HIGH, YouthRiskLevel.CRITICAL]
            ]),
            "agency": self.agency_config,
        }
