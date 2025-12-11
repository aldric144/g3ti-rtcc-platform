"use client";

import React, { useState, useEffect } from "react";
import CyberThreatMap from "./components/CyberThreatMap";
import QuantumAnomalyDashboard from "./components/QuantumAnomalyDashboard";
import DeepfakeDetectionPanel from "./components/DeepfakeDetectionPanel";
import DisinformationRadar from "./components/DisinformationRadar";
import RansomwareShieldPanel from "./components/RansomwareShieldPanel";
import SystemHardeningConsole from "./components/SystemHardeningConsole";

interface ThreatOverview {
  overall_threat_level: string;
  network_threats_24h: number;
  ransomware_alerts_24h: number;
  quantum_threats_24h: number;
  deepfake_alerts_24h: number;
  disinfo_alerts_24h: number;
  critical_alerts: number;
  active_incidents: number;
  post_quantum_readiness: number;
  community_tension_index: number;
  recommendations: string[];
}

type TabType = "threats" | "quantum" | "deepfake" | "disinfo" | "ransomware" | "hardening";

export default function CyberIntelCenterPage() {
  const [activeTab, setActiveTab] = useState<TabType>("threats");
  const [overview, setOverview] = useState<ThreatOverview | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    fetchOverview();
    const interval = setInterval(fetchOverview, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchOverview = async () => {
    try {
      const response = await fetch("/api/cyber-intel/overview");
      if (response.ok) {
        const data = await response.json();
        setOverview(data);
        setIsConnected(true);
      }
    } catch (error) {
      console.error("Failed to fetch cyber intel overview:", error);
      setIsConnected(false);
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case "CRITICAL":
      case "CATASTROPHIC":
      case "EMERGENCY":
        return "bg-red-600";
      case "HIGH":
        return "bg-orange-500";
      case "MEDIUM":
        return "bg-yellow-500";
      case "LOW":
        return "bg-green-500";
      default:
        return "bg-blue-500";
    }
  };

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "threats", label: "Cyber Threats", icon: "shield" },
    { id: "quantum", label: "Quantum Anomalies", icon: "atom" },
    { id: "deepfake", label: "Deepfake Detection", icon: "video" },
    { id: "disinfo", label: "Disinformation", icon: "radar" },
    { id: "ransomware", label: "Ransomware Shield", icon: "lock" },
    { id: "hardening", label: "System Hardening", icon: "settings" },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-cyan-400">
              Cyber Intelligence Center
            </h1>
            <span className="text-sm text-gray-400">
              Riviera Beach PD - ORI: FL0500400
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <div
              className={`px-3 py-1 rounded-full text-sm ${
                isConnected ? "bg-green-600" : "bg-red-600"
              }`}
            >
              {isConnected ? "Connected" : "Disconnected"}
            </div>
            {overview && (
              <div
                className={`px-4 py-2 rounded-lg ${getThreatLevelColor(
                  overview.overall_threat_level
                )}`}
              >
                Threat Level: {overview.overall_threat_level}
              </div>
            )}
          </div>
        </div>
      </header>

      {overview && (
        <div className="grid grid-cols-6 gap-4 p-4 bg-gray-800 border-b border-gray-700">
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-red-400">
              {overview.network_threats_24h}
            </div>
            <div className="text-sm text-gray-400">Network Threats (24h)</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-orange-400">
              {overview.ransomware_alerts_24h}
            </div>
            <div className="text-sm text-gray-400">Ransomware Alerts</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-purple-400">
              {overview.quantum_threats_24h}
            </div>
            <div className="text-sm text-gray-400">Quantum Threats</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-cyan-400">
              {overview.deepfake_alerts_24h}
            </div>
            <div className="text-sm text-gray-400">Deepfake Alerts</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-yellow-400">
              {overview.disinfo_alerts_24h}
            </div>
            <div className="text-sm text-gray-400">Disinfo Alerts</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-green-400">
              {Math.round(overview.post_quantum_readiness * 100)}%
            </div>
            <div className="text-sm text-gray-400">PQ Readiness</div>
          </div>
        </div>
      )}

      <nav className="bg-gray-800 px-6 py-2 border-b border-gray-700">
        <div className="flex space-x-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? "bg-cyan-600 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">
        {activeTab === "threats" && <CyberThreatMap />}
        {activeTab === "quantum" && <QuantumAnomalyDashboard />}
        {activeTab === "deepfake" && <DeepfakeDetectionPanel />}
        {activeTab === "disinfo" && <DisinformationRadar />}
        {activeTab === "ransomware" && <RansomwareShieldPanel />}
        {activeTab === "hardening" && <SystemHardeningConsole />}
      </main>

      {overview && overview.recommendations.length > 0 && (
        <footer className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 px-6 py-3">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-semibold text-yellow-400">
              Recommendations:
            </span>
            <div className="flex-1 overflow-x-auto">
              <div className="flex space-x-4">
                {overview.recommendations.slice(0, 3).map((rec, index) => (
                  <span key={index} className="text-sm text-gray-300 whitespace-nowrap">
                    {rec}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
}
