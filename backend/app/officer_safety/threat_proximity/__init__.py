"""
Threat Proximity Engine

Computes distances to all tactical hazards and provides real-time
radius-based threat alerts for officers.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import ElasticsearchManager
from app.db.neo4j import Neo4jManager
from app.db.redis import RedisManager

logger = get_logger(__name__)

# Default threat radii in meters
THREAT_RADII = {
    "gunfire": 600,
    "vehicle_of_interest": 500,
    "repeat_offender": 300,
    "domestic_violence": 200,
    "ambush_zone": 400,
    "unresolved_weapon": 350,
}

# Threat severity levels
THREAT_SEVERITY = {
    "gunfire": "critical",
    "vehicle_of_interest": "high",
    "repeat_offender": "high",
    "domestic_violence": "elevated",
    "ambush_zone": "critical",
    "unresolved_weapon": "high",
}


class ThreatProximityEngine:
    """
    Computes distances to tactical hazards and generates threat alerts.

    Capabilities:
    - Compute distances to all tactical hazards
    - Real-time radius-based threat alerts
    - Officer -> entity -> incident graph evaluation via Neo4j

    Threat types evaluated:
    - Gunfire radius (600m default)
    - Vehicle-of-interest last sighting radius
    - Repeat offender proximity
    - Domestic violence history at address
    - Ambush-prone zones (Phase 3 anomalies)
    - Unresolved weapons (NESS ballistic IDs)
    """

    def __init__(
        self,
        neo4j: Neo4jManager | None = None,
        es: ElasticsearchManager | None = None,
        redis: RedisManager | None = None,
    ):
        """
        Initialize the threat proximity engine.

        Args:
            neo4j: Neo4j manager for entity relationships
            es: Elasticsearch manager for historical data
            redis: Redis manager for caching and pub/sub
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        # Track active threats per officer
        self._active_threats: dict[str, list[dict]] = {}

        logger.info("threat_proximity_engine_initialized")

    async def evaluate_threats(
        self,
        badge: str,
        lat: float,
        lon: float,
        custom_radii: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate all threats for an officer at a location.

        Args:
            badge: Officer badge number
            lat: Current latitude
            lon: Current longitude
            custom_radii: Optional custom threat radii

        Returns:
            Dictionary with threats and alerts
        """
        logger.debug(
            "evaluating_threats",
            badge=badge,
            lat=lat,
            lon=lon,
        )

        radii = {**THREAT_RADII, **(custom_radii or {})}

        # Evaluate all threat types concurrently
        results = await asyncio.gather(
            self._check_gunfire_threats(lat, lon, radii["gunfire"]),
            self._check_vehicle_threats(lat, lon, radii["vehicle_of_interest"]),
            self._check_repeat_offender_threats(lat, lon, radii["repeat_offender"]),
            self._check_domestic_violence_threats(lat, lon, radii["domestic_violence"]),
            self._check_ambush_zone_threats(lat, lon, radii["ambush_zone"]),
            self._check_weapon_threats(lat, lon, radii["unresolved_weapon"]),
            return_exceptions=True,
        )

        threat_types = [
            "gunfire",
            "vehicle_of_interest",
            "repeat_offender",
            "domestic_violence",
            "ambush_zone",
            "unresolved_weapon",
        ]

        all_threats = []
        for threat_type, result in zip(threat_types, results, strict=False):
            if isinstance(result, Exception):
                logger.warning(
                    "threat_evaluation_error",
                    threat_type=threat_type,
                    error=str(result),
                )
            elif result:
                all_threats.extend(result)

        # Sort by distance
        all_threats.sort(key=lambda x: x.get("distance_m", float("inf")))

        # Check for new threats (for alerting)
        new_threats = self._identify_new_threats(badge, all_threats)
        resolved_threats = self._identify_resolved_threats(badge, all_threats)

        # Update active threats
        self._active_threats[badge] = all_threats

        # Generate alerts for new threats
        alerts = []
        for threat in new_threats:
            alerts.append({
                "type": "threat_alert",
                "threat_type": threat["type"],
                "severity": threat.get("severity", "elevated"),
                "message": threat.get("description", f"New {threat['type']} threat detected"),
                "distance_m": threat.get("distance_m"),
                "location": threat.get("location"),
                "timestamp": datetime.utcnow().isoformat(),
            })

        for threat in resolved_threats:
            alerts.append({
                "type": "threat_resolved",
                "threat_type": threat["type"],
                "message": f"{threat['type']} threat no longer in proximity",
                "timestamp": datetime.utcnow().isoformat(),
            })

        return {
            "badge": badge,
            "location": {"lat": lat, "lon": lon},
            "threats": all_threats,
            "threat_count": len(all_threats),
            "alerts": alerts,
            "evaluated_at": datetime.utcnow().isoformat(),
        }

    async def _check_gunfire_threats(
        self,
        lat: float,
        lon: float,
        radius_m: float,
    ) -> list[dict[str, Any]]:
        """Check for recent gunfire within radius."""
        threats = []

        try:
            # Query ShotSpotter data
            # For now, use mock data
            import random

            if random.random() < 0.15:
                distance = random.uniform(100, radius_m)
                threats.append({
                    "id": f"gunfire-{random.randint(1000, 9999)}",
                    "type": "gunfire",
                    "severity": THREAT_SEVERITY["gunfire"],
                    "description": f"Gunfire detected {int(distance)}m away (last 24h)",
                    "distance_m": distance,
                    "location": {
                        "lat": lat + random.uniform(-0.005, 0.005),
                        "lon": lon + random.uniform(-0.005, 0.005),
                    },
                    "timestamp": (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat(),
                    "rounds_detected": random.randint(1, 8),
                })
        except Exception as e:
            logger.error("gunfire_threat_check_error", error=str(e))

        return threats

    async def _check_vehicle_threats(
        self,
        lat: float,
        lon: float,
        radius_m: float,
    ) -> list[dict[str, Any]]:
        """Check for vehicles of interest within radius."""
        threats = []

        try:
            # Query LPR data
            # For now, use mock data
            import random

            if random.random() < 0.1:
                distance = random.uniform(50, radius_m)
                plate = f"ABC{random.randint(100, 999)}"
                reasons = ["Stolen vehicle", "Wanted suspect vehicle", "BOLO vehicle"]

                threats.append({
                    "id": f"voi-{random.randint(1000, 9999)}",
                    "type": "vehicle_of_interest",
                    "severity": THREAT_SEVERITY["vehicle_of_interest"],
                    "description": f"{random.choice(reasons)} ({plate}) seen {int(distance)}m away",
                    "distance_m": distance,
                    "location": {
                        "lat": lat + random.uniform(-0.004, 0.004),
                        "lon": lon + random.uniform(-0.004, 0.004),
                    },
                    "plate": plate,
                    "reason": random.choice(reasons),
                    "last_seen": (datetime.utcnow() - timedelta(minutes=random.randint(5, 120))).isoformat(),
                })
        except Exception as e:
            logger.error("vehicle_threat_check_error", error=str(e))

        return threats

    async def _check_repeat_offender_threats(
        self,
        lat: float,
        lon: float,
        radius_m: float,
    ) -> list[dict[str, Any]]:
        """Check for repeat offenders within radius."""
        threats = []

        try:
            # Query Neo4j for repeat offenders
            # For now, use mock data
            import random

            num_offenders = random.choices([0, 0, 0, 1, 1, 2], weights=[40, 20, 15, 15, 7, 3])[0]

            for _ in range(num_offenders):
                distance = random.uniform(50, radius_m)
                offense_types = ["violent crime", "weapons offense", "assault", "robbery"]

                threats.append({
                    "id": f"offender-{random.randint(1000, 9999)}",
                    "type": "repeat_offender",
                    "severity": THREAT_SEVERITY["repeat_offender"],
                    "description": f"Repeat offender ({random.choice(offense_types)}) residence {int(distance)}m away",
                    "distance_m": distance,
                    "location": {
                        "lat": lat + random.uniform(-0.003, 0.003),
                        "lon": lon + random.uniform(-0.003, 0.003),
                    },
                    "offense_history": random.choice(offense_types),
                    "risk_score": random.uniform(0.6, 0.95),
                })
        except Exception as e:
            logger.error("repeat_offender_threat_check_error", error=str(e))

        return threats

    async def _check_domestic_violence_threats(
        self,
        lat: float,
        lon: float,
        radius_m: float,
    ) -> list[dict[str, Any]]:
        """Check for domestic violence history at nearby addresses."""
        threats = []

        try:
            # Query RMS for DV history
            # For now, use mock data
            import random

            if random.random() < 0.2:
                distance = random.uniform(20, radius_m)

                threats.append({
                    "id": f"dv-{random.randint(1000, 9999)}",
                    "type": "domestic_violence",
                    "severity": THREAT_SEVERITY["domestic_violence"],
                    "description": f"DV history at address {int(distance)}m away",
                    "distance_m": distance,
                    "location": {
                        "lat": lat + random.uniform(-0.002, 0.002),
                        "lon": lon + random.uniform(-0.002, 0.002),
                    },
                    "incident_count": random.randint(1, 5),
                    "weapons_involved": random.random() < 0.3,
                })
        except Exception as e:
            logger.error("dv_threat_check_error", error=str(e))

        return threats

    async def _check_ambush_zone_threats(
        self,
        lat: float,
        lon: float,
        radius_m: float,
    ) -> list[dict[str, Any]]:
        """Check for ambush-prone zones from AI anomalies."""
        threats = []

        try:
            # Query Phase 3 AI anomaly engine
            # For now, use mock data
            import random

            if random.random() < 0.05:
                distance = random.uniform(50, radius_m)

                threats.append({
                    "id": f"ambush-{random.randint(1000, 9999)}",
                    "type": "ambush_zone",
                    "severity": THREAT_SEVERITY["ambush_zone"],
                    "description": f"AI-detected ambush-prone zone {int(distance)}m away",
                    "distance_m": distance,
                    "location": {
                        "lat": lat + random.uniform(-0.003, 0.003),
                        "lon": lon + random.uniform(-0.003, 0.003),
                    },
                    "confidence": random.uniform(0.7, 0.95),
                    "anomaly_type": "suspicious_clustering",
                })
        except Exception as e:
            logger.error("ambush_zone_threat_check_error", error=str(e))

        return threats

    async def _check_weapon_threats(
        self,
        lat: float,
        lon: float,
        radius_m: float,
    ) -> list[dict[str, Any]]:
        """Check for unresolved weapons from NESS ballistics."""
        threats = []

        try:
            # Query NESS ballistic data
            # For now, use mock data
            import random

            if random.random() < 0.08:
                distance = random.uniform(50, radius_m)

                threats.append({
                    "id": f"weapon-{random.randint(1000, 9999)}",
                    "type": "unresolved_weapon",
                    "severity": THREAT_SEVERITY["unresolved_weapon"],
                    "description": f"Unresolved weapon linked to location {int(distance)}m away",
                    "distance_m": distance,
                    "location": {
                        "lat": lat + random.uniform(-0.003, 0.003),
                        "lon": lon + random.uniform(-0.003, 0.003),
                    },
                    "weapon_type": random.choice(["handgun", "rifle", "shotgun"]),
                    "ballistic_match": True,
                })
        except Exception as e:
            logger.error("weapon_threat_check_error", error=str(e))

        return threats

    def _identify_new_threats(
        self,
        badge: str,
        current_threats: list[dict],
    ) -> list[dict]:
        """Identify threats that are new since last check."""
        previous_threats = self._active_threats.get(badge, [])
        previous_ids = {t.get("id") for t in previous_threats}

        new_threats = [
            t for t in current_threats
            if t.get("id") not in previous_ids
        ]

        return new_threats

    def _identify_resolved_threats(
        self,
        badge: str,
        current_threats: list[dict],
    ) -> list[dict]:
        """Identify threats that have been resolved since last check."""
        previous_threats = self._active_threats.get(badge, [])
        current_ids = {t.get("id") for t in current_threats}

        resolved_threats = [
            t for t in previous_threats
            if t.get("id") not in current_ids
        ]

        return resolved_threats

    async def get_threats_in_area(
        self,
        lat: float,
        lon: float,
        radius_km: float = 1.0,
    ) -> list[dict[str, Any]]:
        """
        Get all threats in an area (for map display).

        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Search radius in kilometers

        Returns:
            List of all threats in the area
        """
        radius_m = radius_km * 1000

        # Get all threat types
        results = await asyncio.gather(
            self._check_gunfire_threats(lat, lon, radius_m),
            self._check_vehicle_threats(lat, lon, radius_m),
            self._check_repeat_offender_threats(lat, lon, radius_m),
            self._check_domestic_violence_threats(lat, lon, radius_m),
            self._check_ambush_zone_threats(lat, lon, radius_m),
            self._check_weapon_threats(lat, lon, radius_m),
            return_exceptions=True,
        )

        all_threats = []
        for result in results:
            if not isinstance(result, Exception) and result:
                all_threats.extend(result)

        return all_threats


# Singleton instance
_threat_engine: ThreatProximityEngine | None = None


def get_threat_engine() -> ThreatProximityEngine:
    """Get or create the singleton ThreatProximityEngine instance."""
    global _threat_engine
    if _threat_engine is None:
        _threat_engine = ThreatProximityEngine()
    return _threat_engine
