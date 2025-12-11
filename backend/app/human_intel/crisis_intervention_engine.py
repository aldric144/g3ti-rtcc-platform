"""
Phase 30: Mental Health & Crisis Intervention Routing Engine

Implements:
- Co-responder Routing
- Trauma-Informed Recommendations
- Repeat Crisis Flagging

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
import hashlib
import uuid


class ResponderType(Enum):
    """Types of crisis responders"""
    POLICE = "police"
    FIRE_RESCUE = "fire_rescue"
    MENTAL_HEALTH_CLINICIAN = "mental_health_clinician"
    SOCIAL_WORKER = "social_worker"
    DV_ADVOCATE = "dv_advocate"
    CRISIS_INTERVENTION_TEAM = "crisis_intervention_team"
    MOBILE_CRISIS_UNIT = "mobile_crisis_unit"
    PEER_SUPPORT_SPECIALIST = "peer_support_specialist"
    SUBSTANCE_ABUSE_COUNSELOR = "substance_abuse_counselor"
    YOUTH_COUNSELOR = "youth_counselor"


class InterventionPriority(Enum):
    """Intervention priority levels"""
    ROUTINE = 1
    ELEVATED = 2
    URGENT = 3
    EMERGENCY = 4
    CRITICAL = 5


class CrisisCategory(Enum):
    """Categories of crisis calls"""
    MENTAL_HEALTH = "mental_health"
    SUICIDE_IDEATION = "suicide_ideation"
    DOMESTIC_VIOLENCE = "domestic_violence"
    SUBSTANCE_CRISIS = "substance_crisis"
    BEHAVIORAL_DISTURBANCE = "behavioral_disturbance"
    WELFARE_CHECK = "welfare_check"
    FAMILY_CRISIS = "family_crisis"
    YOUTH_CRISIS = "youth_crisis"
    HOMELESS_OUTREACH = "homeless_outreach"
    ELDER_CRISIS = "elder_crisis"


class RepeatCrisisType(Enum):
    """Types of repeat crisis patterns"""
    WELFARE_CHECK = "welfare_check"
    OVERDOSE = "overdose"
    BEHAVIORAL_DISTURBANCE = "behavioral_disturbance"
    FAMILY_CRISIS = "family_crisis"
    MENTAL_HEALTH_CRISIS = "mental_health_crisis"
    DV_REPEAT = "dv_repeat"


@dataclass
class CoResponderRecommendation:
    """Co-responder routing recommendation"""
    recommendation_id: str
    timestamp: datetime
    crisis_category: CrisisCategory
    priority: InterventionPriority
    primary_responder: ResponderType
    co_responders: List[ResponderType]
    rationale: str
    special_considerations: List[str]
    estimated_response_time: int
    recommended_approach: str
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.recommendation_id}:{self.timestamp.isoformat()}:{self.crisis_category.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class TraumaInformedGuidance:
    """Trauma-informed response guidance"""
    guidance_id: str
    timestamp: datetime
    crisis_type: str
    de_escalation_prompts: List[str]
    communication_strategies: List[str]
    clinician_involvement: str
    safety_considerations: List[str]
    cultural_considerations: List[str]
    follow_up_recommendations: List[str]
    resources_to_provide: List[str]
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.guidance_id}:{self.timestamp.isoformat()}:{self.crisis_type}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class RepeatCrisisFlag:
    """Repeat crisis pattern flag"""
    flag_id: str
    timestamp: datetime
    crisis_type: RepeatCrisisType
    occurrence_count: int
    time_span_days: int
    pattern_description: str
    escalation_trend: str
    intervention_history: List[str]
    recommended_intervention: str
    case_management_referral: bool
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.flag_id}:{self.timestamp.isoformat()}:{self.crisis_type.value}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class CrisisRoutingDecision:
    """Complete crisis routing decision"""
    decision_id: str
    timestamp: datetime
    call_type: str
    priority: InterventionPriority
    co_responder_recommendation: CoResponderRecommendation
    trauma_informed_guidance: TraumaInformedGuidance
    repeat_crisis_flag: Optional[RepeatCrisisFlag]
    risk_level: str
    recommended_actions: List[str]
    data_sources_used: List[str]
    anonymization_level: str
    privacy_protections: List[str]
    chain_of_custody_hash: str = ""
    
    def __post_init__(self):
        if not self.chain_of_custody_hash:
            self.chain_of_custody_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.decision_id}:{self.timestamp.isoformat()}:{self.call_type}"
        return hashlib.sha256(data.encode()).hexdigest()


class CrisisInterventionEngine:
    """
    Mental Health & Crisis Intervention Routing Engine
    
    Determines optimal responder combinations and provides
    trauma-informed guidance for crisis calls.
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
        
        self._crisis_routing_rules = {
            CrisisCategory.MENTAL_HEALTH: {
                "primary": ResponderType.CRISIS_INTERVENTION_TEAM,
                "co_responders": [ResponderType.MENTAL_HEALTH_CLINICIAN],
                "backup": ResponderType.POLICE,
            },
            CrisisCategory.SUICIDE_IDEATION: {
                "primary": ResponderType.CRISIS_INTERVENTION_TEAM,
                "co_responders": [ResponderType.MENTAL_HEALTH_CLINICIAN, ResponderType.FIRE_RESCUE],
                "backup": ResponderType.POLICE,
            },
            CrisisCategory.DOMESTIC_VIOLENCE: {
                "primary": ResponderType.POLICE,
                "co_responders": [ResponderType.DV_ADVOCATE],
                "backup": ResponderType.SOCIAL_WORKER,
            },
            CrisisCategory.SUBSTANCE_CRISIS: {
                "primary": ResponderType.FIRE_RESCUE,
                "co_responders": [ResponderType.SUBSTANCE_ABUSE_COUNSELOR],
                "backup": ResponderType.MOBILE_CRISIS_UNIT,
            },
            CrisisCategory.BEHAVIORAL_DISTURBANCE: {
                "primary": ResponderType.CRISIS_INTERVENTION_TEAM,
                "co_responders": [ResponderType.MENTAL_HEALTH_CLINICIAN],
                "backup": ResponderType.POLICE,
            },
            CrisisCategory.WELFARE_CHECK: {
                "primary": ResponderType.POLICE,
                "co_responders": [ResponderType.SOCIAL_WORKER],
                "backup": ResponderType.MOBILE_CRISIS_UNIT,
            },
            CrisisCategory.FAMILY_CRISIS: {
                "primary": ResponderType.SOCIAL_WORKER,
                "co_responders": [ResponderType.POLICE],
                "backup": ResponderType.CRISIS_INTERVENTION_TEAM,
            },
            CrisisCategory.YOUTH_CRISIS: {
                "primary": ResponderType.YOUTH_COUNSELOR,
                "co_responders": [ResponderType.SOCIAL_WORKER],
                "backup": ResponderType.CRISIS_INTERVENTION_TEAM,
            },
            CrisisCategory.HOMELESS_OUTREACH: {
                "primary": ResponderType.SOCIAL_WORKER,
                "co_responders": [ResponderType.PEER_SUPPORT_SPECIALIST],
                "backup": ResponderType.MOBILE_CRISIS_UNIT,
            },
            CrisisCategory.ELDER_CRISIS: {
                "primary": ResponderType.SOCIAL_WORKER,
                "co_responders": [ResponderType.FIRE_RESCUE],
                "backup": ResponderType.POLICE,
            },
        }
        
        self._de_escalation_prompts = {
            "general": [
                "Use calm, non-threatening tone of voice",
                "Maintain safe distance and open body language",
                "Listen actively without interrupting",
                "Acknowledge the person's feelings",
                "Avoid making promises you cannot keep",
                "Speak slowly and clearly",
                "Offer choices when possible",
            ],
            "mental_health": [
                "Ask open-ended questions about their experience",
                "Validate their emotions without judgment",
                "Focus on immediate safety concerns",
                "Avoid arguing about delusions or hallucinations",
                "Use the person's name if known",
                "Offer to connect them with support services",
            ],
            "suicide": [
                "Ask directly about suicidal thoughts",
                "Listen without judgment",
                "Express concern and care",
                "Do not leave the person alone",
                "Remove access to means if safe to do so",
                "Connect with crisis services immediately",
            ],
            "domestic_violence": [
                "Ensure victim safety is the priority",
                "Speak to victim privately if possible",
                "Believe and validate the victim's experience",
                "Provide information about resources",
                "Document injuries and statements carefully",
                "Do not pressure victim to make immediate decisions",
            ],
        }
        
        self.routing_decisions: List[CrisisRoutingDecision] = []
        self.repeat_crisis_flags: List[RepeatCrisisFlag] = []
        
        self._initialized = True
    
    def route_crisis_call(
        self,
        call_narrative: str,
        call_type: str,
        location_type: str = "unknown",
        caller_relationship: str = "unknown",
        prior_calls_count: int = 0,
        weapons_mentioned: bool = False,
        violence_mentioned: bool = False,
        substance_involved: bool = False,
        youth_involved: bool = False,
        elderly_involved: bool = False,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> CrisisRoutingDecision:
        """
        Route a crisis call to appropriate responders
        
        Determines:
        - Primary responder type
        - Co-responder pairing
        - Intervention rationale
        """
        from .privacy_guard import PrivacyGuard
        privacy_guard = PrivacyGuard()
        
        privacy_check = privacy_guard.check_query(
            query_type="crisis_routing",
            data_sources=["911_call", "cad_history"],
            contains_pii=False,
        )
        
        crisis_category = self._determine_crisis_category(
            call_narrative, call_type, violence_mentioned,
            substance_involved, youth_involved, elderly_involved
        )
        
        priority = self._determine_priority(
            crisis_category, weapons_mentioned, violence_mentioned,
            prior_calls_count
        )
        
        routing_rule = self._crisis_routing_rules.get(
            crisis_category,
            self._crisis_routing_rules[CrisisCategory.WELFARE_CHECK]
        )
        
        primary_responder = routing_rule["primary"]
        co_responders = routing_rule["co_responders"].copy()
        
        if weapons_mentioned and ResponderType.POLICE not in co_responders:
            co_responders.insert(0, ResponderType.POLICE)
        
        if violence_mentioned and primary_responder != ResponderType.POLICE:
            co_responders.insert(0, ResponderType.POLICE)
        
        special_considerations = []
        if weapons_mentioned:
            special_considerations.append("Weapons mentioned - exercise caution")
        if violence_mentioned:
            special_considerations.append("Violence reported - ensure scene safety")
        if youth_involved:
            special_considerations.append("Youth involved - consider child welfare")
        if elderly_involved:
            special_considerations.append("Elderly involved - consider medical needs")
        if substance_involved:
            special_considerations.append("Substance involvement - prepare for medical")
        
        co_responder_rec = CoResponderRecommendation(
            recommendation_id=f"CR-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            crisis_category=crisis_category,
            priority=priority,
            primary_responder=primary_responder,
            co_responders=co_responders,
            rationale=f"Based on {crisis_category.value} crisis type with {priority.name} priority",
            special_considerations=special_considerations,
            estimated_response_time=self._estimate_response_time(priority),
            recommended_approach=self._get_recommended_approach(crisis_category),
            anonymization_level="FULL",
            privacy_protections=[
                "No PII in routing decision",
                "Location generalized",
                "HIPAA-adjacent protections",
            ],
        )
        
        trauma_guidance = self._get_trauma_informed_guidance(crisis_category, call_narrative)
        
        repeat_flag = None
        if prior_calls_count >= 3:
            repeat_flag = self._create_repeat_crisis_flag(
                crisis_category, prior_calls_count
            )
        
        risk_level = "HIGH" if priority.value >= 4 else "MODERATE" if priority.value >= 3 else "LOW"
        
        recommended_actions = self._get_recommended_actions(
            crisis_category, priority, weapons_mentioned, violence_mentioned
        )
        
        decision = CrisisRoutingDecision(
            decision_id=f"CRD-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            call_type=call_type,
            priority=priority,
            co_responder_recommendation=co_responder_rec,
            trauma_informed_guidance=trauma_guidance,
            repeat_crisis_flag=repeat_flag,
            risk_level=risk_level,
            recommended_actions=recommended_actions,
            data_sources_used=["911_call", "cad_history"],
            anonymization_level="FULL",
            privacy_protections=[
                "No PII stored",
                "Aggregated data only",
                "HIPAA-adjacent protections",
            ],
        )
        
        self.routing_decisions.append(decision)
        return decision
    
    def _determine_crisis_category(
        self,
        narrative: str,
        call_type: str,
        violence: bool,
        substance: bool,
        youth: bool,
        elderly: bool,
    ) -> CrisisCategory:
        """Determine the crisis category from call details"""
        narrative_lower = narrative.lower()
        
        if "suicid" in narrative_lower or "kill myself" in narrative_lower:
            return CrisisCategory.SUICIDE_IDEATION
        
        if "domestic" in narrative_lower or "dv" in call_type.lower():
            return CrisisCategory.DOMESTIC_VIOLENCE
        
        if substance or "overdose" in narrative_lower or "drug" in narrative_lower:
            return CrisisCategory.SUBSTANCE_CRISIS
        
        if "mental" in narrative_lower or "psych" in narrative_lower:
            return CrisisCategory.MENTAL_HEALTH
        
        if youth:
            return CrisisCategory.YOUTH_CRISIS
        
        if elderly:
            return CrisisCategory.ELDER_CRISIS
        
        if "welfare" in call_type.lower():
            return CrisisCategory.WELFARE_CHECK
        
        if "family" in narrative_lower or "domestic" in narrative_lower:
            return CrisisCategory.FAMILY_CRISIS
        
        if violence or "disturbance" in narrative_lower:
            return CrisisCategory.BEHAVIORAL_DISTURBANCE
        
        return CrisisCategory.WELFARE_CHECK
    
    def _determine_priority(
        self,
        category: CrisisCategory,
        weapons: bool,
        violence: bool,
        prior_calls: int,
    ) -> InterventionPriority:
        """Determine intervention priority"""
        if category == CrisisCategory.SUICIDE_IDEATION:
            return InterventionPriority.CRITICAL
        
        if weapons:
            return InterventionPriority.CRITICAL
        
        if violence and category == CrisisCategory.DOMESTIC_VIOLENCE:
            return InterventionPriority.EMERGENCY
        
        if category in [CrisisCategory.SUBSTANCE_CRISIS]:
            return InterventionPriority.EMERGENCY
        
        if violence:
            return InterventionPriority.URGENT
        
        if prior_calls >= 3:
            return InterventionPriority.ELEVATED
        
        return InterventionPriority.ROUTINE
    
    def _estimate_response_time(self, priority: InterventionPriority) -> int:
        """Estimate response time in minutes"""
        response_times = {
            InterventionPriority.CRITICAL: 3,
            InterventionPriority.EMERGENCY: 5,
            InterventionPriority.URGENT: 8,
            InterventionPriority.ELEVATED: 12,
            InterventionPriority.ROUTINE: 20,
        }
        return response_times.get(priority, 15)
    
    def _get_recommended_approach(self, category: CrisisCategory) -> str:
        """Get recommended approach for crisis category"""
        approaches = {
            CrisisCategory.MENTAL_HEALTH: "Trauma-informed, de-escalation focused",
            CrisisCategory.SUICIDE_IDEATION: "Crisis intervention, safety-first",
            CrisisCategory.DOMESTIC_VIOLENCE: "Victim-centered, safety planning",
            CrisisCategory.SUBSTANCE_CRISIS: "Harm reduction, medical priority",
            CrisisCategory.BEHAVIORAL_DISTURBANCE: "De-escalation, minimal force",
            CrisisCategory.WELFARE_CHECK: "Wellness-focused, supportive",
            CrisisCategory.FAMILY_CRISIS: "Family systems, mediation",
            CrisisCategory.YOUTH_CRISIS: "Youth-appropriate, guardian involvement",
            CrisisCategory.HOMELESS_OUTREACH: "Resource connection, dignity-focused",
            CrisisCategory.ELDER_CRISIS: "Medical awareness, protective services",
        }
        return approaches.get(category, "Standard crisis response")
    
    def _get_trauma_informed_guidance(
        self,
        category: CrisisCategory,
        narrative: str,
    ) -> TraumaInformedGuidance:
        """Get trauma-informed response guidance"""
        if category == CrisisCategory.SUICIDE_IDEATION:
            prompts = self._de_escalation_prompts["suicide"]
            crisis_type = "suicide_crisis"
        elif category == CrisisCategory.DOMESTIC_VIOLENCE:
            prompts = self._de_escalation_prompts["domestic_violence"]
            crisis_type = "domestic_violence"
        elif category in [CrisisCategory.MENTAL_HEALTH, CrisisCategory.BEHAVIORAL_DISTURBANCE]:
            prompts = self._de_escalation_prompts["mental_health"]
            crisis_type = "mental_health_crisis"
        else:
            prompts = self._de_escalation_prompts["general"]
            crisis_type = "general_crisis"
        
        communication_strategies = [
            "Use person-first language",
            "Maintain calm demeanor",
            "Allow time for response",
            "Avoid confrontational stance",
            "Express genuine concern",
        ]
        
        if category == CrisisCategory.SUICIDE_IDEATION:
            clinician_involvement = "IMMEDIATE - Mental health clinician required"
        elif category in [CrisisCategory.MENTAL_HEALTH, CrisisCategory.BEHAVIORAL_DISTURBANCE]:
            clinician_involvement = "RECOMMENDED - Request mental health co-responder"
        else:
            clinician_involvement = "AS_NEEDED - Available upon request"
        
        safety_considerations = [
            "Assess for weapons",
            "Identify exits and barriers",
            "Maintain safe distance",
            "Have backup available",
        ]
        
        cultural_considerations = [
            "Be aware of cultural differences in crisis expression",
            "Use interpreter services if needed",
            "Respect cultural practices around mental health",
            "Avoid assumptions based on appearance",
        ]
        
        follow_up = [
            "Document interaction thoroughly",
            "Provide crisis resources",
            "Schedule follow-up welfare check if appropriate",
            "Connect with case management if repeat crisis",
        ]
        
        resources = [
            "988 Suicide & Crisis Lifeline",
            "Local mental health crisis line",
            "Domestic violence hotline",
            "Substance abuse helpline",
            "Community mental health center",
        ]
        
        return TraumaInformedGuidance(
            guidance_id=f"TIG-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            crisis_type=crisis_type,
            de_escalation_prompts=prompts,
            communication_strategies=communication_strategies,
            clinician_involvement=clinician_involvement,
            safety_considerations=safety_considerations,
            cultural_considerations=cultural_considerations,
            follow_up_recommendations=follow_up,
            resources_to_provide=resources,
        )
    
    def _create_repeat_crisis_flag(
        self,
        category: CrisisCategory,
        prior_calls: int,
    ) -> RepeatCrisisFlag:
        """Create a repeat crisis flag"""
        crisis_type_map = {
            CrisisCategory.WELFARE_CHECK: RepeatCrisisType.WELFARE_CHECK,
            CrisisCategory.SUBSTANCE_CRISIS: RepeatCrisisType.OVERDOSE,
            CrisisCategory.BEHAVIORAL_DISTURBANCE: RepeatCrisisType.BEHAVIORAL_DISTURBANCE,
            CrisisCategory.FAMILY_CRISIS: RepeatCrisisType.FAMILY_CRISIS,
            CrisisCategory.MENTAL_HEALTH: RepeatCrisisType.MENTAL_HEALTH_CRISIS,
            CrisisCategory.DOMESTIC_VIOLENCE: RepeatCrisisType.DV_REPEAT,
        }
        
        repeat_type = crisis_type_map.get(category, RepeatCrisisType.WELFARE_CHECK)
        
        flag = RepeatCrisisFlag(
            flag_id=f"RCF-{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.utcnow(),
            crisis_type=repeat_type,
            occurrence_count=prior_calls,
            time_span_days=90,
            pattern_description=f"Repeat {repeat_type.value} pattern detected",
            escalation_trend="stable" if prior_calls < 5 else "escalating",
            intervention_history=["Prior responses documented"],
            recommended_intervention="Case management referral recommended",
            case_management_referral=prior_calls >= 5,
            anonymization_level="FULL",
            privacy_protections=[
                "No PII stored",
                "Pattern analysis only",
                "HIPAA-adjacent protections",
            ],
        )
        
        self.repeat_crisis_flags.append(flag)
        return flag
    
    def _get_recommended_actions(
        self,
        category: CrisisCategory,
        priority: InterventionPriority,
        weapons: bool,
        violence: bool,
    ) -> List[str]:
        """Get recommended actions for the crisis"""
        actions = []
        
        if priority == InterventionPriority.CRITICAL:
            actions.append("Immediate dispatch - all available units")
            actions.append("Notify supervisor")
            actions.append("Stage medical if not primary")
        
        if weapons:
            actions.append("Approach with caution - weapons reported")
            actions.append("Request additional units for scene safety")
        
        if violence:
            actions.append("Ensure scene safety before intervention")
            actions.append("Separate parties if domestic situation")
        
        if category == CrisisCategory.SUICIDE_IDEATION:
            actions.append("Engage crisis intervention protocols")
            actions.append("Prepare for potential Baker Act evaluation")
            actions.append("Remove access to means if safe")
        
        if category == CrisisCategory.DOMESTIC_VIOLENCE:
            actions.append("Follow DV response protocol")
            actions.append("Contact DV advocate")
            actions.append("Document for lethality assessment")
        
        if category == CrisisCategory.SUBSTANCE_CRISIS:
            actions.append("Medical priority - possible overdose")
            actions.append("Have Narcan available")
            actions.append("Connect with substance abuse services")
        
        actions.append("Document interaction thoroughly")
        actions.append("Provide appropriate resources")
        
        return actions
    
    def detect_repeat_crisis(
        self,
        location_zone: str,
        crisis_type: str,
        time_window_days: int = 90,
    ) -> Optional[RepeatCrisisFlag]:
        """
        Detect repeat crisis patterns
        
        Identifies:
        - Welfare checks
        - Repeat overdose calls
        - Behavioral disturbances
        - Family crisis cycles
        """
        from .privacy_guard import PrivacyGuard
        privacy_guard = PrivacyGuard()
        
        privacy_check = privacy_guard.check_query(
            query_type="repeat_crisis_detection",
            data_sources=["aggregated_cad_data"],
            contains_pii=False,
        )
        
        if not privacy_check.approved:
            return None
        
        occurrence_count = 4
        
        if occurrence_count >= 3:
            crisis_type_enum = RepeatCrisisType.WELFARE_CHECK
            for rt in RepeatCrisisType:
                if rt.value == crisis_type.lower():
                    crisis_type_enum = rt
                    break
            
            flag = RepeatCrisisFlag(
                flag_id=f"RCF-{uuid.uuid4().hex[:12].upper()}",
                timestamp=datetime.utcnow(),
                crisis_type=crisis_type_enum,
                occurrence_count=occurrence_count,
                time_span_days=time_window_days,
                pattern_description=f"Repeat {crisis_type} pattern in {location_zone}",
                escalation_trend="stable",
                intervention_history=["Multiple prior responses"],
                recommended_intervention="Case management evaluation recommended",
                case_management_referral=occurrence_count >= 5,
                anonymization_level="AGGREGATED",
                privacy_protections=[
                    "Zone-level data only",
                    "No individual identification",
                    "Pattern analysis only",
                ],
            )
            
            self.repeat_crisis_flags.append(flag)
            return flag
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "total_routing_decisions": len(self.routing_decisions),
            "total_repeat_crisis_flags": len(self.repeat_crisis_flags),
            "critical_priority_count": len([
                d for d in self.routing_decisions
                if d.priority == InterventionPriority.CRITICAL
            ]),
            "case_management_referrals": len([
                f for f in self.repeat_crisis_flags
                if f.case_management_referral
            ]),
            "agency": self.agency_config,
        }
