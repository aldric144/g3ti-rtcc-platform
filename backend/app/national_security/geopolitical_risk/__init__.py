"""
Geopolitical Risk Module

Provides geopolitical risk assessment capabilities including:
- Global conflict intensity index
- Nation-state threat modeling
- Sanctions & terrorism event ingestion (stub)
- Geo-economic instability scoring
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import uuid
import statistics


class ConflictIntensity(Enum):
    """Intensity levels for conflicts."""
    NONE = "none"
    DISPUTE = "dispute"
    CRISIS = "crisis"
    LIMITED_WAR = "limited_war"
    WAR = "war"
    TOTAL_WAR = "total_war"


class ThreatActorType(Enum):
    """Types of nation-state threat actors."""
    STATE = "state"
    STATE_SPONSORED = "state_sponsored"
    TERRORIST_ORG = "terrorist_organization"
    CRIMINAL_ORG = "criminal_organization"
    HACKTIVIST = "hacktivist"
    INSURGENT = "insurgent"
    MILITIA = "militia"
    PROXY = "proxy_force"
    UNKNOWN = "unknown"


class RegionStability(Enum):
    """Regional stability levels."""
    STABLE = "stable"
    MOSTLY_STABLE = "mostly_stable"
    UNSTABLE = "unstable"
    HIGHLY_UNSTABLE = "highly_unstable"
    CONFLICT_ZONE = "conflict_zone"
    FAILED_STATE = "failed_state"


class ThreatDomain(Enum):
    """Domains of geopolitical threats."""
    MILITARY = "military"
    CYBER = "cyber"
    ECONOMIC = "economic"
    POLITICAL = "political"
    INFORMATION = "information"
    TERRORISM = "terrorism"
    HYBRID = "hybrid"
    NUCLEAR = "nuclear"
    BIOLOGICAL = "biological"
    CHEMICAL = "chemical"


class SanctionType(Enum):
    """Types of sanctions."""
    ECONOMIC = "economic"
    TRADE = "trade"
    FINANCIAL = "financial"
    TRAVEL = "travel"
    ARMS = "arms_embargo"
    DIPLOMATIC = "diplomatic"
    SECTORAL = "sectoral"
    COMPREHENSIVE = "comprehensive"


class EventCategory(Enum):
    """Categories of geopolitical events."""
    CONFLICT = "conflict"
    TERRORISM = "terrorism"
    SANCTIONS = "sanctions"
    DIPLOMATIC = "diplomatic"
    ECONOMIC = "economic"
    MILITARY = "military"
    CYBER_ATTACK = "cyber_attack"
    NATURAL_DISASTER = "natural_disaster"
    POLITICAL_UNREST = "political_unrest"
    HUMANITARIAN = "humanitarian"


@dataclass
class ConflictEvent:
    """Represents a conflict event."""
    event_id: str
    name: str
    description: str
    intensity: ConflictIntensity
    region: str
    countries_involved: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    casualties_estimate: int
    displaced_estimate: int
    threat_domains: List[ThreatDomain]
    is_active: bool
    escalation_risk: float
    international_response: str
    sources: List[str]
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NationStateThreat:
    """Represents a nation-state threat assessment."""
    threat_id: str
    actor_name: str
    actor_type: ThreatActorType
    country_of_origin: str
    target_countries: List[str]
    threat_domains: List[ThreatDomain]
    capability_score: float
    intent_score: float
    overall_threat_score: float
    known_operations: List[str]
    attributed_attacks: List[str]
    sanctions_status: bool
    alliance_affiliations: List[str]
    resources_estimate: str
    last_activity: datetime
    assessment_date: datetime
    confidence_level: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SanctionsEvent:
    """Represents a sanctions event."""
    event_id: str
    sanction_type: SanctionType
    issuing_authority: str
    target_country: Optional[str]
    target_entities: List[str]
    target_individuals: List[str]
    reason: str
    effective_date: datetime
    expiration_date: Optional[datetime]
    is_active: bool
    economic_impact_estimate: float
    compliance_requirements: List[str]
    related_events: List[str]
    sources: List[str]
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeoEconomicRisk:
    """Represents geo-economic risk assessment."""
    risk_id: str
    country: str
    region: str
    stability_level: RegionStability
    economic_risk_score: float
    political_risk_score: float
    security_risk_score: float
    overall_risk_score: float
    gdp_growth_forecast: float
    inflation_rate: float
    currency_stability: float
    trade_dependency_score: float
    debt_to_gdp_ratio: float
    foreign_investment_risk: float
    supply_chain_vulnerability: float
    key_risk_factors: List[str]
    opportunities: List[str]
    assessment_date: datetime
    forecast_horizon_months: int
    confidence_level: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GlobalEvent:
    """Represents a global geopolitical event."""
    event_id: str
    title: str
    description: str
    category: EventCategory
    severity: float
    region: str
    countries_affected: List[str]
    event_date: datetime
    source: str
    source_url: Optional[str]
    verified: bool
    impact_assessment: str
    response_actions: List[str]
    related_events: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class GeopoliticalRiskEngine:
    """
    Geopolitical Risk Assessment Engine.
    
    Provides capabilities for:
    - Global conflict intensity indexing
    - Nation-state threat modeling
    - Sanctions & terrorism event tracking
    - Geo-economic instability scoring
    """

    def __init__(self):
        self.conflict_events: Dict[str, ConflictEvent] = {}
        self.nation_state_threats: Dict[str, NationStateThreat] = {}
        self.sanctions_events: Dict[str, SanctionsEvent] = {}
        self.geo_economic_risks: Dict[str, GeoEconomicRisk] = {}
        self.global_events: Dict[str, GlobalEvent] = {}
        self.country_risk_cache: Dict[str, float] = {}
        self.region_stability_cache: Dict[str, RegionStability] = {}

    def record_conflict_event(
        self,
        name: str,
        description: str,
        intensity: ConflictIntensity,
        region: str,
        countries_involved: List[str],
        start_date: Optional[datetime] = None,
        casualties_estimate: int = 0,
        displaced_estimate: int = 0,
        threat_domains: Optional[List[ThreatDomain]] = None,
        escalation_risk: float = 0.5,
        international_response: str = "monitoring",
        sources: Optional[List[str]] = None,
    ) -> ConflictEvent:
        """Record a conflict event."""
        event_id = f"conf-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        event = ConflictEvent(
            event_id=event_id,
            name=name,
            description=description,
            intensity=intensity,
            region=region,
            countries_involved=countries_involved,
            start_date=start_date or now,
            end_date=None,
            casualties_estimate=casualties_estimate,
            displaced_estimate=displaced_estimate,
            threat_domains=threat_domains or [ThreatDomain.MILITARY],
            is_active=True,
            escalation_risk=escalation_risk,
            international_response=international_response,
            sources=sources or [],
            last_updated=now,
        )
        
        self.conflict_events[event_id] = event
        self._update_region_stability(region)
        
        return event

    def get_conflict_events(
        self,
        region: Optional[str] = None,
        intensity: Optional[ConflictIntensity] = None,
        active_only: bool = False,
        country: Optional[str] = None,
        limit: int = 100,
    ) -> List[ConflictEvent]:
        """Retrieve conflict events with optional filtering."""
        events = list(self.conflict_events.values())
        
        if region:
            events = [e for e in events if e.region.lower() == region.lower()]
        
        if intensity:
            intensity_order = list(ConflictIntensity)
            min_index = intensity_order.index(intensity)
            events = [e for e in events if intensity_order.index(e.intensity) >= min_index]
        
        if active_only:
            events = [e for e in events if e.is_active]
        
        if country:
            events = [e for e in events if country in e.countries_involved]
        
        events.sort(key=lambda x: x.last_updated, reverse=True)
        return events[:limit]

    def calculate_conflict_intensity_index(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Calculate global or regional conflict intensity index."""
        events = self.get_conflict_events(region=region, active_only=True)
        
        if not events:
            return {
                "index": 0,
                "level": "peaceful",
                "active_conflicts": 0,
                "region": region or "global",
            }
        
        intensity_scores = {
            ConflictIntensity.NONE: 0,
            ConflictIntensity.DISPUTE: 10,
            ConflictIntensity.CRISIS: 30,
            ConflictIntensity.LIMITED_WAR: 50,
            ConflictIntensity.WAR: 75,
            ConflictIntensity.TOTAL_WAR: 100,
        }
        
        total_score = sum(intensity_scores.get(e.intensity, 0) for e in events)
        weighted_score = total_score / len(events) if events else 0
        
        escalation_factor = sum(e.escalation_risk for e in events) / len(events)
        final_index = min(100, weighted_score * (1 + escalation_factor * 0.5))
        
        if final_index < 15:
            level = "peaceful"
        elif final_index < 30:
            level = "tense"
        elif final_index < 50:
            level = "unstable"
        elif final_index < 70:
            level = "conflict"
        else:
            level = "crisis"
        
        return {
            "index": round(final_index, 2),
            "level": level,
            "active_conflicts": len(events),
            "region": region or "global",
            "highest_intensity": max(events, key=lambda x: intensity_scores.get(x.intensity, 0)).name if events else None,
            "average_escalation_risk": round(escalation_factor, 2),
        }

    def assess_nation_state_threat(
        self,
        actor_name: str,
        actor_type: ThreatActorType,
        country_of_origin: str,
        target_countries: List[str],
        threat_domains: List[ThreatDomain],
        capability_score: float,
        intent_score: float,
        known_operations: Optional[List[str]] = None,
        attributed_attacks: Optional[List[str]] = None,
        sanctions_status: bool = False,
        alliance_affiliations: Optional[List[str]] = None,
        resources_estimate: str = "unknown",
        confidence_level: float = 0.7,
    ) -> NationStateThreat:
        """Create a nation-state threat assessment."""
        threat_id = f"nst-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        overall_threat_score = self._calculate_threat_score(
            capability_score, intent_score, threat_domains, sanctions_status
        )
        
        threat = NationStateThreat(
            threat_id=threat_id,
            actor_name=actor_name,
            actor_type=actor_type,
            country_of_origin=country_of_origin,
            target_countries=target_countries,
            threat_domains=threat_domains,
            capability_score=capability_score,
            intent_score=intent_score,
            overall_threat_score=overall_threat_score,
            known_operations=known_operations or [],
            attributed_attacks=attributed_attacks or [],
            sanctions_status=sanctions_status,
            alliance_affiliations=alliance_affiliations or [],
            resources_estimate=resources_estimate,
            last_activity=now,
            assessment_date=now,
            confidence_level=confidence_level,
        )
        
        self.nation_state_threats[threat_id] = threat
        return threat

    def _calculate_threat_score(
        self,
        capability: float,
        intent: float,
        domains: List[ThreatDomain],
        sanctioned: bool,
    ) -> float:
        """Calculate overall threat score."""
        base_score = (capability * 0.5 + intent * 0.5)
        
        high_risk_domains = [
            ThreatDomain.NUCLEAR, ThreatDomain.BIOLOGICAL,
            ThreatDomain.CHEMICAL, ThreatDomain.CYBER
        ]
        domain_multiplier = 1.0
        for domain in domains:
            if domain in high_risk_domains:
                domain_multiplier += 0.1
        
        score = base_score * min(1.5, domain_multiplier)
        
        if sanctioned:
            score *= 1.1
        
        return min(100, score)

    def get_nation_state_threats(
        self,
        actor_type: Optional[ThreatActorType] = None,
        target_country: Optional[str] = None,
        threat_domain: Optional[ThreatDomain] = None,
        min_threat_score: float = 0,
        limit: int = 100,
    ) -> List[NationStateThreat]:
        """Retrieve nation-state threats with optional filtering."""
        threats = list(self.nation_state_threats.values())
        
        if actor_type:
            threats = [t for t in threats if t.actor_type == actor_type]
        
        if target_country:
            threats = [t for t in threats if target_country in t.target_countries]
        
        if threat_domain:
            threats = [t for t in threats if threat_domain in t.threat_domains]
        
        threats = [t for t in threats if t.overall_threat_score >= min_threat_score]
        
        threats.sort(key=lambda x: x.overall_threat_score, reverse=True)
        return threats[:limit]

    def record_sanctions_event(
        self,
        sanction_type: SanctionType,
        issuing_authority: str,
        reason: str,
        target_country: Optional[str] = None,
        target_entities: Optional[List[str]] = None,
        target_individuals: Optional[List[str]] = None,
        effective_date: Optional[datetime] = None,
        expiration_date: Optional[datetime] = None,
        economic_impact_estimate: float = 0,
        compliance_requirements: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> SanctionsEvent:
        """Record a sanctions event (stub for external feed ingestion)."""
        event_id = f"sanc-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        event = SanctionsEvent(
            event_id=event_id,
            sanction_type=sanction_type,
            issuing_authority=issuing_authority,
            target_country=target_country,
            target_entities=target_entities or [],
            target_individuals=target_individuals or [],
            reason=reason,
            effective_date=effective_date or now,
            expiration_date=expiration_date,
            is_active=True,
            economic_impact_estimate=economic_impact_estimate,
            compliance_requirements=compliance_requirements or [],
            related_events=[],
            sources=sources or [],
            last_updated=now,
        )
        
        self.sanctions_events[event_id] = event
        return event

    def get_sanctions_events(
        self,
        sanction_type: Optional[SanctionType] = None,
        target_country: Optional[str] = None,
        issuing_authority: Optional[str] = None,
        active_only: bool = False,
        limit: int = 100,
    ) -> List[SanctionsEvent]:
        """Retrieve sanctions events with optional filtering."""
        events = list(self.sanctions_events.values())
        
        if sanction_type:
            events = [e for e in events if e.sanction_type == sanction_type]
        
        if target_country:
            events = [e for e in events if e.target_country == target_country]
        
        if issuing_authority:
            events = [e for e in events if e.issuing_authority == issuing_authority]
        
        if active_only:
            events = [e for e in events if e.is_active]
        
        events.sort(key=lambda x: x.effective_date, reverse=True)
        return events[:limit]

    def assess_geo_economic_risk(
        self,
        country: str,
        region: str,
        economic_risk_score: float,
        political_risk_score: float,
        security_risk_score: float,
        gdp_growth_forecast: float = 0,
        inflation_rate: float = 0,
        currency_stability: float = 50,
        trade_dependency_score: float = 50,
        debt_to_gdp_ratio: float = 0,
        foreign_investment_risk: float = 50,
        supply_chain_vulnerability: float = 50,
        key_risk_factors: Optional[List[str]] = None,
        opportunities: Optional[List[str]] = None,
        forecast_horizon_months: int = 12,
        confidence_level: float = 0.7,
    ) -> GeoEconomicRisk:
        """Create a geo-economic risk assessment."""
        risk_id = f"geo-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        
        overall_risk_score = (
            economic_risk_score * 0.35 +
            political_risk_score * 0.35 +
            security_risk_score * 0.30
        )
        
        stability_level = self._calculate_stability_level(overall_risk_score)
        
        risk = GeoEconomicRisk(
            risk_id=risk_id,
            country=country,
            region=region,
            stability_level=stability_level,
            economic_risk_score=economic_risk_score,
            political_risk_score=political_risk_score,
            security_risk_score=security_risk_score,
            overall_risk_score=overall_risk_score,
            gdp_growth_forecast=gdp_growth_forecast,
            inflation_rate=inflation_rate,
            currency_stability=currency_stability,
            trade_dependency_score=trade_dependency_score,
            debt_to_gdp_ratio=debt_to_gdp_ratio,
            foreign_investment_risk=foreign_investment_risk,
            supply_chain_vulnerability=supply_chain_vulnerability,
            key_risk_factors=key_risk_factors or [],
            opportunities=opportunities or [],
            assessment_date=now,
            forecast_horizon_months=forecast_horizon_months,
            confidence_level=confidence_level,
        )
        
        self.geo_economic_risks[risk_id] = risk
        self.country_risk_cache[country] = overall_risk_score
        
        return risk

    def _calculate_stability_level(self, risk_score: float) -> RegionStability:
        """Calculate stability level from risk score."""
        if risk_score < 20:
            return RegionStability.STABLE
        elif risk_score < 35:
            return RegionStability.MOSTLY_STABLE
        elif risk_score < 55:
            return RegionStability.UNSTABLE
        elif risk_score < 75:
            return RegionStability.HIGHLY_UNSTABLE
        elif risk_score < 90:
            return RegionStability.CONFLICT_ZONE
        else:
            return RegionStability.FAILED_STATE

    def _update_region_stability(self, region: str) -> None:
        """Update regional stability based on conflicts."""
        conflicts = self.get_conflict_events(region=region, active_only=True)
        
        if not conflicts:
            self.region_stability_cache[region] = RegionStability.STABLE
            return
        
        intensity_index = self.calculate_conflict_intensity_index(region)
        index_value = intensity_index["index"]
        
        self.region_stability_cache[region] = self._calculate_stability_level(index_value)

    def get_geo_economic_risks(
        self,
        country: Optional[str] = None,
        region: Optional[str] = None,
        stability_level: Optional[RegionStability] = None,
        min_risk_score: float = 0,
        limit: int = 100,
    ) -> List[GeoEconomicRisk]:
        """Retrieve geo-economic risks with optional filtering."""
        risks = list(self.geo_economic_risks.values())
        
        if country:
            risks = [r for r in risks if r.country.lower() == country.lower()]
        
        if region:
            risks = [r for r in risks if r.region.lower() == region.lower()]
        
        if stability_level:
            stability_order = list(RegionStability)
            min_index = stability_order.index(stability_level)
            risks = [r for r in risks if stability_order.index(r.stability_level) >= min_index]
        
        risks = [r for r in risks if r.overall_risk_score >= min_risk_score]
        
        risks.sort(key=lambda x: x.overall_risk_score, reverse=True)
        return risks[:limit]

    def record_global_event(
        self,
        title: str,
        description: str,
        category: EventCategory,
        severity: float,
        region: str,
        countries_affected: List[str],
        source: str,
        source_url: Optional[str] = None,
        verified: bool = False,
        impact_assessment: str = "",
        response_actions: Optional[List[str]] = None,
    ) -> GlobalEvent:
        """Record a global geopolitical event."""
        event_id = f"evt-{uuid.uuid4().hex[:12]}"
        
        event = GlobalEvent(
            event_id=event_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            region=region,
            countries_affected=countries_affected,
            event_date=datetime.utcnow(),
            source=source,
            source_url=source_url,
            verified=verified,
            impact_assessment=impact_assessment,
            response_actions=response_actions or [],
            related_events=[],
        )
        
        self.global_events[event_id] = event
        return event

    def get_global_events(
        self,
        category: Optional[EventCategory] = None,
        region: Optional[str] = None,
        min_severity: float = 0,
        verified_only: bool = False,
        limit: int = 100,
    ) -> List[GlobalEvent]:
        """Retrieve global events with optional filtering."""
        events = list(self.global_events.values())
        
        if category:
            events = [e for e in events if e.category == category]
        
        if region:
            events = [e for e in events if e.region.lower() == region.lower()]
        
        events = [e for e in events if e.severity >= min_severity]
        
        if verified_only:
            events = [e for e in events if e.verified]
        
        events.sort(key=lambda x: x.event_date, reverse=True)
        return events[:limit]

    def get_country_risk_score(self, country: str) -> float:
        """Get cached risk score for a country."""
        return self.country_risk_cache.get(country, 50.0)

    def get_region_stability(self, region: str) -> RegionStability:
        """Get cached stability level for a region."""
        return self.region_stability_cache.get(region, RegionStability.MOSTLY_STABLE)

    def get_global_risk_summary(self) -> Dict[str, Any]:
        """Get a summary of global geopolitical risks."""
        active_conflicts = self.get_conflict_events(active_only=True)
        active_sanctions = self.get_sanctions_events(active_only=True)
        
        global_intensity = self.calculate_conflict_intensity_index()
        
        high_risk_countries = [
            country for country, score in self.country_risk_cache.items()
            if score >= 65
        ]
        
        return {
            "global_conflict_index": global_intensity,
            "active_conflicts_count": len(active_conflicts),
            "active_sanctions_count": len(active_sanctions),
            "nation_state_threats_count": len(self.nation_state_threats),
            "high_risk_countries": high_risk_countries,
            "total_events_tracked": len(self.global_events),
            "regions_monitored": len(self.region_stability_cache),
            "countries_assessed": len(self.country_risk_cache),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get geopolitical risk metrics."""
        conflicts = list(self.conflict_events.values())
        threats = list(self.nation_state_threats.values())
        
        intensity_distribution = {}
        for intensity in ConflictIntensity:
            intensity_distribution[intensity.value] = len([c for c in conflicts if c.intensity == intensity])
        
        threat_type_distribution = {}
        for actor_type in ThreatActorType:
            threat_type_distribution[actor_type.value] = len([t for t in threats if t.actor_type == actor_type])
        
        stability_distribution = {}
        for stability in RegionStability:
            stability_distribution[stability.value] = len([
                r for r in self.geo_economic_risks.values() if r.stability_level == stability
            ])
        
        return {
            "total_conflicts": len(conflicts),
            "active_conflicts": len([c for c in conflicts if c.is_active]),
            "total_nation_state_threats": len(threats),
            "total_sanctions_events": len(self.sanctions_events),
            "active_sanctions": len([s for s in self.sanctions_events.values() if s.is_active]),
            "total_geo_economic_assessments": len(self.geo_economic_risks),
            "total_global_events": len(self.global_events),
            "intensity_distribution": intensity_distribution,
            "threat_type_distribution": threat_type_distribution,
            "stability_distribution": stability_distribution,
            "average_threat_score": statistics.mean([t.overall_threat_score for t in threats]) if threats else 0,
        }
