"use client";

import React, { useState, useEffect } from "react";

interface DeepfakeAlert {
  alert_id: string;
  deepfake_type: string;
  severity: string;
  detection_confidence: string;
  confidence_score: number;
  source_file: string | null;
  source_url: string | null;
  claimed_identity: string | null;
  manipulation_indicators: string[];
  ai_model_detected: string | null;
  officer_involved: boolean;
  officer_id: string | null;
  evidence_integrity_compromised: boolean;
  recommended_action: string;
  timestamp: string;
}

export default function DeepfakeDetectionPanel() {
  const [alerts, setAlerts] = useState<DeepfakeAlert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<DeepfakeAlert | null>(null);
  const [scanMode, setScanMode] = useState<"voice" | "video" | "document">("voice");
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 20000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await fetch("/api/cyber-intel/alerts?alert_type=DEEPFAKE&limit=50");
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error("Failed to fetch deepfake alerts:", error);
    }
  };

  const runScan = async () => {
    setIsScanning(true);
    setScanResult(null);
    
    try {
      const response = await fetch("/api/cyber-intel/scan/deepfake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          media_type: scanMode,
          analysis_features: {
            voice_clone_detected: Math.random() > 0.7,
            blink_rate_anomaly: Math.random() > 0.6,
            facial_boundary_artifacts: Math.random() > 0.5,
            gan_artifacts: Math.random() > 0.8,
          },
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setScanResult(data);
        if (data.deepfake_detected) {
          fetchAlerts();
        }
      }
    } catch (error) {
      console.error("Scan failed:", error);
    } finally {
      setIsScanning(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
      case "CATASTROPHIC":
        return "text-red-500 bg-red-500/20 border-red-500";
      case "HIGH":
        return "text-orange-500 bg-orange-500/20 border-orange-500";
      case "MEDIUM":
        return "text-yellow-500 bg-yellow-500/20 border-yellow-500";
      default:
        return "text-cyan-500 bg-cyan-500/20 border-cyan-500";
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "text-red-400";
    if (score >= 0.6) return "text-orange-400";
    if (score >= 0.4) return "text-yellow-400";
    return "text-green-400";
  };

  const officerAlerts = alerts.filter((a) => a.officer_involved);
  const evidenceAlerts = alerts.filter((a) => a.evidence_integrity_compromised);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-cyan-400">Deepfake Detection Panel</h2>
        <button
          onClick={fetchAlerts}
          className="bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-lg"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-cyan-900/30 border border-cyan-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-cyan-400">{alerts.length}</div>
          <div className="text-sm text-cyan-300">Total Alerts</div>
        </div>
        <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-400">{officerAlerts.length}</div>
          <div className="text-sm text-red-300">Officer-Related</div>
        </div>
        <div className="bg-orange-900/30 border border-orange-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-orange-400">{evidenceAlerts.length}</div>
          <div className="text-sm text-orange-300">Evidence Compromised</div>
        </div>
        <div className="bg-purple-900/30 border border-purple-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-purple-400">
            {alerts.filter((a) => a.ai_model_detected).length}
          </div>
          <div className="text-sm text-purple-300">AI Model Identified</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Scan Media</h3>
          
          <div className="space-y-4">
            <div className="flex bg-gray-700 rounded-lg p-1">
              <button
                onClick={() => setScanMode("voice")}
                className={`flex-1 px-3 py-2 rounded-lg transition-colors ${
                  scanMode === "voice"
                    ? "bg-cyan-600 text-white"
                    : "text-gray-300 hover:bg-gray-600"
                }`}
              >
                Voice
              </button>
              <button
                onClick={() => setScanMode("video")}
                className={`flex-1 px-3 py-2 rounded-lg transition-colors ${
                  scanMode === "video"
                    ? "bg-cyan-600 text-white"
                    : "text-gray-300 hover:bg-gray-600"
                }`}
              >
                Video
              </button>
              <button
                onClick={() => setScanMode("document")}
                className={`flex-1 px-3 py-2 rounded-lg transition-colors ${
                  scanMode === "document"
                    ? "bg-cyan-600 text-white"
                    : "text-gray-300 hover:bg-gray-600"
                }`}
              >
                Document
              </button>
            </div>

            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
              <div className="text-gray-400 mb-4">
                Drop {scanMode} file here or click to upload
              </div>
              <button
                onClick={runScan}
                disabled={isScanning}
                className={`px-6 py-2 rounded-lg ${
                  isScanning
                    ? "bg-gray-600 cursor-not-allowed"
                    : "bg-cyan-600 hover:bg-cyan-700"
                }`}
              >
                {isScanning ? "Scanning..." : "Run Analysis"}
              </button>
            </div>

            {scanResult && (
              <div className={`p-4 rounded-lg border ${
                scanResult.deepfake_detected
                  ? "bg-red-900/30 border-red-500"
                  : "bg-green-900/30 border-green-500"
              }`}>
                <div className="font-semibold mb-2">
                  {scanResult.deepfake_detected ? "Deepfake Detected!" : "No Deepfake Detected"}
                </div>
                {scanResult.deepfake_detected && (
                  <>
                    <div className="text-sm">Type: {scanResult.deepfake_type}</div>
                    <div className="text-sm">
                      Confidence: {Math.round(scanResult.confidence_score * 100)}%
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="col-span-2 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Recent Alerts</h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {alerts.slice(0, 10).map((alert) => (
              <div
                key={alert.alert_id}
                className={`p-4 rounded-lg border cursor-pointer hover:opacity-80 ${
                  alert.evidence_integrity_compromised
                    ? "bg-red-900/20 border-red-500"
                    : alert.officer_involved
                    ? "bg-orange-900/20 border-orange-500"
                    : "bg-gray-700 border-gray-600"
                }`}
                onClick={() => setSelectedAlert(alert)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">{alert.deepfake_type}</span>
                  <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(alert.severity)}`}>
                    {alert.severity}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className={getConfidenceColor(alert.confidence_score)}>
                    {Math.round(alert.confidence_score * 100)}% confidence
                  </span>
                  <span className="text-gray-400">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                {alert.officer_involved && (
                  <div className="mt-2 text-sm text-orange-400">
                    Officer ID: {alert.officer_id || "Unknown"}
                  </div>
                )}
                {alert.evidence_integrity_compromised && (
                  <div className="mt-2 text-sm text-red-400 font-semibold">
                    Evidence Integrity Compromised
                  </div>
                )}
              </div>
            ))}
            
            {alerts.length === 0 && (
              <div className="text-gray-500 text-center py-8">
                No deepfake alerts detected
              </div>
            )}
          </div>
        </div>
      </div>

      {selectedAlert && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-300">Alert Details</h3>
            <button
              onClick={() => setSelectedAlert(null)}
              className="text-gray-400 hover:text-white"
            >
              Close
            </button>
          </div>
          
          <div className="grid grid-cols-3 gap-6">
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400">Alert ID</label>
                <div className="text-white font-mono text-sm">{selectedAlert.alert_id}</div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Deepfake Type</label>
                <div className="text-white">{selectedAlert.deepfake_type}</div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Severity</label>
                <div className={`inline-block px-2 py-1 rounded ${getSeverityColor(selectedAlert.severity)}`}>
                  {selectedAlert.severity}
                </div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Confidence Score</label>
                <div className={`text-2xl font-bold ${getConfidenceColor(selectedAlert.confidence_score)}`}>
                  {Math.round(selectedAlert.confidence_score * 100)}%
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400">Source</label>
                <div className="text-white text-sm">
                  {selectedAlert.source_url || selectedAlert.source_file || "Unknown"}
                </div>
              </div>
              {selectedAlert.claimed_identity && (
                <div>
                  <label className="text-sm text-gray-400">Claimed Identity</label>
                  <div className="text-white">{selectedAlert.claimed_identity}</div>
                </div>
              )}
              {selectedAlert.ai_model_detected && (
                <div>
                  <label className="text-sm text-gray-400">AI Model Detected</label>
                  <div className="text-purple-400">{selectedAlert.ai_model_detected}</div>
                </div>
              )}
              <div>
                <label className="text-sm text-gray-400">Officer Involved</label>
                <div className={selectedAlert.officer_involved ? "text-orange-400" : "text-gray-400"}>
                  {selectedAlert.officer_involved ? `Yes - ${selectedAlert.officer_id}` : "No"}
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400">Manipulation Indicators</label>
                <div className="space-y-1">
                  {selectedAlert.manipulation_indicators.map((indicator, index) => (
                    <div key={index} className="text-sm text-yellow-400">
                      {indicator}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Recommended Action</label>
                <div className="text-yellow-400 text-sm">{selectedAlert.recommended_action}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
