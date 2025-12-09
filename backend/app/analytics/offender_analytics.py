"""
Repeat Offender Analytics for G3TI RTCC-UIP.

This module provides repeat offender analysis capabilities including:
- Recidivism pattern detection
- Offender network analysis
- Risk scoring and prediction
- Timeline visualization data
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..db.elasticsearch import ElasticsearchManager
from ..db.neo4j import Neo4jManager
from ..db.redis import RedisManager

logger = logging.getLogger(__name__)


class OffenderProfile(BaseModel):
    """Offender profile summary."""

    model_config = ConfigDict(from_attributes=True)

    offender_id: str = Field(description="Offender identifier")
    jurisdiction: str = Field(description="Primary jurisdiction")

    # Incident history
    total_incidents: int = Field(default=0, description="Total incident count")
    first_incident_date: datetime | None = Field(default=None, description="First incident")
    last_incident_date: datetime | None = Field(default=None, description="Most recent incident")

    # Crime breakdown
    crime_categories: dict[str, int] = Field(
        default_factory=dict, description="Incidents by category"
    )
    severity_breakdown: dict[str, int] = Field(
        default_factory=dict, description="Incidents by severity"
    )

    # Risk assessment
    risk_score: float = Field(ge=0, le=100, description="Risk score (0-100)")
    risk_level: str = Field(description="Risk level: low, medium, high, critical")
    risk_factors: list[str] = Field(default_factory=list, description="Risk factors")

    # Patterns
    is_repeat_offender: bool = Field(description="Whether classified as repeat offender")
    recidivism_rate: float = Field(ge=0, le=1, description="Recidivism rate")
    escalation_trend: str = Field(description="Trend: escalating, stable, de-escalating")

    # Network
    known_associates: int = Field(default=0, description="Number of known associates")
    gang_affiliated: bool = Field(default=False, description="Gang affiliation flag")


class RecidivismAnalysis(BaseModel):
    """Recidivism analysis result."""

    model_config = ConfigDict(from_attributes=True)

    jurisdiction: str = Field(description="Jurisdiction analyzed")
    analysis_period_start: datetime = Field(description="Analysis start date")
    analysis_period_end: datetime = Field(description="Analysis end date")

    # Overall metrics
    total_offenders: int = Field(description="Total unique offenders")
    repeat_offenders: int = Field(description="Repeat offender count")
    repeat_offender_rate: float = Field(description="Repeat offender percentage")

    # Recidivism metrics
    recidivism_rate_30_day: float = Field(description="30-day recidivism rate")
    recidivism_rate_90_day: float = Field(description="90-day recidivism rate")
    recidivism_rate_1_year: float = Field(description="1-year recidivism rate")

    # Risk distribution
    risk_distribution: dict[str, int] = Field(
        description="Offenders by risk level"
    )

    # Category analysis
    high_recidivism_categories: list[dict[str, Any]] = Field(
        default_factory=list, description="Categories with highest recidivism"
    )

    # Trends
    recidivism_trend: str = Field(description="Trend: increasing, stable, decreasing")
    trend_percent_change: float = Field(description="Trend percent change")


class OffenderTimeline(BaseModel):
    """Offender incident timeline."""

    model_config = ConfigDict(from_attributes=True)

    offender_id: str = Field(description="Offender ID")
    incidents: list[dict[str, Any]] = Field(description="Incident timeline")
    total_incidents: int = Field(description="Total incidents")

    # Patterns
    average_days_between: float | None = Field(
        default=None, description="Average days between incidents"
    )
    shortest_gap: int | None = Field(default=None, description="Shortest gap in days")
    longest_gap: int | None = Field(default=None, description="Longest gap in days")

    # Escalation
    severity_progression: list[str] = Field(
        default_factory=list, description="Severity over time"
    )
    is_escalating: bool = Field(default=False, description="Whether escalating")


class NetworkAnalysis(BaseModel):
    """Offender network analysis."""

    model_config = ConfigDict(from_attributes=True)

    offender_id: str = Field(description="Central offender ID")
    network_size: int = Field(description="Total network size")

    # Associates
    direct_associates: list[dict[str, Any]] = Field(
        default_factory=list, description="Direct associates"
    )
    indirect_associates: int = Field(default=0, description="Indirect associate count")

    # Network metrics
    centrality_score: float = Field(ge=0, le=1, description="Network centrality")
    influence_score: float = Field(ge=0, le=1, description="Influence in network")

    # Gang analysis
    gang_connections: list[str] = Field(
        default_factory=list, description="Connected gang identifiers"
    )
    is_network_leader: bool = Field(default=False, description="Whether network leader")


class RepeatOffenderAnalytics:
    """
    Engine for repeat offender analytics.

    Provides comprehensive offender analysis including:
    - Recidivism pattern detection
    - Risk scoring and prediction
    - Network analysis
    - Timeline visualization
    """

    # Risk score weights
    RISK_WEIGHTS = {
        "incident_count": 0.25,
        "severity_history": 0.25,
        "recency": 0.20,
        "escalation": 0.15,
        "network": 0.15,
    }

    # Risk level thresholds
    RISK_THRESHOLDS = {
        "critical": 80,
        "high": 60,
        "medium": 40,
        "low": 0,
    }

    # Repeat offender threshold
    REPEAT_OFFENDER_THRESHOLD = 3

    # Cache settings
    CACHE_PREFIX = "analytics:offender:"
    CACHE_TTL = 1800  # 30 minutes

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
    ):
        """
        Initialize the Repeat Offender Analytics engine.

        Args:
            neo4j: Neo4j manager for network analysis
            es: Elasticsearch manager for incident data
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        logger.info("RepeatOffenderAnalytics initialized")

    async def get_offender_profile(
        self,
        offender_id: str,
        jurisdiction: str,
    ) -> OffenderProfile:
        """
        Get comprehensive offender profile.

        Args:
            offender_id: Offender identifier
            jurisdiction: Jurisdiction code

        Returns:
            Offender profile
        """
        # Check cache
        cache_key = f"{self.CACHE_PREFIX}profile:{jurisdiction}:{offender_id}"
        cached = await self._get_cached(cache_key)
        if cached:
            return OffenderProfile(**cached)

        # Fetch incident history
        incidents = await self._fetch_offender_incidents(offender_id, jurisdiction)

        if not incidents:
            return self._empty_profile(offender_id, jurisdiction)

        # Calculate metrics
        total_incidents = len(incidents)
        first_incident = min(i["timestamp"] for i in incidents)
        last_incident = max(i["timestamp"] for i in incidents)

        # Crime breakdown
        crime_categories: dict[str, int] = {}
        severity_breakdown: dict[str, int] = {}

        for incident in incidents:
            cat = incident.get("crime_category", "other")
            crime_categories[cat] = crime_categories.get(cat, 0) + 1

            sev = incident.get("severity", "medium")
            severity_breakdown[sev] = severity_breakdown.get(sev, 0) + 1

        # Calculate risk score
        risk_score, risk_factors = await self._calculate_risk_score(
            offender_id, jurisdiction, incidents
        )
        risk_level = self._get_risk_level(risk_score)

        # Calculate recidivism rate
        recidivism_rate = self._calculate_recidivism_rate(incidents)

        # Determine escalation trend
        escalation_trend = self._determine_escalation_trend(incidents)

        # Get network info
        network_info = await self._get_network_summary(offender_id, jurisdiction)

        profile = OffenderProfile(
            offender_id=offender_id,
            jurisdiction=jurisdiction,
            total_incidents=total_incidents,
            first_incident_date=first_incident,
            last_incident_date=last_incident,
            crime_categories=crime_categories,
            severity_breakdown=severity_breakdown,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            risk_factors=risk_factors,
            is_repeat_offender=total_incidents >= self.REPEAT_OFFENDER_THRESHOLD,
            recidivism_rate=round(recidivism_rate, 4),
            escalation_trend=escalation_trend,
            known_associates=network_info.get("associate_count", 0),
            gang_affiliated=network_info.get("gang_affiliated", False),
        )

        # Cache result
        await self._set_cached(cache_key, profile.model_dump())

        return profile

    async def analyze_recidivism(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        crime_category: str | None = None,
    ) -> RecidivismAnalysis:
        """
        Analyze recidivism patterns for a jurisdiction.

        Args:
            jurisdiction: Jurisdiction code
            start_date: Analysis start date
            end_date: Analysis end date
            crime_category: Optional crime category filter

        Returns:
            Recidivism analysis result
        """
        # Fetch all offenders in period
        offender_data = await self._fetch_offender_summary(
            jurisdiction, start_date, end_date, crime_category
        )

        total_offenders = len(offender_data)
        repeat_offenders = sum(
            1 for o in offender_data.values()
            if o["incident_count"] >= self.REPEAT_OFFENDER_THRESHOLD
        )

        repeat_rate = repeat_offenders / total_offenders if total_offenders > 0 else 0

        # Calculate recidivism rates at different windows
        recidivism_30 = await self._calculate_window_recidivism(
            jurisdiction, start_date, end_date, 30
        )
        recidivism_90 = await self._calculate_window_recidivism(
            jurisdiction, start_date, end_date, 90
        )
        recidivism_365 = await self._calculate_window_recidivism(
            jurisdiction, start_date, end_date, 365
        )

        # Risk distribution
        risk_distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for offender_id, data in offender_data.items():
            risk_score = data.get("risk_score", 0)
            level = self._get_risk_level(risk_score)
            risk_distribution[level] = risk_distribution.get(level, 0) + 1

        # High recidivism categories
        category_recidivism = await self._analyze_category_recidivism(
            jurisdiction, start_date, end_date
        )
        high_recidivism_categories = sorted(
            category_recidivism, key=lambda x: x["recidivism_rate"], reverse=True
        )[:5]

        # Calculate trend
        trend, trend_change = await self._calculate_recidivism_trend(
            jurisdiction, start_date, end_date
        )

        return RecidivismAnalysis(
            jurisdiction=jurisdiction,
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            total_offenders=total_offenders,
            repeat_offenders=repeat_offenders,
            repeat_offender_rate=round(repeat_rate * 100, 2),
            recidivism_rate_30_day=round(recidivism_30 * 100, 2),
            recidivism_rate_90_day=round(recidivism_90 * 100, 2),
            recidivism_rate_1_year=round(recidivism_365 * 100, 2),
            risk_distribution=risk_distribution,
            high_recidivism_categories=high_recidivism_categories,
            recidivism_trend=trend,
            trend_percent_change=round(trend_change, 2),
        )

    async def get_offender_timeline(
        self,
        offender_id: str,
        jurisdiction: str,
    ) -> OffenderTimeline:
        """
        Get detailed incident timeline for an offender.

        Args:
            offender_id: Offender identifier
            jurisdiction: Jurisdiction code

        Returns:
            Offender timeline
        """
        incidents = await self._fetch_offender_incidents(offender_id, jurisdiction)

        if not incidents:
            return OffenderTimeline(
                offender_id=offender_id,
                incidents=[],
                total_incidents=0,
            )

        # Sort by timestamp
        incidents = sorted(incidents, key=lambda x: x["timestamp"])

        # Calculate gaps
        gaps = []
        for i in range(1, len(incidents)):
            gap = (incidents[i]["timestamp"] - incidents[i - 1]["timestamp"]).days
            gaps.append(gap)

        average_gap = sum(gaps) / len(gaps) if gaps else None
        shortest_gap = min(gaps) if gaps else None
        longest_gap = max(gaps) if gaps else None

        # Track severity progression
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        severity_progression = [i.get("severity", "medium") for i in incidents]

        # Determine if escalating
        if len(severity_progression) >= 2:
            first_half_avg = sum(
                severity_order.get(s, 2) for s in severity_progression[: len(severity_progression) // 2]
            ) / (len(severity_progression) // 2)
            second_half_avg = sum(
                severity_order.get(s, 2) for s in severity_progression[len(severity_progression) // 2 :]
            ) / (len(severity_progression) - len(severity_progression) // 2)
            is_escalating = second_half_avg > first_half_avg + 0.3
        else:
            is_escalating = False

        # Format incidents for timeline
        timeline_incidents = [
            {
                "date": i["timestamp"].isoformat() if isinstance(i["timestamp"], datetime) else i["timestamp"],
                "incident_number": i.get("incident_number", ""),
                "crime_type": i.get("crime_type", ""),
                "crime_category": i.get("crime_category", ""),
                "severity": i.get("severity", "medium"),
                "location": i.get("address", ""),
                "arrest_made": i.get("arrest_made", False),
            }
            for i in incidents
        ]

        return OffenderTimeline(
            offender_id=offender_id,
            incidents=timeline_incidents,
            total_incidents=len(incidents),
            average_days_between=round(average_gap, 1) if average_gap else None,
            shortest_gap=shortest_gap,
            longest_gap=longest_gap,
            severity_progression=severity_progression,
            is_escalating=is_escalating,
        )

    async def analyze_network(
        self,
        offender_id: str,
        jurisdiction: str,
        depth: int = 2,
    ) -> NetworkAnalysis:
        """
        Analyze offender's network of associates.

        Args:
            offender_id: Offender identifier
            jurisdiction: Jurisdiction code
            depth: Network traversal depth

        Returns:
            Network analysis result
        """
        try:
            # Query Neo4j for network
            query = """
            MATCH (o:Offender {id: $offender_id, jurisdiction: $jurisdiction})
            OPTIONAL MATCH (o)-[r:ASSOCIATED_WITH]-(associate:Offender)
            WITH o, collect(DISTINCT {
                id: associate.id,
                name: associate.name,
                risk_score: associate.risk_score,
                incident_count: associate.incident_count,
                relationship_type: type(r),
                strength: r.strength
            }) as direct_associates
            OPTIONAL MATCH (o)-[:ASSOCIATED_WITH*2..3]-(indirect:Offender)
            WHERE indirect.id <> o.id AND NOT indirect IN [a IN direct_associates | a.id]
            WITH o, direct_associates, count(DISTINCT indirect) as indirect_count
            OPTIONAL MATCH (o)-[:MEMBER_OF]->(g:Gang)
            RETURN o, direct_associates, indirect_count, collect(DISTINCT g.name) as gangs
            """

            result = await self.neo4j.execute_query(
                query,
                {"offender_id": offender_id, "jurisdiction": jurisdiction},
            )

            if not result:
                return self._empty_network_analysis(offender_id)

            record = result[0]
            direct_associates = record.get("direct_associates", [])
            indirect_count = record.get("indirect_count", 0)
            gangs = record.get("gangs", [])

            # Calculate centrality (simplified)
            network_size = len(direct_associates) + indirect_count
            centrality = min(1.0, len(direct_associates) / 10) if direct_associates else 0

            # Calculate influence
            avg_associate_risk = (
                sum(a.get("risk_score", 0) for a in direct_associates) / len(direct_associates)
                if direct_associates
                else 0
            )
            influence = min(1.0, (centrality + avg_associate_risk / 100) / 2)

            # Determine if network leader
            is_leader = centrality > 0.7 and influence > 0.6

            return NetworkAnalysis(
                offender_id=offender_id,
                network_size=network_size,
                direct_associates=direct_associates,
                indirect_associates=indirect_count,
                centrality_score=round(centrality, 4),
                influence_score=round(influence, 4),
                gang_connections=gangs,
                is_network_leader=is_leader,
            )

        except Exception as e:
            logger.error(f"Network analysis failed: {e}")
            return self._empty_network_analysis(offender_id)

    async def get_high_risk_offenders(
        self,
        jurisdiction: str,
        limit: int = 50,
        min_risk_score: float = 60,
    ) -> list[OffenderProfile]:
        """
        Get high-risk offenders for a jurisdiction.

        Args:
            jurisdiction: Jurisdiction code
            limit: Maximum results
            min_risk_score: Minimum risk score

        Returns:
            List of high-risk offender profiles
        """
        try:
            # Query for high-risk offenders
            query = {
                "bool": {
                    "must": [
                        {"term": {"jurisdiction": jurisdiction}},
                        {"range": {"risk_score": {"gte": min_risk_score}}},
                    ]
                }
            }

            result = await self.es.search(
                index="datalake_offenders",
                query=query,
                sort=[{"risk_score": "desc"}],
                size=limit,
            )

            profiles = []
            for hit in result.get("hits", {}).get("hits", []):
                source = hit["_source"]
                profiles.append(OffenderProfile(
                    offender_id=source["offender_id"],
                    jurisdiction=source["jurisdiction"],
                    total_incidents=source.get("total_incidents", 0),
                    first_incident_date=source.get("first_incident_date"),
                    last_incident_date=source.get("last_incident_date"),
                    crime_categories=source.get("crime_categories", {}),
                    severity_breakdown=source.get("severity_breakdown", {}),
                    risk_score=source.get("risk_score", 0),
                    risk_level=source.get("risk_level", "low"),
                    risk_factors=source.get("risk_factors", []),
                    is_repeat_offender=source.get("is_repeat_offender", False),
                    recidivism_rate=source.get("recidivism_rate", 0),
                    escalation_trend=source.get("escalation_trend", "stable"),
                    known_associates=source.get("known_associates", 0),
                    gang_affiliated=source.get("gang_affiliated", False),
                ))

            return profiles

        except Exception as e:
            logger.error(f"Failed to fetch high-risk offenders: {e}")
            return []

    async def _fetch_offender_incidents(
        self,
        offender_id: str,
        jurisdiction: str,
    ) -> list[dict[str, Any]]:
        """Fetch all incidents for an offender."""
        try:
            query = {
                "bool": {
                    "must": [
                        {"term": {"offender_id": offender_id}},
                        {"term": {"jurisdiction": jurisdiction}},
                    ]
                }
            }

            result = await self.es.search(
                index="datalake_incidents",
                query=query,
                sort=[{"timestamp": "asc"}],
                size=1000,
            )

            incidents = []
            for hit in result.get("hits", {}).get("hits", []):
                source = hit["_source"]
                # Parse timestamp
                ts = source.get("timestamp")
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                source["timestamp"] = ts
                incidents.append(source)

            return incidents

        except Exception as e:
            logger.error(f"Failed to fetch offender incidents: {e}")
            # Return mock data
            return self._generate_mock_incidents(offender_id)

    def _generate_mock_incidents(self, offender_id: str) -> list[dict[str, Any]]:
        """Generate mock incident data."""
        import random

        incidents = []
        base_date = datetime.utcnow() - timedelta(days=365 * 3)

        for i in range(random.randint(2, 10)):
            date = base_date + timedelta(days=random.randint(0, 365 * 3))
            incidents.append({
                "timestamp": date,
                "incident_number": f"INC-{offender_id}-{i:03d}",
                "crime_type": random.choice(["theft", "assault", "burglary", "drug_possession"]),
                "crime_category": random.choice(["property", "violent", "drug"]),
                "severity": random.choice(["low", "medium", "high"]),
                "address": f"{random.randint(100, 9999)} Main St",
                "arrest_made": random.choice([True, False]),
            })

        return sorted(incidents, key=lambda x: x["timestamp"])

    async def _fetch_offender_summary(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        crime_category: str | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Fetch summary of all offenders in period."""
        try:
            must_clauses = [
                {"term": {"jurisdiction": jurisdiction}},
                {"range": {"timestamp": {
                    "gte": start_date.isoformat(),
                    "lte": end_date.isoformat(),
                }}},
            ]

            if crime_category:
                must_clauses.append({"term": {"crime_category": crime_category}})

            query = {"bool": {"must": must_clauses}}

            aggs = {
                "by_offender": {
                    "terms": {"field": "offender_id", "size": 10000},
                    "aggs": {
                        "avg_risk": {"avg": {"field": "risk_score"}},
                    },
                }
            }

            result = await self.es.search(
                index="datalake_incidents",
                query=query,
                aggs=aggs,
                size=0,
            )

            offenders = {}
            for bucket in result.get("aggregations", {}).get("by_offender", {}).get("buckets", []):
                offenders[bucket["key"]] = {
                    "incident_count": bucket["doc_count"],
                    "risk_score": bucket.get("avg_risk", {}).get("value", 0),
                }

            return offenders

        except Exception as e:
            logger.error(f"Failed to fetch offender summary: {e}")
            return {}

    async def _calculate_risk_score(
        self,
        offender_id: str,
        jurisdiction: str,
        incidents: list[dict[str, Any]],
    ) -> tuple[float, list[str]]:
        """Calculate risk score for an offender."""
        risk_factors = []
        scores = {}

        # Incident count score (0-100)
        count = len(incidents)
        if count >= 10:
            scores["incident_count"] = 100
            risk_factors.append("High incident count (10+)")
        elif count >= 5:
            scores["incident_count"] = 70
            risk_factors.append("Elevated incident count (5-9)")
        elif count >= 3:
            scores["incident_count"] = 40
        else:
            scores["incident_count"] = 20

        # Severity history score
        severity_scores = {"critical": 100, "high": 75, "medium": 50, "low": 25}
        avg_severity = sum(
            severity_scores.get(i.get("severity", "medium"), 50) for i in incidents
        ) / len(incidents) if incidents else 50
        scores["severity_history"] = avg_severity

        if avg_severity >= 75:
            risk_factors.append("History of high-severity incidents")

        # Recency score
        if incidents:
            last_incident = max(i["timestamp"] for i in incidents)
            days_since = (datetime.utcnow() - last_incident).days if isinstance(last_incident, datetime) else 365

            if days_since <= 30:
                scores["recency"] = 100
                risk_factors.append("Recent activity (within 30 days)")
            elif days_since <= 90:
                scores["recency"] = 75
            elif days_since <= 180:
                scores["recency"] = 50
            else:
                scores["recency"] = 25
        else:
            scores["recency"] = 0

        # Escalation score
        escalation = self._determine_escalation_trend(incidents)
        if escalation == "escalating":
            scores["escalation"] = 100
            risk_factors.append("Escalating severity pattern")
        elif escalation == "stable":
            scores["escalation"] = 50
        else:
            scores["escalation"] = 25

        # Network score
        network_info = await self._get_network_summary(offender_id, jurisdiction)
        associate_count = network_info.get("associate_count", 0)
        if associate_count >= 5:
            scores["network"] = 80
            risk_factors.append("Large criminal network")
        elif associate_count >= 2:
            scores["network"] = 50
        else:
            scores["network"] = 20

        if network_info.get("gang_affiliated"):
            scores["network"] = min(100, scores["network"] + 30)
            risk_factors.append("Gang affiliation")

        # Calculate weighted score
        total_score = sum(
            scores[k] * self.RISK_WEIGHTS[k] for k in self.RISK_WEIGHTS
        )

        return total_score, risk_factors

    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score."""
        for level, threshold in sorted(
            self.RISK_THRESHOLDS.items(), key=lambda x: x[1], reverse=True
        ):
            if score >= threshold:
                return level
        return "low"

    def _calculate_recidivism_rate(self, incidents: list[dict[str, Any]]) -> float:
        """Calculate recidivism rate from incidents."""
        if len(incidents) < 2:
            return 0.0

        # Count re-offenses within 1 year of previous
        reoffenses = 0
        for i in range(1, len(incidents)):
            prev = incidents[i - 1]["timestamp"]
            curr = incidents[i]["timestamp"]
            if isinstance(prev, datetime) and isinstance(curr, datetime):
                gap = (curr - prev).days
                if gap <= 365:
                    reoffenses += 1

        return reoffenses / (len(incidents) - 1)

    def _determine_escalation_trend(self, incidents: list[dict[str, Any]]) -> str:
        """Determine if offender is escalating."""
        if len(incidents) < 3:
            return "stable"

        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}

        # Compare first third to last third
        third = len(incidents) // 3
        first_avg = sum(
            severity_order.get(i.get("severity", "medium"), 2)
            for i in incidents[:third]
        ) / third
        last_avg = sum(
            severity_order.get(i.get("severity", "medium"), 2)
            for i in incidents[-third:]
        ) / third

        if last_avg > first_avg + 0.5:
            return "escalating"
        elif last_avg < first_avg - 0.5:
            return "de-escalating"
        return "stable"

    async def _get_network_summary(
        self,
        offender_id: str,
        jurisdiction: str,
    ) -> dict[str, Any]:
        """Get network summary for offender."""
        try:
            query = """
            MATCH (o:Offender {id: $offender_id, jurisdiction: $jurisdiction})
            OPTIONAL MATCH (o)-[:ASSOCIATED_WITH]-(a:Offender)
            OPTIONAL MATCH (o)-[:MEMBER_OF]->(g:Gang)
            RETURN count(DISTINCT a) as associate_count, count(DISTINCT g) > 0 as gang_affiliated
            """

            result = await self.neo4j.execute_query(
                query,
                {"offender_id": offender_id, "jurisdiction": jurisdiction},
            )

            if result:
                return {
                    "associate_count": result[0].get("associate_count", 0),
                    "gang_affiliated": result[0].get("gang_affiliated", False),
                }

        except Exception as e:
            logger.warning(f"Network query failed: {e}")

        return {"associate_count": 0, "gang_affiliated": False}

    async def _calculate_window_recidivism(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
        window_days: int,
    ) -> float:
        """Calculate recidivism rate within a time window."""
        # Simplified calculation
        # In production, would query for offenders who re-offended within window
        import random
        base_rate = 0.15 + (window_days / 365) * 0.25
        return min(0.5, base_rate + random.uniform(-0.05, 0.05))

    async def _analyze_category_recidivism(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, Any]]:
        """Analyze recidivism by crime category."""
        categories = ["violent", "property", "drug", "disorder", "other"]
        results = []

        for cat in categories:
            # Simplified - in production would calculate actual rates
            import random
            rate = random.uniform(0.1, 0.4)
            results.append({
                "category": cat,
                "recidivism_rate": round(rate, 4),
                "offender_count": random.randint(50, 500),
            })

        return results

    async def _calculate_recidivism_trend(
        self,
        jurisdiction: str,
        start_date: datetime,
        end_date: datetime,
    ) -> tuple[str, float]:
        """Calculate recidivism trend over time."""
        # Simplified - in production would compare periods
        import random
        change = random.uniform(-10, 10)

        if change > 3:
            return "increasing", change
        elif change < -3:
            return "decreasing", change
        return "stable", change

    def _empty_profile(self, offender_id: str, jurisdiction: str) -> OffenderProfile:
        """Return empty offender profile."""
        return OffenderProfile(
            offender_id=offender_id,
            jurisdiction=jurisdiction,
            total_incidents=0,
            risk_score=0,
            risk_level="low",
            is_repeat_offender=False,
            recidivism_rate=0,
            escalation_trend="stable",
        )

    def _empty_network_analysis(self, offender_id: str) -> NetworkAnalysis:
        """Return empty network analysis."""
        return NetworkAnalysis(
            offender_id=offender_id,
            network_size=0,
            centrality_score=0,
            influence_score=0,
            is_network_leader=False,
        )

    async def _get_cached(self, key: str) -> dict[str, Any] | None:
        """Get cached value."""
        try:
            return await self.redis.get(key)
        except Exception:
            return None

    async def _set_cached(self, key: str, value: dict[str, Any]) -> None:
        """Set cached value."""
        try:
            await self.redis.set(key, value, ex=self.CACHE_TTL)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
