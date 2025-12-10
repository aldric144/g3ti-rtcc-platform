"""
Extremist Networks Module

Provides capabilities for:
- Network graph building
- Channel/link mapping
- Influence scoring
- Radicalization trajectory analysis
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import uuid
import math


class NodeType(Enum):
    """Types of network nodes"""
    INDIVIDUAL = "individual"
    GROUP = "group"
    CHANNEL = "channel"
    WEBSITE = "website"
    SOCIAL_ACCOUNT = "social_account"
    FORUM = "forum"
    ORGANIZATION = "organization"
    EVENT = "event"
    LOCATION = "location"
    CONTENT = "content"


class EdgeType(Enum):
    """Types of network edges/relationships"""
    MEMBER_OF = "member_of"
    LEADER_OF = "leader_of"
    FOLLOWS = "follows"
    COMMUNICATES_WITH = "communicates_with"
    SHARES_CONTENT = "shares_content"
    ATTENDED = "attended"
    LOCATED_AT = "located_at"
    LINKED_TO = "linked_to"
    RECRUITED_BY = "recruited_by"
    INFLUENCED_BY = "influenced_by"
    FUNDED_BY = "funded_by"
    ASSOCIATED_WITH = "associated_with"


class IdeologyType(Enum):
    """Types of extremist ideologies"""
    WHITE_SUPREMACIST = "white_supremacist"
    NEO_NAZI = "neo_nazi"
    MILITIA = "militia"
    SOVEREIGN_CITIZEN = "sovereign_citizen"
    ANTI_GOVERNMENT = "anti_government"
    RELIGIOUS_EXTREMIST = "religious_extremist"
    ECO_TERRORIST = "eco_terrorist"
    ANARCHIST = "anarchist"
    INCEL = "incel"
    ACCELERATIONIST = "accelerationist"
    CONSPIRACY = "conspiracy"
    OTHER = "other"


class ThreatLevel(Enum):
    """Threat levels for nodes"""
    UNKNOWN = "unknown"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


class RadicalizationStage(Enum):
    """Stages of radicalization"""
    PRE_RADICALIZATION = "pre_radicalization"
    SELF_IDENTIFICATION = "self_identification"
    INDOCTRINATION = "indoctrination"
    ACTION = "action"
    POST_ACTION = "post_action"


class ActivityLevel(Enum):
    """Activity levels for nodes"""
    INACTIVE = "inactive"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class InfluenceScore:
    """Influence score for a network node"""
    score_id: str = ""
    node_id: str = ""
    overall_score: float = 0.0
    reach_score: float = 0.0
    engagement_score: float = 0.0
    authority_score: float = 0.0
    content_virality_score: float = 0.0
    network_centrality: float = 0.0
    follower_count: int = 0
    content_count: int = 0
    interaction_count: int = 0
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    factors: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.score_id:
            self.score_id = f"infscore-{uuid.uuid4().hex[:12]}"


@dataclass
class RadicalizationTrajectory:
    """Radicalization trajectory analysis for an individual"""
    trajectory_id: str = ""
    node_id: str = ""
    current_stage: RadicalizationStage = RadicalizationStage.PRE_RADICALIZATION
    risk_score: float = 0.0
    velocity: float = 0.0
    stage_history: list[dict[str, Any]] = field(default_factory=list)
    risk_indicators: list[str] = field(default_factory=list)
    protective_factors: list[str] = field(default_factory=list)
    influencer_nodes: list[str] = field(default_factory=list)
    content_consumed: list[str] = field(default_factory=list)
    behavioral_changes: list[str] = field(default_factory=list)
    first_observed: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    predicted_trajectory: str = ""
    intervention_recommended: bool = False
    intervention_type: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.trajectory_id:
            self.trajectory_id = f"traj-{uuid.uuid4().hex[:12]}"


@dataclass
class NetworkNode:
    """A node in the extremist network graph"""
    node_id: str = ""
    node_type: NodeType = NodeType.INDIVIDUAL
    name: str = ""
    aliases: list[str] = field(default_factory=list)
    description: str = ""
    ideology: Optional[IdeologyType] = None
    threat_level: ThreatLevel = ThreatLevel.UNKNOWN
    activity_level: ActivityLevel = ActivityLevel.LOW
    platform: str = ""
    platform_id: str = ""
    url: str = ""
    location: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    follower_count: int = 0
    content_count: int = 0
    influence_score: Optional[InfluenceScore] = None
    radicalization_trajectory: Optional[RadicalizationTrajectory] = None
    tags: list[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    is_monitored: bool = False
    is_verified: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.node_id:
            self.node_id = f"node-{uuid.uuid4().hex[:12]}"


@dataclass
class NetworkEdge:
    """An edge/relationship in the extremist network graph"""
    edge_id: str = ""
    source_node_id: str = ""
    target_node_id: str = ""
    edge_type: EdgeType = EdgeType.ASSOCIATED_WITH
    weight: float = 1.0
    confidence: float = 0.5
    first_observed: datetime = field(default_factory=datetime.utcnow)
    last_observed: datetime = field(default_factory=datetime.utcnow)
    observation_count: int = 1
    evidence: list[str] = field(default_factory=list)
    is_verified: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.edge_id:
            self.edge_id = f"edge-{uuid.uuid4().hex[:12]}"


@dataclass
class NetworkCluster:
    """A cluster of related nodes in the network"""
    cluster_id: str = ""
    name: str = ""
    description: str = ""
    ideology: Optional[IdeologyType] = None
    node_ids: list[str] = field(default_factory=list)
    central_node_id: str = ""
    threat_level: ThreatLevel = ThreatLevel.UNKNOWN
    total_influence: float = 0.0
    cohesion_score: float = 0.0
    growth_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.cluster_id:
            self.cluster_id = f"cluster-{uuid.uuid4().hex[:12]}"


class ExtremistNetworkAnalyzer:
    """
    Extremist Network Analyzer for mapping and analyzing
    extremist networks, influence patterns, and radicalization trajectories.
    """

    def __init__(self):
        self._nodes: dict[str, NetworkNode] = {}
        self._edges: dict[str, NetworkEdge] = {}
        self._clusters: dict[str, NetworkCluster] = {}
        self._influence_scores: dict[str, InfluenceScore] = {}
        self._trajectories: dict[str, RadicalizationTrajectory] = {}
        self._callbacks: list[Callable[[Any], None]] = []
        self._events: list[dict[str, Any]] = []

    def register_callback(self, callback: Callable[[Any], None]) -> None:
        """Register a callback for network events"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, data: Any) -> None:
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(data)
            except Exception:
                pass

    def _record_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Record an event for audit purposes"""
        self._events.append({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    def add_node(
        self,
        name: str,
        node_type: NodeType = NodeType.INDIVIDUAL,
        ideology: Optional[IdeologyType] = None,
        platform: str = "",
        platform_id: str = "",
        description: str = "",
        location: str = "",
        aliases: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
    ) -> NetworkNode:
        """Add a node to the network graph"""
        node = NetworkNode(
            node_type=node_type,
            name=name,
            aliases=aliases or [],
            description=description,
            ideology=ideology,
            platform=platform,
            platform_id=platform_id,
            location=location,
            tags=tags or [],
        )
        
        self._nodes[node.node_id] = node
        self._record_event("node_added", {"node_id": node.node_id, "name": name})
        self._notify_callbacks({"type": "node_added", "node": node})
        
        return node

    def get_node(self, node_id: str) -> Optional[NetworkNode]:
        """Get a node by ID"""
        return self._nodes.get(node_id)

    def get_node_by_platform_id(
        self, platform: str, platform_id: str
    ) -> Optional[NetworkNode]:
        """Get a node by platform and platform ID"""
        for node in self._nodes.values():
            if node.platform == platform and node.platform_id == platform_id:
                return node
        return None

    def get_all_nodes(
        self,
        node_type: Optional[NodeType] = None,
        ideology: Optional[IdeologyType] = None,
        threat_level: Optional[ThreatLevel] = None,
        limit: int = 100,
    ) -> list[NetworkNode]:
        """Get all nodes with optional filtering"""
        nodes = list(self._nodes.values())
        
        if node_type:
            nodes = [n for n in nodes if n.node_type == node_type]
        if ideology:
            nodes = [n for n in nodes if n.ideology == ideology]
        if threat_level:
            nodes = [n for n in nodes if n.threat_level == threat_level]
        
        nodes.sort(key=lambda n: n.last_active, reverse=True)
        return nodes[:limit]

    def update_node(
        self,
        node_id: str,
        threat_level: Optional[ThreatLevel] = None,
        activity_level: Optional[ActivityLevel] = None,
        follower_count: Optional[int] = None,
        is_monitored: Optional[bool] = None,
    ) -> bool:
        """Update a node's properties"""
        node = self._nodes.get(node_id)
        if not node:
            return False
        
        if threat_level:
            node.threat_level = threat_level
        if activity_level:
            node.activity_level = activity_level
        if follower_count is not None:
            node.follower_count = follower_count
        if is_monitored is not None:
            node.is_monitored = is_monitored
        
        node.last_active = datetime.utcnow()
        self._record_event("node_updated", {"node_id": node_id})
        return True

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its edges from the graph"""
        if node_id not in self._nodes:
            return False
        
        edges_to_remove = [
            e.edge_id for e in self._edges.values()
            if e.source_node_id == node_id or e.target_node_id == node_id
        ]
        for edge_id in edges_to_remove:
            del self._edges[edge_id]
        
        del self._nodes[node_id]
        self._record_event("node_removed", {"node_id": node_id})
        return True

    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        edge_type: EdgeType = EdgeType.ASSOCIATED_WITH,
        weight: float = 1.0,
        confidence: float = 0.5,
        evidence: Optional[list[str]] = None,
    ) -> Optional[NetworkEdge]:
        """Add an edge between two nodes"""
        if source_node_id not in self._nodes or target_node_id not in self._nodes:
            return None
        
        for edge in self._edges.values():
            if (edge.source_node_id == source_node_id and
                edge.target_node_id == target_node_id and
                edge.edge_type == edge_type):
                edge.observation_count += 1
                edge.last_observed = datetime.utcnow()
                edge.weight = min(edge.weight + 0.1, 10.0)
                return edge
        
        edge = NetworkEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            weight=weight,
            confidence=confidence,
            evidence=evidence or [],
        )
        
        self._edges[edge.edge_id] = edge
        self._record_event("edge_added", {
            "edge_id": edge.edge_id,
            "source": source_node_id,
            "target": target_node_id,
        })
        
        return edge

    def get_edge(self, edge_id: str) -> Optional[NetworkEdge]:
        """Get an edge by ID"""
        return self._edges.get(edge_id)

    def get_edges_for_node(
        self,
        node_id: str,
        direction: str = "both",
    ) -> list[NetworkEdge]:
        """Get all edges connected to a node"""
        edges = []
        for edge in self._edges.values():
            if direction in ["both", "outgoing"] and edge.source_node_id == node_id:
                edges.append(edge)
            elif direction in ["both", "incoming"] and edge.target_node_id == node_id:
                edges.append(edge)
        return edges

    def get_connected_nodes(
        self,
        node_id: str,
        max_depth: int = 1,
    ) -> list[NetworkNode]:
        """Get all nodes connected to a node up to max_depth"""
        visited = set()
        to_visit = [(node_id, 0)]
        connected = []
        
        while to_visit:
            current_id, depth = to_visit.pop(0)
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            if current_id != node_id:
                node = self._nodes.get(current_id)
                if node:
                    connected.append(node)
            
            if depth < max_depth:
                for edge in self._edges.values():
                    if edge.source_node_id == current_id:
                        to_visit.append((edge.target_node_id, depth + 1))
                    elif edge.target_node_id == current_id:
                        to_visit.append((edge.source_node_id, depth + 1))
        
        return connected

    def calculate_influence_score(self, node_id: str) -> Optional[InfluenceScore]:
        """Calculate influence score for a node"""
        node = self._nodes.get(node_id)
        if not node:
            return None
        
        edges = self.get_edges_for_node(node_id)
        incoming = [e for e in edges if e.target_node_id == node_id]
        outgoing = [e for e in edges if e.source_node_id == node_id]
        
        reach_score = min(node.follower_count / 10000, 1.0) * 100
        
        engagement_score = min(len(incoming) * 5, 100)
        
        authority_score = 0.0
        for edge in incoming:
            if edge.edge_type in [EdgeType.FOLLOWS, EdgeType.INFLUENCED_BY]:
                source_node = self._nodes.get(edge.source_node_id)
                if source_node and source_node.follower_count > 1000:
                    authority_score += 10
        authority_score = min(authority_score, 100)
        
        content_virality_score = min(node.content_count * 2, 100)
        
        total_nodes = len(self._nodes)
        if total_nodes > 1:
            network_centrality = (len(edges) / (total_nodes - 1)) * 100
        else:
            network_centrality = 0
        
        overall_score = (
            reach_score * 0.25 +
            engagement_score * 0.20 +
            authority_score * 0.25 +
            content_virality_score * 0.15 +
            network_centrality * 0.15
        )
        
        influence = InfluenceScore(
            node_id=node_id,
            overall_score=overall_score,
            reach_score=reach_score,
            engagement_score=engagement_score,
            authority_score=authority_score,
            content_virality_score=content_virality_score,
            network_centrality=network_centrality,
            follower_count=node.follower_count,
            content_count=node.content_count,
            interaction_count=len(edges),
            factors={
                "reach_weight": 0.25,
                "engagement_weight": 0.20,
                "authority_weight": 0.25,
                "virality_weight": 0.15,
                "centrality_weight": 0.15,
            },
        )
        
        self._influence_scores[influence.score_id] = influence
        node.influence_score = influence
        self._record_event("influence_calculated", {
            "node_id": node_id,
            "score": overall_score,
        })
        
        return influence

    def analyze_radicalization_trajectory(
        self,
        node_id: str,
        risk_indicators: Optional[list[str]] = None,
        protective_factors: Optional[list[str]] = None,
    ) -> Optional[RadicalizationTrajectory]:
        """Analyze radicalization trajectory for an individual node"""
        node = self._nodes.get(node_id)
        if not node or node.node_type != NodeType.INDIVIDUAL:
            return None
        
        risk_indicators = risk_indicators or []
        protective_factors = protective_factors or []
        
        edges = self.get_edges_for_node(node_id)
        influencer_nodes = []
        for edge in edges:
            if edge.edge_type in [EdgeType.INFLUENCED_BY, EdgeType.RECRUITED_BY]:
                influencer_nodes.append(edge.source_node_id)
        
        risk_score = 0.0
        
        risk_score += len(risk_indicators) * 10
        
        for inf_id in influencer_nodes:
            inf_node = self._nodes.get(inf_id)
            if inf_node and inf_node.threat_level in [ThreatLevel.HIGH, ThreatLevel.SEVERE]:
                risk_score += 15
        
        if node.ideology in [IdeologyType.WHITE_SUPREMACIST, IdeologyType.NEO_NAZI,
                            IdeologyType.ACCELERATIONIST]:
            risk_score += 20
        
        if node.activity_level in [ActivityLevel.HIGH, ActivityLevel.VERY_HIGH]:
            risk_score += 10
        
        risk_score -= len(protective_factors) * 5
        risk_score = max(0, min(risk_score, 100))
        
        if risk_score >= 80:
            stage = RadicalizationStage.ACTION
        elif risk_score >= 60:
            stage = RadicalizationStage.INDOCTRINATION
        elif risk_score >= 40:
            stage = RadicalizationStage.SELF_IDENTIFICATION
        else:
            stage = RadicalizationStage.PRE_RADICALIZATION
        
        velocity = 0.0
        if node.radicalization_trajectory:
            old_score = node.radicalization_trajectory.risk_score
            time_diff = (datetime.utcnow() - node.radicalization_trajectory.last_updated).days
            if time_diff > 0:
                velocity = (risk_score - old_score) / time_diff
        
        trajectory = RadicalizationTrajectory(
            node_id=node_id,
            current_stage=stage,
            risk_score=risk_score,
            velocity=velocity,
            risk_indicators=risk_indicators,
            protective_factors=protective_factors,
            influencer_nodes=influencer_nodes,
            intervention_recommended=risk_score >= 60,
            intervention_type="monitoring" if risk_score >= 60 else "",
            predicted_trajectory="escalating" if velocity > 0 else "stable",
        )
        
        self._trajectories[trajectory.trajectory_id] = trajectory
        node.radicalization_trajectory = trajectory
        self._record_event("trajectory_analyzed", {
            "node_id": node_id,
            "stage": stage.value,
            "risk_score": risk_score,
        })
        
        return trajectory

    def create_cluster(
        self,
        name: str,
        node_ids: list[str],
        ideology: Optional[IdeologyType] = None,
        description: str = "",
    ) -> NetworkCluster:
        """Create a cluster of related nodes"""
        valid_node_ids = [nid for nid in node_ids if nid in self._nodes]
        
        central_node_id = ""
        max_connections = 0
        for nid in valid_node_ids:
            connections = len(self.get_edges_for_node(nid))
            if connections > max_connections:
                max_connections = connections
                central_node_id = nid
        
        total_influence = 0.0
        for nid in valid_node_ids:
            node = self._nodes.get(nid)
            if node and node.influence_score:
                total_influence += node.influence_score.overall_score
        
        threat_level = ThreatLevel.LOW
        high_threat_count = 0
        for nid in valid_node_ids:
            node = self._nodes.get(nid)
            if node and node.threat_level in [ThreatLevel.HIGH, ThreatLevel.SEVERE]:
                high_threat_count += 1
        
        if high_threat_count >= 3:
            threat_level = ThreatLevel.SEVERE
        elif high_threat_count >= 2:
            threat_level = ThreatLevel.HIGH
        elif high_threat_count >= 1:
            threat_level = ThreatLevel.MODERATE
        
        cluster = NetworkCluster(
            name=name,
            description=description,
            ideology=ideology,
            node_ids=valid_node_ids,
            central_node_id=central_node_id,
            threat_level=threat_level,
            total_influence=total_influence,
        )
        
        self._clusters[cluster.cluster_id] = cluster
        self._record_event("cluster_created", {
            "cluster_id": cluster.cluster_id,
            "node_count": len(valid_node_ids),
        })
        
        return cluster

    def get_cluster(self, cluster_id: str) -> Optional[NetworkCluster]:
        """Get a cluster by ID"""
        return self._clusters.get(cluster_id)

    def get_all_clusters(
        self,
        ideology: Optional[IdeologyType] = None,
        threat_level: Optional[ThreatLevel] = None,
    ) -> list[NetworkCluster]:
        """Get all clusters with optional filtering"""
        clusters = list(self._clusters.values())
        
        if ideology:
            clusters = [c for c in clusters if c.ideology == ideology]
        if threat_level:
            clusters = [c for c in clusters if c.threat_level == threat_level]
        
        return clusters

    def detect_clusters(self, min_size: int = 3) -> list[NetworkCluster]:
        """Automatically detect clusters in the network"""
        visited = set()
        clusters = []
        
        for node_id in self._nodes:
            if node_id in visited:
                continue
            
            cluster_nodes = set()
            to_visit = [node_id]
            
            while to_visit:
                current = to_visit.pop(0)
                if current in visited:
                    continue
                
                visited.add(current)
                cluster_nodes.add(current)
                
                for edge in self._edges.values():
                    if edge.source_node_id == current and edge.target_node_id not in visited:
                        to_visit.append(edge.target_node_id)
                    elif edge.target_node_id == current and edge.source_node_id not in visited:
                        to_visit.append(edge.source_node_id)
            
            if len(cluster_nodes) >= min_size:
                ideology = None
                for nid in cluster_nodes:
                    node = self._nodes.get(nid)
                    if node and node.ideology:
                        ideology = node.ideology
                        break
                
                cluster = self.create_cluster(
                    name=f"Auto-detected Cluster {len(clusters) + 1}",
                    node_ids=list(cluster_nodes),
                    ideology=ideology,
                )
                clusters.append(cluster)
        
        return clusters

    def get_high_risk_nodes(self, threshold: float = 60.0) -> list[NetworkNode]:
        """Get nodes with high radicalization risk"""
        high_risk = []
        for node in self._nodes.values():
            if node.radicalization_trajectory:
                if node.radicalization_trajectory.risk_score >= threshold:
                    high_risk.append(node)
        
        high_risk.sort(
            key=lambda n: n.radicalization_trajectory.risk_score if n.radicalization_trajectory else 0,
            reverse=True
        )
        return high_risk

    def get_top_influencers(self, limit: int = 10) -> list[NetworkNode]:
        """Get top influencer nodes"""
        nodes_with_scores = [
            n for n in self._nodes.values()
            if n.influence_score
        ]
        nodes_with_scores.sort(
            key=lambda n: n.influence_score.overall_score if n.influence_score else 0,
            reverse=True
        )
        return nodes_with_scores[:limit]

    def export_graph(self) -> dict[str, Any]:
        """Export the network graph for visualization"""
        nodes = []
        for node in self._nodes.values():
            nodes.append({
                "id": node.node_id,
                "label": node.name,
                "type": node.node_type.value,
                "ideology": node.ideology.value if node.ideology else None,
                "threat_level": node.threat_level.value,
                "influence": node.influence_score.overall_score if node.influence_score else 0,
            })
        
        edges = []
        for edge in self._edges.values():
            edges.append({
                "id": edge.edge_id,
                "source": edge.source_node_id,
                "target": edge.target_node_id,
                "type": edge.edge_type.value,
                "weight": edge.weight,
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "clusters": [
                {
                    "id": c.cluster_id,
                    "name": c.name,
                    "node_ids": c.node_ids,
                }
                for c in self._clusters.values()
            ],
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get network analyzer metrics"""
        nodes = list(self._nodes.values())
        edges = list(self._edges.values())
        
        node_type_counts = {}
        for node_type in NodeType:
            node_type_counts[node_type.value] = len([
                n for n in nodes if n.node_type == node_type
            ])
        
        ideology_counts = {}
        for ideology in IdeologyType:
            ideology_counts[ideology.value] = len([
                n for n in nodes if n.ideology == ideology
            ])
        
        threat_counts = {}
        for threat in ThreatLevel:
            threat_counts[threat.value] = len([
                n for n in nodes if n.threat_level == threat
            ])
        
        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "total_clusters": len(self._clusters),
            "nodes_by_type": node_type_counts,
            "nodes_by_ideology": ideology_counts,
            "nodes_by_threat_level": threat_counts,
            "monitored_nodes": len([n for n in nodes if n.is_monitored]),
            "high_risk_individuals": len(self.get_high_risk_nodes()),
            "total_events": len(self._events),
        }
