'use client';

import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface Entity {
  id: string;
  type: string;
  name: string;
  properties: Record<string, unknown>;
  risk_level?: string;
}

interface Relationship {
  source_id: string;
  target_id: string;
  type: string;
  properties: Record<string, unknown>;
}

interface EntityGraphProps {
  entities: Entity[];
  relationships: Relationship[];
}

const entityColors: Record<string, string> = {
  person: '#3B82F6',
  vehicle: '#10B981',
  incident: '#EF4444',
  weapon: '#F59E0B',
  address: '#8B5CF6',
  camera: '#06B6D4',
  license_plate: '#EC4899',
  default: '#6B7280',
};

const riskColors: Record<string, string> = {
  critical: '#DC2626',
  high: '#EA580C',
  medium: '#CA8A04',
  low: '#16A34A',
  minimal: '#6B7280',
};

function getEntityColor(entity: Entity): string {
  if (entity.risk_level && riskColors[entity.risk_level.toLowerCase()]) {
    return riskColors[entity.risk_level.toLowerCase()];
  }
  return entityColors[entity.type.toLowerCase()] || entityColors.default;
}

function getEntityIcon(type: string): string {
  const icons: Record<string, string> = {
    person: 'P',
    vehicle: 'V',
    incident: 'I',
    weapon: 'W',
    address: 'A',
    camera: 'C',
    license_plate: 'L',
  };
  return icons[type.toLowerCase()] || '?';
}

export function EntityGraph({ entities, relationships }: EntityGraphProps) {
  const initialNodes: Node[] = useMemo(() => {
    const angleStep = (2 * Math.PI) / Math.max(entities.length, 1);
    const radius = Math.min(300, 50 + entities.length * 20);

    return entities.map((entity, index) => {
      const angle = index * angleStep;
      const x = 400 + radius * Math.cos(angle);
      const y = 300 + radius * Math.sin(angle);

      return {
        id: entity.id,
        position: { x, y },
        data: {
          label: (
            <div className="flex flex-col items-center">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-full text-lg font-bold text-white"
                style={{ backgroundColor: getEntityColor(entity) }}
              >
                {getEntityIcon(entity.type)}
              </div>
              <span className="mt-1 max-w-[100px] truncate text-xs font-medium text-gray-700 dark:text-gray-300">
                {entity.name}
              </span>
              {entity.risk_level && (
                <span
                  className="mt-0.5 rounded px-1.5 py-0.5 text-[10px] font-medium"
                  style={{
                    backgroundColor: riskColors[entity.risk_level.toLowerCase()] + '20',
                    color: riskColors[entity.risk_level.toLowerCase()],
                  }}
                >
                  {entity.risk_level}
                </span>
              )}
            </div>
          ),
        },
        style: {
          background: 'transparent',
          border: 'none',
          width: 'auto',
        },
      };
    });
  }, [entities]);

  const initialEdges: Edge[] = useMemo(() => {
    return relationships.map((rel, index) => ({
      id: `edge-${index}`,
      source: rel.source_id,
      target: rel.target_id,
      label: rel.type.replace(/_/g, ' '),
      labelStyle: { fontSize: 10, fill: '#6B7280' },
      labelBgStyle: { fill: 'white', fillOpacity: 0.8 },
      style: { stroke: '#9CA3AF', strokeWidth: 2 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#9CA3AF',
      },
      animated: rel.type.includes('active') || rel.type.includes('recent'),
    }));
  }, [relationships]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  if (entities.length === 0) {
    return (
      <div className="flex h-[400px] items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 dark:border-gray-600 dark:bg-gray-900">
        <p className="text-gray-500 dark:text-gray-400">
          No entities to display. Run a query to see the entity graph.
        </p>
      </div>
    );
  }

  return (
    <div className="h-[400px] rounded-lg border border-gray-200 dark:border-gray-700">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="bottom-left"
      >
        <Background color="#E5E7EB" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const entity = entities.find((e) => e.id === node.id);
            return entity ? getEntityColor(entity) : '#6B7280';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  );
}
