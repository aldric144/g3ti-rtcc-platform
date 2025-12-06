'use client';

import { useState, useCallback, useEffect } from 'react';
import { User, Car, MapPin, AlertTriangle, Loader2, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface GraphNode {
  id: string;
  type: string;
  label: string;
  properties?: Record<string, any>;
}

interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  properties?: Record<string, any>;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface EntityGraphProps {
  entityId?: string;
  graphData?: GraphData;
  onNodeClick?: (node: GraphNode) => void;
  depth?: number;
  maxNodes?: number;
}

/**
 * Entity Graph component for visualizing entity relationships.
 * 
 * Uses a simple canvas-based visualization for entity relationships.
 * Shows persons, vehicles, addresses, incidents, and their connections.
 */
export function EntityGraph({ 
  entityId: initialEntityId, 
  graphData: initialGraphData,
  onNodeClick,
  depth = 2,
  maxNodes = 50
}: EntityGraphProps) {
  const [entityId, setEntityId] = useState(initialEntityId || '');
  const [graphData, setGraphData] = useState<GraphData | null>(initialGraphData || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    if (initialGraphData) {
      setGraphData(initialGraphData);
    }
  }, [initialGraphData]);

  const loadGraph = async () => {
    if (!entityId.trim()) {
      setError('Please enter an entity ID');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/investigations/entities/${entityId}/graph?depth=${depth}&max_nodes=${maxNodes}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load graph');
      }

      const data = await response.json();
      setGraphData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load graph');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
    onNodeClick?.(node);
  }, [onNodeClick]);

  const getNodeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'person':
        return 'bg-blue-500';
      case 'vehicle':
        return 'bg-green-500';
      case 'address':
        return 'bg-purple-500';
      case 'incident':
        return 'bg-red-500';
      case 'weapon':
        return 'bg-orange-500';
      case 'camera':
        return 'bg-cyan-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getNodeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'person':
        return <User className="h-4 w-4 text-white" />;
      case 'vehicle':
        return <Car className="h-4 w-4 text-white" />;
      case 'address':
        return <MapPin className="h-4 w-4 text-white" />;
      case 'incident':
        return <AlertTriangle className="h-4 w-4 text-white" />;
      default:
        return <div className="h-4 w-4" />;
    }
  };

  const calculateNodePositions = (nodes: GraphNode[]) => {
    const centerX = 300;
    const centerY = 200;
    const radius = 150;
    
    return nodes.map((node, index) => {
      if (index === 0) {
        return { ...node, x: centerX, y: centerY };
      }
      const angle = (2 * Math.PI * (index - 1)) / (nodes.length - 1);
      return {
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      };
    });
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Entity Relationship Graph
        </h3>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoom(z => Math.max(0.5, z - 0.1))}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            title="Zoom out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <span className="text-sm text-gray-500">{(zoom * 100).toFixed(0)}%</span>
          <button
            onClick={() => setZoom(z => Math.min(2, z + 0.1))}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            title="Zoom in"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={() => setZoom(1)}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            title="Reset zoom"
          >
            <Maximize2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Search input */}
      {!initialGraphData && (
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            placeholder="Enter entity ID to visualize"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            onKeyDown={(e) => e.key === 'Enter' && loadGraph()}
          />
          <button
            onClick={loadGraph}
            disabled={isLoading}
            className="btn-primary flex items-center gap-2 disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              'Load Graph'
            )}
          </button>
        </div>
      )}

      {error && (
        <p className="mb-4 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      {/* Graph visualization */}
      <div 
        className="relative bg-gray-50 dark:bg-gray-900 rounded-lg overflow-hidden"
        style={{ height: '400px' }}
      >
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          </div>
        ) : graphData && graphData.nodes.length > 0 ? (
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 600 400"
            style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
          >
            {/* Edges */}
            {graphData.edges.map((edge, index) => {
              const positions = calculateNodePositions(graphData.nodes);
              const sourceNode = positions.find(n => n.id === edge.source);
              const targetNode = positions.find(n => n.id === edge.target);
              
              if (!sourceNode || !targetNode) return null;
              
              return (
                <g key={`edge-${index}`}>
                  <line
                    x1={(sourceNode as any).x}
                    y1={(sourceNode as any).y}
                    x2={(targetNode as any).x}
                    y2={(targetNode as any).y}
                    stroke="#9CA3AF"
                    strokeWidth="1"
                    strokeDasharray="4"
                  />
                  <text
                    x={((sourceNode as any).x + (targetNode as any).x) / 2}
                    y={((sourceNode as any).y + (targetNode as any).y) / 2 - 5}
                    fontSize="10"
                    fill="#6B7280"
                    textAnchor="middle"
                  >
                    {edge.relationship}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {calculateNodePositions(graphData.nodes).map((node: any, index) => (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                onClick={() => handleNodeClick(node)}
                style={{ cursor: 'pointer' }}
              >
                <circle
                  r="20"
                  className={`${getNodeColor(node.type)} fill-current`}
                  stroke={selectedNode?.id === node.id ? '#3B82F6' : 'white'}
                  strokeWidth={selectedNode?.id === node.id ? 3 : 2}
                />
                <text
                  y="35"
                  fontSize="10"
                  fill="#374151"
                  textAnchor="middle"
                  className="dark:fill-gray-300"
                >
                  {node.label.length > 15 ? node.label.substring(0, 15) + '...' : node.label}
                </text>
              </g>
            ))}
          </svg>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400">
            {initialGraphData ? 'No graph data available' : 'Enter an entity ID to visualize relationships'}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-3">
        {['Person', 'Vehicle', 'Address', 'Incident', 'Weapon', 'Camera'].map(type => (
          <div key={type} className="flex items-center gap-1">
            <div className={`w-3 h-3 rounded-full ${getNodeColor(type)}`} />
            <span className="text-xs text-gray-600 dark:text-gray-400">{type}</span>
          </div>
        ))}
      </div>

      {/* Selected node details */}
      {selectedNode && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <h4 className="font-medium text-gray-900 dark:text-white mb-2">
            Selected: {selectedNode.label}
          </h4>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <p>Type: {selectedNode.type}</p>
            <p>ID: {selectedNode.id}</p>
            {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
              <div className="mt-2">
                <p className="font-medium">Properties:</p>
                <ul className="list-disc list-inside">
                  {Object.entries(selectedNode.properties).slice(0, 5).map(([key, value]) => (
                    <li key={key}>{key}: {String(value)}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default EntityGraph;
