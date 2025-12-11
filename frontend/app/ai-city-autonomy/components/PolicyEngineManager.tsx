"use client";

import React, { useState } from "react";

interface PolicyRule {
  rule_id: string;
  name: string;
  description: string;
  condition: string;
  action: string;
  priority: number;
  enabled: boolean;
}

interface PolicyThreshold {
  threshold_id: string;
  name: string;
  metric: string;
  operator: string;
  value: number;
  unit: string;
  action_on_breach: string;
}

interface Policy {
  policy_id: string;
  name: string;
  description: string;
  policy_type: string;
  scope: string;
  scope_id?: string;
  rules: PolicyRule[];
  thresholds: PolicyThreshold[];
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
  tags: string[];
}

interface EmergencyOverride {
  override_id: string;
  name: string;
  emergency_type: string;
  description: string;
  is_active: boolean;
  activated_at?: string;
  activated_by?: string;
  affected_policies: string[];
  override_rules: PolicyRule[];
}

interface PolicyConflict {
  conflict_id: string;
  policy_a: string;
  policy_b: string;
  rule_a: string;
  rule_b: string;
  conflict_type: string;
  description: string;
  severity: string;
  resolution_suggestion: string;
}

const mockPolicies: Policy[] = [
  {
    policy_id: "policy-traffic-001",
    name: "Traffic Flow Optimization",
    description: "Automated traffic signal timing and congestion management for Riviera Beach",
    policy_type: "traffic",
    scope: "city",
    rules: [
      {
        rule_id: "rule-001",
        name: "Peak Hour Optimization",
        description: "Optimize signal timing during peak hours",
        condition: "time >= 07:00 AND time <= 09:00 OR time >= 16:00 AND time <= 18:00",
        action: "optimize_signal_timing",
        priority: 8,
        enabled: true,
      },
      {
        rule_id: "rule-002",
        name: "Congestion Response",
        description: "Adjust timing when congestion exceeds threshold",
        condition: "congestion_index > 0.7",
        action: "extend_green_phase",
        priority: 9,
        enabled: true,
      },
    ],
    thresholds: [
      {
        threshold_id: "thresh-001",
        name: "Congestion Alert",
        metric: "congestion_index",
        operator: "gt",
        value: 0.8,
        unit: "index",
        action_on_breach: "alert_traffic_ops",
      },
    ],
    status: "active",
    version: 3,
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-03-20T14:30:00Z",
    tags: ["traffic", "automation", "riviera-beach"],
  },
  {
    policy_id: "policy-patrol-001",
    name: "Patrol Deployment Policy",
    description: "Rules for automated patrol unit deployment and rebalancing",
    policy_type: "patrol",
    scope: "department",
    scope_id: "police",
    rules: [
      {
        rule_id: "rule-003",
        name: "Crime Spike Response",
        description: "Deploy additional units when crime spike detected",
        condition: "crime_density > baseline * 1.5",
        action: "deploy_additional_units",
        priority: 9,
        enabled: true,
      },
      {
        rule_id: "rule-004",
        name: "Coverage Rebalancing",
        description: "Rebalance patrol coverage when gaps detected",
        condition: "coverage_gap > 0.3",
        action: "rebalance_patrol",
        priority: 7,
        enabled: true,
      },
    ],
    thresholds: [
      {
        threshold_id: "thresh-002",
        name: "Response Time Alert",
        metric: "avg_response_time",
        operator: "gt",
        value: 8,
        unit: "minutes",
        action_on_breach: "alert_dispatch",
      },
    ],
    status: "active",
    version: 2,
    created_at: "2024-02-01T08:00:00Z",
    updated_at: "2024-03-15T11:00:00Z",
    tags: ["patrol", "police", "safety"],
  },
];

const mockEmergencyOverrides: EmergencyOverride[] = [
  {
    override_id: "override-hurricane",
    name: "Hurricane Emergency Override",
    emergency_type: "hurricane",
    description: "Activates emergency protocols for hurricane events",
    is_active: false,
    affected_policies: ["policy-traffic-001", "policy-patrol-001"],
    override_rules: [
      {
        rule_id: "override-rule-001",
        name: "Evacuation Priority",
        description: "Prioritize evacuation routes",
        condition: "hurricane_warning = true",
        action: "activate_evacuation_routes",
        priority: 10,
        enabled: true,
      },
    ],
  },
  {
    override_id: "override-flooding",
    name: "Flood Emergency Override",
    emergency_type: "flooding",
    description: "Activates flood response protocols",
    is_active: false,
    affected_policies: ["policy-traffic-001"],
    override_rules: [
      {
        rule_id: "override-rule-002",
        name: "Flood Zone Closure",
        description: "Close flooded roads and reroute traffic",
        condition: "water_level > 2.0",
        action: "close_flood_zones",
        priority: 10,
        enabled: true,
      },
    ],
  },
];

const mockConflicts: PolicyConflict[] = [
  {
    conflict_id: "conflict-001",
    policy_a: "Traffic Flow Optimization",
    policy_b: "Emergency Response Priority",
    rule_a: "Peak Hour Optimization",
    rule_b: "Emergency Vehicle Priority",
    conflict_type: "priority_conflict",
    description: "Peak hour optimization may delay emergency vehicle preemption",
    severity: "medium",
    resolution_suggestion: "Add exception for emergency vehicle detection",
  },
];

export default function PolicyEngineManager() {
  const [policies, setPolicies] = useState<Policy[]>(mockPolicies);
  const [emergencyOverrides, setEmergencyOverrides] = useState<EmergencyOverride[]>(mockEmergencyOverrides);
  const [conflicts, setConflicts] = useState<PolicyConflict[]>(mockConflicts);
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null);
  const [activeView, setActiveView] = useState<"list" | "editor" | "simulation" | "conflicts">("list");
  const [simulationScenario, setSimulationScenario] = useState("");
  const [simulationResult, setSimulationResult] = useState<unknown>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-400 bg-green-400/20";
      case "testing":
        return "text-yellow-400 bg-yellow-400/20";
      case "draft":
        return "text-gray-400 bg-gray-400/20";
      case "deprecated":
        return "text-red-400 bg-red-400/20";
      default:
        return "text-gray-400 bg-gray-400/20";
    }
  };

  const getScopeColor = (scope: string) => {
    switch (scope) {
      case "global":
        return "text-purple-400 bg-purple-400/20";
      case "city":
        return "text-blue-400 bg-blue-400/20";
      case "department":
        return "text-cyan-400 bg-cyan-400/20";
      case "scenario":
        return "text-orange-400 bg-orange-400/20";
      default:
        return "text-gray-400 bg-gray-400/20";
    }
  };

  const handleActivateOverride = (overrideId: string) => {
    setEmergencyOverrides((prev) =>
      prev.map((o) =>
        o.override_id === overrideId
          ? { ...o, is_active: true, activated_at: new Date().toISOString(), activated_by: "Operator" }
          : o
      )
    );
  };

  const handleDeactivateOverride = (overrideId: string) => {
    setEmergencyOverrides((prev) =>
      prev.map((o) =>
        o.override_id === overrideId
          ? { ...o, is_active: false, activated_at: undefined, activated_by: undefined }
          : o
      )
    );
  };

  const runSimulation = () => {
    if (!selectedPolicy || !simulationScenario) return;

    setSimulationResult({
      policy_id: selectedPolicy.policy_id,
      scenario: simulationScenario,
      triggered_rules: selectedPolicy.rules.filter((r) => r.enabled).map((r) => r.name),
      actions_generated: selectedPolicy.rules.filter((r) => r.enabled).map((r) => ({
        rule: r.name,
        action: r.action,
        would_execute: true,
      })),
      conflicts_detected: [],
      metrics: {
        estimated_impact: 0.75,
        resource_usage: 0.45,
        risk_score: 0.2,
      },
      success: true,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => setActiveView("list")}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeView === "list"
              ? "bg-blue-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Policy List
        </button>
        <button
          onClick={() => setActiveView("editor")}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeView === "editor"
              ? "bg-blue-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Policy Editor
        </button>
        <button
          onClick={() => setActiveView("simulation")}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeView === "simulation"
              ? "bg-blue-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Simulation Sandbox
        </button>
        <button
          onClick={() => setActiveView("conflicts")}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeView === "conflicts"
              ? "bg-blue-600 text-white"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          Conflict Detector
          {conflicts.length > 0 && (
            <span className="ml-2 px-2 py-0.5 bg-yellow-500 text-black text-xs rounded-full">
              {conflicts.length}
            </span>
          )}
        </button>
      </div>

      {activeView === "list" && (
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-8">
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Active Policies</h2>
                <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
                  Create Policy
                </button>
              </div>
              <div className="divide-y divide-gray-700">
                {policies.map((policy) => (
                  <div
                    key={policy.policy_id}
                    className="p-4 hover:bg-gray-700/50 transition-colors cursor-pointer"
                    onClick={() => {
                      setSelectedPolicy(policy);
                      setActiveView("editor");
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`px-2 py-0.5 text-xs rounded ${getStatusColor(policy.status)}`}>
                            {policy.status.toUpperCase()}
                          </span>
                          <span className={`px-2 py-0.5 text-xs rounded ${getScopeColor(policy.scope)}`}>
                            {policy.scope.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500">v{policy.version}</span>
                        </div>
                        <h3 className="text-white font-medium">{policy.name}</h3>
                        <p className="text-gray-400 text-sm mt-1">{policy.description}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>{policy.rules.length} rules</span>
                          <span>{policy.thresholds.length} thresholds</span>
                          <span>Updated {new Date(policy.updated_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {policy.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-gray-700 text-gray-400 text-xs rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-span-4 space-y-6">
            <div className="bg-gray-800 rounded-lg border border-gray-700">
              <div className="px-4 py-3 border-b border-gray-700">
                <h2 className="text-lg font-semibold text-white">Emergency Overrides</h2>
              </div>
              <div className="divide-y divide-gray-700">
                {emergencyOverrides.map((override) => (
                  <div key={override.override_id} className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-white font-medium">{override.name}</h3>
                      <span
                        className={`px-2 py-0.5 text-xs rounded ${
                          override.is_active
                            ? "bg-red-500/20 text-red-400"
                            : "bg-gray-500/20 text-gray-400"
                        }`}
                      >
                        {override.is_active ? "ACTIVE" : "INACTIVE"}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mb-3">{override.description}</p>
                    {override.is_active ? (
                      <button
                        onClick={() => handleDeactivateOverride(override.override_id)}
                        className="w-full px-3 py-2 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors"
                      >
                        Deactivate Override
                      </button>
                    ) : (
                      <button
                        onClick={() => handleActivateOverride(override.override_id)}
                        className="w-full px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                      >
                        Activate Override
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <h3 className="text-white font-semibold mb-4">Policy Hierarchy</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-purple-500 rounded" />
                  <span className="text-gray-300">Global Policies</span>
                  <span className="text-gray-500 text-sm ml-auto">Highest Priority</span>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <div className="w-4 h-4 bg-blue-500 rounded" />
                  <span className="text-gray-300">City Policies</span>
                </div>
                <div className="flex items-center gap-2 ml-8">
                  <div className="w-4 h-4 bg-cyan-500 rounded" />
                  <span className="text-gray-300">Department Policies</span>
                </div>
                <div className="flex items-center gap-2 ml-12">
                  <div className="w-4 h-4 bg-orange-500 rounded" />
                  <span className="text-gray-300">Scenario Policies</span>
                  <span className="text-gray-500 text-sm ml-auto">Lowest Priority</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeView === "editor" && selectedPolicy && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">{selectedPolicy.name}</h2>
              <p className="text-gray-400 text-sm">Version {selectedPolicy.version}</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors">
                Rollback
              </button>
              <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
                Save Changes
              </button>
            </div>
          </div>
          <div className="p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <textarea
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                rows={2}
                defaultValue={selectedPolicy.description}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-medium">Rules</h3>
                <button className="text-blue-400 hover:text-blue-300 text-sm">Add Rule</button>
              </div>
              <div className="space-y-3">
                {selectedPolicy.rules.map((rule) => (
                  <div key={rule.rule_id} className="bg-gray-700/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={rule.enabled}
                          className="rounded bg-gray-600 border-gray-500"
                          readOnly
                        />
                        <span className="text-white font-medium">{rule.name}</span>
                        <span className="text-xs text-gray-500">Priority: {rule.priority}</span>
                      </div>
                      <button className="text-gray-400 hover:text-white text-sm">Edit</button>
                    </div>
                    <p className="text-gray-400 text-sm mb-2">{rule.description}</p>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Condition:</span>
                        <code className="ml-2 text-green-400">{rule.condition}</code>
                      </div>
                      <div>
                        <span className="text-gray-500">Action:</span>
                        <code className="ml-2 text-blue-400">{rule.action}</code>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-medium">Thresholds</h3>
                <button className="text-blue-400 hover:text-blue-300 text-sm">Add Threshold</button>
              </div>
              <div className="space-y-3">
                {selectedPolicy.thresholds.map((threshold) => (
                  <div key={threshold.threshold_id} className="bg-gray-700/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">{threshold.name}</span>
                      <button className="text-gray-400 hover:text-white text-sm">Edit</button>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Metric:</span>
                        <span className="ml-2 text-white">{threshold.metric}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Condition:</span>
                        <span className="ml-2 text-yellow-400">
                          {threshold.operator} {threshold.value} {threshold.unit}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Action:</span>
                        <span className="ml-2 text-blue-400">{threshold.action_on_breach}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeView === "simulation" && (
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="px-4 py-3 border-b border-gray-700">
              <h2 className="text-lg font-semibold text-white">Policy Simulation Sandbox</h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Select Policy</label>
                <select
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                  value={selectedPolicy?.policy_id || ""}
                  onChange={(e) => {
                    const policy = policies.find((p) => p.policy_id === e.target.value);
                    setSelectedPolicy(policy || null);
                  }}
                >
                  <option value="">Select a policy...</option>
                  {policies.map((policy) => (
                    <option key={policy.policy_id} value={policy.policy_id}>
                      {policy.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Scenario Data (JSON)</label>
                <textarea
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white font-mono text-sm"
                  rows={10}
                  placeholder='{"congestion_index": 0.85, "time": "08:30", "crime_density": 1.2}'
                  value={simulationScenario}
                  onChange={(e) => setSimulationScenario(e.target.value)}
                />
              </div>
              <button
                onClick={runSimulation}
                disabled={!selectedPolicy || !simulationScenario}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                Run Simulation
              </button>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="px-4 py-3 border-b border-gray-700">
              <h2 className="text-lg font-semibold text-white">Simulation Results</h2>
            </div>
            <div className="p-6">
              {simulationResult ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 rounded text-sm ${
                        (simulationResult as { success: boolean }).success
                          ? "bg-green-500/20 text-green-400"
                          : "bg-red-500/20 text-red-400"
                      }`}
                    >
                      {(simulationResult as { success: boolean }).success ? "SUCCESS" : "FAILED"}
                    </span>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Triggered Rules</h4>
                    <ul className="space-y-1">
                      {(simulationResult as { triggered_rules: string[] }).triggered_rules.map((rule, i) => (
                        <li key={i} className="text-gray-400 text-sm flex items-center gap-2">
                          <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                          {rule}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Actions Generated</h4>
                    <ul className="space-y-1">
                      {(simulationResult as { actions_generated: { rule: string; action: string }[] }).actions_generated.map((action, i) => (
                        <li key={i} className="text-gray-400 text-sm">
                          <span className="text-blue-400">{action.action}</span>
                          <span className="text-gray-500"> from {action.rule}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Metrics</h4>
                    <div className="grid grid-cols-3 gap-4">
                      {Object.entries((simulationResult as { metrics: Record<string, number> }).metrics).map(([key, value]) => (
                        <div key={key} className="bg-gray-700/50 p-3 rounded">
                          <span className="text-gray-400 text-xs">{key.replace(/_/g, " ")}</span>
                          <div className="text-white font-medium">{Math.round(value * 100)}%</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  Run a simulation to see results
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeView === "conflicts" && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Policy Conflict Detector</h2>
            <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
              Run Detection
            </button>
          </div>
          <div className="divide-y divide-gray-700">
            {conflicts.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No policy conflicts detected
              </div>
            ) : (
              conflicts.map((conflict) => (
                <div key={conflict.conflict_id} className="p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className={`px-2 py-0.5 text-xs rounded ${
                            conflict.severity === "high"
                              ? "bg-red-500/20 text-red-400"
                              : conflict.severity === "medium"
                              ? "bg-yellow-500/20 text-yellow-400"
                              : "bg-blue-500/20 text-blue-400"
                          }`}
                        >
                          {conflict.severity.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">{conflict.conflict_type}</span>
                      </div>
                      <h3 className="text-white font-medium mb-1">
                        {conflict.policy_a} vs {conflict.policy_b}
                      </h3>
                      <p className="text-gray-400 text-sm mb-2">{conflict.description}</p>
                      <div className="text-sm">
                        <span className="text-gray-500">Conflicting Rules: </span>
                        <span className="text-gray-300">
                          {conflict.rule_a} / {conflict.rule_b}
                        </span>
                      </div>
                    </div>
                    <button className="px-3 py-1.5 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded transition-colors">
                      Resolve
                    </button>
                  </div>
                  <div className="mt-3 p-3 bg-gray-700/50 rounded">
                    <span className="text-gray-400 text-sm">Suggested Resolution: </span>
                    <span className="text-green-400 text-sm">{conflict.resolution_suggestion}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
