"""
Phase 26: Ethics Score Engine

Computes a combined ethics score for every AI-driven action based on:
- Fairness metrics
- Civil rights exposure
- Use-of-force risk
- Historical disparities
- Policy compliance
- Transparency requirements

Output:
- Score 0-100
- Color-coded level
- Required actions (allow, block, modify, review)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class EthicsLevel(Enum):
    """Ethics score levels with color coding."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    CONCERNING = "CONCERNING"
    CRITICAL = "CRITICAL"


class RequiredAction(Enum):
    """Required actions based on ethics score."""
    ALLOW = "ALLOW"
    ALLOW_WITH_LOGGING = "ALLOW_WITH_LOGGING"
    MODIFY = "MODIFY"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class EthicsComponent(Enum):
    """Components of the ethics score."""
    FAIRNESS = "FAIRNESS"
    CIVIL_RIGHTS = "CIVIL_RIGHTS"
    USE_OF_FORCE = "USE_OF_FORCE"
    HISTORICAL_DISPARITY = "HISTORICAL_DISPARITY"
    POLICY_COMPLIANCE = "POLICY_COMPLIANCE"
    TRANSPARENCY = "TRANSPARENCY"
    COMMUNITY_IMPACT = "COMMUNITY_IMPACT"
    ACCOUNTABILITY = "ACCOUNTABILITY"


@dataclass
class ComponentScore:
    """Score for an individual ethics component."""
    component: EthicsComponent
    score: float
    max_score: float
    weight: float
    contributing_factors: List[str]
    improvement_suggestions: List[str]


@dataclass
class EthicsAssessment:
    """Complete ethics assessment for an action."""
    assessment_id: str
    action_id: str
    action_type: str
    timestamp: datetime
    total_score: float
    ethics_level: EthicsLevel
    color_code: str
    component_scores: List[ComponentScore]
    required_action: RequiredAction
    action_conditions: List[str]
    improvement_recommendations: List[str]
    policy_references: List[str]
    explanation: str
    audit_required: bool
    human_review_required: bool


class EthicsScoreEngine:
    """
    Engine for computing combined ethics scores.
    
    Evaluates fairness, civil rights, use-of-force risk,
    historical disparities, policy compliance, and transparency.
    """
    
    _instance = None
    
    LEVEL_THRESHOLDS = {
        EthicsLevel.EXCELLENT: (90, 100),
        EthicsLevel.GOOD: (75, 89),
        EthicsLevel.ACCEPTABLE: (60, 74),
        EthicsLevel.CONCERNING: (40, 59),
        EthicsLevel.CRITICAL: (0, 39),
    }
    
    LEVEL_COLORS = {
        EthicsLevel.EXCELLENT: "#22C55E",
        EthicsLevel.GOOD: "#84CC16",
        EthicsLevel.ACCEPTABLE: "#EAB308",
        EthicsLevel.CONCERNING: "#F97316",
        EthicsLevel.CRITICAL: "#EF4444",
    }
    
    COMPONENT_WEIGHTS = {
        EthicsComponent.FAIRNESS: 0.20,
        EthicsComponent.CIVIL_RIGHTS: 0.20,
        EthicsComponent.USE_OF_FORCE: 0.15,
        EthicsComponent.HISTORICAL_DISPARITY: 0.15,
        EthicsComponent.POLICY_COMPLIANCE: 0.10,
        EthicsComponent.TRANSPARENCY: 0.10,
        EthicsComponent.COMMUNITY_IMPACT: 0.05,
        EthicsComponent.ACCOUNTABILITY: 0.05,
    }
    
    ACTION_THRESHOLDS = {
        RequiredAction.ALLOW: 90,
        RequiredAction.ALLOW_WITH_LOGGING: 75,
        RequiredAction.MODIFY: 60,
        RequiredAction.REVIEW: 40,
        RequiredAction.BLOCK: 0,
    }
    
    def __init__(self):
        self._assessment_history: List[EthicsAssessment] = []
    
    @classmethod
    def get_instance(cls) -> "EthicsScoreEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def compute_ethics_score(
        self,
        action_id: str,
        action_type: str,
        context: Dict[str, Any],
    ) -> EthicsAssessment:
        """
        Compute comprehensive ethics score for an action.
        
        Args:
            action_id: Unique identifier for the action
            action_type: Type of action being assessed
            context: Context including all relevant factors
            
        Returns:
            EthicsAssessment with score, level, and required actions
        """
        assessment_id = f"ethics-{uuid.uuid4().hex[:12]}"
        component_scores = []
        
        fairness_score = self._compute_fairness_score(context)
        component_scores.append(fairness_score)
        
        civil_rights_score = self._compute_civil_rights_score(context)
        component_scores.append(civil_rights_score)
        
        force_score = self._compute_force_score(context)
        component_scores.append(force_score)
        
        disparity_score = self._compute_disparity_score(context)
        component_scores.append(disparity_score)
        
        policy_score = self._compute_policy_score(context)
        component_scores.append(policy_score)
        
        transparency_score = self._compute_transparency_score(context)
        component_scores.append(transparency_score)
        
        community_score = self._compute_community_score(context)
        component_scores.append(community_score)
        
        accountability_score = self._compute_accountability_score(context)
        component_scores.append(accountability_score)
        
        total_score = sum(
            cs.score * cs.weight for cs in component_scores
        )
        total_score = min(100, max(0, total_score))
        
        ethics_level = self._determine_level(total_score)
        color_code = self.LEVEL_COLORS[ethics_level]
        
        required_action = self._determine_required_action(total_score, context)
        
        action_conditions = self._generate_conditions(
            required_action, component_scores
        )
        
        recommendations = self._generate_recommendations(component_scores)
        
        policy_refs = self._get_policy_references(action_type)
        
        explanation = self._generate_explanation(
            total_score, ethics_level, component_scores, required_action
        )
        
        audit_required = total_score < 75
        human_review_required = total_score < 60 or required_action in [
            RequiredAction.REVIEW, RequiredAction.BLOCK
        ]
        
        assessment = EthicsAssessment(
            assessment_id=assessment_id,
            action_id=action_id,
            action_type=action_type,
            timestamp=datetime.now(),
            total_score=round(total_score, 2),
            ethics_level=ethics_level,
            color_code=color_code,
            component_scores=component_scores,
            required_action=required_action,
            action_conditions=action_conditions,
            improvement_recommendations=recommendations,
            policy_references=policy_refs,
            explanation=explanation,
            audit_required=audit_required,
            human_review_required=human_review_required,
        )
        
        self._assessment_history.append(assessment)
        return assessment
    
    def _compute_fairness_score(self, context: Dict) -> ComponentScore:
        """Compute fairness component score."""
        score = 100.0
        factors = []
        suggestions = []
        
        bias_detected = context.get("bias_detected", False)
        if bias_detected:
            score -= 40
            factors.append("Bias detected in AI output")
            suggestions.append("Review and retrain model for fairness")
        
        disparate_impact = context.get("disparate_impact_ratio", 1.0)
        if disparate_impact < 0.8:
            score -= 30
            factors.append(f"Disparate impact ratio: {disparate_impact:.2f}")
            suggestions.append("Address disparate impact in decision model")
        elif disparate_impact < 0.9:
            score -= 15
            factors.append(f"Marginal disparate impact: {disparate_impact:.2f}")
        
        demographic_parity = context.get("demographic_parity_diff", 0.0)
        if demographic_parity > 0.1:
            score -= 20
            factors.append(f"Demographic parity difference: {demographic_parity:.2f}")
            suggestions.append("Improve demographic parity in outcomes")
        
        if not factors:
            factors.append("No fairness concerns identified")
        
        return ComponentScore(
            component=EthicsComponent.FAIRNESS,
            score=max(0, score),
            max_score=100,
            weight=self.COMPONENT_WEIGHTS[EthicsComponent.FAIRNESS],
            contributing_factors=factors,
            improvement_suggestions=suggestions,
        )
    
    def _compute_civil_rights_score(self, context: Dict) -> ComponentScore:
        """Compute civil rights component score."""
        score = 100.0
        factors = []
        suggestions = []
        
        constitutional_violation = context.get("constitutional_violation", False)
        if constitutional_violation:
            score = 0
            factors.append("Constitutional violation detected")
            suggestions.append("IMMEDIATE: Address constitutional violation")
            return ComponentScore(
                component=EthicsComponent.CIVIL_RIGHTS,
                score=0,
                max_score=100,
                weight=self.COMPONENT_WEIGHTS[EthicsComponent.CIVIL_RIGHTS],
                contributing_factors=factors,
                improvement_suggestions=suggestions,
            )
        
        fourth_amendment_concern = context.get("fourth_amendment_concern", False)
        if fourth_amendment_concern:
            score -= 35
            factors.append("Fourth Amendment concern")
            suggestions.append("Verify warrant or valid exception")
        
        first_amendment_concern = context.get("first_amendment_concern", False)
        if first_amendment_concern:
            score -= 35
            factors.append("First Amendment concern")
            suggestions.append("Ensure protected speech/assembly not targeted")
        
        equal_protection_concern = context.get("equal_protection_concern", False)
        if equal_protection_concern:
            score -= 30
            factors.append("Equal protection concern")
            suggestions.append("Review for discriminatory impact")
        
        if not factors:
            factors.append("No civil rights concerns identified")
        
        return ComponentScore(
            component=EthicsComponent.CIVIL_RIGHTS,
            score=max(0, score),
            max_score=100,
            weight=self.COMPONENT_WEIGHTS[EthicsComponent.CIVIL_RIGHTS],
            contributing_factors=factors,
            improvement_suggestions=suggestions,
        )
    
    def _compute_force_score(self, context: Dict) -> ComponentScore:
        """Compute use-of-force component score."""
        score = 100.0
        factors = []
        suggestions = []
        
        force_risk = context.get("force_risk_score", 0)
        if force_risk > 75:
            score -= 50
            factors.append(f"High force risk: {force_risk}")
            suggestions.append("Apply de-escalation techniques")
        elif force_risk > 50:
            score -= 30
            factors.append(f"Elevated force risk: {force_risk}")
            suggestions.append("Consider de-escalation options")
        elif force_risk > 25:
            score -= 15
            factors.append(f"Moderate force risk: {force_risk}")
        
        excessive_force = context.get("excessive_force_risk", False)
        if excessive_force:
            score -= 40
            factors.append("Excessive force risk identified")
            suggestions.append("Review force continuum compliance")
        
        deescalation_available = context.get("deescalation_available", True)
        if not deescalation_available:
            score -= 10
            factors.append("Limited de-escalation options")
        
        if not factors:
            factors.append("Low use-of-force risk")
        
        return ComponentScore(
            component=EthicsComponent.USE_OF_FORCE,
            score=max(0, score),
            max_score=100,
            weight=self.COMPONENT_WEIGHTS[EthicsComponent.USE_OF_FORCE],
            contributing_factors=factors,
            improvement_suggestions=suggestions,
        )
    
    def _compute_disparity_score(self, context: Dict) -> ComponentScore:
        """Compute historical disparity component score."""
        score = 100.0
        factors = []
        suggestions = []
        
        historical_disparity = context.get("historical_disparity", False)
        if historical_disparity:
            score -= 25
            factors.append("Historical disparity in similar actions")
            suggestions.append("Review historical patterns and adjust")
        
        location_disparity = context.get("location_disparity_score", 0)
        if location_disparity > 0.3:
            score -= 20
            factors.append(f"Location shows enforcement disparity: {location_disparity:.2f}")
            suggestions.append("Review location-based enforcement patterns")
        
        officer_disparity = context.get("officer_disparity_score", 0)
        if officer_disparity > 0.3:
            score -= 15
            factors.append(f"Officer shows disparity pattern: {officer_disparity:.2f}")
            suggestions.append("Review officer-specific patterns")
        
        if not factors:
            factors.append("No historical disparity concerns")
        
        return ComponentScore(
            component=EthicsComponent.HISTORICAL_DISPARITY,
            score=max(0, score),
            max_score=100,
            weight=self.COMPONENT_WEIGHTS[EthicsComponent.HISTORICAL_DISPARITY],
            contributing_factors=factors,
            improvement_suggestions=suggestions,
        )
    
    def _compute_policy_score(self, context: Dict) -> ComponentScore:
        """Compute policy compliance component score."""
        score = 100.0
        factors = []
        suggestions = []
        
        policy_violations = context.get("policy_violations", [])
        for violation in policy_violations[:3]:
            score -= 20
            factors.append(f"Policy violation: {violation}")
            suggestions.append(f"Address {violation}")
        
        sop_compliance = context.get("sop_compliance", True)
        if not sop_compliance:
            score -= 25
            factors.append("SOP non-compliance")
            suggestions.append("Review and follow standard operating procedures")
        
        training_current = context.get("training_current", True)
        if not training_current:
            score -= 10
            factors.append("Required training not current")
            suggestions.append("Complete required training")
        
        if not factors:
            factors.append("Full policy compliance")
        
        return ComponentScore(
            component=EthicsComponent.POLICY_COMPLIANCE,
            score=max(0, score),
            max_score=100,
            weight=self.COMPONENT_WEIGHTS[EthicsComponent.POLICY_COMPLIANCE],
            contributing_factors=factors,
            improvement_suggestions=suggestions,
        )
    
    def _compute_transparency_score(self, context: Dict) -> ComponentScore:
        """Compute transparency component score."""
        score = 100.0
        factors = []
        suggestions = []
        
        explainability = context.get("explainability_score", 1.0)
        if explainability < 0.5:
            score -= 30
            factors.append(f"Low explainability: {explainability:.2f}")
            suggestions.append("Improve AI decision explainability")
        elif explainability < 0.8:
            score -= 15
            factors.append(f"Moderate explainability: {explainability:.2f}")
        
        audit_trail = context.get("audit_trail_complete", True)
        if not audit_trail:
            score -= 25
            factors.append("Incomplete audit trail")
            suggestions.append("Ensure complete audit trail")
        
        body_camera = context.get("body_camera_active", True)
        if not body_camera:
            score -= 20
            factors.append("Body camera not active")
            suggestions.append("Activate body camera")
        
        if not factors:
            factors.append("Full transparency maintained")
        
        return ComponentScore(
            component=EthicsComponent.TRANSPARENCY,
            score=max(0, score),
            max_score=100,
            weight=self.COMPONENT_WEIGHTS[EthicsComponent.TRANSPARENCY],
            contributing_factors=factors,
            improvement_suggestions=suggestions,
        )
    
    def _compute_community_score(self, context: Dict) -> ComponentScore:
        """Compute community impact component score."""
        score = 100.0
        factors = []
        suggestions = []
        
        community_impact = context.get("community_impact_score", 0)
        if community_impact > 0.7:
            score -= 30
            factors.append(f"High community impact: {community_impact:.2f}")
            suggestions.append("Engage community liaison")
        elif community_impact > 0.4:
            score -= 15
            factors.append(f"Moderate community impact: {community_impact:.2f}")
        
        protected_community = context.get("protected_community_affected", False)
        if protected_community:
            score -= 20
            factors.append("Protected community affected")
            suggestions.append("Apply protected community safeguards")
        
        community_trust = context.get("community_trust_score", 1.0)
        if community_trust < 0.5:
            score -= 15
            factors.append(f"Low community trust in area: {community_trust:.2f}")
            suggestions.append("Prioritize community trust building")
        
        if not factors:
            factors.append("Minimal community impact")
        
        return ComponentScore(
            component=EthicsComponent.COMMUNITY_IMPACT,
            score=max(0, score),
            max_score=100,
            weight=self.COMPONENT_WEIGHTS[EthicsComponent.COMMUNITY_IMPACT],
            contributing_factors=factors,
            improvement_suggestions=suggestions,
        )
    
    def _compute_accountability_score(self, context: Dict) -> ComponentScore:
        """Compute accountability component score."""
        score = 100.0
        factors = []
        suggestions = []
        
        supervisor_notified = context.get("supervisor_notified", True)
        if not supervisor_notified:
            score -= 20
            factors.append("Supervisor not notified")
            suggestions.append("Notify supervisor")
        
        documentation_complete = context.get("documentation_complete", True)
        if not documentation_complete:
            score -= 25
            factors.append("Documentation incomplete")
            suggestions.append("Complete all required documentation")
        
        chain_of_command = context.get("chain_of_command_followed", True)
        if not chain_of_command:
            score -= 20
            factors.append("Chain of command not followed")
            suggestions.append("Follow proper chain of command")
        
        if not factors:
            factors.append("Full accountability maintained")
        
        return ComponentScore(
            component=EthicsComponent.ACCOUNTABILITY,
            score=max(0, score),
            max_score=100,
            weight=self.COMPONENT_WEIGHTS[EthicsComponent.ACCOUNTABILITY],
            contributing_factors=factors,
            improvement_suggestions=suggestions,
        )
    
    def _determine_level(self, score: float) -> EthicsLevel:
        """Determine ethics level from score."""
        for level, (min_score, max_score) in self.LEVEL_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return level
        return EthicsLevel.CRITICAL
    
    def _determine_required_action(
        self,
        score: float,
        context: Dict,
    ) -> RequiredAction:
        """Determine required action based on score and context."""
        if context.get("constitutional_violation", False):
            return RequiredAction.BLOCK
        
        if score >= self.ACTION_THRESHOLDS[RequiredAction.ALLOW]:
            return RequiredAction.ALLOW
        elif score >= self.ACTION_THRESHOLDS[RequiredAction.ALLOW_WITH_LOGGING]:
            return RequiredAction.ALLOW_WITH_LOGGING
        elif score >= self.ACTION_THRESHOLDS[RequiredAction.MODIFY]:
            return RequiredAction.MODIFY
        elif score >= self.ACTION_THRESHOLDS[RequiredAction.REVIEW]:
            return RequiredAction.REVIEW
        else:
            return RequiredAction.BLOCK
    
    def _generate_conditions(
        self,
        action: RequiredAction,
        scores: List[ComponentScore],
    ) -> List[str]:
        """Generate conditions for the required action."""
        conditions = []
        
        if action == RequiredAction.ALLOW:
            conditions.append("Proceed with standard logging")
        elif action == RequiredAction.ALLOW_WITH_LOGGING:
            conditions.append("Enhanced logging required")
            conditions.append("Document decision rationale")
        elif action == RequiredAction.MODIFY:
            low_scores = [s for s in scores if s.score < 60]
            for ls in low_scores[:2]:
                conditions.append(f"Address {ls.component.value} concerns before proceeding")
        elif action == RequiredAction.REVIEW:
            conditions.append("Supervisor review required")
            conditions.append("Document review decision")
        elif action == RequiredAction.BLOCK:
            conditions.append("Action blocked pending ethics review")
            conditions.append("Escalate to command staff")
        
        return conditions
    
    def _generate_recommendations(
        self,
        scores: List[ComponentScore],
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        sorted_scores = sorted(scores, key=lambda s: s.score)
        for score in sorted_scores[:3]:
            if score.score < 80:
                recommendations.extend(score.improvement_suggestions[:2])
        
        return list(set(recommendations))[:5]
    
    def _get_policy_references(self, action_type: str) -> List[str]:
        """Get relevant policy references."""
        refs = [
            "Riviera Beach PD Ethics Policy",
            "Florida Law Enforcement Code of Ethics",
            "IACP Law Enforcement Code of Ethics",
        ]
        
        if action_type in ["surveillance", "monitoring"]:
            refs.append("DOJ Surveillance Guidelines")
        
        if action_type in ["use_of_force", "enforcement"]:
            refs.append("DOJ Use of Force Policy Framework")
        
        return refs
    
    def _generate_explanation(
        self,
        score: float,
        level: EthicsLevel,
        scores: List[ComponentScore],
        action: RequiredAction,
    ) -> str:
        """Generate human-readable explanation."""
        explanation = f"Ethics Score: {score:.1f}/100 ({level.value}). "
        
        low_components = [s for s in scores if s.score < 60]
        if low_components:
            names = [s.component.value for s in low_components]
            explanation += f"Concerns in: {', '.join(names)}. "
        
        explanation += f"Required action: {action.value}."
        
        return explanation
    
    def get_assessment_history(
        self,
        level: Optional[EthicsLevel] = None,
        action: Optional[RequiredAction] = None,
        limit: int = 100,
    ) -> List[EthicsAssessment]:
        """Get assessment history with optional filters."""
        results = self._assessment_history
        
        if level:
            results = [r for r in results if r.ethics_level == level]
        if action:
            results = [r for r in results if r.required_action == action]
        
        return results[-limit:]
    
    def get_level_thresholds(self) -> Dict[EthicsLevel, tuple]:
        """Get ethics level thresholds."""
        return self.LEVEL_THRESHOLDS.copy()
    
    def get_component_weights(self) -> Dict[EthicsComponent, float]:
        """Get component weights."""
        return self.COMPONENT_WEIGHTS.copy()


def get_ethics_score_engine() -> EthicsScoreEngine:
    """Get the singleton EthicsScoreEngine instance."""
    return EthicsScoreEngine.get_instance()
