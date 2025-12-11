"use client";

import React, { useState, useEffect } from "react";

interface RansomwareAlert {
  alert_id: string;
  severity: string;
  affected_host: string;
  affected_path: string;
  file_modifications_per_minute: number;
  encryption_detected: boolean;
  ransomware_family: string | null;
  suspicious_extensions: string[];
  c2_communication_detected: boolean;
  files_affected: number;
  recommended_action: string;
  timestamp: string;
  status: string;
}

export default function RansomwareShieldPanel() {
  const [alerts, setAlerts] = useState<RansomwareAlert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<RansomwareAlert | null>(null);
  const [monitoringStatus, setMonitoringStatus] = useState<"active" | "paused">("active");

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await fetch("/api/cyber-intel/alerts?alert_type=RANSOMWARE&limit=50");
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error("Failed to fetch ransomware alerts:", error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "text-red-500 bg-red-500/20 border-red-500";
      case "HIGH":
        return "text-orange-500 bg-orange-500/20 border-orange-500";
      case "MEDIUM":
        return "text-yellow-500 bg-yellow-500/20 border-yellow-500";
      default:
        return "text-green-500 bg-green-500/20 border-green-500";
    }
  };

  const getModificationColor = (rate: number) => {
    if (rate > 100) return "text-red-400";
    if (rate > 50) return "text-orange-400";
    if (rate > 20) return "text-yellow-400";
    return "text-green-400";
  };

  const criticalAlerts = alerts.filter((a) => a.severity === "CRITICAL");
  const encryptionDetected = alerts.filter((a) => a.encryption_detected);
  const c2Detected = alerts.filter((a) => a.c2_communication_detected);

  const knownFamilies = [...new Set(alerts.map((a) => a.ransomware_family).filter(Boolean))];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-orange-400">Ransomware Shield Panel</h2>
        <div className="flex items-center space-x-4">
          <div className={`px-4 py-2 rounded-lg ${
            monitoringStatus === "active"
              ? "bg-green-600"
              : "bg-yellow-600"
          }`}>
            Shield: {monitoringStatus === "active" ? "Active" : "Paused"}
          </div>
          <button
            onClick={() => setMonitoringStatus(monitoringStatus === "active" ? "paused" : "active")}
            className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg"
          >
            {monitoringStatus === "active" ? "Pause" : "Resume"}
          </button>
          <button
            onClick={fetchAlerts}
            className="bg-orange-600 hover:bg-orange-700 px-4 py-2 rounded-lg"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        <div className="bg-orange-900/30 border border-orange-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-orange-400">{alerts.length}</div>
          <div className="text-sm text-orange-300">Total Alerts</div>
        </div>
        <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-400">{criticalAlerts.length}</div>
          <div className="text-sm text-red-300">Critical</div>
        </div>
        <div className="bg-purple-900/30 border border-purple-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-purple-400">{encryptionDetected.length}</div>
          <div className="text-sm text-purple-300">Encryption Detected</div>
        </div>
        <div className="bg-cyan-900/30 border border-cyan-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-cyan-400">{c2Detected.length}</div>
          <div className="text-sm text-cyan-300">C2 Communication</div>
        </div>
        <div className="bg-yellow-900/30 border border-yellow-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-yellow-400">{knownFamilies.length}</div>
          <div className="text-sm text-yellow-300">Known Families</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-300">File Change Accelerometer</h3>
            
            <div className="space-y-4">
              {alerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.alert_id}
                  className="bg-gray-700 rounded-lg p-4 cursor-pointer hover:bg-gray-600"
                  onClick={() => setSelectedAlert(alert)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold">{alert.affected_host}</span>
                    <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <div className="text-sm text-gray-400 mb-2">{alert.affected_path}</div>
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <div className="text-xs text-gray-400 mb-1">Modifications/min</div>
                      <div className="w-full bg-gray-600 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full ${
                            alert.file_modifications_per_minute > 100 ? "bg-red-500" :
                            alert.file_modifications_per_minute > 50 ? "bg-orange-500" :
                            alert.file_modifications_per_minute > 20 ? "bg-yellow-500" : "bg-green-500"
                          }`}
                          style={{ width: `${Math.min(alert.file_modifications_per_minute, 150) / 1.5}%` }}
                        />
                      </div>
                    </div>
                    <div className={`text-2xl font-bold ${getModificationColor(alert.file_modifications_per_minute)}`}>
                      {alert.file_modifications_per_minute}
                    </div>
                  </div>
                  {alert.encryption_detected && (
                    <div className="mt-2 text-sm text-red-400 font-semibold">
                      Encryption Activity Detected
                    </div>
                  )}
                </div>
              ))}
              
              {alerts.length === 0 && (
                <div className="text-gray-500 text-center py-8">
                  No ransomware activity detected
                </div>
              )}
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-300">Encryption Behavior Monitor</h3>
            
            <div className="grid grid-cols-2 gap-4">
              {encryptionDetected.slice(0, 4).map((alert) => (
                <div
                  key={alert.alert_id}
                  className="bg-red-900/20 border border-red-500 rounded-lg p-4 cursor-pointer hover:opacity-80"
                  onClick={() => setSelectedAlert(alert)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-red-400">{alert.affected_host}</span>
                    {alert.ransomware_family && (
                      <span className="px-2 py-1 bg-red-500/30 rounded text-xs text-red-300">
                        {alert.ransomware_family}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-400">
                    Files Affected: {alert.files_affected.toLocaleString()}
                  </div>
                  {alert.suspicious_extensions.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {alert.suspicious_extensions.slice(0, 3).map((ext, i) => (
                        <span key={i} className="px-2 py-1 bg-gray-700 rounded text-xs">
                          {ext}
                        </span>
                      ))}
                    </div>
                  )}
                  {alert.c2_communication_detected && (
                    <div className="mt-2 text-sm text-purple-400">
                      C2 Communication Detected
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Alert Details</h3>
          
          {selectedAlert ? (
            <div className="space-y-4">
              <div className={`px-3 py-2 rounded-lg border ${getSeverityColor(selectedAlert.severity)}`}>
                <span className="font-semibold">{selectedAlert.severity}</span>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Alert ID</label>
                <div className="text-white font-mono text-sm">{selectedAlert.alert_id}</div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Affected Host</label>
                <div className="text-white">{selectedAlert.affected_host}</div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Affected Path</label>
                <div className="text-white text-sm break-all">{selectedAlert.affected_path}</div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Modifications/min</label>
                <div className={`text-2xl font-bold ${getModificationColor(selectedAlert.file_modifications_per_minute)}`}>
                  {selectedAlert.file_modifications_per_minute}
                </div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Files Affected</label>
                <div className="text-white">{selectedAlert.files_affected.toLocaleString()}</div>
              </div>
              
              {selectedAlert.ransomware_family && (
                <div>
                  <label className="text-sm text-gray-400">Ransomware Family</label>
                  <div className="text-red-400 font-semibold">{selectedAlert.ransomware_family}</div>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <div className={`p-3 rounded-lg border ${
                  selectedAlert.encryption_detected
                    ? "bg-red-900/30 border-red-500"
                    : "bg-gray-700 border-gray-600"
                }`}>
                  <div className="text-xs text-gray-400">Encryption</div>
                  <div className={selectedAlert.encryption_detected ? "text-red-400" : "text-gray-400"}>
                    {selectedAlert.encryption_detected ? "Detected" : "None"}
                  </div>
                </div>
                <div className={`p-3 rounded-lg border ${
                  selectedAlert.c2_communication_detected
                    ? "bg-purple-900/30 border-purple-500"
                    : "bg-gray-700 border-gray-600"
                }`}>
                  <div className="text-xs text-gray-400">C2 Comm</div>
                  <div className={selectedAlert.c2_communication_detected ? "text-purple-400" : "text-gray-400"}>
                    {selectedAlert.c2_communication_detected ? "Detected" : "None"}
                  </div>
                </div>
              </div>
              
              {selectedAlert.suspicious_extensions.length > 0 && (
                <div>
                  <label className="text-sm text-gray-400">Suspicious Extensions</label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedAlert.suspicious_extensions.map((ext, i) => (
                      <span key={i} className="px-2 py-1 bg-orange-500/30 rounded text-xs text-orange-300">
                        {ext}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div>
                <label className="text-sm text-gray-400">Recommended Action</label>
                <div className="text-yellow-400 text-sm">{selectedAlert.recommended_action}</div>
              </div>
              
              <div>
                <label className="text-sm text-gray-400">Timestamp</label>
                <div className="text-white text-sm">
                  {new Date(selectedAlert.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              Select an alert to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
