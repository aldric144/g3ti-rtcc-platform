"use client";

import React, { useState, useEffect } from "react";

interface EngineMetrics {
  engine_type: string;
  cpu_percent: number;
  memory_percent: number;
  gpu_percent: number;
  queue_depth: number;
  active_tasks: number;
  latency_ms: number;
  error_rate: number;
  throughput_per_sec: number;
  status: string;
  instance_count: number;
}

export default function SystemLoadHeatmap() {
  const [engines, setEngines] = useState<EngineMetrics[]>([]);
  const [selectedEngine, setSelectedEngine] = useState<EngineMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockEngines: EngineMetrics[] = [
      { engine_type: "drone_task_force", cpu_percent: 45.2, memory_percent: 52.1, gpu_percent: 38.5, queue_depth: 125, active_tasks: 12, latency_ms: 85.3, error_rate: 0.002, throughput_per_sec: 450, status: "healthy", instance_count: 3 },
      { engine_type: "robotics", cpu_percent: 62.8, memory_percent: 71.3, gpu_percent: 55.2, queue_depth: 89, active_tasks: 8, latency_ms: 120.5, error_rate: 0.005, throughput_per_sec: 320, status: "degraded", instance_count: 2 },
      { engine_type: "intel_orchestration", cpu_percent: 78.5, memory_percent: 65.8, gpu_percent: 42.1, queue_depth: 450, active_tasks: 35, latency_ms: 95.2, error_rate: 0.003, throughput_per_sec: 890, status: "warning", instance_count: 4 },
      { engine_type: "human_stability", cpu_percent: 35.2, memory_percent: 48.6, gpu_percent: 28.9, queue_depth: 67, active_tasks: 15, latency_ms: 65.8, error_rate: 0.001, throughput_per_sec: 280, status: "healthy", instance_count: 2 },
      { engine_type: "predictive_ai", cpu_percent: 92.5, memory_percent: 88.3, gpu_percent: 85.6, queue_depth: 1250, active_tasks: 48, latency_ms: 450.2, error_rate: 0.045, throughput_per_sec: 1200, status: "critical", instance_count: 5 },
      { engine_type: "city_autonomy", cpu_percent: 55.8, memory_percent: 62.4, gpu_percent: 45.2, queue_depth: 234, active_tasks: 22, latency_ms: 110.5, error_rate: 0.008, throughput_per_sec: 560, status: "healthy", instance_count: 3 },
      { engine_type: "global_awareness", cpu_percent: 48.9, memory_percent: 55.2, gpu_percent: 35.8, queue_depth: 178, active_tasks: 18, latency_ms: 78.9, error_rate: 0.002, throughput_per_sec: 720, status: "healthy", instance_count: 3 },
      { engine_type: "emergency_management", cpu_percent: 42.1, memory_percent: 51.8, gpu_percent: 32.5, queue_depth: 95, active_tasks: 10, latency_ms: 55.2, error_rate: 0.001, throughput_per_sec: 380, status: "healthy", instance_count: 2 },
      { engine_type: "cyber_intel", cpu_percent: 68.5, memory_percent: 72.8, gpu_percent: 58.9, queue_depth: 320, active_tasks: 28, latency_ms: 135.8, error_rate: 0.012, throughput_per_sec: 650, status: "degraded", instance_count: 3 },
      { engine_type: "officer_assist", cpu_percent: 38.2, memory_percent: 45.6, gpu_percent: 25.8, queue_depth: 78, active_tasks: 14, latency_ms: 48.5, error_rate: 0.001, throughput_per_sec: 420, status: "healthy", instance_count: 2 },
      { engine_type: "city_brain", cpu_percent: 72.5, memory_percent: 78.9, gpu_percent: 62.3, queue_depth: 580, active_tasks: 42, latency_ms: 185.2, error_rate: 0.018, throughput_per_sec: 980, status: "warning", instance_count: 4 },
      { engine_type: "ethics_guardian", cpu_percent: 28.5, memory_percent: 35.2, gpu_percent: 15.8, queue_depth: 45, active_tasks: 8, latency_ms: 32.5, error_rate: 0.0005, throughput_per_sec: 250, status: "healthy", instance_count: 2 },
      { engine_type: "enterprise_infra", cpu_percent: 52.8, memory_percent: 58.5, gpu_percent: 38.2, queue_depth: 156, active_tasks: 20, latency_ms: 92.8, error_rate: 0.004, throughput_per_sec: 520, status: "healthy", instance_count: 3 },
      { engine_type: "national_security", cpu_percent: 45.8, memory_percent: 52.3, gpu_percent: 35.5, queue_depth: 112, active_tasks: 16, latency_ms: 75.2, error_rate: 0.002, throughput_per_sec: 480, status: "healthy", instance_count: 2 },
      { engine_type: "detective_ai", cpu_percent: 58.2, memory_percent: 65.8, gpu_percent: 48.5, queue_depth: 245, active_tasks: 25, latency_ms: 125.8, error_rate: 0.008, throughput_per_sec: 620, status: "degraded", instance_count: 3 },
      { engine_type: "threat_intel", cpu_percent: 42.5, memory_percent: 48.9, gpu_percent: 32.1, queue_depth: 98, active_tasks: 12, latency_ms: 68.5, error_rate: 0.002, throughput_per_sec: 380, status: "healthy", instance_count: 2 },
    ];

    setEngines(mockEngines);
    setLoading(false);
  }, []);

  const getHeatColor = (value: number, max: number = 100) => {
    const percent = (value / max) * 100;
    if (percent >= 90) return "bg-red-600";
    if (percent >= 75) return "bg-orange-500";
    if (percent >= 60) return "bg-yellow-500";
    if (percent >= 40) return "bg-green-500";
    return "bg-green-400";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy": return "text-green-400";
      case "degraded": return "text-yellow-400";
      case "warning": return "text-orange-400";
      case "critical": return "text-red-400";
      case "offline": return "text-gray-400";
      default: return "text-gray-400";
    }
  };

  const formatEngineName = (name: string) => {
    return name.split("_").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
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
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          System Load Heatmap
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-700">
                <th className="text-left py-2 px-3">Engine</th>
                <th className="text-center py-2 px-3">Status</th>
                <th className="text-center py-2 px-3">CPU</th>
                <th className="text-center py-2 px-3">Memory</th>
                <th className="text-center py-2 px-3">GPU</th>
                <th className="text-center py-2 px-3">Queue</th>
                <th className="text-center py-2 px-3">Latency</th>
                <th className="text-center py-2 px-3">Error Rate</th>
                <th className="text-center py-2 px-3">Instances</th>
              </tr>
            </thead>
            <tbody>
              {engines.map((engine) => (
                <tr 
                  key={engine.engine_type}
                  className="border-b border-gray-700/50 hover:bg-gray-700/30 cursor-pointer"
                  onClick={() => setSelectedEngine(engine)}
                >
                  <td className="py-3 px-3 font-medium">{formatEngineName(engine.engine_type)}</td>
                  <td className="py-3 px-3 text-center">
                    <span className={`font-semibold ${getStatusColor(engine.status)}`}>
                      {engine.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center justify-center">
                      <div className={`w-16 h-6 rounded ${getHeatColor(engine.cpu_percent)} flex items-center justify-center text-white text-xs font-bold`}>
                        {engine.cpu_percent.toFixed(1)}%
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center justify-center">
                      <div className={`w-16 h-6 rounded ${getHeatColor(engine.memory_percent)} flex items-center justify-center text-white text-xs font-bold`}>
                        {engine.memory_percent.toFixed(1)}%
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center justify-center">
                      <div className={`w-16 h-6 rounded ${getHeatColor(engine.gpu_percent)} flex items-center justify-center text-white text-xs font-bold`}>
                        {engine.gpu_percent.toFixed(1)}%
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center justify-center">
                      <div className={`w-16 h-6 rounded ${getHeatColor(engine.queue_depth, 1000)} flex items-center justify-center text-white text-xs font-bold`}>
                        {engine.queue_depth}
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center justify-center">
                      <div className={`w-16 h-6 rounded ${getHeatColor(engine.latency_ms, 500)} flex items-center justify-center text-white text-xs font-bold`}>
                        {engine.latency_ms.toFixed(0)}ms
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex items-center justify-center">
                      <div className={`w-16 h-6 rounded ${getHeatColor(engine.error_rate * 1000, 50)} flex items-center justify-center text-white text-xs font-bold`}>
                        {(engine.error_rate * 100).toFixed(2)}%
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3 text-center">{engine.instance_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-center space-x-4 text-xs text-gray-400">
          <div className="flex items-center space-x-1">
            <div className="w-4 h-4 bg-green-400 rounded"></div>
            <span>Low (&lt;40%)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span>Normal (40-60%)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-4 h-4 bg-yellow-500 rounded"></div>
            <span>Elevated (60-75%)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-4 h-4 bg-orange-500 rounded"></div>
            <span>High (75-90%)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-4 h-4 bg-red-600 rounded"></div>
            <span>Critical (&gt;90%)</span>
          </div>
        </div>
      </div>

      {selectedEngine && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              {formatEngineName(selectedEngine.engine_type)} Details
            </h3>
            <button 
              onClick={() => setSelectedEngine(null)}
              className="text-gray-400 hover:text-white"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-gray-700/50 rounded-lg">
              <div className="text-sm text-gray-400">CPU Usage</div>
              <div className="text-xl font-bold">{selectedEngine.cpu_percent.toFixed(1)}%</div>
              <div className="w-full bg-gray-600 rounded-full h-2 mt-2">
                <div className={`h-2 rounded-full ${getHeatColor(selectedEngine.cpu_percent)}`} style={{ width: `${selectedEngine.cpu_percent}%` }}></div>
              </div>
            </div>

            <div className="p-3 bg-gray-700/50 rounded-lg">
              <div className="text-sm text-gray-400">Memory Usage</div>
              <div className="text-xl font-bold">{selectedEngine.memory_percent.toFixed(1)}%</div>
              <div className="w-full bg-gray-600 rounded-full h-2 mt-2">
                <div className={`h-2 rounded-full ${getHeatColor(selectedEngine.memory_percent)}`} style={{ width: `${selectedEngine.memory_percent}%` }}></div>
              </div>
            </div>

            <div className="p-3 bg-gray-700/50 rounded-lg">
              <div className="text-sm text-gray-400">GPU Usage</div>
              <div className="text-xl font-bold">{selectedEngine.gpu_percent.toFixed(1)}%</div>
              <div className="w-full bg-gray-600 rounded-full h-2 mt-2">
                <div className={`h-2 rounded-full ${getHeatColor(selectedEngine.gpu_percent)}`} style={{ width: `${selectedEngine.gpu_percent}%` }}></div>
              </div>
            </div>

            <div className="p-3 bg-gray-700/50 rounded-lg">
              <div className="text-sm text-gray-400">Queue Depth</div>
              <div className="text-xl font-bold">{selectedEngine.queue_depth}</div>
              <div className="text-xs text-gray-500 mt-1">{selectedEngine.active_tasks} active tasks</div>
            </div>

            <div className="p-3 bg-gray-700/50 rounded-lg">
              <div className="text-sm text-gray-400">Latency</div>
              <div className="text-xl font-bold">{selectedEngine.latency_ms.toFixed(1)}ms</div>
            </div>

            <div className="p-3 bg-gray-700/50 rounded-lg">
              <div className="text-sm text-gray-400">Error Rate</div>
              <div className="text-xl font-bold">{(selectedEngine.error_rate * 100).toFixed(3)}%</div>
            </div>

            <div className="p-3 bg-gray-700/50 rounded-lg">
              <div className="text-sm text-gray-400">Throughput</div>
              <div className="text-xl font-bold">{selectedEngine.throughput_per_sec}/s</div>
            </div>

            <div className="p-3 bg-gray-700/50 rounded-lg">
              <div className="text-sm text-gray-400">Instances</div>
              <div className="text-xl font-bold">{selectedEngine.instance_count}</div>
            </div>
          </div>

          <div className="mt-4 flex space-x-2">
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded">
              Scale Up
            </button>
            <button className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded">
              Restart
            </button>
            <button className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded">
              View Logs
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
