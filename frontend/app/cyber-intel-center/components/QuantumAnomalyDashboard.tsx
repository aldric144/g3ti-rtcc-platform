"use client";

import React, { useState, useEffect } from "react";

interface QuantumAnomaly {
  anomaly_id: string;
  threat_type: string;
  severity: string;
  source_identifier: string;
  detection_confidence: string;
  qubit_pattern: string | null;
  photonic_signature: string | null;
  anomaly_description: string;
  recommended_action: string;
  timestamp: string;
}

interface CryptoAttack {
  attack_id: string;
  attack_type: string;
  severity: string;
  target_algorithm: string;
  target_key_size: number;
  detection_confidence: string;
  attack_vector: string;
  estimated_decrypt_timeline: string | null;
  post_quantum_ready: boolean;
  recommended_action: string;
  timestamp: string;
}

export default function QuantumAnomalyDashboard() {
  const [anomalies, setAnomalies] = useState<QuantumAnomaly[]>([]);
  const [cryptoAttacks, setCryptoAttacks] = useState<CryptoAttack[]>([]);
  const [selectedItem, setSelectedItem] = useState<QuantumAnomaly | CryptoAttack | null>(null);
  const [activeView, setActiveView] = useState<"anomalies" | "crypto">("anomalies");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchQuantumData();
    const interval = setInterval(fetchQuantumData, 20000);
    return () => clearInterval(interval);
  }, []);

  const fetchQuantumData = async () => {
    try {
      const response = await fetch("/api/cyber-intel/threats?category=quantum&limit=50");
      if (response.ok) {
        const data = await response.json();
        const quantumThreats = data.threats || [];
        setAnomalies(quantumThreats.filter((t: any) => t.category === "QUANTUM"));
        setCryptoAttacks(quantumThreats.filter((t: any) => t.category === "CRYPTO"));
      }
    } catch (error) {
      console.error("Failed to fetch quantum data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "CATASTROPHIC":
      case "CRITICAL":
        return "text-red-500 bg-red-500/20 border-red-500";
      case "HIGH":
        return "text-orange-500 bg-orange-500/20 border-orange-500";
      case "MEDIUM":
        return "text-yellow-500 bg-yellow-500/20 border-yellow-500";
      case "LOW":
        return "text-green-500 bg-green-500/20 border-green-500";
      default:
        return "text-purple-500 bg-purple-500/20 border-purple-500";
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case "VERY_HIGH":
        return "text-green-400";
      case "HIGH":
        return "text-cyan-400";
      case "MEDIUM":
        return "text-yellow-400";
      default:
        return "text-gray-400";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-purple-400">Quantum Anomaly Dashboard</h2>
        <div className="flex items-center space-x-4">
          <div className="flex bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setActiveView("anomalies")}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeView === "anomalies"
                  ? "bg-purple-600 text-white"
                  : "text-gray-300 hover:bg-gray-600"
              }`}
            >
              Quantum Anomalies
            </button>
            <button
              onClick={() => setActiveView("crypto")}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeView === "crypto"
                  ? "bg-purple-600 text-white"
                  : "text-gray-300 hover:bg-gray-600"
              }`}
            >
              Crypto Attacks
            </button>
          </div>
          <button
            onClick={fetchQuantumData}
            className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-purple-900/30 border border-purple-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-purple-400">{anomalies.length}</div>
          <div className="text-sm text-purple-300">Quantum Anomalies</div>
        </div>
        <div className="bg-cyan-900/30 border border-cyan-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-cyan-400">{cryptoAttacks.length}</div>
          <div className="text-sm text-cyan-300">Crypto Attacks</div>
        </div>
        <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-400">
            {cryptoAttacks.filter((a) => !a.post_quantum_ready).length}
          </div>
          <div className="text-sm text-red-300">Vulnerable Systems</div>
        </div>
        <div className="bg-green-900/30 border border-green-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-400">
            {cryptoAttacks.filter((a) => a.post_quantum_ready).length}
          </div>
          <div className="text-sm text-green-300">PQ-Ready Systems</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">
            {activeView === "anomalies" ? "Qubit Pattern View" : "Post-Quantum Cryptography Alerts"}
          </h3>
          
          {activeView === "anomalies" ? (
            <div className="space-y-4">
              <div className="relative h-64 bg-gray-900 rounded-lg overflow-hidden">
                <svg className="w-full h-full" viewBox="0 0 800 250">
                  {anomalies.slice(0, 20).map((anomaly, index) => {
                    const x = 40 + (index % 10) * 75;
                    const y = 50 + Math.floor(index / 10) * 100;
                    const color = anomaly.severity === "CRITICAL" ? "#ef4444" :
                                 anomaly.severity === "HIGH" ? "#f97316" :
                                 anomaly.severity === "MEDIUM" ? "#eab308" : "#a855f7";
                    
                    return (
                      <g key={anomaly.anomaly_id}>
                        <circle
                          cx={x}
                          cy={y}
                          r="25"
                          fill={color}
                          opacity="0.3"
                          stroke={color}
                          strokeWidth="2"
                          className="cursor-pointer hover:opacity-60"
                          onClick={() => setSelectedItem(anomaly)}
                        />
                        <circle
                          cx={x}
                          cy={y}
                          r="10"
                          fill={color}
                          opacity="0.8"
                        />
                        <text x={x} y={y + 45} textAnchor="middle" fill="#9ca3af" fontSize="10">
                          {anomaly.threat_type.split("_")[0]}
                        </text>
                      </g>
                    );
                  })}
                </svg>
                
                {anomalies.length === 0 && !isLoading && (
                  <div className="absolute inset-0 flex items-center justify-center text-gray-500">
                    No quantum anomalies detected
                  </div>
                )}
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-gray-700">
                      <th className="pb-2">Time</th>
                      <th className="pb-2">Type</th>
                      <th className="pb-2">Source</th>
                      <th className="pb-2">Confidence</th>
                      <th className="pb-2">Severity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {anomalies.slice(0, 10).map((anomaly) => (
                      <tr
                        key={anomaly.anomaly_id}
                        className="border-b border-gray-700 hover:bg-gray-700/50 cursor-pointer"
                        onClick={() => setSelectedItem(anomaly)}
                      >
                        <td className="py-2 text-sm">
                          {new Date(anomaly.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="py-2">{anomaly.threat_type}</td>
                        <td className="py-2 font-mono text-sm">{anomaly.source_identifier}</td>
                        <td className={`py-2 ${getConfidenceColor(anomaly.detection_confidence)}`}>
                          {anomaly.detection_confidence}
                        </td>
                        <td className="py-2">
                          <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(anomaly.severity)}`}>
                            {anomaly.severity}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {cryptoAttacks.slice(0, 6).map((attack) => (
                  <div
                    key={attack.attack_id}
                    className={`p-4 rounded-lg border cursor-pointer hover:opacity-80 ${
                      attack.post_quantum_ready
                        ? "bg-green-900/20 border-green-500"
                        : "bg-red-900/20 border-red-500"
                    }`}
                    onClick={() => setSelectedItem(attack)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">{attack.target_algorithm}</span>
                      <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(attack.severity)}`}>
                        {attack.severity}
                      </span>
                    </div>
                    <div className="text-sm text-gray-400">
                      Key Size: {attack.target_key_size} bits
                    </div>
                    <div className="text-sm text-gray-400">
                      Attack: {attack.attack_type}
                    </div>
                    {attack.estimated_decrypt_timeline && (
                      <div className="text-sm text-yellow-400 mt-2">
                        Est. Decrypt: {attack.estimated_decrypt_timeline}
                      </div>
                    )}
                    <div className={`text-sm mt-2 ${attack.post_quantum_ready ? "text-green-400" : "text-red-400"}`}>
                      {attack.post_quantum_ready ? "PQ-Ready" : "Vulnerable"}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Details</h3>
          {selectedItem ? (
            <div className="space-y-4">
              <div className={`px-3 py-2 rounded-lg border ${getSeverityColor((selectedItem as any).severity)}`}>
                <span className="font-semibold">{(selectedItem as any).severity}</span>
              </div>
              
              {"anomaly_id" in selectedItem ? (
                <>
                  <div>
                    <label className="text-sm text-gray-400">Anomaly ID</label>
                    <div className="text-white font-mono text-sm">{selectedItem.anomaly_id}</div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Threat Type</label>
                    <div className="text-white">{selectedItem.threat_type}</div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Source</label>
                    <div className="text-white">{selectedItem.source_identifier}</div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Confidence</label>
                    <div className={getConfidenceColor(selectedItem.detection_confidence)}>
                      {selectedItem.detection_confidence}
                    </div>
                  </div>
                  {selectedItem.qubit_pattern && (
                    <div>
                      <label className="text-sm text-gray-400">Qubit Pattern</label>
                      <div className="text-purple-400 font-mono text-xs break-all">
                        {selectedItem.qubit_pattern}
                      </div>
                    </div>
                  )}
                  <div>
                    <label className="text-sm text-gray-400">Description</label>
                    <div className="text-white text-sm">{selectedItem.anomaly_description}</div>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="text-sm text-gray-400">Attack ID</label>
                    <div className="text-white font-mono text-sm">{(selectedItem as CryptoAttack).attack_id}</div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Attack Type</label>
                    <div className="text-white">{(selectedItem as CryptoAttack).attack_type}</div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Target Algorithm</label>
                    <div className="text-white">{(selectedItem as CryptoAttack).target_algorithm}</div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Key Size</label>
                    <div className="text-white">{(selectedItem as CryptoAttack).target_key_size} bits</div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-400">Attack Vector</label>
                    <div className="text-white text-sm">{(selectedItem as CryptoAttack).attack_vector}</div>
                  </div>
                  {(selectedItem as CryptoAttack).estimated_decrypt_timeline && (
                    <div>
                      <label className="text-sm text-gray-400">Est. Decrypt Timeline</label>
                      <div className="text-yellow-400">{(selectedItem as CryptoAttack).estimated_decrypt_timeline}</div>
                    </div>
                  )}
                </>
              )}
              
              <div>
                <label className="text-sm text-gray-400">Recommended Action</label>
                <div className="text-yellow-400 text-sm">{(selectedItem as any).recommended_action}</div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              Select an item to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
