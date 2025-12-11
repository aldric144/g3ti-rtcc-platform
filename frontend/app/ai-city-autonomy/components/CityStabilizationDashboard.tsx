"use client";

import React, { useState } from "react";

interface Anomaly {
  anomaly_id: string;
  domain: string;
  anomaly_type: string;
  severity: string;
  title: string;
  description: string;
  affected_area: string;
  metrics: Record<string, number>;
  confidence: number;
  detected_at: string;
  cascade_risk: number;
}

interface CascadePrediction {
  prediction_id: string;
  trigger_anomaly: string;
  predicted_failures: string[];
  probability: number;
  estimated_impact: string;
  time_to_cascade_minutes: number;
  affected_systems: string[];
  recommended_actions: string[];
}

interface StabilizationAction {
  action_id: string;
  action_type: string;
  title: string;
  description: string;
  target_domain: string;
  priority: number;
  requires_approval: boolean;
  status: string;
  created_at: string;
  executed_at?: string;
}

const mockAnomalies: Anomaly[] = [
  {
    anomaly_id: "anomaly-001",
    domain: "traffic",
    anomaly_type: "congestion_spike",
    severity: "high",
    title: "Severe Congestion on Blue Heron Blvd",
    description: "Traffic congestion index exceeded critical threshold. Average speed dropped to 8 mph.",
    affected_area: "Blue Heron Blvd / US-1 Intersection",
    metrics: { congestion_index: 0.92, avg_speed_mph: 8, queue_length_vehicles: 45 },
    confidence: 0.94,
    detected_at: new Date(Date.now() - 300000).toISOString(),
    cascade_risk: 0.65,
  },
  {
    anomaly_id: "anomaly-002",
    domain: "power_grid",
    anomaly_type: "load_spike",
    severity: "medium",
    title: "Power Grid Load Approaching Capacity",
    description: "Grid load in Sector 3 at 87% capacity. Potential brownout risk if demand continues.",
    affected_area: "Sector 3 - Downtown District",
    metrics: { load_percentage: 87, demand_mw: 42.5, capacity_mw: 49 },
    confidence: 0.89,
    detected_at: new Date(Date.now() - 600000).toISOString(),
    cascade_risk: 0.45,
  },
  {
    anomaly_id: "anomaly-003",
    domain: "crime",
    anomaly_type: "density_spike",
    severity: "medium",
    title: "Crime Density Increase in Marina District",
    description: "Property crime incidents increased 60% above baseline in the last 2 hours.",
    affected_area: "Marina District",
    metrics: { crime_density: 1.6, incidents_2h: 8, baseline_2h: 5 },
    confidence: 0.86,
    detected_at: new Date(Date.now() - 900000).toISOString(),
    cascade_risk: 0.25,
  },
];

const mockCascadePredictions: CascadePrediction[] = [
  {
    prediction_id: "cascade-001",
    trigger_anomaly: "anomaly-001",
    predicted_failures: ["Emergency response delays", "Secondary congestion on alternate routes", "Increased accident risk"],
    probability: 0.72,
    estimated_impact: "High - Could affect emergency response times by 40%",
    time_to_cascade_minutes: 15,
    affected_systems: ["Traffic Control", "Emergency Dispatch", "Public Transit"],
    recommended_actions: ["Activate signal preemption", "Reroute traffic to Broadway", "Alert emergency services"],
  },
];

const mockStabilizationActions: StabilizationAction[] = [
  {
    action_id: "stab-001",
    action_type: "traffic_reroute",
    title: "Activate Traffic Rerouting",
    description: "Reroute northbound traffic from Blue Heron to Broadway via 13th Street",
    target_domain: "traffic",
    priority: 9,
    requires_approval: false,
    status: "executed",
    created_at: new Date(Date.now() - 240000).toISOString(),
    executed_at: new Date(Date.now() - 230000).toISOString(),
  },
  {
    action_id: "stab-002",
    action_type: "patrol_rebalance",
    title: "Increase Patrol Coverage in Marina District",
    description: "Deploy 2 additional patrol units to Marina District for enhanced coverage",
    target_domain: "crime",
    priority: 7,
    requires_approval: true,
    status: "pending",
    created_at: new Date(Date.now() - 180000).toISOString(),
  },
  {
    action_id: "stab-003",
    action_type: "load_shedding",
    title: "Prepare Non-Essential Load Shedding",
    description: "Prepare to shed non-essential loads in Sector 3 if grid load exceeds 90%",
    target_domain: "power_grid",
    priority: 8,
    requires_approval: true,
    status: "pending",
    created_at: new Date(Date.now() - 120000).toISOString(),
  },
];

const domainColors: Record<string, string> = {
  traffic: "bg-blue-500",
  power_grid: "bg-yellow-500",
  crime: "bg-red-500",
  ems: "bg-green-500",
  fire: "bg-orange-500",
  weather: "bg-purple-500",
  flooding: "bg-cyan-500",
  crowd: "bg-pink-500",
};

export default function CityStabilizationDashboard() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>(mockAnomalies);
  const [cascadePredictions, setCascadePredictions] = useState<CascadePrediction[]>(mockCascadePredictions);
  const [stabilizationActions, setStabilizationActions] = useState<StabilizationAction[]>(mockStabilizationActions);
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null);
  const [circuitBreakerOpen, setCircuitBreakerOpen] = useState(false);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "text-red-500 bg-red-500/20 border-red-500";
      case "high":
        return "text-orange-500 bg-orange-500/20 border-orange-500";
      case "medium":
        return "text-yellow-500 bg-yellow-500/20 border-yellow-500";
      case "low":
        return "text-green-500 bg-green-500/20 border-green-500";
      default:
        return "text-gray-500 bg-gray-500/20 border-gray-500";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "executed":
        return "text-green-400 bg-green-400/20";
      case "pending":
        return "text-yellow-400 bg-yellow-400/20";
      case "failed":
        return "text-red-400 bg-red-400/20";
      default:
        return "text-gray-400 bg-gray-400/20";
    }
  };

  const handleResolveAnomaly = (anomalyId: string) => {
    setAnomalies((prev) => prev.filter((a) => a.anomaly_id !== anomalyId));
    setCascadePredictions((prev) => prev.filter((p) => p.trigger_anomaly !== anomalyId));
  };

  const handleApproveAction = (actionId: string) => {
    setStabilizationActions((prev) =>
      prev.map((a) =>
        a.action_id === actionId
          ? { ...a, status: "executed", executed_at: new Date().toISOString() }
          : a
      )
    );
  };

  const handleResetCircuitBreaker = () => {
    setCircuitBreakerOpen(false);
  };

  return (
    <div className="space-y-6">
      {circuitBreakerOpen && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse" />
            <div>
              <h3 className="text-red-400 font-semibold">Circuit Breaker Triggered</h3>
              <p className="text-red-300 text-sm">
                Autonomy system has switched to manual mode due to consecutive failures
              </p>
            </div>
          </div>
          <button
            onClick={handleResetCircuitBreaker}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Reset Circuit Breaker
          </button>
        </div>
      )}

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-8 space-y-6">
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Active Anomalies</h2>
              <span className="px-2 py-1 bg-red-500/20 text-red-400 text-sm rounded">
                {anomalies.length} Active
              </span>
            </div>
            <div className="divide-y divide-gray-700">
              {anomalies.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No active anomalies detected
                </div>
              ) : (
                anomalies.map((anomaly) => (
                  <div
                    key={anomaly.anomaly_id}
                    className={`p-4 border-l-4 ${getSeverityColor(anomaly.severity).split(" ")[2]} hover:bg-gray-700/50 transition-colors`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`w-3 h-3 rounded-full ${domainColors[anomaly.domain] || "bg-gray-500"}`} />
                          <span className="text-gray-400 text-sm capitalize">{anomaly.domain.replace(/_/g, " ")}</span>
                          <span className={`px-2 py-0.5 text-xs rounded ${getSeverityColor(anomaly.severity)}`}>
                            {anomaly.severity.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500">
                            {Math.round(anomaly.confidence * 100)}% confidence
                          </span>
                        </div>
                        <h3 className="text-white font-medium mb-1">{anomaly.title}</h3>
                        <p className="text-gray-400 text-sm mb-2">{anomaly.description}</p>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-gray-500">
                            Area: <span className="text-gray-300">{anomaly.affected_area}</span>
                          </span>
                          <span className="text-gray-500">
                            Cascade Risk:{" "}
                            <span
                              className={
                                anomaly.cascade_risk > 0.5
                                  ? "text-red-400"
                                  : anomaly.cascade_risk > 0.3
                                  ? "text-yellow-400"
                                  : "text-green-400"
                              }
                            >
                              {Math.round(anomaly.cascade_risk * 100)}%
                            </span>
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-3">
                          {Object.entries(anomaly.metrics).map(([key, value]) => (
                            <span
                              key={key}
                              className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded"
                            >
                              {key.replace(/_/g, " ")}: {typeof value === "number" ? value.toFixed(1) : value}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex flex-col gap-2 ml-4">
                        <button
                          onClick={() => setSelectedAnomaly(anomaly)}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                        >
                          Details
                        </button>
                        <button
                          onClick={() => handleResolveAnomaly(anomaly.anomaly_id)}
                          className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                        >
                          Resolve
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {cascadePredictions.length > 0 && (
            <div className="bg-gray-800 rounded-lg border border-red-500/50">
              <div className="px-4 py-3 border-b border-gray-700 bg-red-500/10">
                <h2 className="text-lg font-semibold text-red-400">Cascade Failure Predictions</h2>
              </div>
              <div className="divide-y divide-gray-700">
                {cascadePredictions.map((prediction) => (
                  <div key={prediction.prediction_id} className="p-4">
                    <div className="flex items-center gap-4 mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400 text-sm">Probability:</span>
                        <span className="text-red-400 font-medium">
                          {Math.round(prediction.probability * 100)}%
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400 text-sm">Time to Cascade:</span>
                        <span className="text-yellow-400 font-medium">
                          {prediction.time_to_cascade_minutes} min
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-300 mb-3">{prediction.estimated_impact}</p>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-400 mb-2">Predicted Failures</h4>
                        <ul className="space-y-1">
                          {prediction.predicted_failures.map((failure, i) => (
                            <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
                              <span className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                              {failure}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-400 mb-2">Recommended Actions</h4>
                        <ul className="space-y-1">
                          {prediction.recommended_actions.map((action, i) => (
                            <li key={i} className="text-gray-300 text-sm flex items-center gap-2">
                              <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                              {action}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="text-gray-500 text-sm">Affected Systems:</span>
                      {prediction.affected_systems.map((system, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 bg-gray-700 text-gray-300 text-xs rounded"
                        >
                          {system}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="col-span-4 space-y-6">
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="px-4 py-3 border-b border-gray-700">
              <h2 className="text-lg font-semibold text-white">Stabilization Actions</h2>
            </div>
            <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
              {stabilizationActions.map((action) => (
                <div key={action.action_id} className="p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${domainColors[action.target_domain] || "bg-gray-500"}`} />
                      <span className={`px-2 py-0.5 text-xs rounded ${getStatusColor(action.status)}`}>
                        {action.status.toUpperCase()}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">Priority: {action.priority}</span>
                  </div>
                  <h3 className="text-white font-medium text-sm mb-1">{action.title}</h3>
                  <p className="text-gray-400 text-xs mb-2">{action.description}</p>
                  {action.status === "pending" && action.requires_approval && (
                    <button
                      onClick={() => handleApproveAction(action.action_id)}
                      className="w-full px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                    >
                      Approve & Execute
                    </button>
                  )}
                  {action.executed_at && (
                    <p className="text-xs text-gray-500">
                      Executed {new Date(action.executed_at).toLocaleTimeString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-4">Domain Status</h3>
            <div className="space-y-3">
              {Object.entries(domainColors).map(([domain, color]) => {
                const domainAnomalies = anomalies.filter((a) => a.domain === domain);
                const hasAnomaly = domainAnomalies.length > 0;
                const maxSeverity = hasAnomaly
                  ? domainAnomalies.reduce((max, a) => {
                      const severityOrder = ["low", "medium", "high", "critical"];
                      return severityOrder.indexOf(a.severity) > severityOrder.indexOf(max)
                        ? a.severity
                        : max;
                    }, "low")
                  : null;

                return (
                  <div key={domain} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`w-3 h-3 rounded-full ${color}`} />
                      <span className="text-gray-300 capitalize">{domain.replace(/_/g, " ")}</span>
                    </div>
                    {hasAnomaly ? (
                      <span
                        className={`px-2 py-0.5 text-xs rounded ${getSeverityColor(maxSeverity || "low")}`}
                      >
                        {domainAnomalies.length} {domainAnomalies.length === 1 ? "Anomaly" : "Anomalies"}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 text-xs rounded bg-green-500/20 text-green-400">
                        Normal
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-white font-semibold mb-4">Manual Override Control</h3>
            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors">
                Pause All Autonomous Actions
              </button>
              <button className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors">
                Emergency Stop
              </button>
              <button className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                Run Manual Stabilization Cycle
              </button>
            </div>
          </div>
        </div>
      </div>

      {selectedAnomaly && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg border border-gray-700 w-full max-w-2xl">
            <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">Anomaly Details</h2>
              <button
                onClick={() => setSelectedAnomaly(null)}
                className="text-gray-400 hover:text-white"
              >
                Close
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-3">
                <span className={`w-4 h-4 rounded-full ${domainColors[selectedAnomaly.domain] || "bg-gray-500"}`} />
                <span className="text-gray-300 capitalize text-lg">
                  {selectedAnomaly.domain.replace(/_/g, " ")}
                </span>
                <span className={`px-2 py-0.5 text-sm rounded ${getSeverityColor(selectedAnomaly.severity)}`}>
                  {selectedAnomaly.severity.toUpperCase()}
                </span>
              </div>
              <h3 className="text-white text-xl font-medium">{selectedAnomaly.title}</h3>
              <p className="text-gray-400">{selectedAnomaly.description}</p>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700/50 p-3 rounded">
                  <span className="text-gray-400 text-sm">Affected Area</span>
                  <p className="text-white">{selectedAnomaly.affected_area}</p>
                </div>
                <div className="bg-gray-700/50 p-3 rounded">
                  <span className="text-gray-400 text-sm">Detected At</span>
                  <p className="text-white">{new Date(selectedAnomaly.detected_at).toLocaleString()}</p>
                </div>
                <div className="bg-gray-700/50 p-3 rounded">
                  <span className="text-gray-400 text-sm">Confidence</span>
                  <p className="text-white">{Math.round(selectedAnomaly.confidence * 100)}%</p>
                </div>
                <div className="bg-gray-700/50 p-3 rounded">
                  <span className="text-gray-400 text-sm">Cascade Risk</span>
                  <p
                    className={
                      selectedAnomaly.cascade_risk > 0.5
                        ? "text-red-400"
                        : selectedAnomaly.cascade_risk > 0.3
                        ? "text-yellow-400"
                        : "text-green-400"
                    }
                  >
                    {Math.round(selectedAnomaly.cascade_risk * 100)}%
                  </p>
                </div>
              </div>
              <div>
                <h4 className="text-gray-300 font-medium mb-2">Metrics</h4>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries(selectedAnomaly.metrics).map(([key, value]) => (
                    <div key={key} className="bg-gray-700/50 p-2 rounded">
                      <span className="text-gray-400 text-xs">{key.replace(/_/g, " ")}</span>
                      <p className="text-white font-medium">
                        {typeof value === "number" ? value.toFixed(2) : value}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
