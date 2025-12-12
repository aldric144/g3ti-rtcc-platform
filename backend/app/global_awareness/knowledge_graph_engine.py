"""
Phase 32: Global Knowledge Graph Engine

Entity relationships, influence mapping, and causal inference for global intelligence.

Features:
- Entity extraction and linking
- Relationship mapping (political, economic, military, criminal)
- Influence network analysis
- Causal inference modeling
- Temporal relationship tracking
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class EntityType(Enum):
    COUNTRY = "country"
    ORGANIZATION = "organization"
    PERSON = "person"
    LOCATION = "location"
    EVENT = "event"
    ASSET = "asset"
    THREAT_ACTOR = "threat_actor"
    INFRASTRUCTURE = "infrastructure"
    COMMODITY = "commodity"
    ALLIANCE = "alliance"


class RelationshipType(Enum):
    POLITICAL_ALLY = "political_ally"
    POLITICAL_ADVERSARY = "political_adversary"
    ECONOMIC_PARTNER = "economic_partner"
    ECONOMIC_COMPETITOR = "economic_competitor"
    MILITARY_ALLY = "military_ally"
    MILITARY_ADVERSARY = "military_adversary"
    SUPPLIES = "supplies"
    DEPENDS_ON = "depends_on"
    CONTROLS = "controls"
    INFLUENCES = "influences"
    MEMBER_OF = "member_of"
    SANCTIONS = "sanctions"
    TRADES_WITH = "trades_with"
    BORDERS = "borders"
    HOSTILE_TO = "hostile_to"
    SUPPORTS = "supports"
    OPPOSES = "opposes"


class InfluenceCategory(Enum):
    POLITICAL = "political"
    ECONOMIC = "economic"
    MILITARY = "military"
    CULTURAL = "cultural"
    TECHNOLOGICAL = "technological"
    INFORMATIONAL = "informational"


@dataclass
class Entity:
    entity_id: str
    entity_type: EntityType
    name: str
    aliases: list[str]
    attributes: dict
    metadata: dict
    created_at: datetime
    updated_at: datetime
    confidence_score: float
    sources: list[str]
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.entity_id}:{self.name}:{self.entity_type.value}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class Relationship:
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    strength: float
    confidence: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool
    evidence: list[str]
    metadata: dict
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.relationship_id}:{self.source_entity_id}:{self.target_entity_id}:{self.relationship_type.value}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class InfluenceScore:
    entity_id: str
    category: InfluenceCategory
    score: float
    rank: int
    trend: str
    factors: list[str]
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.entity_id}:{self.category.value}:{self.score}:{self.timestamp.isoformat()}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


@dataclass
class CausalLink:
    link_id: str
    cause_entity_id: str
    effect_entity_id: str
    cause_event: str
    effect_event: str
    probability: float
    time_lag_days: int
    evidence_strength: float
    mechanism: str
    timestamp: datetime
    chain_of_custody_hash: str = field(default="")

    def __post_init__(self):
        if not self.chain_of_custody_hash:
            data = f"{self.link_id}:{self.cause_entity_id}:{self.effect_entity_id}:{self.probability}"
            self.chain_of_custody_hash = hashlib.sha256(data.encode()).hexdigest()


class KnowledgeGraphEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.entities: dict[str, Entity] = {}
        self.relationships: list[Relationship] = []
        self.influence_scores: dict[str, list[InfluenceScore]] = {}
        self.causal_links: list[CausalLink] = []

        self._initialize_base_entities()
        self._initialize_base_relationships()

        self.statistics = {
            "total_entities": 0,
            "total_relationships": 0,
            "total_causal_links": 0,
            "entities_by_type": {t.value: 0 for t in EntityType},
            "relationships_by_type": {t.value: 0 for t in RelationshipType},
        }

    def _initialize_base_entities(self):
        major_countries = [
            ("USA", "United States", EntityType.COUNTRY, {"region": "North America", "gdp_rank": 1}),
            ("CHN", "China", EntityType.COUNTRY, {"region": "East Asia", "gdp_rank": 2}),
            ("RUS", "Russia", EntityType.COUNTRY, {"region": "Europe/Asia", "gdp_rank": 11}),
            ("GBR", "United Kingdom", EntityType.COUNTRY, {"region": "Europe", "gdp_rank": 6}),
            ("FRA", "France", EntityType.COUNTRY, {"region": "Europe", "gdp_rank": 7}),
            ("DEU", "Germany", EntityType.COUNTRY, {"region": "Europe", "gdp_rank": 4}),
            ("JPN", "Japan", EntityType.COUNTRY, {"region": "East Asia", "gdp_rank": 3}),
            ("IND", "India", EntityType.COUNTRY, {"region": "South Asia", "gdp_rank": 5}),
            ("BRA", "Brazil", EntityType.COUNTRY, {"region": "South America", "gdp_rank": 9}),
            ("AUS", "Australia", EntityType.COUNTRY, {"region": "Oceania", "gdp_rank": 13}),
            ("IRN", "Iran", EntityType.COUNTRY, {"region": "Middle East", "gdp_rank": 21}),
            ("PRK", "North Korea", EntityType.COUNTRY, {"region": "East Asia", "gdp_rank": 100}),
            ("ISR", "Israel", EntityType.COUNTRY, {"region": "Middle East", "gdp_rank": 29}),
            ("SAU", "Saudi Arabia", EntityType.COUNTRY, {"region": "Middle East", "gdp_rank": 18}),
            ("UKR", "Ukraine", EntityType.COUNTRY, {"region": "Europe", "gdp_rank": 55}),
        ]

        for code, name, entity_type, attrs in major_countries:
            self.create_entity(
                entity_type=entity_type,
                name=name,
                aliases=[code],
                attributes=attrs,
            )

        organizations = [
            ("NATO", "North Atlantic Treaty Organization", EntityType.ALLIANCE, {"type": "military"}),
            ("UN", "United Nations", EntityType.ORGANIZATION, {"type": "international"}),
            ("EU", "European Union", EntityType.ALLIANCE, {"type": "political_economic"}),
            ("BRICS", "BRICS", EntityType.ALLIANCE, {"type": "economic"}),
            ("OPEC", "Organization of Petroleum Exporting Countries", EntityType.ORGANIZATION, {"type": "economic"}),
            ("WHO", "World Health Organization", EntityType.ORGANIZATION, {"type": "health"}),
            ("WTO", "World Trade Organization", EntityType.ORGANIZATION, {"type": "trade"}),
        ]

        for code, name, entity_type, attrs in organizations:
            self.create_entity(
                entity_type=entity_type,
                name=name,
                aliases=[code],
                attributes=attrs,
            )

    def _initialize_base_relationships(self):
        nato_members = ["USA", "GBR", "FRA", "DEU"]
        for member in nato_members:
            member_entity = self.get_entity_by_alias(member)
            nato_entity = self.get_entity_by_alias("NATO")
            if member_entity and nato_entity:
                self.create_relationship(
                    source_entity_id=member_entity.entity_id,
                    target_entity_id=nato_entity.entity_id,
                    relationship_type=RelationshipType.MEMBER_OF,
                    strength=1.0,
                )

        adversarial_pairs = [
            ("USA", "RUS", RelationshipType.POLITICAL_ADVERSARY),
            ("USA", "CHN", RelationshipType.ECONOMIC_COMPETITOR),
            ("USA", "IRN", RelationshipType.HOSTILE_TO),
            ("USA", "PRK", RelationshipType.HOSTILE_TO),
            ("RUS", "UKR", RelationshipType.HOSTILE_TO),
        ]

        for source, target, rel_type in adversarial_pairs:
            source_entity = self.get_entity_by_alias(source)
            target_entity = self.get_entity_by_alias(target)
            if source_entity and target_entity:
                self.create_relationship(
                    source_entity_id=source_entity.entity_id,
                    target_entity_id=target_entity.entity_id,
                    relationship_type=rel_type,
                    strength=0.8,
                )

    def create_entity(
        self,
        entity_type: EntityType,
        name: str,
        aliases: list[str] = None,
        attributes: dict = None,
        metadata: dict = None,
        sources: list[str] = None,
    ) -> Entity:
        entity = Entity(
            entity_id=f"ENT-{uuid.uuid4().hex[:8].upper()}",
            entity_type=entity_type,
            name=name,
            aliases=aliases or [],
            attributes=attributes or {},
            metadata=metadata or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            confidence_score=0.9,
            sources=sources or [],
        )

        self.entities[entity.entity_id] = entity
        self.statistics["total_entities"] += 1
        self.statistics["entities_by_type"][entity_type.value] += 1
        return entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def get_entity_by_alias(self, alias: str) -> Optional[Entity]:
        for entity in self.entities.values():
            if alias in entity.aliases or alias == entity.name:
                return entity
        return None

    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        for entity in self.entities.values():
            if entity.name.lower() == name.lower():
                return entity
        return None

    def create_relationship(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: RelationshipType,
        strength: float = 0.5,
        confidence: float = 0.8,
        start_date: datetime = None,
        evidence: list[str] = None,
        metadata: dict = None,
    ) -> Relationship:
        relationship = Relationship(
            relationship_id=f"REL-{uuid.uuid4().hex[:8].upper()}",
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            strength=strength,
            confidence=confidence,
            start_date=start_date or datetime.utcnow(),
            end_date=None,
            is_active=True,
            evidence=evidence or [],
            metadata=metadata or {},
        )

        self.relationships.append(relationship)
        self.statistics["total_relationships"] += 1
        self.statistics["relationships_by_type"][relationship_type.value] += 1
        return relationship

    def get_relationships_for_entity(self, entity_id: str) -> list[Relationship]:
        return [
            r for r in self.relationships
            if r.source_entity_id == entity_id or r.target_entity_id == entity_id
        ]

    def get_relationships_by_type(self, relationship_type: RelationshipType) -> list[Relationship]:
        return [r for r in self.relationships if r.relationship_type == relationship_type]

    def calculate_influence_score(
        self,
        entity_id: str,
        category: InfluenceCategory,
    ) -> InfluenceScore:
        entity = self.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")

        relationships = self.get_relationships_for_entity(entity_id)

        base_score = 50.0
        factors = []

        outgoing_influence = sum(
            r.strength for r in relationships
            if r.source_entity_id == entity_id and r.relationship_type in [
                RelationshipType.CONTROLS, RelationshipType.INFLUENCES, RelationshipType.SUPPORTS
            ]
        )
        base_score += outgoing_influence * 10
        if outgoing_influence > 0:
            factors.append(f"Outgoing influence: {outgoing_influence:.2f}")

        membership_count = sum(
            1 for r in relationships
            if r.relationship_type == RelationshipType.MEMBER_OF
        )
        base_score += membership_count * 5
        if membership_count > 0:
            factors.append(f"Alliance memberships: {membership_count}")

        if entity.entity_type == EntityType.COUNTRY:
            gdp_rank = entity.attributes.get("gdp_rank", 100)
            economic_bonus = max(0, (100 - gdp_rank) / 2)
            base_score += economic_bonus
            factors.append(f"GDP rank bonus: {economic_bonus:.1f}")

        score = min(100.0, max(0.0, base_score))

        all_scores = sorted(
            [self._quick_influence_estimate(e) for e in self.entities.values()],
            reverse=True
        )
        rank = 1
        for s in all_scores:
            if s > score:
                rank += 1

        influence = InfluenceScore(
            entity_id=entity_id,
            category=category,
            score=score,
            rank=rank,
            trend="stable",
            factors=factors,
            timestamp=datetime.utcnow(),
        )

        if entity_id not in self.influence_scores:
            self.influence_scores[entity_id] = []
        self.influence_scores[entity_id].append(influence)

        return influence

    def _quick_influence_estimate(self, entity: Entity) -> float:
        relationships = self.get_relationships_for_entity(entity.entity_id)
        return 50.0 + len(relationships) * 5

    def create_causal_link(
        self,
        cause_entity_id: str,
        effect_entity_id: str,
        cause_event: str,
        effect_event: str,
        probability: float,
        time_lag_days: int,
        mechanism: str,
    ) -> CausalLink:
        link = CausalLink(
            link_id=f"CL-{uuid.uuid4().hex[:8].upper()}",
            cause_entity_id=cause_entity_id,
            effect_entity_id=effect_entity_id,
            cause_event=cause_event,
            effect_event=effect_event,
            probability=probability,
            time_lag_days=time_lag_days,
            evidence_strength=0.7,
            mechanism=mechanism,
            timestamp=datetime.utcnow(),
        )

        self.causal_links.append(link)
        self.statistics["total_causal_links"] += 1
        return link

    def infer_causal_chain(
        self,
        trigger_entity_id: str,
        trigger_event: str,
        max_depth: int = 3,
    ) -> list[CausalLink]:
        chain = []
        visited = set()
        queue = [(trigger_entity_id, trigger_event, 0)]

        while queue:
            current_entity, current_event, depth = queue.pop(0)
            if depth >= max_depth or current_entity in visited:
                continue

            visited.add(current_entity)

            for link in self.causal_links:
                if link.cause_entity_id == current_entity:
                    chain.append(link)
                    queue.append((link.effect_entity_id, link.effect_event, depth + 1))

        return chain

    def get_entity_network(self, entity_id: str, depth: int = 2) -> dict:
        nodes = []
        edges = []
        visited = set()

        def traverse(eid: str, current_depth: int):
            if current_depth > depth or eid in visited:
                return
            visited.add(eid)

            entity = self.get_entity(eid)
            if entity:
                nodes.append({
                    "id": entity.entity_id,
                    "name": entity.name,
                    "type": entity.entity_type.value,
                })

            for rel in self.get_relationships_for_entity(eid):
                edges.append({
                    "source": rel.source_entity_id,
                    "target": rel.target_entity_id,
                    "type": rel.relationship_type.value,
                    "strength": rel.strength,
                })

                next_id = rel.target_entity_id if rel.source_entity_id == eid else rel.source_entity_id
                traverse(next_id, current_depth + 1)

        traverse(entity_id, 0)

        return {
            "nodes": nodes,
            "edges": edges,
            "center_entity": entity_id,
            "depth": depth,
        }

    def search_entities(
        self,
        query: str,
        entity_type: EntityType = None,
        limit: int = 10,
    ) -> list[Entity]:
        results = []
        query_lower = query.lower()

        for entity in self.entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue

            if query_lower in entity.name.lower():
                results.append(entity)
            elif any(query_lower in alias.lower() for alias in entity.aliases):
                results.append(entity)

        return results[:limit]

    def get_statistics(self) -> dict:
        return self.statistics.copy()
