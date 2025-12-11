"use client";

import React, { useState, useEffect } from "react";
import CommunityStabilityDashboard from "./components/CommunityStabilityDashboard";
import SuicideRiskPanel from "./components/SuicideRiskPanel";
import DVHotspotPredictor from "./components/DVHotspotPredictor";
import YouthCrisisMonitor from "./components/YouthCrisisMonitor";
import CrisisRoutingConsole from "./components/CrisisRoutingConsole";
import MentalHealthPulseMap from "./components/MentalHealthPulseMap";

interface StabilityOverview {
  overall_stability: number;
  mental_health_score: number;
  violence_score: number;
  community_cohesion: number;
  youth_stability: number;
  active_crises: number;
  dv_alerts: number;
  suicide_alerts: number;
  youth_alerts: number;
}

export default function HumanIntelCenter() {
  const [activeTab, setActiveTab] = useState<string>("stability");
  const [overview, setOverview] = useState<StabilityOverview>({
    overall_stability: 74.5,
    mental_health_score: 72.0,
    violence_score: 78.0,
    community_cohesion: 70.0,
    youth_stability: 68.0,
    active_crises: 3,
    dv_alerts: 2,
    suicide_alerts: 1,
    youth_alerts: 4,
  });
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");

  useEffect(() => {
    fetchOverview();
    const interval = setInterval(fetchOverview, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchOverview = async () => {
    try {
      const response = await fetch("/api/human-intel/stability-map");
      if (response.ok) {
        const data = await response.json();
        setOverview({
          overall_stability: data.overall_stability_score || 74.5,
          mental_health_score: data.mental_health_score || 72.0,
          violence_score: data.violence_score || 78.0,
          community_cohesion: data.community_cohesion_score || 70.0,
          youth_stability: data.youth_stability_score || 68.0,
          active_crises: overview.active_crises,
          dv_alerts: overview.dv_alerts,
          suicide_alerts: overview.suicide_alerts,
          youth_alerts: overview.youth_alerts,
        });
        setIsConnected(true);
        setLastUpdate(new Date().toLocaleTimeString());
      }
    } catch (error) {
      setIsConnected(false);
    }
  };

  const getStabilityColor = (score: number): string => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    if (score >= 40) return "text-orange-500";
    return "text-red-500";
  };

  const getStabilityLevel = (score: number): string => {
    if (score >= 80) return "STABLE";
    if (score >= 60) return "MODERATE";
    if (score >= 40) return "ELEVATED";
    return "CRITICAL";
  };

  const tabs = [
    { id: "stability", label: "Community Stability", icon: "📊" },
    { id: "suicide", label: "Suicide Risk", icon: "🆘" },
    { id: "dv", label: "DV Hotspots", icon: "🏠" },
    { id: "youth", label: "Youth Crisis", icon: "👥" },
    { id: "routing", label: "Crisis Routing", icon: "🚨" },
    { id: "mental", label: "Mental Health", icon: "🧠" },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">Human Stability Intelligence Center</h1>
            <p className="text-gray-400 mt-1">
              Community Mental Health | Suicide Prevention | DV Risk | Youth Crisis
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 ${isConnected ? "text-green-400" : "text-red-400"}`}>
              <span className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-400" : "bg-red-400"}`}></span>
              {isConnected ? "Connected" : "Disconnected"}
            </div>
            <div className="text-gray-400 text-sm">
              Last update: {lastUpdate || "Never"}
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Community Stability Overview</h2>
            <div className={`text-2xl font-bold ${getStabilityColor(overview.overall_stability)}`}>
              {getStabilityLevel(overview.overall_stability)} ({overview.overall_stability.toFixed(1)})
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
            <div className="bg-gray-700 rounded p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">Overall</div>
              <div className={`text-xl font-bold ${getStabilityColor(overview.overall_stability)}`}>
                {overview.overall_stability.toFixed(1)}
              </div>
            </div>
            <div className="bg-gray-700 rounded p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">Mental Health</div>
              <div className={`text-xl font-bold ${getStabilityColor(overview.mental_health_score)}`}>
                {overview.mental_health_score.toFixed(1)}
              </div>
            </div>
            <div className="bg-gray-700 rounded p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">Violence</div>
              <div className={`text-xl font-bold ${getStabilityColor(overview.violence_score)}`}>
                {overview.violence_score.toFixed(1)}
              </div>
            </div>
            <div className="bg-gray-700 rounded p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">Cohesion</div>
              <div className={`text-xl font-bold ${getStabilityColor(overview.community_cohesion)}`}>
                {overview.community_cohesion.toFixed(1)}
              </div>
            </div>
            <div className="bg-gray-700 rounded p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">Youth</div>
              <div className={`text-xl font-bold ${getStabilityColor(overview.youth_stability)}`}>
                {overview.youth_stability.toFixed(1)}
              </div>
            </div>
            <div className="bg-gray-700 rounded p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">Active Crises</div>
              <div className="text-xl font-bold text-orange-400">{overview.active_crises}</div>
            </div>
            <div className="bg-gray-700 rounded p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">DV Alerts</div>
              <div className="text-xl font-bold text-red-400">{overview.dv_alerts}</div>
            </div>
            <div className="bg-gray-700 rounded p-3 text-center">
              <div className="text-gray-400 text-xs mb-1">Youth Alerts</div>
              <div className="text-xl font-bold text-yellow-400">{overview.youth_alerts}</div>
            </div>
          </div>
        </div>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          {activeTab === "stability" && <CommunityStabilityDashboard />}
          {activeTab === "suicide" && <SuicideRiskPanel />}
          {activeTab === "dv" && <DVHotspotPredictor />}
          {activeTab === "youth" && <YouthCrisisMonitor />}
          {activeTab === "routing" && <CrisisRoutingConsole />}
          {activeTab === "mental" && <MentalHealthPulseMap />}
        </div>

        <div className="mt-6 bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2">Privacy & Ethics Notice</h3>
          <div className="text-gray-400 text-sm">
            <p>
              All data is anonymized and aggregated. No individual identification is performed.
              This system complies with HIPAA-adjacent protections, FERPA requirements, and VAWA safeguards.
              No private social media monitoring. No demographic profiling. All models undergo fairness audits.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
