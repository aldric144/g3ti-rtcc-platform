'use client';

import React, { useState, useEffect } from 'react';

interface GraphNode {
  node_id: string;
  node_type: string;
  label: string;
  case_ids: string[];
}

interface GraphEdge {
  edge_id: string;
  edge_type: string;
  source_id: string;
  target_id: string;
  weight: number;
}

interface CaseLink {
  link_id: string;
  case_id_1: string;
  case_id_2: string;
  link_type: string;
  strength: number;
  confirmed: boolean;
}

interface Props {
  caseId: string | null;
}

export default function EvidenceGraphExplorer({ caseId }: Props) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [caseLinks, setCaseLinks] = useState<CaseLink[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [viewMode, setViewMode] = useState<'graph' | 'links' | 'clusters'>('graph');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (caseId) {
      loadGraphData();
    }
  }, [caseId]);

  const loadGraphData = async () => {
    setLoading(true);
    setTimeout(() => {
      setNodes([
        { node_id: 'n1', node_type: 'case', label: 'Case #2024-001', case_ids: ['case-001'] },
        { node_id: 'n2', node_type: 'suspect', label: 'John Doe', case_ids: ['case-001'] },
        { node_id: 'n3', node_type: 'victim', label: 'Jane Smith', case_ids: ['case-001'] },
        { node_id: 'n4', node_type: 'evidence', label: 'Knife (EV-001)', case_ids: ['case-001'] },
        { node_id: 'n5', node_type: 'location', label: '123 Main St', case_ids: ['case-001'] },
        { node_id: 'n6', node_type: 'vehicle', label: 'Blue Honda Civic', case_ids: ['case-001'] },
        { node_id: 'n7', node_type: 'case', label: 'Case #2024-002', case_ids: ['case-002'] },
        { node_id: 'n8', node_type: 'suspect', label: 'Unknown Male', case_ids: ['case-002'] },
      ]);
      setEdges([
        { edge_id: 'e1', edge_type: 'suspect_of', source_id: 'n2', target_id: 'n1', weight: 0.85 },
        { edge_id: 'e2', edge_type: 'victim_of', source_id: 'n3', target_id: 'n1', weight: 1.0 },
        { edge_id: 'e3', edge_type: 'evidence_in', source_id: 'n4', target_id: 'n1', weight: 0.9 },
        { edge_id: 'e4', edge_type: 'location_of', source_id: 'n5', target_id: 'n1', weight: 1.0 },
        { edge_id: 'e5', edge_type: 'associated_with', source_id: 'n6', target_id: 'n2', weight: 0.7 },
        { edge_id: 'e6', edge_type: 'mo_match', source_id: 'n1', target_id: 'n7', weight: 0.65 },
      ]);
      setCaseLinks([
        {
          link_id: 'link-001',
          case_id_1: 'case-001',
          case_id_2: 'case-002',
          link_type: 'mo_similarity',
          strength: 0.72,
          confirmed: false,
        },
        {
          link_id: 'link-002',
          case_id_1: 'case-001',
          case_id_2: 'case-003',
          link_type: 'geographic',
          strength: 0.58,
          confirmed: true,
        },
      ]);
      setLoading(false);
    }, 500);
  };

  const getNodeColor = (type: string) => {
    const colors: Record<string, string> = {
      case: 'bg-blue-500',
      suspect: 'bg-red-500',
      victim: 'bg-yellow-500',
      evidence: 'bg-green-500',
      location: 'bg-purple-500',
      vehicle: 'bg-orange-500',
      witness: 'bg-cyan-500',
    };
    return colors[type] || 'bg-gray-500';
  };

  const getNodePosition = (index: number, total: number) => {
    const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
    const radius = 35;
    const x = 50 + radius * Math.cos(angle);
    const y = 50 + radius * Math.sin(angle);
    return { x, y };
  };

  if (!caseId) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-800 rounded-lg">
        <p className="text-gray-400">Select a case to explore evidence graph</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Evidence Graph Explorer</h2>
        <div className="flex items-center gap-4">
          <div className="flex bg-gray-700 rounded-lg p-1">
            {(['graph', 'links', 'clusters'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-4 py-2 rounded text-sm capitalize ${viewMode === mode ? 'bg-blue-600' : ''}`}
              >
                {mode}
              </button>
            ))}
          </div>
          <button
            onClick={loadGraphData}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          {viewMode === 'graph' && (
            <div className="grid grid-cols-3 gap-6">
              <div className="col-span-2 bg-gray-800 rounded-lg p-4">
                <div className="relative bg-gray-900 rounded-lg h-96 overflow-hidden">
                  <svg className="absolute inset-0 w-full h-full">
                    {edges.map((edge) => {
                      const sourceNode = nodes.find((n) => n.node_id === edge.source_id);
                      const targetNode = nodes.find((n) => n.node_id === edge.target_id);
                      if (!sourceNode || !targetNode) return null;

                      const sourceIdx = nodes.indexOf(sourceNode);
                      const targetIdx = nodes.indexOf(targetNode);
                      const sourcePos = getNodePosition(sourceIdx, nodes.length);
                      const targetPos = getNodePosition(targetIdx, nodes.length);

                      return (
                        <line
                          key={edge.edge_id}
                          x1={`${sourcePos.x}%`}
                          y1={`${sourcePos.y}%`}
                          x2={`${targetPos.x}%`}
                          y2={`${targetPos.y}%`}
                          stroke="#4B5563"
                          strokeWidth={edge.weight * 3}
                          strokeOpacity={0.6}
                        />
                      );
                    })}
                  </svg>

                  {nodes.map((node, index) => {
                    const pos = getNodePosition(index, nodes.length);
                    return (
                      <div
                        key={node.node_id}
                        className={`absolute w-12 h-12 rounded-full cursor-pointer transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center ${getNodeColor(node.node_type)} ${
                          selectedNode?.node_id === node.node_id ? 'ring-4 ring-white' : ''
                        }`}
                        style={{ left: `${pos.x}%`, top: `${pos.y}%` }}
                        onClick={() => setSelectedNode(node)}
                        title={node.label}
                      >
                        <span className="text-xs font-bold text-white">
                          {node.node_type.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    );
                  })}
                </div>

                <div className="flex items-center gap-4 mt-4">
                  <span className="text-sm text-gray-400">Legend:</span>
                  {['case', 'suspect', 'victim', 'evidence', 'location', 'vehicle'].map((type) => (
                    <div key={type} className="flex items-center gap-1">
                      <div className={`w-3 h-3 rounded-full ${getNodeColor(type)}`}></div>
                      <span className="text-xs text-gray-400 capitalize">{type}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="font-medium mb-3">Graph Statistics</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Total Nodes</span>
                      <span>{nodes.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Total Edges</span>
                      <span>{edges.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Linked Cases</span>
                      <span>{caseLinks.length}</span>
                    </div>
                  </div>
                </div>

                {selectedNode && (
                  <div className="bg-gray-800 rounded-lg p-4">
                    <h3 className="font-medium mb-3">Selected Node</h3>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-4 h-4 rounded-full ${getNodeColor(selectedNode.node_type)}`}></div>
                        <span className="capitalize">{selectedNode.node_type}</span>
                      </div>
                      <p className="text-sm font-medium">{selectedNode.label}</p>
                      <div className="text-xs text-gray-400">
                        Connected to {edges.filter((e) => e.source_id === selectedNode.node_id || e.target_id === selectedNode.node_id).length} nodes
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="font-medium mb-3">Node Types</h3>
                  <div className="space-y-2">
                    {Object.entries(
                      nodes.reduce((acc, node) => {
                        acc[node.node_type] = (acc[node.node_type] || 0) + 1;
                        return acc;
                      }, {} as Record<string, number>)
                    ).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded-full ${getNodeColor(type)}`}></div>
                          <span className="capitalize">{type}</span>
                        </div>
                        <span>{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {viewMode === 'links' && (
            <div className="space-y-4">
              <h3 className="font-medium text-gray-300">Case Links</h3>
              {caseLinks.map((link) => (
                <div key={link.link_id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-4">
                      <span className="font-medium">{link.case_id_1}</span>
                      <span className="text-gray-400">↔</span>
                      <span className="font-medium">{link.case_id_2}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {link.confirmed && (
                        <span className="px-2 py-1 bg-green-900/50 text-green-400 rounded text-xs">
                          Confirmed
                        </span>
                      )}
                      <span className="px-2 py-1 bg-gray-700 rounded text-xs capitalize">
                        {link.link_type.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-400">Strength:</span>
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${link.strength * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-blue-400">
                      {(link.strength * 100).toFixed(0)}%
                    </span>
                  </div>
                  {!link.confirmed && (
                    <div className="mt-3 flex gap-2">
                      <button className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm">
                        Confirm Link
                      </button>
                      <button className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                        Investigate
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {viewMode === 'clusters' && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium mb-4">Case Clusters</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="font-medium mb-2">Cluster #1 - Burglary Series</h4>
                  <p className="text-sm text-gray-400 mb-3">3 cases linked by MO similarity</p>
                  <div className="space-y-1">
                    <div className="text-sm">Case #2024-001</div>
                    <div className="text-sm">Case #2024-002</div>
                    <div className="text-sm">Case #2024-003</div>
                  </div>
                </div>
                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="font-medium mb-2">Cluster #2 - Geographic</h4>
                  <p className="text-sm text-gray-400 mb-3">2 cases in same area</p>
                  <div className="space-y-1">
                    <div className="text-sm">Case #2024-004</div>
                    <div className="text-sm">Case #2024-005</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
