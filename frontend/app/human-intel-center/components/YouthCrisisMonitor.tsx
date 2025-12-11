"use client";

import React, { useState, useEffect } from "react";

interface YouthAlert {
  alert_id: string;
  timestamp: string;
  risk_level: string;
  risk_types: string[];
  school_zone: string;
  age_group: string;
  recommended_interventions: string[];
  urgency: string;
}

interface SchoolCluster {
  school_zone: string;
  incident_count: number;
  incident_types: string[];
  severity_trend: string;
  peer_involvement: boolean;
}

export default function YouthCrisisMonitor() {
  const [alerts, setAlerts] = useState<YouthAlert[]>([
    {
      alert_id: "YRA-001",
      timestamp: new Date().toISOString(),
      risk_level: "ELEVATED",
      risk_types: ["truancy", "peer_destabilization"],
      school_zone: "Zone_A",
      age_group: "middle_school",
      recommended_interventions: ["school_counselor", "youth_mentor", "after_school_program"],
      urgency: "URGENT",
    },
  ]);
  const [clusters, setClusters] = useState<SchoolCluster[]>([
    { school_zone: "Zone_A", incident_count: 5, incident_types: ["behavioral", "fight"], severity_trend: "increasing", peer_involvement: true },
    { school_zone: "Zone_B", incident_count: 2, incident_types: ["truancy"], severity_trend: "stable", peer_involvement: false },
    { school_zone: "Zone_C", incident_count: 7, incident_types: ["behavioral", "substance"], severity_trend: "increasing", peer_involvement: true },
  ]);
  const [selectedAlert, setSelectedAlert] = useState<YouthAlert | null>(null);
  const [viewMode, setViewMode] = useState<"alerts" | "clusters" | "stability">("alerts");

  const getRiskColor = (level: string): string => {
    switch (level) {
      case "CRITICAL": return "bg-red-800 text-white";
      case "HIGH": return "bg-red-600 text-white";
      case "ELEVATED": return "bg-orange-500 text-white";
      case "MODERATE": return "bg-yellow-500 text-black";
      case "LOW": return "bg-green-500 text-white";
      case "MINIMAL": return "bg-green-600 text-white";
      default: return "bg-gray-500 text-white";
    }
  };

  const getUrgencyColor = (urgency: string): string => {
    switch (urgency) {
      case "IMMEDIATE": return "text-red-400";
      case "URGENT": return "text-orange-400";
      case "STANDARD": return "text-yellow-400";
      default: return "text-gray-400";
    }
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
      <h2 className="text-2xl font-bold mb-4">Youth Crisis Monitor</h2>

      <div className="bg-blue-900 border border-blue-600 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 text-blue-200">
          <span className="text-2xl">👥</span>
          <div>
            <div className="font-semibold">Youth Resources</div>
            <div className="text-sm">Youth Crisis Line: (561) 555-YOUTH | School Counselor Hotline | After-School Programs</div>
          </div>
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setViewMode("alerts")}
          className={`px-4 py-2 rounded ${viewMode === "alerts" ? "bg-blue-600" : "bg-gray-600"}`}
        >
          Risk Alerts
        </button>
        <button
          onClick={() => setViewMode("clusters")}
          className={`px-4 py-2 rounded ${viewMode === "clusters" ? "bg-blue-600" : "bg-gray-600"}`}
        >
          School Clusters
        </button>
        <button
          onClick={() => setViewMode("stability")}
          className={`px-4 py-2 rounded ${viewMode === "stability" ? "bg-blue-600" : "bg-gray-600"}`}
        >
          Stability Map
        </button>
      </div>

      {viewMode === "alerts" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Youth Risk Alerts</h3>
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
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(alert.risk_level)}`}>
                          {alert.risk_level}
                        </span>
                        <span className={`text-sm ${getUrgencyColor(alert.urgency)}`}>
                          {alert.urgency}
                        </span>
                      </div>
                      <span className="text-gray-400 text-sm">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="font-semibold">{alert.school_zone}</span>
                      <span className="text-gray-400 ml-2">| {alert.age_group.replace("_", " ")}</span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {alert.risk_types.map((type, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-gray-500 rounded text-xs">
                          {type.replace(/_/g, " ")}
                        </span>
                      ))}
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
                    <div className="text-gray-400 text-sm">Risk Level</div>
                    <span className={`px-2 py-1 rounded text-sm ${getRiskColor(selectedAlert.risk_level)}`}>
                      {selectedAlert.risk_level}
                    </span>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">School Zone</div>
                    <div>{selectedAlert.school_zone}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Age Group</div>
                    <div className="capitalize">{selectedAlert.age_group.replace("_", " ")}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Risk Types</div>
                    <ul className="list-disc list-inside text-sm">
                      {selectedAlert.risk_types.map((type, idx) => (
                        <li key={idx}>{type.replace(/_/g, " ")}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div className="text-gray-400 text-sm">Recommended Interventions</div>
                    <ul className="list-disc list-inside text-sm">
                      {selectedAlert.recommended_interventions.map((intervention, idx) => (
                        <li key={idx}>{intervention.replace(/_/g, " ")}</li>
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
      )}

      {viewMode === "clusters" && (
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">School Incident Clusters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {clusters.map((cluster) => (
              <div key={cluster.school_zone} className="bg-gray-600 rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <h4 className="font-semibold">{cluster.school_zone}</h4>
                  <span className={`${getTrendColor(cluster.severity_trend)}`}>
                    {getTrendIcon(cluster.severity_trend)} {cluster.severity_trend}
                  </span>
                </div>
                <div className="text-3xl font-bold mb-2">{cluster.incident_count}</div>
                <div className="text-sm text-gray-400 mb-2">incidents in 30 days</div>
                <div className="flex flex-wrap gap-1 mb-2">
                  {cluster.incident_types.map((type, idx) => (
                    <span key={idx} className="px-2 py-0.5 bg-gray-500 rounded text-xs">
                      {type}
                    </span>
                  ))}
                </div>
                {cluster.peer_involvement && (
                  <div className="text-xs text-orange-400">
                    Peer group involvement detected
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {viewMode === "stability" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Youth Stability Map</h3>
            <svg viewBox="0 0 400 300" className="w-full h-64">
              <rect x="10" y="10" width="180" height="130" rx="8" fill="#f97316" fillOpacity="0.3" stroke="#f97316" strokeWidth="2" />
              <text x="100" y="60" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">Zone A</text>
              <text x="100" y="85" textAnchor="middle" fill="white" fontSize="24">72</text>
              <text x="100" y="105" textAnchor="middle" fill="#f97316" fontSize="12">ELEVATED</text>
              
              <rect x="210" y="10" width="180" height="130" rx="8" fill="#22c55e" fillOpacity="0.3" stroke="#22c55e" strokeWidth="2" />
              <text x="300" y="60" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">Zone B</text>
              <text x="300" y="85" textAnchor="middle" fill="white" fontSize="24">85</text>
              <text x="300" y="105" textAnchor="middle" fill="#22c55e" fontSize="12">STABLE</text>
              
              <rect x="10" y="160" width="180" height="130" rx="8" fill="#ef4444" fillOpacity="0.3" stroke="#ef4444" strokeWidth="2" />
              <text x="100" y="210" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">Zone C</text>
              <text x="100" y="235" textAnchor="middle" fill="white" fontSize="24">58</text>
              <text x="100" y="255" textAnchor="middle" fill="#ef4444" fontSize="12">HIGH RISK</text>
              
              <rect x="210" y="160" width="180" height="130" rx="8" fill="#eab308" fillOpacity="0.3" stroke="#eab308" strokeWidth="2" />
              <text x="300" y="210" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">Zone D</text>
              <text x="300" y="235" textAnchor="middle" fill="white" fontSize="24">68</text>
              <text x="300" y="255" textAnchor="middle" fill="#eab308" fontSize="12">MODERATE</text>
            </svg>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Intervention Programs</h3>
            <div className="space-y-3">
              <div className="bg-gray-600 rounded p-3">
                <div className="font-semibold mb-1">School Counselor Program</div>
                <div className="text-sm text-gray-400">Active in all zones | 12 counselors available</div>
              </div>
              <div className="bg-gray-600 rounded p-3">
                <div className="font-semibold mb-1">Youth Mentorship</div>
                <div className="text-sm text-gray-400">Focus on Zone A & C | 8 mentors assigned</div>
              </div>
              <div className="bg-gray-600 rounded p-3">
                <div className="font-semibold mb-1">After-School Activities</div>
                <div className="text-sm text-gray-400">All zones | Sports, arts, tutoring</div>
              </div>
              <div className="bg-gray-600 rounded p-3">
                <div className="font-semibold mb-1">Gang Intervention</div>
                <div className="text-sm text-gray-400">Zone C priority | 3 specialists</div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">Privacy & FERPA Compliance</h3>
        <p className="text-gray-400 text-sm">
          All youth data is protected under FERPA. No individual student identification.
          Data is aggregated at zone level only. No demographic profiling.
          School records accessed only with proper authorization or health/safety emergency.
        </p>
      </div>
    </div>
  );
}
