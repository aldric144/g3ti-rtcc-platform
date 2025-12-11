"use client";

import React, { useState, useEffect } from "react";

interface DVAlert {
  alert_id: string;
  timestamp: string;
  escalation_level: string;
  lethality_score: number;
  zone: string;
  campbell_indicators: string[];
  intervention_pathway: string;
  recommended_actions: string[];
}

interface DVHotspot {
  zone_id: string;
  risk_level: string;
  incident_count: number;
  repeat_patterns: number;
  trend: string;
}

export default function DVHotspotPredictor() {
  const [alerts, setAlerts] = useState<DVAlert[]>([
    {
      alert_id: "DV-001",
      timestamp: new Date().toISOString(),
      escalation_level: "HIGH",
      lethality_score: 0.65,
      zone: "Zone_A",
      campbell_indicators: ["strangulation_history", "threats_to_kill", "weapon_in_home"],
      intervention_pathway: "ENHANCED_RESPONSE",
      recommended_actions: ["Dispatch with DV-trained officers", "Contact DV advocate", "Provide safety planning"],
    },
  ]);
  const [hotspots, setHotspots] = useState<DVHotspot[]>([
    { zone_id: "Zone_A", risk_level: "HIGH", incident_count: 8, repeat_patterns: 3, trend: "increasing" },
    { zone_id: "Zone_B", risk_level: "MODERATE", incident_count: 4, repeat_patterns: 1, trend: "stable" },
    { zone_id: "Zone_C", risk_level: "LOW", incident_count: 2, repeat_patterns: 0, trend: "decreasing" },
    { zone_id: "Zone_D", risk_level: "MODERATE", incident_count: 5, repeat_patterns: 2, trend: "stable" },
  ]);
  const [selectedAlert, setSelectedAlert] = useState<DVAlert | null>(null);
  const [viewMode, setViewMode] = useState<"alerts" | "hotspots">("alerts");

  const getEscalationColor = (level: string): string => {
    switch (level) {
      case "EXTREME": return "bg-red-800 text-white";
      case "HIGH": return "bg-red-600 text-white";
      case "MODERATE": return "bg-orange-500 text-white";
      case "LOW": return "bg-yellow-500 text-black";
      case "MINIMAL": return "bg-green-500 text-white";
      default: return "bg-gray-500 text-white";
    }
  };

  const getLethalityColor = (score: number): string => {
    if (score >= 0.7) return "#ef4444";
    if (score >= 0.5) return "#f97316";
    if (score >= 0.3) return "#eab308";
    return "#22c55e";
  };

  const getTrendIcon = (trend: string): string => {
    switch (trend) {
      case "increasing": return "↑";
      case "decreasing": return "↓";
      default: return "→";
    }
  };

  const getTrendColor = (trend: string): string => {
    switch (trend) {
      case "increasing": return "text-red-400";
      case "decreasing": return "text-green-400";
      default: return "text-gray-400";
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Domestic Violence Hotspot Predictor</h2>

      <div className="bg-red-900 border border-red-600 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 text-red-200">
          <span className="text-2xl">🏠</span>
          <div>
            <div className="font-semibold">DV Resources</div>
            <div className="text-sm">National DV Hotline: 1-800-799-7233 | Local Shelter: (561) 555-SAFE</div>
          </div>
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setViewMode("alerts")}
          className={`px-4 py-2 rounded ${viewMode === "alerts" ? "bg-blue-600" : "bg-gray-600"}`}
        >
          Active Alerts
        </button>
        <button
          onClick={() => setViewMode("hotspots")}
          className={`px-4 py-2 rounded ${viewMode === "hotspots" ? "bg-blue-600" : "bg-gray-600"}`}
        >
          Hotspot Map
        </button>
      </div>

      {viewMode === "alerts" ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">High-Risk DV Alerts</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {alerts.map((alert) => (
                  <div
                    key={alert.alert_id}
                    className={`p-4 rounded-lg cursor-pointer transition-all ${
                      selectedAlert?.alert_id === alert.alert_id
                        ? "bg-gray-600 ring-2 ring-blue-500"
                        : "bg-gray-600 hover:bg-gray-550"
                    }`}
                    onClick={() => setSelectedAlert(alert)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${getEscalationColor(alert.escalation_level)}`}>
                          {alert.escalation_level}
                        </span>
                        <span className="text-sm text-gray-400">
                          Lethality: {(alert.lethality_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <span className="text-gray-400 text-sm">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-sm">
                        <span className="font-semibold">{alert.zone}</span>
                      </div>
                      <div className="text-sm text-gray-400">
                        {alert.campbell_indicators.length} Campbell indicator(s)
                      </div>
                    </div>
                    <div className="mt-2 w-full bg-gray-500 rounded-full h-2">
                      <div
                        className="h-2 rounded-full"
                        style={{
                          width: `${alert.lethality_score * 100}%`,
                          backgroundColor: getLethalityColor(alert.lethality_score),
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Alert Details</h3>
              {selectedAlert ? (
                <div className="space-y-4">
                  <div>
                    <div className="text-gray-400 text-sm">Alert ID</div>
                    <div className="font-mono">{selectedAlert.alert_id}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Escalation Level</div>
                    <span className={`px-2 py-1 rounded text-sm ${getEscalationColor(selectedAlert.escalation_level)}`}>
                      {selectedAlert.escalation_level}
                    </span>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Lethality Risk Score</div>
                    <div className="flex items-center gap-2">
                      <div className="text-2xl font-bold" style={{ color: getLethalityColor(selectedAlert.lethality_score) }}>
                        {(selectedAlert.lethality_score * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Campbell Danger Indicators</div>
                    <ul className="list-disc list-inside text-sm">
                      {selectedAlert.campbell_indicators.map((indicator, idx) => (
                        <li key={idx} className="text-red-400">{indicator.replace(/_/g, " ")}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Intervention Pathway</div>
                    <div className="font-semibold">{selectedAlert.intervention_pathway.replace(/_/g, " ")}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Recommended Actions</div>
                    <ul className="list-disc list-inside text-sm">
                      {selectedAlert.recommended_actions.map((action, idx) => (
                        <li key={idx}>{action}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-gray-400 text-center py-8">
                  Select an alert to view details
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">DV Hotspot Map</h3>
            <svg viewBox="0 0 400 300" className="w-full h-64">
              {hotspots.map((hotspot, idx) => {
                const x = (idx % 2) * 200 + 10;
                const y = Math.floor(idx / 2) * 150 + 10;
                const color = hotspot.risk_level === "HIGH" ? "#ef4444" :
                              hotspot.risk_level === "MODERATE" ? "#f97316" : "#22c55e";
                return (
                  <g key={hotspot.zone_id}>
                    <rect
                      x={x}
                      y={y}
                      width="180"
                      height="130"
                      rx="8"
                      fill={color}
                      fillOpacity="0.3"
                      stroke={color}
                      strokeWidth="2"
                    />
                    <text x={x + 90} y={y + 50} textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">
                      {hotspot.zone_id}
                    </text>
                    <text x={x + 90} y={y + 75} textAnchor="middle" fill="white" fontSize="12">
                      {hotspot.incident_count} incidents
                    </text>
                    <text x={x + 90} y={y + 95} textAnchor="middle" fill={color} fontSize="12">
                      {hotspot.risk_level}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Zone Statistics</h3>
            <div className="space-y-3">
              {hotspots.map((hotspot) => (
                <div key={hotspot.zone_id} className="bg-gray-600 rounded p-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold">{hotspot.zone_id}</span>
                    <span className={`px-2 py-1 rounded text-xs ${getEscalationColor(hotspot.risk_level)}`}>
                      {hotspot.risk_level}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div>
                      <div className="text-gray-400">Incidents</div>
                      <div className="font-bold">{hotspot.incident_count}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Repeat</div>
                      <div className="font-bold">{hotspot.repeat_patterns}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Trend</div>
                      <div className={`font-bold ${getTrendColor(hotspot.trend)}`}>
                        {getTrendIcon(hotspot.trend)} {hotspot.trend}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">Privacy & VAWA Compliance</h3>
        <p className="text-gray-400 text-sm">
          All DV data is protected under VAWA safeguards. Victim identity is never disclosed.
          Location information is generalized to zone level. No perpetrator notification.
          All disclosures require victim consent unless immediate safety threat exists.
        </p>
      </div>
    </div>
  );
}
