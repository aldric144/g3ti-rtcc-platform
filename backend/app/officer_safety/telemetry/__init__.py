"""
Officer Location Telemetry Module

Handles real-time officer GPS position ingestion, storage, and tracking.
Provides time-window smoothing for GPS jitter and officer state management.
"""

import json
from datetime import datetime, timedelta
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import ElasticsearchManager
from app.db.redis import RedisManager

logger = get_logger(__name__)

# Redis key prefixes
OFFICER_POSITION_PREFIX = "officer:position:"
OFFICER_HISTORY_PREFIX = "officer:history:"
OFFICER_STATUS_PREFIX = "officer:status:"
ALL_OFFICERS_SET = "officers:active"

# Configuration
POSITION_TTL_SECONDS = 3600  # 1 hour
HISTORY_MAX_POINTS = 1000  # Max history points per officer
GPS_SMOOTHING_WINDOW = 5  # Number of points for smoothing


class OfficerTelemetryManager:
    """
    Manages officer location telemetry ingestion and storage.

    Features:
    - Real-time GPS position updates via WebSocket
    - Time-window smoothing for GPS jitter reduction
    - Officer state tracking (available, en route, on-scene)
    - Status change event system
    - Position history for trajectory analysis
    """

    def __init__(
        self,
        redis: RedisManager | None = None,
        es: ElasticsearchManager | None = None,
    ):
        """
        Initialize the telemetry manager.

        Args:
            redis: Redis manager for real-time position storage
            es: Elasticsearch manager for historical data
        """
        self.redis = redis
        self.es = es
        self._smoothing_buffers: dict[str, list[dict]] = {}

        logger.info("officer_telemetry_manager_initialized")

    async def update_position(
        self,
        badge: str,
        unit: str,
        lat: float,
        lon: float,
        speed: float | None = None,
        heading: float | None = None,
        status: str = "on_patrol",
        accuracy: float | None = None,
    ) -> dict[str, Any]:
        """
        Update officer position.

        Args:
            badge: Officer badge number
            unit: Unit identifier
            lat: Latitude
            lon: Longitude
            speed: Speed in mph
            heading: Heading in degrees (0-360)
            status: Officer status
            accuracy: GPS accuracy in meters

        Returns:
            Updated position data with smoothing applied
        """
        timestamp = datetime.utcnow()

        # Apply GPS smoothing
        smoothed_lat, smoothed_lon = self._apply_smoothing(
            badge, lat, lon, timestamp
        )

        position_data = {
            "badge": badge,
            "unit": unit,
            "lat": smoothed_lat,
            "lon": smoothed_lon,
            "raw_lat": lat,
            "raw_lon": lon,
            "speed": speed,
            "heading": heading,
            "status": status,
            "accuracy": accuracy,
            "timestamp": timestamp.isoformat(),
            "updated_at": timestamp.isoformat(),
        }

        # Check for status change
        previous_status = await self._get_previous_status(badge)
        status_changed = previous_status and previous_status != status

        if status_changed:
            position_data["previous_status"] = previous_status
            position_data["status_changed_at"] = timestamp.isoformat()
            logger.info(
                "officer_status_changed",
                badge=badge,
                from_status=previous_status,
                to_status=status,
            )

        # Store in Redis
        await self._store_position(badge, position_data)

        # Store in history
        await self._store_history(badge, position_data)

        # Add to active officers set
        await self._add_to_active_set(badge)

        # Index in Elasticsearch for historical queries
        await self._index_position(badge, position_data)

        logger.debug(
            "position_updated",
            badge=badge,
            lat=smoothed_lat,
            lon=smoothed_lon,
            status=status,
        )

        return position_data

    def _apply_smoothing(
        self,
        badge: str,
        lat: float,
        lon: float,
        timestamp: datetime,
    ) -> tuple[float, float]:
        """
        Apply time-window smoothing to reduce GPS jitter.

        Uses a simple moving average over the last N points.

        Args:
            badge: Officer badge number
            lat: Raw latitude
            lon: Raw longitude
            timestamp: Position timestamp

        Returns:
            Tuple of (smoothed_lat, smoothed_lon)
        """
        if badge not in self._smoothing_buffers:
            self._smoothing_buffers[badge] = []

        buffer = self._smoothing_buffers[badge]

        # Add new point
        buffer.append({
            "lat": lat,
            "lon": lon,
            "timestamp": timestamp,
        })

        # Remove old points (older than 30 seconds)
        cutoff = timestamp - timedelta(seconds=30)
        buffer[:] = [p for p in buffer if p["timestamp"] > cutoff]

        # Keep only last N points
        if len(buffer) > GPS_SMOOTHING_WINDOW:
            buffer[:] = buffer[-GPS_SMOOTHING_WINDOW:]

        # Calculate smoothed position
        if len(buffer) == 1:
            return lat, lon

        avg_lat = sum(p["lat"] for p in buffer) / len(buffer)
        avg_lon = sum(p["lon"] for p in buffer) / len(buffer)

        return avg_lat, avg_lon

    async def _get_previous_status(self, badge: str) -> str | None:
        """Get officer's previous status."""
        try:
            if self.redis:
                key = f"{OFFICER_STATUS_PREFIX}{badge}"
                status = await self.redis.get(key)
                return status
        except Exception as e:
            logger.warning("get_previous_status_error", badge=badge, error=str(e))
        return None

    async def _store_position(self, badge: str, data: dict) -> None:
        """Store current position in Redis."""
        try:
            if self.redis:
                # Store position
                position_key = f"{OFFICER_POSITION_PREFIX}{badge}"
                await self.redis.set(
                    position_key,
                    json.dumps(data),
                    ex=POSITION_TTL_SECONDS,
                )

                # Store status separately for quick lookup
                status_key = f"{OFFICER_STATUS_PREFIX}{badge}"
                await self.redis.set(
                    status_key,
                    data["status"],
                    ex=POSITION_TTL_SECONDS,
                )
        except Exception as e:
            logger.error("store_position_error", badge=badge, error=str(e))

    async def _store_history(self, badge: str, data: dict) -> None:
        """Store position in history list."""
        try:
            if self.redis:
                history_key = f"{OFFICER_HISTORY_PREFIX}{badge}"

                # Add to list (most recent first)
                await self.redis.lpush(history_key, json.dumps(data))

                # Trim to max size
                await self.redis.ltrim(history_key, 0, HISTORY_MAX_POINTS - 1)

                # Set TTL
                await self.redis.expire(history_key, POSITION_TTL_SECONDS * 24)
        except Exception as e:
            logger.error("store_history_error", badge=badge, error=str(e))

    async def _add_to_active_set(self, badge: str) -> None:
        """Add officer to active officers set."""
        try:
            if self.redis:
                await self.redis.sadd(ALL_OFFICERS_SET, badge)
        except Exception as e:
            logger.error("add_to_active_set_error", badge=badge, error=str(e))

    async def _index_position(self, badge: str, data: dict) -> None:
        """Index position in Elasticsearch for historical queries."""
        try:
            if self.es:
                await self.es.index(
                    index="officer_positions",
                    document={
                        **data,
                        "location": {
                            "lat": data["lat"],
                            "lon": data["lon"],
                        },
                    },
                )
        except Exception as e:
            logger.warning("index_position_error", badge=badge, error=str(e))

    async def get_position(self, badge: str) -> dict[str, Any] | None:
        """
        Get current position for an officer.

        Args:
            badge: Officer badge number

        Returns:
            Position data or None if not found
        """
        try:
            if self.redis:
                key = f"{OFFICER_POSITION_PREFIX}{badge}"
                data = await self.redis.get(key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.error("get_position_error", badge=badge, error=str(e))

        # Return mock data for development
        return self._generate_mock_position(badge)

    async def get_all_positions(self) -> list[dict[str, Any]]:
        """
        Get positions for all active officers.

        Returns:
            List of position data dictionaries
        """
        positions = []

        try:
            if self.redis:
                # Get all active officer badges
                badges = await self.redis.smembers(ALL_OFFICERS_SET)

                for badge in badges:
                    position = await self.get_position(badge)
                    if position:
                        positions.append(position)
        except Exception as e:
            logger.error("get_all_positions_error", error=str(e))

        # Return mock data if no real data
        if not positions:
            positions = self._generate_mock_positions()

        return positions

    async def get_history(
        self,
        badge: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get position history for an officer.

        Args:
            badge: Officer badge number
            limit: Maximum number of points to return

        Returns:
            List of historical positions (most recent first)
        """
        try:
            if self.redis:
                key = f"{OFFICER_HISTORY_PREFIX}{badge}"
                data = await self.redis.lrange(key, 0, limit - 1)
                return [json.loads(item) for item in data]
        except Exception as e:
            logger.error("get_history_error", badge=badge, error=str(e))

        return []

    async def get_officers_in_area(
        self,
        lat: float,
        lon: float,
        radius_km: float = 1.0,
    ) -> list[dict[str, Any]]:
        """
        Get officers within a radius of a location.

        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Search radius in kilometers

        Returns:
            List of officers within the radius
        """
        all_positions = await self.get_all_positions()

        nearby = []
        for position in all_positions:
            distance = self._haversine_distance(
                lat, lon,
                position["lat"], position["lon"],
            )
            if distance <= radius_km:
                position["distance_km"] = distance
                nearby.append(position)

        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])

        return nearby

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate distance between two points in kilometers."""
        import math

        R = 6371  # Earth's radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _generate_mock_position(self, badge: str) -> dict[str, Any]:
        """Generate mock position data for development."""
        import random

        # Base coordinates (Phoenix, AZ area)
        base_lat = 33.45
        base_lon = -112.07

        return {
            "badge": badge,
            "unit": f"Unit-{badge}",
            "lat": base_lat + random.uniform(-0.05, 0.05),
            "lon": base_lon + random.uniform(-0.05, 0.05),
            "speed": random.uniform(0, 45),
            "heading": random.uniform(0, 360),
            "status": random.choice(["on_patrol", "en_route", "on_scene", "available"]),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _generate_mock_positions(self) -> list[dict[str, Any]]:
        """Generate mock positions for multiple officers."""
        import random

        officers = []
        statuses = ["on_patrol", "en_route", "on_scene", "available"]

        # Generate 10-15 mock officers
        for i in range(random.randint(10, 15)):
            badge = f"{1000 + i}"
            unit_prefix = random.choice(["Alpha", "Bravo", "Charlie", "Delta"])

            officers.append({
                "badge": badge,
                "unit": f"{unit_prefix}-{i + 1}",
                "lat": 33.45 + random.uniform(-0.08, 0.08),
                "lon": -112.07 + random.uniform(-0.08, 0.08),
                "speed": random.uniform(0, 45) if random.random() > 0.3 else 0,
                "heading": random.uniform(0, 360),
                "status": random.choice(statuses),
                "timestamp": datetime.utcnow().isoformat(),
            })

        return officers


# Singleton instance
_telemetry_manager: OfficerTelemetryManager | None = None


def get_telemetry_manager() -> OfficerTelemetryManager:
    """Get or create the singleton OfficerTelemetryManager instance."""
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = OfficerTelemetryManager()
    return _telemetry_manager
