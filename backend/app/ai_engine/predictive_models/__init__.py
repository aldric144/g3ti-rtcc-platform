"""
Predictive Models Module.

This module provides predictive intelligence capabilities for forecasting
crime patterns, vehicle movements, and other predictive analytics.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from app.ai_engine.models import (
    EntityType,
    RiskLevel,
    RiskScore,
)
from app.ai_engine.pipelines import BasePredictor, PipelineContext
from app.core.logging import audit_logger, get_logger

logger = get_logger(__name__)


@dataclass
class RiskFactor:
    """A factor contributing to risk score."""

    name: str
    weight: float
    value: float
    description: str = ""


class RiskScoringEngine:
    """
    Risk scoring engine for entities.

    Calculates weighted risk scores for:
    - Vehicles of interest
    - Repeat offenders
    - High-risk addresses
    - Weapons with ballistic histories
    - Multi-linked persons
    """

    RISK_WEIGHTS = {
        "criminal_history": 0.25,
        "recent_activity": 0.20,
        "association_count": 0.15,
        "incident_involvement": 0.15,
        "location_risk": 0.10,
        "warrant_status": 0.10,
        "weapon_involvement": 0.05,
    }

    VEHICLE_RISK_WEIGHTS = {
        "stolen_status": 0.30,
        "bolo_status": 0.25,
        "incident_involvement": 0.20,
        "owner_risk": 0.15,
        "sighting_frequency": 0.10,
    }

    ADDRESS_RISK_WEIGHTS = {
        "incident_count": 0.30,
        "crime_severity": 0.25,
        "recent_activity": 0.20,
        "known_offenders": 0.15,
        "call_frequency": 0.10,
    }

    def __init__(self) -> None:
        """Initialize the risk scoring engine."""
        self._neo4j_manager = None
        self._score_cache: dict[str, RiskScore] = {}
        self._last_update: datetime | None = None

    async def initialize(self, neo4j_manager: Any) -> None:
        """Initialize with database connection."""
        self._neo4j_manager = neo4j_manager

    async def calculate_risk_score(
        self,
        entity_id: str,
        entity_type: EntityType,
        entity_data: dict[str, Any],
        context: PipelineContext,
    ) -> RiskScore:
        """
        Calculate risk score for an entity.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity
            entity_data: Entity data and attributes
            context: Pipeline context

        Returns:
            Calculated risk score
        """
        logger.info(
            "calculating_risk_score",
            entity_id=entity_id,
            entity_type=entity_type.value,
            request_id=context.request_id,
        )

        if entity_type == EntityType.PERSON:
            return await self._calculate_person_risk(entity_id, entity_data, context)
        elif entity_type == EntityType.VEHICLE:
            return await self._calculate_vehicle_risk(entity_id, entity_data, context)
        elif entity_type == EntityType.ADDRESS:
            return await self._calculate_address_risk(entity_id, entity_data, context)
        elif entity_type == EntityType.WEAPON:
            return await self._calculate_weapon_risk(entity_id, entity_data, context)
        else:
            return await self._calculate_generic_risk(entity_id, entity_type, entity_data, context)

    async def _calculate_person_risk(
        self,
        entity_id: str,
        entity_data: dict[str, Any],
        context: PipelineContext,
    ) -> RiskScore:
        """Calculate risk score for a person."""
        factors: dict[str, float] = {}

        criminal_history = entity_data.get("criminal_history", [])
        if criminal_history:
            severity_sum = sum(
                self._get_crime_severity(c.get("crime_type", "")) for c in criminal_history
            )
            factors["criminal_history"] = min(1.0, severity_sum / 10)
        else:
            factors["criminal_history"] = 0.0

        recent_incidents = entity_data.get("recent_incidents", [])
        recent_count = len(
            [i for i in recent_incidents if self._is_recent(i.get("timestamp"), days=90)]
        )
        factors["recent_activity"] = min(1.0, recent_count / 5)

        associations = entity_data.get("associations", [])
        high_risk_associations = len(
            [a for a in associations if a.get("risk_level") in ["high", "critical"]]
        )
        factors["association_count"] = min(1.0, high_risk_associations / 3)

        incident_count = entity_data.get("incident_count", 0)
        factors["incident_involvement"] = min(1.0, incident_count / 10)

        location_risk = entity_data.get("location_risk", 0.0)
        factors["location_risk"] = location_risk

        has_warrant = entity_data.get("has_warrant", False)
        factors["warrant_status"] = 1.0 if has_warrant else 0.0

        weapon_incidents = entity_data.get("weapon_incidents", 0)
        factors["weapon_involvement"] = min(1.0, weapon_incidents / 3)

        score = sum(factors.get(factor, 0) * weight for factor, weight in self.RISK_WEIGHTS.items())

        level = self._get_risk_level(score)

        historical_scores = self._score_cache.get(entity_id)
        historical = []
        if historical_scores:
            historical = historical_scores.historical_scores[-10:]
        historical.append(score)

        trend = self._calculate_trend(historical)

        risk_score = RiskScore(
            entity_id=entity_id,
            entity_type=EntityType.PERSON,
            score=score,
            level=level,
            factors=factors,
            trend=trend,
            historical_scores=historical,
        )

        self._score_cache[entity_id] = risk_score

        audit_logger.log_system_event(
            event_type="risk_score_calculated",
            details={
                "entity_id": entity_id,
                "entity_type": "person",
                "score": score,
                "level": level.value,
                "request_id": context.request_id,
            },
        )

        return risk_score

    async def _calculate_vehicle_risk(
        self,
        entity_id: str,
        entity_data: dict[str, Any],
        context: PipelineContext,
    ) -> RiskScore:
        """Calculate risk score for a vehicle."""
        factors: dict[str, float] = {}

        is_stolen = entity_data.get("is_stolen", False)
        factors["stolen_status"] = 1.0 if is_stolen else 0.0

        is_bolo = entity_data.get("is_bolo", False) or entity_data.get("on_hotlist", False)
        factors["bolo_status"] = 1.0 if is_bolo else 0.0

        incident_count = entity_data.get("incident_count", 0)
        factors["incident_involvement"] = min(1.0, incident_count / 5)

        owner_risk = entity_data.get("owner_risk_score", 0.0)
        factors["owner_risk"] = owner_risk

        sighting_count = entity_data.get("sighting_count_30d", 0)
        factors["sighting_frequency"] = min(1.0, sighting_count / 20)

        score = sum(
            factors.get(factor, 0) * weight for factor, weight in self.VEHICLE_RISK_WEIGHTS.items()
        )

        level = self._get_risk_level(score)

        risk_score = RiskScore(
            entity_id=entity_id,
            entity_type=EntityType.VEHICLE,
            score=score,
            level=level,
            factors=factors,
        )

        self._score_cache[entity_id] = risk_score

        return risk_score

    async def _calculate_address_risk(
        self,
        entity_id: str,
        entity_data: dict[str, Any],
        context: PipelineContext,
    ) -> RiskScore:
        """Calculate risk score for an address."""
        factors: dict[str, float] = {}

        incident_count = entity_data.get("incident_count", 0)
        factors["incident_count"] = min(1.0, incident_count / 20)

        incidents = entity_data.get("incidents", [])
        if incidents:
            avg_severity = sum(
                self._get_crime_severity(i.get("crime_type", "")) for i in incidents
            ) / len(incidents)
            factors["crime_severity"] = avg_severity
        else:
            factors["crime_severity"] = 0.0

        recent_incidents = len(
            [i for i in incidents if self._is_recent(i.get("timestamp"), days=30)]
        )
        factors["recent_activity"] = min(1.0, recent_incidents / 5)

        known_offenders = entity_data.get("known_offenders", 0)
        factors["known_offenders"] = min(1.0, known_offenders / 5)

        call_count = entity_data.get("call_count_30d", 0)
        factors["call_frequency"] = min(1.0, call_count / 10)

        score = sum(
            factors.get(factor, 0) * weight for factor, weight in self.ADDRESS_RISK_WEIGHTS.items()
        )

        level = self._get_risk_level(score)

        risk_score = RiskScore(
            entity_id=entity_id,
            entity_type=EntityType.ADDRESS,
            score=score,
            level=level,
            factors=factors,
        )

        self._score_cache[entity_id] = risk_score

        return risk_score

    async def _calculate_weapon_risk(
        self,
        entity_id: str,
        entity_data: dict[str, Any],
        context: PipelineContext,
    ) -> RiskScore:
        """Calculate risk score for a weapon."""
        factors: dict[str, float] = {}

        ballistic_matches = entity_data.get("ballistic_matches", 0)
        factors["ballistic_history"] = min(1.0, ballistic_matches / 3)

        incident_count = entity_data.get("incident_count", 0)
        factors["incident_involvement"] = min(1.0, incident_count / 5)

        is_stolen = entity_data.get("is_stolen", False)
        factors["stolen_status"] = 1.0 if is_stolen else 0.0

        owner_risk = entity_data.get("owner_risk_score", 0.0)
        factors["owner_risk"] = owner_risk

        score = (
            factors.get("ballistic_history", 0) * 0.35
            + factors.get("incident_involvement", 0) * 0.30
            + factors.get("stolen_status", 0) * 0.20
            + factors.get("owner_risk", 0) * 0.15
        )

        level = self._get_risk_level(score)

        risk_score = RiskScore(
            entity_id=entity_id,
            entity_type=EntityType.WEAPON,
            score=score,
            level=level,
            factors=factors,
        )

        self._score_cache[entity_id] = risk_score

        return risk_score

    async def _calculate_generic_risk(
        self,
        entity_id: str,
        entity_type: EntityType,
        entity_data: dict[str, Any],
        context: PipelineContext,
    ) -> RiskScore:
        """Calculate generic risk score for other entity types."""
        factors: dict[str, float] = {}

        incident_count = entity_data.get("incident_count", 0)
        factors["incident_involvement"] = min(1.0, incident_count / 10)

        association_count = entity_data.get("association_count", 0)
        factors["associations"] = min(1.0, association_count / 5)

        score = factors.get("incident_involvement", 0) * 0.6 + factors.get("associations", 0) * 0.4

        level = self._get_risk_level(score)

        return RiskScore(
            entity_id=entity_id,
            entity_type=entity_type,
            score=score,
            level=level,
            factors=factors,
        )

    async def batch_calculate_risk_scores(
        self,
        entities: list[dict[str, Any]],
        context: PipelineContext,
    ) -> dict[str, RiskScore]:
        """
        Calculate risk scores for multiple entities.

        Args:
            entities: List of entities with their data
            context: Pipeline context

        Returns:
            Dictionary mapping entity IDs to risk scores
        """
        results: dict[str, RiskScore] = {}

        for entity in entities:
            entity_id = entity.get("id") or entity.get("entity_id")
            entity_type_str = entity.get("entity_type") or entity.get("type")

            if not entity_id or not entity_type_str:
                continue

            try:
                entity_type = EntityType(entity_type_str)
            except ValueError:
                continue

            risk_score = await self.calculate_risk_score(entity_id, entity_type, entity, context)
            results[entity_id] = risk_score

        return results

    async def update_neo4j_risk_scores(
        self,
        risk_scores: dict[str, RiskScore],
        context: PipelineContext,
    ) -> None:
        """
        Update risk scores in Neo4j.

        Args:
            risk_scores: Dictionary of risk scores
            context: Pipeline context
        """
        if not self._neo4j_manager:
            logger.warning("neo4j_manager_not_initialized")
            return

        for entity_id, risk_score in risk_scores.items():
            try:
                query = """
                MATCH (n)
                WHERE n.id = $entity_id
                SET n.risk_score = $score,
                    n.risk_level = $level,
                    n.last_scored_at = $timestamp
                RETURN n
                """
                await self._neo4j_manager.execute_query(
                    query,
                    {
                        "entity_id": entity_id,
                        "score": risk_score.score,
                        "level": risk_score.level.value,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
            except Exception as e:
                logger.error(
                    "neo4j_risk_score_update_failed",
                    entity_id=entity_id,
                    error=str(e),
                )

        self._last_update = datetime.utcnow()

    def _get_risk_level(self, score: float) -> RiskLevel:
        """Get risk level from score."""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        elif score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    def _get_crime_severity(self, crime_type: str) -> float:
        """Get severity score for a crime type."""
        severity_map = {
            "homicide": 1.0,
            "murder": 1.0,
            "attempted_murder": 0.95,
            "shooting": 0.9,
            "armed_robbery": 0.85,
            "aggravated_assault": 0.8,
            "robbery": 0.75,
            "burglary": 0.6,
            "assault": 0.55,
            "theft": 0.4,
            "drug_possession": 0.35,
            "vandalism": 0.25,
            "trespassing": 0.15,
            "disorderly_conduct": 0.1,
        }

        crime_lower = crime_type.lower().replace(" ", "_").replace("-", "_")
        return severity_map.get(crime_lower, 0.3)

    def _is_recent(self, timestamp: Any, days: int = 30) -> bool:
        """Check if timestamp is within specified days."""
        if not timestamp:
            return False

        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                return False

        cutoff = datetime.utcnow() - timedelta(days=days)
        if hasattr(timestamp, "tzinfo") and timestamp.tzinfo:
            cutoff = cutoff.replace(tzinfo=timestamp.tzinfo)

        return timestamp >= cutoff

    def _calculate_trend(self, historical_scores: list[float]) -> str:
        """Calculate trend from historical scores."""
        if len(historical_scores) < 2:
            return "stable"

        recent = historical_scores[-3:] if len(historical_scores) >= 3 else historical_scores
        older = historical_scores[:-3] if len(historical_scores) > 3 else [historical_scores[0]]

        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)

        diff = recent_avg - older_avg

        if diff > 0.1:
            return "increasing"
        elif diff < -0.1:
            return "decreasing"
        else:
            return "stable"


class CrimePredictor(BasePredictor):
    """Predictor for crime patterns and hotspots."""

    def __init__(self) -> None:
        """Initialize the crime predictor."""
        super().__init__("crime_predictor")
        self._historical_data: list[dict[str, Any]] = []

    async def load_model(self) -> None:
        """Load prediction model."""
        self._model_loaded = True
        logger.info("crime_predictor_model_loaded")

    async def predict(self, input_data: dict[str, Any], context: PipelineContext) -> dict[str, Any]:
        """Make crime prediction."""
        prediction_type = input_data.get("type", "hotspot")

        if prediction_type == "hotspot":
            return await self._predict_hotspot(input_data, context)
        elif prediction_type == "time_series":
            return await self._predict_time_series(input_data, context)
        else:
            return {"error": f"Unknown prediction type: {prediction_type}"}

    async def train(self, training_data: list[dict[str, Any]]) -> None:
        """Train model with historical data."""
        self._historical_data.extend(training_data)
        logger.info("crime_predictor_trained", data_count=len(training_data))

    async def _predict_hotspot(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """Predict crime hotspots."""
        center_lat = input_data.get("latitude", 0)
        center_lon = input_data.get("longitude", 0)
        radius_km = input_data.get("radius_km", 5)

        hotspots: list[dict[str, Any]] = []

        for i in range(5):
            offset_lat = (i - 2) * 0.01
            offset_lon = (i - 2) * 0.01

            risk = 0.3 + (0.1 * abs(i - 2))

            hotspots.append(
                {
                    "latitude": center_lat + offset_lat,
                    "longitude": center_lon + offset_lon,
                    "risk_score": risk,
                    "predicted_incidents": int(risk * 10),
                    "primary_crime_type": ["theft", "assault", "burglary"][i % 3],
                }
            )

        return {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "hotspot",
            "hotspots": hotspots,
            "generated_at": datetime.utcnow().isoformat(),
            "confidence": "medium",
        }

    async def _predict_time_series(
        self, input_data: dict[str, Any], context: PipelineContext
    ) -> dict[str, Any]:
        """Predict crime time series."""
        hours_ahead = input_data.get("hours_ahead", 24)

        predictions: list[dict[str, Any]] = []
        base_time = datetime.utcnow()

        for hour in range(hours_ahead):
            pred_time = base_time + timedelta(hours=hour)
            hour_of_day = pred_time.hour

            if 22 <= hour_of_day or hour_of_day <= 4:
                expected_incidents = 8
            elif 14 <= hour_of_day <= 20:
                expected_incidents = 12
            else:
                expected_incidents = 5

            predictions.append(
                {
                    "timestamp": pred_time.isoformat(),
                    "expected_incidents": expected_incidents,
                    "confidence_interval": [
                        max(0, expected_incidents - 3),
                        expected_incidents + 3,
                    ],
                }
            )

        return {
            "prediction_id": str(uuid.uuid4()),
            "prediction_type": "time_series",
            "predictions": predictions,
            "generated_at": datetime.utcnow().isoformat(),
            "confidence": "medium",
        }


async def calculate_entity_risk_scores(
    entities: list[dict[str, Any]],
    context: PipelineContext | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Calculate risk scores for a list of entities.

    Args:
        entities: List of entities
        context: Pipeline context

    Returns:
        Dictionary mapping entity IDs to risk score data
    """
    if context is None:
        context = PipelineContext(request_id=str(uuid.uuid4()))

    engine = RiskScoringEngine()
    scores = await engine.batch_calculate_risk_scores(entities, context)

    return {entity_id: score.to_dict() for entity_id, score in scores.items()}


__all__ = [
    "RiskScoringEngine",
    "RiskFactor",
    "CrimePredictor",
    "calculate_entity_risk_scores",
]
