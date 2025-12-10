"use client";

import { useState, useEffect } from "react";

interface Pipeline {
  id: string;
  name: string;
  type: string;
  status: "running" | "paused" | "stopped" | "error";
  workers: number;
  queueSize: number;
  metrics: {
    itemsReceived: number;
    itemsProcessed: number;
    itemsFailed: number;
    avgProcessingTimeMs: number;
    throughputPerSecond: number;
  };
  stages: {
    name: string;
    status: "active" | "idle" | "error";
    itemsProcessed: number;
  }[];
  lastActivity: string;
}

const mockPipelines: Pipeline[] = [
  {
    id: "pipeline-realtime",
    name: "Real-Time Signal Pipeline",
    type: "real_time",
    status: "running",
    workers: 8,
    queueSize: 45,
    metrics: {
      itemsReceived: 15420,
      itemsProcessed: 15380,
      itemsFailed: 12,
      avgProcessingTimeMs: 18.5,
      throughputPerSecond: 125.3,
    },
    stages: [
      { name: "Ingest", status: "active", itemsProcessed: 15420 },
      { name: "Normalize", status: "active", itemsProcessed: 15410 },
      { name: "Validate", status: "active", itemsProcessed: 15400 },
      { name: "Enrich", status: "active", itemsProcessed: 15390 },
      { name: "Route", status: "active", itemsProcessed: 15380 },
    ],
    lastActivity: new Date().toISOString(),
  },
  {
    id: "pipeline-batch",
    name: "Batch Analytics Pipeline",
    type: "batch",
    status: "running",
    workers: 4,
    queueSize: 1250,
    metrics: {
      itemsReceived: 8500,
      itemsProcessed: 7200,
      itemsFailed: 45,
      avgProcessingTimeMs: 250.0,
      throughputPerSecond: 28.8,
    },
    stages: [
      { name: "Ingest", status: "active", itemsProcessed: 8500 },
      { name: "Aggregate", status: "active", itemsProcessed: 8200 },
      { name: "Analyze", status: "active", itemsProcessed: 7500 },
      { name: "Store", status: "active", itemsProcessed: 7200 },
    ],
    lastActivity: new Date(Date.now() - 5000).toISOString(),
  },
  {
    id: "pipeline-fusion",
    name: "Cross-Engine Fusion Pipeline",
    type: "fusion",
    status: "running",
    workers: 6,
    queueSize: 120,
    metrics: {
      itemsReceived: 4200,
      itemsProcessed: 4150,
      itemsFailed: 8,
      avgProcessingTimeMs: 85.2,
      throughputPerSecond: 48.7,
    },
    stages: [
      { name: "Collect", status: "active", itemsProcessed: 4200 },
      { name: "Correlate", status: "active", itemsProcessed: 4180 },
      { name: "Fuse", status: "active", itemsProcessed: 4160 },
      { name: "Score", status: "active", itemsProcessed: 4150 },
    ],
    lastActivity: new Date(Date.now() - 2000).toISOString(),
  },
  {
    id: "pipeline-officer-safety",
    name: "Officer Safety Pipeline",
    type: "officer_safety",
    status: "running",
    workers: 4,
    queueSize: 5,
    metrics: {
      itemsReceived: 890,
      itemsProcessed: 890,
      itemsFailed: 0,
      avgProcessingTimeMs: 8.2,
      throughputPerSecond: 108.5,
    },
    stages: [
      { name: "Detect", status: "active", itemsProcessed: 890 },
      { name: "Assess", status: "active", itemsProcessed: 890 },
      { name: "Alert", status: "active", itemsProcessed: 890 },
    ],
    lastActivity: new Date(Date.now() - 1000).toISOString(),
  },
  {
    id: "pipeline-alert-priority",
    name: "Alert Priority Pipeline",
    type: "alert_priority",
    status: "running",
    workers: 4,
    queueSize: 32,
    metrics: {
      itemsReceived: 2100,
      itemsProcessed: 2080,
      itemsFailed: 5,
      avgProcessingTimeMs: 35.0,
      throughputPerSecond: 60.0,
    },
    stages: [
      { name: "Receive", status: "active", itemsProcessed: 2100 },
      { name: "Score", status: "active", itemsProcessed: 2095 },
      { name: "Route", status: "active", itemsProcessed: 2080 },
    ],
    lastActivity: new Date(Date.now() - 3000).toISOString(),
  },
  {
    id: "pipeline-leads",
    name: "Investigative Lead Pipeline",
    type: "investigative_lead",
    status: "running",
    workers: 2,
    queueSize: 15,
    metrics: {
      itemsReceived: 650,
      itemsProcessed: 640,
      itemsFailed: 3,
      avgProcessingTimeMs: 120.0,
      throughputPerSecond: 8.3,
    },
    stages: [
      { name: "Analyze", status: "active", itemsProcessed: 650 },
      { name: "Generate", status: "active", itemsProcessed: 645 },
      { name: "Assign", status: "active", itemsProcessed: 640 },
    ],
    lastActivity: new Date(Date.now() - 8000).toISOString(),
  },
  {
    id: "pipeline-datalake",
    name: "Data Lake Feedback Pipeline",
    type: "data_lake_feedback",
    status: "running",
    workers: 2,
    queueSize: 500,
    metrics: {
      itemsReceived: 12000,
      itemsProcessed: 11500,
      itemsFailed: 25,
      avgProcessingTimeMs: 45.0,
      throughputPerSecond: 255.5,
    },
    stages: [
      { name: "Extract", status: "active", itemsProcessed: 12000 },
      { name: "Transform", status: "active", itemsProcessed: 11800 },
      { name: "Load", status: "active", itemsProcessed: 11500 },
    ],
    lastActivity: new Date(Date.now() - 1500).toISOString(),
  },
];

const statusColors = {
  running: "bg-green-600",
  paused: "bg-yellow-600",
  stopped: "bg-gray-600",
  error: "bg-red-600",
};

const stageStatusColors = {
  active: "bg-green-500",
  idle: "bg-gray-500",
  error: "bg-red-500",
};

export default function PipelineStatusView() {
  const [pipelines, setPipelines] = useState<Pipeline[]>(mockPipelines);
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setPipelines((prev) =>
        prev.map((pipeline) => ({
          ...pipeline,
          queueSize: Math.max(0, pipeline.queueSize + Math.floor(Math.random() * 20) - 10),
          metrics: {
            ...pipeline.metrics,
            itemsReceived: pipeline.metrics.itemsReceived + Math.floor(Math.random() * 10),
            itemsProcessed: pipeline.metrics.itemsProcessed + Math.floor(Math.random() * 10),
            throughputPerSecond: Math.random() * 50 + pipeline.metrics.throughputPerSecond * 0.9,
          },
          lastActivity: new Date().toISOString(),
        }))
      );
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const totalMetrics = pipelines.reduce(
    (acc, p) => ({
      received: acc.received + p.metrics.itemsReceived,
      processed: acc.processed + p.metrics.itemsProcessed,
      failed: acc.failed + p.metrics.itemsFailed,
      throughput: acc.throughput + p.metrics.throughputPerSecond,
    }),
    { received: 0, processed: 0, failed: 0, throughput: 0 }
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Pipeline Status</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">
            {pipelines.filter((p) => p.status === "running").length} of {pipelines.length} running
          </span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-900/50 border border-blue-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-300">
            {totalMetrics.received.toLocaleString()}
          </div>
          <div className="text-sm text-gray-400">Total Items Received</div>
        </div>
        <div className="bg-green-900/50 border border-green-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-300">
            {totalMetrics.processed.toLocaleString()}
          </div>
          <div className="text-sm text-gray-400">Total Items Processed</div>
        </div>
        <div className="bg-red-900/50 border border-red-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-red-300">
            {totalMetrics.failed.toLocaleString()}
          </div>
          <div className="text-sm text-gray-400">Total Items Failed</div>
        </div>
        <div className="bg-purple-900/50 border border-purple-700 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-300">
            {totalMetrics.throughput.toFixed(1)}/s
          </div>
          <div className="text-sm text-gray-400">Combined Throughput</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {pipelines.map((pipeline) => (
          <div
            key={pipeline.id}
            className={`bg-gray-800 border rounded-lg p-4 cursor-pointer transition-colors ${
              selectedPipeline?.id === pipeline.id
                ? "border-blue-500"
                : "border-gray-700 hover:border-gray-600"
            }`}
            onClick={() => setSelectedPipeline(pipeline)}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span
                  className={`w-3 h-3 rounded-full ${statusColors[pipeline.status]}`}
                />
                <h3 className="font-semibold">{pipeline.name}</h3>
              </div>
              <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">
                {pipeline.type}
              </span>
            </div>

            <div className="grid grid-cols-4 gap-2 text-sm mb-3">
              <div>
                <div className="text-gray-400">Workers</div>
                <div className="font-medium">{pipeline.workers}</div>
              </div>
              <div>
                <div className="text-gray-400">Queue</div>
                <div className="font-medium">{pipeline.queueSize}</div>
              </div>
              <div>
                <div className="text-gray-400">Throughput</div>
                <div className="font-medium">
                  {pipeline.metrics.throughputPerSecond.toFixed(1)}/s
                </div>
              </div>
              <div>
                <div className="text-gray-400">Latency</div>
                <div className="font-medium">
                  {pipeline.metrics.avgProcessingTimeMs.toFixed(1)}ms
                </div>
              </div>
            </div>

            <div className="flex gap-1">
              {pipeline.stages.map((stage, idx) => (
                <div
                  key={idx}
                  className="flex-1 text-center"
                  title={`${stage.name}: ${stage.itemsProcessed} processed`}
                >
                  <div
                    className={`h-2 rounded ${stageStatusColors[stage.status]}`}
                  />
                  <div className="text-xs text-gray-500 mt-1">{stage.name}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {selectedPipeline && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 mt-4">
          <h3 className="font-semibold mb-4">
            Pipeline Details: {selectedPipeline.name}
          </h3>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Metrics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Items Received:</span>
                  <span>{selectedPipeline.metrics.itemsReceived.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Items Processed:</span>
                  <span>{selectedPipeline.metrics.itemsProcessed.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Items Failed:</span>
                  <span className="text-red-400">
                    {selectedPipeline.metrics.itemsFailed}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Success Rate:</span>
                  <span className="text-green-400">
                    {(
                      (selectedPipeline.metrics.itemsProcessed /
                        selectedPipeline.metrics.itemsReceived) *
                      100
                    ).toFixed(2)}
                    %
                  </span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Stages</h4>
              <div className="space-y-2">
                {selectedPipeline.stages.map((stage, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className={`w-2 h-2 rounded-full ${stageStatusColors[stage.status]}`}
                      />
                      <span>{stage.name}</span>
                    </div>
                    <span className="text-gray-400">
                      {stage.itemsProcessed.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
