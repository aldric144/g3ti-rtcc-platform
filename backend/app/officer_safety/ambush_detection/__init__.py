"""
Ambush Pattern Detection Module

Uses AI anomaly engine to detect suspicious patterns that may indicate
potential ambush situations for officers.
"""

import asyncio
from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import ElasticsearchManager
from app.db.neo4j import Neo4jManager
from app.db.redis import RedisManager

logger = get_logger(__name__)

# Ambush detection thresholds
THRESHOLDS = {
    "civilian_absence_threshold": 0.7,  # Unusual lack of civilian presence
    "vehicle_circling_threshold": 3,  # Number of passes to trigger
    "weapon_anomaly_threshold": 0.6,  # Weapon-related anomaly score
    "movement_anomaly_threshold": 0.65,  # Multi-point movement anomaly
    "timing_anomaly_threshold": 0.7,  # Coordinated timing anomaly
    "convergence_threshold": 3,  # Number of suspicious entities converging
}


class AmbushDetector:
    """
    Detects potential ambush patterns using AI anomaly analysis.

    Detection logic:
    - Unusual lack of civilian presence in normally busy areas
    - Suspicious LPR vehicle circling
    - Weapon-related anomalies
    - Multi-point movement anomalies
    - Coordinated timing anomalies

    Trigger conditions:
    - Officer routed into a high-risk pattern zone
    - Suspicious entity convergence detected
    """

    def __init__(
        self,
        neo4j: Neo4jManager | None = None,
        es: ElasticsearchManager | None = None,
        redis: RedisManager | None = None,
    ):
        """
        Initialize the ambush detector.

        Args:
            neo4j: Neo4j manager for entity relationships
            es: Elasticsearch manager for historical data
            redis: Redis manager for caching and pub/sub
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        # Track active warnings per officer
        self._active_warnings: dict[str, dict] = {}

        logger.info("ambush_detector_initialized")

    async def check_location(
        self,
        badge: str,
        lat: float,
        lon: float,
        heading: float | None = None,
        destination: tuple[float, float] | None = None,
    ) -> dict[str, Any]:
        """
        Check a location for ambush patterns.

        Args:
            badge: Officer badge number
            lat: Current latitude
            lon: Current longitude
            heading: Current heading (for route analysis)
            destination: Destination coordinates (if en route)

        Returns:
            Ambush check result with warning flag and details
        """
        logger.debug(
            "checking_ambush_patterns",
            badge=badge,
            lat=lat,
            lon=lon,
        )

        # Run all detection checks concurrently
        results = await asyncio.gather(
            self._check_civilian_absence(lat, lon),
            self._check_vehicle_circling(lat, lon),
            self._check_weapon_anomalies(lat, lon),
            self._check_movement_anomalies(lat, lon),
            self._check_timing_anomalies(lat, lon),
            self._check_entity_convergence(lat, lon),
            return_exceptions=True,
        )

        check_names = [
            "civilian_absence",
            "vehicle_circling",
            "weapon_anomalies",
            "movement_anomalies",
            "timing_anomalies",
            "entity_convergence",
        ]

        indicators = {}
        warning_factors = []
        total_risk_score = 0.0

        for name, result in zip(check_names, results, strict=False):
            if isinstance(result, Exception):
                logger.warning("ambush_check_error", check=name, error=str(result))
                indicators[name] = {"detected": False, "score": 0.0}
            else:
                indicators[name] = result
                if result.get("detected"):
                    warning_factors.append(result.get("description", name))
                    total_risk_score += result.get("score", 0.0)

        # Normalize risk score
        total_risk_score = min(1.0, total_risk_score / len(check_names))

        # Determine if warning should be issued
        warning = (
            total_risk_score >= 0.5 or
            len(warning_factors) >= 2 or
            any(
                indicators[name].get("score", 0) >= 0.8
                for name in check_names
            )
        )

        # Check route if destination provided
        route_warning = None
        if destination and warning:
            route_warning = await self._check_route_risk(
                lat, lon, destination[0], destination[1]
            )

        result = {
            "badge": badge,
            "location": {"lat": lat, "lon": lon},
            "warning": warning,
            "risk_score": round(total_risk_score, 3),
            "indicators": indicators,
            "warning_factors": warning_factors,
            "checked_at": datetime.utcnow().isoformat(),
        }

        if warning:
            result["message"] = self._generate_warning_message(warning_factors)
            result["severity"] = "critical" if total_risk_score >= 0.7 else "high"

            # Log warning
            logger.warning(
                "ambush_warning_issued",
                badge=badge,
                risk_score=total_risk_score,
                factors=warning_factors,
            )

        if route_warning:
            result["route_warning"] = route_warning

        # Update active warnings
        if warning:
            self._active_warnings[badge] = result
        elif badge in self._active_warnings:
            del self._active_warnings[badge]

        return result

    async def _check_civilian_absence(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Check for unusual lack of civilian presence."""
        try:
            # Query for expected vs actual civilian activity
            # For now, use mock data
            import random

            # Simulate civilian presence check
            expected_activity = random.uniform(0.5, 1.0)
            actual_activity = random.uniform(0.1, 1.0)

            absence_score = max(0, (expected_activity - actual_activity) / expected_activity)
            detected = absence_score >= THRESHOLDS["civilian_absence_threshold"]

            return {
                "detected": detected,
                "score": absence_score,
                "description": "Unusual lack of civilian presence in normally busy area" if detected else None,
                "expected_activity": expected_activity,
                "actual_activity": actual_activity,
            }
        except Exception as e:
            logger.error("civilian_absence_check_error", error=str(e))
            return {"detected": False, "score": 0.0}

    async def _check_vehicle_circling(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Check for suspicious vehicle circling patterns."""
        try:
            # Query LPR data for repeated passes
            # For now, use mock data
            import random

            # Simulate vehicle circling check
            circling_vehicles = random.choices([0, 0, 0, 1, 2], weights=[70, 15, 8, 5, 2])[0]
            passes = random.randint(2, 6) if circling_vehicles > 0 else 0

            detected = passes >= THRESHOLDS["vehicle_circling_threshold"]
            score = min(1.0, passes / 5) if passes > 0 else 0.0

            return {
                "detected": detected,
                "score": score,
                "description": f"Suspicious vehicle circling detected ({passes} passes)" if detected else None,
                "vehicles_detected": circling_vehicles,
                "max_passes": passes,
            }
        except Exception as e:
            logger.error("vehicle_circling_check_error", error=str(e))
            return {"detected": False, "score": 0.0}

    async def _check_weapon_anomalies(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Check for weapon-related anomalies."""
        try:
            # Query AI anomaly engine for weapon patterns
            # For now, use mock data
            import random

            # Simulate weapon anomaly check
            anomaly_score = random.choices(
                [0.0, 0.2, 0.4, 0.6, 0.8],
                weights=[60, 20, 10, 7, 3]
            )[0]

            detected = anomaly_score >= THRESHOLDS["weapon_anomaly_threshold"]

            return {
                "detected": detected,
                "score": anomaly_score,
                "description": "Weapon-related anomaly detected in area" if detected else None,
                "anomaly_type": "weapon_pattern" if detected else None,
            }
        except Exception as e:
            logger.error("weapon_anomaly_check_error", error=str(e))
            return {"detected": False, "score": 0.0}

    async def _check_movement_anomalies(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Check for multi-point movement anomalies."""
        try:
            # Query for suspicious movement patterns
            # For now, use mock data
            import random

            # Simulate movement anomaly check
            anomaly_score = random.choices(
                [0.0, 0.2, 0.4, 0.65, 0.85],
                weights=[55, 25, 12, 5, 3]
            )[0]

            detected = anomaly_score >= THRESHOLDS["movement_anomaly_threshold"]

            return {
                "detected": detected,
                "score": anomaly_score,
                "description": "Suspicious multi-point movement pattern detected" if detected else None,
                "pattern_type": "coordinated_movement" if detected else None,
            }
        except Exception as e:
            logger.error("movement_anomaly_check_error", error=str(e))
            return {"detected": False, "score": 0.0}

    async def _check_timing_anomalies(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Check for coordinated timing anomalies."""
        try:
            # Query for suspicious timing patterns
            # For now, use mock data
            import random

            # Simulate timing anomaly check
            anomaly_score = random.choices(
                [0.0, 0.2, 0.4, 0.7, 0.9],
                weights=[60, 22, 10, 5, 3]
            )[0]

            detected = anomaly_score >= THRESHOLDS["timing_anomaly_threshold"]

            return {
                "detected": detected,
                "score": anomaly_score,
                "description": "Coordinated timing anomaly detected" if detected else None,
                "pattern_type": "synchronized_activity" if detected else None,
            }
        except Exception as e:
            logger.error("timing_anomaly_check_error", error=str(e))
            return {"detected": False, "score": 0.0}

    async def _check_entity_convergence(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, Any]:
        """Check for suspicious entity convergence."""
        try:
            # Query Neo4j for entity convergence patterns
            # For now, use mock data
            import random

            # Simulate entity convergence check
            converging_entities = random.choices(
                [0, 1, 2, 3, 4],
                weights=[65, 20, 10, 4, 1]
            )[0]

            detected = converging_entities >= THRESHOLDS["convergence_threshold"]
            score = min(1.0, converging_entities / 4) if converging_entities > 0 else 0.0

            entity_types = []
            if converging_entities > 0:
                possible_types = ["repeat_offender", "vehicle_of_interest", "known_associate"]
                entity_types = random.sample(possible_types, min(converging_entities, len(possible_types)))

            return {
                "detected": detected,
                "score": score,
                "description": f"Suspicious entity convergence detected ({converging_entities} entities)" if detected else None,
                "entity_count": converging_entities,
                "entity_types": entity_types,
            }
        except Exception as e:
            logger.error("entity_convergence_check_error", error=str(e))
            return {"detected": False, "score": 0.0}

    async def _check_route_risk(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
    ) -> dict[str, Any]:
        """Check if route passes through high-risk areas."""
        try:
            # Analyze route for ambush-prone segments
            # For now, use mock data
            import random

            high_risk_segments = random.randint(0, 2)

            return {
                "high_risk_segments": high_risk_segments,
                "alternative_route_available": high_risk_segments > 0,
                "recommendation": "Consider alternative route" if high_risk_segments > 0 else "Route appears clear",
            }
        except Exception as e:
            logger.error("route_risk_check_error", error=str(e))
            return {"high_risk_segments": 0, "recommendation": "Unable to analyze route"}

    def _generate_warning_message(self, factors: list[str]) -> str:
        """Generate a warning message from detected factors."""
        if not factors:
            return "Potential ambush indicators detected"

        if len(factors) == 1:
            return f"AMBUSH WARNING: {factors[0]}"

        return f"AMBUSH WARNING: Multiple indicators detected - {', '.join(factors[:3])}"

    async def get_active_warnings(self) -> list[dict[str, Any]]:
        """Get all active ambush warnings."""
        return list(self._active_warnings.values())

    async def clear_warning(self, badge: str) -> bool:
        """Clear an active warning for an officer."""
        if badge in self._active_warnings:
            del self._active_warnings[badge]
            logger.info("ambush_warning_cleared", badge=badge)
            return True
        return False


# Singleton instance
_ambush_detector: AmbushDetector | None = None


def get_ambush_detector() -> AmbushDetector:
    """Get or create the singleton AmbushDetector instance."""
    global _ambush_detector
    if _ambush_detector is None:
        _ambush_detector = AmbushDetector()
    return _ambush_detector
