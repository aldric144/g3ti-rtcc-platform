"use client";

import React, { useState, useEffect } from "react";

interface SuicideAlert {
  alert_id: string;
  timestamp: string;
  risk_level: string;
  zone: string;
  crisis_phrases: string[];
  recommended_actions: string[];
  auto_alert_triggered: boolean;
}

export default function SuicideRiskPanel() {
  const [alerts, setAlerts] = useState<SuicideAlert[]>([
    {
      alert_id: "SR-001",
      timestamp: new Date().toISOString(),
      risk_level: "HIGH",
      zone: "Zone_A",
      crisis_phrases: ["crisis_language_detected"],
      recommended_actions: ["Dispatch crisis intervention team", "Alert Fire/Rescue"],
      auto_alert_triggered: true,
    },
  ]);
  const [selectedAlert, setSelectedAlert] = useState<SuicideAlert | null>(null);
  const [riskFilter, setRiskFilter] = useState<string>("ALL");

  useEffect(() => {
    const interval = setInterval(() => {
      setAlerts((prev) => [...prev]);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const getRiskColor = (level: string): string => {
    switch (level) {
      case "IMMEDIATE_DANGER": return "bg-red-800 text-white";
      case "HIGH": return "bg-red-600 text-white";
      case "MODERATE": return "bg-orange-500 text-white";
      case "LOW": return "bg-yellow-500 text-black";
      default: return "bg-gray-500 text-white";
    }
  };

  const filteredAlerts = alerts.filter(
    (alert) => riskFilter === "ALL" || alert.risk_level === riskFilter
  );

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Suicide Risk Monitoring</h2>
      
      <div className="bg-yellow-900 border border-yellow-600 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 text-yellow-200">
          <span className="text-2xl">⚠️</span>
          <div>
            <div className="font-semibold">Crisis Resources</div>
            <div className="text-sm">988 Suicide & Crisis Lifeline | Local Crisis Line: (561) 555-HELP</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Active Alerts</h3>
              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="bg-gray-600 text-white px-3 py-1 rounded"
              >
                <option value="ALL">All Levels</option>
                <option value="IMMEDIATE_DANGER">Immediate Danger</option>
                <option value="HIGH">High</option>
                <option value="MODERATE">Moderate</option>
                <option value="LOW">Low</option>
              </select>
            </div>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {filteredAlerts.length === 0 ? (
                <div className="text-gray-400 text-center py-8">
                  No active alerts matching filter
                </div>
              ) : (
                filteredAlerts.map((alert) => (
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
                          {alert.risk_level.replace("_", " ")}
                        </span>
                        {alert.auto_alert_triggered && (
                          <span className="px-2 py-1 rounded text-xs bg-blue-600">
                            AUTO-ALERT
                          </span>
                        )}
                      </div>
                      <span className="text-gray-400 text-sm">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-sm text-gray-300">
                      <span className="font-semibold">{alert.zone}</span>
                      {alert.crisis_phrases.length > 0 && (
                        <span className="ml-2 text-gray-400">
                          | {alert.crisis_phrases.length} indicator(s)
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
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
                    {selectedAlert.risk_level.replace("_", " ")}
                  </span>
                </div>
                <div>
                  <div className="text-gray-400 text-sm">Zone</div>
                  <div>{selectedAlert.zone}</div>
                </div>
                <div>
                  <div className="text-gray-400 text-sm">Indicators Detected</div>
                  <ul className="list-disc list-inside text-sm">
                    {selectedAlert.crisis_phrases.map((phrase, idx) => (
                      <li key={idx}>{phrase.replace(/_/g, " ")}</li>
                    ))}
                  </ul>
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

          <div className="bg-gray-700 rounded-lg p-4 mt-4">
            <h3 className="text-lg font-semibold mb-4">Suggested Outreach</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-blue-400">●</span>
                Crisis Intervention Team dispatch
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">●</span>
                Mental health co-responder
              </li>
              <li className="flex items-center gap-2">
                <span className="text-yellow-400">●</span>
                Follow-up welfare check
              </li>
              <li className="flex items-center gap-2">
                <span className="text-purple-400">●</span>
                Connect with community resources
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">Privacy Notice</h3>
        <p className="text-gray-400 text-sm">
          All suicide risk assessments are anonymized. No individual identification is performed.
          Data is used only for crisis response coordination. HIPAA-adjacent protections applied.
        </p>
      </div>
    </div>
  );
}
