"""
Phase 26: Protected Community Safeguards

Creates rule sets for protected communities:
- Black community
- Hispanic community
- LGBTQ+ youth
- People with disabilities
- Veterans
- Faith communities
- Aging population

Rules include:
- Higher bias sensitivity
- Automatic review for disproportionate impact
- Prevention of over-surveillance
- Community engagement requirements
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class CommunityType(Enum):
    """Protected community types for Riviera Beach."""
    BLACK_COMMUNITY = "BLACK_COMMUNITY"
    HISPANIC_COMMUNITY = "HISPANIC_COMMUNITY"
    LGBTQ_YOUTH = "LGBTQ_YOUTH"
    PEOPLE_WITH_DISABILITIES = "PEOPLE_WITH_DISABILITIES"
    VETERANS = "VETERANS"
    FAITH_COMMUNITIES = "FAITH_COMMUNITIES"
    AGING_POPULATION = "AGING_POPULATION"
    LOW_INCOME = "LOW_INCOME"
    IMMIGRANT_COMMUNITY = "IMMIGRANT_COMMUNITY"
    HOMELESS_POPULATION = "HOMELESS_POPULATION"


class SafeguardLevel(Enum):
    """Safeguard protection levels."""
    STANDARD = "STANDARD"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    MAXIMUM = "MAXIMUM"


class TriggerType(Enum):
    """Types of safeguard triggers."""
    BIAS_THRESHOLD = "BIAS_THRESHOLD"
    DISPROPORTIONATE_IMPACT = "DISPROPORTIONATE_IMPACT"
    OVER_SURVEILLANCE = "OVER_SURVEILLANCE"
    ENFORCEMENT_DISPARITY = "ENFORCEMENT_DISPARITY"
    COMMUNITY_COMPLAINT = "COMMUNITY_COMPLAINT"
    PATTERN_DETECTED = "PATTERN_DETECTED"


@dataclass
class SafeguardRule:
    """Individual safeguard rule for a protected community."""
    rule_id: str
    community_type: CommunityType
    name: str
    description: str
    trigger_type: TriggerType
    threshold: float
    action_required: str
    auto_review: bool
    escalation_level: str
    notification_required: bool
    community_liaison_required: bool


@dataclass
class CommunityProfile:
    """Profile for a protected community in Riviera Beach."""
    community_type: CommunityType
    population_estimate: int
    population_percentage: float
    geographic_concentration: List[str]
    historical_concerns: List[str]
    safeguard_level: SafeguardLevel
    bias_sensitivity_multiplier: float
    surveillance_limit_factor: float
    engagement_requirements: List[str]
    liaison_contacts: List[str]


@dataclass
class SafeguardCheck:
    """Result of a safeguard check."""
    check_id: str
    action_id: str
    timestamp: datetime
    community_types_affected: List[CommunityType]
    triggered_rules: List[SafeguardRule]
    safeguard_level: SafeguardLevel
    requires_review: bool
    requires_community_liaison: bool
    recommendations: List[str]
    engagement_actions: List[str]
    explanation: str


@dataclass
class ImpactAssessment:
    """Assessment of impact on protected communities."""
    assessment_id: str
    action_type: str
    timestamp: datetime
    communities_assessed: List[CommunityType]
    impact_scores: Dict[str, float]
    disproportionate_impact: bool
    affected_population_estimate: int
    mitigation_required: bool
    mitigation_actions: List[str]
    community_notification_required: bool


class ProtectedCommunitySafeguards:
    """
    Engine for protected community safeguards.
    
    Implements higher bias sensitivity, automatic review for
    disproportionate impact, prevention of over-surveillance,
    and community engagement requirements.
    """
    
    _instance = None
    
    RIVIERA_BEACH_COMMUNITIES = {
        CommunityType.BLACK_COMMUNITY: CommunityProfile(
            community_type=CommunityType.BLACK_COMMUNITY,
            population_estimate=25056,
            population_percentage=66.0,
            geographic_concentration=["Downtown", "Singer Island", "Riviera Beach Heights"],
            historical_concerns=[
                "Historical over-policing",
                "Disparate enforcement rates",
                "Traffic stop disparities",
            ],
            safeguard_level=SafeguardLevel.HIGH,
            bias_sensitivity_multiplier=1.5,
            surveillance_limit_factor=0.7,
            engagement_requirements=[
                "Quarterly community meetings",
                "Annual disparity report",
                "Community advisory board representation",
            ],
            liaison_contacts=["Community Relations Unit", "NAACP Riviera Beach Chapter"],
        ),
        CommunityType.HISPANIC_COMMUNITY: CommunityProfile(
            community_type=CommunityType.HISPANIC_COMMUNITY,
            population_estimate=3037,
            population_percentage=8.0,
            geographic_concentration=["West Riviera Beach", "Industrial District"],
            historical_concerns=[
                "Language barriers",
                "Immigration enforcement concerns",
                "Underreporting of crimes",
            ],
            safeguard_level=SafeguardLevel.ELEVATED,
            bias_sensitivity_multiplier=1.3,
            surveillance_limit_factor=0.8,
            engagement_requirements=[
                "Bilingual outreach materials",
                "Spanish-speaking liaison",
                "Immigration policy transparency",
            ],
            liaison_contacts=["Hispanic Affairs Office", "Community Relations Unit"],
        ),
        CommunityType.LGBTQ_YOUTH: CommunityProfile(
            community_type=CommunityType.LGBTQ_YOUTH,
            population_estimate=500,
            population_percentage=1.3,
            geographic_concentration=["Citywide"],
            historical_concerns=[
                "Harassment and bullying",
                "Mental health crisis response",
                "Family rejection situations",
            ],
            safeguard_level=SafeguardLevel.HIGH,
            bias_sensitivity_multiplier=1.5,
            surveillance_limit_factor=0.6,
            engagement_requirements=[
                "LGBTQ+ sensitivity training",
                "Safe space protocols",
                "Mental health co-responder availability",
            ],
            liaison_contacts=["Youth Services", "LGBTQ+ Resource Center"],
        ),
        CommunityType.PEOPLE_WITH_DISABILITIES: CommunityProfile(
            community_type=CommunityType.PEOPLE_WITH_DISABILITIES,
            population_estimate=4556,
            population_percentage=12.0,
            geographic_concentration=["Citywide"],
            historical_concerns=[
                "ADA compliance",
                "Communication barriers",
                "Use of force incidents",
            ],
            safeguard_level=SafeguardLevel.HIGH,
            bias_sensitivity_multiplier=1.4,
            surveillance_limit_factor=0.7,
            engagement_requirements=[
                "ADA compliance verification",
                "Disability awareness training",
                "Accessible communication options",
            ],
            liaison_contacts=["ADA Coordinator", "Disability Rights Florida"],
        ),
        CommunityType.VETERANS: CommunityProfile(
            community_type=CommunityType.VETERANS,
            population_estimate=2278,
            population_percentage=6.0,
            geographic_concentration=["Singer Island", "Riviera Beach Heights"],
            historical_concerns=[
                "PTSD-related incidents",
                "Mental health crisis response",
                "Homelessness",
            ],
            safeguard_level=SafeguardLevel.ELEVATED,
            bias_sensitivity_multiplier=1.2,
            surveillance_limit_factor=0.85,
            engagement_requirements=[
                "Veteran-specific crisis intervention",
                "VA coordination protocols",
                "Veteran peer support availability",
            ],
            liaison_contacts=["Veterans Affairs Liaison", "VA Medical Center"],
        ),
        CommunityType.FAITH_COMMUNITIES: CommunityProfile(
            community_type=CommunityType.FAITH_COMMUNITIES,
            population_estimate=20000,
            population_percentage=52.7,
            geographic_concentration=["Citywide - 50+ places of worship"],
            historical_concerns=[
                "Religious freedom",
                "House of worship security",
                "Religious expression protection",
            ],
            safeguard_level=SafeguardLevel.ELEVATED,
            bias_sensitivity_multiplier=1.2,
            surveillance_limit_factor=0.8,
            engagement_requirements=[
                "Interfaith council engagement",
                "House of worship security assessments",
                "Religious holiday awareness",
            ],
            liaison_contacts=["Interfaith Council", "Community Relations Unit"],
        ),
        CommunityType.AGING_POPULATION: CommunityProfile(
            community_type=CommunityType.AGING_POPULATION,
            population_estimate=5695,
            population_percentage=15.0,
            geographic_concentration=["Singer Island", "Riviera Beach Marina"],
            historical_concerns=[
                "Elder abuse",
                "Financial exploitation",
                "Medical emergency response",
            ],
            safeguard_level=SafeguardLevel.ELEVATED,
            bias_sensitivity_multiplier=1.2,
            surveillance_limit_factor=0.85,
            engagement_requirements=[
                "Elder abuse prevention protocols",
                "Senior center partnerships",
                "Medical alert coordination",
            ],
            liaison_contacts=["Senior Services", "Adult Protective Services"],
        ),
    }
    
    SAFEGUARD_RULES = [
        SafeguardRule(
            rule_id="SG-001",
            community_type=CommunityType.BLACK_COMMUNITY,
            name="Disparate Impact Review",
            description="Automatic review when enforcement actions show disparate impact",
            trigger_type=TriggerType.DISPROPORTIONATE_IMPACT,
            threshold=1.2,
            action_required="Supervisor review and documentation",
            auto_review=True,
            escalation_level="SUPERVISOR",
            notification_required=True,
            community_liaison_required=False,
        ),
        SafeguardRule(
            rule_id="SG-002",
            community_type=CommunityType.BLACK_COMMUNITY,
            name="Over-Surveillance Prevention",
            description="Limit surveillance in predominantly Black neighborhoods",
            trigger_type=TriggerType.OVER_SURVEILLANCE,
            threshold=0.7,
            action_required="Reduce surveillance intensity",
            auto_review=True,
            escalation_level="COMMAND",
            notification_required=True,
            community_liaison_required=True,
        ),
        SafeguardRule(
            rule_id="SG-003",
            community_type=CommunityType.HISPANIC_COMMUNITY,
            name="Immigration Enforcement Separation",
            description="Separate local policing from immigration enforcement",
            trigger_type=TriggerType.PATTERN_DETECTED,
            threshold=0.0,
            action_required="Verify no immigration enforcement mixing",
            auto_review=True,
            escalation_level="COMMAND",
            notification_required=True,
            community_liaison_required=True,
        ),
        SafeguardRule(
            rule_id="SG-004",
            community_type=CommunityType.LGBTQ_YOUTH,
            name="Youth Protection Protocol",
            description="Enhanced protections for LGBTQ+ youth interactions",
            trigger_type=TriggerType.BIAS_THRESHOLD,
            threshold=0.5,
            action_required="Engage youth services specialist",
            auto_review=True,
            escalation_level="SUPERVISOR",
            notification_required=True,
            community_liaison_required=True,
        ),
        SafeguardRule(
            rule_id="SG-005",
            community_type=CommunityType.PEOPLE_WITH_DISABILITIES,
            name="ADA Compliance Check",
            description="Ensure ADA compliance in all interactions",
            trigger_type=TriggerType.PATTERN_DETECTED,
            threshold=0.0,
            action_required="Verify ADA accommodations provided",
            auto_review=True,
            escalation_level="SUPERVISOR",
            notification_required=False,
            community_liaison_required=False,
        ),
        SafeguardRule(
            rule_id="SG-006",
            community_type=CommunityType.VETERANS,
            name="PTSD-Aware Response",
            description="Apply PTSD-aware protocols for veteran interactions",
            trigger_type=TriggerType.PATTERN_DETECTED,
            threshold=0.0,
            action_required="Engage CIT-trained officer",
            auto_review=False,
            escalation_level="SUPERVISOR",
            notification_required=False,
            community_liaison_required=False,
        ),
        SafeguardRule(
            rule_id="SG-007",
            community_type=CommunityType.FAITH_COMMUNITIES,
            name="Religious Freedom Protection",
            description="Protect religious expression and assembly",
            trigger_type=TriggerType.BIAS_THRESHOLD,
            threshold=0.5,
            action_required="Review for religious freedom compliance",
            auto_review=True,
            escalation_level="SUPERVISOR",
            notification_required=True,
            community_liaison_required=True,
        ),
        SafeguardRule(
            rule_id="SG-008",
            community_type=CommunityType.AGING_POPULATION,
            name="Elder Protection Protocol",
            description="Enhanced protections for elderly individuals",
            trigger_type=TriggerType.PATTERN_DETECTED,
            threshold=0.0,
            action_required="Apply elder-specific protocols",
            auto_review=False,
            escalation_level="SUPERVISOR",
            notification_required=False,
            community_liaison_required=False,
        ),
    ]
    
    def __init__(self):
        self._check_history: List[SafeguardCheck] = []
        self._impact_assessments: List[ImpactAssessment] = []
    
    @classmethod
    def get_instance(cls) -> "ProtectedCommunitySafeguards":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def check_safeguards(
        self,
        action_id: str,
        action_type: str,
        context: Dict[str, Any],
    ) -> SafeguardCheck:
        """
        Check if action triggers any protected community safeguards.
        
        Args:
            action_id: Unique identifier for the action
            action_type: Type of action being checked
            context: Context including location, demographics, etc.
            
        Returns:
            SafeguardCheck with triggered rules and recommendations
        """
        check_id = f"safeguard-{uuid.uuid4().hex[:12]}"
        affected_communities = []
        triggered_rules = []
        recommendations = []
        engagement_actions = []
        
        location = context.get("location", {})
        demographics = context.get("demographics", {})
        subject_info = context.get("subject_info", {})
        
        affected_communities = self._identify_affected_communities(
            location, demographics, subject_info
        )
        
        for community in affected_communities:
            community_rules = self._get_rules_for_community(community)
            for rule in community_rules:
                if self._rule_triggered(rule, action_type, context):
                    triggered_rules.append(rule)
        
        safeguard_level = self._determine_safeguard_level(affected_communities)
        
        requires_review = any(r.auto_review for r in triggered_rules)
        requires_liaison = any(r.community_liaison_required for r in triggered_rules)
        
        recommendations = self._generate_recommendations(
            affected_communities, triggered_rules, action_type
        )
        
        engagement_actions = self._get_engagement_actions(affected_communities)
        
        explanation = self._generate_explanation(
            affected_communities, triggered_rules, safeguard_level
        )
        
        check = SafeguardCheck(
            check_id=check_id,
            action_id=action_id,
            timestamp=datetime.now(),
            community_types_affected=affected_communities,
            triggered_rules=triggered_rules,
            safeguard_level=safeguard_level,
            requires_review=requires_review,
            requires_community_liaison=requires_liaison,
            recommendations=recommendations,
            engagement_actions=engagement_actions,
            explanation=explanation,
        )
        
        self._check_history.append(check)
        return check
    
    def assess_community_impact(
        self,
        action_type: str,
        context: Dict[str, Any],
    ) -> ImpactAssessment:
        """
        Assess the impact of an action on protected communities.
        
        Args:
            action_type: Type of action being assessed
            context: Context including scope, duration, etc.
            
        Returns:
            ImpactAssessment with impact scores and mitigation actions
        """
        assessment_id = f"impact-{uuid.uuid4().hex[:12]}"
        
        communities = list(self.RIVIERA_BEACH_COMMUNITIES.keys())
        impact_scores = {}
        affected_population = 0
        
        for community in communities:
            profile = self.RIVIERA_BEACH_COMMUNITIES[community]
            score = self._calculate_impact_score(community, action_type, context)
            impact_scores[community.value] = score
            
            if score > 0.5:
                affected_population += int(profile.population_estimate * score)
        
        disproportionate = self._check_disproportionate_impact(impact_scores)
        
        mitigation_required = disproportionate or max(impact_scores.values()) > 0.7
        mitigation_actions = []
        if mitigation_required:
            mitigation_actions = self._generate_mitigation_actions(
                impact_scores, action_type
            )
        
        notification_required = disproportionate or affected_population > 1000
        
        assessment = ImpactAssessment(
            assessment_id=assessment_id,
            action_type=action_type,
            timestamp=datetime.now(),
            communities_assessed=communities,
            impact_scores=impact_scores,
            disproportionate_impact=disproportionate,
            affected_population_estimate=affected_population,
            mitigation_required=mitigation_required,
            mitigation_actions=mitigation_actions,
            community_notification_required=notification_required,
        )
        
        self._impact_assessments.append(assessment)
        return assessment
    
    def _identify_affected_communities(
        self,
        location: Dict,
        demographics: Dict,
        subject_info: Dict,
    ) -> List[CommunityType]:
        """Identify which protected communities may be affected."""
        affected = []
        
        neighborhood = location.get("neighborhood", "")
        for community, profile in self.RIVIERA_BEACH_COMMUNITIES.items():
            if neighborhood in profile.geographic_concentration:
                affected.append(community)
        
        if demographics.get("majority_black", False):
            if CommunityType.BLACK_COMMUNITY not in affected:
                affected.append(CommunityType.BLACK_COMMUNITY)
        
        if demographics.get("majority_hispanic", False):
            if CommunityType.HISPANIC_COMMUNITY not in affected:
                affected.append(CommunityType.HISPANIC_COMMUNITY)
        
        subject_age = subject_info.get("age", 30)
        if subject_age < 21 and subject_info.get("lgbtq_identified", False):
            if CommunityType.LGBTQ_YOUTH not in affected:
                affected.append(CommunityType.LGBTQ_YOUTH)
        
        if subject_info.get("disability", False):
            if CommunityType.PEOPLE_WITH_DISABILITIES not in affected:
                affected.append(CommunityType.PEOPLE_WITH_DISABILITIES)
        
        if subject_info.get("veteran", False):
            if CommunityType.VETERANS not in affected:
                affected.append(CommunityType.VETERANS)
        
        if subject_age >= 65:
            if CommunityType.AGING_POPULATION not in affected:
                affected.append(CommunityType.AGING_POPULATION)
        
        if location.get("place_of_worship", False):
            if CommunityType.FAITH_COMMUNITIES not in affected:
                affected.append(CommunityType.FAITH_COMMUNITIES)
        
        return affected
    
    def _get_rules_for_community(
        self,
        community: CommunityType,
    ) -> List[SafeguardRule]:
        """Get safeguard rules for a specific community."""
        return [r for r in self.SAFEGUARD_RULES if r.community_type == community]
    
    def _rule_triggered(
        self,
        rule: SafeguardRule,
        action_type: str,
        context: Dict,
    ) -> bool:
        """Check if a safeguard rule is triggered."""
        if rule.trigger_type == TriggerType.DISPROPORTIONATE_IMPACT:
            disparity_ratio = context.get("disparity_ratio", 1.0)
            return disparity_ratio > rule.threshold
        
        elif rule.trigger_type == TriggerType.OVER_SURVEILLANCE:
            surveillance_rate = context.get("surveillance_rate", 0.0)
            profile = self.RIVIERA_BEACH_COMMUNITIES.get(rule.community_type)
            if profile:
                limit = profile.surveillance_limit_factor
                return surveillance_rate > limit
        
        elif rule.trigger_type == TriggerType.BIAS_THRESHOLD:
            bias_score = context.get("bias_score", 0.0)
            profile = self.RIVIERA_BEACH_COMMUNITIES.get(rule.community_type)
            if profile:
                adjusted_threshold = rule.threshold / profile.bias_sensitivity_multiplier
                return bias_score > adjusted_threshold
        
        elif rule.trigger_type == TriggerType.PATTERN_DETECTED:
            return context.get(f"{rule.community_type.value.lower()}_pattern", False)
        
        return False
    
    def _determine_safeguard_level(
        self,
        communities: List[CommunityType],
    ) -> SafeguardLevel:
        """Determine overall safeguard level from affected communities."""
        if not communities:
            return SafeguardLevel.STANDARD
        
        levels = []
        for community in communities:
            profile = self.RIVIERA_BEACH_COMMUNITIES.get(community)
            if profile:
                levels.append(profile.safeguard_level)
        
        if SafeguardLevel.MAXIMUM in levels:
            return SafeguardLevel.MAXIMUM
        elif SafeguardLevel.HIGH in levels:
            return SafeguardLevel.HIGH
        elif SafeguardLevel.ELEVATED in levels:
            return SafeguardLevel.ELEVATED
        return SafeguardLevel.STANDARD
    
    def _generate_recommendations(
        self,
        communities: List[CommunityType],
        rules: List[SafeguardRule],
        action_type: str,
    ) -> List[str]:
        """Generate recommendations based on affected communities and rules."""
        recommendations = []
        
        for rule in rules:
            recommendations.append(rule.action_required)
        
        for community in communities:
            profile = self.RIVIERA_BEACH_COMMUNITIES.get(community)
            if profile:
                if profile.safeguard_level in [SafeguardLevel.HIGH, SafeguardLevel.MAXIMUM]:
                    recommendations.append(
                        f"Apply enhanced protocols for {community.value}"
                    )
                for req in profile.engagement_requirements[:1]:
                    recommendations.append(req)
        
        return list(set(recommendations))
    
    def _get_engagement_actions(
        self,
        communities: List[CommunityType],
    ) -> List[str]:
        """Get required community engagement actions."""
        actions = []
        
        for community in communities:
            profile = self.RIVIERA_BEACH_COMMUNITIES.get(community)
            if profile:
                for contact in profile.liaison_contacts:
                    actions.append(f"Notify {contact}")
        
        return list(set(actions))
    
    def _generate_explanation(
        self,
        communities: List[CommunityType],
        rules: List[SafeguardRule],
        level: SafeguardLevel,
    ) -> str:
        """Generate human-readable explanation."""
        if not communities:
            return "No protected community safeguards triggered."
        
        community_names = [c.value.replace("_", " ").title() for c in communities]
        
        explanation = f"Safeguard Level: {level.value}. "
        explanation += f"Affected communities: {', '.join(community_names)}. "
        
        if rules:
            explanation += f"{len(rules)} safeguard rule(s) triggered. "
            explanation += f"Primary rule: {rules[0].name}."
        
        return explanation
    
    def _calculate_impact_score(
        self,
        community: CommunityType,
        action_type: str,
        context: Dict,
    ) -> float:
        """Calculate impact score for a community."""
        base_score = 0.3
        
        profile = self.RIVIERA_BEACH_COMMUNITIES.get(community)
        if not profile:
            return base_score
        
        if action_type in ["surveillance", "enforcement", "patrol"]:
            base_score += 0.2
        
        base_score *= profile.bias_sensitivity_multiplier
        
        if context.get("high_intensity", False):
            base_score += 0.2
        
        if context.get("extended_duration", False):
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _check_disproportionate_impact(
        self,
        impact_scores: Dict[str, float],
    ) -> bool:
        """Check if impact is disproportionate across communities."""
        if not impact_scores:
            return False
        
        scores = list(impact_scores.values())
        avg_score = sum(scores) / len(scores)
        
        for score in scores:
            if score > avg_score * 1.5:
                return True
        
        return False
    
    def _generate_mitigation_actions(
        self,
        impact_scores: Dict[str, float],
        action_type: str,
    ) -> List[str]:
        """Generate mitigation actions for high-impact scenarios."""
        actions = []
        
        high_impact = [k for k, v in impact_scores.items() if v > 0.7]
        
        for community_name in high_impact:
            actions.append(f"Reduce {action_type} intensity in {community_name} areas")
            actions.append(f"Engage {community_name} liaison before proceeding")
        
        actions.append("Document mitigation measures taken")
        actions.append("Schedule post-action community impact review")
        
        return actions
    
    def get_community_profile(
        self,
        community: CommunityType,
    ) -> Optional[CommunityProfile]:
        """Get profile for a specific community."""
        return self.RIVIERA_BEACH_COMMUNITIES.get(community)
    
    def get_all_community_profiles(self) -> Dict[CommunityType, CommunityProfile]:
        """Get all community profiles."""
        return self.RIVIERA_BEACH_COMMUNITIES.copy()
    
    def get_check_history(
        self,
        community: Optional[CommunityType] = None,
        limit: int = 100,
    ) -> List[SafeguardCheck]:
        """Get safeguard check history."""
        results = self._check_history
        
        if community:
            results = [
                r for r in results
                if community in r.community_types_affected
            ]
        
        return results[-limit:]
    
    def get_impact_assessments(
        self,
        limit: int = 100,
    ) -> List[ImpactAssessment]:
        """Get impact assessment history."""
        return self._impact_assessments[-limit:]


def get_protected_community_safeguards() -> ProtectedCommunitySafeguards:
    """Get the singleton ProtectedCommunitySafeguards instance."""
    return ProtectedCommunitySafeguards.get_instance()
