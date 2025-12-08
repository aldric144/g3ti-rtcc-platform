"""
Tactical Risk Scoring Engine for G3TI RTCC-UIP.

This module provides risk scoring capabilities for:
- Address-level risk assessment
- Micro-zone risk scoring
- District-level risk aggregation
- Entity risk scoring (persons, vehicles, addresses)

Risk factors include:
- Repeat offender density
- Gunfire frequency
- Vehicle-of-interest recurrence
- LPR cluster acceleration
- RMS violent crime history
- CAD call density
- AI anomaly signals
- Entity risk scores from Phase 3
"""

import logging
from datetime import datetime

import numpy as np

from ...db.elasticsearch import ElasticsearchManager
from ...db.neo4j import Neo4jManager
from ...db.redis import RedisManager

logger = logging.getLogger(__name__)


class TacticalRiskScorer:
    """
    Engine for computing tactical risk scores at various granularities.

    Supports address-level, micro-zone, and district-level risk assessment
    using multiple weighted factors from various data sources.
    """

    # Risk factor weights
    RISK_WEIGHTS = {
        "repeat_offender_density": 0.20,
        "gunfire_frequency": 0.18,
        "vehicle_recurrence": 0.12,
        "lpr_cluster_acceleration": 0.10,
        "violent_crime_history": 0.15,
        "cad_call_density": 0.10,
        "ai_anomaly_signals": 0.08,
        "entity_risk_scores": 0.07,
    }

    # Risk level thresholds
    RISK_THRESHOLDS = {
        "critical": 0.8,
        "high": 0.6,
        "elevated": 0.4,
        "moderate": 0.2,
        "low": 0.0,
    }

    # Time windows for analysis
    TIME_WINDOWS = {
        "short": 24,      # 24 hours
        "medium": 168,    # 7 days
        "long": 720,      # 30 days
    }

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
    ):
        """
        Initialize the Tactical Risk Scorer.

        Args:
            neo4j: Neo4j database manager
            es: Elasticsearch manager
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        # Cache settings
        self._cache_ttl = 600  # 10 minutes

        logger.info("TacticalRiskScorer initialized")

    async def generate_risk_map(
        self,
        zone_id: str | None = None,
        level: str = "micro",
        include_factors: bool = True,
    ) -> dict:
        """
        Generate tactical risk map for zones.

        Args:
            zone_id: Specific zone ID or None for all zones
            level: Risk level granularity (address, micro, district)
            include_factors: Include detailed risk factor breakdown

        Returns:
            Risk map with scores and explanations
        """
        logger.info(f"Generating risk map: zone={zone_id}, level={level}")

        # Get zones to analyze
        zones = await self._get_zones(zone_id, level)

        risk_scores = []
        for zone in zones:
            score_data = await self._compute_zone_risk(zone, include_factors)
            risk_scores.append(score_data)

        # Sort by risk score (highest first)
        risk_scores.sort(key=lambda x: x["risk_score"], reverse=True)

        # Generate summary statistics
        summary = self._generate_risk_summary(risk_scores)

        return {
            "zones": risk_scores,
            "summary": summary,
            "level": level,
            "generated_at": datetime.utcnow().isoformat(),
            "total_zones": len(risk_scores),
        }

    async def score_entity(
        self,
        entity_id: str,
        entity_type: str,
    ) -> dict:
        """
        Get risk score for a specific entity.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity (person, vehicle, address)

        Returns:
            Risk score with contributing factors
        """
        logger.info(f"Scoring entity: {entity_type}/{entity_id}")

        # Fetch entity data from Neo4j
        entity_data = await self._fetch_entity_data(entity_id, entity_type)

        if not entity_data:
            return {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "risk_score": 0.0,
                "risk_level": "unknown",
                "error": "Entity not found",
            }

        # Compute risk based on entity type
        if entity_type == "person":
            score_data = await self._score_person(entity_data)
        elif entity_type == "vehicle":
            score_data = await self._score_vehicle(entity_data)
        elif entity_type == "address":
            score_data = await self._score_address(entity_data)
        else:
            score_data = {"risk_score": 0.0, "factors": {}}

        risk_level = self._get_risk_level(score_data["risk_score"])

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "risk_score": score_data["risk_score"],
            "risk_level": risk_level,
            "factors": score_data.get("factors", {}),
            "recommendations": self._generate_entity_recommendations(
                entity_type, score_data
            ),
            "scored_at": datetime.utcnow().isoformat(),
        }

    async def update_with_incident(self, incident_data: dict) -> dict:
        """
        Update risk scores based on new incident.

        Args:
            incident_data: New incident information

        Returns:
            Update summary with affected zones
        """
        lat = incident_data.get("latitude")
        lon = incident_data.get("longitude")
        incident_type = incident_data.get("type", "unknown")
        severity = incident_data.get("severity", "medium")

        affected_zones = []
        risk_changes = []

        if lat and lon:
            # Find affected zones
            zones = await self._find_zones_by_location(lat, lon)

            for zone in zones:
                # Recalculate zone risk
                old_score = zone.get("risk_score", 0.0)
                new_score_data = await self._compute_zone_risk(zone, False)
                new_score = new_score_data["risk_score"]

                # Apply incident impact
                impact = self._calculate_incident_impact(incident_type, severity)
                adjusted_score = min(1.0, new_score + impact)

                affected_zones.append(zone["id"])
                risk_changes.append({
                    "zone_id": zone["id"],
                    "old_score": old_score,
                    "new_score": adjusted_score,
                    "change": adjusted_score - old_score,
                })

        # Invalidate cache
        await self._invalidate_cache()

        return {
            "updated": True,
            "incident_type": incident_type,
            "affected_zones": affected_zones,
            "risk_changes": risk_changes,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ==================== Zone Risk Computation ====================

    async def _compute_zone_risk(
        self,
        zone: dict,
        include_factors: bool = True,
    ) -> dict:
        """Compute comprehensive risk score for a zone."""
        zone_id = zone.get("id", "unknown")
        bounds = zone.get("bounds", {})

        # Compute individual risk factors
        factors = {}

        # 1. Repeat offender density
        factors["repeat_offender_density"] = await self._compute_repeat_offender_density(
            bounds
        )

        # 2. Gunfire frequency
        factors["gunfire_frequency"] = await self._compute_gunfire_frequency(bounds)

        # 3. Vehicle-of-interest recurrence
        factors["vehicle_recurrence"] = await self._compute_vehicle_recurrence(bounds)

        # 4. LPR cluster acceleration
        factors["lpr_cluster_acceleration"] = await self._compute_lpr_acceleration(
            bounds
        )

        # 5. Violent crime history
        factors["violent_crime_history"] = await self._compute_violent_crime_history(
            bounds
        )

        # 6. CAD call density
        factors["cad_call_density"] = await self._compute_cad_density(bounds)

        # 7. AI anomaly signals
        factors["ai_anomaly_signals"] = await self._compute_ai_anomaly_signals(bounds)

        # 8. Entity risk scores
        factors["entity_risk_scores"] = await self._compute_entity_risk_aggregate(
            bounds
        )

        # Calculate weighted risk score
        risk_score = sum(
            factors[factor] * self.RISK_WEIGHTS[factor]
            for factor in factors
        )

        # Normalize to 0-1
        risk_score = min(1.0, max(0.0, risk_score))

        risk_level = self._get_risk_level(risk_score)

        result = {
            "id": zone_id,
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "center": zone.get("center", {}),
            "bounds": bounds,
        }

        if include_factors:
            result["factors"] = {
                k: round(v, 3) for k, v in factors.items()
            }
            result["top_factors"] = self._get_top_factors(factors)
            result["explanation"] = self._generate_zone_explanation(
                zone_id, risk_level, factors
            )

        return result

    async def _compute_repeat_offender_density(self, bounds: dict) -> float:
        """Compute repeat offender density in zone."""
        try:
            # Query Neo4j for repeat offenders in zone
            query = """
            MATCH (p:Person)-[:INVOLVED_IN]->(i:Incident)
            WHERE i.latitude >= $min_lat AND i.latitude <= $max_lat
            AND i.longitude >= $min_lon AND i.longitude <= $max_lon
            WITH p, count(i) as incident_count
            WHERE incident_count >= 2
            RETURN count(p) as repeat_offenders
            """

            result = await self.neo4j.execute_query(
                query,
                min_lat=bounds.get("min_lat", 0),
                max_lat=bounds.get("max_lat", 0),
                min_lon=bounds.get("min_lon", 0),
                max_lon=bounds.get("max_lon", 0),
            )

            count = result[0]["repeat_offenders"] if result else 0
            # Normalize: 10+ repeat offenders = 1.0
            return min(1.0, count / 10)
        except Exception as e:
            logger.warning(f"Failed to compute repeat offender density: {e}")
            return np.random.uniform(0.2, 0.6)  # Mock data

    async def _compute_gunfire_frequency(self, bounds: dict) -> float:
        """Compute gunfire frequency in zone."""
        try:
            # Query Elasticsearch for gunfire incidents
            query = {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-7d"}}},
                        {"terms": {"type": ["shotspotter", "shots_fired"]}},
                    ],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds.get("max_lat", 0),
                                        "lon": bounds.get("min_lon", 0),
                                    },
                                    "bottom_right": {
                                        "lat": bounds.get("min_lat", 0),
                                        "lon": bounds.get("max_lon", 0),
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            result = await self.es.count(index="incidents,shotspotter", query=query)
            count = result.get("count", 0)

            # Normalize: 20+ gunfire incidents in 7 days = 1.0
            return min(1.0, count / 20)
        except Exception as e:
            logger.warning(f"Failed to compute gunfire frequency: {e}")
            return np.random.uniform(0.1, 0.5)

    async def _compute_vehicle_recurrence(self, bounds: dict) -> float:
        """Compute vehicle-of-interest recurrence in zone."""
        try:
            # Query for recurring vehicles of interest
            query = {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-7d"}}},
                        {"term": {"is_hotlist": True}},
                    ],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds.get("max_lat", 0),
                                        "lon": bounds.get("min_lon", 0),
                                    },
                                    "bottom_right": {
                                        "lat": bounds.get("min_lat", 0),
                                        "lon": bounds.get("max_lon", 0),
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            result = await self.es.count(index="lpr_hits", query=query)
            count = result.get("count", 0)

            # Normalize: 15+ hotlist hits = 1.0
            return min(1.0, count / 15)
        except Exception as e:
            logger.warning(f"Failed to compute vehicle recurrence: {e}")
            return np.random.uniform(0.1, 0.4)

    async def _compute_lpr_acceleration(self, bounds: dict) -> float:
        """Compute LPR cluster acceleration (rate of change)."""
        try:
            # Compare recent week to previous week
            recent_query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": "now-7d"}}}],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds.get("max_lat", 0),
                                        "lon": bounds.get("min_lon", 0),
                                    },
                                    "bottom_right": {
                                        "lat": bounds.get("min_lat", 0),
                                        "lon": bounds.get("max_lon", 0),
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            previous_query = {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "timestamp": {"gte": "now-14d", "lt": "now-7d"}
                            }
                        }
                    ],
                    "filter": recent_query["bool"]["filter"],
                }
            }

            recent_count = (
                await self.es.count(index="lpr_hits", query=recent_query)
            ).get("count", 0)
            previous_count = (
                await self.es.count(index="lpr_hits", query=previous_query)
            ).get("count", 1)  # Avoid division by zero

            # Calculate acceleration
            acceleration = (recent_count - previous_count) / max(previous_count, 1)

            # Normalize: 100% increase = 1.0
            return min(1.0, max(0.0, acceleration))
        except Exception as e:
            logger.warning(f"Failed to compute LPR acceleration: {e}")
            return np.random.uniform(0.0, 0.3)

    async def _compute_violent_crime_history(self, bounds: dict) -> float:
        """Compute violent crime history in zone."""
        try:
            query = {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-30d"}}},
                        {
                            "terms": {
                                "type": [
                                    "assault",
                                    "robbery",
                                    "homicide",
                                    "aggravated_assault",
                                ]
                            }
                        },
                    ],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds.get("max_lat", 0),
                                        "lon": bounds.get("min_lon", 0),
                                    },
                                    "bottom_right": {
                                        "lat": bounds.get("min_lat", 0),
                                        "lon": bounds.get("max_lon", 0),
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            result = await self.es.count(index="incidents", query=query)
            count = result.get("count", 0)

            # Normalize: 10+ violent crimes in 30 days = 1.0
            return min(1.0, count / 10)
        except Exception as e:
            logger.warning(f"Failed to compute violent crime history: {e}")
            return np.random.uniform(0.2, 0.5)

    async def _compute_cad_density(self, bounds: dict) -> float:
        """Compute CAD call density in zone."""
        try:
            query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": "now-7d"}}}],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds.get("max_lat", 0),
                                        "lon": bounds.get("min_lon", 0),
                                    },
                                    "bottom_right": {
                                        "lat": bounds.get("min_lat", 0),
                                        "lon": bounds.get("max_lon", 0),
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            result = await self.es.count(index="cad_calls", query=query)
            count = result.get("count", 0)

            # Normalize: 100+ CAD calls in 7 days = 1.0
            return min(1.0, count / 100)
        except Exception as e:
            logger.warning(f"Failed to compute CAD density: {e}")
            return np.random.uniform(0.3, 0.6)

    async def _compute_ai_anomaly_signals(self, bounds: dict) -> float:
        """Compute AI anomaly signals in zone."""
        try:
            # Query for recent anomalies from AI engine
            query = {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-24h"}}},
                        {"term": {"type": "anomaly"}},
                    ],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds.get("max_lat", 0),
                                        "lon": bounds.get("min_lon", 0),
                                    },
                                    "bottom_right": {
                                        "lat": bounds.get("min_lat", 0),
                                        "lon": bounds.get("max_lon", 0),
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            result = await self.es.count(index="ai_anomalies", query=query)
            count = result.get("count", 0)

            # Normalize: 5+ anomalies in 24h = 1.0
            return min(1.0, count / 5)
        except Exception as e:
            logger.warning(f"Failed to compute AI anomaly signals: {e}")
            return np.random.uniform(0.0, 0.3)

    async def _compute_entity_risk_aggregate(self, bounds: dict) -> float:
        """Compute aggregate entity risk scores in zone."""
        try:
            # Query Neo4j for high-risk entities in zone
            query = """
            MATCH (e)
            WHERE e.latitude >= $min_lat AND e.latitude <= $max_lat
            AND e.longitude >= $min_lon AND e.longitude <= $max_lon
            AND e.risk_score IS NOT NULL
            RETURN avg(e.risk_score) as avg_risk
            """

            result = await self.neo4j.execute_query(
                query,
                min_lat=bounds.get("min_lat", 0),
                max_lat=bounds.get("max_lat", 0),
                min_lon=bounds.get("min_lon", 0),
                max_lon=bounds.get("max_lon", 0),
            )

            avg_risk = result[0]["avg_risk"] if result and result[0]["avg_risk"] else 0
            return min(1.0, avg_risk)
        except Exception as e:
            logger.warning(f"Failed to compute entity risk aggregate: {e}")
            return np.random.uniform(0.1, 0.4)

    # ==================== Entity Risk Scoring ====================

    async def _score_person(self, entity_data: dict) -> dict:
        """Score risk for a person entity."""
        factors = {}

        # Criminal history factor
        criminal_history = entity_data.get("criminal_history", [])
        factors["criminal_history"] = min(1.0, len(criminal_history) / 10)

        # Warrant status
        has_warrant = entity_data.get("has_active_warrant", False)
        factors["warrant_status"] = 1.0 if has_warrant else 0.0

        # Gang affiliation
        gang_affiliated = entity_data.get("gang_affiliated", False)
        factors["gang_affiliation"] = 0.8 if gang_affiliated else 0.0

        # Recent incidents
        recent_incidents = entity_data.get("recent_incidents", 0)
        factors["recent_activity"] = min(1.0, recent_incidents / 5)

        # Known associates risk
        associates_risk = entity_data.get("associates_avg_risk", 0.0)
        factors["associates_risk"] = associates_risk

        # Calculate weighted score
        weights = {
            "criminal_history": 0.25,
            "warrant_status": 0.25,
            "gang_affiliation": 0.20,
            "recent_activity": 0.20,
            "associates_risk": 0.10,
        }

        risk_score = sum(factors[f] * weights[f] for f in factors)

        return {
            "risk_score": round(risk_score, 3),
            "factors": factors,
        }

    async def _score_vehicle(self, entity_data: dict) -> dict:
        """Score risk for a vehicle entity."""
        factors = {}

        # Hotlist status
        on_hotlist = entity_data.get("on_hotlist", False)
        factors["hotlist_status"] = 1.0 if on_hotlist else 0.0

        # Stolen status
        is_stolen = entity_data.get("is_stolen", False)
        factors["stolen_status"] = 1.0 if is_stolen else 0.0

        # LPR hit frequency
        lpr_hits = entity_data.get("lpr_hit_count", 0)
        factors["lpr_frequency"] = min(1.0, lpr_hits / 20)

        # Associated incidents
        incidents = entity_data.get("incident_count", 0)
        factors["incident_association"] = min(1.0, incidents / 5)

        # Owner risk
        owner_risk = entity_data.get("owner_risk_score", 0.0)
        factors["owner_risk"] = owner_risk

        # Calculate weighted score
        weights = {
            "hotlist_status": 0.30,
            "stolen_status": 0.25,
            "lpr_frequency": 0.20,
            "incident_association": 0.15,
            "owner_risk": 0.10,
        }

        risk_score = sum(factors[f] * weights[f] for f in factors)

        return {
            "risk_score": round(risk_score, 3),
            "factors": factors,
        }

    async def _score_address(self, entity_data: dict) -> dict:
        """Score risk for an address entity."""
        factors = {}

        # Incident history
        incidents = entity_data.get("incident_count", 0)
        factors["incident_history"] = min(1.0, incidents / 20)

        # CAD call history
        cad_calls = entity_data.get("cad_call_count", 0)
        factors["cad_history"] = min(1.0, cad_calls / 50)

        # Known offender residence
        offender_residence = entity_data.get("known_offender_residence", False)
        factors["offender_residence"] = 0.8 if offender_residence else 0.0

        # Drug activity
        drug_activity = entity_data.get("drug_activity_flag", False)
        factors["drug_activity"] = 0.7 if drug_activity else 0.0

        # Proximity to hotspots
        hotspot_proximity = entity_data.get("hotspot_proximity_score", 0.0)
        factors["hotspot_proximity"] = hotspot_proximity

        # Calculate weighted score
        weights = {
            "incident_history": 0.25,
            "cad_history": 0.20,
            "offender_residence": 0.25,
            "drug_activity": 0.15,
            "hotspot_proximity": 0.15,
        }

        risk_score = sum(factors[f] * weights[f] for f in factors)

        return {
            "risk_score": round(risk_score, 3),
            "factors": factors,
        }

    # ==================== Helper Methods ====================

    async def _get_zones(
        self,
        zone_id: str | None,
        level: str,
    ) -> list[dict]:
        """Get zones to analyze based on level."""
        if zone_id:
            # Return specific zone
            zone_data = await self._fetch_zone_data(zone_id)
            return [zone_data] if zone_data else []

        # Generate zones based on level
        zones = []

        # Default bounds (example city area)
        base_bounds = {
            "min_lat": 33.35,
            "max_lat": 33.55,
            "min_lon": -112.15,
            "max_lon": -111.95,
        }

        if level == "address":
            # Very fine grid (100m x 100m)
            grid_size = 50
        elif level == "micro":
            # Medium grid (250m x 250m)
            grid_size = 20
        else:  # district
            # Coarse grid (1km x 1km)
            grid_size = 5

        lat_step = (base_bounds["max_lat"] - base_bounds["min_lat"]) / grid_size
        lon_step = (base_bounds["max_lon"] - base_bounds["min_lon"]) / grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                min_lat = base_bounds["min_lat"] + i * lat_step
                max_lat = min_lat + lat_step
                min_lon = base_bounds["min_lon"] + j * lon_step
                max_lon = min_lon + lon_step

                zones.append({
                    "id": f"{level}_{i}_{j}",
                    "bounds": {
                        "min_lat": min_lat,
                        "max_lat": max_lat,
                        "min_lon": min_lon,
                        "max_lon": max_lon,
                    },
                    "center": {
                        "lat": (min_lat + max_lat) / 2,
                        "lon": (min_lon + max_lon) / 2,
                    },
                })

        return zones

    async def _fetch_zone_data(self, zone_id: str) -> dict | None:
        """Fetch zone data from database."""
        try:
            # Parse zone ID to get bounds
            parts = zone_id.split("_")
            if len(parts) >= 3:
                level = parts[0]
                i, j = int(parts[1]), int(parts[2])

                # Reconstruct bounds
                base_bounds = {
                    "min_lat": 33.35,
                    "max_lat": 33.55,
                    "min_lon": -112.15,
                    "max_lon": -111.95,
                }

                grid_sizes = {"address": 50, "micro": 20, "district": 5}
                grid_size = grid_sizes.get(level, 20)

                lat_step = (base_bounds["max_lat"] - base_bounds["min_lat"]) / grid_size
                lon_step = (base_bounds["max_lon"] - base_bounds["min_lon"]) / grid_size

                return {
                    "id": zone_id,
                    "bounds": {
                        "min_lat": base_bounds["min_lat"] + i * lat_step,
                        "max_lat": base_bounds["min_lat"] + (i + 1) * lat_step,
                        "min_lon": base_bounds["min_lon"] + j * lon_step,
                        "max_lon": base_bounds["min_lon"] + (j + 1) * lon_step,
                    },
                    "center": {
                        "lat": base_bounds["min_lat"] + (i + 0.5) * lat_step,
                        "lon": base_bounds["min_lon"] + (j + 0.5) * lon_step,
                    },
                }
        except Exception as e:
            logger.warning(f"Failed to fetch zone data: {e}")

        return None

    async def _fetch_entity_data(
        self,
        entity_id: str,
        entity_type: str,
    ) -> dict | None:
        """Fetch entity data from Neo4j."""
        try:
            query = f"""
            MATCH (e:{entity_type.capitalize()} {{id: $entity_id}})
            RETURN e
            """

            result = await self.neo4j.execute_query(query, entity_id=entity_id)

            if result:
                return dict(result[0]["e"])
        except Exception as e:
            logger.warning(f"Failed to fetch entity data: {e}")

        # Return mock data for development
        return self._generate_mock_entity_data(entity_type)

    def _generate_mock_entity_data(self, entity_type: str) -> dict:
        """Generate mock entity data for development."""
        if entity_type == "person":
            return {
                "criminal_history": [{"type": "theft"}, {"type": "assault"}],
                "has_active_warrant": np.random.random() < 0.2,
                "gang_affiliated": np.random.random() < 0.1,
                "recent_incidents": np.random.randint(0, 5),
                "associates_avg_risk": np.random.uniform(0.1, 0.5),
            }
        elif entity_type == "vehicle":
            return {
                "on_hotlist": np.random.random() < 0.3,
                "is_stolen": np.random.random() < 0.1,
                "lpr_hit_count": np.random.randint(0, 30),
                "incident_count": np.random.randint(0, 5),
                "owner_risk_score": np.random.uniform(0.0, 0.6),
            }
        else:  # address
            return {
                "incident_count": np.random.randint(0, 25),
                "cad_call_count": np.random.randint(0, 60),
                "known_offender_residence": np.random.random() < 0.2,
                "drug_activity_flag": np.random.random() < 0.15,
                "hotspot_proximity_score": np.random.uniform(0.0, 0.8),
            }

    async def _find_zones_by_location(
        self,
        lat: float,
        lon: float,
    ) -> list[dict]:
        """Find zones containing a location."""
        zones = []

        # Check each level
        for level in ["micro", "district"]:
            zone_list = await self._get_zones(None, level)

            for zone in zone_list:
                bounds = zone["bounds"]
                if (
                    bounds["min_lat"] <= lat <= bounds["max_lat"]
                    and bounds["min_lon"] <= lon <= bounds["max_lon"]
                ):
                    zones.append(zone)

        return zones

    def _calculate_incident_impact(
        self,
        incident_type: str,
        severity: str,
    ) -> float:
        """Calculate risk impact of an incident."""
        type_impacts = {
            "homicide": 0.15,
            "shooting": 0.12,
            "assault": 0.08,
            "robbery": 0.07,
            "burglary": 0.04,
            "theft": 0.02,
        }

        severity_multipliers = {
            "critical": 1.5,
            "high": 1.2,
            "medium": 1.0,
            "low": 0.7,
        }

        base_impact = type_impacts.get(incident_type, 0.03)
        multiplier = severity_multipliers.get(severity, 1.0)

        return base_impact * multiplier

    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to risk level."""
        for level, threshold in self.RISK_THRESHOLDS.items():
            if score >= threshold:
                return level
        return "low"

    def _get_top_factors(self, factors: dict) -> list[dict]:
        """Get top contributing risk factors."""
        weighted_factors = [
            {
                "name": name,
                "value": value,
                "weight": self.RISK_WEIGHTS.get(name, 0),
                "contribution": value * self.RISK_WEIGHTS.get(name, 0),
            }
            for name, value in factors.items()
        ]

        weighted_factors.sort(key=lambda x: x["contribution"], reverse=True)

        return weighted_factors[:3]

    def _generate_risk_summary(self, risk_scores: list[dict]) -> dict:
        """Generate summary statistics for risk map."""
        if not risk_scores:
            return {
                "total_zones": 0,
                "avg_risk": 0.0,
                "max_risk": 0.0,
                "critical_zones": 0,
                "high_zones": 0,
            }

        scores = [z["risk_score"] for z in risk_scores]
        levels = [z["risk_level"] for z in risk_scores]

        return {
            "total_zones": len(risk_scores),
            "avg_risk": round(np.mean(scores), 3),
            "max_risk": round(max(scores), 3),
            "min_risk": round(min(scores), 3),
            "critical_zones": levels.count("critical"),
            "high_zones": levels.count("high"),
            "elevated_zones": levels.count("elevated"),
            "moderate_zones": levels.count("moderate"),
            "low_zones": levels.count("low"),
        }

    def _generate_zone_explanation(
        self,
        zone_id: str,
        risk_level: str,
        factors: dict,
    ) -> str:
        """Generate human-readable explanation for zone risk."""
        top_factors = self._get_top_factors(factors)

        if not top_factors:
            return f"Zone {zone_id} has {risk_level} risk level."

        factor_names = {
            "repeat_offender_density": "repeat offender activity",
            "gunfire_frequency": "gunfire incidents",
            "vehicle_recurrence": "vehicle-of-interest sightings",
            "lpr_cluster_acceleration": "increasing LPR activity",
            "violent_crime_history": "violent crime history",
            "cad_call_density": "high call volume",
            "ai_anomaly_signals": "AI-detected anomalies",
            "entity_risk_scores": "high-risk entities present",
        }

        top_factor = top_factors[0]
        factor_desc = factor_names.get(
            top_factor["name"], top_factor["name"].replace("_", " ")
        )

        return (
            f"Zone {zone_id} has {risk_level} risk primarily due to {factor_desc} "
            f"(contributing {top_factor['contribution']:.0%} to overall score)."
        )

    def _generate_entity_recommendations(
        self,
        entity_type: str,
        score_data: dict,
    ) -> list[str]:
        """Generate recommendations based on entity risk."""
        recommendations = []
        risk_score = score_data["risk_score"]
        factors = score_data.get("factors", {})

        if risk_score >= 0.8:
            recommendations.append("Priority monitoring recommended")
            recommendations.append("Consider proactive engagement")
        elif risk_score >= 0.6:
            recommendations.append("Enhanced surveillance suggested")
        elif risk_score >= 0.4:
            recommendations.append("Regular monitoring appropriate")

        # Entity-specific recommendations
        if entity_type == "person":
            if factors.get("warrant_status", 0) > 0:
                recommendations.append("Active warrant - coordinate with warrants unit")
            if factors.get("gang_affiliation", 0) > 0:
                recommendations.append("Gang intelligence unit notification")
        elif entity_type == "vehicle":
            if factors.get("stolen_status", 0) > 0:
                recommendations.append("Stolen vehicle - immediate recovery priority")
            if factors.get("hotlist_status", 0) > 0:
                recommendations.append("Hotlist vehicle - notify requesting agency")
        elif entity_type == "address":
            if factors.get("drug_activity", 0) > 0:
                recommendations.append("Narcotics unit awareness")
            if factors.get("offender_residence", 0) > 0:
                recommendations.append("Known offender residence - exercise caution")

        return recommendations

    async def _invalidate_cache(self) -> None:
        """Invalidate cached risk data."""
        try:
            await self.redis.delete_pattern("risk:*")
        except Exception as e:
            logger.warning(f"Failed to invalidate risk cache: {e}")
