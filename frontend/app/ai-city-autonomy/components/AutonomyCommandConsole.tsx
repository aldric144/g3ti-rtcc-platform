"use client";

import React, { useState, useEffect } from "react";

interface Action {
  action_id: string;
  action_type: string;
  category: string;
  level: number;
  title: string;
  description: string;
  parameters: Record<string, unknown>;
  risk_level: string;
  risk_score: number;
  status: string;
  explainability: {
    decision_tree: unknown;
    model_weights: Record<string, number>;
    recommended_path: string[];
    risk_factors: string[];
    confidence_score: number;
    reasoning: string;
    data_sources: string[];
    alternative_actions: string[];
  };
  created_at: string;
  approved_at?: string;
  approved_by?: string;
  executed_at?: string;
  completed_at?: string;
  priority: number;
}

interface AuditEntry {
  entry_id: string;
  event_type: string;
  severity: string;
  timestamp: string;
  actor_name: string;
  description: string;
}

const mockPendingActions: Action[] = [
  {
    action_id: "action-abc123def456",
    action_type: "deploy_units",
    category: "patrol_deployment",
    level: 2,
    title: "Deploy Additional Patrol Units to Downtown",
    description: "Crime spike detected in downtown area. Recommend deploying 3 additional patrol units for enhanced coverage.",
    parameters: { units: 3, zone: "downtown", duration_hours: 4 },
    risk_level: "medium",
    risk_score: 0.45,
    status: "pending",
    explainability: {
      decision_tree: null,
      model_weights: { crime_density: 0.4, response_time: 0.3, resource_availability: 0.3 },
      recommended_path: ["Analyze crime data", "Identify hotspot", "Calculate coverage gap", "Recommend deployment"],
      risk_factors: ["Increased crime incidents", "Response time degradation", "Coverage gap in sector 4"],
      confidence_score: 0.87,
      reasoning: "Crime density in downtown increased 45% in last 2 hours. Current patrol coverage is insufficient.",
      data_sources: ["CAD System", "Crime Analytics", "Patrol GPS"],
      alternative_actions: ["Increase patrol frequency", "Deploy unmarked units", "Request mutual aid"],
    },
    created_at: new Date().toISOString(),
    priority: 8,
  },
  {
    action_id: "action-xyz789ghi012",
    action_type: "coordinate_evacuation",
    category: "evacuation",
    level: 2,
    title: "Prepare Flood Zone A Evacuation",
    description: "Rising water levels detected. Recommend preparing evacuation routes for Flood Zone A residents.",
    parameters: { zone: "flood_zone_a", shelters: ["riviera_beach_high", "community_center"] },
    risk_level: "high",
    risk_score: 0.72,
    status: "pending",
    explainability: {
      decision_tree: null,
      model_weights: { water_level: 0.5, forecast: 0.3, population_density: 0.2 },
      recommended_path: ["Monitor water levels", "Analyze forecast", "Identify affected population", "Prepare evacuation"],
      risk_factors: ["Water level at 5.2ft", "Additional rainfall expected", "1,200 residents in zone"],
      confidence_score: 0.91,
      reasoning: "Water levels approaching critical threshold. NWS forecast indicates additional 2 inches of rain.",
      data_sources: ["USGS Water Sensors", "NWS Forecast", "Census Data"],
      alternative_actions: ["Issue voluntary evacuation", "Pre-position rescue boats", "Alert shelters"],
    },
    created_at: new Date(Date.now() - 300000).toISOString(),
    priority: 9,
  },
];

const mockRecentActions: Action[] = [
  {
    action_id: "action-completed001",
    action_type: "traffic_signal_timing",
    category: "traffic_control",
    level: 1,
    title: "Optimize Blue Heron Blvd Signal Timing",
    description: "Adjusted signal timing to reduce congestion during peak hours.",
    parameters: { intersection: "blue_heron_us1", cycle_adjustment: 15 },
    risk_level: "low",
    risk_score: 0.15,
    status: "completed",
    explainability: {
      decision_tree: null,
      model_weights: { congestion: 0.5, wait_time: 0.3, throughput: 0.2 },
      recommended_path: ["Detect congestion", "Analyze traffic flow", "Calculate optimal timing", "Apply adjustment"],
      risk_factors: [],
      confidence_score: 0.94,
      reasoning: "Congestion index exceeded threshold. Signal timing optimization reduces average wait time by 23%.",
      data_sources: ["Traffic Sensors", "Signal Controller"],
      alternative_actions: [],
    },
    created_at: new Date(Date.now() - 600000).toISOString(),
    executed_at: new Date(Date.now() - 590000).toISOString(),
    completed_at: new Date(Date.now() - 580000).toISOString(),
    priority: 6,
  },
];

const mockAuditTrail: AuditEntry[] = [
  {
    entry_id: "audit-001",
    event_type: "action_created",
    severity: "info",
    timestamp: new Date().toISOString(),
    actor_name: "City Brain AI",
    description: "Action created: Deploy Additional Patrol Units to Downtown",
  },
  {
    entry_id: "audit-002",
    event_type: "action_completed",
    severity: "info",
    timestamp: new Date(Date.now() - 580000).toISOString(),
    actor_name: "Autonomy Engine",
    description: "Action auto-executed: Optimize Blue Heron Blvd Signal Timing",
  },
];

export default function AutonomyCommandConsole() {
  const [pendingActions, setPendingActions] = useState<Action[]>(mockPendingActions);
  const [recentActions, setRecentActions] = useState<Action[]>(mockRecentActions);
  const [auditTrail, setAuditTrail] = useState<AuditEntry[]>(mockAuditTrail);
  const [selectedAction, setSelectedAction] = useState<Action | null>(null);
  const [showExplainability, setShowExplainability] = useState(false);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "critical":
        return "text-red-500 bg-red-500/20";
      case "high":
        return "text-orange-500 bg-orange-500/20";
      case "medium":
        return "text-yellow-500 bg-yellow-500/20";
      case "low":
        return "text-green-500 bg-green-500/20";
      default:
        return "text-gray-500 bg-gray-500/20";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-400 bg-green-400/20";
      case "executing":
        return "text-blue-400 bg-blue-400/20";
      case "pending":
        return "text-yellow-400 bg-yellow-400/20";
      case "failed":
        return "text-red-400 bg-red-400/20";
      case "denied":
        return "text-gray-400 bg-gray-400/20";
      default:
        return "text-gray-400 bg-gray-400/20";
    }
  };

  const handleApprove = (actionId: string) => {
    setPendingActions((prev) => prev.filter((a) => a.action_id !== actionId));
    const action = pendingActions.find((a) => a.action_id === actionId);
    if (action) {
      setRecentActions((prev) => [
        { ...action, status: "completed", approved_at: new Date().toISOString(), approved_by: "Operator" },
        ...prev,
      ]);
    }
  };

  const handleDeny = (actionId: string) => {
    setPendingActions((prev) => prev.filter((a) => a.action_id !== actionId));
  };

  const RiskScoreIndicator = ({ score }: { score: number }) => {
    const percentage = Math.round(score * 100);
    const color =
      score >= 0.7 ? "bg-red-500" : score >= 0.4 ? "bg-yellow-500" : "bg-green-500";

    return (
      <div className="flex items-center gap-2">
        <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
          <div className={`h-full ${color}`} style={{ width: `${percentage}%` }} />
        </div>
        <span className="text-sm text-gray-400">{percentage}%</span>
      </div>
    );
  };

  return (
    <div className="grid grid-cols-12 gap-6">
      <div className="col-span-8 space-y-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Pending Actions Queue</h2>
            <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-sm rounded">
              {pendingActions.length} Awaiting Approval
            </span>
          </div>
          <div className="divide-y divide-gray-700">
            {pendingActions.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No pending actions requiring approval
              </div>
            ) : (
              pendingActions.map((action) => (
                <div key={action.action_id} className="p-4 hover:bg-gray-700/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded">
                          Level {action.level}
                        </span>
                        <span className={`px-2 py-0.5 text-xs rounded ${getRiskColor(action.risk_level)}`}>
                          {action.risk_level.toUpperCase()} RISK
                        </span>
                        <span className="text-xs text-gray-500">
                          Priority: {action.priority}/10
                        </span>
                      </div>
                      <h3 className="text-white font-medium mb-1">{action.title}</h3>
                      <p className="text-gray-400 text-sm mb-3">{action.description}</p>
                      <div className="flex items-center gap-4">
                        <div>
                          <span className="text-xs text-gray-500">Risk Score</span>
                          <RiskScoreIndicator score={action.risk_score} />
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">Confidence</span>
                          <div className="text-sm text-blue-400">
                            {Math.round(action.explainability.confidence_score * 100)}%
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2 ml-4">
                      <button
                        onClick={() => handleApprove(action.action_id)}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleDeny(action.action_id)}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                      >
                        Deny
                      </button>
                      <button
                        onClick={() => {
                          setSelectedAction(action);
                          setShowExplainability(true);
                        }}
                        className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors"
                      >
                        Explain
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-4 py-3 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Recent Actions</h2>
          </div>
          <div className="divide-y divide-gray-700">
            {recentActions.map((action) => (
              <div key={action.action_id} className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-0.5 text-xs rounded ${getStatusColor(action.status)}`}>
                        {action.status.toUpperCase()}
                      </span>
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded">
                        Level {action.level}
                      </span>
                    </div>
                    <h3 className="text-white font-medium">{action.title}</h3>
                    <p className="text-gray-500 text-sm">
                      {action.completed_at
                        ? `Completed ${new Date(action.completed_at).toLocaleTimeString()}`
                        : action.executed_at
                        ? `Executed ${new Date(action.executed_at).toLocaleTimeString()}`
                        : `Created ${new Date(action.created_at).toLocaleTimeString()}`}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedAction(action);
                      setShowExplainability(true);
                    }}
                    className="text-blue-400 hover:text-blue-300 text-sm"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="col-span-4 space-y-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-4 py-3 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Audit Trail</h2>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {auditTrail.map((entry) => (
              <div key={entry.entry_id} className="p-3 border-b border-gray-700 last:border-0">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      entry.severity === "critical"
                        ? "bg-red-500"
                        : entry.severity === "high"
                        ? "bg-orange-500"
                        : entry.severity === "medium"
                        ? "bg-yellow-500"
                        : "bg-green-500"
                    }`}
                  />
                  <span className="text-xs text-gray-500">
                    {new Date(entry.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm text-gray-300">{entry.description}</p>
                <p className="text-xs text-gray-500 mt-1">by {entry.actor_name}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <h3 className="text-white font-semibold mb-4">Action Statistics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Actions Today</span>
              <span className="text-white font-medium">47</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Auto-Executed (Level 1)</span>
              <span className="text-green-400 font-medium">38</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Approved (Level 2)</span>
              <span className="text-blue-400 font-medium">7</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Denied</span>
              <span className="text-red-400 font-medium">2</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Approval Time</span>
              <span className="text-white font-medium">4.2 min</span>
            </div>
          </div>
        </div>
      </div>

      {showExplainability && selectedAction && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg border border-gray-700 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">Action Explainability</h2>
              <button
                onClick={() => setShowExplainability(false)}
                className="text-gray-400 hover:text-white"
              >
                Close
              </button>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <h3 className="text-white font-medium mb-2">{selectedAction.title}</h3>
                <p className="text-gray-400">{selectedAction.description}</p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Reasoning</h4>
                <p className="text-gray-400 bg-gray-700/50 p-3 rounded">
                  {selectedAction.explainability.reasoning}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Decision Path</h4>
                <div className="space-y-2">
                  {selectedAction.explainability.recommended_path.map((step, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <span className="w-6 h-6 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs">
                        {index + 1}
                      </span>
                      <span className="text-gray-300">{step}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Model Weights</h4>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(selectedAction.explainability.model_weights).map(([key, value]) => (
                    <div key={key} className="bg-gray-700/50 p-2 rounded">
                      <span className="text-gray-400 text-sm">{key.replace(/_/g, " ")}</span>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="flex-1 h-2 bg-gray-600 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{ width: `${value * 100}%` }}
                          />
                        </div>
                        <span className="text-white text-sm">{Math.round(value * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {selectedAction.explainability.risk_factors.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Risk Factors</h4>
                  <ul className="space-y-1">
                    {selectedAction.explainability.risk_factors.map((factor, index) => (
                      <li key={index} className="text-gray-400 text-sm flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-yellow-500 rounded-full" />
                        {factor}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Data Sources</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedAction.explainability.data_sources.map((source, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-700 text-gray-300 text-sm rounded"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              </div>

              {selectedAction.explainability.alternative_actions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Alternative Actions</h4>
                  <ul className="space-y-1">
                    {selectedAction.explainability.alternative_actions.map((alt, index) => (
                      <li key={index} className="text-gray-400 text-sm">
                        {index + 1}. {alt}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
