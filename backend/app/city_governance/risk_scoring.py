"""
Phase 25: Governance Risk Scoring Engine

Calculates risk scores for AI actions based on:
- Legal exposure
- Civil rights impact
- Jurisdictional authority
- Operational consequence
- Political/public risk
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from .constitution_engine import ActionCategory


class RiskCategory(Enum):
    """Risk category levels."""
    LOW = "low"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class RiskDimension(Enum):
    """Dimensions of risk assessment."""
    LEGAL_EXPOSURE = "legal_exposure"
    CIVIL_RIGHTS_IMPACT = "civil_rights_impact"
    JURISDICTIONAL_AUTHORITY = "jurisdictional_authority"
    OPERATIONAL_CONSEQUENCE = "operational_consequence"
    POLITICAL_PUBLIC_RISK = "political_public_risk"


@dataclass
class RiskFactor:
    """A specific risk factor contributing to the overall score."""
    factor_id: str
    dimension: RiskDimension
    name: str
    description: str
    weight: float
    score: float  # 0-100
    evidence: List[str]
    mitigations: List[str]
    
    def weighted_score(self) -> float:
        """Calculate weighted score."""
        return self.score * self.weight
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "factor_id": self.factor_id,
            "dimension": self.dimension.value,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "score": self.score,
            "weighted_score": self.weighted_score(),
            "evidence": self.evidence,
            "mitigations": self.mitigations,
        }


@dataclass
class RiskAssessment:
    """Complete risk assessment for an action."""
    assessment_id: str
    action_type: str
    action_category: ActionCategory
    action_details: Dict[str, Any]
    total_score: int  # 0-100
    category: RiskCategory
    dimension_scores: Dict[RiskDimension, float]
    factors: List[RiskFactor]
    mitigations: List[str]
    recommendations: List[str]
    requires_human_review: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "action_type": self.action_type,
            "action_category": self.action_category.value,
            "action_details": self.action_details,
            "total_score": self.total_score,
            "category": self.category.value,
            "dimension_scores": {d.value: s for d, s in self.dimension_scores.items()},
            "factors": [f.to_dict() for f in self.factors],
            "mitigations": self.mitigations,
            "recommendations": self.recommendations,
            "requires_human_review": self.requires_human_review,
            "timestamp": self.timestamp.isoformat(),
        }


class GovernanceRiskScoringEngine:
    """
    Governance Risk Scoring Engine
    
    Calculates comprehensive risk scores for AI actions based on
    legal, civil rights, jurisdictional, operational, and political factors.
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
        
        self._assessments: Dict[str, RiskAssessment] = {}
        self._assessment_history: List[RiskAssessment] = []
        
        # Dimension weights (must sum to 1.0)
        self._dimension_weights = {
            RiskDimension.LEGAL_EXPOSURE: 0.25,
            RiskDimension.CIVIL_RIGHTS_IMPACT: 0.25,
            RiskDimension.JURISDICTIONAL_AUTHORITY: 0.15,
            RiskDimension.OPERATIONAL_CONSEQUENCE: 0.20,
            RiskDimension.POLITICAL_PUBLIC_RISK: 0.15,
        }
        
        # Risk thresholds
        self._thresholds = {
            RiskCategory.LOW: (0, 25),
            RiskCategory.ELEVATED: (25, 50),
            RiskCategory.HIGH: (50, 75),
            RiskCategory.CRITICAL: (75, 100),
        }
        
        # Human review threshold
        self._human_review_threshold = 50
        
        self._initialized = True
    
    def calculate_risk(
        self,
        action_type: str,
        action_category: ActionCategory,
        action_details: Dict[str, Any],
        context: Dict[str, Any],
    ) -> RiskAssessment:
        """
        Calculate comprehensive risk score for an action.
        
        Args:
            action_type: Type of action
            action_category: Category of action
            action_details: Details of the action
            context: Additional context
        
        Returns:
            RiskAssessment with complete risk analysis
        """
        assessment_id = f"risk-{uuid4().hex[:12]}"
        
        # Merge details and context
        full_context = {**context, **action_details}
        
        # Calculate risk factors for each dimension
        factors: List[RiskFactor] = []
        dimension_scores: Dict[RiskDimension, float] = {}
        
        # Legal Exposure
        legal_factors = self._assess_legal_exposure(action_category, full_context)
        factors.extend(legal_factors)
        dimension_scores[RiskDimension.LEGAL_EXPOSURE] = self._calculate_dimension_score(legal_factors)
        
        # Civil Rights Impact
        civil_rights_factors = self._assess_civil_rights_impact(action_category, full_context)
        factors.extend(civil_rights_factors)
        dimension_scores[RiskDimension.CIVIL_RIGHTS_IMPACT] = self._calculate_dimension_score(civil_rights_factors)
        
        # Jurisdictional Authority
        jurisdictional_factors = self._assess_jurisdictional_authority(action_category, full_context)
        factors.extend(jurisdictional_factors)
        dimension_scores[RiskDimension.JURISDICTIONAL_AUTHORITY] = self._calculate_dimension_score(jurisdictional_factors)
        
        # Operational Consequence
        operational_factors = self._assess_operational_consequence(action_category, full_context)
        factors.extend(operational_factors)
        dimension_scores[RiskDimension.OPERATIONAL_CONSEQUENCE] = self._calculate_dimension_score(operational_factors)
        
        # Political/Public Risk
        political_factors = self._assess_political_public_risk(action_category, full_context)
        factors.extend(political_factors)
        dimension_scores[RiskDimension.POLITICAL_PUBLIC_RISK] = self._calculate_dimension_score(political_factors)
        
        # Calculate total weighted score
        total_score = sum(
            dimension_scores[dim] * self._dimension_weights[dim]
            for dim in RiskDimension
        )
        total_score = min(100, max(0, int(total_score)))
        
        # Determine category
        category = self._determine_category(total_score)
        
        # Collect all mitigations
        all_mitigations = []
        for factor in factors:
            all_mitigations.extend(factor.mitigations)
        mitigations = list(set(all_mitigations))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            total_score, category, factors, action_category
        )
        
        # Determine if human review is required
        requires_human_review = total_score >= self._human_review_threshold
        
        assessment = RiskAssessment(
            assessment_id=assessment_id,
            action_type=action_type,
            action_category=action_category,
            action_details=action_details,
            total_score=total_score,
            category=category,
            dimension_scores=dimension_scores,
            factors=factors,
            mitigations=mitigations,
            recommendations=recommendations,
            requires_human_review=requires_human_review,
        )
        
        self._assessments[assessment_id] = assessment
        self._assessment_history.append(assessment)
        
        return assessment
    
    def _assess_legal_exposure(
        self,
        action_category: ActionCategory,
        context: Dict[str, Any],
    ) -> List[RiskFactor]:
        """Assess legal exposure risk factors."""
        factors = []
        
        # Warrant requirement
        if context.get("requires_warrant", False) and not context.get("has_warrant", False):
            factors.append(RiskFactor(
                factor_id=f"legal-{uuid4().hex[:8]}",
                dimension=RiskDimension.LEGAL_EXPOSURE,
                name="Missing Warrant",
                description="Action requires warrant but none obtained",
                weight=0.4,
                score=90,
                evidence=["Warrant required by law", "No warrant on file"],
                mitigations=["Obtain warrant before proceeding", "Document exigent circumstances"],
            ))
        
        # Exigent circumstances
        if context.get("exigent_circumstances", False):
            factors.append(RiskFactor(
                factor_id=f"legal-{uuid4().hex[:8]}",
                dimension=RiskDimension.LEGAL_EXPOSURE,
                name="Exigent Circumstances Claim",
                description="Relying on exigent circumstances exception",
                weight=0.3,
                score=40,
                evidence=["Exigent circumstances claimed"],
                mitigations=["Document circumstances thoroughly", "Supervisor review"],
            ))
        
        # Use of force
        if context.get("involves_force", False):
            force_level = context.get("force_level", "low")
            score = {"low": 30, "medium": 60, "high": 85, "deadly": 95}.get(force_level, 50)
            factors.append(RiskFactor(
                factor_id=f"legal-{uuid4().hex[:8]}",
                dimension=RiskDimension.LEGAL_EXPOSURE,
                name="Use of Force",
                description=f"Action involves {force_level} level force",
                weight=0.4,
                score=score,
                evidence=[f"Force level: {force_level}"],
                mitigations=["Ensure force is proportional", "Document justification"],
            ))
        
        # Property entry
        if context.get("enters_private_property", False):
            factors.append(RiskFactor(
                factor_id=f"legal-{uuid4().hex[:8]}",
                dimension=RiskDimension.LEGAL_EXPOSURE,
                name="Private Property Entry",
                description="Action involves entry to private property",
                weight=0.3,
                score=70,
                evidence=["Private property entry planned"],
                mitigations=["Obtain consent or warrant", "Document legal basis"],
            ))
        
        # Default factor if none triggered
        if not factors:
            factors.append(RiskFactor(
                factor_id=f"legal-{uuid4().hex[:8]}",
                dimension=RiskDimension.LEGAL_EXPOSURE,
                name="Standard Legal Risk",
                description="Standard legal considerations apply",
                weight=1.0,
                score=15,
                evidence=["No elevated legal concerns identified"],
                mitigations=["Follow standard procedures"],
            ))
        
        return factors
    
    def _assess_civil_rights_impact(
        self,
        action_category: ActionCategory,
        context: Dict[str, Any],
    ) -> List[RiskFactor]:
        """Assess civil rights impact risk factors."""
        factors = []
        
        # Privacy invasion
        if context.get("invades_privacy", False):
            factors.append(RiskFactor(
                factor_id=f"civil-{uuid4().hex[:8]}",
                dimension=RiskDimension.CIVIL_RIGHTS_IMPACT,
                name="Privacy Impact",
                description="Action may impact privacy rights",
                weight=0.35,
                score=65,
                evidence=["Privacy impact identified"],
                mitigations=["Minimize data collection", "Apply data retention limits"],
            ))
        
        # Surveillance duration
        duration = context.get("surveillance_duration_hours", 0)
        if duration > 0:
            score = min(90, 20 + duration * 5)
            factors.append(RiskFactor(
                factor_id=f"civil-{uuid4().hex[:8]}",
                dimension=RiskDimension.CIVIL_RIGHTS_IMPACT,
                name="Surveillance Duration",
                description=f"Surveillance planned for {duration} hours",
                weight=0.25,
                score=score,
                evidence=[f"Duration: {duration} hours"],
                mitigations=["Limit surveillance duration", "Periodic review"],
            ))
        
        # Targeting individuals
        if context.get("targets_individual", False):
            factors.append(RiskFactor(
                factor_id=f"civil-{uuid4().hex[:8]}",
                dimension=RiskDimension.CIVIL_RIGHTS_IMPACT,
                name="Individual Targeting",
                description="Action targets specific individual",
                weight=0.3,
                score=55,
                evidence=["Individual targeting identified"],
                mitigations=["Ensure legal basis for targeting", "Document justification"],
            ))
        
        # Bias concerns
        bias_score = context.get("bias_score", 0)
        if bias_score > 0.1:
            factors.append(RiskFactor(
                factor_id=f"civil-{uuid4().hex[:8]}",
                dimension=RiskDimension.CIVIL_RIGHTS_IMPACT,
                name="Algorithmic Bias",
                description=f"Potential algorithmic bias detected: {bias_score:.2f}",
                weight=0.35,
                score=min(95, int(bias_score * 200)),
                evidence=[f"Bias score: {bias_score:.2f}"],
                mitigations=["Review algorithm for bias", "Apply fairness corrections"],
            ))
        
        # Predictive policing
        if action_category == ActionCategory.PREDICTIVE_POLICING:
            factors.append(RiskFactor(
                factor_id=f"civil-{uuid4().hex[:8]}",
                dimension=RiskDimension.CIVIL_RIGHTS_IMPACT,
                name="Predictive Policing",
                description="Action uses predictive policing models",
                weight=0.3,
                score=45,
                evidence=["Predictive model in use"],
                mitigations=["Ensure model is audited for bias", "Human review of predictions"],
            ))
        
        # Default factor
        if not factors:
            factors.append(RiskFactor(
                factor_id=f"civil-{uuid4().hex[:8]}",
                dimension=RiskDimension.CIVIL_RIGHTS_IMPACT,
                name="Standard Civil Rights Consideration",
                description="Standard civil rights considerations apply",
                weight=1.0,
                score=10,
                evidence=["No elevated civil rights concerns"],
                mitigations=["Follow standard procedures"],
            ))
        
        return factors
    
    def _assess_jurisdictional_authority(
        self,
        action_category: ActionCategory,
        context: Dict[str, Any],
    ) -> List[RiskFactor]:
        """Assess jurisdictional authority risk factors."""
        factors = []
        
        # Outside city limits
        if context.get("outside_city_limits", False):
            factors.append(RiskFactor(
                factor_id=f"juris-{uuid4().hex[:8]}",
                dimension=RiskDimension.JURISDICTIONAL_AUTHORITY,
                name="Outside Jurisdiction",
                description="Action extends beyond city limits",
                weight=0.5,
                score=75,
                evidence=["Location outside Riviera Beach city limits"],
                mitigations=["Coordinate with appropriate jurisdiction", "Obtain mutual aid agreement"],
            ))
        
        # Federal involvement
        if context.get("involves_federal_matters", False):
            factors.append(RiskFactor(
                factor_id=f"juris-{uuid4().hex[:8]}",
                dimension=RiskDimension.JURISDICTIONAL_AUTHORITY,
                name="Federal Jurisdiction",
                description="Action involves federal matters",
                weight=0.4,
                score=60,
                evidence=["Federal jurisdiction implicated"],
                mitigations=["Coordinate with federal agencies", "Follow federal protocols"],
            ))
        
        # Multi-agency operation
        if context.get("multi_agency", False):
            factors.append(RiskFactor(
                factor_id=f"juris-{uuid4().hex[:8]}",
                dimension=RiskDimension.JURISDICTIONAL_AUTHORITY,
                name="Multi-Agency Operation",
                description="Action involves multiple agencies",
                weight=0.3,
                score=35,
                evidence=["Multiple agencies involved"],
                mitigations=["Establish clear command structure", "Define roles and responsibilities"],
            ))
        
        # Emergency declaration
        if context.get("emergency_declared", False):
            factors.append(RiskFactor(
                factor_id=f"juris-{uuid4().hex[:8]}",
                dimension=RiskDimension.JURISDICTIONAL_AUTHORITY,
                name="Emergency Powers",
                description="Operating under emergency declaration",
                weight=0.3,
                score=25,
                evidence=["Emergency declaration in effect"],
                mitigations=["Ensure actions within emergency powers scope"],
            ))
        
        # Default factor
        if not factors:
            factors.append(RiskFactor(
                factor_id=f"juris-{uuid4().hex[:8]}",
                dimension=RiskDimension.JURISDICTIONAL_AUTHORITY,
                name="Standard Jurisdiction",
                description="Operating within normal jurisdictional authority",
                weight=1.0,
                score=10,
                evidence=["Within Riviera Beach jurisdiction"],
                mitigations=["Follow standard procedures"],
            ))
        
        return factors
    
    def _assess_operational_consequence(
        self,
        action_category: ActionCategory,
        context: Dict[str, Any],
    ) -> List[RiskFactor]:
        """Assess operational consequence risk factors."""
        factors = []
        
        # Resource commitment
        resources = context.get("resources_committed", 0)
        if resources > 5:
            factors.append(RiskFactor(
                factor_id=f"ops-{uuid4().hex[:8]}",
                dimension=RiskDimension.OPERATIONAL_CONSEQUENCE,
                name="Resource Commitment",
                description=f"Significant resource commitment: {resources} units",
                weight=0.3,
                score=min(80, resources * 8),
                evidence=[f"Resources: {resources} units"],
                mitigations=["Ensure adequate coverage elsewhere", "Plan for contingencies"],
            ))
        
        # Irreversibility
        if context.get("irreversible", False):
            factors.append(RiskFactor(
                factor_id=f"ops-{uuid4().hex[:8]}",
                dimension=RiskDimension.OPERATIONAL_CONSEQUENCE,
                name="Irreversible Action",
                description="Action cannot be easily reversed",
                weight=0.4,
                score=70,
                evidence=["Action is irreversible"],
                mitigations=["Ensure thorough review before execution", "Document decision process"],
            ))
        
        # Public safety impact
        if context.get("affects_public_safety", False):
            factors.append(RiskFactor(
                factor_id=f"ops-{uuid4().hex[:8]}",
                dimension=RiskDimension.OPERATIONAL_CONSEQUENCE,
                name="Public Safety Impact",
                description="Action directly affects public safety",
                weight=0.35,
                score=55,
                evidence=["Public safety implications"],
                mitigations=["Coordinate with emergency services", "Prepare public communications"],
            ))
        
        # Evacuation
        if action_category == ActionCategory.EVACUATION:
            affected = context.get("affected_population", 0)
            factors.append(RiskFactor(
                factor_id=f"ops-{uuid4().hex[:8]}",
                dimension=RiskDimension.OPERATIONAL_CONSEQUENCE,
                name="Evacuation Operation",
                description=f"Evacuation affecting {affected} people",
                weight=0.4,
                score=min(95, 40 + affected // 100),
                evidence=[f"Affected population: {affected}"],
                mitigations=["Coordinate with all agencies", "Prepare shelters", "Traffic management"],
            ))
        
        # Mass alert
        if action_category == ActionCategory.MASS_ALERT:
            factors.append(RiskFactor(
                factor_id=f"ops-{uuid4().hex[:8]}",
                dimension=RiskDimension.OPERATIONAL_CONSEQUENCE,
                name="Mass Alert",
                description="Mass public alert being issued",
                weight=0.35,
                score=50,
                evidence=["Mass alert planned"],
                mitigations=["Verify information accuracy", "Prepare for public response"],
            ))
        
        # Default factor
        if not factors:
            factors.append(RiskFactor(
                factor_id=f"ops-{uuid4().hex[:8]}",
                dimension=RiskDimension.OPERATIONAL_CONSEQUENCE,
                name="Standard Operations",
                description="Standard operational considerations",
                weight=1.0,
                score=15,
                evidence=["Normal operational scope"],
                mitigations=["Follow standard procedures"],
            ))
        
        return factors
    
    def _assess_political_public_risk(
        self,
        action_category: ActionCategory,
        context: Dict[str, Any],
    ) -> List[RiskFactor]:
        """Assess political and public risk factors."""
        factors = []
        
        # Media attention
        if context.get("high_media_attention", False):
            factors.append(RiskFactor(
                factor_id=f"pol-{uuid4().hex[:8]}",
                dimension=RiskDimension.POLITICAL_PUBLIC_RISK,
                name="Media Attention",
                description="Action likely to attract media attention",
                weight=0.35,
                score=60,
                evidence=["High media interest expected"],
                mitigations=["Prepare public affairs response", "Document actions thoroughly"],
            ))
        
        # Public event
        if context.get("during_public_event", False):
            factors.append(RiskFactor(
                factor_id=f"pol-{uuid4().hex[:8]}",
                dimension=RiskDimension.POLITICAL_PUBLIC_RISK,
                name="Public Event",
                description="Action during public event",
                weight=0.3,
                score=45,
                evidence=["Public event in progress"],
                mitigations=["Minimize disruption", "Coordinate with event organizers"],
            ))
        
        # Protest/assembly
        if context.get("involves_protest", False) or context.get("is_peaceful_assembly", False):
            factors.append(RiskFactor(
                factor_id=f"pol-{uuid4().hex[:8]}",
                dimension=RiskDimension.POLITICAL_PUBLIC_RISK,
                name="Protest/Assembly",
                description="Action involves protest or assembly",
                weight=0.4,
                score=70,
                evidence=["Protest or assembly involved"],
                mitigations=["Respect First Amendment rights", "Document any violations"],
            ))
        
        # Sensitive location
        if context.get("sensitive_location", False):
            location_type = context.get("location_type", "unknown")
            factors.append(RiskFactor(
                factor_id=f"pol-{uuid4().hex[:8]}",
                dimension=RiskDimension.POLITICAL_PUBLIC_RISK,
                name="Sensitive Location",
                description=f"Action at sensitive location: {location_type}",
                weight=0.3,
                score=55,
                evidence=[f"Location type: {location_type}"],
                mitigations=["Exercise heightened discretion", "Coordinate with stakeholders"],
            ))
        
        # Community impact
        community_impact = context.get("community_impact_score", 0)
        if community_impact > 0.3:
            factors.append(RiskFactor(
                factor_id=f"pol-{uuid4().hex[:8]}",
                dimension=RiskDimension.POLITICAL_PUBLIC_RISK,
                name="Community Impact",
                description=f"Significant community impact expected: {community_impact:.2f}",
                weight=0.35,
                score=int(community_impact * 100),
                evidence=[f"Community impact score: {community_impact:.2f}"],
                mitigations=["Community outreach", "Transparent communication"],
            ))
        
        # Default factor
        if not factors:
            factors.append(RiskFactor(
                factor_id=f"pol-{uuid4().hex[:8]}",
                dimension=RiskDimension.POLITICAL_PUBLIC_RISK,
                name="Standard Public Consideration",
                description="Standard public relations considerations",
                weight=1.0,
                score=10,
                evidence=["No elevated public concerns"],
                mitigations=["Follow standard procedures"],
            ))
        
        return factors
    
    def _calculate_dimension_score(self, factors: List[RiskFactor]) -> float:
        """Calculate weighted score for a dimension."""
        if not factors:
            return 0.0
        
        total_weight = sum(f.weight for f in factors)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(f.weighted_score() for f in factors)
        return weighted_sum / total_weight
    
    def _determine_category(self, score: int) -> RiskCategory:
        """Determine risk category from score."""
        for category, (low, high) in self._thresholds.items():
            if low <= score < high:
                return category
        return RiskCategory.CRITICAL
    
    def _generate_recommendations(
        self,
        score: int,
        category: RiskCategory,
        factors: List[RiskFactor],
        action_category: ActionCategory,
    ) -> List[str]:
        """Generate recommendations based on risk assessment."""
        recommendations = []
        
        if category == RiskCategory.CRITICAL:
            recommendations.append("CRITICAL: Immediate command staff review required")
            recommendations.append("Consider alternative approaches with lower risk")
            recommendations.append("Ensure legal counsel review before proceeding")
        
        elif category == RiskCategory.HIGH:
            recommendations.append("HIGH RISK: Supervisor approval required")
            recommendations.append("Document all decision factors thoroughly")
            recommendations.append("Prepare contingency plans")
        
        elif category == RiskCategory.ELEVATED:
            recommendations.append("ELEVATED: Enhanced monitoring recommended")
            recommendations.append("Ensure proper documentation")
        
        else:
            recommendations.append("Standard procedures apply")
        
        # Add specific recommendations based on high-scoring factors
        high_factors = [f for f in factors if f.score >= 60]
        for factor in high_factors[:3]:  # Top 3 high-scoring factors
            recommendations.append(f"Address {factor.name}: {factor.mitigations[0] if factor.mitigations else 'Review carefully'}")
        
        return recommendations
    
    def get_assessment(self, assessment_id: str) -> Optional[RiskAssessment]:
        """Get an assessment by ID."""
        return self._assessments.get(assessment_id)
    
    def get_assessment_history(
        self,
        limit: int = 100,
        category_filter: Optional[RiskCategory] = None,
    ) -> List[RiskAssessment]:
        """Get assessment history with optional filtering."""
        assessments = self._assessment_history[-limit:]
        if category_filter:
            assessments = [a for a in assessments if a.category == category_filter]
        return assessments
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get risk scoring statistics."""
        if not self._assessment_history:
            return {
                "total_assessments": 0,
                "average_score": 0,
                "by_category": {},
            }
        
        return {
            "total_assessments": len(self._assessment_history),
            "average_score": sum(a.total_score for a in self._assessment_history) / len(self._assessment_history),
            "by_category": {
                cat.value: len([a for a in self._assessment_history if a.category == cat])
                for cat in RiskCategory
            },
            "human_review_required": len([a for a in self._assessment_history if a.requires_human_review]),
        }


# Singleton accessor
_risk_scoring_instance: Optional[GovernanceRiskScoringEngine] = None


def get_risk_scoring_engine() -> GovernanceRiskScoringEngine:
    """Get the singleton GovernanceRiskScoringEngine instance."""
    global _risk_scoring_instance
    if _risk_scoring_instance is None:
        _risk_scoring_instance = GovernanceRiskScoringEngine()
    return _risk_scoring_instance
