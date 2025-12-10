"""
Correlation Engine for G3TI RTCC-UIP.

This module provides multi-engine entity and pattern fusion capabilities,
including probabilistic cross-entity matching, temporal and geographic
fusion logic, and threat trajectory inference.
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EntityType(str, Enum):
    """Types of entities for correlation."""
    PERSON = "person"
    VEHICLE = "vehicle"
    WEAPON = "weapon"
    INCIDENT = "incident"
    LOCATION = "location"
    ORGANIZATION = "organization"
    PHONE = "phone"
    ADDRESS = "address"
    CASE = "case"
    PATTERN = "pattern"


class CorrelationType(str, Enum):
    """Types of correlations."""
    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    PROBABILISTIC = "probabilistic"
    TEMPORAL = "temporal"
    GEOGRAPHIC = "geographic"
    NETWORK = "network"
    PATTERN = "pattern"
    BEHAVIORAL = "behavioral"


class CorrelationStrength(str, Enum):
    """Strength of correlation."""
    DEFINITE = "definite"  # 0.95+
    STRONG = "strong"      # 0.80-0.94
    MODERATE = "moderate"  # 0.60-0.79
    WEAK = "weak"          # 0.40-0.59
    TENTATIVE = "tentative"  # < 0.40


class CorrelationConfig(BaseModel):
    """Configuration for correlation engine."""
    enabled: bool = True
    min_correlation_score: float = 0.4
    exact_match_threshold: float = 0.95
    fuzzy_match_threshold: float = 0.75
    temporal_window_hours: float = 24.0
    geographic_radius_meters: float = 1000.0
    max_correlations_per_entity: int = 100
    enable_probabilistic_matching: bool = True
    enable_temporal_fusion: bool = True
    enable_geographic_fusion: bool = True
    enable_network_analysis: bool = True
    cache_ttl_seconds: int = 300


class EntityReference(BaseModel):
    """Reference to an entity for correlation."""
    id: str
    entity_type: EntityType
    source: str
    jurisdiction: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EntityCorrelation(BaseModel):
    """Correlation between two entities."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity1_id: str
    entity1_type: EntityType
    entity2_id: str
    entity2_type: EntityType
    correlation_type: CorrelationType
    score: float = Field(ge=0.0, le=1.0)
    strength: CorrelationStrength
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class PatternCorrelation(BaseModel):
    """Correlation representing a detected pattern."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    pattern_type: str
    entities: list[str]  # Entity IDs involved
    entity_types: list[EntityType]
    score: float = Field(ge=0.0, le=1.0)
    description: str
    temporal_span: dict[str, datetime] | None = None
    geographic_span: dict[str, float] | None = None
    frequency: int | None = None
    trend: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class CorrelationResult(BaseModel):
    """Result of correlation analysis."""
    query_entity_id: str
    entity_correlations: list[EntityCorrelation] = Field(default_factory=list)
    pattern_correlations: list[PatternCorrelation] = Field(default_factory=list)
    total_correlations: int = 0
    processing_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ThreatTrajectory(BaseModel):
    """Inferred threat trajectory from correlations."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    threat_level: str  # low, medium, high, critical
    trajectory_type: str  # escalating, stable, de-escalating
    entities_involved: list[str]
    incidents: list[str]
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    predicted_next_action: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    risk_factors: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CorrelationEngine:
    """
    Multi-engine entity and pattern correlation engine.

    Provides probabilistic cross-entity matching, temporal and geographic
    fusion logic, and threat trajectory inference.
    """

    def __init__(self, config: CorrelationConfig | None = None):
        self.config = config or CorrelationConfig()
        self._entity_cache: dict[str, EntityReference] = {}
        self._correlation_cache: dict[str, list[EntityCorrelation]] = {}
        self._pattern_cache: dict[str, PatternCorrelation] = {}
        self._lock = asyncio.Lock()

        logger.info("CorrelationEngine initialized")

    async def correlate(self, signal: Any) -> list[dict[str, Any]]:
        """
        Correlate a signal with existing intelligence.

        Returns list of correlation results.
        """
        if not self.config.enabled:
            return []

        start_time = datetime.now(UTC)
        correlations = []

        # Extract entities from signal
        entities = self._extract_entities(signal)

        for entity in entities:
            # Find correlations for each entity
            result = await self.find_correlations(entity)

            for corr in result.entity_correlations:
                correlations.append({
                    "type": "entity",
                    "correlation_type": corr.correlation_type.value,
                    "score": corr.score,
                    "strength": corr.strength.value,
                    "entity1_id": corr.entity1_id,
                    "entity2_id": corr.entity2_id,
                    "evidence": corr.evidence,
                })

            for pattern in result.pattern_correlations:
                correlations.append({
                    "type": "pattern",
                    "pattern_type": pattern.pattern_type,
                    "score": pattern.score,
                    "entities": pattern.entities,
                    "description": pattern.description,
                })

        elapsed_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
        logger.debug("Correlation completed in %.2f ms, found %d correlations",
                    elapsed_ms, len(correlations))

        return correlations

    def _extract_entities(self, signal: Any) -> list[EntityReference]:
        """Extract entity references from a signal."""
        entities = []

        if not isinstance(signal, dict) and hasattr(signal, "data"):
            signal = signal.data if isinstance(signal.data, dict) else {}
        elif not isinstance(signal, dict):
            return entities

        # Extract person entities
        if "person" in signal or "suspect" in signal or "offender" in signal:
            person_data = signal.get("person") or signal.get("suspect") or signal.get("offender", {})
            if person_data:
                entities.append(EntityReference(
                    id=person_data.get("id", str(uuid4())),
                    entity_type=EntityType.PERSON,
                    source=signal.get("source", "unknown"),
                    jurisdiction=signal.get("jurisdiction", "unknown"),
                    attributes=person_data,
                ))

        # Extract vehicle entities
        if "vehicle" in signal:
            vehicle_data = signal.get("vehicle", {})
            if vehicle_data:
                entities.append(EntityReference(
                    id=vehicle_data.get("id", str(uuid4())),
                    entity_type=EntityType.VEHICLE,
                    source=signal.get("source", "unknown"),
                    jurisdiction=signal.get("jurisdiction", "unknown"),
                    attributes=vehicle_data,
                ))

        # Extract weapon entities
        if "weapon" in signal:
            weapon_data = signal.get("weapon", {})
            if weapon_data:
                entities.append(EntityReference(
                    id=weapon_data.get("id", str(uuid4())),
                    entity_type=EntityType.WEAPON,
                    source=signal.get("source", "unknown"),
                    jurisdiction=signal.get("jurisdiction", "unknown"),
                    attributes=weapon_data,
                ))

        # Extract location entities
        if "location" in signal or ("latitude" in signal and "longitude" in signal):
            location_data = signal.get("location", {
                "latitude": signal.get("latitude"),
                "longitude": signal.get("longitude"),
                "address": signal.get("address"),
            })
            if location_data.get("latitude") or location_data.get("address"):
                entities.append(EntityReference(
                    id=str(uuid4()),
                    entity_type=EntityType.LOCATION,
                    source=signal.get("source", "unknown"),
                    jurisdiction=signal.get("jurisdiction", "unknown"),
                    attributes=location_data,
                ))

        return entities

    async def find_correlations(
        self, entity: EntityReference
    ) -> CorrelationResult:
        """Find all correlations for an entity."""
        start_time = datetime.now(UTC)
        entity_correlations = []
        pattern_correlations = []

        # Check cache first
        cached = self._correlation_cache.get(entity.id)
        if cached:
            return CorrelationResult(
                query_entity_id=entity.id,
                entity_correlations=cached,
                total_correlations=len(cached),
            )

        # Perform correlation analysis
        async with self._lock:
            # Exact matching
            exact_matches = await self._find_exact_matches(entity)
            entity_correlations.extend(exact_matches)

            # Fuzzy matching
            if self.config.enable_probabilistic_matching:
                fuzzy_matches = await self._find_fuzzy_matches(entity)
                entity_correlations.extend(fuzzy_matches)

            # Temporal correlation
            if self.config.enable_temporal_fusion:
                temporal_matches = await self._find_temporal_correlations(entity)
                entity_correlations.extend(temporal_matches)

            # Geographic correlation
            if self.config.enable_geographic_fusion:
                geo_matches = await self._find_geographic_correlations(entity)
                entity_correlations.extend(geo_matches)

            # Pattern detection
            patterns = await self._detect_patterns(entity, entity_correlations)
            pattern_correlations.extend(patterns)

        # Filter by minimum score
        entity_correlations = [
            c for c in entity_correlations
            if c.score >= self.config.min_correlation_score
        ]

        # Limit results
        entity_correlations = entity_correlations[:self.config.max_correlations_per_entity]

        # Cache results
        self._correlation_cache[entity.id] = entity_correlations

        elapsed_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        return CorrelationResult(
            query_entity_id=entity.id,
            entity_correlations=entity_correlations,
            pattern_correlations=pattern_correlations,
            total_correlations=len(entity_correlations) + len(pattern_correlations),
            processing_time_ms=elapsed_ms,
        )

    async def _find_exact_matches(
        self, entity: EntityReference
    ) -> list[EntityCorrelation]:
        """Find exact matches for an entity."""
        correlations = []

        for cached_id, cached_entity in self._entity_cache.items():
            if cached_id == entity.id:
                continue

            if cached_entity.entity_type != entity.entity_type:
                continue

            # Check for exact attribute matches
            match_score = self._calculate_exact_match_score(entity, cached_entity)

            if match_score >= self.config.exact_match_threshold:
                correlations.append(EntityCorrelation(
                    entity1_id=entity.id,
                    entity1_type=entity.entity_type,
                    entity2_id=cached_entity.id,
                    entity2_type=cached_entity.entity_type,
                    correlation_type=CorrelationType.EXACT_MATCH,
                    score=match_score,
                    strength=self._get_strength(match_score),
                    evidence=[{
                        "type": "exact_match",
                        "matched_attributes": self._get_matched_attributes(entity, cached_entity),
                    }],
                ))

        return correlations

    def _calculate_exact_match_score(
        self, entity1: EntityReference, entity2: EntityReference
    ) -> float:
        """Calculate exact match score between two entities."""
        if entity1.entity_type != entity2.entity_type:
            return 0.0

        attrs1 = entity1.attributes
        attrs2 = entity2.attributes

        if not attrs1 or not attrs2:
            return 0.0

        # Define key attributes by entity type
        key_attrs = {
            EntityType.PERSON: ["ssn", "name", "dob", "drivers_license"],
            EntityType.VEHICLE: ["vin", "plate", "make_model"],
            EntityType.WEAPON: ["serial_number", "type", "caliber"],
            EntityType.LOCATION: ["address", "latitude", "longitude"],
        }

        attrs_to_check = key_attrs.get(entity1.entity_type, list(attrs1.keys()))

        matches = 0
        total = 0

        for attr in attrs_to_check:
            if attr in attrs1 and attr in attrs2:
                total += 1
                if attrs1[attr] == attrs2[attr]:
                    matches += 1

        return matches / total if total > 0 else 0.0

    def _get_matched_attributes(
        self, entity1: EntityReference, entity2: EntityReference
    ) -> list[str]:
        """Get list of matched attributes between entities."""
        matched = []
        attrs1 = entity1.attributes
        attrs2 = entity2.attributes

        for key in attrs1:
            if key in attrs2 and attrs1[key] == attrs2[key]:
                matched.append(key)

        return matched

    async def _find_fuzzy_matches(
        self, entity: EntityReference
    ) -> list[EntityCorrelation]:
        """Find fuzzy/probabilistic matches for an entity."""
        correlations = []

        for cached_id, cached_entity in self._entity_cache.items():
            if cached_id == entity.id:
                continue

            if cached_entity.entity_type != entity.entity_type:
                continue

            # Calculate fuzzy match score
            match_score = self._calculate_fuzzy_match_score(entity, cached_entity)

            if match_score >= self.config.fuzzy_match_threshold:
                correlations.append(EntityCorrelation(
                    entity1_id=entity.id,
                    entity1_type=entity.entity_type,
                    entity2_id=cached_entity.id,
                    entity2_type=cached_entity.entity_type,
                    correlation_type=CorrelationType.FUZZY_MATCH,
                    score=match_score,
                    strength=self._get_strength(match_score),
                    evidence=[{
                        "type": "fuzzy_match",
                        "similarity_factors": self._get_similarity_factors(entity, cached_entity),
                    }],
                ))

        return correlations

    def _calculate_fuzzy_match_score(
        self, entity1: EntityReference, entity2: EntityReference
    ) -> float:
        """Calculate fuzzy match score using probabilistic matching."""
        if entity1.entity_type != entity2.entity_type:
            return 0.0

        attrs1 = entity1.attributes
        attrs2 = entity2.attributes

        if not attrs1 or not attrs2:
            return 0.0

        scores = []

        # Name similarity (for persons)
        if entity1.entity_type == EntityType.PERSON:
            name1 = attrs1.get("name", "").lower()
            name2 = attrs2.get("name", "").lower()
            if name1 and name2:
                scores.append(self._string_similarity(name1, name2))

        # Plate similarity (for vehicles)
        if entity1.entity_type == EntityType.VEHICLE:
            plate1 = attrs1.get("plate", "").upper()
            plate2 = attrs2.get("plate", "").upper()
            if plate1 and plate2:
                scores.append(self._string_similarity(plate1, plate2))

        return sum(scores) / len(scores) if scores else 0.0

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using Levenshtein-like approach."""
        if s1 == s2:
            return 1.0

        if not s1 or not s2:
            return 0.0

        # Simple character overlap similarity
        set1 = set(s1)
        set2 = set(s2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _get_similarity_factors(
        self, entity1: EntityReference, entity2: EntityReference
    ) -> dict[str, float]:
        """Get detailed similarity factors between entities."""
        factors = {}
        attrs1 = entity1.attributes
        attrs2 = entity2.attributes

        for key in set(attrs1.keys()) & set(attrs2.keys()):
            val1 = str(attrs1[key]).lower()
            val2 = str(attrs2[key]).lower()
            factors[key] = self._string_similarity(val1, val2)

        return factors

    async def _find_temporal_correlations(
        self, entity: EntityReference
    ) -> list[EntityCorrelation]:
        """Find temporal correlations within time window."""
        correlations = []
        window = timedelta(hours=self.config.temporal_window_hours)

        for cached_id, cached_entity in self._entity_cache.items():
            if cached_id == entity.id:
                continue

            # Check temporal proximity
            time_diff = abs((entity.timestamp - cached_entity.timestamp).total_seconds())
            max_diff = window.total_seconds()

            if time_diff <= max_diff:
                # Calculate temporal correlation score
                temporal_score = 1.0 - (time_diff / max_diff)

                if temporal_score >= self.config.min_correlation_score:
                    correlations.append(EntityCorrelation(
                        entity1_id=entity.id,
                        entity1_type=entity.entity_type,
                        entity2_id=cached_entity.id,
                        entity2_type=cached_entity.entity_type,
                        correlation_type=CorrelationType.TEMPORAL,
                        score=temporal_score,
                        strength=self._get_strength(temporal_score),
                        evidence=[{
                            "type": "temporal",
                            "time_difference_seconds": time_diff,
                            "window_hours": self.config.temporal_window_hours,
                        }],
                    ))

        return correlations

    async def _find_geographic_correlations(
        self, entity: EntityReference
    ) -> list[EntityCorrelation]:
        """Find geographic correlations within radius."""
        correlations = []

        entity_lat = entity.attributes.get("latitude")
        entity_lon = entity.attributes.get("longitude")

        if entity_lat is None or entity_lon is None:
            return correlations

        for cached_id, cached_entity in self._entity_cache.items():
            if cached_id == entity.id:
                continue

            cached_lat = cached_entity.attributes.get("latitude")
            cached_lon = cached_entity.attributes.get("longitude")

            if cached_lat is None or cached_lon is None:
                continue

            # Calculate distance
            distance = self._haversine_distance(
                entity_lat, entity_lon, cached_lat, cached_lon
            )

            if distance <= self.config.geographic_radius_meters:
                # Calculate geographic correlation score
                geo_score = 1.0 - (distance / self.config.geographic_radius_meters)

                if geo_score >= self.config.min_correlation_score:
                    correlations.append(EntityCorrelation(
                        entity1_id=entity.id,
                        entity1_type=entity.entity_type,
                        entity2_id=cached_entity.id,
                        entity2_type=cached_entity.entity_type,
                        correlation_type=CorrelationType.GEOGRAPHIC,
                        score=geo_score,
                        strength=self._get_strength(geo_score),
                        evidence=[{
                            "type": "geographic",
                            "distance_meters": distance,
                            "radius_meters": self.config.geographic_radius_meters,
                        }],
                    ))

        return correlations

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points in meters."""
        import math

        R = 6371000  # Earth's radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    async def _detect_patterns(
        self,
        entity: EntityReference,
        correlations: list[EntityCorrelation],
    ) -> list[PatternCorrelation]:
        """Detect patterns from correlations."""
        patterns = []

        if len(correlations) < 2:
            return patterns

        # Group correlations by type
        by_type: dict[CorrelationType, list[EntityCorrelation]] = {}
        for corr in correlations:
            if corr.correlation_type not in by_type:
                by_type[corr.correlation_type] = []
            by_type[corr.correlation_type].append(corr)

        # Detect temporal patterns
        temporal_corrs = by_type.get(CorrelationType.TEMPORAL, [])
        if len(temporal_corrs) >= 3:
            patterns.append(PatternCorrelation(
                pattern_type="temporal_cluster",
                entities=[entity.id] + [c.entity2_id for c in temporal_corrs],
                entity_types=[entity.entity_type],
                score=sum(c.score for c in temporal_corrs) / len(temporal_corrs),
                description=f"Temporal cluster of {len(temporal_corrs) + 1} related events",
            ))

        # Detect geographic patterns
        geo_corrs = by_type.get(CorrelationType.GEOGRAPHIC, [])
        if len(geo_corrs) >= 3:
            patterns.append(PatternCorrelation(
                pattern_type="geographic_cluster",
                entities=[entity.id] + [c.entity2_id for c in geo_corrs],
                entity_types=[entity.entity_type],
                score=sum(c.score for c in geo_corrs) / len(geo_corrs),
                description=f"Geographic cluster of {len(geo_corrs) + 1} related entities",
            ))

        return patterns

    def _get_strength(self, score: float) -> CorrelationStrength:
        """Get correlation strength from score."""
        if score >= 0.95:
            return CorrelationStrength.DEFINITE
        elif score >= 0.80:
            return CorrelationStrength.STRONG
        elif score >= 0.60:
            return CorrelationStrength.MODERATE
        elif score >= 0.40:
            return CorrelationStrength.WEAK
        return CorrelationStrength.TENTATIVE

    async def add_entity(self, entity: EntityReference):
        """Add an entity to the correlation cache."""
        async with self._lock:
            self._entity_cache[entity.id] = entity

    async def remove_entity(self, entity_id: str):
        """Remove an entity from the cache."""
        async with self._lock:
            self._entity_cache.pop(entity_id, None)
            self._correlation_cache.pop(entity_id, None)

    async def infer_threat_trajectory(
        self, entity_id: str
    ) -> ThreatTrajectory | None:
        """Infer threat trajectory for an entity."""
        entity = self._entity_cache.get(entity_id)
        if not entity:
            return None

        correlations = self._correlation_cache.get(entity_id, [])
        if not correlations:
            return None

        # Analyze correlation patterns
        temporal_corrs = [
            c for c in correlations
            if c.correlation_type == CorrelationType.TEMPORAL
        ]

        # Determine trajectory type
        if len(temporal_corrs) >= 3:
            scores = [c.score for c in sorted(temporal_corrs, key=lambda x: x.timestamp)]
            if scores[-1] > scores[0]:
                trajectory_type = "escalating"
                threat_level = "high"
            elif scores[-1] < scores[0]:
                trajectory_type = "de-escalating"
                threat_level = "medium"
            else:
                trajectory_type = "stable"
                threat_level = "medium"
        else:
            trajectory_type = "unknown"
            threat_level = "low"

        return ThreatTrajectory(
            threat_level=threat_level,
            trajectory_type=trajectory_type,
            entities_involved=[entity_id] + [c.entity2_id for c in correlations[:10]],
            incidents=[],
            confidence=0.7,
            risk_factors=self._identify_risk_factors(entity, correlations),
            recommended_actions=self._generate_recommendations(threat_level),
        )

    def _identify_risk_factors(
        self,
        entity: EntityReference,
        correlations: list[EntityCorrelation],
    ) -> list[str]:
        """Identify risk factors from entity and correlations."""
        factors = []

        if len(correlations) > 10:
            factors.append("High correlation count")

        high_score_corrs = [c for c in correlations if c.score >= 0.8]
        if high_score_corrs:
            factors.append(f"{len(high_score_corrs)} strong correlations")

        if entity.entity_type == EntityType.WEAPON:
            factors.append("Weapon involvement")

        return factors

    def _generate_recommendations(self, threat_level: str) -> list[str]:
        """Generate recommendations based on threat level."""
        if threat_level == "critical":
            return [
                "Immediate officer notification",
                "Dispatch backup units",
                "Activate real-time monitoring",
            ]
        elif threat_level == "high":
            return [
                "Priority investigation assignment",
                "Enhanced surveillance",
                "Cross-reference with open cases",
            ]
        elif threat_level == "medium":
            return [
                "Add to watchlist",
                "Schedule follow-up analysis",
            ]
        return ["Archive for reference"]

    def get_stats(self) -> dict[str, Any]:
        """Get correlation engine statistics."""
        return {
            "entities_cached": len(self._entity_cache),
            "correlations_cached": sum(
                len(v) for v in self._correlation_cache.values()
            ),
            "patterns_cached": len(self._pattern_cache),
            "config": self.config.model_dump(),
        }

    async def clear_cache(self):
        """Clear all caches."""
        async with self._lock:
            self._entity_cache.clear()
            self._correlation_cache.clear()
            self._pattern_cache.clear()
