"use client";

import React, { useState, useEffect } from "react";

interface NetworkThreat {
  threat_id: string;
  threat_type: string;
  severity: string;
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  protocol: string;
  detection_method: string;
  signature_name: string | null;
  recommended_action: string;
  timestamp: string;
  status: string;
}

interface ThreatNode {
  id: string;
  type: "source" | "target" | "threat";
  label: string;
  severity: string;
  x: number;
  y: number;
}

interface ThreatConnection {
  source: string;
  target: string;
  threat_type: string;
  severity: string;
}

export default function CyberThreatMap() {
  const [threats, setThreats] = useState<NetworkThreat[]>([]);
  const [selectedThreat, setSelectedThreat] = useState<NetworkThreat | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchThreats();
    const interval = setInterval(fetchThreats, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchThreats = async () => {
    try {
      const response = await fetch("/api/cyber-intel/threats?category=network&limit=50");
      if (response.ok) {
        const data = await response.json();
        setThreats(data.threats || []);
      }
    } catch (error) {
      console.error("Failed to fetch threats:", error);
    } finally {
      setIsLoading(false);
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
      case "LOW":
        return "text-green-500 bg-green-500/20 border-green-500";
      default:
        return "text-blue-500 bg-blue-500/20 border-blue-500";
    }
  };

  const filteredThreats = filterSeverity === "ALL"
    ? threats
    : threats.filter((t) => t.severity === filterSeverity);

  const threatCounts = {
    CRITICAL: threats.filter((t) => t.severity === "CRITICAL").length,
    HIGH: threats.filter((t) => t.severity === "HIGH").length,
    MEDIUM: threats.filter((t) => t.severity === "MEDIUM").length,
    LOW: threats.filter((t) => t.severity === "LOW").length,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-cyan-400">Live Cyber Threat Map</h2>
        <div className="flex items-center space-x-4">
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <button
            onClick={fetchThreats}
            className="bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded-lg"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-red-900/30 border border-red-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-red-400">{threatCounts.CRITICAL}</div>
          <div className="text-sm text-red-300">Critical</div>
        </div>
        <div className="bg-orange-900/30 border border-orange-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-orange-400">{threatCounts.HIGH}</div>
          <div className="text-sm text-orange-300">High</div>
        </div>
        <div className="bg-yellow-900/30 border border-yellow-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-yellow-400">{threatCounts.MEDIUM}</div>
          <div className="text-sm text-yellow-300">Medium</div>
        </div>
        <div className="bg-green-900/30 border border-green-500 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-400">{threatCounts.LOW}</div>
          <div className="text-sm text-green-300">Low</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Attack Origin Visualization</h3>
          <div className="relative h-96 bg-gray-900 rounded-lg overflow-hidden">
            <svg className="w-full h-full" viewBox="0 0 800 400">
              <defs>
                <radialGradient id="nodeGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.2" />
                </radialGradient>
              </defs>
              
              <circle cx="400" cy="200" r="60" fill="url(#nodeGradient)" stroke="#06b6d4" strokeWidth="2" />
              <text x="400" y="205" textAnchor="middle" fill="white" fontSize="12">RBPD Network</text>
              
              {filteredThreats.slice(0, 10).map((threat, index) => {
                const angle = (index / 10) * 2 * Math.PI;
                const radius = 150;
                const x = 400 + radius * Math.cos(angle);
                const y = 200 + radius * Math.sin(angle);
                const color = threat.severity === "CRITICAL" ? "#ef4444" :
                             threat.severity === "HIGH" ? "#f97316" :
                             threat.severity === "MEDIUM" ? "#eab308" : "#22c55e";
                
                return (
                  <g key={threat.threat_id}>
                    <line
                      x1="400"
                      y1="200"
                      x2={x}
                      y2={y}
                      stroke={color}
                      strokeWidth="2"
                      strokeDasharray="5,5"
                      opacity="0.6"
                    />
                    <circle
                      cx={x}
                      cy={y}
                      r="20"
                      fill={color}
                      opacity="0.3"
                      stroke={color}
                      strokeWidth="2"
                      className="cursor-pointer hover:opacity-60"
                      onClick={() => setSelectedThreat(threat)}
                    />
                    <text x={x} y={y + 4} textAnchor="middle" fill="white" fontSize="8">
                      {threat.source_ip.split(".").slice(-1)[0]}
                    </text>
                  </g>
                );
              })}
            </svg>
            
            {filteredThreats.length === 0 && !isLoading && (
              <div className="absolute inset-0 flex items-center justify-center text-gray-500">
                No active threats detected
              </div>
            )}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Threat Details</h3>
          {selectedThreat ? (
            <div className="space-y-4">
              <div className={`px-3 py-2 rounded-lg border ${getSeverityColor(selectedThreat.severity)}`}>
                <span className="font-semibold">{selectedThreat.severity}</span>
              </div>
              <div>
                <label className="text-sm text-gray-400">Threat Type</label>
                <div className="text-white">{selectedThreat.threat_type}</div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Source IP</label>
                <div className="text-white font-mono">{selectedThreat.source_ip}:{selectedThreat.source_port}</div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Target IP</label>
                <div className="text-white font-mono">{selectedThreat.destination_ip}:{selectedThreat.destination_port}</div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Protocol</label>
                <div className="text-white">{selectedThreat.protocol}</div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Detection Method</label>
                <div className="text-white">{selectedThreat.detection_method}</div>
              </div>
              {selectedThreat.signature_name && (
                <div>
                  <label className="text-sm text-gray-400">Signature</label>
                  <div className="text-white">{selectedThreat.signature_name}</div>
                </div>
              )}
              <div>
                <label className="text-sm text-gray-400">Recommended Action</label>
                <div className="text-yellow-400 text-sm">{selectedThreat.recommended_action}</div>
              </div>
              <div>
                <label className="text-sm text-gray-400">Timestamp</label>
                <div className="text-white text-sm">
                  {new Date(selectedThreat.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              Click a threat node to view details
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-300">Recent Threats</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-2">Time</th>
                <th className="pb-2">Type</th>
                <th className="pb-2">Source</th>
                <th className="pb-2">Target</th>
                <th className="pb-2">Severity</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredThreats.slice(0, 10).map((threat) => (
                <tr
                  key={threat.threat_id}
                  className="border-b border-gray-700 hover:bg-gray-700/50 cursor-pointer"
                  onClick={() => setSelectedThreat(threat)}
                >
                  <td className="py-2 text-sm">
                    {new Date(threat.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-2">{threat.threat_type}</td>
                  <td className="py-2 font-mono text-sm">{threat.source_ip}</td>
                  <td className="py-2 font-mono text-sm">{threat.destination_ip}</td>
                  <td className="py-2">
                    <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(threat.severity)}`}>
                      {threat.severity}
                    </span>
                  </td>
                  <td className="py-2 text-sm">{threat.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
