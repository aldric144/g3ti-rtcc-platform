"""
Information Warfare / Disinformation Engine

Provides comprehensive disinformation detection including:
- Rumor & Panic Model
- Police Impersonation Detection
- Election Interference Monitor
- Crisis Narrative Manipulation Monitor

Agency: Riviera Beach Police Department (ORI: FL0500400)
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
import uuid
import re


class DisinfoType(Enum):
    """Types of disinformation"""
    VIRAL_FALSE_POST = "VIRAL_FALSE_POST"
    COORDINATED_PANIC = "COORDINATED_PANIC"
    EMERGENCY_HOAX = "EMERGENCY_HOAX"
    FAKE_POLICE_PAGE = "FAKE_POLICE_PAGE"
    FAKE_ALERT = "FAKE_ALERT"
    AI_GENERATED_MESSAGE = "AI_GENERATED_MESSAGE"
    BOT_NETWORK = "BOT_NETWORK"
    IDENTITY_SPOOFING = "IDENTITY_SPOOFING"
    MINORITY_TARGETED = "MINORITY_TARGETED"
    FAKE_CRIME_SPIKE = "FAKE_CRIME_SPIKE"
    FALSE_OIS_CLAIM = "FALSE_OIS_CLAIM"
    ANTI_POLICE_WAVE = "ANTI_POLICE_WAVE"
    ELECTION_INTERFERENCE = "ELECTION_INTERFERENCE"
    CRISIS_MANIPULATION = "CRISIS_MANIPULATION"


class DisinfoSeverity(Enum):
    """Disinformation severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class DisinfoSource(Enum):
    """Source platforms for disinformation"""
    FACEBOOK = "FACEBOOK"
    TWITTER_X = "TWITTER_X"
    INSTAGRAM = "INSTAGRAM"
    TIKTOK = "TIKTOK"
    YOUTUBE = "YOUTUBE"
    TELEGRAM = "TELEGRAM"
    WHATSAPP = "WHATSAPP"
    NEXTDOOR = "NEXTDOOR"
    REDDIT = "REDDIT"
    LOCAL_NEWS_COMMENTS = "LOCAL_NEWS_COMMENTS"
    EMAIL = "EMAIL"
    SMS = "SMS"
    WEBSITE = "WEBSITE"
    UNKNOWN = "UNKNOWN"


class CampaignType(Enum):
    """Types of disinformation campaigns"""
    ORGANIC = "ORGANIC"
    COORDINATED_INAUTHENTIC = "COORDINATED_INAUTHENTIC"
    STATE_SPONSORED = "STATE_SPONSORED"
    DOMESTIC_POLITICAL = "DOMESTIC_POLITICAL"
    CRIMINAL = "CRIMINAL"
    UNKNOWN = "UNKNOWN"


class TargetAudience(Enum):
    """Target audiences for disinformation"""
    GENERAL_PUBLIC = "GENERAL_PUBLIC"
    MINORITY_COMMUNITY = "MINORITY_COMMUNITY"
    ELDERLY = "ELDERLY"
    YOUTH = "YOUTH"
    VOTERS = "VOTERS"
    LAW_ENFORCEMENT = "LAW_ENFORCEMENT"
    LOCAL_GOVERNMENT = "LOCAL_GOVERNMENT"
    BUSINESS_COMMUNITY = "BUSINESS_COMMUNITY"


@dataclass
class RumorAlert:
    """Rumor and panic detection alert"""
    alert_id: str
    timestamp: datetime
    disinfo_type: DisinfoType
    severity: DisinfoSeverity
    source_platform: DisinfoSource
    content_summary: str
    viral_velocity: float
    share_count: int
    reach_estimate: int
    geographic_spread: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    key_accounts: List[str] = field(default_factory=list)
    panic_indicators: List[str] = field(default_factory=list)
    fact_check_status: Optional[str] = None
    recommended_action: str = ""
    chain_of_custody_hash: str = ""


@dataclass
class ImpersonationAlert:
    """Police impersonation detection alert"""
    alert_id: str
    timestamp: datetime
    disinfo_type: DisinfoType
    severity: DisinfoSeverity
    source_platform: DisinfoSource
    impersonated_entity: str
    fake_account_url: Optional[str] = None
    fake_page_name: Optional[str] = None
    follower_count: int = 0
    post_count: int = 0
    creation_date: Optional[datetime] = None
    ai_generated_content: bool = False
    official_branding_misuse: bool = False
    scam_indicators: List[str] = field(default_factory=list)
    victims_identified: int = 0
    recommended_action: str = ""
    chain_of_custody_hash: str = ""


@dataclass
class ElectionThreat:
    """Election interference detection"""
    threat_id: str
    timestamp: datetime
    disinfo_type: DisinfoType
    severity: DisinfoSeverity
    campaign_type: CampaignType
    target_audience: TargetAudience
    source_platforms: List[DisinfoSource] = field(default_factory=list)
    bot_network_detected: bool = False
    bot_account_count: int = 0
    coordinated_accounts: List[str] = field(default_factory=list)
    narratives: List[str] = field(default_factory=list)
    voter_suppression_indicators: List[str] = field(default_factory=list)
    foreign_indicators: List[str] = field(default_factory=list)
    reach_estimate: int = 0
    recommended_action: str = ""
    chain_of_custody_hash: str = ""


@dataclass
class CrisisManipulation:
    """Crisis narrative manipulation detection"""
    manipulation_id: str
    timestamp: datetime
    disinfo_type: DisinfoType
    severity: DisinfoSeverity
    crisis_type: str
    narrative_description: str
    source_platforms: List[DisinfoSource] = field(default_factory=list)
    amplification_accounts: List[str] = field(default_factory=list)
    false_claims: List[str] = field(default_factory=list)
    evidence_of_coordination: bool = False
    media_manipulation: bool = False
    public_safety_impact: str = ""
    community_tension_score: float = 0.0
    recommended_action: str = ""
    chain_of_custody_hash: str = ""


@dataclass
class DisinfoAssessment:
    """Overall disinformation assessment"""
    assessment_id: str
    timestamp: datetime
    overall_threat_level: DisinfoSeverity
    rumor_alerts: List[RumorAlert] = field(default_factory=list)
    impersonation_alerts: List[ImpersonationAlert] = field(default_factory=list)
    election_threats: List[ElectionThreat] = field(default_factory=list)
    crisis_manipulations: List[CrisisManipulation] = field(default_factory=list)
    active_campaigns: int = 0
    bot_networks_detected: int = 0
    community_tension_index: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    chain_of_custody_hash: str = ""


class InfoWarfareEngine:
    """
    Information Warfare / Disinformation Engine
    
    Provides comprehensive disinformation detection for Riviera Beach PD
    including rumor detection, police impersonation, election interference,
    and crisis narrative manipulation monitoring.
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
            "county": "Palm Beach",
            "city": "Riviera Beach",
            "zip": "33404",
        }
        
        self.rumor_alerts: List[RumorAlert] = []
        self.impersonation_alerts: List[ImpersonationAlert] = []
        self.election_threats: List[ElectionThreat] = []
        self.crisis_manipulations: List[CrisisManipulation] = []
        
        self._panic_keywords = [
            "active shooter", "bomb threat", "evacuation",
            "lockdown", "shelter in place", "emergency",
            "terrorist", "attack", "explosion", "shooting",
            "hostage", "riot", "looting", "martial law",
        ]
        
        self._hoax_indicators = [
            "share before deleted", "they don't want you to know",
            "mainstream media won't report", "breaking news",
            "confirmed by sources", "insider information",
            "wake up people", "spread the word",
        ]
        
        self._police_impersonation_indicators = [
            "official police", "police department",
            "law enforcement", "sheriff", "deputy",
            "officer", "badge", "warrant", "arrest",
            "fine", "payment", "gift card",
        ]
        
        self._bot_indicators = [
            "high_post_frequency",
            "repetitive_content",
            "coordinated_timing",
            "new_account",
            "no_profile_picture",
            "generic_username",
            "follows_many_follows_few",
            "identical_messages",
        ]
        
        self._election_keywords = [
            "vote", "election", "ballot", "polling",
            "candidate", "democrat", "republican",
            "voter fraud", "rigged", "stolen",
            "mail-in", "absentee", "registration",
        ]
        
        self._minority_targeting_indicators = [
            "specific_neighborhood_targeting",
            "language_specific_content",
            "cultural_references",
            "community_leader_impersonation",
            "historical_grievance_exploitation",
        ]
        
        self._official_rbpd_accounts: Set[str] = {
            "@RivieraBeachPD",
            "RivieraBeachPolice",
            "rivierabeachpd.gov",
        }
        
        self._tracked_narratives: Dict[str, Dict[str, Any]] = {}
    
    def _generate_chain_of_custody_hash(self, data: Dict[str, Any]) -> str:
        """Generate chain of custody hash for evidence integrity"""
        data_str = str(sorted(data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def detect_rumor_panic(
        self,
        content: str,
        source_platform: DisinfoSource,
        share_count: int = 0,
        reach_estimate: int = 0,
        hashtags: Optional[List[str]] = None,
        geographic_locations: Optional[List[str]] = None,
    ) -> Optional[RumorAlert]:
        """
        Rumor & Panic Model
        
        Detects:
        - Viral false posts
        - Coordinated panic campaigns
        - Emergency hoaxes
        """
        disinfo_type = None
        severity = DisinfoSeverity.LOW
        panic_indicators = []
        
        content_lower = content.lower()
        
        panic_count = sum(1 for kw in self._panic_keywords if kw in content_lower)
        if panic_count >= 3:
            disinfo_type = DisinfoType.COORDINATED_PANIC
            severity = DisinfoSeverity.HIGH
            panic_indicators.append(f"Multiple panic keywords detected: {panic_count}")
        elif panic_count >= 1:
            disinfo_type = DisinfoType.VIRAL_FALSE_POST
            severity = DisinfoSeverity.MEDIUM
        
        hoax_count = sum(1 for ind in self._hoax_indicators if ind in content_lower)
        if hoax_count >= 2:
            disinfo_type = DisinfoType.EMERGENCY_HOAX
            severity = max(severity, DisinfoSeverity.HIGH)
            panic_indicators.append(f"Hoax indicators detected: {hoax_count}")
        
        viral_velocity = 0.0
        if share_count > 10000:
            viral_velocity = 1.0
            severity = DisinfoSeverity.CRITICAL
        elif share_count > 5000:
            viral_velocity = 0.8
            severity = max(severity, DisinfoSeverity.HIGH)
        elif share_count > 1000:
            viral_velocity = 0.5
            severity = max(severity, DisinfoSeverity.MEDIUM)
        elif share_count > 100:
            viral_velocity = 0.2
        
        if "riviera beach" in content_lower or "rbpd" in content_lower:
            severity = max(severity, DisinfoSeverity.HIGH)
            panic_indicators.append("Local reference to Riviera Beach")
        
        if not disinfo_type:
            return None
        
        alert = RumorAlert(
            alert_id=f"rumor-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            disinfo_type=disinfo_type,
            severity=severity,
            source_platform=source_platform,
            content_summary=content[:500] if len(content) > 500 else content,
            viral_velocity=viral_velocity,
            share_count=share_count,
            reach_estimate=reach_estimate,
            geographic_spread=geographic_locations or [],
            hashtags=hashtags or [],
            panic_indicators=panic_indicators,
            recommended_action=self._get_rumor_recommendation(disinfo_type, severity),
        )
        
        alert.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "alert_id": alert.alert_id,
            "timestamp": alert.timestamp.isoformat(),
            "disinfo_type": disinfo_type.value,
            "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
        })
        
        self.rumor_alerts.append(alert)
        return alert
    
    def _get_rumor_recommendation(self, disinfo_type: DisinfoType, severity: DisinfoSeverity) -> str:
        """Get recommended action for rumor/panic"""
        if severity == DisinfoSeverity.CRITICAL or severity == DisinfoSeverity.EMERGENCY:
            return (
                "CRITICAL: Issue official statement immediately. "
                "Coordinate with PIO. Contact platform for content removal. "
                "Monitor for public safety impacts."
            )
        
        recommendations = {
            DisinfoType.COORDINATED_PANIC: 
                "Issue calming official statement. Monitor spread. "
                "Coordinate with local media for accurate reporting.",
            DisinfoType.EMERGENCY_HOAX:
                "Verify with dispatch. Issue official clarification. "
                "Report to platform for removal.",
            DisinfoType.VIRAL_FALSE_POST:
                "Monitor spread. Prepare official response if needed. "
                "Document for future reference.",
        }
        
        return recommendations.get(disinfo_type, "Monitor and document.")
    
    def detect_police_impersonation(
        self,
        account_name: str,
        account_url: Optional[str],
        source_platform: DisinfoSource,
        content_samples: List[str],
        follower_count: int = 0,
        creation_date: Optional[datetime] = None,
    ) -> Optional[ImpersonationAlert]:
        """
        Police Impersonation Detection
        
        Identifies:
        - Fake RBPD pages
        - Fake alerts
        - AI-generated messages
        """
        if account_name in self._official_rbpd_accounts:
            return None
        
        disinfo_type = None
        severity = DisinfoSeverity.LOW
        ai_generated = False
        official_branding = False
        scam_indicators = []
        
        account_lower = account_name.lower()
        if any(term in account_lower for term in ["riviera", "rbpd", "police", "pd"]):
            disinfo_type = DisinfoType.FAKE_POLICE_PAGE
            severity = DisinfoSeverity.HIGH
            official_branding = True
            scam_indicators.append("Uses official-sounding name")
        
        all_content = " ".join(content_samples).lower()
        
        impersonation_count = sum(
            1 for ind in self._police_impersonation_indicators
            if ind in all_content
        )
        
        if impersonation_count >= 3:
            disinfo_type = DisinfoType.FAKE_POLICE_PAGE
            severity = max(severity, DisinfoSeverity.HIGH)
            scam_indicators.append(f"Multiple police-related terms: {impersonation_count}")
        
        scam_terms = ["gift card", "wire transfer", "bitcoin", "payment", "fine", "warrant"]
        scam_count = sum(1 for term in scam_terms if term in all_content)
        if scam_count >= 2:
            severity = DisinfoSeverity.CRITICAL
            scam_indicators.append("Financial scam indicators detected")
        
        ai_indicators = [
            "unusual_formatting",
            "generic_responses",
            "inconsistent_tone",
            "perfect_grammar_with_odd_phrasing",
        ]
        
        if any(ind in all_content for ind in ["dear citizen", "official notice", "immediate action required"]):
            ai_generated = True
            disinfo_type = DisinfoType.AI_GENERATED_MESSAGE
            scam_indicators.append("AI-generated content patterns")
        
        if creation_date:
            account_age = (datetime.utcnow() - creation_date).days
            if account_age < 30:
                scam_indicators.append(f"New account: {account_age} days old")
                severity = max(severity, DisinfoSeverity.MEDIUM)
        
        if not disinfo_type:
            return None
        
        alert = ImpersonationAlert(
            alert_id=f"imperson-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            disinfo_type=disinfo_type,
            severity=severity,
            source_platform=source_platform,
            impersonated_entity="Riviera Beach Police Department",
            fake_account_url=account_url,
            fake_page_name=account_name,
            follower_count=follower_count,
            post_count=len(content_samples),
            creation_date=creation_date,
            ai_generated_content=ai_generated,
            official_branding_misuse=official_branding,
            scam_indicators=scam_indicators,
            recommended_action=self._get_impersonation_recommendation(severity, scam_indicators),
        )
        
        alert.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "alert_id": alert.alert_id,
            "timestamp": alert.timestamp.isoformat(),
            "account_name": account_name,
            "platform": source_platform.value,
        })
        
        self.impersonation_alerts.append(alert)
        return alert
    
    def _get_impersonation_recommendation(
        self,
        severity: DisinfoSeverity,
        scam_indicators: List[str],
    ) -> str:
        """Get recommended action for impersonation"""
        if "Financial scam indicators detected" in scam_indicators:
            return (
                "CRITICAL: Report to platform immediately for removal. "
                "Issue public warning. Coordinate with fraud unit. "
                "Document for potential criminal investigation."
            )
        
        if severity == DisinfoSeverity.CRITICAL:
            return (
                "Report to platform for immediate removal. "
                "Issue official warning to public. "
                "Preserve evidence for investigation."
            )
        
        return (
            "Report to platform. Monitor for victim reports. "
            "Consider public awareness post from official accounts."
        )
    
    def detect_election_interference(
        self,
        content_samples: List[str],
        source_platforms: List[DisinfoSource],
        account_metadata: List[Dict[str, Any]],
        target_demographics: Optional[List[str]] = None,
    ) -> Optional[ElectionThreat]:
        """
        Election Interference Monitor
        
        Scans for:
        - Bot networks
        - Identity spoofing
        - Misinformation targeted at minority communities
        """
        disinfo_type = None
        severity = DisinfoSeverity.LOW
        campaign_type = CampaignType.UNKNOWN
        target_audience = TargetAudience.GENERAL_PUBLIC
        bot_detected = False
        bot_count = 0
        coordinated_accounts = []
        narratives = []
        voter_suppression = []
        foreign_indicators = []
        
        all_content = " ".join(content_samples).lower()
        
        election_count = sum(1 for kw in self._election_keywords if kw in all_content)
        if election_count < 2:
            return None
        
        disinfo_type = DisinfoType.ELECTION_INTERFERENCE
        severity = DisinfoSeverity.MEDIUM
        
        for account in account_metadata:
            bot_score = 0
            for indicator in self._bot_indicators:
                if account.get(indicator, False):
                    bot_score += 1
            
            if bot_score >= 3:
                bot_detected = True
                bot_count += 1
                coordinated_accounts.append(account.get("username", "unknown"))
        
        if bot_count >= 5:
            disinfo_type = DisinfoType.BOT_NETWORK
            severity = DisinfoSeverity.HIGH
            campaign_type = CampaignType.COORDINATED_INAUTHENTIC
        
        if target_demographics:
            for demo in target_demographics:
                if demo.lower() in ["african american", "hispanic", "haitian", "minority"]:
                    disinfo_type = DisinfoType.MINORITY_TARGETED
                    target_audience = TargetAudience.MINORITY_COMMUNITY
                    severity = DisinfoSeverity.CRITICAL
                    break
        
        suppression_terms = [
            "don't vote", "stay home", "rigged anyway",
            "wrong date", "wrong location", "id required",
        ]
        for term in suppression_terms:
            if term in all_content:
                voter_suppression.append(term)
                severity = DisinfoSeverity.CRITICAL
        
        foreign_terms = ["foreign language patterns", "unusual posting times", "vpn indicators"]
        
        if "riviera beach" in all_content or "palm beach" in all_content:
            narratives.append("Local election targeting detected")
            severity = max(severity, DisinfoSeverity.HIGH)
        
        reach = sum(acc.get("followers", 0) for acc in account_metadata)
        
        threat = ElectionThreat(
            threat_id=f"election-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            disinfo_type=disinfo_type,
            severity=severity,
            campaign_type=campaign_type,
            target_audience=target_audience,
            source_platforms=source_platforms,
            bot_network_detected=bot_detected,
            bot_account_count=bot_count,
            coordinated_accounts=coordinated_accounts,
            narratives=narratives,
            voter_suppression_indicators=voter_suppression,
            foreign_indicators=foreign_indicators,
            reach_estimate=reach,
            recommended_action=self._get_election_recommendation(severity, voter_suppression),
        )
        
        threat.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "threat_id": threat.threat_id,
            "timestamp": threat.timestamp.isoformat(),
            "disinfo_type": disinfo_type.value,
            "bot_count": bot_count,
        })
        
        self.election_threats.append(threat)
        return threat
    
    def _get_election_recommendation(
        self,
        severity: DisinfoSeverity,
        voter_suppression: List[str],
    ) -> str:
        """Get recommended action for election interference"""
        if voter_suppression:
            return (
                "CRITICAL: Voter suppression detected. "
                "Report to FBI, CISA, and Supervisor of Elections immediately. "
                "Issue public clarification with correct voting information. "
                "Preserve all evidence."
            )
        
        if severity == DisinfoSeverity.CRITICAL:
            return (
                "Report to FBI Cyber Division and CISA. "
                "Coordinate with Supervisor of Elections. "
                "Monitor for escalation. Preserve evidence."
            )
        
        return (
            "Monitor campaign spread. Document accounts involved. "
            "Report to platforms. Consider public awareness messaging."
        )
    
    def detect_crisis_manipulation(
        self,
        crisis_type: str,
        content_samples: List[str],
        source_platforms: List[DisinfoSource],
        amplification_accounts: Optional[List[str]] = None,
    ) -> Optional[CrisisManipulation]:
        """
        Crisis Narrative Manipulation Monitor
        
        Tracks:
        - Fake crime spikes
        - False officer-involved shooting claims
        - Anti-police disinformation waves
        """
        disinfo_type = None
        severity = DisinfoSeverity.LOW
        false_claims = []
        coordination_evidence = False
        media_manipulation = False
        tension_score = 0.0
        
        all_content = " ".join(content_samples).lower()
        
        crime_spike_terms = [
            "crime wave", "surge in crime", "out of control",
            "unsafe", "dangerous", "crime spike", "murder rate",
        ]
        crime_count = sum(1 for term in crime_spike_terms if term in all_content)
        if crime_count >= 2:
            disinfo_type = DisinfoType.FAKE_CRIME_SPIKE
            severity = DisinfoSeverity.MEDIUM
            false_claims.append("Unverified crime spike claims")
            tension_score += 0.3
        
        ois_terms = [
            "officer shot", "police shooting", "killed by police",
            "police brutality", "excessive force", "unarmed",
        ]
        ois_count = sum(1 for term in ois_terms if term in all_content)
        if ois_count >= 2:
            disinfo_type = DisinfoType.FALSE_OIS_CLAIM
            severity = DisinfoSeverity.HIGH
            false_claims.append("Unverified officer-involved shooting claims")
            tension_score += 0.5
        
        anti_police_terms = [
            "acab", "defund", "corrupt cops", "dirty cops",
            "police state", "oppression", "tyranny",
        ]
        anti_count = sum(1 for term in anti_police_terms if term in all_content)
        if anti_count >= 3:
            disinfo_type = DisinfoType.ANTI_POLICE_WAVE
            severity = max(severity, DisinfoSeverity.HIGH)
            false_claims.append("Coordinated anti-police messaging")
            tension_score += 0.4
        
        if amplification_accounts and len(amplification_accounts) >= 5:
            coordination_evidence = True
            severity = max(severity, DisinfoSeverity.HIGH)
        
        if "riviera beach" in all_content or "rbpd" in all_content:
            severity = max(severity, DisinfoSeverity.HIGH)
            tension_score += 0.2
        
        tension_score = min(tension_score, 1.0)
        
        if not disinfo_type:
            return None
        
        public_safety_impact = "LOW"
        if tension_score >= 0.7:
            public_safety_impact = "HIGH"
            severity = DisinfoSeverity.CRITICAL
        elif tension_score >= 0.4:
            public_safety_impact = "MEDIUM"
        
        manipulation = CrisisManipulation(
            manipulation_id=f"crisis-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            disinfo_type=disinfo_type,
            severity=severity,
            crisis_type=crisis_type,
            narrative_description=f"Detected {disinfo_type.value} related to {crisis_type}",
            source_platforms=source_platforms,
            amplification_accounts=amplification_accounts or [],
            false_claims=false_claims,
            evidence_of_coordination=coordination_evidence,
            media_manipulation=media_manipulation,
            public_safety_impact=public_safety_impact,
            community_tension_score=tension_score,
            recommended_action=self._get_crisis_recommendation(disinfo_type, severity, tension_score),
        )
        
        manipulation.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "manipulation_id": manipulation.manipulation_id,
            "timestamp": manipulation.timestamp.isoformat(),
            "crisis_type": crisis_type,
            "tension_score": tension_score,
        })
        
        self.crisis_manipulations.append(manipulation)
        return manipulation
    
    def _get_crisis_recommendation(
        self,
        disinfo_type: DisinfoType,
        severity: DisinfoSeverity,
        tension_score: float,
    ) -> str:
        """Get recommended action for crisis manipulation"""
        if tension_score >= 0.7:
            return (
                "CRITICAL: High community tension detected. "
                "Coordinate with command staff and PIO immediately. "
                "Consider community outreach. Monitor for civil unrest indicators. "
                "Prepare official statement with verified facts."
            )
        
        recommendations = {
            DisinfoType.FAKE_CRIME_SPIKE:
                "Issue official crime statistics. Coordinate with local media. "
                "Consider community meeting to address concerns.",
            DisinfoType.FALSE_OIS_CLAIM:
                "PRIORITY: Verify with internal affairs. Prepare official statement. "
                "Coordinate with PIO and legal. Preserve all evidence.",
            DisinfoType.ANTI_POLICE_WAVE:
                "Monitor for escalation. Document coordinated accounts. "
                "Consider community engagement response. Brief command staff.",
        }
        
        base = recommendations.get(disinfo_type, "Monitor and document.")
        
        if severity == DisinfoSeverity.CRITICAL:
            return f"CRITICAL: {base}"
        
        return base
    
    def register_official_account(self, account_identifier: str) -> bool:
        """Register an official RBPD account"""
        self._official_rbpd_accounts.add(account_identifier)
        return True
    
    def track_narrative(
        self,
        narrative_id: str,
        description: str,
        keywords: List[str],
    ) -> bool:
        """Track a specific narrative for monitoring"""
        self._tracked_narratives[narrative_id] = {
            "description": description,
            "keywords": keywords,
            "created": datetime.utcnow(),
            "mentions": 0,
        }
        return True
    
    def get_disinfo_assessment(self) -> DisinfoAssessment:
        """Get overall disinformation assessment"""
        now = datetime.utcnow()
        recent_window = now - timedelta(hours=24)
        
        recent_rumors = [a for a in self.rumor_alerts if a.timestamp > recent_window]
        recent_impersonations = [a for a in self.impersonation_alerts if a.timestamp > recent_window]
        recent_election = [t for t in self.election_threats if t.timestamp > recent_window]
        recent_crisis = [m for m in self.crisis_manipulations if m.timestamp > recent_window]
        
        all_severities = (
            [a.severity for a in recent_rumors] +
            [a.severity for a in recent_impersonations] +
            [t.severity for t in recent_election] +
            [m.severity for m in recent_crisis]
        )
        
        if DisinfoSeverity.EMERGENCY in all_severities:
            overall_level = DisinfoSeverity.EMERGENCY
        elif DisinfoSeverity.CRITICAL in all_severities:
            overall_level = DisinfoSeverity.CRITICAL
        elif DisinfoSeverity.HIGH in all_severities:
            overall_level = DisinfoSeverity.HIGH
        elif DisinfoSeverity.MEDIUM in all_severities:
            overall_level = DisinfoSeverity.MEDIUM
        else:
            overall_level = DisinfoSeverity.LOW
        
        bot_networks = sum(1 for t in recent_election if t.bot_network_detected)
        
        tension_scores = [m.community_tension_score for m in recent_crisis]
        avg_tension = sum(tension_scores) / len(tension_scores) if tension_scores else 0.0
        
        recommendations = []
        if recent_impersonations:
            recommendations.append("Active police impersonation detected. Issue public warning.")
        if recent_election:
            recommendations.append("Election-related disinformation detected. Coordinate with authorities.")
        if avg_tension >= 0.5:
            recommendations.append("Elevated community tension. Consider proactive engagement.")
        
        assessment = DisinfoAssessment(
            assessment_id=f"disinfo-{uuid.uuid4().hex[:12]}",
            timestamp=now,
            overall_threat_level=overall_level,
            rumor_alerts=recent_rumors,
            impersonation_alerts=recent_impersonations,
            election_threats=recent_election,
            crisis_manipulations=recent_crisis,
            active_campaigns=len(recent_rumors) + len(recent_election),
            bot_networks_detected=bot_networks,
            community_tension_index=avg_tension,
            recommendations=recommendations,
        )
        
        assessment.chain_of_custody_hash = self._generate_chain_of_custody_hash({
            "assessment_id": assessment.assessment_id,
            "timestamp": assessment.timestamp.isoformat(),
            "overall_threat_level": assessment.overall_threat_level.value,
        })
        
        return assessment
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get disinformation statistics"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        return {
            "total_rumor_alerts": len(self.rumor_alerts),
            "total_impersonation_alerts": len(self.impersonation_alerts),
            "total_election_threats": len(self.election_threats),
            "total_crisis_manipulations": len(self.crisis_manipulations),
            "rumor_alerts_24h": len([a for a in self.rumor_alerts if a.timestamp > last_24h]),
            "impersonation_alerts_24h": len([a for a in self.impersonation_alerts if a.timestamp > last_24h]),
            "election_threats_24h": len([t for t in self.election_threats if t.timestamp > last_24h]),
            "crisis_manipulations_24h": len([m for m in self.crisis_manipulations if m.timestamp > last_24h]),
            "critical_alerts_7d": len([
                a for a in self.rumor_alerts + self.impersonation_alerts
                if a.timestamp > last_7d and a.severity in [DisinfoSeverity.CRITICAL, DisinfoSeverity.EMERGENCY]
            ]),
            "bot_networks_7d": len([
                t for t in self.election_threats
                if t.timestamp > last_7d and t.bot_network_detected
            ]),
            "official_accounts_registered": len(self._official_rbpd_accounts),
            "tracked_narratives": len(self._tracked_narratives),
        }
