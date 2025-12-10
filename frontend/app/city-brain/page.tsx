"use client";

import { useState, useEffect } from "react";
import CityBrainDashboard from "./components/CityBrainDashboard";
import DigitalTwin3DView from "./components/DigitalTwin3DView";
import LiveCityHeatmap from "./components/LiveCityHeatmap";
import EnvironmentalPanel from "./components/EnvironmentalPanel";
import TrafficFlowPanel from "./components/TrafficFlowPanel";
import UtilityGridPanel from "./components/UtilityGridPanel";
import PredictionConsole from "./components/PredictionConsole";
import EventImpactSimulator from "./components/EventImpactSimulator";
import CityAdminInputForm from "./components/CityAdminInputForm";

type TabType = 
  | "dashboard"
  | "digital-twin"
  | "heatmap"
  | "environment"
  | "traffic"
  | "utilities"
  | "predictions"
  | "simulator"
  | "admin";

interface CityState {
  timestamp: string;
  weather: Record<string, unknown>;
  traffic: Record<string, unknown>;
  utilities: Record<string, unknown>;
  incidents: Record<string, unknown>;
  predictions: Record<string, unknown>;
  population_estimate: number;
  active_events: Array<Record<string, unknown>>;
  module_statuses: Record<string, unknown>;
  overall_health: number;
}

export default function CityBrainPage() {
  const [activeTab, setActiveTab] = useState<TabType>("dashboard");
  const [cityState, setCityState] = useState<CityState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    fetchCityState();
    const interval = setInterval(fetchCityState, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchCityState = async () => {
    try {
      const response = await fetch("/api/citybrain/city/state");
      if (!response.ok) throw new Error("Failed to fetch city state");
      const data = await response.json();
      setCityState(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: "dashboard", label: "Dashboard", icon: "grid" },
    { id: "digital-twin", label: "Digital Twin", icon: "cube" },
    { id: "heatmap", label: "Live Heatmap", icon: "map" },
    { id: "environment", label: "Environment", icon: "cloud" },
    { id: "traffic", label: "Traffic", icon: "car" },
    { id: "utilities", label: "Utilities", icon: "zap" },
    { id: "predictions", label: "Predictions", icon: "trending-up" },
    { id: "simulator", label: "Simulator", icon: "play" },
    { id: "admin", label: "Admin Console", icon: "settings" },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <CityBrainDashboard cityState={cityState} />;
      case "digital-twin":
        return <DigitalTwin3DView />;
      case "heatmap":
        return <LiveCityHeatmap />;
      case "environment":
        return <EnvironmentalPanel />;
      case "traffic":
        return <TrafficFlowPanel />;
      case "utilities":
        return <UtilityGridPanel />;
      case "predictions":
        return <PredictionConsole />;
      case "simulator":
        return <EventImpactSimulator />;
      case "admin":
        return <CityAdminInputForm onEventCreated={fetchCityState} />;
      default:
        return <CityBrainDashboard cityState={cityState} />;
    }
  };

  const getHealthColor = (health: number) => {
    if (health >= 0.9) return "text-green-500";
    if (health >= 0.7) return "text-yellow-500";
    if (health >= 0.5) return "text-orange-500";
    return "text-red-500";
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-xl font-bold">CB</span>
              </div>
              <div>
                <h1 className="text-xl font-bold">AI City Brain</h1>
                <p className="text-sm text-gray-400">Riviera Beach, FL 33404</p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${wsConnected ? "bg-green-500" : "bg-yellow-500"} animate-pulse`} />
              <span className="text-sm text-gray-400">
                {wsConnected ? "Live" : "Polling"}
              </span>
            </div>

            {cityState && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-400">System Health:</span>
                <span className={`font-bold ${getHealthColor(cityState.overall_health)}`}>
                  {(cityState.overall_health * 100).toFixed(0)}%
                </span>
              </div>
            )}

            {lastUpdate && (
              <div className="text-sm text-gray-400">
                Updated: {lastUpdate.toLocaleTimeString()}
              </div>
            )}

            <button
              onClick={fetchCityState}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
            >
              Refresh
            </button>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700 px-6">
        <div className="flex space-x-1 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? "text-blue-400 border-b-2 border-blue-400"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
          </div>
        ) : error ? (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
            <p className="text-red-400">Error: {error}</p>
            <button
              onClick={fetchCityState}
              className="mt-2 px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
            >
              Retry
            </button>
          </div>
        ) : (
          renderTabContent()
        )}
      </main>

      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div>
            G3TI RTCC-UIP | AI City Brain Engine | Phase 22
          </div>
          <div className="flex items-center space-x-4">
            <span>Population: {cityState?.population_estimate?.toLocaleString() || "N/A"}</span>
            <span>Active Events: {cityState?.active_events?.length || 0}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
