"use client";

import React, { useState, useEffect } from "react";

interface CorrectionAction {
  action_id: string;
  correction_type: string;
  target_engine: string;
  target_component: string;
  priority: string;
  status: string;
  description: string;
  requires_approval: boolean;
  approved_by: string | null;
  started_at: string | null;
  completed_at: string | null;
  result: string | null;
  created_at: string;
}

interface PipelineStatus {
  pipeline_id: string;
  name: string;
  engine: string;
  status: string;
  last_run: string;
  records_processed: number;
  error_count: number;
  stalled: boolean;
}

interface CorrectorStats {
  total_corrections: number;
  completed: number;
  failed: number;
  pending: number;
  success_rate: number;
  model_drift_reports: number;
  pipelines_monitored: number;
  stalled_pipelines: number;
  auto_correction_enabled: boolean;
}

export default function AutoCorrectionTimeline() {
  const [actions, setActions] = useState<CorrectionAction[]>([]);
  const [pipelines, setPipelines] = useState<PipelineStatus[]>([]);
  const [stats, setStats] = useState<CorrectorStats | null>(null);
  const [activeTab, setActiveTab] = useState<"timeline" | "pipelines">("timeline");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockActions: CorrectionAction[] = [
      {
        action_id: "COR-A1B2C3D4",
        correction_type: "load_rebalance",
        target_engine: "predictive_ai",
        target_component: "predictive_ai -> intel_orchestration",
        priority: "HIGH",
        status: "completed",
        description: "Rebalance 20% load from predictive_ai to intel_orchestration",
        requires_approval: false,
        approved_by: null,
        started_at: new Date(Date.now() - 600000).toISOString(),
        completed_at: new Date(Date.now() - 300000).toISOString(),
        result: "Successfully executed load_rebalance",
        created_at: new Date(Date.now() - 900000).toISOString(),
      },
      {
        action_id: "COR-E5F6G7H8",
        correction_type: "service_restart",
        target_engine: "cyber_intel",
        target_component: "threat_analyzer",
        priority: "CRITICAL",
        status: "requires_approval",
        description: "Restart failed service: threat_analyzer",
        requires_approval: true,
        approved_by: null,
        started_at: null,
        completed_at: null,
        result: null,
        created_at: new Date(Date.now() - 120000).toISOString(),
      },
      {
        action_id: "COR-I9J0K1L2",
        correction_type: "cache_rebuild",
        target_engine: "city_brain",
        target_component: "prediction_cache",
        priority: "HIGH",
        status: "in_progress",
        description: "Rebuild corrupted cache: prediction_cache",
        requires_approval: true,
        approved_by: "auto_corrector",
        started_at: new Date(Date.now() - 60000).toISOString(),
        completed_at: null,
        result: null,
        created_at: new Date(Date.now() - 180000).toISOString(),
      },
      {
        action_id: "COR-M3N4O5P6",
        correction_type: "pipeline_repair",
        target_engine: "intel_orchestration",
        target_component: "Intel Fusion Pipeline",
        priority: "HIGH",
        status: "completed",
        description: "Repair stalled pipeline: Intel Fusion Pipeline",
        requires_approval: false,
        approved_by: null,
        started_at: new Date(Date.now() - 1800000).toISOString(),
        completed_at: new Date(Date.now() - 1500000).toISOString(),
        result: "Successfully executed pipeline_repair",
        created_at: new Date(Date.now() - 2100000).toISOString(),
      },
      {
        action_id: "COR-Q7R8S9T0",
        correction_type: "model_drift_correction",
        target_engine: "predictive_ai",
        target_component: "crime_forecast_model",
        priority: "CRITICAL",
        status: "failed",
        description: "Auto-correct model drift for crime_forecast_model",
        requires_approval: true,
        approved_by: "sentinel_engine",
        started_at: new Date(Date.now() - 3600000).toISOString(),
        completed_at: new Date(Date.now() - 3300000).toISOString(),
        result: "Failed to execute model_drift_correction: Timeout",
        created_at: new Date(Date.now() - 3900000).toISOString(),
      },
    ];

    const mockPipelines: PipelineStatus[] = [
      { pipeline_id: "PL-001", name: "Intel Fusion Pipeline", engine: "intel_orchestration", status: "running", last_run: new Date(Date.now() - 60000).toISOString(), records_processed: 125000, error_count: 2, stalled: false },
      { pipeline_id: "PL-002", name: "Drone Telemetry Pipeline", engine: "drone_task_force", status: "running", last_run: new Date(Date.now() - 30000).toISOString(), records_processed: 45000, error_count: 0, stalled: false },
      { pipeline_id: "PL-003", name: "Global Awareness Pipeline", engine: "global_awareness", status: "running", last_run: new Date(Date.now() - 120000).toISOString(), records_processed: 89000, error_count: 1, stalled: false },
      { pipeline_id: "PL-004", name: "Emergency Response Pipeline", engine: "emergency_management", status: "running", last_run: new Date(Date.now() - 90000).toISOString(), records_processed: 32000, error_count: 0, stalled: false },
      { pipeline_id: "PL-005", name: "Cyber Threat Pipeline", engine: "cyber_intel", status: "warning", last_run: new Date(Date.now() - 300000).toISOString(), records_processed: 67000, error_count: 5, stalled: false },
      { pipeline_id: "PL-006", name: "Human Stability Pipeline", engine: "human_stability", status: "running", last_run: new Date(Date.now() - 45000).toISOString(), records_processed: 28000, error_count: 0, stalled: false },
      { pipeline_id: "PL-007", name: "City Brain Pipeline", engine: "city_brain", status: "stalled", last_run: new Date(Date.now() - 1800000).toISOString(), records_processed: 156000, error_count: 12, stalled: true },
      { pipeline_id: "PL-008", name: "Predictive AI Pipeline", engine: "predictive_ai", status: "running", last_run: new Date(Date.now() - 15000).toISOString(), records_processed: 234000, error_count: 3, stalled: false },
    ];

    const mockStats: CorrectorStats = {
      total_corrections: 156,
      completed: 142,
      failed: 8,
      pending: 6,
      success_rate: 0.91,
      model_drift_reports: 12,
      pipelines_monitored: 8,
      stalled_pipelines: 1,
      auto_correction_enabled: true,
    };

    setActions(mockActions);
    setPipelines(mockPipelines);
    setStats(mockStats);
    setLoading(false);
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <span className="px-2 py-1 text-xs font-bold bg-green-600 text-white rounded">COMPLETED</span>;
      case "in_progress":
        return <span className="px-2 py-1 text-xs font-bold bg-blue-600 text-white rounded animate-pulse">IN PROGRESS</span>;
      case "pending":
        return <span className="px-2 py-1 text-xs font-bold bg-yellow-600 text-white rounded">PENDING</span>;
      case "requires_approval":
        return <span className="px-2 py-1 text-xs font-bold bg-orange-600 text-white rounded">NEEDS APPROVAL</span>;
      case "failed":
        return <span className="px-2 py-1 text-xs font-bold bg-red-600 text-white rounded">FAILED</span>;
      case "rolled_back":
        return <span className="px-2 py-1 text-xs font-bold bg-purple-600 text-white rounded">ROLLED BACK</span>;
      default:
        return <span className="px-2 py-1 text-xs font-bold bg-gray-600 text-white rounded">{status.toUpperCase()}</span>;
    }
  };

  const getPipelineStatusBadge = (status: string, stalled: boolean) => {
    if (stalled) {
      return <span className="px-2 py-1 text-xs font-bold bg-red-600 text-white rounded animate-pulse">STALLED</span>;
    }
    switch (status) {
      case "running":
        return <span className="px-2 py-1 text-xs font-bold bg-green-600 text-white rounded">RUNNING</span>;
      case "warning":
        return <span className="px-2 py-1 text-xs font-bold bg-yellow-600 text-white rounded">WARNING</span>;
      case "error":
        return <span className="px-2 py-1 text-xs font-bold bg-red-600 text-white rounded">ERROR</span>;
      default:
        return <span className="px-2 py-1 text-xs font-bold bg-gray-600 text-white rounded">{status.toUpperCase()}</span>;
    }
  };

  const getCorrectionTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      pipeline_repair: "Pipeline Repair",
      service_restart: "Service Restart",
      cache_rebuild: "Cache Rebuild",
      load_rebalance: "Load Rebalance",
      policy_validation: "Policy Validation",
      model_drift_correction: "Model Drift Correction",
      data_feed_recovery: "Data Feed Recovery",
      queue_flush: "Queue Flush",
      connection_reset: "Connection Reset",
      memory_cleanup: "Memory Cleanup",
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-4 rounded-lg border border-green-700 bg-green-900/30">
          <div className="text-sm text-green-400">Success Rate</div>
          <div className="text-2xl font-bold text-green-400">
            {((stats?.success_rate || 0) * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-green-400/75 mt-1">{stats?.completed} completed</div>
        </div>

        <div className="p-4 rounded-lg border border-yellow-700 bg-yellow-900/30">
          <div className="text-sm text-yellow-400">Pending</div>
          <div className="text-2xl font-bold text-yellow-400">{stats?.pending}</div>
          <div className="text-xs text-yellow-400/75 mt-1">Awaiting execution</div>
        </div>

        <div className="p-4 rounded-lg border border-red-700 bg-red-900/30">
          <div className="text-sm text-red-400">Failed</div>
          <div className="text-2xl font-bold text-red-400">{stats?.failed}</div>
          <div className="text-xs text-red-400/75 mt-1">Requires attention</div>
        </div>

        <div className="p-4 rounded-lg border border-blue-700 bg-blue-900/30">
          <div className="text-sm text-blue-400">Pipelines</div>
          <div className="text-2xl font-bold text-blue-400">{stats?.pipelines_monitored}</div>
          <div className="text-xs text-blue-400/75 mt-1">{stats?.stalled_pipelines} stalled</div>
        </div>

        <div className="p-4 rounded-lg border border-purple-700 bg-purple-900/30">
          <div className="text-sm text-purple-400">Auto-Correction</div>
          <div className="text-2xl font-bold text-purple-400">
            {stats?.auto_correction_enabled ? "ENABLED" : "DISABLED"}
          </div>
          <div className="text-xs text-purple-400/75 mt-1">{stats?.model_drift_reports} drift reports</div>
        </div>
      </div>

      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => setActiveTab("timeline")}
          className={`px-4 py-2 rounded-lg ${
            activeTab === "timeline"
              ? "bg-purple-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Correction Timeline
        </button>
        <button
          onClick={() => setActiveTab("pipelines")}
          className={`px-4 py-2 rounded-lg ${
            activeTab === "pipelines"
              ? "bg-purple-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Pipeline Status
        </button>
      </div>

      {activeTab === "timeline" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold">Auto-Correction Timeline</h3>
          </div>
          <div className="divide-y divide-gray-700">
            {actions.map((action) => (
              <div key={action.action_id} className="p-4 hover:bg-gray-700/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      {getStatusBadge(action.status)}
                      <span className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded">
                        {getCorrectionTypeLabel(action.correction_type)}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded ${
                        action.priority === "CRITICAL" ? "bg-red-900/50 text-red-400" :
                        action.priority === "HIGH" ? "bg-orange-900/50 text-orange-400" :
                        "bg-gray-700 text-gray-300"
                      }`}>
                        {action.priority}
                      </span>
                    </div>
                    
                    <div className="font-medium">{action.description}</div>
                    
                    <div className="mt-2 text-sm text-gray-400 space-y-1">
                      <div>
                        <span className="text-gray-500">Target:</span> {action.target_engine} / {action.target_component}
                      </div>
                      {action.approved_by && (
                        <div>
                          <span className="text-gray-500">Approved by:</span> {action.approved_by}
                        </div>
                      )}
                      {action.result && (
                        <div className={action.status === "failed" ? "text-red-400" : "text-green-400"}>
                          {action.result}
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-2 text-xs text-gray-500">
                      {action.action_id} | Created: {new Date(action.created_at).toLocaleString()}
                      {action.completed_at && ` | Completed: ${new Date(action.completed_at).toLocaleString()}`}
                    </div>
                  </div>
                  
                  <div className="flex flex-col space-y-2 ml-4">
                    {action.status === "requires_approval" && (
                      <button className="px-3 py-1 text-sm bg-green-600 hover:bg-green-700 text-white rounded">
                        Approve
                      </button>
                    )}
                    {action.status === "completed" && (
                      <button className="px-3 py-1 text-sm bg-yellow-600 hover:bg-yellow-700 text-white rounded">
                        Rollback
                      </button>
                    )}
                    <button className="px-3 py-1 text-sm bg-gray-600 hover:bg-gray-500 text-white rounded">
                      Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "pipelines" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold">Pipeline Status</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-400 border-b border-gray-700">
                  <th className="text-left py-3 px-4">Pipeline</th>
                  <th className="text-left py-3 px-4">Engine</th>
                  <th className="text-center py-3 px-4">Status</th>
                  <th className="text-right py-3 px-4">Records</th>
                  <th className="text-right py-3 px-4">Errors</th>
                  <th className="text-right py-3 px-4">Last Run</th>
                  <th className="text-center py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {pipelines.map((pipeline) => (
                  <tr key={pipeline.pipeline_id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                    <td className="py-3 px-4 font-medium">{pipeline.name}</td>
                    <td className="py-3 px-4 text-gray-400">{pipeline.engine}</td>
                    <td className="py-3 px-4 text-center">
                      {getPipelineStatusBadge(pipeline.status, pipeline.stalled)}
                    </td>
                    <td className="py-3 px-4 text-right">{pipeline.records_processed.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">
                      <span className={pipeline.error_count > 5 ? "text-red-400" : pipeline.error_count > 0 ? "text-yellow-400" : "text-green-400"}>
                        {pipeline.error_count}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-gray-400">
                      {new Date(pipeline.last_run).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {pipeline.stalled ? (
                        <button className="px-3 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded">
                          Repair
                        </button>
                      ) : (
                        <button className="px-3 py-1 text-xs bg-gray-600 hover:bg-gray-500 text-white rounded">
                          View
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
