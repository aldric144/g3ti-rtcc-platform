"use client";

import React, { useState, useEffect } from "react";

interface Resource {
  resource_id: string;
  resource_type: string;
  name: string;
  current_zone: string;
  status: string;
  capacity: number;
  utilization: number;
  cost_per_hour: number;
}

interface Zone {
  zone_id: string;
  name: string;
  demand_level: number;
  current_coverage: number;
  target_coverage: number;
  population: number;
}

interface OptimizationResult {
  optimization_id: string;
  algorithm: string;
  status: string;
  allocations: Allocation[];
  metrics_before: Record<string, number>;
  metrics_after: Record<string, number>;
  improvement: Record<string, number>;
  cost_impact: number;
  execution_time_ms: number;
}

interface Allocation {
  resource_id: string;
  from_zone: string;
  to_zone: string;
  reason: string;
  expected_impact: Record<string, number>;
}

export default function ResourceOptimizationPanel() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [showOptimizeModal, setShowOptimizeModal] = useState(false);
  const [showExplainDrawer, setShowExplainDrawer] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState("linear_programming");
  const [selectedObjectives, setSelectedObjectives] = useState<string[]>(["maximize_coverage"]);
  const [draggedResource, setDraggedResource] = useState<string | null>(null);

  useEffect(() => {
    const mockResources: Resource[] = [
      { resource_id: "unit-101", resource_type: "police_unit", name: "Unit 101", current_zone: "downtown", status: "available", capacity: 1.0, utilization: 0.6, cost_per_hour: 45 },
      { resource_id: "unit-102", resource_type: "police_unit", name: "Unit 102", current_zone: "marina", status: "available", capacity: 1.0, utilization: 0.5, cost_per_hour: 45 },
      { resource_id: "unit-103", resource_type: "police_unit", name: "Unit 103", current_zone: "westside", status: "available", capacity: 1.0, utilization: 0.7, cost_per_hour: 45 },
      { resource_id: "unit-104", resource_type: "police_unit", name: "Unit 104", current_zone: "singer_island", status: "available", capacity: 1.0, utilization: 0.4, cost_per_hour: 45 },
      { resource_id: "engine-1", resource_type: "fire_unit", name: "Engine 1", current_zone: "downtown", status: "available", capacity: 4.0, utilization: 0.3, cost_per_hour: 120 },
      { resource_id: "engine-2", resource_type: "fire_unit", name: "Engine 2", current_zone: "singer_island", status: "available", capacity: 4.0, utilization: 0.2, cost_per_hour: 120 },
      { resource_id: "medic-1", resource_type: "ems_unit", name: "Medic 1", current_zone: "downtown", status: "available", capacity: 2.0, utilization: 0.5, cost_per_hour: 80 },
      { resource_id: "medic-2", resource_type: "ems_unit", name: "Medic 2", current_zone: "westside", status: "available", capacity: 2.0, utilization: 0.4, cost_per_hour: 80 },
    ];

    const mockZones: Zone[] = [
      { zone_id: "downtown", name: "Downtown/Marina", demand_level: 0.8, current_coverage: 0.7, target_coverage: 0.9, population: 8500 },
      { zone_id: "singer_island", name: "Singer Island", demand_level: 0.5, current_coverage: 0.6, target_coverage: 0.85, population: 4200 },
      { zone_id: "westside", name: "Westside", demand_level: 0.7, current_coverage: 0.65, target_coverage: 0.85, population: 9800 },
      { zone_id: "marina", name: "Marina District", demand_level: 0.6, current_coverage: 0.7, target_coverage: 0.8, population: 3500 },
      { zone_id: "industrial", name: "Industrial/Port", demand_level: 0.4, current_coverage: 0.5, target_coverage: 0.7, population: 2100 },
      { zone_id: "north", name: "North Riviera Beach", demand_level: 0.5, current_coverage: 0.55, target_coverage: 0.8, population: 9864 },
    ];

    setResources(mockResources);
    setZones(mockZones);
  }, []);

  const handleRunOptimization = async () => {
    setOptimizing(true);
    
    await new Promise(resolve => setTimeout(resolve, 2000));

    const mockResult: OptimizationResult = {
      optimization_id: `opt-${Date.now()}`,
      algorithm: selectedAlgorithm,
      status: "completed",
      allocations: [
        { resource_id: "unit-102", from_zone: "marina", to_zone: "downtown", reason: "Coverage gap detected", expected_impact: { coverage_improvement: 0.05 } },
        { resource_id: "unit-104", from_zone: "singer_island", to_zone: "westside", reason: "High demand area", expected_impact: { coverage_improvement: 0.08 } },
      ],
      metrics_before: { average_coverage: 0.62, response_time_score: 0.75, workload_balance: 0.7 },
      metrics_after: { average_coverage: 0.78, response_time_score: 0.82, workload_balance: 0.85 },
      improvement: { average_coverage: 0.16, response_time_score: 0.07, workload_balance: 0.15 },
      cost_impact: 720,
      execution_time_ms: 1850,
    };

    setOptimizationResult(mockResult);
    setOptimizing(false);
    setShowOptimizeModal(false);
  };

  const handleDragStart = (resourceId: string) => {
    setDraggedResource(resourceId);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (zoneId: string) => {
    if (draggedResource) {
      setResources(prev => prev.map(r => 
        r.resource_id === draggedResource ? { ...r, current_zone: zoneId } : r
      ));
      setDraggedResource(null);
    }
  };

  const getResourceTypeIcon = (type: string) => {
    switch (type) {
      case "police_unit":
        return "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z";
      case "fire_unit":
        return "M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z";
      case "ems_unit":
        return "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z";
      default:
        return "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4";
    }
  };

  const getResourceTypeColor = (type: string) => {
    switch (type) {
      case "police_unit":
        return "text-blue-400";
      case "fire_unit":
        return "text-red-400";
      case "ems_unit":
        return "text-green-400";
      default:
        return "text-gray-400";
    }
  };

  const getCoverageColor = (current: number, target: number) => {
    const ratio = current / target;
    if (ratio >= 0.9) return "bg-green-500";
    if (ratio >= 0.7) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Resource Optimization</h2>
          <p className="text-sm text-gray-400">Drag and drop units to reassign zones or run AI optimization</p>
        </div>
        <button
          onClick={() => setShowOptimizeModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center space-x-2 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>Run Optimization</span>
        </button>
      </div>

      {optimizationResult && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-white">Latest Optimization Result</h3>
            <button
              onClick={() => setShowExplainDrawer(true)}
              className="text-blue-400 hover:text-blue-300 text-sm flex items-center space-x-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Explain Results</span>
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-700/50 rounded-lg p-3">
              <div className="text-sm text-gray-400">Coverage Improvement</div>
              <div className="text-2xl font-bold text-green-400">
                +{(optimizationResult.improvement.average_coverage * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-3">
              <div className="text-sm text-gray-400">Response Time</div>
              <div className="text-2xl font-bold text-green-400">
                +{(optimizationResult.improvement.response_time_score * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-3">
              <div className="text-sm text-gray-400">Workload Balance</div>
              <div className="text-2xl font-bold text-green-400">
                +{(optimizationResult.improvement.workload_balance * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-gray-700/50 rounded-lg p-3">
              <div className="text-sm text-gray-400">Cost Impact</div>
              <div className="text-2xl font-bold text-yellow-400">
                ${optimizationResult.cost_impact.toLocaleString()}
              </div>
            </div>
          </div>
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-300 mb-2">Recommended Reallocations</h4>
            <div className="space-y-2">
              {optimizationResult.allocations.map((allocation, i) => (
                <div key={i} className="flex items-center justify-between bg-gray-700/30 rounded p-2">
                  <div className="flex items-center space-x-3">
                    <span className="text-white font-medium">{allocation.resource_id}</span>
                    <span className="text-gray-400">{allocation.from_zone}</span>
                    <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                    <span className="text-white">{allocation.to_zone}</span>
                  </div>
                  <span className="text-sm text-gray-400">{allocation.reason}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="px-6 py-4 border-b border-gray-700">
              <h3 className="text-lg font-medium text-white">Zone Coverage Map</h3>
            </div>
            <div className="p-4 grid grid-cols-2 md:grid-cols-3 gap-4">
              {zones.map((zone) => (
                <div
                  key={zone.zone_id}
                  className="bg-gray-700/50 rounded-lg p-4 border border-gray-600"
                  onDragOver={handleDragOver}
                  onDrop={() => handleDrop(zone.zone_id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-white">{zone.name}</h4>
                    <span className="text-xs text-gray-400">{zone.population.toLocaleString()} pop</span>
                  </div>
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-400">Coverage</span>
                      <span className="text-white">{(zone.current_coverage * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-600 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getCoverageColor(zone.current_coverage, zone.target_coverage)}`}
                        style={{ width: `${zone.current_coverage * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">Target: {(zone.target_coverage * 100).toFixed(0)}%</div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {resources
                      .filter((r) => r.current_zone === zone.zone_id)
                      .map((resource) => (
                        <div
                          key={resource.resource_id}
                          draggable
                          onDragStart={() => handleDragStart(resource.resource_id)}
                          onClick={() => setSelectedResource(resource)}
                          className={`flex items-center space-x-1 px-2 py-1 bg-gray-600 rounded cursor-move hover:bg-gray-500 transition-colors ${
                            selectedResource?.resource_id === resource.resource_id ? "ring-2 ring-blue-500" : ""
                          }`}
                        >
                          <svg className={`w-4 h-4 ${getResourceTypeColor(resource.resource_type)}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={getResourceTypeIcon(resource.resource_type)} />
                          </svg>
                          <span className="text-xs text-white">{resource.name}</span>
                        </div>
                      ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-lg font-medium text-white mb-4">Optimization Metrics</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-400">Overall Coverage</span>
                  <span className="text-white">
                    {(zones.reduce((sum, z) => sum + z.current_coverage, 0) / zones.length * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-blue-500"
                    style={{ width: `${zones.reduce((sum, z) => sum + z.current_coverage, 0) / zones.length * 100}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-400">Resource Utilization</span>
                  <span className="text-white">
                    {(resources.reduce((sum, r) => sum + r.utilization, 0) / resources.length * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-green-500"
                    style={{ width: `${resources.reduce((sum, r) => sum + r.utilization, 0) / resources.length * 100}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-400">Demand Coverage Gap</span>
                  <span className="text-white">
                    {(zones.reduce((sum, z) => sum + (z.target_coverage - z.current_coverage), 0) / zones.length * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-yellow-500"
                    style={{ width: `${zones.reduce((sum, z) => sum + (z.target_coverage - z.current_coverage), 0) / zones.length * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {selectedResource && (
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-white">Resource Details</h3>
                <button onClick={() => setSelectedResource(null)} className="text-gray-400 hover:text-white">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <svg className={`w-8 h-8 ${getResourceTypeColor(selectedResource.resource_type)}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={getResourceTypeIcon(selectedResource.resource_type)} />
                  </svg>
                  <div>
                    <div className="font-medium text-white">{selectedResource.name}</div>
                    <div className="text-sm text-gray-400">{selectedResource.resource_type.replace("_", " ")}</div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-400">Status</span>
                    <div className="text-white capitalize">{selectedResource.status}</div>
                  </div>
                  <div>
                    <span className="text-gray-400">Zone</span>
                    <div className="text-white capitalize">{selectedResource.current_zone.replace("_", " ")}</div>
                  </div>
                  <div>
                    <span className="text-gray-400">Utilization</span>
                    <div className="text-white">{(selectedResource.utilization * 100).toFixed(0)}%</div>
                  </div>
                  <div>
                    <span className="text-gray-400">Cost/Hour</span>
                    <div className="text-white">${selectedResource.cost_per_hour}</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {showOptimizeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg border border-gray-700 w-full max-w-md p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Run Optimization</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Algorithm</label>
                <select
                  value={selectedAlgorithm}
                  onChange={(e) => setSelectedAlgorithm(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                >
                  <option value="linear_programming">Linear Programming</option>
                  <option value="multi_objective">Multi-Objective Optimization</option>
                  <option value="genetic_algorithm">Genetic Algorithm</option>
                  <option value="simulated_annealing">Simulated Annealing</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Objectives</label>
                <div className="space-y-2">
                  {["maximize_coverage", "minimize_response_time", "balance_workload", "minimize_cost"].map((obj) => (
                    <label key={obj} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedObjectives.includes(obj)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedObjectives([...selectedObjectives, obj]);
                          } else {
                            setSelectedObjectives(selectedObjectives.filter((o) => o !== obj));
                          }
                        }}
                        className="rounded bg-gray-700 border-gray-600 text-blue-500"
                      />
                      <span className="text-white capitalize">{obj.replace(/_/g, " ")}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowOptimizeModal(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleRunOptimization}
                disabled={optimizing || selectedObjectives.length === 0}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center space-x-2 transition-colors disabled:opacity-50"
              >
                {optimizing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Optimizing...</span>
                  </>
                ) : (
                  <span>Run Optimization</span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {showExplainDrawer && optimizationResult && (
        <div className="fixed inset-y-0 right-0 w-96 bg-gray-800 border-l border-gray-700 shadow-xl z-50 overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Optimization Explanation</h3>
              <button onClick={() => setShowExplainDrawer(false)} className="text-gray-400 hover:text-white">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-6">
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Algorithm Used</h4>
                <p className="text-white capitalize">{optimizationResult.algorithm.replace(/_/g, " ")}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Why These Changes?</h4>
                <p className="text-gray-300 text-sm">
                  The optimization algorithm analyzed current resource distribution and identified coverage gaps
                  in high-demand zones. By reallocating units from lower-demand areas, we can improve overall
                  response times and coverage metrics.
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Metrics Before</h4>
                <div className="space-y-2">
                  {Object.entries(optimizationResult.metrics_before).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-gray-400 capitalize">{key.replace(/_/g, " ")}</span>
                      <span className="text-white">{(value * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Metrics After</h4>
                <div className="space-y-2">
                  {Object.entries(optimizationResult.metrics_after).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-gray-400 capitalize">{key.replace(/_/g, " ")}</span>
                      <span className="text-green-400">{(value * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Execution Details</h4>
                <div className="text-sm text-gray-300">
                  <p>Execution time: {optimizationResult.execution_time_ms}ms</p>
                  <p>Allocations made: {optimizationResult.allocations.length}</p>
                  <p>Cost impact: ${optimizationResult.cost_impact.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
