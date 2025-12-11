"use client";

import React, { useState } from "react";

interface BiasMetric {
  name: string;
  value: number;
  threshold: number;
  status: "PASS" | "FAIL" | "WARNING";
  affectedGroup: string;
}

interface BiasAlert {
  id: string;
  timestamp: string;
  analysisType: string;
  status: string;
  affectedGroups: string[];
  metrics: BiasMetric[];
  blocked: boolean;
}

const mockBiasAlerts: BiasAlert[] = [
  {
    id: "bias-001",
    timestamp: "2024-01-15T14:32:00Z",
    analysisType: "PREDICTIVE_AI",
    status: "POSSIBLE_BIAS_FLAG_REVIEW",
    affectedGroups: ["Black Community"],
    metrics: [
      { name: "Disparate Impact Ratio", value: 0.72, threshold: 0.8, status: "FAIL", affectedGroup: "Black" },
      { name: "Demographic Parity", value: 0.15, threshold: 0.1, status: "FAIL", affectedGroup: "Black" },
      { name: "Equal Opportunity", value: 0.08, threshold: 0.1, status: "PASS", affectedGroup: "Black" },
      { name: "Predictive Equality", value: 0.09, threshold: 0.1, status: "PASS", affectedGroup: "Black" },
      { name: "Calibration Fairness", value: 0.07, threshold: 0.1, status: "PASS", affectedGroup: "Black" },
    ],
    blocked: false,
  },
  {
    id: "bias-002",
    timestamp: "2024-01-15T13:15:00Z",
    analysisType: "PATROL_ROUTING",
    status: "NO_BIAS_DETECTED",
    affectedGroups: [],
    metrics: [
      { name: "Disparate Impact Ratio", value: 0.92, threshold: 0.8, status: "PASS", affectedGroup: "N/A" },
      { name: "Demographic Parity", value: 0.05, threshold: 0.1, status: "PASS", affectedGroup: "N/A" },
      { name: "Equal Opportunity", value: 0.04, threshold: 0.1, status: "PASS", affectedGroup: "N/A" },
      { name: "Predictive Equality", value: 0.03, threshold: 0.1, status: "PASS", affectedGroup: "N/A" },
      { name: "Calibration Fairness", value: 0.02, threshold: 0.1, status: "PASS", affectedGroup: "N/A" },
    ],
    blocked: false,
  },
  {
    id: "bias-003",
    timestamp: "2024-01-15T12:45:00Z",
    analysisType: "RISK_SCORE",
    status: "BIAS_DETECTED_BLOCKED",
    affectedGroups: ["Black Community", "Hispanic Community"],
    metrics: [
      { name: "Disparate Impact Ratio", value: 0.58, threshold: 0.8, status: "FAIL", affectedGroup: "Black" },
      { name: "Demographic Parity", value: 0.22, threshold: 0.1, status: "FAIL", affectedGroup: "Black" },
      { name: "Equal Opportunity", value: 0.18, threshold: 0.1, status: "FAIL", affectedGroup: "Hispanic" },
      { name: "Predictive Equality", value: 0.15, threshold: 0.1, status: "FAIL", affectedGroup: "Black" },
      { name: "Calibration Fairness", value: 0.12, threshold: 0.1, status: "FAIL", affectedGroup: "Hispanic" },
    ],
    blocked: true,
  },
];

const mockDisparateImpactData = [
  { group: "Black", ratio: 0.72, population: 66 },
  { group: "White", ratio: 1.0, population: 22 },
  { group: "Hispanic", ratio: 0.85, population: 8 },
  { group: "Asian", ratio: 0.95, population: 2 },
  { group: "Other", ratio: 0.90, population: 2 },
];

export default function BiasMonitorConsole() {
  const [selectedAlert, setSelectedAlert] = useState<BiasAlert | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const getStatusColor = (status: string) => {
    switch (status) {
      case "NO_BIAS_DETECTED":
        return "bg-green-500";
      case "POSSIBLE_BIAS_FLAG_REVIEW":
        return "bg-yellow-500";
      case "BIAS_DETECTED_BLOCKED":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "NO_BIAS_DETECTED":
        return "No Bias";
      case "POSSIBLE_BIAS_FLAG_REVIEW":
        return "Review Required";
      case "BIAS_DETECTED_BLOCKED":
        return "Blocked";
      default:
        return status;
    }
  };

  const getMetricStatusColor = (status: string) => {
    switch (status) {
      case "PASS":
        return "text-green-400";
      case "FAIL":
        return "text-red-400";
      case "WARNING":
        return "text-yellow-400";
      default:
        return "text-gray-400";
    }
  };

  const filteredAlerts = mockBiasAlerts.filter((alert) => {
    if (filterStatus === "all") return true;
    return alert.status === filterStatus;
  });

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-sm text-gray-400">Total Analyses</div>
          <div className="text-2xl font-bold text-white">1,247</div>
          <div className="text-xs text-gray-500 mt-1">Last 30 days</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-green-700">
          <div className="text-sm text-gray-400">No Bias Detected</div>
          <div className="text-2xl font-bold text-green-400">1,198</div>
          <div className="text-xs text-green-500 mt-1">96.1% pass rate</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-700">
          <div className="text-sm text-gray-400">Flagged for Review</div>
          <div className="text-2xl font-bold text-yellow-400">42</div>
          <div className="text-xs text-yellow-500 mt-1">3.4% review rate</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-700">
          <div className="text-sm text-gray-400">Blocked Actions</div>
          <div className="text-2xl font-bold text-red-400">7</div>
          <div className="text-xs text-red-500 mt-1">0.5% block rate</div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Disparate Impact by Demographic Group</h3>
        <div className="space-y-3">
          {mockDisparateImpactData.map((item) => (
            <div key={item.group} className="flex items-center space-x-4">
              <div className="w-24 text-sm text-gray-400">{item.group}</div>
              <div className="flex-1">
                <div className="h-6 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.ratio >= 0.8 ? "bg-green-500" : item.ratio >= 0.7 ? "bg-yellow-500" : "bg-red-500"
                    }`}
                    style={{ width: `${item.ratio * 100}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-16 text-right">
                <span className={item.ratio >= 0.8 ? "text-green-400" : item.ratio >= 0.7 ? "text-yellow-400" : "text-red-400"}>
                  {(item.ratio * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-20 text-right text-sm text-gray-500">
                {item.population}% pop.
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">80% Rule Threshold</span>
            <div className="flex items-center space-x-4">
              <span className="flex items-center"><span className="w-3 h-3 bg-green-500 rounded mr-2"></span>Pass (≥80%)</span>
              <span className="flex items-center"><span className="w-3 h-3 bg-yellow-500 rounded mr-2"></span>Warning (70-79%)</span>
              <span className="flex items-center"><span className="w-3 h-3 bg-red-500 rounded mr-2"></span>Fail (&lt;70%)</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Recent Bias Analyses</h3>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-gray-700 text-white text-sm rounded px-3 py-1 border border-gray-600"
              >
                <option value="all">All Status</option>
                <option value="NO_BIAS_DETECTED">No Bias</option>
                <option value="POSSIBLE_BIAS_FLAG_REVIEW">Review Required</option>
                <option value="BIAS_DETECTED_BLOCKED">Blocked</option>
              </select>
            </div>
          </div>
          <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
            {filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                onClick={() => setSelectedAlert(alert)}
                className={`p-4 cursor-pointer hover:bg-gray-750 transition-colors ${
                  selectedAlert?.id === alert.id ? "bg-gray-750" : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className={`w-3 h-3 rounded-full ${getStatusColor(alert.status)}`}></span>
                    <div>
                      <div className="text-sm font-medium text-white">{alert.analysisType.replace(/_/g, " ")}</div>
                      <div className="text-xs text-gray-400">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs px-2 py-1 rounded ${
                      alert.status === "NO_BIAS_DETECTED" ? "bg-green-900 text-green-300" :
                      alert.status === "POSSIBLE_BIAS_FLAG_REVIEW" ? "bg-yellow-900 text-yellow-300" :
                      "bg-red-900 text-red-300"
                    }`}>
                      {getStatusLabel(alert.status)}
                    </span>
                  </div>
                </div>
                {alert.affectedGroups.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {alert.affectedGroups.map((group) => (
                      <span key={group} className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">
                        {group}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Analysis Details</h3>
          </div>
          {selectedAlert ? (
            <div className="p-4">
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Analysis ID</span>
                  <span className="text-sm text-white font-mono">{selectedAlert.id}</span>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Type</span>
                  <span className="text-sm text-white">{selectedAlert.analysisType.replace(/_/g, " ")}</span>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Status</span>
                  <span className={`text-sm px-2 py-0.5 rounded ${
                    selectedAlert.status === "NO_BIAS_DETECTED" ? "bg-green-900 text-green-300" :
                    selectedAlert.status === "POSSIBLE_BIAS_FLAG_REVIEW" ? "bg-yellow-900 text-yellow-300" :
                    "bg-red-900 text-red-300"
                  }`}>
                    {getStatusLabel(selectedAlert.status)}
                  </span>
                </div>
                {selectedAlert.blocked && (
                  <div className="mt-2 p-2 bg-red-900/30 border border-red-700 rounded">
                    <span className="text-sm text-red-300">Action was blocked due to bias detection</span>
                  </div>
                )}
              </div>

              <div className="border-t border-gray-700 pt-4">
                <h4 className="text-sm font-semibold text-white mb-3">Fairness Metrics</h4>
                <div className="space-y-2">
                  {selectedAlert.metrics.map((metric) => (
                    <div key={metric.name} className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">{metric.name}</span>
                      <div className="flex items-center space-x-2">
                        <span className={getMetricStatusColor(metric.status)}>
                          {metric.name.includes("Ratio") ? `${(metric.value * 100).toFixed(0)}%` : metric.value.toFixed(2)}
                        </span>
                        <span className="text-gray-500">/ {metric.name.includes("Ratio") ? `${metric.threshold * 100}%` : metric.threshold}</span>
                        <span className={`w-2 h-2 rounded-full ${
                          metric.status === "PASS" ? "bg-green-500" : metric.status === "FAIL" ? "bg-red-500" : "bg-yellow-500"
                        }`}></span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {selectedAlert.affectedGroups.length > 0 && (
                <div className="border-t border-gray-700 pt-4 mt-4">
                  <h4 className="text-sm font-semibold text-white mb-2">Affected Groups</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedAlert.affectedGroups.map((group) => (
                      <span key={group} className="text-sm bg-red-900/30 text-red-300 px-3 py-1 rounded border border-red-700">
                        {group}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              Select an analysis to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
