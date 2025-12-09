"""
Scene Intelligence Engine

Provides comprehensive scene intelligence for field operations,
including RTCC Field Packets with location history, known associates,
weapons, vehicles, and tactical recommendations.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import ElasticsearchManager
from app.db.neo4j import Neo4jManager
from app.db.redis import RedisManager

logger = get_logger(__name__)


class SceneIntelligenceEngine:
    """
    Provides comprehensive scene intelligence for officers.

    Given an address, incident, or officer on-scene:
    - Auto-collect relevant RMS/CAD history
    - Identify nearby offenders
    - Identify weapons associated with location
    - Show LPR hits on nearby streets
    - Provide RTCC Field Packet
    """

    def __init__(
        self,
        neo4j: Neo4jManager | None = None,
        es: ElasticsearchManager | None = None,
        redis: RedisManager | None = None,
    ):
        """
        Initialize the scene intelligence engine.

        Args:
            neo4j: Neo4j manager for entity relationships
            es: Elasticsearch manager for historical data
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        logger.info("scene_intelligence_engine_initialized")

    async def get_intelligence(
        self,
        address: str | None = None,
        incident_id: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """
        Get comprehensive scene intelligence.

        Args:
            address: Street address
            incident_id: Incident ID
            lat: Latitude (if no address)
            lon: Longitude (if no address)

        Returns:
            RTCC Field Packet with comprehensive scene intelligence
        """
        logger.info(
            "generating_scene_intelligence",
            address=address,
            incident_id=incident_id,
            lat=lat,
            lon=lon,
        )

        # Resolve location
        location = await self._resolve_location(address, incident_id, lat, lon)

        if not location:
            return {
                "error": "Unable to resolve location",
                "address": address,
                "incident_id": incident_id,
            }

        # Gather all intelligence concurrently
        results = await asyncio.gather(
            self._gather_rms_history(location),
            self._gather_cad_history(location),
            self._gather_known_associates(location),
            self._gather_weapons_info(location),
            self._gather_lpr_hits(location),
            self._gather_prior_violence(location),
            self._gather_nearby_offenders(location),
            return_exceptions=True,
        )

        intel_types = [
            "rms_history",
            "cad_history",
            "known_associates",
            "weapons_associated",
            "lpr_hits",
            "prior_violence",
            "nearby_offenders",
        ]

        intelligence = {}
        for intel_type, result in zip(intel_types, results, strict=False):
            if isinstance(result, Exception):
                logger.warning("intel_gathering_error", type=intel_type, error=str(result))
                intelligence[intel_type] = []
            else:
                intelligence[intel_type] = result

        # Calculate risk level
        risk_level = self._calculate_risk_level(intelligence)

        # Generate recommendations
        recommendations = self._generate_recommendations(intelligence, risk_level)

        # Build RTCC Field Packet
        field_packet = {
            "packet_id": f"FP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "location": location,
            "generated_at": datetime.utcnow().isoformat(),
            "risk_level": risk_level,
            "history": intelligence.get("rms_history", []) + intelligence.get("cad_history", []),
            "known_associates": intelligence.get("known_associates", []),
            "prior_violence": bool(intelligence.get("prior_violence")),
            "weapons_associated": intelligence.get("weapons_associated", []),
            "vehicles_of_interest": intelligence.get("lpr_hits", []),
            "nearby_offenders": intelligence.get("nearby_offenders", []),
            "recommendations": recommendations,
            "summary": self._generate_summary(intelligence, risk_level),
        }

        return field_packet

    async def _resolve_location(
        self,
        address: str | None,
        incident_id: str | None,
        lat: float | None,
        lon: float | None,
    ) -> dict[str, Any] | None:
        """Resolve location from various inputs."""
        if lat is not None and lon is not None:
            return {
                "lat": lat,
                "lon": lon,
                "address": address or f"{lat}, {lon}",
                "source": "coordinates",
            }

        if address:
            # Geocode address (mock for now)
            import random
            return {
                "lat": 33.45 + random.uniform(-0.05, 0.05),
                "lon": -112.07 + random.uniform(-0.05, 0.05),
                "address": address,
                "source": "geocoded",
            }

        if incident_id:
            # Look up incident location (mock for now)
            import random
            return {
                "lat": 33.45 + random.uniform(-0.05, 0.05),
                "lon": -112.07 + random.uniform(-0.05, 0.05),
                "address": f"Incident {incident_id} Location",
                "incident_id": incident_id,
                "source": "incident",
            }

        return None

    async def _gather_rms_history(
        self,
        location: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Gather RMS report history for location."""
        try:
            # Query RMS data
            # For now, use mock data
            import random

            history = []
            num_reports = random.randint(0, 5)

            report_types = [
                "Assault", "Burglary", "Theft", "Domestic Violence",
                "Drug Activity", "Weapons Offense", "Robbery", "Vandalism"
            ]

            for _ in range(num_reports):
                days_ago = random.randint(1, 365)
                history.append({
                    "report_id": f"RMS-{random.randint(10000, 99999)}",
                    "type": random.choice(report_types),
                    "date": (datetime.utcnow() - timedelta(days=days_ago)).isoformat(),
                    "summary": f"Report filed for {random.choice(report_types).lower()} at location",
                    "source": "RMS",
                })

            return sorted(history, key=lambda x: x["date"], reverse=True)

        except Exception as e:
            logger.error("rms_history_error", error=str(e))
            return []

    async def _gather_cad_history(
        self,
        location: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Gather CAD call history for location."""
        try:
            # Query CAD data
            # For now, use mock data
            import random

            history = []
            num_calls = random.randint(0, 8)

            call_types = [
                "Disturbance", "Suspicious Activity", "Welfare Check",
                "Domestic", "Noise Complaint", "Trespass", "Alarm",
                "Medical", "Traffic Stop", "Assault in Progress"
            ]

            for _ in range(num_calls):
                days_ago = random.randint(1, 180)
                history.append({
                    "call_id": f"CAD-{random.randint(100000, 999999)}",
                    "type": random.choice(call_types),
                    "date": (datetime.utcnow() - timedelta(days=days_ago)).isoformat(),
                    "disposition": random.choice(["Report Taken", "Cleared", "Arrest Made", "Gone on Arrival"]),
                    "source": "CAD",
                })

            return sorted(history, key=lambda x: x["date"], reverse=True)

        except Exception as e:
            logger.error("cad_history_error", error=str(e))
            return []

    async def _gather_known_associates(
        self,
        location: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Gather known associates linked to location."""
        try:
            # Query Neo4j for associates
            # For now, use mock data
            import random

            associates = []
            num_associates = random.randint(0, 4)

            for i in range(num_associates):
                associates.append({
                    "person_id": f"P-{random.randint(10000, 99999)}",
                    "name": f"Associate {i + 1}",
                    "relationship": random.choice(["Resident", "Frequent Visitor", "Known Associate"]),
                    "risk_score": round(random.uniform(0.2, 0.9), 2),
                    "prior_offenses": random.randint(0, 5),
                    "active_warrants": random.random() < 0.2,
                })

            return sorted(associates, key=lambda x: x["risk_score"], reverse=True)

        except Exception as e:
            logger.error("known_associates_error", error=str(e))
            return []

    async def _gather_weapons_info(
        self,
        location: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Gather weapons associated with location."""
        try:
            # Query NESS and RMS for weapons
            # For now, use mock data
            import random

            weapons = []
            has_weapons = random.random() < 0.3

            if has_weapons:
                num_weapons = random.randint(1, 3)
                weapon_types = ["Handgun", "Rifle", "Shotgun", "Knife"]

                for _ in range(num_weapons):
                    weapons.append({
                        "weapon_id": f"W-{random.randint(1000, 9999)}",
                        "type": random.choice(weapon_types),
                        "caliber": random.choice(["9mm", ".45 ACP", ".223", "12 gauge", None]),
                        "recovered": random.random() < 0.4,
                        "ballistic_match": random.random() < 0.2,
                        "last_associated": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat(),
                    })

            return weapons

        except Exception as e:
            logger.error("weapons_info_error", error=str(e))
            return []

    async def _gather_lpr_hits(
        self,
        location: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Gather LPR hits on nearby streets."""
        try:
            # Query LPR data
            # For now, use mock data
            import random

            hits = []
            num_hits = random.randint(0, 3)

            for _ in range(num_hits):
                hours_ago = random.randint(1, 72)
                hits.append({
                    "plate": f"ABC{random.randint(100, 999)}",
                    "vehicle_description": f"{random.choice(['Black', 'White', 'Silver', 'Red'])} {random.choice(['Sedan', 'SUV', 'Truck', 'Coupe'])}",
                    "alert_type": random.choice(["Stolen", "BOLO", "Wanted", "Expired Registration"]),
                    "last_seen": (datetime.utcnow() - timedelta(hours=hours_ago)).isoformat(),
                    "distance_m": random.randint(50, 500),
                })

            return sorted(hits, key=lambda x: x["last_seen"], reverse=True)

        except Exception as e:
            logger.error("lpr_hits_error", error=str(e))
            return []

    async def _gather_prior_violence(
        self,
        location: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Gather prior violence incidents at location."""
        try:
            # Query RMS for violence history
            # For now, use mock data
            import random

            violence = []
            has_violence = random.random() < 0.25

            if has_violence:
                num_incidents = random.randint(1, 3)
                violence_types = [
                    "Assault", "Domestic Violence", "Aggravated Assault",
                    "Battery", "Armed Robbery", "Shooting"
                ]

                for _ in range(num_incidents):
                    days_ago = random.randint(30, 730)
                    violence.append({
                        "incident_id": f"V-{random.randint(10000, 99999)}",
                        "type": random.choice(violence_types),
                        "date": (datetime.utcnow() - timedelta(days=days_ago)).isoformat(),
                        "weapons_involved": random.random() < 0.4,
                        "injuries": random.random() < 0.3,
                    })

            return violence

        except Exception as e:
            logger.error("prior_violence_error", error=str(e))
            return []

    async def _gather_nearby_offenders(
        self,
        location: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Gather nearby registered offenders."""
        try:
            # Query for nearby offenders
            # For now, use mock data
            import random

            offenders = []
            num_offenders = random.randint(0, 3)

            for _ in range(num_offenders):
                offenders.append({
                    "offender_id": f"OFF-{random.randint(10000, 99999)}",
                    "offense_type": random.choice(["Violent Crime", "Sex Offense", "Drug Offense", "Property Crime"]),
                    "distance_m": random.randint(100, 500),
                    "risk_level": random.choice(["high", "moderate", "low"]),
                    "supervision_status": random.choice(["Probation", "Parole", "None"]),
                })

            return sorted(offenders, key=lambda x: x["distance_m"])

        except Exception as e:
            logger.error("nearby_offenders_error", error=str(e))
            return []

    def _calculate_risk_level(
        self,
        intelligence: dict[str, Any],
    ) -> str:
        """Calculate overall risk level from gathered intelligence."""
        risk_score = 0.0

        # Prior violence is a major factor
        if intelligence.get("prior_violence"):
            risk_score += 0.3

        # Weapons associated
        weapons = intelligence.get("weapons_associated", [])
        if weapons:
            risk_score += 0.2 * min(len(weapons), 3) / 3

        # Known associates with high risk
        associates = intelligence.get("known_associates", [])
        high_risk_associates = [a for a in associates if a.get("risk_score", 0) > 0.7]
        if high_risk_associates:
            risk_score += 0.15 * min(len(high_risk_associates), 2) / 2

        # Active warrants
        warrants = [a for a in associates if a.get("active_warrants")]
        if warrants:
            risk_score += 0.2

        # Nearby offenders
        offenders = intelligence.get("nearby_offenders", [])
        high_risk_offenders = [o for o in offenders if o.get("risk_level") == "high"]
        if high_risk_offenders:
            risk_score += 0.1 * min(len(high_risk_offenders), 2) / 2

        # LPR hits
        lpr_hits = intelligence.get("lpr_hits", [])
        stolen_vehicles = [h for h in lpr_hits if h.get("alert_type") == "Stolen"]
        if stolen_vehicles:
            risk_score += 0.15

        # Determine level
        if risk_score >= 0.7:
            return "critical"
        elif risk_score >= 0.5:
            return "high"
        elif risk_score >= 0.3:
            return "elevated"
        elif risk_score >= 0.15:
            return "moderate"
        else:
            return "low"

    def _generate_recommendations(
        self,
        intelligence: dict[str, Any],
        risk_level: str,
    ) -> list[str]:
        """Generate tactical recommendations based on intelligence."""
        recommendations = []

        if risk_level in ["critical", "high"]:
            recommendations.append("Request backup before approach")

        if intelligence.get("prior_violence"):
            recommendations.append("History of violence at location - exercise extreme caution")

        weapons = intelligence.get("weapons_associated", [])
        if weapons:
            weapon_types = list({w.get("type") for w in weapons})
            recommendations.append(f"Weapons associated with location: {', '.join(weapon_types)}")

        associates = intelligence.get("known_associates", [])
        warrants = [a for a in associates if a.get("active_warrants")]
        if warrants:
            recommendations.append(f"{len(warrants)} individual(s) with active warrants may be present")

        lpr_hits = intelligence.get("lpr_hits", [])
        if lpr_hits:
            recommendations.append("Vehicle(s) of interest recently seen nearby")

        offenders = intelligence.get("nearby_offenders", [])
        if offenders:
            recommendations.append(f"{len(offenders)} registered offender(s) in vicinity")

        if not recommendations:
            recommendations.append("No significant threats identified - standard precautions apply")

        return recommendations

    def _generate_summary(
        self,
        intelligence: dict[str, Any],
        risk_level: str,
    ) -> str:
        """Generate a brief summary of the intelligence."""
        parts = []

        parts.append(f"Risk Level: {risk_level.upper()}")

        history_count = len(intelligence.get("rms_history", [])) + len(intelligence.get("cad_history", []))
        if history_count > 0:
            parts.append(f"{history_count} prior calls/reports")

        if intelligence.get("prior_violence"):
            parts.append("PRIOR VIOLENCE")

        weapons = intelligence.get("weapons_associated", [])
        if weapons:
            parts.append(f"{len(weapons)} weapon(s) associated")

        associates = intelligence.get("known_associates", [])
        if associates:
            parts.append(f"{len(associates)} known associate(s)")

        return " | ".join(parts)


# Singleton instance
_scene_intel: SceneIntelligenceEngine | None = None


def get_scene_intel() -> SceneIntelligenceEngine:
    """Get or create the singleton SceneIntelligenceEngine instance."""
    global _scene_intel
    if _scene_intel is None:
        _scene_intel = SceneIntelligenceEngine()
    return _scene_intel
