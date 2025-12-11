"""
Phase 26: Use-of-Force Risk Assessment Engine

Evaluates risk for every action involving enforcement:
- Civil rights exposure
- Force escalation probability
- Mental health indicators
- Juvenile involvement
- Proximity to sensitive locations
- Protected classes

Returns:
- Risk level (0-100)
- Mandatory human-review flag
- Recommended de-escalation alternatives
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import math


class ForceLevel(Enum):
    """Levels of force."""
    VERBAL = "VERBAL"
    SOFT_HANDS = "SOFT_HANDS"
    HARD_HANDS = "HARD_HANDS"
    INTERMEDIATE = "INTERMEDIATE"
    LESS_LETHAL = "LESS_LETHAL"
    LETHAL = "LETHAL"


class RiskFactor(Enum):
    """Risk factors for use-of-force assessment."""
    CIVIL_RIGHTS_EXPOSURE = "CIVIL_RIGHTS_EXPOSURE"
    FORCE_ESCALATION_PROBABILITY = "FORCE_ESCALATION_PROBABILITY"
    MENTAL_HEALTH_INDICATORS = "MENTAL_HEALTH_INDICATORS"
    JUVENILE_INVOLVEMENT = "JUVENILE_INVOLVEMENT"
    SENSITIVE_LOCATION = "SENSITIVE_LOCATION"
    PROTECTED_CLASS = "PROTECTED_CLASS"
    CROWD_PRESENCE = "CROWD_PRESENCE"
    MEDIA_PRESENCE = "MEDIA_PRESENCE"
    PRIOR_INCIDENTS = "PRIOR_INCIDENTS"
    OFFICER_HISTORY = "OFFICER_HISTORY"


class SensitiveLocationType(Enum):
    """Types of sensitive locations."""
    SCHOOL = "SCHOOL"
    CHURCH = "CHURCH"
    PLAYGROUND = "PLAYGROUND"
    HOSPITAL = "HOSPITAL"
    DAYCARE = "DAYCARE"
    SENIOR_CENTER = "SENIOR_CENTER"
    COMMUNITY_CENTER = "COMMUNITY_CENTER"
    PLACE_OF_WORSHIP = "PLACE_OF_WORSHIP"
    MENTAL_HEALTH_FACILITY = "MENTAL_HEALTH_FACILITY"


@dataclass
class DeescalationRecommendation:
    """Recommended de-escalation alternative."""
    recommendation_id: str
    technique: str
    description: str
    effectiveness_rating: float
    training_required: str
    time_to_implement: str
    success_rate: float
    applicable_scenarios: List[str]


@dataclass
class RiskFactorScore:
    """Individual risk factor score."""
    factor: RiskFactor
    score: float
    max_score: float
    weight: float
    contributing_elements: List[str]
    mitigation_available: bool
    mitigation_description: str


@dataclass
class ForceRiskAssessment:
    """Complete use-of-force risk assessment."""
    assessment_id: str
    action_id: str
    timestamp: datetime
    total_risk_score: float
    risk_level: str
    factor_scores: List[RiskFactorScore]
    requires_human_review: bool
    mandatory_review_reasons: List[str]
    deescalation_recommendations: List[DeescalationRecommendation]
    civil_rights_concerns: List[str]
    protected_class_flags: List[str]
    sensitive_location_flags: List[str]
    mental_health_flags: List[str]
    juvenile_flags: List[str]
    recommended_force_level: ForceLevel
    max_authorized_force: ForceLevel
    explanation: str
    legal_basis: List[str]
    policy_references: List[str]


class UseOfForceRiskEngine:
    """
    Engine for assessing use-of-force risk.
    
    Evaluates civil rights exposure, force escalation probability,
    mental health indicators, juvenile involvement, proximity to
    sensitive locations, and protected class considerations.
    """
    
    _instance = None
    
    RISK_THRESHOLDS = {
        "LOW": (0, 25),
        "MODERATE": (26, 50),
        "HIGH": (51, 75),
        "CRITICAL": (76, 100),
    }
    
    FACTOR_WEIGHTS = {
        RiskFactor.CIVIL_RIGHTS_EXPOSURE: 0.20,
        RiskFactor.FORCE_ESCALATION_PROBABILITY: 0.15,
        RiskFactor.MENTAL_HEALTH_INDICATORS: 0.15,
        RiskFactor.JUVENILE_INVOLVEMENT: 0.15,
        RiskFactor.SENSITIVE_LOCATION: 0.10,
        RiskFactor.PROTECTED_CLASS: 0.10,
        RiskFactor.CROWD_PRESENCE: 0.05,
        RiskFactor.MEDIA_PRESENCE: 0.05,
        RiskFactor.PRIOR_INCIDENTS: 0.03,
        RiskFactor.OFFICER_HISTORY: 0.02,
    }
    
    SENSITIVE_LOCATIONS_RIVIERA_BEACH = [
        {"name": "Riviera Beach High School", "type": SensitiveLocationType.SCHOOL, "lat": 26.7753, "lon": -80.0583},
        {"name": "First Baptist Church", "type": SensitiveLocationType.CHURCH, "lat": 26.7760, "lon": -80.0590},
        {"name": "Barracuda Bay Playground", "type": SensitiveLocationType.PLAYGROUND, "lat": 26.7745, "lon": -80.0575},
        {"name": "Riviera Beach Marina", "type": SensitiveLocationType.COMMUNITY_CENTER, "lat": 26.7780, "lon": -80.0550},
        {"name": "Palm Beach County Health Dept", "type": SensitiveLocationType.HOSPITAL, "lat": 26.7770, "lon": -80.0600},
    ]
    
    DEESCALATION_TECHNIQUES = [
        DeescalationRecommendation(
            recommendation_id="de-001",
            technique="Active Listening",
            description="Engage in active listening to understand the subject's concerns",
            effectiveness_rating=0.85,
            training_required="CIT Basic",
            time_to_implement="Immediate",
            success_rate=0.78,
            applicable_scenarios=["verbal_confrontation", "mental_health_crisis", "domestic_dispute"],
        ),
        DeescalationRecommendation(
            recommendation_id="de-002",
            technique="Time and Distance",
            description="Create physical and temporal space to reduce tension",
            effectiveness_rating=0.90,
            training_required="Basic Academy",
            time_to_implement="Immediate",
            success_rate=0.82,
            applicable_scenarios=["armed_subject", "barricade", "crowd_control"],
        ),
        DeescalationRecommendation(
            recommendation_id="de-003",
            technique="Crisis Intervention",
            description="Apply CIT techniques for mental health crisis",
            effectiveness_rating=0.88,
            training_required="CIT 40-hour",
            time_to_implement="5-10 minutes",
            success_rate=0.75,
            applicable_scenarios=["mental_health_crisis", "suicide_threat", "substance_abuse"],
        ),
        DeescalationRecommendation(
            recommendation_id="de-004",
            technique="Verbal Judo",
            description="Use tactical communication to gain voluntary compliance",
            effectiveness_rating=0.80,
            training_required="Verbal Judo Certification",
            time_to_implement="Immediate",
            success_rate=0.70,
            applicable_scenarios=["non_compliant_subject", "verbal_confrontation", "traffic_stop"],
        ),
        DeescalationRecommendation(
            recommendation_id="de-005",
            technique="Third-Party Intermediary",
            description="Involve family member, community leader, or mental health professional",
            effectiveness_rating=0.75,
            training_required="Community Policing",
            time_to_implement="15-30 minutes",
            success_rate=0.68,
            applicable_scenarios=["barricade", "domestic_dispute", "community_conflict"],
        ),
    ]
    
    def __init__(self):
        self._assessment_history: List[ForceRiskAssessment] = []
    
    @classmethod
    def get_instance(cls) -> "UseOfForceRiskEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def assess_force_risk(
        self,
        action_id: str,
        context: Dict[str, Any],
    ) -> ForceRiskAssessment:
        """
        Assess use-of-force risk for an action.
        
        Args:
            action_id: Unique identifier for the action
            context: Context including subject info, location, situation
            
        Returns:
            ForceRiskAssessment with risk score and recommendations
        """
        assessment_id = f"force-{uuid.uuid4().hex[:12]}"
        factor_scores = []
        mandatory_review_reasons = []
        civil_rights_concerns = []
        protected_class_flags = []
        sensitive_location_flags = []
        mental_health_flags = []
        juvenile_flags = []
        
        cre_score = self._assess_civil_rights_exposure(context)
        factor_scores.append(cre_score)
        if cre_score.score > 15:
            civil_rights_concerns.append("Elevated civil rights exposure detected")
            mandatory_review_reasons.append("Civil rights exposure exceeds threshold")
        
        fep_score = self._assess_force_escalation(context)
        factor_scores.append(fep_score)
        if fep_score.score > 12:
            mandatory_review_reasons.append("High force escalation probability")
        
        mh_score = self._assess_mental_health(context)
        factor_scores.append(mh_score)
        if mh_score.score > 10:
            mental_health_flags.extend(mh_score.contributing_elements)
            mandatory_review_reasons.append("Mental health indicators present")
        
        juv_score = self._assess_juvenile_involvement(context)
        factor_scores.append(juv_score)
        if juv_score.score > 10:
            juvenile_flags.extend(juv_score.contributing_elements)
            mandatory_review_reasons.append("Juvenile involvement detected")
        
        loc_score = self._assess_sensitive_location(context)
        factor_scores.append(loc_score)
        if loc_score.score > 5:
            sensitive_location_flags.extend(loc_score.contributing_elements)
        
        pc_score = self._assess_protected_class(context)
        factor_scores.append(pc_score)
        if pc_score.score > 5:
            protected_class_flags.extend(pc_score.contributing_elements)
            civil_rights_concerns.append("Protected class considerations apply")
        
        crowd_score = self._assess_crowd_presence(context)
        factor_scores.append(crowd_score)
        
        media_score = self._assess_media_presence(context)
        factor_scores.append(media_score)
        
        prior_score = self._assess_prior_incidents(context)
        factor_scores.append(prior_score)
        
        officer_score = self._assess_officer_history(context)
        factor_scores.append(officer_score)
        
        total_score = sum(fs.score * fs.weight for fs in factor_scores)
        total_score = min(100, max(0, total_score))
        
        risk_level = self._determine_risk_level(total_score)
        
        requires_review = (
            total_score >= 50 or
            len(mandatory_review_reasons) > 0 or
            len(juvenile_flags) > 0 or
            len(mental_health_flags) > 0
        )
        
        deescalation_recs = self._get_deescalation_recommendations(context, factor_scores)
        
        recommended_force, max_force = self._determine_force_levels(total_score, context)
        
        explanation = self._generate_explanation(
            total_score, risk_level, factor_scores, mandatory_review_reasons
        )
        
        legal_basis = self._get_legal_basis(context)
        policy_refs = self._get_policy_references(context)
        
        assessment = ForceRiskAssessment(
            assessment_id=assessment_id,
            action_id=action_id,
            timestamp=datetime.now(),
            total_risk_score=round(total_score, 2),
            risk_level=risk_level,
            factor_scores=factor_scores,
            requires_human_review=requires_review,
            mandatory_review_reasons=mandatory_review_reasons,
            deescalation_recommendations=deescalation_recs,
            civil_rights_concerns=civil_rights_concerns,
            protected_class_flags=protected_class_flags,
            sensitive_location_flags=sensitive_location_flags,
            mental_health_flags=mental_health_flags,
            juvenile_flags=juvenile_flags,
            recommended_force_level=recommended_force,
            max_authorized_force=max_force,
            explanation=explanation,
            legal_basis=legal_basis,
            policy_references=policy_refs,
        )
        
        self._assessment_history.append(assessment)
        return assessment
    
    def _assess_civil_rights_exposure(self, context: Dict) -> RiskFactorScore:
        """Assess civil rights exposure risk."""
        score = 0.0
        elements = []
        
        if context.get("involves_search", False):
            if not context.get("has_warrant", False) and not context.get("consent_given", False):
                score += 15
                elements.append("Warrantless search without consent")
            elif context.get("consent_given", False):
                score += 5
                elements.append("Consent-based search")
        
        if context.get("involves_seizure", False):
            score += 10
            elements.append("Seizure of person or property")
        
        if context.get("involves_surveillance", False):
            score += 8
            elements.append("Surveillance activity")
        
        if context.get("first_amendment_activity", False):
            score += 12
            elements.append("First Amendment protected activity nearby")
        
        return RiskFactorScore(
            factor=RiskFactor.CIVIL_RIGHTS_EXPOSURE,
            score=min(20, score),
            max_score=20,
            weight=self.FACTOR_WEIGHTS[RiskFactor.CIVIL_RIGHTS_EXPOSURE],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Obtain warrant or documented consent",
        )
    
    def _assess_force_escalation(self, context: Dict) -> RiskFactorScore:
        """Assess force escalation probability."""
        score = 0.0
        elements = []
        
        if context.get("subject_armed", False):
            weapon_type = context.get("weapon_type", "unknown")
            if weapon_type == "firearm":
                score += 15
                elements.append("Subject armed with firearm")
            elif weapon_type == "knife":
                score += 10
                elements.append("Subject armed with edged weapon")
            else:
                score += 7
                elements.append(f"Subject armed with {weapon_type}")
        
        if context.get("subject_aggressive", False):
            score += 8
            elements.append("Subject displaying aggressive behavior")
        
        if context.get("subject_fleeing", False):
            score += 5
            elements.append("Subject attempting to flee")
        
        if context.get("multiple_subjects", False):
            score += 6
            elements.append("Multiple subjects involved")
        
        if context.get("confined_space", False):
            score += 4
            elements.append("Confined space limits options")
        
        return RiskFactorScore(
            factor=RiskFactor.FORCE_ESCALATION_PROBABILITY,
            score=min(15, score),
            max_score=15,
            weight=self.FACTOR_WEIGHTS[RiskFactor.FORCE_ESCALATION_PROBABILITY],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Apply time and distance tactics",
        )
    
    def _assess_mental_health(self, context: Dict) -> RiskFactorScore:
        """Assess mental health indicators."""
        score = 0.0
        elements = []
        
        if context.get("mental_health_crisis", False):
            score += 12
            elements.append("Active mental health crisis")
        
        if context.get("known_mental_health_history", False):
            score += 5
            elements.append("Known mental health history")
        
        if context.get("substance_influence", False):
            score += 7
            elements.append("Subject under influence of substances")
        
        if context.get("suicidal_ideation", False):
            score += 15
            elements.append("Suicidal ideation indicated")
        
        if context.get("erratic_behavior", False):
            score += 6
            elements.append("Erratic or unpredictable behavior")
        
        return RiskFactorScore(
            factor=RiskFactor.MENTAL_HEALTH_INDICATORS,
            score=min(15, score),
            max_score=15,
            weight=self.FACTOR_WEIGHTS[RiskFactor.MENTAL_HEALTH_INDICATORS],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Request CIT-trained officer or mental health co-responder",
        )
    
    def _assess_juvenile_involvement(self, context: Dict) -> RiskFactorScore:
        """Assess juvenile involvement."""
        score = 0.0
        elements = []
        
        subject_age = context.get("subject_age", 30)
        if subject_age < 18:
            score += 12
            elements.append(f"Subject is a minor (age {subject_age})")
            
            if subject_age < 14:
                score += 5
                elements.append("Subject under 14 years old")
        
        if context.get("juveniles_present", False):
            score += 5
            elements.append("Juveniles present at scene")
        
        if context.get("school_related", False):
            score += 8
            elements.append("School-related incident")
        
        return RiskFactorScore(
            factor=RiskFactor.JUVENILE_INVOLVEMENT,
            score=min(15, score),
            max_score=15,
            weight=self.FACTOR_WEIGHTS[RiskFactor.JUVENILE_INVOLVEMENT],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Follow juvenile-specific protocols; contact guardian",
        )
    
    def _assess_sensitive_location(self, context: Dict) -> RiskFactorScore:
        """Assess proximity to sensitive locations."""
        score = 0.0
        elements = []
        
        location_type = context.get("location_type")
        if location_type:
            if location_type in ["school", "daycare"]:
                score += 10
                elements.append(f"Location is a {location_type}")
            elif location_type in ["church", "place_of_worship"]:
                score += 8
                elements.append("Location is a place of worship")
            elif location_type in ["hospital", "mental_health_facility"]:
                score += 7
                elements.append(f"Location is a {location_type}")
            elif location_type in ["playground", "community_center"]:
                score += 6
                elements.append(f"Location is a {location_type}")
        
        nearby_sensitive = context.get("nearby_sensitive_locations", [])
        for loc in nearby_sensitive[:2]:
            score += 3
            elements.append(f"Near sensitive location: {loc}")
        
        return RiskFactorScore(
            factor=RiskFactor.SENSITIVE_LOCATION,
            score=min(10, score),
            max_score=10,
            weight=self.FACTOR_WEIGHTS[RiskFactor.SENSITIVE_LOCATION],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Consider relocating encounter if safe to do so",
        )
    
    def _assess_protected_class(self, context: Dict) -> RiskFactorScore:
        """Assess protected class considerations."""
        score = 0.0
        elements = []
        
        if context.get("disability_apparent", False):
            score += 8
            elements.append("Subject has apparent disability")
        
        if context.get("elderly_subject", False) or context.get("subject_age", 30) >= 65:
            score += 5
            elements.append("Elderly subject")
        
        if context.get("pregnant_subject", False):
            score += 8
            elements.append("Pregnant subject")
        
        if context.get("language_barrier", False):
            score += 4
            elements.append("Language barrier present")
        
        if context.get("religious_considerations", False):
            score += 3
            elements.append("Religious considerations apply")
        
        return RiskFactorScore(
            factor=RiskFactor.PROTECTED_CLASS,
            score=min(10, score),
            max_score=10,
            weight=self.FACTOR_WEIGHTS[RiskFactor.PROTECTED_CLASS],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Apply ADA accommodations; request interpreter if needed",
        )
    
    def _assess_crowd_presence(self, context: Dict) -> RiskFactorScore:
        """Assess crowd presence risk."""
        score = 0.0
        elements = []
        
        crowd_size = context.get("crowd_size", 0)
        if crowd_size > 50:
            score += 5
            elements.append(f"Large crowd present ({crowd_size}+ people)")
        elif crowd_size > 20:
            score += 3
            elements.append(f"Moderate crowd present ({crowd_size} people)")
        elif crowd_size > 5:
            score += 1
            elements.append(f"Small crowd present ({crowd_size} people)")
        
        if context.get("crowd_hostile", False):
            score += 4
            elements.append("Crowd displaying hostile behavior")
        
        return RiskFactorScore(
            factor=RiskFactor.CROWD_PRESENCE,
            score=min(5, score),
            max_score=5,
            weight=self.FACTOR_WEIGHTS[RiskFactor.CROWD_PRESENCE],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Request additional units for crowd management",
        )
    
    def _assess_media_presence(self, context: Dict) -> RiskFactorScore:
        """Assess media presence."""
        score = 0.0
        elements = []
        
        if context.get("media_present", False):
            score += 3
            elements.append("Media personnel present")
        
        if context.get("live_streaming", False):
            score += 4
            elements.append("Incident being live-streamed")
        
        if context.get("high_profile_case", False):
            score += 5
            elements.append("High-profile case with media attention")
        
        return RiskFactorScore(
            factor=RiskFactor.MEDIA_PRESENCE,
            score=min(5, score),
            max_score=5,
            weight=self.FACTOR_WEIGHTS[RiskFactor.MEDIA_PRESENCE],
            contributing_elements=elements,
            mitigation_available=False,
            mitigation_description="Ensure body cameras active; follow media protocols",
        )
    
    def _assess_prior_incidents(self, context: Dict) -> RiskFactorScore:
        """Assess prior incidents at location or with subject."""
        score = 0.0
        elements = []
        
        prior_force_incidents = context.get("prior_force_incidents", 0)
        if prior_force_incidents > 0:
            score += min(3, prior_force_incidents)
            elements.append(f"{prior_force_incidents} prior force incidents at location")
        
        subject_prior_violence = context.get("subject_prior_violence", False)
        if subject_prior_violence:
            score += 2
            elements.append("Subject has history of violence")
        
        return RiskFactorScore(
            factor=RiskFactor.PRIOR_INCIDENTS,
            score=min(3, score),
            max_score=3,
            weight=self.FACTOR_WEIGHTS[RiskFactor.PRIOR_INCIDENTS],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Review prior incident reports before engagement",
        )
    
    def _assess_officer_history(self, context: Dict) -> RiskFactorScore:
        """Assess officer history factors."""
        score = 0.0
        elements = []
        
        officer_complaints = context.get("officer_complaints", 0)
        if officer_complaints > 3:
            score += 2
            elements.append(f"Officer has {officer_complaints} prior complaints")
        
        if context.get("officer_recent_force", False):
            score += 1
            elements.append("Officer involved in recent force incident")
        
        return RiskFactorScore(
            factor=RiskFactor.OFFICER_HISTORY,
            score=min(2, score),
            max_score=2,
            weight=self.FACTOR_WEIGHTS[RiskFactor.OFFICER_HISTORY],
            contributing_elements=elements,
            mitigation_available=True,
            mitigation_description="Assign different primary officer if available",
        )
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level from score."""
        for level, (min_score, max_score) in self.RISK_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return level
        return "CRITICAL"
    
    def _get_deescalation_recommendations(
        self,
        context: Dict,
        factor_scores: List[RiskFactorScore],
    ) -> List[DeescalationRecommendation]:
        """Get applicable de-escalation recommendations."""
        recommendations = []
        scenario_tags = []
        
        if any(fs.factor == RiskFactor.MENTAL_HEALTH_INDICATORS and fs.score > 5 for fs in factor_scores):
            scenario_tags.append("mental_health_crisis")
        
        if context.get("subject_armed", False):
            scenario_tags.append("armed_subject")
        
        if context.get("domestic_dispute", False):
            scenario_tags.append("domestic_dispute")
        
        if context.get("subject_aggressive", False):
            scenario_tags.append("verbal_confrontation")
        
        if not scenario_tags:
            scenario_tags = ["verbal_confrontation"]
        
        for rec in self.DEESCALATION_TECHNIQUES:
            if any(tag in rec.applicable_scenarios for tag in scenario_tags):
                recommendations.append(rec)
        
        recommendations.sort(key=lambda r: r.effectiveness_rating, reverse=True)
        return recommendations[:3]
    
    def _determine_force_levels(
        self,
        risk_score: float,
        context: Dict,
    ) -> tuple:
        """Determine recommended and maximum force levels."""
        if risk_score < 25:
            return ForceLevel.VERBAL, ForceLevel.SOFT_HANDS
        elif risk_score < 50:
            return ForceLevel.VERBAL, ForceLevel.HARD_HANDS
        elif risk_score < 75:
            return ForceLevel.SOFT_HANDS, ForceLevel.INTERMEDIATE
        else:
            if context.get("imminent_threat_life", False):
                return ForceLevel.INTERMEDIATE, ForceLevel.LETHAL
            return ForceLevel.SOFT_HANDS, ForceLevel.LESS_LETHAL
    
    def _generate_explanation(
        self,
        score: float,
        level: str,
        factors: List[RiskFactorScore],
        review_reasons: List[str],
    ) -> str:
        """Generate human-readable explanation."""
        top_factors = sorted(factors, key=lambda f: f.score, reverse=True)[:3]
        factor_desc = ", ".join(f.factor.value for f in top_factors if f.score > 0)
        
        explanation = f"Risk Level: {level} (Score: {score:.1f}/100). "
        explanation += f"Primary contributing factors: {factor_desc}. "
        
        if review_reasons:
            explanation += f"Mandatory review required: {'; '.join(review_reasons)}."
        
        return explanation
    
    def _get_legal_basis(self, context: Dict) -> List[str]:
        """Get applicable legal basis."""
        basis = [
            "Graham v. Connor (1989) - Objective reasonableness standard",
            "Tennessee v. Garner (1985) - Fleeing felon rule",
        ]
        
        if context.get("subject_age", 30) < 18:
            basis.append("Florida Statute 985 - Juvenile Justice")
        
        if context.get("mental_health_crisis", False):
            basis.append("Florida Baker Act (Chapter 394)")
        
        return basis
    
    def _get_policy_references(self, context: Dict) -> List[str]:
        """Get applicable policy references."""
        refs = [
            "Riviera Beach PD Use of Force Policy",
            "Florida Law Enforcement Use of Force Guidelines",
            "DOJ Use of Force Policy Framework",
        ]
        
        if context.get("mental_health_crisis", False):
            refs.append("CIT Response Protocol")
        
        if context.get("subject_age", 30) < 18:
            refs.append("Juvenile Interaction Policy")
        
        return refs
    
    def get_assessment_history(
        self,
        risk_level: Optional[str] = None,
        limit: int = 100,
    ) -> List[ForceRiskAssessment]:
        """Get assessment history with optional filters."""
        results = self._assessment_history
        
        if risk_level:
            results = [r for r in results if r.risk_level == risk_level]
        
        return results[-limit:]


def get_force_risk_engine() -> UseOfForceRiskEngine:
    """Get the singleton UseOfForceRiskEngine instance."""
    return UseOfForceRiskEngine.get_instance()
