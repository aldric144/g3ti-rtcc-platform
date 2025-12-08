"""
Officer Safety Score Engine

Calculates real-time safety scores for officers based on environmental threats,
historical data, and AI-detected anomalies.
"""

import asyncio
from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import ElasticsearchManager
from app.db.neo4j import Neo4jManager
from app.db.redis import RedisManager

logger = get_logger(__name__)

# Safety score weights
WEIGHTS = {
    "high_risk_zone_proximity": 0.20,
    "recent_gunfire_proximity": 0.20,
    "repeat_offender_proximity": 0.15,
    "vehicle_of_interest_proximity": 0.10,
    "active_cad_hazards": 0.10,
    "known_threats_at_location": 0.10,
    "time_of_day_patterns": 0.10,
    "ai_anomalies": 0.05,
}

# Risk level thresholds
RISK_LEVELS = {
    "critical": 0.8,
    "high": 0.6,
    "elevated": 0.4,
    "moderate": 0.2,
    "low": 0.0,
}


class OfficerSafetyScorer:
    """
    Calculates officer safety scores based on multiple threat factors.

    Inputs:
    - Proximity to high-risk zones (Phase 5)
    - Proximity to recent gunfire
    - Nearby repeat offenders
    - Nearby vehicles-of-interest
    - Active CAD hazards
    - Known threats at location (RMS)
    - Time-of-day crime patterns
    - AI anomalies relevant to vicinity
    """

    def __init__(
        self,
        neo4j: Neo4jManager | None = None,
        es: ElasticsearchManager | None = None,
        redis: RedisManager | None = None,
    ):
        """
        Initialize the safety scorer.

        Args:
            neo4j: Neo4j manager for entity relationships
            es: Elasticsearch manager for historical data
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        logger.info("officer_safety_scorer_initialized")

    async def calculate_score(
        self,
        badge: str,
        lat: float,
        lon: float,
        include_factors: bool = True,
    ) -> dict[str, Any]:
        """
        Calculate safety score for an officer at a location.

        Args:
            badge: Officer badge number
            lat: Current latitude
            lon: Current longitude
            include_factors: Whether to include detailed factor breakdown

        Returns:
            Safety score result with level and factors
        """
        logger.debug(
            "calculating_safety_score",
            badge=badge,
            lat=lat,
            lon=lon,
        )

        # Calculate individual factor scores
        factors = await self._evaluate_all_factors(lat, lon)

        # Calculate weighted total score
        total_score = 0.0
        for factor_name, factor_data in factors.items():
            weight = WEIGHTS.get(factor_name, 0.0)
            total_score += factor_data["score"] * weight

        # Normalize to 0-1 range
        total_score = min(1.0, max(0.0, total_score))

        # Determine risk level
        risk_level = self._get_risk_level(total_score)

        # Build factor descriptions
        factor_descriptions = []
        for _factor_name, factor_data in factors.items():
            if factor_data["score"] > 0.3:  # Only include significant factors
                factor_descriptions.append(factor_data["description"])

        result = {
            "badge": badge,
            "score": round(total_score, 3),
            "level": risk_level,
            "factors": factor_descriptions,
            "location": {"lat": lat, "lon": lon},
            "calculated_at": datetime.utcnow().isoformat(),
        }

        if include_factors:
            result["factor_details"] = {
                name: {
                    "score": round(data["score"], 3),
                    "weight": WEIGHTS.get(name, 0.0),
                    "weighted_score": round(data["score"] * WEIGHTS.get(name, 0.0), 3),
                    "description": data["description"],
                }
                for name, data in factors.items()
            }

        # Log high-risk scores
        if total_score >= RISK_LEVELS["high"]:
            logger.warning(
                "high_safety_score_detected",
                badge=badge,
                score=total_score,
                level=risk_level,
                factors=factor_descriptions,
            )

        return result

    async def _evaluate_all_factors(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, dict[str, Any]]:
        """Evaluate all safety factors for a location."""
        # Run all evaluations concurrently
        results = await asyncio.gather(
            self._evaluate_high_risk_zone_proximity(lat, lon),
            self._evaluate_recent_gunfire_proximity(lat, lon),
            self._evaluate_repeat_offender_proximity(lat, lon),
            self._evaluate_vehicle_of_interest_proximity(lat, lon),
            self._evaluate_active_cad_hazards(lat, lon),
            self._evaluate_known_threats_at_location(lat, lon),
            self._evaluate_time_of_day_patterns(lat, lon),
            self._evaluate_ai_anomalies(lat, lon),
            return_exceptions=True,
        )

        factor_names = [
            "high_risk_zone_proximity",
            "recent_gunfire_proximity",
            "repeat_offender_proximity",
            "vehicle_of_interest_proximity",
            "active_cad_hazards",
            "known_threats_at_location",
            "time_of_day_patterns",
            "ai_anomalies",
        ]

        factors = {}
        for name, result in zip(factor_names, results, strict=False):
            if isinstance(result, Exception):
                logger.warning("factor_evaluation_error", factor=name, error=str(result))
                factors[name] = {"score": 0.0, "description": "Unable to evaluate"}
            else:
                factors[name] = result

        return factors

    async def _evaluate_high_risk_zone_proximity(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Evaluate proximity to high-risk tactical zones."""
        try:
            # Query Phase 5 tactical zones
            # For now, use mock data
            import random

            # Simulate zone proximity check
            in_high_risk = random.random() < 0.2
            distance_to_nearest = random.uniform(0.1, 2.0)

            if in_high_risk:
                score = 0.9
                description = "Currently in high-risk tactical zone"
            elif distance_to_nearest < 0.3:
                score = 0.7
                description = "Within 300m of high-risk zone"
            elif distance_to_nearest < 0.5:
                score = 0.4
                description = "Within 500m of elevated-risk zone"
            else:
                score = 0.1
                description = "No nearby high-risk zones"

            return {"score": score, "description": description}

        except Exception as e:
            logger.error("high_risk_zone_evaluation_error", error=str(e))
            return {"score": 0.0, "description": "Unable to evaluate zone proximity"}

    async def _evaluate_recent_gunfire_proximity(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Evaluate proximity to recent gunfire incidents."""
        try:
            # Query ShotSpotter data from last 24 hours
            # For now, use mock data
            import random

            gunfire_nearby = random.random() < 0.15
            distance = random.uniform(0.1, 1.0) if gunfire_nearby else random.uniform(1.0, 5.0)

            if gunfire_nearby and distance < 0.3:
                score = 0.95
                description = "Recent gunfire within 300m (last 24h)"
            elif gunfire_nearby and distance < 0.6:
                score = 0.7
                description = "Recent gunfire within 600m (last 24h)"
            elif gunfire_nearby:
                score = 0.4
                description = "Gunfire reported within 1km (last 24h)"
            else:
                score = 0.05
                description = "No recent gunfire nearby"

            return {"score": score, "description": description}

        except Exception as e:
            logger.error("gunfire_proximity_evaluation_error", error=str(e))
            return {"score": 0.0, "description": "Unable to evaluate gunfire proximity"}

    async def _evaluate_repeat_offender_proximity(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Evaluate proximity to known repeat offenders."""
        try:
            # Query Neo4j for repeat offenders near location
            # For now, use mock data
            import random

            offenders_nearby = random.randint(0, 3)

            if offenders_nearby >= 2:
                score = 0.8
                description = f"{offenders_nearby} repeat offenders in vicinity"
            elif offenders_nearby == 1:
                score = 0.5
                description = "1 repeat offender residence nearby"
            else:
                score = 0.1
                description = "No known repeat offenders nearby"

            return {"score": score, "description": description}

        except Exception as e:
            logger.error("repeat_offender_evaluation_error", error=str(e))
            return {"score": 0.0, "description": "Unable to evaluate offender proximity"}

    async def _evaluate_vehicle_of_interest_proximity(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Evaluate proximity to vehicles of interest."""
        try:
            # Query LPR data for recent VOI sightings
            # For now, use mock data
            import random

            voi_nearby = random.random() < 0.1

            if voi_nearby:
                score = 0.75
                description = "High-risk vehicle seen nearby recently"
            else:
                score = 0.05
                description = "No vehicles of interest nearby"

            return {"score": score, "description": description}

        except Exception as e:
            logger.error("voi_proximity_evaluation_error", error=str(e))
            return {"score": 0.0, "description": "Unable to evaluate VOI proximity"}

    async def _evaluate_active_cad_hazards(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Evaluate active CAD hazards at location."""
        try:
            # Query CAD for active hazards
            # For now, use mock data
            import random

            hazards = random.randint(0, 2)
            hazard_types = ["armed subject", "domestic violence", "mental health crisis"]

            if hazards >= 2:
                score = 0.85
                description = "Multiple active CAD hazards in area"
            elif hazards == 1:
                hazard_type = random.choice(hazard_types)
                score = 0.6
                description = f"Active CAD hazard: {hazard_type}"
            else:
                score = 0.05
                description = "No active CAD hazards"

            return {"score": score, "description": description}

        except Exception as e:
            logger.error("cad_hazards_evaluation_error", error=str(e))
            return {"score": 0.0, "description": "Unable to evaluate CAD hazards"}

    async def _evaluate_known_threats_at_location(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Evaluate known threats from RMS at location."""
        try:
            # Query RMS for location-based threats
            # For now, use mock data
            import random

            has_history = random.random() < 0.25

            if has_history:
                threat_types = [
                    "Prior weapons offense at address",
                    "History of violence at location",
                    "Known drug activity location",
                ]
                threat = random.choice(threat_types)
                score = 0.7
                description = threat
            else:
                score = 0.05
                description = "No known threats at location"

            return {"score": score, "description": description}

        except Exception as e:
            logger.error("known_threats_evaluation_error", error=str(e))
            return {"score": 0.0, "description": "Unable to evaluate known threats"}

    async def _evaluate_time_of_day_patterns(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Evaluate time-of-day crime patterns."""
        try:
            current_hour = datetime.utcnow().hour

            # Higher risk during late night hours
            if 22 <= current_hour or current_hour < 4:
                score = 0.6
                description = "High-risk time period (late night)"
            elif 18 <= current_hour < 22:
                score = 0.4
                description = "Elevated-risk time period (evening)"
            elif 4 <= current_hour < 7:
                score = 0.3
                description = "Moderate-risk time period (early morning)"
            else:
                score = 0.1
                description = "Lower-risk time period"

            return {"score": score, "description": description}

        except Exception as e:
            logger.error("time_patterns_evaluation_error", error=str(e))
            return {"score": 0.0, "description": "Unable to evaluate time patterns"}

    async def _evaluate_ai_anomalies(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Evaluate AI-detected anomalies in vicinity."""
        try:
            # Query Phase 3 AI anomaly engine
            # For now, use mock data
            import random

            has_anomaly = random.random() < 0.1

            if has_anomaly:
                anomaly_types = [
                    "Unusual activity pattern detected",
                    "Suspicious clustering detected",
                    "Behavioral anomaly in area",
                ]
                anomaly = random.choice(anomaly_types)
                score = 0.8
                description = f"AI anomaly: {anomaly}"
            else:
                score = 0.05
                description = "No AI anomalies detected"

            return {"score": score, "description": description}

        except Exception as e:
            logger.error("ai_anomalies_evaluation_error", error=str(e))
            return {"score": 0.0, "description": "Unable to evaluate AI anomalies"}

    def _get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level string."""
        for level, threshold in sorted(RISK_LEVELS.items(), key=lambda x: -x[1]):
            if score >= threshold:
                return level
        return "low"


# Singleton instance
_safety_scorer: OfficerSafetyScorer | None = None


def get_safety_scorer() -> OfficerSafetyScorer:
    """Get or create the singleton OfficerSafetyScorer instance."""
    global _safety_scorer
    if _safety_scorer is None:
        _safety_scorer = OfficerSafetyScorer()
    return _safety_scorer
