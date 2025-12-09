"""
Tactical Manager - Central orchestrator for tactical analytics.

This module coordinates all tactical intelligence operations including
heatmap generation, risk scoring, patrol optimization, zone analysis,
shift briefings, and forecasting.
"""

import logging
from datetime import datetime
from typing import Any

from ..db.elasticsearch import ElasticsearchManager
from ..db.neo4j import Neo4jManager
from ..db.redis import RedisManager

logger = logging.getLogger(__name__)


class TacticalManager:
    """
    Central orchestrator for tactical analytics operations.

    Coordinates between various tactical engines and provides
    unified access to tactical intelligence capabilities.
    """

    def __init__(
        self,
        neo4j_manager: Neo4jManager,
        es_manager: ElasticsearchManager,
        redis_manager: RedisManager,
    ):
        """
        Initialize the Tactical Manager.

        Args:
            neo4j_manager: Neo4j database manager for entity/relationship data
            es_manager: Elasticsearch manager for narrative/temporal patterns
            redis_manager: Redis manager for caching and pub/sub
        """
        self.neo4j = neo4j_manager
        self.es = es_manager
        self.redis = redis_manager

        # Lazy-loaded engine instances
        self._heatmap_engine: Any | None = None
        self._risk_engine: Any | None = None
        self._patrol_optimizer: Any | None = None
        self._zone_analyzer: Any | None = None
        self._briefing_builder: Any | None = None
        self._forecaster: Any | None = None

        logger.info("TacticalManager initialized")

    @property
    def heatmap_engine(self):
        """Lazy-load the heatmap engine."""
        if self._heatmap_engine is None:
            from .heatmaps import PredictiveHeatmapEngine
            self._heatmap_engine = PredictiveHeatmapEngine(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._heatmap_engine

    @property
    def risk_engine(self):
        """Lazy-load the risk scoring engine."""
        if self._risk_engine is None:
            from .tactical_risk import TacticalRiskScorer
            self._risk_engine = TacticalRiskScorer(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._risk_engine

    @property
    def patrol_optimizer(self):
        """Lazy-load the patrol optimizer."""
        if self._patrol_optimizer is None:
            from .patrol_optimizer import PatrolRouteOptimizer
            self._patrol_optimizer = PatrolRouteOptimizer(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
                risk_engine=self.risk_engine,
            )
        return self._patrol_optimizer

    @property
    def zone_analyzer(self):
        """Lazy-load the zone analyzer."""
        if self._zone_analyzer is None:
            from .zone_analysis import ZoneAnalyzer
            self._zone_analyzer = ZoneAnalyzer(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._zone_analyzer

    @property
    def briefing_builder(self):
        """Lazy-load the briefing builder."""
        if self._briefing_builder is None:
            from .shift_briefing import ShiftBriefingBuilder
            self._briefing_builder = ShiftBriefingBuilder(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
                heatmap_engine=self.heatmap_engine,
                risk_engine=self.risk_engine,
                patrol_optimizer=self.patrol_optimizer,
            )
        return self._briefing_builder

    @property
    def forecaster(self):
        """Lazy-load the forecaster."""
        if self._forecaster is None:
            from .forecasting import TacticalForecaster
            self._forecaster = TacticalForecaster(
                neo4j=self.neo4j,
                es=self.es,
                redis=self.redis,
            )
        return self._forecaster

    # ==================== Heatmap Operations ====================

    async def get_current_heatmap(
        self,
        heatmap_type: str = "gunfire",
        bounds: dict | None = None,
        resolution: str = "medium",
    ) -> dict:
        """
        Get current heatmap for specified type.

        Args:
            heatmap_type: Type of heatmap (gunfire, vehicles, crime, all)
            bounds: Geographic bounds {min_lat, max_lat, min_lon, max_lon}
            resolution: Grid resolution (low, medium, high)

        Returns:
            Heatmap data with GeoJSON, clusters, and metadata
        """
        logger.info(f"Generating current heatmap: type={heatmap_type}")
        return await self.heatmap_engine.generate_current_heatmap(
            heatmap_type=heatmap_type,
            bounds=bounds,
            resolution=resolution,
        )

    async def get_predictive_heatmap(
        self,
        hours: int | None = None,
        days: int | None = None,
        heatmap_type: str = "all",
        bounds: dict | None = None,
    ) -> dict:
        """
        Get predictive heatmap for future time window.

        Args:
            hours: Prediction window in hours (default 24)
            days: Prediction window in days (overrides hours)
            heatmap_type: Type of prediction
            bounds: Geographic bounds

        Returns:
            Predictive heatmap with confidence scores
        """
        if days:
            hours = days * 24
        elif not hours:
            hours = 24

        logger.info(f"Generating predictive heatmap: hours={hours}, type={heatmap_type}")
        return await self.heatmap_engine.generate_predictive_heatmap(
            hours=hours,
            heatmap_type=heatmap_type,
            bounds=bounds,
        )

    # ==================== Risk Scoring Operations ====================

    async def get_risk_map(
        self,
        zone_id: str | None = None,
        level: str = "micro",
    ) -> dict:
        """
        Get tactical risk map for zones.

        Args:
            zone_id: Specific zone ID or None for all zones
            level: Risk level granularity (address, micro, district)

        Returns:
            Risk map with scores and explanations
        """
        logger.info(f"Generating risk map: zone={zone_id}, level={level}")
        return await self.risk_engine.generate_risk_map(
            zone_id=zone_id,
            level=level,
        )

    async def get_entity_risk_score(
        self,
        entity_id: str,
        entity_type: str,
    ) -> dict:
        """
        Get risk score for a specific entity.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity (person, vehicle, address)

        Returns:
            Risk score with contributing factors
        """
        return await self.risk_engine.score_entity(
            entity_id=entity_id,
            entity_type=entity_type,
        )

    # ==================== Patrol Optimization Operations ====================

    async def generate_patrol_route(
        self,
        unit: str,
        shift: str,
        starting_point: tuple[float, float],
        max_distance: float = 15.0,
        priority_zones: list[str] | None = None,
    ) -> dict:
        """
        Generate optimized patrol route.

        Args:
            unit: Unit identifier
            shift: Shift time range (e.g., "2300-0700")
            starting_point: Starting coordinates (lat, lon)
            max_distance: Maximum route distance in km
            priority_zones: Optional list of priority zone IDs

        Returns:
            Optimized route with waypoints and justifications
        """
        logger.info(f"Generating patrol route: unit={unit}, shift={shift}")
        return await self.patrol_optimizer.optimize_route(
            unit=unit,
            shift=shift,
            starting_point=starting_point,
            max_distance=max_distance,
            priority_zones=priority_zones,
        )

    # ==================== Zone Analysis Operations ====================

    async def get_zones(
        self,
        include_risk: bool = True,
        include_predictions: bool = False,
    ) -> list[dict]:
        """
        Get all tactical zones with optional enrichment.

        Args:
            include_risk: Include risk scores
            include_predictions: Include prediction data

        Returns:
            List of zone data
        """
        return await self.zone_analyzer.get_all_zones(
            include_risk=include_risk,
            include_predictions=include_predictions,
        )

    async def get_zone(
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
        return await self.zone_analyzer.get_zone_details(
            zone_id=zone_id,
            include_history=include_history,
        )

    # ==================== Forecasting Operations ====================

    async def get_forecast(
        self,
        hours: int | None = None,
        days: int | None = None,
        forecast_type: str = "all",
    ) -> dict:
        """
        Get tactical forecast.

        Args:
            hours: Forecast window in hours
            days: Forecast window in days
            forecast_type: Type of forecast (crime, gunfire, vehicles, all)

        Returns:
            Forecast data with predictions and confidence
        """
        if days:
            hours = days * 24
        elif not hours:
            hours = 24

        logger.info(f"Generating forecast: hours={hours}, type={forecast_type}")
        return await self.forecaster.generate_forecast(
            hours=hours,
            forecast_type=forecast_type,
        )

    # ==================== Shift Briefing Operations ====================

    async def get_shift_briefing(
        self,
        shift: str,
        include_routes: bool = True,
        include_heatmaps: bool = True,
    ) -> dict:
        """
        Generate shift briefing intelligence pack.

        Args:
            shift: Shift identifier (A, B, C)
            include_routes: Include patrol route recommendations
            include_heatmaps: Include heatmap snapshots

        Returns:
            Complete shift briefing package
        """
        logger.info(f"Generating shift briefing: shift={shift}")
        return await self.briefing_builder.build_briefing(
            shift=shift,
            include_routes=include_routes,
            include_heatmaps=include_heatmaps,
        )

    # ==================== Real-time Updates ====================

    async def process_new_incident(
        self,
        incident_data: dict,
    ) -> dict:
        """
        Process a new incident and update tactical intelligence.

        Args:
            incident_data: Incident information

        Returns:
            Updated tactical assessments
        """
        logger.info("Processing new incident for tactical updates")

        # Update heatmaps
        heatmap_update = await self.heatmap_engine.update_with_incident(incident_data)

        # Update risk scores
        risk_update = await self.risk_engine.update_with_incident(incident_data)

        # Check for zone alerts
        zone_alerts = await self.zone_analyzer.check_zone_alerts(incident_data)

        # Publish updates via Redis
        await self._publish_tactical_update({
            "type": "incident_processed",
            "heatmap_update": heatmap_update,
            "risk_update": risk_update,
            "zone_alerts": zone_alerts,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "heatmap_update": heatmap_update,
            "risk_update": risk_update,
            "zone_alerts": zone_alerts,
        }

    async def _publish_tactical_update(self, update: dict) -> None:
        """Publish tactical update to Redis pub/sub."""
        try:
            await self.redis.publish("tactical:updates", update)
        except Exception as e:
            logger.error(f"Failed to publish tactical update: {e}")

    # ==================== Audit and Logging ====================

    async def log_tactical_action(
        self,
        action_type: str,
        user_id: str,
        details: dict,
    ) -> None:
        """
        Log tactical action for CJIS compliance.

        Args:
            action_type: Type of action performed
            user_id: User who performed the action
            details: Action details
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "user_id": user_id,
            "details": details,
            "module": "tactical_engine",
        }

        # Store in Elasticsearch for audit trail
        try:
            await self.es.index(
                index="tactical_audit_logs",
                document=audit_entry,
            )
        except Exception as e:
            logger.error(f"Failed to log tactical action: {e}")
            # Also log locally as backup
            logger.info(f"AUDIT: {audit_entry}")
