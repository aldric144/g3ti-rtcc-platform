"""
Dynamic Perimeter & Approach Engine

Auto-generates tactical perimeters and approach routes based on
incident type, suspect information, weapons, and tactical heat zones.
"""

import math
from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import ElasticsearchManager
from app.db.neo4j import Neo4jManager
from app.db.redis import RedisManager

logger = get_logger(__name__)

# Default perimeter radii by incident type (in meters)
PERIMETER_RADII = {
    "active_shooter": {"inner": 200, "outer": 500},
    "armed_robbery": {"inner": 150, "outer": 350},
    "hostage": {"inner": 100, "outer": 300},
    "barricaded_subject": {"inner": 100, "outer": 250},
    "domestic_violence": {"inner": 50, "outer": 150},
    "assault": {"inner": 75, "outer": 200},
    "burglary": {"inner": 50, "outer": 150},
    "default": {"inner": 75, "outer": 200},
}

# Risk multipliers for perimeter expansion
RISK_MULTIPLIERS = {
    "weapon_firearm": 1.5,
    "weapon_rifle": 2.0,
    "multiple_suspects": 1.3,
    "vehicle_involved": 1.4,
    "high_risk_zone": 1.2,
}


class PerimeterEngine:
    """
    Generates tactical perimeters and approach routes.

    Capabilities:
    - Auto-generate tactical perimeter radius based on:
      - Incident type
      - Suspect description
      - Known weapons
      - Vehicle likelihood of escape paths
      - Tactical heat zones (Phase 5)

    Generates:
    - Inner perimeter
    - Outer perimeter
    - Safe ingress and egress paths
    - Blue route (recommended officer approach)
    - Red route (high risk)
    """

    def __init__(
        self,
        neo4j: Neo4jManager | None = None,
        es: ElasticsearchManager | None = None,
        redis: RedisManager | None = None,
    ):
        """
        Initialize the perimeter engine.

        Args:
            neo4j: Neo4j manager for entity relationships
            es: Elasticsearch manager for historical data
            redis: Redis manager for caching
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        logger.info("perimeter_engine_initialized")

    async def generate_perimeter(
        self,
        incident_id: str,
        units: list[str],
        lat: float,
        lon: float,
        incident_type: str | None = None,
        suspect_info: dict | None = None,
        weapons_info: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Generate tactical perimeter for an incident.

        Args:
            incident_id: Incident identifier
            units: List of unit identifiers
            lat: Incident latitude
            lon: Incident longitude
            incident_type: Type of incident
            suspect_info: Suspect description and details
            weapons_info: Known weapons information

        Returns:
            Perimeter data with boundaries and routes
        """
        logger.info(
            "generating_perimeter",
            incident_id=incident_id,
            lat=lat,
            lon=lon,
            incident_type=incident_type,
        )

        # Get base radii for incident type
        incident_key = incident_type.lower().replace(" ", "_") if incident_type else "default"
        base_radii = PERIMETER_RADII.get(incident_key, PERIMETER_RADII["default"])

        # Calculate risk multiplier
        multiplier = await self._calculate_risk_multiplier(
            lat, lon, suspect_info, weapons_info
        )

        # Calculate adjusted radii
        inner_radius = base_radii["inner"] * multiplier
        outer_radius = base_radii["outer"] * multiplier

        # Generate perimeter polygons
        inner_perimeter = self._generate_perimeter_polygon(lat, lon, inner_radius)
        outer_perimeter = self._generate_perimeter_polygon(lat, lon, outer_radius)

        # Generate approach routes
        routes = await self._generate_approach_routes(
            lat, lon, inner_radius, outer_radius, units
        )

        # Generate staging areas
        staging_areas = self._generate_staging_areas(lat, lon, outer_radius)

        # Generate escape routes (for suspect vehicle)
        escape_routes = await self._identify_escape_routes(lat, lon, outer_radius)

        result = {
            "perimeter_id": f"PER-{incident_id}-{datetime.utcnow().strftime('%H%M%S')}",
            "incident_id": incident_id,
            "center": {"lat": lat, "lon": lon},
            "generated_at": datetime.utcnow().isoformat(),
            "inner_perimeter": {
                "radius_m": inner_radius,
                "polygon": inner_perimeter,
                "description": "Inner perimeter - restricted access",
            },
            "outer_perimeter": {
                "radius_m": outer_radius,
                "polygon": outer_perimeter,
                "description": "Outer perimeter - controlled access",
            },
            "routes": routes,
            "staging_areas": staging_areas,
            "escape_routes": escape_routes,
            "units_assigned": units,
            "risk_multiplier": multiplier,
            "recommendations": self._generate_perimeter_recommendations(
                incident_type, weapons_info, multiplier
            ),
        }

        return result

    async def _calculate_risk_multiplier(
        self,
        lat: float,
        lon: float,
        suspect_info: dict | None,
        weapons_info: list[dict] | None,
    ) -> float:
        """Calculate risk multiplier for perimeter expansion."""
        multiplier = 1.0

        # Check weapons
        if weapons_info:
            for weapon in weapons_info:
                weapon_type = weapon.get("type", "").lower()
                if "rifle" in weapon_type or "long gun" in weapon_type:
                    multiplier *= RISK_MULTIPLIERS["weapon_rifle"]
                elif "firearm" in weapon_type or "gun" in weapon_type or "pistol" in weapon_type:
                    multiplier *= RISK_MULTIPLIERS["weapon_firearm"]

        # Check suspect info
        if suspect_info:
            if suspect_info.get("count", 1) > 1:
                multiplier *= RISK_MULTIPLIERS["multiple_suspects"]
            if suspect_info.get("vehicle"):
                multiplier *= RISK_MULTIPLIERS["vehicle_involved"]

        # Check tactical heat zones (mock for now)
        import random
        if random.random() < 0.2:
            multiplier *= RISK_MULTIPLIERS["high_risk_zone"]

        return round(multiplier, 2)

    def _generate_perimeter_polygon(
        self,
        center_lat: float,
        center_lon: float,
        radius_m: float,
        num_points: int = 32,
    ) -> list[dict[str, float]]:
        """Generate a circular perimeter polygon."""
        points = []

        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points

            # Calculate offset in degrees (approximate)
            lat_offset = (radius_m / 111320) * math.cos(angle)
            lon_offset = (radius_m / (111320 * math.cos(math.radians(center_lat)))) * math.sin(angle)

            points.append({
                "lat": center_lat + lat_offset,
                "lon": center_lon + lon_offset,
            })

        # Close the polygon
        points.append(points[0])

        return points

    async def _generate_approach_routes(
        self,
        center_lat: float,
        center_lon: float,
        inner_radius: float,
        outer_radius: float,
        units: list[str],
    ) -> dict[str, Any]:
        """Generate approach routes for units."""
        import random

        # Generate cardinal direction approach points
        directions = ["north", "south", "east", "west"]
        direction_angles = {"north": 0, "south": 180, "east": 90, "west": 270}

        blue_routes = []  # Recommended safe routes
        red_routes = []   # High-risk routes

        for direction in directions:
            angle_deg = direction_angles[direction]
            angle_rad = math.radians(angle_deg)

            # Calculate approach point at outer perimeter
            approach_lat = center_lat + (outer_radius / 111320) * math.cos(angle_rad)
            approach_lon = center_lon + (outer_radius / (111320 * math.cos(math.radians(center_lat)))) * math.sin(angle_rad)

            # Determine if route is safe or high-risk (mock logic)
            is_safe = random.random() > 0.3

            route = {
                "direction": direction,
                "approach_point": {"lat": approach_lat, "lon": approach_lon},
                "waypoints": self._generate_waypoints(
                    approach_lat, approach_lon, center_lat, center_lon, inner_radius
                ),
                "distance_m": outer_radius,
                "cover_available": random.random() > 0.4,
                "visibility": random.choice(["good", "moderate", "limited"]),
            }

            if is_safe:
                route["recommendation"] = "Recommended approach"
                blue_routes.append(route)
            else:
                route["warning"] = "High exposure - limited cover"
                red_routes.append(route)

        return {
            "blue_routes": blue_routes,
            "red_routes": red_routes,
            "primary_approach": blue_routes[0] if blue_routes else None,
        }

    def _generate_waypoints(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        stop_radius: float,
    ) -> list[dict[str, float]]:
        """Generate waypoints along an approach route."""
        waypoints = []

        # Calculate total distance
        total_dist = math.sqrt(
            ((end_lat - start_lat) * 111320) ** 2 +
            ((end_lon - start_lon) * 111320 * math.cos(math.radians(start_lat))) ** 2
        )

        # Generate 3-4 waypoints
        num_waypoints = 3

        for i in range(1, num_waypoints + 1):
            fraction = i / (num_waypoints + 1)

            # Stop before inner perimeter
            if fraction * total_dist > (total_dist - stop_radius):
                break

            waypoints.append({
                "lat": start_lat + (end_lat - start_lat) * fraction,
                "lon": start_lon + (end_lon - start_lon) * fraction,
                "sequence": i,
            })

        return waypoints

    def _generate_staging_areas(
        self,
        center_lat: float,
        center_lon: float,
        outer_radius: float,
    ) -> list[dict[str, Any]]:
        """Generate staging areas outside the perimeter."""
        import random

        staging_areas = []

        # Generate 2-3 staging areas
        num_areas = random.randint(2, 3)
        angles = [45, 135, 225, 315][:num_areas]

        for i, angle_deg in enumerate(angles):
            angle_rad = math.radians(angle_deg)

            # Place staging area 1.5x outer radius
            distance = outer_radius * 1.5

            staging_lat = center_lat + (distance / 111320) * math.cos(angle_rad)
            staging_lon = center_lon + (distance / (111320 * math.cos(math.radians(center_lat)))) * math.sin(angle_rad)

            staging_areas.append({
                "id": f"STAGE-{i + 1}",
                "location": {"lat": staging_lat, "lon": staging_lon},
                "type": random.choice(["command_post", "medical", "tactical"]),
                "capacity": random.randint(5, 15),
                "distance_m": distance,
            })

        return staging_areas

    async def _identify_escape_routes(
        self,
        center_lat: float,
        center_lon: float,
        outer_radius: float,
    ) -> list[dict[str, Any]]:
        """Identify potential escape routes for suspects."""
        import random

        escape_routes = []

        # Identify major roads/highways (mock)
        num_routes = random.randint(2, 4)

        road_types = ["Highway", "Main Street", "Avenue", "Boulevard"]

        for i in range(num_routes):
            angle_deg = random.uniform(0, 360)
            angle_rad = math.radians(angle_deg)

            # Point on outer perimeter
            route_lat = center_lat + (outer_radius / 111320) * math.cos(angle_rad)
            route_lon = center_lon + (outer_radius / (111320 * math.cos(math.radians(center_lat)))) * math.sin(angle_rad)

            escape_routes.append({
                "id": f"ESC-{i + 1}",
                "direction": self._angle_to_direction(angle_deg),
                "road_type": random.choice(road_types),
                "exit_point": {"lat": route_lat, "lon": route_lon},
                "risk_level": random.choice(["high", "medium", "low"]),
                "recommendation": "Position unit to monitor" if random.random() > 0.5 else "Block if possible",
            })

        return escape_routes

    def _angle_to_direction(self, angle: float) -> str:
        """Convert angle to cardinal direction."""
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = int((angle + 22.5) / 45) % 8
        return directions[index]

    def _generate_perimeter_recommendations(
        self,
        incident_type: str | None,
        weapons_info: list[dict] | None,
        multiplier: float,
    ) -> list[str]:
        """Generate tactical recommendations for perimeter."""
        recommendations = []

        if multiplier > 1.5:
            recommendations.append("Extended perimeter due to elevated threat level")

        if weapons_info:
            has_firearm = any(
                "gun" in w.get("type", "").lower() or
                "firearm" in w.get("type", "").lower() or
                "rifle" in w.get("type", "").lower()
                for w in weapons_info
            )
            if has_firearm:
                recommendations.append("Firearm(s) involved - maintain cover at all times")
                recommendations.append("Consider ballistic shields for approach")

        if incident_type:
            incident_lower = incident_type.lower()
            if "hostage" in incident_lower:
                recommendations.append("Establish negotiation position")
                recommendations.append("Identify secondary entry points")
            elif "active" in incident_lower and "shooter" in incident_lower:
                recommendations.append("Immediate action protocol may be required")
                recommendations.append("Coordinate with SWAT if available")
            elif "barricade" in incident_lower:
                recommendations.append("Establish containment before approach")
                recommendations.append("Prepare for extended operation")

        if not recommendations:
            recommendations.append("Standard perimeter protocols apply")

        return recommendations


# Singleton instance
_perimeter_engine: PerimeterEngine | None = None


def get_perimeter_engine() -> PerimeterEngine:
    """Get or create the singleton PerimeterEngine instance."""
    global _perimeter_engine
    if _perimeter_engine is None:
        _perimeter_engine = PerimeterEngine()
    return _perimeter_engine
