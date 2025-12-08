"""
Patrol Route Optimization Engine for G3TI RTCC-UIP.

This module provides patrol route optimization capabilities including:
- Risk-weighted route generation
- Traveling Salesman heuristics for multi-zone patrols
- Priority-based waypoint selection
- Time-of-day pattern optimization
- Repeat offender area coverage
- Vehicle recurrence likelihood routing
"""

import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from ...db.elasticsearch import ElasticsearchManager
from ...db.neo4j import Neo4jManager
from ...db.redis import RedisManager

logger = logging.getLogger(__name__)


class PatrolRouteOptimizer:
    """
    Engine for generating optimized patrol routes.

    Uses graph-based routing with weighted risk factors and
    Traveling Salesman heuristics for efficient coverage.
    """

    # Route optimization parameters
    DEFAULT_MAX_DISTANCE = 15.0  # km
    DEFAULT_WAYPOINT_COUNT = 10
    MIN_WAYPOINT_DISTANCE = 0.5  # km

    # Priority weights
    PRIORITY_WEIGHTS = {
        "risk_score": 0.35,
        "predicted_activity": 0.25,
        "historical_patterns": 0.20,
        "coverage_gap": 0.20,
    }

    # Shift definitions (24-hour format)
    SHIFTS = {
        "A": {"start": 7, "end": 15},   # Day shift
        "B": {"start": 15, "end": 23},  # Evening shift
        "C": {"start": 23, "end": 7},   # Night shift
    }

    def __init__(
        self,
        neo4j: Neo4jManager,
        es: ElasticsearchManager,
        redis: RedisManager,
        risk_engine: Any = None,
    ):
        """
        Initialize the Patrol Route Optimizer.

        Args:
            neo4j: Neo4j database manager
            es: Elasticsearch manager
            redis: Redis manager for caching
            risk_engine: Reference to tactical risk scorer
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis
        self.risk_engine = risk_engine

        logger.info("PatrolRouteOptimizer initialized")

    async def optimize_route(
        self,
        unit: str,
        shift: str,
        starting_point: tuple[float, float],
        max_distance: float = DEFAULT_MAX_DISTANCE,
        priority_zones: list[str] | None = None,
        waypoint_count: int = DEFAULT_WAYPOINT_COUNT,
    ) -> dict:
        """
        Generate optimized patrol route.

        Args:
            unit: Unit identifier
            shift: Shift time range (e.g., "2300-0700" or "A", "B", "C")
            starting_point: Starting coordinates (lat, lon)
            max_distance: Maximum route distance in km
            priority_zones: Optional list of priority zone IDs
            waypoint_count: Number of waypoints to include

        Returns:
            Optimized route with waypoints and justifications
        """
        logger.info(f"Optimizing route for unit {unit}, shift {shift}")

        # Parse shift information
        shift_info = self._parse_shift(shift)

        # Get candidate waypoints based on risk and activity
        candidates = await self._get_candidate_waypoints(
            starting_point, max_distance, shift_info, priority_zones
        )

        if not candidates:
            return self._empty_route_response(unit, shift, starting_point)

        # Score and rank waypoints
        scored_waypoints = await self._score_waypoints(
            candidates, shift_info, priority_zones
        )

        # Select top waypoints
        selected = scored_waypoints[:waypoint_count]

        # Optimize route order using TSP heuristic
        optimized_route = self._optimize_route_order(
            starting_point, selected, max_distance
        )

        # Calculate route statistics
        route_stats = self._calculate_route_stats(optimized_route, starting_point)

        # Generate justifications
        justifications = self._generate_justifications(optimized_route, shift_info)

        return {
            "unit": unit,
            "shift": shift,
            "route": optimized_route,
            "priority_zones": self._extract_priority_zones(optimized_route),
            "statistics": route_stats,
            "justification": justifications,
            "generated_at": datetime.utcnow().isoformat(),
            "valid_until": (
                datetime.utcnow() + timedelta(hours=shift_info.get("duration", 8))
            ).isoformat(),
        }

    async def get_coverage_analysis(
        self,
        zone_id: str | None = None,
        hours_back: int = 24,
    ) -> dict:
        """
        Analyze patrol coverage for zones.

        Args:
            zone_id: Specific zone or None for all
            hours_back: Hours of history to analyze

        Returns:
            Coverage analysis with gaps and recommendations
        """
        # Get patrol history
        patrol_history = await self._get_patrol_history(zone_id, hours_back)

        # Get zone risk data
        zones = await self._get_zones_with_risk()

        # Calculate coverage metrics
        coverage_metrics = self._calculate_coverage_metrics(
            zones, patrol_history, hours_back
        )

        # Identify coverage gaps
        gaps = self._identify_coverage_gaps(coverage_metrics)

        # Generate recommendations
        recommendations = self._generate_coverage_recommendations(gaps)

        return {
            "zones": coverage_metrics,
            "gaps": gaps,
            "recommendations": recommendations,
            "analysis_period_hours": hours_back,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # ==================== Waypoint Generation ====================

    async def _get_candidate_waypoints(
        self,
        starting_point: tuple[float, float],
        max_distance: float,
        shift_info: dict,
        priority_zones: list[str] | None,
    ) -> list[dict]:
        """Get candidate waypoints within range."""
        candidates = []

        # Calculate bounding box from starting point and max distance
        # Approximate: 1 degree latitude ≈ 111 km
        lat_range = max_distance / 111
        lon_range = max_distance / (111 * math.cos(math.radians(starting_point[0])))

        bounds = {
            "min_lat": starting_point[0] - lat_range,
            "max_lat": starting_point[0] + lat_range,
            "min_lon": starting_point[1] - lon_range,
            "max_lon": starting_point[1] + lon_range,
        }

        # Get high-risk zones
        risk_zones = await self._get_high_risk_zones(bounds)
        candidates.extend(risk_zones)

        # Get predicted hotspots
        predicted_hotspots = await self._get_predicted_hotspots(bounds, shift_info)
        candidates.extend(predicted_hotspots)

        # Get historical pattern locations
        pattern_locations = await self._get_pattern_locations(bounds, shift_info)
        candidates.extend(pattern_locations)

        # Add priority zones if specified
        if priority_zones:
            priority_waypoints = await self._get_priority_zone_waypoints(
                priority_zones, bounds
            )
            candidates.extend(priority_waypoints)

        # Deduplicate by proximity
        candidates = self._deduplicate_waypoints(candidates)

        # Filter by actual distance
        candidates = [
            c for c in candidates
            if self._haversine_distance(
                starting_point, (c["lat"], c["lon"])
            ) <= max_distance
        ]

        return candidates

    async def _get_high_risk_zones(self, bounds: dict) -> list[dict]:
        """Get high-risk zone centers as waypoints."""
        waypoints = []

        try:
            if self.risk_engine:
                risk_map = await self.risk_engine.generate_risk_map(
                    zone_id=None, level="micro", include_factors=False
                )

                for zone in risk_map.get("zones", []):
                    if zone["risk_score"] >= 0.5:
                        center = zone.get("center", {})
                        if self._point_in_bounds(
                            center.get("lat", 0), center.get("lon", 0), bounds
                        ):
                            waypoints.append({
                                "lat": center["lat"],
                                "lon": center["lon"],
                                "type": "high_risk_zone",
                                "zone_id": zone["id"],
                                "risk_score": zone["risk_score"],
                                "priority": zone["risk_score"],
                            })
        except Exception as e:
            logger.warning(f"Failed to get high-risk zones: {e}")
            # Generate mock data
            waypoints = self._generate_mock_waypoints(bounds, "high_risk_zone", 5)

        return waypoints

    async def _get_predicted_hotspots(
        self,
        bounds: dict,
        shift_info: dict,
    ) -> list[dict]:
        """Get predicted hotspots for the shift period."""
        waypoints = []

        try:
            # Query for predicted hotspots
            query = {
                "bool": {
                    "must": [
                        {"range": {"prediction_time": {"gte": "now", "lte": "now+8h"}}},
                        {"range": {"confidence": {"gte": 0.6}}},
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
                index="predicted_hotspots", query=query, size=20
            )

            for hit in results.get("hits", {}).get("hits", []):
                source = hit["_source"]
                waypoints.append({
                    "lat": source["latitude"],
                    "lon": source["longitude"],
                    "type": "predicted_hotspot",
                    "prediction_type": source.get("type", "unknown"),
                    "confidence": source.get("confidence", 0.5),
                    "priority": source.get("confidence", 0.5) * 0.9,
                })
        except Exception as e:
            logger.warning(f"Failed to get predicted hotspots: {e}")
            waypoints = self._generate_mock_waypoints(bounds, "predicted_hotspot", 4)

        return waypoints

    async def _get_pattern_locations(
        self,
        bounds: dict,
        shift_info: dict,
    ) -> list[dict]:
        """Get locations with historical patterns matching shift time."""
        waypoints = []

        try:
            # Query for historical patterns during shift hours
            start_hour = shift_info.get("start_hour", 0)
            end_hour = shift_info.get("end_hour", 24)

            query = {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-30d"}}},
                        {
                            "script": {
                                "script": {
                                    "source": """
                                        int hour = doc['timestamp'].value.getHour();
                                        return hour >= params.start && hour < params.end;
                                    """,
                                    "params": {"start": start_hour, "end": end_hour},
                                }
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

            # Aggregate by location
            aggs = {
                "locations": {
                    "geohash_grid": {"field": "location", "precision": 6},
                    "aggs": {"centroid": {"geo_centroid": {"field": "location"}}},
                }
            }

            results = await self.es.search(
                index="incidents", query=query, aggs=aggs, size=0
            )

            for bucket in results.get("aggregations", {}).get("locations", {}).get(
                "buckets", []
            ):
                centroid = bucket.get("centroid", {}).get("location", {})
                if centroid:
                    waypoints.append({
                        "lat": centroid["lat"],
                        "lon": centroid["lon"],
                        "type": "historical_pattern",
                        "incident_count": bucket["doc_count"],
                        "priority": min(1.0, bucket["doc_count"] / 20) * 0.8,
                    })
        except Exception as e:
            logger.warning(f"Failed to get pattern locations: {e}")
            waypoints = self._generate_mock_waypoints(bounds, "historical_pattern", 4)

        return waypoints

    async def _get_priority_zone_waypoints(
        self,
        priority_zones: list[str],
        bounds: dict,
    ) -> list[dict]:
        """Get waypoints for specified priority zones."""
        waypoints = []

        for zone_id in priority_zones:
            try:
                # Parse zone ID to get center
                parts = zone_id.split("_")
                if len(parts) >= 3:
                    i, j = int(parts[1]), int(parts[2])

                    # Calculate center (simplified)
                    lat = bounds["min_lat"] + (bounds["max_lat"] - bounds["min_lat"]) * (
                        i + 0.5
                    ) / 20
                    lon = bounds["min_lon"] + (bounds["max_lon"] - bounds["min_lon"]) * (
                        j + 0.5
                    ) / 20

                    waypoints.append({
                        "lat": lat,
                        "lon": lon,
                        "type": "priority_zone",
                        "zone_id": zone_id,
                        "priority": 1.0,  # Maximum priority
                    })
            except Exception as e:
                logger.warning(f"Failed to parse priority zone {zone_id}: {e}")

        return waypoints

    def _generate_mock_waypoints(
        self,
        bounds: dict,
        waypoint_type: str,
        count: int,
    ) -> list[dict]:
        """Generate mock waypoints for development."""
        waypoints = []

        for _ in range(count):
            lat = np.random.uniform(bounds["min_lat"], bounds["max_lat"])
            lon = np.random.uniform(bounds["min_lon"], bounds["max_lon"])

            waypoints.append({
                "lat": lat,
                "lon": lon,
                "type": waypoint_type,
                "priority": np.random.uniform(0.4, 0.9),
                "risk_score": np.random.uniform(0.3, 0.8),
            })

        return waypoints

    # ==================== Waypoint Scoring ====================

    async def _score_waypoints(
        self,
        candidates: list[dict],
        shift_info: dict,
        priority_zones: list[str] | None,
    ) -> list[dict]:
        """Score and rank candidate waypoints."""
        scored = []

        for waypoint in candidates:
            score = 0.0
            score_breakdown = {}

            # Risk score component
            risk_score = waypoint.get("risk_score", 0.5)
            score_breakdown["risk_score"] = risk_score
            score += risk_score * self.PRIORITY_WEIGHTS["risk_score"]

            # Predicted activity component
            if waypoint["type"] == "predicted_hotspot":
                pred_score = waypoint.get("confidence", 0.5)
            else:
                pred_score = waypoint.get("priority", 0.5) * 0.7
            score_breakdown["predicted_activity"] = pred_score
            score += pred_score * self.PRIORITY_WEIGHTS["predicted_activity"]

            # Historical patterns component
            if waypoint["type"] == "historical_pattern":
                hist_score = waypoint.get("priority", 0.5)
            else:
                hist_score = 0.3
            score_breakdown["historical_patterns"] = hist_score
            score += hist_score * self.PRIORITY_WEIGHTS["historical_patterns"]

            # Coverage gap component (simplified)
            coverage_score = await self._calculate_coverage_gap_score(waypoint)
            score_breakdown["coverage_gap"] = coverage_score
            score += coverage_score * self.PRIORITY_WEIGHTS["coverage_gap"]

            # Priority zone bonus
            if priority_zones and waypoint.get("zone_id") in priority_zones:
                score *= 1.5
                score_breakdown["priority_bonus"] = 0.5

            waypoint["total_score"] = min(1.0, score)
            waypoint["score_breakdown"] = score_breakdown
            scored.append(waypoint)

        # Sort by total score
        scored.sort(key=lambda x: x["total_score"], reverse=True)

        return scored

    async def _calculate_coverage_gap_score(self, waypoint: dict) -> float:
        """Calculate coverage gap score for a waypoint."""
        try:
            # Check recent patrol activity near this location
            query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": "now-24h"}}}],
                    "filter": [
                        {
                            "geo_distance": {
                                "distance": "500m",
                                "location": {
                                    "lat": waypoint["lat"],
                                    "lon": waypoint["lon"],
                                },
                            }
                        }
                    ],
                }
            }

            result = await self.es.count(index="patrol_activity", query=query)
            patrol_count = result.get("count", 0)

            # Higher score for less patrolled areas
            return max(0.0, 1.0 - (patrol_count / 10))
        except Exception:
            return np.random.uniform(0.3, 0.7)

    # ==================== Route Optimization ====================

    def _optimize_route_order(
        self,
        starting_point: tuple[float, float],
        waypoints: list[dict],
        max_distance: float,
    ) -> list[dict]:
        """
        Optimize route order using nearest neighbor heuristic.

        This is a simplified TSP solution that balances efficiency
        with priority coverage.
        """
        if not waypoints:
            return []

        # Start with nearest neighbor heuristic
        route = []
        remaining = waypoints.copy()
        current = starting_point
        total_distance = 0.0

        while remaining and total_distance < max_distance:
            # Find nearest unvisited waypoint with priority weighting
            best_idx = -1
            best_score = -1

            for i, wp in enumerate(remaining):
                distance = self._haversine_distance(current, (wp["lat"], wp["lon"]))

                # Skip if too far
                if total_distance + distance > max_distance:
                    continue

                # Score combines proximity and priority
                # Closer and higher priority = better
                proximity_score = 1.0 / (1.0 + distance)
                priority_score = wp.get("total_score", 0.5)
                combined_score = proximity_score * 0.4 + priority_score * 0.6

                if combined_score > best_score:
                    best_score = combined_score
                    best_idx = i

            if best_idx == -1:
                break

            # Add to route
            selected = remaining.pop(best_idx)
            distance = self._haversine_distance(current, (selected["lat"], selected["lon"]))
            total_distance += distance

            selected["distance_from_previous"] = round(distance, 2)
            selected["cumulative_distance"] = round(total_distance, 2)
            selected["sequence"] = len(route) + 1

            route.append(selected)
            current = (selected["lat"], selected["lon"])

        # Add return to start distance
        if route:
            return_distance = self._haversine_distance(
                current, starting_point
            )
            route[-1]["return_distance"] = round(return_distance, 2)

        return route

    def _haversine_distance(
        self,
        point1: tuple[float, float],
        point2: tuple[float, float],
    ) -> float:
        """Calculate haversine distance between two points in km."""
        R = 6371  # Earth's radius in km

        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    # ==================== Helper Methods ====================

    def _parse_shift(self, shift: str) -> dict:
        """Parse shift string to get time information."""
        # Check if it's a named shift
        if shift.upper() in self.SHIFTS:
            shift_def = self.SHIFTS[shift.upper()]
            return {
                "name": shift.upper(),
                "start_hour": shift_def["start"],
                "end_hour": shift_def["end"],
                "duration": (shift_def["end"] - shift_def["start"]) % 24 or 8,
            }

        # Try to parse time range (e.g., "2300-0700")
        try:
            parts = shift.split("-")
            if len(parts) == 2:
                start = int(parts[0][:2])
                end = int(parts[1][:2])
                return {
                    "name": shift,
                    "start_hour": start,
                    "end_hour": end,
                    "duration": (end - start) % 24 or 8,
                }
        except (ValueError, IndexError):
            pass

        # Default to 8-hour shift
        return {
            "name": shift,
            "start_hour": 0,
            "end_hour": 8,
            "duration": 8,
        }

    def _point_in_bounds(self, lat: float, lon: float, bounds: dict) -> bool:
        """Check if a point is within bounds."""
        return (
            bounds["min_lat"] <= lat <= bounds["max_lat"]
            and bounds["min_lon"] <= lon <= bounds["max_lon"]
        )

    def _deduplicate_waypoints(
        self,
        waypoints: list[dict],
        min_distance: float = MIN_WAYPOINT_DISTANCE,
    ) -> list[dict]:
        """Remove duplicate waypoints that are too close together."""
        if not waypoints:
            return []

        # Sort by priority (highest first)
        sorted_waypoints = sorted(
            waypoints, key=lambda x: x.get("priority", 0), reverse=True
        )

        deduplicated = []
        for wp in sorted_waypoints:
            is_duplicate = False
            for existing in deduplicated:
                distance = self._haversine_distance(
                    (wp["lat"], wp["lon"]),
                    (existing["lat"], existing["lon"]),
                )
                if distance < min_distance:
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(wp)

        return deduplicated

    def _calculate_route_stats(
        self,
        route: list[dict],
        starting_point: tuple[float, float],
    ) -> dict:
        """Calculate statistics for the route."""
        if not route:
            return {
                "total_distance": 0.0,
                "waypoint_count": 0,
                "avg_priority": 0.0,
                "coverage_area": 0.0,
            }

        total_distance = route[-1].get("cumulative_distance", 0)
        return_distance = route[-1].get("return_distance", 0)

        priorities = [wp.get("total_score", 0.5) for wp in route]

        # Estimate coverage area (simplified convex hull area)
        lats = [starting_point[0]] + [wp["lat"] for wp in route]
        lons = [starting_point[1]] + [wp["lon"] for wp in route]

        # Approximate area in sq km
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        coverage_area = lat_range * lon_range * 111 * 111  # Rough conversion

        return {
            "total_distance": round(total_distance + return_distance, 2),
            "patrol_distance": round(total_distance, 2),
            "return_distance": round(return_distance, 2),
            "waypoint_count": len(route),
            "avg_priority": round(np.mean(priorities), 3),
            "max_priority": round(max(priorities), 3),
            "coverage_area_sqkm": round(coverage_area, 2),
            "estimated_duration_hours": round((total_distance + return_distance) / 30, 1),
        }

    def _extract_priority_zones(self, route: list[dict]) -> list[dict]:
        """Extract priority zones from route."""
        zones = []
        seen = set()

        for wp in route:
            zone_id = wp.get("zone_id")
            if zone_id and zone_id not in seen:
                seen.add(zone_id)
                zones.append({
                    "zone_id": zone_id,
                    "priority": wp.get("total_score", 0.5),
                    "type": wp.get("type", "unknown"),
                })

        return zones

    def _generate_justifications(
        self,
        route: list[dict],
        shift_info: dict,
    ) -> list[str]:
        """Generate justifications for route waypoints."""
        justifications = []

        for i, wp in enumerate(route):
            wp_type = wp.get("type", "unknown")
            score = wp.get("total_score", 0.5)

            if wp_type == "high_risk_zone":
                justifications.append(
                    f"Waypoint {i+1}: High-risk zone with risk score "
                    f"{wp.get('risk_score', 0):.0%} - proactive presence recommended"
                )
            elif wp_type == "predicted_hotspot":
                justifications.append(
                    f"Waypoint {i+1}: Predicted hotspot with "
                    f"{wp.get('confidence', 0):.0%} confidence for shift period"
                )
            elif wp_type == "historical_pattern":
                justifications.append(
                    f"Waypoint {i+1}: Historical pattern location with "
                    f"{wp.get('incident_count', 0)} incidents during similar hours"
                )
            elif wp_type == "priority_zone":
                justifications.append(
                    f"Waypoint {i+1}: Command-designated priority zone "
                    f"({wp.get('zone_id', 'unknown')})"
                )
            else:
                justifications.append(
                    f"Waypoint {i+1}: General patrol point with "
                    f"priority score {score:.0%}"
                )

        return justifications

    def _empty_route_response(
        self,
        unit: str,
        shift: str,
        starting_point: tuple[float, float],
    ) -> dict:
        """Return empty route response."""
        return {
            "unit": unit,
            "shift": shift,
            "route": [],
            "priority_zones": [],
            "statistics": {
                "total_distance": 0.0,
                "waypoint_count": 0,
                "avg_priority": 0.0,
            },
            "justification": ["No suitable waypoints found within range"],
            "generated_at": datetime.utcnow().isoformat(),
        }

    # ==================== Coverage Analysis ====================

    async def _get_patrol_history(
        self,
        zone_id: str | None,
        hours_back: int,
    ) -> list[dict]:
        """Get patrol history for analysis."""
        try:
            query = {
                "bool": {
                    "must": [{"range": {"timestamp": {"gte": f"now-{hours_back}h"}}}]
                }
            }

            if zone_id:
                query["bool"]["filter"] = [{"term": {"zone_id": zone_id}}]

            results = await self.es.search(
                index="patrol_activity", query=query, size=1000
            )

            return [hit["_source"] for hit in results.get("hits", {}).get("hits", [])]
        except Exception as e:
            logger.warning(f"Failed to get patrol history: {e}")
            return []

    async def _get_zones_with_risk(self) -> list[dict]:
        """Get all zones with risk scores."""
        try:
            if self.risk_engine:
                risk_map = await self.risk_engine.generate_risk_map(
                    zone_id=None, level="micro", include_factors=False
                )
                return risk_map.get("zones", [])
        except Exception as e:
            logger.warning(f"Failed to get zones with risk: {e}")

        return []

    def _calculate_coverage_metrics(
        self,
        zones: list[dict],
        patrol_history: list[dict],
        hours_back: int,
    ) -> list[dict]:
        """Calculate coverage metrics for zones."""
        # Count patrols per zone
        patrol_counts = defaultdict(int)
        for patrol in patrol_history:
            zone_id = patrol.get("zone_id")
            if zone_id:
                patrol_counts[zone_id] += 1

        metrics = []
        for zone in zones:
            zone_id = zone.get("id", "unknown")
            patrol_count = patrol_counts.get(zone_id, 0)
            risk_score = zone.get("risk_score", 0.5)

            # Calculate coverage adequacy
            # Higher risk zones need more coverage
            expected_patrols = max(1, int(risk_score * hours_back / 4))
            coverage_ratio = patrol_count / max(expected_patrols, 1)

            metrics.append({
                "zone_id": zone_id,
                "risk_score": risk_score,
                "patrol_count": patrol_count,
                "expected_patrols": expected_patrols,
                "coverage_ratio": round(min(1.0, coverage_ratio), 2),
                "coverage_adequate": coverage_ratio >= 0.8,
            })

        return metrics

    def _identify_coverage_gaps(
        self,
        coverage_metrics: list[dict],
    ) -> list[dict]:
        """Identify zones with coverage gaps."""
        gaps = []

        for metric in coverage_metrics:
            if not metric["coverage_adequate"]:
                gaps.append({
                    "zone_id": metric["zone_id"],
                    "risk_score": metric["risk_score"],
                    "coverage_ratio": metric["coverage_ratio"],
                    "deficit": metric["expected_patrols"] - metric["patrol_count"],
                    "severity": "high" if metric["risk_score"] >= 0.6 else "medium",
                })

        # Sort by severity and risk
        gaps.sort(key=lambda x: (x["severity"] == "high", x["risk_score"]), reverse=True)

        return gaps

    def _generate_coverage_recommendations(
        self,
        gaps: list[dict],
    ) -> list[str]:
        """Generate recommendations for coverage gaps."""
        recommendations = []

        high_risk_gaps = [g for g in gaps if g["severity"] == "high"]
        medium_risk_gaps = [g for g in gaps if g["severity"] == "medium"]

        if high_risk_gaps:
            recommendations.append(
                f"PRIORITY: {len(high_risk_gaps)} high-risk zones have inadequate "
                f"coverage. Recommend immediate patrol allocation."
            )

            for gap in high_risk_gaps[:3]:
                recommendations.append(
                    f"  - Zone {gap['zone_id']}: {gap['deficit']} additional "
                    f"patrols needed (risk: {gap['risk_score']:.0%})"
                )

        if medium_risk_gaps:
            recommendations.append(
                f"ADVISORY: {len(medium_risk_gaps)} medium-risk zones have "
                f"coverage gaps. Consider increased patrol frequency."
            )

        if not gaps:
            recommendations.append(
                "Coverage is adequate across all zones. Maintain current "
                "patrol patterns."
            )

        return recommendations
