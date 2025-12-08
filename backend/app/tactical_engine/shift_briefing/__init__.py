"""
Shift Briefing Intelligence Pack Builder for G3TI RTCC-UIP.

This module provides shift briefing capabilities including:
- Top zones of concern
- Vehicles of interest
- Persons of interest
- Overnight case developments
- AI anomalies
- Patrol route recommendations
- Heatmap snapshots
- Tactical advisories
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from ...db.elasticsearch import ElasticsearchManager
from ...db.neo4j import Neo4jManager
from ...db.redis import RedisManager

logger = logging.getLogger(__name__)


class ShiftBriefingBuilder:
    """
    Builder for shift briefing intelligence packs.

    Generates comprehensive briefing packages for shift commanders
    and patrol officers with tactical intelligence and recommendations.
    """

    # Shift definitions
    SHIFTS = {
        "A": {
            "name": "Day Shift",
            "start_hour": 7,
            "end_hour": 15,
            "duration_hours": 8,
        },
        "B": {
            "name": "Evening Shift",
            "start_hour": 15,
            "end_hour": 23,
            "duration_hours": 8,
        },
        "C": {
            "name": "Night Shift",
            "start_hour": 23,
            "end_hour": 7,
            "duration_hours": 8,
        },
    }

    # Briefing configuration
    MAX_ZONES_OF_CONCERN = 10
    MAX_VEHICLES_OF_INTEREST = 15
    MAX_PERSONS_OF_INTEREST = 15
    MAX_CASE_DEVELOPMENTS = 10
    MAX_ANOMALIES = 10
    MAX_PATROL_ROUTES = 5

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
        heatmap_engine: Any = None,
        risk_engine: Any = None,
        patrol_optimizer: Any = None,
    ):
        """
        Initialize the Shift Briefing Builder.

        Args:
            neo4j: Neo4j database manager
            es: Elasticsearch manager
            redis: Redis manager for caching
            heatmap_engine: Reference to heatmap engine
            risk_engine: Reference to risk scoring engine
            patrol_optimizer: Reference to patrol optimizer
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis
        self.heatmap_engine = heatmap_engine
        self.risk_engine = risk_engine
        self.patrol_optimizer = patrol_optimizer

        logger.info("ShiftBriefingBuilder initialized")

    async def build_briefing(
        self,
        shift: str,
        include_routes: bool = True,
        include_heatmaps: bool = True,
        district: str | None = None,
    ) -> dict:
        """
        Generate shift briefing intelligence pack.

        Args:
            shift: Shift identifier (A, B, C)
            include_routes: Include patrol route recommendations
            include_heatmaps: Include heatmap snapshots
            district: Optional district filter

        Returns:
            Complete shift briefing package
        """
        logger.info(f"Building briefing for shift {shift}")

        shift_info = self.SHIFTS.get(shift.upper(), self.SHIFTS["A"])
        briefing_id = f"BRIEF-{shift.upper()}-{datetime.utcnow().strftime('%Y%m%d-%H%M')}"

        # Build briefing components
        zones_of_concern = await self._get_zones_of_concern(shift_info, district)
        vehicles_of_interest = await self._get_vehicles_of_interest(district)
        persons_of_interest = await self._get_persons_of_interest(district)
        case_developments = await self._get_case_developments(shift_info)
        ai_anomalies = await self._get_ai_anomalies(shift_info)
        tactical_advisories = await self._generate_tactical_advisories(
            zones_of_concern, vehicles_of_interest, persons_of_interest
        )
        overnight_summary = await self._generate_overnight_summary(shift_info)

        briefing = {
            "briefing_id": briefing_id,
            "shift": {
                "code": shift.upper(),
                "name": shift_info["name"],
                "start_hour": shift_info["start_hour"],
                "end_hour": shift_info["end_hour"],
                "duration_hours": shift_info["duration_hours"],
            },
            "generated_at": datetime.utcnow().isoformat(),
            "valid_until": (
                datetime.utcnow() + timedelta(hours=shift_info["duration_hours"])
            ).isoformat(),
            "zones_of_concern": zones_of_concern,
            "entity_highlights": {
                "vehicles_of_interest": vehicles_of_interest,
                "persons_of_interest": persons_of_interest,
            },
            "case_developments": case_developments,
            "ai_anomalies": ai_anomalies,
            "tactical_advisories": tactical_advisories,
            "overnight_summary": overnight_summary,
        }

        # Add patrol routes if requested
        if include_routes:
            patrol_routes = await self._generate_patrol_routes(
                shift_info, zones_of_concern
            )
            briefing["patrol_routes"] = patrol_routes

        # Add heatmap snapshots if requested
        if include_heatmaps:
            tactical_map = await self._generate_tactical_map(shift_info)
            briefing["tactical_map"] = tactical_map

        # Add statistics
        briefing["statistics"] = self._calculate_briefing_statistics(briefing)

        # Log briefing generation for audit
        await self._log_briefing_generation(briefing_id, shift)

        return briefing

    # ==================== Zones of Concern ====================

    async def _get_zones_of_concern(
        self,
        shift_info: dict,
        district: str | None,
    ) -> list[dict]:
        """Get top zones of concern for the shift."""
        zones = []

        try:
            if self.risk_engine:
                risk_map = await self.risk_engine.generate_risk_map(
                    zone_id=None, level="micro", include_factors=True
                )

                for zone in risk_map.get("zones", [])[:self.MAX_ZONES_OF_CONCERN]:
                    if zone["risk_score"] >= 0.4:  # Only include elevated+ zones
                        zones.append({
                            "zone_id": zone["id"],
                            "risk_score": zone["risk_score"],
                            "risk_level": zone["risk_level"],
                            "center": zone.get("center", {}),
                            "top_factors": zone.get("top_factors", []),
                            "recommendation": self._get_zone_recommendation(zone),
                        })
        except Exception as e:
            logger.warning(f"Failed to get zones of concern: {e}")
            # Generate mock data
            zones = self._generate_mock_zones()

        return zones

    def _get_zone_recommendation(self, zone: dict) -> str:
        """Generate recommendation for a zone."""
        risk_level = zone.get("risk_level", "moderate")

        recommendations = {
            "critical": "Immediate patrol presence required. Consider dedicated unit assignment.",
            "high": "Increased patrol frequency recommended. Monitor for developing situations.",
            "elevated": "Regular patrol checks advised. Be aware of recent activity patterns.",
            "moderate": "Standard patrol coverage. Note for situational awareness.",
        }

        return recommendations.get(risk_level, "Monitor as part of routine patrol.")

    def _generate_mock_zones(self) -> list[dict]:
        """Generate mock zones for development."""
        zones = []
        risk_levels = ["critical", "high", "elevated", "moderate"]

        for i in range(min(5, self.MAX_ZONES_OF_CONCERN)):
            risk_score = 0.9 - (i * 0.15)
            zones.append({
                "zone_id": f"micro_{i}_{np.random.randint(0, 20)}",
                "risk_score": round(risk_score, 2),
                "risk_level": risk_levels[min(i, len(risk_levels) - 1)],
                "center": {
                    "lat": 33.45 + np.random.uniform(-0.05, 0.05),
                    "lon": -112.07 + np.random.uniform(-0.05, 0.05),
                },
                "top_factors": [
                    {"name": "gunfire_frequency", "contribution": 0.3},
                    {"name": "violent_crime_history", "contribution": 0.25},
                ],
                "recommendation": self._get_zone_recommendation(
                    {"risk_level": risk_levels[min(i, len(risk_levels) - 1)]}
                ),
            })

        return zones

    # ==================== Vehicles of Interest ====================

    async def _get_vehicles_of_interest(
        self,
        district: str | None,
    ) -> list[dict]:
        """Get vehicles of interest for the shift."""
        vehicles = []

        try:
            # Query Neo4j for high-risk vehicles
            query = """
            MATCH (v:Vehicle)
            WHERE v.risk_score >= 0.5 OR v.on_hotlist = true OR v.is_stolen = true
            RETURN v.id as id, v.plate as plate, v.make as make, v.model as model,
                   v.color as color, v.risk_score as risk_score,
                   v.on_hotlist as on_hotlist, v.is_stolen as is_stolen,
                   v.last_seen_lat as lat, v.last_seen_lon as lon,
                   v.last_seen_time as last_seen
            ORDER BY v.risk_score DESC
            LIMIT $limit
            """

            results = await self.neo4j.execute_query(
                query, limit=self.MAX_VEHICLES_OF_INTEREST
            )

            for r in results or []:
                vehicles.append({
                    "id": r["id"],
                    "plate": r["plate"],
                    "description": f"{r.get('color', '')} {r.get('make', '')} {r.get('model', '')}".strip(),
                    "risk_score": r.get("risk_score", 0.5),
                    "flags": self._get_vehicle_flags(r),
                    "last_seen": {
                        "lat": r.get("lat"),
                        "lon": r.get("lon"),
                        "time": r.get("last_seen"),
                    },
                    "action": self._get_vehicle_action(r),
                })
        except Exception as e:
            logger.warning(f"Failed to get vehicles of interest: {e}")
            vehicles = self._generate_mock_vehicles()

        return vehicles

    def _get_vehicle_flags(self, vehicle: dict) -> list[str]:
        """Get flags for a vehicle."""
        flags = []
        if vehicle.get("is_stolen"):
            flags.append("STOLEN")
        if vehicle.get("on_hotlist"):
            flags.append("HOTLIST")
        if vehicle.get("risk_score", 0) >= 0.8:
            flags.append("HIGH_RISK")
        return flags

    def _get_vehicle_action(self, vehicle: dict) -> str:
        """Get recommended action for a vehicle."""
        if vehicle.get("is_stolen"):
            return "STOP AND RECOVER - Confirm stolen status before approach"
        if vehicle.get("on_hotlist"):
            return "STOP AND IDENTIFY - Contact requesting agency"
        if vehicle.get("risk_score", 0) >= 0.8:
            return "MONITOR - Associated with high-risk activity"
        return "OBSERVE - Note location and occupants"

    def _generate_mock_vehicles(self) -> list[dict]:
        """Generate mock vehicles for development."""
        vehicles = []
        makes = ["Honda", "Toyota", "Ford", "Chevrolet", "Nissan"]
        colors = ["Black", "White", "Silver", "Blue", "Red"]

        for i in range(min(5, self.MAX_VEHICLES_OF_INTEREST)):
            is_stolen = i == 0
            on_hotlist = i <= 1

            vehicles.append({
                "id": f"VEH-{1000 + i}",
                "plate": f"ABC{1234 + i}",
                "description": f"{np.random.choice(colors)} {np.random.choice(makes)} Sedan",
                "risk_score": round(0.9 - (i * 0.1), 2),
                "flags": (["STOLEN"] if is_stolen else []) + (["HOTLIST"] if on_hotlist else []),
                "last_seen": {
                    "lat": 33.45 + np.random.uniform(-0.05, 0.05),
                    "lon": -112.07 + np.random.uniform(-0.05, 0.05),
                    "time": (datetime.utcnow() - timedelta(hours=np.random.randint(1, 24))).isoformat(),
                },
                "action": "STOP AND RECOVER" if is_stolen else "MONITOR",
            })

        return vehicles

    # ==================== Persons of Interest ====================

    async def _get_persons_of_interest(
        self,
        district: str | None,
    ) -> list[dict]:
        """Get persons of interest for the shift."""
        persons = []

        try:
            # Query Neo4j for high-risk persons
            query = """
            MATCH (p:Person)
            WHERE p.risk_score >= 0.5 OR p.has_active_warrant = true
            RETURN p.id as id, p.name as name, p.dob as dob,
                   p.risk_score as risk_score, p.has_active_warrant as has_warrant,
                   p.gang_affiliated as gang_affiliated,
                   p.last_known_lat as lat, p.last_known_lon as lon
            ORDER BY p.risk_score DESC
            LIMIT $limit
            """

            results = await self.neo4j.execute_query(
                query, limit=self.MAX_PERSONS_OF_INTEREST
            )

            for r in results or []:
                persons.append({
                    "id": r["id"],
                    "name": r.get("name", "Unknown"),
                    "risk_score": r.get("risk_score", 0.5),
                    "flags": self._get_person_flags(r),
                    "last_known_location": {
                        "lat": r.get("lat"),
                        "lon": r.get("lon"),
                    },
                    "action": self._get_person_action(r),
                })
        except Exception as e:
            logger.warning(f"Failed to get persons of interest: {e}")
            persons = self._generate_mock_persons()

        return persons

    def _get_person_flags(self, person: dict) -> list[str]:
        """Get flags for a person."""
        flags = []
        if person.get("has_warrant"):
            flags.append("WARRANT")
        if person.get("gang_affiliated"):
            flags.append("GANG")
        if person.get("risk_score", 0) >= 0.8:
            flags.append("HIGH_RISK")
        return flags

    def _get_person_action(self, person: dict) -> str:
        """Get recommended action for a person."""
        if person.get("has_warrant"):
            return "ARREST - Active warrant. Verify warrant status before contact."
        if person.get("gang_affiliated"):
            return "CAUTION - Known gang affiliation. Exercise officer safety."
        if person.get("risk_score", 0) >= 0.8:
            return "MONITOR - Associated with high-risk activity"
        return "FIELD INTERVIEW - If circumstances warrant"

    def _generate_mock_persons(self) -> list[dict]:
        """Generate mock persons for development."""
        persons = []

        for i in range(min(5, self.MAX_PERSONS_OF_INTEREST)):
            has_warrant = i == 0
            gang_affiliated = i <= 1

            persons.append({
                "id": f"PER-{2000 + i}",
                "name": f"Person {i + 1}",
                "risk_score": round(0.9 - (i * 0.1), 2),
                "flags": (["WARRANT"] if has_warrant else []) + (["GANG"] if gang_affiliated else []),
                "last_known_location": {
                    "lat": 33.45 + np.random.uniform(-0.05, 0.05),
                    "lon": -112.07 + np.random.uniform(-0.05, 0.05),
                },
                "action": "ARREST" if has_warrant else "MONITOR",
            })

        return persons

    # ==================== Case Developments ====================

    async def _get_case_developments(
        self,
        shift_info: dict,
    ) -> list[dict]:
        """Get recent case developments."""
        developments = []

        try:
            # Query Elasticsearch for recent case updates
            query = {
                "bool": {
                    "must": [
                        {"range": {"updated_at": {"gte": "now-12h"}}},
                        {"term": {"has_updates": True}},
                    ]
                }
            }

            results = await self.es.search(
                index="cases", query=query, size=self.MAX_CASE_DEVELOPMENTS
            )

            for hit in results.get("hits", {}).get("hits", []):
                source = hit["_source"]
                developments.append({
                    "case_id": source.get("case_id"),
                    "title": source.get("title", "Untitled Case"),
                    "update_type": source.get("update_type", "general"),
                    "summary": source.get("update_summary", ""),
                    "updated_at": source.get("updated_at"),
                    "priority": source.get("priority", "normal"),
                })
        except Exception as e:
            logger.warning(f"Failed to get case developments: {e}")
            developments = self._generate_mock_case_developments()

        return developments

    def _generate_mock_case_developments(self) -> list[dict]:
        """Generate mock case developments for development."""
        developments = []
        update_types = ["new_evidence", "suspect_identified", "witness_statement", "forensic_result"]

        for i in range(min(3, self.MAX_CASE_DEVELOPMENTS)):
            developments.append({
                "case_id": f"CASE-2025-{1000 + i}",
                "title": f"Investigation Case {i + 1}",
                "update_type": np.random.choice(update_types),
                "summary": "New development in ongoing investigation. Review case file for details.",
                "updated_at": (datetime.utcnow() - timedelta(hours=np.random.randint(1, 12))).isoformat(),
                "priority": "high" if i == 0 else "normal",
            })

        return developments

    # ==================== AI Anomalies ====================

    async def _get_ai_anomalies(
        self,
        shift_info: dict,
    ) -> list[dict]:
        """Get AI-detected anomalies."""
        anomalies = []

        try:
            # Query Elasticsearch for recent anomalies
            query = {
                "bool": {
                    "must": [
                        {"range": {"detected_at": {"gte": "now-24h"}}},
                        {"term": {"type": "anomaly"}},
                    ]
                }
            }

            results = await self.es.search(
                index="ai_anomalies", query=query, size=self.MAX_ANOMALIES
            )

            for hit in results.get("hits", {}).get("hits", []):
                source = hit["_source"]
                anomalies.append({
                    "id": source.get("id"),
                    "type": source.get("anomaly_type", "unknown"),
                    "description": source.get("description", ""),
                    "severity": source.get("severity", "medium"),
                    "location": source.get("location", {}),
                    "detected_at": source.get("detected_at"),
                    "confidence": source.get("confidence", 0.5),
                })
        except Exception as e:
            logger.warning(f"Failed to get AI anomalies: {e}")
            anomalies = self._generate_mock_anomalies()

        return anomalies

    def _generate_mock_anomalies(self) -> list[dict]:
        """Generate mock anomalies for development."""
        anomalies = []
        anomaly_types = ["activity_spike", "pattern_deviation", "unusual_clustering", "temporal_anomaly"]

        for i in range(min(3, self.MAX_ANOMALIES)):
            anomalies.append({
                "id": f"ANOM-{3000 + i}",
                "type": np.random.choice(anomaly_types),
                "description": "AI detected unusual pattern in zone activity",
                "severity": "high" if i == 0 else "medium",
                "location": {
                    "lat": 33.45 + np.random.uniform(-0.05, 0.05),
                    "lon": -112.07 + np.random.uniform(-0.05, 0.05),
                },
                "detected_at": (datetime.utcnow() - timedelta(hours=np.random.randint(1, 24))).isoformat(),
                "confidence": round(0.9 - (i * 0.1), 2),
            })

        return anomalies

    # ==================== Tactical Advisories ====================

    async def _generate_tactical_advisories(
        self,
        zones: list[dict],
        vehicles: list[dict],
        persons: list[dict],
    ) -> list[dict]:
        """Generate tactical advisories based on intelligence."""
        advisories = []

        # Critical zone advisory
        critical_zones = [z for z in zones if z.get("risk_level") == "critical"]
        if critical_zones:
            advisories.append({
                "priority": "critical",
                "type": "zone_alert",
                "title": f"{len(critical_zones)} Critical Risk Zone(s)",
                "description": (
                    f"Critical risk zones identified: "
                    f"{', '.join(z['zone_id'] for z in critical_zones[:3])}. "
                    f"Immediate patrol presence recommended."
                ),
                "action": "Deploy units to critical zones immediately",
            })

        # Stolen vehicle advisory
        stolen_vehicles = [v for v in vehicles if "STOLEN" in v.get("flags", [])]
        if stolen_vehicles:
            advisories.append({
                "priority": "high",
                "type": "vehicle_alert",
                "title": f"{len(stolen_vehicles)} Stolen Vehicle(s) Active",
                "description": (
                    f"Stolen vehicles in area: "
                    f"{', '.join(v['plate'] for v in stolen_vehicles[:3])}. "
                    f"Be alert for these plates."
                ),
                "action": "Stop and recover if observed. Verify stolen status.",
            })

        # Warrant advisory
        warrant_persons = [p for p in persons if "WARRANT" in p.get("flags", [])]
        if warrant_persons:
            advisories.append({
                "priority": "high",
                "type": "person_alert",
                "title": f"{len(warrant_persons)} Active Warrant(s)",
                "description": (
                    "Persons with active warrants may be in area. "
                    "Review person of interest list for details."
                ),
                "action": "Arrest if encountered. Verify warrant status.",
            })

        # High activity advisory
        high_zones = [z for z in zones if z.get("risk_level") in ["high", "critical"]]
        if len(high_zones) >= 3:
            advisories.append({
                "priority": "medium",
                "type": "activity_alert",
                "title": "Elevated Activity Levels",
                "description": (
                    f"{len(high_zones)} zones showing elevated activity. "
                    f"Consider increased patrol frequency in affected areas."
                ),
                "action": "Increase patrol presence in high-activity zones",
            })

        # Default advisory if none generated
        if not advisories:
            advisories.append({
                "priority": "low",
                "type": "general",
                "title": "Normal Activity Levels",
                "description": "No significant tactical concerns at this time.",
                "action": "Maintain standard patrol operations",
            })

        return advisories

    # ==================== Overnight Summary ====================

    async def _generate_overnight_summary(
        self,
        shift_info: dict,
    ) -> str:
        """Generate overnight activity summary."""
        try:
            # Query for incidents in last 12 hours
            query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": "now-12h"}}}]
                }
            }

            # Get incident count
            incident_result = await self.es.count(index="incidents", query=query)
            incident_count = incident_result.get("count", 0)

            # Get significant incidents
            sig_query = {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-12h"}}},
                        {"terms": {"severity": ["high", "critical"]}},
                    ]
                }
            }
            sig_result = await self.es.count(index="incidents", query=sig_query)
            sig_count = sig_result.get("count", 0)

            summary = (
                f"In the past 12 hours, there were {incident_count} total incidents "
                f"reported, including {sig_count} significant incidents requiring "
                f"follow-up. "
            )

            if sig_count > 5:
                summary += "Activity levels were elevated. Review case developments for details."
            elif sig_count > 0:
                summary += "Activity levels were within normal range."
            else:
                summary += "Activity levels were low with no significant incidents."

            return summary
        except Exception as e:
            logger.warning(f"Failed to generate overnight summary: {e}")
            return (
                "Overnight activity summary unavailable. "
                "Review incident logs for recent activity."
            )

    # ==================== Patrol Routes ====================

    async def _generate_patrol_routes(
        self,
        shift_info: dict,
        zones_of_concern: list[dict],
    ) -> list[dict]:
        """Generate patrol route recommendations."""
        routes = []

        try:
            if self.patrol_optimizer:
                # Generate routes for multiple units
                starting_points = [
                    (33.45, -112.07),  # Central
                    (33.42, -112.05),  # South
                    (33.48, -112.10),  # North
                ]

                priority_zones = [z["zone_id"] for z in zones_of_concern[:5]]

                for i, start in enumerate(starting_points[:self.MAX_PATROL_ROUTES]):
                    route = await self.patrol_optimizer.optimize_route(
                        unit=f"Unit{i + 1}",
                        shift=shift_info["name"],
                        starting_point=start,
                        priority_zones=priority_zones,
                    )
                    routes.append(route)
        except Exception as e:
            logger.warning(f"Failed to generate patrol routes: {e}")
            routes = self._generate_mock_routes()

        return routes

    def _generate_mock_routes(self) -> list[dict]:
        """Generate mock patrol routes for development."""
        routes = []

        for i in range(min(3, self.MAX_PATROL_ROUTES)):
            routes.append({
                "unit": f"Unit{i + 1}",
                "route": [
                    {
                        "lat": 33.45 + np.random.uniform(-0.05, 0.05),
                        "lon": -112.07 + np.random.uniform(-0.05, 0.05),
                        "sequence": j + 1,
                        "type": "waypoint",
                    }
                    for j in range(5)
                ],
                "statistics": {
                    "total_distance": round(np.random.uniform(10, 20), 1),
                    "waypoint_count": 5,
                },
            })

        return routes

    # ==================== Tactical Map ====================

    async def _generate_tactical_map(
        self,
        shift_info: dict,
    ) -> dict:
        """Generate tactical map data."""
        try:
            if self.heatmap_engine:
                heatmap = await self.heatmap_engine.generate_current_heatmap(
                    heatmap_type="all",
                    resolution="medium",
                )

                return {
                    "heatmap": heatmap.get("geojson", {}),
                    "clusters": heatmap.get("clusters", []),
                    "hot_zones": heatmap.get("hot_zones", []),
                    "generated_at": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.warning(f"Failed to generate tactical map: {e}")

        return {
            "heatmap": {"type": "FeatureCollection", "features": []},
            "clusters": [],
            "hot_zones": [],
            "generated_at": datetime.utcnow().isoformat(),
        }

    # ==================== Statistics ====================

    def _calculate_briefing_statistics(self, briefing: dict) -> dict:
        """Calculate briefing statistics."""
        zones = briefing.get("zones_of_concern", [])
        vehicles = briefing.get("entity_highlights", {}).get("vehicles_of_interest", [])
        persons = briefing.get("entity_highlights", {}).get("persons_of_interest", [])
        advisories = briefing.get("tactical_advisories", [])

        return {
            "zones_of_concern_count": len(zones),
            "critical_zones": len([z for z in zones if z.get("risk_level") == "critical"]),
            "high_risk_zones": len([z for z in zones if z.get("risk_level") == "high"]),
            "vehicles_of_interest_count": len(vehicles),
            "stolen_vehicles": len([v for v in vehicles if "STOLEN" in v.get("flags", [])]),
            "persons_of_interest_count": len(persons),
            "active_warrants": len([p for p in persons if "WARRANT" in p.get("flags", [])]),
            "critical_advisories": len([a for a in advisories if a.get("priority") == "critical"]),
            "high_advisories": len([a for a in advisories if a.get("priority") == "high"]),
        }

    # ==================== Audit Logging ====================

    async def _log_briefing_generation(
        self,
        briefing_id: str,
        shift: str,
    ) -> None:
        """Log briefing generation for audit trail."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "briefing_generated",
            "briefing_id": briefing_id,
            "shift": shift,
            "module": "shift_briefing",
        }

        try:
            await self.es.index(
                index="tactical_audit_logs",
                document=audit_entry,
            )
        except Exception as e:
            logger.warning(f"Failed to log briefing generation: {e}")
            logger.info(f"AUDIT: {audit_entry}")
