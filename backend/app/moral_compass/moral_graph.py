"""
Moral Reasoning Graph

Phase 35: AI Moral Compass & Societal Ethics Reasoning Engine
Graph-based moral reasoning for explainability and decision tracing.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NodeType(Enum):
    """Types of nodes in the moral graph."""
    LEGAL_CONSTRAINT = "legal_constraint"
    ETHICAL_PRINCIPLE = "ethical_principle"
    HARM_LEVEL = "harm_level"
    TRAUMA_FACTOR = "trauma_factor"
    RISK_FACTOR = "risk_factor"
    CULTURAL_CONTEXT = "cultural_context"
    COMMUNITY_IMPACT = "community_impact"
    DECISION = "decision"
    ACTION = "action"
    CONDITION = "condition"
    MITIGATION = "mitigation"


class EdgeType(Enum):
    """Types of edges in the moral graph."""
    REQUIRES = "requires"
    CONFLICTS_WITH = "conflicts_with"
    SUPPORTS = "supports"
    MITIGATES = "mitigates"
    LEADS_TO = "leads_to"
    DEPENDS_ON = "depends_on"
    INFLUENCES = "influences"
    BLOCKS = "blocks"


@dataclass
class GraphNode:
    """A node in the moral reasoning graph."""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    node_type: NodeType = NodeType.DECISION
    label: str = ""
    description: str = ""
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "label": self.label,
            "description": self.description,
            "weight": self.weight,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class GraphEdge:
    """An edge in the moral reasoning graph."""
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    target_id: str = ""
    edge_type: EdgeType = EdgeType.LEADS_TO
    weight: float = 1.0
    label: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
            "label": self.label,
            "properties": self.properties,
        }


@dataclass
class ReasoningPath:
    """A path through the moral reasoning graph."""
    path_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    total_weight: float = 0.0
    conclusion: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_id": self.path_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "total_weight": self.total_weight,
            "conclusion": self.conclusion,
            "confidence": self.confidence,
        }


@dataclass
class ExplainabilityCapsule:
    """Encapsulated explanation of moral reasoning."""
    capsule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = ""
    decision: str = ""
    reasoning_paths: List[ReasoningPath] = field(default_factory=list)
    key_factors: List[str] = field(default_factory=list)
    constraints_applied: List[str] = field(default_factory=list)
    ethical_principles: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    community_considerations: List[str] = field(default_factory=list)
    human_readable_explanation: str = ""
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    capsule_hash: str = ""
    
    def __post_init__(self):
        if not self.capsule_hash:
            self.capsule_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        content = f"{self.capsule_id}:{self.action_type}:{self.decision}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "capsule_id": self.capsule_id,
            "action_type": self.action_type,
            "decision": self.decision,
            "reasoning_paths": [p.to_dict() for p in self.reasoning_paths],
            "key_factors": self.key_factors,
            "constraints_applied": self.constraints_applied,
            "ethical_principles": self.ethical_principles,
            "risk_factors": self.risk_factors,
            "community_considerations": self.community_considerations,
            "human_readable_explanation": self.human_readable_explanation,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "capsule_hash": self.capsule_hash,
        }


class MoralGraph:
    """
    Moral Reasoning Graph.
    
    Provides graph-based moral reasoning for explainability,
    decision tracing, and responsible AI action plans.
    """
    
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
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        self.capsules: Dict[str, ExplainabilityCapsule] = {}
        self.adjacency: Dict[str, Set[str]] = {}
        self.statistics = {
            "total_nodes": 0,
            "total_edges": 0,
            "capsules_generated": 0,
            "paths_traced": 0,
        }
        
        self._initialize_base_graph()
    
    def _initialize_base_graph(self) -> None:
        """Initialize base moral reasoning graph."""
        legal_nodes = [
            GraphNode(
                node_id="legal-4a",
                node_type=NodeType.LEGAL_CONSTRAINT,
                label="4th Amendment",
                description="Protection against unreasonable searches and seizures",
                weight=1.5,
                properties={"amendment": "4th", "type": "constitutional"},
            ),
            GraphNode(
                node_id="legal-5a",
                node_type=NodeType.LEGAL_CONSTRAINT,
                label="5th Amendment",
                description="Due process and self-incrimination protection",
                weight=1.5,
                properties={"amendment": "5th", "type": "constitutional"},
            ),
            GraphNode(
                node_id="legal-14a",
                node_type=NodeType.LEGAL_CONSTRAINT,
                label="14th Amendment",
                description="Equal protection under the law",
                weight=1.5,
                properties={"amendment": "14th", "type": "constitutional"},
            ),
        ]
        
        ethical_nodes = [
            GraphNode(
                node_id="ethics-beneficence",
                node_type=NodeType.ETHICAL_PRINCIPLE,
                label="Beneficence",
                description="Act in the best interest of individuals and community",
                weight=1.0,
            ),
            GraphNode(
                node_id="ethics-nonmaleficence",
                node_type=NodeType.ETHICAL_PRINCIPLE,
                label="Non-Maleficence",
                description="Do no harm",
                weight=1.2,
            ),
            GraphNode(
                node_id="ethics-justice",
                node_type=NodeType.ETHICAL_PRINCIPLE,
                label="Justice",
                description="Fair and equal treatment",
                weight=1.1,
            ),
            GraphNode(
                node_id="ethics-autonomy",
                node_type=NodeType.ETHICAL_PRINCIPLE,
                label="Autonomy",
                description="Respect individual autonomy and rights",
                weight=1.0,
            ),
            GraphNode(
                node_id="ethics-dignity",
                node_type=NodeType.ETHICAL_PRINCIPLE,
                label="Dignity",
                description="Preserve human dignity",
                weight=1.0,
            ),
        ]
        
        harm_nodes = [
            GraphNode(
                node_id="harm-none",
                node_type=NodeType.HARM_LEVEL,
                label="No Harm",
                description="No potential harm identified",
                weight=0.0,
                properties={"level": 0},
            ),
            GraphNode(
                node_id="harm-low",
                node_type=NodeType.HARM_LEVEL,
                label="Low Harm",
                description="Minimal potential harm",
                weight=0.25,
                properties={"level": 1},
            ),
            GraphNode(
                node_id="harm-moderate",
                node_type=NodeType.HARM_LEVEL,
                label="Moderate Harm",
                description="Moderate potential harm",
                weight=0.5,
                properties={"level": 2},
            ),
            GraphNode(
                node_id="harm-high",
                node_type=NodeType.HARM_LEVEL,
                label="High Harm",
                description="Significant potential harm",
                weight=0.75,
                properties={"level": 3},
            ),
            GraphNode(
                node_id="harm-severe",
                node_type=NodeType.HARM_LEVEL,
                label="Severe Harm",
                description="Severe potential harm",
                weight=1.0,
                properties={"level": 4},
            ),
        ]
        
        decision_nodes = [
            GraphNode(
                node_id="decision-allow",
                node_type=NodeType.DECISION,
                label="Allow",
                description="Action is permitted",
                weight=1.0,
            ),
            GraphNode(
                node_id="decision-caution",
                node_type=NodeType.DECISION,
                label="Allow with Caution",
                description="Action permitted with safeguards",
                weight=0.8,
            ),
            GraphNode(
                node_id="decision-approval",
                node_type=NodeType.DECISION,
                label="Human Approval Needed",
                description="Action requires human authorization",
                weight=0.5,
            ),
            GraphNode(
                node_id="decision-deny",
                node_type=NodeType.DECISION,
                label="Deny",
                description="Action is not permitted",
                weight=0.0,
            ),
        ]
        
        for node in legal_nodes + ethical_nodes + harm_nodes + decision_nodes:
            self.add_node(node)
        
        base_edges = [
            GraphEdge(
                source_id="legal-4a",
                target_id="decision-deny",
                edge_type=EdgeType.BLOCKS,
                label="Violation blocks action",
            ),
            GraphEdge(
                source_id="legal-5a",
                target_id="decision-deny",
                edge_type=EdgeType.BLOCKS,
                label="Violation blocks action",
            ),
            GraphEdge(
                source_id="legal-14a",
                target_id="decision-deny",
                edge_type=EdgeType.BLOCKS,
                label="Violation blocks action",
            ),
            GraphEdge(
                source_id="ethics-nonmaleficence",
                target_id="harm-high",
                edge_type=EdgeType.CONFLICTS_WITH,
                label="High harm conflicts with non-maleficence",
            ),
            GraphEdge(
                source_id="harm-severe",
                target_id="decision-deny",
                edge_type=EdgeType.LEADS_TO,
                label="Severe harm leads to denial",
            ),
            GraphEdge(
                source_id="harm-high",
                target_id="decision-approval",
                edge_type=EdgeType.LEADS_TO,
                label="High harm requires approval",
            ),
            GraphEdge(
                source_id="harm-moderate",
                target_id="decision-caution",
                edge_type=EdgeType.LEADS_TO,
                label="Moderate harm requires caution",
            ),
            GraphEdge(
                source_id="harm-low",
                target_id="decision-allow",
                edge_type=EdgeType.LEADS_TO,
                label="Low harm allows action",
            ),
            GraphEdge(
                source_id="harm-none",
                target_id="decision-allow",
                edge_type=EdgeType.LEADS_TO,
                label="No harm allows action",
            ),
        ]
        
        for edge in base_edges:
            self.add_edge(edge)
    
    def add_node(self, node: GraphNode) -> GraphNode:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node
        if node.node_id not in self.adjacency:
            self.adjacency[node.node_id] = set()
        self.statistics["total_nodes"] = len(self.nodes)
        return node
    
    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        """Add an edge to the graph."""
        self.edges[edge.edge_id] = edge
        
        if edge.source_id not in self.adjacency:
            self.adjacency[edge.source_id] = set()
        self.adjacency[edge.source_id].add(edge.target_id)
        
        self.statistics["total_edges"] = len(self.edges)
        return edge
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """Get an edge by ID."""
        return self.edges.get(edge_id)
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        """Get all nodes of a specific type."""
        return [n for n in self.nodes.values() if n.node_type == node_type]
    
    def get_edges_from_node(self, node_id: str) -> List[GraphEdge]:
        """Get all edges originating from a node."""
        return [e for e in self.edges.values() if e.source_id == node_id]
    
    def get_edges_to_node(self, node_id: str) -> List[GraphEdge]:
        """Get all edges pointing to a node."""
        return [e for e in self.edges.values() if e.target_id == node_id]
    
    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 10,
    ) -> Optional[ReasoningPath]:
        """Find a path between two nodes."""
        if start_id not in self.nodes or end_id not in self.nodes:
            return None
        
        visited = set()
        queue = [(start_id, [start_id], [])]
        
        while queue:
            current, path_nodes, path_edges = queue.pop(0)
            
            if current == end_id:
                nodes = [self.nodes[nid] for nid in path_nodes]
                edges = path_edges
                
                total_weight = sum(n.weight for n in nodes)
                
                reasoning_path = ReasoningPath(
                    nodes=nodes,
                    edges=edges,
                    total_weight=total_weight,
                    conclusion=f"Path from {start_id} to {end_id}",
                    confidence=1.0 / (len(nodes) + 1),
                )
                
                self.statistics["paths_traced"] += 1
                return reasoning_path
            
            if current in visited or len(path_nodes) > max_depth:
                continue
            
            visited.add(current)
            
            for edge in self.get_edges_from_node(current):
                if edge.target_id not in visited:
                    queue.append((
                        edge.target_id,
                        path_nodes + [edge.target_id],
                        path_edges + [edge],
                    ))
        
        return None
    
    def build_reasoning_graph(
        self,
        action_type: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build a reasoning graph for an action.
        
        Args:
            action_type: Type of action
            context: Context for the action
        
        Returns:
            Dict with graph structure and analysis
        """
        action_node = GraphNode(
            node_id=f"action-{uuid.uuid4().hex[:8]}",
            node_type=NodeType.ACTION,
            label=action_type,
            description=f"Action: {action_type}",
            properties=context,
        )
        self.add_node(action_node)
        
        relevant_nodes = []
        relevant_edges = []
        
        for node in self.get_nodes_by_type(NodeType.LEGAL_CONSTRAINT):
            relevant_nodes.append(node)
            edge = GraphEdge(
                source_id=action_node.node_id,
                target_id=node.node_id,
                edge_type=EdgeType.REQUIRES,
                label=f"Must comply with {node.label}",
            )
            self.add_edge(edge)
            relevant_edges.append(edge)
        
        for node in self.get_nodes_by_type(NodeType.ETHICAL_PRINCIPLE):
            relevant_nodes.append(node)
            edge = GraphEdge(
                source_id=action_node.node_id,
                target_id=node.node_id,
                edge_type=EdgeType.DEPENDS_ON,
                label=f"Evaluated against {node.label}",
            )
            self.add_edge(edge)
            relevant_edges.append(edge)
        
        harm_level = context.get("harm_level", "low")
        harm_node_id = f"harm-{harm_level}"
        if harm_node_id in self.nodes:
            edge = GraphEdge(
                source_id=action_node.node_id,
                target_id=harm_node_id,
                edge_type=EdgeType.LEADS_TO,
                label=f"Has {harm_level} harm potential",
            )
            self.add_edge(edge)
            relevant_edges.append(edge)
        
        return {
            "action_node": action_node.to_dict(),
            "relevant_nodes": [n.to_dict() for n in relevant_nodes],
            "edges": [e.to_dict() for e in relevant_edges],
            "graph_size": {
                "nodes": len(self.nodes),
                "edges": len(self.edges),
            },
        }
    
    def generate_explainability_capsule(
        self,
        action_type: str,
        decision: str,
        context: Dict[str, Any],
    ) -> ExplainabilityCapsule:
        """
        Generate an explainability capsule for a decision.
        
        Args:
            action_type: Type of action
            decision: Decision made
            context: Context for the decision
        
        Returns:
            ExplainabilityCapsule with full explanation
        """
        capsule = ExplainabilityCapsule(
            action_type=action_type,
            decision=decision,
        )
        
        legal_nodes = self.get_nodes_by_type(NodeType.LEGAL_CONSTRAINT)
        capsule.constraints_applied = [n.label for n in legal_nodes]
        
        ethical_nodes = self.get_nodes_by_type(NodeType.ETHICAL_PRINCIPLE)
        capsule.ethical_principles = [n.label for n in ethical_nodes]
        
        capsule.key_factors = context.get("key_factors", [])
        capsule.risk_factors = context.get("risk_factors", [])
        capsule.community_considerations = context.get("community_considerations", [])
        
        decision_node_id = f"decision-{decision.lower().replace(' ', '-').replace('_', '-')}"
        if decision_node_id not in self.nodes:
            decision_node_id = "decision-allow"
        
        paths = []
        for legal_node in legal_nodes[:2]:
            path = self.find_path(legal_node.node_id, decision_node_id)
            if path:
                paths.append(path)
        
        capsule.reasoning_paths = paths
        
        capsule.human_readable_explanation = self._generate_human_explanation(
            action_type, decision, context, capsule
        )
        
        capsule.confidence = context.get("confidence", 0.8)
        capsule.capsule_hash = capsule._compute_hash()
        
        self.capsules[capsule.capsule_id] = capsule
        self.statistics["capsules_generated"] += 1
        
        return capsule
    
    def _generate_human_explanation(
        self,
        action_type: str,
        decision: str,
        context: Dict[str, Any],
        capsule: ExplainabilityCapsule,
    ) -> str:
        """Generate human-readable explanation."""
        parts = []
        
        parts.append(f"The action '{action_type}' was evaluated and the decision is: {decision}.")
        
        if capsule.constraints_applied:
            parts.append(f"Legal constraints considered: {', '.join(capsule.constraints_applied[:3])}.")
        
        if capsule.ethical_principles:
            parts.append(f"Ethical principles applied: {', '.join(capsule.ethical_principles[:3])}.")
        
        if capsule.risk_factors:
            parts.append(f"Risk factors identified: {', '.join(capsule.risk_factors[:2])}.")
        
        if capsule.community_considerations:
            parts.append(f"Community considerations: {', '.join(capsule.community_considerations[:2])}.")
        
        if decision == "deny":
            parts.append("The action was denied due to ethical or legal concerns.")
        elif decision == "human_approval_needed":
            parts.append("Human approval is required before proceeding.")
        elif decision == "allow_with_caution":
            parts.append("The action is permitted with appropriate safeguards.")
        else:
            parts.append("The action is permitted based on the evaluation.")
        
        return " ".join(parts)
    
    def generate_responsible_ai_plan(
        self,
        action_type: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a responsible AI action plan.
        
        Args:
            action_type: Type of action
            context: Context for the action
        
        Returns:
            Dict with responsible AI action plan
        """
        plan = {
            "action_type": action_type,
            "pre_action_checks": [],
            "during_action_safeguards": [],
            "post_action_requirements": [],
            "oversight_requirements": [],
            "documentation_requirements": [],
        }
        
        plan["pre_action_checks"] = [
            "Verify legal compliance",
            "Assess potential harm",
            "Check for bias indicators",
            "Review community context",
        ]
        
        plan["during_action_safeguards"] = [
            "Monitor for unintended consequences",
            "Maintain human oversight capability",
            "Document all decisions",
            "Enable intervention if needed",
        ]
        
        plan["post_action_requirements"] = [
            "Review outcomes for fairness",
            "Document lessons learned",
            "Update risk assessments",
            "Report any concerns",
        ]
        
        if context.get("high_risk", False):
            plan["oversight_requirements"].append("Supervisor approval required")
            plan["oversight_requirements"].append("Real-time monitoring")
        
        if context.get("involves_vulnerable", False):
            plan["oversight_requirements"].append("Specialized unit involvement")
            plan["oversight_requirements"].append("Enhanced documentation")
        
        plan["documentation_requirements"] = [
            "Decision rationale",
            "Factors considered",
            "Alternatives evaluated",
            "Outcome assessment",
        ]
        
        return plan
    
    def get_capsule(self, capsule_id: str) -> Optional[ExplainabilityCapsule]:
        """Get capsule by ID."""
        return self.capsules.get(capsule_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            **self.statistics,
            "node_types": {
                nt.value: len(self.get_nodes_by_type(nt))
                for nt in NodeType
            },
        }
    
    def export_graph(self) -> Dict[str, Any]:
        """Export the entire graph."""
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges.values()],
            "statistics": self.get_statistics(),
        }
