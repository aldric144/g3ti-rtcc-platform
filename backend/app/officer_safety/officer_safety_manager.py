"""
Officer Safety Manager

Central orchestrator for all officer safety and situational awareness operations.
Coordinates between telemetry, safety scoring, threat proximity, ambush detection,
scene intelligence, perimeter generation, and emergency detection modules.
"""

from datetime import datetime
from typing import Any

from app.core.logging import get_logger
from app.db.elasticsearch import ElasticsearchManager
from app.db.neo4j import Neo4jManager
from app.db.redis import RedisManager

logger = get_logger(__name__)


class OfficerSafetyManager:
    """
    Central orchestrator for officer safety operations.

    Provides unified access to all officer safety subsystems and
    coordinates real-time safety monitoring and alerting.
    """

    def __init__(
        self,
        neo4j: Neo4jManager | None = None,
        es: ElasticsearchManager | None = None,
        redis: RedisManager | None = None,
    ):
        """
        Initialize the Officer Safety Manager.

        Args:
            neo4j: Neo4j database manager for entity relationships
            es: Elasticsearch manager for historical data
            redis: Redis manager for real-time state and pub/sub
        """
        self.neo4j = neo4j
        self.es = es
        self.redis = redis

        # Lazy-loaded subsystem managers
        self._telemetry_manager = None
        self._safety_scorer = None
        self._threat_engine = None
        self._ambush_detector = None
        self._scene_intel = None
        self._perimeter_engine = None
        self._emergency_detector = None

        logger.info("officer_safety_manager_initialized")

    @property
    def telemetry(self):
        """Get or create telemetry manager."""
        if self._telemetry_manager is None:
            from app.officer_safety.telemetry import OfficerTelemetryManager
            self._telemetry_manager = OfficerTelemetryManager(
                redis=self.redis,
                es=self.es,
            )
        return self._telemetry_manager

    @property
    def safety_scorer(self):
        """Get or create safety scorer."""
        if self._safety_scorer is None:
            from app.officer_safety.safety_score import OfficerSafetyScorer
            self._safety_scorer = OfficerSafetyScorer(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._safety_scorer

    @property
    def threat_engine(self):
        """Get or create threat proximity engine."""
        if self._threat_engine is None:
            from app.officer_safety.threat_proximity import ThreatProximityEngine
            self._threat_engine = ThreatProximityEngine(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._threat_engine

    @property
    def ambush_detector(self):
        """Get or create ambush detector."""
        if self._ambush_detector is None:
            from app.officer_safety.ambush_detection import AmbushDetector
            self._ambush_detector = AmbushDetector(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._ambush_detector

    @property
    def scene_intel(self):
        """Get or create scene intelligence engine."""
        if self._scene_intel is None:
            from app.officer_safety.scene_intel import SceneIntelligenceEngine
            self._scene_intel = SceneIntelligenceEngine(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._scene_intel

    @property
    def perimeter_engine(self):
        """Get or create perimeter engine."""
        if self._perimeter_engine is None:
            from app.officer_safety.perimeter import PerimeterEngine
            self._perimeter_engine = PerimeterEngine(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._perimeter_engine

    @property
    def emergency_detector(self):
        """Get or create emergency detector."""
        if self._emergency_detector is None:
            from app.officer_safety.emergency import EmergencyDetector
            self._emergency_detector = EmergencyDetector(
                redis=self.redis,
            )
        return self._emergency_detector

    async def process_location_update(
        self,
        badge: str,
        unit: str,
        location: tuple[float, float],
        speed: float | None = None,
        heading: float | None = None,
        status: str = "on_patrol",
    ) -> dict[str, Any]:
        """
        Process an officer location update.

        This is the main entry point for location telemetry. It:
        1. Updates officer position in Redis
        2. Stores position history
        3. Evaluates safety score
        4. Checks threat proximity
        5. Evaluates ambush patterns
        6. Checks for emergency conditions

        Args:
            badge: Officer badge number
            unit: Unit identifier (e.g., "Charlie-12")
            location: (latitude, longitude) tuple
            speed: Current speed in mph
            heading: Current heading in degrees
            status: Officer status (on_patrol, en_route, on_scene, etc.)

        Returns:
            Dictionary with update results and any alerts
        """
        logger.info(
            "processing_location_update",
            badge=badge,
            unit=unit,
            location=location,
            status=status,
        )

        result = {
            "badge": badge,
            "unit": unit,
            "location": {"lat": location[0], "lon": location[1]},
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": [],
            "safety_score": None,
            "threats": [],
        }

        try:
            # Update telemetry
            await self.telemetry.update_position(
                badge=badge,
                unit=unit,
                lat=location[0],
                lon=location[1],
                speed=speed,
                heading=heading,
                status=status,
            )

            # Calculate safety score
            safety_result = await self.safety_scorer.calculate_score(
                badge=badge,
                lat=location[0],
                lon=location[1],
            )
            result["safety_score"] = safety_result

            # Check threat proximity
            threats = await self.threat_engine.evaluate_threats(
                badge=badge,
                lat=location[0],
                lon=location[1],
            )
            result["threats"] = threats.get("threats", [])

            # Check for ambush patterns
            ambush_check = await self.ambush_detector.check_location(
                badge=badge,
                lat=location[0],
                lon=location[1],
            )
            if ambush_check.get("warning"):
                result["alerts"].append({
                    "type": "ambush_warning",
                    "severity": "critical",
                    "message": ambush_check.get("message"),
                    "data": ambush_check,
                })

            # Check for emergency conditions
            emergency_check = await self.emergency_detector.check_conditions(
                badge=badge,
                lat=location[0],
                lon=location[1],
                speed=speed,
                status=status,
            )
            if emergency_check.get("emergency"):
                result["alerts"].append({
                    "type": emergency_check.get("type", "officer_emergency"),
                    "severity": "critical",
                    "message": emergency_check.get("message"),
                    "data": emergency_check,
                })

        except Exception as e:
            logger.error("location_update_error", badge=badge, error=str(e))
            result["error"] = str(e)

        return result

    async def get_officer_status(self, badge: str) -> dict[str, Any]:
        """
        Get comprehensive status for an officer.

        Args:
            badge: Officer badge number

        Returns:
            Dictionary with officer status, location, safety score, and threats
        """
        try:
            # Get current position
            position = await self.telemetry.get_position(badge)

            if not position:
                return {
                    "badge": badge,
                    "status": "unknown",
                    "error": "No position data available",
                }

            # Get safety score
            safety = await self.safety_scorer.calculate_score(
                badge=badge,
                lat=position["lat"],
                lon=position["lon"],
            )

            # Get threats
            threats = await self.threat_engine.evaluate_threats(
                badge=badge,
                lat=position["lat"],
                lon=position["lon"],
            )

            return {
                "badge": badge,
                "unit": position.get("unit"),
                "location": {"lat": position["lat"], "lon": position["lon"]},
                "speed": position.get("speed"),
                "heading": position.get("heading"),
                "status": position.get("status", "unknown"),
                "last_update": position.get("timestamp"),
                "safety_score": safety,
                "threats": threats.get("threats", []),
            }

        except Exception as e:
            logger.error("get_officer_status_error", badge=badge, error=str(e))
            return {
                "badge": badge,
                "status": "error",
                "error": str(e),
            }

    async def get_all_officers(self) -> list[dict[str, Any]]:
        """
        Get status for all active officers.

        Returns:
            List of officer status dictionaries
        """
        try:
            positions = await self.telemetry.get_all_positions()

            officers = []
            for position in positions:
                badge = position.get("badge")
                if badge:
                    status = await self.get_officer_status(badge)
                    officers.append(status)

            return officers

        except Exception as e:
            logger.error("get_all_officers_error", error=str(e))
            return []

    async def get_scene_intelligence(
        self,
        address: str | None = None,
        incident_id: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """
        Get scene intelligence for a location or incident.

        Args:
            address: Street address
            incident_id: Incident ID
            lat: Latitude (if no address)
            lon: Longitude (if no address)

        Returns:
            RTCC Field Packet with comprehensive scene intelligence
        """
        return await self.scene_intel.get_intelligence(
            address=address,
            incident_id=incident_id,
            lat=lat,
            lon=lon,
        )

    async def generate_perimeter(
        self,
        incident_id: str,
        units: list[str],
        location: tuple[float, float],
        incident_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate tactical perimeter for an incident.

        Args:
            incident_id: Incident identifier
            units: List of unit identifiers
            location: (latitude, longitude) tuple
            incident_type: Type of incident

        Returns:
            Perimeter data with inner/outer boundaries and routes
        """
        return await self.perimeter_engine.generate_perimeter(
            incident_id=incident_id,
            units=units,
            lat=location[0],
            lon=location[1],
            incident_type=incident_type,
        )

    async def trigger_officer_down(
        self,
        badge: str,
        source: str = "manual",
        details: dict | None = None,
    ) -> dict[str, Any]:
        """
        Trigger officer down alert.

        Args:
            badge: Officer badge number
            source: Source of trigger (manual, auto, mdt)
            details: Additional details

        Returns:
            Alert confirmation
        """
        return await self.emergency_detector.trigger_officer_down(
            badge=badge,
            source=source,
            details=details,
        )

    async def trigger_sos(
        self,
        badge: str,
        source: str = "manual",
        details: dict | None = None,
    ) -> dict[str, Any]:
        """
        Trigger SOS alert.

        Args:
            badge: Officer badge number
            source: Source of trigger (manual, mdt, radio)
            details: Additional details

        Returns:
            Alert confirmation
        """
        return await self.emergency_detector.trigger_sos(
            badge=badge,
            source=source,
            details=details,
        )


# Singleton instance
_officer_safety_manager: OfficerSafetyManager | None = None


def get_officer_safety_manager() -> OfficerSafetyManager:
    """Get or create the singleton OfficerSafetyManager instance."""
    global _officer_safety_manager
    if _officer_safety_manager is None:
        _officer_safety_manager = OfficerSafetyManager()
    return _officer_safety_manager
