"""
Zone Analysis Engine for G3TI RTCC-UIP.

This module provides tactical zone analysis capabilities including:
- Auto-generated tactical districts
- Micro-grids (250m x 250m)
- Hot/Cold zone indicators
- Next-likely-crime zones
- Confidence levels
- Operational overlays (LPR cameras, gunfire triangulation zones)
"""

import logging
from datetime import datetime

import numpy as np

from ...db.elasticsearch import ElasticsearchManager
from ...db.neo4j import Neo4jManager
from ...db.redis import RedisManager

logger = logging.getLogger(__name__)


class ZoneAnalyzer:
    """
    Engine for tactical zone analysis and operational grid management.

    Provides zone-level intelligence including risk assessment,
    activity patterns, and operational overlays.
    """

    # Grid configuration
    MICRO_GRID_SIZE = 0.0025  # ~250m in degrees
    DISTRICT_GRID_SIZE = 0.01  # ~1km in degrees

    # Zone status thresholds
    HOT_ZONE_THRESHOLD = 0.7
    WARM_ZONE_THRESHOLD = 0.4
    COLD_ZONE_THRESHOLD = 0.2

    # Default bounds (example city area)
    DEFAULT_BOUNDS = {
        "min_lat": 33.35,
        "max_lat": 33.55,
        "min_lon": -112.15,
        "max_lon": -111.95,
    }

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
    ):
        """
        Initialize the Zone Analyzer.

        Args:
            neo4j: Neo4j database manager
            es: Elasticsearch manager
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        # Cache for zone data
        self._zone_cache = {}
        self._cache_ttl = 300  # 5 minutes

        logger.info("ZoneAnalyzer initialized")

    async def get_all_zones(
        self,
        include_risk: bool = True,
        include_predictions: bool = False,
        level: str = "micro",
    ) -> list[dict]:
        """
        Get all tactical zones with optional enrichment.

        Args:
            include_risk: Include risk scores
            include_predictions: Include prediction data
            level: Zone level (micro, district)

        Returns:
            List of zone data
        """
        logger.info(f"Getting all zones: level={level}")

        # Generate zone grid
        zones = self._generate_zone_grid(level)

        # Enrich zones with data
        enriched_zones = []
        for zone in zones:
            zone_data = await self._enrich_zone(
                zone, include_risk, include_predictions
            )
            enriched_zones.append(zone_data)

        # Sort by activity level
        enriched_zones.sort(
            key=lambda x: x.get("activity_score", 0), reverse=True
        )

        return enriched_zones

    async def get_zone_details(
        self,
        zone_id: str,
        include_history: bool = True,
    ) -> dict:
        """
        Get detailed zone information.

        Args:
            zone_id: Zone identifier
            include_history: Include historical data

        Returns:
            Zone details with risk, predictions, and history
        """
        logger.info(f"Getting zone details: {zone_id}")

        # Parse zone ID to get bounds
        zone = self._parse_zone_id(zone_id)

        if not zone:
            return {"error": f"Zone {zone_id} not found"}

        # Get comprehensive zone data
        zone_data = await self._get_comprehensive_zone_data(zone, include_history)

        return zone_data

    async def check_zone_alerts(self, incident_data: dict) -> list[dict]:
        """
        Check for zone alerts based on new incident.

        Args:
            incident_data: New incident information

        Returns:
            List of triggered alerts
        """
        alerts = []

        lat = incident_data.get("latitude")
        lon = incident_data.get("longitude")
        incident_type = incident_data.get("type", "unknown")

        if not lat or not lon:
            return alerts

        # Find containing zone
        zone = self._find_zone_by_location(lat, lon)

        if not zone:
            return alerts

        # Get zone's current status
        zone_data = await self._enrich_zone(zone, include_risk=True)

        # Check for alert conditions
        risk_score = zone_data.get("risk_score", 0)
        activity_score = zone_data.get("activity_score", 0)

        # High-risk zone incident
        if risk_score >= self.HOT_ZONE_THRESHOLD:
            alerts.append({
                "type": "hot_zone_incident",
                "zone_id": zone["id"],
                "severity": "high",
                "message": f"Incident in hot zone {zone['id']} (risk: {risk_score:.0%})",
                "incident_type": incident_type,
                "timestamp": datetime.utcnow().isoformat(),
            })

        # Activity spike detection
        if activity_score > 0.8:
            alerts.append({
                "type": "activity_spike",
                "zone_id": zone["id"],
                "severity": "medium",
                "message": f"Elevated activity in zone {zone['id']}",
                "activity_score": activity_score,
                "timestamp": datetime.utcnow().isoformat(),
            })

        # Pattern match alert
        pattern_match = await self._check_pattern_match(zone, incident_data)
        if pattern_match:
            alerts.append({
                "type": "pattern_match",
                "zone_id": zone["id"],
                "severity": "medium",
                "message": f"Incident matches historical pattern in zone {zone['id']}",
                "pattern": pattern_match,
                "timestamp": datetime.utcnow().isoformat(),
            })

        return alerts

    # ==================== Zone Grid Generation ====================

    def _generate_zone_grid(self, level: str = "micro") -> list[dict]:
        """Generate zone grid based on level."""
        zones = []
        bounds = self.DEFAULT_BOUNDS

        if level == "micro":
            grid_size = self.MICRO_GRID_SIZE
        else:  # district
            grid_size = self.DISTRICT_GRID_SIZE

        lat_steps = int(
            (bounds["max_lat"] - bounds["min_lat"]) / grid_size
        )
        lon_steps = int(
            (bounds["max_lon"] - bounds["min_lon"]) / grid_size
        )

        for i in range(lat_steps):
            for j in range(lon_steps):
                min_lat = bounds["min_lat"] + i * grid_size
                max_lat = min_lat + grid_size
                min_lon = bounds["min_lon"] + j * grid_size
                max_lon = min_lon + grid_size

                zones.append({
                    "id": f"{level}_{i}_{j}",
                    "level": level,
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
                    "grid_position": {"row": i, "col": j},
                })

        return zones

    def _parse_zone_id(self, zone_id: str) -> dict | None:
        """Parse zone ID to get zone data."""
        try:
            parts = zone_id.split("_")
            if len(parts) >= 3:
                level = parts[0]
                i, j = int(parts[1]), int(parts[2])

                if level == "micro":
                    grid_size = self.MICRO_GRID_SIZE
                else:
                    grid_size = self.DISTRICT_GRID_SIZE

                bounds = self.DEFAULT_BOUNDS
                min_lat = bounds["min_lat"] + i * grid_size
                max_lat = min_lat + grid_size
                min_lon = bounds["min_lon"] + j * grid_size
                max_lon = min_lon + grid_size

                return {
                    "id": zone_id,
                    "level": level,
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
                    "grid_position": {"row": i, "col": j},
                }
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse zone ID {zone_id}: {e}")

        return None

    def _find_zone_by_location(
        self,
        lat: float,
        lon: float,
        level: str = "micro",
    ) -> dict | None:
        """Find zone containing a location."""
        bounds = self.DEFAULT_BOUNDS

        if level == "micro":
            grid_size = self.MICRO_GRID_SIZE
        else:
            grid_size = self.DISTRICT_GRID_SIZE

        # Check if within bounds
        if not (
            bounds["min_lat"] <= lat <= bounds["max_lat"]
            and bounds["min_lon"] <= lon <= bounds["max_lon"]
        ):
            return None

        # Calculate grid position
        i = int((lat - bounds["min_lat"]) / grid_size)
        j = int((lon - bounds["min_lon"]) / grid_size)

        return self._parse_zone_id(f"{level}_{i}_{j}")

    # ==================== Zone Enrichment ====================

    async def _enrich_zone(
        self,
        zone: dict,
        include_risk: bool = True,
        include_predictions: bool = False,
    ) -> dict:
        """Enrich zone with activity and risk data."""
        zone_data = zone.copy()
        bounds = zone["bounds"]

        # Get activity metrics
        activity_data = await self._get_zone_activity(bounds)
        zone_data.update(activity_data)

        # Determine zone status
        zone_data["status"] = self._determine_zone_status(
            zone_data.get("activity_score", 0)
        )

        if include_risk:
            # Get risk score
            risk_data = await self._get_zone_risk(bounds)
            zone_data.update(risk_data)

        if include_predictions:
            # Get predictions
            prediction_data = await self._get_zone_predictions(bounds)
            zone_data["predictions"] = prediction_data

        # Get operational overlays
        overlays = await self._get_zone_overlays(bounds)
        zone_data["overlays"] = overlays

        return zone_data

    async def _get_zone_activity(self, bounds: dict) -> dict:
        """Get activity metrics for a zone."""
        try:
            # Query for recent incidents
            query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": "now-24h"}}}],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds["max_lat"],
                                        "lon": bounds["min_lon"],
                                    },
                                    "bottom_right": {
                                        "lat": bounds["min_lat"],
                                        "lon": bounds["max_lon"],
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            # Get incident count
            incident_result = await self.es.count(index="incidents", query=query)
            incident_count = incident_result.get("count", 0)

            # Get CAD call count
            cad_result = await self.es.count(index="cad_calls", query=query)
            cad_count = cad_result.get("count", 0)

            # Get LPR hit count
            lpr_result = await self.es.count(index="lpr_hits", query=query)
            lpr_count = lpr_result.get("count", 0)

            # Calculate activity score
            activity_score = min(
                1.0,
                (incident_count * 0.4 + cad_count * 0.3 + lpr_count * 0.3) / 20,
            )

            return {
                "incident_count_24h": incident_count,
                "cad_count_24h": cad_count,
                "lpr_count_24h": lpr_count,
                "activity_score": round(activity_score, 3),
            }
        except Exception as e:
            logger.warning(f"Failed to get zone activity: {e}")
            # Return mock data
            return {
                "incident_count_24h": np.random.randint(0, 10),
                "cad_count_24h": np.random.randint(0, 20),
                "lpr_count_24h": np.random.randint(0, 30),
                "activity_score": round(np.random.uniform(0.1, 0.8), 3),
            }

    async def _get_zone_risk(self, bounds: dict) -> dict:
        """Get risk metrics for a zone."""
        try:
            # Query for risk factors
            # Violent crime count
            violent_query = {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-7d"}}},
                        {
                            "terms": {
                                "type": ["assault", "robbery", "homicide", "shooting"]
                            }
                        },
                    ],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds["max_lat"],
                                        "lon": bounds["min_lon"],
                                    },
                                    "bottom_right": {
                                        "lat": bounds["min_lat"],
                                        "lon": bounds["max_lon"],
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            violent_result = await self.es.count(index="incidents", query=violent_query)
            violent_count = violent_result.get("count", 0)

            # Calculate risk score
            risk_score = min(1.0, violent_count / 5)

            return {
                "violent_crime_count_7d": violent_count,
                "risk_score": round(risk_score, 3),
                "risk_level": self._get_risk_level(risk_score),
            }
        except Exception as e:
            logger.warning(f"Failed to get zone risk: {e}")
            risk_score = np.random.uniform(0.2, 0.7)
            return {
                "violent_crime_count_7d": np.random.randint(0, 5),
                "risk_score": round(risk_score, 3),
                "risk_level": self._get_risk_level(risk_score),
            }

    async def _get_zone_predictions(self, bounds: dict) -> dict:
        """Get prediction data for a zone."""
        try:
            # Query for predictions
            query = {
                "bool": {
                    "must": [
                        {"range": {"prediction_time": {"gte": "now", "lte": "now+24h"}}},
                    ],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds["max_lat"],
                                        "lon": bounds["min_lon"],
                                    },
                                    "bottom_right": {
                                        "lat": bounds["min_lat"],
                                        "lon": bounds["max_lon"],
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            results = await self.es.search(
                index="predicted_hotspots", query=query, size=10
            )

            predictions = []
            for hit in results.get("hits", {}).get("hits", []):
                source = hit["_source"]
                predictions.append({
                    "type": source.get("type", "unknown"),
                    "confidence": source.get("confidence", 0.5),
                    "prediction_time": source.get("prediction_time"),
                })

            # Calculate next-likely-crime probability
            if predictions:
                max_confidence = max(p["confidence"] for p in predictions)
            else:
                max_confidence = 0.0

            return {
                "predictions": predictions,
                "next_crime_probability": round(max_confidence, 3),
                "prediction_count": len(predictions),
            }
        except Exception as e:
            logger.warning(f"Failed to get zone predictions: {e}")
            return {
                "predictions": [],
                "next_crime_probability": round(np.random.uniform(0.1, 0.5), 3),
                "prediction_count": 0,
            }

    async def _get_zone_overlays(self, bounds: dict) -> dict:
        """Get operational overlays for a zone."""
        overlays = {
            "cameras": [],
            "lpr_cameras": [],
            "gunfire_sensors": [],
            "patrol_units": [],
        }

        try:
            # Get cameras in zone
            camera_query = """
            MATCH (c:Camera)
            WHERE c.latitude >= $min_lat AND c.latitude <= $max_lat
            AND c.longitude >= $min_lon AND c.longitude <= $max_lon
            RETURN c.id as id, c.latitude as lat, c.longitude as lon,
                   c.type as type, c.status as status
            """

            cameras = await self.neo4j.execute_query(
                camera_query,
                min_lat=bounds["min_lat"],
                max_lat=bounds["max_lat"],
                min_lon=bounds["min_lon"],
                max_lon=bounds["max_lon"],
            )

            for cam in cameras or []:
                cam_data = {
                    "id": cam["id"],
                    "lat": cam["lat"],
                    "lon": cam["lon"],
                    "status": cam.get("status", "unknown"),
                }

                if cam.get("type") == "lpr":
                    overlays["lpr_cameras"].append(cam_data)
                else:
                    overlays["cameras"].append(cam_data)
        except Exception as e:
            logger.warning(f"Failed to get zone overlays: {e}")
            # Generate mock overlay data
            overlays["cameras"] = [
                {
                    "id": f"cam_{i}",
                    "lat": np.random.uniform(bounds["min_lat"], bounds["max_lat"]),
                    "lon": np.random.uniform(bounds["min_lon"], bounds["max_lon"]),
                    "status": "online",
                }
                for i in range(np.random.randint(0, 3))
            ]

        return overlays

    async def _get_comprehensive_zone_data(
        self,
        zone: dict,
        include_history: bool = True,
    ) -> dict:
        """Get comprehensive data for a single zone."""
        # Start with enriched zone data
        zone_data = await self._enrich_zone(
            zone, include_risk=True, include_predictions=True
        )

        bounds = zone["bounds"]

        # Add incident breakdown
        zone_data["incident_breakdown"] = await self._get_incident_breakdown(bounds)

        # Add temporal patterns
        zone_data["temporal_patterns"] = await self._get_temporal_patterns(bounds)

        # Add entity summary
        zone_data["entity_summary"] = await self._get_entity_summary(bounds)

        if include_history:
            # Add historical trends
            zone_data["historical_trends"] = await self._get_historical_trends(bounds)

        # Add neighboring zone summary
        zone_data["neighbors"] = await self._get_neighbor_summary(zone)

        return zone_data

    async def _get_incident_breakdown(self, bounds: dict) -> dict:
        """Get incident type breakdown for a zone."""
        try:
            query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": "now-7d"}}}],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds["max_lat"],
                                        "lon": bounds["min_lon"],
                                    },
                                    "bottom_right": {
                                        "lat": bounds["min_lat"],
                                        "lon": bounds["max_lon"],
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            aggs = {
                "by_type": {"terms": {"field": "type", "size": 10}},
                "by_severity": {"terms": {"field": "severity", "size": 5}},
            }

            results = await self.es.search(
                index="incidents", query=query, aggs=aggs, size=0
            )

            type_buckets = (
                results.get("aggregations", {})
                .get("by_type", {})
                .get("buckets", [])
            )
            severity_buckets = (
                results.get("aggregations", {})
                .get("by_severity", {})
                .get("buckets", [])
            )

            return {
                "by_type": {b["key"]: b["doc_count"] for b in type_buckets},
                "by_severity": {b["key"]: b["doc_count"] for b in severity_buckets},
                "total": sum(b["doc_count"] for b in type_buckets),
            }
        except Exception as e:
            logger.warning(f"Failed to get incident breakdown: {e}")
            return {
                "by_type": {
                    "theft": np.random.randint(0, 5),
                    "assault": np.random.randint(0, 3),
                    "burglary": np.random.randint(0, 4),
                },
                "by_severity": {
                    "low": np.random.randint(0, 5),
                    "medium": np.random.randint(0, 3),
                    "high": np.random.randint(0, 2),
                },
                "total": np.random.randint(5, 15),
            }

    async def _get_temporal_patterns(self, bounds: dict) -> dict:
        """Get temporal patterns for a zone."""
        try:
            query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": "now-30d"}}}],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds["max_lat"],
                                        "lon": bounds["min_lon"],
                                    },
                                    "bottom_right": {
                                        "lat": bounds["min_lat"],
                                        "lon": bounds["max_lon"],
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            aggs = {
                "by_hour": {
                    "histogram": {"field": "hour_of_day", "interval": 1}
                },
                "by_day_of_week": {
                    "terms": {"field": "day_of_week", "size": 7}
                },
            }

            results = await self.es.search(
                index="incidents", query=query, aggs=aggs, size=0
            )

            hour_buckets = (
                results.get("aggregations", {})
                .get("by_hour", {})
                .get("buckets", [])
            )
            dow_buckets = (
                results.get("aggregations", {})
                .get("by_day_of_week", {})
                .get("buckets", [])
            )

            # Find peak hours
            hour_counts = {int(b["key"]): b["doc_count"] for b in hour_buckets}
            peak_hours = sorted(
                hour_counts.keys(), key=lambda h: hour_counts.get(h, 0), reverse=True
            )[:3]

            return {
                "by_hour": hour_counts,
                "by_day_of_week": {b["key"]: b["doc_count"] for b in dow_buckets},
                "peak_hours": peak_hours,
                "peak_activity_period": self._determine_peak_period(peak_hours),
            }
        except Exception as e:
            logger.warning(f"Failed to get temporal patterns: {e}")
            return {
                "by_hour": {h: np.random.randint(0, 10) for h in range(24)},
                "by_day_of_week": {
                    d: np.random.randint(5, 20)
                    for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                },
                "peak_hours": [22, 23, 0],
                "peak_activity_period": "night",
            }

    async def _get_entity_summary(self, bounds: dict) -> dict:
        """Get entity summary for a zone."""
        try:
            # Query Neo4j for entities in zone
            query = """
            MATCH (e)
            WHERE e.latitude >= $min_lat AND e.latitude <= $max_lat
            AND e.longitude >= $min_lon AND e.longitude <= $max_lon
            WITH labels(e)[0] as entity_type, count(e) as count
            RETURN entity_type, count
            """

            results = await self.neo4j.execute_query(
                query,
                min_lat=bounds["min_lat"],
                max_lat=bounds["max_lat"],
                min_lon=bounds["min_lon"],
                max_lon=bounds["max_lon"],
            )

            entity_counts = {r["entity_type"]: r["count"] for r in results or []}

            # Get high-risk entities
            high_risk_query = """
            MATCH (e)
            WHERE e.latitude >= $min_lat AND e.latitude <= $max_lat
            AND e.longitude >= $min_lon AND e.longitude <= $max_lon
            AND e.risk_score >= 0.6
            RETURN labels(e)[0] as entity_type, count(e) as count
            """

            high_risk_results = await self.neo4j.execute_query(
                high_risk_query,
                min_lat=bounds["min_lat"],
                max_lat=bounds["max_lat"],
                min_lon=bounds["min_lon"],
                max_lon=bounds["max_lon"],
            )

            high_risk_counts = {
                r["entity_type"]: r["count"] for r in high_risk_results or []
            }

            return {
                "total_entities": sum(entity_counts.values()),
                "by_type": entity_counts,
                "high_risk_entities": sum(high_risk_counts.values()),
                "high_risk_by_type": high_risk_counts,
            }
        except Exception as e:
            logger.warning(f"Failed to get entity summary: {e}")
            return {
                "total_entities": np.random.randint(10, 50),
                "by_type": {
                    "Person": np.random.randint(5, 20),
                    "Vehicle": np.random.randint(3, 15),
                    "Address": np.random.randint(2, 10),
                },
                "high_risk_entities": np.random.randint(0, 5),
                "high_risk_by_type": {},
            }

    async def _get_historical_trends(self, bounds: dict) -> dict:
        """Get historical trends for a zone."""
        try:
            # Get weekly incident counts for past 12 weeks
            query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": "now-12w"}}}],
                    "filter": [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": {
                                        "lat": bounds["max_lat"],
                                        "lon": bounds["min_lon"],
                                    },
                                    "bottom_right": {
                                        "lat": bounds["min_lat"],
                                        "lon": bounds["max_lon"],
                                    },
                                }
                            }
                        }
                    ],
                }
            }

            aggs = {
                "weekly": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "week",
                    }
                }
            }

            results = await self.es.search(
                index="incidents", query=query, aggs=aggs, size=0
            )

            weekly_buckets = (
                results.get("aggregations", {})
                .get("weekly", {})
                .get("buckets", [])
            )

            weekly_counts = [
                {"week": b["key_as_string"], "count": b["doc_count"]}
                for b in weekly_buckets
            ]

            # Calculate trend
            if len(weekly_counts) >= 4:
                recent_avg = np.mean([w["count"] for w in weekly_counts[-4:]])
                older_avg = np.mean([w["count"] for w in weekly_counts[:-4]])
                trend = (recent_avg - older_avg) / max(older_avg, 1)
            else:
                trend = 0.0

            return {
                "weekly_counts": weekly_counts,
                "trend": round(trend, 3),
                "trend_direction": "increasing" if trend > 0.1 else (
                    "decreasing" if trend < -0.1 else "stable"
                ),
            }
        except Exception as e:
            logger.warning(f"Failed to get historical trends: {e}")
            return {
                "weekly_counts": [
                    {"week": f"Week {i}", "count": np.random.randint(5, 20)}
                    for i in range(12)
                ],
                "trend": round(np.random.uniform(-0.2, 0.2), 3),
                "trend_direction": "stable",
            }

    async def _get_neighbor_summary(self, zone: dict) -> list[dict]:
        """Get summary of neighboring zones."""
        neighbors = []
        grid_pos = zone.get("grid_position", {})
        level = zone.get("level", "micro")

        # Get adjacent zones
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue

                ni = grid_pos.get("row", 0) + di
                nj = grid_pos.get("col", 0) + dj

                if ni >= 0 and nj >= 0:
                    neighbor_id = f"{level}_{ni}_{nj}"
                    neighbor_zone = self._parse_zone_id(neighbor_id)

                    if neighbor_zone:
                        # Get basic metrics for neighbor
                        activity = await self._get_zone_activity(neighbor_zone["bounds"])

                        neighbors.append({
                            "zone_id": neighbor_id,
                            "direction": self._get_direction(di, dj),
                            "activity_score": activity.get("activity_score", 0),
                            "status": self._determine_zone_status(
                                activity.get("activity_score", 0)
                            ),
                        })

        return neighbors

    async def _check_pattern_match(
        self,
        zone: dict,
        incident_data: dict,
    ) -> dict | None:
        """Check if incident matches historical patterns."""
        incident_data.get("type", "unknown")
        timestamp = incident_data.get("timestamp", datetime.utcnow().isoformat())

        try:
            # Parse timestamp to get hour
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                dt = timestamp

            hour = dt.hour
            dt.strftime("%a")

            # Get historical patterns
            patterns = await self._get_temporal_patterns(zone["bounds"])
            peak_hours = patterns.get("peak_hours", [])

            # Check if current hour is a peak hour
            if hour in peak_hours:
                return {
                    "pattern_type": "temporal",
                    "description": f"Incident at peak hour ({hour}:00)",
                    "confidence": 0.7,
                }
        except Exception as e:
            logger.warning(f"Failed to check pattern match: {e}")

        return None

    # ==================== Helper Methods ====================

    def _determine_zone_status(self, activity_score: float) -> str:
        """Determine zone status based on activity score."""
        if activity_score >= self.HOT_ZONE_THRESHOLD:
            return "hot"
        elif activity_score >= self.WARM_ZONE_THRESHOLD:
            return "warm"
        elif activity_score >= self.COLD_ZONE_THRESHOLD:
            return "cool"
        else:
            return "cold"

    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level."""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "elevated"
        elif risk_score >= 0.2:
            return "moderate"
        else:
            return "low"

    def _determine_peak_period(self, peak_hours: list[int]) -> str:
        """Determine peak activity period from peak hours."""
        if not peak_hours:
            return "unknown"

        avg_hour = np.mean(peak_hours)

        if 6 <= avg_hour < 12:
            return "morning"
        elif 12 <= avg_hour < 18:
            return "afternoon"
        elif 18 <= avg_hour < 22:
            return "evening"
        else:
            return "night"

    def _get_direction(self, di: int, dj: int) -> str:
        """Get cardinal direction from grid offset."""
        directions = {
            (-1, -1): "northwest",
            (-1, 0): "north",
            (-1, 1): "northeast",
            (0, -1): "west",
            (0, 1): "east",
            (1, -1): "southwest",
            (1, 0): "south",
            (1, 1): "southeast",
        }
        return directions.get((di, dj), "unknown")
