"""
Phase 32: Global Risk Fusion Engine

Multi-domain risk scoring and fusion for global situation awareness.

Risk Domains:
- Climate risk (extreme weather, sea level rise, drought)
- Geopolitical risk (conflicts, sanctions, regime changes)
- Cyber risk (attacks, vulnerabilities, infrastructure threats)
- Supply chain risk (disruptions, dependencies, bottlenecks)
- Health risk (pandemics, outbreaks, healthcare capacity)
- Conflict risk (armed conflicts, terrorism, civil unrest)
- Economic risk (market volatility, debt crises, trade wars)
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class RiskDomain(Enum):
    CLIMATE = "climate"
    GEOPOLITICAL = "geopolitical"
    CYBER = "cyber"
    SUPPLY_CHAIN = "supply_chain"
    HEALTH = "health"
    CONFLICT = "conflict"
    ECONOMIC = "economic"
    INFRASTRUCTURE = "infrastructure"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"


class RiskLevel(Enum):
    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5


class TrendDirection(Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DETERIORATING = "deteriorating"
    RAPIDLY_DETERIORATING = "rapidly_deteriorating"


@dataclass
class DomainRiskScore:
    score_id: str
    domain: RiskDomain
    region: str
    country: Optional[str]
    score: float
    level: RiskLevel
    trend: TrendDirection
    contributing_factors: list[str]
    mitigation_recommendations: list[str]
    confidence: float
    timestamp: datetime
    valid_until: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.score_id}:{self.domain.value}:{self.region}:{self.score}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class FusedRiskAssessment:
    assessment_id: str
    region: str
    country: Optional[str]
    overall_risk_score: float
    overall_risk_level: RiskLevel
    domain_scores: dict[str, float]
    primary_risk_domain: RiskDomain
    secondary_risk_domains: list[RiskDomain]
    risk_interactions: list[str]
    forecast_7_day: float
    forecast_30_day: float
    recommended_actions: list[str]
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.assessment_id}:{self.region}:{self.overall_risk_score}:{self.timestamp.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class RiskAlert:
    alert_id: str
    domain: RiskDomain
    region: str
    country: Optional[str]
    title: str
    description: str
    risk_level: RiskLevel
    trigger_factors: list[str]
    affected_sectors: list[str]
    recommended_response: str
    expires_at: datetime
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.alert_id}:{self.domain.value}:{self.title}:{self.timestamp.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


class RiskFusionEngine:
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

        self.domain_scores: list[DomainRiskScore] = []
        self.fused_assessments: list[FusedRiskAssessment] = []
        self.risk_alerts: list[RiskAlert] = []

        self.domain_weights = {
            RiskDomain.CONFLICT: 0.20,
            RiskDomain.GEOPOLITICAL: 0.15,
            RiskDomain.CYBER: 0.15,
            RiskDomain.CLIMATE: 0.10,
            RiskDomain.HEALTH: 0.10,
            RiskDomain.SUPPLY_CHAIN: 0.10,
            RiskDomain.ECONOMIC: 0.10,
            RiskDomain.INFRASTRUCTURE: 0.05,
            RiskDomain.SOCIAL: 0.03,
            RiskDomain.ENVIRONMENTAL: 0.02,
        }

        self.risk_interactions = {
            (RiskDomain.CONFLICT, RiskDomain.SUPPLY_CHAIN): 1.3,
            (RiskDomain.CLIMATE, RiskDomain.HEALTH): 1.2,
            (RiskDomain.CYBER, RiskDomain.INFRASTRUCTURE): 1.4,
            (RiskDomain.GEOPOLITICAL, RiskDomain.ECONOMIC): 1.25,
            (RiskDomain.CONFLICT, RiskDomain.HEALTH): 1.2,
            (RiskDomain.CLIMATE, RiskDomain.SUPPLY_CHAIN): 1.15,
        }

        self.regions = [
            "North America", "South America", "Western Europe", "Eastern Europe",
            "Middle East", "North Africa", "Sub-Saharan Africa", "Central Asia",
            "South Asia", "East Asia", "Southeast Asia", "Oceania",
        ]

        self.high_risk_regions = {
            "Middle East": {RiskDomain.CONFLICT: 0.3, RiskDomain.GEOPOLITICAL: 0.2},
            "Eastern Europe": {RiskDomain.CONFLICT: 0.25, RiskDomain.CYBER: 0.15},
            "Sub-Saharan Africa": {RiskDomain.HEALTH: 0.2, RiskDomain.CLIMATE: 0.15},
            "South Asia": {RiskDomain.CLIMATE: 0.2, RiskDomain.SOCIAL: 0.1},
        }

        self.statistics = {
            "total_domain_scores": 0,
            "total_fused_assessments": 0,
            "total_alerts": 0,
            "scores_by_domain": {d.value: 0 for d in RiskDomain},
            "alerts_by_level": {l.value: 0 for l in RiskLevel},
        }

    def calculate_domain_risk(
        self,
        domain: RiskDomain,
        region: str,
        country: str = None,
        indicators: dict = None,
    ) -> DomainRiskScore:
        indicators = indicators or {}

        base_score = 30.0

        if region in self.high_risk_regions:
            regional_boost = self.high_risk_regions[region].get(domain, 0)
            base_score += regional_boost * 100

        indicator_adjustments = {
            RiskDomain.CONFLICT: self._calculate_conflict_score(indicators),
            RiskDomain.GEOPOLITICAL: self._calculate_geopolitical_score(indicators),
            RiskDomain.CYBER: self._calculate_cyber_score(indicators),
            RiskDomain.CLIMATE: self._calculate_climate_score(indicators),
            RiskDomain.HEALTH: self._calculate_health_score(indicators),
            RiskDomain.SUPPLY_CHAIN: self._calculate_supply_chain_score(indicators),
            RiskDomain.ECONOMIC: self._calculate_economic_score(indicators),
            RiskDomain.INFRASTRUCTURE: self._calculate_infrastructure_score(indicators),
            RiskDomain.SOCIAL: self._calculate_social_score(indicators),
            RiskDomain.ENVIRONMENTAL: self._calculate_environmental_score(indicators),
        }

        adjustment = indicator_adjustments.get(domain, 0)
        final_score = min(100.0, max(0.0, base_score + adjustment))

        level = self._score_to_level(final_score)
        trend = self._calculate_trend(domain, region)

        contributing_factors = self._identify_contributing_factors(domain, indicators)
        recommendations = self._generate_mitigation_recommendations(domain, level)

        score = DomainRiskScore(
            score_id=f"DRS-{uuid.uuid4().hex[:8].upper()}",
            domain=domain,
            region=region,
            country=country,
            score=final_score,
            level=level,
            trend=trend,
            contributing_factors=contributing_factors,
            mitigation_recommendations=recommendations,
            confidence=0.75 + (len(indicators) * 0.05),
            timestamp=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(hours=24),
        )

        self.domain_scores.append(score)
        self.statistics["total_domain_scores"] += 1
        self.statistics["scores_by_domain"][domain.value] += 1

        if level.value >= RiskLevel.HIGH.value:
            self._create_risk_alert(score)

        return score

    def _calculate_conflict_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("active_conflict", False):
            score += 40
        if indicators.get("terrorism_incidents", 0) > 5:
            score += 20
        if indicators.get("civil_unrest", False):
            score += 15
        if indicators.get("military_buildup", False):
            score += 10
        return score

    def _calculate_geopolitical_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("sanctions_imposed", False):
            score += 25
        if indicators.get("diplomatic_tensions", False):
            score += 15
        if indicators.get("regime_instability", False):
            score += 20
        if indicators.get("border_disputes", False):
            score += 10
        return score

    def _calculate_cyber_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("critical_infrastructure_attack", False):
            score += 35
        if indicators.get("ransomware_campaigns", 0) > 3:
            score += 20
        if indicators.get("state_sponsored_activity", False):
            score += 25
        if indicators.get("zero_day_exploits", 0) > 0:
            score += 15
        return score

    def _calculate_climate_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("extreme_weather_events", 0) > 2:
            score += 25
        if indicators.get("drought_conditions", False):
            score += 20
        if indicators.get("flooding_risk", False):
            score += 15
        if indicators.get("sea_level_threat", False):
            score += 10
        return score

    def _calculate_health_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("pandemic_outbreak", False):
            score += 40
        if indicators.get("disease_outbreak", False):
            score += 25
        if indicators.get("healthcare_capacity_strain", False):
            score += 15
        if indicators.get("vaccine_shortage", False):
            score += 10
        return score

    def _calculate_supply_chain_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("port_disruption", False):
            score += 25
        if indicators.get("shipping_delays", 0) > 7:
            score += 20
        if indicators.get("critical_shortage", False):
            score += 30
        if indicators.get("trade_restrictions", False):
            score += 15
        return score

    def _calculate_economic_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("currency_crisis", False):
            score += 30
        if indicators.get("debt_default_risk", False):
            score += 25
        if indicators.get("market_volatility", 0) > 30:
            score += 20
        if indicators.get("inflation_rate", 0) > 10:
            score += 15
        return score

    def _calculate_infrastructure_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("power_grid_failure", False):
            score += 30
        if indicators.get("communication_outage", False):
            score += 25
        if indicators.get("transportation_disruption", False):
            score += 20
        return score

    def _calculate_social_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("mass_protests", False):
            score += 25
        if indicators.get("refugee_crisis", False):
            score += 30
        if indicators.get("food_insecurity", False):
            score += 20
        return score

    def _calculate_environmental_score(self, indicators: dict) -> float:
        score = 0.0
        if indicators.get("pollution_crisis", False):
            score += 20
        if indicators.get("deforestation", False):
            score += 15
        if indicators.get("water_scarcity", False):
            score += 25
        return score

    def _score_to_level(self, score: float) -> RiskLevel:
        if score < 20:
            return RiskLevel.MINIMAL
        elif score < 40:
            return RiskLevel.LOW
        elif score < 60:
            return RiskLevel.MODERATE
        elif score < 80:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _calculate_trend(self, domain: RiskDomain, region: str) -> TrendDirection:
        recent_scores = [
            s for s in self.domain_scores
            if s.domain == domain and s.region == region
        ][-5:]

        if len(recent_scores) < 2:
            return TrendDirection.STABLE

        avg_old = sum(s.score for s in recent_scores[:-1]) / len(recent_scores[:-1])
        latest = recent_scores[-1].score

        diff = latest - avg_old
        if diff > 10:
            return TrendDirection.RAPIDLY_DETERIORATING
        elif diff > 3:
            return TrendDirection.DETERIORATING
        elif diff < -3:
            return TrendDirection.IMPROVING
        else:
            return TrendDirection.STABLE

    def _identify_contributing_factors(self, domain: RiskDomain, indicators: dict) -> list[str]:
        factors = []
        factor_map = {
            RiskDomain.CONFLICT: ["active_conflict", "terrorism_incidents", "civil_unrest"],
            RiskDomain.CYBER: ["critical_infrastructure_attack", "ransomware_campaigns", "state_sponsored_activity"],
            RiskDomain.CLIMATE: ["extreme_weather_events", "drought_conditions", "flooding_risk"],
            RiskDomain.HEALTH: ["pandemic_outbreak", "disease_outbreak", "healthcare_capacity_strain"],
            RiskDomain.SUPPLY_CHAIN: ["port_disruption", "shipping_delays", "critical_shortage"],
        }

        for factor in factor_map.get(domain, []):
            if indicators.get(factor):
                factors.append(factor.replace("_", " ").title())

        return factors or ["Baseline regional risk"]

    def _generate_mitigation_recommendations(self, domain: RiskDomain, level: RiskLevel) -> list[str]:
        recommendations = {
            RiskDomain.CONFLICT: [
                "Monitor conflict escalation indicators",
                "Review evacuation procedures",
                "Assess personnel safety protocols",
            ],
            RiskDomain.CYBER: [
                "Enhance network monitoring",
                "Update incident response plans",
                "Review backup and recovery procedures",
            ],
            RiskDomain.CLIMATE: [
                "Monitor weather forecasts",
                "Review disaster preparedness plans",
                "Assess infrastructure resilience",
            ],
            RiskDomain.SUPPLY_CHAIN: [
                "Identify alternative suppliers",
                "Increase safety stock levels",
                "Review logistics contingencies",
            ],
        }

        base_recs = recommendations.get(domain, ["Continue monitoring"])

        if level.value >= RiskLevel.HIGH.value:
            base_recs.insert(0, "URGENT: Activate contingency plans")

        return base_recs

    def _create_risk_alert(self, score: DomainRiskScore):
        alert = RiskAlert(
            alert_id=f"RA-{uuid.uuid4().hex[:8].upper()}",
            domain=score.domain,
            region=score.region,
            country=score.country,
            title=f"Elevated {score.domain.value.title()} Risk in {score.region}",
            description=f"Risk level: {score.level.name}. Contributing factors: {', '.join(score.contributing_factors)}",
            risk_level=score.level,
            trigger_factors=score.contributing_factors,
            affected_sectors=self._get_affected_sectors(score.domain),
            recommended_response=score.mitigation_recommendations[0] if score.mitigation_recommendations else "Monitor situation",
            expires_at=score.valid_until,
            timestamp=datetime.utcnow(),
        )

        self.risk_alerts.append(alert)
        self.statistics["total_alerts"] += 1
        self.statistics["alerts_by_level"][score.level.value] += 1

    def _get_affected_sectors(self, domain: RiskDomain) -> list[str]:
        sector_map = {
            RiskDomain.CONFLICT: ["Defense", "Energy", "Transportation", "Finance"],
            RiskDomain.CYBER: ["Technology", "Finance", "Healthcare", "Energy"],
            RiskDomain.CLIMATE: ["Agriculture", "Energy", "Transportation", "Insurance"],
            RiskDomain.HEALTH: ["Healthcare", "Pharmaceuticals", "Travel", "Retail"],
            RiskDomain.SUPPLY_CHAIN: ["Manufacturing", "Retail", "Technology", "Automotive"],
            RiskDomain.ECONOMIC: ["Finance", "Real Estate", "Retail", "Manufacturing"],
        }
        return sector_map.get(domain, ["General"])

    def create_fused_assessment(
        self,
        region: str,
        country: str = None,
    ) -> FusedRiskAssessment:
        domain_scores = {}
        for domain in RiskDomain:
            score = self.calculate_domain_risk(domain, region, country)
            domain_scores[domain.value] = score.score

        weighted_sum = sum(
            domain_scores[d.value] * self.domain_weights[d]
            for d in RiskDomain
        )

        interaction_multiplier = 1.0
        interactions = []
        for (d1, d2), multiplier in self.risk_interactions.items():
            if domain_scores[d1.value] > 60 and domain_scores[d2.value] > 60:
                interaction_multiplier = max(interaction_multiplier, multiplier)
                interactions.append(f"{d1.value} + {d2.value} interaction")

        overall_score = min(100.0, weighted_sum * interaction_multiplier)
        overall_level = self._score_to_level(overall_score)

        sorted_domains = sorted(
            [(d, domain_scores[d.value]) for d in RiskDomain],
            key=lambda x: x[1],
            reverse=True
        )
        primary_domain = sorted_domains[0][0]
        secondary_domains = [d for d, s in sorted_domains[1:4] if s > 40]

        forecast_7 = overall_score * 1.05
        forecast_30 = overall_score * 1.1

        recommendations = self._generate_fused_recommendations(
            overall_level, primary_domain, secondary_domains
        )

        assessment = FusedRiskAssessment(
            assessment_id=f"FRA-{uuid.uuid4().hex[:8].upper()}",
            region=region,
            country=country,
            overall_risk_score=overall_score,
            overall_risk_level=overall_level,
            domain_scores=domain_scores,
            primary_risk_domain=primary_domain,
            secondary_risk_domains=secondary_domains,
            risk_interactions=interactions,
            forecast_7_day=min(100.0, forecast_7),
            forecast_30_day=min(100.0, forecast_30),
            recommended_actions=recommendations,
            timestamp=datetime.utcnow(),
        )

        self.fused_assessments.append(assessment)
        self.statistics["total_fused_assessments"] += 1
        return assessment

    def _generate_fused_recommendations(
        self,
        level: RiskLevel,
        primary: RiskDomain,
        secondary: list[RiskDomain],
    ) -> list[str]:
        recommendations = []

        if level.value >= RiskLevel.CRITICAL.value:
            recommendations.append("CRITICAL: Activate emergency response protocols")
        elif level.value >= RiskLevel.HIGH.value:
            recommendations.append("HIGH PRIORITY: Review and update contingency plans")

        recommendations.append(f"Focus monitoring on {primary.value} indicators")

        for domain in secondary[:2]:
            recommendations.append(f"Secondary focus: {domain.value} risk mitigation")

        return recommendations

    def get_regional_risk_summary(self) -> dict:
        summary = {}
        for region in self.regions:
            recent = [
                a for a in self.fused_assessments
                if a.region == region
            ]
            if recent:
                latest = max(recent, key=lambda x: x.timestamp)
                summary[region] = {
                    "overall_score": latest.overall_risk_score,
                    "level": latest.overall_risk_level.name,
                    "primary_risk": latest.primary_risk_domain.value,
                }
            else:
                summary[region] = {
                    "overall_score": 30.0,
                    "level": "LOW",
                    "primary_risk": "unknown",
                }
        return summary

    def get_active_alerts(self) -> list[RiskAlert]:
        now = datetime.utcnow()
        return [a for a in self.risk_alerts if a.expires_at > now]

    def get_statistics(self) -> dict:
        return self.statistics.copy()
