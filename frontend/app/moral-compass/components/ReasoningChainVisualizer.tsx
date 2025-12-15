'use client';

import React, { useState, useEffect } from 'react';

interface GraphNode {
  node_id: string;
  node_type: string;
  label: string;
  description: string;
  weight: number;
}

interface GraphEdge {
  edge_id: string;
  source_id: string;
  target_id: string;
  edge_type: string;
  weight: number;
  label: string;
}

interface ReasoningPath {
  path_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_weight: number;
  conclusion: string;
  confidence: number;
}

interface ExplainabilityCapsule {
  capsule_id: string;
  action_type: string;
  decision: string;
  reasoning_paths: ReasoningPath[];
  key_factors: string[];
  constraints_applied: string[];
  ethical_principles: string[];
  risk_factors: string[];
  community_considerations: string[];
  human_readable_explanation: string;
  confidence: number;
  created_at: string;
  capsule_hash: string;
}

interface GraphExport {
  nodes: GraphNode[];
  edges: GraphEdge[];
  statistics: {
    total_nodes: number;
    total_edges: number;
    capsules_generated: number;
    paths_traced: number;
    node_types: Record<string, number>;
  };
}

export default function ReasoningChainVisualizer() {
  const [graph, setGraph] = useState<GraphExport | null>(null);
  const [capsule, setCapsule] = useState<ExplainabilityCapsule | null>(null);
  const [actionType, setActionType] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedNodeType, setSelectedNodeType] = useState<string>('all');

  useEffect(() => {
    fetchGraph();
  }, []);

  const fetchGraph = async () => {
    try {
      const response = await fetch('/api/moral/graph/export');
      if (response.ok) {
        const data = await response.json();
        setGraph(data);
      }
    } catch (error) {
      console.error('Failed to fetch graph:', error);
    }
  };

  const generateCapsule = async () => {
    if (!actionType) return;

    setLoading(true);
    try {
      const response = await fetch('/api/moral/graph/capsule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_type: actionType,
          context: {},
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCapsule(data);
      }
    } catch (error) {
      console.error('Failed to generate capsule:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNodeTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'legal_constraint':
        return 'bg-blue-500/30 border-blue-500 text-blue-300';
      case 'ethical_principle':
        return 'bg-purple-500/30 border-purple-500 text-purple-300';
      case 'harm_level':
        return 'bg-red-500/30 border-red-500 text-red-300';
      case 'decision':
        return 'bg-green-500/30 border-green-500 text-green-300';
      case 'action':
        return 'bg-gold-500/30 border-gold-500 text-gold-300';
      default:
        return 'bg-slate-500/30 border-slate-500 text-slate-300';
    }
  };

  const getNodeTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'legal_constraint':
        return '📜';
      case 'ethical_principle':
        return '⚖️';
      case 'harm_level':
        return '⚠️';
      case 'decision':
        return '✓';
      case 'action':
        return '🎯';
      case 'trauma_factor':
        return '💔';
      case 'risk_factor':
        return '🔴';
      case 'cultural_context':
        return '🌍';
      case 'community_impact':
        return '👥';
      default:
        return '📌';
    }
  };

  const getEdgeTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'requires':
        return 'text-blue-400';
      case 'conflicts_with':
        return 'text-red-400';
      case 'supports':
        return 'text-green-400';
      case 'mitigates':
        return 'text-yellow-400';
      case 'leads_to':
        return 'text-purple-400';
      case 'blocks':
        return 'text-red-500';
      default:
        return 'text-slate-400';
    }
  };

  const filteredNodes = graph?.nodes.filter(node => 
    selectedNodeType === 'all' || node.node_type === selectedNodeType
  ) || [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
          <h2 className="text-xl font-semibold text-gold-400 mb-4 flex items-center gap-2">
            <span>🔗</span> Generate Reasoning Capsule
          </h2>

          <div className="mb-4">
            <label className="block text-slate-400 text-sm mb-1">Action Type</label>
            <select
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              className="w-full bg-slate-700 text-white rounded px-3 py-2 border border-slate-600 focus:border-gold-500 focus:outline-none"
            >
              <option value="">Select action type...</option>
              <option value="arrest">Arrest</option>
              <option value="search">Search</option>
              <option value="surveillance">Surveillance</option>
              <option value="use_of_force">Use of Force</option>
              <option value="traffic_stop">Traffic Stop</option>
              <option value="predictive_targeting">Predictive Targeting</option>
            </select>
          </div>

          <button
            onClick={generateCapsule}
            disabled={loading || !actionType}
            className="w-full bg-gold-500 hover:bg-gold-600 text-slate-900 font-semibold py-2 px-4 rounded transition-colors disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Explainability Capsule'}
          </button>

          {capsule && (
            <div className="mt-4 space-y-4">
              <div className="bg-slate-700/50 rounded p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">Decision</span>
                  <span className={`px-3 py-1 rounded text-sm font-semibold ${
                    capsule.decision === 'allow' ? 'bg-green-500/20 text-green-400' :
                    capsule.decision === 'deny' ? 'bg-red-500/20 text-red-400' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {capsule.decision.toUpperCase()}
                  </span>
                </div>
                <div className="text-slate-400 text-sm mb-1">Confidence</div>
                <div className="w-full bg-slate-600 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-gold-500"
                    style={{ width: `${capsule.confidence * 100}%` }}
                  />
                </div>
                <div className="text-right text-sm text-slate-400 mt-1">
                  {(capsule.confidence * 100).toFixed(0)}%
                </div>
              </div>

              <div className="bg-slate-700/50 rounded p-4">
                <div className="text-slate-400 text-sm mb-2">Human-Readable Explanation</div>
                <p className="text-white text-sm">{capsule.human_readable_explanation}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-slate-400 text-sm mb-2">Legal Constraints</div>
                  <div className="space-y-1">
                    {capsule.constraints_applied.map((constraint, idx) => (
                      <div key={idx} className="text-sm text-blue-300 flex items-center gap-1">
                        <span>📜</span> {constraint}
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-slate-400 text-sm mb-2">Ethical Principles</div>
                  <div className="space-y-1">
                    {capsule.ethical_principles.map((principle, idx) => (
                      <div key={idx} className="text-sm text-purple-300 flex items-center gap-1">
                        <span>⚖️</span> {principle}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="text-xs text-slate-500">
                Capsule ID: {capsule.capsule_id} | Hash: {capsule.capsule_hash}
              </div>
            </div>
          )}
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
          <h2 className="text-xl font-semibold text-gold-400 mb-4 flex items-center gap-2">
            <span>📊</span> Graph Statistics
          </h2>

          {graph && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-700/50 rounded p-4 text-center">
                  <div className="text-3xl font-bold text-gold-400">{graph.statistics.total_nodes}</div>
                  <div className="text-slate-400 text-sm">Total Nodes</div>
                </div>
                <div className="bg-slate-700/50 rounded p-4 text-center">
                  <div className="text-3xl font-bold text-blue-400">{graph.statistics.total_edges}</div>
                  <div className="text-slate-400 text-sm">Total Edges</div>
                </div>
                <div className="bg-slate-700/50 rounded p-4 text-center">
                  <div className="text-3xl font-bold text-purple-400">{graph.statistics.capsules_generated}</div>
                  <div className="text-slate-400 text-sm">Capsules Generated</div>
                </div>
                <div className="bg-slate-700/50 rounded p-4 text-center">
                  <div className="text-3xl font-bold text-green-400">{graph.statistics.paths_traced}</div>
                  <div className="text-slate-400 text-sm">Paths Traced</div>
                </div>
              </div>

              <div>
                <div className="text-slate-400 text-sm mb-2">Node Types Distribution</div>
                <div className="space-y-2">
                  {Object.entries(graph.statistics.node_types).map(([type, count]) => (
                    <div key={type} className="flex items-center gap-2">
                      <span>{getNodeTypeIcon(type)}</span>
                      <span className="text-slate-300 text-sm flex-1">{type.replace(/_/g, ' ')}</span>
                      <span className="text-slate-400 text-sm">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-6 border border-gold-500/20">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gold-400 flex items-center gap-2">
            <span>🕸️</span> Moral Reasoning Graph
          </h2>
          <select
            value={selectedNodeType}
            onChange={(e) => setSelectedNodeType(e.target.value)}
            className="bg-slate-700 text-white rounded px-3 py-1 border border-slate-600 focus:border-gold-500 focus:outline-none text-sm"
          >
            <option value="all">All Node Types</option>
            <option value="legal_constraint">Legal Constraints</option>
            <option value="ethical_principle">Ethical Principles</option>
            <option value="harm_level">Harm Levels</option>
            <option value="decision">Decisions</option>
          </select>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-6">
          {filteredNodes.map((node) => (
            <div
              key={node.node_id}
              className={`rounded-lg p-4 border ${getNodeTypeColor(node.node_type)}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">{getNodeTypeIcon(node.node_type)}</span>
                <span className="font-semibold">{node.label}</span>
              </div>
              <p className="text-sm opacity-80">{node.description}</p>
              <div className="mt-2 text-xs opacity-60">
                Weight: {node.weight.toFixed(2)}
              </div>
            </div>
          ))}
        </div>

        {graph && graph.edges.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-slate-300 mb-3">Relationships</h3>
            <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto">
              {graph.edges.slice(0, 15).map((edge) => (
                <div key={edge.edge_id} className="bg-slate-700/50 rounded p-2 text-sm">
                  <div className="flex items-center gap-1">
                    <span className="text-slate-400">{edge.source_id}</span>
                    <span className={getEdgeTypeColor(edge.edge_type)}>→</span>
                    <span className="text-slate-400">{edge.target_id}</span>
                  </div>
                  <div className={`text-xs ${getEdgeTypeColor(edge.edge_type)}`}>
                    {edge.edge_type.replace(/_/g, ' ')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
