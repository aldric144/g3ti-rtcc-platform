"""
Phase 20: Evidence Graph Module

Provides cross-case entity graph expansion, behavioral and temporal edges,
similarity scoring, and unsolved case linking for the Autonomous Detective AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid
import math


class NodeType(str, Enum):
    CASE = "case"
    SUSPECT = "suspect"
    VICTIM = "victim"
    WITNESS = "witness"
    EVIDENCE = "evidence"
    LOCATION = "location"
    VEHICLE = "vehicle"
    WEAPON = "weapon"
    ORGANIZATION = "organization"
    PHONE = "phone"
    ADDRESS = "address"
    BEHAVIOR = "behavior"
    MO_PATTERN = "mo_pattern"


class EdgeType(str, Enum):
    INVOLVED_IN = "involved_in"
    LINKED_TO = "linked_to"
    FOUND_AT = "found_at"
    OWNS = "owns"
    ASSOCIATED_WITH = "associated_with"
    WITNESSED = "witnessed"
    CONTACTED = "contacted"
    SIMILAR_TO = "similar_to"
    TEMPORAL_PROXIMITY = "temporal_proximity"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    BEHAVIORAL_MATCH = "behavioral_match"
    MO_MATCH = "mo_match"
    SUSPECT_OF = "suspect_of"
    VICTIM_OF = "victim_of"


class CaseStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    COLD = "cold"
    SUSPENDED = "suspended"
    CLEARED = "cleared"


@dataclass
class GraphNode:
    node_id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    case_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    edge_id: str
    edge_type: EdgeType
    source_id: str
    target_id: str
    weight: float = 1.0
    confidence: float = 0.5
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimilarityResult:
    result_id: str
    source_case_id: str
    target_case_id: str
    overall_similarity: float
    behavioral_similarity: float
    temporal_similarity: float
    geographic_similarity: float
    mo_similarity: float
    common_entities: List[str] = field(default_factory=list)
    matching_patterns: List[str] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CaseLink:
    link_id: str
    case_id_1: str
    case_id_2: str
    link_type: str
    strength: float
    evidence_basis: List[str] = field(default_factory=list)
    behavioral_basis: List[str] = field(default_factory=list)
    confirmed: bool = False
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class EvidenceGraphExpander:
    """Expands and manages cross-case entity graphs."""

    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}
        self._node_index: Dict[str, Set[str]] = {}
        self._case_nodes: Dict[str, Set[str]] = {}

    def add_node(
        self,
        node_type: NodeType,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
        case_ids: Optional[List[str]] = None,
    ) -> GraphNode:
        node_id = f"node-{uuid.uuid4().hex[:12]}"

        node = GraphNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            properties=properties or {},
            case_ids=case_ids or [],
        )
        self._nodes[node_id] = node

        if node_type.value not in self._node_index:
            self._node_index[node_type.value] = set()
        self._node_index[node_type.value].add(node_id)

        for case_id in node.case_ids:
            if case_id not in self._case_nodes:
                self._case_nodes[case_id] = set()
            self._case_nodes[case_id].add(node_id)

        return node

    def add_edge(
        self,
        edge_type: EdgeType,
        source_id: str,
        target_id: str,
        weight: float = 1.0,
        confidence: float = 0.5,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[GraphEdge]:
        if source_id not in self._nodes or target_id not in self._nodes:
            return None

        edge_id = f"edge-{uuid.uuid4().hex[:12]}"

        edge = GraphEdge(
            edge_id=edge_id,
            edge_type=edge_type,
            source_id=source_id,
            target_id=target_id,
            weight=weight,
            confidence=confidence,
            properties=properties or {},
        )
        self._edges[edge_id] = edge

        return edge

    def find_or_create_node(
        self,
        node_type: NodeType,
        label: str,
        match_properties: Optional[Dict[str, Any]] = None,
        case_id: Optional[str] = None,
    ) -> GraphNode:
        type_nodes = self._node_index.get(node_type.value, set())

        for node_id in type_nodes:
            node = self._nodes[node_id]
            if node.label.lower() == label.lower():
                if match_properties:
                    if all(node.properties.get(k) == v for k, v in match_properties.items()):
                        if case_id and case_id not in node.case_ids:
                            node.case_ids.append(case_id)
                            node.updated_at = datetime.utcnow()
                            if case_id not in self._case_nodes:
                                self._case_nodes[case_id] = set()
                            self._case_nodes[case_id].add(node_id)
                        return node
                else:
                    if case_id and case_id not in node.case_ids:
                        node.case_ids.append(case_id)
                        node.updated_at = datetime.utcnow()
                        if case_id not in self._case_nodes:
                            self._case_nodes[case_id] = set()
                        self._case_nodes[case_id].add(node_id)
                    return node

        return self.add_node(
            node_type=node_type,
            label=label,
            properties=match_properties,
            case_ids=[case_id] if case_id else [],
        )

    def expand_from_case(
        self,
        case_id: str,
        case_data: Dict[str, Any],
    ) -> List[GraphNode]:
        created_nodes = []

        case_node = self.add_node(
            node_type=NodeType.CASE,
            label=f"Case {case_id}",
            properties={
                "case_id": case_id,
                "offense_type": case_data.get("offense_type"),
                "status": case_data.get("status"),
                "date": case_data.get("date"),
            },
            case_ids=[case_id],
        )
        created_nodes.append(case_node)

        for suspect in case_data.get("suspects", []):
            suspect_node = self.find_or_create_node(
                node_type=NodeType.SUSPECT,
                label=suspect.get("name", "Unknown"),
                match_properties={"suspect_id": suspect.get("id")},
                case_id=case_id,
            )
            created_nodes.append(suspect_node)

            self.add_edge(
                edge_type=EdgeType.SUSPECT_OF,
                source_id=suspect_node.node_id,
                target_id=case_node.node_id,
                confidence=suspect.get("confidence", 0.5),
            )

        for victim in case_data.get("victims", []):
            victim_node = self.find_or_create_node(
                node_type=NodeType.VICTIM,
                label=victim.get("name", "Unknown"),
                match_properties={"victim_id": victim.get("id")},
                case_id=case_id,
            )
            created_nodes.append(victim_node)

            self.add_edge(
                edge_type=EdgeType.VICTIM_OF,
                source_id=victim_node.node_id,
                target_id=case_node.node_id,
            )

        location = case_data.get("location", {})
        if location:
            location_node = self.find_or_create_node(
                node_type=NodeType.LOCATION,
                label=location.get("address", "Unknown Location"),
                match_properties={
                    "lat": location.get("lat"),
                    "lng": location.get("lng"),
                },
                case_id=case_id,
            )
            created_nodes.append(location_node)

            self.add_edge(
                edge_type=EdgeType.FOUND_AT,
                source_id=case_node.node_id,
                target_id=location_node.node_id,
            )

        for evidence in case_data.get("evidence", []):
            evidence_node = self.add_node(
                node_type=NodeType.EVIDENCE,
                label=evidence.get("description", "Evidence"),
                properties={
                    "evidence_id": evidence.get("id"),
                    "type": evidence.get("type"),
                },
                case_ids=[case_id],
            )
            created_nodes.append(evidence_node)

            self.add_edge(
                edge_type=EdgeType.LINKED_TO,
                source_id=evidence_node.node_id,
                target_id=case_node.node_id,
            )

        for mo_pattern in case_data.get("mo_patterns", []):
            mo_node = self.find_or_create_node(
                node_type=NodeType.MO_PATTERN,
                label=mo_pattern,
                case_id=case_id,
            )
            created_nodes.append(mo_node)

            self.add_edge(
                edge_type=EdgeType.MO_MATCH,
                source_id=case_node.node_id,
                target_id=mo_node.node_id,
            )

        return created_nodes

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        return self._edges.get(edge_id)

    def get_case_nodes(self, case_id: str) -> List[GraphNode]:
        node_ids = self._case_nodes.get(case_id, set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]

    def get_connected_nodes(
        self,
        node_id: str,
        edge_types: Optional[List[EdgeType]] = None,
        max_depth: int = 1,
    ) -> List[Tuple[GraphNode, GraphEdge, int]]:
        if node_id not in self._nodes:
            return []

        visited = {node_id}
        results = []
        current_level = [(node_id, 0)]

        while current_level:
            next_level = []
            for current_id, depth in current_level:
                if depth >= max_depth:
                    continue

                for edge in self._edges.values():
                    target_id = None
                    if edge.source_id == current_id:
                        target_id = edge.target_id
                    elif edge.target_id == current_id:
                        target_id = edge.source_id

                    if target_id and target_id not in visited:
                        if edge_types is None or edge.edge_type in edge_types:
                            visited.add(target_id)
                            target_node = self._nodes.get(target_id)
                            if target_node:
                                results.append((target_node, edge, depth + 1))
                                next_level.append((target_id, depth + 1))

            current_level = next_level

        return results

    def find_shared_entities(
        self,
        case_id_1: str,
        case_id_2: str,
    ) -> List[GraphNode]:
        nodes_1 = self._case_nodes.get(case_id_1, set())
        nodes_2 = self._case_nodes.get(case_id_2, set())

        shared_ids = nodes_1.intersection(nodes_2)

        return [
            self._nodes[nid] for nid in shared_ids
            if nid in self._nodes and self._nodes[nid].node_type != NodeType.CASE
        ]

    def get_graph_statistics(self) -> Dict[str, Any]:
        node_counts = {}
        for node in self._nodes.values():
            node_counts[node.node_type.value] = node_counts.get(node.node_type.value, 0) + 1

        edge_counts = {}
        for edge in self._edges.values():
            edge_counts[edge.edge_type.value] = edge_counts.get(edge.edge_type.value, 0) + 1

        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "nodes_by_type": node_counts,
            "edges_by_type": edge_counts,
            "cases_indexed": len(self._case_nodes),
        }


class BehavioralEdgeBuilder:
    """Builds behavioral and temporal edges between graph nodes."""

    def __init__(self, graph: EvidenceGraphExpander):
        self._graph = graph

    def add_behavioral_edge(
        self,
        source_id: str,
        target_id: str,
        behavior_type: str,
        similarity: float,
        evidence: Optional[List[str]] = None,
    ) -> Optional[GraphEdge]:
        return self._graph.add_edge(
            edge_type=EdgeType.BEHAVIORAL_MATCH,
            source_id=source_id,
            target_id=target_id,
            weight=similarity,
            confidence=similarity,
            properties={
                "behavior_type": behavior_type,
                "evidence": evidence or [],
            },
        )

    def add_temporal_edge(
        self,
        source_id: str,
        target_id: str,
        time_delta_hours: float,
        temporal_pattern: Optional[str] = None,
    ) -> Optional[GraphEdge]:
        proximity_score = max(0, 1 - (time_delta_hours / 168))

        return self._graph.add_edge(
            edge_type=EdgeType.TEMPORAL_PROXIMITY,
            source_id=source_id,
            target_id=target_id,
            weight=proximity_score,
            confidence=proximity_score,
            properties={
                "time_delta_hours": time_delta_hours,
                "temporal_pattern": temporal_pattern,
            },
        )

    def add_geographic_edge(
        self,
        source_id: str,
        target_id: str,
        distance_km: float,
        geographic_pattern: Optional[str] = None,
    ) -> Optional[GraphEdge]:
        proximity_score = max(0, 1 - (distance_km / 50))

        return self._graph.add_edge(
            edge_type=EdgeType.GEOGRAPHIC_PROXIMITY,
            source_id=source_id,
            target_id=target_id,
            weight=proximity_score,
            confidence=proximity_score,
            properties={
                "distance_km": distance_km,
                "geographic_pattern": geographic_pattern,
            },
        )

    def build_case_behavioral_edges(
        self,
        case_id_1: str,
        case_id_2: str,
        case_data_1: Dict[str, Any],
        case_data_2: Dict[str, Any],
    ) -> List[GraphEdge]:
        edges = []

        case_nodes_1 = [
            n for n in self._graph.get_case_nodes(case_id_1)
            if n.node_type == NodeType.CASE
        ]
        case_nodes_2 = [
            n for n in self._graph.get_case_nodes(case_id_2)
            if n.node_type == NodeType.CASE
        ]

        if not case_nodes_1 or not case_nodes_2:
            return edges

        case_node_1 = case_nodes_1[0]
        case_node_2 = case_nodes_2[0]

        mo_1 = set(case_data_1.get("mo_patterns", []))
        mo_2 = set(case_data_2.get("mo_patterns", []))

        if mo_1 and mo_2:
            intersection = mo_1.intersection(mo_2)
            union = mo_1.union(mo_2)
            mo_similarity = len(intersection) / len(union) if union else 0

            if mo_similarity > 0.3:
                edge = self._graph.add_edge(
                    edge_type=EdgeType.MO_MATCH,
                    source_id=case_node_1.node_id,
                    target_id=case_node_2.node_id,
                    weight=mo_similarity,
                    confidence=mo_similarity,
                    properties={
                        "matching_patterns": list(intersection),
                    },
                )
                if edge:
                    edges.append(edge)

        loc_1 = case_data_1.get("location", {})
        loc_2 = case_data_2.get("location", {})

        if loc_1.get("lat") and loc_2.get("lat"):
            distance = self._calculate_distance(
                loc_1.get("lat"), loc_1.get("lng"),
                loc_2.get("lat"), loc_2.get("lng"),
            )

            if distance < 10:
                edge = self.add_geographic_edge(
                    case_node_1.node_id,
                    case_node_2.node_id,
                    distance,
                )
                if edge:
                    edges.append(edge)

        date_1 = case_data_1.get("date")
        date_2 = case_data_2.get("date")

        if date_1 and date_2:
            if isinstance(date_1, str):
                date_1 = datetime.fromisoformat(date_1.replace("Z", "+00:00"))
            if isinstance(date_2, str):
                date_2 = datetime.fromisoformat(date_2.replace("Z", "+00:00"))

            time_delta = abs((date_1 - date_2).total_seconds() / 3600)

            if time_delta < 168:
                edge = self.add_temporal_edge(
                    case_node_1.node_id,
                    case_node_2.node_id,
                    time_delta,
                )
                if edge:
                    edges.append(edge)

        return edges

    def _calculate_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
    ) -> float:
        R = 6371

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c


class SimilarityScoreEngine:
    """Calculates similarity scores between cases."""

    def __init__(self, graph: EvidenceGraphExpander):
        self._graph = graph
        self._results: Dict[str, SimilarityResult] = {}

    def calculate_similarity(
        self,
        case_id_1: str,
        case_id_2: str,
        case_data_1: Dict[str, Any],
        case_data_2: Dict[str, Any],
    ) -> SimilarityResult:
        result_id = f"sim-{uuid.uuid4().hex[:12]}"

        behavioral = self._calculate_behavioral_similarity(case_data_1, case_data_2)
        temporal = self._calculate_temporal_similarity(case_data_1, case_data_2)
        geographic = self._calculate_geographic_similarity(case_data_1, case_data_2)
        mo = self._calculate_mo_similarity(case_data_1, case_data_2)

        shared_entities = self._graph.find_shared_entities(case_id_1, case_id_2)
        entity_bonus = min(0.2, len(shared_entities) * 0.05)

        overall = (
            behavioral * 0.3 +
            temporal * 0.15 +
            geographic * 0.2 +
            mo * 0.35 +
            entity_bonus
        )

        mo_1 = set(case_data_1.get("mo_patterns", []))
        mo_2 = set(case_data_2.get("mo_patterns", []))
        matching_patterns = list(mo_1.intersection(mo_2))

        result = SimilarityResult(
            result_id=result_id,
            source_case_id=case_id_1,
            target_case_id=case_id_2,
            overall_similarity=min(1.0, overall),
            behavioral_similarity=behavioral,
            temporal_similarity=temporal,
            geographic_similarity=geographic,
            mo_similarity=mo,
            common_entities=[e.label for e in shared_entities],
            matching_patterns=matching_patterns,
        )
        self._results[result_id] = result
        return result

    def _calculate_behavioral_similarity(
        self,
        case_data_1: Dict[str, Any],
        case_data_2: Dict[str, Any],
    ) -> float:
        behaviors_1 = set(case_data_1.get("behaviors", []))
        behaviors_2 = set(case_data_2.get("behaviors", []))

        if not behaviors_1 or not behaviors_2:
            return 0.0

        intersection = behaviors_1.intersection(behaviors_2)
        union = behaviors_1.union(behaviors_2)

        return len(intersection) / len(union) if union else 0.0

    def _calculate_temporal_similarity(
        self,
        case_data_1: Dict[str, Any],
        case_data_2: Dict[str, Any],
    ) -> float:
        time_1 = case_data_1.get("time_of_day")
        time_2 = case_data_2.get("time_of_day")

        if time_1 == time_2 and time_1:
            return 0.8

        day_1 = case_data_1.get("day_of_week")
        day_2 = case_data_2.get("day_of_week")

        if day_1 == day_2 and day_1:
            return 0.5

        return 0.2

    def _calculate_geographic_similarity(
        self,
        case_data_1: Dict[str, Any],
        case_data_2: Dict[str, Any],
    ) -> float:
        loc_1 = case_data_1.get("location", {})
        loc_2 = case_data_2.get("location", {})

        if not loc_1.get("lat") or not loc_2.get("lat"):
            return 0.0

        R = 6371
        lat1 = math.radians(loc_1.get("lat", 0))
        lat2 = math.radians(loc_2.get("lat", 0))
        delta_lat = math.radians(loc_2.get("lat", 0) - loc_1.get("lat", 0))
        delta_lng = math.radians(loc_2.get("lng", 0) - loc_1.get("lng", 0))

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return max(0, 1 - (distance / 50))

    def _calculate_mo_similarity(
        self,
        case_data_1: Dict[str, Any],
        case_data_2: Dict[str, Any],
    ) -> float:
        mo_1 = set(case_data_1.get("mo_patterns", []))
        mo_2 = set(case_data_2.get("mo_patterns", []))

        if not mo_1 or not mo_2:
            return 0.0

        intersection = mo_1.intersection(mo_2)
        union = mo_1.union(mo_2)

        return len(intersection) / len(union) if union else 0.0

    def get_result(self, result_id: str) -> Optional[SimilarityResult]:
        return self._results.get(result_id)

    def find_similar_cases(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        candidate_cases: List[Tuple[str, Dict[str, Any]]],
        min_similarity: float = 0.5,
    ) -> List[SimilarityResult]:
        results = []

        for candidate_id, candidate_data in candidate_cases:
            if candidate_id == case_id:
                continue

            result = self.calculate_similarity(
                case_id, candidate_id, case_data, candidate_data
            )

            if result.overall_similarity >= min_similarity:
                results.append(result)

        results.sort(key=lambda x: x.overall_similarity, reverse=True)
        return results


class UnsolvedCaseLinker:
    """Links unsolved cases based on patterns and similarities."""

    def __init__(
        self,
        graph: EvidenceGraphExpander,
        similarity_engine: SimilarityScoreEngine,
    ):
        self._graph = graph
        self._similarity_engine = similarity_engine
        self._links: Dict[str, CaseLink] = {}
        self._case_links: Dict[str, List[str]] = {}

    def analyze_and_link(
        self,
        unsolved_cases: List[Tuple[str, Dict[str, Any]]],
        min_similarity: float = 0.6,
    ) -> List[CaseLink]:
        new_links = []

        for i, (case_id_1, case_data_1) in enumerate(unsolved_cases):
            for j in range(i + 1, len(unsolved_cases)):
                case_id_2, case_data_2 = unsolved_cases[j]

                similarity = self._similarity_engine.calculate_similarity(
                    case_id_1, case_id_2, case_data_1, case_data_2
                )

                if similarity.overall_similarity >= min_similarity:
                    link = self._create_link(
                        case_id_1, case_id_2, similarity
                    )
                    new_links.append(link)

        return new_links

    def _create_link(
        self,
        case_id_1: str,
        case_id_2: str,
        similarity: SimilarityResult,
    ) -> CaseLink:
        link_id = f"link-{uuid.uuid4().hex[:12]}"

        if similarity.mo_similarity > 0.7:
            link_type = "strong_mo_match"
        elif similarity.behavioral_similarity > 0.7:
            link_type = "behavioral_pattern"
        elif similarity.geographic_similarity > 0.8:
            link_type = "geographic_cluster"
        else:
            link_type = "general_similarity"

        link = CaseLink(
            link_id=link_id,
            case_id_1=case_id_1,
            case_id_2=case_id_2,
            link_type=link_type,
            strength=similarity.overall_similarity,
            evidence_basis=similarity.common_entities,
            behavioral_basis=similarity.matching_patterns,
        )
        self._links[link_id] = link

        if case_id_1 not in self._case_links:
            self._case_links[case_id_1] = []
        self._case_links[case_id_1].append(link_id)

        if case_id_2 not in self._case_links:
            self._case_links[case_id_2] = []
        self._case_links[case_id_2].append(link_id)

        return link

    def confirm_link(
        self,
        link_id: str,
        confirmed_by: str,
        notes: str = "",
    ) -> Optional[CaseLink]:
        link = self._links.get(link_id)
        if not link:
            return None

        link.confirmed = True
        link.confirmed_by = confirmed_by
        link.confirmed_at = datetime.utcnow()
        link.notes = notes

        return link

    def reject_link(
        self,
        link_id: str,
        rejected_by: str,
        reason: str,
    ) -> bool:
        link = self._links.get(link_id)
        if not link:
            return False

        if link.case_id_1 in self._case_links:
            self._case_links[link.case_id_1] = [
                lid for lid in self._case_links[link.case_id_1]
                if lid != link_id
            ]

        if link.case_id_2 in self._case_links:
            self._case_links[link.case_id_2] = [
                lid for lid in self._case_links[link.case_id_2]
                if lid != link_id
            ]

        del self._links[link_id]
        return True

    def get_link(self, link_id: str) -> Optional[CaseLink]:
        return self._links.get(link_id)

    def get_case_links(
        self,
        case_id: str,
        confirmed_only: bool = False,
    ) -> List[CaseLink]:
        link_ids = self._case_links.get(case_id, [])
        links = [self._links[lid] for lid in link_ids if lid in self._links]

        if confirmed_only:
            links = [l for l in links if l.confirmed]

        return links

    def get_linked_cases(self, case_id: str) -> List[str]:
        links = self.get_case_links(case_id)
        linked = []

        for link in links:
            if link.case_id_1 == case_id:
                linked.append(link.case_id_2)
            else:
                linked.append(link.case_id_1)

        return linked

    def find_case_clusters(
        self,
        min_cluster_size: int = 3,
    ) -> List[List[str]]:
        visited = set()
        clusters = []

        for case_id in self._case_links.keys():
            if case_id in visited:
                continue

            cluster = self._expand_cluster(case_id, visited)
            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)

        return clusters

    def _expand_cluster(
        self,
        start_case_id: str,
        visited: Set[str],
    ) -> List[str]:
        cluster = []
        queue = [start_case_id]

        while queue:
            case_id = queue.pop(0)
            if case_id in visited:
                continue

            visited.add(case_id)
            cluster.append(case_id)

            linked = self.get_linked_cases(case_id)
            for linked_id in linked:
                if linked_id not in visited:
                    queue.append(linked_id)

        return cluster

    def get_metrics(self) -> Dict[str, Any]:
        links = list(self._links.values())
        confirmed = [l for l in links if l.confirmed]

        link_types = {}
        for link in links:
            link_types[link.link_type] = link_types.get(link.link_type, 0) + 1

        return {
            "total_links": len(links),
            "confirmed_links": len(confirmed),
            "pending_links": len(links) - len(confirmed),
            "cases_linked": len(self._case_links),
            "by_type": link_types,
            "average_strength": (
                sum(l.strength for l in links) / len(links)
                if links else 0.0
            ),
        }


__all__ = [
    "NodeType",
    "EdgeType",
    "CaseStatus",
    "GraphNode",
    "GraphEdge",
    "SimilarityResult",
    "CaseLink",
    "EvidenceGraphExpander",
    "BehavioralEdgeBuilder",
    "SimilarityScoreEngine",
    "UnsolvedCaseLinker",
]
