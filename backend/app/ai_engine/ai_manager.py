"""
AI Manager - Central Orchestrator for AI Intelligence Engine.

This module provides the central orchestrator for all AI operations,
coordinating between NLP, entity resolution, anomaly detection,
pattern recognition, and predictive models.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from app.ai_engine.anomaly_detection import AnomalyDetector
from app.ai_engine.entity_resolution import EntityResolver
from app.ai_engine.models import (
    AIInsightEvent,
    AIQueryResult,
    AnomalyResult,
    EntityMatch,
    PatternResult,
    PredictionResult,
    Relationship,
    RiskScore,
)
from app.ai_engine.nlp import DSLExecutor, QueryInterpreter, ResultComposer
from app.ai_engine.pattern_recognition import PatternPredictor
from app.ai_engine.pipelines import PipelineContext
from app.ai_engine.predictive_models import RiskScoringEngine
from app.core.logging import audit_logger, get_logger

logger = get_logger(__name__)

_ai_manager_instance: "AIManager | None" = None


class AIManager:
    """
    Central orchestrator for the AI Intelligence Engine.

    Coordinates all AI operations including:
    - Natural language query processing
    - Entity resolution and matching
    - Anomaly detection
    - Pattern recognition
    - Risk scoring
    - Predictive analytics

    Integrates with:
    - Neo4j for graph queries
    - Elasticsearch for full-text search
    - Redis for real-time event streaming
    - WebSocket for broadcasting insights
    """

    def __init__(self) -> None:
        """Initialize the AI Manager."""
        self._initialized = False
        self._neo4j_manager = None
        self._es_client = None
        self._redis_manager = None
        self._websocket_manager = None

        self._query_interpreter = QueryInterpreter()
        self._dsl_executor = DSLExecutor()
        self._result_composer = ResultComposer()
        self._entity_resolver = EntityResolver()
        self._anomaly_detector = AnomalyDetector()
        self._pattern_predictor = PatternPredictor()
        self._risk_scoring_engine = RiskScoringEngine()

        self._query_cache: dict[str, AIQueryResult] = {}
        self._insight_subscribers: list[Any] = []

    async def initialize(
        self,
        neo4j_manager: Any = None,
        es_client: Any = None,
        redis_manager: Any = None,
        websocket_manager: Any = None,
    ) -> None:
        """
        Initialize the AI Manager with database connections.

        Args:
            neo4j_manager: Neo4j database manager
            es_client: Elasticsearch client
            redis_manager: Redis manager for pub/sub
            websocket_manager: WebSocket manager for broadcasting
        """
        logger.info("initializing_ai_manager")

        self._neo4j_manager = neo4j_manager
        self._es_client = es_client
        self._redis_manager = redis_manager
        self._websocket_manager = websocket_manager

        await self._dsl_executor.initialize(neo4j_manager, es_client)
        await self._entity_resolver.initialize(neo4j_manager)
        await self._risk_scoring_engine.initialize(neo4j_manager)
        await self._pattern_predictor.load_model()

        self._initialized = True
        logger.info("ai_manager_initialized")

    async def shutdown(self) -> None:
        """Shutdown the AI Manager and release resources."""
        logger.info("shutting_down_ai_manager")
        self._initialized = False
        self._query_cache.clear()

    async def process_query(
        self,
        query: str,
        user_id: str | None = None,
        role: str | None = None,
    ) -> AIQueryResult:
        """
        Process a natural language investigative query.

        Args:
            query: Natural language query string
            user_id: User ID for audit logging
            role: User role for access control

        Returns:
            Complete AI query result with entities, incidents, relationships, etc.
        """
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        context = PipelineContext(
            request_id=request_id,
            user_id=user_id,
            role=role,
        )

        logger.info(
            "processing_ai_query",
            request_id=request_id,
            query_length=len(query),
            user_id=user_id,
            role=role,
        )

        audit_logger.log_system_event(
            event_type="ai_query_started",
            details={
                "request_id": request_id,
                "user_id": user_id,
                "role": role,
                "query_preview": query[:100] if len(query) > 100 else query,
            },
        )

        try:
            dsl_query = self._query_interpreter.interpret(query, role)

            raw_results = await self._dsl_executor.execute(dsl_query, context)

            resolved_entities = await self._entity_resolver.resolve(
                raw_results.get("entities", []), context
            )

            risk_scores = await self._risk_scoring_engine.batch_calculate_risk_scores(
                resolved_entities, context
            )

            composed_result = self._result_composer.compose(
                query=query,
                raw_results={
                    **raw_results,
                    "entities": resolved_entities,
                },
                risk_scores={k: v.to_dict() for k, v in risk_scores.items()},
                context=context,
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            result = AIQueryResult(
                query_id=composed_result["query_id"],
                original_query=query,
                summary=composed_result["summary"],
                entities=(
                    [
                        EntityMatch(**e) if isinstance(e, dict) else e
                        for e in composed_result.get("entities", [])
                    ]
                    if composed_result.get("entities")
                    else []
                ),
                incidents=composed_result.get("incidents", []),
                relationships=(
                    [
                        Relationship(**r) if isinstance(r, dict) else r
                        for r in composed_result.get("relationships", [])
                    ]
                    if composed_result.get("relationships")
                    else []
                ),
                risk_scores={
                    k: RiskScore(**v) if isinstance(v, dict) else v
                    for k, v in composed_result.get("risk_scores", {}).items()
                },
                recommendations=composed_result.get("recommendations", []),
                processing_time_ms=processing_time,
                confidence=self._calculate_confidence(composed_result),
            )

            self._query_cache[request_id] = result

            audit_logger.log_system_event(
                event_type="ai_query_completed",
                details={
                    "request_id": request_id,
                    "user_id": user_id,
                    "entity_count": len(result.entities),
                    "incident_count": len(result.incidents),
                    "processing_time_ms": processing_time,
                },
            )

            logger.info(
                "ai_query_completed",
                request_id=request_id,
                entity_count=len(result.entities),
                processing_time_ms=processing_time,
            )

            return result

        except Exception as e:
            logger.error(
                "ai_query_failed",
                request_id=request_id,
                error=str(e),
            )
            audit_logger.log_system_event(
                event_type="ai_query_failed",
                details={
                    "request_id": request_id,
                    "user_id": user_id,
                    "error": str(e),
                },
            )
            raise

    async def detect_anomalies(
        self,
        hours: int = 24,
        user_id: str | None = None,
    ) -> list[AnomalyResult]:
        """
        Detect anomalies in recent data.

        Args:
            hours: Time window in hours
            user_id: User ID for audit logging

        Returns:
            List of detected anomalies
        """
        request_id = str(uuid.uuid4())
        context = PipelineContext(request_id=request_id, user_id=user_id)

        logger.info(
            "detecting_anomalies",
            request_id=request_id,
            hours=hours,
        )

        data = await self._fetch_recent_data(hours)

        anomaly_dicts = await self._anomaly_detector.detect(data, context)

        anomalies = []
        for a in anomaly_dicts:
            if isinstance(a, dict):
                try:
                    anomalies.append(AnomalyResult(**a))
                except (TypeError, KeyError):
                    anomalies.append(a)
            else:
                anomalies.append(a)

        for anomaly in anomalies:
            if hasattr(anomaly, "severity") and anomaly.severity > 0.7:
                await self._broadcast_insight(
                    AIInsightEvent(
                        event_id=str(uuid.uuid4()),
                        event_type="anomaly_detected",
                        title=f"Anomaly Detected: {anomaly.anomaly_type.value if hasattr(anomaly.anomaly_type, 'value') else anomaly.anomaly_type}",
                        description=(
                            anomaly.description if hasattr(anomaly, "description") else str(anomaly)
                        ),
                        severity="high" if anomaly.severity > 0.8 else "medium",
                        entity_ids=(
                            anomaly.related_entities if hasattr(anomaly, "related_entities") else []
                        ),
                        location=anomaly.location if hasattr(anomaly, "location") else None,
                    )
                )

        audit_logger.log_system_event(
            event_type="anomaly_detection_completed",
            details={
                "request_id": request_id,
                "user_id": user_id,
                "hours": hours,
                "anomalies_found": len(anomalies),
            },
        )

        return anomalies

    async def get_patterns(
        self,
        pattern_type: str | None = None,
        hours: int = 168,
        user_id: str | None = None,
    ) -> list[PatternResult]:
        """
        Get recognized patterns.

        Args:
            pattern_type: Optional filter for pattern type (vehicles, gunfire, etc.)
            hours: Time window in hours (default 7 days)
            user_id: User ID for audit logging

        Returns:
            List of recognized patterns
        """
        request_id = str(uuid.uuid4())
        context = PipelineContext(request_id=request_id, user_id=user_id)

        logger.info(
            "getting_patterns",
            request_id=request_id,
            pattern_type=pattern_type,
            hours=hours,
        )

        data = await self._fetch_recent_data(hours)

        patterns = await self._pattern_predictor.recognize_patterns(data, context)

        if pattern_type:
            type_map = {
                "vehicles": "vehicle_trajectory",
                "gunfire": "gunfire_recurrence",
                "offenders": "repeat_offender",
                "temporal": "temporal_pattern",
                "geographic": "geographic_cluster",
            }
            target_type = type_map.get(pattern_type, pattern_type)
            patterns = [p for p in patterns if p.pattern_type.value == target_type]

        audit_logger.log_system_event(
            event_type="pattern_recognition_completed",
            details={
                "request_id": request_id,
                "user_id": user_id,
                "pattern_type": pattern_type,
                "patterns_found": len(patterns),
            },
        )

        return patterns

    async def get_predictions(
        self,
        prediction_type: str,
        input_data: dict[str, Any],
        user_id: str | None = None,
    ) -> PredictionResult | dict[str, Any]:
        """
        Get predictions from predictive models.

        Args:
            prediction_type: Type of prediction (vehicle_trajectory, crime_heat, etc.)
            input_data: Input data for prediction
            user_id: User ID for audit logging

        Returns:
            Prediction result
        """
        request_id = str(uuid.uuid4())
        context = PipelineContext(request_id=request_id, user_id=user_id)

        logger.info(
            "getting_prediction",
            request_id=request_id,
            prediction_type=prediction_type,
        )

        input_data["type"] = prediction_type
        result = await self._pattern_predictor.predict(input_data, context)

        audit_logger.log_system_event(
            event_type="prediction_generated",
            details={
                "request_id": request_id,
                "user_id": user_id,
                "prediction_type": prediction_type,
            },
        )

        return result

    async def calculate_risk_scores(
        self,
        entities: list[dict[str, Any]],
        user_id: str | None = None,
    ) -> dict[str, RiskScore]:
        """
        Calculate risk scores for entities.

        Args:
            entities: List of entities to score
            user_id: User ID for audit logging

        Returns:
            Dictionary mapping entity IDs to risk scores
        """
        request_id = str(uuid.uuid4())
        context = PipelineContext(request_id=request_id, user_id=user_id)

        logger.info(
            "calculating_risk_scores",
            request_id=request_id,
            entity_count=len(entities),
        )

        scores = await self._risk_scoring_engine.batch_calculate_risk_scores(entities, context)

        if self._neo4j_manager:
            await self._risk_scoring_engine.update_neo4j_risk_scores(scores, context)

        for entity_id, score in scores.items():
            if score.level.value in ["critical", "high"]:
                await self._broadcast_insight(
                    AIInsightEvent(
                        event_id=str(uuid.uuid4()),
                        event_type="high_risk_entity_updated",
                        title=f"High Risk Entity: {entity_id}",
                        description=f"Risk score updated to {score.score:.2f} ({score.level.value})",
                        severity=score.level.value,
                        entity_ids=[entity_id],
                    )
                )

        audit_logger.log_system_event(
            event_type="risk_scores_calculated",
            details={
                "request_id": request_id,
                "user_id": user_id,
                "entity_count": len(entities),
                "high_risk_count": sum(
                    1 for s in scores.values() if s.level.value in ["critical", "high"]
                ),
            },
        )

        return scores

    async def resolve_entities(
        self,
        entities: list[dict[str, Any]],
        user_id: str | None = None,
    ) -> list[EntityMatch]:
        """
        Resolve and merge entities.

        Args:
            entities: List of entities to resolve
            user_id: User ID for audit logging

        Returns:
            List of resolved entities with merge candidates
        """
        request_id = str(uuid.uuid4())
        context = PipelineContext(request_id=request_id, user_id=user_id)

        logger.info(
            "resolving_entities",
            request_id=request_id,
            entity_count=len(entities),
        )

        resolved = await self._entity_resolver.resolve(entities, context)

        result = []
        for e in resolved:
            if isinstance(e, dict):
                try:
                    result.append(EntityMatch(**e))
                except (TypeError, KeyError):
                    pass
            else:
                result.append(e)

        for entity in result:
            if hasattr(entity, "merge_candidates") and entity.merge_candidates:
                await self._broadcast_insight(
                    AIInsightEvent(
                        event_id=str(uuid.uuid4()),
                        event_type="cross_system_relationship_discovered",
                        title=f"Entity Match Found: {entity.entity_id}",
                        description=f"Found {len(entity.merge_candidates)} potential matches",
                        severity="info",
                        entity_ids=[entity.entity_id] + entity.merge_candidates,
                    )
                )

        return result

    async def process_real_time_event(
        self,
        event: dict[str, Any],
    ) -> None:
        """
        Process a real-time event for AI analysis.

        Args:
            event: Event data from real-time stream
        """
        await self._anomaly_detector.update_baseline([event])

        await self._pattern_predictor.train([event])

        entity_type = event.get("entity_type") or event.get("type")
        if entity_type in ["person", "vehicle", "incident"]:
            request_id = str(uuid.uuid4())
            context = PipelineContext(request_id=request_id)

            scores = await self._risk_scoring_engine.batch_calculate_risk_scores([event], context)

            for entity_id, score in scores.items():
                if score.level.value in ["critical", "high"]:
                    await self._broadcast_insight(
                        AIInsightEvent(
                            event_id=str(uuid.uuid4()),
                            event_type="high_risk_entity_updated",
                            title=f"Real-time Risk Alert: {entity_id}",
                            description=f"Entity risk level: {score.level.value}",
                            severity=score.level.value,
                            entity_ids=[entity_id],
                        )
                    )

    async def get_statistics(self) -> dict[str, Any]:
        """Get AI engine statistics."""
        return {
            "initialized": self._initialized,
            "cached_queries": len(self._query_cache),
            "insight_subscribers": len(self._insight_subscribers),
            "components": {
                "query_interpreter": "active",
                "dsl_executor": "active" if self._neo4j_manager or self._es_client else "inactive",
                "entity_resolver": "active",
                "anomaly_detector": "active",
                "pattern_predictor": "active",
                "risk_scoring_engine": "active",
            },
        }

    async def _fetch_recent_data(self, hours: int) -> list[dict[str, Any]]:
        """Fetch recent data from all sources."""
        data: list[dict[str, Any]] = []

        if self._es_client:
            try:
                cutoff = datetime.utcnow() - timedelta(hours=hours)
                query = {
                    "query": {
                        "range": {
                            "timestamp": {
                                "gte": cutoff.isoformat(),
                            }
                        }
                    },
                    "size": 10000,
                }
                results = await self._es_client.search(index="rtcc_*", body=query)
                for hit in results.get("hits", {}).get("hits", []):
                    data.append(hit.get("_source", {}))
            except Exception as e:
                logger.warning("es_fetch_failed", error=str(e))

        if self._neo4j_manager:
            try:
                cutoff = datetime.utcnow() - timedelta(hours=hours)
                query = """
                MATCH (n)
                WHERE n.created_at >= $cutoff
                RETURN n
                LIMIT 10000
                """
                results = await self._neo4j_manager.execute_query(
                    query, {"cutoff": cutoff.isoformat()}
                )
                data.extend(results)
            except Exception as e:
                logger.warning("neo4j_fetch_failed", error=str(e))

        return data

    async def _broadcast_insight(self, insight: AIInsightEvent) -> None:
        """Broadcast an AI insight event."""
        if self._websocket_manager:
            try:
                await self._websocket_manager.broadcast_ai_insight(insight.to_dict())
            except Exception as e:
                logger.warning("insight_broadcast_failed", error=str(e))

        if self._redis_manager:
            try:
                await self._redis_manager.publish(
                    "ai_insights",
                    insight.to_dict(),
                )
            except Exception as e:
                logger.warning("redis_publish_failed", error=str(e))

    def _calculate_confidence(self, result: dict[str, Any]) -> float:
        """Calculate overall confidence score for a result."""
        factors = []

        entity_count = len(result.get("entities", []))
        if entity_count > 0:
            factors.append(min(1.0, entity_count / 10))

        incident_count = len(result.get("incidents", []))
        if incident_count > 0:
            factors.append(min(1.0, incident_count / 20))

        relationship_count = len(result.get("relationships", []))
        if relationship_count > 0:
            factors.append(min(1.0, relationship_count / 15))

        if not factors:
            return 0.5

        return sum(factors) / len(factors)


def get_ai_manager() -> AIManager:
    """Get the singleton AI Manager instance."""
    global _ai_manager_instance
    if _ai_manager_instance is None:
        _ai_manager_instance = AIManager()
    return _ai_manager_instance


async def initialize_ai_manager(
    neo4j_manager: Any = None,
    es_client: Any = None,
    redis_manager: Any = None,
    websocket_manager: Any = None,
) -> AIManager:
    """Initialize and return the AI Manager."""
    manager = get_ai_manager()
    await manager.initialize(
        neo4j_manager=neo4j_manager,
        es_client=es_client,
        redis_manager=redis_manager,
        websocket_manager=websocket_manager,
    )
    return manager


__all__ = [
    "AIManager",
    "get_ai_manager",
    "initialize_ai_manager",
]
