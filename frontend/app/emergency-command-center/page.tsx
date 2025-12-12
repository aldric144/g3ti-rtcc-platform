"use client";

import React, { useState, useEffect } from "react";
import DisasterPredictionDashboard from "./components/DisasterPredictionDashboard";
import ResponseCoordinationConsole from "./components/ResponseCoordinationConsole";
import ResourceShelterDashboard from "./components/ResourceShelterDashboard";
import RecoveryDamageDashboard from "./components/RecoveryDamageDashboard";
import EmergencyMessagingConsole from "./components/EmergencyMessagingConsole";

type TabType = "prediction" | "response" | "resources" | "recovery" | "messaging";

interface StabilityData {
  timestamp: string;
  activeHazards: number;
  threatLevel: string;
  affectedZones: number;
  shelterCapacity: number;
  shelterOccupancy: number;
}

export default function EmergencyCommandCenterPage() {
  const [activeTab, setActiveTab] = useState<TabType>("prediction");
  const [stabilityData, setStabilityData] = useState<StabilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStabilityData = async () => {
      try {
        setLoading(true);
        
        const [hazardsRes, resourcesRes] = await Promise.all([
          fetch("/api/emergency-ai/hazards"),
          fetch("/api/emergency-ai/resource-status"),
        ]);

        if (hazardsRes.ok && resourcesRes.ok) {
          const hazardsData = await hazardsRes.json();
          const resourcesData = await resourcesRes.json();

          const highThreatCount = hazardsData.high_threat_count || 0;
          let threatLevel = "Normal";
          if (highThreatCount > 0) {
            threatLevel = "Elevated";
          }
          if (hazardsData.total_count > 3) {
            threatLevel = "High";
          }

          setStabilityData({
            timestamp: new Date().toISOString(),
            activeHazards: hazardsData.total_count || 0,
            threatLevel,
            affectedZones: hazardsData.active_hazards?.reduce(
              (acc: number, h: any) => acc + (h.affected_zones?.length || 0),
              0
            ) || 0,
            shelterCapacity: resourcesData.total_shelter_capacity || 0,
            shelterOccupancy: resourcesData.total_shelter_occupancy || 0,
          });
        }
        setError(null);
      } catch (err) {
        console.error("Failed to fetch stability data:", err);
        setError("Failed to load emergency data");
      } finally {
        setLoading(false);
      }
    };

    fetchStabilityData();
    const interval = setInterval(fetchStabilityData, 30000);
    return () => clearInterval(interval);
  }, []);

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "prediction", label: "Disaster Prediction", icon: "🌀" },
    { id: "response", label: "Response Coordination", icon: "🚨" },
    { id: "resources", label: "Resources & Shelters", icon: "🏠" },
    { id: "recovery", label: "Recovery & Damage", icon: "🔧" },
    { id: "messaging", label: "Emergency Messaging", icon: "📢" },
  ];

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case "Normal":
        return "bg-green-500";
      case "Elevated":
        return "bg-yellow-500";
      case "High":
        return "bg-orange-500";
      case "Extreme":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">
              AI Emergency Management Command
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Riviera Beach Emergency Operations Center - Phase 31
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {stabilityData && (
              <>
                <div className="text-right">
                  <p className="text-xs text-gray-400">Threat Level</p>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getThreatLevelColor(
                      stabilityData.threatLevel
                    )}`}
                  >
                    {stabilityData.threatLevel}
                  </span>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400">Active Hazards</p>
                  <p className="text-xl font-bold text-white">
                    {stabilityData.activeHazards}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400">Shelter Occupancy</p>
                  <p className="text-xl font-bold text-white">
                    {stabilityData.shelterOccupancy}/{stabilityData.shelterCapacity}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="bg-gray-800 border-b border-gray-700">
        <nav className="flex space-x-1 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === tab.id
                  ? "bg-gray-900 text-white border-t border-l border-r border-gray-700"
                  : "text-gray-400 hover:text-white hover:bg-gray-700"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <main className="p-6">
        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-4">
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <>
            {activeTab === "prediction" && <DisasterPredictionDashboard />}
            {activeTab === "response" && <ResponseCoordinationConsole />}
            {activeTab === "resources" && <ResourceShelterDashboard />}
            {activeTab === "recovery" && <RecoveryDamageDashboard />}
            {activeTab === "messaging" && <EmergencyMessagingConsole />}
          </>
        )}
      </main>

      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <p>
            G3TI RTCC-UIP | AI Emergency Management Command | Riviera Beach, FL
          </p>
          <p>
            Last updated:{" "}
            {stabilityData
              ? new Date(stabilityData.timestamp).toLocaleString()
              : "Loading..."}
          </p>
        </div>
      </footer>
    </div>
  );
}
