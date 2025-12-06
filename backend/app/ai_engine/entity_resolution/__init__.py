"""
Entity Resolution Engine.

This module provides entity resolution capabilities for matching and merging
entities across different data sources using probabilistic matching techniques.
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.ai_engine.models import ConfidenceLevel, EntityMatch, EntityType
from app.ai_engine.pipelines import BaseResolver, PipelineContext
from app.core.logging import audit_logger, get_logger

logger = get_logger(__name__)


@dataclass
class MatchCandidate:
    """Represents a potential match between two entities."""

    entity1_id: str
    entity2_id: str
    similarity_score: float
    match_factors: dict[str, float] = field(default_factory=dict)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def edit_distance_similarity(s1: str, s2: str) -> float:
    """Calculate similarity based on edit distance (0-1 scale)."""
    if not s1 or not s2:
        return 0.0

    s1_lower = s1.lower().strip()
    s2_lower = s2.lower().strip()

    if s1_lower == s2_lower:
        return 1.0

    max_len = max(len(s1_lower), len(s2_lower))
    if max_len == 0:
        return 1.0

    distance = levenshtein_distance(s1_lower, s2_lower)
    return 1.0 - (distance / max_len)


def soundex(name: str) -> str:
    """Generate Soundex code for a name."""
    if not name:
        return ""

    name = name.upper()
    name = re.sub(r"[^A-Z]", "", name)

    if not name:
        return ""

    soundex_code = name[0]

    mapping = {
        "BFPV": "1",
        "CGJKQSXZ": "2",
        "DT": "3",
        "L": "4",
        "MN": "5",
        "R": "6",
    }

    for char in name[1:]:
        for key, value in mapping.items():
            if char in key:
                if soundex_code[-1] != value:
                    soundex_code += value
                break

    soundex_code = soundex_code[:4].ljust(4, "0")
    return soundex_code


def phonetic_similarity(name1: str, name2: str) -> float:
    """Calculate phonetic similarity using Soundex."""
    if not name1 or not name2:
        return 0.0

    soundex1 = soundex(name1)
    soundex2 = soundex(name2)

    if soundex1 == soundex2:
        return 1.0

    matching_chars = sum(c1 == c2 for c1, c2 in zip(soundex1, soundex2, strict=False))
    return matching_chars / 4.0


def normalize_plate(plate: str) -> str:
    """Normalize a license plate for comparison."""
    if not plate:
        return ""
    return re.sub(r"[^A-Z0-9]", "", plate.upper())


def plate_similarity(plate1: str, plate2: str) -> float:
    """Calculate similarity between two license plates."""
    norm1 = normalize_plate(plate1)
    norm2 = normalize_plate(plate2)

    if not norm1 or not norm2:
        return 0.0

    if norm1 == norm2:
        return 1.0

    return edit_distance_similarity(norm1, norm2)


def normalize_name(name: str) -> str:
    """Normalize a name for comparison."""
    if not name:
        return ""

    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"[^\w\s]", "", name)

    prefixes = ["mr", "mrs", "ms", "dr", "jr", "sr", "ii", "iii", "iv"]
    parts = name.split()
    parts = [p for p in parts if p not in prefixes]

    return " ".join(parts)


def name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two names."""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)

    if not norm1 or not norm2:
        return 0.0

    if norm1 == norm2:
        return 1.0

    edit_sim = edit_distance_similarity(norm1, norm2)
    phonetic_sim = phonetic_similarity(norm1, norm2)

    parts1 = set(norm1.split())
    parts2 = set(norm2.split())
    if parts1 and parts2:
        jaccard = len(parts1 & parts2) / len(parts1 | parts2)
    else:
        jaccard = 0.0

    return (edit_sim * 0.4) + (phonetic_sim * 0.3) + (jaccard * 0.3)


class EntityResolver(BaseResolver):
    """
    Main entity resolver that coordinates resolution across entity types.

    Uses probabilistic matching with multiple similarity metrics to identify
    and merge duplicate entities across different data sources.
    """

    SIMILARITY_THRESHOLD = 0.75
    HIGH_CONFIDENCE_THRESHOLD = 0.9
    MEDIUM_CONFIDENCE_THRESHOLD = 0.8

    def __init__(self) -> None:
        """Initialize the entity resolver."""
        super().__init__("entity_resolver")
        self._neo4j_manager = None

    async def initialize(self, neo4j_manager: Any) -> None:
        """Initialize with database connection."""
        self._neo4j_manager = neo4j_manager

    async def resolve(
        self, entities: list[dict[str, Any]], context: PipelineContext
    ) -> list[dict[str, Any]]:
        """
        Resolve and merge entities.

        Args:
            entities: List of entities to resolve
            context: Pipeline context

        Returns:
            List of resolved entities with merge candidates
        """
        logger.info(
            "resolving_entities",
            entity_count=len(entities),
            request_id=context.request_id,
        )

        resolved_entities = []
        processed_ids: set[str] = set()

        for i, entity in enumerate(entities):
            entity_id = entity.get("id") or entity.get("entity_id") or str(uuid.uuid4())

            if entity_id in processed_ids:
                continue

            entity_type = entity.get("entity_type") or entity.get("type")
            candidates = []

            for j, other_entity in enumerate(entities):
                if i == j:
                    continue

                other_id = other_entity.get("id") or other_entity.get("entity_id")
                if other_id in processed_ids:
                    continue

                similarity = await self.calculate_similarity(entity, other_entity)

                if similarity >= self.SIMILARITY_THRESHOLD:
                    confidence = self._get_confidence_level(similarity)
                    candidates.append(
                        MatchCandidate(
                            entity1_id=entity_id,
                            entity2_id=other_id or "",
                            similarity_score=similarity,
                            confidence=confidence,
                        )
                    )

            resolved_entity = EntityMatch(
                entity_id=entity_id,
                entity_type=EntityType(entity_type) if entity_type else EntityType.PERSON,
                confidence=max([c.similarity_score for c in candidates], default=1.0),
                source_ids=[entity_id],
                properties=entity,
                aliases=self._extract_aliases(entity),
                merge_candidates=[c.entity2_id for c in candidates],
            )

            resolved_entities.append(resolved_entity.to_dict())
            processed_ids.add(entity_id)

            for candidate in candidates:
                processed_ids.add(candidate.entity2_id)

        audit_logger.log_system_event(
            event_type="entity_resolution_completed",
            details={
                "request_id": context.request_id,
                "input_count": len(entities),
                "output_count": len(resolved_entities),
                "merge_candidates_found": sum(
                    len(e.get("merge_candidates", [])) for e in resolved_entities
                ),
            },
        )

        return resolved_entities

    async def calculate_similarity(
        self, entity1: dict[str, Any], entity2: dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two entities.

        Args:
            entity1: First entity
            entity2: Second entity

        Returns:
            Similarity score between 0 and 1
        """
        type1 = entity1.get("entity_type") or entity1.get("type")
        type2 = entity2.get("entity_type") or entity2.get("type")

        if type1 != type2:
            return 0.0

        if type1 == "person" or type1 == EntityType.PERSON.value:
            return self._calculate_person_similarity(entity1, entity2)
        elif type1 == "vehicle" or type1 == EntityType.VEHICLE.value:
            return self._calculate_vehicle_similarity(entity1, entity2)
        elif type1 == "incident" or type1 == EntityType.INCIDENT.value:
            return self._calculate_incident_similarity(entity1, entity2)
        elif type1 == "address" or type1 == EntityType.ADDRESS.value:
            return self._calculate_address_similarity(entity1, entity2)
        else:
            return self._calculate_generic_similarity(entity1, entity2)

    def _calculate_person_similarity(
        self, person1: dict[str, Any], person2: dict[str, Any]
    ) -> float:
        """Calculate similarity between two person entities."""
        scores = []
        weights = []

        name1 = person1.get("name") or person1.get("full_name") or ""
        name2 = person2.get("name") or person2.get("full_name") or ""
        if name1 and name2:
            scores.append(name_similarity(name1, name2))
            weights.append(0.4)

        dob1 = person1.get("date_of_birth") or person1.get("dob")
        dob2 = person2.get("date_of_birth") or person2.get("dob")
        if dob1 and dob2:
            scores.append(1.0 if str(dob1) == str(dob2) else 0.0)
            weights.append(0.3)

        ssn1 = person1.get("ssn") or person1.get("ssn_last4")
        ssn2 = person2.get("ssn") or person2.get("ssn_last4")
        if ssn1 and ssn2:
            scores.append(1.0 if ssn1 == ssn2 else 0.0)
            weights.append(0.5)

        dl1 = person1.get("drivers_license") or person1.get("dl_number")
        dl2 = person2.get("drivers_license") or person2.get("dl_number")
        if dl1 and dl2:
            scores.append(1.0 if dl1 == dl2 else 0.0)
            weights.append(0.4)

        addr1 = person1.get("address") or ""
        addr2 = person2.get("address") or ""
        if addr1 and addr2:
            scores.append(edit_distance_similarity(addr1, addr2))
            weights.append(0.2)

        phone1 = person1.get("phone") or person1.get("phone_number")
        phone2 = person2.get("phone") or person2.get("phone_number")
        if phone1 and phone2:
            norm_phone1 = re.sub(r"\D", "", str(phone1))
            norm_phone2 = re.sub(r"\D", "", str(phone2))
            scores.append(1.0 if norm_phone1 == norm_phone2 else 0.0)
            weights.append(0.3)

        if not scores:
            return 0.0

        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(scores, weights, strict=True)) / total_weight

        return weighted_score

    def _calculate_vehicle_similarity(
        self, vehicle1: dict[str, Any], vehicle2: dict[str, Any]
    ) -> float:
        """Calculate similarity between two vehicle entities."""
        scores = []
        weights = []

        plate1 = vehicle1.get("plate_number") or vehicle1.get("license_plate") or ""
        plate2 = vehicle2.get("plate_number") or vehicle2.get("license_plate") or ""
        if plate1 and plate2:
            scores.append(plate_similarity(plate1, plate2))
            weights.append(0.5)

        vin1 = vehicle1.get("vin") or ""
        vin2 = vehicle2.get("vin") or ""
        if vin1 and vin2:
            scores.append(1.0 if vin1.upper() == vin2.upper() else 0.0)
            weights.append(0.6)

        make1 = (vehicle1.get("make") or "").lower()
        make2 = (vehicle2.get("make") or "").lower()
        if make1 and make2:
            scores.append(1.0 if make1 == make2 else edit_distance_similarity(make1, make2))
            weights.append(0.2)

        model1 = (vehicle1.get("model") or "").lower()
        model2 = (vehicle2.get("model") or "").lower()
        if model1 and model2:
            scores.append(1.0 if model1 == model2 else edit_distance_similarity(model1, model2))
            weights.append(0.2)

        year1 = vehicle1.get("year")
        year2 = vehicle2.get("year")
        if year1 and year2:
            try:
                year_diff = abs(int(year1) - int(year2))
                scores.append(1.0 if year_diff == 0 else max(0, 1 - year_diff * 0.2))
                weights.append(0.15)
            except (ValueError, TypeError):
                pass

        color1 = (vehicle1.get("color") or "").lower()
        color2 = (vehicle2.get("color") or "").lower()
        if color1 and color2:
            scores.append(1.0 if color1 == color2 else 0.0)
            weights.append(0.1)

        if not scores:
            return 0.0

        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(scores, weights, strict=True)) / total_weight

        return weighted_score

    def _calculate_incident_similarity(
        self, incident1: dict[str, Any], incident2: dict[str, Any]
    ) -> float:
        """Calculate similarity between two incident entities."""
        scores = []
        weights = []

        case1 = incident1.get("case_number") or incident1.get("incident_number")
        case2 = incident2.get("case_number") or incident2.get("incident_number")
        if case1 and case2:
            scores.append(1.0 if str(case1) == str(case2) else 0.0)
            weights.append(0.6)

        type1 = (incident1.get("incident_type") or incident1.get("type") or "").lower()
        type2 = (incident2.get("incident_type") or incident2.get("type") or "").lower()
        if type1 and type2:
            scores.append(1.0 if type1 == type2 else edit_distance_similarity(type1, type2))
            weights.append(0.2)

        loc1 = incident1.get("location") or incident1.get("address") or ""
        loc2 = incident2.get("location") or incident2.get("address") or ""
        if loc1 and loc2:
            scores.append(edit_distance_similarity(str(loc1), str(loc2)))
            weights.append(0.3)

        time1 = incident1.get("timestamp") or incident1.get("occurred_at")
        time2 = incident2.get("timestamp") or incident2.get("occurred_at")
        if time1 and time2:
            try:
                if isinstance(time1, str):
                    time1 = datetime.fromisoformat(time1.replace("Z", "+00:00"))
                if isinstance(time2, str):
                    time2 = datetime.fromisoformat(time2.replace("Z", "+00:00"))

                time_diff = abs((time1 - time2).total_seconds())
                hour_diff = time_diff / 3600
                scores.append(max(0, 1 - hour_diff * 0.1))
                weights.append(0.25)
            except (ValueError, TypeError):
                pass

        if not scores:
            return 0.0

        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(scores, weights, strict=True)) / total_weight

        return weighted_score

    def _calculate_address_similarity(
        self, addr1: dict[str, Any], addr2: dict[str, Any]
    ) -> float:
        """Calculate similarity between two address entities."""
        scores = []
        weights = []

        street1 = (addr1.get("street") or addr1.get("address") or "").lower()
        street2 = (addr2.get("street") or addr2.get("address") or "").lower()
        if street1 and street2:
            scores.append(edit_distance_similarity(street1, street2))
            weights.append(0.4)

        city1 = (addr1.get("city") or "").lower()
        city2 = (addr2.get("city") or "").lower()
        if city1 and city2:
            scores.append(1.0 if city1 == city2 else edit_distance_similarity(city1, city2))
            weights.append(0.2)

        zip1 = addr1.get("zip_code") or addr1.get("zip") or ""
        zip2 = addr2.get("zip_code") or addr2.get("zip") or ""
        if zip1 and zip2:
            scores.append(1.0 if str(zip1)[:5] == str(zip2)[:5] else 0.0)
            weights.append(0.3)

        lat1 = addr1.get("latitude")
        lon1 = addr1.get("longitude")
        lat2 = addr2.get("latitude")
        lon2 = addr2.get("longitude")
        if all([lat1, lon1, lat2, lon2]):
            try:
                lat_diff = abs(float(lat1) - float(lat2))
                lon_diff = abs(float(lon1) - float(lon2))
                distance_approx = (lat_diff**2 + lon_diff**2) ** 0.5
                scores.append(max(0, 1 - distance_approx * 100))
                weights.append(0.4)
            except (ValueError, TypeError):
                pass

        if not scores:
            return 0.0

        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(scores, weights, strict=True)) / total_weight

        return weighted_score

    def _calculate_generic_similarity(
        self, entity1: dict[str, Any], entity2: dict[str, Any]
    ) -> float:
        """Calculate generic similarity between two entities."""
        common_keys = set(entity1.keys()) & set(entity2.keys())
        common_keys -= {"id", "entity_id", "created_at", "updated_at", "entity_type", "type"}

        if not common_keys:
            return 0.0

        scores = []
        for key in common_keys:
            val1 = entity1.get(key)
            val2 = entity2.get(key)

            if val1 is None or val2 is None:
                continue

            if isinstance(val1, str) and isinstance(val2, str):
                scores.append(edit_distance_similarity(val1, val2))
            elif val1 == val2:
                scores.append(1.0)
            else:
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 0.0

    def _get_confidence_level(self, similarity: float) -> ConfidenceLevel:
        """Get confidence level from similarity score."""
        if similarity >= self.HIGH_CONFIDENCE_THRESHOLD:
            return ConfidenceLevel.HIGH
        elif similarity >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _extract_aliases(self, entity: dict[str, Any]) -> list[str]:
        """Extract aliases from an entity."""
        aliases = []

        if entity.get("aliases"):
            if isinstance(entity["aliases"], list):
                aliases.extend(entity["aliases"])
            elif isinstance(entity["aliases"], str):
                aliases.append(entity["aliases"])

        if entity.get("aka"):
            if isinstance(entity["aka"], list):
                aliases.extend(entity["aka"])
            elif isinstance(entity["aka"], str):
                aliases.append(entity["aka"])

        if entity.get("nickname"):
            aliases.append(entity["nickname"])

        if entity.get("maiden_name"):
            aliases.append(entity["maiden_name"])

        return list(set(aliases))


class PersonAliasResolver(BaseResolver):
    """Specialized resolver for person aliases."""

    def __init__(self) -> None:
        """Initialize the person alias resolver."""
        super().__init__("person_alias_resolver")

    async def resolve(
        self, entities: list[dict[str, Any]], context: PipelineContext
    ) -> list[dict[str, Any]]:
        """Resolve person aliases."""
        persons = [
            e for e in entities
            if (e.get("entity_type") or e.get("type")) in ["person", EntityType.PERSON.value]
        ]

        resolver = EntityResolver()
        return await resolver.resolve(persons, context)

    async def calculate_similarity(
        self, entity1: dict[str, Any], entity2: dict[str, Any]
    ) -> float:
        """Calculate similarity between two persons."""
        resolver = EntityResolver()
        return resolver._calculate_person_similarity(entity1, entity2)


class VehicleAliasResolver(BaseResolver):
    """Specialized resolver for vehicle aliases (plate variations)."""

    def __init__(self) -> None:
        """Initialize the vehicle alias resolver."""
        super().__init__("vehicle_alias_resolver")

    async def resolve(
        self, entities: list[dict[str, Any]], context: PipelineContext
    ) -> list[dict[str, Any]]:
        """Resolve vehicle aliases."""
        vehicles = [
            e for e in entities
            if (e.get("entity_type") or e.get("type")) in ["vehicle", EntityType.VEHICLE.value]
        ]

        resolver = EntityResolver()
        return await resolver.resolve(vehicles, context)

    async def calculate_similarity(
        self, entity1: dict[str, Any], entity2: dict[str, Any]
    ) -> float:
        """Calculate similarity between two vehicles."""
        resolver = EntityResolver()
        return resolver._calculate_vehicle_similarity(entity1, entity2)


class IncidentLinkageResolver(BaseResolver):
    """Specialized resolver for linking related incidents."""

    def __init__(self) -> None:
        """Initialize the incident linkage resolver."""
        super().__init__("incident_linkage_resolver")

    async def resolve(
        self, entities: list[dict[str, Any]], context: PipelineContext
    ) -> list[dict[str, Any]]:
        """Resolve incident linkages."""
        incidents = [
            e for e in entities
            if (e.get("entity_type") or e.get("type")) in ["incident", EntityType.INCIDENT.value]
        ]

        resolver = EntityResolver()
        return await resolver.resolve(incidents, context)

    async def calculate_similarity(
        self, entity1: dict[str, Any], entity2: dict[str, Any]
    ) -> float:
        """Calculate similarity between two incidents."""
        resolver = EntityResolver()
        return resolver._calculate_incident_similarity(entity1, entity2)


async def resolve_person_aliases(
    persons: list[dict[str, Any]], context: PipelineContext
) -> list[dict[str, Any]]:
    """
    Resolve person aliases across data sources.

    Args:
        persons: List of person entities
        context: Pipeline context

    Returns:
        List of resolved persons with merge candidates
    """
    resolver = PersonAliasResolver()
    return await resolver.resolve(persons, context)


async def resolve_vehicle_aliases(
    vehicles: list[dict[str, Any]], context: PipelineContext
) -> list[dict[str, Any]]:
    """
    Resolve vehicle aliases (plate variations).

    Args:
        vehicles: List of vehicle entities
        context: Pipeline context

    Returns:
        List of resolved vehicles with merge candidates
    """
    resolver = VehicleAliasResolver()
    return await resolver.resolve(vehicles, context)


async def resolve_incident_linkages(
    incidents: list[dict[str, Any]], context: PipelineContext
) -> list[dict[str, Any]]:
    """
    Resolve incident linkages.

    Args:
        incidents: List of incident entities
        context: Pipeline context

    Returns:
        List of resolved incidents with linkage candidates
    """
    resolver = IncidentLinkageResolver()
    return await resolver.resolve(incidents, context)


__all__ = [
    "EntityResolver",
    "PersonAliasResolver",
    "VehicleAliasResolver",
    "IncidentLinkageResolver",
    "resolve_person_aliases",
    "resolve_vehicle_aliases",
    "resolve_incident_linkages",
    "edit_distance_similarity",
    "phonetic_similarity",
    "name_similarity",
    "plate_similarity",
    "MatchCandidate",
]
