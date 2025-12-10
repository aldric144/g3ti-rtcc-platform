"use client";

import { useState, useEffect } from "react";

interface SignalNode {
  id: string;
  type: "source" | "signal" | "fusion" | "alert";
  label: string;
  value: number;
  status: "active" | "processing" | "completed" | "error";
}

interface SignalEdge {
  from: string;
  to: string;
  weight: number;
}

interface SignalMetrics {
  totalSignals: number;
  activeSignals: number;
  processingRate: number;
  avgLatencyMs: number;
  errorRate: number;
}

const mockNodes: SignalNode[] = [
  { id: "src-ai", type: "source", label: "AI Engine", value: 150, status: "active" },
  { id: "src-tactical", type: "source", label: "Tactical Engine", value: 120, status: "active" },
  { id: "src-officer", type: "source", label: "Officer Safety", value: 45, status: "active" },
  { id: "src-dispatch", type: "source", label: "Dispatch", value: 200, status: "active" },
  { id: "src-federal", type: "source", label: "Federal Systems", value: 30, status: "active" },
  { id: "src-federation", type: "source", label: "Federation Hub", value: 65, status: "active" },
  { id: "src-datalake", type: "source", label: "Data Lake", value: 80, status: "active" },
  { id: "sig-001", type: "signal", label: "Crime Pattern", value: 25, status: "processing" },
  { id: "sig-002", type: "signal", label: "Warrant Match", value: 15, status: "completed" },
  { id: "sig-003", type: "signal", label: "Vehicle Alert", value: 18, status: "active" },
  { id: "fus-001", type: "fusion", label: "Fused Intel #1", value: 45, status: "completed" },
  { id: "fus-002", type: "fusion", label: "Fused Intel #2", value: 32, status: "processing" },
  { id: "alert-001", type: "alert", label: "Officer Safety Alert", value: 1, status: "active" },
  { id: "alert-002", type: "alert", label: "BOLO Generated", value: 1, status: "completed" },
];

const nodeColors = {
  source: { bg: "bg-blue-600", border: "border-blue-400", text: "text-blue-300" },
  signal: { bg: "bg-purple-600", border: "border-purple-400", text: "text-purple-300" },
  fusion: { bg: "bg-green-600", border: "border-green-400", text: "text-green-300" },
  alert: { bg: "bg-red-600", border: "border-red-400", text: "text-red-300" },
};

const statusIndicators = {
  active: "bg-green-400 animate-pulse",
  processing: "bg-yellow-400 animate-pulse",
  completed: "bg-blue-400",
  error: "bg-red-400",
};

export default function SignalGraphView() {
  const [nodes, setNodes] = useState<SignalNode[]>(mockNodes);
  const [metrics, setMetrics] = useState<SignalMetrics>({
    totalSignals: 690,
    activeSignals: 45,
    processingRate: 125.5,
    avgLatencyMs: 23.4,
    errorRate: 0.02,
  });
  const [selectedNode, setSelectedNode] = useState<SignalNode | null>(null);
  const [viewMode, setViewMode] = useState<"grid" | "flow">("grid");

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        totalSignals: prev.totalSignals + Math.floor(Math.random() * 10),
        activeSignals: Math.floor(Math.random() * 30) + 30,
        processingRate: Math.random() * 50 + 100,
        avgLatencyMs: Math.random() * 20 + 15,
        errorRate: Math.random() * 0.05,
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const sourceNodes = nodes.filter((n) => n.type === "source");
  const signalNodes = nodes.filter((n) => n.type === "signal");
  const fusionNodes = nodes.filter((n) => n.type === "fusion");
  const alertNodes = nodes.filter((n) => n.type === "alert");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Signal Graph View</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">View:</span>
            <select
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value as "grid" | "flow")}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm"
            >
              <option value="grid">Grid View</option>
              <option value="flow">Flow View</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4 mb-6">
        <MetricCard
          label="Total Signals"
          value={metrics.totalSignals.toLocaleString()}
          color="blue"
        />
        <MetricCard
          label="Active Signals"
          value={metrics.activeSignals.toString()}
          color="green"
        />
        <MetricCard
          label="Processing Rate"
          value={`${metrics.processingRate.toFixed(1)}/s`}
          color="purple"
        />
        <MetricCard
          label="Avg Latency"
          value={`${metrics.avgLatencyMs.toFixed(1)}ms`}
          color="yellow"
        />
        <MetricCard
          label="Error Rate"
          value={`${(metrics.errorRate * 100).toFixed(2)}%`}
          color="red"
        />
      </div>

      {viewMode === "flow" ? (
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex justify-between items-start">
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Sources</h3>
              {sourceNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  onClick={() => setSelectedNode(node)}
                  isSelected={selectedNode?.id === node.id}
                />
              ))}
            </div>

            <div className="flex-1 flex items-center justify-center">
              <div className="text-gray-600 text-4xl">→</div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Signals</h3>
              {signalNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  onClick={() => setSelectedNode(node)}
                  isSelected={selectedNode?.id === node.id}
                />
              ))}
            </div>

            <div className="flex-1 flex items-center justify-center">
              <div className="text-gray-600 text-4xl">→</div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Fusions</h3>
              {fusionNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  onClick={() => setSelectedNode(node)}
                  isSelected={selectedNode?.id === node.id}
                />
              ))}
            </div>

            <div className="flex-1 flex items-center justify-center">
              <div className="text-gray-600 text-4xl">→</div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Alerts</h3>
              {alertNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  onClick={() => setSelectedNode(node)}
                  isSelected={selectedNode?.id === node.id}
                />
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-400 mb-3">
              Intelligence Sources ({sourceNodes.length})
            </h3>
            <div className="space-y-2">
              {sourceNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  onClick={() => setSelectedNode(node)}
                  isSelected={selectedNode?.id === node.id}
                />
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-medium text-purple-400 mb-3">
              Active Signals ({signalNodes.length})
            </h3>
            <div className="space-y-2">
              {signalNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  onClick={() => setSelectedNode(node)}
                  isSelected={selectedNode?.id === node.id}
                />
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-medium text-green-400 mb-3">
              Fused Intelligence ({fusionNodes.length})
            </h3>
            <div className="space-y-2">
              {fusionNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  onClick={() => setSelectedNode(node)}
                  isSelected={selectedNode?.id === node.id}
                />
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-medium text-red-400 mb-3">
              Generated Alerts ({alertNodes.length})
            </h3>
            <div className="space-y-2">
              {alertNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  onClick={() => setSelectedNode(node)}
                  isSelected={selectedNode?.id === node.id}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {selectedNode && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 mt-4">
          <h3 className="font-semibold mb-2">Node Details: {selectedNode.label}</h3>
          <div className="grid grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-400">ID:</span> {selectedNode.id}
            </div>
            <div>
              <span className="text-gray-400">Type:</span> {selectedNode.type}
            </div>
            <div>
              <span className="text-gray-400">Value:</span> {selectedNode.value}
            </div>
            <div>
              <span className="text-gray-400">Status:</span> {selectedNode.status}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: "bg-blue-900/50 border-blue-700 text-blue-300",
    green: "bg-green-900/50 border-green-700 text-green-300",
    purple: "bg-purple-900/50 border-purple-700 text-purple-300",
    yellow: "bg-yellow-900/50 border-yellow-700 text-yellow-300",
    red: "bg-red-900/50 border-red-700 text-red-300",
  };

  return (
    <div className={`rounded-lg border p-3 ${colorClasses[color]}`}>
      <div className="text-xl font-bold">{value}</div>
      <div className="text-xs opacity-80">{label}</div>
    </div>
  );
}

function NodeCard({
  node,
  onClick,
  isSelected,
}: {
  node: SignalNode;
  onClick: () => void;
  isSelected: boolean;
}) {
  const colors = nodeColors[node.type];
  const statusColor = statusIndicators[node.status];

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 rounded border ${colors.border} ${
        isSelected ? colors.bg : "bg-gray-700"
      } hover:opacity-80 transition-opacity`}
    >
      <div className="flex items-center justify-between">
        <span className={`text-sm font-medium ${colors.text}`}>{node.label}</span>
        <span className={`w-2 h-2 rounded-full ${statusColor}`} />
      </div>
      <div className="text-xs text-gray-400 mt-1">
        {node.value} {node.type === "source" ? "signals" : "items"}
      </div>
    </button>
  );
}
